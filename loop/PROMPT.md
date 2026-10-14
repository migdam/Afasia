# Improvement loop: instructions for ONE iteration

You are improving **Afasia**, a bilingual (Polish/English) speech-therapy web app for people with aphasia: FastAPI backend in `backend/`, vanilla HTML/CSS/JS frontend in `frontend/`.

Each time you are invoked, carry out **exactly one iteration** of the protocol below, then stop. Iterations may run in fresh sessions with no memory, so everything you need lives in this repo: this file, `loop/BACKLOG.md`, `loop/LOG.md`, and git history.

If `loop/DONE` exists, reply "Loop complete, see loop/DONE" and do nothing else.

## North star

We are building the best aphasia practice app we can. In priority order, that means:

1. **It works.** Every documented flow works end to end, proven by automated tests, never by assumption.
2. **It is safe.** It holds health data of vulnerable people (special-category data under GDPR art. 9). Security and privacy defects outrank features.
3. **It is clinically sound.** Exercises follow established aphasia-therapy practice (see "Clinical principles"). Never invent clinical claims or references.
4. **People with aphasia can use it.** Aphasia-friendly and accessible (see "Aphasia-friendly UX" and WCAG 2.2 AA).
5. **It is honest.** The UI and docs describe exactly what exists. No "production-ready", compliance, performance or efficacy claims unless a check in this repo proves them.

"Best" is measured by the quality gates at the end of this file, not by feature count. A smaller app that works beats a bigger one that doesn't.

## The protocol

### 1. Orient (read only)
- `git status`, `git branch --show-current`, `git log --oneline -15`.
- Read the newest entries in `loop/LOG.md` and all of `loop/BACKLOG.md`. Humans may edit the backlog (reorder items, add items, answer "Needs a human" questions); their edits override your plans.
- If humans committed since the last log entry, read those commits and respect them.
- On `main`/`master` or a detached HEAD: stop, and log that the loop must run on a feature branch.
- Dirty working tree left by an interrupted iteration: if the change is coherent and you can verify it, finish it as this iteration's task. Otherwise run `git stash push -u -m "loop: abandoned work <date>"` and log it. Never discard work with `git reset --hard`, `git checkout -- .` or `git clean`.

### 2. Baseline
Run `scripts/check.sh` (the single verification entry point; exit code 0 = green). Record the result. If something that was green in the last log entry is now red, fixing that regression is this iteration's task.
`scripts/check.sh` doesn't exist until backlog item P0-1 creates it, so until then, P0-1 is the task.

### 3. Pick one task
- Take the highest-priority unchecked, unblocked item in `loop/BACKLOG.md`: all of P0 before P1, and so on; within a priority, top to bottom.
- If it is too big to finish and verify in one iteration (roughly an hour of focused work), split it into smaller items in the backlog and take the first one.
- Search the code before implementing. Don't assume something is missing or broken; confirm it. Reproduce bugs first (failing test or command output).
- If no backlog item is actionable: audit the gate that is furthest from green (or do a fresh pass on security, accessibility, clinical content, or docs-vs-reality) and add concrete, evidenced findings to the backlog. If the audit finds nothing worth doing, write `loop/DONE` (date, gate status, reason), log it, commit, and stop. Never make cosmetic churn to look busy.

### 4. Do the work
- Write or extend a test that fails before your change and passes after it. For UI work, that's an end-to-end test.
- Keep the diff focused on the one task. No drive-by reformatting or restructuring.
- Match the surrounding code style. Keep the stack (FastAPI + vanilla JS, no frontend framework, no rewrite) unless a human decides otherwise in the backlog.
- Prefer boring, maintained dependencies; pin them; justify every new one in the commit message.
- Content (exercise items, UI text) is authored natively for each language. Polish must be grammatical Polish (cases, gender agreement, plurals), not a word-for-word translation of English.

### 5. Verify
- Run `scripts/check.sh`. All of it must pass.
- UI changes: run the end-to-end tests, and check both languages and both themes.
- Paste the decisive output lines (test counts, coverage, audit results) into the log entry. "It should work" is not evidence.
- If you can't get to green in this iteration: stash your code changes (`git stash push -u -m "loop: <item id> <reason>"`), mark the item `[!]` with the reason in the backlog, add the log entry, then commit and push only those two files (`docs(loop): <item id> blocked`), and stop. Never commit a red build. Never weaken, skip or delete a test to make it pass unless the test itself is wrong; if it is, say so in the commit message.

### 6. Update docs and state
- If behavior changed, update `README.md` **and** `README.pl.md` (and `docs/` guides) to match. Both languages carry the same content.
- In `loop/BACKLOG.md`: tick the item with the commit hash (`- [x] **P0-3** … (abc1234)`), update the gate table, and add any new problems you discovered, with evidence, at the right priority.
- Add an entry at the top of `loop/LOG.md` using its template.

### 7. Commit and push
- Commit message: `type(scope): summary`, where type is one of feat, fix, sec, a11y, content, i18n, test, docs, chore, refactor. The body says what changed, why, and how it was verified.
- Push the current branch: `git push -u origin <branch>`. On network errors, retry up to 4 times, waiting 2 s, 4 s, 8 s and 16 s.
- Never force-push, rewrite pushed history, delete branches, or push to any other branch.

Then stop. One iteration = one task = one commit (or a few small ones).

## Hard rules

