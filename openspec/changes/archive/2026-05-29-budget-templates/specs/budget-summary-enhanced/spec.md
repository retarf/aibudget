## MODIFIED Requirements

Replaces the requirements previously defined in `transaction-summary-api`.

### Requirement: Summary returns planned vs actual at aggregate and per-category level

`GET /budgets/{budget_id}/summary` SHALL return both aggregate planned/actual
totals and a per-category breakdown. The gateway SHALL aggregate two NATS calls
in parallel: `budget.allocation.list` (planned amounts from budget-service) and
`transaction.summary.categories` (actual amounts from transaction-service), then
merge the results.

#### Scenario: Summary with both allocations and transactions

- **WHEN** a client requests the summary for a budget that has both planned
  allocations and recorded transactions
- **THEN** the system responds with `200` and a body containing:
  - `budget_id`
  - `totals` with `planned_income`, `actual_income`, `planned_expense`,
    `actual_expense`, and `net` (`actual_income − actual_expense`)
  - `categories`: a list of entries, one per unique `category_id` appearing
    in either allocations or transactions, each with `category_id`, `kind`,
    `planned_amount`, and `actual_amount`

#### Scenario: Category with allocation but no transactions appears in summary

- **WHEN** a budget has a planned allocation for a category that has no
  recorded transactions
- **THEN** that category appears in `categories` with the correct
  `planned_amount` and `actual_amount` of `"0.00"`

#### Scenario: Category with transactions but no allocation appears in summary

- **WHEN** a budget has transactions for a category that has no planned
  allocation
- **THEN** that category appears in `categories` with `planned_amount` of
  `"0.00"` and the correct `actual_amount`

#### Scenario: Summary for a budget with no allocations and no transactions

- **WHEN** the summary is requested for a budget with no allocations and no
  transactions
- **THEN** the system responds with `200`, all aggregate totals are `"0.00"`,
  and `categories` is an empty list

#### Scenario: Summary for a missing budget

- **WHEN** a client requests the summary for a `budget_id` that does not exist
- **THEN** the system responds with `404`

### Requirement: transaction-service exposes per-category actual sums

Transaction-service SHALL handle the `transaction.summary.categories` NATS
subject. Given a `budget_id`, it SHALL return the actual income and expense
summed per `category_id` for that budget.

#### Scenario: Per-category actuals returned

- **WHEN** `transaction.summary.categories` is requested for a budget with
  transactions across multiple categories
- **THEN** transaction-service replies with one entry per `(category_id, kind)`
  combination containing the summed `amount`

#### Scenario: Empty result for budget with no transactions

- **WHEN** `transaction.summary.categories` is requested for an existing
  budget with no transactions
- **THEN** transaction-service replies with an empty list (not a 404)

#### Scenario: 404 for unknown budget

- **WHEN** `transaction.summary.categories` is requested for a `budget_id`
  not present in the budget projection
- **THEN** transaction-service replies with an error envelope of status `404`

### Requirement: Summary amounts use a consistent decimal representation

All monetary fields in the summary response (`planned_income`, `actual_income`,
`planned_expense`, `actual_expense`, `net`, `planned_amount`, `actual_amount`)
SHALL be decimal strings with exactly two decimal places.

#### Scenario: Amounts are decimal strings with two decimal places

- **WHEN** a client receives any monetary field in the summary response
- **THEN** the value is a JSON string formatted with exactly two decimal places
  (e.g. `"120.50"`, not `120.5` and not a JSON number)
