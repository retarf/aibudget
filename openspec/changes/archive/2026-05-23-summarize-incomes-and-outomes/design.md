## Context

The backend is split into three NATS-backed domain services (`budget`,
`category`, `transaction`) behind a FastAPI gateway, each with its own
PostgreSQL database. The transaction-service already maintains a local
`budget_projection` seeded from `budget.*` events, so it can validate
transaction writes — and now aggregations — against a budget identifier
without cross-service calls.

The frontend is a React + Mantine SPA. `/reports` is wired into the nav and
`ReportsPage` is currently a stub. This change does not touch the page yet;
it only delivers the backend endpoint and a typed frontend API client
method, so a follow-up change can wire the UI without a backend dependency.

## Goals / Non-Goals

**Goals:**
- Provide a single endpoint that returns a per-budget summary (income,
  expense, net) in one round-trip.
- Compute aggregates inside transaction-service using its existing local
  projection — no cross-service RPC, no gateway-side fan-out.
- Preserve the decimal-as-string serialization used by the transaction API
  so future consumers reuse current formatting.
- Ship a typed `api.getBudgetSummary` client method so a follow-up
  frontend change can consume the endpoint without further plumbing.

**Non-Goals:**
- Per-category breakdown.
- Time-series (per-day/week/month) breakdowns.
- Top-N transactions, multi-budget rollups, cross-budget comparisons.
- CSV/PDF export.
- A dedicated report-service with materialized views.
- Replacing the Reports page (`ReportsPage.tsx`) — deferred to a follow-up
  change. No MSW handler or Reports page tests are added here.
- Authentication or per-user scoping (the app doesn't have users yet).

## Decisions

### Decision 1 — Aggregate inside transaction-service via SQL

The new handler runs a single SQL statement against the service's own
`transactions` table:
`SUM(amount) FILTER (WHERE type = 'income')` and
`SUM(amount) FILTER (WHERE type = 'expense')`, filtered by `budget_id`.
`net` is computed in the handler as `income - expense`. A pre-check against
`budget_projection` distinguishes 404-missing-budget from 200-empty-summary.

**Why not a new report-service?** A separate service would have to
subscribe to `transaction.*` events and maintain a derived store — a lot of
machinery for a single SQL `SUM`. Extend the existing service.

**Why not aggregate in the gateway?** The gateway would have to call
`transaction.list`, deserialize every row, and sum in Python — O(N) network
and memory for what Postgres does in one statement. It also leaks domain
logic out of the service that owns the data.

### Decision 2 — Response shape

```json
{
  "budget_id": 1,
  "totals": { "income": "120.00", "expense": "45.50", "net": "74.50" }
}
```

- `totals.net` is computed server-side so the spec has a single source of
  truth for what "net" means and the client doesn't repeat the subtraction.
- All monetary fields are decimal strings with two decimal places, matching
  `TransactionRead.amount` (Decimal → `str` via Pydantic).

### Decision 3 — NATS subject `transaction.summary`

Follows the existing `<domain>.<operation>` convention (sibling to
`transaction.list`, `transaction.get`). The handler returns
`Outcome(reply=..., event_change=None)` — pure read, no event published.
Subscription is added in `backend/services/transaction/main.py` alongside
the existing five.

### Decision 4 — Gateway route `GET /budgets/{budget_id}/summary`

Lives in `backend/gateway/routers/transactions.py`, alongside the existing
`/budgets/{budget_id}/transactions` routes. Body is one line:
`return await call("transaction.summary", {"budget_id": budget_id})`. The
existing `call(...)` helper maps service envelope errors to HTTP status
codes, so 404-for-missing-budget propagates without extra code.

A separate `reports.py` router was considered and rejected: only one route
exists for v1, and it's keyed on `budget_id`, which makes it a natural
sibling to the other budget-scoped routes.

### Decision 5 — Frontend: typed client method only, no UI

`api.getBudgetSummary(budgetId)` is added to `frontend/src/api/client.ts`
and the matching `BudgetSummary` / `BudgetSummaryTotals` types are added to
`frontend/src/api/types.ts`. The Reports page itself stays a stub for this
change; a follow-up change will consume the new method.

The split keeps this change small and lets the backend land independently;
the follow-up only has to touch the page and its test mock.

## Risks / Trade-offs

- **Decimal precision when summing in SQL.** Postgres `SUM(NUMERIC)`
  returns `NUMERIC` and SQLAlchemy maps it to `Decimal`, which Pydantic
  serializes to a string. Risk is low so long as the handler keeps values
  as `Decimal` and never routes through `float`. → Mitigation: a unit test
  that `SUM(12.50 + 7.50)` serializes as `"20.00"` (string, two decimal
  places).

- **Empty `SUM` returns NULL, not zero.** `SUM` over zero rows is NULL.
  → Mitigation: `COALESCE(SUM(...), 0)` in the query, with a regression
  test for the empty-budget case asserting `"0.00"`.

- **An unused client method ships before its UI.** `api.getBudgetSummary`
  is added without any caller. Acceptable because it's typed, tiny, and
  the follow-up change is already scoped. → Mitigation: none needed;
  unused exports are tree-shaken from the production bundle.

## Migration Plan

The change is additive: no schema migrations, no breaking changes to
existing endpoints or NATS subjects, no removed code paths. Deploy order:
transaction-service first (so the new RPC subject is live), then the
gateway. The frontend client method ships whenever the frontend is next
deployed and has no runtime effect until the follow-up wires it up.

## Open Questions

- Should `net` be omitted when both totals are zero, or always returned?
  **Decision:** always returned (`"0.00"`), so future consumers don't
  branch on presence.
