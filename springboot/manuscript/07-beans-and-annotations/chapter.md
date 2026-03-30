# Chapter 7: Beans and Annotations

## What You Will Learn

In this chapter, you will learn:

- What a Spring Bean is and why it matters
- How Spring creates and manages objects for you
- The difference between `@Component`, `@Service`, `@Repository`, and `@Controller`
- How to choose the right annotation with a simple flowchart
- The difference between singleton and prototype beans
- How to create beans using `@Bean` in a `@Configuration` class
- The lifecycle of a Spring Bean from birth to death
- How component scanning finds your beans automatically

## Why This Chapter Matters

Imagine you run a company. You have employees on your payroll. You do not go to the street every morning to find random people to do work. Instead, you hire employees once. They are on your payroll. You know their names. You assign them tasks. They show up when needed.

Spring Boot works the same way. The objects in your application are like employees. Spring keeps them on its "payroll." These managed objects are called **beans**. Spring creates them, tracks them, and hands them out when other parts of your code need them.

Without beans, you would create objects manually everywhere. You would lose track of them. You would create duplicates. Your code would become messy. Beans solve all of these problems.

This chapter is the foundation of everything in Spring. Every feature you will learn after this -- REST controllers, data access, security -- they all depend on beans. Master this chapter, and the rest of Spring will make sense.

---

## 7.1 What Is a Spring Bean?

A **bean** is simply a Java object that Spring creates and manages for you.

Think of it this way:

- A regular Java object is like a freelancer. You create it yourself. You manage it yourself. When you are done, you throw it away.
- A Spring Bean is like a full-time employee. Spring hires it. Spring manages it. Spring makes it available to anyone who needs it.

Here is a regular Java object:

```java
// You create it yourself
NotificationService service = new NotificationService();
service.sendEmail("hello@example.com", "Welcome!");
```

Here is a Spring Bean:

```java
// Spring creates it and gives it to you
@Autowired
private NotificationService service;

// You just use it
service.sendEmail("hello@example.com", "Welcome!");
```

The difference is who creates the object. With regular Java, you do it. With Spring, the framework does it.

### The Spring Container

Spring keeps all its beans in a special place called the **Application Context**. Think of it as an employee directory. When any part of your code needs a bean, Spring looks it up in this directory and hands it over.

```
+--------------------------------------------------+
|           Spring Application Context              |
|              (Employee Directory)                  |
|                                                    |
|  +----------------+  +-------------------+        |
|  | UserService    |  | EmailService      |        |
|  | (Bean)         |  | (Bean)            |        |
|  +----------------+  +-------------------+        |
|                                                    |
|  +----------------+  +-------------------+        |
|  | UserRepository |  | OrderController   |        |
|  | (Bean)         |  | (Bean)            |        |
|  +----------------+  +-------------------+        |
|                                                    |
+--------------------------------------------------+
```

**Application Context** is the container that holds all your beans. It is like a big box where Spring puts every object it creates. When your code needs an object, Spring reaches into this box and pulls out the right one.

---

## 7.2 The @Component Annotation

The simplest way to tell Spring "please manage this object" is the `@Component` annotation.

**Annotation** means a special label you put on your Java class. It starts with the `@` symbol. It gives Spring extra information about your class.

```java
package com.example.demo.util;

import org.springframework.stereotype.Component;

@Component  // "Hey Spring, please manage this class!"
public class GreetingGenerator {

    public String generateGreeting(String name) {
        return "Hello, " + name + "! Welcome aboard!";
    }
}
```

**Line-by-line explanation:**

- `@Component` -- This annotation tells Spring: "Create an object from this class and keep it in your container." Without this annotation, Spring ignores the class completely.
- `public class GreetingGenerator` -- A regular Java class. Nothing special about it.
- `public String generateGreeting(String name)` -- A regular method. It takes a name and returns a greeting message.

