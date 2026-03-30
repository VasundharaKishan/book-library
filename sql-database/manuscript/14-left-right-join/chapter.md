# Chapter 14: LEFT JOIN and RIGHT JOIN — Keeping Non-Matching Rows

## What You Will Learn

- How LEFT JOIN works and why it keeps all rows from the left table
- How RIGHT JOIN works and why it keeps all rows from the right table
- What happens to non-matching rows (they get NULLs)
- How to find rows WITHOUT matches using WHERE ... IS NULL
- Practical patterns: customers without orders, departments without employees
- Why LEFT JOIN and RIGHT JOIN are interchangeable (just swap the table order)

## Why This Chapter Matters

In the previous chapter, you learned that INNER JOIN drops any row that does not have a match. But sometimes the missing data IS the important data.

Think about a classroom. INNER JOIN is like calling roll and only listing students who are present. But what if you need to know who is **absent**? That is what LEFT JOIN is for — it keeps everyone from your list, even if they did not show up.

In real applications, LEFT JOIN is one of the most frequently used join types. Finding customers who have not placed orders, employees without assigned projects, or products that have never been sold — all of these require LEFT JOIN.

---

## Quick Refresher: Our Practice Tables

We will continue using the same tables from Chapter 13. Here is a quick reminder of the data:

```
employees:                              departments:
+----+---------+-----------+--------+   +----+-----------------+------------+
| id | first   | last      | dep_id |   | id | department_name | location   |
+----+---------+-----------+--------+   +----+-----------------+------------+
|  1 | Alice   | Johnson   |      1 |   |  1 | Engineering     | Building A |
|  2 | Bob     | Smith     |      1 |   |  2 | Marketing       | Building B |
|  3 | Charlie | Brown     |      2 |   |  3 | Sales           | Building C |
|  4 | Diana   | Lee       |      3 |   |  4 | HR              | Building D |
|  5 | Eve     | Davis     |      1 |   +----+-----------------+------------+
|  6 | Frank   | Wilson    | NULL   |
+----+---------+-----------+--------+

customers:                     orders:
+----+-------+-----------+     +----+------+------+-----+------------+
| id | first | last      |     | id | c_id | p_id | qty | order_date |
+----+-------+-----------+     +----+------+------+-----+------------+
|  1 | Grace | Taylor    |     |  1 |    1 |    1 |   1 | 2024-01-15 |
|  2 | Henry | Martinez  |     |  2 |    1 |    2 |   2 | 2024-01-15 |
|  3 | Ivy   | Anderson  |     |  3 |    2 |    3 |   1 | 2024-02-20 |
|  4 | Jack  | Thomas    |     |  4 |    3 |    1 |   1 | 2024-03-10 |
+----+-------+-----------+     |  5 |    3 |    4 |   1 | 2024-03-10 |
                               +----+------+------+-----+------------+

Notice: Jack Thomas (customer 4) has NO orders.
Notice: Frank Wilson (employee 6) has NO department.
Notice: HR (department 4) has NO employees.
```

---

## How LEFT JOIN Works

LEFT JOIN returns **all rows** from the left table (the one after FROM), plus any matching rows from the right table (the one after JOIN). If there is no match, the columns from the right table are filled with NULL.

### The Syntax

```sql
SELECT columns
FROM left_table
LEFT JOIN right_table
    ON left_table.column = right_table.column;
```

### Visual Representation

```
    Left Table        Right Table
  +-----------+     +-----------+
  |           |     |           |
  |  +--------+-----+----+     |
  |  | matches|     |    |     |
  |  +--------+-----+----+     |
  |  kept     |     |  dropped |
  |  (NULLs)  |     |          |
  +-----------+     +-----------+

  Everything in the left circle is returned.
  The right side only contributes matching rows.
```

---

## Your First LEFT JOIN

Let us find all employees and their departments — including employees without a department.

```sql
SELECT e.first_name,
       e.last_name,
       d.department_name
FROM employees e
LEFT JOIN departments d
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
| Frank      | Wilson    | NULL            |
+------------+-----------+-----------------+
(6 rows)
```

### Line-by-Line Explanation

