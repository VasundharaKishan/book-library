# Chapter 7: SELECT Queries — Retrieving Data from Your Database

## What You Will Learn

In this chapter, you will learn how to:

- Retrieve data from a table using the SELECT statement
- Choose between selecting all columns and selecting specific columns
- Create column aliases with the AS keyword
- Perform arithmetic calculations directly in your queries
- Combine text columns using concatenation
- Remove duplicate rows with DISTINCT
- Write expressions in your SELECT list

## Why This Chapter Matters

Imagine you have a filing cabinet full of employee records. Every time your boss asks a question — "Who works in Marketing?" or "What is the total salary budget?" — you need to pull out the right folders and find the right information.

The SELECT statement is your way of asking questions to the database. It is the single most important SQL command you will ever learn. Almost every interaction with a database starts with SELECT. Whether you are building a website, generating a report, or analyzing data, SELECT is the tool you reach for first.

Learning to write good SELECT queries is like learning to ask good questions. The more precise your question, the more useful the answer.

---

## Setting Up Our Practice Table

Before we start writing queries, let us create a table we will use throughout this chapter and the next several chapters. Think of this as setting up a spreadsheet with employee information.

```sql
CREATE TABLE employees (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    department  VARCHAR(50)  NOT NULL,
    salary      NUMERIC(10,2) NOT NULL,
    hire_date   DATE         NOT NULL
);
```

Now let us fill it with some sample data:

```sql
INSERT INTO employees (name, department, salary, hire_date) VALUES
    ('Alice Johnson',   'Engineering',  85000.00, '2020-03-15'),
    ('Bob Smith',       'Marketing',    62000.00, '2019-07-22'),
    ('Carol Williams',  'Engineering',  92000.00, '2018-11-01'),
    ('David Brown',     'Sales',        58000.00, '2021-01-10'),
    ('Eva Martinez',    'Marketing',    65000.00, '2020-09-05'),
    ('Frank Lee',       'Engineering',  78000.00, '2022-02-14'),
    ('Grace Kim',       'Sales',        61000.00, '2019-04-30'),
    ('Henry Wilson',    'HR',           55000.00, '2021-06-18'),
    ('Ivy Chen',        'HR',           59000.00, '2020-12-01'),
    ('Jack Davis',      'Sales',        63000.00, '2023-03-20');
```

Our table now looks like this:

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

## SELECT * — Getting Everything

The simplest way to retrieve data is to ask for everything:

```sql
SELECT * FROM employees;
```

**Line-by-line breakdown:**

- `SELECT` — This keyword tells PostgreSQL you want to retrieve data.
- `*` — The asterisk means "all columns." It is a wildcard, like saying "give me everything."
- `FROM employees` — This tells PostgreSQL which table to look in.

**Result:**

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
(10 rows)
```

Think of `SELECT *` like telling a librarian, "Show me every book on that shelf." You get everything, whether you need it or not.

### When SELECT * Is Okay

- **Exploring a new table** — You just found a table and want to see what is in it.
- **Small tables** — The table has only a few columns and rows.
- **Quick debugging** — You are troubleshooting a problem and need to see all the data.

### When SELECT * Is a Bad Idea

- **Large tables** — If a table has 50 columns and millions of rows, `SELECT *` wastes time and memory.
- **Production applications** — Your web app only needs the employee name and department, but `SELECT *` fetches salary, hire date, and everything else too.
- **When the table might change** — If someone adds a new column later, your `SELECT *` query suddenly returns extra data your application was not expecting.

---

## Selecting Specific Columns

Instead of grabbing everything, you can ask for exactly what you need:

```sql
SELECT name, department FROM employees;
```

**Line-by-line breakdown:**

- `SELECT name, department` — We list the exact columns we want, separated by commas.
- `FROM employees` — The table to look in.

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

This is like telling the librarian, "I only need the title and author of each book." You get exactly what you asked for, nothing more.

You can list columns in any order:

```sql
SELECT department, name, salary FROM employees;
```

**Result:**

```
+-------------+------------------+-----------+
| department  | name             | salary    |
+-------------+------------------+-----------+
| Engineering | Alice Johnson    | 85000.00  |
| Marketing   | Bob Smith        | 62000.00  |
| Engineering | Carol Williams   | 92000.00  |
| Sales       | David Brown      | 58000.00  |
| Marketing   | Eva Martinez     | 65000.00  |
| Engineering | Frank Lee        | 78000.00  |
| Sales       | Grace Kim        | 61000.00  |
| HR          | Henry Wilson     | 55000.00  |
| HR          | Ivy Chen         | 59000.00  |
| Sales       | Jack Davis       | 63000.00  |
+-------------+------------------+-----------+
(10 rows)
```

Notice that the columns appear in the order you listed them, not the order they were created in the table.

---

## Column Aliases with AS

Sometimes column names in the database are not very readable. Maybe a column is called `dept` or `emp_nm` or something technical. Aliases let you rename columns in the output without changing anything in the database.

```sql
SELECT
    name        AS employee_name,
    department  AS dept,
    salary      AS annual_salary
