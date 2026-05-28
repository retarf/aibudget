## ADDED Requirements

### Requirement: budget-service owns templates and allocations

Budget-service SHALL own the `templates`, `template_items`, and `allocations`
tables in its PostgreSQL database and expose all template and allocation
operations over NATS request/reply subjects. No other service SHALL read or
write these tables directly.

#### Scenario: Template and allocation operations are served over NATS

- **WHEN** a `budget.template.*` or `budget.allocation.*` request is published
- **THEN** budget-service performs it against its own database and replies with
  the standard envelope

### Requirement: Template operations

Budget-service SHALL handle the following NATS subjects for template management:
`budget.template.create`, `budget.template.list`, `budget.template.get`,
`budget.template.update`, `budget.template.delete`,
`budget.template.item.add`, `budget.template.item.delete`, and
`budget.template.apply`.

#### Scenario: Duplicate category in template item add

- **WHEN** `budget.template.item.add` is requested for a category that already
  has a line item in the same template
- **THEN** budget-service replies with an error envelope of status `409`

#### Scenario: Apply template — merge semantics

- **WHEN** `budget.template.apply` is requested with a `budget_id` and
  `template_id`
- **THEN** for each template line item: if the budget already has an allocation
  for that `category_id`, it is left unchanged; otherwise a new allocation is
  inserted
- **AND** budget-service replies with the list of allocations created (not
  skipped)

### Requirement: Allocation operations

Budget-service SHALL handle `budget.allocation.create`,
`budget.allocation.list`, `budget.allocation.update`, and
`budget.allocation.delete`.

#### Scenario: Duplicate allocation rejected

- **WHEN** `budget.allocation.create` is requested for a `(budget_id,
  category_id)` pair that already has an allocation
- **THEN** budget-service replies with an error envelope of status `409`

#### Scenario: Allocations cascade when budget is deleted

- **WHEN** a budget is deleted
- **THEN** all allocations for that budget are deleted (handled within
  budget-service's own database; no external event required)

### Requirement: budget-service subscribes to category.deleted

Budget-service SHALL subscribe to `category.deleted` domain events published by
category-service. On receipt, it SHALL delete every `template_items` row where
`category_id` matches the deleted category's id.

#### Scenario: Template items removed on category deletion

- **WHEN** a `category.deleted` event arrives
- **THEN** all template line items referencing that `category_id` are deleted
- **AND** templates that had items for other categories are otherwise unaffected

#### Scenario: category.deleted with no matching template items

- **WHEN** a `category.deleted` event arrives and no template item references
  that category
- **THEN** budget-service handles the event without error (no-op)
