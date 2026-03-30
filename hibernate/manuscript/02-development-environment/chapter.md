# Chapter 2: Setting Up Your Development Environment

---

## Learning Goals

By the end of this chapter, you will be able to:

- Install and verify the Java Development Kit (JDK 17 or later)
- Understand what Maven is and how it manages dependencies
- Create a new Spring Boot 3.x project using Spring Initializr
- Understand the project structure of a Spring Boot JPA application
- Configure application.properties for Hibernate and H2
- Access the H2 database console to inspect your data
- Run your Spring Boot application for the first time

---

## Prerequisites

Before we begin, let us make sure you have the foundational tools in place. Here is what you need and what this chapter will help you set up:

```
+---------------------------------------------------------------+
|                   Development Environment                      |
|                                                                |
|  +------------------+  +------------------+  +--------------+  |
|  |    JDK 17+       |  |   Maven 3.9+     |  |    IDE       |  |
|  |  (Java compiler  |  |  (Build tool,    |  | (IntelliJ or |  |
|  |   and runtime)   |  |   dependency     |  |  VS Code)    |  |
|  |                  |  |   manager)       |  |              |  |
|  +------------------+  +------------------+  +--------------+  |
|                                                                |
|  +------------------+  +------------------+                    |
|  | Spring Initializr|  |   H2 Console     |                    |
|  | (Project creator)|  | (DB browser)     |                    |
|  +------------------+  +------------------+                    |
+---------------------------------------------------------------+
```

You do not need to install a database server. H2 runs entirely inside your application.

---

## Installing the JDK

The Java Development Kit (JDK) includes everything you need to compile and run Java applications. We need JDK 17 or later because Spring Boot 3.x requires it.

### What Version to Install

```
JDK Version    Spring Boot 3.x    Recommended?
------------------------------------------------------
JDK 11         Not supported       No
JDK 17         Supported (LTS)     Yes (minimum)
JDK 21         Supported (LTS)     Yes (latest LTS)
JDK 22+        Supported           Optional
```

**LTS** stands for Long-Term Support. JDK 17 and 21 are LTS releases, meaning they receive security updates for years. Either one is a great choice. This book uses JDK 17 syntax, which is compatible with all later versions.

### Installing on macOS

The easiest way is using Homebrew:

```bash
# Install Homebrew if you do not have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install JDK 17
brew install openjdk@17

# Add to PATH (add this line to your ~/.zshrc or ~/.bash_profile)
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

# Verify installation
java -version
```

You should see output similar to:

```
openjdk version "17.0.10" 2024-01-16
OpenJDK Runtime Environment (build 17.0.10+7)
OpenJDK 64-Bit Server VM (build 17.0.10+7, mixed mode)
```

### Installing on Windows

