# Chapter 12: The Dependency Inversion Principle -- Depend on Abstractions, Not Details

---

## What You Will Learn

- What the Dependency Inversion Principle (DIP) means and why the direction of dependencies matters
- Why high-level business logic should never depend directly on low-level infrastructure
- How to invert dependencies using interfaces (ports)
- Dependency injection as the primary mechanism for implementing DIP
- IoC containers in Java (Spring @Autowired) and Python (dependency-injector)
- Abstract factories as a DIP pattern
- How DIP enables testing by letting you inject mock implementations
- Before and after: OrderService with direct MySQL dependency refactored to use a DatabasePort

---

## Why This Chapter Matters

Consider this scenario: your `OrderService` class directly imports and creates a `MySQLDatabase` object. Everything works perfectly. Then one day, the team decides to switch from MySQL to PostgreSQL. Or you need to write unit tests for `OrderService` but cannot because it connects to a real database.

The problem is not MySQL. The problem is the direction of the dependency. Your high-level business logic (processing orders) depends directly on a low-level detail (which specific database to use). When the detail changes, the business logic must change too.

The Dependency Inversion Principle reverses this relationship. Instead of the business logic reaching down to the database, both the business logic and the database depend on an abstraction (an interface). The business logic says "I need something that can save orders." The database says "I can save orders." Neither knows about the other. This makes your code testable, flexible, and resilient to change.

---

## The Dependency Inversion Principle Defined

Robert C. Martin stated two rules:

> 1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
> 2. Abstractions should not depend on details. Details should depend on abstractions.

```
+-----------------------------------------------------------+
|     DEPENDENCY INVERSION PRINCIPLE                         |
+-----------------------------------------------------------+
|                                                            |
|  BEFORE (without DIP):                                     |
|                                                            |
|  +----------------+         +------------------+           |
|  | OrderService   |-------->| MySQLDatabase    |           |
|  | (high-level)   |         | (low-level)      |           |
|  +----------------+         +------------------+           |
|                                                            |
|  High-level depends on low-level.                          |
|  Change MySQL --> change OrderService.                     |
|  Cannot test OrderService without MySQL.                   |
|                                                            |
|  AFTER (with DIP):                                         |
|                                                            |
|  +----------------+         +------------------+           |
|  | OrderService   |-------->| DatabasePort     |           |
|  | (high-level)   |         | (abstraction)    |           |
|  +----------------+         +------------------+           |
|                                    ^                       |
|                                    |                       |
|                             +------------------+           |
|                             | MySQLDatabase    |           |
|                             | (low-level)      |           |
|                             +------------------+           |
|                                                            |
|  Both depend on the abstraction.                           |
|  Change MySQL --> only change MySQLDatabase.               |
|  Test OrderService with a mock DatabasePort.               |
|                                                            |
+-----------------------------------------------------------+
```

Notice how the dependency arrow changed direction. Before DIP, the arrow pointed from high-level to low-level. After DIP, the low-level module points up toward the abstraction. This is the "inversion."

---

## The Problem: Direct Dependencies

### BEFORE: OrderService Coupled to MySQL (Java)

```java
// Java -- BAD: High-level module depends directly on low-level module
public class OrderService {

    private final MySQLDatabase database;
    private final StripePaymentGateway paymentGateway;
    private final SendGridEmailService emailService;

    public OrderService() {
        // Creates its own dependencies -- tightly coupled
        this.database = new MySQLDatabase(
            "jdbc:mysql://prod-server:3306/orders"
        );
        this.paymentGateway = new StripePaymentGateway("sk_live_xxx");
        this.emailService = new SendGridEmailService("sg_api_key_xxx");
    }

    public void placeOrder(Order order) {
        // Validate
        if (order.getItems().isEmpty()) {
            throw new IllegalArgumentException("Order has no items");
        }

        // Charge payment through Stripe specifically
        paymentGateway.charge(
            order.getCreditCard(),
            order.getTotal()
        );

        // Save to MySQL specifically
        database.executeUpdate(
            "INSERT INTO orders (id, customer_id, total) VALUES (?, ?, ?)",
            order.getId(),
            order.getCustomerId(),
            order.getTotal()
        );

        // Send email through SendGrid specifically
        emailService.send(
            order.getCustomerEmail(),
            "Order Confirmation",
            "Your order #" + order.getId() + " has been placed."
        );
    }
}
```

