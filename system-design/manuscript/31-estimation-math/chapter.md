# Chapter 31: Estimation Math for System Design

Every system design interview begins with the same unspoken question: "Does this person understand scale?" Before you draw a single box on the whiteboard, you need to estimate how much traffic, storage, and bandwidth your system will handle. These back-of-the-envelope calculations are not about getting exact numbers -- they are about proving you can reason about whether you need one server or a thousand, one gigabyte or one petabyte, one request per second or one million.

In this chapter, we will build your estimation toolkit from the ground up. We will cover the essential numbers every engineer should have memorized, walk through the math step by step, and practice with real-world worked examples for Instagram, Twitter, and YouTube.

---

## What You Will Learn

- Powers of 2 and how they map to real-world storage and traffic numbers.
- Latency numbers every engineer should know by heart.
- How to estimate QPS (queries per second) from DAU (daily active users).
- How to estimate storage requirements for any system.
- How to estimate bandwidth needs.
- Step-by-step worked examples for Instagram, Twitter, and YouTube.

---

## Why This Chapter Matters

Estimation math is the foundation of every system design discussion. When an interviewer asks you to "design Instagram," they want to see that you think about scale before you start drawing architecture diagrams. A candidate who can quickly say "we need about 50,000 QPS for reads and 500 QPS for writes, so reads dominate and we need caching" immediately establishes credibility.

More importantly, estimation math prevents you from over-engineering or under-engineering your design. If your system handles 100 requests per second, you do not need Kafka and a distributed database. If it handles 1 million requests per second, a single PostgreSQL instance will not cut it.

---

## 31.1 Powers of 2 Reference Table

Every estimation starts with understanding data sizes. Memorize this table.

```
+-------+---------------------+-----------------------+
| Power |  Exact Value        |  Approximate Size     |
+-------+---------------------+-----------------------+
| 2^10  |  1,024              |  1 Thousand     (1 KB)|
| 2^20  |  1,048,576          |  1 Million      (1 MB)|
| 2^30  |  1,073,741,824      |  1 Billion      (1 GB)|
| 2^40  |  1,099,511,627,776  |  1 Trillion     (1 TB)|
| 2^50  |  ~1.13 x 10^15      |  1 Quadrillion  (1 PB)|
+-------+---------------------+-----------------------+
```

### Common Data Units

| Unit | Power of 2 | Bytes | Everyday Analogy |
|------|-----------|-------|-----------------|
| 1 Byte | 2^0 | 1 | A single character |
| 1 KB (Kilobyte) | 2^10 | ~1,000 | A short email |
| 1 MB (Megabyte) | 2^20 | ~1,000,000 | A high-res photo |
| 1 GB (Gigabyte) | 2^30 | ~1,000,000,000 | A movie (SD quality) |
| 1 TB (Terabyte) | 2^40 | ~10^12 | 500 hours of video |
| 1 PB (Petabyte) | 2^50 | ~10^15 | All US academic libraries |

### Quick Conversion Tricks

- **1 million seconds** = ~11.6 days
- **1 billion seconds** = ~31.7 years
- **Seconds in a day** = 86,400 (~10^5, use 100,000 for estimation)
- **Seconds in a month** = ~2.6 million (~2.5 x 10^6)
- **Seconds in a year** = ~31.5 million (~3 x 10^7)

---

## 31.2 Latency Numbers Every Engineer Should Know

These numbers help you understand where time goes in your system. They were originally compiled by Jeff Dean at Google and remain directionally correct even as hardware evolves.

