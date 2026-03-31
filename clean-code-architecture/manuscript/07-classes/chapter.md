# Chapter 7: Classes -- Building Blocks of Clean Software

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Design small, focused classes with a single responsibility
- Understand and measure class cohesion
- Recognize the God Class anti-pattern and refactor it
- Apply the "one reason to change" principle to class design
- Use encapsulation to protect class internals
- Apply the Tell, Don't Ask principle
- Organize classes for change and extensibility
- Split large, unfocused classes into clean, maintainable components

---

## Why This Chapter Matters

Classes are the primary organizational unit in object-oriented software. A well-designed class is easy to understand, easy to test, and easy to change. A poorly designed class becomes a maintenance nightmare that slows down entire teams.

Consider this: you join a new team and open a file called `ApplicationManager.java`. It is 2,400 lines long. It handles user authentication, database connections, email sending, report generation, and logging. Where do you start? How do you add a feature without breaking something else? How do you write a test for just one behavior?

This chapter teaches you to avoid that situation entirely. You will learn how to design classes that are small, focused, and easy to work with. These principles apply whether you are writing Java, Python, or any other object-oriented language.

---

## The Problem With Large Classes

Most developers have encountered a class like this at some point in their career. It starts small, with a clear purpose. Over months and years, developers add "just one more method" until the class becomes a tangled mess of unrelated responsibilities.

```
┌─────────────────────────────────────────────┐
│            UserManager (God Class)           │
├─────────────────────────────────────────────┤
│ - dbConnection                              │
│ - emailClient                               │
│ - logger                                    │
│ - cache                                     │
│ - passwordEncoder                           │
│ - templateEngine                            │
│ - reportFormatter                           │
│ - auditTrail                                │
├─────────────────────────────────────────────┤
│ + createUser()                              │
│ + deleteUser()                              │
│ + findUserById()                            │
│ + findUserByEmail()                         │
│ + authenticateUser()                        │
│ + resetPassword()                           │
│ + sendWelcomeEmail()                        │
│ + sendPasswordResetEmail()                  │
│ + generateMonthlyReport()                   │
│ + exportUsersToCsv()                        │
│ + logUserActivity()                         │
│ + cacheUserSession()                        │
│ + invalidateCache()                         │
│ + validateUserInput()                       │
│ + formatUserForDisplay()                    │
│ + calculateUserStatistics()                 │
│ + ... (30 more methods)                     │
└─────────────────────────────────────────────┘
```

This is the **God Class** anti-pattern. One class that tries to do everything. It knows too much, does too much, and changes for too many reasons.

### Why God Classes Are Harmful

1. **Hard to understand.** A developer must read hundreds or thousands of lines to grasp what the class does.

2. **Hard to test.** Testing one behavior requires setting up dependencies for all behaviors. Want to test password reset? You still need a database connection, email client, cache, and logger.

3. **High risk of bugs.** Changing the email logic might accidentally break the reporting logic because they share instance variables.

4. **Merge conflicts.** Multiple developers working on different features all edit the same file, creating constant merge conflicts.

5. **Hard to reuse.** You cannot use just the email functionality without dragging along the database, caching, and reporting code.

---

## Small Classes: The First Rule

The first rule of classes is that they should be **small**. The second rule is that they should be **smaller than that**.

But "small" does not mean counting lines of code. A 200-line class with a clear, single purpose is better than a 50-line class that mixes two unrelated responsibilities. Size is measured in **responsibilities**, not lines.

### A Class Should Have One Reason to Change

This is the most important principle in class design. Every class should have exactly one reason to change. If you can think of more than one reason why a class might need to be modified, it has more than one responsibility.

Ask yourself: "Who would request changes to this class?" If the answer includes multiple people or teams (the security team, the marketing team, the database administrators), the class has too many responsibilities.

```
┌─────────────────────────────────────────────┐
│              One Reason to Change            │
├─────────────────────────────────────────────┤
│                                             │
│  UserRepository  -- changes when the        │
│                     database schema changes  │
│                                             │
│  EmailService    -- changes when email       │
│                     requirements change      │
│                                             │
│  PasswordHasher  -- changes when security    │
│                     policy changes           │
│                                             │
│  UserFormatter   -- changes when display     │
│                     requirements change      │
│                                             │
└─────────────────────────────────────────────┘
```

Each class has one actor (one stakeholder) who would request changes. The database team changes `UserRepository`. The security team changes `PasswordHasher`. The UI team changes `UserFormatter`. No class changes for two different reasons.

---

## Cohesion: The Measure of a Good Class

Cohesion measures how closely the methods and instance variables of a class are related. In a highly cohesive class, every method uses most of the instance variables. In a low-cohesion class, methods are grouped together but operate on different subsets of data.

