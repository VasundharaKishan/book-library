# Chapter 26: Testing

## What You Will Learn

- What the test pyramid is and why it matters.
- How to write unit tests with JUnit 5 (@Test, assertions).
- How to use Mockito to mock dependencies (@Mock, when().thenReturn()).
- How to test REST controllers with @WebMvcTest and MockMvc.
- How to write full integration tests with @SpringBootTest.
- How to test database operations with @DataJpaTest.
- How to replace beans in tests with @MockBean.
- How to configure test-specific properties.
- How to write complete CRUD API tests from start to finish.

## Why This Chapter Matters

Imagine you are a bridge builder. You build a beautiful bridge and open it to traffic. Cars drive across it every day. Then one day, you need to add a lane. You modify the bridge, and it collapses. People get hurt.

Now imagine you had a testing process. Before opening the bridge, you tested it with heavy trucks. Before adding the lane, you tested the modified design. You would have caught the weakness before anyone got hurt.

Software testing works the same way. Every time you change your code, there is a risk of breaking something. Tests are your safety net. They catch problems before your users do.

Professional developers do not ship code without tests. Companies like Google, Netflix, and Amazon run millions of tests every day. If you want to write production-quality Spring Boot applications, you need to test them.

This chapter teaches you every kind of test you need for a Spring Boot application.

---

## 26.1 The Test Pyramid

The test pyramid is a strategy for organizing your tests. It tells you what kinds of tests to write and how many of each.

```
                /\
               /  \
              / E2E\           Few (slow, expensive)
             / Tests\
            /--------\
           /Integration\       Some (medium speed)
          /   Tests     \
         /--------------\
        /   Unit Tests    \    Many (fast, cheap)
       /                   \
      +---------------------+

      More tests at bottom, fewer at top.
      Faster tests at bottom, slower at top.
```

### Three Types of Tests

| Type | What It Tests | Speed | Example |
|---|---|---|---|
| **Unit Tests** | A single class or method in isolation | Very fast (milliseconds) | Test that `calculateTotal()` returns the correct sum |
| **Integration Tests** | Multiple components working together | Medium (seconds) | Test that a controller saves data to the database |
| **End-to-End (E2E) Tests** | The entire application flow | Slow (minutes) | Test the full user registration process |

Think of it like testing a car:

- **Unit test**: Test that each part works (engine starts, brakes grip, lights turn on).
- **Integration test**: Test that parts work together (engine connects to transmission, brakes work with ABS).
- **E2E test**: Drive the car on a real road and test everything at once.

### Why the Pyramid Shape?

You want **many** unit tests because they are fast and pinpoint exact problems. You want **some** integration tests because they verify components work together. You want **few** E2E tests because they are slow and hard to maintain.

```
Test Type          Count    Speed       Maintenance
--------------------------------------------------
Unit Tests         100+     < 1 sec     Low
Integration Tests   20+     5-30 sec    Medium
E2E Tests            5+     1-5 min     High
```

---

## 26.2 Setting Up Your Test Environment

Spring Boot includes testing support out of the box. When you create a project with Spring Initializr, the test dependency is already there.

### The Test Dependency

```xml
<!-- pom.xml (already included by Spring Initializr) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

This single dependency includes:

| Library | Purpose |
|---|---|
| JUnit 5 | The testing framework (write and run tests) |
| Mockito | Mocking library (fake dependencies) |
| AssertJ | Fluent assertions (readable test checks) |
| Spring Test | Spring-specific test support |
| MockMvc | Test controllers without a real server |
| JSONPath | Assert values in JSON responses |

### Project Structure

```
src/
  main/
    java/
      com/example/bookstore/
        controller/
          BookController.java
        service/
          BookService.java
        repository/
          BookRepository.java
        entity/
          Book.java
  test/
    java/
      com/example/bookstore/
        controller/
          BookControllerTest.java       <- Controller tests
        service/
          BookServiceTest.java          <- Service unit tests
        repository/
          BookRepositoryTest.java       <- Repository tests
        BookstoreApplicationTests.java  <- Integration test
    resources/
      application-test.properties      <- Test configuration
```

Notice that the test directory mirrors the main directory. This is a convention that makes tests easy to find.

### Test Configuration

```properties
# src/test/resources/application-test.properties

# Use H2 in-memory database for tests
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true

# Disable email sending in tests
spring.mail.host=localhost
spring.mail.port=25
```

---

## 26.3 JUnit 5 Basics

JUnit 5 is the testing framework for Java. It provides annotations to mark test methods and assertions to verify results.

### Your First Test

```java
// src/test/java/com/example/bookstore/CalculatorTest.java

package com.example.bookstore;

import org.junit.jupiter.api.Test;                     // 1
import static org.junit.jupiter.api.Assertions.*;      // 2

class CalculatorTest {                                  // 3

    @Test                                               // 4
    void shouldAddTwoNumbers() {                        // 5
        // Arrange
        int a = 5;                                      // 6
        int b = 3;

        // Act
        int result = a + b;                             // 7

        // Assert
        assertEquals(8, result);                        // 8
    }

    @Test
    void shouldSubtractTwoNumbers() {
        int result = 10 - 4;
        assertEquals(6, result);
    }
}
```

**Line-by-line explanation:**

- **Line 1**: Import the `@Test` annotation from JUnit 5.
- **Line 2**: Import assertion methods like `assertEquals`, `assertTrue`, etc.
- **Line 3**: Test classes do not need to be `public` in JUnit 5.
- **Line 4**: `@Test` marks this method as a test. JUnit will run it automatically.
- **Line 5**: Test method names should describe what they test. Use `should...` naming.
- **Line 6**: **Arrange** - Set up the test data.
- **Line 7**: **Act** - Perform the action you are testing.
- **Line 8**: **Assert** - Check the result. `assertEquals(expected, actual)`.

**Output when you run the test:**

```
CalculatorTest > shouldAddTwoNumbers()       PASSED
CalculatorTest > shouldSubtractTwoNumbers()  PASSED

2 tests completed, 2 passed
```

### The AAA Pattern: Arrange, Act, Assert

Every test follows this pattern:

```
+-----------+     +-----------+     +-----------+
|  ARRANGE  |---->|    ACT    |---->|  ASSERT   |
|           |     |           |     |           |
| Set up    |     | Call the  |     | Check the |
| test data |     | method    |     | result    |
+-----------+     +-----------+     +-----------+
```

### Common JUnit 5 Assertions

```java
import static org.junit.jupiter.api.Assertions.*;

