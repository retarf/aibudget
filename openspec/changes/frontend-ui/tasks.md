## 1. Project setup

- [x] 1.1 Scaffold a Vite + React + TypeScript app in `frontend/`
- [x] 1.2 Add Mantine (core, hooks) and its peer dependencies
- [x] 1.3 Add `react-router` and configure the application routes
- [x] 1.4 Wrap the app in `MantineProvider` and emit `ColorSchemeScript` in `index.html`

## 2. Application shell (`app-shell`)

- [x] 2.1 Build the `AppShell` layout with a left `navbar` and a `header`
- [x] 2.2 Add the left navigation menu listing the app's sections
- [x] 2.3 Wire menu items to routes; navigate without a full reload and update the URL
- [x] 2.4 Mark the active section's menu item as active
- [x] 2.5 Add a catch-all route rendering a "not found" view inside the shell

## 3. Theme switching (`theme-switching`)

- [x] 3.1 Configure `defaultColorScheme="auto"` so the OS preference is the default
- [x] 3.2 Add a visible theme toggle in the header using `useMantineColorScheme`
- [x] 3.3 Persist the chosen theme via `localStorageColorSchemeManager`

## 4. Compose & CLI

- [x] 4.1 Add `FRONTEND_PORT` to `.env.template`
- [x] 4.2 Add a `frontend` service to `docker-compose.yml` (Node container, dev server, `depends_on: backend`)
- [x] 4.3 Add a `./cli frontend` command group with a `test` command running jest in the Compose container

## 5. Testing

- [x] 5.1 Set up jest + `@testing-library/react` + `ts-jest`
- [x] 5.2 Set up msw to mock the REST API in tests (scaffolded; activated when feature pages call the API)
- [x] 5.3 Test the app shell: layout renders, navigation switches sections, active item, unknown route
- [x] 5.4 Test theme switching: OS-preference default, toggle, persistence

## 6. Wrap-up

- [ ] 6.1 Run the frontend test suite and confirm all scenarios pass
- [x] 6.2 Update `README.md` with how to run the frontend via `./cli compose up`
- [ ] 6.3 Run `./cli openspec validate frontend-ui` and archive the change
