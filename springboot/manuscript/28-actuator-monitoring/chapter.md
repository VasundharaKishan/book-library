# Chapter 28: Actuator and Monitoring

## What You Will Learn

- What Spring Boot Actuator is and why you need it.
- How to add Actuator to your application with one dependency.
- How to use the `/actuator/health` endpoint to check application health.
- How to expose and configure Actuator endpoints.
- How to use built-in endpoints: health, info, metrics, env, and loggers.
- How to create a custom `HealthIndicator` for your own checks.
- How to create a custom `InfoContributor` to expose application details.
- How to secure Actuator endpoints so only authorized users can access them.

## Why This Chapter Matters

Imagine you own a car. You drive it every day. How do you know if something is wrong? You look at the dashboard. The dashboard shows you fuel level, engine temperature, speed, and warning lights. Without a dashboard, you would drive blind until the engine overheats or the fuel runs out.

Spring Boot Actuator is the dashboard for your application. It tells you:

- Is the application running? (Health)
- Is the database connected? (Health)
- How much memory is being used? (Metrics)
- What configuration is active? (Environment)
- What is happening right now? (Loggers)

In production, you need this information to keep your application running smoothly. When something goes wrong at 3 AM, Actuator endpoints help you diagnose the problem without digging through code.

---

## 28.1 What Is Spring Boot Actuator?

**Spring Boot Actuator** is a set of built-in features that help you monitor and manage your application in production.

Think of it as adding health sensors to your application. Just like a hospital patient has monitors for heart rate, blood pressure, and oxygen levels, Actuator adds monitors for your application's health, performance, and configuration.

```
Your Application Without Actuator:
+------------------+
|  Spring Boot     |
|  Application     |    "Is everything OK?"
|                  |    "I have no idea."
|  [No monitors]   |
+------------------+

Your Application With Actuator:
+------------------+
|  Spring Boot     |
|  Application     |    "Is everything OK?"
|                  |    "Database: UP
|  [Health: UP]    |     Memory: 78% used
|  [Metrics: OK]   |     Requests: 142/min
|  [Info: v1.2.3]  |     Version: 1.2.3"
+------------------+
```

### What Actuator Provides

| Feature | What It Tells You |
|---|---|
| Health checks | Is the app running? Is the database connected? |
| Metrics | How many requests per minute? How much memory? |
| Environment | What properties and profiles are active? |
| Loggers | What log levels are set? Can change them at runtime. |
| Info | What version is deployed? When was it built? |
| Beans | What Spring beans are loaded? |
| Mappings | What URL endpoints are available? |

---

## 28.2 Adding Actuator to Your Application

Adding Actuator is as simple as adding one dependency.

### Step 1: Add the Dependency

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

### Step 2: Start Your Application

```bash
./mvnw spring-boot:run
```

### Step 3: Check the Health Endpoint

```bash
curl http://localhost:8080/actuator/health
```

**Output:**

```json
{
  "status": "UP"
}
```

That is it. Your application now has a health endpoint. "UP" means everything is working.

### What You Get Out of the Box

After adding the dependency, these endpoints are available by default:

| Endpoint | URL | Description |
|---|---|---|
| health | `/actuator/health` | Shows application health status |
| info | `/actuator/info` | Shows application information |

Only `health` and `info` are exposed over HTTP by default. This is a security feature. You do not want to accidentally expose sensitive configuration to the internet.

```
Default Actuator Endpoints:

+-------------------------------------------+
| http://localhost:8080/actuator             |
+-------------------------------------------+
| /actuator/health     -> { "status": "UP" }|
| /actuator/info       -> {}                 |
|                                            |
| All other endpoints: HIDDEN (for safety)   |
+-------------------------------------------+
```

---

## 28.3 Exposing More Endpoints

To see more endpoints, you need to explicitly expose them in `application.properties`.

### Expose Specific Endpoints

```properties
# application.properties

# Expose specific endpoints over HTTP
management.endpoints.web.exposure.include=health,info,metrics,env,loggers
```

### Expose All Endpoints

