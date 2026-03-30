# Chapter 19: State Pattern -- Behavior Changes Based on Internal State

## What You Will Learn

- How to eliminate state-based `if/else` chains by using state objects
- Implementing a state machine for order processing in Java (Pending, Confirmed, Shipped, Delivered)
- Building a Python document workflow (Draft, Review, Published)
- Managing state transitions cleanly and preventing invalid transitions
- Real-world applications: order processing, user sessions, payment states
- When the State pattern is the right tool and when a simple enum is enough

## Why This Chapter Matters

Almost every backend system manages objects that change behavior based on their state. An order behaves differently when it is pending versus shipped. A user session behaves differently when active versus expired. A document goes through draft, review, and published states with different rules at each stage.

The naive approach -- giant `if/else` or `switch` blocks checking the current state -- quickly becomes unreadable and error-prone. Adding a new state means modifying every method that checks state. The State pattern solves this by putting each state's behavior into its own class, making state transitions explicit and state-specific logic isolated.

---

## The Problem: State Checking Everywhere

```java
// Order.java (BEFORE -- state checks everywhere)
public class Order {
    private String state = "PENDING";

    public void confirm() {
        if ("PENDING".equals(state)) {
            state = "CONFIRMED";
        } else if ("CONFIRMED".equals(state)) {
            throw new IllegalStateException("Already confirmed");
        } else if ("SHIPPED".equals(state)) {
            throw new IllegalStateException("Already shipped");
        } else if ("DELIVERED".equals(state)) {
            throw new IllegalStateException("Already delivered");
        } else if ("CANCELLED".equals(state)) {
            throw new IllegalStateException("Order is cancelled");
        }
    }

    public void ship() {
        if ("CONFIRMED".equals(state)) {
            state = "SHIPPED";
        } else if ("PENDING".equals(state)) {
            throw new IllegalStateException("Must confirm first");
        } else if ("SHIPPED".equals(state)) {
            throw new IllegalStateException("Already shipped");
        }
        // ... more checks for every method, every state
    }

    // cancel(), deliver(), getStatus() -- ALL have similar if/else blocks
    // Adding a new state (e.g., PROCESSING) means modifying EVERY method.
}
```

```
The State Explosion Problem:

  States:   PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
  Methods:  confirm(), ship(), deliver(), cancel(), getStatus()

  Every method checks every state:
  5 states x 5 methods = 25 conditional branches

  Add one state (PROCESSING):
  6 states x 5 methods = 30 conditional branches
  You must modify ALL 5 methods.
```

---

## The Solution: State Pattern

```
State Pattern Structure:

  +-------------------+          +-------------------+
  |     Order         |          |   OrderState      |
  | (Context)         |  has-a   |   (Interface)     |
  |                   |--------->|                   |
  | - state: State    |          | + confirm(order)  |
  | + confirm()       |          | + ship(order)     |
  | + ship()          |          | + deliver(order)  |
  | + cancel()        |          | + cancel(order)   |
  +-------------------+          | + getStatus()     |
                                 +-------------------+
                                   ^    ^    ^    ^
                                   |    |    |    |
                         Pending  Confirmed Shipped Delivered
                          State    State    State    State

  Each state class handles ONLY its own behavior.
  The Order delegates to its current state.
  State transitions happen by replacing the state object.
```

---

## Java Implementation: Order State Machine

### Step 1: Define the State Interface

```java
// OrderState.java
public interface OrderState {
    void confirm(Order order);
    void ship(Order order);
    void deliver(Order order);
    void cancel(Order order);
    String getStatus();
}
```

### Step 2: Implement Each State

