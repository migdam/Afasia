# Backlog

**Status markers:** `[ ]` to do · `[x]` done (commit hash) · `[!]` blocked (reason)

**Priorities:**
- **P0**: broken, doesn't run
- **P1**: security, privacy, data integrity
- **P2**: clinically sound and aphasia-friendly
- **P3**: engineering quality
- **P4**: features (only after P0–P2 are done)

**Evidence:**
- ✅ = reproduced on 2026-10-14 by running the code in a scratch copy (Python 3.11, pinned `requirements.txt`; see `loop/LOG.md`, iteration 0).
- 🔎 = found by reading the code. Reproduce it before fixing.

Humans: edit freely. Reorder, add, answer questions inline. The loop treats your edits as authoritative.

## Gates

| Gate | Status | Evidence |
|------|--------|----------|
| G1 Runs | 🟡 | `scripts/check.sh` passes, including `scripts/smoke.sh`: the README backend quick start in a copy of the tree answers `/health`. Not yet covered: a from-scratch install in the copy (it reuses `.venv`) and the frontend half of the quick start (P0-7) |
| G2 Backend tests | 🔴 | 51 tests pass, including register → login → profile and a full scored session; coverage not measured |
| G3 End-to-end | 🟡 | 13 tests in Chromium, including the whole flow (sign-up → word naming and sentence completion → feedback → dashboard and progress scores) in EN and PL, the admin list, the chart, and the session edge cases. Not covered yet: pronunciation (P2-7) and export (CSV/PDF) |
| G4 Authorization | 🟡 | Tested (`test_authorization.py`): no route without a login, no admin route for patients, and users can't reach each other's sessions, answers, schedules or recordings. Admins are created explicitly (P1-3a). Still open: therapists limited to their own patients (P1-3b) |
| G5 Security | 🟢 | Every criterion in `loop/PROMPT.md` met as of iteration 42. Done: no untrusted data reaches `innerHTML`, and the CSP forbids inline scripts (P1-1). Recordings only through the owner-checked endpoint (P1-2); pip-audit clean in `check.sh` (P1-4). Login rate-limited, and accounts checked on every request (P1-5a). The web app's login is an httpOnly cookie with a CSRF guard (P1-5c1, P1-5c2). Logout ends the login on the server (P1-5d). Secrets only from the environment: the template key and short keys are refused (P1-8a); the CSP allows connections only to the app and its API (P1-8c). Related but under G4: therapists aren't yet limited to their own patients (P1-3b, blocked on H7) |
| G6 Accessibility | 🔴 | Not measured |
| G7 Aphasia-friendly | 🔴 | Auto-advance, visible timer, typing required (P2-4..P2-6) |
| G8 Clinical content | 🔴 | All content in PL and EN as data, checked at startup (P2-2a, P2-2b); no answer leaks, by word or by option position (C4). Missing: images, audio and licenses (P2-2c, H2/H3), cue levels (P2-3), and clinical review (H1) |
| G9 i18n | 🔴 | Hard-coded English strings in JS (P2-10) |
| G10 Privacy | 🟢 | Every criterion met (P1-6a–f): export and deletion, consent before recording and before speech recognition, configurable retention, no third-party requests (tested), and a privacy notice in PL and EN. Its legal blanks (who runs the app, legal basis, hosting, contact, retention periods) wait for H4/H5 |
| G11 Honest docs | 🟢 | The READMEs and user guides (EN/PL) describe only what exists, Known limitations are listed, and `test_docs.py` checks that every relative link resolves and that no known-false claim returns (P0-9) |
| G12 Lighthouse | 🔴 | Not measured |
| G13 Delivery | 🟡 | The Docker Compose stack starts and passes `scripts/docker-smoke.sh` (P0-8). No CI yet (P3-2) |

## P0: Make it run

- [x] **P0-1 Verification harness.** (7240b2b) `scripts/check.sh` is the single entry point (exit 0 = green). It creates or reuses `.venv` at the repo root (kept out of the backend Docker build context), reinstalls `requirements.txt` + `requirements-dev.txt` only when they change, then runs `ruff check` (fatal rules only until P3-3) and `pytest`. The smoke tests (app imports, `GET /health` = 200) are strict xfails for the P0-2 crash, so the build is green without hiding it. Later items extend `check.sh`: coverage with pytest-cov (G2), pip-audit (P1-4), e2e (P0-7).
- [x] **P0-2 Backend can't start** ✅ (a22b9fb). Fixed all three crashes. `.env` is now read from the repo root wherever the app runs, and unused keys are ignored. `scripts/smoke.sh` (run by `check.sh`) follows the README quick start and checks `/health`. Original report:
  1. `app/core/config.py`: the `BACKEND_CORS_ORIGINS` validator turns the string into a list, which the `str` field then rejects (`Input should be a valid string`). This happens even with defaults, so the app never starts. Two related problems:
     - The README says to copy the template to the repo root (`cp ../.env.template ../.env`), but settings read `.env` from the working directory (`backend/`), so `SECRET_KEY` is reported missing.
     - Putting `.env` in `backend/` fails too, because `.env.template` contains `SMTP_*` keys that Settings forbids (`Extra inputs are not permitted`).
  2. `app/db/models.py`: `UserBadge.metadata` is reserved by SQLAlchemy Declarative (`Attribute name 'metadata' is reserved`).
  3. `app/api/v1/schemas.py`: `EmailStr` needs `email-validator`, which is missing from requirements.

  **Acceptance:** following the README exactly, `uvicorn app.main:app` starts and `/health` returns 200. Tests cover settings parsing: a comma-separated CORS env var, the `.env` location, and unknown keys. Delete the `crashes_on_import` marker in `backend/tests/test_smoke.py`; strict mode fails the run until you do.
