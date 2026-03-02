# CLAUDE_USER.md — C# / .NET Project

> This file is the single source of truth for Claude Code when operating in this repository.
> Strictly follow every rule below. When in doubt, re-read this file before generating code.

## System Identity

You are an expert .NET/C# enterprise architect agent. This project uses .NET 8+ with highly decoupled, cloud-native architectural patterns. You must prioritize runtime performance, memory allocation efficiency, and strict adherence to SOLID principles.

## Project Scope

**At the start of every new session or project**, ask the user:

> **Is this project for personal/prototype use, or should it be production-ready?**

The user's answer determines which rule tier applies. Default to **Production** if the user does not respond or is unsure.

### Personal / Prototype Mode

When the user confirms this is a personal project, hackathon, prototype, or learning exercise:

- **Architecture:** Clean Architecture and CQRS are optional. A single-project structure with controllers or Minimal APIs is acceptable.
- **Type safety:** Nullable Reference Types are recommended but warnings can be suppressed. `var` everywhere is fine.
- **Testing:** Optional. Write tests only if the user asks. No minimum coverage requirement.
- **MediatR:** Optional. Business logic can live directly in endpoint handlers for simplicity.
- **Validation:** Data Annotations (`[Required]`, `[MaxLength]`) are acceptable. FluentValidation is not required.
- **Error handling:** Throwing exceptions for control flow is acceptable. `Result<T>` pattern is optional.
- **Logging:** `Console.WriteLine()` is acceptable for debugging. Structured logging is not required.
- **Configuration:** `IConfiguration` direct injection is acceptable. Options pattern is not required.
- **Docker:** Optional. Running directly with `dotnet run` is acceptable.
- **Health checks:** Optional.
- **API versioning:** Optional.
- **Quality gates:** Run `dotnet build` only. Skip `dotnet format`, architecture boundary checks, and full test suites.
- **Documentation:** Minimal. Inline comments only when non-obvious.

### Production Mode (Default)

When the user confirms this is production-bound, or does not specify:

- **ALL rules in this file apply without exception.**
- Clean Architecture with strict layer boundaries. CQRS via MediatR.
- Nullable Reference Types enforced. Zero compiler warnings.
- FluentValidation for all commands/queries. No Data Annotations.
- `Result<T>` pattern for expected failures. No exceptions for control flow.
- Structured logging with `ILogger<T>`. Options pattern for configuration.
- Health check endpoints for all external dependencies.
- Docker multi-stage builds. API versioning.
- Comprehensive tests with xUnit + FluentAssertions.
- All quality gates must pass before completing any task.
- Pre-commit hooks enforced.

---

## Technology Stack

| Layer            | Tool / Version                           |
|------------------|------------------------------------------|
| Framework        | .NET 8+ (LTS)                            |
| Language         | C# 12+                                  |
| Architecture     | Clean Architecture + CQRS               |
| Data Access      | Entity Framework Core 8 (PostgreSQL)     |
| Mediation        | MediatR                                 |
| Validation       | FluentValidation                        |
| Error Handling   | OneOf / Result\<T\> pattern              |
| API Style        | Minimal APIs (Program.cs)               |
| Testing          | xUnit + Moq + FluentAssertions          |
| Containers       | Docker + docker-compose                 |
| CI/CD            | GitHub Actions / Azure Pipelines        |

## Directory Topology

```
├── src/
│   ├── Api/                         # Minimal API endpoints, middleware, DI config
│   │   ├── Program.cs               # Application entrypoint + DI registration
│   │   ├── Endpoints/               # Minimal API endpoint groups
│   │   ├── Middleware/              # Custom middleware (auth, error handling, logging)
│   │   └── Filters/                # Endpoint filters
│   ├── Application/                 # Business logic layer
│   │   ├── Commands/               # MediatR commands (write operations)
│   │   ├── Queries/                # MediatR queries (read operations)
│   │   ├── DTOs/                   # Data Transfer Objects (record types)
│   │   ├── Interfaces/             # Abstractions / contracts
│   │   ├── Behaviors/              # MediatR pipeline behaviors (validation, logging)
│   │   └── Mappings/              # Explicit mapping extension methods
│   ├── Domain/                     # Core entities — ZERO external dependencies
│   │   ├── Entities/              # Domain entities
│   │   ├── ValueObjects/          # Immutable value objects
│   │   ├── Enums/                 # Domain enumerations
│   │   ├── Events/                # Domain events
│   │   └── Exceptions/           # Domain-specific exceptions
│   └── Infrastructure/            # External concerns
│       ├── Data/                  # EF Core DbContext, configurations, migrations
│       ├── Repositories/         # Repository implementations
│       ├── Services/             # External API clients
│       └── DependencyInjection.cs # Infrastructure DI registration
├── tests/
│   ├── UnitTests/                # Unit tests (Domain + Application)
│   ├── IntegrationTests/         # Integration tests (API + Infrastructure)
│   └── ArchitectureTests/       # Architecture rule enforcement tests
├── Directory.Build.props          # Shared MSBuild properties
└── <SolutionName>.sln
```

