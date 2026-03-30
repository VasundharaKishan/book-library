# Chapter 23: ER Diagrams (Entity-Relationship Diagrams)

## What You Will Learn

In this chapter, you will learn how to design databases visually using Entity-Relationship (ER) diagrams. You will discover how to identify entities, define attributes, and draw relationships with proper cardinality. You will also learn crow's foot notation and practice converting ER diagrams into actual SQL tables.

## Why This Chapter Matters

Imagine building a house without a blueprint. You start laying bricks, realize the kitchen is too small, knock down a wall, rebuild it, then discover the plumbing does not reach the bathroom. Every mistake costs time and money.

Database design works the same way. If you jump straight into writing CREATE TABLE statements without planning, you will inevitably discover missing relationships, redundant columns, and structural problems that are painful to fix once data is stored.

ER diagrams are your **blueprint**. They let you plan your entire database visually before writing any SQL. You can spot problems, discuss the design with teammates, and make changes on paper instead of in production. Every professional database project starts with an ER diagram.

---

## What Is an ER Diagram?

An ER diagram is a visual representation of the data in your system and the relationships between different pieces of data. It was introduced by Peter Chen in 1976 and has become the standard way to design relational databases.

An ER diagram has three main components:

```
+------------------+
|   ENTITIES       |  =  The "things" you want to store data about
|   (rectangles)   |     (Customer, Order, Product)
+------------------+

+------------------+
|   ATTRIBUTES     |  =  The properties of each entity
|   (listed inside)|     (name, email, price)
+------------------+

+------------------+
|   RELATIONSHIPS  |  =  How entities are connected
|   (lines)        |     (Customer "places" Order)
+------------------+
```

Think of it like planning a school:
- **Entities** = Students, Teachers, Courses, Classrooms
- **Attributes** = Student has name, age, grade. Course has title, credits.
- **Relationships** = Students *enroll in* Courses. Teachers *teach* Courses.

---

## Entities

An entity represents a "thing" or concept that you want to track in your database. Each entity becomes a table in your final database.

### How to Identify Entities

Ask yourself: "What are the main things I need to store information about?"

- In an **e-commerce system**: Customers, Products, Orders, Categories
- In a **library**: Members, Books, Authors, Loans
- In a **hospital**: Patients, Doctors, Appointments, Departments

### Representing Entities

In an ER diagram, entities are drawn as rectangles with the entity name inside.

```
+------------+    +------------+    +------------+
|  CUSTOMER  |    |   ORDER    |    |  PRODUCT   |
+------------+    +------------+    +------------+
```

Each entity will have a **primary key** attribute that uniquely identifies each instance (each row in the eventual table).

---

## Attributes

Attributes are the properties or characteristics of an entity. They become columns in your table.

### Types of Attributes

```
+-------------------------+-------------------------------------------+
| Attribute Type          | Example                                   |
+-------------------------+-------------------------------------------+
| Simple                  | first_name, price, quantity                |
| Composite               | full_name = first_name + last_name        |
| Derived                 | age (calculated from date_of_birth)       |
| Multi-valued            | phone_numbers (a person may have several) |
| Key (Primary Key)       | customer_id, product_id                   |
+-------------------------+-------------------------------------------+
```

### Representing Attributes

Attributes are listed inside the entity rectangle. The primary key is underlined or marked with (PK).

```
+---------------------+
|      CUSTOMER       |
+---------------------+
| customer_id  (PK)   |
| first_name           |
| last_name            |
| email                |
| phone                |
| created_at           |
+---------------------+
```

---

## Relationships

Relationships describe how entities are connected to each other. They answer questions like:
- A Customer *places* how many Orders?
- An Order *contains* how many Products?
- A Doctor *treats* how many Patients?

### Representing Relationships

Relationships are shown as lines connecting entities, with a label describing the relationship.

```
+------------+                   +------------+
|  CUSTOMER  |----< places >----|   ORDER    |
+------------+                   +------------+
```

