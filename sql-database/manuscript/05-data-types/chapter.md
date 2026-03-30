# Chapter 5: Data Types in PostgreSQL

## What You Will Learn

By the end of this chapter, you will understand:

- Integer types: INTEGER, BIGINT, and SMALLINT
- Auto-incrementing types: SERIAL and BIGSERIAL
- Exact decimal types: NUMERIC and DECIMAL (and why you must use them for money)
- Text types: VARCHAR(n), TEXT, and CHAR(n)
- Boolean type: TRUE and FALSE
- Date and time types: DATE, TIME, TIMESTAMP, and INTERVAL
- UUID: universally unique identifiers
- JSON and JSONB: storing structured data inside a column
- ARRAY: storing lists inside a column
- How to choose the right data type for every situation
- Common mistakes like using FLOAT for money or VARCHAR when TEXT works fine

## Why This Chapter Matters

Choosing the right data type is one of the most important decisions you make when designing a database. The wrong data type can cause:

- **Lost data** (storing a large number in a column too small to hold it).
- **Wrong calculations** (using FLOAT for money and getting rounding errors).
- **Wasted space** (using BIGINT when SMALLINT is enough).
- **Slow queries** (using TEXT when VARCHAR would be faster for indexing).

Getting data types right from the start saves you from painful problems later.

---

## Integer Types: Whole Numbers

Integers are whole numbers without decimal points. PostgreSQL provides three sizes:

```
+------------+----------------------------+------------------------------+
| Type       | Range                      | Storage Size                 |
+------------+----------------------------+------------------------------+
| SMALLINT   | -32,768 to 32,767          | 2 bytes                      |
| INTEGER    | -2,147,483,648 to          | 4 bytes                      |
|            |  2,147,483,647             |                              |
| BIGINT     | -9,223,372,036,854,775,808 | 8 bytes                      |
|            |  to 9,223,372,036,854,     |                              |
|            |  775,807                   |                              |
+------------+----------------------------+------------------------------+
```

**Think of it as choosing a container size:**
- SMALLINT is a small box. It holds numbers up to about 32 thousand.
- INTEGER is a medium box. It holds numbers up to about 2 billion.
- BIGINT is a large box. It holds numbers up to about 9 quintillion.

### When to Use Each

```
+------------+-----------------------------------------------+
| Type       | Use When                                      |
+------------+-----------------------------------------------+
| SMALLINT   | Values will never exceed 32,767               |
|            | Examples: age, quantity of items in a cart,    |
|            |   number of pages in a book                   |
+------------+-----------------------------------------------+
| INTEGER    | The default choice for most situations         |
|            | Examples: user IDs, product IDs, counts        |
+------------+-----------------------------------------------+
| BIGINT     | Values could exceed 2 billion                  |
|            | Examples: row counts in huge tables,           |
|            |   social media post IDs, financial cents       |
+------------+-----------------------------------------------+
```

### Example

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    stock_quantity SMALLINT,
    total_views BIGINT
);

INSERT INTO products (id, name, stock_quantity, total_views)
VALUES (1, 'Widget', 500, 15000000000);
```

```sql
SELECT * FROM products;
```

```
 id |  name  | stock_quantity | total_views
----+--------+----------------+-------------
  1 | Widget |            500 | 15000000000
(1 row)
```

### What Happens When You Exceed the Limit

```sql
-- SMALLINT max is 32,767
INSERT INTO products (id, name, stock_quantity, total_views)
VALUES (2, 'Gadget', 50000, 100);

-- ERROR: smallint out of range
```

PostgreSQL stops you from inserting a value that does not fit. This is protection against data loss.

---

## SERIAL and BIGSERIAL: Auto-Incrementing IDs

**SERIAL** and **BIGSERIAL** are not true data types. They are shortcuts that create an auto-incrementing integer column. Each new row automatically gets the next number in the sequence.

```
+------------+----------------------------+-----------+
| Type       | Underlying Type            | Max Value |
+------------+----------------------------+-----------+
| SERIAL     | INTEGER                    | ~2 billion|
| BIGSERIAL  | BIGINT                     | ~9 quintillion|
+------------+----------------------------+-----------+
```

**Think of it as:** A ticket machine at a deli counter. Each customer gets the next number automatically. Nobody has to manually assign numbers.

### Example

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50)
);

-- Notice: we do NOT provide the id value
INSERT INTO students (first_name, last_name) VALUES ('Alice', 'Johnson');
INSERT INTO students (first_name, last_name) VALUES ('Bob', 'Smith');
INSERT INTO students (first_name, last_name) VALUES ('Charlie', 'Brown');
```

