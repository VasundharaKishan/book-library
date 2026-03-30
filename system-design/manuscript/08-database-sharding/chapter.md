# Chapter 8: Database Sharding

## What You Will Learn

- Why a single database cannot handle billions of rows
- What horizontal partitioning (sharding) means
- How to choose a sharding strategy: hash-based, range-based, geographic, and directory-based
- Why shard key selection is the most critical decision
- The problems sharding introduces: cross-shard joins, hotspots, and resharding
- What consistent hashing is and why it matters for sharding
- The celebrity problem (hot partitions)

## Why This Chapter Matters

Your application is a hit. Millions of users are signing up. Your database, even with replicas handling reads, is struggling. The single leader server that handles all writes is running out of disk space, CPU, and memory. You cannot make the server bigger forever. There is a physical limit to how powerful a single machine can be.

Sharding is the answer. It splits your data across multiple independent databases, each handling a portion of the total data. Every large-scale system, from Instagram to Uber to Stripe, uses sharding. In system design interviews, sharding is one of the most frequently discussed topics. Understanding it deeply sets you apart from other candidates.

---

## The Problem: Why Shard?

Let us say you run an e-commerce platform. Your orders table has grown to 2 billion rows. Here is what happens:

```
  Single Database Problem:

  +----------------------------------+
  |         SINGLE DATABASE          |
  |                                  |
  |  Orders Table: 2 billion rows    |
  |  Size: 4 TB                      |
  |  Indexes: 800 GB                 |
  |                                  |
  |  Problems:                       |
  |  - Queries take 30+ seconds      |
  |  - Backups take 12 hours         |
  |  - Schema migrations = downtime  |
  |  - Single disk is full           |
  |  - CPU at 95% constantly         |
  +----------------------------------+
```

**Vertical scaling** (buying a bigger server) has limits. The most powerful single server you can buy might have 128 CPU cores and 4 TB of RAM, but eventually your data outgrows even that. And those machines are extremely expensive.

**Horizontal scaling** (sharding) is the solution. Instead of one giant database, you split the data across multiple smaller databases:

```
  After Sharding:

  +------------+  +------------+  +------------+  +------------+
  |  SHARD 1   |  |  SHARD 2   |  |  SHARD 3   |  |  SHARD 4   |
  |            |  |            |  |            |  |            |
  | 500M rows  |  | 500M rows  |  | 500M rows  |  | 500M rows  |
  | 1 TB       |  | 1 TB       |  | 1 TB       |  | 1 TB       |
  |            |  |            |  |            |  |            |
  | Fast       |  | Fast       |  | Fast       |  | Fast       |
  | queries!   |  | queries!   |  | queries!   |  | queries!   |
  +------------+  +------------+  +------------+  +------------+
```

Each shard is an independent database. It has its own CPU, memory, disk, and indexes. Queries against 500 million rows are much faster than queries against 2 billion rows.

---

## Sharding Strategies

The most important decision in sharding is: **how do you decide which data goes to which shard?** This is determined by the **shard key** (also called partition key) and the **sharding strategy**.

### 1. Hash-Based Sharding

Take the shard key, run it through a hash function, and use the result to determine the shard.

```
  Hash-Based Sharding:

  shard_number = hash(shard_key) % number_of_shards

  Example with 4 shards:

  User ID: 1001  ->  hash(1001) % 4 = 2  ->  Shard 2
  User ID: 1002  ->  hash(1002) % 4 = 0  ->  Shard 0
  User ID: 1003  ->  hash(1003) % 4 = 3  ->  Shard 3
  User ID: 1004  ->  hash(1004) % 4 = 1  ->  Shard 1

  +----------+    +----------+    +----------+    +----------+
  | Shard 0  |    | Shard 1  |    | Shard 2  |    | Shard 3  |
  |          |    |          |    |          |    |          |
  | User 1002|    | User 1004|    | User 1001|    | User 1003|
  | User 1006|    | User 1008|    | User 1005|    | User 1007|
  | ...      |    | ...      |    | ...      |    | ...      |
  +----------+    +----------+    +----------+    +----------+
```

**Pros:**
- Distributes data evenly (good hash functions spread values uniformly)
- Simple to implement
- Works well for key-value lookups

