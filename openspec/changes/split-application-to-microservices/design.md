## Context

The backend (`backend/`) is a single FastAPI app. `backend/main.py` mounts
three routers; `backend/database.py` defines one engine/`Base` against one
PostgreSQL database; `backend/services/transaction.py` enforces cross-domain
rules by reading `Budget` and `Category` rows directly (`db.get(...)`). The
domains are otherwise cleanly separated into `models/`, `schemas/`, `services/`,
`routers/` per domain.

This change splits the monolith into three NATS services plus an HTTP gateway,
with a database per service. `nats-py` is already pinned in `requirements.in`.
The React frontend must keep working against the unchanged REST contract.

## Goals / Non-Goals

**Goals:**
- Three independently deployable domain services (budget, category,
  transaction), each owning its own PostgreSQL database.
- Event-driven inter-service communication: services publish domain events and
  build local projections from them.
- Synchronous NATS request/reply only on the gateway↔service edge, so the REST
  contract stays synchronous.
- A thin FastAPI gateway preserving the current REST contract 1:1.
- A messaging contract (request/reply subjects, event subjects, envelopes,
  error mapping) shared by all services so behavior is consistent.

**Non-Goals:**
- No change to externally observable REST behavior or to the frontend.
- No new domain features (reports stay out of scope).
- No production orchestration (Kubernetes, service mesh) — `docker-compose`
  remains the deployment unit.
- No durable/replayable event streams (NATS JetStream) — plain pub/sub for now;
  see Risks.
- No distributed transactions — see Risks.

## Decisions

### Service topology
`gateway` (FastAPI, HTTP :8000) → NATS → `budget-service`,
`category-service`, `transaction-service`. Each service is a long-running
`nats-py` subscriber process with its own PostgreSQL database
(`budget-db`, `category-db`, `transaction-db`). Rationale: one service per
domain mirrors the existing `models/services/routers` split, so the migration
is mostly a re-packaging rather than a redesign.

### Two messaging styles
- **Request/reply** for the gateway↔service edge: one subject per operation,
  namespaced by domain — `budget.create`, `budget.list`, `budget.get`,
  `budget.update`, `budget.delete`, and likewise `category.*` and
  `transaction.*`. These map directly onto today's service functions
  (`create_budget`, `list_budgets`, …) and let the gateway answer HTTP
  synchronously.
- **Event publish/subscribe** for inter-service communication: each service
  publishes `<domain>.created`, `<domain>.updated`, `<domain>.deleted` after a
  successful state change. Consumers subscribe to build local projections.

Rationale: the gateway needs synchronous answers for the unchanged REST
contract, so its edge stays request/reply; service-to-service coupling is what
the user asked to make event-driven, so domain state propagates as events.
Alternative — events for everything, with the gateway correlating reply events
— rejected because it adds correlation machinery without removing the
synchronous wait the gateway must do anyway.

### Message envelopes
- **Request/reply.** Request: the operation's input payload (existing Pydantic
  `*Create`/`*Update` shapes, plus path params like `budget_id` as fields).
  Reply: `{"ok": true, "data": <payload>}` or
  `{"ok": false, "error": {"status": <http-code>, "detail": <str>}}`. The
  gateway maps `error.status`/`error.detail` straight onto the `HTTPException`
  it currently raises, so REST responses are byte-for-byte compatible.
- **Events.** `{"event": "<domain>.<change>", "data": <entity-state>}` —
  `data` is the full entity for `created`/`updated`, and at least the id for
  `deleted`. Pydantic models are reused for (de)serialization throughout.

### API gateway
The gateway keeps the existing route definitions from `backend/routers/*` but
each handler, instead of calling a service function, issues
`nats.request(subject, payload, timeout)` and unwraps the envelope. `/health`
checks NATS connectivity and pings each service. CORS config moves verbatim
from `backend/main.py`. Rationale: the frontend's API client and CORS origins
stay untouched.

