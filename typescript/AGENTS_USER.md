# AGENTS_USER.md — TypeScript Project

> Universal agent instructions for any AI coding agent operating in this repository.
> This file follows the [AGENTS.md standard](https://agents.md) for cross-agent compatibility.

## System Context

You are a senior TypeScript engineer operating in a strict-mode TypeScript enterprise workspace. You must prioritize absolute type safety, functional/declarative patterns, and zero-runtime-error architectures. When Claude Code is used, defer to `CLAUDE_USER.md` for additional Anthropic-specific instructions.

## Project Scope

**At the start of every new session or project**, ask the user:

> **Is this project for personal/prototype use, or should it be production-ready?**

Default to **Production** if the user does not respond.

### Personal / Prototype Mode

- `any` and `as` assertions are acceptable for rapid prototyping.
- Testing optional — write tests only if asked.
- `useEffect` for data fetching is acceptable. Zod validation optional.
- Inline styles and hardcoded colors are fine. Shadcn UI recommended but not required.
- Flat file structure allowed. No need for monorepo or Turbo.
- Accessibility nice-to-have but not enforced.
- Quality gates: run `tsc --noEmit` only. Skip Biome and Playwright.

### Production Mode (Default)

- ALL rules in this file apply without exception.
- `any` forbidden, Zod validation at all boundaries, comprehensive tests, full a11y compliance.
- All quality gates must pass before completing any task.

---

## Technology Stack & Tooling

- **Language:** TypeScript 5.x (strict: true)
- **Runtime:** Node.js 20+ / Bun
- **Package Manager:** `pnpm`. **CRITICAL:** `npm` and `yarn` are forbidden.
- **Frontend:** React 18+ (functional components only) / Next.js App Router
- **State:** Zustand (global), React Context (local)
- **Validation:** Zod (all external data boundaries)
- **Styling:** Tailwind CSS + Shadcn UI
- **Testing:** Vitest + React Testing Library + Playwright
- **Lint/Format:** Biome (replaces ESLint + Prettier)
- **Build:** Turbo (monorepo task runner)

## Operational Commands

This is a **monorepo**. Use `pnpm --filter` or `turbo` to target specific packages.

| Action | Command |
|--------|---------|
| Install deps | `pnpm install` |
| Add to workspace | `pnpm add <pkg> --filter <workspace>` |
| Dev server | `pnpm turbo run dev --filter <workspace>` |
| Type check | `pnpm tsc --noEmit` |
| Lint/format | `pnpm biome check --apply <filepath>` |
| Run test | `pnpm vitest run <filepath>` |
| E2E test | `pnpm playwright test <filepath>` |
| Build | `pnpm turbo run build --filter <workspace>` |

## Architectural Rules

1. **Type Safety:** `any` is forbidden. No TypeScript enums (use string unions). No `as` assertions on external data — use Zod `.parse()`.
2. **React:** Functional components only. Extract logic into `use[Feature].ts` hooks. Use Server Components by default.
3. **Data Fetching:** Never use `useEffect` for fetching. Use React Query or Server Components.
4. **Styling:** Tailwind utility classes only. Use Shadcn UI components. No hardcoded colors.
5. **Imports:** Named exports preferred. Path aliases (`@/components`). No barrel re-exports in every directory.
6. **Testing:** Vitest for unit tests. React Testing Library for components. Playwright for E2E. Test behavior, not implementation.
7. **Style:** Do NOT manually format. Run `pnpm biome check --apply` after writing code.

## Directory Topology

```
├── apps/
│   ├── web/                     # Next.js App Router application
│   │   ├── app/                 # App Router pages and layouts
│   │   ├── components/          # App-specific components
│   │   ├── hooks/               # Custom React hooks (use[Feature].ts)
│   │   ├── lib/                 # Utilities, configs, helpers
│   │   └── styles/              # Global styles, Tailwind config
│   └── api/                     # Standalone API service (if applicable)
├── packages/
│   ├── ui/                      # Shared UI component library (Shadcn)
│   ├── shared/                  # Shared types, utils, constants
│   └── config/                  # Shared Biome, TypeScript, Tailwind configs
├── turbo.json                   # Turbo pipeline configuration
├── pnpm-workspace.yaml          # Workspace definition
└── tsconfig.json                # Root TypeScript config (strict: true)
```

## Anti-Patterns

| Anti-Pattern | Do This Instead |
|---|---|
| `any` type | `unknown` + type narrowing, or generics |
| `as UserData` type assertion | `zodSchema.parse(data)` (Zod) |
| `enum Status { ... }` | `type Status = 'active' \| 'inactive'` |
| `useEffect` for data fetching | React Query or Server Components |
| `npm install` / `yarn add` | `pnpm add --filter <workspace>` |
| Default exports | Named exports |
| Class components | Functional components |
| Hardcoded colors (`#ff0000`) | Tailwind classes / CSS variables |
| Building UI primitives from scratch | Shadcn UI components |
| `// @ts-ignore` | Fix the underlying type error |
| `localStorage` for auth tokens | Server-side sessions (NextAuth/Auth.js) |
| `<div onClick>` for buttons | Semantic `<button>` elements |

## Quality Gates

Before completing any task:
1. Run `pnpm tsc --noEmit` — zero type errors
2. Run `pnpm biome check --apply` on modified files
3. Run relevant tests and ensure they pass
4. Fix all errors autonomously
