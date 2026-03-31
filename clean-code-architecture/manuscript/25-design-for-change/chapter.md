# Chapter 25: Design for Change

## What You Will Learn

- How to build software that anticipates and accommodates change without over-engineering
- Abstraction boundaries: where to put the seams in your code
- Configuration over code: externalizing decisions that change frequently
- Feature flags: deploying incomplete features safely
- The Strategy pattern: swapping behavior at runtime
- Event-driven architecture: decoupling producers from consumers
- How to balance flexibility with simplicity (the YAGNI tension)

## Why This Chapter Matters

Here is an uncomfortable truth about software: **the only thing you can predict about requirements is that they will change.** The payment provider will switch. The business rules will evolve. A new regulation will arrive. A feature you built last month will need to work differently next quarter.

The question is not whether change will happen. The question is: when change arrives, will it take you two hours or two weeks?

Code that is designed for change has clear seams -- places where you can swap, extend, or modify behavior without rewriting everything. Code that is not designed for change is brittle: one change causes a cascade of modifications across dozens of files.

But there is a trap. Some developers, fearing future change, add abstraction layers for every possible scenario. They build frameworks instead of features. They add flexibility that nobody ever uses. This is over-engineering, and it is just as harmful as under-engineering.

This chapter teaches you to find the balance: build seams where change is likely, keep things simple where it is not.

---

## Abstraction Boundaries: Where to Put the Seams

An abstraction boundary is a point in your code where you can change the implementation without affecting the rest of the system. The most common tool for creating abstraction boundaries is the interface.

```
ABSTRACTION BOUNDARIES:

  Without boundaries (rigid):

  +------------+     +------------+     +------------+
  | Controller |---->| Service    |---->| MySQL      |
  |            |     |            |     | Repository |
  +------------+     +------------+     +------------+

  Changing MySQL to PostgreSQL requires changing Service.

  With boundaries (flexible):

  +------------+     +------------+     +----------------+
  | Controller |---->| Service    |---->| <<interface>>  |
  |            |     |            |     | Repository     |
  +------------+     +------------+     +-------+--------+
                                                |
                                       +--------+--------+
                                       |                 |
                                  +----+------+    +-----+------+
                                  | MySQL     |    | Postgres   |
                                  | Repository|    | Repository |
                                  +-----------+    +------------+

  Changing MySQL to PostgreSQL requires only:
  1. Writing the new implementation
  2. Changing the wiring in the Composition Root
  Service code does not change at all.
```

### Where to Place Boundaries

Not every dependency needs an abstraction boundary. Place them where change is likely:

```
WHERE TO ADD ABSTRACTION BOUNDARIES:

  HIGH likelihood of change (ADD boundary):
  +------------------------------------------+
  | - Database technology                    |
  | - External APIs (payment, shipping, etc) |
  | - Notification channels (email, SMS)     |
  | - File storage (local, S3, Azure Blob)   |
  | - Business rules that vary by client     |
  | - Authentication providers               |
  +------------------------------------------+

  LOW likelihood of change (SKIP boundary):
  +------------------------------------------+
  | - String utility functions               |
  | - Math calculations                      |
  | - Data structures (lists, maps)          |
  | - Language standard library              |
  | - Internal value objects                 |
  +------------------------------------------+

  Rule of thumb: If you can imagine the implementation
  changing within the next year, add a boundary.
  If not, keep it simple.
```

### Java Example: Strategic Abstraction

