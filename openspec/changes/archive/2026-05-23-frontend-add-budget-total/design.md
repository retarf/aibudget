## Context

`GET /budgets/{id}/summary` and `api.getBudgetSummary(id)` shipped in the
previous change but have no consumer. `BudgetDetailPage` already manages
a budget, its categories, and its transactions through three
`useApiResource` hooks, with a `transactions.reload()` call after every
create/edit/delete to keep the list current. `BudgetsPage` manages the
list of budgets through a single `useApiResource` and reloads it after
every create/edit/delete.

The Reports page is still a stub, intentionally, while we decide what
belongs there. This change targets the two pages where budgets are
already shown: the detail page (where users look at one budget's
transactions) and the list page (where users glance across all budgets).

## Goals / Non-Goals

**Goals:**
- Show a budget's income, expense, and net totals at the top of its
  detail page.
- Show per-budget income, expense, and net columns on the budgets list.
- Keep totals consistent with the visible data by refetching whenever the
  underlying list is refetched.
- Use only Mantine primitives already in the codebase — no new
  dependencies.
- No backend changes.

**Non-Goals:**
- Per-category breakdown, time-series, or charts.
- Showing totals on the Dashboard or the Reports page (still a stub).
- Optimistic UI for totals — a refetch after writes is good enough at
  this scale.
- A batched `/budgets/summaries` endpoint — see Decision 3.

## Decisions

### Decision 1 — Detail page: one `useApiResource` for the summary

Add `const summary = useApiResource(() => api.getBudgetSummary(id), [id])`
alongside the existing `budget`, `categories`, and `transactions` hooks
in `BudgetDetailPage`. This matches the existing pattern exactly; no new
abstractions.

**Why not derive totals client-side from `transactions.data`?** Three
reasons: (1) the server already computes `net` and handles the empty
case with `"0.00"`; (2) the existing decimal-as-string representation
means client-side arithmetic would have to pull in a decimal library or
fall back to floats; (3) keeping aggregation server-side keeps the page
honest when paginated/filtered transaction lists are introduced later.

### Decision 2 — Detail page: refresh totals on every transaction write

Wherever `transactions.reload()` is called today (in `handleSubmit` and
`handleDelete`), also call `summary.reload()`. A small inline helper
`reloadAfterWrite()` keeps the two reloads in lockstep so a future
writer can't reload one and forget the other.

### Decision 3 — List page: N parallel summary fetches, no backend change

After `budgets.data` loads, fire one `api.getBudgetSummary(b.id)` per
budget, in parallel. Store results in a map keyed by `budget_id`. Render
each row's totals from `summaries[budget.id]` when present; otherwise
show a dash or empty cell while loading.

**Why not a new batched endpoint?** A `GET /budgets/summaries` endpoint
would be the right call once we have many budgets, but: (1) realistic
budget counts are a handful per user; (2) introducing it now expands
this change into the gateway and transaction-service, breaking the
"frontend only" framing; (3) we can add it later as a pure performance
change without breaking this page (just swap the data source).

**Why not derive list totals from individually-fetched transaction
lists?** That would be N `listTransactions` calls returning O(rows)
data each, plus the float/decimal problem above. The summary endpoint
is built for exactly this and is O(1) bytes per budget.

**Implementation shape**: a custom inline effect in `BudgetsPage`:

```tsx
const [summaries, setSummaries] = useState<Record<number, BudgetSummary>>({});
const [summariesError, setSummariesError] = useState<string>();

useEffect(() => {
  if (!budgets.data) return;
  let cancelled = false;
  setSummariesError(undefined);
  Promise.all(
    budgets.data.map((b) =>
      api.getBudgetSummary(b.id).then((s) => [b.id, s] as const)
    ),
  )
    .then((entries) => {
      if (cancelled) return;
      setSummaries(Object.fromEntries(entries));
    })
    .catch((err) => {
      if (cancelled) return;
      setSummariesError(err instanceof ApiError ? err.message : "Unexpected error");
    });
  return () => { cancelled = true; };
}, [budgets.data]);
```

`Promise.all` is fine for this volume; if any one fails the whole batch
errors. That's acceptable for v1 — if it proves noisy in practice we can
switch to per-row independence.

### Decision 4 — List page: refresh follows the budget list

`useEffect` already depends on `budgets.data`. After a write,
`budgets.reload()` mutates `budgets.data`, which re-runs the effect and
refetches every summary. No extra wiring needed.

### Decision 5 — Layout

- **Detail page**: between the period text and the transactions section,
  a Mantine `Group` of three `Stack`s — each a small `Text c="dimmed"`
  label over a `Text fw={500}` value. While the summary is loading,
  render nothing for the block; the rest of the page renders
  progressively just like budget/categories/transactions do today.
- **List page**: three new `Table.Th` columns (Income, Expense, Net)
  inserted before the action buttons column. Each row's cell renders
  `summaries[budget.id]?.totals.income` etc., or an em-dash `—` while
  the summary is still loading.

### Decision 6 — Errors

- **Detail page**: add `summary.error` to the existing combined error
  `Alert`: `{budget.error ?? transactions.error ?? summary.error}`.
- **List page**: render an additional `Alert color="red"` when
  `summariesError` is set, alongside the existing `budgets.error`
  alert. Stale rows show `—` rather than old numbers.

### Decision 7 — MSW handler computes summary from the seed store

Add `http.get('${API}/budgets/:id/summary', ...)` to
`frontend/src/mocks/handlers.ts`. It looks up the budget (404 on miss)
and sums the in-memory `store.transactions` filtered by `budget_id`,
grouped by type. Decimals are formatted by reducing to a number then
`.toFixed(2)` — acceptable for tests where amounts have at most two
decimal places by construction (the seed helper enforces it).

## Risks / Trade-offs

- **N requests on every Budgets page render.** With N small budgets this
  is fine. → Mitigation: revisit and add a batched endpoint when N grows
  or when profiling shows the cost.

- **Double refetches on a detail-page write.** `handleSubmit` now
  triggers both `transactions.reload()` and `summary.reload()`.
  Acceptable: both are small reads on the same host. → Mitigation:
  revisit if a profile shows it.

- **One slow/failed summary breaks the whole list batch.**
  `Promise.all` fails fast. For v1 we'd rather see the error than half
  a table; the existing `summariesError` alert tells the user what
  happened. → Mitigation: if this becomes noisy, switch to
  `Promise.allSettled` and render per-row.

- **A summary fetch failure shouldn't break the visible data.** On the
  detail page, the transactions table still renders even if the summary
  fails. On the list page, the budget rows still render with `—` in
  the totals columns. → Mitigation: gate the totals UI on
  `summary.data` / `summaries[id]`, not on the budgets/transactions
  resources.

- **Test mock divergence.** The MSW summary uses `Number.toFixed(2)`
  while the backend uses `Decimal`. For test values constructed from
  fixed-precision strings this produces the same JSON. → Mitigation:
  keep the seed helper's amounts to two decimal places (already the
  case) and add a test exercising a non-trivial sum.

## Migration Plan

Pure frontend change: no schema migrations, no API additions. Deploys
with the next frontend build. Rollback = redeploy previous frontend.

## Open Questions

- Should the detail page's totals block be sticky as the user scrolls
  long transaction lists? **Decision:** no — defer until lists actually
  grow that long.
- Should we show the period's "days remaining" alongside the totals?
  **Decision:** out of scope; tracked as a possible follow-up.
- Add a batched `/budgets/summaries` endpoint? **Decision:** not now;
  add it as a pure-performance follow-up once budget counts justify it.
