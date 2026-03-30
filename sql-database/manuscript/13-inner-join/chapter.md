# Chapter 13: INNER JOIN — Finding Matching Rows Across Tables

## What You Will Learn

- How INNER JOIN works and why it only returns matching rows
- How to use the ON clause to specify join conditions
- How to use table aliases to write shorter, cleaner queries
- How to join tables using foreign keys
- How to join three or more tables in a single query
- How to combine JOIN with WHERE, ORDER BY, and LIMIT
- How to solve real-world problems: employees with departments, orders with customers and products

## Why This Chapter Matters

In the previous chapter, you learned what joins are and why relational databases split data across multiple tables. Now it is time to learn the most common join type: INNER JOIN.

Think of INNER JOIN like a matchmaking service. You have two guest lists for a party. INNER JOIN finds the people who appear on **both** lists. If someone is only on one list, they do not show up in the results.

In real-world applications, you use INNER JOIN constantly. Every time you display an order with the customer name, show an employee with their department, or list products with their categories, you are using INNER JOIN.

---

## Setting Up Our Practice Tables

Let us create some tables we will use throughout this chapter.

```sql
CREATE TABLE departments (
    department_id   SERIAL PRIMARY KEY,
    department_name VARCHAR(50) NOT NULL,
    location        VARCHAR(50)
);

CREATE TABLE employees (
    employee_id   SERIAL PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    email         VARCHAR(100),
    salary        NUMERIC(10, 2),
    department_id INTEGER REFERENCES departments(department_id)
);

CREATE TABLE customers (
    customer_id  SERIAL PRIMARY KEY,
    first_name   VARCHAR(50) NOT NULL,
    last_name    VARCHAR(50) NOT NULL,
    email        VARCHAR(100)
);

CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price        NUMERIC(10, 2),
    category     VARCHAR(50)
);

CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_id  INTEGER REFERENCES products(product_id),
    quantity    INTEGER,
    order_date  DATE
);
```

Now let us insert some data.

```sql
INSERT INTO departments (department_name, location) VALUES
('Engineering', 'Building A'),
('Marketing',   'Building B'),
('Sales',       'Building C'),
('HR',          'Building D');

INSERT INTO employees (first_name, last_name, email, salary, department_id) VALUES
('Alice',   'Johnson',  'alice@company.com',   85000, 1),
('Bob',     'Smith',    'bob@company.com',     72000, 1),
('Charlie', 'Brown',    'charlie@company.com', 65000, 2),
('Diana',   'Lee',      'diana@company.com',   78000, 3),
('Eve',     'Davis',    'eve@company.com',     90000, 1),
('Frank',   'Wilson',   'frank@company.com',   60000, NULL);

INSERT INTO customers (first_name, last_name, email) VALUES
('Grace',  'Taylor',   'grace@email.com'),
('Henry',  'Martinez', 'henry@email.com'),
('Ivy',    'Anderson', 'ivy@email.com'),
('Jack',   'Thomas',   'jack@email.com');

INSERT INTO products (product_name, price, category) VALUES
('Laptop',    999.99, 'Electronics'),
('Keyboard',   49.99, 'Electronics'),
('Desk Chair', 299.99, 'Furniture'),
('Monitor',   399.99, 'Electronics');

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2024-01-15'),
(1, 2, 2, '2024-01-15'),
(2, 3, 1, '2024-02-20'),
(3, 1, 1, '2024-03-10'),
(3, 4, 1, '2024-03-10');
```

---

## How INNER JOIN Works

INNER JOIN combines rows from two tables where the join condition is true. If a row in one table does not have a matching row in the other table, it is excluded from the results.

### The Basic Syntax

```sql
SELECT columns
FROM table_a
INNER JOIN table_b
    ON table_a.column = table_b.column;
```

Think of it step by step:

1. Start with `table_a` (the "left" table)
2. For each row in `table_a`, look at every row in `table_b`
3. If the ON condition is true, combine those two rows into one result row
4. If no match is found, skip that row entirely

