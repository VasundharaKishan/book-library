# Chapter 14: Code Smells -- Recognizing the Warning Signs

## What You Will Learn

- What code smells are and why they matter more than bugs
- How to identify the ten most common code smells in real projects
- The difference between a smell and a genuine design problem
- Concrete before-and-after fixes for every smell covered
- When a smell is acceptable and when it demands immediate action
- How smells compound into architectural rot if left unchecked

## Why This Chapter Matters

Bugs crash your program. Code smells slowly rot it from the inside. A codebase with many smells still "works," but every change takes longer, every fix introduces new problems, and onboarding new developers feels like teaching them a foreign language. Martin Fowler and Kent Beck cataloged smells as early warning signals -- patterns that suggest deeper design problems. Learning to spot them is the first step toward writing code that stays healthy over months and years.

---

## 14.1 What Is a Code Smell?

A code smell is a surface-level indicator that usually corresponds to a deeper problem in the system. It is not a bug. The code compiles, passes tests, and runs correctly. But something about its structure makes it harder to understand, extend, or maintain.

```
  +-------------------------------------------------------+
  |                  CODE SMELL SPECTRUM                   |
  +-------------------------------------------------------+
  |                                                        |
  |  Clean Code  ------>  Mild Smell  ------>  Deep Rot    |
  |                                                        |
  |  Easy to read        Takes extra effort    Nobody      |
  |  Easy to change       to understand        wants to    |
  |  Easy to test        Risky to modify       touch it    |
  |                                                        |
  +-------------------------------------------------------+
```

### The Golden Rule

Not every smell requires immediate action. Use judgment:

- **Fix now** if you are already working in that area of code
- **Note it** if you spot it during a code review but the change is unrelated
- **Ignore it** if the code is stable, rarely touched, and well-tested

---

## 14.2 Long Method

A method that tries to do too much. When you need comments inside a method to explain what different sections do, you almost certainly have a long method smell.

### How to Detect It

- The method is longer than 20 to 30 lines
- You need to scroll to see the whole thing
- It has multiple levels of nesting
- You see comments separating "sections" within the method

### BEFORE: Long Method (Java)

```java
public class ReportGenerator {

    public String generateMonthlyReport(List<Sale> sales, int month, int year) {
        // Filter sales for the given month
        List<Sale> filtered = new ArrayList<>();
        for (Sale sale : sales) {
            if (sale.getDate().getMonthValue() == month
                    && sale.getDate().getYear() == year) {
                filtered.add(sale);
            }
        }

        // Calculate totals
        double totalRevenue = 0;
        double totalTax = 0;
        int totalItems = 0;
        for (Sale sale : filtered) {
            totalRevenue += sale.getAmount();
            totalTax += sale.getAmount() * 0.08;
            totalItems += sale.getItemCount();
        }

        // Find top seller
        Sale topSale = null;
        for (Sale sale : filtered) {
            if (topSale == null || sale.getAmount() > topSale.getAmount()) {
                topSale = sale;
            }
        }

        // Build report string
        StringBuilder report = new StringBuilder();
        report.append("Monthly Report: ").append(month).append("/").append(year).append("\n");
        report.append("Total Revenue: $").append(String.format("%.2f", totalRevenue)).append("\n");
        report.append("Total Tax: $").append(String.format("%.2f", totalTax)).append("\n");
        report.append("Total Items Sold: ").append(totalItems).append("\n");
        if (topSale != null) {
            report.append("Top Sale: $").append(String.format("%.2f", topSale.getAmount())).append("\n");
        }
        return report.toString();
    }
}
```

### AFTER: Extracted Methods (Java)

```java
public class ReportGenerator {

    public String generateMonthlyReport(List<Sale> sales, int month, int year) {
        List<Sale> monthlySales = filterByMonth(sales, month, year);
        ReportData data = calculateTotals(monthlySales);
        Sale topSale = findTopSale(monthlySales);
        return buildReportString(month, year, data, topSale);
    }

    private List<Sale> filterByMonth(List<Sale> sales, int month, int year) {
        List<Sale> filtered = new ArrayList<>();
        for (Sale sale : sales) {
            if (sale.getDate().getMonthValue() == month
                    && sale.getDate().getYear() == year) {
                filtered.add(sale);
            }
        }
        return filtered;
    }

    private ReportData calculateTotals(List<Sale> sales) {
        double revenue = 0;
        double tax = 0;
        int items = 0;
        for (Sale sale : sales) {
            revenue += sale.getAmount();
            tax += sale.getAmount() * 0.08;
            items += sale.getItemCount();
        }
        return new ReportData(revenue, tax, items);
    }

    private Sale findTopSale(List<Sale> sales) {
        Sale topSale = null;
        for (Sale sale : sales) {
            if (topSale == null || sale.getAmount() > topSale.getAmount()) {
                topSale = sale;
            }
        }
        return topSale;
    }

    private String buildReportString(int month, int year, ReportData data, Sale topSale) {
        StringBuilder report = new StringBuilder();
        report.append("Monthly Report: ").append(month).append("/").append(year).append("\n");
        report.append("Total Revenue: $").append(String.format("%.2f", data.revenue)).append("\n");
        report.append("Total Tax: $").append(String.format("%.2f", data.tax)).append("\n");
        report.append("Total Items Sold: ").append(data.totalItems).append("\n");
        if (topSale != null) {
            report.append("Top Sale: $").append(String.format("%.2f", topSale.getAmount())).append("\n");
        }
        return report.toString();
    }
}
```

