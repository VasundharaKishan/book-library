# Chapter 22: Bean Validation with Hibernate Validator

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the Jakarta Bean Validation specification and its role
- Use built-in constraint annotations (@NotNull, @Size, @Email, @Min, @Max, etc.)
- Distinguish between @NotNull, @NotEmpty, and @NotBlank
- Apply validation to JPA entities for database-level enforcement
- Create custom constraint annotations with validators
- Use validation groups for context-dependent validation
- Integrate validation with Spring MVC (@Valid in controllers)
- Handle and format validation error responses
- Understand the relationship between Bean Validation and JPA constraints

---

## What Is Bean Validation?

**Jakarta Bean Validation** (formerly javax.validation) is a Java specification for declarative data validation. You annotate fields with constraints, and the framework validates them automatically.

**Hibernate Validator** is the reference implementation — just as Hibernate ORM implements JPA, Hibernate Validator implements Bean Validation. Spring Boot includes it automatically with `spring-boot-starter-web` or `spring-boot-starter-validation`.

```
Bean Validation in the Stack:
+------------------------------------------------------------------+
|                                                                   |
|  Your Entity / DTO                                                |
|  @NotBlank String name;                                           |
|  @Email String email;                                             |
|  @Min(0) BigDecimal price;                                        |
|       |                                                           |
|       v                                                           |
|  Jakarta Bean Validation API (Specification)                      |
|  jakarta.validation.constraints.*                                 |
|       |                                                           |
|       v                                                           |
|  Hibernate Validator (Implementation)                             |
|  Reads annotations, runs validation logic                         |
|       |                                                           |
|       v                                                           |
|  Validation Result                                                |
|  Set<ConstraintViolation> violations                              |
|  (empty = valid, non-empty = invalid with error messages)         |
+------------------------------------------------------------------+
```

---

## Built-In Constraint Annotations

### Null and Blank Checks

```java
@Entity
@Table(name = "users")
public class User {

    @NotNull        // Field cannot be null (allows empty string "")
    private String username;

    @NotEmpty       // Field cannot be null AND cannot be empty ("")
    private String firstName;     // Rejects: null, ""
                                  // Accepts: " ", "Alice"

    @NotBlank       // Cannot be null, empty, or only whitespace
    private String lastName;      // Rejects: null, "", "   "
                                  // Accepts: "Smith", " Smith "
}
```

```
@NotNull vs @NotEmpty vs @NotBlank:
+------------------------------------------------------------------+
|                                                                   |
|  Value          @NotNull     @NotEmpty    @NotBlank               |
|  ----------------------------------------------------------------|
|  null            FAIL         FAIL         FAIL                   |
|  ""              PASS         FAIL         FAIL                   |
|  "   "           PASS         PASS         FAIL                   |
|  "Alice"         PASS         PASS         PASS                   |
|                                                                   |
|  Use @NotNull for: non-String fields (Long, BigDecimal, etc.)    |
|  Use @NotBlank for: String fields where you need real content    |
|  Use @NotEmpty for: String or Collection fields (not just blank) |
+------------------------------------------------------------------+
```

### String Constraints

```java
@Size(min = 2, max = 100)               // String length between 2 and 100
private String name;

@Size(max = 500)                         // Max 500 characters
private String description;

@Email                                   // Must be a valid email format
private String email;

@Pattern(regexp = "^[A-Z]{2}-\\d{4}$")  // Must match regex pattern
private String productCode;              // e.g., "AB-1234"

@Pattern(regexp = "^\\+?[1-9]\\d{1,14}$", message = "Invalid phone number")
private String phone;
```

### Number Constraints

