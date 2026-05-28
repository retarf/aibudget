# ADR 0001: Planned Allocations as a Separate Entity

**Status:** Accepted  
**Date:** 2026-05-28

## Context

Adding budget planning requires storing a "planned amount" per category per budget. The obvious shortcut is to add a `planned` flag to the existing Transaction model — a planned transaction would represent intent rather than an actual financial event.

## Decision

Planned allocations are a first-class entity separate from transactions, owned by the budget-service. A planned allocation holds `(budget_id, category_id, planned_amount)` and is never a transaction.

## Reasons

- **Transactions represent facts.** A transaction is something that happened — a specific amount on a specific date. A planned allocation is intent with no date and no confirmed amount. Mixing them forces every transaction query to filter on a `planned` flag and creates ambiguity about what "the transaction list" means.
- **Different lifecycle.** Allocations are set once and edited occasionally; transactions are append-only. A planned flag on transactions would require allowing mutation of otherwise immutable records.
- **Summary clarity.** The budget summary compares planned vs actual. With a single table, this requires a self-join or two filtered aggregations on the same table. With separate entities, it is two independent queries merged at the gateway.

## Trade-offs

The gateway must aggregate from two services (budget-service for allocations, transaction-service for actuals) to produce the full budget summary. This adds one NATS round-trip per summary request.
