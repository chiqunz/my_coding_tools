#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$SCRIPT_DIR"
mkdir -p "$REPO_DIR/logs"
LOG_FILE="$REPO_DIR/logs/implement.log"
LOCK_FILE="/tmp/dev-loop-implement.lock"
PROMPT_FILE="$REPO_DIR/.claude/routines/issue-implementer.md"
WORKTREE_BASE="$REPO_DIR/../worktrees"

# Source LiteLLM proxy config from mai-agents
# Set MAI_AGENTS_DIR to your mai-agents checkout, or it defaults to ~/Work/Repo/mai-agents
MAI_AGENTS_DIR="${MAI_AGENTS_DIR:-$HOME/Work/Repo/mai-agents}"
MAI_ENV_FILE="$(ls "$MAI_AGENTS_DIR"/.run/.env-* 2>/dev/null | head -1)"
if [ -z "$MAI_ENV_FILE" ] || [ ! -f "$MAI_ENV_FILE" ]; then
  echo "Error: mai-agents .env file not found at $MAI_AGENTS_DIR/.run/" >&2
  echo "Run mai-agents/setup.sh first, or set MAI_AGENTS_DIR to your mai-agents path." >&2
  exit 1
fi
set -a; source "$MAI_ENV_FILE"; set +a
export ANTHROPIC_BASE_URL="${LITELLM_PROXY_URL}"
export ANTHROPIC_API_KEY="${LITELLM_API_KEY}"

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
claude -p "$(cat "$PROMPT_FILE")" \
  --dangerously-skip-permissions \
  >> "$LOG_FILE" 2>&1

# Cleanup: if no changes were made, remove the worktree
cd "$REPO_DIR"
COMMITS_AHEAD=$(git -C "$WORKTREE" rev-list origin/main..HEAD --count)
if [ "$COMMITS_AHEAD" -eq 0 ] && git -C "$WORKTREE" diff --quiet && git -C "$WORKTREE" diff --cached --quiet; then
  echo "$(date): No changes made, cleaning up worktree" >> "$LOG_FILE"
  git worktree remove "$WORKTREE" --force
  git branch -d "$BRANCH" 2>/dev/null || true
else
  echo "$(date): Changes present in $WORKTREE — worktree preserved for review" >> "$LOG_FILE"
fi

echo "$(date): issue-implementer complete" >> "$LOG_FILE"