### A Visual Way to Think About It

Imagine two circles in a Venn diagram. INNER JOIN returns only the overlapping area — the rows that exist in both tables.

```
    Table A           Table B
  +---------+     +---------+
  |         |     |         |
  |    +----+-----+----+    |
  |    |  INNER JOIN   |    |
  |    |  (matches)    |    |
  |    +----+-----+----+    |
  |         |     |         |
  +---------+     +---------+

  Only the middle section is returned.
```

---

## Your First INNER JOIN

Let us find all employees along with their department names.

```sql
SELECT employees.first_name,
       employees.last_name,
       departments.department_name
FROM employees
INNER JOIN departments
    ON employees.department_id = departments.department_id;
```

**Result:**

```
+------------+-----------+-----------------+
| first_name | last_name | department_name |
+------------+-----------+-----------------+
| Alice      | Johnson   | Engineering     |
| Bob        | Smith     | Engineering     |
| Charlie    | Brown     | Marketing       |
| Diana      | Lee       | Sales           |
| Eve        | Davis     | Engineering     |
+------------+-----------+-----------------+
(5 rows)
```

### Line-by-Line Explanation

```
SELECT employees.first_name,       -- Get first_name from employees table
       employees.last_name,        -- Get last_name from employees table
       departments.department_name -- Get department_name from departments table
FROM employees                     -- Start with the employees table
INNER JOIN departments             -- Combine with the departments table
    ON employees.department_id     -- Where the department_id in employees
     = departments.department_id;  -- matches department_id in departments
```

**Notice:** Frank Wilson does not appear in the results. His `department_id` is NULL, so there is no matching row in the departments table. The HR department also does not appear because no employee belongs to it. INNER JOIN only returns matches.

---

## Table Aliases — Writing Cleaner Queries

Typing full table names like `employees.first_name` gets tedious. Table aliases let you give tables short nicknames.

```sql
SELECT e.first_name,
       e.last_name,
       d.department_name
FROM employees AS e
INNER JOIN departments AS d
    ON e.department_id = d.department_id;
```

The `AS` keyword is optional. This works exactly the same:

```sql
SELECT e.first_name,
       e.last_name,
       d.department_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id;
```

**Result:**

```
+------------+-----------+-----------------+
| first_name | last_name | department_name |
+------------+-----------+-----------------+
| Alice      | Johnson   | Engineering     |
| Bob        | Smith     | Engineering     |
| Charlie    | Brown     | Marketing       |
| Diana      | Lee       | Sales           |
| Eve        | Davis     | Engineering     |
+------------+-----------+-----------------+
(5 rows)
```

Common alias conventions:

- `employees` becomes `e`
- `departments` becomes `d`
- `customers` becomes `c`
- `orders` becomes `o`
- `products` becomes `p`

Think of it like a nickname. Your friend "Alexander" might go by "Alex." The table `employees` goes by `e`.

---

## Joining on Foreign Keys

The ON clause almost always matches a **foreign key** in one table with the **primary key** in another. This is the glue that holds relational databases together.

```
employees table                    departments table
+-------------+---------------+    +---------------+-----------------+
| employee_id | department_id |    | department_id | department_name |
+-------------+---------------+    +---------------+-----------------+
| 1           | 1          ---+--->| 1             | Engineering     |
| 2           | 1          ---+--->| 1             | Engineering     |
| 3           | 2          ---+--->| 2             | Marketing       |
| 4           | 3          ---+--->| 3             | Sales           |
| 5           | 1          ---+--->| 1             | Engineering     |
| 6           | NULL (no match)|  | 4             | HR              |
+-------------+---------------+    +---------------+-----------------+

The arrows show FK -> PK relationships.
INNER JOIN follows these arrows to combine rows.
```

The foreign key (`employees.department_id`) points to the primary key (`departments.department_id`). INNER JOIN follows these references to combine the data.

---

## JOIN with WHERE — Filtering Joined Results

You can add a WHERE clause after a JOIN to filter the combined results.

**Find all Engineering employees:**

