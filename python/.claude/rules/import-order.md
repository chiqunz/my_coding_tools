---
description: Enforce Python import ordering conventions
globs: "**/*.py"
---

# Import Order Rules

Imports MUST follow this order (ruff handles this automatically via `ruff check --fix`):

1. **Standard library** — `import os`, `from pathlib import Path`
2. **Third-party** — `import fastapi`, `from pydantic import BaseModel`
3. **Local/project** — `from app.core.service import UserService`

Blank line between each group. Use absolute imports from `app.*`, never relative imports with dots.

After writing any Python file, run:
```bash
uv run ruff check --fix <filepath>
uv run ruff format <filepath>
```
