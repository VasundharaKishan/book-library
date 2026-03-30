# Chapter 11: Rate Limiting

## What You Will Learn

- Why rate limiting is essential for protecting any production API
- Five rate limiting algorithms: token bucket, leaky bucket, fixed window counter, sliding window log, and sliding window counter
- How each algorithm works, with step-by-step ASCII diagrams
- The trade-offs between accuracy, memory, and complexity
- Implementation levels: application, API gateway, load balancer, CDN
- HTTP 429 responses and rate limit headers
- Distributed rate limiting across multiple servers
- How to design rate limits that protect your system without frustrating legitimate users

## Why This Chapter Matters

Without rate limiting, a single user or bot can overwhelm your entire system. One misbehaving client sending 10,000 requests per second can:

- Crash your servers
- Exhaust your database connections
- Spike your cloud bill
- Deny service to all other users
- Enable brute-force attacks on login endpoints
- Scrape your entire dataset

Rate limiting is not optional. Every production API needs it. And in system design interviews, rate limiting is one of the most frequently asked design questions because it combines algorithms, distributed systems, and practical engineering judgment.

---

## 11.1 What Is Rate Limiting?

Rate limiting is the practice of controlling the rate at which clients can send requests to your system. When a client exceeds the allowed rate, their requests are rejected (or throttled) until the rate drops back to an acceptable level.

### The Amusement Park Analogy

Imagine an amusement park ride that can safely handle 20 people per cycle, with a cycle every 5 minutes.

- **Without rate limiting:** 200 people rush to the ride at once. The line is chaotic, people get pushed, and the ride operator is overwhelmed.
- **With rate limiting:** A gate lets exactly 20 people through every 5 minutes. Others wait in an orderly queue. Everyone gets a ride, safely and predictably.

```
WITHOUT RATE LIMITING:

  Requests:  ||||||||||||||||||||||||||||||||||||  (all at once)
                          |
                          v
                    +----------+
                    |  Server  |  <-- OVERWHELMED!
                    +----------+


WITH RATE LIMITING:

  Allowed:   |||| |||| |||| |||| |||| ||||  (steady flow)
  Rejected:                    XXXXX         (excess dropped)
                          |
                          v
                    +----------+
                    |  Server  |  <-- Happy and healthy
                    +----------+
```

### Types of Rate Limits

```
+--------------------+-------------------------------------------+
| Type               | Example                                   |
+--------------------+-------------------------------------------+
| User-based         | User X can make 100 requests per minute   |
| IP-based           | IP address can make 50 requests per minute|
| API key-based      | API key can make 1000 requests per hour   |
| Endpoint-based     | /api/login allows 5 attempts per minute   |
| Global             | Server accepts max 10,000 requests/sec    |
+--------------------+-------------------------------------------+
```

---

## 11.2 Token Bucket Algorithm

The token bucket is one of the most widely used rate limiting algorithms. It is simple, memory-efficient, and allows short bursts of traffic.

### How It Works

Imagine a bucket that holds tokens. Tokens are added at a fixed rate. Each request takes one token from the bucket. If the bucket is empty, the request is rejected.

```
TOKEN BUCKET:

  Bucket capacity: 4 tokens
  Refill rate: 1 token per second

  Time    Bucket      Request     Result
  ----    ------      -------     ------
  t=0     [****]      --          4 tokens (full)
  t=0     [***_]      Request 1   ALLOWED (3 tokens left)
  t=0     [**__]      Request 2   ALLOWED (2 tokens left)
  t=0     [*___]      Request 3   ALLOWED (1 token left)
  t=0     [____]      Request 4   ALLOWED (0 tokens left)
  t=0     [____]      Request 5   REJECTED (empty!)
  t=1     [*___]      --          1 token added (refill)
  t=1     [____]      Request 6   ALLOWED (0 tokens left)
  t=2     [*___]      --          1 token added
  t=3     [**__]      --          1 token added
  t=4     [***_]      --          1 token added


ASCII DIAGRAM:

           Tokens added at fixed rate
                    |
                    v
           +-------+-------+
           |               |
           |    BUCKET     |  Capacity: max tokens
           |   [* * * *]   |
           |               |
           +-------+-------+
                   |
                   v
            Take 1 token
            per request
                   |
           +-------+-------+
           |               |
           | Tokens > 0 ?  |
           |               |
           +---+-------+---+
               |       |
              YES      NO
               |       |
               v       v
           ALLOW    REJECT
           request  request
```

