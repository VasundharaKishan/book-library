# Chapter 10: Request and Response Handling

## What You Will Learn

In this chapter, you will learn:

- How to extract values from URLs with `@PathVariable`
- How to read query parameters with `@RequestParam`
- How to accept JSON request bodies with `@RequestBody`
- How to control HTTP responses with `ResponseEntity`
- The meaning of common HTTP status codes
- What DTOs are and why you should use them
- How to build a complete CRUD controller

## Why This Chapter Matters

In the previous chapter, you built simple GET and POST endpoints. But real-world APIs are more complex. Users need to search for specific items, filter results, send data in different formats, and receive meaningful responses.

Think of it this way. In the previous chapter, you learned to open the front door of a restaurant and seat guests. In this chapter, you learn to take complex orders, handle special requests, and deliver meals with the right presentation.

This chapter gives you the full toolkit for handling any HTTP request and crafting proper responses. After this chapter, you will be able to build a production-quality REST API.

---

## 10.1 Extracting Values from URLs with @PathVariable

A **path variable** is a value embedded in the URL path itself. It identifies a specific resource.

```
GET /api/books/42
              ^^
              This is the path variable (book ID = 42)
```

### Basic Usage

```java
@RestController
@RequestMapping("/api/books")
public class BookController {

    private final BookService bookService;

    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    @GetMapping("/{id}")
    public Book getBookById(@PathVariable Long id) {
        return bookService.getBookById(id);
    }
}
```

**Line-by-line explanation:**

- `@GetMapping("/{id}")` -- The curly braces define a placeholder. Any value in that position will be captured. `/api/books/1`, `/api/books/42`, `/api/books/999` all match.
- `@PathVariable Long id` -- Spring takes the value from the URL and converts it to a `Long`. The parameter name (`id`) must match the placeholder name (`{id}`).

**How it works:**

```
Request: GET /api/books/42

URL pattern: /api/books/{id}
                         ↓
@PathVariable Long id = 42
```

### Multiple Path Variables

You can have more than one path variable in a URL.

```java
@GetMapping("/{bookId}/reviews/{reviewId}")
public Review getReview(@PathVariable Long bookId,
                        @PathVariable Long reviewId) {
    return reviewService.getReview(bookId, reviewId);
}
```

```
Request: GET /api/books/5/reviews/12

URL pattern: /api/books/{bookId}/reviews/{reviewId}
                         ↓                   ↓
@PathVariable Long bookId = 5   Long reviewId = 12
```

### Custom Parameter Name

If the method parameter name does not match the placeholder, use the `value` attribute:

```java
@GetMapping("/{book-id}")
public Book getBook(
        @PathVariable("book-id") Long bookId) {
    return bookService.getBookById(bookId);
}
```

Here the URL uses `{book-id}` (with a dash), but the Java variable is `bookId` (camelCase). The `@PathVariable("book-id")` tells Spring which placeholder to use.

---

## 10.2 Reading Query Parameters with @RequestParam

A **query parameter** is a value added to the end of a URL after a question mark `?`. It is used for filtering, searching, sorting, and pagination.

```
GET /api/books?author=Craig&minPrice=20
              ^^^^^^^^^^^^^^^^^^^^^^^
              These are query parameters
```

### Basic Usage

```java
@GetMapping("/search")
public List<Book> searchBooks(
        @RequestParam String author) {
    return bookService.findByAuthor(author);
}
```

```
Request: GET /api/books/search?author=Craig

@RequestParam String author = "Craig"
```

### Optional Parameters with Default Values

Not all query parameters are required. Use `required = false` or `defaultValue`.

```java
@GetMapping
public List<Book> getAllBooks(
        @RequestParam(required = false) String author,
        @RequestParam(defaultValue = "0") double minPrice,
        @RequestParam(defaultValue = "1000") double maxPrice,
        @RequestParam(defaultValue = "title") String sortBy) {

    List<Book> result = bookService.getAllBooks();

    if (author != null) {
        result = result.stream()
                .filter(b -> b.getAuthor()
                        .toLowerCase()
                        .contains(author.toLowerCase()))
                .toList();
    }

    result = result.stream()
            .filter(b -> b.getPrice() >= minPrice
                      && b.getPrice() <= maxPrice)
            .toList();

    return result;
}
```

