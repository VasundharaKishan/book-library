# Chapter 26: Window Functions — Calculations Across Rows

## What You Will Learn

In this chapter, you will learn:

- What window functions are and how they differ from GROUP BY
- How to use the OVER clause to define a window
- How to partition data with PARTITION BY
- How to rank rows with ROW_NUMBER, RANK, and DENSE_RANK
- How to access previous and next rows with LAG and LEAD
- How to calculate running totals with SUM OVER
- How to use NTILE to divide rows into buckets
- How to control the window frame with ROWS BETWEEN

## Why This Chapter Matters

Imagine you have a spreadsheet of monthly sales. You want to add a column showing each month's rank, another column showing the running total, and another showing the difference from the previous month. In a spreadsheet, you would just add formulas in new columns — the original rows stay intact.

That is exactly what window functions do in SQL. They let you calculate across rows without collapsing them into groups. With GROUP BY, you lose the individual rows. With window functions, you keep every row and add the calculation alongside it.

Window functions are essential for reporting, analytics, and any time you need to compare rows to each other — rankings, running totals, moving averages, row-by-row comparisons, and more.

---

## Setting Up Our Practice Tables

```sql
CREATE TABLE employees (
    employee_id  SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    department   VARCHAR(50) NOT NULL,
    salary       DECIMAL(10, 2) NOT NULL,
    hire_date    DATE NOT NULL
);

INSERT INTO employees (name, department, salary, hire_date) VALUES
('Alice',   'Engineering', 95000, '2020-03-15'),
('Bob',     'Engineering', 90000, '2019-07-01'),
('Charlie', 'Engineering', 90000, '2021-01-10'),
('Diana',   'Sales',       75000, '2020-06-20'),
('Eve',     'Sales',       80000, '2018-11-05'),
('Frank',   'Sales',       72000, '2022-02-14'),
('Grace',   'Marketing',   70000, '2021-05-01'),
('Hank',    'Marketing',   68000, '2020-09-15');

CREATE TABLE monthly_sales (
    sale_id    SERIAL PRIMARY KEY,
    salesperson VARCHAR(50) NOT NULL,
    month      DATE NOT NULL,
    amount     DECIMAL(10, 2) NOT NULL
);

INSERT INTO monthly_sales (salesperson, month, amount) VALUES
('Diana', '2024-01-01', 15000),
('Diana', '2024-02-01', 18000),
('Diana', '2024-03-01', 12000),
('Diana', '2024-04-01', 22000),
('Diana', '2024-05-01', 19000),
('Diana', '2024-06-01', 25000),
('Eve',   '2024-01-01', 20000),
('Eve',   '2024-02-01', 17000),
('Eve',   '2024-03-01', 23000),
('Eve',   '2024-04-01', 19000),
('Eve',   '2024-05-01', 21000),
('Eve',   '2024-06-01', 28000);
```

---

## What Are Window Functions?

A window function performs a calculation across a set of rows that are related to the current row. Unlike GROUP BY, which collapses rows into groups, window functions keep every row and add the result as an extra column.

```
GROUP BY:                           Window Function:
+------------+----------+          +--------+------------+--------+----------+
| department | avg_sal  |          | name   | department | salary | avg_sal  |
+------------+----------+          +--------+------------+--------+----------+
| Engineering| 91666.67 |          | Alice  | Engineering| 95000  | 91666.67 |
| Sales      | 75666.67 |          | Bob    | Engineering| 90000  | 91666.67 |
| Marketing  | 69000.00 |          | Charlie| Engineering| 90000  | 91666.67 |
+------------+----------+          | Diana  | Sales      | 75000  | 75666.67 |
                                   | Eve    | Sales      | 80000  | 75666.67 |
3 rows (details lost)              | Frank  | Sales      | 72000  | 75666.67 |
                                   | Grace  | Marketing  | 70000  | 69000.00 |
                                   | Hank   | Marketing  | 68000  | 69000.00 |
                                   +--------+------------+--------+----------+
                                   8 rows (all details kept!)
```

---

## The OVER Clause

The OVER clause is what makes a function a window function. It defines the "window" of rows the function looks at.

### Basic Syntax

