#!/usr/bin/env bash
# The project's single verification entry point. Exit code 0 means green.
#
#   scripts/check.sh
#
# Creates or reuses .venv-check at the repository root (rebuilt when the pinned
# backend requirements change), then runs the linter, the backend tests, the
# README quick start (scripts/smoke.sh) and the browser tests (e2e/).
# Set PYTHON to choose the interpreter (default: python3.11, else python3).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
backend="$root/backend"
# Owned by this script, so it can be deleted and rebuilt (a .venv of your own
# is left alone). Kept outside backend/, out of the Docker build context.
venv="$root/.venv-check"

python="${PYTHON:-}"
if [[ -z "$python" ]]; then
  python="$(command -v python3.11 || command -v python3 || true)"
fi
if [[ -z "$python" ]]; then
  echo "No python3 found; set PYTHON to a Python 3.11 interpreter." >&2
  exit 1
fi

# Rebuild from scratch when a requirements file changes, so a package that was
# removed from them can't linger and hide a missing requirement.
stamp="$venv/.requirements-stamp"
want="$(cat "$backend/requirements.txt" "$backend/requirements-dev.txt" | cksum)"
if [[ -d "$venv" && "$(cat "$stamp" 2>/dev/null)" != "$want" ]]; then
  echo "== Requirements changed; rebuilding .venv-check"
  rm -rf "$venv"
fi

if [[ ! -d "$venv" ]]; then
  echo "== Creating .venv-check with $("$python" --version)"
  "$python" -m venv "$venv"
  echo "== Installing backend requirements"
  "$venv/bin/python" -m pip install --quiet --disable-pip-version-check \
    -r "$backend/requirements.txt" -r "$backend/requirements-dev.txt"
  echo "$want" >"$stamp"
fi

cd "$backend"
echo "== Lint: ruff"
"$venv/bin/ruff" check . "$root/e2e"
echo "== Known vulnerabilities: pip-audit"
"$venv/bin/pip-audit" --requirement requirements.txt --progress-spinner off
echo "== Tests: pytest"
"$venv/bin/python" -m pytest
echo "== Smoke: README quick start"
"$root/scripts/smoke.sh"
echo "== End-to-end: Playwright"
# Environments that provide browsers set PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD;
# elsewhere, fetch the build this Playwright version needs (cached after once).
if [[ -z "${PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD:-}" ]]; then
  "$venv/bin/python" -m playwright install chromium
fi
"$venv/bin/python" -m pytest "$root/e2e"
echo "== All checks passed"
