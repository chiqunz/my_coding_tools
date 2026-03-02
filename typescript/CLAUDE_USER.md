# CLAUDE_USER.md — TypeScript Project

> This file is the single source of truth for Claude Code when operating in this repository.
> Strictly follow every rule below. When in doubt, re-read this file before generating code.

## System Identity

You are a senior TypeScript engineer agent operating in a modern, strict-mode TypeScript enterprise workspace. You must prioritize absolute type safety, functional/declarative patterns, and zero-runtime-error architectures.

## Project Scope

**At the start of every new session or project**, ask the user:

> **Is this project for personal/prototype use, or should it be production-ready?**

The user's answer determines which rule tier applies. Default to **Production** if the user does not respond or is unsure.

### Personal / Prototype Mode

When the user confirms this is a personal project, hackathon, prototype, or learning exercise:

- **Type safety:** `any` is acceptable for rapid prototyping. `as` assertions are permitted.
- **Testing:** Optional. Write tests only if the user asks. No minimum coverage.
- **React patterns:** Class components are still forbidden, but `useEffect` for data fetching is acceptable.
- **Styling:** Inline styles and hardcoded colors are acceptable. Shadcn UI is recommended but not required.
- **Error handling:** Basic try/catch is fine. Zod validation at boundaries is optional.
- **Architecture:** Flat file structure is acceptable. No need for monorepo setup or Turbo.
- **Accessibility:** Nice to have but not enforced.
- **Auth:** Simple patterns (localStorage tokens) are acceptable for local-only prototypes.
- **Quality gates:** Run `tsc --noEmit` only. Skip Biome, Vitest, and Playwright.
- **Documentation:** Minimal. Inline comments only when non-obvious.
- **Package manager:** `pnpm` is still required (not npm/yarn).

### Production Mode (Default)

When the user confirms this is production-bound, or does not specify:

- **ALL rules in this file apply without exception.**
- `any` is forbidden. All external data parsed with Zod.
- Comprehensive test coverage. E2E tests for critical user flows.
- Full accessibility compliance (WCAG 2.1 AA).
- Server-side auth with NextAuth.js. No secrets in client-side storage.
- Monorepo conventions with Turbo, Biome formatting, and Playwright E2E.
- All quality gates must pass before completing any task.
- Pre-commit hooks enforced.

---

## Technology Stack

| Layer            | Tool / Version                           |
|------------------|------------------------------------------|
| Language         | TypeScript 5.x (strict mode enforced)    |
| Runtime          | Node.js 20+ / Bun                       |
| Package Manager  | **pnpm** — `npm` and `yarn` are **forbidden** |
| Frontend         | React 18+ (functional components only) / Next.js (App Router) |
| State Management | Zustand (global) / React Context (local) |
| Data Validation  | Zod                                     |
| Styling          | Tailwind CSS + Shadcn UI                |
| Testing          | Vitest + React Testing Library + Playwright |
| Linting/Format   | Biome (replaces ESLint + Prettier)       |
| Build / Task     | Turbo (monorepo task runner)             |
| API Layer        | tRPC / Next.js Server Actions            |

## Directory Topology

```
├── apps/
│   ├── web/                     # Next.js App Router application
│   │   ├── app/                 # App Router pages and layouts
│   │   │   ├── (auth)/          # Route groups
│   │   │   ├── api/             # API route handlers
│   │   │   ├── layout.tsx       # Root layout
│   │   │   └── page.tsx         # Root page
│   │   ├── components/          # App-specific components
│   │   ├── hooks/               # Custom React hooks (use[Feature].ts)
│   │   ├── lib/                 # Utilities, configs, helpers
│   │   └── styles/              # Global styles, Tailwind config
│   └── api/                     # Standalone API service (if applicable)
├── packages/
│   ├── ui/                      # Shared UI component library (Shadcn)
│   │   └── src/components/ui/   # Shadcn components
│   ├── shared/                  # Shared types, utils, constants
│   └── config/                  # Shared Biome, TypeScript, Tailwind configs
├── turbo.json                   # Turbo pipeline configuration
├── pnpm-workspace.yaml          # Workspace definition
├── package.json                 # Root package.json
└── tsconfig.json                # Root TypeScript config (strict: true)
```

