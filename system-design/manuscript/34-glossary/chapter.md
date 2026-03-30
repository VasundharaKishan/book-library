# Chapter 34: Glossary of System Design Terms

This glossary contains over 100 terms that appear throughout this book and in system design interviews. Use it as a quick reference when you encounter an unfamiliar term or need a concise refresher. Terms are organized alphabetically for easy lookup.

---

## What You Will Learn

- Clear, concise definitions for the most important system design terms.
- How each concept fits into the broader system design landscape.
- Cross-references to related terms and the chapters where each topic is covered in depth.

---

## Why This Chapter Matters

System design has its own vocabulary. In interviews and on the job, you need to speak this language fluently. Saying "we should use consistent hashing for our cache cluster" is only useful if you and your audience share the same understanding of what consistent hashing means. This glossary ensures you have a precise, interview-ready definition for every major concept.

---

## A

**ACL (Access Control List)** -- A list of permissions attached to a resource that specifies which users or systems are allowed to access it and what operations they can perform.

**Active-Active** -- A deployment model where multiple instances or data centers are all actively serving traffic simultaneously. Provides high availability and geographic distribution. Contrast with active-passive.

**Active-Passive** -- A deployment model where one instance handles all traffic (active) while a standby instance (passive) takes over only if the active one fails. Simpler than active-active but wastes standby resources.

**API (Application Programming Interface)** -- A defined contract that specifies how software components communicate with each other. Common styles include REST, GraphQL, gRPC, and WebSocket.

**API Gateway** -- A server that acts as the single entry point for all client requests. Handles cross-cutting concerns like authentication, rate limiting, request routing, and response aggregation.

**Asynchronous Processing** -- A pattern where work is accepted immediately and processed later, typically using a message queue. The caller does not wait for the result. Improves responsiveness and decouples producers from consumers.

**Availability** -- The percentage of time a system is operational and accessible. Expressed as "nines": 99.9% (three nines) allows ~8.7 hours of downtime per year; 99.99% (four nines) allows ~52 minutes.

**Availability Zone (AZ)** -- An isolated location within a cloud region, with independent power, cooling, and networking. Deploying across multiple AZs protects against localized failures.

## B

**Back Pressure** -- A mechanism where a system signals upstream components to slow down when it is overwhelmed. Prevents cascading failures by controlling the flow of work through the system.

**Batch Processing** -- Processing data in large groups (batches) at scheduled intervals, rather than in real-time. Suitable for analytics, ETL, and workloads where latency is not critical. Tools include Hadoop MapReduce and Apache Spark.

**Bloom Filter** -- A space-efficient probabilistic data structure that tests whether an element is a member of a set. Can produce false positives but never false negatives. Used for duplicate detection in web crawlers and cache lookups.

**Blue-Green Deployment** -- A deployment strategy where two identical environments (blue and green) exist. New code is deployed to the inactive environment, tested, then traffic is switched. Enables instant rollback by switching back.

**Broker** -- A middleware component that receives, stores, and forwards messages between producers and consumers. Examples: Kafka broker, RabbitMQ broker, Redis Pub/Sub.

## C

**Cache** -- A fast, temporary storage layer (usually in-memory) that stores frequently accessed data to reduce latency and database load. Common implementations: Redis, Memcached.

**Cache Eviction** -- The policy for removing items from a cache when it is full. Common policies: LRU (Least Recently Used), LFU (Least Frequently Used), TTL (Time To Live), FIFO (First In First Out).

**Cache Invalidation** -- The process of removing or updating stale data in a cache when the underlying source data changes. One of the hardest problems in computer science.

**Cache-Aside** -- A caching pattern where the application manages the cache explicitly: check cache first, on miss load from database and populate cache, on write update database and invalidate cache.

**Canary Deployment** -- A deployment strategy where new code is rolled out to a small percentage of users first. If no issues are detected, the rollout gradually expands to all users.

**CAP Theorem** -- States that a distributed system can provide at most two of three guarantees simultaneously: Consistency, Availability, and Partition tolerance. In practice, partition tolerance is required, so the trade-off is between consistency and availability.

