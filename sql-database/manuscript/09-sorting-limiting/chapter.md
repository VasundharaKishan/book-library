# Chapter 9: Sorting and Limiting Results

## What You Will Learn

In this chapter, you will learn how to:

- Sort results in ascending and descending order with ORDER BY
- Sort by multiple columns
- Control where NULL values appear with NULLS FIRST and NULLS LAST
- Limit the number of rows returned with LIMIT
- Skip rows with OFFSET for pagination
- Use FETCH FIRST as an alternative to LIMIT
- Combine WHERE, ORDER BY, and LIMIT for powerful top-N queries

## Why This Chapter Matters

Imagine you search for "best restaurants near me" and Google gives you 10,000 results in random order. Not very helpful, right? You want them sorted by rating and you only want to see the top 10.

That is exactly what ORDER BY and LIMIT do for your database queries. ORDER BY puts your results in a logical order — alphabetically, by salary, by date, whatever makes sense. LIMIT controls how many rows you see. Together, they turn a flood of data into a neatly organized, manageable result.

These are the tools you will use every time you build a paginated list (like search results on a website), a leaderboard (top sellers, highest scores), or a report sorted by any criterion.

---

## Our Practice Table

We continue with the employees table from previous chapters:

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

## ORDER BY — Sorting Results

Without ORDER BY, PostgreSQL returns rows in no guaranteed order. It might return them in the order they were inserted, or it might not. You should never rely on the default order.

### Ascending Order (Default)

```sql
SELECT name, salary
FROM employees
ORDER BY salary;
```

**Line-by-line breakdown:**

- `SELECT name, salary` — The columns we want.
- `FROM employees` — The table.
- `ORDER BY salary` — Sort the results by the salary column. The default direction is ascending (smallest to largest).

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Henry Wilson     | 55000.00  |
| David Brown      | 58000.00  |
| Ivy Chen         | 59000.00  |
| Grace Kim        | 61000.00  |
| Bob Smith        | 62000.00  |
| Jack Davis       | 63000.00  |
| Eva Martinez     | 65000.00  |
| Frank Lee        | 78000.00  |
| Alice Johnson    | 85000.00  |
| Carol Williams   | 92000.00  |
+------------------+-----------+
(10 rows)
```

You can also write `ORDER BY salary ASC` to be explicit. ASC stands for "ascending" — from low to high, from A to Z, from oldest to newest.

### Descending Order

```sql
SELECT name, salary
FROM employees
ORDER BY salary DESC;
```

**Line-by-line breakdown:**

- `ORDER BY salary DESC` — DESC stands for "descending" — from high to low, from Z to A, from newest to oldest.

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Carol Williams   | 92000.00  |
| Alice Johnson    | 85000.00  |
| Frank Lee        | 78000.00  |
| Eva Martinez     | 65000.00  |
| Jack Davis       | 63000.00  |
| Bob Smith        | 62000.00  |
| Grace Kim        | 61000.00  |
| Ivy Chen         | 59000.00  |
| David Brown      | 58000.00  |
| Henry Wilson     | 55000.00  |
+------------------+-----------+
(10 rows)
```

Think of ASC/DESC like an elevator. ASC goes up (1, 2, 3...). DESC goes down (10, 9, 8...).

### Sorting Text Alphabetically

```sql
SELECT name, department
FROM employees
ORDER BY name;
```

**Result:**

```
+------------------+-------------+
| name             | department  |
+------------------+-------------+
| Alice Johnson    | Engineering |
| Bob Smith        | Marketing   |
| Carol Williams   | Engineering |
| David Brown      | Sales       |
| Eva Martinez     | Marketing   |
| Frank Lee        | Engineering |
| Grace Kim        | Sales       |
| Henry Wilson     | HR          |
| Ivy Chen         | HR          |
| Jack Davis       | Sales       |
+------------------+-------------+
(10 rows)
```