```
SELECT e.first_name,          -- Get first_name from employees
       e.last_name,           -- Get last_name from employees
       d.department_name      -- Get department_name from departments
FROM employees e              -- Start with ALL employees (left table)
LEFT JOIN departments d       -- Try to match with departments (right table)
    ON e.department_id        -- Where department_id in employees
     = d.department_id;       -- matches department_id in departments
```

**Compare with INNER JOIN:**

| Employee | INNER JOIN | LEFT JOIN |
|----------|-----------|-----------|
| Alice    | Shows     | Shows     |
| Bob      | Shows     | Shows     |
| Charlie  | Shows     | Shows     |
| Diana    | Shows     | Shows     |
| Eve      | Shows     | Shows     |
| Frank    | **Missing** | Shows (NULL department) |

Frank appears in LEFT JOIN but not in INNER JOIN. His department columns are filled with NULL because there is no matching department.

---

## How RIGHT JOIN Works

RIGHT JOIN is the mirror image of LEFT JOIN. It returns **all rows** from the right table (the one after JOIN), plus any matching rows from the left table. If there is no match, the columns from the left table are filled with NULL.

### The Syntax

```sql
SELECT columns
FROM left_table
RIGHT JOIN right_table
    ON left_table.column = right_table.column;
```

### Visual Representation

```
    Left Table        Right Table
  +-----------+     +-----------+
  |           |     |           |
  |    +------+-----+------+   |
  |    | matches     |     |   |
  |    +------+-----+------+   |
  |  dropped  |     |  kept    |
  |           |     |  (NULLs) |
  +-----------+     +-----------+

  Everything in the right circle is returned.
  The left side only contributes matching rows.
```

### RIGHT JOIN Example

Find all departments and their employees — including departments with no employees.

```sql
SELECT e.first_name,
       e.last_name,
       d.department_name
FROM employees e
RIGHT JOIN departments d
    ON e.department_id = d.department_id;
```

**Result:**

```
+------------+-----------+-----------------+
| first_name | last_name | department_name |
+------------+-----------+-----------------+
| Alice      | Johnson   | Engineering     |
| Bob        | Smith     | Engineering     |
| Eve        | Davis     | Engineering     |
| Charlie    | Brown     | Marketing       |
| Diana      | Lee       | Sales           |
| NULL       | NULL      | HR              |
+------------+-----------+-----------------+
(6 rows)
```

Notice that the HR department appears even though no employee belongs to it. The employee columns (first_name, last_name) are NULL for that row.

---

## LEFT JOIN vs RIGHT JOIN — They Are Interchangeable

Here is an important insight: **any RIGHT JOIN can be rewritten as a LEFT JOIN by swapping the table order.**

These two queries produce the exact same result:

```sql
-- Using RIGHT JOIN
SELECT e.first_name, d.department_name
FROM employees e
RIGHT JOIN departments d
    ON e.department_id = d.department_id;

-- Same result using LEFT JOIN (tables swapped)
SELECT e.first_name, d.department_name
FROM departments d
LEFT JOIN employees e
    ON d.department_id = e.department_id;
```

Both return all departments, including those without employees.

**In practice, most developers use LEFT JOIN exclusively** and simply adjust which table comes first. This keeps your queries consistent and easier to read.

```
RIGHT JOIN:  A RIGHT JOIN B  =  B LEFT JOIN A

Just swap the table order and change RIGHT to LEFT.
```

---

## NULL for Non-Matching Rows

When LEFT JOIN (or RIGHT JOIN) finds no match, it fills in NULL for every column from the unmatched table. This is important to understand because NULL behaves differently from regular values.

```sql
SELECT e.first_name,
       e.last_name,
       d.department_name,
       d.location
FROM employees e
LEFT JOIN departments d
    ON e.department_id = d.department_id;
```

**Result:**

```
+------------+-----------+-----------------+------------+
| first_name | last_name | department_name | location   |
+------------+-----------+-----------------+------------+
| Alice      | Johnson   | Engineering     | Building A |
| Bob        | Smith     | Engineering     | Building A |
| Charlie    | Brown     | Marketing       | Building B |
| Diana      | Lee       | Sales           | Building C |
| Eve        | Davis     | Engineering     | Building A |
| Frank      | Wilson    | NULL            | NULL       |
+------------+-----------+-----------------+------------+
(6 rows)
```