```sql
function_name() OVER (
    [PARTITION BY column]
    [ORDER BY column]
    [frame_clause]
)
```

### Simplest Window Function — OVER()

An empty OVER() means "use all rows as the window":

```sql
SELECT
    name,
    department,
    salary,
    AVG(salary) OVER () AS company_avg
FROM employees;
```

```
  name   | department  |  salary  | company_avg
---------+-------------+----------+------------
 Alice   | Engineering | 95000.00 |   80000.00
 Bob     | Engineering | 90000.00 |   80000.00
 Charlie | Engineering | 90000.00 |   80000.00
 Diana   | Sales       | 75000.00 |   80000.00
 Eve     | Sales       | 80000.00 |   80000.00
 Frank   | Sales       | 72000.00 |   80000.00
 Grace   | Marketing   | 70000.00 |   80000.00
 Hank    | Marketing   | 68000.00 |   80000.00
(8 rows)
```

Every row shows the same company-wide average. The key insight: every original row is preserved, and the average is added alongside.

**Line-by-line explanation:**
- `AVG(salary)` — the aggregate function we want to calculate
- `OVER ()` — an empty window means "calculate across all rows"
- `AS company_avg` — gives the computed column a name

---

## PARTITION BY — Grouping Without Collapsing

PARTITION BY divides rows into groups (partitions), and the window function calculates separately within each group. It is like GROUP BY, but you keep all the rows.

```sql
SELECT
    name,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg
FROM employees;
```

```
  name   | department  |  salary  | dept_avg
---------+-------------+----------+----------
 Alice   | Engineering | 95000.00 | 91666.67
 Bob     | Engineering | 90000.00 | 91666.67
 Charlie | Engineering | 90000.00 | 91666.67
 Diana   | Sales       | 75000.00 | 75666.67
 Eve     | Sales       | 80000.00 | 75666.67
 Frank   | Sales       | 72000.00 | 75666.67
 Grace   | Marketing   | 70000.00 | 69000.00
 Hank    | Marketing   | 68000.00 | 69000.00
(8 rows)
```

```
How PARTITION BY works:

All Rows
+-------------------------------------------+
| Alice  | Bob | Charlie | Diana | Eve | ...|
+-------------------------------------------+
         |
    PARTITION BY department
         |
         v
+-------------+  +-----------+  +-----------+
| Engineering |  |   Sales   |  | Marketing |
| Alice       |  | Diana     |  | Grace     |
| Bob         |  | Eve       |  | Hank      |
| Charlie     |  | Frank     |  |           |
| AVG=91666   |  | AVG=75666 |  | AVG=69000 |
+-------------+  +-----------+  +-----------+

Each partition calculates independently.
All original rows are returned.
```

### Comparing Each Employee to Their Department Average

```sql
SELECT
    name,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg,
    salary - AVG(salary) OVER (PARTITION BY department) AS diff_from_avg
FROM employees
ORDER BY department, salary DESC;
```

```
  name   | department  |  salary  | dept_avg  | diff_from_avg
---------+-------------+----------+-----------+--------------
 Alice   | Engineering | 95000.00 | 91666.67 |      3333.33
 Bob     | Engineering | 90000.00 | 91666.67 |     -1666.67
 Charlie | Engineering | 90000.00 | 91666.67 |     -1666.67
 Eve     | Sales       | 80000.00 | 75666.67 |      4333.33
 Diana   | Sales       | 75000.00 | 75666.67 |      -666.67
 Frank   | Sales       | 72000.00 | 75666.67 |     -3666.67
 Grace   | Marketing   | 70000.00 | 69000.00 |      1000.00
 Hank    | Marketing   | 68000.00 | 69000.00 |     -1000.00
(8 rows)
```

Now you can instantly see who earns above or below their department average.

---

## ROW_NUMBER, RANK, and DENSE_RANK

These three functions assign a number to each row based on ordering. They differ in how they handle ties.

### ROW_NUMBER

Assigns a unique sequential number to each row. Ties get different numbers (arbitrarily).

```sql
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num
FROM employees;
```

