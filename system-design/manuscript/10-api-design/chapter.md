# Chapter 10: API Design

## What You Will Learn

- REST principles and how to design clean, predictable APIs
- HTTP methods (GET, POST, PUT, PATCH, DELETE) and when to use each
- HTTP status codes and what they communicate to clients
- API versioning strategies and their trade-offs
- Pagination approaches: offset-based vs cursor-based
- Filtering, sorting, and searching patterns
- Rate limiting headers and how they protect your API
- Idempotency and why it matters for reliable APIs
- Authentication and authorization: API keys, OAuth 2.0, JWT
- GraphQL vs REST vs gRPC: when to use each
- OpenAPI (Swagger) for documentation and code generation

## Why This Chapter Matters

An API (Application Programming Interface) is the contract between your system and its clients. It is how mobile apps, web frontends, third-party services, and other internal services communicate with your backend.

A well-designed API is a joy to use. Developers can guess how it works without reading documentation. Errors are clear and actionable. It scales without breaking existing clients.

A poorly designed API is a nightmare. Endpoints are inconsistent, error messages are cryptic, and every new feature breaks old integrations. Bad APIs generate endless support tickets and slow down every team that depends on them.

In system design interviews, API design is often the first thing you do: define the interface before designing the internals. Getting it right sets the foundation for everything that follows.

---

## 10.1 REST Principles

REST (Representational State Transfer) is an architectural style for designing web APIs. It was defined by Roy Fielding in his 2000 doctoral dissertation. Most web APIs today claim to be RESTful, though few follow every principle strictly.

### Core REST Principles

**1. Resources, not actions.** URLs represent things (nouns), not operations (verbs).

```
GOOD (resource-oriented):
  GET    /users/42          Get user 42
  POST   /users             Create a new user
  PUT    /users/42          Replace user 42
  DELETE /users/42          Delete user 42

BAD (action-oriented):
  GET    /getUser?id=42
  POST   /createUser
  POST   /deleteUser?id=42
  GET    /fetchAllUsers
```

**2. Use HTTP methods for operations.** The verb is in the method, not the URL.

**3. Stateless.** Each request contains all the information needed to process it. The server does not store client session state between requests.

**4. Uniform interface.** All resources follow the same patterns. If you know how `/users` works, you can guess how `/products` works.

**5. HATEOAS (Hypermedia As The Engine Of Application State).** Responses include links to related resources. In practice, few APIs implement this fully.

### Resource Naming Conventions

```
+---------------------------+-------------------------------+
| Convention                | Example                       |
+---------------------------+-------------------------------+
| Use plural nouns          | /users (not /user)            |
| Use lowercase             | /users (not /Users)           |
| Use hyphens for multi-word| /user-profiles (not           |
|                           |  /userProfiles)               |
| Nest for relationships    | /users/42/orders              |
| Limit nesting depth       | /users/42/orders (not         |
|                           |  /users/42/orders/7/items/3)  |
| Use query params for      | /users?role=admin             |
| filtering                 |                               |
+---------------------------+-------------------------------+
```

---

## 10.2 HTTP Methods

Each HTTP method has specific semantics. Using them correctly makes your API predictable.

```
+--------+------------+-------------+-----------+-------------+
| Method | Purpose    | Request Body| Idempotent| Safe (no    |
|        |            |             |           | side effects|
+--------+------------+-------------+-----------+-------------+
| GET    | Read       | No          | Yes       | Yes         |
| POST   | Create     | Yes         | No        | No          |
| PUT    | Replace    | Yes         | Yes       | No          |
| PATCH  | Partial    | Yes         | No*       | No          |
|        | update     |             |           |             |
| DELETE | Delete     | Optional    | Yes       | No          |
+--------+------------+-------------+-----------+-------------+

* PATCH can be made idempotent with careful design
```

### When to Use Each

