# template-api Specification

## Purpose

REST endpoints for Budget Template CRUD and the apply-template action.
Templates are named, reusable blueprints of `(category, planned_amount)`
line items, managed independently of any concrete budget.

## Requirements

### Requirement: Template CRUD

The system SHALL expose REST endpoints to create, list, retrieve, update, and
delete Budget Templates. A template has a name and zero or more line items.
Deleting a template deletes its line items.

#### Scenario: Create a template

- **WHEN** a client sends `POST /templates` with a `name`
- **THEN** the system responds with `201` and the created template (`id`, `name`)

#### Scenario: List templates

- **WHEN** a client sends `GET /templates`
- **THEN** the system responds with `200` and a list of all templates
  (each with `id` and `name`, without line items)

#### Scenario: Get a template with its line items

- **WHEN** a client sends `GET /templates/{template_id}`
- **THEN** the system responds with `200` and the template including its full
  list of line items (`id`, `category_id`, `planned_amount`)

#### Scenario: Unknown template

- **WHEN** a client requests a template id that does not exist
- **THEN** the system responds with `404`

#### Scenario: Update template name

- **WHEN** a client sends `PUT /templates/{template_id}` with a new `name`
- **THEN** the system responds with `200` and the updated template

#### Scenario: Delete a template

- **WHEN** a client sends `DELETE /templates/{template_id}`
- **THEN** the system responds with `204` and all line items of that template
  are removed

### Requirement: Template line item management

The system SHALL allow adding and removing individual line items from a
template. Each category MAY appear at most once per template.

#### Scenario: Add a line item

- **WHEN** a client sends `POST /templates/{template_id}/items` with
  `category_id` and `planned_amount`
- **THEN** the system responds with `201` and the new item (`id`,
  `category_id`, `planned_amount`)

#### Scenario: Duplicate category in template

- **WHEN** a client adds a line item for a category that already has a line
  item in the same template
- **THEN** the system responds with `409`

#### Scenario: Remove a line item

- **WHEN** a client sends
  `DELETE /templates/{template_id}/items/{item_id}`
- **THEN** the system responds with `204` and that item is removed from
  the template

### Requirement: Apply a template to a budget

The system SHALL copy a template's line items into a budget as planned
allocations. Applying uses merge semantics: if the budget already has an
allocation for a category that also appears in the template, the existing
allocation is kept and the template's value for that category is skipped.

#### Scenario: Apply a template to a budget with no existing allocations

- **WHEN** a client sends `POST /budgets/{budget_id}/apply-template` with a
  `template_id`
- **THEN** the system responds with `200`, and the budget gains a planned
  allocation for every line item in the template

#### Scenario: Apply a template when the budget already has overlapping allocations

- **WHEN** a client applies a template and the budget already has a planned
  allocation for one or more of the template's categories
- **THEN** the existing allocations for those categories are kept unchanged
  and the template's values for them are skipped; allocations for categories
  not yet in the budget are inserted

#### Scenario: Apply an unknown template

- **WHEN** a client sends `POST /budgets/{budget_id}/apply-template` with a
  `template_id` that does not exist
- **THEN** the system responds with `404`

#### Scenario: Apply to an unknown budget

- **WHEN** a client sends `POST /budgets/{budget_id}/apply-template` for a
  budget id that does not exist
- **THEN** the system responds with `404`

### Requirement: Category deletion cascades through template line items

When a category is deleted, all template line items referencing that category
SHALL be removed automatically. No template is deleted as a result; only the
affected items are removed.

#### Scenario: Category deleted while referenced by template items

- **WHEN** a category is deleted
- **THEN** all template line items with that `category_id` are removed
- **AND** templates that had no other line items for that category are
  otherwise unaffected
