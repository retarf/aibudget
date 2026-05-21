## 1. Docker Compose & infrastructure

- [x] 1.1 Add `.env.template` listing all required credentials and variables; the `.env` file is created and maintained manually by the developer (never committed)
- [x] 1.2 Create `docker-compose.yml` at the project root, reading environment from `.env`, with a `db` (PostgreSQL) service and a named volume for its data
- [x] 1.3 Add a healthcheck to the `db` service
- [x] 1.4 Add a `backend` service with a `Dockerfile`, environment from `.env`, and `depends_on: db` with `condition: service_healthy`
- [ ] 1.5 Verify the stack starts with `./cli compose up` and the backend reaches PostgreSQL

## 2. Backend skeleton

- [x] 2.1 Create the `backend/` package with `routers/`, `services/`, `models/`, and `schemas/` subpackages
- [x] 2.2 Add the FastAPI app entry point and a health endpoint
- [x] 2.3 Add the PostgreSQL driver (`psycopg`) to `requirements.in` and recompile `requirements.txt`
- [x] 2.4 Add SQLAlchemy engine/session setup and a session-per-request dependency
- [x] 2.5 Create database tables on startup (`create_all`)

## 3. Category API (`category-api`)

- [x] 3.1 Add the `Category` SQLAlchemy model (name, kind) with a uniqueness constraint on (name, kind)
- [x] 3.2 Add `CategoryCreate` / `CategoryRead` Pydantic schemas
- [x] 3.3 Implement the category service: create (reject duplicate name per kind), list (filterable by kind), delete (reject if referenced)
- [x] 3.4 Add the category router (create 201, list 200, delete 204/409)
- [x] 3.5 Test category create, duplicate rejection, invalid kind, list, filtered list, delete, and delete-in-use

## 4. Budget API (`budget-api`)

- [x] 4.1 Add the `Budget` SQLAlchemy model (name, start date, end date) with cascade delete to transactions
- [x] 4.2 Add `BudgetCreate` / `BudgetRead` Pydantic schemas
- [x] 4.3 Implement the budget service: create/update with end-after-start validation, list, retrieve, delete
- [x] 4.4 Add the budget router (create 201, list 200, retrieve 200/404, update 200/404, delete 204/404)
- [x] 4.5 Test create, invalid period, list, retrieve found/not-found, update, delete, and transaction cascade

## 5. Transaction API (`transaction-api`)

- [x] 5.1 Add the `Transaction` SQLAlchemy model (budget, type, amount, date, category)
- [x] 5.2 Add `TransactionCreate` / `TransactionRead` Pydantic schemas
- [x] 5.3 Implement the transaction service: record/update with date-within-budget and amount > 0 validation, list per budget, retrieve, delete
- [x] 5.4 Add the transaction router (create 201/404, list 200, retrieve 200/404, update 200/404, delete 204/404)
- [x] 5.5 Test record, date-outside-period, non-positive amount, missing budget, list, retrieve, update, and delete

## 6. Wrap-up

- [x] 6.1 Run the full test suite (`pytest`) and confirm all scenarios pass
- [x] 6.2 Update `README.md` with how to start the backend via `./cli compose up`
- [ ] 6.3 Run `./cli openspec validate backend-rest-api` and archive the change