```
+---------------------------------------------+----------------+
| Operation                                   | Latency        |
+---------------------------------------------+----------------+
| L1 cache reference                          |       1 ns     |
| L2 cache reference                          |       4 ns     |
| Branch mispredict                           |       5 ns     |
| Mutex lock/unlock                           |      25 ns     |
| Main memory (RAM) reference                 |     100 ns     |
| Compress 1 KB with Snappy                   |   3,000 ns     |
|                                             |     = 3 us     |
| Send 1 KB over 1 Gbps network              |  10,000 ns     |
|                                             |    = 10 us     |
| SSD random read                             | 100,000 ns     |
|                                             |   = 100 us     |
| Read 1 MB sequentially from memory          | 250,000 ns     |
|                                             |   = 250 us     |
| Round trip within same datacenter           | 500,000 ns     |
|                                             |   = 500 us     |
| Read 1 MB sequentially from SSD             |   1,000,000 ns |
|                                             |     = 1 ms     |
| HDD seek                                   |  10,000,000 ns |
|                                             |    = 10 ms     |
| Read 1 MB sequentially from HDD            |  20,000,000 ns |
|                                             |    = 20 ms     |
| Send 1 MB over 1 Gbps network              |  10,000,000 ns |
|                                             |    = 10 ms     |
| Round trip US East <-> US West              |  40,000,000 ns |
|                                             |    = 40 ms     |
| Round trip US <-> Europe                    | 100,000,000 ns |
|                                             |   = 100 ms    |
+---------------------------------------------+----------------+
```

### Key Takeaways from These Numbers

```
Latency Scale (logarithmic):

1 ns    |==  L1 cache
10 ns   |====  L2 cache, mutex
100 ns  |======  RAM
1 us    |========
10 us   |==========  Network send 1KB
100 us  |============  SSD random read
1 ms    |==============  SSD sequential 1MB
10 ms   |================  HDD seek, network 1MB
100 ms  |==================  Cross-continent round trip
```

1. **Memory is 1000x faster than SSD.** RAM access is 100 ns; SSD random read is 100 us.
2. **SSD is 100x faster than HDD.** SSD random read is 100 us; HDD seek is 10 ms.
3. **Network within a datacenter is fast.** A round trip is about 500 us (0.5 ms).
4. **Cross-continent adds real latency.** US East to West is ~40 ms; US to Europe is ~100 ms.
5. **Compression is cheap.** Compressing 1 KB takes only 3 us. Almost always worth it for network transfers.
6. **Sequential reads are much faster than random reads.** Design your data access patterns accordingly.

---

## 31.3 Estimating QPS from DAU

QPS (Queries Per Second) is the most fundamental capacity metric. Here is the formula:

```
QPS = DAU x (average queries per user per day) / seconds per day

Where:
  DAU = Daily Active Users
  Seconds per day = 86,400 (round to 100,000 for easy math)
```

### Step-by-Step Process

1. **Start with DAU.** This is usually given or you estimate it.
2. **Estimate actions per user per day.** How many times does a user read/write?
3. **Divide by 86,400** (or use 100,000 for round numbers).
4. **Calculate peak QPS.** Multiply average QPS by 2x to 5x for peak hours.
5. **Separate reads and writes.** Most systems are read-heavy (10:1 to 100:1 ratio).

### Example: Basic QPS Calculation

```
Given:
  DAU = 10 million
  Average reads per user per day = 20
  Average writes per user per day = 2

Read QPS:
  = 10,000,000 x 20 / 86,400
  = 200,000,000 / 86,400
  = ~2,300 reads/second

Write QPS:
  = 10,000,000 x 2 / 86,400
  = 20,000,000 / 86,400
  = ~230 writes/second

Peak QPS (assume 3x average):
  Peak reads  = 2,300 x 3 = ~7,000 reads/second
  Peak writes = 230 x 3   = ~700 writes/second
```

---

## 31.4 Estimating Storage

Storage estimation follows a simple pattern:

```
Daily storage = (number of new items per day) x (size per item)
Yearly storage = daily storage x 365
N-year storage = yearly storage x N
```

### Estimating Item Size

Break down each item into its components:

```
Example: A social media post

  Field             | Size
  ------------------|--------
  post_id           | 8 bytes (int64)
  user_id           | 8 bytes
  text              | 280 bytes (max)
  timestamp         | 8 bytes
  likes_count       | 4 bytes
  comments_count    | 4 bytes
  media_url         | 256 bytes
  ------------------|--------
  Total per post    | ~568 bytes
  Round up to       | ~600 bytes (for overhead)
```

Always round up. Real storage includes indexes, replication, and overhead.

---

## 31.5 Estimating Bandwidth

Bandwidth is about data flowing in and out of your system per second.

```
Incoming bandwidth = Write QPS x average write size
Outgoing bandwidth = Read QPS x average response size
```

### Example

```
Given:
  Write QPS = 230 writes/second
  Average write size = 10 KB (includes image thumbnail)
  Read QPS = 2,300 reads/second
  Average response size = 50 KB (includes images)

Incoming bandwidth:
  = 230 x 10 KB
  = 2,300 KB/s
  = ~2.3 MB/s

Outgoing bandwidth:
  = 2,300 x 50 KB
  = 115,000 KB/s
  = ~115 MB/s
  = ~920 Mbps
```

At ~1 Gbps outgoing, you need multiple servers behind a load balancer to serve this traffic.

---

## 31.6 Worked Example: Estimate Storage for Instagram

Let us estimate how much storage Instagram needs for photos.

### Assumptions

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| DAU | 500 million | Instagram's approximate DAU |
| % of users who post daily | 10% | Most users consume, few create |
| Photos posted per active poster | 1.5 | Average, including stories |
| Average photo size (compressed) | 1.5 MB | After server-side compression |
| Number of size variants stored | 4 | Original + 3 thumbnails |
| Average variant size | 500 KB | Thumbnails are smaller |

### Calculation

```
Step 1: Photos per day
  = DAU x posting_rate x photos_per_poster
  = 500,000,000 x 0.10 x 1.5
  = 75,000,000 photos/day (75 million)

Step 2: Storage per photo (all variants)
  = original + (3 thumbnails x average variant size)
  = 1.5 MB + (3 x 500 KB)
  = 1.5 MB + 1.5 MB
  = 3 MB per photo

Step 3: Daily photo storage
  = 75,000,000 x 3 MB
  = 225,000,000 MB
  = 225 TB/day

Step 4: Yearly photo storage
  = 225 TB x 365
  = ~82 PB/year

Step 5: With replication (3x for durability)
  = 82 PB x 3
  = ~246 PB/year
```

### Summary

```
+-------------------------+-------------------+
| Metric                  | Estimate          |
+-------------------------+-------------------+
| Photos per day          | 75 million        |
| Daily photo storage     | 225 TB            |
| Yearly photo storage    | ~82 PB            |
| With 3x replication     | ~246 PB/year      |
+-------------------------+-------------------+
```

This explains why Instagram runs on massive distributed object storage systems, not traditional databases.

---

## 31.7 Worked Example: Estimate QPS for Twitter

Let us estimate the QPS for Twitter's home timeline feature.

### Assumptions

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| DAU | 250 million | Twitter's approximate DAU |
| Timeline refreshes per user per day | 10 | Open app, scroll, refresh |
| Tweets viewed per refresh | 20 | Average scroll session |
| New tweets posted per user per day | 0.5 | Not everyone tweets daily |
| Read:write ratio | ~400:1 | Heavily read-dominant |

### Read QPS (Timeline Loads)

```
Step 1: Timeline API calls per day
  = DAU x refreshes_per_day
  = 250,000,000 x 10
  = 2,500,000,000 (2.5 billion)

Step 2: Average QPS
  = 2,500,000,000 / 86,400
  = ~29,000 requests/second

Step 3: Peak QPS (assume 3x for major events)
  = 29,000 x 3
  = ~87,000 requests/second
```

### Write QPS (New Tweets)

