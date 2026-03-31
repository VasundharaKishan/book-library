# Chapter 26: API Design Principles

## What You Will Learn

- The Principle of Least Surprise: design APIs that behave as users expect
- Consistent naming conventions that make APIs intuitive
- Backward compatibility strategies that protect existing users
- API versioning approaches and their trade-offs
- How to design clear, helpful error responses
- Pagination patterns for large data sets
- Idempotency: making APIs safe to retry
- A practical API review checklist

## Why This Chapter Matters

An API is a contract. Whether it is a REST endpoint, a library interface, or a class's public methods, an API is a promise you make to other developers: "Call me this way, and I will do this for you."

A well-designed API is a joy to use. You read the method name, and you know what it does. You pass the obvious parameters, and it works. Error messages tell you exactly what went wrong and how to fix it. You can call it twice by accident, and nothing bad happens.

A poorly-designed API is a nightmare. You guess what the parameters mean. You discover undocumented side effects. Error messages say "Error 500" and nothing else. Calling an endpoint twice creates duplicate records that haunt you forever.

The difference between these two is not talent -- it is a set of principles that anyone can learn and apply. This chapter teaches those principles.

---

## The Principle of Least Surprise

The most important rule in API design: **an API should behave the way its users expect it to behave.** If someone reads the name of your method or endpoint and forms an expectation about what it does, the actual behavior should match that expectation.

```
PRINCIPLE OF LEAST SURPRISE:

  When a developer reads your API signature,
  their first guess about what it does should be correct.

  +-----------------------------+---------------------------+
  | SURPRISING (bad)            | UNSURPRISING (good)       |
  +-----------------------------+---------------------------+
  | user.save()                 | user.save()               |
  |   --> also sends email      |   --> only saves           |
  |   --> also logs analytics   |                           |
  |   --> also clears cache     | email_service.send(user)  |
  |                             |   --> only sends email     |
  +-----------------------------+---------------------------+
  | list.sort()                 | list.sort()               |
  |   --> returns new list      |   --> sorts in place       |
  |   --> original unchanged    |                           |
  |                             | sorted(list)              |
  |                             |   --> returns new list     |
  +-----------------------------+---------------------------+
  | cart.getTotal()             | cart.getTotal()            |
  |   --> applies discount      |   --> returns current total|
  |   --> modifies cart state   |                           |
  |                             | cart.applyDiscount(code)  |
  |                             |   --> modifies cart state  |
  +-----------------------------+---------------------------+
```

### Rules for Least Surprise

1. **Methods named `get` should not modify state.** Getters should be read-only.
2. **Methods named `save` should only save.** Do not add side effects.
3. **Boolean parameters should not change behavior drastically.** Instead, use separate methods.
4. **Error behavior should be consistent.** If one method throws on invalid input, all methods should.

### Java -- Before and After

```java
// SURPRISING: save() does three hidden things
public class UserRepository {
    public void save(User user) {
        database.insert(user);
        emailService.sendWelcome(user);     // Surprise!
        analyticsService.trackSignup(user); // Surprise!
    }
}

// UNSURPRISING: each method does one thing
public class UserRepository {
    public void save(User user) {
        database.insert(user);  // Just saves. Nothing else.
    }
}

public class UserRegistrationService {
    public void register(User user) {
        userRepository.save(user);           // Save
        emailService.sendWelcome(user);      // Explicit: send email
        analyticsService.trackSignup(user);  // Explicit: track
    }
}
```

```python
# SURPRISING: save() does three hidden things
class UserRepository:
    def save(self, user):
        self.database.insert(user)
        self.email_service.send_welcome(user)       # Surprise!
        self.analytics_service.track_signup(user)    # Surprise!

# UNSURPRISING: each method does one thing
class UserRepository:
    def save(self, user):
        self.database.insert(user)  # Just saves. Nothing else.

class UserRegistrationService:
    def register(self, user):
        self.user_repository.save(user)              # Save
        self.email_service.send_welcome(user)         # Explicit
        self.analytics_service.track_signup(user)     # Explicit
```

