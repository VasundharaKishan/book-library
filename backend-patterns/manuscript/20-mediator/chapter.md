# Chapter 20: Mediator Pattern -- Reduce Many-to-Many Complexity

## What You Will Learn

- What the Mediator pattern is and why direct dependencies create chaos
- The air traffic controller analogy that makes Mediator intuitive
- How to implement a chat room mediator in Java
- How to build an event-driven service mediator in Python
- The difference between Mediator and Observer
- When centralized coordination helps and when it becomes a bottleneck

## Why This Chapter Matters

As systems grow, components start talking to each other directly. Service A calls
Service B, which notifies Service C, which updates Service A. Before long, every
component depends on every other component. Adding a new component means modifying
ten existing ones. Removing one breaks five others.

The Mediator pattern breaks this web of dependencies by introducing a central
coordinator. Instead of components talking to each other, they talk to the mediator.
The mediator knows the rules and routes messages accordingly. Components become
independent and reusable.

---

## The Problem

You are building a trading platform. The order system needs to communicate with:
- The inventory service (check stock)
- The payment service (charge the customer)
- The notification service (send confirmation)
- The analytics service (track the sale)
- The shipping service (create shipment)

Without a mediator, every service has direct references to the others:

```
WITHOUT MEDIATOR: Every service knows about every other service

    +----------+     +----------+     +---------+
    |  Order   |<--->| Inventory|<--->| Payment |
    +----------+     +----------+     +---------+
        ^   ^             ^               ^
        |   |             |               |
        |   +--------+    |    +----------+
        |            |    |    |
    +----------+  +----------+  +---------+
    | Shipping |  | Notify   |  |Analytics|
    +----------+  +----------+  +---------+

    15 direct connections between 6 services.
    Adding service #7 requires modifying all 6 existing services.
```

Each service has 5 dependencies. Adding a seventh service means updating 6 existing
services. This is the **many-to-many** problem.

---

## The Solution: Mediator Pattern

```
WITH MEDIATOR: Every service only knows the mediator

    +----------+     +----------+     +---------+
    |  Order   |     | Inventory|     | Payment |
    +----------+     +----------+     +---------+
         \               |               /
          \              |              /
           v             v             v
         +----------------------------+
         |         MEDIATOR            |
         |   (coordinates all          |
         |    communication)           |
         +----------------------------+
           ^             ^             ^
          /              |              \
         /               |               \
    +----------+  +----------+  +---------+
    | Shipping |  | Notify   |  |Analytics|
    +----------+  +----------+  +---------+

    6 connections (one per service to mediator).
    Adding service #7 means updating ONLY the mediator.
```

**Key participants:**

- **Mediator**: defines the interface for communication between components
- **ConcreteMediator**: implements the coordination logic
- **Colleague**: each component that communicates through the mediator

---

## The Air Traffic Controller Analogy

An airport without a control tower would be chaos. Every pilot would need to
communicate with every other pilot to avoid collisions.

```
WITHOUT TOWER (Direct Communication)
Plane A <---> Plane B
Plane A <---> Plane C
Plane B <---> Plane C
Plane A <---> Plane D
...
10 planes = 45 direct communication channels

WITH TOWER (Mediator)
Plane A ---> Tower ---> Plane B
Plane C ---> Tower ---> Plane A
10 planes = 10 communication channels (each to tower)
```

The tower (mediator) knows all the rules:
- Only one plane lands at a time
- Planes queue in order of fuel level
- Emergency landings preempt everything

No plane needs to know these rules. They just report their status to the tower and
follow instructions. The tower coordinates.

---

## Java Implementation: Chat Room

### The Mediator Interface and Colleagues

```java
import java.util.List;

public interface ChatMediator {
    void sendMessage(String message, User sender);
    void sendPrivateMessage(String message, User sender, String recipientName);
    void addUser(User user);
    void removeUser(User user);
    List<String> getOnlineUsers();
}
```

