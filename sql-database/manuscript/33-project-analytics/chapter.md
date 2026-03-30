# Chapter 33: Project -- Analytics Queries for Business Intelligence

## What You Will Learn

In this chapter, you will write the kind of SQL queries that data analysts and business intelligence teams use every day. You will calculate daily, weekly, and monthly revenue, measure year-over-year growth, compute running totals and moving averages, perform customer cohort analysis, segment customers using RFM analysis, find top products per category, and build a conversion funnel. By the end, you will have a complete set of dashboard queries ready for any reporting tool.

## Why This Chapter Matters

Raw data sitting in a database is like crude oil. It has tremendous value, but only after it is refined. Analytics queries are the refinery. They transform rows of transactions into answers: "Is revenue growing?" "Which customers are we losing?" "Which products drive the most profit?"

Every modern business runs on data-driven decisions. The person who can write these queries is invaluable. Whether you become a developer, analyst, or data engineer, these skills will serve you throughout your career.

---

## Setting Up the Dataset

For this chapter, we will work with a sales dataset. If you completed the e-commerce project in Chapter 32, you can use that database. Otherwise, here is a focused dataset for analytics work.

### Create the Tables

```sql
CREATE TABLE customers (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    region          VARCHAR(50) NOT NULL,
    signup_date     DATE NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    category        VARCHAR(100) NOT NULL,
    price           NUMERIC(10, 2) NOT NULL,
    cost            NUMERIC(10, 2) NOT NULL
);

CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers(id),
    order_date      DATE NOT NULL,
    total_amount    NUMERIC(12, 2) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'completed'
);

CREATE TABLE order_items (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER REFERENCES orders(id),
    product_id      INTEGER REFERENCES products(id),
    quantity        INTEGER NOT NULL,
    unit_price      NUMERIC(10, 2) NOT NULL,
    subtotal        NUMERIC(12, 2) NOT NULL
);

-- Funnel tracking table
CREATE TABLE user_events (
    id              SERIAL PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers(id),
    event_type      VARCHAR(50) NOT NULL,
    event_date      TIMESTAMP NOT NULL,
    metadata        JSONB
);
```

### Insert Sample Data

