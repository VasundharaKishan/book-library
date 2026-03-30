# Chapter 9: Your First REST Controller

## What You Will Learn

In this chapter, you will learn:

- What REST is and how it works (explained with a restaurant analogy)
- The five main HTTP methods and when to use each
- How to create a REST controller with `@RestController`
- How to map URLs to methods with `@GetMapping` and `@PostMapping`
- How Spring Boot automatically converts Java objects to JSON
- How to test your endpoints with `curl`
- How to build a complete Book API with GET and POST endpoints

## Why This Chapter Matters

Your Spring Boot application is like a kitchen. It can cook amazing meals. But without a waiter to take orders and deliver food, nobody can eat. The kitchen is useless without the front-of-house staff.

A REST controller is that waiter. It stands between the outside world (web browsers, mobile apps, other services) and your application logic. It takes requests, passes them to the right service, and returns responses.

Almost every modern application needs a REST API. Mobile apps talk to REST APIs. Single-page web applications talk to REST APIs. Microservices talk to each other through REST APIs. Learning to build REST controllers is one of the most practical skills in software development.

---

## 9.1 What Is REST?

**REST** stands for **RE**presentational **S**tate **T**ransfer. That name is confusing. Let us use a simpler explanation.

REST is a set of rules for how computers talk to each other over the internet. It uses the same HTTP protocol that your web browser uses to load web pages. But instead of returning HTML pages, REST returns data (usually in JSON format).

### The Restaurant Analogy

Think of a REST API like a restaurant:

```
+------------------+     +------------------+     +------------------+
|    Customer      |     |     Waiter       |     |     Kitchen      |
|  (Client App)    |     |  (REST API)      |     |  (Your Code)     |
+------------------+     +------------------+     +------------------+
        |                        |                        |
        |  "I want the menu"     |                        |
        |  GET /menu             |                        |
        |----------------------->|                        |
        |                        |  "Get all dishes"      |
        |                        |----------------------->|
        |                        |                        |
        |                        |  [list of dishes]      |
        |                        |<-----------------------|
        |  [menu as JSON]        |                        |
        |<-----------------------|                        |
        |                        |                        |
        |  "I want to order"     |                        |
        |  POST /orders          |                        |
        |  {dish: "pasta"}       |                        |
        |----------------------->|                        |
        |                        |  "Create new order"    |
        |                        |----------------------->|
        |                        |                        |
        |                        |  order #42 created     |
        |                        |<-----------------------|
        |  {orderId: 42}         |                        |
        |<-----------------------|                        |
```

- The **customer** (client) does not go into the kitchen. They talk to the waiter.
- The **waiter** (REST API) takes the order, delivers it to the kitchen, and brings back the result.
- The **kitchen** (your services and repositories) does the actual work.

The customer does not need to know how the kitchen works. They just need to know what is on the menu (the API endpoints) and how to order (HTTP methods).

### What Is JSON?

**JSON** stands for **J**ava**S**cript **O**bject **N**otation. It is a simple text format for representing data. It looks like this:

```json
{
    "id": 1,
    "title": "Spring Boot in Action",
    "author": "Craig Walls",
    "price": 39.99,
    "available": true
}
```

JSON uses curly braces `{}` for objects, square brackets `[]` for lists, and key-value pairs separated by colons. It is the most common format for REST APIs because it is easy for both humans and computers to read.

---

## 9.2 HTTP Methods

HTTP defines several methods (also called verbs) that describe what action to take. Think of them as types of orders at a restaurant.

| HTTP Method | Purpose                | Restaurant Analogy         | Example                    |
|-------------|------------------------|----------------------------|----------------------------|
| `GET`       | Read data              | "Show me the menu"         | `GET /books`              |
| `POST`      | Create new data        | "I want to place an order" | `POST /books`             |
| `PUT`       | Update existing data   | "Change my order entirely" | `PUT /books/1`            |
| `PATCH`     | Partially update data  | "Add extra cheese"         | `PATCH /books/1`          |
| `DELETE`    | Remove data            | "Cancel my order"          | `DELETE /books/1`         |

### The Two Most Important Methods

