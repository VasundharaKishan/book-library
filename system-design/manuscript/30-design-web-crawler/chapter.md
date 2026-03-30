# Chapter 30: Designing a Web Crawler

Every time you type a query into Google, Bing, or DuckDuckGo, the results you see were discovered by a web crawler -- a tireless piece of software that visits billions of web pages, downloads their content, and follows every link it finds. Without crawlers, search engines would have nothing to search. But crawling the entire web is one of the hardest distributed systems problems in existence: you must be fast enough to keep up with a constantly changing internet, polite enough not to overwhelm the websites you visit, and smart enough to avoid traps, duplicates, and irrelevant content.

In this chapter we will design a web crawler that can handle billions of pages. Along the way we will tackle URL frontiers, politeness policies, duplicate detection with bloom filters, robots.txt compliance, and distributed crawling architecture. This is a favorite system design interview question because it blends networking, data structures, distributed systems, and practical engineering trade-offs into a single problem.

---

## What You Will Learn

- How a web crawler discovers and downloads pages at massive scale.
- The architecture of the URL frontier and why a simple queue is not enough.
- How bloom filters provide space-efficient duplicate detection.
- Why politeness and robots.txt compliance are non-negotiable.
- BFS vs DFS traversal strategies and their trade-offs.
- How to distribute crawling across hundreds of machines.
- Techniques to detect and avoid crawler traps.

---

## Why This Chapter Matters

Web crawlers are not just for search engines. Companies use crawlers for price monitoring, content aggregation, SEO auditing, machine learning dataset collection, and legal compliance checking. Understanding crawler design teaches you about rate limiting, distributed coordination, deduplication, and working with unreliable external systems -- skills that transfer to dozens of other system design problems.

In interviews, this question tests whether you can think about systems that interact with the outside world at scale, where you do not control the servers you talk to.

---

## 30.1 Understanding the Problem

A web crawler starts with a set of URLs, downloads each page, extracts new URLs from the page content, and adds those URLs to the list of pages to visit. Repeat this process billions of times, and you have crawled the web.

Sounds simple, right? The devil is in the details.

### The Scale of the Web

| Metric | Approximate Value |
|--------|-------------------|
| Indexed pages (Google) | 50+ billion |
| New pages created daily | hundreds of millions |
| Average page size | ~2 MB (with images), ~100 KB (HTML only) |
| Unique domains | 200+ million active |

A crawler must download, parse, and index this content while being a good citizen of the internet.

---

## 30.2 Requirements

### Functional Requirements

| # | Requirement | Description |
|---|-------------|-------------|
| F1 | **Crawl web pages** | Given seed URLs, discover and download web pages by following hyperlinks. |
| F2 | **Extract content** | Parse HTML to extract text, metadata, and outgoing links. |
| F3 | **Respect robots.txt** | Honor each domain's crawling rules. |
| F4 | **Detect duplicates** | Avoid downloading the same page twice. |
| F5 | **Store content** | Save downloaded pages for indexing or processing. |
| F6 | **Freshness** | Re-crawl pages periodically to keep content up to date. |

### Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NF1 | **Scalability** | Crawl 1 billion pages per day. |
| NF2 | **Politeness** | Never overwhelm any single domain. |
| NF3 | **Robustness** | Handle malformed HTML, timeouts, and server errors gracefully. |
| NF4 | **Extensibility** | Easy to add new content types (images, PDFs, videos). |
| NF5 | **Trap avoidance** | Detect and escape infinite URL loops and spider traps. |

---

## 30.3 Back-of-the-Envelope Estimation

### Traffic

| Metric | Calculation | Value |
|--------|-------------|-------|
| Pages per day | Given | 1 billion |
| Pages per second | 1B / 86,400 | ~11,600 pages/s |
| Average HTML size | Estimated | 100 KB |
| Bandwidth (download) | 11,600 x 100 KB | ~1.16 GB/s |

### Storage

| Metric | Calculation | Value |
|--------|-------------|-------|
| Raw HTML per day | 1B x 100 KB | 100 TB/day |
| Compressed (5:1) | 100 TB / 5 | ~20 TB/day |
| Metadata per page | ~500 bytes | 500 GB/day |

### DNS Lookups