## Operational Commands

This is a **monorepo**. Always use `pnpm --filter` or `turbo` to target specific packages.

```bash
# Dependency management (NEVER use npm or yarn)
pnpm install
pnpm add <package> --filter <workspace>
pnpm add -D <package> --filter <workspace>

# Development
pnpm turbo run dev --filter web
pnpm turbo run dev --filter api

# Type checking (file-scoped for speed)
pnpm tsc --noEmit -p apps/web/tsconfig.json

# Lint and format (deterministic — do NOT format manually)
pnpm biome check --apply <path/to/file.ts>
pnpm biome check --apply apps/web/

# Run specific test
pnpm vitest run <path/to/file.test.ts>
pnpm vitest run --coverage

# Run E2E tests
pnpm playwright test <path/to/test.spec.ts>

# Build
pnpm turbo run build --filter web
```

## Architectural Rules

### 1. Absolute Type Safety (Non-Negotiable)

- **`any` is FORBIDDEN.** Use `unknown` with type narrowing, or generic type parameters.
- **No TypeScript Enums.** Use string union types: `type Status = 'pending' | 'active' | 'archived'`
- **No `as` assertions on external data.** Parse with Zod: `schema.parse(data)` or `schema.safeParse(data)`
- **No `// @ts-ignore` or `// @ts-expect-error`** — fix the type issue properly.
- Infer types from Zod schemas: `type User = z.infer<typeof userSchema>`

```typescript
// FORBIDDEN
const data = response.json() as UserData;
const value: any = getConfig();
enum Status { Active, Inactive }

// CORRECT
const data = userSchema.parse(await response.json());
const value: unknown = getConfig();
type Status = 'active' | 'inactive';
```

### 2. React Conventions

- **Functional components ONLY.** Class components are forbidden.
- Components must be small and focused. Extract logic into custom hooks (`use[Feature].ts`).
- Use `React.FC` sparingly — prefer explicit prop types and return types.
- Use `forwardRef` when wrapping native elements for component libraries.
- Server Components are default in Next.js App Router — only add `'use client'` when necessary.

```typescript
// Preferred pattern
interface UserCardProps {
  user: User;
  onSelect: (id: string) => void;
}

export function UserCard({ user, onSelect }: UserCardProps) {
  return (/* JSX */);
}
```

### 3. State & Data Fetching

- **NEVER use `useEffect` for data fetching.** Use React Query (`@tanstack/react-query`) or Server Components.
- Use Zustand for global client state. Use React Context for localized component trees.
- If `useEffect` is unavoidable, the dependency array MUST be exhaustive and include a cleanup function.
- Use `useMemo` and `useCallback` only when there's a measurable performance benefit — don't premature-optimize.

### 4. Styling

- Use Tailwind utility classes exclusively. No hardcoded hex colors or arbitrary CSS values.
- Use CSS variables defined in the design system for all colors and spacing.
- Use Shadcn UI components from `@/components/ui/` — never build basic components from scratch.
- If a Shadcn component is missing, install it via CLI: `pnpm dlx shadcn@latest add <component>`

### 5. Imports & Exports

- Use **named exports** (not default exports) except where frameworks require it (Next.js pages).
- Import order: Node builtins → external packages → internal absolute (`@/...`) → relative (`./...`)
- Use path aliases: `@/components`, `@/lib`, `@/hooks` (configured in `tsconfig.json`)
- Barrel exports (`index.ts`) only for public API surfaces of packages, not for every directory.

### 6. Error Handling

- Use Zod for all input validation at system boundaries.
- Create typed error classes extending `Error` with discriminated unions.
- Use `Result<T, E>` patterns for operations that can fail predictably (no thrown exceptions for control flow).
- In React, use Error Boundaries for UI crash recovery.

### 7. Testing

- Test files live next to source: `UserCard.tsx` → `UserCard.test.tsx`
- Use Vitest (not Jest) for unit/integration tests.
- Use React Testing Library — test behavior, not implementation.
- Use Playwright for E2E tests in `e2e/` directory.
- Mock external dependencies, not internal modules.

