## Why

The previous change shipped a backend endpoint (`GET /budgets/{id}/summary`)
and a typed frontend client method (`api.getBudgetSummary`), but no UI
consumes them yet. Today, when a user opens a budget's detail page they see
the transaction list with no aggregate view — they have to add the numbers
themselves to know whether they're under, on, or over budget.

This change adds the missing UI: a totals block at the top of the budget
detail page showing income, expense, and net for that budget and totals
columns showing income, expense, and net for budget list.

## What Changes

- Display a totals block (income / expense / net) at the top of
  `BudgetDetailPage`, between the period line and the transactions table,
  driven by `api.getBudgetSummary(budgetId)`.
- Refresh the detail page's totals whenever a transaction is created,
  edited, or deleted, so the numbers stay in lockstep with the visible
  list.
- Add three new columns (Income, Expense, Net) to the budgets list table
  in `BudgetsPage`, one row per budget, each row driven by its own
  `api.getBudgetSummary(budgetId)` call fired in parallel after the
  budgets list loads.
- Refresh the list-page totals after a budget is created, edited, or
  deleted (the budget list already reloads in these cases — the summaries
  follow).
- Surface summary load errors on both pages using the existing `Alert`
  pattern.
- Extend the frontend MSW handlers with a `GET /budgets/:id/summary` mock
  that computes the summary from the in-memory seed store, so the pages
  are testable.
- Extend the jest tests for `BudgetDetailPage` and `BudgetsPage` to cover
  totals rendering, refresh after writes, and error-state handling.

## Capabilities

### New Capabilities

<!-- None — this is a feature added to existing capabilities. -->

### Modified Capabilities

- `transaction-pages`: A budget's detail view now also shows aggregate
  totals (income, expense, net) for the budget, refreshing alongside the
  transaction list.
- `budget-pages`: The budgets list now shows per-budget income, expense,
  and net columns.

## Impact

- **Modified code**: `frontend/src/pages/BudgetDetailPage.tsx` (new totals
  block, new `useApiResource` for the summary, refetch on writes),
  `frontend/src/pages/BudgetsPage.tsx` (new totals columns, per-row
  summary fetch, refetch on writes),
  `frontend/src/mocks/handlers.ts` (new summary handler),
  `frontend/src/__tests__/BudgetDetailPage.test.tsx` and
  `frontend/src/__tests__/BudgetsPage.test.tsx` (new test cases).
- **APIs**: consumes the existing `GET /budgets/{id}/summary`; no backend
  changes.
- **Dependencies**: none. Built from Mantine primitives already in use.
- **Out of scope**: per-category breakdown, time-series, charts, totals
  on the Dashboard, totals on the still-stub Reports page, and a batched
  `/budgets/summaries` endpoint (the list page fires N parallel summary
  requests for now). All deferred to follow-up changes.
