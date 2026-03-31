# Chapter 6: Error Handling -- Keeping the Happy Path Clean

---

## What You Will Learn

- Why exceptions are superior to error codes for communicating failure
- How to use unchecked exceptions effectively and when checked exceptions cause harm
- How to provide meaningful context in your exceptions so debugging is fast
- How to define exception classes based on the caller's needs, not the implementation
- Why returning null is a bug factory and what to return instead
- The try-catch-finally structure and how to use it without cluttering your code
- How to build a custom exception hierarchy for your application
- The fail fast principle and why it saves you hours of debugging
- How to separate error handling from business logic cleanly

---

## Why This Chapter Matters

Error handling is one of those topics that separates amateur code from professional code. In amateur code, errors are an afterthought -- sprinkled in as `if (result == -1)` checks, swallowed with empty catch blocks, or ignored entirely until production explodes. In professional code, error handling is a first-class concern that is designed into the architecture from the beginning.

The challenge is doing error handling without turning every function into a tangled mess of try-catch blocks and null checks. This chapter teaches you how to handle errors thoroughly while keeping your code readable and your business logic clean.

---

## Exceptions vs. Error Codes: Why Exceptions Win

In the early days of programming, functions communicated failure by returning special values. A function might return `-1` for an error, `0` for success, or `null` to indicate "not found." This approach has a fatal flaw: the caller can ignore the error code without the compiler complaining.

```
+-----------------------------------------------------------+
|         ERROR CODES vs EXCEPTIONS                          |
+-----------------------------------------------------------+
|                                                            |
|  Error Codes:                                              |
|  +--------+    returns -1     +--------+                   |
|  | Caller | <--------------- | Method |                    |
|  +--------+                   +--------+                   |
|  Caller can IGNORE the -1.                                 |
|  No compiler warning. Bug hides silently.                  |
|                                                            |
|  Exceptions:                                               |
|  +--------+    throws Error   +--------+                   |
|  | Caller | <======X========= | Method |                   |
|  +--------+                   +--------+                   |
|  Caller MUST handle or propagate.                          |
|  Cannot be silently ignored.                               |
|  Stack trace pinpoints the failure.                        |
|                                                            |
+-----------------------------------------------------------+
```

### BEFORE: Error Code Spaghetti (Java)

```java
// Java -- BAD: Error codes obscure the business logic
public class OrderService {

    public int processOrder(Order order) {
        int validationResult = validateOrder(order);
        if (validationResult != 0) {
            return validationResult;  // -1 = invalid items, -2 = no stock
        }

        int paymentResult = chargePayment(order);
        if (paymentResult != 0) {
            return paymentResult;  // -3 = card declined, -4 = network error
        }

        int shippingResult = arrangeShipping(order);
        if (shippingResult != 0) {
            // Undo payment because shipping failed
            int refundResult = refundPayment(order);
            if (refundResult != 0) {
                return -99;  // Catastrophic: payment taken but cannot refund
            }
            return shippingResult;  // -5 = no carriers, -6 = invalid address
        }

        int notifyResult = notifyCustomer(order);
        if (notifyResult != 0) {
            // Shipping is done, so we log the notification failure
            // but do not roll back. Or do we? Who knows.
            logError("Notification failed: " + notifyResult);
        }

        return 0;  // Success... probably
    }
}
```

What is wrong with this code? The business logic -- validate, charge, ship, notify -- is buried under a mountain of error-checking boilerplate. Every caller of `processOrder` has to remember what `-1`, `-2`, `-3`, `-4`, `-5`, `-6`, and `-99` mean. Nothing enforces that. Nothing prevents a caller from ignoring the return value entirely.

### AFTER: Clean Exception Handling (Java)

```java
// Java -- GOOD: Exceptions separate error handling from business logic
public class OrderService {

    public void processOrder(Order order) {
        validateOrder(order);
        chargePayment(order);

        try {
            arrangeShipping(order);
        } catch (ShippingException e) {
            refundPayment(order);
            throw new OrderProcessingException(
                "Shipping failed after payment. Refund issued.", e
            );
        }

        try {
            notifyCustomer(order);
        } catch (NotificationException e) {
            logger.warn("Customer notification failed for order {}",
                order.getId(), e);
            // Non-critical: order still succeeds
        }
    }
}
```