```java
// BOUNDARY: Notification channel (likely to change)
// Today it is email. Tomorrow it might be SMS, push, or Slack.
public interface NotificationChannel {
    void send(String recipient, String subject, String body);
}

public class EmailNotification implements NotificationChannel {
    private final SmtpClient smtpClient;

    public EmailNotification(SmtpClient smtpClient) {
        this.smtpClient = smtpClient;
    }

    @Override
    public void send(String recipient, String subject, String body) {
        smtpClient.sendEmail(recipient, subject, body);
    }
}

public class SlackNotification implements NotificationChannel {
    private final SlackWebhook webhook;

    public SlackNotification(SlackWebhook webhook) {
        this.webhook = webhook;
    }

    @Override
    public void send(String recipient, String subject, String body) {
        webhook.postMessage("#" + recipient, subject + "\n" + body);
    }
}

// The service does not care HOW notifications are sent
public class OrderService {
    private final NotificationChannel notifications;

    public OrderService(NotificationChannel notifications) {
        this.notifications = notifications;
    }

    public void placeOrder(Order order) {
        // ... business logic ...
        notifications.send(
            order.getCustomerEmail(),
            "Order Confirmed",
            "Your order " + order.getId() + " has been placed."
        );
    }
}
```

```python
# BOUNDARY: Notification channel (likely to change)
from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, body: str) -> None:
        pass

class EmailNotification(NotificationChannel):
    def __init__(self, smtp_client):
        self.smtp_client = smtp_client

    def send(self, recipient: str, subject: str, body: str) -> None:
        self.smtp_client.send_email(recipient, subject, body)

class SlackNotification(NotificationChannel):
    def __init__(self, webhook):
        self.webhook = webhook

    def send(self, recipient: str, subject: str, body: str) -> None:
        self.webhook.post_message(f"#{recipient}", f"{subject}\n{body}")

# The service does not care HOW notifications are sent
class OrderService:
    def __init__(self, notifications: NotificationChannel):
        self.notifications = notifications

    def place_order(self, order) -> None:
        # ... business logic ...
        self.notifications.send(
            order.customer_email,
            "Order Confirmed",
            f"Your order {order.id} has been placed.",
        )
```

---

## Configuration Over Code

Some decisions change frequently but do not require new logic -- just new values. These belong in configuration, not code.

```
DECISIONS THAT BELONG IN CONFIGURATION:

  +------------------------------------------+
  | - Database connection strings            |
  | - API keys and endpoints                 |
  | - Feature flag states (on/off)           |
  | - Retry counts and timeout values        |
  | - Rate limits                            |
  | - Logging levels                         |
  | - Email templates                        |
  | - Tax rates by region                    |
  | - Currency formatting rules              |
  +------------------------------------------+

  DECISIONS THAT BELONG IN CODE:

  +------------------------------------------+
  | - Business logic and rules               |
  | - Data validation                        |
  | - Algorithms                             |
  | - Error handling strategies              |
  | - Security checks                        |
  +------------------------------------------+
```

### Before and After

```java
// BEFORE: Values hard-coded (bad)
public class RetryPolicy {
    public void executeWithRetry(Runnable action) {
        int maxRetries = 3;           // Hard-coded
        long delayMs = 1000;          // Hard-coded
        for (int i = 0; i <= maxRetries; i++) {
            try {
                action.run();
                return;
            } catch (Exception e) {
                if (i == maxRetries) throw e;
                Thread.sleep(delayMs * (i + 1));  // Hard-coded backoff
            }
        }
    }
}

// AFTER: Values from configuration (good)
public class RetryPolicy {
    private final int maxRetries;
    private final long baseDelayMs;

    public RetryPolicy(RetryConfig config) {
        this.maxRetries = config.getMaxRetries();
        this.baseDelayMs = config.getBaseDelayMs();
    }

    public void executeWithRetry(Runnable action) {
        for (int i = 0; i <= maxRetries; i++) {
            try {
                action.run();
                return;
            } catch (Exception e) {
                if (i == maxRetries) throw e;
                Thread.sleep(baseDelayMs * (i + 1));
            }
        }
    }
}
```

