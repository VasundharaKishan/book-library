# Chapter 12: Introduction to Joins — Combining Data from Multiple Tables

## What You Will Learn

In this chapter, you will learn how to:

- Understand why data is split across multiple tables
- Explain what a join does conceptually
- Set up two related tables connected by a foreign key
- Understand the different types of joins at a high level
- Visualize join types with Venn diagrams
- Write basic join syntax
- Avoid the Cartesian product trap

## Why This Chapter Matters

Imagine you are organizing a wedding. You have one list of guests and another list of table assignments. To create the seating chart, you need to combine these two lists — matching each guest with their table. That matching process is exactly what a join does in SQL.

Until now, all your queries have worked with a single table. But real databases almost never work that way. A well-designed database splits data into separate tables to avoid duplication. Customer information goes in a customers table. Orders go in an orders table. Products go in a products table. This design keeps data organized and consistent (we will explore why in the normalization chapter later).

The trade-off is that when you need to see a customer along with their orders, you need to combine the tables. Joins are how you do that. They are the bridge between separate tables, and they are arguably the single most important concept in relational databases.

If SELECT is the most-used SQL command, joins are the most-used technique within SELECT. Once you understand joins, you understand the heart of relational databases.

---

## Why Data Is Split Across Tables

Let us start with a bad design to understand why splitting data is necessary.

### The Bad Way — One Big Table

Imagine storing everything in one table:

```
+----+------------------+-------------+-----------+------------+--------------+------------------+
| id | employee_name    | department  | salary    | hire_date  | dept_budget  | dept_location    |
+----+------------------+-------------+-----------+------------+--------------+------------------+
|  1 | Alice Johnson    | Engineering | 85000.00  | 2020-03-15 | 500000.00    | Building A, Fl 3 |
|  2 | Bob Smith        | Marketing   | 62000.00  | 2019-07-22 | 200000.00    | Building B, Fl 1 |
|  3 | Carol Williams   | Engineering | 92000.00  | 2018-11-01 | 500000.00    | Building A, Fl 3 |
|  4 | David Brown      | Sales       | 58000.00  | 2021-01-10 | 300000.00    | Building A, Fl 1 |
|  5 | Eva Martinez     | Marketing   | 65000.00  | 2020-09-05 | 200000.00    | Building B, Fl 1 |
|  6 | Frank Lee        | Engineering | 78000.00  | 2022-02-14 | 500000.00    | Building A, Fl 3 |
+----+------------------+-------------+-----------+------------+--------------+------------------+
```

See the problem? "500000.00" and "Building A, Fl 3" are repeated for every Engineering employee. This causes three issues:

1. **Wasted storage** — The same information is stored over and over.
2. **Update anomalies** — If Engineering moves to a new building, you need to update every Engineering row. Miss one, and your data is inconsistent.
3. **Deletion anomalies** — If you delete the last Marketing employee, you lose the Marketing department's budget and location information too.

### The Good Way — Two Separate Tables

Split the data into two tables, each storing one type of thing:

**departments table** (information about departments):

```
+---------+-------------+-----------+------------------+
| dept_id | dept_name   | budget    | location         |
+---------+-------------+-----------+------------------+
|       1 | Engineering | 500000.00 | Building A, Fl 3 |
|       2 | Marketing   | 200000.00 | Building B, Fl 1 |
|       3 | Sales       | 300000.00 | Building A, Fl 1 |
|       4 | HR          | 150000.00 | Building B, Fl 2 |
+---------+-------------+-----------+------------------+
```

**employees table** (information about employees):

```
+----+------------------+---------+-----------+------------+
| id | name             | dept_id | salary    | hire_date  |
+----+------------------+---------+-----------+------------+
|  1 | Alice Johnson    |       1 | 85000.00  | 2020-03-15 |
|  2 | Bob Smith        |       2 | 62000.00  | 2019-07-22 |
|  3 | Carol Williams   |       1 | 92000.00  | 2018-11-01 |
|  4 | David Brown      |       3 | 58000.00  | 2021-01-10 |
|  5 | Eva Martinez     |       2 | 65000.00  | 2020-09-05 |
|  6 | Frank Lee        |       1 | 78000.00  | 2022-02-14 |
+----+------------------+---------+-----------+------------+
```