```java
public class User {
    private final String name;
    private ChatMediator mediator;
    private final List<String> messageLog;

    public User(String name) {
        this.name = name;
        this.messageLog = new java.util.ArrayList<>();
    }

    public void setMediator(ChatMediator mediator) {
        this.mediator = mediator;
    }

    public void send(String message) {
        System.out.printf("[%s] sends: %s%n", name, message);
        mediator.sendMessage(message, this);
    }

    public void sendPrivate(String message, String recipientName) {
        System.out.printf("[%s] whispers to %s: %s%n",
                name, recipientName, message);
        mediator.sendPrivateMessage(message, this, recipientName);
    }

    public void receive(String message, String senderName) {
        String formatted = String.format("  [%s] received from %s: %s",
                name, senderName, message);
        messageLog.add(formatted);
        System.out.println(formatted);
    }

    public String getName() { return name; }

    public List<String> getMessageLog() {
        return java.util.Collections.unmodifiableList(messageLog);
    }
}
```

### The Concrete Mediator

```java
import java.util.*;

public class ChatRoom implements ChatMediator {
    private final String roomName;
    private final List<User> users;
    private final List<String> bannedWords;

    public ChatRoom(String roomName) {
        this.roomName = roomName;
        this.users = new ArrayList<>();
        this.bannedWords = Arrays.asList("spam", "scam");
    }

    @Override
    public void addUser(User user) {
        users.add(user);
        user.setMediator(this);
        System.out.printf(">>> %s joined '%s' (online: %d)%n",
                user.getName(), roomName, users.size());

        // Notify others
        for (User u : users) {
            if (u != user) {
                u.receive(user.getName() + " has joined the chat",
                         "System");
            }
        }
    }

    @Override
    public void removeUser(User user) {
        users.remove(user);
        System.out.printf(">>> %s left '%s' (online: %d)%n",
                user.getName(), roomName, users.size());

        for (User u : users) {
            u.receive(user.getName() + " has left the chat", "System");
        }
    }

    @Override
    public void sendMessage(String message, User sender) {
        // Mediator applies rules: filter banned words
        if (containsBannedWord(message)) {
            sender.receive("Your message was blocked (policy violation)",
                          "System");
            return;
        }

        // Broadcast to all EXCEPT sender
        for (User user : users) {
            if (user != sender) {
                user.receive(message, sender.getName());
            }
        }
    }

    @Override
    public void sendPrivateMessage(String message, User sender,
                                    String recipientName) {
        for (User user : users) {
            if (user.getName().equals(recipientName)) {
                user.receive("[PRIVATE] " + message, sender.getName());
                return;
            }
        }
        sender.receive("User '" + recipientName + "' not found", "System");
    }

    @Override
    public List<String> getOnlineUsers() {
        List<String> names = new ArrayList<>();
        for (User u : users) {
            names.add(u.getName());
        }
        return names;
    }

    private boolean containsBannedWord(String message) {
        String lower = message.toLowerCase();
        return bannedWords.stream().anyMatch(lower::contains);
    }
}
```

### Demo

```java
public class ChatDemo {
    public static void main(String[] args) {
        ChatRoom room = new ChatRoom("Backend Developers");

        User alice = new User("Alice");
        User bob = new User("Bob");
        User charlie = new User("Charlie");

        // Users join through the mediator
        room.addUser(alice);
        room.addUser(bob);
        room.addUser(charlie);

        System.out.println("\n--- Messaging ---");
        alice.send("Hey everyone, standup in 5 minutes!");
        bob.send("Got it, thanks!");

        System.out.println("\n--- Private Message ---");
        alice.sendPrivate("Can you review my PR?", "Bob");

        System.out.println("\n--- Content Filtering ---");
        charlie.send("Check out this spam link");

        System.out.println("\n--- User Leaves ---");
        room.removeUser(bob);
        alice.send("Bob just left, meeting canceled.");

        System.out.println("\n--- Online Users ---");
        System.out.println("Online: " + room.getOnlineUsers());
    }
}
```

**Output:**
```
>>> Alice joined 'Backend Developers' (online: 1)
>>> Bob joined 'Backend Developers' (online: 2)
  [Alice] received from System: Bob has joined the chat
>>> Charlie joined 'Backend Developers' (online: 3)
  [Alice] received from System: Charlie has joined the chat
  [Bob] received from System: Charlie has joined the chat

--- Messaging ---
[Alice] sends: Hey everyone, standup in 5 minutes!
  [Bob] received from Alice: Hey everyone, standup in 5 minutes!
  [Charlie] received from Alice: Hey everyone, standup in 5 minutes!
[Bob] sends: Got it, thanks!
  [Alice] received from Bob: Got it, thanks!
  [Charlie] received from Bob: Got it, thanks!

--- Private Message ---
[Alice] whispers to Bob: Can you review my PR?
  [Bob] received from Alice: [PRIVATE] Can you review my PR?

--- Content Filtering ---
[Charlie] sends: Check out this spam link
  [Charlie] received from System: Your message was blocked (policy violation)

--- User Leaves ---
>>> Bob left 'Backend Developers' (online: 2)
  [Alice] received from System: Bob has left the chat
  [Charlie] received from System: Bob has left the chat
[Alice] sends: Bob just left, meeting canceled.
  [Charlie] received from Alice: Bob just left, meeting canceled.

--- Online Users ---
Online: [Alice, Charlie]
```

