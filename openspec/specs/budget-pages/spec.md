# budget-pages Specification

## Purpose
TBD - created by archiving change frontend-budget-management. Update Purpose after archive.
## Requirements
### Requirement: View the budget list
The Budgets page SHALL display all budgets returned by the REST API.

#### Scenario: Budgets are listed
- **WHEN** the user opens the Budgets page
- **THEN** every existing budget is shown with its name and time period

#### Scenario: No budgets yet
- **WHEN** the user opens the Budgets page and no budgets exist
- **THEN** an empty-state message is shown

### Requirement: Create a budget
The Budgets page SHALL let the user create a budget by entering a name, a
start date, and an end date.

#### Scenario: Budget created
- **WHEN** the user submits the create form with a valid name and period
- **THEN** the budget is created via the API and appears in the list

#### Scenario: Invalid period is reported
- **WHEN** the user submits a budget whose end date is not after its start date
- **THEN** the API rejection is shown as a form error and no budget is created

### Requirement: Edit a budget
The Budgets page SHALL let the user edit an existing budget's name and period.

#### Scenario: Budget updated
- **WHEN** the user saves changes to a budget
- **THEN** the budget is updated via the API and the list reflects the change

### Requirement: Delete a budget
The Budgets page SHALL let the user delete a budget after confirmation.

#### Scenario: Budget deleted
- **WHEN** the user confirms deletion of a budget
- **THEN** the budget is removed via the API and disappears from the list

### Requirement: Open a budget's detail
The Budgets page SHALL let the user open a budget to view its detail.

#### Scenario: Navigating to a budget
- **WHEN** the user selects a budget from the list
- **THEN** the budget's detail view is shown

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

