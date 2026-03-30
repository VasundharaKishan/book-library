# Chapter 27: Common Table Expressions and Recursive Queries

## What You Will Learn

In this chapter, you will learn:

- What Common Table Expressions (CTEs) are and why they exist
- How to use the WITH clause to create named temporary results
- How to chain multiple CTEs together
- How CTEs compare to subqueries and views
- What recursive CTEs are and how they work
- How to traverse hierarchies like organizational charts and category trees
- How to generate number and date series with recursion

## Why This Chapter Matters

Imagine you are writing a recipe. You could write it as one enormous paragraph: "Take the flour that you sifted and mixed with the baking powder that you measured from the container and combine it with the eggs that you cracked and whisked with the sugar that you measured..." That is unreadable.

Or you could break it into steps:
1. Sift the dry ingredients
2. Whisk the wet ingredients
3. Combine wet and dry ingredients

CTEs are the SQL equivalent of numbered recipe steps. Instead of nesting subqueries five levels deep, you break the query into named steps that are easy to read, debug, and maintain.

Recursive CTEs go even further. They let you answer questions that regular SQL cannot: "Who reports to whom in the entire company hierarchy?" or "What is the full path from a top-level category down to a subcategory?" These are problems that require traversing tree structures, and recursive CTEs handle them elegantly.

---

## Setting Up Our Practice Tables

```sql
CREATE TABLE employees (
    employee_id  SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    manager_id   INT REFERENCES employees(employee_id),
    department   VARCHAR(50) NOT NULL,
    salary       DECIMAL(10, 2) NOT NULL
);

INSERT INTO employees (employee_id, name, manager_id, department, salary) VALUES
(1, 'Sarah CEO',       NULL, 'Executive',   200000),
(2, 'Tom VP Eng',      1,    'Engineering', 150000),
(3, 'Lisa VP Sales',   1,    'Sales',       145000),
(4, 'Mike Director',   2,    'Engineering', 120000),
(5, 'Anna Director',   2,    'Engineering', 118000),
(6, 'Jake Manager',    4,    'Engineering',  95000),
(7, 'Emma Manager',    4,    'Engineering',  92000),
(8, 'Chris Developer', 6,    'Engineering',  85000),
(9, 'Pat Developer',   6,    'Engineering',  82000),
(10,'Sam Sales Rep',   3,    'Sales',        70000),
(11,'Kim Sales Rep',   3,    'Sales',        72000);

CREATE TABLE categories (
    category_id   SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_id     INT REFERENCES categories(category_id)
);

INSERT INTO categories (category_id, category_name, parent_id) VALUES
(1, 'Electronics',     NULL),
(2, 'Computers',       1),
(3, 'Phones',          1),
(4, 'Laptops',         2),
(5, 'Desktops',        2),
(6, 'Smartphones',     3),
(7, 'Feature Phones',  3),
(8, 'Gaming Laptops',  4),
(9, 'Business Laptops',4),
(10,'Clothing',        NULL),
(11,'Men',             10),
(12,'Women',           10),
(13,'Shirts',          11),
(14,'Pants',           11);

CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date  DATE NOT NULL,
    total       DECIMAL(10, 2) NOT NULL
);

INSERT INTO orders (customer_id, order_date, total) VALUES
(1, '2024-01-15', 250.00),
(2, '2024-01-20', 150.00),
(1, '2024-02-10', 300.00),
(3, '2024-02-15', 450.00),
(2, '2024-03-01', 200.00),
(1, '2024-03-15', 175.00),
(3, '2024-03-20', 500.00),
(4, '2024-04-01', 350.00);
```

---

## What Is a CTE?

A Common Table Expression (CTE) is a named temporary result set that you define at the beginning of a query. It exists only for the duration of that single query.

### Basic Syntax

```sql
WITH cte_name AS (
    SELECT ...
)
SELECT ...
FROM cte_name;
```

Think of it as saying: "First, calculate this result and call it `cte_name`. Then, use `cte_name` in the main query."

### Your First CTE

Let us find employees who earn more than the average salary:

```sql
WITH avg_salary AS (
    SELECT AVG(salary) AS average
    FROM employees
)
SELECT
    e.name,
    e.department,
    e.salary,
    a.average,
    e.salary - a.average AS above_average
FROM employees e
CROSS JOIN avg_salary a
WHERE e.salary > a.average
ORDER BY e.salary DESC;
```

```
     name      | department  |  salary   |   average    | above_average
---------------+-------------+-----------+--------------+--------------
 Sarah CEO     | Executive   | 200000.00 | 111727.27    |     88272.73
 Tom VP Eng    | Engineering | 150000.00 | 111727.27    |     38272.73
 Lisa VP Sales | Sales       | 145000.00 | 111727.27    |     33272.73
 Mike Director | Engineering | 120000.00 | 111727.27    |      8272.73
 Anna Director | Engineering | 118000.00 | 111727.27    |      6272.73
(5 rows)
```

**Line-by-line explanation:**
- `WITH avg_salary AS (...)` — define a CTE named `avg_salary` that calculates the average
- The CTE produces a single row with a single column called `average`
- `CROSS JOIN avg_salary a` — join every employee row with the average value
- `WHERE e.salary > a.average` — filter to only above-average earners

---

## Why Use CTEs Instead of Subqueries?

### The Subquery Version (Harder to Read)

```sql
SELECT
    e.name,
    e.department,
    e.salary,
    (SELECT AVG(salary) FROM employees) AS average,
    e.salary - (SELECT AVG(salary) FROM employees) AS above_average
FROM employees e
WHERE e.salary > (SELECT AVG(salary) FROM employees)
ORDER BY e.salary DESC;
```

The subquery `(SELECT AVG(salary) FROM employees)` is repeated three times. With a CTE, you calculate it once and reference it by name.

### Side-by-Side Comparison

```
Nested Subqueries:                 CTEs:
+---------------------------+      +---------------------------+
| SELECT ...                |      | WITH                      |
|   FROM (                  |      |   step1 AS (SELECT ...),  |
|     SELECT ...            |      |   step2 AS (SELECT ...),  |
|       FROM (              |      |   step3 AS (SELECT ...)   |
|         SELECT ...        |      | SELECT ...                |
|       ) sub2              |      | FROM step1                |
|   ) sub1                  |      | JOIN step2 ...            |
| WHERE ...                 |      | JOIN step3 ...            |
+---------------------------+      +---------------------------+

Read from inside out               Read from top to bottom
Hard to debug                      Easy to debug
Hard to maintain                   Easy to maintain
```

---

## Multiple CTEs

You can chain multiple CTEs together, separated by commas. Each CTE can reference the ones defined before it.

```sql
WITH monthly_totals AS (
    SELECT
        DATE_TRUNC('month', order_date)::DATE AS month,
        SUM(total) AS month_total
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date)
),
monthly_with_prev AS (
    SELECT
        month,
        month_total,
        LAG(month_total) OVER (ORDER BY month) AS prev_total
    FROM monthly_totals
),
monthly_growth AS (
    SELECT
        month,
        month_total,
        prev_total,
        CASE
            WHEN prev_total IS NULL THEN NULL
            ELSE ROUND(
                (month_total - prev_total) / prev_total * 100, 1
            )
        END AS growth_pct
    FROM monthly_with_prev
)
SELECT * FROM monthly_growth
ORDER BY month;
```

```
   month    | month_total | prev_total | growth_pct
------------+-------------+------------+-----------
 2024-01-01 |      400.00 |            |
 2024-02-01 |      750.00 |     400.00 |      87.5
 2024-03-01 |      875.00 |     750.00 |      16.7
 2024-04-01 |      350.00 |     875.00 |     -60.0
(4 rows)
```

**Line-by-line explanation:**
- `monthly_totals` — Step 1: aggregate orders by month
- `monthly_with_prev` — Step 2: add previous month's total using LAG (references step 1)
- `monthly_growth` — Step 3: calculate growth percentage (references step 2)
- The final SELECT reads from the last CTE

Each step is simple on its own. Together, they build a complex analysis.

```
Data Flow Through Multiple CTEs:

orders table
     |
     v
+----------------+     +------------------+     +---------------+
| monthly_totals | --> | monthly_with_prev| --> | monthly_growth|
| (GROUP BY)     |     | (LAG)            |     | (% calc)      |
+----------------+     +------------------+     +---------------+
                                                       |
                                                       v
                                                 Final SELECT
```

