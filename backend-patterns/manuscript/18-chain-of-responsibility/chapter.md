# Chapter 18: Chain of Responsibility -- Pass Requests Along a Handler Chain

## What You Will Learn

- How to build a chain of handlers that each decide whether to process or pass a request
- Implementing middleware chains in Java (AuthHandler, ValidationHandler, LoggingHandler)
- Building Python approval chains for business workflows
- Using Spring interceptors and servlet filters as real-world chains
- Applying Chain of Responsibility to HTTP middleware, validation pipelines, and exception handling

## Why This Chapter Matters

In every backend system, requests pass through multiple processing stages before reaching their destination. An HTTP request might need authentication, then rate limiting, then input validation, then logging -- all before the actual business logic runs. You need a way to compose these stages flexibly, add or remove stages without changing others, and let each stage decide independently whether the request should continue.

The Chain of Responsibility pattern does exactly this. It links handlers into a chain where each handler either processes the request and stops, or passes it to the next handler. This is the pattern behind servlet filters, Express middleware, Django middleware, and Spring interceptors.

---

## The Problem: Hardcoded Processing Pipeline

```java
// RequestProcessor.java (BEFORE -- monolithic)
public class RequestProcessor {

    public Response process(Request request) {
        // Authentication
        if (!isAuthenticated(request)) {
            return new Response(401, "Unauthorized");
        }

        // Rate limiting
        if (isRateLimited(request)) {
            return new Response(429, "Too Many Requests");
        }

        // Input validation
        if (!isValid(request)) {
            return new Response(400, "Bad Request");
        }

        // Logging
        logRequest(request);

        // Business logic
        return handleBusinessLogic(request);
    }
    // Adding a new check = modifying this method
    // Removing a check = modifying this method
    // Reordering checks = modifying this method
    // Testing one check in isolation = impossible
}
```

```
The Problem:

  +------------------------------------------+
  |          RequestProcessor                 |
  |                                          |
  |  if (!authenticated) return 401          |
  |  if (rateLimited) return 429             |
  |  if (!valid) return 400                  |
  |  logRequest()                            |
  |  return businessLogic()                  |
  |                                          |
  |  ALL logic in ONE class.                 |
  |  Cannot reorder, add, or remove steps    |
  |  without touching this code.             |
  +------------------------------------------+
```

---

## The Solution: Chain of Responsibility

```
Chain of Responsibility Structure:

  Request
    |
    v
  +--------+     +--------+     +--------+     +----------+
  |  Auth   |---->| Rate   |---->|Validate|---->| Business |
  | Handler |     | Limiter|     | Handler|     |  Logic   |
  +--------+     +--------+     +--------+     +----------+
    |               |               |
    v               v               v
  (reject)       (reject)       (reject)
  401            429             400

  Each handler:
  1. Inspects the request
  2. Either handles it (stops the chain) or passes it to the next handler
  3. Knows NOTHING about other handlers in the chain
```

---

## Java Implementation: Middleware Chain

### Step 1: Define the Handler Interface

```java
// Handler.java
public abstract class Handler {
    private Handler next;

    public Handler setNext(Handler next) {
        this.next = next;
        return next;  // Return next for fluent chaining
    }

    public Response handle(Request request) {
        if (next != null) {
            return next.handle(request);
        }
        return new Response(200, "OK -- reached end of chain");
    }

    protected Handler getNext() {
        return next;
    }
}

// Request.java
public class Request {
    private final String path;
    private final String method;
    private final Map<String, String> headers;
    private final String body;
    private final String clientIp;

    public Request(String path, String method,
                   Map<String, String> headers, String body,
                   String clientIp) {
        this.path = path;
        this.method = method;
        this.headers = headers;
        this.body = body;
        this.clientIp = clientIp;
    }

    // Getters
    public String getPath() { return path; }
    public String getMethod() { return method; }
    public Map<String, String> getHeaders() { return headers; }
    public String getBody() { return body; }
    public String getClientIp() { return clientIp; }
}

// Response.java
public class Response {
    private final int statusCode;
    private final String body;

    public Response(int statusCode, String body) {
        this.statusCode = statusCode;
        this.body = body;
    }

    public int getStatusCode() { return statusCode; }
    public String getBody() { return body; }

    @Override
    public String toString() {
        return statusCode + ": " + body;
    }
}
```

### Step 2: Implement Concrete Handlers

