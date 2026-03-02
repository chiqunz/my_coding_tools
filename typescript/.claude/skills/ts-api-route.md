---
name: ts-api-route
description: Create new Next.js API routes or tRPC procedures with Zod validation and proper error handling.
triggers:
  - "create endpoint"
  - "add API route"
  - "new route handler"
  - "add API"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# TypeScript API Route Creator Skill

## When Triggered

Create a new API endpoint using Next.js Route Handlers or tRPC procedures.

## Steps — Next.js Route Handler

1. **Create the route file** in `apps/web/app/api/`:
   ```typescript
   // app/api/users/route.ts
   import { NextRequest, NextResponse } from 'next/server';
   import { z } from 'zod';

   const createUserSchema = z.object({
     name: z.string().min(1).max(255),
     email: z.string().email(),
   });

   export async function POST(request: NextRequest) {
     const body = await request.json();
     const result = createUserSchema.safeParse(body);

     if (!result.success) {
       return NextResponse.json(
         { error: result.error.flatten() },
         { status: 422 }
       );
     }

     const user = await userService.create(result.data);
     return NextResponse.json(user, { status: 201 });
   }

   export async function GET(request: NextRequest) {
     const { searchParams } = new URL(request.url);
     const page = Number(searchParams.get('page') ?? '1');

     const users = await userService.list({ page });
     return NextResponse.json(users);
   }
   ```

2. **Create dynamic routes** for parameterized endpoints:
   ```typescript
   // app/api/users/[id]/route.ts
   interface RouteParams {
     params: Promise<{ id: string }>;
   }

   export async function GET(_request: NextRequest, { params }: RouteParams) {
     const { id } = await params;
     const user = await userService.getById(id);

     if (!user) {
       return NextResponse.json({ error: 'Not found' }, { status: 404 });
     }

     return NextResponse.json(user);
   }
   ```

## Steps — tRPC Procedure

1. **Create the router** in the appropriate module:
   ```typescript
   import { z } from 'zod';
   import { createTRPCRouter, protectedProcedure, publicProcedure } from '@/server/trpc';

   export const userRouter = createTRPCRouter({
     getById: publicProcedure
       .input(z.object({ id: z.string().uuid() }))
       .query(async ({ input, ctx }) => {
         return ctx.db.user.findUnique({ where: { id: input.id } });
       }),

     create: protectedProcedure
       .input(z.object({
         name: z.string().min(1),
         email: z.string().email(),
       }))
       .mutation(async ({ input, ctx }) => {
         return ctx.db.user.create({ data: input });
       }),
   });
   ```

2. **Register the router** in the root app router

3. **Create tests** for the endpoint/procedure

4. **Run quality gates**:
   ```bash
   pnpm tsc --noEmit
   pnpm biome check --apply <new files>
   pnpm vitest run <test files>
   ```

## Key Conventions

- ALL input validated with Zod schemas — never trust raw request data
- Use proper HTTP status codes: 201 (created), 204 (no content), 404, 422
- Business logic lives in service layer, NOT in route handlers
- Use NextResponse (not legacy res.json())
- Error responses follow consistent shape: `{ error: string | object }`
