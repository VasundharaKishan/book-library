# Chapter 15: FULL OUTER JOIN, CROSS JOIN, and SELF JOIN

## What You Will Learn

- How FULL OUTER JOIN keeps all rows from both tables, filling NULLs on both sides
- How CROSS JOIN creates every possible combination of rows (cartesian product)
- How SELF JOIN lets a table join to itself
- When to use CROSS JOIN in practice (size and color combinations, scheduling)
- When to use SELF JOIN in practice (employee-manager, finding duplicates)
- Why you should avoid NATURAL JOIN

## Why This Chapter Matters

You have learned INNER JOIN (only matches) and LEFT/RIGHT JOIN (all from one side). This chapter covers three more specialized join types that solve problems the others cannot.

Think of these as specialty tools in a toolbox. You do not use them every day, but when you need them, nothing else will do:

- **FULL OUTER JOIN** is like comparing two guest lists and seeing everyone — attendees at both events, attendees at only the first event, and attendees at only the second event.
- **CROSS JOIN** is like a menu generator — if you have 3 sizes and 4 colors, it produces all 12 combinations.
- **SELF JOIN** is like an organizational chart — each employee row points to another employee row (their manager).

---

## Setting Up Additional Practice Data

We will continue using the tables from previous chapters and add a few more for this chapter.

```sql
CREATE TABLE sizes (
    size_id   SERIAL PRIMARY KEY,
    size_name VARCHAR(20) NOT NULL
);

CREATE TABLE colors (
    color_id   SERIAL PRIMARY KEY,
    color_name VARCHAR(20) NOT NULL
);

INSERT INTO sizes (size_name) VALUES
('Small'), ('Medium'), ('Large');

INSERT INTO colors (color_name) VALUES
('Red'), ('Blue'), ('Green'), ('Black');
```

Let us also create a table where employees have managers (other employees).

```sql
CREATE TABLE staff (
    staff_id   SERIAL PRIMARY KEY,
    name       VARCHAR(50) NOT NULL,
    role       VARCHAR(50),
    manager_id INTEGER REFERENCES staff(staff_id)
);

INSERT INTO staff (name, role, manager_id) VALUES
('Sarah',   'CEO',              NULL),
('Tom',     'VP Engineering',   1),
('Lisa',    'VP Marketing',     1),
('Mike',    'Senior Developer', 2),
('Anna',    'Developer',        2),
('Jake',    'Marketing Lead',   3),
('Rachel',  'Designer',         3);
```

The staff table hierarchy looks like this:

```
Sarah (CEO)
├── Tom (VP Engineering)
│   ├── Mike (Senior Developer)
│   └── Anna (Developer)
└── Lisa (VP Marketing)
    ├── Jake (Marketing Lead)
    └── Rachel (Designer)
```

---

## FULL OUTER JOIN — All Rows from Both Tables

FULL OUTER JOIN returns **everything**: all rows from the left table AND all rows from the right table. Where there is a match, it combines the rows. Where there is no match on either side, it fills in NULLs.

### The Syntax

```sql
SELECT columns
FROM table_a
FULL OUTER JOIN table_b
    ON table_a.column = table_b.column;
```

### Visual Representation

```
    Table A           Table B
  +-----------+     +-----------+
  |           |     |           |
  |  +--------+-----+--------+ |
  |  | matches      |        | |
  |  +--------+-----+--------+ |
  |  kept     |     |   kept   |
  |  (NULLs   |     |  (NULLs  |
  |  on right)|     | on left) |
  +-----------+     +-----------+

  EVERYTHING is returned. The entire Venn diagram.
```

### FULL OUTER JOIN Example

```sql
SELECT e.first_name,
       e.last_name,
       d.department_name
FROM employees e
FULL OUTER JOIN departments d
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
| Frank      | Wilson    | NULL            |
| NULL       | NULL      | HR              |
+------------+-----------+-----------------+
(7 rows)
```

### Line-by-Line Explanation

```
SELECT e.first_name,          -- Employee first name (NULL if no employee)
       e.last_name,           -- Employee last name (NULL if no employee)
       d.department_name      -- Department name (NULL if no department)
FROM employees e              -- All employees
FULL OUTER JOIN departments d -- Combined with all departments
    ON e.department_id        -- Where department IDs match
     = d.department_id;
```

