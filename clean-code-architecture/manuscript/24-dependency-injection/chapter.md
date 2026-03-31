# Chapter 24: Dependency Injection

## What You Will Learn

- What Dependency Injection (DI) is and why it is essential for clean, testable code
- The three types of injection: constructor, setter, and interface injection
- Why constructor injection is the preferred approach
- How DI containers work in Spring (Java) and Python (dependency-injector)
- Why the Service Locator is an anti-pattern
- How DI transforms untestable code into easily testable code
- Practical before-and-after refactoring examples

## Why This Chapter Matters

Imagine you are building a house. Every room has its own plumbing, electrical wiring, and ventilation. Now imagine that every room manufactures its own pipes, wires, and fans from raw materials. That would be absurd -- rooms should receive the infrastructure they need, not build it themselves.

Yet this is exactly what most beginners do in code. Classes create their own dependencies using `new` -- they manufacture the objects they need instead of receiving them. This makes testing impossible (you cannot substitute a fake database), changes expensive (swapping implementations requires editing every class), and the code rigid.

Dependency Injection says: **a class should receive its dependencies from the outside, not create them itself.** This one principle transforms code from rigid and untestable to flexible and clean.

If you have ever struggled to write a unit test because the class you are testing creates a real database connection inside itself, Dependency Injection is the solution.

---

## The Problem: Hard-Coded Dependencies

Look at this common pattern in beginner code:

### Java -- Before (Hard-Coded Dependencies)

```java
// BAD: OrderService creates its own dependencies
public class OrderService {

    // Hard-coded dependency -- created inside the class
    private final OrderRepository repository = new MySqlOrderRepository();
    private final EmailService emailService = new SmtpEmailService();
    private final PaymentGateway paymentGateway = new StripePaymentGateway();

    public void placeOrder(Order order) {
        paymentGateway.charge(order.getCustomerId(), order.getTotal());
        repository.save(order);
        emailService.sendConfirmation(order.getCustomerId(), order.getId());
    }
}
```

### Python -- Before (Hard-Coded Dependencies)

```python
# BAD: OrderService creates its own dependencies
class OrderService:
    def __init__(self):
        # Hard-coded dependencies -- created inside the class
        self.repository = MySqlOrderRepository()
        self.email_service = SmtpEmailService()
        self.payment_gateway = StripePaymentGateway()

    def place_order(self, order):
        self.payment_gateway.charge(order.customer_id, order.total)
        self.repository.save(order)
        self.email_service.send_confirmation(order.customer_id, order.id)
```

### What Is Wrong With This?

```
PROBLEMS WITH HARD-CODED DEPENDENCIES:

  1. UNTESTABLE
     +-------------------+
     | OrderService      |
     |  creates          |
     |  +-------------+  |    To test OrderService, you MUST
     |  | Real MySQL  |  |    have a running MySQL database,
     |  | Database    |  |    a working SMTP server, and a
     |  +-------------+  |    valid Stripe account.
     |  +-------------+  |
     |  | Real SMTP   |  |    That is not a unit test.
     |  | Server      |  |    That is an integration test.
     |  +-------------+  |
     |  +-------------+  |
     |  | Real Stripe |  |
     |  | Gateway     |  |
     |  +-------------+  |
     +-------------------+

  2. RIGID
     Swapping MySQL for PostgreSQL requires editing OrderService.
     Swapping Stripe for PayPal requires editing OrderService.
     Every change ripples through the codebase.

  3. VIOLATES DEPENDENCY INVERSION
     High-level policy (OrderService) depends on
     low-level details (MySqlOrderRepository).
```

---

## The Solution: Dependency Injection

Dependency Injection means passing dependencies to a class from the outside, rather than having the class create them internally.

### Java -- After (Constructor Injection)

```java
// GOOD: Dependencies are injected through the constructor
public class OrderService {

    private final OrderRepository repository;
    private final EmailService emailService;
    private final PaymentGateway paymentGateway;

    // Dependencies come IN through the constructor
    public OrderService(OrderRepository repository,
                        EmailService emailService,
                        PaymentGateway paymentGateway) {
        this.repository = repository;
        this.emailService = emailService;
        this.paymentGateway = paymentGateway;
    }

    public void placeOrder(Order order) {
        paymentGateway.charge(order.getCustomerId(), order.getTotal());
        repository.save(order);
        emailService.sendConfirmation(order.getCustomerId(), order.getId());
    }
}
```