**Line-by-line explanation:**

- `@RequestParam(required = false) String author` -- This parameter is optional. If the client does not provide it, the value is `null`.
- `@RequestParam(defaultValue = "0") double minPrice` -- If the client does not provide `minPrice`, it defaults to `0`.
- `@RequestParam(defaultValue = "title") String sortBy` -- Defaults to `"title"` if not provided.

**Example requests:**

```bash
# All books (no filters)
curl http://localhost:8080/api/books

# Filter by author
curl "http://localhost:8080/api/books?author=Craig"

# Filter by price range
curl "http://localhost:8080/api/books?minPrice=30&maxPrice=50"

# Multiple filters
curl "http://localhost:8080/api/books?author=Craig&minPrice=20&sortBy=price"
```

> **Note:** When using curl with query parameters, wrap the URL in quotes. The `&` symbol has special meaning in the shell.

### @PathVariable vs @RequestParam

| Feature         | @PathVariable             | @RequestParam              |
|-----------------|---------------------------|----------------------------|
| Location in URL | Part of the path          | After the `?`              |
| Purpose         | Identify a specific item  | Filter, search, sort       |
| Required?       | Yes (by default)          | Configurable               |
| Example         | `/books/42`               | `/books?author=Craig`      |

**Rule of thumb:** Use `@PathVariable` to identify WHAT you want. Use `@RequestParam` to specify HOW you want it.

```
GET /api/books/42         --> "Give me book number 42"     (@PathVariable)
GET /api/books?author=Bob --> "Give me books by Bob"       (@RequestParam)
```

---

## 10.3 Accepting JSON with @RequestBody

You learned `@RequestBody` in the previous chapter. Let us go deeper.

**@RequestBody** tells Spring to read the entire HTTP request body and convert it from JSON into a Java object.

```java
@PostMapping
public Book createBook(@RequestBody Book book) {
    return bookService.createBook(book);
}
```

### How the Conversion Works

```
HTTP Request:
──────────────────────────────────────
POST /api/books
Content-Type: application/json

{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "price": 34.99,
    "isbn": "978-0132350884"
}

Jackson Deserialization:
──────────────────────────────────────
1. Create: Book book = new Book()
2. Set:    book.setTitle("Clean Code")
3. Set:    book.setAuthor("Robert C. Martin")
4. Set:    book.setPrice(34.99)
5. Set:    book.setIsbn("978-0132350884")

Result: A fully populated Book object
```

**Deserialization** means converting data from a format (like JSON) into a Java object. The opposite -- converting a Java object to JSON -- is called **serialization**.

### Important Rules for @RequestBody

1. The Java class needs a **no-argument constructor**
2. The class needs **setter methods** (or public fields) for each JSON property
3. The request must have the `Content-Type: application/json` header
4. JSON property names must match Java field names (or getter/setter names)

### Ignoring Unknown Properties

By default, Spring Boot ignores JSON properties that do not match any field in the Java class. This is a safe behavior.

```json
// Client sends:
{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "extraField": "this is ignored"
}
```

The `extraField` is silently ignored. No error occurs.

---

## 10.4 Controlling Responses with ResponseEntity

`ResponseEntity` is a wrapper that gives you full control over the HTTP response: the status code, headers, and body.

### Why Use ResponseEntity?

Without `ResponseEntity`, Spring always returns status 200 (OK):

```java
// Always returns 200 OK, even if something went wrong
@GetMapping("/{id}")
public Book getBook(@PathVariable Long id) {
    return bookService.getBookById(id);  // What if the book is null?
}
```

With `ResponseEntity`, you control the status code:

```java
// Returns 200 if found, 404 if not found
@GetMapping("/{id}")
public ResponseEntity<Book> getBook(@PathVariable Long id) {
    return bookService.getBookById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
}
```

### Common ResponseEntity Patterns

**Return 200 OK with a body:**

```java
return ResponseEntity.ok(book);
// Same as:
return ResponseEntity.status(HttpStatus.OK).body(book);
```

**Return 201 Created:**

```java
return ResponseEntity.status(HttpStatus.CREATED).body(createdBook);
```

**Return 204 No Content (for deletes):**

```java
return ResponseEntity.noContent().build();
```

**Return 404 Not Found:**

