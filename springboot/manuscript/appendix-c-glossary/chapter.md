# Appendix C: Glossary of Spring Boot Terms

## What You Will Learn

- The definitions of 70+ terms used throughout this book.
- How each term relates to Spring Boot development.
- Where in the book each concept is covered in detail.

## Why This Chapter Matters

When you are learning a new technology, the hardest part is often the vocabulary. Spring Boot uses many terms that can be confusing when you first encounter them. This glossary gives you a single place to look up any term you come across in this book, in documentation, in tutorials, or in job interviews.

Think of this glossary as your Spring Boot dictionary. When you see a term you do not recognize, come here first. Each entry explains the term in plain English with a brief example where helpful.

---

## Terms

### @Autowired

An annotation that tells Spring to automatically inject (provide) a dependency. When Spring sees `@Autowired` on a constructor, field, or setter method, it looks for a matching bean in its container and provides it. In modern Spring Boot, constructor injection is preferred, and `@Autowired` is optional on single-constructor classes.

```java
@Service
public class OrderService {
    private final EmailService emailService;

    // @Autowired is optional here because there is only one constructor
    public OrderService(EmailService emailService) {
        this.emailService = emailService;
    }
}
```

See: Chapter 6 (Dependency Injection).

---

### @Bean

An annotation used on a method inside a `@Configuration` class. The method creates and returns an object, and Spring registers that object as a bean in the application context. Use `@Bean` when you need to configure a third-party library object that you cannot annotate with `@Component`.

```java
@Configuration
public class AppConfig {
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

See: Chapter 7 (Beans and Annotations).

---

### BCrypt

A password hashing algorithm designed for security. It is intentionally slow, which makes it resistant to brute-force attacks. Spring Security provides `BCryptPasswordEncoder` to hash and verify passwords. You should never store plain-text passwords.

See: Chapter 19 (Password Encoding and Roles).

---

### Bean

An object that is created and managed by the Spring IoC container. Beans are the building blocks of a Spring application. Spring creates them, injects their dependencies, and manages their lifecycle. Any class annotated with `@Component`, `@Service`, `@Repository`, or `@Controller` becomes a bean.

See: Chapter 7 (Beans and Annotations).

---

### @Cacheable

An annotation that caches the return value of a method. The first time the method is called with specific arguments, the result is stored in the cache. Subsequent calls with the same arguments return the cached result instead of executing the method again. Requires `@EnableCaching` on a configuration class.

```java
@Cacheable(value = "products", key = "#id")
public Product getProduct(Long id) {
    return productRepository.findById(id).orElseThrow();
}
```

See: Chapter 24 (Caching).

---

### @CacheEvict

An annotation that removes entries from the cache. Use this on methods that modify data to ensure the cache does not serve stale (outdated) values.

See: Chapter 24 (Caching).

---

### CommandLineRunner

A functional interface in Spring Boot. If you create a bean of this type, Spring Boot runs it automatically after the application starts. Useful for initializing sample data, running startup checks, or printing diagnostic information.

See: Appendix B (Complete Project).

---

### Component Scanning

The process by which Spring automatically discovers classes annotated with `@Component`, `@Service`, `@Repository`, `@Controller`, and other stereotype annotations. Spring scans the package of your main application class and all sub-packages. Any annotated class it finds becomes a bean in the application context.

See: Chapter 7 (Beans and Annotations).

---

### @Component

A generic annotation that marks a class as a Spring-managed bean. Spring creates an instance of this class and manages it. More specific versions include `@Service`, `@Repository`, and `@Controller`, which add semantic meaning.

See: Chapter 7 (Beans and Annotations).

---

### @Configuration

An annotation that marks a class as a source of bean definitions. Methods annotated with `@Bean` inside a `@Configuration` class produce beans managed by Spring. Configuration classes are where you set up third-party libraries, security rules, and custom components.

See: Chapter 7 (Beans and Annotations).

---

### @ControllerAdvice

An annotation that makes a class a global handler for exceptions thrown by any controller. Combined with `@ExceptionHandler` methods, it provides centralized error handling. `@RestControllerAdvice` is a convenience variant that adds `@ResponseBody` automatically.

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex) {
        return ResponseEntity.status(404)
            .body(new ErrorResponse(404, ex.getMessage()));
    }
}
```

See: Chapter 12 (Exception Handling).

