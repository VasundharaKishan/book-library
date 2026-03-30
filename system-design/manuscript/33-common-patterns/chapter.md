# Chapter 33: Common System Design Patterns

Patterns are reusable solutions to recurring problems. When a senior engineer hears "we need to protect our service from cascading failures," they immediately think "Circuit Breaker." When someone says "our reads and writes have completely different performance requirements," the response is "CQRS." These patterns are the vocabulary of system design -- learning them gives you ready-made building blocks that you can combine and adapt to solve almost any design problem.

This chapter is a catalog of 17 essential patterns. For each pattern, you will find: when to use it, how it works with an ASCII diagram, and a real-world example. Think of this chapter as a reference you come back to whenever you encounter a design challenge.

---

## What You Will Learn

- 17 design patterns that appear repeatedly in system design interviews and production systems.
- When to apply each pattern and when to avoid it.
- How each pattern works, illustrated with ASCII diagrams.
- Real-world examples from companies like Netflix, Amazon, Uber, and Stripe.

---

## Why This Chapter Matters

In interviews, dropping the right pattern name at the right time signals experience. But more importantly, understanding these patterns helps you design better systems. Instead of reinventing solutions from scratch, you can reach for a proven pattern, adapt it to your context, and explain the trade-offs confidently.

These patterns are not academic exercises. Every one of them is used in production at scale by companies processing millions of requests per second.

---

## 33.1 Ambassador

### When to Use

You want to offload cross-cutting concerns (logging, monitoring, retries, TLS termination) from your application to a helper process.

### How It Works

```
+-------------------+       +-------------------+
|   Application     |       |   Ambassador      |
|   Container       |------>|   Container       |------>  External
|                   |       |                   |         Service
|  (business logic  |       |  (retries, TLS,   |
|   only)           |       |   logging, auth)  |
+-------------------+       +-------------------+
         Pod / Host
```

The ambassador sits alongside your application as a proxy. All outbound traffic goes through it. The application itself stays simple and focused on business logic.

### Real-World Example

Envoy Proxy is used as an ambassador in Kubernetes service meshes (Istio). It handles mTLS, retries, circuit breaking, and observability for every service without changing application code.

---

## 33.2 Backends for Frontends (BFF)

### When to Use

Different clients (mobile, web, smart TV) need different API shapes, response sizes, or aggregation logic from the same backend services.

### How It Works

```
+-----------+     +----------+
| Mobile    |---->| Mobile   |---+
| App       |     | BFF      |   |
+-----------+     +----------+   |     +------------------+
                                 +---->| Shared Backend   |
+-----------+     +----------+   |     | Services         |
| Web       |---->| Web      |---+     | (Users, Orders,  |
| App       |     | BFF      |   |     |  Inventory...)   |
+-----------+     +----------+   |     +------------------+
                                 |
+-----------+     +----------+   |
| Smart TV  |---->| TV       |---+
| App       |     | BFF      |
+-----------+     +----------+
```

Each BFF is tailored for its client. The mobile BFF returns smaller payloads with fewer images. The web BFF returns richer data. The TV BFF returns large media-focused responses.

### Real-World Example

Netflix uses BFF extensively. Their mobile, TV, and web clients each have dedicated backend-for-frontend services that optimize API responses for each platform's screen size, bandwidth, and interaction patterns.

---

## 33.3 Bulkhead

### When to Use

You want to isolate failures so that a problem in one part of the system does not take down everything else. Named after the watertight compartments in a ship's hull.

### How It Works

```
                +----------------------------------+
                |         Application Server        |
                |                                  |
                |  +----------+   +----------+     |
                |  | Thread   |   | Thread   |     |
  Requests ---->|  | Pool A   |   | Pool B   |     |
  for Service A |  | (50      |   | (50      |     |
                |  |  threads)|   |  threads)|     |
  Requests ---->|  +----+-----+   +----+-----+     |
  for Service B |       |              |           |
                +-------|--------------|------------+
                        v              v
                   +---------+    +---------+
                   |Service A|    |Service B|
                   |(slow!)  |    |(healthy)|
                   +---------+    +---------+

Without bulkhead: Service A's slowness consumes ALL threads.
                  Service B requests also fail.

With bulkhead: Service A's slowness only exhausts Pool A.
               Pool B continues serving Service B normally.
```

