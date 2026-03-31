# Chapter 9: The Open-Closed Principle -- Extend Without Modifying

---

## What You Will Learn

- What the Open-Closed Principle (OCP) means in practical terms
- How to add new behavior to a system without changing existing, tested code
- The Strategy pattern as the primary tool for achieving OCP
- How to refactor if/else chains for different types into polymorphic designs
- How plugin architectures leverage OCP at a larger scale
- How Python's duck typing naturally supports OCP
- When OCP is overkill and you should keep things simple

---

## Why This Chapter Matters

Every time you modify an existing class to add a new feature, you risk breaking something that already works. If a class handles credit card payments and you edit it to also handle PayPal, you might accidentally break the credit card logic. Multiply this across a team of developers all modifying the same files, and you have a recipe for constant regressions.

The Open-Closed Principle eliminates this risk. It teaches you to design your code so that adding a new payment method means creating a new class, not touching any existing class. The existing code stays untouched, tested, and reliable. The new code is isolated and easy to verify.

This is not theoretical. This principle directly determines whether your team can ship new features quickly or gets bogged down fixing regressions every sprint.

---

## The Open-Closed Principle Defined

The Open-Closed Principle was coined by Bertrand Meyer in 1988:

> Software entities (classes, modules, functions) should be **open for extension** but **closed for modification**.

What does this mean?

- **Open for extension**: You can add new behavior. New features, new types, new rules.
- **Closed for modification**: You do not change existing, working code to add that new behavior.

```
+-----------------------------------------------------------+
|           THE OPEN-CLOSED PRINCIPLE                        |
+-----------------------------------------------------------+
|                                                            |
|  CLOSED for modification:                                  |
|  +---------------------------+                             |
|  |  Existing Code            |  <-- Do NOT change this    |
|  |  (tested, working,        |                             |
|  |   deployed, reliable)     |                             |
|  +---------------------------+                             |
|              |                                             |
|              | extends via abstraction                     |
|              v                                             |
|  OPEN for extension:                                       |
|  +---------------------------+                             |
|  |  New Code                 |  <-- ADD this               |
|  |  (new feature, new type,  |                             |
|  |   new behavior)           |                             |
|  +---------------------------+                             |
|                                                            |
|  Existing tests still pass.                                |
|  New feature has its own tests.                            |
|  Nobody touched the old code.                              |
|                                                            |
+-----------------------------------------------------------+
```

---

## The Problem: If/Else Chains That Keep Growing

The most common OCP violation is an if/else chain (or switch statement) that grows every time you add a new type or variant.

### BEFORE: The Payment Type Problem (Java)

```java
// Java -- BAD: Every new payment type requires modifying this class
public class PaymentProcessor {

    public PaymentResult processPayment(Order order, String paymentType) {

        if (paymentType.equals("CREDIT_CARD")) {
            CreditCardGateway gateway = new CreditCardGateway();
            boolean success = gateway.charge(
                order.getCreditCardNumber(),
                order.getAmount()
            );
            if (success) {
                return new PaymentResult(true, "Credit card charged");
            } else {
                return new PaymentResult(false, "Credit card declined");
            }

        } else if (paymentType.equals("PAYPAL")) {
            PayPalClient client = new PayPalClient();
            String token = client.authenticate(order.getPaypalEmail());
            boolean success = client.executePayment(token, order.getAmount());
            if (success) {
                return new PaymentResult(true, "PayPal payment completed");
            } else {
                return new PaymentResult(false, "PayPal payment failed");
            }

        } else if (paymentType.equals("BITCOIN")) {
            BitcoinWallet wallet = new BitcoinWallet();
            String txHash = wallet.sendPayment(
                order.getBitcoinAddress(),
                order.getAmount()
            );
            if (txHash != null) {
                return new PaymentResult(true, "Bitcoin tx: " + txHash);
            } else {
                return new PaymentResult(false, "Bitcoin payment failed");
            }

        } else {
            throw new UnsupportedPaymentException(
                "Unknown payment type: " + paymentType
            );
        }
    }
}
```

What happens when the business asks you to add Apple Pay? You open `PaymentProcessor`, add another `else if` block, and risk breaking the credit card, PayPal, and Bitcoin logic that already works. This class will grow forever.