Every URL requires a DNS resolution. At 11,600 pages/s, we need a local DNS cache to avoid overwhelming public DNS servers.

---

## 30.4 High-Level Architecture

Here is the big picture of a web crawler:

```
+----------+     +--------------+     +--------------+     +----------------+
|  Seed    |---->|  URL         |---->|  DNS         |---->|  HTML           |
|  URLs    |     |  Frontier    |     |  Resolver    |     |  Downloader     |
+----------+     +--------------+     +--------------+     +----------------+
                       ^                                          |
                       |                                          v
                 +-----------+     +---------------+     +----------------+
                 |  URL      |<----|  Content      |<----|  Content       |
                 |  Filter   |     |  Extractor    |     |  Parser        |
                 +-----------+     +---------------+     +----------------+
                       |                                          |
                       v                                          v
                 +-----------+                            +----------------+
                 |  Duplicate|                            |  Content       |
                 |  Detector |                            |  Storage       |
                 |  (Bloom)  |                            |  (S3/HDFS)     |
                 +-----------+                            +----------------+
```

### Component Walkthrough

**1. Seed URLs** -- The starting points. These are a curated list of high-quality, diverse URLs that cover many domains and topics. Examples include top websites from Alexa rankings, government portals, and university pages.

**2. URL Frontier** -- The heart of the crawler. This is not a simple FIFO queue. It is a priority queue combined with a politeness scheduler (more on this below).

**3. DNS Resolver** -- Translates domain names to IP addresses. We run our own caching DNS resolver to avoid hitting public DNS too hard.

**4. HTML Downloader** -- Fetches the page content via HTTP/HTTPS. Handles redirects, timeouts, retries, and different content types.

**5. Content Parser** -- Validates and cleans the HTML. Rejects malformed or binary content.

**6. Content Extractor** -- Pulls out the useful data: page text, title, metadata, and most importantly, outgoing links.

**7. URL Filter** -- Removes unwanted URLs: different file types (.zip, .exe), blacklisted domains, URLs that are too long, etc.

**8. Duplicate Detector** -- Uses a bloom filter (and optionally a URL database) to check if we have already seen or crawled this URL.

**9. Content Storage** -- Stores the downloaded HTML and extracted data in a distributed file system (HDFS, S3) for later indexing.

---

## 30.5 Deep Dive: The URL Frontier

The URL frontier is the most interesting data structure in a web crawler. It serves two purposes that conflict with each other:

1. **Prioritization** -- Important pages should be crawled first.
2. **Politeness** -- We must not hit the same domain too frequently.

### Architecture of the URL Frontier

```
                    +-------------------+
                    |  Incoming URLs    |
                    +-------------------+
                            |
                            v
                    +-------------------+
                    |  Prioritizer      |
                    |  (assigns         |
                    |   priority score) |
                    +-------------------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
        +---------+   +---------+   +---------+
        | Queue 1 |   | Queue 2 |   | Queue 3 |
        | (High)  |   | (Medium)|   | (Low)   |
        +---------+   +---------+   +---------+
              |             |             |
              +-------------+-------------+
                            |
                            v
                    +-------------------+
                    |  Queue Selector   |
                    |  (weighted random)|
                    +-------------------+
                            |
                            v
                    +-------------------+
                    |  Politeness       |
                    |  Router           |
                    +-------------------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
        +---------+   +---------+   +---------+
        | Domain  |   | Domain  |   | Domain  |
        | Queue A |   | Queue B |   | Queue C |
        +---------+   +---------+   +---------+
              |             |             |
              v             v             v
        (one worker per domain queue)
```

### Front Queues (Priority)

The front queues handle prioritization. Each URL gets a priority score based on:

- **PageRank or similar metric** -- How many other pages link to this URL?
- **Update frequency** -- Pages that change often (news sites) get higher priority.
- **Depth from seed** -- Pages closer to seed URLs tend to be more important.
- **Domain authority** -- Well-known domains get priority.

The queue selector picks from higher-priority queues more often using a weighted random or round-robin with bias.

### Back Queues (Politeness)

The back queues ensure politeness. Each back queue is dedicated to a single domain (or host). A URL for `example.com` always goes to the same back queue. Each back queue has its own worker thread, and that worker enforces a delay between requests to the same domain.

