---
name: dotnet-bug-scan
description: Scan .NET code for potential bugs, security vulnerabilities, async pitfalls, and architecture violations.
triggers:
  - "scan for bugs"
  - "find bugs"
  - "security scan"
  - "check security"
  - "bug scan"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# .NET Bug Scanner Skill

## When Triggered

Scan the .NET codebase for potential bugs, security vulnerabilities, and common runtime pitfalls.

## Steps

### 1. Nullable Reference Type Violations (most common C# bug)

```bash
# Build with nullable warnings surfaced
dotnet build --verbosity normal 2>&1 | grep "CS86"

# CS8600 — Converting null literal or possible null to non-nullable
# CS8602 — Dereference of a possibly null reference
# CS8604 — Possible null reference argument
# CS8618 — Non-nullable property not initialized
```

For each finding: add proper null checks, use null-conditional (`?.`), or fix initialization.

### 2. Async Anti-Patterns (thread starvation / deadlocks)

```bash
# Sync-over-async — causes deadlocks and thread starvation
grep -rn "\.Result\b" src/ --include="*.cs"
grep -rn "\.Wait()" src/ --include="*.cs"
grep -rn "\.GetAwaiter().GetResult()" src/ --include="*.cs"

# Async void — fire and forget, lost exceptions
grep -rn "async void" src/ --include="*.cs" | grep -v "EventHandler"

# Missing CancellationToken — can't cancel long-running ops
grep -rn "async Task" src/ --include="*.cs" | grep -v "CancellationToken\|Test\|test" | head -15

# CS1998 — async method without await (useless overhead)
dotnet build --verbosity normal 2>&1 | grep "CS1998"
```

### 3. Exception Handling Bugs

```bash
# Catching and swallowing exceptions silently
grep -rn "catch" src/ --include="*.cs" -A 2 | grep -B1 "{ }" | head -10

# Catch Exception (too broad — hides real bugs)
grep -rn "catch (Exception\b" src/ --include="*.cs" | grep -v "// intentional\|GlobalException\|Middleware" | head -10

# Throw without preserving stack trace
grep -rn "throw ex;" src/ --include="*.cs"
# Should be: throw; (without ex)

# Missing exception logging
grep -rn "catch" src/ --include="*.cs" -A 3 | grep -v "Log\|log\|_logger" | grep "catch" | head -10
```

### 4. Entity Framework / Data Access Bugs

```bash
# N+1 query pattern (loading navigation properties in a loop)
grep -rn "foreach\|for (" src/ --include="*.cs" -A 5 | grep "await.*Find\|await.*First\|await.*Single" | head -10

# Missing AsNoTracking on read-only queries
grep -rn "await.*ToListAsync\|await.*FirstOrDefaultAsync\|await.*SingleOrDefaultAsync" src/ --include="*.cs" | grep -v "AsNoTracking\|Add\|Update\|Remove\|Save" | head -10

# String concatenation in queries (SQL injection risk)
grep -rn "FromSqlRaw\|FromSql\|ExecuteSqlRaw" src/ --include="*.cs" | grep "\$\"\|string.Format\|+ " | head -5

# Missing Include for navigation properties (lazy loading traps)
grep -rn "\.Select(.*\.\w*\.\w*)" src/ --include="*.cs" | grep -v "Include" | head -10
```

### 5. Security Scan

```bash
# NuGet vulnerability check
dotnet list package --vulnerable 2>&1

# Hardcoded secrets
grep -rni "password\|connectionstring\|secret\|apikey\|token" src/ --include="*.cs" | grep "=\s*\"" | grep -v "test\|Test\|mock\|Mock\|example" | head -10

# Hardcoded connection strings
grep -rn "Server=\|Data Source=\|Host=" src/ --include="*.cs" --include="*.json" | grep -v "appsettings\|test\|example" | head -5

# CORS wildcard
grep -rn "AllowAnyOrigin\|\"\\*\"" src/ --include="*.cs" | grep -i "cors" | head -5

# Missing authorization
grep -rn "MapGet\|MapPost\|MapPut\|MapDelete" src/ --include="*.cs" | grep -v "Authorize\|AllowAnonymous\|RequireAuthorization" | head -10
```

### 6. Dependency Injection Bugs

```bash
# Scoped service injected into singleton (captive dependency)
grep -rn "AddSingleton" src/ --include="*.cs" -A 1 | grep -i "dbcontext\|scoped\|HttpClient" | head -5

# Missing service registration (will throw at runtime)
grep -rn "Depends\|ISender\|IMediator\|IValidator" src/ --include="*.cs" | grep -v "Add\|Register\|builder\|services" | head -10

# Disposable not disposed
grep -rn "new HttpClient\|new SqlConnection\|new StreamReader" src/ --include="*.cs" | grep -v "using\|await using\|IDisposable" | head -5
```

### 7. Generate Report

Structured by severity:
- **Critical**: SQL injection, sync-over-async, hardcoded secrets
- **High**: Null dereferences, async void, swallowed exceptions, N+1 queries
- **Medium**: Missing CancellationToken, broad catch, missing AsNoTracking
- **Low**: Missing authorization attributes, captive dependencies

Each finding: file:line, what, why, fix.