Text is sorted alphabetically. Uppercase and lowercase sorting depends on your database's collation settings, but in most PostgreSQL setups, the sort is case-insensitive alphabetical.

### Sorting by Date

```sql
SELECT name, hire_date
FROM employees
ORDER BY hire_date;
```

**Result:**

```
+------------------+------------+
| name             | hire_date  |
+------------------+------------+
| Carol Williams   | 2018-11-01 |
| Grace Kim        | 2019-04-30 |
| Bob Smith        | 2019-07-22 |
| Alice Johnson    | 2020-03-15 |
| Eva Martinez     | 2020-09-05 |
| Ivy Chen         | 2020-12-01 |
| David Brown      | 2021-01-10 |
| Henry Wilson     | 2021-06-18 |
| Frank Lee        | 2022-02-14 |
| Jack Davis       | 2023-03-20 |
+------------------+------------+
(10 rows)
```

Earliest hire date first. Use `DESC` to see the most recent hires first.

---

## Sorting by Multiple Columns

What happens when two employees have the same value in the sort column? You can add a second (or third) column to break ties.

```sql
SELECT name, department, salary
FROM employees
ORDER BY department, salary DESC;
```

**Line-by-line breakdown:**

- `ORDER BY department` — First, sort by department alphabetically (ascending).
- `, salary DESC` — Within each department, sort by salary from highest to lowest.

**Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| Carol Williams   | Engineering | 92000.00  |
| Alice Johnson    | Engineering | 85000.00  |
| Frank Lee        | Engineering | 78000.00  |
| Ivy Chen         | HR          | 59000.00  |
| Henry Wilson     | HR          | 55000.00  |
| Eva Martinez     | Marketing   | 65000.00  |
| Bob Smith        | Marketing   | 62000.00  |
| Jack Davis       | Sales       | 63000.00  |
| Grace Kim        | Sales       | 61000.00  |
| David Brown      | Sales       | 58000.00  |
+------------------+-------------+-----------+
(10 rows)
```

Notice: departments are in alphabetical order (Engineering, HR, Marketing, Sales), and within each department, salaries go from highest to lowest.

Think of it like sorting a deck of cards: first sort by suit (Hearts, Diamonds, Clubs, Spades), then within each suit, sort by value (King, Queen, Jack, 10...).

```
  Sort by department (ascending)
  |
  |   Then by salary (descending) within each department
  |   |
  v   v
  Engineering  92000  (Carol)
  Engineering  85000  (Alice)
  Engineering  78000  (Frank)
  HR           59000  (Ivy)
  HR           55000  (Henry)
  Marketing    65000  (Eva)
  Marketing    62000  (Bob)
  Sales        63000  (Jack)
  Sales        61000  (Grace)
  Sales        58000  (David)
```

Each column in the ORDER BY can have its own ASC or DESC direction.

---

## NULLS FIRST and NULLS LAST

When a column contains NULL values, where should they appear in the sorted results? PostgreSQL gives you control:

- By default, NULLs come **last** in ascending order.
- By default, NULLs come **first** in descending order.

You can override this:

```sql
-- NULLs at the beginning
SELECT name, department
FROM employees
ORDER BY department NULLS FIRST;

-- NULLs at the end (explicit)
SELECT name, department
FROM employees
ORDER BY department NULLS LAST;
```

This is especially useful in real applications where missing data is common. For example, if you are sorting customers by their last purchase date, you might want customers who have never purchased (NULL date) to appear at the end:

```sql
SELECT customer_name, last_purchase_date
FROM customers
ORDER BY last_purchase_date DESC NULLS LAST;
```

This way, active customers appear first, and customers with no purchase history appear at the bottom.

---

## LIMIT — Controlling How Many Rows You Get

LIMIT restricts the number of rows returned:

```sql
SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 3;
```

**Line-by-line breakdown:**

- `ORDER BY salary DESC` — Sort by salary, highest first.
- `LIMIT 3` — Only return the first 3 rows.

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Carol Williams   | 92000.00  |
| Alice Johnson    | 85000.00  |
| Frank Lee        | 78000.00  |
+------------------+-----------+
(3 rows)
```