### Real-World Example

Amazon isolates customer-facing services from internal batch-processing workloads using separate thread pools, connection pools, and even separate clusters. A spike in internal analytics never affects the shopping cart.

---

## 33.4 Cache-Aside (Lazy Loading)

### When to Use

You want to reduce database load by caching frequently read data, but you need control over what gets cached and when.

### How It Works

```
  Read Path:
  +---------+     +----------+     +----------+
  | App     |---->| Cache    |     | Database |
  | Server  |     | (Redis)  |     |          |
  +---------+     +----------+     +----------+
       |               |                |
       |  1. Check     |                |
       |  cache ------>|                |
       |               |                |
       |  2a. HIT:     |                |
       |  return data <-                |
       |               |                |
       |  2b. MISS:    |                |
       |  query DB ---------------------->
       |               |                |
       |  3. Get result <-----------------
       |               |                |
       |  4. Write to  |                |
       |  cache ------>|                |
       |               |                |
       |  5. Return    |                |
       |  to client    |                |

  Write Path:
  1. Write to database
  2. Invalidate cache (delete the key)
```

The application is responsible for managing the cache. On a miss, it loads from the database and populates the cache. On a write, it updates the database and invalidates the cache entry.

### Real-World Example

Almost every web application uses cache-aside with Redis or Memcached. Facebook uses Memcached as a cache-aside layer in front of MySQL for user profile data, handling billions of lookups per day.

---

## 33.5 Circuit Breaker

### When to Use

You want to prevent cascading failures when a downstream service is unhealthy. Instead of sending requests that will fail (and waiting for timeouts), stop calling the failing service and fail fast.

### How It Works

```
                +------------------------------------------+
                |           Circuit Breaker States          |
                |                                          |
                |  +--------+    failures    +---------+   |
                |  | CLOSED |  exceed ------>|  OPEN   |   |
                |  | (normal|  threshold     | (reject |   |
                |  |  flow) |                |  all    |   |
                |  +---+----+                |  calls) |   |
                |      ^                     +----+----+   |
                |      |                          |        |
                |      |  success    +----------+ | timer  |
                |      +-------------|HALF-OPEN | | expires|
                |                    |(test one |<+        |
                |                    | request) |          |
                |                    +----------+          |
                +------------------------------------------+

  CLOSED:    All requests pass through normally.
             Track failure count.

  OPEN:      All requests immediately fail (no call to
             downstream). Return cached/default response.

  HALF-OPEN: After a timeout, allow ONE test request
             through. If it succeeds, go to CLOSED.
             If it fails, go back to OPEN.
```

### Real-World Example

Netflix's Hystrix (now replaced by Resilience4j) implemented circuit breakers for every downstream service call. When a recommendation service was slow, the circuit opened and Netflix showed cached or default recommendations instead of making users wait.

---

## 33.6 CQRS (Command Query Responsibility Segregation)

### When to Use

Your read and write workloads have fundamentally different requirements. Reads need fast, denormalized data. Writes need normalized, consistent data. Scaling them together forces painful compromises.

### How It Works

```
                     Writes (Commands)
                          |
                          v
  +---------+     +---------------+     +-----------+
  | Client  |---->| Command       |---->| Write     |
  |         |     | Service       |     | Database  |
  +---------+     +---------------+     +-----------+
                                              |
                                         (events)
                                              |
                                              v
  +---------+     +---------------+     +-----------+
  | Client  |<----| Query         |<----| Read      |
  |         |     | Service       |     | Database  |
  +---------+     +---------------+     +-----------+
                     Reads (Queries)

  Write DB: normalized, optimized for writes (PostgreSQL)
  Read DB:  denormalized, optimized for reads (Elasticsearch, Redis)
  Sync:     events propagate changes from write to read store
```

The write side and read side can be scaled, optimized, and even use different technologies independently.

### Real-World Example

An e-commerce product catalog uses PostgreSQL for writes (add/update products) and Elasticsearch for reads (search, filter, faceted browsing). Changes are synced via events with a short delay (eventual consistency).

---

## 33.7 Event Sourcing

### When to Use

You need a complete, immutable history of every change to your data. Instead of storing current state, you store every event that led to the current state.

### How It Works