### 8. API Layer

- For internal full-stack apps, prefer **tRPC** for end-to-end type safety between client and server.
- For public-facing APIs or third-party consumers, use **Next.js Route Handlers** with explicit Zod validation.
- All API inputs MUST be validated with Zod schemas at the handler boundary.
- Use `next-safe-action` for type-safe Server Actions with built-in validation.
- Return consistent error shapes: `{ success: false, error: { code: string, message: string } }`.
- Use HTTP status codes correctly: 200 success, 201 created, 400 bad request, 401 unauthorized, 404 not found.

```typescript
// tRPC procedure example
export const userRouter = router({
  getById: publicProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ input }) => {
      return db.user.findUnique({ where: { id: input.id } });
    }),
});

// Next.js Route Handler example
export async function POST(request: Request) {
  const body = createUserSchema.safeParse(await request.json());
  if (!body.success) {
    return Response.json({ success: false, error: body.error.flatten() }, { status: 400 });
  }
  const user = await createUser(body.data);
  return Response.json({ success: true, data: user }, { status: 201 });
}
```

### 9. Authentication & Authorization

- Use **NextAuth.js (Auth.js)** for authentication in Next.js applications.
- Store session data server-side — never store sensitive tokens in `localStorage`.
- Use `middleware.ts` for route protection — redirect unauthenticated users before page load.
- Define role-based access patterns with TypeScript discriminated unions.
- Protect API routes by verifying the session in every handler.
- Use CSRF protection for all state-changing operations.

```typescript
// middleware.ts — Route protection
import { auth } from '@/lib/auth';

export default auth((req) => {
  if (!req.auth && req.nextUrl.pathname.startsWith('/dashboard')) {
    return Response.redirect(new URL('/login', req.url));
  }
});
```

### 10. Database & ORM

- Use **Drizzle ORM** (preferred) or **Prisma** for type-safe database access.
- Define schemas in `packages/shared/src/db/schema.ts` for monorepo-wide access.
- Use database migrations for all schema changes — never modify the database directly.
- Drizzle: `pnpm drizzle-kit generate` → `pnpm drizzle-kit migrate`
- Prisma: `pnpm prisma migrate dev --name <description>`
- Use transactions for multi-step write operations.
- Always select only needed columns — avoid `SELECT *` patterns.

### 11. Accessibility (a11y)

- All interactive elements MUST have accessible labels (`aria-label`, `aria-labelledby`, or visible text).
- Use semantic HTML elements: `<button>` not `<div onClick>`, `<nav>` not `<div class="nav">`.
- Ensure keyboard navigation works: all interactive elements must be focusable and operable via keyboard.
- Use Shadcn UI components which have built-in accessibility support.
- Color contrast MUST meet WCAG 2.1 AA standards (4.5:1 for normal text, 3:1 for large text).
- Include `alt` text on all `<img>` elements — use empty `alt=""` for decorative images only.
- Test with screen readers and keyboard-only navigation before completing UI tasks.

## Anti-Patterns to Avoid

| Anti-Pattern | Do This Instead |
|---|---|
| `any` type | `unknown` + type narrowing, or generics |
| `as UserData` type assertion | `userSchema.parse(data)` (Zod) |
| `enum Status { ... }` | `type Status = 'active' \| 'inactive'` |
| `useEffect` for data fetching | React Query or Server Components |
| `npm install` / `yarn add` | `pnpm add --filter <workspace>` |
| Default exports | Named exports |
| `class MyComponent extends React.Component` | Functional components |
| Hardcoded colors (`#ff0000`) | Tailwind classes / CSS variables |
| Building UI from scratch | Shadcn components |
| `// @ts-ignore` | Fix the underlying type error |
| `localStorage` for auth tokens | Server-side sessions (NextAuth/Auth.js) |
| `<div onClick>` for buttons | Semantic `<button>` elements |
| `SELECT *` queries | Select specific columns only |
| Missing `alt` on images | Always provide descriptive `alt` text |

## Quality Gates