---

## CTE vs Subquery vs View

```
+------------------+--------------------+-------------------+-------------------+
| Feature          | Subquery           | CTE               | View              |
+------------------+--------------------+-------------------+-------------------+
| Scope            | Inside one query   | Inside one query   | Permanent object  |
| Reusable         | No (must repeat)   | Yes (within query) | Yes (any query)   |
| Readable         | Hard when nested   | Very readable      | Very readable     |
| Stored in DB     | No                 | No                 | Yes               |
| Can be recursive | No                 | Yes                | No                |
| Performance      | Same as CTE*       | Same as subquery*  | Same as CTE*      |
+------------------+--------------------+-------------------+-------------------+

* In PostgreSQL 12+, CTEs are usually inlined (optimized the same as subqueries).
  In earlier versions, CTEs were always materialized (computed once).
```

### When to Use Each

- **Subquery**: Simple, one-time use, not deeply nested
- **CTE**: Complex logic, multiple steps, need to reference the same result multiple times, or when you want readable code
- **View**: Need to reuse the query across multiple queries, or share the logic with other users

---

## Recursive CTEs

A recursive CTE is a CTE that references itself. It is how SQL traverses trees and hierarchies.

### The Basic Structure

```sql
WITH RECURSIVE cte_name AS (
    -- Base case (anchor): the starting point
    SELECT ...
    WHERE ... (starting condition)

    UNION ALL

    -- Recursive case: references the CTE itself
    SELECT ...
    FROM table_name
    JOIN cte_name ON ... (how to find the next level)
)
SELECT * FROM cte_name;
```

```
How Recursion Works:

Step 1: Run the base case (anchor query)
        Result: {Row A}

Step 2: Run recursive query using Step 1 results
        Result: {Row B, Row C}

Step 3: Run recursive query using Step 2 results
        Result: {Row D, Row E}

Step 4: Run recursive query using Step 3 results
        Result: {} (empty — stop!)

Final result: {Row A, Row B, Row C, Row D, Row E}
```

### The Organizational Chart Analogy

Think of it like exploring a family tree. You start with the founder (base case). Then you find everyone who reports directly to the founder (first recursion). Then you find everyone who reports to those people (second recursion). You keep going until there are no more reports to find.

---

## Practical: Organizational Chart

Let us build the complete organizational chart starting from the CEO:

```sql
WITH RECURSIVE org_chart AS (
    -- Base case: start with the CEO (no manager)
    SELECT
        employee_id,
        name,
        manager_id,
        department,
        salary,
        0 AS level,
        name AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: find employees who report to someone
    -- we already found
    SELECT
        e.employee_id,
        e.name,
        e.manager_id,
        e.department,
        e.salary,
        oc.level + 1,
        oc.path || ' > ' || e.name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.employee_id
)
SELECT
    REPEAT('  ', level) || name AS employee,
    department,
    salary,
    level,
    path
FROM org_chart
ORDER BY path;
```

```
       employee        | department  |  salary   | level |                path
------------------------+-------------+-----------+-------+------------------------------------
 Sarah CEO             | Executive   | 200000.00 |     0 | Sarah CEO
   Lisa VP Sales       | Sales       | 145000.00 |     1 | Sarah CEO > Lisa VP Sales
     Kim Sales Rep     | Sales       |  72000.00 |     2 | Sarah CEO > Lisa VP Sales > Kim...
     Sam Sales Rep     | Sales       |  70000.00 |     2 | Sarah CEO > Lisa VP Sales > Sam...
   Tom VP Eng          | Engineering | 150000.00 |     1 | Sarah CEO > Tom VP Eng
     Anna Director     | Engineering | 118000.00 |     2 | Sarah CEO > Tom VP Eng > Anna...
     Mike Director     | Engineering | 120000.00 |     2 | Sarah CEO > Tom VP Eng > Mike...
       Emma Manager    | Engineering |  92000.00 |     3 | Sarah CEO > ... > Emma Manager
       Jake Manager    | Engineering |  95000.00 |     3 | Sarah CEO > ... > Jake Manager
         Chris Developer| Engineering |  85000.00 |     4 | Sarah CEO > ... > Chris Developer
         Pat Developer | Engineering |  82000.00 |     4 | Sarah CEO > ... > Pat Developer
(11 rows)
```