```
  Traditional (state-based):
  +----+--------+--------+
  | id | name   | balance|
  +----+--------+--------+
  | 1  | Alice  | $150   |  <-- only current state
  +----+--------+--------+

  Event Sourcing:
  +-----+--------+----------+---------+
  | seq | entity | event    | data    |
  +-----+--------+----------+---------+
  | 1   | acct-1 | Created  | $0      |
  | 2   | acct-1 | Deposit  | +$200   |
  | 3   | acct-1 | Withdraw | -$50    |  <-- full history
  +-----+--------+----------+---------+
  Current balance = replay events: $0 + $200 - $50 = $150

  +------------------+     +------------------+
  | Event Store      |     | Materialized     |
  | (append-only     |---->| View             |
  |  log of events)  |     | (current state   |
  +------------------+     |  for queries)    |
                           +------------------+
```

You never update or delete events. To get current state, you replay events from the beginning (or from a snapshot).

### Real-World Example

Banking and financial systems use event sourcing to maintain a complete audit trail. Every transaction is an event. The account balance is a materialized view computed by replaying all events. This makes auditing, debugging, and regulatory compliance straightforward.

---

## 33.8 Fan-Out

### When to Use

A single event needs to be delivered to many recipients. A user posts a tweet, and all their followers need to see it.

### How It Works

```
  Fan-Out on Write (Push Model):
  +--------+     +-----------+     +---+---+---+---+
  | User A |---->| Fan-Out   |---->| B | C | D | E |
  | posts  |     | Service   |     +---+---+---+---+
  +--------+     +-----------+     Follower feed caches
  Time: O(N) at write time, O(1) at read time

  Fan-Out on Read (Pull Model):
  +--------+     +-----------+     +---+---+---+---+
  | User B |---->| Feed      |---->| A | X | Y | Z |
  | reads  |     | Builder   |     +---+---+---+---+
  | feed   |     +-----------+     Query all followees
  +--------+
  Time: O(1) at write time, O(N) at read time

  Hybrid (Real-World):
  - Regular users (<10K followers): fan-out on write
  - Celebrities (>10K followers): fan-out on read
```

### Real-World Example

Twitter uses a hybrid fan-out approach. When a regular user tweets, the tweet is pushed into each follower's timeline cache (fan-out on write). When a celebrity with millions of followers tweets, the tweet is fetched at read time (fan-out on read) to avoid millions of cache writes.

---

## 33.9 Gateway Aggregation

### When to Use

A client needs data from multiple backend services for a single page view. Instead of the client making 5 separate API calls, a gateway aggregates the responses.

### How It Works

```
               Without Gateway Aggregation:
  +--------+     5 round trips     +---+---+---+---+---+
  | Client |<--------------------->| A | B | C | D | E |
  +--------+                       +---+---+---+---+---+
  Latency = sum of all 5 calls (on mobile, very slow)

               With Gateway Aggregation:
  +--------+     1 round trip     +-----------+
  | Client |<-------------------->| API       |
  +--------+                      | Gateway   |
                                  +-----+-----+
                                        |
                           +----+----+----+----+----+
                           | A  | B  | C  | D  | E  |
                           +----+----+----+----+----+
                           (parallel internal calls)

  Latency = max of 5 calls (parallel) + gateway overhead
```

The gateway makes parallel calls to backend services, merges the results, and returns a single response. This dramatically reduces latency on high-latency networks (mobile, cross-continent).

### Real-World Example

An e-commerce product detail page needs data from: product service, pricing service, reviews service, inventory service, and recommendation service. A GraphQL gateway or API gateway aggregates these into a single response, reducing the client from 5 round trips to 1.

---

## 33.10 Leader Election

### When to Use

You have a distributed system where exactly one node needs to perform a specific role (like scheduling tasks, writing to a shared resource, or coordinating workers).

### How It Works

```
  +----------+    +----------+    +----------+
  | Node A   |    | Node B   |    | Node C   |
  | (LEADER) |    | (follower|    | (follower|
  +----+-----+    +----+-----+    +----+-----+
       |               |               |
       +-------+-------+-------+-------+
               |               |
               v               v
       +------------------------------+
       |  Coordination Service        |
       |  (ZooKeeper / etcd / Consul) |
       |                              |
       |  Lock: "/leader" -> Node A   |
       +------------------------------+

  If Node A fails:
  1. Its heartbeat / lease expires
  2. Node B and C race to acquire the lock
  3. Winner (say Node B) becomes new leader
  4. Node B takes over the leader's responsibilities
```