```python
# BEFORE: Values hard-coded (bad)
class RetryPolicy:
    def execute_with_retry(self, action):
        max_retries = 3          # Hard-coded
        base_delay = 1.0         # Hard-coded
        for attempt in range(max_retries + 1):
            try:
                return action()
            except Exception:
                if attempt == max_retries:
                    raise
                time.sleep(base_delay * (attempt + 1))

# AFTER: Values from configuration (good)
class RetryPolicy:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    def execute_with_retry(self, action):
        for attempt in range(self.max_retries + 1):
            try:
                return action()
            except Exception:
                if attempt == self.max_retries:
                    raise
                time.sleep(self.base_delay * (attempt + 1))
```

---

## Feature Flags: Deploy Without Risk

Feature flags let you deploy code that is not yet ready for all users. You can enable features for specific users, gradually roll them out, or instantly disable them if something goes wrong.

```
FEATURE FLAGS FLOW:

  Code is deployed with the feature HIDDEN behind a flag:

  +------------------------------------------+
  |  if feature_flags.is_enabled("new_checkout"):
  |      show_new_checkout()
  |  else:
  |      show_old_checkout()
  +------------------------------------------+

  Flag states:
  +------------+-------------------+---------------------------+
  | State      | Who sees it       | Use case                  |
  +------------+-------------------+---------------------------+
  | OFF        | Nobody            | Not ready yet             |
  | INTERNAL   | Team only         | Internal testing          |
  | BETA       | Opt-in users      | Early feedback            |
  | PERCENTAGE | 10% of users      | Gradual rollout           |
  | ON         | Everyone          | Fully launched            |
  +------------+-------------------+---------------------------+
```

### Java Example

```java
// Simple feature flag implementation
public class FeatureFlags {
    private final Map<String, Boolean> flags;

    public FeatureFlags(Map<String, Boolean> flags) {
        this.flags = flags;
    }

    public boolean isEnabled(String featureName) {
        return flags.getOrDefault(featureName, false);
    }
}

// Usage in service code
public class CheckoutService {
    private final FeatureFlags featureFlags;
    private final OldCheckoutProcess oldProcess;
    private final NewCheckoutProcess newProcess;

    public CheckoutService(FeatureFlags featureFlags,
                           OldCheckoutProcess oldProcess,
                           NewCheckoutProcess newProcess) {
        this.featureFlags = featureFlags;
        this.oldProcess = oldProcess;
        this.newProcess = newProcess;
    }

    public CheckoutResult checkout(Cart cart) {
        if (featureFlags.isEnabled("new_checkout_flow")) {
            return newProcess.execute(cart);
        }
        return oldProcess.execute(cart);
    }
}
```

```python
# Simple feature flag implementation
class FeatureFlags:
    def __init__(self, flags: dict[str, bool]):
        self._flags = flags

    def is_enabled(self, feature_name: str) -> bool:
        return self._flags.get(feature_name, False)

    @classmethod
    def from_config(cls, config_path: str) -> "FeatureFlags":
        import json
        with open(config_path) as f:
            return cls(json.load(f))

# Usage in service code
class CheckoutService:
    def __init__(self, feature_flags: FeatureFlags,
                 old_process: OldCheckoutProcess,
                 new_process: NewCheckoutProcess):
        self.feature_flags = feature_flags
        self.old_process = old_process
        self.new_process = new_process

    def checkout(self, cart) -> CheckoutResult:
        if self.feature_flags.is_enabled("new_checkout_flow"):
            return self.new_process.execute(cart)
        return self.old_process.execute(cart)
```

### Feature Flag Best Practices

1. **Remove flags after full rollout.** Dead flags become technical debt.
2. **Keep flag checks at the boundary** (controllers, services), not deep in business logic.
3. **Test both paths.** Every flag creates two code paths. Test them both.
4. **Use a naming convention.** Prefix flags with the team or feature area.

---

## The Strategy Pattern: Swapping Behavior at Runtime

The Strategy pattern encapsulates an algorithm behind an interface, letting you swap algorithms without changing the code that uses them.

