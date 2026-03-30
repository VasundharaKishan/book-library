# Chapter 2: The Relational Model

## What You Will Learn

By the end of this chapter, you will understand:

- What tables, rows, and columns really are
- What a primary key is and why every table needs one
- What a foreign key is and how it connects tables
- The three types of relationships: one-to-one, one-to-many, and many-to-many
- What a schema is
- How to read and draw ASCII table diagrams
- A complete Students/Courses example that ties everything together

## Why This Chapter Matters

The relational model is the foundation of every relational database. It is the blueprint. If you skip this chapter, everything that follows will feel confusing. If you understand this chapter well, everything that follows will feel logical.

Think of it this way: before you build a house, you need to understand walls, floors, doors, and how rooms connect. The relational model teaches you the "architecture" of databases.

---

## Tables: The Core Building Block

A **table** is where your data lives. Every piece of data in a relational database is stored in a table.

**Think of it as:** A spreadsheet with strict rules.

Here is a table called `students`:

```
+----+------------+-----------+-----+-------------------+
| id | first_name | last_name | age | email             |
+----+------------+-----------+-----+-------------------+
|  1 | Alice      | Johnson   |  20 | alice@email.com   |
|  2 | Bob        | Smith     |  22 | bob@email.com     |
|  3 | Charlie    | Brown     |  19 | charlie@email.com |
|  4 | Diana      | Prince    |  21 | diana@email.com   |
+----+------------+-----------+-----+-------------------+
```

A table has a **name** (like `students`). You choose the name when you create the table. The name should describe what kind of data the table holds.

### Rules That Make Tables Different from Spreadsheets

1. **Every column has a fixed data type.** The `age` column only accepts numbers. The `email` column only accepts text. You cannot put a name in the age column.
2. **Every column has a name.** No unnamed columns allowed.
3. **Every row follows the same structure.** You cannot have one row with 5 columns and another with 3 columns.
4. **There is a way to uniquely identify each row.** This is called a primary key (more on this shortly).

---

## Rows: Individual Records

A **row** (also called a **record** or **tuple**) represents one specific item in the table.

In the `students` table above, each row is one student:

```
Row 1: Alice Johnson, age 20, alice@email.com
Row 2: Bob Smith, age 22, bob@email.com
Row 3: Charlie Brown, age 19, charlie@email.com
Row 4: Diana Prince, age 21, diana@email.com
```

**Think of it as:** One folder in your filing cabinet. The folder for Alice contains all of Alice's information.

When you add a new student to the database, you are adding a new row. When you remove a student, you are removing a row.

---

## Columns: Attributes of Your Data

A **column** (also called a **field** or **attribute**) represents one specific piece of information.

In the `students` table:

```
+----+------------+-----------+-----+-------------------+
| id | first_name | last_name | age | email             |
+----+------------+-----------+-----+-------------------+
  ^       ^            ^        ^         ^
  |       |            |        |         |
  |       |            |        |         +-- Column 5: email address
  |       |            |        +------------ Column 4: student's age
  |       |            +--------------------- Column 3: last name
  |       +---------------------------------- Column 2: first name
  +------------------------------------------ Column 1: unique ID
```

**Think of it as:** The labels on a form. First Name: ___, Last Name: ___, Age: ___, Email: ___.

Every column has:
- A **name** (like `first_name`).
- A **data type** (like text, number, or date). We will cover data types in detail in Chapter 5.
- **Rules** (like "this column cannot be empty"). These are called constraints, and we will cover them in Chapter 4.

---

## Primary Keys: The Unique Identifier

A **primary key** is a column (or combination of columns) that uniquely identifies each row in a table. No two rows can have the same primary key value.

**Think of it as:** Your government-issued ID card. No two people have the same ID number. Even if two people share the same name, their ID numbers are different.

```
+----+------------+-----------+
| id | first_name | last_name |
+----+------------+-----------+
|  1 | Alice      | Johnson   |  <-- id = 1 (unique)
|  2 | Bob        | Smith     |  <-- id = 2 (unique)
|  3 | Alice      | Williams  |  <-- id = 3 (unique, even though
|    |            |           |      first_name is also "Alice")
+----+------------+-----------+
  ^
  |
  Primary Key (PK): Every value is unique, never NULL
```

