# Chapter 18: String and Date Functions

## What You Will Learn

**String functions:**
- UPPER, LOWER — change letter case
- LENGTH — count characters
- TRIM, LTRIM, RTRIM — remove whitespace
- SUBSTRING — extract part of a string
- REPLACE — swap text within a string
- CONCAT and || — join strings together
- LEFT, RIGHT — extract from start or end
- POSITION — find where a substring occurs
- SPLIT_PART — split strings by a delimiter
- REGEXP_MATCHES — pattern matching with regular expressions

**Date functions:**
- CURRENT_DATE, CURRENT_TIMESTAMP — get the current date and time
- EXTRACT — pull out year, month, day, etc.
- DATE_TRUNC — truncate to a specific precision
- AGE — calculate the difference between dates
- Interval arithmetic — add and subtract time periods
- TO_CHAR — format dates as strings
- Casting strings to dates

## Why This Chapter Matters

Raw data in a database is rarely in the exact format you need. Customer names might be in all caps. Dates might need to be displayed in a specific format. You might need to extract the domain from an email address or calculate someone's age from their birth date.

String and date functions are the formatting and calculation tools of SQL. Think of them as the equivalent of text functions in a spreadsheet — UPPER, LOWER, LEFT, RIGHT, and date calculations. You will use these functions in almost every real-world query.

---

## Setting Up Practice Data

```sql
CREATE TABLE contacts (
    contact_id SERIAL PRIMARY KEY,
    full_name  VARCHAR(100),
    email      VARCHAR(100),
    phone      VARCHAR(20),
    birth_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO contacts (full_name, email, phone, birth_date, created_at) VALUES
('  Alice Johnson  ', 'ALICE@EXAMPLE.COM',   '555-123-4567', '1990-03-15', '2023-01-15 09:30:00'),
('bob smith',         'bob@example.com',     '555.987.6543', '1985-07-22', '2023-03-20 14:15:00'),
('Charlie Brown',     'charlie@GMAIL.COM',   '(555) 246-8101','1992-11-08', '2023-06-10 11:00:00'),
('DIANA LEE',         'diana@example.com',   '555 369 2580', '1988-01-30', '2024-01-05 16:45:00'),
('Eve Davis-Wilson',  'eve.davis@work.co.uk','555-111-2222', '1995-12-25', '2024-02-14 08:00:00');
```

---

## String Functions

### UPPER and LOWER — Change Letter Case

```sql
SELECT full_name,
       UPPER(full_name) AS upper_name,
       LOWER(full_name) AS lower_name
FROM contacts;
```

**Result:**

```
+--------------------+--------------------+--------------------+
| full_name          | upper_name         | lower_name         |
+--------------------+--------------------+--------------------+
|   Alice Johnson    |   ALICE JOHNSON    |   alice johnson    |
| bob smith          | BOB SMITH          | bob smith          |
| Charlie Brown      | CHARLIE BROWN      | charlie brown      |
| DIANA LEE          | DIANA LEE          | diana lee          |
| Eve Davis-Wilson   | EVE DAVIS-WILSON   | eve davis-wilson   |
+--------------------+--------------------+--------------------+
(5 rows)
```

**Common use:** Standardizing data for comparison.

```sql
-- Case-insensitive search
SELECT full_name FROM contacts
WHERE LOWER(full_name) LIKE '%alice%';
```

### INITCAP — Title Case

```sql
SELECT full_name,
       INITCAP(full_name) AS title_case
FROM contacts;
```

**Result:**

```
+--------------------+--------------------+
| full_name          | title_case         |
+--------------------+--------------------+
|   Alice Johnson    |   Alice Johnson    |
| bob smith          | Bob Smith          |
| Charlie Brown      | Charlie Brown      |
| DIANA LEE          | Diana Lee          |
| Eve Davis-Wilson   | Eve Davis-Wilson   |
+--------------------+--------------------+
(5 rows)
```

INITCAP capitalizes the first letter of each word and lowercases the rest.

---

### LENGTH — Count Characters

```sql
SELECT full_name,
       LENGTH(full_name) AS name_length,
       LENGTH(TRIM(full_name)) AS trimmed_length
FROM contacts;
```

**Result:**

```
+--------------------+-------------+----------------+
| full_name          | name_length | trimmed_length |
+--------------------+-------------+----------------+
|   Alice Johnson    |          18 |             14 |
| bob smith          |           9 |              9 |
| Charlie Brown      |          13 |             13 |
| DIANA LEE          |           9 |              9 |
| Eve Davis-Wilson   |          16 |             16 |
+--------------------+-------------+----------------+
(5 rows)
```

Notice that Alice Johnson's name has leading and trailing spaces, making it 18 characters instead of 14.

---

### TRIM, LTRIM, RTRIM — Remove Whitespace

```sql
SELECT full_name,
       TRIM(full_name) AS trimmed,
       LTRIM(full_name) AS left_trimmed,
       RTRIM(full_name) AS right_trimmed
FROM contacts
WHERE full_name LIKE ' %' OR full_name LIKE '% ';
```

**Result:**

```
+--------------------+----------------+------------------+-------------------+
| full_name          | trimmed        | left_trimmed     | right_trimmed     |
+--------------------+----------------+------------------+-------------------+
|   Alice Johnson    | Alice Johnson  | Alice Johnson    |   Alice Johnson   |
+--------------------+----------------+------------------+-------------------+
(1 row)
```

