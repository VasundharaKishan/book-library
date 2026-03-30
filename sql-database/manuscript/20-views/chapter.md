# Chapter 20: Views

## What You Will Learn

In this chapter, you will learn how to create views, which are saved queries that act like virtual tables. You will discover how to simplify complex queries, control data access, and build reusable abstractions. You will also learn about materialized views, which store cached results for faster performance.

## Why This Chapter Matters

Imagine you live in a house with many windows. Each window gives you a different view of the outside world. The kitchen window shows the garden. The living room window shows the street. The bedroom window shows the backyard. The world outside does not change based on which window you look through, but each window frames a different perspective.

Views in SQL work the same way. Your data sits in tables (the outside world). A view is a window that shows a specific perspective of that data. You do not duplicate the data. You simply define a way to look at it.

In the real world, you will encounter situations where:
- A complex query joins five tables and gets used in ten different reports.
- You want to give a user access to employee names and departments but not salaries.
- You want to hide the complexity of your database schema from application developers.

Views solve all these problems. They are one of the most widely used features in production databases.

---

## What Is a View?

A view is a **saved SQL query** that you can use as if it were a table. When you query a view, PostgreSQL runs the underlying query and returns the results. The view itself does not store any data (with one exception we will cover later).

```
+---------------------------+
|      Regular Tables       |
|  (Actually store data)    |
+---------------------------+
         |
         | SELECT queries
         v
+---------------------------+
|         View              |
|  (Saved query definition) |
|  (No data stored)         |
+---------------------------+
         |
         | You query the view
         v
+---------------------------+
|   Your Results            |
|  (Generated on the fly)   |
+---------------------------+
```

Think of a view like a **recipe card**. The recipe card does not contain the actual cake. It contains instructions for making the cake. Every time you follow the recipe, you get a fresh cake. Similarly, every time you query a view, PostgreSQL follows the saved query and produces fresh results from the current data.

---

## Setting Up Our Practice Data

Let us create tables to work with throughout this chapter.

```sql
CREATE TABLE departments (
    department_id   SERIAL PRIMARY KEY,
    department_name VARCHAR(50) NOT NULL,
    location        VARCHAR(100)
);

CREATE TABLE employees (
    employee_id  SERIAL PRIMARY KEY,
    first_name   VARCHAR(50) NOT NULL,
    last_name    VARCHAR(50) NOT NULL,
    email        VARCHAR(100),
    department_id INTEGER REFERENCES departments(department_id),
    salary       NUMERIC(10,2),
    hire_date    DATE,
    is_active    BOOLEAN DEFAULT TRUE
);

CREATE TABLE sales (
    sale_id      SERIAL PRIMARY KEY,
    employee_id  INTEGER REFERENCES employees(employee_id),
    sale_date    DATE NOT NULL,
    amount       NUMERIC(10,2) NOT NULL,
    product_name VARCHAR(100)
);

INSERT INTO departments (department_name, location) VALUES
('Engineering', 'Building A'),
('Marketing',   'Building B'),
('Sales',       'Building C'),
('HR',          'Building A');

INSERT INTO employees (first_name, last_name, email, department_id, salary, hire_date) VALUES
('Alice',   'Johnson', 'alice@company.com',   1, 95000,  '2020-03-15'),
('Bob',     'Smith',   'bob@company.com',     1, 78000,  '2021-07-01'),
('Charlie', 'Brown',   'charlie@company.com', 2, 62000,  '2019-11-20'),
('Diana',   'Ross',    'diana@company.com',   2, 58000,  '2022-01-10'),
('Edward',  'Wilson',  'edward@company.com',  3, 72000,  '2020-08-05'),
('Fiona',   'Clark',   'fiona@company.com',   3, 45000,  '2023-02-14'),
('George',  'Taylor',  'george@company.com',  1, 110000, '2018-06-01'),
('Hannah',  'Lee',     'hannah@company.com',  4, 65000,  '2021-09-30');

INSERT INTO employees (first_name, last_name, email, department_id, salary, hire_date, is_active) VALUES
('Ivan',    'Petrov',  'ivan@company.com',    3, 55000,  '2022-05-15', FALSE);

INSERT INTO sales (employee_id, sale_date, amount, product_name) VALUES
(5, '2024-01-15', 15000, 'Enterprise License'),
(5, '2024-02-20', 8500,  'Team License'),
(5, '2024-03-10', 22000, 'Enterprise License'),
(6, '2024-01-22', 5000,  'Starter License'),
(6, '2024-02-28', 7500,  'Team License'),
(6, '2024-03-15', 3000,  'Starter License'),
(5, '2024-03-25', 18000, 'Enterprise License'),
(6, '2024-01-05', 4500,  'Starter License');
```

