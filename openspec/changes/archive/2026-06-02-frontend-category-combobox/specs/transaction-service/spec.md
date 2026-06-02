## MODIFIED Requirements

### Requirement: Transaction service validates against the projection

When creating or updating a transaction, transaction-service SHALL validate the
referenced budget and category against its local projection rather than by
calling another service. Validation SHALL include that the referenced
category's `kind` matches the transaction's `type`. Validation SHALL occur
before the local commit, so a failed validation writes nothing.

#### Scenario: Referenced budget not in the projection

- **WHEN** a transaction create/update references a budget id absent from the
  projection
- **THEN** transaction-service replies with an error envelope of status `404`
  and does not write the transaction

#### Scenario: Referenced category not in the projection

- **WHEN** a transaction create/update references a category id absent from the
  projection
- **THEN** transaction-service replies with an error envelope of status `422`
  and does not write the transaction

#### Scenario: Category kind does not match the transaction type

- **WHEN** a transaction create/update references an existing category whose
  `kind` differs from the transaction's `type` (e.g. an `expense` transaction
  referencing an `income` category)
- **THEN** transaction-service replies with an error envelope of status `422`
  and does not write the transaction

#### Scenario: Date outside the budget period

- **WHEN** a transaction's date falls outside the period of the budget recorded
  in the projection
- **THEN** transaction-service replies with an error envelope of status `422`
  and does not write the transaction

#### Scenario: Valid references

- **WHEN** the referenced budget and category are both present in the
  projection, the category's kind matches the transaction type, and the date is
  within the budget period
- **THEN** transaction-service commits the transaction and replies with a
  success envelope

## ADDED Requirements

### Requirement: transaction-service reports and purges category usage

Transaction-service SHALL handle `transaction.category.usage`, returning the
number of transactions that reference a given `category_id`, and
`transaction.category.purge`, deleting every transaction that references it. The
purge SHALL be idempotent.

#### Scenario: Category usage counted

- **WHEN** `transaction.category.usage` is requested for a `category_id`
- **THEN** transaction-service replies with the count of transactions referencing
  that category

#### Scenario: Transactions purged

- **WHEN** `transaction.category.purge` is requested for a `category_id`
- **THEN** transaction-service deletes every transaction referencing it and
  replies with a success envelope

#### Scenario: Purge with nothing to delete

- **WHEN** `transaction.category.purge` is requested for a `category_id` with no
  transactions
- **THEN** transaction-service replies with a success envelope and deletes nothing
