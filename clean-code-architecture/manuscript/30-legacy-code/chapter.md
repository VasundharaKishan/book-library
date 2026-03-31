# Chapter 30: Working with Legacy Code

## What You Will Learn

- What legacy code really is (hint: it is not just "old code")
- Characterization tests: documenting what code actually does before changing it
- The Strangler Fig pattern: gradually replacing a legacy system without a big-bang rewrite
- Branch by Abstraction: swapping implementations behind an interface
- The Sprout Method/Class technique: adding new behavior without modifying risky code
- When to rewrite vs when to refactor
- How to make untestable legacy code testable

## Why This Chapter Matters

Every developer will eventually face legacy code. Maybe you inherited a codebase from a developer who left. Maybe your own code from three years ago has become legacy. Maybe you joined a company with a ten-year-old monolith that nobody fully understands.

Michael Feathers defined legacy code simply: **code without tests.** Without tests, you cannot change the code with confidence. Every modification is a gamble. You fix one bug and introduce two more. You add a feature and break something unrelated. You refactor and hope for the best.

This chapter gives you practical techniques for working safely with code you did not write and do not fully understand. These techniques let you make changes with confidence, gradually improve the codebase, and avoid the temptation of the catastrophic big-bang rewrite.

---

## What Is Legacy Code?

```
LEGACY CODE IS NOT JUST "OLD CODE":

  Old code WITH tests,       Old code WITHOUT tests,
  clear structure,           no documentation,
  good documentation:        tangled dependencies:
  +------------------+       +------------------+
  | Mature Code      |       | Legacy Code      |
  | (not legacy)     |       | (dangerous to    |
  |                  |       |  change)         |
  +------------------+       +------------------+

  New code WITHOUT tests,
  written last month,
  no one understands:
  +------------------+
  | Also Legacy Code |
  | (age does not    |
  |  matter)         |
  +------------------+

  LEGACY CODE = Code you are afraid to change.

  The fear comes from:
  - No tests to catch regressions
  - No documentation to explain intent
  - Tangled dependencies that make changes ripple
  - Knowledge silos (only one person understood it)
```

---

## Step 1: Understand Before You Change

Before modifying legacy code, you must understand what it currently does. Not what it should do, not what the documentation says -- what it actually does right now.

### Reading Strategies

```
STRATEGIES FOR UNDERSTANDING LEGACY CODE:

  1. START FROM THE OUTSIDE
     Find the entry points (controllers, main methods,
     API endpoints). Trace the flow inward.

  2. DRAW THE DEPENDENCY MAP
     +----------+     +-----------+     +--------+
     | Controller| --> | Service   | --> | DAO    |
     |          | --> | Validator | --> | Cache  |
     |          |     | Helper    |     | Logger |
     +----------+     +-----------+     +--------+
     Who calls whom? Who depends on what?

  3. FIND THE HOTSPOTS
     Use version control to find files that change
     most often. Frequently changed files are where
     bugs live and where understanding matters most.

     git log --format=format: --name-only | sort | uniq -c | sort -rn | head -20

  4. LOOK AT THE TESTS (if any exist)
     Tests are documentation. They show how the code
     is expected to behave.

  5. TALK TO PEOPLE
     Former developers, users, support staff -- anyone
     who knows how the system behaves.
```

---

## Step 2: Characterization Tests

A characterization test documents the current behavior of the code, whether that behavior is correct or not. It is not about testing what the code should do -- it is about pinning down what it actually does.

### Why Characterization Tests?

```
THE CHARACTERIZATION TEST MINDSET:

  Normal test:           Characterization test:
  "The code SHOULD       "The code CURRENTLY
   return 42"             returns 42"

  If the test fails:     If the test fails:
  "The code has a bug"   "I accidentally changed
                          the behavior"

  Purpose:               Purpose:
  Verify correctness     Detect unintended changes
```

### Java Example

