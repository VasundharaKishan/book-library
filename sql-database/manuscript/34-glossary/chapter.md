# Chapter 34: Glossary — Every Term You Need to Know

## What You Will Learn

In this chapter, you will find:

- Definitions for 80+ SQL and database terms
- All terms organized alphabetically for quick reference
- Plain-English explanations with brief examples where helpful
- Cross-references to related terms

## Why This Chapter Matters

Every field has its own vocabulary, and databases are no exception. When you read documentation, attend a job interview, or join a team discussion, you will hear terms like "cardinality," "referential integrity," and "materialized view." If these terms are unfamiliar, the conversation becomes confusing fast.

This glossary gives you a single place to look up any term you encounter. Bookmark this chapter. Come back to it whenever you need a quick refresher. Over time, these terms will become second nature.

---

## The Glossary

### ACID

A set of four properties that guarantee database transactions are reliable. ACID stands for **Atomicity** (all or nothing), **Consistency** (data stays valid), **Isolation** (transactions do not interfere with each other), and **Durability** (committed changes survive crashes). Every modern relational database, including PostgreSQL, follows ACID rules. See Chapter 25.

### Aggregate Function

A function that takes multiple rows as input and returns a single value. Common aggregate functions include `COUNT()`, `SUM()`, `AVG()`, `MIN()`, and `MAX()`. For example, `SELECT AVG(price) FROM products` returns the average price across all products. Aggregate functions are often used with GROUP BY. See Chapter 10.

### Alias

A temporary name you give to a table or column in a query. Aliases make queries easier to read. You create them with the `AS` keyword (or just a space). For example, `SELECT first_name AS name FROM customers` renames the output column to "name." Table aliases like `FROM orders AS o` let you write shorter JOIN conditions. See Chapter 7.

### ALTER

A DDL command used to modify an existing database object. `ALTER TABLE` can add or drop columns, add or remove constraints, rename columns, and change data types. For example, `ALTER TABLE customers ADD COLUMN phone VARCHAR(20)`. See Chapters 4 and 24.

### B-tree

The default index type in PostgreSQL. B-tree stands for "balanced tree." It organizes data in a sorted tree structure that allows fast lookups, range scans, and ordering. B-tree indexes work well with equality (`=`) and range (`<`, `>`, `BETWEEN`) comparisons. Think of it like a phone book — you can quickly jump to the right section without reading every page. See Chapter 21.

### BEGIN

A command that starts a new transaction. Everything between `BEGIN` and `COMMIT` (or `ROLLBACK`) is treated as a single unit of work. If anything fails, you can roll back all changes. For example: `BEGIN; UPDATE accounts SET balance = 0; COMMIT;`. See Chapter 25.

### Candidate Key

A column or set of columns that could serve as the primary key because it uniquely identifies every row. A table might have several candidate keys, but only one is chosen as the primary key. The others can be enforced with UNIQUE constraints. For example, both `email` and `social_security_number` might uniquely identify a person — both are candidate keys.

### Cardinality

In database design, cardinality describes the numerical relationship between two tables. The three types are: **one-to-one** (one person has one passport), **one-to-many** (one customer has many orders), and **many-to-many** (many students enroll in many courses). In performance context, cardinality refers to the number of distinct values in a column — high cardinality means many unique values. See Chapter 23.

### CASCADE

An action that automatically propagates changes from a parent table to child tables. `ON DELETE CASCADE` deletes child rows when the parent is deleted. `ON UPDATE CASCADE` updates child foreign keys when the parent's primary key changes. Use CASCADE carefully — it can delete more data than you expect. See Chapter 24.

### CHECK

A constraint that validates data against a custom condition before allowing it into the table. For example, `CHECK (price > 0)` ensures prices are always positive. `CHECK (status IN ('active', 'inactive'))` limits status to specific values. The condition must evaluate to TRUE or NULL for the row to be accepted. See Chapter 24.

### COALESCE

