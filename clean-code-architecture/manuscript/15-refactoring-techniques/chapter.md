# Chapter 15: Refactoring Techniques -- Your Toolbox for Clean Code

## What You Will Learn

- Seven essential refactoring techniques that solve the most common code smells
- How to apply each technique safely with step-by-step before-and-after examples
- The critical role of tests in making refactoring safe
- When each technique is appropriate and when it is overkill
- How to chain multiple techniques to transform messy code into clean code
- Refactoring in both Java and Python with idiomatic patterns for each language

## Why This Chapter Matters

Recognizing code smells (Chapter 14) is only half the battle. You also need the skill to fix them safely. Refactoring is the disciplined process of restructuring existing code without changing its external behavior. The key word is "disciplined" -- refactoring is not hacking at code until it looks different. Each technique here has a clear intent, a clear procedure, and clear before-and-after states. Master these seven techniques, and you can handle the vast majority of code quality improvements you will encounter in your career.

---

## The Safety Net: Tests Before Refactoring

Before applying any refactoring technique, you need a safety net.

```
  +----------------------------------------------+
  |         THE REFACTORING SAFETY RULE           |
  +----------------------------------------------+
  |                                                |
  |  1. Verify existing tests pass                 |
  |  2. Apply ONE refactoring step                 |
  |  3. Run tests again                            |
  |  4. If tests pass --> commit                   |
  |  5. If tests fail --> revert and try again     |
  |                                                |
  |  NEVER skip step 1. NEVER combine steps.       |
  +----------------------------------------------+
```

If there are no tests, write characterization tests first. These tests capture the current behavior (even if it is wrong) so you can verify that your refactoring does not change it.

---

## 15.1 Extract Method

### Intent

Take a fragment of code inside a long method and turn it into its own method with a descriptive name.

### When to Use It

- A method is too long to understand at a glance
- A comment explains what the next block of code does (the method name replaces the comment)
- The same code fragment appears in multiple places

### BEFORE: Java

```java
public class InvoiceProcessor {

    public void printInvoice(Invoice invoice) {
        System.out.println("=== INVOICE ===");
        System.out.println("Date: " + invoice.getDate());

        // Print line items
        double total = 0;
        for (LineItem item : invoice.getItems()) {
            double lineTotal = item.getQuantity() * item.getPrice();
            System.out.println(item.getName() + " x" + item.getQuantity()
                    + " = $" + String.format("%.2f", lineTotal));
            total += lineTotal;
        }

        // Apply discount
        double discount = 0;
        if (total > 500) {
            discount = total * 0.10;
        } else if (total > 200) {
            discount = total * 0.05;
        }

        // Print summary
        System.out.println("Subtotal: $" + String.format("%.2f", total));
        System.out.println("Discount: $" + String.format("%.2f", discount));
        System.out.println("Total: $" + String.format("%.2f", total - discount));
    }
}
```

### AFTER: Java

```java
public class InvoiceProcessor {

    public void printInvoice(Invoice invoice) {
        printHeader(invoice);
        double subtotal = printLineItems(invoice.getItems());
        double discount = calculateDiscount(subtotal);
        printSummary(subtotal, discount);
    }

    private void printHeader(Invoice invoice) {
        System.out.println("=== INVOICE ===");
        System.out.println("Date: " + invoice.getDate());
    }

    private double printLineItems(List<LineItem> items) {
        double total = 0;
        for (LineItem item : items) {
            double lineTotal = item.getQuantity() * item.getPrice();
            System.out.println(item.getName() + " x" + item.getQuantity()
                    + " = $" + String.format("%.2f", lineTotal));
            total += lineTotal;
        }
        return total;
    }

    private double calculateDiscount(double total) {
        if (total > 500) return total * 0.10;
        if (total > 200) return total * 0.05;
        return 0;
    }

    private void printSummary(double subtotal, double discount) {
        System.out.println("Subtotal: $" + String.format("%.2f", subtotal));
        System.out.println("Discount: $" + String.format("%.2f", discount));
        System.out.println("Total: $" + String.format("%.2f", subtotal - discount));
    }
}
```

### BEFORE: Python

