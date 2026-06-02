## Context

The budget detail page picks a category in two places — `TransactionForm` and
`AllocationPanel`'s Add-allocation form — each using a plain Mantine `Select`
with no search. Inline creation exists only in the transaction form, via a
`+ New category` button that reveals `InlineCategoryCreator` (a name + kind
mini-form). Categories are **global** (`CONTEXT.md`; `ADR 0001`): one shared
list, each with a `kind` of `income` or `expense`. That kind alone determines
whether an allocation or transaction lands in the planned/actual **income** vs
**expense** column of the budget summary — yet neither form prevents pairing,
say, an expense transaction with an income category.

This design covers a frontend-only UX change decided in a grill session: a
reusable searchable + creatable picker that also enforces kind-matching.

## Goals / Non-Goals

**Goals:**
- One reusable `CategoryCombobox` used by both category-selection sites.
- Type-to-filter, with a keyboard-and-mouse contract for selecting or creating.
- Make a wrong-kind category structurally unselectable in the UI.
- Inline category creation that needs no extra input beyond the typed name.
- Enforce the kind invariant on the backend so a transaction whose category
  kind disagrees with its type is rejected regardless of client.

**Non-Goals:**
- No domain change — categories stay global; glossary and `ADR 0001` unchanged.
- No change to the `/categories` page or its nav entry (full list / delete /
  rename stay there).
- No new NATS event, schema, or database change — backend enforcement reuses the
  `kind` already present in the category projection.
- No new dependency; in particular **not** `mantine-react-table`.

## Decisions

### Build on Mantine core `Combobox`, not `mantine-react-table`

`mantine-react-table` is a data-*grid* library (sorting, pagination, inline row
editing). The requirement is a *combobox*: one input that filters options and
can create a new one. MRT does not provide a creatable picker, so adopting it
would mean building the combobox anyway — plus a heavy new dependency on a
`package.json` that currently has only `@mantine/core` and `@mantine/hooks`.
Mantine v9's `Combobox` primitive is the documented way to build a searchable +
creatable picker (the old `Select creatable` prop was removed in v7). Chosen for
fit and zero new dependencies.

### Kind is a gate, not a filter applied after the fact

The kind selector starts **unselected**; the picker renders **disabled** until a
kind is chosen. Once chosen, the option list is the global categories filtered
to that kind — mismatched categories are never in the list, so they cannot be
selected by keyboard or mouse. This is stronger than "filter and warn": there is
no path to a wrong-kind pairing. Changing the kind re-derives the list and
**clears** any selection whose kind no longer matches (including a legacy
mismatched record opened for edit — it is re-categorized on save).

- `TransactionForm`: the existing **Type** field is the gate; its default is
  removed so the user must choose first.
- `AllocationPanel` Add-allocation form: gains a **new income/expense
  `SegmentedControl`**, starting empty, so the picker behaves identically there.
  This makes the allocation's planned-income-vs-expense intent explicit, which
  the form previously left implicit.

`CategoryCombobox` therefore always receives a resolved `kind` (and is disabled
when it is unset) — no "kind unknown" branch exists in the component.

### Keyboard / create contract

- **Type** → list filters live; the best match is highlighted.
- **Tab** → accept the highlighted existing category and advance focus; if
  nothing matches, Tab just leaves the field (no creation).
- **Enter** → if the query **exactly matches** an existing category of the
  active kind, select it (never create a duplicate); if it matches **nothing**,
  create a category with that name + the active kind and select it.
- **"＋ Create '<query>'" row** at the bottom of the list (shown when the query
  is non-empty and not an exact match) → the mouse equivalent of Enter-to-create.

The safety property: typing an existing name + Enter selects the existing
category rather than creating a duplicate. Exactness is checked within the
kind-filtered list, so the same name under a different kind is a distinct
creatable entry.

The component **owns the keyboard contract** via its own `onKeyDown` and
disables Mantine's built-in keyboard navigation
(`Combobox.Target withKeyboardNavigation={false}`). This is deliberate: Tab and
Enter act on *different* targets (the best existing match vs. the create row),
which a single Mantine "active option" cannot express, and leaving Mantine's
navigation on makes Enter fire twice — once via our handler and once as
"submit the active option" — creating the category and then 409-ing on the
duplicate. The trade-off is no arrow-key navigation of the dropdown; selection
is type-to-filter plus Tab/Enter or mouse click, and the best match is the first
filtered option (deterministic), not an arrow-driven highlight.

### Inline creation inherits the active kind

Creating a category from the picker reuses the existing API path
(`api.createCategory`, then reload the category list and select the new one).
Because the kind is already resolved by the gate, creation needs only the typed
name — the `InlineCategoryCreator` mini-form is removed entirely.

