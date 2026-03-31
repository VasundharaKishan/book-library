# Chapter 21: Onion Architecture

## What You Will Learn

- What Onion Architecture is and how it organizes code into concentric layers
- The strict dependency rule: dependencies always point inward
- How Domain Model, Domain Services, Application Services, and Infrastructure relate
- Differences between Onion, Hexagonal, and Clean Architecture
- How to structure a real project using Onion Architecture
- When Onion Architecture is the right choice for your project

## Why This Chapter Matters

In the previous chapters, you learned about layered architecture and hexagonal architecture. Both solve real problems, but they leave room for ambiguity about how layers should depend on each other. Onion Architecture removes that ambiguity with one unbreakable rule: **dependencies always point inward, toward the domain**.

This matters because the domain -- your business logic -- is the most valuable and stable part of your application. Databases change. Frameworks change. APIs change. But the core rules of your business change far less often. Onion Architecture protects that core by ensuring nothing in the outside world leaks into it.

If you have ever worked on a project where changing the database forced you to rewrite business logic, or where unit testing required spinning up a web server, you have felt the pain that Onion Architecture prevents.

---

## The Core Idea: Layers Like an Onion

Onion Architecture arranges your code in concentric rings. The innermost ring is the most important and the most protected. Each outer ring depends on the rings inside it, but never the other way around.

```
+----------------------------------------------------------+
|                    INFRASTRUCTURE                        |
|   (Database, File System, External APIs, UI, Web)        |
|                                                          |
|   +--------------------------------------------------+   |
|   |              APPLICATION SERVICES                |   |
|   |   (Use Cases, Orchestration, DTOs, Commands)     |   |
|   |                                                  |   |
|   |   +------------------------------------------+   |   |
|   |   |           DOMAIN SERVICES                |   |   |
|   |   |   (Business Rules Spanning Entities)     |   |   |
|   |   |                                          |   |   |
|   |   |   +----------------------------------+   |   |   |
|   |   |   |         DOMAIN MODEL             |   |   |   |
|   |   |   |   (Entities, Value Objects,      |   |   |   |
|   |   |   |    Repository Interfaces)        |   |   |   |
|   |   |   +----------------------------------+   |   |   |
|   |   |                                          |   |   |
|   |   +------------------------------------------+   |   |
|   |                                                  |   |
|   +--------------------------------------------------+   |
|                                                          |
+----------------------------------------------------------+

       Dependency Direction: ALWAYS inward -->
```

### The Four Layers

**Layer 1: Domain Model (Innermost)**
This is the heart of your application. It contains entities, value objects, and repository interfaces. It has **zero dependencies** on anything outside itself -- no frameworks, no libraries, no database code.

**Layer 2: Domain Services**
Business logic that does not naturally belong to a single entity lives here. A pricing calculator that needs data from multiple entities, for example. Domain Services depend only on the Domain Model.

**Layer 3: Application Services**
These orchestrate use cases. They receive a command ("place an order"), coordinate domain objects, and return results. They depend on Domain Services and the Domain Model, but not on Infrastructure.

**Layer 4: Infrastructure (Outermost)**
Everything external lives here: database access, file I/O, web frameworks, email services, third-party APIs. Infrastructure implements the interfaces defined in the Domain Model.

---

## The Dependency Rule

This is the single most important rule in Onion Architecture:

> **Source code dependencies must point inward. Nothing in an inner layer can know about anything in an outer layer.**

This means:

- The Domain Model does not import database libraries
- Domain Services do not reference HTTP controllers
- Application Services do not instantiate database connections
- Only Infrastructure knows about concrete implementations

```
WRONG:
  Domain Model --> imports SQLAlchemy (infrastructure concern)

RIGHT:
  Domain Model --> defines OrderRepository interface
  Infrastructure --> implements OrderRepository using SQLAlchemy
```

---

## Before and After: Seeing the Difference

### BEFORE: Everything Depends on the Database

