# Chapter 11: Input Validation

## What You Will Learn

In this chapter, you will learn:

- Why input validation matters and what happens without it
- How to add the `spring-boot-starter-validation` dependency
- How to use `@Valid` to trigger validation
- The most common validation annotations: `@NotNull`, `@NotBlank`, `@Size`, `@Email`, `@Pattern`, `@Min`, `@Max`
- How to create your own custom validator
- How to validate nested objects
- How to build a complete user registration example with validation

## Why This Chapter Matters

Imagine you work at a bank. A customer walks in and hands you a deposit slip. The slip says the amount is "negative five million dollars." Do you process it? Of course not. You check the slip first. The amount must be a positive number. The account number must exist. The signature must match.

Your API is like that bank teller. Clients send data to your endpoints. Some of that data will be wrong -- accidentally or intentionally. Without validation, bad data enters your system and causes bugs, crashes, or security problems.

Validation is your first line of defense. It catches bad data at the door, before it reaches your business logic or database. This chapter teaches you how to build that defense.

---

## 11.1 Adding the Validation Dependency

Spring Boot validation is not included by default. You need to add a dependency to your `pom.xml`.

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

**Dependency** means a library that your project needs. Maven downloads it automatically when you add it to `pom.xml`.

This starter brings in **Jakarta Bean Validation** (formerly Java Bean Validation) and **Hibernate Validator** (the implementation). Do not confuse Hibernate Validator with Hibernate ORM. They share a name but serve different purposes.

- **Hibernate ORM** talks to databases.
- **Hibernate Validator** validates Java objects.

After adding the dependency, rebuild your project:

```bash
mvn clean compile
```

---

## 11.2 Your First Validation with @Valid

Let us start with a simple example. We have a `BookCreateRequest` DTO that we want to validate.

### Step 1: Add Validation Annotations to the DTO

```java
package com.example.demo.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;

public class BookCreateRequest {

    @NotBlank(message = "Title is required")
    @Size(min = 1, max = 200, message = "Title must be between 1 and 200 characters")
    private String title;

    @NotBlank(message = "Author is required")
    private String author;

    @NotNull(message = "Price is required")
    @Positive(message = "Price must be greater than zero")
    private Double price;

    @NotBlank(message = "ISBN is required")
    private String isbn;

    // Getters and setters
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public Double getPrice() { return price; }
    public void setPrice(Double price) { this.price = price; }

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }
}
```

**Line-by-line explanation:**

- `@NotBlank(message = "Title is required")` -- The title must not be null, must not be empty, and must not be just whitespace. The `message` is what the user sees when validation fails.
- `@Size(min = 1, max = 200, ...)` -- The title must be between 1 and 200 characters long.
- `@NotNull(message = "Price is required")` -- The price must not be null. We use `Double` (the wrapper class) instead of `double` (the primitive) so it can be null. A primitive `double` is always 0.0, never null.
- `@Positive(message = "Price must be greater than zero")` -- The price must be a positive number (greater than 0).

### Step 2: Add @Valid to the Controller

```java
package com.example.demo.controller;

import com.example.demo.dto.BookCreateRequest;
import com.example.demo.dto.BookResponse;
import com.example.demo.service.BookService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }
}
```

The key change is `@Valid` before `@RequestBody`. This one annotation activates all the validation rules on `BookCreateRequest`.

**@Valid** tells Spring: "Before calling this method, check all the validation annotations on this object. If any validation fails, do not call the method. Throw an exception instead."

### What Happens When Validation Fails?

```bash
# Send a request with missing fields
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "", "price": -5}'
```

**Default Spring Boot error response:**

```json
{
    "timestamp": "2024-01-15T10:30:00.000+00:00",
    "status": 400,
    "error": "Bad Request",
    "path": "/api/books"
}
```

Spring returns a 400 Bad Request status. The default error message is not very helpful for the client. We will fix this in Chapter 12 (Exception Handling).

### The Validation Flow

