# Chapter 29: Triggers — Automatic Actions When Data Changes

## What You Will Learn

In this chapter, you will learn:

- What triggers are and when to use them
- The difference between BEFORE and AFTER triggers
- How triggers respond to INSERT, UPDATE, and DELETE
- How to write trigger functions
- How to use the NEW and OLD records
- The difference between FOR EACH ROW and FOR EACH STATEMENT
- How to build practical triggers for audit logging, timestamps, validation, and deletion prevention

## Why This Chapter Matters

Imagine a security camera system in a building. You do not have to remember to press "record" every time someone walks through the door. The camera detects motion and automatically starts recording. It captures who entered, when they entered, and through which door.

Triggers work the same way in a database. They are automatic actions that fire whenever data changes. When someone inserts a new row, updates an existing row, or deletes a row, a trigger can automatically log the change, update a timestamp, validate the data, or even prevent the operation entirely.

Without triggers, you would have to remember to add audit logging in every piece of application code that modifies data. Miss one spot, and you have a gap in your audit trail. With triggers, the database handles it automatically — no matter where the change comes from.

---

## Setting Up Our Practice Tables

```sql
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    department  VARCHAR(50) NOT NULL,
    salary      DECIMAL(10, 2) NOT NULL,
    email       VARCHAR(150),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

INSERT INTO employees (name, department, salary, email) VALUES
('Alice Johnson',  'Engineering', 95000, 'alice@company.com'),
('Bob Smith',      'Sales',       75000, 'bob@company.com'),
('Charlie Brown',  'Marketing',   70000, 'charlie@company.com');

CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price        DECIMAL(10, 2) NOT NULL,
    min_price    DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW()
);

INSERT INTO products (product_name, price, min_price) VALUES
('Laptop',     999.99, 799.99),
('Mouse',       29.99,  19.99),
('Keyboard',    79.99,  59.99);

CREATE TABLE audit_log (
    log_id      SERIAL PRIMARY KEY,
    table_name  VARCHAR(50) NOT NULL,
    action      VARCHAR(10) NOT NULL,
    record_id   INT,
    old_values  JSONB,
    new_values  JSONB,
    changed_by  VARCHAR(100) DEFAULT CURRENT_USER,
    changed_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE important_records (
    record_id  SERIAL PRIMARY KEY,
    title      VARCHAR(100) NOT NULL,
    content    TEXT,
    is_locked  BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO important_records (title, content, is_locked) VALUES
('Company Policy', 'No changes allowed to this document', TRUE),
('Draft Memo', 'Work in progress', FALSE),
('Annual Report', 'Final version - locked', TRUE);
```

---

## What Is a Trigger?

A trigger is a function that runs automatically when a specific event (INSERT, UPDATE, or DELETE) happens on a table. You do not call it — the database calls it for you.

```
Application
    |
    | INSERT INTO employees ...
    v
+------------------+
|  employees table |
+------------------+
    |
    | (trigger fires automatically)
    v
+------------------+
| Trigger Function |
|  - Log change    |
|  - Validate data |
|  - Update fields |
+------------------+
```

### Two Parts of a Trigger

A trigger has two components:

1. **Trigger function** — the code that runs (what to do)
2. **Trigger definition** — when and where to run it (when to do it)

```
Step 1: Create the function       Step 2: Attach it to a table
+---------------------------+     +---------------------------+
| CREATE FUNCTION            |     | CREATE TRIGGER            |
|   my_trigger_func()       |     |   BEFORE INSERT           |
| RETURNS TRIGGER            |     |   ON employees            |
| ...                        |     |   FOR EACH ROW            |
+---------------------------+     |   EXECUTE FUNCTION        |
                                  |   my_trigger_func();       |
                                  +---------------------------+
```

---

## BEFORE vs AFTER Triggers

```
+--------+----------------------------------------------------+
| Timing | What It Means                                      |
+--------+----------------------------------------------------+
| BEFORE | Runs before the data change is applied             |
|        | Can modify the incoming data (NEW record)          |
|        | Can cancel the operation (return NULL)              |
+--------+----------------------------------------------------+
| AFTER  | Runs after the data change is applied              |
|        | Cannot modify the data (it is already saved)       |
|        | Good for logging, notifications, cascade updates   |
+--------+----------------------------------------------------+
```

