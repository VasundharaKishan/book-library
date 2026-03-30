# Chapter 4: Caching

## What You Will Learn

- What caching is and why it is the single biggest performance lever in most systems
- The difference between a cache hit and a cache miss
- Core caching strategies: cache-aside, read-through, write-through, write-behind, and write-around
- How TTL (Time To Live) controls data freshness
- Eviction policies: LRU, LFU, FIFO, and when to choose each
- Redis vs Memcached and how to pick between them
- CDNs as a caching layer
- Distributed caching and its challenges
- Cache stampede, cache penetration, and cache avalanche -- and how to prevent them

## Why This Chapter Matters

Every millisecond of latency costs you users. Amazon found that every 100ms of latency costs them 1% in sales. Google found that an extra 0.5 seconds in search page generation dropped traffic by 20%.

Caching is the single most effective technique for reducing latency. It works by storing a copy of frequently accessed data in a faster storage layer so future requests can be served without going back to the slow original source.

If load balancing (Chapter 3) is about spreading work across servers, caching is about avoiding the work altogether. A request that never hits your database is infinitely faster than one that does.

---

## 4.1 What Is Caching?

Caching is the practice of storing copies of data in a temporary, fast-access storage layer so that future requests for the same data can be served more quickly.

### The Bookshelf Analogy

Imagine you are a student writing a research paper. You need to reference the same five books over and over.

**Without caching:** Every time you need a quote, you walk to the university library, find the book on the shelf, copy the passage, walk back to your desk, and use it. If you need the same quote ten minutes later, you make the same trip.

**With caching:** You borrow those five books and keep them on your desk. Now when you need a quote, you reach over and grab the book. No walking, no searching, no waiting.

Your desk is the cache. The library is the database. The books on your desk are cached data.

```
WITHOUT CACHING:

  You --> Walk to Library --> Find Book --> Copy Quote --> Walk Back
  You --> Walk to Library --> Find Book --> Copy Quote --> Walk Back
  You --> Walk to Library --> Find Book --> Copy Quote --> Walk Back

  Total time: 30 minutes (3 trips x 10 min each)


WITH CACHING:

  You --> Grab Book from Desk --> Copy Quote
  You --> Grab Book from Desk --> Copy Quote
  You --> Grab Book from Desk --> Copy Quote

  Total time: 30 seconds (3 lookups x 10 sec each)
```

### Where Caching Appears in a System

Caching is not a single technology -- it happens at every layer:

```
+----------+     +--------+     +-----------+     +--------+     +--------+
|  Browser |---->|  CDN   |---->|   Load    |---->|  App   |---->|  DB    |
|  Cache   |     |  Cache |     |  Balancer |     | Server |     |        |
+----------+     +--------+     +-----------+     +---+----+     +--------+
                                                      |
                                                      v
                                                 +----------+
                                                 | In-Memory|
                                                 |  Cache   |
                                                 | (Redis)  |
                                                 +----------+

Layer 1: Browser cache (images, CSS, JS)
Layer 2: CDN cache (static assets at the edge)
Layer 3: Application cache (Redis/Memcached)
Layer 4: Database query cache
Layer 5: CPU caches (L1, L2, L3)
```

### Speed Comparison

Understanding why caching works requires knowing how fast different storage layers are:

```
+---------------------+------------------+------------------+
| Storage Layer       | Access Time      | Analogy          |
+---------------------+------------------+------------------+
| CPU L1 Cache        | ~1 nanosecond    | Blink of an eye  |
| CPU L2 Cache        | ~4 nanoseconds   | One heartbeat    |
| RAM                 | ~100 nanoseconds | Snap your fingers|
| SSD Read            | ~100 microseconds| Deep breath      |
| HDD Read            | ~10 milliseconds | Make a coffee    |
| Network (same DC)   | ~0.5 milliseconds| Walk to mailbox  |
| Network (cross DC)  | ~50 milliseconds | Drive to store   |
+---------------------+------------------+------------------+

RAM is roughly 1,000x faster than SSD
SSD is roughly 100x faster than HDD
```

