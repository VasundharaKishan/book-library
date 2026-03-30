# Chapter 22: Normalization

## What You Will Learn

In this chapter, you will learn how to organize your database tables to eliminate redundancy, prevent data anomalies, and maintain data integrity. You will discover the three main normal forms (1NF, 2NF, 3NF) and Boyce-Codd Normal Form (BCNF). You will also learn when it makes sense to break the rules through denormalization.

## Why This Chapter Matters

Imagine you keep all your personal information -- contacts, appointments, shopping lists, bank records, medical history -- in one giant notebook. At first it seems convenient. Everything is in one place. But soon you run into problems:

- You wrote your doctor's phone number on three different pages. When the number changes, you update it on one page but forget the other two. Now you have conflicting information.
- You want to delete a canceled appointment, but the appointment entry also contains your dentist's address. Deleting the appointment means losing the address.
- You want to add a new contact, but the notebook requires you to also write an appointment date. You do not have an appointment yet, so what do you write?

These are exactly the problems that happen in poorly designed databases. Normalization is the process of organizing your data to prevent these issues. It is one of the most fundamental concepts in database design, and understanding it will make you a significantly better database developer.

---

## The Messy Spreadsheet: Our Starting Point

Let us start with a real-world scenario. A small bookstore tracks orders in a single spreadsheet.

```
+---------+--------+----------+-----------+---------+--------+----------+--------+-------+
|order_id |cust_name|cust_email|cust_phone |book_title|author |author_email|price  |qty    |
+---------+--------+----------+-----------+---------+--------+----------+--------+-------+
|1001     |Alice   |alice@    |555-0101   |SQL Made |Bob Lee |bob@pub   |29.99   |2      |
|         |        |mail.com  |           |Easy     |        |.com      |        |       |
+---------+--------+----------+-----------+---------+--------+----------+--------+-------+
|1001     |Alice   |alice@    |555-0101   |Data     |Carol   |carol@pub |39.99   |1      |
|         |        |mail.com  |           |Design   |King    |.com      |        |       |
+---------+--------+----------+-----------+---------+--------+----------+--------+-------+
|1002     |Dave    |dave@     |555-0202   |SQL Made |Bob Lee |bob@pub   |29.99   |1      |
|         |        |mail.com  |           |Easy     |        |.com      |        |       |
+---------+--------+----------+-----------+---------+--------+----------+--------+-------+
|1003     |Alice   |alice@    |555-0101   |NoSQL    |Bob Lee |bob@pub   |34.99   |3      |
|         |        |mail.com  |           |Basics   |        |.com      |        |       |
+---------+--------+----------+-----------+---------+--------+----------+--------+-------+
```

This spreadsheet has many problems. Let us explore them.

---

## Data Anomalies: Why Bad Design Hurts

### Update Anomaly

Alice's email appears in three rows. If she changes her email, you must update all three rows. If you miss even one, her data becomes inconsistent.

```
Before update:
  Row 1: Alice, alice@mail.com   <-- Updated
  Row 2: Alice, alice@mail.com   <-- FORGOT to update!
  Row 3: Alice, alice_new@mail.com  <-- Wait, which is correct?

This is the UPDATE ANOMALY.
```

### Insert Anomaly

You want to add a new book to your catalog, but since all book information is stored alongside orders, you cannot add a book until someone orders it. What if you want to record a book that nobody has bought yet?

```
Trying to insert:
  order_id: ???       <-- No order yet!
  cust_name: ???      <-- No customer yet!
  book_title: "New SQL Book"
  author: "Jane Doe"
  price: 24.99

Cannot insert! The table requires order and customer data.
This is the INSERT ANOMALY.
```

### Delete Anomaly

Dave only has one order. If you delete that order, you lose all record that Dave was ever a customer. You also lose the fact that "SQL Made Easy" costs 29.99, if Dave's row was the only one with that information.

```
Deleting order 1002:
  Lose Dave's name: Dave        -- Gone!
  Lose Dave's email: dave@mail.com  -- Gone!
  Lose Dave's phone: 555-0202     -- Gone!

This is the DELETE ANOMALY.
```

### Summary of Anomalies