```python
def generate_report(employees):
    report_lines = []

    # Calculate statistics
    total_salary = sum(e.salary for e in employees)
    avg_salary = total_salary / len(employees) if employees else 0
    max_salary = max((e.salary for e in employees), default=0)
    min_salary = min((e.salary for e in employees), default=0)

    # Group by department
    departments = {}
    for emp in employees:
        dept = emp.department
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(emp)

    # Build report
    report_lines.append(f"Total Employees: {len(employees)}")
    report_lines.append(f"Average Salary: ${avg_salary:,.2f}")
    report_lines.append(f"Salary Range: ${min_salary:,.2f} - ${max_salary:,.2f}")
    report_lines.append("")
    for dept, members in sorted(departments.items()):
        report_lines.append(f"  {dept}: {len(members)} employees")

    return "\n".join(report_lines)
```

### AFTER: Python

```python
def generate_report(employees):
    stats = calculate_salary_stats(employees)
    departments = group_by_department(employees)
    return build_report(stats, departments, len(employees))


def calculate_salary_stats(employees):
    if not employees:
        return {"total": 0, "average": 0, "max": 0, "min": 0}
    salaries = [e.salary for e in employees]
    total = sum(salaries)
    return {
        "total": total,
        "average": total / len(employees),
        "max": max(salaries),
        "min": min(salaries),
    }


def group_by_department(employees):
    departments = {}
    for emp in employees:
        departments.setdefault(emp.department, []).append(emp)
    return departments


def build_report(stats, departments, count):
    lines = [
        f"Total Employees: {count}",
        f"Average Salary: ${stats['average']:,.2f}",
        f"Salary Range: ${stats['min']:,.2f} - ${stats['max']:,.2f}",
        "",
    ]
    for dept, members in sorted(departments.items()):
        lines.append(f"  {dept}: {len(members)} employees")
    return "\n".join(lines)
```

### Step-by-Step Procedure

1. Create a new method with a name that describes **what** the code does, not **how**
2. Copy the code fragment into the new method
3. Identify local variables used in the fragment -- pass them as parameters
4. Identify local variables modified in the fragment -- return them
5. Replace the original fragment with a call to the new method
6. Run tests

---

## 15.2 Extract Class

### Intent

Take a class that is doing the work of two and split it into two classes, each with a single responsibility.

### When to Use It

- A class has fields or methods that form a natural subgroup
- You can name the subgroup with a meaningful domain term
- The class has more than one reason to change

### BEFORE: Java

```java
public class Employee {
    private String name;
    private String employeeId;

    // Address fields -- these belong together
    private String street;
    private String city;
    private String state;
    private String zipCode;

    // Phone fields -- these belong together
    private String areaCode;
    private String phoneNumber;

    public String getFullAddress() {
        return street + "\n" + city + ", " + state + " " + zipCode;
    }

    public String getFormattedPhone() {
        return "(" + areaCode + ") " + phoneNumber;
    }

    // ... employee-specific methods
}
```

### AFTER: Java

```java
public class Address {
    private String street;
    private String city;
    private String state;
    private String zipCode;

    public Address(String street, String city, String state, String zipCode) {
        this.street = street;
        this.city = city;
        this.state = state;
        this.zipCode = zipCode;
    }

    public String format() {
        return street + "\n" + city + ", " + state + " " + zipCode;
    }
}

public class PhoneNumber {
    private String areaCode;
    private String number;

    public PhoneNumber(String areaCode, String number) {
        this.areaCode = areaCode;
        this.number = number;
    }

    public String format() {
        return "(" + areaCode + ") " + number;
    }
}

public class Employee {
    private String name;
    private String employeeId;
    private Address address;
    private PhoneNumber phone;

    public String getFullAddress() { return address.format(); }
    public String getFormattedPhone() { return phone.format(); }
}
```

### BEFORE: Python

```python
class Order:
    def __init__(self, order_id, customer_name, customer_email,
                 customer_tier, items):
        self.order_id = order_id
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.customer_tier = customer_tier
        self.items = items

    def customer_display(self):
        return f"{self.customer_name} ({self.customer_email})"

    def customer_discount_rate(self):
        rates = {"gold": 0.15, "silver": 0.10, "bronze": 0.05}
        return rates.get(self.customer_tier, 0)

    def total(self):
        raw = sum(i.price * i.quantity for i in self.items)
        return raw * (1 - self.customer_discount_rate())
```

