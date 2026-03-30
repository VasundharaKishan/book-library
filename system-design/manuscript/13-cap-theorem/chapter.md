# Chapter 13: The CAP Theorem

## What You Will Learn

- What the CAP theorem is and why it matters for distributed systems
- The meaning of Consistency, Availability, and Partition Tolerance
- Why you can only guarantee two out of three properties at a time
- The difference between CP and AP systems with real examples
- How the PACELC extension adds nuance to the CAP theorem
- Strong consistency vs eventual consistency and when to use each
- How real databases like DynamoDB, Cassandra, MongoDB, and PostgreSQL make their trade-offs

## Why This Chapter Matters

Every distributed system you design will force you to make a choice: what happens when part of your network fails? Do you show users stale data to keep things running? Or do you reject requests until the system is back in sync?

The CAP theorem is the foundation of that decision. If you skip this chapter, you will build systems that behave in ways you did not predict. You will pick databases without understanding their guarantees. And when things go wrong at 3 AM, you will not know why your system made the choices it did.

Understanding CAP is not just academic. It is the lens through which experienced engineers evaluate every distributed database, every replication strategy, and every architecture decision.

---

## The CAP Theorem Explained

In 2000, computer scientist Eric Brewer proposed a conjecture. In 2002, Seth Gilbert and Nancy Lynch proved it. The idea is simple but powerful.

In any distributed data store, you can only guarantee **two out of three** properties:

- **C** — Consistency
- **A** — Availability
- **P** — Partition Tolerance

Let us define each one clearly.

### Consistency (C)

Every read receives the most recent write or an error. All nodes in the system see the same data at the same time.

If you write "balance = $500" and then immediately read, you get $500. Not $400. Not "unknown." You get the latest value.

### Availability (A)

Every request receives a response (not an error). The system keeps working even if some nodes are slow or busy.

Note: availability here does not mean the response is the most up-to-date. It just means you get a response.

### Partition Tolerance (P)

The system continues to operate even when network communication between nodes is lost. Messages between nodes can be dropped, delayed, or lost entirely.

A partition is when two parts of your system cannot talk to each other. Think of it as a broken phone line between two offices.

---

## The Real-Life Analogy: Two Offices, One Phone Line

Imagine you run a bank with two branch offices: Office A in New York and Office B in London.

Both offices can accept deposits and withdrawals. They share customer account balances by calling each other on a single phone line after every transaction.

```
+------------------+          Phone Line          +------------------+
|   Office A       |<---------------------------->|   Office B       |
|   (New York)     |     Account Balance Sync     |   (London)       |
|                  |                              |                  |
|  Balance: $1000  |                              |  Balance: $1000  |
+------------------+                              +------------------+
```

Everything works fine when the phone line is up. A customer deposits $200 in New York, Office A calls Office B, and both update to $1200.

**Now the phone line goes down.** This is a partition.

A customer walks into Office A and deposits $200. Another customer walks into Office B and withdraws $300. Neither office can tell the other what happened.

You now have a choice:

### Choice 1: Stay Consistent (CP)

Both offices stop processing transactions until the phone line is restored. Customers are turned away. This is frustrating, but when the line comes back, the balances are correct.

"Sorry, our system is down. Please come back later."

### Choice 2: Stay Available (AP)

Both offices keep processing transactions using their local copy of the balance. Customers are happy — they can deposit and withdraw. But the balances are now different in each office:

- Office A thinks the balance is $1200
- Office B thinks the balance is $700

When the phone line comes back, you have a conflict. Which balance is correct? The answer is: neither. You need a reconciliation strategy.

### Why Not Choose CA (Consistent + Available, No Partition Tolerance)?

In a distributed system, network partitions **will happen**. Cables get cut. Switches fail. Data centers lose connectivity. You cannot choose to ignore partitions.

If all your data is on a single machine, you do not have partition tolerance to worry about — but you also do not have a distributed system. A single PostgreSQL server is effectively a CA system, but it does not help when you need to scale beyond one machine.

```
          The CAP Triangle

              C
             / \
            /   \
           /     \
          / CP  CA \
         /   or   \
        /   AP     \
       /             \
      A ------------- P

  You must pick a side.
  In distributed systems, P is mandatory.
  So the real choice is: CP or AP?
```

---

## CP Systems: Consistency Over Availability

A CP system prioritizes consistency. When a partition occurs, the system will refuse to respond rather than return potentially stale data.

### How It Works