```java
// AuthHandler.java
public class AuthHandler extends Handler {

    private static final Set<String> VALID_TOKENS = Set.of(
        "token-abc123", "token-def456"
    );

    @Override
    public Response handle(Request request) {
        System.out.println("  [Auth] Checking authentication...");

        String authHeader = request.getHeaders().get("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            System.out.println("  [Auth] REJECTED -- No token provided");
            return new Response(401, "Unauthorized: Missing token");
        }

        String token = authHeader.substring(7);
        if (!VALID_TOKENS.contains(token)) {
            System.out.println("  [Auth] REJECTED -- Invalid token");
            return new Response(401, "Unauthorized: Invalid token");
        }

        System.out.println("  [Auth] PASSED");
        return super.handle(request);  // Pass to next handler
    }
}

// RateLimitHandler.java
public class RateLimitHandler extends Handler {

    private final Map<String, Integer> requestCounts = new HashMap<>();
    private final int maxRequests;

    public RateLimitHandler(int maxRequestsPerMinute) {
        this.maxRequests = maxRequestsPerMinute;
    }

    @Override
    public Response handle(Request request) {
        System.out.println("  [RateLimit] Checking rate limit...");

        String clientIp = request.getClientIp();
        int count = requestCounts.getOrDefault(clientIp, 0) + 1;
        requestCounts.put(clientIp, count);

        if (count > maxRequests) {
            System.out.println("  [RateLimit] REJECTED -- "
                + count + "/" + maxRequests + " requests");
            return new Response(429, "Too Many Requests");
        }

        System.out.println("  [RateLimit] PASSED (" + count
            + "/" + maxRequests + ")");
        return super.handle(request);
    }
}

// ValidationHandler.java
public class ValidationHandler extends Handler {

    @Override
    public Response handle(Request request) {
        System.out.println("  [Validation] Validating request...");

        if ("POST".equals(request.getMethod())
                || "PUT".equals(request.getMethod())) {
            if (request.getBody() == null || request.getBody().isEmpty()) {
                System.out.println("  [Validation] REJECTED -- Empty body");
                return new Response(400, "Bad Request: Body required");
            }
        }

        if (request.getPath() == null || request.getPath().isEmpty()) {
            System.out.println("  [Validation] REJECTED -- No path");
            return new Response(400, "Bad Request: Path required");
        }

        System.out.println("  [Validation] PASSED");
        return super.handle(request);
    }
}

// LoggingHandler.java
public class LoggingHandler extends Handler {

    @Override
    public Response handle(Request request) {
        System.out.println("  [Logging] " + request.getMethod()
            + " " + request.getPath()
            + " from " + request.getClientIp());

        long start = System.currentTimeMillis();
        Response response = super.handle(request);  // Continue chain
        long duration = System.currentTimeMillis() - start;

        System.out.println("  [Logging] Response: "
            + response.getStatusCode() + " (" + duration + "ms)");
        return response;
    }
}

// BusinessLogicHandler.java
public class BusinessLogicHandler extends Handler {

    @Override
    public Response handle(Request request) {
        System.out.println("  [Business] Processing business logic...");

        // Simulate actual work
        String result = "Processed: " + request.getMethod()
            + " " + request.getPath();

        return new Response(200, result);
    }
}
```

### Step 3: Build and Use the Chain

```java
// Main.java
public class Main {
    public static void main(String[] args) {
        // Build the chain
        Handler auth = new AuthHandler();
        Handler rateLimit = new RateLimitHandler(5);
        Handler validation = new ValidationHandler();
        Handler logging = new LoggingHandler();
        Handler business = new BusinessLogicHandler();

        // Link: Auth -> RateLimit -> Validation -> Logging -> Business
        auth.setNext(rateLimit)
            .setNext(validation)
            .setNext(logging)
            .setNext(business);

        // Test 1: Valid request
        System.out.println("--- Test 1: Valid Request ---");
        Request validRequest = new Request(
            "/api/users", "GET",
            Map.of("Authorization", "Bearer token-abc123"),
            "", "192.168.1.1"
        );
        Response r1 = auth.handle(validRequest);
        System.out.println("Final: " + r1 + "\n");

        // Test 2: No auth token
        System.out.println("--- Test 2: Missing Auth ---");
        Request noAuth = new Request(
            "/api/users", "GET",
            Map.of(), "", "192.168.1.2"
        );
        Response r2 = auth.handle(noAuth);
        System.out.println("Final: " + r2 + "\n");

        // Test 3: POST with empty body
        System.out.println("--- Test 3: Empty POST Body ---");
        Request emptyPost = new Request(
            "/api/users", "POST",
            Map.of("Authorization", "Bearer token-abc123"),
            "", "192.168.1.1"
        );
        Response r3 = auth.handle(emptyPost);
        System.out.println("Final: " + r3 + "\n");
    }
}
```