The happy path reads like a story: validate, charge, ship, notify. Error handling is present but does not obscure the flow. Each exception carries its own meaning -- you do not need a lookup table to understand `ShippingException`.

### BEFORE: Error Code Spaghetti (Python)

```python
# Python -- BAD: Error codes returned as tuples
class OrderService:

    def process_order(self, order):
        success, error = self.validate_order(order)
        if not success:
            return False, error

        success, error = self.charge_payment(order)
        if not success:
            return False, f"Payment failed: {error}"

        success, error = self.arrange_shipping(order)
        if not success:
            refund_ok, refund_err = self.refund_payment(order)
            if not refund_ok:
                return False, f"CRITICAL: {error} AND refund failed: {refund_err}"
            return False, f"Shipping failed: {error}. Payment refunded."

        success, error = self.notify_customer(order)
        if not success:
            print(f"Warning: notification failed: {error}")
            # Continue anyway? Maybe?

        return True, None
```

### AFTER: Clean Exception Handling (Python)

```python
# Python -- GOOD: Exceptions keep the happy path clean
class OrderService:

    def process_order(self, order: Order) -> None:
        self.validate_order(order)
        self.charge_payment(order)

        try:
            self.arrange_shipping(order)
        except ShippingError as e:
            self.refund_payment(order)
            raise OrderProcessingError(
                f"Shipping failed after payment. Refund issued."
            ) from e

        try:
            self.notify_customer(order)
        except NotificationError:
            logger.warning(
                "Customer notification failed for order %s",
                order.id,
            )
```

---

## Use Unchecked Exceptions

Java has two kinds of exceptions: checked (you must declare them with `throws` or catch them) and unchecked (subclasses of `RuntimeException`, no declaration required). Checked exceptions seemed like a good idea -- the compiler forces you to handle errors! -- but in practice they cause significant problems.

```
+-----------------------------------------------------------+
|       CHECKED vs UNCHECKED EXCEPTIONS                      |
+-----------------------------------------------------------+
|                                                            |
|  Checked (Java):                                           |
|    - Must be declared in method signature                  |
|    - Every caller must handle or re-declare                |
|    - Changes propagate through entire call chain           |
|    - Example: IOException, SQLException                    |
|                                                            |
|  Unchecked (Java):                                         |
|    - No declaration required                               |
|    - Caller handles only if they choose to                 |
|    - Changes do not break calling code                     |
|    - Example: IllegalArgumentException, RuntimeException   |
|                                                            |
|  Python:                                                   |
|    - ALL exceptions are unchecked                          |
|    - No throws declaration in method signatures            |
|    - Document expected exceptions in docstrings            |
|                                                            |
+-----------------------------------------------------------+
```

The problem with checked exceptions is that they violate the Open-Closed Principle. If a low-level method adds a new checked exception, every method in the call chain above it must be modified to either catch or declare that exception. A single change at the bottom can cause modifications to dozens of files.

```java
// Java -- Checked exception chain reaction
// If parseData adds a new checked exception, ALL callers must change:

// Level 3 (low-level)
public Data parseData(String raw) throws ParseException, ValidationException {
    // Adding FormatException here forces changes in Levels 2 and 1
}

// Level 2 (mid-level) -- must declare the new exception
public Report generateReport(String input)
        throws ParseException, ValidationException {
    Data data = parseData(input);
    return buildReport(data);
}

// Level 1 (high-level) -- must also change
public void handleRequest(Request request)
        throws ParseException, ValidationException {
    Report report = generateReport(request.getData());
    sendResponse(report);
}
```

**Prefer unchecked exceptions.** Use `RuntimeException` subclasses in Java. In Python, all exceptions are already unchecked.

```java
// Java -- GOOD: Unchecked exception, no chain reaction
public class ParseException extends RuntimeException {

    public ParseException(String message) {
        super(message);
    }

    public ParseException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

---

## Provide Context with Exceptions

When an exception occurs, the developer debugging it needs to know three things: what happened, where it happened, and why it happened. A good exception message answers all three.

**BAD exception messages:**

```java
throw new RuntimeException("Error");
throw new RuntimeException("Failed");
throw new IllegalArgumentException("Invalid input");
```

**GOOD exception messages:**

```java
throw new OrderNotFoundException(
    "Order with ID 12345 not found in database 'orders_prod'"
);