### High Cohesion Example

**Java:**

```java
// HIGH COHESION: Every method uses the core instance variables
public class Rectangle {
    private double width;
    private double height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }

    public double area() {
        return width * height;   // uses both variables
    }

    public double perimeter() {
        return 2 * (width + height);  // uses both variables
    }

    public double diagonal() {
        return Math.sqrt(width * width + height * height);  // uses both
    }

    public boolean isSquare() {
        return Double.compare(width, height) == 0;  // uses both
    }
}
```

**Python:**

```python
# HIGH COHESION: Every method uses the core instance variables
class Rectangle:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def area(self) -> float:
        return self._width * self._height  # uses both

    def perimeter(self) -> float:
        return 2 * (self._width + self._height)  # uses both

    def diagonal(self) -> float:
        return (self._width ** 2 + self._height ** 2) ** 0.5  # uses both

    def is_square(self) -> bool:
        return self._width == self._height  # uses both
```

Every method in this class operates on `width` and `height`. The class is highly cohesive. All its parts work together toward a single purpose: representing a rectangle.

### Low Cohesion Example

**Java:**

```java
// LOW COHESION: Methods use different subsets of variables
public class UserManager {
    private Database db;
    private EmailClient emailClient;
    private PasswordEncoder encoder;
    private Logger logger;

    public User findUser(int id) {
        return db.query("SELECT * FROM users WHERE id = ?", id);
        // uses: db
    }

    public void sendWelcomeEmail(User user) {
        emailClient.send(user.getEmail(), "Welcome!", buildTemplate(user));
        // uses: emailClient
    }

    public String hashPassword(String password) {
        return encoder.encode(password);
        // uses: encoder
    }

    public void logActivity(String message) {
        logger.info(message);
        // uses: logger
    }
}
```

Each method uses only one of the four instance variables. The methods are not related to each other. They are stuffed into the same class out of convenience, not because they belong together. This is a sign that the class should be split.

### Measuring Cohesion

A simple way to measure cohesion: for each method, count how many instance variables it uses. Then calculate the average.

```
Cohesion Score = (Total variable uses across all methods)
                 / (Number of methods * Number of instance variables)

Rectangle class:
  - 4 methods, 2 variables
  - Each method uses 2 variables
  - Score = (4 * 2) / (4 * 2) = 1.0  (perfect cohesion)

UserManager class:
  - 4 methods, 4 variables
  - Each method uses 1 variable
  - Score = (4 * 1) / (4 * 4) = 0.25  (low cohesion)
```

A score close to 1.0 means high cohesion. A score below 0.5 suggests the class should be split.

---

## Before and After: Refactoring a God Class

Let us take a realistic God Class and refactor it step by step.

### BEFORE: The God Class (500+ lines condensed)

**Java:**