**Output:**
```
--- Test 1: Valid Request ---
  [Auth] Checking authentication...
  [Auth] PASSED
  [RateLimit] Checking rate limit...
  [RateLimit] PASSED (1/5)
  [Validation] Validating request...
  [Validation] PASSED
  [Logging] GET /api/users from 192.168.1.1
  [Business] Processing business logic...
  [Logging] Response: 200 (1ms)
Final: 200: Processed: GET /api/users

--- Test 2: Missing Auth ---
  [Auth] Checking authentication...
  [Auth] REJECTED -- No token provided
Final: 401: Unauthorized: Missing token

--- Test 3: Empty POST Body ---
  [Auth] Checking authentication...
  [Auth] PASSED
  [RateLimit] Checking rate limit...
  [RateLimit] PASSED (2/5)
  [Validation] Validating request...
  [Validation] REJECTED -- Empty body
Final: 400: Bad Request: Body required
```

---

## Before vs After

```
BEFORE (monolithic):                 AFTER (chain):
+---------------------------+       +------+  +------+  +------+
| if (!auth) return 401     |       | Auth |->| Rate |->|Valid. |
| if (rateLimit) return 429 |       +------+  +------+  +------+
| if (!valid) return 400    |           |         |         |
| log()                     |           v         v         v
| return business()         |        reject    reject    reject
+---------------------------+
                                    +------+  +--------+
  Adding CORS handler:              | Log  |->|Business|
  Modify the monolithic class       +------+  +--------+

                                    Adding CORS handler:
                                    Insert CorsHandler between
                                    Auth and RateLimit. No other
                                    handler changes.
```

---

## Python Implementation: Approval Chain

```python
# approval_chain.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PurchaseRequest:
    description: str
    amount: float
    requester: str
    department: str


@dataclass
class ApprovalResult:
    approved: bool
    approver: str
    message: str


class Approver(ABC):
    """Base handler in the approval chain."""

    def __init__(self, name: str, limit: float):
        self.name = name
        self.limit = limit
        self._next: Optional[Approver] = None

    def set_next(self, approver: "Approver") -> "Approver":
        self._next = approver
        return approver

    def handle(self, request: PurchaseRequest) -> ApprovalResult:
        if request.amount <= self.limit:
            return self.approve(request)

        if self._next:
            print(f"  [{self.name}] ${request.amount:,.2f} exceeds "
                  f"my limit (${self.limit:,.2f}). Escalating...")
            return self._next.handle(request)

        return ApprovalResult(
            approved=False,
            approver=self.name,
            message=f"No one can approve ${request.amount:,.2f}"
        )

    def approve(self, request: PurchaseRequest) -> ApprovalResult:
        print(f"  [{self.name}] APPROVED: {request.description} "
              f"(${request.amount:,.2f})")
        return ApprovalResult(
            approved=True,
            approver=self.name,
            message=f"Approved by {self.name}"
        )


class TeamLead(Approver):
    def __init__(self):
        super().__init__("Team Lead", limit=1000.0)


class Manager(Approver):
    def __init__(self):
        super().__init__("Manager", limit=10000.0)


class Director(Approver):
    def __init__(self):
        super().__init__("Director", limit=50000.0)


class VP(Approver):
    def __init__(self):
        super().__init__("VP", limit=100000.0)

    def approve(self, request: PurchaseRequest) -> ApprovalResult:
        # VP adds extra scrutiny
        print(f"  [{self.name}] Reviewing budget impact for "
              f"${request.amount:,.2f}...")
        if request.department == "R&D" and request.amount > 75000:
            print(f"  [{self.name}] R&D budget limit reached. "
                  f"Needs board approval.")
            return ApprovalResult(
                approved=False,
                approver=self.name,
                message="Needs board approval for R&D expenses > $75k"
            )
        return super().approve(request)


# --- Usage ---
if __name__ == "__main__":
    # Build the chain
    team_lead = TeamLead()
    manager = Manager()
    director = Director()
    vp = VP()

    team_lead.set_next(manager).set_next(director).set_next(vp)

    # Test different amounts
    requests = [
        PurchaseRequest("Office supplies", 500, "Alice", "Engineering"),
        PurchaseRequest("New monitors", 5000, "Bob", "Engineering"),
        PurchaseRequest("Server upgrade", 25000, "Charlie", "Ops"),
        PurchaseRequest("ML training cluster", 80000, "Dave", "R&D"),
        PurchaseRequest("Office renovation", 150000, "Eve", "Facilities"),
    ]

    for req in requests:
        print(f"\n--- Purchase Request: {req.description} "
              f"(${req.amount:,.2f}) ---")
        result = team_lead.handle(req)
        status = "APPROVED" if result.approved else "DENIED"
        print(f"  Result: {status} -- {result.message}")
```

