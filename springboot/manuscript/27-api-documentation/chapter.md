# Chapter 27: API Documentation with OpenAPI and Swagger

## What You Will Learn

- What API documentation is and why it matters.
- How to add OpenAPI documentation to your Spring Boot app with one dependency.
- How to access the Swagger UI at `/swagger-ui.html`.
- How to describe your endpoints with `@Operation` and `@ApiResponse`.
- How to document your data models with `@Schema`.
- How to group endpoints with `@Tag`.
- How to hide internal endpoints from the documentation.
- How to customize the API info (title, version, description).
- How to test your API directly from the Swagger UI.

## Why This Chapter Matters

Imagine you just built a beautiful restaurant. The food is amazing. But there is no menu. Customers walk in, sit down, and have no idea what they can order. They have to keep asking the waiter, "What do you have? How much does it cost? What ingredients are in it?"

That is what it is like when your API has no documentation.

API documentation is your menu. It tells developers:

- What endpoints are available.
- What data to send.
- What data they will get back.
- What errors might occur.

Without documentation, other developers (and even your future self) will waste hours guessing how your API works. With good documentation, they can start using your API in minutes.

In this chapter, you will create interactive documentation that not only describes your API but also lets people test it directly from the browser.

---

## 27.1 What Are OpenAPI and Swagger?

These two terms are related but different. Let us clear up the confusion.

**OpenAPI** is a specification (a set of rules) for describing REST APIs. It defines a standard format for documenting your endpoints, request bodies, responses, and more. Think of it as a universal template for writing API menus.

**Swagger** is a set of tools that work with the OpenAPI specification. The most popular tool is **Swagger UI**, which turns your OpenAPI specification into a beautiful, interactive web page.

```
+------------------+       +------------------+       +------------------+
|  Your Spring     |       |  OpenAPI         |       |  Swagger UI      |
|  Boot App        |------>|  Specification   |------>|  (Interactive    |
|  (Java code)     |       |  (JSON/YAML)     |       |   web page)     |
+------------------+       +------------------+       +------------------+

Your code gets           A machine-readable         A human-readable
scanned automatically    description of your API    web page for exploring
                                                    and testing your API
```

| Term | What It Is | Analogy |
|---|---|---|
| OpenAPI | The specification standard | The template for a menu |
| OpenAPI Spec | The actual JSON/YAML document | The completed menu |
| Swagger UI | The interactive web interface | The beautifully printed menu card |
| springdoc-openapi | The library that generates the spec | The printer that creates the menu |

---

## 27.2 Adding OpenAPI to Your Spring Boot App

Adding API documentation to Spring Boot is incredibly easy. One dependency and you are done.

### Step 1: Add the Dependency

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.4</version>
</dependency>
```

That is it. Seriously. Just one dependency.

### Step 2: Start Your Application

```bash
./mvnw spring-boot:run
```

### Step 3: Open Swagger UI

Open your browser and go to:

```
http://localhost:8080/swagger-ui.html
```

You will see a beautiful interactive page listing all your API endpoints. Spring Boot scanned your controllers and generated the documentation automatically.

### What Happened Behind the Scenes?

```
+-------------------+
| Spring Boot Starts |
+--------+----------+
         |
         v
+--------+----------+
| springdoc-openapi  |
| scans your app     |
| for @RestController|
| @GetMapping, etc.  |
+--------+----------+
         |
         v
+--------+----------+
| Generates OpenAPI  |
| spec at:           |
| /v3/api-docs       |
+--------+----------+
         |
         v
+--------+----------+
| Swagger UI reads   |
| the spec and       |
| renders it at:     |
| /swagger-ui.html   |
+--------------------+
```

### Useful URLs

| URL | What It Shows |
|---|---|
| `/swagger-ui.html` | The interactive Swagger UI page |
| `/v3/api-docs` | The raw OpenAPI spec in JSON format |
| `/v3/api-docs.yaml` | The raw OpenAPI spec in YAML format |

---

## 27.3 Customizing API Information

The default documentation shows "OpenAPI definition" as the title. Let us make it more professional.

### Creating an OpenAPI Configuration

```java
// src/main/java/com/example/bookstore/config/OpenApiConfig.java

package com.example.bookstore.config;