```java
public class OrderService {
    private Connection dbConnection;
    private JavaMailSender mailSender;
    private Logger logger;
    private TaxCalculator taxCalc;
    private PdfGenerator pdfGen;
    private InventorySystem inventory;

    // ---- Order CRUD ----
    public Order createOrder(Customer customer, List<Item> items) {
        logger.info("Creating order for " + customer.getName());
        Order order = new Order();
        order.setCustomer(customer);
        order.setItems(items);
        order.setStatus("PENDING");

        double subtotal = 0;
        for (Item item : items) {
            subtotal += item.getPrice() * item.getQuantity();
        }
        double tax = taxCalc.calculate(subtotal, customer.getState());
        order.setSubtotal(subtotal);
        order.setTax(tax);
        order.setTotal(subtotal + tax);

        // Save to database
        PreparedStatement stmt = dbConnection.prepareStatement(
            "INSERT INTO orders (customer_id, subtotal, tax, total, status) " +
            "VALUES (?, ?, ?, ?, ?)"
        );
        stmt.setInt(1, customer.getId());
        stmt.setDouble(2, subtotal);
        stmt.setDouble(3, tax);
        stmt.setDouble(4, subtotal + tax);
        stmt.setString(5, "PENDING");
        stmt.executeUpdate();

        // Update inventory
        for (Item item : items) {
            inventory.decreaseStock(item.getId(), item.getQuantity());
        }

        // Send confirmation email
        String emailBody = "<html><body>"
            + "<h1>Order Confirmation</h1>"
            + "<p>Thank you, " + customer.getName() + "!</p>"
            + "<p>Total: $" + order.getTotal() + "</p>"
            + "</body></html>";
        mailSender.send(customer.getEmail(), "Order Confirmation", emailBody);

        logger.info("Order created successfully: " + order.getId());
        return order;
    }

    public Order findOrderById(int id) {
        PreparedStatement stmt = dbConnection.prepareStatement(
            "SELECT * FROM orders WHERE id = ?"
        );
        stmt.setInt(1, id);
        ResultSet rs = stmt.executeQuery();
        // ... map result set to Order object (20+ lines)
        return order;
    }

    public void cancelOrder(int orderId) {
        Order order = findOrderById(orderId);
        order.setStatus("CANCELLED");
        // Update database
        PreparedStatement stmt = dbConnection.prepareStatement(
            "UPDATE orders SET status = ? WHERE id = ?"
        );
        stmt.setString(1, "CANCELLED");
        stmt.setInt(2, orderId);
        stmt.executeUpdate();

        // Restore inventory
        for (Item item : order.getItems()) {
            inventory.increaseStock(item.getId(), item.getQuantity());
        }

        // Send cancellation email
        mailSender.send(order.getCustomer().getEmail(),
            "Order Cancelled",
            "Your order #" + orderId + " has been cancelled.");

        logger.info("Order cancelled: " + orderId);
    }

    // ---- Reporting ----
    public byte[] generateInvoicePdf(int orderId) {
        Order order = findOrderById(orderId);
        return pdfGen.createInvoice(order);
    }

    public List<Order> getMonthlyReport(int month, int year) {
        PreparedStatement stmt = dbConnection.prepareStatement(
            "SELECT * FROM orders WHERE MONTH(created_at) = ? AND YEAR(created_at) = ?"
        );
        // ... query and build report (30+ lines)
        return orders;
    }

    public String exportOrdersToCsv(List<Order> orders) {
        StringBuilder csv = new StringBuilder("id,customer,total,status\n");
        for (Order order : orders) {
            csv.append(order.getId()).append(",")
               .append(order.getCustomer().getName()).append(",")
               .append(order.getTotal()).append(",")
               .append(order.getStatus()).append("\n");
        }
        return csv.toString();
    }

    // ---- Tax calculation ----
    public double calculateTax(double amount, String state) {
        return taxCalc.calculate(amount, state);
    }

    // ---- Email templates ----
    private String buildConfirmationEmail(Order order) { /* 20 lines */ }
    private String buildCancellationEmail(Order order) { /* 15 lines */ }
    private String buildShippingEmail(Order order) { /* 20 lines */ }

    // ... 200 more lines of mixed concerns
}
```

This class changes when:
- The database schema changes (CRUD operations)
- Email templates change (email formatting)
- Tax rules change (tax calculation)
- Report formats change (reporting)
- Inventory rules change (stock management)

Five reasons to change means five responsibilities. That is four too many.

### AFTER: Focused Classes

**Java:**

```java
// Responsibility: Persisting and retrieving orders
public class OrderRepository {
    private final Connection dbConnection;

    public OrderRepository(Connection dbConnection) {
        this.dbConnection = dbConnection;
    }

    public Order save(Order order) {
        PreparedStatement stmt = dbConnection.prepareStatement(
            "INSERT INTO orders (customer_id, subtotal, tax, total, status) " +
            "VALUES (?, ?, ?, ?, ?)"
        );
        stmt.setInt(1, order.getCustomer().getId());
        stmt.setDouble(2, order.getSubtotal());
        stmt.setDouble(3, order.getTax());
        stmt.setDouble(4, order.getTotal());
        stmt.setString(5, order.getStatus());
        stmt.executeUpdate();
        return order;
    }

    public Order findById(int id) {
        PreparedStatement stmt = dbConnection.prepareStatement(
            "SELECT * FROM orders WHERE id = ?"
        );
        stmt.setInt(1, id);
        ResultSet rs = stmt.executeQuery();
        return mapToOrder(rs);
    }

    public void updateStatus(int orderId, String status) {
        PreparedStatement stmt = dbConnection.prepareStatement(
            "UPDATE orders SET status = ? WHERE id = ?"
        );
        stmt.setString(1, status);
        stmt.setInt(2, orderId);
        stmt.executeUpdate();
    }

    private Order mapToOrder(ResultSet rs) {
        // mapping logic
    }
}
```

```java
// Responsibility: Calculating order totals and tax
public class OrderPriceCalculator {
    private final TaxCalculator taxCalculator;

    public OrderPriceCalculator(TaxCalculator taxCalculator) {
        this.taxCalculator = taxCalculator;
    }

    public OrderTotal calculate(List<Item> items, String state) {
        double subtotal = items.stream()
            .mapToDouble(item -> item.getPrice() * item.getQuantity())
            .sum();
        double tax = taxCalculator.calculate(subtotal, state);
        return new OrderTotal(subtotal, tax, subtotal + tax);
    }
}
```