```java
// PendingState.java
public class PendingState implements OrderState {

    @Override
    public void confirm(Order order) {
        System.out.println("  Order confirmed. Preparing for fulfillment.");
        order.setState(new ConfirmedState());
    }

    @Override
    public void ship(Order order) {
        throw new IllegalStateException(
            "Cannot ship -- order must be confirmed first.");
    }

    @Override
    public void deliver(Order order) {
        throw new IllegalStateException(
            "Cannot deliver -- order is still pending.");
    }

    @Override
    public void cancel(Order order) {
        System.out.println("  Order cancelled. No charges applied.");
        order.setState(new CancelledState());
    }

    @Override
    public String getStatus() {
        return "PENDING";
    }
}

// ConfirmedState.java
public class ConfirmedState implements OrderState {

    @Override
    public void confirm(Order order) {
        throw new IllegalStateException("Order is already confirmed.");
    }

    @Override
    public void ship(Order order) {
        System.out.println("  Order shipped. Tracking number generated.");
        order.setState(new ShippedState());
    }

    @Override
    public void deliver(Order order) {
        throw new IllegalStateException(
            "Cannot deliver -- order has not been shipped.");
    }

    @Override
    public void cancel(Order order) {
        System.out.println("  Order cancelled. Refund initiated.");
        order.setState(new CancelledState());
    }

    @Override
    public String getStatus() {
        return "CONFIRMED";
    }
}

// ShippedState.java
public class ShippedState implements OrderState {

    @Override
    public void confirm(Order order) {
        throw new IllegalStateException("Order is already past confirmation.");
    }

    @Override
    public void ship(Order order) {
        throw new IllegalStateException("Order is already shipped.");
    }

    @Override
    public void deliver(Order order) {
        System.out.println("  Order delivered. Customer notified.");
        order.setState(new DeliveredState());
    }

    @Override
    public void cancel(Order order) {
        throw new IllegalStateException(
            "Cannot cancel -- order is already in transit.");
    }

    @Override
    public String getStatus() {
        return "SHIPPED";
    }
}

// DeliveredState.java
public class DeliveredState implements OrderState {

    @Override
    public void confirm(Order order) {
        throw new IllegalStateException("Order already delivered.");
    }

    @Override
    public void ship(Order order) {
        throw new IllegalStateException("Order already delivered.");
    }

    @Override
    public void deliver(Order order) {
        throw new IllegalStateException("Order already delivered.");
    }

    @Override
    public void cancel(Order order) {
        throw new IllegalStateException(
            "Cannot cancel a delivered order. Use returns.");
    }

    @Override
    public String getStatus() {
        return "DELIVERED";
    }
}

// CancelledState.java
public class CancelledState implements OrderState {

    @Override
    public void confirm(Order order) {
        throw new IllegalStateException("Cannot confirm a cancelled order.");
    }

    @Override
    public void ship(Order order) {
        throw new IllegalStateException("Cannot ship a cancelled order.");
    }

    @Override
    public void deliver(Order order) {
        throw new IllegalStateException("Cannot deliver a cancelled order.");
    }

    @Override
    public void cancel(Order order) {
        throw new IllegalStateException("Order is already cancelled.");
    }

    @Override
    public String getStatus() {
        return "CANCELLED";
    }
}
```

### Step 3: Build the Context (Order)

```java
// Order.java (AFTER -- State Pattern)
public class Order {
    private final String orderId;
    private OrderState state;
    private final List<String> history = new ArrayList<>();

    public Order(String orderId) {
        this.orderId = orderId;
        this.state = new PendingState();
        recordTransition("Order created");
    }

    public void setState(OrderState newState) {
        String transition = state.getStatus() + " -> " + newState.getStatus();
        this.state = newState;
        recordTransition(transition);
    }

    public void confirm()  { state.confirm(this); }
    public void ship()     { state.ship(this); }
    public void deliver()  { state.deliver(this); }
    public void cancel()   { state.cancel(this); }
    public String getStatus() { return state.getStatus(); }

    private void recordTransition(String description) {
        history.add("[" + java.time.LocalTime.now()
            .format(java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss"))
            + "] " + description);
    }

    public void printHistory() {
        System.out.println("  History for " + orderId + ":");
        history.forEach(h -> System.out.println("    " + h));
    }
}
```

### Step 4: Use It

```java
// Main.java
public class Main {
    public static void main(String[] args) {
        Order order = new Order("ORD-001");
        System.out.println("Status: " + order.getStatus());

        // Happy path: Pending -> Confirmed -> Shipped -> Delivered
        order.confirm();
        System.out.println("Status: " + order.getStatus());

        order.ship();
        System.out.println("Status: " + order.getStatus());

        order.deliver();
        System.out.println("Status: " + order.getStatus());

        order.printHistory();

        // Try invalid transition
        System.out.println("\nAttempting to cancel delivered order:");
        try {
            order.cancel();
        } catch (IllegalStateException e) {
            System.out.println("  Error: " + e.getMessage());
        }

        // Cancellation path
        System.out.println("\n--- Cancellation Scenario ---");
        Order order2 = new Order("ORD-002");
        order2.confirm();
        order2.cancel();
        System.out.println("Status: " + order2.getStatus());
        order2.printHistory();
    }
}
```

