# Chapter 5: Content Delivery Networks (CDNs)

## What You Will Learn

- What a CDN is and why it dramatically improves performance for global users
- How CDNs use DNS to route users to the nearest edge server
- The difference between push CDN and pull CDN architectures
- Static content vs dynamic content caching
- Cache-control headers and how they govern CDN behavior
- Cache invalidation and purging strategies
- Major CDN providers: CloudFront, Cloudflare, and Akamai
- When to use a CDN and when not to
- How CDN request flow works from end to end

## Why This Chapter Matters

In Chapter 4, you learned how caching reduces latency by keeping data in a faster storage layer. But there is a type of latency that no amount of server-side caching can fix: the speed of light.

If your server is in New York and your user is in Tokyo, every request must travel roughly 11,000 miles each way. Even at the speed of light, that is about 70 milliseconds of round-trip time -- and real-world networks add much more due to routing hops, congestion, and protocol overhead.

A CDN solves this by placing copies of your content on servers around the world. Instead of every user fetching data from your single origin server, they fetch it from a nearby CDN server (called an edge server). This is one of the simplest and highest-impact improvements you can make to any web application.

---

## 5.1 What Is a CDN?

A CDN (Content Delivery Network) is a geographically distributed network of servers that delivers content to users from the location nearest to them.

### The Warehouse Analogy

Imagine you run an online store that ships physical products. Your only warehouse is in Chicago.

- A customer in Chicago gets their order in 1 day.
- A customer in Los Angeles waits 4 days.
- A customer in London waits 10 days.
- A customer in Tokyo waits 14 days.

Now imagine you open small warehouses (fulfillment centers) in Los Angeles, London, and Tokyo. You stock each warehouse with your most popular products.

- Customer in Chicago: 1 day (from Chicago warehouse)
- Customer in Los Angeles: 1 day (from LA warehouse)
- Customer in London: 1 day (from London warehouse)
- Customer in Tokyo: 1 day (from Tokyo warehouse)

A CDN does exactly this, but for digital content. Your origin server is the main warehouse. CDN edge servers are the regional fulfillment centers.

```
WITHOUT CDN:

  User (Tokyo)  --------11,000 miles-------->  Server (New York)
  User (London) ---------3,500 miles-------->  Server (New York)
  User (Sydney) --------10,000 miles-------->  Server (New York)
  User (NYC)    ----------5 miles----------->  Server (New York)

  Latency depends on distance from origin.


WITH CDN:

  User (Tokyo)  ----> Edge (Tokyo)      ~5ms
  User (London) ----> Edge (London)     ~5ms
  User (Sydney) ----> Edge (Sydney)     ~5ms
  User (NYC)    ----> Edge (New York)   ~2ms

                    +---- Edge: Tokyo
                    |
  Origin Server ----+---- Edge: London
  (New York)        |
                    +---- Edge: Sydney
                    |
                    +---- Edge: Sao Paulo
                    |
                    +---- Edge: Mumbai

  Each edge caches content from the origin.
  Users connect to the nearest edge.
```

### What a CDN Stores

CDNs primarily cache **static content** -- files that do not change between requests:

- Images (JPEG, PNG, WebP, SVG)
- CSS stylesheets
- JavaScript files
- Fonts
- Video and audio files
- PDF documents
- HTML pages (when they rarely change)

Modern CDNs can also cache **dynamic content** -- API responses, personalized pages -- with shorter TTLs and smarter invalidation.

---

## 5.2 How CDN Routing Works

When a user requests content, how does their browser know to connect to a nearby CDN edge server instead of your origin? The answer is DNS.

### DNS-Based Routing

