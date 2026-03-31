# Chapter 3: Functions -- The Building Blocks of Clean Code

---

## What You Will Learn

- Why functions should be small -- ideally 5 to 15 lines -- and how this makes code dramatically easier to read
- The "do one thing" principle and how to tell when a function is doing too much
- How to keep functions at a single level of abstraction
- Why descriptive function names are worth every character
- The ideal number of function arguments (spoiler: fewer is better)
- Why flag arguments are a code smell and what to use instead
- How to eliminate hidden side effects that create bugs
- A complete before/after transformation of a 100-line monster function

---

## Why This Chapter Matters

Functions are the first line of organization in any program. They are the verbs of your codebase -- the actions your software performs. Every single thing your application does happens inside a function. If your functions are bloated, confusing, and tangled, your entire codebase inherits that chaos.

Consider this: the average developer reads 10 to 20 functions for every one they write. When each function is a 100-line maze with six parameters and three hidden side effects, reading becomes an exhausting puzzle. But when each function is short, well-named, and does exactly one thing, reading code feels like reading a well-organized recipe.

This chapter teaches you how to write functions that other developers will thank you for.

---

## Small Functions

The first rule of functions is that they should be small. The second rule is that they should be smaller than that.

How small? In most cases, a function should be between 5 and 15 lines of code. If it grows beyond 20 lines, it is almost certainly doing too much and should be broken apart.

This might sound extreme if you are used to writing functions that span 50, 100, or even 200 lines. But think about it from the reader's perspective. A 10-line function can be understood in a single glance. A 100-line function requires scrolling, mental bookmarking, and deep concentration.

```
+-----------------------------------------------------------+
|              Function Size and Readability                |
+-----------------------------------------------------------+
|                                                           |
|   5 lines   -->  Understood in seconds                    |
|  10 lines   -->  Understood in a glance                   |
|  20 lines   -->  Understood in a minute                   |
|  50 lines   -->  Requires careful reading                 |
| 100 lines   -->  Requires scrolling and mental tracking   |
| 200+ lines  -->  Requires a map and a prayer              |
|                                                           |
+-----------------------------------------------------------+
```

### BEFORE: A Long Function

Java:
```java
public void processOrder(Order order) {
    // Validate order
    if (order == null) {
        throw new IllegalArgumentException("Order cannot be null");
    }
    if (order.getItems() == null || order.getItems().isEmpty()) {
        throw new IllegalArgumentException("Order must have items");
    }
    if (order.getCustomer() == null) {
        throw new IllegalArgumentException("Order must have a customer");
    }

    // Calculate totals
    double subtotal = 0;
    for (OrderItem item : order.getItems()) {
        subtotal += item.getPrice() * item.getQuantity();
    }
    double tax = subtotal * 0.08;
    double total = subtotal + tax;
    order.setSubtotal(subtotal);
    order.setTax(tax);
    order.setTotal(total);

    // Apply discount
    if (order.getCustomer().isPreferred()) {
        order.setTotal(order.getTotal() * 0.9);
    }

    // Save to database
    Connection conn = DriverManager.getConnection(DB_URL);
    PreparedStatement stmt = conn.prepareStatement(
        "INSERT INTO orders (customer_id, total) VALUES (?, ?)"
    );
    stmt.setLong(1, order.getCustomer().getId());
    stmt.setDouble(2, order.getTotal());
    stmt.executeUpdate();
    conn.close();

    // Send confirmation email
    String subject = "Order Confirmation #" + order.getId();
    String body = "Thank you for your order. Total: $" + order.getTotal();
    EmailService.send(order.getCustomer().getEmail(), subject, body);
}
```

This function is about 35 lines, and it does at least five different things: validation, calculation, discount logic, database persistence, and email notification. Imagine what happens when this grows to 100+ lines with more business rules.

### AFTER: Small Functions That Do One Thing