A function that returns the first non-NULL value from a list of arguments. `COALESCE(phone, email, 'No contact')` returns the phone number if it exists, otherwise the email, otherwise the text "No contact." It is commonly used to provide fallback values when dealing with NULL data. See Chapter 18.

### Composite Key

A primary key made up of two or more columns. The combination of values must be unique, but individual columns can have duplicates. For example, an order_items table might use `(order_id, product_id)` as its composite key — the same product can appear in different orders, but not twice in the same order. See Chapter 24.

### Constraint

A rule attached to a table or column that restricts what data can be stored. Constraints include PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK, and DEFAULT. Constraints enforce data integrity at the database level so bad data is rejected before it is stored. See Chapter 24.

### Correlated Subquery

A subquery that references a column from the outer query. Unlike a regular subquery that runs once, a correlated subquery runs once for each row in the outer query. For example: `SELECT * FROM employees e WHERE salary > (SELECT AVG(salary) FROM employees WHERE dept_id = e.dept_id)`. This finds employees who earn more than their department's average. See Chapter 16.

### CTE (Common Table Expression)

A named temporary result set defined within a query using the `WITH` keyword. CTEs make complex queries easier to read by breaking them into logical steps. For example: `WITH top_customers AS (SELECT ... FROM ...) SELECT * FROM top_customers`. CTEs exist only for the duration of the query. See Chapter 27.

### DDL (Data Definition Language)

The subset of SQL commands that define and modify database structure. DDL commands include `CREATE`, `ALTER`, `DROP`, and `TRUNCATE`. These commands change the schema (tables, indexes, views) rather than the data inside the tables. DDL commands are auto-committed in many databases, but PostgreSQL supports transactional DDL.

### Deadlock

A situation where two or more transactions are waiting for each other to release locks, creating a circular dependency. Neither transaction can proceed. PostgreSQL automatically detects deadlocks and kills one of the transactions so the other can continue. Prevent deadlocks by always locking rows in a consistent order. See Chapter 25.

### DEFAULT

A constraint that provides an automatic value for a column when no value is specified during INSERT. For example, `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` automatically records the current time. `status VARCHAR(20) DEFAULT 'active'` sets new rows to "active" unless you specify otherwise. See Chapter 24.

### DELETE

A DML command that removes rows from a table. `DELETE FROM customers WHERE customer_id = 5` removes one specific customer. `DELETE FROM logs WHERE created_at < '2024-01-01'` removes old log entries. DELETE without a WHERE clause removes all rows but keeps the table structure. Always use a WHERE clause unless you intend to delete everything. See Chapter 6.

### Denormalization

The deliberate process of adding redundant data to a normalized database to improve read performance. For example, storing a customer's name directly in the orders table (instead of joining to the customers table every time) is denormalization. It speeds up reads but makes updates harder because you must keep the redundant copies in sync. See Chapter 22.

### DML (Data Manipulation Language)

The subset of SQL commands that work with the data inside tables. DML commands include `SELECT`, `INSERT`, `UPDATE`, and `DELETE`. Unlike DDL (which changes structure), DML changes the actual data stored in tables.

### Entity

A real-world object or concept that is represented as a table in a database. A customer, a product, an order, and an employee are all entities. Each entity has attributes (columns) that describe it and instances (rows) that represent individual records. See Chapter 23.

### ER Diagram (Entity-Relationship Diagram)

A visual representation of the tables in a database and the relationships between them. Tables are shown as boxes, columns as lists within the boxes, and relationships as lines connecting the boxes. ER diagrams help you design and communicate database structure. See Chapter 23.

### EXCEPT

A set operation that returns rows from the first query that do not appear in the second query. `SELECT city FROM customers EXCEPT SELECT city FROM suppliers` returns cities where you have customers but no suppliers. EXCEPT removes duplicates from the result. Use EXCEPT ALL to keep duplicates. See Chapter 17.

### EXPLAIN

