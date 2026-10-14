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
| G1 Runs | 🔴 | Backend fails at import (P0-2) |
| G2 Backend tests | 🔴 | No tests exist |
| G3 End-to-end | 🔴 | No e2e tests |
| G4 Authorization | 🔴 | P1-3 |
| G5 Security | 🔴 | P1-1, P1-2, P1-4 |
| G6 Accessibility | 🔴 | Not measured |
| G7 Aphasia-friendly | 🔴 | Auto-advance, visible timer, typing required (P2-4..P2-6) |
| G8 Clinical content | 🔴 | English-only, answers leak, assets missing |
| G9 i18n | 🔴 | Hard-coded English strings in JS (P2-10) |
| G10 Privacy | 🔴 | P1-6 |
| G11 Honest docs | 🔴 | P0-9 |
| G12 Lighthouse | 🔴 | Not measured |
| G13 Delivery | 🔴 | No CI; Docker stack untested (P0-8) |

## P0: Make it run

- [ ] **P0-1 Verification harness.** Create `scripts/check.sh` as the single entry point (exit 0 = green). It creates or reuses `backend/.venv`, installs `requirements.txt` plus a new `requirements-dev.txt` (pytest, pytest-cov, httpx, ruff, pip-audit), then runs `ruff check` and `pytest`. Add `.venv/` to `.gitignore`. First tests: the app imports, and `GET /health` returns 200. This item is done when the harness works, even if its first run is red because of P0-2. Later items extend `check.sh` (coverage, pip-audit, e2e).
- [ ] **P0-2 Backend can't start** ✅. There are three import-time crashes, each hidden behind the previous one:
  1. `app/core/config.py`: the `BACKEND_CORS_ORIGINS` validator turns the string into a list, which the `str` field then rejects (`Input should be a valid string`). This happens even with defaults, so the app never starts. Two related problems:
     - The README says to copy the template to the repo root (`cp ../.env.template ../.env`), but settings read `.env` from the working directory (`backend/`), so `SECRET_KEY` is reported missing.
     - Putting `.env` in `backend/` fails too, because `.env.template` contains `SMTP_*` keys that Settings forbids (`Extra inputs are not permitted`).
  2. `app/db/models.py`: `UserBadge.metadata` is reserved by SQLAlchemy Declarative (`Attribute name 'metadata' is reserved`).
  3. `app/api/v1/schemas.py`: `EmailStr` needs `email-validator`, which is missing from requirements.

  **Acceptance:** following the README exactly, `uvicorn app.main:app` starts and `/health` returns 200. Tests cover settings parsing: a comma-separated CORS env var, the `.env` location, and unknown keys.
- [ ] **P0-3 Every authenticated request returns 401** ✅. Registration (201) and login (200) work, but the token they return is rejected: tokens are created with an integer `sub`, and python-jose refuses non-string subjects on decode. Fix it by encoding `str(user.id)` and parsing it back. While here:
  - Replace python-jose (unmaintained, has published advisories) with PyJWT.
  - Return 401, not 403, for missing or invalid tokens.

  **Acceptance:** tests for register → login → `GET /users/profile` = 200, and for a bad or missing token = 401.
- [ ] **P0-4 Sessions never complete, so there are no points, progress, streaks or badges** ✅. In `submit_answer`, the "all answered?" count runs before the current answer is flushed (`autoflush=False`). Reproduced: after answering 3/3 correctly, the session shows `completed_exercises=2`, is not completed, has 0 points and no progress record. Re-submitting any answer then "completes" it, and every re-submit awards points again and adds another progress record (10 → 20 points, 1 → 2 records). Further problems in the same flow:
  - Points are computed only for the last answer, not the session.
  - The progress record is written before the duration is known, so time is always 0.
  - `POST /sessions/{id}/complete` overwrites the server-computed score with whatever the client sends.

  **Acceptance:** tests for completion on the last answer, points summed over correct answers, idempotent re-submission (no double points or records), server-only scoring, and a recorded duration.
- [ ] **P0-5 Image-recognition sessions hang the server** ✅. `EXERCISE_DATA` has no `image_recognition` content, and `generate_exercises` loops forever on an empty pool. Reproduced: still spinning after 3 s, pinning a worker thread at 100% CPU. Fail fast with a clear 4xx when there is no content, and add a test.
- [ ] **P0-6 Naming prompts contain the answer** ✅. For example, `"What is this? (cat)"` has the answer `cat`. Fix the naming prompts, and add a test that no naming prompt contains its answer (C4). Repetition prompts like "Say: Hello" are fine. The full content model is P2-2.
- [ ] **P0-7 Frontend flow is broken against the real API** 🔎:
  - The final score is always 0%: `completeSession()` counts `is_correct` on the exercise list fetched at session start (all `null`) and POSTs that score, which the server accepts (P0-4).
  - Wrong-answer feedback reads "Incorrect. Try again! Correct! Well done!: undefined". It concatenates both messages and reads `correct_answer`, a field the API never returns (✅ confirmed absent).
  - Submit stays enabled during the 2 s feedback delay, so a double click submits twice and skips an exercise.
  - `recordedAudio` and the hidden text input aren't reset between exercises or sessions.
  - The admin list reads `user.is_active`, which `UserResponse` doesn't include.
  - The dashboard badge count only updates after visiting Progress.
  - `API_BASE_URL` is hard-coded to `http://localhost:8000`.
  - The images and audio that exercises reference (`/assets/images/*.jpg`, `/assets/audio/*.mp3`) don't exist.
  - The progress chart draws dots but no line (`beginPath()` inside the path loop), the canvas has no height, and its colors are hard-coded for the light theme.

  **Acceptance:** a Playwright e2e test, in EN and PL: register → one session per working exercise type → correct feedback → progress shows the session with the right score.