**Cons:**
- Adding or removing shards requires rehashing almost everything
- Range queries are impossible (data for consecutive IDs is scattered)
- Cannot do efficient "get all users between ID 1000 and 2000"

### 2. Range-Based Sharding

Divide data into contiguous ranges based on the shard key value.

```
  Range-Based Sharding:

  Shard by User ID ranges:

  +------------------+  +------------------+  +------------------+
  |    Shard A       |  |    Shard B       |  |    Shard C       |
  |                  |  |                  |  |                  |
  | User IDs:       |  | User IDs:       |  | User IDs:       |
  | 1 - 1,000,000   |  | 1,000,001 -     |  | 2,000,001 -     |
  |                  |  | 2,000,000       |  | 3,000,000       |
  +------------------+  +------------------+  +------------------+

  Query: "Get users 500 to 600"
  -> Only needs to go to Shard A!
```

**Pros:**
- Range queries are efficient (data in a range lives on the same shard)
- Simple to understand
- Easy to split a shard when it gets too large

**Cons:**
- Can create hotspots (if most new users have high IDs, the last shard gets all the writes)
- Uneven distribution is common
- Requires careful range planning

### 3. Geographic Sharding

Route data to shards based on geographic location. This is common for applications with strong regional data locality requirements.

```
  Geographic Sharding:

  +------------------+  +------------------+  +------------------+
  |   US Shard       |  |   EU Shard       |  |  APAC Shard     |
  |                  |  |                  |  |                  |
  | US users' data   |  | EU users' data   |  | Asian users'    |
  | US East DC       |  | Frankfurt DC     |  | data            |
  |                  |  |                  |  | Singapore DC    |
  +------------------+  +------------------+  +------------------+

  User in Paris -> EU Shard (low latency)
  User in Tokyo -> APAC Shard (low latency)
  User in NYC   -> US Shard (low latency)
```

**Pros:**
- Low latency for users (data is close to them)
- Helps with data residency laws (GDPR requires EU data to stay in EU)
- Natural partitioning for many business models

**Cons:**
- Uneven distribution (some regions have far more users)
- Cross-region queries are slow
- Users who travel may experience higher latency

### 4. Directory-Based Sharding

Maintain a lookup table that maps each shard key to its shard. A central directory service knows where every piece of data lives.

```
  Directory-Based Sharding:

  +---------------------+
  |   LOOKUP TABLE      |
  |                     |
  | User 1001 -> Shard2 |
  | User 1002 -> Shard1 |
  | User 1003 -> Shard3 |
  | User 1004 -> Shard1 |
  | ...                 |
  +----------+----------+
             |
     +-------+-------+-------+
     |       |       |       |
     v       v       v       v
  +------+ +------+ +------+ +------+
  |Shard1| |Shard2| |Shard3| |Shard4|
  +------+ +------+ +------+ +------+
```

**Pros:**
- Maximum flexibility (can move any record to any shard)
- Easy to rebalance without changing the hashing strategy
- Can accommodate custom routing logic

**Cons:**
- The lookup table is a single point of failure
- Every query requires a lookup first (extra latency)
- The lookup table itself can become a bottleneck

### Comparison of Strategies

| Strategy | Distribution | Range Queries | Flexibility | Complexity |
|---|---|---|---|---|
| Hash-Based | Even | Not supported | Low | Low |
| Range-Based | Can be uneven | Efficient | Medium | Medium |
| Geographic | Varies by region | Regional only | Medium | Medium |
| Directory-Based | Controllable | Depends | High | High |

---

## Shard Key Selection: The Most Critical Decision

Choosing the right shard key can make or break your system. A bad shard key leads to hotspots, inefficient queries, and painful migrations. Here is how to think about it.

### What Makes a Good Shard Key?

A good shard key has three properties:

1. **High cardinality**: Many distinct values so data spreads across shards. User ID is good (millions of values). Boolean "is_active" is terrible (only two values).

2. **Even distribution**: Values should distribute data evenly. A timestamp shard key is bad because all recent data goes to one shard.

3. **Query alignment**: The shard key should match your most common query patterns. If you always query by user ID, shard by user ID.