```sql
SELECT e.first_name,
       e.last_name,
       d.department_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id
WHERE d.department_name = 'Engineering';
```

**Result:**

```
+------------+-----------+-----------------+
| first_name | last_name | department_name |
+------------+-----------+-----------------+
| Alice      | Johnson   | Engineering     |
| Bob        | Smith     | Engineering     |
| Eve        | Davis     | Engineering     |
+------------+-----------+-----------------+
(3 rows)
```

### Line-by-Line Explanation

```
SELECT e.first_name,              -- Columns we want
       e.last_name,
       d.department_name
FROM employees e                  -- Start with employees
INNER JOIN departments d          -- Combine with departments
    ON e.department_id            -- Match on department_id
     = d.department_id
WHERE d.department_name           -- Then filter: only keep rows
    = 'Engineering';              -- where department is Engineering
```

**The order of operations matters:**

1. First, the JOIN combines the tables
2. Then, the WHERE filters the combined results

---

## JOIN with ORDER BY and LIMIT

**Find the top 3 highest-paid employees and their departments:**

```sql
SELECT e.first_name,
       e.last_name,
       e.salary,
       d.department_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id
ORDER BY e.salary DESC
LIMIT 3;
```

**Result:**

```
+------------+-----------+----------+-----------------+
| first_name | last_name | salary   | department_name |
+------------+-----------+----------+-----------------+
| Eve        | Davis     | 90000.00 | Engineering     |
| Alice      | Johnson   | 85000.00 | Engineering     |
| Diana      | Lee       | 78000.00 | Sales           |
+------------+-----------+----------+-----------------+
(3 rows)
```

The execution order is: FROM -> JOIN -> WHERE -> ORDER BY -> LIMIT. Think of it as a pipeline: first you gather all the data, then you sort it, then you chop off the extras.

---

## Multi-Table Joins — Joining Three or More Tables

Real applications often need data from three, four, or even more tables. You simply chain multiple JOIN clauses together.

### Orders with Customer Names and Product Names

```sql
SELECT o.order_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       p.product_name,
       o.quantity,
       p.price,
       (o.quantity * p.price) AS total,
       o.order_date
FROM orders o
INNER JOIN customers c
    ON o.customer_id = c.customer_id
INNER JOIN products p
    ON o.product_id = p.product_id;
```

**Result:**

```
+----------+----------------+--------------+----------+--------+---------+------------+
| order_id | customer_name  | product_name | quantity | price  | total   | order_date |
+----------+----------------+--------------+----------+--------+---------+------------+
|        1 | Grace Taylor   | Laptop       |        1 | 999.99 |  999.99 | 2024-01-15 |
|        2 | Grace Taylor   | Keyboard     |        2 |  49.99 |   99.98 | 2024-01-15 |
|        3 | Henry Martinez | Desk Chair   |        1 | 299.99 |  299.99 | 2024-02-20 |
|        4 | Ivy Anderson   | Laptop       |        1 | 999.99 |  999.99 | 2024-03-10 |
|        5 | Ivy Anderson   | Monitor      |        1 | 399.99 |  399.99 | 2024-03-10 |
+----------+----------------+--------------+----------+--------+---------+------------+
(5 rows)
```

### Line-by-Line Explanation

```
SELECT o.order_id,                                    -- Order ID from orders
       c.first_name || ' ' || c.last_name             -- Combine first + last name
           AS customer_name,                           -- Call it customer_name
       p.product_name,                                 -- Product name from products
       o.quantity,                                     -- Quantity from orders
       p.price,                                        -- Price from products
       (o.quantity * p.price) AS total,                -- Calculate total cost
       o.order_date                                    -- Order date from orders
FROM orders o                                          -- Start with orders
INNER JOIN customers c                                 -- Join to customers
    ON o.customer_id = c.customer_id                   -- Match on customer_id
INNER JOIN products p                                  -- Also join to products
    ON o.product_id = p.product_id;                    -- Match on product_id
```

### How Multi-Table Joins Work — Step by Step