```java
return ResponseEntity.notFound().build();
```

**Return 400 Bad Request:**

```java
return ResponseEntity.badRequest().body(errorMessage);
```

### Adding Custom Headers

```java
@PostMapping
public ResponseEntity<Book> createBook(@RequestBody Book book) {
    Book created = bookService.createBook(book);
    return ResponseEntity
            .status(HttpStatus.CREATED)
            .header("X-Book-Id", String.valueOf(created.getId()))
            .body(created);
}
```

**Headers** are metadata sent along with the response. They provide extra information like content type, caching rules, and custom data.

---

## 10.5 HTTP Status Codes

HTTP status codes are three-digit numbers that tell the client what happened. They are grouped by the first digit.

### Status Code Families

```
+-------+------------------+------------------------------------+
| Range | Category         | Meaning                            |
+-------+------------------+------------------------------------+
| 1xx   | Informational    | "Hold on..."                       |
| 2xx   | Success          | "Here you go!"                     |
| 3xx   | Redirection      | "Go look over there"               |
| 4xx   | Client Error     | "You made a mistake"               |
| 5xx   | Server Error     | "I made a mistake"                 |
+-------+------------------+------------------------------------+
```

### Most Common Status Codes

| Code | Name                  | When to Use                        | Spring Constant             |
|------|-----------------------|------------------------------------|-----------------------------|
| 200  | OK                    | Successful GET, PUT, PATCH         | `HttpStatus.OK`             |
| 201  | Created               | Successful POST (new resource)     | `HttpStatus.CREATED`        |
| 204  | No Content            | Successful DELETE (nothing to return)| `HttpStatus.NO_CONTENT`    |
| 400  | Bad Request           | Invalid input from client          | `HttpStatus.BAD_REQUEST`    |
| 401  | Unauthorized          | Not logged in                      | `HttpStatus.UNAUTHORIZED`   |
| 403  | Forbidden             | Logged in but not allowed          | `HttpStatus.FORBIDDEN`      |
| 404  | Not Found             | Resource does not exist            | `HttpStatus.NOT_FOUND`      |
| 409  | Conflict              | Duplicate data or state conflict   | `HttpStatus.CONFLICT`       |
| 500  | Internal Server Error | Bug or crash on the server         | `HttpStatus.INTERNAL_SERVER_ERROR` |

### A Helpful Way to Remember

Think of status codes like restaurant responses:

- **200**: "Here is your food!" (Success)
- **201**: "Your order has been placed!" (Created)
- **204**: "Your plate has been cleared." (Deleted, nothing to show)
- **400**: "Sorry, we do not have that item. Please order something else." (Bad request)
- **404**: "We do not have a table number 99." (Not found)
- **500**: "The kitchen is on fire. Sorry!" (Server error)

---

## 10.6 Data Transfer Objects (DTOs)

A **DTO** (Data Transfer Object) is a simple object used to transfer data between layers of your application. It separates what the client sees from what your internal model looks like.

### Why Use DTOs?

Imagine your `Book` entity has a field called `purchaseCost` -- the wholesale price you paid. You do not want customers to see this. If you return the entity directly, all fields are exposed.

```
Without DTOs:
─────────────
Client sees EVERYTHING:
{
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "price": 34.99,
    "purchaseCost": 12.50,    <-- Client should NOT see this
    "supplierCode": "SUP-123"  <-- Client should NOT see this
}

With DTOs:
──────────
Client sees ONLY what you choose:
{
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "price": 34.99
}
```

### Request DTO vs Response DTO

Use separate DTOs for requests (input) and responses (output).

**Request DTO (what the client sends):**

```java
package com.example.demo.dto;

public class BookCreateRequest {

    private String title;
    private String author;
    private double price;
    private String isbn;

    // Getters and setters
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }
}
```

Notice there is no `id` field. The client does not set the ID -- the server generates it.

**Response DTO (what the client receives):**

```java
package com.example.demo.dto;

import java.time.LocalDateTime;

public class BookResponse {

    private Long id;
    private String title;
    private String author;
    private double price;
    private String isbn;
    private LocalDateTime createdAt;

    // Constructor from entity
    public BookResponse(Long id, String title, String author,
                        double price, String isbn,
                        LocalDateTime createdAt) {
        this.id = id;
        this.title = title;
        this.author = author;
        this.price = price;
        this.isbn = isbn;
        this.createdAt = createdAt;
    }

    // Getters (no setters needed -- response is read-only)
    public Long getId() { return id; }
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public double getPrice() { return price; }
    public String getIsbn() { return isbn; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
```

