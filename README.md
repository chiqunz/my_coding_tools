# Coding Agent Packages — Python, TypeScript, C#

> Production-ready context engineering packages for AI coding agents.
> Based on research from [Context Engineering for Autonomous Development](../Claude%20Coding%20Agent%20Markdown%20Research.md).

## Overview

These packages provide comprehensive, battle-tested configurations for AI coding agents (Claude Code, Cursor, GitHub Copilot, RooCode, Windsurf, Aider, and others) across three major language ecosystems. Each package follows the **WHAT-WHY-HOW** ontological framework and adheres to the "Less is More" principle for optimal agent performance.

## Package Structure

Each language package contains:

```
<language>/
├── CLAUDE_USER.md               # Claude Code-specific instructions (comprehensive)
├── AGENTS_USER.md               # Universal agent instructions (vendor-agnostic)
└── .claude/
    ├── skills/                  # Task-specific skill definitions
    │   ├── <lang>-test-runner.md       # Run tests, analyze failures, fix autonomously
    │   ├── <lang>-<feature>.md         # Feature-specific scaffolding skills
    │   ├── <lang>-refactor.md          # Modernize code to latest language features
    │   ├── <lang>-project-setup.md     # Bootstrap VSCode, editor, and tooling config
    │   ├── <lang>-code-audit.md        # Comprehensive code quality audit
    │   ├── <lang>-simplify.md          # Simplify and modernize code patterns
    │   └── <lang>-bug-scan.md          # Scan for bugs, security issues, anti-patterns
    ├── rules/                   # File-glob-scoped enforcement rules
    │   ├── type-safety.md
    │   ├── <lang>-conventions.md
    │   └── ...
    └── hooks/
        └── hooks.json           # Lifecycle hooks (auto-format, pre-commit gates)
```

## File Purposes

| File | Purpose | Loaded By |
|------|---------|-----------|
| **CLAUDE_USER.md** | Comprehensive project context for Claude Code. Auto-loaded at session start. Contains full architectural rules, code examples, anti-patterns, quality gates, and references to skills/hooks. | Claude Code (automatic) |
| **AGENTS_USER.md** | Vendor-agnostic agent instructions. Concise, compatible with all major AI coding agents. | Cursor, Copilot, RooCode, Windsurf, Aider, Claude Code |
| **Skills** (`.claude/skills/`) | Task-specific workflows with YAML frontmatter for triggers, tool restrictions, and step-by-step instructions. Invoked on-demand. | Claude Code (via `/` commands or auto-triggers) |
| **Rules** (`.claude/rules/`) | File-glob-scoped rules that apply automatically when the agent touches matching files. Lightweight enforcement guards. | Claude Code (automatic by glob match) |
| **Hooks** (`.claude/hooks/hooks.json`) | Lifecycle hooks that run automatically on specific events (PreToolUse, PostToolUse, PreCommit). Block reading sensitive files, enforce formatting on save, and lint+test gates before commits. | Claude Code (automatic) |

## Packages

### 🐍 Python Package

**Stack:** Python 3.12+ • uv • FastAPI • Pydantic v2 • ruff • mypy • pytest

| File | Description |
|------|-------------|
| `CLAUDE_USER.md` | Full Python context with directory topology, modern tooling mandates, async patterns, type safety rules |
| `AGENTS_USER.md` | Concise vendor-agnostic Python agent instructions |
| `skills/python-test-runner.md` | Run pytest, analyze failures, fix autonomously |
| `skills/python-api-endpoint.md` | Create FastAPI endpoints with schemas, DI, and tests |
| `skills/python-database-migration.md` | Manage Alembic/SQLAlchemy migrations |
| `skills/python-refactor.md` | Modernize Python code (type hints, async, modern syntax) |
| `skills/python-project-setup.md` | Bootstrap VSCode config (ruff, mypy, pytest settings) |
| `skills/python-code-audit.md` | Full audit: radon complexity, vulture dead code, mypy coverage, bandit security, pip-audit, ruff extended rules |
| `skills/python-simplify.md` | Simplify code: guard clauses, comprehensions, pattern matching, ruff auto-fix |
| `skills/python-bug-scan.md` | Scan for bugs: bandit security, ruff bugbear, mutable defaults, resource leaks, hardcoded secrets |
| `hooks/hooks.json` | PreToolUse: block reading .env/secrets/config files. PostToolUse: auto ruff format on save. PreCommit: ruff + mypy + pytest gate |
| `hooks/block-sensitive-reads.sh` | PreToolUse hook script — blocks reading `.env`, `secrets.*`, `config.*`, `credentials.*`, `*.pem`, `*.key` files |
| `rules/import-order.md` | Enforce import ordering (stdlib → third-party → local) |
| `rules/type-safety.md` | Forbid `Any`, enforce modern union syntax |
| `rules/async-patterns.md` | Enforce async-first I/O patterns |

