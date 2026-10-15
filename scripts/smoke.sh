#!/usr/bin/env bash
# Follow the README quick start in a scratch copy of the working tree and
# check that the backend starts and answers /health. Reuses the .venv that
# scripts/check.sh creates instead of reinstalling the requirements.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python="$root/.venv/bin/python"
if [[ ! -x "$python" ]]; then
  echo "No .venv yet; run scripts/check.sh first." >&2
  exit 1
fi

work="$(mktemp -d)"
pid=""
cleanup() {
  if [[ -n "$pid" ]]; then
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  fi
  rm -rf "$work"
}
trap cleanup EXIT

# Copy tracked and new files, but nothing ignored (.env, .venv, databases).
mkdir "$work/repo"
(cd "$root" && git ls-files -z --cached --others --exclude-standard |
  while IFS= read -r -d '' f; do
    if [[ -e "$f" ]]; then printf '%s\0' "$f"; fi
  done |
  tar --null -T - -cf -) | tar -C "$work/repo" -xf -

# The README steps: cd backend, cp ../.env.template ../.env, python -m app.main.
# HOST and PORT are overridden so this can't clash with a server you're running.
port="$("$python" -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')"
cd "$work/repo/backend"
cp ../.env.template ../.env
env -u ENV_FILE HOST=127.0.0.1 PORT="$port" "$python" -m app.main >"$work/server.log" 2>&1 &
pid=$!

probe='
import json, sys, urllib.request
with urllib.request.urlopen(f"http://127.0.0.1:{sys.argv[1]}/health", timeout=2) as r:
    sys.exit(0 if r.status == 200 and json.load(r)["status"] == "healthy" else 1)
'
for _ in $(seq 1 60); do
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "The backend exited while starting:" >&2
    cat "$work/server.log" >&2
    exit 1
  fi
  if "$python" -c "$probe" "$port" 2>/dev/null; then
    echo "README quick start: the backend answered /health"
    exit 0
  fi
  sleep 0.5
done
echo "The backend did not answer /health within 30 seconds:" >&2
cat "$work/server.log" >&2
exit 1
