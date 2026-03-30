# Chapter 24: Constraints and Keys — Guarding Your Data

## What You Will Learn

In this chapter, you will learn:

- What constraints are and why every table needs them
- How PRIMARY KEY creates a unique identifier for each row
- How FOREIGN KEY enforces relationships between tables
- How UNIQUE prevents duplicate values
- How NOT NULL stops empty fields
- How CHECK adds custom validation rules
- How DEFAULT provides automatic values
- What composite keys are and when to use them
- What CASCADE options do (ON DELETE CASCADE, ON UPDATE CASCADE, RESTRICT, SET NULL, SET DEFAULT)
- How to add and drop constraints with ALTER TABLE
- How to build a fully constrained e-commerce schema

## Why This Chapter Matters

Imagine you run a library. You have a simple rule: every book must have an ISBN number, and no two books can share the same ISBN. You also have a rule: every loan must reference a real member — you cannot lend books to people who do not exist in your system.

Now imagine your library software had no way to enforce these rules. A volunteer could accidentally enter a book without an ISBN. Another volunteer could record a loan for member number 9999, even though that member does not exist. Over time, your data becomes a mess. You have ghost loans, duplicate books, and no way to trust your records.

Constraints are the rules you attach to your tables so the database itself refuses bad data. You do not rely on the application or the person typing queries to "remember the rules." The database enforces them automatically, every single time, no exceptions.

Every professional database uses constraints. They are not optional extras — they are the foundation of data integrity.

---

## Setting Up Our Practice Tables

Let us start with simple tables and add constraints as we learn each type:

```sql
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    phone       VARCHAR(20),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO customers (first_name, last_name, email, phone) VALUES
('Alice', 'Johnson', 'alice@example.com', '555-0101'),
('Bob',   'Smith',   'bob@example.com',   '555-0102'),
('Carol', 'Davis',   'carol@example.com',  NULL);
```

Let us verify:

```sql
SELECT customer_id, first_name, last_name, email
FROM customers;
```

```
 customer_id | first_name | last_name |       email
-------------+------------+-----------+-------------------
           1 | Alice      | Johnson   | alice@example.com
           2 | Bob        | Smith     | bob@example.com
           3 | Carol      | Davis     | carol@example.com
(3 rows)
```

---

## PRIMARY KEY — The Unique Identifier

A PRIMARY KEY is a column (or set of columns) that uniquely identifies every row in a table. No two rows can have the same primary key value, and it can never be NULL.

### The House Address Analogy

Think of a primary key like a home address. Every house on a street has a unique address. You would never have two houses with the address "123 Main Street" in the same city. And you would never have a house with no address at all — the mail carrier would have no way to find it.

A primary key works the same way. Every row gets a unique "address" so the database can find it instantly.

```
+----------------------------------------------------------+
|                    PRIMARY KEY Rules                      |
+----------------------------------------------------------+
|                                                          |
|  1. Every value must be UNIQUE — no duplicates           |
|  2. The value can NEVER be NULL                          |
|  3. A table can have only ONE primary key                |
|  4. PostgreSQL automatically creates an index on it      |
|                                                          |
+----------------------------------------------------------+
```

### Creating a Table with a Primary Key

```sql
CREATE TABLE products (
    product_id  SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    price       DECIMAL(10, 2) NOT NULL,
    stock       INT NOT NULL DEFAULT 0
);
```

**Line-by-line breakdown:**

- `product_id SERIAL PRIMARY KEY` — SERIAL auto-generates increasing numbers (1, 2, 3...). PRIMARY KEY makes this column the unique identifier.
- `name VARCHAR(100) NOT NULL` — product name, up to 100 characters, cannot be empty.
- `price DECIMAL(10, 2) NOT NULL` — price with 2 decimal places, required.
- `stock INT NOT NULL DEFAULT 0` — stock count, defaults to 0 if not specified.

### What Happens When You Violate a Primary Key

```sql
INSERT INTO products (product_id, name, price) VALUES
(1, 'Laptop', 999.99);

INSERT INTO products (product_id, name, price) VALUES
(1, 'Mouse', 29.99);
```

```
ERROR:  duplicate key value violates unique constraint "products_pkey"
DETAIL:  Key (product_id)=(1) already exists.
```

PostgreSQL refuses the second insert because product_id 1 already exists. The database protects your data even if your application has a bug.

### You Cannot Insert NULL into a Primary Key

```sql
INSERT INTO products (product_id, name, price) VALUES
(NULL, 'Keyboard', 79.99);
```

```
ERROR:  null value in column "product_id" of relation "products"
        violates not-null constraint
```

---

## FOREIGN KEY — The Relationship Enforcer

A FOREIGN KEY is a column in one table that points to the primary key of another table. It creates a link between two tables and ensures that the reference is always valid.

### The Library Card Analogy

Think of a foreign key like a library card number on a loan record. When you check out a book, the library writes your card number on the loan slip. That card number must match a real person in the members list. If you tried to write card number 9999 on the loan slip but no member has that number, the librarian would refuse — that loan record would point to nobody.

