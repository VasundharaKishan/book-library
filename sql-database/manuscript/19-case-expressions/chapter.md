# Chapter 19: CASE Expressions

## What You Will Learn

In this chapter, you will learn how to make decisions inside your SQL queries. You will discover how to use CASE expressions to transform data, categorize results, and build conditional logic directly within SELECT, WHERE, ORDER BY, and aggregate functions. You will also learn about COALESCE and NULLIF, two handy functions that deal with NULL values.

## Why This Chapter Matters

Imagine you are a teacher looking at a list of student scores. You do not just want to see the numbers. You want to see labels like "Pass" or "Fail" next to each score. Or imagine you are a manager who wants to group employees into salary bands like "Low," "Medium," and "High."

Without CASE expressions, you would need to pull the raw data out of the database and then write code in another programming language to add these labels. With CASE, you can do it all inside a single SQL query. This saves time, reduces complexity, and keeps your logic close to your data.

CASE expressions are one of the most practical tools in SQL. You will use them constantly in real-world reporting, data analysis, and application development.

---

## Setting Up Our Practice Data

Before we begin, let us create some tables to work with throughout this chapter.

```sql
CREATE TABLE students (
    student_id   SERIAL PRIMARY KEY,
    first_name   VARCHAR(50),
    last_name    VARCHAR(50),
    score        INTEGER,
    grade_letter VARCHAR(2)
);

INSERT INTO students (first_name, last_name, score, grade_letter) VALUES
('Alice',   'Johnson',  92,   NULL),
('Bob',     'Smith',    85,   NULL),
('Charlie', 'Brown',    67,   NULL),
('Diana',   'Ross',     45,   NULL),
('Edward',  'Wilson',   78,   NULL),
('Fiona',   'Clark',    55,   NULL),
('George',  'Taylor',   91,   NULL),
('Hannah',  'Lee',      73,   NULL);

CREATE TABLE employees (
    employee_id  SERIAL PRIMARY KEY,
    first_name   VARCHAR(50),
    last_name    VARCHAR(50),
    department   VARCHAR(50),
    salary       INTEGER,
    status       VARCHAR(20),
    manager_id   INTEGER
);

INSERT INTO employees (first_name, last_name, department, salary, status, manager_id) VALUES
('Alice',   'Johnson',  'Engineering', 95000,  'active',      NULL),
('Bob',     'Smith',    'Engineering', 78000,  'active',      1),
('Charlie', 'Brown',    'Marketing',   62000,  'active',      1),
('Diana',   'Ross',     'Marketing',   58000,  'on_leave',    3),
('Edward',  'Wilson',   'Sales',       72000,  'active',      1),
('Fiona',   'Clark',    'Sales',       45000,  'terminated',  5),
('George',  'Taylor',   'Engineering', 110000, 'active',      1),
('Hannah',  'Lee',      'HR',          65000,  'active',      1),
('Ivan',    'Petrov',   'HR',          NULL,   'active',      8);
```

---

## Simple CASE: The Switch Statement

The Simple CASE expression works like a light switch panel. You give it a value, and it checks that value against a list of options. When it finds a match, it returns the corresponding result.

Think of it like a vending machine. You press button A, you get chips. You press button B, you get a candy bar. Each button maps to one specific item.

### Syntax

```
CASE expression
    WHEN value1 THEN result1
    WHEN value2 THEN result2
    WHEN value3 THEN result3
    ELSE default_result
END
```

### Example: Converting Status Codes to Readable Labels

```sql
SELECT
    first_name,
    last_name,
    status,
    CASE status
        WHEN 'active'     THEN 'Currently Working'
        WHEN 'on_leave'   THEN 'On Leave'
        WHEN 'terminated' THEN 'No Longer Employed'
        ELSE 'Unknown'
    END AS status_label
FROM employees;
```

**Result:**

```
 first_name | last_name | status     | status_label
------------+-----------+------------+---------------------
 Alice      | Johnson   | active     | Currently Working
 Bob        | Smith     | active     | Currently Working
 Charlie    | Brown     | active     | Currently Working
 Diana      | Ross      | on_leave   | On Leave
 Edward     | Wilson    | active     | Currently Working
 Fiona      | Clark     | terminated | No Longer Employed
 George     | Taylor    | active     | Currently Working
 Hannah     | Lee       | active     | Currently Working
 Ivan       | Petrov    | active     | Currently Working
(9 rows)
```