**Output:**
```
--- Purchase Request: Office supplies ($500.00) ---
  [Team Lead] APPROVED: Office supplies ($500.00)
  Result: APPROVED -- Approved by Team Lead

--- Purchase Request: New monitors ($5,000.00) ---
  [Team Lead] $5,000.00 exceeds my limit ($1,000.00). Escalating...
  [Manager] APPROVED: New monitors ($5,000.00)
  Result: APPROVED -- Approved by Manager

--- Purchase Request: Server upgrade ($25,000.00) ---
  [Team Lead] $25,000.00 exceeds my limit ($1,000.00). Escalating...
  [Manager] $25,000.00 exceeds my limit ($10,000.00). Escalating...
  [Director] APPROVED: Server upgrade ($25,000.00)
  Result: APPROVED -- Approved by Director

--- Purchase Request: ML training cluster ($80,000.00) ---
  [Team Lead] $80,000.00 exceeds my limit ($1,000.00). Escalating...
  [Manager] $80,000.00 exceeds my limit ($10,000.00). Escalating...
  [Director] $80,000.00 exceeds my limit ($50,000.00). Escalating...
  [VP] Reviewing budget impact for $80,000.00...
  [VP] R&D budget limit reached. Needs board approval.
  Result: DENIED -- Needs board approval for R&D expenses > $75k

--- Purchase Request: Office renovation ($150,000.00) ---
  [Team Lead] $150,000.00 exceeds my limit ($1,000.00). Escalating...
  [Manager] $150,000.00 exceeds my limit ($10,000.00). Escalating...
  [Director] $150,000.00 exceeds my limit ($50,000.00). Escalating...
  [VP] $150,000.00 exceeds my limit ($100,000.00). Escalating...
  Result: DENIED -- No one can approve $150,000.00
```

---

## Spring Interceptors

Spring uses Chain of Responsibility via `HandlerInterceptor`.

```java
// AuthInterceptor.java
@Component
public class AuthInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) throws Exception {
        String token = request.getHeader("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            response.setStatus(401);
            response.getWriter().write("Unauthorized");
            return false;  // STOP the chain
        }
        return true;  // CONTINUE the chain
    }
}

// LoggingInterceptor.java
@Component
public class LoggingInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) throws Exception {
        request.setAttribute("startTime", System.currentTimeMillis());
        System.out.println("[Log] " + request.getMethod()
            + " " + request.getRequestURI());
        return true;  // Always continue
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
                                HttpServletResponse response,
                                Object handler, Exception ex) {
        long start = (Long) request.getAttribute("startTime");
        long duration = System.currentTimeMillis() - start;
        System.out.println("[Log] Completed in " + duration + "ms"
            + " -- Status: " + response.getStatus());
    }
}

// Register interceptors
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Autowired private AuthInterceptor authInterceptor;
    @Autowired private LoggingInterceptor loggingInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // Order matters -- auth runs first
        registry.addInterceptor(loggingInterceptor)
                .addPathPatterns("/**");

        registry.addInterceptor(authInterceptor)
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/public/**");
    }
}
```

```
Spring Interceptor Chain:

  HTTP Request
       |
       v
  +------------------+
  | LoggingInterceptor|  preHandle()
  +------------------+
       |
       v
  +------------------+
  | AuthInterceptor   |  preHandle()
  +------------------+       |
       |                 return false -> 401 (chain stops)
       v                 return true  -> chain continues
  +------------------+
  | Controller        |  handleRequest()
  +------------------+
       |
       v
  +------------------+
  | AuthInterceptor   |  afterCompletion()
  +------------------+
       |
       v
  +------------------+
  | LoggingInterceptor|  afterCompletion()
  +------------------+
       |
       v
  HTTP Response
```