---

## Creating a View: CREATE VIEW

The syntax for creating a view is straightforward.

### Syntax

```sql
CREATE VIEW view_name AS
SELECT ...
FROM ...
WHERE ...;
```

### Example: Employee Directory View

Let us create a simple employee directory that shows names, emails, and department names, but hides salaries and internal IDs.

```sql
CREATE VIEW employee_directory AS
SELECT
    e.first_name,
    e.last_name,
    e.email,
    d.department_name,
    e.hire_date
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.is_active = TRUE;
```

**Line-by-Line Explanation:**

- `CREATE VIEW employee_directory AS` -- Define a new view called `employee_directory`. Everything after `AS` is the query that defines what the view shows.
- `SELECT e.first_name, e.last_name, e.email, d.department_name, e.hire_date` -- Choose only the columns we want to expose. Notice we exclude `salary`, `employee_id`, and `department_id`.
- `FROM employees e JOIN departments d ON e.department_id = d.department_id` -- Join the two tables to get department names.
- `WHERE e.is_active = TRUE` -- Only include active employees. Terminated employees are hidden.

---

## Using Views Like Tables

Once a view is created, you use it exactly like a table in SELECT statements.

```sql
SELECT * FROM employee_directory;
```

**Result:**

```
 first_name | last_name | email               | department_name | hire_date
------------+-----------+---------------------+-----------------+-----------
 Alice      | Johnson   | alice@company.com   | Engineering     | 2020-03-15
 Bob        | Smith     | bob@company.com     | Engineering     | 2021-07-01
 Charlie    | Brown     | charlie@company.com | Marketing       | 2019-11-20
 Diana      | Ross      | diana@company.com   | Marketing       | 2022-01-10
 Edward     | Wilson    | edward@company.com  | Sales           | 2020-08-05
 Fiona      | Clark     | fiona@company.com   | Sales           | 2023-02-14
 George     | Taylor    | george@company.com  | Engineering     | 2018-06-01
 Hannah     | Lee       | hannah@company.com  | HR              | 2021-09-30
(8 rows)
```

Notice that Ivan (who has `is_active = FALSE`) does not appear. The view filters him out automatically.

### Filtering a View

You can add WHERE clauses when querying a view, just like a table.

```sql
SELECT first_name, last_name, department_name
FROM employee_directory
WHERE department_name = 'Engineering'
ORDER BY hire_date;
```

**Result:**

```
 first_name | last_name | department_name
------------+-----------+----------------
 George     | Taylor    | Engineering
 Alice      | Johnson   | Engineering
 Bob        | Smith     | Engineering
(3 rows)
```

### Joining a View with Other Tables

Views can be joined with tables or other views.

```sql
SELECT
    ed.first_name,
    ed.last_name,
    COUNT(s.sale_id) AS total_sales,
    COALESCE(SUM(s.amount), 0) AS total_revenue
FROM employee_directory ed
LEFT JOIN sales s ON ed.first_name = 'Edward' AND s.employee_id = 5
    OR ed.first_name = 'Fiona' AND s.employee_id = 6
WHERE ed.department_name = 'Sales'
GROUP BY ed.first_name, ed.last_name;
```

Views participate in queries just like regular tables. Behind the scenes, PostgreSQL merges the view's query with your outer query and optimizes them together.

---

## How Views Work Behind the Scenes

When you query a view, PostgreSQL does not materialize the view first and then filter it. Instead, it merges the view's query definition into your query and optimizes the combined result.

```
Your Query:
  SELECT * FROM employee_directory WHERE department_name = 'Sales';

PostgreSQL Expands To:
  SELECT e.first_name, e.last_name, e.email, d.department_name, e.hire_date
  FROM employees e
  JOIN departments d ON e.department_id = d.department_id
  WHERE e.is_active = TRUE
    AND d.department_name = 'Sales';
```

This means views have **no performance overhead** compared to writing the query directly. They are purely a convenience feature.

---

## CREATE OR REPLACE VIEW

If you need to modify an existing view, you can use `CREATE OR REPLACE VIEW`. This updates the view definition without dropping and recreating it.