1. Download the JDK installer from [https://adoptium.net](https://adoptium.net) (Eclipse Temurin)
2. Run the installer and check "Set JAVA_HOME variable"
3. Open a new Command Prompt and verify:

```bash
java -version
javac -version
```

### Installing on Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-17-jdk

# Fedora/RHEL
sudo dnf install java-17-openjdk-devel

# Verify
java -version
```

### Verifying Your Installation

Run both commands to ensure the JDK (not just JRE) is installed:

```bash
# Check the runtime
java -version

# Check the compiler (this confirms JDK, not just JRE)
javac -version
```

If `java` works but `javac` does not, you installed a JRE (Java Runtime Environment) instead of a JDK. Go back and install the full JDK.

---

## Understanding Maven

Maven is a build tool and dependency manager for Java projects. It handles two critical tasks:

1. **Dependency management**: You declare which libraries your project needs (like Hibernate, Spring Boot, H2), and Maven downloads them automatically.
2. **Build lifecycle**: Maven compiles your code, runs tests, and packages your application into a runnable JAR file.

### How Maven Works

```
+------------------------------------------------------------------+
|                        Your Project                               |
|                                                                   |
|  pom.xml                                                          |
|  (declares dependencies)                                          |
|                                                                   |
|  <dependency>                    Maven reads pom.xml              |
|    spring-boot-starter-data-jpa  and downloads JARs               |
|  </dependency>            -----> from Maven Central               |
|  <dependency>                    Repository (the internet)        |
|    h2database                                                     |
|  </dependency>                                                    |
|                                                                   |
|  +------------------------------------------------------------+  |
|  |  ~/.m2/repository/ (local cache)                            |  |
|  |                                                             |  |
|  |  spring-boot-starter-data-jpa-3.2.x.jar                    |  |
|  |  hibernate-core-6.4.x.jar                                  |  |
|  |  h2-2.x.jar                                                |  |
|  |  jakarta.persistence-api-3.1.x.jar                         |  |
|  |  ... (all transitive dependencies)                          |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

When you add `spring-boot-starter-data-jpa` as a dependency, Maven does not just download that one JAR. It also downloads all of its **transitive dependencies** — the libraries that library depends on. This single starter pulls in:

```
spring-boot-starter-data-jpa
  |
  +-- spring-data-jpa          (Spring Data JPA)
  |     +-- spring-data-commons
  |
  +-- hibernate-core            (Hibernate 6.x)
  |     +-- jakarta.persistence-api  (JPA 3.1)
  |     +-- jboss-logging
  |     +-- byte-buddy          (bytecode generation)
  |
  +-- spring-boot-starter-jdbc  (JDBC support)
  |     +-- HikariCP            (connection pool)
  |     +-- spring-jdbc
  |
  +-- spring-boot-starter-aop   (AOP for transactions)
        +-- aspectjweaver
```

You declare one dependency, and Maven brings in over 20 JARs. This is why dependency management is essential — doing this by hand would be tedious and error-prone.

### Installing Maven

Maven comes bundled with most IDEs (IntelliJ, Eclipse) and is included in the Maven Wrapper that Spring Initializr generates. You usually do not need to install Maven separately. But if you want it available on the command line:

**macOS:**
```bash
brew install maven
mvn -version
```

**Windows:**
Download from [https://maven.apache.org/download.cgi](https://maven.apache.org/download.cgi), unzip, and add the `bin` directory to your PATH.

**Linux:**
```bash
sudo apt install maven    # Ubuntu/Debian
sudo dnf install maven    # Fedora/RHEL
mvn -version
```

### The Maven Wrapper

Every Spring Boot project generated by Spring Initializr includes a **Maven Wrapper** (`mvnw` on macOS/Linux, `mvnw.cmd` on Windows). This is a script that downloads and uses the correct Maven version for your project, without requiring a global Maven installation.

```bash
# Instead of:
mvn spring-boot:run

# You can use:
./mvnw spring-boot:run     # macOS/Linux
mvnw.cmd spring-boot:run   # Windows
```

Throughout this book, we will use `mvn` in examples, but you can always substitute `./mvnw` if you prefer the wrapper.

---

## Choosing an IDE

You can use any Java IDE or text editor, but two options stand out for Spring Boot development:

### IntelliJ IDEA (Recommended)

IntelliJ IDEA is the most popular IDE for Java and Spring Boot development. The Community Edition (free) supports Java and Maven. The Ultimate Edition (paid, free for students) adds Spring Boot support, database tools, and JPA entity designers.

```
IntelliJ IDEA Features for Hibernate/JPA:
+------------------------------------------+
| Community (Free)    | Ultimate (Paid)     |
|---------------------|---------------------|
| Java editing        | Everything in CE    |
| Maven support       | Spring Boot support |
| Code completion     | JPA entity diagram  |
| Debugging           | Database tools      |
| Git integration     | JPQL completion     |
| Refactoring         | Hibernate console   |
+------------------------------------------+
```

Download from: [https://www.jetbrains.com/idea/download/](https://www.jetbrains.com/idea/download/)

### Visual Studio Code

VS Code is lightweight and free. With the right extensions, it becomes a capable Java IDE:

Required extensions:
- **Extension Pack for Java** (by Microsoft) — Java language support
- **Spring Boot Extension Pack** (by VMware) — Spring Boot support
- **Maven for Java** (by Microsoft) — Maven project support

### Other Options

Eclipse (with Spring Tools Suite), NetBeans, or even a plain text editor with command-line Maven all work. The code in this book is IDE-independent.

---

## Creating Your Project with Spring Initializr

Spring Initializr is a web tool that generates a ready-to-run Spring Boot project with the dependencies you choose. It is the standard way to start a new Spring Boot project.

### Step-by-Step Setup

1. Open your browser and go to [https://start.spring.io](https://start.spring.io)

2. Fill in the project settings:

```
Setting              Value                      Why
------------------------------------------------------------------
Project              Maven                      Build tool
Language             Java                       Programming language
Spring Boot          3.3.x (latest stable)      Framework version
Group                com.example                Your organization
Artifact             hibernate-demo             Project name
Name                 hibernate-demo             Application name
Description          Learning Hibernate & JPA   Your description
Package name         com.example.hibernatedemo  Base package
Packaging            Jar                        Executable JAR
Java                 17                         JDK version
```

3. Add the following dependencies (click "Add Dependencies"):

```
+-----------------------------------------------------------+
|  Dependencies to Add                                       |
|                                                            |
|  [x] Spring Data JPA                                       |
|      Provides: JpaRepository, EntityManager,               |
|      auto-configuration for Hibernate                      |
|                                                            |
|  [x] H2 Database                                           |
|      Provides: In-memory database, no installation         |
|      needed, web console for browsing data                 |
|                                                            |
|  [x] Spring Web                                            |
|      Provides: REST controllers, embedded Tomcat           |
|      (needed for H2 console and later chapters)            |
|                                                            |
|  [x] Spring Boot DevTools (optional)                       |
|      Provides: Automatic restart on code changes,          |
|      LiveReload, relaxed development settings              |
+-----------------------------------------------------------+
```

4. Click **"Generate"** to download the project as a ZIP file.

5. Unzip the file and open the project in your IDE.

### What Spring Initializr Creates

```
hibernate-demo/
|
+-- pom.xml                          <-- Maven configuration
+-- mvnw                             <-- Maven Wrapper (Mac/Linux)
+-- mvnw.cmd                         <-- Maven Wrapper (Windows)
+-- .mvn/                            <-- Maven Wrapper config
|
+-- src/
|   +-- main/
|   |   +-- java/
|   |   |   +-- com/example/hibernatedemo/
|   |   |       +-- HibernateDemoApplication.java   <-- Main class
|   |   |
|   |   +-- resources/
|   |       +-- application.properties              <-- Configuration
|   |       +-- static/                              <-- Static files
|   |       +-- templates/                           <-- Template files
|   |
|   +-- test/
|       +-- java/
|           +-- com/example/hibernatedemo/
|               +-- HibernateDemoApplicationTests.java  <-- Test class
|
+-- .gitignore
```

Let us examine the key files.

---

## Understanding the Project Structure

### The pom.xml File

The `pom.xml` is the heart of your Maven project. It declares your project metadata and dependencies. Here is what Spring Initializr generates (simplified):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- Spring Boot parent: provides dependency versions -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.0</version>
    </parent>

    <!-- Your project coordinates -->
    <groupId>com.example</groupId>
    <artifactId>hibernate-demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>hibernate-demo</name>
    <description>Learning Hibernate and JPA</description>

    <!-- Java version -->
    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <!-- Spring Data JPA (includes Hibernate 6.x) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- H2 In-Memory Database -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Spring Web (for REST and H2 console) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- DevTools (optional, for hot reload) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-devtools</artifactId>
            <scope>runtime</scope>
            <optional>true</optional>
        </dependency>

        <!-- Test dependencies -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

**Key observations:**

- **No version numbers on dependencies**: The Spring Boot parent manages all version numbers. When you declare `spring-boot-starter-data-jpa`, the parent decides which version of Hibernate, Spring Data, HikariCP, and Jakarta Persistence to use. This prevents version conflicts.

- **`scope: runtime`** for H2 means the H2 JAR is available when the app runs but not at compile time (you never import H2 classes directly in your code).

- **`spring-boot-starter-data-jpa`** is the single dependency that brings in JPA, Hibernate, Spring Data JPA, HikariCP (connection pool), and everything else you need.

### How Dependencies Flow

```
What you declare          What you actually get
in pom.xml                (transitive dependencies)
-------------------       ----------------------------------

spring-boot-              +-- spring-data-jpa 3.3.x
starter-data-jpa     -->  +-- hibernate-core 6.5.x
                          +-- jakarta.persistence-api 3.1.x
                          +-- HikariCP 5.x
                          +-- spring-jdbc 6.1.x
                          +-- spring-tx 6.1.x (transactions)
                          +-- spring-orm 6.1.x
                          +-- spring-aop 6.1.x

h2                   -->  H2 Database Engine 2.x

spring-boot-              +-- spring-webmvc 6.1.x
starter-web          -->  +-- embedded Tomcat 10.x
                          +-- jackson (JSON processing)
```

### The Main Application Class

```java
package com.example.hibernatedemo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class HibernateDemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(HibernateDemoApplication.class, args);
    }
}
```

This tiny class does a lot thanks to `@SpringBootApplication`, which combines three annotations:

```
@SpringBootApplication
  |
  +-- @SpringBootConfiguration   (This is a configuration class)
  |
  +-- @EnableAutoConfiguration   (Auto-configure based on dependencies)
  |     |
  |     +-- Detects spring-data-jpa on classpath
  |     |   --> Configures EntityManagerFactory, TransactionManager
  |     |
  |     +-- Detects h2 on classpath
  |     |   --> Configures DataSource with H2
  |     |
  |     +-- Detects spring-web on classpath
  |         --> Starts embedded Tomcat
  |
  +-- @ComponentScan             (Scan this package and sub-packages
                                  for @Component, @Service,
                                  @Repository, @Controller)
```

When you run this class, Spring Boot:
1. Starts an embedded Tomcat server
2. Creates an H2 in-memory database
3. Creates a Hibernate `SessionFactory` (which implements JPA's `EntityManagerFactory`)
4. Sets up transaction management
5. Scans for `@Entity` classes and creates the corresponding tables

All of this happens automatically because of the dependencies in your `pom.xml`.

---

## Configuring application.properties

The `src/main/resources/application.properties` file controls how Spring Boot and Hibernate behave. The generated file is empty — Spring Boot uses sensible defaults. But for learning, we want to customize several settings.

Replace the empty file with:

```properties
# ===== Application Name =====
spring.application.name=hibernate-demo

# ===== H2 Database Configuration =====
# Use a named in-memory database (accessible from H2 console)
spring.datasource.url=jdbc:h2:mem:learndb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# ===== H2 Console (Web UI to browse your database) =====
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console

# ===== JPA / Hibernate Configuration =====
# Auto-create tables from @Entity classes (good for development)
spring.jpa.hibernate.ddl-auto=create-drop

# Show SQL statements in the console (essential for learning)
spring.jpa.show-sql=true

# Format the SQL for readability
spring.jpa.properties.hibernate.format_sql=true

# Show parameter values bound to SQL statements
logging.level.org.hibernate.orm.jdbc.bind=TRACE

# Hibernate dialect (optional - Hibernate auto-detects H2)
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
```

Let us understand each setting:

### Database URL

```properties
spring.datasource.url=jdbc:h2:mem:learndb
```

This URL tells H2 to create an **in-memory** database named `learndb`. The format is:

```
jdbc:h2:mem:learndb
|    |  |   |
|    |  |   +-- Database name
|    |  +------ "mem" means in-memory (data lost on restart)
|    +--------- H2 database
+-------------- JDBC protocol
```

Other H2 URL formats you might see:

```
jdbc:h2:mem:testdb           In-memory, named "testdb"
jdbc:h2:file:./data/mydb     File-based, persists to disk
jdbc:h2:tcp://host/db        Server mode, remote access
```

### DDL Auto Strategy

```properties
spring.jpa.hibernate.ddl-auto=create-drop
```

This controls what Hibernate does with the database schema on startup:

```
Strategy        On Startup                On Shutdown      Use Case
---------------------------------------------------------------------------
none            Nothing                   Nothing          Production
validate        Validate schema matches   Nothing          Production
                entities (error if not)
update          Add new tables/columns,   Nothing          Careful dev
                never drops anything
create          Drop and recreate all     Nothing          Development
                tables
create-drop     Drop and recreate all     Drop all         Testing and
                tables                    tables           learning
```

For learning, `create-drop` is perfect. Every time you start the app, you get a fresh database with the correct schema. In production, you would use `validate` (and manage schema changes with Flyway, covered in Chapter 26).

### SQL Logging

```properties
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
logging.level.org.hibernate.orm.jdbc.bind=TRACE
```

These settings make Hibernate print every SQL statement it generates. This is one of the most important learning tools. When you call `repository.save(customer)`, you will see exactly what SQL Hibernate runs:

```sql
Hibernate:
    insert
    into
        customers
        (email, name, id)
    values
        (?, ?, default)

-- With bind parameter logging:
binding parameter (1:VARCHAR) <- [alice@example.com]
binding parameter (2:VARCHAR) <- [Alice Johnson]
```

**Always enable SQL logging during development.** Understanding what SQL Hibernate generates is essential for writing efficient code and debugging performance issues.

---

## The H2 Console

One of H2's best features is its built-in web console. It lets you browse tables, run SQL queries, and inspect your data — all in your browser.

### Accessing the Console

1. Start your application (we will do this shortly)
2. Open your browser to: `http://localhost:8080/h2-console`
3. Enter the connection settings:

```
+------------------------------------------+
|         H2 Console Login                  |
|                                           |
|  Driver Class: org.h2.Driver              |
|  JDBC URL:     jdbc:h2:mem:learndb        |
|  User Name:    sa                         |
|  Password:     (leave empty)              |
|                                           |
|  [Connect]                                |
+------------------------------------------+
```

**Important**: The JDBC URL must match exactly what is in your `application.properties`. If you used `jdbc:h2:mem:learndb` in properties, use the same URL in the console.

### What You Can Do in the Console

```
+------------------------------------------------------------------+
|  H2 Console                                                       |
|                                                                   |
|  Left panel:           |  Right panel:                            |
|  +------------------+  |  +------------------------------------+  |
|  | Tables:          |  |  | SQL Editor:                        |  |
|  |   CUSTOMERS      |  |  |                                    |  |
|  |   ORDERS         |  |  | SELECT * FROM customers;           |  |
|  |   ORDER_ITEMS    |  |  |                                    |  |
|  +------------------+  |  | [Run]                              |  |
|                        |  |                                    |  |
|  Click a table to      |  | Results:                           |  |
|  see its columns       |  | | ID | NAME  | EMAIL             | |  |
|  and auto-generate     |  | | 1  | Alice | alice@example.com | |  |
|  a SELECT query        |  | | 2  | Bob   | bob@example.com   | |  |
|                        |  +------------------------------------+  |
+------------------------------------------------------------------+
```

The H2 console is invaluable for verifying that your entities created the right tables, your data was saved correctly, and your relationships are set up properly.

---

## Running Your Application

### From the Command Line

Navigate to your project directory and run:

```bash
# Using Maven
mvn spring-boot:run

# Or using the Maven Wrapper
./mvnw spring-boot:run
```

### From Your IDE

**IntelliJ IDEA**: Open `HibernateDemoApplication.java` and click the green play button next to the `main` method.

**VS Code**: Open `HibernateDemoApplication.java` and click "Run" above the `main` method (or press F5).

### What You Should See

When the application starts successfully, you will see output like this in the console:

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/

 :: Spring Boot ::                (v3.3.0)

Starting HibernateDemoApplication using Java 17.0.10
HikariPool-1 - Starting...
HikariPool-1 - Start completed.
H2 console available at '/h2-console'. Database available at 'jdbc:h2:mem:learndb'
Hibernate: create table ...
Tomcat started on port 8080
Started HibernateDemoApplication in 2.3 seconds
```

The key lines to look for:

```
Startup Flow:
+--------------------------------------------------------------------+
|  1. Spring Boot banner appears                                      |
|  2. HikariCP connection pool starts                                 |
|  3. H2 console enabled at /h2-console                               |
|  4. Hibernate creates tables (you will see CREATE TABLE statements)  |
|  5. Tomcat starts on port 8080                                      |
|  6. "Started HibernateDemoApplication" -- success!                   |
+--------------------------------------------------------------------+
```

If you see errors, check the troubleshooting section at the end of this chapter.

### Verifying Everything Works

1. Open `http://localhost:8080/h2-console` in your browser
2. Connect using the settings shown earlier
3. You should see an empty database (no tables yet — we will create entities in Chapter 3)

### Stopping the Application

Press `Ctrl+C` in the terminal, or click the stop button in your IDE.

---

## Project Structure Deep Dive

As your project grows, you will organize code into packages. Here is the standard package structure for a Spring Boot JPA application:

```
com.example.hibernatedemo/
|
+-- HibernateDemoApplication.java     Main class (already exists)
|
+-- entity/                           JPA entity classes
|   +-- Customer.java                 @Entity classes go here
|   +-- Order.java
|   +-- Product.java
|
+-- repository/                       Data access layer
|   +-- CustomerRepository.java       JpaRepository interfaces
|   +-- OrderRepository.java
|
+-- service/                          Business logic layer
|   +-- CustomerService.java          @Service classes
|   +-- OrderService.java
|
+-- controller/                       REST API layer
|   +-- CustomerController.java       @RestController classes
|   +-- OrderController.java
|
+-- dto/                              Data Transfer Objects
|   +-- CustomerRequest.java          Request/Response DTOs
|   +-- CustomerResponse.java
|
+-- config/                           Configuration classes
|   +-- AppConfig.java                @Configuration classes
|
+-- exception/                        Custom exceptions
    +-- ResourceNotFoundException.java
```

### How the Layers Connect

```
+-------------------------------------------------------------------+
|                                                                    |
|   HTTP Request                                                     |
|       |                                                            |
|       v                                                            |
|   +------------------+                                             |
|   |   Controller     |  Receives HTTP requests, validates input,   |
|   |   (@RestController)  returns HTTP responses                    |
|   +------------------+                                             |
|           |                                                        |
|           v                                                        |
|   +------------------+                                             |
|   |   Service        |  Business logic, transaction boundaries,    |
|   |   (@Service)     |  orchestrates repository calls              |
|   +------------------+                                             |
|           |                                                        |
|           v                                                        |
|   +------------------+                                             |
|   |   Repository     |  Data access, JPA queries,                  |
|   |   (@Repository / |  Spring Data JPA auto-implementation        |
|   |    JpaRepository)|                                             |
|   +------------------+                                             |
|           |                                                        |
|           v                                                        |
|   +------------------+                                             |
|   |   Entity         |  JPA entities, database table mapping       |
|   |   (@Entity)      |                                             |
|   +------------------+                                             |
|           |                                                        |
|           v                                                        |
|   +------------------+                                             |
|   |   Hibernate/JPA  |  ORM engine, SQL generation, caching        |
|   +------------------+                                             |
|           |                                                        |
|           v                                                        |
|   +------------------+                                             |
|   |   H2 Database    |  In-memory database                         |
|   +------------------+                                             |
|                                                                    |
+-------------------------------------------------------------------+
```

Each layer has a specific responsibility:

- **Controller**: Handles HTTP. Never contains database logic.
- **Service**: Contains business rules. Manages transactions.
- **Repository**: Talks to the database. No business logic.
- **Entity**: Maps Java objects to database tables. Pure data.

We will build this structure gradually over the next several chapters.

---

## Understanding Auto-Configuration

One thing that surprises beginners about Spring Boot is how much happens automatically. Let us trace what Spring Boot does when it sees `spring-boot-starter-data-jpa` and `h2` in your dependencies:

```
Spring Boot Auto-Configuration Flow:
+---------------------------------------------------------------------+
|                                                                      |
|  1. Scans classpath                                                  |
|     - Finds hibernate-core.jar --> "JPA provider detected"           |
|     - Finds h2.jar --> "H2 database detected"                        |
|     - Finds spring-data-jpa.jar --> "Spring Data JPA detected"       |
|                                                                      |
|  2. Creates DataSource                                               |
|     - Reads spring.datasource.* properties                          |
|     - Creates HikariDataSource (connection pool)                     |
|     - Connects to jdbc:h2:mem:learndb                                |
|                                                                      |
|  3. Creates EntityManagerFactory                                     |
|     - Scans for @Entity classes                                      |
|     - Builds Hibernate SessionFactory                                |
|     - Applies ddl-auto strategy (create-drop)                        |
|     - Creates/validates database tables                              |
|                                                                      |
|  4. Creates TransactionManager                                       |
|     - JpaTransactionManager                                          |
|     - Makes @Transactional work                                      |
|                                                                      |
|  5. Creates Repository Implementations                               |
|     - Finds interfaces extending JpaRepository                       |
|     - Generates implementing classes at runtime                      |
|     - Registers them as Spring beans                                 |
|                                                                      |
+---------------------------------------------------------------------+
```

All of this happens in about 2 seconds when you start the application. Without Spring Boot, you would need to configure each of these components manually with XML or Java configuration classes. Spring Boot's auto-configuration is one of its biggest productivity advantages.

---

## Application Properties Reference

Here is a complete reference of the most important properties for Hibernate and JPA in Spring Boot:

```properties
# ===== DataSource =====
spring.datasource.url=                    # JDBC URL
spring.datasource.username=               # Database username
spring.datasource.password=               # Database password
spring.datasource.driver-class-name=      # JDBC driver class

# ===== JPA / Hibernate =====
spring.jpa.hibernate.ddl-auto=            # none|validate|update|create|create-drop
spring.jpa.show-sql=                      # true|false (log SQL)
spring.jpa.database-platform=             # Hibernate dialect class
spring.jpa.open-in-view=                  # true|false (OSIV, default true)
spring.jpa.generate-ddl=                  # true|false

# ===== Hibernate-Specific =====
spring.jpa.properties.hibernate.format_sql=          # true|false
spring.jpa.properties.hibernate.use_sql_comments=    # true|false
spring.jpa.properties.hibernate.jdbc.batch_size=     # e.g., 25
spring.jpa.properties.hibernate.order_inserts=       # true|false
spring.jpa.properties.hibernate.order_updates=       # true|false
spring.jpa.properties.hibernate.generate_statistics= # true|false
spring.jpa.properties.hibernate.default_batch_fetch_size= # e.g., 16

# ===== H2 Console =====
spring.h2.console.enabled=                # true|false
spring.h2.console.path=                   # e.g., /h2-console

# ===== Connection Pool (HikariCP) =====
spring.datasource.hikari.maximum-pool-size=    # default 10
spring.datasource.hikari.minimum-idle=         # default same as max
spring.datasource.hikari.connection-timeout=   # default 30000 (30s)

# ===== Logging =====
logging.level.org.hibernate.SQL=               # DEBUG (show SQL)
logging.level.org.hibernate.orm.jdbc.bind=     # TRACE (show params)
logging.level.org.hibernate.stat=              # DEBUG (statistics)
```

You do not need to memorize these. Bookmark this page and refer back when you need to adjust a setting.

---

## Troubleshooting Common Setup Issues

### Problem: "Port 8080 already in use"

Another application is using port 8080. Either stop it or change the port:

```properties
server.port=8081
```

### Problem: "Cannot determine embedded database driver class"

Your `pom.xml` is missing the H2 dependency, or it has the wrong scope:

```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

### Problem: "Failed to configure a DataSource"

Spring Boot cannot find a database. Ensure your `application.properties` has:

```properties
spring.datasource.url=jdbc:h2:mem:learndb
```

### Problem: H2 Console shows "Database not found"

Make sure the JDBC URL in the H2 console login matches exactly what is in `application.properties`:

```
In application.properties:     jdbc:h2:mem:learndb
In H2 Console login:           jdbc:h2:mem:learndb   <-- Must match!
```

### Problem: "java: error: release version 17 not supported"

Your IDE is using an older JDK. In IntelliJ:
1. Go to File > Project Structure > Project
2. Set Project SDK to JDK 17
3. Set Language Level to 17

In VS Code, set `java.configuration.runtimes` in settings.

### Problem: Maven dependencies not downloading

```bash
# Force Maven to re-download dependencies
mvn dependency:purge-local-repository
mvn clean install
```

---

## Common Mistakes

1. **Not enabling SQL logging**: Without `spring.jpa.show-sql=true`, you cannot see what Hibernate is doing. This is the number one debugging tool for JPA applications. Always enable it during development.

2. **Using `ddl-auto=update` in production**: The `update` strategy tries to modify your database schema automatically. It never drops columns or tables, which can leave orphaned structures. In production, use `validate` and manage schema changes with Flyway (Chapter 26).

3. **Forgetting the Maven Wrapper**: If you share your project with others who do not have Maven installed, they need the `mvnw`/`mvnw.cmd` files. Always commit these to version control.

4. **Wrong H2 Console URL**: The JDBC URL in the H2 console login page defaults to `jdbc:h2:~/test`. You must change it to match your `application.properties` (e.g., `jdbc:h2:mem:learndb`).

5. **Mixing javax and jakarta imports**: If you copy code from older tutorials, you might accidentally use `javax.persistence.*` imports. Spring Boot 3.x and Hibernate 6.x require `jakarta.persistence.*`. If your IDE suggests `javax`, you have an old dependency somewhere.

---

## Best Practices

1. **Use Spring Initializr for new projects**: It generates a correctly configured project with compatible dependency versions. Do not try to set up a Spring Boot project from scratch.

2. **Commit the Maven Wrapper**: Include `mvnw`, `mvnw.cmd`, and the `.mvn/` directory in version control. This ensures everyone on your team uses the same Maven version.

3. **Use profiles for different environments**: Create `application-dev.properties` for development and `application-prod.properties` for production. Activate them with `spring.profiles.active=dev`.

4. **Enable SQL logging during development, disable in production**: Logging every SQL statement helps you learn and debug, but it creates unnecessary log noise in production.

5. **Pin your Java version**: Set `<java.version>17</java.version>` in `pom.xml` so the project compiles with the same Java version everywhere.

---

## Summary

In this chapter, you set up a complete development environment for learning Hibernate and JPA:

- **JDK 17+** provides the Java compiler and runtime needed for Spring Boot 3.x and Hibernate 6.x.

- **Maven** manages your dependencies and build process. The `pom.xml` file declares what your project needs, and Maven downloads everything automatically.

- **Spring Initializr** generates a ready-to-run Spring Boot project with the right dependencies (`spring-boot-starter-data-jpa`, `h2`, `spring-boot-starter-web`).

- **application.properties** controls database connection, Hibernate behavior (ddl-auto, SQL logging), and the H2 console.

- **H2 Console** provides a web-based database browser at `/h2-console` where you can inspect tables and run SQL queries.

- **Spring Boot auto-configuration** detects your dependencies and automatically creates the DataSource, EntityManagerFactory, TransactionManager, and repository implementations.

- **The standard project structure** organizes code into entity, repository, service, controller, and dto packages — each with a clear responsibility.

---

## Interview Questions

**Q1: What is the difference between `ddl-auto=update` and `ddl-auto=create-drop`?**

`update` adds new tables and columns to match your entities but never drops existing structures. It is additive only. `create-drop` drops all tables on startup, recreates them from entity definitions, and drops them again on shutdown. `create-drop` is for testing; `update` is sometimes used in development but is risky for production.

**Q2: Why does Spring Boot only need one dependency (`spring-boot-starter-data-jpa`) to set up Hibernate?**

The starter is a meta-dependency that pulls in all required libraries through transitive dependencies: Hibernate Core, Jakarta Persistence API, Spring Data JPA, HikariCP (connection pool), Spring JDBC, and Spring ORM. Spring Boot's auto-configuration then wires everything together based on what it finds on the classpath.

**Q3: What is HikariCP and why is it important?**

HikariCP is a high-performance JDBC connection pool. Instead of creating a new database connection for every request (which is expensive), HikariCP maintains a pool of reusable connections. It is the default connection pool in Spring Boot and is widely regarded as the fastest available.

**Q4: What happens when Spring Boot starts and finds `@Entity` classes with `ddl-auto=create-drop`?**

Hibernate scans for all classes annotated with `@Entity`, generates `CREATE TABLE` SQL statements based on the field annotations (`@Column`, `@Id`, etc.), and executes them against the database. When the application shuts down, it generates and executes `DROP TABLE` statements for all entity tables.

**Q5: How does Spring Boot know to use Hibernate as the JPA provider?**

Spring Boot's auto-configuration detects `hibernate-core` on the classpath (pulled in by `spring-boot-starter-data-jpa`). It then creates a `LocalContainerEntityManagerFactoryBean` configured with Hibernate as the provider. If you added EclipseLink to the classpath instead, Spring Boot would detect and use that.

**Q6: What is the purpose of `spring.jpa.open-in-view`?**

Open-Session-In-View (OSIV) keeps the Hibernate session open for the entire HTTP request lifecycle, including the view rendering phase. This allows lazy-loaded associations to be fetched during view rendering without a `LazyInitializationException`. It defaults to `true` in Spring Boot but is considered an anti-pattern because it can lead to N+1 queries and should be set to `false` in most applications.

---

## Practice Exercises

**Exercise 1: Create Your Project**
Follow the steps in this chapter to create a Spring Boot project with Spring Initializr. Start the application and verify that:
- The Spring Boot banner appears in the console
- The H2 console is accessible at `http://localhost:8080/h2-console`
- You can connect to the database using the credentials from `application.properties`

**Exercise 2: Experiment with Properties**
Try changing the following properties one at a time and observe the effect:
1. Change `spring.jpa.show-sql` to `false` — what disappears from the console?
2. Change `spring.h2.console.path` to `/db` — where is the console now?
3. Change `server.port` to `9090` — what URL do you use?
4. Remove the `spring.datasource.url` line — what error do you get?

**Exercise 3: Explore the Dependencies**
Run this Maven command to see all dependencies (including transitive ones):

```bash
mvn dependency:tree
```

Find and list: the version of Hibernate Core, the version of the Jakarta Persistence API, and the version of HikariCP. Notice how many JARs the single `spring-boot-starter-data-jpa` brings in.

**Exercise 4: Profile Setup**
Create two property files:
- `application-dev.properties` with `spring.jpa.show-sql=true` and `spring.h2.console.enabled=true`
- `application-prod.properties` with `spring.jpa.show-sql=false` and `spring.h2.console.enabled=false`

Run the app with each profile (`-Dspring.profiles.active=dev` or `prod`) and observe the differences.

---

## What Is Next?

In the next chapter, we will **build your first JPA application from scratch**. You will create an `@Entity` class, understand the JPA `EntityManager`, set up a `JpaRepository`, and perform your first database operations. You will see the SQL that Hibernate generates for each operation and verify the results in the H2 console. By the end of Chapter 3, you will have a working application that creates, reads, updates, and deletes data.
