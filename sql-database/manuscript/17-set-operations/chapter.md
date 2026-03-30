# Chapter 17: Set Operations — UNION, INTERSECT, and EXCEPT

## What You Will Learn

- How UNION combines results from two queries and removes duplicates
- How UNION ALL combines results and keeps duplicates
- How INTERSECT finds rows that appear in both queries
- How EXCEPT finds rows in the first query that are not in the second
- The rules for using set operations (column count, compatible types)
- How to use ORDER BY with set operations
- Practical examples: combining customer lists, finding shared data, reporting

## Why This Chapter Matters

Imagine you have two spreadsheets of customer names — one from your online store and one from your physical store. You might want to:

- **Combine** both lists into one (UNION)
- **Find customers** who appear on both lists (INTERSECT)
- **Find customers** on the first list who are NOT on the second (EXCEPT)

These are set operations, and they work just like the set theory you may have learned in math class. In SQL, set operations let you combine the results of two or more SELECT queries into a single result set.

While JOINs combine tables **horizontally** (adding columns), set operations combine queries **vertically** (adding rows).

```
JOIN (horizontal):             SET OPERATIONS (vertical):
+------+------+               +------+
| T1   | T2   |               | Q1   |
| cols | cols |               | rows |
+------+------+               +------+
                              | Q2   |
                              | rows |
                              +------+
```

---

## Setting Up Practice Data

Let us create two customer tables to simulate data from different sources.

```sql
CREATE TABLE online_customers (
    customer_id SERIAL PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    email       VARCHAR(100),
    city        VARCHAR(50)
);

CREATE TABLE store_customers (
    customer_id SERIAL PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    email       VARCHAR(100),
    city        VARCHAR(50)
);

INSERT INTO online_customers (first_name, last_name, email, city) VALUES
('Alice',   'Johnson', 'alice@email.com',   'New York'),
('Bob',     'Smith',   'bob@email.com',     'Chicago'),
('Charlie', 'Brown',   'charlie@email.com', 'Boston'),
('Diana',   'Lee',     'diana@email.com',   'New York'),
('Eve',     'Davis',   'eve@email.com',     'Seattle');

INSERT INTO store_customers (first_name, last_name, email, city) VALUES
('Charlie', 'Brown',   'charlie@email.com', 'Boston'),
('Frank',   'Wilson',  'frank@email.com',   'Denver'),
('Grace',   'Taylor',  'grace@email.com',   'Chicago'),
('Diana',   'Lee',     'diana@email.com',   'New York'),
('Henry',   'Martinez','henry@email.com',   'Miami');
```

Here is what the data looks like:

```
online_customers:               store_customers:
+---------+---------+--------+  +---------+---------+--------+
| first   | last    | city   |  | first   | last    | city   |
+---------+---------+--------+  +---------+---------+--------+
| Alice   | Johnson | NY     |  | Charlie | Brown   | Boston |
| Bob     | Smith   | Chicago|  | Frank   | Wilson  | Denver |
| Charlie | Brown   | Boston |  | Grace   | Taylor  | Chicago|
| Diana   | Lee     | NY     |  | Diana   | Lee     | NY     |
| Eve     | Davis   | Seattle|  | Henry   | Martinez| Miami  |
+---------+---------+--------+  +---------+---------+--------+

Shared: Charlie Brown and Diana Lee appear in BOTH tables.
```

---

## UNION — Combine and Remove Duplicates

UNION takes the results of two SELECT queries and combines them into one result set, **removing duplicate rows**.

### The Syntax

```sql
SELECT columns FROM table_1
UNION
SELECT columns FROM table_2;
```

### Example: All Unique Customers

```sql
SELECT first_name, last_name, email, city
FROM online_customers
UNION
SELECT first_name, last_name, email, city
FROM store_customers;
```

**Result:**

```
+-----------+-----------+---------------------+----------+
| first_name| last_name | email               | city     |
+-----------+-----------+---------------------+----------+
| Alice     | Johnson   | alice@email.com     | New York |
| Bob       | Smith     | bob@email.com       | Chicago  |
| Charlie   | Brown     | charlie@email.com   | Boston   |
| Diana     | Lee       | diana@email.com     | New York |
| Eve       | Davis     | eve@email.com       | Seattle  |
| Frank     | Wilson    | frank@email.com     | Denver   |
| Grace     | Taylor    | grace@email.com     | Chicago  |
| Henry     | Martinez  | henry@email.com     | Miami    |
+-----------+-----------+---------------------+----------+
(8 rows)
```

