# Chapter 4: Understanding the Project Structure

## What You Will Learn

- The complete folder structure of a Spring Boot project
- What every file and folder does
- How to read `pom.xml` line by line
- What `src/main/java`, `src/main/resources`, and `src/test` contain
- How `application.properties` configures your application
- What `static` and `templates` folders are for
- What the Maven Wrapper (`mvnw`) is
- How starter dependencies work

## Why This Chapter Matters

Imagine you move into a new house. Before you start decorating, you need to know which room is the kitchen, which is the bedroom, and where the electrical panel is. If you plug a washing machine into the wrong outlet, things break.

A Spring Boot project is your house. Each folder has a purpose. Each file has a job. If you put code in the wrong place, things break silently. This chapter gives you a complete tour of the house so you always know where everything belongs.

---

## 4.1 The Complete Folder Tree

Here is the full structure of the project you created in Chapter 3:

```
hello-spring-boot/
│
├── mvnw                              Maven Wrapper script (Mac/Linux)
├── mvnw.cmd                          Maven Wrapper script (Windows)
├── pom.xml                           Project configuration file
│
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           └── hellospringboot/
│   │   │               └── HelloSpringBootApplication.java
│   │   │
│   │   └── resources/
│   │       ├── application.properties    App configuration
│   │       ├── static/                   Static files (CSS, JS, images)
│   │       └── templates/                HTML templates
│   │
│   └── test/
│       └── java/
│           └── com/
│               └── example/
│                   └── hellospringboot/
│                       └── HelloSpringBootApplicationTests.java
│
├── .gitignore                        Files Git should ignore
├── .mvn/
│   └── wrapper/
│       └── maven-wrapper.properties  Maven Wrapper config
│
└── target/                           Build output (created after first build)
```

Let us visit each room in this house.

---

## 4.2 The Root Directory

The root directory is the top-level folder. It contains the most important configuration files.

### pom.xml -- The Heart of the Project

`pom.xml` stands for **Project Object Model**. It is the most important file in a Maven project. It tells Maven:

- What your project is called
- What version of Java to use
- What libraries (dependencies) to download
- How to build the project

Think of `pom.xml` as the blueprint of a house. The builder (Maven) reads the blueprint to know what materials to buy and how to assemble them.

Here is the `pom.xml` from your project, explained line by line:

```xml
<?xml version="1.0" encoding="UTF-8"?>                          <!-- 1 -->
<project xmlns="http://maven.apache.org/POM/4.0.0"              <!-- 2 -->
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">

    <modelVersion>4.0.0</modelVersion>                          <!-- 3 -->

    <parent>                                                     <!-- 4 -->
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.4.4</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>                               <!-- 5 -->
    <artifactId>hello-spring-boot</artifactId>                   <!-- 6 -->
    <version>0.0.1-SNAPSHOT</version>                            <!-- 7 -->
    <name>hello-spring-boot</name>                               <!-- 8 -->
    <description>My first Spring Boot app</description>          <!-- 9 -->

    <properties>                                                 <!-- 10 -->
        <java.version>17</java.version>
    </properties>

    <dependencies>                                               <!-- 11 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>          <!-- 12 -->
            <artifactId>spring-boot-starter-web</artifactId>     <!-- 13 -->
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>          <!-- 14 -->
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>                                  <!-- 15 -->
        </dependency>
    </dependencies>

    <build>                                                      <!-- 16 -->
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```

**Line-by-line explanation:**

- **Line 1:** XML declaration. Every `pom.xml` starts with this. It says "this is an XML file."

- **Line 2:** The `<project>` tag. Everything in the `pom.xml` lives inside this tag. The `xmlns` attributes tell the XML parser what format to expect.

- **Line 3:** `<modelVersion>4.0.0</modelVersion>` -- The version of the POM format. It is always 4.0.0. You never change this.

