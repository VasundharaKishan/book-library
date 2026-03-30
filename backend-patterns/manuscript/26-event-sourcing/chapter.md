# Chapter 26: Event Sourcing

## What You Will Learn

- What Event Sourcing is and how it differs from traditional state storage
- How to store events instead of current state
- How to rebuild current state from a sequence of events
- How to use snapshots for performance optimization
- How to implement event sourcing for a bank account in Java
- How Event Sourcing combines with CQRS
- Real-world applications in financial systems and audit trails
- The complexity trade-offs of adopting Event Sourcing

## Why This Chapter Matters

Traditional databases store only the current state of your data. When a bank account has a balance of $500, that is all you know. You do not know if the customer deposited $1000 and then withdrew $500, or if they received five $100 deposits. The history is lost.

Event Sourcing flips this approach. Instead of storing the current state, you store every event that happened: "Account Created," "Money Deposited $1000," "Money Withdrawn $500." The current state is derived by replaying these events. You never lose history. You can answer questions like "what was the balance on March 15th?" or "how many deposits did this customer make last quarter?"

This is not just about history. Event Sourcing enables powerful capabilities: complete audit trails, temporal queries, debugging by replaying events, and undo operations. Financial systems, healthcare platforms, and compliance-heavy applications use Event Sourcing because the law often requires a complete record of every change.

---

## The Problem

### Traditional State Storage

```
Traditional approach: Only the CURRENT state is stored

  Time 0:  Account created with $0        DB: balance = 0
  Time 1:  Deposit $1000                  DB: balance = 1000
  Time 2:  Withdraw $200                  DB: balance = 800
  Time 3:  Deposit $500                   DB: balance = 1300
  Time 4:  Withdraw $100                  DB: balance = 1200

  What the database knows:  balance = 1200
  What is lost:  HOW we got to 1200

  Questions you CANNOT answer:
    - What was the balance at Time 2?
    - How many deposits were made?
    - What was the largest withdrawal?
    - Did anyone modify the balance directly?
```

### Before: State-Based Updates

```java
// Traditional approach: update state directly
@Entity
public class BankAccount {
    @Id private Long id;
    private String owner;
    private BigDecimal balance;

    public void deposit(BigDecimal amount) {
        this.balance = this.balance.add(amount);
        // Previous balance is GONE
    }

    public void withdraw(BigDecimal amount) {
        if (amount.compareTo(this.balance) > 0) {
            throw new InsufficientFundsException();
        }
        this.balance = this.balance.subtract(amount);
        // No record of this withdrawal
    }
}
```

---

## The Solution: Event Sourcing

Instead of storing state, store the events that produce that state.

```
Event Sourcing approach: Store EVERY event

  Event Store:
  +-----+-------------------+-------------------+----------+
  | Seq |   Event Type      |   Data            | Timestamp|
  +-----+-------------------+-------------------+----------+
  |  1  | AccountCreated    | owner: "Alice"    | 10:00:00 |
  |  2  | MoneyDeposited    | amount: 1000      | 10:05:00 |
  |  3  | MoneyWithdrawn    | amount: 200       | 10:10:00 |
  |  4  | MoneyDeposited    | amount: 500       | 11:00:00 |
  |  5  | MoneyWithdrawn    | amount: 100       | 11:30:00 |
  +-----+-------------------+-------------------+----------+

  To get current state: REPLAY all events
    Start:   balance = 0
    Event 1: AccountCreated    -> balance = 0
    Event 2: MoneyDeposited    -> balance = 0 + 1000 = 1000
    Event 3: MoneyWithdrawn    -> balance = 1000 - 200 = 800
    Event 4: MoneyDeposited    -> balance = 800 + 500 = 1300
    Event 5: MoneyWithdrawn    -> balance = 1300 - 100 = 1200

  Current balance: 1200 (same result, but with FULL history)
```

---

## How Event Sourcing Works