```
+------------------+---------------------------------------------------+
| Anomaly          | Problem                                           |
+------------------+---------------------------------------------------+
| Update Anomaly   | Must update the same fact in multiple rows.       |
|                  | Miss one and data becomes inconsistent.           |
+------------------+---------------------------------------------------+
| Insert Anomaly   | Cannot add new data without unrelated data.       |
|                  | e.g., Cannot add a book without an order.         |
+------------------+---------------------------------------------------+
| Delete Anomaly   | Deleting one fact accidentally removes other      |
|                  | unrelated facts.                                  |
+------------------+---------------------------------------------------+
```

Normalization eliminates these anomalies by organizing data into separate, focused tables.

---

## First Normal Form (1NF): Atomic Values

A table is in **First Normal Form** if:

1. Every column contains **atomic** (indivisible) values. No lists, no sets, no comma-separated values in a single cell.
2. Each row is **unique** (there is a way to identify each row).
3. There are **no repeating groups** of columns.

### Violation: Non-Atomic Values

```
BAD: Comma-separated values in one column

+---------+-----------+----------------------------+
|order_id | cust_name | books_ordered              |
+---------+-----------+----------------------------+
| 1001    | Alice     | SQL Made Easy, Data Design |
| 1002    | Dave      | SQL Made Easy              |
+---------+-----------+----------------------------+

Problem: How do you query "find all orders containing SQL Made Easy"?
You would need string searching, which is slow and error-prone.
```

### Violation: Repeating Groups

```
BAD: Multiple columns for the same kind of data

+---------+-----------+--------+--------+--------+--------+
|order_id | cust_name | book_1 | price_1| book_2 | price_2|
+---------+-----------+--------+--------+--------+--------+
| 1001    | Alice     | SQL    | 29.99  | Data   | 39.99  |
|         |           | Made   |        | Design |        |
| 1002    | Dave      | SQL    | 29.99  | (null) | (null) |
|         |           | Made   |        |        |        |
+---------+-----------+--------+--------+--------+--------+

Problem: What if someone orders 10 books? 50? You cannot keep
adding columns. And queries become nightmarish.
```

### Fixed: 1NF Version

```
GOOD: Each cell has one value, each row is unique

+---------+-----------+-----------+-------+-----+
|order_id | cust_name | book_title| price | qty |
+---------+-----------+-----------+-------+-----+
| 1001    | Alice     | SQL Made  | 29.99 |  2  |
|         |           | Easy      |       |     |
| 1001    | Alice     | Data      | 39.99 |  1  |
|         |           | Design    |       |     |
| 1002    | Dave      | SQL Made  | 29.99 |  1  |
|         |           | Easy      |       |     |
+---------+-----------+-----------+-------+-----+

Each cell contains exactly one value.
No repeating column groups.
```

### 1NF Rule Summary

```
+-------------------------------+--------------------------------+
| Rule                          | Example of Violation           |
+-------------------------------+--------------------------------+
| Atomic values                 | "SQL, Data Design" in one cell |
| No repeating groups           | book_1, book_2, book_3 columns|
| Rows are uniquely identifiable| No primary key                 |
+-------------------------------+--------------------------------+
```

---

## Second Normal Form (2NF): No Partial Dependencies

A table is in **Second Normal Form** if:

1. It is already in 1NF.
2. Every non-key column depends on the **entire** primary key, not just part of it.

2NF only applies to tables with **composite primary keys** (keys made of two or more columns). If your primary key is a single column, the table automatically satisfies 2NF.

### Understanding Dependencies

A **dependency** means one column's value is determined by another. If you know the `order_id`, you can determine the `cust_name`. We say `cust_name` depends on `order_id`.

### Violation: Partial Dependency

Let us look at our bookstore table where the composite key is `(order_id, book_title)`:

```
Composite Key: (order_id, book_title)

+---------+-----------+----------+-----------+-------+-----+
|order_id | book_title|cust_name |cust_email |price  | qty |
+---------+-----------+----------+-----------+-------+-----+
|(PK)     | (PK)      |          |           |       |     |
+---------+-----------+----------+-----------+-------+-----+

Dependencies:
  order_id --> cust_name, cust_email   (depends on PART of key)
  book_title --> price                  (depends on PART of key)
  (order_id, book_title) --> qty        (depends on FULL key)
```

`cust_name` depends only on `order_id`, not on `book_title`. This is a **partial dependency**. Similarly, `price` depends only on `book_title`, not on `order_id`.

### Fixed: 2NF Version

Split the table so that each non-key column depends on the full key of its table.