- [x] **P0-3 Every authenticated request returns 401** ✅ (d3988e9). Tokens carry a string `sub`, PyJWT replaced python-jose, decoding requires `exp` and `sub`, and missing or invalid tokens get 401 with `WWW-Authenticate: Bearer`. The fresh-venv run also showed that every registration crashed (passlib 1.7.4 + bcrypt 5), so bcrypt is held at 4.3.0 until P1-4. Original report: registration (201) and login (200) work, but the token they return is rejected: tokens are created with an integer `sub`, and python-jose refuses non-string subjects on decode. Fix it by encoding `str(user.id)` and parsing it back. While here:
  - Replace python-jose (unmaintained, has published advisories) with PyJWT.
  - Return 401, not 403, for missing or invalid tokens.

  **Acceptance:** tests for register → login → `GET /users/profile` = 200, and for a bad or missing token = 401.
- [x] **P0-4 Sessions never complete, so there are no points, progress, streaks or badges** ✅ (cc1a0b0). The last answer now completes the session once, in `finish_session()` (and under simultaneous requests since P1-10): points are summed over correct answers, the score and duration are computed on the server, and the progress record comes last. Re-answering gets 409. `POST /complete` returns the server's result and ignores the client. Original report: in `submit_answer`, the "all answered?" count runs before the current answer is flushed (`autoflush=False`). Reproduced: after answering 3/3 correctly, the session shows `completed_exercises=2`, is not completed, has 0 points and no progress record. Re-submitting any answer then "completes" it, and every re-submit awards points again and adds another progress record (10 → 20 points, 1 → 2 records). Further problems in the same flow:
  - Points are computed only for the last answer, not the session.
  - The progress record is written before the duration is known, so time is always 0.
  - `POST /sessions/{id}/complete` overwrites the server-computed score with whatever the client sends.

  **Acceptance:** tests for completion on the last answer, points summed over correct answers, idempotent re-submission (no double points or records), server-only scoring, and a recorded duration.
- [x] **P0-5 Image-recognition sessions hang the server** ✅ (dff1068). A type or difficulty without content now gets 422 and creates no session. There's no more silent fallback to medium. Docs mark image recognition as not available yet. Original report: `EXERCISE_DATA` has no `image_recognition` content, and `generate_exercises` loops forever on an empty pool. Reproduced: still spinning after 3 s, pinning a worker thread at 100% CPU. Fail fast with a clear 4xx when there is no content, and add a test.
- [x] **P0-6 Naming prompts contain the answer** ✅ (aa67ddf). Naming items now describe the thing to name, since there are no pictures to show. `test_content.py` enforces C4 for every item. The items are placeholders, pending clinical review. Original report: for example, `"What is this? (cat)"` has the answer `cat`. Fix the naming prompts, and add a test that no naming prompt contains its answer (C4). Repetition prompts like "Say: Hello" are fine. The full content model is P2-2.
- [x] **P0-7 Frontend flow is broken against the real API** 🔎 (cd5bbf7). Split into P0-7a–g on 2026-10-15; all done. Pronunciation is not part of the acceptance test: it can't work until P2-7. Each one comes with Playwright tests in `e2e/`. **Acceptance for the whole item:** a Playwright e2e test, in EN and PL: register → one session per working exercise type → correct feedback → progress shows the session with the right score.
  - [x] **P0-7a E2E harness** (5ff957e). `e2e/`: pytest and Playwright against the real backend and the static frontend, run by `check.sh`. Covers sign-up, staying signed in after a reload, logout and login. Found and fixed along the way: logging out left the sign-up form on screen, password included.
  - [x] **P0-7b Session result and feedback** (6a0c8b4). The answer response carries `correct_answer` once the exercise is answered. A wrong answer shows "Not quite. Correct answer: **blue**", and the final alert shows the server's score. Original report:
    - The final score is always 0%: `completeSession()` counts `is_correct` on the exercise list fetched at session start (all `null`) and shows that. Since P0-4 the server ignores the client's score, and `POST /complete` returns the server-computed session: show its `score`, and stop sending score and duration.
    - Wrong-answer feedback reads "Incorrect. Try again! Correct! Well done!: undefined". It concatenates both messages and reads `correct_answer`, a field the API never returns (✅ confirmed absent). Return the correct answer in the answer response only, once the exercise is answered, and show one calm message.

    **Test:** a sentence-completion session with one wrong answer shows the right answer and ends with the server's score.
  - [x] **P0-7c Exercise state** (1f7fdce). Submit is disabled until the next exercise is shown. The answer is read only from the input the exercise shows. Each exercise starts with an empty text box and no recording. Leaving during feedback cancels the pending move to the next exercise, which used to fire in the next session. Original report:
    - Submit stays enabled during the 2 s feedback delay, so a double click submits twice and skips an exercise. Since P0-4 the second submission gets 409 "Exercise already answered", which the UI shows as an error alert.
    - `recordedAudio` and the hidden text input aren't reset between exercises or sessions.
  - [x] **P0-7d Dashboard and admin data** (19bb94f). `GET /admin/users` returns `is_active`, so deactivation works (it never did). The list is built with DOM methods, not `innerHTML`. The dashboard loads the badge count. The admin menu is hidden again for non-staff users. Original report:
    - The admin list reads `user.is_active`, which `UserResponse` doesn't include.
    - The dashboard badge count only updates after visiting Progress.
  - [x] **P0-7e Unavailable content** (ad4204c). The menus no longer offer Image Recognition. The 15 references to images and audio that don't exist are removed, and a content test requires any referenced asset to exist. Original report:
    - Both exercise-type dropdowns offer Image Recognition, which the server refuses (422) since P0-5. Hide it until P2-2 adds content.
    - The images and audio that exercises reference (`/assets/images/*.jpg`, `/assets/audio/*.mp3`) don't exist, so the UI shows broken media. Show nothing until there are assets (H2, H3).
  - [x] **P0-7f Progress chart** (190fc25). The line is drawn, the canvas is 300 px high, colours follow the theme, and an empty history says so. Original report: It draws dots but no line (`beginPath()` inside the path loop), the canvas has no height, and its colors are hard-coded for the light theme.
  - [x] **P0-7g The whole flow in EN and PL** (cd5bbf7). `e2e/test_full_flow.py`: word naming (80%) and sentence completion (100%), with feedback in each language and the scores on the dashboard and progress page. Pronunciation is left out until P2-7.