**Line-by-Line Explanation:**

- `CASE status` -- We are examining the `status` column. This is the value we will compare.
- `WHEN 'active' THEN 'Currently Working'` -- If `status` equals `'active'`, return `'Currently Working'`.
- `WHEN 'on_leave' THEN 'On Leave'` -- If `status` equals `'on_leave'`, return `'On Leave'`.
- `WHEN 'terminated' THEN 'No Longer Employed'` -- If `status` equals `'terminated'`, return `'No Longer Employed'`.
- `ELSE 'Unknown'` -- If none of the above match, return `'Unknown'`. The ELSE is optional but recommended.
- `END AS status_label` -- Close the CASE block and give the resulting column the alias `status_label`.

### How Simple CASE Evaluates

```
+------------------+
|  CASE status     |
+------------------+
        |
        v
+------------------+     YES    +---------------------+
| status = 'active'|---------->| 'Currently Working' |
+------------------+            +---------------------+
        | NO
        v
+------------------+     YES    +---------------------+
| status = 'on_leave'|-------->| 'On Leave'          |
+------------------+            +---------------------+
        | NO
        v
+------------------+     YES    +---------------------+
| status = 'terminated'|------>| 'No Longer Employed'|
+------------------+            +---------------------+
        | NO
        v
+------------------+
|    ELSE          |
|   'Unknown'      |
+------------------+
```

The Simple CASE checks each WHEN from top to bottom. The moment it finds a match, it stops and returns that result. If nothing matches, it falls through to the ELSE.

---

## Searched CASE: The If/Else If Statement

The Searched CASE is more powerful than the Simple CASE. Instead of comparing one value against a list of options, each WHEN clause contains its own independent condition. This means you can test different columns, use comparison operators, and combine conditions.

Think of it like a series of questions a doctor asks. "Is your temperature above 102? Then you have a high fever. Is it between 99 and 102? Then you have a low fever. Otherwise, you are normal." Each question is a separate test.

### Syntax

```
CASE
    WHEN condition1 THEN result1
    WHEN condition2 THEN result2
    WHEN condition3 THEN result3
    ELSE default_result
END
```

Notice there is no expression after the word CASE. That is the key difference from Simple CASE.

### Example: Categorizing Salaries

```sql
SELECT
    first_name,
    last_name,
    salary,
    CASE
        WHEN salary >= 90000 THEN 'High'
        WHEN salary >= 60000 THEN 'Medium'
        WHEN salary IS NOT NULL THEN 'Low'
        ELSE 'Not Set'
    END AS salary_band
FROM employees;
```

**Result:**

```
 first_name | last_name | salary  | salary_band
------------+-----------+---------+------------
 Alice      | Johnson   |  95000  | High
 Bob        | Smith     |  78000  | Medium
 Charlie    | Brown     |  62000  | Medium
 Diana      | Ross      |  58000  | Low
 Edward     | Wilson    |  72000  | Medium
 Fiona      | Clark     |  45000  | Low
 George     | Taylor    | 110000  | High
 Hannah     | Lee       |  65000  | Medium
 Ivan       | Petrov    |  (null) | Not Set
(9 rows)
```

**Line-by-Line Explanation:**

- `CASE` -- Start a Searched CASE. No expression follows the word CASE.
- `WHEN salary >= 90000 THEN 'High'` -- If salary is 90,000 or more, label it "High."
- `WHEN salary >= 60000 THEN 'Medium'` -- If salary is between 60,000 and 89,999, label it "Medium." Notice we do not need to say `salary < 90000` because CASE checks conditions in order. If salary were 95,000, it would have already matched the first WHEN and stopped.
- `WHEN salary IS NOT NULL THEN 'Low'` -- If salary has a value but did not match the previous conditions, label it "Low."
- `ELSE 'Not Set'` -- If salary is NULL (none of the above conditions were true because comparisons with NULL return false), label it "Not Set."
- `END AS salary_band` -- Close the CASE and name the column `salary_band`.

> **Important:** CASE evaluates conditions from top to bottom and stops at the first match. The order of your WHEN clauses matters. Put the most specific conditions first.

---

## CASE in SELECT: Practical Categorization

