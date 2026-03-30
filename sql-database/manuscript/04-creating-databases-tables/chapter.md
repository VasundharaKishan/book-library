# Chapter 4: Creating Databases and Tables

## What You Will Learn

By the end of this chapter, you will know how to:

- Create and drop databases with `CREATE DATABASE` and `DROP DATABASE`
- Create tables with `CREATE TABLE` and define columns
- Use column constraints: NOT NULL, UNIQUE, DEFAULT, and CHECK
- Set primary keys
- Get a preview of data types (covered fully in Chapter 5)
- Drop tables with `DROP TABLE`
- Modify existing tables with `ALTER TABLE` (add, drop, rename columns)
- Use `IF NOT EXISTS` and `IF EXISTS` to avoid errors
- Build a complete students table from scratch

## Why This Chapter Matters

Creating databases and tables is the first real thing you do as a database developer. Everything else (inserting data, querying, joining tables) depends on having well-designed tables. If your tables are poorly designed, you will struggle with every operation that follows. This chapter teaches you how to lay a solid foundation.

---

## CREATE DATABASE

A database is a container that holds all your tables, data, and other objects. Before you can create tables, you need a database.

### Basic Syntax

```sql
CREATE DATABASE database_name;
```

### Example

```sql
CREATE DATABASE school;
```

```
CREATE DATABASE
```

That is it. One line, and you have a new database.

### Naming Rules for Databases

```
+-----------------------------------+-----------------------------------+
| Rule                              | Example                           |
+-----------------------------------+-----------------------------------+
| Use lowercase letters             | school (not School or SCHOOL)     |
| Use underscores for spaces        | online_store (not online store)   |
| Start with a letter               | my_db (not 1_db)                 |
| Keep it short and descriptive     | school, inventory, blog            |
| Avoid special characters          | No @, #, -, or spaces             |
+-----------------------------------+-----------------------------------+
```

### Connecting to Your Database

After creating a database, you need to connect to it before you can create tables inside it:

```
\c school
```

```
You are now connected to database "school" as user "postgres".
school=#
```

---

## DROP DATABASE

To delete a database and all its data permanently:

```sql
DROP DATABASE database_name;
```

### Example

```sql
DROP DATABASE school;
```

```
DROP DATABASE
```

> **Warning:** This is permanent and irreversible. All tables and all data inside the database are gone forever. There is no undo. There is no recycle bin.

### Using IF EXISTS

If you try to drop a database that does not exist, PostgreSQL throws an error:

```sql
DROP DATABASE school;
-- ERROR: database "school" does not exist
```

To avoid this error, use `IF EXISTS`:

```sql
DROP DATABASE IF EXISTS school;
```

```
DROP DATABASE
```

If the database exists, it gets dropped. If it does not exist, PostgreSQL does nothing and moves on without an error.

> **Important:** You cannot drop a database while you are connected to it. Connect to a different database (like `postgres`) first, then drop the one you want to remove.

```sql
\c postgres
DROP DATABASE school;
```

---

## CREATE TABLE

This is where the real work begins. The `CREATE TABLE` command defines a new table with its columns, data types, and rules.

### Basic Syntax

```sql
CREATE TABLE table_name (
    column1_name data_type constraints,
    column2_name data_type constraints,
    column3_name data_type constraints
);
```

### A Simple Example

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INTEGER
);
```

```
CREATE TABLE
```

Let us break this down piece by piece:

```
CREATE TABLE students (          -- Start defining a table called "students"
    id SERIAL PRIMARY KEY,       -- Column: id
                                 --   SERIAL = auto-incrementing integer (1, 2, 3, ...)
                                 --   PRIMARY KEY = unique identifier for each row
    first_name VARCHAR(50),      -- Column: first_name
                                 --   VARCHAR(50) = text up to 50 characters
    last_name VARCHAR(50),       -- Column: last_name
                                 --   VARCHAR(50) = text up to 50 characters
    age INTEGER                  -- Column: age
                                 --   INTEGER = whole number
);                               -- End of table definition
```

### Verifying the Table

After creating the table, verify it exists:

```
\dt
```

```
          List of relations
 Schema |   Name   | Type  |  Owner
--------+----------+-------+----------
 public | students | table | postgres
(1 row)
```

See the table structure:

```
\d students
```

```
                                      Table "public.students"
   Column   |          Type          | Collation | Nullable |               Default
