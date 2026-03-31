# Chapter 20: Hexagonal Architecture -- Ports and Adapters

## What You Will Learn

- What hexagonal architecture is and why it was created
- The concepts of ports and adapters and how they differ from layers
- The difference between driving (primary) and driven (secondary) adapters
- How the core domain sits at the center, completely isolated from infrastructure
- A complete before-and-after refactoring from layered to hexagonal
- The testing advantage that hexagonal architecture provides
- When to use hexagonal architecture and when layered is sufficient

## Why This Chapter Matters

Layered architecture (Chapter 19) is a great starting point, but it has a structural flaw: the business logic depends on the data access layer. This means your domain code knows about databases, and swapping infrastructure requires changing the core. Hexagonal architecture, introduced by Alistair Cockburn, fixes this by putting the domain at the center and defining clear ports (interfaces) that the outside world plugs into with adapters. The result is a system where the core business logic has zero dependencies on any framework, database, or external service -- making it trivially easy to test, change, and evolve.

---

## 20.1 The Core Idea

Hexagonal architecture (also called Ports and Adapters) is built on one principle:

> The application talks to the outside world through ports. The outside world connects to the application through adapters.

The application does not know or care what is on the other side of a port. It could be a real database, an in-memory fake, a test mock, or a completely different technology.

```
  +-------------------------------------------------------------+
  |                                                              |
  |  Traditional Layered:                                        |
  |    UI  -->  Business Logic  -->  Database                    |
  |    (Business depends on Database)                            |
  |                                                              |
  |  Hexagonal:                                                  |
  |    UI Adapter  -->  [Port]  DOMAIN  [Port]  <--  DB Adapter  |
  |    (Domain depends on NOTHING external)                      |
  |                                                              |
  +-------------------------------------------------------------+
```

---

## 20.2 The Hexagon Diagram

The hexagonal shape is a visual metaphor -- the number of sides is not significant. What matters is that the domain is at the center and all external systems connect through the edges.

```
                        Driving Side
                    (Primary Adapters)

                  REST         CLI
                Controller    Command
                    \          /
                     \        /
          +-----------\------/------------+
         /             \    /              \
        /    +----------\--/----------+     \
       /     |    Driving Ports       |      \
      /      |   (Input Interfaces)   |       \
     |       +------------------------+        |
     |       |                        |        |
     |       |    DOMAIN CORE         |        |
     |       |                        |        |
     |       |  Entities              |        |
     |       |  Use Cases             |        |
     |       |  Business Rules        |        |
     |       |                        |        |
     |       +------------------------+        |
      \      |   Driven Ports         |       /
       \     |   (Output Interfaces)  |      /
        \    +----------+--+----------+     /
         \             /    \              /
          +-----------/------\------------+
                     /        \
                    /          \
              Database       Email
              Adapter       Adapter

                    Driven Side
                (Secondary Adapters)
```

---

## 20.3 Ports: What the Domain Needs and Offers

A **port** is an interface defined by the domain. Ports come in two varieties:

### Driving Ports (Primary / Input)

Driving ports define how the outside world can **use** the application. They are the entry points -- the API of your domain.

```java
// Driving port: defines what the application can DO
public interface OrderManagement {
    Order placeOrder(String customerId, List<OrderItem> items);
    Order getOrder(String orderId);
    void cancelOrder(String orderId);
}
```

```python
# Driving port: defines what the application can DO
from abc import ABC, abstractmethod

class OrderManagement(ABC):
    @abstractmethod
    def place_order(self, customer_id, items): ...

    @abstractmethod
    def get_order(self, order_id): ...

    @abstractmethod
    def cancel_order(self, order_id): ...
```

### Driven Ports (Secondary / Output)

Driven ports define what the application **needs** from the outside world. They are the requirements -- the dependencies the domain declares without knowing who satisfies them.

