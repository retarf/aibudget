## Why

The frontend shell exists and the backend exposes a full REST API, but the
shell's pages are placeholders — users cannot actually manage their data. This
change builds the feature pages so every backend operation (budgets,
transactions, categories) is usable from the UI.

## What Changes

- Add a typed REST API client in the frontend that wraps every backend
  endpoint and surfaces errors.
- Build the **Budgets** pages: list all budgets, create, edit, and delete a
  budget, and open a budget's detail view.
- Build the **transactions** UI inside a budget's detail view: list the
  budget's transactions, record, edit, and delete a transaction.
- Build the **Categories** page: list categories (filterable by kind), create
  a category, and delete a category.
- Surface backend validation and not-found errors to the user (e.g. invalid
  budget period, duplicate category, category in use).
- Activate msw in the test setup and add request handlers mocking the REST
  API, so the new pages are testable.
- Add `VITE_API_URL` to `.env.template` for the API base URL.

## Capabilities

### New Capabilities

- `budget-pages`: UI for managing budgets — listing, creating, editing,
  deleting, and viewing a budget.
- `transaction-pages`: UI for managing the transactions within a budget —
  listing, recording, editing, and deleting a transaction.
- `category-pages`: UI for managing categories — listing (with a kind filter),
  creating, and deleting a category.

### Modified Capabilities

<!-- None — the app-shell and theme-switching specs are unaffected. -->

## Impact

- **New code**: `frontend/src/` — an API client, typed models, and the budget,
  transaction, and category pages, replacing the placeholder pages from the
  `frontend-ui` change.
- **Tests**: msw is activated in `setupTests.ts`; handlers mock the REST API.
- **Config**: `VITE_API_URL` added to `.env.template`.
- **APIs**: Consumes the existing REST API; no backend changes.
- **Dependencies**: No new dependencies — uses `fetch`, React, and Mantine.
- **Out of scope**: Reports, authentication, and pagination/search of large
  lists — separate future changes.