```
CDN REQUEST FLOW (Step by Step):

1. User types "www.example.com/logo.png" in browser

2. Browser asks DNS: "What is the IP of www.example.com?"

3. DNS sees that www.example.com has a CNAME pointing to
   "d1234.cdn-provider.net"

4. CDN's DNS server receives the query. It knows the user's
   approximate location from their DNS resolver's IP address.

5. CDN DNS returns the IP of the nearest edge server.

6. Browser connects to the edge server.

7. Edge server checks: "Do I have /logo.png cached?"
   - YES (cache hit): Return it immediately
   - NO (cache miss): Fetch from origin, cache it, return it


Step-by-step:

  +--------+     +-------+     +---------+     +------+     +--------+
  | User's |     |  DNS  |     | CDN DNS |     | Edge |     | Origin |
  |Browser |     |Resolver|    | Server  |     |Server|     | Server |
  +---+----+     +---+---+     +----+----+     +--+---+     +---+----+
      |              |              |             |              |
      | 1. Resolve   |              |             |              |
      | example.com  |              |             |              |
      |------------->|              |             |              |
      |              | 2. CNAME to  |             |              |
      |              | cdn-provider |             |              |
      |              |------------->|             |              |
      |              |              |             |              |
      |              | 3. Return IP |             |              |
      |              |  of nearest  |             |              |
      |              |  edge server |             |              |
      |              |<-------------|             |              |
      |              |              |             |              |
      | 4. IP address|              |             |              |
      |<-------------|              |             |              |
      |              |              |             |              |
      | 5. Request /logo.png        |             |              |
      |-------------------------------->          |              |
      |              |              |             |              |
      |              |              |    6a. HIT: |              |
      |              |              |    Return   |              |
      |              |              |    cached   |              |
      |<---------------------------------|       |              |
      |              |              |             |              |
      |              |              |   6b. MISS: |              |
      |              |              |   Fetch from|              |
      |              |              |   origin    |              |
      |              |              |             |------------->|
      |              |              |             |<-------------|
      |              |              |   Cache it  |              |
      |              |              |   + return  |              |
      |<---------------------------------|       |              |
```

### Routing Methods

CDNs use several techniques to direct users to the optimal edge server:

**1. GeoDNS:** Routes based on the geographic location of the user's DNS resolver. Simple but not always accurate (VPN users, corporate DNS resolvers in different regions).

**2. Anycast:** Multiple edge servers share the same IP address. The internet's routing protocols (BGP) naturally direct packets to the nearest server. This is very effective and widely used by Cloudflare.

**3. Latency-based routing:** CDN measures actual latency from various locations and routes to the lowest-latency server, not just the geographically closest one.

```
ANYCAST ROUTING:

  All edge servers announce the same IP: 1.2.3.4

  User in Tokyo:
    Internet routing --> Shortest BGP path --> Edge in Tokyo

  User in London:
    Internet routing --> Shortest BGP path --> Edge in London

  Same IP address, different physical servers!
```

---

## 5.3 Push CDN vs Pull CDN

There are two fundamentally different approaches to getting content onto CDN edge servers.

### Pull CDN (Origin Pull)

The CDN pulls content from your origin server on demand, the first time it is requested.

```
PULL CDN:

  1. User requests /image.jpg from edge server
  2. Edge checks: "Do I have it?" --> NO (first request)
  3. Edge fetches /image.jpg from origin server
  4. Edge caches it and returns it to user
  5. Next user requests /image.jpg from same edge
  6. Edge checks: "Do I have it?" --> YES
  7. Edge returns cached copy (origin not contacted)

  Timeline:
  +---------+------------------------------------------+
  | Request | What Happens                             |
  +---------+------------------------------------------+
  | 1st     | Edge MISS --> Fetch from origin --> Cache |
  | 2nd     | Edge HIT  --> Return cached copy         |
  | 3rd     | Edge HIT  --> Return cached copy         |
  | ...     | Edge HIT  --> Return cached copy         |
  | TTL exp | Edge MISS --> Fetch from origin --> Cache |
  +---------+------------------------------------------+
```

**Pros:**
- Simple setup (just point DNS to CDN)
- Only requested content is cached (no wasted storage)
- No need to upload content to CDN manually

