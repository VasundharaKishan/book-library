# Chapter 15: Migrating from Monolith to Microservices

## What You Will Learn

- The Strangler Fig pattern for gradual migration
- How to identify seams in a monolith — the natural places to split
- Database decomposition strategies and shared data challenges
- How to introduce an API gateway during migration
- Using feature flags to control the migration safely
- The dual-write problem and why it causes data inconsistency
- Event-driven decomposition as a migration strategy
- A real-world migration story walkthrough from start to finish

## Why This Chapter Matters

The decision to move from a monolith to microservices is not the hard part. The hard part is doing the migration without breaking your running system. You cannot stop the business for six months while you rewrite everything.

Most failed migrations happen because teams try a "big bang" rewrite — throw away the old code and build everything new. History shows this approach fails far more often than it succeeds. The Netscape browser rewrite took three years and nearly killed the company.

This chapter teaches you the safe, incremental approach. You will learn how to migrate piece by piece, validate each step, and always have a rollback path.

---

## The Strangler Fig Pattern

The Strangler Fig is a tropical plant that grows around an existing tree. Over time, it slowly replaces the host tree. Eventually, the original tree is completely replaced, but at every point during the process, the combined system is functional.

This is exactly how you should migrate a monolith.

```
  Phase 1: Monolith handles everything

  +------------------+
  |     Monolith     |
  |                  |
  | [Users] [Orders] |
  | [Pay]  [Search]  |
  | [Ship] [Notify]  |
  +------------------+

  Phase 2: Extract one service, route traffic

         +--------+
         | Router |
         +---+----+
             |
     +-------+--------+
     |                |
  +--+---+     +------+------+
  | New  |     |  Monolith   |
  | User |     |             |
  | Svc  |     | [Orders]    |
  |      |     | [Pay][Ship] |
  +------+     | [Search]    |
               | [Notify]    |
               +-------------+

  Phase 3: Extract more services

         +--------+
         | Router |
         +---+----+
             |
     +---+---+---+---+
     |   |       |   |
  +--+-+ +--+-+ ++-+ +------+
  |User| |Ord | |Pay| |Mono  |
  |Svc | |Svc | |Svc| |      |
  +----+ +----+ +---+ |[Ship]|
                       |[Srch]|
                       +------+

  Phase 4: Monolith is gone

         +--------+
         | Router |
         +---+----+
             |
   +-+---+---+---+---+---+
   | |   |       |   |   |
  ++-+ +--+-+ ++-+ ++-+ ++-+
  |Us| |Ord | |Py| |Sh| |Sr|
  +--+ +----+ +--+ +--+ +--+
```

### How It Works

1. **Identify a piece of functionality** in the monolith to extract.
2. **Build the new service** alongside the monolith.
3. **Route traffic** to the new service for that functionality.
4. **Verify** the new service works correctly.
5. **Remove the old code** from the monolith.
6. **Repeat** for the next piece.

The key insight: at every step, the system works. If the new service fails, you route traffic back to the monolith. There is always a rollback path.

---

## Step 1: Identify Seams

A **seam** is a natural boundary in your monolith where the code can be split with minimal changes. Not all code is equally easy to extract.

### Finding Good Seams

Look for code that:
- Has few dependencies on other parts of the monolith
- Communicates with the rest of the system through a small number of well-defined interfaces
- Owns its own data (or can be given its own data)
- Changes frequently (extracting it gives the most deployment speed)

```
  Dependency Analysis of a Monolith

  +--------+     +--------+     +--------+
  | User   |<----| Order  |---->| Payment|
  | Module |     | Module |     | Module |
  +---+----+     +---+----+     +--------+
      |              |
      |         +----+----+
      |         | Shipping|
      |         | Module  |
      |         +---------+
      |
  +---+--------+
  | Notification|    <--- Good candidate!
  | Module      |         - Few incoming dependencies
  |             |         - Only needs user data
  +-----------+          - Changes often (new channels)

  +-------------+
  | Search      |    <--- Also good!
  | Module      |         - Read-only
  |             |         - Can use its own data store
  +-------------+
```

### What to Extract First

Start with the **easiest, lowest-risk** service. This is usually:

