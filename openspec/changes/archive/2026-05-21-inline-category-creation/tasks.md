## 1. Transaction form

- [x] 1.1 Add an "add category" control beside the category `Select` in `TransactionForm`
- [x] 1.2 Toggle an inline panel containing a category create form (`InlineCategoryCreator`, not the `<form>`-wrapped `CategoryForm`, to avoid nested forms)
- [x] 1.3 On create, call `api.createCategory`, surface duplicate/API errors inline
- [x] 1.4 On success, refresh the category list and select the new category
- [x] 1.5 Ensure the type, amount, and date fields are preserved across the create

## 2. Wiring

- [x] 2.1 Pass an `onCreateCategory` callback from the budget detail page so its category resource reloads
- [x] 2.2 Confirm the newly created category appears in the `Select` options

## 3. Tests

- [x] 3.1 Test creating a category inline selects it in the transaction form
- [x] 3.2 Test that other transaction fields are kept across the inline create
- [x] 3.3 Test that a duplicate category is reported inline

## 4. Wrap-up

- [ ] 4.1 Run the frontend test suite and confirm all scenarios pass
- [ ] 4.2 Run `./cli openspec validate inline-category-creation` and archive the change