```
Timeline of an INSERT:

  BEFORE trigger       INSERT happens       AFTER trigger
       |                    |                     |
       v                    v                     v
  +---------+         +-----------+         +---------+
  | Validate|         | Row saved |         | Log the |
  | or      |  --->   | to table  |  --->   | change  |
  | modify  |         |           |         |         |
  +---------+         +-----------+         +---------+

  Can change             Data is              Data is
  or cancel              committed            committed
  the data               to table             (read only)
```

---

## NEW and OLD Records

Inside a trigger function, you have access to special variables that represent the data:

```
+-----------+--------+--------+--------+
| Operation | NEW    | OLD    | Notes  |
+-----------+--------+--------+--------+
| INSERT    | Yes    | No     | NEW = the row being inserted       |
| UPDATE    | Yes    | Yes    | OLD = before, NEW = after          |
| DELETE    | No     | Yes    | OLD = the row being deleted        |
+-----------+--------+--------+--------+
```

- **NEW** — the new version of the row (available in INSERT and UPDATE)
- **OLD** — the old version of the row (available in UPDATE and DELETE)

---

## Practical 1: Automatic updated_at Timestamp

One of the most common triggers. Every time a row is updated, automatically set the `updated_at` column to the current time.

### Step 1: Create the Trigger Function

```sql
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;
```

**Line-by-line explanation:**
- `RETURNS TRIGGER` — this function is specifically for use as a trigger
- `NEW.updated_at := NOW()` — modify the `updated_at` field of the incoming row
- `RETURN NEW` — return the modified row (required for BEFORE triggers)

### Step 2: Create the Trigger

```sql
CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
```

**Line-by-line explanation:**
- `CREATE TRIGGER trg_employees_updated_at` — name the trigger (prefix with `trg_`)
- `BEFORE UPDATE` — fire before an UPDATE is applied
- `ON employees` — attach to the employees table
- `FOR EACH ROW` — fire once for each row being updated
- `EXECUTE FUNCTION set_updated_at()` — call this function

### Testing It

```sql
-- Check current timestamps
SELECT name, updated_at FROM employees WHERE employee_id = 1;
```

```
     name      |         updated_at
---------------+----------------------------
 Alice Johnson | 2024-01-15 10:00:00.000000
(1 row)
```

```sql
-- Update Alice's salary
UPDATE employees SET salary = 100000 WHERE employee_id = 1;

-- Check again — updated_at changed automatically!
SELECT name, salary, updated_at FROM employees WHERE employee_id = 1;
```

```
     name      |  salary   |         updated_at
---------------+-----------+----------------------------
 Alice Johnson | 100000.00 | 2024-01-15 14:35:22.123456
(1 row)
```

The `updated_at` timestamp was automatically set to the current time, even though our UPDATE statement only changed the salary.

### Reusing the Same Function on Multiple Tables

```sql
-- Same function works for any table with an updated_at column
CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
```

---

## Practical 2: Audit Logging Trigger

Let us create a comprehensive audit log that records every change to the employees table:

### The Trigger Function

```sql
CREATE OR REPLACE FUNCTION audit_employee_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, action, record_id, new_values)
        VALUES (
            TG_TABLE_NAME,
            'INSERT',
            NEW.employee_id,
            jsonb_build_object(
                'name', NEW.name,
                'department', NEW.department,
                'salary', NEW.salary,
                'email', NEW.email
            )
        );
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, action, record_id,
                               old_values, new_values)
        VALUES (
            TG_TABLE_NAME,
            'UPDATE',
            NEW.employee_id,
            jsonb_build_object(
                'name', OLD.name,
                'department', OLD.department,
                'salary', OLD.salary,
                'email', OLD.email
            ),
            jsonb_build_object(
                'name', NEW.name,
                'department', NEW.department,
                'salary', NEW.salary,
                'email', NEW.email
            )
        );
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, action, record_id, old_values)
        VALUES (
            TG_TABLE_NAME,
            'DELETE',
            OLD.employee_id,
            jsonb_build_object(
                'name', OLD.name,
                'department', OLD.department,
                'salary', OLD.salary,
                'email', OLD.email
            )
        );
        RETURN OLD;
    END IF;
END;
$$;
```

**Key variables explained:**
- `TG_OP` — the operation that fired the trigger ('INSERT', 'UPDATE', or 'DELETE')
- `TG_TABLE_NAME` — the name of the table the trigger is attached to
- `jsonb_build_object(...)` — creates a JSON object from key-value pairs

