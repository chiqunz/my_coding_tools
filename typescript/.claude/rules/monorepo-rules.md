---
description: Enforce monorepo workspace conventions
globs: "**/*.{ts,tsx,json}"
---

# Monorepo Rules

1. **NEVER** use `npm` or `yarn` — this is a `pnpm` workspace
2. Add packages to specific workspaces: `pnpm add <pkg> --filter <workspace>`
3. Run tasks through Turbo: `pnpm turbo run <task> --filter <workspace>`
4. Never run global builds — target specific workspaces for fast feedback
5. Import shared packages using workspace protocol: `"@repo/ui": "workspace:*"`
6. Shared config lives in `packages/config/` — don't duplicate across workspaces
7. Path aliases use `@/` prefix configured in each workspace's `tsconfig.json`
