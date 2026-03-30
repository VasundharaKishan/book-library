# Chapter 14: Spring Data JPA and H2

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand what JPA is and why it exists
- Add Spring Data JPA and H2 dependencies to your project
- Create entity classes that map to database tables
- Use annotations like `@Entity`, `@Id`, `@GeneratedValue`, and `@Column`
- Configure H2 as an in-memory database for development
- Access the H2 console to inspect your database
- Pre-load data using `data.sql`
- Configure `show-sql` and `ddl-auto` properties

## Why This Chapter Matters

So far, your Spring Boot applications have been stateless. Every time you restart the server, all data disappears. That is like a restaurant where the waiters have amnesia -- they forget every order the moment they turn around.

Real applications need to store data. Customer information, product catalogs, order histories -- all of this needs to persist somewhere. That somewhere is a database.

But here is the problem: Java speaks objects (classes, fields, methods), and databases speak tables (rows, columns, SQL). These are two very different languages. **JPA** (Java Persistence API) acts as a translator between them. It lets you work with Java objects while JPA handles all the SQL behind the scenes.

And **H2** is a lightweight database that runs inside your application's memory. It is perfect for learning and development because you do not need to install anything. No MySQL server, no PostgreSQL setup -- just add a dependency and you have a database.

---

## What Is JPA?

JPA stands for **Java Persistence API**. It is a specification (a set of rules) that defines how Java objects should be mapped to database tables. Think of JPA as a contract that says "if you follow these rules, I will handle your database operations."

```
+------------------------------------------+
|          YOUR JAVA APPLICATION           |
|                                          |
|   Product product = new Product();       |
|   product.setName("Laptop");             |
|   product.setPrice(999.99);              |
|   repository.save(product);              |
|                                          |
+------------------+-----------------------+
                   |
                   |  JPA translates your Java
                   |  objects into SQL statements
                   v
+------------------------------------------+
|               JPA LAYER                  |
|   (Hibernate is the implementation)      |
|                                          |
|   INSERT INTO products (name, price)     |
|   VALUES ('Laptop', 999.99);             |
|                                          |
+------------------+-----------------------+
                   |
                   v
+------------------------------------------+
|              DATABASE                    |
|   +----+--------+--------+              |
|   | id | name   | price  |              |
|   +----+--------+--------+              |
|   | 1  | Laptop | 999.99 |              |
|   +----+--------+--------+              |
+------------------------------------------+
```

**Hibernate** is the most popular implementation of JPA. When you use Spring Data JPA, Hibernate is included automatically. You write Java annotations, and Hibernate generates the SQL for you.

### Real-Life Analogy

Imagine you are staying at a hotel in a foreign country. You do not speak the local language, but the hotel has a concierge who speaks both your language and the local language.

- **You** = Your Java application
- **Concierge** = JPA (Hibernate)
- **Local people** = The database
- **Your language** = Java objects
- **Local language** = SQL

You tell the concierge "I need a taxi to the airport." The concierge translates that into the local language and communicates with the taxi driver. You never need to learn the local language.

---

## Setting Up the Project

### Step 1: Add Dependencies

If you are using **Spring Initializr** (start.spring.io), select these dependencies:
- Spring Web
- Spring Data JPA
- H2 Database

If you already have a project, add these to your `pom.xml`:

```xml
<dependencies>
    <!-- Spring Web for REST APIs -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Spring Data JPA for database operations -->
    <dependency>                                              <!-- Line 1 -->
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId> <!-- Line 2 -->
    </dependency>

    <!-- H2 in-memory database -->
    <dependency>                                              <!-- Line 3 -->
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>                           <!-- Line 4 -->
        <scope>runtime</scope>                                <!-- Line 5 -->
    </dependency>

    <!-- Spring Boot Test -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1-2 | `spring-boot-starter-data-jpa` | Pulls in Spring Data JPA, Hibernate, and all related libraries. This is the "concierge" that translates between Java and SQL |
| 3-4 | `h2` | The H2 database engine. It is a lightweight, fast, in-memory database written in Java |
| 5 | `<scope>runtime</scope>` | Tells Maven that H2 is only needed when the application runs, not when compiling your code. Your Java code never directly references H2 classes |

### What Gets Pulled In

When you add `spring-boot-starter-data-jpa`, Maven downloads these key libraries:

```
spring-boot-starter-data-jpa
├── spring-data-jpa          (Repository abstractions)
├── hibernate-core           (JPA implementation)
├── jakarta.persistence-api  (JPA annotations like @Entity, @Id)
├── spring-jdbc              (Low-level database access)
├── HikariCP                 (Connection pool - manages DB connections)
└── spring-tx                (Transaction management)
```

---

## Configuring the Application

### Step 2: Configure application.properties

```properties
# ===== Application =====
spring.application.name=jpa-demo

# ===== H2 Database Configuration =====
# Use in-memory database named "testdb"
spring.datasource.url=jdbc:h2:mem:testdb                     # Line 1
spring.datasource.driver-class-name=org.h2.Driver            # Line 2
spring.datasource.username=sa                                 # Line 3
spring.datasource.password=                                   # Line 4

# ===== H2 Console =====
# Enable the web-based H2 console
spring.h2.console.enabled=true                                # Line 5
spring.h2.console.path=/h2-console                            # Line 6

# ===== JPA / Hibernate Configuration =====
# Automatically create/update tables based on entity classes
spring.jpa.hibernate.ddl-auto=create-drop                     # Line 7
# Show SQL statements in the console
spring.jpa.show-sql=true                                      # Line 8
# Format the SQL for readability
spring.jpa.properties.hibernate.format_sql=true               # Line 9
# Use H2 dialect for SQL generation
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect  # Line 10

# ===== Data Initialization =====
# Run data.sql after tables are created
spring.jpa.defer-datasource-initialization=true               # Line 11
```

**Line-by-line explanation:**

| Line | Property | What It Does |
|------|----------|-------------|
| 1 | `spring.datasource.url` | The JDBC URL for the database. `jdbc:h2:mem:testdb` means "use H2, store in memory, name it testdb." Data is lost when the app stops |
| 2 | `spring.datasource.driver-class-name` | The JDBC driver class for H2. Spring Boot can auto-detect this, but being explicit is clearer |
| 3 | `spring.datasource.username` | Database username. H2 defaults to `sa` (system administrator) |
| 4 | `spring.datasource.password` | Database password. Empty by default for H2 |
| 5 | `spring.h2.console.enabled` | Enables the H2 web console, a browser-based database viewer |
| 6 | `spring.h2.console.path` | The URL path for the H2 console. Access it at `http://localhost:8080/h2-console` |
| 7 | `spring.jpa.hibernate.ddl-auto` | Controls how Hibernate manages the database schema. `create-drop` creates tables on startup and drops them on shutdown |
| 8 | `spring.jpa.show-sql` | Prints every SQL statement Hibernate executes to the console. Very useful for learning |
| 9 | `spring.jpa.properties.hibernate.format_sql` | Formats the SQL output with indentation instead of a single long line |
| 10 | `spring.jpa.database-platform` | Tells Hibernate which SQL dialect to use. H2Dialect generates H2-compatible SQL |
| 11 | `spring.jpa.defer-datasource-initialization` | Ensures `data.sql` runs after Hibernate creates the tables, not before |

### Understanding ddl-auto Options

The `spring.jpa.hibernate.ddl-auto` property is one of the most important settings. Here is what each option does:

```
+---------------+--------------------------------------------------+
| Option        | What It Does                                     |
+---------------+--------------------------------------------------+
| none          | Do nothing. You manage the schema yourself       |
+---------------+--------------------------------------------------+
| validate      | Check that entities match existing tables.        |
|               | Throw error if they don't match. No changes made |
+---------------+--------------------------------------------------+
| update        | Add new columns/tables but never remove existing |
|               | ones. Safe for development, risky for production |
+---------------+--------------------------------------------------+
| create        | Drop all tables and recreate them on startup.    |
|               | All data is lost every restart                   |
+---------------+--------------------------------------------------+
| create-drop   | Same as create, but also drops tables when the   |
|               | application shuts down. Best for testing         |
+---------------+--------------------------------------------------+
```

