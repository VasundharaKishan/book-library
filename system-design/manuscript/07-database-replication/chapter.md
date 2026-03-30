# Chapter 7: Database Replication

## What You Will Learn

- Why databases need replication and what problems it solves
- How leader-follower (master-slave) replication works
- How leader-leader (multi-master) replication works
- The difference between synchronous and asynchronous replication
- What replication lag is and why it matters
- How read replicas improve performance
- What failover means and how it works (manual vs automatic)
- The split-brain problem and how to avoid it

## Why This Chapter Matters

Imagine you run a popular online bookstore. Your single database handles every customer order, every search, and every product page load. One day, that server dies. Your entire business goes offline. Every second costs you money and customer trust.

Now imagine you had an exact copy of that database on another server, ready to take over instantly. That is replication.

In system design interviews, replication comes up in almost every question. Whether you are designing Twitter, Instagram, or a payment system, the interviewer expects you to know how data stays available when servers fail. This chapter gives you that knowledge.

---

## What Is Database Replication?

Database replication is the process of keeping copies of the same data on multiple database servers. Think of it like making photocopies of an important document and storing them in different locations. If one copy gets destroyed, you still have others.

```
  Original Document          Copies
  +----------------+    +----------------+
  |                |    |                |
  |   Important    |--->|   Copy in      |
  |   Contract     |    |   Office Safe  |
  |                |    |                |
  +----------------+    +----------------+
         |
         |               +----------------+
         |               |                |
         +-------------->|   Copy at      |
         |               |   Bank Vault   |
         |               |                |
         |               +----------------+
         |
         |               +----------------+
         |               |                |
         +-------------->|   Copy at      |
                         |   Lawyer       |
                         |                |
                         +----------------+
```

Each copy is called a **replica**. The collection of all replicas is called a **replica set**.

### Why Replicate?

There are three main reasons to replicate your database:

**1. High Availability**

If one server crashes, another replica can serve requests. Your application stays online. In the bookstore example, customers keep shopping even when a server fails.

**2. Better Read Performance**

Most applications read data far more often than they write it. Think about Instagram: millions of people view posts every second, but relatively few are uploading new photos at any given moment. By spreading read requests across multiple replicas, each server handles a smaller share of the traffic.

**3. Geographic Distribution**

If your users are spread across the world, you can place replicas closer to them. A user in Tokyo gets data from a server in Japan instead of waiting for a response from a server in Virginia.

---

## Leader-Follower Replication (Master-Slave)

This is the most common replication setup. One server is the **leader** (also called the master or primary). All other servers are **followers** (also called slaves, secondaries, or read replicas).

The rule is simple:
- All **writes** go to the leader
- All **reads** can go to the leader or any follower
- The leader sends data changes to all followers

```
                    WRITES
                      |
                      v
              +---------------+
              |               |
              |    LEADER     |
              |   (Primary)   |
              |               |
              +-------+-------+
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
   +-----------+ +-----------+ +-----------+
   |           | |           | |           |
   | FOLLOWER  | | FOLLOWER  | | FOLLOWER  |
   |   (R1)    | |   (R2)    | |   (R3)    |
   |           | |           | |           |
   +-----------+ +-----------+ +-----------+
        ^              ^             ^
        |              |             |
   +----+--------------+-------------+----+
   |              READS                    |
   +---------------------------------------+
```

### How It Works Step by Step

1. A client sends a write request (for example, "insert new order").
2. The leader processes the write and stores it in its database.
3. The leader records the change in a **replication log** (also called a write-ahead log or binary log).
4. Each follower reads the replication log and applies the same changes to its own copy of the data.
5. When a client sends a read request, it can be routed to any follower (or the leader).