### 📘 TypeScript Package

**Stack:** TypeScript 5.x (strict) • pnpm • React 18+ • Next.js App Router • Zod • Tailwind • Shadcn UI • Vitest • Biome

| File | Description |
|------|-------------|
| `CLAUDE_USER.md` | Full TypeScript context with monorepo topology, React conventions, Zod validation, styling rules |
| `AGENTS_USER.md` | Concise vendor-agnostic TypeScript agent instructions |
| `skills/ts-test-runner.md` | Run Vitest/Playwright, analyze failures, fix autonomously |
| `skills/ts-react-component.md` | Create React components with types, Tailwind, Shadcn, and tests |
| `skills/ts-api-route.md` | Create Next.js Route Handlers or tRPC procedures with Zod |
| `skills/ts-refactor.md` | Remove `any`, fix type assertions, modernize patterns |
| `skills/ts-project-setup.md` | Bootstrap VSCode config (Biome, Tailwind, Vitest, pnpm settings) |
| `skills/ts-code-audit.md` | Full audit: type safety holes, knip dead code, pnpm audit, Biome diagnostics, React-specific checks |
| `skills/ts-simplify.md` | Simplify code: remove `any`, assertions → Zod, enums → unions, extract hooks, optional chaining |
| `skills/ts-bug-scan.md` | Scan for bugs: type holes, React bugs, async bugs, security (XSS, eval, secrets), Next.js-specific |
| `hooks/hooks.json` | PreToolUse: block reading .env/secrets/config files. PostToolUse: auto biome format on save. PreCommit: tsc + vitest gate |
| `hooks/block-sensitive-reads.sh` | PreToolUse hook script — blocks reading `.env`, `secrets.*`, `config.*`, `credentials.*`, `*.pem`, `*.key` files |
| `rules/type-safety.md` | Forbid `any`, `as` on external data, `enum` |
| `rules/react-conventions.md` | Functional components, named exports, hooks |
| `rules/monorepo-rules.md` | pnpm workspace conventions, Turbo usage |

### 🔷 C# / .NET Package

**Stack:** .NET 8+ • C# 12 • Clean Architecture • CQRS/MediatR • EF Core • FluentValidation • xUnit

| File | Description |
|------|-------------|
| `CLAUDE_USER.md` | Full .NET context with Clean Architecture topology, CQRS patterns, modern C# 12 features, EF Core rules |
| `AGENTS_USER.md` | Concise vendor-agnostic .NET agent instructions |
| `skills/dotnet-test-runner.md` | Run xUnit tests, analyze failures, fix autonomously |
| `skills/dotnet-cqrs-feature.md` | Create complete CQRS features (Command/Query/Handler/Validator/Endpoint) |
| `skills/dotnet-ef-migration.md` | Manage EF Core migrations with Fluent API configurations |
| `skills/dotnet-refactor.md` | Modernize to C# 12 (primary constructors, records, file-scoped namespaces) |
| `skills/dotnet-project-setup.md` | Bootstrap VSCode config + `.editorconfig` (Roslyn, naming, nullable diagnostics) |
| `skills/dotnet-code-audit.md` | Full audit: Roslyn warnings, nullable coverage, architecture boundaries, async anti-patterns, NuGet health |
| `skills/dotnet-simplify.md` | Simplify code: primary constructors, records, collection expressions, switch expressions, guard clauses |
| `skills/dotnet-bug-scan.md` | Scan for bugs: nullable violations, sync-over-async, exception bugs, EF N+1, SQL injection, DI issues |
| `hooks/hooks.json` | PreToolUse: block reading .env/secrets/config files. PostToolUse: auto dotnet format on save. PreCommit: build + test gate |
| `hooks/block-sensitive-reads.sh` | PreToolUse hook script — blocks reading `.env`, `appsettings.json`, `secrets.*`, `config.*`, `*.pfx`, `*.key` files |
| `rules/clean-architecture.md` | Enforce layer boundaries (Domain has zero external deps) |
| `rules/csharp-conventions.md` | Modern C# 12 language conventions |
| `rules/error-handling.md` | Result\<T\> pattern, FluentValidation, no thrown exceptions |