## Operational Commands

Always prefer project-scoped commands over solution-wide builds.

```bash
# Build specific project
dotnet build src/Api/Api.csproj

# Build entire solution
dotnet build

# Run tests in a specific project
dotnet test tests/UnitTests/UnitTests.csproj --verbosity normal

# Run all tests
dotnet test --verbosity normal

# Add NuGet package
dotnet add src/Application/Application.csproj package <PackageName>

# EF Core Migrations
dotnet ef migrations add <MigrationName> -p src/Infrastructure -s src/Api
dotnet ef database update -p src/Infrastructure -s src/Api

# Format code (deterministic — do NOT format manually)
dotnet format src/Api/Api.csproj
dotnet format  # whole solution

# Run the API
dotnet run --project src/Api
```

## Architectural Rules

### 1. CQRS & MediatR (Non-Negotiable)

- **ALL business logic** lives in MediatR Handlers in the Application layer.
- Strictly separate Read models (Queries) from Write models (Commands).
- Naming: `Create[Entity]Command`, `Get[Entity]ByIdQuery`, `[Entity]Response`
- Use pipeline behaviors for cross-cutting concerns (validation, logging, caching).

```csharp
// Command (record for immutability)
public record CreateOrderCommand(
    string CustomerId,
    List<OrderItemDto> Items
) : IRequest<Result<OrderResponse>>;

// Handler
public class CreateOrderHandler(
    AppDbContext db,
    ILogger<CreateOrderHandler> logger
) : IRequestHandler<CreateOrderCommand, Result<OrderResponse>>
{
    public async Task<Result<OrderResponse>> Handle(
        CreateOrderCommand request,
        CancellationToken cancellationToken)
    {
        // Business logic here
    }
}
```

### 2. Data Access Anti-Patterns (CRITICAL)

- **DO NOT** create custom Generic Repository wrappers around EF Core. Use `DbContext` and `DbSet<T>` directly.
- **DO NOT** use AutoMapper. Use explicit mapping methods or extension methods.
- **DO NOT** inject `DbContext` into API controllers/endpoints — inject it only in Infrastructure/Application handlers.

```csharp
// FORBIDDEN — Custom Generic Repository
public interface IRepository<T> { Task<T> GetByIdAsync(int id); }

// CORRECT — Use DbContext directly
public class GetOrderHandler(AppDbContext db) : IRequestHandler<GetOrderQuery, OrderResponse>
{
    public async Task<OrderResponse> Handle(GetOrderQuery query, CancellationToken ct)
    {
        var order = await db.Orders
            .AsNoTracking()
            .FirstOrDefaultAsync(o => o.Id == query.Id, ct);
        return order.ToResponse(); // Explicit mapping extension
    }
}
```

### 3. C# Language Features (Modern C# 12+)

- **Nullable Reference Types:** `<Nullable>enable</Nullable>` is mandatory.
- **Primary Constructors** for dependency injection in classes.
- **Record types** for all DTOs, Commands, Queries, and Value Objects.
- **Expression-bodied members** (`=>`) for simple properties and single-expression methods.
- **File-scoped namespaces** (`namespace App.Domain.Entities;`) — not block-scoped.
- **Raw string literals** (`"""..."""`) for multiline strings and SQL.
- **Pattern matching** (`is`, `switch` expressions) over `if-else` chains.
- **Collection expressions** (`[1, 2, 3]`) where applicable.

```csharp
// Modern C# patterns
namespace App.Application.Commands;

public record CreateUserCommand(string Name, string Email) : IRequest<Result<UserResponse>>;

public record UserResponse(Guid Id, string Name, string Email, DateTime CreatedAt);

public class CreateUserHandler(
    AppDbContext db,
    IValidator<CreateUserCommand> validator,
    ILogger<CreateUserHandler> logger
) : IRequestHandler<CreateUserCommand, Result<UserResponse>>
{
    public async Task<Result<UserResponse>> Handle(
        CreateUserCommand request,
        CancellationToken cancellationToken)
    {
        var validation = await validator.ValidateAsync(request, cancellationToken);
        if (!validation.IsValid)
            return Result<UserResponse>.Failure(validation.Errors);

        var user = new User(request.Name, request.Email);
        db.Users.Add(user);
        await db.SaveChangesAsync(cancellationToken);

        logger.LogInformation("Created user {UserId}", user.Id);
        return Result<UserResponse>.Success(user.ToResponse());
    }
}
```

