---
name: ts-code-audit
description: Comprehensive TypeScript code quality audit — type safety coverage, bundle analysis, dead code detection, dependency health, and complexity.
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

# TypeScript Code Audit Skill

## When Triggered

Perform a comprehensive code quality audit of the TypeScript codebase.

## Steps

### 1. Type Safety Audit

```bash
# Strict type check — count all errors
pnpm tsc --noEmit 2>&1 | tail -5

# Hunt for `any` usage
grep -rn ": any\b\|as any\b\|<any>" src/ --include="*.ts" --include="*.tsx" | wc -l
grep -rn ": any\b\|as any\b\|<any>" src/ --include="*.ts" --include="*.tsx"

# Hunt for type assertions on external data (should be Zod)
grep -rn " as [A-Z]" src/ --include="*.ts" --include="*.tsx" | grep -v "\.test\." | head -20

# Hunt for @ts-ignore / @ts-expect-error
grep -rn "@ts-ignore\|@ts-expect-error" src/ --include="*.ts" --include="*.tsx"

# Hunt for TypeScript enums (should be string unions)
grep -rn "^export enum\|^enum " src/ --include="*.ts" --include="*.tsx"
```

Report: count of `any`, type assertions, `@ts-ignore`, enums. Each is a type safety gap.

### 2. Dead Code & Unused Exports (knip)

```bash
# Install if missing
pnpm add -D knip --filter <workspace> 2>/dev/null

# Find unused files, exports, dependencies, and types
pnpm knip 2>&1 | head -60

# Unused dependencies only
pnpm knip --include dependencies 2>&1
```

### 3. Dependency Health

```bash
# Audit for known vulnerabilities
pnpm audit 2>&1

# Check for outdated packages
pnpm outdated 2>&1 | head -30

# Check bundle size impact (if next.js)
pnpm next build 2>&1 | grep -A 20 "Route (app)"
```

### 4. Complexity & Code Smells (Biome diagnostics)

```bash
# Full diagnostic scan — all categories
pnpm biome check src/ --diagnostic-level=warn 2>&1 | tail -30

# Complexity-related rules
pnpm biome check src/ --diagnostic-level=info 2>&1 | grep -i "complex\|cognitive" | head -20
```

### 5. React-Specific Audit (if applicable)

```bash
# Missing keys in lists
grep -rn "\.map(" src/ --include="*.tsx" -A 3 | grep -v "key=" | head -20

# useEffect without cleanup
grep -rn "useEffect" src/ --include="*.tsx" --include="*.ts" -A 10 | grep -B5 "^--$" | grep -v "return " | head -20

# Direct DOM manipulation (anti-pattern in React)
grep -rn "document\.\|window\." src/ --include="*.tsx" | grep -v "// safe\|SSR\|typeof window" | head -10

# useEffect for data fetching (should be React Query or Server Components)
grep -rn "useEffect" src/ --include="*.tsx" -A 5 | grep "fetch\|axios\|api\." | head -10
```

### 6. Generate Audit Report

Compile findings into:
- Type safety gaps (any count, assertions, ts-ignore)
- Dead code (unused files, exports, deps)
- Vulnerabilities (pnpm audit findings)
- Complexity hotspots
- React anti-patterns
- Prioritized action items
