# Chapter 16: Command Pattern -- Encapsulate Requests as Objects

## What You Will Learn

- How to turn method calls into objects that can be stored, queued, and undone
- Implementing the Command pattern in Java with `execute()` and `undo()`
- Building a Python command queue for batch processing
- Real-world applications: task queues, transaction logging, macro recording
- An introduction to CQRS (Command Query Responsibility Segregation)
- When Command adds value and when it adds unnecessary complexity

## Why This Chapter Matters

In backend systems, you often need to do more than just execute a request. You might need to undo it, replay it, schedule it for later, log it for auditing, or queue it for batch processing. A plain method call cannot do any of these things -- once it runs, it is gone.

The Command pattern solves this by wrapping each request in an object. That object can be passed around, stored in a list, serialized to a database, or placed in a queue. It is the pattern behind undo/redo systems, job queues, transaction logs, and even the CQRS architecture used in large-scale backends.

---

## The Problem: Requests That Cannot Be Managed

```java
// Without Command -- you cannot undo, queue, or replay
public class AccountService {

    public void transfer(String from, String to, double amount) {
        debit(from, amount);   // Done. Cannot undo.
        credit(to, amount);    // Done. Cannot replay.
        // No record of what happened.
        // No way to queue this for later.
        // No way to batch multiple operations.
    }
}
```

```
What we WANT to do with requests:

  +---> Execute now
  |
  Request --+---> Execute later (queue)
  |
  +---> Undo after execution
  |
  +---> Log for auditing
  |
  +---> Replay from history
  |
  +---> Batch multiple requests

  A plain method call gives us ONLY "Execute now."
  The Command pattern gives us ALL of these.
```

---

## The Solution: Command Pattern

```
+--------------------------------------------------------+
|                  COMMAND PATTERN STRUCTURE               |
+--------------------------------------------------------+

  +----------+         +-------------------+
  |  Client  | creates |     Command       |
  |          |-------->| + execute()       |
  +----------+         | + undo()          |
                        +-------------------+
                            ^         ^
                            |         |
                  +-----------+   +-----------+
                  | Transfer   |   | Deposit   |
                  | Command    |   | Command   |
                  +-----------+   +-----------+
                        |               |
                        v               v
                  +----------------------------+
                  |        Receiver             |
                  |    (Account, Database)       |
                  |  The object that does the    |
                  |  actual work                 |
                  +----------------------------+

  +-------------------+
  |     Invoker       |  Stores and manages commands
  | (CommandQueue,    |  Can execute, undo, replay
  |  TransactionLog)  |
  +-------------------+
```

---

## Java Implementation: Command with Execute and Undo

### Step 1: Define the Command Interface

```java
// Command.java
public interface Command {
    void execute();
    void undo();
    String describe();
}
```

### Step 2: Create the Receiver

```java
// BankAccount.java
public class BankAccount {
    private final String accountId;
    private double balance;

    public BankAccount(String accountId, double initialBalance) {
        this.accountId = accountId;
        this.balance = initialBalance;
    }

    public void deposit(double amount) {
        balance += amount;
        System.out.println("    [" + accountId + "] Deposited $"
            + amount + " -> Balance: $" + balance);
    }

    public void withdraw(double amount) {
        if (balance < amount) {
            throw new IllegalStateException(
                accountId + ": Insufficient funds. Balance: $"
                + balance + ", Requested: $" + amount);
        }
        balance -= amount;
        System.out.println("    [" + accountId + "] Withdrew $"
            + amount + " -> Balance: $" + balance);
    }

    public double getBalance() {
        return balance;
    }

    public String getAccountId() {
        return accountId;
    }
}
```

### Step 3: Implement Concrete Commands