```java
// Driven port: defines what the application NEEDS
public interface OrderRepository {
    Order save(Order order);
    Optional<Order> findById(String id);
    void deleteById(String id);
}

public interface PaymentGateway {
    PaymentResult charge(String customerId, Money amount);
    void refund(String transactionId);
}

public interface NotificationSender {
    void sendOrderConfirmation(String customerId, Order order);
}
```

```python
# Driven ports: define what the application NEEDS
class OrderRepository(ABC):
    @abstractmethod
    def save(self, order): ...

    @abstractmethod
    def find_by_id(self, order_id): ...

    @abstractmethod
    def delete_by_id(self, order_id): ...


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, customer_id, amount): ...

    @abstractmethod
    def refund(self, transaction_id): ...


class NotificationSender(ABC):
    @abstractmethod
    def send_order_confirmation(self, customer_id, order): ...
```

### Port Summary

```
  +-----------------------------------------------------------+
  |                                                            |
  |  DRIVING PORTS              DRIVEN PORTS                   |
  |  (Input / Primary)          (Output / Secondary)           |
  |                                                            |
  |  "What I offer"             "What I need"                  |
  |  Defined by domain          Defined by domain              |
  |  Implemented by domain      Implemented by adapters        |
  |  Called by adapters          Called by domain               |
  |                                                            |
  |  Examples:                  Examples:                       |
  |  - OrderManagement          - OrderRepository              |
  |  - UserRegistration         - PaymentGateway               |
  |  - ReportGeneration         - NotificationSender           |
  |                                                            |
  +-----------------------------------------------------------+
```

---

## 20.4 Adapters: Connecting the Outside World

An **adapter** is a concrete implementation that connects an external system to a port.

### Driving Adapters (Primary)

Driving adapters call INTO the domain through driving ports. They adapt external input (HTTP requests, CLI commands, message queue events) into domain operations.

**REST Controller Adapter (Java):**

```java
@RestController
@RequestMapping("/api/orders")
public class OrderRestAdapter {

    private final OrderManagement orderManagement;  // Driving port

    public OrderRestAdapter(OrderManagement orderManagement) {
        this.orderManagement = orderManagement;
    }

    @PostMapping
    public ResponseEntity<OrderDto> placeOrder(@RequestBody PlaceOrderRequest req) {
        List<OrderItem> items = req.getItems().stream()
                .map(i -> new OrderItem(i.getProductId(), i.getQuantity()))
                .collect(Collectors.toList());

        Order order = orderManagement.placeOrder(req.getCustomerId(), items);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(OrderDto.from(order));
    }

    @GetMapping("/{id}")
    public ResponseEntity<OrderDto> getOrder(@PathVariable String id) {
        Order order = orderManagement.getOrder(id);
        return ResponseEntity.ok(OrderDto.from(order));
    }
}
```

**CLI Adapter (Python):**

```python
import click

class OrderCliAdapter:
    def __init__(self, order_management: OrderManagement):
        self.order_management = order_management

    def place_order(self, customer_id, product_id, quantity):
        items = [OrderItem(product_id, quantity)]
        order = self.order_management.place_order(customer_id, items)
        print(f"Order placed: {order.id} - Total: ${order.total:.2f}")

    def get_order(self, order_id):
        order = self.order_management.get_order(order_id)
        print(f"Order {order.id}: {order.status} - ${order.total:.2f}")
```

### Driven Adapters (Secondary)

Driven adapters are called BY the domain through driven ports. They adapt domain requests into external operations (database queries, API calls, email sending).

**Database Adapter (Java):**

```java
@Repository
public class PostgresOrderRepository implements OrderRepository {

    private final JdbcTemplate jdbcTemplate;

    public PostgresOrderRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public Order save(Order order) {
        jdbcTemplate.update(
            "INSERT INTO orders (id, customer_id, total, status) VALUES (?, ?, ?, ?)",
            order.getId(), order.getCustomerId(),
            order.getTotal(), order.getStatus().name()
        );
        return order;
    }

    @Override
    public Optional<Order> findById(String id) {
        List<Order> results = jdbcTemplate.query(
            "SELECT * FROM orders WHERE id = ?",
            new Object[]{id},
            (rs, rowNum) -> new Order(
                rs.getString("id"),
                rs.getString("customer_id"),
                rs.getDouble("total"),
                OrderStatus.valueOf(rs.getString("status"))
            )
        );
        return results.stream().findFirst();
    }

    @Override
    public void deleteById(String id) {
        jdbcTemplate.update("DELETE FROM orders WHERE id = ?", id);
    }
}
```