---

## 4.2 Cache Hit and Cache Miss

Every cache lookup results in one of two outcomes.

### Cache Hit

The requested data is found in the cache. The system returns it directly without going to the slower backend store. This is the fast path.

### Cache Miss

The requested data is NOT in the cache. The system must fetch it from the original source (database, API, disk), and then typically stores a copy in the cache for future requests.

```
CACHE HIT:
                                  +-------+
  Client ----> Request ---+       | Cache |
                          |  +--->| (HIT) |---+
                          |  |    +-------+   |
                          +--+                |
                             |                v
                             |          Return Data
                             |          (FAST: ~1ms)
                             |
                             X  (Database never touched)


CACHE MISS:
                                  +-------+
  Client ----> Request ---+       | Cache |
                          |  +--->| (MISS)|
                          |  |    +-------+
                          +--+        |
                                      | Not found!
                                      v
                                 +----------+
                                 | Database |
                                 +----+-----+
                                      |
                                      v
                                 Fetch Data
                                      |
                          +-----------+-----------+
                          |                       |
                          v                       v
                    Store in Cache          Return Data
                    (for next time)        (SLOW: ~50ms)
```

### Cache Hit Ratio

The **hit ratio** is the percentage of requests served from cache:

```
Hit Ratio = Cache Hits / (Cache Hits + Cache Misses) x 100

Example:
  950 hits + 50 misses = 1000 total requests
  Hit Ratio = 950 / 1000 = 95%
```

A good cache hit ratio is typically 90% or higher. Even going from 90% to 95% cuts your database load in half (from 10% misses to 5% misses).

---

## 4.3 Caching Strategies

There is no single "right" way to use a cache. Different strategies suit different access patterns. Here are the five most important ones.

### Cache-Aside (Lazy Loading)

This is the most common caching strategy. The application manages the cache explicitly.

**How it works:**
1. Application checks the cache first
2. If hit, return cached data
3. If miss, read from database
4. Write the result into cache
5. Return data to client

```
CACHE-ASIDE PATTERN:

         +----------+
         |  Client  |
         +----+-----+
              |
              v
         +----+-----+
         |   App    |
         |  Server  |
         +----+-----+
              |
         1. Check cache
              |
              v
         +----+-----+
         |   Cache  |-----> HIT? Return data (done!)
         +----+-----+
              |
              | MISS
              v
         +----+-----+
    2.   | Database |
         +----+-----+
              |
         3. Read data
              |
              v
         +----+-----+
    4.   |   Cache  |  <-- Store for next time
         +----+-----+
              |
         5. Return to client
```

**Pros:**
- Only requested data is cached (no wasted memory)
- Cache failure does not break the system (just slower)
- Simple to implement

**Cons:**
- First request is always a cache miss (cold start)
- Data can become stale (cache has old data while database has new data)
- Three round trips on a miss (check cache, read database, write cache)

**Best for:** Read-heavy workloads where you can tolerate slightly stale data.

### Read-Through Cache

Similar to cache-aside, but the cache itself is responsible for loading data from the database on a miss. The application only talks to the cache.

```
READ-THROUGH PATTERN:

         +----------+
         |  Client  |
         +----+-----+
              |
              v
         +----+-----+
         |   App    | -- Only talks to cache
         |  Server  |
         +----+-----+
              |
              v
         +----+-----+         +----------+
         |   Cache  |-------->| Database |
         +----------+         +----------+
            |    ^                  |
            |    |    On miss:      |
            |    +--- Cache loads --+
            |         data itself
            v
       Return data
```

**Pros:**
- Application code is simpler (no database-read-then-cache-write logic)
- Consistent data loading pattern

**Cons:**
- First request still has a miss penalty
- Cache library must support the read-through feature
- Harder to debug (logic hidden inside cache layer)

**Best for:** When you want to simplify application code and your cache library supports it.

### Write-Through Cache

Every write goes to the cache AND the database before confirming to the client. The cache always has fresh data.