### Key Properties

- **Burst friendly:** A full bucket allows a burst of requests up to the bucket capacity
- **Smooth average:** Over time, the average rate equals the refill rate
- **Memory efficient:** Only needs to store token count and last refill timestamp (2 values per user)

### Real-World Usage

Amazon API Gateway and Stripe use token bucket. It is the default choice for most rate limiters.

```
PARAMETERS:
  bucket_size = 10       (allows bursts of up to 10)
  refill_rate = 2/sec    (sustained rate of 2 requests/second)

  Scenario 1: Steady traffic (2 req/sec)
  --> All requests allowed, bucket stays near full

  Scenario 2: Burst of 10 requests, then silence
  --> All 10 allowed (bucket drains)
  --> Next request must wait for refill

  Scenario 3: 5 req/sec sustained
  --> First 10 allowed (burst)
  --> Then only 2/sec allowed (refill rate)
  --> 3/sec rejected
```

---

## 11.3 Leaky Bucket Algorithm

The leaky bucket processes requests at a constant rate, like water leaking from a bucket at a fixed drip rate. Requests that arrive when the bucket is full are discarded.

### How It Works

```
LEAKY BUCKET:

  Think of a bucket with a hole at the bottom.
  Water (requests) pours in from the top.
  Water leaks out (is processed) at a constant rate.
  If the bucket overflows, water (requests) is discarded.

           Requests pour in
                |
                v
         +------+------+
         |  ~~~~~~~~   |  <-- Bucket (queue)
         |  ~~~~~~~~   |      Capacity: max queue size
         |  ~~~~~~~~   |
         |  ~~~~~~~~   |
         +------+------+
                |
                | Leak at constant rate
                v
         Process requests
         (fixed rate output)


  TIMELINE:

  Input rate:     ||||  ||    |||||||||||  ||
  (variable)

  Queue:          [####][####][##########][##]
                                ^^^^^^^^
                                overflow --> REJECTED

  Output rate:    | | | | | | | | | | | | | |
  (constant)     (steady, predictable processing)
```

### Token Bucket vs Leaky Bucket

```
+--------------------+------------------+------------------+
| Feature            | Token Bucket     | Leaky Bucket     |
+--------------------+------------------+------------------+
| Burst handling     | Allows bursts    | Smooths out      |
|                    | (up to bucket    | bursts into      |
|                    | capacity)        | steady flow      |
+--------------------+------------------+------------------+
| Output rate        | Variable         | Constant         |
|                    | (bursty)         | (steady)         |
+--------------------+------------------+------------------+
| When bucket is full| Requests rejected| Requests queued  |
|                    | immediately      | then rejected    |
|                    |                  | if queue is full |
+--------------------+------------------+------------------+
| Implementation     | Counter + timer  | Queue + timer    |
+--------------------+------------------+------------------+
| Memory             | Very low         | Higher (stores   |
|                    | (2 values)       | queued requests)  |
+--------------------+------------------+------------------+
| Best for           | APIs where       | Traffic shaping, |
|                    | bursts are OK    | steady processing|
+--------------------+------------------+------------------+
```

### Real-World Usage

Leaky bucket is used in network traffic shaping (controlling bandwidth). Shopify uses a variation for their API rate limiter.

---

## 11.4 Fixed Window Counter

The simplest counting algorithm. Divide time into fixed windows (e.g., 1-minute intervals) and count requests in each window. Reject when the count exceeds the limit.

### How It Works

```
FIXED WINDOW COUNTER:

  Limit: 5 requests per minute

  Window 1          Window 2          Window 3
  [00:00 - 00:59]   [01:00 - 01:59]   [02:00 - 02:59]

  Timeline:
  00:00  Req 1 --> Count=1  ALLOWED
  00:15  Req 2 --> Count=2  ALLOWED
  00:30  Req 3 --> Count=3  ALLOWED
  00:45  Req 4 --> Count=4  ALLOWED
  00:50  Req 5 --> Count=5  ALLOWED
  00:55  Req 6 --> Count=6  REJECTED (limit=5!)
  01:00  -- New window, count resets to 0 --
  01:05  Req 7 --> Count=1  ALLOWED


  +--------+--------+--------+
  | Window1| Window2| Window3|
  |Count: 5|Count: 3|Count: 0|
  +--------+--------+--------+
  ^        ^        ^
  00:00    01:00    02:00
```