The top 3 earners. This is a classic "top-N query."

> **Important:** LIMIT without ORDER BY gives you an unpredictable set of rows. Always use ORDER BY with LIMIT to get meaningful results.

### LIMIT for Quick Peeks

When exploring a large table, use LIMIT to get a quick sample without waiting for millions of rows:

```sql
SELECT * FROM employees LIMIT 5;
```

This is much faster than `SELECT *` on a table with millions of rows.

---

## OFFSET — Skipping Rows

OFFSET tells PostgreSQL to skip a certain number of rows before starting to return results:

```sql
SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 3 OFFSET 3;
```

**Line-by-line breakdown:**

- `ORDER BY salary DESC` — Sort by salary, highest first.
- `LIMIT 3` — Return 3 rows.
- `OFFSET 3` — But first, skip the first 3 rows.

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Eva Martinez     | 65000.00  |
| Jack Davis       | 63000.00  |
| Bob Smith        | 62000.00  |
+------------------+-----------+
(3 rows)
```

We skipped the top 3 (Carol, Alice, Frank) and got the next 3 (Eva, Jack, Bob).

Think of it like pages in a book. LIMIT is how many items per page. OFFSET is how many items to skip:

```
  All employees sorted by salary (high to low):

  OFFSET 0  --> Carol Williams   92000  --|
              Alice Johnson    85000  --|-- LIMIT 3 (Page 1)
              Frank Lee        78000  --|
  OFFSET 3  --> Eva Martinez     65000  --|
              Jack Davis       63000  --|-- LIMIT 3 (Page 2)
              Bob Smith        62000  --|
  OFFSET 6  --> Grace Kim        61000  --|
              Ivy Chen         59000  --|-- LIMIT 3 (Page 3)
              David Brown      58000  --|
  OFFSET 9  --> Henry Wilson     55000  --|-- LIMIT 3 (Page 4, partial)
```

---

## The Pagination Pattern

One of the most common uses of LIMIT and OFFSET is building paginated results — like search results on Google where you click "Next" to see more.

The formula is:

```
OFFSET = (page_number - 1) * items_per_page
```

```sql
-- Page 1: Show employees 1-3
SELECT name, department, salary
FROM employees
ORDER BY name
LIMIT 3 OFFSET 0;

-- Page 2: Show employees 4-6
SELECT name, department, salary
FROM employees
ORDER BY name
LIMIT 3 OFFSET 3;

-- Page 3: Show employees 7-9
SELECT name, department, salary
FROM employees
ORDER BY name
LIMIT 3 OFFSET 6;

-- Page 4: Show employees 10+
SELECT name, department, salary
FROM employees
ORDER BY name
LIMIT 3 OFFSET 9;
```

**Page 1 Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| Alice Johnson    | Engineering | 85000.00  |
| Bob Smith        | Marketing   | 62000.00  |
| Carol Williams   | Engineering | 92000.00  |
+------------------+-------------+-----------+
(3 rows)
```

**Page 2 Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| David Brown      | Sales       | 58000.00  |
| Eva Martinez     | Marketing   | 65000.00  |
| Frank Lee        | Engineering | 78000.00  |
+------------------+-------------+-----------+
(3 rows)
```

> **Performance Warning:** OFFSET can be slow on large tables. To get page 100 with 10 items per page, PostgreSQL must read and discard the first 990 rows. For large datasets, consider cursor-based pagination (using WHERE id > last_seen_id) instead. We will cover this in later chapters.

---

## FETCH FIRST — The SQL Standard Alternative

LIMIT is widely used but is technically a PostgreSQL (and MySQL) extension. The SQL standard way to limit rows is FETCH FIRST:

```sql
-- Using LIMIT (PostgreSQL style)
SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 5;

