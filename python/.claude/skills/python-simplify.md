---
name: python-simplify
description: Simplify Python code — reduce complexity, eliminate redundancy, modernize syntax, and improve readability without changing behavior.
triggers:
  - "simplify"
  - "simplify code"
  - "reduce complexity"
  - "make simpler"
  - "clean up code"
  - "too complex"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# Python Code Simplification Skill

## When Triggered

Systematically simplify Python code to reduce cognitive complexity, eliminate redundancy, and improve readability — all while preserving exact behavior.

## Philosophy

Simplification is NOT about being clever. It's about making code **obvious**. Every change must make the code easier for the next reader to understand in under 5 seconds.

## Steps

### 1. Measure Current Complexity

Before changing anything, baseline the complexity:

```bash
# Cyclomatic complexity of the target file/directory
uv run radon cc <filepath> -a -s

# Lines of code
uv run radon raw <filepath> -s
```

### 2. Apply Simplification Patterns (ordered by impact)

Work through these patterns top-to-bottom on the target code:

#### A. Flatten Nested Conditionals → Early Returns (highest impact)

```python
# BEFORE — deeply nested, hard to follow
def process_order(order):
    if order is not None:
        if order.is_valid:
            if order.has_items:
                total = calculate_total(order)
                if total > 0:
                    return submit(order, total)
                else:
                    return Error("Empty total")
            else:
                return Error("No items")
        else:
            return Error("Invalid order")
    else:
        return Error("No order")

# AFTER — flat, each guard clause is independent
def process_order(order: Order | None) -> Result:
    if order is None:
        return Error("No order")
    if not order.is_valid:
        return Error("Invalid order")
    if not order.has_items:
        return Error("No items")
    total = calculate_total(order)
    if total <= 0:
        return Error("Empty total")
    return submit(order, total)
```

#### B. Replace Loops with Comprehensions / Builtins

```python
# BEFORE
result = []
for item in items:
    if item.is_active:
        result.append(item.name)

# AFTER
result = [item.name for item in items if item.is_active]

# BEFORE
found = False
for item in items:
    if item.id == target_id:
        found = True
        break

# AFTER
found = any(item.id == target_id for item in items)
```

#### C. Eliminate Redundant Boolean Logic

```python
# BEFORE
if condition == True:    →  if condition:
if condition == False:   →  if not condition:
if len(items) > 0:       →  if items:
if len(items) == 0:      →  if not items:
if x is not None:
    return x
else:
    return default       →  return x if x is not None else default
                          →  return x or default  # (if falsy values are ok)
```

#### D. Use Structural Pattern Matching (Python 3.10+)

```python
# BEFORE
if status == "pending":
    handle_pending()
elif status == "active":
    handle_active()
elif status == "cancelled":
    handle_cancelled()
else:
    raise ValueError(f"Unknown: {status}")

# AFTER
match status:
    case "pending":
        handle_pending()
    case "active":
        handle_active()
    case "cancelled":
        handle_cancelled()
    case _:
        raise ValueError(f"Unknown: {status}")
```

#### E. Extract Long Functions → Small Focused Functions

If a function does more than one thing, split it. Each function should have one clear purpose. Signs of a function that needs splitting:
- More than 20 lines of logic
- Multiple levels of indentation
- Comments separating "sections" within the function
- More than 3-4 parameters
- Name contains "and" (e.g., `validate_and_save`)

#### F. Replace Magic Numbers / Strings with Constants

```python
# BEFORE
if retries > 3:
    await asyncio.sleep(60)

# AFTER
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 60

if retries > MAX_RETRIES:
    await asyncio.sleep(RETRY_BACKOFF_SECONDS)
```

#### G. Use Modern Python Syntax (via ruff's UP rules)

```bash
# Auto-apply pyupgrade rules
uv run ruff check <filepath> --select UP --fix
```

This handles:
- `typing.Optional[X]` → `X | None`
- `typing.List[X]` → `list[X]`
- `typing.Dict` → `dict`
- `"{}.format(x)"` → `f"{x}"`
- `super(ClassName, self)` → `super()`
- `open()` without encoding → `open(encoding="utf-8")`

#### H. Use `ruff` Simplification Rules

```bash
# Auto-apply simplification rules
uv run ruff check <filepath> --select SIM,C4,RET,PIE --fix
```

This catches:
- `SIM` — collapsible if-statements, unnecessary dict/list calls, ternary opportunities
- `C4` — unnecessary list/dict comprehension wrappers
- `RET` — unnecessary `else` after `return`, single-expression functions
- `PIE` — unnecessary `pass`, redundant `dict.get` patterns

### 3. Run Tests After Every Change

```bash
uv run pytest <relevant tests> -v --tb=short
```

Never simplify code that breaks tests. If a test fails, revert and investigate.

### 4. Re-measure Complexity

```bash
uv run radon cc <filepath> -a -s
```

Compare before/after. Report the improvement.

### 5. Final Quality Gates

```bash
uv run ruff check --fix <filepath>
uv run ruff format <filepath>
uv run mypy <filepath>
uv run pytest <relevant tests> -v
```

## Rules

- **NEVER change behavior.** Simplification is a refactoring — inputs/outputs must remain identical.
- **NEVER remove error handling** to make code "simpler." Error handling is essential complexity.
- **ONE pattern at a time.** Make a change, run tests, move to the next.
- **If in doubt, don't simplify.** Clarity beats brevity. A 5-line `if/elif` can be clearer than a dense one-liner.