import io.swagger.v3.oas.models.OpenAPI;                   // 1
import io.swagger.v3.oas.models.info.Contact;               // 2
import io.swagger.v3.oas.models.info.Info;                   // 3
import io.swagger.v3.oas.models.info.License;                // 4
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {                         // 5

        return new OpenAPI()
            .info(new Info()                                 // 6
                .title("BookStore API")                      // 7
                .version("1.0.0")                            // 8
                .description(                                // 9
                    "REST API for managing a bookstore. "
                    + "Supports CRUD operations for books, "
                    + "authors, and orders.")
                .contact(new Contact()                       // 10
                    .name("BookStore Team")
                    .email("support@bookstore.com")
                    .url("https://bookstore.com"))
                .license(new License()                       // 11
                    .name("Apache 2.0")
                    .url("https://www.apache.org/licenses/"
                         + "LICENSE-2.0"))
            );
    }
}
```

**Line-by-line explanation:**

- **Line 1**: Import the `OpenAPI` class from the Swagger models library.
- **Line 2-4**: Import classes for contact, info, and license details.
- **Line 5**: Create a `@Bean` that returns a customized `OpenAPI` object.
- **Line 6**: Set the API information section.
- **Line 7**: The title shown at the top of Swagger UI.
- **Line 8**: The API version number.
- **Line 9**: A description of what the API does.
- **Line 10**: Contact information for the API maintainers.
- **Line 11**: License information.

Now Swagger UI shows your custom title, version, and description instead of the defaults.

### Using application.properties for Basic Customization

```properties
# application.properties

# Change the Swagger UI path (default: /swagger-ui.html)
springdoc.swagger-ui.path=/api-docs

# Change the OpenAPI spec path (default: /v3/api-docs)
springdoc.api-docs.path=/api-spec

# Sort endpoints alphabetically
springdoc.swagger-ui.operationsSorter=alpha

# Expand/collapse sections by default
springdoc.swagger-ui.docExpansion=none

# Disable "Try it out" by default
springdoc.swagger-ui.tryItOutEnabled=false
```

---

## 27.4 Documenting Endpoints with @Operation

The auto-generated documentation shows your endpoints, but the descriptions are generic. `@Operation` lets you add detailed descriptions to each endpoint.

### Before: Generic Documentation

Without annotations, Swagger shows method names like `getBook` and `createBook` with no explanation. Users have to guess what each endpoint does.

### After: Rich Documentation

```java
// src/main/java/com/example/bookstore/controller/BookController.java

package com.example.bookstore.controller;

import com.example.bookstore.entity.Book;
import com.example.bookstore.service.BookService;
import io.swagger.v3.oas.annotations.Operation;             // 1
import io.swagger.v3.oas.annotations.Parameter;             // 2
import io.swagger.v3.oas.annotations.responses.ApiResponse;  // 3
import io.swagger.v3.oas.annotations.responses.ApiResponses; // 4
import io.swagger.v3.oas.annotations.tags.Tag;              // 5
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/books")
@Tag(name = "Books",                                        // 6
     description = "Endpoints for managing books")
public class BookController {

    private final BookService bookService;

    public BookController(BookService bookService) {
        this.bookService = bookService;
    }

    @PostMapping
    @Operation(                                              // 7
        summary = "Create a new book",                       // 8
        description = "Creates a new book in the bookstore. "
            + "The book ID is generated automatically."      // 9
    )
    @ApiResponses({                                          // 10
        @ApiResponse(
            responseCode = "201",                            // 11
            description = "Book created successfully"
        ),
        @ApiResponse(
            responseCode = "400",                            // 12
            description = "Invalid book data provided"
        )
    })
    public ResponseEntity<Book> createBook(
            @RequestBody Book book) {

        Book created = bookService.createBook(book);
        return ResponseEntity.status(HttpStatus.CREATED)
                             .body(created);
    }