```
Client sends POST request with JSON body
         |
         v
+---------------------------+
| Spring reads JSON and     |
| creates BookCreateRequest |
+---------------------------+
         |
         v
+---------------------------+
| @Valid triggers validation |
| Check @NotBlank on title  | --> FAIL: title is empty
| Check @NotNull on price   | --> PASS
| Check @Positive on price  | --> FAIL: price is -5
| Check @NotBlank on author | --> FAIL: author is null
| Check @NotBlank on isbn   | --> FAIL: isbn is null
+---------------------------+
         |
         | 4 violations found!
         v
+---------------------------+
| Spring throws              |
| MethodArgumentNot          |
| ValidException             |
| Returns 400 Bad Request    |
+---------------------------+
         |
         | Controller method is NEVER called
         v
```

---

## 11.3 Common Validation Annotations

Here is a complete reference of the most useful validation annotations.

### String Validations

| Annotation    | What It Checks                           | Example                    |
|---------------|------------------------------------------|----------------------------|
| `@NotNull`    | Not null (but can be empty "")           | `@NotNull String name`     |
| `@NotEmpty`   | Not null AND not empty ""                | `@NotEmpty String name`    |
| `@NotBlank`   | Not null, not empty, not just spaces     | `@NotBlank String name`    |
| `@Size`       | Length within range                      | `@Size(min=2, max=50)`     |
| `@Email`      | Valid email format                       | `@Email String email`      |
| `@Pattern`    | Matches a regular expression             | `@Pattern(regexp="[A-Z]+")` |

### The Difference Between @NotNull, @NotEmpty, and @NotBlank

```
Value          | @NotNull | @NotEmpty | @NotBlank
───────────────|──────────|───────────|──────────
null           |  FAIL    |   FAIL    |   FAIL
""             |  PASS    |   FAIL    |   FAIL
"   "          |  PASS    |   PASS    |   FAIL
"hello"        |  PASS    |   PASS    |   PASS
```

**Use `@NotBlank` for most string fields.** It is the strictest and catches all forms of "empty" input.

### Number Validations

| Annotation      | What It Checks                | Example                      |
|-----------------|-------------------------------|------------------------------|
| `@Min`          | Minimum value (inclusive)     | `@Min(0) int age`            |
| `@Max`          | Maximum value (inclusive)     | `@Max(150) int age`          |
| `@Positive`     | Greater than 0               | `@Positive double price`     |
| `@PositiveOrZero` | Greater than or equal to 0 | `@PositiveOrZero int stock`  |
| `@Negative`     | Less than 0                  | `@Negative double discount`  |
| `@Digits`       | Specific integer/fraction digits | `@Digits(integer=5, fraction=2)` |
| `@DecimalMin`   | Minimum decimal value        | `@DecimalMin("0.01")`        |

### Date Validations

| Annotation    | What It Checks                | Example                      |
|---------------|-------------------------------|------------------------------|
| `@Past`       | Date is in the past          | `@Past LocalDate birthDate`  |
| `@PastOrPresent` | Date is today or earlier  | `@PastOrPresent LocalDate`   |
| `@Future`     | Date is in the future        | `@Future LocalDate deadline` |
| `@FutureOrPresent` | Date is today or later  | `@FutureOrPresent LocalDate` |

### Boolean and Other

| Annotation     | What It Checks              | Example                       |
|----------------|-----------------------------|-------------------------------|
| `@AssertTrue`  | Must be true               | `@AssertTrue boolean agreed`  |
| `@AssertFalse` | Must be false              | `@AssertFalse boolean expired` |

---

## 11.4 Practical Example: @Email and @Pattern

### Validating Email Addresses

```java
@NotBlank(message = "Email is required")
@Email(message = "Email must be a valid email address")
private String email;
```

Valid: `user@example.com`, `alice.bob@company.co.uk`
Invalid: `not-an-email`, `@missing.com`, `user@`

### Validating with Regular Expressions

`@Pattern` lets you define custom validation rules using **regular expressions** (regex).

**Regular expression** is a pattern that describes what a string should look like. For example, `[0-9]{3}-[0-9]{4}` means "three digits, a dash, then four digits" (like a phone number: 555-1234).

