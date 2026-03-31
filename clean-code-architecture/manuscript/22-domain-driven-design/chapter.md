# Chapter 22: Domain-Driven Design

## What You Will Learn

- What Domain-Driven Design (DDD) is and why it focuses on the business domain
- How Ubiquitous Language bridges the gap between developers and business experts
- The difference between Entities (identity matters) and Value Objects (value matters)
- How Aggregates enforce consistency boundaries
- What Domain Events are and how they decouple parts of your system
- The role of Repositories and Domain Services
- Why a Rich Domain Model beats an Anemic Model

## Why This Chapter Matters

Most software projects fail not because of technical problems, but because the software does not accurately model the business it serves. Developers build what they think the business needs. Business people describe what they think they want. The result is a system that satisfies nobody.

Domain-Driven Design attacks this problem head-on. It says: **the most important thing in your software is the model of your business domain, and that model should be built collaboratively by developers and domain experts using the same language.**

If you have ever been in a meeting where the business team says "policy" and the development team codes it as "rule," or where "customer" means one thing in billing and another thing in shipping, you have experienced the exact problem DDD solves.

DDD is not a framework or a library. It is a way of thinking about software that puts the business domain at the center of every design decision.

---

## Ubiquitous Language: Speak the Same Words

The foundation of DDD is Ubiquitous Language -- a shared vocabulary that developers and business experts use consistently in conversations, documentation, and code.

```
WITHOUT UBIQUITOUS LANGUAGE:

  Business says:      Developer codes:
  +-----------+       +-------------+
  | "Policy"  | ----> | Rule.java   |
  | "Claim"   | ----> | Request.java|
  | "Holder"  | ----> | User.java   |
  | "Premium" | ----> | Payment.java|
  +-----------+       +-------------+

  Result: Constant translation errors, misunderstandings,
          bugs born from miscommunication.

WITH UBIQUITOUS LANGUAGE:

  Business says:      Developer codes:
  +-----------+       +---------------+
  | "Policy"  | ----> | Policy.java   |
  | "Claim"   | ----> | Claim.java    |
  | "Holder"  | ----> | Holder.java   |
  | "Premium" | ----> | Premium.java  |
  +-----------+       +---------------+

  Result: Code reads like the business speaks.
          Fewer misunderstandings. Faster onboarding.
```

### Rules for Ubiquitous Language

1. **Use the business terms in your code.** If the business calls it a "shipment," do not call it a "delivery" or "package" in code.
2. **Challenge vague terms.** If someone says "process the order," ask what "process" means. It might mean "validate," "charge payment," and "schedule fulfillment" -- three distinct operations.
3. **Update the language as understanding evolves.** When the team discovers a better term, rename it everywhere: code, tests, documentation, conversations.
4. **Write a glossary.** Maintain a shared document that defines each term. Review it regularly.

---

## Entities: Identity Matters

An Entity is a domain object with a unique identity that persists over time. Two entities are the same if they have the same identity, even if all other attributes differ.

**The key question: "Are these two objects the same thing if they have the same ID, even if their attributes changed?"** If yes, it is an Entity.

### Java Example

```java
// ENTITY: Two patients with the same patient ID are the same patient,
// even if their name or address changes.

public class Patient {
    private final PatientId id;       // Identity -- never changes
    private String name;               // Can change
    private String address;            // Can change
    private List<Diagnosis> diagnoses; // Can change

    public Patient(PatientId id, String name) {
        this.id = id;
        this.name = name;
        this.diagnoses = new ArrayList<>();
    }

    public void addDiagnosis(Diagnosis diagnosis) {
        // Business rule: cannot have duplicate active diagnoses
        boolean alreadyActive = diagnoses.stream()
            .anyMatch(d -> d.getCode().equals(diagnosis.getCode())
                        && d.isActive());
        if (alreadyActive) {
            throw new IllegalStateException(
                "Patient already has active diagnosis: " + diagnosis.getCode()
            );
        }
        diagnoses.add(diagnosis);
    }

    public void updateAddress(String newAddress) {
        // Business rule: address changes must be logged for compliance
        this.address = newAddress;
        // The patient is still the SAME patient after this change
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Patient)) return false;
        Patient other = (Patient) o;
        return id.equals(other.id);  // Equality based on IDENTITY only
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}
```