1. **Leaf services** — services that are called by others but do not call others (e.g., notification, search, reporting).
2. **Read-heavy services** — services that mostly read data and rarely write (e.g., product catalog, user profiles).
3. **Independently deployable features** — features that change on a different cadence than the rest of the system.

Do NOT start with the core business logic. Do not extract the order service or payment service first. Start at the edges.

---

## Step 2: Database Decomposition

The database is the hardest part of any migration. The monolith typically has one big database with foreign keys between tables. Splitting the database requires careful planning.

### The Problem

```
  Monolith Database (Shared)

  +-------------------------------------------+
  |                                           |
  |  users          orders         payments   |
  |  +------+      +--------+    +--------+  |
  |  | id   |<-----| user_id|    | order_id|->|
  |  | name |      | total  |    | amount  |  |
  |  | email|      | status |    | status  |  |
  |  +------+      +---+----+    +--------+  |
  |                     |                     |
  |              order_items                  |
  |              +----------+                 |
  |              | order_id |                 |
  |              | product  |                 |
  |              | quantity |                 |
  |              +----------+                 |
  |                                           |
  |  Foreign keys everywhere.                 |
  |  Can't just split tables into separate    |
  |  databases without breaking joins.        |
  +-------------------------------------------+
```

### Strategy 1: Shared Database (Temporary)

As a first step, let the new service access the monolith's database. This is not the final state, but it reduces risk during migration.

```
  +----------+     +----------+
  | New User |     | Monolith |
  | Service  |     |          |
  +----+-----+     +----+-----+
       |                |
       +-------+--------+
               |
        +------+------+
        |  Shared DB  |
        +-------------+

  Temporary! Move to separate databases later.
```

### Strategy 2: Database View or API

Create a read-only view or API that the new service uses to access data it does not own.

```
  +----------+                    +----------+
  | Order    |  GET /users/123    | User     |
  | Service  | -----------------> | Service  |
  +----+-----+                    +----+-----+
       |                               |
  +----+-----+                    +----+-----+
  | Order DB |                    | User DB  |
  +----------+                    +----------+

  Order Service no longer joins against the users table.
  It calls the User Service API to get user data.
```

### Strategy 3: Data Duplication

Copy the data the new service needs into its own database. Keep it synchronized through events or periodic sync.

```
  +----------+     Event: UserUpdated     +----------+
  | User     | --------------------------> | Order    |
  | Service  |                             | Service  |
  +----+-----+                             +----+-----+
       |                                        |
  +----+-----+                             +----+-----+
  | User DB  |                             | Order DB |
  | (source  |                             | (has a   |
  |  of truth|                             |  copy of |
  |  for     |                             |  user    |
  |  users)  |                             |  name,   |
  +----------+                             |  email)  |
                                           +----------+
```

### Handling Foreign Keys Across Services

When tables move to different databases, you lose foreign key constraints. Replace them with:

1. **Application-level validation**: The Order Service calls the User Service to verify a user exists before creating an order.
2. **Eventual consistency**: Accept that references might temporarily point to non-existent entities. Handle this gracefully.
3. **Soft references**: Store IDs as strings without database-enforced constraints. Validate at the application level.

---

## Step 3: Introduce an API Gateway

An API gateway sits between clients and your services. During migration, it is essential for routing traffic between the monolith and new services.

```
  Before API Gateway          After API Gateway

  Client                      Client
    |                           |
    v                         +-v---------+
  Monolith                    | API       |
                              | Gateway   |
                              +--+---+----+
                                 |   |
                          +------+   +------+
                          |                |
                      +---v---+      +-----v-----+
                      | New   |      | Monolith  |
                      | User  |      | (handles  |
                      | Svc   |      |  the rest)|
                      +-------+      +-----------+

  The API Gateway routes:
  /api/users/*  --> User Service
  /api/*        --> Monolith (everything else)
```

### Benefits During Migration

1. **Transparent routing**: Clients do not need to know which backend handles their request.
2. **Gradual cutover**: Route 10% of user traffic to the new service, then 50%, then 100%.
3. **Rollback**: If the new service has issues, route traffic back to the monolith instantly.
4. **Cross-cutting concerns**: Authentication, rate limiting, and logging in one place.