FROM employees;
```

**Line-by-line breakdown:**

- `name AS employee_name` — Show the `name` column, but label it as `employee_name` in the results.
- `department AS dept` — Show `department` but call it `dept` in the output.
- `salary AS annual_salary` — Show `salary` labeled as `annual_salary`.

**Result:**

```
+------------------+-------------+---------------+
| employee_name    | dept        | annual_salary |
+------------------+-------------+---------------+
| Alice Johnson    | Engineering | 85000.00      |
| Bob Smith        | Marketing   | 62000.00      |
| Carol Williams   | Engineering | 92000.00      |
| David Brown      | Sales       | 58000.00      |
| Eva Martinez     | Marketing   | 65000.00      |
| Frank Lee        | Engineering | 78000.00      |
| Grace Kim        | Sales       | 61000.00      |
| Henry Wilson     | HR          | 55000.00      |
| Ivy Chen         | HR          | 59000.00      |
| Jack Davis       | Sales       | 63000.00      |
+------------------+-------------+---------------+
(10 rows)
```

Think of aliases like name tags at a conference. Your real name might be "Robert," but your name tag says "Bob." The alias does not change who you are — it just changes how you are introduced.

### Aliases with Spaces

If you want an alias with spaces in it, use double quotes:

```sql
SELECT
    name        AS "Employee Name",
    salary      AS "Annual Salary"
FROM employees;
```

**Result:**

```
+------------------+---------------+
| Employee Name    | Annual Salary |
+------------------+---------------+
| Alice Johnson    | 85000.00      |
| Bob Smith        | 62000.00      |
| Carol Williams   | 92000.00      |
| ...              | ...           |
+------------------+---------------+
```

> **Note:** The `AS` keyword is actually optional in PostgreSQL. You can write `SELECT name employee_name` instead of `SELECT name AS employee_name`. However, using `AS` makes your code much easier to read, so always include it.

---

## Column Arithmetic — Calculating in Your Queries

SQL can do math right inside your queries. You do not need to pull data into a spreadsheet to calculate things.

### Basic Arithmetic Operators

```
+----------+----------------+
| Operator | Meaning        |
+----------+----------------+
| +        | Addition       |
| -        | Subtraction    |
| *        | Multiplication |
| /        | Division       |
| %        | Modulo         |
+----------+----------------+
```

### Monthly Salary

```sql
SELECT
    name,
    salary                  AS annual_salary,
    salary / 12             AS monthly_salary
FROM employees;
```

**Line-by-line breakdown:**

- `salary / 12` — PostgreSQL divides each employee's salary by 12 and shows the result.
- `AS monthly_salary` — We give the calculated column a meaningful name.

**Result:**

```
+------------------+---------------+------------------+
| name             | annual_salary | monthly_salary   |
+------------------+---------------+------------------+
| Alice Johnson    | 85000.00      | 7083.333333      |
| Bob Smith        | 62000.00      | 5166.666667      |
| Carol Williams   | 92000.00      | 7666.666667      |
| David Brown      | 58000.00      | 4833.333333      |
| Eva Martinez     | 65000.00      | 5416.666667      |
| Frank Lee        | 78000.00      | 6500.000000      |
| Grace Kim        | 61000.00      | 5083.333333      |
| Henry Wilson     | 55000.00      | 4583.333333      |
| Ivy Chen         | 59000.00      | 4916.666667      |
| Jack Davis       | 63000.00      | 5250.000000      |
+------------------+---------------+------------------+
(10 rows)
```

### Salary After a 10% Raise

```sql
SELECT
    name,
    salary              AS current_salary,
    salary * 1.10       AS salary_after_raise,
    salary * 0.10       AS raise_amount
