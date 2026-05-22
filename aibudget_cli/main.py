import os
import shutil
import subprocess
import sys
import tomllib

import click

# openspec is an npm package; we run it through a Node container so that
# contributors don't need Node installed locally.
OPENSPEC_IMAGE = "node:20-alpine"
OPENSPEC_PACKAGE = "@fission-ai/openspec"

# Host directory (relative to the project root) where the container's
# node_modules are persisted, so npm packages are installed once and reused
# across runs. Mounted into the container at /opt/openspec.
OPENSPEC_DEV_DIR = os.path.join("dev", "openspec")

# Marker used to recognize the aibudget project root (the `name` in its
# pyproject.toml). The cli refuses to run outside this project.
PROJECT_NAME = "aibudget-cli"


def _find_project_root():
    """Walk up from the cwd to find the aibudget project root, or None."""
    directory = os.getcwd()
    while True:
        pyproject = os.path.join(directory, "pyproject.toml")
        if os.path.isfile(pyproject):
            try:
                with open(pyproject, "rb") as fh:
                    data = tomllib.load(fh)
            except (OSError, tomllib.TOMLDecodeError):
                data = {}
            if data.get("project", {}).get("name") == PROJECT_NAME:
                return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            return None
        directory = parent


@click.group()
@click.pass_context
def cli(ctx):
    """aibudget developer CLI.

    Must be run from within the aibudget project directory.
    """
    root = _find_project_root()
    if root is None:
        raise click.ClickException(
            "cli must be run from within the aibudget project directory."
        )
    ctx.obj = {"project_root": root}


@cli.group()
def openspec():
    """Run openspec commands inside a Docker container.

    The container mounts the project root at /workspace, so generated
    files (the ./openspec directory) land in the project.
    """


# Subcommands of the openspec CLI, each exposed as `cli openspec <name>`.
# All args/flags after the name are forwarded verbatim to openspec.
OPENSPEC_COMMANDS = {
    "init": "Initialize OpenSpec in your project.",
    "update": "Update OpenSpec instruction files.",
    "list": "List changes (or specs with --specs).",
    "view": "Display an interactive dashboard of specs and changes.",
    "change": "Manage OpenSpec change proposals.",
    "archive": "Archive a completed change and update main specs.",
    "spec": "Manage and view OpenSpec specifications.",
    "config": "View and modify global OpenSpec configuration.",
    "schema": "Manage workflow schemas [experimental].",
    "schemas": "List available workflow schemas with descriptions.",
    "validate": "Validate changes and specs.",
    "show": "Show a change or spec.",
    "feedback": "Submit feedback about OpenSpec.",
    "completion": "Manage shell completions for the OpenSpec CLI.",
    "status": "Display artifact completion status for a change.",
    "instructions": "Output enriched instructions for an artifact.",
    "templates": "Show resolved template paths for artifacts.",
    "new": "Create new items, e.g. `new change <name>`.",
}


def _make_openspec_command(name, summary):
    """Build a `cli openspec <name>` command that forwards to openspec."""

    @click.command(
        name=name,
        # Let openspec's own flags (e.g. --specs, --description) pass through
        # instead of being parsed by click.
        context_settings={"ignore_unknown_options": True},
        help=(
            f"Run `openspec {name}` in the Node container.\n\n"
            f"{summary} Extra ARGS/flags are forwarded to openspec."
        ),
    )
    @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    @click.pass_context
    def _command(ctx, args):
        _run_openspec(ctx.obj["project_root"], name, *args)

    return _command


for _name, _summary in OPENSPEC_COMMANDS.items():
    openspec.add_command(_make_openspec_command(_name, _summary))