**Compare all join types:**

```
+--------+--------+------------+-----------+-----------+
| emp    | dept   | INNER JOIN | LEFT JOIN | FULL JOIN |
+--------+--------+------------+-----------+-----------+
| Alice  | Eng    | Yes        | Yes       | Yes       |
| Bob    | Eng    | Yes        | Yes       | Yes       |
| Eve    | Eng    | Yes        | Yes       | Yes       |
| Charlie| Mktg   | Yes        | Yes       | Yes       |
| Diana  | Sales  | Yes        | Yes       | Yes       |
| Frank  | (none) | NO         | Yes       | Yes       |
| (none) | HR     | NO         | NO        | Yes       |
+--------+--------+------------+-----------+-----------+
```

FULL OUTER JOIN catches both sides: Frank (no department) AND HR (no employees).

### When to Use FULL OUTER JOIN

FULL OUTER JOIN is less common than INNER or LEFT JOIN, but it is useful when you need to find **mismatches on both sides**:

- Reconciling two data sources (find records in A not in B AND records in B not in A)
- Auditing relationships (find all orphaned records on both sides)
- Data migration validation (ensure both old and new tables have the same records)

```sql
-- Find all mismatches: employees without departments AND departments without employees
SELECT e.first_name,
       e.last_name,
       d.department_name,
       CASE
           WHEN e.employee_id IS NULL THEN 'Department has no employees'
           WHEN d.department_id IS NULL THEN 'Employee has no department'
           ELSE 'Matched'
       END AS status
FROM employees e
FULL OUTER JOIN departments d
    ON e.department_id = d.department_id
WHERE e.employee_id IS NULL
   OR d.department_id IS NULL;
```

**Result:**

```
+------------+-----------+-----------------+-----------------------------+
| first_name | last_name | department_name | status                      |
+------------+-----------+-----------------+-----------------------------+
| Frank      | Wilson    | NULL            | Employee has no department   |
| NULL       | NULL      | HR              | Department has no employees  |
+------------+-----------+-----------------+-----------------------------+
(2 rows)
```

---

## CROSS JOIN — Every Possible Combination

CROSS JOIN combines **every row** from the first table with **every row** from the second table. If table A has 3 rows and table B has 4 rows, the result has 3 x 4 = 12 rows.

This is called a **cartesian product**. There is no ON clause because you are not matching anything — you want every combination.

### The Syntax

```sql
SELECT columns
FROM table_a
CROSS JOIN table_b;
```

### CROSS JOIN Example: Size and Color Combinations

```sql
SELECT s.size_name,
       c.color_name
FROM sizes s
CROSS JOIN colors c
ORDER BY s.size_id, c.color_id;
```

**Result:**

```
+-----------+------------+
| size_name | color_name |
+-----------+------------+
| Small     | Red        |
| Small     | Blue       |
| Small     | Green      |
| Small     | Black      |
| Medium    | Red        |
| Medium    | Blue       |
| Medium    | Green      |
| Medium    | Black      |
| Large     | Red        |
| Large     | Blue       |
| Large     | Green      |
| Large     | Black      |
+-----------+------------+
(12 rows)
```

3 sizes x 4 colors = 12 combinations. Every size paired with every color.

### How CROSS JOIN Works Visually

```
Sizes:     Colors:
+--------+ +--------+
| Small  | | Red    |    Small-Red, Small-Blue, Small-Green, Small-Black
| Medium | | Blue   |    Medium-Red, Medium-Blue, Medium-Green, Medium-Black
| Large  | | Green  |    Large-Red, Large-Blue, Large-Green, Large-Black
+--------+ | Black  |
           +--------+

3 rows  x  4 rows  =  12 result rows
```

### Practical Use: Product Variant Generator

```sql
SELECT s.size_name,
       c.color_name,
       'SKU-' || UPPER(LEFT(s.size_name, 1))
              || '-' || UPPER(LEFT(c.color_name, 3)) AS sku
FROM sizes s
CROSS JOIN colors c
ORDER BY s.size_name, c.color_name;
```

**Result:**

