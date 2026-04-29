#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$SCRIPT_DIR"
mkdir -p "$REPO_DIR/logs"
LOG_FILE="$REPO_DIR/logs/triage.log"
LOCK_DIR="/tmp/dev-loop-triage.lock"
PROMPT_FILE="$REPO_DIR/.claude/routines/issue-validator.md"

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

# Prevent concurrent runs (mkdir is atomic, works on macOS without flock)
cleanup_lock() { rmdir "$LOCK_DIR" 2>/dev/null; }
trap cleanup_lock EXIT
mkdir "$LOCK_DIR" 2>/dev/null || { echo "$(date): triage already running, skipping" >> "$LOG_FILE"; exit 0; }

echo "$(date): Starting issue-validator (triage)" >> "$LOG_FILE"

cd "$REPO_DIR"

# Pull latest main
git fetch origin
git checkout main
git pull origin main

# Run the agent
claude -p "$(cat "$PROMPT_FILE")" \
  --dangerously-skip-permissions \
  >> "$LOG_FILE" 2>&1

echo "$(date): issue-validator complete" >> "$LOG_FILE"
