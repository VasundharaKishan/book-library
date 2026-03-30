# Appendix B: Complete Project — TaskTracker API

## What You Will Learn

- How to build a complete REST API from scratch using everything you learned in this book.
- How to design User and Task entities with JPA relationships.
- How to implement repositories, services, and controllers following best practices.
- How to add input validation and global exception handling.
- How to secure the API with JWT authentication and role-based access.
- How to implement pagination, caching, and scheduled tasks.
- How to generate API documentation with OpenAPI and Swagger.
- How to write tests for your controllers and services.
- How to containerize the application with Docker.

## Why This Chapter Matters

Imagine you have learned how to hammer nails, cut wood, install plumbing, and wire electricity. Each skill is useful on its own. But the real test is building an entire house. That is what this appendix is about.

Throughout this book, you learned each Spring Boot concept one at a time. Now you will combine all of those skills into one complete, production-ready application. This is your capstone project. By the end, you will have a TaskTracker API that you can put on your resume and show to potential employers.

Every line of code is included. You will type it, understand it, and run it.

---

## B.1 Project Overview

TaskTracker is a task management API where users can create accounts, log in, and manage their tasks. Here is what the application does:

- Users can register and log in with JWT authentication.
- Users have roles (USER or ADMIN).
- Users can create, read, update, and delete their own tasks.
- Admins can view all tasks and all users.
- Tasks have a title, description, status, priority, and due date.
- Tasks can be filtered by status and priority with pagination.
- Overdue tasks are automatically flagged by a scheduled job.
- Frequently accessed data is cached for performance.
- The API is documented with OpenAPI (Swagger).

```
TaskTracker API Architecture:

+--------------------------------------------------+
|                    Clients                        |
|  (Postman, Browser, Mobile App, Frontend App)     |
+--------------------------------------------------+
                      |
                      | HTTP + JWT
                      v
+--------------------------------------------------+
|              Spring Security Layer                |
|  (JWT Filter, Authentication, Authorization)      |
+--------------------------------------------------+
                      |
                      v
+--------------------------------------------------+
|              REST Controllers                     |
|  (AuthController, TaskController, UserController) |
+--------------------------------------------------+
                      |
                      v
+--------------------------------------------------+
|              Service Layer                        |
|  (AuthService, TaskService, UserService)          |
+--------------------------------------------------+
                      |
                      v
+--------------------------------------------------+
|              Repository Layer                     |
|  (UserRepository, TaskRepository)                 |
+--------------------------------------------------+
                      |
                      v
+--------------------------------------------------+
|              H2 Database                          |
|  (Users table, Tasks table)                       |
+--------------------------------------------------+
```

---

## B.2 Project Setup

### Step 1: Create the Project

