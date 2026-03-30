# Chapter 24: Repository Pattern, Service Layer, and Architecture

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the layered architecture pattern (Controller-Service-Repository)
- Explain the responsibilities of each layer and their boundaries
- Use @Service and @Repository annotations correctly
- Define transaction boundaries at the service layer
- Create custom repository implementations for complex queries
- Build a base entity class for shared audit fields
- Organize packages by feature vs by layer
- Apply the dependency rule: outer layers depend on inner layers
- Avoid common architectural mistakes

---

## Layered Architecture

The standard Spring Boot application follows a three-layer architecture:

```
Layered Architecture:
+------------------------------------------------------------------+
|                                                                   |
|  +------------------------------------------------------------+  |
|  |  CONTROLLER LAYER (@RestController)                         |  |
|  |  - Receives HTTP requests                                   |  |
|  |  - Validates request DTOs (@Valid)                           |  |
|  |  - Calls service methods                                    |  |
|  |  - Returns response DTOs                                    |  |
|  |  - Handles HTTP status codes                                |  |
|  |  - NO business logic, NO database access                    |  |
|  +------------------------------------------------------------+  |
|       |  DTOs                            ^ DTOs                   |
|       v                                  |                        |
|  +------------------------------------------------------------+  |
|  |  SERVICE LAYER (@Service)                                   |  |
|  |  - Contains business logic                                  |  |
|  |  - Defines transaction boundaries (@Transactional)          |  |
|  |  - Coordinates between repositories                         |  |
|  |  - Maps entities to/from DTOs                               |  |
|  |  - Validates business rules                                 |  |
|  |  - NO HTTP concerns, NO SQL                                 |  |
|  +------------------------------------------------------------+  |
|       |  Entities                        ^ Entities               |
|       v                                  |                        |
|  +------------------------------------------------------------+  |
|  |  REPOSITORY LAYER (@Repository / JpaRepository)             |  |
|  |  - Database access (CRUD, queries)                          |  |
|  |  - Spring Data JPA interfaces                               |  |
|  |  - Custom query implementations                             |  |
|  |  - NO business logic, NO HTTP concerns                      |  |
|  +------------------------------------------------------------+  |
|       |                                  ^                        |
|       v                                  |                        |
|  +------------------------------------------------------------+  |
|  |  DATABASE                                                   |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### Layer Responsibilities

```
What Goes Where:
+------------------------------------------------------------------+
|                                                                   |
|  Controller:                  Service:                            |
|  - @GetMapping, @PostMapping  - @Transactional                    |
|  - @Valid @RequestBody        - Business rules                    |
|  - ResponseEntity             - Entity-DTO mapping               |
|  - HTTP status codes          - Coordinate repos                 |
|  - Path variables, params     - Throw business exceptions        |
|  - Exception handling         - Authorization checks             |
|                                                                   |
|  Repository:                  Entity:                             |
|  - extends JpaRepository      - @Entity, @Table                  |
|  - @Query methods             - Field annotations                |
|  - Specifications             - Relationship mappings            |
|  - Custom implementations     - Lifecycle callbacks              |
|  - Projections                - equals/hashCode                  |
|                                                                   |
+------------------------------------------------------------------+
```

---

## The Service Layer in Detail

The service layer is where business logic lives. It orchestrates data access and enforces business rules.

```java
@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;
    private final CustomerRepository customerRepository;
    private final OrderMapper orderMapper;

    public OrderService(OrderRepository orderRepository,
                        ProductRepository productRepository,
                        CustomerRepository customerRepository,
                        OrderMapper orderMapper) {
        this.orderRepository = orderRepository;
        this.productRepository = productRepository;
        this.customerRepository = customerRepository;
        this.orderMapper = orderMapper;
    }

    @Transactional
    public OrderResponse placeOrder(CreateOrderRequest request) {
        // 1. Business validation
        Customer customer = customerRepository.findById(request.getCustomerId())
            .orElseThrow(() -> new CustomerNotFoundException(request.getCustomerId()));

        if (!customer.isActive()) {
            throw new BusinessException("Inactive customers cannot place orders");
        }

        // 2. Create entity
        Order order = new Order(customer);

        // 3. Process items (business logic)
        for (OrderItemRequest itemReq : request.getItems()) {
            Product product = productRepository.findById(itemReq.getProductId())
                .orElseThrow(() -> new ProductNotFoundException(itemReq.getProductId()));

            if (product.getStock() < itemReq.getQuantity()) {
                throw new InsufficientStockException(product.getName());
            }

            order.addItem(product, itemReq.getQuantity());
            product.reduceStock(itemReq.getQuantity());
        }

        // 4. Save and return DTO
        Order saved = orderRepository.save(order);
        return orderMapper.toResponse(saved);
    }

    @Transactional(readOnly = true)
    public Page<OrderSummary> getOrders(Pageable pageable) {
        return orderRepository.findOrderSummaries(pageable);
    }

    @Transactional(readOnly = true)
    public OrderResponse getOrder(Long id) {
        Order order = orderRepository.findWithItemsById(id)
            .orElseThrow(() -> new OrderNotFoundException(id));
        return orderMapper.toResponse(order);
    }
}
```

```
Transaction Boundaries:
+------------------------------------------------------------------+
|                                                                   |
|  Controller (NO @Transactional):                                  |
|  +----------------------------------------------------------+    |
|  | OrderResponse response = orderService.placeOrder(request);|    |
|  | return ResponseEntity.created(uri).body(response);        |    |
|  +----------------------------------------------------------+    |
|                                                                   |
|  Service (@Transactional):                                        |
|  +----------------------------------------------------------+    |
|  | [Transaction starts]                                      |    |
|  | Customer customer = customerRepo.findById(id)             |    |
|  | Product product = productRepo.findById(id)                |    |
|  | order.addItem(product, qty)                               |    |
|  | product.reduceStock(qty)                                  |    |
|  | orderRepo.save(order)                                     |    |
|  | [Dirty checking: UPDATE products SET stock = ...]          |    |
|  | [INSERT INTO orders ...]                                  |    |
|  | [INSERT INTO order_items ...]                              |    |
|  | [Transaction commits]                                     |    |
|  +----------------------------------------------------------+    |
|                                                                   |
|  ALL operations in one transaction:                               |
|  If stock reduction fails, order creation rolls back too.        |
|  Atomicity across multiple repositories.                          |
+------------------------------------------------------------------+
```

---

## The Repository Layer

### Standard Repository

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    // Derived query methods
    List<Order> findByCustomerId(Long customerId);
    List<Order> findByStatus(OrderStatus status);
    boolean existsByCustomerIdAndStatus(Long customerId, OrderStatus status);

    // JPQL queries
    @Query("SELECT o FROM Order o LEFT JOIN FETCH o.items WHERE o.id = :id")
    Optional<Order> findWithItemsById(@Param("id") Long id);

    // Projections
    @Query("SELECT new com.example.dto.OrderSummary(" +
           "o.id, c.name, o.total, o.status, o.createdAt) " +
           "FROM Order o JOIN o.customer c")
    Page<OrderSummary> findOrderSummaries(Pageable pageable);

    // Modifying queries
    @Modifying
    @Query("UPDATE Order o SET o.status = :status WHERE o.id = :id")
    int updateStatus(@Param("id") Long id, @Param("status") OrderStatus status);
}
```