For Frank, **both** department_name and location are NULL. Every column from the right table becomes NULL when there is no match.

---

## Finding Rows WITHOUT Matches — The Anti-Join Pattern

One of the most powerful uses of LEFT JOIN is finding rows that do **not** have a match. This is called an **anti-join** pattern.

The trick: Use LEFT JOIN, then filter for rows where the right table's key IS NULL.

### Pattern: Find Customers Without Orders

```sql
SELECT c.first_name,
       c.last_name,
       c.email
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

**Result:**

```
+------------+-----------+------------------+
| first_name | last_name | email            |
+------------+-----------+------------------+
| Jack       | Thomas    | jack@email.com   |
+------------+-----------+------------------+
(1 row)
```

### Line-by-Line Explanation

```
SELECT c.first_name,           -- Customer first name
       c.last_name,            -- Customer last name
       c.email                 -- Customer email
FROM customers c               -- Start with ALL customers
LEFT JOIN orders o             -- Try to match with orders
    ON c.customer_id           -- Match on customer_id
     = o.customer_id
WHERE o.order_id IS NULL;      -- Keep ONLY rows where no order exists
```

### How It Works — Step by Step

```
Step 1: LEFT JOIN (all customers, matched orders)

+-------+---------+----------+
| c_id  | c_name  | o_id     |
+-------+---------+----------+
|     1 | Grace   |        1 |   <- has order
|     1 | Grace   |        2 |   <- has order
|     2 | Henry   |        3 |   <- has order
|     3 | Ivy     |        4 |   <- has order
|     3 | Ivy     |        5 |   <- has order
|     4 | Jack    |     NULL |   <- NO order (NULL from LEFT JOIN)
+-------+---------+----------+

Step 2: WHERE o.order_id IS NULL (filter to unmatched)

+-------+---------+----------+
| c_id  | c_name  | o_id     |
+-------+---------+----------+
|     4 | Jack    |     NULL |   <- Only Jack remains
+-------+---------+----------+
```

### Pattern: Find Departments Without Employees

```sql
SELECT d.department_name,
       d.location
FROM departments d
LEFT JOIN employees e
    ON d.department_id = e.department_id
WHERE e.employee_id IS NULL;
```

**Result:**

```
+-----------------+------------+
| department_name | location   |
+-----------------+------------+
| HR              | Building D |
+-----------------+------------+
(1 row)
```

The HR department has no employees, so it shows up when we look for unmatched rows.

### Pattern: Find Employees Without a Department

```sql
SELECT e.first_name,
       e.last_name
FROM employees e
LEFT JOIN departments d
    ON e.department_id = d.department_id
WHERE d.department_id IS NULL;
```

**Result:**

```
+------------+-----------+
| first_name | last_name |
+------------+-----------+
| Frank      | Wilson    |
+------------+-----------+
(1 row)
```

---

## The Anti-Join Pattern Explained Visually

```
Full LEFT JOIN result:
+------------------+-------------------+
| Left table rows  | Right table match |
+------------------+-------------------+
| Row A            | Match found       |  <- WHERE right.id IS NOT NULL
| Row B            | Match found       |  <- WHERE right.id IS NOT NULL
| Row C            | NULL (no match)   |  <- WHERE right.id IS NULL <<<
| Row D            | Match found       |  <- WHERE right.id IS NOT NULL
| Row E            | NULL (no match)   |  <- WHERE right.id IS NULL <<<
+------------------+-------------------+

Anti-join (WHERE right.id IS NULL) returns ONLY:
+------------------+-------------------+
| Row C            | NULL (no match)   |
| Row E            | NULL (no match)   |
+------------------+-------------------+

These are the "orphaned" rows — left table rows with no match.
```

---

## LEFT JOIN with Multiple Tables

You can chain LEFT JOINs just like INNER JOINs.

```sql
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       o.order_id,
       p.product_name,
       o.quantity,
       o.order_date
