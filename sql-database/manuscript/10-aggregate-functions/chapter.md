# Chapter 10: Aggregate Functions — Summarizing Your Data

## What You Will Learn

In this chapter, you will learn how to:

- Count rows with COUNT(*), COUNT(column), and COUNT(DISTINCT)
- Add up values with SUM
- Calculate averages with AVG
- Find the smallest and largest values with MIN and MAX
- Combine multiple aggregate functions in a single query
- Understand how NULL values affect aggregates
- Use ROUND to clean up averages
- Write practical summary queries

## Why This Chapter Matters

So far, every query you have written returns individual rows — one row per employee, one row per record. But what if your boss asks, "How many employees do we have?" or "What is our total salary budget?" You do not want a list of 10 (or 10,000) rows. You want a single number.

Aggregate functions collapse many rows into a single summary value. They are like the "total" row at the bottom of a spreadsheet. Instead of looking at every individual sale, you can instantly see the total revenue, the average order size, or the number of customers.

If SELECT is like reading a book word by word, aggregate functions are like reading the summary on the back cover. They give you the big picture.

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

## COUNT — How Many Rows?

COUNT is the simplest aggregate. It counts rows.

### COUNT(*) — Count All Rows

```sql
SELECT COUNT(*) AS total_employees
FROM employees;
```

**Line-by-line breakdown:**

- `COUNT(*)` — Count every row in the table, regardless of what is in the columns.
- `AS total_employees` — Give the result a meaningful name.

**Result:**

```
+-----------------+
| total_employees |
+-----------------+
|              10 |
+-----------------+
(1 row)
```

Notice: instead of 10 individual rows, we get a single row with a single number. That is what aggregate functions do — they collapse many rows into one summary.

Think of COUNT(*) like a headcount at a meeting. You do not care who is there or what they do. You just want to know how many people are in the room.

### COUNT(*) with WHERE

You can combine COUNT with WHERE to count only matching rows:

```sql
SELECT COUNT(*) AS engineering_count
FROM employees
WHERE department = 'Engineering';
```

**Result:**

```
+-------------------+
| engineering_count |
+-------------------+
|                 3 |
+-------------------+
(1 row)
```

Three engineers. The WHERE clause filters first, then COUNT counts what is left.

### COUNT(column) — Count Non-NULL Values

COUNT(column_name) counts only the rows where that column is NOT NULL:

```sql
-- First, let us see what COUNT(column) does differently
-- Add a test row with a NULL salary for demonstration
-- (we will remove it after)

-- For now, on our current data with no NULLs:
SELECT
    COUNT(*)       AS total_rows,
    COUNT(salary)  AS rows_with_salary
FROM employees;
```

**Result:**

```
+------------+------------------+
| total_rows | rows_with_salary |
+------------+------------------+
|         10 |               10 |
+------------+------------------+
```

Since none of our salary values are NULL, both counts are 10. The difference matters when you have NULL values:

```
  COUNT(*)        -->  Counts ALL rows (including those with NULLs)
  COUNT(column)   -->  Counts only rows where column IS NOT NULL
```

Think of it this way: COUNT(*) asks "How many people showed up?" while COUNT(email) asks "How many people left their email address?"

### COUNT(DISTINCT column) — Count Unique Values

```sql
SELECT COUNT(DISTINCT department) AS department_count
FROM employees;
```

**Result:**

```
+------------------+
| department_count |
+------------------+
|                4 |
+------------------+
(1 row)
```

There are 4 unique departments (Engineering, HR, Marketing, Sales), even though we have 10 employees. COUNT(DISTINCT) eliminates duplicates before counting.

```sql
-- Compare:
SELECT
    COUNT(department)          AS total_dept_values,
    COUNT(DISTINCT department) AS unique_departments
FROM employees;
```

**Result:**

```
+-------------------+--------------------+
| total_dept_values | unique_departments |
+-------------------+--------------------+
|                10 |                  4 |
+-------------------+--------------------+
```

---

## SUM — Adding Up Values

SUM adds up all the values in a numeric column:

```sql
SELECT SUM(salary) AS total_salary_budget
FROM employees;
```

**Result:**

```
+---------------------+
| total_salary_budget |
+---------------------+
|           678000.00 |
+---------------------+
(1 row)
```

The company spends $678,000 on salaries. Think of SUM like the total on a receipt — it adds up all the individual items.

### SUM with WHERE

```sql
SELECT SUM(salary) AS engineering_budget
FROM employees
WHERE department = 'Engineering';
```

**Result:**

```
+--------------------+
| engineering_budget |
+--------------------+
|          255000.00 |
+--------------------+
(1 row)
```

The Engineering department costs $255,000 in salaries (85,000 + 92,000 + 78,000).

