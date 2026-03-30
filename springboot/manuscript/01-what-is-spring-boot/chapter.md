# Chapter 1: What Is Spring Boot?

## What You Will Learn

- What the Spring Framework is and why it exists.
- What Spring Boot is and how it improves Spring.
- The history of Spring and Spring Boot.
- How Spring Boot removes boilerplate code.
- What "convention over configuration" means.
- How plain Java, Spring, and Spring Boot compare for building web apps.
- The Spring ecosystem and its major projects.
- Real companies that use Spring Boot in production.

## Why This Chapter Matters

Imagine you want to build a house. You could start by making your own bricks, mixing your own cement, and cutting your own wood. That would take forever. Or you could buy ready-made materials and focus on designing your dream home.

Spring Boot is like buying ready-made materials. It lets you focus on building your application instead of wasting time on setup and configuration. Before you write a single line of Spring Boot code, you need to understand what it is, where it came from, and why millions of developers choose it every day.

This chapter gives you that foundation. By the end, you will understand what Spring Boot does for you and why it has become the most popular way to build Java applications.

---

## 1.1 The Problem: Building Java Web Apps Is Hard

Let us start with a simple question. What does it take to build a web application in plain Java?

Here is what you need to do:

1. Write Java code for your business logic.
2. Set up a web server (like Apache Tomcat).
3. Write XML configuration files.
4. Configure database connections manually.
5. Handle security settings.
6. Package everything into a WAR file.
7. Deploy the WAR file to the server.

That is a lot of work before you can even say "Hello, World!" to a user.

Think of it like cooking a meal from scratch. You need to grow the vegetables, raise the chicken, mill the flour, and churn the butter. By the time you start cooking, you are already exhausted.

There had to be a better way. And there was.

---

## 1.2 What Is the Spring Framework?

The **Spring Framework** is a toolkit for building Java applications. It was created in 2003 by Rod Johnson.

> **Toolkit**: A collection of pre-built tools and libraries that help you do common tasks without writing everything from scratch.

Think of Spring as a well-organized toolbox. Need to connect to a database? There is a tool for that. Need to handle web requests? There is a tool for that too. Need to send emails? Yep, there is a tool for that as well.

Spring solves several big problems:

| Problem | Spring's Solution |
|---|---|
| Objects depend on each other in messy ways | Dependency Injection (DI) |
| Database code is repetitive and error-prone | Spring Data |
| Handling web requests requires lots of setup | Spring MVC |
| Security is complex to implement | Spring Security |
| Configuration files are long and confusing | Annotation-based configuration |

### What "Framework" Means

A **framework** is a structure that your code fits into. You follow the framework's rules, and it handles the boring parts for you.

Think of a framework like a form you fill out at the doctor's office. The form gives you the structure (name here, date of birth there). You just fill in your specific information. The framework handles the layout and organization.

### Spring's Core Idea: Dependency Injection

We will cover this in detail in Chapter 6. For now, here is the simple version.

In plain Java, if class A needs class B, class A creates class B itself:

```java
public class OrderService {
    // OrderService creates its own EmailService
    private EmailService emailService = new EmailService();
}
```

With Spring, you say "I need an EmailService" and Spring gives you one:

```java
public class OrderService {
    private final EmailService emailService;

    // Spring gives OrderService an EmailService automatically
    public OrderService(EmailService emailService) {
        this.emailService = emailService;
    }
}
```

This might seem like a small change. But it makes your code much easier to test, change, and maintain. More on this in Chapter 6.

---

## 1.3 The Problem with Spring: Too Much Configuration

Spring was a huge improvement over plain Java. But Spring had its own problem: **configuration overload**.

To build a simple web application with Spring, you needed to:

1. Create a `web.xml` file to configure the web layer.
2. Create Spring XML configuration files to define your beans.
3. Configure a database connection in another XML file.
4. Set up a view resolver for web pages.
5. Download and install a separate web server.
6. Package your app as a WAR file and deploy it.

Here is a taste of what Spring XML configuration looked like:

```xml
<!-- Spring XML configuration — you needed files like this -->
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans.xsd">

    <bean id="dataSource" class="org.apache.commons.dbcp2.BasicDataSource">
        <property name="driverClassName" value="com.mysql.cj.jdbc.Driver"/>
        <property name="url" value="jdbc:mysql://localhost:3306/mydb"/>
        <property name="username" value="root"/>
        <property name="password" value="password"/>
    </bean>

    <bean id="sessionFactory"
          class="org.springframework.orm.hibernate5.LocalSessionFactoryBean">
        <property name="dataSource" ref="dataSource"/>
        <property name="packagesToScan" value="com.example.model"/>
        <property name="hibernateProperties">
            <props>
                <prop key="hibernate.dialect">
                    org.hibernate.dialect.MySQLDialect
                </prop>
                <prop key="hibernate.show_sql">true</prop>
            </props>
        </property>
    </bean>
</beans>
```

That is a lot of XML just to connect to a database. And this is only one piece of the puzzle.

Developers joked that Spring stood for "Still Programming, Really? I Need to write more XML? No way, Give me something Simpler!"

Something simpler did come along.

---

## 1.4 Enter Spring Boot

**Spring Boot** was released in 2014. It was created by Pivotal (now part of VMware/Broadcom). The goal was simple: make it easy to create Spring applications with minimal setup.

> **Spring Boot**: A project built on top of Spring Framework that provides auto-configuration, embedded servers, and opinionated defaults so you can start building applications quickly.

Spring Boot did not replace Spring. It sits on top of Spring and does the configuration work for you.

Think of it this way:

- **Plain Java** = Building a house from raw materials.
- **Spring Framework** = Building a house from pre-made parts. You still need to read the blueprints and assemble everything.
- **Spring Boot** = Moving into a pre-built house. The walls, plumbing, and electricity are already done. You just decorate and arrange the furniture.

### What Spring Boot Gives You

Spring Boot provides four key features:

1. **Auto-Configuration**: Spring Boot looks at your project dependencies and configures things automatically. Added a database driver? Spring Boot sets up the connection for you.

2. **Embedded Server**: No need to install Tomcat separately. Spring Boot includes a web server inside your application. Just run your app and the server starts.

3. **Starter Dependencies**: Instead of adding 10 individual libraries, you add one "starter" that includes everything you need.

4. **Production-Ready Features**: Health checks, metrics, and monitoring built in.

---

## 1.5 A Brief History

Here is how we got from plain Java to Spring Boot:

```
+------+    +--------+    +----------+    +-------------+
| 1995 |    |  2003  |    |   2014   |    |    Today    |
| Java |--->| Spring |--->| Spring   |--->| Spring Boot |
| Born |    | 1.0    |    | Boot 1.0 |    | 3.4+        |
+------+    +--------+    +----------+    +-------------+
   |            |              |                |
   v            v              v                v
 Write      Less code,     Minimal         Fastest way
 everything  but lots      config,          to build
 yourself    of XML        embedded         production
                           server           Java apps
```

**Key Milestones:**

| Year | Event |
|---|---|
| 1995 | Java released by Sun Microsystems |
| 2003 | Spring Framework 1.0 released |
| 2004 | Spring 1.1 adds AOP (Aspect-Oriented Programming) |
| 2009 | Spring 3.0 adds Java-based configuration (less XML) |
| 2013 | Spring 4.0 adds Java 8 support |
| 2014 | Spring Boot 1.0 released |
| 2018 | Spring Boot 2.0 with Spring Framework 5 |
| 2022 | Spring Boot 3.0 with Spring Framework 6 and Java 17 baseline |
| 2024 | Spring Boot 3.4 with improved auto-configuration and virtual threads support |

---

## 1.6 Comparison: Plain Java vs Spring vs Spring Boot

Let us build a simple web endpoint that returns "Hello, World!" in three different ways. This comparison will show you why Spring Boot is so popular.

### Approach 1: Plain Java (Using Servlets)

