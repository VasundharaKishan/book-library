# Chapter 21: Designing a URL Shortener (TinyURL / Bit.ly)

You click a short link like `https://bit.ly/3xK9mQ2` and instantly land on a long, complicated URL. Behind that tiny redirect lives a fascinating system that handles billions of requests, stores hundreds of millions of mappings, and responds in single-digit milliseconds. In this chapter, we will design that system from scratch.

A URL shortener is one of the most popular system design interview questions, and for good reason. It is simple enough to explain in five minutes yet deep enough to explore caching, hashing, databases, analytics, and horizontal scaling. By the end of this chapter you will have a production-ready blueprint you can confidently walk through in any interview.

---

## 21.1 Understanding the Problem

Before we draw a single box on a whiteboard, let us make sure we agree on what we are building.

A URL shortener takes a long URL such as:

```
https://www.example.com/products/electronics/smartphones/iphone-15-pro-max?color=blue&storage=256gb&ref=homepage_banner_campaign_2024
```

and converts it into something like:

```
https://short.ly/aB3kQ7z
```

When a user visits the short URL, the system looks up the original long URL and redirects the browser.

### Why Do People Use URL Shorteners?

1. **Sharing on character-limited platforms.** A tweet or SMS has limited space.
2. **Tracking clicks.** Marketers want to know how many people clicked a link, from which country, and on what device.
3. **Aesthetics.** A clean, short link looks better in emails, presentations, and printed material.
4. **Custom branding.** Companies create branded short domains (`youtu.be`, `amzn.to`) to reinforce trust.

---

## 21.2 Requirements

### Functional Requirements

| # | Requirement | Description |
|---|-------------|-------------|
| F1 | **Shorten a URL** | Given a long URL, generate a unique short URL. |
| F2 | **Redirect** | When a user visits the short URL, redirect to the original long URL. |
| F3 | **Custom aliases** | Allow users to pick a custom short code (e.g., `short.ly/my-brand`). |
| F4 | **Expiration** | URLs can optionally expire after a set time. |
| F5 | **Analytics** | Track click count, timestamp, referrer, country, and device for each short URL. |

### Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NF1 | **High availability** | 99.99% uptime. Redirects must always work. |
| NF2 | **Low latency** | Redirect in under 10 ms (p99). |
| NF3 | **Scalability** | Handle 100 million new URLs per day and 10 billion redirects per day. |
| NF4 | **Durability** | Once a short URL is created, it must never be lost. |
| NF5 | **No collisions** | Two different long URLs must never map to the same short code. |

### Out of Scope

- User accounts and authentication (we will keep the design focused).
- Spam or malware detection (important in production but orthogonal to core design).

---

## 21.3 Back-of-the-Envelope Estimation

Good estimations show the interviewer you can think about scale before you start drawing boxes.

### Traffic

| Metric | Value |
|--------|-------|
| New URLs per day | 100 million |
| New URLs per second | 100M / 86,400 ≈ **1,160 URLs/s** |
| Read-to-write ratio | ~100:1 (reads dominate) |
| Redirects per second | 1,160 x 100 = **116,000 redirects/s** |

This is a heavily **read-heavy** system. Caching will be critical.

### Storage

| Item | Size |
|------|------|
| Short code | 7 characters = 7 bytes |
| Long URL (average) | 200 bytes |
| Created timestamp | 8 bytes |
| Expiration timestamp | 8 bytes |
| User ID (optional) | 8 bytes |
| **Total per record** | **~250 bytes** |

Over five years:

```
100M URLs/day x 365 days x 5 years = 182.5 billion URLs
182.5 billion x 250 bytes ≈ 45.6 TB
```

That is manageable with modern distributed databases.

### Key Space

If we use a 7-character short code with base62 encoding (a-z, A-Z, 0-9):

```
62^7 = 3.52 trillion unique codes
```

With 182.5 billion URLs over 5 years, we use about 5% of the key space. Plenty of room.

### Bandwidth

| Direction | Calculation | Result |
|-----------|-------------|--------|
| Write (incoming) | 1,160 URLs/s x 250 bytes | ~290 KB/s |
| Read (outgoing) | 116,000 req/s x 250 bytes | ~29 MB/s |