```java
@Min(0)                                  // Must be >= 0
private BigDecimal price;

@Max(150)                                // Must be <= 150
private int age;

@Positive                                // Must be > 0
private BigDecimal salary;

@PositiveOrZero                          // Must be >= 0
private int quantity;

@Negative                                // Must be < 0
private BigDecimal discount;             // Stored as negative value

@DecimalMin(value = "0.01")              // Must be >= 0.01
private BigDecimal minimumOrderAmount;

@DecimalMax(value = "999999.99")         // Must be <= 999999.99
private BigDecimal maximumPrice;

@Digits(integer = 6, fraction = 2)      // Max 6 integer, 2 decimal digits
private BigDecimal amount;               // e.g., 123456.78
```

### Date and Time Constraints

```java
@Past                                    // Must be in the past
private LocalDate birthDate;

@PastOrPresent                           // Must be in the past or today
private LocalDate hireDate;

@Future                                  // Must be in the future
private LocalDate expirationDate;

@FutureOrPresent                         // Must be today or later
private LocalDateTime appointmentTime;
```

### Collection Constraints

```java
@NotEmpty                                // Collection must not be null or empty
@Size(min = 1, max = 10)                 // Must have 1-10 elements
private List<String> tags;
```

```
Complete Built-In Constraints Reference:
+------------------------------------------------------------------+
|                                                                   |
|  Annotation        Applies To        Validates                    |
|  ----------------------------------------------------------------|
|  @NotNull           Any              Not null                     |
|  @NotEmpty          String/Coll      Not null, not empty          |
|  @NotBlank          String           Not null, not blank          |
|  @Null              Any              Must be null                 |
|  @Size              String/Coll      Length/size in range          |
|  @Min               Number           >= value                     |
|  @Max               Number           <= value                     |
|  @Positive          Number           > 0                          |
|  @PositiveOrZero    Number           >= 0                         |
|  @Negative          Number           < 0                          |
|  @NegativeOrZero    Number           <= 0                         |
|  @DecimalMin        Number           >= value (as string)         |
|  @DecimalMax        Number           <= value (as string)         |
|  @Digits            Number           Integer + fraction digits    |
|  @Email             String           Valid email format            |
|  @Pattern           String           Matches regex                |
|  @Past              Date/Time        In the past                  |
|  @PastOrPresent     Date/Time        Past or now                  |
|  @Future            Date/Time        In the future                |
|  @FutureOrPresent   Date/Time        Now or future                |
|  @AssertTrue        Boolean          Must be true                 |
|  @AssertFalse       Boolean          Must be false                |
+------------------------------------------------------------------+
```

---

## Validated Entity Example

```java
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
    @Column(nullable = false, length = 100)
    private String name;

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be a valid email address")
    @Column(nullable = false, unique = true)
    private String email;

    @NotNull(message = "Salary is required")
    @Positive(message = "Salary must be positive")
    @Digits(integer = 8, fraction = 2, message = "Salary must have at most 8 integer and 2 decimal digits")
    @Column(nullable = false)
    private BigDecimal salary;

    @PastOrPresent(message = "Hire date cannot be in the future")
    @Column(name = "hire_date")
    private LocalDate hireDate;

    @Size(max = 500, message = "Bio must be at most 500 characters")
    private String bio;

    protected Employee() {}

    public Employee(String name, String email, BigDecimal salary) {
        this.name = name;
        this.email = email;
        this.salary = salary;
        this.hireDate = LocalDate.now();
    }

    // Getters and setters...
}
```

```
Bean Validation vs JPA Constraints:
+------------------------------------------------------------------+
|                                                                   |
|  Bean Validation (@NotBlank, @Size, @Email):                      |
|  - Validates in JAVA before SQL is executed                       |
|  - Runs when entity is persisted or controller receives input     |
|  - Provides user-friendly error messages                          |
|  - Can validate DTOs (not just entities)                          |
|                                                                   |
|  JPA Constraints (@Column(nullable, length, unique)):             |
|  - Creates DATABASE constraints (NOT NULL, VARCHAR(100), UNIQUE)  |
|  - Enforced by the database itself                                |
|  - Last line of defense — catches issues Bean Validation missed   |
|  - Error messages are database-level (not user-friendly)          |
|                                                                   |
|  Best practice: Use BOTH.                                         |
|  @NotBlank + @Column(nullable = false)                            |
|  @Size(max = 100) + @Column(length = 100)                        |
|  Bean Validation catches errors early with good messages.         |
|  JPA constraints provide database-level data integrity.           |
+------------------------------------------------------------------+
```