-- Using FETCH FIRST (SQL standard)
SELECT name, salary
FROM employees
ORDER BY salary DESC
FETCH FIRST 5 ROWS ONLY;
```

Both produce identical results:

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Carol Williams   | 92000.00  |
| Alice Johnson    | 85000.00  |
| Frank Lee        | 78000.00  |
| Eva Martinez     | 65000.00  |
| Jack Davis       | 63000.00  |
+------------------+-----------+
(5 rows)
```

You can also write `FETCH FIRST 1 ROW ONLY` (singular) for a single row. PostgreSQL accepts both ROW and ROWS.

### FETCH FIRST with OFFSET

```sql
SELECT name, salary
FROM employees
ORDER BY salary DESC
OFFSET 3 ROWS
FETCH FIRST 3 ROWS ONLY;
```

This skips 3 rows and returns the next 3, just like `LIMIT 3 OFFSET 3`.

> **Which should you use?** In PostgreSQL, most people use LIMIT because it is shorter. If you care about SQL portability across different databases, use FETCH FIRST.

---

## Combining WHERE + ORDER BY + LIMIT

The real power comes from combining all three:

### Top 3 Highest-Paid Non-Engineering Employees

```sql
SELECT name, department, salary
FROM employees
WHERE department <> 'Engineering'
ORDER BY salary DESC
LIMIT 3;
```

**Line-by-line breakdown:**

- `WHERE department <> 'Engineering'` — Filter out engineers.
- `ORDER BY salary DESC` — Sort remaining employees by salary, highest first.
- `LIMIT 3` — Take only the top 3.

**Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| Eva Martinez     | Marketing   | 65000.00  |
| Jack Davis       | Sales       | 63000.00  |
| Bob Smith        | Marketing   | 62000.00  |
+------------------+-------------+-----------+
(3 rows)
```

### Most Recent Hire in Each Department (Simple Version)

```sql
-- Most recently hired person in Sales
SELECT name, hire_date
FROM employees
WHERE department = 'Sales'
ORDER BY hire_date DESC
LIMIT 1;
```

**Result:**

```
+------------------+------------+
| name             | hire_date  |
+------------------+------------+
| Jack Davis       | 2023-03-20 |
+------------------+------------+
(1 row)
```

### The 5 Lowest-Paid Employees Hired Since 2020

```sql
SELECT name, department, salary, hire_date
FROM employees
WHERE hire_date >= '2020-01-01'
ORDER BY salary ASC
LIMIT 5;
```

**Result:**

```
+------------------+-------------+-----------+------------+
| name             | department  | salary    | hire_date  |
+------------------+-------------+-----------+------------+
| Henry Wilson     | HR          | 55000.00  | 2021-06-18 |
| David Brown      | Sales       | 58000.00  | 2021-01-10 |
| Ivy Chen         | HR          | 59000.00  | 2020-12-01 |
| Jack Davis       | Sales       | 63000.00  | 2023-03-20 |
| Eva Martinez     | Marketing   | 65000.00  | 2020-09-05 |
+------------------+-------------+-----------+------------+
(5 rows)
```

---

## The Order of Clauses

SQL requires clauses in a specific order:

```sql
SELECT columns          -- 1. What to show
FROM table              -- 2. Where to look
WHERE conditions        -- 3. Which rows to include
ORDER BY columns        -- 4. How to sort
LIMIT n OFFSET m;       -- 5. How many to return
```

You cannot rearrange these. ORDER BY must come after WHERE. LIMIT must come after ORDER BY.

### Execution Order vs. Writing Order

Remember, the order PostgreSQL **executes** the clauses is different from the order you **write** them:

```
  Writing Order:          Execution Order:
  1. SELECT               1. FROM        (find the table)
  2. FROM                 2. WHERE       (filter rows)
  3. WHERE                3. SELECT      (pick columns)
  4. ORDER BY             4. ORDER BY    (sort results)
  5. LIMIT/OFFSET         5. LIMIT/OFFSET (cut to size)
