## Why

Design exploration in the `design/` SVG mockups settled three presentation
decisions for the app shell and the budget detail view that the current specs
either contradict or leave unstated. Recording them keeps the specs aligned
with the intended UI before it is built, and captures one accessibility
guarantee (income/expense must not be conveyed by color alone).

## What Changes

- The routed page content renders on an **elevated, visually distinct surface**
  (a Mantine `Paper`) with rounded corners, sitting on a **darker application
  background**. The content area is no longer flush with the app background.
- On the budget detail view, the budget's aggregate totals (planned income,
  actual income, planned expense, actual expense, net) are **grouped into a
  single totals panel placed directly beneath the budget's name and period**,
  rather than as a loose row of labeled values above the transactions list.
- The budget detail view no longer shows a dedicated **Type/Kind text column**
  in its transactions list or its per-category summary. Each row instead
  indicates income vs expense with a **color cue AND a redundant non-color cue**
  (an up/down direction marker), so the distinction survives for colorblind
  users and in grayscale.

- The budget detail view's **planned-allocations panel** and **per-category
  summary breakdown** — both already present in the UI but never written down —
  are captured as requirements: listing, adding (kind-gated category picker),
  editing, and deleting allocations; applying a template (merge semantics); and
  the planned-vs-actual-by-category breakdown. This backfills existing behavior
  so the detail view is fully specified rather than partially.

No backend, API, or data-model changes. No breaking changes — this is frontend
presentation only (the allocation/summary requirements document existing
behavior).

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `app-shell`: adds a requirement that the shell's content area is rendered as
  an elevated, visually distinct surface (separate from a darker app
  background) with rounded corners.
- `transaction-pages`: the budget detail view lists transactions without a
  separate type column; income vs expense is shown by a color cue plus a
  redundant non-color cue across both the transactions list and the
  per-category summary; and the aggregate totals (planned/actual income,
  planned/actual expense, net) are grouped into one panel placed beneath the
  budget's name and period. Additionally, the previously-unspecified
  planned-allocations panel and per-category summary breakdown of the detail
  view are documented (list/add/edit/delete allocations, apply a template, and
  the planned-vs-actual-by-category breakdown).

## Impact

- Frontend only: `AppLayout` / `AppShell` (content surface + app background),
  `BudgetDetailPage` (totals grouping; transactions and per-category summary
  tables drop the type/kind column and gain the dual income/expense cue).
- Reference mockups live under `design/` (`app_shell.svg`,
  `budget_details/budget_details.svg`).
- Exact colors, border widths, and shadow values are implementation detail and
  are intentionally left out of the specs.
