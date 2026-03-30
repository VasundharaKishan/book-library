# Chapter 28: Stored Procedures and Functions

## What You Will Learn

In this chapter, you will learn:

- What stored procedures and functions are
- How to create functions in PostgreSQL using PL/pgSQL
- How to use parameters (IN, OUT, INOUT)
- How to declare and use variables
- How to write IF/ELSE conditional logic
- How to use loops (FOR, WHILE)
- How to debug with RAISE NOTICE
- How to call functions and handle errors
- How to build practical functions for business logic

## Why This Chapter Matters

Imagine you run a restaurant. Every time a customer orders, the waiter has to remember a long sequence of steps: check if the dish is available, calculate the price with any discounts, update inventory, print the receipt. If you hire a new waiter, they have to learn all these steps from scratch.

Now imagine you create a recipe book that lives in the kitchen. Any waiter can follow it, and the steps are always done the same way. That is what a stored procedure is — a saved program that lives in the database. Instead of writing the same complex SQL over and over in your application code, you write it once as a function in the database.

Stored functions are essential for:
- Encapsulating business logic (like discount calculations)
- Ensuring consistency (everyone uses the same logic)
- Reducing network traffic (one function call instead of many queries)
- Security (grant access to the function, not the underlying tables)

---

## Setting Up Our Practice Tables

```sql
CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price        DECIMAL(10, 2) NOT NULL,
    stock        INT NOT NULL DEFAULT 0
);

INSERT INTO products (product_name, price, stock) VALUES
('Laptop',   999.99, 50),
('Mouse',     29.99, 200),
('Keyboard',  79.99, 150),
('Monitor',  349.99, 75),
('Headphones', 149.99, 100);

CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    owner_name VARCHAR(100) NOT NULL,
    balance    DECIMAL(12, 2) NOT NULL DEFAULT 0.00
);

INSERT INTO accounts (owner_name, balance) VALUES
('Alice', 5000.00),
('Bob',   3000.00),
('Charlie', 1500.00);

CREATE TABLE audit_log (
    log_id     SERIAL PRIMARY KEY,
    action     VARCHAR(50) NOT NULL,
    details    TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## What Is a Stored Function?

A stored function is a block of code that is saved in the database. You create it once, and then you can call it by name whenever you need it.

```
Without functions:                  With functions:
+---------------------------+       +---------------------------+
| Application Code          |       | Application Code          |
|                           |       |                           |
| query1 = "SELECT ..."    |       | CALL calculate_discount() |
| query2 = "UPDATE ..."    |       |                           |
| query3 = "INSERT ..."    |       | (one call does it all)    |
| query4 = "UPDATE ..."    |       +---------------------------+
| (repeat everywhere)      |
+---------------------------+       +---------------------------+
                                    | Database                  |
                                    | calculate_discount():     |
                                    |   SELECT ...              |
                                    |   UPDATE ...              |
                                    |   INSERT ...              |
                                    |   UPDATE ...              |
                                    +---------------------------+
```

### PostgreSQL Note

In PostgreSQL, everything is a function (created with CREATE FUNCTION). PostgreSQL 11 added CREATE PROCEDURE for operations that do not return values, but functions are far more common and flexible. We will focus on CREATE FUNCTION in this chapter.

---

## Your First Function

Let us create a simple function that calculates a discounted price:

```sql
CREATE OR REPLACE FUNCTION calculate_discount(
    original_price DECIMAL,
    discount_pct   DECIMAL
)
RETURNS DECIMAL
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN original_price * (1 - discount_pct / 100);
END;
$$;
```

**Line-by-line explanation:**
- `CREATE OR REPLACE FUNCTION` — creates the function (or updates it if it already exists)
- `calculate_discount` — the function name
- `original_price DECIMAL, discount_pct DECIMAL` — two input parameters
- `RETURNS DECIMAL` — the function returns a decimal number
- `LANGUAGE plpgsql` — we are using PL/pgSQL (PostgreSQL's procedural language)
- `AS $$ ... $$` — the dollar-quoted string contains the function body
- `BEGIN ... END` — the code block
- `RETURN` — sends the result back to the caller

### Calling the Function

```sql
SELECT calculate_discount(100.00, 15);
```

```
 calculate_discount
--------------------
              85.00
