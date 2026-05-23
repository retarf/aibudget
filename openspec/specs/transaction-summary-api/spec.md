# transaction-summary-api Specification

## Purpose
TBD - created by archiving change summarize-incomes-and-outomes. Update Purpose after archive.
## Requirements
### Requirement: Summarize a budget's incomes and expenses
The system SHALL return an aggregated summary of a budget's transactions
containing the total income, the total expense, and the net (income minus
expense) across the entire budget. The summary MUST be derived from the
transaction-service's own transaction data and MUST NOT require live calls
to other services.

#### Scenario: Summary returned for a budget with transactions
- **WHEN** a client requests `GET /budgets/{budget_id}/summary` for an existing budget that has at least one transaction
- **THEN** the system responds with 200 and a body containing `budget_id`, `totals.income`, `totals.expense`, and `totals.net`

#### Scenario: Net equals income minus expense
- **WHEN** a client receives a summary
- **THEN** `totals.net` equals `totals.income` minus `totals.expense`

#### Scenario: Summary returned for a budget with no transactions
- **WHEN** a client requests the summary for an existing budget that has no transactions
- **THEN** the system responds with 200 and `totals.income`, `totals.expense`, and `totals.net` are all `"0.00"`

#### Scenario: Summary for a missing budget
- **WHEN** a client requests the summary for a budget identifier that does not exist
- **THEN** the system responds with 404 and does not return a summary body

### Requirement: Summary amounts use a consistent decimal representation
The system SHALL serialize every monetary value in the summary response as
a decimal string with two decimal places, matching the representation
already used by the transaction REST API.

#### Scenario: Amounts are decimal strings with two decimal places
- **WHEN** a client receives any monetary field in the summary response (`totals.income`, `totals.expense`, or `totals.net`)
- **THEN** the value is a JSON string formatted with exactly two decimal places (for example, `"12.50"`, not `12.5` and not a JSON number)
