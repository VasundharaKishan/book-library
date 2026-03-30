# Chapter 21: Indexes

## What You Will Learn

In this chapter, you will learn how indexes work and why they make your queries faster. You will discover how to create, manage, and choose the right type of index for different situations. You will also learn how to use EXPLAIN and EXPLAIN ANALYZE to read query plans and verify that your indexes are actually being used.

## Why This Chapter Matters

Imagine you have a thick textbook with 800 pages. You need to find every mention of "photosynthesis." You have two choices:

1. **No index:** Start at page 1 and read every single page, looking for the word "photosynthesis." This is slow and tedious.
2. **With an index:** Flip to the back of the book, find "photosynthesis" in the alphabetical index, and see "pages 45, 112, 234, 567." Jump directly to those pages.

Databases work the same way. Without an index, PostgreSQL must scan every row in the table (called a **sequential scan** or **full table scan**). With the right index, PostgreSQL can jump directly to the matching rows.

For small tables with a few hundred rows, this barely matters. But for tables with millions of rows, the difference between a query taking 5 seconds and 5 milliseconds is enormous. Indexes are one of the most important tools for database performance.

---

## Setting Up Our Practice Data

Let us create a reasonably sized dataset to see indexes in action.

```sql
CREATE TABLE customers (
    customer_id  SERIAL PRIMARY KEY,
    first_name   VARCHAR(50) NOT NULL,
    last_name    VARCHAR(50) NOT NULL,
    email        VARCHAR(100) UNIQUE,
    city         VARCHAR(50),
    state        VARCHAR(2),
    created_at   TIMESTAMP DEFAULT NOW(),
    is_active    BOOLEAN DEFAULT TRUE
);

CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INTEGER REFERENCES customers(customer_id),
    order_date   DATE NOT NULL,
    total_amount NUMERIC(10,2),
    status       VARCHAR(20) DEFAULT 'pending'
);

-- Insert sample data
INSERT INTO customers (first_name, last_name, email, city, state)
SELECT
    'First' || n,
    'Last' || n,
    'user' || n || '@example.com',
    CASE (n % 5)
        WHEN 0 THEN 'New York'
        WHEN 1 THEN 'Los Angeles'
        WHEN 2 THEN 'Chicago'
        WHEN 3 THEN 'Houston'
        WHEN 4 THEN 'Phoenix'
    END,
    CASE (n % 5)
        WHEN 0 THEN 'NY'
        WHEN 1 THEN 'CA'
        WHEN 2 THEN 'IL'
        WHEN 3 THEN 'TX'
        WHEN 4 THEN 'AZ'
    END
FROM generate_series(1, 100000) AS n;

INSERT INTO orders (customer_id, order_date, total_amount, status)
SELECT
    (random() * 99999 + 1)::INTEGER,
    '2023-01-01'::DATE + (random() * 730)::INTEGER,
    (random() * 500 + 10)::NUMERIC(10,2),
    CASE (random() * 3)::INTEGER
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'shipped'
        WHEN 2 THEN 'delivered'
        ELSE 'cancelled'
    END
FROM generate_series(1, 500000);
```

---

## How Indexes Speed Up Queries

Without an index, PostgreSQL uses a **Sequential Scan** (Seq Scan). It reads every row in the table and checks whether it matches your condition. For a table with 100,000 rows, it must check all 100,000 rows.

With an index, PostgreSQL uses an **Index Scan**. It looks up the matching values in the index data structure (usually a B-tree) and then jumps directly to the relevant rows. For a query that matches 10 rows out of 100,000, it only needs to read about 10 rows instead of 100,000.

```
Without Index (Sequential Scan):
+------+------+------+------+------+------+------+------+
| Row1 | Row2 | Row3 | Row4 | Row5 | Row6 | Row7 | ...  |
+------+------+------+------+------+------+------+------+
  Check  Check  Check  MATCH  Check  Check  MATCH  ...

  Must check EVERY row. Slow for large tables.


With Index (Index Scan):
+------------------+
|   B-tree Index   |
|  (sorted values) |
+------------------+
       |
       v
  Jump directly to Row4 and Row7

  Checks only matching rows. Fast!
```

---

## B-tree Index: The Default

The B-tree (Balanced tree) is the default index type in PostgreSQL. It works like a well-organized filing system.

