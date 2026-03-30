# Chapter 25: Transactions — All or Nothing

## What You Will Learn

In this chapter, you will learn:

- What a transaction is and why it matters
- The ACID properties that keep your data safe
- How to use BEGIN, COMMIT, and ROLLBACK
- How to create SAVEPOINTs for partial rollbacks
- What isolation levels are and when to change them
- What deadlocks are and how to avoid them
- How to build a safe bank transfer and order placement system

## Why This Chapter Matters

Imagine you are at an ATM. You want to transfer 500 dollars from your savings account to your checking account. The ATM deducts 500 from savings, but right at that moment the power goes out. Your savings account is down 500 dollars, but your checking account never got the money. You just lost 500 dollars.

This is the exact problem transactions solve. A transaction wraps multiple operations into a single unit of work. Either everything succeeds together, or everything fails together. There is no in-between state where your money vanishes.

Every real application needs transactions. Online stores processing orders, banks transferring money, hospitals updating patient records — any time you need multiple changes to happen as one atomic unit, you need a transaction.

---

## Setting Up Our Practice Tables

Let us create tables we will use throughout this chapter:

```sql
CREATE TABLE accounts (
    account_id   SERIAL PRIMARY KEY,
    owner_name   VARCHAR(100) NOT NULL,
    balance      DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    account_type VARCHAR(20) NOT NULL
);

INSERT INTO accounts (owner_name, balance, account_type) VALUES
('Alice', 5000.00, 'checking'),
('Alice', 10000.00, 'savings'),
('Bob',   3000.00, 'checking'),
('Bob',   7500.00, 'savings');

CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    total       DECIMAL(10, 2) NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'pending'
);

CREATE TABLE order_items (
    item_id    SERIAL PRIMARY KEY,
    order_id   INT NOT NULL REFERENCES orders(order_id),
    product_id INT NOT NULL,
    quantity   INT NOT NULL,
    price      DECIMAL(10, 2) NOT NULL
);

CREATE TABLE inventory (
    product_id   SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    stock        INT NOT NULL DEFAULT 0
);

INSERT INTO inventory (product_name, stock) VALUES
('Laptop', 50),
('Mouse', 200),
('Keyboard', 150);
```

---

## What Is a Transaction?

A transaction is a group of SQL statements that execute as a single unit. Think of it like a package deal — you either get everything or nothing.

```
Without Transactions:              With Transactions:
+---------------------------+      +---------------------------+
| Step 1: Deduct from       |      | BEGIN                     |
|         savings   --> OK  |      |   Step 1: Deduct savings  |
| Step 2: Add to            |      |   Step 2: Add to checking |
|         checking --> FAIL |      | COMMIT (or ROLLBACK)      |
|                           |      |                           |
| Result: Money lost!       |      | Result: All or nothing!   |
+---------------------------+      +---------------------------+
```

### The ATM Analogy

Think of a transaction like using an ATM:

1. You insert your card (BEGIN the transaction)
2. You request a withdrawal (execute SQL statements)
3. The ATM dispenses cash and updates your balance (COMMIT)
4. If anything goes wrong, the ATM cancels everything (ROLLBACK)

The ATM never gives you cash without updating your balance, and it never updates your balance without giving you cash. Both things happen together or neither happens.

---

## ACID Properties

Every transaction follows four rules known as ACID. These rules guarantee your data stays consistent and safe.

```
+---------------------------------------------------+
|                 ACID Properties                    |
+---------------------------------------------------+
|                                                   |
|  A - Atomicity    : All or nothing                |
|  C - Consistency  : Data stays valid              |
|  I - Isolation    : Transactions do not interfere |
|  D - Durability   : Changes survive crashes       |
|                                                   |
+---------------------------------------------------+
```

### Atomicity — All or Nothing

Either every statement in the transaction succeeds, or none of them take effect. There is no partial completion.

**Real-life analogy**: Ordering a combo meal. You either get the burger, fries, and drink together, or you get nothing. The restaurant does not give you just the burger and forget the fries.

### Consistency — Data Stays Valid

A transaction moves the database from one valid state to another valid state. It cannot violate any rules (constraints, foreign keys, check constraints).