```java
// Responsibility: Sending order-related emails
public class OrderNotificationService {
    private final JavaMailSender mailSender;
    private final OrderEmailTemplates templates;

    public OrderNotificationService(JavaMailSender mailSender,
                                     OrderEmailTemplates templates) {
        this.mailSender = mailSender;
        this.templates = templates;
    }

    public void sendConfirmation(Order order) {
        String body = templates.confirmation(order);
        mailSender.send(order.getCustomer().getEmail(),
            "Order Confirmation", body);
    }

    public void sendCancellation(Order order) {
        String body = templates.cancellation(order);
        mailSender.send(order.getCustomer().getEmail(),
            "Order Cancelled", body);
    }
}
```

```java
// Responsibility: Managing inventory levels
public class InventoryManager {
    private final InventorySystem inventory;

    public InventoryManager(InventorySystem inventory) {
        this.inventory = inventory;
    }

    public void reserveItems(List<Item> items) {
        for (Item item : items) {
            inventory.decreaseStock(item.getId(), item.getQuantity());
        }
    }

    public void releaseItems(List<Item> items) {
        for (Item item : items) {
            inventory.increaseStock(item.getId(), item.getQuantity());
        }
    }
}
```

```java
// Responsibility: Generating order reports
public class OrderReportService {
    private final OrderRepository orderRepository;
    private final PdfGenerator pdfGenerator;

    public OrderReportService(OrderRepository orderRepository,
                               PdfGenerator pdfGenerator) {
        this.orderRepository = orderRepository;
        this.pdfGenerator = pdfGenerator;
    }

    public byte[] generateInvoice(int orderId) {
        Order order = orderRepository.findById(orderId);
        return pdfGenerator.createInvoice(order);
    }

    public String exportToCsv(List<Order> orders) {
        StringBuilder csv = new StringBuilder("id,customer,total,status\n");
        for (Order order : orders) {
            csv.append(order.getId()).append(",")
               .append(order.getCustomer().getName()).append(",")
               .append(order.getTotal()).append(",")
               .append(order.getStatus()).append("\n");
        }
        return csv.toString();
    }
}
```

```java
// Responsibility: Coordinating the order creation workflow
public class OrderService {
    private final OrderRepository repository;
    private final OrderPriceCalculator calculator;
    private final OrderNotificationService notifications;
    private final InventoryManager inventoryManager;
    private final Logger logger;

    public OrderService(OrderRepository repository,
                        OrderPriceCalculator calculator,
                        OrderNotificationService notifications,
                        InventoryManager inventoryManager,
                        Logger logger) {
        this.repository = repository;
        this.calculator = calculator;
        this.notifications = notifications;
        this.inventoryManager = inventoryManager;
        this.logger = logger;
    }

    public Order createOrder(Customer customer, List<Item> items) {
        logger.info("Creating order for " + customer.getName());

        OrderTotal total = calculator.calculate(items, customer.getState());

        Order order = new Order(customer, items, total);
        repository.save(order);

        inventoryManager.reserveItems(items);
        notifications.sendConfirmation(order);

        logger.info("Order created: " + order.getId());
        return order;
    }

    public void cancelOrder(int orderId) {
        Order order = repository.findById(orderId);
        order.setStatus("CANCELLED");
        repository.updateStatus(orderId, "CANCELLED");

        inventoryManager.releaseItems(order.getItems());
        notifications.sendCancellation(order);

        logger.info("Order cancelled: " + orderId);
    }
}
```

### The Refactored Structure

```
BEFORE:                              AFTER:
┌──────────────────────┐     ┌───────────────────────┐
│                      │     │    OrderService        │
│   OrderService       │     │  (coordination only)   │
│                      │     └───────────┬───────────┘
│  - DB queries        │                 │
│  - Tax calculation   │     ┌───────────┼───────────────┐
│  - Email sending     │     │           │               │
│  - Inventory mgmt    │     ▼           ▼               ▼
│  - PDF generation    │  ┌─────────┐ ┌────────────┐ ┌──────────┐
│  - CSV export        │  │ Order   │ │ Order      │ │ Inventory│
│  - Email templates   │  │ Repo    │ │ Price      │ │ Manager  │
│  - Reporting         │  │         │ │ Calculator │ │          │
│  - Logging           │  └─────────┘ └────────────┘ └──────────┘
│  - ... 40+ methods   │
│                      │     ┌───────────────┐ ┌──────────────┐
│  500+ lines          │     │ Order         │ │ Order Report │
│                      │     │ Notification  │ │ Service      │
└──────────────────────┘     │ Service       │ │              │
                             └───────────────┘ └──────────────┘
```

**Python version of the refactored code:**