**Output:**
```
Status: PENDING
  Order confirmed. Preparing for fulfillment.
Status: CONFIRMED
  Order shipped. Tracking number generated.
Status: SHIPPED
  Order delivered. Customer notified.
Status: DELIVERED
  History for ORD-001:
    [10:30:01] Order created
    [10:30:01] PENDING -> CONFIRMED
    [10:30:01] CONFIRMED -> SHIPPED
    [10:30:01] SHIPPED -> DELIVERED

Attempting to cancel delivered order:
  Error: Cannot cancel a delivered order. Use returns.

--- Cancellation Scenario ---
  Order confirmed. Preparing for fulfillment.
  Order cancelled. Refund initiated.
Status: CANCELLED
  History for ORD-002:
    [10:30:01] Order created
    [10:30:01] PENDING -> CONFIRMED
    [10:30:01] CONFIRMED -> CANCELLED
```

---

## State Transition Diagram

```
+----------------------------------------------------------+
|                 ORDER STATE TRANSITIONS                    |
+----------------------------------------------------------+

                    +----------+
                    | PENDING  |
                    +----------+
                   /            \
            confirm()          cancel()
                /                \
        +----------+        +----------+
        |CONFIRMED |        |CANCELLED |
        +----------+        +----------+
       /            \            (final)
    ship()        cancel()
      /              \
 +----------+        |
 | SHIPPED  |        |
 +----------+   (goes to CANCELLED)
      |
   deliver()
      |
 +----------+
 |DELIVERED |
 +----------+
    (final)

  Valid transitions are defined by each state class.
  Invalid transitions throw IllegalStateException.
  No if/else needed -- just call the method.
+----------------------------------------------------------+
```

---

## Python Implementation: Document Workflow

