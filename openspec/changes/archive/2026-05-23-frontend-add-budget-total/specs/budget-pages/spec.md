## ADDED Requirements

### Requirement: Show per-budget income, expense and net totals on the list
The Budgets page SHALL display, for each budget row, the budget's total
income, total expense, and net (income minus expense), each in its own
column. The totals SHALL be loaded from the budget's summary endpoint,
one request per budget, fired in parallel after the budgets list loads.

#### Scenario: Totals columns are shown for budgets with transactions
- **WHEN** the user opens the Budgets page and at least one budget has transactions
- **THEN** each budget row shows its income, expense, and net values as returned by the summary API

#### Scenario: Totals columns are shown for budgets without transactions
- **WHEN** the user opens the Budgets page and a budget has no transactions
- **THEN** that budget's row shows `0.00` for income, expense, and net

#### Scenario: Totals refresh after a budget is created
- **WHEN** the user creates a budget from the Budgets page
- **THEN** the new budget appears in the list with its totals (`0.00` each, since it has no transactions yet)

#### Scenario: Totals refresh after a budget is edited
- **WHEN** the user saves changes to a budget from the Budgets page
- **THEN** the updated row's totals reflect the budget's current transactions

#### Scenario: Totals refresh after a budget is deleted
- **WHEN** the user deletes a budget from the Budgets page
- **THEN** the row disappears and the remaining rows continue to show correct totals

#### Scenario: A row's summary error is surfaced
- **WHEN** the summary API returns an error while loading totals for one or more rows
- **THEN** the page displays the error and the affected rows do not render stale totals
