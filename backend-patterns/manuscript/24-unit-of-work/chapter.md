# Chapter 24: Unit of Work Pattern

## What You Will Learn

- What the Unit of Work pattern is and what problem it solves
- How to track changes to multiple entities and commit them as one transaction
- How JPA EntityManager and Hibernate Session act as a Unit of Work in Java
- How SQLAlchemy Session implements the Unit of Work pattern in Python
- How to handle partial commits and ensure transactional consistency
- How to apply Unit of Work in batch operations and real-world scenarios

## Why This Chapter Matters

In any non-trivial backend system, a single business operation often touches multiple entities. When a customer places an order, you need to create the order record, update inventory, record a payment, and send a confirmation. If the payment step fails after inventory has already been deducted, your data is inconsistent. The customer sees a charge but no order, or worse, inventory disappears without a sale.

The Unit of Work pattern solves this by keeping track of every change you make during a business operation and committing them all at once as a single transaction. If anything fails, everything rolls back. Nothing is saved halfway.

This is not a niche pattern. Every ORM you use -- JPA, Hibernate, SQLAlchemy, Entity Framework -- implements it under the hood. Understanding how it works helps you use these tools correctly and avoid subtle bugs that appear only in production.

---

## The Problem

Imagine processing an order that involves multiple database operations:

### Before: Multiple Independent Saves

**Java:**

```java
public class OrderProcessor {

    private final OrderRepository orderRepository;
    private final InventoryRepository inventoryRepository;
    private final PaymentRepository paymentRepository;

    public void processOrder(OrderRequest request) {
        // Save the order
        Order order = new Order(request.getCustomerId(), request.getTotal());
        orderRepository.save(order);  // COMMIT 1

        // Deduct inventory
        for (OrderItem item : request.getItems()) {
            Inventory inv = inventoryRepository.findByProductId(
                item.getProductId());
            inv.setQuantity(inv.getQuantity() - item.getQuantity());
            inventoryRepository.save(inv);  // COMMIT 2, 3, 4...
        }

        // Record payment -- THIS FAILS!
        Payment payment = new Payment(order.getId(), request.getTotal());
        paymentRepository.save(payment);  // THROWS EXCEPTION

        // Problem: Order is saved, inventory is deducted,
        // but payment failed. Data is now inconsistent!
    }
}
```

**Python:**

```python
class OrderProcessor:
    def process_order(self, request):
        # Save the order
        order = Order(customer_id=request.customer_id, total=request.total)
        db.session.add(order)
        db.session.commit()  # COMMIT 1

        # Deduct inventory
        for item in request.items:
            inv = Inventory.query.filter_by(
                product_id=item.product_id).first()
            inv.quantity -= item.quantity
            db.session.commit()  # COMMIT 2, 3, 4...

        # Record payment -- THIS FAILS!
        payment = Payment(order_id=order.id, amount=request.total)
        db.session.add(payment)
        db.session.commit()  # THROWS EXCEPTION

        # Order and inventory changes are already committed.
        # Cannot undo them!
```

```
Timeline of failure:

  COMMIT 1      COMMIT 2      COMMIT 3       BOOM!
  Save Order    Update Inv    Update Inv     Payment fails
     |              |             |              |
     v              v             v              v
  [Saved]       [Saved]       [Saved]       [Exception]

  Result: Order exists, inventory is wrong, no payment
          Data is INCONSISTENT
```

---

## The Solution: Unit of Work Pattern

The Unit of Work pattern tracks all changes made during a business operation and commits them as a single atomic transaction.

```
+--------------------------------------------------------------+
|                      Unit of Work                            |
|                                                              |
|   +-- New Objects ----+  +-- Dirty Objects --+  +-- Deleted -+
|   | Order #1          |  | Inventory A       |  |            |
|   | Payment #1        |  | Inventory B       |  |            |
|   +-------------------+  +-------------------+  +------------+
|                                                              |
|   commit() --> BEGIN TRANSACTION                             |
|                INSERT order                                  |
|                UPDATE inventory_a                            |
|                UPDATE inventory_b                            |
|                INSERT payment                                |
|                COMMIT   (all or nothing)                     |
|                                                              |
|   rollback() --> ROLLBACK  (undo everything)                 |
+--------------------------------------------------------------+
```