    @GetMapping("/{id}")
    @Operation(
        summary = "Get a book by ID",
        description = "Returns a single book by its unique ID."
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Book found"
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Book not found"
        )
    })
    public ResponseEntity<Book> getBook(
            @Parameter(description = "The book ID",          // 13
                       example = "1")                        // 14
            @PathVariable Long id) {

        Book book = bookService.getBookById(id);
        return ResponseEntity.ok(book);
    }

    @GetMapping
    @Operation(
        summary = "Get all books",
        description = "Returns a list of all books in the "
            + "bookstore. Returns an empty list if no "
            + "books exist."
    )
    @ApiResponse(
        responseCode = "200",
        description = "List of books retrieved successfully"
    )
    public ResponseEntity<List<Book>> getAllBooks() {
        return ResponseEntity.ok(bookService.getAllBooks());
    }

    @PutMapping("/{id}")
    @Operation(
        summary = "Update an existing book",
        description = "Updates all fields of an existing book. "
            + "The book must exist or a 404 is returned."
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "200",
            description = "Book updated successfully"
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Book not found"
        )
    })
    public ResponseEntity<Book> updateBook(
            @Parameter(description = "The book ID to update")
            @PathVariable Long id,
            @RequestBody Book book) {

        Book updated = bookService.updateBook(id, book);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    @Operation(
        summary = "Delete a book",
        description = "Permanently removes a book from "
            + "the bookstore."
    )
    @ApiResponses({
        @ApiResponse(
            responseCode = "204",
            description = "Book deleted successfully"
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Book not found"
        )
    })
    public ResponseEntity<Void> deleteBook(
            @Parameter(description = "The book ID to delete")
            @PathVariable Long id) {

        bookService.deleteBook(id);
        return ResponseEntity.noContent().build();
    }
}
```

**Key annotations explained:**

- **Line 1/7**: `@Operation` describes what a single endpoint does.
- **Line 8**: `summary` is a short one-line description shown in the endpoint list.
- **Line 9**: `description` is a longer explanation shown when you expand the endpoint.
- **Line 2/13**: `@Parameter` describes a path variable or query parameter.
- **Line 14**: `example` provides a sample value shown in Swagger UI.
- **Line 3-4/10**: `@ApiResponses` and `@ApiResponse` describe the possible responses.
- **Line 11**: Response code `"201"` with its description.
- **Line 12**: Response code `"400"` for error cases.
- **Line 5/6**: `@Tag` groups related endpoints together (more on this next).

---

## 27.5 Documenting Data Models with @Schema

Your API returns and accepts JSON objects. `@Schema` describes the fields in those objects.

```java
// src/main/java/com/example/bookstore/entity/Book.java

package com.example.bookstore.entity;

import io.swagger.v3.oas.annotations.media.Schema;          // 1
import jakarta.persistence.*;

@Entity
@Table(name = "books")
@Schema(description = "Represents a book in the bookstore") // 2
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Schema(                                                 // 3
        description = "Unique identifier of the book",
        example = "1",
        accessMode = Schema.AccessMode.READ_ONLY             // 4
    )
    private Long id;

    @Column(nullable = false)
    @Schema(                                                 // 5
        description = "Title of the book",
        example = "Spring Boot in Action",
        requiredMode = Schema.RequiredMode.REQUIRED,          // 6
        maxLength = 255
    )
    private String title;

    @Column(nullable = false)
    @Schema(
        description = "Author of the book",
        example = "Craig Walls",
        requiredMode = Schema.RequiredMode.REQUIRED
    )
    private String author;

    @Column(nullable = false)
    @Schema(
        description = "Price of the book in USD",
        example = "49.99",
        minimum = "0",                                       // 7
        requiredMode = Schema.RequiredMode.REQUIRED
    )
    private double price;

    // Constructors, getters, and setters...
    public Book() {}

    public Book(String title, String author, double price) {
        this.title = title;
        this.author = author;
        this.price = price;
    }

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

**Key annotations explained:**

- **Line 1/3**: `@Schema` describes a field in the data model.
- **Line 2**: `@Schema` on the class describes the entire model.
- **Line 4**: `accessMode = READ_ONLY` means this field is only in responses, not requests. Users do not send the `id` when creating a book.
- **Line 5**: Description and example help users understand what value to provide.
- **Line 6**: `requiredMode = REQUIRED` marks the field as mandatory.
- **Line 7**: `minimum = "0"` tells users the price must be zero or positive.

Now when users look at the Schemas section of Swagger UI, they see a detailed description of every field with examples.

```
In Swagger UI, the Book schema looks like:

Book {
  id*        integer($int64)    readOnly: true
             Unique identifier of the book
             Example: 1

  title*     string
             Title of the book
             Example: Spring Boot in Action

  author*    string
             Author of the book
             Example: Craig Walls

  price*     number($double)    minimum: 0
             Price of the book in USD
             Example: 49.99
}

* = required
```

---

## 27.6 Grouping Endpoints with @Tag

As your API grows, you will have many endpoints. `@Tag` groups related endpoints under a common heading in Swagger UI.