We already saw CASE in SELECT above. Let us look at a more detailed example that grades students based on their scores.

### Example: Grading Students

```sql
SELECT
    first_name,
    last_name,
    score,
    CASE
        WHEN score >= 90 THEN 'A'
        WHEN score >= 80 THEN 'B'
        WHEN score >= 70 THEN 'C'
        WHEN score >= 60 THEN 'D'
        ELSE 'F'
    END AS letter_grade,
    CASE
        WHEN score >= 60 THEN 'Pass'
        ELSE 'Fail'
    END AS result
FROM students
ORDER BY score DESC;
```

**Result:**

```
 first_name | last_name | score | letter_grade | result
------------+-----------+-------+--------------+-------
 Alice      | Johnson   |    92 | A            | Pass
 George     | Taylor    |    91 | A            | Pass
 Bob        | Smith     |    85 | B            | Pass
 Edward     | Wilson    |    78 | C            | Pass
 Hannah     | Lee       |    73 | C            | Pass
 Charlie    | Brown     |    67 | D            | Pass
 Fiona      | Clark     |    55 | F            | Fail
 Diana      | Ross      |    45 | F            | Fail
(8 rows)
```

You can use multiple CASE expressions in the same SELECT. Each one creates an independent column. Here, we created both a `letter_grade` and a `result` column in one query.

---

## CASE in WHERE

You can use CASE inside a WHERE clause, though this is less common. It is useful when you need conditional filtering logic.

### Example: Filter Based on Department Rules

Suppose you want to find employees who are "underpaid" based on department-specific thresholds. Engineering employees should earn at least 80,000, while other departments should earn at least 55,000.

```sql
SELECT
    first_name,
    last_name,
    department,
    salary
FROM employees
WHERE salary < CASE
    WHEN department = 'Engineering' THEN 80000
    WHEN department = 'Sales'       THEN 60000
    ELSE 55000
END
AND salary IS NOT NULL;
```

**Result:**

```
 first_name | last_name | department  | salary
------------+-----------+-------------+-------
 Bob        | Smith     | Engineering | 78000
 Fiona      | Clark     | Sales       | 45000
(2 rows)
```

**Explanation:**

- Bob earns 78,000 in Engineering, which is below the 80,000 threshold for that department.
- Fiona earns 45,000 in Sales, which is below the 60,000 threshold for Sales.
- Other employees either meet their department threshold or have NULL salaries (filtered out by `AND salary IS NOT NULL`).

---

## CASE in ORDER BY

CASE in ORDER BY lets you create custom sorting orders that do not follow alphabetical or numerical rules.

### Example: Custom Department Sort Order

Suppose you want Engineering first, then Sales, then Marketing, then everything else.

```sql
SELECT
    first_name,
    department,
    salary
FROM employees
WHERE salary IS NOT NULL
ORDER BY
    CASE department
        WHEN 'Engineering' THEN 1
        WHEN 'Sales'       THEN 2
        WHEN 'Marketing'   THEN 3
        ELSE 4
    END,
    salary DESC;
```

**Result:**

```
 first_name | department  | salary
------------+-------------+--------
 George     | Engineering | 110000
 Alice      | Engineering |  95000
 Bob        | Engineering |  78000
 Edward     | Sales       |  72000
 Fiona      | Sales       |  45000
 Charlie    | Marketing   |  62000
 Diana      | Marketing   |  58000
 Hannah     | HR          |  65000
(8 rows)
```

**How it works:**

The CASE assigns a sort number to each department. Engineering gets 1, so it comes first. Within each department, we sort by salary in descending order. This gives you complete control over the display order.

---

## CASE with Aggregates: Pivot-Like Queries

One of the most powerful uses of CASE is combining it with aggregate functions to create pivot-table-like results. This lets you turn row values into columns.

### Example: Count Employees by Status per Department

```sql
SELECT
    department,
    COUNT(*) AS total,
    COUNT(CASE WHEN status = 'active'     THEN 1 END) AS active,
    COUNT(CASE WHEN status = 'on_leave'   THEN 1 END) AS on_leave,
    COUNT(CASE WHEN status = 'terminated' THEN 1 END) AS terminated
FROM employees
GROUP BY department
ORDER BY department;
```

**Result:**