```python
# document_workflow.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class DocumentState(ABC):
    """Base state for document workflow."""

    @abstractmethod
    def edit(self, document: "Document", content: str) -> None:
        pass

    @abstractmethod
    def submit_for_review(self, document: "Document") -> None:
        pass

    @abstractmethod
    def approve(self, document: "Document", reviewer: str) -> None:
        pass

    @abstractmethod
    def reject(self, document: "Document", reason: str) -> None:
        pass

    @abstractmethod
    def publish(self, document: "Document") -> None:
        pass

    @abstractmethod
    def archive(self, document: "Document") -> None:
        pass

    @abstractmethod
    def get_status(self) -> str:
        pass


class DraftState(DocumentState):

    def edit(self, document, content):
        document.content = content
        print(f"  [Draft] Content updated ({len(content)} chars)")

    def submit_for_review(self, document):
        if not document.content:
            raise ValueError("Cannot submit empty document for review")
        print("  [Draft] Submitted for review")
        document.set_state(ReviewState())

    def approve(self, document, reviewer):
        raise IllegalTransition("Cannot approve a draft. Submit for review first.")

    def reject(self, document, reason):
        raise IllegalTransition("Cannot reject a draft.")

    def publish(self, document):
        raise IllegalTransition("Cannot publish a draft. Must go through review.")

    def archive(self, document):
        print("  [Draft] Draft archived")
        document.set_state(ArchivedState())

    def get_status(self):
        return "DRAFT"


class ReviewState(DocumentState):

    def edit(self, document, content):
        raise IllegalTransition("Cannot edit during review. Reject first.")

    def submit_for_review(self, document):
        raise IllegalTransition("Already in review.")

    def approve(self, document, reviewer):
        document.approved_by = reviewer
        document.approved_at = datetime.now()
        print(f"  [Review] Approved by {reviewer}")
        document.set_state(ApprovedState())

    def reject(self, document, reason):
        document.rejection_reason = reason
        print(f"  [Review] Rejected: {reason}")
        document.set_state(DraftState())  # Back to draft for edits

    def publish(self, document):
        raise IllegalTransition("Cannot publish without approval.")

    def archive(self, document):
        raise IllegalTransition("Cannot archive during review.")

    def get_status(self):
        return "IN_REVIEW"


class ApprovedState(DocumentState):

    def edit(self, document, content):
        raise IllegalTransition("Cannot edit approved document.")

    def submit_for_review(self, document):
        raise IllegalTransition("Already approved.")

    def approve(self, document, reviewer):
        raise IllegalTransition("Already approved.")

    def reject(self, document, reason):
        print(f"  [Approved] Approval revoked: {reason}")
        document.set_state(DraftState())

    def publish(self, document):
        document.published_at = datetime.now()
        print(f"  [Approved] Document published!")
        document.set_state(PublishedState())

    def archive(self, document):
        raise IllegalTransition("Publish or reject before archiving.")

    def get_status(self):
        return "APPROVED"


class PublishedState(DocumentState):

    def edit(self, document, content):
        raise IllegalTransition("Cannot edit published document. Create a new version.")

    def submit_for_review(self, document):
        raise IllegalTransition("Already published.")

    def approve(self, document, reviewer):
        raise IllegalTransition("Already published.")

    def reject(self, document, reason):
        raise IllegalTransition("Cannot reject published document.")

    def publish(self, document):
        raise IllegalTransition("Already published.")

    def archive(self, document):
        print("  [Published] Document archived")
        document.set_state(ArchivedState())

    def get_status(self):
        return "PUBLISHED"


class ArchivedState(DocumentState):

    def edit(self, document, content):
        raise IllegalTransition("Cannot edit archived document.")

    def submit_for_review(self, document):
        raise IllegalTransition("Cannot submit archived document.")

    def approve(self, document, reviewer):
        raise IllegalTransition("Cannot approve archived document.")

    def reject(self, document, reason):
        raise IllegalTransition("Cannot reject archived document.")

    def publish(self, document):
        raise IllegalTransition("Cannot publish archived document.")

    def archive(self, document):
        raise IllegalTransition("Already archived.")

    def get_status(self):
        return "ARCHIVED"


class IllegalTransition(Exception):
    pass


class Document:
    """Context -- the object whose behavior changes with state."""

    def __init__(self, title: str, author: str):
        self.title = title
        self.author = author
        self.content: str = ""
        self.approved_by: Optional[str] = None
        self.approved_at: Optional[datetime] = None
        self.published_at: Optional[datetime] = None
        self.rejection_reason: Optional[str] = None
        self._state: DocumentState = DraftState()
        self._history: list[str] = [f"Created by {author}"]

    def set_state(self, new_state: DocumentState) -> None:
        old = self._state.get_status()
        self._state = new_state
        self._history.append(f"{old} -> {new_state.get_status()}")

    @property
    def status(self) -> str:
        return self._state.get_status()

    def edit(self, content: str) -> None:
        self._state.edit(self, content)

    def submit_for_review(self) -> None:
        self._state.submit_for_review(self)

    def approve(self, reviewer: str) -> None:
        self._state.approve(self, reviewer)

    def reject(self, reason: str) -> None:
        self._state.reject(self, reason)

    def publish(self) -> None:
        self._state.publish(self)

    def archive(self) -> None:
        self._state.archive(self)

    def print_history(self) -> None:
        print(f"  History for '{self.title}':")
        for entry in self._history:
            print(f"    - {entry}")


# --- Usage ---
if __name__ == "__main__":
    doc = Document("API Design Guide", "Alice")

    # Happy path: Draft -> Review -> Approved -> Published
    print("--- Happy Path ---")
    doc.edit("REST API best practices and conventions...")
    print(f"  Status: {doc.status}")

    doc.submit_for_review()
    print(f"  Status: {doc.status}")

    doc.approve("Bob")
    print(f"  Status: {doc.status}")

    doc.publish()
    print(f"  Status: {doc.status}")

    doc.print_history()

    # Rejection path
    print("\n--- Rejection Path ---")
    doc2 = Document("Security Policy", "Charlie")
    doc2.edit("Initial security guidelines...")
    doc2.submit_for_review()
    doc2.reject("Needs more detail on authentication")
    print(f"  Status: {doc2.status}")  # Back to DRAFT

    doc2.edit("Updated with authentication details...")
    doc2.submit_for_review()
    doc2.approve("Dave")
    doc2.publish()
    print(f"  Status: {doc2.status}")

    doc2.print_history()

    # Invalid transition
    print("\n--- Invalid Transition ---")
    try:
        doc2.edit("Try to edit published doc")
    except IllegalTransition as e:
        print(f"  Error: {e}")
```

