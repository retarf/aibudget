# budget-api Specification

## Purpose
TBD - created by archiving change backend-rest-api. Update Purpose after archive.
## Requirements
### Requirement: Create a budget
The system SHALL allow a client to create a budget by providing a name and a
time period (start date and end date). The system SHALL reject a budget whose
end date is not strictly after its start date.

#### Scenario: Budget created successfully
- **WHEN** a client sends a request with a valid name, start date, and end date
- **THEN** the system creates the budget and responds with 201 and the created budget including its identifier

#### Scenario: Invalid period rejected
- **WHEN** a client sends a request whose end date is on or before its start date
- **THEN** the system responds with 422 and does not create the budget

### Requirement: List budgets
The system SHALL return all existing budgets.

#### Scenario: Budgets listed
- **WHEN** a client requests the budgets collection
- **THEN** the system responds with 200 and an array of all budgets

### Requirement: Retrieve a budget
The system SHALL return a single budget identified by its identifier.

#### Scenario: Budget found
- **WHEN** a client requests a budget by an existing identifier
- **THEN** the system responds with 200 and that budget

#### Scenario: Budget not found
- **WHEN** a client requests a budget by an identifier that does not exist
- **THEN** the system responds with 404

### Requirement: Update a budget
The system SHALL allow updating a budget's name and time period, applying the
same period validation as creation.

#### Scenario: Budget updated
- **WHEN** a client sends a valid update for an existing budget
- **THEN** the system responds with 200 and the updated budget

#### Scenario: Update of a missing budget
- **WHEN** a client updates a budget identifier that does not exist
- **THEN** the system responds with 404

### Requirement: Delete a budget
The system SHALL allow deleting a budget. Deleting a budget SHALL also remove
all transactions belonging to it.

#### Scenario: Budget deleted
- **WHEN** a client deletes an existing budget
- **THEN** the system responds with 204 and the budget and its transactions are removed

#### Scenario: Delete of a missing budget
- **WHEN** a client deletes a budget identifier that does not exist
- **THEN** the system responds with 404

