# Chapter 18: Clean Architecture Introduction -- Separating What Matters

## What You Will Learn

- What software architecture means and why it matters for every developer
- The principle of Separation of Concerns and how it shapes good architecture
- Why business rules should be independent of frameworks, databases, and UIs
- The Dependency Rule and why dependencies must always point inward
- Uncle Bob's Clean Architecture with its concentric circles
- How to read and apply the Clean Architecture diagram to real projects

## Why This Chapter Matters

You can write perfectly clean functions, well-named classes, and comprehensive tests -- and still end up with an application that is painful to change. Why? Because the architecture is tangled. Your business rules depend on your database. Your database schema is embedded in your UI. Changing one thing means changing everything. Clean Architecture solves this by giving you a simple rule: separate your code into layers, and make sure dependencies always point inward toward your business rules. The result is a system where you can swap frameworks, change databases, and rewrite UIs without touching the core logic.

---

## 18.1 What Is Software Architecture?

Software architecture is the set of decisions about how your code is organized into components, how those components communicate, and which components depend on which.

```
  +-------------------------------------------------------+
  |            ARCHITECTURE IS ABOUT BOUNDARIES            |
  +-------------------------------------------------------+
  |                                                        |
  |  Which code knows about which other code?              |
  |  What can change without affecting other parts?        |
  |  Where do you draw the lines between components?       |
  |                                                        |
  +-------------------------------------------------------+
```

### Architecture Is Not About Tools

A common misconception: "Our architecture is Spring Boot + PostgreSQL + React."

Those are tools, not architecture. Architecture is about how your code is structured so that:

- **Business rules** do not depend on the UI framework
- **Use cases** do not depend on the database
- **Core logic** can be tested without starting a web server

### The Cost of Bad Architecture

```
  Cost of Change
  ^
  |            ___________
  |           /            Bad Architecture
  |          /
  |         /
  |        /
  |   ____/
  |  /
  | /     ______________ Good Architecture
  |/______/
  +-------------------------> Time
```

With bad architecture, every change gets more expensive over time. With good architecture, the cost of change stays relatively flat.

---

## 18.2 Separation of Concerns

The most fundamental principle of architecture: every piece of code should have one reason to exist, and different concerns should live in different places.

### What Are "Concerns"?

```
  +-----------------------------------------------------------+
  |                    COMMON CONCERNS                         |
  +-----------------------------------------------------------+
  |                                                            |
  |  Business logic     What the application does              |
  |  Persistence        How data is stored and retrieved       |
  |  Presentation       How data is shown to the user          |
  |  Communication      How systems talk to each other         |
  |  Security           Who can do what                        |
  |  Logging            What happened and when                 |
  |                                                            |
  +-----------------------------------------------------------+
```

### BEFORE: Concerns Mixed Together (Java)

```java
public class OrderController {

    @PostMapping("/orders")
    public ResponseEntity<String> createOrder(@RequestBody OrderRequest req) {
        // Validation (business logic)
        if (req.getItems().isEmpty()) {
            return ResponseEntity.badRequest().body("No items");
        }

        // Business rule (business logic)
        double total = 0;
        for (Item item : req.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        if (total > 10000) {
            total *= 0.95; // 5% discount for large orders
        }

        // Persistence (data access)
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/shop");
        PreparedStatement stmt = conn.prepareStatement(
            "INSERT INTO orders (customer_id, total) VALUES (?, ?)");
        stmt.setInt(1, req.getCustomerId());
        stmt.setDouble(2, total);
        stmt.executeUpdate();

        // Notification (external service)
        HttpClient client = HttpClient.newHttpClient();
        client.send(HttpRequest.newBuilder()
            .uri(URI.create("https://api.email.com/send"))
            .POST(HttpRequest.BodyPublishers.ofString(
                "{\"to\":\"" + req.getEmail() + "\",\"subject\":\"Order Placed\"}"))
            .build(), HttpResponse.BodyHandlers.ofString());

        // Presentation (response formatting)
        return ResponseEntity.ok("{\"status\":\"created\",\"total\":" + total + "}");
    }
}
```

This single method handles validation, business rules, database access, external API calls, and response formatting. Changing any one concern risks breaking the others.

### AFTER: Concerns Separated (Java)