```java
// You have this legacy method. You do not fully understand it.
// You need to modify it but are afraid of breaking something.
public class LegacyTaxCalculator {

    public double calculateTax(double amount, String stateCode, boolean isExempt) {
        if (isExempt) return 0;
        double rate = 0.0;
        if (stateCode.equals("CA")) rate = 0.0725;
        else if (stateCode.equals("TX")) rate = 0.0625;
        else if (stateCode.equals("NY")) rate = 0.08;
        else if (stateCode.equals("OR")) rate = 0.0;
        else rate = 0.05;

        double tax = amount * rate;
        if (amount > 1000) tax *= 0.95;  // Mysterious discount?

        return Math.round(tax * 100.0) / 100.0;
    }
}

// CHARACTERIZATION TESTS: Pin down the current behavior
class LegacyTaxCalculatorTest {

    private LegacyTaxCalculator calculator = new LegacyTaxCalculator();

    @Test
    void california_standard_tax() {
        // We OBSERVED this result. We document it, not judge it.
        assertEquals(7.25, calculator.calculateTax(100.0, "CA", false));
    }

    @Test
    void california_over_1000_gets_discount() {
        // Discovered: amounts over $1000 get 5% off the tax
        assertEquals(103.36, calculator.calculateTax(1500.0, "CA", false));
    }

    @Test
    void exempt_returns_zero() {
        assertEquals(0.0, calculator.calculateTax(500.0, "CA", true));
    }

    @Test
    void texas_standard_tax() {
        assertEquals(6.25, calculator.calculateTax(100.0, "TX", false));
    }

    @Test
    void unknown_state_uses_default_rate() {
        // Default rate is 5%
        assertEquals(5.0, calculator.calculateTax(100.0, "ZZ", false));
    }

    @Test
    void oregon_has_no_tax() {
        assertEquals(0.0, calculator.calculateTax(100.0, "OR", false));
    }

    @Test
    void zero_amount() {
        assertEquals(0.0, calculator.calculateTax(0.0, "CA", false));
    }

    @Test
    void negative_amount() {
        // Discovered: negative amounts produce negative tax!
        // This might be a bug, but we document the current behavior.
        assertEquals(-7.25, calculator.calculateTax(-100.0, "CA", false));
    }
}
```

```python
# CHARACTERIZATION TESTS in Python
# Pin down current behavior before making any changes

class LegacyTaxCalculator:
    def calculate_tax(self, amount, state_code, is_exempt):
        if is_exempt:
            return 0
        rates = {"CA": 0.0725, "TX": 0.0625, "NY": 0.08, "OR": 0.0}
        rate = rates.get(state_code, 0.05)
        tax = amount * rate
        if amount > 1000:
            tax *= 0.95  # Mysterious discount
        return round(tax, 2)


# Characterization tests
def test_california_standard():
    calc = LegacyTaxCalculator()
    assert calc.calculate_tax(100.0, "CA", False) == 7.25

def test_california_over_1000_gets_discount():
    calc = LegacyTaxCalculator()
    assert calc.calculate_tax(1500.0, "CA", False) == 103.36

def test_exempt_returns_zero():
    calc = LegacyTaxCalculator()
    assert calc.calculate_tax(500.0, "CA", True) == 0

def test_unknown_state_uses_default():
    calc = LegacyTaxCalculator()
    assert calc.calculate_tax(100.0, "ZZ", False) == 5.0

def test_negative_amount():
    calc = LegacyTaxCalculator()
    # Documenting current behavior, not asserting correctness
    assert calc.calculate_tax(-100.0, "CA", False) == -7.25
```

### Writing Characterization Tests: The Process

```
HOW TO WRITE CHARACTERIZATION TESTS:

  1. Pick an input you want to understand
  2. Call the method with that input
  3. Observe the actual output
  4. Write a test that asserts the actual output

  Do NOT guess what the output should be.
  Run the code and OBSERVE what it does.

  Repeat with different inputs until you have
  covered the important paths through the code.

  +-----+     +--------+     +--------+     +------+
  | Pick|---->| Call   |---->| Observe|---->| Write|
  |Input|     | Method |     | Output |     | Test |
  +-----+     +--------+     +--------+     +------+
     ^                                          |
     |                                          |
     +------------- repeat ---------------------+
```

---

## The Strangler Fig Pattern

Named after the strangler fig tree that slowly grows around another tree until it replaces it entirely. Apply the same idea to legacy systems: gradually replace parts while the old system continues running.