### Rules of Primary Keys

1. **Every value must be unique.** No duplicates.
2. **No value can be NULL (empty).** Every row must have a primary key value.
3. **The value should never change.** Once assigned, it stays forever.
4. **Every table should have one.** A table without a primary key is like a filing cabinet without labels. It works, but it is a mess.

### Common Primary Key Patterns

The most common approach is to use an auto-incrementing integer:

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50)
);
```

**Line-by-line:**
- `id SERIAL PRIMARY KEY` creates a column called `id` that automatically generates a unique number for each new row. `SERIAL` is a PostgreSQL feature that auto-increments (1, 2, 3, 4, ...).
- `first_name VARCHAR(50)` creates a text column that can hold up to 50 characters.
- `last_name VARCHAR(50)` creates another text column.

When you insert data, you do not need to provide the `id`. PostgreSQL generates it for you:

```sql
INSERT INTO students (first_name, last_name) VALUES ('Alice', 'Johnson');
INSERT INTO students (first_name, last_name) VALUES ('Bob', 'Smith');
```

```
 id | first_name | last_name
----+------------+-----------
  1 | Alice      | Johnson
  2 | Bob        | Smith
(2 rows)
```

### Why Not Use a Name as the Primary Key?

You might think, "Why not just use the student's name as the primary key?" Here is why:

1. **Names are not unique.** There can be two students named "Alice Johnson."
2. **Names change.** People get married, change their names, or fix typos.
3. **Names are long.** Numbers are faster for the database to search and compare.

Always use a numeric ID or UUID as your primary key.

---

## Foreign Keys: Links Between Tables

A **foreign key** is a column in one table that refers to the primary key of another table. It creates a link between the two tables.

**Think of it as:** A pointer or reference. It says, "This row is connected to that row in another table."

Let us say we have two tables: `students` and `courses`. We want to track which students are enrolled in which courses. We create a third table called `enrollments`:

```
+------------------+         +------------------+
|     students     |         |     courses      |
+------------------+         +------------------+
| id (PK)      = 1 |         | id (PK)      = 10|
| first_name       |         | course_name      |
| last_name        |         | credits          |
+------------------+         +------------------+
        ^                            ^
        |                            |
        |    +------------------+    |
        |    |   enrollments    |    |
        |    +------------------+    |
        +----| student_id (FK)  |    |
             | course_id (FK)   |----+
             | grade            |
             +------------------+
```

In the `enrollments` table:
- `student_id` is a foreign key that points to `students.id`.
- `course_id` is a foreign key that points to `courses.id`.

Here is what the data looks like:

**students table:**
```
+----+------------+-----------+
| id | first_name | last_name |
+----+------------+-----------+
|  1 | Alice      | Johnson   |
|  2 | Bob        | Smith     |
+----+------------+-----------+
```

**courses table:**
```
+----+------------------+---------+
| id | course_name      | credits |
+----+------------------+---------+
| 10 | Mathematics 101  |       3 |
| 20 | History 202      |       4 |
| 30 | Computer Science |       3 |
+----+------------------+---------+
```

**enrollments table:**
```
+----+------------+-----------+-------+
| id | student_id | course_id | grade |
+----+------------+-----------+-------+
|  1 |          1 |        10 | A     |
|  2 |          1 |        20 | B+    |
|  3 |          2 |        10 | A-    |
|  4 |          2 |        30 | B     |
+----+------------+-----------+-------+
```

Reading the enrollments table:
- Row 1: Student 1 (Alice) is enrolled in Course 10 (Mathematics 101) and got an A.
- Row 2: Student 1 (Alice) is enrolled in Course 20 (History 202) and got a B+.
- Row 3: Student 2 (Bob) is enrolled in Course 10 (Mathematics 101) and got an A-.
- Row 4: Student 2 (Bob) is enrolled in Course 30 (Computer Science) and got a B.

### Why Foreign Keys Matter

Foreign keys enforce **referential integrity**. That is a fancy way of saying:

> "You cannot reference something that does not exist."

For example, if you try to insert an enrollment for student_id = 99, but there is no student with id = 99, the database will reject it with an error. This prevents orphaned data (data that points to nothing).

```sql
-- This would FAIL because student_id 99 does not exist:
INSERT INTO enrollments (student_id, course_id, grade)
VALUES (99, 10, 'A');