```
  Client: "Insert Order #1234"
            |
            v
  +-------------------+
  | LEADER            |
  | 1. Process write  |
  | 2. Store data     |
  | 3. Write to log   |-----> Replication Log
  +-------------------+       [INSERT Order #1234]
                                     |
                        +------------+------------+
                        |            |            |
                        v            v            v
                   +---------+  +---------+  +---------+
                   |Follower1|  |Follower2|  |Follower3|
                   |Read log |  |Read log |  |Read log |
                   |Apply    |  |Apply    |  |Apply    |
                   +---------+  +---------+  +---------+
```

### Advantages of Leader-Follower

- Simple to understand and implement
- No write conflicts (only one server accepts writes)
- Easy to scale reads by adding more followers
- Well-supported by most databases (MySQL, PostgreSQL, MongoDB)

### Disadvantages of Leader-Follower

- The leader is a single point of failure for writes
- All writes must go through one server, which can become a bottleneck
- Followers may have slightly stale data (replication lag)

---

## Leader-Leader Replication (Multi-Master)

In leader-leader replication, **two or more servers** can accept writes. Each leader sends its changes to the other leaders. Every server is both a leader and a follower at the same time.

```
            WRITES                    WRITES
              |                         |
              v                         v
      +---------------+        +---------------+
      |               |------->|               |
      |   LEADER A    |        |   LEADER B    |
      |  (US East)    |<-------|  (EU West)    |
      |               |        |               |
      +-------+-------+        +-------+-------+
              |                         |
        +-----+-----+            +-----+-----+
        |           |            |           |
        v           v            v           v
   +---------+ +---------+ +---------+ +---------+
   |Follower | |Follower | |Follower | |Follower |
   |  A1     | |  A2     | |  B1     | |  B2     |
   +---------+ +---------+ +---------+ +---------+
```

### When to Use Multi-Master

Multi-master replication makes sense when:

- You have users in multiple geographic regions and want low-latency writes everywhere
- You need write availability even if one data center goes down
- You are running an application like Google Docs where multiple users edit simultaneously

### The Write Conflict Problem

The biggest challenge with multi-master replication is **write conflicts**. What happens when two users update the same record at the same time on different leaders?

```
  Time   Leader A (US)              Leader B (EU)
  ----   ----------------           ----------------
  T1     User sets price            User sets price
         to $10                     to $15
  T2     Sends change to B -------> Sends change to A
  T3     CONFLICT!                  CONFLICT!
         Should price be            Should price be
         $10 or $15?                $10 or $15?
```

Common strategies to resolve conflicts:

| Strategy | How It Works | Downside |
|---|---|---|
| Last Write Wins (LWW) | The write with the latest timestamp wins | Can lose data silently |
| Merge Values | Combine both values (for example, keep both edits) | Only works for some data types |
| Custom Logic | Application decides which write to keep | Adds complexity |
| Conflict Avoidance | Route all writes for a record to one leader | Reduces multi-master benefits |

### Advantages of Leader-Leader

- No single point of failure for writes
- Better write performance across regions
- Higher write availability

### Disadvantages of Leader-Leader

- Write conflicts are hard to resolve correctly
- More complex to set up and maintain
- Risk of data inconsistency
- Harder to debug when things go wrong

---

## Synchronous vs Asynchronous Replication

When the leader sends changes to followers, it can do so in two ways.

### Synchronous Replication

The leader waits for the follower to confirm it received and stored the change **before** telling the client the write was successful.

```
  Client          Leader            Follower
    |                |                  |
    |--- Write ----->|                  |
    |                |--- Replicate --->|
    |                |                  |
    |                |    (Follower     |
    |                |     writes to    |
    |                |     disk)        |
    |                |                  |
    |                |<-- ACK ----------|
    |                |                  |
    |<-- Success ----|                  |
    |                |                  |

  Total time: Write time + Network round trip + Follower write time
```

**Pros:**
- The follower is guaranteed to have the latest data
- If the leader crashes, the follower has everything
- No data loss

**Cons:**
- Slower writes (the client waits for the follower)
- If the follower is slow or down, the leader is blocked
- Higher latency

