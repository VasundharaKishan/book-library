# Chapter 12: Exception Handling

## What You Will Learn

In this chapter, you will learn:

- Why default Spring Boot error responses are not good enough
- How to create custom exception classes
- How to use `@ControllerAdvice` to handle exceptions globally
- How to use `@ExceptionHandler` to catch specific exceptions
- How to design a clean error response DTO
- How to handle validation errors with proper field-level messages
- How to build a complete, production-quality error handling system

## Why This Chapter Matters

Imagine calling a customer service hotline. You explain your problem. The representative says "Error. Goodbye." and hangs up. That is how most APIs respond to errors without proper exception handling.

Good error responses are like a helpful customer service agent. They tell you:
- What went wrong ("The book you requested was not found")
- Why it went wrong ("No book exists with ID 999")
- What you can do about it ("Check the ID and try again")

Without proper exception handling, your API returns ugly stack traces, inconsistent error formats, and generic messages. Clients cannot figure out what they did wrong. Developers cannot debug problems. Your API feels broken even when it is working correctly.

This chapter teaches you to handle every error gracefully and return clean, consistent, helpful responses.

---

## 12.1 The Problem with Default Error Responses

Let us look at what Spring Boot returns by default when things go wrong.

### Default 404 Response

When a resource is not found, Spring returns:

```json
{
    "timestamp": "2024-01-15T10:30:00.000+00:00",
    "status": 404,
    "error": "Not Found",
    "path": "/api/books/999"
}
```

This is okay but generic. It does not tell the client *what* was not found.

### Default Validation Error Response

When validation fails (from Chapter 11), Spring returns:

```json
{
    "timestamp": "2024-01-15T10:30:00.000+00:00",
    "status": 400,
    "error": "Bad Request",
    "path": "/api/books"
}
```

This is worse. The client knows the request was bad but has no idea *which field* was wrong or *why*.

### Default 500 Response

When an unexpected exception occurs:

```json
{
    "timestamp": "2024-01-15T10:30:00.000+00:00",
    "status": 500,
    "error": "Internal Server Error",
    "path": "/api/books"
}
```

This is useless to both the client and the developer.

### What We Want Instead

We want consistent, informative responses like:

```json
{
    "status": 404,
    "error": "Not Found",
    "message": "Book not found with ID: 999",
    "timestamp": "2024-01-15T10:30:00"
}
```

And for validation errors:

```json
{
    "status": 400,
    "error": "Validation Failed",
    "message": "One or more fields have errors",
    "timestamp": "2024-01-15T10:30:00",
    "fieldErrors": [
        {
            "field": "title",
            "message": "Title is required"
        },
        {
            "field": "price",
            "message": "Price must be greater than zero"
        }
    ]
}
```

Now the client knows exactly what went wrong and how to fix it.

---

## 12.2 Creating Custom Exceptions

The first step is creating your own exception classes. These represent specific error conditions in your application.

### ResourceNotFoundException

This exception is thrown when a requested resource does not exist.

```java
package com.example.demo.exception;

public class ResourceNotFoundException extends RuntimeException {

    private final String resourceName;
    private final String fieldName;
    private final Object fieldValue;

    public ResourceNotFoundException(String resourceName,
                                      String fieldName,
                                      Object fieldValue) {
        super(String.format("%s not found with %s: '%s'",
                resourceName, fieldName, fieldValue));
        this.resourceName = resourceName;
        this.fieldName = fieldName;
        this.fieldValue = fieldValue;
    }

    public String getResourceName() { return resourceName; }
    public String getFieldName() { return fieldName; }
    public Object getFieldValue() { return fieldValue; }
}
```

**Line-by-line explanation:**

- `extends RuntimeException` -- Our exception extends `RuntimeException`, which means it is an **unchecked exception**. You do not need to declare it in method signatures with `throws`.
- `String resourceName` -- The type of resource ("Book", "User", "Order").
- `String fieldName` -- The field used to look up the resource ("id", "isbn", "email").
- `Object fieldValue` -- The value that was not found (42, "978-123", "alice@example.com").
- `super(String.format(...))` -- Creates a human-readable message like "Book not found with id: '999'".

**RuntimeException** is a Java exception that does not require explicit handling with try-catch. Spring can catch it automatically using `@ExceptionHandler`.

### DuplicateResourceException

This exception is thrown when trying to create a resource that already exists.