### Python -- After (Constructor Injection)

```python
# GOOD: Dependencies are injected through the constructor
class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        email_service: EmailService,
        payment_gateway: PaymentGateway,
    ):
        # Dependencies come IN through the constructor
        self.repository = repository
        self.email_service = email_service
        self.payment_gateway = payment_gateway

    def place_order(self, order):
        self.payment_gateway.charge(order.customer_id, order.total)
        self.repository.save(order)
        self.email_service.send_confirmation(order.customer_id, order.id)
```

### What Changed?

```
BEFORE vs AFTER:

  BEFORE (Hard-coded):            AFTER (Injected):

  +-------------------+           +-------------------+
  | OrderService      |           | OrderService      |
  |  CREATES:         |           |  RECEIVES:        |
  |  MySqlRepo        |           |  OrderRepository  | <-- interface
  |  SmtpEmail        |           |  EmailService     | <-- interface
  |  StripeGateway    |           |  PaymentGateway   | <-- interface
  +-------------------+           +-------------------+
                                        ^   ^   ^
                                        |   |   |
  The class knows                  Caller provides
  exactly which                    any implementation
  implementations                  that fits the
  it uses.                         interface.
```

---

## Types of Dependency Injection

### 1. Constructor Injection (Preferred)

Dependencies are provided through the constructor. The object cannot be created without all its dependencies.

```java
// CONSTRUCTOR INJECTION -- the gold standard
public class NotificationService {

    private final EmailSender emailSender;
    private final SmsSender smsSender;

    // All dependencies declared upfront. Cannot create the object without them.
    public NotificationService(EmailSender emailSender, SmsSender smsSender) {
        this.emailSender = Objects.requireNonNull(emailSender);
        this.smsSender = Objects.requireNonNull(smsSender);
    }

    public void notify(User user, String message) {
        if (user.prefersEmail()) {
            emailSender.send(user.getEmail(), message);
        } else {
            smsSender.send(user.getPhone(), message);
        }
    }
}
```

```python
# CONSTRUCTOR INJECTION -- the gold standard
class NotificationService:
    def __init__(self, email_sender: EmailSender, sms_sender: SmsSender):
        if email_sender is None or sms_sender is None:
            raise ValueError("Dependencies cannot be None")
        self.email_sender = email_sender
        self.sms_sender = sms_sender

    def notify(self, user, message: str) -> None:
        if user.prefers_email:
            self.email_sender.send(user.email, message)
        else:
            self.sms_sender.send(user.phone, message)
```

**Why constructor injection is preferred:**

- **Completeness.** The object is fully initialized after construction. No half-created objects.
- **Immutability.** Dependencies can be final/readonly. They never change after creation.
- **Visibility.** All dependencies are declared in one place -- the constructor signature.
- **Fail fast.** Missing dependencies cause an error at construction time, not at runtime.

### 2. Setter Injection

Dependencies are provided through setter methods after construction. The object can exist without all dependencies set.

```java
// SETTER INJECTION -- use only for optional dependencies
public class ReportGenerator {

    private ReportFormatter formatter;  // Optional dependency

    // Required dependency via constructor
    private final DataSource dataSource;

    public ReportGenerator(DataSource dataSource) {
        this.dataSource = dataSource;
        this.formatter = new DefaultFormatter();  // sensible default
    }

    // Optional: caller can override the default formatter
    public void setFormatter(ReportFormatter formatter) {
        this.formatter = formatter;
    }

    public Report generate() {
        Data data = dataSource.fetch();
        return formatter.format(data);
    }
}
```

```python
# SETTER INJECTION -- use only for optional dependencies
class ReportGenerator:
    def __init__(self, data_source: DataSource):
        self.data_source = data_source               # required
        self.formatter = DefaultFormatter()           # sensible default

    def set_formatter(self, formatter: ReportFormatter):
        """Optional: override the default formatter."""
        self.formatter = formatter

    def generate(self) -> Report:
        data = self.data_source.fetch()
        return self.formatter.format(data)
```