```sql
SELECT * FROM students;
```

```
 id | first_name | last_name
----+------------+-----------
  1 | Alice      | Johnson
  2 | Bob        | Smith
  3 | Charlie    | Brown
(3 rows)
```

The `id` values (1, 2, 3) were assigned automatically.

### SERIAL vs BIGSERIAL

Use `SERIAL` for most tables. Use `BIGSERIAL` only when you expect the table to have more than 2 billion rows. Social media platforms, logging systems, and IoT data might need BIGSERIAL. A school or small business application will be fine with SERIAL.

### What Happens If You Delete a Row?

If you delete Bob (id=2) and insert a new student, the new student gets id=4, not id=2. Serial values never reuse numbers:

```sql
DELETE FROM students WHERE id = 2;
INSERT INTO students (first_name, last_name) VALUES ('Diana', 'Prince');
```

```sql
SELECT * FROM students;
```

```
 id | first_name | last_name
----+------------+-----------
  1 | Alice      | Johnson
  3 | Charlie    | Brown
  4 | Diana      | Prince
(3 rows)
```

The gap at id=2 is normal and expected. Do not worry about gaps in SERIAL values.

---

## NUMERIC and DECIMAL: Exact Decimal Numbers

**NUMERIC** and **DECIMAL** are identical in PostgreSQL. They store exact decimal numbers with a specified precision.

```
NUMERIC(precision, scale)
```

- **Precision** is the total number of digits (before and after the decimal point).
- **Scale** is the number of digits after the decimal point.

```
+---------------------+-------------------------------------+
| Definition          | What It Accepts                     |
+---------------------+-------------------------------------+
| NUMERIC(5, 2)       | Up to 5 total digits, 2 after       |
|                     | the decimal: 999.99 max             |
|                     | Examples: 123.45, 99.99, 0.50       |
+---------------------+-------------------------------------+
| NUMERIC(10, 2)      | Up to 10 digits, 2 after decimal    |
|                     | 99,999,999.99 max                   |
|                     | Good for prices and money           |
+---------------------+-------------------------------------+
| NUMERIC(3, 2)       | Up to 3 digits, 2 after decimal     |
|                     | 9.99 max                            |
|                     | Good for GPA (0.00 to 4.00)         |
+---------------------+-------------------------------------+
```

### Why NUMERIC for Money? (The FLOAT Trap)

This is critically important. **Never use FLOAT or REAL for money.** Here is why:

```sql
-- FLOAT is not exact!
SELECT 0.1::FLOAT + 0.2::FLOAT AS float_result;
```

```
    float_result
--------------------
 0.30000000000000004
```

0.1 + 0.2 does not equal 0.3 in floating-point arithmetic. It equals 0.30000000000000004. This is not a PostgreSQL bug. It is how all computers handle floating-point numbers.

Now compare with NUMERIC:

```sql
-- NUMERIC is exact!
SELECT 0.1::NUMERIC + 0.2::NUMERIC AS numeric_result;
```

```
 numeric_result
----------------
            0.3
```

If you store money as FLOAT, you will eventually have transactions that are off by a fraction of a cent. Over thousands of transactions, these errors add up.

### Example

```sql
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    subtotal NUMERIC(10, 2) NOT NULL,
    tax NUMERIC(10, 2) NOT NULL,
    total NUMERIC(10, 2) NOT NULL
);

INSERT INTO invoices (customer_name, subtotal, tax, total)
VALUES ('Alice', 99.99, 8.00, 107.99);
```

```sql
SELECT * FROM invoices;
```

```
 id | customer_name | subtotal | tax  |  total
----+---------------+----------+------+--------
  1 | Alice         |    99.99 | 8.00 | 107.99
(1 row)
```

---

## Text Types: Storing Words and Sentences

PostgreSQL offers three main text types:

```
+----------------+----------------------------------+---------------------------+
| Type           | Description                      | Max Length                |
+----------------+----------------------------------+---------------------------+
| CHAR(n)        | Fixed-length text, padded with   | Exactly n characters      |
|                |   spaces if shorter              |                           |
+----------------+----------------------------------+---------------------------+
| VARCHAR(n)     | Variable-length text with a      | Up to n characters        |
|                |   maximum length                 |                           |
+----------------+----------------------------------+---------------------------+
| TEXT           | Variable-length text with no     | Unlimited (up to ~1 GB)   |
|                |   length limit                   |                           |
+----------------+----------------------------------+---------------------------+
```