```
+---------------------+         +----------------------+
|     customers       |         |       orders         |
+---------------------+         +----------------------+
| customer_id (PK)  <----------| customer_id (FK)     |
| first_name          |         | order_id (PK)        |
| last_name           |         | order_date           |
| email               |         | total                |
+---------------------+         +----------------------+

The FOREIGN KEY in orders points back to the PRIMARY KEY in customers.
An order CANNOT reference a customer_id that does not exist.
```

### Creating a Table with a Foreign Key

```sql
CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    total       DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status      VARCHAR(20) NOT NULL DEFAULT 'pending',
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

**Line-by-line breakdown:**

- `order_id SERIAL PRIMARY KEY` — unique identifier for each order.
- `customer_id INT NOT NULL` — stores which customer placed this order.
- `CONSTRAINT fk_orders_customer` — gives the foreign key a name. Naming constraints makes it easier to find and manage them later.
- `FOREIGN KEY (customer_id)` — declares customer_id as a foreign key.
- `REFERENCES customers(customer_id)` — this foreign key must match a value in the customers table's customer_id column.

### Inserting Valid and Invalid Data

```sql
-- This works: customer_id 1 (Alice) exists
INSERT INTO orders (customer_id, total)
VALUES (1, 149.99);

-- This works: customer_id 2 (Bob) exists
INSERT INTO orders (customer_id, total)
VALUES (2, 59.99);
```

```sql
-- This FAILS: customer_id 999 does not exist
INSERT INTO orders (customer_id, total)
VALUES (999, 29.99);
```

```
ERROR:  insert or update on table "orders" violates foreign key
        constraint "fk_orders_customer"
DETAIL:  Key (customer_id)=(999) is not present in table "customers".
```

PostgreSQL checks the customers table and confirms that customer 999 does not exist. The insert is rejected. Your orders table will never contain a reference to a phantom customer.

### You Cannot Delete a Referenced Parent

```sql
-- Alice (customer_id 1) has an order. Try to delete her:
DELETE FROM customers WHERE customer_id = 1;
```

```
ERROR:  update or delete on table "customers" violates foreign key
        constraint "fk_orders_customer" on table "orders"
DETAIL:  Key (customer_id)=(1) is still referenced from table "orders".
```

By default, PostgreSQL uses the RESTRICT behavior — it refuses to delete a parent row if any child rows reference it. This prevents orphan records.

---

## UNIQUE — No Duplicates Allowed

A UNIQUE constraint ensures that no two rows have the same value in a column. Unlike PRIMARY KEY, a table can have multiple UNIQUE constraints, and UNIQUE columns can contain NULL values (but only one NULL per column in most cases).

### When to Use UNIQUE

```
+------------------------------------------------------+
|              PRIMARY KEY vs UNIQUE                    |
+------------------------------------------------------+
| Feature          | PRIMARY KEY   | UNIQUE            |
+------------------+---------------+--------------------+
| Duplicates       | Not allowed   | Not allowed        |
| NULL values      | Not allowed   | Allowed (one NULL) |
| Per table limit  | Only ONE      | As many as needed  |
| Creates index    | Yes           | Yes                |
+------------------+---------------+--------------------+
```

### Example: Unique Email Addresses

We already defined email as UNIQUE in our customers table. Let us test it:

```sql
INSERT INTO customers (first_name, last_name, email)
VALUES ('Dave', 'Wilson', 'alice@example.com');
```

```
ERROR:  duplicate key value violates unique constraint
        "customers_email_key"
DETAIL:  Key (email)=(alice@example.com) already exists.
```

Alice already has that email address. Dave cannot use the same one.

### UNIQUE on Multiple Columns

You can also make a combination of columns unique. For example, a student can enroll in a course only once:

```sql
CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id    INT NOT NULL,
    course_id     INT NOT NULL,
    enrolled_at   DATE DEFAULT CURRENT_DATE,
    UNIQUE (student_id, course_id)
);
```

This means: the same student_id and course_id combination cannot appear twice. But the same student can enroll in different courses, and different students can enroll in the same course.

```sql
INSERT INTO enrollments (student_id, course_id) VALUES (1, 101);
INSERT INTO enrollments (student_id, course_id) VALUES (1, 102);  -- OK, different course
INSERT INTO enrollments (student_id, course_id) VALUES (2, 101);  -- OK, different student
INSERT INTO enrollments (student_id, course_id) VALUES (1, 101);  -- FAILS: duplicate
```

```
ERROR:  duplicate key value violates unique constraint
        "enrollments_student_id_course_id_key"
DETAIL:  Key (student_id, course_id)=(1, 101) already exists.
```

---

## NOT NULL — No Empty Fields

NOT NULL is the simplest constraint. It says: "This column must always have a value. You cannot leave it blank."

### The Registration Form Analogy

Think of NOT NULL like a required field on a registration form. The form will not submit unless you fill in your name and email. The phone number field might be optional, but the name is mandatory.

```sql
-- This FAILS: first_name is NOT NULL
INSERT INTO customers (first_name, last_name, email)
VALUES (NULL, 'Brown', 'nobody@example.com');
```

```
ERROR:  null value in column "first_name" of relation "customers"
        violates not-null constraint
