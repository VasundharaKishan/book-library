# Chapter 11: GROUP BY and HAVING — Aggregating by Category

## What You Will Learn

In this chapter, you will learn how to:

- Group rows by one or more columns using GROUP BY
- Use aggregate functions (COUNT, SUM, AVG, MIN, MAX) with GROUP BY
- Group by multiple columns at once
- Filter groups using HAVING (vs. WHERE which filters rows)
- Combine GROUP BY with ORDER BY for sorted summaries
- Avoid the most common GROUP BY mistake (non-aggregated columns in SELECT)
- Write practical group-based queries

## Why This Chapter Matters

In the previous chapter, you learned aggregate functions. But you could only summarize the entire table at once, or write separate queries for each department. That is like having a calculator that only shows one total — you would have to manually run it once for each category.

GROUP BY is the tool that lets you say, "Calculate the average salary FOR EACH department" in a single query. It takes a pile of mixed data and organizes it into groups, then runs your aggregate functions on each group separately.

Think of it like sorting a box of mixed LEGO bricks by color, then counting how many bricks you have of each color. Without GROUP BY, you can only count the total number of bricks. With GROUP BY, you get a breakdown: 15 red, 22 blue, 8 green, and so on.

GROUP BY is essential for any kind of reporting: sales by region, orders by month, employees by department, revenue by product category. If you have ever seen a summary table or a bar chart, there was probably a GROUP BY query behind it.

---

## Our Practice Table

We continue with the employees table:

```
+----+------------------+-------------+-----------+------------+
| id | name             | department  | salary    | hire_date  |
+----+------------------+-------------+-----------+------------+
|  1 | Alice Johnson    | Engineering | 85000.00  | 2020-03-15 |
|  2 | Bob Smith        | Marketing   | 62000.00  | 2019-07-22 |
|  3 | Carol Williams   | Engineering | 92000.00  | 2018-11-01 |
|  4 | David Brown      | Sales       | 58000.00  | 2021-01-10 |
|  5 | Eva Martinez     | Marketing   | 65000.00  | 2020-09-05 |
|  6 | Frank Lee        | Engineering | 78000.00  | 2022-02-14 |
|  7 | Grace Kim        | Sales       | 61000.00  | 2019-04-30 |
|  8 | Henry Wilson     | HR          | 55000.00  | 2021-06-18 |
|  9 | Ivy Chen         | HR          | 59000.00  | 2020-12-01 |
| 10 | Jack Davis       | Sales       | 63000.00  | 2023-03-20 |
+----+------------------+-------------+-----------+------------+
```

---

## GROUP BY — The Concept

GROUP BY takes all the rows and puts them into groups based on a column's value. Then, any aggregate functions in your SELECT run once per group instead of once for the entire table.

### Visualizing Groups

Here is what happens when you GROUP BY department:

```
  Before GROUP BY (all mixed together):
  +------------------+-------------+-----------+
  | Alice Johnson    | Engineering | 85000.00  |
  | Bob Smith        | Marketing   | 62000.00  |
  | Carol Williams   | Engineering | 92000.00  |
  | David Brown      | Sales       | 58000.00  |
  | Eva Martinez     | Marketing   | 65000.00  |
  | Frank Lee        | Engineering | 78000.00  |
  | Grace Kim        | Sales       | 61000.00  |
  | Henry Wilson     | HR          | 55000.00  |
  | Ivy Chen         | HR          | 59000.00  |
  | Jack Davis       | Sales       | 63000.00  |
  +------------------+-------------+-----------+

  After GROUP BY department (sorted into buckets):

  +----- Engineering -----+   +----- HR -----+
  | Alice    | 85000.00   |   | Henry | 55000 |
  | Carol    | 92000.00   |   | Ivy   | 59000 |
  | Frank    | 78000.00   |   +-------+-------+
  +----------+------------+
                               +----- Marketing -----+
  +----- Sales -----+         | Bob  | 62000         |
  | David | 58000   |         | Eva  | 65000         |
  | Grace | 61000   |         +------+---------------+
  | Jack  | 63000   |
  +-------+---------+

  Then aggregates run on EACH bucket:
  Engineering: COUNT = 3, AVG = 85000
  HR:          COUNT = 2, AVG = 57000
  Marketing:   COUNT = 2, AVG = 63500
  Sales:       COUNT = 3, AVG = 60666.67
```