```
+-----------+------------+---------+
| size_name | color_name | sku     |
+-----------+------------+---------+
| Large     | Black      | SKU-L-BLA |
| Large     | Blue       | SKU-L-BLU |
| Large     | Green      | SKU-L-GRE |
| Large     | Red        | SKU-L-RED |
| Medium    | Black      | SKU-M-BLA |
| Medium    | Blue       | SKU-M-BLU |
| Medium    | Green      | SKU-M-GRE |
| Medium    | Red        | SKU-M-RED |
| Small     | Black      | SKU-S-BLA |
| Small     | Blue       | SKU-S-BLU |
| Small     | Green      | SKU-S-GRE |
| Small     | Red        | SKU-S-RED |
+-----------+------------+---------+
(12 rows)
```

### Warning: CROSS JOIN Can Produce Huge Results

```
Table A: 1,000 rows
Table B: 1,000 rows
CROSS JOIN result: 1,000,000 rows!

Table A: 10,000 rows
Table B: 10,000 rows
CROSS JOIN result: 100,000,000 rows!
```

Always be aware of the table sizes before using CROSS JOIN. A cartesian product of two large tables can crash your database or consume all available memory.

---

## SELF JOIN — A Table Joins Itself

A SELF JOIN is when a table is joined to itself. This sounds strange at first, but it is incredibly useful for hierarchical data (like org charts) or finding duplicates.

You **must** use different aliases for the same table, so the database can tell the two "copies" apart.

### The Syntax

```sql
SELECT columns
FROM table_name alias_a
INNER JOIN table_name alias_b
    ON alias_a.column = alias_b.column;
```

### Example: Employee-Manager Relationship

```sql
SELECT e.name AS employee,
       e.role AS employee_role,
       m.name AS manager,
       m.role AS manager_role
FROM staff e
LEFT JOIN staff m
    ON e.manager_id = m.staff_id;
```

**Result:**

```
+----------+-------------------+---------+-----------------+
| employee | employee_role     | manager | manager_role    |
+----------+-------------------+---------+-----------------+
| Sarah    | CEO               | NULL    | NULL            |
| Tom      | VP Engineering    | Sarah   | CEO             |
| Lisa     | VP Marketing      | Sarah   | CEO             |
| Mike     | Senior Developer  | Tom     | VP Engineering  |
| Anna     | Developer         | Tom     | VP Engineering  |
| Jake     | Marketing Lead    | Lisa    | VP Marketing    |
| Rachel   | Designer          | Lisa    | VP Marketing    |
+----------+-------------------+---------+-----------------+
(7 rows)
```

### Line-by-Line Explanation

```
SELECT e.name AS employee,       -- The employee's name
       e.role AS employee_role,  -- The employee's role
       m.name AS manager,        -- The manager's name
       m.role AS manager_role    -- The manager's role
FROM staff e                     -- Treat staff as "employees" (alias e)
LEFT JOIN staff m                -- Join the SAME table as "managers" (alias m)
    ON e.manager_id              -- Where the employee's manager_id
     = m.staff_id;               -- matches the manager's staff_id
```

We use LEFT JOIN (not INNER JOIN) so Sarah (the CEO) still appears even though she has no manager (manager_id is NULL).

### How Self Join Works Visually

```
staff table (as "employees"):        staff table (as "managers"):
+----+--------+------------+        +----+--------+
| id | name   | manager_id |        | id | name   |
+----+--------+------------+        +----+--------+
|  1 | Sarah  | NULL       |        |  1 | Sarah  |
|  2 | Tom    | 1       ---+------->|  1 | Sarah  |
|  3 | Lisa   | 1       ---+------->|  1 | Sarah  |
|  4 | Mike   | 2       ---+------->|  2 | Tom    |
|  5 | Anna   | 2       ---+------->|  2 | Tom    |
|  6 | Jake   | 3       ---+------->|  3 | Lisa   |
|  7 | Rachel | 3       ---+------->|  3 | Lisa   |
+----+--------+------------+        +----+--------+

Same table, two aliases, different roles in the query.
```

### Example: Finding Employees Who Share the Same Manager

```sql
SELECT a.name AS employee_1,
       b.name AS employee_2,
       m.name AS shared_manager
FROM staff a
INNER JOIN staff b
    ON a.manager_id = b.manager_id
   AND a.staff_id < b.staff_id
INNER JOIN staff m
    ON a.manager_id = m.staff_id;
```

**Result:**