- [x] **P0-8 Docker stack** 🔎 (e0671a1). Verified with a real Docker daemon: `scripts/docker-smoke.sh` starts the stack and signs up and logs in through nginx on PostgreSQL. Secrets come from `.env`, `/api` is proxied, health checks are in place, and `.dockerignore` files are added. Original report:
  - No PostgreSQL driver in requirements, so the backend can't connect to the compose `db` service.
  - DB password and secret fallback are hard-coded in `docker-compose.yml`.
  - The frontend calls `localhost:8000`, which only works on the developer's own machine. Proxy `/api` through nginx instead. Since P0-7a a page can set `window.API_BASE_URL` before `api.js` loads; the deployed default should be the same-origin `/api/v1`.
  - `.gitignore` ignores `.dockerignore` files, so the build contexts can't exclude anything: local databases, uploads and caches get copied into the images. Stop ignoring it and add a `.dockerignore` per build context.

  **Acceptance:** `docker compose up` passes the smoke test. If Docker can't run in the loop's environment, mark the item `[!]` and say so.
- [x] **P0-9 Docs claim things that aren't true** 🔎 (1276117). Split on 2026-10-15, both parts done:
  - [x] **P0-9a READMEs** (f056514). Both READMEs are rewritten from verified facts: status, what works and is tested, what doesn't work, Known limitations, and no license chosen. `README_IMPLEMENTATION.md` is deleted. `backend/tests/test_docs.py` checks that every relative link resolves and that the READMEs contain no known-false claims.
  - [x] **P0-9b User guides and template** (1276117). Both guides are rewritten from the real screens and labels, the `SMTP_*` keys are gone, and `test_docs.py` checks the guides too. Original plan:
    - Rewrite `docs/USER_GUIDE.md` and `docs/USER_GUIDE.pl.md` the same way, and add both to `CHECKED_FOR_CLAIMS` in `test_docs.py`.
    - Remove the unused `SMTP_*` keys from `.env.template`.
    - The guides still describe the API and deployment documents that don't exist, picture-based exercises, "Explanation", streak-safe rest days, the FAQ's pricing placeholder, and so on.

  Original report: 27 matches across `README.md`, `README.pl.md`, `README_IMPLEMENTATION.md` and `docs/USER_GUIDE.md` for claims that are false or unverified:
  - "production-ready", WCAG 2.1 AA compliance, Lighthouse and performance numbers, CSRF protection, rate limiting.
  - Native-speaker recordings, calendar integration, leaderboards, background sync, a "Schedule Next Session" button.
  - Badges that are never awarded.
  - Links to `docs/API.md`, `docs/DEPLOYMENT.md` and `LICENSE`, none of which exist.
  - Invented contact details: `support@aphasia-therapy.app`, `@AphasiaTherapy`, a website.
  - `.env.template` offers `SMTP_*` settings "for notifications", but nothing sends email and Settings ignores those keys. Remove them until P4-4 uses them.
  - `README.pl.md` has no project-structure section, unlike `README.md`.
  - `docs/USER_GUIDE.md` says total time "excludes paused time". There is no pause: a session's time runs from its start to its last answer (since P0-4).

  Replace them with an accurate status ("early development"), a "Known limitations" section, and links that resolve, in both languages.