### CHAR(n): Fixed-Length Text

`CHAR(n)` always stores exactly `n` characters. If your text is shorter, it pads the rest with spaces.

```sql
CREATE TABLE codes (
    country_code CHAR(2),
    state_code CHAR(3)
);

INSERT INTO codes VALUES ('US', 'CA');
INSERT INTO codes VALUES ('UK', 'LN');
```

`CHAR(2)` is useful for data that is always exactly 2 characters (like country codes: US, UK, CA).

**When to use:** Only when every value has the same fixed length. This is rare.

### VARCHAR(n): Variable-Length Text with a Limit

`VARCHAR(n)` stores text up to `n` characters. If your text is shorter, it does not pad with spaces.

```sql
CREATE TABLE users (
    username VARCHAR(30),
    email VARCHAR(100)
);

INSERT INTO users VALUES ('alice_j', 'alice.johnson@example.com');
```

`VARCHAR(30)` means the username can be anywhere from 0 to 30 characters.

**When to use:** When you want to enforce a maximum length. Good for usernames, emails, phone numbers, and other fields with natural limits.

### TEXT: Unlimited Text

`TEXT` stores text of any length with no specified limit.

```sql
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    content TEXT
);
```

**When to use:** When you do not need a length limit. Good for descriptions, comments, blog content, and notes.

### VARCHAR vs TEXT: The Great Debate

In PostgreSQL, `VARCHAR` without a length limit (just `VARCHAR`) and `TEXT` are **identical in performance.** There is no speed difference.

```
+---------------------------+-----------------------------------------+
| Use This                  | When                                    |
+---------------------------+-----------------------------------------+
| VARCHAR(n) with a limit   | You want the database to enforce a      |
|                           |   maximum length (e.g., username max 30)|
+---------------------------+-----------------------------------------+
| TEXT                      | You do not need a length limit           |
|                           | (e.g., blog post content, comments)    |
+---------------------------+-----------------------------------------+
| CHAR(n)                   | Every value is exactly n characters      |
|                           | (e.g., country codes, zip codes)       |
+---------------------------+-----------------------------------------+
```

> **Common Mistake:** Using `VARCHAR(255)` everywhere "just in case." This is a habit from MySQL, where there was a performance difference. In PostgreSQL, there is no reason to do this. Use `TEXT` if you do not need a limit, or use `VARCHAR(n)` with a meaningful limit.

---

## BOOLEAN: True or False

The **BOOLEAN** type stores true/false values.

```
+---------------------------+-----------------------------------+
| Valid TRUE Values          | Valid FALSE Values                |
+---------------------------+-----------------------------------+
| TRUE, 't', 'true',        | FALSE, 'f', 'false',             |
| 'yes', 'y', '1', 'on'    | 'no', 'n', '0', 'off'           |
+---------------------------+-----------------------------------+
```

In psql output, TRUE is displayed as `t` and FALSE as `f`.

### Example

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    is_urgent BOOLEAN DEFAULT FALSE
);

INSERT INTO tasks (title, is_completed, is_urgent)
VALUES
    ('Write report', FALSE, TRUE),
    ('Buy groceries', FALSE, FALSE),
    ('Submit homework', TRUE, FALSE);
```

```sql
SELECT * FROM tasks;
```

```
 id |      title      | is_completed | is_urgent
----+-----------------+--------------+-----------
  1 | Write report    | f            | t
  2 | Buy groceries   | f            | f
  3 | Submit homework | t            | f
(3 rows)
```

### Filtering by BOOLEAN

```sql
-- Find all incomplete tasks
SELECT * FROM tasks WHERE is_completed = FALSE;

-- Shorter way (same result):
SELECT * FROM tasks WHERE NOT is_completed;
```

```
 id |     title     | is_completed | is_urgent
----+---------------+--------------+-----------
  1 | Write report  | f            | t
  2 | Buy groceries | f            | f
