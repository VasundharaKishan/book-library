# Chapter 14: Microservices

## What You Will Learn

- What microservices are and how they differ from monolithic architecture
- The benefits of microservices: independent deployment, scaling, and technology diversity
- The challenges: network complexity, data consistency, and debugging difficulty
- How to define service boundaries using bounded contexts from Domain-Driven Design
- Synchronous vs asynchronous inter-service communication (REST, gRPC, message queues)
- What a service mesh is and how the sidecar pattern works
- When a monolith is actually the better choice

## Why This Chapter Matters

Microservices are one of the most discussed topics in modern software engineering. Companies like Netflix, Amazon, and Uber have built their platforms on microservices. But microservices are not free. They trade one set of problems (big codebase, slow deployments) for another (network failures, distributed debugging, data inconsistency).

If you adopt microservices without understanding the trade-offs, you will build a distributed monolith — all the complexity of microservices with none of the benefits. This chapter gives you the knowledge to make that decision wisely.

---

## Monolith vs Microservices: The Big Picture

### The Monolith: One Big Building

A monolithic application is a single deployable unit. All features live in one codebase, one process, one deployment.

Think of it as one large office building. Everyone works under the same roof. The accounting department, engineering, sales, and customer support all share the same hallways, the same cafeteria, and the same elevator.

```
+----------------------------------------------------------+
|                    MONOLITH APPLICATION                    |
|                                                          |
|  +----------+  +----------+  +---------+  +----------+  |
|  |  User    |  |  Order   |  | Payment |  | Shipping |  |
|  |  Module  |  |  Module  |  | Module  |  | Module   |  |
|  +----+-----+  +----+-----+  +----+----+  +----+-----+  |
|       |             |             |             |        |
|  +----+-------------+-------------+-------------+----+   |
|  |              Shared Database                      |   |
|  +---------------------------------------------------+   |
|                                                          |
|  Single Codebase | Single Deployment | Single Process    |
+----------------------------------------------------------+
```

### Microservices: Separate Houses

A microservices architecture breaks the application into small, independent services. Each service owns its data, runs in its own process, and communicates with others over the network.

Think of it as a neighborhood of houses. Each house is independent. It has its own plumbing, its own electricity, and its own mailbox. Residents communicate by sending letters or making phone calls.

```
+------------+    +------------+    +------------+    +------------+
|  User      |    |  Order     |    |  Payment   |    |  Shipping  |
|  Service   |    |  Service   |    |  Service   |    |  Service   |
|            |    |            |    |            |    |            |
| +--------+ |    | +--------+ |    | +--------+ |    | +--------+ |
| |  Own   | |    | |  Own   | |    | |  Own   | |    | |  Own   | |
| |  DB    | |    | |  DB    | |    | |  DB    | |    | |  DB    | |
| +--------+ |    | +--------+ |    | +--------+ |    | +--------+ |
+------+-----+    +------+-----+    +------+-----+    +------+-----+
       |                |                |                |
       +--------+-------+--------+-------+--------+------+
                |                |                |
         +------+------+  +-----+------+  +------+------+
         |   REST API  |  |  gRPC      |  | Message     |
         |   Calls     |  |  Calls     |  | Queue       |
         +-------------+  +------------+  +-------------+

  Each service: own codebase, own database, own deployment
```

---

## Benefits of Microservices

### 1. Independent Deployment

Each service can be deployed independently. The payment team can ship a fix at 2 PM without waiting for the shipping team to finish their feature. No coordinated releases. No "deployment trains."

```
  Monolith Deployment          Microservices Deployment

  All teams must              Each team deploys
  deploy together:            independently:

  +-----------+               +------+  +------+  +------+
  | User      |               | User |  | Order|  | Pay  |
  | Order     |  --> Deploy   |      |  |      |  |      |
  | Payment   |     ALL       | v2.1 |  | v3.0 |  | v1.5 |
  | Shipping  |               +------+  +------+  +------+
  +-----------+                  |          |         |
                              Deploy     Deploy    Deploy
                              Mon 2pm   Tue 10am  Wed 4pm
```

### 2. Independent Scaling

If your search service gets 100x more traffic than your payment service, you can scale search independently. No need to scale the entire application.