### AFTER: Python

```python
from dataclasses import dataclass


@dataclass
class Customer:
    name: str
    email: str
    tier: str

    def display(self):
        return f"{self.name} ({self.email})"

    def discount_rate(self):
        rates = {"gold": 0.15, "silver": 0.10, "bronze": 0.05}
        return rates.get(self.tier, 0)


class Order:
    def __init__(self, order_id, customer: Customer, items):
        self.order_id = order_id
        self.customer = customer
        self.items = items

    def total(self):
        raw = sum(i.price * i.quantity for i in self.items)
        return raw * (1 - self.customer.discount_rate())
```

### Step-by-Step Procedure

1. Identify the group of fields and methods that belong together
2. Create a new class with a descriptive name
3. Move the related fields to the new class
4. Move the related methods to the new class
5. Replace the old fields with a single reference to the new class
6. Update all callers to use the new structure
7. Run tests

---

## 15.3 Rename (Method, Variable, Class)

### Intent

Change the name of a method, variable, or class to better communicate its purpose. This is the simplest refactoring, yet one of the most impactful.

### When to Use It

- A name is misleading, abbreviated, or unclear
- You had to read the implementation to understand what a method does
- A name no longer reflects what the code actually does after changes

### BEFORE: Java

```java
public class Proc {
    private List<Map<String, Object>> d;

    public double calc(Map<String, Object> r) {
        double t = 0;
        for (Map<String, Object> i : d) {
            double p = (double) i.get("p");
            int q = (int) i.get("q");
            t += p * q;
        }
        double tx = t * 0.08;
        return t + tx;
    }

    public boolean chk(String s) {
        return s != null && s.length() > 0;
    }
}
```

### AFTER: Java

```java
public class OrderCalculator {
    private List<Map<String, Object>> lineItems;

    public double calculateTotal(Map<String, Object> order) {
        double subtotal = 0;
        for (Map<String, Object> item : lineItems) {
            double price = (double) item.get("price");
            int quantity = (int) item.get("quantity");
            subtotal += price * quantity;
        }
        double tax = subtotal * 0.08;
        return subtotal + tax;
    }

    public boolean isNotEmpty(String value) {
        return value != null && value.length() > 0;
    }
}
```

### BEFORE: Python

```python
def proc(lst, n):
    r = []
    for x in lst:
        if x.s == n:
            r.append(x)
    return r

def fmt(u):
    return f"{u.fn} {u.ln} <{u.e}>"
```

### AFTER: Python

```python
def filter_by_status(tasks, status):
    return [task for task in tasks if task.status == status]

def format_user_display(user):
    return f"{user.first_name} {user.last_name} <{user.email}>"
```

### Naming Guidelines

```
  +-----------------------------------------------------+
  |              GOOD NAMING CHECKLIST                   |
  +-----------------------------------------------------+
  |                                                      |
  |  [x]  Reveals intent: calculateTotal, not calc       |
  |  [x]  Uses domain language: Invoice, not DataObj     |
  |  [x]  Pronounceable: customer, not cstmr             |
  |  [x]  Searchable: MAX_RETRY_COUNT, not 3             |
  |  [x]  No misleading abbreviations                    |
  |  [x]  Consistent with codebase conventions           |
  |                                                      |
  +-----------------------------------------------------+
```

---

## 15.4 Move Method

### Intent

Move a method from one class to another where it is a better fit -- typically to the class whose data it uses most.

### When to Use It

- A method uses more data from another class than from its own (feature envy)
- Moving the method would reduce coupling between classes
- The method does not make sense as a responsibility of its current class

### BEFORE: Java

```java
public class Account {
    private double balance;
    private String type; // "savings" or "checking"

    public double getBalance() { return balance; }
    public String getType() { return type; }
}

public class BankReport {

    public double calculateInterest(Account account) {
        if (account.getType().equals("savings")) {
            return account.getBalance() * 0.04;
        } else if (account.getType().equals("checking")) {
            return account.getBalance() * 0.01;
        }
        return 0;
    }

    public boolean isEligibleForLoan(Account account) {
        return account.getBalance() > 1000
            && account.getType().equals("savings");
    }
}
```