---

## Real-World Use Case: Validation Pipeline

```java
// ValidationHandler.java
public abstract class ValidationHandler extends Handler {
    private final String ruleName;

    protected ValidationHandler(String ruleName) {
        this.ruleName = ruleName;
    }

    @Override
    public Response handle(Request request) {
        List<String> errors = validate(request);
        if (!errors.isEmpty()) {
            System.out.println("  [" + ruleName + "] FAILED: " + errors);
            return new Response(400, "Validation failed: " + errors);
        }
        System.out.println("  [" + ruleName + "] PASSED");
        return super.handle(request);
    }

    protected abstract List<String> validate(Request request);
}

// ContentTypeValidator.java
public class ContentTypeValidator extends ValidationHandler {
    public ContentTypeValidator() { super("ContentType"); }

    @Override
    protected List<String> validate(Request request) {
        List<String> errors = new ArrayList<>();
        String contentType = request.getHeaders().get("Content-Type");
        if ("POST".equals(request.getMethod())
                && !"application/json".equals(contentType)) {
            errors.add("Content-Type must be application/json");
        }
        return errors;
    }
}

// BodySizeValidator.java
public class BodySizeValidator extends ValidationHandler {
    private final int maxSize;

    public BodySizeValidator(int maxSizeBytes) {
        super("BodySize");
        this.maxSize = maxSizeBytes;
    }

    @Override
    protected List<String> validate(Request request) {
        List<String> errors = new ArrayList<>();
        if (request.getBody() != null && request.getBody().length() > maxSize) {
            errors.add("Body exceeds " + maxSize + " bytes");
        }
        return errors;
    }
}

// RequiredFieldsValidator.java
public class RequiredFieldsValidator extends ValidationHandler {
    private final Set<String> requiredFields;

    public RequiredFieldsValidator(String... fields) {
        super("RequiredFields");
        this.requiredFields = Set.of(fields);
    }

    @Override
    protected List<String> validate(Request request) {
        List<String> errors = new ArrayList<>();
        // In a real system, parse JSON body and check fields
        for (String field : requiredFields) {
            if (!request.getBody().contains("\"" + field + "\"")) {
                errors.add("Missing required field: " + field);
            }
        }
        return errors;
    }
}
```

---

## When to Use / When NOT to Use

### Use Chain of Responsibility When

| Scenario | Why Chain Helps |
|---|---|
| HTTP middleware pipeline | Each middleware is independent |
| Validation with multiple rules | Each rule is a separate handler |
| Approval workflows | Different approval levels |
| Exception handling | Try catch chains with fallbacks |
| Logging/monitoring pipeline | Non-blocking pass-through handlers |

### Do NOT Use Chain of Responsibility When

| Scenario | Why Not |
|---|---|
| Guaranteed processing by all handlers | Chain can stop early -- use Observer |
| Order does not matter | A simple list of validators is simpler |
| Only one handler ever handles a request | Direct dispatch is clearer |
| Performance-critical path | Chain traversal adds overhead |

---

## Common Mistakes

### Mistake 1: Broken Chain (Forgetting to Call Next)

```java
// BAD -- Handler processes but never passes to next
public class LoggingHandler extends Handler {
    @Override
    public Response handle(Request request) {
        log(request);
        // Forgot super.handle(request) -- chain stops here!
        return new Response(200, "Logged");
    }
}

// GOOD -- Always call super.handle() to continue the chain
public class LoggingHandler extends Handler {
    @Override
    public Response handle(Request request) {
        log(request);
        return super.handle(request);  // Continue chain
    }
}
```

### Mistake 2: Handlers That Depend on Order

```java
// BAD -- Validation assumes auth already ran
public class ValidationHandler extends Handler {
    @Override
    public Response handle(Request request) {
        User user = request.getAuthenticatedUser();  // Assumes auth set this
        // NullPointerException if auth handler was removed or reordered
    }
}

// GOOD -- Each handler is self-contained
public class ValidationHandler extends Handler {
    @Override
    public Response handle(Request request) {
        // Validate independently, without assumptions about other handlers
        if (request.getBody() == null) {
            return new Response(400, "Body required");
        }
        return super.handle(request);
    }
}
```