```java
// BookController.java
@RestController
@RequestMapping("/api/books")
@Tag(name = "Books",
     description = "Endpoints for managing books")
public class BookController { ... }

// AuthorController.java
@RestController
@RequestMapping("/api/authors")
@Tag(name = "Authors",
     description = "Endpoints for managing authors")
public class AuthorController { ... }

// OrderController.java
@RestController
@RequestMapping("/api/orders")
@Tag(name = "Orders",
     description = "Endpoints for placing and managing orders")
public class OrderController { ... }
```

In Swagger UI, endpoints are now grouped:

```
+------------------------------------------+
|  BookStore API  v1.0.0                   |
+------------------------------------------+
|                                          |
|  Books                                   |
|  Endpoints for managing books            |
|  +------------------------------------+  |
|  | POST   /api/books                  |  |
|  | GET    /api/books                  |  |
|  | GET    /api/books/{id}             |  |
|  | PUT    /api/books/{id}             |  |
|  | DELETE /api/books/{id}             |  |
|  +------------------------------------+  |
|                                          |
|  Authors                                 |
|  Endpoints for managing authors          |
|  +------------------------------------+  |
|  | POST   /api/authors                |  |
|  | GET    /api/authors                |  |
|  | GET    /api/authors/{id}           |  |
|  +------------------------------------+  |
|                                          |
|  Orders                                  |
|  Endpoints for placing and managing...   |
|  +------------------------------------+  |
|  | POST   /api/orders                 |  |
|  | GET    /api/orders                 |  |
|  | GET    /api/orders/{id}            |  |
|  +------------------------------------+  |
+------------------------------------------+
```

### Ordering Tags

You can control the order of tag groups:

```properties
# application.properties
springdoc.swagger-ui.tagsSorter=alpha
```

Or define the order in your OpenAPI config:

```java
@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .info(new Info().title("BookStore API").version("1.0"))
        .tags(List.of(
            new io.swagger.v3.oas.models.tags.Tag()
                .name("Books").description("Book management"),
            new io.swagger.v3.oas.models.tags.Tag()
                .name("Authors").description("Author management"),
            new io.swagger.v3.oas.models.tags.Tag()
                .name("Orders").description("Order management")
        ));
}
```

---

## 27.7 Hiding Endpoints

Not all endpoints should be visible in the documentation. Internal health checks, admin endpoints, or debug endpoints should be hidden from the public API docs.

### Option 1: Hide a Single Endpoint

```java
import io.swagger.v3.oas.annotations.Hidden;

@RestController
@RequestMapping("/api/internal")
public class InternalController {

    @Hidden                                         // 1
    @GetMapping("/debug")
    public String debugInfo() {
        return "Internal debug information";
    }
}
```

- **Line 1**: `@Hidden` removes this endpoint from the Swagger UI and OpenAPI spec.

### Option 2: Hide an Entire Controller

```java
@Hidden                                             // Hides all endpoints
@RestController
@RequestMapping("/api/admin")
public class AdminController {

    @GetMapping("/stats")
    public String stats() { ... }

    @PostMapping("/reset")
    public String reset() { ... }
}
```

### Option 3: Hide Using Properties

```properties
# application.properties

# Only include specific paths in the documentation
springdoc.paths-to-match=/api/books/**, /api/authors/**

# Exclude specific paths
springdoc.paths-to-exclude=/api/internal/**, /api/admin/**
```

### Option 4: Disable Swagger UI in Production

```properties
# application-prod.properties
# Completely disable Swagger UI in production
springdoc.api-docs.enabled=false
springdoc.swagger-ui.enabled=false
```

```properties
# application-dev.properties
# Enable Swagger UI in development
springdoc.api-docs.enabled=true
springdoc.swagger-ui.enabled=true
```

```
Development:                         Production:
+-------------------+               +-------------------+
| /swagger-ui.html  |               | /swagger-ui.html  |
| AVAILABLE         |               | 404 NOT FOUND     |
| (for developers)  |               | (hidden)          |
+-------------------+               +-------------------+
```

---

## 27.8 Testing Your API from Swagger UI

One of the best features of Swagger UI is the "Try it out" button. You can test your API directly from the browser without curl or Postman.

### Step-by-Step: Testing the Create Endpoint

1. Open `http://localhost:8080/swagger-ui.html` in your browser.
2. Find the `POST /api/books` endpoint under the "Books" section.
3. Click on it to expand the details.
4. Click the **"Try it out"** button.
5. Edit the request body:

```json
{
  "title": "Spring Boot in Action",
  "author": "Craig Walls",
  "price": 49.99
}
```

6. Click **"Execute"**.
7. See the response:

```
Response Code: 201

Response Body:
{
  "id": 1,
  "title": "Spring Boot in Action",
  "author": "Craig Walls",
  "price": 49.99
}

Response Headers:
content-type: application/json
```

### Testing the Get Endpoint

1. Expand `GET /api/books/{id}`.
2. Click "Try it out".
3. Enter `1` in the `id` field.
4. Click "Execute".
5. See the book you just created in the response.

```
Swagger UI Test Flow:

+--------+     +-----------+     +--------+     +----------+
| Click  |     | Enter     |     | Click  |     | See      |
| "Try   |---->| Request   |---->|"Execute|---->| Response |
|  it    |     | Data      |     |"       |     | (JSON)   |
|  out"  |     |           |     |        |     |          |
+--------+     +-----------+     +--------+     +----------+
```

### Configuring Default Values for Testing

You can set default values that appear in the "Try it out" form:

```java
@PostMapping
@Operation(summary = "Create a new book")
public ResponseEntity<Book> createBook(
    @io.swagger.v3.oas.annotations.parameters.RequestBody(
        description = "Book data to create",
        required = true,
        content = @io.swagger.v3.oas.annotations.media.Content(
            examples = @io.swagger.v3.oas.annotations.media
                .ExampleObject(
                    name = "Sample Book",
                    value = """
                        {
                            "title": "Spring Boot in Action",
                            "author": "Craig Walls",
                            "price": 49.99
                        }
                        """
                )
        )
    )
    @RequestBody Book book) {

    Book created = bookService.createBook(book);
    return ResponseEntity.status(HttpStatus.CREATED)
                         .body(created);
}
```

---

## 27.9 Complete Example: Fully Documented API

Here is a complete example that brings together everything we have learned:

```java
// src/main/java/com/example/bookstore/config/OpenApiConfig.java

package com.example.bookstore.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI bookstoreOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("BookStore API")
                .version("1.0.0")
                .description(
                    "A complete REST API for managing a "
                    + "bookstore. Supports creating, reading, "
                    + "updating, and deleting books.")
                .contact(new Contact()
                    .name("BookStore Support")
                    .email("support@bookstore.com"))
                .license(new License()
                    .name("MIT License")
                    .url("https://opensource.org/licenses/MIT"))
            )
            .servers(List.of(
                new Server()
                    .url("http://localhost:8080")
                    .description("Development Server"),
                new Server()
                    .url("https://api.bookstore.com")
                    .description("Production Server")
            ));
    }
}
```

```properties
# application.properties

# Swagger UI customization
springdoc.swagger-ui.path=/swagger-ui.html
springdoc.swagger-ui.operationsSorter=method
springdoc.swagger-ui.tagsSorter=alpha
springdoc.swagger-ui.tryItOutEnabled=true
springdoc.swagger-ui.filter=true
springdoc.swagger-ui.docExpansion=list

# Include only public API paths
springdoc.paths-to-match=/api/**
```

---

## Common Mistakes

### Mistake 1: Forgetting to Add the Dependency

```xml
<!-- WRONG: Using the old Springfox library -->
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-boot-starter</artifactId>
    <version>3.0.0</version>
</dependency>
```

```xml
<!-- CORRECT: Use springdoc-openapi for Spring Boot 3.x -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.4</version>
</dependency>
```

Springfox is no longer maintained and does not work with Spring Boot 3. Always use springdoc-openapi.

### Mistake 2: Leaving Swagger UI Enabled in Production

```properties
# WRONG: Swagger UI accessible in production
# (no profile-specific config)
springdoc.swagger-ui.enabled=true
```

```properties
# CORRECT: Disable in production
# application-prod.properties
springdoc.api-docs.enabled=false
springdoc.swagger-ui.enabled=false
```

Exposing your API documentation in production can reveal internal endpoints, data structures, and potential attack vectors.

### Mistake 3: Over-Documenting with Redundant Information

```java
// WRONG: The summary just repeats the URL
@GetMapping("/{id}")
@Operation(summary = "GET /api/books/{id}")  // Redundant!
public ResponseEntity<Book> getBook(...) { }
```

```java
// CORRECT: Add meaningful information
@GetMapping("/{id}")
@Operation(summary = "Get a book by its unique ID")
public ResponseEntity<Book> getBook(...) { }
```

### Mistake 4: Not Documenting Error Responses

```java
// WRONG: Only documenting the happy path
@Operation(summary = "Get a book")
@ApiResponse(responseCode = "200", description = "Success")
public ResponseEntity<Book> getBook(...) { }
```