```java
// Business logic -- no framework dependencies
public class OrderService {
    private final OrderRepository orderRepo;
    private final NotificationService notifier;

    public Order createOrder(int customerId, List<Item> items) {
        if (items.isEmpty()) {
            throw new ValidationException("No items in order");
        }
        double total = calculateTotal(items);
        Order order = orderRepo.save(new Order(customerId, total));
        notifier.orderCreated(order);
        return order;
    }

    private double calculateTotal(List<Item> items) {
        double total = items.stream()
            .mapToDouble(i -> i.getPrice() * i.getQuantity())
            .sum();
        if (total > 10000) {
            total *= 0.95;
        }
        return total;
    }
}

// Presentation -- only handles HTTP concerns
@RestController
public class OrderController {
    private final OrderService orderService;

    @PostMapping("/orders")
    public ResponseEntity<OrderResponse> createOrder(@RequestBody OrderRequest req) {
        Order order = orderService.createOrder(req.getCustomerId(), req.getItems());
        return ResponseEntity.ok(new OrderResponse(order));
    }
}

// Persistence -- only handles data storage
public class JpaOrderRepository implements OrderRepository {
    public Order save(Order order) { /* JPA logic */ }
}

// Notification -- only handles external communication
public class EmailNotificationService implements NotificationService {
    public void orderCreated(Order order) { /* Email logic */ }
}
```

Now each class has one concern. The `OrderService` knows nothing about HTTP, SQL, or email APIs.

---

## 18.3 Independence: The Goal of Clean Architecture

Clean Architecture aims to make your system independent of:

```
  +-------------------------------------------------------+
  |           INDEPENDENCE GOALS                           |
  +-------------------------------------------------------+
  |                                                        |
  |  1. Independent of FRAMEWORKS                          |
  |     The framework is a tool, not the architecture.     |
  |     You can swap Spring for Micronaut.                 |
  |                                                        |
  |  2. Independent of the UI                              |
  |     The UI can change from web to mobile to CLI        |
  |     without changing business rules.                   |
  |                                                        |
  |  3. Independent of the DATABASE                        |
  |     You can swap PostgreSQL for MongoDB                |
  |     without changing business rules.                   |
  |                                                        |
  |  4. Independent of EXTERNAL AGENCIES                   |
  |     Business rules do not know about the outside       |
  |     world (APIs, file systems, etc).                   |
  |                                                        |
  |  5. TESTABLE                                           |
  |     Business rules can be tested without the UI,       |
  |     database, web server, or any external element.     |
  |                                                        |
  +-------------------------------------------------------+
```

---

## 18.4 The Dependency Rule

The Dependency Rule is the single most important rule in Clean Architecture:

> Source code dependencies must point only inward, toward higher-level policies.

```
  +-----------------------------------------------------------+
  |                    THE DEPENDENCY RULE                      |
  +-----------------------------------------------------------+
  |                                                            |
  |  Outer layers can depend on inner layers.                  |
  |  Inner layers MUST NOT depend on outer layers.             |
  |  Inner layers MUST NOT know that outer layers exist.       |
  |                                                            |
  +-----------------------------------------------------------+
```

### What "Inward" Means

"Inward" means toward the center of the architecture -- toward the most important, most stable, most abstract parts of the system. Business rules are at the center. Frameworks, databases, and UIs are at the edges.

### Dependency Direction

```
  +-----------------------------------------------------+
  |                                                      |
  |  Framework  ----depends on---->  Use Case            |
  |  Controller ----depends on---->  Business Rule       |
  |  Database   ----depends on---->  Entity              |
  |  UI         ----depends on---->  Service             |
  |                                                      |
  |  NEVER the reverse.                                  |
  |                                                      |
  +-----------------------------------------------------+
```

### How Dependency Inversion Makes This Work

The inner layer defines an interface. The outer layer implements it. The inner layer never imports, references, or knows about the outer layer.

**Java Example:**

```java
// INNER LAYER: defines the interface (what it needs)
public interface OrderRepository {
    Order save(Order order);
    Order findById(int id);
}

// INNER LAYER: uses the interface
public class OrderService {
    private final OrderRepository repository;  // Depends on abstraction

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }

    public Order placeOrder(Order order) {
        // Business logic here
        return repository.save(order);
    }
}

// OUTER LAYER: implements the interface
public class PostgresOrderRepository implements OrderRepository {
    public Order save(Order order) {
        // SQL INSERT logic
    }
    public Order findById(int id) {
        // SQL SELECT logic
    }
}
```

**Python Example:**