------------+------------------------+-----------+----------+-------------------------------------
 id         | integer                |           | not null | nextval('students_id_seq'::regclass)
 first_name | character varying(50)  |           |          |
 last_name  | character varying(50)  |           |          |
 age        | integer                |           |          |
Indexes:
    "students_pkey" PRIMARY KEY, btree (id)
```

---

## Data Types Preview

Every column needs a data type that tells PostgreSQL what kind of data it can hold. Here is a quick preview of the most common types. We will cover all data types in detail in Chapter 5.

```
+------------------+-----------------------------+---------------------+
| Data Type        | What It Stores              | Example             |
+------------------+-----------------------------+---------------------+
| INTEGER          | Whole numbers               | 42, -7, 0           |
| SERIAL           | Auto-incrementing integer   | 1, 2, 3, 4, ...     |
| VARCHAR(n)       | Text up to n characters     | 'Alice', 'Hello'    |
| TEXT             | Text of any length          | Long descriptions    |
| BOOLEAN          | True or false               | TRUE, FALSE          |
| DATE             | Calendar date               | '2024-01-15'         |
| TIMESTAMP        | Date and time               | '2024-01-15 14:30:00'|
| NUMERIC(p,s)     | Exact decimal number        | 19.99, 1000.50       |
+------------------+-----------------------------+---------------------+
```

**Think of data types as labels on containers:**
- An INTEGER column is like a container labeled "whole numbers only."
- A VARCHAR(50) column is like a container labeled "text, max 50 characters."
- A BOOLEAN column is like a container labeled "yes or no only."

If you try to put the wrong type of data into a column, PostgreSQL rejects it:

```sql
-- This will FAIL because 'twenty' is text, not a number:
INSERT INTO students (first_name, last_name, age)
VALUES ('Alice', 'Johnson', 'twenty');

-- ERROR: invalid input syntax for type integer: "twenty"
```

---

## Column Constraints

**Constraints** are rules you put on columns to control what data is allowed. They protect your data quality.

**Think of constraints as bouncers at a nightclub.** They check every piece of data that tries to enter and reject anything that does not meet the rules.

### NOT NULL

The `NOT NULL` constraint means the column cannot be empty. Every row must have a value for this column.

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    age INTEGER
);
```

Here, `first_name` and `last_name` are required. `email` and `age` are optional (they can be NULL).

What happens if you try to insert without a required field:

```sql
INSERT INTO students (last_name, age)
VALUES ('Johnson', 20);
```

```
ERROR: null value in column "first_name" of relation "students"
violates not-null constraint
```

PostgreSQL stops you from inserting incomplete data. This is a good thing.

### UNIQUE

The `UNIQUE` constraint means no two rows can have the same value in this column.

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INTEGER
);
```

Now each student must have a different email address:

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES ('Alice', 'Johnson', 'alice@email.com', 20);
-- Works fine

INSERT INTO students (first_name, last_name, email, age)
VALUES ('Bob', 'Smith', 'alice@email.com', 22);
-- ERROR: duplicate key value violates unique constraint "students_email_key"
```

> **Note:** NULL values are treated as unique. Two rows can both have NULL in a UNIQUE column. This is because NULL means "unknown," and two unknowns are not considered equal.

### DEFAULT

The `DEFAULT` constraint provides a value automatically when you do not specify one.

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INTEGER,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE
);
```

Now when you insert a student without specifying `enrollment_date` or `is_active`:

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES ('Alice', 'Johnson', 'alice@email.com', 20);
```

```sql
SELECT * FROM students;
```

```
 id | first_name | last_name |      email      | age | enrollment_date | is_active
----+------------+-----------+-----------------+-----+-----------------+-----------
  1 | Alice      | Johnson   | alice@email.com |  20 | 2024-06-15      | t
(1 row)
```

The `enrollment_date` was automatically set to today's date, and `is_active` was automatically set to TRUE (shown as `t` in psql).

### CHECK

The `CHECK` constraint lets you define a custom rule. The data must pass this check to be inserted.

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INTEGER CHECK (age >= 0 AND age <= 150),
    gpa NUMERIC(3,2) CHECK (gpa >= 0.00 AND gpa <= 4.00)
);
```

The `age` column only accepts values between 0 and 150. The `gpa` column only accepts values between 0.00 and 4.00.

```sql
INSERT INTO students (first_name, last_name, age, gpa)
VALUES ('Alice', 'Johnson', -5, 3.80);
-- ERROR: new row for relation "students" violates check constraint
-- "students_age_check"

