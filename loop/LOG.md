# Loop log

Newest entry first. One entry per iteration.

Times in entries 13–23 were first written as estimates that ran up to 2¼ hours ahead of the clock; they were corrected to the time each entry was committed. Take times from `date -u`, not from memory.

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

### 35: 2026-10-15 10:46 UTC: P1-6d Privacy notice
- **Baseline:** `check.sh` exit code 0: 149 backend tests, smoke, 40 e2e. No human commits. Tests were written in the scratchpad until it finished.
- **Facts checked before writing:**
  - The admin endpoints are open to both therapists and admins, and show every patient's account fields and sessions; they don't serve recordings.
  - `revoked_logins` holds only a random `sid` and an expiry.
  - Wrong passwords are counted per username and per (username, address).
  - The frontend references no other origins.
- **Test first:** `e2e/test_privacy_notice.py`, 4 tests: all failed before.
- **Did:**
  - `privacy.html`, with a CSP of `script-src 'none'` and EN and PL sections. The operator's facts are `.to-complete` and highlighted.
  - `.privacy-link` on the login and Account pages; `i18n` points it at the current language's section.
  - Styles, READMEs and user guides.
- **Verified:** `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 149 backend tests, smoke, 44 e2e. Polish section at 375 px checked by eye.
- **Commit:** 52854da (pushed: yes)
- **Discovered:** nothing new. The legal blanks are already H4/H5.
- **Next:** P1-6e (retention for recordings). Its default needs H4, so build it configurable and default it to off ("keep until deleted"), which is what happens today.

### 34: 2026-10-15 10:32 UTC: P1-6c2 Export and delete (web app)
- **Baseline:** `check.sh` exit code 0: 149 backend tests, smoke, 35 e2e. No human commits. Tests were written in the scratchpad until it finished.
- **Test first:** `e2e/test_your_data_page.py`. 4 tests failed on the old frontend: download; delete in EN and PL; cancel.
- **Found by the screenshot check:** at 375 px, "Delete my account" couldn't be clicked; it was behind the fixed bottom nav. The small-screen `.container { padding: 1rem }` overrode `padding-bottom: 6rem`, so on phones the bottom of every page was hidden. I added a test first: it failed with the button bottom at 675.6 px and the nav top at 654 px. Then I fixed the padding.
- **Did:**
  - `index.html`: "Your data" card and the delete `<dialog>` (shared `.app-dialog` style).
  - `api.js`: `exportMyData`, `deleteAccount`.
  - `app.js`: the handlers. A wrong password is explained in words; any close resets the dialog; success returns to login.
  - `ui.clearFormMessage`, used at logout too.
  - `.btn-danger` (white on `#B91C1C`, about 6.5:1, worked out by hand), and the phone padding fix.
  - i18n EN/PL, user guides and READMEs.
- **Verified:**
  - `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 149 backend tests, smoke, 40 e2e.
  - Screenshots at 375 px in PL/dark, before and after the fix.
- **Commit:** 1ccd0ab (pushed: yes)
- **Discovered:** the phone padding bug above, fixed in this commit.
- **Next:** P1-6d (privacy notice).

### 33: 2026-10-15 10:16 UTC: P1-6c1 Export and delete (API)
- **Baseline:** `check.sh` exit code 0: 143 backend tests, smoke, 35 e2e. No human commits. Tests were written in the scratchpad until it finished.
- **Split:** P1-6c became c1 (the API) and c2 (the Account page buttons).
- **Test first:** `backend/tests/test_your_data.py`, 4 tests. 3 failed before. "No secrets, nobody else's data" passed trivially on the old 404 and checks real output now. My first draft counted every file in the shared upload folder; I changed it to count before and after.
- **Did:**
  - `as_data()` turns rows into JSON-ready data.
  - `GET /users/me/export` returns a download, without `hashed_password` or `file_path`.
  - `DELETE /users/me`: password check, using the login limit. It deletes consents and login cut-offs by hand (they have no foreign key), the user with its cascades, and then the files.
  - `docker-smoke.sh` checks export and deletion on PostgreSQL.
  - READMEs (EN/PL).
- **Verified:**
  - `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 149 backend tests, smoke, 35 e2e.
  - `docker-smoke.sh` exit code 0, including "export, and deleting an account with a recording, work on PostgreSQL".
- **Commit:** f69b1cc (pushed: yes)
- **Discovered:** nothing new.
- **Next:** P1-6c2.