---

## Step 4: Feature Flags for Safe Migration

Feature flags let you control which code path runs without deploying new code. They are essential for safe migrations.

```
  if feature_flag("use_new_user_service"):
      response = call_new_user_service(request)
  else:
      response = call_monolith_user_module(request)
```

### Migration with Feature Flags

```
  Phase 1: Flag off (0% new service)
  All traffic goes to monolith.

  Phase 2: Flag on for internal users (1%)
  Employees test the new service.

  Phase 3: Flag on for 10% of users
  Monitor error rates, latency, correctness.

  Phase 4: Flag on for 50% of users
  Continue monitoring.

  Phase 5: Flag on for 100% of users
  New service handles all traffic.

  Phase 6: Remove old code from monolith
  Clean up the flag.

  At any phase, if something goes wrong:
  Turn off the flag --> instant rollback to monolith
```

### Shadow Testing (Dark Launching)

Run both the old and new code paths simultaneously. Compare results. Only return the monolith's response to the user.

```
  +----------+
  |  Request |
  +----+-----+
       |
  +----v-----+
  | Feature  |
  | Flag     |
  +--+---+---+
     |   |
     |   +------ Shadow mode ------+
     |                             |
  +--v--------+            +-------v------+
  | Monolith  |            | New Service  |
  | (returns  |            | (result is   |
  |  response)|            |  compared,   |
  +--+--------+            |  not returned)|
     |                     +-------+------+
     v                             |
  Client gets                Compare results.
  monolith response.         Log differences.
                             Fix bugs before
                             real cutover.
```

---

## The Dual-Write Problem

A common mistake during migration is writing to two databases simultaneously. This seems logical but causes serious consistency issues.

### The Problem

```
  Order Service needs to:
  1. Write to the old monolith database
  2. Write to the new order database

  +-------------+
  | Order       |
  | Service     |
  +--+------+---+
     |      |
     v      v
  +--+--+ +-+----+
  | Old | | New  |
  | DB  | | DB   |
  +-----+ +------+

  What if step 1 succeeds but step 2 fails?
  Now the databases are inconsistent.

  What if step 2 succeeds but step 1 fails?
  Same problem.

  What if both succeed but with different timestamps?
  A concurrent read might see different states.
```

### Why Dual Writes Fail

1. There is no distributed transaction between two different databases (in practice).
2. If the process crashes between the two writes, one database has the data and the other does not.
3. Network issues can cause one write to succeed and the other to fail.

### The Solution: Change Data Capture (CDC)

Write to one database (the source of truth). Use Change Data Capture to stream changes to the other database.

```
  +-------------+
  | Order       |
  | Service     |
  +------+------+
         |
         v  (single write)
  +------+------+
  |  Source DB  |
  +------+------+
         |
         v  (CDC: Debezium, etc.)
  +------+------+
  | Change      |
  | Data        |
  | Capture     |
  +------+------+
         |
         v
  +------+------+
  | Message     |
  | Broker      |
  | (Kafka)     |
  +------+------+
         |
    +----+----+
    |         |
    v         v
  +-+---+ +--+----+
  | New | | Search|
  | DB  | | Index |
  +-----+ +------+

  One source of truth. Changes flow to other systems.
  No dual-write inconsistency.
```

---

## Event-Driven Decomposition

Instead of making synchronous calls between the monolith and new services, use events. The monolith publishes events when things happen. New services subscribe to those events.

### How It Works

```
  Step 1: Add events to the monolith

  +------------------------------------------+
  |              Monolith                      |
  |                                          |
  |  [Order Module]                          |
  |       |                                  |
  |       | When order is created:           |
  |       | publish("OrderCreated", data)    |
  |       |                                  |
  +-------+----------------------------------+
          |
          v
  +-------+-------+
  |  Message       |
  |  Broker        |
  +-------+--------+
          |
          v
  +-------+--------+
  | New Notification|
  | Service         |
  | (subscribes to  |
  |  OrderCreated)  |
  +-----------------+

  Step 2: Move the notification logic out of the monolith
  Step 3: Repeat for other events and services
```

### Benefits