---

## Cardinality: How Many?

Cardinality defines the **number of instances** of one entity that can be associated with instances of another entity. There are three main types:

### One-to-One (1:1)

Each instance of Entity A is associated with exactly one instance of Entity B, and vice versa.

**Example:** Each employee has exactly one company laptop. Each laptop is assigned to exactly one employee.

```
+------------+        1:1        +------------+
|  EMPLOYEE  |------------------| LAPTOP     |
+------------+                   +------------+

One Employee  <-->  One Laptop
```

**Real-world examples:**
- Person and Passport
- Employee and Parking Spot
- Country and Capital City

### One-to-Many (1:N)

Each instance of Entity A can be associated with many instances of Entity B, but each instance of Entity B is associated with exactly one instance of Entity A.

**Example:** A customer can place many orders, but each order belongs to exactly one customer.

```
+------------+        1:N        +------------+
|  CUSTOMER  |---||-----------|<-|   ORDER    |
+------------+                   +------------+

One Customer  -->  Many Orders
One Order     -->  One Customer
```

**Real-world examples:**
- Department and Employees (one department has many employees)
- Author and Books (one author writes many books)
- Parent and Children

### Many-to-Many (M:N)

Each instance of Entity A can be associated with many instances of Entity B, and each instance of Entity B can be associated with many instances of Entity A.

**Example:** A student can enroll in many courses. A course can have many students.

```
+------------+        M:N        +------------+
|  STUDENT   |------|<---->|-----|  COURSE    |
+------------+                   +------------+

One Student   -->  Many Courses
One Course    -->  Many Students
```

**Real-world examples:**
- Students and Courses
- Actors and Movies
- Products and Orders (an order has many products; a product appears in many orders)

> **Important:** Many-to-many relationships cannot be directly implemented in a relational database. They require a **junction table** (also called a bridge table or associative table). We will cover this in the conversion section.

---

## Crow's Foot Notation

Crow's foot notation is the most widely used notation for ER diagrams in practice. It uses special symbols at the ends of relationship lines to indicate cardinality.

### The Symbols

```
----||----    Exactly one (mandatory)
----O|----    Zero or one (optional)
----|<----    One or many (at least one)
----O<----    Zero or many (optional, could be none)

Symbol Key:
  ||   = One (and only one)
  O|   = Zero or one
  |<   = One or many     (the "crow's foot" or "chicken foot")
  O<   = Zero or many
```

### Reading Crow's Foot Diagrams

Read the symbols from the perspective of each entity.

```
CUSTOMER  ||--------O<  ORDER

Read from left to right:
  "A Customer can have ZERO OR MANY (O<) Orders."

Read from right to left:
  "An Order belongs to exactly ONE (||) Customer."
```

### Common Relationships in Crow's Foot

```
One-to-One (mandatory on both sides):
  EMPLOYEE  ||--------||  PARKING_SPOT

One-to-Many (customer must exist, orders are optional):
  CUSTOMER  ||--------O<  ORDER

Many-to-Many (through junction table):
  STUDENT  >O--------O<  ENROLLMENT  >O--------O<  COURSE
```

### Full Crow's Foot Example

```
+------------+          +------------+          +--------------+
|  CUSTOMER  |          |   ORDER    |          | ORDER_ITEM   |
+------------+          +------------+          +--------------+
| customer_id|          | order_id   |          | item_id      |
| name       |---||--O<-| order_date |---||--O<-| quantity      |
| email      |          | customer_id|          | order_id     |
| phone      |          | total      |          | product_id   |
+------------+          +------------+          +--------------+
                                                      |
                                                   O| |
                                                   || |
                                                      |
                                                +--------------+
                                                |   PRODUCT    |
                                                +--------------+
                                                | product_id   |
                                                | name         |
                                                | price        |
                                                | category     |
                                                +--------------+

Reading:
  - One Customer has zero or many Orders
  - One Order belongs to exactly one Customer
  - One Order has zero or many Order Items
  - One Order Item belongs to exactly one Order
  - One Product appears in zero or many Order Items
  - One Order Item refers to exactly one Product
```

