# Chapter 16: Subqueries — Queries Inside Queries

## What You Will Learn

- What a subquery is and how it works
- How to use subqueries in the WHERE clause (filtering with dynamic values)
- How to use subqueries in the FROM clause (derived tables)
- How to use subqueries in the SELECT clause (scalar subqueries)
- How correlated subqueries work (referencing the outer query)
- How to use EXISTS and NOT EXISTS
- How to use IN with subqueries
- When to use subqueries vs JOINs

## Why This Chapter Matters

Imagine you are asked: "Show me all employees who earn more than the average salary." You know how to calculate the average salary. You know how to filter with WHERE. But how do you combine these into one query?

That is exactly what subqueries do. A subquery is a query nested inside another query. Think of it like a Russian nesting doll — a small query lives inside a bigger query, and the bigger query uses the result of the smaller one.

Subqueries let you solve problems that are too complex for a single simple query. They are one of the most powerful tools in SQL, and once you understand them, you can break down almost any complex question into manageable pieces.

---

## What Is a Subquery?

A subquery is a SELECT statement written inside parentheses, placed within another SQL statement. The inner query runs first, and its result is used by the outer query.

```sql
SELECT column
FROM table
WHERE column = (SELECT something FROM another_table);
--              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
--              This is the subquery (inner query)
```

Think of it like asking a question in two steps:

1. "What is the average salary?" (inner query)
2. "Show me employees who earn more than that number." (outer query)

Instead of running two queries manually, you nest the first inside the second.

---

## Subquery in WHERE — Filtering with Dynamic Values

The most common use of subqueries is in the WHERE clause. The subquery calculates a value, and the outer query uses it for filtering.

### Employees Earning Above Average

```sql
SELECT first_name,
       last_name,
       salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

**Result:**

```
+------------+-----------+----------+
| first_name | last_name | salary   |
+------------+-----------+----------+
| Alice      | Johnson   | 85000.00 |
| Diana      | Lee       | 78000.00 |
| Eve        | Davis     | 90000.00 |
+------------+-----------+----------+
(3 rows)
```

### Line-by-Line Explanation

```
SELECT first_name,                         -- Columns to display
       last_name,
       salary
FROM employees                             -- From the employees table
WHERE salary > (                           -- Filter: salary must be greater than...
    SELECT AVG(salary) FROM employees      -- ...the average salary (75000)
);
```

**How it works step by step:**

```
Step 1: Inner query runs first
SELECT AVG(salary) FROM employees
Result: 75000.00

Step 2: Outer query uses that result
SELECT first_name, last_name, salary
FROM employees
WHERE salary > 75000.00
```

The inner query is replaced by its result, and then the outer query runs as a normal query.

### The Subquery Must Return the Right Shape

When using `=`, `>`, `<`, etc., the subquery must return **exactly one value** (one row, one column). This is called a **scalar subquery**.

```sql
-- CORRECT: Returns one value
WHERE salary > (SELECT AVG(salary) FROM employees)

-- CORRECT: Returns one value
WHERE salary = (SELECT MAX(salary) FROM employees)

-- WRONG: Returns multiple values — use IN instead
WHERE salary = (SELECT salary FROM employees WHERE department_id = 1)
-- ERROR: more than one row returned by a subquery used as an expression
```

---

## IN with Subqueries — Matching Against a List

When a subquery returns multiple rows (but one column), use `IN` instead of `=`.

### Find Employees in Departments Located in Building A

```sql
SELECT first_name,
       last_name
FROM employees
WHERE department_id IN (
    SELECT department_id
    FROM departments
    WHERE location = 'Building A'
);
```

**Result:**

```
+------------+-----------+
| first_name | last_name |
+------------+-----------+
| Alice      | Johnson   |
| Bob        | Smith     |
| Eve        | Davis     |
+------------+-----------+
(3 rows)
```

### Line-by-Line Explanation

```
SELECT first_name, last_name          -- Columns to show
FROM employees                        -- From employees table
WHERE department_id IN (              -- department_id must be in the list...
    SELECT department_id              -- ...of department IDs
    FROM departments                  -- ...from departments table
    WHERE location = 'Building A'    -- ...that are in Building A
);
```

**Step by step:**

```
Step 1: Inner query
SELECT department_id FROM departments WHERE location = 'Building A'
Result: (1)    -- Only Engineering is in Building A

