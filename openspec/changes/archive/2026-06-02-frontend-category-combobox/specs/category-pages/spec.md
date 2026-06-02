## MODIFIED Requirements

### Requirement: Delete a category
The Categories page SHALL offer the **Delete** action only for a category that
is **not in use**. For a category that is in use (any transaction, planned
allocation, or template line item references it), the page SHALL instead offer
the **Erase history** action and SHALL NOT offer Delete. Usage is read from the
category list's usage information.

#### Scenario: Delete offered for an unused category
- **WHEN** the user views a category that nothing references
- **THEN** the row offers **Delete** (and not Erase history); confirming it removes the category via the API and it disappears from the list

#### Scenario: Erase history offered for an in-use category
- **WHEN** the user views a category referenced by a transaction, allocation, or template line item
- **THEN** the row offers **Erase history** (and not Delete)

## ADDED Requirements

### Requirement: Erase a category's history
The Categories page SHALL let the user erase an in-use category's history after
a confirmation that shows the impact (counts of transactions, planned
allocations, and templates affected). After erasing, the category becomes
unused and the row SHALL then offer **Delete**.

#### Scenario: Confirmation shows the blast radius
- **WHEN** the user triggers Erase history for a category
- **THEN** a confirmation shows how many transactions, allocations, and templates will be affected before the user commits

#### Scenario: After erasing, the category becomes deletable
- **WHEN** the user confirms Erase history
- **THEN** the category's transactions, allocations, and template line items are erased via the API, the list refreshes, and the row now offers **Delete**