Very lightweight. This system is not bandwidth-bound; it is latency-bound.

### Cache

If we follow the 80/20 rule (20% of URLs generate 80% of traffic), caching the top 20% of daily redirects:

```
116,000 req/s x 86,400 seconds = ~10 billion redirects/day
20% of unique URLs accessed daily ≈ 20M URLs
20M x 250 bytes ≈ 5 GB of cache
```

Five gigabytes fits easily in a single Redis instance, though we will use a cluster for redundancy.

---

## 21.4 High-Level Design

Here is the architecture at a glance:

```
                         ┌──────────────────┐
                         │   Load Balancer   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
              ┌─────▼─────┐ ┌────▼─────┐ ┌────▼─────┐
              │  App Server│ │App Server│ │App Server│
              │  (Write)   │ │ (Read)   │ │ (Read)   │
              └─────┬──────┘ └────┬─────┘ └────┬─────┘
                    │             │             │
                    │        ┌────▼─────────────▼───┐
                    │        │     Cache Cluster     │
                    │        │       (Redis)         │
                    │        └────────┬──────────────┘
                    │                 │ (cache miss)
              ┌─────▼─────────────────▼──────────┐
              │          Database Cluster          │
              │     (Key-Value / NoSQL Store)      │
              │  ┌──────┐ ┌──────┐ ┌──────┐       │
              │  │Shard 1│ │Shard 2│ │Shard N│     │
              │  └──────┘ └──────┘ └──────┘       │
              └──────────────────────────────────┘
                    │
              ┌─────▼──────────────────────┐
              │   Analytics Pipeline        │
              │  (Kafka -> Spark -> OLAP)   │
              └────────────────────────────┘
```

### Request Flows

**Flow 1: Shorten a URL (Write)**

1. Client sends `POST /api/v1/shorten` with the long URL.
2. Load balancer routes to an app server.
3. App server generates a unique short code (we will discuss how shortly).
4. App server writes `(short_code -> long_url)` to the database.
5. App server returns the short URL to the client.

**Flow 2: Redirect (Read)**

1. User clicks `https://short.ly/aB3kQ7z`.
2. Load balancer routes to an app server.
3. App server checks the cache for `aB3kQ7z`.
4. **Cache hit:** Return the long URL immediately.
5. **Cache miss:** Query the database, populate the cache, return the long URL.
6. App server responds with an HTTP redirect (301 or 302).
7. App server asynchronously sends a click event to the analytics pipeline.

---

## 21.5 Deep Dive: Short Code Generation

This is the heart of the system. How do we turn a long URL into a unique 7-character code? There are several approaches, each with trade-offs.

### Approach 1: Hash + Truncate

Take the long URL, hash it with MD5 or SHA-256, then take the first 7 characters of the base62-encoded hash.

```
long_url = "https://www.example.com/very/long/path"
hash     = MD5(long_url)          # 128-bit hash
base62   = base62_encode(hash)    # "aB3kQ7zXm9pL..."
code     = base62[:7]             # "aB3kQ7z"
```

**Pros:**
- Simple to implement.
- Same input always produces the same output (deterministic).
- No coordination needed between servers.

**Cons:**
- **Collisions.** Truncating a hash to 7 characters means collisions will happen. With the birthday paradox, collisions become likely after roughly `sqrt(62^7)` ≈ 1.9 million URLs. We generate 100 million per day, so collisions will be frequent.

**Collision handling:** When a collision is detected (the short code already exists in the database), we can append a counter or a random salt to the URL and re-hash:

```python
def generate_short_code(long_url):
    for attempt in range(MAX_RETRIES):
        candidate = base62(md5(long_url + str(attempt)))[:7]
        if not database.exists(candidate):
            return candidate
    raise Exception("Failed to generate unique code")
```

This works but adds latency on collisions and requires a database check for every generation.

### Approach 2: Pre-Generated Key Service (Recommended)

Maintain a separate **Key Generation Service (KGS)** that pre-generates unique 7-character codes and stores them in a database. When an app server needs a new code, it grabs one from the pool.

