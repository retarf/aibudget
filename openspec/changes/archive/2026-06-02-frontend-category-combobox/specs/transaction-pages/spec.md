## MODIFIED Requirements

### Requirement: Record a transaction
A budget's detail view SHALL let the user record a transaction by entering a
type, an amount, a date, and a category. The Type SHALL start unselected, and
the category picker SHALL be disabled until a Type is chosen. Once a Type is
chosen, only categories of the matching kind SHALL be selectable.

#### Scenario: Transaction recorded
- **WHEN** the user submits the record form with valid values
- **THEN** the transaction is created via the API and appears in the list

#### Scenario: Category cannot be chosen before a Type
- **WHEN** the user opens the record form and has not chosen a Type
- **THEN** the category picker is disabled and the form cannot be submitted

#### Scenario: Category is limited to the chosen Type's kind
- **WHEN** the user chooses a Type and opens the category picker
- **THEN** the picker offers only categories whose kind matches the chosen Type

#### Scenario: Invalid transaction is reported
- **WHEN** the user submits a transaction the API rejects (e.g. a date outside the budget period)
- **THEN** the API rejection is shown as a form error and no transaction is created

## REMOVED Requirements

### Requirement: Create a category from the transaction form
**Reason**: Inline category creation is replaced by the reusable kind-gated
category picker, removing the separate add-category control and the
`InlineCategoryCreator` mini-form.
**Migration**: Creating a category while recording a transaction is now done
through the category picker (type a new name and press Enter, or use the
"Create" option). The new category inherits the chosen Type's kind. See the
`category-picker` capability.