```
Domain Queue for example.com:
  - Last request: 10:00:05.000
  - Minimum delay: 2 seconds
  - Next allowed request: 10:00:07.000
  - Queue: [/page1, /page2, /page3, ...]
```

This guarantees we never send more than one request every N seconds to any single domain.

---

## 30.6 Deep Dive: DNS Resolution

DNS resolution is a hidden bottleneck. Each page requires a DNS lookup, and at 11,600 pages/s, we cannot afford the 10-100ms latency of a public DNS query for every request.

### Solution: Local DNS Cache

```
+----------------+     +------------------+     +------------------+
|  Crawler       |---->|  Local DNS Cache |---->|  Public DNS      |
|  Worker        |     |  (in-memory,     |     |  (Google 8.8.8.8)|
|                |     |   TTL-aware)     |     |                  |
+----------------+     +------------------+     +------------------+
```

- Cache DNS results in memory with TTL (time-to-live) awareness.
- Pre-fetch DNS for URLs in the frontier before they are needed.
- Run our own recursive DNS resolver for control and performance.
- Typical DNS cache hit rate: 90%+ because we crawl many pages per domain.

---

## 30.7 Deep Dive: Duplicate Detection with Bloom Filters

With billions of URLs, we need a space-efficient way to check "have I seen this URL before?" A hash set would work but requires too much memory.

### What Is a Bloom Filter?

A bloom filter is a probabilistic data structure that can tell you:
- **Definitely not in the set** -- 100% accurate.
- **Probably in the set** -- Small chance of false positive.

It never has false negatives. If the bloom filter says "not seen," the URL is definitely new.

### How It Works

```
URL: "https://example.com/page1"
         |
         v
  +------+------+------+
  | Hash |  Hash|  Hash|   (k=3 hash functions)
  |  h1  |  h2  |  h3  |
  +------+------+------+
     |       |       |
     v       v       v
  Bit Array (m bits):
  [0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]
           ^       ^                    ^
         h1=2    h2=4                 h3=11

  To check: if ALL k positions are 1, "probably seen."
  If ANY position is 0, "definitely not seen."
```

### Sizing the Bloom Filter

For 1 billion URLs with a 1% false positive rate:

| Parameter | Value |
|-----------|-------|
| n (expected items) | 1 billion |
| p (false positive rate) | 1% |
| m (bits needed) | ~9.6 billion bits = ~1.2 GB |
| k (hash functions) | 7 |

Only 1.2 GB of memory to track a billion URLs. A hash set would need 50+ GB.

### Content-Based Deduplication

URLs can be different but point to the same content (e.g., with different query parameters or session IDs). For content deduplication, compute a fingerprint (e.g., SimHash or MinHash) of the page content and check it against a separate bloom filter or database.

---

## 30.8 Deep Dive: Robots.txt and Politeness

### Robots.txt

The `robots.txt` file at the root of every website tells crawlers what they are allowed to crawl:

```
# Example robots.txt for example.com
User-agent: *
Disallow: /admin/
Disallow: /private/
Crawl-delay: 2

User-agent: MyCustomBot
Allow: /public/
Disallow: /
```

**Rules our crawler must follow:**

1. Before crawling any page on a domain, fetch and parse its `robots.txt`.
2. Cache the `robots.txt` for each domain (refresh every 24 hours).
3. Respect `Disallow` directives -- never crawl forbidden paths.
4. Respect `Crawl-delay` -- wait at least this many seconds between requests.
5. Identify ourselves with a proper `User-Agent` header.

### Politeness Beyond Robots.txt

Even if `robots.txt` allows aggressive crawling, a well-behaved crawler should:

| Rule | Implementation |
|------|----------------|
| Rate limit per domain | Max 1 request per 1-2 seconds per domain |
| Rate limit per IP | Some domains share IPs; limit per IP too |
| Respect HTTP 429 | Back off when server says "too many requests" |
| Respect HTTP 503 | Server is overloaded; retry later with exponential backoff |
| Off-peak crawling | For small sites, crawl during their off-peak hours |
| Connection reuse | Use HTTP keep-alive to reduce connection overhead |

---

## 30.9 BFS vs DFS Traversal

