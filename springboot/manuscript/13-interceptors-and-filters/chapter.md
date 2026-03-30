# Chapter 13: Interceptors and Filters

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand how HTTP requests travel through a Spring Boot application
- Create custom servlet filters using `OncePerRequestFilter`
- Build handler interceptors with `preHandle`, `postHandle`, and `afterCompletion`
- Know when to use a filter versus an interceptor
- Implement request logging that tracks every incoming request
- Measure request processing time for performance monitoring

## Why This Chapter Matters

Imagine you work at a large office building. Before anyone reaches their meeting room, they must pass through several checkpoints. First, the security guard at the front door checks their ID. Then, the receptionist logs their visit in a book. Finally, a floor guide directs them to the correct room.

HTTP requests in a Spring Boot application work the same way. Before a request reaches your controller method, it can pass through **filters** and **interceptors**. These are checkpoints that can inspect, modify, log, or even reject requests before they arrive at their destination.

This matters because real applications need cross-cutting concerns. You need to log every request for debugging. You need to measure response times for performance. You need to check authentication tokens. You need to add security headers. Filters and interceptors let you do all of this without cluttering your controller code.

---

## The Request Lifecycle

Before we write any code, let us understand the complete journey of an HTTP request through a Spring Boot application.

```
+------------------------------------------------------------------+
|                        CLIENT (Browser/Postman)                   |
|                     Sends HTTP Request (GET /api/products)        |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                      EMBEDDED TOMCAT SERVER                       |
|                   (Receives the raw HTTP request)                 |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                     SERVLET FILTER CHAIN                          |
|  +------------------------------------------------------------+  |
|  |  Filter 1 (e.g., CharacterEncodingFilter)                  |  |
|  |    |                                                        |  |
|  |    v                                                        |  |
|  |  Filter 2 (e.g., Your Custom LoggingFilter)                |  |
|  |    |                                                        |  |
|  |    v                                                        |  |
|  |  Filter 3 (e.g., SecurityFilter)                           |  |
|  +------------------------------------------------------------+  |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                     DISPATCHER SERVLET                            |
|              (Spring's front controller - routes requests)        |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                   HANDLER INTERCEPTOR CHAIN                       |
|  +------------------------------------------------------------+  |
|  |  preHandle()   -->  Runs BEFORE the controller              |  |
|  +------------------------------------------------------------+  |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                        CONTROLLER METHOD                          |
|                   @GetMapping("/api/products")                    |
|                   public List<Product> getAll()                   |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                   HANDLER INTERCEPTOR CHAIN                       |
|  +------------------------------------------------------------+  |
|  |  postHandle()  -->  Runs AFTER controller, BEFORE view      |  |
|  +------------------------------------------------------------+  |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                     VIEW RESOLUTION (if any)                      |
|                  (For REST APIs, JSON serialization)              |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                   HANDLER INTERCEPTOR CHAIN                       |
|  +------------------------------------------------------------+  |
|  |  afterCompletion() --> Runs AFTER everything is done        |  |
|  +------------------------------------------------------------+  |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                  SERVLET FILTER CHAIN (Reverse)                   |
|               (Each filter's post-processing runs)               |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                        CLIENT (Browser/Postman)                   |
|                     Receives HTTP Response                        |
+------------------------------------------------------------------+
```

Think of it like an airport:

- **Filters** are the airport security checkpoints. Everyone goes through them, no matter which gate (controller) they are heading to.
- **DispatcherServlet** is the flight information board that tells you which gate to go to.
- **Interceptors** are the gate agents who check your boarding pass right before you board the plane.

---

## Part 1: Servlet Filters with OncePerRequestFilter

### What Is a Servlet Filter?

A servlet filter sits between the client and the DispatcherServlet. It can inspect or modify the request and response at the lowest level. Every HTTP request passes through filters, regardless of which controller handles it.

Spring provides `OncePerRequestFilter` as a convenient base class. As the name suggests, it guarantees your filter logic runs exactly once per request. This is important because in some setups, a request might pass through the filter chain multiple times due to internal forwards or includes.

### Creating a Request Logging Filter

Let us create a filter that logs every incoming HTTP request with its method, URL, and processing time.

**Step 1: Create the filter class**