**Email Adapter (Python):**

```python
import smtplib
from email.message import EmailMessage


class SmtpNotificationAdapter(NotificationSender):

    def __init__(self, smtp_host, smtp_port, sender_email):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email

    def send_order_confirmation(self, customer_id, order):
        msg = EmailMessage()
        msg["Subject"] = f"Order Confirmation: {order.id}"
        msg["From"] = self.sender_email
        msg["To"] = self._lookup_email(customer_id)
        msg.set_content(
            f"Your order {order.id} has been placed.\n"
            f"Total: ${order.total:.2f}"
        )
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.send_message(msg)
```

---

## 20.5 The Domain Core

The domain core implements the driving ports and uses the driven ports. It contains entities, use cases, and business rules. It has NO dependency on any framework, database, or external system.

### Domain Core (Java)

```java
// Entity: pure business rules
public class Order {
    private final String id;
    private final String customerId;
    private final List<OrderItem> items;
    private OrderStatus status;
    private double total;

    public Order(String customerId, List<OrderItem> items) {
        this.id = UUID.randomUUID().toString();
        this.customerId = customerId;
        this.items = new ArrayList<>(items);
        this.status = OrderStatus.PENDING;
        this.total = calculateTotal();
    }

    private double calculateTotal() {
        return items.stream()
                .mapToDouble(item -> item.getPrice() * item.getQuantity())
                .sum();
    }

    public void cancel() {
        if (status == OrderStatus.SHIPPED) {
            throw new BusinessException("Cannot cancel a shipped order");
        }
        this.status = OrderStatus.CANCELLED;
    }

    // Getters...
}

// Use case: implements the driving port
public class OrderService implements OrderManagement {

    private final OrderRepository orderRepo;
    private final PaymentGateway paymentGateway;
    private final NotificationSender notifier;

    public OrderService(OrderRepository orderRepo,
                        PaymentGateway paymentGateway,
                        NotificationSender notifier) {
        this.orderRepo = orderRepo;
        this.paymentGateway = paymentGateway;
        this.notifier = notifier;
    }

    @Override
    public Order placeOrder(String customerId, List<OrderItem> items) {
        if (items == null || items.isEmpty()) {
            throw new BusinessException("Order must have at least one item");
        }

        Order order = new Order(customerId, items);
        Money amount = Money.of(order.getTotal(), Currency.USD);

        PaymentResult payment = paymentGateway.charge(customerId, amount);
        if (!payment.isSuccessful()) {
            throw new PaymentFailedException("Payment declined");
        }

        Order saved = orderRepo.save(order);
        notifier.sendOrderConfirmation(customerId, saved);
        return saved;
    }

    @Override
    public Order getOrder(String orderId) {
        return orderRepo.findById(orderId)
                .orElseThrow(() -> new OrderNotFoundException(orderId));
    }

    @Override
    public void cancelOrder(String orderId) {
        Order order = getOrder(orderId);
        order.cancel();
        orderRepo.save(order);
        paymentGateway.refund(order.getPaymentTransactionId());
    }
}
```

### Domain Core (Python)