### Python Example

```python
# ENTITY: identity-based equality

class Patient:
    def __init__(self, patient_id: str, name: str):
        self.patient_id = patient_id  # Identity -- never changes
        self.name = name               # Can change
        self.address = None            # Can change
        self._diagnoses: list = []     # Can change

    def add_diagnosis(self, diagnosis) -> None:
        """Business rule: no duplicate active diagnoses."""
        for d in self._diagnoses:
            if d.code == diagnosis.code and d.is_active:
                raise ValueError(
                    f"Patient already has active diagnosis: {diagnosis.code}"
                )
        self._diagnoses.append(diagnosis)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Patient):
            return False
        return self.patient_id == other.patient_id  # Identity only

    def __hash__(self) -> int:
        return hash(self.patient_id)
```

---

## Value Objects: Value Matters

A Value Object has no identity. Two Value Objects are equal if all their attributes are equal. They should be immutable -- once created, they never change.

**The key question: "Do I care which specific instance this is, or only what value it holds?"** A five-dollar bill is a five-dollar bill. You do not care which one.

### Java Example

```java
// VALUE OBJECT: Two Money objects with the same amount and currency
// are completely interchangeable.

public final class Money {
    private final BigDecimal amount;
    private final String currency;

    public Money(BigDecimal amount, String currency) {
        if (amount == null) throw new IllegalArgumentException("Amount required");
        if (currency == null || currency.isBlank())
            throw new IllegalArgumentException("Currency required");
        this.amount = amount;
        this.currency = currency.toUpperCase();
    }

    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Cannot add different currencies");
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }

    public Money multiply(int quantity) {
        return new Money(this.amount.multiply(BigDecimal.valueOf(quantity)),
                        this.currency);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Money)) return false;
        Money money = (Money) o;
        return amount.compareTo(money.amount) == 0
            && currency.equals(money.currency);  // ALL attributes compared
    }

    @Override
    public int hashCode() {
        return Objects.hash(amount, currency);
    }
}
```

### Python Example

```python
# VALUE OBJECT: immutable, equality based on all attributes

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)   # frozen=True makes it immutable
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount is None:
            raise ValueError("Amount required")
        if not self.currency:
            raise ValueError("Currency required")
        # Normalize currency to uppercase
        object.__setattr__(self, 'currency', self.currency.upper())

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, quantity: int) -> 'Money':
        return Money(self.amount * quantity, self.currency)
```

### Entity vs Value Object Decision Guide

```
+------------------------------------------------------------------+
|  Ask yourself:                                                   |
|                                                                  |
|  Does it need a unique ID that persists over time?               |
|    YES --> Entity (Patient, Order, Account)                      |
|    NO  --> Value Object (Money, Address, DateRange)              |
|                                                                  |
|  Can two instances with the same attributes be swapped freely?   |
|    YES --> Value Object                                          |
|    NO  --> Entity                                                |
|                                                                  |
|  Does it change state over its lifetime?                         |
|    YES --> Likely an Entity                                      |
|    NO  --> Likely a Value Object (immutable)                     |
+------------------------------------------------------------------+
```

---

## Aggregates: The Consistency Boundary

An Aggregate is a cluster of Entities and Value Objects treated as a single unit for data changes. Every Aggregate has a **root entity** -- the only object that external code is allowed to reference.

**Why Aggregates matter:** They define the boundary within which all business rules are guaranteed to be consistent. Outside the boundary, consistency is eventual.