```
Client Request: "Read balance for account #123"

+----------+          PARTITION          +----------+
| Node A   |      X  X  X  X  X         | Node B   |
| (Primary)|     Cannot reach B          | (Replica)|
|          |                             |          |
| Has the  |                             | May have |
| latest   |                             | stale    |
| write    |                             | data     |
+----------+                             +----------+
     |
     v
  Node A responds: "Error - cannot confirm consistency"
  OR
  Node A responds with latest data (if it is the primary)
```

### Real-World CP Example: Banking Systems

When you transfer $500 from your checking to your savings account, the system must ensure:

1. The $500 is deducted from checking
2. The $500 is added to savings
3. Both operations succeed or both fail
4. No one reads a state where $500 has left checking but has not arrived in savings

If there is a network issue, the bank shows you an error rather than risk showing you the wrong balance. This is CP behavior.

### CP Databases

- **MongoDB** (with majority write concern): Writes require acknowledgment from a majority of nodes. If a partition isolates the primary from the majority, the primary steps down.
- **HBase**: Uses a single master for consistency. If the master fails, the system is unavailable until a new one is elected.
- **etcd / ZooKeeper**: Used for coordination and configuration. They choose consistency because correct configuration is more important than always being available.

---

## AP Systems: Availability Over Consistency

An AP system prioritizes availability. When a partition occurs, every node keeps serving requests, even if some nodes have stale data.

### How It Works

```
Client Request: "Read post likes count"

+----------+          PARTITION          +----------+
| Node A   |      X  X  X  X  X         | Node B   |
|          |     Cannot sync data        |          |
|          |                             |          |
| Likes:   |                             | Likes:   |
| 1,042    |                             | 1,039    |
+----------+                             +----------+
     |                                        |
     v                                        v
  Responds: 1,042                    Responds: 1,039

  Both responses are "valid" even though
  they disagree. They will converge later.
```

### Real-World AP Example: Social Media Likes

When you like a post on social media, the like count might temporarily differ depending on which server handles your request. One user might see 1,042 likes while another sees 1,039.

This is acceptable. Nobody loses money. The counts will eventually converge when the partition heals.

### AP Databases

- **Cassandra**: Designed for availability. Every node can accept writes. Uses tunable consistency (you can adjust per-query).
- **DynamoDB**: By default, reads are eventually consistent. The system always responds, even during partitions.
- **CouchDB**: Designed for availability and eventual consistency. Uses multi-version concurrency control to handle conflicts.

---

## The Consistency Spectrum

Consistency is not binary. It exists on a spectrum from strong to weak.

```
Strong                                                    Weak
Consistency                                          Consistency
   |                                                      |
   v                                                      v
+--------+    +-----------+    +----------+    +----------+
| Linear-|    | Sequential|    | Causal   |    | Eventual |
| izable |    | Consistency|   | Consist. |    | Consist. |
+--------+    +-----------+    +----------+    +----------+
   |               |               |               |
   v               v               v               v
 Every read      Operations     Causally        Reads may
 sees the        appear in      related ops     return stale
 latest          some total     are ordered;    data, but
 write.          order,         unrelated ops   will converge
 Slowest.        consistent     may be out      eventually.
                 across all     of order.       Fastest.
                 clients.
```

### Strong Consistency

Every read returns the most recent write. Period. If User A writes "name = Alice" and User B reads immediately after, User B gets "Alice."

This is expensive. The system must coordinate across all nodes before acknowledging a write.

**Use when:** Financial transactions, inventory systems, anything where stale reads cause real harm.

### Eventual Consistency

If no new writes happen, all replicas will eventually converge to the same value. But "eventually" could be milliseconds or seconds — the system does not guarantee when.

**Use when:** Social media feeds, view counters, recommendation engines, DNS.

### Causal Consistency

Operations that are causally related are seen in the correct order. If User A posts a message and then User B replies to it, everyone sees the original message before the reply.

But two unrelated operations might appear in different orders to different observers.

**Use when:** Chat applications, collaborative editing, comment threads.

---

## How Real Systems Make Their Choice

No real-world system is purely CP or purely AP. Most systems let you tune the trade-off.

### DynamoDB

DynamoDB defaults to **eventual consistency** for reads (AP behavior). But you can request a **strongly consistent read** that costs more and takes longer. This lets you choose per-query.

```
+------------------+     +------------------+
|  Application     |     |  Application     |
|  (Read: eventual)|     |  (Read: strong)  |
+--------+---------+     +--------+---------+
         |                        |
         v                        v
  +------+------+          +------+------+
  | Any replica |          | Leader node |
  | can respond |          | must respond|
  | Fast, cheap |          | Slow, costly|
  +-------------+          +-------------+
```