```
Step 1: Start with orders
+----------+-------------+------------+----------+
| order_id | customer_id | product_id | quantity |
+----------+-------------+------------+----------+
|        1 |           1 |          1 |        1 |
+----------+-------------+------------+----------+

Step 2: Join with customers (match customer_id)
+----------+-------------+------------+----------+----------------+
| order_id | customer_id | product_id | quantity | customer_name  |
+----------+-------------+------------+----------+----------------+
|        1 |           1 |          1 |        1 | Grace Taylor   |
+----------+-------------+------------+----------+----------------+

Step 3: Join with products (match product_id)
+----------+----------------+--------------+----------+--------+
| order_id | customer_name  | product_name | quantity | price  |
+----------+----------------+--------------+----------+--------+
|        1 | Grace Taylor   | Laptop       |        1 | 999.99 |
+----------+----------------+--------------+----------+--------+
```

Each JOIN adds more columns from another table. Think of it like adding more pieces to a puzzle — each JOIN snaps in another piece of information.

---

## Practical Example: Employee Directory

Let us build a full employee directory with department info, filtering, and sorting.

```sql
SELECT e.employee_id,
       e.first_name || ' ' || e.last_name AS full_name,
       e.email,
       d.department_name,
       d.location,
       e.salary
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id
WHERE e.salary > 70000
ORDER BY d.department_name, e.last_name;
```

**Result:**

```
+-------------+--------------+---------------------+-----------------+------------+----------+
| employee_id | full_name    | email               | department_name | location   | salary   |
+-------------+--------------+---------------------+-----------------+------------+----------+
|           1 | Alice Johnson| alice@company.com   | Engineering     | Building A | 85000.00 |
|           5 | Eve Davis    | eve@company.com     | Engineering     | Building A | 90000.00 |
|           2 | Bob Smith    | bob@company.com     | Engineering     | Building A | 72000.00 |
|           4 | Diana Lee    | diana@company.com   | Sales           | Building C | 78000.00 |
+-------------+--------------+---------------------+-----------------+------------+----------+
(4 rows)
```

---

## Practical Example: Order Summary Report

Create a report showing orders with all related information.

```sql
SELECT o.order_id,
       o.order_date,
       c.first_name || ' ' || c.last_name AS customer,
       c.email AS customer_email,
       p.product_name,
       p.category,
       o.quantity,
       p.price AS unit_price,
       (o.quantity * p.price) AS line_total
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN products p  ON o.product_id  = p.product_id
WHERE o.order_date >= '2024-02-01'
ORDER BY o.order_date, o.order_id;
```

**Result:**

```
+----------+------------+----------------+------------------+--------------+-------------+----------+------------+------------+
| order_id | order_date | customer       | customer_email   | product_name | category    | quantity | unit_price | line_total |
+----------+------------+----------------+------------------+--------------+-------------+----------+------------+------------+
|        3 | 2024-02-20 | Henry Martinez | henry@email.com  | Desk Chair   | Furniture   |        1 |     299.99 |     299.99 |
|        4 | 2024-03-10 | Ivy Anderson   | ivy@email.com    | Laptop       | Electronics |        1 |     999.99 |     999.99 |
|        5 | 2024-03-10 | Ivy Anderson   | ivy@email.com    | Monitor      | Electronics |        1 |     399.99 |     399.99 |
+----------+------------+----------------+------------------+--------------+-------------+----------+------------+------------+
(3 rows)
```

---

## JOIN vs. Comma Syntax (Old Style — Avoid It)

You might see older SQL that uses commas instead of JOIN:

```sql
-- Old style (avoid this)
SELECT e.first_name, d.department_name
FROM employees e, departments d
WHERE e.department_id = d.department_id;

-- Modern style (use this)
SELECT e.first_name, d.department_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id;
```

Both produce the same result, but the modern JOIN syntax is:

- **Clearer** — the join condition is separate from the filter condition
- **Safer** — if you forget the WHERE clause with comma syntax, you get a cartesian product (every row combined with every other row)
- **Standard** — supported by all modern databases