- [ ] **P0-8 Docker stack** 🔎:
  - No PostgreSQL driver in requirements, so the backend can't connect to the compose `db` service.
  - DB password and secret fallback are hard-coded in `docker-compose.yml`.
  - The frontend calls `localhost:8000`, which only works on the developer's own machine. Proxy `/api` through nginx instead.

  **Acceptance:** `docker compose up` passes the smoke test. If Docker can't run in the loop's environment, mark the item `[!]` and say so.
- [ ] **P0-9 Docs claim things that aren't true** 🔎. 27 matches across `README.md`, `README.pl.md`, `README_IMPLEMENTATION.md` and `docs/USER_GUIDE.md` for claims that are false or unverified:
  - "production-ready", WCAG 2.1 AA compliance, Lighthouse and performance numbers, CSRF protection, rate limiting.
  - Native-speaker recordings, calendar integration, leaderboards, background sync, a "Schedule Next Session" button.
  - Badges that are never awarded.
  - Links to `docs/API.md`, `docs/DEPLOYMENT.md` and `LICENSE`, none of which exist.
  - Invented contact details: `support@aphasia-therapy.app`, `@AphasiaTherapy`, a website.

  Replace them with an accurate status ("early development"), a "Known limitations" section, and links that resolve, in both languages.

## P1: Safety (security, privacy, data integrity)

- [ ] **P1-1 Stored XSS into the therapist/admin dashboard** 🔎. Usernames, emails, session and schedule titles, and exercise options go into `innerHTML` (`frontend/js/ui.js`, `frontend/js/app.js`). Usernames have no validation, so a patient can register a username containing HTML/JS that runs in a therapist's browser, where the JWT sits in `localStorage`. Fixes:
  - Render with `textContent` or DOM APIs.
  - Remove the inline `onclick=` handlers.
  - Move the inline service-worker script into a file.
  - Add a strict Content-Security-Policy.

  **Test:** an e2e test with a malicious username shows it as plain text.
- [ ] **P1-2 Voice recordings are served without authentication** 🔎. `main.py` mounts the upload directory at `/uploads` with `StaticFiles`, so recordings of patients' speech can be fetched by anyone with the URL. Fixes:
  - Remove the mount, and serve recordings only through the authenticated, ownership-checked endpoint.
  - Use random (uuid) file names, stored outside any web root.
  - In the upload endpoint, enforce `MAX_UPLOAD_SIZE` (defined but unused; the whole file is read into memory) and check the content type.
  - Store the real format: MediaRecorder produces webm/ogg, but files are saved as `.wav`.
  - Check that the exercise belongs to the user.
- [ ] **P1-3 Therapist and admin model** 🔎. Any therapist can see and deactivate every patient, and there is no way to create a therapist or admin account at all. Add:
  - Therapist–patient assignment (invite plus consent).
  - An admin bootstrap command (`python -m app.cli create-admin`).
  - Authorization tests for every endpoint (G4).
- [ ] **P1-4 Dependency health** 🔎. Pins date from late 2023: fastapi 0.104 / starlette 0.27, python-multipart 0.0.6, python-jose 3.3.0, and passlib 1.7.4, which is unmaintained (it prints a warning with the bcrypt 5.0.0 that pip resolves today). Some of these have published security advisories. Upgrade to current supported versions, drop the unused matplotlib and pillow, and add `pip-audit` to `check.sh` (it must come back clean).
- [ ] **P1-5 Login sessions that fit the users** 🔎. Tokens last 30 minutes with no refresh, so people get logged out mid-exercise and lose the session; the JWT also lives in `localStorage`. Fixes:
  - httpOnly, Secure, SameSite cookies with CSRF protection, or refresh tokens.
  - An idle timeout suited to slow, effortful use.
  - Rate-limited login.
  - A minimum password length.
- [ ] **P1-6 Privacy (GDPR: health data is special-category)** 🔎:
  - A privacy notice in PL and EN.
  - Explicit consent before recording audio, and before browser speech recognition, which can send audio to the browser vendor's cloud.
  - Data export (JSON) and account deletion for the user.
  - A retention policy for recordings.
  - No third-party requests without consent, and no PII in logs.