### Examples of Good and Bad Shard Keys

```
  E-Commerce Application

  GOOD shard key: user_id
  - High cardinality (millions of users)
  - Even distribution
  - Most queries are per-user ("show my orders")

  BAD shard key: order_status
  - Low cardinality (pending, shipped, delivered)
  - Uneven ("delivered" has 80% of orders)
  - Creates massive hotspots

  BAD shard key: created_at
  - All new orders go to one shard
  - Creates a "write hotspot" on the newest shard

  +------------------+------------------+------------------+
  |                  |                  |                  |
  | Shard by         | Shard by         | Shard by         |
  | user_id          | order_status     | created_at       |
  |                  |                  |                  |
  | [====]  [====]   | [==]  [==]       | [=]   [=]        |
  | [====]  [====]   | [========]       | [=]   [========] |
  |                  | (hotspot!)       | (hotspot!)       |
  | Even!            | Uneven!          | Uneven!          |
  +------------------+------------------+------------------+
```

### Compound Shard Keys

Sometimes a single field is not enough. You can combine fields to create a compound shard key.

For a messaging application, you might use `(user_id, date)` as the compound key. This distributes data by user and also keeps recent messages together for efficient queries.

---

## Problems with Sharding

Sharding introduces several challenges that do not exist with a single database.

### 1. Cross-Shard Joins

With a single database, joining the `users` table with the `orders` table is simple. With sharding, user data might be on Shard 1 and their orders on Shard 3.

```
  Cross-Shard Join Problem:

  Query: "Get user name and their orders"

  +------------------+          +------------------+
  |    Shard 1       |          |    Shard 3       |
  |                  |          |                  |
  | Users table:     |          | Orders table:    |
  | ID=1001, Alice   |   ???    | User 1001,       |
  |                  | <------> | Order #5555      |
  +------------------+          +------------------+

  JOIN across shards requires:
  1. Query Shard 1 for user data
  2. Query Shard 3 for order data
  3. Combine results in application code
  4. Much slower than a single-DB join!
```

**Solutions:**
- Denormalize data (store user name alongside orders)
- Keep related data on the same shard (shard both tables by user_id)
- Use an application-level join (query both shards and merge in code)

### 2. Hotspots

Even with a good shard key, certain records may receive disproportionately more traffic. This is the **celebrity problem**.

```
  The Celebrity Problem:

  Instagram sharded by user_id:

  +------------------+  +------------------+  +------------------+
  |    Shard 1       |  |    Shard 2       |  |    Shard 3       |
  |                  |  |                  |  |                  |
  | Regular users    |  | Kim Kardashian   |  | Regular users    |
  | 100 req/s each   |  | 1,000,000 req/s  |  | 100 req/s each   |
  |                  |  |                  |  |                  |
  | Total: 10K req/s |  | Total: 1M req/s  |  | Total: 10K req/s |
  |                  |  |  (OVERLOADED!)   |  |                  |
  +------------------+  +------------------+  +------------------+
```

