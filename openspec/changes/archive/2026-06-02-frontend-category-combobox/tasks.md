## 1. Backend: enforce the kind invariant

- [x] 1.1 In `backend/services/transaction/handlers.py`, extend `_validate` to fetch the `CategoryProjection` and reject with `ServiceError(422, ...)` when its `kind` does not match `data.type` (applies to both create and update, before commit).
- [x] 1.2 Update the comment in `summarize_by_category` that assumes a category may appear under both kinds, reflecting that type now always equals the category's kind for new/edited transactions.
- [x] 1.3 Add transaction-service tests in `backend/services/transaction/tests/test_transaction.py` for the mismatch case on create and on update (422, nothing written), plus a passing matched-kind case.

## 2. Frontend: reusable CategoryCombobox

- [x] 2.1 Create `frontend/src/components/CategoryCombobox.tsx` on Mantine `Combobox`, props `{ categories, kind, value, onChange, onCreateCategory, disabled }`; render disabled when `kind` is unset.
- [x] 2.2 Filter options to the active `kind`; implement type-to-filter with the best match highlighted.
- [x] 2.3 Implement the keyboard/create contract: Tab accepts the highlighted existing category; Enter selects an exact (kind-scoped) name match or creates when none; show a "Create '<query>'" row when the query is non-empty and not an exact match.
- [x] 2.4 On create, call `onCreateCategory({ name, kind })`, then select the returned category; surface API rejection inline.
- [x] 2.5 When `kind` changes, clear the selection if the selected category's kind no longer matches.

## 3. Frontend: wire into the forms

- [x] 3.1 In `TransactionForm.tsx`, remove the Type default (start unselected), replace the category `Select` with `CategoryCombobox` driven by the Type, and drop the `+ New category` button.
- [x] 3.2 Delete `frontend/src/components/InlineCategoryCreator.tsx` and its imports/usages.
- [x] 3.3 In `AllocationPanel.tsx`'s Add-allocation form, add an income/expense `SegmentedControl` (starts empty) and replace the category `Select` with `CategoryCombobox` driven by it; pass an `onCreateCategory` that calls `api.createCategory` and reloads.
- [x] 3.4 Ensure both forms cannot submit until a kind and a category are chosen.

## 4. Frontend tests

- [x] 4.1 Add `CategoryCombobox` tests (jest + msw): disabled until kind set; kind filtering; Tab-select; Enter exact-match select (no duplicate); Enter create; create-row create; kind change clears invalid selection.
- [x] 4.2 Update `TransactionForm` / `BudgetDetailPage` tests for the unset Type gate and picker-based inline create; remove `InlineCategoryCreator`-specific assertions.
- [x] 4.3 Update `AllocationPanel` tests for the new income/expense toggle gating the picker and inline create.

## 5. Verify

- [x] 5.1 Run the frontend test suite (`npm test` in `frontend/`) and the transaction-service tests; confirm all pass.
- [x] 5.2 `openspec validate frontend-category-combobox` passes.

## 6. Backend — category usage + purge subjects

- [x] 6.1 transaction-service: add `transaction.category.usage` (count transactions by `category_id`) and `transaction.category.purge` (delete all transactions for a `category_id`, idempotent) handlers and `HANDLERS` entries; add tests.
- [x] 6.2 budget-service: add `budget.category.usage` (counts of allocations + template line items for a `category_id`) and `budget.category.purge` (delete those allocations + template line items, idempotent) handlers and subjects; add tests.

## 7. Gateway — in-use guard, usage-enriched list, erase history

- [x] 7.1 Enrich `GET /categories` with per-category usage (`in_use` + transaction/allocation/template counts) via bulk `*.category.usage` calls to transaction-service and budget-service, merged.
- [x] 7.2 Guard `DELETE /categories/{id}`: query usage first; if in use return `409` with impact counts and do not call `category.delete`; otherwise delete as today.
- [x] 7.3 Add `POST /categories/{id}/erase-history`: fan out `transaction.category.purge` + `budget.category.purge`; make it safely re-runnable on partial failure.
- [x] 7.4 Gateway tests for the guard (409 + counts), the usage-enriched list, and erase-history.

## 8. Frontend — Categories page

- [x] 8.1 `api/types` + `api/client`: add usage fields to the category list response and an `eraseCategoryHistory(id)` call.
- [x] 8.2 `CategoriesPage`: render **Erase history** vs **Delete** per row from `in_use` (never both).
- [x] 8.3 Erase-history confirmation modal showing impact counts; on confirm call the API and reload the list so the row flips to **Delete**.
- [x] 8.4 msw handlers: usage in the list, `409`-with-counts on in-use delete, and the erase-history route; add/update `CategoriesPage` tests.
- [x] 8.5 Harden `CategoriesPage`: offer Delete only when `in_use === false` and Erase history only when `in_use === true`; an absent/unknown usage flag (e.g. a stale gateway) shows no destructive action. Covered by a test that simulates a usage-less list response.
- [x] 8.6 Fix double-create in `CategoryCombobox`: disable Mantine's built-in keyboard navigation (`Combobox.Target withKeyboardNavigation={false}`) so Enter is handled only once; a real Enter previously fired both our handler and Mantine's option-submit, creating the category then 409-ing on the duplicate. Regression test asserts a real Enter creates exactly once.

## 9. Verify (deletion guard + erase history)

- [x] 9.1 Run backend suites (transaction-service, budget-service, gateway) and the frontend tests; confirm all pass.
- [x] 9.2 `openspec validate frontend-category-combobox` passes.