- [ ] **P1-7 Users would never receive fixes** 🔎. The service worker serves app code cache-first, and nginx marks JS/CSS `immutable` for a year without hashed filenames. Switch app code to network-first, or to stale-while-revalidate with versioned assets. Never cache API responses containing personal data. Either build real offline support or remove the offline claims.
- [ ] **P1-8 Safe defaults** 🔎:
  - `DEBUG` defaults to true.
  - The app should refuse to start with the template `SECRET_KEY` outside development.
  - `/health/detailed` exposes configuration.
  - Datetimes are naive (`datetime.utcnow()`, deprecated in Python 3.12).

## P2: Clinically sound and aphasia-friendly

- [ ] **P2-1 Clinical foundation.** Write `docs/clinical/README.md` and `docs/clinical/README.pl.md` covering the evidence-based approach behind each exercise type (with verified references), the content model, and the review process. Mark everything "pending clinical review" (C1, C7).
- [ ] **P2-2 Content as data.** Replace the hard-coded `EXERCISE_DATA` with versioned content files (e.g. `content/items/*.json`), validated at startup. Each item has:
  - A concept id, and the PL and EN word with accepted synonyms.
  - Semantic features: category, use, location, description.
  - The first sound and letter per language.
  - A difficulty band (frequency, length, imageability).
  - Image and audio asset ids, with licenses in `frontend/assets/CREDITS.md`.

  Content tests check that both languages are present, no answer leaks, and every asset and license exists. Seed about 30 everyday, picturable concepts, authored natively in Polish and English. Exercises currently ignore the session's language and are English-only.
- [ ] **P2-3 Naming with a cueing hierarchy** (U7, C1). A hint button steps through: meaning cue → first sound (audio) or first letter → whole word to repeat. Record the cue level for each answer, and score by independence.
- [ ] **P2-4 Aphasia-friendly UI pass** (U1–U5, U8, U11, U12):
  - Larger type and touch targets.
  - Remove the 2 s auto-advance and the visible timer.
  - A read-aloud button for every instruction (SpeechSynthesis, PL/EN).
  - Accessible dialogs instead of `alert()` and `confirm()`.
  - `aria-live` feedback and proper focus management.
  - Update `<html lang>` when the language changes.
  - Calm feedback copy.
- [ ] **P2-5 Forgiving answer checking** (U6). Normalize case, spacing and diacritics per language, accept synonyms from content, and give "almost" feedback for near misses. Unit tests include Polish (żółw/zolw, ł/l).
- [ ] **P2-6 Answering without typing** (U6). Offer word choice, picture choice and letter tiles; typing becomes optional.
- [ ] **P2-7 Speech practice that works** (C5). Today, recognition starts only at submit time and listens to new audio, so the recording itself is never transcribed. Redesign the flow as listen → record → play back → self-rate (plus a recognizer suggestion, with consent) → continue. Fall back gracefully where speech recognition is unsupported, and store the transcription and confidence.
- [ ] **P2-8 Adaptive difficulty and spaced repetition** (C3).
- [ ] **P2-9 Motivation that doesn't punish** (U10). Use weekly goals or rest days. Three of the six badge types (perfectionist, dedicated, master) are never awarded; implement or remove them. The first-session badge counts unfinished sessions.
- [ ] **P2-10 Full i18n** (G9). Remove the hard-coded English from JS: alerts, "Completed", "Activate"/"Deactivate", "Recording...", "Session complete", chart labels, badge names. Translate the CSV and PDF exports too. Add a key-parity test, Polish plurals (`Intl.PluralRules`) and localized dates (`Intl.DateTimeFormat`).
- [ ] **P2-11 Accessible progress chart.** Draw the line correctly, use theme-aware colors, and provide a data-table alternative.

## P3: Engineering quality

- [ ] **P3-1** Alembic migrations instead of `create_all`.
- [ ] **P3-2** CI: a GitHub Actions workflow running `scripts/check.sh` and the e2e tests on every push and PR.
- [ ] **P3-3** Lint, format and types: `ruff format`, mypy on `app/core` and services, and a JS lint (ESLint, or at least `node --check`).
- [ ] **P3-4** Frontend as ES modules: no globals, no inline handlers. Stay with vanilla JS.
- [ ] **P3-5** Move business logic (scoring, streaks, badges, content selection) out of route handlers into testable services.
- [ ] **P3-6** `.gitignore` ignores all `*.mp3`, `*.wav` and `lib/` paths, so licensed audio assets can't be committed. Scope those rules to `uploads/`.
- [ ] **P3-7** API hygiene: server-side bounds for `num_exercises`, a consistent error schema, pagination limits, and a `/health` that checks the DB.
- [ ] **P3-8** Performance: the "Inter" font is declared but never loaded; self-host it or drop it. Add a Lighthouse budget (G12).
- [ ] **P3-9** PWA: the icons referenced by `manifest.json` don't exist.

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
- [ ] **H7 Product decisions.** Self-registration or therapist invitation? Which kind of gamification suits this population?
