# Chapter 28: Saga Pattern -- Managing Distributed Transactions

## What You Will Learn

- What the Saga pattern is and why distributed transactions are hard
- The difference between Choreography and Orchestration approaches
- How compensating transactions undo partial work on failure
- How to implement an order saga in Java
- A complete e-commerce checkout saga with failure handling
- When to use Sagas vs traditional database transactions

## Why This Chapter Matters

In a monolithic application, a database transaction guarantees that either all
operations succeed or none do. Transfer money from Account A to Account B? Both the
debit and credit happen, or neither does. The database handles it.

In a microservices architecture, a single business operation spans multiple services,
each with its own database. The order service creates an order, the payment service
charges the card, the inventory service reserves stock, and the shipping service
creates a label. There is no single database transaction that can wrap all of these.

If payment succeeds but inventory fails, you have charged the customer for products you
cannot ship. The Saga pattern solves this by breaking the distributed transaction into
a sequence of local transactions, each with a compensating action to undo its work.

---

## The Problem

You are building an e-commerce checkout that involves four services:

```
Customer clicks "Place Order"
    |
    v
+-- OrderService: Create order record
    |
    v
+-- InventoryService: Reserve items
    |
    v
+-- PaymentService: Charge credit card
    |
    v
+-- ShippingService: Create shipping label
    |
    v
Order confirmed!
```

What if PaymentService fails after InventoryService has already reserved the items?

```
OrderService:     Created order #1001        SUCCESS
InventoryService: Reserved 3 items           SUCCESS
PaymentService:   Card declined              FAILURE!
ShippingService:  Never reached              ---

Result: Items are reserved but never paid for.
        Other customers cannot buy those items.
        The order exists but is invalid.
```

You need to undo the inventory reservation and cancel the order. That is what Sagas do.

---

## The Solution: Saga Pattern

A Saga is a sequence of local transactions. Each transaction has a **compensating
transaction** that can undo its effects.

```
FORWARD FLOW (happy path):
  T1 ---------> T2 ---------> T3 ---------> T4
  Create        Reserve        Charge         Ship
  Order         Inventory      Payment        Items

COMPENSATION FLOW (on failure at T3):
  T1 ---------> T2 ---------> T3 (FAIL!)
  Create        Reserve        Charge
  Order         Inventory      Payment
                   |              |
                   v              v
                  C2             C3
                  Release        (nothing to
                  Inventory       undo, it failed)
                   |
                   v
                  C1
                  Cancel
                  Order
```

**Key concepts:**

- **Local transaction (T)**: A single step that modifies one service's data
- **Compensating transaction (C)**: The reverse of a local transaction, undoing its
  effects
- **Saga Execution Coordinator (SEC)**: The component that drives the saga forward
  and triggers compensations on failure

---

## Choreography vs Orchestration

There are two ways to coordinate a saga.

### Choreography: Decentralized, Event-Driven

Each service listens for events and reacts. No central coordinator.

```
+--------+  order.created  +-----------+  inventory.reserved  +---------+
| Order  |---------------->| Inventory |--------------------->| Payment |
+--------+                 +-----------+                      +---------+
    ^                           |                                  |
    |                           | inventory.failed                 |
    |    order.cancelled        v                                  |
    +--<--------------------[cancel]                               |
    |                                                              |
    |                      payment.completed                       |
    +--<-----------------------------------------------------------+
    |                      payment.failed
    +--<-----------------------------------------------------------+
```

**Pros:**
- Simple for small sagas (2-3 steps)
- No single point of failure
- Services are loosely coupled

**Cons:**
- Hard to understand the full flow (logic scattered across services)
- Difficult to debug (follow events across multiple logs)
- Risk of circular event dependencies
- Adding a step means modifying multiple services

### Orchestration: Centralized Coordinator

A saga orchestrator tells each service what to do and when.

```
                    +-----------------------+
                    |   Saga Orchestrator    |
                    |                       |
                    | 1. Create Order  -----|---> OrderService
                    | 2. Reserve Stock -----|---> InventoryService
                    | 3. Charge Payment ----|---> PaymentService
                    | 4. Create Shipment ---|---> ShippingService
                    |                       |
                    | On failure:           |
                    | 3. Refund Payment ----|---> PaymentService
                    | 2. Release Stock -----|---> InventoryService
                    | 1. Cancel Order  -----|---> OrderService
                    +-----------------------+
```