class AssertionExamplesTest {

    @Test
    void demonstrateAssertions() {
        // assertEquals: Check two values are equal
        assertEquals(4, 2 + 2);
        assertEquals("hello", "hello");

        // assertNotEquals: Check two values are NOT equal
        assertNotEquals(5, 2 + 2);

        // assertTrue / assertFalse: Check boolean conditions
        assertTrue(10 > 5);
        assertFalse(10 < 5);

        // assertNull / assertNotNull: Check for null
        String name = "John";
        assertNotNull(name);

        String empty = null;
        assertNull(empty);

        // assertThrows: Check that an exception is thrown
        assertThrows(ArithmeticException.class, () -> {
            int result = 10 / 0;
        });

        // assertEquals with message (shown on failure)
        assertEquals(4, 2 + 2,
            "Basic addition should work");
    }
}
```

### JUnit 5 Lifecycle Annotations

```java
import org.junit.jupiter.api.*;

class LifecycleTest {

    @BeforeAll                                  // 1
    static void setUpOnce() {
        System.out.println("Runs ONCE before all tests");
    }

    @BeforeEach                                 // 2
    void setUp() {
        System.out.println("Runs before EACH test");
    }

    @Test
    void testOne() {
        System.out.println("Test 1");
    }

    @Test
    void testTwo() {
        System.out.println("Test 2");
    }

    @AfterEach                                  // 3
    void tearDown() {
        System.out.println("Runs after EACH test");
    }

    @AfterAll                                   // 4
    static void tearDownOnce() {
        System.out.println("Runs ONCE after all tests");
    }
}
```

**Output:**

```
Runs ONCE before all tests
Runs before EACH test
Test 1
Runs after EACH test
Runs before EACH test
Test 2
Runs after EACH test
Runs ONCE after all tests
```

- **Line 1**: `@BeforeAll` runs once before any test. Must be `static`.
- **Line 2**: `@BeforeEach` runs before each individual test. Great for resetting state.
- **Line 3**: `@AfterEach` runs after each test. Good for cleanup.
- **Line 4**: `@AfterAll` runs once after all tests. Must be `static`.

### @DisplayName for Readable Test Names

```java
@DisplayName("Book Price Calculator")
class BookPriceCalculatorTest {

    @Test
    @DisplayName("should apply 10% discount for orders over $100")
    void shouldApplyDiscount() {
        double price = 150.0;
        double discounted = price * 0.9;
        assertEquals(135.0, discounted);
    }

    @Test
    @DisplayName("should not apply discount for orders under $100")
    void shouldNotApplyDiscount() {
        double price = 80.0;
        assertEquals(80.0, price);
    }
}
```

**Output:**

```
Book Price Calculator
  should apply 10% discount for orders over $100    PASSED
  should not apply discount for orders under $100   PASSED
```

---

## 26.4 Unit Testing with Mockito

In a real application, classes depend on other classes. Your `BookService` depends on `BookRepository`. Your `OrderService` depends on `BookService` and `EmailService`.

When you unit test `BookService`, you do not want to use a real database. You want to test `BookService` in isolation. This is where **Mockito** comes in.

Mockito creates fake (mock) objects that pretend to be your dependencies.

```
Without Mocking:                    With Mocking:

+-------------+   +----------+     +-------------+   +----------+
| BookService |-->| Real     |     | BookService |-->| Mock     |
|   (test)    |   | Database |     |   (test)    |   | (fake)   |
+-------------+   +----------+     +-------------+   +----------+
                  Slow!                               Fast!
                  Needs DB setup!                     No DB needed!
                  Can fail for                        Predictable!
                  DB reasons!
```

### The Book Entity and Service

Let us create the classes we will test:

```java
// src/main/java/com/example/bookstore/entity/Book.java

package com.example.bookstore.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "books")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String author;

    @Column(nullable = false)
    private double price;

    public Book() {}

    public Book(String title, String author, double price) {
        this.title = title;
        this.author = author;
        this.price = price;
    }

    // Getters and Setters
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

```java
// src/main/java/com/example/bookstore/repository/BookRepository.java

package com.example.bookstore.repository;

import com.example.bookstore.entity.Book;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface BookRepository extends JpaRepository<Book, Long> {
    List<Book> findByAuthor(String author);
}
```

```java
// src/main/java/com/example/bookstore/service/BookService.java

package com.example.bookstore.service;

import com.example.bookstore.entity.Book;
import com.example.bookstore.repository.BookRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class BookService {

    private final BookRepository bookRepository;

    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    public Book createBook(Book book) {
        if (book.getPrice() < 0) {
            throw new IllegalArgumentException(
                "Price cannot be negative");
        }
        return bookRepository.save(book);
    }

    public Book getBookById(Long id) {
        return bookRepository.findById(id)
            .orElseThrow(() -> new RuntimeException(
                "Book not found with id: " + id));
    }

    public List<Book> getAllBooks() {
        return bookRepository.findAll();
    }

    public Book updateBook(Long id, Book updatedBook) {
        Book existing = getBookById(id);
        existing.setTitle(updatedBook.getTitle());
        existing.setAuthor(updatedBook.getAuthor());
        existing.setPrice(updatedBook.getPrice());
        return bookRepository.save(existing);
    }

    public void deleteBook(Long id) {
        if (!bookRepository.existsById(id)) {
            throw new RuntimeException(
                "Book not found with id: " + id);
        }
        bookRepository.deleteById(id);
    }

    public List<Book> getBooksByAuthor(String author) {
        return bookRepository.findByAuthor(author);
    }
}
```

### Writing Unit Tests for BookService