FROM customers c
LEFT JOIN orders o   ON c.customer_id = o.customer_id
LEFT JOIN products p ON o.product_id  = p.product_id
ORDER BY c.last_name, o.order_date;
```

**Result:**

```
+----------------+----------+--------------+----------+------------+
| customer_name  | order_id | product_name | quantity | order_date |
+----------------+----------+--------------+----------+------------+
| Ivy Anderson   |        4 | Laptop       |        1 | 2024-03-10 |
| Ivy Anderson   |        5 | Monitor      |        1 | 2024-03-10 |
| Henry Martinez |        3 | Desk Chair   |        1 | 2024-02-20 |
| Grace Taylor   |        1 | Laptop       |        1 | 2024-01-15 |
| Grace Taylor   |        2 | Keyboard     |        2 | 2024-01-15 |
| Jack Thomas    |     NULL | NULL         |     NULL | NULL       |
+----------------+----------+--------------+----------+------------+
(6 rows)
```

Jack Thomas appears with NULLs for all order and product columns because he has no orders.

---

## Practical Example: Customer Activity Report

This report shows every customer with their order count and total spending, including customers who have not ordered anything.

```sql
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       c.email,
       COUNT(o.order_id) AS total_orders,
       COALESCE(SUM(o.quantity * p.price), 0) AS total_spent
FROM customers c
LEFT JOIN orders o   ON c.customer_id = o.customer_id
LEFT JOIN products p ON o.product_id  = p.product_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC;
```

**Result:**

```
+----------------+------------------+--------------+-------------+
| customer_name  | email            | total_orders | total_spent |
+----------------+------------------+--------------+-------------+
| Ivy Anderson   | ivy@email.com    |            2 |     1399.98 |
| Grace Taylor   | grace@email.com  |            2 |     1099.97 |
| Henry Martinez | henry@email.com  |            1 |      299.99 |
| Jack Thomas    | jack@email.com   |            0 |        0.00 |
+----------------+------------------+--------------+-------------+
(4 rows)
```

### Line-by-Line Explanation

```
SELECT c.first_name || ' ' || c.last_name   -- Combine into full name
           AS customer_name,
       c.email,                               -- Customer email
       COUNT(o.order_id) AS total_orders,     -- Count orders (NULL not counted)
       COALESCE(                              -- If the sum is NULL...
           SUM(o.quantity * p.price), 0       -- ...replace with 0
       ) AS total_spent
FROM customers c                              -- Start with ALL customers
LEFT JOIN orders o                            -- Match with orders
    ON c.customer_id = o.customer_id
LEFT JOIN products p                          -- Match with products
    ON o.product_id  = p.product_id
GROUP BY c.customer_id, c.first_name,         -- Group by customer
         c.last_name, c.email
ORDER BY total_spent DESC;                    -- Highest spenders first
```

**Key detail:** `COUNT(o.order_id)` counts only non-NULL values. Since Jack has no orders, his order_id is NULL and the count is 0. We use `COALESCE` to turn a NULL sum into 0.

---

## Practical Example: Department Staffing Overview

```sql
SELECT d.department_name,
       d.location,
       COUNT(e.employee_id) AS employee_count,
       COALESCE(ROUND(AVG(e.salary), 2), 0) AS avg_salary
FROM departments d
LEFT JOIN employees e
    ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name, d.location
ORDER BY employee_count DESC;
```

**Result:**

```
+-----------------+------------+----------------+------------+
| department_name | location   | employee_count | avg_salary |
+-----------------+------------+----------------+------------+
| Engineering     | Building A |              3 |   82333.33 |
| Marketing       | Building B |              1 |   65000.00 |
| Sales           | Building C |              1 |   78000.00 |
| HR              | Building D |              0 |       0.00 |
+-----------------+------------+----------------+------------+
(4 rows)
```

HR shows up with 0 employees and 0 average salary — exactly the kind of insight you need for staffing decisions.

---

## Common Mistakes

### Mistake 1: Using WHERE Instead of AND for Join Conditions

```sql
-- WRONG: This turns LEFT JOIN into INNER JOIN
SELECT c.first_name, o.order_id
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-02-01';
-- Jack disappears! His order_date is NULL, and NULL >= '2024-02-01' is not true.
```

**Fix:** If you want to filter the right table but keep all left rows, put the condition in the ON clause.

```sql
-- CORRECT: Jack still appears with NULLs
SELECT c.first_name, o.order_id, o.order_date
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
   AND o.order_date >= '2024-02-01';