Java:
```java
public void processOrder(Order order) {
    validateOrder(order);
    calculateTotals(order);
    applyDiscounts(order);
    saveOrder(order);
    sendConfirmation(order);
}

private void validateOrder(Order order) {
    Objects.requireNonNull(order, "Order cannot be null");
    requireNonEmpty(order.getItems(), "Order must have items");
    Objects.requireNonNull(order.getCustomer(), "Order must have a customer");
}

private void calculateTotals(Order order) {
    double subtotal = order.getItems().stream()
        .mapToDouble(item -> item.getPrice() * item.getQuantity())
        .sum();
    order.setSubtotal(subtotal);
    order.setTax(subtotal * TAX_RATE);
    order.setTotal(subtotal + order.getTax());
}

private void applyDiscounts(Order order) {
    if (order.getCustomer().isPreferred()) {
        order.setTotal(order.getTotal() * PREFERRED_DISCOUNT);
    }
}

private void saveOrder(Order order) {
    orderRepository.save(order);
}

private void sendConfirmation(Order order) {
    emailService.sendOrderConfirmation(order);
}
```

Now `processOrder` reads like a table of contents. Each helper function is small, focused, and independently testable.

Python equivalent:
```python
def process_order(order):
    validate_order(order)
    calculate_totals(order)
    apply_discounts(order)
    save_order(order)
    send_confirmation(order)


def validate_order(order):
    if order is None:
        raise ValueError("Order cannot be None")
    if not order.items:
        raise ValueError("Order must have items")
    if order.customer is None:
        raise ValueError("Order must have a customer")


def calculate_totals(order):
    order.subtotal = sum(
        item.price * item.quantity for item in order.items
    )
    order.tax = order.subtotal * TAX_RATE
    order.total = order.subtotal + order.tax


def apply_discounts(order):
    if order.customer.is_preferred:
        order.total *= PREFERRED_DISCOUNT


def save_order(order):
    order_repository.save(order)


def send_confirmation(order):
    email_service.send_order_confirmation(order)
```

---

## Do One Thing

A function should do one thing. It should do it well. It should do it only.

But how do you define "one thing"? Here is a practical test:

**The "AND" Test**: Describe what the function does. If your description includes the word "and" or "or," the function is doing more than one thing.

- "This function validates the order AND calculates the total AND saves it to the database." -- Three things. Break it apart.
- "This function calculates the order total." -- One thing. Keep it.

**The Extraction Test**: Try to extract another function from it with a name that is not merely a restatement of the original. If you can, the original function is doing more than one thing.

```
+-----------------------------------------------------------+
|                  The "One Thing" Test                      |
+-----------------------------------------------------------+
|                                                           |
|   Can you describe the function without using "AND"?      |
|                                                           |
|   YES --> The function probably does one thing     [OK]   |
|   NO  --> The function does too much            [SPLIT]   |
|                                                           |
|   Can you extract a meaningful sub-function?              |
|                                                           |
|   YES --> The original does more than one thing  [SPLIT]  |
|   NO  --> The function is properly focused          [OK]  |
|                                                           |
+-----------------------------------------------------------+
```

### Sections Within Functions Are a Warning Sign

If you find yourself putting blank lines or comments inside a function to separate "sections," that function is doing multiple things. Each section should be its own function.

**BEFORE: A function with internal sections**

Python:
```python
def generate_report(employees):
    # Filter active employees
    active = [e for e in employees if e.is_active]

    # Sort by department
    active.sort(key=lambda e: e.department)

    # Build report lines
    lines = []
    current_dept = None
    for emp in active:
        if emp.department != current_dept:
            current_dept = emp.department
            lines.append(f"\n=== {current_dept} ===")
        lines.append(f"  {emp.name}: {emp.role}")

    # Write to file
    with open("report.txt", "w") as f:
        f.write("\n".join(lines))
```

**AFTER: Each section becomes a function**

Python:
```python
def generate_report(employees):
    active_employees = filter_active(employees)
    sorted_employees = sort_by_department(active_employees)
    report_content = build_report(sorted_employees)
    write_report(report_content)


def filter_active(employees):
    return [e for e in employees if e.is_active]


def sort_by_department(employees):
    return sorted(employees, key=lambda e: e.department)


def build_report(employees):
    lines = []
    current_dept = None
    for emp in employees:
        if emp.department != current_dept:
            current_dept = emp.department
            lines.append(f"\n=== {current_dept} ===")
        lines.append(f"  {emp.name}: {emp.role}")
    return "\n".join(lines)


def write_report(content, filename="report.txt"):
    with open(filename, "w") as f:
        f.write(content)
```

---

