# transaction-api Specification

## Purpose
TBD - created by archiving change backend-rest-api. Update Purpose after archive.
## Requirements
### Requirement: Record a transaction
The system SHALL allow recording a transaction within an existing budget,
specifying its type (income or expense), amount, date, and category. The
transaction date MUST fall within the budget's time period and the amount MUST
be greater than zero.

#### Scenario: Transaction recorded
- **WHEN** a client posts a valid transaction to an existing budget
- **THEN** the system creates the transaction and responds with 201 and the created transaction

#### Scenario: Date outside the budget period
- **WHEN** a client posts a transaction whose date falls outside the budget's period
- **THEN** the system responds with 422 and does not create the transaction

#### Scenario: Non-positive amount rejected
- **WHEN** a client posts a transaction with an amount of zero or less
- **THEN** the system responds with 422 and does not create the transaction

#### Scenario: Transaction for a missing budget
- **WHEN** a client posts a transaction to a budget identifier that does not exist
- **THEN** the system responds with 404

### Requirement: List transactions of a budget
The system SHALL return all transactions belonging to a given budget.

#### Scenario: Transactions listed
- **WHEN** a client requests the transactions of an existing budget
- **THEN** the system responds with 200 and an array of that budget's transactions

### Requirement: Retrieve a transaction
The system SHALL return a single transaction identified by its identifier.

#### Scenario: Transaction found
- **WHEN** a client requests a transaction by an existing identifier
- **THEN** the system responds with 200 and that transaction

#### Scenario: Transaction not found
- **WHEN** a client requests a transaction by an identifier that does not exist
- **THEN** the system responds with 404

### Requirement: Update a transaction
The system SHALL allow updating a transaction's type, amount, date, and
category, applying the same validation as recording.

#### Scenario: Transaction updated
- **WHEN** a client sends a valid update for an existing transaction
- **THEN** the system responds with 200 and the updated transaction

#### Scenario: Update of a missing transaction
- **WHEN** a client updates a transaction identifier that does not exist
- **THEN** the system responds with 404

### Requirement: Delete a transaction
The system SHALL allow deleting a transaction.

#### Scenario: Transaction deleted
- **WHEN** a client deletes an existing transaction
- **THEN** the system responds with 204 and the transaction is removed

#### Scenario: Delete of a missing transaction
- **WHEN** a client deletes a transaction identifier that does not exist
- **THEN** the system responds with 404