---

## Drawing ER Diagrams: Library System

Let us design a library management system step by step.

### Step 1: Identify Entities

What "things" does a library need to track?

- **Members** -- people who borrow books
- **Books** -- the physical books in the library
- **Authors** -- who wrote the books
- **Loans** -- the borrowing transactions
- **Categories** -- book categories (Fiction, Science, History)

### Step 2: Define Attributes

```
+---------------------+    +---------------------+    +---------------------+
|       MEMBER        |    |        BOOK         |    |       AUTHOR        |
+---------------------+    +---------------------+    +---------------------+
| member_id    (PK)   |    | book_id      (PK)   |    | author_id    (PK)   |
| first_name          |    | title               |    | first_name          |
| last_name           |    | isbn                |    | last_name           |
| email               |    | publish_year        |    | birth_year          |
| phone               |    | category_id  (FK)   |    | nationality         |
| join_date            |    | copies_available    |    +---------------------+
+---------------------+    +---------------------+

+---------------------+    +---------------------+
|        LOAN         |    |      CATEGORY       |
+---------------------+    +---------------------+
| loan_id      (PK)   |    | category_id  (PK)   |
| member_id    (FK)   |    | category_name       |
| book_id      (FK)   |    | description         |
| loan_date           |    +---------------------+
| due_date            |
| return_date         |
+---------------------+
```

### Step 3: Define Relationships

```
MEMBER  ||--------O<  LOAN
  "A member can have zero or many loans."
  "A loan belongs to exactly one member."

BOOK  ||--------O<  LOAN
  "A book can have zero or many loans."
  "A loan is for exactly one book."

CATEGORY  ||--------O<  BOOK
  "A category contains zero or many books."
  "A book belongs to exactly one category."

AUTHOR  >O--------O<  BOOK_AUTHOR  >O--------O<  BOOK
  "An author can write many books."
  "A book can have many authors."
  (Many-to-many, needs junction table BOOK_AUTHOR)
```

### Step 4: Draw the Complete ER Diagram

```
+----------+                              +----------+
| CATEGORY |                              |  AUTHOR  |
+----------+                              +----------+
|cat_id(PK)|                              |auth_id(PK)|
|cat_name  |                              |first_name|
|descript. |                              |last_name |
+----------+                              |birth_year|
     |                                    +----------+
     | 1                                       |
     |                                         | M
     | N                                       |
+----------+       +----------+       +-------------+
|   BOOK   |       |   LOAN   |       | BOOK_AUTHOR |
+----------+       +----------+       +-------------+
|book_id(PK)|--||--O<|loan_id(PK)|    |book_id (FK) |
|title      |      |member_id(FK)|   |author_id(FK)|
|isbn       |      |book_id(FK) |    +-------------+
|pub_year   |      |loan_date   |          |
|cat_id(FK) |      |due_date    |          | N
|copies     |      |return_date |          |
+----------+       +----------+       +----------+
                        |              |   BOOK   |
                        | N            +----------+
                        |
                   +----------+
                   |  MEMBER  |
                   +----------+
                   |mem_id(PK)|--||--O< LOAN
                   |first_name|
                   |last_name |
                   |email     |
                   |phone     |
                   |join_date |
                   +----------+
```

---

## Drawing ER Diagrams: E-Commerce System

### Entities and Relationships