Leader election typically uses a distributed lock or lease mechanism. The leader must renew its lease periodically. If it fails to renew (crash, network partition), another node takes over.

### Real-World Example

Apache Kafka uses ZooKeeper for leader election among brokers. Each partition has a leader broker that handles all reads and writes. If the leader fails, ZooKeeper triggers a new election and one of the in-sync replicas becomes the new leader.

---

## 33.11 Outbox Pattern

### When to Use

You need to update a database AND publish an event/message atomically. Without the outbox pattern, you risk publishing an event but failing to update the database (or vice versa).

### How It Works

```
  The Problem (dual write):
  +--------+     +---------+
  | App    |---->| Database|  1. Write succeeds
  | Server |     +---------+
  |        |--X->| Message |  2. Publish fails!
  +--------+     | Queue   |     (data inconsistency)
                 +---------+

  The Solution (outbox):
  +--------+     +---------+     +----------+     +---------+
  | App    |---->| Database|     | Outbox   |---->| Message |
  | Server |     |         |     | Relay    |     | Queue   |
  +--------+     | Orders  |     | (CDC or  |     |         |
                 | table   |     |  poller) |     +---------+
                 |---------|     +----------+
                 | Outbox  |         ^
                 | table   |---------+
                 +---------+
                 (same transaction)

  1. App writes to Orders table AND Outbox table in a
     SINGLE database transaction (atomic).
  2. A separate relay process reads the Outbox table and
     publishes events to the message queue.
  3. After successful publish, mark outbox row as processed.
```

Because the business data and the outbox entry are written in the same transaction, they are always consistent. The relay process handles delivery to the message queue.

### Real-World Example

Stripe uses the outbox pattern to ensure that payment state changes are reliably published as events. When a payment succeeds, the payment record and the event are written in one transaction. A background process then delivers the event to webhooks and internal consumers.

---

## 33.12 Retry Pattern

### When to Use

A transient failure (network glitch, temporary server overload) causes a request to fail. Instead of immediately returning an error, retry the request after a delay.

### How It Works

```
  +--------+         +----------+
  | Client |-------->| Service  |
  +--------+         +----------+
       |                   |
       | Request 1         | 503 (overloaded)
       |<------------------|
       |                   |
       | (wait 1 second)   |
       |                   |
       | Request 2         | 503 (still overloaded)
       |<------------------|
       |                   |
       | (wait 2 seconds)  |
       |                   |
       | Request 3         | 200 OK
       |<------------------|

  Exponential Backoff with Jitter:
  Delay = min(base * 2^attempt + random_jitter, max_delay)

  Attempt 1: wait ~1s  (+/- random jitter)
  Attempt 2: wait ~2s  (+/- random jitter)
  Attempt 3: wait ~4s  (+/- random jitter)
  Attempt 4: wait ~8s  (+/- random jitter)
  Max delay: 30s (cap to prevent absurd waits)
```

**Critical:** Only retry on transient errors (5xx, timeouts, connection resets). Never retry on client errors (4xx) -- those will fail every time. And always add jitter to prevent the thundering herd problem (all clients retrying at the exact same time).

### Real-World Example

AWS SDKs use exponential backoff with jitter for all API calls by default. When a DynamoDB write is throttled, the SDK automatically retries with increasing delays and random jitter, preventing all clients from retrying simultaneously.

---

## 33.13 Saga Pattern

### When to Use

You have a business transaction that spans multiple services, and you cannot use a traditional distributed transaction (2PC). Instead, you break it into a sequence of local transactions, each with a compensating action to undo it if a later step fails.

### How It Works

```
  Choreography-based Saga:

  Order          Payment         Inventory        Shipping
  Service        Service         Service          Service
     |               |               |               |
     | 1. Create     |               |               |
     |    Order      |               |               |
     |-------------->|               |               |
     |               | 2. Charge     |               |
     |               |    Payment    |               |
     |               |-------------->|               |
     |               |               | 3. Reserve    |
     |               |               |    Stock      |
     |               |               |-------------->|
     |               |               |               | 4. Ship
     |               |               |               |
     |               |               |  FAILS!       |
     |               |               |<----- X       |
     |               |               |               |
     |               | 3c. Refund    | 3c. Release   |
     |               |    Payment    |    Stock       |
     |               |<--------------|               |
     | 1c. Cancel    |               |               |
     |    Order      |               |               |
     |<--------------|               |               |

  Each step has a compensating transaction (suffix "c"):
  Step 1: Create Order    -> 1c: Cancel Order
  Step 2: Charge Payment  -> 2c: Refund Payment
  Step 3: Reserve Stock   -> 3c: Release Stock
```