For this chapter, we focus on `GET` and `POST`:

**GET** retrieves data. It is like asking a question. "What books do you have?" A GET request should never change data on the server. You can call it 100 times and nothing changes. This property is called **idempotent**.

**Idempotent** means doing something multiple times has the same effect as doing it once. Reading a book does not change the book. Reading it 10 times still gives you the same book. That is idempotent.

**POST** creates new data. It is like placing an order. "Here is a new book to add." A POST request changes data on the server. Calling it twice creates two records.

---

## 9.3 Creating a REST Controller with @RestController

Let us build our first REST controller step by step.

### Step 1: A Simple Hello Endpoint

```java
package com.example.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String sayHello() {
        return "Hello, World!";
    }
}
```

**Line-by-line explanation:**

- `@RestController` -- This annotation combines two things: `@Controller` (handles web requests) and `@ResponseBody` (return values are sent directly as the response body, not as view names). It tells Spring: "This class handles HTTP requests and returns data."
- `@GetMapping("/hello")` -- Maps HTTP GET requests to the URL path `/hello` to this method. When someone visits `http://localhost:8080/hello`, Spring calls this method.
- `public String sayHello()` -- A regular method that returns a String. Spring sends this String directly to the client.

**Testing with your browser:**

Start your application and open `http://localhost:8080/hello` in your browser.

**Output:**

```
Hello, World!
```

That is it. You just built your first REST endpoint.

### How It Works Under the Hood

```
Browser types: http://localhost:8080/hello
         |
         v
+-----------------------------+
| Spring Boot Embedded Server |
| (Tomcat on port 8080)       |
+-----------------------------+
         |
         | "Someone wants GET /hello"
         v
+-----------------------------+
| DispatcherServlet           |
| (Traffic Controller)        |
+-----------------------------+
         |
         | "Which method handles GET /hello?"
         | "Found: HelloController.sayHello()"
         v
+-----------------------------+
| HelloController             |
| sayHello() returns "Hello"  |
+-----------------------------+
         |
         | "Hello, World!"
         v
+-----------------------------+
| Response sent to browser    |
| Status: 200 OK              |
| Body: Hello, World!         |
+-----------------------------+
```

**DispatcherServlet** is Spring's traffic controller. It receives all incoming requests and routes them to the correct controller method. You never interact with it directly. It works behind the scenes.

---

## 9.4 Returning JSON

Returning plain text is fine for simple cases. But real APIs return JSON. The good news: Spring Boot converts Java objects to JSON automatically.

### Step 1: Create a Model Class

```java
package com.example.demo.model;

public class Book {

    private Long id;
    private String title;
    private String author;
    private double price;

    public Book() {
    }

    public Book(Long id, String title, String author, double price) {
        this.id = id;
        this.title = title;
        this.author = author;
        this.price = price;
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
}
```

**Important:** The class needs getter methods. Spring uses them to convert the object to JSON. Without getters, the JSON will be empty `{}`.

The no-argument constructor `public Book() {}` is also needed. Spring uses it when converting JSON back to a Java object (deserialization).

### Step 2: Return the Object from a Controller

```java
package com.example.demo.controller;

import com.example.demo.model.Book;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class BookController {

    @GetMapping("/books")
    public List<Book> getAllBooks() {
        return List.of(
            new Book(1L, "Spring Boot in Action", "Craig Walls", 39.99),
            new Book(2L, "Clean Code", "Robert C. Martin", 34.99),
            new Book(3L, "Effective Java", "Joshua Bloch", 44.99)
        );
    }

    @GetMapping("/books/featured")
    public Book getFeaturedBook() {
        return new Book(1L, "Spring Boot in Action",
                       "Craig Walls", 39.99);
    }
}
```

**Output for `GET /books`:**

```json
[
    {
        "id": 1,
        "title": "Spring Boot in Action",
        "author": "Craig Walls",
        "price": 39.99
    },
    {
        "id": 2,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "price": 34.99
    },
    {
        "id": 3,
        "title": "Effective Java",
        "author": "Joshua Bloch",
        "price": 44.99
    }
]
```

**Output for `GET /books/featured`:**

