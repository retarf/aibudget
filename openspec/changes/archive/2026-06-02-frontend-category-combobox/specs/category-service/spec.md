## MODIFIED Requirements

### Requirement: Category service preserves category behavior

Category-service SHALL preserve the category domain rules and responses of the
monolith, including rejecting a duplicate category and returning `404` for an
unknown category id. The monolith's in-use check on delete is NOT reproduced in
category-service: it SHALL delete the category unconditionally. The system-level
guard that prevents deleting an **in-use** category is enforced upstream at the
API gateway (see `category-api`), which checks usage across transaction-service
and budget-service and only calls `category.delete` once the category is unused;
category-service stays unconditional so the gateway can purge-then-delete and so
the `category.deleted` cascade still acts as a safety net.

#### Scenario: Unknown category

- **WHEN** a `category.delete` request names an id that does not exist
- **THEN** category-service replies with an error envelope of status `404`

#### Scenario: Category in use is still deleted at the service level

- **WHEN** a `category.delete` request reaches category-service for a category
  that classifies transactions
- **THEN** category-service deletes it and replies with a success envelope,
  rather than rejecting the request (the in-use guard lives at the gateway)
