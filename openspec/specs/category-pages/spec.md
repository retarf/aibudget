# category-pages Specification

## Purpose
TBD - created by archiving change frontend-budget-management. Update Purpose after archive.
## Requirements
### Requirement: View the category list
The Categories page SHALL display all categories returned by the REST API.

#### Scenario: Categories are listed
- **WHEN** the user opens the Categories page
- **THEN** every existing category is shown with its name and kind

### Requirement: Filter categories by kind
The Categories page SHALL let the user filter the list by kind (income or
expense).

#### Scenario: Filtering by kind
- **WHEN** the user selects a kind filter
- **THEN** only categories of that kind are shown

### Requirement: Create a category
The Categories page SHALL let the user create a category by entering a name
and selecting a kind.

#### Scenario: Category created
- **WHEN** the user submits the create form with a valid name and kind
- **THEN** the category is created via the API and appears in the list

#### Scenario: Duplicate category is reported
- **WHEN** the user submits a category whose name already exists for that kind
- **THEN** the API rejection is shown as a form error and no category is created

### Requirement: Delete a category
The Categories page SHALL let the user delete a category after confirmation.

#### Scenario: Category deleted
- **WHEN** the user confirms deletion of an unused category
- **THEN** the category is removed via the API and disappears from the list

#### Scenario: Category in use is reported
- **WHEN** the user confirms deletion of a category referenced by a transaction
- **THEN** the API rejection is shown to the user and the category remains