## Lifecycle Hooks

Each package includes `.claude/hooks/hooks.json` with three automated lifecycle hooks:

### PreToolUse — Sensitive File Protection

Intercepts every `Read` tool call and blocks access to files that may contain secrets or sensitive configuration. The hook script (`.claude/hooks/block-sensitive-reads.sh`) checks the filename against blocked patterns and exits with code 2 to deny the read.

**Blocked patterns:** `.env`, `.env.*`, `secrets.*`, `config.json`, `config.yaml`, `credentials.*`, `*.pem`, `*.key`, `*.pfx`, `appsettings.json` (C#), `local.settings.json` (C#), `firebase-adminsdk*.json` (TS), and more.

**Explicitly allowed:** Files ending in `.example`, `.sample`, or `.template` (e.g., `.env.example`, `config.yaml.template`).

### PostToolUse — Auto-Format on Save

Triggers automatically whenever the agent writes a file matching the language pattern. Ensures every file is formatted before continuing.

| Language | Trigger | Action |
|----------|---------|--------|
| Python | Write `**.py` | `ruff check --fix` + `ruff format` |
| TypeScript | Write `**.ts`, `**.tsx` | `biome check --apply` |
| C# | Write `**.cs` | `dotnet format` |

### PreCommit — Quality Gate

Runs before every `git commit`. The commit is **blocked** if any step fails, preventing broken code from entering the repository.

| Language | Pipeline |
|----------|----------|
| Python | `ruff check src/` → `mypy src/` → `pytest tests/ -x -q` |
| TypeScript | `tsc --noEmit` → `vitest run --reporter=verbose` |
| C# | `dotnet build --no-restore` → `dotnet test --no-build` |

## How to Use

### Quick Start

1. **Copy the desired language package** to your repository root:
   ```bash
   cp -r coding-agent-packages/python/* /path/to/your/repo/
   # or
   cp -r coding-agent-packages/typescript/* /path/to/your/repo/
   # or
   cp -r coding-agent-packages/csharp/* /path/to/your/repo/
   ```

2. **Customize** the files to match your specific project:
   - Update the technology stack versions
   - Adjust directory topology to match your actual structure
   - Modify operational commands for your build system
   - Add project-specific anti-patterns you've encountered

3. **Start using** Claude Code or any supported agent — it will automatically load the context.

### Multi-Agent Compatibility

If you use multiple AI coding agents, set `AGENTS_USER.md` as the source of truth and reference it from `CLAUDE_USER.md`:

```markdown
<!-- In CLAUDE_USER.md -->
> Follow all rules defined in AGENTS_USER.md. This file contains additional Claude Code-specific instructions.
```

### Iterative Refinement

The research strongly recommends an **iterative approach**:
1. Start with the minimal package as provided
2. When the agent makes a specific, repeated error, add a targeted rule
3. Remove rules that the agent consistently follows without instruction
4. Keep the total file under ~150 discrete instructions for optimal performance

## Design Principles

These packages are engineered following research-backed principles:

1. **Less is More** — Files are kept actionable and concise (~150 instructions max)
2. **Deterministic Delegation** — Style/formatting delegated to tools (ruff, biome, dotnet format), not the LLM
3. **Progressive Disclosure** — Domain-specific docs are referenced as pointers, not copied inline
4. **Concrete > Aspirational** — "Use `Result<T>` not exceptions" beats "write clean code"
5. **File-Scoped Commands** — Fast feedback loops with targeted commands, not full-suite builds
6. **Quality Gates** — Autonomous self-verification before completing any task

## References

- [AGENTS.md Standard](https://agents.md/)
- [Claude Code Documentation](https://code.claude.com/docs/en/overview)
- [Writing a Good CLAUDE.md (HumanLayer)](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [GitHub Blog: How to Write a Great agents.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)
- [Skill Authoring Best Practices (Claude API Docs)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