Think of a library's card catalog. Cards are organized alphabetically. To find a book by "Smith," you do not start at "A." You jump to the "S" section, then narrow down to "Sm," then "Smi," and quickly find "Smith."

A B-tree works similarly. It organizes values in a tree structure where each level narrows the search.

```
B-tree for last_name index:

                  [Johnson]
                 /          \
          [Brown]            [Smith]
         /      \           /      \
    [Adams] [Clark]   [Miller] [Wilson]
      /\      /\        /\       /\
   rows..  rows..    rows..   rows..

To find "Miller":
  1. Start at root: "Miller" > "Johnson" -> go right
  2. Next level: "Miller" < "Smith" -> go left
  3. Found "Miller" -> follow pointer to actual rows

Only 3 comparisons instead of scanning all rows!
```

B-tree indexes support these operations efficiently:
- **Equality:** `WHERE last_name = 'Smith'`
- **Range:** `WHERE salary > 50000`
- **Sorting:** `ORDER BY last_name`
- **BETWEEN:** `WHERE created_at BETWEEN '2024-01-01' AND '2024-06-30'`
- **IS NULL / IS NOT NULL**

---

## Creating Indexes

### Syntax

```sql
CREATE INDEX index_name ON table_name (column_name);
```

### Example: Index on city

```sql
CREATE INDEX idx_customers_city ON customers (city);
```

**Line-by-Line Explanation:**

- `CREATE INDEX` -- Tell PostgreSQL to create a new index.
- `idx_customers_city` -- The name of the index. A common convention is `idx_tablename_columnname`.
- `ON customers` -- The table this index belongs to.
- `(city)` -- The column to index.

### Naming Convention

A good naming convention makes it easy to understand what an index does at a glance.

```
idx_<table>_<column(s)>

Examples:
  idx_customers_email
  idx_orders_customer_id
  idx_orders_date_status     (composite index)
```

---

## EXPLAIN and EXPLAIN ANALYZE

How do you know if PostgreSQL is actually using your index? Use EXPLAIN and EXPLAIN ANALYZE to see the query plan.

### EXPLAIN: See the Plan Without Running It

```sql
EXPLAIN SELECT * FROM customers WHERE city = 'Chicago';
```

**Result (before creating index):**

```
                         QUERY PLAN
------------------------------------------------------------
 Seq Scan on customers  (cost=0.00..2137.00 rows=20000 width=67)
   Filter: ((city)::text = 'Chicago'::text)
(2 rows)
```

**Reading the output:**

- `Seq Scan on customers` -- PostgreSQL is doing a sequential scan (reading every row). No index is being used.
- `cost=0.00..2137.00` -- Estimated cost (in arbitrary units). The first number is startup cost, the second is total cost.
- `rows=20000` -- PostgreSQL estimates it will find about 20,000 matching rows.
- `Filter: ((city)::text = 'Chicago'::text)` -- The filter condition being applied to each row.

### EXPLAIN ANALYZE: Run It and Show Actual Times

```sql
EXPLAIN ANALYZE SELECT * FROM customers WHERE city = 'Chicago';
```

**Result (before index):**

```
                         QUERY PLAN
------------------------------------------------------------
 Seq Scan on customers  (cost=0.00..2137.00 rows=20000 width=67)
                        (actual time=0.015..12.345 rows=20000 loops=1)
   Filter: ((city)::text = 'Chicago'::text)
   Rows Removed by Filter: 80000
 Planning Time: 0.085 ms
 Execution Time: 13.456 ms
(5 rows)
```

Now let us create the index and see the difference:

```sql
CREATE INDEX idx_customers_city ON customers (city);

EXPLAIN ANALYZE SELECT * FROM customers WHERE city = 'Chicago';
```

**Result (after index):**

```
                         QUERY PLAN
------------------------------------------------------------
 Bitmap Heap Scan on customers  (cost=236.00..1287.00 rows=20000 width=67)
                                (actual time=1.234..5.678 rows=20000 loops=1)
   Recheck Cond: ((city)::text = 'Chicago'::text)
   ->  Bitmap Index Scan on idx_customers_city  (cost=0.00..231.00 rows=20000 width=0)
                                                (actual time=0.987..0.987 rows=20000 loops=1)
         Index Cond: ((city)::text = 'Chicago'::text)
 Planning Time: 0.120 ms
 Execution Time: 6.789 ms
(6 rows)
```

