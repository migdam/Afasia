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

_tmp = tempfile.mkdtemp(prefix="afasia-tests-")
atexit.register(shutil.rmtree, _tmp, ignore_errors=True)

os.environ["ENV_FILE"] = os.path.join(_tmp, "absent.env")
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["UPLOAD_DIR"] = os.path.join(_tmp, "uploads")