```
+------------+------------+----------------+
| employee_1 | employee_2 | shared_manager |
+------------+------------+----------------+
| Tom        | Lisa       | Sarah          |
| Mike       | Anna       | Tom            |
| Jake       | Rachel     | Lisa           |
+------------+------------+----------------+
(3 rows)
```

The trick `a.staff_id < b.staff_id` prevents duplicates. Without it, you would get "Tom-Lisa" AND "Lisa-Tom" as separate rows.

### Example: Finding Duplicate Emails

Self join can find rows that share the same value in a column.

```sql
-- Using our employees table
SELECT a.first_name AS emp_1,
       b.first_name AS emp_2,
       a.email
FROM employees a
INNER JOIN employees b
    ON a.email = b.email
   AND a.employee_id < b.employee_id;
```

If any two employees share the same email address, this query will find them. In our sample data there are no duplicates, so the result would be empty. But in a real database with thousands of records, this is a valuable data quality check.

---

## NATURAL JOIN — Know It, But Avoid It

NATURAL JOIN automatically matches columns that share the same name between two tables. It requires no ON clause.

```sql
-- NATURAL JOIN (avoid this)
SELECT e.first_name, d.department_name
FROM employees e
NATURAL JOIN departments d;
```

This is equivalent to:

```sql
-- Explicit JOIN (use this instead)
SELECT e.first_name, d.department_name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.department_id;
```

### Why You Should Avoid NATURAL JOIN

1. **Fragile.** If someone adds a column with the same name to both tables, the join condition changes silently. Your query could break or return wrong results without any error message.

2. **Implicit.** You cannot tell what columns are being matched just by reading the query. You have to know the table schemas.

3. **Dangerous.** Two tables might share column names that are not meant to be joined on (like `name`, `status`, or `created_at`).

```
Scenario: Both tables have a "name" column

-- NATURAL JOIN will match on BOTH department_id AND name
-- This is almost certainly wrong!

Before: JOIN ON department_id           (correct)
After:  JOIN ON department_id AND name  (wrong!)
```

**Rule of thumb:** Always write explicit JOIN conditions with ON. It is a few more characters to type, but it makes your intent crystal clear and protects against schema changes.

---

## Comparison: All Join Types at a Glance

```
+-------------------+------------------------------------------+
| Join Type         | What It Returns                          |
+-------------------+------------------------------------------+
| INNER JOIN        | Only matching rows                       |
| LEFT JOIN         | All from left + matching from right      |
| RIGHT JOIN        | All from right + matching from left      |
| FULL OUTER JOIN   | All from both sides                      |
| CROSS JOIN        | Every combination (no ON clause)         |
| SELF JOIN         | Table joined to itself (any join type)   |
| NATURAL JOIN      | Auto-matches same-named columns (avoid)  |
+-------------------+------------------------------------------+
```

Visual summary:

```
INNER:       LEFT:        RIGHT:       FULL OUTER:    CROSS:
  +--+         +----+        +----+      +------+      AxB
 /    \       /  +--+\      /+--+  \    / +----+ \    (all
| A&&B |     |A |A&B| |    | |A&B|B |  |A |A&&B| B|   combos)
 \    /       \  +--+/      \+--+  /    \ +----+ /
  +--+         +----+        +----+      +------+
```

---

## Common Mistakes

### Mistake 1: Accidental CROSS JOIN

```sql
-- WRONG: Forgot the ON clause — this creates a CROSS JOIN
SELECT e.first_name, d.department_name
FROM employees e, departments d;
-- Returns 6 x 4 = 24 rows (every combination)!
```

**Fix:** Always use explicit JOIN syntax with an ON clause.

### Mistake 2: SELF JOIN Without Proper Aliases

```sql
-- WRONG: Ambiguous table references
SELECT name, manager_id
FROM staff
INNER JOIN staff ON manager_id = staff_id;
-- ERROR: table name "staff" specified more than once
```

**Fix:** Give each instance a unique alias.

```sql
-- CORRECT
SELECT e.name, m.name AS manager
FROM staff e
INNER JOIN staff m ON e.manager_id = m.staff_id;
```

### Mistake 3: Forgetting the Duplicate Prevention in Self Joins

```sql
-- WRONG: Gets duplicates (Tom-Lisa AND Lisa-Tom)
SELECT a.name, b.name
FROM staff a
INNER JOIN staff b
    ON a.manager_id = b.manager_id;
-- Also includes Tom-Tom and Lisa-Lisa (self-pairs)!
```

