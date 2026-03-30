# Chapter 6: Databases -- SQL and NoSQL

## What You Will Learn

- A solid recap of SQL databases: tables, joins, ACID transactions, and indexes
- The four types of NoSQL databases: key-value, document, wide-column, and graph
- ACID vs BASE: two fundamentally different consistency models
- Schema vs schemaless: the trade-offs of rigid structure vs flexibility
- A decision flowchart for choosing SQL vs NoSQL
- Polyglot persistence: using multiple database types in one system
- When each database type shines and when it struggles

## Why This Chapter Matters

Every system you will ever design stores data. The database is the heart of your architecture. Choose the wrong one, and you will fight it at every turn -- poor performance, painful migrations, and limitations that force ugly workarounds.

For decades, SQL databases (PostgreSQL, MySQL, Oracle) were the only serious option. Then in the mid-2000s, companies like Google, Amazon, and Facebook hit scale problems that traditional SQL databases could not solve. They built new database systems that traded some of SQL's guarantees for massive scalability. These became known as NoSQL databases.

Today, the best architects understand both worlds and know when to use each -- or even when to use both together. This chapter gives you that understanding.

---

## 6.1 SQL Databases: A Recap

SQL (Structured Query Language) databases store data in tables with rows and columns. They enforce a strict schema, support complex queries, and guarantee data consistency through ACID transactions.

### The Spreadsheet Analogy

Think of a SQL database as a collection of interconnected spreadsheets. Each spreadsheet (table) has defined columns (schema), and you can look up data across spreadsheets using common values (joins).

```
USERS TABLE:
+----+----------+-------------------+
| id | name     | email             |
+----+----------+-------------------+
| 1  | Alice    | alice@example.com |
| 2  | Bob      | bob@example.com   |
| 3  | Charlie  | charlie@ex.com    |
+----+----------+-------------------+

ORDERS TABLE:
+----+---------+------------+--------+
| id | user_id | product    | amount |
+----+---------+------------+--------+
| 1  | 1       | Laptop     | 999.99 |
| 2  | 1       | Mouse      | 29.99  |
| 3  | 2       | Keyboard   | 79.99  |
+----+---------+------------+--------+

JOIN: "Show me all orders with user names"

SELECT users.name, orders.product, orders.amount
FROM orders
JOIN users ON orders.user_id = users.id;

+----------+----------+--------+
| name     | product  | amount |
+----------+----------+--------+
| Alice    | Laptop   | 999.99 |
| Alice    | Mouse    | 29.99  |
| Bob      | Keyboard | 79.99  |
+----------+----------+--------+
```

### ACID Properties

ACID is the set of guarantees that SQL databases provide for transactions:

```
A - Atomicity
    All operations in a transaction succeed, or none do.
    "Transfer $100 from Account A to Account B"
    --> Debit A AND credit B, or neither happens.

C - Consistency
    Every transaction moves the database from one valid
    state to another. Constraints are never violated.
    --> Balance cannot go below zero (if that is a rule).

I - Isolation
    Concurrent transactions do not interfere with each other.
    Each transaction sees a consistent snapshot of the data.
    --> Two people buying the last item: only one succeeds.

D - Durability
    Once a transaction is committed, it survives crashes,
    power failures, and restarts. Data is written to disk.
    --> Your bank transfer does not vanish if the server reboots.
```

### Why ACID Matters

ACID is critical for systems where correctness cannot be compromised:

- **Banking:** A transfer must debit one account AND credit another. Never just one.
- **Inventory:** If two users buy the last item simultaneously, only one should succeed.
- **Bookings:** A hotel room should not be double-booked.

### SQL Strengths

- **Complex queries:** JOINs, aggregations, subqueries, window functions
- **Data integrity:** Foreign keys, constraints, triggers ensure valid data
- **ACID transactions:** Strong consistency guarantees
- **Mature tooling:** Decades of optimization, monitoring, and backup tools
- **Standardized language:** SQL is universal across vendors

### SQL Weaknesses