```python
# INNER LAYER: defines the interface
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order): ...

    @abstractmethod
    def find_by_id(self, order_id): ...


# INNER LAYER: uses the interface
class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def place_order(self, order):
        # Business logic here
        return self.repository.save(order)


# OUTER LAYER: implements the interface
class PostgresOrderRepository(OrderRepository):
    def save(self, order):
        # SQL INSERT logic
        ...

    def find_by_id(self, order_id):
        # SQL SELECT logic
        ...
```

The `OrderService` depends on the `OrderRepository` interface, which lives in the same inner layer. It has NO dependency on `PostgresOrderRepository`. You could swap in `MongoOrderRepository` or `InMemoryOrderRepository` without touching `OrderService`.

---

## 18.5 The Concentric Circles

Uncle Bob's Clean Architecture is commonly shown as four concentric circles:

```
  +----------------------------------------------------------+
  |                                                           |
  |    Frameworks & Drivers (outermost)                       |
  |  +------------------------------------------------------+ |
  |  |                                                      | |
  |  |    Interface Adapters                                | |
  |  |  +--------------------------------------------------+ |
  |  |  |                                                  | |  |
  |  |  |    Application Business Rules (Use Cases)        | |  |
  |  |  |  +----------------------------------------------+ |  |
  |  |  |  |                                              | |  |
  |  |  |  |    Enterprise Business Rules (Entities)      | |  |
  |  |  |  |                                              | |  |
  |  |  |  +----------------------------------------------+ |  |
  |  |  |                                                  | |  |
  |  |  +--------------------------------------------------+ |
  |  |                                                      | |
  |  +------------------------------------------------------+ |
  |                                                           |
  +----------------------------------------------------------+

              Dependencies point INWARD only -->
```

### Layer 1: Entities (Center)

Entities encapsulate the most general and high-level business rules. They are the core domain objects that would exist regardless of the application.

```java
// Entity: pure business rules, no dependencies on anything external
public class LoanApplication {
    private double requestedAmount;
    private double annualIncome;
    private int creditScore;

    public boolean isEligible() {
        return creditScore >= 650
            && requestedAmount <= annualIncome * 3;
    }

    public double calculateRate() {
        if (creditScore >= 750) return 0.035;
        if (creditScore >= 700) return 0.045;
        return 0.065;
    }
}
```

```python
class LoanApplication:
    def __init__(self, requested_amount, annual_income, credit_score):
        self.requested_amount = requested_amount
        self.annual_income = annual_income
        self.credit_score = credit_score

    def is_eligible(self):
        return (self.credit_score >= 650
                and self.requested_amount <= self.annual_income * 3)

    def calculate_rate(self):
        if self.credit_score >= 750:
            return 0.035
        if self.credit_score >= 700:
            return 0.045
        return 0.065
```

### Layer 2: Use Cases (Application Business Rules)

Use cases contain application-specific business rules. They orchestrate the flow of data to and from entities and direct them to use their enterprise-level rules.

```java
public class ProcessLoanUseCase {
    private final LoanRepository loanRepo;
    private final CreditCheckService creditCheck;
    private final NotificationService notifier;

    public ProcessLoanUseCase(LoanRepository loanRepo,
                               CreditCheckService creditCheck,
                               NotificationService notifier) {
        this.loanRepo = loanRepo;
        this.creditCheck = creditCheck;
        this.notifier = notifier;
    }

    public LoanResult process(LoanRequest request) {
        int creditScore = creditCheck.getScore(request.getApplicantId());

        LoanApplication application = new LoanApplication(
            request.getAmount(),
            request.getIncome(),
            creditScore
        );

        if (!application.isEligible()) {
            notifier.loanDenied(request.getApplicantId());
            return LoanResult.denied("Does not meet eligibility criteria");
        }

        double rate = application.calculateRate();
        Loan loan = loanRepo.save(new Loan(request, rate));
        notifier.loanApproved(request.getApplicantId(), loan);
        return LoanResult.approved(loan);
    }
}
```

```python
class ProcessLoanUseCase:
    def __init__(self, loan_repo, credit_check, notifier):
        self.loan_repo = loan_repo
        self.credit_check = credit_check
        self.notifier = notifier

    def process(self, request):
        credit_score = self.credit_check.get_score(request.applicant_id)

        application = LoanApplication(
            request.amount, request.income, credit_score
        )

        if not application.is_eligible():
            self.notifier.loan_denied(request.applicant_id)
            return LoanResult.denied("Does not meet eligibility criteria")

        rate = application.calculate_rate()
        loan = self.loan_repo.save(Loan(request, rate))
        self.notifier.loan_approved(request.applicant_id, loan)
        return LoanResult.approved(loan)
```