### BEFORE: Long Method (Python)

```python
def process_order(order_data):
    # Validate
    if not order_data.get("customer_id"):
        raise ValueError("Missing customer ID")
    if not order_data.get("items"):
        raise ValueError("No items in order")
    for item in order_data["items"]:
        if item["quantity"] <= 0:
            raise ValueError(f"Invalid quantity for {item['name']}")
        if item["price"] < 0:
            raise ValueError(f"Invalid price for {item['name']}")

    # Calculate totals
    subtotal = 0
    for item in order_data["items"]:
        subtotal += item["price"] * item["quantity"]
    tax = subtotal * 0.08
    discount = 0
    if subtotal > 100:
        discount = subtotal * 0.10
    total = subtotal + tax - discount

    # Create order record
    order = {
        "customer_id": order_data["customer_id"],
        "items": order_data["items"],
        "subtotal": subtotal,
        "tax": tax,
        "discount": discount,
        "total": total,
        "status": "pending"
    }
    return order
```

### AFTER: Extracted Functions (Python)

```python
def process_order(order_data):
    validate_order(order_data)
    totals = calculate_totals(order_data["items"])
    return create_order_record(order_data, totals)


def validate_order(order_data):
    if not order_data.get("customer_id"):
        raise ValueError("Missing customer ID")
    if not order_data.get("items"):
        raise ValueError("No items in order")
    for item in order_data["items"]:
        if item["quantity"] <= 0:
            raise ValueError(f"Invalid quantity for {item['name']}")
        if item["price"] < 0:
            raise ValueError(f"Invalid price for {item['name']}")


def calculate_totals(items):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax = subtotal * 0.08
    discount = subtotal * 0.10 if subtotal > 100 else 0
    return {"subtotal": subtotal, "tax": tax, "discount": discount,
            "total": subtotal + tax - discount}


def create_order_record(order_data, totals):
    return {
        "customer_id": order_data["customer_id"],
        "items": order_data["items"],
        **totals,
        "status": "pending"
    }
```

---

## 14.3 Large Class

A class that has too many responsibilities. It accumulates fields, methods, and inner classes until it becomes a "god object" that knows everything and does everything.

### How to Detect It

- The class has more than 200 to 300 lines
- It has fields that are only used by a subset of its methods
- Its name includes "Manager," "Handler," "Processor," or "Util" with many unrelated methods
- It implements more than two or three unrelated interfaces

### BEFORE: Large Class (Java)

```java
public class UserManager {
    private Database db;
    private EmailService emailService;
    private Logger logger;

    public User createUser(String name, String email) { /* ... */ }
    public User findUser(int id) { /* ... */ }
    public void updateUser(User user) { /* ... */ }
    public void deleteUser(int id) { /* ... */ }

    public void sendWelcomeEmail(User user) { /* ... */ }
    public void sendPasswordReset(User user) { /* ... */ }
    public void sendNewsletter(List<User> users) { /* ... */ }

    public boolean validatePassword(String password) { /* ... */ }
    public String hashPassword(String password) { /* ... */ }
    public boolean checkPassword(String raw, String hashed) { /* ... */ }

    public String generateReport(List<User> users) { /* ... */ }
    public void exportToCsv(List<User> users, String path) { /* ... */ }
}
```

### AFTER: Split Into Focused Classes (Java)