### Attach the Trigger

```sql
CREATE TRIGGER trg_audit_employees
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION audit_employee_changes();
```

Notice: `AFTER INSERT OR UPDATE OR DELETE` — this single trigger fires on all three operations.

### Testing the Audit Log

```sql
-- Insert a new employee
INSERT INTO employees (name, department, salary, email)
VALUES ('Diana Prince', 'Engineering', 110000, 'diana@company.com');

-- Update an employee
UPDATE employees SET salary = 80000 WHERE employee_id = 2;

-- Delete an employee
DELETE FROM employees WHERE employee_id = 3;

-- Check the audit log
SELECT
    log_id,
    action,
    record_id,
    old_values,
    new_values,
    changed_at::DATE
FROM audit_log
ORDER BY log_id;
```

```
 log_id | action | record_id |              old_values              |              new_values              | changed_at
--------+--------+-----------+--------------------------------------+--------------------------------------+------------
      1 | INSERT |         4 |                                      | {"name": "Diana Prince", ...}        | 2024-01-15
      2 | UPDATE |         2 | {"name": "Bob Smith", "salary": ...} | {"name": "Bob Smith", "salary": ...} | 2024-01-15
      3 | DELETE |         3 | {"name": "Charlie Brown", ...}       |                                      | 2024-01-15
(3 rows)
```

Every change is automatically recorded with the old and new values, who made the change, and when.

---

## Practical 3: Data Validation Trigger

A trigger that enforces business rules that cannot be expressed with simple CHECK constraints:

```sql
CREATE OR REPLACE FUNCTION validate_product_price()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Rule 1: Price cannot be negative
    IF NEW.price < 0 THEN
        RAISE EXCEPTION 'Price cannot be negative. Got: %', NEW.price;
    END IF;

    -- Rule 2: Price cannot be below minimum price
    IF NEW.price < NEW.min_price THEN
        RAISE EXCEPTION 'Price (%) cannot be below minimum price (%)',
                         NEW.price, NEW.min_price;
    END IF;

    -- Rule 3: Price increases cannot exceed 50% at once
    IF TG_OP = 'UPDATE' AND OLD.price > 0 THEN
        IF NEW.price > OLD.price * 1.5 THEN
            RAISE EXCEPTION
                'Price increase too large. Old: %, New: %, Max allowed: %',
                OLD.price, NEW.price, OLD.price * 1.5;
        END IF;
    END IF;

    -- Rule 4: Normalize product name to title case
    NEW.product_name := INITCAP(TRIM(NEW.product_name));

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_product
    BEFORE INSERT OR UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION validate_product_price();
```

### Testing Validation

```sql
-- Try to set a negative price
UPDATE products SET price = -10 WHERE product_id = 1;
```

```
ERROR:  Price cannot be negative. Got: -10
```

```sql
-- Try to set price below minimum
UPDATE products SET price = 500 WHERE product_id = 1;
```

```
ERROR:  Price (500) cannot be below minimum price (799.99)
```

Wait — that is not right. The min_price for the Laptop is 799.99, so 500 is indeed below minimum. The trigger caught it.

```sql
-- Try an excessive price increase (Laptop is currently 999.99)
UPDATE products SET price = 1800 WHERE product_id = 1;
```

```
ERROR:  Price increase too large. Old: 999.99, New: 1800, Max allowed: 1499.985
```

```sql
-- Valid price update
UPDATE products SET price = 1099.99 WHERE product_id = 1;

SELECT product_name, price FROM products WHERE product_id = 1;
```

```
 product_name |  price
--------------+---------
 Laptop       | 1099.99
(1 row)
```

```sql
-- Test name normalization
INSERT INTO products (product_name, price, min_price)
VALUES ('  WIRELESS   headphones  ', 149.99, 99.99);

SELECT product_name, price FROM products WHERE product_id = 4;
```

```
    product_name     |  price
---------------------+---------
 Wireless Headphones | 149.99
(1 row)
```

The trigger automatically cleaned up the product name.

---

## Practical 4: Preventing Deletion

Sometimes you want to prevent certain rows from being deleted:

```sql
CREATE OR REPLACE FUNCTION prevent_locked_deletion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.is_locked THEN
        RAISE EXCEPTION
            'Cannot delete locked record: "%" (ID: %). Unlock it first.',
            OLD.title, OLD.record_id;
    END IF;

    RETURN OLD;
END;
$$;

CREATE TRIGGER trg_prevent_delete_locked
    BEFORE DELETE ON important_records
    FOR EACH ROW
    EXECUTE FUNCTION prevent_locked_deletion();
```

### Testing Deletion Prevention

```sql
-- Try to delete a locked record
DELETE FROM important_records WHERE record_id = 1;
```

```
ERROR:  Cannot delete locked record: "Company Policy" (ID: 1). Unlock it first.
```

```sql
-- Delete an unlocked record — works fine
DELETE FROM important_records WHERE record_id = 2;
```

```
DELETE 1
```

```sql
-- Unlock, then delete
UPDATE important_records SET is_locked = FALSE WHERE record_id = 1;
DELETE FROM important_records WHERE record_id = 1;
```

```
DELETE 1
```

---

## FOR EACH ROW vs FOR EACH STATEMENT

```
+-------------------+----------------------------------------------+
| Type              | When It Fires                                |
+-------------------+----------------------------------------------+
| FOR EACH ROW      | Once for every row affected                  |
|                   | Has access to NEW and OLD                    |
|                   | Most common choice                           |
+-------------------+----------------------------------------------+
| FOR EACH STATEMENT| Once for the entire statement                |
|                   | Even if zero rows are affected               |
|                   | No access to NEW and OLD                     |
|                   | Good for logging that an operation happened  |
+-------------------+----------------------------------------------+
```

### Example

```sql
-- UPDATE employees SET salary = salary + 1000;
-- If this affects 5 rows:

-- FOR EACH ROW trigger fires:    5 times (once per row)
-- FOR EACH STATEMENT trigger:    1 time  (once total)
```

### Statement-Level Trigger Example

```sql
CREATE OR REPLACE FUNCTION log_bulk_operation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit_log (table_name, action, record_id, new_values)
    VALUES (
        TG_TABLE_NAME,
        TG_OP || '_STATEMENT',
        NULL,
        jsonb_build_object('note', 'Bulk operation performed')
    );
    RETURN NULL;  -- Return value is ignored for AFTER triggers
END;
$$;

CREATE TRIGGER trg_log_bulk_employees
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH STATEMENT
    EXECUTE FUNCTION log_bulk_operation();
```

---

## Conditional Triggers with WHEN

You can add a condition to a trigger so it only fires when certain criteria are met:

```sql
-- Only fire when salary actually changes
CREATE TRIGGER trg_salary_change_audit
    AFTER UPDATE ON employees
    FOR EACH ROW
    WHEN (OLD.salary IS DISTINCT FROM NEW.salary)
    EXECUTE FUNCTION audit_employee_changes();
```

This trigger will not fire if you update the employee's name or department — only when the salary changes.

### Column-Specific Triggers

You can also limit triggers to specific columns:

```sql
-- Only fire when salary or department columns are updated
CREATE TRIGGER trg_compensation_change
    BEFORE UPDATE OF salary, department ON employees
    FOR EACH ROW
    EXECUTE FUNCTION audit_employee_changes();
```

---

## Trigger Execution Order

When multiple triggers exist on the same table and event:

```
1. BEFORE statement triggers
2. BEFORE row triggers (for each affected row)
3. The actual data modification
4. AFTER row triggers (for each affected row)
5. AFTER statement triggers

Within the same timing/level, triggers fire in alphabetical order by name.
```

---

## Managing Triggers

### Viewing Triggers

```sql
SELECT
    trigger_name,
    event_manipulation AS event,
    action_timing AS timing,
    action_orientation AS level
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;
```

```
        trigger_name         |  event | timing | level
-----------------------------+--------+--------+-----------
 trg_audit_employees         | INSERT | AFTER  | ROW
 trg_audit_employees         | UPDATE | AFTER  | ROW
 trg_audit_employees         | DELETE | AFTER  | ROW
 trg_employees_updated_at    | UPDATE | BEFORE | ROW
 trg_prevent_delete_locked   | DELETE | BEFORE | ROW
 trg_validate_product        | INSERT | BEFORE | ROW
 trg_validate_product        | UPDATE | BEFORE | ROW
(7 rows)
```

### Disabling and Enabling Triggers