- Never commit secrets, `.env`, databases, real patient data, or uploaded recordings.
- **Never fabricate.** That means no invented contact details, testimonials, metrics, citations, clinical-validation or compliance claims, and no "native speaker" or "therapist-approved" labels on content that isn't. Cite only sources you have actually verified; otherwise write `[citation needed]`.
- Some things need a human: licensed images, recorded voices, clinical review, legal decisions, hosting, accounts and money. List them under "Needs a human" in the backlog, build the code path with clearly labeled placeholders, and move on to other work.
- Use only assets whose license allows it, and record source and license for each one in `frontend/assets/CREDITS.md`.
- Don't edit `loop/PROMPT.md`. If you think the protocol should change, propose it in your log entry.
- Out of scope: deploying, opening or merging PRs, publishing packages, sending emails or messages, creating external accounts.

## Clinical principles

- **C1 Evidence-based tasks only.** Model exercise types on established approaches, for example cueing hierarchies for naming, Semantic Feature Analysis, Phonological Components Analysis, Verb Network Strengthening Treatment (VNeST), script training, repetition, and auditory or reading comprehension (word–picture matching). Document each type's basis with verified references in `docs/clinical/` (EN and PL).
- **C2 Personal vocabulary.** In the Big CACTUS trial (Palmer et al., *Lancet Neurology* 2019), self-managed computerized word-finding practice improved naming of words chosen for each person, but did not improve conversation. Patients, carers and therapists must be able to add their own words and photos, and the app must not claim conversational gains.
- **C3 Keep success high.** Adapt difficulty to performance and bring missed items back with spaced repetition. Make the thresholds configurable, with defaults confirmed by a speech-language therapist.
- **C4 No answer leakage.** A prompt never contains its answer (repetition tasks excepted), and a test enforces this.
- **C5 Speech recognition is unreliable for aphasic or dysarthric speech.** Never make it the sole judge: offer self-rating or therapist review, and always let the user continue.
- **C6 Support, not replacement.** The app supports work with a speech-language therapist (logopeda / neurologopeda). No medical or efficacy claims anywhere.
- **C7 Review gate.** New or changed content is marked "pending clinical review" until a qualified human signs it off (tracked under "Needs a human").

## Aphasia-friendly UX

- **U1** Body text ≥ 18 px (default 20 px), line height ≥ 1.5, short plain sentences, key words emphasized. Users can enlarge text.
- **U2** One task per screen. Consistent layout. Every icon has a text label.
- **U3** Every instruction and prompt has a "read aloud" button (speech synthesis in the selected language).
- **U4** No time pressure: no visible countdown by default and no auto-advance. The user moves on when ready (WCAG 2.2.1).
- **U5** Targets ≥ 48×48 px with spacing. Everything works one-handed (including left hand only) and by keyboard. No drag-only or double-tap-only interactions.
- **U6** Answering never requires typing: offer word choice, picture choice, letter tiles, or speech; typing is optional. Answer checks ignore case, spacing and missing Polish diacritics (żółw = zolw) and accept listed synonyms.
- **U7** Help before failure. A hint button steps through a cueing hierarchy: meaning cue → first sound/letter → whole word to repeat. Hints are recorded, not punished.
- **U8** Calm, adult feedback, with no alarm colors or shaming copy. After an error, show the right answer with picture and audio, then let the user try again or move on.
- **U9** Short sessions by default (about 5–10 items). Users can pause and resume. Progress is never lost on refresh or logout.
- **U10** Motivation without punishment: weekly goals or streaks with rest days. Never shame a missed day, since people get ill and go to hospital.
- **U11** Respectful, adult-appropriate imagery and tone, never childish.
- **U12** Errors and empty states are explained in plain words with a clear next step. No `alert()` or `confirm()` popups.

## Quality gates

Track each gate's status and evidence in the gate table in `loop/BACKLOG.md`. A gate is green only when the check has actually been run and its output recorded in the log.

| Gate | Definition of green |
|------|---------------------|
| G1 Runs | `scripts/check.sh` passes; the README quick start works from a clean clone (scripted smoke test). |
| G2 Backend tests | pytest green with ≥ 85% line coverage of `backend/app`. |
| G3 End-to-end | Playwright covers register/login → every exercise type → feedback → progress → export, in PL and EN. |
| G4 Authorization | Tests prove users can't read or change others' data, therapists see only assigned patients, and admins are created explicitly. |
| G5 Security | `pip-audit` clean; no untrusted data reaches `innerHTML`; CSP without `unsafe-inline` scripts; recordings only via authenticated endpoints; secrets only from the environment; login rate-limited. |
| G6 Accessibility | axe-core: 0 serious or critical violations on every screen, both themes, both languages; fully keyboard-operable. |
| G7 Aphasia-friendly | U1–U12 all met, each backed by a test where feasible. |
| G8 Clinical content | Every item exists natively in PL and EN with image, audio, license, cue levels and no answer leak (content tests). SLP review is a human gate. |
| G9 i18n | No hard-coded user-facing strings; PL/EN key-parity test; Polish plurals and dates via `Intl`. |
| G10 Privacy | Users can export and delete their data; consent before recording or sending audio to any third party; retention for recordings; no third-party requests without consent; privacy notice in PL and EN. |
| G11 Honest docs | README(s) and guides describe only what exists; known limitations listed; every link resolves. |
| G12 Lighthouse | Mobile: Accessibility 100, Performance ≥ 90, Best Practices ≥ 95, measured and recorded. |
| G13 Delivery | CI runs the checks and end-to-end tests on every push; the Docker Compose stack starts and passes the smoke test. |
