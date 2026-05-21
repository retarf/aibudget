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