---

## Consistent Naming

Consistency makes APIs predictable. If you call it `getUser` in one place, do not call it `fetchCustomer` in another. Pick a convention and stick to it.

### Naming Conventions for REST APIs

```
REST API NAMING CONVENTIONS:

  Resource naming:
  +---------------------------+---------------------------+
  | BAD                       | GOOD                      |
  +---------------------------+---------------------------+
  | /getUsers                 | GET /users                |
  | /createUser               | POST /users               |
  | /deleteUser/123           | DELETE /users/123          |
  | /user_list                | GET /users                |
  | /Users                    | GET /users  (lowercase)   |
  +---------------------------+---------------------------+

  Use nouns for resources, HTTP verbs for actions:
  +---------------------------+---------------------------+
  | Action                    | Endpoint                  |
  +---------------------------+---------------------------+
  | List all orders           | GET    /orders            |
  | Get one order             | GET    /orders/{id}       |
  | Create an order           | POST   /orders            |
  | Update an order           | PUT    /orders/{id}       |
  | Partially update          | PATCH  /orders/{id}       |
  | Delete an order           | DELETE /orders/{id}       |
  +---------------------------+---------------------------+

  Sub-resources:
  +---------------------------+---------------------------+
  | Action                    | Endpoint                  |
  +---------------------------+---------------------------+
  | List items in order       | GET /orders/{id}/items    |
  | Add item to order         | POST /orders/{id}/items   |
  +---------------------------+---------------------------+

  Filtering, sorting, pagination via query parameters:
  GET /orders?status=pending&sort=created_at&page=2
```

### Naming Conventions for Code APIs

```java
// CONSISTENT NAMING in Java
// Pick a verb convention and stick to it

// For queries (read-only):
User findById(String id);          // Returns User or throws
Optional<User> findByEmail(String email);  // Returns Optional
List<User> findAllByRole(Role role);       // Returns list
boolean existsById(String id);             // Returns boolean

// For commands (write):
void save(User user);               // Persist
void delete(User user);             // Remove
void update(User user);             // Modify existing

// Do NOT mix:
//   getUser(), fetchUser(), loadUser(), retrieveUser()
// Pick ONE verb and use it everywhere.
```

```python
# CONSISTENT NAMING in Python
# Pick a convention and stick to it

class UserRepository:
    def find_by_id(self, user_id: str) -> User: ...
    def find_by_email(self, email: str) -> Optional[User]: ...
    def find_all_by_role(self, role: str) -> list[User]: ...
    def exists_by_id(self, user_id: str) -> bool: ...

    def save(self, user: User) -> None: ...
    def delete(self, user: User) -> None: ...
    def update(self, user: User) -> None: ...

    # Do NOT mix: get_user(), fetch_user(), load_user()
    # Pick ONE verb and use it everywhere.
```

---

## Backward Compatibility

Once you publish an API, people depend on it. Changing it in ways that break existing users is one of the most expensive mistakes you can make.

```
BACKWARD COMPATIBILITY RULES:

  SAFE CHANGES (backward compatible):
  +------------------------------------------+
  | - Adding a new optional field to response|
  | - Adding a new endpoint                  |
  | - Adding a new optional query parameter  |
  | - Adding a new HTTP method to a resource |
  | - Widening an input type (int -> long)   |
  +------------------------------------------+

  BREAKING CHANGES (not backward compatible):
  +------------------------------------------+
  | - Removing a field from response         |
  | - Renaming a field                       |
  | - Changing a field's type                |
  | - Removing an endpoint                   |
  | - Adding a required field to request     |
  | - Changing error codes or formats        |
  | - Narrowing an input type (long -> int)  |
  +------------------------------------------+
```

### Strategies for Evolving APIs Without Breaking Them

