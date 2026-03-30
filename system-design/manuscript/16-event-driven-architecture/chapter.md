# Chapter 16: Event-Driven Architecture

## What You Will Learn

- The difference between events and commands, and when to use each
- What event sourcing is and how it stores state as a sequence of events
- How CQRS separates reads from writes and why events make it powerful
- What an event bus and event broker are and how they differ
- Choreography vs orchestration: two ways to coordinate services
- The saga pattern for managing distributed transactions
- How eventual consistency works in event-driven systems
- Why idempotent consumers are critical and how to build them
- What dead letter queues do in event-driven pipelines
- How to design an order processing pipeline using events

## Why This Chapter Matters

Imagine a wedding. The bride and groom do not personally call every vendor to coordinate. They do not phone the florist, then the caterer, then the DJ one by one, waiting for each to confirm before calling the next. Instead, they send out invitations. Each vendor receives the invitation and independently prepares their part. The florist arranges flowers. The caterer prepares food. The DJ sets up music. Nobody waits for anyone else. Everyone reacts to the same event: "the wedding is happening."

This is event-driven architecture. Instead of services calling each other directly, they emit events: "order placed," "payment received," "item shipped." Other services listen for these events and react independently. This creates systems that are loosely coupled, highly scalable, and resilient to failure. In system design interviews, event-driven architecture shows up constantly because it is how real-world companies like Amazon, Uber, and Netflix handle millions of operations per second.

---

## Events vs Commands

The most fundamental concept in event-driven architecture is the difference between events and commands.

### What Is an Event?

An event is a record of something that **already happened**. It is a fact. It cannot be rejected. It uses past tense.

- `OrderPlaced` -- an order was placed
- `PaymentReceived` -- a payment was received
- `UserRegistered` -- a user signed up
- `ItemShipped` -- an item was shipped

Events are **immutable**. You cannot undo the fact that an order was placed. You can place a cancellation, but the original event still happened.

### What Is a Command?

A command is a **request** to do something. It has not happened yet. It can be accepted or rejected. It uses imperative tense.

- `PlaceOrder` -- please place this order
- `ProcessPayment` -- please process this payment
- `RegisterUser` -- please register this user
- `ShipItem` -- please ship this item

```
  Commands vs Events:

  COMMAND (Request)                    EVENT (Fact)
  +------------------+                +------------------+
  | PlaceOrder       |                | OrderPlaced      |
  | "Please do this" |    ------>     | "This happened"  |
  | Can be rejected  |                | Cannot be undone |
  | Imperative tense |                | Past tense       |
  +------------------+                +------------------+

  Flow:
  +---------+   Command    +---------+   Event      +---------+
  | Client  |  PlaceOrder  | Order   |  OrderPlaced | Payment |
  |         | -----------> | Service | -----------> | Service |
  +---------+              +---------+              +---------+
                                |
                                |  Event: OrderPlaced
                                v
                           +---------+
                           | Notif.  |
                           | Service |
                           +---------+

  The command goes TO a specific service.
  The event goes FROM a service to anyone listening.
```

### Key Differences

| Aspect | Command | Event |
|---|---|---|
| Direction | Sent TO a specific service | Broadcast FROM a service |
| Tense | Imperative (do this) | Past tense (this happened) |
| Can be rejected? | Yes | No (it already happened) |
| Coupling | Sender knows the receiver | Sender does not know who listens |
| Cardinality | One sender, one receiver | One sender, many receivers |

### When to Use Each

Use **commands** when you need a specific service to do something and you care about the result. Use **events** when you want to notify the rest of the system that something happened and let each service decide how to react.

---

## Event Sourcing

### The Traditional Approach: Storing Current State

In a traditional system, you store the current state of an entity. When something changes, you update the record in place.

```
  Traditional State Storage:

  User places order:    UPDATE orders SET status = 'placed'    WHERE id = 123
  Payment received:     UPDATE orders SET status = 'paid'      WHERE id = 123
  Item shipped:         UPDATE orders SET status = 'shipped'   WHERE id = 123

  Database at any time:
  +----+--------+---------+
  | id | amount | status  |
  +----+--------+---------+
  | 123| $49.99 | shipped |  <-- Only the current state
  +----+--------+---------+

  Question: When was the payment received? How long between
  placing the order and shipping? What was the original address
  before the customer changed it?

  Answer: You do not know. The history is gone.
```