```
STRATEGY PATTERN:

  +------------------+       +-------------------+
  |  PricingService  |------>| <<interface>>     |
  |                  |       | DiscountStrategy  |
  |  applyDiscount() |       +--------+----------+
  +------------------+                |
                              +-------+-------+
                              |       |       |
                         +----+--+ +--+---+ +-+--------+
                         |Percent| |Fixed | |Tiered    |
                         |Discount|Discount|Discount   |
                         +-------+ +------+ +----------+

  The PricingService does not know which discount
  strategy it uses. It just calls strategy.apply(price).
```

### Java Example

```java
// Strategy interface
public interface DiscountStrategy {
    Money apply(Money originalPrice, Customer customer);
}

// Concrete strategies
public class PercentageDiscount implements DiscountStrategy {
    private final double percentage;

    public PercentageDiscount(double percentage) {
        this.percentage = percentage;
    }

    @Override
    public Money apply(Money originalPrice, Customer customer) {
        return originalPrice.multiply(1 - percentage / 100);
    }
}

public class TieredDiscount implements DiscountStrategy {
    @Override
    public Money apply(Money originalPrice, Customer customer) {
        double discount = switch (customer.getLoyaltyTier()) {
            case GOLD     -> 0.15;
            case SILVER   -> 0.10;
            case BRONZE   -> 0.05;
            default       -> 0.0;
        };
        return originalPrice.multiply(1 - discount);
    }
}

public class NoDiscount implements DiscountStrategy {
    @Override
    public Money apply(Money originalPrice, Customer customer) {
        return originalPrice;
    }
}

// The service uses whichever strategy is injected
public class PricingService {
    private final DiscountStrategy discountStrategy;

    public PricingService(DiscountStrategy discountStrategy) {
        this.discountStrategy = discountStrategy;
    }

    public Money calculateFinalPrice(Money basePrice, Customer customer) {
        return discountStrategy.apply(basePrice, customer);
    }
}

// Switching strategies requires only changing the wiring:
// new PricingService(new PercentageDiscount(20))
// new PricingService(new TieredDiscount())
// new PricingService(new NoDiscount())
```

```python
# Strategy using Python's Protocol (duck typing)
from typing import Protocol

class DiscountStrategy(Protocol):
    def apply(self, original_price: float, customer) -> float:
        ...

class PercentageDiscount:
    def __init__(self, percentage: float):
        self.percentage = percentage

    def apply(self, original_price: float, customer) -> float:
        return original_price * (1 - self.percentage / 100)

class TieredDiscount:
    def apply(self, original_price: float, customer) -> float:
        tier_discounts = {
            "gold": 0.15,
            "silver": 0.10,
            "bronze": 0.05,
        }
        discount = tier_discounts.get(customer.loyalty_tier, 0.0)
        return original_price * (1 - discount)

class NoDiscount:
    def apply(self, original_price: float, customer) -> float:
        return original_price

# The service uses whichever strategy is injected
class PricingService:
    def __init__(self, discount_strategy: DiscountStrategy):
        self.discount_strategy = discount_strategy

    def calculate_final_price(self, base_price: float, customer) -> float:
        return self.discount_strategy.apply(base_price, customer)

# Python bonus: you can also use simple functions as strategies
def holiday_discount(original_price: float, customer) -> float:
    return original_price * 0.75

# pricing = PricingService(holiday_discount)  # Functions work too!
```

---

## Event-Driven Architecture: Decoupling Producers from Consumers

Events decouple the code that does something from the code that reacts to it. The producer publishes an event. Zero, one, or many consumers react to it. The producer does not know or care who is listening.

```
DIRECT COUPLING vs EVENT-DRIVEN:

  DIRECT COUPLING (rigid):

  +---------------+     +------------------+
  | OrderService  |---->| InventoryService |
  |               |---->| EmailService     |
  |               |---->| AnalyticsService |
  |               |---->| LoyaltyService   |
  +---------------+     +------------------+

  Adding a new reaction to "order placed" requires
  modifying OrderService. Open/Closed Principle violated.

  EVENT-DRIVEN (flexible):

  +---------------+     +------------+     +------------------+
  | OrderService  |---->| Event Bus  |---->| InventoryHandler |
  |               |     |            |---->| EmailHandler     |
  | publishes:    |     |            |---->| AnalyticsHandler |
  | OrderPlaced   |     |            |---->| LoyaltyHandler   |
  +---------------+     +------------+     +------------------+

  Adding a new reaction means adding a new handler.
  OrderService does not change. Open/Closed Principle upheld.
```

