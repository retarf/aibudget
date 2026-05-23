# transaction-pages Specification

## Purpose
TBD - created by archiving change frontend-budget-management. Update Purpose after archive.
## Requirements
### Requirement: View a budget's transactions
A budget's detail view SHALL display all transactions belonging to that budget.

#### Scenario: Transactions are listed
- **WHEN** the user opens a budget's detail view
- **THEN** the budget's transactions are shown with their type, amount, date, and category

#### Scenario: No transactions yet
- **WHEN** the user opens a budget that has no transactions
- **THEN** an empty-state message is shown

### Requirement: Record a transaction
A budget's detail view SHALL let the user record a transaction by entering a
type, an amount, a date, and a category.

#### Scenario: Transaction recorded
- **WHEN** the user submits the record form with valid values
- **THEN** the transaction is created via the API and appears in the list

#### Scenario: Invalid transaction is reported
- **WHEN** the user submits a transaction the API rejects (e.g. a date outside the budget period)
- **THEN** the API rejection is shown as a form error and no transaction is created

### Requirement: Edit a transaction
A budget's detail view SHALL let the user edit an existing transaction.

#### Scenario: Transaction updated
- **WHEN** the user saves changes to a transaction
- **THEN** the transaction is updated via the API and the list reflects the change

### Requirement: Delete a transaction
A budget's detail view SHALL let the user delete a transaction after
confirmation.

#### Scenario: Transaction deleted
- **WHEN** the user confirms deletion of a transaction
- **THEN** the transaction is removed via the API and disappears from the list

### Requirement: Create a category from the transaction form
The transaction form SHALL let the user create a new category without leaving
the form, when the category they need does not yet exist.

#### Scenario: Creating a category inline
- **WHEN** the user opens the add-category control in the transaction form and submits a valid name and kind
- **THEN** the category is created via the API, the category list refreshes, and the new category becomes the form's selected category

#### Scenario: The transaction form keeps its other values
- **WHEN** the user creates a category inline while other transaction fields are filled in
- **THEN** the type, amount, and date already entered remain unchanged

#### Scenario: Duplicate category is reported
- **WHEN** the user adds a category whose name already exists for that kind
- **THEN** the API rejection is shown inline and no category is created

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

