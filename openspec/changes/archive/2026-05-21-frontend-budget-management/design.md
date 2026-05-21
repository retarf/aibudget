## Context

The `frontend-ui` change delivered the app shell with placeholder pages; the
backend exposes a full REST API for budgets, transactions, and categories.
This change replaces the placeholders with working feature pages that exercise
every backend operation.

## Goals / Non-Goals

**Goals:**

- A typed API client wrapping every backend endpoint.
- Budget pages: list, create, edit, delete, and a detail view.
- Transaction management inside the budget detail view.
- Category page: list, kind filter, create, delete.
- Backend validation/conflict errors surfaced to the user.
- msw activated; the pages are covered by component tests.

**Non-Goals:**

- Reports, authentication.
- Pagination, sorting, or search of large lists.
- Optimistic updates / client-side caching libraries.

## Decisions

- **API client.** A `src/api/` module: typed `Budget`, `Transaction`,
  `Category` models and functions per endpoint, built on `fetch`. The base URL
  comes from `import.meta.env.VITE_API_URL` (default `http://localhost:8000`).
  Non-2xx responses throw an `ApiError` carrying the status and the backend's
  `detail` message.
- **Data fetching.** A small `useApiResource` hook holds `data` / `loading` /
  `error` and exposes a `reload()`. No external data-fetching library — keeps
  dependencies unchanged. Mutations call the client, then `reload()`.
- **Routing.** `/budgets` (list), `/budgets/:budgetId` (detail with its
  transactions), `/categories`. The existing routes are repointed from the
  placeholder pages to these.
- **Forms & dialogs.** Mantine `Modal` hosts create/edit forms; `@mantine/form`
  is already available via `@mantine/core`'s peers — if not, simple controlled
  state is used. Delete actions confirm via a Mantine confirm modal.
- **Error display.** Field-level validation (422) maps to form errors; conflict
  (409) and not-found (404) show a Mantine notification / inline alert.
- **Testing.** msw is activated in `setupTests.ts`; `handlers.ts` gains handlers
  for the budget/transaction/category endpoints. Tests render a page, let msw
  answer, and assert on the result.

## Risks / Trade-offs

- **No caching/optimism.** Every mutation triggers a refetch. Simple and
  correct; slightly chattier. Acceptable at this scale.
- **msw in jest.** Activating msw is the fragile part (ESM/global-fetch
  interplay). If it cannot be stabilized quickly, handlers can fall back to a
  hand-rolled `fetch` mock — the page code is unaffected either way.
- **`@mantine/form` availability.** If it is not a transitive dependency it
  must be added; the design keeps forms simple enough to work without it.
- **CORS.** The browser calls the backend cross-origin; the backend must allow
  the frontend origin. Tracked as a backend follow-up if not already enabled.