### Backend enforces the kind invariant in `_validate`

The UI gate prevents mismatches at the source, but a guarantee that lives only
in the client is not a guarantee. transaction-service already validates the
referenced budget and category against its local projections in `_validate`
(`backend/services/transaction/handlers.py`) before committing. The
`CategoryProjection` already stores `kind` (fed by `category.created` events),
so the check is a single added condition: after confirming the category exists,
reject with `422` when `category.kind != data.type`. This runs on both create
and update, before the local commit, so a failed validation writes nothing.

No NATS event, Pydantic schema, or database migration is needed — the data is
already projected. The pre-existing assumption in `summarize_by_category` that
"a single category may legitimately appear under both kinds" no longer holds for
new/edited transactions; the summary grouping by transaction type still works
unchanged because type now always equals the category's kind.

Alternative considered: validate at the API gateway instead. Rejected — the
gateway does not hold category kinds, and transaction-service is the component
that owns transaction writes and already does reference validation, so the
invariant belongs with it.

### Category deletion guard + Erase History (gateway-orchestrated)

Full rationale and rejected alternatives are in
`docs/adr/0003-gateway-guarded-category-deletion.md`. Summary of the approach:

- **In-use guard at the gateway.** `category-service` cannot see transactions,
  allocations, or templates, so it stays unconditional. The gateway's
  `DELETE /categories/{id}` first asks transaction-service and budget-service
  whether the category is referenced; if so it returns `409` with the impact
  counts and does **not** call `category.delete`.
- **A category is "in use"** if any Transaction (transaction-service), Planned
  Allocation, or Template Line Item (budget-service) references it. Any one
  blocks deletion.
- **Erase History** is a new gateway operation
  (`POST /categories/{id}/erase-history`) that fans out a purge: transaction-
  service deletes all transactions for the `category_id`; budget-service deletes
  all allocations **and** template line items for it. Scope is the whole system
  (every budget, all templates), not just past budgets. It leaves the category
  itself intact; deletion is a separate, second action.
- **Usage-enriched list.** `GET /categories` is augmented at the gateway with
  per-category usage counts via two bulk "count by category" calls (transaction-
  service: transaction counts; budget-service: allocation + template-item
  counts), merged. The UI uses `in_use` to render Erase History vs Delete and
  the counts to populate the Erase History confirmation.
- **New NATS subjects.** transaction-service:
  `transaction.category.usage` (counts by category) and
  `transaction.category.purge` (delete by category). budget-service:
  `budget.category.usage` and `budget.category.purge` (allocations + template
  items). Purges MUST be idempotent so a re-run after partial failure is safe.
- **Cascade kept as a safety net.** The existing `category.deleted` cascade
  remains; after block-on-use + erase history it is normally a no-op, but it
  cleans up any orphan created by the gateway's check-then-delete race. A code
  comment records why it is retained. Allocations are deliberately not added to
  the cascade.

Frontend: `CategoriesPage` reads `in_use`/counts from the list; an in-use row
shows **Erase History** (which opens an impact-count confirmation, then reloads
the list so the row flips to **Delete**); an unused row shows **Delete**.

## Risks / Trade-offs

- **Pre-existing mismatched transactions remain until edited** → The backend
  check applies on create/update only; historical rows with a mismatched kind
  are not retro-validated → they are left as-is and corrected on next edit (the
  UI clears the now-invalid category and forces a valid re-pick). No data
  migration is performed.
- **Legacy mismatched records get re-categorized on edit** → Opening an existing
  expense-with-income-category transaction clears the category and forces a
  valid re-pick on save. This is intentional (consistent with the gate) but
  changes data the user may not have meant to touch → the cleared field is
  visibly empty and required, so the user must consciously re-pick before saving.
- **Removing the Type default adds a click for the common case** → Recording an
  expense now requires explicitly choosing the Type → accepted; it is the
  literal intent ("no category choice before kind is chosen") and removes the
  silent-default footgun.
- **Combobox keyboard semantics are bespoke** → Tab-selects / Enter-creates is
  not Mantine's out-of-the-box default → covered by explicit jest + msw tests
  for each key path.
- **Erase History is not atomic across services** → it purges transaction-
  service then budget-service; a failure in between leaves a partly-erased
  category → purges are idempotent and the operation is safely re-runnable; the
  category stays undeletable (still "in use") until the purge fully succeeds.
- **Erase History rewrites historical reports** → deleting past transactions
  changes budget summaries retroactively → this is the explicit intent of the
  operation; the impact-count confirmation makes the blast radius visible before
  the user commits.
- **Check-then-delete race** → a transaction could be created between the
  gateway's usage check and `category.delete` → the retained `category.deleted`
  cascade cleans up any resulting orphan.