### After: Single Transaction with Unit of Work

**Java (with JPA/Spring):**

```java
@Service
public class OrderProcessor {

    private final OrderRepository orderRepository;
    private final InventoryRepository inventoryRepository;
    private final PaymentRepository paymentRepository;

    @Transactional  // <-- This makes the entire method one Unit of Work
    public void processOrder(OrderRequest request) {
        // Create the order
        Order order = new Order(request.getCustomerId(), request.getTotal());
        orderRepository.save(order);

        // Deduct inventory
        for (OrderItem item : request.getItems()) {
            Inventory inv = inventoryRepository.findByProductId(
                item.getProductId());
            inv.setQuantity(inv.getQuantity() - item.getQuantity());
            inventoryRepository.save(inv);
        }

        // Record payment
        Payment payment = new Payment(order.getId(), request.getTotal());
        paymentRepository.save(payment);

        // If ANY step fails, ALL changes are rolled back automatically
    }
}
```

**Python (with SQLAlchemy):**

```python
class OrderProcessor:
    def __init__(self, session):
        self.session = session  # SQLAlchemy Session IS the Unit of Work

    def process_order(self, request):
        try:
            # Create the order
            order = Order(customer_id=request.customer_id,
                          total=request.total)
            self.session.add(order)

            # Deduct inventory
            for item in request.items:
                inv = self.session.query(Inventory).filter_by(
                    product_id=item.product_id).first()
                inv.quantity -= item.quantity

            # Record payment
            payment = Payment(order_id=order.id, amount=request.total)
            self.session.add(payment)

            # Commit everything as ONE transaction
            self.session.commit()

        except Exception:
            # If anything fails, undo ALL changes
            self.session.rollback()
            raise
```

```
Timeline with Unit of Work:

  Track        Track         Track        COMMIT ALL
  Order        Inventory     Payment      or ROLLBACK
    |              |             |             |
    v              v             v             v
  [Pending]    [Pending]    [Pending]    [All Saved]
                                         or
                                        [All Reverted]

  Result: Data is ALWAYS consistent
```

---

## How the Unit of Work Pattern Works

The Unit of Work maintains three internal lists:

```
+----------------------------------------------------------+
|                    Unit of Work                          |
|                                                          |
|  1. NEW objects     -- entities to be INSERTed           |
|     [Order #1, Payment #1]                               |
|                                                          |
|  2. DIRTY objects   -- entities to be UPDATEd            |
|     [Inventory A (qty: 100 -> 95)]                       |
|     [Inventory B (qty: 50 -> 48)]                        |
|                                                          |
|  3. REMOVED objects -- entities to be DELETEd            |
|     [OldPromotion #7]                                    |
|                                                          |
|  commit():                                               |
|     BEGIN TRANSACTION                                    |
|     for each new    -> INSERT INTO ...                   |
|     for each dirty  -> UPDATE ... SET ...                |
|     for each removed -> DELETE FROM ...                  |
|     COMMIT                                               |
|                                                          |
|  rollback():                                             |
|     Discard all tracked changes                          |
|     Reset to clean state                                 |
+----------------------------------------------------------+
```

---

## Java: JPA EntityManager as Unit of Work

The JPA `EntityManager` (and Hibernate `Session`) already implements the Unit of Work pattern. Understanding this helps you use it correctly.

### How EntityManager Tracks Changes

