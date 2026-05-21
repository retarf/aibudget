## Context

The backend exposes a REST API but there is no UI. This change adds the
frontend foundation: a Vite + React + Mantine single-page application living in
`frontend/`, delivering the application shell (left navigation, routing) and
light/dark theme support. Feature pages are out of scope and will plug into
this shell later.

## Goals / Non-Goals

**Goals:**

- A `frontend/` SPA built with Vite, the latest stable React (19), and Mantine.
- A Mantine `AppShell` layout with a persistent left navigation menu.
- Client-side routing between sections.
- Light/dark theme: OS-preference default, a visible toggle, persisted choice.
- A `frontend` Docker Compose service and a `./cli frontend` command group.
- Component tests with jest + msw.

**Non-Goals:**

- Budget / transaction / category feature pages.
- Authentication and reports.
- Production build/serving hardening (CDN, SSR, asset optimization).

## Decisions

- **Stack.** Vite + React 19 + **TypeScript** (Mantine's templates and typings
  assume TS; it is the modern default). Mantine v9 for components.
- **Theme.** `MantineProvider` with `defaultColorScheme="auto"` (follows the OS)
  and Mantine's `localStorageColorSchemeManager` for persistence. A
  `ColorSchemeScript` in `index.html` applies the stored scheme before first
  paint to avoid a flash. The toggle uses `useMantineColorScheme`.
- **Layout.** Mantine `AppShell` with a `navbar` region for the left menu and a
  `header` holding the app title and theme toggle. The navbar is collapsible on
  small screens.
- **Routing.** `react-router` (v7). The shell hosts an `<Outlet />`; a catch-all
  route renders the "not found" view inside the shell.
- **Testing.** jest + `@testing-library/react` + msw. msw mocks the REST API so
  component tests never hit a real backend. TypeScript is compiled for jest via
  `ts-jest`.
- **Compose.** The `frontend` service runs the Vite dev server in a Node
  container, port from `${FRONTEND_PORT}` (added to `.env.template`). It depends
  on `backend`. `node_modules` is kept in a container volume, not bind-mounted.
- **CLI.** A `./cli frontend` group mirroring `./cli backend`: at minimum a
  `test` command running jest in the Compose container.

## Risks / Trade-offs

- **TypeScript assumed.** Adds a compile step; chosen because Mantine is
  TS-first. Revisitable, but switching later is costly.
- **Theme flash.** Without `ColorSchemeScript`, a dark-mode user briefly sees a
  light flash on load. Mitigated by emitting the script in `index.html`.
- **jest + Vite friction.** Vite projects more commonly use Vitest; jest needs
  `ts-jest` and module-resolution config. Chosen to honor the stack named in
  `CLAUDE.md` (jest, msw).
- **Dev-server-only Compose service.** The `frontend` service runs the dev
  server, not a production build. Fine for development; a production image is
  a separate future concern.