A command that shows the query plan — how PostgreSQL intends to execute a query. `EXPLAIN SELECT * FROM orders WHERE total > 100` shows whether the database will use an index or a sequential scan. `EXPLAIN ANALYZE` actually runs the query and shows real execution times. Essential for performance tuning. See Chapter 30.

### FETCH

A command used with cursors to retrieve a specific number of rows from a result set. In standard SQL, `FETCH FIRST 10 ROWS ONLY` limits results (similar to LIMIT). In PL/pgSQL, `FETCH` retrieves rows from an open cursor one at a time. See Chapter 28.

### FOREIGN KEY

A constraint that creates a link between two tables by requiring that a column's value must match an existing value in another table's primary key (or unique column). Foreign keys enforce referential integrity — they prevent orphan records. For example, an order's customer_id must reference a real customer. See Chapter 24.

### FROM

The clause in a SELECT statement that specifies which table or tables to read data from. `SELECT * FROM customers` reads from the customers table. FROM can include multiple tables (for joins), subqueries, CTEs, or functions. See Chapter 7.

### FULL JOIN (FULL OUTER JOIN)

A join that returns all rows from both tables. Rows that have a match are combined. Rows from either table that have no match are included with NULL values for the missing side. FULL JOIN is useful when you want to see all data from both tables, whether or not there is a match. See Chapter 15.

### Function

A reusable piece of code that accepts input parameters, performs a computation, and returns a result. PostgreSQL has built-in functions (like `NOW()`, `LENGTH()`, `UPPER()`) and lets you create custom functions using PL/pgSQL or other languages. Functions can return a single value, a row, or a table. See Chapters 18 and 28.

### GIN (Generalized Inverted Index)

An index type in PostgreSQL designed for values that contain multiple elements, such as arrays, JSONB documents, and full-text search vectors. GIN indexes store a mapping from each element to the rows that contain it. Think of it like a book index — you look up a word and find all the pages that mention it. See Chapter 21.

### GiST (Generalized Search Tree)

An index type in PostgreSQL that supports complex data types like geometric shapes, ranges, and full-text search. GiST is more flexible than B-tree and can handle operations like "find all points within this circle" or "find all ranges that overlap." See Chapter 21.

### GRANT

A command that gives a user or role specific permissions on a database object. `GRANT SELECT ON customers TO analyst_role` allows the analyst to read the customers table. `GRANT ALL ON products TO admin_role` gives full access. See Chapter 31.

### GROUP BY

A clause that groups rows with the same values into summary rows. Used with aggregate functions to compute per-group results. `SELECT department, COUNT(*) FROM employees GROUP BY department` counts employees in each department. Every column in SELECT must be in GROUP BY or inside an aggregate function. See Chapter 11.

### HAVING

A clause that filters groups after GROUP BY has been applied. HAVING is like WHERE, but for groups instead of individual rows. `SELECT department, AVG(salary) FROM employees GROUP BY department HAVING AVG(salary) > 50000` shows only departments with an average salary above 50,000. See Chapter 11.

### Index

A data structure that speeds up data retrieval at the cost of extra storage and slower writes. Think of an index like a book's index — instead of reading every page to find a topic, you look it up in the index and jump directly to the right page. PostgreSQL supports several index types: B-tree, Hash, GIN, GiST, and others. See Chapter 21.

### INNER JOIN

A join that returns only rows where there is a match in both tables. If a customer has no orders, that customer does not appear in the result. If an order references a non-existent customer, that order does not appear either. INNER JOIN is the most common join type. See Chapter 13.

### INSERT

A DML command that adds new rows to a table. `INSERT INTO customers (name, email) VALUES ('Alice', 'alice@example.com')` adds one row. You can insert multiple rows at once and use RETURNING to see the inserted data. See Chapter 6.

### INTERSECT

A set operation that returns only rows that appear in both the first and second query results. `SELECT city FROM customers INTERSECT SELECT city FROM suppliers` returns cities where you have both customers and suppliers. INTERSECT removes duplicates. See Chapter 17.

