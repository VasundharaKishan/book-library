# Chapter 22: Designing Pastebin

You need to share a code snippet with a colleague. You paste it into a website, click "create," and get a URL you can send to anyone. They open it and see your code, syntax-highlighted and neatly formatted. That website is Pastebin.

Pastebin is a deceptively simple product. On the surface, it stores text and gives you a link. Under the hood, it handles variable-length content that can range from a single line to megabytes of text, access control, expiration, syntax highlighting, and the same scale challenges as any modern web service. In this chapter, we will design it from the ground up.

If you completed the URL shortener chapter, you will recognize many patterns here: unique key generation, key-value lookups, and expiration. But Pastebin introduces new dimensions that make it a different beast. Let us dive in.

---

## 22.1 Understanding the Problem

Pastebin allows users to:

1. **Create a paste** by submitting text content. The system returns a unique URL.
2. **Read a paste** by visiting the URL. The text is displayed, optionally with syntax highlighting.
3. **Control access:** Pastes can be public, private (only the creator can see them), or unlisted (anyone with the link can see them, but the paste does not appear in search results).
4. **Set expiration:** Pastes can expire after a set period or live forever.

### How Is This Different from a URL Shortener?

| Aspect | URL Shortener | Pastebin |
|--------|---------------|----------|
| Stored data | A long URL (small, fixed size) | Text content (variable, potentially large) |
| Storage strategy | Key-value in database | Metadata in database, content in blob/object store |
| Content rendering | None (just redirect) | Syntax highlighting, line numbers, raw view |
| Access control | Typically public | Public, private, unlisted |
| Content size | ~200 bytes | Up to 10 MB |

---

## 22.2 Requirements

### Functional Requirements

| # | Requirement | Description |
|---|-------------|-------------|
| F1 | **Create paste** | Submit text content and receive a unique URL. |
| F2 | **Read paste** | Retrieve and display paste content by its URL. |
| F3 | **Syntax highlighting** | Optionally specify a language for code highlighting. |
| F4 | **Access control** | Support public, private, and unlisted pastes. |
| F5 | **Expiration** | Pastes can expire after a configurable duration or never. |
| F6 | **Raw view** | Provide a raw text endpoint (no HTML, no highlighting). |
| F7 | **Delete paste** | Creator can delete their paste. |

### Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NF1 | **High availability** | 99.9% uptime. |
| NF2 | **Low latency** | Read a paste in under 100 ms (p99). |
| NF3 | **Scalability** | Handle 10 million new pastes per day, 100 million reads per day. |
| NF4 | **Durability** | Paste content must never be lost before expiration. |
| NF5 | **Size limits** | Maximum paste size: 10 MB. |

### Out of Scope

- User registration and authentication (we will note where it plugs in).
- Search across pastes (complex and orthogonal to core design).
- Collaborative editing (that is Google Docs territory).

---

## 22.3 Back-of-the-Envelope Estimation

### Traffic

| Metric | Value |
|--------|-------|
| New pastes per day | 10 million |
| New pastes per second | 10M / 86,400 ≈ **116 pastes/s** |
| Read-to-write ratio | ~10:1 |
| Reads per second | 116 x 10 = **1,160 reads/s** |

This is a moderate scale system, much smaller than the URL shortener. But the content size makes storage the primary concern.

### Storage

| Item | Size |
|------|------|
| Average paste content | 10 KB |
| Maximum paste content | 10 MB |
| Metadata per paste | ~500 bytes |

Daily content storage:

```
10M pastes/day x 10 KB average = 100 GB/day
```

Over five years (assuming 50% of pastes expire within a year):

```
Year 1: 100 GB/day x 365 = 36.5 TB
Years 2-5: 36.5 TB x 0.5 (retained) x 4 = 73 TB
Total: ~110 TB of content
```

Plus metadata:

```
10M pastes/day x 365 x 5 = 18.25 billion records
18.25 billion x 500 bytes ≈ 9.1 TB of metadata
```

Content storage dominates. We need an object store (like S3) for content and a database for metadata.

### Bandwidth

| Direction | Calculation | Result |
|-----------|-------------|--------|
| Write (incoming) | 116 pastes/s x 10 KB | ~1.16 MB/s |
| Read (outgoing) | 1,160 reads/s x 10 KB | ~11.6 MB/s |

Very manageable bandwidth.

### Key Space

Using a 8-character base62 code:

```
62^8 = 218 trillion unique keys
```