```java
package com.example.demo.filter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component                                                    // Line 1
@Order(1)                                                     // Line 2
public class RequestLoggingFilter extends OncePerRequestFilter { // Line 3

    private static final Logger logger =
        LoggerFactory.getLogger(RequestLoggingFilter.class);  // Line 4

    @Override
    protected void doFilterInternal(                          // Line 5
            HttpServletRequest request,                       // Line 6
            HttpServletResponse response,                     // Line 7
            FilterChain filterChain                           // Line 8
    ) throws ServletException, IOException {

        // Code that runs BEFORE the request is processed
        long startTime = System.currentTimeMillis();          // Line 9
        String method = request.getMethod();                  // Line 10
        String uri = request.getRequestURI();                 // Line 11
        String queryString = request.getQueryString();        // Line 12

        logger.info("FILTER START => {} {} {}",
            method, uri,
            queryString != null ? "?" + queryString : "");    // Line 13

        // Pass the request to the next filter or controller
        filterChain.doFilter(request, response);              // Line 14

        // Code that runs AFTER the response is ready
        long duration = System.currentTimeMillis() - startTime; // Line 15
        int status = response.getStatus();                    // Line 16

        logger.info("FILTER END   <= {} {} | Status: {} | Time: {}ms",
            method, uri, status, duration);                   // Line 17
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `@Component` | Registers this filter as a Spring bean so Spring automatically adds it to the filter chain |
| 2 | `@Order(1)` | Sets the priority of this filter. Lower numbers run first. If you have multiple filters, this controls the order |
| 3 | `extends OncePerRequestFilter` | Inherits from Spring's base filter class that guarantees single execution per request |
| 4 | `LoggerFactory.getLogger(...)` | Creates a logger instance for this class. We use SLF4J for logging instead of `System.out.println` |
| 5 | `doFilterInternal(...)` | The main method you override. This is where your filter logic goes |
| 6 | `HttpServletRequest request` | The incoming HTTP request object. Contains method, URL, headers, body, and more |
| 7 | `HttpServletResponse response` | The outgoing HTTP response object. Contains status code, headers, and body |
| 8 | `FilterChain filterChain` | The chain of remaining filters. You must call `doFilter` to pass the request along |
| 9 | `System.currentTimeMillis()` | Records the start time so we can calculate how long the request took |
| 10 | `request.getMethod()` | Gets the HTTP method (GET, POST, PUT, DELETE) |
| 11 | `request.getRequestURI()` | Gets the request path (e.g., `/api/products`) |
| 12 | `request.getQueryString()` | Gets query parameters (e.g., `name=phone&page=1`) |
| 13 | `logger.info(...)` | Logs the request details before processing |
| 14 | `filterChain.doFilter(request, response)` | **Critical line!** Passes the request to the next filter or to the DispatcherServlet. Without this line, the request stops here |
| 15 | `System.currentTimeMillis() - startTime` | Calculates total processing time after the response is ready |
| 16 | `response.getStatus()` | Gets the HTTP status code (200, 404, 500, etc.) |
| 17 | `logger.info(...)` | Logs the response details after processing |

**How filterChain.doFilter() works:**

```
Your Filter Code (before doFilter)
        |
        v
filterChain.doFilter(request, response)  -----> Next Filter / Controller
        |                                              |
        |     <-- control returns after processing --  |
        v
Your Filter Code (after doFilter)
```

Think of `filterChain.doFilter()` like passing a baton in a relay race. You do your work, pass the baton, wait for everyone else to finish, and then do any cleanup work.

### Creating a Simple Controller to Test

```java
package com.example.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    @GetMapping
    public List<Map<String, Object>> getAllProducts() {
        return List.of(
            Map.of("id", 1, "name", "Laptop", "price", 999.99),
            Map.of("id", 2, "name", "Phone", "price", 699.99)
        );
    }

    @GetMapping("/{id}")
    public Map<String, Object> getProduct(@PathVariable int id) {
        return Map.of("id", id, "name", "Laptop", "price", 999.99);
    }
}
```

### Testing the Filter

When you send a GET request to `http://localhost:8080/api/products`, you will see this in the console:

```
INFO  c.e.d.filter.RequestLoggingFilter : FILTER START => GET /api/products
INFO  c.e.d.filter.RequestLoggingFilter : FILTER END   <= GET /api/products | Status: 200 | Time: 45ms
```

When you send a GET request to `http://localhost:8080/api/products/1`:

```
INFO  c.e.d.filter.RequestLoggingFilter : FILTER START => GET /api/products/1
INFO  c.e.d.filter.RequestLoggingFilter : FILTER END   <= GET /api/products/1 | Status: 200 | Time: 12ms
```

### Excluding Certain URLs from the Filter

Sometimes you do not want a filter to run for every request. For example, you might want to skip logging for health check endpoints or static resources.

```java
@Component
@Order(1)
public class RequestLoggingFilter extends OncePerRequestFilter {

    private static final Logger logger =
        LoggerFactory.getLogger(RequestLoggingFilter.class);

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getRequestURI();
        // Skip filtering for these paths
        return path.startsWith("/actuator")
            || path.startsWith("/health")
            || path.endsWith(".css")
            || path.endsWith(".js");
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {
        long startTime = System.currentTimeMillis();
        logger.info("=> {} {}", request.getMethod(), request.getRequestURI());

        filterChain.doFilter(request, response);

        long duration = System.currentTimeMillis() - startTime;
        logger.info("<= {} {} | {}ms",
            request.getMethod(), request.getRequestURI(), duration);
    }
}
```

The `shouldNotFilter()` method returns `true` for paths that should skip this filter entirely.

### Adding a Custom Response Header Filter

Here is another practical filter that adds a custom header to every response:

```java
package com.example.demo.filter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

@Component
@Order(2)
public class CorrelationIdFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        // Check if client sent a correlation ID
        String correlationId = request.getHeader("X-Correlation-Id");

        // If not, generate one
        if (correlationId == null || correlationId.isEmpty()) {
            correlationId = UUID.randomUUID().toString();
        }

        // Add it to the response so the client can see it
        response.setHeader("X-Correlation-Id", correlationId);

        filterChain.doFilter(request, response);
    }
}
```

A correlation ID is a unique identifier attached to each request. It helps you trace a single request across multiple services and log files. Think of it like a tracking number for a package.

**Output (Response Headers):**

```
HTTP/1.1 200 OK
X-Correlation-Id: 3f7a8b2c-1234-5678-abcd-ef0123456789
Content-Type: application/json
```

---

## Part 2: Handler Interceptors

### What Is a Handler Interceptor?

A handler interceptor sits between the DispatcherServlet and your controller. Unlike filters, interceptors are part of the Spring MVC framework and have access to Spring-specific information like which controller method will handle the request.

```
+------------------+     +---------------------+     +------------------+
|  Servlet Filter  | --> | DispatcherServlet   | --> | HandlerInterceptor|
|  (Low level)     |     | (Spring's Router)   |     | (Spring MVC)     |
|                  |     |                     |     |                  |
| Has access to:   |     |                     |     | Has access to:   |
| - Raw request    |     |                     |     | - Raw request    |
| - Raw response   |     |                     |     | - Raw response   |
| - Filter chain   |     |                     |     | - Handler method |
|                  |     |                     |     | - ModelAndView   |
|                  |     |                     |     | - Exception info |
+------------------+     +---------------------+     +------------------+
```

### The Three Methods of HandlerInterceptor

```
         Request arrives
              |
              v
    +-------------------+
    |   preHandle()     |    Runs BEFORE the controller
    |   return true?    |----- false ----> Request stops here
    +--------+----------+
             | true
             v
    +-------------------+
    |    Controller      |    Your @GetMapping / @PostMapping method
    |    Method runs     |
    +--------+----------+
             |
             v
    +-------------------+
    |   postHandle()    |    Runs AFTER controller, BEFORE response
    |                   |    Only if controller succeeded
    +--------+----------+
             |
             v
    +-------------------+
    |  afterCompletion()|    ALWAYS runs, even if an exception occurred
    |                   |    Good for cleanup (like a finally block)
    +-------------------+
             |
             v
      Response sent to client
```

### Creating a Handler Interceptor

**Step 1: Create the interceptor class**