FROM employees;
```

**Result:**

```
+------------------+----------------+---------------------+--------------+
| name             | current_salary | salary_after_raise  | raise_amount |
+------------------+----------------+---------------------+--------------+
| Alice Johnson    | 85000.00       | 93500.0000          | 8500.0000    |
| Bob Smith        | 62000.00       | 68200.0000          | 6200.0000    |
| Carol Williams   | 92000.00       | 101200.0000         | 9200.0000    |
| David Brown      | 58000.00       | 63800.0000          | 5800.0000    |
| Eva Martinez     | 65000.00       | 71500.0000          | 6500.0000    |
| Frank Lee        | 78000.00       | 85800.0000          | 7800.0000    |
| Grace Kim        | 61000.00       | 67100.0000          | 6100.0000    |
| Henry Wilson     | 55000.00       | 60500.0000          | 5500.0000    |
| Ivy Chen         | 59000.00       | 64900.0000          | 5900.0000    |
| Jack Davis       | 63000.00       | 69300.0000          | 6300.0000    |
+------------------+----------------+---------------------+--------------+
(10 rows)
```

> **Important:** These calculations do NOT change the data in your table. They only affect what you see in the results. The actual salary values remain the same. Think of it like looking at a price tag through a magnifying glass — the price does not actually change.

### Rounding Results

Those long decimal numbers are not pretty. Use the ROUND function to clean them up:

```sql
SELECT
    name,
    salary                          AS annual_salary,
    ROUND(salary / 12, 2)           AS monthly_salary
FROM employees;
```

**Result:**

```
+------------------+---------------+----------------+
| name             | annual_salary | monthly_salary |
+------------------+---------------+----------------+
| Alice Johnson    | 85000.00      | 7083.33        |
| Bob Smith        | 62000.00      | 5166.67        |
| Carol Williams   | 92000.00      | 7666.67        |
| David Brown      | 58000.00      | 4833.33        |
| Eva Martinez     | 65000.00      | 5416.67        |
| Frank Lee        | 78000.00      | 6500.00        |
| Grace Kim        | 61000.00      | 5083.33        |
| Henry Wilson     | 55000.00      | 4583.33        |
| Ivy Chen         | 59000.00      | 4916.67        |
| Jack Davis       | 63000.00      | 5250.00        |
+------------------+---------------+----------------+
(10 rows)
```

The `ROUND(value, 2)` function rounds the number to 2 decimal places.

---

## String Concatenation with ||

In PostgreSQL, the `||` operator joins (concatenates) text strings together. Think of it like gluing words together.

```sql
SELECT
    name || ' works in ' || department AS employee_info
FROM employees;
```

**Line-by-line breakdown:**

- `name` — The employee's name (text).
- `||` — The concatenation operator. It glues the next piece of text onto the previous one.
- `' works in '` — A literal string (notice the spaces inside the quotes).
- `||` — Glue again.
- `department` — The department name.
- `AS employee_info` — Give the resulting column a name.

**Result:**

```
+------------------------------------------+
| employee_info                            |
+------------------------------------------+
| Alice Johnson works in Engineering       |
| Bob Smith works in Marketing             |
| Carol Williams works in Engineering      |
| David Brown works in Sales               |
| Eva Martinez works in Marketing          |
| Frank Lee works in Engineering           |
| Grace Kim works in Sales                 |
| Henry Wilson works in HR                 |
| Ivy Chen works in HR                     |
| Jack Davis works in Sales                |
+------------------------------------------+
(10 rows)
```

### Building Formatted Output

You can build complex strings:

```sql
SELECT
    'Employee #' || id || ': ' || name AS employee_label