**Fix:** Use `a.id < b.id` to get each pair only once and exclude self-pairs.

```sql
-- CORRECT
SELECT a.name, b.name
FROM staff a
INNER JOIN staff b
    ON a.manager_id = b.manager_id
   AND a.staff_id < b.staff_id;
```

### Mistake 4: Using CROSS JOIN on Large Tables

```sql
-- DANGEROUS: Could produce millions of rows
SELECT *
FROM customers
CROSS JOIN orders;
-- With 10,000 customers and 50,000 orders = 500,000,000 rows!
```

**Fix:** Only use CROSS JOIN on small reference tables (sizes, colors, categories). Check row counts first.

---

## Best Practices

1. **Use FULL OUTER JOIN for reconciliation tasks.** It is perfect for comparing two data sets and finding mismatches on both sides.

2. **Be cautious with CROSS JOIN.** Always check the row counts of both tables first. Use it only with small reference tables (under a few hundred rows).

3. **Use meaningful aliases in self joins.** Instead of `a` and `b`, use `e` (employee) and `m` (manager) to make the query self-documenting.

4. **Use `a.id < b.id` in self joins** when finding pairs to prevent duplicates and self-matches.

5. **Never use NATURAL JOIN** in production code. Always write explicit ON conditions.

6. **Comment your self joins.** They can be confusing to read. Add a comment explaining the relationship (e.g., `-- e = employee, m = their manager`).

---

## Quick Summary

| Concept | Description |
|---------|-------------|
| FULL OUTER JOIN | Returns all rows from both tables, NULLs on both sides |
| CROSS JOIN | Every row from A combined with every row from B (cartesian product) |
| SELF JOIN | A table joined to itself using different aliases |
| NATURAL JOIN | Auto-matches same-named columns (avoid it) |
| `a.id < b.id` | Prevents duplicate pairs in self joins |
| Cartesian product | M rows x N rows = M*N result rows |

---

## Key Points

- **FULL OUTER JOIN** returns all rows from both tables. Use it when you need to find mismatches on **both sides** of a relationship.
- **CROSS JOIN** produces a cartesian product — every combination. It has no ON clause. Use it for generating combinations (sizes, colors, schedules).
- **SELF JOIN** lets a table reference itself. It requires two different aliases for the same table. Common use cases are hierarchies (employee-manager) and finding duplicates.
- **NATURAL JOIN** automatically matches same-named columns. Avoid it — it is implicit, fragile, and dangerous when schemas change.
- Always use `a.id < b.id` in self joins when finding pairs to eliminate duplicates and self-matches.
- CROSS JOIN on large tables can produce millions of rows. Always check table sizes first.

---

## Practice Questions

**Question 1:** When would you choose FULL OUTER JOIN over LEFT JOIN?

<details>
<summary>Answer</summary>

Use FULL OUTER JOIN when you need to find mismatches on **both sides**. LEFT JOIN only shows unmatched rows from the left table. FULL OUTER JOIN shows unmatched rows from both the left AND right tables. This is useful for data reconciliation and auditing.

</details>

**Question 2:** If table A has 5 rows and table B has 3 rows, how many rows does CROSS JOIN produce?

<details>
<summary>Answer</summary>

5 x 3 = 15 rows. CROSS JOIN produces the cartesian product — every row from A paired with every row from B.

</details>

**Question 3:** Why do self joins require two different aliases for the same table?

<details>
<summary>Answer</summary>

The database needs a way to distinguish between the two "copies" of the table. Without aliases, column references would be ambiguous — the database would not know which instance of the table you mean. Each alias represents a different logical role (e.g., `e` for employee, `m` for manager).

</details>

**Question 4:** Why is NATURAL JOIN considered dangerous?

<details>
<summary>Answer</summary>

NATURAL JOIN automatically matches ALL columns with the same name. If someone adds a new column to one of the tables that happens to share a name with a column in the other table, the join condition silently changes. This can cause wrong results without any error message. Explicit ON conditions prevent this.

</details>

**Question 5:** How do you prevent duplicate pairs in a self join?

<details>
<summary>Answer</summary>

Add the condition `AND a.id < b.id` to the ON clause. This ensures each pair appears only once (A-B but not B-A) and also prevents self-pairs (A-A). Using `<` instead of `<>` or `!=` is the key — `<>` would still give you both A-B and B-A.