### The Event Sourcing Approach: Storing Events

With event sourcing, you never update or delete records. Instead, you store every event that happened to an entity. The current state is derived by replaying all events.

Think of it like a bank account. Your bank does not just store your current balance. It stores every transaction: every deposit, every withdrawal, every transfer. Your balance is the result of replaying all those transactions from the beginning.

```
  Event Sourcing Storage:

  Event Store for Order #123:
  +----+---------------------+----------------------------------+
  | #  | Event Type          | Data                             |
  +----+---------------------+----------------------------------+
  | 1  | OrderCreated        | {id:123, items:[...], total:49.99}|
  | 2  | PaymentReceived     | {id:123, method:"visa", at:"10:01"}|
  | 3  | AddressChanged      | {id:123, new:"456 Oak St"}       |
  | 4  | ItemPicked          | {id:123, warehouse:"WH-East"}    |
  | 5  | ItemShipped         | {id:123, carrier:"FedEx"}        |
  +----+---------------------+----------------------------------+

  Current state = replay events 1 through 5

  Now you know:
  - When payment was received (event #2, 10:01 AM)
  - The original address before the change
  - Which warehouse picked the item
  - The complete history of everything that happened
```

### How Replay Works

To get the current state of an entity, you start with an empty state and apply each event in order.

```
  Rebuilding State from Events:

  Start:   {}
  Event 1: OrderCreated    --> {id:123, status:"created", total:49.99}
  Event 2: PaymentReceived --> {id:123, status:"paid", total:49.99}
  Event 3: AddressChanged  --> {id:123, status:"paid", address:"456 Oak St"}
  Event 4: ItemPicked      --> {id:123, status:"picking", warehouse:"WH-East"}
  Event 5: ItemShipped     --> {id:123, status:"shipped", carrier:"FedEx"}

  Final state: {id:123, status:"shipped", total:49.99,
                address:"456 Oak St", warehouse:"WH-East",
                carrier:"FedEx"}
```

### Benefits of Event Sourcing

1. **Complete audit trail.** You know exactly what happened, when, and in what order. This is critical for financial systems, healthcare, and compliance.
2. **Time travel.** You can rebuild the state of any entity at any point in time by replaying events up to that moment.
3. **Debugging.** When something goes wrong, you can replay the exact sequence of events that caused the bug.
4. **New projections.** When you add a new feature that needs historical data, you can replay all events to build new views. No backfilling needed.

### Challenges of Event Sourcing

1. **Complexity.** It is a fundamentally different way of thinking about data. Most developers are trained to think in terms of current state.
2. **Event schema evolution.** What happens when you need to change the structure of an event? You still need to be able to replay old events.
3. **Performance.** Replaying thousands of events to rebuild state can be slow. You solve this with **snapshots**: periodically save the current state so you only need to replay events after the snapshot.

```
  Snapshots for Performance:

  Without snapshots: Replay all 10,000 events  (SLOW)

  Event 1 -> Event 2 -> ... -> Event 10,000
  |<------------- Replay all ------------->|

  With snapshots: Replay only events after the snapshot (FAST)

  Event 1 -> ... -> Event 9,500 -> [SNAPSHOT] -> Event 9,501 -> ... -> 10,000
                                   |<---- Replay only 500 events ---->|
```

---

## CQRS: Command Query Responsibility Segregation

CQRS is a pattern that separates the read side (queries) from the write side (commands) of your application. It pairs naturally with event sourcing.

### The Problem with a Single Model

In a traditional application, you use the same database tables for both reading and writing. But reads and writes have very different requirements.

- **Writes** need strong consistency, validation, and business rules.
- **Reads** need speed, denormalized data, and flexible queries.

Trying to optimize the same model for both creates compromises. Your write model becomes bloated with read-specific columns. Your read queries become slow because the data is normalized for writes.

### How CQRS Works

CQRS splits your system into two sides.