```java
// File: HelloServlet.java
// Plain Java approach — lots of boilerplate

import jakarta.servlet.http.HttpServlet;            // Line 1
import jakarta.servlet.http.HttpServletRequest;      // Line 2
import jakarta.servlet.http.HttpServletResponse;     // Line 3
import jakarta.servlet.annotation.WebServlet;        // Line 4
import java.io.IOException;                          // Line 5

@WebServlet("/hello")                                // Line 6
public class HelloServlet extends HttpServlet {      // Line 7

    @Override                                         // Line 8
    protected void doGet(HttpServletRequest request,  // Line 9
                         HttpServletResponse response) // Line 10
            throws IOException {                      // Line 11
        response.setContentType("text/plain");        // Line 12
        response.getWriter().write("Hello, World!");  // Line 13
    }                                                 // Line 14
}                                                     // Line 15
```

**Line-by-line explanation:**

- **Lines 1-5**: Import statements. You need to import servlet classes manually.
- **Line 6**: `@WebServlet("/hello")` maps this servlet to the `/hello` URL path.
- **Line 7**: Your class must extend `HttpServlet`. This is required.
- **Lines 8-11**: You override the `doGet` method to handle HTTP GET requests.
- **Line 12**: You manually set the response content type.
- **Line 13**: You manually write the response body.

**But wait, there is more!** You also need:

- A `web.xml` configuration file.
- An external Tomcat server installed and configured.
- A WAR file packaging step.
- Deployment to the Tomcat server.

That is a lot of work for "Hello, World!"

### Approach 2: Spring Framework (Without Boot)

```java
// File: HelloController.java
// Spring MVC approach — better, but still needs setup

import org.springframework.stereotype.Controller;        // Line 1
import org.springframework.web.bind.annotation.GetMapping; // Line 2
import org.springframework.web.bind.annotation.ResponseBody; // Line 3

@Controller                                               // Line 4
public class HelloController {                            // Line 5

    @GetMapping("/hello")                                 // Line 6
    @ResponseBody                                         // Line 7
    public String hello() {                               // Line 8
        return "Hello, World!";                           // Line 9
    }                                                     // Line 10
}                                                         // Line 11
```

**Line-by-line explanation:**

- **Line 1**: `@Controller` tells Spring this class handles web requests.
- **Line 6**: `@GetMapping("/hello")` maps GET requests to `/hello`.
- **Line 7**: `@ResponseBody` tells Spring to return the string directly (not a web page name).
- **Lines 8-9**: A simple method that returns "Hello, World!"

This is cleaner code. But you still need:

- Multiple XML configuration files.
- An external Tomcat server.
- Careful dependency management.
- A WAR file and deployment process.

### Approach 3: Spring Boot

```java
// File: HelloController.java
// Spring Boot approach — clean and simple

import org.springframework.web.bind.annotation.GetMapping;   // Line 1
import org.springframework.web.bind.annotation.RestController; // Line 2

@RestController                                               // Line 3
public class HelloController {                                // Line 4

    @GetMapping("/hello")                                     // Line 5
    public String hello() {                                   // Line 6
        return "Hello, World!";                               // Line 7
    }                                                         // Line 8
}                                                             // Line 9
```

**Line-by-line explanation:**

- **Line 2**: `@RestController` combines `@Controller` and `@ResponseBody`. One annotation instead of two.
- **Line 5**: `@GetMapping("/hello")` maps GET requests to `/hello`.
- **Lines 6-7**: Return "Hello, World!" That is it.

**And the main application class:**