### Mistake 3: Circular Chain

```java
// BAD -- Creates infinite loop
Handler a = new AuthHandler();
Handler b = new LoggingHandler();
a.setNext(b);
b.setNext(a);  // Circular! Infinite loop when handling requests

// GOOD -- Chain always terminates
// Either reaches end (next is null) or a handler stops it
```

---

## Best Practices

1. **Each handler should be independent.** It should not assume what handlers ran before it or will run after it.

2. **Always provide a chain terminator.** The last handler should produce a final response or action.

3. **Make handler order configurable.** Use a builder or configuration file to define the chain, not hardcoded wiring.

4. **Log at each handler.** When debugging, you need to know which handler in the chain processed or rejected the request.

5. **Handle exceptions in each handler.** One handler throwing should not crash the entire chain.

6. **Keep handlers focused.** One handler, one responsibility. Authentication, validation, and logging should be separate handlers.

---

## Quick Summary

```
+---------------------------------------------------------------+
|             CHAIN OF RESPONSIBILITY SUMMARY                    |
+---------------------------------------------------------------+
| Intent:     Pass a request along a chain of handlers. Each     |
|             handler processes or forwards the request.         |
+---------------------------------------------------------------+
| Problem:    Monolithic request processing with tangled logic   |
| Solution:   Independent handlers linked in a configurable     |
|             chain                                              |
+---------------------------------------------------------------+
| Key parts:                                                     |
|   - Handler (abstract, knows next handler)                     |
|   - Concrete handlers (auth, validation, logging, etc.)        |
|   - Client (builds chain, sends initial request)               |
+---------------------------------------------------------------+
| Real-world: HTTP middleware, servlet filters, Spring            |
|             interceptors, approval workflows                   |
+---------------------------------------------------------------+
```

---

## Key Points

- Chain of Responsibility links handlers in a sequence where each handler decides to process or pass the request.
- Each handler is independent and can be added, removed, or reordered without affecting others.
- The pattern is the foundation of HTTP middleware in every major web framework.
- Spring uses `HandlerInterceptor` with `preHandle()` (before controller) and `afterCompletion()` (after response).
- Always ensure the chain terminates -- either a handler stops it or it reaches the end.
- Handlers should not depend on the order of other handlers in the chain.

---

## Practice Questions

1. In the middleware chain example, what happens if the `LoggingHandler` is placed after the `AuthHandler` and a request fails authentication? Does the request get logged? How would you ensure all requests are logged regardless of outcome?

2. How does Chain of Responsibility differ from a simple `List<Validator>` where you iterate and check each one? When does the chain pattern add value over a list?

3. You need to add a CORS handler to the middleware chain. Where should it go? What happens if it is placed after the AuthHandler?

4. In the approval chain, the VP rejects R&D requests over $75K. How would you make this rule configurable without modifying the VP class?

5. Spring's `FilterChain.doFilter()` uses Chain of Responsibility. What happens if a filter calls `doFilter()` twice? How does Spring prevent this?

---

## Exercises

### Exercise 1: Exception Handler Chain

Build a chain of exception handlers: `ValidationExceptionHandler` (returns 400), `AuthenticationExceptionHandler` (returns 401), `NotFoundExceptionHandler` (returns 404), and `GenericExceptionHandler` (returns 500 as fallback). Each handler checks if it can handle the exception type, and if not, passes it to the next.

### Exercise 2: Content Negotiation

Create a handler chain for content negotiation. `JSONHandler` checks if the client accepts JSON, `XMLHandler` checks for XML, and `HTMLHandler` checks for HTML. The first handler that matches the client's `Accept` header produces the response. Add a `DefaultHandler` that returns JSON if no match is found.

### Exercise 3: Multi-Stage Data Pipeline

Build a data processing pipeline as a chain: `DeduplicationHandler` (removes duplicates), `NormalizationHandler` (standardizes formats), `EnrichmentHandler` (adds computed fields), and `PersistenceHandler` (saves to database). Each handler transforms the data and passes the modified version to the next handler.

---

## What Is Next?

Chain of Responsibility lets requests flow through a series of independent handlers. But what happens when an object's behavior needs to change based on its internal state, and you want to avoid a mess of `if/else` conditions? In the next chapter, we explore the **State pattern** -- a clean way to model state machines where objects behave differently depending on what state they are in.