```
  CQRS Architecture:

                          +-------------------+
                          |                   |
           Commands       |   WRITE MODEL     |
  User  ----------------> |   (Command Side)  |
                          |                   |
                          | - Validates       |
                          | - Enforces rules  |
                          | - Stores events   |
                          +--------+----------+
                                   |
                                   | Events published
                                   v
                          +-------------------+
                          |   EVENT BUS       |
                          +--------+----------+
                                   |
                                   v
                          +-------------------+
                          |                   |
           Queries        |   READ MODEL      |
  User  <---------------- |   (Query Side)    |
                          |                   |
                          | - Denormalized    |
                          | - Fast queries    |
                          | - Multiple views  |
                          +-------------------+

  Write Side:                    Read Side:
  - Normalized tables            - Denormalized views
  - Complex validation           - Simple lookups
  - Event store                  - Optimized for queries
  - Strong consistency           - Eventually consistent
```

### CQRS with Events

When the write side processes a command, it emits events. The read side listens for those events and updates its denormalized views.

```
  CQRS + Event Sourcing Flow:

  1. User sends command: PlaceOrder(items, address)

  2. Write side:
     - Validates order
     - Checks inventory
     - Stores event: OrderPlaced

  3. Event bus delivers OrderPlaced to:
     - Read model updater (updates order dashboard)
     - Inventory service (reserves items)
     - Email service (sends confirmation)

  4. User queries the read side:
     - GET /orders/123
     - Returns denormalized order with items, status, tracking
     - Served from a read-optimized store (Redis, Elasticsearch)
```

### When to Use CQRS

CQRS adds complexity. Use it when:

- Read and write patterns are very different (many more reads than writes, or vice versa)
- You need different data models for querying (search, analytics, dashboards)
- You need to scale reads and writes independently
- You are already using event sourcing

Do **not** use CQRS for simple CRUD applications. It is overkill.

---

## Event Bus and Event Broker

An event bus or event broker is the infrastructure that transports events from producers to consumers.

### Event Bus (In-Process)

An event bus is a lightweight, often in-process mechanism for routing events. Think of it as a bulletin board in an office. Someone pins a notice, and everyone who checks the board sees it.

```
  Event Bus (Simple):

  +-----------+                   +-----------+
  | Service A |---+               | Handler 1 |
  +-----------+   |   +-------+  +-----------+
                  +-->|       |-->|           |
  +-----------+   |   | EVENT |  | Handler 2 |
  | Service B |---+   |  BUS  |  +-----------+
  +-----------+       |       |-->|           |
                      +-------+  | Handler 3 |
                                 +-----------+

  - In-process or single-application
  - No persistence (events lost if app crashes)
  - Simple, fast, no external dependencies
  - Examples: MediatR (.NET), Guava EventBus (Java)
```

### Event Broker (Distributed)

An event broker is a dedicated infrastructure component that stores and routes events between distributed services. It persists events, guarantees delivery, and handles retries.

```
  Event Broker (Distributed):

  +-----------+                              +-----------+
  | Order     |---+                     +--->| Payment   |
  | Service   |   |   +-------------+  |    | Service   |
  +-----------+   +-->|             |--+     +-----------+
                  |   |   EVENT     |  |
  +-----------+   |   |   BROKER    |  |     +-----------+
  | User      |---+   |             |--+---->| Inventory |
  | Service   |       | (Kafka,     |  |     | Service   |
  +-----------+       |  RabbitMQ,  |  |     +-----------+
                      |  Pulsar)    |  |
                      +-------------+  |     +-----------+
                                       +---->| Email     |
                                             | Service   |
                                             +-----------+

  - Distributed, runs as separate infrastructure
  - Persists events (can replay)
  - Guarantees delivery (at-least-once)
  - Handles retries, dead letter queues
  - Scales independently
```

### Event Bus vs Event Broker

| Feature | Event Bus | Event Broker |
|---|---|---|
| Deployment | In-process | Separate infrastructure |
| Persistence | No (in-memory) | Yes (disk) |
| Delivery guarantee | None (best-effort) | At-least-once or exactly-once |
| Replay | No | Yes (Kafka) |
| Scaling | Scales with the app | Scales independently |
| Use case | Simple apps, monoliths | Microservices, distributed systems |