(2 rows)
```

---

## Date and Time Types

PostgreSQL has rich support for dates and times.

```
+-------------+-----------------------------+---------------------------+
| Type        | What It Stores              | Example                   |
+-------------+-----------------------------+---------------------------+
| DATE        | Calendar date only          | '2024-06-15'              |
| TIME        | Time of day only            | '14:30:00'                |
| TIMESTAMP   | Date and time combined      | '2024-06-15 14:30:00'     |
| TIMESTAMPTZ | Date, time, and timezone    | '2024-06-15 14:30:00-05'  |
| INTERVAL    | A duration of time          | '3 days', '2 hours'       |
+-------------+-----------------------------+---------------------------+
```

### DATE

Stores a calendar date in the format `YYYY-MM-DD`.

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(100),
    event_date DATE
);

INSERT INTO events (event_name, event_date)
VALUES ('Conference', '2024-09-15');
```

```sql
SELECT * FROM events;
```

```
 id | event_name | event_date
----+------------+------------
  1 | Conference | 2024-09-15
(1 row)
```

### TIME

Stores a time of day without a date.

```sql
ALTER TABLE events ADD COLUMN start_time TIME;

UPDATE events SET start_time = '09:00:00' WHERE id = 1;
```

```sql
SELECT * FROM events;
```

```
 id | event_name | event_date | start_time
----+------------+------------+------------
  1 | Conference | 2024-09-15 | 09:00:00
(1 row)
```

### TIMESTAMP

Stores both date and time together.

```sql
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO logs (message) VALUES ('User logged in');
INSERT INTO logs (message) VALUES ('Page viewed');
```

```sql
SELECT * FROM logs;
```

```
 id |    message     |         created_at
----+----------------+----------------------------
  1 | User logged in | 2024-06-15 14:32:15.123456
  2 | Page viewed    | 2024-06-15 14:32:16.789012
(2 rows)
```

> **Best Practice:** Use `TIMESTAMPTZ` (timestamp with time zone) instead of plain `TIMESTAMP` when your application has users in different time zones. `TIMESTAMPTZ` stores the time zone information, so a time entered in New York is correctly displayed in Tokyo.

### INTERVAL

An INTERVAL represents a duration of time, not a specific point in time.

```sql
SELECT CURRENT_DATE + INTERVAL '30 days' AS thirty_days_from_now;
```

```
 thirty_days_from_now
----------------------
 2024-07-15
(1 row)
```

```sql
SELECT CURRENT_TIMESTAMP + INTERVAL '2 hours 30 minutes' AS later;
```

```
            later
----------------------------
 2024-06-15 17:02:15.123456
(1 row)
```

Intervals are great for calculating due dates, expiration dates, and time differences.

### Useful Date Functions

```
+-------------------------------+-------------------------------+
| Function                      | What It Returns               |
+-------------------------------+-------------------------------+
| CURRENT_DATE                  | Today's date                  |
| CURRENT_TIME                  | Current time                  |
| CURRENT_TIMESTAMP             | Current date and time         |
| NOW()                         | Same as CURRENT_TIMESTAMP     |
| AGE(date)                     | Time elapsed since that date  |
| EXTRACT(YEAR FROM date)       | The year from a date          |
| DATE_TRUNC('month', date)     | Truncate to the first of      |
|                               |   the month                   |
+-------------------------------+-------------------------------+
```

### Example with Date Functions

```sql
SELECT
    CURRENT_DATE AS today,
    CURRENT_DATE + INTERVAL '7 days' AS next_week,
    EXTRACT(YEAR FROM CURRENT_DATE) AS current_year,
    EXTRACT(MONTH FROM CURRENT_DATE) AS current_month;
```

```
   today    | next_week  | current_year | current_month
------------+------------+--------------+---------------
 2024-06-15 | 2024-06-22 |         2024 |             6
(1 row)
```

---

## UUID: Universally Unique Identifiers

A **UUID** (Universally Unique Identifier) is a 128-bit number used as a unique identifier. It looks like this:

```
550e8400-e29b-41d4-a716-446655440000
```

**Think of it as:** A super-long, random ID that is virtually guaranteed to be unique across all computers everywhere, forever.

### Why Use UUID Instead of SERIAL?

```
+------------------+----------------------------------+
| SERIAL           | UUID                             |
+------------------+----------------------------------+
| Simple: 1, 2, 3  | Complex: 550e8400-e29b-...       |
| Predictable      | Random, unpredictable            |
| Unique per table | Unique globally                  |
| Smaller (4 bytes)| Larger (16 bytes)                |
| Easy to guess    | Impossible to guess              |
+------------------+----------------------------------+
```