```
+-------------+       +-------------+       +---------------+
|  CUSTOMER   |       |    ORDER    |       |  ORDER_ITEM   |
+-------------+       +-------------+       +---------------+
|customer_id  |       |order_id     |       |item_id        |
|first_name   |-||--O<|order_date   |-||--O<|order_id   (FK)|
|last_name    |       |customer_id  |       |product_id (FK)|
|email        |       |ship_address |       |quantity       |
|password_hash|       |total_amount |       |unit_price     |
|created_at   |       |status       |       |line_total     |
+-------------+       +-------------+       +---------------+
                                                   |
                                                   |O<
                                                   |
                                                   |||
                                            +---------------+
                                            |   PRODUCT     |
+-------------+                             +---------------+
|  CATEGORY   |                             |product_id     |
+-------------+                             |product_name   |
|category_id  |-||------------------------O<|description    |
|cat_name     |                             |price          |
|parent_cat_id|                             |stock_quantity |
+-------------+                             |category_id(FK)|
      |                                     +---------------+
      |
      +----> (self-referencing for sub-categories)


+-------------+       +-------------+
|   REVIEW    |       |   PAYMENT   |
+-------------+       +-------------+
|review_id    |       |payment_id   |
|product_id   |       |order_id (FK)|
|customer_id  |       |amount       |
|rating       |       |method       |
|comment      |       |paid_at      |
|created_at   |       |status       |
+-------------+       +-------------+
```

**Relationships:**
- Customer 1 --> N Orders (one customer places many orders)
- Order 1 --> N Order Items (one order contains many items)
- Product 1 --> N Order Items (one product appears in many order items)
- Category 1 --> N Products (one category has many products)
- Category 1 --> N Category (self-referencing for subcategories)
- Customer 1 --> N Reviews (one customer writes many reviews)
- Product 1 --> N Reviews (one product has many reviews)
- Order 1 --> 1 Payment (one order has one payment)

---

## Drawing ER Diagrams: Hospital System

### Entities and Relationships

```
+--------------+       +----------------+       +--------------+
|   PATIENT    |       |  APPOINTMENT   |       |    DOCTOR    |
+--------------+       +----------------+       +--------------+
|patient_id(PK)|       |appt_id    (PK) |       |doctor_id(PK) |
|first_name    |-||--O<|patient_id (FK) |>O--||+|first_name    |
|last_name     |       |doctor_id  (FK) |       |last_name     |
|dob           |       |appt_date       |       |specialty     |
|gender        |       |appt_time       |       |phone         |
|phone         |       |reason          |       |dept_id  (FK) |
|address       |       |status          |       +--------------+
|blood_type    |       +----------------+              |
+--------------+                                       | N
      |                                                |
      | 1                                              | 1
      |                                          +--------------+
      | N                                        |  DEPARTMENT  |
+--------------+                                 +--------------+
| PRESCRIPTION |                                 |dept_id  (PK) |
+--------------+                                 |dept_name     |
|rx_id    (PK) |                                 |floor         |
|patient_id(FK)|                                 |phone         |
|doctor_id(FK) |                                 +--------------+
|medication    |
|dosage        |
|start_date    |
|end_date      |
+--------------+

+--------------+       +--------------+
|     ROOM     |       |  ADMISSION   |
+--------------+       +--------------+
|room_id  (PK) |       |admission_id  |
|room_number   |-||--O<|room_id  (FK) |>O--||--PATIENT
|room_type     |       |patient_id(FK)|
|floor         |       |admit_date    |
|is_available  |       |discharge_date|
+--------------+       |doctor_id(FK) |
                       +--------------+
```

**Relationships:**
- Patient 1 --> N Appointments
- Doctor 1 --> N Appointments
- Patient 1 --> N Prescriptions
- Doctor 1 --> N Prescriptions
- Department 1 --> N Doctors
- Room 1 --> N Admissions
- Patient 1 --> N Admissions

---

## Converting ER Diagrams to Tables

Once you have an ER diagram, converting it to SQL tables follows clear rules.

### Rule 1: Each Entity Becomes a Table

```
ER Entity:                    SQL Table:
+------------+                CREATE TABLE customers (
|  CUSTOMER  |                    customer_id  SERIAL PRIMARY KEY,
+------------+                    first_name   VARCHAR(50),
| customer_id|                    last_name    VARCHAR(50),
| first_name |                    email        VARCHAR(100),
| last_name  |      =====>        phone        VARCHAR(20)
| email      |                );
| phone      |
+------------+
```

