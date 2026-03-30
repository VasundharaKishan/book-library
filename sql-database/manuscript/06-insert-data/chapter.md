# Chapter 6: Inserting Data

## What You Will Learn

By the end of this chapter, you will know how to:

- Insert a single row with `INSERT INTO`
- Insert multiple rows in one statement
- Insert data with a column list (and why you should always use one)
- Use DEFAULT values during insertion
- Get back the inserted data with `RETURNING` (a PostgreSQL feature)
- Copy data from one table to another with `INSERT ... SELECT`
- Handle duplicate conflicts with `ON CONFLICT` (upsert)
- Bulk load large amounts of data with `COPY`
- Understand the difference between NULL and an empty string
- Build a complete school database with sample data

## Why This Chapter Matters

A database without data is like a library without books. You have built the shelves (tables) and labeled them (columns and types). Now it is time to fill them up. Knowing how to insert data efficiently and correctly is a fundamental skill. Every application that saves user input, logs events, or stores records uses INSERT statements constantly.

---

## INSERT INTO: Adding a Single Row

The `INSERT INTO` command adds a new row to a table.

### Basic Syntax

```sql
INSERT INTO table_name (column1, column2, column3)
VALUES (value1, value2, value3);
```

### Example

Let us start with a simple `students` table:

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INTEGER,
    enrollment_date DATE DEFAULT CURRENT_DATE
);
```

Now insert one student:

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES ('Alice', 'Johnson', 'alice@email.com', 20);
```

```
INSERT 0 1
```

**Line-by-line:**
- `INSERT INTO students` tells PostgreSQL which table to add data to.
- `(first_name, last_name, email, age)` lists the columns we are providing values for. We did not list `id` (because SERIAL handles it automatically) or `enrollment_date` (because it has a DEFAULT).
- `VALUES ('Alice', 'Johnson', 'alice@email.com', 20)` provides the actual data. The values must match the columns in order.
- The response `INSERT 0 1` means: 0 is the OID (an internal identifier, usually 0) and 1 is the number of rows inserted.

Let us verify:

```sql
SELECT * FROM students;
```

```
 id | first_name | last_name |      email      | age | enrollment_date
----+------------+-----------+-----------------+-----+-----------------
  1 | Alice      | Johnson   | alice@email.com |  20 | 2024-06-15
(1 row)
```

Notice that `id` was automatically set to 1 (by SERIAL) and `enrollment_date` was automatically set to today's date (by DEFAULT CURRENT_DATE).

---

## Inserting Multiple Rows

You can insert several rows in a single statement by separating each set of values with a comma. This is faster than running multiple INSERT statements.

### Syntax

```sql
INSERT INTO table_name (column1, column2, column3)
VALUES
    (value1a, value2a, value3a),
    (value1b, value2b, value3b),
    (value1c, value2c, value3c);
```

### Example

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES
    ('Bob', 'Smith', 'bob@email.com', 22),
    ('Charlie', 'Brown', 'charlie@email.com', 19),
    ('Diana', 'Prince', 'diana@email.com', 21),
    ('Eve', 'Davis', 'eve@email.com', 23);
```

```
INSERT 0 4
```

The response `INSERT 0 4` confirms that 4 rows were inserted.

```sql
SELECT * FROM students;
```

```
 id | first_name | last_name |       email       | age | enrollment_date
----+------------+-----------+-------------------+-----+-----------------
  1 | Alice      | Johnson   | alice@email.com   |  20 | 2024-06-15
  2 | Bob        | Smith     | bob@email.com     |  22 | 2024-06-15
  3 | Charlie    | Brown     | charlie@email.com |  19 | 2024-06-15
  4 | Diana      | Prince    | diana@email.com   |  21 | 2024-06-15
  5 | Eve        | Davis     | eve@email.com     |  23 | 2024-06-15
