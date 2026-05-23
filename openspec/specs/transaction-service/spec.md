# transaction-service Specification

## Purpose
TBD - created by archiving change split-application-to-microservices. Update Purpose after archive.
## Requirements
### Requirement: Transaction service owns the transaction domain

The system SHALL provide a transaction-service that runs as an independent
process, owns its own PostgreSQL database containing the `transactions` table,
and exposes the transaction create, list, get, update, and delete operations
over NATS request/reply subjects. The `transactions` table SHALL store
`budget_id` and `category_id` as plain values without cross-database foreign
key constraints.

#### Scenario: Transaction operations are served over NATS

- **WHEN** a `transaction.*` request is published for a create, list, get,
  update, or delete operation
- **THEN** transaction-service performs it against its own database and replies
  with the standard envelope

### Requirement: Transaction service maintains a budget/category projection

Transaction-service SHALL subscribe to `budget.*` and `category.*` domain
events and maintain a local read-model projection of budgets and categories in
its own database. The projection SHALL be updated idempotently as events
arrive. This projection is **eventually consistent** with the owning services.

#### Scenario: Budget event updates the projection

- **WHEN** transaction-service receives a `budget.created` or `budget.updated`
  event
- **THEN** it records or updates that budget in its local projection

#### Scenario: Category event updates the projection

- **WHEN** transaction-service receives a `category.created`, `category.updated`,
  or `category.deleted` event
- **THEN** it applies the change to the category records in its local projection

### Requirement: Transaction service validates against the projection

When creating or updating a transaction, transaction-service SHALL validate the
referenced budget and category against its local projection rather than by
calling another service. Validation SHALL occur before the local commit, so a
failed validation writes nothing.

#### Scenario: Referenced budget not in the projection

- **WHEN** a transaction create/update references a budget id absent from the
  projection
- **THEN** transaction-service replies with an error envelope of status `404`
  and does not write the transaction

#### Scenario: Referenced category not in the projection

- **WHEN** a transaction create/update references a category id absent from the
  projection
- **THEN** transaction-service replies with an error envelope of status `422`
  and does not write the transaction

#### Scenario: Date outside the budget period

- **WHEN** a transaction's date falls outside the period of the budget recorded
  in the projection
- **THEN** transaction-service replies with an error envelope of status `422`
  and does not write the transaction

#### Scenario: Valid references

- **WHEN** the referenced budget and category are both present in the
  projection and the date is within the budget period
- **THEN** transaction-service commits the transaction and replies with a
  success envelope

### Requirement: Transaction service cascades on budget or category deletion

When transaction-service receives a `budget.deleted` event it SHALL delete every
transaction belonging to that budget, and when it receives a `category.deleted`
event it SHALL delete every transaction classified by that category. This
restores — via events — the cascade behavior the monolith enforced with
`ON DELETE CASCADE` for budgets and with its in-use check for categories.

#### Scenario: Budget deleted

- **WHEN** transaction-service receives a `budget.deleted` event for a budget
  that has transactions
- **THEN** transaction-service deletes all transactions with that `budget_id`

#### Scenario: Category deleted

- **WHEN** transaction-service receives a `category.deleted` event for a
  category that classifies transactions
- **THEN** transaction-service deletes all transactions with that `category_id`