```
STRANGLER FIG PATTERN:

  Phase 1: New system handles 0%, old handles 100%

  +--------+     +------------------+
  | Users  |---->| OLD SYSTEM       |
  |        |     | (100% of traffic)|
  +--------+     +------------------+

  Phase 2: Route SOME requests to new system

  +--------+     +----------+     +------------------+
  | Users  |---->| ROUTER   |---->| OLD SYSTEM       |
  |        |     |          |     | (80% of traffic) |
  +--------+     |          |     +------------------+
                 |          |
                 |          |     +------------------+
                 |          +---->| NEW SYSTEM       |
                 +----------+     | (20% of traffic) |
                                  +------------------+

  Phase 3: New system handles most traffic

  +--------+     +----------+     +------------------+
  | Users  |---->| ROUTER   |---->| OLD SYSTEM       |
  |        |     |          |     | (10% of traffic) |
  +--------+     |          |     +------------------+
                 |          |
                 |          |     +------------------+
                 |          +---->| NEW SYSTEM       |
                 +----------+     | (90% of traffic) |
                                  +------------------+

  Phase 4: Old system decommissioned

  +--------+     +------------------+
  | Users  |---->| NEW SYSTEM       |
  |        |     | (100% of traffic)|
  +--------+     +------------------+
```

### Java Example: Strangler Fig with a Router

```java
// STEP 1: Create a router that delegates to old or new system
public class OrderServiceRouter implements OrderService {

    private final LegacyOrderService legacyService;
    private final NewOrderService newService;
    private final FeatureFlags featureFlags;

    public OrderServiceRouter(LegacyOrderService legacyService,
                              NewOrderService newService,
                              FeatureFlags featureFlags) {
        this.legacyService = legacyService;
        this.newService = newService;
        this.featureFlags = featureFlags;
    }

    @Override
    public Order placeOrder(OrderRequest request) {
        if (featureFlags.isEnabled("new_order_service")) {
            return newService.placeOrder(request);
        }
        return legacyService.placeOrder(request);
    }

    @Override
    public Order getOrder(String orderId) {
        // Maybe migrate one method at a time
        // getOrder uses new system already
        return newService.getOrder(orderId);
    }

    @Override
    public void cancelOrder(String orderId) {
        // cancelOrder still uses legacy
        legacyService.cancelOrder(orderId);
    }
}
```

```python
# STEP 1: Create a router that delegates to old or new system
class OrderServiceRouter:
    def __init__(self, legacy_service, new_service, feature_flags):
        self.legacy_service = legacy_service
        self.new_service = new_service
        self.feature_flags = feature_flags

    def place_order(self, request):
        if self.feature_flags.is_enabled("new_order_service"):
            return self.new_service.place_order(request)
        return self.legacy_service.place_order(request)

    def get_order(self, order_id):
        # Already migrated to new system
        return self.new_service.get_order(order_id)

    def cancel_order(self, order_id):
        # Still on legacy
        self.legacy_service.cancel_order(order_id)
```

---

## Branch by Abstraction

Branch by Abstraction lets you replace an implementation behind an interface without creating long-lived feature branches in version control.

```
BRANCH BY ABSTRACTION:

  Step 1: Code directly uses the legacy implementation

  +----------+     +-------------------+
  | Client   |---->| LegacyPaymentProc |
  | Code     |     | (concrete class)  |
  +----------+     +-------------------+

  Step 2: Insert an interface (abstraction layer)

  +----------+     +----------------+     +-------------------+
  | Client   |---->| PaymentProc    |<----| LegacyPaymentProc |
  | Code     |     | (interface)    |     | (implements)      |
  +----------+     +----------------+     +-------------------+

  Step 3: Build new implementation alongside

  +----------+     +----------------+     +-------------------+
  | Client   |---->| PaymentProc    |<----| LegacyPaymentProc |
  | Code     |     | (interface)    |     +-------------------+
  +----------+     +-------+--------+
                           |              +-------------------+
                           +<-------------| NewPaymentProc    |
                                          | (new, in progress)|
                                          +-------------------+

  Step 4: Switch to new implementation and remove legacy

  +----------+     +----------------+     +-------------------+
  | Client   |---->| PaymentProc    |<----| NewPaymentProc    |
  | Code     |     | (interface)    |     | (complete)        |
  +----------+     +----------------+     +-------------------+

  The client code NEVER changes. Only the wiring in the
  Composition Root changes.
```