```java
// BEFORE: Domain logic tangled with infrastructure
// Java - Order.java
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

public class Order {
    private Connection dbConnection;

    public Order(Connection dbConnection) {
        this.dbConnection = dbConnection;
    }

    public double calculateTotal() {
        double total = 0;
        try {
            PreparedStatement stmt = dbConnection.prepareStatement(
                "SELECT price, quantity FROM order_items WHERE order_id = ?"
            );
            stmt.setLong(1, this.id);
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                total += rs.getDouble("price") * rs.getInt("quantity");
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
        return total;
    }

    public void applyDiscount(double percentage) {
        // Business rule buried inside database code
        if (percentage > 50) {
            throw new IllegalArgumentException("Discount cannot exceed 50%");
        }
        try {
            PreparedStatement stmt = dbConnection.prepareStatement(
                "UPDATE orders SET discount = ? WHERE id = ?"
            );
            stmt.setDouble(1, percentage);
            stmt.setLong(2, this.id);
            stmt.executeUpdate();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

**Problems with this approach:**
- Cannot test `calculateTotal()` without a real database
- Business rule (max 50% discount) is buried in database code
- Changing databases means rewriting business logic
- The `Order` class has two reasons to change: business rules AND data access

### AFTER: Onion Architecture Separates Concerns

```java
// AFTER: Clean separation with Onion Architecture

// === LAYER 1: DOMAIN MODEL ===

// domain/model/OrderItem.java
public class OrderItem {
    private final String productId;
    private final double price;
    private final int quantity;

    public OrderItem(String productId, double price, int quantity) {
        if (price < 0) throw new IllegalArgumentException("Price cannot be negative");
        if (quantity < 1) throw new IllegalArgumentException("Quantity must be at least 1");
        this.productId = productId;
        this.price = price;
        this.quantity = quantity;
    }

    public double subtotal() {
        return price * quantity;
    }
}

// domain/model/Order.java
public class Order {
    private final String orderId;
    private final List<OrderItem> items;
    private double discountPercentage;

    public Order(String orderId, List<OrderItem> items) {
        this.orderId = orderId;
        this.items = new ArrayList<>(items);
        this.discountPercentage = 0;
    }

    public double calculateTotal() {
        double subtotal = items.stream()
            .mapToDouble(OrderItem::subtotal)
            .sum();
        return subtotal * (1 - discountPercentage / 100);
    }

    public void applyDiscount(double percentage) {
        if (percentage > 50) {
            throw new IllegalArgumentException("Discount cannot exceed 50%");
        }
        this.discountPercentage = percentage;
    }
}

// domain/model/OrderRepository.java (INTERFACE in the domain)
public interface OrderRepository {
    Order findById(String orderId);
    void save(Order order);
    List<Order> findByCustomerId(String customerId);
}
```

```java
// === LAYER 2: DOMAIN SERVICES ===

// domain/service/PricingService.java
public class PricingService {

    public double calculateLoyaltyDiscount(Order order, int customerOrderCount) {
        // Business rule: loyal customers get bigger discounts
        if (customerOrderCount > 100) return 15.0;
        if (customerOrderCount > 50) return 10.0;
        if (customerOrderCount > 10) return 5.0;
        return 0.0;
    }
}
```

```java
// === LAYER 3: APPLICATION SERVICES ===

// application/PlaceOrderUseCase.java
public class PlaceOrderUseCase {
    private final OrderRepository orderRepository;
    private final PricingService pricingService;

    // Dependencies injected -- no concrete classes, only interfaces/domain types
    public PlaceOrderUseCase(OrderRepository orderRepository,
                             PricingService pricingService) {
        this.orderRepository = orderRepository;
        this.pricingService = pricingService;
    }

    public OrderResult execute(PlaceOrderCommand command) {
        List<OrderItem> items = command.getItems().stream()
            .map(i -> new OrderItem(i.getProductId(), i.getPrice(), i.getQuantity()))
            .collect(Collectors.toList());

        Order order = new Order(generateId(), items);

        double discount = pricingService.calculateLoyaltyDiscount(
            order, command.getCustomerOrderCount()
        );
        order.applyDiscount(discount);

        orderRepository.save(order);

        return new OrderResult(order.getOrderId(), order.calculateTotal());
    }
}
```

```java
// === LAYER 4: INFRASTRUCTURE ===