### Isolation Level

A setting that controls how much one transaction can see of another transaction's uncommitted changes. PostgreSQL supports three levels: **READ COMMITTED** (default — sees only committed data), **REPEATABLE READ** (consistent snapshot throughout the transaction), and **SERIALIZABLE** (strictest — transactions behave as if they run one at a time). See Chapter 25.

### JOIN

An operation that combines rows from two or more tables based on a related column. The main types are INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, and CROSS JOIN. JOINs are fundamental to relational databases because data is split across multiple tables by design. See Chapters 12 through 15.

### JSON / JSONB

Data types for storing JSON (JavaScript Object Notation) data. `JSON` stores an exact copy of the input text. `JSONB` stores a parsed binary representation that is faster to query and supports indexing. Use JSONB in most cases. PostgreSQL provides operators like `->`, `->>`, and `@>` for querying JSON data.

### Key

A column or set of columns used to identify rows or establish relationships. Types of keys include: primary key (unique identifier), foreign key (references another table), candidate key (could be a primary key), composite key (multiple columns), and surrogate key (artificial identifier like SERIAL).

### LAG

A window function that accesses a value from a previous row without using a self-join. `LAG(sales, 1) OVER (ORDER BY month)` returns the sales value from the previous month. Useful for calculating differences between consecutive rows, like month-over-month growth. See Chapter 26.

### LEAD

A window function that accesses a value from a subsequent row. `LEAD(sales, 1) OVER (ORDER BY month)` returns the sales value from the next month. LEAD is the opposite of LAG. See Chapter 26.

### LEFT JOIN (LEFT OUTER JOIN)

A join that returns all rows from the left table and matching rows from the right table. If a left table row has no match in the right table, the right table's columns are filled with NULL. `SELECT * FROM customers LEFT JOIN orders ON customers.id = orders.customer_id` includes customers even if they have no orders. See Chapter 14.

### LIKE

A pattern-matching operator used in WHERE clauses. `%` matches any sequence of characters, `_` matches any single character. `WHERE name LIKE 'A%'` finds names starting with "A." `WHERE code LIKE '__-___'` finds codes in the format "XX-XXX." ILIKE is the case-insensitive version in PostgreSQL. See Chapter 8.

### LIMIT

A clause that restricts the number of rows returned by a query. `SELECT * FROM products LIMIT 10` returns only the first 10 rows. Often used with ORDER BY and OFFSET for pagination. See Chapter 9.

### Lock

A mechanism that prevents multiple transactions from modifying the same data simultaneously. When a transaction updates a row, it places a lock on that row so other transactions must wait. Locks prevent data corruption but can cause blocking and deadlocks if not managed carefully. See Chapter 25.

### Materialized View

A view that stores its query results physically on disk, like a cached snapshot. Unlike a regular view (which re-executes the query each time), a materialized view returns pre-computed results instantly. You refresh it manually with `REFRESH MATERIALIZED VIEW`. Useful for expensive queries that do not need real-time data. See Chapter 20.

### Normalization

The process of organizing a database to reduce redundancy and improve data integrity. Normalization splits data into multiple related tables. The main normal forms are 1NF (no repeating groups), 2NF (no partial dependencies), and 3NF (no transitive dependencies). Normalization trades some read performance for better data consistency. See Chapter 22.

### NOT NULL

A constraint that prevents a column from containing NULL values. Every INSERT and UPDATE must provide a value for a NOT NULL column. `CREATE TABLE users (name VARCHAR(100) NOT NULL)` ensures every user has a name. Most columns in a well-designed database should be NOT NULL. See Chapter 24.

### NULL

A special marker that represents a missing or unknown value. NULL is not the same as zero, an empty string, or false. Comparisons with NULL use `IS NULL` or `IS NOT NULL` instead of `=` or `!=`. NULL has special behavior in aggregates, sorting, and boolean logic. See Chapter 8.

