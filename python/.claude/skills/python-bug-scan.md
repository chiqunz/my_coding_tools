---
name: python-bug-scan
description: Scan Python code for potential bugs, security vulnerabilities, and common pitfalls using static analysis tools and pattern matching.
triggers:
  - "scan for bugs"
  - "find bugs"
  - "security scan"
  - "check security"
  - "vulnerability scan"
  - "bug scan"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# Python Bug Scanner Skill

## When Triggered

Scan the Python codebase for potential bugs, security vulnerabilities, and common runtime pitfalls.

## Steps

### 1. Security Scan (bandit)

```bash
# Install if missing
uv add --dev bandit 2>/dev/null

# Full security scan with severity and confidence
uv run bandit -r src/ -ll -ii --format txt 2>&1

# High-severity only
uv run bandit -r src/ -ll -ii --severity-level high 2>&1
```

**Critical patterns to flag immediately:**
- `B105/B106/B107` — Hardcoded passwords, secrets, or tokens
- `B301/B302` — Pickle/marshal deserialization (arbitrary code execution)
- `B307` — `eval()` usage
- `B501` — HTTPS requests with `verify=False`
- `B602/B603` — Subprocess with `shell=True`
- `B608` — Possible SQL injection via string formatting
- `B324` — Insecure hash functions (MD5, SHA1)

### 2. Bug-Prone Pattern Detection (ruff bugbear + pylint)

```bash
# Bugbear rules — likely bugs and design problems
uv run ruff check src/ --select B --statistics 2>&1

# Pylint rules — broad code quality issues
uv run ruff check src/ --select PL --statistics 2>&1

# Error-prone patterns
uv run ruff check src/ --select E,W,F --statistics 2>&1
```

**Key bugbear rules:**
| Rule | Bug Pattern |
|------|-------------|
| B006 | Mutable default argument (`def f(x=[])`) — shared state between calls |
| B007 | Unused loop variable (logic error) |
| B008 | Function call in default argument (evaluated once at import) |
| B009/B010 | `getattr`/`setattr` with constant string (use dot notation) |
| B017 | `pytest.raises` without `match` (too broad) |
| B023 | Function variable binding in loop (closure capture bug) |
| B028 | `warnings.warn` without stacklevel |
| B904 | `raise` without `from` inside `except` (lost traceback) |

### 3. Manual Bug Pattern Search

Search for common Python pitfalls that tools often miss:

```bash
# Mutable default arguments (most common Python bug)
uv run ruff check src/ --select B006

# Exception handling anti-patterns
grep -rn "except:" src/ --include="*.py"              # bare except
grep -rn "except Exception:" src/ --include="*.py"     # too broad
grep -rn "pass$" src/ --include="*.py" -A1 -B1        # silent exception swallowing

# Equality vs identity bugs
grep -rn "== None\|!= None" src/ --include="*.py"     # should be "is None"
grep -rn "== True\|== False" src/ --include="*.py"     # should be truthiness check

# Concurrency bugs
grep -rn "\.result()\|\.wait()" src/ --include="*.py"  # sync call in async context
grep -rn "time\.sleep" src/ --include="*.py"           # blocking in async

# Resource leaks
grep -rn "open(" src/ --include="*.py" | grep -v "with "  # file handle not closed

# f-string without f prefix
grep -rn "'{.*}'" src/ --include="*.py" | grep -v "f'" | head -20

# Hardcoded secrets
grep -rn -i "password\|secret\|token\|api_key" src/ --include="*.py" | grep "=" | head -20
```

### 4. Dependency Vulnerability Audit

```bash
# Install if missing
uv add --dev pip-audit 2>/dev/null

# Audit all installed packages for known CVEs
uv run pip-audit 2>&1

# Check for outdated packages
uv pip list --outdated 2>&1 | head -20
```

### 5. Dead Code Scan (vulture)

Dead code is a bug magnet — it misleads readers and accumulates rot.

```bash
# Install if missing
uv add --dev vulture 2>/dev/null

# Find unused code (80%+ confidence)
uv run vulture src/ --min-confidence 80 2>&1
```

### 6. Async Bug Patterns

For async codebases, check for concurrency-specific bugs:

```bash
# Missing await (most common async bug)
grep -rn "async def" src/ --include="*.py" -A 20 | grep -B5 "return.*coroutine\|<coroutine"

# Sync I/O in async context
grep -rn "requests\.\|urllib\.\|open(" src/ --include="*.py" | grep -v "aiohttp\|httpx\|aiofiles"

# Missing CancellationToken equivalent (asyncio.shield / timeout)
grep -rn "await " src/ --include="*.py" | grep -v "timeout\|wait_for\|shield" | head -10
```

### 7. Generate Bug Report

Compile all findings into a structured report, ordered by severity:

```markdown
## Bug Scan Report — [date]

### Critical (fix immediately)
- [ ] [file:line] Description of issue

### High (fix before next release)
- [ ] [file:line] Description

### Medium (fix when touching this code)
- [ ] [file:line] Description

### Low (nice to fix)
- [ ] [file:line] Description

### Dependencies
- Vulnerable: [count] packages
- Action: [upgrade commands]
```

For each finding, provide:
1. **What** — the exact issue and line
2. **Why** — why it's a bug or vulnerability
3. **Fix** — concrete code change to resolve it
