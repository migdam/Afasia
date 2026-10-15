"""Shared test setup.

The app reads its settings when app.core.config is first imported, so the
environment is set here, before any test imports the app. Each test run gets
its own temporary database and upload directory, and ignores any .env a
developer keeps at the repository root.
"""
import atexit
import os
import shutil
import tempfile

import pytest

_tmp = tempfile.mkdtemp(prefix="afasia-tests-")
atexit.register(shutil.rmtree, _tmp, ignore_errors=True)

os.environ["ENV_FILE"] = os.path.join(_tmp, "absent.env")
# HS256 keys need at least 32 bytes (RFC 7518); PyJWT warns about shorter ones.
os.environ["SECRET_KEY"] = "test-secret-key-that-is-at-least-32-bytes"
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["UPLOAD_DIR"] = os.path.join(_tmp, "uploads")


@pytest.fixture
def client():
    """A test client for the app, on an empty database."""
    from fastapi.testclient import TestClient

    from app.core import login_limit
    from app.db.database import Base, engine
    from app.main import app

    login_limit.reset()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
