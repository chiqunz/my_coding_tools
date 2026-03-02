#!/usr/bin/env bash
# PreToolUse hook: Block reading sensitive config/env files.
# Allows .example, .sample, .template variants.
#
# Exit codes:
#   0 = allow the read
#   2 = block the read (stderr shown to Claude)

set -euo pipefail

# Read the JSON payload from stdin
INPUT=$(cat)

# Extract the file path from tool_input.file_path
FILE_PATH=$(echo "$INPUT" | node -e "
const chunks = [];
process.stdin.on('data', c => chunks.push(c));
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(chunks.join(''));
    console.log((data.tool_input && data.tool_input.file_path) || '');
  } catch { console.log(''); }
});
" 2>/dev/null || echo "")

# If we couldn't extract a file path, allow the read
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Get just the filename (basename)
FILENAME=$(basename "$FILE_PATH")

# Allow .example, .sample, .template variants explicitly
case "$FILENAME" in
  *.example|*.sample|*.template|*.example.*|*.sample.*|*.template.*)
    exit 0
    ;;
esac

# Block patterns for sensitive files
BLOCKED=false

case "$FILENAME" in
  # .env files (but not .env.example, .env.sample, .env.template — already allowed above)
  .env|.env.local|.env.development|.env.production|.env.staging|.env.test|.env.*)
    BLOCKED=true
    ;;
  # General config files that may contain secrets
  config.json|config.yaml|config.yml|config.toml)
    BLOCKED=true
    ;;
  # Secrets and credentials
  secrets.json|secrets.yaml|secrets.yml|secrets.toml)
    BLOCKED=true
    ;;
  credentials.json|credentials.yaml|credentials.yml)
    BLOCKED=true
    ;;
  # Key/certificate files
  *.pem|*.key|*.p12|*.pfx|*.jks)
    BLOCKED=true
    ;;
  # Firebase / GCP service accounts
  service-account*.json|service_account*.json|firebase-adminsdk*.json)
    BLOCKED=true
    ;;
  # Vercel / Next.js specific
  .vercel.json)
    BLOCKED=true
    ;;
  # Docker secrets
  .docker-env|docker-compose.override.yml|docker-compose.override.yaml)
    BLOCKED=true
    ;;
esac

if [ "$BLOCKED" = true ]; then
  echo "BLOCKED: Reading '$FILENAME' is not allowed. This file may contain secrets or sensitive configuration." >&2
  echo "If you need configuration reference, read the .example/.sample/.template variant instead." >&2
  exit 2
fi

exit 0