```
┌────────────────┐     ┌──────────────────────────┐
│ Key Generation  │     │     Key Database          │
│    Service      │────>│  ┌────────┐ ┌──────────┐ │
│                 │     │  │ Unused │ │   Used   │ │
└────────────────┘     │  │ Keys   │ │   Keys   │ │
                        │  └────────┘ └──────────┘ │
                        └──────────────────────────┘
                                  │
                        ┌─────────▼─────────┐
                        │    App Servers     │
                        │ (grab keys in      │
                        │  batches of 1000)  │
                        └───────────────────┘
```

**How it works:**

1. KGS generates millions of random 7-character base62 strings and stores them in an "unused" table.
2. When an app server starts (or runs low), it requests a batch of keys (say, 1,000) from KGS.
3. KGS moves those keys from "unused" to "used" in a single atomic transaction.
4. The app server assigns keys from its local batch. No coordination with other servers needed.
5. If the server crashes, we lose at most 1,000 keys. With 3.52 trillion possible keys, this is negligible.

**Pros:**
- Zero collisions (keys are unique by construction).
- Extremely fast (no hashing, no database check per URL).
- Scales horizontally (each server has its own batch).

**Cons:**
- Extra component (the KGS) to maintain.
- A small number of keys are wasted if a server crashes mid-batch.

### Approach 3: Counter-Based with Base62

Use a global counter (or distributed counter like a Snowflake ID generator) and encode it in base62.

```
counter = 1000000      # auto-incrementing
code    = base62(1000000)  # "4c92"
```

**Pros:**
- Guaranteed unique.
- Sequential, so database writes are sequential (good for B-tree indexes).

**Cons:**
- Short codes are predictable. Competitors can enumerate your URLs.
- Requires a centralized counter or a distributed ID generator like Twitter Snowflake.

To hide the sequence, you can apply a bijective shuffle (a reversible permutation) before encoding.

### Recommendation

Use the **Pre-Generated Key Service** for production systems. It gives zero collisions, no coordination overhead, and scales cleanly. Use the hash approach when you need deterministic mappings (same URL always gets the same code).

---

## 21.6 Deep Dive: 301 vs. 302 Redirect

When the app server returns the long URL, it sends an HTTP redirect. But which status code?

| Status Code | Meaning | Browser Behavior |
|-------------|---------|------------------|
| **301 Moved Permanently** | The short URL permanently maps to the long URL. | Browser caches the redirect. Future clicks skip our servers entirely. |
| **302 Found** (Temporary) | The mapping might change. | Browser does not cache. Every click hits our servers. |

### Which Should We Use?

It depends on our priorities:

- **Use 301** if you want to reduce server load. Once the browser caches the redirect, it never asks our server again. But we lose analytics data for repeat visitors.
- **Use 302** if you want accurate analytics. Every click hits our servers, so we can count every visit, track referrers, and measure unique vs. returning visitors.

**Most URL shorteners use 302** because analytics are a key selling point. Bit.ly, for example, uses 302 so it can track every single click.

If you want the best of both worlds, use 302 for analytics but set a short `Cache-Control` header (e.g., 5 minutes) so the browser caches briefly to handle rapid double-clicks.

---

## 21.7 Deep Dive: Database Choice

### Why Key-Value Store?

Our access pattern is simple:
- **Write:** `PUT(short_code, long_url_record)`
- **Read:** `GET(short_code) -> long_url_record`

There are no complex joins, no range queries, no transactions spanning multiple records. This is a textbook use case for a key-value store.

### Options

| Database | Strengths | Considerations |
|----------|-----------|----------------|
| **DynamoDB** | Fully managed, auto-scaling, single-digit ms latency | Cost at extreme scale |
| **Cassandra** | High write throughput, linear scalability | Operational complexity |
| **Redis (persistent)** | Blazing fast, simple API | Memory cost for 45 TB |
| **MongoDB** | Flexible schema, good tooling | Less ideal for pure KV |

**Recommendation:** DynamoDB or Cassandra. Both handle our scale (100M+ writes/day) with ease and shard automatically.

### Database Schema