```
+-------------------+       +-------------------+       +-----------------+
|                   |       |                   |       |                 |
|  Command          | ----> |  Domain Logic     | ----> |  Event Store    |
|  "Deposit $500"   |       |  (Validate +      |       |  (Append Only)  |
|                   |       |   Generate Event)  |       |                 |
+-------------------+       +-------------------+       +-----------------+
                                                                |
                                                                v
                                                        +-------+-------+
                                                        |  Event 1      |
                                                        |  Event 2      |
                                                        |  Event 3      |
                                                        |  ...          |
                                                        |  Event N      |
                                                        +---------------+
                                                                |
                                                        Replay  |
                                                                v
                                                        +---------------+
                                                        | Current State |
                                                        | balance: 1200 |
                                                        +---------------+
```

Key principles:

1. **Events are immutable** -- once stored, they never change
2. **Events are append-only** -- you only add new events, never delete old ones
3. **State is derived** -- current state is computed by replaying events
4. **Events capture intent** -- "MoneyDeposited" not "BalanceUpdated"

---

## Java Implementation: Bank Account Event Sourcing

### Step 1: Define Events

```java
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

// Base event
public abstract class DomainEvent {
    private final String eventId;
    private final String aggregateId;
    private final Instant timestamp;
    private final int version;

    protected DomainEvent(String aggregateId, int version) {
        this.eventId = UUID.randomUUID().toString();
        this.aggregateId = aggregateId;
        this.timestamp = Instant.now();
        this.version = version;
    }

    public String getEventId() { return eventId; }
    public String getAggregateId() { return aggregateId; }
    public Instant getTimestamp() { return timestamp; }
    public int getVersion() { return version; }
}

// Concrete events
public class AccountCreatedEvent extends DomainEvent {
    private final String owner;
    private final BigDecimal initialBalance;

    public AccountCreatedEvent(String aggregateId, int version,
                                String owner, BigDecimal initialBalance) {
        super(aggregateId, version);
        this.owner = owner;
        this.initialBalance = initialBalance;
    }

    public String getOwner() { return owner; }
    public BigDecimal getInitialBalance() { return initialBalance; }

    @Override
    public String toString() {
        return String.format("AccountCreated{owner='%s', balance=%s}",
                             owner, initialBalance);
    }
}

public class MoneyDepositedEvent extends DomainEvent {
    private final BigDecimal amount;
    private final String description;

    public MoneyDepositedEvent(String aggregateId, int version,
                                BigDecimal amount, String description) {
        super(aggregateId, version);
        this.amount = amount;
        this.description = description;
    }

    public BigDecimal getAmount() { return amount; }
    public String getDescription() { return description; }

    @Override
    public String toString() {
        return String.format("MoneyDeposited{amount=%s, desc='%s'}",
                             amount, description);
    }
}

public class MoneyWithdrawnEvent extends DomainEvent {
    private final BigDecimal amount;
    private final String description;

    public MoneyWithdrawnEvent(String aggregateId, int version,
                                BigDecimal amount, String description) {
        super(aggregateId, version);
        this.amount = amount;
        this.description = description;
    }

    public BigDecimal getAmount() { return amount; }
    public String getDescription() { return description; }

    @Override
    public String toString() {
        return String.format("MoneyWithdrawn{amount=%s, desc='%s'}",
                             amount, description);
    }
}
```

### Step 2: Event-Sourced Aggregate