```python
import uuid
from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class Order:
    def __init__(self, customer_id, items):
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.items = list(items)
        self.status = OrderStatus.PENDING
        self.total = self._calculate_total()

    def _calculate_total(self):
        return sum(item.price * item.quantity for item in self.items)

    def cancel(self):
        if self.status == OrderStatus.SHIPPED:
            raise BusinessError("Cannot cancel a shipped order")
        self.status = OrderStatus.CANCELLED


class OrderService(OrderManagement):

    def __init__(self, order_repo: OrderRepository,
                 payment_gateway: PaymentGateway,
                 notifier: NotificationSender):
        self.order_repo = order_repo
        self.payment_gateway = payment_gateway
        self.notifier = notifier

    def place_order(self, customer_id, items):
        if not items:
            raise BusinessError("Order must have at least one item")

        order = Order(customer_id, items)

        payment = self.payment_gateway.charge(customer_id, order.total)
        if not payment.is_successful:
            raise PaymentFailedError("Payment declined")

        saved = self.order_repo.save(order)
        self.notifier.send_order_confirmation(customer_id, saved)
        return saved

    def get_order(self, order_id):
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        return order

    def cancel_order(self, order_id):
        order = self.get_order(order_id)
        order.cancel()
        self.order_repo.save(order)
        self.payment_gateway.refund(order.payment_transaction_id)
```

Notice: the domain core imports NO framework classes, NO database libraries, NO HTTP utilities. It is pure business logic.

---

## 20.6 Before and After: Refactoring to Hexagonal

### BEFORE: Tightly Coupled (Java)

```java
@Service
public class OrderService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private RestTemplate restTemplate;

    public Map<String, Object> createOrder(Map<String, Object> requestData) {
        String customerId = (String) requestData.get("customerId");
        double amount = (double) requestData.get("amount");

        // Direct database call
        jdbcTemplate.update(
            "INSERT INTO orders (customer_id, amount, status) VALUES (?, ?, 'PENDING')",
            customerId, amount);

        // Direct HTTP call to payment service
        ResponseEntity<String> paymentResponse = restTemplate.postForEntity(
            "https://payments.example.com/charge",
            Map.of("customerId", customerId, "amount", amount),
            String.class);

        if (!paymentResponse.getStatusCode().is2xxSuccessful()) {
            throw new RuntimeException("Payment failed");
        }

        // Direct email via SMTP
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(getCustomerEmail(customerId));
        message.setSubject("Order Confirmation");
        message.setText("Your order for $" + amount + " has been placed.");
        mailSender.send(message);

        return Map.of("status", "created", "amount", amount);
    }
}
```

**Problems with this code:**

- Domain logic is tangled with JDBC, HTTP, and SMTP
- Impossible to test without a real database, payment API, and mail server
- Changing the database requires changing the business logic
- Changing the payment provider requires changing the business logic

### AFTER: Hexagonal Architecture (Java)

```java
// DRIVEN PORT (defined in domain)
public interface OrderRepository {
    Order save(Order order);
}

public interface PaymentGateway {
    PaymentResult charge(String customerId, double amount);
}

public interface NotificationSender {
    void sendConfirmation(String customerId, double amount);
}

// DOMAIN CORE (no external dependencies)
public class OrderService implements OrderManagement {

    private final OrderRepository orderRepo;
    private final PaymentGateway paymentGateway;
    private final NotificationSender notifier;

    public OrderService(OrderRepository orderRepo,
                        PaymentGateway paymentGateway,
                        NotificationSender notifier) {
        this.orderRepo = orderRepo;
        this.paymentGateway = paymentGateway;
        this.notifier = notifier;
    }

    @Override
    public Order placeOrder(String customerId, double amount) {
        PaymentResult payment = paymentGateway.charge(customerId, amount);
        if (!payment.isSuccessful()) {
            throw new PaymentFailedException("Payment declined");
        }

        Order order = new Order(customerId, amount);
        Order saved = orderRepo.save(order);
        notifier.sendConfirmation(customerId, amount);
        return saved;
    }
}

// DRIVEN ADAPTERS (implement ports)
public class JdbcOrderAdapter implements OrderRepository {
    private final JdbcTemplate jdbcTemplate;
    public Order save(Order order) {
        jdbcTemplate.update("INSERT INTO orders ...", ...);
        return order;
    }
}

public class HttpPaymentAdapter implements PaymentGateway {
    private final RestTemplate restTemplate;
    public PaymentResult charge(String customerId, double amount) {
        // HTTP call to payment API
        ...
    }
}

public class SmtpNotificationAdapter implements NotificationSender {
    private final JavaMailSender mailSender;
    public void sendConfirmation(String customerId, double amount) {
        // SMTP email sending
        ...
    }
}
```