```sql
-- Customers across different regions
INSERT INTO customers (name, email, region, signup_date) VALUES
    ('Alice Johnson',   'alice@example.com',    'West',     '2023-01-15'),
    ('Bob Smith',       'bob@example.com',      'East',     '2023-02-20'),
    ('Carol Williams',  'carol@example.com',    'West',     '2023-03-10'),
    ('David Brown',     'david@example.com',    'Central',  '2023-04-05'),
    ('Eve Davis',       'eve@example.com',      'East',     '2023-05-12'),
    ('Frank Miller',    'frank@example.com',    'West',     '2023-06-18'),
    ('Grace Taylor',    'grace@example.com',    'Central',  '2023-07-22'),
    ('Henry Anderson',  'henry@example.com',    'East',     '2023-08-30'),
    ('Ivy Chen',        'ivy@example.com',      'West',     '2023-09-15'),
    ('Jack Wilson',     'jack@example.com',     'Central',  '2023-10-01'),
    ('Karen Lee',       'karen@example.com',    'East',     '2024-01-10'),
    ('Leo Martinez',    'leo@example.com',      'West',     '2024-02-14'),
    ('Mia Robinson',    'mia@example.com',      'Central',  '2024-03-20'),
    ('Noah Clark',      'noah@example.com',     'East',     '2024-04-15'),
    ('Olivia Hall',     'olivia@example.com',   'West',     '2024-05-25');

-- Products with cost data for profit analysis
INSERT INTO products (name, category, price, cost) VALUES
    ('ProBook Laptop',       'Electronics',  999.99,  650.00),
    ('SmartPhone X',         'Electronics',  799.99,  480.00),
    ('Wireless Earbuds',     'Electronics',  129.99,   55.00),
    ('Running Shoes',        'Sports',        89.99,   35.00),
    ('Yoga Mat',             'Sports',        29.99,   10.00),
    ('Coffee Maker',         'Home',         149.99,   70.00),
    ('Blender Pro',          'Home',          79.99,   30.00),
    ('SQL Mastery Book',     'Books',         39.99,   12.00),
    ('Data Science Guide',   'Books',         49.99,   15.00),
    ('Winter Jacket',        'Clothing',     199.99,   85.00);

-- Orders spanning 2023 and 2024
INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
    -- 2023 Q1
    (1,  '2023-01-20',  999.99, 'completed'),
    (1,  '2023-02-15',  129.99, 'completed'),
    (2,  '2023-03-01',  799.99, 'completed'),
    (3,  '2023-03-15',   89.99, 'completed'),
    -- 2023 Q2
    (1,  '2023-04-10',   39.99, 'completed'),
    (2,  '2023-04-22',  149.99, 'completed'),
    (4,  '2023-05-08',  129.99, 'completed'),
    (3,  '2023-05-20',   79.99, 'completed'),
    (5,  '2023-06-05',  999.99, 'completed'),
    (5,  '2023-06-25',   29.99, 'completed'),
    -- 2023 Q3
    (1,  '2023-07-12',  199.99, 'completed'),
    (6,  '2023-07-18',  799.99, 'completed'),
    (2,  '2023-08-05',   89.99, 'completed'),
    (7,  '2023-08-14',  129.99, 'completed'),
    (3,  '2023-09-01',   49.99, 'completed'),
    (8,  '2023-09-20',  149.99, 'completed'),
    -- 2023 Q4
    (1,  '2023-10-15',  129.99, 'completed'),
    (4,  '2023-10-28',  799.99, 'completed'),
    (9,  '2023-11-05',   39.99, 'completed'),
    (5,  '2023-11-18',  199.99, 'completed'),
    (2,  '2023-12-01',  149.99, 'completed'),
    (10, '2023-12-15',  999.99, 'completed'),
    (6,  '2023-12-22',   49.99, 'completed'),
    -- 2024 Q1
    (1,  '2024-01-08',   89.99, 'completed'),
    (11, '2024-01-15',  799.99, 'completed'),
    (3,  '2024-01-22',  129.99, 'completed'),
    (2,  '2024-02-10',  999.99, 'completed'),
    (4,  '2024-02-18',   79.99, 'completed'),
    (12, '2024-02-25',  149.99, 'completed'),
    (5,  '2024-03-05',   39.99, 'completed'),
    (7,  '2024-03-12',  199.99, 'completed'),
    (8,  '2024-03-28',   49.99, 'completed'),
    -- 2024 Q2
    (1,  '2024-04-02',  799.99, 'completed'),
    (13, '2024-04-10',  129.99, 'completed'),
    (6,  '2024-04-20',   89.99, 'completed'),
    (3,  '2024-05-08',  999.99, 'completed'),
    (14, '2024-05-15',   29.99, 'completed'),
    (9,  '2024-05-22',  149.99, 'completed'),
    (2,  '2024-06-01',  129.99, 'completed'),
    (10, '2024-06-12',  199.99, 'completed'),
    (4,  '2024-06-25',   49.99, 'completed');

-- Order items (simplified - one item per order for clarity)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES
    (1,  1, 1, 999.99, 999.99), (2,  3, 1, 129.99, 129.99),
    (3,  2, 1, 799.99, 799.99), (4,  4, 1,  89.99,  89.99),
    (5,  8, 1,  39.99,  39.99), (6,  6, 1, 149.99, 149.99),
    (7,  3, 1, 129.99, 129.99), (8,  7, 1,  79.99,  79.99),
    (9,  1, 1, 999.99, 999.99), (10, 5, 1,  29.99,  29.99),
    (11,10, 1, 199.99, 199.99), (12, 2, 1, 799.99, 799.99),
    (13, 4, 1,  89.99,  89.99), (14, 3, 1, 129.99, 129.99),
    (15, 9, 1,  49.99,  49.99), (16, 6, 1, 149.99, 149.99),
    (17, 3, 1, 129.99, 129.99), (18, 2, 1, 799.99, 799.99),
    (19, 8, 1,  39.99,  39.99), (20,10, 1, 199.99, 199.99),
    (21, 6, 1, 149.99, 149.99), (22, 1, 1, 999.99, 999.99),
    (23, 9, 1,  49.99,  49.99), (24, 4, 1,  89.99,  89.99),
    (25, 2, 1, 799.99, 799.99), (26, 3, 1, 129.99, 129.99),
    (27, 1, 1, 999.99, 999.99), (28, 7, 1,  79.99,  79.99),
    (29, 6, 1, 149.99, 149.99), (30, 8, 1,  39.99,  39.99),
    (31,10, 1, 199.99, 199.99), (32, 9, 1,  49.99,  49.99),
    (33, 2, 1, 799.99, 799.99), (34, 3, 1, 129.99, 129.99),
    (35, 4, 1,  89.99,  89.99), (36, 1, 1, 999.99, 999.99),
    (37, 5, 1,  29.99,  29.99), (38, 6, 1, 149.99, 149.99),
    (39, 3, 1, 129.99, 129.99), (40,10, 1, 199.99, 199.99),
    (41, 9, 1,  49.99,  49.99);

-- Funnel events
INSERT INTO user_events (customer_id, event_type, event_date) VALUES
    -- Full funnel users
    (1,  'signup',    '2023-01-15 10:00:00'),
    (1,  'browse',    '2023-01-15 10:05:00'),
    (1,  'add_to_cart','2023-01-18 14:30:00'),
    (1,  'purchase',  '2023-01-20 09:00:00'),
    (2,  'signup',    '2023-02-20 11:00:00'),
    (2,  'browse',    '2023-02-20 11:10:00'),
    (2,  'add_to_cart','2023-02-25 16:00:00'),
    (2,  'purchase',  '2023-03-01 10:00:00'),
    (3,  'signup',    '2023-03-10 09:00:00'),
    (3,  'browse',    '2023-03-10 09:15:00'),
    (3,  'add_to_cart','2023-03-12 13:00:00'),
    (3,  'purchase',  '2023-03-15 11:00:00'),
    -- Dropped at cart
    (4,  'signup',    '2023-04-05 14:00:00'),
    (4,  'browse',    '2023-04-05 14:20:00'),
    (4,  'add_to_cart','2023-04-06 10:00:00'),
    (4,  'purchase',  '2023-05-08 15:00:00'),
    -- Browse but no cart
    (5,  'signup',    '2023-05-12 08:00:00'),
    (5,  'browse',    '2023-05-12 08:30:00'),
    (5,  'add_to_cart','2023-05-15 12:00:00'),
    (5,  'purchase',  '2023-06-05 14:00:00'),
    -- Signup only
    (6,  'signup',    '2023-06-18 16:00:00'),
    (6,  'browse',    '2023-06-20 10:00:00'),
    (6,  'add_to_cart','2023-07-10 09:00:00'),
    (6,  'purchase',  '2023-07-18 11:00:00'),
    (7,  'signup',    '2023-07-22 13:00:00'),
    (7,  'browse',    '2023-07-22 13:30:00'),
    (7,  'add_to_cart','2023-08-01 15:00:00'),
    (7,  'purchase',  '2023-08-14 09:00:00'),
    (8,  'signup',    '2023-08-30 10:00:00'),
    (8,  'browse',    '2023-08-30 10:15:00'),
    (8,  'add_to_cart','2023-09-10 14:00:00'),
    (8,  'purchase',  '2023-09-20 16:00:00'),
    -- Additional signups with partial funnels
    (9,  'signup',    '2023-09-15 11:00:00'),
    (9,  'browse',    '2023-09-16 09:00:00'),
    (9,  'add_to_cart','2023-10-20 14:00:00'),
    (9,  'purchase',  '2023-11-05 10:00:00'),
    (10, 'signup',    '2023-10-01 15:00:00'),
    (10, 'browse',    '2023-10-02 10:00:00'),
    (10, 'add_to_cart','2023-11-28 09:00:00'),
    (10, 'purchase',  '2023-12-15 14:00:00'),
    (11, 'signup',    '2024-01-10 09:00:00'),
    (11, 'browse',    '2024-01-10 09:20:00'),
    (11, 'add_to_cart','2024-01-12 11:00:00'),
    (11, 'purchase',  '2024-01-15 13:00:00'),
    (12, 'signup',    '2024-02-14 10:00:00'),
    (12, 'browse',    '2024-02-14 10:30:00'),
    (12, 'add_to_cart','2024-02-20 16:00:00'),
    (12, 'purchase',  '2024-02-25 09:00:00'),
    (13, 'signup',    '2024-03-20 14:00:00'),
    (13, 'browse',    '2024-03-21 10:00:00'),
    (13, 'add_to_cart','2024-03-25 15:00:00'),
    (13, 'purchase',  '2024-04-10 11:00:00'),
    (14, 'signup',    '2024-04-15 08:00:00'),
    (14, 'browse',    '2024-04-15 08:45:00'),
    (14, 'add_to_cart','2024-04-20 13:00:00'),
    (14, 'purchase',  '2024-05-15 10:00:00'),
    (15, 'signup',    '2024-05-25 12:00:00'),
    (15, 'browse',    '2024-05-25 12:30:00'),
    (15, 'add_to_cart','2024-06-01 14:00:00');
    -- Customer 15 has not purchased yet (dropped at add_to_cart)
```

---

## Daily, Weekly, and Monthly Revenue

### Daily Revenue

```sql
SELECT
    order_date,
    COUNT(*)                AS order_count,
    SUM(total_amount)       AS daily_revenue
FROM orders
WHERE status = 'completed'
  AND order_date >= '2024-01-01'
GROUP BY order_date
ORDER BY order_date;
```