Notice that **no User object references another User**. All communication goes through
the ChatRoom mediator. The mediator handles routing, filtering, and notifications.

---

## Python Implementation: Event Mediator for Microservices

### Event-Driven Service Coordination

```python
from datetime import datetime
from typing import Dict, List, Callable, Any


class EventMediator:
    """Central mediator that coordinates events between services."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._services: Dict[str, object] = {}
        self._event_log: List[dict] = []

    def register_service(self, name, service):
        self._services[name] = service
        service.mediator = self
        print(f"[Mediator] Registered service: {name}")

    def subscribe(self, event_type, handler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event_type, data, source="unknown"):
        self._event_log.append({
            "event": event_type,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "data": str(data)
        })

        handlers = self._handlers.get(event_type, [])
        print(f"\n[Mediator] Event '{event_type}' from {source} "
              f"-> {len(handlers)} handler(s)")

        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"[Mediator] Handler error: {e}")

    def get_service(self, name):
        return self._services.get(name)

    def get_event_log(self):
        return self._event_log


class OrderService:
    """Handles order creation and management."""

    def __init__(self):
        self.mediator = None
        self.orders = {}
        self._next_id = 1000

    def setup(self):
        self.mediator.subscribe("payment.completed", self._on_payment)
        self.mediator.subscribe("inventory.reserved", self._on_reserved)

    def create_order(self, customer, items, total):
        order_id = self._next_id
        self._next_id += 1

        self.orders[order_id] = {
            "id": order_id,
            "customer": customer,
            "items": items,
            "total": total,
            "status": "created"
        }

        print(f"  [Order] Created order #{order_id} for {customer}")
        self.mediator.publish("order.created", {
            "order_id": order_id,
            "items": items,
            "total": total,
            "customer": customer
        }, source="OrderService")

        return order_id

    def _on_payment(self, data):
        order_id = data["order_id"]
        if order_id in self.orders:
            self.orders[order_id]["status"] = "paid"
            print(f"  [Order] Order #{order_id} marked as paid")

    def _on_reserved(self, data):
        order_id = data["order_id"]
        if order_id in self.orders:
            self.orders[order_id]["status"] = "reserved"
            print(f"  [Order] Order #{order_id} inventory reserved")


class InventoryService:
    """Manages product stock levels."""

    def __init__(self):
        self.mediator = None
        self.stock = {
            "WIDGET-A": 50,
            "WIDGET-B": 30,
            "GADGET-X": 10
        }

    def setup(self):
        self.mediator.subscribe("order.created", self._on_order_created)

    def _on_order_created(self, data):
        order_id = data["order_id"]
        items = data["items"]
        all_available = True

        for item, qty in items.items():
            available = self.stock.get(item, 0)
            if available >= qty:
                self.stock[item] -= qty
                print(f"  [Inventory] Reserved {qty}x {item} "
                      f"(remaining: {self.stock[item]})")
            else:
                print(f"  [Inventory] INSUFFICIENT {item}: "
                      f"need {qty}, have {available}")
                all_available = False

        if all_available:
            self.mediator.publish("inventory.reserved", {
                "order_id": order_id,
                "status": "reserved"
            }, source="InventoryService")
        else:
            self.mediator.publish("inventory.failed", {
                "order_id": order_id,
                "reason": "insufficient stock"
            }, source="InventoryService")


class PaymentService:
    """Processes payments."""

    def __init__(self):
        self.mediator = None
        self.payments = {}

    def setup(self):
        self.mediator.subscribe("inventory.reserved",
                                self._on_inventory_reserved)

    def _on_inventory_reserved(self, data):
        order_id = data["order_id"]
        print(f"  [Payment] Processing payment for order #{order_id}")

        # Simulate payment processing
        self.payments[order_id] = {"status": "completed"}

        self.mediator.publish("payment.completed", {
            "order_id": order_id,
            "status": "completed"
        }, source="PaymentService")


class NotificationService:
    """Sends notifications to customers."""

    def __init__(self):
        self.mediator = None
        self.sent = []

    def setup(self):
        self.mediator.subscribe("order.created", self._on_order)
        self.mediator.subscribe("payment.completed", self._on_payment)
        self.mediator.subscribe("inventory.failed", self._on_inv_fail)

    def _on_order(self, data):
        msg = f"Order #{data['order_id']} received for {data['customer']}"
        self.sent.append(msg)
        print(f"  [Notify] EMAIL: {msg}")

    def _on_payment(self, data):
        msg = f"Payment confirmed for order #{data['order_id']}"
        self.sent.append(msg)
        print(f"  [Notify] EMAIL: {msg}")

    def _on_inv_fail(self, data):
        msg = (f"Order #{data['order_id']} cannot be fulfilled: "
               f"{data['reason']}")
        self.sent.append(msg)
        print(f"  [Notify] EMAIL: {msg}")


class AnalyticsService:
    """Tracks business events."""

    def __init__(self):
        self.mediator = None
        self.events = []

    def setup(self):
        self.mediator.subscribe("order.created", self._track)
        self.mediator.subscribe("payment.completed", self._track)
        self.mediator.subscribe("inventory.failed", self._track)

    def _track(self, data):
        self.events.append(data)
        print(f"  [Analytics] Tracked event (total: {len(self.events)})")
```

