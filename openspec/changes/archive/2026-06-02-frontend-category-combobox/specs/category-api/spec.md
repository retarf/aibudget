## MODIFIED Requirements

### Requirement: Delete a category
The system SHALL allow deleting a category only when it is **not in use**. A
category is in use when any transaction, any planned allocation, or any template
line item references it. A delete request for an in-use category SHALL be
rejected with `409` and include the counts of referencing transactions,
allocations, and template line items; nothing is deleted.

#### Scenario: Unused category deleted
- **WHEN** a client deletes a category that no transaction, allocation, or template line item references
- **THEN** the system responds with 204 and the category is removed

#### Scenario: In-use category cannot be deleted
- **WHEN** a client deletes a category referenced by at least one transaction, planned allocation, or template line item
- **THEN** the system responds with 409 and impact counts, and the category and its references are unchanged

## ADDED Requirements

### Requirement: Category list reports usage
The categories collection SHALL report, for each category, whether it is in use
and the number of transactions, planned allocations, and template line items
referencing it, so a client can offer delete only for unused categories.

#### Scenario: Usage included in the listing
- **WHEN** a client requests the categories collection
- **THEN** each returned category carries an in-use indicator and its usage counts

### Requirement: Erase a category's history
The system SHALL provide an operation that erases a category's footprint:
deleting every transaction and every planned allocation that references it in
any budget, and every template line item that references it in any template. The
operation SHALL NOT delete the category, and SHALL leave the category not in
use. The operation SHALL be idempotent.

#### Scenario: History erased, category retained
- **WHEN** a client invokes erase-history for a category that is in use
- **THEN** all transactions, planned allocations, and template line items referencing it are deleted, the category itself remains, and a subsequent delete of the category succeeds

#### Scenario: Erase history with nothing to erase
- **WHEN** a client invokes erase-history for a category that is not in use
- **THEN** the system responds successfully and nothing is changed