```python
class OrderRepository:
    """Persists and retrieves orders from the database."""

    def __init__(self, db_connection):
        self._db = db_connection

    def save(self, order: Order) -> Order:
        self._db.execute(
            "INSERT INTO orders (customer_id, subtotal, tax, total, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (order.customer.id, order.subtotal, order.tax,
             order.total, order.status)
        )
        return order

    def find_by_id(self, order_id: int) -> Order:
        row = self._db.execute(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        return self._map_to_order(row)

    def update_status(self, order_id: int, status: str) -> None:
        self._db.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id)
        )


class OrderPriceCalculator:
    """Calculates order totals including tax."""

    def __init__(self, tax_calculator):
        self._tax_calculator = tax_calculator

    def calculate(self, items: list, state: str) -> OrderTotal:
        subtotal = sum(item.price * item.quantity for item in items)
        tax = self._tax_calculator.calculate(subtotal, state)
        return OrderTotal(subtotal, tax, subtotal + tax)


class OrderNotificationService:
    """Sends order-related email notifications."""

    def __init__(self, mail_sender, templates):
        self._mail_sender = mail_sender
        self._templates = templates

    def send_confirmation(self, order: Order) -> None:
        body = self._templates.confirmation(order)
        self._mail_sender.send(order.customer.email,
                               "Order Confirmation", body)

    def send_cancellation(self, order: Order) -> None:
        body = self._templates.cancellation(order)
        self._mail_sender.send(order.customer.email,
                               "Order Cancelled", body)


class OrderService:
    """Coordinates the order creation workflow."""

    def __init__(self, repository, calculator, notifications,
                 inventory_manager, logger):
        self._repository = repository
        self._calculator = calculator
        self._notifications = notifications
        self._inventory = inventory_manager
        self._logger = logger

    def create_order(self, customer, items) -> Order:
        self._logger.info(f"Creating order for {customer.name}")

        total = self._calculator.calculate(items, customer.state)
        order = Order(customer, items, total)
        self._repository.save(order)

        self._inventory.reserve_items(items)
        self._notifications.send_confirmation(order)

        self._logger.info(f"Order created: {order.id}")
        return order

    def cancel_order(self, order_id: int) -> None:
        order = self._repository.find_by_id(order_id)
        order.status = "CANCELLED"
        self._repository.update_status(order_id, "CANCELLED")

        self._inventory.release_items(order.items)
        self._notifications.send_cancellation(order)

        self._logger.info(f"Order cancelled: {order_id}")
```

---

## Encapsulation

Encapsulation means hiding a class's internal details and exposing only what other classes need to know. It is not just about making fields `private`. It is about protecting the integrity of your objects.

### Why Encapsulation Matters

Without encapsulation, any code anywhere can reach into your object and change its state in ways you did not anticipate:

**Java -- BEFORE (no encapsulation):**

```java
public class BankAccount {
    public double balance;    // anyone can modify this directly
    public String status;     // anyone can set this to anything
}

// Somewhere else in the codebase...
account.balance = -1000;     // negative balance? No validation!
account.status = "banana";   // nonsensical status? No protection!
```

**Java -- AFTER (with encapsulation):**

```java
public class BankAccount {
    private double balance;
    private AccountStatus status;

    public BankAccount(double initialBalance) {
        if (initialBalance < 0) {
            throw new IllegalArgumentException("Initial balance cannot be negative");
        }
        this.balance = initialBalance;
        this.status = AccountStatus.ACTIVE;
    }

    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Deposit amount must be positive");
        }
        this.balance += amount;
    }

    public void withdraw(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Withdrawal amount must be positive");
        }
        if (amount > balance) {
            throw new InsufficientFundsException("Not enough funds");
        }
        this.balance -= amount;
    }

    public double getBalance() {
        return balance;    // read-only access
    }
}
```

**Python:**

```python
class BankAccount:
    def __init__(self, initial_balance: float):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self._balance = initial_balance
        self._status = AccountStatus.ACTIVE

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise InsufficientFundsError("Not enough funds")
        self._balance -= amount

    @property
    def balance(self) -> float:
        return self._balance  # read-only access
```

Now the `BankAccount` class controls how its state changes. No outside code can set a negative balance or an invalid status. The class enforces its own rules.

---

## Tell, Don't Ask

The Tell, Don't Ask principle says: instead of asking an object for its data and then making decisions based on that data, tell the object what to do and let it make the decision itself.

### BEFORE: Ask, Then Decide (Violating Tell, Don't Ask)

**Java:**

```java
// Asking the object for data, then deciding externally
public class OrderProcessor {
    public void processDiscount(Order order) {
        // ASK for internal state
        double total = order.getTotal();
        String customerType = order.getCustomer().getType();
        int itemCount = order.getItems().size();

        // DECIDE based on that state
        double discount = 0;
        if (customerType.equals("PREMIUM") && total > 100) {
            discount = total * 0.15;
        } else if (customerType.equals("REGULAR") && itemCount > 5) {
            discount = total * 0.05;
        }

        // MODIFY the object externally
        order.setDiscount(discount);
        order.setTotal(total - discount);
    }
}
```