```java
// STRATEGY 1: Add optional fields, never remove required ones
// Version 1 response:
{
    "id": "123",
    "name": "Jane Smith",
    "email": "jane@example.com"
}

// Version 1.1 response (backward compatible):
{
    "id": "123",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1-555-0123"      // NEW optional field -- old clients ignore it
}


// STRATEGY 2: Use @JsonIgnoreProperties to handle unknown fields
@JsonIgnoreProperties(ignoreUnknown = true)
public class UserResponse {
    private String id;
    private String name;
    private String email;
    // Old clients will not break if new fields are added
}
```

```python
# STRATEGY: Accept unknown fields gracefully
from dataclasses import dataclass, field
from typing import Any

@dataclass
class UserResponse:
    id: str
    name: str
    email: str
    # New fields have defaults so old code still works
    phone: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "UserResponse":
        known_fields = {"id", "name", "email", "phone"}
        extra = {k: v for k, v in data.items() if k not in known_fields}
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            extra=extra,
        )
```

---

## API Versioning

When breaking changes are unavoidable, use versioning to protect existing users.

```
API VERSIONING STRATEGIES:

  1. URL PATH VERSIONING (most common):
     GET /api/v1/users
     GET /api/v2/users

     Pros: Simple, visible, easy to route
     Cons: URL changes for every version

  2. HEADER VERSIONING:
     GET /api/users
     Accept: application/vnd.myapp.v2+json

     Pros: Clean URLs
     Cons: Hidden, harder to test in browser

  3. QUERY PARAMETER VERSIONING:
     GET /api/users?version=2

     Pros: Easy to add
     Cons: Optional params can be forgotten

  RECOMMENDATION: Use URL path versioning.
  It is the most transparent and widely understood.

  +------------------------------------------+
  |  VERSIONING TIMELINE:                    |
  |                                          |
  |  v1 launched -----> v2 launched          |
  |  |                  |                    |
  |  |  v1 supported   |  v1 deprecated     |
  |  |  v2 available   |  v2 supported      |
  |  |                  |                    |
  |  |                  |  v1 sunset date    |
  |  |                  |  announced         |
  |  |                  |                    |
  |  |                  |  v1 removed        |
  +------------------------------------------+
```

### Java Example: Supporting Multiple Versions

```java
// Version 1: Original response format
@RestController
@RequestMapping("/api/v1/users")
public class UserControllerV1 {

    @GetMapping("/{id}")
    public UserResponseV1 getUser(@PathVariable String id) {
        User user = userService.findById(id);
        return new UserResponseV1(user.getId(), user.getName(), user.getEmail());
    }
}

// Version 2: Enhanced response format
@RestController
@RequestMapping("/api/v2/users")
public class UserControllerV2 {

    @GetMapping("/{id}")
    public UserResponseV2 getUser(@PathVariable String id) {
        User user = userService.findById(id);
        return new UserResponseV2(
            user.getId(),
            user.getFullName(),          // Changed: name -> fullName
            user.getEmail(),
            user.getPhone(),             // Added
            user.getCreatedAt()          // Added
        );
    }
}
```

```python
# Version 1: Original response
@app.get("/api/v1/users/{user_id}")
def get_user_v1(user_id: str):
    user = user_service.find_by_id(user_id)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }

# Version 2: Enhanced response
@app.get("/api/v2/users/{user_id}")
def get_user_v2(user_id: str):
    user = user_service.find_by_id(user_id)
    return {
        "id": user.id,
        "full_name": user.full_name,     # Changed
        "email": user.email,
        "phone": user.phone,             # Added
        "created_at": user.created_at,   # Added
    }
```

---

## Error Responses

Good error responses tell the user what went wrong, why it went wrong, and how to fix it.

```
BAD vs GOOD ERROR RESPONSES:

  BAD:
  {
      "error": "Bad Request"
  }

  What went wrong? No idea. How to fix it? Good luck.

  BAD:
  {
      "code": 422,
      "message": "Validation failed"
  }

  Which field? What was wrong with it?

  GOOD:
  {
      "error": {
          "code": "VALIDATION_ERROR",
          "message": "The request contains invalid fields.",
          "details": [
              {
                  "field": "email",
                  "issue": "Must be a valid email address.",
                  "received": "not-an-email"
              },
              {
                  "field": "age",
                  "issue": "Must be between 0 and 150.",
                  "received": -5
              }
          ],
          "documentation": "https://api.example.com/docs/errors#VALIDATION_ERROR"
      }
  }
```