```
Step 1: New tweets per day
  = DAU x tweets_per_user
  = 250,000,000 x 0.5
  = 125,000,000 (125 million)

Step 2: Average QPS
  = 125,000,000 / 86,400
  = ~1,450 tweets/second

Step 3: Peak QPS
  = 1,450 x 3
  = ~4,350 tweets/second
```

### Fan-out Consideration

Each tweet must be delivered to followers. If the average user has 200 followers:

```
Fan-out writes per second:
  = 1,450 tweets/s x 200 followers
  = 290,000 fan-out writes/second
```

This is why Twitter uses a pre-computed timeline (fan-out on write) for most users but switches to fan-out on read for celebrities with millions of followers.

### Summary

```
+-------------------------+-------------------+
| Metric                  | Estimate          |
+-------------------------+-------------------+
| Timeline read QPS       | ~29,000           |
| Peak timeline QPS       | ~87,000           |
| Write (tweet) QPS       | ~1,450            |
| Fan-out writes/s        | ~290,000          |
| Read:Write ratio        | ~400:1            |
+-------------------------+-------------------+
```

---

## 31.8 Worked Example: Estimate Bandwidth for YouTube

Let us estimate YouTube's bandwidth requirements.

### Assumptions

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| DAU | 800 million | YouTube's approximate DAU |
| Videos watched per user per day | 5 | Average across all users |
| Average video length | 5 minutes | Mix of short and long content |
| Average video bitrate (streaming) | 5 Mbps | 720p-1080p adaptive |
| Video uploads per day | 500,000 | Creators upload ~500K videos/day |
| Average upload size | 500 MB | Before transcoding |
| Number of transcoded variants | 5 | 240p, 360p, 480p, 720p, 1080p |

### Streaming (Outgoing) Bandwidth

```
Step 1: Total viewing time per day
  = DAU x videos_per_user x avg_length
  = 800,000,000 x 5 x 5 minutes
  = 20,000,000,000 minutes/day
  = 20 billion minutes/day

Step 2: Total viewing time in seconds
  = 20,000,000,000 x 60
  = 1,200,000,000,000 seconds/day (1.2 trillion)

Step 3: Average concurrent viewers (spread over 24h)
  = 1,200,000,000,000 / 86,400
  = ~13,900,000 concurrent streams

Step 4: Outgoing bandwidth
  = 13,900,000 x 5 Mbps
  = 69,500,000 Mbps
  = ~69.5 Tbps (terabits per second)

Step 5: With CDN (most traffic served from edge)
  Origin bandwidth = 69.5 Tbps x 10% (CDN cache hit ~90%)
  = ~7 Tbps from origin
```

### Upload (Incoming) Bandwidth

```
Step 1: Upload volume per day
  = 500,000 videos x 500 MB
  = 250,000,000 MB
  = 250 TB/day

Step 2: Upload bandwidth (average)
  = 250 TB / 86,400 seconds
  = ~2.9 GB/s
  = ~23 Gbps

Step 3: Transcoding output (5 variants, each ~60% of original size)
  = 250 TB x 5 x 0.6
  = 750 TB/day of transcoded output
```

### Storage

```
Step 1: Daily storage (all variants)
  = original + transcoded
  = 250 TB + 750 TB
  = 1,000 TB = 1 PB/day

Step 2: Yearly storage
  = 1 PB x 365
  = 365 PB/year

Step 3: With replication (3x)
  = 365 PB x 3
  = ~1,095 PB/year (~1.1 EB/year)
```

### Summary

```
+-------------------------+-------------------+
| Metric                  | Estimate          |
+-------------------------+-------------------+
| Concurrent streams      | ~14 million       |
| Streaming bandwidth     | ~69.5 Tbps        |
| Origin bandwidth (CDN)  | ~7 Tbps           |
| Upload bandwidth        | ~23 Gbps          |
| Daily storage (all)     | ~1 PB             |
| Yearly storage (3x rep) | ~1.1 EB           |
+-------------------------+-------------------+
```

These numbers explain why YouTube operates its own CDN (Google Global Cache), builds custom hardware, and is one of the largest consumers of internet bandwidth worldwide.