```
  name   | department  |  salary  | row_num
---------+-------------+----------+---------
 Alice   | Engineering | 95000.00 |       1
 Bob     | Engineering | 90000.00 |       2
 Charlie | Engineering | 90000.00 |       3
 Eve     | Sales       | 80000.00 |       4
 Diana   | Sales       | 75000.00 |       5
 Frank   | Sales       | 72000.00 |       6
 Grace   | Marketing   | 70000.00 |       7
 Hank    | Marketing   | 68000.00 |       8
(8 rows)
```

Notice Bob and Charlie both earn 90,000, but they get different row numbers (2 and 3).

### RANK

Like ROW_NUMBER, but ties get the same rank. The next rank skips numbers.

```sql
SELECT
    name,
    department,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;
```

```
  name   | department  |  salary  | rank
---------+-------------+----------+------
 Alice   | Engineering | 95000.00 |    1
 Bob     | Engineering | 90000.00 |    2
 Charlie | Engineering | 90000.00 |    2
 Eve     | Sales       | 80000.00 |    4
 Diana   | Sales       | 75000.00 |    5
 Frank   | Sales       | 72000.00 |    6
 Grace   | Marketing   | 70000.00 |    7
 Hank    | Marketing   | 68000.00 |    8
(8 rows)
```

Bob and Charlie both get rank 2. The next rank is 4 (skipping 3).

### DENSE_RANK

Like RANK, but no gaps. Ties get the same rank, and the next rank is the very next number.

```sql
SELECT
    name,
    department,
    salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;
```

```
  name   | department  |  salary  | dense_rank
---------+-------------+----------+------------
 Alice   | Engineering | 95000.00 |          1
 Bob     | Engineering | 90000.00 |          2
 Charlie | Engineering | 90000.00 |          2
 Eve     | Sales       | 80000.00 |          3
 Diana   | Sales       | 75000.00 |          4
 Frank   | Sales       | 72000.00 |          5
 Grace   | Marketing   | 70000.00 |          6
 Hank    | Marketing   | 68000.00 |          7
(8 rows)
```

Bob and Charlie both get rank 2. The next rank is 3 (no gap).

### Comparison of All Three

```
+--------+--------+------------+---------+------+------------+
| name   | salary | ROW_NUMBER | RANK    | DENSE_RANK        |
+--------+--------+------------+---------+-------------------+
| Alice  | 95000  |     1      |    1    |        1          |
| Bob    | 90000  |     2      |    2    |        2          |
| Charlie| 90000  |     3      |    2    |        2   <--tie |
| Eve    | 80000  |     4      |    4    |        3          |
+--------+--------+------------+---------+-------------------+
                        ^           ^            ^
                   Always       Skip after    No gaps
                   unique       ties          after ties
```

### Ranking Within Departments

Combine ranking with PARTITION BY:

```sql
SELECT
    name,
    department,
    salary,
    RANK() OVER (
        PARTITION BY department
        ORDER BY salary DESC
    ) AS dept_rank
FROM employees;
```

```
  name   | department  |  salary  | dept_rank
---------+-------------+----------+-----------
 Alice   | Engineering | 95000.00 |         1
 Bob     | Engineering | 90000.00 |         2
 Charlie | Engineering | 90000.00 |         2
 Eve     | Sales       | 80000.00 |         1
 Diana   | Sales       | 75000.00 |         2
 Frank   | Sales       | 72000.00 |         3
 Grace   | Marketing   | 70000.00 |         1
 Hank    | Marketing   | 68000.00 |         2
(8 rows)
```

Each department has its own ranking starting from 1.

---

## LAG and LEAD — Previous and Next Rows

LAG looks at the previous row. LEAD looks at the next row. They are perfect for comparing a row to its neighbors.

### LAG — Looking Back

```sql
SELECT
    salesperson,
    month,
    amount,
    LAG(amount) OVER (
        PARTITION BY salesperson
        ORDER BY month
    ) AS prev_month,
    amount - LAG(amount) OVER (
        PARTITION BY salesperson
        ORDER BY month
    ) AS change
FROM monthly_sales
WHERE salesperson = 'Diana';
```