### Layer 3: Interface Adapters

Interface adapters convert data between the format used by use cases and the format used by external agencies (database, web, etc.).

```java
// Controller: converts HTTP request to use case input
@RestController
public class LoanController {
    private final ProcessLoanUseCase useCase;

    @PostMapping("/loans")
    public ResponseEntity<LoanResponse> apply(@RequestBody LoanHttpRequest httpReq) {
        LoanRequest domainRequest = new LoanRequest(
            httpReq.getApplicantId(),
            httpReq.getAmount(),
            httpReq.getIncome()
        );
        LoanResult result = useCase.process(domainRequest);
        return ResponseEntity.ok(LoanResponse.from(result));
    }
}

// Repository implementation: converts domain objects to database rows
public class JpaLoanRepository implements LoanRepository {
    private final JpaLoanEntityRepository jpaRepo;

    public Loan save(Loan loan) {
        LoanEntity entity = LoanEntity.from(loan);
        jpaRepo.save(entity);
        return loan;
    }
}
```

### Layer 4: Frameworks and Drivers (Outermost)

This is where frameworks, tools, and external systems live. Spring Boot, Django, PostgreSQL, RabbitMQ. This layer has the least amount of your code -- it is mostly configuration and glue.

---

## 18.6 Data Crossing Boundaries

When data crosses a boundary between layers, it should be in the form that is most convenient for the inner layer. The outer layer does the conversion.

```
  +---------------------------------------------------------------+
  |                                                                |
  |  HTTP Request  -->  Controller  -->  Use Case Input DTO       |
  |                     (converts)       (simple data object)      |
  |                                                                |
  |  Use Case Output DTO  -->  Controller  -->  HTTP Response     |
  |  (simple data object)      (converts)                         |
  |                                                                |
  |  Entity  -->  Repository  -->  Database Row                   |
  |               (converts)                                       |
  |                                                                |
  +---------------------------------------------------------------+
```

### Why Not Just Pass Entities Everywhere?

If your controller returns an Entity directly as JSON, then:

- Your API contract is coupled to your domain model
- Adding a field to the entity automatically exposes it in the API
- The entity gains JSON annotations, making it dependent on the web framework

Keep entities clean. Use DTOs (Data Transfer Objects) to cross boundaries.

---

## 18.7 The Dependency Rule in Practice

Here is a complete dependency map for a typical Clean Architecture application:

```
  +--------------------------------------------------------------+
  |  OUTER: Frameworks & Drivers                                  |
  |    Spring Boot, Django, PostgreSQL driver, HTTP client        |
  |                         |                                     |
  |                         | depends on                         |
  |                         v                                     |
  |  LAYER 3: Interface Adapters                                  |
  |    Controllers, Repositories (impl), Presenters              |
  |                         |                                     |
  |                         | depends on                         |
  |                         v                                     |
  |  LAYER 2: Use Cases                                           |
  |    Application services, input/output ports                  |
  |                         |                                     |
  |                         | depends on                         |
  |                         v                                     |
  |  LAYER 1: Entities (CENTER)                                   |
  |    Domain objects, business rules                             |
  |    No dependencies on anything else                           |
  +--------------------------------------------------------------+
```

### Testing Benefits

Because inner layers have no outward dependencies, you can test them with no framework, no database, and no web server:

```java
@Test
void processLoan_eligibleApplicant_approvesLoan() {
    // All dependencies are fakes -- no Spring, no database
    LoanRepository fakeRepo = new InMemoryLoanRepository();
    CreditCheckService fakeCredit = applicantId -> 720;
    NotificationService fakeNotifier = new NoOpNotificationService();

    ProcessLoanUseCase useCase = new ProcessLoanUseCase(
        fakeRepo, fakeCredit, fakeNotifier
    );

    LoanRequest request = new LoanRequest("APP-001", 50000, 80000);
    LoanResult result = useCase.process(request);

    assertTrue(result.isApproved());
}
```

```python
def test_process_loan_eligible_applicant():
    fake_repo = InMemoryLoanRepository()
    fake_credit = lambda applicant_id: 720
    fake_notifier = NoOpNotificationService()

    use_case = ProcessLoanUseCase(fake_repo, fake_credit, fake_notifier)

    request = LoanRequest("APP-001", 50000, 80000)
    result = use_case.process(request)

    assert result.is_approved
```