---

## Common Mistakes

### Mistake 1: Forgetting the ON Clause

```sql
-- WRONG: This will cause an error or unexpected results
SELECT e.first_name, d.department_name
FROM employees e
INNER JOIN departments d;
-- Missing ON clause!
```

**Fix:** Always include the ON clause to specify how the tables relate.

```sql
-- CORRECT
SELECT e.first_name, d.department_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id;
```

### Mistake 2: Ambiguous Column Names

```sql
-- WRONG: department_id exists in both tables
SELECT first_name, department_id
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id;
-- ERROR: column reference "department_id" is ambiguous
```

**Fix:** Always prefix the column with the table alias.

```sql
-- CORRECT
SELECT e.first_name, e.department_id
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id;
```

### Mistake 3: Expecting Non-Matching Rows to Appear

```sql
-- This will NOT show Frank (department_id is NULL)
-- This will NOT show HR (no employees)
SELECT e.first_name, d.department_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id;
```

**Fix:** If you need non-matching rows, use LEFT JOIN or RIGHT JOIN (next chapter).

### Mistake 4: Wrong Join Column

```sql
-- WRONG: Joining on the wrong columns
SELECT e.first_name, d.department_name
FROM employees e
INNER JOIN departments d
    ON e.employee_id = d.department_id;
-- This joins employee_id to department_id — nonsense!
```

**Fix:** Make sure you join on the foreign key and the primary key it references.

---

## Best Practices

1. **Always use table aliases.** They make queries shorter and easier to read. Use meaningful single letters (e for employees, d for departments).

2. **Always qualify column names.** Write `e.first_name` instead of just `first_name`, even if the column name is unique. It makes the query self-documenting.

3. **Use the modern JOIN syntax.** Write `INNER JOIN ... ON` instead of comma-separated tables with WHERE. It is clearer and less error-prone.

4. **Join on foreign key to primary key.** This is the standard pattern. If you find yourself joining on other columns, double-check your logic.

5. **Put each JOIN on its own line.** When you have multiple joins, put each one on a separate line for readability.

6. **Think about what gets excluded.** INNER JOIN drops non-matching rows. Always ask yourself: "Is it okay if some rows are missing from the results?"

---

## Quick Summary

| Concept | Description |
|---------|-------------|
| INNER JOIN | Returns only rows that have matches in both tables |
| ON clause | Specifies the condition for matching rows |
| Table alias | A short name for a table (e.g., `employees e`) |
| Foreign key join | Matching FK in one table to PK in another |
| Multi-table join | Chaining multiple JOIN clauses in one query |
| JOIN + WHERE | First join, then filter the combined results |

---

## Key Points

- INNER JOIN returns **only matching rows**. If there is no match, the row is excluded.
- The ON clause defines **how** to match rows between tables, usually using a foreign key.
- Table aliases (`FROM employees e`) make your SQL shorter and more readable.
- You can chain multiple INNER JOINs to combine three or more tables.
- WHERE, ORDER BY, and LIMIT work with JOINs just like with single tables.
- INNER JOIN is the **default** join type. Writing `JOIN` without `INNER` works the same way.
- If you need rows that do NOT have matches, INNER JOIN is the wrong choice. Use LEFT JOIN instead.

---

## Practice Questions

**Question 1:** What is the difference between the ON clause and the WHERE clause in a JOIN query?

<details>
<summary>Answer</summary>

The ON clause specifies **how** to match rows between two tables (the join condition). The WHERE clause **filters** the results after the join has been performed. For INNER JOIN, you can technically put conditions in either place and get the same result, but best practice is to use ON for the join condition and WHERE for filtering.

</details>

**Question 2:** Why does Frank Wilson not appear in the results when we INNER JOIN employees with departments?

<details>
<summary>Answer</summary>

Frank's `department_id` is NULL. INNER JOIN only returns rows where the ON condition finds a match. Since NULL does not equal any value (not even another NULL), there is no matching department for Frank, so his row is excluded.