```json
{
    "id": 1,
    "title": "Spring Boot in Action",
    "author": "Craig Walls",
    "price": 39.99
}
```

Spring Boot uses a library called **Jackson** to convert Java objects to JSON. Jackson looks at the getter methods of your class and creates JSON properties from them. `getTitle()` becomes `"title"` in JSON. `getPrice()` becomes `"price"`.

```
Java Object                          JSON Output
─────────────                        ──────────
book.getId()      = 1         -->    "id": 1
book.getTitle()   = "Clean.." -->    "title": "Clean Code"
book.getAuthor()  = "Robert." -->    "author": "Robert C. Martin"
book.getPrice()   = 34.99     -->    "price": 34.99
```

---

## 9.5 The @PostMapping Annotation

`@GetMapping` handles GET requests (reading data). `@PostMapping` handles POST requests (creating data).

```java
package com.example.demo.controller;

import com.example.demo.model.Book;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

@RestController
public class BookController {

    private final List<Book> books = new ArrayList<>();
    private long nextId = 1;

    @GetMapping("/books")
    public List<Book> getAllBooks() {
        return books;
    }

    @PostMapping("/books")
    public Book createBook(@RequestBody Book book) {
        book.setId(nextId++);
        books.add(book);
        return book;
    }
}
```

**Line-by-line explanation:**

- `private final List<Book> books = new ArrayList<>()` -- A simple in-memory list to store books. In a real application, you would use a database.
- `private long nextId = 1` -- A counter to generate unique IDs.
- `@PostMapping("/books")` -- Maps HTTP POST requests to `/books` to this method.
- `@RequestBody Book book` -- Tells Spring: "Take the JSON from the request body and convert it into a `Book` object." This is the opposite of what happens in GET -- instead of Java to JSON, it goes JSON to Java.
- `book.setId(nextId++)` -- Assigns an auto-incrementing ID.
- `books.add(book)` -- Stores the book in the list.
- `return book` -- Returns the created book (with its new ID) as JSON.

### How @RequestBody Works

```
Client sends POST request:
─────────────────────────
POST /books
Content-Type: application/json

{
    "title": "Head First Java",
    "author": "Kathy Sierra",
    "price": 29.99
}

Spring's Jackson library converts JSON to Java:
───────────────────────────────────────────────
Book book = new Book();
book.setTitle("Head First Java");
book.setAuthor("Kathy Sierra");
book.setPrice(29.99);

Your method receives the ready-to-use Java object.
```

**@RequestBody** tells Spring to read the HTTP request body (the JSON data the client sends) and convert it into a Java object. Without this annotation, Spring does not know where to find the data.

---

## 9.6 Testing with curl

**curl** is a command-line tool for making HTTP requests. It comes pre-installed on Mac and Linux. On Windows, use Git Bash or PowerShell.

### Testing GET Requests

```bash
# Simple GET request
curl http://localhost:8080/books
```

**Output:**

```json
[]
```

The list is empty because we have not added any books yet.

```bash
# GET with pretty-printed JSON
curl -s http://localhost:8080/books | python3 -m json.tool
```

The `-s` flag means "silent" (hides progress information). We pipe the output to Python's JSON tool for formatting.

### Testing POST Requests

```bash
# Create a new book
curl -X POST http://localhost:8080/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Spring Boot in Action", "author": "Craig Walls", "price": 39.99}'
```

**Breaking down the curl command:**

- `curl` -- The command itself.
- `-X POST` -- Use the POST method instead of the default GET.
- `http://localhost:8080/books` -- The URL to send the request to.
- `-H "Content-Type: application/json"` -- A **header** that tells the server we are sending JSON data.
- `-d '{"title": ...}'` -- The **data** (request body) to send. This is the JSON that becomes a Book object.

**Output:**

```json
{
    "id": 1,
    "title": "Spring Boot in Action",
    "author": "Craig Walls",
    "price": 39.99
}
```

Notice the `id` is now `1`. Our server assigned it.

### Testing the Full Flow