```java
// src/test/java/com/example/bookstore/service/BookServiceTest.java

package com.example.bookstore.service;

import com.example.bookstore.entity.Book;
import com.example.bookstore.repository.BookRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;                           // 1
import org.mockito.Mock;                                  // 2
import org.mockito.junit.jupiter.MockitoExtension;       // 3

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;           // 4
import static org.mockito.Mockito.*;                      // 5

@ExtendWith(MockitoExtension.class)                       // 6
@DisplayName("BookService Unit Tests")
class BookServiceTest {

    @Mock                                                  // 7
    private BookRepository bookRepository;

    @InjectMocks                                           // 8
    private BookService bookService;

    private Book sampleBook;

    @BeforeEach                                            // 9
    void setUp() {
        sampleBook = new Book("Spring Boot in Action",
                              "Craig Walls", 49.99);
        sampleBook.setId(1L);
    }

    // ---- CREATE Tests ----

    @Test
    @DisplayName("should create a book successfully")
    void shouldCreateBook() {
        // Arrange
        when(bookRepository.save(any(Book.class)))         // 10
            .thenReturn(sampleBook);                       // 11

        // Act
        Book created = bookService.createBook(sampleBook); // 12

        // Assert
        assertNotNull(created);                            // 13
        assertEquals("Spring Boot in Action",
                     created.getTitle());
        assertEquals(49.99, created.getPrice());

        verify(bookRepository, times(1))                   // 14
            .save(any(Book.class));
    }

    @Test
    @DisplayName("should throw exception for negative price")
    void shouldThrowExceptionForNegativePrice() {
        // Arrange
        Book invalidBook =
            new Book("Bad Book", "Author", -10.0);

        // Act & Assert
        assertThrows(IllegalArgumentException.class, () -> {
            bookService.createBook(invalidBook);
        });

        verify(bookRepository, never()).save(any());       // 15
    }

    // ---- READ Tests ----

    @Test
    @DisplayName("should return book when found by ID")
    void shouldReturnBookById() {
        // Arrange
        when(bookRepository.findById(1L))
            .thenReturn(Optional.of(sampleBook));

        // Act
        Book found = bookService.getBookById(1L);

        // Assert
        assertNotNull(found);
        assertEquals("Spring Boot in Action", found.getTitle());
    }

    @Test
    @DisplayName("should throw exception when book not found")
    void shouldThrowWhenBookNotFound() {
        // Arrange
        when(bookRepository.findById(99L))
            .thenReturn(Optional.empty());

        // Act & Assert
        RuntimeException exception =
            assertThrows(RuntimeException.class, () -> {
                bookService.getBookById(99L);
            });

        assertEquals("Book not found with id: 99",
                     exception.getMessage());
    }

    @Test
    @DisplayName("should return all books")
    void shouldReturnAllBooks() {
        // Arrange
        Book book2 = new Book("Clean Code",
                              "Robert Martin", 39.99);
        List<Book> books = Arrays.asList(sampleBook, book2);

        when(bookRepository.findAll()).thenReturn(books);

        // Act
        List<Book> result = bookService.getAllBooks();

        // Assert
        assertEquals(2, result.size());
        verify(bookRepository, times(1)).findAll();
    }

    // ---- UPDATE Tests ----

    @Test
    @DisplayName("should update book successfully")
    void shouldUpdateBook() {
        // Arrange
        Book updatedData = new Book("Updated Title",
                                    "New Author", 59.99);

        when(bookRepository.findById(1L))
            .thenReturn(Optional.of(sampleBook));
        when(bookRepository.save(any(Book.class)))
            .thenReturn(sampleBook);

        // Act
        Book updated = bookService.updateBook(1L, updatedData);

        // Assert
        assertNotNull(updated);
        verify(bookRepository).findById(1L);
        verify(bookRepository).save(any(Book.class));
    }

    // ---- DELETE Tests ----

    @Test
    @DisplayName("should delete book successfully")
    void shouldDeleteBook() {
        // Arrange
        when(bookRepository.existsById(1L)).thenReturn(true);

        // Act
        bookService.deleteBook(1L);

        // Assert
        verify(bookRepository, times(1)).deleteById(1L);
    }

    @Test
    @DisplayName("should throw exception when deleting non-existent book")
    void shouldThrowWhenDeletingNonExistentBook() {
        // Arrange
        when(bookRepository.existsById(99L)).thenReturn(false);

        // Act & Assert
        assertThrows(RuntimeException.class, () -> {
            bookService.deleteBook(99L);
        });

        verify(bookRepository, never()).deleteById(any());
    }
}
```

**Key Mockito concepts explained:**

- **Line 6**: `@ExtendWith(MockitoExtension.class)` enables Mockito in JUnit 5 tests.
- **Line 7**: `@Mock` creates a fake `BookRepository`. It does not connect to any database.
- **Line 8**: `@InjectMocks` creates a real `BookService` and injects the mock repository into it.
- **Line 9**: `@BeforeEach` creates fresh test data before each test.
- **Line 10**: `when(bookRepository.save(any(Book.class)))` means "when someone calls `save` with any Book..."
- **Line 11**: `.thenReturn(sampleBook)` means "...then return this sample book."
- **Line 12**: Now when `bookService.createBook()` internally calls `bookRepository.save()`, it gets our mock response.
- **Line 13**: Assert the result is what we expect.
- **Line 14**: `verify(bookRepository, times(1)).save(any())` confirms that `save` was called exactly once.
- **Line 15**: `verify(bookRepository, never()).save(any())` confirms that `save` was never called (because validation failed).

```
How Mockito Works:

Step 1: Create mocks
+-------------+     +-----------+
| @Mock       |---->| Fake Repo |  (no real database)
| bookRepo    |     | (mockito) |
+-------------+     +-----------+

Step 2: Define behavior
when(mockRepo.save(any()))  -->  return sampleBook

Step 3: Test the service
+-------------+     +-----------+
| BookService |---->| Fake Repo |
| (real code) |     | returns   |
|             |     | sampleBook|
+-------------+     +-----------+

Step 4: Verify calls
verify(mockRepo).save(any())  -->  Was save() called? YES!
```

**Output:**

```
BookService Unit Tests
  should create a book successfully                       PASSED
  should throw exception for negative price               PASSED
  should return book when found by ID                     PASSED
  should throw exception when book not found              PASSED
  should return all books                                 PASSED
  should update book successfully                         PASSED
  should delete book successfully                         PASSED
  should throw exception when deleting non-existent book  PASSED

8 tests completed, 8 passed
```

---

## 26.5 Testing REST Controllers with @WebMvcTest

`@WebMvcTest` tests your controllers without starting the full Spring application. It only loads the web layer (controllers, filters, advice), making tests fast.

### The Book Controller