> **Note:** SUM only works with numeric columns. You cannot SUM text or dates.

---

## AVG — The Average

AVG calculates the arithmetic mean (add everything up, then divide by the count):

```sql
SELECT AVG(salary) AS average_salary
FROM employees;
```

**Result:**

```
+----------------------+
| average_salary       |
+----------------------+
| 67800.000000000000   |
+----------------------+
(1 row)
```

That is a lot of decimal places. Let us clean it up with ROUND:

```sql
SELECT ROUND(AVG(salary), 2) AS average_salary
FROM employees;
```

**Result:**

```
+----------------+
| average_salary |
+----------------+
|       67800.00 |
+----------------+
(1 row)
```

The ROUND function takes two arguments: the number to round and the number of decimal places.

### Average for a Specific Group

```sql
SELECT ROUND(AVG(salary), 2) AS avg_sales_salary
FROM employees
WHERE department = 'Sales';
```

**Result:**

```
+------------------+
| avg_sales_salary |
+------------------+
|         60666.67 |
+------------------+
(1 row)
```

The average salary in Sales is $60,666.67 (58,000 + 61,000 + 63,000 = 182,000 / 3).

---

## MIN and MAX — Finding Extremes

MIN finds the smallest value. MAX finds the largest.

```sql
SELECT
    MIN(salary) AS lowest_salary,
    MAX(salary) AS highest_salary
FROM employees;
```

**Result:**

```
+---------------+----------------+
| lowest_salary | highest_salary |
+---------------+----------------+
|      55000.00 |       92000.00 |
+---------------+----------------+
(1 row)
```

### MIN and MAX with Dates

MIN and MAX work with dates too. MIN gives the earliest date, MAX gives the latest:

```sql
SELECT
    MIN(hire_date) AS earliest_hire,
    MAX(hire_date) AS latest_hire
FROM employees;
```

**Result:**

```
+---------------+-------------+
| earliest_hire | latest_hire |
+---------------+-------------+
| 2018-11-01    | 2023-03-20  |
+---------------+-------------+
(1 row)
```

Carol Williams was the first hired (2018), and Jack Davis was the most recent (2023).

### MIN and MAX with Text

For text columns, MIN gives the first alphabetically and MAX gives the last:

```sql
SELECT
    MIN(name) AS first_alphabetically,
    MAX(name) AS last_alphabetically
FROM employees;
```

**Result:**

```
+----------------------+---------------------+
| first_alphabetically | last_alphabetically |
+----------------------+---------------------+
| Alice Johnson        | Jack Davis          |
+----------------------+---------------------+
```

---

## Combining Multiple Aggregates

You can use multiple aggregate functions in a single query:

```sql
SELECT
    COUNT(*)              AS total_employees,
    SUM(salary)           AS total_salary,
    ROUND(AVG(salary), 2) AS average_salary,
    MIN(salary)           AS lowest_salary,
    MAX(salary)           AS highest_salary,
    MAX(salary) - MIN(salary) AS salary_range
FROM employees;
```

**Result:**

```
+-----------+--------------+----------------+---------------+----------------+--------------+
| total_    | total_salary | average_salary | lowest_salary | highest_salary | salary_range |
| employees |              |                |               |                |              |
+-----------+--------------+----------------+---------------+----------------+--------------+
|        10 |    678000.00 |       67800.00 |      55000.00 |       92000.00 |     37000.00 |
+-----------+--------------+----------------+---------------+----------------+--------------+
(1 row)
```

One query gives you a complete salary summary. This is like getting the executive summary of a 100-page report in a single glance.

### Department-Specific Summary

```sql
SELECT
    COUNT(*)              AS headcount,
    ROUND(AVG(salary), 2) AS avg_salary,
    MIN(salary)           AS min_salary,
    MAX(salary)           AS max_salary
FROM employees
WHERE department = 'Engineering';
```

**Result:**

```
+-----------+------------+------------+------------+
| headcount | avg_salary | min_salary | max_salary |
+-----------+------------+------------+------------+
|         3 |   85000.00 |   78000.00 |   92000.00 |
+-----------+------------+------------+------------+
(1 row)
```

---

## How NULL Values Affect Aggregates

NULLs are a common source of confusion with aggregates. Here is how each function handles them:

```
+----------+--------------------------------------------+
| Function | How it handles NULL                         |
+----------+--------------------------------------------+
| COUNT(*) | Counts ALL rows, including those with NULLs |
| COUNT(x) | Ignores rows where x IS NULL               |
| SUM(x)   | Ignores NULL values                        |
| AVG(x)   | Ignores NULL values (affects the divisor!) |
| MIN(x)   | Ignores NULL values                        |
| MAX(x)   | Ignores NULL values                        |
+----------+--------------------------------------------+
```