```java
import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityManagerFactory;
import jakarta.persistence.Persistence;

public class JpaUnitOfWorkDemo {

    public static void main(String[] args) {
        EntityManagerFactory emf = Persistence.createEntityManagerFactory(
            "demo-unit");
        EntityManager em = emf.createEntityManager();

        // Begin the unit of work
        em.getTransaction().begin();

        // 1. NEW: Create a new entity (tracked as "new")
        Order order = new Order(100L, new BigDecimal("250.00"), "PENDING");
        em.persist(order);
        System.out.println("Order persisted (not yet in DB)");

        // 2. DIRTY: Modify an existing entity (tracked as "dirty")
        Product product = em.find(Product.class, 1L);
        product.setStock(product.getStock() - 5);
        // No explicit save needed! EntityManager detects the change
        System.out.println("Product stock modified (tracked automatically)");

        // 3. REMOVED: Delete an entity (tracked as "removed")
        Coupon expiredCoupon = em.find(Coupon.class, 42L);
        em.remove(expiredCoupon);
        System.out.println("Coupon marked for removal");

        // Commit: All three operations happen in ONE transaction
        em.getTransaction().commit();
        System.out.println("All changes committed as one transaction");

        em.close();
        emf.close();
    }
}
```

**Output:**

```
Order persisted (not yet in DB)
Product stock modified (tracked automatically)
Coupon marked for removal
All changes committed as one transaction
```

### Spring @Transactional as Unit of Work Boundary

In Spring, the `@Transactional` annotation defines the boundary of a Unit of Work:

```java
@Service
public class TransferService {

    private final AccountRepository accountRepository;
    private final TransferLogRepository transferLogRepository;

    public TransferService(AccountRepository accountRepository,
                           TransferLogRepository transferLogRepository) {
        this.accountRepository = accountRepository;
        this.transferLogRepository = transferLogRepository;
    }

    @Transactional
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        // Load accounts (they become "managed" by the EntityManager)
        Account from = accountRepository.findById(fromId)
            .orElseThrow(() -> new RuntimeException("Source not found"));
        Account to = accountRepository.findById(toId)
            .orElseThrow(() -> new RuntimeException("Target not found"));

        // Validate
        if (from.getBalance().compareTo(amount) < 0) {
            throw new InsufficientFundsException("Not enough balance");
        }

        // Modify entities (EntityManager tracks these changes)
        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));

        // Log the transfer
        TransferLog log = new TransferLog(fromId, toId, amount);
        transferLogRepository.save(log);

        // When this method exits normally, Spring commits the transaction
        // If an exception is thrown, Spring rolls back everything
    }
}
```

```
@Transactional method execution:

  Method starts
      |
      v
  Spring creates EntityManager + begins transaction
      |
      v
  Your code runs (find, modify, save entities)
      |
      v
  Method returns normally?
      |          |
     YES         NO (exception thrown)
      |          |
      v          v
   COMMIT     ROLLBACK
  (all saved) (nothing saved)
```

---

## Python: SQLAlchemy Session as Unit of Work

SQLAlchemy's `Session` is an explicit implementation of the Unit of Work pattern.

### Basic Session Usage

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    owner = Column(String(100), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"Account(id={self.id}, owner='{self.owner}', balance={self.balance})"


class TransferLog(Base):
    __tablename__ = "transfer_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_id = Column(Integer, nullable=False)
    to_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)


# Setup
engine = create_engine("sqlite:///bank.db")
Base.metadata.create_all(engine)
SessionFactory = sessionmaker(bind=engine)
```

### Tracking Changes

```python
def demonstrate_unit_of_work():
    session = SessionFactory()

    try:
        # 1. NEW: Add new entities
        alice = Account(id=1, owner="Alice", balance=1000.0)
        bob = Account(id=2, owner="Bob", balance=500.0)
        session.add(alice)
        session.add(bob)
        print(f"New objects: {session.new}")
        # Output: New objects: IdentitySet([Account(...), Account(...)])

        session.commit()
        print("Initial accounts committed")

        # 2. DIRTY: Modify existing entities
        alice = session.query(Account).get(1)
        alice.balance -= 200.0
        bob = session.query(Account).get(2)
        bob.balance += 200.0
        print(f"Dirty objects: {session.dirty}")
        # Output: Dirty objects: IdentitySet([Account(...), Account(...)])

        # 3. NEW: Log the transfer
        log = TransferLog(from_id=1, to_id=2, amount=200.0)
        session.add(log)

        # Commit all changes as one transaction
        session.commit()
        print("Transfer committed successfully")

        # Verify
        alice = session.query(Account).get(1)
        bob = session.query(Account).get(2)
        print(f"Alice: {alice.balance}")  # 800.0
        print(f"Bob: {bob.balance}")      # 700.0

    except Exception as e:
        session.rollback()
        print(f"Rolled back: {e}")
    finally:
        session.close()