When your application starts, Spring sees the `@Component` annotation. It creates one instance of `GreetingGenerator`. It stores that instance in the Application Context. Now any other bean can use it.

### Using a Component Bean

```java
package com.example.demo.service;

import com.example.demo.util.GreetingGenerator;
import org.springframework.stereotype.Service;

@Service
public class WelcomeService {

    private final GreetingGenerator greetingGenerator;

    // Spring automatically provides the GreetingGenerator bean here
    public WelcomeService(GreetingGenerator greetingGenerator) {
        this.greetingGenerator = greetingGenerator;
    }

    public String welcomeUser(String username) {
        return greetingGenerator.generateGreeting(username);
    }
}
```

**Line-by-line explanation:**

- `@Service` -- Another annotation similar to `@Component`. We will explain the difference shortly.
- `private final GreetingGenerator greetingGenerator;` -- A field to hold the `GreetingGenerator` bean. The `final` keyword means it cannot change after being set.
- `public WelcomeService(GreetingGenerator greetingGenerator)` -- This is **constructor injection**. Spring sees that this constructor needs a `GreetingGenerator`. It looks in the Application Context, finds one, and passes it in automatically.
- `greetingGenerator.generateGreeting(username)` -- We use the bean just like a normal object.

**Constructor injection** means Spring provides the required beans through the constructor of your class. This is the recommended way to get beans in Spring.

---

## 7.3 Stereotype Annotations: @Service, @Repository, @Controller

Spring gives you four annotations to mark your beans. They all do the same basic thing: they tell Spring to manage the class. But each one has a specific meaning.

| Annotation      | Purpose                        | Real-Life Analogy            |
|-----------------|--------------------------------|------------------------------|
| `@Component`    | Generic bean, no specific role | General employee             |
| `@Service`      | Business logic                 | Manager who makes decisions  |
| `@Repository`   | Database access                | Filing clerk in the archive  |
| `@Controller`   | Handles web requests           | Receptionist at the front desk |

### @Component -- The Generic Worker

Use `@Component` when your class does not fit into service, repository, or controller categories.

```java
@Component
public class PdfGenerator {
    public byte[] generateReport(String title, String content) {
        // Logic to create a PDF document
        return new byte[0]; // Simplified
    }
}
```

A `PdfGenerator` is not business logic. It is not database access. It is not a web controller. It is a utility. So `@Component` is the right choice.

### @Service -- The Business Brain

Use `@Service` for classes that contain your business logic. Business logic means the rules and decisions your application makes.

```java
package com.example.demo.service;

import org.springframework.stereotype.Service;

@Service
public class PricingService {

    private static final double TAX_RATE = 0.08;

    public double calculateTotal(double price, int quantity) {
        double subtotal = price * quantity;
        double tax = subtotal * TAX_RATE;
        return subtotal + tax;
    }

    public double applyDiscount(double total, double discountPercent) {
        return total * (1 - discountPercent / 100);
    }
}
```

This class makes business decisions. "What is the total price?" and "How much discount to apply?" are business questions. So we use `@Service`.

### @Repository -- The Data Keeper

Use `@Repository` for classes that talk to the database. Spring gives `@Repository` a special power: it automatically translates database errors into Spring exceptions.

```java
package com.example.demo.repository;

import com.example.demo.model.Product;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Repository
public class ProductRepository {

    private final List<Product> products = new ArrayList<>();
    private long nextId = 1;

    public Product save(Product product) {
        product.setId(nextId++);
        products.add(product);
        return product;
    }

    public Optional<Product> findById(Long id) {
        return products.stream()
                .filter(p -> p.getId().equals(id))
                .findFirst();
    }

    public List<Product> findAll() {
        return new ArrayList<>(products);
    }
}
```

**Optional** is a Java class that may or may not contain a value. It helps you avoid `NullPointerException`. Instead of returning `null` when a product is not found, you return an empty `Optional`.

### @Controller -- The Front Desk