```bash
# Step 1: Add first book
curl -X POST http://localhost:8080/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Spring Boot in Action", "author": "Craig Walls", "price": 39.99}'

# Output: {"id":1,"title":"Spring Boot in Action","author":"Craig Walls","price":39.99}

# Step 2: Add second book
curl -X POST http://localhost:8080/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code", "author": "Robert C. Martin", "price": 34.99}'

# Output: {"id":2,"title":"Clean Code","author":"Robert C. Martin","price":34.99}

# Step 3: Get all books
curl http://localhost:8080/books

# Output: [{"id":1,"title":"Spring Boot in Action",...},{"id":2,"title":"Clean Code",...}]
```

---

## 9.7 Building a Complete Book API

Let us put everything together into a proper Book API with a service layer.

### Project Structure

```
src/main/java/com/example/demo/
├── DemoApplication.java
├── model/
│   └── Book.java
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

public class Book {

    private Long id;
    private String title;
    private String author;
    private double price;
    private String isbn;

    public Book() {
    }

    public Book(String title, String author, double price, String isbn) {
        this.title = title;
        this.author = author;
        this.price = price;
        this.isbn = isbn;
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

    @Override
    public String toString() {
        return "Book{id=" + id + ", title='" + title + "', " +
               "author='" + author + "'}";
    }
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
            books.add(book);
        } else {
            // Update existing book
            deleteById(book.getId());
            books.add(book);
        }
        return book;
    }

    public Optional<Book> findById(Long id) {
        return books.stream()
                .filter(book -> book.getId().equals(id))
                .findFirst();
    }

    public List<Book> findAll() {
        return new ArrayList<>(books);
    }

    public boolean deleteById(Long id) {
        return books.removeIf(book -> book.getId().equals(id));
    }

    public boolean existsById(Long id) {
        return books.stream()
                .anyMatch(book -> book.getId().equals(id));
    }
}
```

### The Service

```java
package com.example.demo.service;

import com.example.demo.model.Book;
import com.example.demo.repository.BookRepository;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

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
        // Pre-load some sample books
        createBook(new Book("Spring Boot in Action",
                           "Craig Walls", 39.99, "978-1617292545"));
        createBook(new Book("Clean Code",
                           "Robert C. Martin", 34.99, "978-0132350884"));
        createBook(new Book("Effective Java",
                           "Joshua Bloch", 44.99, "978-0134685991"));
        log.info("Sample books loaded: {}",
                bookRepository.findAll().size());
    }

    public List<Book> getAllBooks() {
        return bookRepository.findAll();
    }

    public Optional<Book> getBookById(Long id) {
        return bookRepository.findById(id);
    }

    public Book createBook(Book book) {
        Book saved = bookRepository.save(book);
        log.info("Created book: {}", saved);
        return saved;
    }
}
```

### The Controller

```java
package com.example.demo.controller;

import com.example.demo.model.Book;
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

    @GetMapping
    public List<Book> getAllBooks() {
        return bookService.getAllBooks();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Book> getBookById(@PathVariable Long id) {
        return bookService.getBookById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Book> createBook(@RequestBody Book book) {
        Book created = bookService.createBook(book);
        return ResponseEntity.status(HttpStatus.CREATED)
                             .body(created);
    }
}
```

**Line-by-line explanation:**

- `@RequestMapping("/api/books")` -- Sets a base URL for all endpoints in this controller. All mappings below are relative to `/api/books`.
- `@GetMapping` -- Without a path, this maps to the base URL `/api/books`.
- `@GetMapping("/{id}")` -- The `{id}` is a **path variable**. It matches any value. `/api/books/1`, `/api/books/42`, etc.
- `@PathVariable Long id` -- Extracts the value from the URL and converts it to a Long. We will explain this in detail in the next chapter.
- `ResponseEntity<Book>` -- A wrapper that lets you control the HTTP status code and headers. We will cover this in detail in the next chapter too.
- `ResponseEntity.status(HttpStatus.CREATED)` -- Returns HTTP status 201 (Created) instead of the default 200 (OK). This is the correct status for creating a new resource.

### Testing the Complete API

```bash
# Get all books (pre-loaded sample data)
curl http://localhost:8080/api/books
```