With 18.25 billion pastes over 5 years, we use 0.008% of the key space. No key exhaustion concerns.

---

## 22.4 High-Level Design

```
                         ┌──────────────────┐
                         │   Load Balancer   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
              ┌─────▼─────┐ ┌────▼─────┐ ┌────▼─────┐
              │  App       │ │  App     │ │  App     │
              │  Server 1  │ │ Server 2 │ │ Server N │
              └─────┬──────┘ └────┬─────┘ └────┬─────┘
                    │             │             │
         ┌──────────┼─────────────┼─────────────┘
         │          │             │
   ┌─────▼───┐ ┌───▼────┐ ┌─────▼──────────────┐
   │  Key    │ │ Cache  │ │  Object Store       │
   │  Gen    │ │(Redis) │ │  (S3 / Blob)        │
   │ Service │ └───┬────┘ │ ┌──────┐ ┌──────┐   │
   └─────────┘     │      │ │Paste │ │Paste │   │
                   │      │ │  1   │ │  2   │   │
              ┌────▼──────┴─┴──────┴─┴──────┴───┐
              │         Metadata DB              │
              │    (PostgreSQL / DynamoDB)        │
              └──────────────────────────────────┘
                         │
              ┌──────────▼───────────────┐
              │   CDN (CloudFront /      │
              │   Cloudflare)            │
              └──────────────────────────┘
```

### Two-Tier Storage Architecture

The key insight is separating **metadata** from **content**:

- **Metadata database** stores: paste ID, title, language, access level, timestamps, and a pointer to the content.
- **Object store** (S3, GCS, Azure Blob) stores the actual paste content. Object stores are optimized for large, variable-size blobs at low cost.

Why not store content in the database? A 10 MB paste in a database row is expensive and slow to retrieve. Object stores are 10-50x cheaper per GB than database storage and purpose-built for this workload.

### Request Flows

**Flow 1: Create a Paste**

1. Client sends `POST /api/v1/pastes` with the text content, language, access level, and expiration.
2. App server gets a unique key from the Key Generation Service.
3. App server uploads the content to the object store: `s3://pastes/{key}`.
4. App server writes metadata to the database.
5. App server returns the paste URL to the client.

**Flow 2: Read a Paste**

1. User visits `https://paste.example.com/{key}`.
2. CDN checks if it has a cached version (for public pastes).
3. **CDN hit:** Return cached content.
4. **CDN miss:** Request reaches the app server.
5. App server checks Redis cache for metadata.
6. App server fetches content from the object store (or cache if recently accessed).
7. App server applies syntax highlighting (if a language is specified).
8. App server returns the rendered page.

---

## 22.5 Deep Dive: Unique Key Generation

We can reuse the Key Generation Service (KGS) approach from the URL shortener chapter. A dedicated service pre-generates unique 8-character base62 keys and distributes them in batches to app servers.

Why 8 characters instead of 7? Pastebin URLs are less commonly typed manually (unlike short URLs), so an extra character is a worthwhile trade for a larger key space.

The alternative approaches (hash-based, counter-based) also apply here with the same trade-offs discussed in Chapter 21.

---

## 22.6 Deep Dive: Content Storage

### Why Object Storage?

| Factor | Database (PostgreSQL) | Object Store (S3) |
|--------|----------------------|-------------------|
| Cost per GB/month | $0.10 - $0.50 | $0.023 |
| Maximum object size | ~1 GB (practical limit) | 5 TB |
| Read latency | 5-20 ms | 50-100 ms (first byte) |
| Throughput | Limited by connections | Virtually unlimited |
| Durability | 99.99% (with replication) | 99.999999999% (11 nines) |

Object storage wins on cost and durability. The higher latency is mitigated by our cache layer and CDN.

### Content Organization

Store pastes in S3 with a flat key structure:

```
s3://pastebin-content/{paste_key}
```

For example: `s3://pastebin-content/aB3kQ7z9`

Do not use folder hierarchies (like `/2024/06/15/aB3kQ7z9`). S3 is not a filesystem; flat keys perform better and simplify lookups.

### Compression

Text compresses extremely well. A 10 KB code snippet might compress to 2-3 KB with gzip or zstd. Compressing before storage:

- Reduces storage costs by 60-80%.
- Reduces bandwidth for reads.
- Adds minimal CPU overhead (compression is fast for text).

Store content compressed, with a `Content-Encoding` header noting the compression algorithm.

---

## 22.7 Deep Dive: Syntax Highlighting

