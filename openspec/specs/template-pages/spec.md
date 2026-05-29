# template-pages Specification

## Purpose

The Templates frontend page lets users create, browse, and manage budget
templates and their line items. Templates are managed independently of any
concrete budget and the page is reachable from the main navigation.

## Requirements

### Requirement: Templates page is reachable from the main navigation

The application SHALL expose a top-level **Templates** section in the main
navigation that opens the Templates page at `/templates`.

#### Scenario: Navigating to Templates

- **WHEN** the user clicks the **Templates** entry in the navigation
- **THEN** the Templates page is shown

### Requirement: View the template list

The Templates page SHALL display all templates returned by the REST API.

#### Scenario: Templates are listed

- **WHEN** the user opens the Templates page
- **THEN** every existing template is shown with its name

#### Scenario: No templates yet

- **WHEN** the user opens the Templates page and no templates exist
- **THEN** an empty-state message is shown

### Requirement: Create a template

The Templates page SHALL let the user create a template by entering a name.

#### Scenario: Template created

- **WHEN** the user submits the create form with a valid name
- **THEN** the template is created via the API and appears in the list

#### Scenario: Empty name is reported

- **WHEN** the user submits the form with an empty name
- **THEN** the form refuses to submit and no template is created

### Requirement: Open a template's detail

The Templates page SHALL let the user open a template to view and manage its
line items.

#### Scenario: Navigating to a template detail

- **WHEN** the user selects a template from the list
- **THEN** the template detail view is shown with its name and its line items

### Requirement: Add a line item to a template

The template detail view SHALL let the user add a line item by picking an
income or expense category and entering a planned amount.

#### Scenario: Line item added

- **WHEN** the user submits the add-item form with a valid category and amount
- **THEN** the item is created via the API and appears in the list

#### Scenario: Duplicate category is reported

- **WHEN** the user adds a line item for a category that already has an item
  in the same template
- **THEN** the API rejection is shown to the user and no item is created

### Requirement: Remove a line item from a template

The template detail view SHALL let the user remove individual line items.

#### Scenario: Line item removed

- **WHEN** the user clicks the delete control on a line item
- **THEN** the item is removed via the API and disappears from the list

### Requirement: Delete a template

The Templates page SHALL let the user delete a template after confirmation.

#### Scenario: Template deleted

- **WHEN** the user confirms deletion of a template
- **THEN** the template is removed via the API and disappears from the list,
  and all of its line items are deleted server-side