**Reading the output:**

- `Bitmap Index Scan on idx_customers_city` -- PostgreSQL is using our index.
- The execution time dropped from ~13ms to ~7ms.

> **Note:** When a query returns a large portion of the table (like 20% of rows), PostgreSQL may still choose a sequential scan because reading lots of scattered index entries is not much faster than reading the whole table. Indexes shine most when finding a small number of rows in a large table.

### A More Dramatic Example

```sql
-- Find a single customer by email (only 1 row out of 100,000)
EXPLAIN ANALYZE SELECT * FROM customers WHERE email = 'user50000@example.com';
```

```
                         QUERY PLAN
------------------------------------------------------------
 Index Scan using customers_email_key on customers
   (cost=0.42..8.44 rows=1 width=67)
   (actual time=0.025..0.026 rows=1 loops=1)
   Index Cond: ((email)::text = 'user50000@example.com'::text)
 Planning Time: 0.095 ms
 Execution Time: 0.045 ms
(4 rows)
```

This query uses the unique index that was automatically created by the `UNIQUE` constraint on `email`. It finds one row out of 100,000 in 0.045 milliseconds. That is the power of indexes.

---

## When Indexes Help

Indexes are most effective in these situations:

### 1. WHERE Clauses

```sql
-- Finding specific rows
CREATE INDEX idx_customers_state ON customers (state);

SELECT * FROM customers WHERE state = 'TX';
```

### 2. JOIN Conditions

```sql
-- Joining tables on foreign keys
CREATE INDEX idx_orders_customer_id ON orders (customer_id);

SELECT c.first_name, o.order_date, o.total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.city = 'Houston';
```

The index on `orders.customer_id` helps PostgreSQL quickly find all orders for each customer.

### 3. ORDER BY

```sql
-- Sorting results
CREATE INDEX idx_orders_order_date ON orders (order_date);

SELECT * FROM orders ORDER BY order_date DESC LIMIT 20;
```

With the index, PostgreSQL can read the rows in order directly from the index instead of sorting them afterward.

### 4. Aggregate Functions with GROUP BY

```sql
SELECT customer_id, COUNT(*), SUM(total_amount)
FROM orders
GROUP BY customer_id;
```

An index on `customer_id` can speed up grouping operations.

---

## When Indexes Hurt

Indexes are not free. They come with costs.

### Cost 1: Slower Writes

Every time you INSERT, UPDATE, or DELETE a row, PostgreSQL must also update every index on that table. More indexes mean slower write operations.

```
INSERT a new row:
  1. Write the row to the table          -- always happens
  2. Update index on customer_id         -- extra work
  3. Update index on email               -- extra work
  4. Update index on city                -- extra work
  5. Update index on state               -- extra work
  6. Update index on created_at          -- extra work

5 indexes = 5 extra operations per INSERT!
```

### Cost 2: Disk Space

Each index takes up disk space. For a large table, indexes can use as much space as the table itself.

### Cost 3: Maintenance Overhead

Indexes need to be maintained. Over time, as data changes, indexes can become bloated and need to be rebuilt.

### Rule of Thumb

```
+----------------------------------+-----------------------------------+
| DO create an index when:         | DO NOT create an index when:      |
+----------------------------------+-----------------------------------+
| Column is used often in WHERE    | Column is rarely used in queries  |
| Column is used in JOIN           | Table is very small (< 1000 rows)|
| Column is used in ORDER BY      | Column has very few distinct      |
| High selectivity (few matches)   |   values (e.g., boolean)          |
| Table has many rows              | Table has heavy write workload    |
+----------------------------------+-----------------------------------+
```

---

## Composite Indexes

A composite (multi-column) index covers two or more columns. It is useful when you frequently query using multiple columns together.

### Creating a Composite Index

```sql
CREATE INDEX idx_orders_date_status ON orders (order_date, status);
```

This index is efficient for queries that filter on:
- `order_date` alone (leftmost column)
- `order_date AND status` (both columns)

But it is **not efficient** for queries that filter on:
- `status` alone (not the leftmost column)

This is called the **leftmost prefix rule**. Think of it like a phone book sorted by last name, then first name. You can look up "Smith" (last name only) or "Smith, John" (both). But you cannot efficiently look up just "John" (first name only) because the book is not sorted that way.