**CDN (Content Delivery Network)** -- A geographically distributed network of proxy servers that cache and serve content from locations close to users, reducing latency for static assets like images, videos, CSS, and JavaScript.

**Choreography** -- A coordination pattern where services communicate through events without a central coordinator. Each service reacts to events and publishes its own events. Contrast with orchestration.

**Circuit Breaker** -- A pattern that prevents cascading failures by stopping requests to a failing downstream service. Has three states: Closed (normal), Open (all requests blocked), Half-Open (test one request).

**Consistent Hashing** -- A hashing technique where adding or removing a node in a distributed system only requires remapping a small fraction of keys, rather than rehashing everything. Used in distributed caches and databases.

**Containerization** -- Packaging an application and its dependencies into a lightweight, portable container that runs consistently across environments. Docker is the most common container runtime; Kubernetes orchestrates containers at scale.

**CQRS (Command Query Responsibility Segregation)** -- A pattern that separates the read model (queries) from the write model (commands), allowing each to be optimized, scaled, and maintained independently.

## D

**Data Lake** -- A centralized repository that stores raw, unstructured, and structured data at any scale. Unlike a data warehouse, data is stored in its native format and transformed only when needed.

**Data Partitioning** -- See Sharding.

**Data Replication** -- Copying data across multiple nodes or data centers to improve availability, durability, and read performance. Common strategies: single-leader, multi-leader, and leaderless replication.

**Database Index** -- A data structure (typically B-tree or hash) that speeds up data retrieval operations at the cost of additional storage and slower writes. Without indexes, queries must scan entire tables.

**Dead Letter Queue (DLQ)** -- A queue that stores messages that could not be processed successfully after a configured number of retries. Allows human or automated investigation of failed messages without blocking the main queue.

**Denormalization** -- Intentionally introducing redundancy in a database schema to improve read performance by reducing the need for joins. Common in read-heavy systems and NoSQL databases.

**DNS (Domain Name System)** -- The distributed system that translates human-readable domain names (example.com) into IP addresses (93.184.216.34). Acts as the internet's phone book.

**Distributed Lock** -- A lock mechanism that works across multiple processes or machines. Used when only one node should perform a specific action at a time. Implemented using tools like Redis (Redlock), ZooKeeper, or etcd.

**Distributed Transaction** -- A transaction that spans multiple databases or services. Traditionally uses Two-Phase Commit (2PC). In modern microservices, often replaced by the Saga pattern due to 2PC's blocking nature.

## E

**Elasticity** -- The ability of a system to automatically scale resources up during high demand and scale down during low demand, typically to optimize cost.

**Endpoint** -- A specific URL or network address where a service can be reached. For example, `https://api.example.com/users` is an endpoint for the users API.

**Eventual Consistency** -- A consistency model where reads may return stale data temporarily, but all replicas will converge to the same value given enough time without new updates. Used in systems that prioritize availability over strict consistency.

**Event-Driven Architecture** -- An architecture where services communicate by producing and consuming events (facts about something that happened). Promotes loose coupling between services. Key components: event producers, event bus/broker, event consumers.

**Event Sourcing** -- A pattern where state changes are stored as an immutable sequence of events rather than as mutable current state. Current state is derived by replaying events. Provides a complete audit trail.

## F

**Failover** -- The process of automatically switching to a standby system when the primary system fails. Can be active-passive (standby takes over) or active-active (traffic redistributes among remaining nodes).

**Fan-Out** -- The process of distributing a single event or message to multiple recipients. Fan-out on write pushes data to recipients at write time; fan-out on read pulls data from sources at read time.

**Fault Tolerance** -- A system's ability to continue operating correctly even when some components fail. Achieved through redundancy, replication, and graceful degradation.

**Firewall** -- A network security system that monitors and controls incoming and outgoing traffic based on predetermined rules. Protects internal services from unauthorized external access.

## G

**Geo-Replication** -- Replicating data across multiple geographic regions to reduce latency for global users and provide disaster recovery. Introduces challenges around consistency and conflict resolution.

**gRPC** -- A high-performance, open-source remote procedure call (RPC) framework developed by Google. Uses Protocol Buffers for serialization and HTTP/2 for transport. More efficient than REST for service-to-service communication.