### Java Example

```java
// STEP 1: Legacy code is used directly everywhere
// public class OrderService {
//     private final LegacyPaymentProcessor processor = new LegacyPaymentProcessor();
//     ...
// }

// STEP 2: Extract interface
public interface PaymentProcessor {
    PaymentResult processPayment(String customerId, Money amount);
    void refund(String transactionId, Money amount);
}

// STEP 3: Legacy class implements the interface
public class LegacyPaymentProcessor implements PaymentProcessor {
    // Existing code, unchanged
    @Override
    public PaymentResult processPayment(String customerId, Money amount) {
        // All the legacy code stays exactly the same
        // ...
    }

    @Override
    public void refund(String transactionId, Money amount) {
        // ...
    }
}

// STEP 4: Build new implementation
public class StripePaymentProcessor implements PaymentProcessor {
    private final StripeClient stripe;

    public StripePaymentProcessor(StripeClient stripe) {
        this.stripe = stripe;
    }

    @Override
    public PaymentResult processPayment(String customerId, Money amount) {
        // Clean, new implementation
        var charge = stripe.charges().create(
            customerId, amount.toCents(), amount.getCurrency()
        );
        return new PaymentResult(charge.getId(), PaymentStatus.COMPLETED);
    }

    @Override
    public void refund(String transactionId, Money amount) {
        stripe.refunds().create(transactionId, amount.toCents());
    }
}

// STEP 5: Switch in Composition Root
// Before: new OrderService(new LegacyPaymentProcessor())
// After:  new OrderService(new StripePaymentProcessor(stripeClient))
```

```python
# STEP 2: Extract interface (using Protocol in Python)
from typing import Protocol

class PaymentProcessor(Protocol):
    def process_payment(self, customer_id: str, amount: float) -> dict: ...
    def refund(self, transaction_id: str, amount: float) -> None: ...

# STEP 3: Legacy class (unchanged, already matches the protocol)
class LegacyPaymentProcessor:
    def process_payment(self, customer_id, amount):
        # All the legacy code, untouched
        ...

    def refund(self, transaction_id, amount):
        ...

# STEP 4: New implementation
class StripePaymentProcessor:
    def __init__(self, stripe_client):
        self.stripe = stripe_client

    def process_payment(self, customer_id, amount):
        charge = self.stripe.charges.create(
            customer=customer_id, amount=int(amount * 100)
        )
        return {"id": charge.id, "status": "completed"}

    def refund(self, transaction_id, amount):
        self.stripe.refunds.create(charge=transaction_id, amount=int(amount * 100))

# STEP 5: Switch in Composition Root
# Before: order_service = OrderService(LegacyPaymentProcessor())
# After:  order_service = OrderService(StripePaymentProcessor(stripe_client))
```

---

## Sprout Method and Sprout Class

When you need to add new behavior to legacy code, the Sprout technique lets you write new, clean code without modifying the risky legacy code.

### Sprout Method

```java
// LEGACY METHOD: 150 lines of tangled code
// You need to add validation, but touching this method is risky.
public class LegacyOrderProcessor {

    public void processOrder(Order order) {
        // 150 lines of legacy code that you cannot easily test
        // and are afraid to modify
        // ...
    }
}

// SPROUT METHOD: Write new behavior in a new, tested method
public class LegacyOrderProcessor {

    public void processOrder(Order order) {
        // NEW: Call the sprouted method at the right point
        validateOrderForProcessing(order);

        // All the original 150 lines stay untouched
        // ...
    }

    // SPROUTED METHOD: New, clean, fully tested
    // This method was written with TDD -- tests first.
    void validateOrderForProcessing(Order order) {
        if (order.getItems().isEmpty()) {
            throw new EmptyOrderException("Order must have at least one item");
        }
        if (order.getTotal().isNegative()) {
            throw new InvalidOrderException("Order total cannot be negative");
        }
        for (OrderItem item : order.getItems()) {
            if (item.getQuantity() <= 0) {
                throw new InvalidOrderException(
                    "Item quantity must be positive: " + item.getProductId()
                );
            }
        }
    }
}
```

