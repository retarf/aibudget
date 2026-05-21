## 1. API client

- [x] 1.1 Add `VITE_API_URL` to `.env.template`
- [x] 1.2 Add typed `Budget`, `Transaction`, `Category` models in `src/api/`
- [x] 1.3 Add a `fetch`-based client with an `ApiError` carrying status + detail
- [x] 1.4 Add client functions for every budget, transaction, and category endpoint
- [x] 1.5 Add a `useApiResource` hook exposing `data` / `loading` / `error` / `reload`

## 2. Budget pages (`budget-pages`)

- [x] 2.1 Build the Budgets list page (with an empty state)
- [x] 2.2 Add create and edit forms in a modal, surfacing 422 errors as form errors
- [x] 2.3 Add delete with a confirmation dialog
- [x] 2.4 Build the budget detail view and route `/budgets/:budgetId` to it

## 3. Transaction pages (`transaction-pages`)

- [x] 3.1 List a budget's transactions in the detail view (with an empty state)
- [x] 3.2 Add record and edit forms, surfacing API rejections as form errors
- [x] 3.3 Add delete with a confirmation dialog

## 4. Category page (`category-pages`)

- [x] 4.1 Build the Categories list page
- [x] 4.2 Add a kind filter (income / expense)
- [x] 4.3 Add a create form, surfacing duplicate (409) errors
- [x] 4.4 Add delete with confirmation, surfacing the in-use (409) error

## 5. Tests

- [x] 5.1 Activate msw in `setupTests.ts` and add REST API handlers
- [x] 5.2 Test the budget pages: list, create, invalid period, edit, delete, open detail
- [x] 5.3 Test the transaction pages: list, record, invalid transaction, edit, delete
- [x] 5.4 Test the category page: list, filter, create, duplicate, delete, in-use

## 6. Wrap-up

- [ ] 6.1 Run the frontend test suite and confirm all scenarios pass
- [ ] 6.2 Update `README.md` if any developer-facing steps changed
- [ ] 6.3 Run `./cli openspec validate frontend-budget-management` and archive the change