```sql
CREATE OR REPLACE VIEW employee_directory AS
SELECT
    e.first_name,
    e.last_name,
    e.email,
    d.department_name,
    d.location,           -- Added this column
    e.hire_date
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.is_active = TRUE;
```

**Important rules for CREATE OR REPLACE:**

- You can **add** new columns to the end of the SELECT list.
- You **cannot remove** existing columns.
- You **cannot change** the data type of existing columns.
- You **cannot reorder** existing columns.

If you need to make those kinds of changes, you must DROP the view first and recreate it.

```sql
SELECT * FROM employee_directory;
```

**Result:**

```
 first_name | last_name | email               | department_name | location   | hire_date
------------+-----------+---------------------+-----------------+------------+-----------
 Alice      | Johnson   | alice@company.com   | Engineering     | Building A | 2020-03-15
 Bob        | Smith     | bob@company.com     | Engineering     | Building A | 2021-07-01
 Charlie    | Brown     | charlie@company.com | Marketing       | Building B | 2019-11-20
 Diana      | Ross      | diana@company.com   | Marketing       | Building B | 2022-01-10
 Edward     | Wilson    | edward@company.com  | Sales           | Building C | 2020-08-05
 Fiona      | Clark     | fiona@company.com   | Sales           | Building C | 2023-02-14
 George     | Taylor    | george@company.com  | Engineering     | Building A | 2018-06-01
 Hannah     | Lee       | hannah@company.com  | HR              | Building A | 2021-09-30
(8 rows)
```

---

## WITH CHECK OPTION

When a view has a WHERE clause, you might be able to INSERT or UPDATE data through the view (for simple views). But what happens if someone inserts a row through the view that violates the view's WHERE condition? The row would go into the underlying table but would immediately become invisible through the view. This is confusing.

`WITH CHECK OPTION` prevents this. It ensures that any INSERT or UPDATE through the view must produce a row that is visible through the view.

### Example

```sql
CREATE VIEW active_employees AS
SELECT
    employee_id,
    first_name,
    last_name,
    is_active
FROM employees
WHERE is_active = TRUE
WITH CHECK OPTION;
```

Now if someone tries to insert an inactive employee through this view:

```sql
INSERT INTO active_employees (first_name, last_name, is_active)
VALUES ('Test', 'User', FALSE);
```

```
ERROR: new row violates check option for view "active_employees"
DETAIL: Failing row contains (10, Test, User, ..., f).
```

The insert is rejected because `is_active = FALSE` violates the view's WHERE condition.

```
+-------------------------------------------+
|  View: active_employees                   |
|  WHERE is_active = TRUE                   |
|  WITH CHECK OPTION                        |
+-------------------------------------------+
        |                          |
        v                          v
  INSERT (is_active=TRUE)    INSERT (is_active=FALSE)
        |                          |
        v                          v
     Allowed                   REJECTED!
```

---

## DROP VIEW

To remove a view, use the DROP VIEW statement.

```sql
DROP VIEW employee_directory;
```

If other views depend on the view you are trying to drop, you will get an error. Use `CASCADE` to drop the view and all dependent views.

```sql
DROP VIEW employee_directory CASCADE;
```

To avoid errors when the view might not exist:

```sql
DROP VIEW IF EXISTS employee_directory;
```

---

## Materialized Views: Cached Results

A regular view runs its query every time you use it. For complex queries that join many tables or process millions of rows, this can be slow. A **materialized view** solves this by storing the query results physically on disk, like a snapshot.

Think of the difference like this:
- **Regular view** = A window you look through. You see the world as it is right now.
- **Materialized view** = A photograph taken through the window. It shows how the world looked when the photo was taken. To see the current state, you need to take a new photo (refresh).

### Creating a Materialized View

```sql
CREATE MATERIALIZED VIEW sales_summary AS
SELECT
    e.first_name || ' ' || e.last_name AS salesperson,
    COUNT(s.sale_id) AS total_deals,
    SUM(s.amount) AS total_revenue,
    ROUND(AVG(s.amount), 2) AS avg_deal_size,
    MAX(s.amount) AS largest_deal,
    MIN(s.sale_date) AS first_sale,
    MAX(s.sale_date) AS last_sale
FROM employees e
JOIN sales s ON e.employee_id = s.employee_id
GROUP BY e.first_name, e.last_name;
```

```sql
SELECT * FROM sales_summary;
```

**Result:**