```
+------------+-------------+---------------+
| order_date | order_count | daily_revenue |
+------------+-------------+---------------+
| 2024-01-08 |           1 |         89.99 |
| 2024-01-15 |           1 |        799.99 |
| 2024-01-22 |           1 |        129.99 |
| 2024-02-10 |           1 |        999.99 |
| 2024-02-18 |           1 |         79.99 |
| 2024-02-25 |           1 |        149.99 |
| 2024-03-05 |           1 |         39.99 |
| 2024-03-12 |           1 |        199.99 |
| 2024-03-28 |           1 |         49.99 |
| ...        |         ... |           ... |
+------------+-------------+---------------+
```

### Weekly Revenue with DATE_TRUNC

`DATE_TRUNC` is the key function for time-based aggregations. It rounds a date down to the start of a period.

```sql
SELECT
    DATE_TRUNC('week', order_date)::DATE    AS week_starting,
    COUNT(*)                                 AS order_count,
    SUM(total_amount)                        AS weekly_revenue,
    ROUND(AVG(total_amount), 2)              AS avg_order_value
FROM orders
WHERE status = 'completed'
  AND order_date >= '2024-01-01'
GROUP BY DATE_TRUNC('week', order_date)
ORDER BY week_starting;
```

```
+---------------+-------------+----------------+-----------------+
| week_starting | order_count | weekly_revenue | avg_order_value |
+---------------+-------------+----------------+-----------------+
| 2024-01-08    |           2 |         889.98 |          444.99 |
| 2024-01-22    |           1 |         129.99 |          129.99 |
| 2024-02-05    |           1 |         999.99 |          999.99 |
| 2024-02-12    |           1 |          79.99 |           79.99 |
| 2024-02-19    |           1 |         149.99 |          149.99 |
| 2024-03-04    |           1 |          39.99 |           39.99 |
| 2024-03-11    |           1 |         199.99 |          199.99 |
| 2024-03-25    |           1 |          49.99 |           49.99 |
| ...           |         ... |            ... |             ... |
+---------------+-------------+----------------+-----------------+
```

Let us break down the key parts:

- `DATE_TRUNC('week', order_date)` -- Rounds each date to the Monday of its week. For example, a Wednesday on January 10th becomes Monday January 8th.
- `::DATE` -- Casts the result to a date (removes the time portion).
- We group by the truncated date, so all orders within the same week are combined.

### Monthly Revenue

```sql
SELECT
    TO_CHAR(DATE_TRUNC('month', order_date), 'YYYY-MM')  AS month,
    COUNT(*)                                               AS order_count,
    SUM(total_amount)                                      AS monthly_revenue,
    ROUND(AVG(total_amount), 2)                            AS avg_order_value
FROM orders
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY DATE_TRUNC('month', order_date);
```

```
+---------+-------------+-----------------+-----------------+
| month   | order_count | monthly_revenue | avg_order_value |
+---------+-------------+-----------------+-----------------+
| 2023-01 |           1 |          999.99 |          999.99 |
| 2023-02 |           1 |          129.99 |          129.99 |
| 2023-03 |           2 |          889.98 |          444.99 |
| 2023-04 |           2 |          189.98 |           94.99 |
| 2023-05 |           2 |          209.98 |          104.99 |
| 2023-06 |           2 |         1029.98 |          514.99 |
| 2023-07 |           2 |          999.98 |          499.99 |
| 2023-08 |           2 |          219.98 |          109.99 |
| 2023-09 |           2 |          199.98 |           99.99 |
| 2023-10 |           2 |          929.98 |          464.99 |
| 2023-11 |           2 |          239.98 |          119.99 |
| 2023-12 |           3 |         1199.97 |          399.99 |
| 2024-01 |           3 |         1019.97 |          339.99 |
| 2024-02 |           3 |         1229.97 |          409.99 |
| 2024-03 |           3 |          289.97 |           96.66 |
| 2024-04 |           3 |         1019.97 |          339.99 |
| 2024-05 |           3 |         1059.97 |          353.32 |
| 2024-06 |           3 |          379.97 |          126.66 |
+---------+-------------+-----------------+-----------------+
(18 rows)
```

---

## Year-over-Year Growth

Year-over-year (YoY) growth compares each month to the same month in the previous year. This is one of the most important business metrics because it removes seasonal effects.

```sql
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date)::DATE   AS month,
        SUM(total_amount)                        AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
    TO_CHAR(month, 'YYYY-MM')                   AS month,
    revenue                                      AS current_revenue,
    LAG(revenue, 12) OVER (ORDER BY month)       AS prior_year_revenue,
    CASE
        WHEN LAG(revenue, 12) OVER (ORDER BY month) IS NOT NULL
        THEN ROUND(
            (revenue - LAG(revenue, 12) OVER (ORDER BY month))
            / LAG(revenue, 12) OVER (ORDER BY month) * 100,
            1
        )
    END                                          AS yoy_growth_pct
FROM monthly_revenue
ORDER BY month;
```

```
+---------+-----------------+--------------------+-----------------+
| month   | current_revenue | prior_year_revenue | yoy_growth_pct  |
+---------+-----------------+--------------------+-----------------+
| 2023-01 |          999.99 |               NULL |            NULL |
| 2023-02 |          129.99 |               NULL |            NULL |
| 2023-03 |          889.98 |               NULL |            NULL |
| 2023-04 |          189.98 |               NULL |            NULL |
| 2023-05 |          209.98 |               NULL |            NULL |
| 2023-06 |         1029.98 |               NULL |            NULL |
| 2023-07 |          999.98 |               NULL |            NULL |
| 2023-08 |          219.98 |               NULL |            NULL |
| 2023-09 |          199.98 |               NULL |            NULL |
| 2023-10 |          929.98 |               NULL |            NULL |
| 2023-11 |          239.98 |               NULL |            NULL |
| 2023-12 |         1199.97 |               NULL |            NULL |
| 2024-01 |         1019.97 |            999.99  |             2.0 |
| 2024-02 |         1229.97 |            129.99  |           846.2 |
| 2024-03 |          289.97 |            889.98  |           -67.4 |
| 2024-04 |         1019.97 |            189.98  |           436.9 |
| 2024-05 |         1059.97 |            209.98  |           404.8 |
| 2024-06 |          379.97 |           1029.98  |           -63.1 |
+---------+-----------------+--------------------+-----------------+
(18 rows)
```

Let us break down the key function:

- `LAG(revenue, 12) OVER (ORDER BY month)` -- The `LAG` window function looks back 12 rows (12 months = 1 year) to find the same month's revenue from last year.
- The growth percentage formula is: `(current - previous) / previous * 100`.
- We wrap it in a `CASE` to handle the first year where there is no prior data (NULL).

This query tells us, for example, that January 2024 revenue grew 2.0% compared to January 2023, while February 2024 saw a massive 846.2% increase over February 2023.