### Custom Repository Implementation

When Spring Data methods are not enough, add custom implementations:

```java
// Step 1: Define custom interface
public interface OrderRepositoryCustom {
    List<Order> findByComplexCriteria(OrderSearchCriteria criteria);
    OrderStatistics calculateStatistics(LocalDate from, LocalDate to);
}
```

```java
// Step 2: Implement it
public class OrderRepositoryCustomImpl implements OrderRepositoryCustom {

    @PersistenceContext
    private EntityManager entityManager;

    @Override
    public List<Order> findByComplexCriteria(OrderSearchCriteria criteria) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<Order> query = cb.createQuery(Order.class);
        Root<Order> root = query.from(Order.class);

        List<Predicate> predicates = new ArrayList<>();

        if (criteria.getCustomerId() != null) {
            predicates.add(cb.equal(root.get("customer").get("id"),
                criteria.getCustomerId()));
        }
        if (criteria.getMinTotal() != null) {
            predicates.add(cb.greaterThanOrEqualTo(root.get("total"),
                criteria.getMinTotal()));
        }
        if (criteria.getStatus() != null) {
            predicates.add(cb.equal(root.get("status"), criteria.getStatus()));
        }
        if (criteria.getFromDate() != null) {
            predicates.add(cb.greaterThanOrEqualTo(root.get("createdAt"),
                criteria.getFromDate()));
        }

        query.where(predicates.toArray(new Predicate[0]));
        query.orderBy(cb.desc(root.get("createdAt")));

        return entityManager.createQuery(query).getResultList();
    }

    @Override
    public OrderStatistics calculateStatistics(LocalDate from, LocalDate to) {
        String jpql = "SELECT new com.example.dto.OrderStatistics(" +
            "COUNT(o), SUM(o.total), AVG(o.total), MIN(o.total), MAX(o.total)) " +
            "FROM Order o WHERE o.createdAt BETWEEN :from AND :to";

        return entityManager.createQuery(jpql, OrderStatistics.class)
            .setParameter("from", from.atStartOfDay())
            .setParameter("to", to.plusDays(1).atStartOfDay())
            .getSingleResult();
    }
}
```