Use `@Controller` (or `@RestController`) for classes that handle web requests. We will cover this in detail in Chapter 9.

```java
package com.example.demo.controller;

import com.example.demo.service.PricingService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PriceController {

    private final PricingService pricingService;

    public PriceController(PricingService pricingService) {
        this.pricingService = pricingService;
    }

    @GetMapping("/price")
    public String getPrice(@RequestParam double price,
                           @RequestParam int quantity) {
        double total = pricingService.calculateTotal(price, quantity);
        return "Total: $" + String.format("%.2f", total);
    }
}
```

### The Truth About These Annotations

Here is a secret. `@Service`, `@Repository`, and `@Controller` are all built on top of `@Component`. They are **specialized versions** of `@Component`.

```
         @Component
        /    |     \
       /     |      \
@Service  @Repository  @Controller
```

If you replaced `@Service` with `@Component`, your code would still work. But using the right annotation makes your code easier to read. When another developer sees `@Service`, they immediately know this class contains business logic. When they see `@Repository`, they know it handles data.

It is like wearing a uniform. A chef and a doctor both work at a hospital cafeteria. But the chef wears a chef hat, and the doctor wears a white coat. You can tell who does what just by looking.

---

## 7.4 Decision Flowchart: Which Annotation to Use?

When you create a new class, follow this flowchart:

```
                    +---------------------------+
                    | Does this class handle     |
                    | HTTP requests?             |
                    +---------------------------+
                           |            |
                          YES           NO
                           |            |
                    +-------------+     |
                    | @Controller |     |
                    | or          |     |
                    | @RestController   |
                    +-------------+     |
                                        |
                    +---------------------------+
                    | Does this class talk to    |
                    | a database or external     |
                    | data source?               |
                    +---------------------------+
                           |            |
                          YES           NO
                           |            |
                    +--------------+    |
                    | @Repository  |    |
                    +--------------+    |
                                        |
                    +---------------------------+
                    | Does this class contain    |
                    | business logic or rules?   |
                    +---------------------------+
                           |            |
                          YES           NO
                           |            |
                    +-----------+  +-----------+
                    | @Service  |  | @Component|
                    +-----------+  +-----------+
```

**Quick rule:** Controller > Repository > Service > Component. Check in that order.

---

## 7.5 Singleton vs Prototype Scope

By default, Spring creates **one** instance of each bean. This is called **singleton scope**. Every time someone asks for that bean, they get the same object.

### Singleton Scope (Default)

**Singleton** means "only one." Spring creates the bean once and reuses it everywhere.

```java
@Service
public class CounterService {

    private int count = 0;

    public int increment() {
        return ++count;
    }

    public int getCount() {
        return count;
    }
}
```

If three different parts of your application use `CounterService`, they all share the same instance. If one part calls `increment()`, the other parts see the updated count.

```
+------------------+
| CounterService   |  <-- Only ONE instance exists
| count = 5       |
+------------------+
      ^   ^   ^
      |   |   |
 ControllerA  |  ControllerC
      ControllerB

All three controllers share the SAME CounterService.
If ControllerA increments, ControllerB sees the change.
```

This is like having one whiteboard in the office. Everyone reads and writes on the same whiteboard.

### Prototype Scope

Sometimes you want a **fresh** object every time. Use the `@Scope` annotation with `prototype`.

**Prototype** means "make a new copy each time." Spring creates a brand new bean every time someone asks for it.

```java
package com.example.demo.model;

import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

@Component
@Scope("prototype")
public class ShoppingCart {

    private final List<String> items = new ArrayList<>();

    public void addItem(String item) {
        items.add(item);
    }

    public List<String> getItems() {
        return new ArrayList<>(items);
    }

    public int getItemCount() {
        return items.size();
    }
}
```

```
Request from User A --> new ShoppingCart (items: [Book])
Request from User B --> new ShoppingCart (items: [Pen, Notebook])
Request from User C --> new ShoppingCart (items: [])

Each user gets their OWN ShoppingCart. They do NOT share.
```