### Java Example

```java
// Simple event system
public interface DomainEvent {
    Instant occurredAt();
}

public record OrderPlacedEvent(
    String orderId,
    String customerId,
    Money total,
    Instant occurredAt
) implements DomainEvent {}

public interface EventHandler<T extends DomainEvent> {
    void handle(T event);
}

public class EventBus {
    private final Map<Class<?>, List<EventHandler<?>>> handlers = new HashMap<>();

    public <T extends DomainEvent> void subscribe(
            Class<T> eventType, EventHandler<T> handler) {
        handlers.computeIfAbsent(eventType, k -> new ArrayList<>()).add(handler);
    }

    @SuppressWarnings("unchecked")
    public void publish(DomainEvent event) {
        List<EventHandler<?>> eventHandlers =
            handlers.getOrDefault(event.getClass(), List.of());
        for (EventHandler handler : eventHandlers) {
            handler.handle(event);
        }
    }
}

// OrderService only publishes -- it does not know who listens
public class OrderService {
    private final OrderRepository repository;
    private final EventBus eventBus;

    public OrderService(OrderRepository repository, EventBus eventBus) {
        this.repository = repository;
        this.eventBus = eventBus;
    }

    public void placeOrder(Order order) {
        order.place();
        repository.save(order);
        eventBus.publish(new OrderPlacedEvent(
            order.getId(), order.getCustomerId(),
            order.getTotal(), Instant.now()
        ));
    }
}

// Handlers are registered separately
public class InventoryReservationHandler implements EventHandler<OrderPlacedEvent> {
    @Override
    public void handle(OrderPlacedEvent event) {
        // Reserve inventory for the order
    }
}

public class OrderConfirmationEmailHandler implements EventHandler<OrderPlacedEvent> {
    @Override
    public void handle(OrderPlacedEvent event) {
        // Send confirmation email
    }
}
```

```python
# Simple event system in Python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable
from collections import defaultdict

@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    customer_id: str
    total: float
    occurred_at: datetime = field(default_factory=datetime.utcnow)

class EventBus:
    def __init__(self):
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)

# OrderService only publishes -- it does not know who listens
class OrderService:
    def __init__(self, repository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    def place_order(self, order) -> None:
        order.place()
        self.repository.save(order)
        self.event_bus.publish(OrderPlacedEvent(
            order_id=order.id,
            customer_id=order.customer_id,
            total=order.total,
        ))

# Handlers are registered separately
def reserve_inventory(event: OrderPlacedEvent) -> None:
    # Reserve inventory for the order
    ...

def send_confirmation_email(event: OrderPlacedEvent) -> None:
    # Send confirmation email
    ...

# Wiring in the Composition Root
event_bus = EventBus()
event_bus.subscribe(OrderPlacedEvent, reserve_inventory)
event_bus.subscribe(OrderPlacedEvent, send_confirmation_email)
```

---

## Balancing Flexibility vs Simplicity

The biggest danger in designing for change is **over-engineering** -- adding flexibility you never use. Here is a framework for deciding:

```
THE FLEXIBILITY DECISION FRAMEWORK:

  Ask yourself these questions:

  1. Has this part of the system changed before?
     YES --> Add an abstraction boundary
     NO  --> Continue to question 2

  2. Is the stakeholder actively discussing changes to this area?
     YES --> Add an abstraction boundary
     NO  --> Continue to question 3

  3. Are there multiple known implementations (e.g., MySQL AND Postgres)?
     YES --> Add an abstraction boundary
     NO  --> Keep it simple. Add the boundary WHEN you need it.

  +---------------------------------------------------+
  |                                                   |
  |  "You Ain't Gonna Need It" (YAGNI) says:          |
  |                                                   |
  |  Do not add flexibility for hypothetical future   |
  |  needs. Add it when you actually need it.          |
  |                                                   |
  |  But ALSO:                                        |
  |                                                   |
  |  Write code that is EASY to add flexibility to    |
  |  later. Small classes, single responsibility,     |
  |  clean interfaces.                                |
  |                                                   |
  +---------------------------------------------------+
```