(5 rows)
```

### Why Multi-Row INSERT Is Better

```
+---------------------------+--------------------------+
| Approach                  | Performance              |
+---------------------------+--------------------------+
| 5 separate INSERT         | 5 round trips to the     |
|   statements              |   database               |
+---------------------------+--------------------------+
| 1 INSERT with 5 rows      | 1 round trip to the      |
|   in VALUES               |   database               |
+---------------------------+--------------------------+
```

When inserting 5 rows, the difference is negligible. When inserting 10,000 rows, multi-row INSERT can be 10 to 50 times faster than individual inserts.

---

## INSERT with Column List

You should always specify the column list in your INSERT statements.

### With Column List (Recommended)

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES ('Frank', 'Wilson', 'frank@email.com', 24);
```

### Without Column List (Not Recommended)

```sql
INSERT INTO students
VALUES (7, 'Frank', 'Wilson', 'frank@email.com', 24, '2024-06-15');
```

This works, but it is fragile and dangerous. Here is why:

1. **You must provide values for ALL columns**, including auto-generated ones like `id`.
2. **The order must match exactly.** If someone adds a column to the table, your INSERT breaks.
3. **It is hard to read.** Without column names, you cannot tell what each value represents.

```
+-----------------------------------+-----------------------------------+
| Without Column List               | With Column List                  |
+-----------------------------------+-----------------------------------+
| VALUES (7, 'Frank', 'Wilson',     | (first_name, last_name, email,   |
|   'frank@email.com', 24,         |   age)                            |
|   '2024-06-15')                   | VALUES ('Frank', 'Wilson',       |
|                                   |   'frank@email.com', 24)         |
| What is 7? What is 24?           | Clear: first_name is 'Frank',    |
| Hard to understand.              |   age is 24.                      |
+-----------------------------------+-----------------------------------+
```

**Rule of thumb:** Always use a column list. It makes your code clear, robust, and maintainable.

---

## INSERT with DEFAULT

When a column has a DEFAULT value, you can let PostgreSQL use it in several ways.

### Method 1: Omit the Column

