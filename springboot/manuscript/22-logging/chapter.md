# Chapter 22: Logging

## What You Will Learn

- Why logging matters and when to use it.
- What SLF4J and Logback are and how they work together.
- How to create a logger with LoggerFactory.
- The five log levels: TRACE, DEBUG, INFO, WARN, ERROR.
- How to configure log levels per package.
- How to write logs to files and configure log rotation.
- What MDC (Mapped Diagnostic Context) is and how to use it.
- How to use @Slf4j from Lombok to simplify logging.

## Why This Chapter Matters

Imagine you are a detective investigating a crime. You arrive at the scene, but there are no security cameras, no witnesses, and no fingerprints. How do you figure out what happened?

Now imagine the building had security cameras on every floor, recording everything. You can rewind, see exactly who entered, what they did, and when they left. Case solved.

Logging is the security camera for your application. When a user reports a bug, when a server crashes at 3 AM, when a payment fails silently, logs are your only way to understand what happened. Without logging, you are debugging blind. With good logging, you can trace every request, every decision, and every error your application makes.

---

## 22.1 What Is Logging?

**Logging** is the practice of recording events that happen in your application. Instead of using `System.out.println()` (which prints to the console and disappears), you use a logging framework that can:

- Write to files that persist after the application stops.
- Include timestamps, thread names, and class names automatically.
- Filter messages by severity (show errors but hide debug messages).
- Rotate log files so they do not fill up your disk.

### System.out.println vs Logging

| Feature | System.out.println | Logging Framework |
|---------|-------------------|-------------------|
| Timestamp | No | Yes (automatic) |
| Log levels | No | Yes (TRACE to ERROR) |
| Output to file | No (console only) | Yes (file, console, or both) |
| Filtering | No | Yes (per package, per level) |
| Performance | Blocking | Configurable (async) |
| Thread info | No | Yes (automatic) |
| Production use | Never | Always |

Here is a comparison:

```java
// Bad - Using System.out.println
System.out.println("User logged in: alice");
// Output: User logged in: alice

// Good - Using a logger
log.info("User logged in: {}", username);
// Output: 2024-01-15 10:30:45.123 INFO  [main]
//   c.e.security.AuthService : User logged in: alice
```

The logger gives you the date, time, log level, thread name, class name, and your message. All automatically.

---

## 22.2 SLF4J and Logback

Spring Boot uses two libraries for logging:

1. **SLF4J** (Simple Logging Facade for Java) -- An API that your code uses. Think of it as the steering wheel.
2. **Logback** -- The implementation that does the actual logging. Think of it as the engine.

```
+-----------------------------------------+
|           LOGGING ARCHITECTURE           |
+-----------------------------------------+
|                                          |
|  Your Code                               |
|     |                                    |
|     v                                    |
|  [SLF4J API]  <-- You program to this   |
|     |                                    |
|     v                                    |
|  [Logback]    <-- Does the actual work   |
|     |                                    |
|     +---> Console output                 |
|     +---> Log file                       |
|     +---> Remote server (optional)       |
|                                          |
+-----------------------------------------+
```

Why use a facade? Because you might want to switch from Logback to Log4j2 later. If your code uses SLF4J, you only change the underlying engine. Your code stays the same.

The good news: Spring Boot includes both SLF4J and Logback automatically. You do not need to add any dependencies.

---

## 22.3 Creating Your First Logger

Here is how to create a logger in a Spring Boot class:

```java
// src/main/java/com/example/logging/service/ProductService.java
package com.example.logging.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class ProductService {

    // Create a logger for this class
    private static final Logger log =
        LoggerFactory.getLogger(ProductService.class);

    public String getProduct(Long id) {
        log.info("Fetching product with id: {}", id);

        // Simulate business logic
        if (id <= 0) {
            log.warn("Invalid product id: {}", id);
            throw new IllegalArgumentException("Product id must be positive");
        }

        log.debug("Product {} found in database", id);
        return "Product " + id;
    }
}
```

**Line-by-line explanation:**