**GraphQL** -- A query language for APIs where the client specifies exactly what data it needs. Reduces over-fetching and under-fetching compared to REST. Created by Facebook.

## H

**Hash Function** -- A function that maps data of arbitrary size to a fixed-size value. Used in hash tables, consistent hashing, checksums, and data integrity verification.

**Heartbeat** -- A periodic signal sent between distributed components to indicate they are alive and functioning. If heartbeats stop, the component is considered failed, triggering failover or recovery.

**Horizontal Scaling (Scale Out)** -- Adding more machines to a system to handle increased load. Contrast with vertical scaling (adding more power to a single machine). Horizontal scaling provides near-unlimited capacity but adds complexity.

**Hot Spot** -- An uneven distribution of load where a small number of nodes, keys, or partitions receive a disproportionate amount of traffic. Common in poorly designed sharding schemes.

**HTTP (Hypertext Transfer Protocol)** -- The foundation protocol of the web. Defines how clients and servers communicate. HTTP/1.1 uses text-based format; HTTP/2 uses binary framing and multiplexing; HTTP/3 uses QUIC over UDP.

## I

**Idempotency** -- A property where performing the same operation multiple times produces the same result as performing it once. Critical for retry safety: if a request is retried due to a timeout, an idempotent operation will not create duplicate effects.

**Indexing** -- The process of creating data structures (indexes) that allow fast lookup of records by specific fields. Without indexes, databases must scan all rows (full table scan).

## J

**Jitter** -- A random delay added to retry intervals or scheduled operations to prevent multiple clients from acting simultaneously (thundering herd). Exponential backoff with jitter is the standard retry strategy.

## K

**Kafka** -- A distributed event streaming platform used as a message broker, event store, and stream processor. Provides high throughput, fault tolerance, and durability. Data is organized into topics and partitions.

## L

**Latency** -- The time elapsed between sending a request and receiving a response. Measured in milliseconds. P50 (median), P95, and P99 percentiles are commonly tracked.

**Leader Election** -- The process of choosing one node in a distributed system to serve as the coordinator or primary. Typically implemented using distributed consensus algorithms or external coordination services (ZooKeeper, etcd).

**Load Balancer** -- A component that distributes incoming requests across multiple servers to prevent any single server from being overwhelmed. Common algorithms: round-robin, least connections, consistent hashing, weighted distribution.

**Load Shedding** -- Intentionally dropping requests when a system is overloaded to protect the system from total failure. Better to reject some requests quickly than to fail on all requests slowly.

**Long Polling** -- A technique where the client sends a request and the server holds the connection open until new data is available or a timeout occurs. A compromise between regular polling and WebSockets.

## M

**MapReduce** -- A programming model for processing large datasets in parallel across a distributed cluster. The Map step transforms data; the Reduce step aggregates results. Originally developed by Google.

**Message Queue** -- A component that stores messages between producers and consumers, enabling asynchronous, decoupled communication. Examples: RabbitMQ, Amazon SQS, Apache Kafka.

**Microservices** -- An architectural style where an application is composed of small, independently deployable services, each responsible for a specific business capability. Contrast with monolithic architecture.

**Middleware** -- Software that sits between an application and the network or operating system, providing services like message routing, authentication, and data transformation.

**Monolithic Architecture** -- An application built as a single, tightly coupled unit where all components share the same codebase and deployment. Simpler to develop initially but harder to scale and maintain as the system grows.

**Multi-Tenancy** -- A software architecture where a single instance of the application serves multiple customers (tenants), with data isolation between them. Common in SaaS applications.

## N

**NoSQL** -- A category of databases that do not use the traditional relational table-based model. Types include: key-value stores (Redis, DynamoDB), document stores (MongoDB), column-family stores (Cassandra), and graph databases (Neo4j).

**Normalization** -- The process of organizing database tables to minimize data redundancy and dependency. Normal forms (1NF, 2NF, 3NF) define progressively stricter rules.

## O

**Object Storage** -- A storage architecture that manages data as objects (with metadata and a unique identifier) rather than as files in a hierarchy or blocks on a disk. Amazon S3 is the most common example. Ideal for unstructured data like images, videos, and backups.