**Update DTO (for PUT/PATCH requests):**

```java
package com.example.demo.dto;

public class BookUpdateRequest {

    private String title;
    private String author;
    private double price;

    // Getters and setters
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
}
```

The update DTO does not have `id` (it comes from the URL) or `isbn` (cannot be changed).

### Mapping Between Entities and DTOs

Create a helper method or use the service layer to convert between entities and DTOs:

```java
@Service
public class BookService {

    private final BookRepository bookRepository;

    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    public BookResponse createBook(BookCreateRequest request) {
        Book book = new Book();
        book.setTitle(request.getTitle());
        book.setAuthor(request.getAuthor());
        book.setPrice(request.getPrice());
        book.setIsbn(request.getIsbn());

        Book saved = bookRepository.save(book);
        return toResponse(saved);
    }

    public BookResponse toResponse(Book book) {
        return new BookResponse(
                book.getId(),
                book.getTitle(),
                book.getAuthor(),
                book.getPrice(),
                book.getIsbn(),
                book.getCreatedAt()
        );
    }
}
```

### DTO Naming Convention

```
+--------------------+-----------------------------------+
| Name Pattern       | Purpose                           |
+--------------------+-----------------------------------+
| BookCreateRequest  | Client sends to create a book     |
| BookUpdateRequest  | Client sends to update a book     |
| BookResponse       | Server sends back to client       |
| BookSummary        | Shortened version for lists       |
+--------------------+-----------------------------------+
```

---

## 10.7 Building a Complete CRUD Controller

**CRUD** stands for **C**reate, **R**ead, **U**pdate, **D**elete. These are the four basic operations for managing data.

Let us build a complete CRUD controller for books.

### Project Structure

```
src/main/java/com/example/demo/
├── DemoApplication.java
├── model/
│   └── Book.java
├── dto/
│   ├── BookCreateRequest.java
│   ├── BookUpdateRequest.java
│   └── BookResponse.java
├── repository/
│   └── BookRepository.java
├── service/
│   └── BookService.java
└── controller/
    └── BookController.java
```

### The Model

```java
package com.example.demo.model;

import java.time.LocalDateTime;

public class Book {

    private Long id;
    private String title;
    private String author;
    private double price;
    private String isbn;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public Book() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}
```

### The DTOs

```java
package com.example.demo.dto;

public class BookCreateRequest {

    private String title;
    private String author;
    private double price;
    private String isbn;

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }
}
```

```java
package com.example.demo.dto;

public class BookUpdateRequest {

    private String title;
    private String author;
    private double price;

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
}
```

```java
package com.example.demo.dto;

import java.time.LocalDateTime;

public class BookResponse {

    private Long id;
    private String title;
    private String author;
    private double price;
    private String isbn;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public BookResponse() {}

    public BookResponse(Long id, String title, String author,
                        double price, String isbn,
                        LocalDateTime createdAt,
                        LocalDateTime updatedAt) {
        this.id = id;
        this.title = title;
        this.author = author;
        this.price = price;
        this.isbn = isbn;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public double getPrice() { return price; }
    public String getIsbn() { return isbn; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
```

### The Repository

```java
package com.example.demo.repository;

import com.example.demo.model.Book;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Repository
public class BookRepository {

    private final List<Book> books = new ArrayList<>();
    private long nextId = 1;

    public Book save(Book book) {
        if (book.getId() == null) {
            book.setId(nextId++);
        } else {
            books.removeIf(b -> b.getId().equals(book.getId()));
        }
        books.add(book);
        return book;
    }

    public Optional<Book> findById(Long id) {
        return books.stream()
                .filter(b -> b.getId().equals(id))
                .findFirst();
    }

    public List<Book> findAll() {
        return new ArrayList<>(books);
    }

    public boolean deleteById(Long id) {
        return books.removeIf(b -> b.getId().equals(id));
    }

    public boolean existsById(Long id) {
        return books.stream().anyMatch(b -> b.getId().equals(id));
    }
}
```

### The Service