### OFFSET

A clause that skips a specified number of rows before returning results. `SELECT * FROM products ORDER BY name LIMIT 10 OFFSET 20` skips the first 20 rows and returns rows 21 through 30. Used with LIMIT for pagination. Large OFFSET values can be slow because the database must still process the skipped rows. See Chapter 9.

### ON DELETE CASCADE

A foreign key option that automatically deletes child rows when the parent row is deleted. For example, if an order is deleted and its order_items have ON DELETE CASCADE, all items for that order are automatically removed. See Chapter 24.

### ORDER BY

A clause that sorts query results by one or more columns. `ORDER BY price ASC` sorts cheapest first. `ORDER BY created_at DESC` sorts newest first. You can sort by multiple columns: `ORDER BY department ASC, salary DESC`. Without ORDER BY, row order is unpredictable. See Chapter 9.

### OUTER JOIN

A general term for joins that include rows even when there is no match in the other table. LEFT OUTER JOIN, RIGHT OUTER JOIN, and FULL OUTER JOIN are all outer joins. The "OUTER" keyword is optional — `LEFT JOIN` and `LEFT OUTER JOIN` are identical. See Chapters 14 and 15.

### Partition

A method of dividing a large table into smaller, more manageable pieces called partitions. Each partition holds a subset of the data based on a partition key (like date ranges or regions). Queries that filter by the partition key only scan the relevant partition, improving performance on very large tables. See Chapter 30.

### PL/pgSQL

PostgreSQL's built-in procedural language for writing functions, procedures, and triggers. PL/pgSQL extends SQL with variables, loops, conditionals, and exception handling. It runs inside the database server, avoiding the overhead of sending queries back and forth from an application. See Chapter 28.

### PRIMARY KEY

A constraint that uniquely identifies each row in a table. A primary key column (or combination of columns) must be unique and cannot contain NULL. Each table can have only one primary key. PostgreSQL automatically creates a B-tree index on the primary key. See Chapter 24.

### Privilege

A permission granted to a user or role that controls what actions they can perform. Common privileges include SELECT (read), INSERT (add), UPDATE (modify), DELETE (remove), and ALL (everything). Privileges are granted with GRANT and removed with REVOKE. See Chapter 31.

### Query Plan

The step-by-step strategy PostgreSQL uses to execute a query. The query planner considers available indexes, table sizes, and statistics to choose the most efficient approach. Use `EXPLAIN` or `EXPLAIN ANALYZE` to view the query plan. Understanding query plans is essential for performance tuning. See Chapter 30.

### RANK

A window function that assigns a rank to each row within a partition based on the ORDER BY values. Rows with equal values receive the same rank, and the next rank is skipped. `RANK() OVER (ORDER BY score DESC)` might produce ranks 1, 2, 2, 4 (rank 3 is skipped because two rows tied for rank 2). See Chapter 26.

### Recursive CTE

A Common Table Expression that references itself, allowing you to traverse hierarchical or graph-like data. For example, you can find all employees in a management chain by starting with the CEO and recursively following the manager_id relationship. Recursive CTEs use `WITH RECURSIVE`. See Chapter 27.

### Referential Integrity

The guarantee that every foreign key value in a child table corresponds to an existing primary key value in the parent table. Referential integrity prevents orphan records — rows that reference data that does not exist. Foreign key constraints enforce referential integrity automatically. See Chapter 24.

### Relation

In relational database theory, a relation is a table. It consists of a set of tuples (rows) with the same attributes (columns). The term comes from the mathematical concept of a relation, not from "relationships between tables." The relational model was proposed by Edgar F. Codd in 1970. See Chapter 2.

### RETURNING

A PostgreSQL clause that returns data from rows affected by INSERT, UPDATE, or DELETE. `INSERT INTO customers (name) VALUES ('Alice') RETURNING customer_id` returns the newly generated ID. `DELETE FROM logs WHERE age > 30 RETURNING *` shows which rows were deleted. RETURNING saves you from needing a separate SELECT query. See Chapter 6.