**Observability** -- The ability to understand the internal state of a system by examining its outputs: logs (what happened), metrics (quantitative measurements), and traces (request flow across services).

**Orchestration** -- A coordination pattern where a central coordinator directs the workflow across multiple services. The coordinator knows the full process and tells each service what to do. Contrast with choreography.

**Outbox Pattern** -- A pattern that ensures atomicity between a database write and an event publish by writing both the data and the event to the same database transaction. A separate process reads the outbox table and publishes events.

## P

**Partition Tolerance** -- A system's ability to continue operating despite network partitions (communication failures between nodes). One of the three guarantees in the CAP theorem; generally considered non-negotiable in distributed systems.

**Peer-to-Peer (P2P)** -- A distributed architecture where each node acts as both client and server. Nodes communicate directly with each other without a central server. Used in file sharing, blockchain, and some CDN architectures.

**Polyglot Persistence** -- Using different database technologies for different services or data stores within the same application, choosing the best tool for each job.

**Primary-Replica** -- A replication model where one node (primary/leader) handles all writes and propagates changes to replica nodes (followers/secondaries) that handle reads. Also called master-slave replication.

**Protocol Buffers (Protobuf)** -- A binary serialization format developed by Google. More compact and faster to serialize/deserialize than JSON or XML. Used with gRPC.

**Pub/Sub (Publish-Subscribe)** -- A messaging pattern where publishers send messages to topics without knowing who will receive them, and subscribers receive messages from topics they are interested in. Decouples producers from consumers.

## Q

**QPS (Queries Per Second)** -- The number of requests a system handles per second. A fundamental metric for capacity planning. Average QPS matters for provisioning; peak QPS matters for scaling.

**Quorum** -- The minimum number of nodes that must agree on an operation for it to be considered successful. In a system with N replicas, a quorum requires agreement from (N/2 + 1) nodes. Ensures consistency in replicated systems.

**Queue** -- A data structure or service that holds items for processing in a defined order (typically FIFO). In distributed systems, message queues decouple producers from consumers and handle load spikes.

## R

**Rate Limiting** -- Controlling the number of requests a client can make to a service within a given time window. Protects services from abuse and overload. Algorithms: token bucket, leaky bucket, sliding window.

**Read Replica** -- A copy of a database that serves read-only queries, offloading read traffic from the primary database. Introduces replication lag (eventual consistency).

**Redis** -- An open-source, in-memory data structure store used as a cache, message broker, and database. Supports strings, lists, sets, sorted sets, hashes, and streams. Known for sub-millisecond latency.

**Redundancy** -- Duplicating critical components or data so that if one fails, another can take over. The foundation of fault tolerance and high availability.

**REST (Representational State Transfer)** -- An architectural style for APIs that uses standard HTTP methods (GET, POST, PUT, DELETE) and treats everything as a resource identified by a URL. The most common API style for web services.

**Reverse Proxy** -- A server that sits in front of backend servers, forwarding client requests to them. Provides benefits like load balancing, SSL termination, caching, and DDoS protection. Examples: Nginx, HAProxy.

**RPC (Remote Procedure Call)** -- A protocol that allows a program to call a function on a remote server as if it were a local function call. gRPC is the most popular modern implementation.

## S

**Saga Pattern** -- A pattern for managing distributed transactions across multiple services. Instead of a single atomic transaction, a saga is a sequence of local transactions with compensating transactions to undo completed steps if a later step fails.

**Scalability** -- A system's ability to handle increased load by adding resources. Horizontal scalability adds more machines; vertical scalability adds more power to existing machines.

**Schema** -- The structure that defines how data is organized in a database: tables, columns, data types, relationships, and constraints. Schema-on-write (relational) vs schema-on-read (NoSQL) is a key design decision.

**Server-Sent Events (SSE)** -- A technology where the server pushes updates to the client over a single long-lived HTTP connection. Simpler than WebSockets but only supports one-way communication (server to client).

**Service Discovery** -- The mechanism by which services find and connect to each other in a dynamic environment. Can be client-side (client queries a registry) or server-side (load balancer queries registry). Examples: Consul, etcd, Kubernetes DNS.