```java
// DepositCommand.java
public class DepositCommand implements Command {
    private final BankAccount account;
    private final double amount;

    public DepositCommand(BankAccount account, double amount) {
        this.account = account;
        this.amount = amount;
    }

    @Override
    public void execute() {
        account.deposit(amount);
    }

    @Override
    public void undo() {
        account.withdraw(amount);  // Reverse: withdraw what was deposited
    }

    @Override
    public String describe() {
        return "Deposit $" + amount + " to " + account.getAccountId();
    }
}

// WithdrawCommand.java
public class WithdrawCommand implements Command {
    private final BankAccount account;
    private final double amount;

    public WithdrawCommand(BankAccount account, double amount) {
        this.account = account;
        this.amount = amount;
    }

    @Override
    public void execute() {
        account.withdraw(amount);
    }

    @Override
    public void undo() {
        account.deposit(amount);  // Reverse: deposit what was withdrawn
    }

    @Override
    public String describe() {
        return "Withdraw $" + amount + " from " + account.getAccountId();
    }
}

// TransferCommand.java
public class TransferCommand implements Command {
    private final BankAccount from;
    private final BankAccount to;
    private final double amount;

    public TransferCommand(BankAccount from, BankAccount to, double amount) {
        this.from = from;
        this.to = to;
        this.amount = amount;
    }

    @Override
    public void execute() {
        from.withdraw(amount);
        to.deposit(amount);
    }

    @Override
    public void undo() {
        to.withdraw(amount);
        from.deposit(amount);
    }

    @Override
    public String describe() {
        return "Transfer $" + amount + " from "
            + from.getAccountId() + " to " + to.getAccountId();
    }
}
```

### Step 4: Build the Invoker with Undo/Redo

```java
// TransactionManager.java
public class TransactionManager {
    private final Deque<Command> undoStack = new ArrayDeque<>();
    private final Deque<Command> redoStack = new ArrayDeque<>();
    private final List<Command> history = new ArrayList<>();

    public void execute(Command command) {
        System.out.println("  Executing: " + command.describe());
        command.execute();
        undoStack.push(command);
        redoStack.clear();  // New action invalidates redo history
        history.add(command);
    }

    public void undo() {
        if (undoStack.isEmpty()) {
            System.out.println("  Nothing to undo.");
            return;
        }
        Command command = undoStack.pop();
        System.out.println("  Undoing: " + command.describe());
        command.undo();
        redoStack.push(command);
    }

    public void redo() {
        if (redoStack.isEmpty()) {
            System.out.println("  Nothing to redo.");
            return;
        }
        Command command = redoStack.pop();
        System.out.println("  Redoing: " + command.describe());
        command.execute();
        undoStack.push(command);
    }

    public void printHistory() {
        System.out.println("\n  Transaction History:");
        for (int i = 0; i < history.size(); i++) {
            System.out.println("    " + (i + 1) + ". " + history.get(i).describe());
        }
    }
}
```

### Step 5: Put It All Together

```java
// Main.java
public class Main {
    public static void main(String[] args) {
        BankAccount checking = new BankAccount("CHK-001", 1000.0);
        BankAccount savings = new BankAccount("SAV-001", 5000.0);

        TransactionManager txManager = new TransactionManager();

        // Execute commands
        txManager.execute(new DepositCommand(checking, 500.0));
        txManager.execute(new WithdrawCommand(checking, 200.0));
        txManager.execute(new TransferCommand(checking, savings, 300.0));

        System.out.println("\nBalances after transactions:");
        System.out.println("  Checking: $" + checking.getBalance());
        System.out.println("  Savings:  $" + savings.getBalance());

        // Undo the transfer
        System.out.println("\nUndoing last transaction:");
        txManager.undo();

        System.out.println("\nBalances after undo:");
        System.out.println("  Checking: $" + checking.getBalance());
        System.out.println("  Savings:  $" + savings.getBalance());

        // Redo it
        System.out.println("\nRedoing:");
        txManager.redo();

        System.out.println("\nBalances after redo:");
        System.out.println("  Checking: $" + checking.getBalance());
        System.out.println("  Savings:  $" + savings.getBalance());

        txManager.printHistory();
    }
}
```

**Output:**
```
  Executing: Deposit $500.0 to CHK-001
    [CHK-001] Deposited $500.0 -> Balance: $1500.0
  Executing: Withdraw $200.0 from CHK-001
    [CHK-001] Withdrew $200.0 -> Balance: $1300.0
  Executing: Transfer $300.0 from CHK-001 to SAV-001
    [CHK-001] Withdrew $300.0 -> Balance: $1000.0
    [SAV-001] Deposited $300.0 -> Balance: $5300.0

Balances after transactions:
  Checking: $1000.0
  Savings:  $5300.0

Undoing last transaction:
  Undoing: Transfer $300.0 from CHK-001 to SAV-001
    [SAV-001] Withdrew $300.0 -> Balance: $5000.0
    [CHK-001] Deposited $300.0 -> Balance: $1300.0

Balances after undo:
  Checking: $1300.0
  Savings:  $5000.0

Redoing:
  Redoing: Transfer $300.0 from CHK-001 to SAV-001
    [CHK-001] Withdrew $300.0 -> Balance: $1000.0
    [SAV-001] Deposited $300.0 -> Balance: $5300.0

Balances after redo:
  Checking: $1000.0
  Savings:  $5300.0

  Transaction History:
    1. Deposit $500.0 to CHK-001
    2. Withdraw $200.0 from CHK-001
    3. Transfer $300.0 from CHK-001 to SAV-001
```

