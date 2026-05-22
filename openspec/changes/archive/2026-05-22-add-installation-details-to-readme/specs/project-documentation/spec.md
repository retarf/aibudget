## ADDED Requirements

### Requirement: README provides an installation guide

The `README.md` SHALL contain a dedicated, numbered "Installation" section that
documents the complete path to install the application using the `cli` tool.
The section MUST cover, in order: prerequisites, setting up the Python
environment, installing Python dependencies, installing the `cli` tool, and
creating the `.env` file from `.env.template`. Each step MUST include a
copy-pasteable command and state the expected outcome.

#### Scenario: A new user follows the installation section

- **WHEN** a new user opens `README.md` and follows the "Installation" section
  from the first step to the last
- **THEN** the prerequisites, Python environment, dependencies, `cli` tool, and
  `.env` file are all in place, with no install step requiring information from
  outside that section

#### Scenario: Installation steps are explicit and ordered

- **WHEN** a reader scans the "Installation" section
- **THEN** each step is numbered, shows the exact command to run, and describes
  the expected result of running it

### Requirement: README provides a run guide for the `cli` tool

The `README.md` SHALL contain a dedicated "Running the application" section
that documents how to start, inspect, and stop the application stack using the
`cli compose` commands. The section MUST show how to start the stack, follow a
service's logs, rebuild a service, and stop the stack, and MUST state the URLs
at which the frontend and API are reachable.

#### Scenario: A user starts the application after installing

- **WHEN** a user who has completed the "Installation" section follows the
  "Running the application" section
- **THEN** they can start the stack with a `cli compose` command and open the
  frontend and API at the documented URLs

#### Scenario: Run section covers the stack lifecycle

- **WHEN** a reader needs to inspect or stop a running stack
- **THEN** the "Running the application" section documents the `cli compose`
  commands for following logs, rebuilding a service, and stopping the stack

### Requirement: Install and run guidance is not duplicated

The install and run guidance SHALL NOT be duplicated within `README.md`.
Development-only details (recompiling dependencies, openspec tooling internals)
MUST remain separate from the core install-and-run path.

#### Scenario: Reader finds a single source for each step

- **WHEN** a reader looks for how to install the `cli` tool or run the stack
- **THEN** the guidance appears in exactly one place, and development-only
  details are kept in a separate section