**Real-life analogy**: A chess game. Every move must follow the rules. You cannot move a pawn backward. The board always stays in a valid state.

### Isolation — Transactions Do Not Interfere

When two transactions run at the same time, they do not see each other's incomplete work. Each transaction acts as if it is the only one running.

**Real-life analogy**: Two people using different ATMs at the same time. Each person sees a consistent view of their account, not some half-updated version.

### Durability — Changes Survive Crashes

Once a transaction is committed, the changes are permanent. Even if the server crashes one second later, the data is safe.

**Real-life analogy**: Once you sign a contract and both parties have copies, the agreement stands even if the office burns down.

---

## BEGIN, COMMIT, and ROLLBACK

These three commands control transactions.

### Starting a Transaction with BEGIN

```sql
BEGIN;
```

This tells PostgreSQL: "Everything I do from now on is part of one transaction. Do not make anything permanent until I say so."

### Committing with COMMIT

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 500
WHERE account_id = 2;

UPDATE accounts
SET balance = balance + 500
WHERE account_id = 1;

COMMIT;
```

COMMIT says: "Everything worked. Make all the changes permanent."

Let us verify:

```sql
SELECT account_id, owner_name, balance, account_type
FROM accounts
WHERE owner_name = 'Alice';
```

```
 account_id | owner_name | balance  | account_type
------------+------------+----------+--------------
          1 | Alice      |  5500.00 | checking
          2 | Alice      |  9500.00 | savings
(2 rows)
```

The 500 dollars moved from savings to checking. Both updates happened together.

### Rolling Back with ROLLBACK

ROLLBACK says: "Something went wrong. Undo everything since BEGIN."

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100000
WHERE account_id = 3;

-- Oops! Bob only has 3000 in checking.
-- We should not allow this.

ROLLBACK;
```

After ROLLBACK, Bob's account is unchanged:

```sql
SELECT account_id, owner_name, balance, account_type
FROM accounts
WHERE account_id = 3;
```

```
 account_id | owner_name | balance | account_type
------------+------------+---------+--------------
          3 | Bob        | 3000.00 | checking
(1 row)
```

### How It Flows

```
BEGIN
  |
  v
+------------------+
| Execute SQL      |
| statements       |
+------------------+
  |            |
  | Success    | Error
  v            v
COMMIT      ROLLBACK
(save)      (undo all)
```

---

## A Practical Bank Transfer

Let us build a proper bank transfer that checks for sufficient funds:

```sql
BEGIN;

-- Step 1: Check if sender has enough money
-- (We read the balance first)
DO $$
DECLARE
    sender_balance DECIMAL(12,2);
BEGIN
    SELECT balance INTO sender_balance
    FROM accounts
    WHERE account_id = 2;  -- Alice's savings

    IF sender_balance < 2000.00 THEN
        RAISE EXCEPTION 'Insufficient funds. Balance: %', sender_balance;
    END IF;

    -- Step 2: Deduct from sender
    UPDATE accounts
    SET balance = balance - 2000.00
    WHERE account_id = 2;

    -- Step 3: Add to receiver
    UPDATE accounts
    SET balance = balance + 2000.00
    WHERE account_id = 3;

    RAISE NOTICE 'Transfer complete!';
END $$;

COMMIT;
```

Let us check the results:

```sql
SELECT account_id, owner_name, balance, account_type
FROM accounts
WHERE account_id IN (2, 3);
```

```
 account_id | owner_name | balance | account_type
------------+------------+---------+--------------
          2 | Alice      | 7500.00 | savings
          3 | Bob        | 5000.00 | checking
(2 rows)
```

If the balance check had failed, the RAISE EXCEPTION would have caused PostgreSQL to automatically rollback the entire transaction.

---

## SAVEPOINT — Partial Rollbacks

Sometimes you want to undo part of a transaction without losing everything. SAVEPOINTs let you create checkpoints within a transaction.

```
BEGIN
  |
  v
Statement 1  -----> saved
  |
  v
SAVEPOINT sp1
  |
  v
Statement 2  -----> can be undone
  |
  v
ROLLBACK TO sp1    (undoes Statement 2 only)
  |
  v
Statement 3  -----> saved
  |
  v
COMMIT             (saves Statement 1 and Statement 3)
```