---

## Validation in Spring MVC Controllers

### Validating Request Bodies

```java
// Request DTO (not an entity — separate class for API input)
public class CreateEmployeeRequest {

    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100)
    private String name;

    @NotBlank(message = "Email is required")
    @Email(message = "Must be a valid email")
    private String email;

    @NotNull(message = "Salary is required")
    @Positive(message = "Salary must be positive")
    private BigDecimal salary;

    // Getters and setters...
}
```

```java
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    private final EmployeeService employeeService;

    @PostMapping
    public ResponseEntity<Employee> createEmployee(
            @Valid @RequestBody CreateEmployeeRequest request) {
        //  ^^^^^^ @Valid triggers validation!
        // If validation fails, Spring throws MethodArgumentNotValidException
        // BEFORE your code runs.

        Employee employee = employeeService.create(
            request.getName(),
            request.getEmail(),
            request.getSalary()
        );
        return ResponseEntity.status(HttpStatus.CREATED).body(employee);
    }
}
```

```
@Valid Request Flow:
+------------------------------------------------------------------+
|                                                                   |
|  POST /api/employees                                              |
|  { "name": "", "email": "not-an-email", "salary": -5 }           |
|       |                                                           |
|       v                                                           |
|  Spring deserializes JSON --> CreateEmployeeRequest               |
|       |                                                           |
|       v                                                           |
|  @Valid triggers Bean Validation                                  |
|       |                                                           |
|  Violations found:                                                |
|  - name: "Name is required" (blank)                               |
|  - email: "Must be a valid email"                                 |
|  - salary: "Salary must be positive" (-5)                        |
|       |                                                           |
|       v                                                           |
|  MethodArgumentNotValidException thrown                           |
|  Controller method is NEVER called                                |
|       |                                                           |
|       v                                                           |
|  @ControllerAdvice handles it --> 400 Bad Request with errors    |
+------------------------------------------------------------------+
```