### Cassandra

Cassandra uses **tunable consistency**. You set the consistency level per operation:

- `ONE`: Write/read from one node (fast, AP behavior)
- `QUORUM`: Write/read from majority of nodes (balanced)
- `ALL`: Write/read from all nodes (slow, CP behavior)

```
  Cassandra Tunable Consistency

  Write to 3 replicas (Replication Factor = 3)

  Consistency    Nodes that    Nodes that    Behavior
  Level          must ACK      can fail
  --------------------------------------------------------
  ONE            1             2             AP (fast)
  QUORUM         2             1             Balanced
  ALL            3             0             CP (slow)
```

The common pattern is `QUORUM` for both reads and writes. If you have 3 replicas and use QUORUM (2 of 3), you guarantee that at least one node in your read set has the latest write. This gives you strong consistency without needing ALL nodes.

### MongoDB

MongoDB uses a **primary-secondary replication** model. Writes go to the primary. By default, reads can go to secondaries (which may be slightly behind).

You can configure:
- **Write Concern**: How many nodes must acknowledge a write (e.g., `majority`)
- **Read Concern**: Whether reads must come from the primary or can come from secondaries
- **Read Preference**: Which node to read from (primary, secondary, nearest)

With `writeConcern: majority` and `readConcern: majority`, MongoDB behaves as a CP system.

### PostgreSQL

A single PostgreSQL instance is consistent and available but not partition tolerant (it is a single machine). When you add replication:

- **Synchronous replication**: The primary waits for the replica to confirm. Strong consistency, but slower and less available (CP).
- **Asynchronous replication**: The primary does not wait. Faster and more available, but replicas may be behind (AP-ish).

---

## PACELC: Beyond CAP

The CAP theorem only talks about what happens **during a partition**. But what about normal operation? That is where PACELC comes in.

**PACELC** says:

> If there is a **P**artition, choose between **A**vailability and **C**onsistency.
> **E**lse (when the system is running normally), choose between **L**atency and **C**onsistency.

```
  PACELC Decision Framework

  Is there a partition?
        |
   +----+----+
   |         |
  YES        NO
   |         |
   v         v
  PAC       ELC
  Pick:     Pick:
  A or C    L or C

  Examples:

  System       During Partition    Normal Operation    PACELC
  -------      ----------------    ----------------    ------
  DynamoDB     Availability        Latency             PA/EL
  Cassandra    Availability        Latency             PA/EL
  MongoDB      Consistency         Consistency         PC/EC
  PostgreSQL   Consistency         Consistency         PC/EC
  (sync repl.)
```

This is more useful in practice because partitions are rare. Most of the time, your system is running normally, and the real trade-off is between latency and consistency.

### PA/EL Systems (DynamoDB, Cassandra)

- During partition: Stay available, accept stale reads
- Normal operation: Prioritize low latency, serve reads from nearest replica (may be slightly stale)

### PC/EC Systems (MongoDB with majority, PostgreSQL with sync replication)

- During partition: Reject requests to stay consistent
- Normal operation: Prioritize consistency even if it means higher latency (reads may need to go to the primary)

---

## Eventual Consistency in Practice

Eventual consistency sounds scary, but it is everywhere. Here are patterns that make it work.

### Read-Your-Own-Writes

After a user writes data, ensure that **the same user** sees the updated data on subsequent reads (even if other users see stale data briefly).

```
User writes "name = Alice"
         |
         v
+--------+--------+
|    Primary       |
| name = "Alice"   |
+--------+---------+
         |
         | Replication (async)
         v
+--------+---------+
|    Replica        |
| name = "Bob"      |  <-- Still has old value
+-------------------+

Strategy: Route the user's reads to the primary
for a few seconds after a write.
```

### Conflict Resolution Strategies

When two nodes accept conflicting writes during a partition, you need a strategy:

1. **Last-Write-Wins (LWW)**: The write with the latest timestamp wins. Simple but can lose data.
2. **Merge**: Combine both writes (e.g., for shopping carts, merge items from both versions).
3. **Application-level resolution**: Show the conflict to the user and let them decide (like Git merge conflicts).

### Anti-Entropy and Repair

Background processes periodically compare data across replicas and fix differences. Cassandra calls this "anti-entropy repair." It runs in the background to ensure eventual convergence.

---

## Common Mistakes

1. **Thinking CAP means you literally pick two and ignore one.** In practice, you tune trade-offs. Systems are not purely CP or AP.

2. **Ignoring partitions because "our network is reliable."** Network partitions happen in every cloud provider, every data center, every system at scale. Design for them.

