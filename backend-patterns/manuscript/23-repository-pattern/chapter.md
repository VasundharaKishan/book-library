# Chapter 23: Repository Pattern

## What You Will Learn

- What the Repository pattern is and why it exists
- How to create a collection-like interface for data access
- How to implement repositories in Java using Spring Data JPA
- How to implement repositories in Python using SQLAlchemy
- The difference between Repository and DAO (Data Access Object)
- How to build in-memory repositories for testing
- How to apply the Repository pattern in clean architecture

## Why This Chapter Matters

Every backend application needs to store and retrieve data. The moment you scatter SQL queries or ORM calls throughout your business logic, you create a tangled mess that is painful to test, hard to change, and impossible to migrate to a different database.

The Repository pattern solves this by placing a clean boundary between your domain logic and your data access code. Your business layer talks to a simple, collection-like interface: "give me all active users," "save this order," "find the product with this ID." It never knows whether the data comes from PostgreSQL, MongoDB, an in-memory list, or a remote API.

This separation is not academic theory. It is a practical technique used in production systems worldwide. When your team decides to switch from MySQL to DynamoDB, only the repository implementation changes. When you write unit tests, you swap in a fake repository that runs in memory. Your business logic stays untouched.

---

## The Problem

Imagine you are building an order management system. Your service class needs to find orders, save new ones, and update existing ones. Without any abstraction, your code looks like this:

### Before: Data Access Mixed with Business Logic

**Java (JDBC scattered everywhere):**

```java
public class OrderService {

    private final DataSource dataSource;

    public OrderService(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public Order findOrderById(Long id) {
        String sql = "SELECT id, customer_id, total, status FROM orders WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, id);
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                Order order = new Order();
                order.setId(rs.getLong("id"));
                order.setCustomerId(rs.getLong("customer_id"));
                order.setTotal(rs.getBigDecimal("total"));
                order.setStatus(rs.getString("status"));
                return order;
            }
            return null;
        } catch (SQLException e) {
            throw new RuntimeException("Failed to find order", e);
        }
    }

    public void applyDiscount(Long orderId, double discountPercent) {
        // Business logic tangled with data access
        String sql = "SELECT id, customer_id, total, status FROM orders WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, orderId);
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                BigDecimal total = rs.getBigDecimal("total");
                BigDecimal discount = total.multiply(
                    BigDecimal.valueOf(discountPercent / 100));
                BigDecimal newTotal = total.subtract(discount);

                String updateSql = "UPDATE orders SET total = ? WHERE id = ?";
                try (PreparedStatement updateStmt =
                         conn.prepareStatement(updateSql)) {
                    updateStmt.setBigDecimal(1, newTotal);
                    updateStmt.setLong(2, orderId);
                    updateStmt.executeUpdate();
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to apply discount", e);
        }
    }
}
```

**Python (raw SQL everywhere):**

```python
import sqlite3

class OrderService:
    def __init__(self, db_path):
        self.db_path = db_path

    def find_order_by_id(self, order_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, customer_id, total, status FROM orders WHERE id = ?",
            (order_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"id": row[0], "customer_id": row[1],
                    "total": row[2], "status": row[3]}
        return None

    def apply_discount(self, order_id, discount_percent):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT total FROM orders WHERE id = ?", (order_id,)
        )
        row = cursor.fetchone()
        if row:
            new_total = row[0] * (1 - discount_percent / 100)
            cursor.execute(
                "UPDATE orders SET total = ? WHERE id = ?",
                (new_total, order_id)
            )
            conn.commit()
        conn.close()
```

**What is wrong with this?**

1. Business logic (calculating discounts) is mixed with data access (SQL queries)
2. You cannot test `applyDiscount` without a real database
3. Changing the database means rewriting every method
4. SQL is duplicated across multiple service classes
5. No consistent error handling strategy

---

## The Solution: Repository Pattern

The Repository pattern introduces an abstraction that looks like an in-memory collection of domain objects. Your service code calls methods like `findById()`, `save()`, and `findAll()` without knowing anything about the underlying storage.

