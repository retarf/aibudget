## 1. Shared schemas

- [x] 1.1 Add `TemplateCreate`, `TemplateRead`, `TemplateItemCreate`,
      `TemplateItemRead` Pydantic models to `backend/common/schemas.py`
- [x] 1.2 Add `AllocationCreate`, `AllocationRead`, `AllocationUpdate` Pydantic
      models to `backend/common/schemas.py`
- [x] 1.3 Add `ApplyTemplateRequest` schema (`template_id: int`) to
      `backend/common/schemas.py`
- [x] 1.4 Replace `BudgetSummary` / `BudgetSummaryTotals` in
      `backend/common/schemas.py` with the enhanced shape: `planned_income`,
      `actual_income`, `planned_expense`, `actual_expense`, `net` in totals;
      add `BudgetSummaryCategory` (`category_id`, `kind`, `planned_amount`,
      `actual_amount`) and a `categories` list on `BudgetSummary`
- [x] 1.5 Add `CategorySummary` Pydantic model to `backend/common/schemas.py`
      for the `transaction.summary.categories` reply
      (`[{category_id, kind, income, expense}]`)

## 2. budget-service — data model

- [x] 2.1 Add `templates` table to `backend/services/budget/models.py`:
      `id`, `name`
- [x] 2.2 Add `template_items` table: `id`, `template_id` (FK → templates),
      `category_id` (plain int, no cross-DB FK), `planned_amount` (Numeric).
      Unique constraint on `(template_id, category_id)`.
- [x] 2.3 Add `allocations` table: `id`, `budget_id` (FK → budgets),
      `category_id` (plain int), `planned_amount` (Numeric).
      Unique constraint on `(budget_id, category_id)`.
      Cascade-delete when the parent budget is deleted.

## 3. budget-service — template handlers

- [x] 3.1 Add `create_template`, `list_templates`, `get_template`,
      `update_template`, `delete_template` to
      `backend/services/budget/handlers.py`; `delete_template` cascades
      `template_items` (handled by SQL FK ON DELETE CASCADE)
- [x] 3.2 Add `add_template_item` (insert; reject if category already in
      template) and `delete_template_item` to handlers
- [x] 3.3 Add `apply_template(db, budget_id, template_id)` handler: load all
      items for the template; for each item, skip if an allocation for that
      `(budget_id, category_id)` already exists; otherwise insert
- [x] 3.4 Subscribe to `budget.template.{create,list,get,update,delete}`,
      `budget.template.item.{add,delete}`, and `budget.template.apply` in
      `backend/services/budget/main.py`
- [x] 3.5 Add pytest cases in `backend/services/budget/tests/`:
      - template CRUD happy paths
      - duplicate category in same template returns 409
      - apply merges correctly (existing allocation kept, new one inserted)
      - apply with unknown budget or template returns 404

## 4. budget-service — allocation handlers

- [x] 4.1 Add `create_allocation`, `list_allocations`, `update_allocation`,
      `delete_allocation` to `backend/services/budget/handlers.py`;
      `create_allocation` rejects if `(budget_id, category_id)` already exists
      (409)
- [x] 4.2 Subscribe to `budget.allocation.{create,list,update,delete}` in
      `backend/services/budget/main.py`
- [x] 4.3 Add pytest cases: allocation CRUD; duplicate allocation returns 409;
      allocation for unknown budget returns 404

## 5. budget-service — category.deleted cascade

- [x] 5.1 Add a `category.deleted` event subscriber in
      `backend/services/budget/main.py` that deletes all `template_items`
      rows where `category_id` matches the deleted category's id
- [x] 5.2 Add pytest cases: after `category.deleted`, template items for that
      category are removed; template items for other categories are untouched

## 6. transaction-service — per-category summary

- [x] 6.1 Add `summarize_by_category(db, request)` handler to
      `backend/services/transaction/handlers.py`: for the given `budget_id`,
      `GROUP BY category_id, type` with `SUM(amount)`; return a list of
      `{category_id, kind, income, expense}` entries; 404 if budget not in
      projection
- [x] 6.2 Subscribe to `transaction.summary.categories` in
      `backend/services/transaction/main.py`
- [x] 6.3 Add pytest cases: returns correct per-category sums; empty result for
      budget with no transactions; 404 for unknown budget

## 7. API gateway — template and allocation routes

- [x] 7.1 Add `backend/gateway/routers/templates.py` with REST routes for
      template CRUD, item add/delete, and apply-template; each handler calls
      `await call("budget.template.*", ...)` using the existing helper
- [x] 7.2 Add `backend/gateway/routers/allocations.py` with REST routes for
      allocation CRUD under `/budgets/{budget_id}/allocations`