```
 department  | total | active | on_leave | terminated
-------------+-------+--------+----------+-----------
 Engineering |     3 |      3 |        0 |          0
 HR          |     2 |      2 |        0 |          0
 Marketing   |     2 |      1 |        1 |          0
 Sales       |     2 |      1 |        0 |          1
(4 rows)
```

**Line-by-Line Explanation:**

- `COUNT(*)` -- Counts all employees in each department.
- `COUNT(CASE WHEN status = 'active' THEN 1 END)` -- For each row, if the status is `'active'`, CASE returns 1. If not, CASE returns NULL (because there is no ELSE). COUNT ignores NULLs, so it only counts the active employees.
- The same pattern repeats for `'on_leave'` and `'terminated'`.

This technique effectively pivots the `status` values from rows into columns.

### Example: Salary Summary by Department

```sql
SELECT
    department,
    SUM(salary) AS total_salary,
    SUM(CASE WHEN status = 'active' THEN salary ELSE 0 END) AS active_salary,
    ROUND(AVG(salary)) AS avg_salary,
    MAX(salary) AS max_salary,
    MIN(salary) AS min_salary
FROM employees
WHERE salary IS NOT NULL
GROUP BY department
ORDER BY total_salary DESC;
```

**Result:**

```
 department  | total_salary | active_salary | avg_salary | max_salary | min_salary
-------------+--------------+---------------+------------+------------+-----------
 Engineering |       283000 |        283000 |      94333 |     110000 |      78000
 Marketing   |       120000 |         62000 |      60000 |      62000 |      58000
 Sales       |       117000 |         72000 |      58500 |      72000 |      45000
 HR          |        65000 |         65000 |      65000 |      65000 |      65000
(4 rows)
```

Here, `active_salary` uses CASE inside SUM to only add up salaries of active employees. Diana is on leave, so her 58,000 salary is excluded from Marketing's `active_salary`.

---

## COALESCE: First Non-NULL Value

COALESCE is a function that takes a list of values and returns the first one that is not NULL. Think of it like a backup plan. "Try this first. If it is NULL, try this. If that is also NULL, use this default."

### Syntax

```
COALESCE(value1, value2, value3, ...)
```

### Example: Displaying a Fallback for Missing Salaries

```sql
SELECT
    first_name,
    last_name,
    salary,
    COALESCE(salary, 0) AS salary_or_zero,
    COALESCE(CAST(salary AS VARCHAR), 'Not Assigned') AS salary_display
FROM employees
WHERE department = 'HR';
```

**Result:**

```
 first_name | last_name | salary | salary_or_zero | salary_display
------------+-----------+--------+----------------+---------------
 Hannah     | Lee       |  65000 |          65000 | 65000
 Ivan       | Petrov    | (null) |              0 | Not Assigned
(2 rows)
```

**Explanation:**

- For Hannah, `salary` is 65,000 (not NULL), so COALESCE returns 65,000.
- For Ivan, `salary` is NULL, so COALESCE moves to the next value: 0 for the numeric version, or `'Not Assigned'` for the text version.

### COALESCE with Multiple Fallbacks

```sql
-- Imagine a contacts table with multiple phone fields
SELECT
    COALESCE(work_phone, mobile_phone, home_phone, 'No Phone') AS best_phone
FROM contacts;
```

This tries `work_phone` first. If that is NULL, it tries `mobile_phone`. If that is also NULL, it tries `home_phone`. If all three are NULL, it returns `'No Phone'`.

### How COALESCE Works

```
COALESCE(NULL, NULL, 42, 99)
         |     |     |
         v     v     v
        NULL? NULL? 42!  --> Returns 42 (first non-NULL)

COALESCE('hello', NULL, 'world')
          |
          v
        'hello'!  --> Returns 'hello' (first non-NULL)

COALESCE(NULL, NULL, NULL)
         |     |     |
         v     v     v
        NULL? NULL? NULL?  --> Returns NULL (no non-NULL found)
```

---

## NULLIF: Create NULL from a Specific Value

NULLIF does the opposite of COALESCE in a way. It takes two arguments. If they are equal, it returns NULL. If they are different, it returns the first argument.

### Syntax

```
NULLIF(value1, value2)
```

- If `value1 = value2`, return NULL.
- If `value1 != value2`, return `value1`.

### Example: Avoiding Division by Zero

NULLIF is most commonly used to prevent division-by-zero errors.