---

## Running Totals and Moving Averages

### Running Total (Cumulative Revenue)

A running total shows how revenue accumulates over time. Think of it as a score that only goes up.

```sql
SELECT
    TO_CHAR(DATE_TRUNC('month', order_date), 'YYYY-MM')  AS month,
    SUM(total_amount)                                     AS monthly_revenue,
    SUM(SUM(total_amount)) OVER (
        ORDER BY DATE_TRUNC('month', order_date)
    )                                                     AS cumulative_revenue
FROM orders
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY DATE_TRUNC('month', order_date);
```

```
+---------+-----------------+--------------------+
| month   | monthly_revenue | cumulative_revenue |
+---------+-----------------+--------------------+
| 2023-01 |          999.99 |             999.99 |
| 2023-02 |          129.99 |            1129.98 |
| 2023-03 |          889.98 |            2019.96 |
| 2023-04 |          189.98 |            2209.94 |
| 2023-05 |          209.98 |            2419.92 |
| 2023-06 |         1029.98 |            3449.90 |
| 2023-07 |          999.98 |            4449.88 |
| 2023-08 |          219.98 |            4669.86 |
| 2023-09 |          199.98 |            4869.84 |
| 2023-10 |          929.98 |            5799.82 |
| 2023-11 |          239.98 |            6039.80 |
| 2023-12 |         1199.97 |            7239.77 |
| 2024-01 |         1019.97 |            8259.74 |
| ...     |             ... |                ... |
+---------+-----------------+--------------------+
```

The trick here is `SUM(SUM(total_amount)) OVER (...)`. The inner `SUM` groups by month. The outer `SUM ... OVER` creates a running total across all months.

### 3-Month Moving Average

A moving average smooths out spikes and dips, revealing the underlying trend. It is like averaging your last three test scores instead of looking at each one individually.

```sql
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_date)::DATE   AS month,
        SUM(total_amount)                        AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
    TO_CHAR(month, 'YYYY-MM')       AS month,
    revenue                          AS monthly_revenue,
    ROUND(AVG(revenue) OVER (
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                            AS moving_avg_3m
FROM monthly
ORDER BY month;
```

```
+---------+-----------------+----------------+
| month   | monthly_revenue | moving_avg_3m  |
+---------+-----------------+----------------+
| 2023-01 |          999.99 |         999.99 |
| 2023-02 |          129.99 |         564.99 |
| 2023-03 |          889.98 |         673.32 |
| 2023-04 |          189.98 |         403.32 |
| 2023-05 |          209.98 |         429.98 |
| 2023-06 |         1029.98 |         476.65 |
| 2023-07 |          999.98 |         746.65 |
| 2023-08 |          219.98 |         749.98 |
| 2023-09 |          199.98 |         473.31 |
| 2023-10 |          929.98 |         449.98 |
| 2023-11 |          239.98 |         456.65 |
| 2023-12 |         1199.97 |         789.98 |
| 2024-01 |         1019.97 |         819.97 |
| 2024-02 |         1229.97 |        1149.97 |
| 2024-03 |          289.97 |         846.64 |
| 2024-04 |         1019.97 |         846.64 |
| 2024-05 |         1059.97 |         789.97 |
| 2024-06 |          379.97 |         819.97 |
+---------+-----------------+----------------+
(18 rows)
```

The key is `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`. This tells PostgreSQL to average the current row plus the two rows before it -- a 3-month window.

The moving average reveals the trend more clearly. While monthly revenue jumps around from 129.99 to 1029.98, the moving average moves more smoothly, making it easier to see whether the business is growing or shrinking.

---

## Customer Cohort Analysis

Cohort analysis groups customers by when they first joined (their "cohort") and tracks their behavior over time. It answers the question: "Are we retaining our customers?"

### Step 1: Identify Each Customer's Cohort

A customer's cohort is the month they made their first purchase:

```sql
WITH customer_cohort AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date))::DATE AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
customer_orders AS (
    SELECT
        o.customer_id,
        cc.cohort_month,
        DATE_TRUNC('month', o.order_date)::DATE AS order_month,
        -- Months since first purchase
        EXTRACT(YEAR FROM AGE(
            DATE_TRUNC('month', o.order_date),
            cc.cohort_month
        )) * 12 +
        EXTRACT(MONTH FROM AGE(
            DATE_TRUNC('month', o.order_date),
            cc.cohort_month
        )) AS months_since_first
    FROM orders o
    JOIN customer_cohort cc ON cc.customer_id = o.customer_id
    WHERE o.status = 'completed'
)
SELECT
    TO_CHAR(cohort_month, 'YYYY-MM')            AS cohort,
    months_since_first                           AS month_number,
    COUNT(DISTINCT customer_id)                  AS active_customers
FROM customer_orders
GROUP BY cohort_month, months_since_first
ORDER BY cohort_month, months_since_first;
```

```
+---------+--------------+------------------+
| cohort  | month_number | active_customers |
+---------+--------------+------------------+
| 2023-01 |            0 |                1 |
| 2023-01 |            1 |                1 |
| 2023-01 |            3 |                1 |
| 2023-01 |            6 |                1 |
| 2023-01 |            9 |                1 |
| 2023-01 |           12 |                1 |
| 2023-01 |           15 |                1 |
| 2023-03 |            0 |                2 |
| 2023-03 |            2 |                1 |
| 2023-03 |            6 |                1 |
| 2023-03 |           10 |                1 |
| 2023-03 |           14 |                1 |
| ...     |          ... |              ... |
+---------+--------------+------------------+
```

### Step 2: Cohort Retention Table

The classic cohort retention table shows what percentage of each cohort returns in subsequent months:

```sql
WITH customer_cohort AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date))::DATE AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohort
    GROUP BY cohort_month
),
customer_activity AS (
    SELECT DISTINCT
        cc.cohort_month,
        o.customer_id,
        EXTRACT(YEAR FROM AGE(
            DATE_TRUNC('month', o.order_date),
            cc.cohort_month
        )) * 12 +
        EXTRACT(MONTH FROM AGE(
            DATE_TRUNC('month', o.order_date),
            cc.cohort_month
        )) AS month_number
    FROM orders o
    JOIN customer_cohort cc ON cc.customer_id = o.customer_id
    WHERE o.status = 'completed'
)
SELECT
    TO_CHAR(ca.cohort_month, 'YYYY-MM')         AS cohort,
    cs.cohort_size,
    ROUND(COUNT(DISTINCT CASE WHEN month_number = 0  THEN customer_id END)::NUMERIC
        / cs.cohort_size * 100)                  AS "M0",
    ROUND(COUNT(DISTINCT CASE WHEN month_number = 1  THEN customer_id END)::NUMERIC
        / cs.cohort_size * 100)                  AS "M1",
    ROUND(COUNT(DISTINCT CASE WHEN month_number = 2  THEN customer_id END)::NUMERIC
        / cs.cohort_size * 100)                  AS "M2",
    ROUND(COUNT(DISTINCT CASE WHEN month_number = 3  THEN customer_id END)::NUMERIC
        / cs.cohort_size * 100)                  AS "M3",
    ROUND(COUNT(DISTINCT CASE WHEN month_number = 6  THEN customer_id END)::NUMERIC
        / cs.cohort_size * 100)                  AS "M6"
FROM customer_activity ca
JOIN cohort_sizes cs ON cs.cohort_month = ca.cohort_month
GROUP BY ca.cohort_month, cs.cohort_size
ORDER BY ca.cohort_month;
```