```
 salesperson |   month    |  amount  | prev_month |  change
-------------+------------+----------+------------+---------
 Diana       | 2024-01-01 | 15000.00 |            |
 Diana       | 2024-02-01 | 18000.00 |   15000.00 | 3000.00
 Diana       | 2024-03-01 | 12000.00 |   18000.00 |-6000.00
 Diana       | 2024-04-01 | 22000.00 |   12000.00 |10000.00
 Diana       | 2024-05-01 | 19000.00 |   22000.00 |-3000.00
 Diana       | 2024-06-01 | 25000.00 |   19000.00 | 6000.00
(6 rows)
```

**Line-by-line explanation:**
- `LAG(amount)` — gets the value of `amount` from the previous row
- `PARTITION BY salesperson` — each salesperson has their own sequence
- `ORDER BY month` — defines what "previous" means (by month)
- The first row has no previous row, so LAG returns NULL

### LAG with Default Value

You can specify a default value for when there is no previous row:

```sql
SELECT
    salesperson,
    month,
    amount,
    LAG(amount, 1, 0) OVER (
        PARTITION BY salesperson
        ORDER BY month
    ) AS prev_month
FROM monthly_sales
WHERE salesperson = 'Diana';
```

```
 salesperson |   month    |  amount  | prev_month
-------------+------------+----------+-----------
 Diana       | 2024-01-01 | 15000.00 |      0.00
 Diana       | 2024-02-01 | 18000.00 |  15000.00
 Diana       | 2024-03-01 | 12000.00 |  18000.00
 Diana       | 2024-04-01 | 22000.00 |  12000.00
 Diana       | 2024-05-01 | 19000.00 |  22000.00
 Diana       | 2024-06-01 | 25000.00 |  19000.00
(6 rows)
```

The three arguments to LAG are: `LAG(column, offset, default)`.
- `column` — which column to look at
- `offset` — how many rows back (default is 1)
- `default` — value to use when there is no previous row

### LEAD — Looking Forward

```sql
SELECT
    salesperson,
    month,
    amount,
    LEAD(amount) OVER (
        PARTITION BY salesperson
        ORDER BY month
    ) AS next_month
FROM monthly_sales
WHERE salesperson = 'Eve';
```

```
 salesperson |   month    |  amount  | next_month
-------------+------------+----------+-----------
 Eve         | 2024-01-01 | 20000.00 |  17000.00
 Eve         | 2024-02-01 | 17000.00 |  23000.00
 Eve         | 2024-03-01 | 23000.00 |  19000.00
 Eve         | 2024-04-01 | 19000.00 |  21000.00
 Eve         | 2024-05-01 | 21000.00 |  28000.00
 Eve         | 2024-06-01 | 28000.00 |
(6 rows)
```

The last row has no next row, so LEAD returns NULL.

---

## Running Totals with SUM OVER

When you combine SUM with ORDER BY in the OVER clause, you get a running total — the sum accumulates row by row.

```sql
SELECT
    salesperson,
    month,
    amount,
    SUM(amount) OVER (
        PARTITION BY salesperson
        ORDER BY month
    ) AS running_total
FROM monthly_sales
WHERE salesperson = 'Diana';
```

```
 salesperson |   month    |  amount  | running_total
-------------+------------+----------+--------------
 Diana       | 2024-01-01 | 15000.00 |     15000.00
 Diana       | 2024-02-01 | 18000.00 |     33000.00
 Diana       | 2024-03-01 | 12000.00 |     45000.00
 Diana       | 2024-04-01 | 22000.00 |     67000.00
 Diana       | 2024-05-01 | 19000.00 |     86000.00
 Diana       | 2024-06-01 | 25000.00 |    111000.00
(6 rows)
```

```
How running total works:

Month    Amount    Running Total
Jan      15000     15000            (15000)
Feb      18000     33000            (15000 + 18000)
Mar      12000     45000            (15000 + 18000 + 12000)
Apr      22000     67000            (15000 + 18000 + 12000 + 22000)
May      19000     86000            (... + 19000)
Jun      25000     111000           (... + 25000)
```

### Running Average

```sql
SELECT
    salesperson,
    month,
    amount,
    ROUND(AVG(amount) OVER (
        PARTITION BY salesperson
        ORDER BY month
    ), 2) AS running_avg
FROM monthly_sales
WHERE salesperson = 'Diana';
```