**Output:**
```
--- Happy Path ---
  [Draft] Content updated (43 chars)
  Status: DRAFT
  [Draft] Submitted for review
  Status: IN_REVIEW
  [Review] Approved by Bob
  Status: APPROVED
  [Approved] Document published!
  Status: PUBLISHED
  History for 'API Design Guide':
    - Created by Alice
    - DRAFT -> IN_REVIEW
    - IN_REVIEW -> APPROVED
    - APPROVED -> PUBLISHED

--- Rejection Path ---
  [Draft] Content updated (32 chars)
  [Draft] Submitted for review
  [Review] Rejected: Needs more detail on authentication
  Status: DRAFT
  [Draft] Content updated (42 chars)
  [Draft] Submitted for review
  [Review] Approved by Dave
  [Approved] Document published!
  Status: PUBLISHED
  History for 'Security Policy':
    - Created by Charlie
    - DRAFT -> IN_REVIEW
    - IN_REVIEW -> DRAFT
    - DRAFT -> IN_REVIEW
    - IN_REVIEW -> APPROVED
    - APPROVED -> PUBLISHED

--- Invalid Transition ---
  Error: Cannot edit published document. Create a new version.
```

---

## Before vs After

```
BEFORE (if/else state checks):       AFTER (State Pattern):

  Order.confirm():                    Order.confirm():
  if (state == "PENDING")               state.confirm(this);
    state = "CONFIRMED";              // That is it. No if/else.
  else if (state == "CONFIRMED")
    throw ...;                        PendingState.confirm(order):
  else if (state == "SHIPPED")          order.setState(new ConfirmedState());
    throw ...;
  else if (state == "DELIVERED")      ConfirmedState.confirm(order):
    throw ...;                          throw "Already confirmed";
  else if (state == "CANCELLED")
    throw ...;                        Each state handles ONLY its behavior.

  Adding a new state:                 Adding a new state:
  Modify EVERY method in Order        Add ONE new state class
  (5 methods x 1 new branch = 5)     (implements the interface)
```

---

## When to Use / When NOT to Use

### Use State When

| Scenario | Why State Helps |
|---|---|
| Object behavior changes with state | Each state encapsulates its rules |
| Many state-dependent conditionals | Eliminates if/else chains |
| State transitions are complex | Transitions are explicit in each state |
| States will grow over time | Adding a state = adding a class |
| You need transition history | Easy to log state changes |

### Do NOT Use State When

| Scenario | Why Not |
|---|---|
| Only 2-3 simple states | A boolean or enum is simpler |
| States do not change behavior | State is just data, not behavior |
| All states behave the same | No variation = no need for pattern |
| Simple flag-based logic | `isActive` boolean suffices |

---

## Common Mistakes

### Mistake 1: State Classes That Know About Each Other

```java
// BAD -- PendingState creates ConfirmedState directly
public class PendingState implements OrderState {
    public void confirm(Order order) {
        ConfirmedState next = new ConfirmedState();
        next.setPreviousState(this);  // Circular dependency
        order.setState(next);
    }
}

// GOOD -- States are independent, context manages transitions
public class PendingState implements OrderState {
    public void confirm(Order order) {
        order.setState(new ConfirmedState());  // Simple and clean
    }
}
```

### Mistake 2: Putting Business Logic in the Context

```java
// BAD -- Order has state-specific logic
public class Order {
    public void confirm() {
        if (state.getStatus().equals("PENDING")) {
            // Business logic here defeats the purpose
            sendConfirmationEmail();
        }
        state.confirm(this);
    }
}

// GOOD -- State handles all state-specific behavior
public class PendingState implements OrderState {
    public void confirm(Order order) {
        // State-specific logic lives HERE
        order.setState(new ConfirmedState());
    }
}
```