### The Boundary Problem

Fixed windows have a critical flaw: traffic can spike at window boundaries.

```
BOUNDARY PROBLEM:

  Limit: 5 requests per minute

  Window 1                    Window 2
  [00:00 -------- 00:59]     [01:00 -------- 01:59]

  00:50  Req 1  ALLOWED       01:00  Req 6  ALLOWED
  00:51  Req 2  ALLOWED       01:01  Req 7  ALLOWED
  00:52  Req 3  ALLOWED       01:02  Req 8  ALLOWED
  00:53  Req 4  ALLOWED       01:03  Req 9  ALLOWED
  00:54  Req 5  ALLOWED       01:04  Req 10 ALLOWED

  10 requests in 14 seconds!
  (5 at end of Window 1 + 5 at start of Window 2)

  |      Window 1      |      Window 2      |
  |                |||||*****|               |
  |                     ^                    |
  |              10 requests in              |
  |              this 14-second span!        |
  |                                          |

  The rate limit is 5/minute, but 10 requests
  passed in a burst at the boundary.
```

### Key Properties

- **Simple:** Just a counter per window (1 value per user per window)
- **Memory efficient:** Very low memory
- **Boundary problem:** Can allow 2x the limit at window boundaries
- **Used when:** Approximate limiting is acceptable

---

## 11.5 Sliding Window Log

Fixes the boundary problem by tracking the exact timestamp of every request.

### How It Works

```
SLIDING WINDOW LOG:

  Limit: 5 requests per minute
  Window: last 60 seconds (slides with current time)

  Keep a log of all request timestamps:

  Time    Log                         Count  Result
  ----    ---                         -----  ------
  00:10   [00:10]                     1      ALLOWED
  00:25   [00:10, 00:25]              2      ALLOWED
  00:40   [00:10, 00:25, 00:40]       3      ALLOWED
  00:50   [00:10, 00:25, 00:40, 00:50] 4     ALLOWED
  00:55   [00:10, 00:25, 00:40,        5     ALLOWED
           00:50, 00:55]
  01:05   [00:25, 00:40, 00:50,        4     ALLOWED
           00:55, 01:05]
           ^-- 00:10 expired (more than 60 seconds ago)

  At any moment, count = timestamps within last 60 seconds.


  SLIDING WINDOW VISUALIZATION:

  Timeline:  00:00    00:20    00:40    01:00    01:20
             |--------|--------|--------|--------|
                 *        *       **  *
                00:10   00:25  00:40 00:50
                               00:55

  At t=00:55:
     Window: [00:55 - 60s] = [23:55 to 00:55]
             --> All 5 timestamps in window
             --> Count = 5, limit reached

  At t=01:05:
     Window: [01:05 - 60s] = [00:05 to 01:05]
             --> 00:10 expired!
             --> Count = 4, request allowed
```

### Key Properties

- **Accurate:** No boundary problem, exact rate tracking
- **Memory intensive:** Must store every request timestamp (could be thousands per user)
- **Slower:** Must scan and clean up old timestamps on each request
- **Used when:** Exact accuracy is required (security-critical endpoints)

---

## 11.6 Sliding Window Counter

Combines the low memory of fixed window with the accuracy of sliding window. It estimates the count using a weighted average of the current and previous windows.

### How It Works

```
SLIDING WINDOW COUNTER:

  Limit: 10 requests per minute
  Current time: 01:15 (15 seconds into the current window)

  Previous window [00:00-00:59]: 8 requests
  Current window  [01:00-01:59]: 3 requests so far

  Sliding window position:
  |---Previous Window---|---Current Window---|
  |########             |###                 |
  |  8 requests         | 3 requests         |
                  ^
            We are here: 01:15
            (25% into current window = 75% of prev window counts)

  Estimated count = (prev_count * overlap%) + current_count
                  = (8 * 0.75) + 3
                  = 6 + 3
                  = 9

  9 < 10 limit --> ALLOWED


  ANOTHER EXAMPLE at 01:45 (75% into current window):

  Estimated count = (8 * 0.25) + current_count
                  = 2 + current_count

  Much more room because most of the previous window
  has "slid out."
```