### SAVEPOINT in Action

```sql
BEGIN;

-- Insert a valid order
INSERT INTO orders (customer_id, total, status)
VALUES (1, 150.00, 'confirmed');

SAVEPOINT before_items;

-- Try to insert order items
INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (1, 1, 1, 100.00);

INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (1, 2, 5, 10.00);

-- Oops, something went wrong with this batch of items
-- Roll back to the savepoint (keeps the order, removes items)
ROLLBACK TO before_items;

-- Insert corrected items instead
INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (1, 1, 1, 100.00);

INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (1, 3, 2, 25.00);

COMMIT;
```

After this transaction:
- The order exists (it was before the savepoint)
- Only the corrected items exist (the first batch was rolled back)

### Nested SAVEPOINTs

You can create multiple savepoints:

```sql
BEGIN;

INSERT INTO orders (customer_id, total) VALUES (2, 200.00);
SAVEPOINT sp1;

INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (2, 1, 1, 150.00);
SAVEPOINT sp2;

INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (2, 2, 10, 5.00);

-- Undo only the last insert
ROLLBACK TO sp2;

-- The order and first item still exist
COMMIT;
```

### Releasing SAVEPOINTs

When you no longer need a savepoint, you can release it to free resources:

```sql
BEGIN;
SAVEPOINT my_savepoint;
-- ... do some work ...
RELEASE SAVEPOINT my_savepoint;
-- Now my_savepoint cannot be rolled back to
COMMIT;
```

---

## Isolation Levels

When multiple transactions run at the same time, isolation levels control how much they can see of each other's work.

### The Problem: Concurrent Access

Imagine two bank tellers processing transactions on the same account at the same time:

```
Teller 1 (Transaction A)         Teller 2 (Transaction B)
-------------------------         -------------------------
Reads balance: $1000
                                  Reads balance: $1000
Deducts $200
Balance = $800
                                  Deducts $300
                                  Balance = $700
Commits ($800)
                                  Commits ($700)

Final balance: $700
Should be: $500  (1000 - 200 - 300)
```

This is called a "lost update" problem. Isolation levels prevent these kinds of issues.

### PostgreSQL Isolation Levels

PostgreSQL supports four isolation levels, but two are most commonly used:

```
+---------------------+------------------+----------------+---------------+
| Isolation Level     | Dirty Read       | Non-Repeatable | Phantom Read  |
|                     |                  | Read           |               |
+---------------------+------------------+----------------+---------------+
| READ UNCOMMITTED*   | Not possible     | Possible       | Possible      |
| READ COMMITTED      | Not possible     | Possible       | Possible      |
| REPEATABLE READ     | Not possible     | Not possible   | Not possible  |
| SERIALIZABLE        | Not possible     | Not possible   | Not possible  |
+---------------------+------------------+----------------+---------------+

* In PostgreSQL, READ UNCOMMITTED behaves like READ COMMITTED.
```

**Dirty Read**: Reading data that another transaction has changed but not yet committed.

**Non-Repeatable Read**: Reading the same row twice and getting different values because another transaction modified it in between.

**Phantom Read**: Running the same query twice and getting different rows because another transaction inserted or deleted rows.

### READ COMMITTED (Default)

This is PostgreSQL's default level. Each statement in a transaction sees only data that was committed before that statement began.

```sql
-- This is the default, but you can set it explicitly:
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

SELECT balance FROM accounts WHERE account_id = 1;
-- Returns the latest committed balance

-- If another transaction commits a change here,
-- the next SELECT will see the new value

SELECT balance FROM accounts WHERE account_id = 1;
-- Might return a different value!

COMMIT;
```

### REPEATABLE READ

Once a transaction reads data, it always sees the same data, even if other transactions modify it.

```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

SELECT balance FROM accounts WHERE account_id = 1;
-- Returns 5500.00

-- Even if another transaction changes this balance
-- and commits, this transaction still sees 5500.00

SELECT balance FROM accounts WHERE account_id = 1;
-- Still returns 5500.00

COMMIT;
```

### SERIALIZABLE

The strictest level. Transactions behave as if they ran one after another, not concurrently. If a conflict is detected, PostgreSQL will abort one of the transactions.