// infrastructure/persistence/JpaOrderRepository.java
public class JpaOrderRepository implements OrderRepository {
    private final EntityManager entityManager;

    public JpaOrderRepository(EntityManager entityManager) {
        this.entityManager = entityManager;
    }

    @Override
    public Order findById(String orderId) {
        OrderEntity entity = entityManager.find(OrderEntity.class, orderId);
        return toDomain(entity);
    }

    @Override
    public void save(Order order) {
        OrderEntity entity = toEntity(order);
        entityManager.persist(entity);
    }

    @Override
    public List<Order> findByCustomerId(String customerId) {
        // JPA query implementation
        return entityManager
            .createQuery("SELECT o FROM OrderEntity o WHERE o.customerId = :cid")
            .setParameter("cid", customerId)
            .getResultList()
            .stream()
            .map(this::toDomain)
            .collect(Collectors.toList());
    }
}
```

**What changed:**
- Domain Model has zero infrastructure dependencies
- Business rules are testable with plain unit tests
- Swapping databases means only changing the Infrastructure layer
- Each layer has a single, clear responsibility

---

## The Same Example in Python

```python
# === LAYER 1: DOMAIN MODEL ===

# domain/model/order.py
from dataclasses import dataclass, field
from typing import List
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class OrderItem:
    """Value Object -- immutable, identity does not matter."""
    product_id: str
    price: float
    quantity: int

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.quantity < 1:
            raise ValueError("Quantity must be at least 1")

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


class Order:
    """Entity -- has identity (order_id)."""
    def __init__(self, order_id: str, items: List[OrderItem]):
        self.order_id = order_id
        self._items = list(items)
        self._discount_percentage = 0.0

    def calculate_total(self) -> float:
        subtotal = sum(item.subtotal for item in self._items)
        return subtotal * (1 - self._discount_percentage / 100)

    def apply_discount(self, percentage: float) -> None:
        if percentage > 50:
            raise ValueError("Discount cannot exceed 50%")
        self._discount_percentage = percentage


class OrderRepository(ABC):
    """Interface defined in the domain -- implemented in infrastructure."""

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order:
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        pass
```

```python
# === LAYER 2: DOMAIN SERVICES ===

# domain/service/pricing_service.py
from domain.model.order import Order


class PricingService:
    def calculate_loyalty_discount(self, order: Order,
                                    customer_order_count: int) -> float:
        if customer_order_count > 100:
            return 15.0
        if customer_order_count > 50:
            return 10.0
        if customer_order_count > 10:
            return 5.0
        return 0.0
```

```python
# === LAYER 3: APPLICATION SERVICES ===

# application/place_order_use_case.py
from dataclasses import dataclass
from typing import List
from domain.model.order import Order, OrderItem, OrderRepository
from domain.service.pricing_service import PricingService
import uuid


@dataclass
class PlaceOrderCommand:
    items: List[dict]
    customer_order_count: int


@dataclass
class OrderResult:
    order_id: str
    total: float


class PlaceOrderUseCase:
    def __init__(self, order_repository: OrderRepository,
                 pricing_service: PricingService):
        self._order_repository = order_repository
        self._pricing_service = pricing_service

    def execute(self, command: PlaceOrderCommand) -> OrderResult:
        items = [
            OrderItem(i["product_id"], i["price"], i["quantity"])
            for i in command.items
        ]

        order = Order(str(uuid.uuid4()), items)

        discount = self._pricing_service.calculate_loyalty_discount(
            order, command.customer_order_count
        )
        order.apply_discount(discount)

        self._order_repository.save(order)

        return OrderResult(order.order_id, order.calculate_total())
```

```python
# === LAYER 4: INFRASTRUCTURE ===

# infrastructure/persistence/sqlalchemy_order_repository.py
from sqlalchemy.orm import Session
from domain.model.order import Order, OrderItem, OrderRepository


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, order_id: str) -> Order:
        entity = self._session.query(OrderEntity).get(order_id)
        return self._to_domain(entity)

    def save(self, order: Order) -> None:
        entity = self._to_entity(order)
        self._session.add(entity)
        self._session.commit()

    def _to_domain(self, entity) -> Order:
        items = [
            OrderItem(ie.product_id, ie.price, ie.quantity)
            for ie in entity.items
        ]
        return Order(entity.order_id, items)

    def _to_entity(self, order: Order):
        # Convert domain object to SQLAlchemy entity
        pass