**Pros:**
- Easy to understand (entire flow in one place)
- Easy to add, remove, or reorder steps
- Central place for logging and monitoring
- Simpler to test

**Cons:**
- Single point of failure (mitigate with redundancy)
- Orchestrator can become complex for large sagas
- Risk of tight coupling to the orchestrator

**Recommendation**: Use **Choreography** for simple, 2-3 step sagas between closely
related services. Use **Orchestration** for complex, multi-step sagas where visibility
and control are important. Most production systems use orchestration.

---

## Java Implementation: Order Saga Orchestrator

### Step Definition

```java
import java.util.function.Consumer;

public class SagaStep {
    private final String name;
    private final Runnable action;
    private final Runnable compensation;
    private StepStatus status;

    public enum StepStatus {
        PENDING, RUNNING, COMPLETED, FAILED, COMPENSATED
    }

    public SagaStep(String name, Runnable action, Runnable compensation) {
        this.name = name;
        this.action = action;
        this.compensation = compensation;
        this.status = StepStatus.PENDING;
    }

    public boolean execute() {
        status = StepStatus.RUNNING;
        try {
            System.out.printf("  [STEP] Executing: %s%n", name);
            action.run();
            status = StepStatus.COMPLETED;
            System.out.printf("  [STEP] Completed: %s%n", name);
            return true;
        } catch (Exception e) {
            status = StepStatus.FAILED;
            System.out.printf("  [STEP] Failed: %s -- %s%n",
                    name, e.getMessage());
            return false;
        }
    }

    public void compensate() {
        if (status == StepStatus.COMPLETED) {
            System.out.printf("  [COMP] Compensating: %s%n", name);
            try {
                compensation.run();
                status = StepStatus.COMPENSATED;
                System.out.printf("  [COMP] Compensated: %s%n", name);
            } catch (Exception e) {
                System.out.printf("  [COMP] Compensation FAILED: %s -- %s%n",
                        name, e.getMessage());
                // In production: alert, retry queue, manual intervention
            }
        }
    }

    public String getName() { return name; }
    public StepStatus getStatus() { return status; }
}
```

### Saga Orchestrator

```java
import java.util.ArrayList;
import java.util.List;

public class SagaOrchestrator {
    private final String sagaId;
    private final List<SagaStep> steps;
    private SagaStatus status;

    public enum SagaStatus {
        NOT_STARTED, RUNNING, COMPLETED, COMPENSATING, FAILED
    }

    public SagaOrchestrator(String sagaId) {
        this.sagaId = sagaId;
        this.steps = new ArrayList<>();
        this.status = SagaStatus.NOT_STARTED;
    }

    public SagaOrchestrator addStep(String name, Runnable action,
                                     Runnable compensation) {
        steps.add(new SagaStep(name, action, compensation));
        return this;
    }

    public boolean execute() {
        System.out.printf("%n=== Saga '%s' Starting ===%n", sagaId);
        status = SagaStatus.RUNNING;
        int completedIndex = -1;

        // Execute steps forward
        for (int i = 0; i < steps.size(); i++) {
            boolean success = steps.get(i).execute();
            if (success) {
                completedIndex = i;
            } else {
                // Step failed -- compensate all completed steps
                System.out.printf("%n  [SAGA] Step %d failed. "
                        + "Starting compensation...%n", i + 1);
                status = SagaStatus.COMPENSATING;
                compensate(completedIndex);
                status = SagaStatus.FAILED;
                System.out.printf("=== Saga '%s' FAILED (compensated) ===%n",
                        sagaId);
                return false;
            }
        }

        status = SagaStatus.COMPLETED;
        System.out.printf("=== Saga '%s' COMPLETED ===%n", sagaId);
        return true;
    }

    private void compensate(int fromIndex) {
        // Compensate in reverse order
        for (int i = fromIndex; i >= 0; i--) {
            steps.get(i).compensate();
        }
    }

    public void printStatus() {
        System.out.printf("%nSaga '%s' Status: %s%n", sagaId, status);
        for (int i = 0; i < steps.size(); i++) {
            SagaStep step = steps.get(i);
            System.out.printf("  Step %d: %-25s [%s]%n",
                    i + 1, step.getName(), step.getStatus());
        }
    }
}
```

