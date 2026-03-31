# Chapter 5: Formatting -- The Silent Communicator

---

## What You Will Learn

- Why code formatting is a communication tool, not a cosmetic preference
- The newspaper metaphor and how it guides vertical formatting decisions
- How vertical openness and density make code scannable at a glance
- Horizontal formatting rules including line length and indentation
- Why team rules always beat personal preferences
- How to use linters and formatters to enforce consistency automatically
- Practical before-and-after transformations in Java and Python

---

## Why This Chapter Matters

You will spend far more time reading code than writing it. Every study on developer behavior confirms this. If code formatting is inconsistent, every reader has to decode the layout before they can understand the logic. That cognitive overhead adds up to hours, days, and weeks of lost productivity across a team.

Formatting is not about making code pretty. It is about making code communicable. A well-formatted codebase tells you where things are, what belongs together, and what is separate -- all before you read a single keyword. A poorly formatted codebase makes every file feel like a puzzle.

This chapter will give you concrete rules and tools to make formatting automatic, consistent, and effortless.

---

## The Newspaper Metaphor

Think about how a newspaper article is structured. At the top, you get a headline that tells you what the article is about. Below that, a summary paragraph gives you the key facts. As you read further down, you get more and more detail. You can stop reading at any point and still have a useful understanding of the story.

Your source code files should work the same way.

```
+-----------------------------------------------+
|          THE NEWSPAPER METAPHOR                |
+-----------------------------------------------+
|                                                |
|  HEADLINE          --> Class name / file name  |
|                                                |
|  Summary paragraph --> Public methods,         |
|                        high-level API          |
|                                                |
|  Supporting details --> Private methods,        |
|                        helper functions         |
|                                                |
|  Fine print         --> Low-level utilities,    |
|                        constants, config        |
|                                                |
+-----------------------------------------------+
|  Reader can stop at any level and still        |
|  understand the purpose of the code.           |
+-----------------------------------------------+
```

### Headline First, Details Later

The name of the file or class is your headline. The first few methods should be the high-level public interface -- the "what" of the code. As you scroll down, the methods become more detailed, more specific, more "how."

**BEFORE -- Details before headline:**

```java
// Java -- BAD: Implementation details at the top, purpose buried below
public class ReportGenerator {

    private String sanitizeInput(String raw) {
        return raw.replaceAll("[^a-zA-Z0-9 ]", "").trim();
    }

    private List<String> splitIntoLines(String data) {
        return Arrays.asList(data.split("\n"));
    }

    private String formatLine(String line, int width) {
        return String.format("%-" + width + "s", line);
    }

    private void writeToFile(String content, String path) {
        try (FileWriter writer = new FileWriter(path)) {
            writer.write(content);
        } catch (IOException e) {
            throw new RuntimeException("Failed to write report", e);
        }
    }

    // The actual public method is buried at the bottom
    public void generateReport(String rawData, String outputPath) {
        String clean = sanitizeInput(rawData);
        List<String> lines = splitIntoLines(clean);
        StringBuilder report = new StringBuilder();
        for (String line : lines) {
            report.append(formatLine(line, 80)).append("\n");
        }
        writeToFile(report.toString(), outputPath);
    }
}
```

**AFTER -- Newspaper order:**

```java
// Java -- GOOD: Public purpose at the top, details below
public class ReportGenerator {

    public void generateReport(String rawData, String outputPath) {
        String clean = sanitizeInput(rawData);
        List<String> lines = splitIntoLines(clean);
        StringBuilder report = new StringBuilder();
        for (String line : lines) {
            report.append(formatLine(line, 80)).append("\n");
        }
        writeToFile(report.toString(), outputPath);
    }

    private String sanitizeInput(String raw) {
        return raw.replaceAll("[^a-zA-Z0-9 ]", "").trim();
    }

    private List<String> splitIntoLines(String data) {
        return Arrays.asList(data.split("\n"));
    }

    private String formatLine(String line, int width) {
        return String.format("%-" + width + "s", line);
    }

    private void writeToFile(String content, String path) {
        try (FileWriter writer = new FileWriter(path)) {
            writer.write(content);
        } catch (IOException e) {
            throw new RuntimeException("Failed to write report", e);
        }
    }
}
```

The same principle applies in Python:

```python
# Python -- GOOD: Public methods first, helpers below
class ReportGenerator:

    def generate_report(self, raw_data: str, output_path: str) -> None:
        """Generate a formatted report from raw data."""
        clean = self._sanitize_input(raw_data)
        lines = self._split_into_lines(clean)
        formatted = [self._format_line(line, 80) for line in lines]
        self._write_to_file("\n".join(formatted), output_path)

    def _sanitize_input(self, raw: str) -> str:
        import re
        return re.sub(r"[^a-zA-Z0-9 ]", "", raw).strip()

    def _split_into_lines(self, data: str) -> list[str]:
        return data.split("\n")

    def _format_line(self, line: str, width: int) -> str:
        return line.ljust(width)

    def _write_to_file(self, content: str, path: str) -> None:
        with open(path, "w") as f:
            f.write(content)
```

Notice how in both languages, you can read just the first method and immediately understand what this class does. The details are there if you need them, but they do not get in the way.

---

## Vertical Formatting

Vertical formatting is about how you use vertical space -- blank lines, grouping, and ordering -- to communicate structure.

### Vertical Openness: Blank Lines Between Concepts

Blank lines are visual separators. They tell the reader: "This thought is done. A new thought begins." Without blank lines, code becomes a wall of text. With too many, it becomes scattered and hard to follow.

**BEFORE -- No vertical openness:**

```java
// Java -- BAD: Everything crammed together
public class UserService {
    private final UserRepository repository;
    private final EmailService emailService;
    private final Logger logger;
    public UserService(UserRepository repository, EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
        this.logger = LoggerFactory.getLogger(UserService.class);
    }
    public User createUser(String name, String email) {
        validateEmail(email);
        User user = new User(name, email);
        repository.save(user);
        emailService.sendWelcome(user);
        logger.info("Created user: {}", email);
        return user;
    }
    public void deleteUser(long id) {
        User user = repository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
        repository.delete(user);
        logger.info("Deleted user: {}", id);
    }
    private void validateEmail(String email) {
        if (email == null || !email.contains("@")) {
            throw new InvalidEmailException(email);
        }
    }
}
```

**AFTER -- Vertical openness between concepts:**

```java
// Java -- GOOD: Blank lines separate distinct concepts
public class UserService {

    private final UserRepository repository;
    private final EmailService emailService;
    private final Logger logger;

    public UserService(UserRepository repository, EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
        this.logger = LoggerFactory.getLogger(UserService.class);
    }

    public User createUser(String name, String email) {
        validateEmail(email);

        User user = new User(name, email);
        repository.save(user);

        emailService.sendWelcome(user);
        logger.info("Created user: {}", email);

        return user;
    }

    public void deleteUser(long id) {
        User user = repository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));

        repository.delete(user);
        logger.info("Deleted user: {}", id);
    }

    private void validateEmail(String email) {
        if (email == null || !email.contains("@")) {
            throw new InvalidEmailException(email);
        }
    }
}
```

The difference is dramatic. In the "after" version, your eyes can quickly scan and identify: fields, constructor, public methods, private methods. Each concept has breathing room.

### Vertical Density: Related Code Together

While blank lines separate unrelated concepts, you should keep related lines close together. Do not scatter things that belong together.

**BEFORE -- Related things separated:**

```python
# Python -- BAD: Related code scattered across the file

class OrderProcessor:

    def __init__(self):
        self.tax_rate = 0.08

    # ... 50 lines of other methods ...

    def calculate_subtotal(self, items: list[dict]) -> float:
        return sum(item["price"] * item["quantity"] for item in items)

    # ... 30 more lines of other methods ...

    def calculate_tax(self, subtotal: float) -> float:
        return subtotal * self.tax_rate

    # ... 20 more lines of other methods ...

    def calculate_total(self, items: list[dict]) -> float:
        subtotal = self.calculate_subtotal(items)
        tax = self.calculate_tax(subtotal)
        return subtotal + tax
```

**AFTER -- Related things together:**

```python
# Python -- GOOD: Calculation methods grouped together

class OrderProcessor:

    def __init__(self):
        self.tax_rate = 0.08

    def calculate_total(self, items: list[dict]) -> float:
        subtotal = self.calculate_subtotal(items)
        tax = self.calculate_tax(subtotal)
        return subtotal + tax

    def calculate_subtotal(self, items: list[dict]) -> float:
        return sum(item["price"] * item["quantity"] for item in items)

    def calculate_tax(self, subtotal: float) -> float:
        return subtotal * self.tax_rate
```