**Service Level Agreement (SLA)** -- A formal contract between a service provider and its users that defines expected availability, latency, and other quality metrics, along with penalties for violations.

**Service Level Objective (SLO)** -- An internal target for a service's performance or availability. More specific than an SLA. For example: "p99 latency under 200ms" or "99.95% availability."

**Service Mesh** -- An infrastructure layer that handles service-to-service communication in a microservices architecture. Typically implemented as sidecar proxies (Envoy) managed by a control plane (Istio, Linkerd).

**Sharding** -- Splitting a database across multiple machines (shards), where each shard holds a subset of the data. Enables horizontal scaling of databases. Key decisions: sharding key, resharding strategy, cross-shard queries.

**Sidecar Pattern** -- Deploying a helper container alongside the main application container in the same pod/host. The sidecar handles cross-cutting concerns (logging, monitoring, networking) without modifying the application.

**SLA/SLO/SLI** -- Service Level Agreement (contract with users), Service Level Objective (internal target), and Service Level Indicator (actual measured metric). SLI measures reality; SLO sets the target; SLA defines the contract.

**Snowflake ID** -- A unique ID generation scheme (created by Twitter) that produces 64-bit IDs composed of: timestamp (41 bits), machine ID (10 bits), and sequence number (12 bits). IDs are time-sortable and globally unique without coordination.

**SQL (Structured Query Language)** -- The standard language for interacting with relational databases. Provides commands for querying (SELECT), modifying (INSERT, UPDATE, DELETE), and defining data structures (CREATE TABLE).

**SSE** -- See Server-Sent Events.

**Sticky Session** -- A load balancing technique where all requests from a specific client are routed to the same server. Useful when server-side state (sessions) exists but complicates scaling and failover.

**Stream Processing** -- Processing data records continuously in real-time as they arrive, rather than in batches. Tools include Apache Kafka Streams, Apache Flink, and Apache Storm.

**Strong Consistency** -- A guarantee that after a write completes, all subsequent reads will return the updated value. Provides the simplest programming model but requires coordination that reduces availability and increases latency.

## T

**Throughput** -- The amount of work a system can handle per unit of time. Measured in requests per second (RPS), transactions per second (TPS), or data volume per second (MB/s).

**Throttling** -- Intentionally limiting the rate of operations to protect a system from overload. Applied per-client, per-API, or globally. Returns HTTP 429 (Too Many Requests) when the limit is exceeded.

**TLS (Transport Layer Security)** -- A cryptographic protocol that provides secure communication over a network. Ensures confidentiality (encryption), integrity (tamper detection), and authentication (certificates). The successor to SSL.

**TTL (Time To Live)** -- A duration after which cached data, DNS records, or messages automatically expire. Prevents serving stale data indefinitely. Common TTL values: cache (5-60 minutes), DNS (1-24 hours).

**Two-Phase Commit (2PC)** -- A distributed transaction protocol that ensures all participants either commit or abort a transaction. Phase 1: coordinator asks all participants to prepare. Phase 2: coordinator tells all to commit (or abort if any failed). Blocking and slow, often replaced by the Saga pattern.

## U

**UUID (Universally Unique Identifier)** -- A 128-bit identifier that is unique across space and time without requiring a central authority. Version 4 UUIDs are randomly generated; version 7 UUIDs are time-ordered.

## V

**Vertical Scaling (Scale Up)** -- Adding more CPU, RAM, or storage to an existing machine. Simpler than horizontal scaling but has a hardware ceiling and creates a single point of failure.

**Virtual IP (VIP)** -- An IP address that is not tied to a specific physical machine. Used in load balancing and failover: the VIP floats between servers, so clients always connect to the same address regardless of which server is active.

## W

**WAL (Write-Ahead Log)** -- A technique where changes are written to an append-only log before being applied to the database. Ensures durability: if the system crashes, the log can be replayed to recover uncommitted changes.

**WebSocket** -- A communication protocol that provides full-duplex (two-way) communication over a single, long-lived TCP connection. Ideal for real-time applications like chat, live feeds, and multiplayer games.

