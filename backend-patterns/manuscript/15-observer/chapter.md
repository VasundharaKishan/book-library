# Chapter 15: Observer Pattern -- Notify Dependents of State Changes

## What You Will Learn

- How the Observer pattern decouples event producers from event consumers
- Implementing Observer in Java with custom `EventPublisher` and `EventListener`
- Building a Python signal/slot system for loose coupling
- Using Spring's `ApplicationEventPublisher` and `@EventListener` for production systems
- Understanding the differences between Observer and Pub/Sub
- Applying Observer to order events, audit logging, and cache invalidation

## Why This Chapter Matters

Backend systems rarely do just one thing when something happens. When a user places an order, you need to send a confirmation email, update inventory, log the event for analytics, notify the warehouse, and maybe invalidate a cache. If the order service calls all these systems directly, it becomes a tangled mess of dependencies that breaks every time you add a new requirement.

The Observer pattern solves this by letting the order service say "something happened" without knowing or caring who is listening. Each listener independently decides how to react. This is the foundation of event-driven architecture, and understanding it will change how you design backend systems.

---

## The Problem: Direct Coupling Between Services

```java
// OrderService.java (BEFORE -- tightly coupled)
public class OrderService {
    private final EmailService emailService;
    private final InventoryService inventoryService;
    private final AnalyticsService analyticsService;
    private final WarehouseService warehouseService;
    private final CacheService cacheService;

    // Every new requirement = new dependency + new code here
    public Order placeOrder(OrderRequest request) {
        Order order = createOrder(request);

        emailService.sendConfirmation(order);        // Coupling #1
        inventoryService.updateStock(order);          // Coupling #2
        analyticsService.trackPurchase(order);        // Coupling #3
        warehouseService.notifyNewOrder(order);       // Coupling #4
        cacheService.invalidateProductCache(order);   // Coupling #5
        // Next month: loyaltyService.addPoints(order);  // Coupling #6
        // Month after: fraudService.checkOrder(order);  // Coupling #7

        return order;
    }
}
```

```
The Problem Visualized:

              OrderService
             /   |   |   \   \
            /    |   |    \   \
           v     v   v     v   v
        Email Inventory Analytics Warehouse Cache
        Service Service  Service  Service  Service

  OrderService KNOWS about every consumer.
  Adding a new consumer requires modifying OrderService.
  If EmailService is slow, the entire order is slow.
  If AnalyticsService throws, does the order fail?
```

---

## The Solution: Observer Pattern

```
Observer Pattern Structure:

  +-------------------+         +-------------------+
  |    Subject         |         |    Observer        |
  | (Event Publisher)  |  fires  | (Event Listener)   |
  |                    | ------> |                    |
  | + subscribe()      |         | + onEvent(event)   |
  | + unsubscribe()    |         +-------------------+
  | + notify()         |              ^   ^   ^
  +-------------------+              |   |   |
                                     |   |   |
                              Email  Inv  Analytics
                              Lstnr  Lstnr Listener

  The Subject does NOT know what the Observers do.
  Observers register themselves and react independently.
```

---

## Java Implementation: Custom EventPublisher

### Step 1: Define the Event

```java
// OrderEvent.java
public class OrderEvent {
    private final String orderId;
    private final String customerEmail;
    private final double totalAmount;
    private final List<String> items;
    private final LocalDateTime timestamp;

    public OrderEvent(String orderId, String customerEmail,
                      double totalAmount, List<String> items) {
        this.orderId = orderId;
        this.customerEmail = customerEmail;
        this.totalAmount = totalAmount;
        this.items = List.copyOf(items);
        this.timestamp = LocalDateTime.now();
    }

    // Getters
    public String getOrderId() { return orderId; }
    public String getCustomerEmail() { return customerEmail; }
    public double getTotalAmount() { return totalAmount; }
    public List<String> getItems() { return items; }
    public LocalDateTime getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return "OrderEvent{id=" + orderId + ", total=$" + totalAmount + "}";
    }
}
```