The caller (`calculate_total`) is near the methods it calls. A reader exploring the total calculation can see all three methods without scrolling.

### Vertical Distance: Declarations Close to Usage

Variables should be declared as close to their first use as possible. In Java, this means declaring variables right before the loop or block that uses them, not at the top of a long method.

```java
// Java -- BAD: Variable declared far from use
public void processOrders(List<Order> orders) {
    double totalRevenue = 0;       // Declared here...
    int failedCount = 0;           // ...but used 15 lines later
    Logger auditLogger = getAuditLogger();

    for (Order order : orders) {
        // ... 10 lines of validation ...
        totalRevenue += order.getAmount();  // First use, far from declaration
    }

    // failedCount used much later...
}

// Java -- GOOD: Variable declared close to use
public void processOrders(List<Order> orders) {
    Logger auditLogger = getAuditLogger();

    double totalRevenue = 0;
    for (Order order : orders) {
        // ... validation ...
        totalRevenue += order.getAmount();
    }

    int failedCount = countFailedOrders(orders);
    auditLogger.info("Failed: {}", failedCount);
}
```

---

## Horizontal Formatting

Horizontal formatting is about how you use horizontal space: line length, alignment, indentation, and whitespace within a line.

### Line Length: The 80-120 Character Rule

The ideal line length is a subject of passionate debate. Here is the practical answer: keep lines between 80 and 120 characters. Anything beyond 120 forces horizontal scrolling, makes side-by-side diffs painful, and breaks readability on smaller screens.

```
+------------------------------------------------------------+
|              LINE LENGTH GUIDE                              |
+------------------------------------------------------------+
|                                                             |
|  0          40          80         120         160          |
|  |----------|-----------|----------|-----------|           |
|  [    Sweet spot: 80-100 chars    ]                        |
|  [       Acceptable: up to 120    ........]                |
|  [       Avoid: beyond 120        ...................]     |
|                                                             |
|  Why?                                                       |
|  - Fits on most screens without scrolling                  |
|  - Works with side-by-side diff tools                      |
|  - Readable in code review interfaces                      |
|  - Allows split-screen editing                             |
|                                                             |
+------------------------------------------------------------+
```

**BEFORE -- Lines too long:**

```java
// Java -- BAD: Horizontal scrolling required
public List<CustomerOrderSummary> getActiveCustomerOrderSummariesByDateRangeAndStatus(LocalDate startDate, LocalDate endDate, OrderStatus status, boolean includeArchived) {
    return customerRepository.findAllByRegistrationDateBetweenAndStatusEquals(startDate, endDate, status).stream().filter(c -> includeArchived || !c.isArchived()).map(c -> new CustomerOrderSummary(c.getId(), c.getName(), c.getOrders().stream().filter(o -> o.getStatus() == status).count())).collect(Collectors.toList());
}
```

**AFTER -- Properly broken lines:**

```java
// Java -- GOOD: Each concept on its own line
public List<CustomerOrderSummary> getActiveCustomerOrderSummaries(
        LocalDate startDate,
        LocalDate endDate,
        OrderStatus status,
        boolean includeArchived) {

    return customerRepository
        .findByDateRangeAndStatus(startDate, endDate, status)
        .stream()
        .filter(customer -> includeArchived || !customer.isArchived())
        .map(customer -> buildSummary(customer, status))
        .collect(Collectors.toList());
}

private CustomerOrderSummary buildSummary(Customer customer, OrderStatus status) {
    long orderCount = customer.getOrders().stream()
        .filter(order -> order.getStatus() == status)
        .count();

    return new CustomerOrderSummary(
        customer.getId(),
        customer.getName(),
        orderCount
    );
}
```

The same principle in Python:

```python
# Python -- BAD: One massive line
def get_active_summaries(start, end, status, include_archived):
    return [{"id": c.id, "name": c.name, "count": len([o for o in c.orders if o.status == status])} for c in repo.find_by_date_range(start, end, status) if include_archived or not c.archived]

# Python -- GOOD: Broken into readable lines
def get_active_summaries(
    start: date,
    end: date,
    status: str,
    include_archived: bool = False,
) -> list[dict]:
    customers = repo.find_by_date_range(start, end, status)

    return [
        build_summary(customer, status)
        for customer in customers
        if include_archived or not customer.archived
    ]


def build_summary(customer: Customer, status: str) -> dict:
    matching_orders = [
        order for order in customer.orders
        if order.status == status
    ]

    return {
        "id": customer.id,
        "name": customer.name,
        "count": len(matching_orders),
    }
```