```
Composite Index: (order_date, status)

+----+------------+-----------+
|    | order_date | status    |  <-- Sorted by order_date first,
+----+------------+-----------+      then by status within each date
|  1 | 2024-01-01 | delivered |
|  2 | 2024-01-01 | pending   |
|  3 | 2024-01-01 | shipped   |
|  4 | 2024-01-02 | cancelled |
|  5 | 2024-01-02 | delivered |
|  6 | 2024-01-02 | pending   |
+----+------------+-----------+

Can use index:                    Cannot use index efficiently:
  WHERE order_date = '2024-01-01'   WHERE status = 'pending'
  WHERE order_date = '2024-01-01'   (status is not the leftmost
    AND status = 'shipped'            column in the index)
```

### Example

```sql
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE order_date = '2024-06-15' AND status = 'shipped';
```

```
                         QUERY PLAN
------------------------------------------------------------
 Index Scan using idx_orders_date_status on orders
   (cost=0.42..12.50 rows=5 width=39)
   (actual time=0.030..0.042 rows=3 loops=1)
   Index Cond: ((order_date = '2024-06-15') AND (status = 'shipped'))
 Planning Time: 0.150 ms
 Execution Time: 0.065 ms
(4 rows)
```

The composite index handles both conditions efficiently.

---

## Partial Indexes

A partial index only indexes rows that meet a certain condition. It is smaller and more efficient than a full index when you only query a subset of the data.

### Syntax

```sql
CREATE INDEX index_name ON table_name (column_name)
WHERE condition;
```

### Example: Index Only Active Customers

If 95% of your queries filter on `is_active = TRUE`, there is no point indexing the inactive rows.

```sql
CREATE INDEX idx_customers_city_active
ON customers (city)
WHERE is_active = TRUE;
```

This index is smaller because it excludes inactive customers. Queries that filter on active customers will be faster, and the index takes up less space.

```sql
-- This query uses the partial index
EXPLAIN ANALYZE
SELECT * FROM customers
WHERE city = 'Phoenix' AND is_active = TRUE;

-- This query CANNOT use the partial index (missing is_active filter)
EXPLAIN ANALYZE
SELECT * FROM customers
WHERE city = 'Phoenix';
```

### When to Use Partial Indexes

- When you frequently filter on a specific condition (e.g., `status = 'active'`, `is_deleted = FALSE`)
- When only a small portion of the table matches your usual queries
- When you want to reduce index size and maintenance cost

---

## Unique Indexes

A unique index ensures that no two rows have the same value in the indexed column(s). PostgreSQL automatically creates a unique index when you define a `UNIQUE` constraint or `PRIMARY KEY`.

```sql
-- These two are equivalent:
ALTER TABLE customers ADD CONSTRAINT unique_email UNIQUE (email);
CREATE UNIQUE INDEX idx_customers_email_unique ON customers (email);
```

Unique indexes serve double duty: they enforce data integrity AND speed up lookups.

---

## Index Types in PostgreSQL

PostgreSQL offers several index types, each optimized for different use cases.

### B-tree (Default)

```sql
CREATE INDEX idx_name ON table_name (column);
-- Equivalent to:
CREATE INDEX idx_name ON table_name USING btree (column);
```

Best for: Equality (`=`), range (`<`, `>`, `BETWEEN`), sorting (`ORDER BY`), pattern matching (`LIKE 'abc%'`).

### Hash

```sql
CREATE INDEX idx_name ON table_name USING hash (column);
```

Best for: Equality comparisons only (`=`). Slightly faster than B-tree for pure equality lookups, but cannot handle ranges or sorting.

### GIN (Generalized Inverted Index)

```sql
CREATE INDEX idx_name ON table_name USING gin (column);
```

Best for: Full-text search, array columns, JSONB data. A GIN index maps each value (like each word in a text) to the rows that contain it.

### GiST (Generalized Search Tree)

```sql
CREATE INDEX idx_name ON table_name USING gist (column);
```

Best for: Geometric data, range types, full-text search, nearest-neighbor queries. Often used with PostGIS for geographic data.

### Summary