Now "Building A, Fl 3" is stored only once. If Engineering moves, you update one row in the departments table and every employee query automatically reflects the change.

The `dept_id` column in the employees table is what connects the two tables. It is a **foreign key** — a pointer that says "this employee belongs to that department."

---

## Setting Up Our Practice Tables

Let us create these two tables so we can practice joining them:

```sql
-- Drop the old employees table and start fresh
DROP TABLE IF EXISTS employees;

-- Create departments table
CREATE TABLE departments (
    dept_id   SERIAL PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL,
    budget    NUMERIC(12,2),
    location  VARCHAR(100)
);

-- Create employees table with a foreign key to departments
CREATE TABLE employees (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    dept_id    INTEGER REFERENCES departments(dept_id),
    salary     NUMERIC(10,2) NOT NULL,
    hire_date  DATE NOT NULL
);
```

Now insert the data:

```sql
INSERT INTO departments (dept_name, budget, location) VALUES
    ('Engineering', 500000.00, 'Building A, Floor 3'),
    ('Marketing',   200000.00, 'Building B, Floor 1'),
    ('Sales',       300000.00, 'Building A, Floor 1'),
    ('HR',          150000.00, 'Building B, Floor 2'),
    ('Research',    400000.00, 'Building C, Floor 1');

INSERT INTO employees (name, dept_id, salary, hire_date) VALUES
    ('Alice Johnson',   1, 85000.00, '2020-03-15'),
    ('Bob Smith',       2, 62000.00, '2019-07-22'),
    ('Carol Williams',  1, 92000.00, '2018-11-01'),
    ('David Brown',     3, 58000.00, '2021-01-10'),
    ('Eva Martinez',    2, 65000.00, '2020-09-05'),
    ('Frank Lee',       1, 78000.00, '2022-02-14'),
    ('Grace Kim',       3, 61000.00, '2019-04-30'),
    ('Henry Wilson',    4, 55000.00, '2021-06-18'),
    ('Ivy Chen',        4, 59000.00, '2020-12-01'),
    ('Jack Davis',      3, 63000.00, '2023-03-20'),
    ('Karen Lopez',  NULL, 52000.00, '2024-01-08');
```

Notice two important things:

1. The **Research** department (dept_id = 5) has no employees assigned to it yet.
2. **Karen Lopez** has `dept_id = NULL` — she has been hired but not yet assigned to a department.

These edge cases will help us understand the difference between join types.

---

## The Foreign Key Connection

The connection between our two tables works through matching values:

```
  departments table                 employees table
  +-------+-------------+          +----+----------------+-------+
  |dept_id| dept_name   |          | id | name           |dept_id|
  +-------+-------------+          +----+----------------+-------+
  |   1   | Engineering |<----+----|  1 | Alice Johnson  |   1   |
  |       |             |     +----|  3 | Carol Williams |   1   |
  |       |             |     +----|  6 | Frank Lee      |   1   |
  +-------+-------------+          +----+----------------+-------+
  |   2   | Marketing   |<----+----|  2 | Bob Smith      |   2   |
  |       |             |     +----|  5 | Eva Martinez   |   2   |
  +-------+-------------+          +----+----------------+-------+
  |   3   | Sales       |<----+----|  4 | David Brown    |   3   |
  |       |             |     +----|  7 | Grace Kim      |   3   |
  |       |             |     +----|  10| Jack Davis     |   3   |
  +-------+-------------+          +----+----------------+-------+
  |   4   | HR          |<----+----|  8 | Henry Wilson   |   4   |
  |       |             |     +----|  9 | Ivy Chen       |   4   |
  +-------+-------------+          +----+----------------+-------+
  |   5   | Research    |<--- (no employees)
  +-------+-------------+          +----+----------------+-------+
                                   | 11 | Karen Lopez    | NULL  |
                                   +----+----------------+-------+
                                         (no department)
```