```

This is why you can use column aliases in ORDER BY but not in WHERE:

```sql
-- This WORKS: ORDER BY can use aliases
SELECT name, salary * 12 AS annual_compensation
FROM employees
ORDER BY annual_compensation DESC;

-- This FAILS: WHERE cannot use aliases
SELECT name, salary * 12 AS annual_compensation
FROM employees
WHERE annual_compensation > 700000;
-- ERROR: column "annual_compensation" does not exist

-- This is the fix: repeat the expression in WHERE
SELECT name, salary * 12 AS annual_compensation
FROM employees
WHERE salary * 12 > 700000;
```

---

## Top-N Queries — A Common Pattern

Top-N queries answer questions like "What are the top 5 most expensive products?" or "Who are the 3 newest employees?" They follow this pattern:

```sql
SELECT columns
FROM table
WHERE filters          -- optional
ORDER BY column DESC   -- or ASC, depending on what "top" means
LIMIT N;
```

### The Single Highest-Paid Employee

```sql
SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 1;
```

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Carol Williams   | 92000.00  |
+------------------+-----------+
(1 row)
```

### The 3 Oldest Employees (by Hire Date)

```sql
SELECT name, hire_date, department
FROM employees
ORDER BY hire_date ASC
LIMIT 3;
```

**Result:**

```
+------------------+------------+-------------+
| name             | hire_date  | department  |
+------------------+------------+-------------+
| Carol Williams   | 2018-11-01 | Engineering |
| Grace Kim        | 2019-04-30 | Sales       |
| Bob Smith        | 2019-07-22 | Marketing   |
+------------------+------------+-------------+
(3 rows)
```

### Bottom-N (The Lowest)

Just flip ASC and DESC:

```sql
-- 3 lowest-paid employees
SELECT name, salary
FROM employees
ORDER BY salary ASC
LIMIT 3;
```

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Henry Wilson     | 55000.00  |
| David Brown      | 58000.00  |
| Ivy Chen         | 59000.00  |
+------------------+-----------+
(3 rows)
```

---

## Common Mistakes

### Mistake 1: Using LIMIT Without ORDER BY

```sql
-- Bad: Which 5 employees will you get? It is unpredictable!
SELECT name FROM employees LIMIT 5;

-- Good: Now you reliably get the first 5 alphabetically
SELECT name FROM employees ORDER BY name LIMIT 5;
```

### Mistake 2: Wrong OFFSET Calculation for Pagination

```sql
-- Wrong: Page 2 with 5 items per page
-- OFFSET 5 is correct, not OFFSET 2
SELECT * FROM employees ORDER BY id LIMIT 5 OFFSET 2;  -- Wrong!
SELECT * FROM employees ORDER BY id LIMIT 5 OFFSET 5;  -- Right!

-- Formula: OFFSET = (page_number - 1) * items_per_page
-- Page 1: OFFSET 0
-- Page 2: OFFSET 5
-- Page 3: OFFSET 10
```

### Mistake 3: Sorting by a Column Not in SELECT

This actually works in PostgreSQL — you can sort by a column even if it is not in your SELECT list:

```sql
-- This is valid! Sort by salary even though it is not displayed
SELECT name, department
FROM employees
ORDER BY salary DESC;
```

It is not a mistake, but it can be confusing to readers of your code. Consider including the sort column in your SELECT.

### Mistake 4: Expecting Consistent Order Without ORDER BY

```sql
-- These two queries might return rows in different orders!
SELECT * FROM employees;  -- run now
SELECT * FROM employees;  -- run later, after updates