```
Table: url_mappings
┌──────────────┬───────────────┬──────────────┐
│ Column       │ Type          │ Notes        │
├──────────────┼───────────────┼──────────────┤
│ short_code   │ VARCHAR(7)    │ Primary Key  │
│ long_url     │ VARCHAR(2048) │ NOT NULL     │
│ created_at   │ TIMESTAMP     │ NOT NULL     │
│ expires_at   │ TIMESTAMP     │ NULLABLE     │
│ user_id      │ VARCHAR(36)   │ NULLABLE     │
│ custom_alias │ BOOLEAN       │ DEFAULT false│
└──────────────┴───────────────┴──────────────┘

Table: analytics_events  (in OLAP store like ClickHouse)
┌──────────────┬───────────────┬──────────────┐
│ Column       │ Type          │ Notes        │
├──────────────┼───────────────┼──────────────┤
│ event_id     │ UUID          │ Primary Key  │
│ short_code   │ VARCHAR(7)    │ Indexed      │
│ clicked_at   │ TIMESTAMP     │ NOT NULL     │
│ referrer     │ VARCHAR(2048) │ NULLABLE     │
│ user_agent   │ VARCHAR(512)  │ NULLABLE     │
│ ip_address   │ VARCHAR(45)   │ For geo-loc  │
│ country      │ VARCHAR(2)    │ Derived      │
│ device_type  │ VARCHAR(20)   │ Derived      │
└──────────────┴───────────────┴──────────────┘
```

---

## 21.8 API Design

### Create Short URL

```
POST /api/v1/urls
Content-Type: application/json

Request:
{
    "long_url": "https://www.example.com/very/long/path",
    "custom_alias": "my-brand",       // optional
    "expires_at": "2025-12-31T23:59:59Z"  // optional
}

Response: 201 Created
{
    "short_url": "https://short.ly/my-brand",
    "short_code": "my-brand",
    "long_url": "https://www.example.com/very/long/path",
    "created_at": "2024-06-15T10:30:00Z",
    "expires_at": "2025-12-31T23:59:59Z"
}
```

### Redirect

```
GET /{short_code}
Example: GET /aB3kQ7z

Response: 302 Found
Location: https://www.example.com/very/long/path
```

### Get Analytics

```
GET /api/v1/urls/{short_code}/analytics

Response: 200 OK
{
    "short_code": "aB3kQ7z",
    "total_clicks": 42567,
    "unique_visitors": 31204,
    "clicks_by_country": {
        "US": 18234,
        "UK": 8912,
        "IN": 5601
    },
    "clicks_by_device": {
        "mobile": 25540,
        "desktop": 15123,
        "tablet": 1904
    },
    "clicks_over_time": [
        {"date": "2024-06-15", "clicks": 1234},
        {"date": "2024-06-16", "clicks": 2345}
    ]
}
```

### Delete Short URL

```
DELETE /api/v1/urls/{short_code}

Response: 204 No Content
```

---

## 21.9 Deep Dive: Cache Layer

With 116,000 redirects per second and a read-to-write ratio of 100:1, caching is essential.

### Cache Strategy

We use **cache-aside** (also called lazy loading):

```
┌──────────┐     ┌───────┐     ┌──────────┐
│ App      │────>│ Redis │     │ Database │
│ Server   │     │ Cache │     │          │
│          │<────│       │     │          │
│          │     └───────┘     │          │
│          │         │         │          │
│          │    (cache miss)   │          │
│          │─────────────────->│          │
│          │<──────────────────│          │
│          │                   │          │
│          │──(populate cache) │          │
│          │────>│ Redis │     │          │
└──────────┘     └───────┘     └──────────┘
```

1. App server checks Redis for the short code.
2. **Hit:** Return the long URL. Done.
3. **Miss:** Query the database, write the result to Redis with a TTL, return the long URL.

### Eviction Policy

Use **LRU (Least Recently Used)** eviction. Popular URLs stay in cache; rarely accessed URLs get evicted naturally.

### Cache Sizing

From our estimation, we need about 5 GB for the top 20% of URLs. A Redis cluster with 3 nodes (each 4 GB, with replication) handles this comfortably.

