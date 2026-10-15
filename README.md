# Afasia: speech practice for people with aphasia

[🇵🇱 Wersja polska](README.pl.md)

A web app for practising words and sentences after a stroke or brain injury. People with aphasia use it on their own, alongside a speech-language therapist, and therapists can see who is practising. The interface is in English and Polish.

> **Status: early development. Not for clinical use.**
> The exercises are placeholders that no speech-language therapist has reviewed yet, the exercise content is English-only, and the security work listed under [Known limitations](#known-limitations) is not done. Progress is tracked in [`loop/BACKLOG.md`](loop/BACKLOG.md).

## What works today

Accounts, practice sessions, feedback, scores, the progress chart and the admin page are covered by automated tests (see [Development](#development)). Export, scheduling and the phone layout are not tested yet.

- **Accounts.** Sign up, log in and out, and stay signed in after a reload. Passwords are hashed with bcrypt; logins use JWTs that expire after 30 minutes.
- **Practice sessions** of 5–50 exercises, at easy, medium or hard:
  - *Word naming*: read a short description ("A pet that barks and wags its tail") and type the word.
  - *Sentence completion*: choose the word that completes a sentence.

  After each answer you see "Correct! Well done!" or the right answer. The server scores the session when the last answer arrives.
- **Progress.** Points per correct answer, daily streaks, three badges (first session, 7-day and 30-day streaks), a progress page with totals and an accuracy chart, and export as CSV or PDF.
- **Planning.** Schedule future sessions. Nothing reminds you of them yet.
- **Therapist/admin page.** See all patients and activate or deactivate accounts. There is no way to create an admin or therapist account in the app yet: an existing user's `role` has to be changed in the database.
- **Interface.** English and Polish, light and dark themes, and layouts for phones and computers.

### Not working yet

- **Pronunciation** sessions let you record yourself, but the answer is judged by the browser's own speech recognition, which doesn't work in most browsers and is unreliable for aphasic speech. It's being redesigned (backlog P2-7).
- **Image recognition** has no exercises, so the app doesn't offer it.
- **Pictures and recorded audio** don't exist yet. Naming exercises use descriptions instead.
- **Offline use.** A service worker caches the app's files, but every exercise needs the server.

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

The backend reads `.env` from the repository root, wherever it is started from. Settings it doesn't use are ignored, so the same file also serves Docker Compose. In development the database is SQLite (`backend/aphasia_app.db`).

## Running with Docker

You need Docker with Compose v2.

```bash
cp .env.template .env           # set SECRET_KEY and POSTGRES_PASSWORD
docker compose up --build
```

- The app: http://localhost:3000. nginx serves the frontend and passes `/api` to the backend.
- The API directly: http://localhost:8000.
- Data is kept in PostgreSQL, in a Docker volume.
- `docker compose up` refuses to start without the two secrets.
- Behind a proxy that inspects TLS, set `PIP_CA_FILE` to its CA bundle so the image build can reach PyPI.

`scripts/docker-smoke.sh` builds and starts a separate copy of the stack, signs up and logs in through nginx, and then removes everything.

## Configuration

Copy `.env.template` to `.env` at the repository root. The settings:

| Setting | Default | Meaning |
|---|---|---|
| `SECRET_KEY` | (required) | Signs login tokens. Use at least 32 random bytes (`openssl rand -hex 32`). |
| `DATABASE_URL` | `sqlite:///./aphasia_app.db` | Any SQLAlchemy URL, e.g. `postgresql://user:password@host/db` |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000,http://localhost:8000` | Comma-separated origins allowed to call the API |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | How long a login lasts |
| `DEBUG`, `HOST`, `PORT` | `true`, `0.0.0.0`, `8000` | Server options |
| `UPLOAD_DIR`, `MAX_UPLOAD_SIZE` | `./uploads`, 10 MB | Where voice recordings go |
| `POSTGRES_PASSWORD`, `FRONTEND_PORT`, `BACKEND_PORT`, `PIP_CA_FILE` | | Docker Compose only |

## API

FastAPI serves interactive documentation at `/docs` and `/redoc`. All endpoints are under `/api/v1`, and all of them except sign-up and login need an `Authorization: Bearer <token>` header. A missing or invalid token gets 401.

| Area | Endpoints |
|---|---|
| Accounts | `POST /auth/register`, `POST /auth/login` |
| Sessions | `POST /therapy/sessions`, `GET /therapy/sessions`, `GET /therapy/sessions/{id}`, `GET /therapy/sessions/{id}/exercises` |
| Answers | `POST /therapy/exercises/{id}/answer`: one answer per exercise. The response includes the right answer, and the last answer completes and scores the session. |
| Results | `POST /therapy/sessions/{id}/complete`: a finished session's server-computed result |
| You | `GET`/`PUT /users/profile`, `GET /users/progress`, `GET /users/badges`, `GET /users/progress/export/csv`, `GET /users/progress/export/pdf` |
| Planning | `GET`/`POST /users/scheduled-sessions`, `DELETE /users/scheduled-sessions/{id}` |
| Recordings | `POST /users/audio/upload`, `GET /users/audio/{id}` |
| Admin | `GET /admin/stats`, `GET /admin/users`, `GET /admin/users/{id}/sessions`, `PUT /admin/users/{id}/activate`, `PUT /admin/users/{id}/deactivate` |

`GET /health` answers without logging in.

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
- the backend tests;
- the quick start above, in a scratch copy of the repository;
- the browser tests, which cover signing up, whole sessions in English and Polish, feedback, the progress chart and the admin page.

Contributions: open an issue or a pull request. Keep `scripts/check.sh` green, add a test for every change, and update this README and [the Polish one](README.pl.md) together.

The app is improved in small, tested steps by a documented loop. See [`loop/README.md`](loop/README.md).

## Known limitations

Before anyone relies on this app, at least these must be fixed. Each one is in [`loop/BACKLOG.md`](loop/BACKLOG.md).

- **Security**
  - Voice recordings can be downloaded by anyone who knows their address (P1-2).
  - Logins aren't rate-limited, and tokens are kept in `localStorage` (P1-5).
  - Some dependencies are outdated (P1-4).
- **Privacy:** there is no privacy notice, no consent step before recording, and no way to export or delete your data (P1-6). The app stores health information.
- **Roles:** any therapist can see every patient, and there is no way to create staff accounts (P1-3).
- **Clinical content:** a handful of English placeholder exercises, not reviewed by a speech-language therapist. There are no pictures or recordings.
- **Accessibility** has not been audited, and the aphasia-friendly design rules in [`loop/PROMPT.md`](loop/PROMPT.md) are not met yet. For example, the app still moves on automatically after 2 seconds.
- **Legal:** whether the app counts as a medical device under EU rules has not been assessed.
- **Delivery:** there is no continuous integration yet.

## License

No license has been chosen yet. Until one is, all rights are reserved by the authors.