### Rule 2: 1:N Relationships Use Foreign Keys

The "many" side gets a foreign key pointing to the "one" side.

```
CUSTOMER  ||--------O<  ORDER

CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    order_date   DATE,
    customer_id  INTEGER REFERENCES customers(customer_id),  -- FK
    total_amount NUMERIC(10,2)
);
```

### Rule 3: M:N Relationships Need a Junction Table

Many-to-many relationships cannot be directly represented. You create a junction table with foreign keys to both entities.

```
STUDENT  >O--------O<  COURSE
      (Many-to-Many)

Becomes three tables:

CREATE TABLE students (
    student_id  SERIAL PRIMARY KEY,
    name        VARCHAR(100)
);

CREATE TABLE courses (
    course_id   SERIAL PRIMARY KEY,
    title       VARCHAR(100)
);

CREATE TABLE enrollments (                -- Junction table
    student_id  INTEGER REFERENCES students(student_id),
    course_id   INTEGER REFERENCES courses(course_id),
    enrolled_at DATE DEFAULT CURRENT_DATE,
    grade       VARCHAR(2),
    PRIMARY KEY (student_id, course_id)   -- Composite PK
);
```

### Rule 4: 1:1 Relationships Use Foreign Key with UNIQUE

Either table can hold the foreign key. Add a UNIQUE constraint to enforce the one-to-one relationship.

```
EMPLOYEE  ||--------||  PARKING_SPOT

CREATE TABLE parking_spots (
    spot_id      SERIAL PRIMARY KEY,
    spot_number  VARCHAR(10),
    location     VARCHAR(50)
);

CREATE TABLE employees (
    employee_id  SERIAL PRIMARY KEY,
    name         VARCHAR(100),
    spot_id      INTEGER UNIQUE REFERENCES parking_spots(spot_id)  -- FK + UNIQUE
);
```

### Conversion Summary

```
+-------------------+-------------------------------------------+
| ER Concept        | SQL Implementation                        |
+-------------------+-------------------------------------------+
| Entity            | CREATE TABLE                              |
| Attribute         | Column in the table                       |
| Primary Key       | PRIMARY KEY constraint                    |
| 1:1 Relationship  | FK with UNIQUE constraint                 |
| 1:N Relationship  | FK on the "many" side                     |
| M:N Relationship  | Junction table with two FKs               |
+-------------------+-------------------------------------------+
```

---

## Complete Conversion Example: Library System

Let us convert our library ER diagram to actual SQL.

```sql
-- Independent tables first (no foreign keys needed)

CREATE TABLE categories (
    category_id    SERIAL PRIMARY KEY,
    category_name  VARCHAR(50) NOT NULL,
    description    TEXT
);

CREATE TABLE authors (
    author_id      SERIAL PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    birth_year     INTEGER,
    nationality    VARCHAR(50)
);

CREATE TABLE members (
    member_id      SERIAL PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    email          VARCHAR(100) UNIQUE,
    phone          VARCHAR(20),
    join_date      DATE DEFAULT CURRENT_DATE
);

-- Tables with foreign keys

CREATE TABLE books (
    book_id          SERIAL PRIMARY KEY,
    title            VARCHAR(200) NOT NULL,
    isbn             VARCHAR(20) UNIQUE,
    publish_year     INTEGER,
    category_id      INTEGER REFERENCES categories(category_id),
    copies_available INTEGER DEFAULT 1
);

-- Junction table for M:N relationship (Book <-> Author)

CREATE TABLE book_authors (
    book_id    INTEGER REFERENCES books(book_id),
    author_id  INTEGER REFERENCES authors(author_id),
    PRIMARY KEY (book_id, author_id)
);

-- Loans table (references both members and books)

CREATE TABLE loans (
    loan_id      SERIAL PRIMARY KEY,
    member_id    INTEGER NOT NULL REFERENCES members(member_id),
    book_id      INTEGER NOT NULL REFERENCES books(book_id),
    loan_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date     DATE NOT NULL,
    return_date  DATE
);
```