```java
package com.example.demo.interceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;

@Component                                                    // Line 1
public class PerformanceInterceptor implements HandlerInterceptor { // Line 2

    private static final Logger logger =
        LoggerFactory.getLogger(PerformanceInterceptor.class);

    @Override
    public boolean preHandle(                                 // Line 3
            HttpServletRequest request,
            HttpServletResponse response,
            Object handler                                    // Line 4
    ) throws Exception {

        // Store the start time as a request attribute
        request.setAttribute("startTime",
            System.currentTimeMillis());                      // Line 5

        // Log which controller method will handle this request
        if (handler instanceof HandlerMethod handlerMethod) { // Line 6
            String className = handlerMethod
                .getBeanType().getSimpleName();                // Line 7
            String methodName = handlerMethod
                .getMethod().getName();                        // Line 8
            logger.info("INTERCEPTOR preHandle => {}.{}()",
                className, methodName);                        // Line 9
        }

        return true;                                          // Line 10
    }

    @Override
    public void postHandle(                                   // Line 11
            HttpServletRequest request,
            HttpServletResponse response,
            Object handler,
            ModelAndView modelAndView                          // Line 12
    ) throws Exception {
        logger.info("INTERCEPTOR postHandle => Response status: {}",
            response.getStatus());
    }

    @Override
    public void afterCompletion(                              // Line 13
            HttpServletRequest request,
            HttpServletResponse response,
            Object handler,
            Exception ex                                      // Line 14
    ) throws Exception {

        long startTime = (Long) request.getAttribute("startTime"); // Line 15
        long duration = System.currentTimeMillis() - startTime;

        if (ex != null) {                                     // Line 16
            logger.error(
                "INTERCEPTOR afterCompletion => FAILED in {}ms. Error: {}",
                duration, ex.getMessage());
        } else {
            logger.info(
                "INTERCEPTOR afterCompletion => Completed in {}ms",
                duration);                                    // Line 17
        }
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `@Component` | Registers the interceptor as a Spring bean |
| 2 | `implements HandlerInterceptor` | Implements Spring's interceptor interface which defines the three callback methods |
| 3 | `preHandle(...)` | Called before the controller method. Returns `boolean` to control whether the request should continue |
| 4 | `Object handler` | The handler that will process the request. Usually a `HandlerMethod` that wraps your controller method |
| 5 | `request.setAttribute(...)` | Stores data in the request that can be retrieved later. Think of it as a sticky note you attach to the request |
| 6 | `handler instanceof HandlerMethod` | Checks if the handler is a controller method (it could also be a static resource handler). Uses Java 16+ pattern matching |
| 7 | `getBeanType().getSimpleName()` | Gets the controller class name (e.g., `ProductController`) |
| 8 | `getMethod().getName()` | Gets the method name (e.g., `getAllProducts`) |
| 9 | `logger.info(...)` | Logs which controller method will handle this request |
| 10 | `return true` | Returning `true` means "continue processing." Returning `false` would stop the request here |
| 11 | `postHandle(...)` | Called after the controller method runs successfully but before the response is committed |
| 12 | `ModelAndView modelAndView` | The model and view returned by the controller. For REST APIs, this is usually `null` |
| 13 | `afterCompletion(...)` | Always called after the complete request is finished, even if an exception occurred |
| 14 | `Exception ex` | If the controller threw an exception, it is passed here. Otherwise `null` |
| 15 | `request.getAttribute(...)` | Retrieves the start time we stored in `preHandle` |
| 16 | `if (ex != null)` | Checks whether an error occurred during processing |
| 17 | `logger.info(...)` | Logs the total time taken for the request |

**Step 2: Register the interceptor**

Unlike filters, interceptors must be explicitly registered with Spring MVC through a configuration class.

```java
package com.example.demo.config;

import com.example.demo.interceptor.PerformanceInterceptor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration                                               // Line 1
public class WebConfig implements WebMvcConfigurer {          // Line 2

    private final PerformanceInterceptor performanceInterceptor;

