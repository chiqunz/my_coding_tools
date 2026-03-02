---
description: Enforce error handling and validation patterns
globs: "**/*.cs"
---

# Error Handling & Validation Rules

1. **Never throw exceptions** for expected business logic failures — use `Result<T>` or `OneOf` pattern
2. **FluentValidation** for all Command/Query validation — no Data Annotations
3. Validators run via MediatR **pipeline behavior** — automatic, not manual
4. **Global exception middleware** at API boundary for truly unexpected errors
5. Domain exceptions only for invariant violations that indicate a programming error
6. Always log errors with structured logging: `logger.LogError(ex, "Failed to {Action} {EntityId}", action, id)`
