---
name: ts-bug-scan
description: Scan TypeScript/React code for potential bugs, security issues, and common pitfalls.
triggers:
  - "scan for bugs"
  - "find bugs"
  - "security scan"
  - "check security"
  - "bug scan"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# TypeScript Bug Scanner Skill

## When Triggered

Scan the TypeScript codebase for potential bugs, security vulnerabilities, and runtime pitfalls.

## Steps

### 1. Type Safety Holes (most common TS bug source)

```bash
# Any type = potential runtime crash
grep -rn ": any\b\|as any\b" src/ --include="*.ts" --include="*.tsx"

# Non-null assertions = hiding null bugs
grep -rn "\!\\." src/ --include="*.ts" --include="*.tsx" | grep -v "node_modules\|\.test\." | head -20

# Type assertions on external data = bypassing validation
grep -rn " as [A-Z]" src/ --include="*.ts" --include="*.tsx" | grep -v "as const\|as React\|\.test\." | head -20
```

### 2. React Bug Patterns

```bash
# Missing key prop in lists
grep -rn "\.map(" src/ --include="*.tsx" -A 5 | grep -v "key=" | grep "return\|=>" | head -15

# useEffect missing deps or cleanup
grep -rn "useEffect" src/ --include="*.tsx" --include="*.ts" -A 15 | grep "\[\]" | head -10

# useState with object/array (mutation risk)
grep -rn "useState<.*\[\]\|useState<.*{" src/ --include="*.tsx" | head -10

# Stale closure in useCallback/useMemo
grep -rn "useCallback\|useMemo" src/ --include="*.tsx" -A 5 | grep "\[\]" | head -10

# Direct DOM access (breaks SSR)
grep -rn "document\.\|window\." src/ --include="*.tsx" --include="*.ts" | grep -v "typeof window\|typeof document" | head -10
```

### 3. Async Bug Patterns

```bash
# Missing await (returns Promise instead of value)
grep -rn "async " src/ --include="*.ts" --include="*.tsx" -A 10 | grep "return " | grep -v "await\|Promise" | head -10

# Unhandled promise rejection
grep -rn "\.then(" src/ --include="*.ts" --include="*.tsx" | grep -v "\.catch\|await" | head -10

# fetch without error handling
grep -rn "fetch(" src/ --include="*.ts" --include="*.tsx" -A 3 | grep -v "catch\|ok\|status\|error" | head -10
```

### 4. Security Scan

```bash
# Dependency vulnerabilities
pnpm audit 2>&1

# Hardcoded secrets
grep -rni "password\|secret\|api_key\|token\|private_key" src/ --include="*.ts" --include="*.tsx" | grep "=\|:" | grep -v "\.test\.\|\.spec\.\|type\|interface" | head -10

# dangerouslySetInnerHTML (XSS risk)
grep -rn "dangerouslySetInnerHTML\|innerHTML" src/ --include="*.tsx" | head -5

# eval or Function constructor
grep -rn "eval(\|new Function(" src/ --include="*.ts" --include="*.tsx" | head -5

# Unsanitized URL construction
grep -rn "href=.*\$\|src=.*\$\|window.location\s*=" src/ --include="*.tsx" | head -5
```

### 5. Next.js Specific (if applicable)

```bash
# Client components importing server-only code
grep -rn "'use client'" src/ --include="*.tsx" -l | xargs grep -l "import.*server\|import.*db\|import.*prisma" 2>/dev/null

# Missing 'use client' directive (uses hooks without it)
grep -rn "useState\|useEffect\|useContext\|useRef" src/ --include="*.tsx" -l | xargs grep -L "'use client'" 2>/dev/null | head -5
```

### 6. Generate Report

Structured by severity: Critical → High → Medium → Low.
Each finding includes file:line, what, why, and concrete fix.
