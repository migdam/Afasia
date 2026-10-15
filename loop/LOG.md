# Loop log

Newest entry first. One entry per iteration.

## Entry template

```
### <N>: <YYYY-MM-DD HH:MM UTC>: <backlog id> <short title>
- Baseline: <scripts/check.sh result before changes>
- Did: <what changed and where>
- Verified: <commands run + decisive output lines>
- Commit: <hash> (pushed: yes/no)
- Discovered: <new backlog items added, or "nothing">
- Next: <what the next iteration should pick>
- Protocol notes: <optional: suggested changes to loop/PROMPT.md>
```

---

### 3: 2026-10-15 04:44 UTC: P0-3 Every authenticated request returns 401
- **Baseline:** `check.sh` green (10 passed, smoke OK), same as entry 2. No human commits.
- **Did:**
  - `create_access_token(user_id)` now builds the claims itself, with a string `sub`.
  - Replaced python-jose with PyJWT 2.15.1. Decoding pins the algorithm and requires `exp` and `sub`.
  - `HTTPBearer(auto_error=False)`, so a missing token or non-Bearer scheme gets 401 with `WWW-Authenticate: Bearer`.
  - Simplified the two token calls in `auth.py`.
  - Added a `client` fixture (fresh database per test) and `test_auth.py` (11 tests).
- **Discovered and fixed here, because they blocked the acceptance test:**
  - **Every registration crashed.** pip resolves bcrypt 5.0.0 today, and passlib 1.7.4's first hash raises `ValueError: password cannot be longer than 72 bytes`. Pinned `bcrypt==4.3.0`. In a throwaway venv, 4.3.0 hashes and verifies, while 5.0.0 raises.
  - **Entry 0 was wrong** to call bcrypt 5 "not a blocker": its run had bcrypt 4.0.1 installed by an earlier step. Corrected in place.
  - **Harness gap:** `check.sh` reinstalled into the existing venv, so a removed package (python-jose) would have lingered and hidden a missing requirement. `check.sh` now owns `.venv-check` and rebuilds it when the requirements change. A developer's own `.venv` is never touched. Deleted the old `.venv` from entry 1.
  - The test `SECRET_KEY` was 15 bytes, which made PyJWT warn (`InsecureKeyLengthWarning`, RFC 7518). Lengthened it.
- **Verified:**
  ```
  old code, new token tests:  6 failed, 4 passed
      assert 401 == 200   (valid token, /users/profile)   ·   assert 403 == 401   (no header)
  now, freshly rebuilt venv:  "Requirements changed; rebuilding .venv-check" · real 0m42.6s
      ruff "All checks passed!" · pytest "21 passed, 24 warnings" · "README quick start: the backend answered /health"
      jose importable in .venv-check: False · bcrypt 4.3.0 · InsecureKeyLengthWarning count: 0
  ```
- **Commit:** d3988e9 (pushed: yes), plus this log/backlog commit.
- **Discovered (added to the backlog):**
  - P1-4 now describes the passlib/bcrypt problem correctly, including the 72-byte limit.
  - P1-5: a deactivated user's token keeps working until it expires, and a deleted user's token gets 404 instead of 401.
  - P1-8: refuse secret keys shorter than 32 bytes.
- **Next:** P0-4. Sessions never complete, so no points, progress or badges are ever saved. With the `client` fixture and working auth, it can be reproduced in tests.
- **Protocol notes:** verifying in a freshly built venv is what exposed the bcrypt crash. Suggest step 5 say so explicitly whenever requirements change.

### 2: 2026-10-15 04:33 UTC: P0-2 Backend can't start
- **Baseline:** `check.sh` green (2 passed, 2 xfailed), same as entry 1. No human commits.
- **Did:**
  - Settings:
    - `BACKEND_CORS_ORIGINS` stays a string; a `cors_origins` property gives the list.
    - `.env` is read from the repo root, where both READMEs and docker compose put it, whatever the working directory.
    - Unknown keys are ignored.
    - `ENV_FILE` overrides the location; the tests point it at a missing file so they stay hermetic.
  - Renamed the reserved `UserBadge.metadata` column, and the matching `BadgeResponse` field, to `details`.
  - Pinned `email-validator==2.3.0`.
  - Deleted the strict-xfail marker.
  - New tests: `test_config.py` (5) and `test_schemas.py` (1).
  - New `scripts/smoke.sh`: the README quick start in a scratch copy of the working tree, polling `/health`. `check.sh` runs it.
- **Verified:**
  ```
  check.sh: ruff "All checks passed!" · pytest "10 passed, 14 warnings in 1.17s"
            "README quick start: the backend answered /health" · real 0m18.5s (incl. installing email-validator)
  ```
  - On the previous commit, in a temporary worktree:
    - the new tests give `3 errors during collection` (`ValidationError: 1 validation error for Settings`);
    - `smoke.sh` gives `The backend exited while starting: ValidationError: 2 validation errors for Settings`.
- **Commit:** a22b9fb (pushed: yes), plus this log/backlog commit.
- **Discovered:**
  - The 14 warnings are 5 kinds of deprecation, now P3-10. passlib's dependency on `crypt` will break on Python 3.13.
  - `.env.template`'s `SMTP_*` keys "for notifications" are unused. Added to P0-9.