throw new PaymentDeclinedException(
    "Payment of $49.99 declined for customer C-789. "
    + "Reason: insufficient funds. Card ending in 4242."
);

throw new ConfigurationException(
    "Required environment variable 'DATABASE_URL' is not set. "
    + "Set it in .env or as a system environment variable."
);
```

```python
# Python -- GOOD: Context-rich exceptions
raise OrderNotFoundError(
    f"Order with ID {order_id} not found in database '{db_name}'"
)

raise PaymentDeclinedError(
    f"Payment of ${amount:.2f} declined for customer {customer_id}. "
    f"Reason: {decline_reason}. Card ending in {card_last_four}."
)

raise ConfigurationError(
    "Required environment variable 'DATABASE_URL' is not set. "
    "Set it in .env or as a system environment variable."
)
```

### Preserve the Cause Chain

When you catch an exception and throw a new one, always include the original exception as the cause. This preserves the full stack trace for debugging.

```java
// Java -- GOOD: Preserve the cause
try {
    database.save(order);
} catch (SQLException e) {
    throw new OrderPersistenceException(
        "Failed to save order " + order.getId(), e  // 'e' is the cause
    );
}
```

```python
# Python -- GOOD: Use 'from' to chain exceptions
try:
    database.save(order)
except DatabaseError as e:
    raise OrderPersistenceError(
        f"Failed to save order {order.id}"
    ) from e  # Preserves the original traceback
```

---

## Define Exception Classes by the Caller's Needs

When you design your exception hierarchy, think about what the caller needs to do when an error occurs, not about what went wrong internally.

**BAD: Exceptions organized by internal cause:**

```java
// Java -- BAD: Caller has to know about internal details
try {
    port.open();
} catch (DeviceResponseException e) {
    reportPortError(e);
    logger.error("Device response error", e);
} catch (ATM1212UnlockedException e) {
    reportPortError(e);
    logger.error("Unlock error", e);
} catch (GMXError e) {
    reportPortError(e);
    logger.error("GMX error", e);
}
```

All three catch blocks do the same thing. The caller does not care whether the device responded incorrectly or used the wrong protocol. The caller just needs to know: did the port open or not?

**GOOD: One exception that wraps the details:**

```java
// Java -- GOOD: Wrap third-party exceptions
public class LocalPort {

    private final ACMEPort innerPort;

    public void open() {
        try {
            innerPort.open();
        } catch (DeviceResponseException e) {
            throw new PortDeviceFailure(e);
        } catch (ATM1212UnlockedException e) {
            throw new PortDeviceFailure(e);
        } catch (GMXError e) {
            throw new PortDeviceFailure(e);
        }
    }
}

// Now the caller has one clean catch:
try {
    port.open();
} catch (PortDeviceFailure e) {
    reportError(e);
    logger.error("Failed to open port", e);
}
```

```python
# Python -- GOOD: Wrap third-party exceptions
class LocalPort:

    def __init__(self, inner_port):
        self._inner_port = inner_port

    def open(self) -> None:
        try:
            self._inner_port.open()
        except (DeviceResponseError, UnlockedError, GMXError) as e:
            raise PortDeviceFailure(
                f"Failed to open port: {e}"
            ) from e


# Caller sees one clean exception
try:
    port.open()
except PortDeviceFailure as e:
    report_error(e)
    logger.error("Failed to open port", exc_info=True)
```

---

## Do Not Return Null

Returning `null` (Java) or `None` (Python) to indicate absence is one of the most common sources of bugs. Every caller must remember to check for null, and if even one forgets, you get a `NullPointerException` at runtime.

```
+-----------------------------------------------------------+
|           THE NULL PROBLEM                                 |
+-----------------------------------------------------------+
|                                                            |
|  Method returns null                                       |
|       |                                                    |
|       v                                                    |
|  Caller A checks for null    --> OK                        |
|  Caller B checks for null    --> OK                        |
|  Caller C forgets to check   --> NullPointerException      |
|  Caller D forgets to check   --> NullPointerException      |
|                                                            |
|  The more callers, the more likely someone forgets.        |
|  null is a ticking time bomb in your API.                  |
|                                                            |
+-----------------------------------------------------------+
```

### BEFORE: Null Returns

```java
// Java -- BAD: Returning null
public class UserRepository {