We started with 5 + 5 = 10 rows, but got only 8. Charlie Brown and Diana Lee appeared in both tables, so UNION removed the duplicates.

### Visual Representation

```
Online:  {Alice, Bob, Charlie, Diana, Eve}
Store:   {Charlie, Frank, Grace, Diana, Henry}

UNION:   {Alice, Bob, Charlie, Diana, Eve, Frank, Grace, Henry}
          (duplicates removed — Charlie and Diana appear once)

Think of it as merging two stacks of cards and
removing any cards that appear twice.
```

---

## UNION ALL — Combine and Keep Duplicates

UNION ALL works like UNION, but it keeps **all rows**, including duplicates.

```sql
SELECT first_name, last_name, email, city
FROM online_customers
UNION ALL
SELECT first_name, last_name, email, city
FROM store_customers;
```

**Result:**

```
+-----------+-----------+---------------------+----------+
| first_name| last_name | email               | city     |
+-----------+-----------+---------------------+----------+
| Alice     | Johnson   | alice@email.com     | New York |
| Bob       | Smith     | bob@email.com       | Chicago  |
| Charlie   | Brown     | charlie@email.com   | Boston   |
| Diana     | Lee       | diana@email.com     | New York |
| Eve       | Davis     | eve@email.com       | Seattle  |
| Charlie   | Brown     | charlie@email.com   | Boston   |
| Frank     | Wilson    | frank@email.com     | Denver   |
| Grace     | Taylor    | grace@email.com     | Chicago  |
| Diana     | Lee       | diana@email.com     | New York |
| Henry     | Martinez  | henry@email.com     | Miami    |
+-----------+-----------+---------------------+----------+
(10 rows)
```

All 10 rows are returned. Charlie and Diana each appear twice.

### UNION vs UNION ALL

```
UNION:     Removes duplicates (slower — must compare all rows)
UNION ALL: Keeps duplicates   (faster — no comparison needed)
```

**When to use which:**

| Use UNION when... | Use UNION ALL when... |
|---|---|
| You need unique results | You want all rows, including duplicates |
| Combining overlapping data sources | Combining data you know has no overlap |
| Building a master list | Aggregating (COUNT, SUM) across sources |

**Performance tip:** UNION ALL is faster than UNION because it does not need to check for and remove duplicates. If you know there are no duplicates, always use UNION ALL.

---

## INTERSECT — Find Common Rows

INTERSECT returns only rows that appear in **both** query results.

### Example: Customers Who Shop Both Online and In-Store

```sql
SELECT first_name, last_name, email
FROM online_customers
INTERSECT
SELECT first_name, last_name, email
FROM store_customers;
```

**Result:**

```
+-----------+-----------+---------------------+
| first_name| last_name | email               |
+-----------+-----------+---------------------+
| Charlie   | Brown     | charlie@email.com   |
| Diana     | Lee       | diana@email.com     |
+-----------+-----------+---------------------+
(2 rows)
```

Only Charlie and Diana appear in both tables.

### Visual Representation

```
Online:    {Alice, Bob, Charlie, Diana, Eve}
Store:     {Charlie, Frank, Grace, Diana, Henry}

INTERSECT: {Charlie, Diana}
            (only the overlap)

Like a Venn diagram — INTERSECT returns
only the middle section.

  Online          Store
+---------+     +---------+
|         |     |         |
| Alice   +-----+ Frank   |
| Bob     |Charl| Grace   |
| Eve     |Diana| Henry   |
|         +-----+         |
+---------+     +---------+
```

---

## EXCEPT — Find Rows in First but Not Second

EXCEPT returns rows from the first query that do **not** appear in the second query. Think of it as subtraction.

### Example: Online-Only Customers

```sql
SELECT first_name, last_name, email
FROM online_customers
EXCEPT
SELECT first_name, last_name, email
FROM store_customers;
```

**Result:**