```
WRITE-THROUGH PATTERN:

         +----------+
         |  Client  |
         +----+-----+
              |
         Write request
              |
              v
         +----+-----+
         |   App    |
         |  Server  |
         +----+-----+
              |
              v
         +----+-----+    Synchronous    +----------+
         |   Cache  |----- Write ------>| Database |
         +----+-----+                   +----------+
              |         Both must succeed
              |         before confirming
              v
         Return "OK"
```

**Pros:**
- Cache is always consistent with the database
- No stale reads
- Good when combined with read-through

**Cons:**
- Higher write latency (must write to both cache and database)
- Writes to data that is never read waste cache space
- More complex failure handling

**Best for:** Systems where data consistency is critical and you read the same data you write.

### Write-Behind (Write-Back) Cache

Writes go to the cache immediately, and the cache asynchronously flushes changes to the database later. The client gets a fast confirmation.

```
WRITE-BEHIND PATTERN:

         +----------+
         |  Client  |
         +----+-----+
              |
         Write request
              |
              v
         +----+-----+
         |   App    |
         |  Server  |
         +----+-----+
              |
              v
         +----+-----+       +----------+
    1.   |   Cache  |       | Database |
         +----+-----+       +----+-----+
              |                   ^
         2. Return "OK"          |
         (immediately!)          |
              |                  |
              +--- 3. Later ---->+
                   (async batch write)
```

**Pros:**
- Very low write latency (cache write is fast)
- Batch writes to database improve throughput
- Absorbs write spikes

**Cons:**
- Risk of data loss if cache crashes before flushing to database
- Complex to implement correctly
- Eventual consistency between cache and database

**Best for:** Write-heavy workloads where you can tolerate some data loss risk (counters, analytics, session data).

### Write-Around Cache

Writes go directly to the database, bypassing the cache. The cache is only populated when data is read.

```
WRITE-AROUND PATTERN:

         +----------+
         |  Client  |
         +----+-----+
              |
       +------+------+
       |              |
    Read            Write
       |              |
       v              v
  +----+-----+  +----+-----+
  |   Cache  |  | Database |  <-- Writes skip the cache
  +----+-----+  +----------+
       |
       | MISS? Load from DB
       v
  +----------+
  | Database |
  +----------+
```

**Pros:**
- Cache is not flooded with write data that may never be read
- Good for write-once, read-maybe workloads

**Cons:**
- Recently written data always causes a cache miss on first read
- Higher read latency for recently written data

**Best for:** Situations where data is written frequently but read infrequently.

### Strategy Comparison

```
+------------------+--------+--------+-----------+------------+
| Strategy         | Read   | Write  | Data Loss | Complexity |
|                  | Speed  | Speed  | Risk      |            |
+------------------+--------+--------+-----------+------------+
| Cache-Aside      | Fast*  | Normal | None      | Low        |
| Read-Through     | Fast*  | Normal | None      | Medium     |
| Write-Through    | Fast   | Slow   | None      | Medium     |
| Write-Behind     | Fast   | Fast   | Yes       | High       |
| Write-Around     | Slow** | Fast   | None      | Low        |
+------------------+--------+--------+-----------+------------+

*  After first miss
** For recently written data
```

---

## 4.4 TTL: Time To Live

A TTL is a timer attached to each cached entry. When the timer expires, the entry is removed (or marked stale). TTL controls how long data lives in the cache.

### Why TTL Matters

Without a TTL, cached data lives forever. If the underlying data changes, your cache serves stale results indefinitely.

```
WITHOUT TTL:
  t=0:   Cache stores user_123.name = "Alice"
  t=10m: User changes name to "Bob" in database
  t=1hr: Cache STILL returns "Alice"  <-- STALE!
  t=1day: Cache STILL returns "Alice" <-- VERY STALE!

WITH TTL of 5 minutes:
  t=0:   Cache stores user_123.name = "Alice" (TTL=5min)
  t=5m:  Cache entry expires, removed automatically
  t=6m:  Request comes in --> cache miss --> reads "Bob" from DB
         Cache stores "Bob" (TTL=5min)  <-- FRESH!
```

