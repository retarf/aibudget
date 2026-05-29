# allocation-api Specification

## Purpose

REST endpoints for Planned Allocation CRUD on a budget. An allocation records
the intended amount for a given category within one budget; allocations are
created either ad-hoc or by applying a template.

## Requirements

### Requirement: Planned allocation CRUD on a budget

The system SHALL expose REST endpoints to create, list, update, and delete
Planned Allocations for a specific budget. An allocation records the intended
amount for a given category within that budget. Each category MAY have at most
one allocation per budget.

#### Scenario: Create an allocation

- **WHEN** a client sends `POST /budgets/{budget_id}/allocations` with
  `category_id` and `planned_amount`
- **THEN** the system responds with `201` and the new allocation (`id`,
  `budget_id`, `category_id`, `planned_amount`)

#### Scenario: Duplicate allocation for the same category

- **WHEN** a client creates an allocation for a category that already has
  one on the same budget
- **THEN** the system responds with `409`

#### Scenario: Allocation for an unknown budget

- **WHEN** a client creates an allocation for a `budget_id` that does not
  exist
- **THEN** the system responds with `404`

#### Scenario: List allocations for a budget

- **WHEN** a client sends `GET /budgets/{budget_id}/allocations`
- **THEN** the system responds with `200` and a list of all allocations for
  that budget (`id`, `category_id`, `planned_amount`)

#### Scenario: List allocations for a budget with none

- **WHEN** a client requests allocations for a budget that has no allocations
- **THEN** the system responds with `200` and an empty list

#### Scenario: Update a planned amount

- **WHEN** a client sends
  `PUT /budgets/{budget_id}/allocations/{allocation_id}` with a new
  `planned_amount`
- **THEN** the system responds with `200` and the updated allocation

#### Scenario: Delete an allocation

- **WHEN** a client sends
  `DELETE /budgets/{budget_id}/allocations/{allocation_id}`
- **THEN** the system responds with `204` and the allocation is removed

#### Scenario: Unknown allocation

- **WHEN** a client updates or deletes an `allocation_id` that does not exist
  on the given budget
- **THEN** the system responds with `404`

### Requirement: Planned amounts use the same decimal representation as transactions

All `planned_amount` values in allocation requests and responses SHALL be
decimal strings with two decimal places, matching `TransactionRead.amount`.

#### Scenario: Planned amount is a decimal string

- **WHEN** a client receives an allocation
- **THEN** `planned_amount` is a JSON string with exactly two decimal places
  (e.g. `"500.00"`, not `500` and not `5e2`)