```java
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

public class BankAccount {

    private String id;
    private String owner;
    private BigDecimal balance;
    private int version;

    // Uncommitted events generated by commands
    private final List<DomainEvent> uncommittedEvents = new ArrayList<>();

    // Private constructor -- use factory methods
    private BankAccount() {
        this.balance = BigDecimal.ZERO;
        this.version = 0;
    }

    // ===== FACTORY: Create from events (rebuilding state) =====
    public static BankAccount fromEvents(List<DomainEvent> events) {
        BankAccount account = new BankAccount();
        for (DomainEvent event : events) {
            account.apply(event);
        }
        return account;
    }

    // ===== COMMANDS: Business operations that generate events =====

    public static BankAccount create(String id, String owner,
                                      BigDecimal initialBalance) {
        BankAccount account = new BankAccount();
        AccountCreatedEvent event = new AccountCreatedEvent(
            id, account.version + 1, owner, initialBalance);
        account.apply(event);
        account.uncommittedEvents.add(event);
        return account;
    }

    public void deposit(BigDecimal amount, String description) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Deposit amount must be positive");
        }
        MoneyDepositedEvent event = new MoneyDepositedEvent(
            this.id, this.version + 1, amount, description);
        apply(event);
        uncommittedEvents.add(event);
    }

    public void withdraw(BigDecimal amount, String description) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException(
                "Withdrawal amount must be positive");
        }
        if (amount.compareTo(this.balance) > 0) {
            throw new IllegalStateException(
                "Insufficient funds. Balance: " + this.balance +
                ", Requested: " + amount);
        }
        MoneyWithdrawnEvent event = new MoneyWithdrawnEvent(
            this.id, this.version + 1, amount, description);
        apply(event);
        uncommittedEvents.add(event);
    }

    // ===== EVENT APPLICATION: Update state based on event type =====

    private void apply(DomainEvent event) {
        if (event instanceof AccountCreatedEvent e) {
            this.id = e.getAggregateId();
            this.owner = e.getOwner();
            this.balance = e.getInitialBalance();
        } else if (event instanceof MoneyDepositedEvent e) {
            this.balance = this.balance.add(e.getAmount());
        } else if (event instanceof MoneyWithdrawnEvent e) {
            this.balance = this.balance.subtract(e.getAmount());
        }
        this.version = event.getVersion();
    }

    // ===== GETTERS =====

    public String getId() { return id; }
    public String getOwner() { return owner; }
    public BigDecimal getBalance() { return balance; }
    public int getVersion() { return version; }

    public List<DomainEvent> getUncommittedEvents() {
        return new ArrayList<>(uncommittedEvents);
    }

    public void clearUncommittedEvents() {
        uncommittedEvents.clear();
    }

    @Override
    public String toString() {
        return String.format("BankAccount{id='%s', owner='%s', balance=%s, version=%d}",
                             id, owner, balance, version);
    }
}
```

### Step 3: Event Store

```java
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class InMemoryEventStore {

    // aggregateId -> list of events
    private final Map<String, List<DomainEvent>> store =
        new ConcurrentHashMap<>();

    public void save(String aggregateId, List<DomainEvent> events,
                     int expectedVersion) {
        List<DomainEvent> existingEvents =
            store.getOrDefault(aggregateId, new ArrayList<>());

        // Optimistic concurrency check
        int currentVersion = existingEvents.size();
        if (currentVersion != expectedVersion) {
            throw new ConcurrentModificationException(
                "Expected version " + expectedVersion +
                " but found " + currentVersion);
        }

        existingEvents.addAll(events);
        store.put(aggregateId, existingEvents);
    }

    public List<DomainEvent> getEvents(String aggregateId) {
        return store.getOrDefault(aggregateId, Collections.emptyList());
    }

    public List<DomainEvent> getEventsUpToVersion(String aggregateId,
                                                    int maxVersion) {
        return getEvents(aggregateId).stream()
            .filter(e -> e.getVersion() <= maxVersion)
            .collect(Collectors.toList());
    }

    public List<DomainEvent> getAllEvents() {
        return store.values().stream()
            .flatMap(Collection::stream)
            .sorted(Comparator.comparing(DomainEvent::getTimestamp))
            .collect(Collectors.toList());
    }
}
```

### Step 4: Account Service

```java
public class BankAccountService {

    private final InMemoryEventStore eventStore;

    public BankAccountService(InMemoryEventStore eventStore) {
        this.eventStore = eventStore;
    }

    public BankAccount createAccount(String id, String owner,
                                      BigDecimal initialBalance) {
        BankAccount account = BankAccount.create(id, owner, initialBalance);

        eventStore.save(id, account.getUncommittedEvents(), 0);
        account.clearUncommittedEvents();

        System.out.println("Created: " + account);
        return account;
    }

    public void deposit(String accountId, BigDecimal amount,
                        String description) {
        // Rebuild state from events
        List<DomainEvent> events = eventStore.getEvents(accountId);
        BankAccount account = BankAccount.fromEvents(events);

        // Execute command
        account.deposit(amount, description);

        // Save new events
        eventStore.save(accountId, account.getUncommittedEvents(),
                        events.size());
        account.clearUncommittedEvents();

        System.out.println("Deposited " + amount + " -> " + account);
    }

    public void withdraw(String accountId, BigDecimal amount,
                          String description) {
        List<DomainEvent> events = eventStore.getEvents(accountId);
        BankAccount account = BankAccount.fromEvents(events);

        account.withdraw(amount, description);

        eventStore.save(accountId, account.getUncommittedEvents(),
                        events.size());
        account.clearUncommittedEvents();

        System.out.println("Withdrew " + amount + " -> " + account);
    }

    public BankAccount getAccount(String accountId) {
        List<DomainEvent> events = eventStore.getEvents(accountId);
        if (events.isEmpty()) {
            throw new RuntimeException("Account not found: " + accountId);
        }
        return BankAccount.fromEvents(events);
    }

    // Temporal query: get balance at a specific point in time
    public BankAccount getAccountAtVersion(String accountId, int version) {
        List<DomainEvent> events = eventStore.getEventsUpToVersion(
            accountId, version);
        return BankAccount.fromEvents(events);
    }

    public void printEventHistory(String accountId) {
        List<DomainEvent> events = eventStore.getEvents(accountId);
        System.out.println("\nEvent history for account " + accountId + ":");
        for (DomainEvent event : events) {
            System.out.println("  v" + event.getVersion() + ": " + event);
        }
    }
}
```

