# budget-service Specification

## Purpose
TBD - created by archiving change split-application-to-microservices. Update Purpose after archive.
## Requirements
### Requirement: Budget service owns the budget domain

The system SHALL provide a budget-service that runs as an independent process,
owns its own PostgreSQL database containing the `budgets` table, and exposes the
budget create, list, get, update, and delete operations over NATS request/reply
subjects. No other service SHALL read or write the budget database directly.

#### Scenario: Budget operations are served over NATS

- **WHEN** a `budget.*` request is published for a create, list, get, update,
  or delete operation
- **THEN** budget-service performs it against its own database and replies with
  the standard envelope

#### Scenario: Budget data is isolated

- **WHEN** any other service needs budget data
- **THEN** it obtains it via a `budget.*` NATS request, not by querying the
  budget database

### Requirement: Budget service preserves budget behavior

Budget-service SHALL preserve the budget domain rules and responses of the
monolith, including returning `404` for an unknown budget id.

#### Scenario: Unknown budget

- **WHEN** a `budget.get` request names an id that does not exist
- **THEN** budget-service replies with an error envelope of status `404`

### Requirement: Budget service publishes budget events

After every successful budget create, update, or delete, budget-service SHALL
publish the corresponding `budget.created`, `budget.updated`, or
`budget.deleted` domain event so other services can maintain projections.

#### Scenario: Budget created

- **WHEN** budget-service successfully creates a budget
- **THEN** it publishes a `budget.created` event carrying the new budget's state

#### Scenario: Budget deleted

- **WHEN** budget-service successfully deletes a budget
- **THEN** it publishes a `budget.deleted` event carrying at least the deleted
  budget's id