</details>

**Question 3:** Write a query to find all orders placed by "Grace Taylor" and show the product names.

<details>
<summary>Answer</summary>

```sql
SELECT o.order_id,
       p.product_name,
       o.quantity,
       o.order_date
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN products p  ON o.product_id  = p.product_id
WHERE c.first_name = 'Grace'
  AND c.last_name  = 'Taylor';
```

</details>

**Question 4:** What happens if you write JOIN instead of INNER JOIN?

<details>
<summary>Answer</summary>

Nothing different. `JOIN` is shorthand for `INNER JOIN`. They produce exactly the same result. Most developers use `INNER JOIN` for clarity, but `JOIN` alone is perfectly valid.

</details>

**Question 5:** Can you join a table to itself? What would that be called?

<details>
<summary>Answer</summary>

Yes, you can. It is called a **self join**. You would give the same table two different aliases. We will cover this in Chapter 15.

</details>

---

## Exercises

### Exercise 1: Employee Department Report

Write a query that shows each employee's full name (first and last combined), their email, department name, and location. Sort the results by department name, then by last name.

<details>
<summary>Solution</summary>

```sql
SELECT e.first_name || ' ' || e.last_name AS full_name,
       e.email,
       d.department_name,
       d.location
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id
ORDER BY d.department_name, e.last_name;
```

Expected output:

```
+---------------+---------------------+-----------------+------------+
| full_name     | email               | department_name | location   |
+---------------+---------------------+-----------------+------------+
| Eve Davis     | eve@company.com     | Engineering     | Building A |
| Alice Johnson | alice@company.com   | Engineering     | Building A |
| Bob Smith     | bob@company.com     | Engineering     | Building A |
| Charlie Brown | charlie@company.com | Marketing       | Building B |
| Diana Lee     | diana@company.com   | Sales           | Building C |
+---------------+---------------------+-----------------+------------+
```

</details>

### Exercise 2: Customer Order Summary

Write a query that shows each customer's name, the products they ordered, quantities, and the total cost for each line item. Only show orders from March 2024 or later. Sort by order date.

<details>
<summary>Solution</summary>

```sql
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       p.product_name,
       o.quantity,
       p.price,
       (o.quantity * p.price) AS total_cost,
       o.order_date
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN products p  ON o.product_id  = p.product_id
WHERE o.order_date >= '2024-03-01'
ORDER BY o.order_date;
```

Expected output:

```
+---------------+--------------+----------+--------+------------+------------+
| customer_name | product_name | quantity | price  | total_cost | order_date |
+---------------+--------------+----------+--------+------------+------------+
| Ivy Anderson  | Laptop       |        1 | 999.99 |     999.99 | 2024-03-10 |
| Ivy Anderson  | Monitor      |        1 | 399.99 |     399.99 | 2024-03-10 |
+---------------+--------------+----------+--------+------------+------------+
```

</details>

### Exercise 3: Department Salary Report

Write a query that shows each department's name and the number of employees in it, along with the average salary. Only show departments that have more than one employee. Sort by average salary descending.

<details>
<summary>Solution</summary>

```sql
SELECT d.department_name,
       COUNT(e.employee_id) AS employee_count,
       ROUND(AVG(e.salary), 2) AS avg_salary
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id
GROUP BY d.department_name
HAVING COUNT(e.employee_id) > 1
ORDER BY avg_salary DESC;
```

Expected output:

```
+-----------------+----------------+------------+
| department_name | employee_count | avg_salary |
+-----------------+----------------+------------+
| Engineering     |              3 |   82333.33 |
+-----------------+----------------+------------+
```

</details>

---

## What Is Next?

INNER JOIN is powerful, but it has a limitation: it drops rows that do not have matches. What if you want to see ALL employees, even those without a department? Or ALL departments, even those with no employees?

In the next chapter, you will learn about **LEFT JOIN** and **RIGHT JOIN** — join types that keep non-matching rows and fill in NULL for the missing data. This is essential for finding gaps in your data, like customers who have never placed an order.