### Step 5: Running the System

```java
public class EventSourcingDemo {

    public static void main(String[] args) {
        InMemoryEventStore eventStore = new InMemoryEventStore();
        BankAccountService service = new BankAccountService(eventStore);

        // Create account
        service.createAccount("ACC-001", "Alice", BigDecimal.ZERO);

        // Perform transactions
        service.deposit("ACC-001", new BigDecimal("1000"), "Initial deposit");
        service.deposit("ACC-001", new BigDecimal("500"), "Salary");
        service.withdraw("ACC-001", new BigDecimal("200"), "Groceries");
        service.deposit("ACC-001", new BigDecimal("50"), "Refund");
        service.withdraw("ACC-001", new BigDecimal("100"), "Utilities");

        // Print event history
        service.printEventHistory("ACC-001");

        // Temporal query: what was the balance after the salary deposit?
        BankAccount atVersion3 = service.getAccountAtVersion("ACC-001", 3);
        System.out.println("\nBalance at version 3: " + atVersion3.getBalance());

        // Current state
        BankAccount current = service.getAccount("ACC-001");
        System.out.println("Current balance: " + current.getBalance());
    }
}
```

**Output:**

```
Created: BankAccount{id='ACC-001', owner='Alice', balance=0, version=1}
Deposited 1000 -> BankAccount{id='ACC-001', owner='Alice', balance=1000, version=2}
Deposited 500 -> BankAccount{id='ACC-001', owner='Alice', balance=1500, version=3}
Withdrew 200 -> BankAccount{id='ACC-001', owner='Alice', balance=1300, version=4}
Deposited 50 -> BankAccount{id='ACC-001', owner='Alice', balance=1350, version=5}
Withdrew 100 -> BankAccount{id='ACC-001', owner='Alice', balance=1250, version=6}

Event history for account ACC-001:
  v1: AccountCreated{owner='Alice', balance=0}
  v2: MoneyDeposited{amount=1000, desc='Initial deposit'}
  v3: MoneyDeposited{amount=500, desc='Salary'}
  v4: MoneyWithdrawn{amount=200, desc='Groceries'}
  v5: MoneyDeposited{amount=50, desc='Refund'}
  v6: MoneyWithdrawn{amount=100, desc='Utilities'}

Balance at version 3: 1500
Current balance: 1250
```

---

## Snapshots for Performance

As events accumulate, replaying them all becomes slow. Snapshots capture the state at a point in time so you only need to replay events after the snapshot.

```
Without snapshots (1000 events):
  Replay event 1, 2, 3, ... 998, 999, 1000  --> Current State
  Time: O(n) where n = total events

With snapshot at event 900:
  Load snapshot (state at event 900)
  Replay event 901, 902, ... 999, 1000  --> Current State
  Time: O(k) where k = events since snapshot
```

### Java: Snapshot Implementation