---

### CORS (Cross-Origin Resource Sharing)

A security mechanism that controls which websites can make requests to your API. By default, browsers block requests from a different domain. CORS headers tell the browser which origins are allowed. Spring Boot provides `@CrossOrigin` and `WebMvcConfigurer` to configure CORS.

See: Chapter 20 (CORS Configuration).

---

### CRUD

An acronym for Create, Read, Update, Delete. These are the four basic operations for managing data. In Spring Boot, you implement CRUD through REST endpoints: POST (create), GET (read), PUT/PATCH (update), and DELETE (delete).

See: Chapter 15 (Repositories and CRUD).

---

### CSRF (Cross-Site Request Forgery)

A type of web attack where a malicious website tricks a user's browser into making an unwanted request to your application. Spring Security enables CSRF protection by default for form-based applications. For stateless REST APIs using JWT tokens, CSRF is typically disabled because the token itself prevents this type of attack.

See: Chapter 17 (Spring Security Introduction).

---

### DAO (Data Access Object)

A design pattern that provides an abstract interface to a database. In Spring Boot, the `@Repository` annotation marks a class as a DAO. Spring Data JPA repositories serve the same purpose with much less code.

See: Chapter 15 (Repositories and CRUD).

---

### @DeleteMapping

A shortcut annotation for `@RequestMapping(method = RequestMethod.DELETE)`. It maps HTTP DELETE requests to a specific controller method. Used for endpoints that delete resources.

See: Chapter 10 (Request and Response Handling).

---

### Dependency Injection (DI)

A design pattern where an object receives its dependencies from an external source instead of creating them itself. In Spring Boot, the framework creates objects (beans) and injects them where needed. This makes code easier to test and maintain because you can swap implementations without changing the dependent class.

See: Chapter 6 (Dependency Injection).

---

### DispatcherServlet

The front controller in Spring MVC. It receives all incoming HTTP requests and routes them to the correct controller method based on the URL, HTTP method, and other factors. Spring Boot configures the DispatcherServlet automatically. You rarely interact with it directly.

```
Client Request --> DispatcherServlet --> Controller --> Service --> Repository
```

See: Chapter 9 (Your First REST Controller).

---

### DTO (Data Transfer Object)

A simple Java object used to transfer data between layers of an application. DTOs separate the data sent to or received from clients from the internal entity structure. This improves security (you control what is exposed) and flexibility (you can change entities without breaking the API).

See: Chapter 10 (Request and Response Handling).

---

### @EnableCaching

An annotation that activates Spring's cache abstraction. Without this annotation, `@Cacheable` and `@CacheEvict` are ignored. Place it on a configuration class or the main application class.

See: Chapter 24 (Caching).

---

### @EnableScheduling

An annotation that enables Spring's scheduled task execution. Without this annotation, `@Scheduled` methods are ignored. Place it on a configuration class or the main application class.

See: Chapter 23 (Scheduling).

---

### @EnableWebSocketMessageBroker

An annotation that enables WebSocket message handling with a STOMP message broker. It sets up the infrastructure for WebSocket communication, including message routing and subscription management.

See: Appendix A (WebSocket).

---

### @Entity

A JPA annotation that marks a class as a database entity. Each entity maps to a table in the database. Each instance of the entity represents a row in that table. Fields in the entity class map to columns.

```java
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private double price;
}
```

See: Chapter 14 (Spring Data JPA and H2).

---

### @ExceptionHandler

An annotation on a method that handles a specific type of exception. When the specified exception is thrown, Spring calls this method instead of returning a default error page. Usually used inside a `@ControllerAdvice` class.

See: Chapter 12 (Exception Handling).

---

### Filter

A component that intercepts HTTP requests and responses before they reach a controller or after the controller processes them. Filters operate at the servlet level and are useful for cross-cutting concerns like logging, authentication, and CORS. Spring Security uses a chain of filters to enforce security.

See: Chapter 13 (Interceptors and Filters).

---

### @GetMapping

A shortcut annotation for `@RequestMapping(method = RequestMethod.GET)`. It maps HTTP GET requests to a specific controller method. Used for endpoints that retrieve data.

See: Chapter 9 (Your First REST Controller).

---

### H2 Database