---

## Before vs After

```
BEFORE (direct calls):              AFTER (Command objects):
+----------------------------+      +----------------------------+
| service.transfer(a, b, $)  |      | Command cmd = new Transfer |
| // Executed immediately    |      |   Command(a, b, $);       |
| // Cannot undo             |      |                            |
| // No history              |      | manager.execute(cmd);      |
| // Cannot queue            |      | // Can undo: manager.undo()|
| // Cannot replay           |      | // Has history             |
+----------------------------+      | // Can queue for later     |
                                    | // Can replay from log     |
                                    +----------------------------+
```

---

## Python Implementation: Command Queue

```python
# command_queue.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from typing import Optional
import json


class Command(ABC):
    """Base command with execute, undo, and serialization."""

    @abstractmethod
    def execute(self) -> bool:
        """Execute the command. Returns True on success."""
        pass

    @abstractmethod
    def undo(self) -> bool:
        """Reverse the command. Returns True on success."""
        pass

    @abstractmethod
    def describe(self) -> str:
        pass


@dataclass
class Task:
    name: str
    priority: int = 0
    completed: bool = False


class TaskManager:
    """Receiver -- the object commands act upon."""

    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def add_task(self, name: str, priority: int = 0) -> None:
        self.tasks[name] = Task(name=name, priority=priority)
        print(f"    [TaskManager] Added: '{name}' (priority={priority})")

    def remove_task(self, name: str) -> Optional[Task]:
        task = self.tasks.pop(name, None)
        if task:
            print(f"    [TaskManager] Removed: '{name}'")
        return task

    def complete_task(self, name: str) -> bool:
        task = self.tasks.get(name)
        if task:
            task.completed = True
            print(f"    [TaskManager] Completed: '{name}'")
            return True
        return False

    def uncomplete_task(self, name: str) -> bool:
        task = self.tasks.get(name)
        if task:
            task.completed = False
            print(f"    [TaskManager] Uncompleted: '{name}'")
            return True
        return False

    def list_tasks(self) -> None:
        print("    Current tasks:")
        for name, task in sorted(self.tasks.items(),
                                  key=lambda x: -x[1].priority):
            status = "DONE" if task.completed else "TODO"
            print(f"      [{status}] {name} (priority={task.priority})")


class AddTaskCommand(Command):
    def __init__(self, manager: TaskManager, name: str, priority: int = 0):
        self.manager = manager
        self.name = name
        self.priority = priority

    def execute(self) -> bool:
        self.manager.add_task(self.name, self.priority)
        return True

    def undo(self) -> bool:
        self.manager.remove_task(self.name)
        return True

    def describe(self) -> str:
        return f"Add task '{self.name}'"


class CompleteTaskCommand(Command):
    def __init__(self, manager: TaskManager, name: str):
        self.manager = manager
        self.name = name

    def execute(self) -> bool:
        return self.manager.complete_task(self.name)

    def undo(self) -> bool:
        return self.manager.uncomplete_task(self.name)

    def describe(self) -> str:
        return f"Complete task '{self.name}'"


class RemoveTaskCommand(Command):
    def __init__(self, manager: TaskManager, name: str):
        self.manager = manager
        self.name = name
        self._removed_task: Optional[Task] = None

    def execute(self) -> bool:
        self._removed_task = self.manager.remove_task(self.name)
        return self._removed_task is not None

    def undo(self) -> bool:
        if self._removed_task:
            self.manager.add_task(
                self._removed_task.name,
                self._removed_task.priority
            )
            return True
        return False

    def describe(self) -> str:
        return f"Remove task '{self.name}'"


class MacroCommand(Command):
    """A command that groups multiple commands into one."""

    def __init__(self, name: str, commands: list[Command]):
        self._name = name
        self._commands = commands

    def execute(self) -> bool:
        print(f"  [Macro] Executing '{self._name}' "
              f"({len(self._commands)} commands)")
        for cmd in self._commands:
            if not cmd.execute():
                return False
        return True

    def undo(self) -> bool:
        print(f"  [Macro] Undoing '{self._name}'")
        for cmd in reversed(self._commands):
            cmd.undo()
        return True

    def describe(self) -> str:
        return f"Macro '{self._name}' ({len(self._commands)} commands)"


class CommandQueue:
    """Invoker -- queues commands and manages undo history."""

    def __init__(self):
        self._queue: deque[Command] = deque()
        self._history: list[Command] = []
        self._undo_stack: list[Command] = []

    def enqueue(self, command: Command) -> None:
        self._queue.append(command)
        print(f"  Queued: {command.describe()}")

    def process_all(self) -> None:
        print(f"\n  Processing {len(self._queue)} queued commands:")
        while self._queue:
            command = self._queue.popleft()
            print(f"  Executing: {command.describe()}")
            if command.execute():
                self._history.append(command)
                self._undo_stack.append(command)

    def undo_last(self) -> None:
        if not self._undo_stack:
            print("  Nothing to undo.")
            return
        command = self._undo_stack.pop()
        print(f"  Undoing: {command.describe()}")
        command.undo()

    def print_history(self) -> None:
        print("\n  Command History:")
        for i, cmd in enumerate(self._history, 1):
            print(f"    {i}. {cmd.describe()}")


# --- Usage ---
if __name__ == "__main__":
    manager = TaskManager()
    queue = CommandQueue()

    # Queue up commands (not executed yet)
    queue.enqueue(AddTaskCommand(manager, "Design API", priority=3))
    queue.enqueue(AddTaskCommand(manager, "Write tests", priority=2))
    queue.enqueue(AddTaskCommand(manager, "Deploy to staging", priority=1))
    queue.enqueue(CompleteTaskCommand(manager, "Design API"))

    # Process all queued commands at once
    queue.process_all()
    manager.list_tasks()

    # Undo the last command
    print("\n  --- Undo last command ---")
    queue.undo_last()
    manager.list_tasks()

    # Macro command
    print("\n  --- Macro: Sprint Setup ---")
    macro = MacroCommand("Sprint Setup", [
        AddTaskCommand(manager, "Sprint planning", priority=3),
        AddTaskCommand(manager, "Daily standup setup", priority=2),
        AddTaskCommand(manager, "Create board", priority=1),
    ])
    queue.enqueue(macro)
    queue.process_all()
    manager.list_tasks()

    queue.print_history()
```