```
GET /users
  --> List all users (with pagination)

GET /users/42
  --> Get user with ID 42

POST /users
  Body: {"name": "Alice", "email": "alice@ex.com"}
  --> Create a new user. Server assigns the ID.

PUT /users/42
  Body: {"name": "Alice Smith", "email": "alice@ex.com", "age": 30}
  --> Replace user 42 entirely. All fields must be present.

PATCH /users/42
  Body: {"name": "Alice Smith"}
  --> Update only the name. Other fields unchanged.

DELETE /users/42
  --> Delete user 42.
```

### PUT vs PATCH

This is a common source of confusion:

```
Current state of user 42:
  {"name": "Alice", "email": "alice@ex.com", "age": 30}

PUT /users/42 with body {"name": "Alice Smith"}
  Result: {"name": "Alice Smith"}
  --> email and age are GONE! PUT replaces the entire resource.

PATCH /users/42 with body {"name": "Alice Smith"}
  Result: {"name": "Alice Smith", "email": "alice@ex.com", "age": 30}
  --> Only name changed. Other fields preserved.
```

---

## 10.3 HTTP Status Codes

Status codes tell the client what happened. Using them correctly eliminates ambiguity.

### The Five Categories

```
1xx - Informational (rarely used in APIs)
2xx - Success
3xx - Redirection
4xx - Client Error (the client did something wrong)
5xx - Server Error (the server failed)
```

### Essential Status Codes for APIs

```
SUCCESS CODES:
+------+---------------------+---------------------------------------+
| Code | Name                | When to Use                           |
+------+---------------------+---------------------------------------+
| 200  | OK                  | Successful GET, PUT, PATCH, DELETE    |
| 201  | Created             | Successful POST that created a        |
|      |                     | resource. Include Location header.    |
| 204  | No Content          | Successful DELETE with no response    |
|      |                     | body                                  |
+------+---------------------+---------------------------------------+

CLIENT ERROR CODES:
+------+---------------------+---------------------------------------+
| 400  | Bad Request         | Malformed request, invalid JSON,      |
|      |                     | missing required fields                |
| 401  | Unauthorized        | No authentication provided or         |
|      |                     | invalid credentials                    |
| 403  | Forbidden           | Authenticated but not authorized      |
|      |                     | for this resource                      |
| 404  | Not Found           | Resource does not exist                |
| 405  | Method Not Allowed  | POST to a read-only endpoint           |
| 409  | Conflict            | Resource state conflict (e.g.,         |
|      |                     | duplicate email)                       |
| 422  | Unprocessable Entity| Valid JSON but semantically invalid    |
|      |                     | (e.g., age = -5)                       |
| 429  | Too Many Requests   | Rate limit exceeded                    |
+------+---------------------+---------------------------------------+

SERVER ERROR CODES:
+------+---------------------+---------------------------------------+
| 500  | Internal Server Err | Unexpected server failure              |
| 502  | Bad Gateway         | Upstream service returned bad response |
| 503  | Service Unavailable | Server is overloaded or in maintenance |
| 504  | Gateway Timeout     | Upstream service timed out             |
+------+---------------------+---------------------------------------+
```

### Error Response Format

Always return structured error responses. Never return a bare string or an empty body.

```
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      },
      {
        "field": "age",
        "message": "Must be a positive integer"
      }
    ]
  }
}
```

---

## 10.4 API Versioning

APIs evolve. You need to make breaking changes without breaking existing clients. Versioning gives you that safety.

### Versioning Strategies

**1. URL Path Versioning (most common)**

```
GET /v1/users/42
GET /v2/users/42

Pros: Simple, visible, easy to route
Cons: Not truly RESTful (version is not a resource)
Used by: Twitter, Stripe, GitHub (partially)
```

**2. Query Parameter Versioning**

```
GET /users/42?version=1
GET /users/42?version=2

Pros: Clean URLs, optional parameter
Cons: Easy to forget, harder to route
Used by: Google APIs (some)
```

**3. Header Versioning**