```
  Scaling a Monolith           Scaling Microservices

  Must scale everything:       Scale only what needs it:

  +-------+ +-------+         +---+ +---+ +---+ +---+ +---+
  | ALL   | | ALL   |         | S | | S | | S | | S | | S |  <-- 5 search
  | code  | | code  |         +---+ +---+ +---+ +---+ +---+     instances
  +-------+ +-------+
                               +---+                           <-- 1 payment
  2 full copies                | P |                              instance
  (wasteful)                   +---+
```

### 3. Technology Diversity

Each team can pick the best technology for their service. The search team can use Elasticsearch. The payment team can use a relational database. The analytics team can use Python while everyone else uses Java.

### 4. Fault Isolation

If the recommendation service crashes, the rest of the application keeps running. Users can still browse, search, and purchase. In a monolith, one bad module can bring down the entire application.

### 5. Team Autonomy

Small teams (2-pizza teams, as Amazon calls them) own their services end to end. They make their own technology choices, set their own release schedules, and are responsible for their own operations.

---

## Challenges of Microservices

### 1. Network Complexity

In a monolith, function calls are local and fast. In microservices, they become network calls that can fail, time out, or be slow. Every call between services is a potential point of failure.

```
  Monolith: In-Process Call     Microservices: Network Call

  orderService.create(order)    POST http://order-service/orders

  - Always succeeds              - Can time out
  - Nanoseconds                  - Milliseconds
  - No serialization             - JSON/Protobuf serialization
  - No network issues            - Network can fail
  - Type-safe                    - Schema mismatch possible
```

### 2. Data Consistency

In a monolith, you can use a database transaction to update multiple tables atomically. In microservices, each service has its own database. There are no cross-service transactions.

```
  Monolith: Single Transaction

  BEGIN TRANSACTION
    UPDATE orders SET status = 'confirmed'
    UPDATE inventory SET quantity = quantity - 1
    UPDATE payments SET status = 'charged'
  COMMIT

  ------------------------------------------

  Microservices: Distributed Operations

  Order Service:    "Order confirmed"    --> Success
  Inventory Service: "Reduce stock"      --> Success
  Payment Service:   "Charge customer"   --> FAILED!

  Now what? Order is confirmed, stock is reduced,
  but payment failed. You need a saga pattern or
  compensation logic to undo the partial work.
```

### 3. Debugging Difficulty

A single user request might touch 10 different services. When something goes wrong, you need distributed tracing to follow the request across services. Logs are spread across dozens of machines.

```
  User Request: "Place Order"

  API Gateway --> User Service --> Order Service --> Inventory Service
                                       |
                                       +--> Payment Service
                                       |
                                       +--> Notification Service
                                       |
                                       +--> Shipping Service

  Where did the request fail? Which service was slow?
  You need distributed tracing (Chapter 20) to find out.
```

### 4. Operational Overhead

Instead of deploying one application, you now deploy 50. Each needs monitoring, logging, health checks, CI/CD pipelines, and on-call rotations. The infrastructure cost is significant.

### 5. Testing Complexity

Integration testing becomes harder. How do you test that the order service works correctly with the payment service, the inventory service, and the shipping service — all together?

---

## Defining Service Boundaries

The hardest part of microservices is deciding where to draw the lines. If you split too fine, you get "nanoservices" — services so small that they cannot do anything useful without calling other services. If you split too coarse, you get a distributed monolith.

### Bounded Contexts from Domain-Driven Design (DDD)

Domain-Driven Design gives us the concept of **bounded contexts**. A bounded context is a boundary within which a particular model is defined and applicable.

Think of it this way: the word "account" means different things in different parts of a business.

- In **User Management**, an account is a login with email and password.
- In **Billing**, an account is a payment profile with credit card and invoices.
- In **Analytics**, an account is a set of usage metrics and behavior data.

Each of these is a separate bounded context, and each could be a separate microservice.