```java
// CORRECT: Document all possible responses
@Operation(summary = "Get a book")
@ApiResponses({
    @ApiResponse(responseCode = "200",
                 description = "Book found"),
    @ApiResponse(responseCode = "404",
                 description = "Book not found"),
    @ApiResponse(responseCode = "500",
                 description = "Internal server error")
})
public ResponseEntity<Book> getBook(...) { }
```

---

## Best Practices

1. **Add meaningful summaries.** Every endpoint should have a clear `summary` that explains what it does in plain English.

2. **Document all response codes.** Show both success and error responses so API consumers know what to expect.

3. **Use @Schema on your models.** Add descriptions and examples to every field. This helps users understand what data to send and what they will receive.

4. **Group endpoints with @Tag.** Organize related endpoints together so users can find what they need quickly.

5. **Disable Swagger in production.** Use profile-specific properties to hide the documentation in production environments.

6. **Keep documentation up to date.** If you change an endpoint, update the annotations immediately. Outdated documentation is worse than no documentation.

7. **Use examples.** Add `example` values to `@Schema` and `@Parameter`. This makes "Try it out" immediately useful.

8. **Hide internal endpoints.** Use `@Hidden` or path filters to keep internal, admin, and debug endpoints out of the public documentation.

---

## Quick Summary

In this chapter, you learned how to create professional API documentation for your Spring Boot application. You added the `springdoc-openapi-starter-webmvc-ui` dependency to auto-generate an OpenAPI specification and Swagger UI. You customized the API information with titles, descriptions, and contact details. You used `@Operation` and `@ApiResponse` to describe each endpoint's purpose and possible responses. You documented your data models with `@Schema`, adding descriptions and examples for every field. You organized endpoints into logical groups with `@Tag`. You learned how to hide internal endpoints and disable Swagger in production. Finally, you tested your API directly from the browser using the Swagger UI's "Try it out" feature.

---

## Key Points

| Concept | Description |
|---|---|
| OpenAPI | A standard specification for describing REST APIs |
| Swagger UI | An interactive web page for exploring and testing APIs |
| `springdoc-openapi-starter-webmvc-ui` | The library that generates OpenAPI docs for Spring Boot 3 |
| `/swagger-ui.html` | The URL to access Swagger UI |
| `/v3/api-docs` | The URL for the raw OpenAPI specification |
| `@Operation` | Describes a single endpoint (summary and description) |
| `@ApiResponse` | Describes a possible response (code and description) |
| `@Schema` | Describes a field in a data model (description, example, constraints) |
| `@Tag` | Groups related endpoints under a common heading |
| `@Hidden` | Hides an endpoint or controller from the documentation |
| `@Parameter` | Describes a path variable or query parameter |

---

## Practice Questions

1. What is the difference between OpenAPI and Swagger? How do they relate to each other?

2. What dependency do you need to add API documentation to a Spring Boot 3 application? Why should you not use Springfox?

3. What do `@Operation`, `@ApiResponse`, and `@Schema` do? Give an example of when you would use each one.

4. Why should you disable Swagger UI in production? How do you do it?

5. How does `@Tag` improve the organization of your API documentation? Give an example.

---

## Exercises

### Exercise 1: Document a Student API

Create a `StudentController` with CRUD endpoints for students (id, name, email, grade). Add complete OpenAPI documentation:
- Custom API info (title, version, description).
- `@Operation` and `@ApiResponse` on every endpoint.
- `@Schema` on all Student fields with examples.
- `@Tag` to group the endpoints.

### Exercise 2: Multiple Tags

Create two controllers: `ProductController` and `CategoryController`. Use `@Tag` to group them separately. Add an `@Operation` that assigns a single endpoint to two tags (hint: use the `tags` property of `@Operation`).

### Exercise 3: Environment-Specific Documentation

Configure your application so that:
- In the `dev` profile, Swagger UI is accessible and shows all endpoints.
- In the `prod` profile, Swagger UI is completely disabled.
- In the `staging` profile, Swagger UI is accessible but internal endpoints are hidden.

Test each profile and verify the behavior.

---

## What Is Next?

Your API is well-documented and easy to use. But how do you know if your application is healthy in production? Is the database connected? How much memory is being used? Are there any performance bottlenecks? In the next chapter, we will learn about **Actuator and Monitoring**. Spring Boot Actuator gives you production-ready monitoring endpoints right out of the box.