A lightweight, in-memory relational database written in Java. It is embedded in your application (no separate installation needed) and perfect for development and testing. Spring Boot provides auto-configuration for H2, and it includes a web console for viewing data at `/h2-console`.

See: Chapter 14 (Spring Data JPA and H2).

---

### @Id

A JPA annotation that marks a field as the primary key of an entity. Every entity must have exactly one field annotated with `@Id`. Combined with `@GeneratedValue`, the database automatically assigns unique values.

See: Chapter 14 (Spring Data JPA and H2).

---

### Interceptor

A Spring MVC component that intercepts requests before and after controller execution. Unlike filters (which operate at the servlet level), interceptors operate at the Spring MVC level and have access to the handler method information. Implement `HandlerInterceptor` to create one.

See: Chapter 13 (Interceptors and Filters).

---

### IoC (Inversion of Control)

A design principle where the framework controls the creation and management of objects instead of the programmer. In traditional programming, your code creates objects. With IoC, the Spring container creates objects and gives them to your code. Dependency Injection is the most common way to implement IoC.

See: Chapter 6 (Dependency Injection).

---

### Jackson

A Java library for converting between Java objects and JSON. Spring Boot uses Jackson automatically to serialize (Java to JSON) controller responses and deserialize (JSON to Java) request bodies. You can customize Jackson behavior with annotations like `@JsonIgnore`, `@JsonProperty`, and `@JsonFormat`.

See: Chapter 10 (Request and Response Handling).

---

### Jakarta EE

The enterprise Java platform, formerly known as Java EE (Enterprise Edition). Spring Boot 3.x uses Jakarta EE APIs instead of the older javax packages. This means imports changed from `javax.persistence` to `jakarta.persistence` and from `javax.servlet` to `jakarta.servlet`.

See: Chapter 1 (What Is Spring Boot).

---

### JAR (Java Archive)

A file format that packages Java classes, resources, and metadata into a single compressed file. Spring Boot creates "fat JARs" (also called "uber JARs") that include your application code, all dependencies, and an embedded web server. You run them with `java -jar myapp.jar`.

See: Chapter 3 (Your First Spring Boot Project).

---

### JPA (Java Persistence API)

A specification for mapping Java objects to relational database tables. JPA defines annotations like `@Entity`, `@Table`, `@Column`, and `@Id`. Hibernate is the most popular implementation of JPA. Spring Data JPA builds on top of JPA to provide repositories with automatic query generation.

See: Chapter 14 (Spring Data JPA and H2).

---

### @JoinColumn

A JPA annotation that specifies the foreign key column for a relationship. Used with `@ManyToOne` and `@OneToOne` to define which column in the database links two tables together.

See: Chapter 14 (Spring Data JPA and H2).

---

### JSON (JavaScript Object Notation)

A lightweight data format used for exchanging data between a client and server. JSON uses key-value pairs and is easy for both humans and machines to read. Spring Boot automatically converts Java objects to JSON and JSON to Java objects using Jackson.

```json
{
    "id": 1,
    "name": "Spring Boot",
    "version": "3.4"
}
```

See: Chapter 9 (Your First REST Controller).

---

### JWT (JSON Web Token)

A compact, self-contained token used for authentication and information exchange. A JWT contains three parts: a header (algorithm), a payload (user data), and a signature (verification). In Spring Boot, JWT tokens are used for stateless authentication. The client includes the token in the Authorization header of each request.

See: Chapter 18 (JWT Authentication).

---

### Logback

The default logging framework in Spring Boot. It is an improved version of Log4j and implements the SLF4J API. Configuration is done through `logback-spring.xml` or `application.properties`. Logback supports multiple log levels: TRACE, DEBUG, INFO, WARN, ERROR.

See: Chapter 22 (Logging).

---

### @ManyToOne

A JPA annotation that defines a many-to-one relationship between entities. For example, many tasks belong to one user. The entity with `@ManyToOne` contains the foreign key column.

See: Chapter 14 (Spring Data JPA and H2).

---

### Maven

A build automation tool for Java projects. Maven manages dependencies (libraries your project uses), compiles code, runs tests, and packages your application. It uses a `pom.xml` file to define project settings and dependencies. Spring Boot projects typically use Maven or Gradle.

See: Chapter 2 (Development Environment).

---

### @MessageMapping

A WebSocket annotation similar to `@RequestMapping` for HTTP. It maps incoming STOMP messages to a handler method based on the destination. The application destination prefix (like `/app`) is stripped before matching.