```

---

## Complete Project Folder Structure

Here is how a real project organized with Onion Architecture looks on disk:

```
my-order-service/
|
+-- domain/                          # LAYERS 1 & 2 (innermost)
|   +-- model/
|   |   +-- order.py                 # Order entity
|   |   +-- order_item.py            # OrderItem value object
|   |   +-- customer.py              # Customer entity
|   |   +-- order_repository.py      # Repository interface
|   |   +-- customer_repository.py   # Repository interface
|   |
|   +-- service/
|       +-- pricing_service.py       # Domain service
|       +-- inventory_checker.py     # Domain service
|
+-- application/                     # LAYER 3
|   +-- use_cases/
|   |   +-- place_order.py           # Use case
|   |   +-- cancel_order.py          # Use case
|   |   +-- get_order_status.py      # Query use case
|   |
|   +-- dto/
|       +-- order_commands.py        # Input DTOs
|       +-- order_results.py         # Output DTOs
|
+-- infrastructure/                  # LAYER 4 (outermost)
|   +-- persistence/
|   |   +-- sqlalchemy_order_repo.py # Repository implementation
|   |   +-- orm_models.py            # Database models
|   |
|   +-- web/
|   |   +-- flask_app.py             # Web framework setup
|   |   +-- order_controller.py      # HTTP endpoints
|   |
|   +-- messaging/
|   |   +-- rabbitmq_publisher.py    # Message queue
|   |
|   +-- config/
|       +-- settings.py              # Configuration
|
+-- tests/
    +-- unit/
    |   +-- test_order.py            # Tests domain model (no infra)
    |   +-- test_pricing_service.py  # Tests domain service
    |   +-- test_place_order.py      # Tests use case with mocks
    |
    +-- integration/
        +-- test_order_repository.py # Tests with real database
