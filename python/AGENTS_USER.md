# AGENTS_USER.md — Python Project

> Universal agent instructions for any AI coding agent operating in this repository.
> This file follows the [AGENTS.md standard](https://agents.md) for cross-agent compatibility.

## System Context

You are a senior Python architecture agent working in a modern Python 3.12+ repository. You must prioritize type safety, deterministic dependency management, and async-first patterns. When Claude Code is used, defer to `CLAUDE_USER.md` for additional Anthropic-specific instructions.

## Project Scope

**At the start of every new session or project**, ask the user:

> **Is this project for personal/prototype use, or should it be production-ready?**

Default to **Production** if the user does not respond.

### Personal / Prototype Mode

- Type hints recommended but not enforced. `Any` is acceptable.
- Testing optional — write tests only if asked.
- `print()` acceptable for debugging. Structured logging not required.
- Basic try/except is fine. Custom exceptions optional.
- Flat file structure allowed. Layered architecture not required.
- Quality gates: run `ruff format` only. Skip `mypy --strict` and coverage.

### Production Mode (Default)

- ALL rules in this file apply without exception.
- Full type safety, structured logging, comprehensive tests, security scanning.
- All quality gates must pass before completing any task.

---

## Technology Stack & Tooling

- **Language:** Python 3.12+ with strict type hints
- **Package Manager:** `uv` (Astral). **CRITICAL:** `pip`, `poetry`, and `conda` are forbidden.
- **Formatting & Linting:** `ruff` (replaces black, isort, flake8, pylint)
- **Type Checking:** `mypy` in strict mode
- **Web Framework:** FastAPI with Pydantic v2
- **Testing:** pytest + pytest-asyncio + pytest-cov
- **HTTP Client:** httpx (async-native, not requests)

## Operational Commands

Prefer file-scoped checks over full-suite executions.

| Action | Command |
|--------|---------|
| Add dependency | `uv add <package>` |
| Add dev dependency | `uv add --dev <package>` |
| Sync environment | `uv sync` |
| Run dev server | `uv run uvicorn app.main:app --reload` |
| Format file | `uv run ruff format <filepath>` |
| Lint file | `uv run ruff check --fix <filepath>` |
| Type check file | `uv run mypy <filepath>` |
| Run specific test | `uv run pytest <filepath> -v` |
| Run all tests | `uv run pytest --cov=src tests/` |

## Architectural Rules

1. **Dependencies:** All managed in `pyproject.toml`. Never use `requirements.txt`.
2. **Type Safety:** Every function has full type hints. `Any` is forbidden. Use `str | None` not `Optional[str]`.
3. **API Design:** Endpoints are thin controllers. All data shapes use Pydantic `BaseModel`. Use `Depends()` for DI.
4. **Async:** Default to `async def` for I/O. Use `asyncio.gather()` for concurrency. Never use `.result` or blocking calls in async context.
5. **Testing:** Mirror source structure. Use `pytest.fixture`, `pytest.mark.asyncio`, `httpx.AsyncClient` for integration tests.
6. **Error Handling:** Custom exceptions in `core/exceptions.py`. Use FastAPI exception handlers. Never catch bare `Exception`.
7. **Style:** Do NOT manually format. Run `ruff format` after writing code.

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

## Anti-Patterns

| Anti-Pattern | Do This Instead |
|---|---|
| `from typing import Optional, Union, List, Dict` | Built-in generics: `list[str]`, `dict[str, int]`, `str \| None` |
| `requirements.txt` | `pyproject.toml` with `uv` |
| `requests` library for HTTP | `httpx` (async-native) |
| Bare `print()` for logging | `import logging; logger = logging.getLogger(__name__)` |
| Global mutable state | Dependency injection via `Depends()` |
| `os.getenv()` scattered everywhere | `pydantic-settings` `BaseSettings` class |
| Manual string SQL queries | SQLAlchemy ORM or parameterized queries |
| `class MyTest(unittest.TestCase)` | Plain functions with `pytest` + fixtures |
| Hardcoded secrets in source code | Environment variables via `pydantic-settings` |
| `random` for security tokens | `secrets` module |

## Quality Gates

Before completing any task:
1. Run `uv run ruff check --fix` on modified files
2. Run `uv run ruff format` on modified files
3. Run `uv run mypy` on modified files
4. Run relevant tests and ensure they pass
5. Fix all errors autonomously