Both methods in `BankReport` depend entirely on `Account` data. They belong in `Account`.

### AFTER: Java

```java
public class Account {
    private double balance;
    private String type;

    public double calculateInterest() {
        if ("savings".equals(type)) return balance * 0.04;
        if ("checking".equals(type)) return balance * 0.01;
        return 0;
    }

    public boolean isEligibleForLoan() {
        return balance > 1000 && "savings".equals(type);
    }

    public double getBalance() { return balance; }
    public String getType() { return type; }
}

public class BankReport {
    // BankReport now calls account.calculateInterest()
    // instead of doing the calculation itself
}
```

### BEFORE: Python

```python
class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class GeometryUtils:
    def area(self, rect: Rectangle):
        return rect.width * rect.height

    def perimeter(self, rect: Rectangle):
        return 2 * (rect.width + rect.height)

    def contains_point(self, rect: Rectangle, px, py):
        return (rect.x <= px <= rect.x + rect.width
                and rect.y <= py <= rect.y + rect.height)
```

### AFTER: Python

```python
class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def contains_point(self, px, py):
        return (self.x <= px <= self.x + self.width
                and self.y <= py <= self.y + self.height)
```

### Step-by-Step Procedure

1. Examine all features (fields, methods) used by the method
2. Check if there is another method in the source class that depends on this one
3. Declare the method in the target class
4. Copy the body and adjust references (use `this`/`self` for the target class)
5. Turn the old method into a delegating method (or remove it and update callers)
6. Run tests

---

## 15.5 Replace Conditional with Polymorphism

### Intent

Replace a conditional (if-else chain or switch statement) that selects behavior based on type with polymorphism. Each branch becomes a separate class that implements a shared interface.

### When to Use It

- The same conditional appears in multiple methods
- New types are added frequently, requiring updates to every conditional
- Each branch contains significantly different logic

### BEFORE: Java

```java
public class AreaCalculator {

    public double calculateArea(String shape, double[] dimensions) {
        switch (shape) {
            case "circle":
                return Math.PI * dimensions[0] * dimensions[0];
            case "rectangle":
                return dimensions[0] * dimensions[1];
            case "triangle":
                return 0.5 * dimensions[0] * dimensions[1];
            default:
                throw new IllegalArgumentException("Unknown shape: " + shape);
        }
    }

    public String describe(String shape) {
        switch (shape) {
            case "circle":    return "A round shape with a radius";
            case "rectangle": return "A four-sided shape with width and height";
            case "triangle":  return "A three-sided shape with base and height";
            default: throw new IllegalArgumentException("Unknown shape");
        }
    }
}
```

### AFTER: Java

```java
public interface Shape {
    double area();
    String describe();
}

public class Circle implements Shape {
    private final double radius;

    public Circle(double radius) { this.radius = radius; }

    public double area() { return Math.PI * radius * radius; }
    public String describe() { return "A round shape with radius " + radius; }
}

public class Rectangle implements Shape {
    private final double width;
    private final double height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }

    public double area() { return width * height; }
    public String describe() {
        return "A four-sided shape (" + width + " x " + height + ")";
    }
}

public class Triangle implements Shape {
    private final double base;
    private final double height;

    public Triangle(double base, double height) {
        this.base = base;
        this.height = height;
    }

    public double area() { return 0.5 * base * height; }
    public String describe() {
        return "A three-sided shape (base=" + base + ", height=" + height + ")";
    }
}

// Usage:
// Shape shape = new Circle(5);
// shape.area();       // No switch needed
// shape.describe();   // No switch needed
```

```
  BEFORE                          AFTER
  +------------------+            +-----------+
  | AreaCalculator   |            | <<Shape>> |
  |                  |            +-----------+
  | switch(shape)    |            | area()    |
  |   circle: ...    |    --->    | describe()|
  |   rect: ...      |            +-----+-----+
  |   tri: ...       |                  |
  +------------------+        +---------+---------+
                              |         |         |
                          +-------+ +-------+ +--------+
                          |Circle | | Rect  | |Triangle|
                          +-------+ +-------+ +--------+
```

### BEFORE: Python