```python
# SPROUT METHOD in Python
class LegacyOrderProcessor:

    def process_order(self, order):
        # NEW: Call the sprouted method
        self._validate_order_for_processing(order)

        # All the original legacy code stays untouched
        # ...

    # SPROUTED METHOD: New, clean, fully tested
    def _validate_order_for_processing(self, order):
        if not order.items:
            raise EmptyOrderError("Order must have at least one item")
        if order.total < 0:
            raise InvalidOrderError("Order total cannot be negative")
        for item in order.items:
            if item.quantity <= 0:
                raise InvalidOrderError(
                    f"Item quantity must be positive: {item.product_id}"
                )
```

### Sprout Class

When the new behavior is complex enough to warrant its own class:

```java
// SPROUT CLASS: Extract new behavior into a separate, clean class
public class OrderFraudDetector {
    private final FraudRuleEngine ruleEngine;
    private final CustomerRiskProfile riskProfile;

    public OrderFraudDetector(FraudRuleEngine ruleEngine,
                              CustomerRiskProfile riskProfile) {
        this.ruleEngine = ruleEngine;
        this.riskProfile = riskProfile;
    }

    public FraudCheckResult checkForFraud(Order order) {
        // Clean, well-tested code
        RiskScore score = riskProfile.scoreFor(order.getCustomerId());
        List<FraudRule> violations = ruleEngine.evaluate(order);

        if (score.isHigh() || violations.size() > 2) {
            return FraudCheckResult.flagged(violations);
        }
        return FraudCheckResult.clear();
    }
}

// Then add ONE line to the legacy code:
public class LegacyOrderProcessor {
    public void processOrder(Order order) {
        // ONE new line -- minimal change to legacy code
        FraudCheckResult fraudCheck = fraudDetector.checkForFraud(order);
        if (fraudCheck.isFlagged()) {
            throw new FraudDetectedException(fraudCheck.getViolations());
        }

        // Original 150 lines unchanged
        // ...
    }
}
```

---

## Making Legacy Code Testable

The biggest obstacle to testing legacy code is dependencies. Legacy classes often create their dependencies internally, making it impossible to substitute test doubles.

### Technique: Extract and Override

```java
// LEGACY: Untestable because it creates its own dependencies
public class InvoiceGenerator {

    public Invoice generate(Order order) {
        // Creates its own connection -- cannot test without a real database
        DatabaseConnection db = new DatabaseConnection("prod-db:5432");
        TaxRate taxRate = db.getTaxRate(order.getState());

        // Creates its own email client -- cannot test without SMTP server
        EmailClient email = new EmailClient("smtp.company.com");

        Invoice invoice = new Invoice(order, taxRate);
        email.send(order.getCustomerEmail(), invoice.toPdf());
        return invoice;
    }
}

// STEP 1: Extract dependency creation into protected methods
public class InvoiceGenerator {

    public Invoice generate(Order order) {
        DatabaseConnection db = createDatabaseConnection();
        TaxRate taxRate = db.getTaxRate(order.getState());

        EmailClient email = createEmailClient();

        Invoice invoice = new Invoice(order, taxRate);
        email.send(order.getCustomerEmail(), invoice.toPdf());
        return invoice;
    }

    // Protected so tests can override
    protected DatabaseConnection createDatabaseConnection() {
        return new DatabaseConnection("prod-db:5432");
    }

    protected EmailClient createEmailClient() {
        return new EmailClient("smtp.company.com");
    }
}

// STEP 2: In tests, override the factory methods
class InvoiceGeneratorTest {

    @Test
    void generates_invoice_with_correct_tax() {
        // Create a testable subclass that returns fakes
        InvoiceGenerator generator = new InvoiceGenerator() {
            @Override
            protected DatabaseConnection createDatabaseConnection() {
                return new FakeDatabaseConnection();
            }
            @Override
            protected EmailClient createEmailClient() {
                return new FakeEmailClient();
            }
        };

        Invoice invoice = generator.generate(testOrder);
        assertEquals(expectedTotal, invoice.getTotal());
    }
}
```