```
+---------+-------------+------+------+------+------+------+
| cohort  | cohort_size | M0   | M1   | M2   | M3   | M6   |
+---------+-------------+------+------+------+------+------+
| 2023-01 |           1 |  100 |  100 |    0 |  100 |  100 |
| 2023-03 |           2 |  100 |    0 |   50 |    0 |   50 |
| 2023-04 |           1 |  100 |    0 |    0 |    0 |    0 |
| 2023-05 |           2 |  100 |   50 |    0 |    0 |   50 |
| 2023-06 |           1 |  100 |    0 |    0 |    0 |    0 |
| 2023-07 |           1 |  100 |  100 |    0 |    0 |    0 |
| 2023-08 |           1 |  100 |    0 |    0 |    0 |    0 |
| 2023-09 |           1 |  100 |    0 |    0 |    0 |    0 |
| 2023-10 |           1 |  100 |    0 |  100 |    0 |    0 |
| 2023-12 |           1 |  100 |    0 |    0 |    0 |  100 |
| 2024-01 |           1 |  100 |    0 |    0 |    0 |    0 |
| 2024-02 |           1 |  100 |    0 |    0 |    0 |    0 |
| 2024-04 |           2 |  100 |   50 |    0 |    0 |    0 |
+---------+-------------+------+------+------+------+------+
```

How to read this table:

- The 2023-01 cohort (1 customer) had 100% active in month 0 (by definition), 100% in month 1, then returned in months 3 and 6.
- The 2023-03 cohort (2 customers) had 100% in month 0, but only 50% (1 of 2) returned in month 2.

This is one of the most powerful analytical tools in business. High retention means customers keep coming back. Low retention means you are losing people.

---

## RFM Analysis

RFM stands for Recency, Frequency, and Monetary value. It is a customer segmentation technique that divides customers into groups based on:

- **Recency**: How recently did they buy? (Recent buyers are more engaged)
- **Frequency**: How often do they buy? (Frequent buyers are more loyal)
- **Monetary**: How much do they spend? (High spenders are more valuable)

```sql
WITH rfm_raw AS (
    SELECT
        c.id                                AS customer_id,
        c.name                              AS customer_name,
        -- Recency: days since last purchase
        CURRENT_DATE - MAX(o.order_date)    AS recency_days,
        -- Frequency: number of orders
        COUNT(DISTINCT o.id)                AS frequency,
        -- Monetary: total amount spent
        SUM(o.total_amount)                 AS monetary
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.name
),
rfm_scored AS (
    SELECT
        customer_id,
        customer_name,
        recency_days,
        frequency,
        ROUND(monetary, 2)                  AS monetary,
        -- Score each dimension from 1-4 using NTILE
        NTILE(4) OVER (ORDER BY recency_days DESC)     AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC)          AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC)           AS m_score
    FROM rfm_raw
)
SELECT
    customer_name,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    r_score + f_score + m_score     AS rfm_total,
    CASE
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 2                   THEN 'Loyal Customers'
        WHEN r_score >= 3 AND f_score = 1                    THEN 'New Customers'
        WHEN r_score = 2  AND f_score >= 2                   THEN 'At Risk'
        WHEN r_score = 1  AND f_score >= 2                   THEN 'Losing Them'
        WHEN r_score = 1  AND f_score = 1                    THEN 'Lost'
        ELSE 'Other'
    END                              AS segment
FROM rfm_scored
ORDER BY rfm_total DESC;
```

```
+-----------------+--------------+-----------+----------+---------+---------+---------+-----------+-----------------+
| customer_name   | recency_days | frequency | monetary | r_score | f_score | m_score | rfm_total | segment         |
+-----------------+--------------+-----------+----------+---------+---------+---------+-----------+-----------------+
| Alice Johnson   |          362 |         7 |  2389.92 |       4 |       4 |       4 |        12 | Champions       |
| Bob Smith       |          301 |         5 |  2119.95 |       4 |       4 |       4 |        12 | Champions       |
| Carol Williams  |          326 |         5 |  1349.94 |       4 |       4 |       3 |        11 | Champions       |
| David Brown     |          277 |         4 |  1059.96 |       4 |       3 |       3 |        10 | Loyal Customers |
| Eve Davis       |          390 |         4 |  1269.96 |       3 |       3 |       3 |         9 | Champions       |
| Jack Wilson     |          291 |         3 |  1249.97 |       4 |       2 |       3 |         9 | Loyal Customers |
| Frank Miller    |          343 |         3 |   939.97 |       3 |       2 |       2 |         7 | Loyal Customers |
| Grace Taylor    |          383 |         2 |   329.98 |       2 |       1 |       1 |         4 | At Risk         |
| Ivy Chen        |          311 |         2 |   189.98 |       3 |       1 |       1 |         5 | New Customers   |
| Henry Anderson  |          367 |         2 |   199.98 |       2 |       1 |       1 |         4 | At Risk         |
| Leo Martinez    |          397 |         1 |   149.99 |       1 |       1 |       1 |         3 | Lost            |
| Karen Lee       |          439 |         1 |   799.99 |       1 |       1 |       2 |         4 | Lost            |
| Mia Robinson    |          354 |         1 |   129.99 |       2 |       1 |       1 |         4 | Other           |
| Noah Clark      |          318 |         1 |    29.99 |       3 |       1 |       1 |         5 | New Customers   |
+-----------------+--------------+-----------+----------+---------+---------+---------+-----------+-----------------+
```

Let us break down the scoring:

- `NTILE(4) OVER (ORDER BY recency_days DESC)` -- Divides customers into 4 equal groups. The most recent buyers (fewest days) get a score of 4. We use `DESC` because low recency_days is better.
- `NTILE(4) OVER (ORDER BY frequency ASC)` -- Most frequent buyers get a 4.
- `NTILE(4) OVER (ORDER BY monetary ASC)` -- Highest spenders get a 4.

The `CASE` statement then assigns human-readable segments:

- **Champions**: Recent, frequent, high-spending. Your best customers.
- **Loyal Customers**: Regular buyers who come back often.
- **New Customers**: Recent but low frequency. Just getting started.
- **At Risk**: Used to buy but have not recently.
- **Losing Them**: Were once active but falling away.
- **Lost**: Have not bought in a long time and were infrequent.