- **Vertical scaling:** Traditional SQL databases scale by adding more power to a single server (bigger CPU, more RAM). There is a ceiling.
- **Rigid schema:** Changing the schema (adding/removing columns) on a large table can be slow and disruptive.
- **Impedance mismatch:** Object-oriented code does not map naturally to flat tables. ORMs help but add complexity.
- **Horizontal scaling is hard:** Distributing a SQL database across multiple machines (sharding) is complex and breaks some guarantees (see Chapter 8).

### Popular SQL Databases

```
+---------------+-------------------------------------------+
| Database      | Notable Features                          |
+---------------+-------------------------------------------+
| PostgreSQL    | Most feature-rich open-source SQL DB.     |
|               | JSON support, extensions, very reliable.  |
+---------------+-------------------------------------------+
| MySQL         | Most popular open-source SQL DB. Fast     |
|               | reads, widely deployed. Used by Facebook. |
+---------------+-------------------------------------------+
| SQLite        | Embedded database (no server). Perfect    |
|               | for mobile apps and small tools.          |
+---------------+-------------------------------------------+
| SQL Server    | Microsoft's enterprise DB. Deep Windows   |
|               | integration, strong BI tools.             |
+---------------+-------------------------------------------+
| Oracle        | Enterprise heavyweight. Expensive but     |
|               | extremely capable for large organizations.|
+---------------+-------------------------------------------+
```

---

## 6.2 NoSQL Databases

NoSQL ("Not Only SQL") databases sacrifice some of SQL's guarantees to gain flexibility, scalability, or performance. There are four main types, each designed for different data access patterns.

### Type 1: Key-Value Stores

The simplest NoSQL database. Data is stored as key-value pairs, like a giant hash map.

```
KEY-VALUE STORE:

  +------------------+----------------------------------+
  | Key              | Value                            |
  +------------------+----------------------------------+
  | user:1           | {"name":"Alice","email":"a@b.c"} |
  | session:abc123   | {"logged_in":true,"cart":[1,2]}  |
  | config:timeout   | "30"                             |
  +------------------+----------------------------------+

  Operations:
    GET user:1          --> Returns Alice's data
    SET user:1 {...}    --> Stores/updates Alice's data
    DELETE user:1       --> Removes Alice's data

  That is it. No queries by value, no joins, no indexes.
  You look up by key or not at all.
```

**Examples:** Redis, Amazon DynamoDB (also document), Memcached, Riak

**Best for:** Caching, session storage, user preferences, shopping carts, leaderboards

**Not for:** Complex queries, relationships between data, reporting

### Type 2: Document Stores

Store data as documents (usually JSON or BSON). Each document can have a different structure. You can query by any field, not just the key.

```
DOCUMENT STORE:

  Collection: "users"

  Document 1:
  {
    "_id": "user_1",
    "name": "Alice",
    "email": "alice@example.com",
    "addresses": [
      {"type": "home", "city": "New York"},
      {"type": "work", "city": "Boston"}
    ]
  }

  Document 2:
  {
    "_id": "user_2",
    "name": "Bob",
    "email": "bob@example.com",
    "phone": "+1-555-0100"       <-- Different fields! OK!
  }

  Queries:
    Find where name = "Alice"           --> Document 1
    Find where addresses.city = "Boston" --> Document 1
    Find where phone exists             --> Document 2
```

**Examples:** MongoDB, Amazon DynamoDB, Couchbase, CouchDB

**Best for:** Content management, catalogs, user profiles, event logging, any data that is naturally hierarchical

**Not for:** Highly relational data with many cross-references, complex transactions across multiple documents

### Type 3: Wide-Column Stores

Store data in tables with rows and columns, but unlike SQL, each row can have a different set of columns. Designed for massive-scale, write-heavy workloads.

```
WIDE-COLUMN STORE:

  Row Key: "user_1"
  +------------------+---------------------+------------------+
  | Column Family: personal                | Column Family:   |
  |                                        | activity         |
  +----------+---------+------------------++---------+--------+
  | name     | email   | phone            | last_login| posts |
  | "Alice"  | "a@b.c" | "+1-555-0100"    | "2024-01" | "42"  |
  +----------+---------+------------------+-----------+--------+

  Row Key: "user_2"
  +------------------+---------------------+------------------+
  | Column Family: personal                | Column Family:   |
  |                                        | activity         |
  +----------+---------+------------------++-----------+------+
  | name     | email   |                  | last_login |      |
  | "Bob"    | "b@c.d" |  (no phone!)     | "2024-02"  |      |
  +----------+---------+------------------+------------+------+

  Each row can have different columns.
  Columns are grouped into "column families."
  Optimized for reads/writes by row key.
```

