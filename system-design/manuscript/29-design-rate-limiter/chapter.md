# Chapter 29: Design a Distributed Rate Limiter

## What You Will Learn

By the end of this chapter, you will understand how to design a distributed rate limiter that protects your services from being overwhelmed. You will learn two core algorithms in depth -- token bucket and sliding window counter -- and implement them with Redis. You will see how to handle race conditions with Lua scripts, build a configurable rule engine, design multi-tier rate limiting (per user, per API, and global), and create a complete architecture that works across multiple servers.

## Why This Chapter Matters

Rate limiting is the immune system of your infrastructure. Without it, a single misbehaving client can take down your entire service. Every major API (GitHub, Stripe, Twitter, AWS) enforces rate limits. In system design interviews, rate limiting comes up both as a standalone question and as a component of larger designs. Understanding the algorithms, trade-offs, and distributed implementation details will make you stronger in any interview.

---

## 1. Requirements Gathering

### Functional Requirements

- Limit requests by user ID, IP address, or API key
- Support configurable rules (e.g., 100 requests per minute per user)
- Return appropriate HTTP responses when limits are exceeded
- Support multiple rate limiting tiers (user-level, API-level, global)
- Allow different limits for different API endpoints
- Provide rate limit headers in responses (remaining quota, reset time)

### Non-Functional Requirements

- **Low latency:** Rate limit check must complete in under 1 millisecond
- **High availability:** If the rate limiter is down, requests should still be processed (fail-open vs fail-closed)
- **Distributed:** Must work consistently across multiple application servers
- **Accuracy:** Minor over-counting is acceptable; significant under-counting is not
- **Scale:** Handle 1 million+ requests per second across all services

### Back-of-Envelope Estimation

```
Total requests per second: 1,000,000
Rate limit check per request: 1 (minimum)
Redis operations per check: 2-3

Redis throughput needed: 2-3 million ops/sec
Redis single instance: ~100,000 ops/sec
Redis instances needed: 20-30 (with Redis Cluster)

Memory per rate limit counter: ~100 bytes
Active users at any time: 10 million
Memory for all counters: 10M x 100B = 1 GB
```

---

## 2. Rate Limiting Algorithms

Before building the distributed system, let us understand the algorithms.

### 2.1 Token Bucket (Deep Dive)

The token bucket is the most widely used rate limiting algorithm. It is simple, memory-efficient, and allows controlled bursts.

**How It Works:**

Imagine a bucket that holds tokens. The bucket has a maximum capacity. Tokens are added to the bucket at a fixed rate. When a request arrives, it takes one token from the bucket. If the bucket is empty, the request is rejected.

```
Token Bucket Parameters:
  - capacity:    Maximum tokens the bucket can hold (burst size)
  - refill_rate: Tokens added per second

Example: capacity = 10, refill_rate = 2 tokens/sec

Time 0s:  Bucket = [T T T T T T T T T T]  (10 tokens, full)
          5 requests arrive, 5 tokens consumed
          Bucket = [T T T T T _ _ _ _ _]  (5 tokens left)

Time 1s:  2 tokens added (refill_rate = 2)
          Bucket = [T T T T T T T _ _ _]  (7 tokens)
          3 requests arrive
          Bucket = [T T T T _ _ _ _ _ _]  (4 tokens)

Time 2s:  2 tokens added
          Bucket = [T T T T T T _ _ _ _]  (6 tokens)
          8 requests arrive, only 6 succeed
          Bucket = [_ _ _ _ _ _ _ _ _ _]  (0 tokens)
          2 requests REJECTED

Time 3s:  2 tokens added
          Bucket = [T T _ _ _ _ _ _ _ _]  (2 tokens)
```

**Token Bucket Implementation (Pseudocode):**