### Step 2: Define the Observer Interface

```java
// EventListener.java
public interface EventListener<T> {
    void onEvent(T event);
    String getName();
}
```

### Step 3: Build the EventPublisher (Subject)

```java
// EventPublisher.java
public class EventPublisher<T> {
    private final List<EventListener<T>> listeners = new ArrayList<>();
    private final String topic;

    public EventPublisher(String topic) {
        this.topic = topic;
    }

    public void subscribe(EventListener<T> listener) {
        listeners.add(listener);
        System.out.println("  [" + topic + "] Subscribed: " + listener.getName());
    }

    public void unsubscribe(EventListener<T> listener) {
        listeners.remove(listener);
        System.out.println("  [" + topic + "] Unsubscribed: " + listener.getName());
    }

    public void publish(T event) {
        System.out.println("  [" + topic + "] Publishing to "
            + listeners.size() + " listeners: " + event);
        for (EventListener<T> listener : listeners) {
            try {
                listener.onEvent(event);
            } catch (Exception e) {
                System.err.println("  [" + topic + "] Error in "
                    + listener.getName() + ": " + e.getMessage());
                // One listener failing should NOT stop others
            }
        }
    }
}
```

### Step 4: Implement Concrete Observers

```java
// EmailNotificationListener.java
public class EmailNotificationListener implements EventListener<OrderEvent> {

    @Override
    public void onEvent(OrderEvent event) {
        System.out.println("    [Email] Sending confirmation to "
            + event.getCustomerEmail()
            + " for order " + event.getOrderId());
    }

    @Override
    public String getName() {
        return "EmailNotification";
    }
}

// InventoryUpdateListener.java
public class InventoryUpdateListener implements EventListener<OrderEvent> {

    @Override
    public void onEvent(OrderEvent event) {
        System.out.println("    [Inventory] Reserving "
            + event.getItems().size() + " items for order "
            + event.getOrderId());
    }

    @Override
    public String getName() {
        return "InventoryUpdate";
    }
}

// AuditLogListener.java
public class AuditLogListener implements EventListener<OrderEvent> {

    @Override
    public void onEvent(OrderEvent event) {
        System.out.println("    [Audit] Logged: Order "
            + event.getOrderId() + " - $"
            + event.getTotalAmount() + " at " + event.getTimestamp());
    }

    @Override
    public String getName() {
        return "AuditLog";
    }
}
```

### Step 5: Refactored OrderService

```java
// OrderService.java (AFTER -- Observer Pattern)
public class OrderService {
    private final EventPublisher<OrderEvent> orderPublisher;

    public OrderService(EventPublisher<OrderEvent> orderPublisher) {
        this.orderPublisher = orderPublisher;
    }

    public String placeOrder(String customerEmail, double total,
                             List<String> items) {
        String orderId = "ORD-" + System.currentTimeMillis();
        System.out.println("\nPlacing order: " + orderId);

        // Business logic here...

        // Notify all listeners -- OrderService does NOT know who they are
        OrderEvent event = new OrderEvent(orderId, customerEmail, total, items);
        orderPublisher.publish(event);

        return orderId;
    }
}
```

### Step 6: Wire It Together

```java
// Main.java
public class Main {
    public static void main(String[] args) {
        // Create the publisher
        EventPublisher<OrderEvent> publisher = new EventPublisher<>("orders");

        // Register listeners -- each is independent
        publisher.subscribe(new EmailNotificationListener());
        publisher.subscribe(new InventoryUpdateListener());
        publisher.subscribe(new AuditLogListener());

        // Create the service
        OrderService orderService = new OrderService(publisher);

        // Place an order
        orderService.placeOrder(
            "alice@example.com", 149.99,
            List.of("Laptop Stand", "USB-C Hub")
        );

        // Add a NEW listener without changing OrderService
        publisher.subscribe(new EventListener<OrderEvent>() {
            @Override
            public void onEvent(OrderEvent event) {
                System.out.println("    [Analytics] Tracked purchase: $"
                    + event.getTotalAmount());
            }
            @Override
            public String getName() { return "Analytics"; }
        });

        // Next order goes to ALL listeners including Analytics
        orderService.placeOrder(
            "bob@example.com", 299.99,
            List.of("Mechanical Keyboard")
        );
    }
}
```