```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- All operations here are fully isolated
-- If a conflict is detected, PostgreSQL will raise:
-- ERROR: could not serialize access

COMMIT;
```

### When to Use Each Level

```
+-------------------+----------------------------------------+
| Level             | Use When                               |
+-------------------+----------------------------------------+
| READ COMMITTED    | Most everyday operations               |
|                   | Simple INSERT/UPDATE/DELETE             |
|                   | Default — use unless you need more     |
+-------------------+----------------------------------------+
| REPEATABLE READ   | Reports that need consistent data      |
|                   | Reading the same data multiple times   |
+-------------------+----------------------------------------+
| SERIALIZABLE      | Financial calculations                 |
|                   | Inventory management                   |
|                   | Any time correctness is critical       |
+-------------------+----------------------------------------+
```

---

## Deadlocks

A deadlock happens when two transactions are each waiting for the other to release a lock. Neither can proceed, so they are stuck forever.

### The Deadlock Analogy

Imagine two cars meeting on a narrow one-lane bridge from opposite sides. Neither can move forward, and neither will back up. They are deadlocked.

```
Transaction A                    Transaction B
-------------                    -------------
Locks Row 1                      Locks Row 2
  |                                |
  v                                v
Wants Row 2 (locked by B)       Wants Row 1 (locked by A)
  |                                |
  v                                v
WAITING...                       WAITING...

  ==> DEADLOCK! Neither can proceed.
```

### Deadlock Example

```sql
-- Transaction A (in one session):
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- Now locks row with account_id = 1

-- Transaction B (in another session):
BEGIN;
UPDATE accounts SET balance = balance - 50 WHERE account_id = 2;
-- Now locks row with account_id = 2

-- Transaction A tries:
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
-- WAITS... because B has locked account_id = 2

-- Transaction B tries:
UPDATE accounts SET balance = balance + 50 WHERE account_id = 1;
-- WAITS... because A has locked account_id = 1

-- DEADLOCK DETECTED!
-- PostgreSQL automatically kills one transaction:
-- ERROR: deadlock detected
```

### Preventing Deadlocks

**Rule 1: Always lock rows in the same order.**

```sql
-- GOOD: Both transactions lock accounts in order (1, then 2)
-- Transaction A:
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;

-- Transaction B:
BEGIN;
UPDATE accounts SET balance = balance + 50 WHERE account_id = 1;
UPDATE accounts SET balance = balance - 50 WHERE account_id = 2;
COMMIT;
```

**Rule 2: Keep transactions short.**

```sql
-- BAD: Long transaction holds locks for too long
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- ... lots of slow processing ...
-- ... calculating reports ...
-- ... sending emails ...
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;

-- GOOD: Do processing outside the transaction
-- Calculate everything first, then:
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;
```

**Rule 3: Use SELECT ... FOR UPDATE to explicitly lock rows you plan to modify.**

```sql
BEGIN;

-- Lock both rows upfront in a consistent order
SELECT * FROM accounts
WHERE account_id IN (1, 2)
ORDER BY account_id
FOR UPDATE;

-- Now safe to update both
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

COMMIT;
```

---

## Practical Example: Order Placement

Let us build a complete order placement system that uses transactions properly:

```sql
BEGIN;

-- Step 1: Check inventory for all items
DO $$
DECLARE
    laptop_stock INT;
    mouse_stock INT;
BEGIN
    -- Lock inventory rows to prevent race conditions
    SELECT stock INTO laptop_stock
    FROM inventory
    WHERE product_id = 1
    FOR UPDATE;

    SELECT stock INTO mouse_stock
    FROM inventory
    WHERE product_id = 2
    FOR UPDATE;

    -- Step 2: Verify sufficient stock
    IF laptop_stock < 1 THEN
        RAISE EXCEPTION 'Not enough laptops in stock. Available: %',
                         laptop_stock;
    END IF;

    IF mouse_stock < 2 THEN
        RAISE EXCEPTION 'Not enough mice in stock. Available: %',
                         mouse_stock;
    END IF;

    -- Step 3: Create the order
    INSERT INTO orders (customer_id, total, status)
    VALUES (1, 1020.00, 'confirmed');

    -- Step 4: Add order items
    INSERT INTO order_items (order_id, product_id, quantity, price)
    VALUES
        (currval('orders_order_id_seq'), 1, 1, 1000.00),
        (currval('orders_order_id_seq'), 2, 2, 10.00);

    -- Step 5: Reduce inventory
    UPDATE inventory SET stock = stock - 1 WHERE product_id = 1;
    UPDATE inventory SET stock = stock - 2 WHERE product_id = 2;

    RAISE NOTICE 'Order placed successfully!';
END $$;

COMMIT;
```