```
class TokenBucket:
    capacity = 10          # max tokens
    refill_rate = 2        # tokens per second
    tokens = 10            # current tokens
    last_refill_time = NOW()

    function allow_request():
        # Step 1: Refill tokens based on elapsed time
        now = NOW()
        elapsed = now - last_refill_time
        tokens_to_add = elapsed * refill_rate
        tokens = MIN(capacity, tokens + tokens_to_add)
        last_refill_time = now

        # Step 2: Check if we have a token
        if tokens >= 1:
            tokens = tokens - 1
            return ALLOW
        else:
            return REJECT
```

**Why Token Bucket?**

| Property        | Token Bucket Behavior                              |
|-----------------|---------------------------------------------------|
| Steady rate     | Sustained rate equals refill_rate                  |
| Bursts          | Allows bursts up to capacity                       |
| Memory          | O(1) per bucket (just 3 values)                    |
| Precision       | Smooth, not tied to fixed time windows              |

**Redis Implementation of Token Bucket:**

```
-- Lua script for atomic token bucket check
-- KEYS[1] = rate limit key (e.g., "ratelimit:user:123")
-- ARGV[1] = capacity
-- ARGV[2] = refill_rate (tokens per second)
-- ARGV[3] = current timestamp (in microseconds)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Get current state
local state = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(state[1])
local last_refill = tonumber(state[2])

-- Initialize if first request
if tokens == nil then
    tokens = capacity
    last_refill = now
end

-- Refill tokens
local elapsed = (now - last_refill) / 1000000  -- convert to seconds
local new_tokens = elapsed * refill_rate
tokens = math.min(capacity, tokens + new_tokens)

-- Try to consume a token
local allowed = 0
if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end

-- Save state
redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) + 1)

-- Return: allowed (0 or 1), remaining tokens, time until next token
local retry_after = 0
if allowed == 0 then
    retry_after = math.ceil((1 - tokens) / refill_rate)
end

return {allowed, math.floor(tokens), retry_after}
```

### 2.2 Sliding Window Counter (Deep Dive)

The sliding window counter provides more precise rate limiting than fixed windows without the memory cost of tracking every individual request.

**The Problem with Fixed Windows:**

```
Fixed Window: 10 requests per minute

Window 1 (0:00 - 0:59):  Requests at 0:50-0:59 = 10 (all near end)
Window 2 (1:00 - 1:59):  Requests at 1:00-1:09 = 10 (all near start)

In the 20-second span from 0:50 to 1:09, user made 20 requests!
The fixed window allowed DOUBLE the intended limit.

     Window 1                Window 2
|............XXXXXXXXXX|XXXXXXXXXX............|
              10 reqs    10 reqs
              ^------- 20 in 20 sec -------^
```

**Sliding Window Counter Solution:**

The sliding window counter uses a weighted combination of the current and previous window counts.

```
Sliding Window Formula:
  weighted_count = (prev_window_count * overlap_percentage)
                 + current_window_count

Example: Limit = 10 requests per minute

Previous window (0:00 - 0:59): 8 requests
Current window  (1:00 - 1:59): 5 requests
Current time: 1:15 (25% into current window)

Overlap of previous window = 1 - 0.25 = 0.75 (75%)

weighted_count = (8 * 0.75) + 5 = 6 + 5 = 11

11 > 10, so REJECT the request!

     Previous Window          Current Window
|XXXXXXXX..............|XXXXX..................|
  8 requests              5 requests
         ^-- 75% overlap --^-- 25% elapsed
```

**Sliding Window Counter Implementation (Pseudocode):**

```
class SlidingWindowCounter:
    limit = 10             # max requests per window
    window_size = 60       # window size in seconds

    function allow_request(user_id):
        now = NOW()
        current_window = floor(now / window_size)
        previous_window = current_window - 1

        # Get counts for current and previous windows
        current_count = redis.GET(key(user_id, current_window)) or 0
        previous_count = redis.GET(key(user_id, previous_window)) or 0

        # Calculate position within current window
        elapsed_in_window = now % window_size
        overlap = 1 - (elapsed_in_window / window_size)

        # Weighted count
        weighted = (previous_count * overlap) + current_count

        if weighted < limit:
            redis.INCR(key(user_id, current_window))
            redis.EXPIRE(key(user_id, current_window), window_size * 2)
            return ALLOW
        else:
            return REJECT
```