- **Next:** P0-3. Every authenticated request returns 401 (integer JWT `sub`). The harness can now reproduce it in a test.

### 1: 2026-10-15 04:23 UTC: P0-1 Verification harness
- **Baseline:** no `scripts/check.sh` yet, so P0-1 was the task by rule. No human commits since entry 0; no `loop/DONE`.
- **Did:**
  - Added `scripts/check.sh`. It creates or reuses `.venv`, reinstalls only when a requirements file changes, then runs ruff and pytest from `backend/`.
  - Added `backend/requirements-dev.txt`: pytest 9.1.1, ruff 0.17.0, httpx 0.27.2.
  - Added `backend/pyproject.toml`: strict xfail, strict markers, ruff limited to fatal rules (E9, F63, F7, F82).
  - Added `backend/tests/`: a conftest with a temp DB and upload dir, the smoke tests, and a guard that every requirement is pinned.
  - Updated `.gitignore`, plus one line in each README.
- **Deviations from the backlog text:**
  - The venv is at the repo root, not `backend/.venv`, so it can't end up in the backend Docker build context.
  - pytest-cov and pip-audit are not installed yet. They come with the iterations that make `check.sh` use them.
  - httpx must stay below 0.28: Starlette 0.27's `TestClient` calls `httpx.Client(app=...)` (`starlette/testclient.py:399-400`), which 0.28 removed.
- **Verified:**
  ```
  first run:  real 4m37s (venv + installs) · re-run: real 0m0.98s
  ruff:       All checks passed!
  pytest:     2 passed, 2 xfailed, 4 warnings in 0.63s
  XFAIL tests/test_smoke.py::test_app_imports - P0-2: backend crashes at import time
  ```
  - `--runxfail` shows the hidden error is the known one: `ValidationError ... BACKEND_CORS_ORIGINS Input should be a valid string`.
  - With iteration 0's three P0-2 patches applied in a scratch copy, both smoke tests report `[XPASS(strict)]` and pytest exits 1. So the fix iteration has to delete the marker.
- **Commit:** 7240b2b (pushed: yes), plus this log/backlog commit.
- **Discovered:** `.gitignore` ignores `.dockerignore`, so Docker build contexts can't exclude anything. Added to P0-8.
- **Next:** P0-2. Fix the three import crashes and the `.env` handling, then delete the `crashes_on_import` marker.
- **Protocol notes:** P0-1 allowed committing a red harness, but PROMPT.md step 5 says never commit red. I resolved it with strict xfails restricted (via `raises=`) to the known crash, so the build stays green, the bug stays visible, and the fix can't forget the marker. Suggest step 5 explicitly allow this for a known bug that a named backlog item will fix.

### 0: 2026-10-14: Loop set up (by hand, not by the loop)
- **Baseline:** no tests and no `scripts/check.sh` yet.
- **What I ran:** the backend in a scratch copy, outside the repo, with exactly the pinned `backend/requirements.txt` on Python 3.11.17. pip resolved bcrypt 5.0.0, passlib 1.7.4, pydantic 2.5.0, pydantic-settings 2.1.0, fastapi 0.104.1, starlette 0.27.0, python-jose 3.3.0 and sqlalchemy 2.0.23.

**Import, following the README** (`.env` in the repo root, server run from `backend/`):
```
SECRET_KEY: Field required
BACKEND_CORS_ORIGINS: Input should be a valid string [input_value=['http://localhost:3000', 'http://localhost:8000']]
```
- With `.env` in `backend/` instead, it also fails with `SMTP_*: Extra inputs are not permitted`.
- With only `SECRET_KEY` set, the CORS error remains: the validator runs on the default too.

**Patching each blocker in turn revealed the next one:**
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
ImportError: email-validator is not installed, run `pip install pydantic[email]`
IMPORT OK
```

**Auth flow, with the three import fixes:**
```
register: HTTP 201 · login: HTTP 200
GET /users/profile with app-issued token: HTTP 401 {"detail":"Could not validate credentials"}
generate_exercises(image_recognition) still spinning after 3 s: True
word_naming item as shipped: {'question': 'What is this? (cat)', 'answer': 'cat', ...}
```

**Scoring, with the JWT subject also patched to a string** (bcrypt pinned below 4.1 for this run ~~, though 5.0.0 also registered fine~~; wrong, see entry 3):
```
answer response includes correct_answer: False
is_correct stored: [True, True, True]
after 3 answers: completed_exercises=2 is_completed=False score=0.0 points=0 progress_records=0
after re-submitting 1 answer: completed_exercises=3 is_completed=True score=100.0 points=10 progress_records=1
after re-submitting again: points=20 progress_records=2
```

- **Not a blocker:** ~~bcrypt 5.0.0 with passlib 1.7.4. Registration works; passlib only prints a warning.~~ **Wrong, corrected in entry 3:** that run already had bcrypt 4.0.1 installed. With bcrypt 5.0.0, every registration crashes.
- **Did:** wrote `loop/PROMPT.md`, `loop/BACKLOG.md`, `loop/LOG.md`, `loop/README.md` and `loop/run.sh`. No app code changed.
- **Next:** P0-1, then P0-2.
