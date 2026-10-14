# Improvement loop

These files turn Claude Code into a loop that improves the app one verified step at a time. Each iteration, Claude:

1. reads the rules in `PROMPT.md` and the work queue in `BACKLOG.md`;
2. takes the top unblocked item, reproduces the problem, and fixes it with a test;
3. runs `scripts/check.sh` and refuses to commit anything that fails;
4. writes what it did, and the proof, in `LOG.md`;
5. commits and pushes the branch you're on.

The backlog starts with the blockers that were reproduced on 2026-10-14 (the backend currently doesn't start). Next come security and privacy, then clinical and accessibility work, then features. "Finished" is defined by 13 measurable quality gates at the end of `PROMPT.md`, not by a feature count.

## Start it

**Inside Claude Code** (CLI, desktop, or the Claude app):

```
/loop Read loop/PROMPT.md and carry out exactly one iteration.
```

**Headless from a terminal.** Each iteration is a fresh `claude -p` session:

```
loop/run.sh 5      # at most 5 iterations
```

## Stop it

- **`run.sh`:** `touch loop/STOP` stops it after the current iteration; Ctrl-C stops it immediately.
- **Automatically:** when nothing worthwhile is left, the loop writes `loop/DONE` and stops. Delete that file to restart.

## Steer it

- **Change priorities:** edit `BACKLOG.md` to reorder or add items. Your edits override the loop's plans.
- **Unblock it:** answer the items under "Needs a human" in `BACKLOG.md` (images, voice recordings, clinical review, legal questions). The loop builds placeholders around them and never fakes them.
- **See what happened:** `LOG.md` has one entry per iteration, with the commands it ran and their output.

## Before you leave it running

- **Cost:** every iteration is a full agent session with tests and builds, so many iterations add up quickly. Start with a small number and read the log.
- **Pushes:** it pushes after each iteration to the current branch, and refuses to run on `main`/`master`.
- **Permissions:** `run.sh` lets Claude run shell commands without asking. Use it only in a disposable environment (container, VM, or cloud session).
- **Limits:** "best in the world" ultimately depends on things only people can provide: a speech-language therapist reviewing the exercises, licensed pictures, real voice recordings, and testing with people who have aphasia. The loop can make the software excellent and ready for those inputs.
