# Afasia: speech practice for people with aphasia

[🇵🇱 Wersja polska](README.pl.md)

A web app for practising words and sentences after a stroke or brain injury. People with aphasia use it on their own, alongside a speech-language therapist, and therapists can see who is practising. The interface is in English and Polish.

> **Status: early development. Not for clinical use.**
> The exercises are placeholders that no speech-language therapist has reviewed yet, the exercises come in Polish and English, and the gaps listed under [Known limitations](#known-limitations) remain. Progress is tracked in [`loop/BACKLOG.md`](loop/BACKLOG.md).

## What works today

Accounts, practice sessions, feedback, scores, the progress chart and the admin page are covered by automated tests (see [Development](#development)). Export, scheduling and the phone layout are not tested yet.

- **Accounts.** Sign up, log in and out, stay signed in after a reload, and change your password on the Account page. Passwords are hashed with bcrypt; logins use JWTs. A login ends after 30 minutes without using the app, and at most 12 hours after logging in.
- **Practice sessions** of 5–50 exercises, at easy, medium or hard:
  - *Word naming*: read a short description ("A pet that barks and wags its tail") and type the word.
  - *Sentence completion*: choose the word that completes a sentence.

  After each answer you see "Correct! Well done!" or the right answer. The server scores the session when the last answer arrives.
- **Progress.** Points per correct answer, daily streaks, three badges (first session, 7-day and 30-day streaks), a progress page with totals and an accuracy chart, and export as CSV or PDF.
- **Planning.** Schedule future sessions. Nothing reminds you of them yet.
- **Therapist/admin page.** See all patients and activate or deactivate accounts. Signing up always makes a patient account; staff accounts are made on the server (see [Staff accounts](#staff-accounts)).
- **Interface.** English and Polish, light and dark themes, and layouts for phones and computers.

### Not working yet

- **Pronunciation** sessions let you record yourself, but the answer is judged by the browser's own speech recognition, which doesn't work in most browsers and is unreliable for aphasic speech. It's being redesigned (backlog P2-7).
- **Image recognition** has no exercises, so the app doesn't offer it.
- **Pictures and recorded audio** don't exist yet. Naming exercises use descriptions instead.
- **Offline use** isn't supported: every exercise needs the server. The app used to install a service worker that kept old code and cached personal data; it has been retired, and `sw.js` now removes it, and its caches, from browsers that still have it.

## Quick start (development)

You need Python 3.11 and Git.

```bash
git clone <this repository>
cd Afasia

# Backend: http://localhost:8000 (API docs: http://localhost:8000/docs)
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.template ../.env     # then set SECRET_KEY: openssl rand -hex 32
python -m app.main
```

```bash
# Frontend, in a second terminal: http://localhost:3000
cd frontend
python3 -m http.server 3000
```

Open the app at `http://localhost:3000`, not `http://127.0.0.1:3000`. The login cookie comes from `localhost:8000`, and the browser only sends it back for pages on the same site (and only `localhost` origins are allowed by default).

The frontend finds the API through `frontend/js/config.js`. Its Content-Security-Policy (in `frontend/index.html`) lets the page talk only to its own origin and to local development ports, so a script injected into the page can't send data elsewhere. If you put the API on another site, add that origin to `connect-src` there. The Docker setup keeps the API on the same origin and sends a stricter policy from nginx.

The backend reads `.env` from the repository root, wherever it is started from. Settings it doesn't use are ignored, so the same file also serves Docker Compose. In development the database is SQLite (`backend/aphasia_app.db`).

## Running with Docker

You need Docker with Compose v2.

```bash
cp .env.template .env           # set SECRET_KEY and POSTGRES_PASSWORD
docker compose up --build
```

- The app: http://localhost:3000. nginx serves the frontend and passes `/api` to the backend.
- The API directly: http://localhost:8000, from this machine only. The backend trusts nginx's `X-Forwarded-For` header to tell clients apart (`FORWARDED_ALLOW_IPS`), so its port must not be reachable from elsewhere.
- Data is kept in PostgreSQL, in a Docker volume.
- `docker compose up` refuses to start without the two secrets.
- Every setting in the table below is taken from `.env`, except `DATABASE_URL`, `UPLOAD_DIR`, `HOST` and `PORT`, which the Docker setup fixes. `.env.template` turns `DEBUG` on; set `DEBUG=false` anywhere but your own machine.
- Behind a proxy that inspects TLS, set `PIP_CA_FILE` to its CA bundle so the image build can reach PyPI.

`scripts/docker-smoke.sh` builds and starts a separate copy of the stack, signs up and logs in through nginx, and then removes everything.

## Staff accounts

Signing up in the app always makes a patient account. Admin and therapist accounts are made on the server, from the `backend/` directory, with the same settings as the backend:

```bash
python -m app.cli create-user --username ada --email ada@example.com --role admin
python -m app.cli set-role tess therapist      # change an existing account's role
python -m app.cli delete-old-recordings --days 365   # delete recordings older than a year now
```

`create-user` asks for the password, which must have at least 12 characters, so it never ends up in shell history. With Docker, run the same commands as `docker compose exec backend python -m app.cli …`.

## Configuration

Copy `.env.template` to `.env` at the repository root. The settings:

| Setting | Default | Meaning |
|---|---|---|
| `SECRET_KEY` | (required) | Signs login tokens. Use at least 32 random bytes (`openssl rand -hex 32`). The app refuses to start with a shorter key or with the example from `.env.template`. |
| `DATABASE_URL` | `sqlite:///./aphasia_app.db` | Any SQLAlchemy URL, e.g. `postgresql://user:password@host/db` |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000,http://localhost:8000` | Comma-separated origins allowed to call the API |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Minutes without using the app before a login ends (the app renews the login while it is in use) |
| `LOGIN_MAX_HOURS` | `12` | Hours after logging in when a login ends anyway |
| `LOGIN_MAX_FAILURES`, `LOGIN_MAX_FAILURES_PER_ACCOUNT`, `LOGIN_LOCK_MINUTES` | `5`, `50`, `15` | Wrong passwords allowed per username from one client address, and per account from all addresses together, within that many minutes; after that, logins wait (429) |
| `RECORDING_RETENTION_DAYS` | `0` | Delete recordings older than this many days, at start-up and then daily; `0` keeps them until the person deletes them or their account. Also passed through by Docker Compose |
| `COOKIE_SECURE` | `true` | Send the login cookie over HTTPS only (browsers allow it on `http://localhost` too). Set to `false` only to test over plain HTTP on another host. |
| `DEBUG`, `HOST`, `PORT` | `false`, `0.0.0.0`, `8000` | Server options. `.env.template` turns `DEBUG` on for development (more detail in logs, and auto-reload); leave it off anywhere else |
| `UPLOAD_DIR`, `MAX_UPLOAD_SIZE` | `./uploads`, 10 MB | Where voice recordings go |
| `POSTGRES_PASSWORD`, `FRONTEND_PORT`, `BACKEND_PORT`, `PIP_CA_FILE` | | Docker Compose only |

## API

FastAPI serves interactive documentation at `/docs` and `/redoc`. All endpoints are under `/api/v1`, and all of them except sign-up, login and logout need a login. Sign-up, login and `/auth/refresh` set the token as an httpOnly `access_token` cookie (path `/api`, `SameSite=Strict`), and say when it was issued and when it ends (`issued_at`, `expires_at`). They also return it in the body, except for a renewal made through the cookie, so that page scripts never see it. Send it either as an `Authorization: Bearer <token>` header or as that cookie. Requests that change something through the cookie must also carry an `X-Requested-With` header, or they get 403; this guards against cross-site request forgery. A missing or invalid token gets 401. Times are UTC: the API sends them with `+00:00`, and takes times without an offset as UTC.

| Area | Endpoints |
|---|---|
| Accounts | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh` (renews a login), `POST /auth/logout` (ends this login on the server and removes the cookie; other devices stay logged in), `POST /users/password` (change your password: needs the current one; your other logins end, and this one gets a new token) |
| Sessions | `POST /therapy/sessions` (`num_exercises` 1 to 50; the form offers 5 to 50), `GET /therapy/sessions`, `GET /therapy/sessions/{id}`, `GET /therapy/sessions/{id}/exercises` |
| Hints | `POST /therapy/exercises/{id}/hint`: the next naming hint (1 what it is for, 2 the first letter, 3 the word); fewer points for each hint used (shares pending clinical review) |
| Answers | `POST /therapy/exercises/{id}/answer`: one answer per exercise. The response includes the right answer, and the last answer completes and scores the session. |
| Results | `POST /therapy/sessions/{id}/complete`: a finished session's server-computed result |
| You | `GET`/`PUT /users/profile`, `GET /users/progress`, `GET /users/badges`, `GET /users/progress/export/csv`, `GET /users/progress/export/pdf` |
| Planning | `GET`/`POST /users/scheduled-sessions`, `DELETE /users/scheduled-sessions/{id}` |
| Recordings | `POST /users/audio/upload` (only after consent: 403 otherwise), `GET /users/audio/{id}` |
| Your data | `GET /users/me/export`: everything stored about you as a JSON download (no password hash, no file locations); `DELETE /users/me` with `{"password": ...}`: deletes the account and everything stored about you, recording files included |
| Consent | `GET`/`PUT /users/consents`: `recordings` and `speech_recognition`, each `true`, `false` or `null` (not asked yet) |
| Admin | `GET /admin/stats`, `GET /admin/users`, `GET /admin/users/{id}/sessions`, `PUT /admin/users/{id}/activate`, `PUT /admin/users/{id}/deactivate` |

`GET /health` answers without logging in; `GET /health/detailed` also checks the database (503 when it can't reach it) and shows no settings.

## Project structure

```
backend/          FastAPI app (app/), tests (tests/), requirements
frontend/         index.html, css/, js/ (plain JavaScript, no build step), nginx.conf
e2e/              Browser tests (Playwright)
scripts/          check.sh (all checks), smoke.sh (README quick start), docker-smoke.sh
docs/             User guides (English and Polish)
loop/             The improvement loop: rules, backlog, log
docker-compose.yml, .env.template
```

## Development

```bash
scripts/check.sh
```

This is the one check that must pass before every commit. It sets up its own environment (`.venv-check`) and runs:
- the linter;
- a check of the backend's dependencies for known vulnerabilities (pip-audit);
- the backend tests;
- the quick start above, in a scratch copy of the repository;
- the browser tests, which cover signing up, whole sessions in English and Polish, feedback, the progress chart and the admin page.

Contributions: open an issue or a pull request. Keep `scripts/check.sh` green, add a test for every change, and update this README and [the Polish one](README.pl.md) together.

The app is improved in small, tested steps by a documented loop. See [`loop/README.md`](loop/README.md).

## Known limitations

Before anyone relies on this app, at least these must be fixed. Each one is in [`loop/BACKLOG.md`](loop/BACKLOG.md).

- **Security**
  - There is no "forgot password" reset, and no way to log out on all devices at once without changing the password.
  - The limits on wrong passwords are kept in memory: each server process counts on its own, and a restart forgets them. Behind a proxy, clients are told apart only if the server trusts the proxy's `X-Forwarded-For` (the Docker setup does); otherwise everyone shares one count per username. Whether 5 and 50 suit people with aphasia is an open question (backlog H7).
- **Privacy:** recordings and speech recognition need the person's consent, asked in the app. People can download or delete all their data on the Account page. The privacy notice (`frontend/privacy.html`, EN and PL, linked from the login and Account pages) describes what the code does; who runs the app, the legal basis, where it is hosted and whom to contact are marked "[to be completed]" until someone decides them (backlog H4, H5). The app stores health information.
- **Roles:** any therapist can see and deactivate every patient. Therapists aren't linked to their own patients yet (P1-3b).
- **Clinical content:** in Polish and English, in `backend/content/` and checked when the app starts: 30 naming concepts, 12 sentences to complete and 9 phrases to repeat. All are placeholders, not reviewed by a speech-language therapist. There are no pictures or recordings. What each exercise type should be based on, with checked references, is in [`docs/clinical/README.md`](docs/clinical/README.md), also pending clinical review.
- **Accessibility** has not been audited, and the aphasia-friendly design rules in [`loop/PROMPT.md`](loop/PROMPT.md) are not met yet. For example, read-aloud covers only the exercise screen, and only where the device has a voice of its own for the language.
- **Legal:** whether the app counts as a medical device under EU rules has not been assessed.
- **Delivery:** there is no continuous integration yet.

## License

No license has been chosen yet. Until one is, all rights are reserved by the authors.
