# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview
The home budget app. It contains:
- incomes
- expenses
- reports

## Architecture

The backend is split into an HTTP API gateway and three domain services that
communicate over NATS; each service owns its own PostgreSQL database.

- **UI** — React, Mantine (tested with jest + msw); in `frontend/`.
- **API gateway** — FastAPI; exposes the REST API and translates each request
  into a NATS request/reply call. In `backend/gateway/`.
- **Domain services** — `budget-service`, `category-service`,
  `transaction-service`, each a `nats-py` process owning its own database; in
  `backend/services/<domain>/`.
- **Messaging** — NATS. Request/reply on the gateway↔service edge; domain
  events (`<domain>.created/updated/deleted`) between services.
  transaction-service maintains a local projection of budgets/categories from
  those events and cascades deletes. Shared helpers in `backend/common/`.
- **Persistence** — PostgreSQL, one database per service.

### Data model:
budget (period of time where user can add expenses and incomes)
transaction (income, expenses) embedded in time
categories of expenses and incomes

## Commands

Commands are built using the Python click library. Every command starts with the 'cli' keyword.

### cli openspec
openspec - run openspec commands inside a docker container with result in projects ./openspec directory

#### cli openspec init
initialize the openspec