**Problems with this code:**

1. **Cannot test without real services.** Unit testing `placeOrder` requires a MySQL server, a Stripe account, and a SendGrid account.
2. **Cannot swap implementations.** Switching from MySQL to PostgreSQL requires modifying `OrderService`.
3. **Cannot reuse.** This class is welded to three specific vendors.
4. **Violates SRP.** `OrderService` knows about MySQL connection strings, Stripe API keys, and SendGrid configuration.

### BEFORE: Same Problem in Python

```python
# Python -- BAD: Direct dependency on specific implementations
import mysql.connector
import stripe
from sendgrid import SendGridAPIClient


class OrderService:

    def __init__(self):
        self.db = mysql.connector.connect(
            host="prod-server",
            database="orders",
            user="admin",
            password="secret",
        )
        stripe.api_key = "sk_live_xxx"
        self.email_client = SendGridAPIClient("sg_api_key_xxx")

    def place_order(self, order: Order) -> None:
        if not order.items:
            raise ValueError("Order has no items")

        # Coupled to Stripe
        stripe.Charge.create(
            amount=int(order.total * 100),
            currency="usd",
            source=order.credit_card_token,
        )

        # Coupled to MySQL
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO orders (id, customer_id, total) "
            "VALUES (%s, %s, %s)",
            (order.id, order.customer_id, order.total),
        )
        self.db.commit()

        # Coupled to SendGrid
        self.email_client.send(
            to_emails=order.customer_email,
            subject="Order Confirmation",
            html_content=f"Your order #{order.id} has been placed.",
        )
```

---

## The Solution: Depend on Abstractions

### Step 1: Define the Abstractions (Ports)

The abstractions represent what the high-level module needs, not how the low-level module works.

```java
// Java -- Define abstractions (ports)

public interface OrderRepository {
    void save(Order order);
    Optional<Order> findById(String orderId);
    List<Order> findByCustomer(String customerId);
}

public interface PaymentGateway {
    PaymentResult charge(String paymentToken, BigDecimal amount);
    void refund(String transactionId);
}

public interface NotificationService {
    void sendOrderConfirmation(Order order);
}
```

```python
# Python -- Define abstractions
from abc import ABC, abstractmethod


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None:
        pass

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> list[Order]:
        pass


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, payment_token: str, amount: float) -> PaymentResult:
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> None:
        pass


class NotificationService(ABC):
    @abstractmethod
    def send_order_confirmation(self, order: Order) -> None:
        pass
```

### Step 2: Rewrite the High-Level Module Against Abstractions

```java
// Java -- GOOD: OrderService depends only on abstractions
public class OrderService {

    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    private final NotificationService notificationService;

    // Dependencies are INJECTED, not created internally
    public OrderService(
            OrderRepository orderRepository,
            PaymentGateway paymentGateway,
            NotificationService notificationService) {

        this.orderRepository = orderRepository;
        this.paymentGateway = paymentGateway;
        this.notificationService = notificationService;
    }

    public void placeOrder(Order order) {
        if (order.getItems().isEmpty()) {
            throw new IllegalArgumentException("Order has no items");
        }

        PaymentResult payment = paymentGateway.charge(
            order.getPaymentToken(),
            order.getTotal()
        );

        order.setTransactionId(payment.getTransactionId());
        orderRepository.save(order);

        notificationService.sendOrderConfirmation(order);
    }
}
```

```python
# Python -- GOOD: OrderService depends only on abstractions
class OrderService:

    def __init__(
        self,
        order_repository: OrderRepository,
        payment_gateway: PaymentGateway,
        notification_service: NotificationService,
    ):
        self._order_repository = order_repository
        self._payment_gateway = payment_gateway
        self._notification_service = notification_service

    def place_order(self, order: Order) -> None:
        if not order.items:
            raise ValueError("Order has no items")

        payment = self._payment_gateway.charge(
            order.payment_token, order.total
        )

        order.transaction_id = payment.transaction_id
        self._order_repository.save(order)

        self._notification_service.send_order_confirmation(order)
```

Notice that `OrderService` no longer mentions MySQL, Stripe, SendGrid, or any specific technology. It works with abstractions.

