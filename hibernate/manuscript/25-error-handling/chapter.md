# Chapter 25: Error Handling and Exception Translation

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand Spring's persistence exception translation mechanism
- Handle common JPA/Hibernate exceptions (DataIntegrityViolation, OptimisticLock, etc.)
- Create custom business exceptions with meaningful messages
- Build a global exception handler with @ControllerAdvice
- Design a consistent error response format for REST APIs
- Map database constraint violations to user-friendly messages
- Handle validation errors from Bean Validation
- Use Problem Details (RFC 9457) for standardized error responses

---

## Spring's Exception Translation

Spring automatically translates low-level JPA/Hibernate exceptions into Spring's `DataAccessException` hierarchy. This happens because of `@Repository` and Spring's persistence exception translation.

```
Exception Translation Flow:
+------------------------------------------------------------------+
|                                                                   |
|  Your Code                                                        |
|  repository.save(employee);                                       |
|       |                                                           |
|       v                                                           |
|  Hibernate throws:                                                |
|  jakarta.persistence.PersistenceException                         |
|  org.hibernate.exception.ConstraintViolationException             |
|       |                                                           |
|       v                                                           |
|  Spring @Repository translates to:                                |
|  org.springframework.dao.DataIntegrityViolationException          |
|       |                                                           |
|       v                                                           |
|  Your service catches Spring's exception                          |
|  (not Hibernate's — your code is provider-independent)            |
+------------------------------------------------------------------+
```

### Common Spring Data Access Exceptions

```
Spring Exception Hierarchy:
+------------------------------------------------------------------+
|                                                                   |
|  DataAccessException (root)                                       |
|  |                                                                |
|  +-- NonTransientDataAccessException                              |
|  |   |  (permanent errors — retrying won't help)                  |
|  |   |                                                            |
|  |   +-- DataIntegrityViolationException                          |
|  |   |   Unique constraint violation                              |
|  |   |   Foreign key violation                                    |
|  |   |   NOT NULL violation                                       |
|  |   |                                                            |
|  |   +-- EmptyResultDataAccessException                           |
|  |   |   Expected one result, got none                            |
|  |   |                                                            |
|  |   +-- IncorrectResultSizeDataAccessException                   |
|  |       Expected one result, got many                            |
|  |                                                                |
|  +-- TransientDataAccessException                                 |
|  |   |  (temporary errors — retrying might help)                  |
|  |   |                                                            |
|  |   +-- CannotAcquireLockException                               |
|  |   |   Row or table lock timeout                                |
|  |   |                                                            |
|  |   +-- OptimisticLockingFailureException                        |
|  |       @Version mismatch (concurrent update detected)           |
|  |                                                                |
|  +-- InvalidDataAccessApiUsageException                           |
|      Wrong API usage (e.g., query syntax error)                   |
+------------------------------------------------------------------+
```

---

## Custom Business Exceptions

Create domain-specific exceptions that communicate what went wrong in business terms:

```java
// Base business exception
public class BusinessException extends RuntimeException {

    private final String errorCode;

    public BusinessException(String message) {
        super(message);
        this.errorCode = "BUSINESS_ERROR";
    }

    public BusinessException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public String getErrorCode() { return errorCode; }
}

// Specific exceptions
public class ResourceNotFoundException extends BusinessException {

    public ResourceNotFoundException(String resource, Long id) {
        super("NOT_FOUND",
              String.format("%s with id %d not found", resource, id));
    }

    public ResourceNotFoundException(String resource, String field, String value) {
        super("NOT_FOUND",
              String.format("%s with %s '%s' not found", resource, field, value));
    }
}

public class DuplicateResourceException extends BusinessException {

    public DuplicateResourceException(String resource, String field, String value) {
        super("DUPLICATE",
              String.format("%s with %s '%s' already exists", resource, field, value));
    }
}

public class InsufficientStockException extends BusinessException {

    public InsufficientStockException(String productName, int requested, int available) {
        super("INSUFFICIENT_STOCK",
              String.format("Product '%s': requested %d but only %d available",
                  productName, requested, available));
    }
}
```

