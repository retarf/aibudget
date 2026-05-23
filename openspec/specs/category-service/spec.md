# category-service Specification

## Purpose
TBD - created by archiving change split-application-to-microservices. Update Purpose after archive.
## Requirements
### Requirement: Category service owns the category domain

The system SHALL provide a category-service that runs as an independent
process, owns its own PostgreSQL database containing the `categories` table,
and exposes the category create, list, and delete operations over NATS
request/reply subjects (these are the operations the monolith's REST API
offered). No other service SHALL read or write the category database directly.

#### Scenario: Category operations are served over NATS

- **WHEN** a `category.*` request is published for a create, list, or delete
  operation
- **THEN** category-service performs it against its own database and replies
  with the standard envelope

#### Scenario: Category data is isolated

- **WHEN** any other service needs category data
- **THEN** it obtains it via a `category.*` NATS request, not by querying the
  category database

### Requirement: Category service preserves category behavior

Category-service SHALL preserve the category domain rules and responses of the
monolith, including rejecting a duplicate category and returning `404` for an
unknown category id. The monolith's in-use check on delete is NOT reproduced:
category-service SHALL delete the category unconditionally; cleanup of
transactions classified by it happens via the `category.deleted` cascade in
transaction-service.

#### Scenario: Unknown category

- **WHEN** a `category.delete` request names an id that does not exist
- **THEN** category-service replies with an error envelope of status `404`

#### Scenario: Category in use is still deleted

- **WHEN** a `category.delete` request names a category that classifies
  transactions
- **THEN** category-service deletes it and replies with a success envelope,
  rather than rejecting the request

### Requirement: Category service publishes category events

Category-service SHALL publish the corresponding `category.created` or
`category.deleted` domain event after every successful category create or
delete, so other services can maintain projections.

#### Scenario: Category created

- **WHEN** category-service successfully creates a category
- **THEN** it publishes a `category.created` event carrying the new category's
  state

#### Scenario: Category deleted

- **WHEN** category-service successfully deletes a category
- **THEN** it publishes a `category.deleted` event carrying at least the deleted
  category's id