### Step 3: Implement the Abstractions (Adapters)

```java
// Java -- Low-level implementations (adapters)

public class MySQLOrderRepository implements OrderRepository {

    private final DataSource dataSource;

    public MySQLOrderRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public void save(Order order) {
        try (Connection conn = dataSource.getConnection()) {
            PreparedStatement stmt = conn.prepareStatement(
                "INSERT INTO orders (id, customer_id, total, tx_id) "
                + "VALUES (?, ?, ?, ?)"
            );
            stmt.setString(1, order.getId());
            stmt.setString(2, order.getCustomerId());
            stmt.setBigDecimal(3, order.getTotal());
            stmt.setString(4, order.getTransactionId());
            stmt.executeUpdate();
        } catch (SQLException e) {
            throw new RepositoryException(
                "Failed to save order: " + order.getId(), e
            );
        }
    }

    @Override
    public Optional<Order> findById(String orderId) {
        // MySQL-specific implementation
    }

    @Override
    public List<Order> findByCustomer(String customerId) {
        // MySQL-specific implementation
    }
}

public class StripePaymentGateway implements PaymentGateway {

    private final String apiKey;

    public StripePaymentGateway(String apiKey) {
        this.apiKey = apiKey;
    }

    @Override
    public PaymentResult charge(String paymentToken, BigDecimal amount) {
        // Stripe-specific implementation
        Stripe.apiKey = this.apiKey;
        Charge charge = Charge.create(Map.of(
            "amount", amount.multiply(BigDecimal.valueOf(100)).intValue(),
            "currency", "usd",
            "source", paymentToken
        ));
        return new PaymentResult(true, charge.getId());
    }

    @Override
    public void refund(String transactionId) {
        // Stripe-specific refund implementation
    }
}
```

```python
# Python -- Low-level implementations (adapters)
import mysql.connector


class MySQLOrderRepository(OrderRepository):

    def __init__(self, connection_config: dict):
        self._config = connection_config

    def save(self, order: Order) -> None:
        conn = mysql.connector.connect(**self._config)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (id, customer_id, total, tx_id) "
                "VALUES (%s, %s, %s, %s)",
                (order.id, order.customer_id, order.total,
                 order.transaction_id),
            )
            conn.commit()
        except Exception as e:
            raise RepositoryError(
                f"Failed to save order: {order.id}"
            ) from e
        finally:
            conn.close()

    def find_by_id(self, order_id: str) -> Order | None:
        # MySQL-specific implementation
        pass

    def find_by_customer(self, customer_id: str) -> list[Order]:
        # MySQL-specific implementation
        pass


class StripePaymentGateway(PaymentGateway):

    def __init__(self, api_key: str):
        self._api_key = api_key

    def charge(self, payment_token: str, amount: float) -> PaymentResult:
        import stripe
        stripe.api_key = self._api_key
        charge = stripe.Charge.create(
            amount=int(amount * 100),
            currency="usd",
            source=payment_token,
        )
        return PaymentResult(success=True, transaction_id=charge.id)

    def refund(self, transaction_id: str) -> None:
        # Stripe-specific refund implementation
        pass
```

---

## The Dependency Arrows: Before and After

```
+-----------------------------------------------------------+
|     DEPENDENCY DIRECTION: BEFORE vs AFTER                  |
+-----------------------------------------------------------+
|                                                            |
|  BEFORE (Dependencies point downward):                     |
|                                                            |
|    OrderService                                            |
|        |                                                   |
|        +---------> MySQLDatabase                           |
|        +---------> StripeGateway                           |
|        +---------> SendGridEmail                           |
|                                                            |
|  High-level knows about low-level details.                 |
|  Change flows UPWARD (breaking high-level code).           |
|                                                            |
|  -------------------------------------------------------- |
|                                                            |
|  AFTER (Dependencies point toward abstractions):           |
|                                                            |
|    OrderService                                            |
|        |                                                   |
|        +---------> OrderRepository (interface)             |
|        |                  ^                                |
|        |                  |                                |
|        |           MySQLOrderRepository                    |
|        |                                                   |
|        +---------> PaymentGateway (interface)              |
|        |                  ^                                |
|        |                  |                                |
|        |           StripePaymentGateway                    |
|        |                                                   |
|        +---------> NotificationService (interface)         |
|                          ^                                 |
|                          |                                 |
|                   EmailNotificationService                 |
|                                                            |
|  Everything depends on abstractions.                       |
|  Change is isolated to the adapter that changes.           |
|                                                            |
+-----------------------------------------------------------+
```