```java
// Step 3: Extend both interfaces in the main repository
@Repository
public interface OrderRepository
        extends JpaRepository<Order, Long>, OrderRepositoryCustom {
    // Spring Data methods + custom methods available together
}
```

```
Custom Repository Naming Convention:
+------------------------------------------------------------------+
|                                                                   |
|  Main interface:   OrderRepository                                |
|  Custom interface: OrderRepositoryCustom                          |
|  Implementation:   OrderRepositoryCustomImpl                      |
|                                                                   |
|  The Impl suffix is REQUIRED by convention.                       |
|  Spring Data finds OrderRepositoryCustomImpl automatically        |
|  and delegates custom method calls to it.                         |
|                                                                   |
|  OrderRepository                                                  |
|  +-- extends JpaRepository (Spring Data auto-implements)         |
|  +-- extends OrderRepositoryCustom                               |
|      +-- OrderRepositoryCustomImpl (you implement)               |
+------------------------------------------------------------------+
```

---

## Base Entity Class

Share common fields across all entities with `@MappedSuperclass`:

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Version   // Optimistic locking
    private Integer version;

    public Long getId() { return id; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public Integer getVersion() { return version; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        BaseEntity that = (BaseEntity) o;
        return id != null && id.equals(that.id);
    }

    @Override
    public int hashCode() {
        return getClass().hashCode();  // Stable across new/managed states
    }
}
```

```java
// All entities extend BaseEntity
@Entity
@Table(name = "products")
public class Product extends BaseEntity {

    @NotBlank
    private String name;

    @Positive
    private BigDecimal price;