If any step fails, the saga executes the compensating transactions for all previously completed steps, in reverse order.

### Real-World Example

Uber uses sagas for ride booking. The saga coordinates: matching a rider with a driver, authorizing payment, updating driver availability, and starting the trip. If any step fails (payment declined, driver cancels), the saga reverses the completed steps.

---

## 33.14 Scatter-Gather

### When to Use

You need to query multiple sources (shards, services, or indexes) and combine the results into a single response.

### How It Works

```
  +--------+     +-----------+
  | Client |---->| Scatter-  |
  +--------+     | Gather    |
                 | Controller|
                 +-----+-----+
                       |
          +------------+------------+
          |            |            |
          v            v            v
    +---------+  +---------+  +---------+
    | Shard 1 |  | Shard 2 |  | Shard 3 |
    | or      |  | or      |  | or      |
    | Service |  | Service |  | Service |
    +---------+  +---------+  +---------+
          |            |            |
          +------------+------------+
                       |
                       v
                 +-----------+
                 | Merge     |
                 | Results   |
                 +-----------+
                       |
                       v
                 (combined response)

  SCATTER: Send the query to all shards/services in parallel
  GATHER:  Collect all responses, merge, sort, return
```

The total latency is the maximum latency across all shards, not the sum. But you must handle stragglers: set a timeout and return partial results if one shard is slow.

### Real-World Example

Elasticsearch uses scatter-gather for every search query. The coordinating node sends the query to all relevant shards in parallel, each shard returns its top results, and the coordinator merges and re-ranks them into the final result set.

---

## 33.15 Sidecar

### When to Use

You want to add functionality to an existing application (logging, monitoring, networking, security) without modifying the application's code. The sidecar is a separate process that runs alongside the application.

### How It Works

```
  +------------------------------------------+
  |                  Pod / Host               |
  |                                          |
  |  +------------------+  +---------------+ |
  |  |  Application     |  |  Sidecar      | |
  |  |  Container       |  |  Container    | |
  |  |                  |  |               | |
  |  |  (business       |  |  (logging,    | |
  |  |   logic)         |  |   metrics,    | |
  |  |                  |  |   proxy,      | |
  |  |                  |  |   config)     | |
  |  +------------------+  +---------------+ |
  |        |                     |           |
  |        +--------+------------+           |
  |                 |                        |
  +------------------------------------------+
                    |
              Shared network namespace
              (localhost communication)
```

The sidecar shares the same lifecycle and network namespace as the main application. They communicate over localhost, which has near-zero latency.

### Real-World Example

Kubernetes service meshes (Istio, Linkerd) inject an Envoy sidecar proxy into every pod. The sidecar handles mTLS encryption, traffic management, retries, and observability -- all without changing a single line of application code.

---

## 33.16 Strangler Fig

### When to Use

You need to migrate from a legacy (monolith) system to a new system incrementally, without a risky big-bang cutover. Named after the strangler fig tree that grows around an existing tree and eventually replaces it.

### How It Works

```
  Phase 1: All traffic goes to monolith
  +--------+     +-------------------+
  | Client |---->|    Monolith       |
  +--------+     +-------------------+

  Phase 2: New features go to new service
  +--------+     +---------+     +-------------------+
  | Client |---->| Facade/ |---->|    Monolith       |
  +--------+     | Router  |     | (existing features|
                 |         |     +-------------------+
                 |         |
                 |         |---->+-------------------+
                 +---------+     | New Service       |
                                 | (new + migrated   |
                                 |  features)        |
                                 +-------------------+

  Phase 3: Most traffic goes to new services
  +--------+     +---------+     +-------------------+
  | Client |---->| Facade/ |---->| Monolith          |
  +--------+     | Router  |     | (shrinking)       |
                 |         |     +-------------------+
                 |         |
                 |         |---->+---+---+---+-------+
                 +---------+     | A | B | C | ...   |
                                 +---+---+---+-------+
                                 New Microservices

  Phase 4: Monolith is decommissioned
  +--------+     +---------+     +---+---+---+-------+
  | Client |---->| Facade/ |---->| A | B | C | ...   |
  +--------+     | Router  |     +---+---+---+-------+
                 +---------+     New Microservices
```

