## Why

Users recreate similar budgets every period (monthly rent, salary, groceries,
etc.) by hand, retyping the same income and expense lines. We want them to
save a reusable **budget template** once and then spin up a new budget from
it by supplying only the new dates.

## What Changes

- New domain concept **budget template**: a named blueprint owning a list of
  default lines (category + kind income/expense + amount).
- New **template-service**: its own process, its own PostgreSQL database,
  its own NATS subjects (`template.create|list|get|update|delete`). It does
  not share storage with budget-service so the template schema can evolve
  without risking budget data.
- Add an "instantiate" operation orchestrated by the gateway:
  `POST /templates/{id}/instantiate` with a start/end date creates a real
  budget plus one transaction per template line via existing services.
- `transaction-service` gains a `transaction.create_many` bulk handler so
  instantiate is a single round-trip to that service.
- Frontend: a Templates page (list / create / edit / delete) and a "Create
  budget from template" entry point on the Budgets page that asks only for
  the dates.

## Capabilities

### New Capabilities
- `template-service`: independent process, owner of the `budget_templates`
  and `budget_template_lines` tables, NATS handlers, and `template.*`
  events.
- `template-api`: REST endpoints `/templates` (CRUD) and
  `/templates/{id}/instantiate` on the gateway.
- `template-pages`: the frontend Templates page and the
  instantiate-from-template flow on Budgets.

### Modified Capabilities
- `transaction-service`: SHALL accept a bulk-create operation
  (`transaction.create_many`) used by the instantiate flow to materialize
  a template's lines as transactions in a newly created budget.
- `budget-pages`: SHALL offer a "Create from template" action that opens a
  template-picker + date inputs and calls the instantiate endpoint.

## Impact

- **backend/services/template** (new): ORM models, handlers, migrations,
  Dockerfile, tests, and NATS subjects
  (`template.create|list|get|update|delete` and `template.*` events).
- **backend/services/transaction**: new `transaction.create_many` handler
  used by the instantiate orchestration.
- **backend/gateway**: new `/templates` routes and a
  `/templates/{id}/instantiate` route that fans out a `budget.create` +
  `transaction.create_many` (with best-effort rollback on partial failure).
- **backend/common/schemas.py**: Pydantic models for template, template
  line, and instantiate payloads.
- **docker-compose.yml**: a `template-service` service and its
  `template-db` PostgreSQL instance.
- **cli**: a `template` test target added to `TEST_TARGETS`.
- **frontend**: new `TemplatesPage`, template form, "Create from template"
  modal on `BudgetsPage`, API client and MSW handlers.
- No breaking changes to existing budget, category, or transaction APIs.
