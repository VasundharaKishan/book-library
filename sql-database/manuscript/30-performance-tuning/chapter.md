# Chapter 30: Performance Tuning — Making Queries Fast

## What You Will Learn

In this chapter, you will learn:

- How to use EXPLAIN ANALYZE to understand query plans
- How to read query plan nodes (Seq Scan, Index Scan, Hash Join, etc.)
- How to identify slow queries with pg_stat_statements
- When and how to create indexes for maximum impact
- How to rewrite queries for better performance
- What connection pooling is and why PgBouncer matters
- How VACUUM and ANALYZE keep your database healthy
- What table partitioning is and when to use it
- How to optimize real slow queries step by step

## Why This Chapter Matters

Imagine you own a library with a million books. A customer asks for a specific book. Without any organization, you would have to walk through every shelf and check every book one by one. That could take hours. But with a card catalog (an index), you look up the book's location in seconds and walk straight to it.

Database performance works the same way. A query that takes 5 seconds on a small development database might take 5 minutes on a production database with millions of rows. The difference between a fast application and a frustratingly slow one often comes down to how well your queries and indexes are designed.

Performance tuning is not about premature optimization — it is about knowing how to diagnose problems when they arise and having the tools to fix them. This chapter gives you those tools.

---

## Setting Up Our Practice Tables

We need a reasonably large dataset to see meaningful performance differences:

```sql
-- Create a large orders table
CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INT NOT NULL,
    product_id   INT NOT NULL,
    order_date   DATE NOT NULL,
    amount       DECIMAL(10, 2) NOT NULL,
    status       VARCHAR(20) NOT NULL,
    shipping_city VARCHAR(100)
);

-- Insert 100,000 rows of sample data
INSERT INTO orders (customer_id, product_id, order_date, amount,
                    status, shipping_city)
SELECT
    (random() * 999 + 1)::INT,
    (random() * 49 + 1)::INT,
    DATE '2022-01-01' + (random() * 730)::INT,
    (random() * 500 + 10)::DECIMAL(10,2),
    CASE (random() * 3)::INT
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'shipped'
        WHEN 2 THEN 'delivered'
        ELSE 'cancelled'
    END,
    CASE (random() * 5)::INT
        WHEN 0 THEN 'New York'
        WHEN 1 THEN 'Los Angeles'
        WHEN 2 THEN 'Chicago'
        WHEN 3 THEN 'Houston'
        WHEN 4 THEN 'Phoenix'
        ELSE 'Seattle'
    END
FROM generate_series(1, 100000);

CREATE TABLE customers (
    customer_id  SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(150) NOT NULL,
    city         VARCHAR(100),
    created_at   DATE NOT NULL DEFAULT CURRENT_DATE
);

INSERT INTO customers (name, email, city)
SELECT
    'Customer ' || i,
    'customer' || i || '@example.com',
    CASE (random() * 5)::INT
        WHEN 0 THEN 'New York'
        WHEN 1 THEN 'Los Angeles'
        WHEN 2 THEN 'Chicago'
        WHEN 3 THEN 'Houston'
        WHEN 4 THEN 'Phoenix'
        ELSE 'Seattle'
    END
FROM generate_series(1, 1000) AS i;

-- Run ANALYZE so PostgreSQL has accurate statistics
ANALYZE orders;
ANALYZE customers;
```

---

## EXPLAIN ANALYZE — Your Diagnostic Tool

EXPLAIN ANALYZE is the single most important tool for performance tuning. It shows you exactly what PostgreSQL does to execute your query, how long each step takes, and how many rows it processes.

### Basic Usage

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42;
```

```
                                                  QUERY PLAN
--------------------------------------------------------------------------------------------------------------
 Seq Scan on orders  (cost=0.00..2137.00 rows=98 width=52) (actual time=0.025..12.345 loops=1)
   Filter: (customer_id = 42)
   Rows Removed by Filter: 99902
 Planning Time: 0.085 ms
 Execution Time: 12.432 ms
(5 rows)
```

### Reading the Query Plan

Let us break down every piece of that output:

```
Seq Scan on orders
     ^         ^
     |         |
     |         +-- Which table
     +-- The method used (Sequential Scan = read every row)

(cost=0.00..2137.00 rows=98 width=52)
       ^        ^      ^       ^
       |        |      |       +-- Average row size in bytes
       |        |      +-- Estimated number of rows returned
       |        +-- Estimated total cost
       +-- Estimated startup cost

(actual time=0.025..12.345 loops=1)
              ^        ^       ^
              |        |       +-- Number of times this step ran
              |        +-- Actual total time in milliseconds
              +-- Actual time to return first row

Filter: (customer_id = 42)
   +-- The condition being applied

Rows Removed by Filter: 99902
   +-- Rows that were read but did not match
```

```
What a Seq Scan looks like:

+---------------------------------------------------+
| orders table (100,000 rows)                       |
| [x] [x] [x] [x] [x] [x] [x] [x] [x] [x] ...   |
|  ^                                                |
|  Read EVERY row, check if customer_id = 42        |
|  Keep matches, discard the rest                   |
+---------------------------------------------------+

99,902 rows read and discarded
98 rows matched and returned

This is slow! We read 100,000 rows to find 98.
```

### EXPLAIN vs EXPLAIN ANALYZE

```
+------------------+-------------------------------------------+
| Command          | What It Shows                             |
+------------------+-------------------------------------------+
| EXPLAIN          | Estimated plan only (does not run query)  |
| EXPLAIN ANALYZE  | Estimated plan + actual execution times   |
|                  | (runs the query!)                         |
+------------------+-------------------------------------------+
```

**Warning**: EXPLAIN ANALYZE actually executes the query. For INSERT, UPDATE, or DELETE, wrap it in a transaction and roll back:

```sql
BEGIN;
EXPLAIN ANALYZE DELETE FROM orders WHERE status = 'cancelled';
ROLLBACK;  -- Undo the delete!
```

---

## Scan Types — How PostgreSQL Reads Data

### Sequential Scan (Seq Scan)

Reads every row in the table. Like reading every page of a book to find one paragraph.

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE amount > 400;
```

```
 Seq Scan on orders  (cost=0.00..2387.00 rows=20105 width=52)
                      (actual time=0.015..15.234 loops=1)
   Filter: (amount > 400.00)
```

A Seq Scan is not always bad. If you need most of the rows, scanning the whole table is actually faster than using an index.

### Index Scan

Uses an index to go directly to the matching rows. Like using a book's index to jump to the right page.

```sql
-- First, create an index
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Now try the same query
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42;
```

```
 Index Scan using idx_orders_customer_id on orders
   (cost=0.29..38.50 rows=98 width=52) (actual time=0.030..0.245 loops=1)
   Index Cond: (customer_id = 42)
```

```
What an Index Scan looks like:

Index: idx_orders_customer_id
+----------------------------------+
| 1 -> row 523, row 8821          |
| 2 -> row 102, row 3344, ...     |
| ...                              |
| 42 -> row 55, row 1203, ...     |  <-- Jump directly here!
| ...                              |
+----------------------------------+
          |
          v
+---------------------------------------------------+
| orders table                                      |
| [...] [...] [row 55] [...] [...] [row 1203] [...] |
|              ^                    ^                |
|              Fetch only matching rows              |
+---------------------------------------------------+

Only 98 rows read (vs 100,000 with Seq Scan)
```

The query went from 12.4ms to 0.25ms — about 50 times faster.

### Index Only Scan

Even faster than an Index Scan. If all the columns you need are in the index, PostgreSQL does not even need to look at the table.

```sql
-- Create a covering index
CREATE INDEX idx_orders_customer_amount
ON orders(customer_id, amount);

EXPLAIN ANALYZE
SELECT customer_id, amount FROM orders WHERE customer_id = 42;
```

```
 Index Only Scan using idx_orders_customer_amount on orders
   (cost=0.29..4.50 rows=98 width=10) (actual time=0.025..0.089 loops=1)
   Index Cond: (customer_id = 42)
   Heap Fetches: 0
```

`Heap Fetches: 0` means PostgreSQL got everything from the index without touching the table at all.

### Bitmap Index Scan

A middle ground between Seq Scan and Index Scan. PostgreSQL first scans the index to build a bitmap of matching pages, then reads those pages from the table.

```sql
CREATE INDEX idx_orders_status ON orders(status);

EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending';
```

```
 Bitmap Heap Scan on orders  (cost=289.25..1534.50 rows=25000 width=52)
   Recheck Cond: (status = 'pending'::text)
   ->  Bitmap Index Scan on idx_orders_status
       (cost=0.00..283.00 rows=25000 width=0)
       Index Cond: (status = 'pending'::text)
```

PostgreSQL chose a Bitmap scan because about 25% of rows match — too many for an Index Scan to be efficient, but not enough to justify a full Seq Scan.

---

## Join Types — How PostgreSQL Combines Tables

### Nested Loop Join

For each row in the outer table, scan the inner table. Fast when the outer table is small and the inner table has an index.

```sql
EXPLAIN ANALYZE
SELECT c.name, o.order_date, o.amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id = 42;
```

```
 Nested Loop  (cost=0.58..42.85 rows=98 width=30)
              (actual time=0.045..0.312 loops=1)
   ->  Index Scan using customers_pkey on customers c
       (cost=0.28..8.30 rows=1 width=18)
       Index Cond: (customer_id = 42)
   ->  Index Scan using idx_orders_customer_id on orders o
       (cost=0.29..34.05 rows=98 width=16)
       Index Cond: (customer_id = 42)
```

```
Nested Loop:

customers (1 row: customer_id = 42)
    |
    +---> For this 1 customer, find all matching orders
          using the index on orders.customer_id
          (98 matches)

Result: 98 rows
```