Step 2: Outer query
SELECT first_name, last_name FROM employees
WHERE department_id IN (1)
```

You can also use `NOT IN` to find the opposite — employees NOT in those departments.

```sql
SELECT first_name, last_name
FROM employees
WHERE department_id NOT IN (
    SELECT department_id
    FROM departments
    WHERE location = 'Building A'
);
```

**Result:**

```
+------------+-----------+
| first_name | last_name |
+------------+-----------+
| Charlie    | Brown     |
| Diana      | Lee       |
+------------+-----------+
(2 rows)
```

> **Warning about NOT IN and NULLs:** If the subquery returns any NULL values, `NOT IN` will return no rows at all! This is because `value NOT IN (1, 2, NULL)` is equivalent to `value != 1 AND value != 2 AND value != NULL`, and comparing anything to NULL yields NULL (not true). Use `NOT EXISTS` instead when NULLs are possible.

---

## Subquery in FROM — Derived Tables

You can use a subquery in the FROM clause to create a temporary table (called a **derived table**) that the outer query can select from.

### Department Salary Statistics

```sql
SELECT dept_stats.department_name,
       dept_stats.emp_count,
       dept_stats.avg_salary
FROM (
    SELECT d.department_name,
           COUNT(e.employee_id) AS emp_count,
           ROUND(AVG(e.salary), 2) AS avg_salary
    FROM departments d
    INNER JOIN employees e
        ON d.department_id = e.department_id
    GROUP BY d.department_name
) AS dept_stats
WHERE dept_stats.avg_salary > 70000;
```

**Result:**

```
+-----------------+-----------+------------+
| department_name | emp_count | avg_salary |
+-----------------+-----------+------------+
| Engineering     |         3 |   82333.33 |
| Sales           |         1 |   78000.00 |
+-----------------+-----------+------------+
(2 rows)
```

### Line-by-Line Explanation

```
SELECT dept_stats.department_name,     -- Columns from the derived table
       dept_stats.emp_count,
       dept_stats.avg_salary
FROM (                                 -- Start of subquery (derived table)
    SELECT d.department_name,          -- Department name
           COUNT(e.employee_id)        -- Count employees
               AS emp_count,
           ROUND(AVG(e.salary), 2)     -- Average salary, rounded
               AS avg_salary
    FROM departments d
    INNER JOIN employees e
        ON d.department_id = e.department_id
    GROUP BY d.department_name
) AS dept_stats                        -- Give the derived table an alias
WHERE dept_stats.avg_salary > 70000;   -- Filter using derived table columns
```

**The derived table is like a virtual table:**

```
Step 1: Inner query produces a "table"

dept_stats:
+-----------------+-----------+------------+
| department_name | emp_count | avg_salary |
+-----------------+-----------+------------+
| Engineering     |         3 |   82333.33 |
| Marketing       |         1 |   65000.00 |
| Sales           |         1 |   78000.00 |
+-----------------+-----------+------------+

Step 2: Outer query filters this "table"
WHERE avg_salary > 70000
```

> **Note:** A derived table MUST have an alias. You cannot write `FROM (SELECT ...) WHERE ...` — you must write `FROM (SELECT ...) AS some_name WHERE ...`.

---

## Subquery in SELECT — Scalar Subqueries

You can place a subquery in the SELECT clause to add a calculated column. The subquery must return exactly one value (scalar).

### Employees with Company Average for Comparison

```sql
SELECT first_name,
       last_name,
       salary,
       (SELECT ROUND(AVG(salary), 2) FROM employees) AS company_avg,
       salary - (SELECT ROUND(AVG(salary), 2) FROM employees) AS diff_from_avg
FROM employees
WHERE department_id IS NOT NULL
ORDER BY salary DESC;
```

**Result:**

```
+------------+-----------+----------+-------------+---------------+
| first_name | last_name | salary   | company_avg | diff_from_avg |
+------------+-----------+----------+-------------+---------------+
| Eve        | Davis     | 90000.00 |    75000.00 |      15000.00 |
| Alice      | Johnson   | 85000.00 |    75000.00 |      10000.00 |
| Diana      | Lee       | 78000.00 |    75000.00 |       3000.00 |
| Bob        | Smith     | 72000.00 |    75000.00 |      -3000.00 |
| Charlie    | Brown     | 65000.00 |    75000.00 |     -10000.00 |
+------------+-----------+----------+-------------+---------------+
(5 rows)
```

The scalar subquery `(SELECT ROUND(AVG(salary), 2) FROM employees)` runs once and returns the same value for every row. Each employee's row now shows how their salary compares to the company average.

---

## Correlated Subqueries — Referencing the Outer Query

A **correlated subquery** is different from a regular subquery. It references a column from the outer query, which means it runs **once for each row** in the outer query.

### Employees Who Earn More Than Their Department's Average

```sql
SELECT e.first_name,
       e.last_name,
       e.salary,
       e.department_id