```
GET /users/42
Accept: application/vnd.myapi.v1+json

GET /users/42
Accept: application/vnd.myapi.v2+json

Pros: Clean URLs, proper content negotiation
Cons: Not visible in URL, harder to test in browser
Used by: GitHub API
```

**4. No Versioning (evolve carefully)**

```
Add new fields without removing old ones.
Make new fields optional.
Deprecate old fields gradually.

Pros: Simplest, no version management
Cons: Limits the changes you can make
Used by: Slack API (partially)
```

### Versioning Best Practices

```
+--------------------------------------+----------------------------+
| Practice                             | Why                        |
+--------------------------------------+----------------------------+
| Use URL versioning (v1, v2) unless   | Simplest for most teams    |
| you have a strong reason not to      |                            |
+--------------------------------------+----------------------------+
| Support at least 2 versions          | Give clients time to       |
| simultaneously                       | migrate                    |
+--------------------------------------+----------------------------+
| Announce deprecation early           | 6-12 months notice is      |
| (sunset headers)                     | standard                   |
+--------------------------------------+----------------------------+
| Version major changes only           | Adding a new optional field|
| (breaking changes)                   | does not need a new version|
+--------------------------------------+----------------------------+
```

---

## 10.5 Pagination

When a resource has many items (thousands of users, millions of orders), you cannot return them all in one response. Pagination breaks the result into manageable pages.

### Offset-Based Pagination

The simplest approach. Client specifies `offset` (skip N items) and `limit` (return M items).

```
OFFSET-BASED PAGINATION:

  GET /users?offset=0&limit=20    --> Items 1-20
  GET /users?offset=20&limit=20   --> Items 21-40
  GET /users?offset=40&limit=20   --> Items 41-60

  Response:
  {
    "data": [...],
    "pagination": {
      "offset": 20,
      "limit": 20,
      "total": 1000
    }
  }

  Database query: SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 20;
```

**Pros:**
- Simple to implement
- Client can jump to any page
- Total count is easy to provide

**Cons:**
- Slow for large offsets (OFFSET 1000000 must scan 1 million rows)
- Inconsistent results if data changes between pages (items can be skipped or duplicated)

### Cursor-Based Pagination

Client provides a cursor (usually the ID or timestamp of the last item seen). The server returns items after that cursor.

```
CURSOR-BASED PAGINATION:

  GET /users?limit=20
  --> Returns items 1-20, cursor="user_20"

  GET /users?limit=20&after=user_20
  --> Returns items 21-40, cursor="user_40"

  GET /users?limit=20&after=user_40
  --> Returns items 41-60, cursor="user_60"

  Response:
  {
    "data": [...],
    "pagination": {
      "next_cursor": "eyJpZCI6IDQwfQ==",
      "has_more": true
    }
  }

  Database query:
  SELECT * FROM users WHERE id > 40 ORDER BY id LIMIT 20;
  (Uses index, fast regardless of position!)
```

**Pros:**
- Consistent performance regardless of position (no large OFFSET)
- Stable results even if data changes between pages
- Better for infinite scroll UIs

**Cons:**
- Cannot jump to arbitrary pages ("show me page 50")
- More complex to implement
- Cursor must encode the sort order

### Comparison

```
+--------------------+-----------------+------------------+
| Feature            | Offset-Based    | Cursor-Based     |
+--------------------+-----------------+------------------+
| Performance at     | Degrades with   | Constant         |
| large offsets      | offset size     |                  |
+--------------------+-----------------+------------------+
| Jump to page N     | Yes             | No               |
+--------------------+-----------------+------------------+
| Data consistency   | Items can shift | Stable           |
| between pages      |                 |                  |
+--------------------+-----------------+------------------+
| Implementation     | Simple          | More complex     |
+--------------------+-----------------+------------------+
| Best for           | Small datasets, | Large datasets,  |
|                    | admin panels    | feeds, timelines |
+--------------------+-----------------+------------------+
```

---

## 10.6 Filtering, Sorting, and Searching

### Filtering