**For development with H2:** Use `create-drop` or `create`. Since H2 is in-memory, data is lost anyway when the app stops.

**For production with a real database:** Use `validate` or `none`. Never use `create` or `create-drop` in production -- you would lose all your data!

---

## Creating Entity Classes

### Step 3: Create a Product Entity

An entity class is a Java class that maps to a database table. Each instance of the class represents a row in the table.

```java
package com.example.demo.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity                                                       // Line 1
@Table(name = "products")                                     // Line 2
public class Product {

    @Id                                                       // Line 3
    @GeneratedValue(strategy = GenerationType.IDENTITY)       // Line 4
    private Long id;                                          // Line 5

    @Column(name = "product_name", nullable = false,
            length = 100)                                     // Line 6
    private String name;

    @Column(nullable = false)                                 // Line 7
    private Double price;

    @Column(length = 500)                                     // Line 8
    private String description;

    @Column(name = "in_stock")                                // Line 9
    private Boolean inStock = true;                           // Line 10

    // Default constructor (REQUIRED by JPA)
    public Product() {                                        // Line 11
    }

    // Parameterized constructor (for convenience)
    public Product(String name, Double price,
                   String description) {                      // Line 12
        this.name = name;
        this.price = price;
        this.description = description;
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Double getPrice() {
        return price;
    }

    public void setPrice(Double price) {
        this.price = price;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Boolean getInStock() {
        return inStock;
    }

    public void setInStock(Boolean inStock) {
        this.inStock = inStock;
    }

    @Override
    public String toString() {
        return "Product{id=" + id + ", name='" + name + "'"
            + ", price=" + price + ", inStock=" + inStock + "}";
    }
}
```

**Line-by-line explanation:**

| Line | Annotation/Code | What It Does |
|------|----------------|-------------|
| 1 | `@Entity` | Marks this class as a JPA entity. Hibernate will create a database table for it |
| 2 | `@Table(name = "products")` | Specifies the table name. Without this, the table would be named `product` (the class name in lowercase) |
| 3 | `@Id` | Marks this field as the primary key of the table |
| 4 | `@GeneratedValue(strategy = GenerationType.IDENTITY)` | The database auto-generates the ID value. `IDENTITY` uses auto-increment (1, 2, 3, ...) |
| 5 | `private Long id` | Use `Long` (not `long`) for IDs because it can be `null` for new entities that have not been saved yet |
| 6 | `@Column(name = "product_name", nullable = false, length = 100)` | Maps to column `product_name`, cannot be NULL, max 100 characters |
| 7 | `@Column(nullable = false)` | Price cannot be NULL. Column name defaults to `price` (field name) |
| 8 | `@Column(length = 500)` | Description can be up to 500 characters. Can be NULL (default) |
| 9 | `@Column(name = "in_stock")` | Maps the `inStock` Java field to the `in_stock` database column |
| 10 | `= true` | Default value for new products. They are in stock unless specified otherwise |
| 11 | `public Product()` | **Required!** JPA needs a no-argument constructor to create entity instances via reflection |
| 12 | `public Product(String name, ...)` | Convenience constructor for creating products in your code |

### How the Entity Maps to a Table