```
+-----------+-----------+---------------------+
| first_name| last_name | email               |
+-----------+-----------+---------------------+
| Alice     | Johnson   | alice@email.com     |
| Bob       | Smith     | bob@email.com       |
| Eve       | Davis     | eve@email.com       |
+-----------+-----------+---------------------+
(3 rows)
```

These customers shop online but have never visited the physical store.

### Example: Store-Only Customers (Reverse the Order)

```sql
SELECT first_name, last_name, email
FROM store_customers
EXCEPT
SELECT first_name, last_name, email
FROM online_customers;
```

**Result:**

```
+-----------+-----------+---------------------+
| first_name| last_name | email               |
+-----------+-----------+---------------------+
| Frank     | Wilson    | frank@email.com     |
| Grace     | Taylor    | grace@email.com     |
| Henry     | Martinez  | henry@email.com     |
+-----------+-----------+---------------------+
(3 rows)
```

**Order matters with EXCEPT.** `A EXCEPT B` gives rows in A but not B. `B EXCEPT A` gives rows in B but not A. These are different results.

### Visual Representation

```
Online EXCEPT Store:              Store EXCEPT Online:

  Online          Store             Online          Store
+---------+     +---------+      +---------+     +---------+
|#########|     |         |      |         |     |#########|
|# Alice #|     |         |      |         |     |# Frank #|
|# Bob   #|     |         |      |         |     |# Grace #|
|# Eve   #|     |         |      |         |     |# Henry #|
|#########|     |         |      |         |     |#########|
+---------+     +---------+      +---------+     +---------+

The shaded area (###) is the result.
```

---

## Rules for Set Operations

All set operations follow these rules:

### Rule 1: Same Number of Columns

Both queries must select the **same number of columns**.

```sql
-- WRONG: First query has 3 columns, second has 2
SELECT first_name, last_name, email FROM online_customers
UNION
SELECT first_name, last_name FROM store_customers;
-- ERROR: each UNION query must have the same number of columns
```

**Fix:** Make sure both queries have the same number of columns.

```sql
-- CORRECT
SELECT first_name, last_name, email FROM online_customers
UNION
SELECT first_name, last_name, email FROM store_customers;
```

### Rule 2: Compatible Data Types

The columns in matching positions must have **compatible data types**.

```sql
-- WRONG: Can't UNION a VARCHAR with an INTEGER
SELECT first_name FROM online_customers
UNION
SELECT customer_id FROM store_customers;
-- ERROR: UNION types varchar and integer cannot be matched
```

**Fix:** Make sure corresponding columns have compatible types.

### Rule 3: Column Names Come from the First Query

The column names in the result are determined by the **first** query.

```sql
SELECT first_name AS name, city AS location FROM online_customers
UNION
SELECT first_name AS customer, city AS town FROM store_customers;
-- Result columns will be "name" and "location" (from the first query)
```

### Summary of Rules

```
+-------------------------------------------------+
| SET OPERATION RULES                             |
+-------------------------------------------------+
| 1. Same number of columns in both queries       |
| 2. Corresponding columns have compatible types  |
| 3. Column names come from the first query       |
| 4. ORDER BY goes at the very end (once)         |
+-------------------------------------------------+
```

---

## ORDER BY with Set Operations

You can add ORDER BY to a set operation, but it goes at the **very end** and applies to the **entire combined result**.

```sql
SELECT first_name, last_name, city
FROM online_customers
UNION
SELECT first_name, last_name, city
FROM store_customers
ORDER BY city, last_name;
```

**Result:**

```
+-----------+-----------+----------+
| first_name| last_name | city     |
+-----------+-----------+----------+
| Charlie   | Brown     | Boston   |
| Bob       | Smith     | Chicago  |
| Grace     | Taylor    | Chicago  |
| Frank     | Wilson    | Denver   |
| Henry     | Martinez  | Miami    |
| Alice     | Johnson   | New York |
| Diana     | Lee       | New York |
| Eve       | Davis     | Seattle  |
+-----------+-----------+----------+
(8 rows)
```

**Important:** You cannot put ORDER BY inside individual queries of a set operation (unless you wrap the query in a subquery).

```sql
-- WRONG
SELECT first_name FROM online_customers ORDER BY first_name
UNION
SELECT first_name FROM store_customers;
-- ERROR: ORDER BY within individual UNION queries is not allowed

-- CORRECT: ORDER BY at the end
SELECT first_name FROM online_customers
UNION
SELECT first_name FROM store_customers
ORDER BY first_name;
```