**Write-Behind (Write-Back) Cache** -- A caching strategy where writes go to the cache first and are asynchronously flushed to the database. Provides fast writes but risks data loss if the cache fails before flushing.

**Write-Through Cache** -- A caching strategy where writes go to both the cache and the database simultaneously. Ensures consistency but adds write latency since every write waits for both operations.

## Z

**ZooKeeper** -- A centralized service for distributed coordination, including: configuration management, naming, leader election, distributed locking, and group membership. Widely used in the Hadoop and Kafka ecosystems. Being replaced by etcd and Raft-based alternatives in newer systems.

---

## Quick Summary

This glossary covers over 100 terms spanning every major area of system design: networking, databases, caching, messaging, deployment, security, and distributed systems. Use it as a reference whenever you encounter an unfamiliar term in this book, in an interview, or on the job.

---

## Key Points

- System design has a rich vocabulary. Knowing the precise meaning of terms like "eventual consistency," "quorum," and "idempotency" is essential for interviews and professional communication.
- Many terms are related: understanding one helps you understand others. For example, CAP theorem connects to consistency, availability, and partition tolerance.
- This glossary is a starting point. Each term could fill a chapter (and many of them do, earlier in this book). Use the glossary for quick reference and dive into the full chapters for depth.

---

## Practice Questions

1. Explain the difference between horizontal scaling and vertical scaling. When would you choose one over the other?

2. What is the relationship between SLI, SLO, and SLA? Give an example of each for a web application.

3. Compare and contrast WebSockets, Server-Sent Events, and long polling. When would you use each?

4. What does idempotency mean, and why is it important for APIs that may be retried?

5. Explain the difference between eventual consistency and strong consistency. Give a real-world example of a system that uses each.

---

## Exercises

**Exercise 1: Term Association**

Match each term to the problem it solves:
- Bloom filter -> ?
- Circuit breaker -> ?
- Consistent hashing -> ?
- Dead letter queue -> ?
- Write-ahead log -> ?

Problems: (a) Distributing keys evenly when nodes change, (b) Space-efficient set membership testing, (c) Preventing cascading failures, (d) Recovering from crashes without data loss, (e) Handling messages that repeatedly fail processing.

**Exercise 2: Build a Mini Glossary**

Pick a system you use daily (email, social media, streaming video). List 20 terms from this glossary that are relevant to how that system works. For each term, write one sentence explaining how it applies specifically to that system.

---

## Congratulations

You have made it through the entire book. From the fundamentals of scaling and load balancing, through databases, caching, message queues, and microservices, to designing real systems like URL shorteners, chat applications, and video platforms -- you now have a comprehensive toolkit for system design.

But this is not the end. It is the beginning of a much longer journey. Here is what to learn next:

### Keep Building Your Knowledge

1. **Read engineering blogs.** Companies like Netflix, Uber, Stripe, Airbnb, Meta, and Google regularly publish detailed posts about their architecture. These are the best source of real-world system design knowledge.

2. **Study open-source systems.** Read the documentation and architecture overviews of systems like Kafka, Cassandra, Elasticsearch, Kubernetes, and Redis. Understanding how these tools work internally makes you a stronger designer.

3. **Practice regularly.** Pick a new system design problem every week and work through it using the four-step framework from Chapter 32. Time yourself. Practice with a friend who can play the interviewer role.

4. **Build things.** The best way to understand distributed systems is to build one. Implement a simple key-value store with replication, or build a chat application with WebSockets, or create a URL shortener that handles thousands of requests per second.

5. **Go deeper on fundamentals.** Read "Designing Data-Intensive Applications" by Martin Kleppmann for a rigorous treatment of distributed systems fundamentals. Read the original papers on Raft consensus, Google's Spanner, Amazon's Dynamo, and Facebook's TAO.

6. **Stay current.** The field evolves rapidly. Serverless architectures, edge computing, AI-driven infrastructure, and new database technologies continue to reshape how we build systems.

### The Mindset That Matters

The most important thing this book teaches is not any specific pattern or technology. It is a way of thinking: start with requirements, estimate scale, design for the common case, plan for failure, and always understand the trade-offs. Every design decision has a cost. The art of system design is making the right trade-offs for your specific context.

You are ready. Go build great systems.