    public User findByEmail(String email) {
        // Returns null if not found
        return database.query("SELECT * FROM users WHERE email = ?", email);
    }
}

// Every caller must do this -- and many will forget:
User user = repository.findByEmail(email);
if (user != null) {
    sendWelcomeEmail(user);  // Safe
} else {
    // Handle not found
}

// The inevitable bug:
User user = repository.findByEmail(email);
sendWelcomeEmail(user);  // NullPointerException if not found
```

### AFTER: Optional and Empty Collections

```java
// Java -- GOOD: Return Optional for single values
public class UserRepository {

    public Optional<User> findByEmail(String email) {
        User user = database.query(
            "SELECT * FROM users WHERE email = ?", email
        );
        return Optional.ofNullable(user);
    }
}

// Caller is forced to handle the absence:
repository.findByEmail(email)
    .ifPresentOrElse(
        user -> sendWelcomeEmail(user),
        () -> logger.warn("User not found: {}", email)
    );

// Or with a default:
User user = repository.findByEmail(email)
    .orElseThrow(() -> new UserNotFoundException(email));
```

```java
// Java -- GOOD: Return empty collection, never null
public List<Order> findOrdersByCustomer(String customerId) {
    List<Order> orders = database.query(
        "SELECT * FROM orders WHERE customer_id = ?", customerId
    );
    return orders != null ? orders : Collections.emptyList();
}

// Caller can always iterate safely -- no null check needed:
for (Order order : findOrdersByCustomer(customerId)) {
    processOrder(order);
}
```

In Python, the same principles apply:

```python
# Python -- BAD: Returning None
def find_user_by_email(email: str):
    user = database.query("SELECT * FROM users WHERE email = %s", email)
    return user  # Could be None


# Python -- GOOD: Raise an exception when absence is an error
def find_user_by_email(email: str) -> User:
    user = database.query("SELECT * FROM users WHERE email = %s", email)
    if user is None:
        raise UserNotFoundError(f"No user with email: {email}")
    return user


# Python -- GOOD: Return a sentinel or use Optional typing when absence is normal
def find_user_by_email(email: str) -> User | None:
    """Returns the User or None if not found."""
    return database.query("SELECT * FROM users WHERE email = %s", email)


# Python -- GOOD: Return empty collection, never None
def find_orders_by_customer(customer_id: str) -> list[Order]:
    orders = database.query(
        "SELECT * FROM orders WHERE customer_id = %s", customer_id
    )
    return orders or []
```

---

## Do Not Pass Null

If returning null is bad, passing null as an argument is worse. When a method receives a null argument, it has to decide what to do. Most of the time, the right response is to blow up immediately.

```java
// Java -- BAD: Accepting null and trying to handle it
public double calculateArea(Double width, Double height) {
    if (width == null) {
        width = 0.0;  // Silent corruption of intent
    }
    if (height == null) {
        height = 0.0;
    }
    return width * height;
}

// Java -- GOOD: Reject null immediately
public double calculateArea(double width, double height) {
    if (width <= 0 || height <= 0) {
        throw new IllegalArgumentException(
            String.format(
                "Width and height must be positive. Got width=%f, height=%f",
                width, height
            )
        );
    }
    return width * height;
}
```

```python
# Python -- BAD: Silently accepting None
def calculate_area(width, height):
    width = width or 0
    height = height or 0
    return width * height  # Returns 0 instead of failing -- hides bugs


# Python -- GOOD: Fail fast on invalid input
def calculate_area(width: float, height: float) -> float:
    if width <= 0 or height <= 0:
        raise ValueError(
            f"Width and height must be positive. "
            f"Got width={width}, height={height}"
        )
    return width * height