### Asynchronous Replication

The leader confirms the write to the client immediately. It sends the change to followers in the background.

```
  Client          Leader            Follower
    |                |                  |
    |--- Write ----->|                  |
    |                |                  |
    |<-- Success ----|                  |
    |                |                  |
    |                |--- Replicate --->|
    |                |                  |
    |                |    (Follower     |
    |                |     writes to    |
    |                |     disk)        |
    |                |                  |
    |                |<-- ACK ----------|

  Total time for client: Write time only (much faster)
```

**Pros:**
- Faster writes (the client does not wait for followers)
- The leader is never blocked by slow followers
- Works even when followers are temporarily unavailable

**Cons:**
- Risk of data loss if the leader crashes before replicating
- Followers may serve stale data

### Semi-Synchronous Replication

A practical middle ground: the leader waits for **at least one** follower to confirm, then acknowledges the client. The remaining followers replicate asynchronously.

```
  Client          Leader         Follower 1     Follower 2
    |                |               |               |
    |--- Write ----->|               |               |
    |                |-- Replicate ->|               |
    |                |               |               |
    |                |<---- ACK -----|               |
    |<-- Success ----|               |               |
    |                |               |               |
    |                |-- Replicate --|-------------->|
    |                |               |          (async)
```

This approach is used by many production systems. You get durability (at least one follower has the data) without waiting for every follower.

### Comparison Table

| Feature | Synchronous | Asynchronous | Semi-Synchronous |
|---|---|---|---|
| Write Speed | Slow | Fast | Medium |
| Data Safety | Highest | Lowest | Good |
| Complexity | Medium | Low | Medium |
| Availability | Lower (blocked by followers) | Higher | Good |
| Common Use | Financial systems | Social media, analytics | Most production databases |

---

## Replication Lag

Replication lag is the delay between when data is written to the leader and when it appears on the followers. With asynchronous replication, this lag is unavoidable.

### Real-World Example

Imagine you post a photo on social media. You upload it (write goes to the leader), and immediately refresh your profile page (read goes to a follower). But the follower has not received your photo yet. Your photo is missing from your own profile. Confusing, right?

```
  Timeline:

  T0: User uploads photo
      Leader: [Photo stored]     Follower: [No photo yet]

  T1: User refreshes profile (reads from follower)
      Leader: [Photo stored]     Follower: [No photo yet]

      User sees: "Where is my photo?!"

  T2: Follower catches up
      Leader: [Photo stored]     Follower: [Photo stored]

      User sees: "Oh, there it is."
```

### Types of Consistency Guarantees

To deal with replication lag, systems offer different consistency models:

**Read-After-Write Consistency (Read-Your-Writes)**

After a user writes something, they are guaranteed to see their own write. Other users might still see stale data. Implementation: route reads for the user's own data to the leader.

**Monotonic Reads**

A user will never see data go backward in time. If they saw a value at time T, they will not see an older value in a subsequent read. Implementation: route a user's reads to the same replica consistently.

**Consistent Prefix Reads**

If a sequence of writes happens in a certain order, any reader will see them in the same order. This matters for conversations:

```
  Without consistent prefix reads:

  Alice writes: "How are you?"     (T1)
  Bob writes:   "I am fine!"       (T2)

  Observer might see:
  Bob: "I am fine!"
  Alice: "How are you?"

  That makes no sense!
```

---

## Read Replicas

Read replicas are followers specifically designated to handle read traffic. They are one of the simplest ways to scale a database.

### How Read Replicas Help

```
  WITHOUT Read Replicas          WITH Read Replicas

  All traffic -> 1 server        Writes -> Leader
                                 Reads  -> Multiple Replicas

  +--------+                     +--------+
  | Leader | <-- 10,000 req/s    | Leader | <-- 1,000 writes/s
  +--------+                     +--------+
                                      |
                                 +----+----+----+
                                 |    |    |    |
                                 v    v    v    v
                                R1   R2   R3   R4
                                         |
                                   9,000 reads/s
                                   split across 4
                                   = 2,250 each
```