### Mistake 3: Forgetting Terminal States

```java
// BAD -- Delivered order can transition to anything
public class DeliveredState implements OrderState {
    public void confirm(Order order) {
        order.setState(new ConfirmedState());  // This makes no sense
    }
}

// GOOD -- Terminal states reject all transitions
public class DeliveredState implements OrderState {
    public void confirm(Order order) {
        throw new IllegalStateException("Order already delivered.");
    }
    // ALL methods throw -- this is a final state
}
```

---

## Best Practices

1. **Make invalid transitions throw explicit exceptions.** The caller should know exactly why a transition failed.

2. **Log state transitions.** Maintain a history of state changes for debugging and audit trails.

3. **Keep state classes stateless when possible.** If a state does not store data, it can be shared (Flyweight).

4. **Define transitions in the state, not the context.** The context delegates; the state decides.

5. **Draw the state diagram first.** Before writing code, sketch all states and valid transitions. This prevents missed edge cases.

6. **Consider using an enum for simple cases.** If states do not have complex behavior, an enum with methods may be sufficient.

---

## Quick Summary

```
+---------------------------------------------------------------+
|                    STATE PATTERN SUMMARY                        |
+---------------------------------------------------------------+
| Intent:     Allow an object to change its behavior when its    |
|             internal state changes.                            |
+---------------------------------------------------------------+
| Problem:    if/else chains checking state in every method      |
| Solution:   Each state is a class that handles its own         |
|             behavior and transitions                           |
+---------------------------------------------------------------+
| Key parts:                                                     |
|   - Context (the object with state, e.g., Order)               |
|   - State interface (defines all state-dependent methods)      |
|   - Concrete states (one class per state)                      |
+---------------------------------------------------------------+
| Transitions: State objects replace themselves in the context   |
+---------------------------------------------------------------+
```

---

## Key Points

- The State pattern replaces state-conditional logic with polymorphic state objects.
- Each state is a separate class that defines behavior for that state only.
- State transitions happen by replacing the state object in the context.
- Invalid transitions are explicitly rejected with descriptive exceptions.
- Always draw the state diagram before coding to catch invalid transitions early.
- For simple cases with 2-3 states and minimal behavior, an enum is sufficient.

---

## Practice Questions

1. In the order example, how would you add a `PROCESSING` state between `CONFIRMED` and `SHIPPED`? How many existing classes would you need to modify?

2. Can two states share common behavior? For example, both `PendingState` and `ConfirmedState` allow cancellation. How would you avoid duplicating the cancellation logic?

3. The document workflow sends a document back to `DraftState` after rejection. But the original `DraftState` has no memory of previous reviews. How would you track that a document has been rejected before?

4. How does the State pattern relate to finite state machines (FSMs)? Could you generate state classes from an FSM definition?

5. In a multithreaded environment, what happens if two threads try to transition an order's state simultaneously? How would you make state transitions thread-safe?

---

## Exercises

### Exercise 1: Traffic Light State Machine

Build a traffic light with states: `Red`, `Green`, `Yellow`. Each state transitions to the next in sequence (Red -> Green -> Yellow -> Red). Each state has a `getDuration()` method returning how long it lasts. Add a `FlashingYellow` emergency state that can be entered from any state.

### Exercise 2: User Account States

Implement a user account with states: `Unverified`, `Active`, `Suspended`, `Closed`. Define valid transitions (e.g., Unverified -> Active via email verification, Active -> Suspended via admin action). Each state determines what actions the user can perform (login, post, edit profile).

### Exercise 3: Payment State Machine

Build a payment processor with states: `Initiated`, `Authorized`, `Captured`, `Refunded`, `Failed`. Model the transitions for a typical payment flow. Include partial refunds (Captured -> PartiallyRefunded -> Refunded). Log every transition with timestamps and amounts.

---

## What Is Next?

The State pattern manages how one object transitions through different behaviors. But what happens when you have many objects that need to communicate with each other, creating a tangled web of dependencies? In the next chapter, we explore the **Mediator pattern** -- a central coordinator that simplifies many-to-many communication down to manageable one-to-many relationships.