The facade/router layer is the key. It intercepts all requests and decides whether to route them to the monolith or the new services. As you migrate features one by one, the monolith shrinks until it can be turned off.

### Real-World Example

Amazon famously migrated from a monolithic bookstore to microservices using the strangler fig pattern over several years. They incrementally extracted services (product catalog, ordering, recommendations) while keeping the monolith running. The facade layer routed traffic to the appropriate service based on the feature.

---

## 33.17 Throttling

### When to Use

You need to protect your service from being overwhelmed by too many requests. Throttling limits the rate at which clients can make requests.

### How It Works

```
  Token Bucket Algorithm:
  +------------------------------------------+
  |  Bucket (capacity = 10 tokens)           |
  |                                          |
  |  Tokens: [*] [*] [*] [*] [*] [ ] [ ]    |
  |           5 tokens remaining             |
  |                                          |
  |  Refill rate: 2 tokens/second            |
  |                                          |
  |  Request arrives:                        |
  |    Token available? -> Consume 1, allow  |
  |    No tokens?       -> Reject (429)      |
  +------------------------------------------+

  Per-Client Throttling:
  +---------+     +------------+     +---------+
  | Client  |---->| Throttle   |---->| Service |
  | A (100  |     | Layer      |     |         |
  |  req/s) |     | (checks    |     |         |
  +---------+     |  rate per  |     |         |
                  |  client)   |     |         |
  +---------+     |            |     |         |
  | Client  |---->| Client A:  |---->|         |
  | B (200  |     |  100/100   |     |         |
  |  req/s) |     | Client B:  |     |         |
  +---------+     |  200/150   |     +---------+
                  |  (throttled|
                  |   50 req/s)|
                  +------------+
```

Common algorithms: Token Bucket (allows bursts), Leaky Bucket (smooths traffic), Fixed Window Counter (simple but imprecise), Sliding Window (precise but more complex).

### Real-World Example

Every major API (GitHub, Stripe, Twitter) uses throttling. GitHub's API allows 5,000 requests per hour per authenticated user. When you exceed the limit, you receive a `429 Too Many Requests` response with a `Retry-After` header telling you when to try again.

---

## Pattern Quick Reference

```
+-------------------+----------------------------------------+
| Pattern           | Use When...                            |
+-------------------+----------------------------------------+
| Ambassador        | Offload cross-cutting concerns         |
| BFF               | Different clients need different APIs   |
| Bulkhead          | Isolate failures between components    |
| Cache-Aside       | Reduce DB load with controlled caching |
| Circuit Breaker   | Prevent cascading downstream failures  |
| CQRS              | Read/write workloads differ greatly    |
| Event Sourcing    | Need full audit trail of all changes   |
| Fan-Out           | One event -> many recipients           |
| Gateway Aggregate | Client needs data from many services   |
| Leader Election   | Exactly one node must coordinate       |
| Outbox            | Atomic DB update + event publish       |
| Retry             | Transient failures are expected        |
| Saga              | Multi-service transaction without 2PC  |
| Scatter-Gather    | Query multiple sources, merge results  |
| Sidecar           | Add features without code changes      |
| Strangler Fig     | Incremental monolith-to-micro migration|
| Throttling        | Protect service from overload          |
+-------------------+----------------------------------------+
```

---

## Common Mistakes

1. **Over-applying patterns.** Not every system needs CQRS or Event Sourcing. Use the simplest solution that meets your requirements.

2. **Using Saga when a simple transaction will do.** If all your data is in one database, use a regular transaction. Sagas are for cross-service coordination.

3. **Circuit breaker without fallback.** Opening the circuit is only half the solution. You need a fallback (cached data, default response, graceful degradation).

4. **Retry without backoff.** Retrying immediately at full speed makes the overloaded service worse. Always use exponential backoff with jitter.

5. **Throttling without feedback.** Return a `429` status code AND a `Retry-After` header so clients know when to come back.