### BFS (Breadth-First Search)

BFS explores all links at the current depth before going deeper. This is the standard approach for web crawling.

```
Seed URL (depth 0)
    |
    +-- Link A (depth 1)
    |       |
    |       +-- Link D (depth 2)
    |       +-- Link E (depth 2)
    |
    +-- Link B (depth 1)
    |       |
    |       +-- Link F (depth 2)
    |
    +-- Link C (depth 1)

BFS order: Seed -> A -> B -> C -> D -> E -> F
```

**Advantages:**
- Discovers important pages (close to seeds) first.
- Natural fit for level-by-level crawling.
- Less likely to get trapped in deep link chains.

**Disadvantages:**
- Requires large memory for the frontier queue.
- May hit many domains simultaneously at shallow depths.

### DFS (Depth-First Search)

DFS follows one link chain as deep as possible before backtracking.

```
DFS order: Seed -> A -> D -> E -> B -> F -> C
```

**Advantages:**
- Uses less memory (only needs the current path stack).
- Good for focused crawling of a single domain.

**Disadvantages:**
- Can get trapped in deep link chains or spider traps.
- May miss important pages on other branches.
- Not suitable for general-purpose web crawling.

**Verdict:** Use BFS for general web crawling. Use DFS only for focused, single-domain crawls with a depth limit.

---

## 30.10 Crawler Traps

A crawler trap is a set of URLs that cause the crawler to loop infinitely or generate an unlimited number of pages.

### Common Traps

| Trap Type | Example | Solution |
|-----------|---------|----------|
| Infinite query strings | `/page?id=1`, `/page?id=2`, ... forever | Limit unique URLs per domain |
| Calendar traps | `/calendar/2024/01`, `/calendar/2024/02`, ... | Detect date patterns, set depth limits |
| Session ID URLs | `/page?sid=abc123` (new session each visit) | Strip known session parameters |
| Soft 404s | Server returns 200 OK with "page not found" content | Content similarity detection |
| Redirect loops | A -> B -> C -> A | Track redirect chains, limit to 5 hops |
| Dynamic content | JavaScript generates infinite links | Set per-domain URL budget |

### Anti-Trap Strategies

1. **URL budget per domain** -- Allow at most N URLs (e.g., 10,000) per domain.
2. **Depth limit** -- Stop following links beyond depth D (e.g., 15) from seed URLs.
3. **URL pattern detection** -- If URLs from a domain follow a repetitive pattern with only a counter changing, flag it.
4. **Manual blacklist** -- Maintain a list of known trap domains.
5. **Content fingerprinting** -- If many pages from the same domain have nearly identical content, slow down or stop crawling that domain.

---

## 30.11 Distributed Architecture

A single machine cannot crawl a billion pages per day. We need a distributed system.

```
                        +-------------------+
                        |  Coordinator      |
                        |  (assigns domains |
                        |   to workers)     |
                        +-------------------+
                                |
            +-------------------+-------------------+
            |                   |                   |
            v                   v                   v
    +---------------+   +---------------+   +---------------+
    |  Crawler      |   |  Crawler      |   |  Crawler      |
    |  Worker 1     |   |  Worker 2     |   |  Worker N     |
    |               |   |               |   |               |
    | - URL Frontier|   | - URL Frontier|   | - URL Frontier|
    | - DNS Cache   |   | - DNS Cache   |   | - DNS Cache   |
    | - Downloader  |   | - Downloader  |   | - Downloader  |
    | - Parser      |   | - Parser      |   | - Parser      |
    +---------------+   +---------------+   +---------------+
            |                   |                   |
            +-------------------+-------------------+
                                |
                                v
                    +------------------------+
                    |  Shared Storage         |
                    |  (HDFS / S3)            |
                    +------------------------+
                    |  Shared Bloom Filter    |
                    |  (Redis / distributed)  |
                    +------------------------+
                    |  URL Database           |
                    |  (for persistence)      |
                    +------------------------+
```

### Partitioning Strategy

The most common approach is **domain-based partitioning**: each worker is responsible for a set of domains. This has several advantages:

1. **Natural politeness** -- Each worker manages rate limiting for its own domains.
2. **DNS cache efficiency** -- Domains stay on the same worker, so DNS results are cached locally.
3. **robots.txt caching** -- Each worker caches robots.txt for its domains.
4. **No coordination overhead for politeness** -- Workers do not need to coordinate rate limits.

Use consistent hashing to assign domains to workers. When a worker discovers a URL for a domain owned by another worker, it sends the URL to that worker via a message queue.

### Fault Tolerance

| Failure | Recovery |
|---------|----------|
| Worker crash | Reassign its domains to other workers. Persist frontier to disk periodically. |
| DNS resolver down | Fall back to public DNS servers. |
| Storage unavailable | Buffer downloaded pages locally, flush when storage recovers. |
| Network partition | Workers continue crawling their local frontier independently. |

---

## 30.12 Handling Freshness

The web is constantly changing. A crawler must re-visit pages to keep its index fresh.

### Re-Crawl Strategies

| Strategy | How It Works | Pros | Cons |
|----------|-------------|------|------|
| Uniform | Re-crawl all pages every N days | Simple | Wastes resources on static pages |
| Frequency-based | Crawl pages that change often more frequently | Efficient | Requires change history |
| Priority-based | Re-crawl important pages more often | Good use of budget | Need a quality signal |
| HTTP headers | Use `Last-Modified` and `ETag` headers | Minimal bandwidth for unchanged pages | Not all servers support them |

### Conditional Requests

```
GET /page HTTP/1.1
Host: example.com
If-Modified-Since: Mon, 01 Jan 2024 00:00:00 GMT
If-None-Match: "abc123"

Response (if unchanged):
HTTP/1.1 304 Not Modified
(no body -- saves bandwidth)
```

Using conditional requests, we can check if a page has changed without downloading the full content.

---

## 30.13 Content Processing Pipeline

Once a page is downloaded, it goes through a processing pipeline:

```
+----------------+     +----------------+     +----------------+
|  Raw HTML      |---->|  Encoding      |---->|  HTML           |
|  Download      |     |  Detection     |     |  Cleaning       |
+----------------+     +----------------+     +----------------+
                                                      |
                                                      v
+----------------+     +----------------+     +----------------+
|  Store in      |<----|  Content       |<----|  Link           |
|  Index         |     |  Fingerprint   |     |  Extraction     |
+----------------+     +----------------+     +----------------+
```

1. **Encoding Detection** -- Determine character encoding (UTF-8, ISO-8859-1, etc.).
2. **HTML Cleaning** -- Remove scripts, styles, ads, and boilerplate. Extract the main content.
3. **Link Extraction** -- Find all `<a href>` tags. Resolve relative URLs to absolute URLs.
4. **Content Fingerprinting** -- Compute SimHash or MinHash to detect near-duplicate pages.
5. **Indexing** -- Store the cleaned content and metadata for the search engine or downstream processing.

---

## 30.14 Putting It All Together

Here is the complete flow for crawling a single page:

```
1. URL Frontier picks next URL (respecting priority and politeness)
        |
2. Check robots.txt cache (fetch if missing or expired)
        |
3. Is this path allowed? --NO--> Discard URL
        |YES
4. Resolve DNS (check local cache first)
        |
5. Download page via HTTP (with timeout, retries)
        |
6. Is it HTML? --NO--> Store raw or discard based on config
        |YES
7. Parse HTML, extract text and links
        |
8. Compute content fingerprint
        |
9. Is content a duplicate? --YES--> Discard
        |NO
10. Store content in distributed storage
        |
11. For each extracted link:
    a. Normalize URL (lowercase host, remove fragment, etc.)
    b. Check URL bloom filter
    c. Already seen? --YES--> Skip
    d. Pass URL filter (extension, blacklist, length)
    e. Add to URL frontier with priority score
```

---

## Common Mistakes

1. **Ignoring robots.txt.** This is not optional. Ignoring it can get your crawler banned and your company sued.

2. **No politeness controls.** Hammering a small website with 100 requests per second will take it down. You are responsible for the damage.

3. **Using a simple FIFO queue as the frontier.** Without priority and politeness, you will crawl unimportant pages and overwhelm popular domains.

4. **Not handling DNS efficiently.** DNS resolution becomes the bottleneck if you do not cache aggressively.

