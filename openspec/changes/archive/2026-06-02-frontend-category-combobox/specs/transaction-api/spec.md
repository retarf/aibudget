## MODIFIED Requirements

### Requirement: Record a transaction
The system SHALL allow recording a transaction within an existing budget,
specifying its type (income or expense), amount, date, and category. The
transaction date MUST fall within the budget's time period, the amount MUST be
greater than zero, and the referenced category's kind MUST match the
transaction's type.

#### Scenario: Transaction recorded
- **WHEN** a client posts a valid transaction to an existing budget
- **THEN** the system creates the transaction and responds with 201 and the created transaction

#### Scenario: Date outside the budget period
- **WHEN** a client posts a transaction whose date falls outside the budget's period
- **THEN** the system responds with 422 and does not create the transaction

#### Scenario: Non-positive amount rejected
- **WHEN** a client posts a transaction with an amount of zero or less
- **THEN** the system responds with 422 and does not create the transaction

#### Scenario: Category kind does not match the transaction type
- **WHEN** a client posts a transaction whose category's kind differs from the transaction's type
- **THEN** the system responds with 422 and does not create the transaction

#### Scenario: Transaction for a missing budget
- **WHEN** a client posts a transaction to a budget identifier that does not exist
- **THEN** the system responds with 404

### Requirement: Update a transaction
The system SHALL allow updating a transaction's type, amount, date, and
category, applying the same validation as recording — including that the
referenced category's kind matches the transaction's type.

#### Scenario: Transaction updated
- **WHEN** a client sends a valid update for an existing transaction
- **THEN** the system responds with 200 and the updated transaction

#### Scenario: Update with a mismatched category kind rejected
- **WHEN** a client updates a transaction so its category's kind no longer matches the transaction's type
- **THEN** the system responds with 422 and does not change the transaction

#### Scenario: Update of a missing transaction
- **WHEN** a client updates a transaction identifier that does not exist
- **THEN** the system responds with 404