6. **Strangler fig without monitoring.** You must monitor both the old and new paths to detect regressions before cutting over.

---

## Best Practices

1. **Start simple.** Use cache-aside and retry before reaching for CQRS and sagas.

2. **Combine patterns.** Circuit breaker + retry + bulkhead is a powerful combination for resilient service-to-service communication.

3. **Know the trade-offs.** Every pattern adds complexity. Event sourcing gives you an audit trail but makes queries harder. CQRS gives you read/write optimization but introduces eventual consistency.

4. **Name patterns in interviews.** Saying "I would use the outbox pattern here" signals experience and gives the interviewer a shorthand for your approach.

5. **Match patterns to requirements.** Do not use event sourcing because it sounds cool. Use it because you need an audit trail or time-travel debugging.

---

## Quick Summary

This chapter covered 17 design patterns that appear repeatedly in system design: Ambassador, BFF, Bulkhead, Cache-Aside, Circuit Breaker, CQRS, Event Sourcing, Fan-Out, Gateway Aggregation, Leader Election, Outbox, Retry, Saga, Scatter-Gather, Sidecar, Strangler Fig, and Throttling. Each pattern solves a specific recurring problem. The key is knowing when to apply each one and understanding the trade-offs involved. In interviews, naming the right pattern at the right time demonstrates experience and provides a shared vocabulary with the interviewer.

---

## Key Points

- Patterns are reusable solutions to recurring design problems, not silver bullets.
- Circuit Breaker + Retry + Bulkhead is the standard combination for resilient inter-service communication.
- CQRS and Event Sourcing add significant complexity; only use them when the requirements demand it.
- The Outbox pattern solves the dual-write problem (database + message queue atomicity).
- Sagas replace distributed transactions for multi-service workflows, using compensating actions for rollback.
- Strangler Fig is the safest way to migrate from a monolith to microservices incrementally.
- Fan-out on write is fast for reads but expensive for writes (celebrity problem). Hybrid approaches are common.
- Always combine throttling with informative error responses (429 + Retry-After).

---

## Practice Questions

1. A microservice calls three downstream services. Service A responds in 10ms, Service B in 50ms, and Service C is intermittently failing with 30-second timeouts. Which patterns would you apply to protect your service?

2. You are designing an e-commerce checkout flow that involves: creating an order, charging payment, reserving inventory, and sending a confirmation email. Which pattern would you use, and what are the compensating transactions for each step?

3. Your team is migrating a 10-year-old monolith to microservices. The monolith handles 500 requests per second and cannot have downtime. Which pattern do you use, and what is your first step?

4. A social media platform has 100 million users. When a user posts, the post needs to appear in all followers' feeds. A celebrity has 50 million followers. How do you handle this using the Fan-Out pattern?

5. Your service writes to a PostgreSQL database and publishes events to Kafka. Occasionally, the Kafka publish fails after the database write succeeds, causing data inconsistency. Which pattern solves this, and how does it work?

---

## Exercises

**Exercise 1: Pattern Matching**

For each scenario below, identify which pattern(s) apply and explain why:
- A payment service needs to call a fraud detection API that is occasionally slow.
- A mobile app loads a home screen that requires data from 7 different backend services.
- A hotel booking system needs to reserve a room, charge the credit card, and send a confirmation, and must roll back if any step fails.
- A legacy system processes 10,000 orders per day and the team wants to gradually move to a new architecture.

**Exercise 2: Design a Resilient Service Call**

Design the complete error-handling strategy for a service that calls a downstream payment API. Include: retry policy (how many retries, backoff strategy, which errors to retry), circuit breaker configuration (failure threshold, timeout, half-open behavior), bulkhead configuration (thread pool size), and fallback behavior (what to return when the circuit is open).

**Exercise 3: Implement a Saga**

Design a saga for a food delivery order that involves: (1) accept order, (2) charge customer, (3) notify restaurant, (4) assign delivery driver. Define the compensating transaction for each step. Draw the sequence diagram for both the success path and a failure at step 3. Would you use choreography (event-based) or orchestration (coordinator-based)? Why?

---

## What Is Next?

In the final chapter, we provide a comprehensive glossary of system design terms -- over 100 definitions organized alphabetically. Whether you need a quick refresher on "consistent hashing" or want to look up "quorum," the glossary has you covered.