**Redis Implementation of Sliding Window Counter:**

```
-- Lua script for atomic sliding window counter
-- KEYS[1] = current window key
-- KEYS[2] = previous window key
-- ARGV[1] = limit
-- ARGV[2] = window_size (seconds)
-- ARGV[3] = current timestamp

local current_key = KEYS[1]
local previous_key = KEYS[2]
local limit = tonumber(ARGV[1])
local window_size = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Get counts
local current_count = tonumber(redis.call('GET', current_key) or "0")
local previous_count = tonumber(redis.call('GET', previous_key) or "0")

-- Calculate overlap
local elapsed = now % window_size
local overlap = 1 - (elapsed / window_size)

-- Weighted count
local weighted = math.floor(previous_count * overlap) + current_count

if weighted < limit then
    redis.call('INCR', current_key)
    redis.call('EXPIRE', current_key, window_size * 2)
    return {1, limit - weighted - 1}  -- allowed, remaining
else
    local retry_after = window_size - elapsed
    return {0, 0, retry_after}  -- rejected, 0 remaining, retry after
end
```

### 2.3 Algorithm Comparison

```
+--------------------+--------------+------------------+-------------+
| Property           | Token Bucket | Sliding Window   | Fixed Window|
+--------------------+--------------+------------------+-------------+
| Memory per user    | O(1)         | O(1)             | O(1)        |
| Burst handling     | Allows burst | Smooth, no burst | Edge burst  |
| Accuracy           | Good         | Very good        | Poor at edge|
| Implementation     | Simple       | Moderate         | Simplest    |
| Best for           | API rate     | Precise limits   | Simple      |
|                    | limiting     | anti-abuse       | use cases   |
+--------------------+--------------+------------------+-------------+
```

**When to use which:**
- **Token bucket:** When you want to allow controlled bursts (most API rate limiting)
- **Sliding window counter:** When you need precise counts without burst tolerance
- **Fixed window:** Only when simplicity matters more than accuracy

---

## 3. Distributed Rate Limiting with Redis

### 3.1 Why Redis?

Rate limiting requires shared state across all application servers. Redis is the standard choice because:

1. **Sub-millisecond latency:** Rate limit checks must be fast
2. **Atomic operations:** INCR, Lua scripts prevent race conditions
3. **TTL support:** Counters automatically expire
4. **High throughput:** 100K+ operations per second per instance
5. **Replication:** Redis Sentinel or Cluster for high availability

### 3.2 Architecture with Redis

```
+-------------------+     +-------------------+     +-------------------+
| App Server 1      |     | App Server 2      |     | App Server 3      |
| +---------------+ |     | +---------------+ |     | +---------------+ |
| | Rate Limiter  | |     | | Rate Limiter  | |     | | Rate Limiter  | |
| | Middleware    | |     | | Middleware    | |     | | Middleware    | |
| +-------+-------+ |     | +-------+-------+ |     | +-------+-------+ |
+---------+---------+     +---------+---------+     +---------+---------+
          |                         |                         |
          +-------------------------+-------------------------+
                                    |
                                    v
                    +---------------+---------------+
                    |         Redis Cluster          |
                    |  +-------+  +-------+  +---+  |
                    |  |Shard 1|  |Shard 2|  | 3 |  |
                    |  |A-F    |  |G-M    |  |N-Z|  |
                    |  +-------+  +-------+  +---+  |
                    +-------------------------------+
```

All application servers talk to the same Redis cluster. This ensures that no matter which server handles a request, the rate limit count is consistent.

### 3.3 Handling Race Conditions

Without atomicity, two servers can read the same count, both decide the request is allowed, and both increment -- exceeding the limit.

**The Race Condition:**