- `TRIM` removes spaces from both sides
- `LTRIM` removes spaces from the left only
- `RTRIM` removes spaces from the right only

You can also trim specific characters:

```sql
SELECT TRIM(BOTH '-' FROM '--hello--') AS result;
-- Result: hello
```

---

### SUBSTRING — Extract Part of a String

SUBSTRING extracts a portion of a string by position and length.

```sql
-- SUBSTRING(string FROM start FOR length)
-- or: SUBSTRING(string, start, length)

SELECT email,
       SUBSTRING(email FROM 1 FOR 5) AS first_five,
       SUBSTRING(email, 1, POSITION('@' IN email) - 1) AS username
FROM contacts;
```

**Result:**

```
+----------------------+------------+-----------+
| email                | first_five | username  |
+----------------------+------------+-----------+
| ALICE@EXAMPLE.COM    | ALICE      | ALICE     |
| bob@example.com      | bob@e      | bob       |
| charlie@GMAIL.COM    | charl      | charlie   |
| diana@example.com    | diana      | diana     |
| eve.davis@work.co.uk | eve.d      | eve.davis |
+----------------------+------------+-----------+
(5 rows)
```

### Line-by-Line Explanation

```
SUBSTRING(email FROM 1 FOR 5)                   -- Characters 1 through 5
SUBSTRING(email, 1, POSITION('@' IN email) - 1) -- From char 1 to the char
                                                 -- before the @ symbol
```

---

### REPLACE — Swap Text

```sql
SELECT phone,
       REPLACE(phone, '-', '') AS no_dashes,
       REPLACE(REPLACE(REPLACE(phone, '-', ''), '.', ''), ' ', '') AS digits_only
FROM contacts;
```

**Result:**

```
+----------------+-------------+-------------+
| phone          | no_dashes   | digits_only |
+----------------+-------------+-------------+
| 555-123-4567   | 5551234567  | 5551234567  |
| 555.987.6543   | 555.987.6543| 5559876543  |
| (555) 246-8101 | (555) 2468101| (555)2468101|
| 555 369 2580   | 555 369 2580| 5553692580  |
| 555-111-2222   | 5551112222  | 5551112222  |
+----------------+-------------+-------------+
(5 rows)
```

REPLACE is case-sensitive and replaces **all** occurrences of the search string.

---

### CONCAT and || — Join Strings Together

PostgreSQL offers two ways to concatenate strings:

```sql
SELECT CONCAT('Hello', ' ', 'World') AS using_concat,
       'Hello' || ' ' || 'World' AS using_pipes;
```

**Result:**

```
+--------------+-------------+
| using_concat | using_pipes |
+--------------+-------------+
| Hello World  | Hello World |
+--------------+-------------+
```

**Key difference:** `||` returns NULL if any part is NULL. `CONCAT` treats NULL as an empty string.

```sql
SELECT CONCAT('Hello', NULL, 'World') AS concat_result,
       'Hello' || NULL || 'World' AS pipe_result;
```

**Result:**

```
+---------------+-------------+
| concat_result | pipe_result |
+---------------+-------------+
| HelloWorld    | NULL        |
+---------------+-------------+
```

Use `CONCAT` when NULLs are possible and you do not want the entire result to become NULL.

---

### LEFT and RIGHT — Extract from Start or End

```sql
SELECT email,
       LEFT(email, 3) AS first_three,
       RIGHT(email, 3) AS last_three
FROM contacts;
```

**Result:**

```
+----------------------+-------------+------------+
| email                | first_three | last_three |
+----------------------+-------------+------------+
| ALICE@EXAMPLE.COM    | ALI         | COM        |
| bob@example.com      | bob         | com        |
| charlie@GMAIL.COM    | cha         | COM        |
| diana@example.com    | dia         | com        |
| eve.davis@work.co.uk | eve         | .uk        |
+----------------------+-------------+------------+
(5 rows)
```

---

### POSITION — Find Where a Substring Occurs

POSITION returns the index of the first occurrence of a substring. Returns 0 if not found.

```sql
SELECT email,
       POSITION('@' IN email) AS at_position,
       POSITION('.' IN email) AS dot_position
FROM contacts;
```

**Result:**

```
+----------------------+-------------+--------------+
| email                | at_position | dot_position |
+----------------------+-------------+--------------+
| ALICE@EXAMPLE.COM    |           6 |           14 |
| bob@example.com      |           4 |            12|
| charlie@GMAIL.COM    |           8 |           14 |
| diana@example.com    |           6 |           14 |
| eve.davis@work.co.uk |          10 |            4 |
+----------------------+-------------+--------------+
(5 rows)
```

### Practical: Extract Domain from Email

```sql
SELECT email,
       SUBSTRING(email FROM POSITION('@' IN email) + 1) AS domain
FROM contacts;
```

**Result:**

```
+----------------------+--------------+
| email                | domain       |
+----------------------+--------------+
| ALICE@EXAMPLE.COM    | EXAMPLE.COM  |
| bob@example.com      | example.com  |
| charlie@GMAIL.COM    | GMAIL.COM    |
| diana@example.com    | example.com  |
| eve.davis@work.co.uk | work.co.uk   |
+----------------------+--------------+
(5 rows)
```