FROM employees e
WHERE e.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e.department_id
);
```

**Result:**

```
+------------+-----------+----------+---------------+
| first_name | last_name | salary   | department_id |
+------------+-----------+----------+---------------+
| Alice      | Johnson   | 85000.00 |             1 |
| Eve        | Davis     | 90000.00 |             1 |
+------------+-----------+----------+---------------+
(2 rows)
```

### Line-by-Line Explanation

```
SELECT e.first_name,                     -- Employee info
       e.last_name,
       e.salary,
       e.department_id
FROM employees e                         -- Outer query: each employee
WHERE e.salary > (                       -- Salary must exceed...
    SELECT AVG(e2.salary)                -- ...the average salary
    FROM employees e2                    -- ...of employees
    WHERE e2.department_id               -- ...in the SAME department
        = e.department_id                -- (references outer query!)
);
```

**How it works — step by step for each row:**

```
For Alice (dept 1, salary 85000):
  Inner query: AVG salary where dept = 1 → (85000+72000+90000)/3 = 82333
  85000 > 82333? YES → include Alice

For Bob (dept 1, salary 72000):
  Inner query: AVG salary where dept = 1 → 82333
  72000 > 82333? NO → exclude Bob

For Charlie (dept 2, salary 65000):
  Inner query: AVG salary where dept = 2 → 65000
  65000 > 65000? NO → exclude Charlie (not greater than, equal to)

For Diana (dept 3, salary 78000):
  Inner query: AVG salary where dept = 3 → 78000
  78000 > 78000? NO → exclude Diana

For Eve (dept 1, salary 90000):
  Inner query: AVG salary where dept = 1 → 82333
  90000 > 82333? YES → include Eve
```

The key difference: `e.department_id` in the inner query comes from the **outer** query. This link makes the subquery "correlated" — it depends on the current row of the outer query.

---

## EXISTS and NOT EXISTS

`EXISTS` checks whether a subquery returns **any rows at all**. It does not care about the actual values — only whether the result set is empty or not.

### Find Customers Who Have Placed At Least One Order

```sql
SELECT c.first_name,
       c.last_name
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
);
```

**Result:**

```
+------------+-----------+
| first_name | last_name |
+------------+-----------+
| Grace      | Taylor    |
| Henry      | Martinez  |
| Ivy        | Anderson  |
+------------+-----------+
(3 rows)
```

### Line-by-Line Explanation

```
SELECT c.first_name,                -- Customer info
       c.last_name
FROM customers c                    -- For each customer...
WHERE EXISTS (                      -- ...check if there exists...
    SELECT 1                        -- ...any row at all (1 is arbitrary)
    FROM orders o                   -- ...in the orders table
    WHERE o.customer_id             -- ...where the customer_id
        = c.customer_id             -- ...matches this customer
);
```

> **Note:** `SELECT 1` is conventional in EXISTS subqueries. Since EXISTS only checks if rows exist (not what they contain), the actual selected value does not matter. `SELECT *`, `SELECT 42`, or `SELECT 'hello'` would all work the same way.

### Find Customers Who Have NEVER Placed an Order

```sql
SELECT c.first_name,
       c.last_name,
       c.email
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
);
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

`NOT EXISTS` is the opposite — it returns rows from the outer query where the subquery finds **no matches**. This is similar to the anti-join pattern (LEFT JOIN + IS NULL) from Chapter 14.

### EXISTS vs IN — Which to Use?

Both can accomplish similar tasks:

```sql
-- Using IN
SELECT first_name FROM customers
WHERE customer_id IN (SELECT customer_id FROM orders);

-- Using EXISTS
SELECT first_name FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
```

Key differences:

| Feature | IN | EXISTS |
|---------|------|--------|
| NULL handling | NOT IN fails with NULLs | NOT EXISTS handles NULLs correctly |
| Performance | Good for small subquery results | Good for large tables with indexes |
| Readability | Simpler for simple cases | Better for complex conditions |