**Output:**
```
  [orders] Subscribed: EmailNotification
  [orders] Subscribed: InventoryUpdate
  [orders] Subscribed: AuditLog

Placing order: ORD-1700000001
  [orders] Publishing to 3 listeners: OrderEvent{id=ORD-1700000001, total=$149.99}
    [Email] Sending confirmation to alice@example.com for order ORD-1700000001
    [Inventory] Reserving 2 items for order ORD-1700000001
    [Audit] Logged: Order ORD-1700000001 - $149.99 at 2024-11-15T10:30:00

  [orders] Subscribed: Analytics

Placing order: ORD-1700000002
  [orders] Publishing to 4 listeners: OrderEvent{id=ORD-1700000002, total=$299.99}
    [Email] Sending confirmation to bob@example.com for order ORD-1700000002
    [Inventory] Reserving 1 items for order ORD-1700000002
    [Audit] Logged: Order ORD-1700000002 - $299.99 at 2024-11-15T10:30:01
    [Analytics] Tracked purchase: $299.99
```

---

## Before vs After

```
BEFORE:                              AFTER:
+-------------------+                +-------------------+
| OrderService      |                | OrderService      |
|                   |                |                   |
| - emailService    |                | - publisher       |
| - inventoryService|                |   (EventPublisher)|
| - analyticsService|                |                   |
| - warehouseService|                | placeOrder() {    |
| - cacheService    |                |   publisher       |
|                   |                |     .publish(evt) |
| placeOrder() {    |                | }                 |
|   email.send()    |                +-------------------+
|   inventory.update|                         |
|   analytics.track |                    publishes to
|   warehouse.notify|                         |
|   cache.invalidate|                +--------+--------+
| }                 |                |        |        |
+-------------------+                v        v        v
                                  Email    Inv.    Audit
  5 dependencies                  Lstnr    Lstnr   Lstnr
  Change = modify OrderService
                                  0 dependencies in OrderService
                                  Change = add/remove a listener
```

---

## Python Implementation: Signal/Slot System

