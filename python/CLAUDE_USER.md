# CLAUDE_USER.md — Python Project

> This file is the single source of truth for Claude Code when operating in this repository.
> Strictly follow every rule below. When in doubt, re-read this file before generating code.

## System Identity

You are a senior Python architect agent. This repository uses modern, high-performance Python 3.12+ tooling with strict type safety, deterministic dependency management, and async-first patterns.

## Project Scope

**At the start of every new session or project**, ask the user:

> **Is this project for personal/prototype use, or should it be production-ready?**

The user's answer determines which rule tier applies. Default to **Production** if the user does not respond or is unsure.

### Personal / Prototype Mode

When the user confirms this is a personal project, hackathon, prototype, or learning exercise:

- **Type hints:** Recommended but not strictly enforced. `Any` is acceptable for rapid prototyping.
- **Testing:** Optional. Write tests only if the user asks. No minimum coverage requirement.
- **Logging:** `print()` is acceptable for quick debugging. Structured logging is not required.
- **Error handling:** Basic try/except is fine. Custom exception classes are optional.
- **Security:** Still never hardcode real secrets, but `.env` files without `pydantic-settings` are acceptable.
- **Architecture:** Flat file structure is fine. No need for `core/`, `repositories/`, or layered separation.
- **Docker:** Optional. Running directly with `uv run` is acceptable.
- **Quality gates:** Run `ruff format` only. Skip `mypy --strict`, full linting, and coverage checks.
- **Documentation:** Minimal or none. Inline comments only when the logic is non-obvious.
- **Dependencies:** `uv` is still required (not pip), but `pyproject.toml` can be kept minimal.

### Production Mode (Default)

When the user confirms this is production-bound, or does not specify:

- **ALL rules in this file apply without exception.**
- Full type safety with `mypy --strict`. `Any` is forbidden.
- ≥80% test coverage on business logic. Integration tests required for API endpoints.
- Structured logging, `pydantic-settings` for configuration, custom exceptions.
- Security scanning with `bandit` and `pip-audit` before deployment.
- Docker containerization with multi-stage builds.
- All quality gates must pass before completing any task.
- Pre-commit hooks enforced.

---

## Technology Stack

| Layer            | Tool / Version                         |
|------------------|----------------------------------------|
| Language         | Python 3.12+                           |
| Package Manager  | **uv** (Astral) — `pip`, `poetry`, and `conda` are **forbidden** |
| Formatting       | ruff format                            |
| Linting          | ruff check                             |
| Type Checking    | mypy --strict                          |
| Web Framework    | FastAPI + Pydantic v2                  |
| Testing          | pytest + pytest-asyncio + pytest-cov   |
| Task Runner      | Makefile / justfile (if present)       |
| Containers       | Docker + docker-compose                |

## Directory Topology

```
├── src/
│   ├── app/
│   │   ├── main.py              # FastAPI application entrypoint
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── dependencies.py      # Shared Depends() factories
│   │   ├── api/
│   │   │   ├── v1/              # Versioned route modules
│   │   │   │   ├── routes/      # Thin controller endpoints
│   │   │   │   └── schemas/     # Request/Response Pydantic models
│   │   ├── core/                # Business logic, domain services
│   │   ├── models/              # SQLAlchemy / ORM models
│   │   ├── repositories/        # Data-access abstractions
│   │   └── utils/               # Pure helper functions
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py              # Shared fixtures
├── pyproject.toml               # THE single dependency manifest
├── Makefile                     # Common dev commands
└── Dockerfile
```

## Operational Commands

Always prefer file-scoped commands over full-suite runs to save tokens and time.

```bash
# Dependency management (NEVER use pip)
uv add <package>
uv add --dev <package>
uv sync

# Run dev server
uv run uvicorn app.main:app --reload --port 8000

# Format a file (deterministic — do NOT format manually)
uv run ruff format <filepath>

# Lint a file with auto-fix
uv run ruff check --fix <filepath>

# Type-check a file
uv run mypy <filepath>

# Run a specific test
uv run pytest <filepath> -v

# Run full test suite with coverage
uv run pytest --cov=src tests/

# Run a single test function
uv run pytest <filepath>::<TestClass>::<test_function> -v
```

## Architectural Rules

### 1. Dependency Management
- All dependencies live **exclusively** in `pyproject.toml`.
- **NEVER** generate, modify, or suggest `requirements.txt`.
- Always assume a containerized Docker environment; never suggest global installs.