### Wiring Everything Together

```python
# Create the mediator
mediator = EventMediator()

# Create services
orders = OrderService()
inventory = InventoryService()
payments = PaymentService()
notifications = NotificationService()
analytics = AnalyticsService()

# Register all services with the mediator
mediator.register_service("orders", orders)
mediator.register_service("inventory", inventory)
mediator.register_service("payments", payments)
mediator.register_service("notifications", notifications)
mediator.register_service("analytics", analytics)

# Subscribe to events
orders.setup()
inventory.setup()
payments.setup()
notifications.setup()
analytics.setup()

# Trigger a successful order flow
print("\n" + "=" * 60)
print("SCENARIO 1: Successful Order")
print("=" * 60)
order_id = orders.create_order(
    customer="Alice",
    items={"WIDGET-A": 2, "GADGET-X": 1},
    total=149.99
)

# Trigger an order that fails due to insufficient stock
print("\n" + "=" * 60)
print("SCENARIO 2: Failed Order (insufficient stock)")
print("=" * 60)
orders.create_order(
    customer="Bob",
    items={"GADGET-X": 100},  # only 9 left
    total=999.99
)

# Show event log
print("\n" + "=" * 60)
print("EVENT LOG")
print("=" * 60)
for entry in mediator.get_event_log():
    print(f"  {entry['event']:25s} from {entry['source']}")
```

**Output:**
```
[Mediator] Registered service: orders
[Mediator] Registered service: inventory
[Mediator] Registered service: payments
[Mediator] Registered service: notifications
[Mediator] Registered service: analytics

============================================================
SCENARIO 1: Successful Order
============================================================
  [Order] Created order #1000 for Alice

[Mediator] Event 'order.created' from OrderService -> 3 handler(s)
  [Inventory] Reserved 2x WIDGET-A (remaining: 48)
  [Inventory] Reserved 1x GADGET-X (remaining: 9)

[Mediator] Event 'inventory.reserved' from InventoryService -> 2 handler(s)
  [Order] Order #1000 inventory reserved
  [Payment] Processing payment for order #1000

[Mediator] Event 'payment.completed' from PaymentService -> 3 handler(s)
  [Order] Order #1000 marked as paid
  [Notify] EMAIL: Payment confirmed for order #1000
  [Analytics] Tracked event (total: 2)
  [Notify] EMAIL: Order #1000 received for Alice
  [Analytics] Tracked event (total: 1)

============================================================
SCENARIO 2: Failed Order (insufficient stock)
============================================================
  [Order] Created order #1001 for Bob

[Mediator] Event 'order.created' from OrderService -> 3 handler(s)
  [Inventory] INSUFFICIENT GADGET-X: need 100, have 9

[Mediator] Event 'inventory.failed' from InventoryService -> 2 handler(s)
  [Notify] EMAIL: Order #1001 cannot be fulfilled: insufficient stock
  [Analytics] Tracked event (total: 3)
  [Notify] EMAIL: Order #1001 received for Bob
  [Analytics] Tracked event (total: 2)

============================================================
EVENT LOG
============================================================
  order.created             from OrderService
  inventory.reserved        from InventoryService
  payment.completed         from PaymentService
  order.created             from OrderService
  inventory.failed          from InventoryService
```