Go to [start.spring.io](https://start.spring.io) and create a new project with these settings:

| Setting | Value |
|---|---|
| Project | Maven |
| Language | Java |
| Spring Boot | 3.4.x (latest stable) |
| Group | com.example |
| Artifact | tasktracker |
| Name | tasktracker |
| Package name | com.example.tasktracker |
| Packaging | Jar |
| Java | 17 |

Add these dependencies:

- Spring Web
- Spring Data JPA
- H2 Database
- Spring Security
- Spring Boot Starter Validation
- Spring Boot Starter Cache

Click "Generate" to download the project. Unzip it and open it in your IDE.

### Step 2: Add Additional Dependencies

Open `pom.xml` and add these additional dependencies inside the `<dependencies>` section:

```xml
<!-- JWT Support -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.6</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.6</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.6</version>
    <scope>runtime</scope>
</dependency>

<!-- OpenAPI / Swagger Documentation -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.4</version>
</dependency>
```

### Step 3: Configure application.properties

Open `src/main/resources/application.properties` and add:

```properties
# Application name
spring.application.name=tasktracker

# H2 Database
spring.datasource.url=jdbc:h2:mem:tasktracker
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console

# JPA
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect

# JWT
jwt.secret=mySecretKeyForJWTTokenGenerationThatIsAtLeast256BitsLong2024
jwt.expiration=86400000

# Swagger / OpenAPI
springdoc.swagger-ui.path=/swagger-ui.html
springdoc.api-docs.path=/api-docs

# Cache
spring.cache.type=simple
```

**Line-by-line explanation:**

- `spring.datasource.url=jdbc:h2:mem:tasktracker` creates an in-memory H2 database named "tasktracker." Data is lost when the application stops, which is perfect for development.
- `spring.h2.console.enabled=true` enables the H2 web console at `/h2-console` so you can view the database tables.
- `spring.jpa.hibernate.ddl-auto=create-drop` tells Hibernate to create tables on startup and drop them on shutdown. In production, you would use `validate` or `none`.
- `spring.jpa.show-sql=true` prints SQL statements to the console so you can see what Hibernate is doing.
- `jwt.secret` is the secret key for signing JWT tokens. In production, use a secure, random key and store it in environment variables.
- `jwt.expiration=86400000` sets the JWT token expiration to 24 hours (in milliseconds).
- `spring.cache.type=simple` uses a simple in-memory cache based on `ConcurrentHashMap`.

---

## B.3 Entity Classes

### The User Entity

Create the file `src/main/java/com/example/tasktracker/entity/User.java`:

```java
package com.example.tasktracker.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @JsonIgnore
    @Column(nullable = false)
    private String password;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role = Role.USER;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @JsonIgnore
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL,
               orphanRemoval = true)
    private List<Task> tasks = new ArrayList<>();

    public User() {
    }

    public User(String username, String email, String password) {
        this.username = username;
        this.email = email;
        this.password = password;
    }

    // Getters and setters

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public Role getRole() {
        return role;
    }

    public void setRole(Role role) {
        this.role = role;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public List<Task> getTasks() {
        return tasks;
    }

    public void setTasks(List<Task> tasks) {
        this.tasks = tasks;
    }
}
```

**Line-by-line explanation:**

- `@Entity` marks this class as a JPA entity that maps to a database table.
- `@Table(name = "users")` sets the table name to "users." We cannot use "user" because it is a reserved word in H2.
- `@Id` and `@GeneratedValue(strategy = GenerationType.IDENTITY)` make the `id` field the primary key with auto-increment.
- `@Column(nullable = false, unique = true, length = 50)` means the column cannot be null, must be unique, and has a max length of 50 characters.
- `@JsonIgnore` on the `password` field prevents the password from being included in JSON responses. You never want to send passwords to the client.
- `@Enumerated(EnumType.STRING)` stores the enum as a string in the database (like "USER" or "ADMIN") instead of a number.
- `@OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)` creates a one-to-many relationship: one user has many tasks. `cascade = CascadeType.ALL` means operations on the user (like delete) cascade to their tasks. `orphanRemoval = true` means if a task is removed from the list, it is deleted from the database.
- `@JsonIgnore` on the `tasks` field prevents infinite recursion when converting to JSON (User has Tasks, Task has User, User has Tasks...).

### The Role Enum

Create `src/main/java/com/example/tasktracker/entity/Role.java`:

```java
package com.example.tasktracker.entity;

public enum Role {
    USER,
    ADMIN
}
```

### The Task Entity

Create `src/main/java/com/example/tasktracker/entity/Task.java`:

```java
package com.example.tasktracker.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "tasks")
public class Task {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(length = 1000)
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TaskStatus status = TaskStatus.TODO;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TaskPriority priority = TaskPriority.MEDIUM;

    private LocalDate dueDate;

    @Column(nullable = false)
    private boolean overdue = false;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    private LocalDateTime updatedAt = LocalDateTime.now();

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    public Task() {
    }

    public Task(String title, String description,
                TaskPriority priority, LocalDate dueDate, User user) {
        this.title = title;
        this.description = description;
        this.priority = priority;
        this.dueDate = dueDate;
        this.user = user;
    }

    // Getters and setters

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public TaskStatus getStatus() {
        return status;
    }

    public void setStatus(TaskStatus status) {
        this.status = status;
    }

    public TaskPriority getPriority() {
        return priority;
    }

    public void setPriority(TaskPriority priority) {
        this.priority = priority;
    }

    public LocalDate getDueDate() {
        return dueDate;
    }

    public void setDueDate(LocalDate dueDate) {
        this.dueDate = dueDate;
    }

    public boolean isOverdue() {
        return overdue;
    }

    public void setOverdue(boolean overdue) {
        this.overdue = overdue;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }
}
```

**Line-by-line explanation:**

- `@ManyToOne(fetch = FetchType.LAZY)` creates the many-to-one side of the relationship. Many tasks belong to one user. `FetchType.LAZY` means the user data is only loaded from the database when you actually access it, which improves performance.
- `@JoinColumn(name = "user_id", nullable = false)` creates a `user_id` foreign key column in the tasks table. It cannot be null because every task must belong to a user.
- `boolean overdue` is a flag that gets set to `true` by a scheduled task when the due date has passed and the task is not completed.
- `updatedAt` tracks when the task was last modified.

### The TaskStatus Enum

Create `src/main/java/com/example/tasktracker/entity/TaskStatus.java`:

```java
package com.example.tasktracker.entity;

public enum TaskStatus {
    TODO,
    IN_PROGRESS,
    COMPLETED
}
```

### The TaskPriority Enum

Create `src/main/java/com/example/tasktracker/entity/TaskPriority.java`:

```java
package com.example.tasktracker.entity;

public enum TaskPriority {
    LOW,
    MEDIUM,
    HIGH
}
```

### Entity Relationship Diagram

```
+-------------------+          +-------------------+
|      users        |          |      tasks        |
+-------------------+          +-------------------+
| id (PK)           |<---------| id (PK)           |
| username          |    1:N   | title             |
| email             |          | description       |
| password          |          | status            |
| role              |          | priority          |
| created_at        |          | due_date          |
+-------------------+          | overdue           |
                               | created_at        |
                               | updated_at        |
                               | user_id (FK)      |
                               +-------------------+
```

---

## B.4 DTOs (Data Transfer Objects)

DTOs separate what the client sends and receives from the internal entity structure. This is important for security (you do not want to expose passwords) and flexibility (you can change DTOs without changing entities).

### Registration Request

Create `src/main/java/com/example/tasktracker/dto/RegisterRequest.java`:

```java
package com.example.tasktracker.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class RegisterRequest {

    @NotBlank(message = "Username is required")
    @Size(min = 3, max = 50, message = "Username must be 3-50 characters")
    private String username;

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    private String email;

    @NotBlank(message = "Password is required")
    @Size(min = 6, max = 100, message = "Password must be 6-100 characters")
    private String password;

    public RegisterRequest() {
    }

    public RegisterRequest(String username, String email, String password) {
        this.username = username;
        this.email = email;
        this.password = password;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
```

### Login Request

Create `src/main/java/com/example/tasktracker/dto/LoginRequest.java`:

```java
package com.example.tasktracker.dto;

import jakarta.validation.constraints.NotBlank;

public class LoginRequest {

    @NotBlank(message = "Username is required")
    private String username;

    @NotBlank(message = "Password is required")
    private String password;

    public LoginRequest() {
    }

    public LoginRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
```

### Auth Response

Create `src/main/java/com/example/tasktracker/dto/AuthResponse.java`:

```java
package com.example.tasktracker.dto;

public class AuthResponse {

    private String token;
    private String username;
    private String role;

    public AuthResponse() {
    }

    public AuthResponse(String token, String username, String role) {
        this.token = token;
        this.username = username;
        this.role = role;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }
}
```

### Task Request

Create `src/main/java/com/example/tasktracker/dto/TaskRequest.java`:

```java
package com.example.tasktracker.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.time.LocalDate;

public class TaskRequest {

    @NotBlank(message = "Title is required")
    @Size(max = 200, message = "Title cannot exceed 200 characters")
    private String title;

    @Size(max = 1000, message = "Description cannot exceed 1000 characters")
    private String description;

    private String priority;
    private LocalDate dueDate;

    public TaskRequest() {
    }

    public TaskRequest(String title, String description,
                       String priority, LocalDate dueDate) {
        this.title = title;
        this.description = description;
        this.priority = priority;
        this.dueDate = dueDate;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getPriority() {
        return priority;
    }

    public void setPriority(String priority) {
        this.priority = priority;
    }

    public LocalDate getDueDate() {
        return dueDate;
    }

    public void setDueDate(LocalDate dueDate) {
        this.dueDate = dueDate;
    }
}
```

### Task Response

Create `src/main/java/com/example/tasktracker/dto/TaskResponse.java`:

```java
package com.example.tasktracker.dto;

import com.example.tasktracker.entity.Task;

import java.time.LocalDate;
import java.time.LocalDateTime;

public class TaskResponse {

    private Long id;
    private String title;
    private String description;
    private String status;
    private String priority;
    private LocalDate dueDate;
    private boolean overdue;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private String username;

    public TaskResponse() {
    }

    public TaskResponse(Task task) {
        this.id = task.getId();
        this.title = task.getTitle();
        this.description = task.getDescription();
        this.status = task.getStatus().name();
        this.priority = task.getPriority().name();
        this.dueDate = task.getDueDate();
        this.overdue = task.isOverdue();
        this.createdAt = task.getCreatedAt();
        this.updatedAt = task.getUpdatedAt();
        this.username = task.getUser().getUsername();
    }

    // Getters and setters

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getPriority() {
        return priority;
    }

    public void setPriority(String priority) {
        this.priority = priority;
    }

    public LocalDate getDueDate() {
        return dueDate;
    }

    public void setDueDate(LocalDate dueDate) {
        this.dueDate = dueDate;
    }

    public boolean isOverdue() {
        return overdue;
    }

    public void setOverdue(boolean overdue) {
        this.overdue = overdue;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }
}
```

---

## B.5 Repositories

### UserRepository

Create `src/main/java/com/example/tasktracker/repository/UserRepository.java`:

```java
package com.example.tasktracker.repository;

import com.example.tasktracker.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByUsername(String username);

    Optional<User> findByEmail(String email);

    boolean existsByUsername(String username);

    boolean existsByEmail(String email);
}
```

**Line-by-line explanation:**

- `JpaRepository<User, Long>` gives us all standard CRUD operations (save, findById, findAll, delete) plus pagination and sorting. `User` is the entity type, and `Long` is the type of its primary key.
- `findByUsername` and `findByEmail` are query methods. Spring Data JPA automatically generates the SQL query from the method name. `findByUsername` becomes `SELECT * FROM users WHERE username = ?`.
- `existsByUsername` and `existsByEmail` return a boolean. These are useful for checking if a username or email is already taken during registration.

### TaskRepository

Create `src/main/java/com/example/tasktracker/repository/TaskRepository.java`:

```java
package com.example.tasktracker.repository;

import com.example.tasktracker.entity.Task;
import com.example.tasktracker.entity.TaskPriority;
import com.example.tasktracker.entity.TaskStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface TaskRepository extends JpaRepository<Task, Long> {

    Page<Task> findByUserId(Long userId, Pageable pageable);

    Page<Task> findByUserIdAndStatus(Long userId, TaskStatus status,
                                     Pageable pageable);

    Page<Task> findByUserIdAndPriority(Long userId, TaskPriority priority,
                                       Pageable pageable);

    Optional<Task> findByIdAndUserId(Long id, Long userId);

    @Query("SELECT t FROM Task t WHERE t.dueDate < :today "
         + "AND t.status <> 'COMPLETED' AND t.overdue = false")
    List<Task> findOverdueTasks(@Param("today") LocalDate today);

    long countByUserIdAndStatus(Long userId, TaskStatus status);
}
```

**Line-by-line explanation:**

- `Page<Task> findByUserId(Long userId, Pageable pageable)` returns a page of tasks for a specific user. `Pageable` contains the page number, page size, and sort order.
- `findByUserIdAndStatus` filters by both user and status, returning paginated results.
- `findByIdAndUserId` finds a task by its ID but only if it belongs to the specified user. This prevents users from accessing other users' tasks.
- `@Query` defines a custom JPQL query. This query finds tasks where the due date is before today, the status is not COMPLETED, and the `overdue` flag is not yet set.
- `countByUserIdAndStatus` counts how many tasks a user has with a specific status. Useful for dashboard statistics.

---

## B.6 Exception Handling

### Custom Exceptions

Create `src/main/java/com/example/tasktracker/exception/ResourceNotFoundException.java`:

```java
package com.example.tasktracker.exception;

public class ResourceNotFoundException extends RuntimeException {

    public ResourceNotFoundException(String message) {
        super(message);
    }
}
```

Create `src/main/java/com/example/tasktracker/exception/DuplicateResourceException.java`:

```java
package com.example.tasktracker.exception;

public class DuplicateResourceException extends RuntimeException {

    public DuplicateResourceException(String message) {
        super(message);
    }
}
```

Create `src/main/java/com/example/tasktracker/exception/UnauthorizedException.java`:

```java
package com.example.tasktracker.exception;

public class UnauthorizedException extends RuntimeException {

    public UnauthorizedException(String message) {
        super(message);
    }
}
```

### Error Response DTO

Create `src/main/java/com/example/tasktracker/dto/ErrorResponse.java`:

```java
package com.example.tasktracker.dto;

import java.time.LocalDateTime;
import java.util.Map;

public class ErrorResponse {

    private int status;
    private String message;
    private LocalDateTime timestamp;
    private Map<String, String> errors;

    public ErrorResponse(int status, String message) {
        this.status = status;
        this.message = message;
        this.timestamp = LocalDateTime.now();
    }

    public ErrorResponse(int status, String message,
                         Map<String, String> errors) {
        this.status = status;
        this.message = message;
        this.timestamp = LocalDateTime.now();
        this.errors = errors;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public Map<String, String> getErrors() {
        return errors;
    }

    public void setErrors(Map<String, String> errors) {
        this.errors = errors;
    }
}
```

### Global Exception Handler

Create `src/main/java/com/example/tasktracker/exception/GlobalExceptionHandler.java`:

```java
package com.example.tasktracker.exception;

import com.example.tasktracker.dto.ErrorResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex) {

        ErrorResponse error = new ErrorResponse(
            HttpStatus.NOT_FOUND.value(), ex.getMessage()
        );
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    @ExceptionHandler(DuplicateResourceException.class)
    public ResponseEntity<ErrorResponse> handleDuplicate(
            DuplicateResourceException ex) {

        ErrorResponse error = new ErrorResponse(
            HttpStatus.CONFLICT.value(), ex.getMessage()
        );
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }

    @ExceptionHandler(UnauthorizedException.class)
    public ResponseEntity<ErrorResponse> handleUnauthorized(
            UnauthorizedException ex) {

        ErrorResponse error = new ErrorResponse(
            HttpStatus.UNAUTHORIZED.value(), ex.getMessage()
        );
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            MethodArgumentNotValidException ex) {

        Map<String, String> errors = new HashMap<>();
        for (FieldError fieldError : ex.getBindingResult().getFieldErrors()) {
            errors.put(fieldError.getField(),
                       fieldError.getDefaultMessage());
        }

        ErrorResponse error = new ErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            "Validation failed",
            errors
        );
        return ResponseEntity.badRequest().body(error);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(Exception ex) {

        ErrorResponse error = new ErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "An unexpected error occurred"
        );
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                             .body(error);
    }
}
```

**Line-by-line explanation:**

- `@RestControllerAdvice` makes this a global exception handler for all controllers. It combines `@ControllerAdvice` and `@ResponseBody`.
- Each `@ExceptionHandler` method catches a specific exception type and converts it to a meaningful JSON response.
- `MethodArgumentNotValidException` is thrown when `@Valid` validation fails. We extract each field error and create a map of field name to error message.
- The catch-all `Exception` handler catches any unexpected errors and returns a generic message. In production, you would also log the full stack trace.

---

## B.7 JWT Security

### JWT Utility Class

Create `src/main/java/com/example/tasktracker/security/JwtUtil.java`:

```java
package com.example.tasktracker.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Component
public class JwtUtil {

    private final SecretKey key;
    private final long expiration;

    public JwtUtil(@Value("${jwt.secret}") String secret,
                   @Value("${jwt.expiration}") long expiration) {
        this.key = Keys.hmacShaKeyFor(
            secret.getBytes(StandardCharsets.UTF_8)
        );
        this.expiration = expiration;
    }

    public String generateToken(String username, String role) {
        return Jwts.builder()
            .subject(username)
            .claim("role", role)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expiration))
            .signWith(key)
            .compact();
    }

    public String extractUsername(String token) {
        return extractClaims(token).getSubject();
    }

    public String extractRole(String token) {
        return extractClaims(token).get("role", String.class);
    }

    public boolean isTokenValid(String token) {
        try {
            extractClaims(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private Claims extractClaims(String token) {
        return Jwts.parser()
            .verifyWith(key)
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }
}
```

**Line-by-line explanation:**

- `@Value("${jwt.secret}")` injects the secret key from `application.properties`.
- `Keys.hmacShaKeyFor(...)` creates a cryptographic key from the secret string.
- `generateToken` creates a JWT with the username as the subject, the role as a custom claim, and an expiration time.
- `extractUsername` and `extractRole` parse the token to read the stored values.
- `isTokenValid` attempts to parse the token. If parsing fails (expired, tampered, wrong key), it returns false.

### JWT Authentication Filter

Create `src/main/java/com/example/tasktracker/security/JwtAuthenticationFilter.java`:

```java
package com.example.tasktracker.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    public JwtAuthenticationFilter(JwtUtil jwtUtil) {
        this.jwtUtil = jwtUtil;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);

            if (jwtUtil.isTokenValid(token)) {
                String username = jwtUtil.extractUsername(token);
                String role = jwtUtil.extractRole(token);

                SimpleGrantedAuthority authority =
                    new SimpleGrantedAuthority("ROLE_" + role);

                UsernamePasswordAuthenticationToken authentication =
                    new UsernamePasswordAuthenticationToken(
                        username, null, List.of(authority)
                    );

                SecurityContextHolder.getContext()
                    .setAuthentication(authentication);
            }
        }

        filterChain.doFilter(request, response);
    }
}
```

**Line-by-line explanation:**

- `OncePerRequestFilter` ensures this filter runs exactly once per HTTP request.
- `request.getHeader("Authorization")` reads the Authorization header from the incoming request.
- `authHeader.startsWith("Bearer ")` checks if the header follows the Bearer token format.
- `authHeader.substring(7)` extracts the token by removing the "Bearer " prefix (7 characters).
- `jwtUtil.isTokenValid(token)` verifies the token is not expired or tampered with.
- `SimpleGrantedAuthority("ROLE_" + role)` creates a Spring Security authority. The "ROLE_" prefix is required by Spring Security conventions.
- `UsernamePasswordAuthenticationToken` represents the authenticated user. We pass the username, null for credentials (we already verified the token), and the authorities.
- `SecurityContextHolder.getContext().setAuthentication(authentication)` stores the authentication in the security context. Now Spring Security knows who the user is for the rest of the request.
- `filterChain.doFilter(request, response)` continues to the next filter in the chain. If we did not call this, the request would stop here.

### Security Configuration

Create `src/main/java/com/example/tasktracker/security/SecurityConfig.java`:

```java
package com.example.tasktracker.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http)
            throws Exception {

        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/h2-console/**").permitAll()
                .requestMatchers("/swagger-ui/**", "/api-docs/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .headers(headers -> headers
                .frameOptions(frame -> frame.disable())
            )
            .addFilterBefore(jwtAuthenticationFilter,
                UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

**Line-by-line explanation:**

- `csrf(csrf -> csrf.disable())` disables CSRF protection. REST APIs that use JWT tokens do not need CSRF because the token itself prevents cross-site request forgery.
- `SessionCreationPolicy.STATELESS` tells Spring Security not to create HTTP sessions. We use JWT tokens instead of sessions.
- `requestMatchers("/api/auth/**").permitAll()` allows anyone to access the registration and login endpoints without authentication.
- `requestMatchers("/h2-console/**").permitAll()` allows access to the H2 database console during development.
- `requestMatchers("/swagger-ui/**", "/api-docs/**").permitAll()` allows access to the API documentation.
- `requestMatchers("/api/admin/**").hasRole("ADMIN")` restricts admin endpoints to users with the ADMIN role only.
- `anyRequest().authenticated()` requires authentication for all other endpoints.
- `headers(headers -> headers.frameOptions(frame -> frame.disable()))` disables X-Frame-Options so the H2 console (which uses iframes) can load.
- `addFilterBefore(...)` adds our JWT filter before Spring Security's default authentication filter. This means every request is checked for a JWT token first.

---

## B.8 Service Layer

### AuthService

Create `src/main/java/com/example/tasktracker/service/AuthService.java`:

```java
package com.example.tasktracker.service;

import com.example.tasktracker.dto.AuthResponse;
import com.example.tasktracker.dto.LoginRequest;
import com.example.tasktracker.dto.RegisterRequest;
import com.example.tasktracker.entity.User;
import com.example.tasktracker.exception.DuplicateResourceException;
import com.example.tasktracker.exception.UnauthorizedException;
import com.example.tasktracker.repository.UserRepository;
import com.example.tasktracker.security.JwtUtil;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public AuthService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder,
                       JwtUtil jwtUtil) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
    }

    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new DuplicateResourceException(
                "Username already exists: " + request.getUsername()
            );
        }

        if (userRepository.existsByEmail(request.getEmail())) {
            throw new DuplicateResourceException(
                "Email already exists: " + request.getEmail()
            );
        }

        User user = new User(
            request.getUsername(),
            request.getEmail(),
            passwordEncoder.encode(request.getPassword())
        );

        userRepository.save(user);

        String token = jwtUtil.generateToken(
            user.getUsername(), user.getRole().name()
        );

        return new AuthResponse(
            token, user.getUsername(), user.getRole().name()
        );
    }

    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
            .orElseThrow(() -> new UnauthorizedException(
                "Invalid username or password"
            ));

        if (!passwordEncoder.matches(request.getPassword(),
                                     user.getPassword())) {
            throw new UnauthorizedException("Invalid username or password");
        }

        String token = jwtUtil.generateToken(
            user.getUsername(), user.getRole().name()
        );

        return new AuthResponse(
            token, user.getUsername(), user.getRole().name()
        );
    }
}
```

**Line-by-line explanation:**

- `passwordEncoder.encode(request.getPassword())` hashes the password using BCrypt before storing it. You should never store plain-text passwords.
- `passwordEncoder.matches(request.getPassword(), user.getPassword())` compares the raw password from the login request with the hashed password from the database.
- Notice that the same error message "Invalid username or password" is used for both a wrong username and a wrong password. This is a security best practice. If you said "User not found," an attacker would know which usernames exist.

### TaskService

Create `src/main/java/com/example/tasktracker/service/TaskService.java`:

```java
package com.example.tasktracker.service;

