---
name: dotnet-ef-migration
description: Create and manage Entity Framework Core migrations safely.
triggers:
  - "create migration"
  - "add migration"
  - "database change"
  - "alter table"
  - "new entity"
  - "update schema"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# .NET EF Core Migration Skill

## When Triggered

Create or manage EF Core database migrations when schema changes are needed.

## Steps

1. **Create/modify the Entity** in `src/Domain/Entities/`:
   ```csharp
   namespace App.Domain.Entities;

   public class Order
   {
       public Guid Id { get; private set; }
       public string CustomerId { get; private set; } = null!;
       public decimal TotalAmount { get; private set; }
       public OrderStatus Status { get; private set; }
       public DateTime CreatedAt { get; private set; }
       public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();

       private readonly List<OrderItem> _items = [];

       public static Order Create(string customerId, List<OrderItemDto> items)
       {
           // Factory method with business logic
       }
   }
   ```

2. **Create/update the EF Configuration** in `src/Infrastructure/Data/Configurations/`:
   ```csharp
   namespace App.Infrastructure.Data.Configurations;

   public class OrderConfiguration : IEntityTypeConfiguration<Order>
   {
       public void Configure(EntityTypeBuilder<Order> builder)
       {
           builder.HasKey(o => o.Id);
           builder.Property(o => o.CustomerId).IsRequired().HasMaxLength(255);
           builder.Property(o => o.TotalAmount).HasPrecision(18, 2);
           builder.HasMany(o => o.Items).WithOne().HasForeignKey(i => i.OrderId);
           builder.HasIndex(o => o.CustomerId);
       }
   }
   ```

3. **Register in DbContext** (if new entity):
   ```csharp
   public DbSet<Order> Orders => Set<Order>();
   ```

4. **Generate the migration**:
   ```bash
   dotnet ef migrations add AddOrderTable -p src/Infrastructure -s src/Api
   ```

5. **Review the generated migration** in `src/Infrastructure/Data/Migrations/`:
   - Verify `Up()` and `Down()` methods
   - Check indexes, foreign keys, and constraints
   - Ensure column types and precision are correct

6. **Apply the migration**:
   ```bash
   dotnet ef database update -p src/Infrastructure -s src/Api
   ```

7. **Verify**:
   ```bash
   dotnet ef migrations list -p src/Infrastructure -s src/Api
   dotnet build
   ```

## Key Conventions

- Entity configuration uses Fluent API (IEntityTypeConfiguration), NOT Data Annotations
- Entities have private setters — enforce invariants through methods
- Use factory methods (`Create()`) for entity construction
- Migration names are descriptive: `AddOrderTable`, `AddCustomerEmailIndex`
- Never modify an already-applied migration — create a new one
- Always include `Down()` for reversibility
- Use `HasPrecision()` for decimal columns
- Create indexes for frequently queried columns
- Domain entities must NOT reference EF Core types