```
Time    Server A                    Server B
----    --------                    --------
T1      GET counter = 9
T2                                  GET counter = 9
T3      9 < 10, ALLOW
T4                                  9 < 10, ALLOW
T5      INCR counter -> 10
T6                                  INCR counter -> 11  (OVER LIMIT!)
```

**Solution: Lua Scripts**

Redis executes Lua scripts atomically. The entire read-check-increment happens as a single operation.

```
-- Atomic rate limit check with Lua
-- This entire script runs atomically in Redis

local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = tonumber(redis.call('GET', key) or "0")

if current < limit then
    -- Atomically increment and set expiry
    local new_count = redis.call('INCR', key)
    if new_count == 1 then
        redis.call('EXPIRE', key, window)
    end
    return {1, limit - new_count}  -- allowed, remaining
else
    local ttl = redis.call('TTL', key)
    return {0, 0, ttl}  -- rejected, 0 remaining, retry after
end
```

With this Lua script, the race condition is eliminated. Redis processes the script atomically -- no other command can run between the GET and the INCR.

**Alternative: Redis MULTI/EXEC**

For simpler cases, you can use Redis transactions, but Lua scripts are preferred because they can include conditional logic.

### 3.4 Handling Redis Failures

What happens when Redis is unavailable?

```
+-------------------+
| Request arrives   |
+--------+----------+
         |
         v
+--------+----------+
| Rate limit check  |
| (Redis call)      |
+--------+----------+
         |
    +----+----+
    | Redis   |
    | healthy?|
    +----+----+
    YES  |    NO
     |   |     |
     v   |     v
  Normal |  +--+------------------+
  check  |  | Fail-open policy    |
         |  | ALLOW the request   |
         |  | Log the failure     |
         |  | Alert ops team      |
         |  +---------------------+
         |
         v
      Continue
```

**Fail-open vs fail-closed:**
- **Fail-open (recommended):** Allow requests when Redis is down. You temporarily lose rate limiting but your service stays available.
- **Fail-closed:** Reject all requests when Redis is down. Your service becomes unavailable, which is usually worse than temporarily exceeding rate limits.

**Local fallback:**

For extra resilience, keep an in-memory rate limiter as a fallback. It will not be perfectly accurate (each server counts independently), but it provides basic protection.

```
function check_rate_limit(user_id):
    try:
        return redis_rate_limit_check(user_id)
    except RedisConnectionError:
        log.warn("Redis unavailable, using local fallback")
        return local_rate_limit_check(user_id)  # in-memory counter
```

---

## 4. Rule Engine

Different API endpoints need different limits. Free users get fewer requests than paid users. The rule engine makes this configurable.

### 4.1 Rule Configuration

```yaml
# rate_limit_rules.yaml

rules:
  # Global rules (apply to all requests)
  - name: "global-rate-limit"
    scope: "global"
    limit: 10000
    window: 1          # per second
    priority: 1        # evaluated first

  # Per-API endpoint rules
  - name: "search-api"
    scope: "endpoint"
    match:
      path: "/api/v1/search"
      method: "GET"
    limit: 30
    window: 60         # 30 per minute
    priority: 2

  - name: "write-api"
    scope: "endpoint"
    match:
      path: "/api/v1/posts"
      method: "POST"
    limit: 10
    window: 60         # 10 per minute
    priority: 2

  # Per-user tier rules
  - name: "free-user"
    scope: "user"
    match:
      tier: "free"
    limit: 100
    window: 3600       # 100 per hour
    priority: 3

  - name: "pro-user"
    scope: "user"
    match:
      tier: "pro"
    limit: 1000
    window: 3600       # 1000 per hour
    priority: 3

  # Per-IP rules (for unauthenticated requests)
  - name: "ip-rate-limit"
    scope: "ip"
    limit: 50
    window: 60         # 50 per minute per IP
    priority: 4
```

### 4.2 Rule Evaluation