The problem: the discount logic lives outside the `Order` class. If another part of the codebase also calculates discounts, you get duplicated logic. The `Order` class has no control over how its own discount is calculated.

### AFTER: Tell the Object What to Do

**Java:**

```java
public class Order {
    private double subtotal;
    private double discount;
    private Customer customer;
    private List<Item> items;

    // TELL the order to apply its discount
    public void applyDiscount() {
        if (customer.isPremium() && subtotal > 100) {
            this.discount = subtotal * 0.15;
        } else if (items.size() > 5) {
            this.discount = subtotal * 0.05;
        } else {
            this.discount = 0;
        }
    }

    public double getTotal() {
        return subtotal - discount;
    }
}

// Usage:
order.applyDiscount();   // Tell, don't ask
double total = order.getTotal();
```

**Python:**

```python
class Order:
    def __init__(self, customer, items):
        self._customer = customer
        self._items = items
        self._subtotal = sum(item.price * item.quantity for item in items)
        self._discount = 0.0

    def apply_discount(self) -> None:
        """Tell the order to calculate its own discount."""
        if self._customer.is_premium and self._subtotal > 100:
            self._discount = self._subtotal * 0.15
        elif len(self._items) > 5:
            self._discount = self._subtotal * 0.05
        else:
            self._discount = 0.0

    @property
    def total(self) -> float:
        return self._subtotal - self._discount


# Usage:
order.apply_discount()   # Tell, don't ask
print(order.total)
```

The discount logic now lives where it belongs: inside the `Order` class. The class knows its own rules and enforces them.

### Spotting Tell, Don't Ask Violations

Look for this pattern in your code:

```
obj.getX()           # ASK
if (someCondition)   # DECIDE externally
obj.setY(newValue)   # MODIFY externally
```

This pattern means the logic belongs inside the object, not outside it. Refactor it to:

```
obj.doSomething()    # TELL
```

---

## Organizing Classes for Change

Well-organized classes make future changes easy. Poorly organized classes make every change risky.

### The Newspaper Metaphor

Organize your class like a newspaper article:

1. **Public constants** at the top (the headline)
2. **Private variables** next (the subheading)
3. **Constructors** (the lead paragraph)
4. **Public methods** (the body of the article)
5. **Private methods** right after the public method that calls them (supporting details)

**Java:**

```java
public class UserService {
    // 1. Constants
    private static final int MAX_LOGIN_ATTEMPTS = 5;
    private static final int LOCKOUT_DURATION_MINUTES = 30;

    // 2. Instance variables
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    // 3. Constructor
    public UserService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    // 4. Public methods
    public User register(String email, String password) {
        validateEmail(email);
        String hashedPassword = passwordEncoder.encode(password);
        User user = new User(email, hashedPassword);
        return userRepository.save(user);
    }

    public boolean authenticate(String email, String password) {
        User user = userRepository.findByEmail(email);
        if (user == null) {
            return false;
        }
        if (isLockedOut(user)) {
            throw new AccountLockedException("Account is locked");
        }
        return passwordEncoder.matches(password, user.getPasswordHash());
    }

    // 5. Private methods (near the public methods that use them)
    private void validateEmail(String email) {
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Invalid email");
        }
    }

    private boolean isLockedOut(User user) {
        return user.getFailedLoginAttempts() >= MAX_LOGIN_ATTEMPTS
            && user.getLastFailedLogin()
                   .plusMinutes(LOCKOUT_DURATION_MINUTES)
                   .isAfter(LocalDateTime.now());
    }
}
```

### Open for Extension

When you design classes, think about what is likely to change. Isolate those parts so they can be modified or extended without touching existing code.

```
┌─────────────────────────────────────────────────┐
│            Designing for Change                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  Ask: "What is likely to change?"               │
│                                                 │
│  - Data source?    --> Repository interface     │
│  - Business rules? --> Strategy pattern         │
│  - Output format?  --> Formatter interface      │
│  - Notification?   --> Notification interface   │
│                                                 │
│  Isolate the volatile part behind an interface. │
│  The rest of the code stays stable.             │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Real-World Scenario: The Growing User Class

You are building a web application. In the first sprint, you create a `User` class:

```python
class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
```

Simple and clean. Then the requirements grow:

- Sprint 2: "We need email validation." You add `validate_email()`.
- Sprint 3: "We need password hashing." You add `hash_password()`.
- Sprint 4: "We need to send welcome emails." You add `send_welcome_email()`.
- Sprint 5: "We need to generate profile URLs." You add `generate_profile_url()`.
- Sprint 6: "We need activity logging." You add `log_activity()`.

After six sprints, your `User` class is doing five unrelated things. The fix: split it early.

```python
# Data representation
class User:
    def __init__(self, name: str, email: str, password_hash: str):
        self.name = name
        self.email = email
        self.password_hash = password_hash