The most important thing to understand is how AVG handles NULLs:

```
  Example with 5 values: 10, 20, NULL, 30, NULL

  AVG ignores NULLs:
  AVG = (10 + 20 + 30) / 3 = 20.0

  NOT:
  AVG = (10 + 20 + 0 + 30 + 0) / 5 = 12.0

  NULL is ignored entirely — it does not count as zero,
  and it does not increase the divisor.
```

This is important because it means AVG gives you the average of known values, not the average of all possible values. In most cases this is what you want, but be aware of it.

### SUM on All NULLs

If every value is NULL, SUM returns NULL (not zero):

```sql
SELECT SUM(NULL::numeric) AS result;
```

**Result:**

```
+--------+
| result |
+--------+
|  NULL  |
+--------+
```

Use COALESCE to convert NULL to zero if needed:

```sql
SELECT COALESCE(SUM(NULL::numeric), 0) AS result;
```

**Result:**

```
+--------+
| result |
+--------+
|      0 |
+--------+
```

---

## Practical Queries

### What Percentage of the Budget Goes to Each Department?

```sql
SELECT
    ROUND(
        SUM(CASE WHEN department = 'Engineering' THEN salary ELSE 0 END)
        / SUM(salary) * 100, 1
    ) AS engineering_pct,
    ROUND(
        SUM(CASE WHEN department = 'Sales' THEN salary ELSE 0 END)
        / SUM(salary) * 100, 1
    ) AS sales_pct,
    ROUND(
        SUM(CASE WHEN department = 'Marketing' THEN salary ELSE 0 END)
        / SUM(salary) * 100, 1
    ) AS marketing_pct,
    ROUND(
        SUM(CASE WHEN department = 'HR' THEN salary ELSE 0 END)
        / SUM(salary) * 100, 1
    ) AS hr_pct
FROM employees;
```

**Result:**

```
+----------------+-----------+---------------+--------+
| engineering_pct| sales_pct | marketing_pct | hr_pct |
+----------------+-----------+---------------+--------+
|           37.6 |      26.8 |          18.7 |   16.8 |
+----------------+-----------+---------------+--------+
```

(Do not worry about CASE — we will cover it in Chapter 19. The point here is that aggregate functions can be used in creative ways.)

### How Many Employees Earn Above Average?

```sql
SELECT COUNT(*) AS above_average_count
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

**Result:**

```
+---------------------+
| above_average_count |
+---------------------+
|                   4 |
+---------------------+
(1 row)
```

Four employees earn above the average salary of $67,800. This uses a subquery (a query inside a query), which we will cover in detail in Chapter 16.

### Salary Summary by Salary Range

```sql
SELECT
    COUNT(CASE WHEN salary < 60000 THEN 1 END)                  AS under_60k,
    COUNT(CASE WHEN salary BETWEEN 60000 AND 79999 THEN 1 END)  AS between_60k_80k,
    COUNT(CASE WHEN salary >= 80000 THEN 1 END)                 AS over_80k
FROM employees;
```

**Result:**

```
+-----------+-----------------+----------+
| under_60k | between_60k_80k | over_80k |
+-----------+-----------------+----------+
|         3 |               5 |        2 |
+-----------+-----------------+----------+
```

---

## How Aggregates Fit in the Query Flow

Here is our updated mental model of how PostgreSQL processes a query:

```
                +-------------------+
                |   employees       |
                |   (all 10 rows)   |
                +--------+----------+
                         |
                Step 1: FROM
                         |
                         v
                +-------------------+
                |  All rows         |
                +--------+----------+
                         |
                Step 2: WHERE
                (filter individual rows)
                         |
                         v
                +-------------------+
                |  Filtered rows    |
                +--------+----------+
                         |
                Step 3: SELECT + Aggregates
                (collapse rows into
                 summary values)
                         |
                         v
                +-------------------+
                |  Single summary   |
                |  row              |
                +-------------------+
```

> **Key insight:** WHERE runs BEFORE aggregates. This means you cannot use WHERE to filter on the result of an aggregate. For that, you need HAVING, which we will learn in the next chapter.

---

## Common Mistakes

### Mistake 1: Mixing Aggregates with Regular Columns

```sql
-- Wrong: What name should PostgreSQL show with the MAX salary?
SELECT name, MAX(salary) FROM employees;
-- ERROR: column "employees.name" must appear in the GROUP BY clause