---

## Dependency Injection: The Mechanism

DIP tells you what to depend on (abstractions). Dependency Injection (DI) tells you how to provide those abstractions to the classes that need them. There are three common forms:

### Constructor Injection (Preferred)

```java
// Java -- Constructor injection
public class OrderService {

    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }
}
```

```python
# Python -- Constructor injection
class OrderService:

    def __init__(self, repository: OrderRepository):
        self._repository = repository
```

### Method Injection (For One-Off Dependencies)

```java
// Java -- Method injection: dependency used only in one method
public class ReportGenerator {

    public Report generate(DataSource dataSource) {
        // dataSource is only needed for this method
    }
}
```

### Setter Injection (Least Preferred)

```java
// Java -- Setter injection: allows changing dependency at runtime
public class OrderService {

    private OrderRepository repository;

    public void setRepository(OrderRepository repository) {
        this.repository = repository;
    }
}
// Problem: object is in invalid state between construction and setRepository()
```

Constructor injection is preferred because it makes dependencies explicit, ensures the object is always in a valid state, and makes the class immutable.

---

## IoC Containers

In a real application, you might have dozens of classes with dependencies. Wiring them together manually becomes tedious. IoC (Inversion of Control) containers automate this wiring.

### Java: Spring Framework

```java
// Java -- Spring @Autowired wires dependencies automatically

@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    private final NotificationService notificationService;

    @Autowired
    public OrderService(
            OrderRepository orderRepository,
            PaymentGateway paymentGateway,
            NotificationService notificationService) {

        this.orderRepository = orderRepository;
        this.paymentGateway = paymentGateway;
        this.notificationService = notificationService;
    }

    public void placeOrder(Order order) {
        // Business logic -- no infrastructure concerns
    }
}

@Repository
public class MySQLOrderRepository implements OrderRepository {
    // Spring finds this because it implements OrderRepository
}

@Component
public class StripePaymentGateway implements PaymentGateway {
    // Spring finds this because it implements PaymentGateway
}

@Component
public class EmailNotificationService implements NotificationService {
    // Spring finds this because it implements NotificationService
}
```

Spring scans for classes annotated with `@Service`, `@Repository`, and `@Component`, figures out which class implements which interface, and automatically wires everything together.

### Python: dependency-injector

```python
# Python -- Using dependency-injector library
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    # Low-level modules
    order_repository = providers.Singleton(
        MySQLOrderRepository,
        connection_config=config.database,
    )

    payment_gateway = providers.Singleton(
        StripePaymentGateway,
        api_key=config.stripe_api_key,
    )

    notification_service = providers.Singleton(
        EmailNotificationService,
        smtp_host=config.smtp_host,
    )

    # High-level module -- wired automatically
    order_service = providers.Factory(
        OrderService,
        order_repository=order_repository,
        payment_gateway=payment_gateway,
        notification_service=notification_service,
    )


# Usage
container = Container()
container.config.from_yaml("config.yaml")

service = container.order_service()
service.place_order(order)
```

### Simple Manual Wiring (No Framework)

You do not always need a framework. For smaller applications, manual wiring at the application entry point is perfectly fine:

```python
# Python -- Simple manual dependency injection
def create_app():
    """Wire everything together at the top level."""
    db_config = load_config("database")
    stripe_key = load_config("stripe_api_key")

    repository = MySQLOrderRepository(db_config)
    gateway = StripePaymentGateway(stripe_key)
    notifier = EmailNotificationService(load_config("smtp"))

    order_service = OrderService(repository, gateway, notifier)

    return order_service
```

```java
// Java -- Simple manual wiring
public class Application {

    public static void main(String[] args) {
        // Wire everything at the entry point
        DataSource dataSource = createDataSource();
        OrderRepository repository = new MySQLOrderRepository(dataSource);
        PaymentGateway gateway = new StripePaymentGateway("sk_live_xxx");
        NotificationService notifier = new EmailNotificationService();

        OrderService service = new OrderService(
            repository, gateway, notifier
        );

        // Use the service
        service.placeOrder(order);
    }
}
```