## One Level of Abstraction per Function

Each function should operate at a single level of abstraction. Mixing high-level business logic with low-level implementation details makes code jarring to read.

Think of it like giving driving directions. You would not say: "Drive to the grocery store, engage the clutch pedal with your left foot while simultaneously rotating the ignition key clockwise, and pick up some milk." The directions mix high-level intent (drive to the store, buy milk) with low-level mechanics (clutch and ignition).

```
+-----------------------------------------------------------+
|             Abstraction Level Hierarchy                    |
+-----------------------------------------------------------+
|                                                           |
|  HIGH       processOrder()                                |
|              |                                            |
|  MEDIUM      +-- validateOrder()                          |
|              +-- calculateTotals()                        |
|              +-- saveOrder()                              |
|              |    |                                       |
|  LOW         |    +-- prepareStatement()                  |
|              |    +-- executeUpdate()                     |
|              +-- sendConfirmation()                       |
|                   |                                       |
|  LOW              +-- formatEmailBody()                   |
|                   +-- connectToSmtpServer()               |
|                                                           |
+-----------------------------------------------------------+
```

### The Stepdown Rule

Code should read like a top-down narrative. Every function should be followed by those at the next level of abstraction. This is called the Stepdown Rule -- you read the program by descending one level of abstraction at a time.

**BEFORE: Mixed abstraction levels**

Java:
```java
public void registerUser(String name, String email, String password) {
    // High level: validate
    if (name == null || name.trim().isEmpty()) {
        throw new IllegalArgumentException("Name required");
    }
    // Low level: regex check
    if (!email.matches("^[A-Za-z0-9+_.-]+@(.+)$")) {
        throw new IllegalArgumentException("Invalid email");
    }
    // Low level: hashing
    byte[] salt = new byte[16];
    new SecureRandom().nextBytes(salt);
    String hashedPassword = Base64.getEncoder().encodeToString(
        MessageDigest.getInstance("SHA-256")
            .digest((password + Base64.getEncoder().encodeToString(salt))
            .getBytes())
    );
    // High level: save
    User user = new User(name, email, hashedPassword);
    userRepository.save(user);
}
```

**AFTER: Consistent abstraction level**

Java:
```java
public void registerUser(String name, String email, String password) {
    validateRegistration(name, email, password);
    String hashedPassword = hashPassword(password);
    User user = new User(name, email, hashedPassword);
    userRepository.save(user);
}

private void validateRegistration(String name, String email, String password) {
    requireNonBlank(name, "Name");
    requireValidEmail(email);
    requireStrongPassword(password);
}

private String hashPassword(String password) {
    byte[] salt = generateSalt();
    return passwordHasher.hash(password, salt);
}
```

---

## Use Descriptive Names

A long descriptive name is better than a short enigmatic name. A long descriptive name is better than a long descriptive comment.

Do not be afraid of long function names. Your IDE will autocomplete them. What matters is that a reader understands what the function does without reading its body.

```
+-----------------------------------------------------------+
|                Naming Comparison Table                     |
+-----------------------------------------------------------+
|                                                           |
|  BAD                     |  GOOD                          |
|  ------------------------|--------------------------------|
|  calc()                  |  calculateMonthlyPayment()     |
|  process()               |  processRefundRequest()        |
|  handle()                |  handleExpiredSubscription()    |
|  doIt()                  |  sendWelcomeEmail()            |
|  run()                   |  runDailyInventoryCheck()      |
|  check()                 |  checkPasswordStrength()       |
|  update()                |  updateShippingAddress()       |
|  get()                   |  getActiveSubscribers()        |
|                                                           |
+-----------------------------------------------------------+
```

### Naming Conventions for Functions

**Java**: Use camelCase verbs. Start with a verb that describes the action: `calculateTax()`, `isValid()`, `hasPermission()`, `sendEmail()`.

**Python**: Use snake_case verbs. Same verb-first principle: `calculate_tax()`, `is_valid()`, `has_permission()`, `send_email()`.

The verb tells you what the function does. The noun tells you what it operates on. Together they form a clear action: `validateEmail()`, `parseJsonResponse()`, `formatCurrency()`.

### Be Consistent