```python
class NotificationSender:

    def send(self, notification_type, recipient, message):
        if notification_type == "email":
            print(f"Sending email to {recipient}: {message}")
            # email-specific logic
        elif notification_type == "sms":
            if len(message) > 160:
                message = message[:157] + "..."
            print(f"Sending SMS to {recipient}: {message}")
        elif notification_type == "push":
            print(f"Sending push notification to {recipient}: {message}")
            # push-specific logic
        else:
            raise ValueError(f"Unknown type: {notification_type}")

    def cost(self, notification_type):
        if notification_type == "email":
            return 0.001
        elif notification_type == "sms":
            return 0.05
        elif notification_type == "push":
            return 0.002
        else:
            raise ValueError(f"Unknown type: {notification_type}")
```

### AFTER: Python

```python
from abc import ABC, abstractmethod


class Notification(ABC):
    @abstractmethod
    def send(self, recipient, message): ...

    @abstractmethod
    def cost(self) -> float: ...


class EmailNotification(Notification):
    def send(self, recipient, message):
        print(f"Sending email to {recipient}: {message}")

    def cost(self):
        return 0.001


class SmsNotification(Notification):
    def send(self, recipient, message):
        if len(message) > 160:
            message = message[:157] + "..."
        print(f"Sending SMS to {recipient}: {message}")

    def cost(self):
        return 0.05


class PushNotification(Notification):
    def send(self, recipient, message):
        print(f"Sending push to {recipient}: {message}")

    def cost(self):
        return 0.002


# Adding a new type = adding a new class. No existing code changes.
```

---

## 15.6 Introduce Parameter Object

### Intent

Replace a recurring group of parameters with a single object that carries them together.

### When to Use It

- The same group of parameters appears in multiple method signatures
- Parameters that always travel together suggest a missing concept in your domain
- Method signatures are getting unwieldy (more than three or four parameters)

### BEFORE: Java

```java
public class EventService {

    public List<Event> findEvents(LocalDate startDate, LocalDate endDate,
                                   String city, int maxResults) {
        // ...
    }

    public int countEvents(LocalDate startDate, LocalDate endDate,
                           String city) {
        // ...
    }

    public List<Event> findPopularEvents(LocalDate startDate, LocalDate endDate,
                                          String city, int minAttendees) {
        // ...
    }
}
```

### AFTER: Java

```java
public class EventSearchCriteria {
    private final LocalDate startDate;
    private final LocalDate endDate;
    private final String city;

    public EventSearchCriteria(LocalDate startDate, LocalDate endDate, String city) {
        if (endDate.isBefore(startDate)) {
            throw new IllegalArgumentException("End date must be after start date");
        }
        this.startDate = startDate;
        this.endDate = endDate;
        this.city = city;
    }

    public int durationInDays() {
        return (int) ChronoUnit.DAYS.between(startDate, endDate);
    }

    // Getters...
}

public class EventService {

    public List<Event> findEvents(EventSearchCriteria criteria, int maxResults) {
        // ...
    }

    public int countEvents(EventSearchCriteria criteria) {
        // ...
    }

    public List<Event> findPopularEvents(EventSearchCriteria criteria,
                                          int minAttendees) {
        // ...
    }
}
```

Notice how the parameter object also became a natural home for the `durationInDays()` method and date validation logic.

### BEFORE: Python

```python
def create_user(first_name, last_name, email, phone, role, department):
    ...

def update_user(user_id, first_name, last_name, email, phone, role, department):
    ...

def format_user(first_name, last_name, email, role):
    return f"{first_name} {last_name} ({role}) - {email}"
```

### AFTER: Python

```python
from dataclasses import dataclass


@dataclass
class UserInfo:
    first_name: str
    last_name: str
    email: str
    phone: str
    role: str
    department: str

    def display_name(self):
        return f"{self.first_name} {self.last_name}"

    def format(self):
        return f"{self.display_name()} ({self.role}) - {self.email}"


def create_user(info: UserInfo):
    ...

def update_user(user_id, info: UserInfo):
    ...
```

---

## 15.7 Replace Magic Number with Named Constant

### Intent

Replace a literal number (or string) that has a particular meaning with a named constant that explains that meaning.

### When to Use It

- A number appears in the code without explanation
- The same literal value appears in multiple places
- Changing the value would require hunting through the codebase

### BEFORE: Java