**Examples:** Apache Cassandra, HBase, Google Bigtable

**Best for:** Time-series data, IoT sensor data, event logging, recommendation engines, any workload with massive write volume

**Not for:** Small datasets, ad-hoc queries, systems needing strong consistency

### Type 4: Graph Databases

Store data as nodes (entities) and edges (relationships). Optimized for traversing relationships.

```
GRAPH DATABASE:

  Nodes and Edges:

    (Alice)---[FRIENDS_WITH]--->(Bob)
       |                         |
  [WORKS_AT]               [WORKS_AT]
       |                         |
       v                         v
    (Google)                  (Meta)
       |
  [LOCATED_IN]
       |
       v
  (Mountain View)

  Queries:
  "Find all of Alice's friends" --> Traverse FRIENDS_WITH edges
  "Find friends of friends"     --> Two-hop traversal
  "Shortest path Alice to Meta" --> Graph traversal algorithm

  These queries are FAST in a graph DB (follow pointers)
  but SLOW in SQL (multiple JOINs on large tables).
```

**Examples:** Neo4j, Amazon Neptune, JanusGraph, ArangoDB

**Best for:** Social networks, recommendation engines, fraud detection, knowledge graphs, network topology, dependency analysis

**Not for:** Simple CRUD operations, tabular data, high-volume writes

### NoSQL Type Comparison

```
+----------------+------------+----------+----------+----------+
| Feature        | Key-Value  | Document | Wide-    | Graph    |
|                |            |          | Column   |          |
+----------------+------------+----------+----------+----------+
| Data model     | Key:Value  | JSON/BSON| Row +    | Nodes +  |
|                | pairs      | documents| columns  | edges    |
+----------------+------------+----------+----------+----------+
| Query by       | Key only   | Any field| Row key  | Traversal|
|                |            |          | + column |          |
+----------------+------------+----------+----------+----------+
| Schema         | None       | Flexible | Flexible | Flexible |
+----------------+------------+----------+----------+----------+
| Joins          | No         | Limited  | No       | Native   |
|                |            |          |          |(traversal|
|                |            |          |          | = join)  |
+----------------+------------+----------+----------+----------+
| Best for       | Cache,     | CMS,     | Time     | Social,  |
|                | sessions   | catalogs | series,  | fraud,   |
|                |            |          | IoT      | recs     |
+----------------+------------+----------+----------+----------+
| Scale          | Excellent  | Very good| Excellent| Good     |
+----------------+------------+----------+----------+----------+
| Complexity     | Lowest     | Low      | Medium   | Higher   |
+----------------+------------+----------+----------+----------+
```

---

## 6.3 ACID vs BASE

SQL databases follow ACID. Many NoSQL databases follow a different model called BASE.

### BASE Properties

```
BA - Basically Available
     The system guarantees availability: it will respond
     to every request, even if the data is not the
     latest version.

S  - Soft state
     The state of the system may change over time, even
     without new input, as data propagates between nodes.

E  - Eventually consistent
     If you stop writing, all replicas will eventually
     converge to the same value. But at any given moment,
     different replicas might return different values.
```

### ACID vs BASE Comparison

```
+------------------+-------------------------+-------------------------+
| Property         | ACID                    | BASE                    |
+------------------+-------------------------+-------------------------+
| Consistency      | Strong: every read      | Eventual: reads may     |
|                  | returns the latest      | return stale data       |
|                  | committed write         | temporarily             |
+------------------+-------------------------+-------------------------+
| Availability     | May sacrifice           | Prioritizes             |
|                  | availability for        | availability over       |
|                  | consistency             | consistency             |
+------------------+-------------------------+-------------------------+
| Transactions     | Full multi-operation    | Usually single-item     |
|                  | transactions            | operations              |
+------------------+-------------------------+-------------------------+
| Scaling          | Harder to scale         | Designed to scale       |
|                  | horizontally            | horizontally            |
+------------------+-------------------------+-------------------------+
| Use cases        | Banking, inventory,     | Social feeds, analytics,|
|                  | booking systems         | shopping carts, logs    |
+------------------+-------------------------+-------------------------+
```