    public WebConfig(PerformanceInterceptor performanceInterceptor) {
        this.performanceInterceptor = performanceInterceptor; // Line 3
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) { // Line 4
        registry.addInterceptor(performanceInterceptor)       // Line 5
                .addPathPatterns("/api/**")                    // Line 6
                .excludePathPatterns("/api/health");           // Line 7
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `@Configuration` | Marks this as a configuration class that Spring processes at startup |
| 2 | `implements WebMvcConfigurer` | Provides callback methods to customize Spring MVC configuration |
| 3 | Constructor injection | Spring automatically injects the `PerformanceInterceptor` bean |
| 4 | `addInterceptors(...)` | Override this method to register your interceptors |
| 5 | `registry.addInterceptor(...)` | Adds your interceptor to the chain |
| 6 | `.addPathPatterns("/api/**")` | This interceptor only runs for URLs starting with `/api/`. The `**` means any sub-path |
| 7 | `.excludePathPatterns(...)` | Skips the interceptor for the health endpoint |

### Testing the Interceptor

When you send a GET request to `http://localhost:8080/api/products`:

```
INFO  c.e.d.filter.RequestLoggingFilter       : FILTER START => GET /api/products
INFO  c.e.d.interceptor.PerformanceInterceptor : INTERCEPTOR preHandle => ProductController.getAllProducts()
INFO  c.e.d.interceptor.PerformanceInterceptor : INTERCEPTOR postHandle => Response status: 200
INFO  c.e.d.interceptor.PerformanceInterceptor : INTERCEPTOR afterCompletion => Completed in 32ms
INFO  c.e.d.filter.RequestLoggingFilter       : FILTER END   <= GET /api/products | Status: 200 | Time: 45ms
```

Notice the order: Filter starts first, then the interceptor runs, then the interceptor finishes, and finally the filter finishes. This is because filters wrap around the entire Spring MVC processing.

```
Filter Start
    Interceptor preHandle
        Controller Method
    Interceptor postHandle
    Interceptor afterCompletion
Filter End
```

### Using preHandle to Block Requests

One powerful use of `preHandle` is to block requests that do not meet certain criteria. For example, you could require a specific API key header:

```java
@Component
public class ApiKeyInterceptor implements HandlerInterceptor {

    private static final String API_KEY = "my-secret-key-123";

    @Override
    public boolean preHandle(
            HttpServletRequest request,
            HttpServletResponse response,
            Object handler
    ) throws Exception {

        String apiKey = request.getHeader("X-API-Key");

        if (apiKey == null || !apiKey.equals(API_KEY)) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.setContentType("application/json");
            response.getWriter().write(
                "{\"error\": \"Invalid or missing API key\"}"
            );
            return false;   // Stop! Do not proceed to the controller
        }

        return true;        // API key is valid, continue
    }
}
```

When `preHandle` returns `false`:
- The controller method is never called
- `postHandle` is never called
- `afterCompletion` IS still called (for cleanup)

---

## Part 3: Filter vs Interceptor Comparison

Now that you have seen both in action, here is a detailed comparison:

```
+-----------------------------+-------------------------------+-------------------------------+
|        Feature              |         Servlet Filter        |     Handler Interceptor       |
+-----------------------------+-------------------------------+-------------------------------+
| Part of                     | Servlet API (Jakarta EE)      | Spring MVC Framework          |
+-----------------------------+-------------------------------+-------------------------------+
| Scope                       | All requests (including       | Only requests handled by      |
|                             | static resources)             | Spring MVC controllers        |
+-----------------------------+-------------------------------+-------------------------------+
| When it runs                | Before DispatcherServlet      | After DispatcherServlet,      |
|                             |                               | before/after Controller       |
+-----------------------------+-------------------------------+-------------------------------+
| Access to handler info      | No                            | Yes (knows which controller   |
|                             |                               | method will run)              |
+-----------------------------+-------------------------------+-------------------------------+
| Access to ModelAndView      | No                            | Yes (in postHandle)           |
+-----------------------------+-------------------------------+-------------------------------+
| Access to exceptions        | No (must use try-catch)       | Yes (in afterCompletion)      |
+-----------------------------+-------------------------------+-------------------------------+
| Can modify request/response | Yes (can wrap them)           | Yes                           |
+-----------------------------+-------------------------------+-------------------------------+
| Registration                | @Component or @Bean           | WebMvcConfigurer +            |
|                             |                               | addInterceptors()             |
+-----------------------------+-------------------------------+-------------------------------+
| URL pattern control         | shouldNotFilter() or          | addPathPatterns() /           |
|                             | FilterRegistrationBean        | excludePathPatterns()         |
+-----------------------------+-------------------------------+-------------------------------+
| Best for                    | Security, CORS, encoding,     | Logging with controller info, |
|                             | compression, low-level tasks  | auth checks, performance      |
+-----------------------------+-------------------------------+-------------------------------+
```

### When to Use What

**Use a Filter when:**
- You need to process every request, including static resources
- You need to modify the raw request or response (e.g., wrapping them)
- You are working with non-Spring concerns (e.g., servlet-level security)
- You need to set response headers for all requests
- You are implementing CORS, encoding, or compression

**Use an Interceptor when:**
- You need to know which controller method will handle the request
- You need access to Spring MVC concepts like `ModelAndView`
- You want fine-grained URL pattern matching
- You need separate logic for before-controller, after-controller, and after-completion
- You want to access the exception that a controller threw

---

## Part 4: Complete Request Logging Example

Let us put everything together into a complete, production-ready request logging system that uses both a filter and an interceptor.

**Project structure:**

```
src/main/java/com/example/demo/
├── DemoApplication.java
├── config/
│   └── WebConfig.java
├── controller/
│   └── ProductController.java
├── filter/
│   └── RequestLoggingFilter.java
└── interceptor/
    └── RequestTimingInterceptor.java
```

**application.properties:**

```properties
# Application name
spring.application.name=interceptor-filter-demo

# Server port
server.port=8080

# Logging level for our packages
logging.level.com.example.demo=DEBUG
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

**RequestLoggingFilter.java:**

```java
package com.example.demo.filter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class RequestLoggingFilter extends OncePerRequestFilter {

    private static final Logger logger =
        LoggerFactory.getLogger(RequestLoggingFilter.class);

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getRequestURI();
        return path.contains("favicon")
            || path.startsWith("/actuator");
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        String method = request.getMethod();
        String uri = request.getRequestURI();
        String clientIp = request.getRemoteAddr();

        logger.info("========== REQUEST START ==========");
        logger.info("Method: {} | URI: {} | Client IP: {}",
            method, uri, clientIp);
        logger.info("Content-Type: {}",
            request.getContentType());
        logger.info("User-Agent: {}",
            request.getHeader("User-Agent"));

        long startTime = System.currentTimeMillis();

        try {
            filterChain.doFilter(request, response);
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            logger.info("Status: {} | Duration: {}ms",
                response.getStatus(), duration);
            logger.info("========== REQUEST END ============");
        }
    }
}
```

**RequestTimingInterceptor.java:**

```java
package com.example.demo.interceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;

@Component
public class RequestTimingInterceptor implements HandlerInterceptor {