```java
@NotBlank(message = "Phone number is required")
@Pattern(
    regexp = "^\\d{3}-\\d{3}-\\d{4}$",
    message = "Phone must be in format XXX-XXX-XXXX"
)
private String phone;
```

Common patterns:

```java
// Only letters and spaces
@Pattern(regexp = "^[a-zA-Z ]+$",
         message = "Name must contain only letters and spaces")
private String name;

// Alphanumeric username, 3-20 characters
@Pattern(regexp = "^[a-zA-Z0-9]{3,20}$",
         message = "Username must be 3-20 alphanumeric characters")
private String username;

// Strong password: at least 8 chars, one upper, one lower, one digit
@Pattern(
    regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).{8,}$",
    message = "Password must be 8+ chars with uppercase, lowercase, and digit"
)
private String password;

// ISBN-13 format
@Pattern(regexp = "^978-\\d{10}$",
         message = "ISBN must be in format 978-XXXXXXXXXX")
private String isbn;
```

---

## 11.5 A Complete Validation Example

Let us build a fully validated DTO that shows many annotations working together.

```java
package com.example.demo.dto;

import jakarta.validation.constraints.*;

public class BookCreateRequest {

    @NotBlank(message = "Title is required")
    @Size(min = 1, max = 200,
          message = "Title must be between 1 and 200 characters")
    private String title;

    @NotBlank(message = "Author is required")
    @Size(min = 2, max = 100,
          message = "Author name must be between 2 and 100 characters")
    private String author;

    @NotNull(message = "Price is required")
    @DecimalMin(value = "0.01",
                message = "Price must be at least $0.01")
    @DecimalMax(value = "9999.99",
                message = "Price cannot exceed $9,999.99")
    private Double price;

    @NotBlank(message = "ISBN is required")
    @Pattern(regexp = "^978-\\d{10}$",
             message = "ISBN must be in format 978-XXXXXXXXXX")
    private String isbn;

    @Size(max = 2000,
          message = "Description cannot exceed 2000 characters")
    private String description;

    @Min(value = 1, message = "Page count must be at least 1")
    @Max(value = 10000, message = "Page count cannot exceed 10,000")
    private Integer pageCount;

    // Getters and setters
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public Double getPrice() { return price; }
    public void setPrice(Double price) { this.price = price; }

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }

    public String getDescription() { return description; }
    public void setDescription(String description) {
        this.description = description;
    }

    public Integer getPageCount() { return pageCount; }
    public void setPageCount(Integer pageCount) {
        this.pageCount = pageCount;
    }
}
```

### Testing Validation

```bash
# Valid request
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Spring Boot in Action",
    "author": "Craig Walls",
    "price": 39.99,
    "isbn": "978-1617292545",
    "description": "A great book about Spring Boot",
    "pageCount": 350
  }'

# Response: 201 Created
```

```bash
# Invalid request (multiple errors)
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "",
    "author": "A",
    "price": -5.00,
    "isbn": "invalid",
    "pageCount": -1
  }'

# Response: 400 Bad Request
```

---

## 11.6 Custom Validators

Sometimes the built-in annotations are not enough. You need custom validation logic. For example, "the end date must be after the start date" or "this field must be unique."

### Step 1: Create the Annotation

```java
package com.example.demo.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Documented
@Constraint(validatedBy = NoOffensiveWordsValidator.class)
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
public @interface NoOffensiveWords {

    String message() default "Field contains offensive language";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};
}
```

**Line-by-line explanation:**

- `@Constraint(validatedBy = NoOffensiveWordsValidator.class)` -- Links this annotation to the class that contains the validation logic.
- `@Target({ElementType.FIELD})` -- This annotation can only be placed on fields.
- `@Retention(RetentionPolicy.RUNTIME)` -- The annotation is available at runtime (so Spring can read it).
- `String message() default "..."` -- The default error message. Users can override it.
- `groups()` and `payload()` -- Required by the Bean Validation spec. You can leave them with default values.

### Step 2: Create the Validator Class