```
Table: orders
+---------+----------+-----------+
|order_id | cust_name| cust_email|
|(PK)     |          |           |
+---------+----------+-----------+
| 1001    | Alice    | alice@    |
| 1002    | Dave     | dave@     |
+---------+----------+-----------+

Table: books
+-----------+-------+
|book_title | price |
|(PK)       |       |
+-----------+-------+
|SQL Made   | 29.99 |
|Data Design| 39.99 |
+-----------+-------+

Table: order_items
+---------+-----------+-----+
|order_id | book_title| qty |
|(PK)     | (PK)      |     |
+---------+-----------+-----+
| 1001    | SQL Made  |  2  |
| 1001    | Data Design|  1 |
| 1002    | SQL Made  |  1  |
+---------+-----------+-----+
```

Now:
- `cust_name` depends on `order_id` (the full key of the `orders` table).
- `price` depends on `book_title` (the full key of the `books` table).
- `qty` depends on `(order_id, book_title)` (the full key of the `order_items` table).

No partial dependencies remain.

---

## Third Normal Form (3NF): No Transitive Dependencies

A table is in **Third Normal Form** if:

1. It is already in 2NF.
2. No non-key column depends on another non-key column. Every non-key column must depend **directly** on the primary key, not through another non-key column.

### Understanding Transitive Dependencies

A **transitive dependency** is when column A determines column B, and column B determines column C. So A determines C, but indirectly, through B.

### Violation: Transitive Dependency

Look at our `orders` table from the 2NF step:

```
Table: orders
+---------+----------+-----------+-----------+
|order_id | cust_name| cust_email| cust_phone|
|(PK)     |          |           |           |
+---------+----------+-----------+-----------+

Dependencies:
  order_id --> cust_name      (direct, OK)
  order_id --> cust_email     (but wait...)
  cust_name --> cust_email    (cust_email depends on cust_name,
                               not directly on order_id!)

  order_id --> cust_name --> cust_email
  This is a TRANSITIVE dependency.
```

The problem: `cust_email` is really a fact about the **customer**, not about the **order**. If Alice's email changes, we must update every order she has made.

### Fixed: 3NF Version

Move customer information to its own table.

```
Table: customers
+-----------+----------+-----------+-----------+
|customer_id| cust_name| cust_email| cust_phone|
|(PK)       |          |           |           |
+-----------+----------+-----------+-----------+
| 1         | Alice    | alice@    | 555-0101  |
| 2         | Dave     | dave@     | 555-0202  |
+-----------+----------+-----------+-----------+

Table: orders
+---------+-----------+
|order_id | customer_id|
|(PK)     | (FK)       |
+---------+-----------+
| 1001    | 1          |
| 1002    | 2          |
| 1003    | 1          |
+---------+-----------+

Table: books
+---------+-----------+-------+-----------+-----------+
|book_id  | book_title| price | author    |author_email|
|(PK)     |           |       |           |            |
+---------+-----------+-------+-----------+-----------+
| 1       | SQL Made  | 29.99 | Bob Lee   | bob@pub   |
| 2       | Data Design| 39.99| Carol King| carol@pub |
| 3       | NoSQL     | 34.99 | Bob Lee   | bob@pub   |
+---------+-----------+-------+-----------+-----------+

Table: order_items
+---------+---------+-----+
|order_id | book_id | qty |
|(PK)     | (PK)    |     |
+---------+---------+-----+
| 1001    | 1       |  2  |
| 1001    | 2       |  1  |
| 1002    | 1       |  1  |
| 1003    | 3       |  3  |
+---------+---------+-----+
```

Wait, the `books` table still has a problem. `author_email` depends on `author`, not on `book_id`. Let us fix that too:

```
Table: authors
+-----------+-----------+-----------+
|author_id  | author_name| author_email|
|(PK)       |            |            |
+-----------+-----------+-----------+
| 1         | Bob Lee    | bob@pub    |
| 2         | Carol King | carol@pub  |
+-----------+-----------+-----------+

Table: books
+---------+-----------+-------+-----------+
|book_id  | book_title| price | author_id |
|(PK)     |           |       | (FK)      |
+---------+-----------+-------+-----------+
| 1       | SQL Made  | 29.99 | 1         |
| 2       | Data Design| 39.99| 2         |
| 3       | NoSQL     | 34.99 | 1         |
+---------+-----------+-------+-----------+
```

Now every non-key column depends directly on its table's primary key.