import com.example.tasktracker.dto.TaskRequest;
import com.example.tasktracker.dto.TaskResponse;
import com.example.tasktracker.entity.Task;
import com.example.tasktracker.entity.TaskPriority;
import com.example.tasktracker.entity.TaskStatus;
import com.example.tasktracker.entity.User;
import com.example.tasktracker.exception.ResourceNotFoundException;
import com.example.tasktracker.repository.TaskRepository;
import com.example.tasktracker.repository.UserRepository;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional
public class TaskService {

    private final TaskRepository taskRepository;
    private final UserRepository userRepository;

    public TaskService(TaskRepository taskRepository,
                       UserRepository userRepository) {
        this.taskRepository = taskRepository;
        this.userRepository = userRepository;
    }

    public TaskResponse createTask(TaskRequest request, String username) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException(
                "User not found: " + username
            ));

        TaskPriority priority = TaskPriority.MEDIUM;
        if (request.getPriority() != null) {
            priority = TaskPriority.valueOf(
                request.getPriority().toUpperCase()
            );
        }

        Task task = new Task(
            request.getTitle(),
            request.getDescription(),
            priority,
            request.getDueDate(),
            user
        );

        Task savedTask = taskRepository.save(task);
        return new TaskResponse(savedTask);
    }

    @Cacheable(value = "tasks", key = "#username + '-' + #pageable.pageNumber")
    @Transactional(readOnly = true)
    public Page<TaskResponse> getTasksByUser(String username,
                                             Pageable pageable) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException(
                "User not found: " + username
            ));

        return taskRepository.findByUserId(user.getId(), pageable)
            .map(TaskResponse::new);
    }

    @Transactional(readOnly = true)
    public Page<TaskResponse> getTasksByStatus(String username,
                                               TaskStatus status,
                                               Pageable pageable) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException(
                "User not found: " + username
            ));

        return taskRepository
            .findByUserIdAndStatus(user.getId(), status, pageable)
            .map(TaskResponse::new);
    }

    @Transactional(readOnly = true)
    public Page<TaskResponse> getTasksByPriority(String username,
                                                 TaskPriority priority,
                                                 Pageable pageable) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException(
                "User not found: " + username
            ));

        return taskRepository
            .findByUserIdAndPriority(user.getId(), priority, pageable)
            .map(TaskResponse::new);
    }

    @Transactional(readOnly = true)
    public TaskResponse getTaskById(Long taskId, String username) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException(
                "User not found: " + username
            ));

        Task task = taskRepository.findByIdAndUserId(taskId, user.getId())
            .orElseThrow(() -> new ResourceNotFoundException(
                "Task not found with id: " + taskId
            ));

        return new TaskResponse(task);
    }

    @CacheEvict(value = "tasks", allEntries = true)
    public TaskResponse updateTask(Long taskId, TaskRequest request,
                                   String username) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException(
                "User not found: " + username
            ));

        Task task = taskRepository.findByIdAndUserId(taskId, user.getId())
            .orElseThrow(() -> new ResourceNotFoundException(
                "Task not found with id: " + taskId
            ));

        task.setTitle(request.getTitle());
        task.setDescription(request.getDescription());
        task.setDueDate(request.getDueDate());
        task.setUpdatedAt(LocalDateTime.now());

        if (request.getPriority() != null) {
            task.setPriority(
                TaskPriority.valueOf(request.getPriority().toUpperCase())
            );
        }

        Task updatedTask = taskRepository.save(task);
        return new TaskResponse(updatedTask);
    }

    @CacheEvict(value = "tasks", allEntries = true)
    public TaskResponse updateTaskStatus(Long taskId, TaskStatus status,
                                         String username) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException(
                "User not found: " + username
            ));

        Task task = taskRepository.findByIdAndUserId(taskId, user.getId())
            .orElseThrow(() -> new ResourceNotFoundException(
                "Task not found with id: " + taskId
            ));

        task.setStatus(status);
        task.setUpdatedAt(LocalDateTime.now());

        if (status == TaskStatus.COMPLETED) {
            task.setOverdue(false);
        }

        Task updatedTask = taskRepository.save(task);
        return new TaskResponse(updatedTask);
    }

    @CacheEvict(value = "tasks", allEntries = true)
    public void deleteTask(Long taskId, String username) {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException(
                "User not found: " + username
            ));

        Task task = taskRepository.findByIdAndUserId(taskId, user.getId())
            .orElseThrow(() -> new ResourceNotFoundException(
                "Task not found with id: " + taskId
            ));

        taskRepository.delete(task);
    }

    public int markOverdueTasks() {
        List<Task> overdueTasks = taskRepository
            .findOverdueTasks(LocalDate.now());

        for (Task task : overdueTasks) {
            task.setOverdue(true);
            task.setUpdatedAt(LocalDateTime.now());
        }

        taskRepository.saveAll(overdueTasks);
        return overdueTasks.size();
    }

    @Transactional(readOnly = true)
    public Page<TaskResponse> getAllTasks(Pageable pageable) {
        return taskRepository.findAll(pageable)
            .map(TaskResponse::new);
    }
}
```

**Line-by-line explanation of key methods:**

- `@Transactional` ensures that database operations within each method are wrapped in a transaction. If anything fails, the entire operation is rolled back.
- `@Transactional(readOnly = true)` on read-only methods tells Spring and the database driver that no writes will happen, which can improve performance.
- `@Cacheable(value = "tasks", key = "#username + '-' + #pageable.pageNumber")` caches the result. The next time the same user requests the same page, the result comes from the cache instead of the database.
- `@CacheEvict(value = "tasks", allEntries = true)` clears the cache when a task is created, updated, or deleted. This ensures the cache does not serve stale data.
- `findByIdAndUserId(taskId, user.getId())` ensures users can only access their own tasks. Without the `userId` check, a user could access any task by guessing its ID.
- `markOverdueTasks()` finds all tasks where the due date has passed, the task is not completed, and the overdue flag is not yet set. It then marks them as overdue. This method is called by a scheduled task.

### UserService

Create `src/main/java/com/example/tasktracker/service/UserService.java`:

```java
package com.example.tasktracker.service;

