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

**Scoring, with the JWT subject also patched to a string** (bcrypt pinned below 4.1 for this run, though 5.0.0 also registered fine):
```
answer response includes correct_answer: False
is_correct stored: [True, True, True]
after 3 answers: completed_exercises=2 is_completed=False score=0.0 points=0 progress_records=0
after re-submitting 1 answer: completed_exercises=3 is_completed=True score=100.0 points=10 progress_records=1
after re-submitting again: points=20 progress_records=2
```

- **Not a blocker:** bcrypt 5.0.0 with passlib 1.7.4. Registration works; passlib only prints a warning.
- **Did:** wrote `loop/PROMPT.md`, `loop/BACKLOG.md`, `loop/LOG.md`, `loop/README.md` and `loop/run.sh`. No app code changed.
- **Next:** P0-1, then P0-2.