-- ERROR: insert or update on table "enrollments" violates
-- foreign key constraint
```

---

## Relationships: How Tables Connect

Tables in a relational database are connected through relationships. There are three types.

### One-to-One (1:1)

Each row in Table A is linked to exactly one row in Table B, and vice versa.

**Real-world example:** Each person has exactly one passport, and each passport belongs to exactly one person.

```
+------------------+         +------------------+
|     persons      |         |    passports     |
+------------------+         +------------------+
| id (PK)          |----+    | id (PK)          |
| name             |    |    | person_id (FK)   |-----> persons.id
| date_of_birth    |    |    | passport_number  |       (UNIQUE)
+------------------+    |    | expiry_date      |
                        |    +------------------+
                        |
                        +--> One person = One passport
```

The key detail: `person_id` in the passports table has a **UNIQUE** constraint, meaning no two passports can have the same `person_id`. This enforces the one-to-one relationship.

```sql
CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE
);

CREATE TABLE passports (
    id SERIAL PRIMARY KEY,
    person_id INTEGER UNIQUE REFERENCES persons(id),
    passport_number VARCHAR(20),
    expiry_date DATE
);
```

**Line-by-line for the passports table:**
- `id SERIAL PRIMARY KEY` creates an auto-incrementing unique identifier.
- `person_id INTEGER UNIQUE REFERENCES persons(id)` creates a foreign key to the persons table. `UNIQUE` ensures each person can have only one passport. `REFERENCES persons(id)` means this column points to the `id` column in the `persons` table.
- `passport_number VARCHAR(20)` stores the passport number as text up to 20 characters.
- `expiry_date DATE` stores the expiration date.

### One-to-Many (1:N)

Each row in Table A can be linked to many rows in Table B, but each row in Table B is linked to only one row in Table A.

**This is the most common relationship type.**

**Real-world example:** One teacher teaches many courses, but each course has only one teacher.

```
+------------------+         +------------------+
|    teachers      |         |     courses      |
+------------------+         +------------------+
| id (PK)          |----+    | id (PK)          |
| name             |    |    | course_name      |
| department       |    +---<| teacher_id (FK)  |
+------------------+         | credits          |
                              +------------------+

One teacher -----> Many courses
```

The arrow `---<` means "one to many." One teacher points to many courses.

```
teachers table:
+----+------------------+------------+
| id | name             | department |
+----+------------------+------------+
|  1 | Prof. Smith      | Math       |
|  2 | Prof. Garcia     | History    |
+----+------------------+------------+

courses table:
+----+------------------+------------+---------+
| id | course_name      | teacher_id | credits |
+----+------------------+------------+---------+
| 10 | Algebra          |          1 |       3 |
| 20 | Calculus         |          1 |       4 |
| 30 | World History    |          2 |       3 |
+----+------------------+------------+---------+
```

Reading this data:
- Prof. Smith (id=1) teaches Algebra and Calculus (two courses).
- Prof. Garcia (id=2) teaches World History (one course).
- Each course has exactly one teacher.

### Many-to-Many (M:N)

Each row in Table A can be linked to many rows in Table B, and each row in Table B can also be linked to many rows in Table A.

**Real-world example:** Students and courses. One student can enroll in many courses, and one course can have many students.

```
+------------------+     +------------------+     +------------------+
|    students      |     |   enrollments    |     |     courses      |
+------------------+     +------------------+     +------------------+
| id (PK)          |--+  | id (PK)          |  +--| id (PK)          |
| first_name       |  +->| student_id (FK)  |  |  | course_name      |
| last_name        |     | course_id (FK)   |<-+  | credits          |
+------------------+     | grade            |     +------------------+
                          +------------------+

                          This middle table is
                          called a "junction table"
                          or "bridge table"
```

**Important:** You cannot directly represent a many-to-many relationship in a relational database. You always need a **junction table** (also called a bridge table, linking table, or join table) in the middle.

The junction table has foreign keys pointing to both of the related tables. Each row in the junction table represents one specific link between the two sides.

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50)
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR(100),
    credits INTEGER
);

CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    grade VARCHAR(2)
);
```