### Choosing the Right TTL

```
+----------------------+----------------+---------------------------+
| Data Type            | Suggested TTL  | Why                       |
+----------------------+----------------+---------------------------+
| User session         | 30 minutes     | Security + memory         |
| Product catalog      | 1-6 hours      | Changes infrequently      |
| Stock price          | 1-5 seconds    | Changes constantly        |
| Config/feature flags | 1-5 minutes    | Needs fast rollout        |
| Static assets (CSS)  | 1 year         | URL-versioned, never stale|
| Search results       | 5-15 minutes   | Good enough freshness     |
| DNS records          | 5 min - 48 hrs | Varies by provider        |
+----------------------+----------------+---------------------------+
```

### The Freshness vs Performance Trade-off

```
Short TTL (seconds)                    Long TTL (hours/days)
<------------------------------------------------------>
Fresh data                             Stale data
More DB load                           Less DB load
Lower hit ratio                        Higher hit ratio
Higher latency                         Lower latency
```

There is no universally correct TTL. It depends on how stale your data can be before users notice or care.

---

## 4.5 Cache Eviction Policies

Your cache has limited memory. When it is full and a new entry needs to be stored, the cache must decide which existing entry to remove. This decision is the eviction policy.

### LRU: Least Recently Used

Remove the entry that has not been accessed for the longest time.

**The analogy:** Your desk can hold 5 books. When you need a 6th, you put away the one you have not opened in the longest time.

```
LRU EXAMPLE (capacity = 4):

Access: A, B, C, D, E, A, F

Step 1: [A]              -- Add A
Step 2: [A, B]           -- Add B
Step 3: [A, B, C]        -- Add C
Step 4: [A, B, C, D]     -- Full!
Step 5: [B, C, D, E]     -- Add E, evict A (least recently used)
Step 6: [C, D, E, A]     -- Access A (fetched from DB), evict B
Step 7: [D, E, A, F]     -- Add F, evict C (least recently used)

Most recently used -->  [D, E, A, F]  <-- Least recently used
                         ^                 ^
                         |                 |
                     Keep these        Evict this next
```

**Pros:** Simple, works well for most workloads
**Cons:** A one-time scan of many items can pollute the cache (push out frequently used items)

**Used by:** Redis (approximated LRU), Memcached, most CPU caches

### LFU: Least Frequently Used

Remove the entry that has been accessed the fewest times.

**The analogy:** You keep count of how many times you open each book. When your desk is full, you put away the one you have opened the fewest times.

```
LFU EXAMPLE (capacity = 3):

Action                    Cache State              Access Counts
------                    -----------              -------------
Access A                  [A]                      A:1
Access A                  [A]                      A:2
Access B                  [A, B]                   A:2, B:1
Access C                  [A, B, C]  (Full!)       A:2, B:1, C:1
Access A                  [A, B, C]                A:3, B:1, C:1
Access D                  [A, D, C] or [A, B, D]   A:3, D:1, ...
                          ^-- Evict B or C (both have count=1)
```

**Pros:** Keeps genuinely popular items in cache
**Cons:** New items may be evicted too quickly (they start with count=1). Items that were popular long ago linger.

**Used by:** Redis (LFU mode), some CDN caches

### FIFO: First In, First Out

Remove the oldest entry, regardless of how recently or frequently it was accessed.

```
FIFO EXAMPLE (capacity = 3):

Access: A, B, C, D, B, E

Step 1: [A]
Step 2: [A, B]
Step 3: [A, B, C]     -- Full!
Step 4: [B, C, D]     -- Add D, evict A (first in)
Step 5: [B, C, D]     -- B is already cached (hit)
Step 6: [C, D, E]     -- Add E, evict B (first in)
                          ^-- Even though B was just accessed!
```

**Pros:** Very simple, predictable
**Cons:** Does not consider access patterns at all; can evict hot data

**Used by:** Some simple caching layers, message queues