**Cons:**
- First request to each edge is slow (origin pull)
- Origin must handle pull requests from many edges
- Sudden traffic spikes can overwhelm origin

**Best for:** Most websites, APIs, and applications. This is the default for most CDN providers.

### Push CDN

You explicitly upload content to the CDN. The CDN stores it and serves it directly. The origin is only involved during uploads.

```
PUSH CDN:

  1. You upload /video.mp4 to CDN (ahead of time)
  2. CDN distributes it to edge servers
  3. User requests /video.mp4
  4. Edge already has it --> Returns immediately

  +--------+    Upload     +----------+   Replicate   +-------+
  | Origin |-------------->| CDN Core |-------------->| Edges |
  +--------+   (you push)  +----------+  (CDN handles)+-------+
                                                          |
                                                     User requests
                                                     served here
```

**Pros:**
- No cold-miss penalty (content is already on edges)
- Origin is not contacted for serving (fully offloaded)
- You control exactly what is cached

**Cons:**
- You must manage uploads and deletions
- You pay for storage on all edge servers, even for rarely accessed content
- More operational complexity

**Best for:** Large static files (videos, software downloads), content with predictable access patterns.

### Comparison

```
+----------------+------------------+------------------+
| Feature        | Pull CDN         | Push CDN         |
+----------------+------------------+------------------+
| Setup effort   | Low              | Higher           |
| First request  | Slow (origin     | Fast (already    |
|                | fetch)           | cached)          |
+----------------+------------------+------------------+
| Storage cost   | Lower (only      | Higher (all      |
|                | popular content) | uploaded content)|
+----------------+------------------+------------------+
| Origin load    | Moderate (pulls) | Minimal          |
+----------------+------------------+------------------+
| Best for       | Websites, APIs   | Video, large     |
|                |                  | file downloads   |
+----------------+------------------+------------------+
| Most providers | Default mode     | Optional feature |
+----------------+------------------+------------------+
```

---

## 5.4 Static vs Dynamic Content

### Static Content

Static content is the same for every user: images, CSS, JavaScript, fonts, videos. This is the bread and butter of CDN caching.

```
Static content: Same file for everyone

  User A requests /style.css --> Gets the same file
  User B requests /style.css --> Gets the same file
  User C requests /style.css --> Gets the same file

  Cache-Control: public, max-age=31536000
  (Cache for 1 year -- use versioned URLs to bust cache)
```

### Dynamic Content

Dynamic content varies by user, time, or context: personalized dashboards, search results, API responses.

```
Dynamic content: Different for each user

  User A requests /api/feed --> Gets User A's feed
  User B requests /api/feed --> Gets User B's feed
  User C requests /api/feed --> Gets User C's feed

  Can you cache this? Maybe, with the right strategy:
  - Cache by user (Vary: Cookie or Vary: Authorization)
  - Cache with short TTL (Cache-Control: max-age=10)
  - Cache at edge with ESI (Edge Side Includes)
```

### Edge Side Includes (ESI)

Some CDNs support ESI, which lets you cache parts of a page separately:

```
PAGE WITH ESI:

  +--------------------------------------------------+
  | Header (cached 1 day -- same for everyone)       |
  +--------------------------------------------------+
  | <esi:include src="/api/user-greeting"/>           |
  | (cached 5 min -- per user)                       |
  +--------------------------------------------------+
  | Product listing (cached 1 hour -- same for all)  |
  +--------------------------------------------------+
  | Footer (cached 1 day -- same for everyone)       |
  +--------------------------------------------------+

  The edge assembles the page from cached fragments,
  each with its own TTL and cache key.
```

---

## 5.5 Cache-Control Headers

Cache-Control headers are HTTP headers that tell the CDN (and browser) how to cache content. These are your primary tool for controlling CDN behavior.

### Key Cache-Control Directives