1. **Low coupling**: The monolith does not need to know about the new services.
2. **Gradual migration**: You can add new services without changing the monolith (just add subscribers).
3. **Reversible**: If a new service fails, the monolith still works. Events queue up and are processed when the service recovers.

---

## Real-World Migration Story: Online Bookstore

Let us walk through a complete migration for a fictional online bookstore called PageTurner.

### The Starting Point

PageTurner is a monolith built in Java with a single PostgreSQL database. It handles:
- User accounts and authentication
- Book catalog and search
- Shopping cart
- Order processing
- Payment
- Email notifications
- Reviews and ratings

The team has 30 engineers. Deployments take 2 hours and happen once a week. A bug in the review feature last month brought down the entire site for 4 hours.

### Phase 1: Assess and Plan (Week 1-2)

The team maps dependencies between modules:

```
  Dependency Map

  Auth ---------> User
                    ^
                    |
  Catalog -------> |
     ^             |
     |             |
  Search           |
                   |
  Cart ----------> Catalog
     |
     v
  Order ---------> Payment
     |              |
     v              v
  Notification    Notification

  Reviews ------> User, Catalog
```

They identify the best candidates for extraction:
1. **Notifications** (leaf node, no dependents)
2. **Search** (read-only, can have its own data store)
3. **Reviews** (low coupling, independent feature)

### Phase 2: Set Up Infrastructure (Week 3-4)

- Deploy an API gateway (Kong)
- Set up a message broker (RabbitMQ)
- Set up CI/CD pipelines for new services
- Add monitoring and logging infrastructure
- Set up feature flags (LaunchDarkly)

### Phase 3: Extract Notification Service (Week 5-8)

1. Add event publishing to the monolith's order module: publish `OrderCreated`, `OrderShipped` events.
2. Build a new Notification Service that subscribes to these events.
3. Test with shadow mode — both old and new notification code send emails. Compare.
4. Use feature flag to switch from old to new.
5. Remove notification code from the monolith.

```
  Before:                        After:

  +----------+                   +----------+     +-----------+
  | Monolith |                   | Monolith | --> | Rabbit MQ |
  |          |                   | (publishes     |           |
  | sends    |                   |  events)  |    +-+---+-----+
  | emails   |                   +----------+      |   |
  | directly |                                     v   v
  +----------+                   +-----------+ +---+-------+
                                 | Notif Svc | | Other     |
                                 | (sends    | | future    |
                                 |  emails)  | | services  |
                                 +-----------+ +-----------+
```

### Phase 4: Extract Search Service (Week 9-12)

1. Set up Elasticsearch cluster.
2. Build a Search Service that indexes book data from the monolith database (using CDC).
3. Route search API calls through the API gateway to the new service.
4. Use feature flag: 10% -> 50% -> 100%.
5. Remove search code from the monolith.

### Phase 5: Extract Reviews Service (Week 13-16)

1. Create a separate reviews database.
2. Migrate review data from the monolith database.
3. Build Reviews Service with its own API.
4. Update the monolith to call the Reviews Service API instead of querying the reviews table directly.
5. Feature flag rollout.
6. Remove reviews code and table from the monolith.

### Phase 6: Continue Extracting (Month 5+)

With three successful extractions, the team has the infrastructure, processes, and confidence to continue. They tackle Cart, Catalog, and eventually Order and Payment — the harder services with more dependencies.

### Results After 6 Months

- Deployment frequency: From weekly to multiple times per day (per service)
- Deployment time: From 2 hours to 15 minutes
- A review service outage no longer affects the rest of the site
- The search team switched from PostgreSQL full-text search to Elasticsearch without affecting other teams
- The notification team added push notifications without touching the monolith

---

## Common Mistakes

1. **Big bang rewrite.** Throwing away the monolith and rewriting everything from scratch. This almost always fails. The Strangler Fig pattern is safer.

2. **Extracting the hardest service first.** Start with the easiest, lowest-risk service to build confidence and infrastructure.

3. **Dual writes without a consistency strategy.** Writing to two databases simultaneously leads to inconsistency. Use CDC or events instead.

4. **No rollback path.** Every migration step should be reversible. If the new service fails, you should be able to route traffic back to the monolith.