### Standard Error Response Structure

```java
// A consistent error response structure
public class ApiError {
    private final String code;           // Machine-readable error code
    private final String message;        // Human-readable summary
    private final List<FieldError> details;  // Specific field errors
    private final String documentation;  // Link to docs

    // ... constructor and getters
}

public class FieldError {
    private final String field;
    private final String issue;
    private final Object received;

    // ... constructor and getters
}

// Controller advice for consistent error handling
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ValidationException.class)
    @ResponseStatus(HttpStatus.UNPROCESSABLE_ENTITY)
    public ApiError handleValidation(ValidationException e) {
        return new ApiError(
            "VALIDATION_ERROR",
            "The request contains invalid fields.",
            e.getFieldErrors().stream()
                .map(f -> new FieldError(f.getField(), f.getMessage(), f.getValue()))
                .toList(),
            "https://api.example.com/docs/errors#VALIDATION_ERROR"
        );
    }

    @ExceptionHandler(NotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiError handleNotFound(NotFoundException e) {
        return new ApiError(
            "NOT_FOUND",
            "The requested resource was not found.",
            List.of(),
            "https://api.example.com/docs/errors#NOT_FOUND"
        );
    }
}
```

```python
# A consistent error response structure
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class FieldError(BaseModel):
    field: str
    issue: str
    received: str | None = None

class ApiError(BaseModel):
    code: str
    message: str
    details: list[FieldError] = []
    documentation: str = ""

app = FastAPI()

@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    error = ApiError(
        code="VALIDATION_ERROR",
        message="The request contains invalid fields.",
        details=[
            FieldError(field=e["field"], issue=e["message"], received=e.get("value"))
            for e in exc.errors
        ],
        documentation="https://api.example.com/docs/errors#VALIDATION_ERROR",
    )
    return JSONResponse(status_code=422, content=error.dict())
```

### HTTP Status Code Guide

```
COMMON HTTP STATUS CODES:

  Success:
  +-------+------------------+-------------------------------+
  | Code  | Name             | When to use                   |
  +-------+------------------+-------------------------------+
  | 200   | OK               | Successful GET, PUT, PATCH    |
  | 201   | Created          | Successful POST (resource     |
  |       |                  | created)                      |
  | 204   | No Content       | Successful DELETE             |
  +-------+------------------+-------------------------------+

  Client Errors:
  +-------+------------------+-------------------------------+
  | 400   | Bad Request      | Malformed request syntax      |
  | 401   | Unauthorized     | Missing or invalid auth       |
  | 403   | Forbidden        | Authenticated but not allowed |
  | 404   | Not Found        | Resource does not exist       |
  | 409   | Conflict         | Resource state conflict       |
  | 422   | Unprocessable    | Valid syntax but invalid data |
  | 429   | Too Many Requests| Rate limit exceeded           |
  +-------+------------------+-------------------------------+

  Server Errors:
  +-------+------------------+-------------------------------+
  | 500   | Internal Error   | Unexpected server failure     |
  | 502   | Bad Gateway      | Upstream service failure      |
  | 503   | Service Unavail  | Server temporarily down       |
  +-------+------------------+-------------------------------+
```

---

## Pagination

Any endpoint that returns a list should support pagination. Returning all records at once is a performance disaster.

```
PAGINATION STRATEGIES:

  1. OFFSET-BASED (simple, most common):
     GET /orders?page=2&size=20

     Response:
     {
         "data": [...],
         "page": 2,
         "size": 20,
         "total_items": 243,
         "total_pages": 13
     }

     Pros: Simple, random access to any page
     Cons: Skips/duplicates if data changes between requests

  2. CURSOR-BASED (better for large/changing data):
     GET /orders?cursor=eyJpZCI6MTAwfQ&size=20

     Response:
     {
         "data": [...],
         "next_cursor": "eyJpZCI6MTIwfQ",
         "has_more": true
     }

     Pros: No skips/duplicates, better performance
     Cons: No random access, forward-only navigation
```