```
+----------------------+----------------------------------------------+
| Directive            | Meaning                                      |
+----------------------+----------------------------------------------+
| public               | Any cache (CDN, browser) can store this       |
| private              | Only the user's browser can cache (not CDN)   |
| no-cache             | Cache can store it, but must revalidate       |
|                      | with origin before serving                    |
| no-store             | Do not cache at all, anywhere                 |
| max-age=N            | Cache for N seconds                           |
| s-maxage=N           | CDN-specific max-age (overrides max-age       |
|                      | for shared caches, browser uses max-age)      |
| must-revalidate      | Once expired, must check with origin           |
| stale-while-         | Serve stale content while fetching fresh       |
|   revalidate=N       | copy in background (for N seconds)             |
| stale-if-error=N     | Serve stale content if origin returns error    |
+----------------------+----------------------------------------------+
```

### Common Cache-Control Patterns

```
STATIC ASSETS (images, CSS, JS with versioned URLs):
  Cache-Control: public, max-age=31536000, immutable
  --> Cache for 1 year. URL changes when content changes.

API RESPONSES (semi-dynamic):
  Cache-Control: public, s-maxage=60, stale-while-revalidate=300
  --> CDN caches for 60s, serves stale for 5 min while refreshing.

PRIVATE USER DATA:
  Cache-Control: private, no-cache
  --> Only browser can cache. Must revalidate every time.

SENSITIVE DATA (banking, health records):
  Cache-Control: no-store
  --> Never cache anywhere. Not on CDN, not in browser.

HTML PAGES:
  Cache-Control: public, max-age=0, must-revalidate
  --> Always check with origin. If unchanged (304), use cache.
```

### ETag and Conditional Requests

ETags let the CDN check if content has changed without downloading it again:

```
CONDITIONAL REQUEST FLOW:

  1. First request:
     Edge --> Origin: GET /page.html
     Origin --> Edge: 200 OK
                      ETag: "abc123"
                      Body: <html>...</html>

  2. Subsequent request (after max-age expires):
     Edge --> Origin: GET /page.html
                      If-None-Match: "abc123"

     Origin checks: Has /page.html changed?

     NOT changed:
       Origin --> Edge: 304 Not Modified (no body!)
       Edge uses its cached copy. Saves bandwidth.

     Changed:
       Origin --> Edge: 200 OK
                        ETag: "def456"
                        Body: <html>new content</html>
       Edge updates its cache.
```

---

## 5.6 Cache Invalidation and Purging

Sometimes you need to remove content from the CDN before its TTL expires. This is called invalidation or purging.

### Why Invalidate?

- You published an article with a typo and need to fix it immediately
- A product price changed and stale prices would cause problems
- A security vulnerability requires an immediate asset update
- A legal takedown request requires content removal

### Invalidation Methods

**1. Purge by URL:** Remove a specific URL from all edge servers.

```
PURGE BY URL:

  API Call: PURGE /images/product-42.jpg

  +--------+       +--------+       +--------+
  | Edge 1 |       | Edge 2 |       | Edge 3 |
  | Tokyo  |       | London |       | NYC    |
  +--------+       +--------+       +--------+
       |                |                |
       v                v                v
  DELETE            DELETE            DELETE
  product-42.jpg    product-42.jpg    product-42.jpg

  Next request triggers a fresh pull from origin.
```

**2. Purge by tag/key:** Group related content with a tag and purge all content with that tag at once.

```
PURGE BY TAG:

  Tag: "product-42"
  Applies to: /images/product-42.jpg
              /api/product/42
              /pages/product-42.html

  API Call: PURGE tag="product-42"
  --> All three URLs purged from all edges
```

**3. Purge everything:** Nuclear option. Removes all cached content from all edges.

**4. URL versioning:** Instead of purging, change the URL when content changes. The old URL naturally expires; the new URL is a cache miss.

```
URL VERSIONING:

  Before change: /static/style.v1.css  (cached)
  After change:  /static/style.v2.css  (new URL, cache miss)

  The old URL is never purged -- it just expires naturally.
  No purge needed! This is the most reliable strategy.
```

### Invalidation Propagation Time