```
Java Entity Class                    Database Table: products
+---------------------------+       +-------------+--------------+------+
| @Entity                   |       | Column      | Type         | Null |
| class Product {           |       +-------------+--------------+------+
|                           |       |             |              |      |
|   @Id                     | ----> | id          | BIGINT (PK)  | NO   |
|   Long id;                |       |             | AUTO_INCR    |      |
|                           |       |             |              |      |
|   @Column("product_name") | ----> | product_name| VARCHAR(100) | NO   |
|   String name;            |       |             |              |      |
|                           |       |             |              |      |
|   @Column                 | ----> | price       | DOUBLE       | NO   |
|   Double price;           |       |             |              |      |
|                           |       |             |              |      |
|   @Column(length=500)     | ----> | description | VARCHAR(500) | YES  |
|   String description;     |       |             |              |      |
|                           |       |             |              |      |
|   @Column("in_stock")     | ----> | in_stock    | BOOLEAN      | YES  |
|   Boolean inStock;        |       |             |              |      |
| }                         |       +-------------+--------------+------+
+---------------------------+
```

### Understanding @GeneratedValue Strategies

```
+-------------------+-------------------------------------------+
| Strategy          | How It Works                              |
+-------------------+-------------------------------------------+
| IDENTITY          | Database auto-increments the ID.          |
|                   | Most common for H2, MySQL, PostgreSQL     |
|                   | Example: 1, 2, 3, 4, ...                  |
+-------------------+-------------------------------------------+
| SEQUENCE          | Uses a database sequence object.           |
|                   | Preferred for Oracle and PostgreSQL       |
|                   | Can pre-allocate IDs for better           |
|                   | performance                               |
+-------------------+-------------------------------------------+
| TABLE             | Uses a separate table to track IDs.       |
|                   | Works everywhere but is slower.           |
|                   | Rarely used in practice                   |
+-------------------+-------------------------------------------+
| AUTO              | Hibernate picks the best strategy for     |
|                   | your database. Convenient but less        |
|                   | predictable                               |
+-------------------+-------------------------------------------+
| UUID              | Generates a UUID (universally unique ID). |
| (Hibernate 6+)   | Example: 550e8400-e29b-41d4-a716-...      |
+-------------------+-------------------------------------------+
```

---

## Creating More Entity Examples

### A User Entity

```java
package com.example.demo.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50)
    private String firstName;

    @Column(nullable = false, length = 50)
    private String lastName;

    @Column(nullable = false, unique = true, length = 100)   // Line 1
    private String email;

    @Column(nullable = false)
    private Boolean active = true;

    @Column(name = "created_at", updatable = false)          // Line 2
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist                                               // Line 3
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate                                                // Line 4
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    // Default constructor
    public User() {
    }

    public User(String firstName, String lastName, String email) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
    }

    // Getters and setters omitted for brevity
    // (You must include them in your actual code)

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public Boolean getActive() { return active; }
    public void setActive(Boolean active) { this.active = active; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
```

**Key annotations explained:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `unique = true` | Creates a unique constraint on the `email` column. No two users can have the same email |
| 2 | `updatable = false` | Once `created_at` is set, it cannot be changed through JPA updates |
| 3 | `@PrePersist` | This method runs automatically before a new entity is saved to the database for the first time |
| 4 | `@PreUpdate` | This method runs automatically before an existing entity is updated in the database |

---

## Pre-Loading Data with data.sql

### Step 4: Create data.sql

Spring Boot can automatically run a SQL script at startup to populate your database with initial data. Create a file called `data.sql` in the `src/main/resources` folder:

```sql
-- src/main/resources/data.sql

-- Insert sample products
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Laptop', 999.99, 'High-performance laptop with 16GB RAM', true);

INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Smartphone', 699.99, 'Latest model with 128GB storage', true);

INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Headphones', 149.99, 'Noise-cancelling wireless headphones', true);

INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Tablet', 449.99, '10-inch display tablet', false);

INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Smartwatch', 299.99, 'Fitness tracking smartwatch', true);

-- Insert sample users
INSERT INTO users (first_name, last_name, email, active, created_at, updated_at)
VALUES ('Alice', 'Johnson', 'alice@example.com', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO users (first_name, last_name, email, active, created_at, updated_at)
VALUES ('Bob', 'Smith', 'bob@example.com', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO users (first_name, last_name, email, active, created_at, updated_at)
VALUES ('Charlie', 'Brown', 'charlie@example.com', false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

**Important:** Notice that we use `product_name` (the column name from `@Column(name = "product_name")`), not `name` (the Java field name). SQL works with column names, not Java field names.

Also note that `spring.jpa.defer-datasource-initialization=true` must be set in `application.properties` for `data.sql` to run after Hibernate creates the tables.

---

## Using the H2 Console

### Step 5: Access the H2 Console

The H2 console is a web-based database viewer that lets you inspect your tables and run SQL queries directly.

1. Start your Spring Boot application
2. Open your browser and go to `http://localhost:8080/h2-console`
3. Fill in the connection details:

```
+------------------------------------------+
|          H2 Console Login                |
+------------------------------------------+
| Driver Class: org.h2.Driver              |
| JDBC URL:     jdbc:h2:mem:testdb         |
| User Name:    sa                         |
| Password:     (leave empty)              |
+------------------------------------------+
| [ Connect ]                              |
+------------------------------------------+
```

4. Click **Connect**

You will see your tables listed on the left side:

```
+------------------------------------------+
|  H2 Console                              |
+------------------------------------------+
|  Tables:                                 |
|  ├── PRODUCTS                            |
|  │   ├── ID (BIGINT, PK)                |
|  │   ├── PRODUCT_NAME (VARCHAR)          |
|  │   ├── PRICE (DOUBLE)                 |
|  │   ├── DESCRIPTION (VARCHAR)          |
|  │   └── IN_STOCK (BOOLEAN)             |
|  └── USERS                              |
|      ├── ID (BIGINT, PK)                |
|      ├── FIRST_NAME (VARCHAR)            |
|      ├── LAST_NAME (VARCHAR)             |
|      ├── EMAIL (VARCHAR, UNIQUE)         |
|      ├── ACTIVE (BOOLEAN)               |
|      ├── CREATED_AT (TIMESTAMP)          |
|      └── UPDATED_AT (TIMESTAMP)          |
+------------------------------------------+
```

You can run queries directly:

```sql
SELECT * FROM products;
SELECT * FROM users WHERE active = true;
SELECT product_name, price FROM products WHERE price > 500;
```

---

## Seeing SQL in the Console

With `spring.jpa.show-sql=true` and `spring.jpa.properties.hibernate.format_sql=true`, you will see the generated SQL in your application console when the app starts:

```
Hibernate:
    drop table if exists products cascade
Hibernate:
    drop table if exists users cascade
Hibernate:
    create table products (
        id bigint generated by default as identity,
        description varchar(500),
        in_stock boolean,
        product_name varchar(100) not null,
        price double not null,
        primary key (id)
    )
Hibernate:
    create table users (
        id bigint generated by default as identity,
        active boolean,
        created_at timestamp(6),
        email varchar(100) not null unique,
        first_name varchar(50) not null,
        last_name varchar(50) not null,
        updated_at timestamp(6),
        primary key (id)
    )
```

This is Hibernate creating tables based on your `@Entity` classes. Notice how the Java annotations translated into SQL column definitions:

- `@Column(nullable = false)` became `not null`
- `@Column(length = 100)` became `varchar(100)`
- `@Column(unique = true)` became `unique`
- `@GeneratedValue(strategy = GenerationType.IDENTITY)` became `generated by default as identity`

---

## Complete Project Structure

```
src/
├── main/
│   ├── java/com/example/demo/
│   │   ├── DemoApplication.java
│   │   └── entity/
│   │       ├── Product.java
│   │       └── User.java
│   └── resources/
│       ├── application.properties
│       └── data.sql
└── test/
    └── java/com/example/demo/
        └── DemoApplicationTests.java
```

**DemoApplication.java:**

```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

### Startup Output

When you run the application, you will see:

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/

 :: Spring Boot ::                (v3.4.1)

INFO  Starting DemoApplication...
INFO  HikariPool-1 - Starting...
INFO  HikariPool-1 - Start completed.
INFO  H2 console available at '/h2-console'. Database available at 'jdbc:h2:mem:testdb'

Hibernate:
    create table products (
        id bigint generated by default as identity,
        ...
    )

Hibernate:
    create table users (
        id bigint generated by default as identity,
        ...
    )

INFO  Started DemoApplication in 2.345 seconds
```

