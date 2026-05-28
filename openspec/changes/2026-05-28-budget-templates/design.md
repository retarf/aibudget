## Context

The budget app has no concept of planning. Budgets are created with a name and
date range; categories are global entities; transactions record actual spend.
Users who create similar budgets each month must re-enter the same intended
spending amounts each time — there is no way to save and reuse that structure.

This change introduces two new concepts (templates, planned allocations) and
enhances the existing budget summary with planned vs actual comparison.

The backend is split into three NATS services (`budget-service`,
`category-service`, `transaction-service`) behind a FastAPI gateway. Each
service owns its own PostgreSQL database. Categories are global entities owned
by category-service. The gateway already performs multi-service orchestration for
health checks; this change adds a second aggregation point for the summary.

## Goals / Non-Goals

**Goals:**
- Named, reusable budget templates stored independently of any concrete budget.
- Planned allocations as a first-class entity (`budget + category + planned_amount`),
  distinct from transactions.
- Template application: one-time copy of line items as allocations; merge
  semantics (keep existing allocation if the category already has one).
- Ad-hoc allocation management: create, update, and delete individual allocations
  without a template.
- Enhanced `GET /budgets/{budget_id}/summary`: planned vs actual at both
  aggregate and per-category level.
- Template selector in the budget creation form and budget detail page.

**Non-Goals:**
- Live link between a template and its derived budgets (template edits never
  propagate to existing budgets).
- Importing an existing budget as a template.
- Per-template permissions or sharing between users.
- Time-series planning (weekly/monthly breakdown within a budget).
- Currency handling beyond the existing decimal-as-string convention.

## Decisions

### Decision 1 — Templates and allocations live in budget-service

Templates are blueprints for budgets; allocations are a budget's plan. Both are
planning concerns, not transaction concerns. Placing them in budget-service keeps
transaction-service focused on actual financial facts.

Trade-off: `GET /budgets/{budget_id}/summary` now requires the gateway to make
two NATS calls — `budget.allocation.list` and `transaction.summary.categories`
— and merge the results. This is consistent with the existing multi-service
health-check aggregation pattern in the gateway.

### Decision 2 — Planned allocations are a separate entity, not a transaction type

A transaction records something that happened (amount, date, category). A planned
allocation records intent (planned amount, category) with no date and no
confirmed occurrence. Mixing them into one table would require filtering every
transaction query on a `planned` flag, muddy the transaction list semantics, and
force planned records to carry a date they don't logically have.

See ADR 0001 for the full trade-off analysis.

### Decision 3 — One-time copy when applying a template

Applying a template copies its line items as allocations at that moment.
Subsequent changes to the template do not affect the budget. A live link would
silently alter a budget the user is actively working with, which is surprising
and destructive. Budget periods are finite and intentional; their plan should be
stable once started.

### Decision 4 — Merge semantics on apply

If the budget already has a planned allocation for a category that also appears
in the template, the existing allocation is kept and the template's value for
that category is skipped. Replacing existing work would be destructive.
Overwriting on a per-item basis would silently undo manual adjustments.

### Decision 5 — Category deletion cascades through template line items

When a category is deleted, every template line item referencing that category
is deleted. This mirrors the existing cascade behaviour for transactions
(`category.deleted` removes all transactions using that category). Budget-service
subscribes to `category.deleted` events and deletes the affected line items.
Blocking deletion at the category-service level would add friction for a planning
artifact that category-service cannot even see.

### Decision 6 — Summary aggregation in the gateway

The enhanced summary requires planned amounts (from budget-service) and actual
per-category sums (from transaction-service). The gateway issues two NATS
requests and merges them:

1. `budget.allocation.list` → `[(category_id, planned_amount)]`
2. `transaction.summary.categories` → `[(category_id, kind, income, expense)]`

The union of category IDs from both sources forms the rows of the response.
Categories appearing only in allocations have actual `"0.00"`. Categories
appearing only in transactions have planned `"0.00"`.

A new `transaction.summary.categories` subject is added to transaction-service
(sibling to the existing `transaction.summary`); it returns per-category actual
sums for a given `budget_id`.

### Decision 7 — Summary response shape (breaking change)

The existing `BudgetSummary` response is extended:

```json
{
  "budget_id": 1,
  "totals": {
    "planned_income": "1500.00",
    "actual_income": "1200.00",
    "planned_expense": "900.00",
    "actual_expense": "650.00",
    "net": "550.00"
  },
  "categories": [
    {
      "category_id": 3,
      "kind": "expense",
      "planned_amount": "500.00",
      "actual_amount": "320.00"
    }
  ]
}
```

`totals.net` remains `actual_income − actual_expense`. `totals` gains four
fields; the old `income`/`expense`/`net` keys are replaced. This is a breaking
change to the `transaction-summary-api` shape; the frontend is updated in the
same change.

### Decision 8 — NATS subject naming

Follows the existing `<domain>.<noun>.<operation>` pattern:

| Subject | Owner | Kind |
|---|---|---|
| `budget.template.create` | budget-service | request/reply |
| `budget.template.list` | budget-service | request/reply |
| `budget.template.get` | budget-service | request/reply |
| `budget.template.update` | budget-service | request/reply |
| `budget.template.delete` | budget-service | request/reply |
| `budget.template.item.add` | budget-service | request/reply |
| `budget.template.item.delete` | budget-service | request/reply |
| `budget.template.apply` | budget-service | request/reply |
| `budget.allocation.create` | budget-service | request/reply |
| `budget.allocation.list` | budget-service | request/reply |
| `budget.allocation.update` | budget-service | request/reply |
| `budget.allocation.delete` | budget-service | request/reply |
| `transaction.summary.categories` | transaction-service | request/reply |

### Decision 9 — REST routes

| Method | Path | Description |
|---|---|---|
| `POST` | `/templates` | Create template |
| `GET` | `/templates` | List templates |
| `GET` | `/templates/{template_id}` | Get template with line items |
| `PUT` | `/templates/{template_id}` | Update template name |
| `DELETE` | `/templates/{template_id}` | Delete template and its line items |
| `POST` | `/templates/{template_id}/items` | Add line item to template |
| `DELETE` | `/templates/{template_id}/items/{item_id}` | Remove line item |
| `POST` | `/budgets/{budget_id}/apply-template` | Apply a template to a budget |
| `GET` | `/budgets/{budget_id}/allocations` | List allocations for a budget |
| `POST` | `/budgets/{budget_id}/allocations` | Create allocation |
| `PUT` | `/budgets/{budget_id}/allocations/{allocation_id}` | Update planned amount |
| `DELETE` | `/budgets/{budget_id}/allocations/{allocation_id}` | Delete allocation |

`GET /budgets/{budget_id}/summary` is modified in-place (breaking response shape change).

## Risks / Trade-offs

- **Breaking summary shape.** Frontend and any other consumers of
  `GET /budgets/{budget_id}/summary` must be updated in the same deploy.
  → Mitigation: frontend is updated in this change; no other known consumers.
- **Gateway aggregation latency.** The summary now requires two serial or
  parallel NATS round-trips instead of one. → Two requests can be issued in
  parallel (asyncio.gather); sub-millisecond overhead on a healthy local stack.
- **Budget-service has no category projection.** To include category names in
  allocation responses the service would need to subscribe to category events.
  → Deferred: allocation responses return `category_id` only; the frontend
  resolves names from its already-loaded global category list.
- **Eventual consistency on category cascade.** A `category.deleted` event may
  arrive at budget-service after a template-apply that already copied the line
  item into allocations. The allocation referencing the deleted category remains
  valid (it records a historical planned amount). Only new line items are
  cascade-deleted. → Acceptable; allocations are planning records, not enforced
  references.

## Migration Plan

1. Add `templates`, `template_items`, and `allocations` tables to `budget-db`
   via Alembic (or inline `Base.metadata.create_all`). Additive; no existing
   data is affected.
2. Deploy updated budget-service (new handlers + category.deleted subscription).
3. Deploy updated transaction-service (new `transaction.summary.categories`
   subject).
4. Deploy updated gateway (new routes + enhanced summary aggregation).
5. Deploy updated frontend (template selector, allocation panel, updated
   summary display).

All steps are additive except the summary shape change; steps 4 and 5 must be
deployed together.

## Open Questions

- Should `planned_amount` be nullable in allocations (to mark a category as
  "tracked but unplanned")? **Assumed no** — if there is no plan, there is no
  allocation row.
- Should deleting a budget cascade-delete its allocations?
  **Assumed yes** — budget-service handles this internally (same process,
  same database) rather than via an event.