Purging is not instant. It takes time to propagate across all edge servers:

```
+------------------+---------------------------+
| CDN Provider     | Typical Purge Time        |
+------------------+---------------------------+
| Cloudflare       | ~2-5 seconds (very fast)  |
| CloudFront       | ~5-60 seconds             |
| Akamai           | ~5-10 seconds             |
+------------------+---------------------------+
```

During propagation, some users may see old content while others see new content.

---

## 5.7 Major CDN Providers

### Amazon CloudFront

- Integrated with AWS ecosystem (S3, EC2, Lambda@Edge)
- 450+ edge locations worldwide
- Supports Lambda@Edge for running code at the edge
- Pay-per-use pricing (per GB transferred + per request)
- Good for: AWS-heavy architectures, video streaming

### Cloudflare

- Global anycast network with 300+ cities
- Free tier available (generous for small sites)
- Built-in DDoS protection, WAF, and DNS
- Workers (serverless at the edge) for dynamic content
- Good for: Websites of all sizes, security-focused deployments

### Akamai

- The original CDN, largest network (4,000+ edge locations)
- Enterprise-focused with advanced features
- Strong in media delivery and security
- Higher cost, longer contracts
- Good for: Large enterprises, media companies, gaming

### Comparison

```
+------------------+-----------+------------+----------+
| Feature          | CloudFront| Cloudflare | Akamai   |
+------------------+-----------+------------+----------+
| Edge locations   | 450+      | 300+ cities| 4,000+   |
| Free tier        | No*       | Yes        | No       |
| DDoS protection  | Shield    | Built-in   | Kona     |
| Edge compute     | Lambda    | Workers    | EdgeWorkers|
|                  | @Edge     |            |          |
| Pricing model    | Pay-per-  | Plans +    | Contract |
|                  | use       | pay-per-use| based    |
| Best for         | AWS users | Everyone   | Enterprise|
+------------------+-----------+------------+----------+

* AWS Free Tier includes limited CloudFront usage for 12 months
```

---

## 5.8 When to Use a CDN

### Use a CDN When:

- Your users are geographically distributed
- You serve static assets (images, CSS, JS, videos)
- You want to reduce load on your origin server
- You need DDoS protection
- You want to improve page load times globally
- You serve large files (software downloads, media)

### Skip the CDN When:

- All your users are in one region close to your server
- Your content is highly personalized and cannot be cached
- You have strict data residency requirements (content must stay in one country)
- You are in early development and latency optimization is premature
- Your traffic is very low and the added complexity is not justified

### CDN Impact on Performance

```
BEFORE CDN (origin in US-East):

  User Location    | Latency (first byte) | Page Load
  -----------------+---------------------+-----------
  New York         | 20ms                | 1.2s
  Los Angeles      | 70ms                | 2.1s
  London           | 90ms                | 2.8s
  Tokyo            | 180ms               | 4.5s
  Sydney           | 220ms               | 5.2s


AFTER CDN:

  User Location    | Latency (first byte) | Page Load
  -----------------+---------------------+-----------
  New York         | 5ms                 | 0.8s
  Los Angeles      | 8ms                 | 0.9s
  London           | 10ms                | 0.9s
  Tokyo            | 12ms                | 1.0s
  Sydney           | 15ms                | 1.1s

  Everyone gets a fast, consistent experience.
```

---

## 5.9 CDN Architecture: Full Request Flow

Here is the complete flow of a request through a CDN-enabled system:

```
COMPLETE CDN REQUEST FLOW:

  +--------+
  | User   |  1. Types www.example.com/photo.jpg
  +---+----+
      |
      | 2. DNS lookup: www.example.com
      v
  +---+------+
  | DNS      |  3. Returns CNAME: cdn.example.com
  | Resolver |  4. Resolves cdn.example.com to nearest edge IP
  +---+------+
      |
      | 5. Connect to edge server
      v
  +---+------+
  | CDN Edge |  6. Check local cache for /photo.jpg
  | Server   |
  +---+------+
      |
      +-------- HIT? ---------> 7a. Return cached photo
      |                              (fast: ~10ms)
      |
      +-------- MISS? --------> 7b. Forward request to origin
      |
      v
  +---+------+
  | Origin   |  8. Origin returns photo.jpg
  | Server   |
  +---+------+
      |
      v
  +---+------+
  | CDN Edge |  9. Cache photo.jpg locally (with TTL)
  | Server   | 10. Return photo.jpg to user
  +----------+     (slower: ~100ms, but next request is fast)


COMPLETE ARCHITECTURE:

  +--------+     +--------+     +--------+     +--------+
  |  User  |     |  CDN   |     |  Load  |     | Origin |
  |        |     |  Edge  |     |Balancer|     | Server |
  +---+----+     +---+----+     +---+----+     +---+----+
      |              |              |              |
      |  Request     |              |              |
      |------------->|              |              |
      |              |              |              |
      |         HIT? |              |              |
      |<-------------|              |              |
      |   (done!)    |              |              |
      |              |              |              |
      |        MISS? |              |              |
      |              |   Forward    |              |
      |              |------------->|              |
      |              |              |   Route to   |
      |              |              |   server     |
      |              |              |------------->|
      |              |              |              |
      |              |              |   Response   |
      |              |              |<-------------|
      |              |   Response   |              |
      |              |<-------------|              |
      |              |              |              |
      |              | Cache + send |              |
      |<-------------|              |              |
```

---

## 5.10 Advanced CDN Topics

### CDN and HTTPS

CDNs terminate TLS connections at the edge, which has two benefits:
1. Users get a faster TLS handshake (shorter round trip to nearby edge)
2. The connection between edge and origin can use a persistent, optimized connection

```
TLS WITH CDN:

  User <--TLS--> Edge (fast handshake, nearby)
                 Edge <--TLS--> Origin (persistent connection)

  Without CDN:
  User <--TLS--> Origin (slow handshake, far away)
```

### CDN for API Acceleration

Modern CDNs can accelerate API traffic even when responses are not cacheable:

- **Connection pooling:** Edge keeps persistent connections to your origin
- **TCP optimization:** Edge uses optimized TCP settings for the long-haul connection
- **Route optimization:** CDN's private backbone may be faster than the public internet
- **Compression:** Edge can compress responses (gzip, Brotli) closer to the user

### Edge Computing

Modern CDNs let you run code at the edge:

```
EDGE COMPUTING:

  Traditional:
  User --> Edge (cache only) --> Origin (all logic)

  With Edge Computing:
  User --> Edge (cache + logic) --> Origin (only when needed)

  Examples:
  - A/B testing decisions at the edge
  - URL rewriting and redirects
  - Authentication checks
  - Geolocation-based content
  - Image resizing on the fly
```

---

## Common Mistakes

1. **Not setting Cache-Control headers.** Without explicit headers, CDN behavior is unpredictable. Always set headers on your origin responses.

2. **Using the same TTL for everything.** Static assets can be cached for months; API responses may need seconds. Differentiate.

3. **Forgetting about cache busting.** If you cache CSS for 1 year but update it, users see the old version. Use versioned URLs (style.v2.css) or content hashes (style.a1b2c3.css).

4. **Caching private data on a shared CDN.** If you do not set Cache-Control: private for user-specific data, the CDN may serve one user's data to another.

5. **Ignoring the Vary header.** If your response varies by Accept-Encoding or Cookie, you must include the Vary header or the CDN may serve wrong content.

6. **Over-purging.** Frequent purges negate the benefit of caching. Use versioned URLs instead.

7. **Not monitoring CDN hit ratio.** If your CDN has a low hit ratio, you are paying for a CDN without getting much benefit. Investigate and fix.

---

## Best Practices

1. **Use versioned or hashed URLs for static assets.** This eliminates the need for purging and ensures users always get the correct version.

2. **Set long TTLs for truly static content.** Images, fonts, and versioned JS/CSS can safely be cached for 1 year.