- `import org.slf4j.Logger` -- Import the SLF4J Logger interface (not Logback's logger).
- `import org.slf4j.LoggerFactory` -- The factory that creates loggers.
- `private static final Logger log = LoggerFactory.getLogger(ProductService.class)` -- Creates a logger named after this class. We make it `static final` because one logger per class is enough.
- `log.info("Fetching product with id: {}", id)` -- Logs an INFO message. The `{}` is a placeholder that gets replaced with the value of `id`.
- `log.warn("Invalid product id: {}", id)` -- Logs a WARNING message. Something unexpected happened, but the application can continue.
- `log.debug("Product {} found in database", id)` -- Logs a DEBUG message. This is detailed information useful during development but usually hidden in production.

### Why Use {} Placeholders Instead of String Concatenation?

```java
// Bad - String is always concatenated, even if level is disabled
log.debug("Product: " + product.toString());

// Good - toString() only called if debug is enabled
log.debug("Product: {}", product);
```

With `{}` placeholders, the argument is only converted to a string if the log level is enabled. This is a performance optimization. If debug logging is turned off (which it usually is in production), the string concatenation never happens.

---

## 22.4 Understanding Log Levels

SLF4J has five log levels, from most detailed to most critical:

```
+----------------------------------------------+
|          LOG LEVELS (least to most severe)    |
+----------------------------------------------+
|                                              |
|  TRACE  <-- Most detailed, rarely used       |
|    |                                         |
|    v                                         |
|  DEBUG  <-- Development details              |
|    |                                         |
|    v                                         |
|  INFO   <-- Normal operations                |
|    |                                         |
|    v                                         |
|  WARN   <-- Something unexpected             |
|    |                                         |
|    v                                         |
|  ERROR  <-- Something broke                  |
|                                              |
+----------------------------------------------+
```

| Level | When to Use | Example |
|-------|-------------|---------|
| **TRACE** | Very detailed diagnostic info | Method entry/exit, variable values |
| **DEBUG** | Development-time details | SQL queries, cache hits, algorithm steps |
| **INFO** | Normal business events | User login, order placed, server started |
| **WARN** | Unexpected but recoverable | Retry attempt, deprecated API used, slow query |
| **ERROR** | Something failed | Database connection lost, payment failed, exception |

### How Level Filtering Works

When you set a log level, you see that level **and everything above it**:

```
Set level to WARN:
  TRACE  --> Hidden
  DEBUG  --> Hidden
  INFO   --> Hidden
  WARN   --> Visible
  ERROR  --> Visible

Set level to DEBUG:
  TRACE  --> Hidden
  DEBUG  --> Visible
  INFO   --> Visible
  WARN   --> Visible
  ERROR  --> Visible

Set level to TRACE:
  TRACE  --> Visible  (everything visible)
  DEBUG  --> Visible
  INFO   --> Visible
  WARN   --> Visible
  ERROR  --> Visible
```

### Using Each Level Correctly

```java
@Service
public class OrderService {

    private static final Logger log =
        LoggerFactory.getLogger(OrderService.class);

    public void placeOrder(Order order) {
        log.trace("Entering placeOrder method with order: {}", order);

        log.debug("Validating order items: {}", order.getItems());

        log.info("Order placed successfully. OrderId: {}, " +
            "Total: ${}", order.getId(), order.getTotal());

        if (order.getTotal() > 10000) {
            log.warn("Large order detected. OrderId: {}, " +
                "Total: ${}", order.getId(), order.getTotal());
        }

        try {
            paymentService.charge(order);
        } catch (PaymentException e) {
            log.error("Payment failed for OrderId: {}. Reason: {}",
                order.getId(), e.getMessage(), e);
            // Note: passing the exception as last argument
            // prints the full stack trace
        }

        log.trace("Exiting placeOrder method");
    }
}
```

**Important**: When you pass an exception to a log method, pass it as the last argument. SLF4J will print the full stack trace. You do not need a `{}` placeholder for the exception:

```java
// Correct - exception is the last argument (no placeholder needed)
log.error("Payment failed: {}", order.getId(), exception);

// Wrong - this will NOT print the stack trace
log.error("Payment failed: {} {}", order.getId(), exception);
```

---

## 22.5 Configuring Log Levels in application.properties

Spring Boot's default log level is INFO. You can change it:

```properties
# src/main/resources/application.properties

# Change the root log level (affects everything)
logging.level.root=WARN

# Set level for your application packages
logging.level.com.example=DEBUG

# Set level for a specific class
logging.level.com.example.logging.service.ProductService=TRACE

# Set level for Spring framework classes
logging.level.org.springframework.web=DEBUG

# Set level for Hibernate SQL queries
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.type.descriptor.sql.BasicBinder=TRACE
```

**Line-by-line explanation:**

- `logging.level.root=WARN` -- The root logger affects all packages. Setting it to WARN hides INFO and DEBUG messages from all libraries.
- `logging.level.com.example=DEBUG` -- Shows DEBUG (and above) messages from your application code.
- `logging.level.org.springframework.web=DEBUG` -- Shows DEBUG messages from Spring's web layer. Useful for seeing how requests are processed.
- `logging.level.org.hibernate.SQL=DEBUG` -- Shows the actual SQL queries that Hibernate generates. Very useful for debugging database issues.

### Per-Package Logging Strategy

```
+--------------------------------------------+
|     RECOMMENDED LOGGING STRATEGY            |
+--------------------------------------------+
|                                             |
|  Development:                               |
|    root = INFO                              |
|    com.example = DEBUG                      |
|    org.hibernate.SQL = DEBUG                |
|                                             |
|  Production:                                |
|    root = WARN                              |
|    com.example = INFO                       |
|    org.hibernate.SQL = WARN                 |
|                                             |
|  Troubleshooting (temporary):               |
|    root = WARN                              |
|    com.example.problem.area = DEBUG         |
|                                             |
+--------------------------------------------+
```

---

## 22.6 Customizing the Log Format

Spring Boot uses a default log format. You can customize it:

```properties
# Default format (this is what Spring Boot uses)
logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss.SSS} %5level [%15.15thread] %-40.40logger{39} : %msg%n

# Simpler format
logging.pattern.console=%d{HH:mm:ss} %-5level [%thread] %logger{20} - %msg%n
```

| Pattern | Meaning | Example |
|---------|---------|---------|
| `%d{...}` | Date/time | `2024-01-15 10:30:45.123` |
| `%level` | Log level | `INFO` |
| `%5level` | Level, right-padded to 5 chars | ` INFO` |
| `%thread` | Thread name | `http-nio-8080-exec-1` |
| `%logger` | Logger name (class) | `c.e.l.s.ProductService` |
| `%msg` | Your message | `Fetching product with id: 42` |
| `%n` | New line | (line break) |
| `%-40.40` | Left-align, min/max 40 chars | Pads or truncates |

Example output with the default format:

```
2024-01-15 10:30:45.123  INFO [http-nio-8080-exec-1] c.e.l.s.ProductService  : Fetching product with id: 42
2024-01-15 10:30:45.124 DEBUG [http-nio-8080-exec-1] c.e.l.s.ProductService  : Product 42 found in database
2024-01-15 10:30:45.200  WARN [http-nio-8080-exec-2] c.e.l.s.ProductService  : Invalid product id: -1
2024-01-15 10:30:45.300 ERROR [http-nio-8080-exec-3] c.e.l.s.OrderService    : Payment failed for OrderId: 100
```

---

## 22.7 Writing Logs to Files

In production, console output disappears when the terminal closes. You need to write logs to files:

```properties
# src/main/resources/application.properties

# Write logs to a file
logging.file.name=logs/application.log

# Set the file log format (can be different from console)
logging.pattern.file=%d{yyyy-MM-dd HH:mm:ss.SSS} %5level [%thread] %logger{36} : %msg%n
```

**Line-by-line explanation:**

- `logging.file.name=logs/application.log` -- Writes logs to the file `logs/application.log` relative to the application directory. The directory is created automatically.
- `logging.pattern.file` -- You can use a different format for file output than console output.

After starting the application, you will see:

```
project/
  +-- logs/
  |     +-- application.log
  +-- src/
  +-- pom.xml
```

---

## 22.8 Log File Rotation

Log files can grow very large. Log rotation automatically archives old logs and starts new ones:

```properties
# src/main/resources/application.properties

# Write to file
logging.file.name=logs/application.log

# Maximum size of a single log file (default 10MB)
logging.logback.rollingpolicy.max-file-size=10MB

# Maximum number of archived log files to keep (default 7)
logging.logback.rollingpolicy.max-history=30

# Maximum total size of all log files (default unlimited)
logging.logback.rollingpolicy.total-size-cap=1GB

# Name pattern for archived files
logging.logback.rollingpolicy.file-name-pattern=logs/application.%d{yyyy-MM-dd}.%i.log.gz
```

**Line-by-line explanation:**

- `max-file-size=10MB` -- When the log file reaches 10MB, it is archived and a new one starts.
- `max-history=30` -- Keep the last 30 days of log files. Older files are deleted automatically.
- `total-size-cap=1GB` -- The total size of all log files cannot exceed 1GB. This prevents logs from filling your disk.
- `file-name-pattern` -- Archived files are named like `application.2024-01-15.0.log.gz`. The `.gz` extension means they are compressed to save space.

Here is what the logs directory looks like after a few days:

```
logs/
  +-- application.log               (current, active log)
  +-- application.2024-01-14.0.log.gz  (yesterday, compressed)
  +-- application.2024-01-13.0.log.gz  (two days ago)
  +-- application.2024-01-12.0.log.gz  (three days ago)
```

---

## 22.9 MDC (Mapped Diagnostic Context)

When your server handles hundreds of requests simultaneously, log lines from different requests get mixed together. How do you trace all log lines for a single request?

**MDC** (Mapped Diagnostic Context) lets you attach contextual data (like a request ID or user ID) to every log line in the current thread:

```java
// src/main/java/com/example/logging/filter/RequestIdFilter.java
package com.example.logging.filter;

import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.UUID;

@Component
public class RequestIdFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request,
                         ServletResponse response,
                         FilterChain chain)
            throws IOException, ServletException {

        try {
            // Generate a unique ID for this request
            String requestId = UUID.randomUUID().toString()
                .substring(0, 8);

            // Get username if available
            HttpServletRequest httpRequest = (HttpServletRequest) request;
            String user = httpRequest.getRemoteUser();
            if (user == null) {
                user = "anonymous";
            }

            // Put values into MDC
            MDC.put("requestId", requestId);
            MDC.put("user", user);

            // Continue processing the request
            chain.doFilter(request, response);

        } finally {
            // Always clear MDC after request is done
            MDC.clear();
        }
    }
}
```

**Line-by-line explanation:**

- `MDC.put("requestId", requestId)` -- Adds a key-value pair to the MDC for the current thread. Every log statement on this thread will have access to this value.
- `MDC.clear()` -- Removes all MDC values. This must be in a `finally` block to prevent memory leaks and data bleeding between requests.

Now update the log pattern to include MDC values:

```properties
logging.pattern.console=%d{HH:mm:ss.SSS} %-5level [%thread] [%X{requestId}] [%X{user}] %logger{20} - %msg%n
```

- `%X{requestId}` -- Prints the MDC value for "requestId".
- `%X{user}` -- Prints the MDC value for "user".

Now your logs look like this:

```
10:30:45.123 INFO  [exec-1] [a1b2c3d4] [alice] ProductService - Fetching product with id: 42
10:30:45.124 DEBUG [exec-1] [a1b2c3d4] [alice] ProductService - Product 42 found
10:30:45.130 INFO  [exec-2] [e5f6a7b8] [bob]   OrderService   - Placing order 100
10:30:45.131 INFO  [exec-1] [a1b2c3d4] [alice] OrderService   - Placing order 101
10:30:45.132 ERROR [exec-2] [e5f6a7b8] [bob]   OrderService   - Payment failed
```

Even though Alice's and Bob's requests are interleaved on different threads, you can filter by `requestId` to see all log lines for a single request:

```bash
# Find all log lines for request a1b2c3d4
grep "a1b2c3d4" logs/application.log
```

```
10:30:45.123 INFO  [exec-1] [a1b2c3d4] [alice] ProductService - Fetching product with id: 42
10:30:45.124 DEBUG [exec-1] [a1b2c3d4] [alice] ProductService - Product 42 found
10:30:45.131 INFO  [exec-1] [a1b2c3d4] [alice] OrderService   - Placing order 101
```

---

## 22.10 Logging in Controllers and Services

Here is a complete example showing logging across different layers:

```java
// src/main/java/com/example/logging/controller/ProductController.java
package com.example.logging.controller;

import com.example.logging.service.ProductService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private static final Logger log =
        LoggerFactory.getLogger(ProductController.class);

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getProduct(
            @PathVariable Long id) {

        log.info("Received request to get product: {}", id);
        long startTime = System.currentTimeMillis();

        try {
            Map<String, Object> product = productService.findById(id);
            long duration = System.currentTimeMillis() - startTime;

            log.info("Product {} retrieved in {} ms", id, duration);
            return ResponseEntity.ok(product);

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;
            log.error("Failed to get product {} after {} ms",
                id, duration, e);
            return ResponseEntity.notFound().build();
        }
    }
}
```

```java
// src/main/java/com/example/logging/service/ProductService.java
package com.example.logging.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class ProductService {

    private static final Logger log =
        LoggerFactory.getLogger(ProductService.class);

    public Map<String, Object> findById(Long id) {
        log.debug("Searching for product {} in database", id);

        if (id <= 0) {
            log.warn("Invalid product id received: {}", id);
            throw new IllegalArgumentException(
                "Product id must be positive");
        }

        // Simulate database lookup
        log.debug("Product {} found, preparing response", id);

        return Map.of(
            "id", id,
            "name", "Widget " + id,
            "price", 29.99
        );
    }
}
```

**Output when calling GET /api/products/42:**

```
10:30:45.100 INFO  [exec-1] [a1b2c3d4] ProductController - Received request to get product: 42
10:30:45.101 DEBUG [exec-1] [a1b2c3d4] ProductService    - Searching for product 42 in database
10:30:45.105 DEBUG [exec-1] [a1b2c3d4] ProductService    - Product 42 found, preparing response
10:30:45.106 INFO  [exec-1] [a1b2c3d4] ProductController - Product 42 retrieved in 6 ms
```

---

## 22.11 Using @Slf4j from Lombok

If you use Project Lombok, you can avoid the boilerplate logger declaration. Add Lombok to your dependencies:

```xml
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <optional>true</optional>
</dependency>
```

Then use the `@Slf4j` annotation:

```java
// Without Lombok
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class ProductService {
    private static final Logger log =
        LoggerFactory.getLogger(ProductService.class);

    // ... use log.info(), log.debug(), etc.
}

// With Lombok @Slf4j
import lombok.extern.slf4j.Slf4j;

@Slf4j    // Lombok generates the Logger field for you
@Service
public class ProductService {
    // log is already available! No need to declare it.

    public void doSomething() {
        log.info("This works without declaring the logger");
    }
}
```

**Line-by-line explanation:**

- `@Slf4j` -- Lombok generates `private static final Logger log = LoggerFactory.getLogger(ProductService.class);` at compile time. The variable is always named `log`.
- You save two import lines and one field declaration. In a large project with hundreds of classes, this adds up.

> **Note**: Make sure your IDE has the Lombok plugin installed. Without it, your IDE will show errors because it cannot see the generated `log` field.

---

## 22.12 What to Log and What Not to Log

### What to Log

| Category | Examples |
|----------|---------|
| **Business events** | User registered, order placed, payment processed |
| **Security events** | Login success, login failure, access denied |
| **Performance data** | Request duration, slow queries, cache misses |
| **Errors and exceptions** | Database errors, API failures, validation errors |
| **Application lifecycle** | Startup, shutdown, configuration loaded |

### What NOT to Log

| Category | Why |
|----------|-----|
| **Passwords** | Even encoded passwords should not appear in logs |
| **Credit card numbers** | PCI compliance prohibits logging card data |
| **Personal data** | GDPR and privacy laws restrict logging personal info |
| **Session tokens** | Attackers could steal them from log files |
| **Large objects** | Logging an entire database result set wastes disk space |

```java
// BAD - logging sensitive data
log.info("User login: username={}, password={}", username, password);

// GOOD - log the event without sensitive data
log.info("User login successful: username={}", username);

// BAD - logging too much data
log.info("Query result: {}", entireDatabaseResultSet);

// GOOD - log a summary
log.info("Query returned {} results", results.size());
```

---

## Common Mistakes

1. **Using System.out.println instead of a logger.** Print statements have no timestamps, no levels, and no file output. They should never appear in production code.

2. **Logging too much in production.** Setting the root level to DEBUG in production generates enormous log files and can slow down your application. Use INFO or WARN for production.

3. **Logging too little.** If you only log errors, you have no context when an error occurs. Log important business events at INFO level so you can understand the flow.

4. **Using string concatenation instead of {} placeholders.** `log.debug("User: " + user)` evaluates the string even when DEBUG is disabled. Use `log.debug("User: {}", user)` instead.

5. **Forgetting to clear MDC.** If you put values into MDC but do not clear them in a `finally` block, values can leak to other requests using the same thread.

6. **Logging sensitive information.** Never log passwords, credit card numbers, social security numbers, or session tokens. This is a security violation.

---

## Best Practices

1. **Use SLF4J with {} placeholders.** This is both more readable and more performant than string concatenation.

2. **Log at the right level.** Use INFO for business events, WARN for unexpected situations, ERROR for failures, and DEBUG for development details.

3. **Include context in log messages.** Instead of "Error occurred", write "Payment failed for orderId: 123, reason: insufficient funds". The more context, the faster you can diagnose problems.

4. **Use MDC for request tracing.** Assign a unique ID to each request so you can follow it through all service layers.

5. **Configure log rotation.** Set max-file-size, max-history, and total-size-cap to prevent logs from filling your disk.

6. **Use different logging configurations per environment.** DEBUG in development, INFO in staging, WARN in production. Use Spring profiles to manage this.

---

## Quick Summary

Logging records events that happen in your application for debugging and monitoring. Spring Boot uses SLF4J as the logging API and Logback as the implementation. You create loggers with LoggerFactory.getLogger() or by adding the @Slf4j Lombok annotation to your class. There are five log levels: TRACE (most detailed), DEBUG, INFO, WARN, and ERROR (most critical). Setting a level shows that level and everything above it. You configure per-package log levels in application.properties using logging.level.package.name=LEVEL. Logs can be written to files with automatic rotation to prevent disk space issues. MDC (Mapped Diagnostic Context) lets you attach contextual data like request IDs to every log line on the current thread, making it easy to trace a single request through multiple service layers.

---

## Key Points

- SLF4J is the logging API. Logback is the implementation. Spring Boot includes both.
- Create loggers with `LoggerFactory.getLogger(YourClass.class)`.
- Five levels: TRACE < DEBUG < INFO < WARN < ERROR.
- Setting a level shows that level and all higher levels.
- Use `{}` placeholders instead of string concatenation for performance.
- Pass exceptions as the last argument to log methods for stack traces.
- Configure per-package levels with `logging.level.package=LEVEL`.
- Write to files with `logging.file.name`.
- Use log rotation to prevent disk space issues.
- MDC attaches contextual data (request ID, user) to log lines.
- @Slf4j from Lombok eliminates boilerplate logger declarations.
- Never log passwords, credit card numbers, or session tokens.

---

## Practice Questions

1. What is the difference between SLF4J and Logback, and why does Spring Boot use both?

2. If you set the log level to WARN, which log levels will be visible and which will be hidden?

3. Why should you use `log.debug("User: {}", user)` instead of `log.debug("User: " + user)`?

4. What is MDC, and how does it help when debugging a production issue?

5. You set `logging.level.com.example=DEBUG` but you are not seeing DEBUG messages from your `com.example.service.OrderService` class. What could be wrong?

---

## Exercises

### Exercise 1: Add Logging to a REST Controller

Create a REST controller with GET and POST endpoints. Add appropriate logging:
- Log incoming requests at INFO level (include the request details).
- Log successful responses at INFO level (include response time).
- Log validation errors at WARN level.
- Log exceptions at ERROR level (include the stack trace).

### Exercise 2: Configure Per-Environment Logging

Create three profile-specific property files:
- `application-dev.properties`: Root level WARN, your package DEBUG, console output only.
- `application-prod.properties`: Root level WARN, your package INFO, file output with rotation (5MB files, 30 days, 500MB total).

Test both profiles and verify the output differences.

### Exercise 3: Request Tracing with MDC

Create a filter that generates a unique request ID and adds it to MDC. Configure the log pattern to include the request ID. Send multiple concurrent requests and use the request ID to trace each request through the logs.

---

## What Is Next?

You now know how to record what your application does. But what about making your application do things automatically? In Chapter 23, you will learn about scheduling. You will set up tasks that run at fixed intervals, after delays, or on specific schedules using cron expressions. Think of it as setting alarm clocks for your application.
