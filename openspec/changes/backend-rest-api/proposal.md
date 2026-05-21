## Why

The aibudget app has no backend yet — there is no way for the UI to persist or
retrieve budgets, transactions, or categories. We need a REST API that exposes
the core domain so the React UI can be built against a real contract, and it
should run via Docker Compose so the whole environment starts with one command.

## What Changes

- Add a `docker-compose.yml` in the **project root** that orchestrates the
  backend and its database.
- Add a **PostgreSQL** service to Docker Compose as the project's database
  (for now).
- Add a `backend/` directory containing a FastAPI application, run as a service
  in Docker Compose.
- Introduce SQLAlchemy persistence (backed by PostgreSQL) for the core domain
  (budgets, transactions, categories).
- Expose REST endpoints to create, read, update, and delete budgets.
- Expose REST endpoints to record and manage transactions (incomes and
  expenses) within a budget.
- Expose REST endpoints to manage categories used to classify transactions.
- Provide request/response validation via Pydantic schemas, kept separate from
  the ORM models.
- Manage the stack with the `cli compose` commands (`up`, `down`, `logs`,
  `rebuild`).

## Capabilities

### New Capabilities

- `budget-api`: Manage budgets — the time periods a user records transactions
  in. Covers creating, listing, retrieving, updating, and deleting budgets.
- `transaction-api`: Record and manage transactions (incomes and expenses)
  embedded in time within a budget, each classified by a category.
- `category-api`: Manage the categories used to classify incomes and expenses.

### Modified Capabilities

<!-- None — there are no existing specs under openspec/specs/ yet. -->

## Impact

- **New code**: `docker-compose.yml` at the project root; `backend/` — FastAPI
  app, SQLAlchemy models, Pydantic schemas, routers, and a service layer.
- **Infrastructure**: The FastAPI backend and a PostgreSQL database run as
  Docker Compose services; `cli compose up` starts the full environment.
- **Dependencies**: Uses the already-pinned `fastapi`, `sqlalchemy`,
  `pydantic`, and `httpx` (test client). Adds the `postgres` container image
  and a PostgreSQL driver for SQLAlchemy.
- **APIs**: Introduces the first public REST surface; the React UI will be
  built against it.
- **Data**: Introduces a PostgreSQL database running in a container; an initial
  schema/migration is required.
- **Out of scope**: Authentication, reports, and the NATS microservices —
  these are separate future changes.