**Output:**
```
  Queued: Add task 'Design API'
  Queued: Add task 'Write tests'
  Queued: Add task 'Deploy to staging'
  Queued: Complete task 'Design API'

  Processing 4 queued commands:
  Executing: Add task 'Design API'
    [TaskManager] Added: 'Design API' (priority=3)
  Executing: Add task 'Write tests'
    [TaskManager] Added: 'Write tests' (priority=2)
  Executing: Add task 'Deploy to staging'
    [TaskManager] Added: 'Deploy to staging' (priority=1)
  Executing: Complete task 'Design API'
    [TaskManager] Completed: 'Design API'
    Current tasks:
      [DONE] Design API (priority=3)
      [TODO] Write tests (priority=2)
      [TODO] Deploy to staging (priority=1)

  --- Undo last command ---
  Undoing: Complete task 'Design API'
    [TaskManager] Uncompleted: 'Design API'
    Current tasks:
      [TODO] Design API (priority=3)
      [TODO] Write tests (priority=2)
      [TODO] Deploy to staging (priority=1)

  --- Macro: Sprint Setup ---
  Queued: Macro 'Sprint Setup' (3 commands)

  Processing 1 queued commands:
  Executing: Macro 'Sprint Setup' (3 commands)
  [Macro] Executing 'Sprint Setup' (3 commands)
    [TaskManager] Added: 'Sprint planning' (priority=3)
    [TaskManager] Added: 'Daily standup setup' (priority=2)
    [TaskManager] Added: 'Create board' (priority=1)
    Current tasks:
      [TODO] Design API (priority=3)
      [TODO] Sprint planning (priority=3)
      [TODO] Daily standup setup (priority=2)
      [TODO] Write tests (priority=2)
      [TODO] Create board (priority=1)
      [TODO] Deploy to staging (priority=1)

  Command History:
    1. Add task 'Design API'
    2. Add task 'Write tests'
    3. Add task 'Deploy to staging'
    4. Complete task 'Design API'
    5. Macro 'Sprint Setup' (3 commands)
```

---

## Real-World Use Case: Transaction Logging

