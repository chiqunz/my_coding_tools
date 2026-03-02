---
name: python-code-audit
description: Comprehensive code quality audit — complexity analysis, dead code detection, type coverage, dependency health, and code smells.
triggers:
  - "audit code"
  - "code audit"
  - "check code quality"
  - "code health"
  - "code review"
  - "analyze code"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# Python Code Audit Skill

## When Triggered

Perform a comprehensive code quality audit of the Python codebase. Checks complexity, dead code, type coverage, dependency vulnerabilities, and common code smells.

## Steps

### 1. Cyclomatic & Cognitive Complexity (radon)

Measure function-level complexity. Anything rated C or worse needs refactoring.

```bash
# Install if missing
uv add --dev radon

# Cyclomatic complexity — flag C and worse (score > 10)
uv run radon cc src/ -a -nc

# Maintainability Index — flag B and worse (< 20 = unmaintainable)
uv run radon mi src/ -n B

# Raw metrics (LOC, LLOC, SLOC, comments)
uv run radon raw src/ -s
```

**Interpret results:**
| Grade | CC Score | Action |
|-------|----------|--------|
| A | 1–5 | Good — no action |
| B | 6–10 | Acceptable — monitor |
| C | 11–15 | **Refactor** — extract helper functions |
| D | 16–20 | **Urgent** — split into smaller units |
| F | 21+ | **Critical** — redesign entirely |

For each function rated C or worse:
- Read the function
- Identify nested conditionals, long parameter lists, multiple responsibilities
- Propose concrete refactoring (extract method, early returns, strategy pattern)

### 2. Dead Code Detection (vulture)

Find unused functions, variables, imports, and unreachable code.

```bash
# Install if missing
uv add --dev vulture

# Scan for dead code (default 60% confidence)
uv run vulture src/ --min-confidence 80

# If too many false positives, create a whitelist
uv run vulture src/ --make-whitelist > vulture_whitelist.py
uv run vulture src/ vulture_whitelist.py --min-confidence 80
```

For each finding:
- Verify it's truly unused (check tests, dynamic usage, framework hooks)
- If confirmed dead: remove it
- If false positive: add to whitelist

### 3. Type Coverage (mypy)

Measure how much of the codebase has type annotations.

```bash
# Strict check — shows all type errors
uv run mypy src/ --strict --no-error-summary 2>&1 | head -50

# Count untyped functions
uv run mypy src/ --strict 2>&1 | grep -c "Function is missing"

# Per-module report
uv run mypy src/ --strict --txt-report mypy-report/
```

Report:
- Total files checked
- Number of type errors
- Files with most errors (prioritize these)
- Untyped function count

### 4. Security Vulnerability Scan (bandit)

Scan for common Python security issues.

```bash
# Install if missing
uv add --dev bandit

# Full scan — all severity levels
uv run bandit -r src/ -f json 2>/dev/null | python3 -m json.tool | head -80

# Summary only
uv run bandit -r src/ -ll -ii 2>&1 | tail -20

# Skip tests directory (usually has intentional "bad" patterns)
uv run bandit -r src/ --exclude tests/
```

**Key issues to flag:**
| Bandit ID | Issue | Severity |
|-----------|-------|----------|
| B101 | `assert` used (stripped in `-O` mode) | Low |
| B105/B106 | Hardcoded passwords | High |
| B301/B302 | Pickle usage (arbitrary code exec) | High |
| B307 | `eval()` usage | High |
| B501 | SSL verification disabled | High |
| B602/B603 | Subprocess shell injection | Medium |
| B608 | SQL injection | High |

### 5. Dependency Vulnerability Audit (pip-audit)

Check installed packages for known CVEs.

```bash
# Install if missing
uv add --dev pip-audit

# Audit all dependencies
uv run pip-audit

# JSON output for parsing
uv run pip-audit -f json 2>/dev/null | python3 -m json.tool
```

For each vulnerability:
- Report package name, installed version, fix version, CVE ID
- If a fix version exists: update with `uv add <package>@<fix_version>`
- If no fix: report and suggest alternative packages

### 6. Code Smell Detection (ruff extended rules)

Use ruff's extended rule set to catch code smells beyond basic linting.

```bash
# Enable all relevant rule categories
uv run ruff check src/ --select E,W,F,I,N,UP,S,B,A,C4,DTZ,PIE,PT,RSE,RET,SLF,SIM,TID,TCH,ARG,ERA,PL,RUF --statistics
```

**Rule categories explained:**
- `UP` — pyupgrade: modernize syntax (old-style typing, deprecated patterns)
- `S` — bandit-equivalent security rules
- `B` — bugbear: likely bugs and design problems
- `SIM` — simplification: unnecessarily complex expressions
- `C4` — comprehension: simplifiable comprehensions/loops
- `RET` — return: unnecessary return/else patterns
- `ARG` — unused arguments
- `ERA` — commented-out code
- `PL` — pylint: broad code quality checks

### 7. Generate Audit Report

Compile all findings into a structured summary:

```markdown
## Code Audit Report — [date]

### Complexity
- Functions rated C+: [count]
- Worst offenders: [list top 5]

### Dead Code
- Unused functions: [count]
- Unused imports: [count]
- Unused variables: [count]

### Type Coverage
- Type errors (strict): [count]
- Untyped functions: [count]

### Security
- High severity: [count]
- Medium severity: [count]
- Findings: [list]

### Dependencies
- Vulnerable packages: [count]
- Outdated packages: [count]

### Action Items (prioritized)
1. [Most critical finding]
2. ...
```