INSERT INTO students (first_name, last_name, age, gpa)
VALUES ('Alice', 'Johnson', 20, 5.00);
-- ERROR: new row for relation "students" violates check constraint
-- "students_gpa_check"
```

### Combining Constraints

You can use multiple constraints on the same column:

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    price NUMERIC(10,2) NOT NULL CHECK (price > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
);
```

This table enforces:
- Every product must have a name (`NOT NULL`), and no two products can have the same name (`UNIQUE`).
- Every product must have a price (`NOT NULL`), and the price must be positive (`CHECK (price > 0)`).
- Stock defaults to 0 (`DEFAULT 0`), must be provided or defaulted (`NOT NULL`), and cannot be negative (`CHECK (stock >= 0)`).

### Constraints Summary

```
+------------+---------------------------------------+----------------------+
| Constraint | Rule                                  | Example              |
+------------+---------------------------------------+----------------------+
| NOT NULL   | Column cannot be empty                | first_name NOT NULL  |
| UNIQUE     | No duplicate values allowed           | email UNIQUE         |
| DEFAULT    | Automatic value if none provided      | status DEFAULT 'new' |
| CHECK      | Custom validation rule                | age CHECK(age >= 0)  |
| PRIMARY KEY| Unique + NOT NULL (identifies the row)| id PRIMARY KEY       |
+------------+---------------------------------------+----------------------+
```

---

## PRIMARY KEY

We covered primary keys in Chapter 2, but let us see the SQL syntax.

### Method 1: Inline (Column Level)

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50)
);
```

### Method 2: Table Level

```sql
CREATE TABLE students (
    id SERIAL,
    first_name VARCHAR(50),
    PRIMARY KEY (id)
);
```

Both methods do the same thing. Method 1 is more common for single-column primary keys. Method 2 is useful when you need a **composite primary key** (a primary key made of multiple columns):

```sql
CREATE TABLE enrollments (
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    grade VARCHAR(2),
    PRIMARY KEY (student_id, course_id)
);
```

Here, the combination of `student_id` and `course_id` is the primary key. This means a student can enroll in a course only once (no duplicate enrollments).

---

## DROP TABLE

To delete a table and all its data:

```sql
DROP TABLE students;
```

```
DROP TABLE
```

> **Warning:** Like `DROP DATABASE`, this is permanent. All data in the table is lost.

### Using IF EXISTS

```sql
DROP TABLE IF EXISTS students;
```

This drops the table if it exists. If it does not exist, PostgreSQL does nothing instead of throwing an error.

### Dropping Multiple Tables

You can drop several tables in one command:

```sql
DROP TABLE IF EXISTS enrollments, students, courses;
```

> **Order matters!** If `enrollments` has foreign keys pointing to `students` and `courses`, you must drop `enrollments` first. Or use `CASCADE`:

```sql
DROP TABLE IF EXISTS students CASCADE;
```

`CASCADE` automatically drops anything that depends on the table (like foreign key constraints in other tables). Use this carefully.

---

## ALTER TABLE

After creating a table, you may need to change it. The `ALTER TABLE` command lets you modify an existing table without dropping and recreating it.

### Adding a Column

```sql
ALTER TABLE students ADD COLUMN phone VARCHAR(20);
```

```
ALTER TABLE
```

Let us verify:

```
\d students
```

The new `phone` column appears at the end of the column list.

### Adding a Column with Constraints

```sql
ALTER TABLE students ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL;
```

This adds a column called `is_active` that defaults to TRUE and cannot be NULL.

### Dropping a Column

```sql
ALTER TABLE students DROP COLUMN phone;
```

```
ALTER TABLE
```

> **Warning:** Dropping a column deletes all data in that column for every row. This cannot be undone.

### Renaming a Column

```sql
ALTER TABLE students RENAME COLUMN first_name TO given_name;
```

```
ALTER TABLE
```

This changes the column name from `first_name` to `given_name`. The data stays the same.

### Renaming a Table

```sql
ALTER TABLE students RENAME TO pupils;
```

```
ALTER TABLE
```

Now the table is called `pupils` instead of `students`.

### Changing a Column's Data Type

```sql
ALTER TABLE students ALTER COLUMN age TYPE SMALLINT;
```

This changes the `age` column from INTEGER to SMALLINT (a smaller number type). PostgreSQL will try to convert existing data to the new type.

### Adding a Constraint to an Existing Column

```sql
ALTER TABLE students ALTER COLUMN email SET NOT NULL;
```

This makes the `email` column required (NOT NULL) after the table has already been created.

```sql
ALTER TABLE students ADD CONSTRAINT email_unique UNIQUE (email);
```

This adds a UNIQUE constraint to the `email` column.

### Dropping a Constraint

```sql
ALTER TABLE students DROP CONSTRAINT email_unique;
```

### ALTER TABLE Summary

```
+-------------------------------+------------------------------------------+
| Command                       | What It Does                             |
+-------------------------------+------------------------------------------+
| ADD COLUMN name TYPE          | Add a new column                         |
| DROP COLUMN name              | Remove a column and its data             |
| RENAME COLUMN old TO new      | Change a column's name                   |
| RENAME TO new_table_name      | Change the table's name                  |
| ALTER COLUMN name TYPE new    | Change a column's data type              |
| ALTER COLUMN name SET NOT NULL| Make a column required                   |
| ALTER COLUMN name DROP NOT NULL| Make a column optional                  |
| ALTER COLUMN name SET DEFAULT | Set a default value                      |
| ADD CONSTRAINT name ...       | Add a new constraint                     |
| DROP CONSTRAINT name          | Remove a constraint                      |
+-------------------------------+------------------------------------------+
```

---

## IF NOT EXISTS

When you create a table that already exists, PostgreSQL throws an error:

```sql
CREATE TABLE students (id SERIAL PRIMARY KEY);
-- ERROR: relation "students" already exists
```

To avoid this, use `IF NOT EXISTS`:

```sql
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INTEGER
);
```

```
NOTICE: relation "students" already exists, skipping
CREATE TABLE
```

If the table exists, PostgreSQL skips the command and gives you a notice. If the table does not exist, it creates it.

This is especially useful in scripts that you might run multiple times.

---

## Complete Example: Building a School Database

Let us put everything together and create a complete school database from scratch. This example uses everything we have learned in this chapter.

```sql
-- ============================================
-- Step 1: Create the database
-- ============================================