```
+------------------------------------------+
|  ORDER AGGREGATE                         |
|                                          |
|  +--------------------+                  |
|  | Order (ROOT)       |                  |
|  | - orderId          |                  |
|  | - status           |                  |
|  | - customerId       |   Reference by   |
|  +----+---------+-----+   ID only        |
|       |         |         (not by object) |
|       v         v                         |
|  +---------+ +---------+                 |
|  |OrderItem| |OrderItem|                 |
|  |- product| |- product|                 |
|  |- price  | |- price  |                 |
|  |- qty    | |- qty    |                 |
|  +---------+ +---------+                 |
|                                          |
+------------------------------------------+
  External code accesses OrderItems
  ONLY through the Order root.
```

### Aggregate Rules

1. **The root entity is the only entry point.** External objects never hold references to inner objects.
2. **The aggregate enforces all invariants.** When you add an item to an order, the Order (root) validates the business rules.
3. **One transaction per aggregate.** Save or update one aggregate at a time. Cross-aggregate consistency is handled through Domain Events.
4. **Reference other aggregates by ID, not by object.** An Order holds a `customerId`, not a `Customer` object.

### Java Example

```java
// AGGREGATE ROOT: Order controls access to its OrderItems

public class Order {
    private final OrderId id;
    private final CustomerId customerId;  // Reference by ID, not object
    private final List<OrderItem> items;
    private OrderStatus status;
    private Money totalPrice;

    public Order(OrderId id, CustomerId customerId) {
        this.id = id;
        this.customerId = customerId;
        this.items = new ArrayList<>();
        this.status = OrderStatus.DRAFT;
        this.totalPrice = Money.zero("USD");
    }

    public void addItem(String productId, Money price, int quantity) {
        // Invariant: cannot add items to a submitted order
        if (status != OrderStatus.DRAFT) {
            throw new IllegalStateException("Cannot modify a submitted order");
        }
        // Invariant: max 50 items per order
        if (items.size() >= 50) {
            throw new IllegalStateException("Order cannot have more than 50 items");
        }

        OrderItem item = new OrderItem(productId, price, quantity);
        items.add(item);
        recalculateTotal();
    }

    public void submit() {
        if (items.isEmpty()) {
            throw new IllegalStateException("Cannot submit an empty order");
        }
        this.status = OrderStatus.SUBMITTED;
        // This would also raise a domain event (covered next)
    }

    private void recalculateTotal() {
        this.totalPrice = items.stream()
            .map(OrderItem::subtotal)
            .reduce(Money.zero("USD"), Money::add);
    }

    // OrderItem is NOT exposed directly -- return an unmodifiable view
    public List<OrderItem> getItems() {
        return Collections.unmodifiableList(items);
    }
}
```

### Python Example

```python
# AGGREGATE ROOT

from enum import Enum
from typing import List
from dataclasses import dataclass


class OrderStatus(Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


class Order:
    """Aggregate Root -- all access to OrderItems goes through Order."""

    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id   # Reference by ID
        self._items: List[OrderItem] = []
        self._status = OrderStatus.DRAFT

    def add_item(self, product_id: str, price: float, quantity: int) -> None:
        if self._status != OrderStatus.DRAFT:
            raise ValueError("Cannot modify a submitted order")
        if len(self._items) >= 50:
            raise ValueError("Order cannot have more than 50 items")

        self._items.append(OrderItem(product_id, price, quantity))

    def submit(self) -> None:
        if not self._items:
            raise ValueError("Cannot submit an empty order")
        self._status = OrderStatus.SUBMITTED

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self._items)

    @property
    def items(self) -> tuple:
        return tuple(self._items)  # Immutable view
```

---

## Domain Events: Something Important Happened

A Domain Event is a record of something that happened in the domain. Events are named in the past tense: `OrderPlaced`, `PaymentReceived`, `PatientAdmitted`.

**Why events matter:** They let different parts of the system react to changes without being tightly coupled. When an order is placed, the inventory service needs to know -- but the Order aggregate should not call the inventory service directly.

