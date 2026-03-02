# AGENTS_USER.md — C# / .NET Project

> Universal agent instructions for any AI coding agent operating in this repository.
> This file follows the [AGENTS.md standard](https://agents.md) for cross-agent compatibility.

## System Context

You are an expert .NET/C# enterprise architect agent. This project uses .NET 8+ with Clean Architecture, CQRS, and cloud-native patterns. You must prioritize runtime performance, memory efficiency, and SOLID principles. When Claude Code is used, defer to `CLAUDE_USER.md` for additional Anthropic-specific instructions.

## Project Scope

**At the start of every new session or project**, ask the user:

> **Is this project for personal/prototype use, or should it be production-ready?**

Default to **Production** if the user does not respond.

### Personal / Prototype Mode

- Clean Architecture and CQRS are optional. Single-project structure is acceptable.
- MediatR optional — business logic can live in endpoint handlers directly.
- Data Annotations (`[Required]`) acceptable. FluentValidation not required.
- Throwing exceptions for control flow is acceptable. `Result<T>` optional.
- `Console.WriteLine()` acceptable for debugging. Structured logging not required.
- Testing optional — write tests only if asked.
- Quality gates: run `dotnet build` only. Skip formatting and architecture checks.

### Production Mode (Default)

- ALL rules in this file apply without exception.
- Clean Architecture, CQRS, FluentValidation, Result pattern, structured logging, comprehensive tests.
- All quality gates must pass before completing any task.

---

## Technology Stack & Tooling

- **Framework:** .NET 8+ (LTS)
- **Language:** C# 12+ with Nullable Reference Types enabled
- **Architecture:** Clean Architecture + CQRS (MediatR)
- **Data Access:** Entity Framework Core 8 (PostgreSQL)
- **Validation:** FluentValidation (NOT Data Annotations)
- **Error Handling:** Result\<T\> / OneOf pattern (NOT thrown exceptions)
- **Testing:** xUnit + Moq + FluentAssertions
- **API Style:** Minimal APIs (Program.cs)

## Operational Commands

Prefer project-scoped commands over solution-wide execution.

| Action | Command |
|--------|---------|
| Build project | `dotnet build src/Api/Api.csproj` |
| Build solution | `dotnet build` |
| Run tests | `dotnet test tests/UnitTests/UnitTests.csproj` |
| Add package | `dotnet add src/<Project>/<Project>.csproj package <Name>` |
| Add migration | `dotnet ef migrations add <Name> -p src/Infrastructure -s src/Api` |
| Apply migration | `dotnet ef database update -p src/Infrastructure -s src/Api` |
| Format code | `dotnet format src/Api/Api.csproj` |
| Run API | `dotnet run --project src/Api` |

## Directory Topology

- `src/Api/` — Minimal API endpoints, middleware, DI config. NO business logic.
- `src/Application/` — MediatR Commands/Queries, DTOs, interfaces, behaviors.
- `src/Domain/` — Entities, value objects, domain events. ZERO external dependencies.
- `src/Infrastructure/` — EF Core DbContext, external API clients, repository implementations.
- `tests/UnitTests/` — Unit tests for Domain + Application layers.
- `tests/IntegrationTests/` — Integration tests for API + Infrastructure.

## Architectural Rules

1. **CQRS:** All business logic in MediatR Handlers (Application layer). Separate Commands from Queries.
2. **Data Access:** DO NOT create Generic Repositories over EF Core. DO NOT use AutoMapper. Use explicit mapping methods.
3. **C# Features:** Use Primary Constructors, record types, file-scoped namespaces, pattern matching, collection expressions.
4. **Async:** Every async method MUST accept and pass `CancellationToken`. Never use `.Result` or `.Wait()`.
5. **Error Handling:** Use `Result<T>` pattern for expected failures. Don't throw exceptions for control flow.
6. **Validation:** FluentValidation for all Commands/Queries. No Data Annotations.
7. **Testing:** xUnit + FluentAssertions. Integration tests use `WebApplicationFactory<Program>`.
8. **Style:** Do NOT manually format. Run `dotnet format` after writing code.

## Anti-Patterns

| Anti-Pattern | Do This Instead |
|---|---|
| `Startup.cs` class | Minimal API in `Program.cs` |
| Custom Generic Repository over EF Core | Use `DbContext` / `DbSet<T>` directly |
| AutoMapper | Explicit mapping extension methods |
| Data Annotations `[Required]` | FluentValidation |
| Throwing exceptions for control flow | `Result<T>` / `OneOf` pattern |
| `.Result` / `.Wait()` on tasks | `await` with `CancellationToken` |
| Block-scoped namespaces `{ }` | File-scoped: `namespace X;` |
| `var x = new List<string>()` | `List<string> x = [];` (collection expressions) |
| Legacy `Nullable<T>` | Enable Nullable Reference Types project-wide |
| `$"Order {id}"` in log messages | Structured templates: `"Order {OrderId}"` |
| Injecting `IConfiguration` directly | `IOptions<T>` / Options pattern |
| No health check endpoints | `MapHealthChecks("/health")` with dependency checks |
| Single-stage Dockerfile | Multi-stage build: `sdk` → `aspnet` |

## Quality Gates

Before completing any task:
1. `dotnet build` — zero warnings
2. `dotnet format` on modified projects
3. Run relevant tests — all pass
4. Verify Domain project has zero external framework references
5. Fix all errors autonomously