CREATE DATABASE school;

-- Connect to it (in psql, use \c school)
```

```
\c school
```

```sql
-- ============================================
-- Step 2: Create the teachers table
-- ============================================

CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    hire_date DATE DEFAULT CURRENT_DATE
);
```

**Line-by-line:**
- `id SERIAL PRIMARY KEY` auto-incrementing unique identifier.
- `name VARCHAR(100) NOT NULL` teacher's name, required, up to 100 characters.
- `email VARCHAR(100) UNIQUE NOT NULL` teacher's email, must be unique, required.
- `department VARCHAR(50) NOT NULL` department name, required.
- `hire_date DATE DEFAULT CURRENT_DATE` automatically set to today when not specified.

```sql
-- ============================================
-- Step 3: Create the courses table
-- ============================================

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_code VARCHAR(10) UNIQUE NOT NULL,
    credits INTEGER NOT NULL CHECK (credits >= 1 AND credits <= 6),
    department VARCHAR(50) NOT NULL,
    teacher_id INTEGER REFERENCES teachers(id)
);
```

**Line-by-line:**
- `course_code VARCHAR(10) UNIQUE NOT NULL` a short unique code like "MATH101."
- `credits INTEGER NOT NULL CHECK (credits >= 1 AND credits <= 6)` credits must be between 1 and 6.
- `teacher_id INTEGER REFERENCES teachers(id)` foreign key linking to the teachers table.

```sql
-- ============================================
-- Step 4: Create the students table
-- ============================================

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_of_birth DATE,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    gpa NUMERIC(3,2) DEFAULT 0.00 CHECK (gpa >= 0.00 AND gpa <= 4.00),
    is_active BOOLEAN DEFAULT TRUE
);
```

**Line-by-line:**
- `date_of_birth DATE` optional field for the student's birthday.
- `enrollment_date DATE DEFAULT CURRENT_DATE` auto-set to today.
- `gpa NUMERIC(3,2) DEFAULT 0.00 CHECK (gpa >= 0.00 AND gpa <= 4.00)` GPA starts at 0.00 and must stay between 0.00 and 4.00. `NUMERIC(3,2)` means 3 total digits, 2 after the decimal point (e.g., 3.85).
- `is_active BOOLEAN DEFAULT TRUE` defaults to TRUE for new students.

```sql
-- ============================================
-- Step 5: Create the enrollments junction table
-- ============================================

CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    enrolled_date DATE DEFAULT CURRENT_DATE,
    grade VARCHAR(2),
    UNIQUE (student_id, course_id)
);
```

**Line-by-line:**
- `student_id INTEGER NOT NULL REFERENCES students(id)` required foreign key to students.
- `course_id INTEGER NOT NULL REFERENCES courses(id)` required foreign key to courses.
- `UNIQUE (student_id, course_id)` prevents a student from enrolling in the same course twice.

### The Complete Schema

```
+=================================================================+
|                    SCHOOL DATABASE SCHEMA                        |
+=================================================================+
|                                                                  |
|  +------------------+                                            |
|  |    teachers      |                                            |
|  +------------------+                                            |
|  | id (PK, SERIAL)  |                                            |
|  | name (NOT NULL)   |                                            |
|  | email (UNIQUE)    |                                            |
|  | department        |                                            |
|  | hire_date (DEFAULT)|                                           |
|  +------------------+                                            |
|           |                                                      |
|           | one-to-many                                          |
|           v                                                      |
|  +------------------+                                            |
|  |    courses       |                                            |
|  +------------------+                                            |
|  | id (PK, SERIAL)  |                                            |
|  | course_name       |                                            |
|  | course_code       |                                            |
|  | credits (CHECK)   |                                            |
|  | department        |                                            |
|  | teacher_id (FK)   |---> teachers.id                           |
|  +------------------+                                            |
|           ^                                                      |
|           | one-to-many                                          |
|           |                                                      |
|  +------------------+                                            |
|  |   enrollments    |                                            |
|  +------------------+                                            |
|  | id (PK, SERIAL)  |                                            |
|  | student_id (FK)   |---> students.id                           |
|  | course_id (FK)    |---> courses.id                            |
|  | enrolled_date      |                                           |
|  | grade             |                                            |
|  +------------------+                                            |
|           |                                                      |
|           | one-to-many                                          |
|           v                                                      |
|  +------------------+                                            |
|  |    students      |                                            |
|  +------------------+                                            |
|  | id (PK, SERIAL)  |                                            |
|  | first_name        |                                            |
|  | last_name         |                                            |
|  | email (UNIQUE)    |                                            |
|  | date_of_birth     |                                            |
|  | enrollment_date   |                                            |
|  | gpa (CHECK)       |                                            |
|  | is_active (DEFAULT)|                                           |
|  +------------------+                                            |
|                                                                  |
+=================================================================+
```

### Verify Everything

```
\dt
```

```
            List of relations
 Schema |    Name     | Type  |  Owner
--------+-------------+-------+----------
 public | courses     | table | postgres
 public | enrollments | table | postgres
 public | students    | table | postgres
 public | teachers    | table | postgres
(4 rows)
```

```
\d students
```

```
                                         Table "public.students"
     Column      |          Type          | Collation | Nullable |               Default
-----------------+------------------------+-----------+----------+-------------------------------------
 id              | integer                |           | not null | nextval('students_id_seq'::regclass)
 first_name      | character varying(50)  |           | not null |
 last_name       | character varying(50)  |           | not null |
 email           | character varying(100) |           | not null |
 date_of_birth   | date                   |           |          |
 enrollment_date | date                   |           |          | CURRENT_DATE
 gpa             | numeric(3,2)           |           |          | 0.00
 is_active       | boolean                |           |          | true
Indexes:
    "students_pkey" PRIMARY KEY, btree (id)
    "students_email_key" UNIQUE CONSTRAINT, btree (email)
Check constraints:
    "students_gpa_check" CHECK (gpa >= 0.00 AND gpa <= 4.00)