This analysis tells you exactly where to focus your marketing efforts. Champions get reward programs. At-risk customers get re-engagement campaigns. Lost customers might get a "We miss you" email.

---

## Top N Products per Category

Finding the top-selling products within each category requires the `ROW_NUMBER` window function with `PARTITION BY`.

```sql
WITH product_sales AS (
    SELECT
        p.id                            AS product_id,
        p.name                          AS product_name,
        p.category,
        p.price,
        p.cost,
        SUM(oi.quantity)                AS total_sold,
        SUM(oi.subtotal)               AS total_revenue,
        SUM(oi.subtotal) - SUM(oi.quantity * p.cost)
                                        AS total_profit,
        ROW_NUMBER() OVER (
            PARTITION BY p.category
            ORDER BY SUM(oi.subtotal) DESC
        )                               AS rank_in_category
    FROM products p
    JOIN order_items oi ON oi.product_id = p.id
    JOIN orders o ON o.id = oi.order_id
    WHERE o.status = 'completed'
    GROUP BY p.id, p.name, p.category, p.price, p.cost
)
SELECT
    category,
    rank_in_category    AS rank,
    product_name,
    total_sold,
    total_revenue,
    ROUND(total_profit, 2) AS total_profit,
    ROUND(total_profit / NULLIF(total_revenue, 0) * 100, 1)
                        AS profit_margin_pct
FROM product_sales
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;
```

```
+-------------+------+---------------------+------------+---------------+--------------+------------------+
| category    | rank | product_name        | total_sold | total_revenue | total_profit | profit_margin_pct|
+-------------+------+---------------------+------------+---------------+--------------+------------------+
| Books       | 1    | Data Science Guide  |          4 |        199.96 |       139.96 |             70.0 |
| Books       | 2    | SQL Mastery Book    |          3 |        119.97 |        83.97 |             70.0 |
| Clothing    | 1    | Winter Jacket       |          3 |        599.97 |       344.97 |             57.5 |
| Electronics | 1    | ProBook Laptop      |          4 |       3999.96 |      1399.96 |             35.0 |
| Electronics | 2    | SmartPhone X        |          4 |       3199.96 |      1279.96 |             40.0 |
| Electronics | 3    | Wireless Earbuds    |          5 |        649.95 |       374.95 |             57.7 |
| Home        | 1    | Coffee Maker        |          4 |        599.96 |       319.96 |             53.3 |
| Home        | 2    | Blender Pro         |          2 |        159.98 |        99.98 |             62.5 |
| Sports      | 1    | Running Shoes       |          3 |        269.97 |       164.97 |             61.1 |
| Sports      | 2    | Yoga Mat            |          2 |         59.98 |        39.98 |             66.7 |
+-------------+------+---------------------+------------+---------------+--------------+------------------+
```

The key technique here:

- `ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(oi.subtotal) DESC)` -- This assigns rank 1, 2, 3... within each category based on total revenue.
- `WHERE rank_in_category <= 3` -- We filter to keep only the top 3 per category.

This is sometimes called a "Top N per group" query. It is one of the most common analytical patterns.

---

## Funnel Analysis

Funnel analysis tracks how users move through a conversion process. Each step narrows the funnel, and we want to know where people drop off.

```
               +----------------------------+
               |         Signup             |     100%
               |        (15 users)          |
               +-------------+--------------+
                             |
               +-------------v--------------+
               |         Browse             |     100%
               |        (15 users)          |
               +-------------+--------------+
                             |
               +-------------v--------------+
               |      Add to Cart           |     100%
               |        (15 users)          |
               +-------------+--------------+
                             |
               +-------------v--------------+
               |        Purchase            |     93%
               |        (14 users)          |
               +----------------------------+
```

### Building the Funnel Query

```sql
WITH funnel AS (
    SELECT
        customer_id,
        MAX(CASE WHEN event_type = 'signup'      THEN 1 ELSE 0 END) AS signed_up,
        MAX(CASE WHEN event_type = 'browse'      THEN 1 ELSE 0 END) AS browsed,
        MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS added_to_cart,
        MAX(CASE WHEN event_type = 'purchase'    THEN 1 ELSE 0 END) AS purchased
    FROM user_events
    GROUP BY customer_id
)
SELECT
    'Signup'        AS stage,
    SUM(signed_up)  AS users,
    ROUND(SUM(signed_up)::NUMERIC / SUM(signed_up) * 100, 1)
                    AS pct_of_total,
    100.0           AS conversion_rate
FROM funnel
UNION ALL
SELECT
    'Browse',
    SUM(browsed),
    ROUND(SUM(browsed)::NUMERIC / SUM(signed_up) * 100, 1),
    ROUND(SUM(browsed)::NUMERIC / SUM(signed_up) * 100, 1)
FROM funnel
UNION ALL
SELECT
    'Add to Cart',
    SUM(added_to_cart),
    ROUND(SUM(added_to_cart)::NUMERIC / SUM(signed_up) * 100, 1),
    ROUND(SUM(added_to_cart)::NUMERIC / SUM(browsed) * 100, 1)
FROM funnel
UNION ALL
SELECT
    'Purchase',
    SUM(purchased),
    ROUND(SUM(purchased)::NUMERIC / SUM(signed_up) * 100, 1),
    ROUND(SUM(purchased)::NUMERIC / SUM(added_to_cart) * 100, 1)
FROM funnel;
```

```
+--------------+-------+--------------+-----------------+
| stage        | users | pct_of_total | conversion_rate |
+--------------+-------+--------------+-----------------+
| Signup       |    15 |        100.0 |           100.0 |
| Browse       |    15 |        100.0 |           100.0 |
| Add to Cart  |    15 |        100.0 |           100.0 |
| Purchase     |    14 |         93.3 |            93.3 |
+--------------+-------+--------------+-----------------+
(4 rows)
```

The `conversion_rate` column shows the step-by-step conversion. The `pct_of_total` shows cumulative drop-off from the first step.

### Funnel with Time Analysis

How long does each step take?

```sql
WITH step_times AS (
    SELECT
        customer_id,
        MIN(CASE WHEN event_type = 'signup'      THEN event_date END) AS signup_time,
        MIN(CASE WHEN event_type = 'browse'      THEN event_date END) AS browse_time,
        MIN(CASE WHEN event_type = 'add_to_cart' THEN event_date END) AS cart_time,
        MIN(CASE WHEN event_type = 'purchase'    THEN event_date END) AS purchase_time
    FROM user_events
    GROUP BY customer_id
)
SELECT
    ROUND(AVG(EXTRACT(EPOCH FROM (browse_time - signup_time)) / 60), 0)
        AS avg_signup_to_browse_min,
    ROUND(AVG(EXTRACT(EPOCH FROM (cart_time - browse_time)) / 3600 / 24), 1)
        AS avg_browse_to_cart_days,
    ROUND(AVG(EXTRACT(EPOCH FROM (purchase_time - cart_time)) / 3600 / 24), 1)
        AS avg_cart_to_purchase_days,
    ROUND(AVG(EXTRACT(EPOCH FROM (purchase_time - signup_time)) / 3600 / 24), 1)
        AS avg_total_journey_days
FROM step_times
WHERE purchase_time IS NOT NULL;
```