### REVOKE

A command that removes previously granted permissions from a user or role. `REVOKE INSERT ON customers FROM intern_role` takes away the ability to add data. REVOKE is the opposite of GRANT. See Chapter 31.

### Role

A named collection of database permissions in PostgreSQL. Roles can represent individual users or groups. A role can own database objects, have specific privileges, and inherit permissions from other roles. PostgreSQL uses roles instead of separate "user" and "group" concepts. See Chapter 31.

### ROLLBACK

A command that undoes all changes made during the current transaction. After ROLLBACK, the database returns to the state it was in before BEGIN. Use ROLLBACK when an error occurs or when you decide not to proceed with the changes. See Chapter 25.

### ROW_NUMBER

A window function that assigns a unique sequential number to each row within a partition. Unlike RANK, ROW_NUMBER never produces duplicates — even rows with identical values get different numbers. `ROW_NUMBER() OVER (ORDER BY created_at)` numbers rows 1, 2, 3, 4 regardless of ties. See Chapter 26.

### Schema

A named container within a database that organizes tables, views, functions, and other objects. Think of a schema like a folder. The default schema in PostgreSQL is `public`. You can create additional schemas to organize objects by purpose: `CREATE SCHEMA sales`. Refer to objects as `schema_name.table_name`. See Chapter 4.

### SELECT

The most used SQL command. SELECT retrieves data from one or more tables. A basic SELECT includes columns to return and a FROM clause specifying the table. Additional clauses like WHERE, JOIN, GROUP BY, ORDER BY, and LIMIT refine the results. See Chapter 7.

### Self Join

A join where a table is joined to itself. Useful for comparing rows within the same table or traversing hierarchical data. For example, finding employees and their managers from the same employees table: `SELECT e.name, m.name AS manager FROM employees e JOIN employees m ON e.manager_id = m.employee_id`. See Chapter 15.

### Sequence

A database object that generates a series of unique numbers. Sequences are the engine behind SERIAL and BIGSERIAL columns. You can create custom sequences with `CREATE SEQUENCE`, get the next value with `nextval('sequence_name')`, and see the current value with `currval('sequence_name')`. Sequences are guaranteed to be unique even with concurrent access.

### SERIAL

A pseudo data type in PostgreSQL that creates an auto-incrementing integer column. `SERIAL` is shorthand for creating a sequence and setting the column's default to `nextval()`. SERIAL produces integers from 1 to about 2.1 billion. Use BIGSERIAL for larger ranges. In newer PostgreSQL versions, `GENERATED ALWAYS AS IDENTITY` is the preferred alternative. See Chapter 5.

### Subquery

A query nested inside another query. Subqueries can appear in SELECT, FROM, WHERE, and HAVING clauses. A subquery in WHERE acts as a filter: `SELECT * FROM products WHERE price > (SELECT AVG(price) FROM products)`. A subquery in FROM acts as a temporary table. See Chapter 16.

### TABLE

A database object that stores data in rows and columns. Tables are the fundamental building blocks of a relational database. Each table represents an entity (like customers, orders, or products). Tables are created with `CREATE TABLE` and removed with `DROP TABLE`. See Chapter 4.

### Transaction

A sequence of SQL statements that are executed as a single unit of work. Either all statements succeed (COMMIT) or all fail (ROLLBACK). Transactions follow ACID properties to ensure data integrity. In PostgreSQL, every single statement runs inside an implicit transaction even if you do not use BEGIN. See Chapter 25.

### Trigger

A function that automatically runs in response to a specific event on a table (INSERT, UPDATE, DELETE, or TRUNCATE). Triggers can fire BEFORE or AFTER the event. For example, a trigger can automatically update an `updated_at` timestamp whenever a row is modified. See Chapter 29.

### TRUNCATE

