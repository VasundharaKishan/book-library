# Chapter 8: WHERE Clause — Filtering Your Data

## What You Will Learn

In this chapter, you will learn how to:

- Filter rows using the WHERE clause
- Use comparison operators (=, <>, <, >, <=, >=)
- Combine conditions with AND, OR, and NOT
- Check for values within a list using IN
- Find values within a range using BETWEEN
- Search for text patterns with LIKE and ILIKE
- Handle missing data with IS NULL and IS NOT NULL
- Understand operator precedence when combining conditions

## Why This Chapter Matters

In the previous chapter, you learned how to retrieve data — but you got all of it every time. Imagine going to a library and asking, "Show me every book you have." That is not very helpful when you are looking for mystery novels published after 2020.

The WHERE clause is your filter. It lets you say, "Only show me the rows that match these conditions." In the real world, nearly every query you write will have a WHERE clause. Whether you are looking up a customer by email, finding overdue invoices, or checking which products are low on stock, WHERE is the tool that narrows millions of rows down to exactly what you need.

Without WHERE, SQL would be like a search engine that always returns every web page on the internet.

---

## Our Practice Table

We will continue using the employees table from Chapter 7:

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

## The WHERE Clause — Basic Syntax

The WHERE clause goes after FROM and before any ORDER BY:

```sql
SELECT columns
FROM table_name
WHERE condition;
```

Think of WHERE like a bouncer at a club. Every row in the table walks up to the door. The WHERE clause checks each row: "Do you meet the condition?" If yes, the row gets through. If no, it is turned away.

```
                +-------------------+
                |   employees       |
                |   (all 10 rows)   |
                +--------+----------+
                         |
                WHERE department = 'Sales'
                "Does this row match?"
                         |
                    +----+----+
                    |         |
                  Yes         No
                    |         |
                    v         v
              +----------+ (discarded)
              | Matching |
              |   rows   |
              +----------+
```

---

## Comparison Operators

These operators compare a column value to something:

```
+----------+------------------------+-----------------------------------+
| Operator | Meaning                | Example                           |
+----------+------------------------+-----------------------------------+
| =        | Equal to               | department = 'Sales'              |
| <> or != | Not equal to           | department <> 'HR'                |
| <        | Less than              | salary < 60000                    |
| >        | Greater than           | salary > 80000                    |
| <=       | Less than or equal     | salary <= 65000                   |
| >=       | Greater than or equal  | salary >= 70000                   |
+----------+------------------------+-----------------------------------+
```

### Equal To (=)

```sql
SELECT name, department, salary
FROM employees
WHERE department = 'Engineering';
```

**Line-by-line breakdown:**

- `SELECT name, department, salary` — The columns we want to see.
- `FROM employees` — The table to search.
- `WHERE department = 'Engineering'` — Only include rows where the department column contains exactly 'Engineering'.

**Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| Alice Johnson    | Engineering | 85000.00  |
| Carol Williams   | Engineering | 92000.00  |
| Frank Lee        | Engineering | 78000.00  |
+------------------+-------------+-----------+
(3 rows)
```

> **Important:** Text values in SQL must be wrapped in single quotes: `'Engineering'`, not `"Engineering"`. Double quotes are for column names and aliases in PostgreSQL.

### Not Equal To (<>)

```sql
SELECT name, department
FROM employees
WHERE department <> 'Sales';
```

**Result:**

```
+------------------+-------------+
| name             | department  |
+------------------+-------------+
| Alice Johnson    | Engineering |
| Bob Smith        | Marketing   |
| Carol Williams   | Engineering |
| Eva Martinez     | Marketing   |
| Frank Lee        | Engineering |
| Henry Wilson     | HR          |
| Ivy Chen         | HR          |
+------------------+-------------+
(7 rows)
```

Everyone except the Sales department. You can also use `!=` instead of `<>` — they mean the same thing. The `<>` syntax is the SQL standard, while `!=` is more common in programming languages.

### Greater Than (>) and Less Than (<)

```sql
SELECT name, salary
FROM employees
WHERE salary > 80000;
```

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Alice Johnson    | 85000.00  |
| Carol Williams   | 92000.00  |
+------------------+-----------+
(2 rows)
```