- **Lines 4:** `<parent>` -- This is the secret sauce. Your project **inherits** settings from `spring-boot-starter-parent`. This parent POM defines:
  - Default Java version
  - Default plugin versions
  - Default dependency versions
  - Sensible default settings

  Think of it as inheriting a house that already has plumbing and electricity. You just need to add furniture.

- **Line 5:** `<groupId>com.example</groupId>` -- Your organization identifier. Like a last name for the project.

- **Line 6:** `<artifactId>hello-spring-boot</artifactId>` -- Your project name. Like a first name.

- **Line 7:** `<version>0.0.1-SNAPSHOT</version>` -- The current version of your project. SNAPSHOT means "work in progress."

- **Line 8-9:** `<name>` and `<description>` -- Human-readable metadata. They do not affect how the project builds.

- **Line 10:** `<properties>` -- Variables you can reuse. Here, `java.version` is set to 17. Maven and Spring Boot use this to configure the Java compiler.

- **Line 11:** `<dependencies>` -- The libraries your project needs. This is where you list everything your code depends on.

- **Lines 12-13:** `spring-boot-starter-web` -- The web dependency. Notice there is no `<version>` tag. The version comes from the parent POM. This is one benefit of using the parent.

- **Lines 14-15:** `spring-boot-starter-test` -- Testing libraries (JUnit, Mockito, etc.). The `<scope>test</scope>` means this library is only used when running tests, not in the final application.

- **Line 16:** `<build>` -- Build configuration. The `spring-boot-maven-plugin` lets you run the app with `mvn spring-boot:run` and creates executable JAR files.

```
+------------------------------------------------------+
|         How the Parent POM Works                     |
+------------------------------------------------------+
|                                                       |
|   spring-boot-starter-parent (v3.4.4)                |
|     |                                                 |
|     ├── Sets Java version defaults                    |
|     ├── Manages 300+ dependency versions              |
|     ├── Configures Maven plugins                      |
|     └── Defines sensible defaults                     |
|           |                                           |
|           v                                           |
|   Your pom.xml inherits all of the above.             |
|   You only need to list WHAT you need,                |
|   not WHICH VERSION.                                  |
|                                                       |
+------------------------------------------------------+
```

---

## 4.3 The src/main/java Directory

This is where your Java source code lives.

```
src/main/java/
└── com/
    └── example/
        └── hellospringboot/
            ├── HelloSpringBootApplication.java
            └── HelloController.java
```

The folder path `com/example/hellospringboot` matches the Java package `com.example.hellospringboot`. In Java, every folder is a package. Every class must declare which package it belongs to.

**Why packages matter:**

- They organize your code (like folders organize files on your computer).
- They prevent naming conflicts (two classes can have the same name if they are in different packages).
- Spring Boot scans the package of the main class and its sub-packages for components.

As your project grows, you will create sub-packages:

```
src/main/java/
└── com/
    └── example/
        └── hellospringboot/
            ├── HelloSpringBootApplication.java
            ├── controller/
            │   ├── HelloController.java
            │   └── UserController.java
            ├── service/
            │   ├── UserService.java
            │   └── EmailService.java
            ├── repository/
            │   └── UserRepository.java
            └── model/
                └── User.java
```

This is a common pattern in Spring Boot projects:

| Package      | Purpose                                    |
|-------------|---------------------------------------------|
| `controller` | Classes that handle web requests            |
| `service`    | Classes that contain business logic         |
| `repository` | Classes that talk to the database           |
| `model`      | Classes that represent data (entities)      |

We will use this pattern in later chapters.

---

## 4.4 The src/main/resources Directory

This directory holds non-Java files that your application needs.

```
src/main/resources/
├── application.properties
├── static/
└── templates/
```

### application.properties

This is the main configuration file. It controls how your application behaves. It uses a simple `key=value` format.

```properties
# Server configuration
server.port=8080

# Application name
spring.application.name=hello-spring-boot
```

Each line sets one property. Lines starting with `#` are comments. Spring Boot reads this file at startup and applies the settings.

Here are some common properties:

```properties
# Change the port
server.port=9090

# Set the context path (adds a prefix to all URLs)
server.servlet.context-path=/api

# Enable/disable the Spring banner
spring.main.banner-mode=off

# Set logging level
logging.level.root=INFO
logging.level.com.example=DEBUG
```

> **Tip:** You can also use `application.yml` instead of `application.properties`. YAML is another format that uses indentation instead of dots. Both work. We use `.properties` in this book because it is simpler.

```
+--------------------------------------------------+
|     application.properties vs application.yml    |
+--------------------------------------------------+
|                                                   |
|  Properties format:                               |
|    server.port=8080                               |
|    spring.application.name=hello                  |
|                                                   |
|  YAML format:                                     |
|    server:                                        |
|      port: 8080                                   |
|    spring:                                        |
|      application:                                 |
|        name: hello                                |
|                                                   |
|  Both are equivalent. Pick one style.             |
|                                                   |
+--------------------------------------------------+
```

### static/ Folder

The `static` folder holds files that are served directly to the browser without processing. These are:

- **CSS files** -- stylesheets for web pages
- **JavaScript files** -- client-side scripts
- **Images** -- logos, icons, photos
- **HTML files** -- static web pages

If you put a file called `logo.png` in `src/main/resources/static/`, you can access it at `http://localhost:8080/logo.png`.

```
src/main/resources/static/
├── css/
│   └── style.css          --> http://localhost:8080/css/style.css
├── js/
│   └── app.js             --> http://localhost:8080/js/app.js
└── images/
    └── logo.png           --> http://localhost:8080/images/logo.png
```

### templates/ Folder

The `templates` folder holds server-side HTML templates. These templates are processed by a template engine (like Thymeleaf) before being sent to the browser.

The difference between `static` and `templates`:

- **static:** Files are served as-is. No processing.
- **templates:** Files are processed. You can insert dynamic data (like the current user's name) into the HTML.

We will not use templates in this book. We focus on building REST APIs that return JSON, not HTML pages.

---

## 4.5 The src/test Directory

```
src/test/
└── java/
    └── com/
        └── example/
            └── hellospringboot/
                └── HelloSpringBootApplicationTests.java
```

This directory mirrors the `src/main/java` structure. It holds your test classes. The generated test class looks like this:

```java
package com.example.hellospringboot;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest                                       // 1
class HelloSpringBootApplicationTests {

    @Test                                              // 2
    void contextLoads() {                              // 3
    }
}
```

- **Line 1:** `@SpringBootTest` -- This annotation tells JUnit to start the full Spring Boot application before running the tests. It tests that the application starts without errors.

- **Line 2:** `@Test` -- This marks a method as a test case. JUnit will run this method when you run tests.

- **Line 3:** `contextLoads()` -- This test has an empty body. It passes if the application context loads without throwing an exception. It is a smoke test that verifies your configuration is correct.

Run the tests with:

```bash
./mvnw test
```

Expected output:

```
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

---

## 4.6 The Maven Wrapper (mvnw)

You will notice two files in the root: `mvnw` and `mvnw.cmd`.

```
hello-spring-boot/
├── mvnw          (Mac/Linux)
├── mvnw.cmd      (Windows)
└── .mvn/
    └── wrapper/
        └── maven-wrapper.properties
```

**What is the Maven Wrapper?**

The Maven Wrapper is a small script that downloads and uses a specific version of Maven. This way, every developer on a team uses the same Maven version, even if they have different versions installed globally.

Think of it as a portable toolbox. Instead of saying "make sure you have wrench size 12," the Wrapper includes its own wrench.

**Why does it matter?**

- **Consistency:** Everyone uses the same Maven version.
- **No installation required:** A new developer can clone the project and build it immediately, without installing Maven first.
- **Version control:** The Maven version is defined in `maven-wrapper.properties`.

**How to use it:**

Instead of `mvn`, use `./mvnw` (Mac/Linux) or `mvnw.cmd` (Windows):

```bash
# Instead of:
mvn spring-boot:run

# Use:
./mvnw spring-boot:run
```

```
+--------------------------------------------------+
|     mvn vs ./mvnw                                |
+--------------------------------------------------+
|                                                   |
|   mvn                                             |
|     Uses the globally installed Maven.            |
|     Version depends on what you installed.        |
|                                                   |
|   ./mvnw                                          |
|     Uses the Maven version defined in the         |
|     project. Downloads it if needed.              |
|     Guarantees the same version for everyone.     |
|                                                   |
+--------------------------------------------------+
```

---

## 4.7 The target/ Directory

The `target` folder does not exist when you first create the project. Maven creates it when you build the project.

```bash
./mvnw package
```

After building:

```
target/
├── classes/                      Compiled .class files
│   └── com/
│       └── example/
│           └── hellospringboot/
│               ├── HelloSpringBootApplication.class
│               └── HelloController.class
├── test-classes/                 Compiled test .class files
├── hello-spring-boot-0.0.1-SNAPSHOT.jar   The executable JAR
└── ...                           Other build artifacts
```

**Important:** Never edit files in `target/`. They are generated. Maven deletes and recreates this folder every time you build. Any changes you make will be lost.

To clean the `target` folder:

```bash
./mvnw clean
```

---

## 4.8 The .gitignore File

Git is a version control system. It tracks changes to your code. The `.gitignore` file tells Git which files to **not** track.

The generated `.gitignore` typically contains:

```
HELP.md
target/
!.mvn/wrapper/maven-wrapper.jar
!**/src/main/**/target/
!**/src/test/**/target/

### IntelliJ IDEA ###
.idea
*.iws
*.iml
*.ipr

### VS Code ###
.vscode/
```

**Why ignore these files?**

- `target/` -- Generated files. Every developer can recreate them by running `mvn package`.
- `.idea/`, `.vscode/` -- IDE-specific settings. Each developer's IDE settings are personal.
- `*.iml` -- IntelliJ module files. Generated by the IDE.

**Rule of thumb:** Track source code and configuration. Ignore generated files and IDE settings.

---

## 4.9 Understanding Starter Dependencies

In the `pom.xml`, you added `spring-boot-starter-web`. But what is a "starter"?

A **starter** is a bundle of related libraries. Instead of listing 10 individual libraries, you add one starter that includes all of them.

Think of it as ordering a combo meal at a restaurant. Instead of ordering a burger, fries, a drink, and a napkin separately, you say "Combo #1" and get everything.

```
+------------------------------------------------------+
|       What spring-boot-starter-web Includes          |
+------------------------------------------------------+
|                                                       |
|   spring-boot-starter-web                             |
|     |                                                 |
|     ├── spring-web                                    |
|     │     (core web support)                          |
|     │                                                 |
|     ├── spring-webmvc                                 |
|     │     (@Controller, @GetMapping, etc.)            |
|     │                                                 |
|     ├── spring-boot-starter-tomcat                    |
|     │     (embedded Tomcat web server)                |
|     │                                                 |
|     ├── spring-boot-starter-json                      |
|     │     (Jackson for JSON processing)               |
|     │                                                 |
|     └── spring-boot-starter                           |
|           (core Spring Boot + logging + YAML)         |
|                                                       |
+------------------------------------------------------+
```

Here are some common starters:

| Starter                          | What It Provides                        |
|----------------------------------|-----------------------------------------|
| `spring-boot-starter-web`        | Web application + embedded Tomcat       |
| `spring-boot-starter-data-jpa`   | Database access with JPA/Hibernate      |
| `spring-boot-starter-test`       | JUnit, Mockito, and testing utilities   |
| `spring-boot-starter-security`   | Authentication and authorization        |
| `spring-boot-starter-validation` | Bean validation (@NotNull, @Size, etc.) |
| `spring-boot-starter-actuator`   | Health checks and monitoring endpoints  |

You never need to memorize versions. The parent POM manages them all. Just add the starter. Maven handles the rest.

---

## Common Mistakes

1. **Editing files in the `target/` directory.** These files are generated. Maven deletes them on every clean build. Always edit files in `src/`.
2. **Putting Java classes outside the base package.** If your main class is in `com.example.hellospringboot`, all other classes must be in the same package or a sub-package.
3. **Putting configuration files in `src/main/java`.** Configuration files like `application.properties` go in `src/main/resources`. Java files go in `src/main/java`.
4. **Adding version numbers to starter dependencies.** The parent POM manages versions. Adding your own version can cause conflicts.
5. **Committing the `target/` folder to Git.** Always add `target/` to `.gitignore`. It wastes space and causes merge conflicts.

---

## Best Practices

1. **Follow the standard directory layout.** Put Java code in `src/main/java`, resources in `src/main/resources`, tests in `src/test/java`. Maven expects this structure.
2. **Organize code into sub-packages.** Use `controller`, `service`, `repository`, and `model` packages to separate concerns.
3. **Use `application.properties` for configuration.** Do not hard-code values like port numbers or database URLs in Java code.
4. **Use the Maven Wrapper (`mvnw`).** It ensures consistent builds across different machines.
5. **Keep `pom.xml` clean.** Only add dependencies you actually use. Remove unused ones regularly.

---

## Quick Summary

A Spring Boot project has a well-defined structure:

- **`pom.xml`** is the project blueprint. It lists dependencies, Java version, and build settings.
- **`src/main/java`** holds your Java source code, organized in packages.
- **`src/main/resources`** holds configuration files (`application.properties`), static files, and templates.
- **`src/test`** holds test classes that mirror the main source structure.
- **`mvnw`** is the Maven Wrapper. It ensures everyone uses the same Maven version.
- **`target/`** is the build output directory. Never edit files here.
- **Starters** are bundles of related libraries. They simplify dependency management.

---

## Key Points

- `pom.xml` is the most important file. It controls what Maven downloads and how it builds the project.
- The `<parent>` section inherits settings from `spring-boot-starter-parent`, including dependency versions.
- `src/main/java` is for Java code. `src/main/resources` is for configuration and static files.
- `application.properties` controls application behavior (port, logging, database, etc.).
- The `static/` folder serves files directly. The `templates/` folder uses a template engine.
- Starters are dependency bundles. `spring-boot-starter-web` includes Tomcat, Spring MVC, and Jackson.
- The Maven Wrapper (`mvnw`) guarantees consistent builds without requiring Maven installation.
- Never commit `target/` to version control.

---

## Practice Questions

1. What is the purpose of `pom.xml`? What happens if you delete it?

2. What is the difference between `src/main/resources/static` and `src/main/resources/templates`?

3. Why does the `spring-boot-starter-web` dependency in `pom.xml` not have a `<version>` tag?

4. You put a file called `style.css` in `src/main/resources/static/css/`. What URL would you use to access it in the browser?

5. What is the Maven Wrapper and why should you use `./mvnw` instead of `mvn`?

---

## Exercises

### Exercise 1: Explore Your Project

Open your project in a file explorer (not the IDE). Navigate through every folder. For each folder and file, write down its purpose in one sentence. Compare your notes with the descriptions in this chapter.

### Exercise 2: Add a Static File

Create a file called `src/main/resources/static/hello.html` with this content:

```html
<!DOCTYPE html>
<html>
<head><title>Hello</title></head>
<body><h1>Hello from a static file!</h1></body>
</html>
```

Start the application and visit `http://localhost:8080/hello.html`. You should see the HTML page. Notice that no controller was needed. Static files are served automatically.

### Exercise 3: Read the Dependency Tree

Run this command in your project folder:

```bash
./mvnw dependency:tree
```

This shows all libraries your project uses, including ones pulled in by the starters. Look at the output. Count how many libraries `spring-boot-starter-web` brings in. Write down three libraries you recognize.

---

## What Is Next?

Now you know where everything lives in a Spring Boot project. But how does Spring Boot know which libraries to configure automatically? How does it know to start Tomcat without you writing any server code? In the next chapter, we will uncover the magic of auto-configuration.