### Cache Invalidation

- **On expiration:** When a URL expires, we do not need to actively remove it from cache. Set the Redis TTL to match the URL's expiration time, and Redis will evict it automatically.
- **On deletion:** When a user deletes a short URL, explicitly remove it from cache.
- **On update:** If we allow updating the long URL for a short code, invalidate the cache entry on update.

---

## 21.10 Deep Dive: Analytics Pipeline

Analytics must not slow down the redirect path. We use an asynchronous pipeline.

```
┌────────────┐     ┌─────────┐     ┌──────────────┐     ┌────────────┐
│ App Server │────>│  Kafka  │────>│ Stream       │────>│  OLAP DB   │
│ (click     │     │ (event  │     │ Processor    │     │(ClickHouse │
│  event)    │     │  queue) │     │ (Flink/Spark)│     │ or Druid)  │
└────────────┘     └─────────┘     └──────────────┘     └────────────┘
```

1. When a redirect happens, the app server fires a click event to Kafka (fire-and-forget, non-blocking).
2. A stream processor (Apache Flink or Spark Streaming) consumes events, enriches them (geo-IP lookup, device parsing), and writes aggregated results to an OLAP database.
3. The analytics API reads from the OLAP database.

This decoupling means:
- Redirect latency is unaffected by analytics processing.
- We can replay Kafka events if the OLAP database needs rebuilding.
- Analytics processing can scale independently.

---

## 21.11 Deep Dive: Custom Aliases

When a user requests a custom alias like `short.ly/my-brand`, we need to:

1. **Validate the alias:** Only allow alphanumeric characters, hyphens, and underscores. Reject reserved words (`api`, `admin`, `health`).
2. **Check uniqueness:** Query the database to ensure the alias is not taken.
3. **Store it:** Save it just like an auto-generated code. The `custom_alias` flag in the schema marks it as user-chosen.

Custom aliases bypass the Key Generation Service entirely. The user provides the key; we just validate and store it.

### Potential Issues

- **Squatting:** Someone might reserve popular aliases. Consider requiring authentication for custom aliases.
- **Length limits:** Custom aliases should be between 3 and 30 characters. Too short risks collisions with auto-generated codes; too long defeats the purpose.

---

## 21.12 Deep Dive: URL Expiration

Some URLs should expire after a set period (e.g., a promotional link valid for 30 days).

### How It Works

1. When creating a URL, the user optionally provides an `expires_at` timestamp.
2. During redirect, the app server checks if `expires_at` has passed.
3. If expired, return a 410 Gone response instead of redirecting.

### Cleanup

Expired URLs still consume storage. We need a cleanup process:

- **Lazy cleanup:** Check expiration on read. If expired, delete and return 410. Simple but leaves dead data in the database.
- **Active cleanup:** A background job scans for expired URLs and deletes them periodically (e.g., every hour). Use a secondary index on `expires_at` for efficient scanning.
- **Database TTL:** Some databases (DynamoDB, Cassandra) support native TTL on records. The database automatically deletes expired records. This is the simplest approach.

---

## 21.13 Scaling Considerations

### Database Sharding

With 45 TB over 5 years, we need to shard the database. The **short code** is the natural shard key because:

- All lookups are by short code (point queries).
- Short codes are random (with the KGS approach), ensuring even distribution.
- No cross-shard queries needed.

Use consistent hashing to distribute short codes across shards, allowing us to add shards without massive data migration.

### App Server Scaling

App servers are stateless (they hold a batch of pre-generated keys in memory, but losing them is acceptable). We can auto-scale horizontally based on request rate.

### Read Replicas

For the database, add read replicas to handle the read-heavy workload. Writes go to the primary; reads go to replicas.

### Geographic Distribution

Deploy the service in multiple regions. Use a global load balancer (e.g., AWS Global Accelerator, Cloudflare) to route users to the nearest region. Each region has its own cache cluster. The database can use multi-region replication (DynamoDB Global Tables or Cassandra multi-datacenter).