    private static final Logger logger =
        LoggerFactory.getLogger(RequestTimingInterceptor.class);

    @Override
    public boolean preHandle(
            HttpServletRequest request,
            HttpServletResponse response,
            Object handler
    ) throws Exception {
        request.setAttribute("controllerStartTime",
            System.currentTimeMillis());

        if (handler instanceof HandlerMethod hm) {
            logger.debug("  -> Handler: {}.{}()",
                hm.getBeanType().getSimpleName(),
                hm.getMethod().getName());
        }

        return true;
    }

    @Override
    public void postHandle(
            HttpServletRequest request,
            HttpServletResponse response,
            Object handler,
            ModelAndView modelAndView
    ) throws Exception {
        if (handler instanceof HandlerMethod hm) {
            long startTime = (Long)
                request.getAttribute("controllerStartTime");
            long controllerTime =
                System.currentTimeMillis() - startTime;
            logger.debug("  -> Controller execution time: {}ms",
                controllerTime);
        }
    }

    @Override
    public void afterCompletion(
            HttpServletRequest request,
            HttpServletResponse response,
            Object handler,
            Exception ex
    ) throws Exception {
        if (ex != null) {
            logger.error("  -> Exception occurred: {}",
                ex.getMessage());
        }
    }
}
```

**WebConfig.java:**

```java
package com.example.demo.config;

import com.example.demo.interceptor.RequestTimingInterceptor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final RequestTimingInterceptor requestTimingInterceptor;