This is like giving each customer their own shopping basket at a store. They do not share baskets.

### When to Use Each Scope

| Scope     | When to Use                                  | Example              |
|-----------|----------------------------------------------|----------------------|
| Singleton | Stateless services, shared logic             | PricingService       |
| Prototype | Stateful objects, per-user/per-request data  | ShoppingCart          |

**Stateless** means the bean does not remember anything between method calls. It processes data and returns a result. It does not store data inside itself.

**Stateful** means the bean remembers data. A shopping cart remembers what items are in it.

> **Rule of thumb:** If your bean has fields that change during use, consider prototype scope. If your bean only has methods that compute and return results, use singleton (the default).

---

## 7.6 Creating Beans with @Bean and @Configuration

Sometimes you cannot add `@Component` to a class. Maybe the class comes from an external library. Maybe you need to configure the object before using it. In these cases, use `@Bean` inside a `@Configuration` class.

**@Configuration** marks a class as a source of bean definitions. Think of it as a recipe book. Each `@Bean` method is one recipe.

**@Bean** marks a method that creates and returns an object. Spring will call this method, take the returned object, and register it as a bean.

### Example: Configuring an External Library

Imagine you use a library class called `ObjectMapper` from the Jackson JSON library. You cannot edit its source code to add `@Component`. So you create a configuration class:

```java
package com.example.demo.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.enable(SerializationFeature.INDENT_OUTPUT);
        return mapper;
    }
}
```

**Line-by-line explanation:**

- `@Configuration` -- Tells Spring: "This class contains bean definitions. Scan it for `@Bean` methods."
- `@Bean` -- Tells Spring: "Call this method at startup. Take the returned object and manage it as a bean."
- `public ObjectMapper objectMapper()` -- The method name (`objectMapper`) becomes the bean name by default.
- `mapper.enable(SerializationFeature.INDENT_OUTPUT)` -- We configure the object before Spring takes it. This is the advantage of `@Bean`. You can customize the object.
- `return mapper` -- Spring takes this returned object and puts it in the Application Context.

### Example: Multiple Beans of the Same Type

You can create multiple beans of the same type. Give them different names.

```java
@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource primaryDataSource() {
        // Configuration for the main database
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:h2:mem:maindb");
        ds.setUsername("sa");
        return ds;
    }

    @Bean
    public DataSource reportingDataSource() {
        // Configuration for the reporting database
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl("jdbc:h2:mem:reportdb");
        ds.setUsername("sa");
        return ds;
    }
}
```

When you have multiple beans of the same type, use `@Qualifier` to tell Spring which one you want:

```java
@Service
public class ReportService {

    private final DataSource dataSource;

    public ReportService(
            @Qualifier("reportingDataSource") DataSource dataSource) {
        this.dataSource = dataSource;
    }
}
```

**@Qualifier** tells Spring: "I do not want just any DataSource. I want the specific one named `reportingDataSource`."

### @Component vs @Bean: When to Use Which

| Feature          | @Component                    | @Bean                           |
|------------------|-------------------------------|---------------------------------|
| Where to use     | On the class itself           | On a method in @Configuration   |
| Best for         | Your own classes              | Third-party library classes     |
| Customization    | Limited                       | Full control over creation      |
| Auto-detected    | Yes, by component scanning    | Yes, through @Configuration     |

---

## 7.7 Bean Lifecycle

Every bean goes through a lifecycle. It is born, it lives, and it dies. Spring gives you hooks to run code at each stage.

```
+-------------+     +-------------+     +-------------+
|  Bean       | --> |  Bean       | --> |  Bean       |
|  Created    |     |  Initialized|     |  Destroyed  |
|             |     |  (Ready)    |     |             |
+-------------+     +-------------+     +-------------+
   |                    |                    |
   |                    |                    |
Constructor        @PostConstruct       @PreDestroy
called             method called        method called
```