```java
package com.example.demo.exception;

public class DuplicateResourceException extends RuntimeException {

    private final String resourceName;
    private final String fieldName;
    private final Object fieldValue;

    public DuplicateResourceException(String resourceName,
                                       String fieldName,
                                       Object fieldValue) {
        super(String.format("%s already exists with %s: '%s'",
                resourceName, fieldName, fieldValue));
        this.resourceName = resourceName;
        this.fieldName = fieldName;
        this.fieldValue = fieldValue;
    }

    public String getResourceName() { return resourceName; }
    public String getFieldName() { return fieldName; }
    public Object getFieldValue() { return fieldValue; }
}
```

### Using Custom Exceptions in the Service Layer

```java
package com.example.demo.service;

import com.example.demo.dto.BookCreateRequest;
import com.example.demo.dto.BookResponse;
import com.example.demo.exception.DuplicateResourceException;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.model.Book;
import com.example.demo.repository.BookRepository;
import org.springframework.stereotype.Service;

@Service
public class BookService {

    private final BookRepository bookRepository;

    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    public BookResponse getBookById(Long id) {
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Book", "id", id));
        return toResponse(book);
    }

    public BookResponse createBook(BookCreateRequest request) {
        // Check for duplicate ISBN
        if (bookRepository.existsByIsbn(request.getIsbn())) {
            throw new DuplicateResourceException(
                    "Book", "isbn", request.getIsbn());
        }

        Book book = new Book();
        book.setTitle(request.getTitle());
        book.setAuthor(request.getAuthor());
        book.setPrice(request.getPrice());
        book.setIsbn(request.getIsbn());

        Book saved = bookRepository.save(book);
        return toResponse(saved);
    }

    public BookResponse updateBook(Long id,
                                    BookUpdateRequest request) {
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Book", "id", id));

        book.setTitle(request.getTitle());
        book.setAuthor(request.getAuthor());
        book.setPrice(request.getPrice());

        Book updated = bookRepository.save(book);
        return toResponse(updated);
    }

    public void deleteBook(Long id) {
        if (!bookRepository.existsById(id)) {
            throw new ResourceNotFoundException("Book", "id", id);
        }
        bookRepository.deleteById(id);
    }

    private BookResponse toResponse(Book book) {
        return new BookResponse(
                book.getId(), book.getTitle(),
                book.getAuthor(), book.getPrice(),
                book.getIsbn(), book.getCreatedAt(),
                book.getUpdatedAt());
    }
}
```

Notice how the service now throws specific exceptions instead of returning `Optional` or `null`. The controller does not need to check for missing resources. The exception handler takes care of it.

---

## 12.3 The Error Response DTO

Before we handle exceptions, let us define what our error responses should look like.

```java
package com.example.demo.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.time.LocalDateTime;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class ErrorResponse {

    private int status;
    private String error;
    private String message;
    private LocalDateTime timestamp;
    private String path;
    private List<FieldError> fieldErrors;

    public ErrorResponse() {
        this.timestamp = LocalDateTime.now();
    }

    public ErrorResponse(int status, String error, String message) {
        this();
        this.status = status;
        this.error = error;
        this.message = message;
    }

    // Getters and setters
    public int getStatus() { return status; }
    public void setStatus(int status) { this.status = status; }

    public String getError() { return error; }
    public void setError(String error) { this.error = error; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public String getPath() { return path; }
    public void setPath(String path) { this.path = path; }

    public List<FieldError> getFieldErrors() { return fieldErrors; }
    public void setFieldErrors(List<FieldError> fieldErrors) {
        this.fieldErrors = fieldErrors;
    }

    // Inner class for field-level validation errors
    public static class FieldError {

        private String field;
        private String message;
        private Object rejectedValue;

        public FieldError() {}

        public FieldError(String field, String message,
                          Object rejectedValue) {
            this.field = field;
            this.message = message;
            this.rejectedValue = rejectedValue;
        }

        public String getField() { return field; }
        public void setField(String field) { this.field = field; }

        public String getMessage() { return message; }
        public void setMessage(String message) {
            this.message = message;
        }

        public Object getRejectedValue() { return rejectedValue; }
        public void setRejectedValue(Object rejectedValue) {
            this.rejectedValue = rejectedValue;
        }
    }
}
```

**Line-by-line explanation:**

