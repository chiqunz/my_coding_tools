---
name: ts-project-setup
description: Bootstrap the TypeScript project dev environment — generate .vscode/settings.json, .vscode/extensions.json, and verify tooling is installed.
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

# TypeScript Project Setup Skill

## When Triggered

Bootstrap or verify the TypeScript project dev environment. Generate editor configuration files if missing.

## Steps

### 1. Check and create `.vscode/settings.json`

Check if `.vscode/settings.json` exists. If missing, create the `.vscode/` directory and write the settings file with these exact values:

```json
{
  "editor.defaultFormatter": "biomejs.biome",
  "editor.formatOnSave": true,
  "editor.formatOnPaste": false,
  "editor.codeActionsOnSave": {
    "source.fixAll.biome": "explicit",
    "source.organizeImports.biome": "explicit"
  },
  "editor.rulers": [100, 120],
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.linkedEditing": true,
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": "active",

  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.trimFinalNewlines": true,
  "files.exclude": {
    "**/node_modules": true,
    "**/.next": true,
    "**/dist": true,
    "**/.turbo": true,
    "**/coverage": true
  },

  "[typescript]": {
    "editor.defaultFormatter": "biomejs.biome",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.biome": "explicit",
      "source.organizeImports.biome": "explicit"
    },
    "editor.tabSize": 2
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "biomejs.biome",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.biome": "explicit",
      "source.organizeImports.biome": "explicit"
    },
    "editor.tabSize": 2
  },
  "[javascript]": {
    "editor.defaultFormatter": "biomejs.biome",
    "editor.formatOnSave": true,
    "editor.tabSize": 2
  },
  "[javascriptreact]": {
    "editor.defaultFormatter": "biomejs.biome",
    "editor.formatOnSave": true,
    "editor.tabSize": 2
  },
  "[json]": {
    "editor.defaultFormatter": "biomejs.biome",
    "editor.formatOnSave": true,
    "editor.tabSize": 2
  },
  "[jsonc]": {
    "editor.defaultFormatter": "biomejs.biome",
    "editor.formatOnSave": true,
    "editor.tabSize": 2
  },
  "[css]": {
    "editor.defaultFormatter": "biomejs.biome",
    "editor.formatOnSave": true,
    "editor.tabSize": 2
  },

  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"],
    ["cn\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"],
    ["clsx\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ],
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  },

  "biome.enabled": true,
  "eslint.enable": false,
  "prettier.enable": false,

  "typescript.preferences.importModuleSpecifier": "non-relative",
  "typescript.preferences.importModuleSpecifierEnding": "minimal",
  "typescript.suggest.autoImports": true,
  "typescript.updateImportsOnFileMove.enabled": "always",
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "typescript.preferences.preferTypeOnlyAutoImports": true,

  "emmet.includeLanguages": {
    "typescriptreact": "html",
    "javascriptreact": "html"
  },

  "vitest.enable": true,
  "vitest.commandLine": "pnpm vitest",
  "npm.packageManager": "pnpm",

  "search.exclude": {
    "**/node_modules": true,
    "**/.next": true,
    "**/dist": true,
    "**/.turbo": true,
    "**/pnpm-lock.yaml": true
  }
}
```

If it already exists, verify the key settings are present (biome as formatter, format on save, eslint/prettier disabled, pnpm). Add any missing keys without overwriting existing customizations.

### 2. Check and create `.vscode/extensions.json`

If missing, create with:

```json
{
  "recommendations": [
    "biomejs.biome",
    "bradlc.vscode-tailwindcss",
    "vitest.explorer",
    "ms-playwright.playwright",
    "yoavbls.pretty-ts-errors",
    "mattpocock.ts-error-translator",
    "formulahendry.auto-rename-tag",
    "usernamehw.errorlens",
    "eamodio.gitlens",
    "ms-azuretools.vscode-docker"
  ]
}
```

### 3. Verify tooling is available

Run these checks and report status:

```bash
# Check pnpm is installed
pnpm --version

# Check Node.js version
node --version

# Check TypeScript version
pnpm tsc --version

# Check if node_modules exists
test -d node_modules || pnpm install

# Verify biome works
pnpm biome --version

# Check for turbo (monorepo)
pnpm turbo --version 2>/dev/null || echo "turbo not installed"

# Verify vitest works
pnpm vitest --version 2>/dev/null || echo "vitest not installed"
```

### 4. Check for tsconfig.json

Verify `tsconfig.json` exists and has `"strict": true`. If strict mode is not enabled, warn the user.

### 5. Check for biome.json

Verify `biome.json` or `biome.jsonc` exists. If missing, warn the user to initialize with `pnpm biome init`.

### 6. Summary

Report what was created/verified:
- `.vscode/settings.json` — created / already existed / updated
- `.vscode/extensions.json` — created / already existed
- Node.js version
- pnpm version
- TypeScript strict mode status
- Biome configuration status
- Any issues found