```
                    ┌───────────────────┐
                    │  Global DNS/LB    │
                    └───────┬───────────┘
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼─────┐ ┌────▼──────┐ ┌────▼──────┐
        │ US-East   │ │ EU-West   │ │ AP-South  │
        │ ┌───────┐ │ │ ┌───────┐ │ │ ┌───────┐ │
        │ │ App   │ │ │ │ App   │ │ │ │ App   │ │
        │ │Servers│ │ │ │Servers│ │ │ │Servers│ │
        │ └───────┘ │ │ └───────┘ │ │ └───────┘ │
        │ ┌───────┐ │ │ ┌───────┐ │ │ ┌───────┐ │
        │ │ Cache │ │ │ │ Cache │ │ │ │ Cache │ │
        │ └───────┘ │ │ └───────┘ │ │ └───────┘ │
        │ ┌───────┐ │ │ ┌───────┐ │ │ ┌───────┐ │
        │ │  DB   │ │ │ │  DB   │ │ │ │  DB   │ │
        │ │Replica│ │ │ │Replica│ │ │ │Replica│ │
        │ └───────┘ │ │ └───────┘ │ │ └───────┘ │
        └───────────┘ └───────────┘ └───────────┘
```

### Rate Limiting

Protect the write endpoint with rate limiting (e.g., 100 URLs per minute per IP). The read (redirect) endpoint should not be rate-limited for normal traffic, but use DDoS protection at the load balancer level.

---

## 21.14 Complete Architecture

Putting it all together:

```
                            ┌──────────────────────┐
                            │   DNS / Global LB    │
                            └──────────┬───────────┘
                                       │
                            ┌──────────▼───────────┐
                            │   Rate Limiter /     │
                            │   API Gateway        │
                            └──────────┬───────────┘
                                       │
                         ┌─────────────┼──────────────┐
                         │             │              │
                   ┌─────▼─────┐ ┌────▼─────┐ ┌──────▼────┐
                   │ App Server│ │App Server│ │App Server │
                   │     1     │ │    2     │ │     N     │
                   └─────┬─────┘ └────┬─────┘ └─────┬─────┘
                         │            │              │
           ┌─────────────┼────────────┼──────────────┘
           │             │            │
     ┌─────▼─────┐ ┌────▼────┐ ┌────▼──────────────┐
     │ Key Gen   │ │ Redis   │ │ Analytics         │
     │ Service   │ │ Cache   │ │ (Kafka -> Flink   │
     │ (KGS)     │ │ Cluster │ │  -> ClickHouse)   │
     └─────┬─────┘ └────┬────┘ └───────────────────┘
           │             │
     ┌─────▼─────────────▼──────────────────┐
     │        Database Cluster               │
     │  (DynamoDB / Cassandra, sharded)      │
     │  ┌────────┐ ┌────────┐ ┌────────┐    │
     │  │Shard 1 │ │Shard 2 │ │Shard N │    │
     │  └────────┘ └────────┘ └────────┘    │
     └──────────────────────────────────────┘
```

---

## 21.15 Trade-offs

| Decision | Option A | Option B | Our Choice |
|----------|----------|----------|------------|
| Code generation | Hash + truncate | Pre-generated KGS | **KGS** (zero collisions) |
| Redirect code | 301 (permanent) | 302 (temporary) | **302** (better analytics) |
| Database | SQL (PostgreSQL) | NoSQL (DynamoDB) | **NoSQL** (simple KV, massive scale) |
| Cache eviction | LRU | LFU | **LRU** (simpler, works well for URLs) |
| Analytics | Synchronous | Asynchronous pipeline | **Async** (no impact on redirect latency) |
| Expiration cleanup | Lazy (on read) | Active (background job) | **DB TTL** (simplest, most reliable) |
| Key length | 6 chars (56B keys) | 7 chars (3.5T keys) | **7 chars** (room for growth) |

---

## 21.16 Common Mistakes

1. **Ignoring collisions with hash-based approaches.** Candidates often say "just hash it" without addressing what happens when two URLs hash to the same short code. Always discuss collision handling.

2. **Forgetting the read-to-write ratio.** This is a 100:1 read-heavy system. If you do not mention caching, you have missed the most important optimization.