### BEFORE: The Same Problem in Python

```python
# Python -- BAD: Growing if/elif chain
class PaymentProcessor:

    def process_payment(self, order, payment_type: str) -> dict:

        if payment_type == "credit_card":
            gateway = CreditCardGateway()
            success = gateway.charge(
                order.credit_card_number, order.amount
            )
            return {
                "success": success,
                "message": "Credit card charged" if success
                           else "Credit card declined",
            }

        elif payment_type == "paypal":
            client = PayPalClient()
            token = client.authenticate(order.paypal_email)
            success = client.execute_payment(token, order.amount)
            return {
                "success": success,
                "message": "PayPal completed" if success
                           else "PayPal failed",
            }

        elif payment_type == "bitcoin":
            wallet = BitcoinWallet()
            tx_hash = wallet.send_payment(
                order.bitcoin_address, order.amount
            )
            return {
                "success": tx_hash is not None,
                "message": f"Bitcoin tx: {tx_hash}" if tx_hash
                           else "Bitcoin failed",
            }

        else:
            raise ValueError(f"Unknown payment type: {payment_type}")
```

---

## The Solution: Strategy Pattern Enables OCP

The Strategy pattern extracts each variant into its own class that implements a common interface. The processor delegates to whatever strategy it receives, without knowing the details.

```
+-----------------------------------------------------------+
|           STRATEGY PATTERN FOR OCP                         |
+-----------------------------------------------------------+
|                                                            |
|  +-------------------+                                     |
|  | PaymentProcessor  |    uses     +-------------------+   |
|  |                   |------------>| PaymentStrategy   |   |
|  | process(order,    |             | (interface)       |   |
|  |   strategy)       |             +-------------------+   |
|  +-------------------+             | + pay(order)      |   |
|                                    +-------------------+   |
|                                      ^    ^    ^    ^      |
|                                      |    |    |    |      |
|                    +---------+-------+    |    |    +----+  |
|                    |         |            |    |         |  |
|               +--------+ +--------+ +--------+ +--------+ |
|               |Credit  | |PayPal  | |Bitcoin | |ApplePay| |
|               |Card    | |Strategy| |Strategy| |Strategy| |
|               |Strategy| |        | |        | |        | |
|               +--------+ +--------+ +--------+ +--------+ |
|                                                            |
|  To add Apple Pay:                                         |
|    1. Create ApplePayStrategy (NEW class)                  |
|    2. PaymentProcessor: UNCHANGED                          |
|    3. CreditCardStrategy: UNCHANGED                        |
|    4. PayPalStrategy: UNCHANGED                            |
|    5. BitcoinStrategy: UNCHANGED                           |
|                                                            |
+-----------------------------------------------------------+
```

### AFTER: Strategy Pattern (Java)

```java
// Java -- GOOD: OCP-compliant with Strategy pattern

// Step 1: Define the abstraction
public interface PaymentStrategy {

    PaymentResult pay(Order order);

    String getPaymentType();
}

// Step 2: Implement each strategy
public class CreditCardPayment implements PaymentStrategy {

    private final CreditCardGateway gateway;

    public CreditCardPayment(CreditCardGateway gateway) {
        this.gateway = gateway;
    }

    @Override
    public PaymentResult pay(Order order) {
        boolean success = gateway.charge(
            order.getCreditCardNumber(),
            order.getAmount()
        );
        return new PaymentResult(
            success,
            success ? "Credit card charged" : "Credit card declined"
        );
    }

    @Override
    public String getPaymentType() {
        return "CREDIT_CARD";
    }
}

public class PayPalPayment implements PaymentStrategy {

    private final PayPalClient client;

    public PayPalPayment(PayPalClient client) {
        this.client = client;
    }

    @Override
    public PaymentResult pay(Order order) {
        String token = client.authenticate(order.getPaypalEmail());
        boolean success = client.executePayment(token, order.getAmount());
        return new PaymentResult(
            success,
            success ? "PayPal payment completed" : "PayPal payment failed"
        );
    }

    @Override
    public String getPaymentType() {
        return "PAYPAL";
    }
}

public class BitcoinPayment implements PaymentStrategy {

    private final BitcoinWallet wallet;

    public BitcoinPayment(BitcoinWallet wallet) {
        this.wallet = wallet;
    }

    @Override
    public PaymentResult pay(Order order) {
        String txHash = wallet.sendPayment(
            order.getBitcoinAddress(),
            order.getAmount()
        );
        boolean success = txHash != null;
        return new PaymentResult(
            success,
            success ? "Bitcoin tx: " + txHash : "Bitcoin payment failed"
        );
    }

    @Override
    public String getPaymentType() {
        return "BITCOIN";
    }
}

// Step 3: The processor is now closed for modification
public class PaymentProcessor {

    public PaymentResult processPayment(
            Order order,
            PaymentStrategy strategy) {

        return strategy.pay(order);
    }
}
```