A DDL command that removes all rows from a table quickly. `TRUNCATE TABLE logs` is faster than `DELETE FROM logs` because it does not scan individual rows. TRUNCATE resets auto-increment sequences and cannot be used with a WHERE clause. In PostgreSQL, TRUNCATE is transactional. See Chapter 4.

### UNION

A set operation that combines the results of two or more SELECT queries into one result set. `UNION` removes duplicates. `UNION ALL` keeps duplicates and is faster. Both queries must have the same number of columns with compatible data types. See Chapter 17.

### UNIQUE

A constraint that ensures no two rows have the same value in a column (or combination of columns). Unlike PRIMARY KEY, a table can have multiple UNIQUE constraints, and UNIQUE columns can contain NULL values. PostgreSQL automatically creates an index on UNIQUE columns. See Chapter 24.

### UPDATE

A DML command that modifies existing rows in a table. `UPDATE products SET price = 49.99 WHERE product_id = 5` changes one row. Always use a WHERE clause unless you intend to update every row. UPDATE can use JOINs, subqueries, and RETURNING. See Chapter 6.

### Upsert

An operation that inserts a row if it does not exist or updates it if it does. PostgreSQL implements upsert with `INSERT ... ON CONFLICT DO UPDATE`. For example: `INSERT INTO products (id, name, price) VALUES (1, 'Laptop', 999) ON CONFLICT (id) DO UPDATE SET price = EXCLUDED.price`. This avoids separate "check then insert or update" logic.

### UUID (Universally Unique Identifier)

A 128-bit value used as a unique identifier. UUIDs look like `550e8400-e29b-41d4-a716-446655440000`. Unlike SERIAL (which depends on a sequence), UUIDs can be generated independently by any system without risk of collision. PostgreSQL provides the `gen_random_uuid()` function. UUIDs are useful for distributed systems where multiple servers create records.

### VACUUM

A PostgreSQL maintenance command that reclaims storage occupied by dead tuples (rows that have been deleted or updated). PostgreSQL uses MVCC, which means old row versions are not immediately removed. VACUUM cleans them up. `VACUUM ANALYZE` also updates statistics used by the query planner. PostgreSQL runs autovacuum automatically, but heavily updated tables may need manual vacuuming. See Chapter 30.

### View

A virtual table defined by a stored SELECT query. A view does not store data — it runs the query every time you select from it. Views simplify complex queries, provide a layer of abstraction, and can restrict which columns or rows a user can see. Create with `CREATE VIEW view_name AS SELECT ...`. See Chapter 20.

### WHERE

A clause that filters rows based on a condition. `SELECT * FROM orders WHERE total > 100` returns only orders with a total above 100. WHERE supports comparison operators (`=`, `>`, `<`, `!=`), logical operators (`AND`, `OR`, `NOT`), pattern matching (`LIKE`), and more. WHERE filters individual rows before grouping — use HAVING to filter groups. See Chapter 8.

### Window Function

A function that performs a calculation across a set of rows related to the current row, without collapsing them into a single output row. Unlike aggregate functions with GROUP BY, window functions keep all rows in the result. They use the `OVER()` clause to define the window. Common window functions include `ROW_NUMBER()`, `RANK()`, `LAG()`, `LEAD()`, `SUM() OVER()`, and `AVG() OVER()`. See Chapter 26.

### WITH

The keyword that introduces a Common Table Expression (CTE). `WITH monthly_sales AS (SELECT ...) SELECT * FROM monthly_sales` defines a temporary named result set. `WITH RECURSIVE` creates a recursive CTE for hierarchical queries. The WITH clause appears at the beginning of a query, before the main SELECT. See Chapter 27.

---

## Quick Reference: Constraint Types