```
 salesperson |   month    |  amount  | running_avg
-------------+------------+----------+------------
 Diana       | 2024-01-01 | 15000.00 |   15000.00
 Diana       | 2024-02-01 | 18000.00 |   16500.00
 Diana       | 2024-03-01 | 12000.00 |   15000.00
 Diana       | 2024-04-01 | 22000.00 |   16750.00
 Diana       | 2024-05-01 | 19000.00 |   17200.00
 Diana       | 2024-06-01 | 25000.00 |   18500.00
(6 rows)
```

---

## NTILE — Dividing Rows into Buckets

NTILE divides rows into a specified number of roughly equal groups:

```sql
SELECT
    name,
    salary,
    NTILE(4) OVER (ORDER BY salary DESC) AS quartile
FROM employees;
```

```
  name   |  salary  | quartile
---------+----------+----------
 Alice   | 95000.00 |        1
 Bob     | 90000.00 |        1
 Charlie | 90000.00 |        2
 Eve     | 80000.00 |        2
 Diana   | 75000.00 |        3
 Frank   | 72000.00 |        3
 Grace   | 70000.00 |        4
 Hank    | 68000.00 |        4
(8 rows)
```

**Line-by-line explanation:**
- `NTILE(4)` — divide all rows into 4 groups
- `ORDER BY salary DESC` — highest salaries in group 1
- 8 employees / 4 groups = 2 per group

This is useful for percentile analysis. Quartile 1 is the top 25 percent, quartile 4 is the bottom 25 percent.

---

## Frame Clause — ROWS BETWEEN

The frame clause gives you precise control over which rows the window function considers. This is how you create moving averages and sliding windows.

### Default Frame

When you use ORDER BY in the OVER clause, the default frame is:

```
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
```

This means "from the first row in the partition up to the current row" — which is why SUM with ORDER BY gives you a running total.

### Moving Average (3-Month)

A 3-month moving average smooths out fluctuations by averaging the current row and the two rows before it:

```sql
SELECT
    salesperson,
    month,
    amount,
    ROUND(AVG(amount) OVER (
        PARTITION BY salesperson
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS moving_avg_3m
FROM monthly_sales
WHERE salesperson = 'Diana';
```

```
 salesperson |   month    |  amount  | moving_avg_3m
-------------+------------+----------+--------------
 Diana       | 2024-01-01 | 15000.00 |     15000.00
 Diana       | 2024-02-01 | 18000.00 |     16500.00
 Diana       | 2024-03-01 | 12000.00 |     15000.00
 Diana       | 2024-04-01 | 22000.00 |     17333.33
 Diana       | 2024-05-01 | 19000.00 |     17666.67
 Diana       | 2024-06-01 | 25000.00 |     22000.00
(6 rows)
```

```
How ROWS BETWEEN 2 PRECEDING AND CURRENT ROW works:

Row 1 (Jan):  AVG(15000)                        = 15000
Row 2 (Feb):  AVG(15000, 18000)                  = 16500
Row 3 (Mar):  AVG(15000, 18000, 12000)           = 15000
Row 4 (Apr):  AVG(18000, 12000, 22000)           = 17333   <-- window slides
Row 5 (May):  AVG(12000, 22000, 19000)           = 17667
Row 6 (Jun):  AVG(22000, 19000, 25000)           = 22000

         +-----+
         | Jan |  Feb   Mar   Apr   May   Jun
         +-----+
               +-------+
          Jan  |  Feb  |  Mar   Apr   May   Jun
               +-------+
               +-------------+
          Jan  |  Feb    Mar  |  Apr   May   Jun
               +-------------+
                     +-------------+
          Jan   Feb  |  Mar    Apr  |  May   Jun
                     +-------------+
                              The window slides forward!
```

### Frame Clause Options