### Service Simulators

```java
public class OrderService {
    private String currentOrderId = null;

    public void createOrder(String orderId) {
        System.out.printf("    OrderService: Creating order %s%n", orderId);
        this.currentOrderId = orderId;
        // In production: INSERT INTO orders ...
    }

    public void cancelOrder(String orderId) {
        System.out.printf("    OrderService: Cancelling order %s%n", orderId);
        this.currentOrderId = null;
        // In production: UPDATE orders SET status='cancelled' ...
    }
}

public class InventoryService {
    private final java.util.Map<String, Integer> stock;
    private final List<String> reservations;

    public InventoryService() {
        stock = new java.util.HashMap<>();
        stock.put("LAPTOP", 5);
        stock.put("MOUSE", 20);
        stock.put("KEYBOARD", 0);  // out of stock!
        reservations = new ArrayList<>();
    }

    public void reserveItems(String orderId, String item, int qty) {
        int available = stock.getOrDefault(item, 0);
        if (available < qty) {
            throw new RuntimeException(
                String.format("Insufficient stock for %s: need %d, have %d",
                    item, qty, available));
        }
        stock.put(item, available - qty);
        reservations.add(orderId + ":" + item + ":" + qty);
        System.out.printf("    InventoryService: Reserved %dx %s "
                + "(remaining: %d)%n", qty, item, stock.get(item));
    }

    public void releaseItems(String orderId, String item, int qty) {
        stock.put(item, stock.getOrDefault(item, 0) + qty);
        reservations.removeIf(r -> r.startsWith(orderId));
        System.out.printf("    InventoryService: Released %dx %s "
                + "(remaining: %d)%n", qty, item, stock.get(item));
    }
}

public class PaymentService {
    private boolean simulateFailure = false;

    public void setSimulateFailure(boolean fail) {
        this.simulateFailure = fail;
    }

    public void charge(String orderId, double amount) {
        if (simulateFailure) {
            throw new RuntimeException("Payment declined: card expired");
        }
        System.out.printf("    PaymentService: Charged $%.2f for order %s%n",
                amount, orderId);
    }

    public void refund(String orderId, double amount) {
        System.out.printf("    PaymentService: Refunded $%.2f for order %s%n",
                amount, orderId);
    }
}

public class ShippingService {
    public void createShipment(String orderId) {
        System.out.printf("    ShippingService: Created shipment for %s%n",
                orderId);
    }

    public void cancelShipment(String orderId) {
        System.out.printf("    ShippingService: Cancelled shipment for %s%n",
                orderId);
    }
}
```

### Running the Saga

```java
public class SagaDemo {
    public static void main(String[] args) {
        OrderService orders = new OrderService();
        InventoryService inventory = new InventoryService();
        PaymentService payments = new PaymentService();
        ShippingService shipping = new ShippingService();

        // Scenario 1: Successful order
        System.out.println("*".repeat(60));
        System.out.println("SCENARIO 1: Successful Order");
        System.out.println("*".repeat(60));

        SagaOrchestrator saga1 = new SagaOrchestrator("order-1001")
            .addStep("Create Order",
                () -> orders.createOrder("1001"),
                () -> orders.cancelOrder("1001"))
            .addStep("Reserve Inventory",
                () -> inventory.reserveItems("1001", "LAPTOP", 1),
                () -> inventory.releaseItems("1001", "LAPTOP", 1))
            .addStep("Process Payment",
                () -> payments.charge("1001", 999.99),
                () -> payments.refund("1001", 999.99))
            .addStep("Create Shipment",
                () -> shipping.createShipment("1001"),
                () -> shipping.cancelShipment("1001"));

        saga1.execute();
        saga1.printStatus();

        // Scenario 2: Payment failure (triggers compensation)
        System.out.println("\n" + "*".repeat(60));
        System.out.println("SCENARIO 2: Payment Failure");
        System.out.println("*".repeat(60));

        payments.setSimulateFailure(true);

        SagaOrchestrator saga2 = new SagaOrchestrator("order-1002")
            .addStep("Create Order",
                () -> orders.createOrder("1002"),
                () -> orders.cancelOrder("1002"))
            .addStep("Reserve Inventory",
                () -> inventory.reserveItems("1002", "MOUSE", 2),
                () -> inventory.releaseItems("1002", "MOUSE", 2))
            .addStep("Process Payment",
                () -> payments.charge("1002", 49.98),
                () -> payments.refund("1002", 49.98))
            .addStep("Create Shipment",
                () -> shipping.createShipment("1002"),
                () -> shipping.cancelShipment("1002"));

        saga2.execute();
        saga2.printStatus();

        // Scenario 3: Inventory failure
        payments.setSimulateFailure(false);

        System.out.println("\n" + "*".repeat(60));
        System.out.println("SCENARIO 3: Out of Stock");
        System.out.println("*".repeat(60));

        SagaOrchestrator saga3 = new SagaOrchestrator("order-1003")
            .addStep("Create Order",
                () -> orders.createOrder("1003"),
                () -> orders.cancelOrder("1003"))
            .addStep("Reserve Inventory",
                () -> inventory.reserveItems("1003", "KEYBOARD", 1),
                () -> inventory.releaseItems("1003", "KEYBOARD", 1))
            .addStep("Process Payment",
                () -> payments.charge("1003", 79.99),
                () -> payments.refund("1003", 79.99));

        saga3.execute();
        saga3.printStatus();
    }
}
```