---

## 20.7 The Testing Advantage

The greatest practical benefit of hexagonal architecture is testability. Because the domain has no external dependencies, you can test it with simple in-memory implementations.

### Testing the Domain (Java)

```java
class OrderServiceTest {

    private InMemoryOrderRepository orderRepo;
    private FakePaymentGateway paymentGateway;
    private SpyNotificationSender notifier;
    private OrderService orderService;

    @BeforeEach
    void setUp() {
        orderRepo = new InMemoryOrderRepository();
        paymentGateway = new FakePaymentGateway();
        notifier = new SpyNotificationSender();
        orderService = new OrderService(orderRepo, paymentGateway, notifier);
    }

    @Test
    void placeOrder_successfulPayment_savesOrder() {
        paymentGateway.willSucceed();

        Order order = orderService.placeOrder("CUST-1", 99.99);

        assertNotNull(order.getId());
        assertEquals(99.99, order.getTotal(), 0.01);
        assertTrue(orderRepo.contains(order.getId()));
    }

    @Test
    void placeOrder_successfulPayment_sendsNotification() {
        paymentGateway.willSucceed();

        orderService.placeOrder("CUST-1", 99.99);

        assertTrue(notifier.wasCalled());
        assertEquals("CUST-1", notifier.getLastCustomerId());
    }

    @Test
    void placeOrder_failedPayment_throwsException() {
        paymentGateway.willFail();

        assertThrows(PaymentFailedException.class,
            () -> orderService.placeOrder("CUST-1", 99.99));

        assertTrue(orderRepo.isEmpty());
    }

    @Test
    void placeOrder_failedPayment_doesNotSendNotification() {
        paymentGateway.willFail();

        try {
            orderService.placeOrder("CUST-1", 99.99);
        } catch (PaymentFailedException ignored) {}

        assertFalse(notifier.wasCalled());
    }
}

// Test doubles -- simple in-memory implementations
class InMemoryOrderRepository implements OrderRepository {
    private final Map<String, Order> store = new HashMap<>();

    public Order save(Order order) {
        store.put(order.getId(), order);
        return order;
    }
    public boolean contains(String id) { return store.containsKey(id); }
    public boolean isEmpty() { return store.isEmpty(); }
}

class FakePaymentGateway implements PaymentGateway {
    private boolean shouldSucceed = true;

    public void willSucceed() { shouldSucceed = true; }
    public void willFail() { shouldSucceed = false; }

    public PaymentResult charge(String customerId, double amount) {
        return new PaymentResult(shouldSucceed);
    }
}

class SpyNotificationSender implements NotificationSender {
    private boolean called = false;
    private String lastCustomerId;

    public void sendConfirmation(String customerId, double amount) {
        called = true;
        lastCustomerId = customerId;
    }
    public boolean wasCalled() { return called; }
    public String getLastCustomerId() { return lastCustomerId; }
}
```

### Testing the Domain (Python)