### Step-by-Step Diagram

```
SLIDING WINDOW COUNTER VISUALIZATION:

  Previous Window (00:00-00:59)    Current Window (01:00-01:59)
  +-------------------------------+-------------------------------+
  |  ########                     | ###                           |
  |  8 requests                   | 3 requests                   |
  +-------------------------------+-------------------------------+
                                  ^
                             Window boundary

  At t=01:15 (15 sec into current window):
  Overlap with previous = 1 - (15/60) = 0.75 (75%)

  +-------------------------------+-------------------------------+
  |                  |############|####|                           |
  |   Already slid   | 75% of    |Curr|   Rest of current window  |
  |   out (25%)      | prev (6)  | (3)|                           |
  +-------------------------------+-------------------------------+
  <--- 60 second sliding window ---->

  Estimated rate = 6 + 3 = 9 requests in the sliding window
```

### Key Properties

- **Good accuracy:** Much better than fixed window, close to sliding log
- **Low memory:** Only 2 counters per user per window (previous count + current count)
- **Fast:** Simple arithmetic, no timestamp scanning
- **Slight inaccuracy:** The estimate assumes previous window requests are evenly distributed (they might not be)

### This is the recommended algorithm for most production rate limiters.

---

## 11.7 Algorithm Comparison

```
+------------------+----------+--------+---------+-----------+
| Algorithm        | Accuracy | Memory | Speed   | Burst     |
|                  |          |        |         | Handling  |
+------------------+----------+--------+---------+-----------+
| Token Bucket     | Good     | Low    | Fast    | Allows    |
|                  |          | (2 val)| O(1)    | bursts    |
+------------------+----------+--------+---------+-----------+
| Leaky Bucket     | Good     | Medium | Fast    | Smooths   |
|                  |          | (queue)| O(1)    | bursts    |
+------------------+----------+--------+---------+-----------+
| Fixed Window     | Poor     | Low    | Fast    | 2x burst  |
| Counter          | (boundary| (1 val)| O(1)    | at edges  |
|                  |  issue)  |        |         |           |
+------------------+----------+--------+---------+-----------+
| Sliding Window   | Exact    | High   | Slower  | No burst  |
| Log              |          | (all   | O(n)    | issues    |
|                  |          | stamps)|         |           |
+------------------+----------+--------+---------+-----------+
| Sliding Window   | Very Good| Low    | Fast    | Minor     |
| Counter          | (approx) | (2 val)| O(1)    | approx    |
+------------------+----------+--------+---------+-----------+

Recommendation:
  - Default choice: Token Bucket or Sliding Window Counter
  - Need bursting: Token Bucket
  - Need smoothing: Leaky Bucket
  - Need exact accuracy: Sliding Window Log
  - Need simplicity: Fixed Window Counter
```

---

## 11.8 Implementation Levels

Rate limiting can be applied at different points in your architecture:

```
RATE LIMITING AT DIFFERENT LAYERS:

  +--------+
  | Client |
  +---+----+
      |
      v
  +---+--------+   Layer 1: CDN / Edge
  |  CDN       |   (Cloudflare rate limiting)
  |  Rate Limit|   Catches bot traffic, DDoS
  +---+--------+
      |
      v
  +---+--------+   Layer 2: API Gateway
  |  API       |   (Kong, AWS API Gateway)
  |  Gateway   |   Per-API-key rate limiting
  +---+--------+
      |
      v
  +---+--------+   Layer 3: Load Balancer
  |  Load      |   (Nginx, HAProxy)
  |  Balancer  |   Connection rate limiting
  +---+--------+
      |
      v
  +---+--------+   Layer 4: Application
  |  App       |   (middleware in your code)
  |  Server    |   Fine-grained, per-endpoint limits
  +---+--------+
      |
      v
  +---+--------+   Layer 5: Database
  |  Database  |   Connection pooling
  |            |   Query rate limiting
  +---+--------+
```

### Where to Implement