```java
public class UserRepository {
    private Database db;

    public User create(String name, String email) { /* ... */ }
    public User findById(int id) { /* ... */ }
    public void update(User user) { /* ... */ }
    public void delete(int id) { /* ... */ }
}

public class UserNotificationService {
    private EmailService emailService;

    public void sendWelcomeEmail(User user) { /* ... */ }
    public void sendPasswordReset(User user) { /* ... */ }
    public void sendNewsletter(List<User> users) { /* ... */ }
}

public class PasswordService {
    public boolean validate(String password) { /* ... */ }
    public String hash(String password) { /* ... */ }
    public boolean verify(String raw, String hashed) { /* ... */ }
}

public class UserReportService {
    public String generateReport(List<User> users) { /* ... */ }
    public void exportToCsv(List<User> users, String path) { /* ... */ }
}
```

```
  +------------------+         +--------------------+
  |   UserManager    |         |  UserRepository    |
  |  (God Object)    |  --->   +--------------------+
  |                  |         | UserNotification   |
  |  12+ methods     |         +--------------------+
  |  4 concerns      |         | PasswordService    |
  |                  |         +--------------------+
  +------------------+         | UserReportService  |
                               +--------------------+
       BEFORE                        AFTER
```

### BEFORE: Large Class (Python)

```python
class ShopManager:
    def __init__(self, db):
        self.db = db

    # Product methods
    def add_product(self, name, price): ...
    def remove_product(self, product_id): ...
    def update_price(self, product_id, new_price): ...

    # Order methods
    def create_order(self, customer_id, items): ...
    def cancel_order(self, order_id): ...
    def get_order_status(self, order_id): ...

    # Customer methods
    def register_customer(self, name, email): ...
    def deactivate_customer(self, customer_id): ...

    # Reporting methods
    def daily_sales_report(self): ...
    def inventory_report(self): ...
```

### AFTER: Focused Classes (Python)

```python
class ProductCatalog:
    def __init__(self, db):
        self.db = db

    def add(self, name, price): ...
    def remove(self, product_id): ...
    def update_price(self, product_id, new_price): ...


class OrderService:
    def __init__(self, db):
        self.db = db

    def create(self, customer_id, items): ...
    def cancel(self, order_id): ...
    def get_status(self, order_id): ...


class CustomerService:
    def __init__(self, db):
        self.db = db

    def register(self, name, email): ...
    def deactivate(self, customer_id): ...


class ReportGenerator:
    def __init__(self, db):
        self.db = db

    def daily_sales(self): ...
    def inventory(self): ...
```

---

## 14.4 Feature Envy

A method that uses data from another class more than from its own class. It "envies" the features of the other class and should probably live there instead.

### How to Detect It

- A method calls multiple getters on another object
- It accesses little or nothing from its own class
- Moving the method to the other class would eliminate multiple getter calls

### BEFORE: Feature Envy (Java)

```java
public class OrderPrinter {

    public String formatOrder(Order order) {
        StringBuilder sb = new StringBuilder();
        sb.append("Customer: ").append(order.getCustomer().getName()).append("\n");
        sb.append("Email: ").append(order.getCustomer().getEmail()).append("\n");
        sb.append("Address: ").append(order.getCustomer().getAddress().getStreet())
          .append(", ").append(order.getCustomer().getAddress().getCity())
          .append(", ").append(order.getCustomer().getAddress().getZip()).append("\n");
        sb.append("Total: $").append(String.format("%.2f", order.getTotal()));
        return sb.toString();
    }
}
```

The method calls `order.getCustomer()` four times and digs into `getAddress()` three times. It clearly envies the Customer and Address classes.

### AFTER: Move Behavior to the Right Class (Java)

```java
public class Customer {
    private String name;
    private String email;
    private Address address;

    public String formatContactInfo() {
        return "Customer: " + name + "\n"
             + "Email: " + email + "\n"
             + "Address: " + address.format();
    }
}

public class Address {
    private String street;
    private String city;
    private String zip;

    public String format() {
        return street + ", " + city + ", " + zip;
    }
}

public class OrderPrinter {

    public String formatOrder(Order order) {
        return order.getCustomer().formatContactInfo() + "\n"
             + "Total: $" + String.format("%.2f", order.getTotal());
    }
}
```

### BEFORE: Feature Envy (Python)

```python
class InvoiceMailer:

    def build_email_body(self, invoice):
        customer = invoice.customer
        lines = [
            f"Dear {customer.first_name} {customer.last_name},",
            f"Your invoice #{invoice.number} is ready.",
            f"Amount: ${invoice.amount:.2f}",
            f"Due: {invoice.due_date.strftime('%B %d, %Y')}",
            f"Send payment to: {customer.payment_address}",
        ]
        return "\n".join(lines)
```

### AFTER: Let the Objects Format Themselves (Python)