3. **Choosing strong consistency everywhere "just to be safe."** Strong consistency is expensive in latency and availability. Use it where it matters (money, inventory), not where it does not (likes, views).

4. **Confusing CAP consistency with ACID consistency.** CAP consistency means all nodes see the same data. ACID consistency means the database enforces rules (constraints, triggers). They are different concepts.

5. **Thinking eventual consistency means "inconsistent forever."** Eventual consistency means the system converges. The window of inconsistency is usually milliseconds to seconds.

---

## Best Practices

1. **Classify your data by consistency requirements.** User account balance? Strong consistency. Like count? Eventual is fine. Make deliberate choices per data type.

2. **Use tunable consistency when available.** Databases like Cassandra and DynamoDB let you choose consistency per query. Use strong reads for critical paths and eventual reads for everything else.

3. **Design for partition recovery.** Have a clear strategy for what happens when a partition heals. How do you reconcile conflicting writes?

4. **Use the PACELC model for real-world decisions.** CAP only covers partitions. PACELC also covers normal operation, which is where your system spends 99.99% of its time.

5. **Test partition behavior.** Use chaos engineering tools (like Chaos Monkey or Toxiproxy) to simulate partitions and verify your system behaves as expected.

6. **Document your consistency guarantees.** Make it clear to your team what consistency level each service provides. This prevents bugs caused by wrong assumptions.

---

## Quick Summary

The CAP theorem states that a distributed system can guarantee at most two of three properties: Consistency, Availability, and Partition Tolerance. Since partitions are unavoidable in distributed systems, the real choice is between consistency (CP) and availability (AP) during failures. The PACELC extension adds that during normal operation, the trade-off is between latency and consistency. Real systems like DynamoDB, Cassandra, and MongoDB offer tunable consistency, letting you make different choices for different data.

---

## Key Points

- The CAP theorem limits distributed systems to two of three guarantees: Consistency, Availability, and Partition Tolerance.
- Network partitions are inevitable, so the practical choice is CP (consistency) vs AP (availability).
- CP systems reject requests during partitions to maintain correctness (e.g., banking).
- AP systems serve requests during partitions but may return stale data (e.g., social media).
- Consistency exists on a spectrum: linearizable, sequential, causal, and eventual.
- PACELC extends CAP to cover normal operation: the trade-off between latency and consistency.
- Real databases (DynamoDB, Cassandra, MongoDB) offer tunable consistency levels per query.
- Eventual consistency works well with patterns like read-your-own-writes and conflict resolution.
- CAP consistency (all nodes see the same data) is different from ACID consistency (enforcing rules).

---

## Practice Questions

1. You are designing a system for an airline seat reservation. Should it be CP or AP? What happens if two users try to book the same seat during a network partition?

2. A social media platform shows post like counts. The count is slightly different for users in different regions. Is this a bug or expected behavior? What consistency model is at work?

3. Your Cassandra cluster has a replication factor of 5. You use QUORUM for both reads and writes. How many nodes must acknowledge each operation? Can you tolerate node failures?

4. Explain why a single-server PostgreSQL database does not face the CAP trade-off. What changes when you add replication?

5. Your system uses DynamoDB with eventual consistency reads. A user updates their profile and immediately refreshes the page but sees old data. How would you fix this?

---

## Exercises

### Exercise 1: Classify Real Systems

For each system below, determine whether it leans CP or AP, and explain why:

- A bank's core ledger system
- A DNS system
- A shopping cart service
- A distributed lock service (like ZooKeeper)
- A content delivery network

Think about what happens during a partition for each one.

### Exercise 2: Design a Consistency Strategy

You are building a ride-sharing application. Different parts of the system have different consistency needs:

- Driver location updates (sent every 2 seconds)
- Ride fare calculation
- Payment processing
- Rider-driver matching

For each component, choose a consistency level (strong, causal, or eventual) and justify your choice. What databases or patterns would you use?

### Exercise 3: Simulate a Partition

Set up a simple system with two data stores (even just two files on disk). Write a script that:

1. Writes data to both stores (simulating replication)
2. Simulates a partition (stop syncing)
3. Writes different data to each store
4. Restores the partition
5. Implements a reconciliation strategy (last-write-wins or merge)

Document what happens at each step and what data you end up with.

---

## What Is Next?

Now that you understand the CAP theorem and how distributed systems make consistency trade-offs, you are ready to explore how organizations structure their systems. In the next chapter, we will dive into **Microservices** — how to break a large application into smaller, independent services and the new set of challenges that approach introduces.