```java
// src/main/java/com/example/bookstore/controller/BookController.java

package com.example.bookstore.controller;

import com.example.bookstore.entity.Book;
import com.example.bookstore.service.BookService;
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

    @PostMapping
    public ResponseEntity<Book> createBook(@RequestBody Book book) {
        Book created = bookService.createBook(book);
        return ResponseEntity.status(HttpStatus.CREATED)
                             .body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Book> getBook(@PathVariable Long id) {
        Book book = bookService.getBookById(id);
        return ResponseEntity.ok(book);
    }

    @GetMapping
    public ResponseEntity<List<Book>> getAllBooks() {
        return ResponseEntity.ok(bookService.getAllBooks());
    }

    @PutMapping("/{id}")
    public ResponseEntity<Book> updateBook(
            @PathVariable Long id,
            @RequestBody Book book) {
        Book updated = bookService.updateBook(id, book);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteBook(@PathVariable Long id) {
        bookService.deleteBook(id);
        return ResponseEntity.noContent().build();
    }
}
```

### Writing Controller Tests

```java
// src/test/java/com/example/bookstore/controller/BookControllerTest.java

package com.example.bookstore.controller;

import com.example.bookstore.entity.Book;
import com.example.bookstore.service.BookService;
import com.fasterxml.jackson.databind.ObjectMapper;          // 1
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet
    .WebMvcTest;                                             // 2
import org.springframework.boot.test.mock.mockito.MockBean;  // 3
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;          // 4

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.*;                        // 5
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.doNothing;
import static org.springframework.test.web.servlet
    .request.MockMvcRequestBuilders.*;                       // 6
import static org.springframework.test.web.servlet
    .result.MockMvcResultMatchers.*;                         // 7

@WebMvcTest(BookController.class)                             // 8
@DisplayName("BookController Tests")
class BookControllerTest {

    @Autowired
    private MockMvc mockMvc;                                  // 9

    @MockBean                                                 // 10
    private BookService bookService;

    @Autowired
    private ObjectMapper objectMapper;                        // 11

    // ---- POST /api/books ----

    @Test
    @DisplayName("POST /api/books - should create book")
    void shouldCreateBook() throws Exception {

        // Arrange
        Book book = new Book("Spring Boot Guide",
                             "John Doe", 39.99);
        book.setId(1L);

        when(bookService.createBook(any(Book.class)))
            .thenReturn(book);

        // Act & Assert
        mockMvc.perform(                                      // 12
            post("/api/books")                                // 13
                .contentType(MediaType.APPLICATION_JSON)      // 14
                .content(objectMapper                         // 15
                    .writeValueAsString(book))
        )
        .andExpect(status().isCreated())                      // 16
        .andExpect(jsonPath("$.id").value(1))                 // 17
        .andExpect(jsonPath("$.title")                        // 18
            .value("Spring Boot Guide"))
        .andExpect(jsonPath("$.author")
            .value("John Doe"))
        .andExpect(jsonPath("$.price").value(39.99));
    }

    // ---- GET /api/books/{id} ----

    @Test
    @DisplayName("GET /api/books/1 - should return book")
    void shouldReturnBookById() throws Exception {

        Book book = new Book("Clean Code",
                             "Robert Martin", 44.99);
        book.setId(1L);

        when(bookService.getBookById(1L)).thenReturn(book);

        mockMvc.perform(
            get("/api/books/1")                               // 19
        )
        .andExpect(status().isOk())                           // 20
        .andExpect(jsonPath("$.title").value("Clean Code"))
        .andExpect(jsonPath("$.author")
            .value("Robert Martin"));
    }

    // ---- GET /api/books ----

    @Test
    @DisplayName("GET /api/books - should return all books")
    void shouldReturnAllBooks() throws Exception {

        Book book1 = new Book("Book 1", "Author 1", 29.99);
        book1.setId(1L);
        Book book2 = new Book("Book 2", "Author 2", 39.99);
        book2.setId(2L);
        List<Book> books = Arrays.asList(book1, book2);

        when(bookService.getAllBooks()).thenReturn(books);

        mockMvc.perform(
            get("/api/books")
        )
        .andExpect(status().isOk())
        .andExpect(jsonPath("$", hasSize(2)))                 // 21
        .andExpect(jsonPath("$[0].title")                     // 22
            .value("Book 1"))
        .andExpect(jsonPath("$[1].title")
            .value("Book 2"));
    }

    // ---- PUT /api/books/{id} ----

    @Test
    @DisplayName("PUT /api/books/1 - should update book")
    void shouldUpdateBook() throws Exception {

        Book updatedBook = new Book("Updated Title",
                                    "Updated Author", 59.99);
        updatedBook.setId(1L);

        when(bookService.updateBook(eq(1L), any(Book.class)))
            .thenReturn(updatedBook);

        mockMvc.perform(
            put("/api/books/1")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper
                    .writeValueAsString(updatedBook))
        )
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.title")
            .value("Updated Title"))
        .andExpect(jsonPath("$.price").value(59.99));
    }

    // ---- DELETE /api/books/{id} ----

    @Test
    @DisplayName("DELETE /api/books/1 - should delete book")
    void shouldDeleteBook() throws Exception {

        doNothing().when(bookService).deleteBook(1L);         // 23

        mockMvc.perform(
            delete("/api/books/1")                            // 24
        )
        .andExpect(status().isNoContent());                   // 25

        verify(bookService).deleteBook(1L);
    }
}
```

**Key lines explained:**

- **Line 2/8**: `@WebMvcTest(BookController.class)` starts only the web layer for `BookController`. No database, no services. Very fast.
- **Line 3/10**: `@MockBean` creates a mock `BookService` and adds it to the Spring context. The controller will use this mock instead of the real service.
- **Line 4/9**: `MockMvc` lets you send fake HTTP requests to your controller without starting a real server.
- **Line 11**: `ObjectMapper` converts Java objects to JSON strings.
- **Line 12**: `mockMvc.perform(...)` sends a fake HTTP request.
- **Line 13**: `post("/api/books")` creates a POST request to `/api/books`.
- **Line 14**: Set the content type to JSON.
- **Line 15**: Convert the book object to a JSON string for the request body.
- **Line 16**: `status().isCreated()` checks that the response status is 201 Created.
- **Line 17**: `jsonPath("$.id").value(1)` checks that the JSON response has `"id": 1`.
- **Line 18**: `jsonPath("$.title")` checks the title field in the JSON response.
- **Line 19**: `get("/api/books/1")` creates a GET request.
- **Line 20**: `status().isOk()` checks for 200 OK.
- **Line 21**: `hasSize(2)` verifies the JSON array has 2 elements.
- **Line 22**: `$[0].title` accesses the first element's title in the JSON array.
- **Line 23**: `doNothing()` is used for void methods. "When deleteBook is called, do nothing."
- **Line 24**: `delete("/api/books/1")` creates a DELETE request.
- **Line 25**: `status().isNoContent()` checks for 204 No Content.

