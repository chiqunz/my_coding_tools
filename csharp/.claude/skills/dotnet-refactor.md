---
name: dotnet-refactor
description: Refactor C# code to modern patterns while maintaining functionality and Clean Architecture compliance.
triggers:
  - "refactor"
  - "clean up"
  - "modernize"
  - "improve code"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# .NET Refactoring Skill

## When Triggered

Refactor C#/.NET code to modern patterns while preserving behavior.

## Steps

1. **Read and understand** the current code and its tests
2. **Identify refactoring opportunities**:

   **Language Modernization:**
   - Constructor injection → Primary Constructors
   - `class` DTOs → `record` types
   - Block-scoped namespace `{ }` → File-scoped `namespace X;`
   - `new List<T>()` → `List<T> x = []` (collection expressions)
   - `if/else if/else` chains → `switch` expressions
   - `Nullable<T>` → Enable Nullable Reference Types
   - String concatenation → String interpolation or raw string literals
   - `var x = new ClassName()` → Target-typed `new()`

   **Architecture:**
   - Business logic in controllers → Move to MediatR Handlers
   - Custom Generic Repository → Use DbContext directly
   - AutoMapper → Explicit mapping extensions
   - Data Annotations → FluentValidation
   - Thrown exceptions for control flow → Result\<T\> pattern
   - Startup.cs → Minimal API Program.cs
   - `.Result`/`.Wait()` → `await` with `CancellationToken`

3. **Make changes incrementally** — one concern at a time

4. **Run tests after each change**:
   ```bash
   dotnet test tests/UnitTests/UnitTests.csproj --verbosity normal
   ```

5. **Run full quality gates**:
   ```bash
   dotnet build  # Zero warnings
   dotnet format <modified project>
   dotnet test --verbosity normal
   ```

## Refactoring Checklist

- [ ] Primary Constructors for DI
- [ ] Record types for DTOs/Commands/Queries
- [ ] File-scoped namespaces
- [ ] Collection expressions where applicable
- [ ] Pattern matching over if/else
- [ ] Nullable Reference Types enabled and clean
- [ ] CancellationToken in all async methods
- [ ] No `.Result`/`.Wait()` calls
- [ ] No AutoMapper — explicit mappings only
- [ ] No Generic Repository — DbContext directly
- [ ] FluentValidation — no Data Annotations
- [ ] Result\<T\> — no thrown exceptions for control flow
- [ ] AsNoTracking() on read-only queries
- [ ] Domain layer has zero external dependencies
- [ ] All tests pass