```java
public class Snapshot {
    private final String aggregateId;
    private final int version;
    private final BigDecimal balance;
    private final String owner;
    private final Instant createdAt;

    public Snapshot(String aggregateId, int version,
                    BigDecimal balance, String owner) {
        this.aggregateId = aggregateId;
        this.version = version;
        this.balance = balance;
        this.owner = owner;
        this.createdAt = Instant.now();
    }

    // Getters
    public String getAggregateId() { return aggregateId; }
    public int getVersion() { return version; }
    public BigDecimal getBalance() { return balance; }
    public String getOwner() { return owner; }
}

public class SnapshotStore {
    private final Map<String, Snapshot> snapshots = new HashMap<>();

    public void save(Snapshot snapshot) {
        snapshots.put(snapshot.getAggregateId(), snapshot);
        System.out.println("  Snapshot saved at version " +
                           snapshot.getVersion());
    }

    public Snapshot getLatest(String aggregateId) {
        return snapshots.get(aggregateId);
    }
}

// Enhanced service with snapshots
public class BankAccountServiceWithSnapshots {

    private final InMemoryEventStore eventStore;
    private final SnapshotStore snapshotStore;
    private final int snapshotInterval;

    public BankAccountServiceWithSnapshots(InMemoryEventStore eventStore,
                                           SnapshotStore snapshotStore,
                                           int snapshotInterval) {
        this.eventStore = eventStore;
        this.snapshotStore = snapshotStore;
        this.snapshotInterval = snapshotInterval;
    }

    public BankAccount getAccount(String accountId) {
        Snapshot snapshot = snapshotStore.getLatest(accountId);
        List<DomainEvent> events;

        BankAccount account;
        if (snapshot != null) {
            // Load from snapshot + replay only recent events
            events = eventStore.getEvents(accountId).stream()
                .filter(e -> e.getVersion() > snapshot.getVersion())
                .toList();

            account = BankAccount.fromSnapshot(snapshot);
            for (DomainEvent event : events) {
                account.replayEvent(event);
            }

            System.out.println("  Loaded from snapshot v" +
                               snapshot.getVersion() +
                               " + replayed " + events.size() + " events");
        } else {
            // No snapshot, replay all events
            events = eventStore.getEvents(accountId);
            account = BankAccount.fromEvents(events);
            System.out.println("  Loaded by replaying " +
                               events.size() + " events");
        }

        // Create snapshot if needed
        if (account.getVersion() % snapshotInterval == 0) {
            snapshotStore.save(new Snapshot(
                accountId, account.getVersion(),
                account.getBalance(), account.getOwner()));
        }

        return account;
    }
}
```

**Output with snapshots (interval = 5):**

```
After 7 transactions:
  Loaded from snapshot v5 + replayed 2 events
  Balance: 1250

Without snapshots:
  Loaded by replaying 7 events
  Balance: 1250
```

---

## Python Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import uuid

# ===== EVENTS =====

@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_id: str = ""
    version: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AccountCreated(DomainEvent):
    owner: str = ""
    initial_balance: float = 0.0

@dataclass
class MoneyDeposited(DomainEvent):
    amount: float = 0.0
    description: str = ""

@dataclass
class MoneyWithdrawn(DomainEvent):
    amount: float = 0.0
    description: str = ""


# ===== EVENT-SOURCED AGGREGATE =====

class BankAccount:
    def __init__(self):
        self.id = ""
        self.owner = ""
        self.balance = 0.0
        self.version = 0
        self._uncommitted_events: List[DomainEvent] = []

    @classmethod
    def create(cls, account_id: str, owner: str,
               initial_balance: float = 0.0) -> "BankAccount":
        account = cls()
        event = AccountCreated(
            aggregate_id=account_id,
            version=1,
            owner=owner,
            initial_balance=initial_balance
        )
        account._apply(event)
        account._uncommitted_events.append(event)
        return account

    @classmethod
    def from_events(cls, events: List[DomainEvent]) -> "BankAccount":
        account = cls()
        for event in events:
            account._apply(event)
        return account

    def deposit(self, amount: float, description: str = ""):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        event = MoneyDeposited(
            aggregate_id=self.id,
            version=self.version + 1,
            amount=amount,
            description=description
        )
        self._apply(event)
        self._uncommitted_events.append(event)

    def withdraw(self, amount: float, description: str = ""):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError(
                f"Insufficient funds. Balance: {self.balance}, "
                f"Requested: {amount}")
        event = MoneyWithdrawn(
            aggregate_id=self.id,
            version=self.version + 1,
            amount=amount,
            description=description
        )
        self._apply(event)
        self._uncommitted_events.append(event)

    def _apply(self, event: DomainEvent):
        if isinstance(event, AccountCreated):
            self.id = event.aggregate_id
            self.owner = event.owner
            self.balance = event.initial_balance
        elif isinstance(event, MoneyDeposited):
            self.balance += event.amount
        elif isinstance(event, MoneyWithdrawn):
            self.balance -= event.amount
        self.version = event.version

    def get_uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)

    def clear_uncommitted_events(self):
        self._uncommitted_events.clear()

    def __repr__(self):
        return (f"BankAccount(id='{self.id}', owner='{self.owner}', "
                f"balance={self.balance:.2f}, version={self.version})")