If you call one function `fetchCustomer()`, do not call the equivalent function for orders `retrieveOrder()` or `getProduct()`. Pick one convention -- `fetch`, `get`, or `retrieve` -- and stick with it throughout the codebase.

---

## Function Arguments

The ideal number of arguments for a function is zero. Next comes one. Then two. Three arguments should be avoided. More than three requires very special justification -- and then should not be used anyway.

Why? Each argument increases the cognitive load on the reader. Each argument is one more thing to understand, remember, and get right when calling the function.

```
+-----------------------------------------------------------+
|              Argument Count Guidelines                    |
+-----------------------------------------------------------+
|                                                           |
|  0 args  (niladic)   -->  Ideal                           |
|  1 arg   (monadic)   -->  Good, very common               |
|  2 args  (dyadic)    -->  Acceptable, use carefully        |
|  3 args  (triadic)   -->  Avoid if possible                |
|  4+ args (polyadic)  -->  Almost always wrong              |
|                                                           |
+-----------------------------------------------------------+
```

### Common Monadic Forms

There are three common reasons to pass a single argument:

1. **Asking a question**: `boolean fileExists("MyFile")` -- You pass something and get a boolean answer.
2. **Transforming it**: `InputStream fileOpen("MyFile")` -- You pass something and get a transformed version back.
3. **Processing an event**: `passwordAttemptFailed(attemptCount)` -- You pass something to signal an event.

### Dyadic Functions

Two arguments are fine when they have a natural ordering or relationship:

```java
// Natural pair -- coordinates
Point p = new Point(0, 0);

// Natural pair -- expected vs actual
assertEquals(expected, actual);

// Problematic -- which is which?
writeField(outputStream, name);  // Better: outputStream.writeField(name)
```

### Reduce Arguments with Objects

When a function needs many arguments, it is often a sign that some of those arguments should be grouped into an object.

**BEFORE: Too many arguments**

Java:
```java
Circle makeCircle(double x, double y, double radius) {
    // ...
}
```

**AFTER: Arguments grouped into an object**

Java:
```java
Circle makeCircle(Point center, double radius) {
    // ...
}
```

Python:
```python
# BEFORE
def create_user(first_name, last_name, email, phone, street,
                city, state, zip_code):
    pass

# AFTER
def create_user(name: PersonName, contact: ContactInfo,
                address: Address):
    pass
```

---

## No Flag Arguments

Flag arguments -- boolean parameters that change a function's behavior -- are ugly. They loudly proclaim that the function does more than one thing. It does one thing if the flag is true and another thing if the flag is false.

**BEFORE: Flag argument**

Java:
```java
public void render(boolean isSuite) {
    if (isSuite) {
        // ... render suite header ...
    } else {
        // ... render single test header ...
    }
    // ... common rendering ...
    if (isSuite) {
        // ... render suite footer ...
    } else {
        // ... render single test footer ...
    }
}
```

**AFTER: Two separate functions**

Java:
```java
public void renderSuite() {
    renderSuiteHeader();
    renderBody();
    renderSuiteFooter();
}

public void renderSingleTest() {
    renderSingleTestHeader();
    renderBody();
    renderSingleTestFooter();
}
```

Python:
```python
# BEFORE
def create_report(data, include_charts=False):
    # Does two different things based on flag
    pass

# AFTER
def create_text_report(data):
    pass

def create_visual_report(data):
    report = create_text_report(data)
    add_charts(report, data)
    return report
```

When you see `render(true)` in calling code, you have to look up the function to understand what `true` means. But `renderSuite()` is immediately clear.

---

## No Side Effects

A side effect is when a function promises to do one thing but quietly does something else too. Side effects are lies. Your function promises to do one thing, but it also does other hidden things.

**BEFORE: A function with a hidden side effect**

Java:
```java
public boolean checkPassword(String userName, String password) {
    User user = userRepository.findByName(userName);
    if (user != null) {
        String encodedPhrase = cryptographer.encrypt(password, user.getSalt());
        if (encodedPhrase.equals(user.getEncryptedPassword())) {
            Session.initialize();  // <-- SIDE EFFECT!
            return true;
        }
    }
    return false;
}
```

The function is called `checkPassword`. It says it checks a password and returns true or false. But it also initializes the session. A developer calling `checkPassword` during a routine validation might accidentally erase session data.

