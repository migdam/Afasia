#!/usr/bin/env bash
# The project's single verification entry point. Exit code 0 means green.
#
#   scripts/check.sh
#
# Creates or reuses .venv at the repository root, installs the pinned backend
# requirements (only when they change), then runs the linter and the tests.
# Set PYTHON to choose the interpreter (default: python3.11, else python3).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
backend="$root/backend"
# Kept outside backend/ so it never ends up in the backend's Docker build context.
venv="$root/.venv"

python="${PYTHON:-}"
if [[ -z "$python" ]]; then
  python="$(command -v python3.11 || command -v python3 || true)"
fi
if [[ -z "$python" ]]; then
  echo "No python3 found; set PYTHON to a Python 3.11 interpreter." >&2
  exit 1
fi

if [[ ! -x "$venv/bin/python" ]]; then
  echo "== Creating .venv with $("$python" --version)"
  "$python" -m venv "$venv"
fi

# Reinstall only when a requirements file changes.
stamp="$venv/.requirements-stamp"
want="$(cat "$backend/requirements.txt" "$backend/requirements-dev.txt" | cksum)"
if [[ "$(cat "$stamp" 2>/dev/null)" != "$want" ]]; then
  echo "== Installing backend requirements"
  "$venv/bin/python" -m pip install --quiet --disable-pip-version-check \
    -r "$backend/requirements.txt" -r "$backend/requirements-dev.txt"
  echo "$want" >"$stamp"
fi

cd "$backend"
echo "== Lint: ruff"
"$venv/bin/ruff" check .
echo "== Tests: pytest"
"$venv/bin/python" -m pytest
echo "== All checks passed"