---

## DIP Enables Testing

The biggest practical benefit of DIP is testability. When your business logic depends on abstractions, you can inject test doubles (mocks, stubs, fakes) instead of real infrastructure.

```java
// Java -- Testing with mock dependencies
public class OrderServiceTest {

    @Test
    public void placeOrder_shouldSaveOrderAfterPayment() {
        // Create test doubles
        OrderRepository mockRepo = mock(OrderRepository.class);
        PaymentGateway mockGateway = mock(PaymentGateway.class);
        NotificationService mockNotifier = mock(NotificationService.class);

        when(mockGateway.charge(anyString(), any(BigDecimal.class)))
            .thenReturn(new PaymentResult(true, "tx_123"));

        // Inject test doubles
        OrderService service = new OrderService(
            mockRepo, mockGateway, mockNotifier
        );

        // Test
        Order order = new Order("order_1", "cust_1",
            List.of(new Item("Widget", 1)),
            "tok_visa", BigDecimal.valueOf(29.99));

        service.placeOrder(order);

        // Verify
        verify(mockGateway).charge("tok_visa", BigDecimal.valueOf(29.99));
        verify(mockRepo).save(order);
        verify(mockNotifier).sendOrderConfirmation(order);
    }

    @Test
    public void placeOrder_shouldNotSaveIfPaymentFails() {
        OrderRepository mockRepo = mock(OrderRepository.class);
        PaymentGateway mockGateway = mock(PaymentGateway.class);
        NotificationService mockNotifier = mock(NotificationService.class);

        when(mockGateway.charge(anyString(), any(BigDecimal.class)))
            .thenThrow(new PaymentException("Card declined"));

        OrderService service = new OrderService(
            mockRepo, mockGateway, mockNotifier
        );

        Order order = new Order("order_1", "cust_1",
            List.of(new Item("Widget", 1)),
            "tok_declined", BigDecimal.valueOf(29.99));

        assertThrows(PaymentException.class,
            () -> service.placeOrder(order));

        verify(mockRepo, never()).save(any());
        verify(mockNotifier, never()).sendOrderConfirmation(any());
    }
}
```

```python
# Python -- Testing with mock dependencies
from unittest.mock import Mock, MagicMock
import pytest


class TestOrderService:

    def test_place_order_saves_after_payment(self):
        # Create test doubles
        mock_repo = Mock(spec=OrderRepository)
        mock_gateway = Mock(spec=PaymentGateway)
        mock_notifier = Mock(spec=NotificationService)

        mock_gateway.charge.return_value = PaymentResult(
            success=True, transaction_id="tx_123"
        )

        # Inject test doubles
        service = OrderService(mock_repo, mock_gateway, mock_notifier)

        order = Order(
            id="order_1",
            customer_id="cust_1",
            items=[Item("Widget", 1)],
            payment_token="tok_visa",
            total=29.99,
        )

        service.place_order(order)

        # Verify
        mock_gateway.charge.assert_called_once_with("tok_visa", 29.99)
        mock_repo.save.assert_called_once_with(order)
        mock_notifier.send_order_confirmation.assert_called_once_with(order)

    def test_place_order_does_not_save_if_payment_fails(self):
        mock_repo = Mock(spec=OrderRepository)
        mock_gateway = Mock(spec=PaymentGateway)
        mock_notifier = Mock(spec=NotificationService)

        mock_gateway.charge.side_effect = PaymentError("Card declined")

        service = OrderService(mock_repo, mock_gateway, mock_notifier)

        order = Order(
            id="order_1",
            customer_id="cust_1",
            items=[Item("Widget", 1)],
            payment_token="tok_declined",
            total=29.99,
        )

        with pytest.raises(PaymentError):
            service.place_order(order)

        mock_repo.save.assert_not_called()
        mock_notifier.send_order_confirmation.assert_not_called()
```

Without DIP, these tests would require a running MySQL database, a Stripe account, and an email server. With DIP, they run in milliseconds with zero infrastructure.

---

## Abstract Factories: Creating Families of Objects

