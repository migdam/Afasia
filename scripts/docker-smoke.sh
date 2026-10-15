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
# Not a default, so the check below shows that .env settings reach the backend.
ACCESS_TOKEN_EXPIRE_MINUTES=17
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
import json, sys, urllib.error, urllib.request, uuid

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
login = json.loads(body)
assert login["expires_at"] - login["issued_at"] == 17 * 60, "ACCESS_TOKEN_EXPIRE_MINUTES from .env didn't reach the backend"
token = login["access_token"]
status, body = call("GET", "/api/v1/users/profile", token=token)
assert status == 200 and json.loads(body)["username"] == name, f"profile: {status}"
status, _ = call("POST", "/api/v1/auth/logout", token=token)
assert status == 204, f"logout: {status}"
try:
    call("GET", "/api/v1/users/profile", token=token)
    raise AssertionError("the token still works after logging out")
except urllib.error.HTTPError as error:
    assert error.code == 401, f"profile after logout: {error.code}"
print("page, /api, sign-up, login, profile and logout all work through nginx")

# Caching and headers (P1-7): files are revalidated, never kept for a year,
# every response has the security headers, and the privacy notice is there.
for path in ("/", "/js/app.js", "/css/styles.css", "/sw.js", "/privacy.html"):
    with urllib.request.urlopen(base + path, timeout=10) as response:
        headers, page = response.headers, response.read()
    assert headers["Cache-Control"] == "no-cache", f"{path}: Cache-Control {headers['Cache-Control']}"
    assert headers["X-Content-Type-Options"] == "nosniff", f"{path}: no security headers"
    policy = headers["Content-Security-Policy"] or ""
    assert "connect-src 'self';" in policy and "frame-ancestors 'none'" in policy, f"{path}: CSP {policy}"
assert b"Informacja o prywatno" in page, "privacy.html is missing from the image"
print("pages, scripts and styles are revalidated, with security headers; the privacy notice is served")

# Your data (P1-6c1), on PostgreSQL, which enforces the foreign keys that
# SQLite in the tests doesn't: export, then delete an account with a recording.
status, body = call("POST", "/api/v1/auth/login", {"username": name, "password": account["password"]})
token = json.loads(body)["access_token"]
call("PUT", "/api/v1/users/consents", {"recordings": True}, token=token)
status, body = call("POST", "/api/v1/therapy/sessions", {"title": "smoke", "exercise_type": "pronunciation",
                                                          "difficulty": "easy", "num_exercises": 1}, token=token)
session_id = json.loads(body)["id"]
status, body = call("GET", f"/api/v1/therapy/sessions/{session_id}/exercises", token=token)
exercise_id = json.loads(body)[0]["id"]
boundary = "smokeboundary"
upload = urllib.request.Request(
    f"{base}/api/v1/users/audio/upload?exercise_id={exercise_id}", method="POST",
    headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"},
    data=(f"--{boundary}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"r\"\r\n"
          f"Content-Type: audio/webm\r\n\r\n").encode() + b"\x1aE\xdf\xa3" + b"\0" * 64
         + f"\r\n--{boundary}--\r\n".encode(),
)
assert urllib.request.urlopen(upload, timeout=10).status == 200, "recording upload"
naming = json.loads(call("POST", "/api/v1/therapy/sessions", {"title": "smoke", "exercise_type": "word_naming",
                                                               "difficulty": "easy", "num_exercises": 1}, token=token)[1])
naming_exercise = json.loads(call("GET", f"/api/v1/therapy/sessions/{naming['id']}/exercises", token=token)[1])[0]
assert call("POST", f"/api/v1/therapy/exercises/{naming_exercise['id']}/hint", token=token)[0] == 200, "hint"
assert call("POST", f"/api/v1/therapy/exercises/{naming_exercise['id']}/choices", token=token)[0] == 200, "choices"
assert call("POST", f"/api/v1/therapy/exercises/{naming_exercise['id']}/tiles", token=token)[0] == 200, "tiles"
status, body = call("GET", "/api/v1/users/me/export", token=token)
assert status == 200 and len(json.loads(body)["recordings"]) == 1, "export"
status, _ = call("DELETE", "/api/v1/users/me", {"password": account["password"]}, token=token)
assert status == 204, f"delete: {status}"
try:
    call("POST", "/api/v1/auth/login", {"username": name, "password": account["password"]})
    raise AssertionError("the deleted account can still log in")
except urllib.error.HTTPError as error:
    assert error.code == 401, f"login after deletion: {error.code}"
print("export, and deleting an account with a recording, a hint, word choices and tiles, work on PostgreSQL")
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

echo "== Wrong passwords are counted per real client, and a forged X-Forwarded-For doesn't help"
python3 -I - "$frontend_port" <<'EOF'
import json, sys, urllib.error, urllib.request

base = f"http://127.0.0.1:{sys.argv[1]}/api/v1"

def login(password, forwarded_for):
    request = urllib.request.Request(
        base + "/auth/login", method="POST",
        headers={"Content-Type": "application/json", "X-Forwarded-For": forwarded_for},
        data=json.dumps({"username": "smokeadmin", "password": password}).encode(),
    )
    try:
        return urllib.request.urlopen(request, timeout=10).status
    except urllib.error.HTTPError as error:
        return error.code

statuses = [login("wrong password", f"203.0.113.{n}") for n in range(1, 6)]
assert statuses == [401] * 5, statuses
assert login("a long smoke-test password", "198.51.100.1") == 429, "a forged address got around the limit"
print("5 wrong passwords lock out the real client, whatever X-Forwarded-For says")
EOF
nginx_ip="$("${compose[@]}" exec -T frontend hostname -i | tr -d '[:space:]')"
last_login="$("${compose[@]}" logs backend | grep 'POST /api/v1/auth/login' | tail -1)"
echo "nginx is $nginx_ip; the backend logged: $last_login"
if [[ -z "$nginx_ip" || "$last_login" == *" $nginx_ip:"* ]]; then
  echo "The backend sees nginx's address instead of the client's." >&2
  exit 1
fi