```python
class Customer:
    def __init__(self, first_name, last_name, payment_address):
        self.first_name = first_name
        self.last_name = last_name
        self.payment_address = payment_address

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Invoice:
    def __init__(self, number, amount, due_date, customer):
        self.number = number
        self.amount = amount
        self.due_date = due_date
        self.customer = customer

    def summary(self):
        return (f"Invoice #{self.number}\n"
                f"Amount: ${self.amount:.2f}\n"
                f"Due: {self.due_date.strftime('%B %d, %Y')}")


class InvoiceMailer:

    def build_email_body(self, invoice):
        return (f"Dear {invoice.customer.full_name()},\n"
                f"{invoice.summary()}\n"
                f"Send payment to: {invoice.customer.payment_address}")
```

---

## 14.5 Data Clumps

Groups of data items that travel together across multiple methods or classes. If you always pass the same three parameters together, they probably belong in their own object.

### How to Detect It

- The same group of parameters appears in multiple method signatures
- Multiple classes have the same group of fields
- You find yourself passing the same variables together repeatedly

### BEFORE: Data Clumps (Java)

```java
public class ShippingCalculator {

    public double calculate(String street, String city, String state, String zip,
                            double weight) {
        double distance = lookupDistance(city, state, zip);
        return distance * weight * 0.05;
    }

    public boolean validateAddress(String street, String city, String state,
                                   String zip) {
        return street != null && city != null && state != null && zip != null;
    }

    public String formatLabel(String name, String street, String city,
                              String state, String zip) {
        return name + "\n" + street + "\n" + city + ", " + state + " " + zip;
    }
}
```

The four address fields appear in every method. They form a data clump.

### AFTER: Introduce a Parameter Object (Java)

```java
public class Address {
    private final String street;
    private final String city;
    private final String state;
    private final String zip;

    public Address(String street, String city, String state, String zip) {
        this.street = street;
        this.city = city;
        this.state = state;
        this.zip = zip;
    }

    public boolean isValid() {
        return street != null && city != null && state != null && zip != null;
    }

    public String format() {
        return street + "\n" + city + ", " + state + " " + zip;
    }

    // Getters omitted for brevity
}

public class ShippingCalculator {

    public double calculate(Address address, double weight) {
        double distance = lookupDistance(address);
        return distance * weight * 0.05;
    }

    public String formatLabel(String name, Address address) {
        return name + "\n" + address.format();
    }
}
```

### BEFORE: Data Clumps (Python)

```python
def create_event(title, start_year, start_month, start_day,
                 end_year, end_month, end_day):
    ...

def is_event_today(start_year, start_month, start_day):
    ...

def format_date_range(start_year, start_month, start_day,
                      end_year, end_month, end_day):
    ...
```

### AFTER: Use a Data Class (Python)

```python
from dataclasses import dataclass
from datetime import date


@dataclass
class DateRange:
    start: date
    end: date

    def includes_today(self):
        return self.start <= date.today() <= self.end

    def format(self):
        return f"{self.start.strftime('%b %d')} - {self.end.strftime('%b %d, %Y')}"


def create_event(title, date_range: DateRange):
    ...

def format_date_range(date_range: DateRange):
    return date_range.format()
```

---

## 14.6 Primitive Obsession

Using primitive types (strings, integers, booleans) instead of small objects to represent domain concepts. An email address is not just a string. Money is not just a double. A phone number is not just an integer.

### How to Detect It

- String variables with names like `email`, `phone`, `currency`, `zipCode`
- Validation logic for the same primitive repeated across the codebase
- Methods that accept a `String` or `int` when the value has specific rules

### BEFORE: Primitive Obsession (Java)

```java
public class User {
    private String email;       // Just a string?
    private String phoneNumber; // Any format?
    private int age;            // Negative age?

    public void setEmail(String email) {
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Invalid email");
        }
        this.email = email;
    }

    public void setPhoneNumber(String phone) {
        if (phone == null || phone.length() < 10) {
            throw new IllegalArgumentException("Invalid phone");
        }
        this.phoneNumber = phone;
    }

    public void setAge(int age) {
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("Invalid age");
        }
        this.age = age;
    }
}
```

Every place that uses these values must repeat the same validation logic.

### AFTER: Value Objects (Java)