</details>

---

## Exercises

### Exercise 1: Data Reconciliation

Write a query using FULL OUTER JOIN to find all employees without departments AND all departments without employees. Show the employee name (or "No employee"), the department name (or "No department"), and a status column indicating the issue.

<details>
<summary>Solution</summary>

```sql
SELECT COALESCE(e.first_name || ' ' || e.last_name, 'No employee')
           AS person,
       COALESCE(d.department_name, 'No department')
           AS department,
       CASE
           WHEN e.employee_id IS NULL THEN 'Empty department'
           WHEN d.department_id IS NULL THEN 'Unassigned employee'
           ELSE 'OK'
       END AS status
FROM employees e
FULL OUTER JOIN departments d
    ON e.department_id = d.department_id;
```

Expected output:

```
+---------------+-----------------+---------------------+
| person        | department      | status              |
+---------------+-----------------+---------------------+
| Alice Johnson | Engineering     | OK                  |
| Bob Smith     | Engineering     | OK                  |
| Eve Davis     | Engineering     | OK                  |
| Charlie Brown | Marketing       | OK                  |
| Diana Lee     | Sales           | OK                  |
| Frank Wilson  | No department   | Unassigned employee |
| No employee   | HR              | Empty department    |
+---------------+-----------------+---------------------+
```

</details>

### Exercise 2: Product Combinations

Using the sizes and colors tables, write a query that generates a product catalog with a formatted product description and a price based on the size (Small = 19.99, Medium = 24.99, Large = 29.99).

<details>
<summary>Solution</summary>

```sql
SELECT s.size_name || ' ' || c.color_name || ' T-Shirt' AS product,
       CASE s.size_name
           WHEN 'Small'  THEN 19.99
           WHEN 'Medium' THEN 24.99
           WHEN 'Large'  THEN 29.99
       END AS price
FROM sizes s
CROSS JOIN colors c
ORDER BY price, c.color_name;
```

Expected output:

```
+---------------------------+-------+
| product                   | price |
+---------------------------+-------+
| Small Black T-Shirt       | 19.99 |
| Small Blue T-Shirt        | 19.99 |
| Small Green T-Shirt       | 19.99 |
| Small Red T-Shirt         | 19.99 |
| Medium Black T-Shirt      | 24.99 |
| Medium Blue T-Shirt       | 24.99 |
| Medium Green T-Shirt      | 24.99 |
| Medium Red T-Shirt        | 24.99 |
| Large Black T-Shirt       | 29.99 |
| Large Blue T-Shirt        | 29.99 |
| Large Green T-Shirt       | 29.99 |
| Large Red T-Shirt         | 29.99 |
+---------------------------+-------+
```

</details>

### Exercise 3: Organization Chart

Using the staff table, write a query that shows each person, their role, their manager's name, and their manager's manager's name (grandmanager). Use self joins. Include everyone, even the CEO who has no manager.

<details>
<summary>Solution</summary>

```sql
SELECT e.name AS employee,
       e.role,
       m.name AS manager,
       gm.name AS grandmanager
FROM staff e
LEFT JOIN staff m  ON e.manager_id = m.staff_id
LEFT JOIN staff gm ON m.manager_id = gm.staff_id
ORDER BY e.staff_id;
```

Expected output:

```
+----------+-------------------+---------+--------------+
| employee | role              | manager | grandmanager |
+----------+-------------------+---------+--------------+
| Sarah    | CEO               | NULL    | NULL         |
| Tom      | VP Engineering    | Sarah   | NULL         |
| Lisa     | VP Marketing      | Sarah   | NULL         |
| Mike     | Senior Developer  | Tom     | Sarah        |
| Anna     | Developer         | Tom     | Sarah        |
| Jake     | Marketing Lead    | Lisa    | Sarah        |
| Rachel   | Designer          | Lisa    | Sarah        |
+----------+-------------------+---------+--------------+
```

</details>

---

## What Is Next?

You now know all the major join types. But what if you need to use the result of one query as the input to another? What if you want to find employees who earn more than the average salary, or departments that have at least one employee?

In the next chapter, you will learn about **subqueries** — queries nested inside other queries. Subqueries let you break complex problems into smaller, manageable steps and are one of the most powerful features in SQL.