5. **Ignoring crawler traps.** Without depth limits and URL budgets, your crawler will get stuck in infinite loops and waste all its resources on a single domain.

6. **Storing all raw HTML forever.** Without compression and retention policies, storage costs explode.

7. **Not normalizing URLs.** `http://Example.COM/Page` and `http://example.com/page` are the same URL. Without normalization, you crawl duplicates.

---

## Best Practices

1. **Identify your crawler.** Set a descriptive `User-Agent` header and provide a contact URL or email.

2. **Implement exponential backoff.** When a server returns errors, back off exponentially rather than retrying immediately.

3. **Normalize URLs consistently.** Lowercase the scheme and host, remove default ports, remove fragments, sort query parameters.

4. **Use conditional requests.** `If-Modified-Since` and `If-None-Match` headers save bandwidth on re-crawls.

5. **Monitor everything.** Track pages per second, error rates per domain, bloom filter false positive rate, DNS cache hit rate, and frontier size.

6. **Design for extensibility.** Use a plugin architecture so you can easily add support for new content types (PDF, images, JavaScript-rendered pages).

7. **Persist the frontier.** If a worker crashes, you do not want to lose millions of URLs. Write the frontier to disk periodically.

---

## Quick Summary

A web crawler starts from seed URLs, uses a URL frontier (priority + politeness queues) to decide what to crawl next, downloads pages, extracts links, and adds new URLs to the frontier. Bloom filters provide space-efficient duplicate detection. Robots.txt and rate limiting ensure politeness. The system is distributed by partitioning domains across workers. BFS is preferred over DFS for general crawling. Trap avoidance requires depth limits, URL budgets, and pattern detection. Freshness is maintained through re-crawling strategies and conditional HTTP requests.

---

## Key Points

- The URL frontier is a two-tier system: front queues for priority, back queues for per-domain politeness.
- Bloom filters use ~1.2 GB to track 1 billion URLs with a 1% false positive rate.
- Robots.txt must be fetched, cached, and respected for every domain.
- Domain-based partitioning provides natural politeness isolation in distributed crawling.
- BFS is the default traversal strategy; DFS is only for focused single-domain crawls.
- Crawler traps are real and dangerous. Always set depth limits and URL budgets per domain.
- Conditional HTTP requests save bandwidth when re-crawling pages for freshness.
- URL normalization prevents duplicate downloads of the same page under different URL formats.

---

## Practice Questions

1. A website has no `robots.txt` file. Does this mean you can crawl everything on it without limits? What should your crawler do?

2. Your bloom filter has a 1% false positive rate. This means 1% of new URLs are incorrectly identified as "already seen" and skipped. How would you reduce the impact of false positives on crawl coverage?

3. You discover that 80% of your crawler's time is spent on DNS lookups. What three changes would you make to fix this?

4. A domain generates URLs like `/products?page=1`, `/products?page=2`, all the way to `/products?page=999999`. Your crawler is stuck crawling this one domain. How do you detect and handle this situation?

5. Your crawler needs to handle JavaScript-rendered pages (single-page applications where content loads dynamically). How would you modify the architecture to support this?

---

## Exercises

**Exercise 1: Design a Politeness Module**

Design the politeness component of a web crawler. Specify the data structures, the algorithm for deciding when a domain can be crawled next, and how you handle `Crawl-delay` directives from robots.txt. Include pseudocode for the `getNextURL()` function.

**Exercise 2: Bloom Filter Sizing**

You need to crawl 10 billion unique URLs over the lifetime of your crawler. Calculate the optimal bloom filter size (in GB) for false positive rates of 0.1%, 1%, and 5%. How many hash functions does each configuration need? What happens to memory usage if you need to support 50 billion URLs?

**Exercise 3: Freshness Strategy**

Design a re-crawl scheduler for a news aggregation crawler. News sites update every few minutes, blogs update weekly, and corporate pages update monthly. Describe your priority scheme, how you detect update frequency, and how you allocate your crawl budget (10 million pages per day) across these categories.

---

## What Is Next?

You now understand how to design a system that interacts with the entire internet at scale. In the next chapter, we will step back from specific designs and focus on estimation math -- the back-of-the-envelope calculations that let you quickly reason about scale, storage, bandwidth, and capacity in any system design interview.