```java
package com.example.demo.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.List;

public class NoOffensiveWordsValidator
        implements ConstraintValidator<NoOffensiveWords, String> {

    private static final List<String> BLOCKED_WORDS =
            List.of("spam", "scam", "fake");

    @Override
    public boolean isValid(String value,
                           ConstraintValidatorContext context) {
        if (value == null) {
            return true;  // Let @NotNull handle null checks
        }

        String lowerValue = value.toLowerCase();
        for (String word : BLOCKED_WORDS) {
            if (lowerValue.contains(word)) {
                return false;
            }
        }
        return true;
    }
}
```

**Line-by-line explanation:**

- `implements ConstraintValidator<NoOffensiveWords, String>` -- This validator is linked to the `@NoOffensiveWords` annotation and validates `String` values.
- `isValid(...)` -- The method that performs the validation. Return `true` if valid, `false` if invalid.
- `if (value == null) return true` -- Important convention: a custom validator should not check for null. Let `@NotNull` or `@NotBlank` handle null. This allows optional fields to skip this check when they are null.

### Step 3: Use the Custom Annotation

```java
public class BookCreateRequest {

    @NotBlank(message = "Title is required")
    @NoOffensiveWords(message = "Title contains inappropriate language")
    private String title;

    @NotBlank(message = "Author is required")
    @NoOffensiveWords
    private String author;

    // ... other fields
}
```

```bash
# Test with offensive word
curl -X POST http://localhost:8080/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "This is spam content", "author": "Bob", "price": 9.99, "isbn": "978-1234567890"}'

# Response: 400 Bad Request
# Error: "Title contains inappropriate language"
```

---

## 11.7 Validating Nested Objects

When your DTO contains another object, you need to validate the nested object too. Use `@Valid` on the nested field.

### Example: Order with Shipping Address

```java
package com.example.demo.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

public class OrderCreateRequest {

    @NotBlank(message = "Customer name is required")
    private String customerName;

    @NotBlank(message = "Customer email is required")
    @Email(message = "Email must be valid")
    private String customerEmail;

    @NotNull(message = "Shipping address is required")
    @Valid  // This tells Spring to validate the Address object too
    private Address shippingAddress;

    // Getters and setters
    public String getCustomerName() { return customerName; }
    public void setCustomerName(String customerName) {
        this.customerName = customerName;
    }

    public String getCustomerEmail() { return customerEmail; }
    public void setCustomerEmail(String customerEmail) {
        this.customerEmail = customerEmail;
    }

    public Address getShippingAddress() { return shippingAddress; }
    public void setShippingAddress(Address shippingAddress) {
        this.shippingAddress = shippingAddress;
    }
}
```

```java
package com.example.demo.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public class Address {

    @NotBlank(message = "Street is required")
    @Size(max = 200, message = "Street cannot exceed 200 characters")
    private String street;

    @NotBlank(message = "City is required")
    private String city;

    @NotBlank(message = "State is required")
    @Size(min = 2, max = 2, message = "State must be 2 characters")
    private String state;

    @NotBlank(message = "ZIP code is required")
    @Pattern(regexp = "^\\d{5}(-\\d{4})?$",
             message = "ZIP code must be in format XXXXX or XXXXX-XXXX")
    private String zipCode;

    // Getters and setters
    public String getStreet() { return street; }
    public void setStreet(String street) { this.street = street; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public String getState() { return state; }
    public void setState(String state) { this.state = state; }

    public String getZipCode() { return zipCode; }
    public void setZipCode(String zipCode) {
        this.zipCode = zipCode;
    }
}
```

**The key annotation is `@Valid` on the `shippingAddress` field.** Without it, Spring creates the `Address` object but does not validate its fields. The address could have empty streets, invalid ZIP codes, and Spring would not catch it.

```
Without @Valid on shippingAddress:
──────────────────────────────────
customerName  --> validated (must not be blank)
customerEmail --> validated (must be valid email)
shippingAddress --> only checked for null (@NotNull)
    street     --> NOT validated!
    city       --> NOT validated!
    zipCode    --> NOT validated!

With @Valid on shippingAddress:
──────────────────────────────
customerName  --> validated
customerEmail --> validated
shippingAddress --> checked for null AND all fields validated
    street     --> validated (must not be blank)
    city       --> validated (must not be blank)
    zipCode    --> validated (must match pattern)
```