```java
public class Email {
    private final String value;

    public Email(String value) {
        if (value == null || !value.contains("@")) {
            throw new IllegalArgumentException("Invalid email: " + value);
        }
        this.value = value.toLowerCase().trim();
    }

    public String getValue() { return value; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Email)) return false;
        return value.equals(((Email) o).value);
    }

    @Override
    public int hashCode() { return value.hashCode(); }
}

public class PhoneNumber {
    private final String value;

    public PhoneNumber(String value) {
        String digits = value.replaceAll("[^0-9]", "");
        if (digits.length() < 10 || digits.length() > 15) {
            throw new IllegalArgumentException("Invalid phone number");
        }
        this.value = digits;
    }

    public String format() {
        return "(" + value.substring(0, 3) + ") "
             + value.substring(3, 6) + "-" + value.substring(6);
    }
}

public class User {
    private Email email;
    private PhoneNumber phoneNumber;
    private Age age;

    // Validation is now handled by the value objects themselves
}
```

### BEFORE: Primitive Obsession (Python)

```python
def transfer_money(from_account, to_account, amount, currency):
    if currency not in ("USD", "EUR", "GBP"):
        raise ValueError("Unsupported currency")
    if amount <= 0:
        raise ValueError("Amount must be positive")
    # Transfer logic...
```

### AFTER: Value Objects (Python)

```python
from dataclasses import dataclass
from enum import Enum


class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


@dataclass(frozen=True)
class Money:
    amount: float
    currency: Currency

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __str__(self):
        symbols = {Currency.USD: "$", Currency.EUR: "EUR", Currency.GBP: "GBP"}
        return f"{symbols[self.currency]}{self.amount:.2f}"


def transfer_money(from_account, to_account, money: Money):
    # No validation needed -- Money enforces its own rules
    ...
```

---

## 14.7 Switch Statements (and Long If-Else Chains)

A switch or long if-else chain that selects behavior based on a type code. If the same switch appears in multiple places, adding a new type means updating every switch.

### How to Detect It

- The same `switch` or `if-else` chain appears in more than one method
- Cases are added frequently as new types are introduced
- Each branch does something significantly different

### BEFORE: Switch Statement Smell (Java)

```java
public class PaymentProcessor {

    public double calculateFee(String paymentType, double amount) {
        switch (paymentType) {
            case "CREDIT_CARD": return amount * 0.03;
            case "DEBIT_CARD":  return amount * 0.01;
            case "BANK_TRANSFER": return 1.50;
            case "PAYPAL":      return amount * 0.029 + 0.30;
            default: throw new IllegalArgumentException("Unknown type");
        }
    }

    public String getConfirmationMessage(String paymentType) {
        switch (paymentType) {
            case "CREDIT_CARD": return "Charged to your credit card.";
            case "DEBIT_CARD":  return "Debited from your bank account.";
            case "BANK_TRANSFER": return "Transfer initiated.";
            case "PAYPAL":      return "PayPal payment confirmed.";
            default: throw new IllegalArgumentException("Unknown type");
        }
    }
}
```

### AFTER: Replace with Polymorphism (Java)

```java
public interface PaymentMethod {
    double calculateFee(double amount);
    String getConfirmationMessage();
}

public class CreditCardPayment implements PaymentMethod {
    public double calculateFee(double amount) { return amount * 0.03; }
    public String getConfirmationMessage() { return "Charged to your credit card."; }
}

public class DebitCardPayment implements PaymentMethod {
    public double calculateFee(double amount) { return amount * 0.01; }
    public String getConfirmationMessage() { return "Debited from your bank account."; }
}

public class BankTransferPayment implements PaymentMethod {
    public double calculateFee(double amount) { return 1.50; }
    public String getConfirmationMessage() { return "Transfer initiated."; }
}

public class PayPalPayment implements PaymentMethod {
    public double calculateFee(double amount) { return amount * 0.029 + 0.30; }
    public String getConfirmationMessage() { return "PayPal payment confirmed."; }
}

// Usage: paymentMethod.calculateFee(amount);
// Adding a new type = adding a new class. No existing code changes.
```

### BEFORE: Long If-Else Chain (Python)

```python
def get_shipping_cost(method, weight):
    if method == "standard":
        return 5.99 + weight * 0.50
    elif method == "express":
        return 12.99 + weight * 0.75
    elif method == "overnight":
        return 24.99 + weight * 1.00
    elif method == "drone":
        return 19.99 + weight * 1.25
    else:
        raise ValueError(f"Unknown shipping method: {method}")
```

### AFTER: Strategy Pattern (Python)

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod


class ShippingStrategy(ABC):
    @abstractmethod
    def cost(self, weight: float) -> float: ...


class StandardShipping(ShippingStrategy):
    def cost(self, weight): return 5.99 + weight * 0.50

class ExpressShipping(ShippingStrategy):
    def cost(self, weight): return 12.99 + weight * 0.75

class OvernightShipping(ShippingStrategy):
    def cost(self, weight): return 24.99 + weight * 1.00