DETAIL:  Failing row contains (null, Brown, nobody@example.com, null, ...).
```

### When to Use NOT NULL

Use NOT NULL on any column that should always have a value. In practice, most columns should be NOT NULL. Only leave a column nullable when a missing value genuinely makes sense (like a middle name or a phone number).

```
+----------------------------------------------+
|       Should this column be NOT NULL?        |
+----------------------------------------------+
| Column          | NOT NULL? | Why?           |
+-----------------+-----------+-----------------+
| customer_name   | YES       | Must have name  |
| email           | YES       | Must have email |
| phone           | NO        | Optional info   |
| order_total     | YES       | Must have value |
| discount_code   | NO        | May not apply   |
| created_at      | YES       | Use DEFAULT     |
+-----------------+-----------+-----------------+
```

---

## CHECK — Custom Validation Rules

A CHECK constraint lets you write custom rules that data must satisfy. Think of it like a bouncer at a club who checks whether you meet specific criteria before letting you in.

### Basic CHECK Constraints

```sql
CREATE TABLE products_v2 (
    product_id   SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    price        DECIMAL(10, 2) NOT NULL,
    stock        INT NOT NULL DEFAULT 0,
    weight_kg    DECIMAL(5, 2),
    CONSTRAINT chk_price_positive CHECK (price > 0),
    CONSTRAINT chk_stock_not_negative CHECK (stock >= 0),
    CONSTRAINT chk_weight_reasonable CHECK (weight_kg IS NULL OR weight_kg > 0)
);
```

**Line-by-line breakdown:**

- `CHECK (price > 0)` — price must be greater than zero. You cannot sell something for free or for a negative amount.
- `CHECK (stock >= 0)` — stock cannot go below zero. You cannot have negative inventory.
- `CHECK (weight_kg IS NULL OR weight_kg > 0)` — weight is optional (can be NULL), but if provided, it must be positive.

### Testing CHECK Constraints

```sql
-- This FAILS: price must be positive
INSERT INTO products_v2 (name, price, stock)
VALUES ('Free Item', 0, 10);
```

```
ERROR:  new row for relation "products_v2" violates check constraint
        "chk_price_positive"
DETAIL:  Failing row contains (1, Free Item, 0, 10, null).
```

```sql
-- This FAILS: stock cannot be negative
INSERT INTO products_v2 (name, price, stock)
VALUES ('Laptop', 999.99, -5);
```

```
ERROR:  new row for relation "products_v2" violates check constraint
        "chk_stock_not_negative"