```
+--------+----------------------------------+----------------------------+
| Type   | Best For                         | Example Use Case           |
+--------+----------------------------------+----------------------------+
| B-tree | Equality, ranges, sorting        | WHERE price > 100          |
|        |                                  | ORDER BY date              |
+--------+----------------------------------+----------------------------+
| Hash   | Equality only                    | WHERE status = 'active'    |
+--------+----------------------------------+----------------------------+
| GIN    | Arrays, JSONB, full-text search   | WHERE tags @> '{sql}'      |
|        |                                  | Full-text search           |
+--------+----------------------------------+----------------------------+
| GiST   | Geometry, ranges, proximity       | Nearest restaurant query   |
|        |                                  | Overlapping date ranges    |
+--------+----------------------------------+----------------------------+
```

For most everyday work, **B-tree** is the right choice. You will use GIN and GiST for specialized scenarios.

---

## DROP INDEX

To remove an index:

```sql
DROP INDEX idx_customers_city;
```

To avoid errors if the index does not exist:

```sql
DROP INDEX IF EXISTS idx_customers_city;
```

To drop an index even when used by views or other objects:

```sql
DROP INDEX idx_customers_city CASCADE;
```

> **Note:** Dropping an index does not delete any data. It only removes the index structure. Queries will still work, they just might be slower.

---

## Reading Query Plans in Detail

Let us break down a more complex EXPLAIN ANALYZE output to understand what each part means.

```sql
EXPLAIN ANALYZE
SELECT c.first_name, c.last_name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.state = 'TX'
GROUP BY c.first_name, c.last_name
ORDER BY order_count DESC
LIMIT 10;
```

```
                         QUERY PLAN
------------------------------------------------------------
 Limit  (cost=5000.00..5000.02 rows=10 width=23)
        (actual time=45.123..45.130 rows=10 loops=1)
   ->  Sort  (cost=5000.00..5050.00 rows=20000 width=23)
             (actual time=45.120..45.125 rows=10 loops=1)
         Sort Key: (count(o.order_id)) DESC
         Sort Method: top-N heapsort  Memory: 25kB
         ->  HashAggregate  (cost=4500.00..4700.00 rows=20000 width=23)
                            (actual time=40.000..43.000 rows=20000 loops=1)
               Group Key: c.first_name, c.last_name
               ->  Hash Join  (cost=700.00..3500.00 rows=100000 width=19)
                              (actual time=5.000..25.000 rows=100234 loops=1)
                     Hash Cond: (o.customer_id = c.customer_id)
                     ->  Seq Scan on orders o  (cost=0.00..2000.00 rows=500000 width=8)
                                               (actual time=0.010..8.000 rows=500000 loops=1)
                     ->  Hash  (cost=600.00..600.00 rows=20000 width=19)
                               (actual time=4.500..4.500 rows=20000 loops=1)
                           ->  Seq Scan on customers c  (cost=0.00..600.00 rows=20000 width=19)
                                                        (actual time=0.010..3.000 rows=20000 loops=1)
                                 Filter: ((state)::text = 'TX'::text)
                                 Rows Removed by Filter: 80000
 Planning Time: 0.500 ms
 Execution Time: 45.250 ms
(15 rows)
```

**Reading from bottom to top (that is how execution flows):**

1. **Seq Scan on customers** -- Scans all 100,000 customers, filters to 20,000 where state = 'TX'. Removes 80,000 rows.
2. **Hash** -- Builds a hash table of those 20,000 Texas customers in memory.
3. **Seq Scan on orders** -- Scans all 500,000 orders.
4. **Hash Join** -- Joins orders to the hash table of Texas customers. Finds ~100,234 matching order-customer pairs.
5. **HashAggregate** -- Groups by first_name and last_name, counts orders per group. Produces 20,000 groups.
6. **Sort** -- Sorts by order count descending.
7. **Limit** -- Returns only the top 10.

**Key numbers to watch:**

- `actual time` -- Real wall-clock time in milliseconds. Look at the second number (total time).
- `rows` -- How many rows that step produced. Compare estimated (`rows=20000` in cost section) vs actual (`rows=20000` in actual section). Large mismatches suggest stale statistics.
- `Rows Removed by Filter` -- How many rows were read but did not match. High numbers may indicate a missing index.

---

## Practical Example: Adding Indexes to Slow Queries

Let us walk through a real-world scenario of finding and fixing a slow query.

### Step 1: Identify the Slow Query