class DroneShipping(ShippingStrategy):
    def cost(self, weight): return 19.99 + weight * 1.25


STRATEGIES = {
    "standard": StandardShipping(),
    "express": ExpressShipping(),
    "overnight": OvernightShipping(),
    "drone": DroneShipping(),
}

def get_shipping_cost(method: str, weight: float) -> float:
    strategy = STRATEGIES.get(method)
    if not strategy:
        raise ValueError(f"Unknown shipping method: {method}")
    return strategy.cost(weight)
```

---

## 14.8 Lazy Class

A class that does too little to justify its existence. It might have been created "just in case" or left over after a refactoring removed most of its responsibilities.

### How to Detect It

- The class has only one or two trivial methods
- It delegates everything to another class
- Removing it and inlining its logic would simplify the codebase

### BEFORE: Lazy Class (Java)

```java
public class StringFormatter {
    public String toUpperCase(String input) {
        return input.toUpperCase();
    }
}

// Used as:
StringFormatter formatter = new StringFormatter();
String result = formatter.toUpperCase(name);
```

This class adds nothing over using `String.toUpperCase()` directly.

### AFTER: Inline the Class (Java)

```java
// Just use the method directly
String result = name.toUpperCase();
```

### When Lazy Classes Are Acceptable

Sometimes a thin wrapper class exists for a good reason:

- It represents a domain concept (even if the implementation is trivial today)
- It provides a seam for testing
- It is part of an interface you do not control

### BEFORE: Lazy Class (Python)

```python
class MathHelper:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b
```

### AFTER: Just Use the Operators (Python)

```python
# No class needed. Use a + b and a * b directly.
total = price + tax
cost = quantity * unit_price
```

---

## 14.9 Speculative Generality

Code that was written "just in case" someone might need it in the future. Abstract classes with a single subclass, parameters that are never used, hooks that nobody calls.

### How to Detect It

- Abstract classes or interfaces with only one implementation
- Methods with unused parameters
- Code paths protected by flags that are never toggled
- Complex frameworks wrapping simple operations

### BEFORE: Speculative Generality (Java)

```java
public abstract class AbstractDataProcessor<T, R, E extends Exception> {
    protected abstract R preProcess(T input) throws E;
    protected abstract R process(R preprocessed) throws E;
    protected abstract R postProcess(R processed) throws E;
    protected abstract void onError(E error);
    protected abstract void onComplete(R result);

    public final R execute(T input) throws E {
        try {
            R step1 = preProcess(input);
            R step2 = process(step1);
            R result = postProcess(step2);
            onComplete(result);
            return result;
        } catch (Exception e) {
            onError((E) e);
            throw e;
        }
    }
}

// The only implementation:
public class CsvParser extends AbstractDataProcessor<String, List<String[]>, IOException> {
    // ... implements all five abstract methods for one simple use case
}
```

### AFTER: Just Write What You Need (Java)

```java
public class CsvParser {

    public List<String[]> parse(String filePath) throws IOException {
        List<String[]> rows = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                rows.add(line.split(","));
            }
        }
        return rows;
    }
}

// If you later need a second parser, THEN consider an abstraction.
```

### BEFORE: Speculative Generality (Python)

```python
class BaseNotifier(ABC):
    @abstractmethod
    def validate_recipient(self, recipient): ...

    @abstractmethod
    def format_message(self, message): ...

    @abstractmethod
    def send(self, recipient, message): ...

    @abstractmethod
    def on_success(self, recipient): ...

    @abstractmethod
    def on_failure(self, recipient, error): ...


# Only implementation:
class EmailNotifier(BaseNotifier):
    # Must implement all five methods for a simple email
    ...
```

### AFTER: Simple and Direct (Python)

```python
class EmailNotifier:
    def __init__(self, smtp_client):
        self.smtp_client = smtp_client

    def send(self, to_email, subject, body):
        self.smtp_client.send_message(to_email, subject, body)

# Add an abstraction layer ONLY when you have a second notifier type.
```

---

## 14.10 Message Chains

A series of calls like `a.getB().getC().getD().doSomething()`. The caller must know the entire chain of object relationships, creating tight coupling to the internal structure.

### How to Detect It

- Chains of three or more getter calls: `obj.getA().getB().getC()`
- Any change to an intermediate object breaks all callers
- The chain exposes internal structure that should be hidden

### BEFORE: Message Chain (Java)

```java
public class OrderShipper {