No framework startup. No database connection. Runs in milliseconds.

---

## Common Mistakes

1. **Letting entities depend on the framework.** Putting `@Entity`, `@Column`, or ORM annotations on domain objects couples your core to the persistence framework.
2. **Skipping the interface.** Directly importing `PostgresRepository` in your use case instead of depending on a `Repository` interface violates the Dependency Rule.
3. **Over-engineering for small projects.** A TODO app does not need four layers. Apply Clean Architecture proportionally to the project's complexity.
4. **Treating architecture as a one-time decision.** Architecture evolves. Start simple and add boundaries as the system grows.
5. **Confusing layers with folders.** Having folders named `entities/`, `usecases/`, and `adapters/` means nothing if the code inside them has tangled dependencies. The Dependency Rule must be enforced in actual import statements.

---

## Best Practices

1. **Start with two layers.** Domain (business rules) and Infrastructure (everything else). Split further when needed.
2. **Define interfaces in the inner layer.** The inner layer declares what it needs. The outer layer provides the implementation.
3. **Use dependency injection.** Pass dependencies through constructors so that inner layers never create outer-layer objects.
4. **Keep entities framework-free.** No annotations from Spring, Django, or any ORM on your core domain objects.
5. **Test the inner layers first.** If your entities and use cases are well-tested, you have high confidence in your business logic regardless of what happens at the edges.

---

## Quick Summary

| Concept | Definition |
|---------|-----------|
| Separation of Concerns | Each component handles one concern |
| Independence | Business rules do not depend on frameworks, UI, or databases |
| Dependency Rule | Dependencies point inward only |
| Entities | Core business rules, no external dependencies |
| Use Cases | Application-specific business rules |
| Interface Adapters | Convert data between layers |
| Frameworks & Drivers | External tools, outermost layer |

---

## Key Points

- Architecture determines how expensive it is to change your system over time.
- The Dependency Rule is the single most important principle: inner layers must not depend on outer layers.
- Entities contain enterprise-wide business rules. Use cases contain application-specific rules.
- Interface adapters convert between the formats of inner and outer layers.
- Clean Architecture makes your business logic testable without any framework or infrastructure.

---

## Practice Questions

1. Your `UserService` class imports `org.springframework.stereotype.Service`. Which Clean Architecture layer does it belong in? Does the annotation violate the Dependency Rule?

2. Draw the dependency direction for these components: `UserController`, `UserService`, `UserRepository` (interface), `PostgresUserRepository`. Which component should know about which?

3. You need to switch from PostgreSQL to MongoDB. If you followed Clean Architecture, which layers would need to change? Which would remain untouched?

4. Explain why passing a JPA `@Entity` object directly to a REST controller response violates Clean Architecture principles.

5. A teammate says "Clean Architecture has too many layers for our simple app." How would you respond? When is it appropriate to use fewer layers?

---

## Exercises

### Exercise 1: Identify the Violations

This code has multiple Clean Architecture violations. Find them all:

```java
public class OrderService {
    @Autowired
    private JdbcTemplate jdbcTemplate;

    public ResponseEntity<String> processOrder(HttpServletRequest request) {
        String json = request.getReader().lines().collect(Collectors.joining());
        JSONObject data = new JSONObject(json);

        double total = data.getDouble("amount") * 1.08;

        jdbcTemplate.update("INSERT INTO orders VALUES (?, ?)",
            data.getString("customerId"), total);

        return ResponseEntity.ok("Order placed: $" + total);
    }
}
```

### Exercise 2: Refactor to Clean Architecture

Take the code from Exercise 1 and refactor it into proper Clean Architecture layers:
- Create an `Order` entity with business logic
- Create a `PlaceOrderUseCase` with application logic
- Create an `OrderRepository` interface and implementation
- Create a controller that only handles HTTP concerns

### Exercise 3: Dependency Map

Draw a dependency map for a blog application with these features:
- Users can create and edit posts
- Posts are stored in a database
- An email is sent when a post is published
- Posts are displayed on a web page

Identify the entities, use cases, interface adapters, and frameworks. Draw arrows showing which component depends on which. Verify that all arrows point inward.

---

## What Is Next?

Clean Architecture gives you the principles. The next three chapters show you specific architectural patterns that implement these principles. Chapter 19: Layered Architecture covers the most common pattern -- the three-tier architecture used by the vast majority of business applications.