```
How @WebMvcTest Works:

+----------+     +----------+     +----------+
|  Test    |     | MockMvc  |     | Book     |
|  Class   |---->| (fake    |---->| Controller|
|          |     | server)  |     | (real)   |
+----------+     +----------+     +----+-----+
                                       |
                                  +----+-----+
                                  | @MockBean |
                                  | BookService|
                                  | (fake)    |
                                  +-----------+

What is loaded:     Controllers, Filters, Exception Handlers
What is NOT loaded: Services, Repositories, Database
```

**Output:**

```
BookController Tests
  POST /api/books - should create book           PASSED
  GET /api/books/1 - should return book           PASSED
  GET /api/books - should return all books        PASSED
  PUT /api/books/1 - should update book           PASSED
  DELETE /api/books/1 - should delete book        PASSED

5 tests completed, 5 passed
```

---

## 26.6 Integration Testing with @SpringBootTest

`@SpringBootTest` loads the complete Spring application context. It starts everything: controllers, services, repositories, and the database. This tests that all the pieces work together.

```java
// src/test/java/com/example/bookstore/BookstoreIntegrationTest.java

package com.example.bookstore;

import com.example.bookstore.entity.Book;
import com.example.bookstore.repository.BookRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet
    .AutoConfigureMockMvc;                                   // 1
import org.springframework.boot.test.context
    .SpringBootTest;                                         // 2
import org.springframework.http.MediaType;
import org.springframework.test.context
    .ActiveProfiles;                                         // 3
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet
    .request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet
    .result.MockMvcResultMatchers.*;

@SpringBootTest                                              // 4
@AutoConfigureMockMvc                                        // 5
@ActiveProfiles("test")                                      // 6
@DisplayName("Bookstore Integration Tests")
class BookstoreIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private BookRepository bookRepository;                   // 7

    @Autowired
    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() {
        bookRepository.deleteAll();                          // 8
    }

    @Test
    @DisplayName("Full CRUD flow - create, read, update, delete")
    void shouldPerformFullCrudFlow() throws Exception {

        // Step 1: Create a book
        Book book = new Book("Test Book",
                             "Test Author", 29.99);

        String response = mockMvc.perform(
            post("/api/books")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper
                    .writeValueAsString(book))
        )
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.id").exists())                // 9
        .andExpect(jsonPath("$.title").value("Test Book"))
        .andReturn()                                         // 10
        .getResponse()
        .getContentAsString();

        // Extract the ID from the response
        Long bookId = objectMapper.readTree(response)        // 11
            .get("id").asLong();

        // Step 2: Read the book
        mockMvc.perform(get("/api/books/" + bookId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.title")
                .value("Test Book"));

        // Step 3: Update the book
        Book updated = new Book("Updated Book",
                                "New Author", 39.99);

        mockMvc.perform(
            put("/api/books/" + bookId)
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper
                    .writeValueAsString(updated))
        )
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.title")
            .value("Updated Book"))
        .andExpect(jsonPath("$.price").value(39.99));

        // Step 4: Verify the update persisted
        mockMvc.perform(get("/api/books/" + bookId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.title")
                .value("Updated Book"));

        // Step 5: Delete the book
        mockMvc.perform(delete("/api/books/" + bookId))
            .andExpect(status().isNoContent());

        // Step 6: Verify deletion
        mockMvc.perform(get("/api/books"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    @DisplayName("should return empty list when no books exist")
    void shouldReturnEmptyList() throws Exception {
        mockMvc.perform(get("/api/books"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    @DisplayName("should create multiple books and list them")
    void shouldCreateAndListMultipleBooks() throws Exception {

        // Create two books
        Book book1 = new Book("Book One", "Author A", 19.99);
        Book book2 = new Book("Book Two", "Author B", 29.99);

        mockMvc.perform(
            post("/api/books")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper
                    .writeValueAsString(book1))
        ).andExpect(status().isCreated());

        mockMvc.perform(
            post("/api/books")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper
                    .writeValueAsString(book2))
        ).andExpect(status().isCreated());

        // List all books
        mockMvc.perform(get("/api/books"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(2)))
            .andExpect(jsonPath("$[0].title")
                .value("Book One"))
            .andExpect(jsonPath("$[1].title")
                .value("Book Two"));
    }
}
```

**Key differences from @WebMvcTest:**

- **Line 2/4**: `@SpringBootTest` loads the entire application (all beans, database, etc.).
- **Line 1/5**: `@AutoConfigureMockMvc` provides MockMvc for sending HTTP requests.
- **Line 3/6**: `@ActiveProfiles("test")` activates the "test" profile, loading `application-test.properties`.
- **Line 7**: We can inject the real `BookRepository` (no `@MockBean`).
- **Line 8**: Clean the database before each test for isolation.
- **Line 9**: `jsonPath("$.id").exists()` checks that the database generated an ID.
- **Line 10**: `.andReturn()` captures the response so we can extract data from it.
- **Line 11**: Extract the generated ID to use in subsequent requests.

```
@WebMvcTest vs @SpringBootTest:

@WebMvcTest                          @SpringBootTest
+----------+                         +----------+
| Controller| (real)                 | Controller| (real)
+-----+----+                         +-----+----+
      |                                    |
+-----+----+                         +-----+----+
| Service  | (@MockBean = fake)      | Service  | (real)
+----------+                         +-----+----+
                                           |
                                     +-----+----+
                                     | Repository| (real)
                                     +-----+----+
                                           |
                                     +-----+----+
                                     | H2 DB   | (real)
                                     +----------+

Faster, isolated                     Slower, full integration
```

---