---

## The Full Normalization Journey

Let us visualize the entire transformation from messy spreadsheet to clean 3NF design:

```
ORIGINAL MESSY SPREADSHEET (Not normalized)
+----------------------------------------------------------+
| order_id, cust_name, cust_email, cust_phone,             |
| book_title, author, author_email, price, qty             |
+----------------------------------------------------------+
                    |
                    | Apply 1NF: Atomic values, no repeating groups
                    v
+----------------------------------------------------------+
| Each cell has one value, rows uniquely identifiable      |
| Still one big table                                      |
+----------------------------------------------------------+
                    |
                    | Apply 2NF: Remove partial dependencies
                    v
+------------------+  +------------------+  +--------------+
| orders           |  | books            |  | order_items  |
| order_id (PK)    |  | book_title (PK)  |  | order_id(PK) |
| cust_name        |  | price            |  | book_title(PK)|
| cust_email       |  | author           |  | qty          |
| cust_phone       |  | author_email     |  |              |
+------------------+  +------------------+  +--------------+
                    |
                    | Apply 3NF: Remove transitive dependencies
                    v
+-----------+  +----------+  +----------+  +--------+  +------------+
| customers |  | orders   |  | books    |  | authors|  | order_items|
| cust_id   |  | order_id |  | book_id  |  | auth_id|  | order_id   |
| name      |  | cust_id  |  | title    |  | name   |  | book_id    |
| email     |  | date     |  | price    |  | email  |  | qty        |
| phone     |  |          |  | auth_id  |  |        |  |            |
+-----------+  +----------+  +----------+  +--------+  +------------+
```

---

## BCNF (Boyce-Codd Normal Form)

BCNF is a stricter version of 3NF. A table is in BCNF if:

1. It is in 3NF.
2. For every dependency, the left side (determinant) is a **candidate key** (a column or set of columns that could serve as the primary key).

In practice, most tables that are in 3NF are also in BCNF. The difference only matters in rare cases involving overlapping composite candidate keys.

### Simple Example

Consider a table tracking which teachers teach which subjects in which rooms:

```
+---------+---------+------+
| teacher | subject | room |
+---------+---------+------+
| Smith   | Math    | 101  |
| Smith   | Science | 102  |
| Jones   | Math    | 101  |
+---------+---------+------+

Rules:
  - Each room is used for only one subject.
  - A teacher can teach multiple subjects.
  - Multiple teachers can teach in the same room.

Dependencies:
  (teacher, subject) --> room    (composite key determines room)
  room --> subject               (room determines subject)

Problem: room --> subject, but room is NOT a candidate key.
This violates BCNF.
```

The fix is to split into two tables:

```
Table: room_subjects          Table: teacher_rooms
+------+---------+            +---------+------+
| room | subject |            | teacher | room |
+------+---------+            +---------+------+
| 101  | Math    |            | Smith   | 101  |
| 102  | Science |            | Smith   | 102  |
+------+---------+            | Jones   | 101  |
                              +---------+------+
```

For most real-world databases, achieving 3NF is sufficient. BCNF matters mainly in academic study and edge cases.

---

## Denormalization: When to Break the Rules

Normalization is about correctness and data integrity. But sometimes, fully normalized databases can be slow for certain queries because they require many JOINs to reassemble the data.

**Denormalization** is the deliberate process of introducing some redundancy back into your database to improve read performance.

### When to Consider Denormalization

```
+-----------------------------------+-----------------------------------+
| Normalize When:                   | Denormalize When:                 |
+-----------------------------------+-----------------------------------+
| Data integrity is critical        | Read performance is critical      |
| Data changes frequently           | Data rarely changes               |
| Storage space is limited          | JOINs are too slow                |
| You need to avoid anomalies       | You need reporting/analytics speed|
| It is an OLTP system (many        | It is an OLAP system (few writes, |
|   writes, small reads)            |   large reads)                    |
+-----------------------------------+-----------------------------------+
```

### Example: Denormalization for Reporting

Suppose you have a fully normalized schema with customers, orders, order_items, products, and categories. A dashboard query joins all five tables to show sales by category.

```sql
-- Normalized: 5-table JOIN (slow for a dashboard)
SELECT
    c.category_name,
    SUM(oi.qty * p.price) AS revenue
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
JOIN customers cu ON o.customer_id = cu.customer_id
WHERE o.order_date >= '2024-01-01'
GROUP BY c.category_name;
```