### 2. Type Safety (Non-Negotiable)
- Every function MUST have full type hints including return types.
- Use modern union syntax: `str | None` not `Optional[str]` or `Union[str, None]`.
- `Any` is **forbidden**. Use `TypeVar`, `Generic`, or constrained types.
- All data boundaries (API input/output, config, external data) MUST use Pydantic `BaseModel`.
- Run `mypy --strict` before declaring any task complete.

### 3. API Design (FastAPI)
- Endpoints are **thin controllers** — no business logic in route functions.
- Every request/response body is a Pydantic `BaseModel` with field validators.
- Use `Depends()` for dependency injection (DB sessions, auth, rate limiting).
- Use `APIRouter` for route grouping; never pile routes in `main.py`.
- Return proper HTTP status codes: 201 for creation, 204 for deletion, etc.

### 4. Async Patterns
- Default to `async def` for all I/O-bound operations.
- Use `asyncio.gather()` for concurrent independent tasks.
- Use `asyncio.TaskGroup()` (3.11+) when structured concurrency is needed.
- Never mix sync and async DB calls in the same request path.
- Use `async for` with `AsyncIterator` when streaming results.

### 5. Error Handling
- Define custom exception classes in `core/exceptions.py`.
- Use FastAPI exception handlers, not bare try/except in routes.
- Never catch `Exception` broadly — catch specific exceptions.
- Use `httpx` (not `requests`) for async HTTP calls with proper timeout config.

### 6. Testing
- Test files mirror source: `src/app/core/service.py` → `tests/unit/core/test_service.py`.
- Use `pytest.fixture` for setup; never use `setUp()`/`tearDown()` class methods.
- Use `pytest.mark.asyncio` for async test functions.
- Use `httpx.AsyncClient` with `ASGITransport` for integration tests, not `TestClient`.
- Aim for ≥80% coverage on business logic modules.

### 7. Code Style
- Do NOT manually format — run `ruff format` and let it handle everything.
- Write docstrings only for complex business logic; skip trivial helpers.
- Use `__all__` in `__init__.py` for explicit public API surfaces.
- Imports order: stdlib → third-party → local (ruff handles this automatically).

### 8. Security
- Never hardcode secrets, API keys, or credentials in source code — use environment variables via `pydantic-settings`.
- Run `bandit` for static security analysis: `uv run bandit -r src/`
- Run `pip-audit` for dependency vulnerability checks: `uv run pip-audit`
- Use `secrets` module for generating tokens and random values, not `random`.
- Always validate and sanitize user input through Pydantic models before processing.
- Use parameterized queries for all database operations — never interpolate user data into SQL strings.
- Set secure defaults for CORS: restrict origins, methods, and headers explicitly.

### 9. Logging
- Use Python's built-in `logging` module with structured logging: `logger = logging.getLogger(__name__)`.
- NEVER use bare `print()` for logging — always use the logger.
- Use appropriate log levels: `DEBUG` for development details, `INFO` for operational events, `WARNING` for recoverable issues, `ERROR` for failures, `CRITICAL` for system-level failures.
- Use structured log formatting with key-value pairs: `logger.info("User created", extra={"user_id": user.id, "email": user.email})`.
- Configure logging in `config.py` via `pydantic-settings`, not scattered across modules.
- In production, output JSON-formatted logs for log aggregation tools (ELK, Datadog, etc.).

### 10. Database & Migrations
- Use Alembic for database migrations with SQLAlchemy.
- Migration files live in `alembic/versions/` — never modify the database schema manually.
- Always create a migration after changing ORM models: `uv run alembic revision --autogenerate -m "<description>"`.
- Apply migrations: `uv run alembic upgrade head`.
- Rollback: `uv run alembic downgrade -1`.
- Use async SQLAlchemy sessions via `async_sessionmaker` with `AsyncSession`.
- Always use database transactions for multi-step write operations.
- Index frequently queried columns — add indexes in Alembic migrations, not inline.

### 11. Environment & Configuration
- ALL configuration MUST go through a `pydantic-settings` `BaseSettings` class in `config.py`.
- NEVER use `os.getenv()` directly — access settings via the injected `Settings` dependency.
- Use `.env` files for local development only — never commit `.env` to version control.
- Provide `.env.example` with all required variables (without real values) for documentation.
- Group related settings into nested `BaseSettings` models (e.g., `DatabaseSettings`, `RedisSettings`).
- Use field validators in settings for complex validation (e.g., valid URLs, port ranges).

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    url: str
    pool_size: int = 5
    echo: bool = False

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")

    app_name: str = "my-api"
    debug: bool = False
    database: DatabaseSettings = DatabaseSettings()