```python
import pytest


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self.store = {}

    def save(self, order):
        self.store[order.id] = order
        return order

    def find_by_id(self, order_id):
        return self.store.get(order_id)


class FakePaymentGateway(PaymentGateway):
    def __init__(self, should_succeed=True):
        self.should_succeed = should_succeed

    def charge(self, customer_id, amount):
        return PaymentResult(successful=self.should_succeed)

    def refund(self, transaction_id):
        pass


class SpyNotificationSender(NotificationSender):
    def __init__(self):
        self.calls = []

    def send_order_confirmation(self, customer_id, order):
        self.calls.append((customer_id, order))

    @property
    def was_called(self):
        return len(self.calls) > 0


@pytest.fixture
def order_repo():
    return InMemoryOrderRepository()

@pytest.fixture
def payment_gateway():
    return FakePaymentGateway(should_succeed=True)

@pytest.fixture
def notifier():
    return SpyNotificationSender()

@pytest.fixture
def order_service(order_repo, payment_gateway, notifier):
    return OrderService(order_repo, payment_gateway, notifier)


def test_place_order_saves_order(order_service, order_repo):
    items = [OrderItem("PROD-1", 2, 49.99)]
    order = order_service.place_order("CUST-1", items)

    assert order.id in order_repo.store
    assert order.total == pytest.approx(99.98)


def test_place_order_sends_notification(order_service, notifier):
    items = [OrderItem("PROD-1", 1, 29.99)]
    order_service.place_order("CUST-1", items)

    assert notifier.was_called
    assert notifier.calls[0][0] == "CUST-1"


def test_failed_payment_raises_error(order_repo, notifier):
    failing_gateway = FakePaymentGateway(should_succeed=False)
    service = OrderService(order_repo, failing_gateway, notifier)
    items = [OrderItem("PROD-1", 1, 29.99)]

    with pytest.raises(PaymentFailedError):
        service.place_order("CUST-1", items)

    assert len(order_repo.store) == 0
    assert not notifier.was_called
```

### Testing Comparison

```
  +------------------------------------------------------+
  |                                                       |
  |  LAYERED (tightly coupled)                            |
  |  - Need a running database to test business logic     |
  |  - Need a running payment API to test order flow      |
  |  - Tests take seconds to minutes                      |
  |  - Tests are fragile (external services can be down)  |
  |                                                       |
  |  HEXAGONAL (loosely coupled)                          |
  |  - Test business logic with in-memory fakes           |
  |  - No external services needed                        |
  |  - Tests take milliseconds                            |
  |  - Tests are 100% reliable and repeatable             |
  |                                                       |
  +------------------------------------------------------+
```

---

## 20.8 Project Structure

Here is how a hexagonal architecture project is typically organized:

```
  src/main/java/com/example/orders/
  +-- domain/                        <-- CORE (no external deps)
  |   +-- model/
  |   |   +-- Order.java
  |   |   +-- OrderItem.java
  |   |   +-- OrderStatus.java
  |   +-- port/
  |   |   +-- in/                    <-- Driving ports
  |   |   |   +-- OrderManagement.java
  |   |   +-- out/                   <-- Driven ports
  |   |       +-- OrderRepository.java
  |   |       +-- PaymentGateway.java
  |   |       +-- NotificationSender.java
  |   +-- service/
  |       +-- OrderService.java      <-- Implements driving port
  |
  +-- adapter/                       <-- ADAPTERS (external deps)
      +-- in/                        <-- Driving adapters
      |   +-- rest/
      |   |   +-- OrderRestAdapter.java
      |   |   +-- dto/
      |   |       +-- PlaceOrderRequest.java
      |   |       +-- OrderDto.java
      |   +-- cli/
      |       +-- OrderCliAdapter.java
      +-- out/                       <-- Driven adapters
          +-- persistence/
          |   +-- JdbcOrderAdapter.java
          |   +-- OrderEntity.java
          +-- payment/
          |   +-- HttpPaymentAdapter.java
          +-- notification/
              +-- SmtpNotificationAdapter.java
```

### Python Project Structure

```
  orders/
  +-- domain/                        # CORE
  |   +-- __init__.py
  |   +-- model.py                   # Order, OrderItem, OrderStatus
  |   +-- ports.py                   # All port interfaces
  |   +-- service.py                 # OrderService
  |   +-- exceptions.py              # BusinessError, etc.
  |
  +-- adapters/                      # ADAPTERS
  |   +-- __init__.py
  |   +-- api/
  |   |   +-- rest_adapter.py        # Flask/FastAPI routes
  |   |   +-- dto.py                 # Request/response models
  |   +-- persistence/
  |   |   +-- postgres_adapter.py    # PostgresOrderRepository
  |   |   +-- in_memory_adapter.py   # InMemoryOrderRepository
  |   +-- payment/
  |   |   +-- stripe_adapter.py      # StripePaymentGateway
  |   +-- notification/
  |       +-- email_adapter.py       # SmtpNotificationSender
  |
  +-- config.py                      # Wiring / dependency injection
  +-- main.py                        # Application entry point
```