### The Real-World Trade-off

```
ACID (Bank Transfer):

  Account A: $500     Account B: $300
  Transfer $100 from A to B:

  BEGIN TRANSACTION
    UPDATE accounts SET balance = 400 WHERE id = A;
    UPDATE accounts SET balance = 400 WHERE id = B;
  COMMIT

  Result: A=$400, B=$400  (ALWAYS correct, never A=$400 B=$300)


BASE (Social Media Like Count):

  Post has 1000 likes. User clicks "Like."

  Server 1 records: 1001 likes
  Server 2 still shows: 1000 likes  (stale for a few seconds)
  Server 3 still shows: 1000 likes  (stale for a few seconds)

  After a few seconds, all servers show: 1001 likes

  Is this OK? Yes! Nobody notices if a like count is
  off by 1 for a few seconds.
```

---

## 6.4 Schema vs Schemaless

### Schema (SQL)

The database enforces the structure of your data. Every row in a table has the same columns. You must define the schema before inserting data. Changing the schema requires a migration.

```
SCHEMA-BASED (SQL):

  CREATE TABLE users (
    id    INT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age   INT
  );

  INSERT INTO users (id, name, email, age)
  VALUES (1, 'Alice', 'alice@ex.com', 30);

  -- This FAILS:
  INSERT INTO users (id, name, email, age, phone)
  VALUES (2, 'Bob', 'bob@ex.com', 25, '555-0100');
  -- Error: column "phone" does not exist!

  -- Must ALTER table first:
  ALTER TABLE users ADD COLUMN phone VARCHAR(20);
  -- On a table with 100M rows, this can take minutes to hours!
```

### Schemaless (NoSQL)

Each document/record can have a different structure. No upfront schema definition needed. Great flexibility, but the application must handle inconsistent data.

```
SCHEMALESS (MongoDB):

  // Document 1
  {
    "_id": 1,
    "name": "Alice",
    "email": "alice@ex.com",
    "age": 30
  }

  // Document 2 -- different fields, no problem!
  {
    "_id": 2,
    "name": "Bob",
    "email": "bob@ex.com",
    "phone": "555-0100",
    "preferences": {"theme": "dark", "lang": "en"}
  }

  // No ALTER TABLE needed. Just store what you want.
```

### The Trade-off

```
+------------------+---------------------------+---------------------------+
| Aspect           | Schema (SQL)              | Schemaless (NoSQL)        |
+------------------+---------------------------+---------------------------+
| Data quality     | High (DB enforces rules)  | Depends on app code       |
+------------------+---------------------------+---------------------------+
| Flexibility      | Low (must migrate schema) | High (store anything)     |
+------------------+---------------------------+---------------------------+
| Schema changes   | ALTER TABLE (can be slow) | Just write new structure  |
+------------------+---------------------------+---------------------------+
| Documentation    | Schema IS documentation   | Must document separately  |
+------------------+---------------------------+---------------------------+
| Debugging        | Predictable data shape    | "What fields does this    |
|                  |                           |  document have?"          |
+------------------+---------------------------+---------------------------+
| Best for         | Stable, well-understood   | Evolving, varied, or      |
|                  | data models               | semi-structured data      |
+------------------+---------------------------+---------------------------+
```

**Important note:** "Schemaless" is somewhat misleading. In practice, your application code always expects some structure. The question is whether the database or your application enforces it. Many teams use schema validation libraries even with NoSQL databases.

---

## 6.5 SQL vs NoSQL: Decision Flowchart

Use this flowchart when choosing a database for a new project:

```
START
  |
  v
Do you need ACID transactions across
multiple records/tables?
  |
  +-- YES --> Do you need complex JOINs
  |           and aggregations?
  |             |
  |             +-- YES --> SQL DATABASE
  |             |           (PostgreSQL, MySQL)
  |             |
  |             +-- NO --> SQL DATABASE
  |                        (but consider NewSQL like
  |                         CockroachDB, TiDB for scale)
  |
  +-- NO --> What is your primary access pattern?
              |
              +-- Simple key lookups
              |   (get by ID, session store)
              |   --> KEY-VALUE STORE
              |       (Redis, DynamoDB)
              |
              +-- Flexible documents with
              |   varying structure
              |   --> DOCUMENT STORE
              |       (MongoDB, DynamoDB)
              |
              +-- Massive write volume,
              |   time-series data
              |   --> WIDE-COLUMN STORE
              |       (Cassandra, HBase)
              |
              +-- Complex relationships,
                  graph traversal
                  --> GRAPH DATABASE
                      (Neo4j, Neptune)
```