---

## Choreography vs Orchestration

When multiple services need to collaborate to complete a business process, there are two approaches: choreography and orchestration.

### Choreography: Everyone Dances Independently

In choreography, there is no central coordinator. Each service listens for events and decides what to do next. It is like a dance where everyone knows the steps and reacts to the music independently.

```
  Choreography (Order Processing):

  1. Order Service emits: OrderPlaced
  2. Payment Service hears OrderPlaced --> processes payment
  3. Payment Service emits: PaymentReceived
  4. Inventory Service hears PaymentReceived --> reserves items
  5. Inventory Service emits: ItemsReserved
  6. Shipping Service hears ItemsReserved --> ships order
  7. Shipping Service emits: OrderShipped
  8. Notification Service hears OrderShipped --> notifies customer

  +-------+     +-------+     +---------+     +--------+     +--------+
  | Order |     |Payment|     |Inventory|     |Shipping|     | Notif. |
  +---+---+     +---+---+     +----+----+     +---+----+     +---+----+
      |             |              |              |              |
      | OrderPlaced |              |              |              |
      +------------>|              |              |              |
      |             |              |              |              |
      |             |PaymentRecvd  |              |              |
      |             +------------->|              |              |
      |             |              |              |              |
      |             |              |ItemsReserved |              |
      |             |              +------------->|              |
      |             |              |              |              |
      |             |              |              |OrderShipped  |
      |             |              |              +------------->|
      |             |              |              |              |

  No central coordinator. Each service reacts to events.
```

**Pros:**
- Loose coupling. Each service only knows about events, not other services.
- Easy to add new services. Just subscribe to events.
- No single point of failure.

**Cons:**
- Hard to understand the full business flow. Logic is spread across services.
- Hard to debug. You need to trace events across multiple services.
- Hard to handle failures. What if the payment succeeds but inventory reservation fails?

### Orchestration: One Conductor Leads

In orchestration, a central coordinator (the orchestrator) tells each service what to do and when. It is like an orchestra conductor directing each musician.

```
  Orchestration (Order Processing):

  The Order Orchestrator controls the flow:

  +-------------------------------------------------------------+
  |                   ORDER ORCHESTRATOR                          |
  |                                                              |
  |  Step 1: Call Payment Service --> ProcessPayment             |
  |  Step 2: Call Inventory Service --> ReserveItems             |
  |  Step 3: Call Shipping Service --> ShipOrder                 |
  |  Step 4: Call Notification Service --> NotifyCustomer        |
  |                                                              |
  |  If Step 2 fails: Call Payment Service --> RefundPayment     |
  +-------------------------------------------------------------+
        |            |             |             |
        v            v             v             v
  +---------+  +---------+  +---------+  +---------+
  | Payment |  |Inventory|  | Shipping|  | Notif.  |
  | Service |  | Service |  | Service |  | Service |
  +---------+  +---------+  +---------+  +---------+

  The orchestrator knows the entire flow and handles failures.
```

**Pros:**
- Easy to understand. The entire business flow is in one place.
- Easy to handle failures. The orchestrator knows what to undo.
- Easy to test. Test the orchestrator to test the flow.

**Cons:**
- Tight coupling to the orchestrator. It becomes a single point of failure.
- The orchestrator can become a "god service" that knows too much.
- Harder to scale. The orchestrator must handle all coordination.

### Which to Choose?

| Aspect | Choreography | Orchestration |
|---|---|---|
| Coupling | Low (services independent) | Higher (depends on orchestrator) |
| Visibility | Low (distributed logic) | High (centralized logic) |
| Failure handling | Complex (distributed compensation) | Simple (orchestrator manages) |
| Scalability | High (no bottleneck) | Moderate (orchestrator is bottleneck) |
| Best for | Simple flows, high scale | Complex flows, many failure cases |

In practice, many systems use a **hybrid approach**: orchestration for complex workflows and choreography for simple event notifications.

---

## The Saga Pattern

When a business process spans multiple services, you cannot use a traditional database transaction. The saga pattern is a way to manage distributed transactions using a sequence of local transactions coordinated by events.

### The Problem