```sql
SELECT name, salary
FROM employees
WHERE salary < 60000;
```

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| David Brown      | 58000.00  |
| Henry Wilson     | 55000.00  |
| Ivy Chen         | 59000.00  |
+------------------+-----------+
(3 rows)
```

### Comparing Dates

Dates work with comparison operators too. Think of dates as a timeline — "less than" means earlier, "greater than" means later:

```sql
SELECT name, hire_date
FROM employees
WHERE hire_date >= '2021-01-01';
```

**Result:**

```
+------------------+------------+
| name             | hire_date  |
+------------------+------------+
| David Brown      | 2021-01-10 |
| Frank Lee        | 2022-02-14 |
| Henry Wilson     | 2021-06-18 |
| Jack Davis       | 2023-03-20 |
+------------------+------------+
(4 rows)
```

Employees hired on or after January 1, 2021.

---

## Combining Conditions: AND, OR, NOT

Real-world questions often have multiple parts: "Who works in Engineering AND earns more than 80,000?" The logical operators AND, OR, and NOT let you combine conditions.

### AND — Both Conditions Must Be True

```sql
SELECT name, department, salary
FROM employees
WHERE department = 'Engineering'
  AND salary > 80000;
```

**Line-by-line breakdown:**

- `WHERE department = 'Engineering'` — First condition: must be in Engineering.
- `AND salary > 80000` — Second condition: must also earn more than 80,000.
- Both conditions must be true for a row to appear in the results.

**Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| Alice Johnson    | Engineering | 85000.00  |
| Carol Williams   | Engineering | 92000.00  |
+------------------+-------------+-----------+
(2 rows)
```

Frank Lee is in Engineering but earns 78,000, so he does not pass the salary check.

Think of AND like a checklist at airport security. You need a valid ID AND a boarding pass. If you have only one, you do not get through.

### OR — At Least One Condition Must Be True

```sql
SELECT name, department, salary
FROM employees
WHERE department = 'Sales'
   OR department = 'Marketing';
```

**Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| Bob Smith        | Marketing   | 62000.00  |
| David Brown      | Sales       | 58000.00  |
| Eva Martinez     | Marketing   | 65000.00  |
| Grace Kim        | Sales       | 61000.00  |
| Jack Davis       | Sales       | 63000.00  |
+------------------+-------------+-----------+
(5 rows)
```

A row only needs to match one of the conditions. Think of OR like a restaurant menu: "Would you like coffee OR tea?" Either one works.

### NOT — Reverse a Condition

```sql
SELECT name, department
FROM employees
WHERE NOT department = 'Engineering';
```

**Result:**

```
+------------------+-------------+
| name             | department  |
+------------------+-------------+
| Bob Smith        | Marketing   |
| David Brown      | Sales       |
| Eva Martinez     | Marketing   |
| Grace Kim        | Sales       |
| Henry Wilson     | HR          |
| Ivy Chen         | HR          |
| Jack Davis       | Sales       |
+------------------+-------------+
(7 rows)
```

NOT flips the condition. "Not Engineering" means everyone who is NOT in Engineering. This gives the same result as `department <> 'Engineering'`, but NOT becomes more powerful when combined with other operators like IN and BETWEEN.

---

## IN — Checking Against a List

When you want to check if a value matches any item in a list, use IN instead of writing multiple OR conditions:

```sql
-- The long way with OR
SELECT name, department
FROM employees
WHERE department = 'Sales'
   OR department = 'Marketing'
   OR department = 'HR';