```
  salesperson   | total_deals | total_revenue | avg_deal_size | largest_deal | first_sale | last_sale
----------------+-------------+---------------+---------------+--------------+------------+-----------
 Edward Wilson  |           4 |         63500 |      15875.00 |        22000 | 2024-01-15 | 2024-03-25
 Fiona Clark    |           4 |         20000 |       5000.00 |         7500 | 2024-01-05 | 2024-03-15
(2 rows)
```

### Refreshing a Materialized View

When the underlying data changes (new sales are added, for example), the materialized view still shows the old data. You need to explicitly refresh it.

```sql
-- Add a new sale
INSERT INTO sales (employee_id, sale_date, amount, product_name)
VALUES (5, '2024-04-01', 30000, 'Enterprise License');

-- The materialized view still shows old data
SELECT total_deals, total_revenue FROM sales_summary
WHERE salesperson = 'Edward Wilson';
```

```
 total_deals | total_revenue
-------------+--------------
           4 |         63500
(1 row)
```

```sql
-- Refresh the materialized view
REFRESH MATERIALIZED VIEW sales_summary;

-- Now it shows updated data
SELECT total_deals, total_revenue FROM sales_summary
WHERE salesperson = 'Edward Wilson';
```

```
 total_deals | total_revenue
-------------+--------------
           5 |         93500
(1 row)
```

### CONCURRENTLY Refresh

The basic `REFRESH` command locks the materialized view while refreshing. No one can query it during the refresh. For large views, use `CONCURRENTLY` to allow queries during the refresh.

```sql
-- First, create a unique index (required for CONCURRENTLY)
CREATE UNIQUE INDEX idx_sales_summary_person ON sales_summary(salesperson);

-- Now you can refresh without blocking readers
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_summary;
```

### Regular View vs. Materialized View

```
+--------------------+---------------------------+---------------------------+
| Feature            | Regular View              | Materialized View         |
+--------------------+---------------------------+---------------------------+
| Stores data?       | No (query only)           | Yes (cached on disk)      |
| Always up to date? | Yes                       | No (needs REFRESH)        |
| Query speed         | Same as running the query | Fast (reads cached data)  |
| Uses disk space?   | No                        | Yes                       |
| Can have indexes?  | No                        | Yes                       |
| Good for           | Simple queries, security  | Complex/slow queries      |
+--------------------+---------------------------+---------------------------+
```

---

## When to Use Views

### 1. Security: Restricting Access to Data

Views let you control what data users can see without modifying the underlying tables.

```sql
-- HR can see everything
CREATE VIEW hr_employee_view AS
SELECT * FROM employees;

-- Managers see names and departments, but not salaries
CREATE VIEW manager_employee_view AS
SELECT employee_id, first_name, last_name, department_id, hire_date
FROM employees
WHERE is_active = TRUE;

-- Public directory shows only names and emails
CREATE VIEW public_directory AS
SELECT first_name, last_name, email
FROM employees
WHERE is_active = TRUE;
```

```
+------------------+
|  employees table |
| (all columns,    |
|  all rows)       |
+------------------+
   |       |       |
   v       v       v
+------+ +------+ +------+
| HR   | | Mgr  | | Pub  |
| View | | View | | View |
| All  | | No $ | | Name |
| cols | | only | | only |
+------+ +------+ +------+
```

### 2. Simplicity: Hiding Complex Queries

Save a complex query once, then use it with a simple SELECT.

```sql
CREATE VIEW monthly_sales_report AS
SELECT
    TO_CHAR(s.sale_date, 'YYYY-MM') AS month,
    d.department_name,
    e.first_name || ' ' || e.last_name AS salesperson,
    COUNT(s.sale_id) AS deals,
    SUM(s.amount) AS revenue,
    ROUND(AVG(s.amount), 2) AS avg_deal
FROM sales s
JOIN employees e ON s.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
GROUP BY
    TO_CHAR(s.sale_date, 'YYYY-MM'),
    d.department_name,
    e.first_name, e.last_name
ORDER BY month, revenue DESC;
```

Now anyone can get the monthly sales report with:

```sql
SELECT * FROM monthly_sales_report;
```

**Result:**

```
  month  | department_name |  salesperson  | deals | revenue |  avg_deal
---------+-----------------+---------------+-------+---------+----------
 2024-01 | Sales           | Edward Wilson |     1 |   15000 | 15000.00
 2024-01 | Sales           | Fiona Clark   |     2 |    9500 |  4750.00
 2024-02 | Sales           | Edward Wilson |     1 |    8500 |  8500.00
 2024-02 | Sales           | Fiona Clark   |     1 |    7500 |  7500.00
 2024-03 | Sales           | Edward Wilson |     2 |   40000 | 20000.00
 2024-03 | Sales           | Fiona Clark   |     1 |    3000 |  3000.00
(6 rows)
```

