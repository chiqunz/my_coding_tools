---
name: ts-refactor
description: Refactor TypeScript code to improve type safety, remove anti-patterns, and follow project conventions.
triggers:
  - "refactor"
  - "clean up"
  - "improve types"
  - "fix types"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# TypeScript Refactoring Skill

## When Triggered

Refactor TypeScript code to improve quality while preserving behavior.

## Steps

1. **Read and understand** the current code and its tests
2. **Identify refactoring opportunities**:
   - `any` type → `unknown` + narrowing, or proper generics
   - `as TypeName` on external data → Zod `.parse()`
   - `enum` → string union types (`type X = 'a' | 'b'`)
   - `useEffect` for data fetching → React Query / Server Components
   - Class components → functional components
   - Default exports → named exports
   - `// @ts-ignore` → Fix the actual type issue
   - Manual null checks → optional chaining (`?.`) and nullish coalescing (`??`)
   - Imperative array manipulation → `map`, `filter`, `reduce`
   - Mutable state → immutable patterns
   - Hardcoded strings → const objects or union types
   - `npm`/`yarn` references → `pnpm`

3. **Make changes incrementally** — one concern at a time

4. **Run tests after each change**:
   ```bash
   pnpm vitest run <relevant tests>
   ```

5. **Run full quality gates**:
   ```bash
   pnpm tsc --noEmit
   pnpm biome check --apply <modified files>
   ```

## Refactoring Checklist

- [ ] Zero `any` types
- [ ] Zero `as` assertions on external data
- [ ] Zero `// @ts-ignore` comments
- [ ] No TypeScript enums (string unions only)
- [ ] All external data parsed with Zod
- [ ] Functional components only
- [ ] Named exports
- [ ] No `useEffect` for data fetching
- [ ] Tailwind classes (no hardcoded colors)
- [ ] Tests still pass