---

## GROUP BY with COUNT

The simplest GROUP BY query — count how many employees are in each department:

```sql
SELECT
    department,
    COUNT(*) AS employee_count
FROM employees
GROUP BY department;
```

**Line-by-line breakdown:**

- `SELECT department` — Show the department name (this is the column we are grouping by).
- `COUNT(*) AS employee_count` — Count the rows in each group.
- `FROM employees` — The table.
- `GROUP BY department` — Create groups based on unique department values.

**Result:**

```
+-------------+----------------+
| department  | employee_count |
+-------------+----------------+
| Engineering |              3 |
| HR          |              2 |
| Marketing   |              2 |
| Sales       |              3 |
+-------------+----------------+
(4 rows)
```

One row per group, not one row per employee. The result has 4 rows because there are 4 unique departments.

---

## GROUP BY with Other Aggregates

### Average Salary by Department

```sql
SELECT
    department,
    ROUND(AVG(salary), 2) AS avg_salary
FROM employees
GROUP BY department;
```

**Result:**

```
+-------------+------------+
| department  | avg_salary |
+-------------+------------+
| Engineering |   85000.00 |
| HR          |   57000.00 |
| Marketing   |   63500.00 |
| Sales       |   60666.67 |
+-------------+------------+
(4 rows)
```

In one query, you can see that Engineering has the highest average salary and HR has the lowest.

### Total Salary Budget by Department

```sql
SELECT
    department,
    SUM(salary) AS total_budget,
    COUNT(*)    AS headcount
FROM employees
GROUP BY department;
```

**Result:**

```
+-------------+--------------+-----------+
| department  | total_budget | headcount |
+-------------+--------------+-----------+
| Engineering |    255000.00 |         3 |
| HR          |    114000.00 |         2 |
| Marketing   |    127000.00 |         2 |
| Sales       |    182000.00 |         3 |
+-------------+--------------+-----------+
(4 rows)
```

### Complete Department Summary

You can use multiple aggregates with GROUP BY:

```sql
SELECT
    department,
    COUNT(*)              AS headcount,
    SUM(salary)           AS total_salary,
    ROUND(AVG(salary), 2) AS avg_salary,
    MIN(salary)           AS min_salary,
    MAX(salary)           AS max_salary
FROM employees
GROUP BY department;
```

**Result:**

```
+-------------+-----------+--------------+------------+------------+------------+
| department  | headcount | total_salary | avg_salary | min_salary | max_salary |
+-------------+-----------+--------------+------------+------------+------------+
| Engineering |         3 |    255000.00 |   85000.00 |   78000.00 |   92000.00 |
| HR          |         2 |    114000.00 |   57000.00 |   55000.00 |   59000.00 |
| Marketing   |         2 |    127000.00 |   63500.00 |   62000.00 |   65000.00 |
| Sales       |         3 |    182000.00 |   60666.67 |   58000.00 |   63000.00 |
+-------------+-----------+--------------+------------+------------+------------+
(4 rows)
```

This is a complete departmental salary report in a single query. This is the power of GROUP BY.

---

## GROUP BY with Multiple Columns

You can group by more than one column. Each unique combination of values becomes its own group.

Let us add a second table to make this more interesting:

```sql
CREATE TABLE sales (
    id          SERIAL PRIMARY KEY,
    product     VARCHAR(50),
    category    VARCHAR(50),
    amount      NUMERIC(10,2),
    sale_date   DATE
);

INSERT INTO sales (product, category, amount, sale_date) VALUES
    ('Laptop',     'Electronics', 1200.00, '2024-01-15'),
    ('Mouse',      'Electronics',   25.00, '2024-01-15'),
    ('Laptop',     'Electronics', 1200.00, '2024-01-20'),
    ('Desk Chair', 'Furniture',    350.00, '2024-01-18'),
    ('Desk',       'Furniture',    500.00, '2024-01-22'),
    ('Mouse',      'Electronics',   25.00, '2024-02-01'),
    ('Keyboard',   'Electronics',   75.00, '2024-02-05'),
    ('Bookshelf',  'Furniture',    200.00, '2024-02-10'),
    ('Laptop',     'Electronics', 1200.00, '2024-02-15'),
    ('Desk Chair', 'Furniture',    350.00, '2024-02-20');
```

