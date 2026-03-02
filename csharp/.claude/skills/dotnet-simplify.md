---
name: dotnet-simplify
description: Simplify C# code — reduce complexity, modernize to C# 12 patterns, eliminate ceremony, and improve readability.
triggers:
  - "simplify"
  - "simplify code"
  - "reduce complexity"
  - "make simpler"
  - "clean up code"
  - "modernize"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# .NET Code Simplification Skill

## When Triggered

Simplify C#/.NET code by applying modern language features and reducing unnecessary ceremony.

## Simplification Patterns (ordered by impact)

### A. Block-Scoped → File-Scoped Namespaces (removes 1 indent level everywhere)

```csharp
// BEFORE
namespace App.Domain.Entities
{
    public class Order
    {
        // everything indented one extra level
    }
}

// AFTER
namespace App.Domain.Entities;

public class Order
{
    // cleaner, one less indent
}
```

### B. Constructor Injection → Primary Constructors

```csharp
// BEFORE (11 lines of ceremony)
public class OrderService
{
    private readonly IOrderRepository _repo;
    private readonly ILogger<OrderService> _logger;

    public OrderService(IOrderRepository repo, ILogger<OrderService> logger)
    {
        _repo = repo;
        _logger = logger;
    }
}

// AFTER (1 line)
public class OrderService(IOrderRepository repo, ILogger<OrderService> logger)
{
    // use repo and logger directly
}
```

### C. Class DTOs → Records

```csharp
// BEFORE (15+ lines)
public class OrderResponse
{
    public Guid Id { get; set; }
    public string CustomerName { get; set; } = null!;
    public decimal Total { get; set; }
}

// AFTER (1 line)
public record OrderResponse(Guid Id, string CustomerName, decimal Total);
```

### D. `new List<T>()` → Collection Expressions

```csharp
// BEFORE
var items = new List<string>();
var empty = new List<int>();
var arr = new int[] { 1, 2, 3 };

// AFTER
List<string> items = [];
List<int> empty = [];
int[] arr = [1, 2, 3];
```

### E. If/Else Chains → Switch Expressions

```csharp
// BEFORE
string message;
if (status == Status.Active)
    message = "Running";
else if (status == Status.Paused)
    message = "On hold";
else
    message = "Unknown";

// AFTER
var message = status switch
{
    Status.Active => "Running",
    Status.Paused => "On hold",
    _ => "Unknown"
};
```

### F. Null Checks → Pattern Matching + Null-Coalescing

```csharp
// BEFORE
if (user != null && user.Profile != null)
    return user.Profile.Name;
return "Anonymous";

// AFTER
return user?.Profile?.Name ?? "Anonymous";

// BEFORE
if (result is not null)
{
    Process(result);
}

// AFTER
if (result is { } value)
{
    Process(value);
}
```

### G. Flatten Nested Conditionals → Guard Clauses

```csharp
// BEFORE
public Result<Order> Process(OrderRequest request)
{
    if (request != null)
    {
        if (request.Items.Count > 0)
        {
            if (request.CustomerId != null)
            {
                return CreateOrder(request);
            }
            return Result.Failure("Missing customer");
        }
        return Result.Failure("No items");
    }
    return Result.Failure("Null request");
}

// AFTER
public Result<Order> Process(OrderRequest? request)
{
    if (request is null) return Result.Failure("Null request");
    if (request.Items.Count == 0) return Result.Failure("No items");
    if (request.CustomerId is null) return Result.Failure("Missing customer");

    return CreateOrder(request);
}
```

### H. Auto-Format

```bash
dotnet format <project.csproj>
```

## Steps

1. Apply patterns above, one at a time
2. Build after each change: `dotnet build`
3. Run tests: `dotnet test <test project> --verbosity normal`
4. Format: `dotnet format <project.csproj>`