Now adding Apple Pay requires zero changes to existing code:

```java
// Java -- Adding Apple Pay: create a NEW class, change NOTHING else
public class ApplePayPayment implements PaymentStrategy {

    private final ApplePayService service;

    public ApplePayPayment(ApplePayService service) {
        this.service = service;
    }

    @Override
    public PaymentResult pay(Order order) {
        String receipt = service.processPayment(
            order.getApplePayToken(),
            order.getAmount()
        );
        boolean success = receipt != null;
        return new PaymentResult(
            success,
            success ? "Apple Pay receipt: " + receipt
                    : "Apple Pay failed"
        );
    }

    @Override
    public String getPaymentType() {
        return "APPLE_PAY";
    }
}
```

### AFTER: Strategy Pattern (Python)

```python
# Python -- GOOD: OCP-compliant with Strategy pattern
from abc import ABC, abstractmethod


class PaymentStrategy(ABC):
    """Abstraction that all payment methods implement."""

    @abstractmethod
    def pay(self, order: Order) -> PaymentResult:
        pass


class CreditCardPayment(PaymentStrategy):

    def __init__(self, gateway: CreditCardGateway):
        self._gateway = gateway

    def pay(self, order: Order) -> PaymentResult:
        success = self._gateway.charge(
            order.credit_card_number, order.amount
        )
        return PaymentResult(
            success=success,
            message="Credit card charged" if success
                    else "Credit card declined",
        )


class PayPalPayment(PaymentStrategy):

    def __init__(self, client: PayPalClient):
        self._client = client

    def pay(self, order: Order) -> PaymentResult:
        token = self._client.authenticate(order.paypal_email)
        success = self._client.execute_payment(token, order.amount)
        return PaymentResult(
            success=success,
            message="PayPal completed" if success
                    else "PayPal failed",
        )


class BitcoinPayment(PaymentStrategy):

    def __init__(self, wallet: BitcoinWallet):
        self._wallet = wallet

    def pay(self, order: Order) -> PaymentResult:
        tx_hash = self._wallet.send_payment(
            order.bitcoin_address, order.amount
        )
        return PaymentResult(
            success=tx_hash is not None,
            message=f"Bitcoin tx: {tx_hash}" if tx_hash
                    else "Bitcoin failed",
        )


# The processor is closed for modification
class PaymentProcessor:

    def process_payment(
        self,
        order: Order,
        strategy: PaymentStrategy,
    ) -> PaymentResult:
        return strategy.pay(order)
```

Adding Apple Pay in Python:

```python
# Python -- Adding Apple Pay: new class, nothing else changes
class ApplePayPayment(PaymentStrategy):

    def __init__(self, service: ApplePayService):
        self._service = service

    def pay(self, order: Order) -> PaymentResult:
        receipt = self._service.process_payment(
            order.apple_pay_token, order.amount
        )
        return PaymentResult(
            success=receipt is not None,
            message=f"Apple Pay receipt: {receipt}" if receipt
                    else "Apple Pay failed",
        )
```

---

## Polymorphism Over Conditionals

The Strategy pattern is one instance of a broader principle: **prefer polymorphism over conditionals**. Whenever you have an if/else or switch that checks the type of something to decide what to do, consider replacing it with polymorphic dispatch.