**Solutions:**
- Add a random suffix to the shard key for hot records (split one celebrity's data across multiple shards)
- Cache celebrity data aggressively
- Assign dedicated resources to hot shards

### 3. Resharding

When you need to change the number of shards (because data grew or shrank), you need to redistribute data. With simple hash-based sharding, this means moving most of your data.

```
  Resharding Problem (hash-based):

  BEFORE: 4 shards
  hash(key) % 4 = shard_number

  AFTER: 5 shards
  hash(key) % 5 = shard_number

  Key "user_1001":
    hash(1001) = 7834
    7834 % 4 = 2  (was on Shard 2)
    7834 % 5 = 4  (now belongs on Shard 4)

  ~80% of data needs to move!
```

This is why **consistent hashing** was invented (covered in Chapter 12). With consistent hashing, adding a new shard only requires moving about `1/n` of the data, where `n` is the number of shards.

### 4. Auto-Incrementing IDs

With a single database, auto-incrementing IDs are easy. With multiple shards, each shard generates its own IDs, causing collisions.

```
  ID Collision Problem:

  Shard 1: INSERT -> ID = 1, 2, 3, 4...
  Shard 2: INSERT -> ID = 1, 2, 3, 4...   <-- Same IDs!
```

**Solutions:**

| Solution | How It Works | Downside |
|---|---|---|
| UUID | Generate random 128-bit IDs | Large, not sortable |
| Snowflake IDs | Combine timestamp + machine ID + sequence | Requires clock synchronization |
| Range allocation | Each shard gets a range (Shard 1: 1-1M, Shard 2: 1M-2M) | Requires coordination |
| Central ID service | One service generates all IDs | Single point of failure |

### 5. Transactions Across Shards

Single-database transactions are straightforward. Cross-shard transactions (distributed transactions) are slow and complex.

```
  Cross-Shard Transaction:

  "Transfer $100 from Account A (Shard 1) to Account B (Shard 3)"

  Shard 1: Debit $100 from A   \
                                 } Must BOTH succeed or BOTH fail
  Shard 3: Credit $100 to B    /

  Requires: Two-Phase Commit (2PC) or Saga pattern
  Both add significant complexity.
```

---

## Consistent Hashing Preview

Consistent hashing solves the resharding problem. Instead of `hash(key) % n`, it uses a hash ring where both servers and keys are mapped to positions on a circle.

```
  Consistent Hashing Ring (Preview):

           0
           |
     315 --+-- 45
          /   \
    270 -+     +- 90
          \   /
     225 --+-- 135
           |
          180

  Servers at positions: S1=45, S2=135, S3=270
  Keys map to positions and go to the next server clockwise.

  Adding S4 at 200:
  - Only keys between 135 and 200 move to S4
  - Everything else stays put!
```

We will explore consistent hashing in detail in Chapter 12.

---

## Sharded Architecture in Practice

Here is what a complete sharded architecture looks like:

```
  Complete Sharded Architecture:

  +------------------+
  |   Application    |
  |    Servers       |
  +--------+---------+
           |
           v
  +------------------+
  |  Shard Router /  |
  |  Proxy Layer     |
  |                  |
  | "Which shard     |
  |  has this data?" |
  +--------+---------+
           |
     +-----+-----+-----+-----+
     |     |     |     |     |
     v     v     v     v     v
  +----+ +----+ +----+ +----+ +----+
  | S1 | | S2 | | S3 | | S4 | | S5 |
  +----+ +----+ +----+ +----+ +----+
  | L  | | L  | | L  | | L  | | L  |  <-- Each shard has
  | |  | | |  | | |  | | |  | | |  |      its own leader
  | F F| | F F| | F F| | F F| | F F|      and followers
  +----+ +----+ +----+ +----+ +----+      (replication!)

  L = Leader    F = Follower

  Each shard is independently replicated for high availability.
```

The **shard router** (also called a proxy or coordinator) is the component that knows which shard holds which data. It can be:

- A dedicated proxy service (like Vitess for MySQL or mongos for MongoDB)
- A library embedded in the application
- A middleware layer

---

## Trade-Offs

| Decision | Option A | Option B |
|---|---|---|
| Sharding vs Not Sharding | Shard (handles scale, adds complexity) | Single DB with replicas (simpler, limited scale) |
| Hash vs Range | Hash (even distribution, no range queries) | Range (range queries, risk of hotspots) |
| Shard Key | user_id (per-user queries are fast) | order_id (per-order queries are fast, cross-user analytics hard) |
| Number of Shards | Few large shards (simpler, resharding sooner) | Many small shards (longer runway, more operational burden) |
| Routing | Proxy-based (centralized, extra hop) | Client-side (faster, clients need shard map) |

---

## Common Mistakes

1. **Sharding too early.** Sharding adds enormous complexity. Many systems never need it. Optimize queries, add indexes, use read replicas, and cache aggressively before considering sharding.

2. **Choosing the wrong shard key.** Changing the shard key after the system is in production is extremely painful, often requiring a full data migration. Spend significant time on this decision.

3. **Forgetting about cross-shard queries.** If your application needs complex joins or aggregations across all data, sharding will make those operations much slower or impossible.

4. **Ignoring the celebrity problem.** Even with hash-based sharding, a single hot key can overwhelm one shard. Plan for uneven traffic patterns.

5. **Not planning for resharding.** Your data will grow. If you use simple modular hashing, adding shards means moving most of your data. Use consistent hashing from the start.

---

## Best Practices

1. **Delay sharding as long as possible.** Use vertical scaling, read replicas, caching, and query optimization first. Shard only when you truly need to.

2. **Choose the shard key based on your query patterns.** The most common query determines the best shard key. If 90% of queries are "get data for user X," shard by user_id.

3. **Keep related data on the same shard.** If users and their orders are always queried together, shard both tables by user_id so joins stay local.

4. **Plan for at least 2x your current data.** If you have 100 GB now, design for 200 GB or more. This gives you room to grow before resharding.

5. **Use consistent hashing.** It makes adding and removing shards much less painful. Most modern systems use this approach.

6. **Each shard should be replicated.** Sharding alone does not provide high availability. Each shard needs its own leader-follower replication setup.

7. **Monitor shard sizes and query patterns.** Uneven shards indicate a bad shard key or hotspot. Catch this early.

8. **Build a shard management tool.** You will need the ability to split shards, merge shards, and move data between shards. Automate these operations.

---

## Quick Summary

Database sharding splits data across multiple independent databases (shards) to handle scale beyond what a single server can manage. The shard key determines how data is distributed. Hash-based sharding gives even distribution but prevents range queries. Range-based sharding supports range queries but risks hotspots. Geographic sharding keeps data close to users. Directory-based sharding offers maximum flexibility but adds a lookup overhead. Sharding introduces challenges including cross-shard joins, hotspots (the celebrity problem), resharding complexity, ID generation, and distributed transactions. Start with the simplest approach that works, and always replicate each shard for availability.

---

## Key Points

- Shard when a single database cannot handle the data size or write throughput, not before
- The shard key is the most important decision; it determines data distribution and query efficiency
- Hash-based sharding distributes evenly but scatters range queries; range-based supports ranges but risks hotspots
- Cross-shard joins are expensive; keep related data on the same shard
- The celebrity problem causes hotspots even with good shard keys; use caching or key splitting
- Resharding with modular hashing moves most data; consistent hashing moves only 1/n of data
- Each shard should be independently replicated for high availability
- Delay sharding as long as possible; it adds significant operational complexity

---

## Practice Questions

1. You are building a messaging application with 500 million users. Each user sends an average of 50 messages per day. How would you shard the messages table? What would you choose as the shard key, and why?

2. Your e-commerce platform is sharded by user_id. A product manager asks for a report: "Show me total revenue per product category across all users." How would you generate this report? What are the challenges?

3. A social media platform uses hash-based sharding with 8 shards. A celebrity with 100 million followers posts an update. How does this create a problem, and what would you do about it?

4. Compare hash-based and range-based sharding for a time-series database that stores IoT sensor readings. Which would you choose and why?

5. You currently have 4 shards and need to add a fifth. With simple modular hashing, approximately what percentage of data needs to move? How does consistent hashing improve this?

---

## Exercises

**Exercise 1: Shard Key Analysis**

For each of the following applications, propose a shard key and justify your choice. Consider query patterns, distribution, and potential hotspots.

- A ride-sharing application (like Uber)
- An email service (like Gmail)
- A video streaming platform (like YouTube)

**Exercise 2: Design a Sharding Migration Plan**

Your application currently uses a single PostgreSQL database with 500 GB of data. You need to shard it into 4 shards with zero downtime. Write a step-by-step migration plan. Consider: how to set up the new shards, how to copy data, how to handle writes during migration, and how to switch traffic.

**Exercise 3: Cross-Shard Query Optimization**

You have a users table sharded by user_id and an orders table also sharded by user_id. The business needs a daily report that ranks the top 100 products by total revenue across all users. Design an efficient way to generate this report without querying all shards synchronously.

---

## What Is Next?

You now know how to replicate databases for availability and shard them for scale. But what happens between your services? When Service A needs to tell Service B that something happened, should it call Service B directly? What if Service B is down? What if it takes too long? The answer is **message queues**, the backbone of asynchronous communication in modern systems. In the next chapter, you will learn how message queues decouple services, buffer traffic, and make your system more resilient.