### Java Example: Offset-Based Pagination

```java
// Pagination request
public record PageRequest(int page, int size) {
    public PageRequest {
        if (page < 1) throw new IllegalArgumentException("Page must be >= 1");
        if (size < 1 || size > 100) throw new IllegalArgumentException(
            "Size must be between 1 and 100"
        );
    }

    public int offset() {
        return (page - 1) * size;
    }
}

// Pagination response wrapper
public record PageResponse<T>(
    List<T> data,
    int page,
    int size,
    long totalItems,
    int totalPages
) {
    public static <T> PageResponse<T> of(List<T> data, PageRequest request, long total) {
        return new PageResponse<>(
            data,
            request.page(),
            request.size(),
            total,
            (int) Math.ceil((double) total / request.size())
        );
    }
}

// Controller
@GetMapping("/orders")
public PageResponse<OrderResponse> listOrders(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "20") int size) {
    PageRequest pageRequest = new PageRequest(page, size);
    List<Order> orders = orderService.findAll(pageRequest);
    long total = orderService.count();
    return PageResponse.of(
        orders.stream().map(OrderResponse::from).toList(),
        pageRequest,
        total
    );
}
```

```python
# Pagination response
from dataclasses import dataclass
from math import ceil
from typing import Generic, TypeVar, List

T = TypeVar("T")

@dataclass
class PageResponse:
    data: list
    page: int
    size: int
    total_items: int
    total_pages: int

    @classmethod
    def of(cls, data: list, page: int, size: int, total: int):
        return cls(
            data=data,
            page=page,
            size=size,
            total_items=total,
            total_pages=ceil(total / size) if size > 0 else 0,
        )

# Endpoint
@app.get("/orders")
def list_orders(page: int = 1, size: int = 20):
    if page < 1:
        raise ValueError("Page must be >= 1")
    if size < 1 or size > 100:
        raise ValueError("Size must be between 1 and 100")

    offset = (page - 1) * size
    orders = order_service.find_all(offset=offset, limit=size)
    total = order_service.count()

    return PageResponse.of(
        data=[order.to_dict() for order in orders],
        page=page,
        size=size,
        total=total,
    )
```

---

## Idempotency: Safe to Retry

An idempotent operation produces the same result whether you call it once or multiple times. This is crucial for reliability -- networks fail, requests get retried, and your API must handle this gracefully.

```
IDEMPOTENCY:

  Calling it once:       Calling it three times:
  PUT /users/123         PUT /users/123  (same result)
  {"name": "Jane"}       PUT /users/123  (same result)
                         PUT /users/123  (same result)

  Result is the same regardless of how many times you call it.

  NATURALLY IDEMPOTENT:
  +--------+-----------------------------------------------+
  | Method | Why                                           |
  +--------+-----------------------------------------------+
  | GET    | Reading does not change state                 |
  | PUT    | Replaces entire resource to known state       |
  | DELETE | Deleting already-deleted resource is harmless |
  +--------+-----------------------------------------------+

  NOT NATURALLY IDEMPOTENT:
  +--------+-----------------------------------------------+
  | Method | Why                                           |
  +--------+-----------------------------------------------+
  | POST   | Each call may create a new resource           |
  | PATCH  | "increment by 1" is not idempotent            |
  +--------+-----------------------------------------------+
```

### Making POST Idempotent with Idempotency Keys

```java
// The client sends a unique key with each request
// If the same key is sent again, return the original result
@PostMapping("/payments")
public ResponseEntity<PaymentResponse> createPayment(
        @RequestHeader("Idempotency-Key") String idempotencyKey,
        @RequestBody PaymentRequest request) {

    // Check if we already processed this key
    Optional<PaymentResponse> existing = idempotencyStore.find(idempotencyKey);
    if (existing.isPresent()) {
        return ResponseEntity.ok(existing.get());  // Return cached result
    }

    // Process the payment
    PaymentResponse response = paymentService.processPayment(request);

    // Store the result keyed by idempotency key
    idempotencyStore.save(idempotencyKey, response);

    return ResponseEntity.status(HttpStatus.CREATED).body(response);
}
```