### Quick Decision Table

```
+------------------------------+-------------------+
| If your data looks like...   | Consider...       |
+------------------------------+-------------------+
| Tables with relationships    | PostgreSQL, MySQL |
| JSON documents               | MongoDB, DynamoDB |
| Key-value pairs              | Redis, DynamoDB   |
| Time-series / IoT logs       | Cassandra, HBase  |
| Social graph / network       | Neo4j, Neptune    |
| Full-text search             | Elasticsearch     |
| Everything (you are unsure)  | PostgreSQL        |
+------------------------------+-------------------+

When in doubt, start with PostgreSQL. It handles JSON,
full-text search, and relational data well. Specialize later.
```

---

## 6.6 SQL vs NoSQL: Detailed Comparison

```
+--------------------+------------------------+------------------------+
| Dimension          | SQL                    | NoSQL                  |
+--------------------+------------------------+------------------------+
| Data model         | Tables (rows/columns)  | Varies (documents,     |
|                    |                        | key-value, graph, etc.)|
+--------------------+------------------------+------------------------+
| Schema             | Fixed, enforced by DB  | Flexible or none       |
+--------------------+------------------------+------------------------+
| Query language     | SQL (standardized)     | Varies by database     |
+--------------------+------------------------+------------------------+
| Transactions       | Multi-row ACID         | Usually single-item    |
|                    |                        | (some support multi)   |
+--------------------+------------------------+------------------------+
| Joins              | Native, optimized      | Usually not supported  |
|                    |                        | (denormalize instead)  |
+--------------------+------------------------+------------------------+
| Scaling            | Vertical (scale up)    | Horizontal (scale out) |
|                    | Horizontal is hard     | Built-in sharding      |
+--------------------+------------------------+------------------------+
| Consistency        | Strong (ACID)          | Eventual (BASE)        |
|                    |                        | or tunable             |
+--------------------+------------------------+------------------------+
| Normalization      | Normalized (reduce     | Denormalized (embed    |
|                    | redundancy)            | related data)          |
+--------------------+------------------------+------------------------+
| Maturity           | 40+ years              | ~15-20 years           |
+--------------------+------------------------+------------------------+
| Tooling/ecosystem  | Very mature            | Growing rapidly        |
+--------------------+------------------------+------------------------+
```

### Normalization vs Denormalization

This is one of the most important differences in practice:

```
NORMALIZED (SQL):
  Users Table:        Orders Table:          Products Table:
  +----+-------+      +----+--------+----+   +----+--------+-------+
  | id | name  |      | id | user_id|prod|   | id | name   | price |
  +----+-------+      +----+--------+----+   +----+--------+-------+
  | 1  | Alice |      | 1  | 1      | 10 |   | 10 | Laptop | 999   |
  +----+-------+      +----+--------+----+   +----+--------+-------+

  To get "Alice's order": JOIN three tables
  Pro: No duplicate data. Update product name in ONE place.
  Con: Requires JOINs (slower at scale).


DENORMALIZED (NoSQL):
  Orders Collection:
  {
    "order_id": 1,
    "user_name": "Alice",           <-- Embedded, not referenced
    "user_email": "alice@ex.com",   <-- Duplicated
    "product_name": "Laptop",       <-- Duplicated
    "product_price": 999            <-- Duplicated
  }

  To get "Alice's order": Read ONE document
  Pro: Single read, very fast. No JOINs needed.
  Con: If product name changes, must update ALL orders.
```

---

## 6.7 Polyglot Persistence

Modern systems rarely use just one database. Different parts of the system have different data needs, and different databases excel at different things. Using multiple database types in one system is called **polyglot persistence**.

### Example: E-Commerce System