-- The short way with IN
SELECT name, department
FROM employees
WHERE department IN ('Sales', 'Marketing', 'HR');
```

Both queries produce the same result:

```
+------------------+-------------+
| name             | department  |
+------------------+-------------+
| Bob Smith        | Marketing   |
| David Brown      | Sales       |
| Eva Martinez     | Marketing   |
| Grace Kim        | Sales       |
| Henry Wilson     | HR          |
| Ivy Chen         | HR          |
| Jack Davis       | Sales       |
+------------------+-------------+
(7 rows)
```

IN is cleaner and easier to read, especially with long lists. Think of it like a guest list at a party: "Is your name IN the list? Come on in."

### NOT IN — Excluding a List

```sql
SELECT name, department
FROM employees
WHERE department NOT IN ('Engineering', 'HR');
```

**Result:**

```
+------------------+-------------+
| name             | department  |
+------------------+-------------+
| Bob Smith        | Marketing   |
| David Brown      | Sales       |
| Eva Martinez     | Marketing   |
| Grace Kim        | Sales       |
| Jack Davis       | Sales       |
+------------------+-------------+
(5 rows)
```

---

## BETWEEN — Range Checking

BETWEEN checks if a value falls within a range (inclusive on both ends):

```sql
SELECT name, salary
FROM employees
WHERE salary BETWEEN 60000 AND 75000;
```

**Line-by-line breakdown:**

- `BETWEEN 60000 AND 75000` — This includes 60,000 and 75,000 themselves. It is the same as writing `salary >= 60000 AND salary <= 75000`.

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Bob Smith        | 62000.00  |
| Eva Martinez     | 65000.00  |
| Grace Kim        | 61000.00  |
| Jack Davis       | 63000.00  |
+------------------+-----------+
(4 rows)
```

### BETWEEN with Dates

```sql
SELECT name, hire_date
FROM employees
WHERE hire_date BETWEEN '2020-01-01' AND '2021-12-31';
```

**Result:**

```
+------------------+------------+
| name             | hire_date  |
+------------------+------------+
| Alice Johnson    | 2020-03-15 |
| David Brown      | 2021-01-10 |
| Eva Martinez     | 2020-09-05 |
| Henry Wilson     | 2021-06-18 |
| Ivy Chen         | 2020-12-01 |
+------------------+------------+
(5 rows)
```

Employees hired during 2020 or 2021.

### NOT BETWEEN

```sql
SELECT name, salary
FROM employees
WHERE salary NOT BETWEEN 60000 AND 80000;
```

**Result:**

```
+------------------+-----------+
| name             | salary    |
+------------------+-----------+
| Carol Williams   | 92000.00  |
| Alice Johnson    | 85000.00  |
| David Brown      | 58000.00  |
| Henry Wilson     | 55000.00  |
| Ivy Chen         | 59000.00  |
+------------------+-----------+
(5 rows)
```

---

## LIKE and ILIKE — Pattern Matching

LIKE lets you search for text patterns. It uses two special wildcard characters:

```
+-----------+-------------------------------------------+
| Wildcard  | Meaning                                   |
+-----------+-------------------------------------------+
| %         | Matches any sequence of characters        |
|           | (including zero characters)                |
| _         | Matches exactly one character              |
+-----------+-------------------------------------------+
```

### The % Wildcard — Any Number of Characters

```sql
-- Names that start with 'A'
SELECT name FROM employees
WHERE name LIKE 'A%';
```

**Result:**

```
+------------------+
| name             |
+------------------+
| Alice Johnson    |
+------------------+
(1 row)
```

```sql
-- Names that end with 'son'
SELECT name FROM employees
WHERE name LIKE '%son';
```

**Result:**

```
+------------------+
| name             |
+------------------+
| Alice Johnson    |
| Henry Wilson     |
+------------------+
(2 rows)
```

```sql
-- Names that contain 'ar'
SELECT name FROM employees
WHERE name LIKE '%ar%';
```

**Result:**

```
+------------------+
| name             |
+------------------+
| Carol Williams   |
| Eva Martinez     |
+------------------+
(2 rows)
```

Think of `%` like a wildcard in card games — it can stand for anything.

### The _ Wildcard — Exactly One Character

```sql
-- Names where the second character is 'v'
SELECT name FROM employees
WHERE name LIKE '_v%';
```

**Result:**

```
+------------------+
| name             |
+------------------+
| Eva Martinez     |
| Ivy Chen         |
+------------------+
(2 rows)
```

The `_` matches exactly one character, then `v` must be the second character, then `%` matches the rest.

### ILIKE — Case-Insensitive Pattern Matching

LIKE is case-sensitive. ILIKE is the PostgreSQL extension that ignores case:

```sql
-- LIKE is case-sensitive (this finds nothing because 'engineering' != 'Engineering')
SELECT name, department FROM employees
WHERE department LIKE 'engineering';
```

**Result:**

```
(0 rows)
```

```sql
-- ILIKE ignores case (this works!)
SELECT name, department FROM employees
WHERE department ILIKE 'engineering';
```

**Result:**