```
+------------------+-------------------------------------------+
| Layer            | Best For                                  |
+------------------+-------------------------------------------+
| CDN/Edge         | DDoS protection, bot blocking,            |
|                  | geographic filtering                      |
+------------------+-------------------------------------------+
| API Gateway      | Per-key limits, plan-based tiers,          |
|                  | centralized rate limiting                  |
+------------------+-------------------------------------------+
| Load Balancer    | Connection limits, basic request rate      |
+------------------+-------------------------------------------+
| Application      | Complex business rules (e.g., "5 login    |
|                  | attempts per account per minute")          |
+------------------+-------------------------------------------+
```

Most production systems use multiple layers. The CDN handles DDoS-scale abuse. The API gateway enforces per-customer limits. The application handles business-specific rate limiting.

---

## 11.9 HTTP 429 and Rate Limit Headers

When a request is rate limited, your API should return HTTP 429 (Too Many Requests) with headers that tell the client what happened and when to retry.

```
RATE LIMITED RESPONSE:

  HTTP/1.1 429 Too Many Requests
  Content-Type: application/json
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1672531260
  Retry-After: 30

  {
    "error": {
      "code": "RATE_LIMIT_EXCEEDED",
      "message": "You have exceeded the rate limit of 100
                  requests per minute. Please wait 30 seconds.",
      "retry_after": 30
    }
  }


SUCCESSFUL RESPONSE (with rate limit info):

  HTTP/1.1 200 OK
  Content-Type: application/json
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 73
  X-RateLimit-Reset: 1672531260

  {
    "data": { ... }
  }


HEADER REFERENCE:
+------------------------+-----------------------------------+
| Header                 | Meaning                           |
+------------------------+-----------------------------------+
| X-RateLimit-Limit      | Max requests per window           |
| X-RateLimit-Remaining  | Requests remaining in window      |
| X-RateLimit-Reset      | Unix timestamp when window resets |
| Retry-After            | Seconds to wait (in 429 response) |
+------------------------+-----------------------------------+
```

### Client Behavior

Good API clients respect rate limits:

```
CLIENT-SIDE RATE LIMIT HANDLING:

  1. Check X-RateLimit-Remaining before making requests
  2. If remaining is low, slow down
  3. If you get a 429, wait for Retry-After seconds
  4. Use exponential backoff for retries:
     - 1st retry: wait 1 second
     - 2nd retry: wait 2 seconds
     - 3rd retry: wait 4 seconds
     - 4th retry: wait 8 seconds
     - Add jitter (random offset) to avoid thundering herd
```

---

## 11.10 Distributed Rate Limiting

When your API runs on multiple servers, rate limiting becomes much harder. Each server sees only a fraction of the traffic.

### The Problem

```
PROBLEM: LOCAL RATE LIMITING

  Limit: 100 requests per minute per user

  +----------+     +----------+     +----------+
  | Server 1 |     | Server 2 |     | Server 3 |
  | Count: 40|     | Count: 40|     | Count: 40|
  +----------+     +----------+     +----------+

  Each server thinks the user has sent 40 requests.
  Each server allows the user to continue.
  But the user has actually sent 120 requests total!
  The rate limit is ineffective.
```

### Solution 1: Centralized Rate Limiter (Redis)

Use a shared counter in Redis that all servers read and write to.

```
CENTRALIZED RATE LIMITER:

  +----------+     +----------+     +----------+
  | Server 1 |     | Server 2 |     | Server 3 |
  +-----+----+     +-----+----+     +-----+----+
        |                |                |
        +--------+-------+--------+-------+
                 |                |
           +-----+-----+         |
           |   Redis    |         |
           |  Count:120 |  <------+
           |  REJECTED! |
           +------------+

  All servers check the same counter in Redis.
  Atomic increment: INCR user:42:rate_limit
```

```
REDIS IMPLEMENTATION (pseudocode):

  function is_allowed(user_id, limit, window_seconds):
      key = "rate:" + user_id + ":" + current_window()
      count = redis.INCR(key)
      if count == 1:
          redis.EXPIRE(key, window_seconds)
      return count <= limit
```

**Pros:** Accurate, simple logic
**Cons:** Redis becomes a single point of failure. Added latency for every request (network round trip to Redis).

### Solution 2: Sticky Sessions

Route all requests from the same user to the same server. Each server can use local rate limiting.