**Output:**
```
************************************************************
SCENARIO 1: Successful Order
************************************************************

=== Saga 'order-1001' Starting ===
  [STEP] Executing: Create Order
    OrderService: Creating order 1001
  [STEP] Completed: Create Order
  [STEP] Executing: Reserve Inventory
    InventoryService: Reserved 1x LAPTOP (remaining: 4)
  [STEP] Completed: Reserve Inventory
  [STEP] Executing: Process Payment
    PaymentService: Charged $999.99 for order 1001
  [STEP] Completed: Process Payment
  [STEP] Executing: Create Shipment
    ShippingService: Created shipment for 1001
  [STEP] Completed: Create Shipment
=== Saga 'order-1001' COMPLETED ===

Saga 'order-1001' Status: COMPLETED
  Step 1: Create Order              [COMPLETED]
  Step 2: Reserve Inventory         [COMPLETED]
  Step 3: Process Payment           [COMPLETED]
  Step 4: Create Shipment           [COMPLETED]

************************************************************
SCENARIO 2: Payment Failure
************************************************************

=== Saga 'order-1002' Starting ===
  [STEP] Executing: Create Order
    OrderService: Creating order 1002
  [STEP] Completed: Create Order
  [STEP] Executing: Reserve Inventory
    InventoryService: Reserved 2x MOUSE (remaining: 18)
  [STEP] Completed: Reserve Inventory
  [STEP] Executing: Process Payment
  [STEP] Failed: Process Payment -- Payment declined: card expired

  [SAGA] Step 3 failed. Starting compensation...
  [COMP] Compensating: Reserve Inventory
    InventoryService: Released 2x MOUSE (remaining: 20)
  [COMP] Compensated: Reserve Inventory
  [COMP] Compensating: Create Order
    OrderService: Cancelling order 1002
  [COMP] Compensated: Create Order
=== Saga 'order-1002' FAILED (compensated) ===

Saga 'order-1002' Status: FAILED
  Step 1: Create Order              [COMPENSATED]
  Step 2: Reserve Inventory         [COMPENSATED]
  Step 3: Process Payment           [FAILED]
  Step 4: Create Shipment           [PENDING]

************************************************************
SCENARIO 3: Out of Stock
************************************************************

=== Saga 'order-1003' Starting ===
  [STEP] Executing: Create Order
    OrderService: Creating order 1003
  [STEP] Completed: Create Order
  [STEP] Executing: Reserve Inventory
  [STEP] Failed: Reserve Inventory -- Insufficient stock for KEYBOARD: need 1, have 0

  [SAGA] Step 2 failed. Starting compensation...
  [COMP] Compensating: Create Order
    OrderService: Cancelling order 1003
  [COMP] Compensated: Create Order
=== Saga 'order-1003' FAILED (compensated) ===

Saga 'order-1003' Status: FAILED
  Step 1: Create Order              [COMPENSATED]
  Step 2: Reserve Inventory         [FAILED]
  Step 3: Process Payment           [PENDING]
```

---

## Compensating Transactions: The Hard Part

Compensating transactions are not always simple "undo" operations. They must account
for the real-world effects that have already occurred.