### @PostConstruct -- Run Code After Bean Is Created

**@PostConstruct** marks a method that Spring calls right after creating the bean and injecting all its dependencies. Use it for initialization logic.

```java
package com.example.demo.service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class CacheService {

    private static final Logger log =
            LoggerFactory.getLogger(CacheService.class);

    private final Map<String, String> cache = new HashMap<>();

    @PostConstruct
    public void init() {
        log.info("CacheService is starting up...");
        cache.put("app.name", "My Spring App");
        cache.put("app.version", "1.0.0");
        log.info("Cache initialized with {} entries", cache.size());
    }

    public String get(String key) {
        return cache.get(key);
    }

    public void put(String key, String value) {
        cache.put(key, value);
    }

    @PreDestroy
    public void cleanup() {
        log.info("CacheService is shutting down...");
        cache.clear();
        log.info("Cache cleared");
    }
}
```

**Line-by-line explanation:**

- `@PostConstruct` on `init()` -- Spring calls this method after creating the `CacheService` bean. We use it to pre-load some data into the cache.
- `@PreDestroy` on `cleanup()` -- Spring calls this method before destroying the bean (when the application shuts down). We use it to clean up resources.

**Output when the application starts:**

```
CacheService is starting up...
Cache initialized with 2 entries
```

**Output when the application stops:**

```
CacheService is shutting down...
Cache cleared
```

### The Complete Bean Lifecycle

Here is the full lifecycle in order:

```
1. Spring finds the class (component scanning)
2. Spring calls the constructor
3. Spring injects dependencies
4. Spring calls @PostConstruct method
5. Bean is ready to use
6. ... application runs ...
7. Application shutdown begins
8. Spring calls @PreDestroy method
9. Bean is destroyed
```

Think of it like an employee's journey:

1. HR finds the candidate (component scanning)
2. Employee is hired (constructor)
3. Employee gets a desk, computer, and tools (dependency injection)
4. Employee completes orientation training (@PostConstruct)
5. Employee works daily (bean is in use)
6. Employee gets retirement notice (application shutdown)
7. Employee returns equipment and wraps up (@PreDestroy)
8. Employee leaves the company (bean destroyed)

---

## 7.8 Component Scanning

How does Spring find your beans? Through **component scanning**.

**Component scanning** means Spring automatically searches through your packages to find classes with annotations like `@Component`, `@Service`, `@Repository`, and `@Controller`.

### How It Works

Your main application class has `@SpringBootApplication`. This annotation includes `@ComponentScan`, which tells Spring to scan the package of the main class and all sub-packages.

```java
package com.example.demo;  // <-- Spring scans from here

@SpringBootApplication  // Includes @ComponentScan
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

Spring will scan:

```
com.example.demo           <-- Scanned (main package)
com.example.demo.service   <-- Scanned (sub-package)
com.example.demo.repository <-- Scanned (sub-package)
com.example.demo.controller <-- Scanned (sub-package)
com.example.demo.config    <-- Scanned (sub-package)

com.example.other          <-- NOT scanned (different root)
com.another.project        <-- NOT scanned (different root)
```

### The Scanning Process

```
+-----------------------------------------------------+
|  Application Starts                                   |
+-----------------------------------------------------+
          |
          v
+-----------------------------------------------------+
|  @SpringBootApplication triggers component scanning   |
+-----------------------------------------------------+
          |
          v
+-----------------------------------------------------+
|  Spring scans com.example.demo and sub-packages       |
+-----------------------------------------------------+
          |
          v
+-----------------------------------------------------+
|  Found @Component on GreetingGenerator? --> Create    |
|  Found @Service on PricingService?      --> Create    |
|  Found @Repository on ProductRepository? --> Create   |
|  Found @Controller on PriceController?  --> Create    |
|  Found plain class Calculator?          --> Skip      |
+-----------------------------------------------------+
          |
          v