```properties
# application.properties

# Expose ALL endpoints over HTTP (use with caution!)
management.endpoints.web.exposure.include=*
```

> **Warning**: Exposing all endpoints is fine for development, but never do this in production without proper security. Some endpoints reveal sensitive information.

### Exclude Specific Endpoints

```properties
# Expose all EXCEPT env and beans
management.endpoints.web.exposure.include=*
management.endpoints.web.exposure.exclude=env,beans
```

### List All Available Endpoints

After exposing endpoints, visit:

```bash
curl http://localhost:8080/actuator
```

**Output:**

```json
{
  "_links": {
    "self": {
      "href": "http://localhost:8080/actuator"
    },
    "health": {
      "href": "http://localhost:8080/actuator/health"
    },
    "info": {
      "href": "http://localhost:8080/actuator/info"
    },
    "metrics": {
      "href": "http://localhost:8080/actuator/metrics"
    },
    "loggers": {
      "href": "http://localhost:8080/actuator/loggers"
    }
  }
}
```

This is a directory of all available endpoints with their URLs.

---

## 28.4 The Health Endpoint

The health endpoint is the most important Actuator endpoint. It tells you whether your application is healthy.

### Basic Health Check

```bash
curl http://localhost:8080/actuator/health
```

**Output (healthy):**

```json
{
  "status": "UP"
}
```

**Output (unhealthy):**

```json
{
  "status": "DOWN"
}
```

### Showing Detailed Health Information

By default, the health endpoint only shows "UP" or "DOWN". To see details about each component (database, disk space, etc.), add:

```properties
# application.properties
management.endpoint.health.show-details=always
```

Now the output includes component-level health:

```bash
curl http://localhost:8080/actuator/health
```

**Output:**

```json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "H2",
        "validationQuery": "isValid()"
      }
    },
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 499963174912,
        "free": 250148225024,
        "threshold": 10485760,
        "path": "/Users/dev/bookstore/.",
        "exists": true
      }
    },
    "ping": {
      "status": "UP"
    }
  }
}
```

```
Health Endpoint with Details:

+-------------------+
|  Application      |
|  Status: UP       |
+-------------------+
        |
   +----+----+----+
   |         |    |
+--+--+  +---+--+ +-----+
| DB  |  | Disk | | Ping|
| UP  |  | UP   | | UP  |
|     |  |      | |     |
| H2  |  | 250GB| |     |
| OK  |  | free | |     |
+-----+  +------+ +-----+

If ANY component is DOWN, the overall status becomes DOWN.
```

### Health Status Options

```properties
# Show details options:
management.endpoint.health.show-details=never     # Only UP/DOWN
management.endpoint.health.show-details=always     # Always show details
management.endpoint.health.show-details=when-authorized  # Only for authenticated users
```

### Health Indicators Spring Boot Provides

Spring Boot automatically adds health checks for components it detects:

| Component | Health Indicator | What It Checks |
|---|---|---|
| Database | `DataSourceHealthIndicator` | Can connect to the database? |
| Disk Space | `DiskSpaceHealthIndicator` | Is there enough free disk space? |
| Mail Server | `MailHealthIndicator` | Can connect to the SMTP server? |
| Redis | `RedisHealthIndicator` | Can connect to Redis? |
| RabbitMQ | `RabbitHealthIndicator` | Can connect to RabbitMQ? |

These are added automatically when the corresponding starter is in your `pom.xml`.

---

## 28.5 The Info Endpoint

The info endpoint shows information about your application. By default, it returns an empty object `{}`. You need to add information to it.

### Adding Info via Properties

```properties
# application.properties

management.info.env.enabled=true

info.app.name=BookStore API
info.app.description=A REST API for managing books
info.app.version=1.0.0
info.app.java-version=${java.version}
```

```bash
curl http://localhost:8080/actuator/info
```

**Output:**

```json
{
  "app": {
    "name": "BookStore API",
    "description": "A REST API for managing books",
    "version": "1.0.0",
    "java-version": "17.0.9"
  }
}
```

### Adding Build Info from Maven

Spring Boot can automatically include build information from Maven.

Add this plugin to your `pom.xml`:

```xml
<!-- pom.xml -->
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <executions>
                <execution>
                    <goals>
                        <goal>build-info</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

Now the info endpoint includes build details:

```json
{
  "build": {
    "artifact": "bookstore",
    "name": "bookstore",
    "time": "2024-01-15T10:30:00Z",
    "version": "1.0.0",
    "group": "com.example"
  }
}
```

---

## 28.6 The Metrics Endpoint

The metrics endpoint provides numerical measurements about your application.

### Listing Available Metrics

```bash
curl http://localhost:8080/actuator/metrics
```

**Output:**

```json
{
  "names": [
    "application.ready.time",
    "application.started.time",
    "disk.free",
    "disk.total",
    "http.server.requests",
    "jvm.memory.used",
    "jvm.memory.max",
    "jvm.threads.live",
    "process.cpu.usage",
    "system.cpu.usage",
    "tomcat.sessions.active.current"
  ]
}
```

### Getting a Specific Metric

```bash
curl http://localhost:8080/actuator/metrics/jvm.memory.used
```

**Output:**

```json
{
  "name": "jvm.memory.used",
  "description": "The amount of used memory",
  "baseUnit": "bytes",
  "measurements": [
    {
      "statistic": "VALUE",
      "value": 157286400
    }
  ],
  "availableTags": [
    {
      "tag": "area",
      "values": ["heap", "nonheap"]
    }
  ]
}
```

### Useful Metrics

| Metric | What It Measures | Command |
|---|---|---|
| `jvm.memory.used` | Memory usage | `/actuator/metrics/jvm.memory.used` |
| `jvm.memory.max` | Maximum memory | `/actuator/metrics/jvm.memory.max` |
| `process.cpu.usage` | CPU usage (0-1) | `/actuator/metrics/process.cpu.usage` |
| `http.server.requests` | HTTP request stats | `/actuator/metrics/http.server.requests` |
| `jvm.threads.live` | Active threads | `/actuator/metrics/jvm.threads.live` |
| `disk.free` | Free disk space | `/actuator/metrics/disk.free` |

### Filtering Metrics by Tag

```bash
# Get HTTP request metrics for GET requests only
curl "http://localhost:8080/actuator/metrics/http.server.requests?tag=method:GET"

# Get HTTP request metrics for a specific endpoint
curl "http://localhost:8080/actuator/metrics/http.server.requests?tag=uri:/api/books"