```
Incoming request:
  IP: 192.168.1.100
  User: user-123 (tier: pro)
  Endpoint: POST /api/v1/posts

Rule evaluation (ordered by priority):

1. Global rate limit check
   Key: "rl:global"
   Limit: 10,000/sec
   Current: 5,432 -> PASS

2. Endpoint rate limit check
   Key: "rl:endpoint:POST:/api/v1/posts"
   Limit: 10/min
   Current: 7 -> PASS

3. User tier rate limit check
   Key: "rl:user:user-123"
   Limit: 1,000/hour (pro tier)
   Current: 245 -> PASS

4. IP rate limit check
   Key: "rl:ip:192.168.1.100"
   Limit: 50/min
   Current: 12 -> PASS

All checks pass -> ALLOW request
```

If any rule fails, the request is rejected immediately. There is no need to check remaining rules.

### 4.3 Rule Storage and Hot Reload

```
+-------------------+     +------------------+
| Rules Config      |     | Rules Config     |
| (YAML file or DB) |     | Service          |
+--------+----------+     +--------+---------+
         |                          |
         v                          v
+--------+----------+     +--------+---------+
| On startup:       |     | On rule change:  |
| Load all rules    |     | Publish event    |
| into memory       |     | to Pub/Sub       |
+--------+----------+     +--------+---------+
         |                          |
         v                          v
+--------+----------+     +--------+---------+
| In-memory rule    |<----| All servers      |
| cache on each     |     | receive update   |
| app server        |     | and reload rules |
+-------------------+     +------------------+
```

Rules are loaded into memory on each server at startup and refreshed via pub/sub when changes occur. This avoids a database call on every request.

---

## 5. Multi-Tier Rate Limiting

Production systems need multiple layers of rate limiting. Here is how they work together.

```
+------------------------------------------------------------------+
|                    MULTI-TIER RATE LIMITING                        |
+------------------------------------------------------------------+
|                                                                    |
|  Tier 1: GLOBAL                                                   |
|  +--------------------------------------------------------------+ |
|  | Protects the entire system from total overload                | |
|  | Limit: 50,000 requests/second across all users                | |
|  | Key: "rl:global"                                              | |
|  +--------------------------------------------------------------+ |
|                              |                                     |
|  Tier 2: PER-SERVICE                                               |
|  +--------------------------------------------------------------+ |
|  | Protects individual microservices                              | |
|  | Limit: 5,000 req/sec for user-service                         | |
|  | Key: "rl:service:user-service"                                | |
|  +--------------------------------------------------------------+ |
|                              |                                     |
|  Tier 3: PER-ENDPOINT                                              |
|  +--------------------------------------------------------------+ |
|  | Protects expensive operations                                  | |
|  | Limit: 10 req/min for POST /api/search                        | |
|  | Key: "rl:endpoint:POST:/api/search"                           | |
|  +--------------------------------------------------------------+ |
|                              |                                     |
|  Tier 4: PER-USER                                                  |
|  +--------------------------------------------------------------+ |
|  | Fair usage per user based on tier                              | |
|  | Limit: 100 req/hour for free users                             | |
|  | Key: "rl:user:user-123"                                       | |
|  +--------------------------------------------------------------+ |
|                              |                                     |
|  Tier 5: PER-IP                                                    |
|  +--------------------------------------------------------------+ |
|  | Protects against unauthenticated abuse                         | |
|  | Limit: 50 req/min per IP                                       | |
|  | Key: "rl:ip:192.168.1.100"                                    | |
|  +--------------------------------------------------------------+ |
|                                                                    |
+------------------------------------------------------------------+

Evaluation order: Global -> Service -> Endpoint -> User -> IP
First failure = REJECT (short-circuit)
```

**Why multiple tiers?**

Consider these scenarios:
- A single user makes 1000 requests per second (caught by user tier)
- A botnet of 10,000 IPs each makes 10 requests per second (caught by global tier)
- A bug in a client repeatedly hits a search endpoint (caught by endpoint tier)

No single tier catches all abuse patterns. Multiple tiers provide defense in depth.

---

## 6. HTTP Response Design

When a request is rate-limited, the response must be informative.