```
+-----------------------------------------------------------+
|     CONDITIONALS vs POLYMORPHISM                           |
+-----------------------------------------------------------+
|                                                            |
|  Conditional approach:                                     |
|  if (shape == "circle")     draw circle                    |
|  else if (shape == "rect")  draw rectangle                 |
|  else if (shape == "tri")   draw triangle                  |
|  --> Adding a new shape means finding every if/else        |
|      chain in the entire codebase and updating it.         |
|                                                            |
|  Polymorphic approach:                                     |
|  shape.draw()               // each shape knows how        |
|  --> Adding a new shape means creating one new class.      |
|      Zero other classes change.                            |
|                                                            |
+-----------------------------------------------------------+
```

### Another Example: Discount Calculation

```java
// Java -- BAD: Conditional discount calculation
public double calculateDiscount(Customer customer, double amount) {
    if (customer.getType().equals("REGULAR")) {
        return 0;
    } else if (customer.getType().equals("PREMIUM")) {
        return amount * 0.10;
    } else if (customer.getType().equals("VIP")) {
        return amount * 0.20;
    } else if (customer.getType().equals("EMPLOYEE")) {
        return amount * 0.30;
    }
    return 0;
}

// Java -- GOOD: Polymorphic discount calculation
public interface DiscountPolicy {
    double calculateDiscount(double amount);
}

public class RegularDiscount implements DiscountPolicy {
    public double calculateDiscount(double amount) { return 0; }
}

public class PremiumDiscount implements DiscountPolicy {
    public double calculateDiscount(double amount) {
        return amount * 0.10;
    }
}

public class VipDiscount implements DiscountPolicy {
    public double calculateDiscount(double amount) {
        return amount * 0.20;
    }
}

// Usage: customer carries its own discount policy
double discount = customer.getDiscountPolicy().calculateDiscount(amount);
```

---

## Plugin Architecture: OCP at Scale

The Strategy pattern is OCP applied to a single decision point. A plugin architecture is OCP applied to an entire system. The core application defines extension points, and plugins provide implementations without modifying the core.

```
+-----------------------------------------------------------+
|           PLUGIN ARCHITECTURE                              |
+-----------------------------------------------------------+
|                                                            |
|  +--------------------------------------------------+     |
|  |              CORE APPLICATION                     |     |
|  |                                                   |     |
|  |  +-----------+  +-----------+  +-----------+     |     |
|  |  | Extension |  | Extension |  | Extension |     |     |
|  |  | Point A   |  | Point B   |  | Point C   |     |     |
|  |  +-----------+  +-----------+  +-----------+     |     |
|  |       ^              ^              ^             |     |
|  +-------|--------------|--------------|-------------+     |
|          |              |              |                   |
|     +---------+    +---------+    +---------+              |
|     | Plugin  |    | Plugin  |    | Plugin  |              |
|     | A1      |    | B1      |    | C1      |              |
|     +---------+    +---------+    +---------+              |
|     | Plugin  |    | Plugin  |                             |
|     | A2      |    | B2      |                             |
|     +---------+    +---------+                             |
|                                                            |
|  Core never changes. Plugins are added independently.      |
|                                                            |
+-----------------------------------------------------------+
```

Real-world examples of plugin architectures:

- **IDEs**: VS Code extensions, IntelliJ plugins
- **Build tools**: Maven plugins, Webpack loaders
- **Web frameworks**: Django middleware, Spring Boot starters
- **Browsers**: Chrome extensions, Firefox add-ons

### Registry Pattern for Dynamic Strategy Selection

In real applications, you often need to select a strategy at runtime based on some input. A registry pattern lets you add strategies without modifying the selection logic.

```java
// Java -- Registry pattern for strategy selection
public class PaymentStrategyRegistry {

    private final Map<String, PaymentStrategy> strategies = new HashMap<>();

    public void register(PaymentStrategy strategy) {
        strategies.put(strategy.getPaymentType(), strategy);
    }

    public PaymentStrategy getStrategy(String paymentType) {
        PaymentStrategy strategy = strategies.get(paymentType);
        if (strategy == null) {
            throw new UnsupportedPaymentException(
                "No strategy registered for: " + paymentType
            );
        }
        return strategy;
    }
}

// Configuration: register strategies at startup
PaymentStrategyRegistry registry = new PaymentStrategyRegistry();
registry.register(new CreditCardPayment(new CreditCardGateway()));
registry.register(new PayPalPayment(new PayPalClient()));
registry.register(new BitcoinPayment(new BitcoinWallet()));
// Adding a new payment type: just register it. No code changes.
registry.register(new ApplePayPayment(new ApplePayService()));
```