```python
# signal_slot.py
from typing import Callable, Any
from dataclasses import dataclass, field
from datetime import datetime


class Signal:
    """A signal that can be connected to multiple slots (callbacks)."""

    def __init__(self, name: str):
        self.name = name
        self._slots: list[Callable] = []

    def connect(self, slot: Callable) -> None:
        """Connect a slot (callback) to this signal."""
        self._slots.append(slot)
        print(f"  [{self.name}] Connected: {slot.__name__}")

    def disconnect(self, slot: Callable) -> None:
        """Disconnect a slot from this signal."""
        self._slots.remove(slot)
        print(f"  [{self.name}] Disconnected: {slot.__name__}")

    def emit(self, *args, **kwargs) -> None:
        """Emit the signal, calling all connected slots."""
        print(f"  [{self.name}] Emitting to {len(self._slots)} slots")
        for slot in self._slots:
            try:
                slot(*args, **kwargs)
            except Exception as e:
                print(f"  [{self.name}] Error in {slot.__name__}: {e}")


@dataclass
class OrderEvent:
    order_id: str
    customer: str
    total: float
    items: list[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class OrderService:
    """Service that emits signals instead of calling listeners directly."""

    def __init__(self):
        self.order_placed = Signal("order_placed")
        self.order_cancelled = Signal("order_cancelled")

    def place_order(self, customer: str, total: float, items: list[str]) -> str:
        order_id = f"ORD-{id(self) % 10000:04d}"
        event = OrderEvent(order_id, customer, total, items)
        print(f"\nPlacing order: {order_id}")
        self.order_placed.emit(event)
        return order_id

    def cancel_order(self, order_id: str, reason: str) -> None:
        print(f"\nCancelling order: {order_id}")
        self.order_cancelled.emit(order_id, reason)


# --- Slot functions (listeners) ---

def send_confirmation_email(event: OrderEvent) -> None:
    print(f"    [Email] Confirmation sent to {event.customer}")

def update_inventory(event: OrderEvent) -> None:
    print(f"    [Inventory] Reserved {len(event.items)} items")

def log_audit_trail(event: OrderEvent) -> None:
    print(f"    [Audit] Order {event.order_id}: ${event.total:.2f}")

def handle_cancellation(order_id: str, reason: str) -> None:
    print(f"    [Cancel] Processing refund for {order_id}: {reason}")

def notify_warehouse_cancel(order_id: str, reason: str) -> None:
    print(f"    [Warehouse] Stopping fulfillment for {order_id}")


# --- Usage ---
if __name__ == "__main__":
    service = OrderService()

    # Connect slots to signals
    service.order_placed.connect(send_confirmation_email)
    service.order_placed.connect(update_inventory)
    service.order_placed.connect(log_audit_trail)

    service.order_cancelled.connect(handle_cancellation)
    service.order_cancelled.connect(notify_warehouse_cancel)

    # Place an order
    service.place_order("alice@example.com", 149.99, ["Laptop Stand", "USB Hub"])

    # Cancel it
    service.cancel_order("ORD-0001", "Customer changed mind")
```

**Output:**
```
  [order_placed] Connected: send_confirmation_email
  [order_placed] Connected: update_inventory
  [order_placed] Connected: log_audit_trail
  [order_cancelled] Connected: handle_cancellation
  [order_cancelled] Connected: notify_warehouse_cancel

Placing order: ORD-4821
  [order_placed] Emitting to 3 slots
    [Email] Confirmation sent to alice@example.com
    [Inventory] Reserved 2 items
    [Audit] Order ORD-4821: $149.99

Cancelling order: ORD-0001
  [order_cancelled] Emitting to 2 slots
    [Cancel] Processing refund for ORD-0001: Customer changed mind
    [Warehouse] Stopping fulfillment for ORD-0001
```

---

## Spring Boot: ApplicationEventPublisher and @EventListener

Spring has the Observer pattern built into the framework.

### Step 1: Define Domain Events

```java
// OrderPlacedEvent.java
public class OrderPlacedEvent {
    private final String orderId;
    private final String customerEmail;
    private final double total;
    private final List<String> items;
    private final Instant timestamp;

    public OrderPlacedEvent(String orderId, String customerEmail,
                            double total, List<String> items) {
        this.orderId = orderId;
        this.customerEmail = customerEmail;
        this.total = total;
        this.items = items;
        this.timestamp = Instant.now();
    }

    // Getters...
    public String getOrderId() { return orderId; }
    public String getCustomerEmail() { return customerEmail; }
    public double getTotal() { return total; }
    public List<String> getItems() { return items; }
    public Instant getTimestamp() { return timestamp; }
}

// OrderCancelledEvent.java
public class OrderCancelledEvent {
    private final String orderId;
    private final String reason;
    private final Instant timestamp;

    public OrderCancelledEvent(String orderId, String reason) {
        this.orderId = orderId;
        this.reason = reason;
        this.timestamp = Instant.now();
    }

    public String getOrderId() { return orderId; }
    public String getReason() { return reason; }
    public Instant getTimestamp() { return timestamp; }
}
```

### Step 2: Publish Events from the Service