Before declaring ANY task complete, you MUST autonomously run:
1. `pnpm tsc --noEmit` (type checking — zero errors)
2. `pnpm biome check --apply <modified files>` (lint + format)
3. `pnpm vitest run <relevant test files>` (tests pass)

Fix all errors before finalizing. Do not ask the user to fix type errors.

## Dev Environment Bootstrap

On first setup or when `.vscode/settings.json` is missing, you MUST check and generate proper editor configuration:

1. **Check** if `.vscode/settings.json` exists. If missing or outdated, create it with:
   - Biome (`biomejs.biome`) as the default formatter for `[typescript]`, `[typescriptreact]`, `[javascript]`, `[javascriptreact]`, `[json]`, `[jsonc]`, `[css]`
   - Format on save enabled for all above languages
   - Code actions on save: `source.fixAll.biome` + `source.organizeImports.biome`
   - ESLint and Prettier explicitly **disabled** (`eslint.enable: false`, `prettier.enable: false`)
   - Tailwind CSS class regex for `cn()`, `cva()`, `clsx()` helpers
   - `typescript.tsdk` pointing to `node_modules/typescript/lib`
   - `typescript.preferences.importModuleSpecifier` set to `"non-relative"`
   - `typescript.preferences.preferTypeOnlyAutoImports` enabled
   - `npm.packageManager` set to `"pnpm"`
   - Vitest integration enabled
   - Emmet for JSX (`typescriptreact: html`)
   - Tab size 2, linked editing, bracket pair colorization
   - File exclusions for `node_modules`, `.next`, `.turbo`, `dist`, `coverage`

2. **Check** if `.vscode/extensions.json` exists. If missing, create it recommending:
   - `biomejs.biome`, `bradlc.vscode-tailwindcss`, `vitest.explorer`
   - `ms-playwright.playwright`, `yoavbls.pretty-ts-errors`
   - `formulahendry.auto-rename-tag`, `usernamehw.errorlens`, `eamodio.gitlens`

Run the `ts-project-setup` skill for the full bootstrap procedure.

## Code Quality Skills

The following on-demand skills are available for code quality workflows. Invoke them by name or trigger phrase:

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `ts-code-audit` | "audit code", "code health" | Full audit: type safety (`any`/`as`/`ts-ignore` count), knip dead code, pnpm audit, Biome diagnostics, React-specific checks (missing keys, useEffect, DOM access). |
| `ts-simplify` | "simplify", "clean up code" | Simplify code: remove `any` → proper types, assertions → Zod, enums → unions, flatten conditionals, extract hooks, simplify rendering, optional chaining. |
| `ts-bug-scan` | "find bugs", "security scan" | Scan for bugs: type holes, React bugs (missing keys, stale closures, useEffect deps), async bugs (missing await, unhandled rejections), security (secrets, XSS, eval), Next.js-specific. |
| `ts-project-setup` | "setup project", "bootstrap" | Generate `.vscode/settings.json` and `extensions.json` with Biome, Tailwind, Vitest, pnpm config. |

## Lifecycle Hooks

Hooks are defined in `.claude/hooks/hooks.json` and run automatically:

- **PreToolUse (Read files):** Blocks reading sensitive files (`.env`, `.env.local`, `config.json`, `secrets.*`, `credentials.*`, `*.pem`, `*.key`, `firebase-adminsdk*.json`, etc.). Files with `.example`, `.sample`, or `.template` suffixes are explicitly allowed. The hook script is at `.claude/hooks/block-sensitive-reads.sh`.
- **PostToolUse (Write `.ts`/`.tsx` files):** Auto-runs `biome check --apply` on every saved TypeScript file.
- **PreCommit:** Runs `tsc --noEmit` → `vitest run --reporter=verbose` before every commit. Commit is blocked if type checking or tests fail.

These hooks enforce quality gates and security boundaries without manual intervention.

## Progressive Disclosure

For domain-specific context, read these files only when the task requires it:
- API routes and schemas → `docs/api-reference.md`
- Design system tokens → `packages/ui/src/styles/tokens.ts`
- Database schema → `packages/shared/src/db/schema.ts` (Drizzle/Prisma)
- Environment configuration → `.env.example`
- Deployment → `docs/deployment.md`