### 3. Abstraction: Insulating from Schema Changes

If you rename a column or restructure a table, you can update the view definition without changing the application code that queries the view.

```
Before:                          After:
  App --> employees table          App --> employee_view --> employees table
                                          (view absorbs     (column renamed)
                                           the change)
```

---

## Practical Example: Sales Summary View

Let us build a comprehensive sales dashboard view.

```sql
CREATE VIEW sales_dashboard AS
SELECT
    e.first_name || ' ' || e.last_name AS salesperson,
    d.department_name,
    COUNT(s.sale_id) AS total_deals,
    SUM(s.amount) AS total_revenue,
    ROUND(AVG(s.amount), 2) AS avg_deal_size,
    MAX(s.amount) AS best_deal,
    MIN(s.sale_date) AS first_sale_date,
    MAX(s.sale_date) AS most_recent_sale,
    CASE
        WHEN SUM(s.amount) >= 50000 THEN 'Gold'
        WHEN SUM(s.amount) >= 20000 THEN 'Silver'
        ELSE 'Bronze'
    END AS performance_tier
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN sales s ON e.employee_id = s.employee_id
GROUP BY e.first_name, e.last_name, d.department_name;
```

```sql
SELECT * FROM sales_dashboard;
```

**Result:**

```
  salesperson   | department_name | total_deals | total_revenue | avg_deal_size | best_deal | first_sale_date | most_recent_sale | performance_tier
----------------+-----------------+-------------+---------------+---------------+-----------+-----------------+------------------+-----------------
 Edward Wilson  | Sales           |           4 |         63500 |      15875.00 |     22000 | 2024-01-15      | 2024-03-25       | Gold
 Fiona Clark    | Sales           |           4 |         20000 |       5000.00 |      7500 | 2024-01-05      | 2024-03-15       | Silver
(2 rows)
```

Now simple queries give you rich insights:

```sql
-- Who are the gold performers?
SELECT salesperson, total_revenue
FROM sales_dashboard
WHERE performance_tier = 'Gold';

-- What is the average deal size per tier?
SELECT performance_tier, ROUND(AVG(avg_deal_size), 2) AS avg_across_reps
FROM sales_dashboard
GROUP BY performance_tier;
```

---

## Listing and Inspecting Views

To see all views in your schema:

```sql
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'VIEW';
```

To see the definition of a specific view:

```sql
SELECT pg_get_viewdef('employee_directory', TRUE);
```

Or using the psql shortcut:

```
\dv          -- List all views
\d+ view_name  -- Show view details
```

---

## Common Mistakes

### Mistake 1: Thinking Views Store Data

```
-- WRONG mental model:
-- "I created a view, so the data is now copied."

-- CORRECT mental model:
-- "I saved a query. It runs fresh every time I use it."
```

Regular views store only the query definition, not the data. Only materialized views store data.

### Mistake 2: Not Refreshing Materialized Views

```sql
-- You add new data to the tables
INSERT INTO sales (employee_id, sale_date, amount, product_name)
VALUES (5, '2024-04-15', 25000, 'Enterprise License');

-- But forget to refresh
-- The materialized view still shows stale data!

-- Fix: Always refresh after data changes
REFRESH MATERIALIZED VIEW sales_summary;
```

### Mistake 3: Creating Views for One-Time Queries

Not every query needs to be a view. If you only use a query once, just run it directly. Views are for queries you reuse repeatedly or need to share.

### Mistake 4: Trying to CREATE OR REPLACE with Removed Columns

```sql
-- Original view has: first_name, last_name, email
CREATE OR REPLACE VIEW my_view AS
SELECT first_name, last_name  -- Removed email!
FROM employees;

-- ERROR: cannot drop columns from view
```

Use DROP VIEW and then CREATE VIEW instead.

### Mistake 5: Forgetting CASCADE When Dropping Views with Dependencies

```sql
-- view_b depends on view_a
DROP VIEW view_a;
-- ERROR: cannot drop view view_a because other objects depend on it

-- Fix:
DROP VIEW view_a CASCADE;
-- This also drops view_b
```

---

## Best Practices

1. **Name views descriptively.** Use names like `active_employee_directory` or `monthly_sales_summary` instead of `v1` or `temp_view`.