+-----------------------------------------------------+
|  All beans created and stored in Application Context  |
+-----------------------------------------------------+
```

### Custom Component Scanning

You can tell Spring to scan additional packages:

```java
@SpringBootApplication
@ComponentScan(basePackages = {
    "com.example.demo",
    "com.example.shared"
})
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

But in most projects, the default scanning is enough. Just keep all your classes under the same root package as your main class.

---

## 7.9 Putting It All Together

Let us build a small example that uses everything we learned. We will create a simple notification system.

### Project Structure

```
src/main/java/com/example/demo/
├── DemoApplication.java
├── config/
│   └── NotificationConfig.java
├── model/
│   └── Notification.java
├── repository/
│   └── NotificationRepository.java
├── service/
│   └── NotificationService.java
└── util/
    └── MessageFormatter.java
```

### The Model

```java
package com.example.demo.model;

import java.time.LocalDateTime;

public class Notification {

    private Long id;
    private String recipient;
    private String message;
    private boolean sent;
    private LocalDateTime createdAt;

    public Notification() {
        this.createdAt = LocalDateTime.now();
        this.sent = false;
    }

    public Notification(String recipient, String message) {
        this();
        this.recipient = recipient;
        this.message = message;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getRecipient() { return recipient; }
    public void setRecipient(String recipient) {
        this.recipient = recipient;
    }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public boolean isSent() { return sent; }
    public void setSent(boolean sent) { this.sent = sent; }
    public LocalDateTime getCreatedAt() { return createdAt; }

    @Override
    public String toString() {
        return "Notification{" +
                "id=" + id +
                ", recipient='" + recipient + '\'' +
                ", message='" + message + '\'' +
                ", sent=" + sent +
                '}';
    }
}
```

This is a plain Java class. No annotations. It is not a bean. It is just a data container.

### The Utility (@Component)

```java
package com.example.demo.util;

import org.springframework.stereotype.Component;

@Component
public class MessageFormatter {

    private static final String PREFIX = "[NOTIFICATION] ";

    public String format(String recipient, String message) {
        return PREFIX + "To: " + recipient + " | " + message;
    }

    public String formatUrgent(String recipient, String message) {
        return "*** URGENT *** " +
                PREFIX + "To: " + recipient + " | " + message;
    }
}
```

We use `@Component` because this is a utility class. It does not contain business logic, access data, or handle web requests.

### The Repository (@Repository)

```java
package com.example.demo.repository;

import com.example.demo.model.Notification;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Repository
public class NotificationRepository {

    private final List<Notification> notifications = new ArrayList<>();
    private long nextId = 1;

    public Notification save(Notification notification) {
        notification.setId(nextId++);
        notifications.add(notification);
        return notification;
    }

    public Optional<Notification> findById(Long id) {
        return notifications.stream()
                .filter(n -> n.getId().equals(id))
                .findFirst();
    }

    public List<Notification> findAll() {
        return new ArrayList<>(notifications);
    }

    public List<Notification> findUnsent() {
        return notifications.stream()
                .filter(n -> !n.isSent())
                .toList();
    }
}
```

We use `@Repository` because this class stores and retrieves data.

### The Service (@Service)

```java
package com.example.demo.service;

import com.example.demo.model.Notification;
import com.example.demo.repository.NotificationRepository;
import com.example.demo.util.MessageFormatter;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class NotificationService {

    private static final Logger log =
            LoggerFactory.getLogger(NotificationService.class);

    private final NotificationRepository repository;
    private final MessageFormatter formatter;

    public NotificationService(NotificationRepository repository,
                                MessageFormatter formatter) {
        this.repository = repository;
        this.formatter = formatter;
    }

    @PostConstruct
    public void init() {
        log.info("NotificationService is ready");
    }

    public Notification createNotification(String recipient,
                                            String message) {
        String formattedMessage = formatter.format(recipient, message);
        Notification notification =
                new Notification(recipient, formattedMessage);
        return repository.save(notification);
    }

    public Notification sendNotification(Long id) {
        Notification notification = repository.findById(id)
                .orElseThrow(() -> new RuntimeException(
                        "Notification not found: " + id));

        // Simulate sending
        log.info("Sending: {}", notification.getMessage());
        notification.setSent(true);
        return notification;
    }

    public List<Notification> getUnsentNotifications() {
        return repository.findUnsent();
    }

    public List<Notification> getAllNotifications() {
        return repository.findAll();
    }
}
```