# Get metrics for a specific status code
curl "http://localhost:8080/actuator/metrics/http.server.requests?tag=status:200"
```

---

## 28.7 The Env Endpoint

The env endpoint shows all environment properties and their sources.

```bash
curl http://localhost:8080/actuator/env
```

**Output (abbreviated):**

```json
{
  "activeProfiles": ["dev"],
  "propertySources": [
    {
      "name": "systemProperties",
      "properties": {
        "java.version": {
          "value": "17.0.9"
        }
      }
    },
    {
      "name": "applicationConfig: application.properties",
      "properties": {
        "server.port": {
          "value": "8080"
        },
        "spring.datasource.url": {
          "value": "jdbc:h2:mem:bookstore"
        }
      }
    }
  ]
}
```

### Looking Up a Specific Property

```bash
curl http://localhost:8080/actuator/env/server.port
```

**Output:**

```json
{
  "property": {
    "source": "applicationConfig: application.properties",
    "value": "8080"
  }
}
```

> **Security Note**: The env endpoint can reveal sensitive information like database passwords. Spring Boot automatically sanitizes known sensitive keys (replacing values with `******`), but always be careful about exposing this endpoint.

---

## 28.8 The Loggers Endpoint

The loggers endpoint lets you view and change log levels at runtime. This is incredibly useful for debugging production issues without restarting the application.

### View All Loggers

```bash
curl http://localhost:8080/actuator/loggers
```

**Output (abbreviated):**

```json
{
  "levels": ["OFF", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"],
  "loggers": {
    "ROOT": {
      "configuredLevel": "INFO",
      "effectiveLevel": "INFO"
    },
    "com.example.bookstore": {
      "configuredLevel": null,
      "effectiveLevel": "INFO"
    },
    "com.example.bookstore.service.BookService": {
      "configuredLevel": null,
      "effectiveLevel": "INFO"
    }
  }
}
```

### View a Specific Logger

```bash
curl http://localhost:8080/actuator/loggers/com.example.bookstore
```

**Output:**

```json
{
  "configuredLevel": null,
  "effectiveLevel": "INFO"
}
```

### Change Log Level at Runtime

This is the killer feature. You can change log levels without restarting your application.

```bash
# Change to DEBUG level
curl -X POST http://localhost:8080/actuator/loggers/com.example.bookstore \
  -H "Content-Type: application/json" \
  -d '{"configuredLevel": "DEBUG"}'
```

Now your application logs DEBUG messages for `com.example.bookstore`.

```bash
# Reset to default
curl -X POST http://localhost:8080/actuator/loggers/com.example.bookstore \
  -H "Content-Type: application/json" \
  -d '{"configuredLevel": null}'
```

```
Changing Log Level at Runtime:

Before:                                After POST:
+-----------------------+             +-----------------------+
| Logger: bookstore     |             | Logger: bookstore     |
| Level: INFO           |             | Level: DEBUG          |
|                       |             |                       |
| Shows: INFO, WARN,    |   POST -->  | Shows: DEBUG, INFO,   |
|        ERROR          |             |        WARN, ERROR    |
| Hides: DEBUG, TRACE   |             | Hides: TRACE          |
+-----------------------+             +-----------------------+

No restart needed! Change takes effect immediately.
```

---

## 28.9 Creating a Custom HealthIndicator

The built-in health indicators check standard components like databases and disk space. But what about your own dependencies? Maybe your app depends on an external payment API or a file storage service. You can create custom health indicators to check those.

### Example: Checking an External API

```java
// src/main/java/com/example/bookstore/health/PaymentServiceHealthIndicator.java

package com.example.bookstore.health;

import org.springframework.boot.actuate.health.Health;           // 1
import org.springframework.boot.actuate.health.HealthIndicator;  // 2
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component                                                       // 3
public class PaymentServiceHealthIndicator
    implements HealthIndicator {                                  // 4

    @Override
    public Health health() {                                     // 5

        try {
            // Try to reach the payment service
            RestTemplate restTemplate = new RestTemplate();
            restTemplate.getForObject(                           // 6
                "https://api.payment-service.com/health",
                String.class
            );

            return Health.up()                                   // 7
                .withDetail("service", "Payment API")            // 8
                .withDetail("status", "Reachable")
                .build();

        } catch (Exception e) {
            return Health.down()                                 // 9
                .withDetail("service", "Payment API")
                .withDetail("error", e.getMessage())             // 10
                .build();
        }
    }
}
```

**Line-by-line explanation:**

- **Line 1**: Import `Health`, the builder class for health status.
- **Line 2**: Import `HealthIndicator`, the interface you implement.
- **Line 3**: `@Component` registers this as a Spring bean so Actuator discovers it automatically.
- **Line 4**: Implement `HealthIndicator`. You must override one method: `health()`.
- **Line 5**: This method is called every time someone hits `/actuator/health`.
- **Line 6**: Try to call the external service.
- **Line 7**: If successful, return `Health.up()` (healthy).
- **Line 8**: `withDetail()` adds extra information to the health response.
- **Line 9**: If the call fails, return `Health.down()` (unhealthy).
- **Line 10**: Include the error message so operators know what went wrong.

**Output when the payment service is healthy:**

```json
{
  "status": "UP",
  "components": {
    "db": { "status": "UP" },
    "diskSpace": { "status": "UP" },
    "paymentService": {
      "status": "UP",
      "details": {
        "service": "Payment API",
        "status": "Reachable"
      }
    }
  }
}
```

**Output when the payment service is down:**

```json
{
  "status": "DOWN",
  "components": {
    "db": { "status": "UP" },
    "diskSpace": { "status": "UP" },
    "paymentService": {
      "status": "DOWN",
      "details": {
        "service": "Payment API",
        "error": "Connection refused"
      }
    }
  }
}
```

Notice: The overall status becomes "DOWN" because one component is down.

### Example: Checking Disk Space Threshold

```java
@Component
public class StorageHealthIndicator implements HealthIndicator {

    private static final long MIN_FREE_SPACE =
        1024 * 1024 * 500;  // 500 MB

    @Override
    public Health health() {
        File root = new File("/");
        long freeSpace = root.getFreeSpace();

        if (freeSpace >= MIN_FREE_SPACE) {
            return Health.up()
                .withDetail("freeSpace",
                    freeSpace / (1024 * 1024) + " MB")
                .withDetail("threshold",
                    MIN_FREE_SPACE / (1024 * 1024) + " MB")
                .build();
        } else {
            return Health.down()
                .withDetail("freeSpace",
                    freeSpace / (1024 * 1024) + " MB")
                .withDetail("error",
                    "Free space below threshold")
                .build();
        }
    }
}
```

---

## 28.10 Creating a Custom InfoContributor

Just as you can create custom health indicators, you can add custom information to the info endpoint.

```java
// src/main/java/com/example/bookstore/info/BookStoreInfoContributor.java

package com.example.bookstore.info;

import com.example.bookstore.repository.BookRepository;
import org.springframework.boot.actuate.info.Info;            // 1
import org.springframework.boot.actuate.info.InfoContributor; // 2
import org.springframework.stereotype.Component;

@Component
public class BookStoreInfoContributor
    implements InfoContributor {                               // 3

    private final BookRepository bookRepository;

    public BookStoreInfoContributor(
            BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    @Override
    public void contribute(Info.Builder builder) {            // 4

        builder.withDetail("bookstore",                       // 5
            java.util.Map.of(
                "totalBooks", bookRepository.count(),          // 6
                "status", "operational",
                "supportEmail", "support@bookstore.com"
            )
        );
    }
}
```

**Line-by-line explanation:**

- **Line 1-2**: Import the `Info` builder and `InfoContributor` interface.
- **Line 3**: Implement `InfoContributor`. You must override `contribute()`.
- **Line 4**: The `contribute` method receives an `Info.Builder` that you add data to.
- **Line 5**: `withDetail("bookstore", ...)` adds a "bookstore" section to the info output.
- **Line 6**: Query the actual database for the book count.

**Output:**

```bash
curl http://localhost:8080/actuator/info
```

```json
{
  "app": {
    "name": "BookStore API",
    "version": "1.0.0"
  },
  "bookstore": {
    "totalBooks": 42,
    "status": "operational",
    "supportEmail": "support@bookstore.com"
  }
}
```

---

## 28.11 Securing Actuator Endpoints

Actuator endpoints can expose sensitive information. In production, you must secure them.

### Option 1: Change the Actuator Base Path

```properties
# application.properties

# Move actuator to a non-obvious path
management.endpoints.web.base-path=/internal/monitor
```

Now endpoints are at `/internal/monitor/health` instead of `/actuator/health`. This hides them from casual discovery but is **not real security** (security through obscurity).

### Option 2: Use a Different Port

```properties
# application.properties

# Run actuator on a different port
management.server.port=9090
```

Now your API runs on port 8080 and Actuator runs on port 9090. You can configure your firewall to block port 9090 from the internet while allowing internal monitoring tools to access it.

```
Two-Port Setup:

Internet Users:
+--------+     +------------------+
| Users  |---->| Port 8080        |     Actuator endpoints
|        |     | /api/books       |     are NOT accessible
|        |     | /api/authors     |     from port 8080
+--------+     +------------------+

Internal Monitoring:
+-----------+     +------------------+
| Monitoring|---->| Port 9090        |
| System    |     | /actuator/health |
| (internal)|     | /actuator/metrics|
+-----------+     +------------------+
```

### Option 3: Secure with Spring Security

If you have Spring Security in your project, you can restrict access to Actuator endpoints:

```java
// src/main/java/com/example/bookstore/config/SecurityConfig.java

package com.example.bookstore.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders
    .HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http) throws Exception {

        http
            .authorizeHttpRequests(auth -> auth
                // Public API endpoints
                .requestMatchers("/api/**").permitAll()

                // Health endpoint is public
                // (for load balancers)
                .requestMatchers(
                    "/actuator/health").permitAll()

                // All other actuator endpoints require
                // ADMIN role
                .requestMatchers(
                    "/actuator/**").hasRole("ADMIN")

                .anyRequest().authenticated()
            )
            .httpBasic(httpBasic -> {});  // Basic auth for actuator

        return http.build();
    }
}
```

```properties
# application.properties