## P1: Safety (security, privacy, data integrity)

- [x] **P1-10 Simultaneous answers are all accepted** ✅ (945b598). Answers and completion are claimed with conditional UPDATEs, the count is taken after commit, and points are added in SQL. Tested with simultaneous requests on SQLite and PostgreSQL. It also fixed sessions left unfinished for good when the last two answers arrived together. Original report: The "already answered" check in `submit_answer` reads the row and then writes it, so two requests at the same moment both pass. Measured on 2026-10-15: two threads answered the same exercise, and both were accepted in 20 of 20 trials. 20 one-exercise sessions ended with 40 progress records, so `finish_session()` ran twice for each and points were doubled. In the browser, a double click caused the same thing before P0-7c. Two tabs or a network retry still can. Fixes:
  - Claim the answer atomically: `UPDATE … WHERE id = :id AND is_correct IS NULL`, then check the row count.
  - Complete the session atomically too (`… WHERE is_completed = false`). Two different last exercises answered at once must neither both complete the session nor both miss it.
  - Add tests with concurrent requests.

- [x] **P1-1 Stored XSS into the therapist/admin dashboard** 🔎 (64ae795). Every list and button is built with DOM methods, the inline script is moved into a file, and `index.html` sets a CSP with `script-src 'self'`. Tested with markup in titles, plus a guard test against `innerHTML` and inline handlers. Original report: Usernames, emails, session and schedule titles, and exercise options go into `innerHTML` (`frontend/js/ui.js`, `frontend/js/app.js`). Usernames have no validation, so a patient can register a username containing HTML/JS that runs in a therapist's browser, where the JWT sits in `localStorage`. Fixes:
  - Render with `textContent` or DOM APIs.
  - Remove the inline `onclick=` handlers.
  - Move the inline service-worker script into a file.
  - Add a strict Content-Security-Policy.

  **Test:** an e2e test with a malicious username shows it as plain text.

  Progress: the admin list, the worst case, has been built with DOM methods since P0-7d, and `e2e/test_admin.py` shows a `<b>…</b>` username there as text. Still to do (`grep -n "innerHTML\|onclick=" frontend/js`):
  - `ui.js`: recent sessions, scheduled sessions (titles, plus an inline `onclick`), badges, and the empty-state messages.
  - `app.js`: exercise options and the record button.
- [x] **P1-2 Voice recordings are served without authentication** 🔎 (99716d3). The public mount is gone. Files are stored in `UPLOAD_DIR/audio` under random names with their real format. Uploads check the owner, type and size. Tested. Original report: `main.py` mounts the upload directory at `/uploads` with `StaticFiles`, so recordings of patients' speech can be fetched by anyone with the URL. Fixes:
  - Remove the mount, and serve recordings only through the authenticated, ownership-checked endpoint.
  - Use random (uuid) file names, stored outside any web root.
  - In the upload endpoint, enforce `MAX_UPLOAD_SIZE` (defined but unused; the whole file is read into memory) and check the content type.
  - Store the real format: MediaRecorder produces webm/ogg, but files are saved as `.wav`.
  - Check that the exercise belongs to the user.
- [ ] **P1-3 Therapist and admin model** 🔎. Split on 2026-10-15:
  - [x] **P1-3a Staff accounts and authorization tests** (719dca3). `python -m app.cli create-user` / `set-role` (12-character minimum, password never on the command line), documented in both READMEs and checked in `docker-smoke.sh`. `test_authorization.py`: every non-public route needs a login, patients get 403 on admin routes, and users can't reach each other's data.
  - [!] **P1-3b Therapists see only their patients.** Blocked on H7: it needs a decision on how therapists and patients are linked. Today every therapist can see and deactivate every patient. Needs a therapist–patient link, plus decisions from H7: who invites whom, and how the patient consents. Admins keep the whole list. Only admins should deactivate accounts.

  Original report: Any therapist can see and deactivate every patient, and there is no way to create a therapist or admin account at all. Add:
  - Therapist–patient assignment (invite plus consent).
  - An admin bootstrap command (`python -m app.cli create-admin`).
  - Authorization tests for every endpoint (G4).