**When to use setter injection:**
- The dependency is truly optional and has a sensible default.
- The dependency may need to change after construction (rare).

**Risks of setter injection:**
- Object may be used before all dependencies are set.
- Dependencies are mutable, which can lead to bugs.
- Harder to reason about the object's state.

### 3. Interface Injection

The dependency provides an injector method that the client must implement. This is rarely used in modern code.

```java
// INTERFACE INJECTION -- rarely used, shown for completeness
public interface LoggerAware {
    void setLogger(Logger logger);
}

public class UserService implements LoggerAware {
    private Logger logger;

    @Override
    public void setLogger(Logger logger) {
        this.logger = logger;
    }
}
```

---

## Comparison of Injection Types

```
INJECTION TYPE COMPARISON:

  +-------------------+------------+-----------+-------------+
  | Criteria          | Constructor| Setter    | Interface   |
  +-------------------+------------+-----------+-------------+
  | Completeness      | YES        | NO        | NO          |
  | Immutability      | YES        | NO        | NO          |
  | Required deps     | CLEAR      | UNCLEAR   | UNCLEAR     |
  | Optional deps     | AWKWARD    | GOOD      | AWKWARD     |
  | Testability       | EXCELLENT  | GOOD      | GOOD        |
  | Recommended       | DEFAULT    | SOMETIMES | RARELY      |
  +-------------------+------------+-----------+-------------+

  Rule of thumb:
  - Use CONSTRUCTOR injection for required dependencies (90% of cases)
  - Use SETTER injection for optional dependencies (10% of cases)
  - Avoid interface injection
```

---

## The Testing Benefit

The single biggest benefit of Dependency Injection is testability. When dependencies are injected, you can substitute fakes, mocks, or stubs during testing.

### Java -- Testing with Injected Dependencies

```java
// BEFORE DI: Testing is nearly impossible
// You would need a real MySQL database, SMTP server, and Stripe account

// AFTER DI: Testing is trivial
class OrderServiceTest {

    @Test
    void placeOrder_chargesPaymentAndSavesOrder() {
        // Create test doubles
        FakeOrderRepository fakeRepo = new FakeOrderRepository();
        FakeEmailService fakeEmail = new FakeEmailService();
        FakePaymentGateway fakePayment = new FakePaymentGateway();

        // Inject test doubles
        OrderService service = new OrderService(fakeRepo, fakeEmail, fakePayment);

        // Act
        Order order = new Order("customer-1", List.of(
            new OrderItem("widget", 2, Money.of(10))
        ));
        service.placeOrder(order);

        // Assert
        assertTrue(fakePayment.wasCharged("customer-1", Money.of(20)));
        assertTrue(fakeRepo.wasSaved(order));
        assertTrue(fakeEmail.wasSentTo("customer-1"));
    }
}

// Simple fake for testing -- no framework needed
class FakeOrderRepository implements OrderRepository {
    private final List<Order> saved = new ArrayList<>();

    @Override
    public void save(Order order) {
        saved.add(order);
    }

    public boolean wasSaved(Order order) {
        return saved.contains(order);
    }
}
```

### Python -- Testing with Injected Dependencies

```python
# AFTER DI: Testing is trivial
def test_place_order_charges_payment_and_saves():
    # Create test doubles
    fake_repo = FakeOrderRepository()
    fake_email = FakeEmailService()
    fake_payment = FakePaymentGateway()

    # Inject test doubles
    service = OrderService(fake_repo, fake_email, fake_payment)

    # Act
    order = Order(customer_id="customer-1", items=[
        OrderItem("widget", quantity=2, unit_price=10.0)
    ])
    service.place_order(order)

    # Assert
    assert fake_payment.was_charged("customer-1", 20.0)
    assert fake_repo.was_saved(order)
    assert fake_email.was_sent_to("customer-1")


# Simple fake for testing
class FakeOrderRepository:
    def __init__(self):
        self.saved_orders = []

    def save(self, order):
        self.saved_orders.append(order)

    def was_saved(self, order) -> bool:
        return order in self.saved_orders
```