def _run_openspec(project_root, *args):
    """Run `openspec <args>` in a Node container mounted on the project root.

    The container's node_modules live in `dev/openspec/` on the host, so
    openspec is installed once and reused on later runs.
    """
    if shutil.which("docker") is None:
        raise click.ClickException("docker is not installed or not on PATH")

    # Persistent npm install location, mounted into the container.
    dev_dir = os.path.join(project_root, OPENSPEC_DEV_DIR)
    os.makedirs(dev_dir, exist_ok=True)

    # Install openspec into the mounted volume only if it isn't there yet,
    # then exec it. `"$@"` forwards the args passed after `sh` below.
    container_script = (
        "if [ ! -x /opt/openspec/node_modules/.bin/openspec ]; then "
        f"npm install --prefix /opt/openspec {OPENSPEC_PACKAGE}; fi; "
        'exec /opt/openspec/node_modules/.bin/openspec "$@"'
    )

    docker_cmd = [
        "docker", "run", "--rm", "-i",
        # Keep generated files owned by the invoking user, not root.
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-e", "HOME=/tmp",
        "-e", "npm_config_cache=/tmp/.npm",
        "-v", f"{project_root}:/workspace",
        "-v", f"{dev_dir}:/opt/openspec",
        "-w", "/workspace",
        OPENSPEC_IMAGE,
        "sh", "-c", container_script, "sh", *args,
    ]
    # Attach a TTY when running interactively so openspec prompts work.
    if sys.stdin.isatty():
        docker_cmd.insert(docker_cmd.index("-i") + 1, "-t")

    click.echo(f"$ {' '.join(docker_cmd)}")
    result = subprocess.run(docker_cmd)
    if result.returncode != 0:
        raise click.ClickException(
            f"openspec {' '.join(args)} failed (exit code {result.returncode})"
        )


@cli.group()
def compose():
    """Manage the project's Docker Compose stack.

    Runs `docker compose` against the docker-compose.yml in the project root.
    """


@compose.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def up(ctx, args):
    """Start the stack (`docker compose up`).

    Extra ARGS/flags are forwarded, e.g. `cli compose up -d`.
    """
    _run_compose(ctx.obj["project_root"], "up", *args)


@compose.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def down(ctx, args):
    """Stop and remove the stack (`docker compose down`)."""
    _run_compose(ctx.obj["project_root"], "down", *args)


@compose.command(context_settings={"ignore_unknown_options": True})
@click.argument("service")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def logs(ctx, service, args):
    """Show logs for SERVICE (`docker compose logs`).

    Extra ARGS/flags are forwarded, e.g. `cli compose logs backend -f`.
    """
    _run_compose(ctx.obj["project_root"], "logs", service, *args)


@compose.command()
@click.argument("service")
@click.pass_context
def rebuild(ctx, service):
    """Rebuild SERVICE's image and recreate its container."""
    _run_compose(ctx.obj["project_root"], "up", "-d", "--build", service)


def _run_compose(project_root, *args):
    """Run `docker compose <args>` from the project root."""
    if shutil.which("docker") is None:
        raise click.ClickException("docker is not installed or not on PATH")

    cmd = ["docker", "compose", *args]
    click.echo(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_root)
    if result.returncode != 0:
        raise click.ClickException(
            f"docker compose {' '.join(args)} failed (exit code {result.returncode})"
        )


# Maps a test target to its (compose service, pytest path). Each suite uses
# in-memory SQLite, so `--no-deps` skips starting databases and NATS.
TEST_TARGETS = {
    "budget": ("budget-service", "backend/services/budget/tests"),
    "category": ("category-service", "backend/services/category/tests"),
    "transaction": (
        "transaction-service",
        "backend/services/transaction/tests",
    ),
    "gateway": ("gateway", "backend/gateway/tests"),
}


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument(
    "target", type=click.Choice([*TEST_TARGETS, "all"]), default="all"
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def test(ctx, target, args):
    """Run service test suites inside their Docker Compose containers.

    TARGET selects a suite — budget, category, transaction, gateway — or `all`
    (the default). Extra ARGS/flags are forwarded to pytest, e.g.
    `cli test budget -k create`.
    """
    selected = (
        TEST_TARGETS if target == "all" else {target: TEST_TARGETS[target]}
    )
    for name, (service, path) in selected.items():
        click.echo(f"# {name} tests")
        _run_compose(
            ctx.obj["project_root"],
            "run", "--rm", "--no-deps", service,
            "python", "-m", "pytest", path, *args,
        )


@cli.group()
def frontend():
    """Manage the frontend service."""


@frontend.command(name="test", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def frontend_test(ctx, args):
    """Run the frontend test suite inside the Docker Compose container.

    Runs jest in a one-off `frontend` container. Extra ARGS/flags are
    forwarded to the test runner, e.g. `cli frontend test -t theme`.
    """
    _run_compose(
        ctx.obj["project_root"],
        "run", "--rm", "--no-deps", "frontend",
        "npm", "test", "--", *args,
    )


if __name__ == "__main__":
    cli()