### Using in Services

```java
@Service
public class EmployeeService {

    @Transactional
    public EmployeeResponse create(CreateEmployeeRequest request) {
        // Check for duplicate email
        if (employeeRepository.existsByEmail(request.getEmail())) {
            throw new DuplicateResourceException("Employee", "email", request.getEmail());
        }

        Department dept = departmentRepository.findById(request.getDepartmentId())
            .orElseThrow(() -> new ResourceNotFoundException("Department",
                request.getDepartmentId()));

        Employee employee = new Employee(request.getName(), request.getEmail());
        employee.setDepartment(dept);
        return mapper.toResponse(employeeRepository.save(employee));
    }

    @Transactional(readOnly = true)
    public EmployeeResponse getById(Long id) {
        Employee employee = employeeRepository.findWithDeptById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Employee", id));
        return mapper.toResponse(employee);
    }
}
```

---

## Consistent Error Response Format

Define a standard error response structure for your API:

```java
public class ErrorResponse {

    private int status;
    private String error;
    private String message;
    private String path;
    private LocalDateTime timestamp;
    private Map<String, String> fieldErrors;  // For validation errors

    public ErrorResponse(int status, String error, String message, String path) {
        this.status = status;
        this.error = error;
        this.message = message;
        this.path = path;
        this.timestamp = LocalDateTime.now();
    }

    public void setFieldErrors(Map<String, String> fieldErrors) {
        this.fieldErrors = fieldErrors;
    }

    // Getters...
}
```

```
Error Response Examples:
+------------------------------------------------------------------+
|                                                                   |
|  404 Not Found:                                                   |
|  {                                                                |
|    "status": 404,                                                 |
|    "error": "NOT_FOUND",                                          |
|    "message": "Employee with id 42 not found",                    |
|    "path": "/api/employees/42",                                   |
|    "timestamp": "2025-09-15T14:30:00"                             |
|  }                                                                |
|                                                                   |
|  400 Validation Error:                                            |
|  {                                                                |
|    "status": 400,                                                 |
|    "error": "VALIDATION_FAILED",                                  |
|    "message": "Request validation failed",                        |
|    "path": "/api/employees",                                      |
|    "timestamp": "2025-09-15T14:30:00",                            |
|    "fieldErrors": {                                               |
|      "name": "Name is required",                                  |
|      "email": "Must be a valid email",                            |
|      "salary": "Salary must be positive"                          |
|    }                                                              |
|  }                                                                |
|                                                                   |
|  409 Conflict:                                                    |
|  {                                                                |
|    "status": 409,                                                 |
|    "error": "DUPLICATE",                                          |
|    "message": "Employee with email 'a@co.com' already exists",    |
|    "path": "/api/employees",                                      |
|    "timestamp": "2025-09-15T14:30:00"                             |
|  }                                                                |
+------------------------------------------------------------------+
```

---

