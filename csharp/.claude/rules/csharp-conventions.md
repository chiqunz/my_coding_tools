---
description: Enforce modern C# language conventions
globs: "**/*.cs"
---

# C# Language Rules

1. **File-scoped namespaces:** `namespace App.Domain.Entities;` (not block-scoped `{ }`)
2. **Primary Constructors** for dependency injection
3. **Record types** for DTOs, Commands, Queries, and Value Objects
4. **Collection expressions:** `List<T> x = []` not `new List<T>()`
5. **Nullable Reference Types** enabled — no nullable warnings
6. **Pattern matching** and `switch` expressions over `if/else` chains
7. **Expression-bodied members** (`=>`) for simple methods/properties
8. **String interpolation** over concatenation
9. **`CancellationToken`** in ALL async method signatures — passed down the chain
10. **NEVER** use `.Result` or `.Wait()` on tasks — `await` all the way down
