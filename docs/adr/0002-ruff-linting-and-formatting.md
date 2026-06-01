# ADR 0002: Ruff for Python Linting and Formatting

**Status:** Accepted  
**Date:** 2026-06-01

## Context

The Python codebase (gateway, three domain services, the `aibudget_cli`) had no
linter or formatter. The goal is a codebase that stays "clear and consistent
with best practices" without relying on anyone remembering to check.

## Decision

Adopt [ruff](https://docs.astral.sh/ruff/) as the single linter **and** formatter
for all Python. It is pinned in `requirements-dev.txt` (kept out of the runtime
`requirements.txt`, so production images don't ship it) and configured in
`[tool.ruff]` in `pyproject.toml`:

- `target-version = "py311"` (the project's minimum supported Python)
- `line-length = 88`
- `lint.select = ["E", "F", "I", "UP", "B", "SIM", "C4"]`
- scoped to `backend/` and `aibudget_cli/`

Enforcement is a **Claude Code `Stop` hook** in `.claude/settings.json` that runs
`ruff check` and `ruff format --check` (report-only) and **blocks** completion of
a turn until both pass. The hook invokes ruff via `pyenv exec` so it works on any
machine with the `aibudget` pyenv virtualenv, with no hardcoded paths.

## Reasons

- **Best-practices ruleset, not just the default.** Ruff's defaults (`E`, `F`) are
  only a syntax/unused-import safety net. The curated set adds import sorting
  (`I`), modern-syntax upgrades (`UP`), likely-bug detection (`B`), simplification
  (`SIM`) and comprehension hygiene (`C4`) — the breadth that makes "best
  practices" meaningful. Measured cost was small: 6 lint errors and 36 files to
  reformat, fixed once in a baseline commit.
- **Block, don't warn.** A non-blocking warning lets violations land, so the
  codebase drifts back out of consistency. Blocking at the natural "I'm finished"
  moment guarantees checked-and-clean code every time.
- **Report-only, no silent rewrites.** The hook never auto-edits; every change
  passes through a reviewed diff rather than ruff rewriting files after work is
  declared done.

## Considered options

- **Default ruleset (`E`, `F`) only** — passed with zero changes but doesn't
  deliver "best practices" (no import sorting, modernization, or bug detection).
- **Near-`ALL` ruleset** (docstrings, annotations, naming) — hundreds of
  violations on existing code, fought the developer more than it helped.
- **PostToolUse hook** (lint after every edit) — tighter loop but fires on
  half-finished intermediate states; rejected for noise.
- **pre-commit / CI enforcement** — deliberately deferred. The config and
  `requirements-dev.txt` make adding them later trivial; for now the Stop hook
  covers the stated need.

## Consequences

- The Stop hook only fires inside Claude Code sessions. Hand edits committed
  outside a session are not checked until pre-commit/CI is added.
- The hook checks the whole tree, so it depends on the baseline staying clean;
  it was cleaned once in a dedicated commit to make this hold.