### Sales by Category

```sql
SELECT
    category,
    COUNT(*)    AS total_sales,
    SUM(amount) AS total_revenue
FROM sales
GROUP BY category;
```

**Result:**

```
+-------------+-------------+---------------+
| category    | total_sales | total_revenue |
+-------------+-------------+---------------+
| Electronics |           6 |       3725.00 |
| Furniture   |           4 |       1400.00 |
+-------------+-------------+---------------+
(2 rows)
```

### Sales by Category and Product

```sql
SELECT
    category,
    product,
    COUNT(*)    AS times_sold,
    SUM(amount) AS total_revenue
FROM sales
GROUP BY category, product
ORDER BY category, total_revenue DESC;
```

**Result:**

```
+-------------+------------+------------+---------------+
| category    | product    | times_sold | total_revenue |
+-------------+------------+------------+---------------+
| Electronics | Laptop     |          3 |       3600.00 |
| Electronics | Keyboard   |          1 |         75.00 |
| Electronics | Mouse      |          2 |         50.00 |
| Furniture   | Desk       |          1 |        500.00 |
| Furniture   | Desk Chair |          2 |        700.00 |
| Furniture   | Bookshelf  |          1 |        200.00 |
+-------------+------------+------------+---------------+
(6 rows)
```

With two GROUP BY columns, each unique combination of category + product becomes its own group. Laptops in Electronics is one group, Mice in Electronics is another, and so on.

---

## GROUP BY + ORDER BY

GROUP BY produces groups but does not guarantee their order. Add ORDER BY to sort the grouped results:

```sql
SELECT
    department,
    ROUND(AVG(salary), 2) AS avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;
```

**Result:**

```
+-------------+------------+
| department  | avg_salary |
+-------------+------------+
| Engineering |   85000.00 |
| Marketing   |   63500.00 |
| Sales       |   60666.67 |
| HR          |   57000.00 |
+-------------+------------+
(4 rows)
```

Now the departments are sorted by average salary, highest first. You can quickly see that Engineering pays the most on average.

---

## HAVING — Filtering Groups

WHERE filters individual rows BEFORE grouping. But what if you want to filter AFTER grouping? For example, "Show me only departments that have more than 2 employees."

That is what HAVING does. It filters groups, not rows.

### WHERE vs. HAVING

```
  WHERE:   Filters individual rows  BEFORE they are grouped
  HAVING:  Filters groups           AFTER  they are formed
```

```
  +-------------------+
  |   All rows        |
  +--------+----------+
           |
  WHERE (filter rows)
           |
           v
  +-------------------+
  |  Filtered rows    |
  +--------+----------+
           |
  GROUP BY (create groups)
           |
           v
  +-------------------+
  |  Groups with      |
  |  aggregates       |
  +--------+----------+
           |
  HAVING (filter groups)
           |
           v
  +-------------------+
  |  Filtered groups  |
  +-------------------+
```

### Example: Departments with More Than 2 Employees

```sql
SELECT
    department,
    COUNT(*) AS employee_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 2;
```

**Line-by-line breakdown:**

- `GROUP BY department` — Create groups by department.
- `HAVING COUNT(*) > 2` — After grouping, keep only groups where the count is greater than 2.

**Result:**

```
+-------------+----------------+
| department  | employee_count |
+-------------+----------------+
| Engineering |              3 |
| Sales       |              3 |
+-------------+----------------+
(2 rows)
```

HR (2 employees) and Marketing (2 employees) are excluded because they do not have more than 2 employees.

### Example: Departments with High Average Salary

```sql
SELECT
    department,
    ROUND(AVG(salary), 2) AS avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 60000
ORDER BY avg_salary DESC;
```

**Result:**

```
+-------------+------------+
| department  | avg_salary |
+-------------+------------+
| Engineering |   85000.00 |
| Marketing   |   63500.00 |
| Sales       |   60666.67 |
+-------------+------------+
(3 rows)
```

HR is excluded because its average salary ($57,000) is below $60,000.

### Combining WHERE and HAVING

You can use both WHERE and HAVING in the same query. WHERE filters rows first, then GROUP BY groups the remaining rows, then HAVING filters the groups:

```sql
SELECT
    department,
    COUNT(*)              AS headcount,
    ROUND(AVG(salary), 2) AS avg_salary
FROM employees
WHERE hire_date >= '2020-01-01'
GROUP BY department
HAVING COUNT(*) >= 2
ORDER BY avg_salary DESC;
```

**Line-by-line breakdown:**

- `WHERE hire_date >= '2020-01-01'` — First, keep only employees hired in 2020 or later.
- `GROUP BY department` — Group the remaining employees by department.
- `HAVING COUNT(*) >= 2` — Keep only groups with 2 or more employees.

**Step-by-step execution:**

```
  Step 1: WHERE hire_date >= '2020-01-01'
  Keeps: Alice, David, Eva, Frank, Henry, Ivy, Jack  (7 rows)
  Removes: Bob (2019), Carol (2018), Grace (2019)

  Step 2: GROUP BY department
  Engineering: Alice, Frank          (2 employees)
  HR:          Henry, Ivy            (2 employees)
  Marketing:   Eva                   (1 employee)
  Sales:       David, Jack           (2 employees)

  Step 3: HAVING COUNT(*) >= 2
  Keeps: Engineering (2), HR (2), Sales (2)
  Removes: Marketing (1)
```

**Result:**

```
+-------------+-----------+------------+
| department  | headcount | avg_salary |
+-------------+-----------+------------+
| Engineering |         2 |   81500.00 |
| Sales       |         2 |   60500.00 |
| HR          |         2 |   57000.00 |
+-------------+-----------+------------+
(3 rows)
```

---

## The Critical Mistake: Non-Aggregated Columns in SELECT

This is the most common GROUP BY error. Every column in your SELECT must either:

1. Be in the GROUP BY clause, OR
2. Be inside an aggregate function (COUNT, SUM, AVG, etc.)

### The Error

```sql
-- WRONG: "name" is not in GROUP BY and not inside an aggregate
SELECT
    department,
    name,           -- Which name? There are multiple per department!
    AVG(salary)
FROM employees
GROUP BY department;
```

```
ERROR:  column "employees.name" must appear in the GROUP BY clause
        or be used in an aggregate function
```

### Why This Happens

When you GROUP BY department, PostgreSQL collapses the Engineering group from 3 rows (Alice, Carol, Frank) into 1 row. If you also SELECT name, which of those 3 names should it show? PostgreSQL does not know and refuses to guess.

```
  Engineering group:
  +------------------+-----------+
  | Alice Johnson    | 85000.00  |   Which name should
  | Carol Williams   | 92000.00  |   appear in the result?
  | Frank Lee        | 78000.00  |   PostgreSQL says: ERROR!
  +------------------+-----------+

  The average is clear: 85000.00
  But the name is ambiguous.
```

### How to Fix It

**Option 1:** Remove the non-aggregated column:

```sql
SELECT
    department,
    ROUND(AVG(salary), 2) AS avg_salary
FROM employees
GROUP BY department;
```

**Option 2:** Add the column to GROUP BY (changes the grouping):

```sql
SELECT
    department,
    name,
    salary
FROM employees
GROUP BY department, name, salary;
```

But this gives you one row per employee again, defeating the purpose of grouping.

**Option 3:** Use an aggregate function on the column:

```sql
SELECT
    department,
    MIN(name)             AS first_name_alphabetically,
    ROUND(AVG(salary), 2) AS avg_salary
FROM employees
GROUP BY department;
```

**Result:**

```
+-------------+----------------------------+------------+
| department  | first_name_alphabetically  | avg_salary |
+-------------+----------------------------+------------+
| Engineering | Alice Johnson              |   85000.00 |
| HR          | Henry Wilson               |   57000.00 |
| Marketing   | Bob Smith                  |   63500.00 |
| Sales       | David Brown                |   60666.67 |
+-------------+----------------------------+------------+
```

---

## Practical Examples

### Example 1: Hiring Trends by Year

```sql
SELECT
    EXTRACT(YEAR FROM hire_date) AS hire_year,
    COUNT(*)                     AS hires
FROM employees
GROUP BY EXTRACT(YEAR FROM hire_date)
ORDER BY hire_year;
```

**Result:**

