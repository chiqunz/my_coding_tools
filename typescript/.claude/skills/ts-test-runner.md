---
name: ts-test-runner
description: Run TypeScript tests with Vitest, analyze failures, and fix issues autonomously.
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

# TypeScript Test Runner Skill

## When Triggered

Run TypeScript tests using Vitest when the user asks to test code or verify changes.

## Steps

1. **Identify test files** related to the modified source files:
   - Source: `UserCard.tsx` → Test: `UserCard.test.tsx` (co-located)
   - Source: `lib/utils.ts` → Test: `lib/utils.test.ts` (co-located)
   - E2E: `e2e/auth.spec.ts` (Playwright)

2. **Run targeted tests first** (fast feedback):
   ```bash
   pnpm vitest run <test_file> --reporter=verbose
   ```

3. **If tests fail**, read the failure output carefully:
   - Type errors → Check prop types, Zod schemas, function signatures
   - Component tests → Check selectors, user interactions, async assertions
   - Fix the issue in source or test code
   - Re-run the specific failing test

4. **Run broader tests** after fixing:
   ```bash
   pnpm vitest run --reporter=verbose
   ```

5. **Run with coverage** if requested:
   ```bash
   pnpm vitest run --coverage
   ```

6. **For E2E tests**:
   ```bash
   pnpm playwright test <test_file> --reporter=list
   ```

## Important Rules

- Always use `pnpm vitest run`, never bare `vitest`
- Use `--reporter=verbose` for detailed output
- For component tests, ensure proper async handling with `waitFor`
- For E2E tests with Playwright, use `page.getByRole()` / `page.getByText()` selectors
- Never modify tests just to make them pass — fix the source code
- Run `pnpm tsc --noEmit` alongside tests to catch type errors
