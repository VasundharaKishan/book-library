# Chapter 20: Transaction Management

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand ACID properties and why transactions matter
- Use Spring's @Transactional annotation effectively
- Explain and apply propagation levels (REQUIRED, REQUIRES_NEW, etc.)
- Understand isolation levels and choose the right one
- Use readOnly transactions for performance optimization
- Configure rollback rules for checked and unchecked exceptions
- Avoid common pitfalls: self-invocation, checked exception swallowing
- Use programmatic transactions with TransactionTemplate
- Debug transaction issues in Spring Boot applications

---

## Why Transactions Matter

A transaction groups multiple database operations into a single unit of work — either ALL succeed or ALL fail. Without transactions, a failure midway through an operation leaves your data in an inconsistent state.

```
Without Transactions — Data Corruption:
+------------------------------------------------------------------+
|                                                                   |
|  Transfer $500 from Account A to Account B:                       |
|                                                                   |
|  Step 1: UPDATE accounts SET balance = balance - 500              |
|          WHERE id = 'A'                         --> SUCCESS       |
|          Account A: $1000 --> $500                                |
|                                                                   |
|  Step 2: UPDATE accounts SET balance = balance + 500              |
|          WHERE id = 'B'                         --> CRASH!        |
|          Server crashes, database restarts                        |
|                                                                   |
|  Result: $500 disappeared! A lost money, B never received it.    |
|                                                                   |
+------------------------------------------------------------------+

With Transactions — Atomicity:
+------------------------------------------------------------------+
|                                                                   |
|  BEGIN TRANSACTION                                                |
|                                                                   |
|  Step 1: UPDATE accounts SET balance = balance - 500              |
|          WHERE id = 'A'                         --> SUCCESS       |
|                                                                   |
|  Step 2: UPDATE accounts SET balance = balance + 500              |
|          WHERE id = 'B'                         --> CRASH!        |
|                                                                   |
|  ROLLBACK (automatic on crash)                                    |
|  Account A: Still $1000 (change was rolled back)                  |
|  Account B: Still $500 (never changed)                            |
|                                                                   |
|  Result: Data is consistent. No money lost.                       |
+------------------------------------------------------------------+
```

---

## ACID Properties

```
ACID Properties:
+------------------------------------------------------------------+
|                                                                   |
|  A - Atomicity                                                    |
|  "All or nothing"                                                 |
|  Either all operations in the transaction succeed,                |
|  or none of them do. Partial changes are rolled back.             |
|                                                                   |
|  C - Consistency                                                  |
|  "Rules are always followed"                                      |
|  The database moves from one valid state to another.              |
|  Constraints (FK, unique, check) are never violated.              |
|                                                                   |
|  I - Isolation                                                    |
|  "Transactions don't interfere"                                   |
|  Concurrent transactions see a consistent view of data.           |
|  One transaction's uncommitted changes are invisible to others.   |
|                                                                   |
|  D - Durability                                                   |
|  "Committed changes survive crashes"                               |
|  Once a transaction is committed, the data is permanently saved.  |
|  Even if the server crashes immediately after commit.             |
+------------------------------------------------------------------+
```

---

## Spring's @Transactional

In Spring Boot, you manage transactions declaratively with `@Transactional`:

```java
@Service
public class TransferService {

    private final AccountRepository accountRepository;

    @Transactional    // Everything in this method runs in ONE transaction
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        Account from = accountRepository.findById(fromId).orElseThrow();
        Account to = accountRepository.findById(toId).orElseThrow();

        if (from.getBalance().compareTo(amount) < 0) {
            throw new InsufficientFundsException("Not enough balance");
        }

        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));

        // No explicit save needed — dirty checking handles it
        // If any exception is thrown, everything rolls back
    }
}
```

```
How @Transactional Works:
+------------------------------------------------------------------+
|                                                                   |
|  Spring creates a PROXY around your service class:                |
|                                                                   |
|  Caller --> [Proxy] --> [Your Service Method]                     |
|                |                                                  |
|                |  1. Begin transaction                            |
|                |  2. Open EntityManager / persistence context     |
|                |  3. Call your method                              |
|                |  4a. Method returns normally:                     |
|                |      --> Flush (dirty checking, SQL sent)        |
|                |      --> Commit transaction                      |
|                |  4b. Method throws RuntimeException:             |
|                |      --> Rollback transaction                    |
|                |  5. Close EntityManager                          |
|                                                                   |
|  The proxy intercepts the method call and wraps it in a          |
|  transaction. Your code does not manage transactions explicitly.  |
+------------------------------------------------------------------+
```