5. **Migrating without feature flags.** Feature flags give you fine-grained control over the migration. Without them, you are doing big-bang cutover at a smaller scale.

6. **Ignoring the database.** Extracting code into a new service but still reading from the monolith's database is not a real migration. Plan for database decomposition from the start.

7. **Not investing in infrastructure first.** CI/CD, monitoring, logging, and an API gateway need to exist before you start extracting services.

---

## Best Practices

1. **Follow the Strangler Fig pattern.** Migrate incrementally. Always keep the system working.

2. **Extract leaf services first.** Start with services that have the fewest dependencies.

3. **Use events for decoupling.** Publish events from the monolith. New services subscribe to events instead of calling the monolith directly.

4. **One source of truth for data.** During migration, be clear about which system owns which data. Use CDC to propagate changes.

5. **Shadow test before cutover.** Run the old and new code paths in parallel. Compare results. Fix discrepancies before switching traffic.

6. **Set up infrastructure before migrating.** API gateway, message broker, CI/CD, monitoring, and feature flags should all be in place before you extract the first service.

7. **Communicate the plan.** The whole team should understand the migration strategy, the current phase, and the rollback plan.

---

## Quick Summary

Migrating from a monolith to microservices should be gradual, not a big-bang rewrite. The Strangler Fig pattern lets you extract services one at a time while keeping the system functional. Start by identifying seams (natural boundaries) in the monolith, beginning with leaf services. Database decomposition is the hardest part — use strategies like API access, data duplication, and Change Data Capture to avoid dual-write problems. An API gateway enables transparent routing between the monolith and new services. Feature flags and shadow testing provide safe rollout and instant rollback.

---

## Key Points

- The Strangler Fig pattern is the safest way to migrate: extract one service at a time, always keeping the system functional.
- Start with leaf services (notifications, search) that have the fewest dependencies.
- Database decomposition is the hardest part — plan for it early.
- Dual writes cause data inconsistency. Use Change Data Capture or events instead.
- An API gateway routes traffic between the monolith and new services transparently.
- Feature flags enable gradual rollout and instant rollback.
- Shadow testing (dark launching) lets you compare old and new implementations before switching.
- Event-driven decomposition decouples new services from the monolith.
- Always have a rollback path at every step of the migration.

---

## Practice Questions

1. Your monolith has 15 modules. Which three characteristics would make a module a good candidate for first extraction?

2. During migration, your new Order Service needs customer data owned by the User module (still in the monolith). What are three ways to provide this data, and what are the trade-offs of each?

3. You are using dual writes to keep the old and new databases in sync. A developer reports that some orders appear in the new database but not the old one. What went wrong, and how would you fix it?

4. Your team wants to skip the API gateway and have clients call the new services directly. What problems will this cause during migration?

5. Explain how feature flags help with migration safety. What happens if you migrate without them?

---

## Exercises

### Exercise 1: Migration Plan

You have a monolith with these modules: Authentication, User Profile, Product Catalog, Search, Shopping Cart, Checkout, Payment, Shipping, Reviews, Recommendations, Notifications, Admin Dashboard.

Create a migration plan:
- Map the dependencies between modules
- Rank the modules by extraction difficulty (1 = easiest)
- Plan the order of extraction (which first, which last?)
- Identify which data needs to be shared and how

### Exercise 2: Solve the Dual-Write Problem

You are migrating the Order module. During the transition, both the monolith and the new Order Service need to write to their respective databases. Design a solution using Change Data Capture that:

- Has one source of truth
- Keeps both databases synchronized
- Handles failures gracefully
- Can be rolled back if needed

Draw the architecture diagram and describe the data flow.

### Exercise 3: Feature Flag Rollout Plan

Design a feature flag rollout plan for migrating the Search module:

- Define 5 rollout phases with percentage of traffic
- For each phase, list what you monitor and what would trigger a rollback
- Define the criteria for moving from one phase to the next
- Include a timeline estimate

---

## What Is Next?

Now that you know how to break apart a monolith, the next chapter explores **Event-Driven Architecture** in depth. You will learn about event sourcing, CQRS, saga patterns, and how to build systems where services communicate through events rather than direct calls.
