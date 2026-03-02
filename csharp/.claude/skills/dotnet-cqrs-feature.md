---
name: dotnet-cqrs-feature
description: Create a complete CQRS feature with MediatR Command/Query, Handler, Validator, DTO, and endpoint.
triggers:
  - "create feature"
  - "add endpoint"
  - "new command"
  - "new query"
  - "add API"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# .NET CQRS Feature Creator Skill

## When Triggered

Create a complete CQRS feature following Clean Architecture conventions.

## Steps

### For a Write Operation (Command):

1. **Create the Command** in `src/Application/Commands/`:
   ```csharp
   namespace App.Application.Commands;

   public record CreateOrderCommand(
       string CustomerId,
       List<OrderItemDto> Items
   ) : IRequest<Result<OrderResponse>>;
   ```

2. **Create the DTO/Response** in `src/Application/DTOs/`:
   ```csharp
   namespace App.Application.DTOs;

   public record OrderResponse(
       Guid Id,
       string CustomerId,
       decimal TotalAmount,
       DateTime CreatedAt
   );

   public record OrderItemDto(string ProductId, int Quantity, decimal UnitPrice);
   ```

3. **Create the Validator** in `src/Application/Commands/`:
   ```csharp
   namespace App.Application.Commands;

   public class CreateOrderValidator : AbstractValidator<CreateOrderCommand>
   {
       public CreateOrderValidator()
       {
           RuleFor(x => x.CustomerId).NotEmpty();
           RuleFor(x => x.Items).NotEmpty();
           RuleForEach(x => x.Items).ChildRules(item =>
           {
               item.RuleFor(i => i.Quantity).GreaterThan(0);
               item.RuleFor(i => i.UnitPrice).GreaterThan(0);
           });
       }
   }
   ```

4. **Create the Handler** in `src/Application/Commands/`:
   ```csharp
   namespace App.Application.Commands;

   public class CreateOrderHandler(
       AppDbContext db,
       ILogger<CreateOrderHandler> logger
   ) : IRequestHandler<CreateOrderCommand, Result<OrderResponse>>
   {
       public async Task<Result<OrderResponse>> Handle(
           CreateOrderCommand request,
           CancellationToken cancellationToken)
       {
           var order = Order.Create(request.CustomerId, request.Items);
           db.Orders.Add(order);
           await db.SaveChangesAsync(cancellationToken);

           logger.LogInformation("Created order {OrderId}", order.Id);
           return Result<OrderResponse>.Success(order.ToResponse());
       }
   }
   ```

5. **Create the Mapping Extension** in `src/Application/Mappings/`:
   ```csharp
   namespace App.Application.Mappings;

   public static class OrderMappings
   {
       public static OrderResponse ToResponse(this Order order) =>
           new(order.Id, order.CustomerId, order.TotalAmount, order.CreatedAt);
   }
   ```

6. **Create the Endpoint** in `src/Api/Endpoints/`:
   ```csharp
   namespace App.Api.Endpoints;

   public static class OrderEndpoints
   {
       public static void MapOrderEndpoints(this IEndpointRouteBuilder app)
       {
           var group = app.MapGroup("/api/orders").WithTags("Orders");

           group.MapPost("/", async (CreateOrderCommand command, ISender sender, CancellationToken ct) =>
           {
               var result = await sender.Send(command, ct);
               return result.IsSuccess
                   ? Results.Created($"/api/orders/{result.Value!.Id}", result.Value)
                   : Results.BadRequest(result.Error);
           });
       }
   }
   ```

7. **Register the endpoint** in `Program.cs`:
   ```csharp
   app.MapOrderEndpoints();
   ```

### For a Read Operation (Query):

Follow the same pattern but use `IRequest<Result<T>>` for Query, read-only handler with `AsNoTracking()`.

8. **Create tests** in `tests/UnitTests/`:
   - Handler tests with mocked DbContext
   - Validator tests for each rule

9. **Run quality gates**:
   ```bash
   dotnet build
   dotnet format src/Application/Application.csproj
   dotnet format src/Api/Api.csproj
   dotnet test tests/UnitTests/UnitTests.csproj --verbosity normal
   ```

## Key Conventions

- Commands = Write operations, Queries = Read operations
- Every Command/Query has a FluentValidation validator
- Handlers use Primary Constructors for DI
- DTOs are `record` types (immutable)
- Explicit mapping (no AutoMapper)
- `CancellationToken` passed through entire chain
- `Result<T>` return type (not thrown exceptions)