### Random Replacement

Remove a random entry. Surprisingly effective in some workloads.

**Pros:** No overhead for tracking access patterns
**Cons:** Unpredictable; can evict hot data

### Eviction Policy Comparison

```
+---------+------------+---------------+----------+------------------+
| Policy  | Tracks     | Overhead      | Quality  | Best For         |
+---------+------------+---------------+----------+------------------+
| LRU     | Last access| Medium        | Good     | General purpose  |
| LFU     | Frequency  | Higher        | Better*  | Stable hotspots  |
| FIFO    | Insert time| Lowest        | Fair     | Simple systems   |
| Random  | Nothing    | Lowest        | OK       | When simplicity  |
|         |            |               |          | matters most     |
+---------+------------+---------------+----------+------------------+

* Better when popular items remain popular over time
```

---

## 4.6 Redis vs Memcached

These are the two most popular in-memory caching systems. Both store data in RAM for fast access, but they differ in important ways.

### Redis

Redis (Remote Dictionary Server) is an in-memory data store that supports rich data structures.

**Key features:**
- Data structures: strings, hashes, lists, sets, sorted sets, bitmaps, streams
- Persistence: can snapshot to disk (RDB) or log every write (AOF)
- Replication: leader-follower replication for high availability
- Clustering: built-in sharding across multiple nodes
- Pub/Sub: built-in messaging
- Lua scripting: atomic operations
- TTL support per key

### Memcached

Memcached is a high-performance, distributed memory caching system. It does one thing and does it well: key-value caching.

**Key features:**
- Simple key-value store (string keys, string/binary values)
- Multi-threaded architecture (uses all CPU cores)
- No persistence (pure cache, data lost on restart)
- No replication (each node is independent)
- Simple protocol (easy to implement clients)
- Slab-based memory allocation (predictable memory usage)

### Comparison

```
+--------------------+-------------------+-------------------+
| Feature            | Redis             | Memcached         |
+--------------------+-------------------+-------------------+
| Data structures    | Rich (lists, sets | Simple (string    |
|                    | hashes, sorted    | key-value only)   |
|                    | sets, etc.)       |                   |
+--------------------+-------------------+-------------------+
| Persistence        | Yes (RDB + AOF)   | No                |
+--------------------+-------------------+-------------------+
| Replication        | Yes (leader-      | No                |
|                    | follower)         |                   |
+--------------------+-------------------+-------------------+
| Clustering         | Yes (built-in)    | Client-side only  |
+--------------------+-------------------+-------------------+
| Threading          | Single-threaded*  | Multi-threaded    |
+--------------------+-------------------+-------------------+
| Max value size     | 512 MB            | 1 MB (default)    |
+--------------------+-------------------+-------------------+
| Memory efficiency  | Higher overhead   | Lower overhead    |
+--------------------+-------------------+-------------------+
| Pub/Sub            | Yes               | No                |
+--------------------+-------------------+-------------------+
| Scripting          | Lua scripts       | No                |
+--------------------+-------------------+-------------------+

* Redis 6+ has I/O threading for network operations
```

### When to Choose Which

**Choose Redis when:**
- You need data structures beyond simple key-value (leaderboards, queues, sessions)
- You need persistence (data survives restarts)
- You need replication or clustering
- You need pub/sub or message brokering

**Choose Memcached when:**
- You need simple, fast key-value caching
- You want to maximize memory efficiency for caching
- You want multi-threaded performance on a single node
- Your caching needs are straightforward

In practice, Redis has become the default choice for most teams because of its versatility. Memcached remains popular for large-scale simple caching (Facebook uses it extensively).

---

## 4.7 CDN as a Cache

A CDN (Content Delivery Network) is essentially a geographically distributed cache. It stores copies of your content on servers around the world so users can access it from a nearby location.

We will cover CDNs in depth in Chapter 5. Here is how they fit into the caching picture:

```
WITHOUT CDN:
  User in Tokyo --> Request travels to Server in New York
  Latency: ~200ms

WITH CDN:
  User in Tokyo --> CDN Edge Server in Tokyo (cached copy)
  Latency: ~20ms

                     +-- Edge: Tokyo
                     |
  Origin Server -----+-- Edge: London
  (New York)         |
                     +-- Edge: Sydney
                     |
                     +-- Edge: Sao Paulo

  Each edge server caches content from the origin.
  Users connect to the nearest edge.
```

CDNs primarily cache static content (images, CSS, JavaScript, videos) but can also cache API responses and dynamically generated pages.

---

## 4.8 Distributed Caching

When your application runs on multiple servers, you have a choice: each server has its own local cache, or all servers share a distributed cache.

### Local Cache vs Distributed Cache

```
LOCAL CACHE (each server has its own):

  +----------+     +----------+     +----------+
  | Server 1 |     | Server 2 |     | Server 3 |
  | +------+ |     | +------+ |     | +------+ |
  | |Cache | |     | |Cache | |     | |Cache | |
  | |A,B,C | |     | |A,D,E | |     | |B,F,G | |
  | +------+ |     | +------+ |     | +------+ |
  +----------+     +----------+     +----------+

  Problem: Data duplicated. Server 1 updates A,
  but Server 2 still has the old copy of A.


DISTRIBUTED CACHE (shared by all servers):

  +----------+     +----------+     +----------+
  | Server 1 |     | Server 2 |     | Server 3 |
  +-----+----+     +-----+----+     +-----+----+
        |                |                |
        +--------+-------+--------+-------+
                 |                |
           +-----+-----+   +-----+-----+
           |  Cache     |   |  Cache    |
           |  Node 1    |   |  Node 2   |
           |  A,B,C,D   |   |  E,F,G   |
           +------------+   +-----------+

  All servers see the same cache.
  Data is partitioned across cache nodes.
```

### Benefits of Distributed Cache

- **Consistency:** All application servers see the same cached data
- **Capacity:** Cache can be larger than any single machine's RAM
- **Survivability:** If one app server restarts, the cache is not lost
- **Scalability:** Add more cache nodes as data grows

### Challenges of Distributed Cache

- **Network latency:** Cache is accessed over the network (~0.5ms) vs in-process (~0.001ms)
- **Serialization cost:** Data must be serialized/deserialized for network transfer
- **Operational complexity:** Another system to deploy, monitor, and maintain
- **Partitioning:** You need a strategy to distribute keys across nodes (see Chapter 12: Consistent Hashing)

---

## 4.9 Cache Problems and Solutions

Caching introduces its own set of problems. Understanding these is critical for building reliable systems.

### Cache Stampede (Thundering Herd)

**The problem:** A popular cache entry expires. Hundreds of requests simultaneously find a cache miss and all hit the database at once, overwhelming it.

```
CACHE STAMPEDE:

  t=0: Cache entry for "hot_product" expires

  t=0.001s:  Request 1 --> Cache MISS --> Query DB
  t=0.002s:  Request 2 --> Cache MISS --> Query DB
  t=0.003s:  Request 3 --> Cache MISS --> Query DB
  ...
  t=0.050s:  Request 100 --> Cache MISS --> Query DB

  Database receives 100 identical queries simultaneously!

           +------+------+------+------+------+
           | Req1 | Req2 | Req3 | ...  |Req100|
           +--+---+--+---+--+---+--+---+--+---+
              |      |      |      |      |
              v      v      v      v      v
           +-------------------------------+
           |          DATABASE              |
           |      (OVERWHELMED!)            |
           +-------------------------------+
```

**Solutions:**

1. **Locking:** Only the first request on a miss fetches from the database. Other requests wait for the cache to be repopulated.

```
WITH LOCKING:
  Request 1 --> Cache MISS --> Acquire lock --> Query DB --> Update cache
  Request 2 --> Cache MISS --> Lock taken, WAIT...
  Request 3 --> Cache MISS --> Lock taken, WAIT...
  ...
  Cache updated! --> Requests 2, 3, ... --> Cache HIT
```