```
TESTING WITHOUT DI vs WITH DI:

  WITHOUT DI:                       WITH DI:
  +-------------------+             +-------------------+
  | Test              |             | Test              |
  | +---------------+ |             | +---------------+ |
  | | OrderService  | |             | | OrderService  | |
  | | +---+---+---+ | |             | +---+-----------+ |
  | | |DB |SMTP|$$| | |             |     |   |   |     |
  | | +---+---+---+ | |             |  +--+  ++-+ +--+  |
  | +---------------+ |             |  |Fake||Fake||Fake| |
  +-------------------+             |  |Repo||Mail||Pay | |
                                    |  +----++----++----+ |
  Requires:                         +-------------------+
  - Running database
  - Running mail server              Requires:
  - Payment API credentials          - Nothing! Just objects.
  - Network access
  - Minutes to run                    Runs in milliseconds.
```

---

## DI Containers

In a small application, you can wire dependencies manually. But as the application grows, manual wiring becomes tedious. DI containers automate the wiring.

### Spring Framework (Java)

Spring is the most popular DI container in Java. It can automatically discover and inject dependencies.

```java
// Step 1: Define your interfaces
public interface OrderRepository {
    void save(Order order);
    Optional<Order> findById(String id);
}

public interface EmailService {
    void sendConfirmation(String customerId, String orderId);
}

// Step 2: Implement them and mark as Spring components
@Repository  // Tells Spring: "This is a bean, manage it for me"
public class JpaOrderRepository implements OrderRepository {
    @Override
    public void save(Order order) {
        // JPA implementation
    }

    @Override
    public Optional<Order> findById(String id) {
        // JPA implementation
        return Optional.empty();
    }
}

@Component
public class SmtpEmailService implements EmailService {
    @Override
    public void sendConfirmation(String customerId, String orderId) {
        // SMTP implementation
    }
}

// Step 3: Declare dependencies via constructor -- Spring injects automatically
@Service
public class OrderService {

    private final OrderRepository repository;
    private final EmailService emailService;

    // Spring sees this constructor and automatically injects
    // the matching beans (JpaOrderRepository, SmtpEmailService)
    public OrderService(OrderRepository repository,
                        EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
    }

    public void placeOrder(Order order) {
        repository.save(order);
        emailService.sendConfirmation(order.getCustomerId(), order.getId());
    }
}
```

```
HOW SPRING DI WORKS:

  1. Application starts
  2. Spring scans for @Component, @Service, @Repository, etc.
  3. Spring creates instances (beans) of each
  4. Spring looks at constructors and matches parameters to beans
  5. Spring injects the matching beans automatically

  +------------------+
  | Spring Container |
  |                  |
  | Beans:           |     OrderService needs OrderRepository?
  | - JpaOrderRepo   |---> Here, take JpaOrderRepo.
  | - SmtpEmailSvc   |
  | - OrderService   |     OrderService needs EmailService?
  |                  |---> Here, take SmtpEmailSvc.
  +------------------+
```

### Python Dependency Injection

Python has several approaches. Here is a clean pattern using `dependency-injector`:

```python
# Approach 1: Manual wiring (good for small apps)
def create_app():
    """Composition root: wire everything together in one place."""
    # Create implementations
    repository = PostgresOrderRepository(connection_string="...")
    email_service = SmtpEmailService(smtp_host="mail.example.com")
    payment_gateway = StripePaymentGateway(api_key="...")

    # Wire them together
    order_service = OrderService(
        repository=repository,
        email_service=email_service,
        payment_gateway=payment_gateway,
    )

    return Application(order_service=order_service)


# Approach 2: Using dependency-injector library
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    """DI Container: defines how to create and wire objects."""

    config = providers.Configuration()

    # Infrastructure
    order_repository = providers.Singleton(
        PostgresOrderRepository,
        connection_string=config.db.connection_string,
    )

    email_service = providers.Singleton(
        SmtpEmailService,
        smtp_host=config.email.smtp_host,
    )

    payment_gateway = providers.Singleton(
        StripePaymentGateway,
        api_key=config.payment.api_key,
    )

    # Application services -- automatically wired
    order_service = providers.Factory(
        OrderService,
        repository=order_repository,
        email_service=email_service,
        payment_gateway=payment_gateway,
    )


# Usage
container = Container()
container.config.from_yaml("config.yml")

order_service = container.order_service()
order_service.place_order(order)

# For testing: override specific dependencies
with container.order_repository.override(FakeOrderRepository()):
    test_service = container.order_service()
    # test_service uses FakeOrderRepository but real email and payment
```