### 4. Asynchronous & Performance Standards

- Every async method MUST accept `CancellationToken` and pass it down the entire chain.
- **NEVER** use `.Result` or `.Wait()` — async all the way down.
- Use `IAsyncEnumerable<T>` for streaming large datasets.
- Use `AsNoTracking()` for read-only queries.
- Use `ValueTask<T>` for hot-path methods that may complete synchronously.
- Use `Span<T>` and `Memory<T>` for performance-critical buffer operations.

```csharp
// FORBIDDEN
var result = GetDataAsync().Result;  // Thread starvation!

// CORRECT
var result = await GetDataAsync(cancellationToken);
```

### 5. Error Handling (Result Pattern)

- **DO NOT** throw exceptions for expected business logic flow.
- Use `Result<T>` or `OneOf<Success, Error>` pattern for deterministic success/failure.
- Domain exceptions are for truly exceptional/unexpected scenarios only.
- Global exception middleware catches unhandled exceptions at the API boundary.

```csharp
// Result pattern
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }

    public static Result<T> Success(T value) => new() { IsSuccess = true, Value = value };
    public static Result<T> Failure(string error) => new() { IsSuccess = false, Error = error };
}
```

### 6. Validation (FluentValidation)

- Every Command/Query that accepts user input MUST have a FluentValidation validator.
- Validators run automatically via MediatR pipeline behavior.
- Never use Data Annotations (`[Required]`, `[MaxLength]`) — use FluentValidation exclusively.

```csharp
public class CreateUserValidator : AbstractValidator<CreateUserCommand>
{
    public CreateUserValidator()
    {
        RuleFor(x => x.Name).NotEmpty().MaximumLength(255);
        RuleFor(x => x.Email).NotEmpty().EmailAddress();
    }
}
```

### 7. Testing

- Test projects mirror source structure.
- Use xUnit + FluentAssertions for assertions.
- Use Moq for mocking dependencies.
- Integration tests use `WebApplicationFactory<Program>` with test database.
- Architecture tests enforce layer boundaries (Domain has zero external deps).

```csharp
public class CreateUserHandlerTests
{
    [Fact]
    public async Task Handle_ValidCommand_ReturnsSuccess()
    {
        // Arrange
        var db = CreateInMemoryDb();
        var handler = new CreateUserHandler(db, validator, logger);
        var command = new CreateUserCommand("John", "john@example.com");

        // Act
        var result = await handler.Handle(command, CancellationToken.None);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.Value!.Name.Should().Be("John");
    }
}
```

### 8. Logging

- Use the built-in `ILogger<T>` via dependency injection — never instantiate loggers manually.
- Use **structured logging** with message templates: `logger.LogInformation("Order {OrderId} created for {CustomerId}", orderId, customerId)`.
- NEVER use string interpolation in log messages (`$"Order {orderId}"`) — it defeats structured logging.
- Use appropriate log levels: `Trace` for verbose diagnostics, `Debug` for development, `Information` for operational events, `Warning` for recoverable issues, `Error` for failures, `Critical` for system-level failures.
- Configure logging in `Program.cs` via `builder.Logging` — add `Console`, `Debug`, and production sinks (Application Insights, Seq, etc.).
- Use **Serilog** for advanced scenarios (JSON output, enrichment, sinks). Configure via `UseSerilog()` in `Program.cs`.
- Add correlation IDs to all log entries for request tracing across services.

```csharp
// CORRECT — Structured logging with message templates
logger.LogInformation("Order {OrderId} created for customer {CustomerId}", order.Id, command.CustomerId);

// FORBIDDEN — String interpolation (breaks structured logging)
logger.LogInformation($"Order {order.Id} created for customer {command.CustomerId}");
```

### 9. Configuration Management