### 32: 2026-10-15 10:02 UTC: P1-6b2 Consent questions in the app
- **Baseline:** `check.sh` exit code 0: 143 backend tests, smoke, 29 e2e. No human commits. Tests were written in the scratchpad until it finished.
- **Test first:** `e2e/test_consent_questions.py`, 6 tests. A fake `SpeechRecognition` counts its starts, and `COUNT_STREAMS` counts the microphone streams. On the old frontend, 5 failed; "recognition used with consent" is a guard and passed both times.
- **Did:**
  - `index.html`: the consent `<dialog>` and a "Your choices" card.
  - `ui.askConsent` (yes, no, or null on Escape).
  - `app.js`: `hasConsent`, `saveConsent` and `showConsents`. The recording start is gated, and recognition is gated separately.
  - A recording is now uploaded whenever there is one. Before, it was uploaded only when recognition succeeded.
  - Consents are forgotten at logout.
  - `api.js`: `getConsents`/`setConsents`. `i18n.js`: 14 keys, EN and PL. CSS for the dialog and the choices.
  - `test_microphone.py` gives consent through the API first.
  - User guides and READMEs.
- **Verified:**
  - `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 143 backend tests, smoke, 35 e2e.
  - Screenshots at 375 px. The first look showed the dialog stuck to the top (the global margin reset) and a shrunken checkbox. Both were fixed and checked again in PL/dark.
- **Commit:** 12af361 (pushed: yes)
- **Discovered:** nothing new. The open H4 question about deleting recordings on withdrawal is noted on P1-6b2.
- **Next:** P1-6c (export and delete your data).

### 31: 2026-10-15 09:49 UTC: P1-6b1 Consent kept on the server
- **Baseline:** `check.sh` exit code 0: 136 backend tests, smoke, 29 e2e. No human commits. Tests were written in the scratchpad until it finished.
- **Split:** P1-6b became b1 (store the answers, and enforce them where only the server can, on uploads) and b2 (the questions and the Account page switches).
- **Test first:** `backend/tests/test_consent.py`, 5 tests: all failed before.
- **Did:**
  - `Consents` schema: strict booleans or null, unknown keys forbidden.
  - New `consents` table, with no foreign key; P1-6c must delete its rows.
  - `GET`/`PUT /users/consents`.
  - The upload checks ownership first (404), then consent (403).
  - `test_recordings.py`'s fixture grants consent first. That is new required setup; what those tests check is unchanged.
  - READMEs and user guides (EN/PL): the web app keeps no recordings until it can ask.
- **Verified:** `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 143 backend tests, smoke, 29 e2e.
- **Commit:** 2ebb758 (pushed: yes)
- **Discovered:** whether withdrawing consent should delete existing recordings is a legal question. It is noted in P1-6b2 for H4.
- **Next:** P1-6b2.

### 30: 2026-10-15 09:36 UTC: P1-6a Release the microphone
- **Baseline:** `check.sh` exit code 0: 136 backend tests, smoke, 25 e2e. No human commits. Tests were written in the scratchpad until the baseline finished.
- **Split:** P1-6 became a–f: the microphone, consent, export and deletion, the privacy notice, retention, and third parties and logs.
- **Test first:** `e2e/test_microphone.py`, 4 tests: stop recording; record twice; leave mid-recording; log out mid-recording. The page counts the streams it opens, and Chromium runs with `--use-fake-device-for-media-stream`. On the old code all 4 failed: `assert 1 == 0` (one track still live), and timeouts waiting for the tracks to end.
- **Did:**
  - `audio.js`: `startRecording()` opens the microphone, `stopRecording()` releases it, and `cleanup()` drops a recording in progress.
  - `app.js`: `stopListening()` (microphone, speech recognition and the record button) runs when an exercise is shown, when the session completes, on exit and at logout. `leaveExercise()` does the clean-up without the page switch, so logout no longer flashes the dashboard. Clicks while the microphone opens are ignored.
  - User guides (EN/PL): the microphone is on only while recording.