import com.example.tasktracker.entity.User;
import com.example.tasktracker.exception.ResourceNotFoundException;
import com.example.tasktracker.repository.UserRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public Page<User> getAllUsers(Pageable pageable) {
        return userRepository.findAll(pageable);
    }

    public User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
            .orElseThrow(() -> new ResourceNotFoundException(
                "User not found: " + username
            ));
    }
}
```

---

## B.9 Scheduled Task for Overdue Check

Create `src/main/java/com/example/tasktracker/scheduler/OverdueTaskScheduler.java`:

```java
package com.example.tasktracker.scheduler;

import com.example.tasktracker.service.TaskService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class OverdueTaskScheduler {

    private static final Logger logger =
        LoggerFactory.getLogger(OverdueTaskScheduler.class);

    private final TaskService taskService;

    public OverdueTaskScheduler(TaskService taskService) {
        this.taskService = taskService;
    }

    @Scheduled(cron = "0 0 * * * *")
    public void checkOverdueTasks() {
        logger.info("Running overdue task check...");
        int count = taskService.markOverdueTasks();
        logger.info("Marked {} tasks as overdue", count);
    }
}
```

**Line-by-line explanation:**

- `@Scheduled(cron = "0 0 * * * *")` runs this method at the start of every hour. The cron expression means: second 0, minute 0, every hour, every day, every month, every day of the week.
- `taskService.markOverdueTasks()` calls the service method that finds and marks overdue tasks. It returns the count of newly marked tasks.
- We use SLF4J logging instead of `System.out.println` for proper log management.

**Output in the console:**

```
INFO  c.e.t.scheduler.OverdueTaskScheduler : Running overdue task check...
INFO  c.e.t.scheduler.OverdueTaskScheduler : Marked 3 tasks as overdue
```

---

## B.10 REST Controllers

### AuthController

Create `src/main/java/com/example/tasktracker/controller/AuthController.java`:

```java
package com.example.tasktracker.controller;