### Setting Up Read Replicas

Most cloud databases make this easy:

- **AWS RDS**: Create up to 15 read replicas with a few clicks
- **Google Cloud SQL**: Add read replicas across zones or regions
- **Azure Database**: Create read replicas in different regions

### When to Use Read Replicas

Read replicas work best when your application is **read-heavy**. Many applications fit this pattern:

| Application | Read:Write Ratio | Good Fit? |
|---|---|---|
| Social media feed | 100:1 | Excellent |
| E-commerce product pages | 50:1 | Excellent |
| Banking transactions | 1:1 | Poor (use synchronous replication instead) |
| Analytics dashboard | 1000:1 | Excellent |
| Chat application | 5:1 | Moderate |

---

## Failover

Failover is the process of switching from a failed server to a backup server. In the context of replication, failover usually means promoting a follower to become the new leader when the old leader fails.

### Manual Failover

A human operator detects the failure and manually promotes a follower. This is the safest approach but the slowest.

```
  Step 1: Leader fails

  +--------+     +-----------+     +-----------+
  |LEADER  |     |FOLLOWER 1 |     |FOLLOWER 2 |
  |  XXXX  |     |           |     |           |
  | (dead) |     |           |     |           |
  +--------+     +-----------+     +-----------+

  Step 2: Operator promotes Follower 1

  +--------+     +-----------+     +-----------+
  |OLD      |     |NEW LEADER |     |FOLLOWER 2 |
  |LEADER   |     |(promoted) |     |           |
  | (dead)  |     |           |     |           |
  +--------+     +-----+-----+     +-----------+
                        |                |
                        +----Replicates--+

  Step 3: Reconfigure clients to point to new leader
```

**Pros:** Lower risk of mistakes, operator can verify state
**Cons:** Slow (minutes to hours of downtime), requires on-call staff

### Automatic Failover

The system detects the failure and promotes a follower without human intervention. This is faster but riskier.

```
  Automatic Failover Flow:

  +------------------+
  | Health Monitor   |
  | checks every 5s  |
  +--------+---------+
           |
           v
  +------------------+
  | Leader missed    |
  | 3 health checks? |
  +--------+---------+
           | YES
           v
  +------------------+
  | Select best      |
  | follower         |
  | (most up-to-date)|
  +--------+---------+
           |
           v
  +------------------+
  | Promote follower |
  | to leader        |
  +--------+---------+
           |
           v
  +------------------+
  | Update routing   |
  | (DNS / config)   |
  +--------+---------+
           |
           v
  +------------------+
  | Other followers  |
  | follow new leader|
  +------------------+
```

**Pros:** Fast recovery (seconds to minutes), no human needed
**Cons:** Risk of false positives, potential data loss, split-brain risk

### Challenges of Automatic Failover

1. **False Positives**: The leader might be slow due to a temporary network issue, not actually dead. If the system promotes a follower too quickly, you now have two leaders (split-brain).

2. **Data Loss**: If the old leader had unreplicated writes (asynchronous replication), those writes are lost when a follower takes over.

3. **Stale Reads**: The promoted follower might be behind the old leader, serving slightly old data until it catches up.

---

## The Split-Brain Problem

Split-brain is one of the most dangerous situations in distributed databases. It occurs when two servers both believe they are the leader and accept writes independently.

```
  SPLIT-BRAIN SCENARIO

  Network partition splits the cluster:

       Network Partition
            |||
  +---------|||----------+
  |         |||          |
  | +------+|||+------+  |
  | |LEADER|||||LEADER|  |   <-- TWO LEADERS!
  | |  A   |||||  B   |  |
  | +---+--+|||+--+---+  |
  |     |   |||   |      |
  |  +--+-- |||--++--+   |
  |  |F1|F2||||F3||F4|   |
  |  +--+--+|||+-+--++   |
  |         |||          |
  +---------|||----------+

  Leader A accepts: UPDATE price = $10
  Leader B accepts: UPDATE price = $15

  When network heals: WHICH PRICE IS CORRECT?
```