## Global Exception Handler with @ControllerAdvice

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // === Business Exceptions ===

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex, HttpServletRequest request) {
        ErrorResponse error = new ErrorResponse(
            404, ex.getErrorCode(), ex.getMessage(), request.getRequestURI());
        return ResponseEntity.status(404).body(error);
    }

    @ExceptionHandler(DuplicateResourceException.class)
    public ResponseEntity<ErrorResponse> handleDuplicate(
            DuplicateResourceException ex, HttpServletRequest request) {
        ErrorResponse error = new ErrorResponse(
            409, ex.getErrorCode(), ex.getMessage(), request.getRequestURI());
        return ResponseEntity.status(409).body(error);
    }

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusiness(
            BusinessException ex, HttpServletRequest request) {
        ErrorResponse error = new ErrorResponse(
            422, ex.getErrorCode(), ex.getMessage(), request.getRequestURI());
        return ResponseEntity.status(422).body(error);
    }

    // === Validation Exceptions ===

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            MethodArgumentNotValidException ex, HttpServletRequest request) {

        Map<String, String> fieldErrors = new LinkedHashMap<>();
        for (FieldError fe : ex.getBindingResult().getFieldErrors()) {
            fieldErrors.put(fe.getField(), fe.getDefaultMessage());
        }

        ErrorResponse error = new ErrorResponse(
            400, "VALIDATION_FAILED", "Request validation failed",
            request.getRequestURI());
        error.setFieldErrors(fieldErrors);

        return ResponseEntity.badRequest().body(error);
    }

    // === JPA / Database Exceptions ===

    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<ErrorResponse> handleDataIntegrity(
            DataIntegrityViolationException ex, HttpServletRequest request) {

        String message = "Data integrity violation";

        // Extract meaningful message from constraint name
        String rootMessage = ex.getMostSpecificCause().getMessage();
        if (rootMessage != null) {
            if (rootMessage.contains("UNIQUE") || rootMessage.contains("unique")) {
                message = "A record with this value already exists";
            } else if (rootMessage.contains("FOREIGN KEY")) {
                message = "Referenced record does not exist or cannot be deleted";
            } else if (rootMessage.contains("NULL")) {
                message = "A required field is missing";
            }
        }

        ErrorResponse error = new ErrorResponse(
            409, "DATA_INTEGRITY", message, request.getRequestURI());
        return ResponseEntity.status(409).body(error);
    }

    @ExceptionHandler(OptimisticLockingFailureException.class)
    public ResponseEntity<ErrorResponse> handleOptimisticLock(
            OptimisticLockingFailureException ex, HttpServletRequest request) {
        ErrorResponse error = new ErrorResponse(
            409, "CONCURRENT_UPDATE",
            "This record was modified by another user. Please refresh and try again.",
            request.getRequestURI());
        return ResponseEntity.status(409).body(error);
    }

    // === Catch-All ===

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(
            Exception ex, HttpServletRequest request) {
        // Log the full exception for debugging
        log.error("Unhandled exception", ex);

        ErrorResponse error = new ErrorResponse(
            500, "INTERNAL_ERROR", "An unexpected error occurred",
            request.getRequestURI());
        return ResponseEntity.status(500).body(error);
    }

    private static final org.slf4j.Logger log =
        org.slf4j.LoggerFactory.getLogger(GlobalExceptionHandler.class);
}
```

```
Exception Handler Priority:
+------------------------------------------------------------------+
|                                                                   |
|  Exception thrown in service layer                                |
|       |                                                           |
|       v                                                           |
|  Spring looks for matching @ExceptionHandler:                     |
|                                                                   |
|  1. Most specific match first:                                    |
|     ResourceNotFoundException handler (matches exactly)           |
|                                                                   |
|  2. Parent class match:                                           |
|     BusinessException handler (if no specific handler)            |
|                                                                   |
|  3. Catch-all:                                                    |
|     Exception handler (last resort)                               |
|                                                                   |
|  Order matters! Put specific handlers before general ones.        |
+------------------------------------------------------------------+
```

---

## Handling Constraint Violations from Bean Validation

When validation happens at the entity level (not controller), `ConstraintViolationException` is thrown:

```java
@ExceptionHandler(ConstraintViolationException.class)
public ResponseEntity<ErrorResponse> handleConstraintViolation(
        ConstraintViolationException ex, HttpServletRequest request) {

    Map<String, String> fieldErrors = new LinkedHashMap<>();
    for (var violation : ex.getConstraintViolations()) {
        String field = violation.getPropertyPath().toString();
        fieldErrors.put(field, violation.getMessage());
    }

    ErrorResponse error = new ErrorResponse(
        400, "VALIDATION_FAILED", "Constraint validation failed",
        request.getRequestURI());
    error.setFieldErrors(fieldErrors);

    return ResponseEntity.badRequest().body(error);
}
```

---

## Mapping Constraint Names to User Messages

For database-level constraint violations, map constraint names to friendly messages:

```java
@Component
public class ConstraintMessageMapper {

    private final Map<String, String> constraintMessages = Map.of(
        "UK_EMPLOYEE_EMAIL", "An employee with this email already exists",
        "UK_DEPARTMENT_NAME", "A department with this name already exists",
        "FK_EMPLOYEE_DEPARTMENT", "The specified department does not exist",
        "UK_PRODUCT_SKU", "A product with this SKU already exists"
    );