---

## Adding a Source Column

When combining data from different sources, it is often helpful to add a column that identifies where each row came from.

```sql
SELECT first_name, last_name, city, 'Online' AS source
FROM online_customers
UNION ALL
SELECT first_name, last_name, city, 'Store' AS source
FROM store_customers
ORDER BY last_name;
```

**Result:**

```
+-----------+-----------+----------+--------+
| first_name| last_name | city     | source |
+-----------+-----------+----------+--------+
| Charlie   | Brown     | Boston   | Online |
| Charlie   | Brown     | Boston   | Store  |
| Eve       | Davis     | Seattle  | Online |
| Alice     | Johnson   | New York | Online |
| Diana     | Lee       | New York | Online |
| Diana     | Lee       | New York | Store  |
| Henry     | Martinez  | Miami    | Store  |
| Bob       | Smith     | Chicago  | Online |
| Grace     | Taylor    | Chicago  | Store  |
| Frank     | Wilson    | Denver   | Store  |
+-----------+-----------+----------+--------+
(10 rows)
```

Notice we used UNION ALL here, not UNION. If we used UNION, it would consider Charlie's two rows different (because the source column differs) and keep both anyway. But UNION ALL is faster since no duplicate checking is needed.

---

## Practical Example: Combining Different Query Results

Set operations do not have to combine data from different tables. You can combine different queries from the **same** table.

### Employees by Salary Category

```sql
SELECT first_name, last_name, salary, 'High' AS category
FROM employees
WHERE salary >= 80000

UNION ALL

SELECT first_name, last_name, salary, 'Medium' AS category
FROM employees
WHERE salary >= 65000 AND salary < 80000

UNION ALL

SELECT first_name, last_name, salary, 'Low' AS category
FROM employees
WHERE salary < 65000

ORDER BY salary DESC;
```

**Result:**

```
+------------+-----------+----------+----------+
| first_name | last_name | salary   | category |
+------------+-----------+----------+----------+
| Eve        | Davis     | 90000.00 | High     |
| Alice      | Johnson   | 85000.00 | High     |
| Diana      | Lee       | 78000.00 | Medium   |
| Bob        | Smith     | 72000.00 | Medium   |
| Charlie    | Brown     | 65000.00 | Medium   |
| Frank      | Wilson    | 60000.00 | Low      |
+------------+-----------+----------+----------+
(6 rows)
```

> **Note:** This specific example could be done more cleanly with a CASE expression, but it illustrates how UNION ALL can combine categorized subsets.

---

## Practical Example: Finding Cities Served by Both Channels

```sql
-- Cities with both online and store customers
SELECT city FROM online_customers
INTERSECT
SELECT city FROM store_customers;
```

**Result:**

```
+----------+
| city     |
+----------+
| Boston   |
| Chicago  |
| New York |
+----------+
(3 rows)
```

These cities have customers in both channels.

```sql
-- Cities with online customers but NO store customers
SELECT city FROM online_customers
EXCEPT
SELECT city FROM store_customers;
```

**Result:**

```
+----------+
| city     |
+----------+
| Seattle  |
+----------+
(1 row)
```

Seattle only has online customers.

---

## Chaining Multiple Set Operations

You can chain more than two queries with set operations.

```sql
-- All cities from all customer sources (employees too)
SELECT city FROM online_customers
UNION
SELECT city FROM store_customers
UNION
SELECT location AS city FROM departments
ORDER BY city;
```

**Result:**

```
+------------+
| city       |
+------------+
| Boston     |
| Building A |
| Building B |
| Building C |
| Building D |
| Chicago    |
| Denver     |
| Miami      |
| New York   |
| Seattle    |
+------------+
(10 rows)
```

When chaining, operations are evaluated left to right. You can use parentheses to control the order:

```sql
-- Parentheses control evaluation order
(SELECT city FROM online_customers
 INTERSECT
 SELECT city FROM store_customers)
EXCEPT
SELECT 'Boston';
```

This first finds cities in both tables (Boston, Chicago, New York), then removes Boston.

---

## Common Mistakes

### Mistake 1: Different Number of Columns