```
+------------------+    OrderPlaced     +-------------------+
|  Order           | =================> |  Inventory        |
|  Aggregate       |    (event)         |  Service          |
+------------------+                    +-------------------+
                     \
                      \  OrderPlaced    +-------------------+
                       ===============> |  Notification     |
                          (event)       |  Service          |
                                        +-------------------+

The Order does not know about Inventory or Notifications.
It just says "this happened." Others decide what to do.
```

### Java Example

```java
// Domain Event
public class OrderPlaced {
    private final String orderId;
    private final String customerId;
    private final double totalAmount;
    private final Instant occurredAt;

    public OrderPlaced(String orderId, String customerId,
                       double totalAmount) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.totalAmount = totalAmount;
        this.occurredAt = Instant.now();
    }

    // Getters omitted for brevity
}

// Aggregate raises events
public class Order {
    private final List<Object> domainEvents = new ArrayList<>();

    public void submit() {
        if (items.isEmpty()) {
            throw new IllegalStateException("Cannot submit empty order");
        }
        this.status = OrderStatus.SUBMITTED;

        // Record the event -- do not publish yet
        domainEvents.add(new OrderPlaced(
            this.id.toString(),
            this.customerId.toString(),
            this.calculateTotal()
        ));
    }

    public List<Object> getDomainEvents() {
        return Collections.unmodifiableList(domainEvents);
    }

    public void clearDomainEvents() {
        domainEvents.clear();
    }
}

// Application Service publishes events after saving
public class PlaceOrderUseCase {
    public void execute(PlaceOrderCommand command) {
        Order order = createOrder(command);
        order.submit();

        orderRepository.save(order);

        // Publish events after successful save
        for (Object event : order.getDomainEvents()) {
            eventPublisher.publish(event);
        }
        order.clearDomainEvents();
    }
}
```

### Python Example

```python
# Domain Event
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class OrderPlaced:
    order_id: str
    customer_id: str
    total_amount: float
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# Aggregate with events
class Order:
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self._items = []
        self._status = OrderStatus.DRAFT
        self._domain_events = []

    def submit(self) -> None:
        if not self._items:
            raise ValueError("Cannot submit empty order")
        self._status = OrderStatus.SUBMITTED

        self._domain_events.append(
            OrderPlaced(
                order_id=self.order_id,
                customer_id=self.customer_id,
                total_amount=self.total,
            )
        )

    @property
    def domain_events(self) -> list:
        return list(self._domain_events)

    def clear_events(self) -> None:
        self._domain_events.clear()
```

---

## Repositories: Collection-Like Access

A Repository provides a collection-like interface for accessing and persisting Aggregates. It hides the details of the data store. To the domain, a Repository looks like an in-memory collection.

```
Domain thinks:              Reality:
+-----------+               +-----------+       +-----------+
| orders.   |               | Repository|       | Database  |
| find(id)  | ------------> | translates| ----> | SELECT *  |
| orders.   |               | to SQL or |       | FROM ...  |
| save(o)   |               | API calls |       |           |
+-----------+               +-----------+       +-----------+

The domain never knows a database exists.
```

### Java Example

```java
// Interface in the domain layer
public interface OrderRepository {
    Order findById(OrderId id);
    void save(Order order);
    List<Order> findByCustomer(CustomerId customerId);
    void delete(OrderId id);
}

// Usage in Application Service -- no database awareness
public class CancelOrderUseCase {
    private final OrderRepository orders;

    public CancelOrderUseCase(OrderRepository orders) {
        this.orders = orders;
    }

    public void execute(String orderId) {
        Order order = orders.findById(new OrderId(orderId));
        if (order == null) {
            throw new OrderNotFoundException(orderId);
        }
        order.cancel();
        orders.save(order);
    }
}
```

### Python Example