**AFTER: Side effect removed**

Java:
```java
public boolean checkPassword(String userName, String password) {
    User user = userRepository.findByName(userName);
    if (user == null) {
        return false;
    }
    String encodedPhrase = cryptographer.encrypt(password, user.getSalt());
    return encodedPhrase.equals(user.getEncryptedPassword());
}

// Session initialization happens explicitly in the login flow
public void login(String userName, String password) {
    if (checkPassword(userName, password)) {
        session.initialize();
    }
}
```

Python:
```python
# BEFORE: Hidden side effect
def check_password(username, password):
    user = user_repository.find_by_name(username)
    if user and hasher.verify(password, user.hashed_password):
        session.initialize()  # Hidden side effect!
        return True
    return False


# AFTER: No side effects
def check_password(username, password):
    user = user_repository.find_by_name(username)
    if user is None:
        return False
    return hasher.verify(password, user.hashed_password)


def login(username, password):
    if check_password(username, password):
        session.initialize()
```

### Output Arguments

Arguments should be inputs to a function, not outputs. Avoid using arguments to return results.

**BEFORE: Output argument**

Java:
```java
// What does this do? Does it append 's' to the footer?
// Or does it append the footer to 's'?
appendFooter(s);
```

**AFTER: Method on the object**

Java:
```java
// Clear and obvious
report.appendFooter();
```

---

## Command-Query Separation

Functions should either do something (a command) or answer something (a query), but not both.

**BEFORE: Mixed command and query**

Java:
```java
// Returns true if the attribute existed and was set successfully
public boolean set(String attribute, String value) {
    // ...
}

// Confusing in calling code:
if (set("username", "bob")) {
    // Was it already set? Did the set succeed? Unclear.
}
```

**AFTER: Separated command and query**

Java:
```java
if (attributeExists("username")) {
    setAttribute("username", "bob");
}
```

Python:
```python
# BEFORE: Mixed command and query
def set_value(key, value):
    """Sets value and returns True if key existed."""
    pass

# AFTER: Separated
def has_key(key):
    return key in _store

def set_value(key, value):
    _store[key] = value
```

---

## Prefer Exceptions to Returning Error Codes

When you return error codes from a function, you create a problem: the caller must deal with the error immediately, leading to deeply nested structures.

**BEFORE: Error codes lead to deep nesting**

Java:
```java
if (deletePage(page) == E_OK) {
    if (registry.deleteReference(page.name) == E_OK) {
        if (configKeys.deleteKey(page.name.makeKey()) == E_OK) {
            logger.log("page deleted");
        } else {
            logger.log("configKey not deleted");
        }
    } else {
        logger.log("deleteReference failed");
    }
} else {
    logger.log("delete failed");
    return E_ERROR;
}
```

**AFTER: Exceptions simplify the flow**

Java:
```java
try {
    deletePage(page);
    registry.deleteReference(page.name);
    configKeys.deleteKey(page.name.makeKey());
} catch (Exception e) {
    logger.log(e.getMessage());
}
```

### Extract Try/Catch Blocks

`try/catch` blocks are ugly. They mix error processing with normal processing. Extract the bodies into their own functions.

Java:
```java
public void delete(Page page) {
    try {
        deletePageAndReferences(page);
    } catch (Exception e) {
        logError(e);
    }
}

private void deletePageAndReferences(Page page) throws Exception {
    deletePage(page);
    registry.deleteReference(page.name);
    configKeys.deleteKey(page.name.makeKey());
}
```

---

## The Complete Monster Refactoring

Here is a real-world-style 100-line monster function, followed by its clean refactoring.

### BEFORE: The 100-Line Monster