### Why Split-Brain Is Dangerous

- Two copies of data diverge, and merging them is hard or impossible
- Clients connected to different leaders see different data
- Financial systems could process duplicate transactions
- Auto-incrementing IDs could produce duplicates

### How to Prevent Split-Brain

**1. Quorum-Based Decisions**

A server can only become leader if a majority of nodes agree. Since a majority can only exist on one side of a partition, only one leader can emerge.

```
  5-node cluster: Need 3 votes to be leader

  Partition:
  Side A: 3 nodes -> CAN elect leader (has majority)
  Side B: 2 nodes -> CANNOT elect leader (no majority)
```

**2. Fencing (STONITH)**

When a new leader is promoted, the old leader is forcefully shut down. STONITH stands for "Shoot The Other Node In The Head."

**3. Lease-Based Leadership**

The leader holds a time-limited lease. If it cannot renew the lease (because of a network partition), it must step down. Only one server can hold the lease at a time.

**4. External Coordination Service**

Use a system like ZooKeeper or etcd to manage leader election. These systems are designed to handle exactly this kind of problem.

---

## Replication in Practice

### MySQL Replication

MySQL uses binary log (binlog) replication. The leader writes all changes to the binary log, and followers read from it.

```
  MySQL Replication Architecture

  +------------------+
  |     LEADER       |
  |                  |
  | +-----+ +-----+ |
  | | InnoDB| |Binlog| |
  | |Engine| | Log | |
  | +-----+ +--+--+ |
  +-------------|----+
                |
        +-------+-------+
        |               |
        v               v
  +-----------+   +-----------+
  | FOLLOWER1 |   | FOLLOWER2 |
  | +-------+ |   | +-------+ |
  | |Relay  | |   | |Relay  | |
  | |Log    | |   | |Log    | |
  | +---+---+ |   | +---+---+ |
  |     |     |   |     |     |
  | +---v---+ |   | +---v---+ |
  | |InnoDB | |   | |InnoDB | |
  | |Engine | |   | |Engine | |
  | +-------+ |   | +-------+ |
  +-----------+   +-----------+
```

### PostgreSQL Replication

PostgreSQL uses Write-Ahead Log (WAL) shipping. The leader streams WAL records to followers.

### MongoDB Replication

MongoDB uses replica sets with automatic leader election. If the primary fails, the remaining members vote to elect a new primary.

---

## Trade-Offs

| Decision | Option A | Option B |
|---|---|---|
| Topology | Leader-Follower (simple, no conflicts) | Leader-Leader (multi-region writes, complex) |
| Replication Mode | Synchronous (safe, slow) | Asynchronous (fast, risk of data loss) |
| Failover | Manual (safe, slow recovery) | Automatic (fast recovery, risk of split-brain) |
| Number of Replicas | Few (less overhead, limited read scaling) | Many (better read scaling, more lag management) |
| Consistency | Strong (correct but slow) | Eventual (fast but stale reads possible) |

---

## Common Mistakes

1. **Using multi-master replication without handling conflicts.** If two leaders accept conflicting writes, data corruption follows. Always have a conflict resolution strategy.

2. **Ignoring replication lag in application code.** Your application must handle the case where a read replica returns stale data. Do not assume followers are always up to date.

3. **No monitoring on replication lag.** If lag grows, reads become increasingly stale. Set up alerts when lag exceeds acceptable thresholds.

4. **Treating failover as fully automatic and forgetting about it.** Even with automatic failover, you need runbooks, testing, and monitoring. Simulate failures regularly.

5. **Not testing failover before you need it.** The worst time to discover your failover does not work is during an actual outage. Practice with chaos engineering.

---

## Best Practices