**Rule of thumb:** Use `NOT EXISTS` instead of `NOT IN` when the subquery might return NULLs. For other cases, choose whichever is more readable.

---

## Subquery vs JOIN — When to Use Each

Many subqueries can be rewritten as JOINs, and vice versa. Here are the same problem solved both ways.

### Problem: Find Employees in the Engineering Department

**Using a subquery:**

```sql
SELECT first_name, last_name
FROM employees
WHERE department_id = (
    SELECT department_id
    FROM departments
    WHERE department_name = 'Engineering'
);
```

**Using a JOIN:**

```sql
SELECT e.first_name, e.last_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id
WHERE d.department_name = 'Engineering';
```

Both return the same result. So when should you use which?

### When to Use Subqueries

```
+------------------------------------------------+
| USE A SUBQUERY WHEN:                           |
+------------------------------------------------+
| 1. You need a single value for comparison      |
|    WHERE salary > (SELECT AVG(salary) ...)     |
|                                                |
| 2. You need to check existence                 |
|    WHERE EXISTS (SELECT ...)                   |
|                                                |
| 3. The logic is step-by-step                   |
|    "First find X, then use X to find Y"        |
|                                                |
| 4. You do NOT need columns from the subquery   |
|    in your final result                        |
+------------------------------------------------+
```

### When to Use JOINs

```
+------------------------------------------------+
| USE A JOIN WHEN:                               |
+------------------------------------------------+
| 1. You need columns from BOTH tables           |
|    SELECT e.name, d.department_name            |
|                                                |
| 2. You need to combine multiple tables         |
|    Three or more tables are easier with JOINs  |
|                                                |
| 3. Performance matters on large tables          |
|    JOINs are often faster than correlated      |
|    subqueries                                  |
|                                                |
| 4. You want aggregations across joined data    |
|    GROUP BY with joined tables                 |
+------------------------------------------------+
```

### Quick Comparison

| Aspect | Subquery | JOIN |
|--------|----------|------|
| Readability | Step-by-step logic | All at once |
| Columns from inner table | Not available (unless in FROM) | Available |
| Performance | Correlated can be slow | Usually optimized well |
| NULL safety | EXISTS handles NULLs | LEFT JOIN handles NULLs |
| Aggregation comparison | Natural (WHERE > AVG) | Requires derived table |

---

## Practical Example: Complete Order Analysis

Let us combine several subquery techniques in one practical scenario.

```sql
-- Find orders where the total exceeds the average order total
SELECT o.order_id,
       c.first_name || ' ' || c.last_name AS customer,
       p.product_name,
       (o.quantity * p.price) AS order_total
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN products p  ON o.product_id  = p.product_id
WHERE (o.quantity * p.price) > (
    SELECT AVG(o2.quantity * p2.price)
    FROM orders o2
    INNER JOIN products p2 ON o2.product_id = p2.product_id
)
ORDER BY order_total DESC;
```

**Result:**

```
+----------+----------------+--------------+-------------+
| order_id | customer       | product_name | order_total |
+----------+----------------+--------------+-------------+
|        1 | Grace Taylor   | Laptop       |      999.99 |
|        4 | Ivy Anderson   | Laptop       |      999.99 |
|        5 | Ivy Anderson   | Monitor      |      399.99 |
+----------+----------------+--------------+-------------+
(3 rows)
```

The average order total is about 559.99. Only orders exceeding that amount appear.

---

## Nesting Subqueries

You can nest subqueries inside other subqueries, but keep it reasonable. Deeply nested subqueries become hard to read.

```sql
-- Find employees in departments that have above-average employee counts
SELECT first_name, last_name
FROM employees
WHERE department_id IN (
    SELECT department_id
    FROM employees
    WHERE department_id IS NOT NULL
    GROUP BY department_id
    HAVING COUNT(*) > (
        SELECT AVG(dept_count)
        FROM (
            SELECT COUNT(*) AS dept_count
            FROM employees
            WHERE department_id IS NOT NULL
            GROUP BY department_id
        ) AS counts
    )
);
```

**Result:**

```
+------------+-----------+
| first_name | last_name |
+------------+-----------+
| Alice      | Johnson   |
| Bob        | Smith     |
| Eve        | Davis     |
+------------+-----------+
(3 rows)
```

These are the Engineering department employees. Engineering has 3 employees, which is above the average department size of about 1.67.

> **Tip:** If your subqueries are nested more than 2-3 levels deep, consider using CTEs (Common Table Expressions) instead, which you will learn in a later chapter. CTEs make complex queries much more readable.