```java
// OrderService.java
@Service
public class OrderService {

    private final ApplicationEventPublisher eventPublisher;

    public OrderService(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    @Transactional
    public String placeOrder(String email, double total, List<String> items) {
        String orderId = "ORD-" + UUID.randomUUID().toString().substring(0, 8);

        // Save order to database...

        // Publish event -- Spring delivers it to all @EventListener methods
        eventPublisher.publishEvent(
            new OrderPlacedEvent(orderId, email, total, items)
        );

        return orderId;
    }

    @Transactional
    public void cancelOrder(String orderId, String reason) {
        // Update order status in database...

        eventPublisher.publishEvent(
            new OrderCancelledEvent(orderId, reason)
        );
    }
}
```

### Step 3: Listen for Events with @EventListener

```java
// EmailEventListener.java
@Component
public class EmailEventListener {

    @EventListener
    public void handleOrderPlaced(OrderPlacedEvent event) {
        System.out.println("[Email] Sending confirmation to "
            + event.getCustomerEmail()
            + " for order " + event.getOrderId());
        // emailService.sendOrderConfirmation(event);
    }

    @EventListener
    public void handleOrderCancelled(OrderCancelledEvent event) {
        System.out.println("[Email] Sending cancellation notice for "
            + event.getOrderId());
    }
}

// InventoryEventListener.java
@Component
public class InventoryEventListener {

    @EventListener
    public void handleOrderPlaced(OrderPlacedEvent event) {
        System.out.println("[Inventory] Reserving "
            + event.getItems().size() + " items");
        // inventoryRepository.reserveItems(event.getItems());
    }

    @EventListener
    public void handleOrderCancelled(OrderCancelledEvent event) {
        System.out.println("[Inventory] Releasing stock for "
            + event.getOrderId());
    }
}

// AuditEventListener.java
@Component
public class AuditEventListener {

    @EventListener
    public void handleOrderPlaced(OrderPlacedEvent event) {
        System.out.println("[Audit] Order placed: " + event.getOrderId()
            + " at " + event.getTimestamp());
    }

    @EventListener
    public void handleOrderCancelled(OrderCancelledEvent event) {
        System.out.println("[Audit] Order cancelled: " + event.getOrderId()
            + " reason: " + event.getReason());
    }
}

// Async listener for non-critical work
@Component
public class AnalyticsEventListener {

    @Async
    @EventListener
    public void handleOrderPlaced(OrderPlacedEvent event) {
        System.out.println("[Analytics] Tracking purchase: $" + event.getTotal());
        // analyticsClient.trackEvent("purchase", event);
    }
}
```

```
Spring Event Flow:

  OrderService
      |
      | publishEvent(OrderPlacedEvent)
      v
  ApplicationEventPublisher (Spring)
      |
      | Spring finds all @EventListener methods
      | that accept OrderPlacedEvent
      |
      +---> EmailEventListener.handleOrderPlaced()
      |         (synchronous -- runs in same thread)
      |
      +---> InventoryEventListener.handleOrderPlaced()
      |         (synchronous)
      |
      +---> AuditEventListener.handleOrderPlaced()
      |         (synchronous)
      |
      +---> AnalyticsEventListener.handleOrderPlaced()
                (@Async -- runs in separate thread)
```

---

## Real-World Use Case: Cache Invalidation

```java
// CacheInvalidationListener.java
@Component
public class CacheInvalidationListener {

    private final CacheManager cacheManager;

    public CacheInvalidationListener(CacheManager cacheManager) {
        this.cacheManager = cacheManager;
    }

    @EventListener
    public void onProductUpdated(ProductUpdatedEvent event) {
        Cache productCache = cacheManager.getCache("products");
        if (productCache != null) {
            productCache.evict(event.getProductId());
            System.out.println("[Cache] Evicted product: " + event.getProductId());
        }
    }

    @EventListener
    public void onOrderPlaced(OrderPlacedEvent event) {
        // Inventory changed, invalidate related caches
        Cache inventoryCache = cacheManager.getCache("inventory");
        if (inventoryCache != null) {
            for (String itemId : event.getItems()) {
                inventoryCache.evict(itemId);
            }
            System.out.println("[Cache] Evicted " + event.getItems().size()
                + " inventory entries");
        }
    }
}
```