```java
package com.example.demo.service;

import com.example.demo.dto.BookCreateRequest;
import com.example.demo.dto.BookResponse;
import com.example.demo.dto.BookUpdateRequest;
import com.example.demo.model.Book;
import com.example.demo.repository.BookRepository;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class BookService {

    private static final Logger log =
            LoggerFactory.getLogger(BookService.class);

    private final BookRepository bookRepository;

    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    @PostConstruct
    public void init() {
        BookCreateRequest book1 = new BookCreateRequest();
        book1.setTitle("Spring Boot in Action");
        book1.setAuthor("Craig Walls");
        book1.setPrice(39.99);
        book1.setIsbn("978-1617292545");
        createBook(book1);

        BookCreateRequest book2 = new BookCreateRequest();
        book2.setTitle("Clean Code");
        book2.setAuthor("Robert C. Martin");
        book2.setPrice(34.99);
        book2.setIsbn("978-0132350884");
        createBook(book2);

        log.info("Loaded {} sample books", bookRepository.findAll().size());
    }

    public List<BookResponse> getAllBooks() {
        return bookRepository.findAll().stream()
                .map(this::toResponse)
                .toList();
    }

    public Optional<BookResponse> getBookById(Long id) {
        return bookRepository.findById(id)
                .map(this::toResponse);
    }

    public BookResponse createBook(BookCreateRequest request) {
        Book book = new Book();
        book.setTitle(request.getTitle());
        book.setAuthor(request.getAuthor());
        book.setPrice(request.getPrice());
        book.setIsbn(request.getIsbn());

        Book saved = bookRepository.save(book);
        log.info("Created book: {} (ID: {})",
                saved.getTitle(), saved.getId());
        return toResponse(saved);
    }

    public Optional<BookResponse> updateBook(Long id,
                                  BookUpdateRequest request) {
        return bookRepository.findById(id)
                .map(existing -> {
                    existing.setTitle(request.getTitle());
                    existing.setAuthor(request.getAuthor());
                    existing.setPrice(request.getPrice());
                    existing.setUpdatedAt(LocalDateTime.now());
                    Book updated = bookRepository.save(existing);
                    log.info("Updated book ID: {}", id);
                    return toResponse(updated);
                });
    }

    public boolean deleteBook(Long id) {
        boolean deleted = bookRepository.deleteById(id);
        if (deleted) {
            log.info("Deleted book ID: {}", id);
        }
        return deleted;
    }

    private BookResponse toResponse(Book book) {
        return new BookResponse(
                book.getId(),
                book.getTitle(),
                book.getAuthor(),
                book.getPrice(),
                book.getIsbn(),
                book.getCreatedAt(),
                book.getUpdatedAt()
        );
    }
}
```

### The Complete CRUD Controller

```java
package com.example.demo.controller;

import com.example.demo.dto.BookCreateRequest;
import com.example.demo.dto.BookResponse;
import com.example.demo.dto.BookUpdateRequest;
import com.example.demo.service.BookService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/books")
public class BookController {

    private final BookService bookService;

    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    // CREATE - POST /api/books
    @PostMapping
    public ResponseEntity<BookResponse> createBook(
            @RequestBody BookCreateRequest request) {
        BookResponse created = bookService.createBook(request);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(created);
    }

    // READ ALL - GET /api/books
    @GetMapping
    public ResponseEntity<List<BookResponse>> getAllBooks() {
        List<BookResponse> books = bookService.getAllBooks();
        return ResponseEntity.ok(books);
    }

    // READ ONE - GET /api/books/{id}
    @GetMapping("/{id}")
    public ResponseEntity<BookResponse> getBookById(
            @PathVariable Long id) {
        return bookService.getBookById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // UPDATE - PUT /api/books/{id}
    @PutMapping("/{id}")
    public ResponseEntity<BookResponse> updateBook(
            @PathVariable Long id,
            @RequestBody BookUpdateRequest request) {
        return bookService.updateBook(id, request)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // DELETE - DELETE /api/books/{id}
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBook(@PathVariable Long id) {
        if (bookService.deleteBook(id)) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
```

**Line-by-line explanation of the CRUD operations:**