Syntax highlighting can be done server-side or client-side.

### Server-Side Highlighting

Use a library like Pygments (Python), highlight.js (Node.js), or Rouge (Ruby) to convert raw text into highlighted HTML.

```
Input:  def hello():\n    print("Hello")
Output: <span class="kw">def</span> <span class="fn">hello</span>()...
```

**Pros:** Works without JavaScript. SEO-friendly. Consistent rendering.
**Cons:** CPU cost on the server. Need to regenerate if themes change.

### Client-Side Highlighting

Send raw text to the browser and use a JavaScript library (Prism.js, highlight.js) to highlight on the client.

**Pros:** Zero server CPU cost. Easy to change themes. Lazy highlighting for large files.
**Cons:** Requires JavaScript. Slower initial render for large files.

### Recommendation

Use **client-side highlighting** for the web interface (offloads CPU to the client) and **server-side highlighting** for the API (when clients request pre-rendered HTML). Cache the highlighted output for popular pastes.

### Supported Languages

Support at least the top 30 programming languages. Store the language as metadata so the highlighter knows which grammar to apply. If no language is specified, offer auto-detection (most highlighting libraries support this, though it is imperfect).

---

## 22.8 Deep Dive: Access Control

### Three Access Levels

| Level | Behavior |
|-------|----------|
| **Public** | Anyone can view. Appears in recent pastes and search. |
| **Unlisted** | Anyone with the link can view. Does not appear in listings or search. |
| **Private** | Only the creator can view. Requires authentication. |

### Implementation

```
if paste.access_level == "public":
    allow_access()
elif paste.access_level == "unlisted":
    allow_access()  # Security through obscurity (the URL is the secret)
elif paste.access_level == "private":
    if request.user_id == paste.creator_id:
        allow_access()
    else:
        return 403 Forbidden
```

### Security Considerations

- **Unlisted pastes** rely on the URL being secret. With 8-character base62 keys (218 trillion combinations), guessing a URL is practically impossible. But anyone with the link can share it further.
- **Private pastes** require proper authentication. Use session tokens or API keys.
- **Never cache private pastes** in the CDN or shared cache. Only cache public and unlisted pastes.

---

## 22.9 Deep Dive: Size Limits and Rate Limiting

### Size Limits

| Limit | Value | Reason |
|-------|-------|--------|
| Maximum paste size | 10 MB | Prevents abuse, keeps storage manageable |
| Minimum paste size | 1 byte | No reason to allow empty pastes |
| Maximum title length | 256 characters | Keep metadata compact |

Enforce size limits at multiple layers:
1. **Client-side:** Show a warning if content exceeds the limit (immediate feedback).
2. **Load balancer / API gateway:** Reject requests with `Content-Length` exceeding 10 MB (prevents large payloads from consuming server resources).
3. **App server:** Validate actual content size after parsing.

### Rate Limiting

| Operation | Limit | Window |
|-----------|-------|--------|
| Create paste (unauthenticated) | 10 per minute | Per IP |
| Create paste (authenticated) | 60 per minute | Per user |
| Read paste | 300 per minute | Per IP |

Use a token bucket or sliding window rate limiter at the API gateway level.

### Why Rate Limit?

Without rate limiting, an attacker could:
- Exhaust storage by creating millions of large pastes.
- Consume all pre-generated keys.
- DDoS the write path.

---

## 22.10 Deep Dive: CDN for Popular Pastes

A CDN (Content Delivery Network) caches popular pastes at edge locations worldwide, reducing latency and offloading traffic from our servers.

### What to Cache

| Content Type | Cache in CDN? | TTL |
|-------------|---------------|-----|
| Public pastes | Yes | 1 hour |
| Unlisted pastes | Yes (with full URL as cache key) | 1 hour |
| Private pastes | No | N/A |
| Raw paste content | Yes (for public/unlisted) | 1 hour |
| Static assets (CSS, JS) | Yes | 1 week |

### Cache Invalidation

When a paste is deleted or updated, we need to invalidate the CDN cache:
- Use the CDN's invalidation API (e.g., CloudFront invalidation, Cloudflare purge).
- Alternatively, include a version hash in the URL (`/paste/{key}?v=abc123`) and update it on modification.

### CDN Architecture