See: Appendix A (WebSocket).

---

### MockMvc

A Spring testing utility that simulates HTTP requests to your controllers without starting a real web server. It lets you test controllers in isolation, verify response status codes, check response body content, and validate headers. Use it with `@AutoConfigureMockMvc` in integration tests.

```java
mockMvc.perform(get("/api/products"))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$[0].name").value("Laptop"));
```

See: Chapter 26 (Testing).

---

### @OneToMany

A JPA annotation that defines a one-to-many relationship between entities. For example, one user has many tasks. The `mappedBy` attribute specifies the field in the child entity that owns the relationship.

See: Chapter 14 (Spring Data JPA and H2).

---

### @OneToOne

A JPA annotation that defines a one-to-one relationship between entities. For example, one user has one profile. One side owns the relationship and contains the foreign key.

See: Chapter 14 (Spring Data JPA and H2).

---

### OpenAPI

A specification for describing REST APIs. It defines endpoints, request and response formats, authentication methods, and more in a machine-readable format. Springdoc OpenAPI generates this specification automatically from your Spring Boot controllers. The Swagger UI provides a visual, interactive interface for the API documentation.

See: Chapter 27 (API Documentation).

---

### @PatchMapping

A shortcut annotation for `@RequestMapping(method = RequestMethod.PATCH)`. It maps HTTP PATCH requests to a specific controller method. Used for endpoints that partially update a resource (only the fields that are provided are changed).

See: Chapter 10 (Request and Response Handling).

---

### @PathVariable

An annotation that extracts a value from the URL path and binds it to a method parameter. For example, in `/api/users/42`, the `42` can be captured as a path variable.

```java
@GetMapping("/api/users/{id}")
public User getUser(@PathVariable Long id) {
    return userService.findById(id);
}
```

See: Chapter 10 (Request and Response Handling).

---

### POJO (Plain Old Java Object)

A regular Java class with no special requirements. It does not extend framework-specific classes or implement framework-specific interfaces. Spring Boot encourages the use of POJOs for entities, DTOs, and other objects. The framework handles the rest through annotations.

---

### @PostMapping

A shortcut annotation for `@RequestMapping(method = RequestMethod.POST)`. It maps HTTP POST requests to a specific controller method. Used for endpoints that create new resources.

See: Chapter 9 (Your First REST Controller).

---

### Profile

A named set of configuration settings that can be activated in different environments. For example, you might have a `dev` profile for development (using H2) and a `prod` profile for production (using PostgreSQL). Activate a profile with `spring.profiles.active=dev` in `application.properties` or as a command-line argument.

See: Chapter 8 (Properties and Profiles).

---

### @PutMapping

A shortcut annotation for `@RequestMapping(method = RequestMethod.PUT)`. It maps HTTP PUT requests to a specific controller method. Used for endpoints that fully replace a resource.

See: Chapter 10 (Request and Response Handling).

---

### @Query

A Spring Data JPA annotation that defines a custom JPQL or native SQL query on a repository method. Use this when the automatically generated query method name would be too long or complex.

```java
@Query("SELECT t FROM Task t WHERE t.status = :status AND t.user.id = :userId")
List<Task> findTasksByStatusAndUser(@Param("status") TaskStatus status,
                                    @Param("userId") Long userId);
```

See: Chapter 15 (Repositories and CRUD).

---

### @Repository

A stereotype annotation that marks a class as a data access component. It is a specialization of `@Component` and tells Spring to translate database-specific exceptions into Spring's `DataAccessException` hierarchy. In Spring Data JPA, you typically use interfaces that extend `JpaRepository` instead of writing repository classes by hand.

See: Chapter 15 (Repositories and CRUD).

---

### @RequestBody

An annotation that tells Spring to convert the JSON body of an HTTP request into a Java object. Spring uses Jackson to perform this conversion automatically.

```java
@PostMapping("/api/users")
public User createUser(@RequestBody User user) {
    return userService.save(user);
}
```

See: Chapter 10 (Request and Response Handling).

---

### @RequestMapping

