#!/usr/bin/env bash
# Claude Code Stop hook: block turn completion until ruff lint + format pass.
#
# ruff exits 1 on violations, but a Stop hook must exit 2 for Claude Code to
# treat it as blocking and feed the output back for a fix. So we run both
# checks, collect their output, and remap any failure to exit 2.
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 2

lint_output=$(pyenv exec ruff check backend aibudget_cli 2>&1)
lint_status=$?
fmt_output=$(pyenv exec ruff format --check backend aibudget_cli 2>&1)
fmt_status=$?

if [ "$lint_status" -ne 0 ] || [ "$fmt_status" -ne 0 ]; then
  {
    echo "ruff found issues — fix them before finishing:"
    echo "$lint_output"
    echo "$fmt_output"
    echo "(formatting: run 'pyenv exec ruff format backend aibudget_cli')"
  } >&2
  exit 2
fi

exit 0