    public String getShippingLabel(Order order) {
        String street = order.getCustomer().getAddress().getStreet();
        String city = order.getCustomer().getAddress().getCity();
        String zip = order.getCustomer().getAddress().getZipCode();
        String country = order.getCustomer().getAddress().getCountry();
        return street + "\n" + city + " " + zip + "\n" + country;
    }
}
```

### AFTER: Hide the Chain (Java)

```java
public class Order {
    private Customer customer;

    public String getShippingLabel() {
        return customer.getShippingLabel();
    }
}

public class Customer {
    private Address address;

    public String getShippingLabel() {
        return address.format();
    }
}

public class Address {
    private String street, city, zipCode, country;

    public String format() {
        return street + "\n" + city + " " + zipCode + "\n" + country;
    }
}

// Now the caller only needs:
public class OrderShipper {
    public String getShippingLabel(Order order) {
        return order.getShippingLabel();
    }
}
```

### BEFORE: Message Chain (Python)

```python
# Reaching deep into nested objects
city = company.get_ceo().get_assistant().get_contact_info().get_address().city
```

### AFTER: Ask, Don't Dig (Python)

```python
# Each object exposes only what callers need
class Company:
    def ceo_assistant_city(self):
        return self._ceo.assistant_city()

class CEO:
    def assistant_city(self):
        return self._assistant.city()

class Assistant:
    def city(self):
        return self._contact_info.city

# Caller:
city = company.ceo_assistant_city()
```

> **Note:** The Law of Demeter says "only talk to your immediate friends." Message chains violate this by talking to friends of friends of friends.

---

## 14.11 Middle Man

The opposite of message chains. A class that delegates almost everything to another class, adding no value of its own. It exists only to forward calls.

### How to Detect It

- Most methods in the class just call the same method on another object
- The class adds no logic, validation, or transformation
- Callers would be just as well off talking directly to the delegate

### BEFORE: Middle Man (Java)

```java
public class Department {
    private Manager manager;

    public Employee getWorker(int id)   { return manager.getWorker(id); }
    public String getBudget()           { return manager.getBudget(); }
    public List<Project> getProjects()  { return manager.getProjects(); }
    public void addProject(Project p)   { manager.addProject(p); }
    public void removeProject(int id)   { manager.removeProject(id); }
}
```

Every method just forwards to `manager`. The `Department` class is pure overhead.

### AFTER: Remove the Middle Man (Java)

```java
// Let callers talk to the manager directly
Manager manager = department.getManager();
manager.getWorker(id);
manager.getBudget();
```

Or, if `Department` should exist as a concept, give it real behavior:

```java
public class Department {
    private Manager manager;
    private String name;
    private Budget budget;

    public boolean isOverBudget() {
        return manager.getSpending() > budget.getLimit();
    }

    public List<Employee> getAvailableWorkers() {
        return manager.getWorkers().stream()
                .filter(w -> !w.isOnLeave())
                .collect(Collectors.toList());
    }
}
```

### BEFORE: Middle Man (Python)

```python
class Facade:
    def __init__(self, service):
        self._service = service

    def get_data(self):
        return self._service.get_data()

    def save_data(self, data):
        return self._service.save_data(data)

    def delete_data(self, id):
        return self._service.delete_data(id)
```

### AFTER: Use the Service Directly (Python)

```python
# Instead of creating a Facade, just use the service:
service = DataService()
service.get_data()
service.save_data(data)
```

---

## 14.12 Smell Interaction Map

Smells rarely appear alone. One smell often leads to or masks another:

```
  +-------------------+       +---------------------+
  |   Long Method     | ----> | Feature Envy        |
  +-------------------+       +---------------------+
          |                           |
          v                           v
  +-------------------+       +---------------------+
  |   Large Class     | ----> | Data Clumps         |
  +-------------------+       +---------------------+
          |                           |
          v                           v
  +-------------------+       +---------------------+
  | Switch Statements | ----> | Primitive Obsession |
  +-------------------+       +---------------------+
          |
          v
  +-------------------+
  |  Speculative       |
  |  Generality        |
  +-------------------+

  Arrows indicate: "often leads to" or "co-occurs with"