Allow clients to narrow results using query parameters:

```
GET /products?category=electronics
GET /products?category=electronics&price_min=100&price_max=500
GET /products?status=active&created_after=2024-01-01
GET /orders?user_id=42&status=shipped
```

### Sorting

Allow clients to control the order of results:

```
GET /products?sort=price           --> Ascending by price
GET /products?sort=-price          --> Descending by price (minus prefix)
GET /products?sort=category,-price --> By category asc, then price desc
```

### Searching

For full-text search, use a dedicated query parameter:

```
GET /products?q=wireless+keyboard
GET /users?search=alice
```

### Combined Example

```
GET /products?category=electronics&price_min=50&sort=-rating&limit=20

Translation: "Give me the top 20 electronics over $50,
              sorted by rating (highest first)"
```

---

## 10.7 Rate Limiting Headers

Rate limiting protects your API from abuse (see Chapter 11 for algorithms). The API communicates rate limits to clients through HTTP headers.

```
RATE LIMIT HEADERS:

HTTP/1.1 200 OK
X-RateLimit-Limit: 100          <-- Max requests allowed per window
X-RateLimit-Remaining: 73       <-- Requests remaining in current window
X-RateLimit-Reset: 1672531200   <-- Unix timestamp when window resets

When exceeded:
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1672531200
Retry-After: 30                 <-- Seconds to wait before retrying

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 30 seconds."
  }
}
```

### Rate Limit Tiers

```
+------------------+---------+---------+--------------------+
| Tier             | Limit   | Window  | Who                |
+------------------+---------+---------+--------------------+
| Free             | 60/hr   | 1 hour  | Unauthenticated    |
| Basic            | 1000/hr | 1 hour  | Free tier users    |
| Pro              | 10000/hr| 1 hour  | Paid users         |
| Enterprise       | Custom  | Custom  | Contract customers |
+------------------+---------+---------+--------------------+
```

---

## 10.8 Idempotency

An operation is **idempotent** if performing it multiple times has the same effect as performing it once.

### Why Idempotency Matters

Network failures happen. When a client sends a request and does not get a response, it does not know if the server processed it or not. The safe thing is to retry. But if the operation is not idempotent, retrying can cause problems.

```
WITHOUT IDEMPOTENCY:

  Client: POST /payments  {"amount": 100, "to": "Bob"}
  Server: Processes payment, but response is lost in network
  Client: No response received. Retry!
  Client: POST /payments  {"amount": 100, "to": "Bob"}
  Server: Processes payment AGAIN.

  Result: Bob received $200 instead of $100!


WITH IDEMPOTENCY:

  Client: POST /payments  {"amount": 100, "to": "Bob"}
          Header: Idempotency-Key: "abc-123"
  Server: Processes payment, stores result with key "abc-123"
          Response lost in network
  Client: No response received. Retry!
  Client: POST /payments  {"amount": 100, "to": "Bob"}
          Header: Idempotency-Key: "abc-123"
  Server: Sees key "abc-123" already processed.
          Returns the original result without processing again.

  Result: Bob received exactly $100. Correct!
```

### Idempotency by HTTP Method

```
+--------+-----------+---------------------------------------+
| Method | Idempotent| Explanation                           |
+--------+-----------+---------------------------------------+
| GET    | Yes       | Reading does not change state          |
| PUT    | Yes       | Replacing with same data = same result|
| DELETE | Yes       | Deleting twice = still deleted         |
| POST   | No        | Creating twice = two resources         |
| PATCH  | Maybe     | Depends on the operation               |
+--------+-----------+---------------------------------------+

POST is the dangerous one. Use idempotency keys for
POST requests that must not be duplicated (payments,
order placements, account creation).
```

### Implementing Idempotency Keys

