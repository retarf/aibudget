# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview
The home budget app. It contains:
- incomes
- expenses
- reports

## Architecture
- UI (React, Mantine, jest, msw)
- REST API: FastAPI 
- microservices: nats-py

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