---

## 20.9 Driving vs Driven: The Complete Picture

```
  +-------------------------------------------------------------------+
  |                                                                    |
  |  DRIVING (Primary)                  DRIVEN (Secondary)            |
  |  "Things that USE the app"          "Things the app USES"         |
  |                                                                    |
  |  - REST API controller              - Database repository         |
  |  - CLI command handler              - Payment API client          |
  |  - Message queue consumer           - Email/SMS sender            |
  |  - Scheduled job trigger            - File storage                |
  |  - gRPC server                      - Message queue producer      |
  |  - Test harness                     - External API client         |
  |                                                                    |
  |  Direction: Outside --> IN           Direction: IN --> Outside     |
  |  Calls domain methods               Called BY domain methods      |
  |                                                                    |
  +-------------------------------------------------------------------+
```

### Both Types of Adapters for the Same Port

A driven port can have multiple adapters, and you choose which one to use at runtime:

```java
// Production configuration
@Configuration
public class ProductionConfig {
    @Bean
    public OrderRepository orderRepository(JdbcTemplate jdbc) {
        return new PostgresOrderAdapter(jdbc);
    }

    @Bean
    public PaymentGateway paymentGateway() {
        return new StripePaymentAdapter("sk_live_xxx");
    }
}

// Test configuration
public class TestConfig {
    public OrderRepository orderRepository() {
        return new InMemoryOrderRepository();
    }

    public PaymentGateway paymentGateway() {
        return new FakePaymentGateway();
    }
}
```

```python
# Production
def create_production_app():
    order_repo = PostgresOrderRepository(connection_string)
    payment = StripePaymentGateway(api_key)
    notifier = SmtpNotificationSender(smtp_config)
    service = OrderService(order_repo, payment, notifier)
    return create_flask_app(service)

# Testing
def create_test_service():
    order_repo = InMemoryOrderRepository()
    payment = FakePaymentGateway(should_succeed=True)
    notifier = SpyNotificationSender()
    return OrderService(order_repo, payment, notifier)
```

---

## 20.10 When to Use Hexagonal Architecture

```
  +------------------------------------------------------+
  |  USE HEXAGONAL WHEN:                                  |
  +------------------------------------------------------+
  |                                                       |
  |  - Business logic is complex and needs isolation      |
  |  - You have multiple input channels (REST + CLI + MQ) |
  |  - You want to swap infrastructure without pain       |
  |  - Testability of business logic is a priority        |
  |  - The project will live for years                    |
  |                                                       |
  +------------------------------------------------------+
  |  USE SIMPLE LAYERED WHEN:                             |
  +------------------------------------------------------+
  |                                                       |
  |  - The project is small with little business logic    |
  |  - There is only one input channel                    |
  |  - The team is new to architecture patterns           |
  |  - The project is a prototype or proof of concept     |
  |  - Time-to-market is more important than flexibility  |
  |                                                       |
  +------------------------------------------------------+
```

---

## Common Mistakes

1. **Putting framework annotations in the domain.** The domain core must have zero framework dependencies. No `@Service`, no `@Autowired`, no `@Entity` from Spring or Django.
2. **Leaking adapter types through ports.** A port should not expose `ResultSet`, `HttpResponse`, or any adapter-specific type. Use domain types only.
3. **Creating too many ports.** Not every method call needs a port. Ports are for boundaries between the domain and the outside world.
4. **Skipping ports for "simple" dependencies.** Even if your repository is simple today, define a port. It costs almost nothing and pays off immediately in testability.
5. **Over-engineering small applications.** A 200-line CRUD app does not need hexagonal architecture. Start with layers and evolve when complexity demands it.

---

## Best Practices