```sql
-- Find all pending orders from Texas customers in the last month
EXPLAIN ANALYZE
SELECT
    c.first_name,
    c.last_name,
    c.email,
    o.order_date,
    o.total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.state = 'TX'
  AND o.status = 'pending'
  AND o.order_date >= '2024-06-01'
ORDER BY o.order_date DESC;
```

### Step 2: Read the Query Plan

Look for:
- **Seq Scan** on large tables (indicates no index is being used)
- **Rows Removed by Filter** (high numbers mean we are reading many unnecessary rows)
- **High execution time**

### Step 3: Add Targeted Indexes

```sql
-- Index for filtering customers by state
CREATE INDEX idx_customers_state ON customers (state);

-- Composite index for filtering orders by status and date
CREATE INDEX idx_orders_status_date ON orders (status, order_date);

-- Index for the join condition (if not already indexed)
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
```

### Step 4: Verify Improvement

```sql
EXPLAIN ANALYZE
SELECT
    c.first_name,
    c.last_name,
    c.email,
    o.order_date,
    o.total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.state = 'TX'
  AND o.status = 'pending'
  AND o.order_date >= '2024-06-01'
ORDER BY o.order_date DESC;
```

After adding indexes, you should see:
- Index Scans replacing Seq Scans
- Lower execution time
- Fewer rows removed by filter

### Step 5: Clean Up Unused Indexes

You can check which indexes are not being used:

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS times_used
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY tablename, indexname;
```

If an index has `idx_scan = 0` after weeks of production use, consider dropping it to save space and improve write performance.

---

## Common Mistakes

### Mistake 1: Indexing Every Column

```sql
-- WRONG: Creating an index on every column
CREATE INDEX idx1 ON orders (order_id);       -- Already has PK index
CREATE INDEX idx2 ON orders (customer_id);
CREATE INDEX idx3 ON orders (order_date);
CREATE INDEX idx4 ON orders (total_amount);
CREATE INDEX idx5 ON orders (status);

-- This slows down every INSERT, UPDATE, and DELETE!
```

Only create indexes on columns that are frequently used in WHERE, JOIN, or ORDER BY clauses.

### Mistake 2: Wrong Column Order in Composite Indexes

```sql
-- You query: WHERE status = 'pending' AND order_date > '2024-01-01'
-- But most of your rows are filtered by order_date, not status

-- LESS EFFECTIVE: status first (low selectivity)
CREATE INDEX idx_bad ON orders (status, order_date);

-- MORE EFFECTIVE: order_date first (high selectivity)
CREATE INDEX idx_good ON orders (order_date, status);
```

Put the most selective column (the one that eliminates the most rows) first in a composite index.

### Mistake 3: Not Checking if Indexes Are Used

Always verify with EXPLAIN ANALYZE that your index is actually being used. PostgreSQL might choose not to use it if:
- The table is small enough that a sequential scan is faster
- The query returns too many rows (low selectivity)
- Statistics are outdated (run `ANALYZE table_name` to update)

### Mistake 4: Indexing Low-Selectivity Columns

```sql
-- POOR: Boolean columns have only 2 values
CREATE INDEX idx_customers_active ON customers (is_active);
-- PostgreSQL will likely ignore this index

