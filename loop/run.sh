#!/usr/bin/env bash
# Run the improvement loop headlessly: one fresh Claude Code session per iteration.
#
#   loop/run.sh [max-iterations]      (default: 5)
#
# Stops when the iteration limit is reached, when loop/STOP exists (touch it to stop
# after the current iteration), when Claude has written loop/DONE, when an iteration
# exits with an error, or after two iterations in a row without a commit (usually
# blocked; read loop/LOG.md).
#
# Iterations run shell commands (pip, pytest, git push) without asking for approval,
# so run this somewhere disposable: a container, a VM, or a cloud session.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
max="${1:-5}"
branch="$(git branch --show-current)"
if [[ -z "$branch" || "$branch" == main || "$branch" == master ]]; then
  echo "Check out a feature branch first (current: ${branch:-detached HEAD})." >&2
  exit 1
fi
command -v claude >/dev/null || { echo "Claude Code CLI ('claude') is not on PATH." >&2; exit 1; }

mkdir -p loop/runs
idle=0
for ((i = 1; i <= max; i++)); do
  if [[ -f loop/STOP ]]; then echo "loop/STOP exists; stopping."; break; fi
  if [[ -f loop/DONE ]]; then echo "loop/DONE exists; nothing left to do."; break; fi

  before="$(git rev-parse HEAD)"
  log="loop/runs/$(date -u +%Y%m%dT%H%M%SZ)-$i.log"
  echo "== Iteration $i/$max on $branch (log: $log)"
  if ! claude -p "Read loop/PROMPT.md and carry out exactly one iteration." \
      --permission-mode acceptEdits \
      --allowedTools "Bash" "WebSearch" "WebFetch" \
      >"$log" 2>&1; then
    echo "Iteration $i failed. Last lines of $log:" >&2
    tail -n 20 "$log" >&2
    exit 1
  fi
  tail -n 3 "$log"

  if [[ "$(git rev-parse HEAD)" == "$before" ]]; then
    idle=$((idle + 1))
    if ((idle >= 2)); then
      echo "Two iterations in a row without a commit; stopping. See loop/LOG.md."
      break
    fi
  else
    idle=0
  fi
done