---

### SPLIT_PART — Split Strings by a Delimiter

SPLIT_PART splits a string by a delimiter and returns the Nth part.

```sql
-- SPLIT_PART(string, delimiter, position)

SELECT email,
       SPLIT_PART(email, '@', 1) AS username,
       SPLIT_PART(email, '@', 2) AS domain
FROM contacts;
```

**Result:**

```
+----------------------+-----------+--------------+
| email                | username  | domain       |
+----------------------+-----------+--------------+
| ALICE@EXAMPLE.COM    | ALICE     | EXAMPLE.COM  |
| bob@example.com      | bob       | example.com  |
| charlie@GMAIL.COM    | charlie   | GMAIL.COM    |
| diana@example.com    | diana     | example.com  |
| eve.davis@work.co.uk | eve.davis | work.co.uk   |
+----------------------+-----------+--------------+
(5 rows)
```

SPLIT_PART is often more readable than SUBSTRING + POSITION for splitting strings.

```sql
-- Splitting a phone number
SELECT phone,
       SPLIT_PART(phone, '-', 1) AS area_code,
       SPLIT_PART(phone, '-', 2) AS prefix,
       SPLIT_PART(phone, '-', 3) AS line_number
FROM contacts
WHERE phone LIKE '%-%-%';
```

**Result:**

```
+--------------+-----------+--------+-------------+
| phone        | area_code | prefix | line_number |
+--------------+-----------+--------+-------------+
| 555-123-4567 | 555       | 123    | 4567        |
| 555-111-2222 | 555       | 111    | 2222        |
+--------------+-----------+--------+-------------+
(2 rows)
```

---

### REGEXP_MATCHES — Pattern Matching with Regular Expressions

For complex pattern matching, PostgreSQL supports regular expressions.

```sql
-- Extract numbers from phone numbers
SELECT phone,
       (REGEXP_MATCHES(phone, '\d+', 'g')) AS number_parts
FROM contacts;
```

**Result:**

```
+----------------+--------------+
| phone          | number_parts |
+----------------+--------------+
| 555-123-4567   | {555}        |
| 555-123-4567   | {123}        |
| 555-123-4567   | {4567}       |
| 555.987.6543   | {555}        |
| ...            | ...          |
+----------------+--------------+
```

The `'g'` flag means "global" — find all matches, not just the first.

A simpler approach for checking patterns is the `~` operator:

```sql
-- Find emails that end with .com (case-insensitive)
SELECT email
FROM contacts
WHERE email ~* '\.com$';
```

**Result:**

```
+----------------------+
| email                |
+----------------------+
| ALICE@EXAMPLE.COM    |
| bob@example.com      |
| charlie@GMAIL.COM    |
| diana@example.com    |
+----------------------+
(4 rows)
```

- `~` is case-sensitive regex match
- `~*` is case-insensitive regex match
- `!~` is case-sensitive regex NOT match
- `!~*` is case-insensitive regex NOT match

---

## String Functions Quick Reference

```
+---------------+--------------------------------+--------------------+
| Function      | What It Does                   | Example            |
+---------------+--------------------------------+--------------------+
| UPPER(s)      | All uppercase                  | 'hello' -> 'HELLO' |
| LOWER(s)      | All lowercase                  | 'HELLO' -> 'hello' |
| INITCAP(s)    | Title Case                     | 'bob smith'->'Bob Smith'|
| LENGTH(s)     | Character count                | 'hello' -> 5       |
| TRIM(s)       | Remove leading/trailing spaces | ' hi ' -> 'hi'    |
| SUBSTRING     | Extract part of string         | 'hello',2,3->'ell' |
| REPLACE(s,a,b)| Replace a with b               | 'hello','l','r'->'herro'|
| CONCAT(a,b)   | Join strings (NULL-safe)       | 'a','b' -> 'ab'    |
| a || b        | Join strings (NULL=NULL)       | 'a'||'b' -> 'ab'   |
| LEFT(s,n)     | First n characters             | 'hello',3 -> 'hel' |
| RIGHT(s,n)    | Last n characters              | 'hello',3 -> 'llo' |
| POSITION(a IN b)| Find substring position      | '@' IN 'a@b' -> 2  |
| SPLIT_PART    | Split by delimiter, get Nth    | 'a-b-c','-',2->'b' |
| REGEXP_MATCHES| Regex pattern matching         | Find complex patterns|
+---------------+--------------------------------+--------------------+
```

---

## Date Functions

### CURRENT_DATE and CURRENT_TIMESTAMP

```sql
SELECT CURRENT_DATE      AS today,
       CURRENT_TIMESTAMP AS right_now,
       NOW()             AS also_right_now;
```

**Result:**

```
+------------+----------------------------+----------------------------+
| today      | right_now                  | also_right_now             |
+------------+----------------------------+----------------------------+
| 2024-06-15 | 2024-06-15 14:30:45.123456 | 2024-06-15 14:30:45.123456 |
+------------+----------------------------+----------------------------+
```

- `CURRENT_DATE` returns just the date (no time)
- `CURRENT_TIMESTAMP` and `NOW()` return date + time with microseconds