Use UUID when:
- You need IDs that are unique across multiple databases or systems.
- You do not want people to guess IDs (security).
- You are building distributed systems.

### Example

```sql
-- Enable the UUID extension (one time per database)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE api_keys (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    key_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO api_keys (key_name) VALUES ('Production Key');
INSERT INTO api_keys (key_name) VALUES ('Development Key');
```

```sql
SELECT * FROM api_keys;
```

```
                  id                  |    key_name     |         created_at
--------------------------------------+-----------------+----------------------------
 a1b2c3d4-e5f6-7890-abcd-ef1234567890 | Production Key  | 2024-06-15 14:35:00.000000
 f9e8d7c6-b5a4-3210-fedc-ba9876543210 | Development Key | 2024-06-15 14:35:01.000000
(2 rows)
```

> **Note:** PostgreSQL 13 and later also supports `gen_random_uuid()` without needing the extension.

---

## JSON and JSONB: Structured Data in a Column

**JSON** (JavaScript Object Notation) is a format for storing structured data. PostgreSQL lets you store JSON directly in a column.

There are two types:

```
+--------+----------------------------------------------+
| Type   | Description                                  |
+--------+----------------------------------------------+
| JSON   | Stores JSON as plain text. Preserves         |
|        |   formatting and duplicate keys.             |
+--------+----------------------------------------------+
| JSONB  | Stores JSON in a binary format. Faster       |
|        |   for queries, supports indexing.             |
+--------+----------------------------------------------+
```

**Always use JSONB.** It is faster for reading and supports indexing. The only reason to use JSON is if you need to preserve the exact formatting of the input (which is rare).

### Example

```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    preferences JSONB
);

INSERT INTO user_profiles (username, preferences)
VALUES (
    'alice',
    '{"theme": "dark", "language": "en", "notifications": {"email": true, "sms": false}}'
);

INSERT INTO user_profiles (username, preferences)
VALUES (
    'bob',
    '{"theme": "light", "language": "es", "notifications": {"email": false, "sms": true}}'
);
```

```sql
SELECT * FROM user_profiles;
```

```
 id | username |                                    preferences
----+----------+------------------------------------------------------------------------------------
  1 | alice    | {"theme": "dark", "language": "en", "notifications": {"email": true, "sms": false}}
  2 | bob      | {"theme": "light", "language": "es", "notifications": {"email": false, "sms": true}}
(2 rows)
```

### Querying JSON Data

You can query inside JSON columns using the `->` and `->>` operators:

```sql
-- Get the theme (as JSON)
SELECT username, preferences -> 'theme' AS theme
FROM user_profiles;
```

```
 username | theme
----------+--------
 alice    | "dark"
 bob      | "light"
(2 rows)
```

```sql
-- Get the theme (as text, without quotes)
SELECT username, preferences ->> 'theme' AS theme
FROM user_profiles;
```

```
 username | theme
----------+-------
 alice    | dark
 bob      | light
(2 rows)
```

The difference: `->` returns JSON (with quotes). `->>` returns plain text (without quotes).

### When to Use JSONB

- Storing user preferences or settings.
- Storing data with a flexible structure that varies from row to row.
- Storing API responses.
- **Not** for core business data. If every row has the same fields, use regular columns instead.

---

## ARRAY: Storing Lists in a Column

PostgreSQL lets you store arrays (ordered lists) in a column. This is a feature most other databases do not have.

### Example

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    hobbies TEXT[],
    scores INTEGER[]
);

INSERT INTO students (name, hobbies, scores)
VALUES ('Alice', ARRAY['reading', 'swimming', 'coding'], ARRAY[95, 88, 92]);

INSERT INTO students (name, hobbies, scores)
VALUES ('Bob', ARRAY['gaming', 'cooking'], ARRAY[78, 85, 90, 88]);
```

```sql
SELECT * FROM students;
```

```
 id | name  |         hobbies          |    scores
----+-------+--------------------------+---------------
  1 | Alice | {reading,swimming,coding}| {95,88,92}
  2 | Bob   | {gaming,cooking}         | {78,85,90,88}
(2 rows)
```

### Accessing Array Elements

Arrays in PostgreSQL are 1-indexed (they start counting at 1, not 0):

```sql
-- Get the first hobby
SELECT name, hobbies[1] AS first_hobby FROM students;
```

```
 name  | first_hobby
-------+-------------
 Alice | reading
 Bob   | gaming
