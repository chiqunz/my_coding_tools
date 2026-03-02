---
description: Enforce TypeScript strict type safety rules
globs: "**/*.{ts,tsx}"
---

# Type Safety Rules

1. `any` is **FORBIDDEN** — use `unknown` with type narrowing or generic parameters
2. No TypeScript `enum` — use `type Status = 'active' | 'inactive'`
3. No `as` type assertions on external data — use `zodSchema.parse(data)`
4. No `// @ts-ignore` or `// @ts-expect-error` — fix the underlying type issue
5. All Zod schemas must have inferred types: `type X = z.infer<typeof xSchema>`
6. Function return types should be explicit for public API functions
7. Use `satisfies` operator for type checking without widening: `const config = { ... } satisfies Config`