```java
public class TaxCalculator {

    public double calculateTax(double income) {
        if (income <= 10275) {
            return income * 0.10;
        } else if (income <= 41775) {
            return 1027.50 + (income - 10275) * 0.12;
        } else if (income <= 89075) {
            return 4807.50 + (income - 41775) * 0.22;
        } else {
            return 15213.50 + (income - 89075) * 0.24;
        }
    }
}
```

What do these numbers mean? Where do they come from? If tax brackets change, how many places must you update?

### AFTER: Java

```java
public class TaxCalculator {

    private static final double BRACKET_1_LIMIT = 10_275.00;
    private static final double BRACKET_2_LIMIT = 41_775.00;
    private static final double BRACKET_3_LIMIT = 89_075.00;

    private static final double RATE_BRACKET_1 = 0.10;
    private static final double RATE_BRACKET_2 = 0.12;
    private static final double RATE_BRACKET_3 = 0.22;
    private static final double RATE_BRACKET_4 = 0.24;

    private static final double BASE_TAX_BRACKET_2 = 1_027.50;
    private static final double BASE_TAX_BRACKET_3 = 4_807.50;
    private static final double BASE_TAX_BRACKET_4 = 15_213.50;

    public double calculateTax(double income) {
        if (income <= BRACKET_1_LIMIT) {
            return income * RATE_BRACKET_1;
        } else if (income <= BRACKET_2_LIMIT) {
            return BASE_TAX_BRACKET_2 + (income - BRACKET_1_LIMIT) * RATE_BRACKET_2;
        } else if (income <= BRACKET_3_LIMIT) {
            return BASE_TAX_BRACKET_3 + (income - BRACKET_2_LIMIT) * RATE_BRACKET_3;
        } else {
            return BASE_TAX_BRACKET_4 + (income - BRACKET_3_LIMIT) * RATE_BRACKET_4;
        }
    }
}
```

### BEFORE: Python

```python
def calculate_shipping(weight, distance):
    if weight > 50:
        return distance * 0.75 + 15.00
    elif weight > 20:
        return distance * 0.50 + 8.00
    else:
        return distance * 0.25 + 3.00

def is_eligible_for_free_shipping(order_total):
    return order_total >= 75.00

def apply_loyalty_discount(price, years):
    if years >= 5:
        return price * 0.85
    elif years >= 2:
        return price * 0.90
    return price
```

### AFTER: Python

```python
# Shipping thresholds
HEAVY_PACKAGE_WEIGHT_KG = 50
MEDIUM_PACKAGE_WEIGHT_KG = 20

HEAVY_RATE_PER_KM = 0.75
MEDIUM_RATE_PER_KM = 0.50
LIGHT_RATE_PER_KM = 0.25

HEAVY_BASE_FEE = 15.00
MEDIUM_BASE_FEE = 8.00
LIGHT_BASE_FEE = 3.00

FREE_SHIPPING_THRESHOLD = 75.00

# Loyalty discounts
GOLD_LOYALTY_YEARS = 5
SILVER_LOYALTY_YEARS = 2
GOLD_DISCOUNT_MULTIPLIER = 0.85
SILVER_DISCOUNT_MULTIPLIER = 0.90


def calculate_shipping(weight, distance):
    if weight > HEAVY_PACKAGE_WEIGHT_KG:
        return distance * HEAVY_RATE_PER_KM + HEAVY_BASE_FEE
    elif weight > MEDIUM_PACKAGE_WEIGHT_KG:
        return distance * MEDIUM_RATE_PER_KM + MEDIUM_BASE_FEE
    else:
        return distance * LIGHT_RATE_PER_KM + LIGHT_BASE_FEE


def is_eligible_for_free_shipping(order_total):
    return order_total >= FREE_SHIPPING_THRESHOLD


def apply_loyalty_discount(price, years):
    if years >= GOLD_LOYALTY_YEARS:
        return price * GOLD_DISCOUNT_MULTIPLIER
    elif years >= SILVER_LOYALTY_YEARS:
        return price * SILVER_DISCOUNT_MULTIPLIER
    return price
```

### When NOT to Replace

Some numbers are self-explanatory and do not need a constant:

```java
// These are fine as literals:
int[] pair = new int[2];          // 2 elements in a pair is obvious
double half = total / 2.0;        // Dividing by 2 is obvious
String empty = "";                // Empty string is obvious
```

---

## 15.8 Chaining Techniques Together

Real-world refactoring rarely uses a single technique in isolation. Here is an example that combines multiple techniques:

### BEFORE: Multiple Smells (Java)

```java
public class ReportManager {
    public String generate(List<Map<String, Object>> data, String type,
                           int year, int month, int day,
                           double threshold) {
        // Filter
        List<Map<String, Object>> filtered = new ArrayList<>();
        for (Map<String, Object> row : data) {
            double val = (double) row.get("value");
            if (val >= threshold) {
                filtered.add(row);
            }
        }

        // Format
        StringBuilder sb = new StringBuilder();
        if (type.equals("summary")) {
            double total = 0;
            for (Map<String, Object> row : filtered) {
                total += (double) row.get("value");
            }
            sb.append("Summary for ").append(month).append("/")
              .append(day).append("/").append(year).append("\n");
            sb.append("Total: ").append(total).append("\n");
            sb.append("Count: ").append(filtered.size());
        } else if (type.equals("detail")) {
            sb.append("Detail for ").append(month).append("/")
              .append(day).append("/").append(year).append("\n");
            for (Map<String, Object> row : filtered) {
                sb.append("  ").append(row.get("name"))
                  .append(": ").append(row.get("value")).append("\n");
            }
        }
        return sb.toString();
    }
}
```

### AFTER: Multiple Techniques Applied

```java
// Technique: Introduce Parameter Object (date clump)
public class ReportDate {
    private final int year, month, day;

    public ReportDate(int year, int month, int day) {
        this.year = year; this.month = month; this.day = day;
    }

    public String format() {
        return month + "/" + day + "/" + year;
    }
}

// Technique: Replace Conditional with Polymorphism
public interface ReportFormatter {
    String format(List<Map<String, Object>> data, ReportDate date);
}

public class SummaryFormatter implements ReportFormatter {
    public String format(List<Map<String, Object>> data, ReportDate date) {
        double total = data.stream()
                .mapToDouble(r -> (double) r.get("value")).sum();
        return "Summary for " + date.format() + "\n"
             + "Total: " + total + "\n"
             + "Count: " + data.size();
    }
}

public class DetailFormatter implements ReportFormatter {
    public String format(List<Map<String, Object>> data, ReportDate date) {
        StringBuilder sb = new StringBuilder();
        sb.append("Detail for ").append(date.format()).append("\n");
        for (Map<String, Object> row : data) {
            sb.append("  ").append(row.get("name"))
              .append(": ").append(row.get("value")).append("\n");
        }
        return sb.toString();
    }
}

// Technique: Extract Method (filtering)
public class ReportGenerator {
    private final ReportFormatter formatter;

    public ReportGenerator(ReportFormatter formatter) {
        this.formatter = formatter;
    }

    public String generate(List<Map<String, Object>> data,
                           ReportDate date, double threshold) {
        List<Map<String, Object>> filtered = filterByThreshold(data, threshold);
        return formatter.format(filtered, date);
    }

    private List<Map<String, Object>> filterByThreshold(
            List<Map<String, Object>> data, double threshold) {
        return data.stream()
                .filter(row -> (double) row.get("value") >= threshold)
                .collect(Collectors.toList());
    }
}
```

---

## Common Mistakes

1. **Refactoring without tests.** Every refactoring technique assumes you can verify behavior has not changed. Without tests, you are just editing code and hoping.
2. **Doing too much at once.** Apply one technique, run tests, commit. Then apply the next. Combining multiple changes into one big step makes it impossible to isolate problems.
3. **Over-extracting.** Not every three-line block deserves its own method. Extract only when the method name adds clarity.
4. **Renaming to satisfy a style guide but losing meaning.** A name like `processData` renamed to `handleData` is not a refactoring -- it is just shuffling words. Rename to reveal intent.
5. **Creating parameter objects with no behavior.** A parameter object that is just a data carrier misses the opportunity to move validation and formatting logic into the object.

---

## Best Practices