- `@JsonInclude(JsonInclude.Include.NON_NULL)` -- This Jackson annotation means "only include fields in the JSON output if they are not null." So if there are no `fieldErrors`, that field is omitted from the response entirely. This keeps responses clean.
- `ErrorResponse` contains the standard error information: status code, error name, message, timestamp, and request path.
- `FieldError` is a nested class for validation errors. It includes the field name, the error message, and the rejected value.
- `rejectedValue` shows the client what value they sent. This is helpful for debugging. "The field 'price' has value '-5' which is invalid."

### What the Error Responses Look Like

**Simple error (resource not found):**

```json
{
    "status": 404,
    "error": "Not Found",
    "message": "Book not found with id: '999'",
    "timestamp": "2024-01-15T10:30:00",
    "path": "/api/books/999"
}
```

**Validation error (with field details):**

```json
{
    "status": 400,
    "error": "Validation Failed",
    "message": "One or more fields have validation errors",
    "timestamp": "2024-01-15T10:30:00",
    "path": "/api/books",
    "fieldErrors": [
        {
            "field": "title",
            "message": "Title is required",
            "rejectedValue": ""
        },
        {
            "field": "price",
            "message": "Price must be greater than zero",
            "rejectedValue": -5.0
        }
    ]
}
```

---

## 12.4 Global Exception Handling with @ControllerAdvice

`@ControllerAdvice` is a special annotation that lets you handle exceptions across all controllers in one place. Without it, you would need to handle exceptions in every controller separately.

**@ControllerAdvice** tells Spring: "This class contains exception handling logic that applies to all controllers." Think of it as a safety net under all your controllers.

**@ExceptionHandler** marks a method that handles a specific type of exception. When that exception is thrown anywhere in your controllers, Spring calls this method instead of returning the default error.

### The Complete Global Exception Handler

```java
package com.example.demo.exception;

import com.example.demo.dto.ErrorResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;

import java.util.List;

@ControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log =
            LoggerFactory.getLogger(GlobalExceptionHandler.class);

    // Handle resource not found
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFound(
            ResourceNotFoundException ex, WebRequest request) {

        log.warn("Resource not found: {}", ex.getMessage());

        ErrorResponse error = new ErrorResponse(
                HttpStatus.NOT_FOUND.value(),
                "Not Found",
                ex.getMessage()
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error, HttpStatus.NOT_FOUND);
    }

    // Handle duplicate resource
    @ExceptionHandler(DuplicateResourceException.class)
    public ResponseEntity<ErrorResponse> handleDuplicateResource(
            DuplicateResourceException ex, WebRequest request) {

        log.warn("Duplicate resource: {}", ex.getMessage());

        ErrorResponse error = new ErrorResponse(
                HttpStatus.CONFLICT.value(),
                "Conflict",
                ex.getMessage()
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error, HttpStatus.CONFLICT);
    }

    // Handle validation errors
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationErrors(
            MethodArgumentNotValidException ex,
            WebRequest request) {

        log.warn("Validation failed: {} errors",
                ex.getBindingResult().getErrorCount());

        List<ErrorResponse.FieldError> fieldErrors =
                ex.getBindingResult().getFieldErrors().stream()
                    .map(fieldError -> new ErrorResponse.FieldError(
                            fieldError.getField(),
                            fieldError.getDefaultMessage(),
                            fieldError.getRejectedValue()
                    ))
                    .toList();

        ErrorResponse error = new ErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                "Validation Failed",
                "One or more fields have validation errors"
        );
        error.setPath(getPath(request));
        error.setFieldErrors(fieldErrors);

        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }

    // Handle all other unexpected exceptions
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleAllOtherExceptions(
            Exception ex, WebRequest request) {

        log.error("Unexpected error occurred", ex);

        ErrorResponse error = new ErrorResponse(
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                "Internal Server Error",
                "An unexpected error occurred. Please try again later."
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error,
                HttpStatus.INTERNAL_SERVER_ERROR);
    }

    private String getPath(WebRequest request) {
        return request.getDescription(false).replace("uri=", "");
    }
}
```

**Line-by-line explanation of each handler:**

#### handleResourceNotFound

- `@ExceptionHandler(ResourceNotFoundException.class)` -- This method catches all `ResourceNotFoundException` instances thrown by any controller.
- `ResourceNotFoundException ex` -- The actual exception object, which contains the error message.
- `WebRequest request` -- Contains information about the HTTP request, including the URL path.
- `log.warn(...)` -- Logs the error at WARN level. Not found errors are not critical but should be logged for monitoring.
- Returns a 404 status with our clean error response.