```
+------------------+       +--------------------+       +------------+
|                  |       |                    |       |            |
|  Business Logic  | ----> |    Repository      | ----> |  Database  |
|  (OrderService)  |       |  (Interface)       |       |            |
|                  |       |                    |       |            |
+------------------+       +--------------------+       +------------+
                                    ^
                                    |
                           +--------+--------+
                           |                 |
                    +------+------+   +------+------+
                    |   JPA Impl  |   | In-Memory   |
                    | (Production)|   |   (Testing)  |
                    +-------------+   +-------------+
```

### After: Clean Separation with Repository

**Java:**

```java
// Step 1: Define the repository interface
public interface OrderRepository {
    Order findById(Long id);
    List<Order> findAll();
    List<Order> findByStatus(String status);
    Order save(Order order);
    void delete(Order order);
}

// Step 2: Service uses only the interface
public class OrderService {

    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public void applyDiscount(Long orderId, double discountPercent) {
        Order order = orderRepository.findById(orderId);
        if (order == null) {
            throw new IllegalArgumentException("Order not found: " + orderId);
        }

        BigDecimal discount = order.getTotal()
            .multiply(BigDecimal.valueOf(discountPercent / 100));
        order.setTotal(order.getTotal().subtract(discount));

        orderRepository.save(order);
    }

    public List<Order> getPendingOrders() {
        return orderRepository.findByStatus("PENDING");
    }
}
```

**Python:**

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class OrderRepository(ABC):
    """Abstract repository - looks like a collection of orders."""

    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[dict]:
        pass

    @abstractmethod
    def find_all(self) -> List[dict]:
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[dict]:
        pass

    @abstractmethod
    def save(self, order: dict) -> dict:
        pass

    @abstractmethod
    def delete(self, order_id: int) -> None:
        pass


class OrderService:
    """Service uses only the repository interface."""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def apply_discount(self, order_id: int, discount_percent: float):
        order = self.order_repository.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order not found: {order_id}")

        discount = order["total"] * (discount_percent / 100)
        order["total"] -= discount

        self.order_repository.save(order)

    def get_pending_orders(self) -> list:
        return self.order_repository.find_by_status("PENDING")
```

Notice how `OrderService` has zero knowledge of SQL, databases, or ORMs. It simply calls repository methods that behave like collection operations.

---

## How the Repository Pattern Works

```
    Client Code (Service Layer)
            |
            |  findById(42)
            v
    +-------------------+
    |    Repository      |     <-- Interface: Collection-like API
    |    Interface       |
    +-------------------+
            |
            |  (Implementation chosen at runtime)
            v
    +-------------------+         +-------------------+
    |  JpaOrderRepo     |   OR   | InMemoryOrderRepo  |
    |  (Production)     |         | (Testing)          |
    +-------------------+         +-------------------+
            |                              |
            v                              v
    +-------------------+         +-------------------+
    |   PostgreSQL      |         |   HashMap / Dict   |
    |   Database        |         |   (in memory)      |
    +-------------------+         +-------------------+
```

The key components:

1. **Repository Interface** - Defines collection-like operations (find, save, delete)
2. **Concrete Implementation** - Connects to the actual data store
3. **Domain Entity** - The object being stored and retrieved
4. **Client Code** - Uses only the interface, never the implementation directly

---

## Java Implementation: Spring Data JPA Repository

Spring Data JPA makes the Repository pattern almost effortless. You define an interface, and Spring generates the implementation at runtime.

### Step 1: Define the Entity

```java
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "orders")
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(nullable = false)
    private BigDecimal total;

    @Column(nullable = false)
    private String status;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    // Constructors
    public Order() {}

    public Order(Long customerId, BigDecimal total, String status) {
        this.customerId = customerId;
        this.total = total;
        this.status = status;
        this.createdAt = LocalDateTime.now();
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getCustomerId() { return customerId; }
    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }
    public BigDecimal getTotal() { return total; }
    public void setTotal(BigDecimal total) { this.total = total; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "Order{id=" + id + ", customerId=" + customerId +
               ", total=" + total + ", status='" + status + "'}";
    }
}
```

### Step 2: Define the Repository Interface

```java
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.math.BigDecimal;
import java.util.List;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    // Spring generates SQL from method name automatically
    List<Order> findByStatus(String status);

    List<Order> findByCustomerId(Long customerId);

    List<Order> findByStatusAndCustomerId(String status, Long customerId);

    // Custom query when method naming is not enough
    @Query("SELECT o FROM Order o WHERE o.total > :minTotal ORDER BY o.total DESC")
    List<Order> findExpensiveOrders(BigDecimal minTotal);

    @Query("SELECT COUNT(o) FROM Order o WHERE o.status = :status")
    long countByStatus(String status);
}
```

### Step 3: Use the Repository in a Service

```java
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.util.List;

