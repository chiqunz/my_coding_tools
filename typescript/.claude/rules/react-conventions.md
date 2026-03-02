---
description: Enforce React component conventions
globs: "**/*.tsx"
---

# React Component Rules

1. **Functional components ONLY** — class components are forbidden
2. **Named exports** — no default exports (except Next.js page/layout files)
3. Props interface named `[Component]Props` — defined above the component
4. Use `'use client'` directive ONLY when needed (hooks, interactivity, browser APIs)
5. Extract complex logic into custom hooks: `use[Feature].ts`
6. Styling: Tailwind utility classes only, use `cn()` for conditional classes
7. Data fetching: React Query or Server Components — NEVER `useEffect`
8. Use Shadcn UI components from `@/components/ui/` — don't build primitives from scratch