Consider an e-commerce order:
1. Charge the customer (Payment Service)
2. Reserve inventory (Inventory Service)
3. Schedule delivery (Shipping Service)

In a monolith, you would wrap all three in a single database transaction. If any step fails, everything rolls back. In microservices, there is no such thing as a distributed transaction (at least not a practical one).

### How Sagas Work

A saga breaks the transaction into a series of steps. Each step has a **compensating action** -- something that undoes the step if a later step fails.

```
  Saga: Order Processing

  Step 1: Charge Payment
    Compensating action: Refund Payment

  Step 2: Reserve Inventory
    Compensating action: Release Inventory

  Step 3: Schedule Delivery
    Compensating action: Cancel Delivery

  Happy Path:
  Charge --> Reserve --> Schedule --> SUCCESS

  Failure at Step 3:
  Charge --> Reserve --> Schedule (FAILS!)
                  |
                  v
         Release Inventory (compensate step 2)
                  |
                  v
         Refund Payment (compensate step 1)
                  |
                  v
               FAILED (customer notified)
```

### Choreography-Based Saga

Each service listens for events and triggers the next step or compensating action.

```
  Choreography-Based Saga:

  +----------+   OrderPlaced    +----------+   PaymentCharged   +-----------+
  |  Order   | --------------> | Payment  | -----------------> | Inventory |
  |  Service |                 | Service  |                    | Service   |
  +----------+                 +----------+                    +-----------+
                                    |                               |
                               PaymentFailed                   ReservationFailed
                                    |                               |
                                    v                               v
                              Order Cancelled              Refund Payment
                                                           Release Inventory
                                                           Order Cancelled
```

### Orchestration-Based Saga

A central saga orchestrator manages the steps and compensations.

```
  Orchestration-Based Saga:

  +----------------------------------------------------------+
  |                  SAGA ORCHESTRATOR                         |
  |                                                           |
  |  State Machine:                                           |
  |                                                           |
  |  PENDING --> CHARGING --> RESERVING --> SCHEDULING --> DONE|
  |     |           |            |              |              |
  |     v           v            v              v              |
  |  CANCELLED  REFUNDING   RELEASING      CANCELLING          |
  +----------------------------------------------------------+
       |           |            |              |
       v           v            v              v
  +---------+ +---------+ +---------+    +---------+
  | Payment | |Inventory| | Shipping|    | Notif.  |
  +---------+ +---------+ +---------+    +---------+
```

---

## Eventual Consistency

In event-driven systems, services do not update simultaneously. After an event is published, it takes time for all consumers to process it. During this window, different parts of the system have different views of the data. This is **eventual consistency**.

### How It Feels to the User

```
  Eventual Consistency Timeline:

  Time 0: User places order
  Time 1: Order Service stores order         (Order: "placed")
  Time 2: Event "OrderPlaced" published
  Time 3: Payment Service receives event     (Payment: "none" -> "processing")
  Time 4: Inventory Service receives event   (Inventory: "available")
  Time 5: Payment processed                  (Payment: "charged")
  Time 6: Inventory reserved                 (Inventory: "reserved")

  Between Time 2 and Time 6, different services show
  different states. The system is temporarily inconsistent.

  Eventually (by Time 6), everything is consistent.

  +---------+  +---------+  +---------+
  | Order:  |  | Payment:|  | Invent.:|
  | placed  |  | charged |  | reserved|
  +---------+  +---------+  +---------+
       All consistent (eventually)
```

### Dealing with Eventual Consistency

1. **Design UIs to show pending states.** Show "Processing..." instead of assuming instant updates.
2. **Use read-your-own-writes.** After a user creates something, route their next read to the write model so they see their own change immediately.
3. **Set expectations.** Tell users "Your order is being processed" rather than pretending it is instant.

---

## Idempotent Consumers

In an event-driven system with at-least-once delivery (which is the most common guarantee), your consumers **will** receive duplicate events. Network glitches, retries, and broker redeliveries all cause duplicates.

An **idempotent consumer** produces the same result whether it processes an event once or ten times.

### Why This Matters