### Horizontal Whitespace: Use It to Show Association

Whitespace within a line communicates which things are related and which are separate.

```java
// Java -- Whitespace shows association
private void measureLine(String line) {
    lineCount++;                          // No space around ++ (tight binding)
    int lineSize = line.length();         // Space around = (assignment)
    totalChars += lineSize;               // Space around += (assignment)
    lineWidthHistogram.addLine(lineSize); // No space before ( (method call)
}

// Operators: space around low-precedence, no space around high-precedence
int result = a*b + c*d;    // Multiplication binds tighter than addition
double det = b*b - 4*a*c;  // Visual grouping matches mathematical grouping
```

```python
# Python -- Consistent whitespace
def calculate_score(hits: int, misses: int, bonus: float) -> float:
    base_score = hits*10 - misses*5   # Tight binding for arithmetic
    return base_score + bonus         # Space around + for clarity
```

### Indentation: The Structure Visualizer

Indentation reveals the hierarchical structure of your code. Without it, you cannot tell what is inside a loop, a conditional, a method, or a class.

**BEFORE -- Broken indentation:**

```python
# Python -- BAD: Inconsistent indentation
class DataProcessor:
  def process(self, data):
        for item in data:
            if item.is_valid():
              result = self.transform(item)
                  self.save(result)
          else:
            self.log_error(item)
```

**AFTER -- Consistent indentation:**

```python
# Python -- GOOD: Consistent 4-space indentation (PEP 8)
class DataProcessor:

    def process(self, data: list) -> None:
        for item in data:
            if item.is_valid():
                result = self.transform(item)
                self.save(result)
            else:
                self.log_error(item)
```

**The tabs vs. spaces debate:** Pick one. The industry has largely settled on spaces (4 spaces for Python per PEP 8, 4 spaces for Java by convention, 2 spaces for JavaScript by convention). What matters is that everyone on the team uses the same setting. Configure your editor and never think about it again.

---

## Team Rules Beat Personal Preferences

This is the most important formatting rule in this entire chapter:

**A team's formatting rules always override your personal preferences.**

It does not matter if you prefer tabs over spaces, or 2-space indentation over 4-space, or opening braces on the same line versus the next line. What matters is consistency across the codebase. A codebase where every file looks different is harder to read than one where every file follows a convention you do not personally love.

```
+-----------------------------------------------------------+
|           PERSONAL PREFERENCE vs TEAM STANDARD             |
+-----------------------------------------------------------+
|                                                            |
|  Developer A:  "I prefer tabs and 80-char lines."         |
|  Developer B:  "I prefer spaces and 120-char lines."      |
|  Developer C:  "I prefer K&R braces."                     |
|  Developer D:  "I prefer Allman braces."                  |
|                                                            |
|  Result if everyone follows their preference:              |
|  --> Every file looks different                            |
|  --> Git diffs are full of formatting noise                |
|  --> Code reviews waste time on style arguments            |
|                                                            |
|  Result if everyone follows team standard:                 |
|  --> Every file looks the same                             |
|  --> Git diffs show only real changes                      |
|  --> Code reviews focus on logic and design                |
|                                                            |
+-----------------------------------------------------------+
```

### How to Establish Team Rules

1. Pick a well-known style guide as your starting point (Google Java Style, PEP 8, Airbnb JavaScript)
2. Discuss and document any deviations the team agrees on
3. Configure an automated formatter to enforce the rules
4. Run the formatter as part of your CI/CD pipeline
5. Never argue about formatting in a code review again

---

## Linters and Formatters: Automate Your Style

The best formatting is formatting you never have to think about. Modern tools can enforce style rules automatically.

### The Tooling Landscape

```
+-------------------------------------------------------------+
|              FORMATTING TOOLS BY LANGUAGE                     |
+-------------------------------------------------------------+
|                                                              |
|  Language    | Formatter        | Linter                    |
|  ------------|------------------|---------------------------|
|  Python      | Black            | Pylint, Ruff, Flake8      |
|  Java        | google-java-fmt  | Checkstyle, PMD           |
|  JavaScript  | Prettier         | ESLint                    |
|  TypeScript  | Prettier         | ESLint, TSLint (legacy)   |
|  Go          | gofmt            | (built-in)                |
|  Rust        | rustfmt          | clippy                    |
|                                                              |
+-------------------------------------------------------------+
|                                                              |
|  Formatter = automatically rewrites code to match style      |
|  Linter    = reports violations (may or may not auto-fix)    |
|                                                              |
+-------------------------------------------------------------+
```