import com.example.tasktracker.dto.AuthResponse;
import com.example.tasktracker.dto.LoginRequest;
import com.example.tasktracker.dto.RegisterRequest;
import com.example.tasktracker.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@Tag(name = "Authentication", description = "Register and login endpoints")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/register")
    @Operation(summary = "Register a new user")
    public ResponseEntity<AuthResponse> register(
            @Valid @RequestBody RegisterRequest request) {

        AuthResponse response = authService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @PostMapping("/login")
    @Operation(summary = "Log in and receive a JWT token")
    public ResponseEntity<AuthResponse> login(
            @Valid @RequestBody LoginRequest request) {

        AuthResponse response = authService.login(request);
        return ResponseEntity.ok(response);
    }
}
```

**Sample request and response for registration:**

```
POST /api/auth/register
Content-Type: application/json

{
    "username": "alice",
    "email": "alice@example.com",
    "password": "password123"
}
```

**Response (201 Created):**

```json
{
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbGljZSIs...",
    "username": "alice",
    "role": "USER"
}
```

**Sample request and response for login:**

```
POST /api/auth/login
Content-Type: application/json

{
    "username": "alice",
    "password": "password123"
}
```

**Response (200 OK):**

```json
{
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbGljZSIs...",
    "username": "alice",
    "role": "USER"
}
```

### TaskController

Create `src/main/java/com/example/tasktracker/controller/TaskController.java`:

```java
package com.example.tasktracker.controller;