### @Transactional Attributes

```java
@Transactional(
    readOnly = false,                    // Default: false
    propagation = Propagation.REQUIRED,  // Default: REQUIRED
    isolation = Isolation.DEFAULT,       // Default: database default
    timeout = -1,                        // Default: no timeout (-1)
    rollbackFor = {},                    // Additional exception types to rollback
    noRollbackFor = {}                   // Exception types to NOT rollback
)
```

---

## Propagation Levels

Propagation defines what happens when a transactional method calls another transactional method.

```
Propagation Levels:
+------------------------------------------------------------------+
|                                                                   |
|  REQUIRED (default):                                              |
|  "Join existing or create new"                                    |
|  If a transaction exists, join it. If not, create a new one.     |
|                                                                   |
|  Caller                    Service A              Service B       |
|    |                          |                      |            |
|    |  call A.methodA()        |                      |            |
|    |------------------------->|                      |            |
|    |  [Tx1 starts]            |                      |            |
|    |                          |  call B.methodB()    |            |
|    |                          |--------------------->|            |
|    |                          |  [Joins Tx1]         |            |
|    |                          |  (same transaction!) |            |
|    |                          |<---------------------|            |
|    |  [Tx1 commits]           |                      |            |
|    |<-------------------------|                      |            |
|                                                                   |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|                                                                   |
|  REQUIRES_NEW:                                                    |
|  "Always create a new transaction"                                |
|  Suspends the current transaction and starts a new one.           |
|  The new transaction commits/rollbacks independently.             |
|                                                                   |
|  Caller                    Service A              Service B       |
|    |                          |                      |            |
|    |  call A.methodA()        |                      |            |
|    |------------------------->|                      |            |
|    |  [Tx1 starts]            |                      |            |
|    |                          |  call B.methodB()    |            |
|    |                          |--------------------->|            |
|    |                          |  [Tx1 suspended]     |            |
|    |                          |  [Tx2 starts]        |            |
|    |                          |  [Tx2 commits]       |            |
|    |                          |<---------------------|            |
|    |                          |  [Tx1 resumes]       |            |
|    |  [Tx1 commits]           |                      |            |
|    |<-------------------------|                      |            |
|                                                                   |
|  Use case: Audit logging that must persist even if the            |
|  main transaction rolls back.                                     |
+------------------------------------------------------------------+
```

```
All Propagation Levels:
+------------------------------------------------------------------+
|                                                                   |
|  Level            Existing Tx?  No Existing Tx?  Use When         |
|  ----------------------------------------------------------------|
|  REQUIRED         Join it       Create new       Default, most    |
|  (default)                                       cases            |
|                                                                   |
|  REQUIRES_NEW     Suspend,      Create new       Independent ops  |
|                   create new                     (audit logs)     |
|                                                                   |
|  SUPPORTS         Join it       Run without      Read-only        |
|                                 transaction      queries          |
|                                                                   |
|  NOT_SUPPORTED    Suspend it    Run without      External API     |
|                                 transaction      calls            |
|                                                                   |
|  MANDATORY        Join it       THROW            Must be called   |
|                                 exception!       within Tx        |
|                                                                   |
|  NEVER            THROW         Run without      Must NOT be      |
|                   exception!    transaction      called in Tx     |
|                                                                   |
|  NESTED           Create        Create new       Savepoints       |
|                   savepoint                      (partial rollback)|
+------------------------------------------------------------------+
```

### REQUIRES_NEW Example: Audit Logging

```java
@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final AuditService auditService;

    @Transactional
    public void cancelOrder(Long orderId) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        order.setStatus("CANCELLED");

        // This runs in a SEPARATE transaction
        // Even if cancelOrder() rolls back, the audit log persists
        auditService.log("ORDER_CANCELLED", orderId);

        // If this throws, the order cancellation rolls back
        // but the audit log is already committed
        processRefund(order);
    }
}

@Service
public class AuditService {

    private final AuditLogRepository auditLogRepository;

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void log(String action, Long entityId) {
        auditLogRepository.save(new AuditLog(action, entityId));
        // Commits independently of the caller's transaction
    }
}
```