- Use the **Options pattern** (`IOptions<T>`, `IOptionsSnapshot<T>`, `IOptionsMonitor<T>`) for all configuration.
- Define strongly-typed configuration classes as POCOs with validation.
- Bind configuration sections in `Program.cs`: `builder.Services.Configure<DatabaseOptions>(builder.Configuration.GetSection("Database"))`.
- NEVER inject `IConfiguration` directly into services — use `IOptions<T>` for type-safe access.
- Validate configuration at startup using `ValidateDataAnnotations()` or `Validate()` with a custom delegate.
- Use `appsettings.json` for defaults, `appsettings.{Environment}.json` for overrides, and environment variables for secrets.
- Never commit secrets to `appsettings.json` — use Azure Key Vault, User Secrets, or environment variables.

```csharp
// Configuration POCO
public class DatabaseOptions
{
    public const string SectionName = "Database";
    public required string ConnectionString { get; init; }
    public int MaxRetryCount { get; init; } = 3;
    public int CommandTimeout { get; init; } = 30;
}

// Registration in Program.cs
builder.Services.AddOptions<DatabaseOptions>()
    .BindConfiguration(DatabaseOptions.SectionName)
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

### 10. Health Checks

- Register health checks in `Program.cs` for all external dependencies (database, cache, message queues, external APIs).
- Use `Microsoft.Extensions.Diagnostics.HealthChecks` and community packages (`AspNetCore.HealthChecks.*`).
- Map health check endpoints: `app.MapHealthChecks("/health")` for liveness, `app.MapHealthChecks("/ready")` for readiness.
- Liveness checks verify the app is running. Readiness checks verify all dependencies are available.
- Return detailed health check results in non-production environments for debugging.

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "database")
    .AddRedis(redisConnectionString, name: "cache");

app.MapHealthChecks("/health/live", new HealthCheckOptions { Predicate = _ => false });
app.MapHealthChecks("/health/ready");
```

### 11. Docker & Containerization

- Use multi-stage builds to minimize image size: `sdk` stage for build, `aspnet` stage for runtime.
- Expose only the necessary port (default 8080 for .NET 8+).
- Use `.dockerignore` to exclude `bin/`, `obj/`, `.vs/`, `TestResults/`, and `*.sln` from the build context.
- Run as non-root user in production: `USER app` (default in .NET 8+ images).
- Use `docker-compose.yml` for local development with database and cache dependencies.
- Set `DOTNET_EnableDiagnostics=0` in production containers for security.

```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/Api/Api.csproj", "Api/"]
COPY ["src/Application/Application.csproj", "Application/"]
COPY ["src/Domain/Domain.csproj", "Domain/"]
COPY ["src/Infrastructure/Infrastructure.csproj", "Infrastructure/"]
RUN dotnet restore "Api/Api.csproj"
COPY src/ .
RUN dotnet publish "Api/Api.csproj" -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENTRYPOINT ["dotnet", "Api.dll"]
```

### 12. API Versioning

- Use **Asp.Versioning** (`Asp.Versioning.Http`) for API version management.
- Version via URL path (`/api/v1/`, `/api/v2/`) — preferred for clarity.
- Group endpoints by version in separate static classes or files.
- Deprecate old versions with `[ApiVersion("1.0", Deprecated = true)]` attributes.
- Document version lifecycle in API specification.

```csharp
// Program.cs
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;
});

// Versioned endpoint group
var v1 = app.NewVersionedApi().MapGroup("/api/v1");
v1.MapGet("/users", GetUsersV1).HasApiVersion(1.0);

var v2 = app.NewVersionedApi().MapGroup("/api/v2");
v2.MapGet("/users", GetUsersV2).HasApiVersion(2.0);
```

## Anti-Patterns to Avoid

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
| `$"Order {id}"` in log messages | Structured templates: `"Order {OrderId}"` with parameters |
| Injecting `IConfiguration` directly | `IOptions<T>` / Options pattern |
| No health check endpoints | `MapHealthChecks("/health")` with dependency checks |
| Single-stage Dockerfile | Multi-stage build: `sdk` → `aspnet` |
| No API versioning | `Asp.Versioning` with URL path versioning |

## Quality Gates

Before declaring ANY task complete, you MUST autonomously:
1. `dotnet build` — zero compiler warnings
2. `dotnet format <modified project>` — enforce code style
3. `dotnet test <relevant test project>` — all tests pass
4. Verify Domain project has ZERO references to `Microsoft.EntityFrameworkCore` or UI namespaces

Fix all issues before finalizing. Do not ask the user to fix compilation errors.

## Dev Environment Bootstrap

On first setup or when `.vscode/settings.json` or `.editorconfig` is missing, you MUST check and generate proper editor configuration:

1. **Check** if `.vscode/settings.json` exists. If missing or outdated, create it with:
   - C# (`ms-dotnettools.csharp`) as the default formatter for `[csharp]`
   - Format on save AND format on type enabled
   - Code actions on save: `source.fixAll` + `source.organizeImports`
   - Roslyn analyzers enabled (`omnisharp.enableRoslynAnalyzers`)
   - EditorConfig support enabled (`omnisharp.enableEditorConfigSupport`)
   - Organize imports on format enabled
   - Inlay hints for parameters enabled
   - Tab size 4, rulers at 120
   - Terminal env: `DOTNET_CLI_TELEMETRY_OPTOUT=1`, `DOTNET_NOLOGO=1`
   - File exclusions for `bin`, `obj`, `.vs`, `TestResults`
   - Search exclusions for `Migrations/*.Designer.cs`

2. **Check** if `.vscode/extensions.json` exists. If missing, create it recommending:
   - `ms-dotnettools.csharp`, `ms-dotnettools.csdevkit`
   - `ms-dotnettools.vscode-dotnet-runtime`, `ms-dotnettools.vscodeintellicode-csharp`
   - `formulahendry.dotnet-test-explorer`, `patcx.vscode-nuget-gallery`
   - `humao.rest-client`, `redhat.vscode-xml`
   - `EditorConfig.EditorConfig`, `usernamehw.errorlens`, `eamodio.gitlens`

3. **Check** if `.editorconfig` exists. If missing, create it with:
   - File-scoped namespaces enforced (`csharp_style_namespace_declarations = file_scoped:warning`)
   - Primary constructors preferred
   - Expression-bodied members for simple properties/methods
   - Pattern matching over `is`/`as` with cast/null checks
   - Null coalescing and propagation preferred
   - `var` preferred when type is apparent
   - Naming: PascalCase for public, `_camelCase` for private fields, `I` prefix for interfaces, `T` prefix for type params
   - Sort system directives first
   - Nullable reference type diagnostics (CS8600-CS8625) set to warning
   - IDE0005 (unnecessary usings), IDE0161 (file-scoped namespace) set to warning
   - Indent sizes: 4 for C#, 2 for XML/JSON/YAML

Run the `dotnet-project-setup` skill for the full bootstrap procedure.

## Code Quality Skills

The following on-demand skills are available for code quality workflows. Invoke them by name or trigger phrase:

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `dotnet-code-audit` | "audit code", "code health" | Full audit: Roslyn analyzer warnings, nullable coverage, architecture boundary enforcement, async anti-patterns, `dotnet format` check, NuGet dependency health. |
| `dotnet-simplify` | "simplify", "clean up code" | Simplify code: block → file-scoped namespaces, constructor → primary constructors, class → records, `new List<T>()` → collection expressions, if/else → switch expressions, guard clauses. |
| `dotnet-bug-scan` | "find bugs", "security scan" | Scan for bugs: nullable violations, sync-over-async (`.Result`/`.Wait()`), async void, exception handling bugs, EF N+1 queries, SQL injection, NuGet vulnerabilities, hardcoded secrets, DI bugs. |
| `dotnet-project-setup` | "setup project", "bootstrap" | Generate `.vscode/settings.json`, `extensions.json`, and `.editorconfig` with Roslyn, C# conventions, naming rules, nullable diagnostics. |

## Lifecycle Hooks

Hooks are defined in `.claude/hooks/hooks.json` and run automatically:

- **PreToolUse (Read files):** Blocks reading sensitive files (`.env`, `appsettings.json`, `appsettings.*.json`, `secrets.*`, `config.json`, `credentials.*`, `*.pem`, `*.pfx`, `*.key`, `local.settings.json`, etc.). Files with `.example`, `.sample`, or `.template` suffixes are explicitly allowed. The hook script is at `.claude/hooks/block-sensitive-reads.sh`.
- **PostToolUse (Write `.cs` files):** Auto-runs `dotnet format` on the modified project after every saved C# file.
- **PreCommit:** Runs `dotnet build --no-restore` → `dotnet test --no-build --verbosity normal` before every commit. Commit is blocked if build or tests fail.

These hooks enforce quality gates and security boundaries without manual intervention.

## Progressive Disclosure

For domain-specific context, read these files only when the task requires it:
- Database schema → `docs/database-schema.md`
- API specification → `docs/api-spec.md`
- Architecture decision records → `docs/adr/`
- Deployment guide → `docs/deployment.md`
- Environment configuration → `appsettings.Development.json`