```java
// TransactionLog.java -- Persist commands for replay
public class TransactionLog {
    private final List<String> entries = new ArrayList<>();

    public void log(Command command, String status) {
        String entry = String.format("[%s] %s: %s",
            LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
            status, command.describe());
        entries.add(entry);
    }

    public void printLog() {
        System.out.println("\nTransaction Log:");
        entries.forEach(e -> System.out.println("  " + e));
    }

    // In a real system, you would serialize commands to a database
    // and replay them to reconstruct state (Event Sourcing)
}

// AuditedTransactionManager.java
public class AuditedTransactionManager {
    private final TransactionManager txManager = new TransactionManager();
    private final TransactionLog log = new TransactionLog();

    public void execute(Command command) {
        try {
            txManager.execute(command);
            log.log(command, "EXECUTED");
        } catch (Exception e) {
            log.log(command, "FAILED: " + e.getMessage());
            throw e;
        }
    }

    public void undo() {
        // The last executed command is logged as undone
        txManager.undo();
    }

    public TransactionLog getLog() {
        return log;
    }
}
```

---

## Real-World Use Case: CQRS Introduction

CQRS separates read operations from write operations. Commands (writes) and Queries (reads) use different models.

```
Traditional CRUD:                   CQRS:
+-------------------+               +---------+     +----------+
|   Single Model    |               | Command |     |  Query   |
|                   |               | Model   |     |  Model   |
| Create            |               | (Write) |     | (Read)   |
| Read              |               +---------+     +----------+
| Update            |                    |               ^
| Delete            |                    v               |
|                   |               +----------+    +----------+
+-------------------+               | Write DB |    | Read DB  |
        |                           +----------+    +----------+
        v                                |               ^
  +----------+                           +--- sync ------+
  | Database |
  +----------+

CQRS uses the Command pattern at its core:
- Each write operation is a Command object
- Commands are validated, executed, and stored
- The read side is optimized separately
```

```java
// CQRS-style command
public class CreateOrderCommand {
    private final String customerId;
    private final List<OrderItem> items;
    private final String shippingAddress;

    // Constructor, getters...
}

// Command Handler
@Service
public class CreateOrderCommandHandler {

    private final OrderRepository orderRepository;
    private final ApplicationEventPublisher eventPublisher;

    public OrderId handle(CreateOrderCommand command) {
        // Validate
        validateCustomer(command.getCustomerId());
        validateItems(command.getItems());

        // Execute
        Order order = Order.create(
            command.getCustomerId(),
            command.getItems(),
            command.getShippingAddress()
        );
        orderRepository.save(order);

        // Publish event for the read side to update
        eventPublisher.publishEvent(new OrderCreatedEvent(order));

        return order.getId();
    }
}

// Query side -- separate, optimized read model
@Service
public class OrderQueryService {

    private final OrderReadRepository readRepository;

    public OrderSummaryDTO getOrderSummary(String orderId) {
        // Reads from a denormalized, read-optimized store
        return readRepository.findSummaryById(orderId);
    }
}
```

---

## When to Use / When NOT to Use

### Use Command When

| Scenario | Why Command Helps |
|---|---|
| Undo/redo functionality | Commands store state needed to reverse |
| Task/job queues | Commands can be serialized and queued |
| Transaction logging | Commands describe exactly what happened |
| Macro recording | Group commands into composite macros |
| Deferred execution | Create now, execute later |
| Audit trails | Every action is a named, logged object |

### Do NOT Use Command When

| Scenario | Why Not |
|---|---|
| Simple one-shot operations | Direct method calls are simpler |
| No need for undo or queuing | The overhead is not justified |
| Operations that cannot be undone | Delete-from-external-API has no undo |
| Very high throughput paths | Object creation overhead may matter |

---

## Common Mistakes

### Mistake 1: Commands That Cannot Be Undone

```java
// BAD -- No way to undo
public class SendEmailCommand implements Command {
    @Override
    public void execute() {
        emailService.send(email);  // Sent. Cannot unsend.
    }

    @Override
    public void undo() {
        // What do we do here? Nothing useful.
        throw new UnsupportedOperationException("Cannot unsend email");
    }
}

// BETTER -- Be honest about it
public class SendEmailCommand implements Command {
    private boolean executed = false;

    @Override
    public void undo() {
        if (executed) {
            // Log that a compensating action is needed
            auditLog.warn("Email sent to " + recipient
                + " -- manual follow-up required for reversal");
        }
    }
}
```

### Mistake 2: Mutable Commands