```sql
-- WRONG
SELECT first_name, last_name, email FROM online_customers
UNION
SELECT first_name, last_name FROM store_customers;
-- ERROR: each UNION query must have the same number of columns
```

**Fix:** Add NULL or a placeholder for missing columns.

```sql
-- CORRECT
SELECT first_name, last_name, email FROM online_customers
UNION
SELECT first_name, last_name, NULL AS email FROM store_customers;
```

### Mistake 2: ORDER BY Inside a UNION

```sql
-- WRONG
SELECT first_name FROM online_customers ORDER BY first_name
UNION
SELECT first_name FROM store_customers;
```

**Fix:** Put ORDER BY at the very end.

```sql
-- CORRECT
SELECT first_name FROM online_customers
UNION
SELECT first_name FROM store_customers
ORDER BY first_name;
```

### Mistake 3: Using UNION When You Mean UNION ALL

```sql
-- WRONG: UNION removes duplicates, hiding the true count
SELECT customer_id, product_id FROM orders
UNION
SELECT customer_id, product_id FROM orders;
-- Duplicates removed — you lose information!
```

**Fix:** Use UNION ALL when you want to keep all rows.

### Mistake 4: Assuming EXCEPT Is Commutative

```sql
-- These are NOT the same!
SELECT city FROM online_customers EXCEPT SELECT city FROM store_customers;
-- vs
SELECT city FROM store_customers EXCEPT SELECT city FROM online_customers;
```

**Fix:** Remember that EXCEPT is directional. `A EXCEPT B` is different from `B EXCEPT A`.

---

## Best Practices

1. **Use UNION ALL instead of UNION** when you know there are no duplicates or when you want to keep duplicates. It is significantly faster on large data sets.

2. **Add a source column** when combining data from different tables. This makes it easy to trace where each row came from.

3. **Use the same column aliases** in both queries for clarity, even though only the first query's names matter.

4. **Put ORDER BY at the end** of the entire set operation, not inside individual queries.

5. **Use INTERSECT for "both" questions** and EXCEPT for "only in one" questions. They are more readable than equivalent subqueries or JOINs for these specific patterns.

6. **Be explicit about what you want.** UNION removes duplicates and UNION ALL does not. Choose deliberately rather than defaulting to one.

---

## Quick Summary

| Operation | What It Returns |
|-----------|----------------|
| UNION | All rows from both queries, duplicates removed |
| UNION ALL | All rows from both queries, duplicates kept |
| INTERSECT | Only rows that appear in both queries |
| EXCEPT | Rows in the first query that are NOT in the second |

---

## Key Points

- **UNION** combines results and removes duplicates. **UNION ALL** keeps all rows.
- **INTERSECT** finds rows common to both queries (the overlap).
- **EXCEPT** finds rows in the first query that do not appear in the second (the difference). Order matters.
- All set operations require the **same number of columns** with **compatible data types**.
- Column names in the result come from the **first query**.
- **ORDER BY** goes at the very end and applies to the entire combined result.
- **UNION ALL is faster** than UNION because it skips duplicate checking.
- Set operations combine results **vertically** (more rows), while JOINs combine **horizontally** (more columns).

---

## Practice Questions

**Question 1:** What is the difference between UNION and UNION ALL?

<details>
<summary>Answer</summary>

UNION combines results from two queries and **removes duplicate rows**. UNION ALL combines results and **keeps all rows**, including duplicates. UNION ALL is faster because it does not need to check for duplicates.

</details>

**Question 2:** If Query A returns 100 rows and Query B returns 80 rows, what is the maximum number of rows UNION can return? What about UNION ALL?

<details>
<summary>Answer</summary>

UNION: Maximum 180 rows (if there are no duplicates between the two queries). Minimum 100 rows (if all 80 rows of B are duplicates of rows in A).

UNION ALL: Always exactly 180 rows (100 + 80), regardless of duplicates.

</details>

**Question 3:** Is `A EXCEPT B` the same as `B EXCEPT A`?

<details>
<summary>Answer</summary>

No. `A EXCEPT B` returns rows that are in A but NOT in B. `B EXCEPT A` returns rows that are in B but NOT in A. EXCEPT is not commutative — the order of the queries matters.

</details>

**Question 4:** Can you use set operations with queries from the same table?