> **Note:** These return the current date and time when the query runs. Your results will differ from the examples shown here.

---

### EXTRACT — Pull Out Parts of a Date

EXTRACT lets you get specific parts (year, month, day, hour, etc.) from a date or timestamp.

```sql
SELECT full_name,
       birth_date,
       EXTRACT(YEAR  FROM birth_date) AS birth_year,
       EXTRACT(MONTH FROM birth_date) AS birth_month,
       EXTRACT(DAY   FROM birth_date) AS birth_day,
       EXTRACT(DOW   FROM birth_date) AS day_of_week
FROM contacts;
```

**Result:**

```
+--------------------+------------+------------+-------------+-----------+-------------+
| full_name          | birth_date | birth_year | birth_month | birth_day | day_of_week |
+--------------------+------------+------------+-------------+-----------+-------------+
|   Alice Johnson    | 1990-03-15 |       1990 |           3 |        15 |           4 |
| bob smith          | 1985-07-22 |       1985 |           7 |        22 |           1 |
| Charlie Brown      | 1992-11-08 |       1992 |          11 |         8 |           0 |
| DIANA LEE          | 1988-01-30 |       1988 |           1 |        30 |           6 |
| Eve Davis-Wilson   | 1995-12-25 |       1995 |          12 |        25 |           1 |
+--------------------+------------+------------+-------------+-----------+-------------+
(5 rows)
```

**Day of week values (DOW):**

```
0 = Sunday
1 = Monday
2 = Tuesday
3 = Wednesday
4 = Thursday
5 = Friday
6 = Saturday
```

### Practical: Group by Month

```sql
SELECT EXTRACT(MONTH FROM created_at) AS month,
       COUNT(*) AS signups
FROM contacts
GROUP BY EXTRACT(MONTH FROM created_at)
ORDER BY month;
```

**Result:**

```
+-------+---------+
| month | signups |
+-------+---------+
|     1 |       2 |
|     2 |       1 |
|     3 |       1 |
|     6 |       1 |
+-------+---------+
(4 rows)
```

---

### DATE_TRUNC — Truncate to a Specific Precision

DATE_TRUNC rounds a date/timestamp down to the specified precision.

```sql
SELECT created_at,
       DATE_TRUNC('year',  created_at) AS trunc_year,
       DATE_TRUNC('month', created_at) AS trunc_month,
       DATE_TRUNC('day',   created_at) AS trunc_day
FROM contacts;
```

**Result:**

```
+---------------------+---------------------+---------------------+---------------------+
| created_at          | trunc_year          | trunc_month         | trunc_day           |
+---------------------+---------------------+---------------------+---------------------+
| 2023-01-15 09:30:00 | 2023-01-01 00:00:00 | 2023-01-01 00:00:00 | 2023-01-15 00:00:00 |
| 2023-03-20 14:15:00 | 2023-01-01 00:00:00 | 2023-03-01 00:00:00 | 2023-03-20 00:00:00 |
| 2023-06-10 11:00:00 | 2023-01-01 00:00:00 | 2023-06-01 00:00:00 | 2023-06-10 00:00:00 |
| 2024-01-05 16:45:00 | 2024-01-01 00:00:00 | 2024-01-01 00:00:00 | 2024-01-05 00:00:00 |
| 2024-02-14 08:00:00 | 2024-01-01 00:00:00 | 2024-02-01 00:00:00 | 2024-02-14 00:00:00 |
+---------------------+---------------------+---------------------+---------------------+
(5 rows)
```

DATE_TRUNC is extremely useful for grouping by time periods:

```sql
-- Count signups per month
SELECT DATE_TRUNC('month', created_at) AS month,
       COUNT(*) AS signups
FROM contacts
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month;
```

**Result:**

```
+---------------------+---------+
| month               | signups |
+---------------------+---------+
| 2023-01-01 00:00:00 |       1 |
| 2023-03-01 00:00:00 |       1 |
| 2023-06-01 00:00:00 |       1 |
| 2024-01-01 00:00:00 |       1 |
| 2024-02-01 00:00:00 |       1 |
+---------------------+---------+
(5 rows)
```

---

### AGE — Calculate the Difference Between Dates

AGE returns the difference between two dates as an interval.

```sql
SELECT full_name,
       birth_date,
       AGE(birth_date) AS age
FROM contacts;
```

**Result:**

```
+--------------------+------------+---------------------------+
| full_name          | birth_date | age                       |
+--------------------+------------+---------------------------+
|   Alice Johnson    | 1990-03-15 | 34 years 3 mons 0 days    |
| bob smith          | 1985-07-22 | 38 years 10 mons 23 days  |
| Charlie Brown      | 1992-11-08 | 31 years 7 mons 7 days    |
| DIANA LEE          | 1988-01-30 | 36 years 4 mons 15 days   |
| Eve Davis-Wilson   | 1995-12-25 | 28 years 5 mons 20 days   |
+--------------------+------------+---------------------------+
(5 rows)
```

> **Note:** Your results will differ because AGE calculates from the current date.

You can also calculate the age between two specific dates:

```sql
SELECT AGE('2024-06-15', '2023-01-15') AS time_between;
-- Result: 1 year 5 mons 0 days
```

### Extract Just the Years from AGE

