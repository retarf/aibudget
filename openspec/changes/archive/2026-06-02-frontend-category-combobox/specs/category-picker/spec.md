## ADDED Requirements

### Requirement: Kind-gated category picker

The application SHALL provide a reusable category picker that is disabled until
a category kind (`income` or `expense`) has been chosen by the surrounding
form. Once a kind is chosen, the picker SHALL offer only the global categories
of that kind; categories of the other kind SHALL NOT be selectable through the
picker by any means.

#### Scenario: Picker disabled until a kind is chosen

- **WHEN** a form containing the picker is shown and no kind has been chosen
- **THEN** the category picker is disabled and no category can be selected

#### Scenario: Only matching-kind categories are offered

- **WHEN** a kind is chosen and the user opens the picker
- **THEN** the picker lists only categories whose kind equals the chosen kind

#### Scenario: Changing the kind clears an invalid selection

- **WHEN** a category is selected and the form's kind is then changed so the
  selected category's kind no longer matches
- **THEN** the selection is cleared and the picker is re-filtered to the new kind

### Requirement: Select an existing category

The picker SHALL let the user filter categories by typing and select an
existing category by keyboard or mouse.

#### Scenario: Typing filters the list

- **WHEN** the user types text into the picker
- **THEN** the list shows only categories of the active kind whose name matches
  the typed text, with the best match highlighted

#### Scenario: Tab accepts the highlighted category

- **WHEN** a category is highlighted and the user presses Tab
- **THEN** that category becomes the selection and focus advances to the next field

#### Scenario: Enter selects an exact match

- **WHEN** the typed text exactly matches the name of an existing category of
  the active kind and the user presses Enter
- **THEN** that existing category is selected and no new category is created

#### Scenario: Tab with no match leaves the field

- **WHEN** the typed text matches no category and the user presses Tab
- **THEN** focus leaves the field and no category is created or selected

### Requirement: Create a category from the picker

The picker SHALL let the user create a new category without leaving the form
when the typed text matches no existing category of the active kind. The new
category MUST take the typed text as its name and the active kind as its kind.
Creation MUST be reachable both by pressing Enter and by activating a create
option shown at the bottom of the list.

#### Scenario: Enter creates a category when none matches

- **WHEN** the typed text matches no existing category of the active kind and
  the user presses Enter
- **THEN** a category is created via the API with the typed name and the active
  kind, the category list refreshes, and the new category becomes the selection

#### Scenario: A single Enter creates exactly one category

- **WHEN** the user types a new name and presses Enter once
- **THEN** exactly one create request is issued — the keypress MUST NOT also
  trigger a second create that would be rejected as a duplicate

#### Scenario: Create option creates a category with the mouse

- **WHEN** the typed text is not an exact match and the user activates the
  "Create '<query>'" option in the list
- **THEN** a category is created via the API with the typed name and the active
  kind and becomes the selection

#### Scenario: Existing name never produces a duplicate

- **WHEN** the typed text exactly matches an existing category of the active kind
- **THEN** the picker selects the existing category and offers no create option

#### Scenario: API rejection on create is surfaced

- **WHEN** the API rejects the category creation
- **THEN** the rejection message is shown and no category is selected

### Requirement: Allocation form chooses a kind before picking a category

The Add-allocation form SHALL present an income/expense selector that starts
unselected and that gates the category picker. The chosen value SHALL drive the
picker's kind in the same way the transaction Type does.

#### Scenario: Allocation kind starts unselected

- **WHEN** the user opens the Add-allocation form
- **THEN** the income/expense selector has no value and the category picker is disabled

#### Scenario: Choosing the allocation kind enables the picker

- **WHEN** the user chooses income or expense in the Add-allocation form
- **THEN** the category picker becomes enabled and lists only categories of that kind

#### Scenario: Category created from the allocation form inherits the chosen kind

- **WHEN** the user creates a category through the picker in the Add-allocation form
- **THEN** the new category is created with the kind chosen in the income/expense selector