1. **Keep the domain dependency-free.** The domain module should have zero external imports. If you see `import org.springframework` or `import flask` in the domain, something is wrong.
2. **Name ports by domain concept, not technology.** Use `OrderRepository`, not `OrderDatabaseAccess`. Use `NotificationSender`, not `SmtpEmailer`.
3. **Put ports in the domain package.** Ports are defined by the domain, not by the adapters.
4. **Start with one adapter per port.** You can always add more later. The port interface ensures you can.
5. **Test the domain first and most thoroughly.** If your domain is well-tested, the adapters are thin enough to verify with integration tests.

---

## Quick Summary

| Concept | Definition |
|---------|-----------|
| Port | Interface defined by the domain for communication with the outside |
| Driving Port | How the outside world uses the domain (input) |
| Driven Port | What the domain needs from the outside world (output) |
| Driving Adapter | Converts external input into domain calls (controller, CLI) |
| Driven Adapter | Implements domain needs with real infrastructure (database, API) |
| Domain Core | Business logic with zero external dependencies |

---

## Key Points

- Hexagonal architecture puts the domain at the center with no outward dependencies.
- Ports are interfaces defined by the domain. Adapters implement those interfaces using real infrastructure.
- Driving adapters call into the domain. Driven adapters are called by the domain.
- The testing advantage is the primary practical benefit: domain logic can be tested in milliseconds with simple in-memory fakes.
- Hexagonal architecture naturally enforces the Dependency Rule from Clean Architecture.

---

## Practice Questions

1. What is the fundamental difference between a port and an adapter? Which one lives in the domain and which one lives outside?

2. A `PaymentService` in the domain directly imports `com.stripe.Stripe`. Does this violate hexagonal architecture? How would you fix it?

3. You need to support both REST and GraphQL for your application. How does hexagonal architecture make this easier compared to layered architecture?

4. Your team has a `UserRepository` interface and a `PostgresUserRepository` implementation. A new requirement says you also need to cache users in Redis. How would you add this in a hexagonal architecture?

5. Explain why hexagonal architecture makes it easier to follow Test-Driven Development (Chapter 17). How do ports help with the RED phase?

---

## Exercises

### Exercise 1: Identify Ports and Adapters

Given this requirement: "A library system where users can borrow and return books. Overdue books incur a fine. Users receive email notifications for due dates."

Identify:
- All driving ports (what the system offers)
- All driven ports (what the system needs)
- At least two driving adapters and three driven adapters

Draw the hexagon diagram with your identified components.

### Exercise 2: Refactor to Hexagonal

Take this tightly coupled code and refactor it to hexagonal architecture:

```python
import sqlite3
import requests

class BookingService:
    def __init__(self):
        self.db = sqlite3.connect("bookings.db")

    def create_booking(self, user_id, room_id, date):
        # Check availability directly in database
        cursor = self.db.execute(
            "SELECT count(*) FROM bookings WHERE room_id=? AND date=?",
            (room_id, date))
        if cursor.fetchone()[0] > 0:
            raise ValueError("Room not available")

        # Save booking directly
        self.db.execute(
            "INSERT INTO bookings (user_id, room_id, date) VALUES (?, ?, ?)",
            (user_id, room_id, date))
        self.db.commit()

        # Send notification via external API
        requests.post("https://api.notify.com/send", json={
            "user_id": user_id,
            "message": f"Booking confirmed for room {room_id} on {date}"
        })
```

Create: domain model, driven ports, domain service, and adapter stubs.

### Exercise 3: Test the Domain

Using the code you created in Exercise 2, write a complete test suite for the domain service using in-memory fakes. Cover:
- Successful booking
- Room not available
- Notification sent on success
- Notification NOT sent on failure

---

## What Is Next?

Hexagonal architecture gives your application a clean separation between domain logic and infrastructure. The next chapters explore additional architectural patterns that build on these same principles: Onion Architecture (Chapter 21) adds more granularity to the domain layers, and Domain-Driven Design (Chapter 22) provides a rich set of patterns for modeling complex business domains within these architectural boundaries.