```python
# Interface in the domain layer
from abc import ABC, abstractmethod


class OrderRepository(ABC):

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order:
        """Returns the Order or raises NotFoundError."""
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        pass

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> list:
        pass


# Usage -- no database awareness
class CancelOrderUseCase:
    def __init__(self, orders: OrderRepository):
        self._orders = orders

    def execute(self, order_id: str) -> None:
        order = self._orders.find_by_id(order_id)
        order.cancel()
        self._orders.save(order)
```

---

## Domain Services: Stateless Business Operations

A Domain Service handles business logic that does not naturally belong to a single Entity or Value Object. It is **stateless** -- it performs a calculation or validation using data from multiple objects and returns a result.

### When to Use a Domain Service

- The operation involves multiple aggregates
- The logic does not belong to any single entity
- The operation is a recognized concept in the business domain

```java
// Domain Service: transfer between accounts involves two aggregates
public class MoneyTransferService {

    public TransferResult transfer(Account source, Account destination,
                                    Money amount) {
        if (!source.hasEnoughFunds(amount)) {
            return TransferResult.insufficientFunds();
        }

        source.debit(amount);
        destination.credit(amount);

        return TransferResult.success(source.getId(),
                                      destination.getId(), amount);
    }
}
```

```python
# Domain Service
class MoneyTransferService:

    def transfer(self, source: Account, destination: Account,
                 amount: Money) -> TransferResult:
        if not source.has_enough_funds(amount):
            return TransferResult.insufficient_funds()

        source.debit(amount)
        destination.credit(amount)

        return TransferResult.success(
            source.account_id, destination.account_id, amount
        )
```

---

## Rich Domain Model vs Anemic Model

This is one of the most important distinctions in DDD. An **Anemic Model** is a domain object that is just a bag of getters and setters with no behavior. A **Rich Domain Model** encapsulates both data and behavior.

### BEFORE: Anemic Model (Anti-Pattern)

```java
// ANEMIC MODEL: just data, no behavior
public class BankAccount {
    private String accountId;
    private double balance;
    private String status;

    // Only getters and setters -- no business logic
    public double getBalance() { return balance; }
    public void setBalance(double balance) { this.balance = balance; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}

// All logic lives in a "service" that manipulates the object
public class BankAccountService {
    public void withdraw(BankAccount account, double amount) {
        if (account.getStatus().equals("FROZEN")) {
            throw new RuntimeException("Account is frozen");
        }
        if (account.getBalance() < amount) {
            throw new RuntimeException("Insufficient funds");
        }
        account.setBalance(account.getBalance() - amount);
    }
}
```

**Problems with the Anemic Model:**
- Business rules are scattered across service classes
- The `BankAccount` can be put into an invalid state (negative balance) by anyone calling `setBalance`
- Rules get duplicated -- every service that touches `BankAccount` must remember to check the status
- The class is just a glorified `HashMap`

### AFTER: Rich Domain Model

```java
// RICH MODEL: data AND behavior together
public class BankAccount {
    private final AccountId id;
    private Money balance;
    private AccountStatus status;

    public BankAccount(AccountId id, Money initialDeposit) {
        this.id = id;
        this.balance = initialDeposit;
        this.status = AccountStatus.ACTIVE;
    }

    public void withdraw(Money amount) {
        // Business rules are right here, inside the object
        if (status == AccountStatus.FROZEN) {
            throw new AccountFrozenException(id);
        }
        if (balance.isLessThan(amount)) {
            throw new InsufficientFundsException(id, amount, balance);
        }
        this.balance = balance.subtract(amount);
    }

    public void deposit(Money amount) {
        if (status == AccountStatus.CLOSED) {
            throw new AccountClosedException(id);
        }
        this.balance = balance.add(amount);
    }

    public void freeze() {
        this.status = AccountStatus.FROZEN;
    }

    // No setBalance() -- the only way to change the balance
    // is through withdraw() or deposit(), which enforce the rules.
    public Money getBalance() {
        return balance;  // Money is immutable, so this is safe
    }
}
```