- [x] 7.3 Mount both routers in `backend/gateway/main.py`
- [x] 7.4 Add gateway tests covering happy paths and error envelopes for
      templates and allocations

## 8. API gateway — enhanced summary

- [x] 8.1 Replace the single `call("transaction.summary", ...)` in
      `backend/gateway/routers/transactions.py` with two parallel NATS calls
      (`asyncio.gather`): `budget.allocation.list` and
      `transaction.summary.categories`
- [x] 8.2 Merge results in the gateway: union of category IDs from both sources;
      compute `planned_totals` and `actual_totals` from the merged rows; set
      `actual_amount = "0.00"` for categories present only in allocations, and
      `planned_amount = "0.00"` for categories present only in transactions
- [x] 8.3 Return the enhanced `BudgetSummary` shape
- [x] 8.4 Add gateway tests: summary with allocations and transactions; summary
      with allocations only (no transactions); summary with transactions only
      (no allocations); 404 for unknown budget

## 9. Frontend — types and API client

- [x] 9.1 Add `Template`, `TemplateItem`, `TemplateCreate`, `ApplyTemplate`
      types to `frontend/src/api/types.ts`
- [x] 9.2 Add `Allocation`, `AllocationCreate`, `AllocationUpdate` types
- [x] 9.3 Update `BudgetSummary` / `BudgetSummaryTotals` types to match the new
      shape; add `BudgetSummaryCategory`
- [x] 9.4 Add `api.listTemplates`, `api.createTemplate`, `api.deleteTemplate`,
      `api.addTemplateItem`, `api.deleteTemplateItem`, `api.applyTemplate`
      to `frontend/src/api/client.ts`
- [x] 9.5 Add `api.listAllocations`, `api.createAllocation`,
      `api.updateAllocation`, `api.deleteAllocation`

## 10. Frontend — template selector in budget form

- [x] 10.1 Add an optional `Select` for "Start from a template" to
       `frontend/src/components/BudgetForm.tsx`; fetch template list on mount;
       when a template is selected, call `api.applyTemplate` after budget
       creation succeeds
- [x] 10.2 Add MSW handler for `/templates` in test fixtures; update
       `BudgetForm` tests

## 11. Frontend — allocation management panel

- [x] 11.1 Add `AllocationPanel` component to
       `frontend/src/components/AllocationPanel.tsx`: lists current
       allocations for the open budget, allows adding (category select +
       amount), editing (inline amount field), and deleting
- [x] 11.2 Add "Apply template" action to `AllocationPanel` (opens a modal
       to pick a template, then calls `api.applyTemplate`)
- [x] 11.3 Wire `AllocationPanel` into the budget detail view
       (`BudgetsPage.tsx` or its budget-detail sub-view)
- [x] 11.4 Add MSW handlers and tests for `AllocationPanel`

## 12. Frontend — enhanced summary display

- [x] 12.1 Update the summary display (currently in `BudgetsPage.tsx` or
       `ReportsPage.tsx`) to render the new shape: aggregate planned vs actual
       totals, and the per-category breakdown table
- [x] 12.2 Update MSW handler for `/budgets/{id}/summary` to return the new
       shape; fix any broken snapshot or assertion tests

## 13. Frontend — templates management page

- [x] 13.1 Add `TemplatesPage` to `frontend/src/pages/TemplatesPage.tsx`:
       list all templates, create form, delete confirmation
- [x] 13.2 Add a `Templates` entry to `NavMenu` and a `/templates` route in
       `App.tsx`
- [x] 13.3 Add a template detail view (inline or sub-route) that shows the
       template's items, lets the user add an item (category Select + amount)
       and delete individual items
- [x] 13.4 Surface the 409 from the API as a form error on add-item when the
       category already has an item in the template
- [x] 13.5 Add MSW handlers in `frontend/src/mocks/handlers.ts` for any
       template/item endpoint not already covered (PUT/templates/:id, etc.)
- [x] 13.6 Add jest+msw tests in `frontend/src/__tests__/TemplatesPage.test.tsx`
       covering: list, create, add item, add duplicate item shows the API
       error, delete item, delete template

## 14. Verification

- [x] 14.1 `cli test budget` — budget-service tests pass (templates,
       allocations, cascade)
- [x] 14.2 `cli test transaction` — transaction-service tests pass
       (summary.categories)
- [x] 14.3 `cli test gateway` — gateway tests pass (new routes, enhanced
       summary)
- [x] 14.4 `cli frontend test` — frontend tests pass (including new
       Templates page)
- [x] 14.5 `cli compose up -d` — manual smoke test: create a template from the
       Templates page, create a budget from the template, add a transaction,
       verify summary shows correct planned vs actual figures