```sql
SELECT TRIM(full_name) AS name,
       birth_date,
       EXTRACT(YEAR FROM AGE(birth_date)) AS age_years
FROM contacts;
```

**Result:**

```
+------------------+------------+-----------+
| name             | birth_date | age_years |
+------------------+------------+-----------+
| Alice Johnson    | 1990-03-15 |        34 |
| bob smith        | 1985-07-22 |        38 |
| Charlie Brown    | 1992-11-08 |        31 |
| DIANA LEE        | 1988-01-30 |        36 |
| Eve Davis-Wilson | 1995-12-25 |        28 |
+------------------+------------+-----------+
(5 rows)
```

---

### Interval Arithmetic — Add and Subtract Time Periods

In PostgreSQL, you can add or subtract intervals from dates and timestamps.

```sql
SELECT CURRENT_DATE AS today,
       CURRENT_DATE + INTERVAL '7 days' AS next_week,
       CURRENT_DATE - INTERVAL '1 month' AS last_month,
       CURRENT_DATE + INTERVAL '1 year' AS next_year;
```

**Result:**

```
+------------+------------+------------+------------+
| today      | next_week  | last_month | next_year  |
+------------+------------+------------+------------+
| 2024-06-15 | 2024-06-22 | 2024-05-15 | 2025-06-15 |
+------------+------------+------------+------------+
```

### Practical: Find Records from the Last 30 Days

```sql
SELECT TRIM(full_name) AS name,
       created_at
FROM contacts
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '30 days';
```

### Practical: Find Upcoming Birthdays (Next 30 Days)

```sql
SELECT TRIM(full_name) AS name,
       birth_date,
       EXTRACT(MONTH FROM birth_date) AS birth_month,
       EXTRACT(DAY FROM birth_date) AS birth_day
FROM contacts
WHERE (EXTRACT(MONTH FROM birth_date), EXTRACT(DAY FROM birth_date))
   IN (
       SELECT EXTRACT(MONTH FROM d), EXTRACT(DAY FROM d)
       FROM generate_series(
           CURRENT_DATE,
           CURRENT_DATE + INTERVAL '30 days',
           INTERVAL '1 day'
       ) AS d
   );
```

---

### Date Formatting with TO_CHAR

TO_CHAR converts a date or timestamp to a formatted string.

```sql
SELECT birth_date,
       TO_CHAR(birth_date, 'MM/DD/YYYY')    AS us_format,
       TO_CHAR(birth_date, 'DD-Mon-YYYY')   AS readable,
       TO_CHAR(birth_date, 'Day, Month DD, YYYY') AS full_format,
       TO_CHAR(birth_date, 'YYYY-MM-DD')    AS iso_format
FROM contacts;
```

**Result:**

```
+------------+------------+-------------+-----------------------------+------------+
| birth_date | us_format  | readable    | full_format                 | iso_format |
+------------+------------+-------------+-----------------------------+------------+
| 1990-03-15 | 03/15/1990 | 15-Mar-1990 | Thursday , March     15, 1990| 1990-03-15|
| 1985-07-22 | 07/22/1985 | 22-Jul-1985 | Monday   , July      22, 1985| 1985-07-22|
| 1992-11-08 | 11/08/1992 | 08-Nov-1992 | Sunday   , November  08, 1992| 1992-11-08|
| 1988-01-30 | 01/30/1988 | 30-Jan-1988 | Saturday , January   30, 1988| 1988-01-30|
| 1995-12-25 | 12/25/1995 | 25-Dec-1995 | Monday   , December  25, 1995| 1995-12-25|
+------------+------------+-------------+-----------------------------+------------+
(5 rows)
```

### Common TO_CHAR Format Codes

```
+--------+---------------------------+------------------+
| Code   | Meaning                   | Example          |
+--------+---------------------------+------------------+
| YYYY   | 4-digit year              | 2024             |
| YY     | 2-digit year              | 24               |
| MM     | Month number (01-12)      | 06               |
| Mon    | Abbreviated month name    | Jun              |
| Month  | Full month name           | June             |
| DD     | Day of month (01-31)      | 15               |
| Day    | Full day name             | Saturday         |
| Dy     | Abbreviated day name      | Sat              |
| HH24   | Hour (00-23)              | 14               |
| HH12   | Hour (01-12)              | 02               |
| MI     | Minute (00-59)            | 30               |
| SS     | Second (00-59)            | 45               |
| AM/PM  | AM or PM indicator        | PM               |
+--------+---------------------------+------------------+
```

### Formatting Timestamps

```sql
SELECT created_at,
       TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS iso_timestamp,
       TO_CHAR(created_at, 'Mon DD, YYYY at HH12:MI AM') AS readable
FROM contacts;
```

**Result:**

```
+---------------------+---------------------+----------------------------+
| created_at          | iso_timestamp       | readable                   |
+---------------------+---------------------+----------------------------+
| 2023-01-15 09:30:00 | 2023-01-15 09:30:00 | Jan 15, 2023 at 09:30 AM  |
| 2023-03-20 14:15:00 | 2023-03-20 14:15:00 | Mar 20, 2023 at 02:15 PM  |
| 2023-06-10 11:00:00 | 2023-06-10 11:00:00 | Jun 10, 2023 at 11:00 AM  |
| 2024-01-05 16:45:00 | 2024-01-05 16:45:00 | Jan 05, 2024 at 04:45 PM  |
| 2024-02-14 08:00:00 | 2024-02-14 08:00:00 | Feb 14, 2024 at 08:00 AM  |
+---------------------+---------------------+----------------------------+
(5 rows)
```