#### handleDuplicateResource

- Similar to the above, but returns HTTP 409 (Conflict).
- A **409 Conflict** means the request conflicts with the current state of the server. Creating a book with an ISBN that already exists is a conflict.

#### handleValidationErrors

- `@ExceptionHandler(MethodArgumentNotValidException.class)` -- This exception is thrown by Spring when `@Valid` validation fails.
- `ex.getBindingResult().getFieldErrors()` -- Gets the list of field-level errors from the validation result.
- We convert each field error into our `ErrorResponse.FieldError` format with the field name, message, and rejected value.
- Returns a 400 status with field-level error details.

**MethodArgumentNotValidException** is the exception Spring throws when `@Valid` detects validation errors. It contains a `BindingResult` which holds all the field errors.

#### handleAllOtherExceptions

- `@ExceptionHandler(Exception.class)` -- This is the **catch-all handler**. It catches any exception not handled by the other methods.
- `log.error("Unexpected error occurred", ex)` -- Logs the full stack trace at ERROR level. This is critical for debugging.
- The response message is generic on purpose. You do not want to expose internal error details to the client. Stack traces, class names, and database errors should stay in the logs.

### How Exception Handling Flows

```
Controller throws ResourceNotFoundException
         |
         v
+-----------------------------------+
| Spring looks for @ExceptionHandler |
| that matches the exception type    |
+-----------------------------------+
         |
         | Found: handleResourceNotFound()
         v
+-----------------------------------+
| Handler creates ErrorResponse      |
| Sets status, message, path         |
+-----------------------------------+
         |
         v
+-----------------------------------+
| Spring sends the response:         |
| Status: 404                        |
| Body: ErrorResponse as JSON        |
+-----------------------------------+
```

```
No matching specific handler?
         |
         v
+-----------------------------------+
| Falls through to catch-all:        |
| handleAllOtherExceptions()         |
+-----------------------------------+
         |
         v
+-----------------------------------+
| Status: 500                        |
| Body: Generic error message        |
| Stack trace logged to server       |
+-----------------------------------+
```

---

## 12.5 Simplified Controllers with Exception Handling

Now that exceptions are handled globally, your controllers become much simpler.

### Before (Without Global Exception Handling)

```java
@GetMapping("/{id}")
public ResponseEntity<BookResponse> getBookById(
        @PathVariable Long id) {
    return bookService.getBookById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    // Ugly: 404 with no body, no message
}

@PostMapping
public ResponseEntity<?> createBook(
        @Valid @RequestBody BookCreateRequest request) {
    try {
        BookResponse created = bookService.createBook(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(created);
    } catch (DuplicateResourceException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(Map.of("error", e.getMessage()));
        // Inconsistent error format
    }
}
```

### After (With Global Exception Handling)

```java
@RestController
@RequestMapping("/api/books")
public class BookController {

    private final BookService bookService;

    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    @PostMapping
    public ResponseEntity<BookResponse> createBook(
            @Valid @RequestBody BookCreateRequest request) {
        BookResponse created = bookService.createBook(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(created);
    }

    @GetMapping
    public ResponseEntity<List<BookResponse>> getAllBooks() {
        return ResponseEntity.ok(bookService.getAllBooks());
    }

    @GetMapping("/{id}")
    public ResponseEntity<BookResponse> getBookById(
            @PathVariable Long id) {
        BookResponse book = bookService.getBookById(id);
        return ResponseEntity.ok(book);
    }

    @PutMapping("/{id}")
    public ResponseEntity<BookResponse> updateBook(
            @PathVariable Long id,
            @Valid @RequestBody BookUpdateRequest request) {
        BookResponse updated = bookService.updateBook(id, request);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBook(@PathVariable Long id) {
        bookService.deleteBook(id);
        return ResponseEntity.noContent().build();
    }
}
```

Look how clean this is. No try-catch blocks. No null checks. No Optional handling. The controller focuses on the happy path. The `GlobalExceptionHandler` takes care of all errors.

