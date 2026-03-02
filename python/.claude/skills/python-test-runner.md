---
name: python-test-runner
description: Run Python tests with pytest, analyze failures, and fix issues autonomously.
triggers:
  - "run tests"
  - "test this"
  - "verify tests pass"
  - "check tests"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# Python Test Runner Skill

## When Triggered

Run Python tests using pytest when the user asks to test code or verify changes.

## Steps

1. **Identify test files** related to the modified source files:
   - Source: `src/app/core/service.py` → Test: `tests/unit/core/test_service.py`
   - Source: `src/app/api/v1/routes/users.py` → Test: `tests/integration/api/v1/test_users.py`

2. **Run targeted tests first** (fast feedback):
   ```bash
   uv run pytest <test_file> -v --tb=short
   ```

3. **If tests fail**, read the failure output carefully:
   - Identify the root cause (assertion error, import error, fixture issue)
   - Read the relevant source and test files
   - Fix the issue in either source or test code
   - Re-run the specific failing test

4. **Run broader tests** after fixing:
   ```bash
   uv run pytest tests/ -v --tb=short -x  # stop on first failure
   ```

5. **Run with coverage** if requested:
   ```bash
   uv run pytest --cov=src --cov-report=term-missing tests/
   ```

## Important Rules

- Always use `uv run pytest`, never bare `pytest`
- Use `-v` for verbose output to see individual test names
- Use `--tb=short` for concise tracebacks
- Use `-x` to stop on first failure during debugging
- Use `-k "test_name"` to filter specific tests
- For async tests, ensure `pytest.mark.asyncio` decorator is present
- Never modify tests just to make them pass — fix the source code