### Hash Join

Builds a hash table from the smaller table, then probes it with rows from the larger table. Good for joining large tables.

```sql
EXPLAIN ANALYZE
SELECT c.name, o.order_date, o.amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date = '2023-06-15';
```

```
 Hash Join  (cost=28.50..2285.15 rows=137 width=30)
            (actual time=0.425..18.234 loops=1)
   Hash Cond: (o.customer_id = c.customer_id)
   ->  Seq Scan on orders o  (cost=0.00..2137.00 rows=137 width=16)
       Filter: (order_date = '2023-06-15')
   ->  Hash  (cost=16.00..16.00 rows=1000 width=18)
       ->  Seq Scan on customers c  (cost=0.00..16.00 rows=1000 width=18)
```

```
Hash Join:

Step 1: Build hash table from customers (smaller table)
+----------------------------------+
| Hash Table                       |
| customer_id 1 -> "Customer 1"   |
| customer_id 2 -> "Customer 2"   |
| ...                              |
+----------------------------------+

Step 2: Scan orders, look up each customer_id in hash table
+----------------------------------+
| orders row (customer_id=42)      |
|   -> Look up 42 in hash table   |
|   -> Found! Join them.          |
+----------------------------------+
```

### Merge Join

Both tables are sorted on the join column, then PostgreSQL walks through them simultaneously. Efficient when both tables are large and sorted.

```sql
-- PostgreSQL may choose Merge Join when both sides are large and sorted
-- You can hint at it by ensuring indexes exist on both join columns
```

```
Merge Join:

Sorted customers:     Sorted orders:
[1] [2] [3] ...       [1] [1] [2] [3] [3] ...
 ^                     ^
 |                     |
 Walk through both lists simultaneously
 Match when values are equal
```

### Comparison

```
+-------------+------------------+----------------------------------+
| Join Type   | Best When        | How It Works                     |
+-------------+------------------+----------------------------------+
| Nested Loop | Small outer,     | For each outer row, search inner |
|             | indexed inner    |                                  |
+-------------+------------------+----------------------------------+
| Hash Join   | Medium/large     | Build hash table from smaller    |
|             | tables, no index | table, probe with larger         |
+-------------+------------------+----------------------------------+
| Merge Join  | Both tables      | Walk through both sorted lists   |
|             | sorted on key    | simultaneously                   |
+-------------+------------------+----------------------------------+
```

---

## Identifying Slow Queries with pg_stat_statements

The pg_stat_statements extension tracks execution statistics for all queries. It is the best way to find which queries are actually slow in production.

### Enabling pg_stat_statements

```sql
-- Add to postgresql.conf:
-- shared_preload_libraries = 'pg_stat_statements'
-- Then restart PostgreSQL and run:
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

### Finding Your Slowest Queries

```sql
SELECT
    calls,
    ROUND(total_exec_time::NUMERIC, 2) AS total_ms,
    ROUND(mean_exec_time::NUMERIC, 2) AS avg_ms,
    ROUND((100 * total_exec_time /
           SUM(total_exec_time) OVER ())::NUMERIC, 2) AS pct_time,
    query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

```
 calls  | total_ms  | avg_ms  | pct_time |              query
--------+-----------+---------+----------+---------------------------------
  15234 | 45230.50  |   2.97  |    32.15 | SELECT * FROM orders WHERE ...
   8901 | 28103.20  |   3.16  |    19.97 | SELECT c.name, o.* FROM ...
   3456 | 15890.00  |   4.60  |    11.29 | UPDATE orders SET status = ...
    ...
```

This tells you:
- Which queries run most often (calls)
- Which queries take the most total time (total_ms)
- Which queries are slowest per execution (avg_ms)
- What percentage of total database time each query uses (pct_time)

### Reset Statistics

```sql
SELECT pg_stat_statements_reset();
```

---

## Index Strategies

### When to Create an Index

```
+------------------------------------------+-------------------+
| Scenario                                 | Create Index?     |
+------------------------------------------+-------------------+
| Column used in WHERE frequently          | Yes               |
| Column used in JOIN conditions           | Yes               |
| Column used in ORDER BY                  | Often yes         |
| Column with high cardinality (many       | Yes               |
|   unique values, like customer_id)       |                   |
| Column with low cardinality (few unique  | Usually no        |
|   values, like status with 4 values)     |                   |
| Small table (< 1000 rows)               | Usually no        |
| Column rarely used in queries            | No                |
| Table with heavy INSERT/UPDATE           | Be selective      |
+------------------------------------------+-------------------+
```

### Composite Indexes

When queries filter on multiple columns, a composite index can help:

```sql
-- Query that filters on two columns
SELECT * FROM orders
WHERE customer_id = 42 AND status = 'shipped';

-- Composite index for this query
CREATE INDEX idx_orders_customer_status
ON orders(customer_id, status);
```

**Column order matters!** Put the most selective column first (the one that filters out the most rows).