---

## Tools for Drawing ER Diagrams

While ASCII diagrams are great for learning and quick sketches, professional projects benefit from dedicated tools.

### Free Tools

- **draw.io (diagrams.net)** -- Free, browser-based diagramming tool. Supports ER diagram shapes and crow's foot notation. Can export to PNG, SVG, and PDF. Works offline. This is an excellent choice for beginners.

- **dbdiagram.io** -- Free online tool specifically designed for database diagrams. You write a simple text-based syntax and it generates the visual diagram. Very fast for creating schemas.

Example dbdiagram.io syntax:
```
Table customers {
  customer_id integer [pk, increment]
  first_name varchar
  last_name varchar
  email varchar [unique]
}

Table orders {
  order_id integer [pk, increment]
  customer_id integer [ref: > customers.customer_id]
  order_date date
  total numeric
}
```

- **pgModeler** -- Open-source tool specifically for PostgreSQL. Can generate SQL from diagrams and reverse-engineer diagrams from existing databases.

### Tips for Drawing ER Diagrams

1. **Start with entities.** List all the "things" you need to track before thinking about relationships.
2. **Add attributes.** For each entity, list all the properties you need to store.
3. **Identify primary keys.** Every entity needs a unique identifier.
4. **Draw relationships.** Connect entities and label the relationships.
5. **Determine cardinality.** For each relationship, ask "how many?" on both sides.
6. **Handle M:N relationships.** Add junction tables where needed.
7. **Review for normalization.** Check that your design follows the normal forms from Chapter 22.

---

## Common Mistakes

### Mistake 1: Skipping the ER Diagram

Jumping straight into SQL without planning leads to redesigns later. Even a rough sketch on paper saves time.

### Mistake 2: Confusing Entities with Attributes

```
WRONG: Making "phone_number" an entity
  +---------------+
  | PHONE_NUMBER  |   <-- This is an attribute, not an entity!
  +---------------+

RIGHT: Phone number is an attribute of Customer
  +------------+
  |  CUSTOMER  |
  +------------+
  | phone      |
  +------------+
```

An entity is something that has its own attributes and exists independently. "Phone number" is a property of a customer, not a thing on its own (unless you are building a phone system where phone numbers have their own attributes like carrier, type, etc.).

### Mistake 3: Forgetting Junction Tables for M:N

```
WRONG: Trying to implement M:N directly
  students.course_id --> courses.course_id
  (But a student can have MANY courses! A single FK does not work.)

RIGHT: Use a junction table
  students --> enrollments <-- courses
```

### Mistake 4: Wrong Cardinality

Think carefully about the business rules. "Can a book have zero authors?" (Probably not.) "Can a customer have zero orders?" (Yes, they just signed up.) Getting cardinality wrong leads to incorrect constraints in your database.

### Mistake 5: Not Including All Necessary Attributes

Forgetting important attributes at the design stage means ALTER TABLE later. Take time to think through what data each entity needs.

---

## Best Practices

1. **Always start with an ER diagram.** Even for small projects, spending 15 minutes on an ER diagram saves hours of rework.

2. **Use consistent naming.** Pick a convention (singular or plural table names, snake_case or camelCase) and stick with it throughout.

3. **Include data types in your diagram.** Knowing that `price` is NUMERIC(10,2) versus INTEGER affects your design decisions.

4. **Review with stakeholders.** Show your ER diagram to the people who will use the system. They can catch missing entities and incorrect relationships that you might miss.

5. **Iterate.** Your first ER diagram will not be perfect. Draw it, review it, improve it, and repeat.

6. **Keep it readable.** Avoid crossing lines when possible. Group related entities together. Use colors or sections for large diagrams.