### Testing Nested Validation

```bash
# Invalid nested object
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customerName": "Alice Johnson",
    "customerEmail": "alice@example.com",
    "shippingAddress": {
      "street": "",
      "city": "",
      "state": "California",
      "zipCode": "abc"
    }
  }'

# Response: 400 Bad Request
# Errors:
# - "Street is required"
# - "City is required"
# - "State must be 2 characters"
# - "ZIP code must be in format XXXXX or XXXXX-XXXX"
```

---

## 11.8 Complete Example: User Registration

Let us build a complete user registration system with thorough validation.

### The Registration Request DTO

```java
package com.example.demo.dto;

import jakarta.validation.constraints.*;

public class UserRegistrationRequest {

    @NotBlank(message = "Username is required")
    @Size(min = 3, max = 20,
          message = "Username must be between 3 and 20 characters")
    @Pattern(regexp = "^[a-zA-Z0-9_]+$",
             message = "Username can only contain letters, numbers, and underscores")
    private String username;

    @NotBlank(message = "Email is required")
    @Email(message = "Please provide a valid email address")
    private String email;

    @NotBlank(message = "Password is required")
    @Size(min = 8, max = 100,
          message = "Password must be between 8 and 100 characters")
    @Pattern(
        regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).+$",
        message = "Password must contain at least one uppercase letter, "
                + "one lowercase letter, and one digit"
    )
    private String password;

    @NotBlank(message = "First name is required")
    @Size(min = 1, max = 50,
          message = "First name cannot exceed 50 characters")
    private String firstName;

    @NotBlank(message = "Last name is required")
    @Size(min = 1, max = 50,
          message = "Last name cannot exceed 50 characters")
    private String lastName;

    @Min(value = 13,
         message = "You must be at least 13 years old to register")
    @Max(value = 150,
         message = "Please enter a valid age")
    private Integer age;

    @Pattern(regexp = "^\\d{3}-\\d{3}-\\d{4}$",
             message = "Phone must be in format XXX-XXX-XXXX")
    private String phone;  // Optional -- no @NotBlank

    // Getters and setters
    public String getUsername() { return username; }
    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getPassword() { return password; }
    public void setPassword(String password) {
        this.password = password;
    }

    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() { return lastName; }
    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
}
```

### The User Response DTO

```java
package com.example.demo.dto;

import java.time.LocalDateTime;

public class UserResponse {

    private Long id;
    private String username;
    private String email;
    private String firstName;
    private String lastName;
    private Integer age;
    private String phone;
    private LocalDateTime registeredAt;

    public UserResponse() {}

    public UserResponse(Long id, String username, String email,
                        String firstName, String lastName,
                        Integer age, String phone,
                        LocalDateTime registeredAt) {
        this.id = id;
        this.username = username;
        this.email = email;
        this.firstName = firstName;
        this.lastName = lastName;
        this.age = age;
        this.phone = phone;
        this.registeredAt = registeredAt;
    }

    // Getters only (no password!)
    public Long getId() { return id; }
    public String getUsername() { return username; }
    public String getEmail() { return email; }
    public String getFirstName() { return firstName; }
    public String getLastName() { return lastName; }
    public Integer getAge() { return age; }
    public String getPhone() { return phone; }
    public LocalDateTime getRegisteredAt() { return registeredAt; }
}
```

Notice the response DTO does **not** include the password. Never return passwords in API responses.

### The Controller

```java
package com.example.demo.controller;

import com.example.demo.dto.UserRegistrationRequest;
import com.example.demo.dto.UserResponse;
import com.example.demo.service.UserService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/register")
    public ResponseEntity<UserResponse> register(
            @Valid @RequestBody UserRegistrationRequest request) {
        UserResponse user = userService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }
}
```

### The Service