**Line-by-line for the enrollments table:**
- `id SERIAL PRIMARY KEY` gives each enrollment its own unique ID.
- `student_id INTEGER REFERENCES students(id)` is a foreign key linking to the students table.
- `course_id INTEGER REFERENCES courses(id)` is a foreign key linking to the courses table.
- `grade VARCHAR(2)` stores the grade as text (like "A", "B+", "C").

### Relationship Summary

```
+------------------+---------------------+----------------------------+
| Type             | Example             | How It Works               |
+------------------+---------------------+----------------------------+
| One-to-One (1:1) | Person - Passport   | FK with UNIQUE constraint  |
| One-to-Many (1:N)| Teacher - Courses   | FK in the "many" table     |
| Many-to-Many     | Students - Courses  | Junction table with two    |
|  (M:N)           |                     |   foreign keys             |
+------------------+---------------------+----------------------------+
```

---

## What Is a Schema?

A **schema** is the overall structure or design of your database. It defines:

- What tables exist
- What columns each table has
- What data type each column uses
- What relationships exist between tables
- What rules (constraints) apply

**Think of it as:** The blueprint of a house. The blueprint tells you how many rooms there are, how big each room is, and where the doors connect them. The schema is the blueprint of your database.

Here is a schema for a simple school database:

```
+=================================================================+
|                    SCHOOL DATABASE SCHEMA                        |
+=================================================================+
|                                                                  |
|  +------------------+                                            |
|  |    students      |                                            |
|  +------------------+                                            |
|  | id        SERIAL | (PK)                                      |
|  | first_name VARCHAR(50)                                        |
|  | last_name  VARCHAR(50)                                        |
|  | email      VARCHAR(100)                                       |
|  | age        INTEGER                                            |
|  +------------------+                                            |
|           |                                                      |
|           | (one-to-many: one student, many enrollments)          |
|           v                                                      |
|  +------------------+                                            |
|  |   enrollments    |                                            |
|  +------------------+                                            |
|  | id         SERIAL | (PK)                                     |
|  | student_id INTEGER | (FK -> students.id)                     |
|  | course_id  INTEGER | (FK -> courses.id)                      |
|  | grade      VARCHAR(2)                                         |
|  | enrolled_date DATE                                            |
|  +------------------+                                            |
|           ^                                                      |
|           | (one-to-many: one course, many enrollments)           |
|           |                                                      |
|  +------------------+                                            |
|  |    courses       |                                            |
|  +------------------+                                            |
|  | id          SERIAL | (PK)                                    |
|  | course_name VARCHAR(100)                                      |
|  | credits     INTEGER                                           |
|  | department  VARCHAR(50)                                       |
|  +------------------+                                            |
|                                                                  |
+=================================================================+
```

You do not need to memorize schema diagrams. You need to be able to read them and eventually design your own. We will practice this throughout the book.

---

## Complete Example: A School Database

Let us walk through a complete example step by step. We will build a small school database with students, courses, and enrollments.

### Step 1: Identify the Entities

An **entity** is a thing you want to store data about. In a school:

- Students
- Courses
- Teachers

### Step 2: Identify the Attributes

**Attributes** are the details about each entity:

```
Student: first_name, last_name, email, age, enrollment_date
Course: course_name, credits, department
Teacher: name, email, department
```

### Step 3: Identify the Relationships

- A student can enroll in many courses. A course can have many students. This is a **many-to-many** relationship. We need a junction table: `enrollments`.
- A teacher can teach many courses, but each course has one teacher. This is a **one-to-many** relationship.

### Step 4: Design the Tables

```sql
-- Teachers table
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50)
);

-- Courses table (has a FK to teachers)
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    credits INTEGER NOT NULL,
    department VARCHAR(50),
    teacher_id INTEGER REFERENCES teachers(id)
);

-- Students table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER,
    enrollment_date DATE DEFAULT CURRENT_DATE
);

-- Enrollments junction table (many-to-many between students and courses)
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    grade VARCHAR(2),
    enrolled_date DATE DEFAULT CURRENT_DATE
);
```

### Step 5: Add Some Data