```

---

## Common Mistakes

1. **Treating all smells as equally urgent.** Some smells in rarely-touched code are harmless. Focus on smells in code you change frequently.
2. **Refactoring smells without tests.** Always have test coverage before you start moving code around. Refactoring without tests is gambling.
3. **Over-correcting a smell.** Splitting a 25-line method into ten 3-line methods can make code harder to follow, not easier.
4. **Creating value objects for everything.** Not every string needs its own class. Apply primitive obsession fixes where validation and formatting are genuinely repeated.
5. **Confusing delegation with the middle man smell.** Delegation is healthy when the delegating class adds value. It is a smell only when it adds nothing.

---

## Best Practices

1. **Use the Boy Scout Rule.** Leave code cleaner than you found it. Fix one smell each time you visit a file.
2. **Track smells in code reviews.** Mention smells as suggestions, not blockers, unless they introduce risk.
3. **Prioritize smells in hot spots.** Use version control history to find frequently changed files -- those benefit most from smell removal.
4. **Refactor in small steps.** Address one smell at a time. Run tests after each step.
5. **Document intentional smells.** If a smell exists for a good reason, add a comment explaining why.

---

## Quick Summary

| Smell | Core Problem | Primary Fix |
|-------|-------------|-------------|
| Long Method | Too many responsibilities in one method | Extract Method |
| Large Class | Too many responsibilities in one class | Extract Class |
| Feature Envy | Method uses another class's data excessively | Move Method |
| Data Clumps | Same group of values passed together repeatedly | Introduce Parameter Object |
| Primitive Obsession | Using primitives instead of domain types | Create Value Objects |
| Switch Statements | Type-based branching duplicated across methods | Replace with Polymorphism |
| Lazy Class | Class does too little to justify existence | Inline Class |
| Speculative Generality | Abstractions built for hypothetical future needs | Remove unused abstractions |
| Message Chains | Long chains of getter calls exposing internals | Hide Delegate |
| Middle Man | Class delegates everything without adding value | Remove Middle Man |

---

## Key Points

- A code smell is a surface indicator of a deeper design problem, not a bug.
- The ten smells covered here account for the vast majority of structural problems in real codebases.
- Not every smell needs fixing. Prioritize smells in frequently changed code.
- Most smell fixes involve moving behavior to where it belongs (closer to the data it uses).
- Smells compound over time. A long method inside a large class with feature envy is exponentially harder to fix than any single smell alone.

---

## Practice Questions

1. You find a method that calls `customer.getProfile().getPreferences().getNotificationSettings().isEmailEnabled()`. Which smell is this, and how would you fix it?

2. A class called `ApplicationHelper` has 45 methods covering logging, email, file I/O, and date formatting. Which smell does it exhibit? What is your first step to fix it?

3. Three methods each accept parameters `(double latitude, double longitude, double altitude)`. Which smell is this? Write a value object class to fix it.

4. You see an abstract class `AbstractValidator<T>` with exactly one subclass: `EmailValidator`. The team says they "might need more validators later." Should you keep the abstract class or remove it? Explain your reasoning.

5. What is the difference between the middle man smell and the message chain smell? Can they exist in the same codebase simultaneously?

---

## Exercises

### Exercise 1: Smell Safari

Take a codebase you work with (or an open-source project) and find at least three different code smells from this chapter. For each one, write down:
- Which smell it is
- Why it qualifies as that smell
- What refactoring you would apply
- Whether it is urgent or can wait

### Exercise 2: Fix the Smells

Given this code, identify ALL the smells and refactor it:

```java
public class EverythingManager {
    public String processTransaction(String type, String customerName,
            String customerEmail, String customerPhone,
            double amount, String currency) {
        // Validate customer
        if (customerName == null) throw new RuntimeException("No name");
        if (!customerEmail.contains("@")) throw new RuntimeException("Bad email");

        double fee;
        if (type.equals("purchase")) {
            fee = amount * 0.02;
        } else if (type.equals("refund")) {
            fee = 0;
        } else if (type.equals("transfer")) {
            fee = 1.50;
        } else {
            throw new RuntimeException("Unknown type");
        }

        double total = amount + fee;
        String confirmation = "Transaction: " + type + "\n"
            + "Customer: " + customerName + "\n"
            + "Email: " + customerEmail + "\n"
            + "Phone: " + customerPhone + "\n"
            + "Amount: " + currency + amount + "\n"
            + "Fee: " + currency + fee + "\n"
            + "Total: " + currency + total;
        return confirmation;
    }
}
```

Identify: long method, data clumps (customer fields), primitive obsession (email, phone, money), switch statement smell, and large class tendencies.

### Exercise 3: Smell or Not a Smell?

For each scenario, decide whether it is a code smell and explain why or why not:

1. A `Logger` class that wraps `System.out.println` with timestamp formatting
2. A 50-line method that performs a single complex mathematical calculation with no branches
3. An `enum` with a switch statement that handles all cases in exactly one place in the codebase

---

## What Is Next?

Now that you can recognize code smells, the next chapter teaches you the specific techniques to fix them. Chapter 15: Refactoring Techniques gives you a toolbox of safe, systematic transformations that turn smelly code into clean code -- one step at a time.