---

## 31.9 Estimation Cheat Sheet

Use this quick reference during interviews:

```
+----------------------------------+----------------------------+
| What You Need                    | Formula                    |
+----------------------------------+----------------------------+
| QPS                              | DAU x actions/user / 86400 |
| Peak QPS                         | Average QPS x 2~5         |
| Daily storage                    | New items/day x item size  |
| Yearly storage                   | Daily x 365               |
| Incoming bandwidth               | Write QPS x write size     |
| Outgoing bandwidth               | Read QPS x response size   |
| Number of servers (CPU-bound)    | Peak QPS / QPS per server  |
| Number of servers (memory-bound) | Working set / RAM per node |
+----------------------------------+----------------------------+
```

### Common Reference Numbers

```
+----------------------------------+----------------------------+
| Item                             | Typical Size               |
+----------------------------------+----------------------------+
| A tweet / short text post        | 300 bytes - 1 KB           |
| A user profile record            | 1 - 5 KB                  |
| A compressed photo (JPEG)        | 200 KB - 2 MB              |
| A 1-minute video (720p)          | 30 - 60 MB                |
| A database row (relational)      | 100 bytes - 1 KB          |
| An API response (JSON)           | 1 - 50 KB                 |
+----------------------------------+----------------------------+

+----------------------------------+----------------------------+
| System Capacity                  | Typical Range              |
+----------------------------------+----------------------------+
| Single web server QPS            | 1,000 - 10,000             |
| Single DB server QPS (simple)    | 5,000 - 20,000             |
| Single Redis instance QPS        | 50,000 - 100,000           |
| Single machine RAM               | 64 - 512 GB               |
| Single machine SSD               | 1 - 8 TB                  |
| 1 Gbps network link              | ~125 MB/s throughput       |
| 10 Gbps network link             | ~1.25 GB/s throughput      |
+----------------------------------+----------------------------+
```

---

## 31.10 Tips for Estimation in Interviews

### Do

1. **State your assumptions clearly.** "I will assume DAU is 100 million" is much better than just using a number.
2. **Round aggressively.** Use 100,000 instead of 86,400. Use 300 million instead of 328 million. Precision does not matter.
3. **Show your work.** Write each step on the whiteboard. The interviewer wants to see your thought process.
4. **Sanity check results.** If you calculate that a text messaging app needs 1 PB of storage per day, something is wrong.
5. **Use powers of 10.** Everything is easier when you think in powers of 10.

### Do Not

1. **Do not spend more than 5 minutes on estimation.** It is a tool, not the design itself.
2. **Do not argue about exact numbers.** "Is it 3 MB or 5 MB?" does not matter. The order of magnitude matters.
3. **Do not forget peak traffic.** Average QPS is useful, but your system must handle peaks.
4. **Do not ignore replication.** Storage estimates should include replication factor (usually 3x).
5. **Do not forget the read/write ratio.** This determines your caching and scaling strategy.

---

## Common Mistakes

1. **Confusing bits and bytes.** Network speeds are in bits per second (Mbps, Gbps). Storage is in bytes (MB, GB). There are 8 bits in a byte.

2. **Forgetting to account for metadata.** A 1 MB photo needs more than 1 MB of storage when you add database indexes, file system overhead, and metadata.

3. **Using daily averages for capacity planning.** Peak traffic can be 3-10x the average. Size your system for peaks.

4. **Ignoring compression.** Text compresses 5-10x. Images are already compressed. Not accounting for compression leads to wildly wrong bandwidth estimates.

5. **Treating all users as equal.** Power users (celebrities, brands) generate disproportionate traffic. A single viral tweet can create millions of reads.

---

## Best Practices

1. **Memorize the latency numbers table.** You will use it in every interview.

2. **Practice converting between units quickly.** You should be able to go from "500 million requests per day" to "~6,000 QPS" in your head.