```
+-------------------+--------------------------------------------------+
| Constraint        | Purpose                                          |
+-------------------+--------------------------------------------------+
| PRIMARY KEY       | Unique row identifier, no NULLs                  |
| FOREIGN KEY       | References another table, enforces relationships |
| UNIQUE            | No duplicate values (NULLs allowed)              |
| NOT NULL          | Value required, no NULLs                         |
| CHECK             | Custom validation rule                           |
| DEFAULT           | Auto-fill value when none given                  |
+-------------------+--------------------------------------------------+
```

## Quick Reference: JOIN Types

```
+-------------------+--------------------------------------------------+
| JOIN Type         | Returns                                          |
+-------------------+--------------------------------------------------+
| INNER JOIN        | Only matching rows from both tables              |
| LEFT JOIN         | All left rows + matching right rows              |
| RIGHT JOIN        | All right rows + matching left rows              |
| FULL JOIN         | All rows from both tables                        |
| CROSS JOIN        | Every combination of rows (Cartesian product)    |
| SELF JOIN         | Table joined to itself                           |
+-------------------+--------------------------------------------------+
```

## Quick Reference: Common Commands

```
+-------------------+--------------------------------------------------+
| Command           | Category  | Purpose                             |
+-------------------+-----------+--------------------------------------+
| SELECT            | DML       | Read data                            |
| INSERT            | DML       | Add rows                             |
| UPDATE            | DML       | Modify rows                          |
| DELETE            | DML       | Remove rows                          |
| CREATE TABLE      | DDL       | Create a table                       |
| ALTER TABLE       | DDL       | Modify table structure               |
| DROP TABLE        | DDL       | Remove a table                       |
| TRUNCATE          | DDL       | Remove all rows quickly              |
| BEGIN             | TCL       | Start a transaction                  |
| COMMIT            | TCL       | Save transaction changes             |
| ROLLBACK          | TCL       | Undo transaction changes             |
| GRANT             | DCL       | Give permissions                     |
| REVOKE            | DCL       | Remove permissions                   |
+-------------------+-----------+--------------------------------------+
```

---

## Congratulations

You have reached the end of this book. Take a moment to appreciate how far you have come.

When you started, a database was a mysterious black box. Now you can:

- Design tables with proper data types and constraints
- Write queries that filter, sort, group, and join data across multiple tables
- Use subqueries, CTEs, and window functions for advanced analysis
- Create views and indexes to simplify and speed up your queries
- Normalize your data to eliminate redundancy
- Draw ER diagrams to plan and communicate your designs
- Write transactions that keep your data safe and consistent
- Build stored procedures and triggers for automation
- Tune queries for performance using EXPLAIN
- Manage security with roles and privileges
- Build complete database-backed applications from scratch

That is a substantial skill set. Many working professionals do not know half of what you have learned.

### What to Learn Next

Your SQL and database journey does not end here. Here are paths you can explore:

**Deepen your PostgreSQL knowledge.** Explore advanced features like table inheritance, custom data types, extensions (PostGIS for geographic data, pg_trgm for fuzzy text search), and logical replication.

**Learn database administration.** Understand backup and restore strategies, monitoring tools, connection pooling, high availability with streaming replication, and disaster recovery planning.

**Explore other databases.** Try MySQL, SQLite, or SQL Server to see how they differ from PostgreSQL. Learn a NoSQL database like MongoDB or Redis to understand when relational databases are not the best fit.

**Build real applications.** Connect PostgreSQL to a programming language you know — Python with psycopg2 or SQLAlchemy, JavaScript with node-postgres or Prisma, Java with JDBC or Hibernate. Build a project that solves a real problem for you.

**Study data engineering.** Learn about ETL pipelines, data warehousing, columnar databases, and tools like dbt for data transformation.

**Practice with real data.** Download public datasets (government data, Kaggle datasets, public APIs) and load them into PostgreSQL. Ask questions of the data. Build dashboards. The best way to solidify your skills is to use them on problems you care about.

The most important thing is to keep writing SQL. Like any skill, database work gets better with practice. Every query you write, every schema you design, and every bug you debug makes you stronger.

Good luck, and happy querying.
