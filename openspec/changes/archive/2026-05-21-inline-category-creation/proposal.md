## Why

When recording a transaction, the category dropdown only offers categories
that already exist. If the one the user needs is missing, they must abandon
the half-filled transaction form, go to the Categories page, create the
category, and start over. Letting them create the category in place removes
that interruption.

## What Changes

- Add an "add category" affordance to the transaction form's category field.
- Activating it opens an inline create-category form (name + kind).
- On success, the new category is created via the existing REST API and
  becomes the form's selected category — the transaction form keeps its
  other in-progress values.
- Duplicate-category and other API errors are surfaced inline.

## Capabilities

### New Capabilities

<!-- None. -->

### Modified Capabilities

- `transaction-pages`: Adds the ability to create a category from within the
  transaction form, in addition to selecting an existing one.

## Impact

- **Code**: `frontend/src/components/TransactionForm.tsx` (and a reused
  category create form). No new pages.
- **APIs**: Uses the existing `POST /categories` endpoint — no backend or API
  changes.
- **Dependencies**: None.
- **Out of scope**: Editing or deleting categories from the transaction form,
  and inline creation in any other form.