```
  Without Idempotency:

  Event: PaymentReceived {orderId: 123, amount: $50}

  Delivery 1: Charge customer $50    (Total: $50)  CORRECT
  Delivery 2: Charge customer $50    (Total: $100) WRONG!
  Delivery 3: Charge customer $50    (Total: $150) VERY WRONG!

  With Idempotency:

  Event: PaymentReceived {orderId: 123, amount: $50, eventId: "evt-abc"}

  Delivery 1: Check "evt-abc" processed? No.  Charge $50.  Record "evt-abc".
  Delivery 2: Check "evt-abc" processed? Yes. Skip.
  Delivery 3: Check "evt-abc" processed? Yes. Skip.

  Total charged: $50 (CORRECT, no matter how many deliveries)
```

### Strategies for Idempotency

1. **Event ID deduplication.** Store processed event IDs. Before processing, check if the ID already exists.

2. **Natural idempotency.** Some operations are naturally idempotent. Setting a status to "shipped" is the same whether you do it once or five times.

3. **Idempotency keys.** Use a unique key (like order ID + event type) to ensure each logical operation happens exactly once.

```
  Idempotent Consumer Pattern:

  +------------------+
  |  Receive Event   |
  +--------+---------+
           |
           v
  +------------------+
  | Check: eventId   |
  | in processed_set?|
  +--------+---------+
           |
      +----+----+
      |         |
     YES        NO
      |         |
      v         v
  +-------+  +------------------+
  | SKIP  |  | Process Event    |
  | (ack) |  | Store eventId    |
  +-------+  | in processed_set |
             | ACK to broker    |
             +------------------+
```

---

## Dead Letter Queues in Event-Driven Systems

A dead letter queue (DLQ) is a special queue where events go when they cannot be processed after multiple retries. It is your safety net for events that would otherwise be lost or block the pipeline.

### When Events End Up in the DLQ

```
  Event Processing with DLQ:

  +---------+     +--------+     +-----------+
  | Event   |---->| Event  |---->| Consumer  |
  | Source  |     | Broker |     |           |
  +---------+     +--------+     +-----------+
                      |               |
                      |          Retry 1: FAIL
                      |          Retry 2: FAIL
                      |          Retry 3: FAIL
                      |               |
                      |               v
                      |         +----------+
                      |         |   DLQ    |
                      |         | (Dead    |
                      |         |  Letter  |
                      |         |  Queue)  |
                      |         +----------+
                      |               |
                      |               v
                      |         Alert! Engineers
                      |         investigate and
                      |         reprocess manually

  Common reasons for DLQ:
  - Malformed event data (missing required fields)
  - Consumer bug (null pointer, logic error)
  - Downstream service permanently unavailable
  - Schema mismatch (producer updated, consumer did not)
```

### Best Practices for DLQs

1. **Always configure a DLQ.** Never let failed events disappear silently.
2. **Set a reasonable retry count** (3 to 5 retries with exponential backoff).
3. **Monitor DLQ depth.** A growing DLQ means something is wrong.
4. **Build a reprocessing tool.** After fixing the issue, you need a way to move events from the DLQ back to the main queue.
5. **Include metadata.** Store the failure reason, retry count, and original timestamp with each DLQ event.

---

## Order Processing Pipeline: Putting It All Together

Let us design a complete order processing pipeline using event-driven architecture.