```sql
-- Disable a specific trigger
ALTER TABLE employees DISABLE TRIGGER trg_audit_employees;

-- Re-enable it
ALTER TABLE employees ENABLE TRIGGER trg_audit_employees;

-- Disable ALL triggers on a table (useful for bulk data loads)
ALTER TABLE employees DISABLE TRIGGER ALL;

-- Re-enable ALL triggers
ALTER TABLE employees ENABLE TRIGGER ALL;
```

### Dropping Triggers

```sql
-- Drop a trigger
DROP TRIGGER trg_audit_employees ON employees;

-- Drop if exists
DROP TRIGGER IF EXISTS trg_audit_employees ON employees;
```

Note: Dropping a trigger does not drop the trigger function. You must drop the function separately if you no longer need it.

---

## A Complete Trigger Workflow

Here is a typical workflow showing BEFORE and AFTER triggers working together on an employee insert:

```
INSERT INTO employees (name, department, salary, email)
VALUES ('New Person', 'engineering', 85000, 'NEW@COMPANY.COM');

    |
    v
BEFORE INSERT trigger (set_updated_at):
    - Sets updated_at to NOW()
    |
    v
BEFORE INSERT trigger (validate_and_normalize):
    - Could normalize department to 'Engineering'
    - Could lowercase the email
    - Returns the modified NEW record
    |
    v
Actual INSERT happens (with modified data)
    |
    v
AFTER INSERT trigger (audit_employee_changes):
    - Records the insert in audit_log
    - NEW record has the final, saved values
    |
    v
Done! One INSERT triggered three automatic actions.
```

---

## Common Mistakes

### Mistake 1: Forgetting RETURN NEW in BEFORE Triggers

```sql
-- BAD: Forgetting to return NEW cancels the operation!
CREATE OR REPLACE FUNCTION bad_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    -- Forgot RETURN NEW!
    -- This returns NULL, which cancels the INSERT/UPDATE
END;
$$;

-- GOOD: Always return NEW for BEFORE INSERT/UPDATE triggers
CREATE OR REPLACE FUNCTION good_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;  -- Required!
END;
$$;
```

### Mistake 2: Infinite Trigger Loops

```sql
-- BAD: Trigger on employees that updates employees
-- causes the trigger to fire again, which updates again...
CREATE OR REPLACE FUNCTION infinite_loop_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE employees SET updated_at = NOW()
    WHERE employee_id = NEW.employee_id;
    -- This UPDATE fires this trigger again!
    RETURN NEW;
END;
$$;

-- GOOD: Modify NEW directly instead of running another UPDATE
CREATE OR REPLACE FUNCTION no_loop_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();  -- Modifies the row being inserted/updated
    RETURN NEW;               -- No additional UPDATE needed
END;
$$;
```

### Mistake 3: Heavy Logic in Triggers

```sql
-- BAD: Sending emails, calling external APIs, or doing
-- heavy computation in triggers makes every INSERT/UPDATE slow

-- GOOD: Keep triggers lightweight. Use triggers for:
--   - Setting timestamps
--   - Simple validation
--   - Writing to audit tables
-- Use application code or background jobs for heavy work.
```

### Mistake 4: Not Handling All Operations

```sql
-- BAD: Trigger function only handles INSERT but is attached to
-- INSERT OR UPDATE OR DELETE
-- The function crashes on UPDATE/DELETE because it tries to
-- access NEW on a DELETE (which has no NEW)

-- GOOD: Use IF TG_OP = ... to handle each operation correctly
```

---

## Best Practices

1. **Name triggers consistently.** Use a prefix like `trg_` followed by the table name and purpose: `trg_employees_updated_at`, `trg_orders_audit`.

2. **Keep triggers simple and fast.** Triggers run synchronously — they block the original operation until they finish. Complex or slow triggers make every INSERT/UPDATE/DELETE slow.

3. **Use BEFORE triggers for data modification.** If you need to change the incoming data (normalize, validate, set defaults), use BEFORE.

4. **Use AFTER triggers for side effects.** If you need to log changes, update related tables, or send notifications, use AFTER.

5. **Return NEW from BEFORE INSERT/UPDATE triggers.** Returning NULL cancels the operation. Return OLD from BEFORE DELETE triggers.

6. **Avoid modifying the same table in an AFTER trigger.** This can cause infinite loops. If you need to modify the row, use a BEFORE trigger and change the NEW record directly.

7. **Document your triggers.** Triggers are invisible in application code. Other developers may not know they exist. Keep a clear record of what triggers are on each table.