```
+------------------+-------------+
| name             | department  |
+------------------+-------------+
| Alice Johnson    | Engineering |
| Carol Williams   | Engineering |
| Frank Lee        | Engineering |
+------------------+-------------+
(3 rows)
```

> **Note:** ILIKE is a PostgreSQL-specific feature. In other databases like MySQL, LIKE is case-insensitive by default. In SQL Server, you would use `LIKE` with a case-insensitive collation.

### Common LIKE Patterns

```
+------------------+-----------------------------------------+
| Pattern          | Matches                                 |
+------------------+-----------------------------------------+
| 'A%'             | Starts with 'A'                         |
| '%son'           | Ends with 'son'                         |
| '%art%'          | Contains 'art' anywhere                 |
| '_a%'            | Second character is 'a'                 |
| '____'           | Exactly 4 characters long               |
| 'A%n'            | Starts with 'A' and ends with 'n'       |
+------------------+-----------------------------------------+
```

---

## IS NULL and IS NOT NULL

In SQL, NULL means "unknown" or "no value." It is not zero, not an empty string — it is the absence of a value. Think of it like a blank space on a form that was never filled in.

Let us add an employee with a missing department to demonstrate:

```sql
INSERT INTO employees (name, department, salary, hire_date)
VALUES ('Karen Null', 'Temp', 45000.00, '2024-01-15');

UPDATE employees SET department = NULL WHERE name = 'Karen Null';
```

Now here is the critical rule: **you cannot use = or <> to check for NULL**. You must use IS NULL or IS NOT NULL.

```sql
-- WRONG: This will NOT find Karen
SELECT name FROM employees
WHERE department = NULL;
-- Returns: (0 rows)  <-- Nothing! Even though Karen has NULL department

-- RIGHT: Use IS NULL
SELECT name, department FROM employees
WHERE department IS NULL;
```

**Result:**

```
+------------------+-------------+
| name             | department  |
+------------------+-------------+
| Karen Null       | NULL        |
+------------------+-------------+
(1 row)
```

Why does `= NULL` not work? Because NULL means "unknown." Is an unknown value equal to another unknown value? SQL says "I do not know" — which is not true, so the row is excluded. It is like asking, "Is the monster under the bed the same as the monster in the closet?" If you have never seen either one, you cannot say yes.

### IS NOT NULL — Finding Rows That Have Values

```sql
SELECT name, department FROM employees
WHERE department IS NOT NULL;
```

This returns all employees who have a department assigned (all 10 original employees, excluding Karen).

Let us clean up our test data:

```sql
DELETE FROM employees WHERE name = 'Karen Null';
```

---

## Operator Precedence — Order of Operations

When you combine AND, OR, and NOT, SQL follows a specific order, just like math follows "multiplication before addition":

```
+----------+---------------------------+
| Priority | Operator                  |
+----------+---------------------------+
| 1 (high) | NOT                       |
| 2        | AND                       |
| 3 (low)  | OR                        |
+----------+---------------------------+
```

This means AND is evaluated before OR. This can cause surprising results:

### The Trap

```sql
-- What does this return?
SELECT name, department, salary
FROM employees
WHERE department = 'Sales'
   OR department = 'Marketing'
  AND salary > 63000;
```

You might expect: "Sales or Marketing employees who earn more than 63,000."

But because AND is evaluated first, PostgreSQL reads it as:

```
department = 'Sales'
OR
(department = 'Marketing' AND salary > 63000)
```

**Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| David Brown      | Sales       | 58000.00  |
| Eva Martinez     | Marketing   | 65000.00  |
| Grace Kim        | Sales       | 61000.00  |
| Jack Davis       | Sales       | 63000.00  |
+------------------+-------------+-----------+
(4 rows)
```

ALL Sales employees appear (regardless of salary), plus only Marketing employees earning more than 63,000. David Brown from Sales at 58,000 got through even though you might not have intended that.

### The Fix — Use Parentheses

Always use parentheses to make your intentions clear:

```sql
-- "Sales or Marketing employees" who earn more than 63,000
SELECT name, department, salary
FROM employees
WHERE (department = 'Sales' OR department = 'Marketing')
  AND salary > 63000;
```

**Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| Eva Martinez     | Marketing   | 65000.00  |
+------------------+-------------+-----------+
(1 row)
```