FROM employees;
```

**Result:**

```
+----------------------------------+
| employee_label                   |
+----------------------------------+
| Employee #1: Alice Johnson       |
| Employee #2: Bob Smith           |
| Employee #3: Carol Williams      |
| Employee #4: David Brown         |
| Employee #5: Eva Martinez        |
| Employee #6: Frank Lee           |
| Employee #7: Grace Kim           |
| Employee #8: Henry Wilson        |
| Employee #9: Ivy Chen            |
| Employee #10: Jack Davis         |
+----------------------------------+
(10 rows)
```

Notice that PostgreSQL automatically converts the `id` (a number) to text when you concatenate it with strings.

---

## DISTINCT — Removing Duplicates

Sometimes you want to know what unique values exist in a column. DISTINCT removes duplicate rows from your results.

### Without DISTINCT

```sql
SELECT department FROM employees;
```

**Result:**

```
+-------------+
| department  |
+-------------+
| Engineering |
| Marketing   |
| Engineering |
| Sales       |
| Marketing   |
| Engineering |
| Sales       |
| HR          |
| HR          |
| Sales       |
+-------------+
(10 rows)
```

You see "Engineering" three times, "Sales" three times, and so on.

### With DISTINCT

```sql
SELECT DISTINCT department FROM employees;
```

**Result:**

```
+-------------+
| department  |
+-------------+
| Engineering |
| HR          |
| Marketing   |
| Sales       |
+-------------+
(4 rows)
```

Now each department appears only once. Think of DISTINCT like removing duplicate cards from a deck — if you have three Kings of Hearts, DISTINCT keeps just one.

### DISTINCT with Multiple Columns

When you use DISTINCT with multiple columns, it removes rows where the combination of all listed columns is the same:

```sql
SELECT DISTINCT department, salary FROM employees;
```

**Result:**

```
+-------------+-----------+
| department  | salary    |
+-------------+-----------+
| Engineering | 78000.00  |
| Engineering | 85000.00  |
| Engineering | 92000.00  |
| HR          | 55000.00  |
| HR          | 59000.00  |
| Marketing   | 62000.00  |
| Marketing   | 65000.00  |
| Sales       | 58000.00  |
| Sales       | 61000.00  |
| Sales       | 63000.00  |
+-------------+-----------+
(10 rows)
```

All 10 rows appear because every combination of department and salary is unique in our data.

---

## Expressions in SELECT

You can use SELECT without a FROM clause to evaluate expressions, almost like a calculator:

```sql
SELECT 2 + 3 AS result;
```

**Result:**

```
+--------+
| result |
+--------+
|      5 |
+--------+
```

```sql
SELECT
    100 * 0.15      AS fifteen_percent,
    'Hello' || ' ' || 'World' AS greeting,
    CURRENT_DATE    AS today;
```

**Result:**

```
+-----------------+-------------+------------+
| fifteen_percent | greeting    | today      |
+-----------------+-------------+------------+
|           15.00 | Hello World | 2024-01-15 |
+-----------------+-------------+------------+
```

This is handy for quick calculations or testing expressions before using them in bigger queries.

---

## How SELECT Works — A Mental Model

Here is how to think about what happens when you run a SELECT query:

```
                    +-------------------+
                    |   employees       |
                    |   (full table)    |
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
                    Step 2: SELECT
                    "Pick the columns
                     you want to see"
                             |
                             v
                    +-------------------+
                    |  Only the columns |
                    |  you asked for    |
                    +-------------------+
```

Even though you write SELECT first, PostgreSQL actually processes FROM first (to know where to look), then applies SELECT (to know what to show). We will add more steps to this mental model in later chapters.

---

## Common Mistakes

### Mistake 1: Forgetting the FROM Clause

```sql
-- Wrong: PostgreSQL does not know which table to look in
SELECT name, salary;

-- ERROR: column "name" does not exist

-- Right: Always specify the table
SELECT name, salary FROM employees;
```

### Mistake 2: Misspelling Column Names

```sql
-- Wrong: The column is called "name", not "nme"
SELECT nme, department FROM employees;

-- ERROR: column "nme" does not exist

-- Right: Check your spelling
SELECT name, department FROM employees;
```

### Mistake 3: Using Commas Incorrectly

```sql
-- Wrong: Extra comma after the last column
SELECT name, department, FROM employees;

-- ERROR: syntax error at or near "FROM"