Let us verify everything worked:

```sql
SELECT * FROM orders WHERE customer_id = 1;
```

```
 order_id | customer_id | order_date |  total  |  status
----------+-------------+------------+---------+-----------
        1 |           1 | 2024-01-15 | 1020.00 | confirmed
(1 row)
```

```sql
SELECT * FROM order_items WHERE order_id = 1;
```

```
 item_id | order_id | product_id | quantity |  price
---------+----------+------------+----------+---------
       1 |        1 |          1 |        1 | 1000.00
       2 |        1 |          2 |        2 |   10.00
(2 rows)
```

```sql
SELECT product_id, product_name, stock FROM inventory;
```

```
 product_id | product_name | stock
------------+--------------+-------
          1 | Laptop       |    49
          2 | Mouse        |   198
          3 | Keyboard     |   150
(3 rows)
```

All three tables were updated together. If any step had failed, everything would have been rolled back — no orphaned orders, no incorrect inventory.

---

## Auto-Commit Mode

By default, PostgreSQL runs in auto-commit mode. Every single statement is its own transaction:

```sql
-- These are actually two separate transactions:
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- ^ automatically committed

UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
-- ^ automatically committed
```

If the second statement fails, the first one has already been committed. That is why you need explicit BEGIN/COMMIT when multiple statements must succeed together.

```
Auto-commit (default):           Explicit transaction:
+--------+    +--------+        +----------------------------+
| UPDATE | -> | UPDATE |        | BEGIN                      |
| (auto  |    | (auto  |        |   UPDATE accounts ...      |
| commit)|    | commit)|        |   UPDATE accounts ...      |
+--------+    +--------+        | COMMIT                     |
                                +----------------------------+
If #2 fails,    #1 is           If anything fails,
#1 already      already         everything is
committed       gone            rolled back
```

---

## Common Mistakes

### Mistake 1: Forgetting BEGIN

```sql
-- BAD: These are two separate auto-committed transactions
UPDATE accounts SET balance = balance - 500 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 500 WHERE account_id = 2;

-- GOOD: Wrapped in a transaction
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 500 WHERE account_id = 2;
COMMIT;
```

### Mistake 2: Long-Running Transactions

```sql
-- BAD: Transaction holds locks while waiting for user input
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- ... wait for user confirmation for 5 minutes ...
COMMIT;

-- GOOD: Keep transactions short
-- Validate and prepare data first, then:
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;
```

### Mistake 3: Not Handling Errors

```sql
-- BAD: If the second UPDATE fails, the first is already done
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 500 WHERE account_id = 999;
-- account_id 999 does not exist — but no error raised!
COMMIT;

-- GOOD: Check that updates actually affected rows
BEGIN;

DO $$
DECLARE
    rows_affected INT;
BEGIN
    UPDATE accounts SET balance = balance - 500 WHERE account_id = 1;
    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    IF rows_affected = 0 THEN
        RAISE EXCEPTION 'Source account not found';
    END IF;

    UPDATE accounts SET balance = balance + 500 WHERE account_id = 2;
    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    IF rows_affected = 0 THEN
        RAISE EXCEPTION 'Destination account not found';
    END IF;
END $$;

COMMIT;
```

### Mistake 4: Catching Exceptions and Continuing

```sql
-- BAD: Swallowing errors inside a transaction
BEGIN;
-- After an error in PostgreSQL, the transaction is "aborted"
-- You cannot run more statements — you must ROLLBACK
-- Trying to continue will give:
-- ERROR: current transaction is aborted, commands ignored until
--        end of transaction block
```

---

## Best Practices

1. **Keep transactions as short as possible.** Do validation and calculations before BEGIN. Only put the actual data modifications inside the transaction.