    public String getMessage(DataIntegrityViolationException ex) {
        String rootMessage = ex.getMostSpecificCause().getMessage();

        for (Map.Entry<String, String> entry : constraintMessages.entrySet()) {
            if (rootMessage != null &&
                rootMessage.toUpperCase().contains(entry.getKey())) {
                return entry.getValue();
            }
        }

        return "A data integrity constraint was violated";
    }
}
```

```java
// Use in exception handler
@ExceptionHandler(DataIntegrityViolationException.class)
public ResponseEntity<ErrorResponse> handleDataIntegrity(
        DataIntegrityViolationException ex, HttpServletRequest request) {
    String message = constraintMessageMapper.getMessage(ex);
    ErrorResponse error = new ErrorResponse(409, "DATA_INTEGRITY", message,
        request.getRequestURI());
    return ResponseEntity.status(409).body(error);
}
```

---

## Complete Exception Handling Flow

```
End-to-End Error Handling:
+------------------------------------------------------------------+
|                                                                   |
|  Client sends: POST /api/employees                                |
|  { "name": "", "email": "alice@co.com", "salary": -5 }           |
|       |                                                           |
|       v                                                           |
|  @Valid catches validation errors BEFORE service is called:       |
|  --> 400 { "fieldErrors": { "name": "required", "salary": ">0" }}|
|                                                                   |
|  Client sends: POST /api/employees                                |
|  { "name": "Alice", "email": "existing@co.com", "salary": 80000 }|
|       |                                                           |
|       v                                                           |
|  Service checks: existsByEmail("existing@co.com") == true         |
|  Throws: DuplicateResourceException                               |
|  --> 409 { "error": "DUPLICATE", "message": "already exists" }   |
|                                                                   |
|  Client sends: GET /api/employees/999                             |
|       |                                                           |
|       v                                                           |
|  Service: findById(999) returns empty                             |
|  Throws: ResourceNotFoundException                                |
|  --> 404 { "error": "NOT_FOUND", "message": "not found" }        |
|                                                                   |
|  Client sends: PUT /api/employees/1 (with stale version)         |
|       |                                                           |
|       v                                                           |
|  Hibernate: @Version mismatch                                    |
|  Throws: OptimisticLockingFailureException                       |
|  --> 409 { "error": "CONCURRENT_UPDATE", "message": "refresh" }  |
|                                                                   |
|  Unexpected bug in code:                                          |
|       |                                                           |
|       v                                                           |
|  Throws: NullPointerException (unhandled)                         |
|  Catch-all handler logs it and returns:                           |
|  --> 500 { "error": "INTERNAL_ERROR", "message": "unexpected" }  |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Returning stack traces to clients**: Never include exception stack traces in API responses. Log them server-side, return user-friendly messages to clients.

2. **Using generic 500 for all errors**: Differentiate between 400 (client error), 404 (not found), 409 (conflict), 422 (business rule), and 500 (server error).

3. **Catching exceptions silently in services**: Swallowing exceptions inside `@Transactional` prevents rollback and hides problems. Rethrow or handle explicitly.

4. **Not handling DataIntegrityViolationException**: If you do not check for duplicate emails before saving, the database unique constraint throws `DataIntegrityViolationException`. Handle it with a friendly message.

5. **Inconsistent error response formats**: Some endpoints return `{"error": "..."}`, others return `{"message": "..."}`. Use one consistent format everywhere.

6. **Not logging unexpected exceptions**: The catch-all handler should always log the full exception. Without logging, production bugs are invisible.

---

## Best Practices

1. **Create domain-specific exceptions**: `ResourceNotFoundException`, `DuplicateResourceException`, `InsufficientStockException` communicate intent clearly.

2. **Use @ControllerAdvice for centralized handling**: One class handles all exceptions consistently. No try-catch in controllers.

3. **Validate at the boundary first**: Check for duplicates and invalid references in the service layer before calling save. This gives better error messages than database constraint violations.

