#!/usr/bin/env bash
# Build and start the Docker Compose stack under a throwaway project name,
# with its own secrets and ports, and check it through the frontend's nginx
# the way a browser would: the page loads, the API answers under /api, and
# signing up and logging in work (which needs the database), and an admin
# made with the CLI can use the admin API. Everything,
# volumes included, is removed afterwards. Needs a running Docker daemon.
#
#   scripts/docker-smoke.sh
#
# FRONTEND_PORT and BACKEND_PORT choose the host ports (default: free ones).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
free_port() { python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])'; }
frontend_port="${FRONTEND_PORT:-$(free_port)}"
backend_port="${BACKEND_PORT:-$(free_port)}"

work="$(mktemp -d)"
cat >"$work/.env" <<EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
POSTGRES_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
FRONTEND_PORT=$frontend_port
BACKEND_PORT=$backend_port
EOF
compose=(docker compose -p afasia-smoke --env-file "$work/.env" -f "$root/docker-compose.yml")
cleanup() {
  "${compose[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
  rm -rf "$work"
}
trap cleanup EXIT

echo "== Building and starting the stack"
if ! "${compose[@]}" up -d --build --wait --wait-timeout 180; then
  "${compose[@]}" logs --tail 40 >&2 || true
  exit 1
fi

echo "== Checking it through nginx on port $frontend_port"
if ! python3 -I - "$frontend_port" <<'EOF'; then
import json, sys, urllib.request, uuid

base = f"http://127.0.0.1:{sys.argv[1]}"

def call(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status, response.read()

status, page = call("GET", "/")
assert status == 200 and b"Aphasia" in page, "the app page did not load"
name = f"smoke{uuid.uuid4().hex[:8]}"
account = {"email": f"{name}@example.com", "username": name, "password": "correct horse battery"}
status, _ = call("POST", "/api/v1/auth/register", account)
assert status == 201, f"register: {status}"
status, body = call("POST", "/api/v1/auth/login", {"username": name, "password": account["password"]})
assert status == 200, f"login: {status}"
status, body = call("GET", "/api/v1/users/profile", token=json.loads(body)["access_token"])
assert status == 200 and json.loads(body)["username"] == name, f"profile: {status}"
print("page, /api, sign-up, login and profile all work through nginx")
EOF
  "${compose[@]}" logs --tail 40 >&2 || true
  exit 1
fi

echo "== Creating an admin with the CLI (README: Staff accounts)"
echo "a long smoke-test password" | "${compose[@]}" exec -T backend \
  python -m app.cli create-user --username smokeadmin --email smokeadmin@example.com --role admin --password-stdin
python3 -I - "$frontend_port" <<'EOF'
import json, sys, urllib.request

base = f"http://127.0.0.1:{sys.argv[1]}/api/v1"
login = urllib.request.Request(
    base + "/auth/login", method="POST", headers={"Content-Type": "application/json"},
    data=json.dumps({"username": "smokeadmin", "password": "a long smoke-test password"}).encode(),
)
token = json.load(urllib.request.urlopen(login, timeout=10))["access_token"]
stats = urllib.request.Request(base + "/admin/stats", headers={"Authorization": f"Bearer {token}"})
assert urllib.request.urlopen(stats, timeout=10).status == 200
print("the CLI-made admin can log in and use the admin API")
EOF