# ===== EVENT STORE =====

class EventStore:
    def __init__(self):
        self._store: Dict[str, List[DomainEvent]] = {}

    def save(self, aggregate_id: str, events: List[DomainEvent],
             expected_version: int):
        existing = self._store.get(aggregate_id, [])
        if len(existing) != expected_version:
            raise Exception(
                f"Concurrency conflict: expected version "
                f"{expected_version}, found {len(existing)}")
        existing.extend(events)
        self._store[aggregate_id] = existing

    def get_events(self, aggregate_id: str) -> List[DomainEvent]:
        return self._store.get(aggregate_id, [])

    def get_events_up_to(self, aggregate_id: str,
                         max_version: int) -> List[DomainEvent]:
        return [e for e in self.get_events(aggregate_id)
                if e.version <= max_version]


# ===== SERVICE =====

class BankAccountService:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def create_account(self, account_id: str, owner: str,
                       initial_balance: float = 0.0) -> BankAccount:
        account = BankAccount.create(account_id, owner, initial_balance)
        self.event_store.save(
            account_id, account.get_uncommitted_events(), 0)
        account.clear_uncommitted_events()
        print(f"Created: {account}")
        return account

    def deposit(self, account_id: str, amount: float,
                description: str = ""):
        events = self.event_store.get_events(account_id)
        account = BankAccount.from_events(events)
        account.deposit(amount, description)
        self.event_store.save(
            account_id, account.get_uncommitted_events(), len(events))
        account.clear_uncommitted_events()
        print(f"Deposited {amount:.2f} -> {account}")

    def withdraw(self, account_id: str, amount: float,
                 description: str = ""):
        events = self.event_store.get_events(account_id)
        account = BankAccount.from_events(events)
        account.withdraw(amount, description)
        self.event_store.save(
            account_id, account.get_uncommitted_events(), len(events))
        account.clear_uncommitted_events()
        print(f"Withdrew {amount:.2f} -> {account}")

    def get_account(self, account_id: str) -> BankAccount:
        events = self.event_store.get_events(account_id)
        return BankAccount.from_events(events)

    def get_balance_at_version(self, account_id: str,
                                version: int) -> float:
        events = self.event_store.get_events_up_to(account_id, version)
        account = BankAccount.from_events(events)
        return account.balance

    def print_history(self, account_id: str):
        events = self.event_store.get_events(account_id)
        print(f"\nEvent history for {account_id}:")
        for event in events:
            event_type = type(event).__name__
            if isinstance(event, AccountCreated):
                detail = f"owner={event.owner}"
            elif isinstance(event, MoneyDeposited):
                detail = f"amount={event.amount:.2f}, {event.description}"
            elif isinstance(event, MoneyWithdrawn):
                detail = f"amount={event.amount:.2f}, {event.description}"
            else:
                detail = ""
            print(f"  v{event.version}: {event_type} [{detail}]")


# ===== DEMO =====

store = EventStore()
service = BankAccountService(store)

service.create_account("ACC-001", "Alice")
service.deposit("ACC-001", 1000.00, "Initial deposit")
service.deposit("ACC-001", 500.00, "Salary")
service.withdraw("ACC-001", 200.00, "Groceries")
service.deposit("ACC-001", 50.00, "Refund")
service.withdraw("ACC-001", 100.00, "Utilities")

service.print_history("ACC-001")

# Temporal query
balance_v3 = service.get_balance_at_version("ACC-001", 3)
print(f"\nBalance at version 3: {balance_v3:.2f}")