- **Verified:** `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 136 backend tests, smoke, 29 e2e.
- **Commit:** da7ebeb (pushed: yes)
- **Discovered:** speech recognition listens to new audio at submit time instead of the recording. That is already in P2-7, so nothing new.
- **Next:** P1-6b (consent).

### 29: 2026-10-15 09:23 UTC: P1-5e2 Change password (web app)
- **Baseline:** `check.sh` ran the 136 backend tests, smoke and the 20 existing e2e tests, all green. It also collected my new `e2e/test_account_page.py`, which I had written while it ran, and those 5 tests failed (rc=1). That doubles as "fails before"; the existing code was green.
- **Test first:** `e2e/test_account_page.py`, 5 tests (EN and PL): change the password, then log out and log in with the new one, and the old one gets 401; a wrong current password is explained in words with `role="alert"`; the fields are labelled, with `autocomplete` and `minlength`.
- **Did:**
  - `index.html`: Account page and nav item.
  - `i18n.js`: 8 keys, EN and PL.
  - `api.js`: `changePassword`; API errors carry `status`.
  - `app.js`: form handler, mapping 400, 422 and 429 to messages.
  - `ui.js`: `showFormMessage`, and logout clears the form.
  - `styles.css`: `.form-message`.
  - User guides (EN/PL): how to change your password. READMEs: feature line, and the limitation removed.
- **Verified:**
  - `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 136 backend tests, smoke, 25 e2e.
  - Screenshots at 375 px, in EN/light and PL/dark, checked by eye: four nav items fit, and the message is readable in both themes.
- **Commit:** d81dbb7 (pushed: yes)
- **Discovered:** low contrast on the language button in the dark theme; added to P2-4.
- **Next:** P1-6 (privacy). It is large, so split it first.
- **Protocol notes:** refining iteration 27's note: during the baseline, new *test files* also get picked up if `check.sh` hasn't collected that stage yet. Write them in the scratchpad, or wait for the baseline.

### 28: 2026-10-15 09:10 UTC: P1-5e1 Change password (API)
- **Baseline:** `check.sh` exit code 0: 130 backend tests, smoke, 20 e2e. No human commits. Per the iteration 27 note, I wrote only tests until the baseline finished.
- **Split:** the web app has no account page to hold a form, so P1-5e became e1 (the API) and e2 (the account page and form).
- **Test first:** `backend/tests/test_change_password.py`, 5 tests: all failed before.
- **Did:**
  - `POST /users/password` with `PasswordChange`; the sign-up rules are now shared (`check_new_password`).
  - Wrong current passwords give 400 and count towards `login_limit`; there is a shared `too_many_attempts()` for the 429.
  - New `login_cutoffs` table, which `get_current_user_id` checks against the token's `auth_time`. It has no foreign key, so it never blocks deleting a user.
  - The changing login gets a new token (cookie; in the body only for Bearer callers).
  - READMEs (EN/PL): endpoint table and Known limitations.