```
+-----------+-------+
| hire_year | hires |
+-----------+-------+
|      2018 |     1 |
|      2019 |     2 |
|      2020 |     3 |
|      2021 |     2 |
|      2022 |     1 |
|      2023 |     1 |
+-----------+-------+
(6 rows)
```

2020 was the busiest hiring year with 3 new employees.

### Example 2: Sales Report by Category

```sql
SELECT
    category,
    COUNT(*)              AS transactions,
    SUM(amount)           AS total_revenue,
    ROUND(AVG(amount), 2) AS avg_transaction,
    MIN(amount)           AS smallest_sale,
    MAX(amount)           AS largest_sale
FROM sales
GROUP BY category
ORDER BY total_revenue DESC;
```

**Result:**

```
+-------------+--------------+---------------+-----------------+---------------+--------------+
| category    | transactions | total_revenue | avg_transaction | smallest_sale | largest_sale |
+-------------+--------------+---------------+-----------------+---------------+--------------+
| Electronics |            6 |       3725.00 |          620.83 |         25.00 |      1200.00 |
| Furniture   |            4 |       1400.00 |          350.00 |        200.00 |       500.00 |
+-------------+--------------+---------------+-----------------+---------------+--------------+
(2 rows)
```

### Example 3: Finding Departments That Need Attention

"Show me departments where the salary range (max - min) is greater than 10,000."

```sql
SELECT
    department,
    MIN(salary)              AS min_salary,
    MAX(salary)              AS max_salary,
    MAX(salary) - MIN(salary) AS salary_spread
FROM employees
GROUP BY department
HAVING MAX(salary) - MIN(salary) > 10000
ORDER BY salary_spread DESC;
```

**Result:**

```
+-------------+------------+------------+---------------+
| department  | min_salary | max_salary | salary_spread |
+-------------+------------+------------+---------------+
| Engineering |   78000.00 |   92000.00 |      14000.00 |
+-------------+------------+------------+---------------+
(1 row)
```

Only Engineering has a salary spread greater than $10,000. This might indicate salary inequality worth investigating.

---

## The Complete Query Execution Order

Here is the full picture of how PostgreSQL processes a query with GROUP BY and HAVING:

```
  Writing Order:           Execution Order:
  1. SELECT                1. FROM         (find the table)
  2. FROM                  2. WHERE        (filter individual rows)
  3. WHERE                 3. GROUP BY     (form groups)
  4. GROUP BY              4. HAVING       (filter groups)
  5. HAVING                5. SELECT       (pick columns & compute)
  6. ORDER BY              6. ORDER BY     (sort results)
  7. LIMIT/OFFSET          7. LIMIT/OFFSET (cut to size)
```

This is why:
- WHERE cannot use aggregate functions (it runs before GROUP BY)
- HAVING can use aggregate functions (it runs after GROUP BY)
- ORDER BY can use aliases (it runs after SELECT)

---

## Common Mistakes

### Mistake 1: Using WHERE Instead of HAVING for Aggregate Conditions

```sql
-- Wrong: WHERE runs before GROUP BY, so it cannot filter aggregates
SELECT department, COUNT(*)
FROM employees
WHERE COUNT(*) > 2        -- ERROR!
GROUP BY department;

-- Right: Use HAVING for aggregate conditions
SELECT department, COUNT(*)
FROM employees
GROUP BY department
HAVING COUNT(*) > 2;
```

### Mistake 2: Non-Aggregated Column in SELECT

```sql
-- Wrong: salary is not in GROUP BY and not in an aggregate
SELECT department, salary, AVG(salary)
FROM employees
GROUP BY department;

-- Right: Either add salary to GROUP BY or use it in an aggregate
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;
```

### Mistake 3: Using HAVING When WHERE Would Work

```sql
-- Works but inefficient: HAVING filters after grouping
SELECT department, COUNT(*) AS cnt
FROM employees
GROUP BY department
HAVING department = 'Sales';

-- Better: WHERE filters before grouping (fewer rows to process)
SELECT department, COUNT(*) AS cnt
FROM employees
WHERE department = 'Sales'
GROUP BY department;
```

Use WHERE for conditions on individual row values. Use HAVING only for conditions on aggregate results.

### Mistake 4: Forgetting GROUP BY with Aggregates