current = service.get_account("ACC-001")
print(f"Current balance: {current.balance:.2f}")
```

**Output:**

```
Created: BankAccount(id='ACC-001', owner='Alice', balance=0.00, version=1)
Deposited 1000.00 -> BankAccount(id='ACC-001', owner='Alice', balance=1000.00, version=2)
Deposited 500.00 -> BankAccount(id='ACC-001', owner='Alice', balance=1500.00, version=3)
Withdrew 200.00 -> BankAccount(id='ACC-001', owner='Alice', balance=1300.00, version=4)
Deposited 50.00 -> BankAccount(id='ACC-001', owner='Alice', balance=1350.00, version=5)
Withdrew 100.00 -> BankAccount(id='ACC-001', owner='Alice', balance=1250.00, version=6)

Event history for ACC-001:
  v1: AccountCreated [owner=Alice]
  v2: MoneyDeposited [amount=1000.00, Initial deposit]
  v3: MoneyDeposited [amount=500.00, Salary]
  v4: MoneyWithdrawn [amount=200.00, Groceries]
  v5: MoneyDeposited [amount=50.00, Refund]
  v6: MoneyWithdrawn [amount=100.00, Utilities]

Balance at version 3: 1500.00
Current balance: 1250.00
```

---

## Event Sourcing + CQRS Combination

Event Sourcing and CQRS are natural partners:

```
+-------------------+       +-------------------+       +------------------+
|   Command Side    |       |   Event Store     |       |   Query Side     |
|                   |       |                   |       |                  |
| Validate command  | ----> | Append events     | ----> | Project events   |
| Apply to          |       |                   |       | into read models |
| aggregate         |       | AccountCreated    |       |                  |
|                   |       | MoneyDeposited    |       | account_summary  |
|                   |       | MoneyWithdrawn    |       | (denormalized)   |
+-------------------+       +-------------------+       +------------------+
                                                                |
                                                                v
                                                        +------------------+
                                                        | Read Database    |
                                                        | - Balance: 1250  |
                                                        | - Tx Count: 6    |
                                                        | - Last Tx: ...   |
                                                        +------------------+
```

Events from the event store feed projections that build read-optimized views. The event store is the single source of truth. Read models are disposable -- you can delete and rebuild them by replaying events.

---

## Real-World Applications

### Financial Systems

```
Banking transactions: Every deposit, withdrawal, transfer is an event
Audit trail:          Regulators can see every change and who made it
Reconciliation:       Replay events to verify account balances
Debugging:            Reproduce exact state at any point in time
```

### E-Commerce Order Tracking

```
OrderPlaced -> PaymentReceived -> ItemsPicked -> OrderShipped -> Delivered
     |               |                |              |             |
   Event 1         Event 2          Event 3        Event 4      Event 5