- **Verified:** `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 136 backend tests, smoke, 20 e2e. `docker-smoke.sh` was not run: it doesn't change passwords, and the new table is created the same way as `revoked_logins`, which it checked on PostgreSQL in iteration 27.
- **Commit:** e29ebc9 (pushed: yes)
- **Discovered:** nothing new.
- **Next:** P1-5e2.

### 27: 2026-10-15 08:58 UTC: P1-5d Logout ends the login on the server
- **Baseline:** the backend stage passed: 125 tests. Then 1 e2e test failed, but that's on me: I edited `security.py` (which now requires `sid`) while the baseline was still running. Its e2e server started on my edited code, and the old aged-token test sent no `sid`. Not a regression.
- **Test first:**
  - `backend/tests/test_logout.py`, 5 tests. 4 failed before. The "other devices carry on" test is a guard and passed both times.
  - The e2e logout test now also checks that a copied token gets 401. Against the old backend it got 200.
- **Did:**
  - Tokens get a random `sid`, kept by `/auth/refresh`, and `decode_token` requires it.
  - New `revoked_logins` table, with `sid` and `expires_at`. It is a table and not a column, because there are no migrations yet (P3-1).
  - `get_current_user_id` refuses revoked logins.
  - `/auth/logout` revokes the login when the request carries a valid token (Bearer, or the cookie with `X-Requested-With`), and deletes rows that have expired.
  - Hand-made test tokens (`test_login_renewal.py`, e2e aged token) now include `sid`.
  - `docker-smoke.sh` logs out and checks for 401.
  - READMEs (EN/PL): endpoint table and Known limitations.
- **Verified:**
  - `scripts/check.sh` exit code 0 (run twice, the second after the docs edits): ruff, pip-audit "No known vulnerabilities found", 130 backend tests, smoke, 20 e2e.
  - `scripts/docker-smoke.sh` exit code 0: "page, /api, sign-up, login, profile and logout all work through nginx".
- **Commit:** 4e5c445 (pushed: yes)
- **Discovered:** P1-5e (no way to change a password).
- **Next:** P1-5e.
- **Protocol notes:** don't edit backend code while the baseline `check.sh` is still running. Its e2e stage starts its server from the working tree a minute or two in, so the baseline ends up testing a mix of old and new code. Read and write tests during the baseline, but make code changes only after it finishes.

### 26: 2026-10-15 08:45 UTC: P1-5c3 Wrong-password limit per client
- **Baseline:** `check.sh` exit code 0: 123 backend tests, smoke, 20 e2e. No human commits.
- **Found while planning:** in Docker every request reached the backend from nginx's address, and nginx appended to any `X-Forwarded-For` header the client sent. So keying on the client address needs the proxy set up too, or it changes nothing, or it can be forged.
- **Test first:** 2 new tests in `test_login_safety.py`, using `TestClient(client=(address, port))`. Both failed before: a stranger's 5 wrong passwords locked the owner out, and the account limit didn't exist.
- **Did:**
  - `login_limit.py`: per (username, client) count, limit 5, and per-account count, limit 50, in a 15-minute window. All three are settings. A success clears only that client's count, so an attacker can't reset the account count by waiting for the owner to log in.
  - `docker-compose.yml`: `FORWARDED_ALLOW_IPS: "*"`, and the backend port is bound to `127.0.0.1`. `nginx.conf`: `X-Forwarded-For $remote_addr`, replacing the header instead of appending to it.
  - `docker-smoke.sh`: forged `X-Forwarded-For` values still add up to 429. The backend's access log shows the client's address, not nginx's.
  - READMEs (config table, Docker section, Known limitations), user guides (EN/PL), `.env.template`. H7 now also asks about the numbers.
- **Verified:**
  - `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 125 backend tests, smoke, 20 e2e.
  - `scripts/docker-smoke.sh` exit code 0: "nginx is 172.18.0.4; the backend logged: 172.18.0.1:0 - POST /api/v1/auth/login ... 429".
  - Not done: running the new Docker checks against the old setup.
- **Commit:** 1027037 (pushed: yes)
- **Discovered:** nothing new.
- **Next:** P1-5d (revoke tokens at logout).

### 25: 2026-10-15 08:35 UTC: P1-5c2 Web app uses the cookie
- **Baseline:** `check.sh` exit code 0: 121 backend tests, smoke, 17 e2e. No human commits.
- **Found while planning:** with a cookie login, `/auth/refresh` still returned the token in its body, so an injected script could fetch it and defeat httpOnly. Fixed in the same change.
- **Test first:**
  - Backend: 2 new tests in `test_cookie_login.py`. Both failed before: the token came back in the body of a cookie renewal, and there were no `issued_at`/`expires_at` fields.
  - E2E: 3 new account tests, and the renewal tests rewritten for cookies. On the old frontend, 3 failed: the token was readable from `localStorage`, an old token wasn't removed, and the cookie wasn't renewed. The logout test passed both times, because the old frontend never stored the cookie.
- **Did:**
  - `api.js`: `credentials: 'include'` and `X-Requested-With` on every call, including the CSV/PDF export and recording upload; no token kept; renewal from `issued_at`/`expires_at` in memory; `logout()` waits for any renewal, then calls `/auth/logout`.
  - `app.js`: start-up asks the server whether you're logged in, and logout waits for the server.
  - Backend: `TokenResponse` gains `issued_at`/`expires_at`; `access_token` is `null` for a renewal made through the cookie.
  - E2E: the tests read the httpOnly cookie through Playwright (`login_cookie`, `browser_token` in conftest).
  - READMEs (EN/PL): the API section; open the dev app on `localhost`, not `127.0.0.1`; Known limitations now says tokens survive logout.
