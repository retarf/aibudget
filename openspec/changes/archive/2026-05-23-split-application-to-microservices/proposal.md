## Why

The backend is a single FastAPI monolith: the budget, category, and
transaction domains share one process, one `Base.metadata`, and one PostgreSQL
database. `CLAUDE.md` already declares the intended architecture includes
"microservices: nats-py", so the domains should be split into independently
deployable services that communicate over NATS — improving isolation, allowing
each domain to scale and evolve on its own, and matching the documented design.

## What Changes

- Decompose the monolithic backend into three domain services, each its own
  process: **budget-service**, **category-service**, **transaction-service**.
- Introduce a **NATS** server with two messaging styles:
  - **Request/reply** for the gateway↔service edge (HTTP-facing create, read,
    update, delete operations).
  - **Event publish/subscribe** for inter-service communication: every domain
    service publishes domain events (`budget.created/updated/deleted`,
    `category.*`, `transaction.*`) after each state change.
- Each service owns **its own PostgreSQL database**. The current cross-domain
  foreign keys (`transactions.budget_id`, `transactions.category_id`) are no
  longer enforced by the database. Instead, `transaction-service` **subscribes
  to budget and category events** and maintains a **local read-model
  projection** of those domains; transaction validation runs against the
  projection (eventually consistent).
- `transaction-service` reacts to `budget.deleted` / `category.deleted` events
  by **deleting the affected transactions** — restoring, via events, the
  monolith's `ON DELETE CASCADE` for budgets and replacing its in-use check for
  categories.
- **BREAKING** (behavior): deleting a category that is used by transactions now
  succeeds and removes those transactions, instead of being rejected with
  `409`. category-service cannot see transactions, so the in-use check is
  dropped in favor of the cascade.
- Add a thin **API gateway** (FastAPI) that keeps the existing REST routes
  (`/budgets`, `/categories`, `/transactions`, `/health`) and translates each
  HTTP request into a NATS request/reply call. The React frontend and its API
  client are **unchanged**.
- Update `docker-compose.yml`: replace the single `backend` service with the
  gateway, three domain services, a `nats` server, and a database per service.
- **BREAKING** (internal/deployment only): the single `backend` container and
  shared database are removed; deployment topology and `.env` change. The
  external REST contract consumed by the frontend is preserved.

## Capabilities

### New Capabilities
- `api-gateway`: HTTP entry point that preserves the existing REST contract and
  translates requests to NATS request/reply calls.
- `service-messaging`: the NATS messaging contract — request/reply subjects and
  envelopes for the gateway edge, plus the domain-event subjects, event
  envelope, and projection-consumer rules shared by all services.
- `budget-service`: the budget domain as an independent NATS service owning its
  own database.
- `category-service`: the category domain as an independent NATS service owning
  its own database.
- `transaction-service`: the transaction domain as an independent NATS service
  owning its own database, validating budget and category references against a
  local projection built from budget/category events, and cascading deletes on
  `budget.deleted`.

### Modified Capabilities
<!-- None. The existing REST-behavior specs (budget-api, category-api,
     transaction-api) describe externally observable behavior, which the API
     gateway preserves unchanged. -->

## Impact

- **Code:** `backend/` is restructured from one app into a `gateway/` and three
  `services/*` packages; `backend/services/transaction.py` validation switches
  from direct DB reads to a local projection fed by budget/category events.
- **APIs:** external REST contract unchanged; new internal NATS request/reply
  subjects and domain-event subjects added.
- **Data:** one shared PostgreSQL becomes one database per service; no
  cross-service DB foreign keys.
- **Infrastructure:** `docker-compose.yml` gains a `nats` service, a gateway,
  three domain services, and per-service databases; `.env.template` /`.env`
  gain NATS and per-service DB settings.
- **Dependencies:** `nats-py` (already pinned in `requirements.in`) becomes a
  runtime dependency of every service.
- **Frontend:** no changes.