-- Always use ORDER BY if order matters to you
```

---

## Best Practices

1. **Always use ORDER BY when order matters.** Never assume a default order. Tables are unordered sets.

2. **Always pair LIMIT with ORDER BY.** Without ORDER BY, LIMIT gives you arbitrary rows.

3. **Be cautious with large OFFSET values.** Paginating to page 1000 (OFFSET 9990) is slow. Consider keyset pagination for large datasets.

4. **Use LIMIT for data exploration.** When exploring a table for the first time, `SELECT * FROM big_table LIMIT 10` is much safer than `SELECT * FROM big_table`.

5. **Include a tiebreaker column in ORDER BY.** If two employees have the same salary, their order is unpredictable. Add a second column (like `id` or `name`) to ensure consistent ordering:

   ```sql
   SELECT name, salary
   FROM employees
   ORDER BY salary DESC, name ASC;
   ```

---

## Quick Summary

```
+-------------------+------------------------------------------------+
| Concept           | Example                                        |
+-------------------+------------------------------------------------+
| Sort ascending    | ORDER BY salary ASC                            |
| Sort descending   | ORDER BY salary DESC                           |
| Multiple sorts    | ORDER BY department, salary DESC               |
| NULLs position    | ORDER BY col NULLS FIRST                       |
| Limit rows        | LIMIT 10                                       |
| Skip rows         | LIMIT 10 OFFSET 20                             |
| SQL standard      | FETCH FIRST 10 ROWS ONLY                       |
| Top-N query       | ORDER BY salary DESC LIMIT 3                   |
| Pagination        | LIMIT size OFFSET (page - 1) * size             |
+-------------------+------------------------------------------------+
```

---

## Key Points

- ORDER BY sorts results. ASC (ascending) is the default; use DESC for descending.
- You can sort by multiple columns. The first column is the primary sort, the second breaks ties.
- NULLS FIRST and NULLS LAST control where NULL values appear in sorted results.
- LIMIT restricts the number of rows returned. Always pair it with ORDER BY.
- OFFSET skips rows before returning results. Useful for pagination.
- FETCH FIRST is the SQL standard equivalent of LIMIT.
- The pagination formula is: OFFSET = (page_number - 1) * items_per_page.
- Clauses must appear in order: SELECT, FROM, WHERE, ORDER BY, LIMIT/OFFSET.
- Column aliases can be used in ORDER BY but not in WHERE.

---

## Practice Questions

1. Write a query to list all employees sorted by hire date, with the most recent hire first.

2. Write a query to find the 3 lowest-paid employees. Show their name, department, and salary.

3. How would you write a pagination query to show page 4 of results, with 3 employees per page, sorted by name?

4. What is wrong with this query?
   ```sql
   SELECT name FROM employees LIMIT 5 ORDER BY name;
   ```

5. Explain the difference between these two queries:
   ```sql
   -- Query A
   SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 1;

   -- Query B
   SELECT name, salary FROM employees ORDER BY salary ASC LIMIT 1;
   ```

---

## Exercises

### Exercise 1: Top Earners Report

Write queries to answer:
1. Who is the highest-paid employee in each department? (Write a separate query for each department using WHERE and LIMIT 1.)
2. List all employees sorted by department (A-Z), then by salary within each department (highest first).

### Exercise 2: Pagination System

Imagine you are building a web page that shows 4 employees per page, sorted alphabetically by name. Write the queries for pages 1, 2, and 3.

### Exercise 3: Combined Filtering and Sorting

Write a single query that:
1. Excludes employees from the HR department
2. Only includes employees earning more than 60,000
3. Sorts the results by hire date (newest first)
4. Returns only the top 3 results

---

## What Is Next?

You can now filter, sort, and paginate your data. But what if you want to know the total salary of all employees, or the average salary per department? In the next chapter, you will learn **aggregate functions** — tools like COUNT, SUM, AVG, MIN, and MAX that let you calculate summaries from your data instead of looking at individual rows.
