## 1. Shared schemas

- [x] 1.1 Add `BudgetSummary` and `BudgetSummaryTotals` Pydantic models to `backend/common/schemas.py`, with `income`, `expense`, and `net` as `Decimal` serialized to strings with two decimal places (mirroring `TransactionRead.amount`)

## 2. Transaction-service handler

- [x] 2.1 Add `summarize_transactions(db, request)` to `backend/services/transaction/handlers.py` that:
  - validates `budget_id` exists in `budget_projection` (raise `ServiceError(status=404, ...)` otherwise)
  - computes `income` and `expense` with `COALESCE(SUM(amount) FILTER (WHERE type = ...), 0)` over `transactions` filtered by `budget_id`
  - sets `net = income - expense` in Python, keeping values as `Decimal`
  - returns `Outcome(reply=<serialized BudgetSummary>, event_change=None)`
- [x] 2.2 Subscribe to the `transaction.summary` subject in `backend/services/transaction/main.py` using `make_rpc_callback(...)` alongside the existing five
- [x] 2.3 Add pytest cases in `backend/services/transaction/tests/`:
  - summary returned for a budget with mixed income + expense transactions
  - `totals.net = income - expense` is correct for non-trivial values
  - empty summary returned for a budget with no transactions (income, expense, and net are `"0.00"`)
  - 404 for a `budget_id` that does not exist in `budget_projection`
  - decimal precision: `SUM` of `12.50` + `7.50` serializes as `"20.00"` (string, two decimal places)

## 3. Gateway route

- [x] 3.1 Add `GET /budgets/{budget_id}/summary` to `backend/gateway/routers/transactions.py`, calling `await call("transaction.summary", {"budget_id": budget_id})` and returning the result (response model `BudgetSummary`)
- [x] 3.2 Add a gateway test in `backend/gateway/tests/` covering the happy path and 404, using the same NATS mocking approach as the existing transaction route tests

## 4. Frontend API client

- [x] 4.1 Add `BudgetSummary` and `BudgetSummaryTotals` types to `frontend/src/api/types.ts` (decimals as `string`)
- [x] 4.2 Add `api.getBudgetSummary(budgetId: number)` to `frontend/src/api/client.ts`

## 5. Verification

- [x] 5.1 `cli test transaction` — transaction-service tests pass
- [x] 5.2 `cli test gateway` — gateway tests pass
- [x] 5.3 `cli frontend test` — frontend tests still pass (the new client method has no consumer in this change)
- [ ] 5.4 `cli compose up -d` then `curl http://localhost:8000/budgets/{id}/summary` against a budget with known transactions and confirm the totals match