```
+--------------------------------------------------+
|   Controller (Happy Path Only)                    |
|   - Takes request                                 |
|   - Calls service                                 |
|   - Returns response                              |
+--------------------------------------------------+
         |
         | If exception thrown...
         v
+--------------------------------------------------+
|   GlobalExceptionHandler (All Error Handling)     |
|   - Catches exception                             |
|   - Creates clean ErrorResponse                   |
|   - Returns proper HTTP status                    |
+--------------------------------------------------+
```

---

## 12.6 Handling Additional Exception Types

Your application may encounter other types of exceptions. Here are common ones and how to handle them.

### Handling Malformed JSON

When a client sends invalid JSON, Spring throws `HttpMessageNotReadableException`:

```java
@ExceptionHandler(HttpMessageNotReadableException.class)
public ResponseEntity<ErrorResponse> handleMalformedJson(
        HttpMessageNotReadableException ex,
        WebRequest request) {

    log.warn("Malformed JSON request: {}", ex.getMessage());

    ErrorResponse error = new ErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            "Malformed JSON",
            "The request body contains invalid JSON. "
            + "Please check the syntax."
    );
    error.setPath(getPath(request));

    return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
}
```

**Test:**

```bash
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{invalid json here}'
```

**Response:**

```json
{
    "status": 400,
    "error": "Malformed JSON",
    "message": "The request body contains invalid JSON. Please check the syntax.",
    "timestamp": "2024-01-15T10:30:00",
    "path": "/api/books"
}
```

### Handling Wrong HTTP Method

When a client uses GET on a POST-only endpoint, Spring throws `HttpRequestMethodNotSupportedException`:

```java
@ExceptionHandler(HttpRequestMethodNotSupportedException.class)
public ResponseEntity<ErrorResponse> handleMethodNotSupported(
        HttpRequestMethodNotSupportedException ex,
        WebRequest request) {

    String message = String.format(
            "HTTP method '%s' is not supported for this endpoint. "
            + "Supported methods: %s",
            ex.getMethod(),
            ex.getSupportedHttpMethods());

    ErrorResponse error = new ErrorResponse(
            HttpStatus.METHOD_NOT_ALLOWED.value(),
            "Method Not Allowed",
            message
    );
    error.setPath(getPath(request));

    return new ResponseEntity<>(error,
            HttpStatus.METHOD_NOT_ALLOWED);
}
```

### Handling Missing Path Variables or Parameters

When a required request parameter is missing:

```java
@ExceptionHandler(MissingServletRequestParameterException.class)
public ResponseEntity<ErrorResponse> handleMissingParameter(
        MissingServletRequestParameterException ex,
        WebRequest request) {

    String message = String.format(
            "Required parameter '%s' of type '%s' is missing",
            ex.getParameterName(), ex.getParameterType());

    ErrorResponse error = new ErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            "Missing Parameter",
            message
    );
    error.setPath(getPath(request));

    return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
}
```

---

## 12.7 The Complete Exception Handling System

Here is the full picture of all the pieces working together.

### Project Structure

```
src/main/java/com/example/demo/
├── DemoApplication.java
├── controller/
│   └── BookController.java
├── dto/
│   ├── BookCreateRequest.java
│   ├── BookUpdateRequest.java
│   ├── BookResponse.java
│   └── ErrorResponse.java
├── exception/
│   ├── GlobalExceptionHandler.java
│   ├── ResourceNotFoundException.java
│   └── DuplicateResourceException.java
├── model/
│   └── Book.java
├── repository/
│   └── BookRepository.java
└── service/
    └── BookService.java
```

### Complete GlobalExceptionHandler