```
Composite Index (customer_id, status):

customer_id = 42:
  status = 'pending'   -> [row 55, row 1203]
  status = 'shipped'   -> [row 892, row 3401]   <-- finds these directly
  status = 'delivered' -> [row 2100]

The index works for:
  WHERE customer_id = 42                    -- YES (uses first column)
  WHERE customer_id = 42 AND status = 'x'  -- YES (uses both columns)
  WHERE status = 'shipped'                  -- NO  (cannot skip first column)
```

### Partial Indexes

Index only the rows that matter:

```sql
-- If you mostly query pending orders:
CREATE INDEX idx_orders_pending
ON orders(customer_id, order_date)
WHERE status = 'pending';
```

This index is smaller and faster because it only includes pending orders.

### Expression Indexes

Index the result of an expression:

```sql
-- If you often search by lowercase email:
CREATE INDEX idx_customers_email_lower
ON customers(LOWER(email));

-- Now this query uses the index:
SELECT * FROM customers WHERE LOWER(email) = 'customer42@example.com';
```

### Checking Index Usage

```sql
SELECT
    indexrelname AS index_name,
    idx_scan AS times_used,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

```
         index_name          | times_used | index_size
-----------------------------+------------+-----------
 orders_pkey                 |      15234 | 2208 kB
 idx_orders_customer_id      |       8901 | 2208 kB
 idx_orders_status           |       3456 | 2208 kB
 idx_orders_customer_status  |        234 | 2208 kB
 idx_orders_pending          |         12 | 560 kB
(5 rows)
```

If an index has `times_used = 0`, it is wasting disk space and slowing down writes. Consider dropping it.

---

## Query Rewriting Tips

### Tip 1: Avoid SELECT *

```sql
-- BAD: Fetches all columns, even ones you do not need
SELECT * FROM orders WHERE customer_id = 42;

-- GOOD: Fetch only what you need
SELECT order_id, order_date, amount FROM orders WHERE customer_id = 42;
```

Fetching fewer columns means less data to read from disk, less data to send over the network, and potentially allows Index Only Scans.

### Tip 2: Use EXISTS Instead of IN for Subqueries

```sql
-- SLOWER: IN with subquery
SELECT * FROM customers c
WHERE c.customer_id IN (
    SELECT customer_id FROM orders WHERE amount > 400
);

-- FASTER: EXISTS stops at the first match
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.customer_id
    AND o.amount > 400
);
```

IN must collect all matching customer_ids first. EXISTS can stop as soon as it finds one match for each customer.

### Tip 3: Minimize Subqueries in SELECT

```sql
-- BAD: Subquery runs once per row in the outer query
SELECT
    c.name,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) AS order_count,
    (SELECT SUM(amount) FROM orders o WHERE o.customer_id = c.customer_id) AS total_spent
FROM customers c;