---

### Casting Strings to Dates

Sometimes you receive dates as strings and need to convert them to proper date types.

```sql
-- Using CAST
SELECT CAST('2024-06-15' AS DATE) AS cast_date;

-- Using :: shorthand (PostgreSQL-specific)
SELECT '2024-06-15'::DATE AS cast_date;

-- Using TO_DATE for custom formats
SELECT TO_DATE('15/06/2024', 'DD/MM/YYYY') AS parsed_date;
SELECT TO_DATE('June 15, 2024', 'Month DD, YYYY') AS parsed_date;
```

**Result:**

```
+------------+
| parsed_date|
+------------+
| 2024-06-15 |
+------------+
```

For timestamps:

```sql
SELECT TO_TIMESTAMP('2024-06-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS')
    AS parsed_timestamp;
```

---

## Practical Example: Contact Data Cleanup

Let us combine several string functions to clean up our contact data.

```sql
SELECT contact_id,
       INITCAP(TRIM(full_name)) AS clean_name,
       LOWER(email) AS clean_email,
       SPLIT_PART(LOWER(email), '@', 2) AS email_domain,
       REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS clean_phone,
       EXTRACT(YEAR FROM AGE(birth_date)) AS age,
       TO_CHAR(created_at, 'Mon DD, YYYY') AS joined
FROM contacts
ORDER BY clean_name;
```

**Result:**

```
+----+------------------+----------------------+--------------+-------------+-----+--------------+
| id | clean_name       | clean_email          | email_domain | clean_phone | age | joined       |
+----+------------------+----------------------+--------------+-------------+-----+--------------+
|  1 | Alice Johnson    | alice@example.com    | example.com  | 5551234567  |  34 | Jan 15, 2023 |
|  2 | Bob Smith        | bob@example.com      | example.com  | 5559876543  |  38 | Mar 20, 2023 |
|  3 | Charlie Brown    | charlie@gmail.com    | gmail.com    | 5552468101  |  31 | Jun 10, 2023 |
|  4 | Diana Lee        | diana@example.com    | example.com  | 5553692580  |  36 | Jan 05, 2024 |
|  5 | Eve Davis-Wilson | eve.davis@work.co.uk | work.co.uk   | 5551112222  |  28 | Feb 14, 2024 |
+----+------------------+----------------------+--------------+-------------+-----+--------------+
(5 rows)
```

This query:
- Trims whitespace and applies title case to names
- Lowercases all emails for consistency
- Extracts the email domain
- Strips non-numeric characters from phone numbers
- Calculates age from birth date
- Formats the sign-up date in a readable format

---

## Practical Example: Monthly Signup Report

```sql
SELECT TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') AS month,
       COUNT(*) AS new_contacts,
       STRING_AGG(INITCAP(TRIM(full_name)), ', ' ORDER BY full_name) AS names
FROM contacts
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month;
```

**Result:**

```
+---------+--------------+------------------------+
| month   | new_contacts | names                  |
+---------+--------------+------------------------+
| 2023-01 |            1 | Alice Johnson          |
| 2023-03 |            1 | Bob Smith              |
| 2023-06 |            1 | Charlie Brown          |
| 2024-01 |            1 | Diana Lee              |
| 2024-02 |            1 | Eve Davis-Wilson       |
+---------+--------------+------------------------+
(5 rows)
```

`STRING_AGG` concatenates values from multiple rows into a single string, separated by the delimiter you choose (`, ` in this case).

---

## Date Functions Quick Reference

```
+--------------------+-----------------------------------+-------------------------+
| Function           | What It Does                      | Example                 |
+--------------------+-----------------------------------+-------------------------+
| CURRENT_DATE       | Today's date                      | 2024-06-15              |
| CURRENT_TIMESTAMP  | Current date + time               | 2024-06-15 14:30:45     |
| NOW()              | Same as CURRENT_TIMESTAMP         | 2024-06-15 14:30:45     |
| EXTRACT(part FROM) | Get year, month, day, etc.        | EXTRACT(YEAR FROM d)    |
| DATE_TRUNC(prec,d) | Truncate to precision             | DATE_TRUNC('month', d)  |
| AGE(date)          | Time elapsed since date           | 34 years 3 mons        |
| AGE(d1, d2)        | Difference between two dates      | 1 year 5 mons           |
| + INTERVAL         | Add time to a date                | d + INTERVAL '7 days'   |
| - INTERVAL         | Subtract time from a date         | d - INTERVAL '1 month'  |
| TO_CHAR(d, fmt)    | Format date as string             | TO_CHAR(d, 'MM/DD/YYYY')|
| TO_DATE(s, fmt)    | Parse string as date              | TO_DATE('06/15/24',fmt) |
| TO_TIMESTAMP       | Parse string as timestamp         | TO_TIMESTAMP(s, fmt)    |
| d::DATE            | Cast to date (PostgreSQL)         | '2024-06-15'::DATE      |
+--------------------+-----------------------------------+-------------------------+
```