```java
package com.example.demo.exception;

import com.example.demo.dto.ErrorResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

import java.util.List;

@ControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log =
            LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /**
     * Handle resource not found (404)
     */
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFound(
            ResourceNotFoundException ex, WebRequest request) {

        log.warn("Resource not found: {}", ex.getMessage());

        ErrorResponse error = new ErrorResponse(
                HttpStatus.NOT_FOUND.value(),
                "Not Found",
                ex.getMessage()
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error, HttpStatus.NOT_FOUND);
    }

    /**
     * Handle duplicate resource (409)
     */
    @ExceptionHandler(DuplicateResourceException.class)
    public ResponseEntity<ErrorResponse> handleDuplicateResource(
            DuplicateResourceException ex, WebRequest request) {

        log.warn("Duplicate resource: {}", ex.getMessage());

        ErrorResponse error = new ErrorResponse(
                HttpStatus.CONFLICT.value(),
                "Conflict",
                ex.getMessage()
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error, HttpStatus.CONFLICT);
    }

    /**
     * Handle validation errors (400)
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationErrors(
            MethodArgumentNotValidException ex,
            WebRequest request) {

        log.warn("Validation failed: {} error(s)",
                ex.getBindingResult().getErrorCount());

        List<ErrorResponse.FieldError> fieldErrors =
                ex.getBindingResult().getFieldErrors().stream()
                    .map(fe -> new ErrorResponse.FieldError(
                            fe.getField(),
                            fe.getDefaultMessage(),
                            fe.getRejectedValue()
                    ))
                    .toList();

        ErrorResponse error = new ErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                "Validation Failed",
                "One or more fields have validation errors"
        );
        error.setPath(getPath(request));
        error.setFieldErrors(fieldErrors);

        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }

    /**
     * Handle malformed JSON (400)
     */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ErrorResponse> handleMalformedJson(
            HttpMessageNotReadableException ex,
            WebRequest request) {

        log.warn("Malformed JSON: {}", ex.getMessage());

        ErrorResponse error = new ErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                "Malformed Request",
                "The request body is missing or contains "
                + "invalid JSON"
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }

    /**
     * Handle wrong HTTP method (405)
     */
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<ErrorResponse> handleMethodNotSupported(
            HttpRequestMethodNotSupportedException ex,
            WebRequest request) {

        log.warn("Method not supported: {}", ex.getMessage());

        ErrorResponse error = new ErrorResponse(
                HttpStatus.METHOD_NOT_ALLOWED.value(),
                "Method Not Allowed",
                "HTTP method '" + ex.getMethod()
                + "' is not supported for this endpoint"
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error,
                HttpStatus.METHOD_NOT_ALLOWED);
    }

    /**
     * Handle missing request parameters (400)
     */
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<ErrorResponse> handleMissingParameter(
            MissingServletRequestParameterException ex,
            WebRequest request) {

        log.warn("Missing parameter: {}", ex.getParameterName());

        ErrorResponse error = new ErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                "Missing Parameter",
                "Required parameter '"
                + ex.getParameterName() + "' is missing"
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }

    /**
     * Handle type mismatch (e.g., string where number expected) (400)
     */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<ErrorResponse> handleTypeMismatch(
            MethodArgumentTypeMismatchException ex,
            WebRequest request) {

        log.warn("Type mismatch: {}", ex.getMessage());

        String message = String.format(
                "Parameter '%s' should be of type '%s'",
                ex.getName(),
                ex.getRequiredType() != null
                    ? ex.getRequiredType().getSimpleName()
                    : "unknown");

        ErrorResponse error = new ErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                "Type Mismatch",
                message
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }

    /**
     * Handle all other exceptions (500)
     * This is the catch-all handler.
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleAllOtherExceptions(
            Exception ex, WebRequest request) {

        log.error("Unexpected error", ex);

        ErrorResponse error = new ErrorResponse(
                HttpStatus.INTERNAL_SERVER_ERROR.value(),
                "Internal Server Error",
                "An unexpected error occurred. "
                + "Please try again later."
        );
        error.setPath(getPath(request));

        return new ResponseEntity<>(error,
                HttpStatus.INTERNAL_SERVER_ERROR);
    }

    private String getPath(WebRequest request) {
        return request.getDescription(false)
                .replace("uri=", "");
    }
}
```

### Testing All Error Scenarios

```bash
# 1. Resource not found (404)
curl -s http://localhost:8080/api/books/999 | python3 -m json.tool
```

```json
{
    "status": 404,
    "error": "Not Found",
    "message": "Book not found with id: '999'",
    "timestamp": "2024-01-15T10:30:00",
    "path": "/api/books/999"
}
```

```bash
# 2. Validation error (400)
curl -s -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "", "price": -5}' | python3 -m json.tool
```

```json
{
    "status": 400,
    "error": "Validation Failed",
    "message": "One or more fields have validation errors",
    "timestamp": "2024-01-15T10:30:00",
    "path": "/api/books",
    "fieldErrors": [
        {
            "field": "title",
            "message": "Title is required",
            "rejectedValue": ""
        },
        {
            "field": "author",
            "message": "Author is required",
            "rejectedValue": null
        },
        {
            "field": "price",
            "message": "Price must be greater than zero",
            "rejectedValue": -5.0
        },
        {
            "field": "isbn",
            "message": "ISBN is required",
            "rejectedValue": null
        }
    ]
}
```

