"""End-to-end setup: the real backend and frontend, driven by headless Chromium.

The backend runs with a temporary database and the frontend is served as
static files, each on a free port, for the whole test run. Every test gets a
fresh browser context, and an uncaught JavaScript error fails the test.
"""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PASSWORD = "correct horse battery staple"
SECRET_KEY = "e2e-secret-key-that-is-at-least-32-bytes"


def call_api(servers, method, path, body=None, token=None):
    """Call the test backend directly; returns (status, JSON body)."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(servers["api"] + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start(command, cwd, env, log_path):
    log = open(log_path, "w")
    return subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT)


def wait_until_up(url, process, log_path, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError(f"{url} did not come up:\n{Path(log_path).read_text()[-2000:]}")


@pytest.fixture(scope="session")
def servers(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("e2e")
    api_port, web_port = free_port(), free_port()
    web_url = f"http://127.0.0.1:{web_port}"
    env = {
        **os.environ,
        "ENV_FILE": str(tmp / "absent.env"),
        "SECRET_KEY": SECRET_KEY,
        "DATABASE_URL": f"sqlite:///{tmp}/e2e.db",
        "UPLOAD_DIR": str(tmp / "uploads"),
        "BACKEND_CORS_ORIGINS": web_url,
    }
    api = start(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(api_port)],
        ROOT / "backend", env, tmp / "api.log",
    )
    web = start(
        [sys.executable, "-m", "http.server", str(web_port), "--bind", "127.0.0.1"],
        ROOT / "frontend", env, tmp / "web.log",
    )
    try:
        wait_until_up(f"http://127.0.0.1:{api_port}/health", api, tmp / "api.log")
        wait_until_up(web_url, web, tmp / "web.log")
        yield {"api": f"http://127.0.0.1:{api_port}/api/v1", "web": web_url, "db": tmp / "e2e.db"}
    finally:
        for process in (api, web):
            process.terminate()
            process.wait(timeout=10)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser, servers):
    # The service worker caches the app (being redesigned in backlog P1-7);
    # keep it out of the tests.
    context = browser.new_context(service_workers="block")
    context.add_init_script(f"window.API_BASE_URL = {json.dumps(servers['api'])};")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(servers["web"])
    yield page
    context.close()
    assert not errors, f"JavaScript errors: {errors}"


@pytest.fixture
def account(page):
    """Sign up a new user in the browser; returns the username."""
    username = f"pat{uuid.uuid4().hex[:8]}"
    page.click("#show-register")
    page.fill("#register-email", f"{username}@example.com")
    page.fill("#register-username", username)
    page.fill("#register-password", PASSWORD)
    page.click("#register-form-submit button[type=submit]")
    expect(page.locator("#dashboard-page")).to_be_visible()
    return username
