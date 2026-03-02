---
name: ts-simplify
description: Simplify TypeScript/React code — reduce complexity, eliminate type hacks, modernize patterns, and improve readability.
triggers:
  - "simplify"
  - "simplify code"
  - "reduce complexity"
  - "make simpler"
  - "clean up code"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# TypeScript Code Simplification Skill

## When Triggered

Simplify TypeScript/React code while preserving exact behavior.

## Simplification Patterns (ordered by impact)

### A. Remove `any` → Proper Types

```typescript
// BEFORE
const data: any = await fetch(url).then(r => r.json());

// AFTER
const data = userSchema.parse(await fetch(url).then(r => r.json()));
```

### B. Remove Type Assertions on External Data → Zod

```typescript
// BEFORE
const user = response.data as User;

// AFTER
const user = userSchema.parse(response.data);
```

### C. Replace Enums → String Unions

```typescript
// BEFORE
enum Status { Active = "active", Inactive = "inactive" }

// AFTER
type Status = "active" | "inactive";
const STATUS = { Active: "active", Inactive: "inactive" } as const;
```

### D. Flatten Nested Conditionals → Early Returns

Same principle as Python: guard clauses at the top, happy path at the bottom.

### E. Extract Complex Components → Custom Hooks

```typescript
// BEFORE — component with embedded logic
function UserProfile({ userId }: Props) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { /* fetch logic */ }, [userId]);
  if (loading) return <Spinner />;
  // ... 50 lines of JSX
}

// AFTER — logic extracted to hook
function useUser(userId: string) {
  return useQuery({ queryKey: ["user", userId], queryFn: () => getUser(userId) });
}

function UserProfile({ userId }: Props) {
  const { data: user, isLoading } = useUser(userId);
  if (isLoading) return <Spinner />;
  // ... clean JSX only
}
```

### F. Simplify Conditional Rendering

```typescript
// BEFORE
{condition ? <Component /> : null}

// AFTER
{condition && <Component />}

// BEFORE (ternary soup)
{isLoading ? <Spinner /> : error ? <Error msg={error} /> : data ? <List items={data} /> : null}

// AFTER (early returns in component)
if (isLoading) return <Spinner />;
if (error) return <Error msg={error} />;
if (!data) return null;
return <List items={data} />;
```

### G. Use Optional Chaining & Nullish Coalescing

```typescript
// BEFORE
const name = user && user.profile && user.profile.name ? user.profile.name : "Anonymous";

// AFTER
const name = user?.profile?.name ?? "Anonymous";
```

### H. Auto-Fix with Biome

```bash
# Apply all safe fixes
pnpm biome check --apply <filepath>
```

## Steps

1. Measure: identify complexity hotspots
2. Apply patterns above, one at a time
3. Run tests after each change: `pnpm vitest run <test>`
4. Run type check: `pnpm tsc --noEmit`
5. Run format: `pnpm biome check --apply <filepath>`