## 26.7 Testing Repositories with @DataJpaTest

`@DataJpaTest` tests only the database layer. It configures an in-memory H2 database, scans for `@Entity` classes, and configures Spring Data JPA repositories.

```java
// src/test/java/com/example/bookstore/repository/BookRepositoryTest.java

package com.example.bookstore.repository;

import com.example.bookstore.entity.Book;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa
    .DataJpaTest;                                            // 1

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest                                                  // 2
@DisplayName("BookRepository Tests")
class BookRepositoryTest {

    @Autowired
    private BookRepository bookRepository;                   // 3

    @BeforeEach
    void setUp() {
        bookRepository.deleteAll();
    }

    @Test
    @DisplayName("should save and find a book by ID")
    void shouldSaveAndFindBook() {
        // Arrange
        Book book = new Book("JPA in Action",
                             "John Doe", 34.99);

        // Act
        Book saved = bookRepository.save(book);              // 4
        Optional<Book> found =
            bookRepository.findById(saved.getId());          // 5

        // Assert
        assertTrue(found.isPresent());                       // 6
        assertEquals("JPA in Action",
                     found.get().getTitle());
    }

    @Test
    @DisplayName("should find books by author")
    void shouldFindBooksByAuthor() {
        // Arrange
        bookRepository.save(
            new Book("Book 1", "Craig Walls", 29.99));
        bookRepository.save(
            new Book("Book 2", "Craig Walls", 39.99));
        bookRepository.save(
            new Book("Book 3", "Other Author", 49.99));

        // Act
        List<Book> books =
            bookRepository.findByAuthor("Craig Walls");      // 7

        // Assert
        assertEquals(2, books.size());
        assertTrue(books.stream()
            .allMatch(b ->
                b.getAuthor().equals("Craig Walls")));
    }

    @Test
    @DisplayName("should return empty when book not found")
    void shouldReturnEmptyForNonExistentBook() {
        Optional<Book> result =
            bookRepository.findById(999L);

        assertTrue(result.isEmpty());
    }

    @Test
    @DisplayName("should delete a book")
    void shouldDeleteBook() {
        // Arrange
        Book book = bookRepository.save(
            new Book("To Delete", "Author", 19.99));

        // Act
        bookRepository.deleteById(book.getId());

        // Assert
        Optional<Book> result =
            bookRepository.findById(book.getId());
        assertTrue(result.isEmpty());
    }

    @Test
    @DisplayName("should count books")
    void shouldCountBooks() {
        bookRepository.save(
            new Book("Book 1", "Author 1", 10.0));
        bookRepository.save(
            new Book("Book 2", "Author 2", 20.0));

        long count = bookRepository.count();

        assertEquals(2, count);
    }
}
```

- **Line 1-2**: `@DataJpaTest` configures only the JPA layer: entities, repositories, and an H2 database. No controllers or services.
- **Line 3**: Inject the real repository. It connects to an in-memory H2 database.
- **Line 4**: `save()` inserts the book into the H2 database.
- **Line 5**: `findById()` queries the H2 database.
- **Line 6**: Assert the book was found.
- **Line 7**: Test the custom query method `findByAuthor()`.

```
What @DataJpaTest Loads:

+--------------------+
|   @DataJpaTest     |
|                    |
|  +------------+    |
|  | Entities   |    |    NOT loaded:
|  +------------+    |    - Controllers
|  | Repositories|   |    - Services
|  +------------+    |    - Security
|  | H2 Database|    |    - Web Layer
|  +------------+    |
+--------------------+
```

**Output:**

```
BookRepository Tests
  should save and find a book by ID           PASSED
  should find books by author                 PASSED
  should return empty when book not found     PASSED
  should delete a book                        PASSED
  should count books                          PASSED

5 tests completed, 5 passed
```

---

## 26.8 Using Test Properties

You often need different settings for tests. Maybe you want a different database, or you want to disable certain features.

### Option 1: application-test.properties

```properties
# src/test/resources/application-test.properties

spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=false

# Disable features that interfere with tests
spring.mail.host=localhost
spring.cache.type=none
```

Activate with:

```java
@SpringBootTest
@ActiveProfiles("test")
class MyTest { ... }
```

### Option 2: @TestPropertySource

```java
@SpringBootTest
@TestPropertySource(properties = {
    "spring.datasource.url=jdbc:h2:mem:customdb",
    "app.feature.email-enabled=false"
})
class MyTest { ... }
```

### Option 3: application.properties in test/resources

```properties
# src/test/resources/application.properties
# This automatically overrides main application.properties

spring.datasource.url=jdbc:h2:mem:testdb
```

### Priority Order

```
Highest Priority:
  1. @TestPropertySource (in the test class)
  2. src/test/resources/application-test.properties
  3. src/test/resources/application.properties
  4. src/main/resources/application.properties
Lowest Priority
```

---

## 26.9 Complete CRUD API Test Suite

Here is a complete, production-ready test suite that tests all CRUD operations with various scenarios:

```java
// src/test/java/com/example/bookstore/BookCrudApiTest.java

package com.example.bookstore;

import com.example.bookstore.entity.Book;
import com.example.bookstore.repository.BookRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet
    .AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet
    .request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet
    .result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@DisplayName("Book CRUD API Tests")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class BookCrudApiTest {

    @Autowired private MockMvc mockMvc;
    @Autowired private BookRepository bookRepository;
    @Autowired private ObjectMapper objectMapper;

    @BeforeEach
    void cleanDatabase() {
        bookRepository.deleteAll();
    }

    // ======= Helper Methods =======

    private Book createTestBook(String title,
                                String author,
                                double price) {
        return new Book(title, author, price);
    }

    private Long createBookAndReturnId(Book book)
            throws Exception {

        MvcResult result = mockMvc.perform(
            post("/api/books")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper
                    .writeValueAsString(book))
        )
        .andExpect(status().isCreated())
        .andReturn();

        return objectMapper
            .readTree(result.getResponse()
                .getContentAsString())
            .get("id").asLong();
    }

    // ======= CREATE Tests =======

    @Test
    @Order(1)
    @DisplayName("CREATE: should create a new book")
    void shouldCreateNewBook() throws Exception {
        Book book = createTestBook(
            "Effective Java", "Joshua Bloch", 45.99);

        mockMvc.perform(
            post("/api/books")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper
                    .writeValueAsString(book))
        )
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.id").isNumber())
        .andExpect(jsonPath("$.title")
            .value("Effective Java"))
        .andExpect(jsonPath("$.author")
            .value("Joshua Bloch"))
        .andExpect(jsonPath("$.price").value(45.99));

        // Verify it was saved to the database
        assertEquals(1, bookRepository.count());
    }

    @Test
    @Order(2)
    @DisplayName("CREATE: should persist book in database")
    void shouldPersistBookInDatabase() throws Exception {
        Book book = createTestBook(
            "Clean Code", "Robert Martin", 39.99);

        Long id = createBookAndReturnId(book);

        // Verify directly in the database
        Book saved = bookRepository.findById(id)
            .orElseThrow();
        assertEquals("Clean Code", saved.getTitle());
        assertEquals("Robert Martin", saved.getAuthor());
        assertEquals(39.99, saved.getPrice());
    }

    // ======= READ Tests =======

    @Test
    @Order(3)
    @DisplayName("READ: should return book by ID")
    void shouldReturnBookById() throws Exception {
        Book book = createTestBook(
            "Head First Java", "Kathy Sierra", 49.99);
        Long id = createBookAndReturnId(book);

        mockMvc.perform(get("/api/books/" + id))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(id))
            .andExpect(jsonPath("$.title")
                .value("Head First Java"));
    }

    @Test
    @Order(4)
    @DisplayName("READ: should return all books")
    void shouldReturnAllBooks() throws Exception {
        createBookAndReturnId(
            createTestBook("Book A", "Author A", 10.0));
        createBookAndReturnId(
            createTestBook("Book B", "Author B", 20.0));
        createBookAndReturnId(
            createTestBook("Book C", "Author C", 30.0));

        mockMvc.perform(get("/api/books"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(3)))
            .andExpect(jsonPath("$[*].title",
                containsInAnyOrder(
                    "Book A", "Book B", "Book C")));
    }

    @Test
    @Order(5)
    @DisplayName("READ: should return empty list when no books")
    void shouldReturnEmptyList() throws Exception {
        mockMvc.perform(get("/api/books"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$", hasSize(0)));
    }

    // ======= UPDATE Tests =======

    @Test
    @Order(6)
    @DisplayName("UPDATE: should update existing book")
    void shouldUpdateExistingBook() throws Exception {
        Long id = createBookAndReturnId(
            createTestBook("Old Title", "Old Author", 10.0));

        Book updated = createTestBook(
            "New Title", "New Author", 99.99);

        mockMvc.perform(
            put("/api/books/" + id)
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper
                    .writeValueAsString(updated))
        )
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.title").value("New Title"))
        .andExpect(jsonPath("$.author").value("New Author"))
        .andExpect(jsonPath("$.price").value(99.99));

        // Verify the update persisted
        Book fromDb = bookRepository.findById(id)
            .orElseThrow();
        assertEquals("New Title", fromDb.getTitle());
    }

    // ======= DELETE Tests =======

    @Test
    @Order(7)
    @DisplayName("DELETE: should delete existing book")
    void shouldDeleteExistingBook() throws Exception {
        Long id = createBookAndReturnId(
            createTestBook("To Delete", "Author", 10.0));

        // Verify book exists
        assertEquals(1, bookRepository.count());

        // Delete
        mockMvc.perform(delete("/api/books/" + id))
            .andExpect(status().isNoContent());

        // Verify book is gone
        assertEquals(0, bookRepository.count());
        assertTrue(bookRepository.findById(id).isEmpty());
    }

    @Test
    @Order(8)
    @DisplayName("DELETE: should not affect other books")
    void shouldNotAffectOtherBooks() throws Exception {
        Long id1 = createBookAndReturnId(
            createTestBook("Keep This", "Author", 10.0));
        Long id2 = createBookAndReturnId(
            createTestBook("Delete This", "Author", 20.0));

        assertEquals(2, bookRepository.count());

        mockMvc.perform(delete("/api/books/" + id2))
            .andExpect(status().isNoContent());

        assertEquals(1, bookRepository.count());
        assertTrue(bookRepository.findById(id1).isPresent());
        assertTrue(bookRepository.findById(id2).isEmpty());
    }
}
```

**Output:**

```
Book CRUD API Tests
  CREATE: should create a new book               PASSED
  CREATE: should persist book in database         PASSED
  READ: should return book by ID                  PASSED
  READ: should return all books                   PASSED
  READ: should return empty list when no books    PASSED
  UPDATE: should update existing book             PASSED
  DELETE: should delete existing book             PASSED
  DELETE: should not affect other books            PASSED

8 tests completed, 8 passed
```

---

## 26.10 Running Tests

### From the Command Line

```bash
# Run all tests
./mvnw test

# Run a specific test class
./mvnw test -Dtest=BookServiceTest

# Run a specific test method
./mvnw test -Dtest=BookServiceTest#shouldCreateBook

# Run tests with verbose output
./mvnw test -Dtest=BookControllerTest -Dsurefire.useFile=false
```

### Understanding Test Output

```
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.example.bookstore.service.BookServiceTest
[INFO] Tests run: 8, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.example.bookstore.controller.BookControllerTest
[INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running com.example.bookstore.repository.BookRepositoryTest
[INFO] Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
[INFO]
[INFO] Results:
[INFO]
[INFO] Tests run: 18, Failures: 0, Errors: 0, Skipped: 0
[INFO]
[INFO] BUILD SUCCESS
```

---

## Common Mistakes

### Mistake 1: Not Cleaning the Database Between Tests

```java
// WRONG: Tests affect each other
@Test
void testCreateBook() {
    bookRepository.save(new Book("A", "B", 10.0));
    // If this runs first, the next test sees this book
}

@Test
void testEmptyList() {
    // FAILS because previous test left data!
    assertEquals(0, bookRepository.count());
}
```

```java
// CORRECT: Clean before each test
@BeforeEach
void setUp() {
    bookRepository.deleteAll();
}
```

### Mistake 2: Using @MockBean When You Need Real Beans

```java
// WRONG: @MockBean replaces the real service
// Your test never actually tests the real service logic
@SpringBootTest
class IntegrationTest {
    @MockBean  // This defeats the purpose of integration testing!
    private BookService bookService;
}
```