```
+----------------------------------+----------------------------------------+
| Frame Specification              | Meaning                                |
+----------------------------------+----------------------------------------+
| ROWS BETWEEN UNBOUNDED PRECEDING | From first row to current row          |
| AND CURRENT ROW                  |                                        |
+----------------------------------+----------------------------------------+
| ROWS BETWEEN 2 PRECEDING        | From 2 rows before to current row      |
| AND CURRENT ROW                  |                                        |
+----------------------------------+----------------------------------------+
| ROWS BETWEEN 1 PRECEDING        | From 1 row before to 1 row after       |
| AND 1 FOLLOWING                  | (centered window)                      |
+----------------------------------+----------------------------------------+
| ROWS BETWEEN CURRENT ROW        | From current row to last row           |
| AND UNBOUNDED FOLLOWING          |                                        |
+----------------------------------+----------------------------------------+
| ROWS BETWEEN UNBOUNDED PRECEDING | All rows in the partition              |
| AND UNBOUNDED FOLLOWING          |                                        |
+----------------------------------+----------------------------------------+
```

### Centered Moving Average

```sql
SELECT
    salesperson,
    month,
    amount,
    ROUND(AVG(amount) OVER (
        PARTITION BY salesperson
        ORDER BY month
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ), 2) AS centered_avg
FROM monthly_sales
WHERE salesperson = 'Diana';
```

```
 salesperson |   month    |  amount  | centered_avg
-------------+------------+----------+-------------
 Diana       | 2024-01-01 | 15000.00 |    16500.00
 Diana       | 2024-02-01 | 18000.00 |    15000.00
 Diana       | 2024-03-01 | 12000.00 |    17333.33
 Diana       | 2024-04-01 | 22000.00 |    17666.67
 Diana       | 2024-05-01 | 19000.00 |    22000.00
 Diana       | 2024-06-01 | 25000.00 |    22000.00
(6 rows)
```

This looks at one row before AND one row after the current row.

---

## Practical: Ranking Employees by Department

Let us create a comprehensive employee ranking report:

```sql
SELECT
    name,
    department,
    salary,
    RANK() OVER (
        PARTITION BY department
        ORDER BY salary DESC
    ) AS dept_salary_rank,
    ROUND(salary / SUM(salary) OVER (PARTITION BY department) * 100, 1)
        AS pct_of_dept_total,
    CASE
        WHEN salary >= AVG(salary) OVER (PARTITION BY department)
        THEN 'Above Average'
        ELSE 'Below Average'
    END AS vs_dept_avg
FROM employees
ORDER BY department, salary DESC;
```

```
  name   | department  |  salary  | dept_salary_rank | pct_of_dept_total |   vs_dept_avg
---------+-------------+----------+------------------+-------------------+---------------
 Alice   | Engineering | 95000.00 |                1 |              34.5 | Above Average
 Bob     | Engineering | 90000.00 |                2 |              32.7 | Below Average
 Charlie | Engineering | 90000.00 |                2 |              32.7 | Below Average
 Grace   | Marketing   | 70000.00 |                1 |              50.7 | Above Average
 Hank    | Marketing   | 68000.00 |                2 |              49.3 | Below Average
 Eve     | Sales       | 80000.00 |                1 |              35.2 | Above Average
 Diana   | Sales       | 75000.00 |                2 |              33.0 | Below Average
 Frank   | Sales       | 72000.00 |                3 |              31.7 | Below Average
(8 rows)
```

---

## Practical: Running Sales Total with Comparison

```sql
SELECT
    salesperson,
    month,
    amount,
    SUM(amount) OVER (
        PARTITION BY salesperson
        ORDER BY month
    ) AS ytd_total,
    LAG(amount) OVER (
        PARTITION BY salesperson
        ORDER BY month
    ) AS prev_month,
    CASE
        WHEN LAG(amount) OVER (
            PARTITION BY salesperson ORDER BY month
        ) IS NULL THEN 'N/A'
        WHEN amount > LAG(amount) OVER (
            PARTITION BY salesperson ORDER BY month
        ) THEN 'UP'
        WHEN amount < LAG(amount) OVER (
            PARTITION BY salesperson ORDER BY month
        ) THEN 'DOWN'
        ELSE 'FLAT'
    END AS trend
FROM monthly_sales
ORDER BY salesperson, month;
```