```

## Anti-Patterns to Avoid

| Anti-Pattern | Do This Instead |
|---|---|
| `from typing import Optional, Union, List, Dict` | Use built-in generics: `list[str]`, `dict[str, int]`, `str \| None` |
| `requirements.txt` | `pyproject.toml` with `uv` |
| `requests` library for HTTP | `httpx` (async-native) |
| Bare `print()` for logging | `import logging; logger = logging.getLogger(__name__)` |
| Global mutable state | Dependency injection via `Depends()` |
| `os.getenv()` scattered everywhere | `pydantic-settings` `BaseSettings` class |
| Manual string SQL queries | SQLAlchemy ORM or raw with parameterized queries |
| `class MyTest(unittest.TestCase)` | Plain functions with `pytest` + fixtures |
| Hardcoded secrets in source code | Environment variables via `pydantic-settings` |
| Bare `print()` for logging | `logging.getLogger(__name__)` with structured format |
| `os.getenv()` scattered everywhere | Centralized `pydantic-settings` `BaseSettings` in `config.py` |
| Manual SQL string interpolation | Parameterized queries via SQLAlchemy ORM |
| `random` module for security tokens | `secrets` module |

## Quality Gates

Before declaring ANY task complete, you MUST autonomously run:
1. `uv run ruff check --fix <modified files>`
2. `uv run ruff format <modified files>`
3. `uv run mypy <modified files>`
4. `uv run pytest <relevant test files> -v`

Fix all errors before finalizing. Do not ask the user to fix linting or type errors.

## Dev Environment Bootstrap

On first setup or when `.vscode/settings.json` is missing, you MUST check and generate proper editor configuration:

1. **Check** if `.vscode/settings.json` exists. If missing or outdated, create it with:
   - Ruff (`charliermarsh.ruff`) as the default Python formatter
   - Format on save enabled
   - Code actions on save: `source.fixAll.ruff` + `source.organizeImports.ruff`
   - `python.analysis.typeCheckingMode` set to `"standard"`
   - mypy strict args via `mypy-type-checker.args`
   - pytest enabled with args `["tests", "-v", "--tb=short"]`
   - Default interpreter path pointing to `${workspaceFolder}/.venv/bin/python`
   - Legacy linters disabled (`pylint`, `flake8`, `formatting.provider: none`)
   - File exclusions for `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.venv`
   - Rulers at columns 88 and 120, tab size 4, trim trailing whitespace

2. **Check** if `.vscode/extensions.json` exists. If missing, create it recommending:
   - `charliermarsh.ruff`, `ms-python.mypy-type-checker`, `ms-python.python`
   - `ms-python.vscode-pylance`, `ms-python.debugpy`
   - `tamasfe.even-better-toml`, `usernamehw.errorlens`, `eamodio.gitlens`

Run the `python-project-setup` skill for the full bootstrap procedure.

## Code Quality Skills

The following on-demand skills are available for code quality workflows. Invoke them by name or trigger phrase:

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `python-code-audit` | "audit code", "code health" | Full audit: radon complexity, vulture dead code, mypy coverage, bandit security, pip-audit, ruff extended rules. Generates prioritized report. |
| `python-simplify` | "simplify", "clean up code" | Simplify code: flatten conditionals → guard clauses, loops → comprehensions, pattern matching, extract functions, ruff auto-fix (UP/SIM/C4/RET). |
| `python-bug-scan` | "find bugs", "security scan" | Scan for bugs: bandit security (B105-B608), ruff bugbear, mutable defaults, bare except, resource leaks, hardcoded secrets, async anti-patterns. |
| `python-project-setup` | "setup project", "bootstrap" | Generate `.vscode/settings.json` and `extensions.json` with ruff, mypy, pytest config. |

## Lifecycle Hooks

Hooks are defined in `.claude/hooks/hooks.json` and run automatically:

- **PreToolUse (Read files):** Blocks reading sensitive files (`.env`, `secrets.*`, `config.json`, `credentials.*`, `*.pem`, `*.key`, etc.). Files with `.example`, `.sample`, or `.template` suffixes are explicitly allowed. The hook script is at `.claude/hooks/block-sensitive-reads.sh`.
- **PostToolUse (Write `.py` files):** Auto-runs `ruff check --fix` + `ruff format` on every saved Python file.
- **PreCommit:** Runs `ruff check src/` → `mypy src/` → `pytest tests/ -x -q` before every commit. Commit is blocked if any step fails.

These hooks enforce quality gates and security boundaries without manual intervention.

## Progressive Disclosure

For domain-specific context, read these files only when the task requires it:
- Database schema details → `docs/database-schema.md`
- API specification → `docs/api-spec.md`
- Deployment guide → `docs/deployment.md`
- Environment variables → `.env.example`