3. **Use s-maxage to control CDN caching separately from browser caching.** This lets you set a short browser cache but a long CDN cache.

4. **Enable stale-while-revalidate.** This lets the CDN serve slightly stale content while fetching fresh content in the background, preventing latency spikes.

5. **Use a CDN for all static assets, even in development.** It catches caching bugs early.

6. **Monitor CDN hit ratio, bandwidth savings, and origin offload.** These metrics tell you if your CDN is working well.

7. **Consider edge computing for simple logic.** Authentication, redirects, and A/B testing can run at the edge, reducing origin load.

8. **Use HTTPS between CDN and origin.** Do not let the internal connection be unencrypted.

---

## Quick Summary

A CDN is a geographically distributed network of edge servers that caches content close to users, reducing latency from hundreds of milliseconds to single digits. CDNs use DNS-based routing (GeoDNS or Anycast) to direct users to the nearest edge. Pull CDNs fetch content from your origin on demand (most common); push CDNs require you to upload content in advance. Cache-Control headers govern what gets cached and for how long. Invalidation can be done via purging or URL versioning (preferred). Major providers include CloudFront (AWS integrated), Cloudflare (free tier, anycast), and Akamai (largest network, enterprise). Use a CDN whenever you have geographically distributed users and static content to serve.

---

## Key Points

- A CDN places copies of your content on servers worldwide so users connect to a nearby edge instead of a distant origin
- DNS routing (GeoDNS or Anycast) directs users to the optimal edge server
- Pull CDNs fetch content on demand (simple, most common); push CDNs require manual uploads (good for large files)
- Cache-Control headers are the primary mechanism for controlling CDN behavior
- Use versioned URLs for static assets to avoid purge-related issues
- s-maxage controls CDN caching independently from browser caching
- stale-while-revalidate prevents latency spikes during cache refreshes
- CDN hit ratio is the key metric to monitor

---

## Practice Questions

1. Your website serves users globally, but you notice that users in Asia consistently experience 3-4 second load times while US users see 0.5 seconds. Explain how a CDN would help and what steps you would take to implement it.

2. You have an e-commerce site where product images change occasionally but product prices change multiple times per day. How would you configure CDN caching differently for images vs API responses? Include specific Cache-Control headers.

3. A developer on your team sets Cache-Control: public, max-age=86400 on an API endpoint that returns user-specific data. What is the security risk, and how would you fix it?

4. Compare Anycast routing and GeoDNS routing for a CDN. What are the trade-offs? When might one be preferred over the other?

5. Your CDN hit ratio is only 40%. List three possible causes and how you would investigate and improve it.

---

## Exercises

**Exercise 1: CDN Configuration**
You are building a news website with these content types: (a) article text that updates after publication, (b) article images that never change, (c) the homepage that changes every few minutes, (d) user comment sections. For each, decide: should it be cached on the CDN? If yes, write the Cache-Control header you would use. If no, explain why.

**Exercise 2: Draw the Request Flow**
Draw a detailed ASCII diagram showing what happens when a user in Sydney requests a page from your origin server in London. Include DNS resolution, CDN edge lookup (miss then hit), origin fetch, and caching. Show the difference in latency for the first request vs subsequent requests.

**Exercise 3: CDN Cost Analysis**
Your site serves 10 million image requests per day. Average image size is 200KB. Without a CDN, all traffic hits your origin server. With a CDN at 90% hit ratio, only 10% of requests reach origin. Calculate: (a) daily bandwidth saved on origin, (b) if your cloud provider charges $0.09/GB for origin bandwidth, how much do you save per month?

---

## What Is Next?

Now that you understand how CDNs cache and deliver content at the edge, it is time to dive into the backbone of any system: the database. In Chapter 6, you will explore SQL and NoSQL databases -- their strengths, weaknesses, and when to use each. Understanding databases is essential because nearly every system design decision revolves around how data is stored, queried, and scaled.