```

This is one of the trickiest aspects of LEFT JOIN. Conditions in WHERE filter **after** the join, potentially eliminating rows that LEFT JOIN was supposed to keep. Conditions in ON filter **during** the join, keeping all left rows regardless.

### Mistake 2: Using = Instead of IS NULL to Check for NULLs

```sql
-- WRONG: This returns no rows
SELECT c.first_name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id = NULL;
-- NULL = NULL is not true! It evaluates to NULL.
```

**Fix:** Always use IS NULL.

```sql
-- CORRECT
SELECT c.first_name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

### Mistake 3: Checking the Wrong Column for IS NULL

```sql
-- WRONG: Checking a column that could legitimately be NULL
SELECT c.first_name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.quantity IS NULL;
-- This finds both unmatched rows AND rows where quantity happens to be NULL
```

**Fix:** Always check the primary key or a NOT NULL column from the right table.

```sql
-- CORRECT: Check the primary key
SELECT c.first_name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

---

## Best Practices

1. **Prefer LEFT JOIN over RIGHT JOIN.** Most developers exclusively use LEFT JOIN and put the "must keep all rows" table first (after FROM). This is a widely accepted convention.

2. **Use COALESCE for NULL values in aggregations.** When LEFT JOIN produces NULLs, use `COALESCE(value, default)` to replace them with meaningful defaults.

3. **Check the primary key for IS NULL in anti-joins.** When finding unmatched rows, check the right table's primary key (or any NOT NULL column) for IS NULL. This avoids false positives.

4. **Be careful with WHERE on LEFT JOINed tables.** A WHERE clause on the right table can accidentally turn your LEFT JOIN into an INNER JOIN. Put the condition in the ON clause if you want to preserve all left rows.

5. **Comment your intent.** Add a comment like `-- Find customers WITHOUT orders` so future readers understand why you are using the anti-join pattern.

---

## Quick Summary

| Concept | Description |
|---------|-------------|
| LEFT JOIN | All rows from left table, matching from right, NULLs for no match |
| RIGHT JOIN | All rows from right table, matching from left, NULLs for no match |
| Anti-join | LEFT JOIN + WHERE right.pk IS NULL to find unmatched rows |
| LEFT vs RIGHT | Interchangeable — just swap table order |
| WHERE vs ON | WHERE filters after join (can remove NULLs); ON filters during join |
| COALESCE | Replaces NULL with a default value |

---

## Key Points

- LEFT JOIN keeps **all rows** from the left table, even if there is no match in the right table.
- Non-matching rows get **NULL** for every column from the right table.
- The **anti-join pattern** (LEFT JOIN + WHERE IS NULL) is a powerful way to find orphaned or missing data.
- RIGHT JOIN is the mirror of LEFT JOIN. In practice, use LEFT JOIN and swap table order instead.
- Be careful with WHERE clauses on the right table — they can accidentally turn a LEFT JOIN into an INNER JOIN.
- Use **COALESCE** to replace NULLs with default values in your results.
- Always check the **primary key** (or a NOT NULL column) when using the IS NULL anti-join pattern.

---

## Practice Questions

**Question 1:** What is the difference between INNER JOIN and LEFT JOIN?

<details>
<summary>Answer</summary>

INNER JOIN returns only rows that have matches in **both** tables. LEFT JOIN returns **all** rows from the left table, plus matching rows from the right table. If there is no match, the right table's columns are filled with NULL.

</details>

**Question 2:** Why does this query not find customers without orders?

```sql
SELECT c.first_name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id = NULL;
```

<details>
<summary>Answer</summary>

Because you cannot compare with NULL using `=`. The expression `NULL = NULL` evaluates to NULL (not true), so no rows are returned. You must use `WHERE o.order_id IS NULL` instead.

</details>

**Question 3:** How can you rewrite a RIGHT JOIN as a LEFT JOIN?

<details>
<summary>Answer</summary>

Swap the table order. `A RIGHT JOIN B ON ...` is the same as `B LEFT JOIN A ON ...`. Most developers prefer LEFT JOIN and adjust which table comes first.

</details>

**Question 4:** Why might a WHERE clause on the right table be problematic with LEFT JOIN?

<details>
<summary>Answer</summary>

A WHERE clause filters results **after** the join. If the right table's columns are NULL (for non-matching rows), the WHERE condition will filter them out, effectively turning the LEFT JOIN into an INNER JOIN. To avoid this, put the condition in the ON clause instead.

</details>

**Question 5:** What is the anti-join pattern and when would you use it?

<details>
<summary>Answer</summary>

The anti-join pattern is: LEFT JOIN followed by WHERE right_table.primary_key IS NULL. It finds rows in the left table that have **no match** in the right table. Use it to find missing relationships: customers without orders, departments without employees, products never sold, etc.

</details>

---

## Exercises

### Exercise 1: Products Never Ordered

Write a query to find all products that have never been ordered. Show the product name, price, and category.

<details>
<summary>Solution</summary>

```sql
SELECT p.product_name,
       p.price,
       p.category