```
STICKY SESSIONS:

  Load Balancer routes by user_id:

  User 42 --> Always Server 1
  User 43 --> Always Server 2
  User 44 --> Always Server 3

  Each server has the complete count for its users.
  No shared state needed!
```

**Pros:** No shared state, fast
**Cons:** Uneven load distribution. If a server restarts, counts are lost.

### Solution 3: Loose Coordination

Each server tracks locally but periodically syncs with a central store. This allows slight over-limiting but avoids the latency of checking Redis on every request.

```
LOOSE COORDINATION:

  +----------+                +----------+
  | Server 1 |                | Server 2 |
  | Local: 15|  Sync every    | Local: 12|
  +-----+----+  5 seconds     +-----+----+
        |                           |
        +--------> Redis <----------+
                   Total: 27
                   (approximate)
```

### Choosing a Strategy

```
+-------------------+----------+----------+-------------+
| Strategy          | Accuracy | Latency  | Complexity  |
+-------------------+----------+----------+-------------+
| Redis (central)   | High     | +1-2ms   | Low         |
| Sticky sessions   | High     | None     | Medium      |
| Loose coordination| Moderate | Minimal  | High        |
+-------------------+----------+----------+-------------+

For most systems, centralized Redis is the right choice.
Redis is fast enough (~1ms) that the added latency is
acceptable, and accuracy is important.
```

---

## 11.11 Rate Limiting Strategies

### Different Limits for Different Endpoints

Not all endpoints are equal. Protect sensitive endpoints more aggressively:

```
+------------------------+-------------------+-----------------+
| Endpoint               | Rate Limit        | Why             |
+------------------------+-------------------+-----------------+
| GET /products          | 1000/min          | Read-only, safe |
| POST /orders           | 20/min            | Creates data    |
| POST /login            | 5/min per account | Brute force     |
|                        |                   | protection      |
| POST /password-reset   | 3/hour            | Abuse prevention|
| GET /search            | 30/min            | Expensive query |
| POST /upload           | 10/min            | Resource heavy  |
+------------------------+-------------------+-----------------+
```

### Tiered Rate Limits

Different limits for different customer tiers:

```
+------------------+---------+----------+--------------------+
| Tier             | Limit   | Window   | Monthly Cost       |
+------------------+---------+----------+--------------------+
| Free             | 60/hr   | 1 hour   | $0                 |
| Starter          | 600/hr  | 1 hour   | $29                |
| Professional     | 6000/hr | 1 hour   | $99                |
| Enterprise       | Custom  | Custom   | Contact sales      |
+------------------+---------+----------+--------------------+
```

### Graceful Degradation

Instead of hard rejecting, you can degrade service quality:

```
GRACEFUL DEGRADATION:

  0-50%   of limit: Full service
  50-80%  of limit: Serve from cache (skip DB)
  80-100% of limit: Return simplified responses
  >100%   of limit: 429 Too Many Requests

  This lets high-traffic users still get some value
  instead of being completely cut off.
```

---

## Common Mistakes

1. **No rate limiting at all.** Every production API needs rate limiting. It is not optional.

2. **Limiting only by IP.** Multiple users can share an IP (corporate NAT, mobile carriers). Limit by authenticated user ID when possible.

3. **Too aggressive limits.** If your limit is too low, legitimate users are frustrated. Start generous and tighten based on data.

4. **Not returning rate limit headers.** Clients cannot respect limits they do not know about. Always include X-RateLimit-* headers.

5. **Local-only rate limiting with multiple servers.** Each server sees only its portion of traffic. Use centralized rate limiting (Redis) for accuracy.

6. **Same limits for all endpoints.** A login endpoint needs much stricter limits than a product listing endpoint.

7. **Not handling the clock synchronization problem.** In distributed systems, server clocks may differ. Use a central time source (Redis) rather than local server time.

8. **Forgetting about legitimate spikes.** If a user goes viral and their content is shared widely, sudden traffic is legitimate. Have a plan for temporary limit increases.

---

## Best Practices

1. **Use token bucket or sliding window counter.** These provide the best balance of accuracy, memory, and performance.

2. **Rate limit at multiple layers.** CDN for DDoS, API gateway for per-key limits, application for business rules.

3. **Return clear 429 responses with Retry-After.** Help clients understand and respect your limits.