No service references another service directly. OrderService does not import
InventoryService. PaymentService does not know about NotificationService. They all
communicate through the mediator.

---

## Mediator vs Observer

These patterns are frequently confused. Here is the difference:

```
+-------------------+------------------------------------+------------------------------------+
| Aspect            | Mediator                           | Observer                           |
+-------------------+------------------------------------+------------------------------------+
| Direction         | Bidirectional (components talk     | Unidirectional (subject notifies   |
|                   | to mediator, mediator talks back)  | observers)                         |
+-------------------+------------------------------------+------------------------------------+
| Knowledge         | Mediator knows all components      | Subject does not know observer     |
|                   |                                    | details                            |
+-------------------+------------------------------------+------------------------------------+
| Logic location    | Coordination logic in mediator     | No coordination logic; observers   |
|                   |                                    | react independently                |
+-------------------+------------------------------------+------------------------------------+
| Purpose           | Reduce coupling between peers      | Notify interested parties of       |
|                   |                                    | state changes                      |
+-------------------+------------------------------------+------------------------------------+
| Components        | Peers (equal participants)         | Subject and subscribers            |
|                   |                                    | (hierarchy)                        |
+-------------------+------------------------------------+------------------------------------+
```

**Observer** says: "When X changes, notify everyone who cares." There is no logic about
what to do with the notification.

**Mediator** says: "When X happens, here is exactly what Y and Z should do." The mediator
contains business logic about coordination.

In practice, a Mediator often uses Observer internally (publish/subscribe for routing)
but adds coordination logic on top.

---

## Before vs After Comparison

### Before: Direct Dependencies

```python
class OrderService:
    def __init__(self, inventory, payment, notifications, analytics):
        self.inventory = inventory      # direct dependency
        self.payment = payment          # direct dependency
        self.notifications = notifications  # direct dependency
        self.analytics = analytics      # direct dependency

    def create_order(self, data):
        self.inventory.reserve(data)
        self.payment.charge(data)
        self.notifications.send(data)
        self.analytics.track(data)
        # Adding shipping means changing this class
```

### After: Mediator

```python
class OrderService:
    def __init__(self, mediator):
        self.mediator = mediator  # single dependency

    def create_order(self, data):
        self.mediator.publish("order.created", data)
        # Adding shipping means adding a handler to the mediator
        # This class does not change
```

---

## When to Use / When NOT to Use

### Use Mediator When

- Multiple components communicate in complex ways (many-to-many)
- You want to reuse components independently without their communication partners
- Adding new components should not require modifying existing ones
- Communication logic should be centralized and easy to change
- You need audit logging of all inter-component communication

### Do NOT Use Mediator When

- Components have simple, one-to-one relationships (direct calls are fine)
- The mediator would become a massive "God Object" doing too much
- Real-time performance is critical (the indirection adds latency)
- The coordination logic is trivial (adding a mediator is over-engineering)
- You only have 2-3 components (not enough complexity to justify it)

---

## Common Mistakes

### Mistake 1: God Mediator

```python
# WRONG: mediator does ALL the business logic
class GodMediator:
    def handle_order(self, data):
        self.check_inventory(data)      # business logic here
        self.calculate_tax(data)         # and here
        self.process_payment(data)       # and here
        self.generate_invoice(data)      # and here
        self.send_notification(data)     # and here
        # Mediator becomes a 5000-line monolith

# RIGHT: mediator only routes, services contain logic
class OrderMediator:
    def handle_order(self, data):
        self.publish("order.created", data)
        # Each service handles its own logic
```

### Mistake 2: Components Bypassing the Mediator

```java
// WRONG: direct communication defeats the pattern
public class UserService {
    private NotificationService notifier; // direct reference!

    public void createUser(User user) {
        // ... create user ...
        notifier.sendWelcome(user); // bypassing mediator!
    }
}
```

### Mistake 3: Circular Event Chains

```python
# WRONG: A triggers B, B triggers A -> infinite loop
mediator.subscribe("order.updated", payment_service.handle)
mediator.subscribe("payment.updated", order_service.handle)
# order.updated -> payment.updated -> order.updated -> ...
```