```bash
# 3. Duplicate resource (409)
curl -s -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "author": "Bob", "price": 9.99, "isbn": "978-1617292545"}' \
  | python3 -m json.tool
```

```json
{
    "status": 409,
    "error": "Conflict",
    "message": "Book already exists with isbn: '978-1617292545'",
    "timestamp": "2024-01-15T10:30:00",
    "path": "/api/books"
}
```

```bash
# 4. Malformed JSON (400)
curl -s -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{broken json' | python3 -m json.tool
```

```json
{
    "status": 400,
    "error": "Malformed Request",
    "message": "The request body is missing or contains invalid JSON",
    "timestamp": "2024-01-15T10:30:00",
    "path": "/api/books"
}
```

```bash
# 5. Type mismatch (400)
curl -s http://localhost:8080/api/books/abc | python3 -m json.tool
```

```json
{
    "status": 400,
    "error": "Type Mismatch",
    "message": "Parameter 'id' should be of type 'Long'",
    "timestamp": "2024-01-15T10:30:00",
    "path": "/api/books/abc"
}
```

---

## Common Mistakes

### Mistake 1: Catching Exceptions in the Controller

```java
// WRONG: Handling exceptions in the controller
@GetMapping("/{id}")
public ResponseEntity<?> getBook(@PathVariable Long id) {
    try {
        BookResponse book = bookService.getBookById(id);
        return ResponseEntity.ok(book);
    } catch (ResourceNotFoundException e) {
        return ResponseEntity.status(404)
                .body(Map.of("error", e.getMessage()));
    }
}
```

```java
// CORRECT: Let the global handler catch it
@GetMapping("/{id}")
public ResponseEntity<BookResponse> getBook(
        @PathVariable Long id) {
    return ResponseEntity.ok(bookService.getBookById(id));
}
```

The whole point of `@ControllerAdvice` is to centralize error handling. Do not duplicate it in controllers.

### Mistake 2: Exposing Stack Traces to Clients

```java
// WRONG: Sending the exception message directly
@ExceptionHandler(Exception.class)
public ResponseEntity<ErrorResponse> handleAll(Exception ex) {
    ErrorResponse error = new ErrorResponse(
            500, "Error", ex.getMessage());
    // ex.getMessage() might contain: "Connection refused:
    // jdbc:postgresql://internal-db:5432/mydb"
    // This exposes internal infrastructure details!
    return new ResponseEntity<>(error,
            HttpStatus.INTERNAL_SERVER_ERROR);
}
```

```java
// CORRECT: Use a generic message for unexpected errors
@ExceptionHandler(Exception.class)
public ResponseEntity<ErrorResponse> handleAll(Exception ex) {
    log.error("Unexpected error", ex);  // Log full details
    ErrorResponse error = new ErrorResponse(
            500, "Internal Server Error",
            "An unexpected error occurred. Please try again later.");
    return new ResponseEntity<>(error,
            HttpStatus.INTERNAL_SERVER_ERROR);
}
```

Log the full details for debugging. Send a generic message to the client. Never expose database URLs, file paths, class names, or stack traces.

### Mistake 3: Forgetting the Catch-All Handler

Without a catch-all `@ExceptionHandler(Exception.class)`, unexpected exceptions fall through to Spring's default handler. That default handler returns a different format than your custom handlers, creating inconsistency.

Always include a catch-all handler as the last `@ExceptionHandler` method.

### Mistake 4: Inconsistent Error Response Format

```java
// WRONG: Different formats in different handlers
@ExceptionHandler(ResourceNotFoundException.class)
public ResponseEntity<Map<String, String>> handle404(...) {
    return ResponseEntity.status(404)
            .body(Map.of("error", ex.getMessage()));
}

@ExceptionHandler(Exception.class)
public ResponseEntity<String> handle500(...) {
    return ResponseEntity.status(500).body("Something went wrong");
}
```

Always use the same `ErrorResponse` class for all error responses. Clients should be able to parse every error response with the same code.

---

## Best Practices

1. **Use one `@ControllerAdvice` class** for all exception handling. Having multiple can cause confusion about which handler runs.

2. **Create specific exception classes** for specific error conditions. `ResourceNotFoundException`, `DuplicateResourceException`, and `InvalidOperationException` are better than throwing generic `RuntimeException`.