- `dept_id` in the departments table is the **primary key** — a unique identifier for each department.
- `dept_id` in the employees table is the **foreign key** — it references the primary key in departments.
- The arrows show which employees belong to which department.

---

## What a Join Does

A join combines rows from two tables based on a related column. You specify the condition that connects them (usually a matching key), and PostgreSQL pairs up the matching rows.

```
   departments              employees
   +-------+--------+       +----+--------+-------+
   |dept_id|dept_name|       | id | name   |dept_id|
   +-------+--------+       +----+--------+-------+
   |   1   | Eng    |       |  1 | Alice  |   1   |
   |   2   | Mkt    |       |  2 | Bob    |   2   |
   +-------+--------+       +----+--------+-------+

                   JOIN ON
            departments.dept_id = employees.dept_id

                      |
                      v

   +-------+--------+----+--------+-------+
   |dept_id|dept_name| id | name   |dept_id|
   +-------+--------+----+--------+-------+
   |   1   | Eng    |  1 | Alice  |   1   |  <-- dept_id 1 matches
   |   2   | Mkt    |  2 | Bob    |   2   |  <-- dept_id 2 matches
   +-------+--------+----+--------+-------+
```

The join condition `departments.dept_id = employees.dept_id` tells PostgreSQL: "For each employee, find the department where the dept_id values match, and combine those rows."

Think of it like a matchmaking service. Two lists of people. The join condition is what they have in common (like matching interest in hiking). The result is pairs of people who share that connection.

---

## Types of Joins — The Big Picture

There are several types of joins, each handling unmatched rows differently. Here is an overview using Venn diagrams:

### INNER JOIN — Only Matches

```
         +-------------+-------------+
        /               \             \
       /    Departments   \  Employees  \
      /      only          \   only      \
     |                      |             |
     |         +-----------+|             |
     |         |  MATCHING ||             |
     |         |   ROWS   ||             |
     |         +-----------+|             |
     |                      |             |
      \                    /             /
       \                  /             /
        \                /             /
         +-------------+-------------+
                       ^
                       |
              INNER JOIN returns
              only the overlap
```

INNER JOIN returns only rows that have a match in BOTH tables. Departments with no employees and employees with no department are excluded.

### LEFT JOIN — All Left + Matches

```
         +-------------+-------------+
        /               \             \
       / +-------------+ \             \
      /  | ALL LEFT    |  \             \
     |   | TABLE ROWS  |   |             |
     |   |  +---------+|   |             |
     |   |  |MATCHING ||   |             |
     |   |  | ROWS    ||   |             |
     |   |  +---------+|   |             |
     |   +-------------+   |             |
      \                    /             /
       \                  /             /
        +-------------+-------------+
                ^
                |
       LEFT JOIN returns
       everything shaded
```

LEFT JOIN returns ALL rows from the left table. If a left-table row has no match in the right table, the right-table columns are filled with NULL.

### RIGHT JOIN — Matches + All Right

```
         +-------------+-------------+
        /               \             \
       /                 \  +--------+ \
      /                   \ | ALL    |  \
     |                     || RIGHT  |   |
     |         +-----------+| TABLE  |   |
     |         |  MATCHING || ROWS   |   |
     |         |   ROWS   ||        |   |
     |         +-----------+|        |   |
     |                     |+--------+   |
      \                    /             /
       \                  /             /
        +-------------+-------------+
                            ^
                            |
                   RIGHT JOIN returns
                   everything shaded
```

RIGHT JOIN is the mirror of LEFT JOIN. It returns ALL rows from the right table.

### FULL OUTER JOIN — Everything

```
         +-------------+-------------+
        / +---------------------------+\
       /  | ALL ROWS FROM BOTH TABLES | \
      /   |                           |  \
     |    |         +-----------+     |   |
     |    |         |  MATCHING |     |   |
     |    |         |   ROWS    |     |   |
     |    |         +-----------+     |   |
     |    |                           |   |
      \   +---------------------------+  /
       \                              /
        +-------------+-------------+
                      ^
                      |
             FULL OUTER JOIN returns
               everything
```