```python
# LEGACY: Untestable
class InvoiceGenerator:
    def generate(self, order):
        db = DatabaseConnection("prod-db:5432")
        tax_rate = db.get_tax_rate(order.state)
        email = EmailClient("smtp.company.com")
        invoice = Invoice(order, tax_rate)
        email.send(order.customer_email, invoice.to_pdf())
        return invoice

# STEP 1: Extract dependency creation
class InvoiceGenerator:
    def generate(self, order):
        db = self._create_db_connection()
        tax_rate = db.get_tax_rate(order.state)
        email = self._create_email_client()
        invoice = Invoice(order, tax_rate)
        email.send(order.customer_email, invoice.to_pdf())
        return invoice

    def _create_db_connection(self):
        return DatabaseConnection("prod-db:5432")

    def _create_email_client(self):
        return EmailClient("smtp.company.com")

# STEP 2: In tests, override or use dependency injection
def test_generates_invoice_with_correct_tax():
    generator = InvoiceGenerator()
    generator._create_db_connection = lambda: FakeDatabaseConnection()
    generator._create_email_client = lambda: FakeEmailClient()

    invoice = generator.generate(test_order)
    assert invoice.total == expected_total
```

---

## When to Rewrite vs When to Refactor

```
REWRITE vs REFACTOR DECISION:

  REFACTOR when:                      REWRITE when:
  +-------------------------------+   +-------------------------------+
  | - Core logic is sound         |   | - Technology is obsolete      |
  | - Architecture is salvageable |   |   (no security updates)       |
  | - Team understands the domain |   | - Architecture fundamentally  |
  | - Business cannot pause for   |   |   wrong (cannot be evolved)   |
  |   a rewrite                   |   | - Codebase is tiny enough     |
  | - Risk tolerance is low       |   |   to rewrite quickly          |
  |                               |   | - Business can tolerate       |
  |                               |   |   parallel development        |
  +-------------------------------+   +-------------------------------+

  THE BIG REWRITE TRAP:

  Plan:     "We'll rewrite from scratch in 6 months!"
  Reality:  +----+----+----+----+----+----+----+----+-->
            Month 1: "Going great!"
            Month 3: "Harder than expected..."
            Month 6: "Not done yet, but old system got
                       6 months of new features we
                       now need to implement too"
            Month 9: "We are trying to hit a moving target"
            Month 12: "Project cancelled. Back to the
                        old system."

  PREFER: Strangler Fig pattern. Replace piece by piece.
          The old system keeps running. The new system
          grows gradually. No big-bang cutover.
```

---

## Common Mistakes

### Mistake 1: Changing Legacy Code Without Tests First

Making changes to code you do not have tests for. When things break, you will not know if the bug is old or new.

**Fix:** Write characterization tests before making any changes. Pin down the current behavior, then modify with confidence.

### Mistake 2: The Big-Bang Rewrite

Stopping all feature development to rewrite the entire system from scratch. This almost always fails because the old system keeps getting new requirements.

**Fix:** Use the Strangler Fig pattern. Replace the system incrementally while both systems run in parallel.

### Mistake 3: Trying to Understand Everything First

Spending weeks reading every line of legacy code before making any changes. You will forget the beginning by the time you reach the end.

**Fix:** Focus on the area you need to change. Write characterization tests for that area. Understand locally, not globally.

### Mistake 4: Refactoring Without a Safety Net

Refactoring legacy code without tests. "I'll just clean this up" leads to subtle behavior changes.

**Fix:** Characterization tests first. Always. No exceptions.

### Mistake 5: Gold-Plating the Legacy Code

Trying to make legacy code perfect. Rewriting entire modules that are stable and working just because they are "ugly."

**Fix:** Only improve code you need to change. If ugly code works and nobody needs to modify it, leave it alone. Focus your energy where it provides value.

---

## Best Practices

1. **Write characterization tests before changing anything.** Document what the code does before modifying it.
2. **Use the Strangler Fig pattern** for system-level replacements. Avoid big-bang rewrites.
3. **Use Branch by Abstraction** for component-level replacements. Insert an interface, build behind it, switch.
4. **Use Sprout Method/Class** for adding new features. Write new code cleanly without touching risky legacy code.
5. **Make the smallest possible change.** Each change should be independently testable and deployable.
6. **Improve code you touch, leave the rest.** The Boy Scout Rule applied to legacy code.
7. **Extract and Override** to break dependencies for testing. Move `new` calls into overridable methods.
8. **Use version control hotspot analysis** to find the most frequently changed files. Those are your highest-value targets for improvement.