```java
// CORRECT: Use real beans in integration tests
@SpringBootTest
class IntegrationTest {
    @Autowired  // Use the real service
    private BookService bookService;
}
```

### Mistake 3: Testing Framework Code Instead of Your Code

```java
// WRONG: Testing that Spring Data JPA's save() works
// Spring already tests this. You do not need to.
@Test
void testSave() {
    Book book = new Book("A", "B", 10.0);
    Book saved = bookRepository.save(book);
    assertNotNull(saved.getId());  // This just tests JPA
}
```

```java
// CORRECT: Test YOUR custom logic
@Test
void shouldRejectNegativePrice() {
    Book book = new Book("A", "B", -10.0);
    assertThrows(IllegalArgumentException.class,
        () -> bookService.createBook(book));
}
```

### Mistake 4: Using @SpringBootTest for Unit Tests

```java
// WRONG: Loads the entire application just to test one method
@SpringBootTest
class BookServiceTest {
    @Autowired
    private BookService bookService;
    // Slow! Takes seconds to start the entire application.
}
```

```java
// CORRECT: Use Mockito for unit tests (much faster)
@ExtendWith(MockitoExtension.class)
class BookServiceTest {
    @Mock
    private BookRepository bookRepository;
    @InjectMocks
    private BookService bookService;
    // Fast! No Spring context needed.
}
```

### Mistake 5: Not Testing Error Scenarios

```java
// WRONG: Only testing the happy path
@Test
void testGetBook() {
    // Only tests when the book exists
    when(repo.findById(1L)).thenReturn(Optional.of(book));
    Book result = service.getBookById(1L);
    assertNotNull(result);
}
```

```java
// CORRECT: Test both success AND failure paths
@Test
void shouldReturnBookWhenFound() { ... }

@Test
void shouldThrowWhenBookNotFound() {
    when(repo.findById(99L)).thenReturn(Optional.empty());
    assertThrows(RuntimeException.class,
        () -> service.getBookById(99L));
}
```

---

## Best Practices

1. **Follow the test pyramid.** Write many unit tests, some integration tests, and few end-to-end tests.

2. **Use descriptive test names.** A test name should explain what is being tested and the expected outcome. Use `@DisplayName` for readability.

3. **Follow the AAA pattern.** Every test should have three sections: Arrange (set up), Act (execute), Assert (verify).

4. **Keep tests independent.** Each test should be able to run alone. Clean the database between tests with `@BeforeEach`.

5. **Use `@WebMvcTest` for controller tests.** It is faster than `@SpringBootTest` because it only loads the web layer.

6. **Use `@DataJpaTest` for repository tests.** It only loads the JPA layer and is much faster than a full integration test.

7. **Test error scenarios.** Do not just test the happy path. Test what happens when things go wrong (invalid input, missing data, timeouts).

8. **Use `@MockBean` only in slice tests.** In integration tests (`@SpringBootTest`), use real beans to verify the full flow.

---

## Quick Summary

In this chapter, you learned how to test Spring Boot applications from top to bottom. You started with the test pyramid, which guides you on how many of each type of test to write. You learned JUnit 5 basics: `@Test`, assertions, and lifecycle annotations. You used Mockito to mock dependencies in unit tests, isolating the class under test. You tested controllers with `@WebMvcTest` and `MockMvc`, sending fake HTTP requests without a real server. You wrote integration tests with `@SpringBootTest` that exercise the full application. You tested repositories with `@DataJpaTest` and an in-memory H2 database. Finally, you built a complete CRUD test suite that covers all operations and edge cases.

---

## Key Points

| Concept | Description |
|---|---|
| Test Pyramid | Strategy: many unit tests, some integration, few E2E |
| JUnit 5 `@Test` | Marks a method as a test |
| `assertEquals()` | Checks that expected and actual values match |
| `assertThrows()` | Checks that a specific exception is thrown |
| `@BeforeEach` | Runs before each test (setup) |
| Mockito `@Mock` | Creates a fake object that pretends to be a dependency |
| `@InjectMocks` | Creates a real object and injects mocks into it |
| `when().thenReturn()` | Defines what a mock should return when called |
| `verify()` | Checks that a mock method was called |
| `@WebMvcTest` | Tests only the web layer (controller tests) |
| `MockMvc` | Sends fake HTTP requests to controllers |
| `@MockBean` | Replaces a real bean with a mock in the Spring context |
| `@SpringBootTest` | Loads the full application for integration tests |
| `@DataJpaTest` | Tests only the JPA/database layer |
| `@ActiveProfiles` | Activates a specific configuration profile for tests |
| `jsonPath()` | Asserts values in JSON responses |

---

## Practice Questions

1. What is the test pyramid and why does it recommend more unit tests than integration tests?

2. What is the difference between `@Mock` and `@MockBean`? When would you use each one?

3. Explain the difference between `@WebMvcTest` and `@SpringBootTest`. When is each appropriate?

4. What does the `when().thenReturn()` pattern do in Mockito? Write an example.

5. Why should you clean the database before each test in integration tests? What problems occur if you do not?

---

## Exercises

### Exercise 1: Test a Calculator Service

Create a `CalculatorService` with methods for `add`, `subtract`, `multiply`, and `divide`. Write unit tests for all four operations, including a test that verifies `divide` throws an `ArithmeticException` when dividing by zero.

### Exercise 2: Test an Employee API

Create an `Employee` entity with fields `id`, `name`, `department`, and `salary`. Build a complete REST API (controller, service, repository) and write:
- Unit tests for the service layer using Mockito.
- Controller tests using `@WebMvcTest`.
- Repository tests using `@DataJpaTest`.
- An integration test that covers the full CRUD flow.

### Exercise 3: Test Edge Cases

Add the following edge case tests to the Book CRUD test suite:
- Test creating a book with a very long title (255 characters).
- Test creating a book with an empty title (should fail validation).
- Test updating a book that does not exist (should return 404).
- Test deleting a book that does not exist (should return 404).

---

## What Is Next?

You now know how to test your Spring Boot applications thoroughly. But how do your API consumers know what endpoints are available and how to use them? In the next chapter, we will learn about **API Documentation** with Swagger and OpenAPI. You will create interactive, auto-generated documentation that lets anyone explore and test your API directly from a browser.