-- Right: If you want the name of the highest-paid person, use a subquery or ORDER BY
SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 1;
```

This is one of the most common SQL mistakes. When you use an aggregate like MAX(salary), PostgreSQL collapses all rows into one. But which `name` should it pick? It does not know, so it gives you an error.

### Mistake 2: Using COUNT(column) When You Mean COUNT(*)

```sql
-- These are different!
SELECT COUNT(*)          AS all_rows;       -- Counts every row
SELECT COUNT(department) AS dept_values;    -- Counts non-NULL departments only
```

If you want to count total rows, use `COUNT(*)`. Use `COUNT(column)` only when you specifically want to count non-NULL values.

### Mistake 3: Forgetting That AVG Ignores NULLs

```sql
-- If you have: 100, 200, NULL, 400
-- AVG = (100 + 200 + 400) / 3 = 233.33
-- NOT:  (100 + 200 + 0 + 400) / 4 = 175.00
```

### Mistake 4: Trying to Filter Aggregates with WHERE

```sql
-- Wrong: WHERE runs before aggregates
SELECT department, AVG(salary)
FROM employees
WHERE AVG(salary) > 60000   -- ERROR!
GROUP BY department;

-- Right: Use HAVING (covered in the next chapter)
SELECT department, AVG(salary)
FROM employees
GROUP BY department
HAVING AVG(salary) > 60000;
```

---

## Best Practices

1. **Always alias your aggregates.** `SELECT COUNT(*) FROM employees` gives you a column named `count`. `SELECT COUNT(*) AS total_employees` is self-documenting.

2. **Use ROUND with AVG.** Averages often produce many decimal places. ROUND(AVG(col), 2) keeps results clean.

3. **Use COUNT(*) for total row counts.** It is the fastest and clearest way to count rows.

4. **Be aware of NULL behavior.** Know that SUM, AVG, MIN, and MAX all ignore NULLs. Use COALESCE if you need to treat NULL as zero.

5. **Do not mix aggregates with non-aggregated columns** unless you use GROUP BY (next chapter).

---

## Quick Summary

```
+-----------------+---------------------------------------------+
| Function        | What It Does                                |
+-----------------+---------------------------------------------+
| COUNT(*)        | Counts all rows                             |
| COUNT(column)   | Counts non-NULL values in a column          |
| COUNT(DISTINCT) | Counts unique non-NULL values               |
| SUM(column)     | Adds up all values                          |
| AVG(column)     | Calculates the average (ignores NULLs)      |
| MIN(column)     | Finds the smallest value                    |
| MAX(column)     | Finds the largest value                     |
| ROUND(value, n) | Rounds to n decimal places                  |
+-----------------+---------------------------------------------+
```

---

## Key Points

- Aggregate functions collapse many rows into a single summary value.
- COUNT(*) counts all rows. COUNT(column) counts non-NULL values only.
- COUNT(DISTINCT column) counts unique values.
- SUM and AVG only work with numeric columns. MIN and MAX work with numbers, text, and dates.
- All aggregate functions except COUNT(*) ignore NULL values.
- AVG ignores NULLs in both the sum and the count (which can be surprising).
- You cannot mix aggregate and non-aggregate columns in SELECT without GROUP BY.
- WHERE filters rows BEFORE aggregation. To filter after aggregation, use HAVING (next chapter).
- Always use aliases and ROUND to make aggregate results readable.

---

## Practice Questions

1. Write a query to find the total number of employees and the total salary budget.

2. What is the difference between `COUNT(*)` and `COUNT(department)`? When would they give different results?

3. Write a query to find the average salary of employees hired in 2020 or later. Round to 2 decimal places.

4. If a column has values 10, 20, NULL, and 40, what does AVG return? What does SUM return? What does COUNT(*) return? What does COUNT(column) return?

5. Write a query that shows the lowest salary, highest salary, and the difference between them (the salary range).

---

## Exercises

### Exercise 1: Company Dashboard

Write a single query that produces a "company dashboard" showing:
- Total number of employees
- Total salary budget
- Average salary (rounded to 2 decimal places)
- Lowest salary
- Highest salary
- Number of departments

### Exercise 2: Department Comparison

Write separate queries to find the average salary for each department (Engineering, Sales, Marketing, HR). Which department has the highest average? Which has the lowest?

(Hint: In the next chapter, you will learn how to do this in a single query with GROUP BY.)

### Exercise 3: Tenure Analysis

Write queries to answer:
1. When was the first employee hired? (Earliest hire date)
2. When was the most recent hire? (Latest hire date)
3. How many employees were hired in 2020?

---

## What Is Next?

Right now, to compare departments, you need to write a separate query for each one. That is tedious and does not scale. In the next chapter, you will learn **GROUP BY** and **HAVING** — tools that let you calculate aggregates for each group in a single query. Instead of asking "What is the average salary in Engineering?" then "What is the average salary in Sales?" you will be able to ask "What is the average salary in EACH department?" with one query.