    public WebConfig(RequestTimingInterceptor requestTimingInterceptor) {
        this.requestTimingInterceptor = requestTimingInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(requestTimingInterceptor)
                .addPathPatterns("/api/**");
    }
}
```

**ProductController.java:**

```java
package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    @GetMapping
    public List<Map<String, Object>> getAllProducts() {
        return List.of(
            Map.of("id", 1, "name", "Laptop", "price", 999.99),
            Map.of("id", 2, "name", "Phone", "price", 699.99),
            Map.of("id", 3, "name", "Tablet", "price", 449.99)
        );
    }

    @GetMapping("/{id}")
    public Map<String, Object> getProductById(@PathVariable int id) {
        return Map.of("id", id, "name", "Laptop", "price", 999.99);
    }

    @PostMapping
    public Map<String, Object> createProduct(
            @RequestBody Map<String, Object> product) {
        product.put("id", 100);
        return product;
    }
}
```

### Complete Output

**GET http://localhost:8080/api/products**

```
INFO  c.e.d.filter.RequestLoggingFilter           : ========== REQUEST START ==========
INFO  c.e.d.filter.RequestLoggingFilter           : Method: GET | URI: /api/products | Client IP: 127.0.0.1
INFO  c.e.d.filter.RequestLoggingFilter           : Content-Type: null
INFO  c.e.d.filter.RequestLoggingFilter           : User-Agent: PostmanRuntime/7.36.0
DEBUG c.e.d.interceptor.RequestTimingInterceptor   :   -> Handler: ProductController.getAllProducts()
DEBUG c.e.d.interceptor.RequestTimingInterceptor   :   -> Controller execution time: 15ms
INFO  c.e.d.filter.RequestLoggingFilter           : Status: 200 | Duration: 42ms
INFO  c.e.d.filter.RequestLoggingFilter           : ========== REQUEST END ============
```

**Response body:**

```json
[
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Phone", "price": 699.99},
    {"id": 3, "name": "Tablet", "price": 449.99}
]
```

---

## Common Mistakes

### Mistake 1: Forgetting to Call filterChain.doFilter()

```java
// WRONG - Request gets stuck in the filter and never reaches the controller
@Override
protected void doFilterInternal(
        HttpServletRequest request,
        HttpServletResponse response,
        FilterChain filterChain
) throws ServletException, IOException {
    logger.info("Processing request...");
    // Oops! Forgot to call filterChain.doFilter()
    // The client will get an empty response
}

// CORRECT - Always call filterChain.doFilter() unless you intentionally
// want to block the request
@Override
protected void doFilterInternal(
        HttpServletRequest request,
        HttpServletResponse response,
        FilterChain filterChain
) throws ServletException, IOException {
    logger.info("Processing request...");
    filterChain.doFilter(request, response);  // Pass the request along!
}
```

### Mistake 2: Not Registering the Interceptor

```java
// WRONG - Creating the interceptor class but not registering it
// The interceptor exists but Spring MVC does not know about it
@Component
public class MyInterceptor implements HandlerInterceptor {
    // This alone is not enough!
}

// CORRECT - You must also register it in a WebMvcConfigurer
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(myInterceptor)
                .addPathPatterns("/**");  // Now it is registered!
    }
}
```

### Mistake 3: Modifying the Response After filterChain.doFilter()

```java
// WRONG - Setting headers after the response has been committed
@Override
protected void doFilterInternal(...) {
    filterChain.doFilter(request, response);
    response.setHeader("X-Custom", "value"); // May not work!
    // Response might already be sent to the client
}

// CORRECT - Set response headers BEFORE calling doFilter
@Override
protected void doFilterInternal(...) {
    response.setHeader("X-Custom", "value"); // Set before processing
    filterChain.doFilter(request, response);
}
```

### Mistake 4: Using Filter When You Need Controller Info

```java
// WRONG - Trying to get controller info in a filter
// Filters run BEFORE Spring MVC, so they do not know which
// controller will handle the request
@Override
protected void doFilterInternal(...) {
    // There is no way to know which controller method
    // will handle this request from a filter
}

