---
name: dotnet-test-runner
description: Run .NET tests with xUnit, analyze failures, and fix issues autonomously.
triggers:
  - "run tests"
  - "test this"
  - "verify tests pass"
  - "check tests"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# .NET Test Runner Skill

## When Triggered

Run .NET tests using xUnit when the user asks to test code or verify changes.

## Steps

1. **Identify test projects** related to the modified source:
   - Domain/Application changes → `tests/UnitTests/`
   - API/Infrastructure changes → `tests/IntegrationTests/`
   - Architecture rules → `tests/ArchitectureTests/`

2. **Run targeted tests first** (fast feedback):
   ```bash
   dotnet test tests/UnitTests/UnitTests.csproj --verbosity normal --filter "FullyQualifiedName~CreateUser"
   ```

3. **If tests fail**, read the failure output:
   - Build error → Check compilation, missing references
   - Assertion failure → Check business logic or test expectations
   - Fix the issue in source or test code
   - Re-run the failing test

4. **Run broader tests** after fixing:
   ```bash
   dotnet test --verbosity normal
   ```

5. **Run with coverage** if requested:
   ```bash
   dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage
   ```

## Important Rules

- Use `--verbosity normal` for readable output
- Use `--filter` to target specific test classes/methods
- Filter syntax: `--filter "FullyQualifiedName~ClassName"` or `--filter "DisplayName~test_name"`
- Always ensure `CancellationToken.None` is passed in test handler calls
- Use FluentAssertions for readable assertions: `result.Should().BeTrue()`
- Integration tests should use `WebApplicationFactory<Program>` with test database
- Never modify tests just to make them pass — fix the source code
