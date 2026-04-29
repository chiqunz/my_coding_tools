#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$SCRIPT_DIR"
mkdir -p "$REPO_DIR/logs"
LOG_FILE="$REPO_DIR/logs/prompt-auditor.log"
LOCK_FILE="/tmp/dev-loop-prompt-auditor.lock"
PROMPT_FILE="$REPO_DIR/.claude/routines/prompt-auditor.md"

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
flock -n 9 || { echo "$(date): prompt-auditor already running, skipping" >> "$LOG_FILE"; exit 0; }

echo "$(date): Starting prompt-auditor" >> "$LOG_FILE"

cd "$REPO_DIR"

# Always pull latest main
git fetch origin
git checkout main
git pull origin main

# Run the agent
claude -p "$(cat "$PROMPT_FILE")" \
  --dangerously-skip-permissions \
  >> "$LOG_FILE" 2>&1

echo "$(date): prompt-auditor complete" >> "$LOG_FILE"