```
IDEMPOTENCY KEY FLOW:

  +--------+                    +--------+           +---------+
  | Client |                    | Server |           | ID Key  |
  |        |                    |        |           | Store   |
  +---+----+                    +---+----+           +----+----+
      |                             |                     |
      | POST /orders                |                     |
      | Idempotency-Key: xyz-789    |                     |
      |---------------------------->|                     |
      |                             | Check key "xyz-789" |
      |                             |-------------------->|
      |                             |   Not found         |
      |                             |<--------------------|
      |                             |                     |
      |                             | Process order       |
      |                             | Store result        |
      |                             |  with key "xyz-789" |
      |                             |-------------------->|
      |   201 Created               |                     |
      |<----------------------------|                     |
      |                             |                     |
      | RETRY (same key)            |                     |
      | POST /orders                |                     |
      | Idempotency-Key: xyz-789    |                     |
      |---------------------------->|                     |
      |                             | Check key "xyz-789" |
      |                             |-------------------->|
      |                             |   Found! Return     |
      |                             |   stored result     |
      |                             |<--------------------|
      |   201 Created (same result) |                     |
      |<----------------------------|                     |
```

---

## 10.9 Authentication and Authorization

### API Keys

The simplest authentication method. The client includes a secret key with each request.

```
GET /users
Authorization: ApiKey sk_live_abc123def456

Or in a custom header:
X-API-Key: sk_live_abc123def456
```

**Pros:** Simple to implement and use
**Cons:** If leaked, anyone can use it. No user context (key represents an app, not a user).

**Best for:** Server-to-server communication, public APIs with rate limiting

### OAuth 2.0

A protocol that lets users grant third-party apps limited access to their resources without sharing passwords.

```
OAUTH 2.0 FLOW (Authorization Code):

  +------+     +--------+     +-----------+     +----------+
  | User |     | Client |     | Auth      |     | Resource |
  |      |     | (App)  |     | Server    |     | Server   |
  +--+---+     +---+----+     +-----+-----+     +----+-----+
     |             |                |                  |
     | 1. Click    |                |                  |
     | "Login with |                |                  |
     |  Google"    |                |                  |
     |------------>|                |                  |
     |             |                |                  |
     |             | 2. Redirect to |                  |
     |             |    auth server |                  |
     |<------------|                |                  |
     |             |                |                  |
     | 3. User logs in and         |                  |
     |    approves access          |                  |
     |--------------------------->|                  |
     |             |                |                  |
     |             | 4. Auth code   |                  |
     |             |<---------------|                  |
     |             |                |                  |
     |             | 5. Exchange    |                  |
     |             |  code for token|                  |
     |             |--------------->|                  |
     |             |                |                  |
     |             | 6. Access token|                  |
     |             |<---------------|                  |
     |             |                |                  |
     |             | 7. Use token   |                  |
     |             |  to access API |                  |
     |             |---------------------------------->|
     |             |                |                  |
     |             | 8. Protected   |                  |
     |             |    resource    |                  |
     |             |<----------------------------------|
```

**Best for:** When users authorize third-party access to their data (social logins, API integrations)

### JWT (JSON Web Tokens)

A compact, self-contained token that encodes user information and is signed to prevent tampering.

```
JWT STRUCTURE:

  Header.Payload.Signature

  Header:   {"alg": "HS256", "typ": "JWT"}
  Payload:  {"user_id": 42, "role": "admin", "exp": 1672531200}
  Signature: HMAC-SHA256(header + "." + payload, secret_key)

  Encoded:
  eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo0Mn0.abc123signature

  Usage:
  GET /users
  Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...


  +--------+                     +--------+
  | Client |                     | Server |
  +---+----+                     +---+----+
      |                              |
      | POST /login                  |
      | {"email":"a@b.c","pass":"x"} |
      |----------------------------->|
      |                              | Verify credentials
      |                              | Generate JWT
      |   {"token": "eyJ..."}       |
      |<-----------------------------|
      |                              |
      | GET /users                   |
      | Authorization: Bearer eyJ... |
      |----------------------------->|
      |                              | Verify JWT signature
      |                              | Extract user_id from payload
      |                              | (No database lookup needed!)
      |   200 OK                     |
      |<-----------------------------|
```