Simply leave the column out of your column list:

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES ('Grace', 'Lee', 'grace@email.com', 20);
```

Since `enrollment_date` is not in the column list, PostgreSQL uses its DEFAULT (CURRENT_DATE).

### Method 2: Use the DEFAULT Keyword

You can explicitly say "use the default":

```sql
INSERT INTO students (first_name, last_name, email, age, enrollment_date)
VALUES ('Grace', 'Lee', 'grace@email.com', 20, DEFAULT);
```

This does the same thing as Method 1 but is more explicit. Use this when you want to make it clear that you intentionally want the default value.

### Method 3: DEFAULT VALUES (All Defaults)

If every column has either a DEFAULT or is nullable, you can insert a row with all defaults:

```sql
CREATE TABLE counters (
    id SERIAL PRIMARY KEY,
    count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO counters DEFAULT VALUES;
```

```sql
SELECT * FROM counters;
```

```
 id | count |         created_at
----+-------+----------------------------
  1 |     0 | 2024-06-15 14:45:00.000000
(1 row)
```

Every column used its default value. This is useful for tables where you want to create a record and fill in details later.

---

## RETURNING: Get Back What You Inserted

The `RETURNING` clause is a powerful PostgreSQL feature that returns the data you just inserted. This is incredibly useful when you need the auto-generated `id` of a new row.

### Syntax

```sql
INSERT INTO table_name (columns)
VALUES (values)
RETURNING column1, column2, ...;
```

### Example: Get the New ID

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES ('Henry', 'Taylor', 'henry@email.com', 21)
RETURNING id;
```

```
 id
----
  8
(1 row)
```

Instead of the usual `INSERT 0 1` response, you get back the id of the newly inserted row. This is essential in applications where you need the new record's ID immediately (for example, to insert related data in another table).

### Example: Return Multiple Columns

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES ('Ivy', 'Clark', 'ivy@email.com', 22)
RETURNING id, first_name, last_name, enrollment_date;
```

```
 id | first_name | last_name | enrollment_date
----+------------+-----------+-----------------
  9 | Ivy        | Clark     | 2024-06-15
(1 row)
```

### Example: Return Everything

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES ('Jack', 'White', 'jack@email.com', 19)
RETURNING *;
```

```
 id | first_name | last_name |     email      | age | enrollment_date
----+------------+-----------+----------------+-----+-----------------
 10 | Jack       | White     | jack@email.com |  19 | 2024-06-15
(1 row)
```

`RETURNING *` returns all columns of the inserted row, including auto-generated ones.

### RETURNING with Multi-Row INSERT

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES
    ('Kate', 'Adams', 'kate@email.com', 20),
    ('Leo', 'Brown', 'leo@email.com', 23)
RETURNING id, first_name, email;
```

```
 id | first_name |     email
----+------------+----------------
 11 | Kate       | kate@email.com
 12 | Leo        | leo@email.com
(2 rows)
```

> **Note:** RETURNING is a PostgreSQL extension. It is not available in all databases (MySQL does not have it, for example). But it is one of the features that makes PostgreSQL so great.

---

## INSERT from SELECT: Copying Data Between Tables

You can insert data into a table by selecting it from another table (or even the same table).

### Syntax

```sql
INSERT INTO target_table (column1, column2)
SELECT column1, column2
FROM source_table
WHERE condition;
```

### Example: Archive Old Students

Let us say we want to move graduated students to an archive table:

```sql
-- Create the archive table with the same structure
CREATE TABLE students_archive (
    id INTEGER,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    age INTEGER,
    enrollment_date DATE,
    archived_date DATE DEFAULT CURRENT_DATE
);

-- Copy students older than 22 to the archive
INSERT INTO students_archive (id, first_name, last_name, email, age, enrollment_date)
SELECT id, first_name, last_name, email, age, enrollment_date
FROM students
WHERE age > 22;
```

```
INSERT 0 2
```

```sql
SELECT * FROM students_archive;
```

```
 id | first_name | last_name |     email      | age | enrollment_date | archived_date
----+------------+-----------+----------------+-----+-----------------+---------------
  5 | Eve        | Davis     | eve@email.com  |  23 | 2024-06-15      | 2024-06-15
 12 | Leo        | Brown     | leo@email.com  |  23 | 2024-06-15      | 2024-06-15
(2 rows)
```

**Line-by-line:**
- `INSERT INTO students_archive (id, first_name, ...)` specifies the target table and columns.
- `SELECT id, first_name, ... FROM students` selects the data from the source table.
- `WHERE age > 22` filters to only include students older than 22.
- The `archived_date` was not in the column list, so it used its DEFAULT (CURRENT_DATE).

### Example: Create a Summary Table

```sql
CREATE TABLE department_counts (
    department VARCHAR(50),
    student_count INTEGER
);

INSERT INTO department_counts (department, student_count)
SELECT department, COUNT(*)
FROM courses
GROUP BY department;
```

This creates a summary by counting courses per department and storing the results in a new table.

---

## ON CONFLICT: Upsert (Insert or Update)

**Upsert** means "insert if new, update if already exists." PostgreSQL handles this with `ON CONFLICT`.

**Think of it as:** A guest list at a hotel. If the guest is new, check them in (INSERT). If they are already checked in, update their room information (UPDATE).

### Syntax

```sql
INSERT INTO table_name (columns)
VALUES (values)
ON CONFLICT (conflict_column)
DO UPDATE SET column = value;
```

### Example: Insert or Update

Let us create a table where each student can have only one profile:

```sql
CREATE TABLE student_profiles (
    student_email VARCHAR(100) PRIMARY KEY,
    nickname VARCHAR(50),
    bio TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Insert a new profile:

```sql
INSERT INTO student_profiles (student_email, nickname, bio)
VALUES ('alice@email.com', 'Ali', 'Math enthusiast')
ON CONFLICT (student_email)
DO UPDATE SET
    nickname = EXCLUDED.nickname,
    bio = EXCLUDED.bio,
    updated_at = CURRENT_TIMESTAMP;
```

```
INSERT 0 1
```

**Line-by-line:**
- `INSERT INTO student_profiles ... VALUES (...)` tries to insert a new row.
- `ON CONFLICT (student_email)` if a row with this email already exists...
- `DO UPDATE SET` ...then update these columns instead.
- `EXCLUDED.nickname` refers to the value that was attempted to be inserted. In this case, 'Ali'.
- `updated_at = CURRENT_TIMESTAMP` also updates the timestamp.

Now run the same command again with a different nickname:

```sql
INSERT INTO student_profiles (student_email, nickname, bio)
VALUES ('alice@email.com', 'Alice J', 'Math and science enthusiast')
ON CONFLICT (student_email)
DO UPDATE SET
    nickname = EXCLUDED.nickname,
    bio = EXCLUDED.bio,
    updated_at = CURRENT_TIMESTAMP;
```

```sql
SELECT * FROM student_profiles;
```

```
  student_email  | nickname |             bio             |         updated_at
-----------------+----------+-----------------------------+----------------------------
 alice@email.com | Alice J  | Math and science enthusiast | 2024-06-15 15:10:00.000000
(1 row)
```

The row was updated, not duplicated. The nickname changed from 'Ali' to 'Alice J' and the bio was updated.

### ON CONFLICT DO NOTHING

If you just want to skip the insert when a conflict occurs (without updating):

```sql
INSERT INTO student_profiles (student_email, nickname, bio)
VALUES ('alice@email.com', 'Ignored', 'This will be ignored')
ON CONFLICT (student_email)
DO NOTHING;
```

```
INSERT 0 0
```

The response `INSERT 0 0` means zero rows were inserted. The existing row was not touched.

### When to Use ON CONFLICT

- Importing data that might have duplicates.
- Synchronizing data from an external source.
- Caching or storing "last known" values.
- Any situation where you want "insert if new, update if exists" behavior.

---

## COPY: Bulk Loading Data

For loading large amounts of data (thousands or millions of rows), `COPY` is much faster than INSERT. It reads data directly from a file.

### Loading from a CSV File

First, create a CSV file called `students.csv`:

```
first_name,last_name,email,age
Alice,Johnson,alice@school.com,20
Bob,Smith,bob@school.com,22
Charlie,Brown,charlie@school.com,19
Diana,Prince,diana@school.com,21
```

Then load it into PostgreSQL:

```sql
COPY students (first_name, last_name, email, age)
FROM '/path/to/students.csv'
DELIMITER ','
CSV HEADER;
```

**Line-by-line:**
- `COPY students (first_name, last_name, email, age)` specifies the table and columns.
- `FROM '/path/to/students.csv'` points to the file on disk. **This must be an absolute path.**
- `DELIMITER ','` says the columns are separated by commas.
- `CSV HEADER` tells PostgreSQL that the first line contains column names, not data.

### The \copy Command (For Client-Side Files)

The `COPY` command runs on the **server** and needs the file to be on the server's filesystem. If you are working locally and want to load a file from your own computer, use `\copy` (with a backslash) instead:

```
\copy students (first_name, last_name, email, age) FROM '/path/to/students.csv' DELIMITER ',' CSV HEADER;
```

`\copy` is a psql command (not SQL), so it accesses files on the client machine. It has the same syntax as COPY but runs client-side.

### Exporting Data to a CSV File

You can also export data from a table to a CSV file:

```sql
COPY students TO '/path/to/export.csv' DELIMITER ',' CSV HEADER;
```

Or using psql's `\copy`:

```
\copy students TO '/path/to/export.csv' DELIMITER ',' CSV HEADER;
```

### Performance Comparison

```
+---------------------------+-----------------------------------+
| Method                    | Speed for 100,000 Rows            |
+---------------------------+-----------------------------------+
| Individual INSERT         | ~30-60 seconds                    |
|   statements              |                                   |
+---------------------------+-----------------------------------+
| Multi-row INSERT          | ~5-10 seconds                     |
|   (batches of 1000)       |                                   |
+---------------------------+-----------------------------------+
| COPY from CSV             | ~1-2 seconds                      |
+---------------------------+-----------------------------------+
```

For large data loads, COPY is the clear winner.

---

## NULL vs Empty String

This is a concept that trips up many beginners. NULL and an empty string ('') are not the same thing.

```
+-------------------+------------------------------------------+
| Value             | Meaning                                  |
+-------------------+------------------------------------------+
| NULL              | "Unknown" or "Not applicable"            |
|                   | There is no value.                       |
+-------------------+------------------------------------------+
| '' (empty string) | "Known to be empty"                      |
|                   | There IS a value, and it is empty text.  |
+-------------------+------------------------------------------+
```

**Think of it this way:**
- NULL is like a blank space on a form. The person did not fill it in. You do not know the answer.
- An empty string is like a person who wrote nothing in the box on purpose. The answer is intentionally empty.

### Example

```sql
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    notes TEXT
);

INSERT INTO contacts (name, phone, notes) VALUES ('Alice', '555-1234', 'Friend');
INSERT INTO contacts (name, phone, notes) VALUES ('Bob', NULL, 'No phone');
INSERT INTO contacts (name, phone, notes) VALUES ('Charlie', '', 'Has phone but unknown');
```

```sql
SELECT * FROM contacts;
```

```
 id |  name   |  phone   |         notes
----+---------+----------+-----------------------
  1 | Alice   | 555-1234 | Friend
  2 | Bob     |          | No phone
  3 | Charlie |          | Has phone but unknown
(2 rows)
```

They look the same in the output, but they are different:

```sql
-- Find contacts where phone is NULL
SELECT name FROM contacts WHERE phone IS NULL;
```

```
 name
------
 Bob
(1 row)
```

```sql
-- Find contacts where phone is an empty string
SELECT name FROM contacts WHERE phone = '';
```

```
  name
---------
 Charlie
(1 row)
```

### Important NULL Rules

1. **NULL is not equal to anything, not even another NULL.**
   ```sql
   SELECT NULL = NULL;  -- Returns NULL, not TRUE
   ```

2. **Use IS NULL and IS NOT NULL to check for NULL.**
   ```sql
   -- Correct:
   WHERE phone IS NULL

   -- Wrong (will not work as expected):
   WHERE phone = NULL
   ```

3. **NULL in calculations produces NULL.**
   ```sql
   SELECT 5 + NULL;  -- Returns NULL
   SELECT NULL || 'hello';  -- Returns NULL (|| is string concatenation)
   ```

---

## Complete Example: Populating a School Database

Let us put everything together. We will create a school database and fill it with realistic sample data.

### Step 1: Create the Tables

```sql
-- Create a fresh database
CREATE DATABASE school_complete;
```

```
\c school_complete
```

```sql
-- Teachers
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    hire_date DATE DEFAULT CURRENT_DATE
);

-- Courses
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_code VARCHAR(10) UNIQUE NOT NULL,
    credits INTEGER NOT NULL CHECK (credits >= 1 AND credits <= 6),
    department VARCHAR(50) NOT NULL,
    teacher_id INTEGER REFERENCES teachers(id),
    max_students INTEGER DEFAULT 30
);

-- Students
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_of_birth DATE,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    gpa NUMERIC(3,2) DEFAULT 0.00 CHECK (gpa >= 0.00 AND gpa <= 4.00),
    is_active BOOLEAN DEFAULT TRUE
);

-- Enrollments (junction table)
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    enrolled_date DATE DEFAULT CURRENT_DATE,
    grade VARCHAR(2),
    UNIQUE (student_id, course_id)
);
```

### Step 2: Insert Teachers

```sql
INSERT INTO teachers (name, email, department, hire_date)
VALUES
    ('Dr. Sarah Chen', 'chen@school.edu', 'Mathematics', '2015-08-15'),
    ('Prof. James Miller', 'miller@school.edu', 'Computer Science', '2018-01-10'),
    ('Dr. Maria Garcia', 'garcia@school.edu', 'History', '2012-09-01'),
    ('Prof. David Kim', 'kim@school.edu', 'Physics', '2020-03-20'),
    ('Dr. Emily Brown', 'brown@school.edu', 'English', '2016-06-01')
RETURNING id, name, department;
```

```
 id |        name        |    department
----+--------------------+------------------
  1 | Dr. Sarah Chen     | Mathematics
  2 | Prof. James Miller | Computer Science
  3 | Dr. Maria Garcia   | History
  4 | Prof. David Kim    | Physics
  5 | Dr. Emily Brown    | English
(5 rows)
```

### Step 3: Insert Courses

```sql
INSERT INTO courses (course_name, course_code, credits, department, teacher_id, max_students)
VALUES
    ('Calculus I', 'MATH101', 4, 'Mathematics', 1, 35),
    ('Linear Algebra', 'MATH201', 3, 'Mathematics', 1, 30),
    ('Intro to Programming', 'CS101', 3, 'Computer Science', 2, 40),
    ('Data Structures', 'CS201', 4, 'Computer Science', 2, 30),
    ('World History', 'HIST101', 3, 'History', 3, 50),
    ('American History', 'HIST201', 3, 'History', 3, 40),
    ('Physics I', 'PHYS101', 4, 'Physics', 4, 35),
    ('Creative Writing', 'ENG101', 3, 'English', 5, 25),
    ('English Literature', 'ENG201', 3, 'English', 5, 30)
RETURNING id, course_name, course_code;
```

```
 id |     course_name      | course_code
----+----------------------+-------------
  1 | Calculus I            | MATH101
  2 | Linear Algebra        | MATH201
  3 | Intro to Programming  | CS101
  4 | Data Structures       | CS201
  5 | World History         | HIST101
  6 | American History      | HIST201
  7 | Physics I             | PHYS101
  8 | Creative Writing      | ENG101
  9 | English Literature    | ENG201
(9 rows)
```

### Step 4: Insert Students

```sql
INSERT INTO students (first_name, last_name, email, date_of_birth, gpa)
VALUES
    ('Alice', 'Johnson', 'alice.j@student.edu', '2004-03-15', 3.85),
    ('Bob', 'Smith', 'bob.s@student.edu', '2003-07-22', 3.20),
    ('Charlie', 'Brown', 'charlie.b@student.edu', '2004-11-08', 2.95),
    ('Diana', 'Prince', 'diana.p@student.edu', '2003-01-30', 3.90),
    ('Eve', 'Davis', 'eve.d@student.edu', '2004-05-12', 3.50),
    ('Frank', 'Wilson', 'frank.w@student.edu', '2003-09-25', 2.80),
    ('Grace', 'Lee', 'grace.l@student.edu', '2004-02-14', 3.75),
    ('Henry', 'Taylor', 'henry.t@student.edu', '2003-12-01', 3.10),
    ('Ivy', 'Clark', 'ivy.c@student.edu', '2004-08-19', 3.60),
    ('Jack', 'White', 'jack.w@student.edu', '2003-04-05', 2.70)
RETURNING id, first_name, last_name, gpa;
```

```
 id | first_name | last_name | gpa
----+------------+-----------+------
  1 | Alice      | Johnson   | 3.85
  2 | Bob        | Smith     | 3.20
  3 | Charlie    | Brown     | 2.95
  4 | Diana      | Prince    | 3.90
  5 | Eve        | Davis     | 3.50
  6 | Frank      | Wilson    | 2.80
  7 | Grace      | Lee       | 3.75
  8 | Henry      | Taylor    | 3.10
  9 | Ivy        | Clark     | 3.60
 10 | Jack       | White     | 2.70
(10 rows)
```

### Step 5: Insert Enrollments

```sql
INSERT INTO enrollments (student_id, course_id, grade)
VALUES
    -- Alice: Calculus, Data Structures, World History
    (1, 1, 'A'),
    (1, 4, 'A-'),
    (1, 5, 'B+'),

    -- Bob: Intro to Programming, Physics, Creative Writing
    (2, 3, 'B'),
    (2, 7, 'B+'),
    (2, 8, 'A'),

    -- Charlie: Calculus, World History, American History
    (3, 1, 'C+'),
    (3, 5, 'B'),
    (3, 6, 'B-'),

    -- Diana: Linear Algebra, Data Structures, English Literature
    (4, 2, 'A'),
    (4, 4, 'A'),
    (4, 9, 'A-'),

    -- Eve: Intro to Programming, Physics, Creative Writing
    (5, 3, 'A-'),
    (5, 7, 'B+'),
    (5, 8, 'A'),

    -- Frank: Calculus, World History
    (6, 1, 'C'),
    (6, 5, 'C+'),

    -- Grace: Linear Algebra, Data Structures, English Literature
    (7, 2, 'A-'),
    (7, 4, 'B+'),
    (7, 9, 'A'),

    -- Henry: Intro to Programming, American History, Physics
    (8, 3, 'B-'),
    (8, 6, 'B'),
    (8, 7, 'C+'),

    -- Ivy: Calculus, Creative Writing, English Literature
    (9, 1, 'B+'),
    (9, 8, 'A'),
    (9, 9, 'A-'),

    -- Jack: World History, American History
    (10, 5, 'C'),
    (10, 6, 'C-')
RETURNING id, student_id, course_id, grade;
```

```
 id | student_id | course_id | grade
----+------------+-----------+-------
  1 |          1 |         1 | A
  2 |          1 |         4 | A-
  3 |          1 |         5 | B+
  4 |          2 |         3 | B
  5 |          2 |         7 | B+
  6 |          2 |         8 | A
  7 |          3 |         1 | C+
  8 |          3 |         5 | B
  9 |          3 |         6 | B-
 10 |          4 |         2 | A
 11 |          4 |         4 | A
 12 |          4 |         9 | A-
 13 |          5 |         3 | A-
 14 |          5 |         7 | B+
 15 |          5 |         8 | A
 16 |          6 |         1 | C
 17 |          6 |         5 | C+
 18 |          7 |         2 | A-
 19 |          7 |         4 | B+
 20 |          7 |         9 | A
 21 |          8 |         3 | B-
 22 |          8 |         6 | B
 23 |          8 |         7 | C+
 24 |          9 |         1 | B+
 25 |          9 |         8 | A
 26 |          9 |         9 | A-
 27 |         10 |         5 | C
 28 |         10 |         6 | C-
(28 rows)
```

### Step 6: Verify the Data

Let us run a few queries to make sure everything looks right:

```sql
-- How many students?
SELECT COUNT(*) AS total_students FROM students;
```

```
 total_students
----------------
             10
(1 row)
```

```sql
-- How many courses per department?
SELECT department, COUNT(*) AS course_count
FROM courses
GROUP BY department
ORDER BY course_count DESC;
```

```
    department    | course_count
------------------+--------------
 Mathematics      |            2
 Computer Science |            2
 History          |            2
 English          |            2
 Physics          |            1
(5 rows)
```

```sql
-- Which students are in Calculus I?
SELECT s.first_name, s.last_name, e.grade
FROM enrollments e
JOIN students s ON e.student_id = s.id
JOIN courses c ON e.course_id = c.id
WHERE c.course_name = 'Calculus I'
ORDER BY s.last_name;
```

```
 first_name | last_name | grade
------------+-----------+-------
 Charlie    | Brown     | C+
 Ivy        | Clark     | B+
 Alice      | Johnson   | A
 Frank      | Wilson    | C
(4 rows)
```

The school database is now fully populated and ready for use in future chapters.

---

## Common Mistakes

1. **Forgetting the column list in INSERT.** Always specify which columns you are inserting into. It makes your code readable and resistant to table changes.

2. **Mixing up the order of values.** If your column list says `(first_name, last_name)` but your values say `('Smith', 'Bob')`, you will get Bob's name backwards. Always double-check the order.

3. **Inserting into columns with foreign keys that do not exist.** If you try to insert `teacher_id = 99` but there is no teacher with id 99, PostgreSQL will reject the insert. Insert parent records first.

4. **Confusing NULL and empty string.** NULL means "unknown." An empty string means "intentionally blank." Use NULL for missing data and empty strings only when emptiness is a valid value.

5. **Not using RETURNING.** When you need the auto-generated ID of a new row, use `RETURNING id` instead of running a separate SELECT query. It is faster and safer.

6. **Using individual INSERTs for bulk data.** When inserting more than a few rows, use multi-row INSERT or COPY. Individual INSERTs are slow for large datasets.

---

## Best Practices

1. **Always use a column list.** Never rely on the default column order.

2. **Use multi-row INSERT for batches.** It is faster and more readable than multiple individual INSERTs.

3. **Use RETURNING when you need the result.** Especially useful for getting auto-generated IDs.

4. **Use ON CONFLICT for upserts.** It handles the "insert or update" pattern cleanly in a single statement.

5. **Use COPY for large data loads.** It is orders of magnitude faster than INSERT for thousands or millions of rows.

6. **Insert parent records before child records.** If courses reference teachers, insert teachers first.

7. **Use transactions for related inserts.** When inserting related data (like a student and their enrollments), wrap everything in a transaction to ensure consistency. We will cover transactions in a later chapter.

8. **Validate your data after insertion.** Run a quick SELECT to make sure the data looks right, especially after bulk inserts.

---

## Quick Summary

INSERT INTO adds rows to a table. Always specify a column list for clarity and safety. Use multi-row INSERT to add several rows at once. The RETURNING clause gives you back the inserted data, including auto-generated IDs. INSERT ... SELECT copies data between tables. ON CONFLICT handles upserts (insert or update on duplicate). COPY loads data from files and is the fastest method for bulk imports. NULL means "unknown" and is different from an empty string.

---

## Key Points

- `INSERT INTO table (columns) VALUES (values);` adds a new row.
- Always include a **column list** in your INSERT statements.
- Use **multi-row INSERT** for efficiency: `VALUES (row1), (row2), (row3);`
- **DEFAULT** lets PostgreSQL fill in a value automatically.
- **RETURNING** gives back the inserted data (great for getting auto-generated IDs).
- **INSERT ... SELECT** copies data from one table to another.
- **ON CONFLICT DO UPDATE** performs an upsert (insert or update).
- **ON CONFLICT DO NOTHING** silently skips duplicate inserts.
- **COPY** loads data from CSV files and is much faster than INSERT for large datasets.
- **NULL** means "unknown." **Empty string** means "intentionally empty." They are different.
- Insert parent records (teachers, courses) before child records (enrollments).

---

## Practice Questions

1. What is the difference between `INSERT INTO students VALUES (...)` and `INSERT INTO students (first_name, last_name) VALUES (...)`? Which is better and why?

2. You insert a student and need to know the auto-generated ID immediately. How do you do this in PostgreSQL without running a separate query?

3. Explain what `ON CONFLICT DO NOTHING` does. Give a scenario where it would be useful.

4. What is the difference between NULL and an empty string ('')? Write a query that finds all rows where the `phone` column is NULL.

5. You need to load 500,000 rows of product data from a CSV file into a PostgreSQL table. What command would you use, and why?

---

## Exercises

### Exercise 1: Build a Bookstore Database

Create a `bookstore` database with these tables and populate them with data:

1. **authors** table: id, name, country (at least 5 authors).
2. **books** table: id, title, isbn, price, publication_year, author_id (at least 10 books).
3. **customers** table: id, name, email, joined_date (at least 5 customers).

Use multi-row INSERT for efficiency. Use RETURNING to verify the IDs.

### Exercise 2: Practice ON CONFLICT

1. Create a `user_settings` table with columns: user_email (PRIMARY KEY), theme (VARCHAR), font_size (INTEGER).
2. Insert a row for 'alice@email.com' with theme 'dark' and font_size 14.
3. Write an ON CONFLICT statement that updates the theme to 'light' if a row with the same email already exists.
4. Run the ON CONFLICT statement and verify the theme changed.

### Exercise 3: NULL vs Empty String

1. Create a `survey_responses` table with: id (SERIAL PK), respondent_name (VARCHAR), answer (TEXT).
2. Insert three rows: one with a real answer, one with NULL, and one with an empty string.
3. Write a query that finds only the rows where the answer is NULL.
4. Write a query that finds only the rows where the answer is an empty string.
5. Write a query that finds rows where the answer is either NULL or an empty string.

---

## What Is Next?

Your tables are now filled with data. It is time to start asking questions. In Chapter 7, you will learn how to **query data with SELECT**. You will master selecting specific columns, using aliases, removing duplicates, and combining SELECT with arithmetic expressions. The real power of SQL is in reading data, and that is where we are headed next.