**Fix:** Use event naming that distinguishes commands from responses, or add loop
detection to the mediator.

---

## Best Practices

1. **Keep the mediator thin.** It should coordinate, not compute. Business logic belongs
   in the services, not the mediator.

2. **Use event naming conventions.** Adopt a pattern like `entity.action`
   (order.created, payment.completed) to make events discoverable.

3. **Log all mediated communication.** Since everything goes through the mediator, it is
   the perfect place for audit trails and debugging.

4. **Prevent circular events.** Track event chains and break cycles. Consider maximum
   chain depth limits.

5. **Consider splitting large mediators.** If one mediator handles 50 event types, split
   it into domain-specific mediators (OrderMediator, UserMediator).

6. **Make the mediator replaceable.** Define the mediator as an interface so you can
   swap implementations (in-memory for testing, message queue for production).

---

## Quick Summary

The Mediator pattern replaces many-to-many direct dependencies with many-to-one
relationships through a central coordinator. Components communicate exclusively through
the mediator, making them independent and reusable. The mediator encapsulates the
coordination logic that would otherwise be scattered across components.

```
Problem:  N components with direct dependencies create N*(N-1)/2 connections.
Solution: Route all communication through a central mediator.
Key:      Components know only the mediator, never each other.
```

---

## Key Points

- **Mediator** centralizes complex communication between multiple objects
- It converts **many-to-many** relationships into **many-to-one** (each to mediator)
- Components (colleagues) are decoupled from each other and only know the mediator
- The air traffic controller is the classic analogy: planes talk to the tower, not each
  other
- **Mediator vs Observer**: Mediator adds coordination logic; Observer just broadcasts
- Watch out for the **God Mediator** anti-pattern: keep coordination logic thin
- Use event naming conventions and logging for debuggability
- Adding new components requires changing only the mediator, not existing components

---

## Practice Questions

1. In the air traffic controller analogy, what happens when the tower (mediator) goes
   down? How does this translate to software systems, and what can you do about it?

2. How would you prevent the God Mediator anti-pattern in a system with 20+ event
   types? Describe a concrete approach.

3. Explain the difference between Mediator and Observer with a concrete example of each
   solving the same problem differently.

4. You have 4 microservices that currently communicate directly. Adding a 5th service
   requires changing all 4. Describe how a Mediator would solve this, step by step.

5. In the Python EventMediator example, what would happen if the InventoryService
   published "order.created" instead of "inventory.reserved"? How would you prevent
   such bugs?

---

## Exercises

### Exercise 1: Smart Home Mediator

Build a smart home controller:

- Components: Thermostat, Lights, SecuritySystem, MusicPlayer, CoffeeMaker
- Rules coordinated by the mediator:
  - When SecuritySystem detects "away mode", turn off Lights and Thermostat, stop Music
  - When SecuritySystem detects "home mode", turn on Lights, set Thermostat to 72F
  - When Thermostat goes above 80F, turn off CoffeeMaker (heat reduction)
- No component should reference another directly
- Demonstrate adding a new component (Blinds) by only modifying the mediator

### Exercise 2: Form Validation Mediator

Create a form validation system:

- Fields: UsernameField, EmailField, PasswordField, ConfirmPasswordField, SubmitButton
- Rules:
  - SubmitButton is disabled until all fields are valid
  - ConfirmPasswordField validates against PasswordField (must match)
  - EmailField shows a warning if username part of email does not match UsernameField
- All validation logic lives in the mediator, not in the fields
- Fields only emit "changed" events and receive "setError" or "clearError" commands

### Exercise 3: Microservice Orchestrator

Build an order fulfillment orchestrator:

- Services: OrderService, WarehouseService, PaymentService, ShippingService,
  NotificationService
- Flow: Order -> Warehouse reserves -> Payment charges -> Shipping creates label ->
  Notification sends confirmation
- If any step fails, previous steps must be compensated (reverse order)
- The mediator tracks the state of each order through the pipeline
- Add logging that shows the complete event chain for debugging

---

## What Is Next?

The next chapter introduces the **Iterator Pattern**, which provides a way to access
elements of a collection sequentially without exposing the underlying structure. Where
Mediator centralizes communication between components, Iterator standardizes how you
traverse them. Both patterns reduce coupling, but in different dimensions.