**Line-by-line explanation of the recursive CTE:**
- `WHERE manager_id IS NULL` — the base case finds the CEO (who has no manager)
- `0 AS level` — the CEO is at level 0
- `name AS path` — start building the path with just the CEO's name
- `JOIN org_chart oc ON e.manager_id = oc.employee_id` — find employees whose manager is someone we already found
- `oc.level + 1` — each level down adds 1
- `oc.path || ' > ' || e.name` — append the current name to the path

### Visualizing the Hierarchy

```
                    Sarah CEO (Level 0)
                    /              \
           Tom VP Eng          Lisa VP Sales (Level 1)
           /        \            /        \
    Mike Dir    Anna Dir    Sam Rep    Kim Rep (Level 2)
     /     \
Jake Mgr  Emma Mgr                              (Level 3)
  /    \
Chris  Pat                                       (Level 4)
```

---

## Practical: Category Tree with Breadcrumb Paths

Let us build breadcrumb paths for a product category tree:

```sql
WITH RECURSIVE category_tree AS (
    -- Base case: top-level categories (no parent)
    SELECT
        category_id,
        category_name,
        parent_id,
        1 AS depth,
        category_name AS breadcrumb
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive case: child categories
    SELECT
        c.category_id,
        c.category_name,
        c.parent_id,
        ct.depth + 1,
        ct.breadcrumb || ' > ' || c.category_name
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.category_id
)
SELECT
    REPEAT('  ', depth - 1) || category_name AS category,
    depth,
    breadcrumb
FROM category_tree
ORDER BY breadcrumb;
```

```
        category       | depth |                breadcrumb
-----------------------+-------+------------------------------------------
 Clothing              |     1 | Clothing
   Men                 |     2 | Clothing > Men
     Pants             |     3 | Clothing > Men > Pants
     Shirts            |     3 | Clothing > Men > Shirts
   Women               |     2 | Clothing > Women
 Electronics           |     1 | Electronics
   Computers           |     2 | Electronics > Computers
     Desktops          |     3 | Electronics > Computers > Desktops
     Laptops           |     3 | Electronics > Computers > Laptops
       Business Laptops|     4 | Electronics > Computers > Laptops > ...
       Gaming Laptops  |     4 | Electronics > Computers > Laptops > ...
   Phones              |     2 | Electronics > Phones
     Feature Phones    |     3 | Electronics > Phones > Feature Phones
     Smartphones       |     3 | Electronics > Phones > Smartphones
(14 rows)
```

The breadcrumb paths are exactly what you would see in an e-commerce navigation bar:

```
Electronics > Computers > Laptops > Gaming Laptops
```

---

## Finding All Descendants

Find all employees who report to Tom VP Eng (directly or indirectly):

```sql
WITH RECURSIVE reports AS (
    -- Base case: start with Tom
    SELECT employee_id, name, manager_id, salary
    FROM employees
    WHERE employee_id = 2  -- Tom VP Eng

    UNION ALL

    -- Recursive case: find everyone who reports to someone
    -- we already found
    SELECT e.employee_id, e.name, e.manager_id, e.salary
    FROM employees e
    JOIN reports r ON e.manager_id = r.employee_id
)
SELECT name, salary
FROM reports
WHERE employee_id != 2  -- Exclude Tom himself
ORDER BY salary DESC;
```

```
      name       |  salary
-----------------+----------
 Mike Director   | 120000.00
 Anna Director   | 118000.00
 Jake Manager    |  95000.00
 Emma Manager    |  92000.00
 Chris Developer |  85000.00
 Pat Developer   |  82000.00
(6 rows)
```

---

## Generating a Number Series

Recursive CTEs can generate sequences of numbers:

```sql
WITH RECURSIVE numbers AS (
    -- Base case: start with 1
    SELECT 1 AS n

    UNION ALL

    -- Recursive case: add 1 each time
    SELECT n + 1
    FROM numbers
    WHERE n < 10
)
SELECT n FROM numbers;
```

```
 n
----
  1
  2
  3
  4
  5
  6
  7
  8
  9
 10
(10 rows)
```