```
  Order Processing Pipeline:

  +--------+   PlaceOrder   +---------+  OrderPlaced  +----------+
  | Client | -------------> |  Order  | ------------> | Event    |
  |  (App) |   (command)    | Service |   (event)     | Broker   |
  +--------+                +---------+               +-----+----+
                                                            |
                    +---------------------------------------+
                    |                |               |
                    v                v               v
              +-----------+   +-----------+   +-----------+
              |  Payment  |   | Inventory |   |   Email   |
              |  Service  |   |  Service  |   |  Service  |
              +-----------+   +-----------+   +-----------+
                    |                |               |
           PaymentCharged    ItemsReserved    ConfirmationSent
                    |                |
                    v                v
              +----------+    +----------+
              | Event    |    | Event    |
              | Broker   |    | Broker   |
              +-----+----+    +-----+----+
                    |                |
                    v                v
              +-----------+   +-----------+
              | Shipping  |   | Analytics |
              |  Service  |   |  Service  |
              +-----------+   +-----------+
                    |
              OrderShipped
                    |
                    v
              +-----------+
              |   Push    |
              |  Notif.   |
              |  Service  |
              +-----------+


  Detailed Event Flow:

  Step 1: Client sends PlaceOrder command to Order Service
  Step 2: Order Service validates and stores order
  Step 3: Order Service emits OrderPlaced event
  Step 4: Payment Service listens, charges customer
  Step 5: Payment Service emits PaymentCharged
  Step 6: Inventory Service listens, reserves items
  Step 7: Inventory Service emits ItemsReserved
  Step 8: Shipping Service listens, schedules shipment
  Step 9: Shipping Service emits OrderShipped
  Step 10: Notification Service sends push notification

  Failure Handling (Saga):
  - If payment fails: emit PaymentFailed, cancel order
  - If inventory fails: emit ReservationFailed, refund payment
  - If shipping fails: emit ShippingFailed, release inventory, refund
```

### The Event Store for This Pipeline

```
  Event Store (Order #789):

  +----+--------------------+------+---------------------------------------+
  | #  | Timestamp          | Type | Data                                  |
  +----+--------------------+------+---------------------------------------+
  | 1  | 2024-01-15 10:00:01| OrderPlaced    | {items: [...], total: $129} |
  | 2  | 2024-01-15 10:00:03| PaymentCharged | {method: "visa_4242"}       |
  | 3  | 2024-01-15 10:00:04| ItemsReserved  | {warehouse: "US-East"}      |
  | 4  | 2024-01-15 10:00:10| OrderShipped   | {tracking: "FX123456"}      |
  | 5  | 2024-01-15 10:00:11| CustomerNotified| {channel: "push+email"}    |
  +----+--------------------+------+---------------------------------------+

  Complete audit trail. You can:
  - Replay to any point in time
  - Debug any issue
  - Build new reports from historical events
  - Prove compliance to auditors
```

---

## Trade-offs

| Decision | Option A | Option B |
|---|---|---|
| Architecture | Request-response (simple, synchronous) | Event-driven (complex, async, scalable) |
| Coordination | Choreography (decoupled, hard to debug) | Orchestration (centralized, easier to debug) |
| State storage | Current state (simple, fast reads) | Event sourcing (audit trail, complex, replay) |
| Read/write model | Single model (simple, consistent) | CQRS (optimized, eventually consistent) |
| Consistency | Strong (immediate, slower) | Eventual (fast, temporary inconsistency) |
| Delivery | At-most-once (fast, may lose events) | At-least-once (safe, needs idempotency) |

---

## Common Mistakes

1. **Using event-driven architecture for everything.** Simple CRUD operations do not need events. If a user updates their profile name, a direct database update is fine. Reserve events for cross-service communication and important business state changes.

2. **Not making consumers idempotent.** This is the number one source of bugs in event-driven systems. Every consumer must handle duplicate events gracefully.

3. **Ignoring event ordering.** Events for the same entity should be processed in order. If `OrderShipped` arrives before `OrderPlaced`, your system will be confused. Use partition keys (like order ID) to ensure ordering within an entity.

4. **Creating event chains that are too long.** If Service A triggers B, which triggers C, which triggers D, which triggers E, a failure anywhere creates a complex debugging puzzle. Keep event chains short or use an orchestrator for complex workflows.

5. **Not versioning events.** When you change the structure of an event, old consumers will break. Always version your events (e.g., `OrderPlaced_v2`) and support backward compatibility.

6. **Skipping the dead letter queue.** Without a DLQ, failed events either block the pipeline or disappear silently. Both are unacceptable in production.

---

## Best Practices

1. **Start with commands, evolve to events.** Begin with direct service-to-service calls. When you see a need for decoupling, introduce events for that specific flow.

2. **Use unique event IDs.** Every event should have a globally unique ID (UUID) for deduplication and tracing.

3. **Include metadata in events.** Every event should carry: event ID, timestamp, source service, correlation ID (to trace across services), and schema version.

4. **Design events as contracts.** Treat event schemas like API contracts. Use schema registries (like Confluent Schema Registry) to manage compatibility.