### The Spectrum of Flexibility

```
TOO RIGID              JUST RIGHT              TOO FLEXIBLE
(hard to change)       (easy to change)        (hard to understand)

+------------------+   +------------------+   +------------------+
| Hard-coded       |   | Interface for    |   | 5 layers of      |
| everything.      |   | things that      |   | abstraction.     |
| One massive      |   | actually change. |   | Plugin system    |
| class.           |   | Config for       |   | for everything.  |
| No interfaces.   |   | values that      |   | XML config for   |
| No config.       |   | vary.            |   | every decision.  |
| No patterns.     |   | Simple patterns  |   | Factory of       |
|                  |   | where needed.    |   | factory of       |
|                  |   |                  |   | abstract factory.|
+------------------+   +------------------+   +------------------+

  "I can't change     "Change is            "I can't understand
   anything without    straightforward        what this code
   breaking things."   and localized."        actually does."
```

### Practical Rules

```java
// OVER-ENGINEERED: Abstract factory for something that never changes
public interface StringFormatterFactory {
    StringFormatter createFormatter(String type);
}
public interface StringFormatter {
    String format(String input);
}
public class UpperCaseFormatterFactory implements StringFormatterFactory { ... }
// This is just: input.toUpperCase()!

// JUST RIGHT: Direct call for stable operations
public String formatName(String name) {
    return name.trim().toUpperCase();
}

// JUST RIGHT: Interface for something that actually varies
public interface TaxCalculator {
    Money calculateTax(Money subtotal, Address address);
}
// Tax rules vary by country, state, and change regularly.
// An interface here is justified.
```

---

## Common Mistakes

### Mistake 1: Abstracting Everything

Creating interfaces for every class, even when there is only one implementation and no foreseeable need for another.

**Fix:** Apply the Rule of Three -- add an abstraction when you have or foresee at least two implementations.

### Mistake 2: Feature Flags That Never Get Removed

Deploying feature flags and forgetting to clean them up. Over time, the code fills with dead branches.

**Fix:** Set an expiration date for every flag. Add a tech debt ticket when the flag is created. Review flags monthly.

### Mistake 3: Configuration for Logic

Putting business logic in configuration files (XML workflows, JSON rule engines) instead of code. Configuration should drive values, not behavior.

**Fix:** Keep business logic in code where it can be tested, debugged, and refactored. Use configuration for values that change without new logic.

### Mistake 4: Events Everywhere

Using events for every method call, even within a single module. This makes the code flow impossible to follow.

**Fix:** Use events for cross-module or cross-context communication. Within a module, direct method calls are clearer.

### Mistake 5: Premature Optimization for Change

Designing for changes that never come. "What if we need to support five databases?" when you only ever use one.

**Fix:** Design for the changes you know about. Make the code clean enough that adding flexibility later is easy.

---

## Best Practices

1. **Place abstraction boundaries at integration points.** Database, external APIs, messaging systems -- these are where change is most likely.
2. **Use configuration for values, code for logic.** Connection strings, retry counts, and feature flags go in config. Business rules go in code.
3. **Remove feature flags promptly.** Set a cleanup deadline when creating any flag.
4. **Use the Strategy pattern when behavior varies.** Pricing rules, tax calculations, and notification channels are natural fits.
5. **Use events for cross-boundary communication.** Events decouple producers from consumers and follow the Open/Closed Principle.
6. **Follow YAGNI, but write clean code.** Do not add flexibility you do not need. But write code that is easy to make flexible later.
7. **Apply the Rule of Three.** If you have done something similar three times, it is time to abstract. Before that, duplication may be cheaper than the wrong abstraction.
8. **Prefer composition over inheritance.** Injecting strategies and collaborators gives you more flexibility than deep class hierarchies.