```python
# Making POST idempotent with idempotency keys
@app.post("/payments")
def create_payment(
    request: PaymentRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    # Check if we already processed this key
    existing = idempotency_store.find(idempotency_key)
    if existing is not None:
        return existing  # Return cached result

    # Process the payment
    response = payment_service.process_payment(request)

    # Store the result
    idempotency_store.save(idempotency_key, response)

    return response
```

---

## API Review Checklist

Use this checklist when designing or reviewing any API:

```
API REVIEW CHECKLIST:

  NAMING AND CONSISTENCY:
  [ ] Resource names are plural nouns (users, orders, products)
  [ ] Naming is consistent across all endpoints
  [ ] No verbs in URLs (use HTTP methods instead)
  [ ] Snake_case or camelCase is used consistently (not mixed)

  REQUESTS:
  [ ] Required vs optional fields are clearly documented
  [ ] Input validation is thorough with clear error messages
  [ ] Sensible defaults for optional parameters
  [ ] Maximum limits on list sizes and string lengths

  RESPONSES:
  [ ] Consistent response structure across all endpoints
  [ ] Error responses include code, message, and details
  [ ] Successful responses include only relevant data
  [ ] Dates use ISO 8601 format (2024-01-15T10:30:00Z)
  [ ] Monetary values include currency information

  PAGINATION:
  [ ] List endpoints are paginated
  [ ] Page size has a maximum limit (e.g., 100)
  [ ] Response includes total count and navigation info

  ERRORS:
  [ ] Appropriate HTTP status codes used
  [ ] Error format is consistent and documented
  [ ] No sensitive information leaked in errors
  [ ] Rate limiting returns 429 with Retry-After header

  COMPATIBILITY:
  [ ] No breaking changes to existing fields
  [ ] New fields have default values
  [ ] Versioning strategy is defined
  [ ] Deprecation policy is communicated

  SAFETY:
  [ ] GET requests are read-only (no side effects)
  [ ] PUT and DELETE are idempotent
  [ ] POST endpoints support idempotency keys where needed
  [ ] Authentication and authorization are enforced
  [ ] Input is sanitized to prevent injection attacks

  DOCUMENTATION:
  [ ] Every endpoint is documented with examples
  [ ] Request/response schemas are defined
  [ ] Error codes are listed and explained
  [ ] Rate limits are documented
```

---

## Common Mistakes

### Mistake 1: Verbs in URLs

Using `/getUsers` or `/createOrder` instead of letting HTTP methods convey the action.

**Fix:** Use `GET /users` and `POST /orders`. The HTTP method is the verb.

### Mistake 2: Inconsistent Error Formats

Some endpoints return `{"error": "..."}`, others return `{"message": "..."}`, and others return plain strings.

**Fix:** Use a single error response structure everywhere. Enforce it with a global exception handler.

### Mistake 3: No Pagination

Returning all 50,000 records in a single response because "it works with test data."

**Fix:** Always paginate list endpoints. Default to a reasonable page size (20-50). Set a maximum (100).

### Mistake 4: Breaking Changes Without Versioning

Renaming a response field from `name` to `fullName` without versioning, breaking all existing clients.

**Fix:** Either keep backward compatibility (add `fullName` alongside `name`) or introduce a new API version.

### Mistake 5: Exposing Internal Models Directly

Using your database entity as your API response, leaking internal fields like `password_hash` or `internal_notes`.

**Fix:** Create separate response DTOs that contain only the fields API consumers should see.

---

## Best Practices

