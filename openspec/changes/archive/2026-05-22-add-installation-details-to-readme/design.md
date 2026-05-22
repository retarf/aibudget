## Context

`README.md` currently has one "Development setup" section that interleaves
prerequisites, the pyenv environment, dependency management, `cli` tool
internals, openspec tooling, Docker Compose, and a verification checklist. The
information needed to *install and run the app with the `cli` tool* is correct
but scattered, so a newcomer has to read past development-only material to find
the core path.

The `cli` tool (`aibudget_cli/main.py`) already exposes the relevant commands:
`cli openspec …`, `cli compose {up,down,logs,rebuild}`, and
`cli {backend,frontend} test`. The stack is defined in `docker-compose.yml`
(db, backend, frontend) and configured through a manually-created `.env` file
based on `.env.template`. This change is documentation-only.

## Goals / Non-Goals

**Goals:**
- A self-contained, numbered "Installation" section: prerequisites → Python
  environment → dependencies → `cli` tool → `.env`.
- A self-contained "Running the application" section using `cli compose`,
  including the frontend/API URLs and the stack lifecycle commands.
- Every step copy-pasteable, with the expected outcome stated.
- Development-only material (recompiling deps, openspec internals) kept
  separate from the install/run path, with no duplicated guidance.

**Non-Goals:**
- No changes to `cli`, the stack, dependencies, or any application behavior.
- No new tooling or installation method (no `pipx`, no published package).
- Not removing the existing development guidance — only reorganizing it.

## Decisions

- **Split "Development setup" into "Installation" + "Running the application"
  + "Development".** The install/run path becomes two focused top-level
  sections; recompiling dependencies and openspec tooling move under a
  "Development" section. Rationale: a reader's first goal is "install and run",
  which should not be gated behind contributor-only details. Alternative
  considered — a single expanded section — rejected because it keeps the
  scanning problem.
- **Keep the existing factual content; restructure rather than rewrite.** The
  current pyenv/`pip install -e .`/`cp .env.template .env`/`cli compose`
  commands are accurate and stay verbatim where possible. Rationale: minimize
  risk of documenting a command that does not work.
- **State the expected outcome under each step.** e.g. `pip install -e .` →
  "the `cli` command becomes available". Rationale: lets a reader confirm
  success without guessing.
- **Reference `cli openspec` from the Development section only.** openspec is a
  contributor tool, not part of installing or running the app, so it does not
  belong in the install path.

## Risks / Trade-offs

- [Reorganizing the README could drop a detail that only existed in the old
  flow.] → Migrate content section-by-section and diff against the original to
  confirm every command and note is preserved or intentionally moved.
- [Documented commands could drift from the actual `cli` interface.] → Verify
  each command against `aibudget_cli/main.py` and `docker-compose.yml` while
  editing.
- [A "Verify the setup" checklist exists today and could be lost.] → Keep it,
  attached to the end of the "Installation" section.