FROM products p
LEFT JOIN orders o
    ON p.product_id = o.product_id
WHERE o.order_id IS NULL;
```

Expected output (no products are missing in our sample data, so let us verify):

```
+--------------+-------+----------+
| product_name | price | category |
+--------------+-------+----------+
(0 rows)
```

All products have been ordered in our sample data. If we had a product with no orders, it would appear here.

</details>

### Exercise 2: Complete Employee Directory

Write a query that shows ALL employees (including those without a department) and ALL departments (including those without employees). Use two separate queries — one LEFT JOIN for all employees and one LEFT JOIN for all departments.

<details>
<summary>Solution</summary>

```sql
-- All employees with their departments (including Frank with no department)
SELECT e.first_name || ' ' || e.last_name AS employee_name,
       COALESCE(d.department_name, 'Unassigned') AS department
FROM employees e
LEFT JOIN departments d
    ON e.department_id = d.department_id
ORDER BY e.last_name;

-- All departments with employee count (including HR with 0)
SELECT d.department_name,
       COUNT(e.employee_id) AS employee_count
FROM departments d
LEFT JOIN employees e
    ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name
ORDER BY d.department_name;
```

Expected output for first query:

```
+---------------+-------------+
| employee_name | department  |
+---------------+-------------+
| Charlie Brown | Marketing   |
| Eve Davis     | Engineering |
| Alice Johnson | Engineering |
| Diana Lee     | Sales       |
| Bob Smith     | Engineering |
| Frank Wilson  | Unassigned  |
+---------------+-------------+
```

Expected output for second query:

```
+-----------------+----------------+
| department_name | employee_count |
+-----------------+----------------+
| Engineering     |              3 |
| HR              |              0 |
| Marketing       |              1 |
| Sales           |              1 |
+-----------------+----------------+
```

</details>

### Exercise 3: Customer Order Gaps

Write a query that identifies customers who have NOT placed any orders in 2024. Show their name and email. (Hint: You need to check if the customer has no orders at all OR no orders in 2024.)

<details>
<summary>Solution</summary>

```sql
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       c.email
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
   AND o.order_date >= '2024-01-01'
   AND o.order_date < '2025-01-01'
WHERE o.order_id IS NULL;
```

Expected output:

```
+---------------+------------------+
| customer_name | email            |
+---------------+------------------+
| Jack Thomas   | jack@email.com   |
+---------------+------------------+
```

Note: The date filter is in the ON clause, not the WHERE clause. This ensures that customers without any orders still appear. If we put it in WHERE, it would turn into an INNER JOIN.

</details>

---

## What Is Next?

You now know how to use INNER JOIN (matching rows only) and LEFT/RIGHT JOIN (keep all rows from one side). But what if you want to keep all rows from **both** sides? Or combine every row with every other row? Or join a table to itself?

In the next chapter, you will learn about **FULL OUTER JOIN**, **CROSS JOIN**, and **SELF JOIN** — three specialized join types that handle these less common but important scenarios.