(2 rows)
```

### Searching Inside Arrays

```sql
-- Find students who have 'coding' as a hobby
SELECT name FROM students WHERE 'coding' = ANY(hobbies);
```

```
 name
-------
 Alice
(1 row)
```

### When to Use Arrays

- Storing tags or categories.
- Storing a short list of values that belong to one record.
- **Not** for large or complex lists. If you need to query or filter by individual items often, use a separate table instead.

---

## Choosing the Right Data Type

Here is a decision guide to help you choose the right type for any column:

```
+---------------------------+-------------------+----------------------------+
| What You Are Storing      | Recommended Type  | Notes                      |
+---------------------------+-------------------+----------------------------+
| Primary key (auto)        | SERIAL            | BIGSERIAL for huge tables  |
| Primary key (manual)      | UUID              | For distributed systems    |
| Person's age              | SMALLINT          | Range: 0-150               |
| Quantity of items         | INTEGER           | Or SMALLINT for small qty  |
| Money / prices            | NUMERIC(10,2)     | NEVER use FLOAT for money  |
| GPA / rating              | NUMERIC(3,2)      | Small precise decimal      |
| Short text (name, email)  | VARCHAR(n)        | Set a meaningful limit     |
| Long text (description)   | TEXT              | No need for a limit        |
| Fixed-length code         | CHAR(n)           | Country code, zip code     |
| Yes/No flag               | BOOLEAN           | DEFAULT FALSE or TRUE      |
| Calendar date             | DATE              | YYYY-MM-DD                 |
| Time of day               | TIME              | HH:MM:SS                   |
| Date + time               | TIMESTAMPTZ       | Always with time zone      |
| Duration                  | INTERVAL          | '3 days', '2 hours'        |
| Globally unique ID        | UUID              | uuid_generate_v4()         |
| Flexible/nested data      | JSONB             | Preferences, metadata      |
| Short list of values      | ARRAY             | Tags, scores               |
+---------------------------+-------------------+----------------------------+
```

### The Golden Rules

1. **Use INTEGER for most whole numbers.** Only use SMALLINT or BIGINT when you have a specific reason.
2. **Use NUMERIC for money. Always.** Never FLOAT, never REAL, never DOUBLE PRECISION.
3. **Use TEXT for text without a size limit.** Use VARCHAR(n) only when you need to enforce a maximum length.
4. **Use TIMESTAMPTZ, not TIMESTAMP.** Always store time zones. You will thank yourself later.
5. **Use BOOLEAN for yes/no values.** Do not use INTEGER (0/1) or VARCHAR ('yes'/'no').

---

## Common Mistakes

1. **Using FLOAT or REAL for money.** This leads to rounding errors. Always use `NUMERIC(10,2)` or similar for financial data.

   ```sql
   -- BAD: Will cause rounding errors
   price FLOAT

   -- GOOD: Exact decimal
   price NUMERIC(10,2)
   ```

2. **Using VARCHAR(255) for everything.** This is a MySQL habit. In PostgreSQL, VARCHAR without a limit and TEXT are identical in performance. Use TEXT if you do not need a limit.

   ```sql
   -- Unnecessary in PostgreSQL
   description VARCHAR(255)

   -- Better: use TEXT if no limit needed
   description TEXT

   -- Better: use VARCHAR with a meaningful limit
   username VARCHAR(30)
   ```

3. **Using CHAR when VARCHAR would be better.** CHAR pads with spaces, which can cause unexpected behavior when comparing strings. Only use CHAR for truly fixed-length data like country codes.

4. **Using TIMESTAMP instead of TIMESTAMPTZ.** If your application has users in different time zones, plain TIMESTAMP loses time zone information and leads to bugs.

5. **Storing dates as strings.** If you store a date as VARCHAR ('June 15, 2024'), you cannot sort by date, calculate differences, or use date functions. Always use the DATE type.

   ```sql
   -- BAD: Cannot sort or compare properly
   event_date VARCHAR(20)

   -- GOOD: Full date functionality
   event_date DATE
   ```

6. **Using BIGINT when INTEGER is enough.** BIGINT uses twice the storage (8 bytes vs 4 bytes). For a table with millions of rows, this adds up. Use INTEGER unless you genuinely need numbers larger than 2 billion.

---

## Best Practices

1. **Match the type to the data.** Ages are SMALLINT. Prices are NUMERIC. Names are VARCHAR with a limit. Descriptions are TEXT. Do not overthink it, but do not use the same type for everything.

2. **Use NUMERIC for any financial calculation.** There are no exceptions. Money must be exact.

3. **Set meaningful VARCHAR limits.** If an email address can be at most 254 characters (per the email standard), use VARCHAR(254). If a name can be at most 100 characters, use VARCHAR(100).

4. **Use BOOLEAN instead of tricks.** Do not use an INTEGER column with 0 and 1 to represent true/false. PostgreSQL has a proper BOOLEAN type. Use it.

5. **Prefer TIMESTAMPTZ for timestamps.** Always include time zone information unless you have a very specific reason not to.

6. **Use JSONB sparingly.** It is powerful, but overusing it defeats the purpose of a relational database. Use regular columns for core data and JSONB for truly flexible metadata.

7. **Use SERIAL for primary keys in most tables.** It is simple, efficient, and sufficient for the vast majority of applications.

---

## Quick Summary

PostgreSQL offers a rich set of data types. INTEGER, SMALLINT, and BIGINT store whole numbers of different sizes. SERIAL auto-increments for primary keys. NUMERIC provides exact decimal storage and must be used for money. VARCHAR(n) enforces a maximum text length, while TEXT has no limit. BOOLEAN stores true/false values. DATE, TIME, TIMESTAMP, and INTERVAL handle dates and durations. UUID provides globally unique identifiers. JSONB stores flexible structured data, and ARRAY stores ordered lists. Choosing the right type prevents data loss, rounding errors, and wasted space.

---

## Key Points

- **INTEGER** is the default for whole numbers. Use **SMALLINT** for small ranges and **BIGINT** for very large numbers.
- **SERIAL** auto-increments and is perfect for primary keys.
- **NUMERIC(p,s)** stores exact decimals. **Always use it for money.**
- **VARCHAR(n)** limits text length. **TEXT** has no limit. Both perform the same in PostgreSQL.
- **CHAR(n)** is fixed-length and pads with spaces. Use it rarely.
- **BOOLEAN** stores TRUE or FALSE.
- **DATE** stores a date. **TIMESTAMPTZ** stores date, time, and timezone.
- **INTERVAL** represents a duration like '3 days' or '2 hours'.
- **UUID** provides globally unique identifiers.
- **JSONB** stores flexible structured data. Use it for metadata, not core data.
- **ARRAY** stores lists. Use separate tables for large or frequently queried lists.
- **Never use FLOAT for money.** This cannot be stressed enough.

---

## Practice Questions

1. You are storing product prices that can range from $0.01 to $99,999.99. What data type and parameters would you use?

2. What is the difference between VARCHAR(100) and TEXT in PostgreSQL? When would you use each?

3. Why is it dangerous to use FLOAT for financial calculations? Give an example of what could go wrong.

4. What is the difference between TIMESTAMP and TIMESTAMPTZ? When should you use each?

5. You have a column that stores a student's grade letter (A, B, C, D, F). Would you use CHAR(1), VARCHAR(2), or TEXT? Why?

---

## Exercises

### Exercise 1: Design a Product Catalog

Create a table called `products` with appropriate data types for:
- A unique auto-incrementing ID
- Product name (max 150 characters, required)
- Description (no length limit)
- Price (exact, up to $999,999.99)
- Stock quantity (will never exceed 10,000)
- Is available (yes/no, default yes)
- Weight in kilograms (up to 9999.99 kg)
- Release date
- Tags (a list of text tags)
- Created timestamp (auto-set)

Write the complete `CREATE TABLE` statement.

### Exercise 2: Fix the Bad Schema

The following table has several data type mistakes. Identify each mistake and write the corrected version:

```sql
CREATE TABLE bank_accounts (
    id VARCHAR(10) PRIMARY KEY,
    account_holder CHAR(255),
    balance FLOAT,
    is_active INTEGER,
    opened_date VARCHAR(20),
    account_type BOOLEAN
);
```

### Exercise 3: JSON Exploration

Create a table called `app_settings` with an id, app_name (VARCHAR), and config (JSONB) column. Insert two rows with different JSON structures in the config column. Then write a SELECT query that extracts a specific value from the JSON.

---

## What Is Next?

Now that you understand data types, it is time to fill your tables with data. In Chapter 6, you will learn how to **insert data** using INSERT INTO, insert multiple rows at once, use the RETURNING clause, handle conflicts with ON CONFLICT (upsert), and bulk load data with COPY. Your empty tables are about to come alive.