-- BETTER: Use a partial index
CREATE INDEX idx_customers_inactive ON customers (customer_id)
WHERE is_active = FALSE;
```

### Mistake 5: Forgetting to ANALYZE After Bulk Loads

```sql
-- After inserting many rows, update statistics
ANALYZE customers;
ANALYZE orders;
```

PostgreSQL uses statistics to decide whether to use an index. Outdated statistics can lead to poor query plans.

---

## Best Practices

1. **Start without indexes, then add as needed.** Create indexes to solve specific performance problems, not preemptively.

2. **Always verify with EXPLAIN ANALYZE.** Do not assume an index is helping. Check the query plan.

3. **Index foreign key columns.** Columns used in JOINs (especially foreign keys) are almost always worth indexing.

4. **Use composite indexes for multi-column filters.** If you always filter on `status AND date`, a composite index on `(status, date)` is better than two separate indexes.

5. **Use partial indexes for common filters.** If 95% of queries filter `WHERE is_active = TRUE`, a partial index saves space and improves performance.

6. **Monitor index usage.** Regularly check `pg_stat_user_indexes` to find and remove unused indexes.

7. **Run ANALYZE after bulk operations.** After large inserts, updates, or deletes, update table statistics so PostgreSQL can make good query planning decisions.

8. **Consider CONCURRENTLY for production.** Use `CREATE INDEX CONCURRENTLY` to avoid locking the table during index creation:

```sql
CREATE INDEX CONCURRENTLY idx_orders_date ON orders (order_date);
```

This takes longer but allows reads and writes to continue during index creation.

---

## Quick Summary

```
+---------------------------+------------------------------------------+
| Feature                   | Description                              |
+---------------------------+------------------------------------------+
| CREATE INDEX              | Create an index on a column              |
+---------------------------+------------------------------------------+
| CREATE UNIQUE INDEX       | Index that enforces uniqueness            |
+---------------------------+------------------------------------------+
| Composite Index           | Index on multiple columns                |
+---------------------------+------------------------------------------+
| Partial Index             | Index with a WHERE condition             |
+---------------------------+------------------------------------------+
| DROP INDEX                | Remove an index                          |
+---------------------------+------------------------------------------+
| EXPLAIN                   | Show the query plan (without running)    |
+---------------------------+------------------------------------------+
| EXPLAIN ANALYZE           | Show the plan with actual execution data |
+---------------------------+------------------------------------------+
| B-tree                    | Default. Equality, range, sorting        |
+---------------------------+------------------------------------------+
| Hash                      | Equality only                            |
+---------------------------+------------------------------------------+
| GIN                       | Arrays, JSONB, full-text search          |
+---------------------------+------------------------------------------+
| GiST                      | Geometry, ranges, proximity              |
+---------------------------+------------------------------------------+
```

---

## Key Points

- An **index** is a data structure that speeds up data retrieval, similar to a book's index.
- The default index type is **B-tree**, which works well for equality, range, and sorting operations.
- Indexes speed up **reads** (SELECT) but slow down **writes** (INSERT, UPDATE, DELETE).
- Use **EXPLAIN ANALYZE** to verify that PostgreSQL is using your indexes and to measure actual performance.
- **Composite indexes** cover multiple columns. The leftmost prefix rule determines which queries can use them.
- **Partial indexes** only index rows matching a condition, making them smaller and faster.
- **Do not over-index.** Every index adds overhead to write operations. Only index columns that are frequently queried.
- Use **CREATE INDEX CONCURRENTLY** in production to avoid locking tables.
- Monitor index usage with `pg_stat_user_indexes` and remove unused indexes.

---

## Practice Questions

1. Explain the book index analogy for database indexes. Why does a sequential scan become problematic as a table grows?

2. You have a composite index on `(city, state)`. Which of these queries can use the index: (a) `WHERE city = 'Houston'`, (b) `WHERE state = 'TX'`, (c) `WHERE city = 'Houston' AND state = 'TX'`? Explain why.

3. What is the difference between EXPLAIN and EXPLAIN ANALYZE? When would you use one over the other?

4. Why would you choose a partial index over a regular index? Give an example scenario.

5. A table has 10 indexes and experiences heavy INSERT traffic. The INSERT operations are becoming slow. What would you investigate and how might you fix the problem?

---

## Exercises

### Exercise 1: Index Investigation

Using the `orders` table, write a query that finds all delivered orders with a total amount greater than 400. First, run it with EXPLAIN ANALYZE to see the plan without any custom indexes. Then create an appropriate index and run EXPLAIN ANALYZE again. Compare the results.

### Exercise 2: Composite Index Design

You frequently run this query:
```sql
SELECT * FROM orders
WHERE customer_id = 12345
  AND order_date >= '2024-01-01'
ORDER BY order_date DESC;
```
Design the best composite index for this query. Explain your choice of column order. Verify with EXPLAIN ANALYZE.

### Exercise 3: Finding and Removing Unused Indexes

Write a query against `pg_stat_user_indexes` that lists all indexes on your tables along with how many times each has been scanned. Identify any indexes that have never been used and write the DROP statements for them (but do not execute them yet -- review first).

---

## What Is Next?

Now that you understand how indexes make queries fast, the next chapter will explore **Normalization**. Normalization is the art of organizing your tables to reduce redundancy and prevent data anomalies. You will learn the normal forms (1NF, 2NF, 3NF) and how to transform a messy spreadsheet into a set of clean, well-structured tables.