```
 salesperson |   month    |  amount  | ytd_total | prev_month | trend
-------------+------------+----------+-----------+------------+------
 Diana       | 2024-01-01 | 15000.00 |  15000.00 |            | N/A
 Diana       | 2024-02-01 | 18000.00 |  33000.00 |   15000.00 | UP
 Diana       | 2024-03-01 | 12000.00 |  45000.00 |   18000.00 | DOWN
 Diana       | 2024-04-01 | 22000.00 |  67000.00 |   12000.00 | UP
 Diana       | 2024-05-01 | 19000.00 |  86000.00 |   22000.00 | DOWN
 Diana       | 2024-06-01 | 25000.00 | 111000.00 |   19000.00 | UP
 Eve         | 2024-01-01 | 20000.00 |  20000.00 |            | N/A
 Eve         | 2024-02-01 | 17000.00 |  37000.00 |   20000.00 | DOWN
 Eve         | 2024-03-01 | 23000.00 |  60000.00 |   17000.00 | UP
 Eve         | 2024-04-01 | 19000.00 |  79000.00 |   23000.00 | DOWN
 Eve         | 2024-05-01 | 21000.00 | 100000.00 |   19000.00 | UP
 Eve         | 2024-06-01 | 28000.00 | 128000.00 |   21000.00 | UP
(12 rows)
```

This single query gives you the year-to-date total, the previous month's amount, and a trend indicator — all without any JOINs or subqueries.

---

## Named Windows with WINDOW Clause

When you use the same window definition multiple times, you can name it to avoid repetition:

```sql
SELECT
    salesperson,
    month,
    amount,
    SUM(amount) OVER w AS running_total,
    AVG(amount) OVER w AS running_avg,
    COUNT(*)    OVER w AS months_so_far
FROM monthly_sales
WHERE salesperson = 'Diana'
WINDOW w AS (PARTITION BY salesperson ORDER BY month)
ORDER BY month;
```

```
 salesperson |   month    |  amount  | running_total | running_avg | months_so_far
-------------+------------+----------+---------------+-------------+--------------
 Diana       | 2024-01-01 | 15000.00 |     15000.00  |   15000.00  |            1
 Diana       | 2024-02-01 | 18000.00 |     33000.00  |   16500.00  |            2
 Diana       | 2024-03-01 | 12000.00 |     45000.00  |   15000.00  |            3
 Diana       | 2024-04-01 | 22000.00 |     67000.00  |   16750.00  |            4
 Diana       | 2024-05-01 | 19000.00 |     86000.00  |   17200.00  |            5
 Diana       | 2024-06-01 | 25000.00 |    111000.00  |   18500.00  |            6
(6 rows)
```

The `WINDOW w AS (...)` at the bottom defines the window once, and all three functions reference it with `OVER w`.

---

## Common Mistakes

### Mistake 1: Using Window Functions in WHERE

```sql
-- BAD: You cannot filter by a window function in WHERE
SELECT name, salary, RANK() OVER (ORDER BY salary DESC) AS rnk
FROM employees
WHERE rnk <= 3;   -- ERROR!

-- GOOD: Use a subquery or CTE
SELECT * FROM (
    SELECT name, salary, RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM employees
) ranked
WHERE rnk <= 3;
```

Window functions are computed after WHERE, so you must wrap the query.

### Mistake 2: Confusing RANK, DENSE_RANK, and ROW_NUMBER

```sql
-- If you want exactly 3 results, use ROW_NUMBER:
-- RANK might return more than 3 if there are ties at position 3

-- ROW_NUMBER: Always exactly N results
-- RANK: Might return more than N (ties share a rank)
-- DENSE_RANK: No gaps, but might still return more than N
```

### Mistake 3: Forgetting ORDER BY in Running Totals

```sql
-- BAD: Without ORDER BY, SUM gives the total for the whole partition
SELECT month, amount,
       SUM(amount) OVER (PARTITION BY salesperson) AS not_running
FROM monthly_sales;
-- Every row shows the same total!

-- GOOD: Add ORDER BY for a running total
SELECT month, amount,
       SUM(amount) OVER (
           PARTITION BY salesperson
           ORDER BY month
       ) AS running_total
FROM monthly_sales;
```

### Mistake 4: Not Understanding the Default Frame