-- GOOD: Use a JOIN with aggregation
SELECT
    c.name,
    COUNT(o.order_id) AS order_count,
    COALESCE(SUM(o.amount), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;
```

### Tip 4: Use LIMIT for Pagination

```sql
-- BAD: Fetch everything, then paginate in the application
SELECT * FROM orders ORDER BY order_date DESC;

-- GOOD: Fetch only the page you need
SELECT * FROM orders ORDER BY order_date DESC
LIMIT 20 OFFSET 0;  -- Page 1

SELECT * FROM orders ORDER BY order_date DESC
LIMIT 20 OFFSET 20;  -- Page 2
```

### Tip 5: Avoid Functions on Indexed Columns in WHERE

```sql
-- BAD: The function prevents index usage
SELECT * FROM orders
WHERE EXTRACT(YEAR FROM order_date) = 2023;

-- GOOD: Rewrite to use the column directly
SELECT * FROM orders
WHERE order_date >= '2023-01-01'
  AND order_date < '2024-01-01';
```

The first query applies a function to every row's order_date, so the index cannot be used. The second query compares the column directly, which allows index usage.

---

## Connection Pooling with PgBouncer

Every database connection consumes memory (about 5-10 MB in PostgreSQL). If your application opens 200 connections, that is 1-2 GB just for connections. Connection pooling solves this.

```
Without Pooling:                    With PgBouncer:

App Server (200 threads)            App Server (200 threads)
    |  |  |  |  |  |                    |  |  |  |  |  |
    |  |  |  |  |  |                    v  v  v  v  v  v
    v  v  v  v  v  v               +------------------+
+---------------------+           | PgBouncer         |
| PostgreSQL          |           | (connection pool) |
| 200 connections     |           | 200 app conns ->  |
| (1-2 GB memory!)   |           |  20 DB conns      |
+---------------------+           +------------------+
                                        |  |
                                        v  v
                                  +------------------+
                                  | PostgreSQL       |
                                  | 20 connections   |
                                  | (100-200 MB)     |
                                  +------------------+
```

PgBouncer sits between your application and PostgreSQL. It maintains a small pool of database connections and shares them among many application connections.

### PgBouncer Modes

```
+-------------------+----------------------------------------------+
| Mode              | How It Works                                 |
+-------------------+----------------------------------------------+
| Session pooling   | Connection assigned for entire session       |
|                   | Safest, least efficient                      |
+-------------------+----------------------------------------------+
| Transaction       | Connection assigned per transaction          |
| pooling           | Best balance of safety and efficiency        |
+-------------------+----------------------------------------------+
| Statement pooling | Connection assigned per statement            |
|                   | Most efficient, but no multi-statement       |
|                   | transactions                                 |
+-------------------+----------------------------------------------+
```

Transaction pooling is the most commonly used mode. It gives each transaction a dedicated connection, then returns the connection to the pool when the transaction completes.

---

## VACUUM and ANALYZE

### Why VACUUM?

When you UPDATE or DELETE a row in PostgreSQL, the old version of the row is not immediately removed. It is marked as "dead" but still takes up space. VACUUM reclaims that space.

```
Before VACUUM:
+------+------+------+------+------+------+------+
| Live | Dead | Live | Dead | Dead | Live | Dead |
+------+------+------+------+------+------+------+

After VACUUM:
+------+------+------+------+
| Live | Live | Live | Free |
+------+------+------+------+

Space from dead rows is now available for reuse.
```

### Running VACUUM

```sql
-- VACUUM a specific table
VACUUM orders;

-- VACUUM with verbose output
VACUUM VERBOSE orders;

-- VACUUM FULL — reclaims space and compacts the table
-- WARNING: Locks the table! Use during maintenance windows.
VACUUM FULL orders;
```

### Autovacuum

PostgreSQL runs VACUUM automatically in the background. You can check its activity:

```sql
SELECT
    relname AS table_name,
    n_dead_tup AS dead_rows,
    n_live_tup AS live_rows,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY n_dead_tup DESC;
```

```
 table_name | dead_rows | live_rows |     last_autovacuum
------------+-----------+-----------+------------------------
 orders     |      1523 |    100000 | 2024-01-15 03:00:00
 customers  |        45 |      1000 | 2024-01-15 03:00:00
(2 rows)
```

### Why ANALYZE?

ANALYZE collects statistics about the distribution of data in your tables. PostgreSQL uses these statistics to decide the best query plan.

```sql
-- Analyze a specific table
ANALYZE orders;

-- Analyze all tables in the database
ANALYZE;
```

**When to run ANALYZE:**
- After loading a large amount of data
- After major UPDATE or DELETE operations
- When query plans suddenly change for the worse

```
Without ANALYZE:                    With ANALYZE:
PostgreSQL guesses:                 PostgreSQL knows:
"status has ~4 unique values"       "status has 4 values:
                                     pending=25%, shipped=25%,
                                     delivered=25%, cancelled=25%"

Bad guess -> Bad query plan          Accurate stats -> Good query plan
```

---

## Table Partitioning Basics

Partitioning splits a large table into smaller physical pieces (partitions) while treating them as one logical table. Queries that filter on the partition key only scan the relevant partition.

```
Single large table:                 Partitioned table:
+---------------------------+       +----------+----------+----------+
| orders (10 million rows)  |       | orders   | orders   | orders   |
| ALL data scanned          |       | 2022     | 2023     | 2024     |
+---------------------------+       | 3M rows  | 4M rows  | 3M rows  |
                                    +----------+----------+----------+
                                         ^
                                         |
                                    Query for 2023?
                                    Only scan this partition!
```

### Creating a Partitioned Table

```sql
-- Create the parent table
CREATE TABLE orders_partitioned (
    order_id     SERIAL,
    customer_id  INT NOT NULL,
    order_date   DATE NOT NULL,
    amount       DECIMAL(10, 2) NOT NULL,
    status       VARCHAR(20) NOT NULL
) PARTITION BY RANGE (order_date);

-- Create partitions for each year
CREATE TABLE orders_2022 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');

CREATE TABLE orders_2023 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### How Partition Pruning Works

```sql
EXPLAIN ANALYZE
SELECT * FROM orders_partitioned
WHERE order_date = '2023-06-15';
```

```
 Append  (cost=0.00..15.00 rows=1 width=44)
   ->  Seq Scan on orders_2023 orders_partitioned_1
       (cost=0.00..15.00 rows=1 width=44)
       Filter: (order_date = '2023-06-15')
```

PostgreSQL only scanned the 2023 partition. The 2022 and 2024 partitions were completely skipped (pruned).

### When to Use Partitioning

- Tables with millions of rows
- Queries that consistently filter on a date or category column
- When you need to efficiently drop old data (drop the partition instead of DELETE)
- When maintenance operations (VACUUM, REINDEX) need to work on smaller chunks

---

## Practical: Optimizing 5 Slow Queries

### Slow Query 1: Missing Index

```sql
-- BEFORE: Full table scan
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';
```

```
 Seq Scan on orders  (cost=0.00..2637.00 rows=25 width=52)
                      (actual time=0.045..14.567 loops=1)
   Filter: ((customer_id = 42) AND (status = 'shipped'))
   Rows Removed by Filter: 99975
 Execution Time: 14.623 ms
```

**Diagnosis**: Sequential scan reading 100,000 rows to find 25.

**Fix**: Create a composite index.

```sql
CREATE INDEX idx_orders_cust_status ON orders(customer_id, status);

-- AFTER:
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42 AND status = 'shipped';
```

```
 Index Scan using idx_orders_cust_status on orders
   (cost=0.42..28.50 rows=25 width=52) (actual time=0.025..0.098 loops=1)
   Index Cond: ((customer_id = 42) AND (status = 'shipped'))
 Execution Time: 0.132 ms
```

**Result**: 14.6ms down to 0.13ms — 112 times faster.

---

### Slow Query 2: Function on Indexed Column

```sql
-- BEFORE: Function prevents index usage
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE EXTRACT(YEAR FROM order_date) = 2023
  AND EXTRACT(MONTH FROM order_date) = 6;
```

```
 Seq Scan on orders  (cost=0.00..3137.00 rows=500 width=52)
                      (actual time=0.035..22.456 loops=1)
   Filter: ((EXTRACT(YEAR FROM order_date) = 2023) AND ...)
   Rows Removed by Filter: 99500
 Execution Time: 22.512 ms
```

**Diagnosis**: Functions on columns prevent index usage.

**Fix**: Rewrite to use range comparison.

```sql
CREATE INDEX idx_orders_date ON orders(order_date);

-- AFTER: Range comparison uses the index
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE order_date >= '2023-06-01'
  AND order_date < '2023-07-01';
```

```
 Index Scan using idx_orders_date on orders
   (cost=0.29..55.30 rows=500 width=52) (actual time=0.028..0.456 loops=1)
   Index Cond: ((order_date >= '2023-06-01') AND (order_date < '2023-07-01'))
 Execution Time: 0.523 ms
```

**Result**: 22.5ms down to 0.52ms — 43 times faster.

---

### Slow Query 3: SELECT * with Unnecessary Columns

```sql
-- BEFORE: Fetching all columns when we only need two
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42;
```

```
 Index Scan using idx_orders_customer_id on orders
   (cost=0.29..38.50 rows=98 width=52) (actual time=0.030..0.245 loops=1)
 Execution Time: 0.312 ms
```

**Fix**: Select only needed columns, use a covering index.

```sql
CREATE INDEX idx_orders_cust_date_amount
ON orders(customer_id) INCLUDE (order_date, amount);

-- AFTER: Index Only Scan
EXPLAIN ANALYZE
SELECT order_date, amount FROM orders WHERE customer_id = 42;
```

```
 Index Only Scan using idx_orders_cust_date_amount on orders
   (cost=0.42..4.85 rows=98 width=10) (actual time=0.020..0.065 loops=1)
   Heap Fetches: 0
 Execution Time: 0.089 ms
```

**Result**: 0.31ms down to 0.089ms — 3.5 times faster. Plus much less data transferred.

---

### Slow Query 4: IN Subquery vs EXISTS

```sql
-- BEFORE: IN with correlated subquery
EXPLAIN ANALYZE
SELECT c.name, c.city
FROM customers c
WHERE c.customer_id IN (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE amount > 400
);
```

```
 Hash Join  (cost=2637.50..2682.00 rows=500 width=24)
            (actual time=18.234..18.890 loops=1)
   ->  HashAggregate  (cost=2637.00..2642.00 rows=500 width=4)
       ->  Seq Scan on orders  (cost=0.00..2387.00 rows=20000 width=4)
           Filter: (amount > 400.00)
 Execution Time: 19.012 ms
```

**Fix**: Use EXISTS.

```sql
-- AFTER: EXISTS with index
EXPLAIN ANALYZE
SELECT c.name, c.city
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.customer_id
    AND o.amount > 400
);
```

```
 Nested Loop Semi Join  (cost=0.29..1650.00 rows=500 width=24)
                         (actual time=0.045..8.234 loops=1)
   ->  Seq Scan on customers c  (cost=0.00..16.00 rows=1000 width=28)
   ->  Index Scan using idx_orders_customer_id on orders o
       (cost=0.29..1.50 rows=1 width=4)
       Index Cond: (customer_id = c.customer_id)
       Filter: (amount > 400.00)
 Execution Time: 8.345 ms
```

**Result**: 19ms down to 8.3ms — 2.3 times faster. The improvement is even larger on bigger tables.

---

### Slow Query 5: Aggregate Without Proper Index

```sql
-- BEFORE: Aggregating over a large table
EXPLAIN ANALYZE
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_spent
FROM orders
WHERE order_date >= '2023-01-01' AND order_date < '2024-01-01'
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;
```

```
 Limit  (cost=2890.00..2890.03 rows=10 width=44)
        (actual time=25.678..25.689 loops=1)
   ->  Sort  (cost=2890.00..2892.50 rows=1000 width=44)
       ->  HashAggregate  (cost=2637.00..2867.00 rows=1000 width=44)
           ->  Seq Scan on orders  (cost=0.00..2387.00 rows=50000 width=10)
               Filter: ((order_date >= ...) AND (order_date < ...))
 Execution Time: 25.756 ms
```

**Fix**: Create an index that covers the filter and grouping.

```sql
CREATE INDEX idx_orders_date_customer
ON orders(order_date, customer_id) INCLUDE (amount);

-- AFTER:
EXPLAIN ANALYZE
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_spent
FROM orders
WHERE order_date >= '2023-01-01' AND order_date < '2024-01-01'
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;
```

```
 Limit  (cost=890.00..890.03 rows=10 width=44)
        (actual time=8.234..8.245 loops=1)
   ->  Sort  (cost=890.00..892.50 rows=1000 width=44)
       ->  HashAggregate  (cost=637.00..867.00 rows=1000 width=44)
           ->  Index Only Scan using idx_orders_date_customer on orders
               (cost=0.42..387.00 rows=50000 width=10)
               Index Cond: ((order_date >= ...) AND (order_date < ...))
               Heap Fetches: 0
 Execution Time: 8.312 ms
```

**Result**: 25.8ms down to 8.3ms — 3.1 times faster. The Index Only Scan avoids reading the table entirely.

---

## Performance Tuning Checklist

```
+--+-----------------------------------------------------------+
|  | Step                                                      |
+--+-----------------------------------------------------------+
| 1| Run EXPLAIN ANALYZE on the slow query                     |
| 2| Check for Seq Scans on large tables — add indexes         |
| 3| Check for functions on columns in WHERE — rewrite         |
| 4| Check for missing indexes on JOIN columns                 |
| 5| Replace SELECT * with specific columns                    |
| 6| Replace IN subqueries with EXISTS                         |
| 7| Check if VACUUM and ANALYZE have run recently             |
| 8| Check for unused indexes (wasting write performance)      |
| 9| Consider partial indexes for common filters               |
|10| Consider partitioning for very large tables (100M+ rows)  |
+--+-----------------------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Adding Indexes to Everything

```sql
-- BAD: Index on every column
CREATE INDEX idx1 ON orders(customer_id);
CREATE INDEX idx2 ON orders(product_id);
CREATE INDEX idx3 ON orders(order_date);
CREATE INDEX idx4 ON orders(amount);
CREATE INDEX idx5 ON orders(status);
CREATE INDEX idx6 ON orders(shipping_city);

-- Every INSERT/UPDATE must update ALL six indexes.
-- This slows down writes significantly.

-- GOOD: Only index columns that appear in WHERE, JOIN, or ORDER BY
-- of your actual slow queries.
```

### Mistake 2: Not Running ANALYZE After Loading Data

```sql
-- After a bulk load, PostgreSQL's statistics are outdated.
-- The query planner may make bad decisions.

-- Always run:
ANALYZE orders;
-- After loading significant amounts of data.
```

### Mistake 3: Optimizing Before Measuring

```sql
-- BAD: "I think this query might be slow, let me add indexes"
-- You might be adding indexes for queries that are not even slow.

-- GOOD: First measure with EXPLAIN ANALYZE or pg_stat_statements,
-- then optimize the queries that are actually slow.
```

### Mistake 4: Ignoring the Execution Plan

```sql
-- BAD: Only looking at execution time
EXPLAIN ANALYZE SELECT ...;
-- "It took 500ms, that seems slow"

-- GOOD: Read the full plan to understand WHY it is slow
-- Look for:
--   Seq Scan on large tables (missing index?)
--   Rows Removed by Filter: 999,000 (index needed)
--   Sort (could ORDER BY use an index?)
--   Nested Loop with high loop count (missing index on inner table?)
```

---

## Best Practices

1. **Measure first, optimize second.** Use EXPLAIN ANALYZE and pg_stat_statements to find the actual bottlenecks before making changes.

2. **Create indexes based on your query patterns.** Look at WHERE clauses, JOIN conditions, and ORDER BY columns in your most frequent and slowest queries.

3. **Keep statistics up to date.** Ensure autovacuum is running. Run ANALYZE manually after bulk data loads.

4. **Use composite indexes wisely.** Put the most selective column first. An index on (customer_id, status) works for queries filtering on customer_id alone, but not for status alone.

5. **Avoid SELECT * in production queries.** Fetch only the columns you need. This enables Index Only Scans and reduces data transfer.

6. **Use EXISTS instead of IN for correlated subqueries.** EXISTS stops at the first match, while IN must collect all values.

7. **Keep functions out of WHERE clauses on indexed columns.** Instead of `WHERE UPPER(email) = 'X'`, create a functional index or rewrite the query.

8. **Use connection pooling in production.** PgBouncer in transaction pooling mode is the standard approach.

9. **Monitor dead tuples and vacuum activity.** Too many dead tuples slow down queries because PostgreSQL must skip over them.

10. **Consider partitioning for tables with hundreds of millions of rows** and queries that consistently filter on a date or category column.

---

## Quick Summary

```
+----------------------+----------------------------------------------+
| Tool / Concept       | What It Does                                 |
+----------------------+----------------------------------------------+
| EXPLAIN ANALYZE      | Shows actual query execution plan and times  |
| Seq Scan             | Reads every row (slow on large tables)       |
| Index Scan           | Jumps to matching rows via index (fast)      |
| Index Only Scan      | Gets data from index without touching table  |
| Bitmap Scan          | Builds a map of matching pages               |
| Nested Loop Join     | For each outer row, search inner table       |
| Hash Join            | Build hash from small table, probe with big  |
| pg_stat_statements   | Tracks query execution statistics            |
| Composite Index      | Index on multiple columns                    |
| Partial Index        | Index with a WHERE clause                    |
| INCLUDE              | Add columns to index for Index Only Scans    |
| VACUUM               | Reclaims space from dead rows                |
| ANALYZE              | Updates table statistics for query planner   |
| PgBouncer            | Connection pooler for PostgreSQL              |
| Partitioning         | Splits table into smaller physical pieces    |
+----------------------+----------------------------------------------+
```

---

## Key Points

- EXPLAIN ANALYZE is your most important diagnostic tool. It shows what PostgreSQL actually does and how long each step takes.
- Sequential Scans on large tables are a common performance problem. Adding the right index often provides dramatic improvements.
- Composite indexes should put the most selective column first. They work for queries filtering on the leading columns but not for trailing columns alone.
- Functions on indexed columns in WHERE clauses prevent index usage. Rewrite queries to compare columns directly.
- SELECT * fetches unnecessary data. Specify only the columns you need to enable Index Only Scans.
- EXISTS is generally faster than IN for subqueries because it stops at the first match.
- VACUUM reclaims space from deleted rows. ANALYZE updates statistics. Both are essential for performance.
- Connection pooling (PgBouncer) reduces memory usage by sharing database connections among many application connections.
- Table partitioning helps with very large tables by allowing PostgreSQL to skip irrelevant partitions entirely.
- Always measure before optimizing. Fix the queries that actually cause problems, not the ones you think might be slow.

---

## Practice Questions

1. What is the difference between EXPLAIN and EXPLAIN ANALYZE? Why should you be careful using EXPLAIN ANALYZE with DELETE or UPDATE statements?

2. A query shows `Seq Scan on orders` with `Rows Removed by Filter: 999,500` and only `rows=500` returned. What does this tell you, and how would you fix it?

3. You have an index on `orders(customer_id)`. Will it help this query: `WHERE LOWER(customer_id::TEXT) = '42'`? Why or why not?

4. What is the difference between `VACUUM` and `VACUUM FULL`? When would you use each?

5. You have a table with columns A, B, C and a composite index on (A, B). Which of these queries can use the index?
   - `WHERE A = 1`
   - `WHERE B = 2`
   - `WHERE A = 1 AND B = 2`
   - `WHERE A = 1 AND C = 3`

---

## Exercises

### Exercise 1: Diagnose and Fix

Run EXPLAIN ANALYZE on the following query and optimize it. Document the before and after execution times:

```sql
SELECT c.name, c.city, COUNT(*) AS order_count, SUM(o.amount) AS total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE EXTRACT(YEAR FROM o.order_date) = 2023
GROUP BY c.name, c.city
HAVING COUNT(*) > 5
ORDER BY total DESC;
```

**Hint**: Rewrite the date filter and ensure proper indexes exist on the join and filter columns.

### Exercise 2: Index Audit

Write a query that shows all indexes in the public schema along with:
- How many times each index has been used (scanned)
- The size of each index
- Whether the index has been used in the last 30 days

Identify indexes that should be dropped (never used, taking up space).

**Hint**: Use `pg_stat_user_indexes` and `pg_relation_size()`.

### Exercise 3: Full Performance Report

Create a comprehensive performance report that:
1. Shows the 5 largest tables and their row counts
2. Shows tables with the most dead tuples (needing VACUUM)
3. Shows the most-used and least-used indexes
4. Identifies tables missing indexes on foreign key columns

**Hint**: Use `pg_stat_user_tables`, `pg_stat_user_indexes`, `pg_class`, and `information_schema`.

---

## What Is Next?

Congratulations! You have completed the advanced SQL section of this book. You now have a solid foundation in transactions, window functions, CTEs, stored procedures, triggers, and performance tuning. These skills will serve you well as you build and maintain real-world database applications. In the next section, we will explore database administration and deployment topics to complete your journey from beginner to confident database practitioner.