A denormalized approach might add `category_name` directly to the `order_items` table:

```sql
-- Denormalized: simpler, faster query
SELECT
    category_name,
    SUM(line_total) AS revenue
FROM order_items_denormalized
WHERE order_date >= '2024-01-01'
GROUP BY category_name;
```

The tradeoff: if a category name changes, you must update it in the `order_items_denormalized` table too. But for a reporting database that rarely sees category changes, this is often acceptable.

### Common Denormalization Techniques

1. **Add redundant columns.** Store a frequently needed value from another table directly (e.g., store `customer_name` in the orders table).

2. **Use materialized views.** Create a pre-computed view of joined data (covered in Chapter 20).

3. **Create summary tables.** Maintain pre-aggregated data for dashboards:

```sql
CREATE TABLE daily_sales_summary (
    sale_date       DATE,
    category_name   VARCHAR(50),
    total_orders    INTEGER,
    total_revenue   NUMERIC(12,2)
);
```

4. **Store computed values.** Instead of calculating `total_amount` from line items every time, store it directly in the orders table.

---

## Step-by-Step: Normalizing an Order Spreadsheet

Let us do a complete normalization exercise from start to finish.

### Step 0: The Original Spreadsheet

A company tracks orders in a spreadsheet:

```
+--------+-------+--------+---------+--------+------+--------+-------+--------+
|OrderNo |ODate  |CustName|CustCity |Product |ProdCat|Supplier|SuppPh |Qty     |
+--------+-------+--------+---------+--------+------+--------+-------+--------+
|5001    |Jan 10 |Alice   |New York |Laptop  |Elec  |TechCo  |555-100|2       |
|5001    |Jan 10 |Alice   |New York |Mouse   |Elec  |TechCo  |555-100|5       |
|5001    |Jan 10 |Alice   |New York |Desk    |Furn  |OfficeCo|555-200|1       |
|5002    |Jan 12 |Bob     |Chicago  |Laptop  |Elec  |TechCo  |555-100|1       |
|5003    |Jan 15 |Alice   |New York |Chair   |Furn  |OfficeCo|555-200|4       |
+--------+-------+--------+---------+--------+------+--------+-------+--------+
```

### Step 1: Verify 1NF

Check: Are all values atomic? Yes, each cell has one value.
Check: Are there repeating groups? No repeating column patterns.
Check: Can we identify each row? The combination of (OrderNo, Product) is unique.

The table is in 1NF.

### Step 2: Achieve 2NF

Identify the composite key: `(OrderNo, Product)`

Find partial dependencies (columns that depend on only part of the key):
- `ODate, CustName, CustCity` depend only on `OrderNo`
- `ProdCat, Supplier, SuppPh` depend only on `Product`
- `Qty` depends on the full key `(OrderNo, Product)`

Split into tables:

```sql
-- Table: orders (depends on OrderNo)
CREATE TABLE orders (
    order_no    INTEGER PRIMARY KEY,
    order_date  DATE,
    cust_name   VARCHAR(50),
    cust_city   VARCHAR(50)
);

-- Table: products (depends on Product)
CREATE TABLE products (
    product_name VARCHAR(50) PRIMARY KEY,
    category     VARCHAR(50),
    supplier     VARCHAR(50),
    supplier_ph  VARCHAR(20)
);

-- Table: order_items (depends on full key)
CREATE TABLE order_items (
    order_no     INTEGER,
    product_name VARCHAR(50),
    qty          INTEGER,
    PRIMARY KEY (order_no, product_name)
);
```

### Step 3: Achieve 3NF

Check for transitive dependencies in each table.

In `orders`:
- `order_no --> cust_name --> cust_city` (city depends on customer, not order)
- This is a transitive dependency. Split customers out.

In `products`:
- `product_name --> supplier --> supplier_ph` (phone depends on supplier, not product)
- This is a transitive dependency. Split suppliers out.

Final 3NF schema:

```sql
CREATE TABLE customers (
    customer_id  SERIAL PRIMARY KEY,
    cust_name    VARCHAR(50),
    cust_city    VARCHAR(50)
);

CREATE TABLE suppliers (
    supplier_id  SERIAL PRIMARY KEY,
    supplier_name VARCHAR(50),
    supplier_ph   VARCHAR(20)
);

CREATE TABLE orders (
    order_no     INTEGER PRIMARY KEY,
    order_date   DATE,
    customer_id  INTEGER REFERENCES customers(customer_id)
);

CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    product_name VARCHAR(50),
    category     VARCHAR(50),
    supplier_id  INTEGER REFERENCES suppliers(supplier_id)
);

CREATE TABLE order_items (
    order_no     INTEGER REFERENCES orders(order_no),
    product_id   INTEGER REFERENCES products(product_id),
    qty          INTEGER,
    PRIMARY KEY (order_no, product_id)
);
```

### Final Schema Diagram

```
+------------+       +------------+       +------------+
| customers  |       | orders     |       | order_items|
+------------+       +------------+       +------------+
| customer_id|<------| order_no   |<------| order_no   |
| cust_name  |  (FK) | order_date |       | product_id |----+
| cust_city  |       | customer_id|       | qty        |    |
+------------+       +------------+       +------------+    |
                                                            |
+------------+       +------------+                         |
| suppliers  |       | products   |                         |
+------------+       +------------+                         |
| supplier_id|<------| product_id |<------------------------+
| supplier_name|  (FK)| product_name|
| supplier_ph|       | category   |
+------------+       | supplier_id|
                     +------------+
```

### Verify: Anomalies Are Gone

- **Update:** Change Alice's city? Update one row in `customers`. All her orders still link to the correct customer record.
- **Insert:** Add a new product? Insert into `products`. No order needed.
- **Delete:** Delete order 5002? Bob's customer record remains in `customers`.

---

## Normal Forms Summary

```
+------+-----------------------------+----------------------------------+
| Form | Rule                        | What It Prevents                 |
+------+-----------------------------+----------------------------------+
| 1NF  | Atomic values               | Comma-separated lists,           |
|      | No repeating groups         | repeating columns (book_1,       |
|      | Unique rows                 | book_2, book_3)                  |
+------+-----------------------------+----------------------------------+
| 2NF  | No partial dependencies     | Non-key column depending on      |
|      | (depends on full key)       | only part of a composite key     |
+------+-----------------------------+----------------------------------+
| 3NF  | No transitive dependencies  | Non-key column depending on      |
|      | (depends directly on key)   | another non-key column           |
+------+-----------------------------+----------------------------------+
| BCNF | Every determinant is a      | Rare edge cases with             |
|      | candidate key               | overlapping candidate keys       |
+------+-----------------------------+----------------------------------+
```

---

## Common Mistakes

### Mistake 1: Storing Comma-Separated Lists

```sql
-- WRONG: Violates 1NF
CREATE TABLE students (
    student_id   INTEGER PRIMARY KEY,
    student_name VARCHAR(50),
    courses      VARCHAR(200)  -- 'Math, Science, English'
);

-- CORRECT: Separate table for the many-to-many relationship
CREATE TABLE enrollments (
    student_id INTEGER REFERENCES students(student_id),
    course_id  INTEGER REFERENCES courses(course_id),
    PRIMARY KEY (student_id, course_id)
);
```

### Mistake 2: Over-Normalizing

Not everything needs to be in a separate table. A country code inside an address table is fine. You do not need a separate table for every small piece of data.

```sql
-- OVER-NORMALIZED: Separate table for city? Overkill for most apps.
CREATE TABLE cities (city_id SERIAL PRIMARY KEY, city_name VARCHAR(50));

-- REASONABLE: City as a column in the address table.
CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    street     VARCHAR(100),
    city       VARCHAR(50),
    state      VARCHAR(2)
);
```

### Mistake 3: Confusing Normalization with Optimization

Normalization is about **correctness**, not speed. Sometimes a normalized schema is slower for queries. That is okay -- you can add indexes, materialized views, or targeted denormalization to improve speed without abandoning correctness everywhere.

### Mistake 4: Skipping the Design Step

Do not jump straight into creating tables. Start with a list of all the data you need to store, identify the dependencies, and work through the normal forms systematically.

---

## Best Practices

1. **Aim for 3NF as your default.** Most applications benefit from 3NF. Only denormalize when you have measured evidence of a performance problem.

2. **Normalize first, denormalize later.** It is much easier to denormalize a normalized schema than to normalize a denormalized one.

3. **Identify entities clearly.** Each "thing" in your system (customer, order, product, supplier) should have its own table.

4. **Use surrogate keys.** Instead of using `cust_name` as a primary key, add an auto-generated `customer_id`. Names change; IDs do not.