---

## Common Mistakes

### Mistake 1: Forgetting That || Returns NULL with NULL Inputs

```sql
-- WRONG: Returns NULL if middle_name is NULL
SELECT first_name || ' ' || middle_name || ' ' || last_name AS full_name
FROM people;
-- If middle_name is NULL, the entire result is NULL!
```

**Fix:** Use CONCAT or COALESCE.

```sql
-- CORRECT: CONCAT ignores NULLs
SELECT CONCAT(first_name, ' ', COALESCE(middle_name, ''), ' ', last_name)
FROM people;
```

### Mistake 2: Using = for Date Comparison with Timestamps

```sql
-- WRONG: This misses rows with non-zero times
SELECT * FROM contacts
WHERE created_at = '2023-01-15';
-- Only matches exactly '2023-01-15 00:00:00.000000'
```

**Fix:** Use a range or DATE_TRUNC.

```sql
-- CORRECT: Range comparison
SELECT * FROM contacts
WHERE created_at >= '2023-01-15'
  AND created_at <  '2023-01-16';

-- CORRECT: Using DATE_TRUNC
SELECT * FROM contacts
WHERE DATE_TRUNC('day', created_at) = '2023-01-15';
```

### Mistake 3: Confusing POSITION Return Value

```sql
-- WRONG: POSITION returns 0 (not NULL) if not found
SELECT email FROM contacts
WHERE POSITION('@' IN email) IS NULL;
-- Returns nothing! POSITION returns 0, not NULL.
```

**Fix:** Compare with 0.

```sql
-- CORRECT
SELECT email FROM contacts
WHERE POSITION('@' IN email) = 0;
-- Finds emails without @ signs
```

### Mistake 4: Using String Functions on NULL Values

```sql
-- Most string functions return NULL when given NULL input
SELECT UPPER(NULL);     -- Returns NULL
SELECT LENGTH(NULL);    -- Returns NULL
SELECT TRIM(NULL);      -- Returns NULL
```

**Fix:** Use COALESCE to provide a default value before applying the function.

---

## Best Practices

1. **Clean data at the boundary.** Apply TRIM, LOWER, and other cleanup functions when inserting or updating data, not just when querying. This keeps your data consistently formatted.

2. **Use DATE_TRUNC for time-based grouping.** It is cleaner than extracting individual parts and easier to work with in ORDER BY.

3. **Prefer CONCAT over || when NULLs are possible.** CONCAT treats NULL as an empty string, while || returns NULL if any operand is NULL.

4. **Use SPLIT_PART over SUBSTRING+POSITION** when splitting by delimiters. It is more readable and less error-prone.

5. **Store dates as DATE or TIMESTAMP types**, not as strings. Use TO_DATE or CAST only when receiving string input from external sources.

6. **Use ISO 8601 format (YYYY-MM-DD)** for date literals in your SQL. It is unambiguous and works regardless of locale settings.

7. **Be aware of time zones** when working with TIMESTAMP. Use `TIMESTAMP WITH TIME ZONE` (or `TIMESTAMPTZ`) for applications that span multiple time zones.

---

## Quick Summary

| Category | Key Functions |
|----------|---------------|
| Case | UPPER, LOWER, INITCAP |
| Length/Trim | LENGTH, TRIM, LTRIM, RTRIM |
| Extract/Split | SUBSTRING, LEFT, RIGHT, SPLIT_PART, POSITION |
| Replace/Combine | REPLACE, CONCAT, \|\| |
| Pattern | REGEXP_MATCHES, ~, ~* |
| Current time | CURRENT_DATE, CURRENT_TIMESTAMP, NOW() |
| Date parts | EXTRACT, DATE_TRUNC |
| Date math | AGE, INTERVAL arithmetic |
| Formatting | TO_CHAR, TO_DATE, TO_TIMESTAMP |

---

## Key Points

- **String functions** let you clean, format, split, and search text data. TRIM, LOWER, and SPLIT_PART are among the most commonly used.
- **CONCAT is NULL-safe**, while `||` returns NULL if any operand is NULL.
- **POSITION** returns 0 (not NULL) if the substring is not found.
- **SPLIT_PART** is a clean way to parse delimited strings.
- **EXTRACT** pulls out specific parts of dates (year, month, day, hour, etc.).
- **DATE_TRUNC** rounds down to a time precision and is ideal for grouping by time periods.
- **AGE** calculates the difference between dates in a human-readable interval format.
- **INTERVAL arithmetic** lets you add or subtract time from dates (`+ INTERVAL '7 days'`).
- **TO_CHAR** formats dates and timestamps as strings for display.
- **TO_DATE** and `::DATE` convert strings to proper date types.

---

## Practice Questions

**Question 1:** What is the difference between CONCAT and || in PostgreSQL?

<details>
<summary>Answer</summary>

Both concatenate strings. The key difference is NULL handling: `||` returns NULL if any operand is NULL, while CONCAT treats NULL as an empty string and continues concatenation. Use CONCAT when NULLs are possible.

</details>

**Question 2:** How would you extract just the year from a DATE column called `hire_date`?

<details>
<summary>Answer</summary>

Use `EXTRACT(YEAR FROM hire_date)`. This returns the year as a number. For example, if hire_date is '2023-06-15', EXTRACT returns 2023.