```
+--------------------+----------------------------+---------------------------+
| Action             | Compensation               | Complication              |
+--------------------+----------------------------+---------------------------+
| Create order       | Cancel order               | Simple status update      |
| Reserve inventory  | Release inventory          | Simple: add quantity back |
| Charge credit card | Refund credit card         | Refund takes 3-5 days!    |
| Send email         | Send correction email      | Cannot unsend             |
| Ship package       | Initiate return shipment   | Package may be in transit |
| Update external API| Revert API call            | API may not support it    |
+--------------------+----------------------------+---------------------------+
```

**Key rules for compensating transactions:**

1. **Compensations must be idempotent.** They might be called multiple times (retries).
   Running a compensation twice should have the same effect as running it once.

2. **Compensations must always succeed.** If a compensation fails, you need a retry
   mechanism, dead letter queue, or manual intervention process.

3. **Compensations are semantic, not technical.** You cannot "undo" a credit card
   charge. You issue a refund, which is a separate forward transaction.

4. **Order matters.** Compensate in reverse order of execution. You cannot release
   inventory before cancelling the shipment that depends on it.

---

## Python Implementation: E-Commerce Checkout Saga

```python
from enum import Enum
from datetime import datetime
from typing import Callable, Optional, List
import traceback


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaStep:
    def __init__(self, name: str, action: Callable,
                 compensation: Callable):
        self.name = name
        self.action = action
        self.compensation = compensation
        self.status = StepStatus.PENDING
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def execute(self, context: dict) -> bool:
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()
        try:
            self.action(context)
            self.status = StepStatus.COMPLETED
            self.completed_at = datetime.now()
            return True
        except Exception as e:
            self.status = StepStatus.FAILED
            self.error = str(e)
            self.completed_at = datetime.now()
            return False

    def compensate(self, context: dict) -> bool:
        if self.status != StepStatus.COMPLETED:
            return True  # nothing to compensate

        self.status = StepStatus.COMPENSATING
        try:
            self.compensation(context)
            self.status = StepStatus.COMPENSATED
            return True
        except Exception as e:
            self.error = f"Compensation failed: {e}"
            return False


class SagaOrchestrator:
    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        self.steps: List[SagaStep] = []
        self.context: dict = {"saga_id": saga_id}
        self.status = "not_started"

    def add_step(self, name, action, compensation):
        self.steps.append(SagaStep(name, action, compensation))
        return self

    def execute(self) -> bool:
        print(f"\n{'=' * 55}")
        print(f"  Saga '{self.saga_id}' STARTING")
        print(f"{'=' * 55}")
        self.status = "running"
        completed_steps = []

        for i, step in enumerate(self.steps):
            print(f"\n  Step {i + 1}/{len(self.steps)}: {step.name}")

            if step.execute(self.context):
                completed_steps.append(step)
                print(f"  --> OK")
            else:
                print(f"  --> FAILED: {step.error}")
                print(f"\n  Starting compensation "
                      f"({len(completed_steps)} steps to undo)...")

                self.status = "compensating"
                for comp_step in reversed(completed_steps):
                    print(f"  Undoing: {comp_step.name}")
                    if comp_step.compensate(self.context):
                        print(f"  --> Undone")
                    else:
                        print(f"  --> UNDO FAILED: {comp_step.error}")

                self.status = "failed"
                print(f"\n{'=' * 55}")
                print(f"  Saga '{self.saga_id}' FAILED (compensated)")
                print(f"{'=' * 55}")
                self._print_status()
                return False

        self.status = "completed"
        print(f"\n{'=' * 55}")
        print(f"  Saga '{self.saga_id}' COMPLETED")
        print(f"{'=' * 55}")
        self._print_status()
        return True

    def _print_status(self):
        print(f"\n  Step Status:")
        for i, step in enumerate(self.steps):
            marker = {
                StepStatus.COMPLETED: "+",
                StepStatus.COMPENSATED: "~",
                StepStatus.FAILED: "X",
                StepStatus.PENDING: ".",
            }.get(step.status, "?")
            print(f"    [{marker}] {step.name}: {step.status.value}")


# --- Service Simulators ---

class CheckoutServices:
    def __init__(self):
        self.orders = {}
        self.inventory = {"SKU-001": 10, "SKU-002": 5, "SKU-003": 0}
        self.payments = {}
        self.shipments = {}
        self.emails_sent = []
        self.fail_payment = False

    # Order Service
    def create_order(self, ctx):
        order_id = ctx["saga_id"]
        self.orders[order_id] = {
            "status": "created",
            "items": ctx["items"],
            "total": ctx["total"]
        }
        print(f"    [Order] Created order {order_id}")

    def cancel_order(self, ctx):
        order_id = ctx["saga_id"]
        self.orders[order_id]["status"] = "cancelled"
        print(f"    [Order] Cancelled order {order_id}")

    # Inventory Service
    def reserve_inventory(self, ctx):
        for sku, qty in ctx["items"].items():
            available = self.inventory.get(sku, 0)
            if available < qty:
                raise Exception(
                    f"Out of stock: {sku} (need {qty}, have {available})")
            self.inventory[sku] -= qty
            print(f"    [Inventory] Reserved {qty}x {sku} "
                  f"(remaining: {self.inventory[sku]})")

    def release_inventory(self, ctx):
        for sku, qty in ctx["items"].items():
            self.inventory[sku] = self.inventory.get(sku, 0) + qty
            print(f"    [Inventory] Released {qty}x {sku} "
                  f"(remaining: {self.inventory[sku]})")

    # Payment Service
    def process_payment(self, ctx):
        if self.fail_payment:
            raise Exception("Payment declined: insufficient funds")
        order_id = ctx["saga_id"]
        self.payments[order_id] = {
            "amount": ctx["total"],
            "status": "charged"
        }
        print(f"    [Payment] Charged ${ctx['total']:.2f}")

    def refund_payment(self, ctx):
        order_id = ctx["saga_id"]
        if order_id in self.payments:
            self.payments[order_id]["status"] = "refunded"
            print(f"    [Payment] Refunded ${ctx['total']:.2f}")

    # Shipping Service
    def create_shipment(self, ctx):
        order_id = ctx["saga_id"]
        self.shipments[order_id] = {"status": "label_created"}
        print(f"    [Shipping] Created shipping label")

    def cancel_shipment(self, ctx):
        order_id = ctx["saga_id"]
        if order_id in self.shipments:
            self.shipments[order_id]["status"] = "cancelled"
            print(f"    [Shipping] Cancelled shipment")

    # Notification Service
    def send_confirmation(self, ctx):
        order_id = ctx["saga_id"]
        self.emails_sent.append(f"confirmation-{order_id}")
        print(f"    [Email] Sent order confirmation")

    def send_cancellation(self, ctx):
        order_id = ctx["saga_id"]
        self.emails_sent.append(f"cancellation-{order_id}")
        print(f"    [Email] Sent cancellation notice")


# --- Run Scenarios ---

services = CheckoutServices()

# Scenario 1: Successful checkout
saga1 = SagaOrchestrator("ORD-2001")
saga1.context.update({
    "items": {"SKU-001": 2, "SKU-002": 1},
    "total": 149.97,
    "customer": "alice@example.com"
})

(saga1
    .add_step("Create Order",
              services.create_order, services.cancel_order)
    .add_step("Reserve Inventory",
              services.reserve_inventory, services.release_inventory)
    .add_step("Process Payment",
              services.process_payment, services.refund_payment)
    .add_step("Create Shipment",
              services.create_shipment, services.cancel_shipment)
    .add_step("Send Confirmation",
              services.send_confirmation, services.send_cancellation))

saga1.execute()

# Scenario 2: Payment failure
print("\n" + "#" * 55)
print("  SCENARIO 2: Payment Failure")
print("#" * 55)

services.fail_payment = True

saga2 = SagaOrchestrator("ORD-2002")
saga2.context.update({
    "items": {"SKU-001": 1},
    "total": 49.99,
    "customer": "bob@example.com"
})

(saga2
    .add_step("Create Order",
              services.create_order, services.cancel_order)
    .add_step("Reserve Inventory",
              services.reserve_inventory, services.release_inventory)
    .add_step("Process Payment",
              services.process_payment, services.refund_payment)
    .add_step("Create Shipment",
              services.create_shipment, services.cancel_shipment))

saga2.execute()

# Verify inventory was restored
print(f"\n  Inventory after compensation: {services.inventory}")
```