import com.example.tasktracker.dto.TaskRequest;
import com.example.tasktracker.dto.TaskResponse;
import com.example.tasktracker.entity.TaskPriority;
import com.example.tasktracker.entity.TaskStatus;
import com.example.tasktracker.service.TaskService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/tasks")
@SecurityRequirement(name = "bearerAuth")
@Tag(name = "Tasks", description = "Task management endpoints")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @PostMapping
    @Operation(summary = "Create a new task")
    public ResponseEntity<TaskResponse> createTask(
            @Valid @RequestBody TaskRequest request,
            Authentication authentication) {

        String username = authentication.getName();
        TaskResponse response = taskService.createTask(request, username);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping
    @Operation(summary = "Get all tasks for the current user")
    public ResponseEntity<Page<TaskResponse>> getMyTasks(
            @PageableDefault(size = 10, sort = "createdAt")
            Pageable pageable,
            Authentication authentication) {

        String username = authentication.getName();
        Page<TaskResponse> tasks =
            taskService.getTasksByUser(username, pageable);
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get a specific task by ID")
    public ResponseEntity<TaskResponse> getTask(
            @PathVariable Long id,
            Authentication authentication) {

        String username = authentication.getName();
        TaskResponse response = taskService.getTaskById(id, username);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/status/{status}")
    @Operation(summary = "Get tasks filtered by status")
    public ResponseEntity<Page<TaskResponse>> getTasksByStatus(
            @PathVariable TaskStatus status,
            @PageableDefault(size = 10) Pageable pageable,
            Authentication authentication) {

        String username = authentication.getName();
        Page<TaskResponse> tasks =
            taskService.getTasksByStatus(username, status, pageable);
        return ResponseEntity.ok(tasks);
    }

    @GetMapping("/priority/{priority}")
    @Operation(summary = "Get tasks filtered by priority")
    public ResponseEntity<Page<TaskResponse>> getTasksByPriority(
            @PathVariable TaskPriority priority,
            @PageableDefault(size = 10) Pageable pageable,
            Authentication authentication) {

        String username = authentication.getName();
        Page<TaskResponse> tasks =
            taskService.getTasksByPriority(username, priority, pageable);
        return ResponseEntity.ok(tasks);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update a task")
    public ResponseEntity<TaskResponse> updateTask(
            @PathVariable Long id,
            @Valid @RequestBody TaskRequest request,
            Authentication authentication) {

        String username = authentication.getName();
        TaskResponse response =
            taskService.updateTask(id, request, username);
        return ResponseEntity.ok(response);
    }

    @PatchMapping("/{id}/status")
    @Operation(summary = "Update task status")
    public ResponseEntity<TaskResponse> updateTaskStatus(
            @PathVariable Long id,
            @RequestBody Map<String, String> body,
            Authentication authentication) {

        String username = authentication.getName();
        TaskStatus status = TaskStatus.valueOf(
            body.get("status").toUpperCase()
        );
        TaskResponse response =
            taskService.updateTaskStatus(id, status, username);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete a task")
    public ResponseEntity<Void> deleteTask(
            @PathVariable Long id,
            Authentication authentication) {

        String username = authentication.getName();
        taskService.deleteTask(id, username);
        return ResponseEntity.noContent().build();
    }
}
```

**Line-by-line explanation of key features:**

- `Authentication authentication` is injected by Spring Security. It contains the currently logged-in user's information (extracted from the JWT token by our filter).
- `authentication.getName()` returns the username stored in the JWT token.
- `@PageableDefault(size = 10, sort = "createdAt")` sets default pagination: 10 items per page, sorted by creation date. Clients can override with query parameters like `?page=0&size=20&sort=title`.
- `@SecurityRequirement(name = "bearerAuth")` tells Swagger that these endpoints require a Bearer token.
- `@PatchMapping("/{id}/status")` uses PATCH because we are partially updating the task (only the status field).

**Sample request to create a task (with JWT token):**

```
POST /api/tasks
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "title": "Complete Spring Boot book",
    "description": "Read all chapters and do the exercises",
    "priority": "HIGH",
    "dueDate": "2024-12-31"
}
```

**Response (201 Created):**

```json
{
    "id": 1,
    "title": "Complete Spring Boot book",
    "description": "Read all chapters and do the exercises",
    "status": "TODO",
    "priority": "HIGH",
    "dueDate": "2024-12-31",
    "overdue": false,
    "createdAt": "2024-01-15T10:30:00",
    "updatedAt": "2024-01-15T10:30:00",
    "username": "alice"
}
```

**Sample request to get tasks with pagination:**

```
GET /api/tasks?page=0&size=5&sort=priority,desc
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

**Response (200 OK):**

```json
{
    "content": [
        {
            "id": 1,
            "title": "Complete Spring Boot book",
            "status": "TODO",
            "priority": "HIGH",
            "dueDate": "2024-12-31",
            "overdue": false,
            "username": "alice"
        }
    ],
    "pageable": {
        "pageNumber": 0,
        "pageSize": 5
    },
    "totalElements": 1,
    "totalPages": 1,
    "last": true,
    "first": true
}
```

### AdminController

Create `src/main/java/com/example/tasktracker/controller/AdminController.java`:

```java
package com.example.tasktracker.controller;

import com.example.tasktracker.dto.TaskResponse;
import com.example.tasktracker.entity.User;
import com.example.tasktracker.service.TaskService;
import com.example.tasktracker.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
@SecurityRequirement(name = "bearerAuth")
@Tag(name = "Admin", description = "Admin-only endpoints")
public class AdminController {

    private final UserService userService;
    private final TaskService taskService;

    public AdminController(UserService userService,
                           TaskService taskService) {
        this.userService = userService;
        this.taskService = taskService;
    }

    @GetMapping("/users")
    @Operation(summary = "Get all users (admin only)")
    public ResponseEntity<Page<User>> getAllUsers(
            @PageableDefault(size = 10) Pageable pageable) {

        return ResponseEntity.ok(userService.getAllUsers(pageable));
    }

    @GetMapping("/tasks")
    @Operation(summary = "Get all tasks from all users (admin only)")
    public ResponseEntity<Page<TaskResponse>> getAllTasks(
            @PageableDefault(size = 10) Pageable pageable) {

        return ResponseEntity.ok(taskService.getAllTasks(pageable));
    }
}
```

---

## B.11 OpenAPI Configuration

Create `src/main/java/com/example/tasktracker/config/OpenApiConfig.java`:

```java
package com.example.tasktracker.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Contact;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.security.SecurityScheme;
import org.springframework.context.annotation.Configuration;

@Configuration
@OpenAPIDefinition(
    info = @Info(
        title = "TaskTracker API",
        version = "1.0",
        description = "A task management REST API built with Spring Boot",
        contact = @Contact(name = "Developer", email = "dev@example.com")
    )
)
@SecurityScheme(
    name = "bearerAuth",
    type = SecuritySchemeType.HTTP,
    bearerFormat = "JWT",
    scheme = "bearer"
)
public class OpenApiConfig {
}
```

After starting the application, you can view the interactive API documentation at `http://localhost:8080/swagger-ui.html`.

---

## B.12 Cache Configuration

Create `src/main/java/com/example/tasktracker/config/CacheConfig.java`:

```java
package com.example.tasktracker.config;

import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableCaching
public class CacheConfig {
}
```

The `@EnableCaching` annotation activates Spring's cache infrastructure. Combined with `spring.cache.type=simple` in `application.properties`, this uses a `ConcurrentHashMap`-based cache. The `@Cacheable` and `@CacheEvict` annotations in `TaskService` handle the caching logic.

---

## B.13 Data Initializer

For testing purposes, let us create some sample data when the application starts.

Create `src/main/java/com/example/tasktracker/config/DataInitializer.java`:

```java
package com.example.tasktracker.config;

import com.example.tasktracker.entity.Role;
import com.example.tasktracker.entity.Task;
import com.example.tasktracker.entity.TaskPriority;
import com.example.tasktracker.entity.User;
import com.example.tasktracker.repository.TaskRepository;
import com.example.tasktracker.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDate;

@Configuration
public class DataInitializer {

    @Bean
    CommandLineRunner initData(UserRepository userRepository,
                               TaskRepository taskRepository,
                               PasswordEncoder passwordEncoder) {

        return args -> {
            // Create admin user
            User admin = new User(
                "admin",
                "admin@example.com",
                passwordEncoder.encode("admin123")
            );
            admin.setRole(Role.ADMIN);
            userRepository.save(admin);

            // Create regular user
            User alice = new User(
                "alice",
                "alice@example.com",
                passwordEncoder.encode("password123")
            );
            userRepository.save(alice);

            // Create sample tasks for alice
            taskRepository.save(new Task(
                "Read Spring Boot documentation",
                "Go through the official Spring Boot docs",
                TaskPriority.HIGH,
                LocalDate.now().plusDays(7),
                alice
            ));

            taskRepository.save(new Task(
                "Build a REST API",
                "Create a complete REST API with CRUD operations",
                TaskPriority.MEDIUM,
                LocalDate.now().plusDays(14),
                alice
            ));

            taskRepository.save(new Task(
                "Learn Docker basics",
                "Understand containers and images",
                TaskPriority.LOW,
                LocalDate.now().minusDays(2),
                alice
            ));

            System.out.println("Sample data initialized!");
            System.out.println("Admin: admin / admin123");
            System.out.println("User:  alice / password123");
        };
    }
}
```

**Output when the application starts:**

```
Sample data initialized!
Admin: admin / admin123
User:  alice / password123
```

---

## B.14 Main Application Class

Update `src/main/java/com/example/tasktracker/TasktrackerApplication.java`:

```java
package com.example.tasktracker;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class TasktrackerApplication {

    public static void main(String[] args) {
        SpringApplication.run(TasktrackerApplication.class, args);
    }
}
```

---

## B.15 Writing Tests

### Testing the AuthController

Create `src/test/java/com/example/tasktracker/controller/AuthControllerTest.java`:

```java
package com.example.tasktracker.controller;

import com.example.tasktracker.dto.AuthResponse;
import com.example.tasktracker.dto.RegisterRequest;
import com.example.tasktracker.security.JwtUtil;
import com.example.tasktracker.service.AuthService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void registerShouldReturnToken() throws Exception {
        RegisterRequest request = new RegisterRequest(
            "testuser", "test@example.com", "password123"
        );

        mockMvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.token").isNotEmpty())
            .andExpect(jsonPath("$.username").value("testuser"))
            .andExpect(jsonPath("$.role").value("USER"));
    }

    @Test
    void registerWithInvalidDataShouldReturn400() throws Exception {
        RegisterRequest request = new RegisterRequest("", "", "12");

        mockMvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.errors").isNotEmpty());
    }

    @Test
    void loginWithValidCredentialsShouldReturnToken() throws Exception {
        String loginJson = """
            {
                "username": "alice",
                "password": "password123"
            }
            """;

        mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(loginJson))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.token").isNotEmpty())
            .andExpect(jsonPath("$.username").value("alice"));
    }

    @Test
    void loginWithInvalidPasswordShouldReturn401() throws Exception {
        String loginJson = """
            {
                "username": "alice",
                "password": "wrongpassword"
            }
            """;

        mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(loginJson))
            .andExpect(status().isUnauthorized());
    }
}
```

### Testing the TaskController

Create `src/test/java/com/example/tasktracker/controller/TaskControllerTest.java`:

```java
package com.example.tasktracker.controller;

import com.example.tasktracker.dto.AuthResponse;
import com.example.tasktracker.dto.LoginRequest;
import com.example.tasktracker.service.AuthService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class TaskControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private AuthService authService;

    private String token;

    @BeforeEach
    void setUp() {
        AuthResponse response = authService.login(
            new LoginRequest("alice", "password123")
        );
        token = response.getToken();
    }

    @Test
    void createTaskShouldReturn201() throws Exception {
        String taskJson = """
            {
                "title": "Test task",
                "description": "A task for testing",
                "priority": "HIGH",
                "dueDate": "2024-12-31"
            }
            """;

        mockMvc.perform(post("/api/tasks")
                .header("Authorization", "Bearer " + token)
                .contentType(MediaType.APPLICATION_JSON)
                .content(taskJson))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.title").value("Test task"))
            .andExpect(jsonPath("$.priority").value("HIGH"))
            .andExpect(jsonPath("$.status").value("TODO"));
    }

    @Test
    void getTasksShouldReturnPaginatedResults() throws Exception {
        mockMvc.perform(get("/api/tasks")
                .header("Authorization", "Bearer " + token)
                .param("page", "0")
                .param("size", "5"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.content").isArray())
            .andExpect(jsonPath("$.totalElements").isNumber());
    }

    @Test
    void getTaskWithoutTokenShouldReturn403() throws Exception {
        mockMvc.perform(get("/api/tasks"))
            .andExpect(status().isForbidden());
    }

    @Test
    void deleteTaskShouldReturn204() throws Exception {
        // First, create a task
        String taskJson = """
            {
                "title": "Task to delete",
                "description": "Will be deleted",
                "priority": "LOW"
            }
            """;

        String responseBody = mockMvc.perform(post("/api/tasks")
                .header("Authorization", "Bearer " + token)
                .contentType(MediaType.APPLICATION_JSON)
                .content(taskJson))
            .andExpect(status().isCreated())
            .andReturn()
            .getResponse()
            .getContentAsString();

        Long taskId = objectMapper.readTree(responseBody).get("id").asLong();

        // Then, delete it
        mockMvc.perform(delete("/api/tasks/" + taskId)
                .header("Authorization", "Bearer " + token))
            .andExpect(status().isNoContent());
    }
}
```

### Testing the TaskService

Create `src/test/java/com/example/tasktracker/service/TaskServiceTest.java`:

```java
package com.example.tasktracker.service;

import com.example.tasktracker.dto.TaskRequest;
import com.example.tasktracker.dto.TaskResponse;
import com.example.tasktracker.exception.ResourceNotFoundException;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

@SpringBootTest
class TaskServiceTest {

    @Autowired
    private TaskService taskService;

    @Test
    void createTaskShouldReturnTaskResponse() {
        TaskRequest request = new TaskRequest(
            "Service test task", "Testing the service", "HIGH", null
        );

        TaskResponse response = taskService.createTask(request, "alice");

        assertNotNull(response.getId());
        assertEquals("Service test task", response.getTitle());
        assertEquals("HIGH", response.getPriority());
        assertEquals("TODO", response.getStatus());
    }

    @Test
    void getTasksByUserShouldReturnPaginatedResults() {
        Page<TaskResponse> tasks = taskService.getTasksByUser(
            "alice", PageRequest.of(0, 10)
        );

        assertNotNull(tasks);
        assertEquals(0, tasks.getNumber());
    }

    @Test
    void getTaskByIdWithWrongUserShouldThrowException() {
        assertThrows(ResourceNotFoundException.class, () -> {
            taskService.getTaskById(999L, "alice");
        });
    }

    @Test
    void markOverdueTasksShouldReturnCount() {
        int count = taskService.markOverdueTasks();
        assertNotNull(count);
    }
}
```

**Output when you run `mvn test`:**

```
[INFO] Running com.example.tasktracker.controller.AuthControllerTest
[INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.example.tasktracker.controller.TaskControllerTest
[INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.example.tasktracker.service.TaskServiceTest
[INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
[INFO]
[INFO] Results:
[INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
[INFO]
[INFO] BUILD SUCCESS
```

---

## B.16 Dockerfile

Create a `Dockerfile` in the project root directory:

```dockerfile
# Stage 1: Build the application
FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
COPY .mvn ./.mvn
COPY mvnw .
RUN chmod +x mvnw
RUN ./mvnw clean package -DskipTests

# Stage 2: Run the application
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Line-by-line explanation:**

- `FROM eclipse-temurin:17-jdk-alpine AS build` uses a lightweight Alpine Linux image with Java 17 JDK for building the application. This is the "build stage."
- `COPY pom.xml .` and `COPY src ./src` copy the project files into the container.
- `RUN ./mvnw clean package -DskipTests` builds the JAR file inside the container, skipping tests (they should pass before you build the Docker image).
- `FROM eclipse-temurin:17-jre-alpine` starts a new stage with only the JRE (no JDK). This makes the final image smaller because you only need the runtime to run the application.
- `COPY --from=build /app/target/*.jar app.jar` copies the built JAR from the build stage.
- `EXPOSE 8080` documents that the application listens on port 8080.
- `ENTRYPOINT ["java", "-jar", "app.jar"]` starts the application.

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t tasktracker .

# Run the container
docker run -p 8080:8080 tasktracker
```

**Output:**

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/

 :: Spring Boot ::                (v3.4.x)

INFO  --- Started TasktrackerApplication in 3.2 seconds
Sample data initialized!
Admin: admin / admin123
User:  alice / password123
```

---

## B.17 Complete Project Structure

Here is the full project structure for reference:

```
tasktracker/
+-- src/
|   +-- main/
|   |   +-- java/com/example/tasktracker/
|   |   |   +-- TasktrackerApplication.java
|   |   |   +-- config/
|   |   |   |   +-- CacheConfig.java
|   |   |   |   +-- DataInitializer.java
|   |   |   |   +-- OpenApiConfig.java
|   |   |   +-- controller/
|   |   |   |   +-- AdminController.java
|   |   |   |   +-- AuthController.java
|   |   |   |   +-- TaskController.java
|   |   |   +-- dto/
|   |   |   |   +-- AuthResponse.java
|   |   |   |   +-- ErrorResponse.java
|   |   |   |   +-- LoginRequest.java
|   |   |   |   +-- RegisterRequest.java
|   |   |   |   +-- TaskRequest.java
|   |   |   |   +-- TaskResponse.java
|   |   |   +-- entity/
|   |   |   |   +-- Role.java
|   |   |   |   +-- Task.java
|   |   |   |   +-- TaskPriority.java
|   |   |   |   +-- TaskStatus.java
|   |   |   |   +-- User.java
|   |   |   +-- exception/
|   |   |   |   +-- DuplicateResourceException.java
|   |   |   |   +-- GlobalExceptionHandler.java
|   |   |   |   +-- ResourceNotFoundException.java
|   |   |   |   +-- UnauthorizedException.java
|   |   |   +-- repository/
|   |   |   |   +-- TaskRepository.java
|   |   |   |   +-- UserRepository.java
|   |   |   +-- scheduler/
|   |   |   |   +-- OverdueTaskScheduler.java
|   |   |   +-- security/
|   |   |   |   +-- JwtAuthenticationFilter.java
|   |   |   |   +-- JwtUtil.java
|   |   |   |   +-- SecurityConfig.java
|   |   |   +-- service/
|   |   |       +-- AuthService.java
|   |   |       +-- TaskService.java
|   |   |       +-- UserService.java
|   |   +-- resources/
|   |       +-- application.properties
|   +-- test/
|       +-- java/com/example/tasktracker/
|           +-- TasktrackerApplicationTests.java
|           +-- controller/
|           |   +-- AuthControllerTest.java
|           |   +-- TaskControllerTest.java
|           +-- service/
|               +-- TaskServiceTest.java
+-- Dockerfile
+-- pom.xml
```

---

## B.18 API Endpoint Summary

Here is a quick reference of all the endpoints in the TaskTracker API:

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | /api/auth/register | Public | Register a new user |
| POST | /api/auth/login | Public | Log in and get JWT token |
| POST | /api/tasks | Authenticated | Create a new task |
| GET | /api/tasks | Authenticated | Get your tasks (paginated) |
| GET | /api/tasks/{id} | Authenticated | Get a specific task |
| GET | /api/tasks/status/{status} | Authenticated | Filter tasks by status |
| GET | /api/tasks/priority/{priority} | Authenticated | Filter tasks by priority |
| PUT | /api/tasks/{id} | Authenticated | Update a task |
| PATCH | /api/tasks/{id}/status | Authenticated | Update task status |
| DELETE | /api/tasks/{id} | Authenticated | Delete a task |
| GET | /api/admin/users | Admin only | Get all users |
| GET | /api/admin/tasks | Admin only | Get all tasks |

```
Testing Flow:

1. Register: POST /api/auth/register
   -> Get JWT token

2. Create Task: POST /api/tasks (with token)
   -> Get task with ID

3. List Tasks: GET /api/tasks (with token)
   -> See paginated results

4. Update Status: PATCH /api/tasks/1/status (with token)
   -> Change TODO to IN_PROGRESS

5. Filter: GET /api/tasks/status/IN_PROGRESS (with token)
   -> See filtered results

6. Delete: DELETE /api/tasks/1 (with token)
   -> 204 No Content
```

---

## Common Mistakes

1. **Forgetting @EnableScheduling.** The overdue task checker uses `@Scheduled`, which requires `@EnableScheduling` on the main application class or a configuration class.

2. **Not adding @EnableCaching.** The `@Cacheable` and `@CacheEvict` annotations are ignored unless caching is enabled.

3. **Storing plain-text passwords.** Always use `PasswordEncoder` to hash passwords before saving. Never store passwords in plain text.

4. **Not checking task ownership.** Always verify that the task belongs to the requesting user. Use `findByIdAndUserId` instead of just `findById`.

5. **Using @RestController for WebSocket handlers.** When you add WebSocket to this project later, remember to use `@Controller` for WebSocket message handlers.

6. **Returning entities directly from controllers.** Use DTOs (like `TaskResponse`) to control what data is sent to the client. Returning the `User` entity directly would expose the password hash.

---

## Best Practices

1. **Separate concerns into layers.** Keep controllers thin. Put business logic in services. Let repositories handle data access.

2. **Use DTOs for input and output.** DTOs decouple your API contract from your database structure. You can change your entities without breaking the API.

3. **Validate input at the controller level.** Use `@Valid` and Jakarta Validation annotations to reject bad data before it reaches your service layer.

4. **Handle exceptions globally.** Use `@RestControllerAdvice` to return consistent error responses across all endpoints.

5. **Write tests.** Even basic tests catch many bugs. Test your controllers with MockMvc and your services with JUnit.

6. **Use environment variables for secrets.** Never hardcode JWT secrets or database passwords in `application.properties` for production. Use environment variables or a secrets manager.

---

## Quick Summary

The TaskTracker API is a complete Spring Boot application that demonstrates entities and JPA relationships, repositories with custom queries and pagination, services with business logic and transactions, REST controllers with validation and authentication, JWT security with role-based access control, caching for performance, scheduled tasks for automated checks, global exception handling, OpenAPI documentation, integration and service tests, and Docker containerization. This project uses every major concept from the book and shows how they work together in a real application.

---

## Key Points

- Start with entities and work your way up through repositories, services, and controllers.
- Use DTOs to separate your API contract from your internal data model.
- Use `@Valid` for input validation and `@RestControllerAdvice` for exception handling.
- JWT tokens provide stateless authentication. The server does not need to store sessions.
- Role-based access control (USER, ADMIN) restricts what users can do.
- `@Cacheable` improves read performance. `@CacheEvict` keeps the cache fresh.
- `@Scheduled` automates recurring tasks like checking for overdue items.
- OpenAPI (Swagger) generates interactive API documentation automatically.
- Docker packages your application into a portable container.

---

## Practice Questions

1. Why do we use DTOs instead of returning the User entity directly from controllers?

2. Explain why the login method uses the same error message for both "user not found" and "wrong password." What security risk would a more specific message create?

3. What is the purpose of `@Transactional(readOnly = true)` on read-only service methods?

4. How does `findByIdAndUserId` in TaskRepository prevent users from accessing other users' tasks?

5. Why do we use a multi-stage Dockerfile? What is the benefit of separating build and runtime stages?

---

## Exercises

### Exercise 1: Add Task Search

Add a new endpoint `GET /api/tasks/search?keyword=spring` that searches tasks by title or description containing the keyword. Add the query method to `TaskRepository` and the logic to `TaskService`.

### Exercise 2: Add User Profile

Create a `GET /api/profile` endpoint that returns the current user's information along with task statistics (total tasks, completed tasks, overdue tasks). Create a `ProfileResponse` DTO for this.

### Exercise 3: Add Task Comments

Add a `Comment` entity with a many-to-one relationship to `Task`. Create endpoints to add comments to a task (`POST /api/tasks/{id}/comments`) and list comments for a task (`GET /api/tasks/{id}/comments`).

---

## Congratulations!

You have built a complete, production-ready REST API from scratch. You started with empty files and ended with a fully functional application that includes authentication, authorization, validation, error handling, pagination, caching, scheduled tasks, documentation, tests, and Docker support.

This is a significant achievement. You now understand how all the pieces of a Spring Boot application fit together. You can confidently build similar applications for your own projects or for your employer.

### What to Learn Next

Here are some topics to explore as you continue your Spring Boot journey:

1. **Spring WebFlux** - Build reactive, non-blocking applications for high-concurrency use cases.
2. **Microservices with Spring Cloud** - Break large applications into smaller, independently deployable services.
3. **Message Queues (RabbitMQ, Apache Kafka)** - Handle asynchronous communication between services.
4. **PostgreSQL or MySQL** - Replace H2 with a production-grade database.
5. **CI/CD Pipelines** - Automate testing and deployment with GitHub Actions, Jenkins, or GitLab CI.
6. **Kubernetes** - Orchestrate your Docker containers at scale.
7. **Spring Boot Actuator** - Add production-ready monitoring and health checks (covered in Chapter 28).
8. **GraphQL with Spring** - Build flexible APIs that let clients request exactly the data they need.

Keep building. Keep learning. The best way to master Spring Boot is to use it in real projects. Good luck!