7. **Version control your diagrams.** Save your ER diagram files alongside your code. When the schema changes, update the diagram.

---

## Quick Summary

```
+---------------------------+------------------------------------------+
| Concept                   | Description                              |
+---------------------------+------------------------------------------+
| Entity                    | A thing to store data about (table)      |
+---------------------------+------------------------------------------+
| Attribute                 | A property of an entity (column)         |
+---------------------------+------------------------------------------+
| Relationship              | A connection between entities             |
+---------------------------+------------------------------------------+
| 1:1 Cardinality           | One to one (FK + UNIQUE)                 |
+---------------------------+------------------------------------------+
| 1:N Cardinality           | One to many (FK on the "many" side)      |
+---------------------------+------------------------------------------+
| M:N Cardinality           | Many to many (junction table)            |
+---------------------------+------------------------------------------+
| Crow's Foot Notation      | Industry-standard visual notation        |
+---------------------------+------------------------------------------+
| Junction Table            | Bridge table for M:N relationships       |
+---------------------------+------------------------------------------+
```

---

## Key Points

- **ER diagrams** are visual blueprints for database design. Always create one before writing SQL.
- **Entities** are the things you store data about. They become tables.
- **Attributes** are properties of entities. They become columns.
- **Relationships** connect entities. They are implemented with foreign keys and junction tables.
- **Cardinality** defines how many instances relate to each other: 1:1, 1:N, or M:N.
- **Crow's foot notation** is the most common way to show cardinality in professional diagrams.
- **M:N relationships** always require a **junction table** with foreign keys to both entities.
- **Convert ER to SQL** by making entities into tables, attributes into columns, and relationships into foreign keys.
- Tools like **draw.io** and **dbdiagram.io** make creating ER diagrams fast and free.
- **Review and iterate** on your ER diagram before building the database.

---

## Practice Questions

1. What are the three main components of an ER diagram? Give an example of each from a school system.

2. Explain the difference between 1:1, 1:N, and M:N relationships. For each, give a real-world example and explain how it would be implemented in SQL.

3. Why can many-to-many relationships not be directly implemented in a relational database? What solution do we use instead?

4. In crow's foot notation, what does `||--------O<` mean? Read it from both directions.

5. You are designing a music streaming service. Identify at least five entities and their relationships (with cardinality).

---

## Exercises

### Exercise 1: Design a Library System ER Diagram

Draw a complete ER diagram for a library system with these requirements:
- Members can borrow books. Track loan date and due date.
- Books can have multiple authors. Authors can write multiple books.
- Books belong to categories (Fiction, Non-Fiction, Science, etc.).
- Members can write reviews for books (rating 1-5 and comment).

Show all entities, attributes, relationships, and cardinality using crow's foot notation. Then write the CREATE TABLE statements to implement your design.

### Exercise 2: E-Commerce ER Diagram

Design an ER diagram for an online store:
- Customers can place orders containing multiple products.
- Products belong to categories. Categories can have subcategories.
- Customers can leave reviews on products.
- Orders have a shipping address and a billing address.
- Track order status history (ordered, processing, shipped, delivered).

Draw the ER diagram and convert it to CREATE TABLE statements.

### Exercise 3: Convert an Existing Design

Given these business rules, draw the ER diagram and write the SQL:
- A hospital has many departments.
- Each department has many doctors. A doctor belongs to one department.
- Patients can have appointments with doctors.
- Doctors can prescribe medications to patients during appointments.
- Track the medication name, dosage, and duration for each prescription.

---

## What Is Next?

Now that you can design your database visually with ER diagrams, the next chapter will cover **Constraints and Keys** in depth. You have already seen PRIMARY KEY and FOREIGN KEY in this chapter. Next, you will learn about all the constraint types (UNIQUE, NOT NULL, CHECK, DEFAULT) and how to use CASCADE rules to control what happens when referenced data is deleted or updated. Constraints are the rules that keep your data clean and consistent.