### Python with FastAPI

```python
# FastAPI has built-in dependency injection
from fastapi import Depends, FastAPI

app = FastAPI()

def get_repository() -> OrderRepository:
    return PostgresOrderRepository(connection_string="...")

def get_email_service() -> EmailService:
    return SmtpEmailService(smtp_host="mail.example.com")

def get_order_service(
    repo: OrderRepository = Depends(get_repository),
    email: EmailService = Depends(get_email_service),
) -> OrderService:
    return OrderService(repository=repo, email_service=email)


@app.post("/orders")
def create_order(
    order_data: OrderRequest,
    service: OrderService = Depends(get_order_service),
):
    service.place_order(order_data.to_order())
    return {"status": "created"}


# Testing: override dependencies
def test_create_order():
    app.dependency_overrides[get_repository] = lambda: FakeOrderRepository()
    app.dependency_overrides[get_email_service] = lambda: FakeEmailService()

    client = TestClient(app)
    response = client.post("/orders", json={"item": "widget", "qty": 1})
    assert response.status_code == 200

    app.dependency_overrides.clear()
```

---

## The Service Locator Anti-Pattern

The Service Locator pattern looks like it solves the same problem as DI, but it introduces hidden dependencies and makes code harder to understand and test.

```java
// SERVICE LOCATOR ANTI-PATTERN
// Dependencies are HIDDEN -- you cannot see them from the constructor

public class OrderService {

    public void placeOrder(Order order) {
        // Dependencies are fetched from a global registry
        OrderRepository repo = ServiceLocator.get(OrderRepository.class);
        EmailService email = ServiceLocator.get(EmailService.class);
        PaymentGateway payment = ServiceLocator.get(PaymentGateway.class);

        payment.charge(order.getCustomerId(), order.getTotal());
        repo.save(order);
        email.sendConfirmation(order.getCustomerId(), order.getId());
    }
}
```

```python
# SERVICE LOCATOR ANTI-PATTERN
class OrderService:
    def place_order(self, order):
        # Dependencies are HIDDEN inside the method
        repo = ServiceLocator.get(OrderRepository)
        email = ServiceLocator.get(EmailService)
        payment = ServiceLocator.get(PaymentGateway)

        payment.charge(order.customer_id, order.total)
        repo.save(order)
        email.send_confirmation(order.customer_id, order.id)
```

### Why Service Locator Is an Anti-Pattern

```
SERVICE LOCATOR vs DEPENDENCY INJECTION:

  SERVICE LOCATOR:                  DEPENDENCY INJECTION:

  class OrderService:               class OrderService:
      def place_order(self):            def __init__(self, repo, email):
          repo = SL.get(Repo)               self.repo = repo
          email = SL.get(Email)             self.email = email
          ...                           ...

  Problems:                         Benefits:
  +-------------------------------+ +-------------------------------+
  | 1. Hidden dependencies        | | 1. Explicit dependencies      |
  |    Cannot see what the class  | |    Constructor tells you       |
  |    needs without reading the  | |    exactly what is needed.     |
  |    method body.               | |                               |
  |                               | |                               |
  | 2. Global mutable state       | | 2. No global state            |
  |    ServiceLocator is a global | |    Dependencies are local      |
  |    registry that any code     | |    to each object.             |
  |    can modify.                | |                               |
  |                               | |                               |
  | 3. Hard to test               | | 3. Easy to test               |
  |    Must configure the global  | |    Just pass test doubles     |
  |    locator before every test. | |    to the constructor.         |
  |                               | |                               |
  | 4. Runtime errors             | | 4. Compile-time safety        |
  |    Fails at runtime if a      | |    Missing dependency is a    |
  |    service is not registered. | |    compile error (or TypeError)|
  +-------------------------------+ +-------------------------------+
```

---

## The Composition Root

Where do you actually create and wire all the dependencies? In a single place called the **Composition Root** -- the entry point of your application.