- [x] **P1-4 Dependency health** 🔎 (c625e62). Everything is on current releases (SQLAlchemy on 2.0.54). Unused packages are dropped. passlib is replaced by bcrypt 5, and passwords over 72 bytes are refused. `pip-audit` runs in `check.sh` and reports 0 known vulnerabilities (there were 67). Original report: Pins date from late 2023: fastapi 0.104 / starlette 0.27 and python-multipart 0.0.6, some with published security advisories. passlib 1.7.4 is unmaintained and crashes on its first hash with bcrypt 5 ✅, so bcrypt is held at 4.3.0 (P0-3). Replace passlib (bcrypt used directly, or Argon2) and decide what happens to passwords over bcrypt's 72-byte limit: bcrypt 4 silently truncates them, bcrypt 5 raises. (python-jose was replaced by PyJWT in P0-3.) Upgrade to current supported versions, drop the unused matplotlib and pillow, and add `pip-audit` to `requirements-dev.txt` and `check.sh` (it must come back clean). Upgrading to Starlette 0.37.2 or later also lifts the `httpx<0.28` pin in `requirements-dev.txt`: 0.37.2 is the first release whose `TestClient` no longer passes `app=` to `httpx.Client` (checked in the published wheels).
- [x] **P1-5a Login safety** (73b9ee7). The account is looked up on every request, so a deactivated or deleted user's token gets 401 at once. 5 wrong passwords for a username within 15 minutes give 429 with `Retry-After`; a successful login clears the count. The count is in memory, so it is per process. Sign-up passwords need at least 8 characters (staff accounts from the CLI already needed 12).
- [x] **P1-5b Stay logged in while active** 🔎 (032db35). Tokens lasted 30 minutes with no refresh, so people were logged out mid-exercise. Now 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`) is an idle timeout: `POST /auth/refresh` issues a fresh token, and the frontend renews once a token is past half its life. Tokens carry `auth_time`, and no login lasts past `LOGIN_MAX_HOURS` (12) after logging in. Whether these defaults suit slow, effortful practice is a question for H7.
- [x] **P1-5c1 Login cookie on the server** (e17c94e). Sign-up, login and refresh also set an httpOnly, `SameSite=Strict`, Secure (`COOKIE_SECURE`) cookie on path `/api`. The token is read from the Bearer header or else the cookie; a change made through the cookie needs `X-Requested-With`, or gets 403 (CSRF). `POST /auth/logout` clears the cookie. Bearer clients are unchanged.
- [x] **P1-5c2 Web app uses the cookie, not `localStorage`** (b3315c5). Every call sends the cookie (`credentials: 'include'`) and `X-Requested-With`. Start-up asks `/users/profile`; logout waits for any renewal, then calls `/auth/logout`. Renewal keeps only `issued_at`/`expires_at` in memory. Old `localStorage` tokens are removed. A renewal made through the cookie no longer returns the token in the body. Chromium stores the Secure cookie on `http://127.0.0.1`; `docker-smoke.sh` passes.
- [x] **P1-5c3 Wrong-password limit per client** (1027037). Counted per username and client address (5), plus a looser per-account count from all addresses (50), within 15 minutes; all three are settings. In Docker, nginx replaces `X-Forwarded-For`, the backend trusts it (`FORWARDED_ALLOW_IPS`), and the backend port is bound to 127.0.0.1; `docker-smoke.sh` checks that forged headers don't help and that the backend sees the client's address. Still open: whether 5 and 50 suit people with aphasia (H7). The counts are per process, which matters only if the app ever runs several workers (Docker runs one).
- [x] **P1-5d Logout ends the login on the server too** (4e5c445). Tokens carry a random login id (`sid`), kept by renewals. Logout records it in `revoked_logins`, which every request checks; other devices stay logged in. Tokens without `sid` are refused, so everyone logs in again once after upgrading.
- [x] **P1-5e1 Change password, API** (e29ebc9). `POST /users/password` needs the current password (wrong ones count towards the login limit), applies the sign-up rules, ends the person's other logins (`login_cutoffs` table), and gives this login a new token. A "forgot password" reset needs email, which is out of scope for the loop; it goes to H5 (hosting and accounts) when someone wants it.
- [x] **P1-5e2 Change password, web app** (d81dbb7). New Account page (bottom nav, EN/PL) with a labelled change-password form. Results show as a message in words under the button (`role="alert"` for errors, `role="status"` for success), in the current language. `ui.showFormMessage` can be reused when P2-4 replaces `alert()`.
- **P1-6 Privacy (GDPR: health data is special-category)** 🔎. Split into a–f on 2026-10-15; all done.
  - [x] **P1-6a Release the microphone** 🔎 (da7ebeb). It is opened for each recording and released when the recording stops, when you leave the session or exercise, or when you log out. `e2e/test_microphone.py` uses Chromium's fake microphone.
  - [x] **P1-6b1 Consent kept on the server** (2ebb758). `GET`/`PUT /users/consents` (`recordings`, `speech_recognition`: true, false or null for not asked), in a `consents` table. Uploads get 403 without consent to recordings. Until P1-6b2 the web app keeps no recordings.
  - [x] **P1-6b2 Consent questions in the app** (12af361). An in-app `<dialog>` asks before the first recording, and separately before speech recognition, in EN and PL. No keeps the microphone off, or recognition unstarted, and the exercise can still be submitted. Both answers can be changed under "Your choices" on the Account page. Still open for H4: should withdrawing consent to recordings also delete the recordings already kept? Self-rating as the fallback judge belongs to P2-7.
  - [x] **P1-6c1 Export and delete, API** (f69b1cc). `GET /users/me/export` (JSON download; no password hash or file locations) and `DELETE /users/me` with the password (all rows and recording files; the cookie is cleared). Checked on PostgreSQL by `docker-smoke.sh`.
  - [x] **P1-6c2 Export and delete, web app** (1ccd0ab). On the Account page: "Download my data", and "Delete my account" with an in-app password dialog, in EN and PL. Also fixed: on phones, the bottom of every page was hidden behind the bottom nav.
  - [x] **P1-6d Privacy notice** (52854da). `frontend/privacy.html` (no scripts), EN and PL, linked from the login and Account pages in the current language. Only facts the code supports; the operator's parts are marked "[to be completed]". **Keep it true:** any change to what is stored or who can see it must update this page in both languages.
  - [x] **P1-6e Retention for recordings** (369a4cd). `RECORDING_RETENTION_DAYS` (default 0: keep until deleted). With a limit, the clean-up runs at start-up and then daily; `python -m app.cli delete-old-recordings [--days N]` runs it at once. The actual period is H4's decision; the privacy notice marks it "[to be completed]".
  - [x] **P1-6f No third-party requests, no personal data in logs** (2d75caf). The audit found nothing to fix. `tests/test_logs.py` (a whole visit at DEBUG, checked to catch a planted leak) and `e2e/test_no_third_parties.py` (browser requests, and the real uvicorn log) keep it so. The privacy notice says what the logs do hold: time, network address, path.