// CORRECT - Use an interceptor when you need controller info
@Override
public boolean preHandle(HttpServletRequest request,
                         HttpServletResponse response,
                         Object handler) {
    if (handler instanceof HandlerMethod hm) {
        String methodName = hm.getMethod().getName(); // Works!
    }
    return true;
}
```

---

## Best Practices

1. **Use `OncePerRequestFilter` instead of `Filter`**: It prevents double execution in forwarded requests. Always extend `OncePerRequestFilter` unless you have a specific reason not to.

2. **Wrap `filterChain.doFilter()` in try-finally**: This ensures your cleanup code runs even if an exception occurs downstream.

3. **Keep filters and interceptors focused**: Each filter or interceptor should do one thing well. Do not create a single filter that does logging, authentication, and header modification all at once.

4. **Use `@Order` to control filter execution order**: When you have multiple filters, use `@Order` annotations to define a clear execution sequence. Lower numbers run first.

5. **Use interceptors for Spring-specific concerns**: If you need access to the handler method, `ModelAndView`, or Spring's exception handling, use an interceptor.

6. **Use `shouldNotFilter()` to exclude paths**: Do not add `if` statements inside `doFilterInternal`. Override `shouldNotFilter()` for cleaner code.

7. **Log at appropriate levels**: Use `DEBUG` for detailed information and `INFO` for important events. Do not log everything at `INFO` level in production.

8. **Be careful with request body reading**: Once you read the request body in a filter, the controller cannot read it again. If you need to read the body, wrap the request in a `ContentCachingRequestWrapper`.

---

## Quick Summary

```
+----------------------------------+
|  Filters and Interceptors        |
|  Quick Reference                 |
+----------------------------------+
|                                  |
|  FILTER (OncePerRequestFilter)   |
|  - Sits before DispatcherServlet |
|  - Processes ALL requests        |
|  - doFilterInternal() method     |
|  - Must call filterChain.doFilter|
|  - @Component + @Order           |
|  - Best for: logging, headers,   |
|    security, encoding            |
|                                  |
|  INTERCEPTOR (HandlerInterceptor)|
|  - Sits after DispatcherServlet  |
|  - Only Spring MVC requests      |
|  - preHandle() -> boolean        |
|  - postHandle() -> after ctrl    |
|  - afterCompletion() -> cleanup  |
|  - Register in WebMvcConfigurer  |
|  - Best for: controller-aware    |
|    logging, auth, timing         |
|                                  |
+----------------------------------+
```

---

## Key Points

1. **Filters** are part of the Servlet API and run before the DispatcherServlet. **Interceptors** are part of Spring MVC and run after the DispatcherServlet.

2. `OncePerRequestFilter` guarantees your filter logic runs exactly once per request, even with internal forwards.

3. You must call `filterChain.doFilter(request, response)` in a filter, or the request will never reach the controller.

4. Handler interceptors have three methods: `preHandle` (before controller), `postHandle` (after controller), and `afterCompletion` (always runs, like a finally block).

5. Returning `false` from `preHandle` stops the request from reaching the controller.

6. Interceptors must be registered in a `WebMvcConfigurer` implementation using `addInterceptors()`.

7. Filters are registered automatically with `@Component`, or manually with `FilterRegistrationBean` for more control.

---

## Practice Questions

1. What is the difference between a servlet filter and a handler interceptor? When would you choose one over the other?

2. What happens if you forget to call `filterChain.doFilter(request, response)` inside a filter?

3. Explain the three methods of `HandlerInterceptor`. When does each one run? Which one always runs regardless of exceptions?

4. How do you control the order in which multiple filters execute? How do you control interceptor order?

5. Why does Spring provide `OncePerRequestFilter` instead of just using the basic `Filter` interface?

---

## Exercises

### Exercise 1: Rate Limiting Interceptor

Create an interceptor that limits each client to 10 requests per minute. Store the request count in a `ConcurrentHashMap` using the client's IP address as the key. If the limit is exceeded, return a 429 (Too Many Requests) status code.

**Hints:**
- Use `request.getRemoteAddr()` to get the client IP
- Use `System.currentTimeMillis()` to track time windows
- Return `false` from `preHandle` to block the request

### Exercise 2: Request/Response Body Logging Filter

Create a filter that logs the request body for POST and PUT requests, and the response body for all requests. You will need to use `ContentCachingRequestWrapper` and `ContentCachingResponseWrapper` from Spring.

**Hints:**
- Wrap the request: `new ContentCachingRequestWrapper(request)`
- Wrap the response: `new ContentCachingResponseWrapper(response)`
- Read cached content after `filterChain.doFilter()` completes
- Call `response.copyBodyToResponse()` to ensure the client receives the response

### Exercise 3: Multi-Interceptor Chain

Create three interceptors: `AuthInterceptor`, `LoggingInterceptor`, and `TimingInterceptor`. Register them in a specific order and observe how they execute. Add logging to each method to verify the execution order matches your expectations.

---

## What Is Next?

Now that you understand how to intercept and process requests at different levels, it is time to work with data. In the next chapter, you will learn about **Spring Data JPA and H2** -- how to set up a database, create entity classes, and let Spring automatically create your database tables. This is where your applications start to store and retrieve real data.