---

## Observer vs Pub/Sub

These two patterns are related but differ in important ways.

```
Observer Pattern:
+----------+    direct reference    +----------+
| Subject  | ---------------------> | Observer |
| (knows   |    calls onEvent()     | (known   |
|  its     |                        |  to the  |
| observers|                        |  subject)|
+----------+                        +----------+

  - Subject holds references to observers
  - Tight coupling (same process, same JVM)
  - Synchronous by default
  - Subject knows observer interface


Pub/Sub Pattern:
+----------+                        +----------+
|Publisher  |   message    +------+  |Subscriber|
|(does NOT  | -----------> |Broker|->|(does NOT |
| know      |              |/Bus  |  | know     |
| subscribers)             +------+  | publisher)
+----------+                         +----------+

  - Publisher and subscriber do NOT know each other
  - Fully decoupled (can be different processes/machines)
  - Asynchronous (message broker handles delivery)
  - Communication via topics/channels
```

### Comparison Table

| Feature | Observer | Pub/Sub |
|---|---|---|
| Coupling | Subject knows observers | Fully decoupled via broker |
| Location | Same process | Can cross processes/networks |
| Delivery | Synchronous (usually) | Asynchronous (usually) |
| Reliability | No guarantees | Broker can guarantee delivery |
| Complexity | Simple | Needs infrastructure (Kafka, RabbitMQ) |
| Use when | In-process events | Cross-service events |

### Spring Bridges Both

```java
// In-process Observer (same JVM)
eventPublisher.publishEvent(new OrderPlacedEvent(...));

// Pub/Sub (cross-service, using Spring Cloud Stream + Kafka)
streamBridge.send("orders-out", new OrderPlacedEvent(...));
```

---

## When to Use / When NOT to Use

### Use Observer When

| Scenario | Why Observer Helps |
|---|---|
| Multiple reactions to one event | Each listener handles its own concern |
| Adding reactions without modifying the source | Open/Closed Principle in action |
| In-process event notification | Simple, no infrastructure needed |
| Audit logging and tracking | Listeners observe without affecting flow |
| Cache invalidation on data change | Automatic, decoupled cache management |

### Do NOT Use Observer When

| Scenario | Why Not |
|---|---|
| Cross-service communication | Use Pub/Sub with a message broker |
| Order of execution matters | Observer does not guarantee order |
| Listeners need to modify the event | Events should be immutable |
| Only one listener will ever exist | Direct method call is simpler |
| Performance-critical hot path | Observer adds overhead per listener |

---

## Common Mistakes

### Mistake 1: One Listener Failure Breaks Everything

```java
// BAD -- No error handling
public void publish(T event) {
    for (EventListener<T> listener : listeners) {
        listener.onEvent(event);  // If this throws, remaining listeners are skipped
    }
}

// GOOD -- Isolate listener failures
public void publish(T event) {
    for (EventListener<T> listener : listeners) {
        try {
            listener.onEvent(event);
        } catch (Exception e) {
            log.error("Listener {} failed: {}", listener.getName(), e.getMessage());
        }
    }
}
```

### Mistake 2: Modifying Listener List During Notification

```java
// BAD -- ConcurrentModificationException
public void publish(T event) {
    for (EventListener<T> listener : listeners) {
        listener.onEvent(event);  // What if onEvent() calls subscribe()?
    }
}

// GOOD -- Iterate over a copy
public void publish(T event) {
    List<EventListener<T>> snapshot = new ArrayList<>(listeners);
    for (EventListener<T> listener : snapshot) {
        listener.onEvent(event);
    }
}
```

### Mistake 3: Memory Leaks from Forgotten Subscriptions