1. **Refactor on Green.** Only refactor when all tests pass. If tests are failing, fix the bug first.
2. **Use your IDE's refactoring tools.** Modern IDEs (IntelliJ, VS Code, PyCharm) automate Extract Method, Rename, and Move Method safely. Use them instead of manual editing.
3. **Commit after each successful refactoring.** Small commits let you revert a single change if something goes wrong.
4. **Follow the Boy Scout Rule.** Refactor a little bit every time you touch a file. Small, continuous improvements are more effective than big refactoring sprints.
5. **Refactor toward a goal.** Do not refactor aimlessly. Have a specific smell you are removing or a specific design you are moving toward.

---

## Quick Summary

| Technique | Fixes This Smell | Core Action |
|-----------|-----------------|-------------|
| Extract Method | Long Method | Pull code into a named method |
| Extract Class | Large Class | Split class into two |
| Rename | Unclear names | Change name to reveal intent |
| Move Method | Feature Envy | Move method to the class it envies |
| Replace Conditional with Polymorphism | Switch Statements | Each branch becomes a class |
| Introduce Parameter Object | Data Clumps | Group related parameters into a class |
| Replace Magic Number with Constant | Mysterious literals | Give meaningful names to numbers |

---

## Key Points

- Refactoring changes code structure without changing behavior. Tests verify this.
- Each technique targets a specific smell. Knowing which technique to apply is as important as knowing how.
- Small steps with frequent test runs are the safest way to refactor.
- IDE refactoring tools eliminate an entire category of errors. Use them.
- Real refactoring combines multiple techniques. Master each one individually, then learn to chain them.

---

## Practice Questions

1. You have a 60-line method with three distinct sections separated by comments. Which refactoring technique should you apply first? What would you name the extracted methods?

2. A method `calculatePrice(String itemType, double basePrice, int quantity, boolean isMember, String couponCode)` has five parameters. Which technique would reduce this to a cleaner signature? Design the parameter object.

3. You find this code: `if (status == 1) ... else if (status == 2) ... else if (status == 3) ...`. The same pattern appears in four different methods. Which technique fixes this? Outline the class hierarchy you would create.

4. A class `DataProcessor` has methods that call `record.getAccount().getOwner().getEmail()` frequently. Which smell is this, and which two refactoring techniques could fix it?

5. When is it acceptable to NOT replace a magic number with a named constant? Give two examples.

---

## Exercises

### Exercise 1: Extract and Rename

Take this function and apply Extract Method and Rename to make it readable:

```python
def p(d):
    r = []
    for x in d:
        if x["t"] == "A" and x["v"] > 100:
            r.append({"n": x["n"], "v": x["v"] * 1.1})
        elif x["t"] == "B":
            r.append({"n": x["n"], "v": x["v"] * 0.9})
    s = sum(i["v"] for i in r)
    return {"items": r, "total": s}
```

### Exercise 2: Full Refactoring

Refactor this Java class using at least three different techniques from this chapter:

```java
public class OrderHandler {
    public String handle(String cType, String cName, String cEmail,
                         String item, int qty, double price, String promoCode) {
        double total = qty * price;
        double discount = 0;
        if (promoCode != null) {
            if (promoCode.equals("SAVE10")) discount = total * 0.10;
            else if (promoCode.equals("SAVE20")) discount = total * 0.20;
            else if (promoCode.equals("HALF")) discount = total * 0.50;
        }
        if (cType.equals("VIP")) discount += total * 0.05;
        total = total - discount;
        double tax = total * 0.0825;
        return "Order for " + cName + " (" + cEmail + ")\n"
            + item + " x" + qty + "\n"
            + "Subtotal: $" + total + "\n"
            + "Tax: $" + tax + "\n"
            + "Total: $" + (total + tax);
    }
}
```

Identify the smells first, then apply the appropriate technique for each one.

### Exercise 3: Refactoring Plan

You inherit a 500-line class called `ApplicationController` that handles user authentication, request routing, input validation, and response formatting. Write a refactoring plan that uses techniques from this chapter. List the steps in order, and explain why you chose that order.

---

## What Is Next?

Refactoring makes existing code better. But how do you know the code works correctly before, during, and after refactoring? The answer is testing. Chapter 16: Unit Testing Principles teaches you how to write tests that are fast, reliable, and meaningful -- the safety net that makes refactoring possible.