```java
// COMPOSITION ROOT: Wire everything together at the application entry point
public class Application {

    public static void main(String[] args) {
        // Create implementations
        OrderRepository repo = new JpaOrderRepository(dataSource());
        EmailService email = new SmtpEmailService("mail.example.com");
        PaymentGateway payment = new StripePaymentGateway(apiKey());

        // Wire them together
        OrderService orderService = new OrderService(repo, email, payment);
        OrderController controller = new OrderController(orderService);

        // Start the application
        WebServer server = new WebServer(controller);
        server.start(8080);
    }
}
```

```python
# COMPOSITION ROOT: Wire everything together at the application entry point
def main():
    # Create implementations
    repo = PostgresOrderRepository(connection_string=os.getenv("DB_URL"))
    email = SmtpEmailService(smtp_host=os.getenv("SMTP_HOST"))
    payment = StripePaymentGateway(api_key=os.getenv("STRIPE_KEY"))

    # Wire them together
    order_service = OrderService(
        repository=repo,
        email_service=email,
        payment_gateway=payment,
    )

    # Start the application
    app = create_web_app(order_service=order_service)
    app.run(port=8080)


if __name__ == "__main__":
    main()
```

```
THE COMPOSITION ROOT PRINCIPLE:

  +-----------------------------------------------------+
  |                                                     |
  |  Application Entry Point (Composition Root)          |
  |                                                     |
  |  Creates: Repo, EmailSvc, PaymentGw                 |
  |  Wires:   OrderService(Repo, EmailSvc, PaymentGw)   |
  |  Starts:  WebServer(OrderController(OrderService))   |
  |                                                     |
  +-----------------------------------------------------+
       |            |              |
       v            v              v
  +---------+  +---------+   +---------+
  | Repo    |  | Email   |   | Payment |
  +---------+  +---------+   +---------+

  Rule: Dependency creation happens in ONE place.
        All other code receives its dependencies.
```

---

## Common Mistakes

### Mistake 1: Too Many Constructor Parameters

If your constructor takes more than 4-5 parameters, your class probably does too much. This is a signal to split the class.

```java
// BAD: Too many dependencies = too many responsibilities
public class OrderService(
    OrderRepository repo,
    EmailService email,
    PaymentGateway payment,
    InventoryService inventory,
    TaxCalculator tax,
    ShippingCalculator shipping,
    AuditLogger audit,
    NotificationService notifications,
    DiscountEngine discounts
) { ... }

// GOOD: Split into focused classes
public class OrderPlacer(OrderRepository repo, PaymentGateway payment) { ... }
public class OrderNotifier(EmailService email, NotificationService notif) { ... }
public class OrderPricer(TaxCalculator tax, DiscountEngine discounts) { ... }
```

### Mistake 2: Injecting the Container Itself

Never inject the DI container into a class. That is just a Service Locator in disguise.

```java
// BAD: Injecting the container
public class OrderService {
    private final ApplicationContext context;  // Spring container

    public OrderService(ApplicationContext context) {
        this.context = context;
    }

    public void placeOrder(Order order) {
        // This is a Service Locator!
        OrderRepository repo = context.getBean(OrderRepository.class);
    }
}

// GOOD: Inject the actual dependencies
public class OrderService {
    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }
}
```

### Mistake 3: Using `new` for Services Inside Business Logic

If you use `new` to create a service (not a value object or data structure), you are creating a hard-coded dependency.

```python
# BAD: Creating services with new inside business logic
class OrderService:
    def place_order(self, order):
        validator = OrderValidator()           # Hard-coded!
        pricer = PricingEngine()               # Hard-coded!
        validator.validate(order)
        total = pricer.calculate(order)

# GOOD: Inject the services
class OrderService:
    def __init__(self, validator: OrderValidator, pricer: PricingEngine):
        self.validator = validator
        self.pricer = pricer

    def place_order(self, order):
        self.validator.validate(order)
        total = self.pricer.calculate(order)
```

### Mistake 4: Circular Dependencies

If A depends on B and B depends on A, you have a design problem. DI will expose this, which is a feature, not a bug.

**Fix:** Extract the shared logic into a third class that both A and B depend on.

---

## Best Practices