---

## Common Mistakes

### Mistake 1: Subquery Returns Multiple Rows with = Operator

```sql
-- WRONG: Subquery returns multiple values
SELECT first_name FROM employees
WHERE department_id = (SELECT department_id FROM departments);
-- ERROR: more than one row returned by a subquery
```

**Fix:** Use `IN` for multiple values, or add a filter to return one value.

```sql
-- CORRECT: Use IN for multiple values
SELECT first_name FROM employees
WHERE department_id IN (SELECT department_id FROM departments);
```

### Mistake 2: Forgetting the Alias for Derived Tables

```sql
-- WRONG: No alias for the subquery in FROM
SELECT * FROM (SELECT department_id, COUNT(*) FROM employees GROUP BY department_id);
-- ERROR: subquery in FROM must have an alias
```

**Fix:** Always give derived tables an alias.

```sql
-- CORRECT
SELECT * FROM (
    SELECT department_id, COUNT(*) AS emp_count
    FROM employees
    GROUP BY department_id
) AS dept_counts;
```

### Mistake 3: NOT IN with NULLs

```sql
-- WRONG: If the subquery returns any NULLs, NO rows are returned
SELECT first_name FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM orders);
-- Works only if customer_id in orders is never NULL
```

**Fix:** Use NOT EXISTS, which handles NULLs correctly.

```sql
-- CORRECT: NOT EXISTS handles NULLs safely
SELECT c.first_name FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
);
```

### Mistake 4: Using Correlated Subqueries When a Join Would Be Faster

```sql
-- SLOW: Correlated subquery runs once per row
SELECT e.first_name,
       (SELECT d.department_name FROM departments d
        WHERE d.department_id = e.department_id) AS dept
FROM employees e;

-- FASTER: Simple JOIN
SELECT e.first_name, d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id;
```

**Fix:** When you need columns from another table, use a JOIN instead of a correlated scalar subquery.

---

## Best Practices

1. **Start simple.** Write and test the inner query by itself before nesting it. Make sure it returns the right shape (one value, one column, or a table).

2. **Use EXISTS/NOT EXISTS over IN/NOT IN** when NULLs are possible. EXISTS handles NULLs correctly and often performs better on large tables.

3. **Prefer JOINs when you need columns from both tables.** Subqueries in WHERE are great for filtering, but if you need data from the subquery table in your results, a JOIN is cleaner.

4. **Limit nesting depth.** If you have more than 2-3 levels of nesting, refactor using CTEs (covered in a later chapter).

5. **Always alias derived tables.** PostgreSQL requires it, and it makes your code self-documenting.

6. **Test correlated subqueries carefully.** They run once per outer row, which can be slow on large tables. Check performance and consider JOINs as an alternative.

---

## Quick Summary

| Concept | Description |
|---------|-------------|
| Subquery in WHERE | Filter using a dynamically calculated value |
| Subquery in FROM | Create a temporary "derived table" |
| Subquery in SELECT | Add a calculated column (must be scalar) |
| Correlated subquery | References the outer query; runs per row |
| EXISTS / NOT EXISTS | Checks if any rows exist (or do not) |
| IN with subquery | Matches against a list of values from a subquery |
| Scalar subquery | Returns exactly one row and one column |

---

## Key Points

- A **subquery** is a query nested inside another query, enclosed in parentheses.
- Subqueries in WHERE are used for **dynamic filtering** (e.g., above average, in a specific set).
- Subqueries in FROM create **derived tables** that must have an alias.
- Subqueries in SELECT add **scalar calculated columns** (one value per row).
- **Correlated subqueries** reference the outer query and run once per outer row. They can be slow on large data sets.
- **EXISTS** checks for row existence. **NOT EXISTS** is safer than NOT IN when NULLs are involved.
- **JOINs** are preferred when you need columns from both tables or need better performance. Subqueries are preferred for step-by-step logic and aggregate comparisons.

---

## Practice Questions

**Question 1:** What is the difference between a regular subquery and a correlated subquery?

<details>
<summary>Answer</summary>

A regular subquery runs **once** and its result is used by the outer query. A correlated subquery references a column from the outer query, so it runs **once for each row** in the outer query. Correlated subqueries are more flexible but can be slower.

</details>

**Question 2:** Why is `NOT IN` dangerous when the subquery might return NULL values?

<details>
<summary>Answer</summary>