demonstrate_unit_of_work()
```

**Output:**

```
New objects: IdentitySet([Account(id=1, owner='Alice', balance=1000.0), Account(id=2, owner='Bob', balance=500.0)])
Initial accounts committed
Dirty objects: IdentitySet([Account(id=1, owner='Alice', balance=800.0), Account(id=2, owner='Bob', balance=700.0)])
Transfer committed successfully
Alice: 800.0
Bob: 700.0
```

### Context Manager Pattern

```python
from contextlib import contextmanager

@contextmanager
def unit_of_work():
    """Context manager that provides a transactional scope."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Usage
def transfer_money(from_id: int, to_id: int, amount: float):
    with unit_of_work() as session:
        source = session.query(Account).get(from_id)
        target = session.query(Account).get(to_id)

        if source.balance < amount:
            raise ValueError("Insufficient funds")

        source.balance -= amount
        target.balance += amount

        log = TransferLog(from_id=from_id, to_id=to_id, amount=amount)
        session.add(log)

        # commit happens automatically when the with block exits
        # rollback happens automatically if an exception is raised
```

---

## Building a Custom Unit of Work

Understanding the internals helps you appreciate what ORMs do for you. Here is a simplified custom implementation.

### Python: Custom Unit of Work

```python
class UnitOfWork:
    """Tracks changes and commits them as a single transaction."""

    def __init__(self, connection):
        self.connection = connection
        self._new = []       # Entities to INSERT
        self._dirty = []     # Entities to UPDATE
        self._removed = []   # Entities to DELETE

    def register_new(self, entity):
        """Mark an entity for insertion."""
        if entity not in self._new:
            self._new.append(entity)
            print(f"  Registered NEW: {entity}")

    def register_dirty(self, entity):
        """Mark an entity for update."""
        if entity not in self._dirty and entity not in self._new:
            self._dirty.append(entity)
            print(f"  Registered DIRTY: {entity}")

    def register_removed(self, entity):
        """Mark an entity for deletion."""
        if entity in self._new:
            self._new.remove(entity)
        else:
            if entity not in self._removed:
                self._removed.append(entity)
                print(f"  Registered REMOVED: {entity}")

    def commit(self):
        """Persist all tracked changes in one transaction."""
        cursor = self.connection.cursor()
        try:
            # Process inserts
            for entity in self._new:
                sql, params = entity.to_insert_sql()
                cursor.execute(sql, params)
                print(f"  INSERT: {entity}")

            # Process updates
            for entity in self._dirty:
                sql, params = entity.to_update_sql()
                cursor.execute(sql, params)
                print(f"  UPDATE: {entity}")

            # Process deletes
            for entity in self._removed:
                sql, params = entity.to_delete_sql()
                cursor.execute(sql, params)
                print(f"  DELETE: {entity}")

            self.connection.commit()
            print("  COMMITTED all changes")

        except Exception as e:
            self.connection.rollback()
            print(f"  ROLLED BACK: {e}")
            raise
        finally:
            self._new.clear()
            self._dirty.clear()
            self._removed.clear()

    def rollback(self):
        """Discard all tracked changes."""
        self._new.clear()
        self._dirty.clear()
        self._removed.clear()
        self.connection.rollback()
        print("  ROLLED BACK all pending changes")
```

### Using the Custom Unit of Work

```python
import sqlite3

# Simple entity class
class Product:
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def to_insert_sql(self):
        return (
            "INSERT INTO products (id, name, price, stock) VALUES (?,?,?,?)",
            (self.id, self.name, self.price, self.stock)
        )

    def to_update_sql(self):
        return (
            "UPDATE products SET name=?, price=?, stock=? WHERE id=?",
            (self.name, self.price, self.stock, self.id)
        )

    def to_delete_sql(self):
        return ("DELETE FROM products WHERE id=?", (self.id,))

    def __repr__(self):
        return f"Product(id={self.id}, name='{self.name}', stock={self.stock})"


# Demo
conn = sqlite3.connect(":memory:")
conn.execute("""CREATE TABLE products (
    id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER
)""")

uow = UnitOfWork(conn)

# Register changes
laptop = Product(1, "Laptop", 999.99, 50)
mouse = Product(2, "Mouse", 29.99, 200)

uow.register_new(laptop)
uow.register_new(mouse)

# Simulate a stock update
laptop.stock = 45
uow.register_dirty(laptop)

# Commit everything
print("\nCommitting:")
uow.commit()
```

**Output:**

```
  Registered NEW: Product(id=1, name='Laptop', stock=50)
  Registered NEW: Product(id=2, name='Mouse', stock=200)
  Registered DIRTY: Product(id=1, name='Laptop', stock=45)

Committing:
  INSERT: Product(id=1, name='Laptop', stock=50)
  INSERT: Product(id=2, name='Mouse', stock=200)
  UPDATE: Product(id=1, name='Laptop', stock=45)
  COMMITTED all changes
```

---

## Real-World Use Case: Batch Operations

The Unit of Work pattern shines in batch processing where you need to process many records efficiently.

### Java: Batch Import with Unit of Work

```java
@Service
public class ProductImportService {

    private final EntityManager entityManager;

    @Transactional
    public ImportResult importProducts(List<ProductCsvRow> rows) {
        int created = 0;
        int updated = 0;
        int batchSize = 50;

        for (int i = 0; i < rows.size(); i++) {
            ProductCsvRow row = rows.get(i);

            Product existing = entityManager
                .createQuery("SELECT p FROM Product p WHERE p.sku = :sku",
                             Product.class)
                .setParameter("sku", row.getSku())
                .getResultStream()
                .findFirst()
                .orElse(null);

            if (existing != null) {
                // Dirty tracking: EntityManager detects these changes
                existing.setName(row.getName());
                existing.setPrice(row.getPrice());
                existing.setStock(row.getStock());
                updated++;
            } else {
                // New entity
                Product product = new Product(
                    row.getSku(), row.getName(),
                    row.getPrice(), row.getStock());
                entityManager.persist(product);
                created++;
            }

            // Flush and clear periodically to avoid memory issues
            if (i % batchSize == 0 && i > 0) {
                entityManager.flush();
                entityManager.clear();
                System.out.println("Flushed batch at index " + i);
            }
        }

        // Final commit happens when @Transactional method exits
        return new ImportResult(created, updated);
    }
}
```

### Python: Batch Processing with Session

```python
def import_products(csv_rows: list, batch_size: int = 50):
    """Import products in batches using Unit of Work."""
    with unit_of_work() as session:
        created = 0
        updated = 0

        for i, row in enumerate(csv_rows):
            existing = session.query(Product).filter_by(
                sku=row["sku"]
            ).first()

            if existing:
                existing.name = row["name"]
                existing.price = row["price"]
                existing.stock = row["stock"]
                updated += 1
            else:
                product = Product(
                    sku=row["sku"],
                    name=row["name"],
                    price=row["price"],
                    stock=row["stock"]
                )
                session.add(product)
                created += 1

            # Flush periodically for memory efficiency
            if i % batch_size == 0 and i > 0:
                session.flush()
                print(f"Flushed batch at index {i}")

        # Commit happens automatically via context manager
        print(f"Import complete: {created} created, {updated} updated")

# Usage
csv_data = [
    {"sku": "LAP001", "name": "Laptop Pro", "price": 1299.99, "stock": 30},
    {"sku": "MOU001", "name": "Wireless Mouse", "price": 49.99, "stock": 150},
    {"sku": "KEY001", "name": "Mech Keyboard", "price": 129.99, "stock": 75},
]
import_products(csv_data)
```

**Output:**

```
Import complete: 3 created, 0 updated
```

---

## Unit of Work with Repository Pattern

The Unit of Work and Repository patterns work together naturally. The repository handles entity retrieval and registration, while the Unit of Work manages the transaction.

```
+---------------------------------------------------+
|                   Service Layer                   |
|                                                   |
|   orderService.processOrder(request)              |
+---------------------------------------------------+
          |                    |
          v                    v
+------------------+  +------------------+
| OrderRepository  |  | InventoryRepo    |
| .save(order)     |  | .findById(id)    |
| .findById(id)    |  | .save(inv)       |
+------------------+  +------------------+
          |                    |
          +-------- + ---------+
                    |
                    v
          +------------------+
          |  Unit of Work    |
          |  (Session /      |
          |   EntityManager) |
          |                  |
          |  commit()        |
          |  rollback()      |
          +------------------+
                    |
                    v
          +------------------+
          |    Database      |
          +------------------+
```

### Python: Repositories Sharing a Unit of Work

```python
class SqlAlchemyUnitOfWork:
    """Unit of Work that provides repositories sharing the same session."""

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None
        self.orders = None
        self.products = None
        self.payments = None

    def __enter__(self):
        self.session = self.session_factory()
        self.orders = SqlAlchemyOrderRepository(self.session)
        self.products = SqlAlchemyProductRepository(self.session)
        self.payments = SqlAlchemyPaymentRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()


# Usage in service
class CheckoutService:
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    def checkout(self, cart):
        with self.uow_factory() as uow:
            # Create order
            order = Order(customer_id=cart.customer_id,
                          total=cart.total)
            uow.orders.save(order)

            # Update inventory
            for item in cart.items:
                product = uow.products.find_by_id(item.product_id)
                product.stock -= item.quantity
                uow.products.save(product)

            # Record payment
            payment = Payment(order_id=order.id, amount=cart.total)
            uow.payments.save(payment)

            # One commit for everything
            uow.commit()

            return order
```

---

## When to Use / When NOT to Use

### Use the Unit of Work Pattern When

- A business operation modifies multiple entities that must be consistent
- You need transactional guarantees across multiple repository calls
- You are doing batch imports or updates
- You want to minimize database round-trips by batching changes
- You are building a clean architecture with explicit transaction boundaries

### Do NOT Use the Unit of Work Pattern When

- Each operation is independent and does not need to be atomic
- You are working with a single entity at a time (simple CRUD)
- Your data store does not support transactions (some NoSQL databases)
- You are building a read-only application (queries only)
- The overhead of tracking changes is not justified by the complexity

---

## Common Mistakes

1. **Committing too early.** Calling `commit()` or `flush()` in the middle of a business operation defeats the purpose. Wait until the entire operation is complete.

2. **Forgetting to rollback on failure.** If you catch an exception but do not rollback, the session may be in an inconsistent state. Always rollback in your error handler.

3. **Long-running Units of Work.** Keeping a transaction open for minutes or hours locks database rows and hurts concurrency. Keep your Unit of Work short and focused.

4. **Mixing auto-commit with Unit of Work.** If your database connection is in auto-commit mode, every statement is its own transaction. Make sure auto-commit is off when using Unit of Work.

5. **Not flushing in batch operations.** When processing thousands of entities, the Unit of Work accumulates all changes in memory. Flush periodically and clear the session to avoid out-of-memory errors.

---

## Best Practices

1. **Use framework-provided Unit of Work.** Do not build your own unless you have a specific reason. JPA EntityManager, Hibernate Session, and SQLAlchemy Session are battle-tested implementations.

2. **Define clear transaction boundaries.** In Spring, use `@Transactional` on service methods. In Python, use context managers. The service layer is the right place for transaction boundaries.

3. **Keep transactions short.** Do all your non-database work (validation, calculation) before starting the Unit of Work. Only include database operations inside the transaction.

4. **Pair with the Repository pattern.** Let repositories handle data access and the Unit of Work handle transaction management. This gives you clean separation of concerns.

5. **Flush in batches during bulk operations.** For large imports, flush every 50-100 entities and clear the session to keep memory usage constant.

6. **Handle nested transactions carefully.** In Spring, understand the propagation settings (`REQUIRED`, `REQUIRES_NEW`, etc.). In SQLAlchemy, use savepoints for nested transactions.

---

## Quick Summary

The Unit of Work pattern tracks all changes made to entities during a business operation and commits them as a single database transaction. This ensures data consistency -- either all changes are saved or none are. In Java, the JPA EntityManager and Spring's `@Transactional` annotation provide built-in Unit of Work behavior. In Python, SQLAlchemy's Session tracks new, dirty, and removed objects and commits them together. The pattern is essential for any operation that touches multiple entities and must remain atomic.

---

## Key Points

- Unit of Work tracks new, modified, and deleted entities during a business operation
- All tracked changes are committed as a single database transaction
- If any part fails, all changes are rolled back to maintain consistency
- JPA EntityManager and Hibernate Session are built-in Java implementations
- SQLAlchemy Session is the standard Python implementation
- Spring's @Transactional annotation defines the Unit of Work boundary
- Batch operations should flush periodically to manage memory
- Unit of Work pairs naturally with the Repository pattern
- Keep transactions short to avoid locking issues

---

## Practice Questions

1. What three types of changes does a Unit of Work track? How does each type map to a SQL operation?

2. In a Spring application, what happens when an exception is thrown inside a method annotated with `@Transactional`? What if the exception is a checked exception versus an unchecked exception?

3. Explain the difference between `flush()` and `commit()` in the context of JPA and SQLAlchemy. When would you use `flush()` without committing?

4. You are importing 100,000 products from a CSV file. Without any optimizations, what problem would you encounter with the Unit of Work pattern? How would you solve it?

5. Why is it important that repositories sharing the same Unit of Work use the same database session? What would happen if they used different sessions?

---

## Exercises

### Exercise 1: Bank Transfer System

Build a bank transfer system in Python with `Account` and `TransferLog` entities. Create a `transfer()` function that deducts from one account and adds to another, logging the transfer. Use SQLAlchemy's Session as the Unit of Work. Write tests that verify: (a) successful transfers update both accounts and create a log, (b) transfers with insufficient funds roll back completely.

### Exercise 2: Batch Order Processor

Create a Java service that processes a list of orders in a single transaction. Each order should: create an Order entity, deduct inventory for each item, and record a payment. Use `@Transactional` and flush every 20 orders. Write a test that processes 100 orders and verify they all commit together.

### Exercise 3: Custom Unit of Work

Build a custom Unit of Work class in Python (without SQLAlchemy) that tracks new, dirty, and removed objects. Implement `register_new()`, `register_dirty()`, `register_removed()`, `commit()`, and `rollback()` methods. Use it with a simple in-memory data store and write tests demonstrating atomic commits and rollbacks.

---

## What Is Next?

You now understand how the Repository pattern provides a clean data access interface and how the Unit of Work pattern ensures transactional consistency. The next chapter introduces **CQRS (Command Query Responsibility Segregation)**, a pattern that takes data access to the next level by using separate models for reading and writing data. This separation allows you to optimize reads and writes independently, which is critical for high-traffic backend systems.