---

## Isolation Levels

Isolation controls how concurrent transactions interact and what data they can see.

```
Concurrency Problems:
+------------------------------------------------------------------+
|                                                                   |
|  Dirty Read:                                                      |
|  Tx1 writes data, Tx2 reads it BEFORE Tx1 commits.              |
|  If Tx1 rolls back, Tx2 has read data that never existed.        |
|                                                                   |
|  Tx1: UPDATE salary = 100000 ... (not committed yet)             |
|  Tx2: SELECT salary --> reads 100000 (dirty!)                    |
|  Tx1: ROLLBACK                                                    |
|  Tx2 now has stale data that was never actually committed.       |
|                                                                   |
|  Non-Repeatable Read:                                             |
|  Tx2 reads data twice and gets different results because          |
|  Tx1 committed a change between the two reads.                   |
|                                                                   |
|  Tx2: SELECT salary --> 80000                                    |
|  Tx1: UPDATE salary = 100000 + COMMIT                            |
|  Tx2: SELECT salary --> 100000 (different from first read!)      |
|                                                                   |
|  Phantom Read:                                                    |
|  Tx2 runs a range query twice and gets different rows because    |
|  Tx1 inserted or deleted rows between the two queries.           |
|                                                                   |
|  Tx2: SELECT * WHERE dept='Eng' --> 10 rows                      |
|  Tx1: INSERT new employee in Eng + COMMIT                        |
|  Tx2: SELECT * WHERE dept='Eng' --> 11 rows (phantom row!)      |
+------------------------------------------------------------------+
```

```
Isolation Levels:
+------------------------------------------------------------------+
|                                                                   |
|  Level               Dirty    Non-Repeatable  Phantom             |
|                      Read     Read            Read                |
|  ----------------------------------------------------------------|
|  READ_UNCOMMITTED    Possible Possible        Possible            |
|                      (worst isolation, best performance)          |
|                                                                   |
|  READ_COMMITTED      Prevented Possible       Possible            |
|                      (most common default)                        |
|                                                                   |
|  REPEATABLE_READ     Prevented Prevented      Possible            |
|                      (good isolation)                             |
|                                                                   |
|  SERIALIZABLE        Prevented Prevented      Prevented           |
|                      (best isolation, worst performance)          |
|                                                                   |
|  DEFAULT             Uses the database's default level            |
|                      (usually READ_COMMITTED)                     |
+------------------------------------------------------------------+
```

```java
// Set isolation on a specific method
@Transactional(isolation = Isolation.REPEATABLE_READ)
public BigDecimal calculateBalance(Long accountId) {
    // Multiple reads guaranteed to see the same data
    Account account = accountRepository.findById(accountId).orElseThrow();
    List<Transaction> txns = transactionRepository.findByAccountId(accountId);
    return computeBalance(account, txns);
}
```

```
Choosing an Isolation Level:
+------------------------------------------------------------------+
|                                                                   |
|  DEFAULT (READ_COMMITTED) — use for most operations               |
|  Prevents dirty reads. Good enough for most CRUD.                 |
|                                                                   |
|  REPEATABLE_READ — use for financial calculations                 |
|  When you read data multiple times and need consistency.          |
|  Example: Balance calculation, report generation.                 |
|                                                                   |
|  SERIALIZABLE — use rarely, for critical operations               |
|  Maximum safety but worst performance (transactions queue up).    |
|  Example: Seat reservation, inventory deduction.                  |
|                                                                   |
|  READ_UNCOMMITTED — almost never use                              |
|  Only for approximate analytics where dirty reads are acceptable. |
+------------------------------------------------------------------+
```

---

## Read-Only Transactions

```java
@Transactional(readOnly = true)
public List<Employee> getAllEmployees() {
    return employeeRepository.findAll();
}
```