3. **Always estimate both reads and writes.** The ratio between them drives fundamental design decisions.

4. **Work top-down.** Start with users, then actions per user, then QPS, then storage, then bandwidth.

5. **Use a consistent framework.** Same steps every time: Traffic -> Storage -> Bandwidth -> Number of machines.

6. **Keep a mental model of "big company" numbers.** Google: billions of searches. Instagram: hundreds of millions of DAU. YouTube: billions of hours watched per day. These anchor your estimates.

---

## Quick Summary

Estimation math is about reasoning at the right order of magnitude, not getting exact answers. Memorize the powers of 2 table, the latency numbers, and the conversion shortcuts. Follow the top-down framework: start with DAU, calculate QPS (average and peak, reads and writes), estimate storage (daily, yearly, with replication), and compute bandwidth. Always state your assumptions, round aggressively, and sanity check your results. Five minutes of good estimation sets the foundation for the entire design discussion.

---

## Key Points

- Seconds in a day: ~86,400 (round to 100,000 for easy math).
- RAM is 1000x faster than SSD; SSD is 100x faster than HDD.
- QPS = DAU x actions per user / 86,400. Peak QPS = 2x to 5x average.
- Storage grows linearly: new items per day x item size x 365 x replication factor.
- Network bandwidth is measured in bits; storage in bytes. 1 byte = 8 bits.
- Always estimate reads and writes separately. The ratio drives design decisions.
- Compression saves 5-10x for text, but images and video are already compressed.
- Your estimates should be within the right order of magnitude (10x), not exact.

---

## Practice Questions

1. A messaging app has 50 million DAU. Each user sends 40 messages per day and receives 40 messages per day. Average message size is 200 bytes. Calculate the write QPS, read QPS, daily storage, and yearly storage.

2. A video conferencing platform has 10 million DAU. Each user averages 2 meetings per day, each lasting 30 minutes. Video is streamed at 2 Mbps per participant. Average meeting size is 4 participants. What is the peak concurrent bandwidth?

3. An e-commerce site receives 50 million product page views per day. Each page view returns 100 KB of data. The site has 10 million products, each with a 5 KB database record. How much RAM do you need to cache all products? What is the outgoing bandwidth?

4. Why is cross-continent latency (~100 ms) a critical factor for global system design, but L1 cache latency (1 ns) is rarely discussed in system design interviews?

5. You are designing a system that stores 10 billion records, each 1 KB in size. You want all data accessible with less than 1 ms latency. Can you keep all data in RAM? How many machines do you need? (Assume 256 GB RAM per machine.)

---

## Exercises

**Exercise 1: Estimate Slack's Infrastructure**

Slack has 30 million DAU. Each user sends 50 messages per day across 10 channels. Messages average 500 bytes. Users also upload 0.5 files per day averaging 2 MB each. Calculate: write QPS, read QPS (assume 10:1 read/write), daily message storage, daily file storage, and outgoing bandwidth. How many database servers do you need if each handles 10,000 write QPS?

**Exercise 2: Cost Estimation**

Using your Instagram storage estimate from Section 31.6 (225 TB/day, ~82 PB/year), calculate the approximate annual storage cost using cloud pricing of $0.02 per GB per month for standard storage. How much would you save by moving data older than 90 days to cold storage at $0.004 per GB per month?

**Exercise 3: Build Your Own Cheat Sheet**

Create a one-page estimation cheat sheet for three systems you might encounter in an interview: a ride-sharing app, a photo-sharing app, and a real-time multiplayer game. For each, list the key assumptions (DAU, actions per user, data sizes), and pre-calculate the QPS, storage, and bandwidth. Practice presenting each estimate in under 3 minutes.

---

## What Is Next?

Now that you can reason about scale, the next chapter gives you a complete framework for structuring your system design interview from start to finish. You will learn the four-step process that top candidates follow, the communication patterns that impress interviewers, and how to manage your time in a 45-minute session.