3. **Using 301 without discussing analytics impact.** A 301 redirect means the browser caches the mapping forever. You lose all future click data for that user. This is a critical trade-off.

4. **Putting analytics on the hot path.** Writing analytics data synchronously during a redirect adds latency. Always use an async pipeline.

5. **Not discussing how to handle the same URL submitted twice.** Should it get the same short code or a different one? Both are valid, but you need to decide and explain your reasoning.

6. **Choosing SQL without justification.** The access pattern is pure key-value. There is no compelling reason to use a relational database unless you need complex queries on metadata.

---

## 21.17 Best Practices

1. **Use base62 encoding** (a-z, A-Z, 0-9) instead of base64. Base64 includes `+` and `/` which are not URL-safe without encoding.

2. **Validate URLs on write.** Check that the long URL is well-formed, uses HTTP or HTTPS, and is not pointing to your own domain (to prevent redirect loops).

3. **Add a health check endpoint.** `/health` should return 200 OK with database and cache connectivity status. This allows your load balancer to route traffic away from unhealthy instances.

4. **Use connection pooling** for database and cache connections. Creating a new connection per request is prohibitively expensive at 116,000 requests per second.

5. **Monitor cache hit ratio.** If it drops below 80%, investigate. You may need to increase cache size or adjust TTL.

6. **Log and alert on key exhaustion.** Monitor the KGS pool. If unused keys drop below a threshold, generate more.

---

## 21.18 Quick Summary

A URL shortener maps short codes to long URLs and redirects users. The key design decisions are:

- **Code generation:** A pre-generated Key Generation Service eliminates collisions and coordination overhead.
- **Storage:** A NoSQL key-value store (DynamoDB/Cassandra) handles the simple access pattern at scale.
- **Caching:** Redis caches the top 20% of URLs, handling most of the 116K redirects/second.
- **Redirect:** Use 302 for analytics tracking; 301 if you prioritize reduced server load.
- **Analytics:** An async pipeline (Kafka, Flink, ClickHouse) tracks clicks without affecting redirect latency.
- **Scaling:** Stateless app servers, database sharding by short code, multi-region deployment.

---

## 21.19 Key Points

- URL shortening is a **read-heavy** system with a 100:1 read-to-write ratio.
- A 7-character base62 code gives 3.52 trillion unique keys, far more than needed.
- **Pre-generated keys** (KGS) are the cleanest solution for uniqueness and performance.
- **Caching** is the single biggest performance lever. A 5 GB Redis cache handles most traffic.
- Use **302 redirects** if you need analytics; **301** if you need lower server load.
- **Shard by short code** for even distribution across database nodes.
- **Decouple analytics** from the redirect path using a message queue.

---

## 21.20 Practice Questions

1. How would you handle the case where two users submit the same long URL? Should they get the same short code or different ones? What are the trade-offs?

2. If the Key Generation Service goes down, what happens? How would you make it highly available?

3. How would you implement a "preview" feature where users can see where a short URL leads before being redirected?

4. What happens if a popular short URL suddenly gets millions of clicks per second (e.g., posted by a celebrity)? How does your cache handle it?

5. How would you implement rate limiting that is fair across multiple regions?

---

## 21.21 Exercises

1. **Calculate the key space:** If we use a 6-character base62 code, how many unique codes can we generate? Is that enough for 10 years at 200 million URLs per day?

2. **Design the KGS:** Write pseudocode for the Key Generation Service, including batch allocation and crash recovery.

3. **Compare databases:** Create a comparison table of DynamoDB, Cassandra, and Redis for this use case, evaluating cost, latency, throughput, and operational complexity.

4. **Estimate cache hit ratio:** Given that URL access follows a Zipf distribution with parameter s=1.0, what percentage of requests would be served from a cache holding the top 1% of URLs?

5. **Design a monitoring dashboard:** List the top 10 metrics you would display on an operations dashboard for this system.

---

## 21.22 What Is Next?

In the next chapter, we will design **Pastebin**, a system that shares several patterns with our URL shortener (unique key generation, key-value storage, expiration) but introduces new challenges: storing larger text content, syntax highlighting, and access control. You will see how the building blocks from this chapter can be reused and extended for a different product.