# Validation logic
class UserValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password(password: str) -> bool:
        return len(password) >= 8


# Password handling
class PasswordService:
    def __init__(self, hasher):
        self._hasher = hasher

    def hash_password(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        return self._hasher.verify(password, hashed)


# Email notifications
class UserNotificationService:
    def __init__(self, email_sender):
        self._sender = email_sender

    def send_welcome_email(self, user: User) -> None:
        self._sender.send(
            to=user.email,
            subject="Welcome!",
            body=f"Hello {user.name}, welcome aboard!"
        )


# Profile URLs
class ProfileUrlGenerator:
    def __init__(self, base_url: str):
        self._base_url = base_url

    def generate(self, user: User) -> str:
        slug = user.name.lower().replace(" ", "-")
        return f"{self._base_url}/users/{slug}"
```

Each class has one job. Each can be tested independently. Each changes for exactly one reason.

---

## Common Mistakes

### Mistake 1: Classes Named "Manager," "Handler," "Processor," or "Utility"

These vague names are a red flag. They give the class permission to do anything. A `DataManager` can manage data in any way, so developers keep adding unrelated methods.

**Fix:** Name classes after what they specifically do: `OrderRepository`, `PasswordHasher`, `InvoiceGenerator`, `EmailSender`.

### Mistake 2: Creating Getters and Setters for Everything

Automatically generating getters and setters for every field defeats the purpose of encapsulation. You are just adding extra steps to access public fields.

**Fix:** Only expose what is necessary. Prefer methods that perform actions (`deposit`, `withdraw`) over methods that expose raw state (`getBalance`, `setBalance`).

### Mistake 3: Making Everything Static

Static methods and static state create hidden dependencies and make testing difficult. A class full of static methods is really just a disguised set of global functions.

**Fix:** Use instance methods. If a class has no state, consider whether it should be a class at all, or whether its methods belong on another class.

### Mistake 4: Feature Envy

A method that uses more data from another class than from its own class is exhibiting Feature Envy. The method probably belongs in the other class.

```java
// Feature Envy: this method belongs in Customer, not OrderProcessor
public class OrderProcessor {
    public double calculateShipping(Customer customer) {
        if (customer.getCity().equals("NYC") &&
            customer.isPremium() &&
            customer.getOrderCount() > 10) {
            return 0.0;
        }
        return customer.getAddress().getState().getShippingRate();
    }
}
```

**Fix:** Move the method to `Customer`:

```java
public class Customer {
    public double calculateShipping() {
        if (city.equals("NYC") && isPremium && orderCount > 10) {
            return 0.0;
        }
        return address.getState().getShippingRate();
    }
}
```

### Mistake 5: Splitting Too Aggressively

Not every class needs to be 10 lines long. Splitting a class into 15 tiny classes that constantly call each other is worse than having one slightly large but cohesive class. Split only when you identify genuinely separate responsibilities.

---

## Best Practices

1. **Keep classes small by responsibility, not by line count.** A class with one responsibility and 150 lines is better than a class with three responsibilities and 50 lines.

2. **Aim for high cohesion.** Every method should use most of the class's instance variables. If you see clusters of methods that use different variables, those clusters are separate classes waiting to be extracted.

3. **Name classes after what they do, not what they contain.** `InvoiceGenerator` is better than `InvoiceData`. `OrderValidator` is better than `OrderHelper`.

4. **Follow Tell, Don't Ask.** Push behavior into the objects that own the data. If you find yourself calling `getX()` followed by an `if` statement, that logic probably belongs inside the object.

5. **Design for one reason to change.** Ask: "Who would request a change to this class?" If the answer is more than one person or team, the class has too many responsibilities.

6. **Encapsulate aggressively.** Make fields private. Expose behavior, not data. Let the class protect its own invariants.

7. **Organize code like a newspaper.** Constants at the top, then variables, then constructors, then public methods, then private helper methods.

8. **Prefer composition over inheritance.** Instead of extending a base class to gain functionality, inject collaborating objects. This keeps classes focused and flexible.

---

## Quick Summary

Classes are the fundamental building blocks of object-oriented software. Clean classes are small, focused, and cohesive. Each class has exactly one reason to change. The God Class anti-pattern, where one class absorbs dozens of unrelated responsibilities, is one of the most common sources of complexity in real-world codebases. Encapsulation protects a class's internal state, and the Tell, Don't Ask principle pushes behavior to the objects that own the data. When you split a God Class, each resulting class is easier to understand, easier to test, and easier to change independently.

---

## Key Points

- A class should have **one reason to change** -- one responsibility, one stakeholder.
- **Cohesion** measures how closely a class's methods and variables are related. High cohesion means every method uses most instance variables.
- The **God Class** anti-pattern happens when a class accumulates unrelated responsibilities over time. It is hard to understand, test, and change.
- **Encapsulation** means hiding internal state and exposing behavior. Make fields private and control access through methods.
- **Tell, Don't Ask** means telling an object what to do instead of querying its state and making decisions externally.
- Classes should be organized like a newspaper: public interface first, private details last.
- Split classes when you identify **separate responsibilities**, not just to reduce line count.
- Vague names like "Manager" or "Helper" are a sign that the class has too many responsibilities.

---

## Practice Questions

1. You find a class called `ReportManager` with methods: `generatePdfReport()`, `sendReportByEmail()`, `saveReportToDatabase()`, `formatReportAsHtml()`, and `scheduleReportGeneration()`. How many responsibilities does this class have? How would you split it?

2. A colleague argues that creating many small classes increases complexity because there are more files to navigate. How would you respond? What are the tradeoffs?

3. Consider a `ShoppingCart` class with fields `items`, `discountCode`, and `shippingAddress`. It has methods `addItem()`, `removeItem()`, `calculateTotal()`, `applyDiscount()`, and `calculateShipping()`. Is this class cohesive? Should it be split? Why or why not?

4. What is the difference between encapsulation and simply making fields private? Give an example where making a field private without proper encapsulation still leads to problems.

5. Look at this code and identify the Tell, Don't Ask violation:

```java
if (employee.getVacationDays() > 0 && employee.getStatus().equals("ACTIVE")) {
    employee.setVacationDays(employee.getVacationDays() - 1);
    employee.setLastVacation(LocalDate.now());
}
```

---

## Exercises

### Exercise 1: Identify and Split a God Class

Below is a `StudentManager` class. Identify its separate responsibilities and refactor it into focused classes.

```python
class StudentManager:
    def __init__(self, db, email_client, pdf_generator):
        self.db = db
        self.email_client = email_client
        self.pdf_generator = pdf_generator

    def add_student(self, name, email, grade):
        self.db.insert("students", {"name": name, "email": email, "grade": grade})

    def find_student(self, student_id):
        return self.db.query("SELECT * FROM students WHERE id = ?", student_id)

    def calculate_gpa(self, student_id):
        grades = self.db.query("SELECT grade FROM courses WHERE student_id = ?", student_id)
        return sum(grades) / len(grades)

    def send_report_card(self, student_id):
        student = self.find_student(student_id)
        gpa = self.calculate_gpa(student_id)
        self.email_client.send(student["email"], "Report Card", f"GPA: {gpa}")

    def generate_transcript(self, student_id):
        student = self.find_student(student_id)
        return self.pdf_generator.create(student)

    def get_honor_roll(self):
        return self.db.query("SELECT * FROM students WHERE gpa > 3.5")
```

### Exercise 2: Apply Tell, Don't Ask

Refactor this code to follow the Tell, Don't Ask principle:

```java
public class TemperatureMonitor {
    public void checkTemperature(Thermostat thermostat) {
        double temp = thermostat.getCurrentTemperature();
        double max = thermostat.getMaxTemperature();
        double min = thermostat.getMinTemperature();

        if (temp > max) {
            thermostat.setMode("COOLING");
            thermostat.setFanSpeed(3);
        } else if (temp < min) {
            thermostat.setMode("HEATING");
            thermostat.setFanSpeed(2);
        } else {
            thermostat.setMode("IDLE");
            thermostat.setFanSpeed(0);
        }
    }
}
```

### Exercise 3: Measure Cohesion

For the following class, calculate the cohesion score using the formula from this chapter. Then refactor it into classes with higher cohesion.

```java
public class FileProcessor {
    private String inputPath;
    private String outputPath;
    private Logger logger;
    private EmailClient notifier;

    public String readFile() { /* uses inputPath */ }
    public void writeFile(String content) { /* uses outputPath */ }
    public void logOperation(String msg) { /* uses logger */ }
    public void notifyComplete(String recipient) { /* uses notifier */ }
}
```

---

## What Is Next?

Now that you understand how to design small, focused classes with a single responsibility, you are ready to explore this concept in greater depth. The next chapter dives into the **Single Responsibility Principle (SRP)** -- the first of the five SOLID principles. You will learn Uncle Bob's precise definition, including the actor-based perspective that makes SRP more actionable, and you will see detailed examples of identifying and separating responsibilities in real-world code.
