## Why

Categories are global, but the only convenient place to need one is while
recording a transaction or planning an allocation inside a budget. Today the
category field is a plain `Select` with no search, and creating a missing
category means a separate `+ New category` button and a nested mini-form
(`InlineCategoryCreator`). The flow is clunky, and nothing stops a user from
attaching an income category to an expense (or vice versa), which silently
corrupts the planned-vs-actual summary.

## What Changes

- Add a reusable **searchable + creatable category picker** built on Mantine
  core's `Combobox` (no new dependency; **not** `mantine-react-table`). Type to
  filter, **Tab** to accept the highlighted match, **Enter** to select an exact
  match or create when none exists, plus a **"＋ Create '<query>'"** row for the
  mouse.
- The picker is **gated by kind**: the kind selector starts **unselected** and
  the picker is **disabled** until the user chooses income or expense. Only
  categories of the chosen kind are shown — a wrong-kind category is never
  selectable. Changing the kind re-filters and clears any now-invalid selection.
- A newly created category **inherits the active kind** — no separate kind
  prompt.
- Use the picker in **both** category-selection sites on the budget detail page:
  - `TransactionForm` — driven by the existing **Type** field (default removed
    so the user must choose first).
  - `AllocationPanel`'s Add-allocation form — gains a **new income/expense
    toggle** that drives the picker.
- **Remove** `InlineCategoryCreator`; its job is absorbed into the picker.
- **Enforce the kind invariant on the backend too.** transaction-service SHALL
  reject creating or updating a transaction whose category's kind does not match
  the transaction type, so a mismatched pairing is impossible regardless of
  client. The category projection already stores `kind`, so this is a validation
  addition only — no new events or schema changes.
- Categories stay global; the `/categories` page keeps its nav entry. Category
  management on that page is reworked by the deletion guard below.

### Category deletion guard + Erase History

Today deleting a category succeeds unconditionally and silently cascade-deletes
its transactions. This inverts that model (see ADR 0003):

- **Block deletion while a category is in use.** A category is *in use* if any
  Transaction, Planned Allocation, or Template Line Item references it. The
  gateway refuses the delete with `409` and returns the impact counts.
- **Add an Erase History operation.** A separate, gateway-orchestrated operation
  purges the category's transactions and planned allocations from **every**
  budget and its line items from **all** templates, leaving it unused so it can
  then be deleted in a second step. It does not delete the category itself.
- **Gateway orchestration.** category-service still deletes unconditionally at
  its own level; the gateway is what checks usage and fans out the purge across
  transaction-service (transactions) and budget-service (allocations + template
  items).
- **Usage-enriched category list.** The gateway augments the category list with
  per-category usage counts (bulk "count by category" calls merged in), so the
  Categories page shows **Erase History** when a category is in use and
  **Delete** only when it is not — never both — and the Erase History
  confirmation shows the blast radius.
- **Keep the `category.deleted` cascade as a safety net** against the gateway's
  check-then-delete race; allocations are not added to the cascade (only Erase
  History deletes them).

## Capabilities

### New Capabilities
- `category-picker`: The reusable searchable + creatable category combobox —
  its filtering, keyboard/create contract, kind-gating behavior, and its use in
  the budget detail page's transaction and allocation forms (including the new
  allocation income/expense toggle).

### Modified Capabilities
- `transaction-pages`: The "Create a category from the transaction form"
  requirement is replaced (inline creation now happens through the picker, not a
  separate add-category control), and recording a transaction now requires a
  Type to be chosen before a category can be selected.
- `transaction-service`: The projection-validation requirement now also rejects
  a transaction whose category kind does not match the transaction type. Adds
  NATS subjects to count and to purge transactions by `category_id`.
- `transaction-api`: Recording or updating a transaction with a category whose
  kind does not match the transaction type is rejected with `422`.
- `category-api`: Deleting a category in use returns `409` with impact counts
  (replacing the stale transaction-only rule); the list carries per-category
  usage counts; a new Erase History endpoint purges the category's footprint.
- `category-service`: Clarifies that the in-use guard is enforced upstream at
  the gateway; the service itself still deletes unconditionally.
- `budget-service-planning`: Adds NATS subjects to count and to purge a
  category's allocations and template line items by `category_id`.
- `category-pages`: The Categories page shows Erase History vs Delete per
  category by usage, with an impact-count confirmation for Erase History.

## Impact

- **Frontend.** New `frontend/src/components/CategoryCombobox.tsx`; removed
  `frontend/src/components/InlineCategoryCreator.tsx`. Modified:
  `frontend/src/components/TransactionForm.tsx`,
  `frontend/src/components/AllocationPanel.tsx`. `CategoriesPage` reworked for
  usage-driven Erase History / Delete actions. Tests: `TransactionForm`,
  `AllocationPanel`, `BudgetDetailPage`, `CategoriesPage` (jest + msw) and new
  `CategoryCombobox` tests; msw handlers gain usage + erase-history routes.
- **Backend.** Kind-match check in `transaction/handlers.py`. New cross-service
  NATS subjects: usage-count and purge-by-category on transaction-service and
  budget-service. Gateway orchestrates the in-use guard, usage-enriched list,
  and Erase History across both services. The `category.deleted` cascade is kept
  as a safety net.
- No new dependency. Recorded in `docs/adr/0003-gateway-guarded-category-deletion.md`.
