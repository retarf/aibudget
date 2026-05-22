## 1. Shared messaging module

- [x] 1.1 Create `common/` package with `__init__.py`
- [x] 1.2 Implement `common/messaging.py`: NATS connect helper, subject name
      constants, request/reply envelope encode/decode (`{"ok", "data"}` /
      `{"ok", "error": {"status", "detail"}}`), event envelope encode/decode
      (`{"event", "data"}`), and an `error_envelope(status, detail)` helper
      mirroring the monolith's `HTTPException` mapping
- [x] 1.3 Add a `ServiceError` exception (status + detail) used by handlers and
      translated into the error envelope

## 2. budget-service

- [x] 2.1 Create `services/budget/` with `database.py` (own `DATABASE_URL`,
      `Base`, session) following the `backend/database.py` pattern
- [x] 2.2 Add `models.py` (the `budgets` table, ported from
      `backend/models/budget.py`); Pydantic schemas are shared via
      `common/schemas.py` (used by gateway and services alike)
- [x] 2.3 Add `handlers.py`: create/list/get/update/delete ported from
      `backend/services/budget.py`, raising `ServiceError` instead of
      `HTTPException`
- [x] 2.4 Add `main.py`: connect to NATS, subscribe to `budget.{create,list,
      get,update,delete}` request/reply subjects, and publish
      `budget.{created,updated,deleted}` events after each successful change
- [x] 2.5 Add `services/budget/Dockerfile` (modeled on `backend/Dockerfile`)

## 3. category-service

- [x] 3.1 Create `services/category/` with `database.py` (own `DATABASE_URL`)
- [x] 3.2 Add `models.py` ported from `backend/models/category.py`; schemas
      shared via `common/schemas.py`
- [x] 3.3 Add `handlers.py` ported from `backend/services/category.py`, raising
      `ServiceError`; in-use check on delete dropped (cascade replaces it)
- [x] 3.4 Add `main.py`: subscribe to `category.{create,list,delete}` subjects
      and publish `category.{created,deleted}` events
- [x] 3.5 Add `services/category/Dockerfile`

## 4. transaction-service

- [x] 4.1 Create `services/transaction/` with `database.py` (own
      `DATABASE_URL`)
- [x] 4.2 Add `models.py`: the `transactions` table (ported from
      `backend/models/transaction.py`, `budget_id`/`category_id` as plain
      integers, no cross-DB `ForeignKey`) plus `budget_projection` and
      `category_projection` tables
- [x] 4.3 Transaction schemas shared via `common/schemas.py`
- [x] 4.4 Add `projection.py`: idempotent event handlers that upsert/delete
      rows in `budget_projection` / `category_projection`
- [x] 4.5 Add `handlers.py`: create/list/get/update/delete ported from
      `backend/services/transaction.py`, with `_validate` reworked to read the
      projection tables (missing budget → 404, missing category → 422,
      out-of-period date → 422)
- [x] 4.6 Add `budget.deleted` / `category.deleted` event handlers that delete
      all transactions with the deleted `budget_id` / `category_id` (cascade)
- [x] 4.7 Add `main.py`: subscribe to `transaction.*` request/reply subjects,
      subscribe to `budget.*` / `category.*` events for the projection and
      cascade, and publish `transaction.{created,updated,deleted}` events
- [x] 4.8 Add `services/transaction/Dockerfile`

## 5. API gateway

- [x] 5.1 Create `gateway/` with a FastAPI `main.py`: lifespan opens a NATS
      connection, CORS middleware ported verbatim from `backend/main.py`
- [x] 5.2 Port `backend/routers/{budgets,categories,transactions}.py` into
      `gateway/routers/`, each handler issuing a NATS request via the `call`
      helper and unwrapping the reply envelope into the response or an
      `HTTPException`; a NATS timeout maps to `503`
- [x] 5.3 Implement `/health`: report healthy only when NATS is reachable and
      every domain service responds (`<domain>.health` subjects)
- [x] 5.4 Add `gateway/Dockerfile`

## 6. Infrastructure

- [x] 6.1 Update `docker-compose.yml`: remove the `backend` service; add
      `nats` (`nats:2-alpine`), `gateway`, the three services, and
      `budget-db` / `category-db` / `transaction-db` (`postgres:17-alpine`
      with healthchecks); wire `depends_on` (services → own DB + nats, gateway
      → nats)
- [x] 6.2 Update `.env.template`: drop the single-DB vars, keep shared
      Postgres credentials + `NATS_URL`; per-service `DATABASE_URL`s are
      composed in `docker-compose.yml`
- [x] 6.3 Update `aibudget_cli/main.py`: replace the `backend` group with a
      `cli test [budget|category|transaction|gateway|all]` command; update
      `pyproject.toml` `testpaths`

## 7. Tests

- [x] 7.1 Split `backend/tests/` into per-service suites; each service's
      handler tests use in-memory SQLite (pattern from
      `backend/tests/conftest.py`)
- [x] 7.2 transaction-service tests: seed `budget_projection` /
      `category_projection` directly and assert validation outcomes and the
      `budget.deleted` / `category.deleted` cascades
- [x] 7.3 Gateway tests: mock the NATS request/reply layer and assert HTTP
      status/body mapping (success, error envelope, timeout → 503) and health
- [x] 7.4 Run every per-service suite and confirm all pass — 28 passed
      (`python -m pytest`; in containers via `cli test all`)

## 8. Documentation & cleanup

- [x] 8.1 Update `CLAUDE.md` architecture section to describe the gateway,
      services, NATS messaging, and database-per-service
- [x] 8.2 Update `README.md` architecture and run instructions for the new
      stack
- [x] 8.3 Remove the obsolete monolith `backend/` app once all services and
      tests are green