If the subquery returns any NULL values, `NOT IN` returns no rows at all. This is because `value != NULL` evaluates to NULL (not true or false), and `NOT IN` requires all comparisons to be true. Use `NOT EXISTS` instead, which handles NULLs correctly.

</details>

**Question 3:** When would you use a subquery in the FROM clause instead of a regular query?

<details>
<summary>Answer</summary>

Use a subquery in FROM (derived table) when you need to filter on aggregated values that you cannot use directly in WHERE (because WHERE runs before GROUP BY). For example, finding departments where the average salary exceeds a threshold. The inner query groups and aggregates, the outer query filters.

</details>

**Question 4:** Write a query to find the product with the highest price using a subquery.

<details>
<summary>Answer</summary>

```sql
SELECT product_name, price
FROM products
WHERE price = (SELECT MAX(price) FROM products);
```

</details>

**Question 5:** Can you always replace a subquery with a JOIN?

<details>
<summary>Answer</summary>

Not always. Subqueries that calculate aggregate values for comparison (like "above average") do not have a direct JOIN equivalent. You would need a JOIN with a derived table or CTE. However, many subqueries (especially IN subqueries and correlated subqueries that fetch columns) can be rewritten as JOINs.

</details>

---

## Exercises

### Exercise 1: Above-Average Products

Write a query that shows all products whose price is above the average product price. Display the product name, price, and how much above the average they are.

<details>
<summary>Solution</summary>

```sql
SELECT product_name,
       price,
       price - (SELECT ROUND(AVG(price), 2) FROM products) AS above_avg_by
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC;
```

Expected output:

```
+--------------+--------+-------------+
| product_name | price  | above_avg_by|
+--------------+--------+-------------+
| Laptop       | 999.99 |      562.50 |
| Monitor      | 399.99 |      -37.50 |
+--------------+--------+-------------+
```

(Average price is 437.49)

</details>

### Exercise 2: Customers with Multiple Orders

Write a query using EXISTS to find customers who have placed more than one order. Show their name and email.

<details>
<summary>Solution</summary>

```sql
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       c.email
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
    GROUP BY o.customer_id
    HAVING COUNT(*) > 1
);
```

Expected output:

```
+----------------+------------------+
| customer_name  | email            |
+----------------+------------------+
| Grace Taylor   | grace@email.com  |
| Ivy Anderson   | ivy@email.com    |
+----------------+------------------+
```

Alternative approach using IN:

```sql
SELECT first_name || ' ' || last_name AS customer_name, email
FROM customers
WHERE customer_id IN (
    SELECT customer_id
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(*) > 1
);
```

</details>

### Exercise 3: Department Salary Comparison

Write a query that shows each employee, their salary, their department's average salary, and whether they earn above or below the department average. Use a correlated subquery.

<details>
<summary>Solution</summary>

```sql
SELECT e.first_name,
       e.last_name,
       e.salary,
       (SELECT ROUND(AVG(e2.salary), 2)
        FROM employees e2
        WHERE e2.department_id = e.department_id) AS dept_avg,
       CASE
           WHEN e.salary > (SELECT AVG(e2.salary)
                            FROM employees e2
                            WHERE e2.department_id = e.department_id)
               THEN 'Above average'
           WHEN e.salary < (SELECT AVG(e2.salary)
                            FROM employees e2
                            WHERE e2.department_id = e.department_id)
               THEN 'Below average'
           ELSE 'At average'
       END AS comparison
FROM employees e
WHERE e.department_id IS NOT NULL
ORDER BY e.department_id, e.salary DESC;
```

Expected output:

```
+------------+-----------+----------+----------+---------------+
| first_name | last_name | salary   | dept_avg | comparison    |
+------------+-----------+----------+----------+---------------+
| Eve        | Davis     | 90000.00 | 82333.33 | Above average |
| Alice      | Johnson   | 85000.00 | 82333.33 | Above average |
| Bob        | Smith     | 72000.00 | 82333.33 | Below average |
| Charlie    | Brown     | 65000.00 | 65000.00 | At average    |
| Diana      | Lee       | 78000.00 | 78000.00 | At average    |
+------------+-----------+----------+----------+---------------+
```

</details>

---

## What Is Next?

Now that you can nest queries inside other queries, the next chapter introduces another way to combine results from multiple queries: **set operations**. UNION, INTERSECT, and EXCEPT let you combine, find common elements, or subtract the results of two or more queries. Think of them as mathematical operations for result sets.