```sql
-- With ORDER BY, the default frame is:
-- RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
-- This means SUM gives a running total, not a full partition total.
-- Without ORDER BY, the default frame is the entire partition.
```

---

## Best Practices

1. **Use named windows (WINDOW clause) when reusing the same definition.** It reduces code duplication and makes queries easier to maintain.

2. **Choose the right ranking function.** Use ROW_NUMBER for unique numbering, RANK for competition-style ranking (with gaps), and DENSE_RANK for ranking without gaps.

3. **Always specify ORDER BY in the OVER clause** when using LAG, LEAD, or running totals. The result is undefined without it.

4. **Use window functions instead of self-joins.** Comparing rows to previous rows with LAG is much cleaner and faster than joining a table to itself.

5. **Be explicit about the frame clause** when using aggregate window functions with ORDER BY. Do not rely on the default frame unless you are certain it does what you want.

---

## Quick Summary

```
+-------------------+------------------------------------------------+
| Function          | What It Does                                   |
+-------------------+------------------------------------------------+
| ROW_NUMBER()      | Unique sequential number (no ties)             |
| RANK()            | Rank with gaps after ties                      |
| DENSE_RANK()      | Rank without gaps after ties                   |
| LAG(col, n)       | Value from n rows before (default n=1)         |
| LEAD(col, n)      | Value from n rows after (default n=1)          |
| SUM() OVER        | Running total (with ORDER BY)                  |
| AVG() OVER        | Running average (with ORDER BY)                |
| NTILE(n)          | Divide rows into n equal buckets               |
| PARTITION BY      | Split rows into groups (like GROUP BY)          |
| ROWS BETWEEN      | Define exact frame of rows to consider          |
+-------------------+------------------------------------------------+
```

---

## Key Points

- Window functions calculate across related rows without collapsing them — every row is preserved.
- The OVER clause defines the window. An empty OVER() uses all rows.
- PARTITION BY splits rows into independent groups for calculation.
- ROW_NUMBER gives unique numbers; RANK and DENSE_RANK handle ties differently.
- LAG looks at previous rows; LEAD looks at next rows. Both are great for comparisons.
- SUM with ORDER BY in OVER gives you a running total.
- The frame clause (ROWS BETWEEN) controls exactly which rows the function considers.
- Named windows (WINDOW clause) reduce repetition when multiple functions share the same window.
- Window functions cannot be used in WHERE — wrap the query in a subquery instead.

---

## Practice Questions

1. What is the difference between GROUP BY and a window function with PARTITION BY? When would you use each?

2. You have a table of exam scores. Three students scored 95. What rank would the next student (scoring 90) receive with RANK vs DENSE_RANK?

3. What does `LAG(amount, 2, 0)` return? What do the three arguments mean?

4. Why does `SUM(amount) OVER (PARTITION BY salesperson ORDER BY month)` give a running total, but `SUM(amount) OVER (PARTITION BY salesperson)` gives the same total for every row?

5. Can you use a window function in a WHERE clause? If not, how do you filter by a window function's result?

---

## Exercises

### Exercise 1: Top Earners per Department

Write a query that shows the top 2 highest-paid employees in each department. Include their name, department, salary, and rank within the department. Use ROW_NUMBER to ensure exactly 2 results per department.

**Hint**: Use ROW_NUMBER with PARTITION BY department, then wrap it in a subquery to filter.

### Exercise 2: Month-over-Month Growth Rate

Using the monthly_sales table, write a query that shows each salesperson's monthly sales along with:
- The previous month's sales
- The percentage change from the previous month
- Whether sales went UP, DOWN, or stayed FLAT

**Hint**: Use LAG to get the previous month's value, then calculate the percentage.

### Exercise 3: Moving Average Report

Create a report showing each salesperson's monthly sales with a 3-month moving average. Also include the cumulative year-to-date total. Use the WINDOW clause to avoid repeating the partition definition.

**Hint**: The moving average needs `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`. The running total uses the default frame.

---

## What Is Next?

In Chapter 27, you will learn about Common Table Expressions (CTEs) and recursive queries. CTEs let you break complex queries into named, readable steps — like giving names to temporary results. Recursive CTEs take it further, letting you traverse hierarchies like organizational charts and category trees.
