## 1. BudgetDetailPage totals block

- [x] 1.1 Add a `summary` resource to `frontend/src/pages/BudgetDetailPage.tsx`: `useApiResource(() => api.getBudgetSummary(id), [id])` alongside the existing `budget`, `categories`, and `transactions` hooks
- [x] 1.2 Render a totals block between the period `Text` and the transactions section: a Mantine `Group` of three labeled values for income, expense, and net, sourced from `summary.data?.totals`. While `summary.data` is undefined, render nothing
- [x] 1.3 Include `summary.error` in the existing combined error `Alert`: `{budget.error ?? transactions.error ?? summary.error}`
- [x] 1.4 Introduce an inline `reloadAfterWrite()` helper that calls both `transactions.reload()` and `summary.reload()`. Replace the two existing `transactions.reload()` call sites (in `handleSubmit` and `handleDelete`) with `reloadAfterWrite()` so a future writer can't reload one without the other

## 2. BudgetsPage totals columns

- [x] 2.1 In `frontend/src/pages/BudgetsPage.tsx`, add `summaries` state (`Record<number, BudgetSummary>`) and `summariesError` state (`string | undefined`)
- [x] 2.2 Add a `useEffect` keyed on `budgets.data` that fires `api.getBudgetSummary(b.id)` for every budget in parallel via `Promise.all`, stores the resulting map in `summaries`, sets `summariesError` on failure, and uses a `cancelled` flag to ignore stale completions when `budgets.data` changes during the fetch
- [x] 2.3 Add three new `Table.Th` columns (Income, Expense, Net) before the actions column. Render each row's cell as `summaries[budget.id]?.totals.income` (etc.), falling back to an em-dash `—` while the summary is loading
- [x] 2.4 Render an additional `Alert color="red"` showing `summariesError` when set, alongside the existing `budgets.error` alert
- [x] 2.5 Confirm no explicit refetch wiring is needed in `handleSubmit` / `handleDelete`: `budgets.reload()` mutates `budgets.data`, which re-runs the effect

## 3. MSW handler

- [x] 3.1 Add a `http.get(\`${API}/budgets/:id/summary\`)` handler to `frontend/src/mocks/handlers.ts` that returns 404 for an unknown budget, otherwise computes income, expense, and net from `store.transactions` filtered by `budget_id`, formatted via `.toFixed(2)`, in the same shape the backend returns

## 4. Tests — BudgetDetailPage

- [x] 4.1 In `frontend/src/__tests__/BudgetDetailPage.test.tsx`, add a case that seeds a budget with both income and expense transactions, opens the page, and asserts the rendered income, expense, and net values match the seeded sums (use non-trivial amounts so the assertion proves real aggregation)
- [x] 4.2 Add a case that seeds a budget with no transactions and asserts the totals render as `0.00`
- [x] 4.3 Add a case that opens a budget, records a new transaction via the form, and asserts the totals update accordingly without reload
- [x] 4.4 Add a case that deletes an existing transaction and asserts the totals update accordingly without reload
- [x] 4.5 Add a case where the summary handler returns an error envelope and assert the page surfaces the error in the shared alert and renders no stale totals

## 5. Tests — BudgetsPage

- [x] 5.1 In `frontend/src/__tests__/BudgetsPage.test.tsx`, add a case that seeds two budgets with different transaction sets and asserts each row shows its own correct income / expense / net values
- [x] 5.2 Add a case that seeds a budget with no transactions and asserts its totals columns render as `0.00`
- [x] 5.3 Add a case that creates a new budget through the form and asserts the new row appears with `0.00` in all three totals columns
- [x] 5.4 Add a case that deletes a budget and asserts the remaining rows still show correct totals
- [x] 5.5 Add a case where the summary handler returns an error envelope and assert the page renders the additional error alert and does not show stale totals in the rows

## 6. Verification

- [x] 6.1 `cli frontend test` — all frontend tests pass
- [ ] 6.2 `cli compose up -d` then open the Budgets page in a browser, confirm the columns render; open a budget's detail page, record/edit/delete a transaction, and confirm both pages' totals update in lockstep