2. **Early expiration (stale-while-revalidate):** Start refreshing the cache before it actually expires. Serve slightly stale data while fetching fresh data in the background.

3. **Jittered TTL:** Add a random offset to TTLs so entries do not all expire at the same time.

```
Without jitter: All entries expire at t=300s
With jitter:    Entry A expires at t=287s
                Entry B expires at t=312s
                Entry C expires at t=295s
```

### Cache Penetration

**The problem:** Repeated requests for data that does not exist. Each request misses the cache and hits the database, which also returns nothing. The cache never gets populated.

```
CACHE PENETRATION:

  Request for user_id=999999 (does not exist)
  --> Cache MISS
  --> Database query returns EMPTY
  --> Nothing to cache!
  --> Next request: same thing again

  Attacker sends millions of requests for non-existent IDs
  --> Every single one hits the database!
```

**Solutions:**

1. **Cache null results:** Store a "not found" marker in the cache with a short TTL.

```
Cache key: "user:999999" --> value: "NULL" (TTL=60s)
```

2. **Bloom filter:** A space-efficient data structure that can quickly tell you if an item definitely does NOT exist. Check the Bloom filter before checking the cache or database.

```
WITH BLOOM FILTER:

  Request for user_id=999999
  --> Check Bloom filter: "Definitely not in database"
  --> Return "not found" immediately
  --> Database never touched!
```

### Cache Avalanche

**The problem:** A large number of cache entries expire at the same time (or the entire cache goes down), causing a massive spike in database load.

```
CACHE AVALANCHE:

  t=0: All cache entries set with TTL=3600s
  t=3600s: EVERYTHING expires at once!

  +---+---+---+---+---+---+---+---+
  | A | B | C | D | E | F | G | H |  ALL EXPIRED!
  +---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |
    v   v   v   v   v   v   v   v
  +-----------------------------------+
  |            DATABASE                |
  |          (CRUSHED!)                |
  +-----------------------------------+
```

**Solutions:**

1. **Jittered TTL:** Spread expiration times randomly
2. **Multi-level caching:** Use a local cache as a fallback when the distributed cache is down
3. **Cache warm-up:** Pre-populate the cache before it goes live
4. **Circuit breaker:** If the database is overwhelmed, fail fast instead of queuing more requests

---

## 4.10 Cache Invalidation

Cache invalidation -- deciding when to remove or update cached data -- is one of the hardest problems in computer science.

> "There are only two hard things in Computer Science: cache invalidation and naming things." -- Phil Karlton

### Common Invalidation Strategies

**1. TTL-based expiration:** Set a timer. Data is removed when the timer expires. Simple but blunt.

**2. Event-driven invalidation:** When the source data changes, actively delete or update the cache entry.

```
EVENT-DRIVEN INVALIDATION:

  1. User updates profile
  2. App writes new data to database
  3. App deletes cache entry for that user
  4. Next read triggers cache miss --> loads fresh data

  +--------+    2. Write    +----------+
  |  App   |--------------->| Database |
  +---+----+                +----------+
      |
      | 3. Delete cache entry
      v
  +--------+
  |  Cache |  key "user:123" DELETED
  +--------+
```

**3. Version-based invalidation:** Include a version number in the cache key. When data changes, increment the version.

```
Version-based:
  v1: cache key = "product:42:v1"
  v2: cache key = "product:42:v2"  <-- New version, old key ignored
```

---

## Common Mistakes

1. **Caching everything.** Only cache data that is read frequently. Caching rarely-read data wastes memory.

2. **No TTL.** Always set a TTL. Without one, stale data lives forever.

3. **Ignoring cache warm-up.** After a deploy or restart, the cache is empty. All requests hit the database. Pre-populate the cache with hot data.

4. **Not monitoring cache hit ratio.** If your hit ratio drops, something is wrong. Monitor it.

5. **Treating cache as a source of truth.** A cache is temporary. Data can be evicted at any time. Your system must work (slowly) without the cache.

6. **Same TTL for all keys.** Different data types need different TTLs. A stock price and a user profile should not share the same expiration.