Sometimes you need to create objects at runtime, but you still want to depend on abstractions. An abstract factory lets you do this.

```java
// Java -- Abstract factory for DIP-compliant object creation
public interface DatabaseFactory {
    Connection createConnection();
    QueryBuilder createQueryBuilder();
    MigrationRunner createMigrationRunner();
}

public class MySQLDatabaseFactory implements DatabaseFactory {

    @Override
    public Connection createConnection() {
        return new MySQLConnection("jdbc:mysql://...");
    }

    @Override
    public QueryBuilder createQueryBuilder() {
        return new MySQLQueryBuilder();
    }

    @Override
    public MigrationRunner createMigrationRunner() {
        return new MySQLMigrationRunner();
    }
}

public class PostgresDatabaseFactory implements DatabaseFactory {

    @Override
    public Connection createConnection() {
        return new PostgresConnection("jdbc:postgresql://...");
    }

    @Override
    public QueryBuilder createQueryBuilder() {
        return new PostgresQueryBuilder();
    }

    @Override
    public MigrationRunner createMigrationRunner() {
        return new PostgresMigrationRunner();
    }
}

// High-level code uses the factory abstraction
public class DataService {

    private final DatabaseFactory dbFactory;

    public DataService(DatabaseFactory dbFactory) {
        this.dbFactory = dbFactory;
    }

    public void runMigrations() {
        Connection conn = dbFactory.createConnection();
        MigrationRunner runner = dbFactory.createMigrationRunner();
        runner.migrate(conn);
    }
}
```

```python
# Python -- Abstract factory
from abc import ABC, abstractmethod


class DatabaseFactory(ABC):
    @abstractmethod
    def create_connection(self) -> Connection:
        pass

    @abstractmethod
    def create_query_builder(self) -> QueryBuilder:
        pass


class MySQLDatabaseFactory(DatabaseFactory):

    def create_connection(self) -> Connection:
        return MySQLConnection("mysql://...")

    def create_query_builder(self) -> QueryBuilder:
        return MySQLQueryBuilder()


class PostgresDatabaseFactory(DatabaseFactory):

    def create_connection(self) -> Connection:
        return PostgresConnection("postgresql://...")

    def create_query_builder(self) -> QueryBuilder:
        return PostgresQueryBuilder()


class DataService:

    def __init__(self, db_factory: DatabaseFactory):
        self._db_factory = db_factory

    def execute_query(self, query_spec) -> list:
        conn = self._db_factory.create_connection()
        builder = self._db_factory.create_query_builder()
        query = builder.build(query_spec)
        return conn.execute(query)
```

---

## Common Mistakes

1. **Depending on abstractions but creating concrete classes internally.** If your constructor does `this.repo = new MySQLRepository()`, you have DIP in name only. The dependency must be injected from outside.

2. **Creating an abstraction for every class.** Not everything needs an interface. DIP matters at architectural boundaries -- between business logic and infrastructure, between your code and third-party libraries. A utility class that formats strings does not need an interface.

3. **Leaking implementation details through the abstraction.** If your `OrderRepository` interface has a method called `executeMySQLQuery()`, the abstraction is not abstract. Define the interface in terms of business operations: `save()`, `findById()`, `delete()`.

4. **Using a DI container as a service locator.** Do not pass the container itself around and have classes pull dependencies from it. This hides dependencies and makes code harder to understand.

5. **Circular dependencies.** If A depends on B's abstraction and B depends on A's abstraction, you have a design problem that DIP cannot fix. Refactor to remove the cycle.

---

## Best Practices

1. **Define abstractions in the high-level module.** The `OrderRepository` interface should live in the same package/module as `OrderService`, not in the database package. This ensures the high-level module owns its own abstractions.

2. **Use constructor injection.** It makes dependencies explicit, enables immutability, and makes invalid states impossible.

3. **Apply DIP at architectural boundaries.** Invert dependencies between your business logic and databases, APIs, file systems, email services, and other infrastructure.

4. **Keep abstractions stable.** The interface should change rarely. If it changes frequently, the abstraction is wrong.

5. **Wire dependencies at the composition root.** The entry point of your application (main function, Spring configuration, container setup) is where all the concrete implementations get wired together. Business logic classes should never create their own dependencies.

