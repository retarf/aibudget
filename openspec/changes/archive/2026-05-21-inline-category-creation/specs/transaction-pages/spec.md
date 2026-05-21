## ADDED Requirements

### Requirement: Create a category from the transaction form
The transaction form SHALL let the user create a new category without leaving
the form, when the category they need does not yet exist.

#### Scenario: Creating a category inline
- **WHEN** the user opens the add-category control in the transaction form and submits a valid name and kind
- **THEN** the category is created via the API, the category list refreshes, and the new category becomes the form's selected category

#### Scenario: The transaction form keeps its other values
- **WHEN** the user creates a category inline while other transaction fields are filled in
- **THEN** the type, amount, and date already entered remain unchanged

#### Scenario: Duplicate category is reported
- **WHEN** the user adds a category whose name already exists for that kind
- **THEN** the API rejection is shown inline and no category is created
