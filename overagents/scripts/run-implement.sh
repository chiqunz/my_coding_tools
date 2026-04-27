#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$SCRIPT_DIR"
LOG_FILE="$REPO_DIR/logs/implement.log"
LOCK_FILE="/tmp/dev-loop-implement.lock"
PROMPT_FILE="$REPO_DIR/.claude/routines/issue-implementer.md"
WORKTREE_BASE="$REPO_DIR/../worktrees"

# Prevent concurrent runs
exec 9>"$LOCK_FILE"
flock -n 9 || { echo "$(date): implementer already running, skipping" >> "$LOG_FILE"; exit 0; }

echo "$(date): Starting issue-implementer" >> "$LOG_FILE"

# Check if any triage issues exist before doing anything
TRIAGE_COUNT=$(gh issue list --label "triage" --state open --json number | jq length)
if [ "$TRIAGE_COUNT" -eq 0 ]; then
  echo "$(date): No triage issues found, exiting" >> "$LOG_FILE"
  exit 0
fi

cd "$REPO_DIR"

# Pull latest main
git fetch origin
git checkout main
git pull origin main

# Create timestamped worktree
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BRANCH="claude/implement-$TIMESTAMP"
WORKTREE="$WORKTREE_BASE/$BRANCH"

mkdir -p "$WORKTREE_BASE"
git worktree add "$WORKTREE" -b "$BRANCH" origin/main

echo "$(date): Created worktree at $WORKTREE (branch: $BRANCH)" >> "$LOG_FILE"

# Run implementer inside the worktree
cd "$WORKTREE"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  claude -p "$(cat "$PROMPT_FILE")" \
  --dangerously-skip-permissions \
  >> "$LOG_FILE" 2>&1

# Cleanup: if no changes were made, remove the worktree
cd "$REPO_DIR"
if git -C "$WORKTREE" diff --quiet && git -C "$WORKTREE" diff --cached --quiet; then
  echo "$(date): No changes made, cleaning up worktree" >> "$LOG_FILE"
  git worktree remove "$WORKTREE" --force
  git branch -d "$BRANCH" 2>/dev/null || true
else
  echo "$(date): Changes present in $WORKTREE — worktree preserved for review" >> "$LOG_FILE"
fi

echo "$(date): issue-implementer complete" >> "$LOG_FILE"