We use `@Service` because this class contains business logic. It decides how to create, format, and send notifications.

Notice the constructor takes two parameters: `NotificationRepository` and `MessageFormatter`. Spring injects both automatically.

### The Configuration (@Configuration with @Bean)

```java
package com.example.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.format.DateTimeFormatter;

@Configuration
public class NotificationConfig {

    @Bean
    public DateTimeFormatter notificationDateFormatter() {
        return DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    }
}
```

We use `@Bean` here because `DateTimeFormatter` is a Java standard library class. We cannot add `@Component` to it. So we create it in a `@Configuration` class.

### How Spring Wires It All Together

```
+--------------------------------------------------+
|           Spring Application Context              |
|                                                    |
|  Scanning com.example.demo...                     |
|                                                    |
|  Found: @Component MessageFormatter    --> Create  |
|  Found: @Repository NotificationRepo  --> Create   |
|  Found: @Service NotificationService   --> Create  |
|  Found: @Configuration NotificationConfig          |
|         @Bean notificationDateFormatter --> Create  |
|                                                    |
|  Wiring dependencies:                              |
|  NotificationService needs:                        |
|    - NotificationRepository  ✓ Found              |
|    - MessageFormatter        ✓ Found              |
|                                                    |
|  All beans created and wired!                      |
+--------------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Forgetting the Annotation

```java
// WRONG: No annotation -- Spring ignores this class
public class EmailService {
    public void sendEmail(String to, String body) {
        // ...
    }
}
```

```java
// CORRECT: Add @Service so Spring manages it
@Service
public class EmailService {
    public void sendEmail(String to, String body) {
        // ...
    }
}
```

### Mistake 2: Putting Classes in the Wrong Package

```
// WRONG: Class is outside the scanned package
com.other.project.MyService  <-- Spring will NOT find this

// CORRECT: Class is under the main package
com.example.demo.service.MyService  <-- Spring WILL find this
```

### Mistake 3: Using new Instead of Injection

```java
// WRONG: Creating the object yourself
@Service
public class OrderService {
    public void processOrder() {
        PricingService pricing = new PricingService();  // BAD!
        pricing.calculateTotal(10.0, 2);
    }
}
```

```java
// CORRECT: Let Spring inject it
@Service
public class OrderService {
    private final PricingService pricingService;

    public OrderService(PricingService pricingService) {
        this.pricingService = pricingService;
    }

    public void processOrder() {
        pricingService.calculateTotal(10.0, 2);
    }
}
```

When you use `new`, you get a different object than the one Spring manages. That object will not have its own dependencies injected. Always let Spring provide beans through injection.

### Mistake 4: Circular Dependencies

```java
// WRONG: A depends on B, and B depends on A
@Service
public class ServiceA {
    public ServiceA(ServiceB serviceB) { }  // Needs B
}