4. **Design a consistent error response format**: Same structure for all errors (status, error code, message, timestamp, path). Frontend can parse any error the same way.

5. **Map HTTP status codes correctly**: 400 for validation, 404 for not found, 409 for conflicts/duplicates, 422 for business rule violations, 500 for unexpected errors.

6. **Log server errors, not client errors**: Log 500s with full stack trace. Do not log 400s and 404s (these are expected client behavior).

---

## Summary

- **Spring exception translation** converts Hibernate/JPA exceptions into Spring's `DataAccessException` hierarchy, keeping your code provider-independent.

- **Custom business exceptions** communicate domain problems (not found, duplicate, insufficient stock) with meaningful error codes and messages.

- **@ControllerAdvice** centralizes exception handling. Each `@ExceptionHandler` maps an exception type to an HTTP status and error response.

- **Consistent error response format** with status, error code, message, timestamp, and path lets frontends handle errors uniformly.

- **Validation errors** from `@Valid` produce field-level error maps. Database constraint violations should be mapped to friendly messages.

- **Optimistic locking failures** (`@Version` mismatch) return 409 with a "refresh and retry" message.

- **Catch-all handler** logs unexpected exceptions and returns 500 without exposing internals.

---

## Interview Questions

**Q1: How does Spring translate Hibernate exceptions?**

The `@Repository` annotation enables Spring's persistence exception translation. When Hibernate throws a `PersistenceException` or its subclasses, Spring's `PersistenceExceptionTranslationPostProcessor` catches it and wraps it in a Spring `DataAccessException` subclass. This keeps your service code independent of the JPA provider.

**Q2: What is the difference between DataIntegrityViolationException and ConstraintViolationException?**

`DataIntegrityViolationException` (Spring) is thrown when a database constraint is violated (unique, FK, NOT NULL) — it comes from the database after SQL execution. `ConstraintViolationException` (Jakarta Validation) is thrown when Bean Validation annotations fail — it comes from Java validation before SQL is executed.

**Q3: How does @ControllerAdvice work?**

`@ControllerAdvice` creates a global exception handler that applies to all controllers. Methods annotated with `@ExceptionHandler(SomeException.class)` catch that exception type thrown by any controller method. Spring selects the most specific handler first.

**Q4: What HTTP status codes should you use for common errors?**

400 for validation errors, 404 for resource not found, 409 for conflicts (duplicates, optimistic lock failures), 422 for business rule violations, 500 for unexpected server errors. Never use 200 for errors.

**Q5: Why should you not return stack traces in API responses?**

Stack traces expose internal implementation details (class names, library versions, file paths) that could be exploited by attackers. They also confuse API consumers. Log stack traces server-side and return user-friendly messages to clients.

---

## Practice Exercises

**Exercise 1: Custom Exceptions**
Create `ResourceNotFoundException`, `DuplicateResourceException`, and `InsufficientFundsException`. Use them in a `BankAccountService` with transfer, create, and find operations.

**Exercise 2: Global Exception Handler**
Build a `@ControllerAdvice` that handles your custom exceptions, `MethodArgumentNotValidException`, `DataIntegrityViolationException`, and a catch-all. Test each handler returns the correct HTTP status and error format.

**Exercise 3: Constraint Mapping**
Create a `ConstraintMessageMapper` that maps database constraint names to friendly messages. Test with unique constraint violations on email and department name.

**Exercise 4: Optimistic Locking**
Add `@Version` to an entity. Write a test that simulates concurrent updates: load the entity in two transactions, modify both, save both. Verify `OptimisticLockingFailureException` is thrown and handled with 409.

**Exercise 5: End-to-End Error Testing**
Write integration tests for every error scenario: validation error (400), not found (404), duplicate (409), concurrent update (409), and unexpected error (500). Verify consistent response format for all.

---

## What Is Next?

In the next chapter, we will explore **Database Migrations with Flyway** — how to manage database schema changes in a production-safe way. You will learn why `ddl-auto=update` is dangerous in production, how Flyway versioned migrations work, naming conventions, and how to integrate Flyway with Spring Boot for automatic migration execution.