Now the parentheses ensure OR is evaluated first, then AND. Only Eva qualifies — she is in Marketing and earns more than 63,000.

---

## Combining Multiple Conditions — Practical Examples

### Example 1: Complex Employee Search

"Find engineers hired after 2019 who earn between 75,000 and 90,000."

```sql
SELECT name, department, salary, hire_date
FROM employees
WHERE department = 'Engineering'
  AND hire_date > '2019-12-31'
  AND salary BETWEEN 75000 AND 90000;
```

**Result:**

```
+------------------+-------------+-----------+------------+
| name             | department  | salary    | hire_date  |
+------------------+-------------+-----------+------------+
| Alice Johnson    | Engineering | 85000.00  | 2020-03-15 |
| Frank Lee        | Engineering | 78000.00  | 2022-02-14 |
+------------------+-------------+-----------+------------+
(2 rows)
```

### Example 2: Name Search

"Find employees whose last name starts with 'W' or 'D'."

```sql
SELECT name, department
FROM employees
WHERE name LIKE '%W%'
  AND (name LIKE '% W%' OR name LIKE '% D%');
```

A simpler approach:

```sql
SELECT name, department
FROM employees
WHERE name LIKE '% W%'
   OR name LIKE '% D%';
```

**Result:**

```
+------------------+-------------+
| name             | department  |
+------------------+-------------+
| Carol Williams   | Engineering |
| Henry Wilson     | HR          |
| David Brown      | Sales       |
| Jack Davis       | Sales       |
+------------------+-------------+
(4 rows)
```

### Example 3: Exclusion Query

"Find everyone who is NOT in Engineering or HR and earns at least 60,000."

```sql
SELECT name, department, salary
FROM employees
WHERE department NOT IN ('Engineering', 'HR')
  AND salary >= 60000;
```

**Result:**

```
+------------------+-------------+-----------+
| name             | department  | salary    |
+------------------+-------------+-----------+
| Bob Smith        | Marketing   | 62000.00  |
| Eva Martinez     | Marketing   | 65000.00  |
| Grace Kim        | Sales       | 61000.00  |
| Jack Davis       | Sales       | 63000.00  |
+------------------+-------------+-----------+
(4 rows)
```

---

## Updated Mental Model

Here is how SELECT works now with WHERE added:

```
                +-------------------+
                |   employees       |
                |   (all 10 rows)   |
                +--------+----------+
                         |
                Step 1: FROM
                "Open the filing cabinet"
                         |
                         v
                +-------------------+
                |  All rows from    |
                |  employees table  |
                +--------+----------+
                         |
                Step 2: WHERE
                "Check each row against
                 the conditions"
                         |
                         v
                +-------------------+
                |  Only rows that   |
                |  pass the filter  |
                +--------+----------+
                         |
                Step 3: SELECT
                "Pick the columns
                 you want to see"
                         |
                         v
                +-------------------+
                |  Final results    |
                +-------------------+
```

---

## Common Mistakes

### Mistake 1: Using = Instead of IS NULL

```sql
-- Wrong: This will always return 0 rows
SELECT * FROM employees WHERE department = NULL;

-- Right: Use IS NULL
SELECT * FROM employees WHERE department IS NULL;
```

### Mistake 2: Forgetting Quotes Around Text

```sql
-- Wrong: PostgreSQL thinks Sales is a column name
SELECT * FROM employees WHERE department = Sales;
-- ERROR: column "sales" does not exist

-- Right: Text values need single quotes
SELECT * FROM employees WHERE department = 'Sales';
```

### Mistake 3: Ignoring Operator Precedence

```sql
-- Probably wrong: AND binds tighter than OR
SELECT * FROM employees
WHERE department = 'Sales' OR department = 'HR' AND salary > 60000;

-- Right: Use parentheses to be explicit
SELECT * FROM employees
WHERE (department = 'Sales' OR department = 'HR') AND salary > 60000;
```

### Mistake 4: Using LIKE When = Would Do

```sql
-- Works but unnecessary — no wildcards used
SELECT * FROM employees WHERE name LIKE 'Alice Johnson';

-- Better: Use = for exact matches (faster too)
SELECT * FROM employees WHERE name = 'Alice Johnson';
```

### Mistake 5: Case Sensitivity with LIKE