```sql
-- Insert teachers
INSERT INTO teachers (name, email, department)
VALUES
    ('Prof. Smith', 'smith@school.edu', 'Mathematics'),
    ('Prof. Garcia', 'garcia@school.edu', 'History'),
    ('Prof. Lee', 'lee@school.edu', 'Computer Science');

-- Insert courses
INSERT INTO courses (course_name, credits, department, teacher_id)
VALUES
    ('Algebra', 3, 'Mathematics', 1),
    ('Calculus', 4, 'Mathematics', 1),
    ('World History', 3, 'History', 2),
    ('Intro to Programming', 3, 'Computer Science', 3);

-- Insert students
INSERT INTO students (first_name, last_name, email, age)
VALUES
    ('Alice', 'Johnson', 'alice@email.com', 20),
    ('Bob', 'Smith', 'bob@email.com', 22),
    ('Charlie', 'Brown', 'charlie@email.com', 19),
    ('Diana', 'Prince', 'diana@email.com', 21);

-- Insert enrollments
INSERT INTO enrollments (student_id, course_id, grade)
VALUES
    (1, 1, 'A'),     -- Alice in Algebra
    (1, 3, 'B+'),    -- Alice in World History
    (2, 1, 'A-'),    -- Bob in Algebra
    (2, 4, 'B'),     -- Bob in Intro to Programming
    (3, 2, 'B+'),    -- Charlie in Calculus
    (3, 3, 'A'),     -- Charlie in World History
    (4, 1, 'A'),     -- Diana in Algebra
    (4, 4, 'A-');    -- Diana in Intro to Programming
```

### Step 6: Query the Data

Now we can ask the database questions using SQL. Here is a query that shows each student's name and the courses they are enrolled in:

```sql
SELECT
    s.first_name,
    s.last_name,
    c.course_name,
    e.grade
FROM enrollments e
JOIN students s ON e.student_id = s.id
JOIN courses c ON e.course_id = c.id
ORDER BY s.last_name, c.course_name;
```

```
 first_name | last_name | course_name          | grade
------------+-----------+----------------------+-------
 Charlie    | Brown     | Calculus             | B+
 Charlie    | Brown     | World History        | A
 Alice      | Johnson   | Algebra              | A
 Alice      | Johnson   | World History        | B+
 Diana      | Prince    | Algebra              | A
 Diana      | Prince    | Intro to Programming | A-
 Bob        | Smith     | Algebra              | A-
 Bob        | Smith     | Intro to Programming | B
(8 rows)
```

Do not worry if the JOIN syntax looks unfamiliar. We will cover it in detail in Chapters 12 through 15. The point here is to see how tables connect and how you can combine data from multiple tables.

---

## Reading ASCII Table Diagrams

Throughout this book and in many online resources, you will see ASCII diagrams that show table structures and relationships. Here is how to read them:

### Table Structure Diagram

```
+------------------+
|    table_name    |     <-- Table name at the top
+------------------+
| column1 (PK)    |     <-- PK means Primary Key
| column2 (FK)    |     <-- FK means Foreign Key
| column3          |     <-- Regular column
| column4          |     <-- Regular column
+------------------+
```

### Relationship Diagram

```
+----------+         +----------+
| Table A  |----+    | Table B  |
+----------+    |    +----------+
| id (PK)  |    +--->| a_id(FK) |
| name     |         | data     |
+----------+         +----------+

The arrow shows the direction of the foreign key.
Table B has a foreign key (a_id) that points to Table A's id.
```

### Common Symbols

```
+----------+----------+-----------------------------------+
| Symbol   | Meaning  | Example                           |
+----------+----------+-----------------------------------+
| PK       | Primary  | id (PK) - unique identifier       |
|          |   Key    |                                   |
| FK       | Foreign  | student_id (FK) - reference to    |
|          |   Key    |   another table                   |
| --->     | Points   | Table B points to Table A         |
|          |   to     |                                   |
| ---<     | One to   | One teacher, many courses          |
|          |   many   |                                   |
| >---<    | Many to  | Many students, many courses        |
|          |   many   |   (needs junction table)          |
+----------+----------+-----------------------------------+
```

---

## Common Mistakes

1. **Forgetting to add a primary key.** Every table needs a way to uniquely identify each row. Always add a primary key.