@Service
public class OrderService {

    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @Transactional
    public Order createOrder(Long customerId, BigDecimal total) {
        Order order = new Order(customerId, total, "PENDING");
        return orderRepository.save(order);
    }

    @Transactional
    public Order confirmOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new RuntimeException("Order not found"));
        order.setStatus("CONFIRMED");
        return orderRepository.save(order);
    }

    public List<Order> getPendingOrders() {
        return orderRepository.findByStatus("PENDING");
    }

    public List<Order> getCustomerOrders(Long customerId) {
        return orderRepository.findByCustomerId(customerId);
    }
}
```

**Output when running:**

```
Created: Order{id=1, customerId=100, total=250.00, status='PENDING'}
Created: Order{id=2, customerId=100, total=75.50, status='PENDING'}
Created: Order{id=3, customerId=200, total=500.00, status='PENDING'}

Confirmed: Order{id=1, customerId=100, total=250.00, status='CONFIRMED'}

Pending orders: 2
Customer 100 orders: 2
```

---

## Python Implementation: SQLAlchemy Repository

In Python, we build the Repository pattern explicitly since SQLAlchemy does not generate implementations for us.

### Step 1: Define the Model

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (f"Order(id={self.id}, customer_id={self.customer_id}, "
                f"total={self.total}, status='{self.status}')")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "total": self.total,
            "status": self.status,
            "created_at": str(self.created_at),
        }
```

### Step 2: Define the Abstract Repository

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class AbstractOrderRepository(ABC):
    """Collection-like interface for Order entities."""

    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[Order]:
        pass

    @abstractmethod
    def find_all(self) -> List[Order]:
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Order]:
        pass

    @abstractmethod
    def find_by_customer_id(self, customer_id: int) -> List[Order]:
        pass

    @abstractmethod
    def save(self, order: Order) -> Order:
        pass

    @abstractmethod
    def delete(self, order: Order) -> None:
        pass
```

### Step 3: SQLAlchemy Implementation

```python
from sqlalchemy.orm import Session