---

## Java Type to SQL Type Mapping

Here is a quick reference for how Java types map to database column types:

```
+---------------------+------------------------+
| Java Type           | SQL Type (H2)          |
+---------------------+------------------------+
| String              | VARCHAR(255) default   |
| Integer / int       | INTEGER                |
| Long / long         | BIGINT                 |
| Double / double     | DOUBLE                 |
| Float / float       | REAL                   |
| Boolean / boolean   | BOOLEAN                |
| BigDecimal          | DECIMAL                |
| LocalDate           | DATE                   |
| LocalDateTime       | TIMESTAMP              |
| LocalTime           | TIME                   |
| byte[]              | BLOB                   |
| @Lob String         | CLOB (large text)      |
| Enum (with @Enum)   | VARCHAR or INTEGER     |
+---------------------+------------------------+
```

---

## Common Mistakes

### Mistake 1: Missing No-Argument Constructor

```java
// WRONG - No default constructor
@Entity
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    // Only parameterized constructor
    public Product(String name) {
        this.name = name;
    }
    // JPA will throw: "No default constructor for entity"
}

// CORRECT - Always include a no-arg constructor
@Entity
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    public Product() {}  // JPA needs this!

    public Product(String name) {
        this.name = name;
    }
}
```

### Mistake 2: Using Wrong Column Names in data.sql

```sql
-- WRONG - Using Java field names instead of column names
INSERT INTO products (name, inStock) VALUES ('Laptop', true);
-- Error: Column "NAME" not found

-- CORRECT - Use the column names from @Column annotations
INSERT INTO products (product_name, in_stock) VALUES ('Laptop', true);
```

### Mistake 3: Forgetting defer-datasource-initialization

```properties
# WRONG - data.sql runs BEFORE Hibernate creates tables
# This causes "Table not found" errors
spring.jpa.hibernate.ddl-auto=create-drop
# Missing: spring.jpa.defer-datasource-initialization=true

# CORRECT - data.sql runs AFTER Hibernate creates tables
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.defer-datasource-initialization=true
```

### Mistake 4: Using create-drop in Production

```properties
# WRONG - ALL DATA WILL BE LOST when the app restarts!
# Never use this in production
spring.jpa.hibernate.ddl-auto=create-drop

# CORRECT for production
spring.jpa.hibernate.ddl-auto=validate
# Or
spring.jpa.hibernate.ddl-auto=none
```

### Mistake 5: Wrong H2 Console JDBC URL

```
# WRONG - Using the default URL shown in H2 console
JDBC URL: jdbc:h2:~/test

# CORRECT - Must match your application.properties
JDBC URL: jdbc:h2:mem:testdb
```

---

## Best Practices

1. **Use `Long` for entity IDs**: Use the wrapper class `Long` instead of primitive `long`. A new entity has a `null` ID before it is saved, which cannot be represented by `long`.

2. **Always provide a no-arg constructor**: JPA requires it. If you create a parameterized constructor, you must also explicitly add a no-arg constructor.

3. **Use `@Column` for clarity**: Even when the defaults are fine, explicitly specifying column names, nullability, and length makes your code self-documenting.

4. **Use `@PrePersist` and `@PreUpdate` for timestamps**: Instead of manually setting `createdAt` and `updatedAt`, use lifecycle callbacks to do it automatically.

5. **Use `BigDecimal` for money**: `Double` has floating-point precision issues. For financial data, always use `BigDecimal`.

6. **Keep show-sql for development only**: In production, SQL logging should be controlled through your logging framework, not `show-sql`.

7. **Use profile-specific properties**: Create `application-dev.properties` with H2 settings and `application-prod.properties` with real database settings.

