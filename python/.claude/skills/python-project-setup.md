---
name: python-project-setup
description: Bootstrap the Python project dev environment — generate .vscode/settings.json, .vscode/extensions.json, and verify tooling is installed.
triggers:
  - "setup project"
  - "init project"
  - "bootstrap"
  - "setup vscode"
  - "configure editor"
  - "setup dev environment"
tools:
  - Bash
  - Read
  - Write
  - Glob
---

# Python Project Setup Skill

## When Triggered

Bootstrap or verify the Python project dev environment. Generate editor configuration files if missing.

## Steps

### 1. Check and create `.vscode/settings.json`

Check if `.vscode/settings.json` exists. If missing, create the `.vscode/` directory and write the settings file with these exact values:

```json
{
  "editor.defaultFormatter": "charliermarsh.ruff",
  "editor.formatOnSave": true,
  "editor.formatOnPaste": false,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit",
    "source.organizeImports.ruff": "explicit"
  },
  "editor.rulers": [88, 120],
  "editor.tabSize": 4,
  "editor.insertSpaces": true,

  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.trimFinalNewlines": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true,
    "**/*.egg-info": true,
    "**/.venv": true,
    "**/dist": true
  },

  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    },
    "editor.tabSize": 4
  },

  "ruff.enable": true,
  "ruff.fixAll": true,
  "ruff.organizeImports": true,
  "ruff.lint.run": "onSave",
  "ruff.importStrategy": "fromEnvironment",

  "python.analysis.typeCheckingMode": "standard",
  "mypy-type-checker.args": ["--strict"],
  "mypy-type-checker.importStrategy": "fromEnvironment",

  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,

  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": ["tests", "-v", "--tb=short"],

  "python.linting.enabled": false,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": false,
  "python.formatting.provider": "none",

  "search.exclude": {
    "**/__pycache__": true,
    "**/.venv": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true
  }
}
```

If it already exists, verify the key settings are present (ruff as formatter, format on save, mypy strict). Add any missing keys without overwriting existing customizations.

### 2. Check and create `.vscode/extensions.json`

If missing, create with:

```json
{
  "recommendations": [
    "charliermarsh.ruff",
    "ms-python.mypy-type-checker",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.debugpy",
    "tamasfe.even-better-toml",
    "usernamehw.errorlens",
    "eamodio.gitlens",
    "ms-azuretools.vscode-docker"
  ]
}
```

### 3. Verify tooling is available

Run these checks and report status:

```bash
# Check uv is installed
uv --version

# Check Python version
python3 --version

# Check if .venv exists, create if not
test -d .venv || uv venv

# Sync dependencies
uv sync

# Verify ruff works
uv run ruff --version

# Verify mypy works
uv run mypy --version

# Verify pytest works
uv run pytest --version
```

### 4. Check for pyproject.toml

If `pyproject.toml` doesn't exist, warn the user that this is required. Do NOT create it — the user should initialize the project with `uv init`.

### 5. Summary

Report what was created/verified:
- `.vscode/settings.json` — created / already existed / updated
- `.vscode/extensions.json` — created / already existed
- Python version
- uv version
- Virtual environment status
- Any issues found