```java
// File: Application.java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

No XML. No external server. No WAR file. Just run the `main` method and your web app is live.

### The Comparison at a Glance

```
+---------------------+------------+--------+-------------+
|                     | Plain Java | Spring | Spring Boot |
+---------------------+------------+--------+-------------+
| XML config files    | Yes        | Yes    | No          |
| External server     | Yes        | Yes    | No          |
| Lines of setup code | 50+        | 30+    | ~5          |
| Time to "Hello"     | 30+ min    | 15 min | 2 min       |
| Dependency mgmt     | Manual     | Manual | Auto        |
+---------------------+------------+--------+-------------+
```

---

## 1.7 Convention Over Configuration

You will hear this phrase a lot in the Spring Boot world:

> **Convention over configuration**: The framework makes smart default choices for you. You only need to change settings when you want something different from the default.

Here is an analogy. When you check into a hotel room, you expect:

- A bed with clean sheets.
- A bathroom with hot water.
- Wi-Fi that works.
- A TV with basic channels.

You did not have to ask for any of that. It is the convention. The hotel assumed you would want these things.

But if you want extra pillows or a room with a view, you can request that. You configure only what you want to change.

Spring Boot works the same way:

| Convention (Default) | You Can Configure |
|---|---|
| Embedded Tomcat server on port 8080 | Change to port 9090 in `application.properties` |
| H2 in-memory database if H2 is on classpath | Switch to MySQL or PostgreSQL |
| `/static` folder serves static files | Change the static file location |
| `application.properties` for settings | Use `application.yml` instead |

To change the default port, you only need one line:

```properties
# File: application.properties
server.port=9090
```

That is it. No XML. No Java configuration class. One line.

---

## 1.8 The Spring Ecosystem

Spring Boot is part of a larger family of projects called the **Spring ecosystem**. Here is how they fit together:

```
+----------------------------------------------------------+
|                   SPRING ECOSYSTEM                       |
|                                                          |
|  +---------------------------------------------------+  |
|  |              SPRING BOOT                           |  |
|  |  (Auto-config, embedded server, starters)          |  |
|  |                                                    |  |
|  |  +----------------------------------------------+ |  |
|  |  |           SPRING FRAMEWORK                   | |  |
|  |  |  (Core, MVC, Data Access, AOP)               | |  |
|  |  +----------------------------------------------+ |  |
|  +---------------------------------------------------+  |
|                                                          |
|  OTHER SPRING PROJECTS:                                  |
|  +----------------+  +----------------+                  |
|  | Spring Data    |  | Spring Security|                  |
|  | (Database      |  | (Login, roles, |                  |
|  |  access)       |  |  permissions)  |                  |
|  +----------------+  +----------------+                  |
|  +----------------+  +----------------+                  |
|  | Spring Cloud   |  | Spring Batch   |                  |
|  | (Microservices,|  | (Process large |                  |
|  |  distributed)  |  |  data sets)    |                  |
|  +----------------+  +----------------+                  |
|  +----------------+  +----------------+                  |
|  | Spring AMQP    |  | Spring GraphQL |                  |
|  | (Message       |  | (GraphQL API   |                  |
|  |  queues)       |  |  support)      |                  |
|  +----------------+  +----------------+                  |
+----------------------------------------------------------+
```

**Key Spring Projects Explained:**

- **Spring Framework**: The foundation. Provides core features like dependency injection and web support.
- **Spring Boot**: Sits on top of Spring Framework. Adds auto-configuration and embedded servers.
- **Spring Data**: Makes database access easy. Write less code to talk to databases.
- **Spring Security**: Handles login, passwords, roles, and permissions.
- **Spring Cloud**: Tools for building microservices (small, independent services that work together).
- **Spring Batch**: Processes large amounts of data in batches (like reading a million records from a file).

You do not need to learn all of these right now. In this book, we focus on Spring Boot with Spring Web and Spring Data.

---

## 1.9 Who Uses Spring Boot?

Spring Boot is not just a learning tool. It powers some of the biggest applications in the world:

| Company | How They Use Spring Boot |
|---|---|
| **Netflix** | Runs backend microservices that serve millions of users |
| **Amazon** | Uses Spring Boot for internal tools and services |
| **LinkedIn** | Powers parts of their professional networking platform |
| **Alibaba** | Runs e-commerce backend services |
| **JPMorgan Chase** | Builds financial applications and trading platforms |
| **Uber** | Uses it for backend microservices |

According to developer surveys, Spring Boot is consistently the most popular Java framework. It has millions of downloads every month.

**Why do companies choose Spring Boot?**

1. **Fast development**: Less setup means faster time to market.
2. **Large talent pool**: Many Java developers know Spring Boot.
3. **Production-ready**: Built-in monitoring, health checks, and metrics.
4. **Scalable**: Works for small apps and large enterprise systems.
5. **Strong community**: Excellent documentation, tutorials, and Stack Overflow support.

---

## 1.10 What Spring Boot Is NOT

Let us clear up some common misconceptions:

- **Spring Boot is NOT a new language.** It is Java. You write Java code.
- **Spring Boot is NOT a replacement for Spring.** It uses Spring underneath. It just makes Spring easier to use.
- **Spring Boot is NOT only for web apps.** You can build command-line tools, batch processors, messaging apps, and more.
- **Spring Boot is NOT magic.** It has sensible defaults, but you can change everything. Understanding what it does under the hood (which this book will teach you) makes you a better developer.

---

## Common Mistakes

1. **Confusing Spring and Spring Boot.** Spring is the framework. Spring Boot is the tool that makes Spring easier to use. Spring Boot uses Spring internally.

2. **Thinking Spring Boot is only for microservices.** Spring Boot works great for monolithic applications too. You can build any type of Java application with it.

3. **Skipping the fundamentals.** Do not jump into Spring Boot without understanding basic Java concepts like classes, objects, interfaces, and inheritance.

4. **Thinking you need to learn all Spring projects at once.** Start with Spring Boot and Spring Web. Add more as you need them.

---

## Best Practices

1. **Learn Java basics first.** You should be comfortable with classes, objects, methods, interfaces, and collections before starting Spring Boot.

2. **Start with the latest stable version.** This book uses Spring Boot 3.4+. Avoid older versions when starting fresh.

3. **Use Java 17 or later.** Spring Boot 3.x requires Java 17 as the minimum version. Java 17 is a Long-Term Support (LTS) release.

4. **Read the official documentation.** The Spring Boot documentation at `docs.spring.io` is excellent and well-organized.

5. **Build projects, do not just read.** The best way to learn is by typing the code yourself and running it.

---

## Quick Summary

Spring Boot is a tool built on top of the Spring Framework. It removes the tedious configuration work and lets you build Java applications quickly. It provides auto-configuration (smart defaults), an embedded web server (no separate installation needed), and starter dependencies (one dependency instead of many). Spring Boot follows the principle of "convention over configuration" which means it makes sensible choices for you and you only change what you need to. It was released in 2014 and has become the most popular way to build Java applications. Companies like Netflix, Amazon, and LinkedIn use it in production.

---

## Key Points

- Spring Framework (2003) is a toolkit for building Java applications.
- Spring Boot (2014) sits on top of Spring and provides auto-configuration.
- Spring Boot includes an embedded web server. No external Tomcat needed.
- "Convention over configuration" means smart defaults with easy overrides.
- Spring Boot requires Java 17+ (starting from Spring Boot 3.0).
- The Spring ecosystem includes many projects: Data, Security, Cloud, and more.
- Spring Boot is used by major companies in production systems.

---

## Practice Questions

1. What is the main difference between Spring Framework and Spring Boot?

2. Name three things that Spring Boot provides that plain Spring does not.

3. What does "convention over configuration" mean? Give an example.

4. Why does Spring Boot 3.x require Java 17 as a minimum?

5. A colleague says "Spring Boot is only for building microservices." Is this correct? Explain your answer.

---

## Exercises

### Exercise 1: Research Spring Boot Versions

Visit the Spring Boot releases page at `https://github.com/spring-projects/spring-boot/releases`. Find the latest stable version. Write down:
- The version number.
- The release date.
- One new feature mentioned in the release notes.

### Exercise 2: Identify the Spring Projects

Go to `https://spring.io/projects`. List five Spring projects and write one sentence about what each one does. Which ones do you think you will use most often?

### Exercise 3: Compare Frameworks

Research one alternative to Spring Boot (such as Quarkus, Micronaut, or Jakarta EE). Write three similarities and three differences between it and Spring Boot.

---

## What Is Next?

Now that you understand what Spring Boot is and why it matters, it is time to set up your development environment. In Chapter 2, you will install Java, an IDE, and Maven. By the end of that chapter, you will have all the tools you need to start building Spring Boot applications.