```java
package com.example.demo.service;

import com.example.demo.dto.UserRegistrationRequest;
import com.example.demo.dto.UserResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class UserService {

    private static final Logger log =
            LoggerFactory.getLogger(UserService.class);

    private final AtomicLong nextId = new AtomicLong(1);

    public UserResponse register(UserRegistrationRequest request) {
        // At this point, all validation has already passed
        Long id = nextId.getAndIncrement();

        log.info("Registering user: {} ({})",
                request.getUsername(), request.getEmail());

        return new UserResponse(
                id,
                request.getUsername(),
                request.getEmail(),
                request.getFirstName(),
                request.getLastName(),
                request.getAge(),
                request.getPhone(),
                LocalDateTime.now()
        );
    }
}
```

### Testing the Registration

```bash
# Valid registration
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_dev",
    "email": "alice@example.com",
    "password": "SecurePass1",
    "firstName": "Alice",
    "lastName": "Johnson",
    "age": 28,
    "phone": "555-123-4567"
  }'
```

**Output:**

```json
{
    "id": 1,
    "username": "alice_dev",
    "email": "alice@example.com",
    "firstName": "Alice",
    "lastName": "Johnson",
    "age": 28,
    "phone": "555-123-4567",
    "registeredAt": "2024-01-15T10:30:00"
}
```

```bash
# Invalid registration (multiple errors)
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "a",
    "email": "not-an-email",
    "password": "weak",
    "firstName": "",
    "lastName": "",
    "age": 10,
    "phone": "12345"
  }'
```

This request fails with a 400 status and multiple validation errors.

---

## 11.9 Validation on Update Endpoints

Do not forget to validate update requests too.

```java
@PutMapping("/{id}")
public ResponseEntity<UserResponse> updateUser(
        @PathVariable Long id,
        @Valid @RequestBody UserUpdateRequest request) {
    return userService.updateUser(id, request)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
}
```

The update DTO may have different validation rules than the create DTO. For example, you might not require the password on update:

```java
public class UserUpdateRequest {

    @NotBlank(message = "First name is required")
    private String firstName;

    @NotBlank(message = "Last name is required")
    private String lastName;

    @Email(message = "Please provide a valid email address")
    private String email;

    // Password is optional on update
    @Size(min = 8, message = "Password must be at least 8 characters")
    private String password;

    // Getters and setters...
}
```

---

## Common Mistakes

### Mistake 1: Forgetting @Valid

```java
// WRONG: No @Valid -- validation annotations are IGNORED
@PostMapping
public ResponseEntity<UserResponse> register(
        @RequestBody UserRegistrationRequest request) {
    // No validation happens! All bad data gets through!
}
```

```java
// CORRECT: Add @Valid to activate validation
@PostMapping
public ResponseEntity<UserResponse> register(
        @Valid @RequestBody UserRegistrationRequest request) {
    // Validation runs before this method is called
}
```

This is the most common mistake. Without `@Valid`, the annotations on your DTO are decorations. They do nothing.

### Mistake 2: Using Primitive Types for Optional Fields

```java
// WRONG: Primitive double is never null, defaults to 0.0
@NotNull
private double price;  // @NotNull never fails on primitives

// CORRECT: Use wrapper type Double
@NotNull(message = "Price is required")
@Positive(message = "Price must be positive")
private Double price;  // Can be null, so @NotNull works
```

### Mistake 3: Not Validating Nested Objects

```java
// WRONG: Missing @Valid on nested object
@NotNull
private Address address;  // Address fields are NOT validated

// CORRECT: Add @Valid
@NotNull
@Valid
private Address address;  // Address fields ARE validated
```

### Mistake 4: Missing the Validation Dependency

If you see this error:

```
jakarta.validation.constraints.NotBlank cannot be resolved
```

You forgot to add the dependency:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

### Mistake 5: Putting Business Validation in Annotations

```java
// WRONG: This is business logic, not data validation
@UniqueEmail  // Custom annotation that checks the database
private String email;
```

Annotations should validate the **format** of data (not blank, valid email, correct length). Business rules like "email must be unique" belong in the service layer, not in annotations.