```python
# RICH MODEL in Python
class BankAccount:
    def __init__(self, account_id: str, initial_deposit: Money):
        self.account_id = account_id
        self._balance = initial_deposit
        self._status = AccountStatus.ACTIVE

    def withdraw(self, amount: Money) -> None:
        if self._status == AccountStatus.FROZEN:
            raise AccountFrozenError(self.account_id)
        if self._balance < amount:
            raise InsufficientFundsError(
                self.account_id, amount, self._balance
            )
        self._balance = self._balance.subtract(amount)

    def deposit(self, amount: Money) -> None:
        if self._status == AccountStatus.CLOSED:
            raise AccountClosedError(self.account_id)
        self._balance = self._balance.add(amount)

    def freeze(self) -> None:
        self._status = AccountStatus.FROZEN

    @property
    def balance(self) -> Money:
        return self._balance   # No setter -- enforced via methods
```

### Comparison Table

```
+-----------------------+-------------------+--------------------+
|  Aspect               | Anemic Model      | Rich Domain Model  |
+-----------------------+-------------------+--------------------+
| Business logic lives  | In service classes | Inside the entity  |
| Data + behavior       | Separated          | Together           |
| Invalid states        | Possible           | Prevented by design|
| Rule duplication      | Common             | Eliminated         |
| Testability           | Must test services | Test the entity    |
| Encapsulation         | Weak (setters)     | Strong (methods)   |
| Code reads like       | Technical steps    | Business language  |
+-----------------------+-------------------+--------------------+
```

---

## Real-World Scenario: Insurance Claims System

An insurance company needs to model their claims process.

**Ubiquitous Language glossary:**
- **Policy**: An insurance contract between the insurer and the policyholder
- **Claim**: A request by the policyholder for payment after a covered event
- **Adjuster**: The person who evaluates the claim
- **Settlement**: The agreed payment amount

```
AGGREGATES:

+------------------+     +------------------+     +------------------+
| Policy           |     | Claim            |     | Adjuster         |
| (Aggregate Root) |     | (Aggregate Root) |     | (Aggregate Root) |
|                  |     |                  |     |                  |
| - policyId       |<-id-| - policyId (ref) |     | - adjusterId     |
| - holderId (ref) |     | - claimId        |<-id-| - currentClaim   |
| - coverageItems  |     | - documents      |     |   Id (ref)       |
| - status         |     | - adjusterId(ref)|     | - specialties    |
| - effectiveDate  |     | - settlement     |     |                  |
| - expirationDate |     | - status         |     |                  |
+------------------+     +------------------+     +------------------+

Each aggregate is loaded and saved independently.
Cross-aggregate references are by ID only.

DOMAIN EVENTS:
  ClaimFiled --> triggers assignment to Adjuster
  ClaimApproved --> triggers payment processing
  PolicyExpired --> triggers notification to holder
```

---

## Common Mistakes

**Mistake 1: Using DDD for simple CRUD applications.**
If your application is mostly reading and writing data with little business logic, DDD adds unnecessary complexity. Use it when the domain is genuinely complex.

**Mistake 2: Making aggregates too large.**
An Order aggregate that contains Customer, Product, Warehouse, and ShippingRoute objects is too big. Keep aggregates small and reference other aggregates by ID.

**Mistake 3: Ignoring Ubiquitous Language.**
If the code uses `User` but the business says `Policyholder`, you are losing the primary benefit of DDD. Rename the code.

**Mistake 4: Treating Domain Services as a dumping ground.**
If most of your logic lives in Domain Services rather than Entities, you have an Anemic Model. Push behavior into the entities first.

**Mistake 5: Skipping the domain experts.**
DDD without domain expert involvement is just architecture theater. The whole point is collaborative modeling with people who understand the business.

---

## Best Practices

1. **Start with the Ubiquitous Language.** Before writing code, spend time with domain experts to establish shared terminology. Write it down.

2. **Make Value Objects your default.** When in doubt, model something as a Value Object. They are simpler, safer, and easier to test. Only use Entities when identity truly matters.