    // id, createdAt, updatedAt, version inherited automatically
}
```

```
BaseEntity Fields:
+------------------------------------------------------------------+
|                                                                   |
|  Field        Source              Purpose                         |
|  ----------------------------------------------------------------|
|  id           @GeneratedValue     Primary key                     |
|  createdAt    @CreatedDate        When row was created            |
|  updatedAt    @LastModifiedDate   When row was last modified      |
|  version      @Version            Optimistic locking              |
|                                   (prevents lost updates)         |
|                                                                   |
|  Every entity gets these 4 fields for free.                       |
|  Just extend BaseEntity instead of managing them per entity.     |
+------------------------------------------------------------------+
```

---

## Package Organization

### By Layer (Traditional)

```
By Layer:
+------------------------------------------------------------------+
|                                                                   |
|  com.example.myapp/                                               |
|  +-- controller/                                                  |
|  |   +-- EmployeeController.java                                 |
|  |   +-- DepartmentController.java                               |
|  |   +-- OrderController.java                                    |
|  +-- service/                                                     |
|  |   +-- EmployeeService.java                                    |
|  |   +-- DepartmentService.java                                  |
|  |   +-- OrderService.java                                       |
|  +-- repository/                                                  |
|  |   +-- EmployeeRepository.java                                 |
|  |   +-- DepartmentRepository.java                               |
|  |   +-- OrderRepository.java                                    |
|  +-- entity/                                                      |
|  |   +-- Employee.java                                            |
|  |   +-- Department.java                                          |
|  |   +-- Order.java                                               |
|  +-- dto/                                                         |
|      +-- EmployeeResponse.java                                   |
|      +-- CreateEmployeeRequest.java                              |
|      +-- ...                                                      |
|                                                                   |
|  Problem: Related classes are scattered across packages.          |
|  To understand "Employee", you check 5 packages.                 |
+------------------------------------------------------------------+
```

### By Feature (Recommended for Larger Projects)

```
By Feature:
+------------------------------------------------------------------+
|                                                                   |
|  com.example.myapp/                                               |
|  +-- employee/                                                    |
|  |   +-- Employee.java                                            |
|  |   +-- EmployeeRepository.java                                 |
|  |   +-- EmployeeService.java                                    |
|  |   +-- EmployeeController.java                                 |
|  |   +-- dto/                                                     |
|  |       +-- CreateEmployeeRequest.java                          |
|  |       +-- EmployeeResponse.java                               |
|  +-- department/                                                  |
|  |   +-- Department.java                                          |
|  |   +-- DepartmentRepository.java                               |
|  |   +-- DepartmentService.java                                  |
|  |   +-- DepartmentController.java                               |
|  |   +-- dto/                                                     |
|  +-- order/                                                       |
|  |   +-- Order.java                                               |
|  |   +-- OrderItem.java                                           |
|  |   +-- OrderRepository.java                                    |
|  |   +-- OrderService.java                                       |
|  |   +-- OrderController.java                                    |
|  |   +-- dto/                                                     |
|  +-- common/                                                      |
|      +-- BaseEntity.java                                          |
|      +-- GlobalExceptionHandler.java                              |
|                                                                   |
|  Benefit: Everything about "Employee" is in one place.            |
|  Easier to navigate, understand, and modify.                      |
+------------------------------------------------------------------+
```

```
Choosing Package Structure:
+------------------------------------------------------------------+
|                                                                   |
|  Small project (< 10 entities):   By layer is fine                |
|  Medium project (10-30 entities): By feature recommended          |
|  Large project (30+ entities):    By feature essential             |
|                                                                   |
|  You can mix: feature packages for domain,                       |
|  shared package for cross-cutting concerns.                       |
+------------------------------------------------------------------+
```

---

## Dependency Rules

```
Dependency Direction:
+------------------------------------------------------------------+
|                                                                   |
|  Controller --> Service --> Repository --> Database                |
|                                                                   |
|  Rules:                                                           |
|  1. Controllers depend on Services (never on Repositories)        |
|  2. Services depend on Repositories (never on Controllers)        |
|  3. Repositories depend on Entities (never on Services)           |
|  4. Entities depend on nothing (pure JPA annotations)             |
|                                                                   |
|  Violations to avoid:                                             |
|  X Controller calling Repository directly (skips business logic)  |
|  X Repository calling Service (inverted dependency)               |
|  X Entity depending on Service (entity should be passive)         |
|  X Service depending on Controller (inverted dependency)          |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Putting business logic in controllers**: Controllers should only handle HTTP concerns. Move validation, calculations, and orchestration to the service layer.

2. **Calling repositories directly from controllers**: This bypasses the service layer, losing transaction management and business rule enforcement.

3. **Having services call other services excessively**: Deep service-to-service chains create complex call graphs. Prefer having services coordinate through repositories, not through other services.

4. **Putting @Transactional on repositories**: Spring Data repositories already run each method in a transaction. The service layer defines the business transaction boundary spanning multiple repository calls.

5. **Fat entities with business logic**: Entities should be data holders with JPA annotations. Business rules belong in services.

6. **Creating a service per repository method**: A service method should represent a business operation, not a thin wrapper around a repository call.

---

## Best Practices

1. **One service per domain concept**: `EmployeeService`, `OrderService`, `PaymentService`. Not one service per entity if entities are related.

