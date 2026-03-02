---
description: Enforce Clean Architecture layer boundaries
globs: "**/*.cs"
---

# Clean Architecture Rules

1. **Domain Layer** (`src/Domain/`): ZERO external dependencies. No references to EF Core, MediatR, FluentValidation, or any infrastructure/UI namespace.
2. **Application Layer** (`src/Application/`): May reference Domain. May reference MediatR, FluentValidation. NEVER reference Infrastructure or API.
3. **Infrastructure Layer** (`src/Infrastructure/`): May reference Domain and Application. Contains EF Core, external API clients.
4. **API Layer** (`src/Api/`): May reference Application (via MediatR). NEVER contains business logic.

Dependency flow: API → Application → Domain ← Infrastructure