Java:
```java
public String generateInvoice(int customerId, List<Integer> productIds,
        String discountCode, boolean sendEmail, String format) {
    // Look up customer
    Connection conn = null;
    String invoice = "";
    try {
        conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
        PreparedStatement ps = conn.prepareStatement(
            "SELECT * FROM customers WHERE id = ?");
        ps.setInt(1, customerId);
        ResultSet rs = ps.executeQuery();
        if (!rs.next()) {
            return "ERROR: Customer not found";
        }
        String custName = rs.getString("name");
        String custEmail = rs.getString("email");
        String custAddress = rs.getString("address");

        // Look up products and calculate total
        double subtotal = 0;
        List<String> lines = new ArrayList<>();
        for (int pid : productIds) {
            PreparedStatement ps2 = conn.prepareStatement(
                "SELECT * FROM products WHERE id = ?");
            ps2.setInt(1, pid);
            ResultSet rs2 = ps2.executeQuery();
            if (rs2.next()) {
                String pName = rs2.getString("name");
                double pPrice = rs2.getDouble("price");
                int stock = rs2.getInt("stock");
                if (stock <= 0) {
                    lines.add(pName + " - OUT OF STOCK");
                } else {
                    lines.add(pName + " - $" + pPrice);
                    subtotal += pPrice;
                    // Update stock
                    PreparedStatement ps3 = conn.prepareStatement(
                        "UPDATE products SET stock = stock - 1 WHERE id = ?");
                    ps3.setInt(1, pid);
                    ps3.executeUpdate();
                }
            }
        }

        // Apply discount
        double discount = 0;
        if (discountCode != null && !discountCode.isEmpty()) {
            PreparedStatement ps4 = conn.prepareStatement(
                "SELECT percentage FROM discounts WHERE code = ? AND active = 1");
            ps4.setString(1, discountCode);
            ResultSet rs4 = ps4.executeQuery();
            if (rs4.next()) {
                discount = rs4.getDouble("percentage");
            }
        }
        double discountAmount = subtotal * (discount / 100.0);
        double tax = (subtotal - discountAmount) * 0.08;
        double total = subtotal - discountAmount + tax;

        // Format invoice
        if (format.equals("HTML")) {
            invoice = "<html><body><h1>Invoice</h1>";
            invoice += "<p>Customer: " + custName + "</p>";
            invoice += "<p>Address: " + custAddress + "</p>";
            for (String line : lines) {
                invoice += "<p>" + line + "</p>";
            }
            invoice += "<p>Subtotal: $" + subtotal + "</p>";
            if (discount > 0) {
                invoice += "<p>Discount: -$" + discountAmount + "</p>";
            }
            invoice += "<p>Tax: $" + tax + "</p>";
            invoice += "<p><strong>Total: $" + total + "</strong></p>";
            invoice += "</body></html>";
        } else {
            invoice = "INVOICE\n";
            invoice += "Customer: " + custName + "\n";
            invoice += "Address: " + custAddress + "\n";
            invoice += "---\n";
            for (String line : lines) {
                invoice += line + "\n";
            }
            invoice += "---\n";
            invoice += "Subtotal: $" + subtotal + "\n";
            if (discount > 0) {
                invoice += "Discount: -$" + discountAmount + "\n";
            }
            invoice += "Tax: $" + tax + "\n";
            invoice += "Total: $" + total + "\n";
        }

        // Send email
        if (sendEmail) {
            Properties props = new Properties();
            props.put("mail.smtp.host", "smtp.company.com");
            Session session = Session.getInstance(props);
            MimeMessage msg = new MimeMessage(session);
            msg.setFrom(new InternetAddress("billing@company.com"));
            msg.setRecipient(Message.RecipientType.TO,
                new InternetAddress(custEmail));
            msg.setSubject("Your Invoice");
            msg.setContent(invoice, format.equals("HTML")
                ? "text/html" : "text/plain");
            Transport.send(msg);
        }

        // Save invoice
        PreparedStatement ps5 = conn.prepareStatement(
            "INSERT INTO invoices (customer_id, total, content) VALUES (?, ?, ?)");
        ps5.setInt(1, customerId);
        ps5.setDouble(2, total);
        ps5.setString(3, invoice);
        ps5.executeUpdate();

    } catch (Exception e) {
        return "ERROR: " + e.getMessage();
    } finally {
        if (conn != null) try { conn.close(); } catch (Exception e) {}
    }
    return invoice;
}
```

This function has every problem we have discussed: it is enormous, it does at least seven different things, it mixes abstraction levels, it has five arguments including a flag, it has side effects (updating stock, sending email, saving to the database), and it returns error codes as strings.

### AFTER: Refactored Into Clean Functions