2. **Always use transactions for multi-table operations.** Any time you modify more than one table, wrap it in a transaction.

3. **Lock rows in a consistent order.** If transaction A locks accounts in the order (1, 2, 3), then transaction B should also lock them in the order (1, 2, 3), not (3, 2, 1). This prevents deadlocks.

4. **Use SELECT ... FOR UPDATE when you read data that you plan to modify.** This prevents other transactions from changing the data between your read and your write.

5. **Handle errors properly.** Check row counts, use exception handling, and always have a plan for what happens when things go wrong.

6. **Use the right isolation level.** READ COMMITTED is fine for most operations. Use SERIALIZABLE for critical financial operations where correctness matters more than performance.

7. **Monitor for deadlocks.** Check PostgreSQL logs regularly. Deadlocks are a sign that your transactions need redesigning.

---

## Quick Summary

```
+------------------+----------------------------------------------+
| Concept          | What It Does                                 |
+------------------+----------------------------------------------+
| BEGIN            | Starts a transaction                         |
| COMMIT           | Makes all changes permanent                  |
| ROLLBACK         | Undoes all changes since BEGIN                |
| SAVEPOINT        | Creates a checkpoint for partial rollback     |
| ROLLBACK TO      | Undoes changes back to a savepoint            |
| RELEASE SAVEPOINT| Removes a savepoint (frees resources)        |
| READ COMMITTED   | Default — sees only committed data           |
| REPEATABLE READ  | Same data throughout the transaction          |
| SERIALIZABLE     | Strictest — transactions run "one at a time" |
| FOR UPDATE       | Locks rows you plan to modify                |
+------------------+----------------------------------------------+
```

---

## Key Points

- A transaction groups multiple SQL statements into a single all-or-nothing unit.
- ACID properties (Atomicity, Consistency, Isolation, Durability) guarantee data integrity.
- BEGIN starts a transaction. COMMIT saves changes. ROLLBACK undoes everything.
- SAVEPOINTs let you undo part of a transaction without losing all of it.
- READ COMMITTED is the default isolation level in PostgreSQL and is suitable for most operations.
- SERIALIZABLE provides the strongest guarantees but may cause transactions to fail and retry.
- Deadlocks happen when two transactions wait for each other. Prevent them by locking rows in a consistent order.
- Keep transactions short to minimize lock contention.
- Always use transactions when modifying multiple related tables.

---

## Practice Questions

1. What happens if you run an UPDATE statement without BEGIN? Does it still use a transaction?

2. You have a transaction with three INSERT statements. The second INSERT violates a UNIQUE constraint. What happens to the first and third INSERTs?

3. What is the difference between ROLLBACK and ROLLBACK TO SAVEPOINT? When would you use each?

4. Two transactions are running at READ COMMITTED isolation level. Transaction A reads a row, then Transaction B updates and commits that row, then Transaction A reads the same row again. Will Transaction A see the change?

5. Why is it important to lock rows in a consistent order across all transactions?

---

## Exercises

### Exercise 1: Safe Transfer Function

Write a transaction that transfers money between two accounts. The transaction should:
- Check that both accounts exist
- Verify the sender has sufficient funds
- Perform the transfer
- Roll back if anything goes wrong

**Hint**: Use a DO block with exception handling and GET DIAGNOSTICS to check row counts.

### Exercise 2: Order with Rollback

Write a transaction that:
1. Creates a new order
2. Adds three items to the order
3. Uses a SAVEPOINT after the second item
4. Attempts to add a third item that fails (simulate with a bad product_id)
5. Rolls back to the savepoint
6. Adds a valid third item instead
7. Commits the transaction

### Exercise 3: Concurrent Simulation

Open two psql sessions. In each session, start a transaction and try to update the same row. Observe what happens:
- What does the second session see while the first transaction is still open?
- What happens when the first session commits?
- Try the same experiment with REPEATABLE READ isolation level.

---

## What Is Next?

Now that you understand how to keep your data safe with transactions, you are ready to learn about window functions in Chapter 26. Window functions let you perform calculations across groups of rows without collapsing them — like running totals, rankings, and comparisons to previous rows. They are one of SQL's most powerful features for data analysis.