```
Allowed Response:
  HTTP/1.1 200 OK
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 57
  X-RateLimit-Reset: 1705312800

Rejected Response:
  HTTP/1.1 429 Too Many Requests
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1705312800
  Retry-After: 45

  {
    "error": "rate_limit_exceeded",
    "message": "You have exceeded your rate limit of 100 requests per hour.",
    "retry_after": 45
  }
```

**Header meanings:**
- `X-RateLimit-Limit`: The maximum number of requests allowed in the window
- `X-RateLimit-Remaining`: How many requests the client can still make
- `X-RateLimit-Reset`: Unix timestamp when the window resets
- `Retry-After`: Seconds until the client should retry (only on 429 responses)

---

## 7. Complete Architecture Diagram

```
+------------------------------------------------------------------+
|                     CLIENT REQUESTS                               |
|  +----------+  +----------+  +----------+  +----------+          |
|  | Mobile   |  | Web App  |  | API      |  | Partner  |          |
|  | Client   |  | Client   |  | Client   |  | API      |          |
|  +----+-----+  +----+-----+  +----+-----+  +----+-----+          |
+-------|-------------|-------------|-------------|------------------+
        |             |             |             |
        v             v             v             v
+-------+-------------+-------------+-------------+-----------------+
|                    API GATEWAY / LOAD BALANCER                     |
|              (First-tier: IP-based rate limiting)                  |
+-------------------------------+-----------------------------------+
                                |
                                v
+-------------------------------+-----------------------------------+
|                    RATE LIMITER MIDDLEWARE                         |
|                                                                    |
|  +------------------+     +------------------+                    |
|  | Request Context  |     | Rule Engine      |                    |
|  | Extractor        |---->| (in-memory rules)|                    |
|  | (user, IP, API   |     | Match request to |                    |
|  |  key, endpoint)  |     | applicable rules |                    |
|  +------------------+     +--------+---------+                    |
|                                    |                               |
|  For each matched rule:            v                               |
|  +------------------+     +--------+---------+                    |
|  | Build Redis Key  |---->| Execute Lua      |                    |
|  | (scope:id:window)|     | Script on Redis  |                    |
|  +------------------+     | (atomic check)   |                    |
|                           +--------+---------+                    |
|                                    |                               |
|                           +--------+---------+                    |
|                           | ALLOW or REJECT  |                    |
|                           | Set response     |                    |
|                           | headers          |                    |
|                           +------------------+                    |
+-------------------------------+-----------------------------------+
                                |
               +----------------+----------------+
               |                                 |
          ALLOWED                            REJECTED
               |                                 |
               v                                 v
+------+-------+--------+          +-------------+--+
| Application Server    |          | 429 Response   |
| (process request      |          | with headers:  |
|  normally)            |          | Retry-After,   |
+------+----------------+          | RateLimit-*    |
       |                           +---------+------+
       v                                     |
  Normal response                            v
  with RateLimit                        Client waits
  headers                              and retries

+-----------------------------------------------------------------+
|                      REDIS CLUSTER                               |
|                                                                   |
|  +----------+  +----------+  +----------+  +----------+         |
|  | Shard 1  |  | Shard 2  |  | Shard 3  |  | Shard 4  |         |
|  |          |  |          |  |          |  |          |         |
|  | Keys:    |  | Keys:    |  | Keys:    |  | Keys:    |         |
|  | rl:user: |  | rl:user: |  | rl:ip:   |  | rl:global|         |
|  |  A-F     |  |  G-M     |  |  all     |  | rl:svc:  |         |
|  +----+-----+  +----+-----+  +----+-----+  +----+-----+         |
|       |              |              |              |              |
|  +----+-----+  +----+-----+  +----+-----+  +----+-----+         |
|  | Replica  |  | Replica  |  | Replica  |  | Replica  |         |
|  +----------+  +----------+  +----------+  +----------+         |
+-----------------------------------------------------------------+

+-----------------------------------------------------------------+
|                   SUPPORTING COMPONENTS                          |
|                                                                   |
|  +-------------------+  +-------------------+  +---------------+ |
|  | Rules Config DB   |  | Metrics Collector |  | Dashboard     | |
|  | (PostgreSQL)      |  | (Prometheus)      |  | (Grafana)     | |
|  |                   |  |                   |  |               | |
|  | Store and update  |  | Track:            |  | Visualize:    | |
|  | rate limit rules  |  | - Requests/sec    |  | - Rate limit  | |
|  | per endpoint,     |  | - Rejections/sec  |  |   hit rates   | |
|  | user tier, etc.   |  | - Latency of      |  | - Top limited | |
|  |                   |  |   rate checks     |  |   users/IPs   | |
|  +-------------------+  +-------------------+  +---------------+ |
+-----------------------------------------------------------------+
```

