## ADDED Requirements

### Requirement: Indicate income vs expense without a dedicated type/kind column

Income and expense rows on a budget's detail view SHALL convey their direction without a dedicated type/kind text column. This applies to both the transactions list and the per-category summary breakdown. Each such row SHALL indicate whether it is income or expense using a color cue AND a redundant non-color cue, so the distinction never relies on color alone.

#### Scenario: Transaction row shows its direction without a type column

- **WHEN** the user views the transactions list on a budget's detail view
- **THEN** each row conveys income vs expense by a color cue and a redundant
  non-color cue, and no separate type column is present

#### Scenario: Per-category summary row shows its direction without a kind column

- **WHEN** the user views the per-category summary on a budget's detail view
- **THEN** each row conveys income vs expense by a color cue and a redundant
  non-color cue, and no separate kind column is present

#### Scenario: Direction is distinguishable without color

- **WHEN** income and expense rows are viewed in grayscale or by a colorblind
  user
- **THEN** the non-color cue still distinguishes income from expense

### Requirement: View planned vs actual by category

A budget's detail view SHALL display a per-category breakdown showing, for each
category that appears in the budget's summary, the category together with its
planned amount and its actual amount.

#### Scenario: Breakdown is shown

- **WHEN** the user opens a budget's detail view and the summary has at least one category
- **THEN** the breakdown lists each category with its planned and actual amounts

#### Scenario: Category with an allocation but no transactions

- **WHEN** a category has a planned allocation but no recorded transactions
- **THEN** its breakdown row shows the planned amount and an actual amount of `0.00`

#### Scenario: Category with transactions but no allocation

- **WHEN** a category has recorded transactions but no planned allocation
- **THEN** its breakdown row shows a planned amount of `0.00` and the actual amount

#### Scenario: No categories to break down

- **WHEN** the budget has no allocations and no transactions
- **THEN** the per-category breakdown is not shown

### Requirement: View a budget's planned allocations

A budget's detail view SHALL display the budget's planned allocations, each with
its category and its planned amount.

#### Scenario: Allocations are listed

- **WHEN** the user opens a budget's detail view and the budget has planned allocations
- **THEN** each allocation is shown with its category and planned amount

#### Scenario: No allocations yet

- **WHEN** the user opens a budget that has no planned allocations
- **THEN** an empty-state message is shown

### Requirement: Add a planned allocation

A budget's detail view SHALL let the user add a planned allocation by choosing a
kind, then a category of that kind, and entering a planned amount. The category
picker SHALL be disabled until a kind is chosen, and once a kind is chosen only
categories of the matching kind SHALL be selectable.

#### Scenario: Allocation added

- **WHEN** the user submits the add-allocation form with a kind, a matching category, and an amount
- **THEN** the allocation is created via the API and appears in the allocations list

#### Scenario: Category cannot be chosen before a kind

- **WHEN** the user opens the add-allocation form and has not chosen a kind
- **THEN** the category picker is disabled and the form cannot be submitted

#### Scenario: Duplicate allocation is reported

- **WHEN** the user adds an allocation for a category that already has one on the budget
- **THEN** the API rejection is shown to the user and no second allocation is created

### Requirement: Edit a planned allocation

A budget's detail view SHALL let the user edit the planned amount of an existing
allocation.

#### Scenario: Allocation amount updated

- **WHEN** the user saves a new planned amount for an allocation
- **THEN** the allocation is updated via the API and the list reflects the new amount

### Requirement: Delete a planned allocation

A budget's detail view SHALL let the user delete a planned allocation.

#### Scenario: Allocation deleted

- **WHEN** the user clicks the delete control on an allocation
- **THEN** the allocation is removed via the API and disappears from the list

### Requirement: Apply a template to a budget

A budget's detail view SHALL let the user apply a budget template to bulk-create
planned allocations. Applying a template SHALL create an allocation only for
each template line item whose category does not already have an allocation on
the budget; existing allocations SHALL be left unchanged.

#### Scenario: Template applied

- **WHEN** the user selects a template and applies it
- **THEN** allocations are created for the template's categories that the budget did not already have, and the allocations list reflects them

#### Scenario: Existing allocations are preserved

- **WHEN** the applied template includes a category the budget already has an allocation for
- **THEN** that existing allocation is left unchanged

#### Scenario: No templates available

- **WHEN** the user opens the apply-template control and no templates exist
- **THEN** a message indicates there are no templates to apply

## MODIFIED Requirements

### Requirement: View a budget's transactions

A budget's detail view SHALL display all transactions belonging to that budget.

#### Scenario: Transactions are listed

- **WHEN** the user opens a budget's detail view
- **THEN** the budget's transactions are shown with their amount, date, and
  category, and each transaction's income/expense direction is conveyed by the
  income/expense cue rather than a separate type column

#### Scenario: No transactions yet

- **WHEN** the user opens a budget that has no transactions
- **THEN** an empty-state message is shown

### Requirement: Show a budget's income, expense and net totals

A budget's detail view SHALL display the budget's aggregate totals — planned
income, actual income, planned expense, actual expense, and net (actual income
minus actual expense) — grouped together as a single totals panel placed
directly beneath the budget's name and period. The totals SHALL be loaded from
the budget's summary endpoint.

#### Scenario: Totals are shown for a budget with transactions

- **WHEN** the user opens a budget's detail view and the budget has at least one transaction
- **THEN** the panel shows the planned income, actual income, planned expense, actual expense, and net figures returned by the summary API

#### Scenario: Totals are shown for a budget without transactions

- **WHEN** the user opens a budget's detail view and the budget has no transactions
- **THEN** the panel shows `0.00` for actual income, actual expense, and net

#### Scenario: Totals refresh after a transaction is recorded

- **WHEN** the user records a transaction from the budget's detail view
- **THEN** the displayed totals update to reflect the new transaction without a page reload

#### Scenario: Totals refresh after a transaction is edited

- **WHEN** the user saves changes to a transaction from the budget's detail view
- **THEN** the displayed totals update to reflect the change without a page reload

#### Scenario: Totals refresh after a transaction is deleted

- **WHEN** the user deletes a transaction from the budget's detail view
- **THEN** the displayed totals update to reflect the deletion without a page reload

#### Scenario: Summary load error is surfaced

- **WHEN** the summary API returns an error while loading the totals
- **THEN** the page displays the error message and does not render stale totals