**Output:**
```
=======================================================
  Saga 'ORD-2001' STARTING
=======================================================

  Step 1/5: Create Order
    [Order] Created order ORD-2001
  --> OK

  Step 2/5: Reserve Inventory
    [Inventory] Reserved 2x SKU-001 (remaining: 8)
    [Inventory] Reserved 1x SKU-002 (remaining: 4)
  --> OK

  Step 3/5: Process Payment
    [Payment] Charged $149.97
  --> OK

  Step 4/5: Create Shipment
    [Shipping] Created shipping label
  --> OK

  Step 5/5: Send Confirmation
    [Email] Sent order confirmation
  --> OK

=======================================================
  Saga 'ORD-2001' COMPLETED
=======================================================

  Step Status:
    [+] Create Order: completed
    [+] Reserve Inventory: completed
    [+] Process Payment: completed
    [+] Create Shipment: completed
    [+] Send Confirmation: completed

#######################################################
  SCENARIO 2: Payment Failure
#######################################################

=======================================================
  Saga 'ORD-2002' STARTING
=======================================================

  Step 1/4: Create Order
    [Order] Created order ORD-2002
  --> OK

  Step 2/4: Reserve Inventory
    [Inventory] Reserved 1x SKU-001 (remaining: 7)
  --> OK

  Step 3/4: Process Payment
  --> FAILED: Payment declined: insufficient funds

  Starting compensation (2 steps to undo)...
  Undoing: Reserve Inventory
    [Inventory] Released 1x SKU-001 (remaining: 8)
  --> Undone
  Undoing: Create Order
    [Order] Cancelled order ORD-2002
  --> Undone

=======================================================
  Saga 'ORD-2002' FAILED (compensated)
=======================================================

  Step Status:
    [~] Create Order: compensated
    [~] Reserve Inventory: compensated
    [X] Process Payment: failed
    [.] Create Shipment: pending

  Inventory after compensation: {'SKU-001': 8, 'SKU-002': 4, 'SKU-003': 0}
```