```
┌────────┐     ┌─────────────────────────┐     ┌────────────┐
│ User   │────>│  CDN Edge (PoP)         │────>│ Origin     │
│(Brazil)│     │  Sao Paulo              │     │ Server     │
└────────┘     │  ┌───────────────────┐  │     │ (US-East)  │
               │  │ Cached: paste X   │  │     │            │
               │  │ Cached: paste Y   │  │     │            │
               │  └───────────────────┘  │     │            │
               └─────────────────────────┘     └────────────┘
```

For a viral paste (e.g., shared on a popular forum), the CDN handles 99% of traffic. Our origin servers barely feel it.

---

## 22.11 Database Schema

### Metadata Table

```sql
CREATE TABLE pastes (
    paste_id        VARCHAR(8)   PRIMARY KEY,
    title           VARCHAR(256),
    language        VARCHAR(50),
    access_level    ENUM('public', 'unlisted', 'private') DEFAULT 'unlisted',
    content_url     VARCHAR(512) NOT NULL,  -- S3 URL
    content_size    INTEGER      NOT NULL,  -- bytes
    creator_id      VARCHAR(36),            -- nullable for anonymous
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP,              -- nullable = never expires
    view_count      INTEGER      DEFAULT 0,
    is_compressed   BOOLEAN      DEFAULT true
);

-- Index for expiration cleanup
CREATE INDEX idx_expires_at ON pastes(expires_at)
    WHERE expires_at IS NOT NULL;

-- Index for user's pastes
CREATE INDEX idx_creator ON pastes(creator_id, created_at DESC)
    WHERE creator_id IS NOT NULL;

-- Index for public paste listing
CREATE INDEX idx_public_recent ON pastes(created_at DESC)
    WHERE access_level = 'public';
```

### Why PostgreSQL for Metadata?

Unlike the URL shortener (which is pure key-value), Pastebin metadata benefits from:
- **Indexes** on `expires_at`, `creator_id`, and `access_level`.
- **SQL queries** for listing a user's pastes, finding recent public pastes, and cleanup jobs.
- **ACID transactions** for create/delete operations.

At 10 million rows per day, PostgreSQL with proper sharding handles the load well. If scale exceeds a single cluster, switch to a horizontally scalable option like CockroachDB or use DynamoDB with secondary indexes.

---

## 22.12 API Design

### Create a Paste

```
POST /api/v1/pastes
Content-Type: application/json

Request:
{
    "content": "def hello():\n    print('Hello, World!')",
    "title": "My Python Snippet",
    "language": "python",
    "access_level": "unlisted",
    "expires_in": "24h"  // "10m", "1h", "24h", "7d", "30d", "never"
}

Response: 201 Created
{
    "paste_id": "aB3kQ7z9",
    "url": "https://paste.example.com/aB3kQ7z9",
    "raw_url": "https://paste.example.com/raw/aB3kQ7z9",
    "title": "My Python Snippet",
    "language": "python",
    "access_level": "unlisted",
    "created_at": "2024-06-15T10:30:00Z",
    "expires_at": "2024-06-16T10:30:00Z"
}
```

### Read a Paste (HTML)

```
GET /pastes/{paste_id}

Response: 200 OK
Content-Type: text/html

(Rendered HTML page with syntax-highlighted content)
```

### Read a Paste (Raw)

```
GET /raw/{paste_id}

Response: 200 OK
Content-Type: text/plain

def hello():
    print('Hello, World!')
```

### Read Paste Metadata (API)

```
GET /api/v1/pastes/{paste_id}

Response: 200 OK
{
    "paste_id": "aB3kQ7z9",
    "title": "My Python Snippet",
    "language": "python",
    "access_level": "unlisted",
    "content_size": 42,
    "view_count": 156,
    "created_at": "2024-06-15T10:30:00Z",
    "expires_at": "2024-06-16T10:30:00Z"
}
```

### Delete a Paste

```
DELETE /api/v1/pastes/{paste_id}
Authorization: Bearer <token>

Response: 204 No Content
```

### List User's Pastes

```
GET /api/v1/users/me/pastes?page=1&limit=20

Response: 200 OK
{
    "pastes": [
        {
            "paste_id": "aB3kQ7z9",
            "title": "My Python Snippet",
            "language": "python",
            "created_at": "2024-06-15T10:30:00Z",
            "view_count": 156
        }
    ],
    "total": 42,
    "page": 1,
    "limit": 20
}
```

---

## 22.13 Scaling Considerations

### Object Store Scaling

S3 and similar object stores scale virtually infinitely. No sharding decisions needed. This is one of the biggest advantages of the two-tier architecture: the hardest scaling problem (content storage) is solved by a managed service.