3. **Keep Aggregates small.** A good aggregate fits in your head. If you cannot explain what it protects in one sentence, it is too big.

4. **Use Domain Events for cross-aggregate communication.** Do not have one aggregate reach into another. Raise an event and let the other aggregate react.

5. **Put business rules in the domain objects.** If you find yourself writing `if (order.getStatus() == ...)` in a service class, that check belongs inside the `Order` class.

6. **Test the domain in isolation.** Domain tests should be fast, require no database, and read like business specifications.

---

## Quick Summary

Domain-Driven Design is an approach to software development that places the business domain at the center of the design process. It starts with Ubiquitous Language -- a shared vocabulary used by both developers and business experts. The domain model is built from Entities (objects with identity), Value Objects (objects defined by their attributes), and Aggregates (consistency boundaries with a root entity). Domain Events capture significant occurrences. Repositories provide collection-like access to aggregates. Domain Services handle logic spanning multiple objects. A Rich Domain Model encapsulates both data and behavior, preventing invalid states by design.

---

## Key Points

- DDD focuses on modeling the business domain, not the technology
- Ubiquitous Language eliminates translation errors between business and development
- Entities have unique identity; Value Objects are defined by their attributes
- Aggregates are consistency boundaries with a single root entity
- Domain Events decouple parts of the system by broadcasting that something happened
- Repositories hide persistence details behind a collection-like interface
- Domain Services handle stateless operations spanning multiple entities
- Rich Domain Models encapsulate data and behavior; Anemic Models are an anti-pattern
- DDD is most valuable for complex domains -- do not use it for simple CRUD

---

## Practice Questions

1. You are modeling an e-commerce system. Is a shipping address an Entity or a Value Object? Explain your reasoning.

2. An `Order` aggregate currently includes a `Customer` object loaded from the database. What is wrong with this design, and how would you fix it?

3. A developer puts the rule "orders over $500 require manager approval" in the `OrderController` class. Where should this rule live according to DDD, and why?

4. Explain why an Anemic Model makes it easier to create objects in invalid states. Give a specific example.

5. When should you use a Domain Service instead of putting logic directly in an Entity?

---

## Exercises

### Exercise 1: Model a Library System

Using DDD concepts, model a library system with the following requirements:
- Members can borrow books
- A member can have at most 5 books checked out
- Books have ISBNs and titles
- Overdue books incur a daily fine

Identify: Which classes are Entities? Which are Value Objects? What is the Aggregate Root? What Domain Events would you raise?

### Exercise 2: Anemic to Rich

Refactor this anemic model into a rich domain model:

```java
public class Subscription {
    private String id;
    private String plan;      // "BASIC", "PRO", "ENTERPRISE"
    private String status;    // "ACTIVE", "CANCELLED", "EXPIRED"
    private LocalDate startDate;
    private LocalDate endDate;

    // Only getters and setters
}

public class SubscriptionService {
    public void cancel(Subscription sub) {
        if (sub.getStatus().equals("CANCELLED")) {
            throw new RuntimeException("Already cancelled");
        }
        sub.setStatus("CANCELLED");
        sub.setEndDate(LocalDate.now());
    }

    public void upgrade(Subscription sub, String newPlan) {
        if (!sub.getStatus().equals("ACTIVE")) {
            throw new RuntimeException("Can only upgrade active subscriptions");
        }
        sub.setPlan(newPlan);
    }
}
```

Move the business rules into the `Subscription` class. Remove the setters. Make invalid states impossible.

### Exercise 3: Design Domain Events

For an online food delivery system, identify at least four Domain Events. For each event, describe:
- The event name (past tense)
- What data it carries
- What other parts of the system might react to it

---

## What Is Next?

DDD works best when you clearly define the boundaries of your domain models. In large systems, different parts of the business use the same words to mean different things -- "customer" in sales is not the same as "customer" in support. The next chapter on **Bounded Contexts** shows you how to draw these boundaries, prevent naming collisions, and build systems where each team has its own clean, focused model.