```

---

## Try-Catch-Finally Structure

The `try-catch-finally` (Java) or `try-except-finally` (Python) structure is your primary tool for error handling. Use it correctly:

- **try**: The happy path code that might throw an exception
- **catch/except**: What to do when a specific error occurs
- **finally**: Cleanup that must happen regardless of success or failure

```java
// Java -- Clean try-catch-finally
public String readFile(String path) {
    BufferedReader reader = null;
    try {
        reader = new BufferedReader(new FileReader(path));
        StringBuilder content = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            content.append(line).append("\n");
        }
        return content.toString();
    } catch (FileNotFoundException e) {
        throw new ConfigFileException(
            "Configuration file not found: " + path, e
        );
    } catch (IOException e) {
        throw new ConfigFileException(
            "Error reading configuration file: " + path, e
        );
    } finally {
        if (reader != null) {
            try {
                reader.close();
            } catch (IOException e) {
                logger.warn("Failed to close reader for: {}", path, e);
            }
        }
    }
}

// Java -- Even cleaner with try-with-resources
public String readFile(String path) {
    try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
        StringBuilder content = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            content.append(line).append("\n");
        }
        return content.toString();
    } catch (FileNotFoundException e) {
        throw new ConfigFileException(
            "Configuration file not found: " + path, e
        );
    } catch (IOException e) {
        throw new ConfigFileException(
            "Error reading configuration file: " + path, e
        );
    }
}
```

```python
# Python -- Clean try-except-finally
def read_file(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        raise ConfigFileError(
            f"Configuration file not found: {path}"
        )
    except PermissionError:
        raise ConfigFileError(
            f"Permission denied reading: {path}"
        )
    except OSError as e:
        raise ConfigFileError(
            f"Error reading configuration file: {path}"
        ) from e
```

---

## Custom Exception Hierarchy

For any non-trivial application, you should build a hierarchy of custom exceptions. This lets callers decide how specifically they want to handle errors.

```
+-----------------------------------------------------------+
|           EXCEPTION HIERARCHY EXAMPLE                      |
+-----------------------------------------------------------+
|                                                            |
|  AppException (base for all app exceptions)                |
|    |                                                       |
|    +-- OrderException                                      |
|    |     +-- OrderNotFoundException                        |
|    |     +-- OrderProcessingException                      |
|    |     +-- PaymentDeclinedException                      |
|    |                                                       |
|    +-- UserException                                       |
|    |     +-- UserNotFoundException                         |
|    |     +-- DuplicateEmailException                       |
|    |     +-- InvalidCredentialsException                   |
|    |                                                       |
|    +-- InfrastructureException                             |
|          +-- DatabaseConnectionException                   |
|          +-- ExternalServiceException                      |
|          +-- ConfigurationException                        |
|                                                            |
+-----------------------------------------------------------+
```

### Java Implementation

```java
// Java -- Base exception for the application
public class AppException extends RuntimeException {

    private final String errorCode;

    public AppException(String message, String errorCode) {
        super(message);
        this.errorCode = errorCode;
    }

    public AppException(String message, String errorCode, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }

    public String getErrorCode() {
        return errorCode;
    }
}

// Domain-specific exceptions
public class OrderNotFoundException extends AppException {

    public OrderNotFoundException(long orderId) {
        super(
            "Order not found: " + orderId,
            "ORDER_NOT_FOUND"
        );
    }
}

public class PaymentDeclinedException extends AppException {

    public PaymentDeclinedException(String reason, String cardLastFour) {
        super(
            String.format(
                "Payment declined. Reason: %s. Card ending in %s.",
                reason, cardLastFour
            ),
            "PAYMENT_DECLINED"
        );
    }
}
```

### Python Implementation

```python
# Python -- Custom exception hierarchy

class AppError(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, error_code: str):
        super().__init__(message)
        self.error_code = error_code


class OrderError(AppError):
    """Base for order-related errors."""
    pass


class OrderNotFoundError(OrderError):

    def __init__(self, order_id: int):
        super().__init__(
            f"Order not found: {order_id}",
            "ORDER_NOT_FOUND",
        )
        self.order_id = order_id


class PaymentDeclinedError(OrderError):

    def __init__(self, reason: str, card_last_four: str):
        super().__init__(
            f"Payment declined. Reason: {reason}. "
            f"Card ending in {card_last_four}.",
            "PAYMENT_DECLINED",
        )
        self.reason = reason
        self.card_last_four = card_last_four
```

---

## The Fail Fast Principle

Fail fast means: if something is wrong, stop immediately with a clear error rather than continuing with corrupted state. The earlier you detect and report a problem, the easier it is to fix.

```
+-----------------------------------------------------------+
|              FAIL FAST vs FAIL SLOW                        |
+-----------------------------------------------------------+
|                                                            |
|  Fail Slow (BAD):                                         |
|  Input --> Process --> Process --> Process --> ERROR!       |
|  "Something went wrong somewhere... but where?"            |
|                                                            |
|  Fail Fast (GOOD):                                        |
|  Input --> VALIDATE --> ERROR!                             |
|  "Invalid email format: 'not-an-email'"                   |
|                                                            |
|  Fail fast = less debugging, clearer errors, safer code   |
|                                                            |
+-----------------------------------------------------------+
```

```java
// Java -- GOOD: Fail fast with guard clauses
public class TransferService {

    public void transfer(Account from, Account to, BigDecimal amount) {
        // Validate everything before doing anything
        Objects.requireNonNull(from, "Source account must not be null");
        Objects.requireNonNull(to, "Target account must not be null");
        Objects.requireNonNull(amount, "Amount must not be null");

        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException(
                "Transfer amount must be positive: " + amount
            );
        }

        if (from.equals(to)) {
            throw new IllegalArgumentException(
                "Cannot transfer to the same account: " + from.getId()
            );
        }

        if (from.getBalance().compareTo(amount) < 0) {
            throw new InsufficientFundsException(from.getId(), amount);
        }

        // Happy path -- all validation passed
        from.debit(amount);
        to.credit(amount);
    }
}
```

```python
# Python -- GOOD: Fail fast with guard clauses
class TransferService:

    def transfer(
        self,
        from_account: Account,
        to_account: Account,
        amount: Decimal,
    ) -> None:
        if amount <= 0:
            raise ValueError(
                f"Transfer amount must be positive: {amount}"
            )

        if from_account == to_account:
            raise ValueError(
                f"Cannot transfer to the same account: "
                f"{from_account.id}"
            )

        if from_account.balance < amount:
            raise InsufficientFundsError(from_account.id, amount)

        # Happy path -- all validation passed
        from_account.debit(amount)
        to_account.credit(amount)