### Metadata Database Scaling

At 10 million inserts per day (~116/s), a single PostgreSQL instance handles writes easily. For reads (1,160/s), add read replicas.

If we grow beyond a single cluster's capacity:
- **Shard by paste_id** for even distribution.
- Use a consistent hashing ring to map paste IDs to shards.
- The "list user's pastes" query becomes a fan-out across shards (or maintain a separate index by user_id).

### App Server Scaling

App servers are stateless (like the URL shortener). Scale horizontally behind a load balancer based on CPU and request rate.

### Cache Scaling

Use a Redis cluster with 3-5 nodes. Cache paste metadata and recently accessed content. A 10 GB cache holds ~1 million recent pastes' metadata and ~100,000 content blobs.

### Expiration at Scale

Running `DELETE FROM pastes WHERE expires_at < NOW()` on 18 billion rows is expensive. Better approaches:

1. **Partition by time.** Create monthly partitions. Drop entire partitions when all pastes in them have expired.
2. **Lazy deletion.** Do not delete expired pastes proactively. Check expiration on read. Run a background sweeper during off-peak hours.
3. **Use object store lifecycle rules.** S3 lifecycle policies can automatically delete objects after a set period. Set the object's expiration to match the paste's expiration.

```
┌──────────────────────────────────────────┐
│  Expiration Strategy                      │
│                                          │
│  1. Read request arrives for paste X     │
│  2. Check metadata: is expires_at past?  │
│  3. If yes: return 410 Gone             │
│  4. Background job (hourly):            │
│     - Scan expired pastes               │
│     - Delete from S3                    │
│     - Delete metadata row               │
│  5. S3 lifecycle rule (backup):         │
│     - Auto-delete objects older than    │
│       max_expiration + 1 day            │
└──────────────────────────────────────────┘
```

---

## 22.14 Complete Architecture

```
                         ┌────────────────────┐
                         │   CDN (CloudFront)  │
                         └────────┬───────────┘
                                  │
                         ┌────────▼───────────┐
                         │   Load Balancer /   │
                         │   API Gateway       │
                         │  (Rate Limiting)    │
                         └────────┬───────────┘
                                  │
                    ┌─────────────┼──────────────┐
                    │             │              │
              ┌─────▼─────┐ ┌────▼─────┐ ┌─────▼─────┐
              │ App Server│ │App Server│ │ App Server│
              │     1     │ │    2     │ │     N     │
              └──┬──┬──┬──┘ └────┬─────┘ └─────┬─────┘
                 │  │  │         │              │
    ┌────────────┘  │  └─────────┼──────────────┘
    │               │            │
┌───▼─────┐  ┌─────▼────┐  ┌────▼─────────────────┐
│  Key    │  │  Cache   │  │   S3 / Object Store   │
│  Gen    │  │  (Redis) │  │                       │
│ Service │  │  Cluster │  │  ┌─────┐ ┌─────┐     │
└─────────┘  └─────┬────┘  │  │Paste│ │Paste│ ... │
                   │       │  │  1  │ │  2  │     │
             ┌─────▼───────┤  └─────┘ └─────┘     │
             │  Metadata   │                       │
             │  Database   └───────────────────────┘
             │ (PostgreSQL)│
             │ ┌────┐┌────┐│
             │ │ RW ││ RO ││
             │ └────┘└────┘│
             └─────────────┘
                   │
             ┌─────▼──────────────┐
             │ Expiration Worker   │
             │ (Cron Job)         │
             └────────────────────┘
```

---

## 22.15 Trade-offs

| Decision | Option A | Option B | Our Choice |
|----------|----------|----------|------------|
| Content storage | Database (BLOB column) | Object store (S3) | **S3** (cheaper, more durable, infinite scale) |
| Metadata store | NoSQL (DynamoDB) | SQL (PostgreSQL) | **PostgreSQL** (need indexes, queries, transactions) |
| Syntax highlighting | Server-side | Client-side | **Client-side** for web, **server-side** for API |
| Compression | None | gzip/zstd | **Compress** (60-80% storage savings for text) |
| Expiration | Eager deletion | Lazy + background | **Lazy + background** (no read-path overhead) |
| CDN caching | All pastes | Public + unlisted only | **Public + unlisted** (never cache private) |

---

## 22.16 Common Mistakes

1. **Storing content in the database.** This is the most common mistake. Variable-size text blobs (up to 10 MB) do not belong in a relational database. Use an object store for content and a database for metadata.