2. **@Transactional on service methods, not repositories**: The service defines what constitutes a business transaction (e.g., place order = check stock + create order + reduce inventory).

3. **Use constructor injection**: Inject dependencies via constructor, not `@Autowired` fields. This makes dependencies explicit and testing easier.

4. **Return DTOs from service methods**: Services should convert entities to DTOs before returning to the controller. Entities should not leak out of the service layer.

5. **Use BaseEntity for shared fields**: id, createdAt, updatedAt, version — define once, inherit everywhere.

6. **Organize by feature for growing projects**: Group all related classes (entity, repository, service, controller, DTOs) in a feature package.

---

## Summary

- The **three-layer architecture** (Controller-Service-Repository) separates concerns: HTTP handling, business logic, and data access.

- **Controllers** handle HTTP, validate input, and return responses. No business logic.

- **Services** contain business logic, define transaction boundaries with `@Transactional`, coordinate repositories, and map between entities and DTOs.

- **Repositories** handle data access. Use Spring Data interfaces for standard operations and custom implementations for complex queries.

- **Custom repositories** use the `Impl` suffix convention. The main repository extends both `JpaRepository` and the custom interface.

- **BaseEntity** with `@MappedSuperclass` provides shared fields (id, timestamps, version) across all entities.

- **Package by feature** groups related classes together, improving navigability in larger projects.

- **Dependencies flow inward**: Controller -> Service -> Repository -> Database. Never violate this direction.

---

## Interview Questions

**Q1: What are the responsibilities of the service layer?**

The service layer contains business logic, defines transaction boundaries, coordinates between multiple repositories, validates business rules, maps entities to/from DTOs, and enforces authorization. It does not handle HTTP concerns (that is the controller) or write SQL (that is the repository).

**Q2: Why should @Transactional be on the service layer, not the repository?**

The service layer defines business transactions that may span multiple repository operations. For example, placing an order involves checking stock, creating the order, and reducing inventory — all of which must succeed or fail together. Repository methods already run in individual transactions.

**Q3: How do custom repository implementations work in Spring Data?**

Create a custom interface (e.g., `OrderRepositoryCustom`), implement it in a class with the `Impl` suffix (e.g., `OrderRepositoryCustomImpl`), and have the main repository extend both `JpaRepository` and the custom interface. Spring Data detects the `Impl` class and delegates custom method calls to it.

**Q4: What is the advantage of packaging by feature over packaging by layer?**

Feature-based packaging keeps all related classes together (entity, repository, service, controller, DTOs in one package). This makes it easier to understand a feature, navigate the codebase, and enforce boundaries. Layer-based packaging scatters related classes across packages.

**Q5: Why should entities not be returned from controllers?**

Entities expose internal structure (sensitive fields, database schema), cause circular reference issues during JSON serialization, trigger lazy loading exceptions outside transactions, and tightly couple the API to the database schema. DTOs provide a clean, stable API contract.

---

## Practice Exercises

**Exercise 1: Layered Architecture**
Build a complete `Product` CRUD with proper layering: controller (HTTP only), service (business logic, DTO mapping), repository (data access). Verify no layer violates its responsibilities.

**Exercise 2: Custom Repository**
Create a `ProductRepositoryCustom` with a `search(ProductSearchCriteria)` method using Criteria API. Support filters for name, category, price range, and active status — all optional.

**Exercise 3: BaseEntity**
Create a `BaseEntity` with id, createdAt, updatedAt, and version. Create 3 entities extending it. Verify all entities get audit timestamps automatically.

**Exercise 4: Package by Feature**
Refactor an existing project from layer-based to feature-based packaging. Verify that everything still works and that the package structure is clearer.

**Exercise 5: Service Orchestration**
Create an `OrderService.placeOrder()` method that coordinates `CustomerRepository`, `ProductRepository`, and `OrderRepository`. Enforce business rules: customer must be active, stock must be sufficient. Verify atomic transaction behavior (all succeed or all rollback).

---

## What Is Next?

In the next chapter, we will explore **Error Handling and Exception Translation** — how Spring translates database exceptions, how to create a consistent error response format, and how to build a global exception handler with `@ControllerAdvice` for clean error responses across your entire API.