```sql
CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    list_price   NUMERIC(10,2),
    sale_price   NUMERIC(10,2)
);

INSERT INTO products (product_name, list_price, sale_price) VALUES
('Widget A', 25.00, 20.00),
('Widget B', 30.00, 30.00),
('Widget C', 15.00,  0.00),
('Widget D', 40.00, 35.00);
```

```sql
SELECT
    product_name,
    list_price,
    sale_price,
    ROUND(list_price / NULLIF(sale_price, 0), 2) AS price_ratio
FROM products;
```

**Result:**

```
 product_name | list_price | sale_price | price_ratio
--------------+------------+------------+------------
 Widget A     |      25.00 |      20.00 |        1.25
 Widget B     |      30.00 |      30.00 |        1.00
 Widget C     |      15.00 |       0.00 |      (null)
 Widget D     |      40.00 |      35.00 |        1.14
(4 rows)
```

**Explanation:**

- For Widget C, `sale_price` is 0. Without NULLIF, dividing by 0 would cause an error. `NULLIF(0, 0)` returns NULL, and dividing by NULL produces NULL instead of crashing.
- For all other products, `sale_price` is not 0, so NULLIF returns the original `sale_price` value, and division proceeds normally.

### Another Use: Treating Empty Strings as NULL

```sql
SELECT
    NULLIF(email, '') AS email_or_null
FROM users;
```

If `email` is an empty string `''`, NULLIF converts it to NULL. This is useful when some systems store empty strings instead of NULL for missing data.

---

## Practical Example: Complete Student Grading System

Let us bring everything together with a complete grading system.

```sql
SELECT
    first_name || ' ' || last_name AS student_name,
    score,
    CASE
        WHEN score >= 90 THEN 'A'
        WHEN score >= 80 THEN 'B'
        WHEN score >= 70 THEN 'C'
        WHEN score >= 60 THEN 'D'
        ELSE 'F'
    END AS letter_grade,
    CASE
        WHEN score >= 90 THEN 'Excellent'
        WHEN score >= 80 THEN 'Good'
        WHEN score >= 70 THEN 'Satisfactory'
        WHEN score >= 60 THEN 'Needs Improvement'
        ELSE 'Failing'
    END AS performance,
    CASE
        WHEN score >= 60 THEN 'Pass'
        ELSE 'Fail'
    END AS result,
    CASE
        WHEN score >= 90 THEN 4.0
        WHEN score >= 80 THEN 3.0
        WHEN score >= 70 THEN 2.0
        WHEN score >= 60 THEN 1.0
        ELSE 0.0
    END AS grade_points
FROM students
ORDER BY score DESC;
```

**Result:**

```
  student_name   | score | letter_grade | performance       | result | grade_points
-----------------+-------+--------------+-------------------+--------+-------------
 Alice Johnson   |    92 | A            | Excellent         | Pass   |          4.0
 George Taylor   |    91 | A            | Excellent         | Pass   |          4.0
 Bob Smith       |    85 | B            | Good              | Pass   |          3.0
 Edward Wilson   |    78 | C            | Satisfactory      | Pass   |          2.0
 Hannah Lee      |    73 | C            | Satisfactory      | Pass   |          2.0
 Charlie Brown   |    67 | D            | Needs Improvement | Pass   |          1.0
 Fiona Clark     |    55 | F            | Failing           | Fail   |          0.0
 Diana Ross      |    45 | F            | Failing           | Fail   |          0.0
(8 rows)
```

### Grade Distribution Summary

```sql
SELECT
    CASE
        WHEN score >= 90 THEN 'A'
        WHEN score >= 80 THEN 'B'
        WHEN score >= 70 THEN 'C'
        WHEN score >= 60 THEN 'D'
        ELSE 'F'
    END AS letter_grade,
    COUNT(*) AS num_students,
    ROUND(AVG(score), 1) AS avg_score,
    MIN(score) AS lowest,
    MAX(score) AS highest
FROM students
GROUP BY
    CASE
        WHEN score >= 90 THEN 'A'
        WHEN score >= 80 THEN 'B'
        WHEN score >= 70 THEN 'C'
        WHEN score >= 60 THEN 'D'
        ELSE 'F'
    END
ORDER BY
    MIN(score) DESC;
```

**Result:**