<details>
<summary>Answer</summary>

Yes. Set operations work with any two SELECT queries, regardless of whether they come from the same table or different tables. The only requirement is that both queries return the same number of columns with compatible types.

</details>

**Question 5:** Why might you add a literal string column (like `'Online'` or `'Store'`) when using UNION ALL?

<details>
<summary>Answer</summary>

To identify which source each row came from. When you combine data from multiple tables or queries, a source column helps you trace the origin of each row. This is especially useful for reporting and debugging.

</details>

---

## Exercises

### Exercise 1: Master Customer List

Create a deduplicated master customer list from both online_customers and store_customers. Include all columns and sort by last name. How many unique customers are there?

<details>
<summary>Solution</summary>

```sql
SELECT first_name, last_name, email, city
FROM online_customers
UNION
SELECT first_name, last_name, email, city
FROM store_customers
ORDER BY last_name;
```

Expected output (8 unique customers):

```
+-----------+-----------+---------------------+----------+
| first_name| last_name | email               | city     |
+-----------+-----------+---------------------+----------+
| Charlie   | Brown     | charlie@email.com   | Boston   |
| Eve       | Davis     | eve@email.com       | Seattle  |
| Alice     | Johnson   | alice@email.com     | New York |
| Diana     | Lee       | diana@email.com     | New York |
| Henry     | Martinez  | henry@email.com     | Miami    |
| Bob       | Smith     | bob@email.com       | Chicago  |
| Grace     | Taylor    | grace@email.com     | Chicago  |
| Frank     | Wilson    | frank@email.com     | Denver   |
+-----------+-----------+---------------------+----------+
```

</details>

### Exercise 2: Exclusive Customers Report

Write two queries: (1) customers who ONLY shop online and (2) customers who ONLY shop in-store. Add a source column to each and combine them into one result using UNION ALL.

<details>
<summary>Solution</summary>

```sql
SELECT first_name, last_name, 'Online Only' AS channel
FROM (
    SELECT first_name, last_name, email
    FROM online_customers
    EXCEPT
    SELECT first_name, last_name, email
    FROM store_customers
) AS online_only

UNION ALL

SELECT first_name, last_name, 'Store Only' AS channel
FROM (
    SELECT first_name, last_name, email
    FROM store_customers
    EXCEPT
    SELECT first_name, last_name, email
    FROM online_customers
) AS store_only

ORDER BY channel, last_name;
```

Expected output:

```
+-----------+-----------+-------------+
| first_name| last_name | channel     |
+-----------+-----------+-------------+
| Eve       | Davis     | Online Only |
| Alice     | Johnson   | Online Only |
| Bob       | Smith     | Online Only |
| Henry     | Martinez  | Store Only  |
| Grace     | Taylor    | Store Only  |
| Frank     | Wilson    | Store Only  |
+-----------+-----------+-------------+
```

</details>

### Exercise 3: City Analysis

Write queries to answer these three questions:
1. Which cities have customers in BOTH channels?
2. Which cities have ONLY online customers?
3. Which cities have ONLY store customers?

<details>
<summary>Solution</summary>

```sql
-- 1. Cities with customers in BOTH channels
SELECT city, 'Both channels' AS status
FROM online_customers
INTERSECT
SELECT city, 'Both channels'
FROM store_customers;

-- 2. Cities with ONLY online customers
SELECT city FROM online_customers
EXCEPT
SELECT city FROM store_customers;

-- 3. Cities with ONLY store customers
SELECT city FROM store_customers
EXCEPT
SELECT city FROM online_customers;
```

Expected outputs:

```
-- Query 1: Both channels
+----------+
| city     |
+----------+
| Boston   |
| Chicago  |
| New York |
+----------+

-- Query 2: Online only
+----------+
| city     |
+----------+
| Seattle  |
+----------+

-- Query 3: Store only
+----------+
| city     |
+----------+
| Denver   |
| Miami    |
+----------+
```

</details>

---

## What Is Next?

You now know how to combine, intersect, and subtract query results. In the next chapter, we switch gears to work with **string and date functions** — the tools you need to manipulate text data (formatting names, extracting substrings, searching within strings) and date data (calculating ages, extracting parts of dates, formatting timestamps). These are the functions you will use in almost every real-world query.