Java:
```java
public class InvoiceService {

    private final CustomerRepository customerRepository;
    private final ProductRepository productRepository;
    private final DiscountRepository discountRepository;
    private final InvoiceRepository invoiceRepository;
    private final EmailService emailService;
    private final TaxCalculator taxCalculator;

    public Invoice generateInvoice(InvoiceRequest request) {
        Customer customer = findCustomer(request.getCustomerId());
        List<InvoiceLine> lines = buildInvoiceLines(request.getProductIds());
        PriceSummary pricing = calculatePricing(lines, request.getDiscountCode());
        Invoice invoice = createInvoice(customer, lines, pricing);
        invoiceRepository.save(invoice);
        return invoice;
    }

    private Customer findCustomer(int customerId) {
        return customerRepository.findById(customerId)
            .orElseThrow(() -> new CustomerNotFoundException(customerId));
    }

    private List<InvoiceLine> buildInvoiceLines(List<Integer> productIds) {
        return productIds.stream()
            .map(this::createInvoiceLine)
            .collect(Collectors.toList());
    }

    private InvoiceLine createInvoiceLine(int productId) {
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(productId));

        if (product.isOutOfStock()) {
            return InvoiceLine.outOfStock(product);
        }

        productRepository.decrementStock(productId);
        return InvoiceLine.forProduct(product);
    }

    private PriceSummary calculatePricing(List<InvoiceLine> lines,
                                          String discountCode) {
        double subtotal = lines.stream()
            .filter(InvoiceLine::isAvailable)
            .mapToDouble(InvoiceLine::getPrice)
            .sum();

        double discountPercent = discountRepository
            .findActiveDiscount(discountCode)
            .orElse(0.0);

        double discountAmount = subtotal * (discountPercent / 100.0);
        double tax = taxCalculator.calculate(subtotal - discountAmount);
        double total = subtotal - discountAmount + tax;

        return new PriceSummary(subtotal, discountAmount, tax, total);
    }

    private Invoice createInvoice(Customer customer,
                                   List<InvoiceLine> lines,
                                   PriceSummary pricing) {
        return new Invoice(customer, lines, pricing);
    }
}

// Email sending is now a separate concern
public class InvoiceEmailSender {
    public void sendInvoice(Invoice invoice) {
        emailService.send(
            invoice.getCustomer().getEmail(),
            "Your Invoice",
            invoiceFormatter.format(invoice)
        );
    }
}

// Formatting is a separate concern
public class InvoiceFormatter {
    public String formatAsText(Invoice invoice) { /* ... */ }
    public String formatAsHtml(Invoice invoice) { /* ... */ }
}
```

```
+-----------------------------------------------------------+
|        Monster Function vs Clean Refactoring              |
+-----------------------------------------------------------+
|                                                           |
|  BEFORE                    |  AFTER                       |
|  100+ lines, 1 function   |  10 functions, 5-15 lines    |
|  5 arguments + flag        |  1 argument (request object) |
|  7 responsibilities        |  1 responsibility each       |
|  Mixed abstractions        |  Consistent levels           |
|  String error codes        |  Proper exceptions           |
|  Hidden side effects       |  Explicit operations         |
|  Untestable                |  Fully testable              |
|  Hard to change            |  Easy to extend              |
|                                                           |
+-----------------------------------------------------------+
```

---

## Common Mistakes

1. **Writing functions that are too long** -- If you need to scroll to see the whole function, it is too long. Break it apart.

2. **Using vague names like `process()`, `handle()`, `manage()`** -- These names tell the reader nothing. Be specific about what is being processed, handled, or managed.

3. **Passing boolean flags** -- Every flag argument doubles the function's responsibilities. Create separate functions instead.

4. **Mixing abstraction levels** -- Do not put SQL queries next to business logic. Do not put HTTP headers next to domain calculations. Each function should live at one level.

5. **Creating hidden side effects** -- If a function modifies global state, writes to a file, sends an email, or changes a database, that action should be visible in the function's name or handled at the appropriate level.

6. **Returning error codes instead of throwing exceptions** -- Error codes force callers into deeply nested if-else chains. Use exceptions and let the error handling happen at the right level.

7. **Writing functions with too many arguments** -- If you need more than three arguments, consider creating a parameter object.

---

## Best Practices

1. **Start with a working mess, then refactor** -- Nobody writes perfectly clean functions on the first pass. Write the code that works, then extract, rename, and restructure until each function does one thing.