```python
# Python -- Registry pattern
class PaymentStrategyRegistry:

    def __init__(self):
        self._strategies: dict[str, PaymentStrategy] = {}

    def register(self, payment_type: str, strategy: PaymentStrategy):
        self._strategies[payment_type] = strategy

    def get_strategy(self, payment_type: str) -> PaymentStrategy:
        strategy = self._strategies.get(payment_type)
        if strategy is None:
            raise UnsupportedPaymentError(
                f"No strategy registered for: {payment_type}"
            )
        return strategy


# Configuration at startup
registry = PaymentStrategyRegistry()
registry.register("credit_card", CreditCardPayment(CreditCardGateway()))
registry.register("paypal", PayPalPayment(PayPalClient()))
registry.register("bitcoin", BitcoinPayment(BitcoinWallet()))
registry.register("apple_pay", ApplePayPayment(ApplePayService()))
```

---

## OCP in Python: Duck Typing Helps

Python's duck typing makes OCP even easier. You do not always need a formal abstract base class. If an object has the right methods, it works.

```python
# Python -- Duck typing enables OCP naturally

# No formal interface needed -- just define the method
class EmailNotifier:
    def notify(self, user: User, message: str) -> None:
        send_email(user.email, message)


class SlackNotifier:
    def notify(self, user: User, message: str) -> None:
        post_to_slack(user.slack_id, message)


class SmsNotifier:
    def notify(self, user: User, message: str) -> None:
        send_sms(user.phone, message)


# The service works with anything that has a notify() method
class AlertService:

    def __init__(self, notifiers: list):
        self._notifiers = notifiers

    def send_alert(self, user: User, message: str) -> None:
        for notifier in self._notifiers:
            notifier.notify(user, message)


# Adding a new notifier requires zero changes to AlertService
class TeamsNotifier:
    def notify(self, user: User, message: str) -> None:
        post_to_teams(user.teams_id, message)
```

However, if you want to be explicit about the contract (recommended for larger projects), use Python's `Protocol`:

```python
# Python -- Protocol for explicit duck typing
from typing import Protocol


class Notifier(Protocol):
    def notify(self, user: User, message: str) -> None: ...


class AlertService:

    def __init__(self, notifiers: list[Notifier]):
        self._notifiers = notifiers

    def send_alert(self, user: User, message: str) -> None:
        for notifier in self._notifiers:
            notifier.notify(user, message)
```

---

## When OCP Is Overkill

OCP is powerful, but applying it everywhere leads to over-engineered code. Here are signs that OCP is overkill:

1. **The if/else has only two branches and is unlikely to grow.** If your application will only ever have two user roles (admin and user), a simple if/else is fine.

2. **The variation point is in only one place.** OCP shines when the same type check appears in multiple places. If it only exists in one function, the overhead of an interface and multiple classes may not be worth it.

3. **You are speculating about future requirements.** Do not create extension points for features nobody has asked for. Apply OCP when you see an actual pattern of change, not a hypothetical one.

4. **The code is a short script or prototype.** If the code will live for a few days, formatting it with full OCP compliance is wasted effort.

**The rule of three**: If you have modified the same if/else chain three times to add a new case, it is time to refactor to OCP. Before that, keep it simple.

---

## Common Mistakes

1. **Applying OCP preemptively to everything.** Not every conditional needs a strategy pattern. Apply OCP where you see repeated change.

2. **Modifying the interface when adding a new strategy.** If adding a new payment type requires changing the `PaymentStrategy` interface, you have not achieved OCP.

3. **Forgetting the registry/factory.** The strategies need to be wired together somewhere. Without a registry or factory, the caller still needs to know about all the concrete types.

4. **Using string type checks instead of polymorphism.** If you see `instanceof` checks or string comparisons to decide behavior, you have an OCP violation.

5. **Over-abstracting with too many layers.** One interface with concrete implementations is usually enough. Do not add abstract factory, builder, and decorator on top unless you genuinely need them.

---

## Best Practices

1. **Identify the axis of change.** What is the thing that keeps changing? Payment types? Export formats? Notification channels? That is where to apply OCP.