---

## Best Practices

1. **Always use `@Valid` on controller method parameters.** It is easy to forget and hard to catch.

2. **Use `@NotBlank` for strings, not `@NotNull`.** `@NotBlank` catches null, empty, and whitespace-only strings.

3. **Use wrapper types (`Double`, `Integer`) instead of primitives (`double`, `int`)** when the field can be null. Primitives cannot be null, so `@NotNull` never fails on them.

4. **Write clear, user-friendly error messages.** "Price is required" is better than "must not be null."

5. **Keep validation annotations on DTOs, not on entities.** DTOs are the API boundary. Entities are the database boundary. They may have different rules.

6. **Validate at the API boundary.** By the time data reaches your service, it should already be validated. Services should not need to check for null or empty strings.

7. **Use separate DTOs for create and update.** Create may require fields that update does not (like password).

8. **Let `@NotNull` handle null checks in custom validators.** Your custom validator's `isValid()` method should return `true` for null values.

---

## Quick Summary

- Add `spring-boot-starter-validation` to your `pom.xml` to enable validation.
- `@Valid` on a method parameter activates validation. Without it, annotations do nothing.
- `@NotBlank` validates strings (not null, not empty, not whitespace). `@NotNull` only checks for null.
- `@Size` validates length. `@Min`/`@Max` validate numeric ranges. `@Email` validates email format.
- `@Pattern` validates against a regular expression for custom formats.
- Custom validators need two parts: an annotation and a validator class.
- Use `@Valid` on nested object fields to validate their contents.
- Use wrapper types (`Double`, `Integer`) instead of primitives when fields can be null.

---

## Key Points

- Validation is your first line of defense against bad data.
- Always add `@Valid` to your controller parameters -- it is the trigger.
- Use `@NotBlank` for strings, wrapper types for numbers.
- Keep error messages clear and user-friendly.
- Validate at the API boundary (DTOs), not deep in your business logic.
- Nested objects need `@Valid` on the field to be validated.

---

## Practice Questions

1. What is the difference between `@NotNull`, `@NotEmpty`, and `@NotBlank`? Which should you use for a user's name field?

2. Why should you use `Double` instead of `double` for a price field that has `@NotNull`?

3. You have an `Order` DTO with a `List<OrderItem> items` field. Each `OrderItem` has validation annotations. What do you need to add to the `items` field to make the validation work?

4. Explain the two parts needed to create a custom validator. What does each part do?

5. What happens if you put validation annotations on a DTO but forget `@Valid` on the controller parameter?

---

## Exercises

### Exercise 1: Contact Form Validation

Create a contact form API endpoint `POST /api/contact` with a DTO that validates:

- `name` -- required, 2-100 characters
- `email` -- required, valid email
- `subject` -- required, 5-200 characters
- `message` -- required, 10-5000 characters
- `phone` -- optional, but if provided must match format XXX-XXX-XXXX
- `urgency` -- optional, must be one of: "low", "medium", "high" (use @Pattern)

### Exercise 2: Product with Nested Category

Create a `POST /api/products` endpoint with:

- `ProductCreateRequest` with fields: `name` (required, 2-100 chars), `price` (required, positive), `description` (optional, max 1000 chars)
- Nested `Category` object with fields: `name` (required), `code` (required, exactly 3 uppercase letters)
- Make sure the nested Category is validated

### Exercise 3: Custom Date Range Validator

Create a custom `@ValidDateRange` annotation that validates an object has `startDate` before `endDate`. Apply it to a class-level annotation on an `EventCreateRequest` DTO with `name`, `startDate`, and `endDate` fields.

Hint: Use `@Target(ElementType.TYPE)` for class-level validation and implement `ConstraintValidator<ValidDateRange, EventCreateRequest>`.

---

## What Is Next?

You now know how to validate input data. But what happens when validation fails? Or when a requested resource does not exist? Or when an unexpected error occurs? The default Spring Boot error responses are ugly and inconsistent. In the next chapter, you will learn **exception handling** -- how to return clean, consistent, and helpful error responses from your API.