**Pros:** Stateless (server does not need to store sessions), contains user info
**Cons:** Cannot be revoked before expiry (unless you add a blacklist), size grows with claims

### Comparison

```
+------------------+----------+-----------+----------+
| Feature          | API Keys | OAuth 2.0 | JWT      |
+------------------+----------+-----------+----------+
| Complexity       | Low      | High      | Medium   |
| User context     | No       | Yes       | Yes      |
| Revocable        | Yes      | Yes       | Hard*    |
| Stateless        | Yes      | No**      | Yes      |
| Best for         | Server-  | Third-    | Stateless|
|                  | to-server| party     | auth in  |
|                  |          | access    | your APIs|
+------------------+----------+-----------+----------+

*  JWT requires blacklist or short expiry + refresh tokens
** OAuth requires storing tokens server-side
```

---

## 10.10 GraphQL vs REST vs gRPC

REST is not the only API style. Here are the three major approaches and when to choose each.

### REST

```
REST API:

  GET /users/42           --> Get user
  GET /users/42/orders    --> Get user's orders
  GET /orders/7/items     --> Get order items

  Problems:
  1. Over-fetching: GET /users/42 returns ALL fields,
     even if you only need the name.

  2. Under-fetching: To show a user's profile page, you
     need 3 separate requests (user, orders, reviews).

  3. Multiple round trips:
     Client --> GET /users/42
     Client --> GET /users/42/orders
     Client --> GET /users/42/reviews
     (3 network round trips!)
```

### GraphQL

GraphQL lets the client specify exactly what data it needs in a single request.

```
GRAPHQL:

  Single request, client specifies the shape:

  POST /graphql
  {
    query {
      user(id: 42) {
        name
        email
        orders(last: 5) {
          id
          total
          items {
            name
            price
          }
        }
      }
    }
  }

  Response matches the query shape exactly:
  {
    "data": {
      "user": {
        "name": "Alice",
        "email": "alice@ex.com",
        "orders": [
          {
            "id": 1,
            "total": 129.99,
            "items": [
              {"name": "Laptop Stand", "price": 49.99},
              {"name": "USB Hub", "price": 29.99}
            ]
          }
        ]
      }
    }
  }

  One request, exactly the data needed. No over-fetching,
  no under-fetching.
```

### gRPC

gRPC uses Protocol Buffers (protobuf) for binary serialization and HTTP/2 for transport. It is much faster than JSON-based REST.

```
gRPC:

  1. Define service in .proto file:

     service UserService {
       rpc GetUser (UserRequest) returns (UserResponse);
       rpc ListUsers (ListRequest) returns (stream UserResponse);
     }

     message UserRequest {
       int32 id = 1;
     }

     message UserResponse {
       int32 id = 1;
       string name = 2;
       string email = 3;
     }

  2. Generate client and server code from .proto
  3. Call methods like local functions:

     user = client.GetUser(UserRequest(id=42))
     print(user.name)  // "Alice"

  Features:
  - Binary protocol (smaller, faster than JSON)
  - HTTP/2 (multiplexing, streaming)
  - Bi-directional streaming
  - Strong typing (code generation from .proto)
```

### Comparison

```
+-------------------+-------------+-------------+-------------+
| Feature           | REST        | GraphQL     | gRPC        |
+-------------------+-------------+-------------+-------------+
| Protocol          | HTTP/1.1    | HTTP/1.1    | HTTP/2      |
| Data format       | JSON        | JSON        | Protobuf    |
|                   |             |             | (binary)    |
+-------------------+-------------+-------------+-------------+
| Fetching          | Fixed       | Client      | Fixed       |
|                   | response    | specifies   | response    |
|                   | shape       | shape       | shape       |
+-------------------+-------------+-------------+-------------+
| Performance       | Good        | Good        | Excellent   |
+-------------------+-------------+-------------+-------------+
| Browser support   | Native      | Via library | Limited*    |
+-------------------+-------------+-------------+-------------+
| Streaming         | Limited     | Subscriptions| Native     |
+-------------------+-------------+-------------+-------------+
| Learning curve    | Low         | Medium      | Medium-High |
+-------------------+-------------+-------------+-------------+
| Caching           | HTTP caching| Complex     | Not built-in|
|                   | built-in    | (POST-based)|             |
+-------------------+-------------+-------------+-------------+
| Best for          | Public APIs,| Mobile apps,| Microservice|
|                   | CRUD apps   | complex UIs | to micro-   |
|                   |             |             | service     |
+-------------------+-------------+-------------+-------------+

* gRPC-Web adds browser support, but it is not native
```