---

## Quick Summary

```
WORKING WITH LEGACY CODE AT A GLANCE:

  Technique              When to use it
  +--------------------+------------------------------------+
  | Characterization   | Before ANY change to legacy code.  |
  | Tests              | Pin down current behavior.         |
  +--------------------+------------------------------------+
  | Strangler Fig      | Replacing an entire system         |
  |                    | gradually. No big-bang rewrite.    |
  +--------------------+------------------------------------+
  | Branch by          | Replacing a component. Insert      |
  | Abstraction        | interface, build new, switch.      |
  +--------------------+------------------------------------+
  | Sprout Method/     | Adding new behavior. Write clean   |
  | Sprout Class       | code, call it from legacy code.    |
  +--------------------+------------------------------------+
  | Extract and        | Making legacy code testable by     |
  | Override           | moving dependency creation into    |
  |                    | overridable methods.               |
  +--------------------+------------------------------------+
```

---

## Key Points

- Legacy code is code you are afraid to change, usually because it lacks tests. Age is not the defining factor.
- Characterization tests document what code actually does, not what it should do. Write them before making any changes.
- The Strangler Fig pattern replaces a system gradually: route traffic to the new system piece by piece while the old system continues running.
- Branch by Abstraction lets you replace implementations behind interfaces without long-lived feature branches.
- Sprout Method and Sprout Class let you add new, clean, tested code without modifying risky legacy code.
- Extract and Override breaks hard-coded dependencies by moving `new` calls into overridable factory methods.
- Prefer refactoring over rewriting. Big-bang rewrites almost always fail because the old system is a moving target.
- Only improve code you need to change. Stable, working legacy code that nobody touches does not need to be "cleaned up."

---

## Practice Questions

1. You need to add a new validation rule to a 500-line method that has no tests. Describe the steps you would take, in order, to make this change safely.

2. Your team wants to replace a legacy payment system with a new one. The legacy system processes 10,000 transactions per day. Would you recommend a big-bang rewrite or the Strangler Fig pattern? Why?

3. What is the difference between a characterization test and a unit test? When would you write each?

4. A legacy class creates a `new DatabaseConnection()` inside its constructor, making it impossible to test without a real database. Describe two techniques for making this class testable.

5. A colleague says: "This legacy code is terrible. Let's spend a month cleaning it all up." What are the risks of this approach, and what would you suggest instead?

---

## Exercises

### Exercise 1: Write Characterization Tests

Given this legacy method, write at least six characterization tests that document its current behavior:

```java
public double calculateShipping(double weight, String destination, boolean express) {
    double base = weight * 0.5;
    if (destination.startsWith("US")) {
        base += 5.0;
    } else if (destination.startsWith("EU")) {
        base += 15.0;
    } else {
        base += 25.0;
    }
    if (express) {
        base *= 2;
    }
    if (weight > 50) {
        base += 10;  // heavy surcharge
    }
    return Math.round(base * 100.0) / 100.0;
}
```

### Exercise 2: Apply Sprout Method

You have a legacy `ReportGenerator.generate()` method that produces monthly reports. A new requirement says that reports for amounts over $100,000 must include an "auditor's note" section. Apply the Sprout Method technique: write the new behavior in a separate, tested method and add a single call to it in the legacy method. Write the new method with full test coverage.

### Exercise 3: Plan a Strangler Fig Migration

Your company has a legacy monolith that handles: user authentication, product catalog, ordering, payments, and shipping. Draw a migration plan using the Strangler Fig pattern. Which module would you extract first and why? How would you route traffic between old and new systems? What risks should you mitigate?

---

## What Is Next?

Now that you have the techniques for safely working with legacy code, the next chapter brings everything together in a complete Project Refactoring. You will take a messy, 300-line "god class" and refactor it step by step -- applying every principle from this book -- into clean, well-structured code spread across multiple focused files.