FULL OUTER JOIN returns ALL rows from BOTH tables. Unmatched rows on either side get NULLs.

### Quick Comparison Table

```
+-----------------+---------------------------------------------------+
| Join Type       | Returns                                           |
+-----------------+---------------------------------------------------+
| INNER JOIN      | Only rows with matches in both tables             |
| LEFT JOIN       | All rows from left table + matches from right     |
| RIGHT JOIN      | All rows from right table + matches from left     |
| FULL OUTER JOIN | All rows from both tables                         |
| CROSS JOIN      | Every possible combination (Cartesian product)    |
+-----------------+---------------------------------------------------+
```

We will dive deeply into each join type in the next two chapters. For now, let us learn the basic syntax using INNER JOIN.

---

## Basic Join Syntax

Here is how to write a simple INNER JOIN:

```sql
SELECT
    employees.name,
    departments.dept_name,
    employees.salary
FROM employees
INNER JOIN departments
    ON employees.dept_id = departments.dept_id;
```

**Line-by-line breakdown:**

- `SELECT employees.name, departments.dept_name, employees.salary` — We prefix columns with table names to be clear about which table each column comes from.
- `FROM employees` — Start with the employees table.
- `INNER JOIN departments` — Combine it with the departments table.
- `ON employees.dept_id = departments.dept_id` — The join condition: match rows where the dept_id values are equal.

**Result:**

```
+------------------+-------------+-----------+
| name             | dept_name   | salary    |
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
(10 rows)
```

Notice: **Karen Lopez is missing** (she has no department — NULL dept_id) and the **Research department is missing** (it has no employees). INNER JOIN only returns matches.

### Using Table Aliases for Shorter Queries

Typing `employees.name` and `departments.dept_name` gets tedious. Table aliases make it shorter:

```sql
SELECT
    e.name,
    d.dept_name,
    e.salary
FROM employees AS e
INNER JOIN departments AS d
    ON e.dept_id = d.dept_id;
```

`e` is short for `employees`, `d` is short for `departments`. The result is identical — aliases are just nicknames.

You can even drop the `AS` keyword:

```sql
SELECT e.name, d.dept_name, e.salary
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;
```

### Using Joins with WHERE, ORDER BY, and GROUP BY

Joins work seamlessly with everything you have learned so far:

```sql
-- Employees in Engineering, sorted by salary
SELECT e.name, d.dept_name, e.salary
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id
WHERE d.dept_name = 'Engineering'
ORDER BY e.salary DESC;
```

**Result:**

```
+------------------+-------------+-----------+
| name             | dept_name   | salary    |
+------------------+-------------+-----------+
| Carol Williams   | Engineering | 92000.00  |
| Alice Johnson    | Engineering | 85000.00  |
| Frank Lee        | Engineering | 78000.00  |
+------------------+-------------+-----------+
(3 rows)
```

```sql
-- Employee count and average salary per department
SELECT
    d.dept_name,
    COUNT(*)              AS headcount,
    ROUND(AVG(e.salary), 2) AS avg_salary
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id
GROUP BY d.dept_name
ORDER BY avg_salary DESC;
```

**Result:**

```
+-------------+-----------+------------+
| dept_name   | headcount | avg_salary |
+-------------+-----------+------------+
| Engineering |         3 |   85000.00 |
| Marketing   |         2 |   63500.00 |
| Sales       |         3 |   60666.67 |
| HR          |         2 |   57000.00 |
+-------------+-----------+------------+
(4 rows)
```

---

## The Cartesian Product Warning

What happens if you forget the join condition? You get a **Cartesian product** (also called a CROSS JOIN) — every row from one table is combined with every row from the other table.

```sql
-- DANGER: No join condition!
SELECT e.name, d.dept_name
FROM employees e, departments d;
```

If employees has 11 rows and departments has 5 rows, you get 11 x 5 = **55 rows**. Each employee is paired with EVERY department, which is almost never what you want.

