#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$SCRIPT_DIR"
mkdir -p "$REPO_DIR/logs"
LOG_FILE="$REPO_DIR/logs/prompt-auditor.log"
LOCK_FILE="/tmp/dev-loop-prompt-auditor.lock"
PROMPT_FILE="$REPO_DIR/.claude/routines/prompt-auditor.md"

# Prevent concurrent runs
exec 9>"$LOCK_FILE"
flock -n 9 || { echo "$(date): prompt-auditor already running, skipping" >> "$LOG_FILE"; exit 0; }

echo "$(date): Starting prompt-auditor" >> "$LOG_FILE"

cd "$REPO_DIR"

# Always pull latest main
git fetch origin
git checkout main
git pull origin main

# Run the agent
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  claude -p "$(cat "$PROMPT_FILE")" \
  --dangerously-skip-permissions \
  >> "$LOG_FILE" 2>&1

echo "$(date): prompt-auditor complete" >> "$LOG_FILE"