**Output:**

```json
[
    {
        "id": 1,
        "title": "Spring Boot in Action",
        "author": "Craig Walls",
        "price": 39.99,
        "isbn": "978-1617292545"
    },
    {
        "id": 2,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "price": 34.99,
        "isbn": "978-0132350884"
    },
    {
        "id": 3,
        "title": "Effective Java",
        "author": "Joshua Bloch",
        "price": 44.99,
        "isbn": "978-0134685991"
    }
]
```

```bash
# Get a specific book
curl http://localhost:8080/api/books/1
```

**Output:**

```json
{
    "id": 1,
    "title": "Spring Boot in Action",
    "author": "Craig Walls",
    "price": 39.99,
    "isbn": "978-1617292545"
}
```

```bash
# Get a book that does not exist
curl -v http://localhost:8080/api/books/99
```

**Output (note the 404 status):**

```
< HTTP/1.1 404 Not Found
```

```bash
# Create a new book
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Head First Java", "author": "Kathy Sierra", "price": 29.99, "isbn": "978-0596009205"}'
```

**Output (note the 201 status):**

```json
{
    "id": 4,
    "title": "Head First Java",
    "author": "Kathy Sierra",
    "price": 29.99,
    "isbn": "978-0596009205"
}
```

### Request-Response Flow

```
Client: POST /api/books
        Body: {"title": "Head First Java", ...}
         |
         v
+----------------------------------+
| BookController.createBook()      |
| @RequestBody converts JSON       |
| to Book object                   |
+----------------------------------+
         |
         v
+----------------------------------+
| BookService.createBook()         |
| Logs the creation                |
+----------------------------------+
         |
         v
+----------------------------------+
| BookRepository.save()            |
| Assigns ID, stores in list       |
+----------------------------------+
         |
         v
+----------------------------------+
| Response flows back:             |
| Book (id=4) -> JSON -> Client    |
| Status: 201 Created              |
+----------------------------------+
```

---

## Common Mistakes

### Mistake 1: Forgetting @RestController

```java
// WRONG: Missing @RestController
public class BookController {
    @GetMapping("/books")
    public List<Book> getBooks() {
        return List.of();
    }
}
// Result: 404 Not Found (Spring does not know about this class)
```

```java
// CORRECT: Add @RestController
@RestController
public class BookController {
    @GetMapping("/books")
    public List<Book> getBooks() {
        return List.of();
    }
}
```

### Mistake 2: Missing @RequestBody on POST

```java
// WRONG: Missing @RequestBody
@PostMapping("/books")
public Book createBook(Book book) {
    // book will have all null fields!
    return bookService.createBook(book);
}
```

```java
// CORRECT: Add @RequestBody
@PostMapping("/books")
public Book createBook(@RequestBody Book book) {
    return bookService.createBook(book);
}
```

Without `@RequestBody`, Spring does not know to read the JSON from the request body. The Book object will be empty.

### Mistake 3: Missing No-Argument Constructor

```java
// WRONG: No default constructor
public class Book {
    private String title;

    public Book(String title) {
        this.title = title;
    }
}
// Jackson cannot deserialize JSON to this class
```

```java
// CORRECT: Add a no-argument constructor
public class Book {
    private String title;

    public Book() {}  // Required for JSON deserialization

    public Book(String title) {
        this.title = title;
    }
}
```

Jackson needs a no-argument constructor to create the object first, then uses setters to fill in the values.

### Mistake 4: Missing Getters

```java
// WRONG: No getters
public class Book {
    private String title;

    public void setTitle(String title) {
        this.title = title;
    }
    // Missing getTitle()!
}
// JSON output will be: {}
```

```java
// CORRECT: Include getters
public class Book {
    private String title;

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
}
// JSON output will be: {"title": "..."}
```

### Mistake 5: Wrong Content-Type Header in curl

```bash
# WRONG: No Content-Type header
curl -X POST http://localhost:8080/books \
  -d '{"title": "Test"}'
# Result: 415 Unsupported Media Type
```

```bash
# CORRECT: Include Content-Type header
curl -X POST http://localhost:8080/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'
```