```
  Without join condition (Cartesian product):

  Alice   + Engineering  ]
  Alice   + Marketing    ]-- Alice paired with ALL 5 depts
  Alice   + Sales        ]
  Alice   + HR           ]
  Alice   + Research     ]
  Bob     + Engineering  ]
  Bob     + Marketing    ]-- Bob paired with ALL 5 depts
  Bob     + Sales        ]
  Bob     + HR           ]
  Bob     + Research     ]
  ...                       (55 total rows!)
```

This is one of the most common join mistakes. With small tables it produces confusing results. With large tables, it can crash your database or fill up memory. Imagine two tables with 10,000 rows each — a Cartesian product would produce 100,000,000 rows.

### How to Avoid It

Always use the explicit JOIN syntax with an ON condition:

```sql
-- Good: Explicit join with condition
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;

-- Bad: Implicit join (easy to forget the WHERE)
SELECT e.name, d.dept_name
FROM employees e, departments d
WHERE e.dept_id = d.dept_id;
```

Both produce the same result, but the explicit `JOIN ... ON` syntax makes it impossible to accidentally forget the join condition.

> **Note:** There are rare cases where a Cartesian product is intentional (such as generating all possible combinations). We will cover CROSS JOIN in a later chapter.

---

## How Joins Fit in the Query Flow

```
                +-------------------+    +-------------------+
                |   employees       |    |   departments     |
                +--------+----------+    +--------+----------+
                         |                        |
                Step 1: FROM + JOIN
                "Combine the tables using
                 the ON condition"
                         |
                         v
                +-------------------+
                |  Combined rows    |
                |  (matched pairs)  |
                +--------+----------+
                         |
                Step 2: WHERE
                "Filter individual rows"
                         |
                Step 3: GROUP BY
                "Form groups"
                         |
                Step 4: HAVING
                "Filter groups"
                         |
                Step 5: SELECT
                "Pick columns"
                         |
                Step 6: ORDER BY
                "Sort results"
                         |
                Step 7: LIMIT/OFFSET
                "Cut to size"
                         |
                         v
                +-------------------+
                |  Final results    |
                +-------------------+
```

The join happens first, before WHERE, GROUP BY, or anything else. PostgreSQL combines the tables into one big result set, then processes everything else on that combined data.

---

## A Preview of What Is Next

Here is a quick preview of how the different join types handle our test data:

```sql
-- INNER JOIN: Only matched rows (10 rows)
-- Missing: Karen (no dept), Research dept (no employees)
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;

-- LEFT JOIN: All employees + their dept (11 rows)
-- Karen shows up with NULL dept_name
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;

-- RIGHT JOIN: All departments + their employees (11 rows)
-- Research shows up with NULL employee name
SELECT e.name, d.dept_name
FROM employees e
RIGHT JOIN departments d ON e.dept_id = d.dept_id;

-- FULL OUTER JOIN: Everything (12 rows)
-- Both Karen and Research show up
SELECT e.name, d.dept_name
FROM employees e
FULL OUTER JOIN departments d ON e.dept_id = d.dept_id;
```

We will explore each of these in detail in the next two chapters.

---

## Common Mistakes

### Mistake 1: Forgetting the Join Condition

```sql
-- Wrong: Creates a Cartesian product (every combination)
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d;
-- ERROR (or unexpected results)

-- Right: Always specify ON
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;
```

### Mistake 2: Ambiguous Column Names

```sql
-- Wrong: Both tables have a column that could be "dept_id"
SELECT name, dept_id, dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;
-- ERROR: column reference "dept_id" is ambiguous

-- Right: Prefix with the table name or alias
SELECT e.name, e.dept_id, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;
```

When both tables have a column with the same name, you must specify which table you mean by using the table name or alias prefix.

### Mistake 3: Joining on the Wrong Column

```sql
-- Wrong: Joining employee id with department id (different things!)
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.id = d.dept_id;
-- Returns wrong results: employee 1 matched with dept 1, etc.

-- Right: Join on the foreign key relationship
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;
```