### When to Choose Which

```
Choose REST when:
  - Building a public API consumed by third parties
  - Your resources map cleanly to CRUD operations
  - You want maximum compatibility (any HTTP client works)
  - HTTP caching is important

Choose GraphQL when:
  - Your frontend needs flexible, nested data
  - Mobile apps need to minimize data transfer
  - You have many client types with different data needs
  - You want to avoid managing many endpoint versions

Choose gRPC when:
  - You have internal service-to-service communication
  - You need high performance and low latency
  - You need bi-directional streaming
  - You want strong typing and code generation
```

---

## 10.11 OpenAPI (Swagger)

OpenAPI is a specification for describing REST APIs. It produces machine-readable API documentation that can generate client libraries, server stubs, and interactive documentation.

```
OPENAPI EXAMPLE (YAML):

  openapi: "3.0.0"
  info:
    title: User API
    version: "1.0"
  paths:
    /users/{id}:
      get:
        summary: Get a user by ID
        parameters:
          - name: id
            in: path
            required: true
            schema:
              type: integer
        responses:
          "200":
            description: User found
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    email:
                      type: string
          "404":
            description: User not found


OPENAPI TOOLING:

  +------------------+     +-----------------------+
  | OpenAPI Spec     |---->| Swagger UI            |
  | (YAML/JSON)      |     | (interactive docs)    |
  +------------------+     +-----------------------+
          |
          +--------------->+-----------------------+
          |                | Client SDK Generator  |
          |                | (Python, JS, Java...) |
          |                +-----------------------+
          |
          +--------------->+-----------------------+
                           | Server Stub Generator |
                           | (Spring, Express...)  |
                           +-----------------------+
```

---

## Common Mistakes

1. **Using verbs in URLs.** `/getUser/42` should be `GET /users/42`. The HTTP method is the verb.

2. **Returning 200 for errors.** If something failed, use a 4xx or 5xx status code. Returning 200 with `{"error": "not found"}` breaks HTTP conventions and caching.

3. **Not paginating list endpoints.** Returning 10,000 items in one response is slow and wasteful. Always paginate.

4. **Breaking changes without versioning.** Removing a field or changing a response structure breaks existing clients. Version your API or use additive changes only.

5. **Inconsistent naming.** If one endpoint uses `userId` and another uses `user_id`, your API is confusing. Pick one convention and stick to it.

6. **No rate limiting.** Without rate limits, a single misbehaving client can take down your API. Always implement rate limiting.

7. **Overly nested URLs.** `/companies/1/departments/2/teams/3/members/4` is hard to use. Flatten where possible: `/members/4?team_id=3`.

8. **Not using idempotency keys for critical operations.** Payment processing, order creation, and other non-idempotent operations need idempotency keys.

---

## Best Practices

1. **Use consistent, predictable naming.** Plural nouns, lowercase, hyphens. Follow one convention everywhere.

2. **Return meaningful error responses.** Include an error code, human-readable message, and field-level details.

3. **Always paginate list endpoints.** Default to a reasonable page size (20-50 items) with a maximum limit.

4. **Use cursor-based pagination for large datasets.** Offset-based is fine for small, admin-facing datasets.

5. **Version your API from day one.** Even if you only have `v1`, it sets the pattern.