1. **Start with leader-follower replication.** It covers the vast majority of use cases and avoids the complexity of multi-master conflict resolution.

2. **Use semi-synchronous replication for important data.** At least one follower should confirm writes synchronously to prevent data loss.

3. **Route read-after-write queries to the leader.** When a user writes data and immediately reads it back, send that read to the leader to avoid confusion from replication lag.

4. **Monitor replication lag continuously.** Set alerts for lag exceeding your acceptable threshold (often 1 to 5 seconds for most applications).

5. **Test failover regularly.** Schedule periodic failover drills. Netflix popularized this with Chaos Monkey, which randomly terminates instances in production.

6. **Use connection pooling and routing layers.** Tools like ProxySQL (MySQL) or pgBouncer (PostgreSQL) can automatically route reads to replicas and writes to the leader.

7. **Plan for cross-region replication latency.** A replica in another continent will always have higher lag. Design your application to tolerate this.

---

## Quick Summary

Database replication keeps copies of your data on multiple servers. Leader-follower replication is the most common pattern: one server handles writes, and followers handle reads. Leader-leader replication allows writes on multiple servers but introduces conflict resolution challenges. Synchronous replication guarantees data safety at the cost of speed; asynchronous replication is faster but risks data loss. Failover promotes a follower when the leader fails. The split-brain problem occurs when two servers think they are the leader, and it is prevented using quorums, fencing, or coordination services.

---

## Key Points

- Replication provides high availability, read scaling, and geographic distribution
- Leader-follower is simpler and avoids write conflicts; leader-leader supports multi-region writes but requires conflict resolution
- Synchronous replication guarantees follower has the data; asynchronous is faster but can lose data
- Replication lag means followers may serve stale data; use read-after-write consistency for user's own data
- Failover can be manual (safe, slow) or automatic (fast, risky)
- Split-brain means two leaders accepting writes independently, causing data divergence
- Semi-synchronous replication is a practical middle ground for most production systems

---

## Practice Questions

1. Your e-commerce application writes 100 orders per second and serves 10,000 product page views per second. You currently have a single database. How would you use replication to handle this load? Which topology would you choose and why?

2. A user updates their profile picture and immediately sees the old picture on their profile page. What is happening, and how would you fix it?

3. Your database cluster has one leader and four followers with asynchronous replication. The leader crashes and has 30 seconds of unreplicated writes. What are your options, and what are the trade-offs of each?

4. You are designing a system that operates in three regions: US, Europe, and Asia. Each region needs low-latency writes. Would you use leader-follower or leader-leader replication? What challenges would you face?

5. Explain why the split-brain problem is especially dangerous for a banking application. How would you prevent it?

---

## Exercises

**Exercise 1: Design a Replication Strategy**

You are building a social media platform with 10 million daily active users. The read-to-write ratio is 100:1. Users are distributed 60% in North America, 30% in Europe, and 10% in Asia. Design a replication topology. Draw the architecture, specify synchronous vs asynchronous for each link, and explain your failover strategy.

**Exercise 2: Replication Lag Simulation**

Imagine you have a leader and two followers. The leader processes writes at 1,000 per second. Follower A can apply 800 writes per second. Follower B can apply 1,200 writes per second. After 10 minutes of continuous operation, how far behind is Follower A? What would you do about it?

**Exercise 3: Failover Runbook**

Write a step-by-step runbook for handling a leader failure in a leader-follower setup with three followers. Include: how to detect the failure, how to choose which follower to promote, how to handle unreplicated writes, how to reconfigure the remaining followers, and how to verify the system is healthy after failover.

---

## What Is Next?

Now that you understand how to replicate data across multiple servers, the next question is: what happens when a single database grows so large that even the leader cannot handle all the writes or store all the data? The answer is **database sharding**, which splits your data across multiple independent databases. In the next chapter, you will learn how to partition data, choose a shard key, and handle the unique challenges that sharding introduces.