- **CREATE** (`@PostMapping`): Takes a `BookCreateRequest` from the request body. Returns 201 Created with the new book.
- **READ ALL** (`@GetMapping`): Returns all books as a list. Returns 200 OK.
- **READ ONE** (`@GetMapping("/{id}")`): Returns a single book by ID. Returns 200 OK if found, 404 Not Found if not.
- **UPDATE** (`@PutMapping("/{id}")`): Takes the ID from the URL and update data from the body. Returns 200 OK if updated, 404 if the book does not exist.
- **DELETE** (`@DeleteMapping("/{id}")`): Takes the ID from the URL. Returns 204 No Content if deleted, 404 if not found.

### CRUD Endpoint Summary

```
+--------+------------------+---------------------+---------+
| Method | URL              | Action              | Status  |
+--------+------------------+---------------------+---------+
| POST   | /api/books       | Create a new book   | 201     |
| GET    | /api/books       | Get all books       | 200     |
| GET    | /api/books/{id}  | Get one book        | 200/404 |
| PUT    | /api/books/{id}  | Update a book       | 200/404 |
| DELETE | /api/books/{id}  | Delete a book       | 204/404 |
+--------+------------------+---------------------+---------+
```

### Testing the Complete CRUD API

```bash
# CREATE: Add a new book
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Head First Java", "author": "Kathy Sierra", "price": 29.99, "isbn": "978-0596009205"}'

# Response: 201 Created
# {"id":3,"title":"Head First Java","author":"Kathy Sierra",
#  "price":29.99,"isbn":"978-0596009205",
#  "createdAt":"2024-01-15T10:30:00","updatedAt":"2024-01-15T10:30:00"}
```

```bash
# READ ALL: Get all books
curl http://localhost:8080/api/books

# Response: 200 OK
# [{"id":1,"title":"Spring Boot in Action",...},
#  {"id":2,"title":"Clean Code",...},
#  {"id":3,"title":"Head First Java",...}]
```

```bash
# READ ONE: Get book by ID
curl http://localhost:8080/api/books/1

# Response: 200 OK
# {"id":1,"title":"Spring Boot in Action","author":"Craig Walls",...}
```

```bash
# UPDATE: Update book price and title
curl -X PUT http://localhost:8080/api/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Spring Boot in Action (2nd Edition)", "author": "Craig Walls", "price": 44.99}'

# Response: 200 OK
# {"id":1,"title":"Spring Boot in Action (2nd Edition)",...,"price":44.99,...}
```

```bash
# DELETE: Remove a book
curl -X DELETE http://localhost:8080/api/books/3

# Response: 204 No Content (empty body)
```

```bash
# Verify deletion
curl http://localhost:8080/api/books/3

# Response: 404 Not Found
```

---

## Common Mistakes

### Mistake 1: Wrong HTTP Method

```bash
# WRONG: Using GET to create a resource
curl "http://localhost:8080/api/books?title=Test&author=Bob"
# This reads, it does not create

# CORRECT: Use POST to create
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "author": "Bob"}'
```

### Mistake 2: Returning Entity Instead of DTO

```java
// WRONG: Exposes internal fields
@GetMapping("/{id}")
public Book getBook(@PathVariable Long id) {
    return bookRepository.findById(id).orElseThrow();
    // Client sees: purchaseCost, supplierCode, etc.
}
```

```java
// CORRECT: Return a DTO
@GetMapping("/{id}")
public ResponseEntity<BookResponse> getBook(@PathVariable Long id) {
    return bookService.getBookById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
}
```

### Mistake 3: Always Returning 200

```java
// WRONG: Returns 200 even for creation
@PostMapping
public Book createBook(@RequestBody BookCreateRequest request) {
    return bookService.createBook(request);
    // Status is 200, but it should be 201
}
```

```java
// CORRECT: Return appropriate status codes
@PostMapping
public ResponseEntity<BookResponse> createBook(
        @RequestBody BookCreateRequest request) {
    BookResponse created = bookService.createBook(request);
    return ResponseEntity.status(HttpStatus.CREATED).body(created);
}
```

### Mistake 4: Path Variable Name Mismatch

```java
// WRONG: Name mismatch
@GetMapping("/{bookId}")
public Book getBook(@PathVariable Long id) {
    // "bookId" in URL but "id" in parameter -- Spring throws an error
}
```

