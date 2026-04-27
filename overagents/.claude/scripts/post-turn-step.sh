#!/bin/bash
# Reads CLAUDE.md and executes the post-turn-step section

CLAUDE_MD="${CLAUDE_PROJECT_DIR}/CLAUDE.md"

if [ ! -f "$CLAUDE_MD" ]; then
  exit 0
fi

# Extract and run the post-turn-step block from CLAUDE.md
POST_TURN_CMD=$(awk '/## post-turn-step/{found=1; next} found && /^```bash/{in_block=1; next} in_block && /^```/{exit} in_block{print}' "$CLAUDE_MD")

if [ -n "$POST_TURN_CMD" ]; then
  echo "Running post-turn-step..."
  eval "$POST_TURN_CMD"
fi
