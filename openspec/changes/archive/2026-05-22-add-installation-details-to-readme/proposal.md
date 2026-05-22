## Why

The README's "Development setup" section mixes prerequisites, dependency
management, tooling internals, and run instructions in a single flow, so a
newcomer cannot quickly see the minimal path to *install the app with the `cli`
tool and run it*. A focused, ordered install-and-run guide lowers the barrier
to getting the application started.

## What Changes

- Add a dedicated, numbered **Installation** section to `README.md` covering
  the end-to-end path: prerequisites → Python environment → install the `cli`
  tool → create `.env` from the template.
- Add a **Running the application** section showing how to start, inspect, and
  stop the stack with the `cli compose` commands, plus how to reach the
  frontend and API.
- Each step is explicit and copy-pasteable, with the expected outcome of each
  command stated.
- Reorganize the existing "Development setup" content so install/run guidance
  is not duplicated — development-only details (recompiling dependencies,
  openspec internals) stay separate from the core install/run path.

## Capabilities

### New Capabilities
- `project-documentation`: Covers the README's user-facing guidance for
  installing the application with the `cli` tool and running it.

### Modified Capabilities
<!-- None: no existing spec captures README documentation requirements. -->

## Impact

- `README.md` — restructured and expanded; no code changes.
- No changes to application behavior, APIs, or dependencies.