### Database per service
Each service gets its own engine/`Base`/session, reusing the current
`backend/database.py` pattern but with a service-specific `DATABASE_URL`.
Models split by domain: `budgets` table → budget-service, `categories` →
category-service, `transactions` → transaction-service. The
`transactions.budget_id` / `transactions.category_id` columns remain as plain
integers but lose their SQL `ForeignKey` constraints, since the referenced
rows live in other databases.

### Transaction validation via a local projection
`transaction-service` subscribes to `budget.*` and `category.*` events and
maintains projection tables (`budget_projection`, `category_projection`) in its
own database. `_validate` (from `backend/services/transaction.py`) is reworked
to read those tables instead of `db.get(Budget/Category, ...)`: a missing
budget yields `404`, a missing category `422`, an out-of-period date `422` —
the same outcomes as the monolith. Event handlers are idempotent (upsert by id;
delete-if-present) so at-least-once redelivery is safe. Rationale: removes the
run-time coupling of the request/reply approach; the trade-off is eventual
consistency (see Risks).

### Cascade on budget or category deletion
`transaction-service` handles `budget.deleted` by deleting every transaction
with that `budget_id`, and `category.deleted` by deleting every transaction
with that `category_id`. Rationale: with no cross-database FK, the monolith's
`ON DELETE CASCADE` for budgets is gone, and category-service can no longer run
the monolith's in-use check (it cannot see transactions). Event-driven cascades
restore consistent cleanup for both without a shared schema. Trade-off:
deleting a category now also removes its transactions instead of being rejected
with `409` — an intentional behavior change recorded in the category-service
spec.

### docker-compose
Replace the `backend` service with: `nats` (`nats:2-alpine`), `gateway`,
`budget-service`, `category-service`, `transaction-service`, and three
`postgres:17-alpine` databases. Domain services `depend_on` their own DB +
`nats`; the gateway depends on `nats`. `.env.template` gains `NATS_URL` (already
present) and per-service `DATABASE_URL`s.

## Risks / Trade-offs

- **Eventual consistency.** A transaction created moments after its budget or
  category may be rejected because the projection has not yet received the
  event. → Acceptable for this app's workload; projection lag is sub-second on
  a healthy NATS connection. Documented behavior, not a bug.
- **At-least-once delivery / duplicates.** An event may be delivered more than
  once. → All projection handlers are idempotent (upsert by id; delete is a
  no-op if absent), so duplicates do not corrupt state.
- **Missed events while a consumer is down.** Plain NATS pub/sub does not
  retain messages for an offline subscriber, so a projection can drift if
  transaction-service is down during a budget/category change. → Accepted for
  this change; a durable stream (NATS JetStream) is a follow-up.
- **Cascade ordering.** A `budget.deleted` event could arrive before a related
  `created`. → Handlers are order-tolerant: a cascade delete for an unknown
  budget is a no-op, and a later transaction referencing a deleted budget fails
  validation.
- **More moving parts in local dev.** ~8 containers (gateway, 3 services, 3
  DBs, NATS) instead of three. → `cli compose up` orchestrates the stack;
  healthchecks gate startup order.
- **Test strategy changes.** The current in-process pytest suite
  (`backend/tests/`, SQLite) must split per service; transaction-service tests
  seed the projection tables directly and assert validation + cascade, and the
  gateway's NATS calls are mocked. → Covered in tasks.md.

## Migration Plan

1. Stand up `nats` and the per-service databases alongside the existing
   backend.
2. Build the three services and the gateway.
3. Switch `docker-compose` and `.env` over; remove the old `backend` service
   and shared database.
4. Rollback: revert `docker-compose.yml`/`.env` and redeploy the monolith
   image — no schema migration is shared, so rollback is config-only as long as
   the old `backend` image is retained.

## Open Questions

- Should the gateway expose readiness separately from liveness (it now depends
  on three services being up)? Assumed: a single `/health` that degrades to
  unhealthy if any service is unreachable.
- Data migration of existing rows from the shared DB into per-service DBs is
  assumed unnecessary (no production data yet); if that changes, a one-off
  copy step is needed.