6. **Start without a DI framework.** Manual constructor injection is simple and clear. Add a framework only when the wiring becomes complex enough to justify it.

---

## Quick Summary

```
+-----------------------------------------------------------+
|              DIP CHEAT SHEET                               |
+-----------------------------------------------------------+
|                                                            |
|  PRINCIPLE:                                                |
|    High-level modules should not depend on low-level       |
|    modules. Both should depend on abstractions.            |
|                                                            |
|  HOW TO APPLY:                                             |
|    1. Define an interface for what the high-level module   |
|       needs (OrderRepository, PaymentGateway)              |
|    2. High-level module depends on the interface           |
|    3. Low-level module implements the interface            |
|    4. Inject the implementation via constructor            |
|                                                            |
|  KEY BENEFIT:                                              |
|    Testability. Inject mocks instead of real databases,    |
|    APIs, and services. Tests run in milliseconds.          |
|                                                            |
|  TOOLS:                                                    |
|    Java: Spring (@Autowired, @Service, @Repository)        |
|    Python: dependency-injector, or manual wiring           |
|                                                            |
|  WHERE TO APPLY:                                           |
|    At architectural boundaries:                            |
|    - Business logic <--> Database                          |
|    - Business logic <--> External APIs                     |
|    - Business logic <--> File system                       |
|    - Business logic <--> Email/notification services       |
|                                                            |
+-----------------------------------------------------------+
```

---

## Key Points

- The Dependency Inversion Principle says high-level modules should not depend on low-level modules; both should depend on abstractions
- "Inversion" means the dependency arrow flips: instead of business logic pointing to infrastructure, infrastructure points toward the abstraction that business logic defines
- Dependency injection is the mechanism for implementing DIP: pass abstractions into constructors instead of creating concrete classes internally
- DIP enables testability because you can inject mock implementations instead of real databases and APIs
- IoC containers like Spring and dependency-injector automate the wiring, but manual constructor injection works well for smaller applications
- Define abstractions from the high-level module's perspective, using business language, not infrastructure language
- Apply DIP at architectural boundaries between business logic and infrastructure, not between every pair of classes

---

## Practice Questions

1. Explain the Dependency Inversion Principle in your own words. What does "inversion" refer to specifically?

2. What is the difference between Dependency Inversion (the principle) and Dependency Injection (the technique)? How are they related?

3. Why is constructor injection preferred over setter injection? What problems does setter injection create?

4. How does DIP enable unit testing? Give a specific example of how you would test a service that depends on a database without DIP, and then with DIP.

5. Where should the abstraction (interface) live -- in the high-level module's package or the low-level module's package? Why does this matter?

---

## Exercises

### Exercise 1: Invert the Dependencies

Refactor the following class to follow DIP. Define appropriate abstractions, implement them, and update the class to use constructor injection.

```python
import requests
import json


class WeatherReporter:

    def get_daily_report(self, city: str) -> str:
        # Directly coupled to OpenWeatherMap API
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid=hardcoded_api_key"
        )
        data = response.json()

        # Directly coupled to file system
        with open(f"/reports/{city}_weather.json", "w") as f:
            json.dump(data, f)

        # Directly coupled to print
        report = f"Weather in {city}: {data['main']['temp']}K"
        print(report)
        return report
```

### Exercise 2: Write Tests with Mock Dependencies

Using the refactored code from Exercise 1, write unit tests that verify:
1. The reporter fetches weather data from the weather service
2. The reporter saves the data using the storage service
3. The reporter formats and returns a readable report
4. If the weather service fails, the reporter raises an appropriate error

Use mock objects -- no real HTTP calls or file I/O.

### Exercise 3: Compare Manual Wiring vs. Container

Set up the OrderService example from this chapter twice: once with manual constructor injection in a `main()` function, and once using a DI container (Spring for Java or dependency-injector for Python). Compare the two approaches in terms of boilerplate code, readability, and flexibility. Which would you choose for a project with 10 services? With 100 services?

---

## What Is Next?

You have now completed all five SOLID principles. Together, they provide a foundation for building software that is easy to understand, easy to change, and easy to test. The next chapters build on this foundation with additional principles (DRY, KISS, YAGNI) and practical techniques (code smells, refactoring patterns, unit testing) that turn these principles into daily practice.