```

---

## Error Handling vs. Business Logic Separation

The most important principle in this chapter: error handling and business logic should live in separate places. When they are interleaved, both become hard to understand.

### BEFORE: Error Handling Mixed with Business Logic

```java
// Java -- BAD: Error handling and business logic tangled
public class ReportService {

    public Report generateMonthlyReport(int year, int month) {
        List<Transaction> transactions = null;
        try {
            transactions = transactionRepo.findByMonth(year, month);
        } catch (DatabaseException e) {
            logger.error("DB error", e);
            return null;
        }

        if (transactions == null || transactions.isEmpty()) {
            return new Report(year, month, 0, 0, Collections.emptyList());
        }

        double totalRevenue = 0;
        double totalExpenses = 0;
        List<ReportLine> lines = new ArrayList<>();

        for (Transaction t : transactions) {
            try {
                if (t.getType() == TransactionType.REVENUE) {
                    double converted = 0;
                    try {
                        converted = currencyService.convert(
                            t.getAmount(), t.getCurrency(), "USD"
                        );
                    } catch (CurrencyConversionException e) {
                        logger.warn("Currency conversion failed", e);
                        converted = t.getAmount();  // Use unconverted
                    }
                    totalRevenue += converted;
                    lines.add(new ReportLine(t, converted));
                } else {
                    double converted = 0;
                    try {
                        converted = currencyService.convert(
                            t.getAmount(), t.getCurrency(), "USD"
                        );
                    } catch (CurrencyConversionException e) {
                        logger.warn("Currency conversion failed", e);
                        converted = t.getAmount();
                    }
                    totalExpenses += converted;
                    lines.add(new ReportLine(t, converted));
                }
            } catch (Exception e) {
                logger.error("Error processing transaction: " + t.getId(), e);
            }
        }

        return new Report(year, month, totalRevenue, totalExpenses, lines);
    }
}
```

### AFTER: Separated Concerns

```java
// Java -- GOOD: Business logic is clean, error handling is separate
public class ReportService {

