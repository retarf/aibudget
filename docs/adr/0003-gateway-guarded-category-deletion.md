# ADR 0003: Gateway-guarded category deletion with Erase History

**Status:** Accepted
**Date:** 2026-06-02

## Context

Categories are global and owned by category-service, which — by the decision in
the split-to-microservices change — deletes them **unconditionally** and relies
on a `category.deleted` cascade for cleanup (transaction-service deletes the
category's transactions; budget-service deletes its template line items;
planned allocations are deliberately not cascaded). category-service cannot see
transactions, allocations, or templates, which is precisely why the monolith's
"reject delete if in use" check was dropped.

This silently destroys history: deleting a category erases every transaction it
classified across all budgets, with no warning. We want the opposite — deleting
a category in use should be **prevented**, and clearing its history should be a
deliberate, visible act.

## Decision

Invert the model. A category may be deleted only when it is **not in use** —
i.e. no Transaction, Planned Allocation, or Template Line Item references it.
The in-use guard and the new **Erase History** operation are **orchestrated at
the API gateway**, which queries transaction-service and budget-service; 
category-service is unchanged and still deletes unconditionally at its own
level.

- **Block-on-use:** the gateway refuses a delete (`409`) while the category is
  referenced anywhere, returning the impact counts.
- **Erase History:** a separate gateway-orchestrated operation that purges the
  category's transactions and planned allocations from **every** budget and its
  line items from **all** templates, making the category unused so it can then
  be deleted in a second step.
- **Usage-enriched list:** the gateway augments the category list with per-
  category usage counts (bulk "count by category" calls to the two services,
  merged), so the UI can show Erase History vs. Delete per row and render the
  confirmation's blast radius.

## Considered Options

- **category-service usage projection.** category-service subscribes to events
  and keeps a local usage count checked synchronously on delete. Rejected:
  heavy machinery, and it puts eventual-consistency risk on a hard-delete guard.
- **Keep pure cascade (status quo).** Rejected: it is exactly the silent
  history loss we are removing.
- **Gateway orchestration (chosen).** No new owned state; reuses the existing
  service boundaries; keeps category-service ignorant of other domains.

## Consequences

- The gateway becomes the place where cross-domain category usage is known;
  transaction-service and budget-service gain usage-count and purge subjects.
- Erase History spans two services and is therefore **not atomic** — a partial
  failure can leave a partly-erased category; the implementation needs an
  idempotent/retryable purge so it can be re-run safely.
- The existing `category.deleted` cascade is **kept as a safety net** against
  the gateway's check-then-delete race (normally a no-op). Allocations are not
  added to the cascade — only Erase History ever deletes them.
- The `category-api` spec's stale "delete only when no transaction references
  it" requirement is replaced by block-on-any-use.