8. **Use WHEN clauses to limit trigger execution.** Only fire when relevant columns change: `WHEN (OLD.salary IS DISTINCT FROM NEW.salary)`.

---

## Quick Summary

```
+-------------------------+----------------------------------------------+
| Concept                 | What It Does                                 |
+-------------------------+----------------------------------------------+
| BEFORE trigger          | Fires before data change, can modify data    |
| AFTER trigger           | Fires after data change, for side effects    |
| INSERT trigger          | Fires when a new row is added                |
| UPDATE trigger          | Fires when an existing row is changed        |
| DELETE trigger          | Fires when a row is removed                  |
| NEW                     | The new version of the row                   |
| OLD                     | The old version of the row                   |
| TG_OP                   | The operation: INSERT, UPDATE, or DELETE      |
| TG_TABLE_NAME           | Name of the table that fired the trigger     |
| FOR EACH ROW            | Fire once per affected row                   |
| FOR EACH STATEMENT      | Fire once per SQL statement                  |
| RETURN NEW              | Allow the operation (BEFORE INSERT/UPDATE)   |
| RETURN NULL             | Cancel the operation (BEFORE trigger)        |
| WHEN clause             | Conditional trigger execution                |
| DISABLE TRIGGER         | Temporarily turn off a trigger               |
+-------------------------+----------------------------------------------+
```

---

## Key Points

- Triggers are automatic functions that fire when data is inserted, updated, or deleted.
- A trigger consists of a trigger function (RETURNS TRIGGER) and a trigger definition (CREATE TRIGGER).
- BEFORE triggers can modify or cancel the operation. AFTER triggers cannot modify data but are good for logging.
- NEW holds the new row data (INSERT/UPDATE). OLD holds the old row data (UPDATE/DELETE).
- FOR EACH ROW triggers fire once per affected row. FOR EACH STATEMENT triggers fire once per statement.
- Always RETURN NEW from BEFORE INSERT/UPDATE triggers. Returning NULL cancels the operation.
- TG_OP and TG_TABLE_NAME are special variables that tell the trigger function what happened and where.
- Keep triggers lightweight — they run synchronously and slow down the original operation.
- Avoid infinite loops by modifying NEW directly in BEFORE triggers instead of running additional UPDATE statements.

---

## Practice Questions

1. What is the difference between a BEFORE trigger and an AFTER trigger? When would you choose each?

2. In a trigger function, what are the NEW and OLD records? Which operations have access to each?

3. What happens if a BEFORE INSERT trigger returns NULL instead of returning NEW?

4. Why is it dangerous to have a trigger on the `employees` table that runs `UPDATE employees ...`? How do you avoid this problem?

5. What is the difference between FOR EACH ROW and FOR EACH STATEMENT? Which one has access to NEW and OLD?

---

## Exercises

### Exercise 1: Email Normalization Trigger

Create a BEFORE INSERT OR UPDATE trigger on the employees table that:
- Converts the email to lowercase
- Trims whitespace from the email
- Validates that the email contains an @ symbol (raise an exception if it does not)

Test with: `INSERT INTO employees (name, department, salary, email) VALUES ('Test', 'IT', 60000, '  TEST@Company.COM  ');`

### Exercise 2: Comprehensive Audit Trigger

Create a generic audit trigger function that works on any table. It should:
- Log the table name, operation, timestamp, and user
- For UPDATEs, only log columns that actually changed
- Store old and new values as JSONB

Attach it to both the employees and products tables.

**Hint**: Use `TG_TABLE_NAME` for the table name. For detecting changes, compare `OLD.column IS DISTINCT FROM NEW.column`.

### Exercise 3: Salary Change Guardian

Create a trigger that:
- Prevents salary decreases of more than 10% in a single update
- Prevents salary increases of more than 25% in a single update
- Logs all salary changes (old salary, new salary, percentage change) to the audit_log table
- Allows unrestricted changes for employees in the "Executive" department

**Hint**: Calculate the percentage change with `(NEW.salary - OLD.salary) / OLD.salary * 100`.

---

## What Is Next?

In Chapter 30, you will learn about performance tuning — how to make your queries run faster. You will learn to read query plans with EXPLAIN ANALYZE, choose the right indexes, rewrite slow queries, and use tools like VACUUM and ANALYZE to keep your database running smoothly. Performance tuning is where everything you have learned comes together.