### Formatter vs. Linter: What Is the Difference?

A **formatter** automatically rewrites your code to conform to style rules. You run it, and your code is reformatted. No decisions, no arguments. Black for Python is famously "uncompromising" -- it gives you almost zero configuration options, and that is the point.

A **linter** analyzes your code for potential problems -- not just style issues but also bugs, complexity, and anti-patterns. Linters often report issues for you to fix manually, though many support auto-fix for simple problems.

### Python: Black in Action

```python
# Python -- BEFORE Black formats it
def calculate_price(base_price,discount_percentage,tax_rate,
    is_member):
    if is_member==True:
        discount=discount_percentage+5
    else:
        discount=discount_percentage
    subtotal=base_price*(1-discount/100)
    total=subtotal*(1+tax_rate/100)
    return   total
```

```python
# Python -- AFTER Black formats it
def calculate_price(
    base_price,
    discount_percentage,
    tax_rate,
    is_member,
):
    if is_member:
        discount = discount_percentage + 5
    else:
        discount = discount_percentage

    subtotal = base_price * (1 - discount / 100)
    total = subtotal * (1 + tax_rate / 100)
    return total
```

Black fixed: spacing around operators, trailing commas, parameter alignment, the `== True` anti-pattern is flagged by linters, and consistent blank lines.

### Java: Checkstyle Configuration

```xml
<!-- checkstyle.xml -- Example configuration -->
<module name="Checker">
    <module name="TreeWalker">
        <module name="Indentation">
            <property name="basicOffset" value="4"/>
        </module>
        <module name="LineLength">
            <property name="max" value="120"/>
        </module>
        <module name="NeedBraces"/>
        <module name="LeftCurly">
            <property name="option" value="eol"/>
        </module>
    </module>
</module>
```

### Setting Up Pre-Commit Hooks

The best way to enforce formatting is to make it impossible to commit unformatted code:

```bash
# .pre-commit-config.yaml (Python project using pre-commit framework)
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
```

```bash
# For Java (using Maven)
# pom.xml plugin that runs Checkstyle on every build
mvn checkstyle:check
```

---

## Complete Before/After: A Messy File Cleaned Up

Let us look at a complete transformation. This is a realistic example of code you might encounter in a real project.

### BEFORE: The Mess

```java
// Java -- BEFORE: Multiple formatting violations
public class    invoiceCalculator{
private static final double TAX=0.08;
private static final double MEMBER_DISCOUNT=0.05;
    public double calculateInvoiceTotal(List<LineItem> items,boolean isMember,String couponCode){
double subtotal=0;
for(LineItem item:items){if(item.getQuantity()>0){
subtotal+=item.getPrice()*item.getQuantity();}else{System.out.println("invalid quantity for item: "+item.getName());}}
double discount=0;
if(isMember){discount=MEMBER_DISCOUNT;}
if(couponCode!=null&&!couponCode.isEmpty()){if(couponCode.equals("SAVE10")){discount+=0.10;}else if(couponCode.equals("SAVE20")){discount+=0.20;}else{System.out.println("invalid coupon");}}
double afterDiscount=subtotal*(1-discount);
        double tax=afterDiscount*TAX;
return afterDiscount+tax;
}
public void printInvoice(List<LineItem> items,boolean isMember,String coupon){
double total=calculateInvoiceTotal(items,isMember,coupon);
System.out.println("=== INVOICE ===");
for(LineItem item:items){System.out.println(item.getName()+": $"+item.getPrice()+" x "+item.getQuantity());}
System.out.println("Total: $"+String.format("%.2f",total));
System.out.println("===============");
}
}
```

### AFTER: Clean and Readable