2. **Forgetting access control for private pastes.** Saying "the URL is the security" works for unlisted pastes but not for private ones. Private pastes need authentication.

3. **No size limits.** Without a maximum paste size, attackers can upload gigabytes of data. Always enforce limits at the API gateway and app server level.

4. **Ignoring compression.** Text compresses remarkably well. Not compressing content wastes 60-80% of storage costs.

5. **Caching private pastes in CDN.** A CDN is shared infrastructure. Private pastes in a CDN can be served to unauthorized users if cache keys are predictable.

6. **No rate limiting.** A simple script could create millions of pastes, exhausting storage and keys.

---

## 22.17 Best Practices

1. **Use pre-signed URLs** for S3 reads. Instead of proxying content through your app servers, generate a time-limited S3 URL and redirect the client. This offloads bandwidth from your servers to S3.

2. **Store content with its hash** for deduplication. If two users paste identical content, store it once and reference it twice. Use SHA-256 of the content as a secondary key.

3. **Set reasonable defaults.** Default expiration to 30 days (not "never"). This prevents abandoned pastes from accumulating forever.

4. **Add abuse detection.** Scan paste content for known malware patterns, phishing URLs, or illegal content. Use automated scanning on the write path.

5. **Implement "burn after reading."** Some pastes should self-destruct after being viewed once. Store a `burn_after_read` flag and delete the paste after the first successful read.

6. **Version your API.** Use `/api/v1/` prefixes so you can evolve the API without breaking existing clients.

---

## 22.18 Quick Summary

Pastebin stores text content and serves it via unique URLs. The key design decisions are:

- **Two-tier storage:** Metadata in PostgreSQL, content in S3. This separates structured queries from blob storage.
- **Key generation:** A pre-generated Key Generation Service provides unique 8-character codes.
- **CDN caching:** Public and unlisted pastes are cached at the edge for low-latency reads.
- **Access control:** Public, unlisted, and private levels. Private requires authentication; unlisted relies on URL secrecy.
- **Syntax highlighting:** Client-side for web UI, server-side for API.
- **Expiration:** Lazy check on read plus a background cleanup job.

---

## 22.19 Key Points

- Pastebin shares patterns with URL shorteners (key generation, expiration) but differs in **content storage** (variable-size blobs vs. small URLs).
- **Object storage (S3)** is the right choice for paste content: 10-50x cheaper than database storage, 11 nines of durability, and infinite scale.
- **Compress text content** before storing. Text compresses 60-80%, saving significant storage costs.
- **Never cache private pastes** in a CDN or shared cache.
- **Rate limiting and size limits** are essential to prevent abuse.
- **Pre-signed S3 URLs** offload read traffic from app servers to the object store.
- Syntax highlighting is best done **client-side** for web and **server-side** for API consumers.

---

## 22.20 Practice Questions

1. If two users paste identical content, should we store it once or twice? What are the privacy implications of deduplication?

2. How would you implement a "burn after reading" feature where the paste is deleted after the first view? What happens if two users click the link at the exact same time?

3. How would you add a search feature for public pastes? What kind of index would you use?

4. If a paste goes viral and gets 1 million views per second, walk through exactly what happens at each layer of the architecture.

5. How would you handle a paste that contains malware or phishing content? At what point in the pipeline would you detect it?

---

## 22.21 Exercises

1. **Estimate S3 costs.** Using current S3 pricing, calculate the monthly cost of storing 100 TB of paste content with standard storage, including PUT and GET request costs at our traffic levels.

2. **Design the deduplication system.** Write pseudocode for a system that detects duplicate content and stores it only once, while maintaining separate metadata entries for each paste.

3. **Compare object stores.** Create a table comparing S3, Google Cloud Storage, and Azure Blob Storage on cost, latency, durability, and maximum object size.

4. **Design the expiration worker.** Write pseudocode for a background job that efficiently finds and deletes expired pastes across both the metadata database and S3.

5. **Calculate CDN savings.** If 10% of pastes account for 90% of reads, and a CDN has a 95% hit ratio for those popular pastes, how many requests per second does the origin server handle?

---

## 22.22 What Is Next?

In the next chapter, we will tackle a dramatically more complex system: **Twitter/X**. While Pastebin is a straightforward "store and retrieve" system, Twitter introduces fan-out (how do you deliver a tweet to millions of followers?), real-time timelines, trending topics, and the fascinating trade-off between fan-out on write and fan-out on read. Get ready for one of the most popular system design interview questions.