```

Notice how the `domain/` folder has no imports from `infrastructure/`. You can verify this with a simple grep:

```bash
# This should return ZERO results in a properly structured project
grep -r "from infrastructure" domain/
grep -r "import infrastructure" domain/
```

---

## Onion vs Hexagonal vs Clean Architecture

These three architectures share the same core philosophy -- protect the domain from infrastructure -- but differ in terminology and emphasis.

```
+--------------------+--------------------+---------------------+
|  ONION             |  HEXAGONAL         |  CLEAN              |
|  ARCHITECTURE      |  ARCHITECTURE      |  ARCHITECTURE       |
+--------------------+--------------------+---------------------+
| Domain Model       | Domain Model       | Entities            |
+--------------------+--------------------+---------------------+
| Domain Services    | Domain Services    | Use Cases           |
+--------------------+--------------------+---------------------+
| Application        | Application        | Interface           |
| Services           | Services (Ports)   | Adapters            |
+--------------------+--------------------+---------------------+
| Infrastructure     | Adapters           | Frameworks &        |
|                    |                    | Drivers              |
+--------------------+--------------------+---------------------+
| Emphasizes:        | Emphasizes:        | Emphasizes:         |
| Explicit layers    | Ports and adapters | Dependency rule     |
| with strict        | for pluggable      | across concentric   |
| inward dependency  | external systems   | circles             |
+--------------------+--------------------+---------------------+
| Coined by:         | Coined by:         | Coined by:          |
| Jeffrey Palermo    | Alistair Cockburn  | Robert C. Martin    |
| (2008)             | (2005)             | (2012)              |
+--------------------+--------------------+---------------------+
```

**Key Differences:**

| Aspect                  | Onion           | Hexagonal         | Clean              |
|--------------------------|-----------------|--------------------|--------------------|
| Number of layers         | 4 explicit      | 2 (inside/outside) | 4 concentric rings |
| How externals connect    | Dependency injection | Ports and adapters | Interface adapters |
| Primary metaphor         | Onion rings     | Hexagon with ports | Concentric circles |
| Domain isolation method  | Layer boundaries | Port interfaces   | Dependency rule    |
| Practical difference     | Most prescriptive about layers | Most flexible about structure | Most prescriptive about dependency direction |

**The truth:** In practice, all three lead to very similar code. The differences are mainly in vocabulary and emphasis. Choose the one whose mental model makes the most sense to your team.

---

## Real-World Scenario: Hospital Patient Management

Imagine you are building a patient management system for a hospital.

```
+----------------------------------------------------------+
|  INFRASTRUCTURE                                          |
|  - PostgreSQL for patient records                        |
|  - REST API for doctor-facing app                        |
|  - HL7 FHIR adapter for insurance systems                |
|  - Email service for appointment reminders               |
|                                                          |
|  +----------------------------------------------------+  |
|  |  APPLICATION SERVICES                               |  |
|  |  - ScheduleAppointmentUseCase                       |  |
|  |  - AdmitPatientUseCase                              |  |
|  |  - TransferPatientUseCase                           |  |
|  |  - DischargePatientUseCase                          |  |
|  |                                                     |  |
|  |  +----------------------------------------------+   |  |
|  |  |  DOMAIN SERVICES                             |   |  |
|  |  |  - BedAllocationService                      |   |  |
|  |  |  - InsuranceVerificationService (interface)  |   |  |
|  |  |  - MedicationInteractionChecker              |   |  |
|  |  |                                              |   |  |
|  |  |  +--------------------------------------+    |   |  |
|  |  |  |  DOMAIN MODEL                        |    |   |  |
|  |  |  |  - Patient (entity)                  |    |   |  |
|  |  |  |  - Appointment (entity)              |    |   |  |
|  |  |  |  - MedicalRecord (entity)            |    |   |  |
|  |  |  |  - Diagnosis (value object)          |    |   |  |
|  |  |  |  - Medication (value object)         |    |   |  |
|  |  |  |  - PatientRepository (interface)     |    |   |  |
|  |  |  +--------------------------------------+    |   |  |
|  |  +----------------------------------------------+   |  |
|  +----------------------------------------------------+  |
+----------------------------------------------------------+
```

The Domain Model knows nothing about PostgreSQL, REST, or HL7. If the hospital switches from PostgreSQL to MongoDB, only the Infrastructure layer changes. If they add a mobile app, they add a new adapter in Infrastructure. The domain stays untouched.

---

## When to Use Onion Architecture

**Good fit:**
- Medium to large applications with complex business logic
- Projects where the domain is the competitive advantage
- Teams that want clear architectural guidance on where code belongs
- Systems that need to support multiple delivery mechanisms (web, mobile, CLI)
- Long-lived applications where infrastructure will change over time

**Not a good fit:**
- Simple CRUD applications with little business logic
- Prototypes or throwaway projects
- Very small microservices that are essentially data pipes
- Projects where time-to-market matters more than long-term maintainability

---

## Common Mistakes

**Mistake 1: Putting business logic in the Application Services layer.**
Application Services should orchestrate, not decide. If you see `if/else` statements about business rules in a use case class, that logic belongs in the Domain Model or Domain Services.

**Mistake 2: Having the Domain Model depend on infrastructure types.**
Your `Order` entity should never import `@Entity` from JPA or inherit from a SQLAlchemy `Base`. Use separate ORM models in the Infrastructure layer and map between them.

**Mistake 3: Making every layer depend on a shared "commons" package.**
A shared utilities package that every layer imports defeats the purpose. If something is truly shared, it should be in the Domain Model (innermost layer). If it is infrastructure-specific, keep it in Infrastructure.

**Mistake 4: Skipping layers.**
If a controller directly calls a repository without going through a use case, you have bypassed the architecture. Every external request should flow through Application Services.

**Mistake 5: Over-engineering simple operations.**
A simple "get user by ID" query does not need a Domain Service, an Application Service, and three DTOs. Use the architecture where it adds value, and keep simple operations simple.

---

## Best Practices

1. **Define interfaces in the domain, implement them in infrastructure.** Repository interfaces live in the Domain Model. Concrete database classes live in Infrastructure.

2. **Keep the Domain Model free of annotations and decorators.** No `@Entity`, no `@Column`, no `@JsonProperty`. These are infrastructure concerns.

3. **Use Application Services as the entry point for all operations.** Controllers call Application Services, never Domain Services or Repositories directly.

4. **Test the domain without infrastructure.** If your domain tests require a database, something is wrong. Domain tests should be fast, plain unit tests.

5. **Map between layers explicitly.** Use DTOs at the Application Services boundary. Use ORM entities at the Infrastructure boundary. The Domain Model uses its own types.

6. **Enforce the dependency rule with tooling.** Use module dependency checks, architectural fitness functions, or import analysis tools to catch violations early.

---

## Quick Summary

Onion Architecture organizes code into four concentric layers: Domain Model at the center, surrounded by Domain Services, then Application Services, and finally Infrastructure on the outside. The fundamental rule is that dependencies always point inward -- outer layers depend on inner layers, never the reverse. This protects your business logic from infrastructure changes and makes the domain testable in isolation.

---

## Key Points

- Onion Architecture has four explicit layers: Domain Model, Domain Services, Application Services, and Infrastructure
- The dependency rule states that code dependencies must always point inward
- The Domain Model is the innermost layer and has zero external dependencies
- Repository interfaces are defined in the domain but implemented in infrastructure
- Infrastructure (databases, web frameworks, external APIs) lives in the outermost layer
- Onion, Hexagonal, and Clean Architecture share the same core philosophy with different vocabulary
- The architecture shines when business logic is complex and infrastructure is expected to change
- Simple CRUD applications may not benefit from the additional structure

---

## Practice Questions

1. A developer adds a `@Entity` JPA annotation to a domain class to "save time." What architectural rule does this violate, and what problems could it cause?

2. Your team has a `PricingService` that calculates discounts. It currently lives in the Application Services layer. A new requirement says the discount calculation needs data from two different entities. Where should `PricingService` live, and why?

3. Draw the dependency arrows for this scenario: `OrderController` calls `PlaceOrderUseCase`, which calls `OrderRepository`. `JpaOrderRepository` implements `OrderRepository`. Which arrows point inward, and which point outward?

4. You are told to add Redis caching to speed up order lookups. Which layer does the caching code belong in? Should the `Order` entity know about Redis?

5. A junior developer argues that having four layers is "over-engineering" for their CRUD app. Are they right? Under what circumstances would you agree with them?

---

## Exercises

### Exercise 1: Identify the Layer Violations

The following code has three architectural violations. Find them and explain which layer each piece of code should live in.

```python
# domain/model/invoice.py
from sqlalchemy import Column, Integer, String    # Violation?
from infrastructure.email import send_email        # Violation?