```java
// Java -- AFTER: Properly formatted
public class InvoiceCalculator {

    private static final double TAX_RATE = 0.08;
    private static final double MEMBER_DISCOUNT = 0.05;

    private static final Map<String, Double> COUPON_DISCOUNTS = Map.of(
        "SAVE10", 0.10,
        "SAVE20", 0.20
    );

    public double calculateInvoiceTotal(
            List<LineItem> items,
            boolean isMember,
            String couponCode) {

        double subtotal = calculateSubtotal(items);
        double discount = calculateDiscount(isMember, couponCode);
        double afterDiscount = subtotal * (1 - discount);
        double tax = afterDiscount * TAX_RATE;

        return afterDiscount + tax;
    }

    public void printInvoice(
            List<LineItem> items,
            boolean isMember,
            String couponCode) {

        double total = calculateInvoiceTotal(items, isMember, couponCode);

        System.out.println("=== INVOICE ===");
        for (LineItem item : items) {
            System.out.printf(
                "%s: $%.2f x %d%n",
                item.getName(),
                item.getPrice(),
                item.getQuantity()
            );
        }
        System.out.printf("Total: $%.2f%n", total);
        System.out.println("===============");
    }

    private double calculateSubtotal(List<LineItem> items) {
        double subtotal = 0;

        for (LineItem item : items) {
            if (item.getQuantity() <= 0) {
                throw new IllegalArgumentException(
                    "Invalid quantity for item: " + item.getName()
                );
            }
            subtotal += item.getPrice() * item.getQuantity();
        }

        return subtotal;
    }

    private double calculateDiscount(boolean isMember, String couponCode) {
        double discount = 0;

        if (isMember) {
            discount = MEMBER_DISCOUNT;
        }

        if (couponCode != null && !couponCode.isEmpty()) {
            Double couponDiscount = COUPON_DISCOUNTS.get(couponCode);
            if (couponDiscount == null) {
                throw new IllegalArgumentException(
                    "Invalid coupon code: " + couponCode
                );
            }
            discount += couponDiscount;
        }

        return discount;
    }
}
```

The same transformation in Python:

### BEFORE: Python Mess

```python
# Python -- BEFORE: Formatting chaos
class   invoiceCalculator:
    TAX=0.08
    MEMBER_DISCOUNT=0.05
    def calculateTotal(self,items,is_member,coupon_code):
        subtotal=0
        for item in items:
            if item['qty']>0:
                    subtotal+=item['price']*item['qty']
            else:
                print("bad qty")
        discount=0
        if is_member==True:discount=self.MEMBER_DISCOUNT
        if coupon_code!=None:
          if coupon_code=="SAVE10":discount+=0.10
          elif coupon_code=="SAVE20":discount+=0.20
          else:print("bad coupon")
        return (subtotal*(1-discount))*(1+self.TAX)
```

### AFTER: Python Clean

```python
# Python -- AFTER: PEP 8 compliant, Black-formatted
class InvoiceCalculator:

    TAX_RATE = 0.08
    MEMBER_DISCOUNT = 0.05

    COUPON_DISCOUNTS = {
        "SAVE10": 0.10,
        "SAVE20": 0.20,
    }

    def calculate_total(
        self,
        items: list[dict],
        is_member: bool,
        coupon_code: str | None = None,
    ) -> float:
        subtotal = self._calculate_subtotal(items)
        discount = self._calculate_discount(is_member, coupon_code)
        after_discount = subtotal * (1 - discount)
        tax = after_discount * self.TAX_RATE

        return after_discount + tax

    def _calculate_subtotal(self, items: list[dict]) -> float:
        subtotal = 0.0

        for item in items:
            if item["qty"] <= 0:
                raise ValueError(
                    f"Invalid quantity for item: {item['name']}"
                )
            subtotal += item["price"] * item["qty"]

        return subtotal

    def _calculate_discount(
        self,
        is_member: bool,
        coupon_code: str | None,
    ) -> float:
        discount = 0.0

        if is_member:
            discount = self.MEMBER_DISCOUNT

        if coupon_code:
            coupon_discount = self.COUPON_DISCOUNTS.get(coupon_code)
            if coupon_discount is None:
                raise ValueError(f"Invalid coupon code: {coupon_code}")
            discount += coupon_discount

        return discount
```

---

## Common Mistakes

1. **No formatter configured.** Teams that rely on "everyone will follow the style guide" always end up with inconsistent code. Automate it.

2. **Arguing about formatting in code reviews.** If your team is spending review time on formatting, you have not set up your tooling correctly. Let the formatter handle it.

3. **Giant commits that mix formatting and logic changes.** If you need to reformat a file, do it in a separate commit with the message "Apply formatter" so that logic changes are easy to review in isolation.

4. **Ignoring vertical formatting.** Many developers get horizontal formatting right (indentation, line length) but neglect vertical formatting (blank lines, ordering, grouping). Both matter.