5. **Document your design decisions.** If you denormalize, document why. Future developers (including your future self) will thank you.

6. **Think about how data will change.** Normalization prevents anomalies. Ask yourself: "If this data changes, will I need to update it in multiple places?"

7. **Use foreign keys.** Always define foreign key relationships. They enforce referential integrity and make the relationships between tables explicit.

---

## Quick Summary

```
+---------------------------+------------------------------------------+
| Concept                   | Description                              |
+---------------------------+------------------------------------------+
| Normalization             | Organizing tables to reduce redundancy   |
+---------------------------+------------------------------------------+
| Update Anomaly            | Same fact in multiple rows, risk of      |
|                           | inconsistency when updating              |
+---------------------------+------------------------------------------+
| Insert Anomaly            | Cannot add data without unrelated data   |
+---------------------------+------------------------------------------+
| Delete Anomaly            | Removing a row loses unrelated facts     |
+---------------------------+------------------------------------------+
| 1NF                       | Atomic values, no repeating groups       |
+---------------------------+------------------------------------------+
| 2NF                       | No partial dependencies on composite key |
+---------------------------+------------------------------------------+
| 3NF                       | No transitive dependencies               |
+---------------------------+------------------------------------------+
| BCNF                      | Every determinant is a candidate key     |
+---------------------------+------------------------------------------+
| Denormalization           | Adding controlled redundancy for speed   |
+---------------------------+------------------------------------------+
```

---

## Key Points

- **Normalization** is the process of organizing database tables to eliminate redundancy and prevent update, insert, and delete anomalies.
- **1NF** requires atomic values (no lists or repeating groups in a single column).
- **2NF** requires that all non-key columns depend on the **entire** primary key, not just part of it. Only relevant for composite keys.
- **3NF** requires that non-key columns depend **directly** on the primary key, not through other non-key columns (no transitive dependencies).
- **BCNF** is a stricter 3NF where every determinant must be a candidate key.
- **Denormalization** deliberately reintroduces redundancy for performance, typically in reporting or analytics systems.
- Always **normalize first**, then denormalize specific areas only when you have measured evidence of performance problems.
- Use **surrogate keys** (auto-generated IDs) instead of natural keys when possible.

---

## Practice Questions

1. Explain the three types of data anomalies (update, insert, delete) using a real-world example of your choosing.

2. A table has the columns `(student_id, course_id, student_name, course_name, grade)` with a composite primary key of `(student_id, course_id)`. Which normal form does this table violate? What are the partial dependencies? How would you fix it?

3. What is a transitive dependency? Give an example of a table that violates 3NF and show how to fix it.

4. When is denormalization appropriate? Give two specific scenarios where you might choose to denormalize.

5. Why is it recommended to "normalize first, denormalize later" rather than starting with a denormalized design?

---

## Exercises

### Exercise 1: Normalize a Library Spreadsheet

A library tracks loans in one spreadsheet:

```
| LoanID | MemberName | MemberPhone | BookTitle | Author | AuthorCountry | DueDate | Fine |
```

Identify all anomalies. Normalize this to 3NF. Show each step (1NF, 2NF, 3NF) and the final set of CREATE TABLE statements.

### Exercise 2: Normalize an Order Spreadsheet

You receive this spreadsheet from a client:

```
| InvoiceNo | InvoiceDate | CustomerName | CustomerAddress | ProductCode | ProductDesc | Category | UnitPrice | Qty | LineTotal |
```

The primary key is `(InvoiceNo, ProductCode)`. Normalize to 3NF. Write the final CREATE TABLE statements with appropriate primary keys and foreign keys.

### Exercise 3: Identify the Normal Form

For each of the following tables, identify the highest normal form it satisfies (1NF, 2NF, 3NF, or unnormalized). Explain your reasoning.

Table A: `employee_id, employee_name, department_id, department_name, department_location`

Table B: `order_id, product_id, quantity` (composite PK: order_id, product_id)

Table C: `student_id, courses_enrolled` (where courses_enrolled = "Math, Science, English")

---

## What Is Next?

Now that you understand how to organize your data through normalization, the next chapter will introduce **ER Diagrams** (Entity-Relationship Diagrams). ER diagrams are visual blueprints that help you plan and communicate your database design before writing a single line of SQL. They are the bridge between understanding your data (normalization) and building your schema (SQL).