### Global Error Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationErrors(
            MethodArgumentNotValidException ex) {

        Map<String, String> fieldErrors = new LinkedHashMap<>();
        for (FieldError error : ex.getBindingResult().getFieldErrors()) {
            fieldErrors.put(error.getField(), error.getDefaultMessage());
        }

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("status", 400);
        response.put("error", "Validation Failed");
        response.put("fieldErrors", fieldErrors);

        return ResponseEntity.badRequest().body(response);
    }
}
```

```
Error Response Example:
+------------------------------------------------------------------+
|                                                                   |
|  {                                                                |
|    "status": 400,                                                 |
|    "error": "Validation Failed",                                  |
|    "fieldErrors": {                                               |
|      "name": "Name is required",                                  |
|      "email": "Must be a valid email",                            |
|      "salary": "Salary must be positive"                          |
|    }                                                              |
|  }                                                                |
+------------------------------------------------------------------+
```

---

## Custom Constraint Annotations

When built-in constraints are not enough, create your own:

### Example: @ValidPhoneNumber

```java
// Step 1: Define the annotation
@Documented
@Constraint(validatedBy = PhoneNumberValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidPhoneNumber {
    String message() default "Invalid phone number format";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

```java
// Step 2: Implement the validator
public class PhoneNumberValidator
        implements ConstraintValidator<ValidPhoneNumber, String> {

    private static final Pattern PHONE_PATTERN =
        Pattern.compile("^\\+?[1-9]\\d{6,14}$");

    @Override
    public void initialize(ValidPhoneNumber annotation) {
        // Optional initialization
    }

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null) {
            return true;  // Use @NotNull separately for null check
        }
        return PHONE_PATTERN.matcher(value).matches();
    }
}
```

```java
// Step 3: Use it
public class ContactRequest {

    @NotBlank
    private String name;

    @ValidPhoneNumber    // Custom constraint!
    private String phone;
}
```

### Example: @UniqueEmail (Database-Aware Validation)

```java
@Documented
@Constraint(validatedBy = UniqueEmailValidator.class)
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface UniqueEmail {
    String message() default "Email is already registered";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

```java
@Component  // Must be a Spring bean to inject repositories
public class UniqueEmailValidator
        implements ConstraintValidator<UniqueEmail, String> {

    private final UserRepository userRepository;

    public UniqueEmailValidator(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public boolean isValid(String email, ConstraintValidatorContext context) {
        if (email == null) return true;
        return !userRepository.existsByEmail(email);
    }
}
```

```java
public class RegisterRequest {
    @NotBlank
    @Email
    @UniqueEmail   // Checks database for duplicates!
    private String email;
}
```

---

## Validation Groups

Groups let you apply different validation rules in different contexts:

```java
// Define group marker interfaces
public interface OnCreate {}
public interface OnUpdate {}
```

```java
public class ProductRequest {

    @Null(groups = OnCreate.class, message = "ID must not be provided for creation")
    @NotNull(groups = OnUpdate.class, message = "ID is required for update")
    private Long id;

    @NotBlank(groups = {OnCreate.class, OnUpdate.class})
    @Size(min = 2, max = 100)
    private String name;

    @NotNull(groups = OnCreate.class, message = "Price is required")
    @Positive
    private BigDecimal price;
}
```

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    @PostMapping
    public ResponseEntity<Product> create(
            @Validated(OnCreate.class) @RequestBody ProductRequest request) {
        //  ^^^^^^^^^^^^^^^^^^^^^^^^^ Use @Validated (not @Valid) for groups
        // Validates: id must be null, name required, price required
    }

    @PutMapping("/{id}")
    public ResponseEntity<Product> update(
            @PathVariable Long id,
            @Validated(OnUpdate.class) @RequestBody ProductRequest request) {
        // Validates: id must not be null, name required
        // Price NOT validated (not in OnUpdate group)
    }
}
```

```
Validation Groups:
+------------------------------------------------------------------+
|                                                                   |
|  Without groups: Same rules for create and update                 |
|  Problem: Create requires price, update may not                   |
|           Create has no ID, update requires ID                    |
|                                                                   |
|  With groups:                                                     |
|  OnCreate: id=@Null, name=@NotBlank, price=@NotNull              |
|  OnUpdate: id=@NotNull, name=@NotBlank                           |
|                                                                   |
|  Note: Use @Validated (Spring) not @Valid (Jakarta)               |
|  @Valid does not support groups parameter.                        |
+------------------------------------------------------------------+
```

---

## Cascading Validation with @Valid

Validate nested objects by adding `@Valid` to the field:

```java
public class OrderRequest {

    @NotBlank
    private String customerName;

    @NotEmpty(message = "Order must have at least one item")
    @Valid    // Cascade validation to each OrderItemRequest
    private List<OrderItemRequest> items;
}

public class OrderItemRequest {

    @NotBlank(message = "Product name is required")
    private String productName;

    @NotNull
    @Positive(message = "Quantity must be positive")
    private Integer quantity;

    @NotNull
    @Positive(message = "Price must be positive")
    private BigDecimal price;
}
```

```
Cascading @Valid:
+------------------------------------------------------------------+
|                                                                   |
|  Without @Valid on the list:                                      |
|  - OrderRequest is validated (customerName, items not empty)      |
|  - OrderItemRequest fields are NOT validated                      |
|  - Invalid items slip through!                                    |
|                                                                   |
|  With @Valid on the list:                                         |
|  - OrderRequest is validated                                      |
|  - EACH OrderItemRequest in the list is also validated            |
|  - If item[2].quantity is -1, validation fails with:              |
|    field: "items[2].quantity"                                     |
|    message: "Quantity must be positive"                            |
+------------------------------------------------------------------+
```

---

## Programmatic Validation

Validate entities manually in service methods:

```java
@Service
public class EmployeeService {

    private final Validator validator;   // jakarta.validation.Validator

    public EmployeeService(Validator validator) {
        this.validator = validator;
    }

    public void validateEmployee(Employee employee) {
        Set<ConstraintViolation<Employee>> violations = validator.validate(employee);

        if (!violations.isEmpty()) {
            StringBuilder sb = new StringBuilder("Validation failed:\n");
            for (ConstraintViolation<Employee> v : violations) {
                sb.append("  ")
                   .append(v.getPropertyPath())
                   .append(": ")
                   .append(v.getMessage())
                   .append("\n");
            }
            throw new IllegalArgumentException(sb.toString());
        }
    }

    // Validate with specific group
    public void validateForCreate(ProductRequest request) {
        Set<ConstraintViolation<ProductRequest>> violations =
            validator.validate(request, OnCreate.class);
        // Handle violations...
    }
}
```

---

## Custom Error Messages

### Inline Messages

```java
@NotBlank(message = "First name is required")
private String firstName;

@Size(min = 8, max = 64, message = "Password must be between {min} and {max} characters")
private String password;  // {min} and {max} are interpolated from the annotation

@Min(value = 18, message = "Must be at least {value} years old")
private int age;
```

### Messages from Properties File

```java
@NotBlank(message = "{employee.name.required}")
private String name;

@Email(message = "{employee.email.invalid}")
private String email;
```

```properties
# src/main/resources/ValidationMessages.properties
employee.name.required=Employee name is required
employee.email.invalid=Please provide a valid email address
employee.salary.positive=Salary must be a positive amount

# With interpolation
password.size=Password must be between {min} and {max} characters
```

---

## Common Mistakes

1. **Using @NotNull on String fields instead of @NotBlank**: `@NotNull` allows empty strings `""`. For strings where you need actual content, use `@NotBlank`.

2. **Using @Valid instead of @Validated for groups**: `@Valid` (Jakarta) does not support validation groups. Use `@Validated` (Spring) when you need group-specific validation.

3. **Returning null from custom validators for null input**: Custom validators should return `true` for null values and let `@NotNull` handle null checks separately. This follows the Jakarta Bean Validation convention.

4. **Not validating nested objects**: Adding `@NotEmpty` to a `List<OrderItem>` validates the list is not empty but does NOT validate each item's fields. Add `@Valid` to cascade validation.

5. **Putting validation only on entities, not on DTOs**: Validate request DTOs at the controller level. Entity-level validation is a safety net, not the primary validation point.

6. **Not handling MethodArgumentNotValidException**: Without a `@ControllerAdvice` handler, Spring returns a generic 400 error. Add a handler that returns structured field errors.

---

## Best Practices

1. **Validate at the boundary**: Validate incoming data in controllers (DTOs with `@Valid`) and as a safety net on entities. Do not rely solely on database constraints.

2. **Use @NotBlank for strings, @NotNull for everything else**: This covers the most common validation needs correctly.

3. **Keep validation messages user-friendly**: Use `message` attributes or message properties files. "Name is required" is better than "must not be blank."

4. **Use separate DTOs for create and update**: With different validation groups or completely separate DTO classes instead of reusing the same class.

5. **Return structured error responses**: Include field names, messages, and HTTP 400 status. Frontend developers need to map errors to form fields.

6. **Use @Valid on nested objects and collections**: Always cascade validation into complex request structures.

---

## Summary

- **Jakarta Bean Validation** is a specification for declarative data validation. **Hibernate Validator** is the implementation (included in Spring Boot).

- **Built-in constraints**: `@NotNull`, `@NotBlank`, `@Size`, `@Email`, `@Min`, `@Max`, `@Positive`, `@Past`, `@Future`, `@Pattern`, and more.

- **@NotBlank** is preferred for String fields (rejects null, empty, and whitespace). `@NotNull` is for non-String fields.

- **@Valid** in controllers triggers automatic validation before the method executes. Validation failures throw `MethodArgumentNotValidException`.

- **Custom constraints** are created with an annotation + a `ConstraintValidator` implementation. The validator can be a Spring bean for database-aware validation.

- **Validation groups** (`OnCreate`, `OnUpdate`) apply different rules in different contexts. Use `@Validated` (not `@Valid`) for group support.

- **Cascading @Valid** on nested objects and collections ensures deeply nested data is validated.

- Use **both** Bean Validation (Java-level, user-friendly messages) and JPA constraints (database-level, data integrity).

---

## Interview Questions

**Q1: What is the difference between @NotNull, @NotEmpty, and @NotBlank?**

`@NotNull` only checks that the value is not null (allows empty string `""`). `@NotEmpty` checks not null AND not empty (rejects `null` and `""`but allows `"   "`). `@NotBlank` checks not null, not empty, AND not whitespace-only (rejects `null`, `""`, and `"   "`).

**Q2: How does @Valid work in a Spring controller?**

When `@Valid` is placed on a `@RequestBody` parameter, Spring deserializes the request body, then runs Bean Validation on the resulting object before the controller method executes. If validation fails, `MethodArgumentNotValidException` is thrown and the method is never called.

**Q3: How do you create a custom validation annotation?**

Create an annotation with `@Constraint(validatedBy = MyValidator.class)` and the required attributes (`message`, `groups`, `payload`). Then create a class implementing `ConstraintValidator<MyAnnotation, FieldType>` with an `isValid()` method. Return `true` for valid, `false` for invalid.

**Q4: What are validation groups and when should you use them?**

Groups are marker interfaces that let you apply different validation rules in different contexts. For example, `@Null(groups = OnCreate.class)` on an ID field ensures no ID is sent during creation, while `@NotNull(groups = OnUpdate.class)` ensures an ID is provided during updates. Use `@Validated(OnCreate.class)` in the controller.

**Q5: Should you validate on entities, DTOs, or both?**

Both. Validate on DTOs at the controller layer for user-friendly error messages and early rejection. Validate on entities as a safety net to ensure data integrity regardless of how the entity is created. The DTO validation is the primary line of defense; entity validation is the secondary.

---

## Practice Exercises

**Exercise 1: Validated Entity**
Create a `Product` entity with: `@NotBlank` name, `@Positive` price, `@Size(max=500)` description, `@PastOrPresent` createdAt. Write a test that persists invalid data and verifies `ConstraintViolationException` is thrown.

**Exercise 2: Controller Validation**
Create a `POST /api/products` endpoint with a `CreateProductRequest` DTO. Add `@Valid`. Write a `@ControllerAdvice` that returns structured field errors. Test with invalid input and verify the error response format.

**Exercise 3: Custom Constraint**
Create a `@StrongPassword` annotation that requires: at least 8 characters, one uppercase, one lowercase, one digit, one special character. Write the validator and test with various passwords.

**Exercise 4: Validation Groups**
Create a `UserRequest` with `OnCreate` and `OnUpdate` groups. On create: password is required, email must be unique. On update: password is optional, ID is required. Implement both endpoints and test.

**Exercise 5: Cascading Validation**
Create an `OrderRequest` with a `List<@Valid OrderItemRequest>`. Validate that: order has at least one item, each item has a positive quantity and price. Test with a request where item[2] has invalid data and verify the error path includes the index.

---

## What Is Next?

In the next chapter, we enter **Part V: Production Patterns** and start with **DTOs, Projections, and Data Transfer**. You will learn why exposing JPA entities directly in APIs is dangerous, how to create proper DTOs, use MapStruct for automated mapping, and leverage JPA projections for efficient data retrieval.
