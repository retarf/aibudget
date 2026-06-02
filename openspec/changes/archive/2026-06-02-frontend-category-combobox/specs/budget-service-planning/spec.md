## ADDED Requirements

### Requirement: budget-service reports and purges category usage

Budget-service SHALL handle `budget.category.usage`, returning the number of
allocations and the number of template line items that reference a given
`category_id`, and `budget.category.purge`, deleting every allocation and every
template line item that references it. The purge SHALL be idempotent.

#### Scenario: Category usage counted

- **WHEN** `budget.category.usage` is requested for a `category_id`
- **THEN** budget-service replies with the count of allocations and the count of
  template line items referencing that category

#### Scenario: Category footprint purged

- **WHEN** `budget.category.purge` is requested for a `category_id`
- **THEN** budget-service deletes every allocation and every template line item
  referencing it and replies with a success envelope

#### Scenario: Purge with nothing to delete

- **WHEN** `budget.category.purge` is requested for a `category_id` with no
  allocations and no template line items
- **THEN** budget-service replies with a success envelope and deletes nothing