5. **Keep events small.** Include only the essential data in the event. If consumers need more detail, they can query the source service. This is called the "thin event" approach.

6. **Use correlation IDs.** When an event triggers a chain of downstream events, carry a correlation ID through the entire chain so you can trace the full flow.

7. **Monitor consumer lag.** Track how far behind each consumer is. A growing lag means the consumer cannot keep up with the event rate.

8. **Test with chaos.** Simulate failures, duplicate deliveries, and out-of-order events in your test environment to verify your system handles them correctly.

---

## Quick Summary

Event-driven architecture builds systems around events: immutable records of things that happened. Events differ from commands: commands request action, events report facts. Event sourcing stores state as a sequence of events, giving you a complete audit trail and the ability to replay history. CQRS separates read and write models, optimizing each independently. Events flow through an event bus (in-process) or event broker (distributed like Kafka). Choreography lets services react independently to events; orchestration uses a central coordinator. The saga pattern manages distributed transactions through compensating actions. Eventual consistency means different services may temporarily have different views of the data. Idempotent consumers are critical because at-least-once delivery means duplicates will happen. Dead letter queues catch events that cannot be processed after retries.

---

## Key Points

- Events are immutable facts about what happened; commands are requests that can be rejected
- Event sourcing stores every change as an event, enabling audit trails and time travel
- CQRS separates read and write models for independent optimization
- Choreography offers loose coupling; orchestration offers centralized control and easier debugging
- The saga pattern replaces distributed transactions with local transactions and compensating actions
- Eventual consistency is the trade-off for decoupling and scalability
- Idempotent consumers are not optional -- they are required for correctness
- Dead letter queues are your safety net for events that cannot be processed

---

## Practice Questions

1. Your e-commerce platform uses event sourcing for orders. After one year, each order has an average of 50 events. Rebuilding order state is taking 200 milliseconds. Your SLA requires responses under 50 milliseconds. How would you solve this?

2. You are building a food delivery app. When a customer places an order, you need to: validate the order, charge payment, notify the restaurant, and assign a driver. Should you use choreography or orchestration? Justify your answer considering failure scenarios.

3. Your payment service processes `PaymentCharged` events. Due to a network glitch, the same event is delivered three times. Your current implementation charges the customer three times. How would you redesign the consumer to be idempotent?

4. You are designing a system where the order service and the inventory service need to stay in sync. A customer places an order, but by the time the inventory service processes the event, the item is out of stock. How would you handle this using the saga pattern? What compensating actions are needed?

5. Your dead letter queue has 50,000 events from the last 24 hours. All of them are `OrderPlaced` events that failed in the inventory service. What is your investigation and recovery plan?

---

## Exercises

**Exercise 1: Design an Event-Driven Notification System**

Design the event flow for a social media application. When a user posts a photo, the following must happen: generate thumbnails, scan for inappropriate content, notify followers, update the news feed, and update the user's post count. Draw the architecture showing events, services, and the event broker. Identify which steps can happen in parallel and which must be sequential.

**Exercise 2: Implement a Saga for Hotel Booking**

Design a saga for a travel booking system. When a customer books a trip, you need to: reserve a flight, reserve a hotel, and reserve a rental car. Define the compensating action for each step. Draw the saga flow for both the happy path and a failure at each step. Choose between choreography-based and orchestration-based saga and justify your choice.

**Exercise 3: Event Schema Evolution**

You have an `OrderPlaced` event with the following schema: `{orderId, customerId, items[], total}`. The business now requires you to add a `currency` field and split `total` into `subtotal`, `tax`, and `total`. Design a migration strategy that does not break existing consumers. Consider versioning, backward compatibility, and how you would handle replaying old events.

---

## What Is Next?

You now understand how services communicate through events, how to store state as events, and how to manage distributed transactions with sagas. But modern systems deal with more than structured data flowing between services. Users upload photos, videos, and documents. These large binary objects need a completely different storage approach. In the next chapter, you will learn about blob storage: how systems like S3 store files at scale, how to integrate with CDNs for fast delivery, and how platforms like Instagram handle millions of image uploads per day.