1. **Follow the Principle of Least Surprise.** APIs should do what their names suggest, nothing more.
2. **Be consistent.** Pick naming conventions and stick to them everywhere.
3. **Never break backward compatibility** without versioning and a deprecation period.
4. **Design error responses for humans.** Include the field, the issue, and a link to documentation.
5. **Paginate all list endpoints.** No exceptions. Default page sizes are your friend.
6. **Make unsafe operations idempotent** where possible, using idempotency keys for POST requests.
7. **Create response DTOs.** Never expose internal models directly through your API.
8. **Use your own API.** The best way to find usability issues is to be your own first user.
9. **Review APIs before implementing them.** Changing an API after clients depend on it is expensive.
10. **Document with examples.** Show complete request/response pairs, not just schemas.

---

## Quick Summary

```
API DESIGN PRINCIPLES AT A GLANCE:

  Principle             What it means
  +-------------------+------------------------------------+
  | Least Surprise    | API behaves as the name suggests.  |
  |                   | No hidden side effects.            |
  +-------------------+------------------------------------+
  | Consistency       | Same conventions everywhere.       |
  |                   | Pick one style, use it always.     |
  +-------------------+------------------------------------+
  | Backward Compat   | Adding is safe. Removing breaks.   |
  |                   | Use versioning for breaking change.|
  +-------------------+------------------------------------+
  | Clear Errors      | Code + message + details + docs.   |
  |                   | Tell users what went wrong and how |
  |                   | to fix it.                         |
  +-------------------+------------------------------------+
  | Pagination        | Never return unbounded lists.      |
  |                   | Always paginate.                   |
  +-------------------+------------------------------------+
  | Idempotency       | Safe to retry. Same call, same     |
  |                   | result. Use idempotency keys.      |
  +-------------------+------------------------------------+
```

---

## Key Points

- The Principle of Least Surprise is the foundation of good API design: APIs should behave as their names suggest.
- Consistent naming (plural nouns for resources, HTTP methods for actions) makes APIs predictable and learnable.
- Backward compatibility protects existing users: add new fields, never remove or rename existing ones without versioning.
- Use URL path versioning (e.g., `/api/v1/users`) as the most transparent versioning strategy.
- Error responses should include a machine-readable code, human-readable message, field-level details, and a documentation link.
- Always paginate list endpoints with a maximum page size limit.
- Idempotency makes APIs safe to retry: use idempotency keys for POST endpoints where duplicate processing is dangerous.
- Review APIs using the checklist before implementation, not after.

---

## Practice Questions

1. A developer proposes this endpoint: `POST /api/users/getByEmail`. What are two things wrong with this design, and how would you fix it?

2. Your API currently returns user responses with a `name` field. A new requirement asks you to split this into `firstName` and `lastName`. How would you handle this without breaking existing clients?

3. Explain the difference between offset-based and cursor-based pagination. When would you choose each?

4. A POST endpoint to create orders sometimes receives the same request twice due to network retries, resulting in duplicate orders. How would you solve this?

5. Your team uses these error response formats across different endpoints: `{"error": "..."}`, `{"message": "..."}`, `{"err_code": 1, "err_msg": "..."}`. What is the problem and how would you fix it?

---

## Exercises

### Exercise 1: Design a REST API

Design a complete REST API for a library management system. Define endpoints for books (list, get, create, update, delete), members (list, get, create), and loans (borrow, return, list active). Include: URL paths, HTTP methods, request/response formats, error responses, and pagination. Apply all principles from this chapter.

### Exercise 2: Build Error Handling

Implement a global error handler (in Java or Python) that catches common exceptions (`NotFoundException`, `ValidationException`, `UnauthorizedException`, `RateLimitException`) and returns consistent error responses with the structure defined in this chapter.

### Exercise 3: Add Idempotency

You have a `POST /transfers` endpoint that moves money between bank accounts. Implement idempotency using an idempotency key so that network retries do not cause double transfers. Include the key storage mechanism and the duplicate detection logic.

---

## What Is Next?

With strong API design principles in your toolkit, we jump ahead to Chapter 29: Code Review Culture -- how teams use code reviews not just to catch bugs, but to maintain quality, share knowledge, and build a culture of continuous improvement. You will learn what to look for in a review, how to give and receive feedback constructively, and how to keep pull requests at a reviewable size.
