## ADDED Requirements

### Requirement: Show a budget's income, expense and net totals
A budget's detail view SHALL display the budget's total income, total
expense, and net (income minus expense), each as a labeled value, laid out
above the transactions list. The totals SHALL be loaded from the budget's
summary endpoint.

#### Scenario: Totals are shown for a budget with transactions
- **WHEN** the user opens a budget's detail view and the budget has at least one transaction
- **THEN** the page shows the income, expense, and net totals returned by the summary API

#### Scenario: Totals are shown for a budget without transactions
- **WHEN** the user opens a budget's detail view and the budget has no transactions
- **THEN** the page shows `0.00` for income, expense, and net

#### Scenario: Totals refresh after a transaction is recorded
- **WHEN** the user records a transaction from the budget's detail view
- **THEN** the displayed totals update to reflect the new transaction without a page reload

#### Scenario: Totals refresh after a transaction is edited
- **WHEN** the user saves changes to a transaction from the budget's detail view
- **THEN** the displayed totals update to reflect the change without a page reload

#### Scenario: Totals refresh after a transaction is deleted
- **WHEN** the user deletes a transaction from the budget's detail view
- **THEN** the displayed totals update to reflect the deletion without a page reload

#### Scenario: Summary load error is surfaced
- **WHEN** the summary API returns an error while loading the totals
- **THEN** the page displays the error message and does not render stale totals