An annotation that maps HTTP requests to controller methods. It can specify the URL path, HTTP method, content types, and more. Shortcut annotations like `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, and `@PatchMapping` are more commonly used.

See: Chapter 9 (Your First REST Controller).

---

### @RequestParam

An annotation that extracts a query parameter from the URL and binds it to a method parameter. For example, in `/api/products?category=electronics`, the `category` value is extracted.

```java
@GetMapping("/api/products")
public List<Product> search(@RequestParam String category) {
    return productService.findByCategory(category);
}
```

See: Chapter 10 (Request and Response Handling).

---

### REST (Representational State Transfer)

An architectural style for building web services. RESTful APIs use HTTP methods (GET, POST, PUT, DELETE) to perform operations on resources identified by URLs. Data is typically exchanged in JSON format. Spring Boot makes it easy to build REST APIs with `@RestController`.

See: Chapter 9 (Your First REST Controller).

---

### @RestController

An annotation that combines `@Controller` and `@ResponseBody`. It marks a class as a REST controller where every method's return value is automatically converted to JSON and written to the HTTP response body. This is the most common annotation for building REST APIs.

See: Chapter 9 (Your First REST Controller).

---

### @Scheduled

An annotation that marks a method to be executed on a schedule. You can specify a fixed rate (every N milliseconds), a fixed delay (N milliseconds after the previous execution finishes), or a cron expression for complex schedules. Requires `@EnableScheduling`.

```java
@Scheduled(fixedRate = 60000)  // Every 60 seconds
public void checkStatus() {
    // This runs automatically
}
```

See: Chapter 23 (Scheduling).

---

### @Scope

An annotation that defines the lifecycle scope of a bean. The default scope is `singleton` (one instance per application). Other scopes include `prototype` (new instance every time), `request` (one per HTTP request), and `session` (one per HTTP session).

See: Chapter 7 (Beans and Annotations).

---

### SecurityFilterChain

A Spring Security bean that defines the security rules for your application. It specifies which URLs require authentication, which roles can access which endpoints, how sessions are managed, and where custom filters are inserted. Configured as a `@Bean` method that takes `HttpSecurity` as a parameter.

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http)
        throws Exception {
    http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/api/public/**").permitAll()
        .anyRequest().authenticated()
    );
    return http.build();
}
```

See: Chapter 17 (Spring Security Introduction).

---

### @SendTo

A WebSocket annotation that specifies the destination topic for the return value of a `@MessageMapping` method. All clients subscribed to that topic receive the message.

See: Appendix A (WebSocket).

---

### @Service

A stereotype annotation that marks a class as a service component containing business logic. It is a specialization of `@Component`. Using `@Service` instead of `@Component` communicates the class's purpose and follows the layered architecture pattern.

See: Chapter 7 (Beans and Annotations).

---

### SimpMessagingTemplate

A Spring class for sending WebSocket STOMP messages programmatically. Unlike `@SendTo` (which only works in `@MessageMapping` methods), `SimpMessagingTemplate` can send messages from any part of your application, including services, scheduled tasks, and REST controllers.

See: Appendix A (WebSocket).

---

### SLF4J (Simple Logging Facade for Java)

A logging API that provides a common interface for various logging frameworks (Logback, Log4j2, etc.). Spring Boot uses SLF4J with Logback by default. You create a logger with `LoggerFactory.getLogger(MyClass.class)` and use methods like `logger.info()`, `logger.error()`, and `logger.debug()`.

```java
private static final Logger logger = LoggerFactory.getLogger(MyClass.class);
logger.info("Application started");
```

See: Chapter 22 (Logging).

---

### Spring Boot Actuator

A module that adds production-ready features to your application. It exposes endpoints for health checks (`/actuator/health`), metrics (`/actuator/metrics`), environment info, and more. Useful for monitoring applications in production.

See: Chapter 28 (Actuator and Monitoring).

---

### Spring Boot DevTools

A development-time tool that provides automatic application restart when code changes, live reload for browser resources, and sensible development defaults (like disabling template caching). Add the `spring-boot-devtools` dependency to use it. It is automatically disabled in production.

See: Chapter 2 (Development Environment).

---

### @SpringBootApplication