    public Report generateMonthlyReport(int year, int month) {
        List<Transaction> transactions = fetchTransactions(year, month);

        if (transactions.isEmpty()) {
            return Report.empty(year, month);
        }

        return buildReport(year, month, transactions);
    }

    private Report buildReport(
            int year,
            int month,
            List<Transaction> transactions) {

        double totalRevenue = 0;
        double totalExpenses = 0;
        List<ReportLine> lines = new ArrayList<>();

        for (Transaction transaction : transactions) {
            double amount = convertToUsd(transaction);
            lines.add(new ReportLine(transaction, amount));

            if (transaction.getType() == TransactionType.REVENUE) {
                totalRevenue += amount;
            } else {
                totalExpenses += amount;
            }
        }

        return new Report(year, month, totalRevenue, totalExpenses, lines);
    }

    private List<Transaction> fetchTransactions(int year, int month) {
        try {
            return transactionRepo.findByMonth(year, month);
        } catch (DatabaseException e) {
            throw new ReportGenerationException(
                "Failed to fetch transactions for " + year + "-" + month, e
            );
        }
    }

    private double convertToUsd(Transaction transaction) {
        try {
            return currencyService.convert(
                transaction.getAmount(),
                transaction.getCurrency(),
                "USD"
            );
        } catch (CurrencyConversionException e) {
            logger.warn(
                "Currency conversion failed for transaction {}. "
                + "Using original amount.",
                transaction.getId(), e
            );
            return transaction.getAmount();
        }
    }
}
```

The Python version follows the same separation:

```python
# Python -- GOOD: Business logic clean, error handling in helper methods
class ReportService:

    def generate_monthly_report(self, year: int, month: int) -> Report:
        transactions = self._fetch_transactions(year, month)

        if not transactions:
            return Report.empty(year, month)

        return self._build_report(year, month, transactions)

    def _build_report(
        self,
        year: int,
        month: int,
        transactions: list[Transaction],
    ) -> Report:
        total_revenue = 0.0
        total_expenses = 0.0
        lines = []

        for transaction in transactions:
            amount = self._convert_to_usd(transaction)
            lines.append(ReportLine(transaction, amount))

            if transaction.type == TransactionType.REVENUE:
                total_revenue += amount
            else:
                total_expenses += amount

        return Report(year, month, total_revenue, total_expenses, lines)

    def _fetch_transactions(
        self, year: int, month: int
    ) -> list[Transaction]:
        try:
            return self.transaction_repo.find_by_month(year, month)
        except DatabaseError as e:
            raise ReportGenerationError(
                f"Failed to fetch transactions for {year}-{month}"
            ) from e

    def _convert_to_usd(self, transaction: Transaction) -> float:
        try:
            return self.currency_service.convert(
                transaction.amount, transaction.currency, "USD"
            )
        except CurrencyConversionError:
            logger.warning(
                "Currency conversion failed for transaction %s. "
                "Using original amount.",
                transaction.id,
            )
            return transaction.amount