**Important**: The `WHERE n < 10` is the termination condition. Without it, the recursion would run forever (or until PostgreSQL's recursion limit is hit).

### Generating a Date Series

```sql
WITH RECURSIVE dates AS (
    SELECT DATE '2024-01-01' AS d

    UNION ALL

    SELECT d + INTERVAL '1 month'
    FROM dates
    WHERE d < DATE '2024-06-01'
)
SELECT d::DATE AS month FROM dates;
```

```
   month
------------
 2024-01-01
 2024-02-01
 2024-03-01
 2024-04-01
 2024-05-01
 2024-06-01
(6 rows)
```

**Note**: PostgreSQL has a built-in `generate_series()` function that is usually better for simple sequences. Recursive CTEs are more useful when the logic at each step is complex.

---

## Counting Levels in a Hierarchy

How many levels deep is each part of the organization?

```sql
WITH RECURSIVE org_depth AS (
    SELECT
        employee_id,
        name,
        manager_id,
        0 AS depth
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT
        e.employee_id,
        e.name,
        e.manager_id,
        od.depth + 1
    FROM employees e
    JOIN org_depth od ON e.manager_id = od.employee_id
)
SELECT
    MAX(depth) AS max_depth,
    COUNT(*) FILTER (WHERE depth = 0) AS level_0,
    COUNT(*) FILTER (WHERE depth = 1) AS level_1,
    COUNT(*) FILTER (WHERE depth = 2) AS level_2,
    COUNT(*) FILTER (WHERE depth = 3) AS level_3,
    COUNT(*) FILTER (WHERE depth = 4) AS level_4
FROM org_depth;
```

```
 max_depth | level_0 | level_1 | level_2 | level_3 | level_4
-----------+---------+---------+---------+---------+---------
         4 |       1 |       2 |       4 |       2 |       2
(1 row)
```

The organization is 5 levels deep (0 through 4), with the most employees at level 2.

---

## Safety: Preventing Infinite Recursion

If your data has a cycle (employee A reports to B, who reports to A), the recursive CTE will loop forever. PostgreSQL has a default recursion limit, but you can also protect yourself:

### Method 1: Limit Depth

```sql
WITH RECURSIVE safe_tree AS (
    SELECT employee_id, name, manager_id, 0 AS depth
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT e.employee_id, e.name, e.manager_id, st.depth + 1
    FROM employees e
    JOIN safe_tree st ON e.manager_id = st.employee_id
    WHERE st.depth < 20  -- Safety limit: stop at 20 levels
)
SELECT * FROM safe_tree;
```

### Method 2: Track Visited Nodes

```sql
WITH RECURSIVE safe_tree AS (
    SELECT
        employee_id,
        name,
        manager_id,
        ARRAY[employee_id] AS visited
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT
        e.employee_id,
        e.name,
        e.manager_id,
        st.visited || e.employee_id
    FROM employees e
    JOIN safe_tree st ON e.manager_id = st.employee_id
    WHERE e.employee_id != ALL(st.visited)  -- Skip if already visited
)
SELECT * FROM safe_tree;
```

---

## Common Mistakes

### Mistake 1: Forgetting RECURSIVE Keyword

```sql
-- BAD: Missing RECURSIVE keyword
WITH org AS (
    SELECT * FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.* FROM employees e JOIN org ON e.manager_id = org.employee_id
    -- ERROR: relation "org" does not exist
)
SELECT * FROM org;

-- GOOD: Include RECURSIVE
WITH RECURSIVE org AS (
    ...
)
SELECT * FROM org;
```

### Mistake 2: No Termination Condition

```sql
-- BAD: This will run forever!
WITH RECURSIVE nums AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM nums
    -- No WHERE clause to stop!
)
SELECT * FROM nums;

-- GOOD: Always have a stopping condition
WITH RECURSIVE nums AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM nums
    WHERE n < 100  -- Stop at 100
)
SELECT * FROM nums;
```

### Mistake 3: Using UNION Instead of UNION ALL

```sql
-- CAUTION: UNION removes duplicates (slower, and may hide
-- legitimate duplicate paths in a graph)
-- Use UNION ALL unless you specifically need deduplication
WITH RECURSIVE tree AS (
    ...
    UNION ALL  -- Usually want UNION ALL for recursion
    ...
)
```

### Mistake 4: Not Referencing the CTE in the Recursive Part

```sql
-- BAD: The recursive part must reference the CTE
WITH RECURSIVE tree AS (
    SELECT * FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT * FROM employees WHERE manager_id IS NOT NULL
    -- This is not recursive! It just gets all rows with managers.
)
```

---

## Best Practices

1. **Use CTEs for readability.** Any time you have more than two levels of nested subqueries, refactor into CTEs.

2. **Give CTEs descriptive names.** Use `monthly_totals` instead of `cte1`. Good names make the query self-documenting.

3. **Always include a termination condition in recursive CTEs.** Either filter by depth, use a WHERE clause, or track visited nodes.

4. **Use UNION ALL (not UNION) in recursive CTEs** unless you specifically need to eliminate duplicates. UNION ALL is faster and the correct choice for most tree traversals.

5. **Test recursive CTEs on small data first.** Infinite recursion on a large table can consume significant resources.

6. **Consider PostgreSQL's `generate_series()` instead of recursive CTEs** for simple number or date sequences.

---

## Quick Summary

```
+---------------------+----------------------------------------------+
| Concept             | What It Does                                 |
+---------------------+----------------------------------------------+
| WITH ... AS         | Define a named temporary result (CTE)        |
| Multiple CTEs       | Chain CTEs separated by commas               |
| WITH RECURSIVE      | Enable self-referencing CTEs                 |
| Base case (anchor)  | Starting point of recursion                  |
| UNION ALL           | Combines base case with recursive results    |
| Recursive case      | Finds the next level by joining to the CTE   |
| Termination         | WHERE clause that stops the recursion        |
| Path tracking       | Build strings showing the path from root     |
| Depth tracking      | Count levels with a depth counter            |
+---------------------+----------------------------------------------+
```

---

## Key Points

- A CTE is a named temporary result defined with WITH that exists only for one query.
- CTEs improve readability by turning nested subqueries into sequential named steps.
- Multiple CTEs can be chained with commas, each referencing previous ones.
- Recursive CTEs use WITH RECURSIVE and have two parts: a base case and a recursive case joined by UNION ALL.
- The base case provides the starting rows. The recursive case references the CTE itself to find the next level.
- Always include a termination condition to prevent infinite recursion.
- Recursive CTEs are ideal for hierarchies (org charts, category trees) and generating sequences.
- In PostgreSQL 12 and later, non-recursive CTEs are usually optimized the same as subqueries.

---

## Practice Questions

1. What is the difference between a CTE and a subquery? When would you choose one over the other?

2. In a recursive CTE, what are the two required parts? What keyword connects them?

3. What happens if a recursive CTE has no termination condition? How can you protect against this?

4. Can one CTE reference another CTE defined before it in the same WITH clause? Can it reference one defined after it?

5. Why do recursive CTEs typically use UNION ALL instead of UNION?

---

## Exercises

### Exercise 1: Multi-Step Sales Analysis

Using CTEs, write a query that:
1. First CTE: Calculate the total sales per customer
2. Second CTE: Rank customers by their total sales
3. Final query: Show only the top 3 customers with their rank and total

**Hint**: Use two CTEs — one for aggregation and one for ranking.

### Exercise 2: Full Category Breadcrumbs

Write a recursive CTE that generates the full breadcrumb path for every category in the categories table. The output should look like:

```
Electronics > Computers > Laptops > Gaming Laptops
```

Include only leaf categories (categories that have no children).

**Hint**: A leaf category is one whose category_id does not appear as any other category's parent_id.

### Exercise 3: Chain of Command

Write a recursive CTE that, given a specific employee (like Chris Developer), shows the full chain of command from that employee up to the CEO. The output should list each person in the chain with their title and level.

**Hint**: This time, the recursion goes upward — start with the employee and follow manager_id up the tree.

---

## What Is Next?

In Chapter 28, you will learn about stored procedures and functions. You will discover how to save programs directly in the database using PL/pgSQL — complete with variables, IF/ELSE logic, loops, and error handling. These are reusable programs that encapsulate business logic right where your data lives.