</details>

**Question 3:** What is the difference between EXTRACT and DATE_TRUNC?

<details>
<summary>Answer</summary>

EXTRACT returns a **number** representing one part of the date (e.g., the month number 6). DATE_TRUNC returns a **date/timestamp** truncated to the specified precision (e.g., '2024-06-01' for month truncation). DATE_TRUNC is better for grouping and ranges; EXTRACT is better when you need the numeric value of a date part.

</details>

**Question 4:** How do you find records from the last 7 days?

<details>
<summary>Answer</summary>

```sql
SELECT * FROM table_name
WHERE date_column >= CURRENT_DATE - INTERVAL '7 days';
```

For timestamps, use `CURRENT_TIMESTAMP` instead of `CURRENT_DATE`.

</details>

**Question 5:** What does SPLIT_PART('hello-world-test', '-', 2) return?

<details>
<summary>Answer</summary>

It returns `'world'`. SPLIT_PART splits the string by the delimiter '-' into parts ('hello', 'world', 'test') and returns the 2nd part.

</details>

---

## Exercises

### Exercise 1: Email Analysis

Write a query that shows each contact's clean name (trimmed, title case), their email domain (lowercase), and whether the domain is a free email provider (gmail.com, yahoo.com, hotmail.com) or a business email.

<details>
<summary>Solution</summary>

```sql
SELECT INITCAP(TRIM(full_name)) AS name,
       LOWER(SPLIT_PART(email, '@', 2)) AS domain,
       CASE
           WHEN LOWER(SPLIT_PART(email, '@', 2))
               IN ('gmail.com', 'yahoo.com', 'hotmail.com')
               THEN 'Personal'
           ELSE 'Business'
       END AS email_type
FROM contacts
ORDER BY email_type, name;
```

Expected output:

```
+------------------+--------------+------------+
| name             | domain       | email_type |
+------------------+--------------+------------+
| Alice Johnson    | example.com  | Business   |
| Bob Smith        | example.com  | Business   |
| Diana Lee        | example.com  | Business   |
| Eve Davis-Wilson | work.co.uk   | Business   |
| Charlie Brown    | gmail.com    | Personal   |
+------------------+--------------+------------+
```

</details>

### Exercise 2: Age Groups

Write a query that categorizes contacts by age group (Under 30, 30-35, 36-40, Over 40), shows their name and exact age, and counts how many contacts are in each group.

<details>
<summary>Solution</summary>

```sql
SELECT INITCAP(TRIM(full_name)) AS name,
       EXTRACT(YEAR FROM AGE(birth_date))::INTEGER AS age,
       CASE
           WHEN EXTRACT(YEAR FROM AGE(birth_date)) < 30 THEN 'Under 30'
           WHEN EXTRACT(YEAR FROM AGE(birth_date)) BETWEEN 30 AND 35 THEN '30-35'
           WHEN EXTRACT(YEAR FROM AGE(birth_date)) BETWEEN 36 AND 40 THEN '36-40'
           ELSE 'Over 40'
       END AS age_group
FROM contacts
ORDER BY age;
```

For the group summary:

```sql
SELECT CASE
           WHEN EXTRACT(YEAR FROM AGE(birth_date)) < 30 THEN 'Under 30'
           WHEN EXTRACT(YEAR FROM AGE(birth_date)) BETWEEN 30 AND 35 THEN '30-35'
           WHEN EXTRACT(YEAR FROM AGE(birth_date)) BETWEEN 36 AND 40 THEN '36-40'
           ELSE 'Over 40'
       END AS age_group,
       COUNT(*) AS count
FROM contacts
GROUP BY age_group
ORDER BY age_group;
```

</details>

### Exercise 3: Date-Based Reporting

Write a query that shows for each contact:
- Their clean name
- How many days since they signed up
- Which quarter they signed up in (Q1, Q2, Q3, Q4)
- Their sign-up date formatted as "January 15, 2023"

<details>
<summary>Solution</summary>

```sql
SELECT INITCAP(TRIM(full_name)) AS name,
       (CURRENT_DATE - created_at::DATE) AS days_since_signup,
       'Q' || EXTRACT(QUARTER FROM created_at) AS signup_quarter,
       TO_CHAR(created_at, 'Month DD, YYYY') AS formatted_date
FROM contacts
ORDER BY created_at;
```

Expected output (days_since_signup will vary):

```
+------------------+-------------------+----------------+--------------------+
| name             | days_since_signup | signup_quarter | formatted_date     |
+------------------+-------------------+----------------+--------------------+
| Alice Johnson    |               517 | Q1             | January   15, 2023 |
| Bob Smith        |               453 | Q1             | March     20, 2023 |
| Charlie Brown    |               371 | Q2             | June      10, 2023 |
| Diana Lee        |               162 | Q1             | January   05, 2024 |
| Eve Davis-Wilson |               122 | Q1             | February  14, 2024 |
+------------------+-------------------+----------------+--------------------+
```

</details>

---

## What Is Next?

You now have a solid toolkit for manipulating strings and dates in your queries. In the next chapter, you will learn about **CASE expressions** — SQL's version of if/then/else logic. CASE lets you add conditional logic directly inside your queries, transforming values, creating categories, and building dynamic columns based on conditions.