The inventory was correctly restored after the payment failure. The order was cancelled.
The system is back to a consistent state.

---

## Before vs After Comparison

### Before: No Saga (Inconsistent State on Failure)

```python
def checkout(order_data):
    create_order(order_data)        # succeeds
    reserve_inventory(order_data)   # succeeds
    charge_payment(order_data)      # FAILS!
    # Inventory is reserved but payment failed
    # Order exists but is invalid
    # No automatic cleanup
```

### After: Saga (Automatic Compensation)

```python
saga = SagaOrchestrator("order-123")
saga.add_step("Create Order", create_order, cancel_order)
saga.add_step("Reserve Inventory", reserve, release)
saga.add_step("Charge Payment", charge, refund)
saga.execute()
# If charge fails: inventory released, order cancelled automatically
```

---

## When to Use / When NOT to Use

### Use Saga When

- Business operations span multiple services or databases
- You need eventual consistency across service boundaries
- Operations have natural compensating actions
- The system must remain available even during partial failures
- You are building microservices that cannot share a database

### Do NOT Use Saga When

- All operations are within a single database (use ACID transactions)
- You need strict immediate consistency (Sagas provide eventual consistency)
- Compensating actions are impossible or meaningless
- The operation is simple (2 services, one call each)
- You can use a distributed transaction coordinator (like XA) and accept the
  performance cost

---

## Common Mistakes

### Mistake 1: Non-Idempotent Compensations

```python
# WRONG: calling refund twice charges the refund twice
def refund_payment(ctx):
    payment_service.refund(ctx["amount"])  # no idempotency check

# RIGHT: use idempotency keys
def refund_payment(ctx):
    refund_id = f"refund-{ctx['saga_id']}"
    if not payment_service.refund_exists(refund_id):
        payment_service.refund(ctx["amount"], idempotency_key=refund_id)
```

### Mistake 2: Ignoring Compensation Failures

```python
# WRONG: silently swallowing compensation errors
def compensate(self):
    try:
        self.compensation()
    except:
        pass  # hope for the best

# RIGHT: log, alert, and queue for retry
def compensate(self):
    try:
        self.compensation()
    except Exception as e:
        logger.critical(f"Compensation failed: {self.name}: {e}")
        alert_ops_team(self.name, e)
        dead_letter_queue.add(self)
```