Customer can see full order history
Support can replay to see what happened
Analytics can count events by type
```

### Healthcare Records

```
PatientAdmitted -> DiagnosisRecorded -> TreatmentStarted -> MedicationGiven
Complete history required by law
Cannot delete records (append only matches regulation)
Temporal queries: "What medications was the patient on at date X?"
```

---

## Complexity Trade-Offs

```
+---------------------------+----------------------------------+
| Benefit                   | Cost                             |
+---------------------------+----------------------------------+
| Complete audit trail      | More storage (events accumulate) |
| Temporal queries          | Complex event schema evolution   |
| Debug by replaying events | Eventual consistency with CQRS   |
| Undo / compensation       | Learning curve for the team      |
| Event-driven integration  | Snapshot management overhead     |
| Rebuild read models       | Complex conflict resolution      |
+---------------------------+----------------------------------+
```

---

## When to Use / When NOT to Use

### Use Event Sourcing When

- You need a complete audit trail (finance, healthcare, compliance)
- You need to answer "what was the state at time X?"
- You are building an event-driven architecture
- Domain experts think in terms of events ("order placed," "payment received")
- You need to support undo operations
- You are using CQRS and want events as the sync mechanism

### Do NOT Use Event Sourcing When

- You have a simple CRUD application
- You do not need audit trails or temporal queries
- Your team is unfamiliar with the pattern and delivery timelines are tight
- The domain is not naturally event-driven
- You need to delete data (GDPR right to be forgotten requires special handling)
- Read-after-write consistency is critical and eventual consistency is not acceptable

---

## Common Mistakes

1. **Storing too much data in events.** Events should capture the fact and its parameters, not the entire entity state. "PriceChanged(productId, newPrice)" not "ProductUpdated(all fields)."

2. **Not planning for event schema evolution.** Events are immutable. When the schema changes, you need upcasters to transform old events into the new format during replay.

3. **Forgetting snapshots.** Without snapshots, replaying 100,000 events to load an aggregate becomes unusably slow.

4. **Making events too fine-grained.** "FieldXUpdated" events are not meaningful business events. Use domain language: "OrderShipped," "PaymentReceived."

5. **Treating the event store as a message queue.** The event store is for persistence and rebuilding state. Use a separate message broker for event distribution.

---

## Best Practices

1. **Name events in past tense.** Events describe what happened: "OrderPlaced," not "PlaceOrder" (that is a command).

2. **Include all necessary data in the event.** Events should be self-contained. Do not require external lookups to process an event.

3. **Plan for schema evolution from day one.** Use versioned event schemas and write upcasters early.

4. **Take snapshots at regular intervals.** Every 100 or 1000 events, depending on replay time requirements.

5. **Test by replaying events.** Write tests that create events, replay them, and verify the resulting state.

6. **Keep aggregates small.** An aggregate with millions of events is a design problem. Consider splitting it.

---

## Quick Summary

Event Sourcing stores every state change as an immutable event instead of overwriting the current state. Current state is derived by replaying events from the beginning. Snapshots improve performance by capturing state at intervals so only recent events need replay. Event Sourcing provides complete audit trails, temporal queries, and the ability to rebuild state from history. It pairs naturally with CQRS, where events from the write side feed projections that build read models. The pattern adds significant complexity and is best suited for domains where history and auditability are critical, such as financial and healthcare systems.

---

## Key Points

- Event Sourcing stores events (facts), not state
- Events are immutable and append-only
- Current state is derived by replaying events
- Snapshots prevent performance degradation as events accumulate
- Event Sourcing enables temporal queries ("what was the state at time X?")
- Events should use past tense and domain language
- CQRS and Event Sourcing are complementary patterns
- Schema evolution requires careful planning (upcasters, versioning)
- The event store is not a message queue
- GDPR "right to erasure" requires special handling (crypto shredding)

---

## Practice Questions

1. What is the fundamental difference between traditional state storage and Event Sourcing? What information do you gain and what complexity do you introduce?

2. Explain how snapshots improve performance in an Event Sourced system. How would you decide the snapshot interval?

3. A bank account has been active for 5 years with 50,000 events. A customer disputes a transaction from 3 years ago. How does Event Sourcing help resolve this dispute compared to traditional state storage?

4. What happens when you need to change the schema of an event? For example, you originally stored "MoneyDeposited(amount)" and now need "MoneyDeposited(amount, currency)". How do you handle existing events?

5. Explain the relationship between Event Sourcing and CQRS. Can you use one without the other? When would you use both together?

---

## Exercises

### Exercise 1: Shopping Cart Event Sourcing

Build an event-sourced shopping cart with events: `CartCreated`, `ItemAdded`, `ItemRemoved`, `QuantityChanged`, `CartCheckedOut`. Implement the aggregate, event store, and a service that supports temporal queries ("what was in the cart before the last item was removed?").

### Exercise 2: Snapshots

Extend the bank account example to include automatic snapshot creation every 100 events. Write a benchmark that measures loading time with and without snapshots for accounts with 1000, 5000, and 10000 events.

### Exercise 3: Event Sourcing + CQRS

Combine Event Sourcing with CQRS for a simple order system. Events like `OrderPlaced`, `OrderPaid`, `OrderShipped` feed into two read models: (1) an order status view for customers and (2) an order analytics view that counts orders by status and calculates total revenue.

---

## What Is Next?

Event Sourcing and CQRS handle data complexity within your services. But what happens when a downstream service fails? The next chapter introduces the **Circuit Breaker** pattern, which prevents cascading failures in distributed systems by detecting when a service is down and failing fast instead of hanging indefinitely.