```java
// CORRECT: Names must match
@GetMapping("/{bookId}")
public Book getBook(@PathVariable Long bookId) {
    return bookService.getBookById(bookId);
}
// OR use explicit naming:
@GetMapping("/{bookId}")
public Book getBook(@PathVariable("bookId") Long id) {
    return bookService.getBookById(id);
}
```

---

## Best Practices

1. **Use DTOs.** Never expose your internal entities directly. DTOs protect your API from internal changes.

2. **Return proper HTTP status codes.** 201 for creation, 204 for deletion, 404 for not found. Clients depend on these codes.

3. **Use `ResponseEntity` for all endpoints.** It gives you consistent control over status codes and headers.

4. **Validate path variables.** Check that the resource exists before operating on it. Return 404 if it does not.

5. **Use `@RequestMapping` at the class level** for a common base path. This keeps your method-level mappings short.

6. **Make request DTOs separate from response DTOs.** They serve different purposes and often have different fields.

7. **Keep controllers thin.** The controller should only handle HTTP concerns: reading parameters, calling services, and building responses. Business logic belongs in the service layer.

8. **Use meaningful URL paths.** `/api/books/{id}` is better than `/api/getBook?id=1`.

---

## Quick Summary

- `@PathVariable` extracts values from the URL path (`/books/{id}`). Use it to identify specific resources.
- `@RequestParam` extracts query parameters (`/books?author=Craig`). Use it for filtering and searching.
- `@RequestBody` reads JSON from the request body and converts it to a Java object.
- `ResponseEntity` gives you full control over the HTTP response: status code, headers, and body.
- HTTP status codes tell the client what happened: 200 OK, 201 Created, 204 No Content, 404 Not Found.
- **DTOs** separate your internal data model from what the API exposes. Use separate DTOs for requests and responses.
- **CRUD** operations map to HTTP methods: POST (Create), GET (Read), PUT (Update), DELETE (Delete).

---

## Key Points

- Path variables identify resources. Query parameters filter or modify the result.
- Always use `ResponseEntity` to return appropriate HTTP status codes.
- DTOs protect your internal model from being exposed to clients.
- A complete CRUD controller needs five endpoints: Create, Read All, Read One, Update, Delete.
- Keep controllers thin -- delegate business logic to services.
- Match path variable names in the URL template to the method parameter.

---

## Practice Questions

1. What is the difference between `@PathVariable` and `@RequestParam`? Give an example URL for each.

2. Why should you use DTOs instead of returning your entity objects directly?

3. What HTTP status code should you return when: (a) a resource is created, (b) a resource is deleted, (c) a resource is not found?

4. Explain how `ResponseEntity` differs from returning a plain object from a controller method.

5. You need an endpoint where clients can search for books by title and optionally filter by minimum price. What would the URL look like, and which annotations would you use?

---

## Exercises

### Exercise 1: Employee CRUD API

Build a complete CRUD API for employees with:

- `Employee` model: `id`, `name`, `email`, `department`, `salary`, `hireDate`
- `EmployeeCreateRequest` DTO (no id, no hireDate)
- `EmployeeResponse` DTO (all fields)
- `EmployeeUpdateRequest` DTO (name, department, salary only)
- All five CRUD endpoints with proper status codes
- A `GET /api/employees/department/{dept}` endpoint that returns employees in a specific department

### Exercise 2: Product API with Search

Build a product API with:

- `Product` model: `id`, `name`, `category`, `price`, `inStock` (boolean)
- `GET /api/products` with optional query parameters: `category`, `minPrice`, `maxPrice`, `inStock`
- `POST /api/products` to create
- `PUT /api/products/{id}` to update
- `DELETE /api/products/{id}` to delete
- Use DTOs for all request and response objects

### Exercise 3: Convert Chapter 9 Exercises

Take the Movie API or Todo API from Chapter 9 exercises and:

- Add DTOs for request and response
- Use `ResponseEntity` with proper status codes
- Add query parameter search (e.g., search movies by genre or year)
- Add PUT and DELETE endpoints

---

## What Is Next?

You can now handle all kinds of requests and build complete CRUD APIs. But what happens when a client sends invalid data? An empty title? A negative price? An email without an `@` symbol? Your application should reject bad data gracefully. In the next chapter, you will learn **input validation** -- how to ensure the data your API receives is correct before processing it.