The main annotation for a Spring Boot application. It combines three annotations: `@Configuration` (marks the class as a configuration source), `@EnableAutoConfiguration` (enables Spring Boot's auto-configuration), and `@ComponentScan` (enables component scanning in the current package and sub-packages).

See: Chapter 3 (Your First Spring Boot Project).

---

### SpringBootTest

A test annotation that loads the full Spring application context for integration testing. It starts the entire Spring Boot application, including all beans, configurations, and auto-configurations. Use it when you need to test how components work together.

See: Chapter 26 (Testing).

---

### Starter

A Spring Boot dependency that bundles together all the libraries you need for a specific feature. For example, `spring-boot-starter-web` includes Spring MVC, Jackson, Tomcat, and validation. Starters eliminate the need to figure out which individual libraries and versions are compatible.

See: Chapter 1 (What Is Spring Boot).

---

### STOMP (Simple Text Oriented Messaging Protocol)

A messaging protocol that adds structure to WebSocket communication. It defines commands like CONNECT, SUBSCRIBE, SEND, and MESSAGE, along with destinations (topics) and headers. Spring Boot uses STOMP for its WebSocket support.

See: Appendix A (WebSocket).

---

### Swagger

A set of tools for designing, building, and documenting REST APIs. In the Spring Boot ecosystem, Springdoc OpenAPI generates a Swagger UI that provides an interactive, browser-based interface for exploring and testing your API endpoints. Access it at `/swagger-ui.html`.

See: Chapter 27 (API Documentation).

---

### @Table

A JPA annotation that specifies the database table name for an entity. If not provided, JPA uses the class name as the table name. Use `@Table` when the class name conflicts with a database reserved word (like "user" in H2).

See: Chapter 14 (Spring Data JPA and H2).

---

### Tomcat

An open-source web server and servlet container. Spring Boot embeds Tomcat by default, so you do not need to install it separately. Your application runs on Tomcat's built-in HTTP server (port 8080 by default). You can switch to Jetty or Undertow if preferred.

See: Chapter 1 (What Is Spring Boot).

---

### @Transactional

An annotation that wraps a method's execution in a database transaction. If the method completes successfully, the transaction is committed. If an exception is thrown, the transaction is rolled back (all changes are undone). Use `@Transactional(readOnly = true)` for read-only operations to optimize performance.

See: Chapter 15 (Repositories and CRUD).

---

### @Valid

An annotation that triggers Jakarta Bean Validation on a request body or method parameter. When placed before a `@RequestBody` parameter, Spring validates the object using annotations like `@NotBlank`, `@Size`, `@Email`, and `@Min`. If validation fails, Spring throws a `MethodArgumentNotValidException`.

```java
@PostMapping("/api/users")
public User createUser(@Valid @RequestBody CreateUserRequest request) {
    return userService.create(request);
}
```

See: Chapter 11 (Input Validation).

---

### @Value

An annotation that injects a value from `application.properties` or an environment variable into a field or constructor parameter. It uses the `${property.name}` syntax.

```java
@Value("${app.name}")
private String appName;

@Value("${server.port:8080}")  // with default value
private int serverPort;
```

See: Chapter 8 (Properties and Profiles).

---

### WAR (Web Application Archive)

A file format for packaging web applications to be deployed on an external servlet container like Tomcat or Jetty. Spring Boot defaults to JAR packaging with an embedded server, but WAR packaging is available if you need to deploy to an existing application server.

See: Chapter 30 (Docker and Deployment).

---

### WebSocket

A communication protocol that provides persistent, full-duplex (two-way) communication between a client and server over a single TCP connection. Unlike HTTP, where the client must initiate every exchange, WebSocket allows the server to push messages to the client at any time without a prior request.

See: Appendix A (WebSocket).

---

### YAML (YAML Ain't Markup Language)

A human-readable data format used for configuration files. Spring Boot supports YAML as an alternative to `.properties` files. YAML uses indentation to show hierarchy, which some developers find more readable than dot-separated property names.

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
server:
  port: 8080
```

See: Chapter 8 (Properties and Profiles).

---

## Additional Terms

### Application Context

The central container in Spring that holds all beans and their configurations. It is the implementation of the IoC container. When your Spring Boot application starts, it creates an application context, scans for components, creates beans, and injects dependencies.

---

### Auto-Configuration

A Spring Boot feature that automatically configures beans based on the dependencies on your classpath and the properties you set. For example, if `spring-boot-starter-data-jpa` and an H2 driver are on the classpath, Spring Boot automatically configures a DataSource, EntityManagerFactory, and transaction manager.

See: Chapter 5 (Auto-Configuration).

---

### Classpath

The set of directories and JAR files where Java looks for classes and resources. In a Maven project, the classpath includes your compiled classes and all dependencies defined in `pom.xml`. Spring Boot uses the classpath to detect which auto-configurations to activate.

---

### Connection Pool

A cache of database connections that are reused across requests. Creating a new database connection for every request is slow. A connection pool (like HikariCP, which Spring Boot uses by default) keeps a set of connections open and lends them to requests as needed.

---

### Embedded Server

A web server (like Tomcat, Jetty, or Undertow) that is bundled inside your Spring Boot application. You do not need to install or configure it separately. When you run your JAR file, the embedded server starts automatically.

---

### Hibernate

The most popular implementation of the JPA specification. It handles the mapping between Java objects and database tables, generates SQL queries, and manages database sessions. Spring Data JPA uses Hibernate under the hood by default.

---

### HikariCP

The default JDBC connection pool in Spring Boot. It is known for being fast and lightweight. Spring Boot configures HikariCP automatically when you add a database dependency.

---

### JPQL (Java Persistence Query Language)

A query language similar to SQL but operates on JPA entities instead of database tables. JPQL uses entity class names and field names instead of table and column names. Used with the `@Query` annotation in Spring Data JPA repositories.

---

### Lazy Loading

A JPA strategy where related entities are loaded from the database only when they are accessed for the first time, not when the parent entity is loaded. For example, with `@ManyToOne(fetch = FetchType.LAZY)`, the related entity is loaded only when you call the getter method.

---

### Migration (Database)

The process of evolving your database schema over time. Tools like Flyway and Liquibase manage database migrations by tracking which changes have been applied. In production, you use migrations instead of `ddl-auto=create-drop`.

---

### Pageable

A Spring Data interface that contains pagination and sorting information: page number, page size, and sort order. Spring MVC automatically creates a `Pageable` object from query parameters like `?page=0&size=10&sort=name`.

See: Chapter 16 (Pagination and Sorting).

---

### ResponseEntity

A class that represents an HTTP response, including the status code, headers, and body. It gives you full control over the response returned by a controller method.

```java
return ResponseEntity.status(HttpStatus.CREATED).body(newUser);
return ResponseEntity.ok(users);
return ResponseEntity.noContent().build();
```

See: Chapter 10 (Request and Response Handling).

---

### Singleton

The default scope for Spring beans. A singleton bean has exactly one instance in the entire application context. Every time you inject that bean, you get the same instance.

See: Chapter 7 (Beans and Annotations).

---

### Stereotype Annotation

An annotation that marks a class for a specific role in the application: `@Component` (generic), `@Service` (business logic), `@Repository` (data access), and `@Controller` (web handler). They all result in the class being registered as a bean, but they communicate the class's purpose.

See: Chapter 7 (Beans and Annotations).

---

### Transaction

A sequence of database operations that are treated as a single unit. Either all operations succeed (commit) or all are undone (rollback). Spring's `@Transactional` annotation manages transactions automatically.

---

## Quick Reference Table

| Term | One-Line Definition |
|---|---|
| @Autowired | Injects a dependency automatically |
| Bean | Object managed by Spring's container |
| @Cacheable | Caches a method's return value |
| Component Scanning | Spring's auto-discovery of annotated classes |
| @ControllerAdvice | Global exception handler for controllers |
| CORS | Controls cross-domain API access |
| CSRF | Protection against cross-site request attacks |
| DAO | Pattern for abstracting database access |
| DI | Objects receive their dependencies externally |
| DispatcherServlet | Routes all HTTP requests to controllers |
| DTO | Object for transferring data between layers |
| @Entity | Maps a Java class to a database table |
| Filter | Intercepts HTTP requests at the servlet level |
| H2 | Lightweight, in-memory Java database |
| Interceptor | Intercepts requests at the Spring MVC level |
| IoC | Framework controls object creation |
| Jackson | Converts between Java objects and JSON |
| JAR | Packaged Java application file |
| Jakarta EE | Enterprise Java platform (formerly Java EE) |
| JPA | Specification for object-relational mapping |
| JWT | Self-contained authentication token |
| Logback | Default logging framework in Spring Boot |
| Maven | Build tool and dependency manager |
| MockMvc | Tests controllers without a running server |
| @PathVariable | Extracts a value from the URL path |
| POJO | Plain Java class with no framework dependencies |
| Profile | Named configuration for different environments |
| @Repository | Marks a data access class |
| REST | Architectural style for web APIs |
| @RestController | Controller that returns JSON responses |
| SecurityFilterChain | Defines security rules for the application |
| @Service | Marks a business logic class |
| SLF4J | Logging API used by Spring Boot |
| Starter | Bundled dependency for a specific feature |
| Swagger | Interactive API documentation tool |
| Tomcat | Default embedded web server |
| @Transactional | Wraps method execution in a transaction |
| @Valid | Triggers input validation on a parameter |
| WebSocket | Protocol for real-time, two-way communication |
| YAML | Human-readable configuration file format |

---

## Common Mistakes

1. **Confusing @Component with @Bean.** Use `@Component` on your own classes. Use `@Bean` on methods inside `@Configuration` classes when you need to configure third-party objects.

2. **Confusing REST and HTTP.** REST is an architectural style. HTTP is a protocol. REST uses HTTP methods to define operations, but not all HTTP APIs follow REST principles.

3. **Confusing JPA and Hibernate.** JPA is a specification (a set of rules). Hibernate is an implementation (the code that follows those rules). Spring Data JPA provides a layer on top of both.

4. **Confusing Filter and Interceptor.** Filters work at the servlet level (before Spring MVC). Interceptors work at the Spring MVC level (after the DispatcherServlet). Use filters for security, CORS, and logging. Use interceptors for request-specific logic.

5. **Using @Autowired on fields.** Field injection with `@Autowired` makes testing harder. Prefer constructor injection, which is the recommended approach in modern Spring.

---

## Best Practices

1. **Learn the vocabulary.** Understanding terms helps you read documentation faster and communicate with other developers more effectively.

2. **Use the correct stereotype annotation.** Use `@Service` for services, `@Repository` for data access, and `@Controller`/`@RestController` for web handlers. Do not use `@Component` for everything.

3. **Understand the layers.** Controller handles HTTP, Service handles business logic, Repository handles data. Keep them separate.

4. **Read the official documentation.** The Spring Boot reference documentation at `docs.spring.io` is thorough and well-organized. This glossary is a starting point. The docs go deeper.

5. **Practice with real projects.** Build the TaskTracker project in Appendix B. Then build your own projects. Terms become natural when you use them in context.

---

## Quick Summary

This glossary covers more than 70 terms that you will encounter when working with Spring Boot. Terms range from core concepts like Dependency Injection and IoC to specific annotations like @RestController and @Transactional. Each entry explains the term in plain English and points you to the chapter in this book where you can learn more. Use this glossary as a reference whenever you encounter an unfamiliar term.

---

## Key Points

- Spring Boot uses many terms from Java, JPA, Spring Framework, and web development.
- Annotations like @Component, @Service, @Repository, and @Controller are stereotype annotations that mark classes for specific roles.
- JPA is a specification. Hibernate is an implementation. Spring Data JPA provides a convenience layer on top.
- DTOs separate what clients see from how your database is structured.
- Dependency Injection and IoC are the core principles that make Spring Boot work.
- Understanding the vocabulary makes reading documentation and learning new features much faster.

---

## Practice Questions

1. What is the difference between @Component, @Service, @Repository, and @Controller? When would you use each one?

2. Explain the difference between a Filter and an Interceptor. At what level does each one operate?

3. What is the relationship between JPA, Hibernate, and Spring Data JPA? How do they relate to each other?

4. What is the purpose of a DTO? Why would you use a DTO instead of returning an entity directly from a controller?

5. Explain the difference between @Cacheable and @CacheEvict. When would you use each one?

---

## Exercises

### Exercise 1: Build a Flashcard Set

Pick 20 terms from this glossary. Create a flashcard for each one with the term on the front and the definition on the back. Quiz yourself until you can define each term from memory.

### Exercise 2: Map the Annotations

Draw a diagram showing where each major annotation is used in a Spring Boot application. Start with `@SpringBootApplication` at the top and show how `@RestController`, `@Service`, `@Repository`, `@Entity`, and other annotations fit into the layered architecture.

### Exercise 3: Write Example Code

Choose five annotations you find most confusing. For each one, write a small code example (5 to 10 lines) that demonstrates how it works. Run the code to verify your understanding.