2. **Use views for security.** Grant users access to views instead of tables. This lets you control exactly which columns and rows they can see.

3. **Use materialized views for expensive queries.** If a query takes seconds or minutes and the data does not change every second, a materialized view can make it instant.

4. **Schedule materialized view refreshes.** Set up a cron job or scheduled task to refresh your materialized views at appropriate intervals (hourly, daily, etc.).

5. **Do not nest views too deeply.** A view that queries a view that queries another view becomes hard to debug and may have performance implications. Keep nesting to two or three levels at most.

6. **Document your views.** Use `COMMENT ON VIEW` to add descriptions that help other developers understand the purpose of each view.

```sql
COMMENT ON VIEW employee_directory IS
    'Public employee directory showing active employees with department info. Excludes salaries and internal IDs.';
```

---

## Quick Summary

```
+---------------------------+------------------------------------------+
| Feature                   | Description                              |
+---------------------------+------------------------------------------+
| CREATE VIEW               | Save a query as a virtual table          |
+---------------------------+------------------------------------------+
| SELECT FROM view          | Query a view like a regular table        |
+---------------------------+------------------------------------------+
| CREATE OR REPLACE VIEW    | Modify a view (can add columns only)     |
+---------------------------+------------------------------------------+
| DROP VIEW                 | Remove a view                            |
+---------------------------+------------------------------------------+
| WITH CHECK OPTION         | Prevent inserts/updates that violate     |
|                           | the view's WHERE clause                  |
+---------------------------+------------------------------------------+
| CREATE MATERIALIZED VIEW  | Store query results on disk for speed    |
+---------------------------+------------------------------------------+
| REFRESH MATERIALIZED VIEW | Update cached results in a mat. view     |
+---------------------------+------------------------------------------+
```

---

## Key Points

- A **view** is a saved query, not a stored copy of data. It runs fresh every time you query it.
- Views act like **virtual tables**. You can SELECT from them, filter them, and join them with other tables.
- Use views for **security** (hide sensitive columns), **simplicity** (save complex queries), and **abstraction** (insulate from schema changes).
- **CREATE OR REPLACE VIEW** lets you modify a view but only by adding columns. You cannot remove or reorder existing columns.
- **WITH CHECK OPTION** prevents data modifications through a view that would make the row invisible in the view.
- **Materialized views** physically store query results for faster access. They require explicit **REFRESH** to update.
- Use **REFRESH MATERIALIZED VIEW CONCURRENTLY** (with a unique index) to avoid locking during refresh.
- Do not create views for queries you only use once. Views are for reusable, shared queries.

---

## Practice Questions

1. What is the difference between a regular view and a materialized view? When would you choose one over the other?

2. You create a view with `WHERE status = 'active'`. A user inserts a row through the view with `status = 'inactive'`. What happens without WITH CHECK OPTION? What happens with it?

3. Can you create an index on a regular view? What about a materialized view? Why?

4. You have a view that three other views depend on. What happens when you run `DROP VIEW my_view`? How do you force the drop?

5. A materialized view was refreshed yesterday. Since then, 1,000 new rows were added to the underlying table. When you query the materialized view, will you see the new rows? Why or why not?

---

## Exercises

### Exercise 1: Employee Directory View

Create a view called `department_roster` that shows each employee's full name (first and last combined), email, department name, and the number of years they have been with the company (calculated from hire_date). Only include active employees. Then write a query that uses this view to find all employees in Engineering who have been with the company for more than 3 years.

### Exercise 2: Materialized Sales Summary

Create a materialized view called `quarterly_sales` that shows the year, quarter number, total number of sales, total revenue, and average deal size for each quarter. Then add a new sale to the sales table and demonstrate the difference between querying before and after a REFRESH.

### Exercise 3: Security Views

Create three views for different access levels:
1. `public_staff_list` - Shows only first names and department names of active employees.
2. `manager_view` - Shows full names, departments, hire dates, and years of service, but not salaries.
3. `hr_full_view` - Shows everything including salaries, with a CASE expression that labels salary bands as "Executive" (>= 100,000), "Senior" (>= 75,000), "Mid" (>= 55,000), and "Entry."

Query each view to verify they show the correct level of detail.

---

## What Is Next?

Now that you know how to create views to simplify and secure your queries, the next chapter will introduce **Indexes**. Indexes are the key to making your queries fast. Just like a book index helps you find a topic without reading every page, a database index helps PostgreSQL find rows without scanning every record. You will learn when to create indexes, which types to use, and how to read query plans to understand performance.