3. **Always include a catch-all handler.** Unexpected exceptions should return a clean 500 response, not a stack trace.

4. **Never expose internal details** in error messages. Database errors, file paths, and class names are for logs, not for clients.

5. **Log errors at the right level.** Use `log.warn()` for client errors (4xx) and `log.error()` for server errors (5xx).

6. **Include the request path** in error responses. It helps clients and developers identify which endpoint failed.

7. **Use consistent error response format.** Every error from your API should use the same `ErrorResponse` structure.

8. **Keep error messages actionable.** "Book not found with id: '999'" is better than "Error occurred." The client can fix the first message; the second is useless.

---

## Quick Summary

- **Custom exceptions** like `ResourceNotFoundException` represent specific error conditions in your application.
- **@ControllerAdvice** marks a class that handles exceptions across all controllers.
- **@ExceptionHandler** marks a method that catches a specific exception type and returns a custom response.
- **ErrorResponse** is a DTO that gives errors a consistent, clean format with status, error type, message, timestamp, and path.
- Validation errors from `@Valid` throw `MethodArgumentNotValidException`, which you catch and convert into field-level error details.
- Always include a **catch-all handler** for `Exception.class` to handle unexpected errors.
- **Never expose** stack traces, database details, or internal class names to the client.

---

## Key Points

- Centralize all exception handling in one `@ControllerAdvice` class.
- Keep controllers focused on the happy path. Let the exception handler deal with errors.
- Use specific exception classes for specific error conditions.
- Log full error details. Return generic messages to clients.
- Use consistent error response format across all error types.
- Handle common Spring exceptions: validation errors, malformed JSON, type mismatches, missing parameters.
- The catch-all handler is your safety net. Never skip it.

---

## Practice Questions

1. What is the difference between `@ControllerAdvice` and putting try-catch blocks in every controller method? Why is `@ControllerAdvice` better?

2. Why should you never return `ex.getMessage()` directly in a 500 error response? What should you do instead?

3. What exception does Spring throw when `@Valid` validation fails? What information can you extract from it?

4. Explain the purpose of `@JsonInclude(JsonInclude.Include.NON_NULL)` on the `ErrorResponse` class.

5. You have a `UserService` that throws `IllegalArgumentException` when a username contains special characters. How would you handle this in a `@ControllerAdvice` class?

---

## Exercises

### Exercise 1: E-Commerce Error Handling

Build an error handling system for an e-commerce API with these custom exceptions:

- `ProductNotFoundException` -- when a product ID does not exist
- `InsufficientStockException` -- when ordering more items than available
- `InvalidOrderException` -- when an order has invalid data (e.g., negative quantity)

Create a `GlobalExceptionHandler` that handles each one with appropriate HTTP status codes (404, 409, and 400 respectively). Test with curl.

### Exercise 2: User Management Errors

Build a user management API with:

- `UserAlreadyExistsException` for duplicate email addresses
- Validation on the user registration DTO (email, password, name)
- Global exception handler that returns clean error responses for both validation errors and duplicate user errors
- Handle the case where a client sends a non-numeric ID in the URL (`/api/users/abc`)

### Exercise 3: Complete API with Full Error Handling

Combine everything from Chapters 9 through 12 into a complete Task Management API:

- Task model: `id`, `title`, `description`, `priority` (1-5), `status` (PENDING/IN_PROGRESS/COMPLETED), `dueDate`
- Full CRUD endpoints with DTOs
- Validation on all input fields
- Custom exceptions: `TaskNotFoundException`, `InvalidStatusTransitionException` (e.g., cannot go from COMPLETED to PENDING)
- Global exception handler covering all error scenarios
- Test every success and error scenario with curl

---

## What Is Next?

Congratulations! You have now built a complete, production-quality REST API. You know how to:

- Create and manage beans (Chapter 7)
- Configure your application for different environments (Chapter 8)
- Build REST controllers that handle HTTP requests (Chapter 9)
- Handle path variables, query parameters, and request bodies (Chapter 10)
- Validate input data (Chapter 11)
- Handle errors gracefully (Chapter 12)

These six chapters cover the essential skills for building Spring Boot REST APIs. In the upcoming chapters, you will learn how to persist data to a database with Spring Data JPA, secure your API with Spring Security, and write tests to verify your code works correctly. The foundation you built here will make those topics much easier to learn.
