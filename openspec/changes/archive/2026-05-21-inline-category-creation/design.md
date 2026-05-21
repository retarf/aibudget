## Context

The transaction form (`frontend-budget-management`) lets the user pick a
category from existing ones. This change adds inline creation so a missing
category no longer forces the user out of the form.

## Goals / Non-Goals

**Goals:**

- An add-category control next to the transaction form's category field.
- An inline create form (name + kind) reusing the existing category form.
- The created category is auto-selected; other transaction fields are kept.
- API errors (e.g. duplicate) shown inline.

**Non-Goals:**

- Editing or deleting categories from the transaction form.
- Inline creation in other forms (budget, etc.).

## Decisions

- **Affordance.** A small "+ New" button beside the category `Select`. It
  toggles an inline panel (not a nested modal — nesting modals is awkward)
  containing the existing `CategoryForm`.
- **Reuse.** `CategoryForm` is reused as-is; on submit the parent calls
  `api.createCategory`.
- **State.** `TransactionForm` becomes responsible for refreshing categories
  after a create. The page passes a callback (or the form calls the client and
  the page reloads its category resource); the new category's id is set as the
  form's `categoryId`. Other field state is local to `TransactionForm` and is
  untouched by this flow.
- **Errors.** A create failure keeps the inline panel open and shows the
  message; a success closes the panel and selects the category.

## Risks / Trade-offs

- **Where the category list lives.** Categories are fetched by the budget
  detail page and passed into `TransactionForm`. The cleanest wiring is a
  `onCategoryCreated` callback that triggers the page's category `reload()` and
  reports the new id. Slight added coupling between page and form — acceptable.
- **Inline panel vs nested modal.** An inline panel avoids modal-in-modal focus
  issues at the cost of a taller form. Acceptable for a two-field create.
