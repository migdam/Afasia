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

### 22: 2026-10-15 09:50 UTC: P1-5a Login safety
- **Baseline:** `check.sh` green (102 backend, smoke, 15 e2e). No human commits.
- **Split:** P1-5 became P1-5a (per-request account check, login limit, minimum password length) and P1-5b (cookies or refresh tokens, idle timeout).
- **Test first:** `backend/tests/test_login_safety.py`, 4 tests. On the old code: 3 failed, 1 passed (`assert 200 == 429`; a deactivated user's token still got 200).
- **Did:**
  - `get_current_user_id` looks up the user's `is_active` on each request; a missing or inactive account gets 401.
  - `app/core/login_limit.py`: 5 failures per username (case-insensitive) in 15 minutes → 429 "Too many failed attempts" with `Retry-After`. Success clears the record. In memory, per process; reset in the test fixture.
  - `UserCreate` passwords need 8+ characters; the sign-up field has `minlength="8"`.
  - READMEs' Known limitations and the user guides (EN/PL) updated, with a new troubleshooting row.
- **Verified:** `scripts/check.sh` exit code 0: ruff, pip-audit clean, 110 backend tests, smoke, 15 e2e.
- **Commit:** 73b9ee7 (pushed: yes)
- **Discovered:**
  - The frontend shows a 422's `detail` list as text, so a too-short password from an old client reads badly. The form's `minlength` covers the normal case. Folded into P2 error-message work when it comes up.
  - The limit is per username, so an attacker can lock someone out for 15 minutes. That is accepted for now and noted in P1-5b's scope for review.
- **Next:** P1-5b if it fits one iteration, otherwise P1-6.

### 21: 2026-10-15 09:05 UTC: P1-4 Dependency health
- **Baseline:** `check.sh` green (102 backend, smoke, 15 e2e). No human commits.
- **Audit of the old pins** (pip-audit in a scratch venv): 67 known vulnerabilities.
  - pillow 31, python-multipart 16, starlette 14, python-dotenv 2, anyio 2, fastapi 1.
  - matplotlib, pillow and aiofiles aren't imported anywhere.
- **Did:**
  - Upgraded fastapi 0.143.1 (starlette 1.x), uvicorn 0.54.0, pydantic 2.14.1, pydantic-settings 2.16.0, python-multipart 0.0.32, python-dotenv 1.2.4, structlog 26.1.0 and reportlab 5.0.1.
  - Moved SQLAlchemy to 2.0.54. 2.1 is left for its own migration.
  - Dropped the three unused packages.
  - Replaced passlib with bcrypt 5. Passwords over 72 bytes are refused at sign-up and in the CLI, and never verify.
  - Replaced `on_event` with a lifespan handler.
  - Lifted the httpx pin to 0.28.1.
  - Added `pip-audit` to `check.sh`.
- **Found:** with the new FastAPI, `test_authorization.py`'s route list from `app.routes` came out empty, so 26 checks silently became 2 skips. Fixed:
  - the list now comes from the OpenAPI schema;
  - a test requires at least 20 routes;
  - `empty_parameter_set_mark = fail_at_collect` is set in both pytest configs.
- **Verified:**
  ```
  old code: "assert 201 == 422" (a 74-byte password accepted, silently cut to 72)
  now:      "No known vulnerabilities found" · backend "106 passed" (none skipped; warnings 70 -> 11) · smoke OK · e2e "15 passed"
            docker-smoke on the new stack: all three checks pass
  ```
- **Docs:** removed "outdated dependencies" from both READMEs, and listed the pip-audit check under Development.
- **Commit:** c625e62 (pushed: yes), plus this log/docs commit.
- **Protocol notes:** after any dependency upgrade, compare the test count with the previous run. A drop or new skips means tests stopped running.
- **Next:** P1-5, login sessions.

### 20: 2026-10-15 08:40 UTC: P1-3a Staff accounts and authorization tests
- **Baseline:** `check.sh` green (71 backend, smoke, 15 e2e). No human commits.
- **Split:** P1-3 became P1-3a (done here) and P1-3b. P1-3b needs product decisions (H7): how therapists and patients get linked, and how the patient consents.
- **Did:**
  - `app/cli.py`: `create-user` (role, password from a prompt or stdin, at least 12 characters, duplicates refused) and `set-role`.
  - New "Staff accounts" section in both READMEs, including the Docker form; both guides point to it.
  - `docker-smoke.sh` now also creates an admin with the CLI and uses it.
  - Tests: `test_cli.py` (3) and `test_authorization.py` (28). The routes are enumerated from the app, so a new route without a login check fails automatically.
- **Verified:**
  ```
  old code: test_cli — ImportError: cannot import name 'cli' · test_authorization: 28 passed (it guards what already works)
  now:      check.sh backend "102 passed" · smoke OK · e2e "15 passed" (exit code checked directly)
            docker-smoke: "Created admin smokeadmin." · "the CLI-made admin can log in and use the admin API" · 0 containers left
  ```
- **Slip:** the first attempt to extend `docker-smoke.sh` nested an `EOF` heredoc inside another, so the outer one ended early. Nothing was changed; I redid it with the Edit tool plus a heredoc under a different delimiter. Lesson, as a protocol note: never nest heredocs that share a delimiter.
- **Commit:** 719dca3 (pushed: yes), plus this log/backlog commit.
- **Discovered:** nothing new.
- **Next:** P1-3b needs H7's decisions, so take P1-4 (dependency health) first. Then P1-5 onwards.

### 19: 2026-10-15 08:20 UTC: P1-2 Private voice recordings
- **Baseline:** `check.sh` green (67 backend, smoke, 15 e2e). No human commits.
- **Did:**
  - Removed the public `/uploads` mount.
  - The upload now:
    - checks the exercise belongs to the uploader (404);
    - accepts audio content types only (415);
    - reads at most `MAX_UPLOAD_SIZE + 1` bytes (413) and refuses empty files (400);
    - stores files under `UPLOAD_DIR/audio` with a random name and the real extension.
  - `GET /users/audio/{id}` sends the real content type.
  - The upload response no longer includes `file_path`.
  - Frontend: recordings keep the browser's real format, and the unused form field is gone.
  - Added `test_recordings.py` (4 tests).
- **Worse than reported:** uploads ignored `UPLOAD_DIR`, writing under the working directory. Running the new tests on the old code left 4 `.wav` files in `backend/uploads/audio` (gitignored, since deleted).
- **Verified:**
  ```
  old code: 4 failed ('file_path' in the response · file not under UPLOAD_DIR · "assert 200 == 413" · "assert 200 == 404" for someone else's exercise)
  now:      test_recordings 2 runs "4 passed" · check.sh backend "71 passed" · smoke OK · e2e "15 passed" (exit code checked directly)
  ```
- **Docs:** removed P1-2 from Known limitations in both READMEs.
- **Commit:** 99716d3 (pushed: yes), plus this log/docs commit.
- **Discovered:** nothing new. Recordings are still kept forever and uploaded without a consent step; both are already in P1-6.
- **Next:** P1-3, the therapist/admin model.

### 18: 2026-10-15 08:05 UTC: P1-1 No user input as HTML; CSP
- **Baseline:** `check.sh` green (65 backend, smoke, 13 e2e). No human commits.
- **Did:**
  - Replaced every `innerHTML` and inline `onclick` in `ui.js` (recent and scheduled sessions, badges, empty states) and `app.js` (options, record button) with DOM methods. Two helpers, `el()` and `showEmpty()`, put all text in via `textContent`.
  - Moved the inline service-worker script into `js/sw-register.js`.
  - Added a CSP `<meta>`: `script-src 'self'` and `object-src 'none'`. `connect-src` stays broad because in development the API is on another port.
  - Tests:
    - `test_frontend_safety.py`, a guard against `innerHTML`, `insertAdjacentHTML`, inline handlers and inline `<script>`.
    - `e2e/test_untrusted_text.py`: titles containing `<b>`/`<img onerror>` are shown as text, and the policy forbids inline scripts.
- **Verified:**
  ```
  old code: guard found 10 places plus the inline <script> · e2e "Expected '<b>bold</b><img …>' · Actual value: bold" (markup rendered)
  now:      backend "67 passed" · smoke OK · e2e "15 passed" (every flow runs under the CSP) · exit code checked directly
  ```
- **Docs:** removed P1-1 from Known limitations in both READMEs.
- **Slip:** two heredocs in one shell command were in the wrong order, so the commit got the bookkeeping script as its message. It was amended before pushing (now 64ae795).
- **Commit:** 64ae795 (pushed: yes), plus this log/docs commit.
- **Discovered:** nothing new.
- **Next:** P1-2, recordings served without authentication.

### 17: 2026-10-15 07:50 UTC: P1-10 Simultaneous answers
- **Baseline:** `check.sh` green (63 backend, smoke, 13 e2e). No human commits.
- **Did:**
  - The answer is claimed with `UPDATE … WHERE is_correct IS NULL` (no row changed: 409) and committed.
  - The answered exercises are then counted from the database.
  - Completion is claimed with `UPDATE … WHERE is_completed = false`, and only the winner runs `finish_session`.
  - `completed_exercises` is only ever raised.
  - Points are added as `total_points + n` in SQL.
  - Added `test_concurrency.py`: 2 tests, 10 trials each, using a thread barrier.
- **New finding, fixed by the same change:** two different last answers sent at once left the session unfinished for good. Each request counted only its own answer in memory.
- **Verified:**
  ```
  old code: "assert [200, 200] == [200, 409]" · "assert (False, 1, 0.0) == (True, 2, 100)"
  now:      SQLite, 5 repeated runs: "2 passed" each
            PostgreSQL 15 (throwaway container, scratch copy of the tests pointed at it), 3 runs: "10 passed" each
            check.sh: backend "65 passed" · smoke OK · e2e "13 passed" (exit code checked directly)
  ```
- **Docs:** removed the P1-10 line from Known limitations in both READMEs.
- **Commit:** 945b598 (pushed: yes), plus this log/docs commit.
- **Discovered:** the streak update in `finish_session` is still read-modify-write. Two sessions of the same user finishing in the same instant could miscount the streak by one. That's low impact; noted for P2-9, which redesigns streaks.
- **Next:** P1-1, rendering user data without `innerHTML`.

### 16: 2026-10-15 07:35 UTC: P0-9b User guides (all P0 items done)
- **Baseline:** `check.sh` green (61 backend, smoke, 13 e2e). No human commits.
- **Did:**
  - Rewrote `docs/USER_GUIDE.md` and `docs/USER_GUIDE.pl.md` from the actual screens, labels (the Polish labels from `i18n.js`) and behaviour.
  - Every specific was checked against the code: the last five sessions, the confirmation on exit, case-sensitive usernames, the export contents, the admin page, and UTC streak days.
  - The guides say where the Polish UI still shows English (P2-10).
  - Removed `SMTP_*` from `.env.template`.
  - `test_docs.py` now checks the guides for false claims, including `API.md`, `DEPLOYMENT.md` and the pricing placeholder.
- **Verified:**
  ```
  old guides: claim test failed (support address, API.md, DEPLOYMENT.md, pricing placeholder; PL: pricing placeholder)
  now:        backend "63 passed" · README smoke OK · e2e "13 passed" (exit code checked directly)
  ```
- **Commit:** 1276117 (pushed: yes), plus this log/backlog commit.
- **Gates:** G11 is now 🟢. All P0 items are done.
- **Discovered:** nothing new.
- **Next:** the P1 list, top to bottom, starting with P1-10 (simultaneous answers are all accepted).

### 15: 2026-10-15 07:20 UTC: P0-9a READMEs describe only what exists
- **Baseline:** `check.sh` green (51 backend, smoke, 13 e2e). No human commits.
- **Split:** P0-9 covers about 3,600 lines of docs, so it became P0-9a (READMEs, done here) and P0-9b (user guides and `.env.template`).
- **Did:**
  - Rewrote `README.md` and `README.pl.md` (the Polish written natively) from what the tests and iterations 1–14 verified.
  - The new READMEs include:
    - an early-development, not-for-clinical-use status;
    - what works, with the untested parts marked;
    - what doesn't work;
    - the quick start, which `smoke.sh` still checks;
    - Docker;
    - a settings table and an API overview;
    - Known limitations, each linked to its backlog item;
    - "no license chosen yet".
  - Deleted `README_IMPLEMENTATION.md`.
  - New `test_docs.py`: all relative links resolve, and the READMEs contain no known-false claims.
- **Verified:**
  ```
  old docs: 4 failed — LICENSE link missing (both READMEs); README.md 9 false claims, README.pl.md 6
  now:      backend "61 passed" · README smoke OK · e2e "13 passed" (exit code checked directly)
  ```
- **Slip:** the first commit message said "66 backend tests". I corrected it to 61 with `--amend` before pushing.
- **Commit:** f056514 (pushed: yes), plus this log/backlog commit.
- **Discovered:** nothing new.
- **Next:** P0-9b, the user guides.

### 14: 2026-10-15 07:05 UTC: P0-8 Docker stack
- **Baseline:** `check.sh` green (51 backend, smoke, 13 e2e). No human commits.
- **Environment:**
  - No Docker daemon was running. I started `dockerd`, which works as root here and is still running in this container.
  - Docker Hub returned 429 for `postgres:15-alpine` once; a retry worked.
  - pip inside the image build failed with `CERTIFICATE_VERIFY_FAILED`: this sandbox inspects TLS with its own certificate authority. Added an optional `pip_ca` build secret (`PIP_CA_FILE`), which is generic for corporate proxies and never ends up in the image.
- **Did:**
  - `docker-compose.yml`: secrets required from `.env`; health checks with `depends_on: service_healthy`; named volumes and no source mounts; no `container_name`; configurable ports.
  - nginx proxies `^~ /api/`.
  - `frontend/js/config.js` holds the API base URL (dev default `localhost:8000`; the Docker image writes `/api/v1`).
  - The frontend image copies only app files.
  - Added `.dockerignore` files and stopped gitignoring them.
  - Added `psycopg2-binary==2.9.13`.
  - Updated `.env.template` and both READMEs.
  - New `scripts/docker-smoke.sh`. It's not in `check.sh`, because it needs Docker.
- **Verified:**
  ```
  old stack: smoke "HTTP Error 405: Not Allowed" (no /api route) · backend image: "No module named 'psycopg2'"
  new stack: db, backend and frontend Healthy · "page, /api, sign-up, login and profile all work through nginx" · 0 containers left
             compose without secrets: "required variable POSTGRES_PASSWORD is missing a value: Set POSTGRES_PASSWORD in .env"
             frontend image serves only 50x.html, css, index.html, js, manifest.json, sw.js
  check.sh:  backend "51 passed" · smoke OK · e2e "13 passed" (exit code checked directly)
  ```
- **Commit:** e0671a1 (pushed: yes), plus this log/backlog commit.
- **Discovered:** nothing new. `DEBUG` is still `"true"` in Compose (P1-8).
- **Next:** P0-9, honest docs.

### 13: 2026-10-15 06:40 UTC: P0-7g The whole flow in EN and PL (P0-7 done)
- **Baseline:** `check.sh` green (51 backend, smoke, 11 e2e). No human commits.
- **Did:** added `e2e/test_full_flow.py`, parametrized over EN and PL. Each run signs up, switches language, then does:
  - a word-naming session with typed answers, one of them wrong (80%);
  - a sentence-completion session, all correct (100%).

  It checks each feedback message in that language, both scores on the dashboard, and 2 sessions at 90% average accuracy on the progress page.
- **Not covered:** pronunciation. It needs a microphone and speech recognition, and recordings are always scored wrong today (P2-7).
- **Verified:**
  ```
  before the P0-7 fixes (5ff957e, temporary worktree): 2 failed —
      "Actual value: Incorrect. Try again! Correct! Well done!: undefined"
      "Actual value: Niepoprawnie. Spróbuj ponownie! Poprawnie! Świetna robota!: undefined"
  now: backend "51 passed" · smoke OK · e2e "13 passed in 107.72s" (exit code checked directly)
  ```
- **Commit:** cd5bbf7 (pushed: yes), plus this log/backlog commit.
- **Discovered:** nothing new. The "Session complete! Score: …" alert is still English in Polish mode (already listed in P2-10). The e2e suite now takes about 1:50, and `check.sh` about 2:30 in total.
- **Next:** P0-8, the Docker stack.

### 12: 2026-10-15 06:30 UTC: P0-7f Progress chart
- **Baseline:** `check.sh` green (51 backend, smoke, 10 e2e). No human commits.
- **Did:**
  - `chart.js`: the line is one path, with the dots drawn after it. The old code called `beginPath()` per dot, so only the last dot was stroked.
  - Colours come from the theme's CSS variables.
  - The canvas is 300 px high via CSS; it had been the 150 px default.
  - `ui.js` draws "No data available" for an empty history.
  - New `e2e/test_progress.py`: two perfect sessions created through the API, dark theme, then pixel checks.
- **Verified:**
  ```
  old code: "assert 150 >= 250" · with only the height fixed: midpoint "[0, 0, 0, 0]" (no line)
  now:      backend "51 passed" · smoke OK · e2e "11 passed in 42.54s" (exit code checked directly)
  ```
- **Commit:** 190fc25 (pushed: yes), plus this log/backlog commit.
- **Discovered:** nothing new. The y-axis scales to the highest value rather than 0–100%; that belongs with P2-11, the accessible chart.
- **Next:** P0-7g, the whole flow in EN and PL.

### 11: 2026-10-15 06:20 UTC: P0-7e Unavailable content
- **Baseline:** `check.sh` green (49 backend, smoke, 8 e2e). No human commits.
- **Did:**
  - Removed the 15 `image`/`audio` references from `EXERCISE_DATA`. `frontend/assets` doesn't exist, so every one was broken.
  - Removed the Image Recognition options from both menus.
  - Marked "Play Audio" as not available yet in both user guides.
  - Tests:
    - Content test: every referenced asset must exist under `frontend/`.
    - 2 e2e tests: the menus offer only types with content, and starting exercises loads no missing files.
- **Verified:**
  ```
  old code: asset test "2 failed" · menu test listed 'image_recognition' · "#exercise-image … Actual value: visible"
  now:      ruff clean · backend "51 passed" · smoke OK · e2e "10 passed in 41.47s" (exit code checked directly)
  ```
- **Caught by the checks:** my first version of the missing-files test had no dialog handler, so the exit confirmation was dismissed and the test timed out. I added one. Nothing was committed while red.
- **Commit:** ad4204c (pushed: yes), plus this log/backlog commit.
- **Discovered:** nothing new.
- **Next:** P0-7f, the progress chart.

### 10b: 2026-10-15 06:06 UTC: Flaky admin e2e test (regression fix)
- **What happened:** the `check.sh` run before entry 10's bookkeeping commit (4e5e82c) had `1 failed, 7 passed` in e2e. My command piped `check.sh` through `grep` and chained `&& git commit`, and `grep`'s exit status hid the failure, so 4e5e82c was committed and pushed while `check.sh` was red. That commit changed only `loop/` files, and its code was identical to 19bb94f, which had passed 8/8. That made it an intermittent failure, not a code change.
- **Cause:** in `test_an_admin_sees_patients_as_text_and_can_deactivate_them`, which failed in about 1 of 7 full-suite runs with `KeyError: 'detail'`, the patient's login succeeded. Playwright matches role names by case-insensitive substring, so the wait for the "Activate" button matched the old "Deactivate" button and passed at once. The test's direct login then raced the browser's deactivate request (CORS preflight plus PUT).
- **Proof:** before any click, `name="Activate"` matched 1 button, with text "Deactivate"; with `exact=True` it matched 0. A first attempt to force the race by delaying the request proved nothing: a blocking sleep in a sync route handler serializes the requests.
- **Fix:** `exact=True` on both button lookups (a08eb9d).
- **Verified:** the full e2e suite passed 10 runs in a row. A worker restart killed the first batch partway, so the runs were split 4+6. `check.sh` green, with its exit code checked directly.
- **Protocol notes:**
  - Never pipe `check.sh` into another command before deciding to commit. Capture it (`scripts/check.sh > log; rc=$?`) and commit only if `rc` is 0.
  - In Playwright tests, use `exact=True` whenever one name is a substring of another.

### 10: 2026-10-15 05:45 UTC: P0-7d Dashboard and admin data
- **Baseline:** `check.sh` green (48 backend, smoke, 6 e2e), same as entry 9. No human commits.
- **Did:**
  - Added `AdminUserResponse` (`UserResponse` plus `is_active`) for `GET /admin/users`.
  - The admin list is now built with DOM methods (`textContent`, `addEventListener`), not `innerHTML` with an inline `onclick`.
  - `showDashboard()` loads the badge count, and hides the admin menu for non-staff users.
  - Tests:
    - Backend: `test_admin.py`.
    - e2e: `test_admin.py` (2 tests), plus a badge assertion in the full-session test.
    - e2e `conftest.py`: `call_api()` and the database path.
  - There is no way to create an admin yet (P1-3), so the tests set the role in the database. SQLAlchemy stores enum names, so the role is `'ADMIN'`.
- **Worse than reported:** without `is_active`, every patient was offered "Activate", and clicking it re-activated an active user, so no admin could ever deactivate anyone.
- **Found and fixed:** the admin menu stayed visible for the next person to log in on the same page after an admin logged out. The API still refused them with 403.
- **Verified:**
  ```
  old code: backend KeyError: 'is_active'
            e2e "Expected '<b>pat2be989</b>' · Actual value: pat2be989" (the markup was rendered)
            badge count "Actual value: 0"
            admin menu "expected to be hidden · Actual value: visible"
  now:      ruff "All checks passed!" · backend "49 passed" · smoke OK · e2e "8 passed in 37.74s" · node --check OK
  ```
- **Commit:** 19bb94f (pushed: yes), plus this log/backlog commit.
- **Discovered:** nothing new. P1-1 now records what's done and lists the `innerHTML` and `onclick` uses still left.
- **Next:** P0-7e. Hide Image Recognition from the dropdowns, and stop showing broken images and audio.

### 9: 2026-10-15 05:35 UTC: P0-7c Exercise state
- **Baseline:** `check.sh` green (48 backend, smoke, 3 e2e), same as entry 8. No human commits.
- **Did** (all in `frontend/js/app.js`):
  - Submit is disabled from the first click until the next exercise is shown. It is re-enabled when there's no answer yet or the request fails.
  - The answer is read from the input the exercise shows (option, recording or text box), never from a hidden input.
  - Each exercise starts with an empty text box and no recording.
  - `exitExercise()` cancels the pending move to the next exercise.
  - Added 3 e2e tests and shared helpers in `e2e/test_sessions.py`.
- **Verified:**
  ```
  old code: double click -> "Expected '2/5' · Actual value: 3/5" (both submissions accepted, an exercise skipped)
            stale typed answer -> no "Please provide an answer"; the earlier word was submitted
            leaving during feedback -> next session "Expected '1/5' · Actual value: 2/5"
  now:      ruff "All checks passed!" · backend "48 passed" · smoke OK · e2e "6 passed in 34.11s"
            e2e repeated 3 times: "6 passed" each time (the double-click and timing tests are stable)
  ```
- **Commit:** 1f7fdce (pushed: yes), plus this log/backlog commit.
- **Discovered (added to the backlog):**
  - **P1-10, at the top of P1:** the server accepts simultaneous answers. The double click got past P0-4's 409 because both requests raced the check. A probe confirmed it: both answers accepted in 20/20 trials, and 20 sessions produced 40 progress records. P0-4's ticked line now says so.
  - **P1-6 (code reading):** the microphone stream is never released after the first recording, and leaving mid-recording keeps it recording.
  - The recording reset has no e2e test, because headless Chromium has no microphone (P2-7 redesigns speech practice).
- **Next:** P0-7d. The admin list's `is_active`, and the dashboard badge count.

### 8: 2026-10-15 05:25 UTC: P0-7b Session result and feedback
- **Baseline:** `check.sh` green (47 backend, smoke, 2 e2e), same as entry 7. No human commits.
- **Did:**
  - New `AnswerResult` response for `POST /exercises/{id}/answer`, which adds `correct_answer`. The exercise list still leaves it out, so nobody can peek.
  - Wrong-answer feedback is now one calm message with the answer in bold, set with `textContent` and a `<strong>` element rather than HTML. EN "Not quite. Correct answer: …", PL "Nie tym razem. Prawidłowa odpowiedź: …".
  - "Try again!" is gone, since there is no retry.
  - The final alert uses the score from the server's `/complete` response. The client no longer sends a score or duration, and the dead `sessionStartTime` is removed.
  - Updated both user guides' feedback sections.
  - Tests:
    - New `e2e/test_sessions.py`: 5 exercises, the first answered wrongly.
    - New backend test: the right answer is revealed only once the exercise is answered.
    - New `account` fixture in `e2e/conftest.py`.
- **Verified:**
  ```
  old code: e2e "Expected 'Not quite. Correct answer: blue' · Actual value: Incorrect. Try again! Correct! Well done!: undefined"
            backend: KeyError: 'correct_answer'
  now:      ruff "All checks passed!" · backend "48 passed" · smoke OK · e2e "3 passed in 22.13s" · node --check OK for all JS
  ```
- **Commit:** 6a0c8b4 (pushed: yes), plus this log/backlog commit.
- **Discovered:** nothing new. The session e2e test takes about 12 s because the app waits 2 s before each next exercise; P2-4 removes that wait. The e2e test copies the three easy sentence-completion answers from `therapy.py`, so update it when P2-2 changes the content.
- **Next:** P0-7c. Disable Submit while feedback shows, and reset the answer and recording between exercises.

### 7: 2026-10-15 05:18 UTC: P0-7a E2E harness (P0-7 split into a–g)
- **Baseline:** `check.sh` green (47 passed, smoke OK), same as entry 6. No human commits.
- **Split:** P0-7 is too big for one iteration and every part needs browser tests, so it became P0-7a–g. The harness (a) comes first. Each existing bullet moved to the sub-item that will fix it, and the API-address bullet moved to P0-8.
- **Feasibility:**
  - This environment blocks Playwright's browser download (`cdn.playwright.dev` returns 403: "no rule or allowlist entry allows host").
  - It does provide Chromium build 1194 in `/opt/pw-browsers` and sets `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD`.
  - Reading `browsers.json` from the 1.55–1.57 wheels showed that 1.56.0 is the release that expects build 1194. Pinned it. Headless Chromium 141 launches.
- **Did:**
  - `e2e/` (pytest and Playwright). A session fixture starts the real backend (temp DB, CORS for the test origin) and a static server for `frontend/`. Each test gets a fresh context with the service worker blocked, and an uncaught JS error fails the test.
  - `api.js` honours `window.API_BASE_URL`.
  - `check.sh` runs the browser tests (and downloads a browser where the environment allows it) and lints `e2e/`.
  - Added `e2e/` and `scripts/` to the README's project tree.
- **Found and fixed:** after logging out, the auth page kept showing the sign-up form with the earlier password still in it (28 characters, checked with a throwaway probe test), and the login form was hidden. `showAuthPage()` now resets both forms and shows the login form.
- **Verified:**
  ```
  check.sh: ruff "All checks passed!" · backend "47 passed" · "README quick start: the backend answered /health"
            e2e "2 passed in 5.48s" · first run with the venv rebuild: real 0m49s
  ```
  - Before the `ui.js` fix: `test_logging_out_shows_an_empty_login_form` failed ("#login-form … Actual value: hidden").
  - With `api.js` temporarily set back to the hard-coded address: the sign-up test fails ("expected to be visible, Actual value: hidden"). So the tests do go through the browser to the backend.
- **Commit:** 5ff957e (pushed: yes), plus this log/backlog commit.
- **Discovered:** `README.pl.md` has no project-structure section (added to P0-9).
- **Next:** P0-7b. Show the server's score, and wrong-answer feedback with the right answer.
- **Protocol notes:** browser downloads may be blocked in other environments too. `check.sh` honours `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD`, and if no matching browser is available the e2e step fails loudly instead of skipping.

### 6: 2026-10-15 05:06 UTC: P0-6 Naming prompts contain the answer
- **Baseline:** `check.sh` green (31 passed, smoke OK), same as entry 5. No human commits.
- **Did:**
  - Added `tests/test_content.py`: for every item except repetition (pronunciation), the prompt must not contain the answer as a whole word, case-insensitively.
  - Rewrote the 10 naming prompts as short plain descriptions ("What is it? A small pet that purrs and says meow."). The pictures they were meant to sit under don't exist, so dropping "(cat)" alone would have left "What is this?" next to a broken image.
  - Marked all content as placeholders pending clinical review (comment above `EXERCISE_DATA`).
  - Both READMEs and both user guides now describe naming from a description, with pictures still to come.
- **Design choices:**
  - Naming from a description works without pictures. Once pictures exist, the description becomes the first hint (noted in P2-3).
  - The image URLs stay as slots for the pictures. The broken-image icon belongs with P0-7's asset decision, which also covers the missing audio.
  - No clinical references are cited: verified references are P2-1's job.
- **Verified:**
  ```
  old content: 10 failed (every word_naming item), 6 passed (sentence completion)
  now:         ruff "All checks passed!" · pytest "47 passed, 31 warnings" · "README quick start: the backend answered /health"
  ```
- **Commit:** aa67ddf (pushed: yes), plus this log/backlog commit.
- **Discovered:** nothing new.
- **Next:** P0-7. The frontend flow is broken against the real API. It needs Playwright e2e tests (G3), so it is big: split it before starting.

### 5: 2026-10-15 05:00 UTC: P0-5 Image-recognition sessions hang the server
- **Baseline:** `check.sh` green (27 passed, smoke OK), same as entry 4. No human commits.
- **Did:**
  - `generate_exercises` raises `LookupError` when there is no content for the requested type and difficulty. It also no longer substitutes medium items for a missing difficulty.
  - `create_session` picks exercises before creating the session row, so a refused request leaves nothing behind (the row used to be committed first), and answers 422.
  - Both READMEs and both user guides mark image recognition as not available yet.
  - Added `test_exercise_selection.py` (3 tests, with a 5 s thread guard so a regression fails instead of hanging) and one API test in `test_sessions.py`. They patch the content, so they stay valid once image content exists.
- **Verified:**
  ```
  old code: empty pool -> "did not return within 5 s" · missing difficulty -> returned a medium item
            API test -> still running after 60 s, killed (exit 124)
  now:      ruff "All checks passed!" · pytest "31 passed, 31 warnings" · "README quick start: the backend answered /health"
  ```
- **Commit:** dff1068 (pushed: yes), plus this log/backlog commit.
- **Discovered:** `num_exercises` is unbounded (measured with a throwaway database). 0 and -5 are accepted. 20,000 takes 1.6 s and inserts 20,000 rows, and it scales linearly. Filed as **P1-9**, moved up from P3-7's API-hygiene list. P0-7 now notes that the dropdowns still offer image recognition.
- **Next:** P0-6. Naming prompts contain their answers ("What is this? (cat)").

### 4: 2026-10-15 04:52 UTC: P0-4 Sessions never complete
- **Baseline:** `check.sh` green (21 passed, smoke OK), same as entry 3. No human commits.
- **Did:**
  - `submit_answer` counts answered exercises in memory. The old query ran before the unflushed answer was visible, so it was always one short.
  - Completion moved, otherwise unchanged, into `finish_session()`, which only the last new answer reaches. Points are summed over all correct answers. The score is computed there. The duration runs from the session start to the last answer. The progress record is written after both.
  - Re-answering an exercise gets 409.
  - `POST /sessions/{id}/complete` returns the server's result (409 before the last answer) and ignores the client's body. Removed the `SessionComplete` schema.
  - Updated the API table rows in both READMEs.
  - Added `test_sessions.py` (6 tests).
  - Checked first that the frontend still works: it calls `/complete` after the last answer and only then returns to the dashboard, so the endpoint had to stay.
- **Design choices:**
  - One answer per exercise for now. Retries with feedback (U8) are a scoring decision for P2-3/P2-4.
  - Duration is server-side wall-clock time, so the client can't set it.
- **Verified:**
  ```
  old code, new tests:  6 failed — "assert False" (is_completed) · "assert 0 == 20" (points)
                        "assert 0.0 == 100" (client score accepted) · "assert 422 == 409" · "assert 90 <= 0" (duration)
  now: ruff "All checks passed!" · pytest "27 passed, 30 warnings" · "README quick start: the backend answered /health"
  ```
  The warnings are the same 5 kinds as entry 2 (P3-10). The count rose because more tests create a test client.
- **Commit:** cc1a0b0 (pushed: yes), plus this log/backlog commit.
- **Discovered (added to the backlog):**
  - Streak days are UTC dates, not local days (P2-9).
  - `USER_GUIDE.md` claims total time "excludes paused time" (P0-9).
  - P0-7 now notes that `/complete` returns the server's score and that a double submit gets 409.
- **Next:** P0-5. Image-recognition sessions hang the server (empty content pool, infinite loop).

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