```
+--------------------------+------------------------+---------------------------+------------------------+
| avg_signup_to_browse_min | avg_browse_to_cart_days | avg_cart_to_purchase_days  | avg_total_journey_days |
+--------------------------+------------------------+---------------------------+------------------------+
|                       17 |                   13.5 |                      14.8 |                   29.1 |
+--------------------------+------------------------+---------------------------+------------------------+
(1 row)
```

This tells us that on average:

- Users browse within 17 minutes of signing up.
- It takes about 13.5 days from browsing to adding something to the cart.
- It takes about 14.8 more days to go from cart to purchase.
- The total journey from signup to first purchase is about 29.1 days.

This information helps the marketing team decide when to send reminder emails and follow-up offers.

---

## Complete Dashboard Queries

Here is a set of queries you might use to power an executive dashboard.

### Dashboard Query 1: Revenue Overview

```sql
WITH current_period AS (
    SELECT
        SUM(total_amount)                        AS current_month_revenue,
        COUNT(DISTINCT id)                       AS current_month_orders,
        COUNT(DISTINCT customer_id)              AS current_month_customers
    FROM orders
    WHERE status = 'completed'
      AND DATE_TRUNC('month', order_date) = DATE_TRUNC('month', CURRENT_DATE)
),
prior_period AS (
    SELECT
        SUM(total_amount)                        AS prior_month_revenue,
        COUNT(DISTINCT id)                       AS prior_month_orders,
        COUNT(DISTINCT customer_id)              AS prior_month_customers
    FROM orders
    WHERE status = 'completed'
      AND DATE_TRUNC('month', order_date) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
)
SELECT
    COALESCE(cp.current_month_revenue, 0)       AS this_month_revenue,
    COALESCE(pp.prior_month_revenue, 0)         AS last_month_revenue,
    CASE
        WHEN pp.prior_month_revenue > 0
        THEN ROUND((cp.current_month_revenue - pp.prior_month_revenue)
             / pp.prior_month_revenue * 100, 1)
        ELSE NULL
    END                                          AS revenue_change_pct,
    COALESCE(cp.current_month_orders, 0)        AS this_month_orders,
    COALESCE(cp.current_month_customers, 0)     AS this_month_customers
FROM current_period cp
CROSS JOIN prior_period pp;
```

### Dashboard Query 2: Revenue by Region

```sql
SELECT
    c.region,
    COUNT(DISTINCT o.id)                AS order_count,
    COUNT(DISTINCT o.customer_id)       AS customer_count,
    SUM(o.total_amount)                 AS total_revenue,
    ROUND(AVG(o.total_amount), 2)       AS avg_order_value,
    ROUND(SUM(o.total_amount) / SUM(SUM(o.total_amount)) OVER () * 100, 1)
                                        AS revenue_share_pct
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.region
ORDER BY total_revenue DESC;
```

```
+----------+-------------+----------------+---------------+-----------------+-------------------+
| region   | order_count | customer_count | total_revenue | avg_order_value | revenue_share_pct |
+----------+-------------+----------------+---------------+-----------------+-------------------+
| West     |          17 |              5 |       5349.83 |          314.70 |              39.5 |
| East     |          13 |              4 |       4419.87 |          339.99 |              32.7 |
| Central  |          11 |              4 |       3769.90 |          342.72 |              27.8 |
+----------+-------------+----------------+---------------+-----------------+-------------------+
(3 rows)
```

The clever part is `SUM(o.total_amount) / SUM(SUM(o.total_amount)) OVER ()`. The inner `SUM` groups by region. The outer `SUM ... OVER ()` with an empty window calculates the grand total. Dividing gives us each region's share.

### Dashboard Query 3: Customer Acquisition Trend

```sql
SELECT
    TO_CHAR(signup_date, 'YYYY-MM')     AS month,
    COUNT(*)                             AS new_customers,
    SUM(COUNT(*)) OVER (
        ORDER BY TO_CHAR(signup_date, 'YYYY-MM')
    )                                    AS cumulative_customers
FROM customers
GROUP BY TO_CHAR(signup_date, 'YYYY-MM')
ORDER BY month;
```

```
+---------+----------------+-----------------------+
| month   | new_customers  | cumulative_customers  |
+---------+----------------+-----------------------+
| 2023-01 |              1 |                     1 |
| 2023-02 |              1 |                     2 |
| 2023-03 |              1 |                     3 |
| 2023-04 |              1 |                     4 |
| 2023-05 |              1 |                     5 |
| 2023-06 |              1 |                     6 |
| 2023-07 |              1 |                     7 |
| 2023-08 |              1 |                     8 |
| 2023-09 |              1 |                     9 |
| 2023-10 |              1 |                    10 |
| 2024-01 |              1 |                    11 |
| 2024-02 |              1 |                    12 |
| 2024-03 |              1 |                    13 |
| 2024-04 |              1 |                    14 |
| 2024-05 |              1 |                    15 |
+---------+----------------+-----------------------+
(15 rows)
```

### Dashboard Query 4: Product Category Performance

```sql
SELECT
    p.category,
    COUNT(DISTINCT oi.order_id)         AS orders,
    SUM(oi.quantity)                     AS units_sold,
    SUM(oi.subtotal)                    AS revenue,
    SUM(oi.subtotal - (oi.quantity * p.cost))
                                        AS gross_profit,
    ROUND(
        SUM(oi.subtotal - (oi.quantity * p.cost))
        / NULLIF(SUM(oi.subtotal), 0) * 100,
        1
    )                                    AS margin_pct
FROM products p
JOIN order_items oi ON oi.product_id = p.id
JOIN orders o ON o.id = oi.order_id
WHERE o.status = 'completed'
GROUP BY p.category
ORDER BY revenue DESC;
```

```
+-------------+--------+------------+----------+--------------+------------+
| category    | orders | units_sold | revenue  | gross_profit | margin_pct |
+-------------+--------+------------+----------+--------------+------------+
| Electronics |     13 |         13 | 7849.87  |     3054.87  |       38.9 |
| Home        |      6 |          6 |  759.94  |      419.94  |       55.3 |
| Clothing    |      3 |          3 |  599.97  |      344.97  |       57.5 |
| Sports      |      5 |          5 |  329.95  |      204.95  |       62.1 |
| Books       |      7 |          7 |  319.93  |      223.93  |       70.0 |
+-------------+--------+------------+----------+--------------+------------+
(5 rows)
```