@Service
public class ServiceB {
    public ServiceB(ServiceA serviceA) { }  // Needs A
}
// Spring cannot create either one first!
```

This is like two employees who each say "I will not start until the other person starts first." Nobody starts. Redesign your code to break the cycle.

---

## Best Practices

1. **Use the most specific annotation.** Use `@Service` for services, `@Repository` for data access, `@Controller` for web controllers. Only use `@Component` when none of the others fit.

2. **Use constructor injection.** It makes dependencies clear, supports immutability with `final` fields, and makes testing easier.

3. **Keep beans stateless when possible.** Singleton beans are shared. If they store mutable state, you will get bugs with concurrent access.

4. **One responsibility per bean.** A service should not also access the database directly. Delegate to a repository.

5. **Keep your classes in sub-packages of the main package.** This ensures component scanning finds them.

6. **Use `@Bean` for third-party classes.** You cannot annotate library code, so configure it in a `@Configuration` class.

7. **Name your beans clearly.** The class name becomes the bean name (with a lowercase first letter). `PricingService` becomes the bean `pricingService`.

---

## Quick Summary

- A **bean** is an object managed by Spring. Spring creates it, stores it, and provides it to other beans.
- The **Application Context** is the container that holds all beans.
- `@Component` is the generic annotation. `@Service`, `@Repository`, and `@Controller` are specialized versions.
- **Singleton** scope (default) means one instance shared everywhere. **Prototype** scope means a new instance each time.
- `@Bean` in a `@Configuration` class lets you create beans from third-party classes or when you need custom setup.
- `@PostConstruct` runs code after a bean is created. `@PreDestroy` runs code before it is destroyed.
- **Component scanning** automatically finds annotated classes in the main package and sub-packages.

---

## Key Points

- Every Spring feature depends on beans. They are the foundation.
- Always use constructor injection over field injection.
- Use the right stereotype annotation for readability.
- Beans are singleton by default. Use prototype only when needed.
- Do not use `new` to create objects that should be beans.
- Keep beans in sub-packages of your main application class.

---

## Practice Questions

1. What is the difference between a regular Java object and a Spring Bean?

2. You have a class that sends SMS messages. It does not access a database and does not handle web requests. Which annotation should you use: `@Component`, `@Service`, `@Repository`, or `@Controller`? Why?

3. Explain the difference between singleton and prototype scope. Give an example of when you would use each.

4. Why would you use `@Bean` in a `@Configuration` class instead of putting `@Component` on the class directly?

5. What happens if you put a class in a package that is not under the main application package?

---

## Exercises

### Exercise 1: Build a Calculator Service

Create a Spring Boot application with the following beans:

- `MathUtils` (`@Component`) -- has methods `add(int a, int b)`, `subtract(int a, int b)`, `multiply(int a, int b)`
- `CalculatorService` (`@Service`) -- uses `MathUtils` to perform calculations and logs the results
- `AppConfig` (`@Configuration`) -- creates a `DecimalFormat` bean configured with pattern `"#,###.##"`

Run the application and verify all beans are created using `@PostConstruct` logging.

### Exercise 2: Employee Management System

Create beans for a simple employee management system:

- `Employee` model class (not a bean) with fields: `id`, `name`, `department`, `salary`
- `EmployeeRepository` (`@Repository`) -- stores employees in a `List`, with `save()`, `findById()`, `findAll()`, and `findByDepartment()` methods
- `SalaryCalculator` (`@Component`) -- has a method `calculateAnnualSalary(double monthlySalary)` that multiplies by 12 and adds a 10% bonus
- `EmployeeService` (`@Service`) -- uses both `EmployeeRepository` and `SalaryCalculator`

Add `@PostConstruct` to `EmployeeService` to pre-load three employees.

### Exercise 3: Prototype Scope Experiment

Create a `RequestTracker` bean with prototype scope that has an `id` field set to a random UUID in its constructor. Create a `@Service` that gets two `RequestTracker` instances and prints their IDs. Verify they are different objects.

Hint: You cannot inject a prototype bean into a singleton bean using simple constructor injection and get a new instance each time. Look up `ObjectProvider<T>` or `ApplicationContext.getBean()`.

---

## What Is Next?

You now understand how Spring manages objects. But real applications need configuration. They need different settings for development, testing, and production. In the next chapter, you will learn about **properties and profiles** -- how to configure your Spring Boot application for different environments without changing code.