```
POLYGLOT PERSISTENCE IN E-COMMERCE:

  +-------------------+     +-------------------+
  |   Product Catalog |     |   User Accounts   |
  |   (MongoDB)       |     |   (PostgreSQL)    |
  |   - Flexible      |     |   - ACID for      |
  |     product attrs |     |     payments       |
  |   - Varies by     |     |   - Strong        |
  |     category      |     |     consistency    |
  +-------------------+     +-------------------+

  +-------------------+     +-------------------+
  |   Shopping Cart   |     |   Product Search  |
  |   (Redis)         |     |   (Elasticsearch) |
  |   - Fast R/W      |     |   - Full-text     |
  |   - Expirable     |     |     search        |
  |   - Key-value     |     |   - Faceted       |
  |     perfect fit   |     |     filtering     |
  +-------------------+     +-------------------+

  +-------------------+     +-------------------+
  |   Recommendations |     |   Analytics/Logs  |
  |   (Neo4j)         |     |   (Cassandra)     |
  |   - "Users who    |     |   - High write    |
  |     bought X also |     |     throughput     |
  |     bought Y"     |     |   - Time-series   |
  |   - Graph         |     |     data          |
  |     traversal     |     |                   |
  +-------------------+     +-------------------+
```

### Benefits of Polyglot Persistence

- Each database is optimized for its use case
- Better performance for specialized access patterns
- Independent scaling of each data store

### Costs of Polyglot Persistence

- **Operational complexity:** More databases to deploy, monitor, backup, and upgrade
- **Data consistency:** Keeping data in sync across databases is hard
- **Team knowledge:** Developers must understand multiple database technologies
- **Increased infrastructure cost:** Each database system requires its own resources

### When to Use Polyglot Persistence

- **Do** use it when different parts of your system have fundamentally different data access patterns
- **Do not** use it just because it sounds modern. Start with one database (usually PostgreSQL) and add specialized databases only when you hit clear limitations

---

## 6.8 NewSQL: The Best of Both Worlds?

A newer category of databases attempts to combine SQL's ACID guarantees with NoSQL's horizontal scalability.

```
+-------------------+-------------------------------------------+
| NewSQL Database   | Key Feature                               |
+-------------------+-------------------------------------------+
| CockroachDB       | Distributed SQL, survives datacenter      |
|                   | failures, PostgreSQL-compatible            |
+-------------------+-------------------------------------------+
| TiDB              | MySQL-compatible distributed SQL,          |
|                   | scales horizontally                        |
+-------------------+-------------------------------------------+
| Google Spanner    | Globally distributed, strongly consistent,|
|                   | Google-scale (managed service)             |
+-------------------+-------------------------------------------+
| YugabyteDB        | PostgreSQL-compatible, distributed,        |
|                   | cloud-native                               |
+-------------------+-------------------------------------------+
```

NewSQL databases are a good option when you need both ACID compliance and horizontal scaling, but they come with their own trade-offs: higher operational complexity, potential latency from distributed consensus, and relative immaturity compared to traditional SQL databases.

---

## Common Mistakes

1. **Choosing NoSQL because it is trendy.** Most applications work perfectly well with PostgreSQL. Choose NoSQL for specific technical reasons, not hype.

2. **Using MongoDB as a relational database.** If you find yourself doing many cross-collection lookups (JOINs), you probably need a SQL database.

3. **Ignoring data modeling.** NoSQL does not mean "no thinking about data." You must model your data around your access patterns, which requires even more upfront design than SQL.

4. **Assuming NoSQL is always faster.** SQL databases with proper indexes are very fast. NoSQL is faster for specific access patterns, not universally.

5. **Not considering operational cost.** Running Cassandra, MongoDB, Elasticsearch, AND PostgreSQL means your team must be expert in all of them. That is expensive.

6. **Over-normalizing in SQL.** If every query requires five JOINs, your schema might be too normalized. Some denormalization is OK for read-heavy workloads.

7. **Forgetting about backups and recovery.** NoSQL databases have different backup and recovery characteristics. Understand them before going to production.

---

## Best Practices

1. **Start with PostgreSQL when unsure.** It handles relational data, JSON documents, full-text search, and more. It is the safest default choice.

2. **Model data around access patterns, not just entities.** In NoSQL, design your data model based on the queries you need to run, not the shape of your domain objects.