6. **Document your API with OpenAPI.** Auto-generated documentation stays in sync with your code.

7. **Use HTTPS everywhere.** Never serve an API over plain HTTP.

8. **Implement idempotency keys for POST requests that create resources.** Especially for financial operations.

9. **Set rate limits and communicate them via headers.** Clients should know their limits before hitting them.

10. **Design for backwards compatibility.** Add new fields, do not remove old ones. Mark deprecated fields clearly.

---

## Quick Summary

API design is about creating clear, consistent, predictable interfaces. REST uses HTTP methods (GET, POST, PUT, PATCH, DELETE) on resource-oriented URLs. Status codes communicate outcomes (2xx success, 4xx client error, 5xx server error). APIs should be versioned (URL path is simplest), paginated (cursor-based for large datasets), and protected with rate limiting. Idempotency keys prevent duplicate operations from network retries. Authentication options include API keys (simple), OAuth 2.0 (third-party access), and JWT (stateless auth). GraphQL lets clients request exactly the data they need. gRPC uses binary protobuf for high-performance service-to-service communication. OpenAPI provides machine-readable documentation. The best API is one that developers can use correctly without reading documentation.

---

## Key Points

- Use resource-oriented URLs with HTTP methods as verbs: GET /users/42, not GET /getUser?id=42
- Return appropriate status codes: 201 for creation, 404 for not found, 429 for rate limiting
- Version your API from the start -- URL path versioning (/v1/) is the simplest approach
- Use cursor-based pagination for large datasets; offset-based for small ones
- Implement idempotency keys for non-idempotent operations to handle retries safely
- Choose REST for public APIs, GraphQL for flexible client needs, gRPC for internal services
- Always rate limit your API and communicate limits through response headers
- Document with OpenAPI to keep documentation in sync with implementation

---

## Practice Questions

1. You are designing an API for a ride-sharing app. Define the REST endpoints for: requesting a ride, tracking a ride in progress, completing a ride, and rating a driver. Include HTTP methods, URLs, request bodies, and response codes.

2. A client reports that they were charged twice for the same order. Explain how idempotency keys could have prevented this. Design the implementation, including key storage, expiration, and race condition handling.

3. Your API serves both a mobile app (needs minimal data, slow network) and an admin dashboard (needs full data, fast network). Compare how you would handle this with REST (multiple endpoints or field selection) vs GraphQL. Which approach would you recommend and why?

4. You have an endpoint `GET /products` that returns 2 million products. A client complains that fetching page 50,000 is extremely slow. Explain why offset-based pagination causes this and how cursor-based pagination solves it.

5. Compare API keys, OAuth 2.0, and JWT for a SaaS platform that needs to support both first-party mobile apps and third-party developer integrations. Which authentication method(s) would you use for each, and why?

---

## Exercises

**Exercise 1: Design a REST API**
Design a complete REST API for a blog platform. Define endpoints for: users, posts, comments, and tags. For each endpoint, specify: HTTP method, URL, request body (if applicable), response body, and status codes. Include pagination, filtering by author, and sorting by date.

**Exercise 2: Idempotency Implementation**
Write pseudocode for an idempotency middleware that: (a) checks for an Idempotency-Key header on POST requests, (b) returns the cached result if the key was seen before, (c) processes the request and stores the result if the key is new, (d) handles race conditions when two requests with the same key arrive simultaneously.

**Exercise 3: API Comparison**
Take one feature from a real API you use (e.g., creating a tweet, placing an order). Design the interface three ways: REST, GraphQL, and gRPC (using proto definitions). Compare them on: number of round trips, data transferred, type safety, and ease of implementation.

---

## What Is Next?

You now know how to design clean, reliable APIs. But how do you protect those APIs from being overwhelmed by too many requests? In Chapter 11, you will learn about rate limiting -- the algorithms, strategies, and implementations that keep your API healthy under heavy load. Rate limiting is one of the most common system design topics in interviews and a critical component of any production API.