- **Verified:**
  - `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 123 backend tests, smoke, 20 e2e.
  - `scripts/docker-smoke.sh` exit code 0: "page, /api, sign-up, login and profile all work through nginx", and the CLI admin works.
- **Commit:** b3315c5 (pushed: yes)
- **Discovered:** P1-5d. Logout doesn't revoke tokens, and a copied token can be renewed with Bearer for up to 12 hours.
- **Next:** P1-5c3 (the lockout review; its numbers depend on H7), or P1-5d if P1-5c3 can't go further without H7.

### 24: 2026-10-15 08:24 UTC: P1-5c1 Login cookie on the server
- **Baseline:** green at the end of iteration 23, with the same code (only `loop/` changed since): 115 backend, smoke, 17 e2e. No human commits.
- **Split:** P1-5c became c1 (the server side), c2 (the web app switches to the cookie) and c3 (the follow-ups on the wrong-password limit). Docker runs one uvicorn worker, so the shared-count item is only needed if that changes.
- **Test first:** `backend/tests/test_cookie_login.py`, 6 tests. On the old code: 5 failed, and the Bearer test passed (it's a regression guard). I first expected 201 from creating a session; the endpoint answers 200, and I fixed the test.
- **Did:**
  - `security.py`: `get_token` takes the Bearer header, or else the `access_token` cookie. A change made through the cookie must carry `X-Requested-With`, or it gets 403. Helpers set and clear the cookie (httpOnly, `SameSite=Strict`, path `/api`, Secure unless `COOKIE_SECURE=false`).
  - `auth.py`: register, login and refresh set the cookie; new public `POST /auth/logout` clears it.
  - READMEs (EN/PL): API section, endpoint table, `COOKIE_SECURE`, Known limitations; `.env.template`. The endpoint table now lists `/auth/refresh`, which I missed in iteration 23.
  - `tests/test_docs.py`: "csrf" removed from the known-false claims, since the guard now exists and is tested.
- **Verified:** `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 121 backend tests, smoke, 17 e2e. The first run failed on the docs test (the README now mentions CSRF); fixed as above. `scripts/docker-smoke.sh` was not run, because nothing in the Docker setup changed; P1-5c2 runs it.
- **Commit:** e17c94e (pushed: yes)
- **Discovered:** people with aphasia may mistype often enough to lock themselves out after 5 wrong passwords; added to P1-5c3.
- **Next:** P1-5c2.

### 23: 2026-10-15 08:15 UTC: P1-5b Stay logged in while active
- **Baseline:** `check.sh` green (110 backend, smoke, 15 e2e). No human commits.
- **Split:** P1-5b (renewal and idle timeout) and P1-5c (tokens out of `localStorage`, plus the two limiter follow-ups from P1-5a).
- **Test first:**
  - `backend/tests/test_login_renewal.py`, 4 tests: 4 failed on the old code.
  - `e2e/test_login_renewal.py`, 2 tests: the renewal test failed on the old frontend (timeout waiting for a new token); the "fresh token is left alone" test passed both times.
- **Did:**
  - Tokens carry `iat` and `auth_time`. `exp` is capped at `auth_time + LOGIN_MAX_HOURS` (new setting, default 12).
  - `POST /api/v1/auth/refresh` (logged-in only, so the authorization test covers it automatically): same `auth_time`, new `exp`. 401 for tokens without `auth_time` or past the maximum.
  - `frontend/js/api.js`: after any successful non-auth call, renew in the background once the token is past half its life. A refused renewal is remembered for that token; a renewal that finishes after logout is ignored.
  - READMEs (feature line, config table, Known limitations), user guides (EN/PL) and `.env.template` updated. Fixed "szyfrowane" → "haszowane" in README.pl.md (bcrypt hashes; it doesn't encrypt).
- **Verified:** `scripts/check.sh` exit code 0: ruff, pip-audit "No known vulnerabilities found", 115 backend tests, smoke, 17 e2e.
- **Commit:** 032db35 (pushed: yes)
- **Discovered:** whether 30 minutes idle and 12 hours maximum suit this population is a human decision; added to H7.
- **Next:** P1-5c (cookies with CSRF) if it fits one iteration; otherwise split it, or take P1-6.

### 22: 2026-10-15 08:05 UTC: P1-5a Login safety
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

### 21: 2026-10-15 07:54 UTC: P1-4 Dependency health
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

### 20: 2026-10-15 07:40 UTC: P1-3a Staff accounts and authorization tests
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

### 19: 2026-10-15 07:30 UTC: P1-2 Private voice recordings
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

### 18: 2026-10-15 07:20 UTC: P1-1 No user input as HTML; CSP
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

### 17: 2026-10-15 07:11 UTC: P1-10 Simultaneous answers
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

### 16: 2026-10-15 07:02 UTC: P0-9b User guides (all P0 items done)
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

### 15: 2026-10-15 06:53 UTC: P0-9a READMEs describe only what exists
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

### 14: 2026-10-15 06:43 UTC: P0-8 Docker stack
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

### 13: 2026-10-15 06:30 UTC: P0-7g The whole flow in EN and PL (P0-7 done)
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