(1 row)
```

### Using It in Queries

```sql
SELECT
    product_name,
    price AS original_price,
    calculate_discount(price, 10) AS sale_price
FROM products;
```

```
 product_name | original_price | sale_price
--------------+----------------+-----------
 Laptop       |         999.99 |    899.99
 Mouse        |          29.99 |     26.99
 Keyboard     |          79.99 |     71.99
 Monitor      |         349.99 |    314.99
 Headphones   |         149.99 |    134.99
(5 rows)
```

---

## Parameters: IN, OUT, and INOUT

### IN Parameters (Default)

IN parameters pass values into the function. They are the default:

```sql
CREATE OR REPLACE FUNCTION get_product_info(
    p_product_id INT  -- IN is the default
)
RETURNS TABLE(name VARCHAR, price DECIMAL, stock INT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT product_name, p.price, p.stock
    FROM products p
    WHERE p.product_id = p_product_id;
END;
$$;
```

```sql
SELECT * FROM get_product_info(1);
```

```
  name  |  price  | stock
--------+---------+-------
 Laptop | 999.99  |    50
(1 row)
```

### OUT Parameters

OUT parameters return values from the function. They are an alternative to RETURNS:

```sql
CREATE OR REPLACE FUNCTION get_account_summary(
    IN  p_account_id INT,
    OUT p_owner      VARCHAR,
    OUT p_balance    DECIMAL,
    OUT p_status     VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT owner_name, balance
    INTO p_owner, p_balance
    FROM accounts
    WHERE account_id = p_account_id;

    -- Determine status based on balance
    IF p_balance >= 5000 THEN
        p_status := 'Gold';
    ELSIF p_balance >= 2000 THEN
        p_status := 'Silver';
    ELSE
        p_status := 'Bronze';
    END IF;
END;
$$;
```

```sql
SELECT * FROM get_account_summary(1);
```

```
 p_owner | p_balance | p_status
---------+-----------+----------
 Alice   |   5000.00 | Gold
(1 row)
```

**Line-by-line explanation:**
- `IN p_account_id INT` — input parameter (the account to look up)
- `OUT p_owner VARCHAR` — output parameter (will hold the owner's name)
- `OUT p_balance DECIMAL` — output parameter (will hold the balance)
- `OUT p_status VARCHAR` — output parameter (will hold the calculated status)
- No `RETURNS` clause needed — the OUT parameters define the return type
- `SELECT ... INTO p_owner, p_balance` — fills the OUT parameters from the query
- `p_status := 'Gold'` — the `:=` operator assigns a value

### INOUT Parameters

INOUT parameters pass a value in and can be modified to pass a value back out:

```sql
CREATE OR REPLACE FUNCTION apply_tax(
    INOUT amount DECIMAL,
    IN    tax_rate DECIMAL DEFAULT 8.5
)
LANGUAGE plpgsql
AS $$
BEGIN
    amount := amount * (1 + tax_rate / 100);
END;
$$;
```

```sql
SELECT apply_tax(100.00);
```

```
 apply_tax
-----------
    108.50
(1 row)
```

```sql
SELECT apply_tax(100.00, 10);
```

```
 apply_tax
-----------
    110.00
(1 row)
```

---

## Variables with DECLARE

You can declare local variables inside a function using the DECLARE section:

```sql
CREATE OR REPLACE FUNCTION calculate_order_total(
    p_product_id INT,
    p_quantity   INT
)
RETURNS DECIMAL
LANGUAGE plpgsql
AS $$
DECLARE
    v_price      DECIMAL;
    v_subtotal   DECIMAL;
    v_tax_rate   DECIMAL := 0.085;  -- 8.5% tax
    v_total      DECIMAL;
    v_product    VARCHAR;
BEGIN
    -- Get the product price
    SELECT price, product_name
    INTO v_price, v_product
    FROM products
    WHERE product_id = p_product_id;

    -- Check if product exists
    IF v_price IS NULL THEN
        RAISE EXCEPTION 'Product with ID % not found', p_product_id;
    END IF;

    -- Calculate totals
    v_subtotal := v_price * p_quantity;
    v_total    := v_subtotal * (1 + v_tax_rate);

    RAISE NOTICE 'Product: %, Qty: %, Subtotal: %, Total with tax: %',
                 v_product, p_quantity, v_subtotal, v_total;

    RETURN ROUND(v_total, 2);
END;
$$;
```

```sql
SELECT calculate_order_total(1, 2);
```

```
NOTICE:  Product: Laptop, Qty: 2, Subtotal: 1999.98, Total with tax: 2169.9783
 calculate_order_total
-----------------------
               2169.98
(1 row)
```

**Line-by-line explanation of DECLARE:**
- `DECLARE` — starts the variable declaration section
- `v_price DECIMAL` — declares a variable (no initial value, defaults to NULL)
- `v_tax_rate DECIMAL := 0.085` — declares and initializes a variable
- Variables are local to the function and exist only while it runs
- The `v_` prefix is a naming convention to distinguish variables from column names

---

## IF/ELSE Conditional Logic

PL/pgSQL supports IF, ELSIF, and ELSE for branching:

```sql
CREATE OR REPLACE FUNCTION get_shipping_cost(
    p_order_total DECIMAL,
    p_is_member   BOOLEAN DEFAULT FALSE
)
RETURNS DECIMAL
LANGUAGE plpgsql
AS $$
DECLARE
    v_shipping DECIMAL;
BEGIN
    IF p_is_member THEN
        -- Members get free shipping on orders over $50
        IF p_order_total >= 50 THEN
            v_shipping := 0;
        ELSE
            v_shipping := 4.99;
        END IF;
    ELSE
        -- Non-members
        IF p_order_total >= 100 THEN
            v_shipping := 0;
        ELSIF p_order_total >= 50 THEN
            v_shipping := 7.99;
        ELSIF p_order_total >= 25 THEN
            v_shipping := 9.99;
        ELSE
            v_shipping := 12.99;
        END IF;
    END IF;

    RETURN v_shipping;
END;
$$;
```

```sql
SELECT
    get_shipping_cost(120, FALSE) AS non_member_120,
    get_shipping_cost(75, FALSE)  AS non_member_75,
    get_shipping_cost(30, TRUE)   AS member_30,
    get_shipping_cost(60, TRUE)   AS member_60;
```

```
 non_member_120 | non_member_75 | member_30 | member_60
----------------+---------------+-----------+-----------
           0.00 |          7.99 |      4.99 |      0.00
(1 row)
```

```
Decision Flow:

                   Is Member?
                  /          \
               Yes            No
              /                \
    Total >= 50?           Total >= 100?
    /        \             /          \
  Yes        No          Yes          No
  |           |           |            |
$0.00      $4.99       $0.00     Total >= 50?
                                  /        \
                                Yes        No
                                |           |
                              $7.99    Total >= 25?
                                        /       \
                                      Yes       No
                                       |         |
                                     $9.99    $12.99
```

---

## Loops

### FOR Loop — Iterating Over a Range

```sql
CREATE OR REPLACE FUNCTION generate_multiplication_table(
    p_number INT
)
RETURNS TABLE(expression TEXT, result INT)
LANGUAGE plpgsql
AS $$
BEGIN
    FOR i IN 1..10 LOOP
        expression := p_number || ' x ' || i;
        result := p_number * i;
        RETURN NEXT;  -- Add this row to the result set
    END LOOP;
END;
$$;
```

```sql
SELECT * FROM generate_multiplication_table(7);
```

```
 expression | result
------------+--------
 7 x 1      |      7
 7 x 2      |     14
 7 x 3      |     21
 7 x 4      |     28
 7 x 5      |     35
 7 x 6      |     42
 7 x 7      |     49
 7 x 8      |     56
 7 x 9      |     63
 7 x 10     |     70
(10 rows)
```

**Line-by-line explanation:**
- `FOR i IN 1..10 LOOP` — loop from 1 to 10, with `i` as the loop variable
- `RETURN NEXT` — adds the current row to the output (used with RETURNS TABLE)
- `END LOOP` — marks the end of the loop body

### FOR Loop — Iterating Over Query Results

```sql
CREATE OR REPLACE FUNCTION list_low_stock(
    p_threshold INT DEFAULT 100
)
RETURNS TABLE(name VARCHAR, current_stock INT, needs INT)
LANGUAGE plpgsql
AS $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN
        SELECT product_name, stock
        FROM products
        WHERE stock < p_threshold
        ORDER BY stock
    LOOP
        name := rec.product_name;
        current_stock := rec.stock;
        needs := p_threshold - rec.stock;
        RETURN NEXT;
    END LOOP;
END;
$$;
```

```sql
SELECT * FROM list_low_stock(100);
```

```
   name   | current_stock | needs
----------+---------------+-------
 Laptop   |            50 |    50
 Monitor  |            75 |    25
(2 rows)
```

### WHILE Loop

```sql
CREATE OR REPLACE FUNCTION compound_interest(
    p_principal   DECIMAL,
    p_rate        DECIMAL,    -- Annual rate as percentage
    p_years       INT
)
RETURNS TABLE(year INT, balance DECIMAL)
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance DECIMAL;
    v_year    INT := 0;
BEGIN
    v_balance := p_principal;

    WHILE v_year <= p_years LOOP
        year := v_year;
        balance := ROUND(v_balance, 2);
        RETURN NEXT;

        v_balance := v_balance * (1 + p_rate / 100);
        v_year := v_year + 1;
    END LOOP;
END;
$$;
```

```sql
SELECT * FROM compound_interest(1000, 5, 5);
```

```
 year | balance
------+---------
    0 | 1000.00
    1 | 1050.00
    2 | 1102.50
    3 | 1157.63
    4 | 1215.51
    5 | 1276.28
(6 rows)
```

---

## RAISE NOTICE for Debugging

RAISE NOTICE prints messages to the console. It is your primary debugging tool:

```sql
CREATE OR REPLACE FUNCTION debug_example(p_value INT)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_result INT;
BEGIN
    RAISE NOTICE 'Function called with value: %', p_value;

    v_result := p_value * 2;
    RAISE NOTICE 'After doubling: %', v_result;

    v_result := v_result + 10;
    RAISE NOTICE 'After adding 10: %', v_result;

    RETURN v_result;
END;
$$;
```

```sql
SELECT debug_example(5);
```

```
NOTICE:  Function called with value: 5
NOTICE:  After doubling: 10
NOTICE:  After adding 10: 20
 debug_example
---------------
            20
(1 row)
```

### RAISE Levels

```
+----------+-----------------------------------------------+
| Level    | Purpose                                       |
+----------+-----------------------------------------------+
| DEBUG    | Detailed information for debugging            |
| LOG      | Information logged to server log               |
| NOTICE   | Information sent to the client (most common)  |
| WARNING  | Warning message                               |
| EXCEPTION| Error — aborts the transaction!               |
+----------+-----------------------------------------------+
```

```sql
RAISE NOTICE 'This is informational';
RAISE WARNING 'This might be a problem';
RAISE EXCEPTION 'This stops execution and rolls back!';
```

---

## Error Handling with EXCEPTION

You can catch and handle errors using the EXCEPTION block:

```sql
CREATE OR REPLACE FUNCTION safe_divide(
    p_numerator   DECIMAL,
    p_denominator DECIMAL
)
RETURNS DECIMAL
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN p_numerator / p_denominator;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE 'Division by zero attempted. Returning NULL.';
        RETURN NULL;
    WHEN OTHERS THEN
        RAISE NOTICE 'Unexpected error: %', SQLERRM;
        RETURN NULL;
END;
$$;
```

```sql
SELECT safe_divide(10, 3);
```

```
 safe_divide
--------------
 3.3333333333
(1 row)
```

```sql
SELECT safe_divide(10, 0);
```

```
NOTICE:  Division by zero attempted. Returning NULL.
 safe_divide
-------------

(1 row)
```

**Line-by-line explanation:**
- `EXCEPTION` — starts the error-handling section (like try/catch in other languages)
- `WHEN division_by_zero THEN` — catches a specific error type
- `WHEN OTHERS THEN` — catches any error not handled above
- `SQLERRM` — a built-in variable containing the error message

---

## Practical: Transfer Funds Function

Let us build a complete, production-ready fund transfer function:

```sql
CREATE OR REPLACE FUNCTION transfer_funds(
    p_from_account INT,
    p_to_account   INT,
    p_amount       DECIMAL
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_from_balance DECIMAL;
    v_from_owner   VARCHAR;
    v_to_owner     VARCHAR;
    v_rows         INT;
BEGIN
    -- Validate amount
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Transfer amount must be positive. Got: %', p_amount;
    END IF;

    IF p_from_account = p_to_account THEN
        RAISE EXCEPTION 'Cannot transfer to the same account';
    END IF;

    -- Lock both accounts in consistent order to prevent deadlocks
    SELECT owner_name, balance
    INTO v_from_owner, v_from_balance
    FROM accounts
    WHERE account_id = p_from_account
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Source account % not found', p_from_account;
    END IF;

    SELECT owner_name
    INTO v_to_owner
    FROM accounts
    WHERE account_id = p_to_account
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Destination account % not found', p_to_account;
    END IF;

    -- Check sufficient funds
    IF v_from_balance < p_amount THEN
        RAISE EXCEPTION 'Insufficient funds. Account % has %, needs %',
                         p_from_account, v_from_balance, p_amount;
    END IF;

    -- Perform the transfer
    UPDATE accounts
    SET balance = balance - p_amount
    WHERE account_id = p_from_account;

    UPDATE accounts
    SET balance = balance + p_amount
    WHERE account_id = p_to_account;

    -- Log the transfer
    INSERT INTO audit_log (action, details)
    VALUES (
        'TRANSFER',
        FORMAT('$%s from %s (acct %s) to %s (acct %s)',
               p_amount, v_from_owner, p_from_account,
               v_to_owner, p_to_account)
    );

    RETURN FORMAT('Success: $%s transferred from %s to %s',
                  p_amount, v_from_owner, v_to_owner);

EXCEPTION
    WHEN OTHERS THEN
        -- Log the error
        INSERT INTO audit_log (action, details)
        VALUES ('TRANSFER_FAILED', SQLERRM);
        RAISE;  -- Re-raise the exception
END;
$$;
```

### Using the Transfer Function

```sql
SELECT transfer_funds(1, 2, 500.00);
```

```
                   transfer_funds
---------------------------------------------------
 Success: $500.00 transferred from Alice to Bob
(1 row)
```

```sql
SELECT account_id, owner_name, balance FROM accounts;
```

```
 account_id | owner_name | balance
------------+------------+---------
          3 | Charlie    | 1500.00
          1 | Alice      | 4500.00
          2 | Bob        | 3500.00
(3 rows)
```

```sql
SELECT * FROM audit_log;
```

```
 log_id |  action  |                       details                        |         created_at
--------+----------+------------------------------------------------------+----------------------------
      1 | TRANSFER | $500.00 from Alice (acct 1) to Bob (acct 2)          | 2024-01-15 10:30:00.000000
(1 row)
```

### Testing Error Handling

```sql
SELECT transfer_funds(1, 2, 99999.00);
```

```
ERROR:  Insufficient funds. Account 1 has 4500.00, needs 99999.00
```

```sql
SELECT transfer_funds(1, 99, 100.00);
```

```
ERROR:  Destination account 99 not found
```

---

## Practical: Generate Report Function

A function that generates a product inventory report:

```sql
CREATE OR REPLACE FUNCTION generate_inventory_report()
RETURNS TABLE(
    report_line TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_products INT;
    v_total_value    DECIMAL;
    v_low_stock      INT;
    rec              RECORD;
BEGIN
    -- Header
    report_line := '=== INVENTORY REPORT ===';
    RETURN NEXT;
    report_line := 'Generated: ' || NOW()::DATE;
    RETURN NEXT;
    report_line := '';
    RETURN NEXT;

    -- Summary statistics
    SELECT COUNT(*), SUM(price * stock)
    INTO v_total_products, v_total_value
    FROM products;

    SELECT COUNT(*)
    INTO v_low_stock
    FROM products
    WHERE stock < 100;

    report_line := 'Total Products: ' || v_total_products;
    RETURN NEXT;
    report_line := 'Total Inventory Value: $' || TO_CHAR(v_total_value, 'FM999,999.99');
    RETURN NEXT;
    report_line := 'Low Stock Items: ' || v_low_stock;
    RETURN NEXT;
    report_line := '';
    RETURN NEXT;

    -- Detail section
    report_line := '--- PRODUCT DETAILS ---';
    RETURN NEXT;
    report_line := RPAD('Product', 15) || RPAD('Price', 12) ||
                   RPAD('Stock', 8) || 'Value';
    RETURN NEXT;
    report_line := REPEAT('-', 50);
    RETURN NEXT;

    FOR rec IN
        SELECT product_name, price, stock, (price * stock) AS value
        FROM products
        ORDER BY price * stock DESC
    LOOP
        report_line := RPAD(rec.product_name, 15) ||
                       RPAD('$' || rec.price, 12) ||
                       RPAD(rec.stock::TEXT, 8) ||
                       '$' || TO_CHAR(rec.value, 'FM999,999.99');
        RETURN NEXT;
    END LOOP;

    report_line := REPEAT('-', 50);
    RETURN NEXT;
    report_line := '=== END OF REPORT ===';
    RETURN NEXT;
END;
$$;
```

```sql
SELECT * FROM generate_inventory_report();
```

```
               report_line
---------------------------------------------------
 === INVENTORY REPORT ===
 Generated: 2024-01-15

 Total Products: 5
 Total Inventory Value: $107,645.50
 Low Stock Items: 2

 --- PRODUCT DETAILS ---
 Product        Price       Stock   Value
 --------------------------------------------------
 Laptop         $999.99     50      $49,999.50
 Monitor        $349.99     75      $26,249.25
 Headphones     $149.99     100     $14,999.00
 Keyboard       $79.99      150     $11,998.50
 Mouse          $29.99      200     $5,998.00
 --------------------------------------------------
 === END OF REPORT ===
(16 rows)
```

---

## Dropping Functions

To remove a function:

```sql
-- Drop a function (must match the parameter types)
DROP FUNCTION calculate_discount(DECIMAL, DECIMAL);

-- Drop if it exists (no error if it does not)
DROP FUNCTION IF EXISTS calculate_discount(DECIMAL, DECIMAL);
```

---

## Viewing Existing Functions

```sql
-- List all user-defined functions in the current schema
SELECT
    routine_name,
    routine_type,
    data_type AS return_type
FROM information_schema.routines
WHERE routine_schema = 'public'
ORDER BY routine_name;
```

```
       routine_name        | routine_type | return_type
---------------------------+--------------+------------
 apply_tax                 | FUNCTION     | numeric
 calculate_discount        | FUNCTION     | numeric
 calculate_order_total     | FUNCTION     | numeric
 compound_interest         | FUNCTION     | record
 generate_inventory_report | FUNCTION     | record
 get_account_summary       | FUNCTION     | record
 transfer_funds            | FUNCTION     | text
(7 rows)
```

---

## Common Mistakes

### Mistake 1: Variable Name Conflicts with Column Names

```sql
-- BAD: Variable 'name' conflicts with column 'name'
CREATE OR REPLACE FUNCTION bad_example(name VARCHAR)
RETURNS INT
LANGUAGE plpgsql
AS $$
BEGIN
    -- Does this compare to the parameter or the column?
    RETURN (SELECT COUNT(*) FROM products WHERE product_name = name);
END;
$$;

-- GOOD: Prefix parameters with p_ and variables with v_
CREATE OR REPLACE FUNCTION good_example(p_name VARCHAR)
RETURNS INT
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM products WHERE product_name = p_name);
END;
$$;
```

### Mistake 2: Forgetting IF NOT FOUND

```sql
-- BAD: Does not check if the SELECT found anything
SELECT price INTO v_price FROM products WHERE product_id = p_id;
-- v_price is NULL if not found, which may cause silent bugs

-- GOOD: Always check
SELECT price INTO v_price FROM products WHERE product_id = p_id;
IF NOT FOUND THEN
    RAISE EXCEPTION 'Product % not found', p_id;
END IF;
```

### Mistake 3: Using RETURN in a RETURNS TABLE Function

```sql
-- BAD: RETURN exits the function immediately
-- Use RETURN NEXT to add rows, then the function ends naturally

-- GOOD pattern for RETURNS TABLE functions:
--   Set column values, then call RETURN NEXT for each row
--   The function returns all accumulated rows when it ends
```

### Mistake 4: Not Using CREATE OR REPLACE

```sql
-- BAD: CREATE FUNCTION fails if function already exists
CREATE FUNCTION my_func() ...

-- GOOD: CREATE OR REPLACE updates the function if it exists
CREATE OR REPLACE FUNCTION my_func() ...
```

---

## Best Practices

1. **Use naming conventions.** Prefix parameters with `p_` and local variables with `v_`. This prevents ambiguity with column names.

2. **Always validate inputs.** Check for NULL values, negative numbers, and invalid IDs at the start of the function.

3. **Use CREATE OR REPLACE.** This makes it easy to update functions during development without dropping them first.

4. **Keep functions focused.** Each function should do one thing well. A function that calculates a discount should not also send an email.

5. **Use RAISE NOTICE during development** for debugging. Remove or change to DEBUG level before deploying to production.

6. **Handle errors with EXCEPTION blocks.** Catch specific exceptions when possible, and always provide helpful error messages.

7. **Document your functions** with comments explaining what they do, what parameters they expect, and what they return.

8. **Use transactions within functions** when multiple tables need to be updated together (functions run inside the caller's transaction by default).

---

## Quick Summary

```
+-----------------------+----------------------------------------------+
| Concept               | What It Does                                 |
+-----------------------+----------------------------------------------+
| CREATE FUNCTION       | Creates a new stored function                |
| CREATE OR REPLACE     | Creates or updates a function                |
| RETURNS type          | Declares the return type                     |
| RETURNS TABLE(...)    | Returns multiple columns/rows                |
| LANGUAGE plpgsql      | Uses PostgreSQL's procedural language        |
| DECLARE               | Section for declaring local variables        |
| :=                    | Assignment operator                          |
| IF/ELSIF/ELSE/END IF  | Conditional logic                            |
| FOR i IN 1..10 LOOP   | Loop over a range                            |
| FOR rec IN query LOOP | Loop over query results                      |
| WHILE condition LOOP  | Loop while condition is true                 |
| RETURN                | Return a single value and exit               |
| RETURN NEXT           | Add a row to the result set (RETURNS TABLE)  |
| RETURN QUERY          | Add query results to the result set          |
| RAISE NOTICE          | Print a debug message                        |
| RAISE EXCEPTION       | Throw an error (aborts transaction)          |
| EXCEPTION WHEN        | Catch and handle errors                      |
| NOT FOUND             | True when SELECT INTO finds no rows          |
| DROP FUNCTION         | Remove a function                            |
+-----------------------+----------------------------------------------+
```

---

## Key Points

- Stored functions are saved programs in the database created with CREATE FUNCTION.
- PL/pgSQL is PostgreSQL's procedural language for writing functions with variables, logic, and loops.
- Parameters can be IN (input), OUT (output), or INOUT (both).
- DECLARE lets you define local variables with types and optional default values.
- Use IF/ELSIF/ELSE for conditional logic and FOR/WHILE for loops.
- RAISE NOTICE is the primary debugging tool. RAISE EXCEPTION stops execution and rolls back.
- RETURNS TABLE lets functions return multiple rows and columns.
- RETURN NEXT adds one row at a time to the result set.
- Always prefix parameters with `p_` and variables with `v_` to avoid name conflicts with column names.
- Functions run inside the caller's transaction by default.

---

## Practice Questions

1. What is the difference between RETURN and RETURN NEXT? When do you use each?

2. What happens when RAISE EXCEPTION is called inside a function? What happens to any changes the function already made?

3. Why should you prefix parameter names with `p_` and variable names with `v_`? What problem does this solve?

4. What does the NOT FOUND special variable tell you? When is it set?

5. How do you update an existing function without dropping it first?

---

## Exercises

### Exercise 1: Tiered Discount Function

Create a function called `tiered_discount` that takes a product price and quantity, then returns the discounted total:
- 1-9 items: no discount
- 10-49 items: 5% discount
- 50-99 items: 10% discount
- 100+ items: 15% discount

Include input validation (price must be positive, quantity must be at least 1).

### Exercise 2: Account Statement Function

Create a function called `account_statement` that takes an account_id and returns a formatted statement showing:
- Account holder name
- Current balance
- Account status (Gold/Silver/Bronze based on balance)
- The last 5 transactions from the audit_log related to that account

Use RETURNS TABLE and RETURN NEXT to build the output.

### Exercise 3: Stock Reorder Function

Create a function called `reorder_stock` that:
1. Takes a minimum stock threshold as input
2. Finds all products below that threshold
3. Calculates how many units to order to bring stock up to the threshold
4. Inserts a record into an `orders_placed` table for each product
5. Returns a summary of what was ordered
6. Uses RAISE NOTICE to show progress during execution

---

## What Is Next?

In Chapter 29, you will learn about triggers — automatic actions that fire when data changes. Triggers use the same PL/pgSQL language you just learned, but they run automatically in response to INSERT, UPDATE, or DELETE operations. They are perfect for audit logging, automatic timestamps, and data validation.