---

## Quick Summary

```
DESIGN FOR CHANGE AT A GLANCE:

  Tool                   When to use it
  +--------------------+------------------------------------+
  | Abstraction        | At integration points where        |
  | Boundaries         | implementations are likely to      |
  |                    | change (DB, APIs, messaging).      |
  +--------------------+------------------------------------+
  | Configuration      | For values that change without     |
  | Over Code          | new logic (timeouts, URLs, keys).  |
  +--------------------+------------------------------------+
  | Feature Flags      | To deploy incomplete features      |
  |                    | safely and roll out gradually.     |
  +--------------------+------------------------------------+
  | Strategy Pattern   | When algorithm or behavior needs   |
  |                    | to vary (pricing, discounts, tax). |
  +--------------------+------------------------------------+
  | Event-Driven       | For cross-module reactions where   |
  |                    | the producer should not know       |
  |                    | about consumers.                   |
  +--------------------+------------------------------------+

  The golden rule: Make change easy, but do not pay for
  flexibility you do not need yet.
```

---

## Key Points

- Abstraction boundaries (interfaces) create seams where you can swap implementations without changing calling code.
- Place boundaries at integration points where change is most likely: databases, external APIs, notification channels.
- Use configuration for values that change frequently (timeouts, URLs, keys) and code for business logic.
- Feature flags let you deploy incomplete code safely, but remove them promptly after full rollout.
- The Strategy pattern encapsulates varying algorithms behind an interface for easy swapping.
- Event-driven architecture decouples producers from consumers, making it easy to add new reactions without modifying existing code.
- Balance flexibility with simplicity: follow YAGNI, but write clean code that is easy to extend later.
- The Rule of Three helps decide when to abstract: wait for two or three similar cases before generalizing.

---

## Practice Questions

1. You are building a reporting system that currently generates PDF reports. The product team mentions that CSV and Excel exports might be needed in the future. Should you create an abstraction boundary now, or wait? Justify your answer.

2. A developer on your team has created interfaces for every class in the project, even for utility classes like `StringHelper` and `DateFormatter` that have exactly one implementation. What would you tell them?

3. Your application has 47 feature flags. Only 12 are actively being tested. The rest were for features that shipped months ago. What is the problem, and how would you address it?

4. Compare the Strategy pattern with using `if/else` chains for handling different discount types. When would you choose one approach over the other?

5. An event-driven system publishes 200 different event types. Debugging is difficult because you cannot trace the flow of a single operation. What went wrong, and how would you fix it?

---

## Exercises

### Exercise 1: Add an Abstraction Boundary

You have a `UserService` that directly calls `SmtpEmailClient.send()` to send welcome emails. Refactor it to use an abstraction boundary so that the notification method (email, SMS, push notification) can be swapped without changing `UserService`.

### Exercise 2: Implement Feature Flags

Build a simple feature flag system that:
- Loads flag states from a JSON file
- Supports boolean flags (on/off)
- Supports percentage-based rollout (enabled for X% of users based on user ID hash)
- Can be updated at runtime without restarting the application

### Exercise 3: Event-Driven Refactoring

You have an `OrderService.placeOrder()` method that directly calls `inventoryService.reserve()`, `emailService.sendConfirmation()`, `analyticsService.trackPurchase()`, and `loyaltyService.addPoints()`. Refactor this to use an event-driven approach. What are the trade-offs?

---

## What Is Next?

Now that you know how to design code that accommodates change gracefully, the next chapter focuses on API Design Principles -- how to design interfaces that other developers love to use. You will learn about the principle of least surprise, consistent naming, backward compatibility, versioning, and building APIs that are hard to misuse.