### Mistake 3: Forward Compensation Order

```python
# WRONG: compensating in forward order
# Release inventory BEFORE cancelling shipment
# Shipment references the inventory reservation!

# RIGHT: compensate in REVERSE order
# 1. Cancel shipment (depends on inventory reservation)
# 2. Release inventory (now safe, no shipment depends on it)
# 3. Refund payment
# 4. Cancel order
```

---

## Best Practices

1. **Make compensations idempotent.** Network retries might trigger the same
   compensation multiple times. Use idempotency keys to prevent duplicate effects.

2. **Compensate in reverse order.** Later steps may depend on earlier steps. Undo the
   latest step first.

3. **Persist saga state.** Store the saga's progress in a database so it survives
   crashes. On restart, resume from where it left off.

4. **Use timeouts.** If a step does not respond within a timeout, treat it as failed
   and begin compensation.

5. **Log everything.** Sagas cross service boundaries, making debugging hard. Log every
   step, every compensation, and every context value.

6. **Handle compensation failures.** When a compensation fails, queue it for retry or
   alert for manual intervention. Never silently ignore failures.

7. **Start with orchestration.** Orchestration is easier to understand, test, and
   debug. Only use choreography when you need extreme decoupling.

---

## Quick Summary

The Saga pattern manages distributed transactions by breaking them into local
transactions with compensating actions. When a step fails, all previously completed
steps are undone in reverse order. Orchestration uses a central coordinator;
choreography uses events. Compensating transactions must be idempotent and always
succeed.

```
Problem:  Distributed operations lack ACID transactions.
Solution: Execute steps in sequence; compensate in reverse on failure.
Key:      Every forward action must have a compensating action.
```

---

## Key Points

- **Saga** manages distributed transactions across multiple services
- Each step has a **compensating transaction** to undo its effects on failure
- **Orchestration**: central coordinator drives the saga (recommended for most cases)
- **Choreography**: services react to events (simpler for 2-3 step sagas)
- Compensations execute in **reverse order** of the forward steps
- Compensations must be **idempotent** (safe to retry)
- Saga provides **eventual consistency**, not immediate consistency
- **Persist saga state** to survive service crashes and restarts
- Handle compensation failures with retries, dead letter queues, or manual intervention

---

## Practice Questions

1. Explain the difference between Choreography and Orchestration with a concrete
   example. When would you choose each?

2. A saga has 5 steps. Step 4 fails. Which steps need compensation and in what order?
   What about Step 4 itself?

3. Why must compensating transactions be idempotent? Give a concrete example of what
   goes wrong if they are not.

4. You have an e-commerce saga where step 3 (charge credit card) succeeds but step 4
   (reserve inventory) fails. The refund takes 3-5 business days. How do you handle
   the customer experience during this time?

5. How would you handle a scenario where the compensation itself fails? Describe three
   different strategies.

---

## Exercises

### Exercise 1: Travel Booking Saga

Build a travel booking saga with these steps:

- Book flight (compensation: cancel flight)
- Book hotel (compensation: cancel hotel)
- Book car rental (compensation: cancel rental)
- Charge payment (compensation: refund)
- Send confirmation email (compensation: send cancellation email)

Implement scenarios: all succeed, hotel unavailable, payment fails. Show that each
failure correctly compensates all previous steps.

### Exercise 2: Saga with Retries

Extend the SagaOrchestrator to support:

- Configurable retry count per step (e.g., retry payment up to 3 times)
- Exponential backoff between retries (1s, 2s, 4s)
- Only trigger compensation after all retries are exhausted
- Log each retry attempt
- Demonstrate with a step that fails twice then succeeds on the third try

### Exercise 3: Choreography-Based Saga

Implement the e-commerce checkout using choreography (event-driven) instead of
orchestration:

- Each service publishes events when it completes its work
- Each service listens for events and reacts
- Each service also listens for failure events and compensates
- No central orchestrator
- Track the order status across all services using a shared event log
- Compare the code complexity with the orchestration approach

---

## What Is Next?

The next chapter introduces the **API Gateway Pattern**, which provides a single entry
point for all client requests to your microservices. Where Saga coordinates transactions
across services, the API Gateway coordinates request routing, authentication, and rate
limiting. Both patterns are essential for building robust microservice architectures.
