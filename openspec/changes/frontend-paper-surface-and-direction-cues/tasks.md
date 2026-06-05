## 1. App shell content surface

- [ ] 1.1 Wrap the routed content in `AppLayout` (`AppShell.Main` / `Outlet`) in a Mantine `Paper` with rounded corners and a light elevation
- [ ] 1.2 Set the application background a step darker than the Mantine body color so the Paper reads as a raised surface
- [ ] 1.3 Confirm the header and navbar still read as chrome against the darker background (borders intact)

## 2. Budget totals panel

- [ ] 2.1 On `BudgetDetailPage`, group the aggregate totals (planned income, actual income, planned expense, actual expense, net) into a single totals panel
- [ ] 2.2 Place that panel directly beneath the budget's name and period

## 3. Income vs expense cue (drop type/kind column)

- [ ] 3.1 Remove the `Type` column from the transactions table; render a per-row color cue plus a redundant non-color cue (up/down marker) for income vs expense
- [ ] 3.2 Remove the `Kind` column from the per-category summary table; render the same color + non-color cue per row
- [ ] 3.3 Verify the non-color cue distinguishes income from expense in grayscale / for colorblind users (color is never the sole channel)

## 4. Tests

- [ ] 4.1 Update `BudgetDetailPage` tests: assert no Type/Kind column and that each row exposes the income/expense direction via the non-color cue (e.g. an accessible label or marker)
- [ ] 4.2 Adjust any tests that asserted the old totals layout to the grouped panel
- [ ] 4.3 Run the frontend test suite and fix fallout

## 5. Verify against design

- [ ] 5.1 Compare the running budget detail view and app shell against `design/budget_details/budget_details.svg` and `design/app_shell/app_shell.svg`

## 6. Backfilled detail-view specs (existing behavior)

- [ ] 6.1 Confirm the planned-allocations panel (list, add with kind-gated category picker, edit amount, delete, apply template) matches the new requirements; close any gap and ensure `AllocationPanel` tests cover them
- [ ] 6.2 Confirm the per-category "planned vs actual by category" breakdown matches the new requirement (planned/actual per category, `0.00` fallbacks, hidden when empty) and is covered by `BudgetDetailPage` tests