```
readOnly = true Optimizations:
+------------------------------------------------------------------+
|                                                                   |
|  What readOnly = true does:                                       |
|                                                                   |
|  1. Hibernate skips dirty checking                                |
|     - No snapshot taken on entity load                            |
|     - No field-by-field comparison on flush                       |
|     - Saves CPU and memory                                        |
|                                                                   |
|  2. Hibernate sets flush mode to MANUAL                           |
|     - No automatic flushing before queries                        |
|     - No UPDATE/INSERT/DELETE SQL generated                       |
|                                                                   |
|  3. Database hint (some drivers)                                  |
|     - Some JDBC drivers optimize for read-only connections        |
|     - May route to read replicas in master-slave setups           |
|                                                                   |
|  Use readOnly = true for:                                         |
|  - All GET/read endpoints                                         |
|  - Report generation                                              |
|  - Search and listing operations                                  |
|  - Any method that does not modify data                           |
|                                                                   |
|  WARNING: If you modify an entity in a readOnly transaction,     |
|  the change is SILENTLY IGNORED (not an error, just not saved).  |
+------------------------------------------------------------------+
```

---

## Rollback Rules

By default, Spring rolls back on **unchecked exceptions** (RuntimeException and its subclasses) but commits on **checked exceptions**:

```
Default Rollback Behavior:
+------------------------------------------------------------------+
|                                                                   |
|  Exception Type              Default Behavior                     |
|  ----------------------------------------------------------------|
|  RuntimeException             ROLLBACK                            |
|  (NullPointerException,       (transaction is aborted)            |
|   IllegalArgumentException,                                       |
|   DataIntegrityViolation...)                                      |
|                                                                   |
|  Error                        ROLLBACK                            |
|  (OutOfMemoryError, etc.)                                         |
|                                                                   |
|  Checked Exception            COMMIT!                             |
|  (IOException, SQLException,  (transaction is committed!)         |
|   custom checked exceptions)  This surprises many developers.    |
+------------------------------------------------------------------+
```

### Customizing Rollback

```java
// Rollback on a specific checked exception
@Transactional(rollbackFor = BusinessException.class)
public void processOrder(Order order) throws BusinessException {
    // If BusinessException is thrown, transaction rolls back
    // (normally checked exceptions would commit)
}

// Rollback on all exceptions
@Transactional(rollbackFor = Exception.class)
public void criticalOperation() throws Exception {
    // Any exception causes rollback
}

// Do NOT rollback on a specific runtime exception
@Transactional(noRollbackFor = ItemNotFoundException.class)
public void processItems(List<Long> ids) {
    for (Long id : ids) {
        try {
            processItem(id);
        } catch (ItemNotFoundException e) {
            // Log and continue — transaction should NOT rollback
            log.warn("Item {} not found, skipping", id);
        }
    }
}
```

---

## Common Pitfall: Self-Invocation

The most common `@Transactional` bug — calling a transactional method from within the same class bypasses the proxy:

```
Self-Invocation Problem:
+------------------------------------------------------------------+
|                                                                   |
|  @Service                                                         |
|  public class OrderService {                                      |
|                                                                   |
|      public void processOrders(List<Long> ids) {  // No @Tx      |
|          for (Long id : ids) {                                    |
|              processOrder(id);  // Calls method below             |
|          }                                                        |
|      }                                                            |
|                                                                   |
|      @Transactional                                               |
|      public void processOrder(Long id) {  // Has @Tx             |
|          // But @Transactional is IGNORED!                        |
|          // Because this call bypasses the proxy.                 |
|      }                                                            |
|  }                                                                |
|                                                                   |
|  Why? Spring's proxy intercepts calls FROM OUTSIDE the class.    |
|  Internal calls (this.processOrder) go directly to the method,   |
|  skipping the proxy that manages the transaction.                 |
|                                                                   |
|  External call:  Caller --> [Proxy] --> processOrder  (Tx works)  |
|  Self-invocation: processOrders --> processOrder     (Tx skipped!)|
|                                                                   |
+------------------------------------------------------------------+
```

### Fixes for Self-Invocation

```
Fix 1: Move the method to a separate service (BEST):
+------------------------------------------------------------------+
|  @Service                                                         |
|  public class OrderBatchService {                                 |
|      private final OrderService orderService;  // Inject          |
|                                                                   |
|      public void processOrders(List<Long> ids) {                  |
|          for (Long id : ids) {                                    |
|              orderService.processOrder(id);  // External call!    |
|          }                     // Goes through proxy -- Tx works  |
|      }                                                            |
|  }                                                                |
|                                                                   |
|  @Service                                                         |
|  public class OrderService {                                      |
|      @Transactional                                               |
|      public void processOrder(Long id) { ... }                   |
|  }                                                                |
+------------------------------------------------------------------+

Fix 2: Put @Transactional on the calling method:
+------------------------------------------------------------------+
|  @Transactional  // Wrap the entire loop in one transaction       |
|  public void processOrders(List<Long> ids) {                      |
|      for (Long id : ids) {                                        |
|          processOrder(id);  // Internal call, but we're already   |
|      }                      // inside a transaction               |
|  }                                                                |
+------------------------------------------------------------------+
```