2. **Using meaningful data as a primary key.** Do not use email, phone number, or name as a primary key. These can change. Use a numeric ID or UUID.

3. **Not understanding many-to-many relationships.** You cannot directly link two tables in a many-to-many relationship. You always need a junction table in the middle.

4. **Putting all data in one big table.** Beginners often try to cram everything into a single table. This leads to duplicated data and maintenance nightmares. Use separate tables and connect them with foreign keys.

5. **Confusing primary keys and foreign keys.** A primary key identifies a row in its own table. A foreign key references a row in another table. They work together, but they are different things.

---

## Best Practices

1. **Always use a SERIAL or BIGSERIAL integer as your primary key.** It is simple, fast, and reliable. Name it `id`.

2. **Name your tables in lowercase with underscores.** Use `student_courses`, not `StudentCourses` or `STUDENT-COURSES`. This is the PostgreSQL convention.

3. **Name foreign key columns clearly.** Use `student_id` for a foreign key that references the `students` table. The pattern is `referenced_table_singular_id`.

4. **Draw your tables on paper or a whiteboard before writing SQL.** Even a rough sketch helps you spot problems early.

5. **Start simple.** Design two or three tables first. Get them working. Then add more complexity.

6. **Use plural names for tables.** A table holds many students, so call it `students`, not `student`.

---

## Quick Summary

The relational model organizes data into tables with rows and columns. Each table has a primary key that uniquely identifies every row. Foreign keys create links between tables, allowing you to represent relationships. There are three relationship types: one-to-one, one-to-many (the most common), and many-to-many (which requires a junction table). A schema is the complete blueprint of your database structure.

---

## Key Points

- A **table** stores related data in rows and columns.
- A **row** (record) is one entry in a table.
- A **column** (field) is one attribute of the data.
- A **primary key** uniquely identifies each row. It must be unique and never NULL.
- A **foreign key** is a reference from one table to another table's primary key.
- **One-to-one:** Each row in Table A links to exactly one row in Table B.
- **One-to-many:** One row in Table A links to many rows in Table B.
- **Many-to-many:** Rows in Table A and Table B link to each other through a junction table.
- A **schema** is the blueprint that describes all tables, columns, types, and relationships.

---

## Practice Questions

1. What is the difference between a row and a column? Give a real-world example of each.

2. Why should you not use a person's name as a primary key? Give at least two reasons.

3. A library has books and authors. One book can have many authors, and one author can write many books. What type of relationship is this? What tables would you need?

4. Look at the enrollments table in our school example. What would happen if you tried to insert a row with `student_id = 99` when no student with id 99 exists?

5. In a one-to-many relationship between teachers and courses, which table contains the foreign key? Why?

---

## Exercises

### Exercise 1: Design a Database for a Bookstore

A bookstore needs to track:
- Books (title, price, publication year, number of pages)
- Authors (name, country, birth year)
- Customers (name, email, phone)
- Orders (which customer bought which books, when, for how much)

Draw the tables with their columns. Identify the primary keys, foreign keys, and relationships. Use ASCII diagrams.

### Exercise 2: Identify Relationships

For each pair below, identify the relationship type (one-to-one, one-to-many, or many-to-many):

1. Country and Capital City
2. Doctor and Patients
3. Movie and Actors
4. Car and License Plate
5. Blog Post and Comments

### Exercise 3: Read the Schema

Given this schema, answer the questions below:

```
+------------------+     +------------------+     +------------------+
|    employees     |     | project_members  |     |    projects      |
+------------------+     +------------------+     +------------------+
| id (PK)          |---->| employee_id (FK) |     | id (PK)          |
| name             |     | project_id (FK)  |<----| project_name     |
| email            |     | role             |     | start_date       |
| department       |     +------------------+     | budget           |
+------------------+                               +------------------+
```

1. What type of relationship exists between employees and projects?
2. What is the junction table?
3. Can an employee work on multiple projects? Can a project have multiple employees?
4. What extra information does the junction table store besides the foreign keys?

---

## What Is Next?

You now understand the theory behind relational databases. In Chapter 3, you will get your hands dirty by **installing PostgreSQL** on your computer. You will set up the database software, connect to it, and run your first commands. Theory is important, but nothing beats actually doing it.