-- Right: No trailing comma
SELECT name, department FROM employees;
```

### Mistake 4: Confusing || with +

```sql
-- Wrong in PostgreSQL: + is for math, not string joining
SELECT name + department FROM employees;

-- ERROR: operator is not unique

-- Right: Use || for concatenation
SELECT name || ' - ' || department FROM employees;
```

---

## Best Practices

1. **Select only the columns you need.** Avoid `SELECT *` in production code. It wastes resources and can break your application when table structures change.

2. **Always use aliases for calculated columns.** Without an alias, PostgreSQL generates an ugly name like `?column?` for expressions.

3. **Use meaningful alias names.** `AS x` tells you nothing. `AS monthly_salary` is clear and self-documenting.

4. **Format your SQL for readability.** Put each column on its own line for complex queries:

   ```sql
   SELECT
       name,
       department,
       salary,
       ROUND(salary / 12, 2) AS monthly_salary
   FROM employees;
   ```

5. **Use DISTINCT sparingly.** If you find yourself using DISTINCT to fix duplicate results, the real problem might be in your query logic (especially once you learn JOINs).

---

## Quick Summary

```
+-------------------+------------------------------------------+
| Concept           | Example                                  |
+-------------------+------------------------------------------+
| All columns       | SELECT * FROM employees;                 |
| Specific columns  | SELECT name, salary FROM employees;      |
| Alias             | SELECT name AS employee_name ...          |
| Arithmetic        | SELECT salary * 1.10 AS new_salary ...   |
| Concatenation     | SELECT name || ' - ' || department ...   |
| Remove duplicates | SELECT DISTINCT department ...            |
| Expression only   | SELECT 2 + 3 AS result;                  |
+-------------------+------------------------------------------+
```

---

## Key Points

- `SELECT *` retrieves all columns. Use it for exploration, not production code.
- List specific column names to get only the data you need.
- The `AS` keyword creates aliases that rename columns in the output without changing the table.
- You can perform arithmetic (`+`, `-`, `*`, `/`) directly in SELECT.
- The `||` operator concatenates (joins) strings together in PostgreSQL.
- `DISTINCT` removes duplicate rows from results.
- Calculations in SELECT do not modify the actual data in the table.
- Always give calculated columns a meaningful alias.

---

## Practice Questions

1. Write a query that selects only the `name` and `hire_date` columns from the employees table.

2. What is wrong with this query?
   ```sql
   SELECT name salary FROM employees;
   ```

3. Write a query that shows each employee's name and their daily salary (assume 260 working days per year). Round the result to 2 decimal places and give it an appropriate alias.

4. Write a query that shows the unique departments in the employees table. How many rows does the result have?

5. What will this query produce?
   ```sql
   SELECT DISTINCT department, name FROM employees;
   ```
   Will it return fewer rows than `SELECT department, name FROM employees`? Why or why not?

---

## Exercises

### Exercise 1: Employee Directory

Write a query that produces output like this:

```
+--------------------------------------------+-------------+
| employee_listing                           | department  |
+--------------------------------------------+-------------+
| #1 - Alice Johnson                         | Engineering |
| #2 - Bob Smith                             | Marketing   |
| ...                                        | ...         |
+--------------------------------------------+-------------+
```

Use concatenation to build the `employee_listing` column.

### Exercise 2: Compensation Report

Write a query that shows each employee's:
- Name
- Annual salary
- Monthly salary (rounded to 2 decimal places)
- Weekly salary (assume 52 weeks, rounded to 2 decimal places)
- Salary after a 15% raise (rounded to 2 decimal places)

Give all columns clear, readable aliases.

### Exercise 3: Data Exploration

Imagine you just discovered the employees table and need to answer these questions:
1. How many rows does the table have? (Hint: `SELECT * FROM employees` and count, or peek ahead to Chapter 10 for a better way.)
2. What departments exist?
3. What is the salary range? (Find the lowest and highest by scanning the output.)

Write the queries you would use to explore this table.

---

## What Is Next?

Now that you know how to retrieve and format data, the next chapter will teach you how to **filter** that data. Instead of getting all 10 employees every time, you will learn to ask questions like "Show me only the engineers" or "Who earns more than 70,000?" The WHERE clause is what turns SQL from a simple data viewer into a powerful query language.