7. **No plan for cache failure.** If Redis goes down, can your system still serve requests? If not, you have a single point of failure.

---

## Best Practices

1. **Start with cache-aside.** It is the simplest and most flexible strategy. Add complexity only when needed.

2. **Set appropriate TTLs.** Balance freshness and performance for each data type.

3. **Add jitter to TTLs.** Prevent mass expiration by adding random offsets.

4. **Monitor hit ratio, latency, and eviction rate.** These three metrics tell you if your cache is healthy.

5. **Use consistent hashing for distributed caches.** See Chapter 12 for details.

6. **Cache at multiple levels.** Browser cache, CDN, application cache, and database cache each serve different purposes.

7. **Design for cache failure.** Your system should degrade gracefully, not crash, when the cache is unavailable.

8. **Use the right eviction policy.** LRU is a safe default. Switch to LFU if you have stable hotspots.

9. **Keep cached objects small.** Smaller objects mean faster serialization, lower memory usage, and better hit ratios.

10. **Invalidate on writes.** When data changes, invalidate or update the cache immediately rather than waiting for TTL expiration.

---

## Quick Summary

Caching stores copies of frequently accessed data in a fast storage layer to reduce latency and database load. The main strategies are cache-aside (application manages the cache), read-through and write-through (cache manages itself), write-behind (async writes for speed), and write-around (writes bypass cache). TTL controls how long data stays cached. When the cache is full, eviction policies (LRU, LFU, FIFO) decide what to remove. Redis and Memcached are the most popular cache systems. Watch out for cache stampede (many requests hitting DB on expiry), cache penetration (requests for non-existent data), and cache avalanche (mass expiration). Cache invalidation remains one of the hardest problems in computing.

---

## Key Points

- A cache hit serves data from fast storage; a cache miss requires fetching from the slow original source
- Cache-aside is the most common strategy: check cache first, fall back to database on miss
- Write-through ensures consistency but adds write latency; write-behind is fast but risks data loss
- TTL controls freshness -- short TTLs mean fresher data but more DB load
- LRU (evict least recently used) is the best default eviction policy
- Redis is more feature-rich; Memcached is simpler and more memory-efficient for pure caching
- Cache stampede, penetration, and avalanche are the three main cache failure modes
- Always design your system to work without the cache -- just slower

---

## Practice Questions

1. You have an e-commerce site where product prices change once a day but product pages are viewed millions of times. Which caching strategy would you use, and what TTL would you set? Why?

2. Your cache hit ratio drops from 95% to 60% after a new feature deployment. What are three possible causes, and how would you investigate each?

3. You are designing a social media feed. Users see posts from people they follow. Should you cache the feed per user, or cache individual posts and assemble feeds on the fly? What are the trade-offs of each approach?

4. Explain why write-behind caching is risky for financial transactions but acceptable for view counters.

5. Your Redis cache is running at 95% memory capacity. What steps would you take to address this before it starts evicting important data?

---

## Exercises

**Exercise 1: Design a Cache Layer**
You are building a news website. Articles are written by editors and published once. After publication, an article rarely changes but is read millions of times. Design the caching strategy. Specify: which caching strategy, TTL, eviction policy, and how you handle article updates.

**Exercise 2: Cache Stampede Simulation**
Draw a timeline showing what happens when a cache entry with 1000 requests per second expires. Then draw a second timeline showing the same scenario with a locking mechanism. Label the database load at each point.

**Exercise 3: Redis vs Memcached Decision**
You are building three different systems: (a) a session store for a web app, (b) a simple page cache for a static website, (c) a real-time leaderboard for a game. For each, recommend Redis or Memcached and explain your reasoning.

---

## What Is Next?

In this chapter, you learned how caching speeds up your system by keeping frequently accessed data close to where it is needed. One of the most powerful forms of caching is the CDN -- a globally distributed cache that brings content physically closer to your users. In Chapter 5, you will learn how CDNs work, when to use them, and how they fit into your overall system architecture.
