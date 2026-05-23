## Why

Users can record incomes and expenses against a budget but have no way to see
how the budget is doing in aggregate. The Reports page is wired into the nav
menu but currently shows only a placeholder ("Reports will appear here"). This
change delivers the first real reporting feature: a per-budget summary of
incomes vs. expenses.

## What Changes

- Add a `transaction.summary` NATS RPC handler to `transaction-service` that,
  given a `budget_id`, aggregates the service's own transactions into:
  - totals: `income`, `expense`, `net` (income − expense),
- Add a `GET /budgets/{budget_id}/summary` route on the API gateway that
  forwards to `transaction.summary` using the existing `call(...)` helper.
- Add a `BudgetSummary` Pydantic model to `backend/common/schemas.py`.
- Extend the frontend API client (`api.getBudgetSummary`) and types
  (`BudgetSummary`).

## Capabilities

### New Capabilities

- `transaction-summary-api`: Backend capability covering the new
  `transaction.summary` RPC and `GET /budgets/{budget_id}/summary` gateway
  route — its inputs, response shape, validation, and error behavior.

### Modified Capabilities

<!-- None. `transaction-api` is untouched (existing CRUD subjects are unchanged);
     `app-shell` already exposes the /reports route. The new endpoint and page
     are additive, so they live in their own new capabilities rather than as
     deltas against the existing ones. -->

## Impact

- **New code (backend)**: `backend/services/transaction/handlers.py` (new
  handler), `backend/services/transaction/main.py` (new subscription),
  `backend/common/schemas.py` (new `BudgetSummary` model),
  `backend/gateway/routers/transactions.py` (new route).
- **Tests**: new pytest cases for the handler and gateway route;
- **APIs**: additive — no breaking changes to existing endpoints.
- **Dependencies**: none. The page uses only Mantine components already in
  use; no chart library is introduced in v1.
- **Out of scope**: time-series charts, top-N transactions, cross-budget
  rollups, CSV/PDF export. These are deferred to follow-up changes.
