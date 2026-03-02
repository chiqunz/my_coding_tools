---
description: Enforce strict type safety rules for Python code
globs: "**/*.py"
---

# Type Safety Rules

1. Every function MUST have full type annotations (all parameters + return type)
2. Use modern syntax:
   - `str | None` NOT `Optional[str]`
   - `list[str]` NOT `List[str]`
   - `dict[str, int]` NOT `Dict[str, int]`
3. `Any` is **FORBIDDEN** — use TypeVar, Generic, or Protocol instead
4. All Pydantic models use `BaseModel` with field validators
5. External data MUST be validated through Pydantic before use
6. Run `uv run mypy --strict <filepath>` to verify