- [x] **P1-7 Users would never receive fixes** 🔎 (14bdae4). The caching service worker is retired: `sw.js` is now a clean-up worker that deletes caches and unregisters itself on devices that have the old one, and the app registers none. It had also cached API responses, personal data included, when the API was same-origin (Docker). nginx: `no-cache` for pages, scripts and styles, a day for images and fonts, and security headers on every location. Also fixed: `privacy.html` was missing from the Docker image. No offline support, and the READMEs say so.
- **P1-8 Safe defaults** 🔎. Split into a–d on 2026-10-15; all done.
  - [x] **P1-8a Debug off, no guessable keys, no settings on show** (fc2e1a0). `DEBUG` defaults to false (Compose uses `${DEBUG:-false}`). The app refuses the template's `SECRET_KEY` and keys under 32 bytes. `/health/detailed` shows no settings and really checks the database (503 when it's down).
  - [x] **P1-8b Docker gets all the settings** 🔎 (f93f6db). Compose lists every setting as `${NAME:-default}` (the app's defaults); `DATABASE_URL`, `UPLOAD_DIR`, `HOST` and `PORT` are fixed by the setup. `tests/test_docker_settings.py` keeps the list complete and the defaults in step, and `docker-smoke.sh` checks that a value from `.env` (a 17-minute login) reaches the backend.
  - [x] **P1-8c A tighter CSP** (8feaeaf). The page's `connect-src` allows only itself and local development ports. Docker's nginx adds a header policy with `connect-src 'self'` and `frame-ancestors 'none'`. An API on another site must be added to `index.html` (README).
  - [x] **P1-8d Times in UTC, with an offset** (e94cf91). The API takes times as UTC and sends them with `+00:00` (`schemas.UTCDateTime`); the database keeps naive UTC until migrations (P3-1); `app/core/clock.py` replaces the deprecated `datetime.utcnow`. A browser in Europe/Warsaw now sees a 10:00 plan at 10:00 (it showed 08:00).

- [x] **P1-9 Unbounded session size** ✅ (d17e99b). `num_exercises` must be 1 to 50 (422 otherwise, nothing stored). It used to accept 0 and -5 (sessions that could never finish) and 20,000 (20,000 rows in one request). The form offers 5 to 50.

## P2: Clinically sound and aphasia-friendly

- [x] **P2-1 Clinical foundation** (c069437). `docs/clinical/README.md` and `README.pl.md`: pending clinical review; the evidence in short (Brady 2016, Big CACTUS 2019); each exercise type's current state, intended basis (cueing hierarchy, SFA, PCA, VNeST as a model, script training planned) and gaps; the content model; and the review process. Seven references, checked against publisher and repository records (full texts not read). `[citation needed]` where unsupported. `test_clinical_docs.py` keeps both languages in step.
- **P2-2 Content as data.** Split into a–c on 2026-10-15. The original ask: replace the hard-coded `EXERCISE_DATA` with versioned content files, validated at startup; each item with a concept id, PL and EN words with synonyms, semantic features, first sound and letter, a difficulty band, and image and audio assets with licenses; content tests; about 30 concepts authored natively in both languages.
  - [x] **P2-2a Naming concepts as data** (8e4218a). `backend/content/concepts.json`: 30 concepts, PL and EN, with synonyms, first sound, description and features, all pending review. Checked at startup by `app/content.py`, including no answer leak with inflected forms. Naming sessions are in the session's language; synonyms count. The difficulty bands and first sounds are author estimates; real frequency and imageability data would need a source and H1.
  - [x] **P2-2b Sentences and phrases as data** (250d1de). `sentences.json` (12 items: one gap, four grammatical options) and `phrases.json` (9), in PL and EN, checked at startup. Also fixed: options were never shuffled, and the right answer was usually first; now each exercise gets a fresh order.
  - [ ] **P2-2c Pictures and audio.** Waiting on H2/H3. When assets exist: asset ids in the content, files under `frontend/assets/`, licenses in `frontend/assets/CREDITS.md`, and a test that every referenced asset and license exists.
- **P2-3 Naming with a cueing hierarchy** (U7, C1). Split on 2026-10-15; done. A hint button steps through: meaning cue → first sound (audio) or first letter → whole word to repeat. Record the cue level for each answer, and score by independence. Since P0-6, the naming prompt shows a description of the item, because there are no pictures. That is the meaning cue given up front. Once pictures exist (H2), show the picture alone and make the description the first hint.
  - [x] **P2-3a Hints in the API** (e7b8178). `POST /therapy/exercises/{id}/hint`: 1 features (what for, where), 2 first letter, 3 the word, in the session's language. The level is stored (`exercise_cues`) and shown as `cue_level`; points keep 100/75/50/25% (pending review). The no-leak check now covers the features (three leaks fixed).
  - [x] **P2-3b The hint button** (157affb). "Hint"/"Podpowiedź" in naming exercises; hints appear as a numbered `aria-live` list; the button is off after the third; the feedback adds "Hints used: N". Later, with audio (H3), level 2 should also play the first sound.
- **P2-4 Aphasia-friendly UI pass** (U1–U5, U8, U11, U12). Split into a–f on 2026-10-15.
  - [x] **P2-4a No time pressure** (U4; 7eb6b49). No automatic move on and no visible clock; "Next"/"Dalej" (then "See my result") takes the focus after an answer, and the feedback is a `role="status"` region.
  - [x] **P2-4b In-app messages instead of `alert()` and `confirm()`** (U12; 49dad60). A message area (`ui.notify`), form messages for login and sign-up, an in-app "Leave this session?" dialog, and words for an empty answer and a blocked microphone; 20 messages in EN and PL. The e2e fixture fails any test in which a browser dialog appears.
  - [x] **P2-4c Larger text and targets** (U1, U5; 7b30886). 20 px body text, nothing under 18 px, controls at least 48×48 px, "A+" for larger text (remembered), and the language button readable in the dark theme (1.43:1 before). The header wraps on phones. `e2e/test_sizes.py` measures all of this in the browser.
  - [x] **P2-4d Read aloud on the exercise screen** (U3; 28e8d8e). For the question, each hint and the feedback, only with voices the browser reports as local (`localService`); no button without one. The privacy notice says so.
  - [ ] **P2-4d2 Read aloud elsewhere.** Instructions on the other pages (login, dashboard, account, the consent and leave dialogs) also need a read-aloud button (U3).
  - [ ] **P2-4g A compact header on phones** 🔎. Since the header controls wrap (P2-4c), the sticky header is about 200 px tall at 375 px (three rows) and covers the question. Options: move Logout to the Account page, or stop the header being sticky on small screens. Check with a screenshot and a test that the question is visible.
  - [ ] **P2-4e Language and focus.** Update `<html lang>` when the language changes, and move the focus sensibly when pages change.
  - [ ] **P2-4f Calm feedback** (U8). After a wrong answer, show the right answer (later with picture and audio), and let the person try again or move on; check the colors and copy.

- [ ] **P2-5 Forgiving answer checking** (U6). Normalize case, spacing and diacritics per language, accept synonyms from content, and give "almost" feedback for near misses. Unit tests include Polish (żółw/zolw, ł/l).
- [ ] **P2-6 Answering without typing** (U6). Offer word choice, picture choice and letter tiles; typing becomes optional.
- [ ] **P2-7 Speech practice that works** (C5). Today, recognition starts only at submit time and listens to new audio, so the recording itself is never transcribed. Redesign the flow as listen → record → play back → self-rate (plus a recognizer suggestion, with consent) → continue. Fall back gracefully where speech recognition is unsupported, and store the transcription and confidence.
- [ ] **P2-8 Adaptive difficulty and spaced repetition** (C3).
- [ ] **P2-9 Motivation that doesn't punish** (U10). The streak update in `finish_session` is read-modify-write, so two sessions finishing in the same instant could miscount it (seen in P1-10). Use weekly goals or rest days. Streak days are UTC dates, not the user's local day: practice at 00:30 in Poland counts for the day before. Use the user's time zone. Three of the six badge types (perfectionist, dedicated, master) are never awarded; implement or remove them. The first-session badge counts unfinished sessions.
- [ ] **P2-10 Full i18n** (G9). Remove the hard-coded English from JS: alerts, "Completed", "Activate"/"Deactivate", "Recording...", "Session complete", chart labels, badge names. Translate the CSV and PDF exports too. Add a key-parity test, Polish plurals (`Intl.PluralRules`) and localized dates (`Intl.DateTimeFormat`).
- [ ] **P2-11 Accessible progress chart.** Provide a data-table alternative, and scale the y-axis to 0–100% (it scales to the highest value, so a steady 80% looks like the top of the chart). The line and theme colours were fixed in P0-7f.

## P3: Engineering quality

- [ ] **P3-1** Alembic migrations instead of `create_all`.
- [ ] **P3-2** CI: a GitHub Actions workflow running `scripts/check.sh` and the e2e tests on every push and PR.
- [ ] **P3-3** Lint, format and types: `ruff format`, mypy on `app/core` and services, and a JS lint (ESLint, or at least `node --check`).
- [ ] **P3-4** Frontend as ES modules: no globals, no inline handlers. Stay with vanilla JS.
- [ ] **P3-5** Move business logic (scoring, streaks, badges, content selection) out of route handlers into testable services.
- [ ] **P3-6** `.gitignore` ignores all `*.mp3`, `*.wav` and `lib/` paths, so licensed audio assets can't be committed. Scope those rules to `uploads/`.
- [ ] **P3-7** API hygiene: a consistent error schema, pagination limits, and a `/health` that checks the DB. (Bounds for `num_exercises` moved to P1-9.)
- [ ] **P3-8** Performance: the "Inter" font is declared but never loaded; self-host it or drop it. Add a Lighthouse budget (G12).
- [ ] **P3-9** PWA: the icons referenced by `manifest.json` don't exist.
- [ ] **P3-10** Deprecation warnings in the test run ✅ (`pytest -W default`). Since P1-4, `on_event`, passlib's `crypt` and httpx's `app=` are gone (70 warnings down to 11). The list:
  - FastAPI `@app.on_event` (`main.py:65`, `:73`) → a lifespan handler.
  - pydantic class-based `Config` in 7 schemas → `model_config = ConfigDict(from_attributes=True)`.
  - SQLAlchemy `declarative_base()` (`db/database.py:14`) → `sqlalchemy.orm.declarative_base`.
  - passlib uses `crypt`, which Python 3.13 removes, and httpx's `app=` shortcut is deprecated. Both go away with P1-4.

  Then set pytest's `filterwarnings = ["error"]`, so new deprecations fail the run instead of scrolling past.

## P4: Features (only when P0–P2 are green)

- [ ] **P4-1 Therapist portal.** Assign patients, build homework plans, review recordings and per-item results (accuracy, cue level), keep notes, and export a per-patient PDF report.
- [ ] **P4-2 Personal vocabulary** (C2). Users add their own words and photos (family, home, hobbies), with privacy controls.
- [ ] **P4-3 More evidence-based exercise types**, one per backlog item, each with a clinical doc and a review flag:
  - Semantic feature analysis
  - Auditory comprehension (hear a word → pick the picture)
  - Reading comprehension
  - Repetition
  - VNeST-style verb and sentence production
  - Everyday conversation scripts
  - Yes/no reliability
- [ ] **P4-4 Reminders that actually remind.** Web Push and/or email, with consent, plus iCal export. `reminder_sent` is currently unused.
- [ ] **P4-5 Caregiver accounts** linked to a patient.
- [ ] **P4-6 Pause and resume sessions,** with an offline answer queue that syncs later.
- [ ] **P4-7 Synthetic audio for every item,** clearly labeled, as a stopgap until human recordings exist.

## Needs a human

The loop must not fake these. Write decisions or answers directly under each item.

- [ ] **H1 Clinical review.** A speech-language therapist (logopeda / neurologopeda) reviews the exercise design and every content item, in both languages.
- [ ] **H2 Images.** Licensed or commissioned, adult-appropriate, in a consistent style; ideally with name-agreement data for PL and EN.
- [ ] **H3 Audio.** Native Polish and English recordings, or an explicit decision to use synthetic voices.
- [ ] **H4 Legal.** Decide whether the intended purpose makes this a medical device under EU MDR 2017/745 (software with a therapeutic purpose can qualify), which decides what the app may claim. Also: a GDPR DPIA, a privacy policy, EU hosting, and processor agreements.
- [ ] **H5 Project facts.** The license (the README says MIT, but there is no LICENSE file), a real support contact, the domain, and hosting.
- [ ] **H6 Usability testing** with people with aphasia, carers and therapists. This is the most important input for "best in the world".
- [ ] **H7 Product decisions.** Self-registration or therapist invitation? Which kind of gamification suits this population? For P1-3b, how does a therapist get linked to a patient: the patient enters a therapist's code, the therapist invites by email, or an admin assigns? And how does the patient agree to share their results? Are a 30-minute idle timeout and a 12-hour maximum login (P1-5b) right for people who practise slowly, often on a shared family device? And are 5 wrong passwords per device and 50 per account in 15 minutes (P1-5c3) enough for someone who mistypes often?