# Admin user for actuator access
spring.security.user.name=admin
spring.security.user.password=secretPassword
spring.security.user.roles=ADMIN
```

Now:
- `/actuator/health` is accessible without authentication (needed by load balancers).
- All other `/actuator/**` endpoints require the ADMIN role.

### Option 4: Only Expose What You Need

The simplest security measure is to only expose the endpoints you actually use:

```properties
# application.properties

# Only expose health and info (safest option)
management.endpoints.web.exposure.include=health,info

# Show health details only to authorized users
management.endpoint.health.show-details=when-authorized
```

---

## 28.12 Recommended Production Configuration

Here is a complete, production-ready Actuator configuration:

```properties
# application-prod.properties

# Expose only necessary endpoints
management.endpoints.web.exposure.include=health,info,metrics,loggers

# Health endpoint configuration
management.endpoint.health.show-details=when-authorized
management.endpoint.health.show-components=when-authorized

# Run on a separate port (optional, for firewall control)
management.server.port=9090

# Customize the base path
management.endpoints.web.base-path=/actuator

# Info endpoint
management.info.env.enabled=true
info.app.name=BookStore API
info.app.version=@project.version@
info.app.environment=production
```

```properties
# application-dev.properties

# In development, expose everything
management.endpoints.web.exposure.include=*
management.endpoint.health.show-details=always
```

---

## Common Mistakes

### Mistake 1: Exposing All Endpoints in Production

```properties
# WRONG: Exposes sensitive data to the internet
management.endpoints.web.exposure.include=*
```

```properties
# CORRECT: Only expose what you need
management.endpoints.web.exposure.include=health,info,metrics
```

### Mistake 2: Showing Health Details to Everyone

```properties
# WRONG: Anyone can see your database details
management.endpoint.health.show-details=always
```

```properties
# CORRECT: Only show to authorized users in production
management.endpoint.health.show-details=when-authorized
```

### Mistake 3: Not Adding Actuator at All

Many developers skip Actuator. Then when their application goes down in production, they have no way to diagnose the problem. Always add Actuator. It costs nothing and provides invaluable monitoring.

### Mistake 4: Custom Health Checks That Are Too Slow

```java
// WRONG: Health check takes 30 seconds
@Override
public Health health() {
    // This call takes 30 seconds if the service is slow
    restTemplate.getForObject("https://slow-api.com/check",
                              String.class);
    return Health.up().build();
}
```

```java
// CORRECT: Set a timeout on the health check
@Override
public Health health() {
    try {
        // 3-second timeout
        RequestConfig config = RequestConfig.custom()
            .setConnectTimeout(Timeout.ofSeconds(3))
            .build();
        // ... use the config with your HTTP client
        return Health.up().build();
    } catch (Exception e) {
        return Health.down()
            .withDetail("error", "Timeout after 3 seconds")
            .build();
    }
}
```

### Mistake 5: Not Understanding When Health Returns DOWN

```
Overall Status Logic:

Component 1: UP    \
Component 2: UP     >  Overall: UP (all components up)
Component 3: UP    /

Component 1: UP    \
Component 2: DOWN   >  Overall: DOWN (one component down!)
Component 3: UP    /

If ANY component is DOWN, the overall status is DOWN.
This can trigger alerts and kill your load balancer routing.
Make sure your custom health checks are accurate!
```

---

## Best Practices

1. **Always add Actuator.** It is free, lightweight, and essential for production monitoring. There is no good reason to skip it.

2. **Expose only necessary endpoints in production.** Use `management.endpoints.web.exposure.include` to whitelist specific endpoints.

3. **Secure sensitive endpoints.** Use Spring Security, a separate port, or both to protect endpoints like env, beans, and loggers.

4. **Keep the health endpoint public.** Load balancers and orchestrators (like Kubernetes) need `/actuator/health` to be accessible without authentication.

5. **Create custom health indicators for external dependencies.** If your app depends on an external service, add a health check for it.

6. **Use the loggers endpoint for production debugging.** When you need to debug an issue, change the log level to DEBUG at runtime instead of redeploying.

7. **Add build info to the info endpoint.** This tells you exactly which version is deployed, which is invaluable when debugging.

8. **Set timeouts on custom health checks.** A slow health check can make your entire health endpoint slow, affecting load balancer decisions.

---

## Quick Summary

In this chapter, you learned how to monitor your Spring Boot application with Actuator. You added the `spring-boot-starter-actuator` dependency and immediately got a `/actuator/health` endpoint. You exposed additional endpoints like metrics, env, loggers, and info. You explored the health endpoint in detail, seeing how Spring Boot automatically checks your database and disk space. You used the metrics endpoint to monitor JVM memory, CPU usage, and HTTP request statistics. You changed log levels at runtime using the loggers endpoint. You created custom health indicators to monitor external dependencies and custom info contributors to expose application-specific data. Finally, you learned how to secure Actuator endpoints in production using separate ports, Spring Security, and selective endpoint exposure.

---

## Key Points

| Concept | Description |
|---|---|
| `spring-boot-starter-actuator` | Adds monitoring endpoints to your application |
| `/actuator/health` | Shows whether the application and its dependencies are healthy |
| `/actuator/info` | Shows application information (version, build time, etc.) |
| `/actuator/metrics` | Shows numerical measurements (memory, CPU, requests) |
| `/actuator/env` | Shows environment properties and their sources |
| `/actuator/loggers` | Shows and changes log levels at runtime |
| `management.endpoints.web.exposure.include` | Controls which endpoints are exposed over HTTP |
| `management.endpoint.health.show-details` | Controls whether health details are shown |
| `HealthIndicator` | Interface for creating custom health checks |
| `InfoContributor` | Interface for adding custom data to the info endpoint |
| `management.server.port` | Runs Actuator on a separate port |

---

## Practice Questions

1. What is Spring Boot Actuator and why is it important for production applications?

2. Why are only the health and info endpoints exposed by default? What security risk exists if you expose all endpoints?

3. How do you create a custom `HealthIndicator`? What happens to the overall health status when one component returns DOWN?

4. How can you change the log level of a specific package at runtime without restarting the application?

5. Describe three different strategies for securing Actuator endpoints in production.

---

## Exercises

### Exercise 1: Custom Health Indicator

Create a custom `HealthIndicator` called `DatabaseStorageHealthIndicator` that:
- Queries the `books` table and counts the total number of books.
- Returns UP if there are fewer than 10,000 books.
- Returns DOWN (with a warning) if there are 10,000 or more books, indicating the database storage might be running low.
- Returns DOWN if the count query fails.

### Exercise 2: Application Dashboard

Create a custom `InfoContributor` that exposes the following information at `/actuator/info`:
- Total number of books in the database.
- Total number of authors.
- The most expensive book title and price.
- Application uptime.

Test it by adding books and verifying the info endpoint updates.

### Exercise 3: Production Configuration

Create a complete Actuator configuration for three environments:
- **dev**: All endpoints exposed, health details always shown, same port as the application.
- **staging**: Health, info, metrics, and loggers exposed. Health details shown when authorized. Same port.
- **prod**: Only health and info exposed. Health details shown when authorized. Separate management port (9090). Endpoints secured with Spring Security.

Test each profile and verify the correct endpoints are accessible.

---

## What Is Next?

You now know how to monitor your application in production. But how do you manage configuration across different environments? How do you handle secrets like database passwords? In the next chapter, we will learn about **Externalized Configuration**. You will discover how Spring Boot lets you configure your application differently for development, staging, and production without changing any code.
