---
name: ts-react-component
description: Create new React components following project conventions with proper types, styling, and tests.
triggers:
  - "create component"
  - "new component"
  - "add component"
  - "build component"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# TypeScript React Component Creator Skill

## When Triggered

Create a new React component following the project's conventions.

## Steps

1. **Determine component location**:
   - Shared UI → `packages/ui/src/components/`
   - App-specific → `apps/web/components/`
   - Page-specific → Co-locate with the page

2. **Check if a Shadcn component exists first**:
   - Browse `packages/ui/src/components/ui/` for existing primitives
   - If needed, install via: `pnpm dlx shadcn@latest add <component>`

3. **Create the component file** with proper types:
   ```typescript
   'use client'; // ONLY if client interactivity is needed

   import { cn } from '@/lib/utils';

   interface UserCardProps {
     user: User;
     className?: string;
     onSelect?: (id: string) => void;
   }

   export function UserCard({ user, className, onSelect }: UserCardProps) {
     return (
       <div className={cn('rounded-lg border p-4', className)}>
         <h3 className="text-lg font-semibold">{user.name}</h3>
         {onSelect && (
           <button
             onClick={() => onSelect(user.id)}
             className="mt-2 text-sm text-primary hover:underline"
           >
             Select
           </button>
         )}
       </div>
     );
   }
   ```

4. **Create the test file** (co-located):
   ```typescript
   import { render, screen } from '@testing-library/react';
   import userEvent from '@testing-library/user-event';
   import { describe, expect, it, vi } from 'vitest';
   import { UserCard } from './UserCard';

   describe('UserCard', () => {
     it('renders user name', () => {
       render(<UserCard user={mockUser} />);
       expect(screen.getByText('John Doe')).toBeInTheDocument();
     });

     it('calls onSelect when button is clicked', async () => {
       const onSelect = vi.fn();
       render(<UserCard user={mockUser} onSelect={onSelect} />);
       await userEvent.click(screen.getByText('Select'));
       expect(onSelect).toHaveBeenCalledWith('123');
     });
   });
   ```

5. **Extract complex logic** into a custom hook if needed:
   ```typescript
   // hooks/useUserCard.ts
   export function useUserCard(userId: string) {
     // Complex state/effect logic here
   }
   ```

6. **Run quality gates**:
   ```bash
   pnpm tsc --noEmit
   pnpm biome check --apply <new files>
   pnpm vitest run <test file>
   ```

## Key Conventions

- Functional components only — no class components
- Named exports (not default exports)
- Props interface named `[Component]Props`
- Use `cn()` utility for conditional classNames
- Use Tailwind classes, CSS variables — no hardcoded colors
- `'use client'` directive ONLY when needed (interactivity, hooks, browser APIs)
- Extract logic into `use[Feature].ts` hooks
- Co-locate tests: `Component.tsx` → `Component.test.tsx`