Always join on the column that represents the actual relationship (the foreign key to the primary key).

### Mistake 4: Using INNER JOIN When You Want All Rows

```sql
-- If you want ALL employees including those without a department:
-- Wrong: INNER JOIN excludes Karen (NULL dept_id)
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;
-- Karen is missing!

-- Right: Use LEFT JOIN
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;
-- Karen appears with NULL dept_name
```

---

## Best Practices

1. **Always use explicit JOIN syntax.** Write `INNER JOIN ... ON` instead of listing tables with commas. It is clearer and prevents accidental Cartesian products.

2. **Use table aliases.** They keep queries short and readable, especially when joining many tables.

3. **Prefix all column names with table aliases in join queries.** Even if a column name is unique, prefixing makes it clear which table it comes from.

4. **Choose the right join type.** Think about what should happen with unmatched rows before writing your query. Need all employees, even unassigned ones? Use LEFT JOIN.

5. **Start with INNER JOIN when in doubt.** It is the most common join and the safest default. Switch to LEFT/RIGHT/FULL only when you need unmatched rows.

6. **Verify your results.** After writing a join, check the row count. If you expect 10 rows but get 50, you might have a bad join condition causing duplicates.

---

## Quick Summary

```
+--------------------+----------------------------------------------------+
| Concept            | Description                                        |
+--------------------+----------------------------------------------------+
| Why split tables?  | Avoid duplication, prevent update anomalies        |
| Foreign key        | Column in one table that references another table  |
| INNER JOIN         | Returns only matching rows from both tables        |
| LEFT JOIN          | All left rows + matches from right (NULLs if none) |
| RIGHT JOIN         | All right rows + matches from left (NULLs if none) |
| FULL OUTER JOIN    | All rows from both tables                          |
| CROSS JOIN         | Every combination (Cartesian product)              |
| Join condition     | ON table1.col = table2.col                         |
| Table alias        | FROM employees AS e (or just FROM employees e)     |
+--------------------+----------------------------------------------------+
```

---

## Key Points

- Real databases split data across multiple tables to avoid duplication and inconsistency.
- A foreign key in one table references the primary key of another table, creating a relationship.
- A join combines rows from two tables based on a matching condition (the ON clause).
- INNER JOIN returns only rows that have matches in both tables.
- LEFT JOIN returns all rows from the left table, filling in NULLs for unmatched right-side columns.
- Always use explicit `JOIN ... ON` syntax to prevent accidental Cartesian products.
- Table aliases (e for employees, d for departments) keep join queries readable.
- Prefix column names with table aliases to avoid ambiguity.
- The join is processed before WHERE, GROUP BY, HAVING, and ORDER BY.

---

## Practice Questions

1. In our setup, why does Karen Lopez not appear in an INNER JOIN result between employees and departments?

2. What is a Cartesian product, and how do you accidentally create one?

3. Write a query that shows each employee's name, their department name, and their department's location. Use INNER JOIN.

4. How many rows would a Cartesian product produce between a table with 100 rows and a table with 50 rows?

5. Which join type would you use if you want to see ALL departments, including those with no employees?

---

## Exercises

### Exercise 1: Employee Directory

Write a query that produces a complete employee directory showing:
- Employee name
- Department name
- Salary
- Department location

Sort by department name, then by employee name within each department.

### Exercise 2: Department Report with Joins

Write a query that shows each department's name, location, number of employees, and total salary. Sort by total salary descending. (Hint: use INNER JOIN with GROUP BY.)

### Exercise 3: Exploring Join Behavior

Run each of these queries and compare the results:
1. INNER JOIN between employees and departments
2. Count the rows in the INNER JOIN result
3. How many employees are in the employees table total?
4. Why are the counts different? Which employees or departments are missing from the INNER JOIN result?

---

## What Is Next?

Now that you understand what joins are and why they matter, the next chapter dives deep into **INNER JOIN** — the most common join type. You will practice writing INNER JOIN queries with multiple conditions, joining more than two tables, and solving real-world problems that require combining data from different sources.
