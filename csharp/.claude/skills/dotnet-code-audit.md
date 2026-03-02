---
name: dotnet-code-audit
description: Comprehensive .NET code quality audit — Roslyn analyzers, architecture rule enforcement, nullable coverage, dependency health, and complexity.
triggers:
  - "audit code"
  - "code audit"
  - "check code quality"
  - "code health"
  - "code review"
  - "analyze code"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# .NET Code Audit Skill

## When Triggered

Perform a comprehensive code quality audit of the .NET codebase.

## Steps

### 1. Compiler Warnings & Roslyn Analyzers

```bash
# Full build with all warnings treated as output
dotnet build --verbosity normal 2>&1 | grep -E "warning|error" | head -40

# Count warnings by category
dotnet build --verbosity normal 2>&1 | grep "warning" | sed 's/.*warning \([A-Z]*[0-9]*\).*/\1/' | sort | uniq -c | sort -rn | head -20
```

**Key warning categories:**
| Category | Meaning |
|----------|---------|
| CS8600-CS8625 | Nullable reference type violations |
| CA1xxx | Code analysis / design rules |
| IDE0xxx | Code style (file-scoped ns, unnecessary using) |
| CS0168/CS0219 | Unused variables |
| CS1998 | Async method lacks await |

### 2. Nullable Reference Type Coverage

```bash
# Check if Nullable is enabled project-wide
grep -rn "<Nullable>" src/ --include="*.csproj"

# Count nullable warnings
dotnet build --verbosity normal 2>&1 | grep -c "CS86"

# Find files with most nullable issues
dotnet build --verbosity normal 2>&1 | grep "CS86" | sed 's/(.*//' | sort | uniq -c | sort -rn | head -10
```

### 3. Architecture Rule Enforcement

Manually verify Clean Architecture boundaries:

```bash
# Domain layer MUST NOT reference infrastructure
grep -rn "using Microsoft.EntityFrameworkCore\|using System.Net.Http\|using MediatR" src/Domain/ --include="*.cs"
# Expected: zero results

# API layer MUST NOT contain business logic
grep -rn "DbContext\|\.SaveChanges\|\.Add(\|\.Remove(" src/Api/ --include="*.cs" | grep -v "Program.cs\|Startup.cs"
# Expected: zero results

# Check for forbidden patterns
grep -rn "AutoMapper\|IMapper" src/ --include="*.cs"                    # Should be zero
grep -rn "IRepository<\|IGenericRepository" src/ --include="*.cs"      # Should be zero
grep -rn "\[Required\]\|\[MaxLength\]" src/ --include="*.cs"           # Should use FluentValidation
grep -rn "\.Result\b\|\.Wait()" src/ --include="*.cs"                  # Sync-over-async
```

### 4. Code Style & Modernization

```bash
# Run dotnet format in check mode (report, don't fix)
dotnet format --verify-no-changes --verbosity diagnostic 2>&1 | head -30

# Find block-scoped namespaces (should be file-scoped)
grep -rn "^namespace.*{$" src/ --include="*.cs" | head -10

# Find old-style constructors (should be primary constructors)
grep -rn "public class.*\n.*{" src/ --include="*.cs" -A 5 | grep "private readonly" | head -10

# Find non-record DTOs
grep -rn "class.*Dto\|class.*Response\|class.*Command\|class.*Query" src/ --include="*.cs" | grep -v "record" | head -10
```

### 5. Async Anti-Patterns

```bash
# Sync-over-async (thread starvation risk)
grep -rn "\.Result\b\|\.Wait()\|\.GetAwaiter().GetResult()" src/ --include="*.cs"

# Missing CancellationToken
grep -rn "async Task" src/ --include="*.cs" | grep -v "CancellationToken" | grep -v "Test" | head -10

# Missing ConfigureAwait (for library code)
grep -rn "await " src/ --include="*.cs" | grep -v "ConfigureAwait\|Test\|Program.cs" | head -10

# Fire-and-forget tasks (lost exceptions)
grep -rn "Task\.Run\|_ = " src/ --include="*.cs" | head -5
```

### 6. Dependency Health

```bash
# List outdated NuGet packages
dotnet list package --outdated 2>&1 | head -30

# Check for deprecated packages
dotnet list package --deprecated 2>&1 | head -20

# Check for vulnerable packages
dotnet list package --vulnerable 2>&1 | head -20
```

### 7. Generate Audit Report

Compile into structured report with:
- Compiler warnings by category
- Nullable coverage gaps
- Architecture violations
- Async anti-patterns
- Modernization opportunities
- Dependency issues
- Prioritized action items