```sql
-- Wrong: department is not aggregated and GROUP BY is missing
SELECT department, AVG(salary)
FROM employees;
-- ERROR!

-- Right: Add GROUP BY
SELECT department, AVG(salary)
FROM employees
GROUP BY department;
```

---

## Best Practices

1. **Use WHERE for row-level filters, HAVING for group-level filters.** WHERE is more efficient because it reduces the number of rows before grouping.

2. **Always pair GROUP BY with aggregates.** A GROUP BY without any aggregate function in SELECT is technically valid but usually means something is wrong.

3. **Include the GROUP BY column in SELECT.** While not required, it makes results readable:
   ```sql
   -- Confusing: What do these numbers refer to?
   SELECT COUNT(*), AVG(salary) FROM employees GROUP BY department;

   -- Clear: Now we know which department each row represents
   SELECT department, COUNT(*), AVG(salary) FROM employees GROUP BY department;
   ```

4. **Add ORDER BY for predictable results.** GROUP BY does not guarantee any particular order.

5. **Use aliases for aggregate columns.** `COUNT(*)` as a column header is not very informative. `employee_count` is much better.

---

## Quick Summary

```
+---------------------+--------------------------------------------------+
| Concept             | Example                                          |
+---------------------+--------------------------------------------------+
| Group by 1 column   | GROUP BY department                              |
| Group by 2 columns  | GROUP BY category, product                       |
| Count per group     | SELECT dept, COUNT(*) ... GROUP BY dept           |
| Average per group   | SELECT dept, AVG(salary) ... GROUP BY dept        |
| Filter groups       | HAVING COUNT(*) > 2                              |
| WHERE + HAVING      | WHERE salary > 50000 ... HAVING AVG(salary) > 60k|
| Sorted groups       | GROUP BY dept ORDER BY AVG(salary) DESC           |
+---------------------+--------------------------------------------------+
```

---

## Key Points

- GROUP BY divides rows into groups based on column values, then aggregates run on each group.
- Every non-aggregated column in SELECT must appear in the GROUP BY clause.
- You can GROUP BY multiple columns — each unique combination becomes a group.
- WHERE filters individual rows BEFORE grouping. HAVING filters groups AFTER grouping.
- Use WHERE for row-level conditions (department, salary, date). Use HAVING for aggregate conditions (COUNT, AVG, SUM).
- GROUP BY does not guarantee order — add ORDER BY if you need sorted results.
- GROUP BY + aggregate functions are the foundation of all summary reports.

---

## Practice Questions

1. Write a query to count how many employees are in each department. Sort by count, highest first.

2. Write a query to find the average salary for each department. Only show departments where the average salary is above $60,000.

3. What is wrong with this query?
   ```sql
   SELECT department, name, COUNT(*)
   FROM employees
   GROUP BY department;
   ```

4. Explain the difference between these two queries:
   ```sql
   -- Query A
   SELECT department, COUNT(*)
   FROM employees
   WHERE salary > 60000
   GROUP BY department;

   -- Query B
   SELECT department, COUNT(*)
   FROM employees
   GROUP BY department
   HAVING COUNT(*) > 2;
   ```

5. Can you use both WHERE and HAVING in the same query? If yes, write a query that uses both.

---

## Exercises

### Exercise 1: Department Budget Report

Write a single query that shows for each department:
- Department name
- Number of employees
- Total salary budget
- Average salary (rounded to 2 decimal places)
- Highest salary

Sort the results by total salary budget, highest first.

### Exercise 2: Sales Analysis

Using the sales table created in this chapter, write queries to answer:
1. How many transactions occurred for each product?
2. What is the total revenue per category?
3. Which products generated more than $500 in total revenue?

### Exercise 3: Selective Grouping

Write a query that:
1. Excludes employees hired before 2020 (use WHERE)
2. Groups the remaining employees by department
3. Only shows departments with 2 or more recent hires (use HAVING)
4. Shows the department name, count of recent hires, and their average salary
5. Sorts by average salary descending

---

## What Is Next?

So far, all your queries have worked with a single table. But real databases spread data across multiple tables. Employees are in one table, departments in another, and projects in a third. In the next chapter, you will learn about **JOINs** — the technique for combining data from multiple tables into a single result. Joins are one of the most powerful features of relational databases and the key reason why the relational model has dominated data storage for decades.
