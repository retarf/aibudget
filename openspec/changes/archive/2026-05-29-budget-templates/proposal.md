## Why

Creating a new budget requires the user to manually add planned spending amounts
for every category — even when the new budget closely resembles previous ones.
There is no way to save and reuse a budget structure. Users who run the same
monthly household budget repeatedly have to re-enter the same category/amount
pairs from scratch every time.

## What Changes

- Introduce **Budget Templates**: named, reusable entities that hold a set of
  (category, planned_amount) pairs. Templates are created and managed
  independently of any concrete budget.
- Introduce **Planned Allocations**: a first-class `(budget, category,
  planned_amount)` association on a specific budget. Allocations express intent
  and are separate from transactions (which record actual spend). Allocations can
  be created ad-hoc on any budget or bulk-created by applying a template.
- Add a **template-apply** action: applying a template to a budget copies its
  line items as planned allocations (one-time copy; later changes to the template
  do not affect the budget). If the budget already has an allocation for a
  category the template also covers, the existing allocation is kept.
- Enhance `GET /budgets/{budget_id}/summary` to show **planned vs actual** at
  both aggregate and per-category level. Categories with a planned allocation but
  no transactions appear with actual `"0.00"`. The gateway merges allocation data
  from budget-service with actuals from transaction-service.
- Add a dedicated **Templates page** with its own navigation entry, allowing
  users to create templates, manage their line items (add/remove a category
  with a planned amount), and delete templates.
- Update the **budget creation form** to include an optional template selector.
  Users can also apply a template to an existing budget at any time.

## Capabilities

### New Capabilities

- `template-api`: REST endpoints for template CRUD and the apply-template action.
- `allocation-api`: REST endpoints for planned allocation CRUD on a budget.
- `budget-service-planning`: budget-service NATS handlers for templates and
  allocations; cascade behaviour when a referenced category is deleted.
- `template-pages`: frontend page for creating and managing templates and
  their line items, reachable from the main navigation.

### Modified Capabilities

- `budget-summary-enhanced`: replaces `transaction-summary-api` — the summary
  now covers planned vs actual at both aggregate and per-category level, with
  the gateway aggregating two NATS calls.
- `api-gateway`: new routes for templates and allocations; enhanced summary
  aggregation.
- `budget-pages`: optional template selector added to the budget creation form
  and the budget detail page.

## Impact

- **New code (backend)**: templates and allocations tables and handlers in
  `budget-service`; new NATS subjects (`budget.template.*`,
  `budget.allocation.*`); `transaction.summary.categories` subject for
  per-category actuals; gateway routes and aggregation logic.
- **Schema**: two new tables in `budget-db` (`templates`, `template_items`,
  `allocations`); no changes to other service databases.
- **APIs**: new REST routes are additive; `GET /budgets/{id}/summary` response
  shape changes (breaking: adds `planned_totals` and `categories` fields).
- **Frontend**: new Templates page (list + create + item management + delete)
  with a navigation entry; template selector in the budget creation form;
  allocation management UI on the budget detail page; updated summary display.
- **Events**: budget-service subscribes to `category.deleted` to cascade-delete
  template line items referencing the removed category.