DETAIL:  Failing row contains (2, Laptop, 999.99, -5, null).
```

```sql
-- This WORKS: all rules are satisfied
INSERT INTO products_v2 (name, price, stock, weight_kg)
VALUES ('Laptop', 999.99, 50, 2.10);
```

### CHECK with Multiple Conditions

You can combine conditions:

```sql
CREATE TABLE employees (
    employee_id  SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    salary       DECIMAL(10, 2) NOT NULL,
    hire_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    age          INT NOT NULL,
    CONSTRAINT chk_salary_range CHECK (salary >= 30000 AND salary <= 500000),
    CONSTRAINT chk_age_valid CHECK (age >= 18 AND age <= 100)
);
```

This ensures salaries fall within a reasonable range and employees are between 18 and 100 years old.

---

## DEFAULT — Automatic Values

A DEFAULT constraint provides a value automatically when you do not specify one during INSERT. Think of it like a form that pre-fills certain fields for you.

### Common DEFAULT Patterns

```sql
CREATE TABLE articles (
    article_id   SERIAL PRIMARY KEY,
    title        VARCHAR(200) NOT NULL,
    content      TEXT NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'draft',
    views        INT NOT NULL DEFAULT 0,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Line-by-line breakdown:**

- `DEFAULT 'draft'` — new articles start as drafts.
- `DEFAULT 0` — view count starts at zero.
- `DEFAULT FALSE` — articles are not published by default.
- `DEFAULT CURRENT_TIMESTAMP` — automatically records when the row was created.

### Testing DEFAULT Values

```sql
INSERT INTO articles (title, content)
VALUES ('My First Post', 'Hello, world!');

SELECT article_id, title, status, views, is_published, created_at
FROM articles;
```

```
 article_id |     title     | status | views | is_published |         created_at
------------+---------------+--------+-------+--------------+----------------------------
          1 | My First Post | draft  |     0 | f            | 2025-01-15 10:30:00.000000
(1 row)
```

We only specified title and content. The database filled in status, views, is_published, and created_at automatically.

### You Can Override DEFAULT Values

```sql
INSERT INTO articles (title, content, status, views)
VALUES ('Breaking News', 'Important story!', 'published', 500);
```

If you provide a value, the DEFAULT is ignored. DEFAULT only applies when you omit the column.

---

## Composite Keys — Two Columns as One Key

Sometimes a single column is not enough to uniquely identify a row. You need two or more columns working together. This is called a composite key (or compound key).

### The Concert Ticket Analogy

Think of concert seating. A seat is identified by its section AND seat number. Section "A" alone does not identify a seat. Seat number "12" alone does not identify a seat. But "Section A, Seat 12" uniquely identifies exactly one seat in the venue.

```
+----------------------------------------------------+
|              Composite Primary Key                  |
+----------------------------------------------------+
|                                                    |
| Section alone:  A, A, A, B, B, B  (not unique)    |
| Seat alone:     1, 2, 3, 1, 2, 3  (not unique)    |
| Section + Seat: A1, A2, A3, B1, B2, B3  (unique!) |
|                                                    |
+----------------------------------------------------+
```

### Creating a Table with a Composite Key

```sql
CREATE TABLE order_items (
    order_id   INT NOT NULL,
    product_id INT NOT NULL,
    quantity   INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    CONSTRAINT fk_items_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_items_product
        FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT chk_quantity_positive CHECK (quantity > 0)
);
```

**Line-by-line breakdown:**

- `PRIMARY KEY (order_id, product_id)` — the combination of order and product is the unique identifier. One order can have many products, and one product can appear in many orders, but the same product cannot appear twice in the same order.
- Both columns also serve as foreign keys, linking to the orders and products tables.

### Testing the Composite Key

```sql
-- Add products first
INSERT INTO products (name, price, stock) VALUES
('Laptop', 999.99, 50),
('Mouse', 29.99, 200),
('Keyboard', 79.99, 150);

-- Add items to order 1
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 999.99),  -- 1 Laptop
(1, 2, 2, 29.99);   -- 2 Mice

-- This FAILS: same order_id + product_id combination
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 3, 999.99);  -- Laptop already in order 1
```

```
ERROR:  duplicate key value violates unique constraint "order_items_pkey"
DETAIL:  Key (order_id, product_id)=(1, 1) already exists.
```

```sql
-- This WORKS: same product, different order
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(2, 1, 1, 999.99);  -- Laptop in order 2 — perfectly fine
```

---

## CASCADE Options — What Happens to Children?

When you delete or update a parent row, what should happen to the child rows that reference it? CASCADE options let you control this behavior.

### The Family Tree Analogy

Imagine a company closes a department. What happens to the employees in that department?

- **CASCADE**: All employees are also removed (deleted automatically).
- **RESTRICT**: The company cannot close the department until all employees are reassigned.
- **SET NULL**: Employees stay but their department field becomes NULL (unassigned).
- **SET DEFAULT**: Employees are moved to a default department (like "General").

```
+------------------------------------------------------------------+
|                   CASCADE Options Summary                        |
+------------------------------------------------------------------+
| Option       | What Happens to Child Rows                       |
+--------------+---------------------------------------------------+
| CASCADE      | Automatically deleted or updated along with       |
|              | the parent                                        |
| RESTRICT     | Prevent the parent from being deleted or updated  |
|              | (this is the default)                             |
| SET NULL     | Set the foreign key column to NULL                |
| SET DEFAULT  | Set the foreign key column to its DEFAULT value   |
| NO ACTION    | Similar to RESTRICT but checked at end of         |
|              | transaction                                       |
+--------------+---------------------------------------------------+
```

### ON DELETE CASCADE

When a parent row is deleted, automatically delete all child rows that reference it.

```sql
CREATE TABLE departments (
    dept_id   SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL
);

CREATE TABLE staff (
    staff_id  SERIAL PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    dept_id   INT,
    CONSTRAINT fk_staff_dept
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON DELETE CASCADE
);

INSERT INTO departments (dept_name) VALUES ('Engineering'), ('Marketing');
INSERT INTO staff (name, dept_id) VALUES
('Alice', 1), ('Bob', 1), ('Carol', 2);
```

Now watch what happens when we delete the Engineering department:

```sql
DELETE FROM departments WHERE dept_id = 1;

SELECT * FROM staff;
```

```
 staff_id | name  | dept_id
----------+-------+---------
        3 | Carol |       2
(1 row)
```

Alice and Bob were automatically deleted because they belonged to the Engineering department. The cascade happened automatically — no extra DELETE statement was needed.

### ON DELETE SET NULL

When a parent row is deleted, set the foreign key to NULL instead of deleting the child rows.

```sql
CREATE TABLE staff_v2 (
    staff_id  SERIAL PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    dept_id   INT,
    CONSTRAINT fk_staff_dept_v2
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON DELETE SET NULL
);

INSERT INTO departments (dept_name) VALUES ('Engineering');
INSERT INTO staff_v2 (name, dept_id) VALUES
('Dave', 3), ('Eve', 3);

DELETE FROM departments WHERE dept_id = 3;

SELECT * FROM staff_v2;
```

```
 staff_id | name | dept_id
----------+------+---------
        1 | Dave |    NULL
        2 | Eve  |    NULL
(2 rows)
```

Dave and Eve still exist, but their department is now NULL. They are "unassigned" rather than deleted.

### ON DELETE SET DEFAULT

When a parent row is deleted, set the foreign key to its DEFAULT value.

```sql
CREATE TABLE staff_v3 (
    staff_id  SERIAL PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    dept_id   INT DEFAULT 1,
    CONSTRAINT fk_staff_dept_v3
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON DELETE SET DEFAULT
);
```

If department 1 is the "General" department, then any employee whose department is deleted gets reassigned to "General."

### ON UPDATE CASCADE

When a parent row's primary key is updated, automatically update all child rows to match.

```sql
CREATE TABLE categories (
    category_code VARCHAR(10) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE items (
    item_id        SERIAL PRIMARY KEY,
    item_name      VARCHAR(100) NOT NULL,
    category_code  VARCHAR(10),
    CONSTRAINT fk_items_category
        FOREIGN KEY (category_code) REFERENCES categories(category_code)
        ON UPDATE CASCADE
);

INSERT INTO categories VALUES ('ELEC', 'Electronics');
INSERT INTO items (item_name, category_code) VALUES ('Laptop', 'ELEC');
```

Now update the category code:

```sql
UPDATE categories SET category_code = 'ELECTRONICS' WHERE category_code = 'ELEC';

SELECT * FROM items;
```

```
 item_id | item_name | category_code
---------+-----------+---------------
       1 | Laptop    | ELECTRONICS
(1 row)
```

The items table automatically updated to match the new category code.

### ON DELETE RESTRICT (The Default)

RESTRICT prevents deletion if any child rows exist. This is the safest option and the default in PostgreSQL.

```sql
-- With the default RESTRICT behavior:
DELETE FROM customers WHERE customer_id = 1;
```

```
ERROR:  update or delete on table "customers" violates foreign key
        constraint "fk_orders_customer" on table "orders"
```

You must delete all orders for customer 1 before you can delete the customer. This is intentional — it forces you to handle the dependent data explicitly.

### How to Choose the Right Option

```
+--------------------------------------------------------------+
|            Choosing the Right CASCADE Option                 |
+--------------------------------------------------------------+
| Scenario                          | Use                      |
+-----------------------------------+--------------------------+
| Deleting a user should delete     | ON DELETE CASCADE        |
| their posts                       |                          |
|                                   |                          |
| Deleting a manager should NOT     | ON DELETE SET NULL       |
| delete employees, just unassign   |                          |
|                                   |                          |
| Renaming a category code should   | ON UPDATE CASCADE        |
| update all products               |                          |
|                                   |                          |
| Deleting a category should be     | ON DELETE RESTRICT       |
| blocked if products exist         | (default)                |
|                                   |                          |
| Deleting a team should move       | ON DELETE SET DEFAULT    |
| members to a default team         |                          |
+-----------------------------------+--------------------------+
```

---

## Adding and Dropping Constraints with ALTER TABLE

You do not always know every constraint you need when you first create a table. ALTER TABLE lets you add, modify, or remove constraints later.

### Adding a NOT NULL Constraint

```sql
-- Make the phone column required
ALTER TABLE customers
ALTER COLUMN phone SET NOT NULL;
```

This will fail if any existing rows have NULL in the phone column. You would need to update those rows first:

```sql
-- First, fill in missing values
UPDATE customers SET phone = 'unknown' WHERE phone IS NULL;

-- Now add the constraint
ALTER TABLE customers
ALTER COLUMN phone SET NOT NULL;
```

### Dropping a NOT NULL Constraint

```sql
ALTER TABLE customers
ALTER COLUMN phone DROP NOT NULL;
```

### Adding a UNIQUE Constraint

```sql
ALTER TABLE customers
ADD CONSTRAINT uq_customers_phone UNIQUE (phone);
```

### Adding a CHECK Constraint

```sql
ALTER TABLE orders
ADD CONSTRAINT chk_total_not_negative CHECK (total >= 0);
```

### Adding a FOREIGN KEY Constraint

```sql
ALTER TABLE orders
ADD CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    ON DELETE RESTRICT;
```

### Dropping Any Named Constraint

```sql
ALTER TABLE orders
DROP CONSTRAINT chk_total_not_negative;
```

### Adding a DEFAULT Value

```sql
ALTER TABLE customers
ALTER COLUMN phone SET DEFAULT 'Not provided';
```

### Dropping a DEFAULT Value

```sql
ALTER TABLE customers
ALTER COLUMN phone DROP DEFAULT;
```

### Viewing All Constraints on a Table

In psql, you can see a table's constraints with:

```sql
\d customers
```

Or query the information schema:

```sql
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'customers';
```

```
       constraint_name       | constraint_type
-----------------------------+-----------------
 customers_pkey              | PRIMARY KEY
 customers_email_key         | UNIQUE
 fk_orders_customer          | FOREIGN KEY
(3 rows)
```

---

## Practical: Building a Fully Constrained E-Commerce Schema

Let us put everything together and build a real e-commerce database with proper constraints. This is what a professional schema looks like.

```
+-------------------+       +-------------------+       +-------------------+
|    customers      |       |     orders        |       |   order_items     |
+-------------------+       +-------------------+       +-------------------+
| customer_id (PK)  |<------| customer_id (FK)  |       | order_id (FK) (PK)|
| first_name        |       | order_id (PK)     |<------| product_id(FK)(PK)|
| last_name         |       | order_date        |       | quantity          |
| email (UNIQUE)    |       | total             |       | unit_price        |
| phone             |       | status            |       +-------------------+
| created_at        |       | shipping_address  |              |
+-------------------+       +-------------------+              |
                                                                |
+-------------------+       +-------------------+              |
|   categories      |       |    products       |--------------+
+-------------------+       +-------------------+
| category_id (PK)  |<------| category_id (FK)  |
| name (UNIQUE)     |       | product_id (PK)   |
| description       |       | name              |
+-------------------+       | price             |
                             | stock             |
                             | is_active         |
                             +-------------------+
```

### The Complete Schema

```sql
-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS ecom_order_items;
DROP TABLE IF EXISTS ecom_orders;
DROP TABLE IF EXISTS ecom_products;
DROP TABLE IF EXISTS ecom_categories;
DROP TABLE IF EXISTS ecom_customers;

-- 1. Customers table
CREATE TABLE ecom_customers (
    customer_id    SERIAL PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    email          VARCHAR(100) NOT NULL,
    phone          VARCHAR(20),
    date_of_birth  DATE,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Email must be unique across all customers
    CONSTRAINT uq_ecom_email UNIQUE (email),

    -- Age must be at least 13 if provided
    CONSTRAINT chk_ecom_age CHECK (
        date_of_birth IS NULL
        OR date_of_birth <= CURRENT_DATE - INTERVAL '13 years'
    )
);

-- 2. Categories table
CREATE TABLE ecom_categories (
    category_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    description   TEXT,

    CONSTRAINT uq_ecom_category_name UNIQUE (name)
);

-- 3. Products table
CREATE TABLE ecom_products (
    product_id    SERIAL PRIMARY KEY,
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    price         DECIMAL(10, 2) NOT NULL,
    stock         INT NOT NULL DEFAULT 0,
    category_id   INT,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Price must be positive
    CONSTRAINT chk_ecom_price CHECK (price > 0),

    -- Stock cannot be negative
    CONSTRAINT chk_ecom_stock CHECK (stock >= 0),

    -- Category must exist (SET NULL if category is deleted)
    CONSTRAINT fk_ecom_product_category
        FOREIGN KEY (category_id) REFERENCES ecom_categories(category_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- 4. Orders table
CREATE TABLE ecom_orders (
    order_id          SERIAL PRIMARY KEY,
    customer_id       INT NOT NULL,
    order_date        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total             DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status            VARCHAR(20) NOT NULL DEFAULT 'pending',
    shipping_address  TEXT NOT NULL,

    -- Total cannot be negative
    CONSTRAINT chk_ecom_total CHECK (total >= 0),

    -- Status must be one of these values
    CONSTRAINT chk_ecom_status CHECK (
        status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')
    ),

    -- Customer must exist (RESTRICT delete if they have orders)
    CONSTRAINT fk_ecom_order_customer
        FOREIGN KEY (customer_id) REFERENCES ecom_customers(customer_id)
        ON DELETE RESTRICT
);

-- 5. Order Items table (composite primary key)
CREATE TABLE ecom_order_items (
    order_id    INT NOT NULL,
    product_id  INT NOT NULL,
    quantity    INT NOT NULL,
    unit_price  DECIMAL(10, 2) NOT NULL,

    -- Composite primary key: one product per order line
    PRIMARY KEY (order_id, product_id),

    -- Quantity must be at least 1
    CONSTRAINT chk_ecom_item_qty CHECK (quantity >= 1),

    -- Unit price must be positive
    CONSTRAINT chk_ecom_item_price CHECK (unit_price > 0),

    -- Order must exist (CASCADE delete: if order is deleted, items go too)
    CONSTRAINT fk_ecom_item_order
        FOREIGN KEY (order_id) REFERENCES ecom_orders(order_id)
        ON DELETE CASCADE,

    -- Product must exist (RESTRICT: cannot delete product if it is in orders)
    CONSTRAINT fk_ecom_item_product
        FOREIGN KEY (product_id) REFERENCES ecom_products(product_id)
        ON DELETE RESTRICT
);
```

### Inserting Sample Data

```sql
-- Insert categories
INSERT INTO ecom_categories (name, description) VALUES
('Electronics', 'Gadgets and devices'),
('Clothing',    'Apparel and accessories'),
('Books',       'Physical and digital books');

-- Insert products
INSERT INTO ecom_products (name, price, stock, category_id) VALUES
('Laptop Pro 15',    1299.99, 50, 1),
('Wireless Mouse',   29.99,  200, 1),
('SQL Textbook',     49.99,  100, 3),
('Winter Jacket',    89.99,  75,  2);

-- Insert customers
INSERT INTO ecom_customers (first_name, last_name, email, phone) VALUES
('Alice', 'Johnson', 'alice.j@example.com', '555-0101'),
('Bob',   'Smith',   'bob.s@example.com',   '555-0102');

-- Insert an order for Alice
INSERT INTO ecom_orders (customer_id, total, status, shipping_address) VALUES
(1, 1359.97, 'processing', '123 Main St, Springfield');

-- Insert order items
INSERT INTO ecom_order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1299.99),  -- 1 Laptop
(1, 2, 2, 29.99);    -- 2 Mice
```

### Testing the Constraints

```sql
-- Test 1: Cannot add product with negative price
INSERT INTO ecom_products (name, price, stock, category_id)
VALUES ('Bad Product', -10.00, 5, 1);
-- ERROR: violates check constraint "chk_ecom_price"

-- Test 2: Cannot add order with invalid status
INSERT INTO ecom_orders (customer_id, total, status, shipping_address)
VALUES (1, 50.00, 'unknown', '456 Oak Ave');
-- ERROR: violates check constraint "chk_ecom_status"

-- Test 3: Cannot delete customer who has orders
DELETE FROM ecom_customers WHERE customer_id = 1;
-- ERROR: violates foreign key constraint "fk_ecom_order_customer"

-- Test 4: Deleting an order cascades to order items
DELETE FROM ecom_orders WHERE order_id = 1;

SELECT * FROM ecom_order_items WHERE order_id = 1;
```

```
 order_id | product_id | quantity | unit_price
----------+------------+----------+------------
(0 rows)
```

The order items were automatically deleted along with the order, thanks to ON DELETE CASCADE.

```sql
-- Test 5: Cannot delete a product that is referenced in order items
-- (First, let us re-create the order and items)
INSERT INTO ecom_orders (customer_id, total, status, shipping_address)
VALUES (1, 29.99, 'pending', '123 Main St, Springfield');

INSERT INTO ecom_order_items (order_id, product_id, quantity, unit_price)
VALUES (2, 2, 1, 29.99);

DELETE FROM ecom_products WHERE product_id = 2;
-- ERROR: violates foreign key constraint "fk_ecom_item_product"
```

```sql
-- Test 6: Deleting a category sets product's category_id to NULL
DELETE FROM ecom_categories WHERE category_id = 2;

SELECT product_id, name, category_id
FROM ecom_products
WHERE name = 'Winter Jacket';
```

```
 product_id |     name      | category_id
------------+---------------+-------------
          4 | Winter Jacket |        NULL
(1 row)
```

The Winter Jacket's category became NULL instead of being deleted, thanks to ON DELETE SET NULL.

---

## Common Mistakes

### Mistake 1: Forgetting NOT NULL on Foreign Key Columns

```sql
-- BAD: customer_id can be NULL
CREATE TABLE bad_orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INT,  -- Should be NOT NULL!
    total       DECIMAL(10,2)
);

-- This creates an order with no customer — an orphan!
INSERT INTO bad_orders (total) VALUES (99.99);
```

The foreign key only checks that the value matches a parent row if a value is provided. If the column allows NULL, you can have orders that belong to nobody. Always add NOT NULL to foreign key columns unless you specifically want to allow "unassigned" rows.

### Mistake 2: Naming Constraints Poorly (or Not at All)

```sql
-- BAD: auto-generated name like "orders_check" — hard to find later
CREATE TABLE bad_table (
    age INT CHECK (age >= 0)
);

-- GOOD: descriptive name tells you what the constraint checks
CREATE TABLE good_table (
    age INT,
    CONSTRAINT chk_age_not_negative CHECK (age >= 0)
);
```

When a constraint violation error appears, a descriptive name tells you immediately what went wrong. Auto-generated names like "table_column_check" are cryptic.

### Mistake 3: Using CASCADE Everywhere Without Thinking

```sql
-- DANGEROUS: Deleting a customer deletes all their orders
CONSTRAINT fk_order_customer
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    ON DELETE CASCADE
```

CASCADE is powerful but dangerous. Accidentally deleting a customer would wipe out their entire order history. Use CASCADE only when the child data truly has no meaning without the parent. Order items without an order make no sense (use CASCADE). But orders without a customer might still be needed for accounting (use RESTRICT).

### Mistake 4: Adding Constraints After Data Exists Without Checking

```sql
-- You have existing data with some NULL phone numbers
ALTER TABLE customers ALTER COLUMN phone SET NOT NULL;
-- ERROR: column "phone" of relation "customers" contains null values
```

Always check existing data before adding constraints:

```sql
-- Check for violations first
SELECT COUNT(*) FROM customers WHERE phone IS NULL;

-- Fix the data
UPDATE customers SET phone = 'Not provided' WHERE phone IS NULL;

-- Now add the constraint
ALTER TABLE customers ALTER COLUMN phone SET NOT NULL;
```

---

## Best Practices

1. **Always use PRIMARY KEY on every table.** Every table needs a unique identifier. Use SERIAL or UUID for auto-generated keys.

2. **Name your constraints explicitly.** Use a consistent naming convention like `chk_tablename_rule`, `fk_tablename_reference`, `uq_tablename_column`. This makes errors and maintenance much easier.

3. **Default to NOT NULL.** Start with NOT NULL on every column, then only remove it if you have a genuine reason to allow NULL values.

4. **Use CHECK constraints for business rules.** Prices should be positive, quantities should be at least 1, status values should be from a defined list. Enforce these at the database level, not just in your application code.

5. **Choose CASCADE options carefully.** Use RESTRICT (the default) unless you have a specific reason for CASCADE, SET NULL, or SET DEFAULT. RESTRICT is the safest option.

6. **Add constraints early.** It is much easier to add constraints when you create the table than to retrofit them onto a table with existing data.

7. **Use DEFAULT values for columns that have an obvious initial state.** Status columns, timestamps, boolean flags, and counters are great candidates for DEFAULT.

---

## Quick Summary

```
+-------------------+---------------------------------------------------+
| Constraint        | What It Does                                      |
+-------------------+---------------------------------------------------+
| PRIMARY KEY       | Unique identifier for each row (no NULLs,         |
|                   | no duplicates, one per table)                     |
| FOREIGN KEY       | Links to another table's primary key, ensuring     |
|                   | references are valid                               |
| UNIQUE            | Prevents duplicate values (allows one NULL)        |
| NOT NULL          | Column must always have a value                    |
| CHECK             | Custom validation rule (e.g., price > 0)           |
| DEFAULT           | Auto-fills a value when none is provided           |
| Composite Key     | Two or more columns together form the primary key  |
| ON DELETE CASCADE | Automatically deletes child rows                   |
| ON DELETE RESTRICT| Blocks deletion if child rows exist (default)      |
| ON DELETE SET NULL| Sets foreign key to NULL in child rows             |
| ON UPDATE CASCADE | Updates child rows when parent key changes         |
+-------------------+---------------------------------------------------+
```

---

## Key Points

- Constraints enforce rules at the database level so bad data can never sneak in, regardless of which application or user is writing data.
- PRIMARY KEY uniquely identifies each row. Every table should have one.
- FOREIGN KEY creates a relationship between two tables and prevents orphan records.
- UNIQUE prevents duplicate values in a column. A table can have multiple UNIQUE constraints.
- NOT NULL ensures a column always has a value. Most columns should be NOT NULL.
- CHECK lets you write custom rules like "price must be positive" or "status must be one of these values."
- DEFAULT provides automatic values for columns when no value is specified.
- Composite keys use two or more columns together as the primary key.
- CASCADE options control what happens to child rows when a parent is deleted or updated.
- Use ALTER TABLE to add or remove constraints after a table is created. Always check existing data before adding new constraints.

---

## Practice Questions

1. What is the difference between PRIMARY KEY and UNIQUE? Can a table have more than one of each?

2. If you have a foreign key with ON DELETE SET NULL and the foreign key column is defined as NOT NULL, what happens when you try to delete the parent row?

3. You have a products table with a CHECK constraint `CHECK (price > 0)`. Can you INSERT a row where price is NULL? Why or why not?

4. What is the difference between ON DELETE RESTRICT and ON DELETE NO ACTION in PostgreSQL?

5. Why should you name your constraints explicitly instead of letting PostgreSQL auto-generate names?

---

## Exercises

### Exercise 1: Build a School Database

Create a schema with these tables and constraints:
- **students**: student_id (PK), first_name (NOT NULL), last_name (NOT NULL), email (UNIQUE, NOT NULL), enrollment_date (DEFAULT today), gpa (CHECK between 0.0 and 4.0)
- **courses**: course_id (PK), course_name (NOT NULL, UNIQUE), credits (CHECK between 1 and 6), department (NOT NULL)
- **enrollments**: student_id (FK), course_id (FK), composite PK, grade (CHECK: A, B, C, D, F, or NULL), enrolled_at (DEFAULT now)

Test your constraints by attempting to insert invalid data.

### Exercise 2: Constraint Migration

You have an existing table with no constraints:

```sql
CREATE TABLE legacy_users (
    id INT,
    username VARCHAR(50),
    email VARCHAR(100),
    age INT,
    status VARCHAR(20)
);
```

Write ALTER TABLE statements to add: a PRIMARY KEY on id, NOT NULL on username and email, UNIQUE on email, a CHECK that age is between 13 and 150, a CHECK that status is one of 'active', 'inactive', or 'banned', and a DEFAULT of 'active' for status.

### Exercise 3: Design a Booking System

Design a hotel booking schema with proper constraints and CASCADE options. You need tables for hotels, rooms, guests, and bookings. Think carefully about what should happen when a hotel is deleted (should rooms be deleted too?), when a guest is deleted (should bookings be kept for records?), and what CHECK constraints you need (check-out after check-in, price positive, room capacity at least 1).

---

## What Is Next?

In Chapter 25, you will learn about **Transactions** — how to group multiple SQL statements into a single all-or-nothing operation. Transactions work hand-in-hand with constraints: constraints ensure individual rows are valid, while transactions ensure that multi-step operations either succeed completely or fail completely. Together, they form the backbone of reliable database applications.