The server needs to know the data format. The `Content-Type: application/json` header tells it "I am sending JSON."

---

## Best Practices

1. **Use a base path with `@RequestMapping`.** Put `/api/` in front of your endpoints: `/api/books`, `/api/users`. This separates API endpoints from web pages.

2. **Follow RESTful naming conventions.** Use nouns, not verbs. Use `/books` not `/getBooks` or `/createBook`. The HTTP method (GET, POST) already describes the action.

3. **Use the right HTTP status codes.** Return 201 for creation, 404 for not found. Do not always return 200. We will cover status codes in detail in the next chapter.

4. **Keep controllers thin.** Controllers should only handle request/response logic. Put business logic in services.

5. **Use plural nouns for collections.** Use `/books` not `/book`. The URL represents a collection of books.

6. **Return the created resource.** After a POST, return the created object with its assigned ID. This saves the client from making another request.

7. **Pre-load sample data for development.** Use `@PostConstruct` in a service to load test data when the app starts.

---

## Quick Summary

- **REST** is a way for programs to communicate over HTTP. It uses standard HTTP methods and returns JSON data.
- **GET** reads data. **POST** creates data. They are the two most common HTTP methods.
- `@RestController` marks a class as a REST endpoint handler. It combines `@Controller` and `@ResponseBody`.
- `@GetMapping("/path")` maps GET requests to a method. `@PostMapping("/path")` maps POST requests.
- Spring Boot uses **Jackson** to automatically convert Java objects to JSON and back.
- `@RequestBody` tells Spring to convert the incoming JSON into a Java object.
- `@RequestMapping` on a class sets a base URL for all endpoints in that controller.
- **curl** is a command-line tool for testing REST endpoints.

---

## Key Points

- Controllers are the front door of your application. Keep them thin.
- Jackson needs getters for serialization and a no-arg constructor for deserialization.
- Always include `Content-Type: application/json` when sending JSON data.
- Use `@RequestMapping` at the class level for a common base path.
- REST uses nouns for URLs and HTTP methods for actions.
- Return meaningful HTTP status codes, not just 200 for everything.

---

## Practice Questions

1. What is the difference between `@Controller` and `@RestController`? Why do we use `@RestController` for APIs?

2. Explain what `@RequestBody` does. What happens if you forget it on a POST method?

3. A client sends a POST request with `{"name": "Alice", "age": 30}` to your endpoint. Your method parameter is a `Person` object. What must the `Person` class have for this to work?

4. Why should you use `/api/books` instead of `/api/getBooks` for a GET endpoint?

5. What curl command would you use to send a POST request with JSON data to `http://localhost:8080/api/orders`?

---

## Exercises

### Exercise 1: Movie API

Create a REST API for movies with:

- `Movie` model with fields: `id`, `title`, `director`, `year`, `genre`
- `GET /api/movies` -- returns all movies
- `GET /api/movies/{id}` -- returns a specific movie
- `POST /api/movies` -- creates a new movie
- Pre-load 3 sample movies using `@PostConstruct`

Test all endpoints with curl.

### Exercise 2: Todo API

Create a simple Todo API with:

- `TodoItem` model with fields: `id`, `title`, `completed` (boolean), `createdAt` (LocalDateTime)
- `GET /api/todos` -- returns all todos
- `POST /api/todos` -- creates a new todo (set `completed` to false and `createdAt` to now)
- `GET /api/todos/pending` -- returns only todos where `completed` is false

### Exercise 3: Student Grade Tracker

Create an API that manages student grades:

- `Student` model with fields: `id`, `name`, `grade` (String like "A", "B", "C")
- `GET /api/students` -- returns all students
- `POST /api/students` -- creates a new student
- `GET /api/students/honor-roll` -- returns only students with grade "A"

Add a service layer that validates the grade is one of A, B, C, D, or F before saving.

---

## What Is Next?

You have built your first REST controller. You can handle GET and POST requests. But real APIs need more. They need to handle path variables, query parameters, different HTTP status codes, and data transfer objects. In the next chapter, you will learn **request and response handling** in depth -- everything you need to build a complete CRUD API.
