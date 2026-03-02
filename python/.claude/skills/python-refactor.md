---
name: python-refactor
description: Refactor Python code while maintaining functionality, improving type safety, and following project conventions.
triggers:
  - "refactor"
  - "clean up"
  - "improve code"
  - "simplify"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# Python Refactoring Skill

## When Triggered

Refactor Python code to improve quality while preserving behavior.

## Steps

1. **Read and understand** the current code and its tests
2. **Identify refactoring opportunities**:
   - Missing type hints → Add full annotations
   - `Optional[X]` → `X | None`
   - `Union[X, Y]` → `X | Y`
   - `List[str]`, `Dict[str, int]` → `list[str]`, `dict[str, int]`
   - `Any` type → Proper generics or constrained types
   - Long functions → Extract into smaller, focused functions
   - Repeated patterns → DRY with shared utilities
   - `os.getenv()` calls → `pydantic-settings` BaseSettings
   - `print()` → `logging.getLogger(__name__)`
   - `requests` → `httpx`
   - Class-based patterns → Functional patterns where appropriate

3. **Make changes incrementally** — one refactoring concern at a time

4. **Run tests after each change**:
   ```bash
   uv run pytest <relevant tests> -v
   ```

5. **Run full quality gates**:
   ```bash
   uv run ruff check --fix <modified files>
   uv run ruff format <modified files>
   uv run mypy <modified files>
   ```

## Refactoring Checklist

- [ ] All functions have complete type hints (params + return)
- [ ] No use of `Any` type
- [ ] Modern union syntax (`X | None`)
- [ ] Built-in generics (`list`, `dict`, `tuple`, `set`)
- [ ] Pydantic models for all data boundaries
- [ ] Proper error handling (no bare `except:`)
- [ ] Async functions for I/O operations
- [ ] No mutable default arguments
- [ ] Descriptive variable/function names
- [ ] Tests still pass after changes