```java
// BAD -- Command state can be corrupted
public class DepositCommand implements Command {
    public double amount;  // Public and mutable!

    @Override
    public void execute() {
        account.deposit(amount);
    }
}

// GOOD -- Immutable commands
public class DepositCommand implements Command {
    private final BankAccount account;
    private final double amount;  // Private and final

    public DepositCommand(BankAccount account, double amount) {
        this.account = account;
        this.amount = amount;
    }
}
```

### Mistake 3: Commands That Do Too Much

```java
// BAD -- One command does everything
public class ProcessOrderCommand implements Command {
    @Override
    public void execute() {
        validateOrder();
        chargePayment();
        updateInventory();
        sendConfirmation();
        notifyWarehouse();
    }
}

// GOOD -- Compose small commands
MacroCommand processOrder = new MacroCommand("ProcessOrder",
    List.of(
        new ValidateOrderCommand(order),
        new ChargePaymentCommand(order),
        new UpdateInventoryCommand(order),
        new SendConfirmationCommand(order)
    )
);
```

---

## Best Practices

1. **Keep commands small and focused.** One command, one action. Use `MacroCommand` to compose them.

2. **Make commands immutable.** Set all fields in the constructor and make them `final`.

3. **Store undo state at execution time.** The command should capture whatever it needs to reverse itself when `execute()` runs.

4. **Handle partial failures in macros.** If the third command in a macro fails, undo the first two.

5. **Separate command creation from execution.** The client creates commands; the invoker decides when to run them.

6. **Log commands for auditing.** Every command is a clear record of what action was requested and by whom.

7. **Consider serialization.** If commands need to survive restarts (job queues), they must be serializable.

---

## Quick Summary

```
+---------------------------------------------------------------+
|                    COMMAND PATTERN SUMMARY                      |
+---------------------------------------------------------------+
| Intent:     Encapsulate a request as an object, allowing you   |
|             to parameterize, queue, log, and undo operations.  |
+---------------------------------------------------------------+
| Problem:    Method calls cannot be undone, queued, or replayed |
| Solution:   Wrap each action in a Command object               |
+---------------------------------------------------------------+
| Key parts:                                                     |
|   - Command interface (execute + undo)                         |
|   - Concrete commands (each wraps one action)                  |
|   - Receiver (the object being acted upon)                     |
|   - Invoker (manages command lifecycle)                        |
+---------------------------------------------------------------+
| Enables:    Undo/redo, queuing, logging, macros, CQRS          |
+---------------------------------------------------------------+
```

---

## Key Points

- The Command pattern turns requests into objects with `execute()` and `undo()` methods.
- Commands can be stored in stacks (undo/redo), queues (task processing), or logs (audit trails).
- `MacroCommand` groups multiple commands into a single composite operation.
- CQRS uses commands to separate the write path from the read path.
- Commands should be immutable -- store all parameters at construction time.
- Not every operation can be undone. Be honest about it in your `undo()` implementation.

---

## Practice Questions

1. In the bank account example, what happens if the `TransferCommand.execute()` succeeds on `withdraw` but fails on `deposit`? How should the command handle this partial failure?

2. How would you serialize a `Command` to store it in a database for later replay? What challenges arise with commands that reference in-memory objects?

3. A macro command has five sub-commands. The fourth one fails. Should you undo the first three? Always? What factors influence this decision?

4. How does the Command pattern differ from simply using a `Runnable` or a lambda in Java? What does Command add that `Runnable` does not?

5. In CQRS, why is the read model eventually consistent? What problems can this cause, and how do real systems handle them?

---

## Exercises

### Exercise 1: Text Editor Undo/Redo

Build a simple text editor that supports `InsertTextCommand`, `DeleteTextCommand`, and `ReplaceTextCommand`. Each command must support `undo()`. Implement a `TextEditorHistory` that lets the user undo and redo multiple steps.

### Exercise 2: Job Queue with Priority

Create a command-based job queue where commands have priorities. Implement `HighPriorityCommand`, `NormalCommand`, and `LowPriorityCommand`. The queue should process high-priority commands first. Add the ability to cancel queued (not yet executed) commands.

### Exercise 3: Event-Sourced Shopping Cart

Build a shopping cart using event sourcing. Every change (add item, remove item, change quantity) is a command that produces an event. Store all events in a list. Rebuild the cart state by replaying events from the beginning. Verify that replaying produces the same final state.

---

## What Is Next?

Commands let you treat individual requests as objects. But what if you have a multi-step process where the overall algorithm is fixed, but individual steps vary? In the next chapter, we explore the **Template Method pattern** -- a way to define the skeleton of an algorithm in a base class while letting subclasses fill in the specific steps.