```

---

## Common Mistakes

1. **Empty catch blocks.** Catching an exception and doing nothing with it is almost always a bug. If you truly want to ignore an exception, add a comment explaining why.

2. **Catching Exception (the base class).** Catching every possible exception hides bugs. Catch specific exceptions that you know how to handle.

3. **Using exceptions for control flow.** Exceptions should represent exceptional conditions, not normal branching. Do not use try-catch as a replacement for if-else.

4. **Returning null from methods.** Return `Optional`, throw an exception, or return an empty collection instead.

5. **Logging and re-throwing the same exception.** This produces duplicate log entries. Either log it and handle it, or re-throw it for a higher-level handler to log.

6. **Exception messages without context.** "Error occurred" tells you nothing. Include the what, where, and why.

7. **Swallowing the cause chain.** When wrapping exceptions, always pass the original as the cause (`throw new X(msg, e)` in Java, `raise X() from e` in Python).

---

## Best Practices

1. **Use exceptions instead of error codes.** They cannot be silently ignored, carry stack traces, and keep the happy path clean.

2. **Prefer unchecked exceptions.** Checked exceptions cause cascading changes through the call chain.

3. **Provide rich context in exception messages.** Include IDs, values, and expected vs. actual states.

4. **Define exceptions by the caller's needs.** One `PortDeviceFailure` is better than five low-level device exceptions if the caller handles them all the same way.

5. **Never return null.** Use `Optional`, empty collections, or throw exceptions for truly exceptional cases.

6. **Fail fast.** Validate inputs at the boundary and throw immediately if something is wrong.

7. **Separate error handling from business logic.** Extract error-prone operations into helper methods that handle their own errors.

8. **Build a custom exception hierarchy.** Start with a base `AppException` and create domain-specific subclasses.

---

## Quick Summary

```
+-----------------------------------------------------------+
|              ERROR HANDLING CHEAT SHEET                     |
+-----------------------------------------------------------+
|                                                            |
|  DO:                                                       |
|    - Use exceptions, not error codes                       |
|    - Use unchecked exceptions (RuntimeException)           |
|    - Provide context: what, where, why                     |
|    - Return Optional or empty collections, not null        |
|    - Fail fast with guard clauses                          |
|    - Separate error handling from business logic           |
|    - Preserve the cause chain (throw ... from e)           |
|    - Build a custom exception hierarchy                    |
|                                                            |
|  DON'T:                                                    |
|    - Swallow exceptions with empty catch blocks            |
|    - Catch the base Exception class                        |
|    - Use exceptions for normal control flow                |
|    - Return null from methods                              |
|    - Pass null as arguments                                |
|    - Log AND re-throw the same exception                   |
|    - Write exception messages without context              |
|                                                            |
+-----------------------------------------------------------+
```

---

## Key Points

- Exceptions are superior to error codes because they cannot be silently ignored and they separate the happy path from error handling
- Unchecked exceptions (RuntimeException in Java, all Python exceptions) avoid cascading changes through the call chain
- Exception messages must include context: what failed, what values were involved, and what was expected
- Design exception classes around what the caller needs to do, not what went wrong internally
- Returning null forces every caller to add null checks and guarantees that someone will forget -- use Optional or empty collections instead
- The fail fast principle means validating early and failing with clear messages before corrupted state can spread
- Separating error handling from business logic keeps both readable -- extract error-prone calls into helper methods

---

## Practice Questions

1. Explain why error codes are problematic compared to exceptions. Give a specific example of how a caller might silently ignore an error code.

2. What is the difference between checked and unchecked exceptions in Java? Why do most modern Java developers prefer unchecked exceptions?

3. What three pieces of information should every exception message contain? Write an example exception message for a failed database connection.

4. Why is returning null from a method considered bad practice? What are three alternatives?

5. Explain the fail fast principle. Why is it better to fail immediately at the boundary than to continue processing with invalid data?

---

## Exercises

### Exercise 1: Refactor Error Codes to Exceptions

Take the following error-code-based code and refactor it to use exceptions. Create appropriate custom exception classes and ensure the happy path reads cleanly.

```python
def register_user(username, email, password):
    if not username:
        return {"error": "USERNAME_EMPTY", "success": False}
    if len(password) < 8:
        return {"error": "PASSWORD_TOO_SHORT", "success": False}
    existing = db.find_user_by_email(email)
    if existing is not None:
        return {"error": "EMAIL_TAKEN", "success": False}
    result = db.create_user(username, email, password)
    if result == -1:
        return {"error": "DB_ERROR", "success": False}
    email_result = send_welcome_email(email)
    if email_result == -1:
        return {"error": "EMAIL_SEND_FAILED", "success": False}
    return {"success": True, "user_id": result}
```

### Exercise 2: Build an Exception Hierarchy

Design and implement a custom exception hierarchy for an e-commerce application. Include at least three levels of specificity (base, domain, specific) and cover at least two domains (orders and users). Each exception should accept relevant context in its constructor and produce a clear, debuggable message.

### Exercise 3: Eliminate Null Returns

Find three methods in one of your own projects (or an open-source project) that return null. For each one, determine the appropriate replacement: Optional, empty collection, or exception. Refactor the method and update one of its callers.

---

## What Is Next?

With clean error handling in place, your code can fail gracefully and communicate problems clearly. The next few chapters dive into the SOLID principles -- five foundational rules that guide how you structure classes and their relationships. You will start with the Single Responsibility Principle and build up to the full set, learning how each principle prevents a specific category of design problems.