```java
// BAD -- Listener never unsubscribed, holds reference forever
publisher.subscribe(new HeavyResourceListener());
// The publisher now holds a reference, preventing garbage collection

// GOOD -- Use weak references or explicit lifecycle management
public void shutdown() {
    publisher.unsubscribe(this);
}
```

---

## Best Practices

1. **Make events immutable.** Once published, an event should not change. Use `final` fields and `List.copyOf()`.

2. **Handle listener exceptions.** One failing listener must not prevent other listeners from receiving the event.

3. **Use `@Async` for slow listeners.** Email sending should not slow down order placement.

4. **Name events in past tense.** `OrderPlacedEvent`, not `PlaceOrderEvent`. Events describe something that already happened.

5. **Keep events focused.** An event should carry only the data its listeners need. Do not dump the entire domain model into an event.

6. **Unsubscribe when done.** Especially in long-running applications, forgotten subscriptions cause memory leaks.

7. **Log event publishing.** When debugging, knowing which events fired and which listeners ran is invaluable.

---

## Quick Summary

```
+---------------------------------------------------------------+
|                   OBSERVER PATTERN SUMMARY                     |
+---------------------------------------------------------------+
| Intent:     Define a one-to-many dependency so that when one   |
|             object changes state, all dependents are notified. |
+---------------------------------------------------------------+
| Problem:    Source must call N services directly                |
| Solution:   Source publishes events, listeners react           |
+---------------------------------------------------------------+
| Key parts:                                                     |
|   - Subject / Publisher (fires events)                         |
|   - Observer / Listener (reacts to events)                     |
|   - Event object (carries data)                                |
+---------------------------------------------------------------+
| Spring:     ApplicationEventPublisher + @EventListener         |
| Python:     Signal/slot pattern or callback lists              |
+---------------------------------------------------------------+
```

---

## Key Points

- Observer decouples the event source from the event consumers.
- The publisher does not know what listeners do or how many exist.
- Adding a new reaction means adding a new listener, not modifying the publisher.
- Spring's `@EventListener` makes Observer nearly invisible -- just annotate a method.
- Use `@Async` for listeners that do slow work like sending emails or calling APIs.
- Observer is in-process; Pub/Sub extends the concept across services using a message broker.
- Always handle exceptions in listeners to prevent cascading failures.

---

## Practice Questions

1. In the Spring example, what happens if `InventoryEventListener` throws an exception? Does the email still get sent? How would you change this behavior?

2. Why should events be immutable? What could go wrong if a listener modifies the event object before the next listener receives it?

3. You need to guarantee that the email confirmation is sent after the inventory is reserved. Can Observer guarantee this ordering? What alternatives exist?

4. How does `@Async` on an `@EventListener` change the transactional behavior? If the order transaction rolls back, does the async listener still run?

5. When would you choose Pub/Sub over Observer? Give two specific backend scenarios where Observer is insufficient.

---

## Exercises

### Exercise 1: User Registration Events

Build a user registration system where `UserService.register()` publishes a `UserRegisteredEvent`. Create three listeners: one sends a welcome email, one creates a default profile, and one logs the registration for analytics. Verify that adding a fourth listener (free trial activation) requires zero changes to `UserService`.

### Exercise 2: Stock Price Monitor

Create a `StockTicker` that publishes price updates. Implement observers for `PriceAlertObserver` (triggers when price crosses a threshold), `MovingAverageObserver` (calculates running average), and `DashboardObserver` (prints current price). Allow observers to subscribe and unsubscribe dynamically.

### Exercise 3: Event Replay System

Extend the Observer pattern to store all published events in a list. Add a `replay()` method that re-publishes all stored events to any newly subscribed listener. This is how event sourcing systems allow new services to "catch up" on history.

---

## What Is Next?

Observer lets you broadcast events to multiple listeners. But what if you need to treat a request itself as an object -- something you can queue, undo, log, or replay? In the next chapter, we explore the **Command pattern**, which wraps requests into objects, enabling undo/redo operations, task queues, and transaction logging.