---

## 8. Advanced Topics

### 8.1 Distributed Rate Limiting Across Data Centers

When your service runs in multiple data centers, you have two choices:

```
Option A: Global counters (consistent but slower)

+------------------+            +------------------+
| Data Center US   |            | Data Center EU   |
| +------+         |            |         +------+ |
| | App  +----+    |            |    +----+ App  | |
| +------+    |    |            |    |    +------+ |
|             v    |            |    v              |
|       +-----+--+ |            | +--+-----+       |
|       | Redis  +--+----------+--+ Redis  |       |
|       | (sync) | |  Cross-DC  | | (sync) |       |
|       +--------+ |  replication| +--------+       |
+------------------+            +------------------+

Pros: Globally accurate counts
Cons: Cross-DC latency on every request (50-100ms)


Option B: Local counters with sync (fast but approximate)

+------------------+            +------------------+
| Data Center US   |            | Data Center EU   |
| +------+         |            |         +------+ |
| | App  +----+    |            |    +----+ App  | |
| +------+    |    |            |    |    +------+ |
|             v    |            |    v              |
|       +-----+--+ |            | +--+-----+       |
|       | Local  | |            | | Local  |       |
|       | Redis  | |  Periodic  | | Redis  |       |
|       +---+----+ |   sync    | +----+---+       |
|           |      +--+-----+--+      |            |
|           +-------->|Sync |<--------+            |
|                  |  |Svc  |  |                    |
|                  +--+-----+--+                    |
+------------------+            +------------------+

Pros: Low latency (local Redis)
Cons: Slightly inaccurate (users can exceed limit by up to 2x briefly)
```

Most systems choose Option B and accept the slight inaccuracy. For the total limit, split it across data centers proportional to their traffic.

### 8.2 Rate Limiting WebSocket Connections

WebSocket connections are long-lived. Rate limiting applies differently:

```
Connection-level:
  - Limit new connections per user: 5 per minute
  - Limit total active connections per user: 3

Message-level:
  - Limit messages per connection per second: 10
  - Limit message size: 64 KB
```

### 8.3 Client-Side Rate Limiting

Smart clients implement their own rate limiting to avoid wasting requests:

```
Client-side approach:

1. Read X-RateLimit-Remaining from responses
2. If remaining < threshold, slow down proactively
3. If 429 received, back off using Retry-After header
4. Implement exponential backoff for retries:
   wait = min(base * 2^attempt + jitter, max_wait)
```

---

## Common Mistakes

1. **Using fixed windows without understanding boundary issues.** Clients can send 2x the intended rate by timing requests at window boundaries. Use sliding windows or token buckets instead.

2. **Non-atomic read-then-write in Redis.** Separate GET and INCR commands create race conditions. Always use Lua scripts for atomic operations.

3. **Fail-closed by default.** If Redis is down and you reject all traffic, your rate limiter has become a denial-of-service attack on your own service. Default to fail-open.

4. **Same limits for all endpoints.** A search endpoint and a health check have vastly different costs. Expensive endpoints need tighter limits.

5. **No rate limit headers in responses.** Clients cannot implement smart backoff without knowing their remaining quota. Always include `X-RateLimit-*` headers.