```

Everything is in place. In Chapter 6, we will populate these tables with data.

---

## Common Mistakes

1. **Forgetting the semicolon.** Every SQL command must end with `;`. If your command seems stuck, you probably forgot it.

2. **Creating tables in the wrong order.** If Table B has a foreign key pointing to Table A, you must create Table A first. Otherwise, PostgreSQL does not know what you are referencing.

3. **Using reserved words as column names.** Words like `user`, `order`, `table`, `select` are reserved. If you must use them, put them in double quotes: `"user"`, `"order"`. Better yet, choose different names: `app_user`, `customer_order`.

4. **Forgetting NOT NULL on important columns.** If a column should always have a value (like a person's name), add NOT NULL. Otherwise, you will end up with incomplete data.

5. **Not using IF NOT EXISTS.** When writing scripts that might run multiple times, always use `CREATE TABLE IF NOT EXISTS` to avoid errors.

6. **Dropping tables with CASCADE without thinking.** `DROP TABLE ... CASCADE` removes the table and everything that depends on it. This can have unexpected consequences.

---

## Best Practices

1. **Always start with a primary key.** Every table should have an `id SERIAL PRIMARY KEY` column (or equivalent).

2. **Use NOT NULL generously.** Require data for columns that should always have values. It is easier to remove a NOT NULL constraint later than to fix dirty data.

3. **Use meaningful names.** `students` is better than `tbl1`. `enrollment_date` is better than `ed`.

4. **Use snake_case for everything.** `first_name`, not `firstName` or `First_Name`. This is the PostgreSQL convention.

5. **Add CHECK constraints for numeric ranges.** If age must be between 0 and 150, say so. Let the database enforce it.

6. **Use DEFAULT values where appropriate.** `enrollment_date DATE DEFAULT CURRENT_DATE` saves you from having to specify the date every time.

7. **Plan your schema on paper first.** Draw the tables, columns, and relationships before writing any SQL.

---

## Quick Summary

`CREATE DATABASE` makes a new database. `CREATE TABLE` defines a new table with columns, data types, and constraints. Constraints like NOT NULL, UNIQUE, DEFAULT, and CHECK protect your data quality. `DROP TABLE` removes a table permanently. `ALTER TABLE` lets you modify existing tables by adding, removing, or renaming columns. `IF NOT EXISTS` prevents errors when creating objects that might already exist.

---

## Key Points

- `CREATE DATABASE name;` creates a new database.
- `CREATE TABLE name (columns);` creates a new table.
- **NOT NULL** ensures a column always has a value.
- **UNIQUE** prevents duplicate values in a column.
- **DEFAULT** provides an automatic value when none is specified.
- **CHECK** enforces a custom rule on values.
- **PRIMARY KEY** is a combination of UNIQUE and NOT NULL. It identifies each row.
- `DROP TABLE name;` permanently deletes a table.
- `ALTER TABLE` modifies an existing table (add/drop/rename columns).
- `IF NOT EXISTS` prevents "already exists" errors.
- Always create referenced tables before tables that reference them.

---

## Practice Questions

1. What is the difference between `NOT NULL` and `DEFAULT`? Can you use both on the same column?

2. You try to create a table called `orders`, but you get an error saying the name is reserved. How would you solve this?

3. What happens if you run `DROP TABLE students;` and the `enrollments` table has a foreign key pointing to `students`?

4. You have a table with a `price` column. Write a CHECK constraint that ensures the price is always greater than zero.

5. What is the difference between `DROP TABLE students;` and `DROP TABLE IF EXISTS students;`?

---

## Exercises

### Exercise 1: Create a Library Database

Create a database called `library` with the following tables:

1. **authors** table with columns: id (auto-increment PK), name (required), country (optional), birth_year (integer).
2. **books** table with columns: id (auto-increment PK), title (required, unique), isbn (required, unique), publication_year (integer), price (must be positive), author_id (foreign key to authors).

Write the complete SQL statements. Verify your work with `\dt` and `\d table_name`.

### Exercise 2: Modify the Table

Starting from the `students` table in the complete example:

1. Add a column called `phone` (VARCHAR(20)).
2. Add a column called `major` (VARCHAR(50)) with a default value of 'Undeclared'.
3. Rename the `email` column to `school_email`.
4. Drop the `date_of_birth` column.

Write the ALTER TABLE statements for each change.

### Exercise 3: Design Constraints

For each scenario below, write the column definition with appropriate constraints:

1. A `temperature` column that stores readings between -100 and 100 degrees.
2. A `status` column that defaults to 'pending' and cannot be empty.
3. A `username` column that is required and must be unique.
4. An `account_balance` column that defaults to 0.00 and cannot be negative.
5. A `created_at` column that defaults to the current date and time.

---

## What Is Next?

Now that you can create databases and tables, you need to know what types of data your columns can hold. In Chapter 5, you will do a deep dive into **PostgreSQL data types**. You will learn about integers, decimals, text, booleans, dates, UUIDs, JSON, arrays, and how to choose the right type for every situation.