5. **Over-formatting.** Do not add blank lines between every single line of code. Blank lines should separate concepts, not every statement. Three related assignments can stay together.

6. **Using different formatters in the same project.** If half the team uses Prettier with one config and the other half uses a different config, you get endless formatting battles in version control.

---

## Best Practices

1. **Configure a formatter on day one of every project.** Do not wait until the codebase is large.

2. **Use pre-commit hooks to enforce formatting.** Make it impossible to commit unformatted code.

3. **Follow the newspaper metaphor.** Public interface at the top, implementation details below.

4. **Use blank lines to separate concepts, not individual lines.** Group related code together.

5. **Keep lines under 120 characters.** Aim for 80-100 as the sweet spot.

6. **Declare variables close to their first use.** Do not declare everything at the top of a method.

7. **Adopt a well-known style guide.** PEP 8 for Python, Google Java Style for Java. Do not invent your own.

8. **Make formatting changes in separate commits.** Never mix formatting and logic in the same commit.

---

## Quick Summary

```
+-----------------------------------------------------------+
|              FORMATTING CHEAT SHEET                        |
+-----------------------------------------------------------+
|                                                            |
|  VERTICAL:                                                 |
|    - Newspaper metaphor (headline -> details)              |
|    - Blank lines between concepts (openness)               |
|    - Related code together (density)                       |
|    - Variables declared near first use                     |
|                                                            |
|  HORIZONTAL:                                               |
|    - Line length: 80-120 characters                        |
|    - Consistent indentation (spaces, not tabs)             |
|    - Whitespace shows association                          |
|    - Break long lines at logical points                    |
|                                                            |
|  TEAM:                                                     |
|    - Team rules > personal preference                      |
|    - Adopt a standard style guide                          |
|    - Automate with formatters (Black, Prettier)            |
|    - Enforce with pre-commit hooks and CI                  |
|                                                            |
+-----------------------------------------------------------+
```

---

## Key Points

- Formatting is a communication tool that makes code scannable and understandable before you read a single keyword
- The newspaper metaphor means putting high-level public methods first and implementation details below
- Vertical openness (blank lines between concepts) and vertical density (related code together) work together to create readable structure
- Horizontal formatting should keep lines under 120 characters with consistent indentation
- Team formatting rules always override personal preferences because consistency across a codebase is more valuable than any individual style choice
- Formatters like Black and Prettier automate style enforcement so developers never need to argue about formatting
- Formatting changes should always be in separate commits from logic changes

---

## Practice Questions

1. Explain the newspaper metaphor for code formatting. How does it guide the ordering of methods within a class?

2. What is the difference between vertical openness and vertical density? Give an example of when you would use each.

3. Why should team formatting rules take priority over personal preferences? What problems arise when every developer follows their own style?

4. What is the difference between a formatter and a linter? Name one of each for Python and one of each for Java.

5. You are reviewing a pull request that contains both a new feature and a codebase-wide reformatting. What would you tell the author?

---

## Exercises

### Exercise 1: Reformat a Messy File

Take the following code and apply proper formatting rules. Fix vertical openness, vertical density, horizontal line length, indentation, and method ordering.

```python
class  reportBuilder:
  def _header(self):return "=== REPORT ==="
  def generate(self,data,format_type):
        result=self._header()+"\n"
        for item in data:
            if format_type=="csv":result+=",".join(str(v) for v in item.values())+"\n"
            elif format_type=="table":
                    result+="|".join(f"{str(v):>15}" for v in item.values())+"\n"
            else:result+= str(item)+"\n"
        result+=self._footer()
        return result
  def _footer(self):return "=== END ==="
```

### Exercise 2: Configure a Formatter

Set up Black for a Python project with a `pyproject.toml` configuration. Include settings for line length of 100 characters and target Python 3.11. Then set up a pre-commit hook that runs Black automatically before every commit.

### Exercise 3: Evaluate Formatting Choices

Look at an open-source project on GitHub in a language you use regularly. Examine three different files and answer: Does the project follow consistent formatting? What style guide does it appear to follow? Is there a formatter configured? Check for `.prettierrc`, `pyproject.toml`, `checkstyle.xml`, or similar configuration files.

---

## What Is Next?

Now that you know how to make code visually consistent and scannable, the next chapter tackles a topic that can make or break your application's reliability: error handling. You will learn why exceptions beat error codes, how to build a clean exception hierarchy, and how to separate error handling from business logic so that neither clutters the other.