3. **Use the right database for the right job.** Do not force a key-value store to do complex queries, and do not force a SQL database to do high-throughput time-series writes.

4. **Evaluate operational complexity.** A simpler database that your team knows well may be better than a theoretically superior one nobody understands.

5. **Plan for schema evolution.** In SQL, use migration tools (Flyway, Alembic). In NoSQL, version your documents and handle old formats gracefully.

6. **Benchmark with realistic data.** Toy benchmarks are misleading. Test with production-like data volumes and access patterns.

7. **Consider managed services.** Running databases yourself is complex. AWS RDS, DynamoDB, Atlas (MongoDB), and Aiven reduce operational burden significantly.

---

## Quick Summary

SQL databases store data in structured tables with strong ACID guarantees, enforced schemas, and powerful query capabilities through JOINs and aggregations. They are the right default for most applications. NoSQL databases come in four flavors: key-value (simplest, for lookups), document (flexible JSON storage), wide-column (massive write throughput), and graph (relationship traversal). NoSQL trades consistency (BASE model) for horizontal scalability. Schema enforcement in SQL catches data errors early but makes changes harder; schemaless NoSQL is flexible but shifts validation to application code. Polyglot persistence uses multiple database types in one system, matching each data need to the best tool. When in doubt, start with PostgreSQL and add specialized databases only when specific limitations emerge.

---

## Key Points

- SQL databases provide ACID transactions, enforced schemas, and powerful JOINs -- ideal for data integrity
- NoSQL databases come in four types: key-value, document, wide-column, and graph
- ACID guarantees strong consistency; BASE provides eventual consistency with better availability
- Schema enforcement catches errors early but makes changes harder; schemaless is flexible but riskier
- Choose SQL when you need transactions, complex queries, and data integrity
- Choose NoSQL when you need horizontal scaling, flexible schemas, or specific access patterns
- Polyglot persistence uses multiple databases, each optimized for its use case
- When in doubt, start with PostgreSQL -- it is the safest default

---

## Practice Questions

1. You are designing a social media platform. User profiles are well-structured (name, email, bio), but posts can include text, images, polls, links, or any combination. Would you use SQL, NoSQL, or both? Explain your reasoning.

2. An online game needs to store player scores and display real-time leaderboards. Players can also form guilds, and you need to query "friends of friends." Which database type(s) would you use and why?

3. Explain why a banking system should use ACID transactions rather than BASE. Give a specific example of what could go wrong with eventual consistency in a banking context.

4. Your company currently uses PostgreSQL for everything. The analytics team complains that their queries on 500 million event records are too slow and blocking production traffic. What would you recommend?

5. A startup is building a product catalog where each product category has completely different attributes (electronics have specs like RAM and screen size; clothing has size, color, material). Compare how you would model this in SQL vs a document database.

---

## Exercises

**Exercise 1: Database Selection**
For each scenario, choose the most appropriate database type and justify your choice: (a) storing user sessions that expire after 30 minutes, (b) a content management system where articles have different structures (blog posts, news, tutorials), (c) a fraud detection system that needs to find connections between accounts, (d) a ride-sharing app that logs every GPS coordinate from every ride.

**Exercise 2: Data Modeling**
Take a simple e-commerce domain (users, products, orders, reviews). Model it in two ways: (a) a normalized SQL schema with at least 4 tables and foreign keys, (b) a denormalized MongoDB document schema. For each, write pseudo-queries for: "Get all orders for user Alice" and "Get the average review score for product X." Compare the complexity.

**Exercise 3: Migration Planning**
Your startup has been running on MongoDB for 2 years. You now realize that most of your data is highly relational (users, organizations, permissions, projects, tasks). You want to migrate to PostgreSQL. Outline a step-by-step migration plan that minimizes downtime and risk. Consider: data transformation, dual-write period, testing, and rollback strategy.

---

## What Is Next?

Now that you understand the fundamentals of SQL and NoSQL databases, the next chapters will dive deeper into how databases handle scale. Chapter 7 covers database replication (keeping copies of your data for availability and read performance), and Chapter 8 covers database sharding (splitting your data across multiple machines for write performance). Together with this chapter, they complete your understanding of how databases work in large-scale systems.