4. **Use Redis for distributed rate limiting.** It is fast, atomic, and battle-tested for this use case.

5. **Set different limits for different endpoints.** Expensive operations need stricter limits.

6. **Monitor rate limit metrics.** Track how often limits are hit, by whom, and for which endpoints. This data informs limit adjustments.

7. **Provide rate limit headers on every response.** Let clients see their remaining quota before they hit the limit.

8. **Allow limit overrides for special cases.** Internal services, load testing, and trusted partners may need higher limits. Build in the mechanism to override.

9. **Use exponential backoff on the client side.** Clients should not retry immediately after a 429; they should wait and increase the wait time on successive retries.

10. **Log rate-limited requests.** You need to distinguish between abuse (block the user) and legitimate overuse (increase the limit).

---

## Quick Summary

Rate limiting controls how many requests a client can make in a given time period. The five main algorithms are: token bucket (allows bursts, simple, most popular), leaky bucket (smooths traffic), fixed window counter (simple but has boundary issues), sliding window log (exact but memory-heavy), and sliding window counter (good balance of accuracy and efficiency). Rate limiting should happen at multiple levels: CDN, API gateway, and application. Return HTTP 429 with rate limit headers when limits are exceeded. For multi-server deployments, use centralized rate limiting with Redis for accurate counting. Set different limits for different endpoints and customer tiers.

---

## Key Points

- Rate limiting protects your system from abuse, DDoS, brute force, and runaway clients
- Token bucket and sliding window counter are the best default algorithms
- Fixed window counter has a boundary problem that allows 2x burst at window edges
- Sliding window log is exact but uses too much memory for high-traffic systems
- Use Redis for distributed rate limiting -- local-only counters are inaccurate with multiple servers
- Return HTTP 429 with X-RateLimit-* headers and Retry-After
- Rate limit at multiple layers: CDN, API gateway, and application
- Different endpoints need different limits -- protect login and payment endpoints aggressively

---

## Practice Questions

1. Explain the boundary problem with fixed window counters. A user has a limit of 100 requests per minute. Show a scenario where they make 200 requests in 2 minutes but 150 of them fall within a single 60-second span.

2. Your API serves 50,000 users with a rate limit of 100 requests per minute per user. You use the sliding window log algorithm, storing timestamps in Redis. Estimate the memory usage. Then calculate the memory for the same scenario using the sliding window counter. Which would you choose?

3. A customer complains that they are being rate limited even though they believe they are under the limit. You have 5 API servers behind a load balancer, each with its own local rate counter. Explain the problem and propose a solution.

4. Design a rate limiting system for a login endpoint that prevents brute-force attacks but does not lock out legitimate users. Consider: per-IP limits, per-account limits, CAPTCHA triggers, and gradual lockout.

5. Compare token bucket and leaky bucket for an API that receives bursty traffic (e.g., a mobile app that syncs data every few minutes). Which algorithm would be better and why?

---

## Exercises

**Exercise 1: Implement Token Bucket**
Write pseudocode for a token bucket rate limiter. Include: initialization (bucket size, refill rate), the `allow_request()` function, and token refill logic. Handle the case where multiple seconds have passed since the last request (add multiple tokens at once, capped at bucket size).

**Exercise 2: Distributed Rate Limiter Design**
Design a distributed rate limiting service using Redis. Draw the architecture with multiple API servers, a Redis cluster, and the request flow. Address: how to handle Redis being temporarily unavailable (fail open or fail closed?), how to minimize the number of Redis calls per request, and how to handle clock skew.

**Exercise 3: Rate Limit Configuration**
You are building a SaaS API with three tiers: Free, Pro, and Enterprise. Design the rate limit configuration for these endpoints: GET /items (list), POST /items (create), GET /items/:id (detail), DELETE /items/:id (delete), POST /items/bulk (batch create), GET /search (full-text search). For each tier and endpoint, specify the limit and window, and explain your reasoning.

---

## What Is Next?

In this chapter, you learned how to protect your API from excessive traffic. But rate limiting is just one piece of the puzzle. When you need to distribute data across multiple servers -- whether for a cache, a database, or a rate limiter -- you need a way to decide which server handles which data. In Chapter 12, you will learn about consistent hashing, the algorithm that solves this distribution problem elegantly and is used by virtually every distributed system.