```
 letter_grade | num_students | avg_score | lowest | highest
--------------+--------------+-----------+--------+--------
 A            |            2 |      91.5 |     91 |      92
 B            |            1 |      85.0 |     85 |      85
 C            |            2 |      75.5 |     73 |      78
 D            |            1 |      67.0 |     67 |      67
 F            |            2 |      50.0 |     45 |      55
(5 rows)
```

> **Note:** When you use a CASE expression in GROUP BY, you must repeat the entire CASE expression. You cannot use the alias (`letter_grade`) in GROUP BY in standard SQL. PostgreSQL does allow column aliases in GROUP BY, but repeating the expression is the portable approach.

---

## Practical Example: Employee Status Dashboard

```sql
SELECT
    department,
    COUNT(*) AS headcount,
    SUM(COALESCE(salary, 0)) AS total_payroll,
    COUNT(CASE WHEN status = 'active' THEN 1 END) AS active_count,
    COUNT(CASE WHEN status = 'on_leave' THEN 1 END) AS leave_count,
    COUNT(CASE WHEN status = 'terminated' THEN 1 END) AS termed_count,
    ROUND(
        100.0 * COUNT(CASE WHEN status = 'active' THEN 1 END) / COUNT(*),
        1
    ) AS active_pct
FROM employees
GROUP BY department
ORDER BY headcount DESC;
```

**Result:**

```
 department  | headcount | total_payroll | active_count | leave_count | termed_count | active_pct
-------------+-----------+---------------+--------------+-------------+--------------+-----------
 Engineering |         3 |        283000 |            3 |           0 |            0 |      100.0
 Marketing   |         2 |        120000 |            1 |           1 |            0 |       50.0
 Sales       |         2 |        117000 |            1 |           0 |            1 |       50.0
 HR          |         2 |         65000 |            2 |           0 |            0 |      100.0
(4 rows)
```

This query combines CASE with aggregates and COALESCE to build a department dashboard in a single query.

---

## Common Mistakes

### Mistake 1: Forgetting END

```sql
-- WRONG: Missing END
SELECT
    CASE status
        WHEN 'active' THEN 'Working'
        WHEN 'on_leave' THEN 'Away'
    AS label
FROM employees;

-- ERROR: syntax error at or near "AS"
```

```sql
-- CORRECT: Always close with END
SELECT
    CASE status
        WHEN 'active' THEN 'Working'
        WHEN 'on_leave' THEN 'Away'
    END AS label
FROM employees;
```

### Mistake 2: Wrong Order of WHEN Clauses

```sql
-- WRONG: The second WHEN will never match
SELECT
    score,
    CASE
        WHEN score >= 60 THEN 'Pass'
        WHEN score >= 90 THEN 'Excellent'  -- Never reached!
        ELSE 'Fail'
    END AS result
FROM students;
```

A score of 95 matches `score >= 60` first and returns "Pass." It never gets to check `score >= 90`. Always put the most specific (highest threshold) condition first.

### Mistake 3: Mixing Simple CASE and Searched CASE Syntax

```sql
-- WRONG: Cannot use conditions with Simple CASE
SELECT
    CASE department
        WHEN salary > 90000 THEN 'High Paid'  -- ERROR!
    END
FROM employees;
```

Simple CASE compares against exact values. If you need conditions with operators like `>`, `<`, or `BETWEEN`, use Searched CASE (no expression after CASE).

### Mistake 4: Forgetting ELSE

```sql
-- Missing ELSE returns NULL for unmatched rows
SELECT
    CASE status
        WHEN 'active' THEN 'Working'
    END AS label
FROM employees;
-- 'on_leave' and 'terminated' employees get NULL
```

Always include ELSE unless you intentionally want NULL for unmatched cases.

### Mistake 5: Using COALESCE with Mismatched Types

```sql
-- WRONG: Mixing integer and text
SELECT COALESCE(salary, 'Not Set') FROM employees;
-- ERROR: COALESCE types integer and text cannot be matched

-- CORRECT: Cast to the same type
SELECT COALESCE(CAST(salary AS VARCHAR), 'Not Set') FROM employees;
```

---

## Best Practices

1. **Always include ELSE.** Even if you think all cases are covered, an ELSE clause acts as a safety net. It makes your intent clear and handles unexpected values.

