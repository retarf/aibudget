# aibudget

A home budget app — track incomes and expenses within budget periods, organize
them by category, and produce reports.

## Architecture

- **UI** — React, Mantine (tested with jest + msw)
- **REST API** — FastAPI
- **Microservices** — nats-py
- **Persistence** — SQLAlchemy

## Development setup

How to set up the full development environment.

### Prerequisites

| Tool | Purpose |
|------|---------|
| [pyenv](https://github.com/pyenv/pyenv) | Manage the Python version |
| [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) | Project-scoped virtualenv |
| [Docker](https://docs.docker.com/get-docker/) | Runs the openspec Node container |
| Python **3.14** | Built/managed via pyenv |

The Docker daemon must be running and your user must be able to run `docker`
without `sudo` (or adjust the commands accordingly).

### 1. Python environment

The project uses a **pyenv virtualenv named `aibudget`**. The `.python-version`
file in the repo root activates it automatically when you `cd` into the project.

```bash
# Install Python 3.14 (skip if already installed)
pyenv install 3.14

# Create the project virtualenv
pyenv virtualenv 3.14 aibudget
```

Once created, entering the project directory auto-selects the `aibudget`
environment. Verify:

```bash
cd /path/to/aibudget
python --version      # -> Python 3.14.x
pyenv version         # -> aibudget (set by .python-version)
```

### 2. Python dependencies

Dependencies are pinned in `requirements.txt` (compiled from `requirements.in`
with `pip-compile`).

```bash
pip install -r requirements.txt
```

This installs the API/microservice stack: `fastapi`, `sqlalchemy`, `nats-py`,
`httpx`, `pydantic`, `pytest`, and `click`.

To change dependencies, edit `requirements.in`, then recompile:

```bash
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

### 3. Developer CLI

Install the `cli` tool (the `aibudget_cli` package) in editable mode:

```bash
pip install -e .
```

This provides the `cli` command, invokable three equivalent ways:

```bash
cli --help                      # installed console script
./cli --help                    # executable script in the repo root
python -m aibudget_cli --help   # module form
```

`cli` only runs from within the project directory tree — it refuses to run
elsewhere.

### 4. openspec (via Docker)

openspec runs inside a Node container, so **no local Node install is needed** —
only Docker. On first use, openspec (`@fission-ai/openspec`) is installed into
`dev/openspec/node_modules/` on the host and reused on later runs.

```bash
cli openspec init                   # initialize openspec -> creates ./openspec/
cli openspec new change <name>      # create a new change proposal
cli openspec list                   # list changes (--specs for specs)
```

Every openspec subcommand is exposed as `cli openspec <command>`; run
`cli openspec --help` for the full list. Args and flags are forwarded
verbatim to openspec. The container pulls the `node:20-alpine` image
automatically on first run.

### 5. The stack (Docker Compose)

The frontend, backend, and PostgreSQL database all run as Docker Compose
services. First, create the `.env` file manually from the template:

```bash
cp .env.template .env       # then edit .env and set real credentials
```

Then manage the stack with the `cli compose` commands:

```bash
cli compose up -d                 # start frontend + backend + db
cli compose logs backend -f       # follow a service's logs
cli compose rebuild frontend      # rebuild and recreate after code changes
cli compose down                  # stop the stack
```

- Frontend (React + Mantine): `http://localhost:${FRONTEND_PORT}`
- API: `http://localhost:${BACKEND_PORT}` — `/health` and docs at `/docs`

Run the test suites inside their containers:

```bash
cli backend test                  # pytest in the backend container
cli frontend test                 # jest in the frontend container
```

### 6. Verify the setup

```bash
python --version            # Python 3.14.x
cli --help                  # CLI help is shown
docker run --rm hello-world # Docker works
pytest                      # test suite runs (backend tests)
```

## Notes

- `dev/openspec/node_modules/` is generated and git-ignored; the `package.json`
  there stays tracked.
- `aibudget_cli.egg-info/` is a build artifact of `pip install -e .` and is
  git-ignored.