class Invoice:
    def __init__(self, amount, customer_email):
        self.amount = amount
        self.customer_email = customer_email

    def finalize(self):
        if self.amount > 10000:
            send_email(self.customer_email,          # Violation?
                      "Large invoice requires approval")
        self.status = "FINALIZED"
```

### Exercise 2: Restructure a Monolith

Take a simple application (a library book checkout system) and restructure it using Onion Architecture. Define:

- At least two entities (e.g., `Book`, `Member`)
- One value object (e.g., `ISBN`)
- One repository interface
- One domain service (e.g., `LateFeesCalculator`)
- One application service (e.g., `CheckOutBookUseCase`)
- One infrastructure implementation (e.g., in-memory repository)

Write the code so that the domain layer has zero imports from infrastructure.

### Exercise 3: Swap the Database

Using your solution from Exercise 2, write a second repository implementation that stores data in a JSON file instead of in memory. Verify that you do not need to change any code in the domain or application layers. This proves your architecture is working correctly.

---

## What Is Next?

Now that you understand how to structure your application with explicit layers and inward dependencies, the next chapter explores **Domain-Driven Design (DDD)** -- the methodology for modeling the business domain that lives at the center of your onion. DDD gives you the tools to build rich, expressive domain models that capture real business rules, not just data containers.