```sql
-- Returns nothing because LIKE is case-sensitive
SELECT * FROM employees WHERE department LIKE 'sales';

-- Use ILIKE for case-insensitive matching
SELECT * FROM employees WHERE department ILIKE 'sales';
```

---

## Best Practices

1. **Always use parentheses when mixing AND and OR.** Even if you know the precedence rules, parentheses make your code readable for others (and your future self).

2. **Use IN instead of multiple ORs.** `WHERE x IN (1, 2, 3)` is cleaner than `WHERE x = 1 OR x = 2 OR x = 3`.

3. **Use BETWEEN for range checks.** It is more readable than `x >= 10 AND x <= 20`.

4. **Use IS NULL, never = NULL.** This is the most common beginner mistake with SQL.

5. **Use ILIKE when case does not matter.** If users might type "sales", "Sales", or "SALES", use ILIKE to catch all variations.

6. **Put the most selective condition first.** While PostgreSQL's optimizer usually handles this, writing your most restrictive filter first makes the query easier to read.

---

## Quick Summary

```
+-------------------+-------------------------------------------+
| Concept           | Example                                   |
+-------------------+-------------------------------------------+
| Equal             | WHERE name = 'Alice Johnson'              |
| Not equal         | WHERE department <> 'HR'                  |
| Greater than      | WHERE salary > 70000                      |
| Less than         | WHERE salary < 60000                      |
| AND               | WHERE dept = 'Sales' AND salary > 60000   |
| OR                | WHERE dept = 'Sales' OR dept = 'HR'       |
| NOT               | WHERE NOT department = 'Sales'            |
| IN                | WHERE dept IN ('Sales', 'HR')             |
| BETWEEN           | WHERE salary BETWEEN 50000 AND 80000      |
| LIKE              | WHERE name LIKE 'A%'                      |
| ILIKE             | WHERE name ILIKE 'alice%'                 |
| IS NULL           | WHERE department IS NULL                  |
| IS NOT NULL       | WHERE department IS NOT NULL              |
+-------------------+-------------------------------------------+
```

---

## Key Points

- WHERE filters rows before they appear in results. It goes after FROM.
- Use `=` for exact matches and `<>` (or `!=`) for "not equal."
- AND requires all conditions to be true. OR requires at least one.
- IN checks if a value is in a list — cleaner than multiple ORs.
- BETWEEN checks inclusive ranges and works with numbers, dates, and text.
- LIKE uses `%` (any characters) and `_` (one character) for pattern matching.
- ILIKE is the case-insensitive version of LIKE (PostgreSQL only).
- Always use IS NULL and IS NOT NULL to check for missing values, never `= NULL`.
- AND has higher precedence than OR. Use parentheses to be safe.

---

## Practice Questions

1. Write a query to find all employees in the HR department.

2. Write a query to find employees who earn between 60,000 and 80,000 (inclusive).

3. What is wrong with this query?
   ```sql
   SELECT * FROM employees WHERE salary = NULL;
   ```

4. Write a query to find employees whose names contain the letter 'a' (case-insensitive).

5. Explain what this query returns and why:
   ```sql
   SELECT name, department, salary
   FROM employees
   WHERE department = 'Engineering'
      OR salary > 80000
     AND hire_date > '2020-01-01';
   ```

---

## Exercises

### Exercise 1: Employee Search Tool

Write queries to answer each of these questions:
1. Who works in Sales or Marketing?
2. Which engineers were hired before 2021?
3. Who earns less than the average of all salaries (you can calculate the average mentally or just pick a reasonable number for now)?

### Exercise 2: Pattern Matching Detective

Using LIKE and ILIKE, write queries to find:
1. All employees whose first name starts with a vowel (A, E, I, O, U).
2. All employees whose last name is exactly 3 characters long.
3. All employees whose name contains "an" anywhere.

### Exercise 3: Complex Conditions

Write a single query that finds employees who meet ALL of these criteria:
- Not in the Engineering department
- Hired in 2020 or later
- Earning between 55,000 and 65,000

---

## What Is Next?

You can now filter data, but the results come back in whatever order PostgreSQL feels like. In the next chapter, you will learn how to **sort** your results with ORDER BY and **limit** how many rows you get back with LIMIT. Together with WHERE, these tools let you ask precise questions like "Show me the top 3 highest-paid engineers hired after 2020."
