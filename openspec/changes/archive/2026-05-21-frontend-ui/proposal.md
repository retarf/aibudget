## Why

The aibudget backend now exposes a REST API, but there is no user interface.
Users need a web frontend to view and manage their budgets. This change
establishes the frontend foundation — the application shell — so feature pages
can be built on top of it.

## What Changes

- Add a `frontend/` directory containing a React single-page application built
  with **Vite**, using the latest stable React (React 19) and **Mantine** for
  UI components.
- Provide an application shell with a persistent **left-side navigation menu**
  and a content area, with client-side routing between sections.
- Support **light and dark themes** with a user-facing toggle; the theme
  defaults to the operating-system preference and the user's choice persists
  across visits.
- Add a `frontend` service to `docker-compose.yml` so `./cli compose up` starts
  the frontend alongside the backend and database.
- Add a `./cli frontend` command group for frontend developer tasks.
- Set up component testing with **jest** and **msw** (mocking the REST API).

## Capabilities

### New Capabilities

- `app-shell`: The application layout — a persistent left-side navigation menu
  and a routed content area that lets the user move between sections of the app.
- `theme-switching`: Light and dark theme support, including a visible toggle,
  an OS-preference default, and persistence of the user's choice.

### Modified Capabilities

<!-- None — there are no existing specs under openspec/specs/ yet. -->

## Impact

- **New code**: `frontend/` — a Vite + React + Mantine SPA (app shell,
  navigation, theme provider, routing).
- **Infrastructure**: A new `frontend` Docker Compose service; the frontend
  runs in a Node container.
- **Tooling**: A `./cli frontend` command group (mirroring `./cli backend`).
- **Dependencies**: Adds the frontend's own `package.json` (React, Mantine,
  the router, jest, msw); no change to the Python dependencies.
- **APIs**: The frontend will consume the existing REST API; no API changes.
- **Out of scope**: The actual budget / transaction / category feature pages,
  authentication, and reports — these are separate future changes. This change
  delivers only the shell they will plug into.