1. **Use constructor injection for required dependencies.** Make them final/readonly. This is the default choice.
2. **Use setter injection only for optional dependencies** with sensible defaults.
3. **Program to interfaces, not implementations.** Inject `OrderRepository`, not `MySqlOrderRepository`.
4. **Keep constructors simple.** No logic, no computation -- just assignment.
5. **Wire everything in the Composition Root.** One place for all dependency creation.
6. **Avoid the Service Locator pattern.** It hides dependencies and makes code harder to understand.
7. **Watch for too many constructor parameters.** More than 4-5 means your class has too many responsibilities.
8. **Never inject the DI container itself.** That is a Service Locator in disguise.

---

## Quick Summary

```
DEPENDENCY INJECTION AT A GLANCE:

  What:    Providing dependencies from outside rather than
           creating them inside a class.

  Why:     Makes code testable, flexible, and loosely coupled.

  How:     Constructor injection (preferred), setter injection
           (optional deps), DI containers (Spring, dependency-injector).

  +---------------------------+-------------------------------+
  | WITHOUT DI                | WITH DI                       |
  +---------------------------+-------------------------------+
  | Class creates deps        | Class receives deps           |
  | Rigid, tightly coupled    | Flexible, loosely coupled     |
  | Hard to test              | Easy to test with fakes       |
  | Changes ripple everywhere | Changes are local             |
  | new MySqlRepo() inside    | OrderRepository interface     |
  +---------------------------+-------------------------------+
```

---

## Key Points

- Dependency Injection means receiving dependencies from outside rather than creating them with `new` inside the class.
- Constructor injection is the preferred method: it makes dependencies explicit, required, and immutable.
- Setter injection is for optional dependencies that have sensible defaults.
- DI containers (Spring, dependency-injector, FastAPI Depends) automate wiring but are not required for small apps.
- The Service Locator pattern is an anti-pattern because it hides dependencies and introduces global state.
- The Composition Root is the single place in your application where all dependencies are created and wired together.
- Too many constructor parameters signal that your class has too many responsibilities and should be split.
- The biggest benefit of DI is testability: you can substitute fakes and mocks without changing production code.

---

## Practice Questions

1. What is the key difference between Dependency Injection and the Service Locator pattern? Why is the Service Locator considered an anti-pattern?

2. A class has a constructor with eight parameters. What does this tell you about the class design, and what would you do to fix it?

3. When would you use setter injection instead of constructor injection? Give a concrete example.

4. Explain what a Composition Root is and why all dependency wiring should happen there. What problems arise if you scatter `new` calls throughout your codebase?

5. You are reviewing code that uses `@Autowired` on a private field in a Spring application (field injection). Why is this problematic, and what would you recommend instead?

---

## Exercises

### Exercise 1: Refactor to Use DI

Refactor the following class to use constructor injection. Create the necessary interfaces and write a unit test using fake implementations.

```java
public class UserRegistrationService {
    private final UserDatabase db = new MySqlUserDatabase();
    private final PasswordHasher hasher = new BcryptPasswordHasher();
    private final WelcomeEmailSender sender = new SmtpWelcomeEmailSender();

    public void register(String email, String password) {
        if (db.findByEmail(email) != null) {
            throw new EmailAlreadyExistsException(email);
        }
        String hashed = hasher.hash(password);
        db.save(new User(email, hashed));
        sender.sendWelcome(email);
    }
}
```

### Exercise 2: Build a Composition Root

Create a Composition Root for a simple blogging application with these components: `PostService` (depends on `PostRepository` and `NotificationService`), `PostRepository` (depends on `DatabaseConnection`), `NotificationService` (depends on `EmailSender`). Wire everything together manually, then show how you would override `EmailSender` for testing.

### Exercise 3: Identify the Anti-Pattern

The following code uses a DI container but still has a problem. Identify the anti-pattern and fix it.

```python
class ReportService:
    def __init__(self, container):
        self.container = container

    def generate_report(self, report_type):
        if report_type == "sales":
            repo = self.container.get(SalesRepository)
            formatter = self.container.get(SalesFormatter)
        elif report_type == "inventory":
            repo = self.container.get(InventoryRepository)
            formatter = self.container.get(InventoryFormatter)
        data = repo.fetch_all()
        return formatter.format(data)
```

---

## What Is Next?

Now that you know how to inject dependencies cleanly, the next chapter -- Design for Change -- explores how to build software that anticipates and accommodates change. You will learn about abstraction boundaries, feature flags, the strategy pattern, and how to balance flexibility with simplicity.