---

## Programmatic Transactions

For cases where `@Transactional` is not flexible enough, use `TransactionTemplate`:

```java
@Service
public class BatchService {

    private final TransactionTemplate transactionTemplate;
    private final EmployeeRepository employeeRepository;

    public BatchService(PlatformTransactionManager txManager,
                        EmployeeRepository employeeRepository) {
        this.transactionTemplate = new TransactionTemplate(txManager);
        this.employeeRepository = employeeRepository;
    }

    public void processBatch(List<EmployeeData> dataList) {
        for (int i = 0; i < dataList.size(); i += 50) {
            int end = Math.min(i + 50, dataList.size());
            List<EmployeeData> batch = dataList.subList(i, end);

            // Each batch in its own transaction
            transactionTemplate.execute(status -> {
                for (EmployeeData data : batch) {
                    employeeRepository.save(new Employee(data.getName()));
                }
                return null;
            });
            // Transaction committed. If next batch fails, previous batches are safe.
        }
    }

    public Employee findOrCreate(String email) {
        return transactionTemplate.execute(status -> {
            return employeeRepository.findByEmail(email)
                .orElseGet(() -> employeeRepository.save(new Employee(email)));
        });
    }
}
```

```
@Transactional vs TransactionTemplate:
+------------------------------------------------------------------+
|                                                                   |
|  @Transactional (declarative):                                    |
|  + Clean, simple, less code                                       |
|  + Covers 95% of use cases                                       |
|  - Entire method is one transaction                               |
|  - Self-invocation issues                                         |
|                                                                   |
|  TransactionTemplate (programmatic):                              |
|  + Fine-grained control                                           |
|  + Multiple transactions in one method                            |
|  + No self-invocation issues                                      |
|  - More verbose code                                              |
|  - Must manage template manually                                  |
|                                                                   |
|  Use @Transactional for most cases.                               |
|  Use TransactionTemplate for batch processing where you need     |
|  multiple smaller transactions within one method.                 |
+------------------------------------------------------------------+
```

---

## Transaction Best Practices Summary