8. **Name your tables explicitly**: Use `@Table(name = "products")` to avoid surprises when your class name does not match the table name you want.

---

## Quick Summary

```
+------------------------------------------+
|  Spring Data JPA + H2 Quick Reference    |
+------------------------------------------+
|                                          |
|  DEPENDENCIES:                           |
|  - spring-boot-starter-data-jpa         |
|  - h2 (scope: runtime)                  |
|                                          |
|  KEY ANNOTATIONS:                        |
|  @Entity     -> marks a JPA entity      |
|  @Table      -> sets table name         |
|  @Id         -> primary key             |
|  @GeneratedValue -> auto-generate ID    |
|  @Column     -> column settings         |
|  @PrePersist -> before first save       |
|  @PreUpdate  -> before update           |
|                                          |
|  KEY PROPERTIES:                         |
|  ddl-auto=create-drop (dev)             |
|  ddl-auto=validate (prod)               |
|  show-sql=true (dev only)               |
|  h2.console.enabled=true (dev)          |
|  defer-datasource-initialization=true   |
|                                          |
|  H2 CONSOLE:                            |
|  URL: http://localhost:8080/h2-console  |
|  JDBC URL: jdbc:h2:mem:testdb           |
|  Username: sa | Password: (empty)       |
|                                          |
+------------------------------------------+
```

---

## Key Points

1. **JPA** is a specification for mapping Java objects to database tables. **Hibernate** is the implementation that Spring Boot uses by default.

2. **H2** is an in-memory database perfect for development and testing. No installation needed -- just add the dependency.

3. Every entity needs `@Entity`, `@Id`, and a no-argument constructor.

4. `@GeneratedValue(strategy = GenerationType.IDENTITY)` lets the database auto-increment your primary key.

5. `@Column` lets you customize column names, nullability, length, and uniqueness.

6. `spring.jpa.hibernate.ddl-auto` controls how Hibernate manages your database schema. Use `create-drop` for development, `validate` for production.

7. `data.sql` in `src/main/resources` pre-loads data at startup. Remember to set `defer-datasource-initialization=true`.

8. The H2 console at `/h2-console` lets you visually inspect your database and run SQL queries.

---

## Practice Questions

1. What is the difference between JPA and Hibernate? Why does Spring Boot include both?

2. Explain what `spring.jpa.hibernate.ddl-auto=create-drop` does. Why should you never use it in production?

3. Why does JPA require a no-argument constructor in entity classes?

4. What is the purpose of `spring.jpa.defer-datasource-initialization=true`? What happens without it?

5. How does `@Column(name = "product_name", nullable = false, length = 100)` translate to a database column?

---

## Exercises

### Exercise 1: Create a Book Entity

Create a `Book` entity with the following fields:
- `id` (auto-generated Long)
- `title` (required, max 200 characters)
- `author` (required, max 100 characters)
- `isbn` (unique, max 13 characters)
- `publishedYear` (integer)
- `available` (boolean, default true)

Create a `data.sql` file to insert 5 sample books. Start the application and verify the data in the H2 console.

### Exercise 2: Create an Order Entity with Enum

Create an `Order` entity with:
- `id` (auto-generated)
- `customerName` (required)
- `totalAmount` (BigDecimal, required)
- `status` (enum: PENDING, PROCESSING, SHIPPED, DELIVERED)
- `createdAt` and `updatedAt` (auto-populated timestamps)

Hint: Use `@Enumerated(EnumType.STRING)` to store enum values as strings in the database.

### Exercise 3: Explore Different ddl-auto Settings

Run your application four times, each time with a different `ddl-auto` setting: `create`, `create-drop`, `update`, and `validate`. Observe the console output for each setting. Document what happens and when each setting is appropriate.

---

## What Is Next?

Now that you have entity classes and a database, you need a way to interact with the data. In the next chapter, you will learn about **Repositories and CRUD Operations** -- how to save, find, update, and delete data using Spring Data JPA's powerful `JpaRepository` interface without writing a single SQL query.