```
  Bounded Contexts for an E-Commerce System

  +-------------------+  +-------------------+  +-------------------+
  |  User Context     |  |  Order Context    |  |  Payment Context  |
  |                   |  |                   |  |                   |
  |  - User profile   |  |  - Order          |  |  - Payment method |
  |  - Authentication |  |  - Order items    |  |  - Transaction    |
  |  - Preferences    |  |  - Order status   |  |  - Invoice        |
  |                   |  |                   |  |  - Refund          |
  |  "Account" =      |  |  "Account" =      |  |  "Account" =      |
  |  login + email    |  |  customer who      |  |  payment profile  |
  |                   |  |  placed orders     |  |                   |
  +-------------------+  +-------------------+  +-------------------+
         |                       |                       |
         +--- User Service -----+--- Order Service -----+--- Payment Service
```

### Guidelines for Drawing Boundaries

1. **High cohesion within a service**: Things that change together should live together.
2. **Low coupling between services**: Changing one service should rarely require changing another.
3. **Align with team structure**: Each service should be owned by a single team (Conway's Law).
4. **One service, one business capability**: A service should map to a business function, not a technical layer.

---

## Inter-Service Communication

### Synchronous Communication

The calling service sends a request and waits for a response.

#### REST (HTTP/JSON)

The most common approach. Simple, well-understood, works with any language.

```
  Order Service                    Payment Service
  +-------------+                  +-------------+
  |             |  POST /payments  |             |
  |  Create     | ---------------> |  Charge     |
  |  Order      | <--------------- |  Customer   |
  |             |  200 OK          |             |
  +-------------+  {txn_id: 123}   +-------------+

  Pros: Simple, widely supported, human-readable
  Cons: Coupled, latency adds up, both must be online
```

#### gRPC (Protocol Buffers)

A high-performance RPC framework from Google. Uses binary serialization (Protocol Buffers) instead of JSON. Supports streaming.

```
  Order Service                    Payment Service
  +-------------+                  +-------------+
  |             | ChargeCustomer() |             |
  |  Create     | ---------------> |  Charge     |
  |  Order      | <--------------- |  Customer   |
  |             | PaymentResponse  |             |
  +-------------+  (binary)        +-------------+

  Pros: Fast (binary), type-safe (schema), streaming support
  Cons: Not human-readable, requires code generation
```

### Asynchronous Communication

The calling service sends a message and moves on. It does not wait for a response.

#### Message Queue

Services communicate through a message broker (RabbitMQ, Amazon SQS, Kafka).

```
  Order Service         Message Queue          Payment Service
  +-------------+      +-------------+         +-------------+
  |             | ---> |  [Message]   | ------> |             |
  |  Create     |      |  [Message]   |         |  Process    |
  |  Order      |      |  [Message]   |         |  Payment    |
  |             |      +-------------+          |             |
  +-------------+                               +-------------+
       |
       v
  Returns immediately
  (does not wait for payment)

  Pros: Decoupled, resilient (queue buffers messages), scalable
  Cons: Eventual consistency, harder to debug, no immediate response
```

### When to Use Each

```
  Use Synchronous When:               Use Asynchronous When:

  - You need an immediate response    - You can tolerate delay
  - The operation is fast             - The operation is slow
  - Failure should be visible         - Retries are acceptable
  - Simple request/response           - Fan-out to many services

  Examples:                           Examples:
  - Get user profile                  - Send notification email
  - Check inventory                   - Process payment (background)
  - Authenticate user                 - Generate report
                                      - Update search index
```

---

## Service Mesh and the Sidecar Pattern

As you add more microservices, cross-cutting concerns like load balancing, retries, circuit breaking, authentication, and observability become repetitive. Every service needs the same infrastructure code.

A **service mesh** handles these concerns outside of your application code.

### The Sidecar Pattern

Each service gets a **sidecar proxy** — a small process that runs alongside it and handles all network communication.

```
  Without Service Mesh               With Service Mesh (Sidecar)

  +------------------+               +------------------+--------+
  | Order Service    |               | Order Service    | Sidecar|
  |                  |               |                  | Proxy  |
  | - Business logic |               | - Business logic | - TLS  |
  | - Retry logic    |               |                  | - Retry|
  | - Circuit breaker|               |                  | - Auth |
  | - TLS            |               |                  | - Trace|
  | - Auth           |               |                  | - Load |
  | - Tracing        |               |                  |   Bal. |
  | - Load balancing |               |                  |        |
  +------------------+               +------------------+--------+
                                            |
  All infrastructure code                   | Network calls go
  mixed with business logic                 | through the sidecar
```

### How a Service Mesh Works

```
  +--------+-------+          +--------+-------+
  | Service A      |          | Service B      |
  | +------------+ |          | +------------+ |
  | | App Code   | |          | | App Code   | |
  | +-----+------+ |          | +-----+------+ |
  |       |        |          |       ^        |
  | +-----v------+ |          | +-----+------+ |
  | | Sidecar    | | -------> | | Sidecar    | |
  | | (Envoy)    | |  mTLS    | | (Envoy)    | |
  | +------------+ |          | +------------+ |
  +----------------+          +----------------+
         |                           |
         +----------+----------------+
                    |
            +-------v--------+
            |  Control Plane |
            |  (Istio, etc.) |
            |  - Config      |
            |  - Policies    |
            |  - Routing     |
            +----------------+

  Popular service meshes: Istio, Linkerd, Consul Connect
```

The service mesh has two parts:

1. **Data plane**: The sidecar proxies that handle actual traffic (usually Envoy).
2. **Control plane**: The management layer that configures the proxies (Istio, Linkerd).

---

## When the Monolith Is Better

Microservices are not always the answer. Here are situations where a monolith is the better choice.

### 1. Early-Stage Startups

You are still figuring out what your product is. Service boundaries are unclear. A monolith lets you move fast and refactor easily.

### 2. Small Teams

If you have fewer than 10 engineers, the operational overhead of microservices will slow you down. A well-structured monolith is easier to manage.

### 3. Low Complexity

If your application is a CRUD app with straightforward business logic, microservices add unnecessary complexity.

### 4. Tight Coupling Is Natural

Some domains are inherently tightly coupled. Splitting them into services creates more network calls and coordination without real benefit.

```
  When to Use What

  +-------------------+----------------------------+
  |  Monolith         |  Microservices             |
  +-------------------+----------------------------+
  | Small team (<10)  | Large team (50+)           |
  | New product       | Mature product             |
  | Unclear boundaries| Clear domain boundaries    |
  | Simple domain     | Complex domain             |
  | Speed matters most| Scale matters most         |
  | Single deployment | Independent deployments    |
  +-------------------+----------------------------+

  Start with a monolith. Split when you feel the pain.
```

### The Modular Monolith: A Middle Ground

A **modular monolith** is a single deployment unit with clear internal boundaries. Modules communicate through well-defined interfaces, not direct database access.

```
  +----------------------------------------------------------+
  |                  MODULAR MONOLITH                          |
  |                                                          |
  |  +----------+  +----------+  +---------+  +----------+  |
  |  |  User    |  |  Order   |  | Payment |  | Shipping |  |
  |  |  Module  |  |  Module  |  | Module  |  | Module   |  |
  |  |          |  |          |  |         |  |          |  |
  |  | Own DB   |  | Own DB   |  | Own DB  |  | Own DB   |  |
  |  | schema   |  | schema   |  | schema  |  | schema   |  |
  |  +----+-----+  +----+-----+  +----+----+  +----+-----+  |
  |       |             |             |             |        |
  |  Communication through defined interfaces only           |
  |  (No direct database access across modules)              |
  +----------------------------------------------------------+

  Benefits: Clear boundaries + simple deployment
  Migration: Easy to extract modules into services later
```

---

## Common Mistakes

1. **Starting with microservices on day one.** You do not know your domain well enough. Start with a monolith and split when you understand the boundaries.

2. **Creating a distributed monolith.** If every service must call 5 other services to handle a request, you have not actually decoupled anything. You just made it harder to deploy.

3. **Sharing databases between services.** This creates tight coupling. If two services share a table, changing that table requires coordinating both teams.

4. **Making services too small.** A service that does one tiny thing and always needs to call other services is not a service — it is a function. Keep services at the level of business capabilities.

5. **Ignoring operational requirements.** Microservices need CI/CD, monitoring, logging, tracing, and alerting for every service. Budget for this infrastructure before you start splitting.

6. **Synchronous chains.** Service A calls B, which calls C, which calls D. If any service in the chain is slow or down, the entire request fails. Use async communication where possible.

---

## Best Practices

1. **Start with a well-structured monolith.** Use clear module boundaries from the beginning. This makes future splitting easier.

2. **One service, one database.** Each service owns its data. No sharing tables. If another service needs your data, expose it through an API.

3. **Design for failure.** Every network call can fail. Use circuit breakers, retries with backoff, and timeouts.

4. **Use asynchronous communication for non-critical paths.** Sending a notification email after an order does not need to be synchronous.

5. **Invest in observability early.** Distributed tracing, centralized logging, and health checks are not optional. Build them from the start.

6. **Automate everything.** Each service needs its own CI/CD pipeline, automated tests, and deployment process. Manual processes do not scale with 50 services.

7. **Define API contracts.** Use OpenAPI specs or Protocol Buffer definitions. Version your APIs. Never make breaking changes without a migration path.

---

## Quick Summary

Microservices break a large application into small, independent services that communicate over the network. They enable independent deployment, independent scaling, and technology diversity. But they introduce network complexity, data consistency challenges, and operational overhead. Service boundaries should align with business capabilities using bounded contexts from Domain-Driven Design. Communication can be synchronous (REST, gRPC) or asynchronous (message queues). A service mesh handles cross-cutting concerns like retries, authentication, and tracing. For many teams, a well-structured monolith or modular monolith is the better starting point.

---

## Key Points

- A monolith is a single deployable unit; microservices are many small, independent services.
- Microservices enable independent deployment, scaling, and technology choices per team.
- The main challenges are network failures, data consistency across services, and operational complexity.
- Bounded contexts from DDD help define natural service boundaries.
- Synchronous communication (REST, gRPC) is simpler but creates coupling; asynchronous (message queues) is more resilient.
- A service mesh with sidecar proxies handles cross-cutting concerns outside application code.
- A modular monolith offers clear boundaries without the operational overhead of microservices.
- Start with a monolith and migrate to microservices only when you feel specific pain points.

---

## Practice Questions

1. Your monolith takes 45 minutes to deploy and a bug in the payment module brought down the entire application last week. Should you switch to microservices? What factors would influence your decision?

2. Two teams need to share customer data. Team A owns the User Service and Team B owns the Order Service. How should Team B access customer data without creating tight coupling?

3. The checkout flow in your microservices system involves 6 synchronous service calls in sequence. The 95th percentile latency is 3 seconds. How would you reduce this?

4. Your company has 5 engineers and is building an MVP. A senior engineer insists on using microservices. What counter-arguments would you present?

5. Explain the difference between a distributed monolith and a true microservices architecture. What are the symptoms of a distributed monolith?

---

## Exercises

### Exercise 1: Decompose a Monolith (On Paper)

Take a familiar application (e-commerce, social media, or ride-sharing) and identify:

- 5-8 potential microservices
- The data each service would own
- The API each service would expose
- The communication pattern between services (sync vs async)

Draw the architecture diagram showing services, databases, and communication flows.

### Exercise 2: Compare Communication Patterns

Build two versions of a simple order system:

**Version 1 (Synchronous):**
- Order Service calls Payment Service via REST
- If payment fails, return error to user immediately

**Version 2 (Asynchronous):**
- Order Service publishes "OrderCreated" event to a message queue
- Payment Service subscribes and processes payment
- Payment Service publishes "PaymentCompleted" or "PaymentFailed" event

Compare: What happens when the Payment Service is down for 5 minutes? How does each version behave?

### Exercise 3: Service Boundary Analysis

You are building a food delivery application. The product manager gives you these features:

- User registration and login
- Restaurant menu browsing
- Order placement
- Real-time delivery tracking
- Payment processing
- Driver assignment
- Restaurant dashboard
- Customer reviews

Group these features into microservices. For each service, define what data it owns and which other services it needs to communicate with. Justify your grouping.

---

## What Is Next?

Now that you understand the trade-offs between monoliths and microservices, the next chapter covers the practical process of migrating from a monolith to microservices. You will learn the **Strangler Fig pattern**, database decomposition strategies, and how to avoid the pitfalls of a big-bang rewrite.