```
Transaction Best Practices:
+------------------------------------------------------------------+
|                                                                   |
|  1. Put @Transactional on service methods, not repositories       |
|     Repositories already run in a transaction per method.         |
|     Services define the business transaction boundary.            |
|                                                                   |
|  2. Use readOnly = true for all read operations                   |
|     Saves CPU (no dirty checking) and memory (no snapshots).      |
|                                                                   |
|  3. Keep transactions short                                       |
|     Do not call external APIs, send emails, or do file I/O       |
|     inside a transaction. These hold DB connections and locks.    |
|                                                                   |
|  4. Do not swallow exceptions silently                            |
|     Catching an exception inside @Transactional prevents          |
|     rollback. Rethrow or use noRollbackFor explicitly.           |
|                                                                   |
|  5. Beware of self-invocation                                     |
|     Calling @Transactional methods from the same class            |
|     bypasses the proxy. Split into separate services.             |
|                                                                   |
|  6. Use rollbackFor for checked exceptions                        |
|     @Transactional(rollbackFor = Exception.class) if your        |
|     methods throw checked exceptions that should rollback.        |
|                                                                   |
|  7. Default isolation is usually fine                              |
|     READ_COMMITTED covers most cases. Use REPEATABLE_READ        |
|     only for financial calculations or multi-read consistency.    |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Self-invocation bypasses @Transactional**: Calling a `@Transactional` method from within the same class goes directly to the method, not through the proxy. The transaction annotation is ignored.

2. **Checked exceptions do not trigger rollback**: By default, only `RuntimeException` and `Error` cause rollback. A method throwing `IOException` will COMMIT the transaction. Use `rollbackFor` to change this.

3. **Long transactions holding connections**: Calling external APIs, sending emails, or performing file I/O inside a transaction holds the database connection for the entire duration. Move non-DB work outside the transaction.

4. **Catching exceptions and preventing rollback**: Wrapping code in try-catch inside `@Transactional` prevents the exception from reaching the proxy, so the transaction commits with partial changes.

5. **Using @Transactional on private methods**: Spring proxies cannot intercept private methods. `@Transactional` on a private method is silently ignored.

6. **Modifying data in readOnly transactions**: Changes to entities in a `readOnly = true` transaction are silently discarded. No error is thrown, but the data is not saved.

---

## Summary

- **Transactions** ensure atomicity — all operations succeed or all fail. ACID properties (Atomicity, Consistency, Isolation, Durability) guarantee data integrity.

- **@Transactional** is Spring's declarative transaction management. It creates a proxy that begins a transaction before the method and commits/rollbacks after.

- **Propagation** controls behavior when transactional methods call each other. `REQUIRED` (default) joins existing transactions. `REQUIRES_NEW` creates independent transactions.

- **Isolation levels** control concurrent transaction visibility. `READ_COMMITTED` (default) prevents dirty reads. Higher levels provide more safety at the cost of performance.

- **readOnly = true** skips dirty checking and snapshots, improving performance for read operations.

- **Rollback rules**: Unchecked exceptions rollback, checked exceptions commit by default. Use `rollbackFor` to customize.

- **Self-invocation** bypasses the proxy. Split transactional methods into separate services.

- **TransactionTemplate** provides programmatic control for batch processing with multiple transactions.

---

## Interview Questions

**Q1: What are the ACID properties?**

Atomicity (all or nothing), Consistency (valid state to valid state), Isolation (concurrent transactions don't interfere), Durability (committed data survives crashes).

**Q2: What is the default propagation level and what does it do?**

`REQUIRED` (default). If a transaction already exists, the method joins it. If no transaction exists, a new one is created. This means nested service calls share the same transaction.

**Q3: When would you use REQUIRES_NEW propagation?**

When an operation must commit independently of the calling transaction. Common use case: audit logging that must persist even if the main business operation rolls back.

**Q4: Why do checked exceptions not trigger rollback by default?**

Spring follows the EJB convention where checked exceptions indicate recoverable business conditions (order not found, insufficient funds) that the caller can handle. Unchecked exceptions indicate programming errors that should abort the transaction. Use `rollbackFor` to change this behavior.

**Q5: What is the self-invocation problem with @Transactional?**

When a method within a class calls another `@Transactional` method in the same class, the call goes directly to the method (bypassing the Spring proxy). The `@Transactional` annotation is ignored because there is no proxy to intercept the call. Fix by moving the transactional method to a separate service bean.

**Q6: What does readOnly = true do?**

It tells Hibernate to skip dirty checking (no snapshot comparison) and set flush mode to MANUAL (no SQL updates generated). This saves CPU and memory. Some JDBC drivers may also route to read replicas. Changes made to entities are silently discarded.

---

## Practice Exercises

**Exercise 1: Basic Transaction**
Create a transfer service that moves money between two accounts. Test: (a) successful transfer, (b) rollback on insufficient funds (throw RuntimeException), (c) verify both accounts unchanged after rollback.

**Exercise 2: Propagation**
Create `OrderService.placeOrder()` (REQUIRED) that calls `AuditService.logAction()` (REQUIRES_NEW). Throw an exception in `placeOrder` after calling `logAction`. Verify the order is rolled back but the audit log is committed.

**Exercise 3: Self-Invocation**
Create a service with `processAll()` calling `@Transactional processOne()`. Observe that `processOne`'s transaction is ignored. Fix by extracting to a separate service. Verify with SQL logging.

**Exercise 4: Rollback Rules**
Create a method that throws a custom checked exception. Observe it commits. Add `rollbackFor`. Verify it now rolls back.

**Exercise 5: Read-Only Optimization**
Enable Hibernate statistics. Run a query with and without `readOnly = true`. Compare the dirty checking overhead in statistics output.

---

## What Is Next?

In the next chapter, we will explore **Second-Level Cache and Query Cache** — how to cache entity data across transactions for improved performance. You will learn the difference between the first-level cache (persistence context) and the second-level cache, how to configure cache providers, and when caching helps vs when it hurts.
