---
name: post-turn-step
description: >
  Reads CLAUDE.md and runs the post-turn-step section after file modifications.
  Triggered automatically by PostToolUse hook on Write/Edit/MultiEdit.
---

# Post-Turn-Step

This skill is triggered automatically after every file write/edit by the implementer agent.

## Behavior

1. Reads `CLAUDE.md` from the project directory
2. Extracts the `## post-turn-step` section
3. Executes any bash commands found in that section

## Purpose

Ensures that project-specific post-modification checks (linting, formatting, type checking, etc.) are always run after code changes, without the agent needing to remember to do it.