Notice that Electronics generates the most revenue but has the lowest margin (38.9%), while Books has the highest margin (70.0%) but the least revenue. This is a common business insight: high-ticket items often have lower margins.

---

## Common Mistakes

1. **Forgetting to handle NULL in LAG/LEAD.** When there is no prior row, `LAG` returns NULL. Always wrap growth calculations in a `CASE` or `COALESCE` to avoid dividing by NULL.

2. **Using the wrong date function.** `DATE_TRUNC('month', date)` rounds down to the first of the month. `EXTRACT(MONTH FROM date)` gives just the month number. Know which one you need.

3. **Not filtering cancelled orders.** Analytics should typically exclude cancelled orders. Always include `WHERE status = 'completed'` (or your equivalent) to avoid inflating numbers.

4. **Confusing ROW_NUMBER, RANK, and DENSE_RANK.** `ROW_NUMBER` always gives unique numbers. `RANK` skips numbers for ties. `DENSE_RANK` does not skip. For "Top N" queries, `ROW_NUMBER` is usually what you want.

5. **Mixing aggregation levels.** Be careful when joining tables at different granularities. Joining orders with order_items before aggregating can multiply your counts. Use CTEs to aggregate first, then join.

---

## Best Practices

1. **Use CTEs for readability.** Break complex analytics queries into named steps with `WITH`. Each CTE should do one thing. This makes queries easier to understand, debug, and modify.

2. **Always use DATE_TRUNC for time-based grouping.** It handles all the edge cases (different month lengths, leap years, etc.) correctly.

3. **Name your columns clearly.** Use aliases like `monthly_revenue` instead of `sum`. Dashboard tools and downstream users need to understand what each column represents.

4. **Test with known data.** Before running analytics on production data, test your queries on a small dataset where you can manually verify the results.

5. **Consider materialized views for heavy queries.** If a dashboard query scans millions of rows and runs frequently, create a materialized view that refreshes on a schedule.

6. **Document your business rules.** "Revenue" can mean gross, net, or adjusted. Make sure everyone agrees on definitions before writing queries.

---

## Quick Summary

You built a complete analytics toolkit:

- **Time-based aggregation** with `DATE_TRUNC` and `GROUP BY` for daily, weekly, and monthly revenue.
- **Year-over-year growth** using the `LAG` window function to compare months across years.
- **Running totals** with `SUM() OVER (ORDER BY ...)` for cumulative metrics.
- **Moving averages** with `AVG() OVER (ROWS BETWEEN ... AND ...)` for trend analysis.
- **Cohort analysis** to track customer retention over time.
- **RFM segmentation** using `NTILE` to classify customers.
- **Top N per group** with `ROW_NUMBER` and `PARTITION BY`.
- **Funnel analysis** to measure conversion rates at each step.
- **Dashboard queries** combining all techniques for real-time business intelligence.

---

## Key Points

- `DATE_TRUNC` is the essential function for grouping data by time periods.
- `LAG` and `LEAD` window functions compare rows to previous or next rows.
- Running totals use `SUM() OVER (ORDER BY ...)` without a frame clause.
- Moving averages use `AVG() OVER (ROWS BETWEEN N PRECEDING AND CURRENT ROW)`.
- Cohort analysis identifies when customers first appeared and tracks them over time.
- RFM analysis uses `NTILE` to score customers on Recency, Frequency, and Monetary value.
- `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` is the standard pattern for Top N per group.
- Funnel analysis uses `CASE` expressions to flag whether each user reached each stage.
- Always exclude cancelled or invalid orders from analytics calculations.

---

## Practice Questions

1. How would you modify the YoY growth query to show quarter-over-quarter growth instead of month-over-month? What changes are needed?

2. In the RFM analysis, why do we use `NTILE(4)` instead of manually setting score thresholds? What are the advantages and disadvantages of each approach?

3. The funnel analysis shows a 93.3% conversion from "Add to Cart" to "Purchase." What query would you write to find the specific customers who dropped off at the cart stage?

4. How is a running total different from a moving average? When would you use each one?

5. In the cohort retention table, what does a 0% value in month 3 mean? Is this necessarily bad? What additional data might help explain it?

---

## Exercises

### Exercise 1: Revenue Forecast

Using the monthly revenue data, write a query that:

1. Calculates the average monthly growth rate over the last 6 months.
2. Projects the next 3 months of revenue using that growth rate.
3. Shows both actual and projected values in the same result set.

Hint: Use a CTE for the historical data and a `generate_series` for future months.

### Exercise 2: Customer Lifetime Value

Write a query that calculates the Customer Lifetime Value (CLV) for each customer:

1. Calculate their average order value.
2. Calculate their average time between orders (in days).
3. Calculate their estimated yearly order frequency.
4. Estimate CLV as: `avg_order_value * estimated_yearly_orders * avg_customer_lifespan_years` (assume 3-year lifespan).
5. Rank customers by CLV and identify the top 5.

### Exercise 3: Build a Complete Dashboard

Create a single query (or set of queries) that produces a complete monthly business report including:

1. Total revenue, order count, and unique customers.
2. New vs. returning customer breakdown.
3. Top 3 products by revenue.
4. Revenue by region with percentage share.
5. Comparison to the previous month (with percentage change).

---

## Congratulations!

You have reached the end of the practical chapters in this book. Take a moment to appreciate how far you have come.

You started with the basics: what a database is, how to create tables, and how to write your first SELECT query. Along the way you learned joins, subqueries, window functions, normalization, indexes, triggers, transactions, and security. Then you put it all together by building a complete e-commerce database and writing the analytical queries that power real business decisions.

These are not theoretical skills. They are the same techniques used by data analysts at every major company, by backend developers building applications, and by data engineers designing data pipelines. You now have a solid foundation in SQL and database design.

### What to Learn Next

Your SQL journey does not end here. Here are paths to explore:

- **Advanced PostgreSQL features**: Partitioning, materialized views, JSONB operations, full-text search, and PostGIS for geospatial data.
- **Database administration**: Replication, high availability, connection pooling with PgBouncer, and monitoring with pg_stat_statements.
- **Data warehousing**: Star schemas, fact and dimension tables, slowly changing dimensions, and ETL pipelines.
- **Other databases**: MySQL, SQLite, Microsoft SQL Server, and cloud databases like Amazon RDS and Google Cloud SQL.
- **NoSQL databases**: MongoDB, Redis, Cassandra, and understanding when to use them instead of (or alongside) relational databases.
- **ORMs and frameworks**: SQLAlchemy (Python), Prisma (JavaScript), ActiveRecord (Ruby), and how they generate SQL under the hood.
- **Data tools**: dbt for data transformation, Apache Airflow for orchestration, and Metabase or Grafana for visualization.

Whatever path you choose, remember: SQL has been around since the 1970s and is not going anywhere. The skills you have built in this book will serve you for your entire career.

Good luck, and happy querying.
