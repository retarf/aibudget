# category-api Specification

## Purpose
TBD - created by archiving change backend-rest-api. Update Purpose after archive.
## Requirements
### Requirement: Create a category
The system SHALL allow creating a category with a name and a kind (income or
expense). A category name MUST be unique within its kind.

#### Scenario: Category created
- **WHEN** a client posts a category with a name and a valid kind
- **THEN** the system creates the category and responds with 201 and the created category

#### Scenario: Duplicate name within a kind rejected
- **WHEN** a client posts a category whose name already exists for the same kind
- **THEN** the system responds with 409 and does not create the category

#### Scenario: Invalid kind rejected
- **WHEN** a client posts a category whose kind is neither income nor expense
- **THEN** the system responds with 422 and does not create the category

### Requirement: List categories
The system SHALL return all existing categories and SHALL allow filtering them
by kind.

#### Scenario: All categories listed
- **WHEN** a client requests the categories collection without a filter
- **THEN** the system responds with 200 and an array of all categories

#### Scenario: Categories filtered by kind
- **WHEN** a client requests the categories collection filtered by a kind
- **THEN** the system responds with 200 and only the categories of that kind

### Requirement: Delete a category
The system SHALL allow deleting a category only when no transaction references
it.

#### Scenario: Unused category deleted
- **WHEN** a client deletes a category that no transaction references
- **THEN** the system responds with 204 and the category is removed

#### Scenario: Category in use cannot be deleted
- **WHEN** a client deletes a category referenced by at least one transaction
- **THEN** the system responds with 409 and does not delete the category