class SqlAlchemyOrderRepository(AbstractOrderRepository):
    """Repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, order_id: int) -> Optional[Order]:
        return self.session.query(Order).filter(
            Order.id == order_id
        ).first()

    def find_all(self) -> List[Order]:
        return self.session.query(Order).all()

    def find_by_status(self, status: str) -> List[Order]:
        return self.session.query(Order).filter(
            Order.status == status
        ).all()

    def find_by_customer_id(self, customer_id: int) -> List[Order]:
        return self.session.query(Order).filter(
            Order.customer_id == customer_id
        ).all()

    def save(self, order: Order) -> Order:
        if order.id is None:
            self.session.add(order)
        self.session.flush()  # Get the generated ID
        return order

    def delete(self, order: Order) -> None:
        self.session.delete(order)
        self.session.flush()
```

### Step 4: Service Layer

```python
class OrderService:
    """Business logic that depends only on the repository interface."""

    def __init__(self, repository: AbstractOrderRepository):
        self.repository = repository

    def create_order(self, customer_id: int, total: float) -> Order:
        order = Order(customer_id=customer_id, total=total, status="PENDING")
        return self.repository.save(order)

    def confirm_order(self, order_id: int) -> Order:
        order = self.repository.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order not found: {order_id}")
        order.status = "CONFIRMED"
        return self.repository.save(order)

    def get_pending_orders(self) -> list:
        return self.repository.find_by_status("PENDING")

    def apply_discount(self, order_id: int, percent: float) -> Order:
        order = self.repository.find_by_id(order_id)
        if order is None:
            raise ValueError(f"Order not found: {order_id}")
        order.total = order.total * (1 - percent / 100)
        return self.repository.save(order)
```

### Step 5: Wire It Together

```python
# Setup database
engine = create_engine("sqlite:///orders.db", echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# Create session and repository
session = SessionLocal()
repository = SqlAlchemyOrderRepository(session)
service = OrderService(repository)

# Use the service
order1 = service.create_order(customer_id=100, total=250.00)
order2 = service.create_order(customer_id=100, total=75.50)
order3 = service.create_order(customer_id=200, total=500.00)

print(f"Created: {order1}")
print(f"Created: {order2}")
print(f"Created: {order3}")

# Confirm an order
confirmed = service.confirm_order(order1.id)
print(f"\nConfirmed: {confirmed}")

# Query pending orders
pending = service.get_pending_orders()
print(f"\nPending orders: {len(pending)}")
for o in pending:
    print(f"  {o}")

session.commit()
session.close()
```

**Output:**

```
Created: Order(id=1, customer_id=100, total=250.0, status='PENDING')
Created: Order(id=2, customer_id=100, total=75.5, status='PENDING')
Created: Order(id=3, customer_id=200, total=500.0, status='PENDING')

Confirmed: Order(id=1, customer_id=100, total=250.0, status='CONFIRMED')

Pending orders: 2
  Order(id=2, customer_id=100, total=75.5, status='PENDING')
  Order(id=3, customer_id=200, total=500.0, status='PENDING')
```

---

## In-Memory Repository for Testing

One of the biggest benefits of the Repository pattern is testability. You can create an in-memory implementation that requires no database at all.

### Java: In-Memory Repository

```java
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

public class InMemoryOrderRepository implements OrderRepository {

    private final Map<Long, Order> store = new HashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    @Override
    public Order findById(Long id) {
        return store.get(id);
    }

    @Override
    public List<Order> findAll() {
        return new ArrayList<>(store.values());
    }

    @Override
    public List<Order> findByStatus(String status) {
        return store.values().stream()
            .filter(o -> o.getStatus().equals(status))
            .collect(Collectors.toList());
    }

    @Override
    public Order save(Order order) {
        if (order.getId() == null) {
            order.setId(idGenerator.getAndIncrement());
        }
        store.put(order.getId(), order);
        return order;
    }

    @Override
    public void delete(Order order) {
        store.remove(order.getId());
    }

    // Helper for tests
    public void clear() {
        store.clear();
        idGenerator.set(1);
    }

    public int size() {
        return store.size();
    }
}
```

### Java: Unit Test Using In-Memory Repository

```java
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.math.BigDecimal;

class OrderServiceTest {

    private InMemoryOrderRepository repository;
    private OrderService service;

    @BeforeEach
    void setUp() {
        repository = new InMemoryOrderRepository();
        service = new OrderService(repository);
    }

    @Test
    void shouldCreateOrder() {
        Order order = service.createOrder(100L, new BigDecimal("250.00"));

        assertNotNull(order.getId());
        assertEquals("PENDING", order.getStatus());
        assertEquals(1, repository.size());
    }

    @Test
    void shouldConfirmOrder() {
        Order order = service.createOrder(100L, new BigDecimal("250.00"));
        Order confirmed = service.confirmOrder(order.getId());

        assertEquals("CONFIRMED", confirmed.getStatus());
    }

    @Test
    void shouldApplyDiscount() {
        Order order = service.createOrder(100L, new BigDecimal("100.00"));
        service.applyDiscount(order.getId(), 10.0);

        Order updated = repository.findById(order.getId());
        assertEquals(new BigDecimal("90.00"), updated.getTotal());
    }

    @Test
    void shouldThrowWhenOrderNotFound() {
        assertThrows(RuntimeException.class,
            () -> service.confirmOrder(999L));
    }
}
```

**Test Output:**

```
OrderServiceTest
  shouldCreateOrder           PASSED
  shouldConfirmOrder          PASSED
  shouldApplyDiscount         PASSED
  shouldThrowWhenOrderNotFound PASSED

4 tests passed, 0 failed
```

### Python: In-Memory Repository

```python
class InMemoryOrderRepository(AbstractOrderRepository):
    """In-memory repository for fast unit tests."""

    def __init__(self):
        self._store: dict[int, Order] = {}
        self._next_id = 1

    def find_by_id(self, order_id: int) -> Optional[Order]:
        return self._store.get(order_id)

    def find_all(self) -> List[Order]:
        return list(self._store.values())

    def find_by_status(self, status: str) -> List[Order]:
        return [o for o in self._store.values() if o.status == status]

    def find_by_customer_id(self, customer_id: int) -> List[Order]:
        return [o for o in self._store.values()
                if o.customer_id == customer_id]

    def save(self, order: Order) -> Order:
        if order.id is None:
            order.id = self._next_id
            self._next_id += 1
        self._store[order.id] = order
        return order

    def delete(self, order: Order) -> None:
        self._store.pop(order.id, None)

    def clear(self):
        self._store.clear()
        self._next_id = 1
```

### Python: Unit Test

```python
import pytest

class TestOrderService:

    def setup_method(self):
        self.repository = InMemoryOrderRepository()
        self.service = OrderService(self.repository)

    def test_create_order(self):
        order = self.service.create_order(customer_id=100, total=250.00)
        assert order.id is not None
        assert order.status == "PENDING"
        assert len(self.repository.find_all()) == 1

    def test_confirm_order(self):
        order = self.service.create_order(customer_id=100, total=250.00)
        confirmed = self.service.confirm_order(order.id)
        assert confirmed.status == "CONFIRMED"

    def test_apply_discount(self):
        order = self.service.create_order(customer_id=100, total=100.00)
        updated = self.service.apply_discount(order.id, 10.0)
        assert updated.total == 90.0

    def test_order_not_found(self):
        with pytest.raises(ValueError):
            self.service.confirm_order(999)
```

**Output:**

```
test_order_service.py
  test_create_order      PASSED
  test_confirm_order     PASSED
  test_apply_discount    PASSED
  test_order_not_found   PASSED

4 passed in 0.02s
```

---

## Repository vs DAO (Data Access Object)

These two patterns are often confused. Here is how they differ:

```
+-------------------+----------------------------------+----------------------------------+
|    Aspect         |       Repository                 |          DAO                     |
+-------------------+----------------------------------+----------------------------------+
| Abstraction Level | Domain-oriented (collection of   | Data-oriented (table-level       |
|                   | domain objects)                  | operations)                      |
+-------------------+----------------------------------+----------------------------------+
| Interface Style   | findByStatus("ACTIVE")           | executeQuery("SELECT ... WHERE") |
|                   | save(order)                      | insert(row)                      |
+-------------------+----------------------------------+----------------------------------+
| Return Type       | Domain entities                  | DTOs, Maps, or ResultSets        |
+-------------------+----------------------------------+----------------------------------+
| Awareness         | Knows nothing about SQL or       | May expose database-specific     |
|                   | database structure               | concepts                         |
+-------------------+----------------------------------+----------------------------------+
| Belongs To        | Domain layer                     | Infrastructure / persistence     |
|                   |                                  | layer                            |
+-------------------+----------------------------------+----------------------------------+
| Composability     | Can aggregate multiple data      | Usually maps 1:1 to a table      |
|                   | sources behind one interface     |                                  |
+-------------------+----------------------------------+----------------------------------+
```

### DAO Example (Data-Oriented)

```java
// DAO - exposes data access details
public class OrderDao {
    public ResultSet executeQuery(String sql) { ... }
    public void insert(String table, Map<String, Object> values) { ... }
    public void update(String table, Map<String, Object> values,
                       String whereClause) { ... }
}
```

### Repository Example (Domain-Oriented)

```java
// Repository - domain language, no SQL exposure
public interface OrderRepository {
    Order findById(Long id);
    List<Order> findActiveOrdersForCustomer(Long customerId);
    Order save(Order order);
}
```

**In practice**, the distinction has blurred. Spring Data's `JpaRepository` is called a repository but sometimes behaves like a DAO. The important thing is to keep your interface domain-focused rather than data-focused.

---

## Real-World Use Case: Clean Architecture Data Layer

In clean architecture, the Repository pattern forms the boundary between the domain layer and the infrastructure layer.

```
+------------------------------------------------------------------+
|                        Presentation Layer                         |
|                    (Controllers, REST APIs)                       |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                        Application Layer                         |
|                     (Use Cases / Services)                       |
|                                                                  |
|   OrderService uses OrderRepository (interface)                  |
+------------------------------------------------------------------+
                              |
                              | depends on interface only
                              v
+------------------------------------------------------------------+
|                         Domain Layer                             |
|                  (Entities, Repository Interfaces)               |
|                                                                  |
|   interface OrderRepository { findById(), save(), ... }          |
+------------------------------------------------------------------+
                              ^
                              | implements
                              |
+------------------------------------------------------------------+
|                      Infrastructure Layer                        |
|              (Database, ORM, External Services)                  |
|                                                                  |
|   JpaOrderRepository implements OrderRepository                 |
|   MongoOrderRepository implements OrderRepository               |
+------------------------------------------------------------------+
```

### Generic Repository Base Class

For larger projects, create a generic repository to avoid repeating common operations:

**Java:**

```java
public interface GenericRepository<T, ID> {
    Optional<T> findById(ID id);
    List<T> findAll();
    T save(T entity);
    void delete(T entity);
    long count();
    boolean existsById(ID id);
}

// Specific repository adds domain methods
public interface ProductRepository extends GenericRepository<Product, Long> {
    List<Product> findByCategory(String category);
    List<Product> findByPriceRange(BigDecimal min, BigDecimal max);
    List<Product> findInStock();
}
```

**Python:**

```python
from typing import TypeVar, Generic, List, Optional

T = TypeVar("T")
ID = TypeVar("ID")

class GenericRepository(ABC, Generic[T, ID]):
    """Base repository with common CRUD operations."""

    @abstractmethod
    def find_by_id(self, entity_id: ID) -> Optional[T]:
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class ProductRepository(GenericRepository[Product, int]):
    """Product-specific repository with domain methods."""

    @abstractmethod
    def find_by_category(self, category: str) -> List[Product]:
        pass

    @abstractmethod
    def find_by_price_range(self, min_price: float,
                            max_price: float) -> List[Product]:
        pass

    @abstractmethod
    def find_in_stock(self) -> List[Product]:
        pass
```

---

## When to Use / When NOT to Use

### Use the Repository Pattern When

- You want to isolate business logic from data access details
- You need to support multiple data stores (SQL, NoSQL, APIs)
- You want fast, database-free unit tests
- Your domain model is complex and does not map one-to-one to tables
- You are following clean architecture or hexagonal architecture
- Your team works on different layers independently

### Do NOT Use the Repository Pattern When

- Your application is a simple CRUD with no business logic
- You are building a quick prototype or proof of concept
- The framework already provides sufficient abstraction (simple Django views)
- Adding a repository layer would just be a pass-through with no value
- Your application has only one data source and will never change

---

## Common Mistakes

1. **Leaking persistence details through the interface.** Repository methods should use domain language, not SQL or ORM concepts. Avoid methods like `executeQuery()` or `flush()` on the interface.

2. **Creating repositories that are too generic.** A repository with only `save()` and `findById()` is too thin. Add domain-specific finder methods that express business concepts.

3. **Putting business logic in the repository.** The repository should only handle data access. Calculations, validations, and rules belong in the service or domain layer.

4. **Not using the interface for dependency injection.** If your service class depends on `JpaOrderRepository` instead of `OrderRepository`, you lose the ability to swap implementations.

5. **One repository per table instead of per aggregate.** In domain-driven design, repositories should correspond to aggregate roots, not individual tables. An `OrderRepository` might internally manage `Order` and `OrderItem` together.

---

## Best Practices

1. **Name repository methods using domain language.** Use `findActiveCustomers()` rather than `findByStatusEquals("ACTIVE")`.

2. **Return domain objects, not database rows.** The repository translates between the persistence format and domain entities.

3. **Keep the repository interface in the domain layer.** The implementation lives in the infrastructure layer. This ensures the domain never depends on infrastructure.

4. **Create in-memory implementations for testing.** This makes your tests fast and independent of any database.

5. **Use the Specification pattern for complex queries.** Instead of adding a new method for every query combination, pass specification objects that describe the criteria.

6. **Limit the number of methods.** A repository with 30 methods is a sign that you need to rethink your design. Focus on the queries your domain actually needs.

---

## Quick Summary

The Repository pattern provides a collection-like interface for accessing domain entities. It hides all persistence details behind a clean abstraction, allowing your business logic to remain independent of the data store. In Java, Spring Data JPA generates repository implementations automatically. In Python, you define an abstract base class and implement it with SQLAlchemy. The pattern enables fast testing through in-memory implementations and supports clean architecture by keeping the domain layer free from infrastructure concerns.

---

## Key Points

- The Repository pattern abstracts data access behind a collection-like interface
- Business logic depends on the repository interface, not the implementation
- Spring Data JPA generates repository implementations from interface definitions
- In Python, define an abstract repository class and implement it with SQLAlchemy
- In-memory repositories enable fast, database-free unit tests
- Repository is domain-oriented; DAO is data-oriented
- Repository interfaces belong in the domain layer; implementations in infrastructure
- Generic repositories reduce boilerplate for common CRUD operations
- Methods should use domain language, not database terminology

---

## Practice Questions

1. What is the main difference between a Repository and a DAO? In what situations would you choose one over the other?

2. Why is it important that the service layer depends on the repository interface rather than a concrete implementation? What design principle does this follow?

3. You have an `Order` entity that contains a list of `OrderItem` entities. Should you create separate repositories for `Order` and `OrderItem`, or a single `OrderRepository` that manages both? Explain your reasoning.

4. How does Spring Data JPA derive SQL queries from method names like `findByStatusAndCustomerId`? What happens when the method name becomes too complex?

5. A teammate argues that the Repository pattern adds unnecessary complexity to a simple CRUD application. How would you respond?

---

## Exercises

### Exercise 1: Build a User Repository

Create a `UserRepository` interface with methods: `findById`, `findByEmail`, `findActiveUsers`, `save`, and `delete`. Implement both a SQLAlchemy version and an in-memory version in Python. Write unit tests using the in-memory version to verify that all operations work correctly.

### Exercise 2: Generic Repository in Java

Create a generic `CrudRepository<T, ID>` interface with basic CRUD operations. Then create a `ProductRepository` that extends it with methods like `findByCategory(String category)` and `findByPriceBelow(BigDecimal price)`. Implement an in-memory version and write tests.

### Exercise 3: Repository with Specification Pattern

Extend your repository to support dynamic queries using a Specification pattern. Create a `Specification<T>` interface with a `boolean isSatisfiedBy(T entity)` method. Add a `findAll(Specification<T> spec)` method to your repository. Build specifications like `OrderAboveTotal`, `OrderByCustomer`, and `PendingOrders`. Demonstrate how specifications can be combined with AND/OR logic.

---

## What Is Next?

Now that you understand how the Repository pattern isolates data access behind a clean interface, the next chapter explores the **Unit of Work** pattern. While the repository handles individual entity operations, the Unit of Work tracks all changes made during a business transaction and commits them as a single atomic operation. Together, these two patterns form the foundation of a robust data access layer.