2. **Define a clean interface for the variation point.** The interface should represent the caller's needs, not the implementation details.

3. **Use the Strategy pattern for single-method behaviors.** If the variation is one operation, Strategy is the right pattern.

4. **Use a registry for runtime strategy selection.** Map type identifiers to strategy instances at configuration time.

5. **Apply the Rule of Three.** Wait until you have seen the pattern repeat before investing in OCP infrastructure.

6. **Keep strategies independent.** Each strategy should be fully self-contained. Strategies should not know about or depend on each other.

---

## Quick Summary

```
+-----------------------------------------------------------+
|              OCP CHEAT SHEET                               |
+-----------------------------------------------------------+
|                                                            |
|  PRINCIPLE:                                                |
|    Open for extension, closed for modification             |
|    Add new behavior by adding new code, not changing       |
|    existing code                                           |
|                                                            |
|  KEY PATTERN:                                              |
|    Strategy pattern: define an interface, implement it      |
|    once per variant, let the processor delegate             |
|                                                            |
|  SIGNS YOU NEED OCP:                                       |
|    - if/else or switch on a type that keeps growing         |
|    - Same type check scattered across multiple classes      |
|    - Adding a new type requires changes to many files       |
|                                                            |
|  SIGNS OCP IS OVERKILL:                                    |
|    - Only 2 branches, unlikely to grow                     |
|    - Type check in only one place                          |
|    - Speculating about future requirements                 |
|                                                            |
+-----------------------------------------------------------+
```

---

## Key Points

- The Open-Closed Principle says code should be open for extension (add new behavior) but closed for modification (do not change existing code)
- If/else chains that check types and grow with each new variant are the classic OCP violation
- The Strategy pattern solves this by defining an interface and creating one implementation per variant
- Polymorphism replaces conditionals: instead of checking what type something is, let each type implement its own behavior
- A registry pattern enables runtime selection of strategies without modifying the selection logic
- Python's duck typing and Protocol make OCP natural without heavy interface hierarchies
- Apply the Rule of Three: wait until an if/else chain has been modified three times before refactoring to OCP

---

## Practice Questions

1. Explain the Open-Closed Principle in your own words. What does "open for extension" mean, and what does "closed for modification" mean?

2. Why is an if/else chain that checks types considered an OCP violation? What specific problems does it cause as the codebase grows?

3. How does the Strategy pattern enable OCP? Draw or describe the relationship between the context class, the strategy interface, and the concrete strategies.

4. What is the Rule of Three, and how does it help you decide when to apply OCP?

5. How does Python's duck typing relate to OCP? Can you achieve OCP in Python without defining an abstract base class?

---

## Exercises

### Exercise 1: Refactor to Strategy Pattern

Refactor the following shipping cost calculator from a conditional chain to a Strategy pattern in both Java and Python:

```java
public double calculateShippingCost(String method, double weight) {
    if (method.equals("STANDARD")) {
        return weight * 1.50;
    } else if (method.equals("EXPRESS")) {
        return weight * 3.00 + 5.00;
    } else if (method.equals("OVERNIGHT")) {
        return weight * 5.00 + 15.00;
    } else if (method.equals("INTERNATIONAL")) {
        return weight * 8.00 + 25.00;
    }
    throw new IllegalArgumentException("Unknown method: " + method);
}
```

### Exercise 2: Build a Plugin Registry

Create a file export system that supports multiple formats (CSV, JSON, XML). Design it so that adding a new format (such as YAML) requires only creating a new class and registering it. Include a registry that maps format names to exporter instances.

### Exercise 3: Identify OCP Violations

Look at a codebase you work with regularly. Find three if/else or switch statements that check a type or category to decide behavior. For each one, assess whether it would benefit from an OCP refactoring or whether it is simple enough to leave as is. Justify your decision.

---

## What Is Next?

The Open-Closed Principle taught you how to extend behavior without modifying existing code. The next chapter covers the Liskov Substitution Principle, which ensures that your extensions actually work correctly. It answers a critical question: when you create a subclass, can it truly replace the parent class everywhere without breaking anything? You will discover why a Square is not always a valid Rectangle, and why a Penguin that throws an exception when asked to fly violates a fundamental design rule.