6. **Forgetting about distributed clock skew.** Servers in different data centers may have slightly different clocks. Use Redis server time or tolerate small inaccuracies.

---

## Best Practices

1. **Use Lua scripts for atomicity.** Every rate limit check should be a single atomic operation. Lua scripts in Redis guarantee this.

2. **Include rate limit information in every response.** Even successful responses should include `X-RateLimit-Remaining` so clients can self-regulate.

3. **Implement multiple tiers.** Global, per-service, per-endpoint, per-user, and per-IP tiers catch different abuse patterns.

4. **Use token bucket for most API rate limiting.** It is simple, memory efficient, and handles bursts gracefully. Sliding window is better when you need strict precision.

5. **Monitor and alert on rate limit hit rates.** A sudden increase in 429 responses might mean a legitimate user is having problems, not just abuse. Track and investigate.

6. **Allow configuration changes without deployments.** Store rules in a database or config service with hot reloading. This lets you respond to abuse quickly.

---

## Quick Summary

A distributed rate limiter checks every incoming request against configurable rules using shared counters in Redis. The two main algorithms are token bucket (allows bursts, simple) and sliding window counter (precise, no burst). Lua scripts ensure atomicity. Multi-tier limiting (global, service, endpoint, user, IP) provides defense in depth. The system fails open when Redis is unavailable and includes informative headers so clients can self-regulate.

---

## Key Points

- Token bucket allows controlled bursts and uses O(1) memory per user
- Sliding window counter avoids the boundary problem of fixed windows
- Lua scripts in Redis eliminate race conditions by making read-check-increment atomic
- Multi-tier rate limiting (global, service, endpoint, user, IP) catches different abuse patterns
- Fail-open is usually better than fail-closed when Redis is unavailable
- Rate limit headers (Remaining, Reset, Retry-After) enable smart client behavior
- Rules should be configurable without code deployments
- Local in-memory counters serve as a fallback when Redis is down

---

## Practice Questions

1. Your Redis cluster is experiencing high latency (50ms instead of the usual 1ms). How does this affect your rate limiter, and what can you do about it?

2. A sophisticated attacker rotates through thousands of IP addresses to bypass per-IP rate limits. How would you detect and mitigate this?

3. You need to implement a rate limiter for a real-time bidding system where latency above 5ms is unacceptable. How would you modify the architecture?

4. Your API has both read and write endpoints. Reads are cheap, writes are expensive. How would you design the rate limiting rules?

5. A partner integration sends legitimate bursts of 1000 requests in 1 second, then nothing for 59 seconds. How would you configure the rate limiter to allow this pattern while still protecting against abuse?

---

## Exercises

**Exercise 1: Implement Token Bucket in Redis**

Write a complete Redis Lua script that implements the token bucket algorithm. Test it by simulating 100 requests arriving at different intervals and verifying that the correct number are allowed and rejected. Your script should handle the case where the key does not exist yet (first request).

**Exercise 2: Compare Algorithms**

Build a simulation (in any language) that compares fixed window, sliding window counter, and token bucket. For each algorithm:
- Simulate 1000 requests with a limit of 10 per minute
- Vary the arrival pattern (uniform, bursty, boundary-crossing)
- Report how many requests each algorithm allows
- Calculate the maximum actual rate achieved in any 60-second window

**Exercise 3: Design a Rate Limit Dashboard**

Design a monitoring dashboard for your rate limiter. Specify:
- What metrics to collect (counters, histograms, gauges)
- How to identify the top 10 rate-limited users in real time
- How to detect when a legitimate user is being unfairly limited
- What alerts to configure and at what thresholds

---

## What Is Next?

You now understand how to protect your services with a distributed rate limiter. The next chapter tackles a very different kind of system: a web crawler. You will learn how to systematically crawl billions of web pages while being polite, avoiding traps, and handling the immense scale of the internet. The web crawler design will test your ability to think about distributed systems, queues, and deduplication at truly massive scale.