2. **Order WHEN clauses carefully.** Put the most specific conditions first in Searched CASE. Remember that evaluation stops at the first match.

3. **Use meaningful aliases.** Always give your CASE expression an alias with `AS`. Without it, the column will have no useful name.

4. **Keep CASE expressions readable.** If a CASE has more than five or six WHEN clauses, consider whether a lookup table might be cleaner.

5. **Use COALESCE for NULL defaults.** It is cleaner than writing `CASE WHEN value IS NULL THEN default ELSE value END`.

6. **Use NULLIF to prevent division by zero.** Wrap the divisor in NULLIF(divisor, 0) to safely handle zero values.

7. **Use CASE with aggregates for pivot-like reports.** This is one of the most valuable patterns in real-world SQL.

---

## Quick Summary

```
+-------------------+------------------------------------------+
| Feature           | Description                              |
+-------------------+------------------------------------------+
| Simple CASE       | Compare one value against a list         |
|                   | CASE expr WHEN val THEN result END       |
+-------------------+------------------------------------------+
| Searched CASE     | Evaluate independent conditions          |
|                   | CASE WHEN cond THEN result END           |
+-------------------+------------------------------------------+
| CASE in SELECT    | Create computed/categorized columns      |
+-------------------+------------------------------------------+
| CASE in WHERE     | Conditional filtering                    |
+-------------------+------------------------------------------+
| CASE in ORDER BY  | Custom sort orders                       |
+-------------------+------------------------------------------+
| CASE + Aggregates | Pivot rows into columns                  |
+-------------------+------------------------------------------+
| COALESCE          | Returns first non-NULL value             |
|                   | COALESCE(a, b, c, default)               |
+-------------------+------------------------------------------+
| NULLIF            | Returns NULL if two values are equal     |
|                   | NULLIF(value, 0) prevents /0 errors      |
+-------------------+------------------------------------------+
```

---

## Key Points

- **Simple CASE** compares one expression against multiple values, like a switch statement.
- **Searched CASE** evaluates independent Boolean conditions, like an if/else if chain.
- CASE expressions work in **SELECT, WHERE, ORDER BY, GROUP BY**, and inside **aggregate functions**.
- Evaluation stops at the **first matching WHEN**. Order matters.
- **COALESCE** returns the first non-NULL value from a list of arguments.
- **NULLIF** returns NULL if two values are equal. It is most useful for preventing division-by-zero errors.
- Combining CASE with **COUNT, SUM,** and **AVG** lets you create pivot-table-like reports.
- Always include **ELSE** and always use **AS** to name your CASE columns.

---

## Practice Questions

1. What is the difference between Simple CASE and Searched CASE? When would you use one over the other?

2. What does the following expression return: `COALESCE(NULL, NULL, 'hello', 'world')`? Explain why.

3. Write a CASE expression that labels employees as "Senior" if their salary is 80,000 or more, "Mid-Level" if 50,000 or more, and "Junior" otherwise.

4. Why does `NULLIF(0, 0)` return NULL, and how does this help with division?

5. You have a CASE expression with these WHEN clauses in this order: `WHEN score >= 50`, `WHEN score >= 70`, `WHEN score >= 90`. What is wrong with this order? What would a score of 95 return?

---

## Exercises

### Exercise 1: Product Price Categories

Using the `products` table, write a query that categorizes each product as "Premium" (list_price >= 30), "Standard" (list_price >= 15), or "Budget" (less than 15). Show the product name, list price, and category. Sort by list price descending.

### Exercise 2: Employee Salary Report with COALESCE

Write a query that shows all employees with their names, departments, and salaries. Replace any NULL salary with 0 using COALESCE. Add a CASE column that shows "Above Average" if the salary is above 70,000, "Average" for 50,000 to 70,000, and "Below Average" or "No Salary" as appropriate.

### Exercise 3: Department Pivot Report

Write a single query that shows each department with separate columns counting the number of employees earning "High" (>= 90,000), "Medium" (60,000-89,999), and "Low" (< 60,000) salaries. Use CASE inside COUNT. Include a total column.

---

## What Is Next?

Now that you can add conditional logic to your queries with CASE expressions, the next chapter will introduce **Views**. Views let you save your complex queries (including those with CASE expressions) as reusable virtual tables. Instead of writing the same long query over and over, you can save it once as a view and then query it with a simple SELECT statement.