2. **Apply the newspaper metaphor** -- High-level functions at the top, lower-level details below. The reader should be able to skim the public methods and understand the story without diving into the details.

3. **Name functions after what they do, not how they do it** -- `calculateShippingCost()` is better than `iterateOverItemsAndSumWeights()`.

4. **Keep argument counts low** -- Zero, one, or two arguments. Group related arguments into objects.

5. **Write functions that can be read without context** -- A well-named function with well-named parameters should be understandable without reading its implementation.

6. **Separate commands from queries** -- Functions that change state should not return values. Functions that return values should not change state.

7. **Extract try/catch bodies** -- The error handling and the logic should live in separate functions.

8. **Test your functions independently** -- If a function is hard to test, it is doing too much. Difficulty testing is a design signal.

---

## Quick Summary

Functions should be small (5 to 15 lines), do exactly one thing, operate at a single level of abstraction, and have descriptive names. They should take as few arguments as possible, never use flag arguments, and have no hidden side effects. Prefer exceptions to error codes. When you encounter a monster function, refactor it into a collection of small, focused functions that read like a story.

---

## Key Points

- Functions should be small. Really small. Five to fifteen lines is the sweet spot.
- Each function should do one thing and do it well.
- Functions should maintain a single level of abstraction. Do not mix high-level business logic with low-level implementation details.
- Descriptive names eliminate the need for comments. Use verbs that describe the action.
- The ideal argument count is zero. One and two are acceptable. Three or more is a code smell.
- Boolean flag arguments announce that a function does two things. Split it.
- Side effects are hidden behaviors that surprise callers. Make all effects visible.
- Commands (change state) and queries (return values) should be separate functions.
- Exceptions are cleaner than error codes for error handling.
- Nobody writes clean functions on the first try. Write the mess, make it work, then clean it up.

---

## Practice Questions

1. You encounter a function called `processData()` that is 80 lines long. It validates input, transforms data, writes to a database, and sends a notification. Describe step by step how you would refactor it following the principles from this chapter.

2. Why is `render(boolean isSuite)` worse than having two separate functions `renderSuite()` and `renderSingleTest()`? What principle does the flag argument violate?

3. Explain the difference between a "command" and a "query" in the context of Command-Query Separation. Give an example of a function that violates this principle and show how to fix it.

4. A colleague argues that writing many small functions creates "too many files" and "too much jumping around." How would you respond to this concern?

5. Look at this function signature: `createUser(String firstName, String lastName, String email, String phone, String street, String city, String state, String zipCode)`. What is wrong with it and how would you improve it?

---

## Exercises

### Exercise 1: Extract and Name

Take this function and refactor it into small, well-named functions:

```python
def handle_order(order_data):
    if not order_data.get("items"):
        print("Error: no items")
        return None
    total = 0
    for item in order_data["items"]:
        if item["quantity"] <= 0:
            print(f"Error: bad quantity for {item['name']}")
            return None
        total += item["price"] * item["quantity"]
    if total > 100:
        total *= 0.9  # 10% discount for large orders
    tax = total * 0.07
    total += tax
    print(f"Order total: ${total:.2f}")
    with open("orders.log", "a") as f:
        f.write(f"Order: ${total:.2f}\n")
    return total
```

### Exercise 2: Eliminate the Flag

Refactor this Java function to eliminate the boolean parameter:

```java
public List<Employee> getEmployees(boolean includeTerminated) {
    List<Employee> result = new ArrayList<>();
    for (Employee emp : allEmployees) {
        if (includeTerminated || emp.isActive()) {
            result.add(emp);
        }
    }
    return result;
}
```

### Exercise 3: Reduce Arguments

This function has too many arguments. Refactor it using a parameter object:

```java
public void sendEmail(String to, String from, String subject,
                      String body, String cc, String bcc,
                      boolean isHtml, int priority) {
    // ...
}
```

---

## What Is Next?

You now know how to write functions that are small, focused, and expressive. But even clean functions can be obscured by bad comments -- or, conversely, clarified by good ones. In Chapter 4, we will explore the art of commenting: when comments help, when they hurt, and how to write code so clear that most comments become unnecessary. You will learn why self-documenting code is the best kind of documentation.
