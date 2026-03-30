# Chapter 12: Consistent Hashing

## What You Will Learn

- Why simple modular hashing breaks down when servers are added or removed
- How consistent hashing solves this problem using a hash ring
- The clock analogy for understanding the hash ring
- Virtual nodes and why they are essential for even distribution
- A step-by-step walkthrough with ASCII ring diagrams
- Real-world use cases: DynamoDB, Cassandra, CDN routing, load balancing
- How to handle server failures and additions gracefully
- Trade-offs and alternatives to consistent hashing

## Why This Chapter Matters

Whenever you distribute data across multiple servers -- whether it is a distributed cache, a sharded database, or a CDN -- you need a way to decide which server handles which piece of data. The naive approach (modular hashing) works until you add or remove a server, at which point nearly all your data needs to be moved. This is catastrophic at scale.

Consistent hashing is the algorithm that solves this problem. It minimizes data movement when servers change. It is used by almost every major distributed system: Amazon DynamoDB, Apache Cassandra, Akamai CDN, Discord, and many more.

If you understand consistent hashing, you understand the foundation of data distribution in distributed systems.

---

## 12.1 The Problem with Modular Hashing

The simplest way to assign data to servers is modular hashing: take the hash of the key and compute `hash(key) % number_of_servers`.

### How Modular Hashing Works

```
MODULAR HASHING:

  3 servers: Server 0, Server 1, Server 2

  hash("user_A") = 7    -->  7 % 3 = 1  --> Server 1
  hash("user_B") = 12   --> 12 % 3 = 0  --> Server 0
  hash("user_C") = 5    -->  5 % 3 = 2  --> Server 2
  hash("user_D") = 9    -->  9 % 3 = 0  --> Server 0
  hash("user_E") = 14   --> 14 % 3 = 2  --> Server 2
  hash("user_F") = 3    -->  3 % 3 = 0  --> Server 0

  Server 0: user_B, user_D, user_F
  Server 1: user_A
  Server 2: user_C, user_E
```

This works well with a fixed number of servers. But what happens when you add a server?

### The Catastrophe: Adding a Server

```
ADDING SERVER 3 (now 4 servers):

  hash("user_A") = 7    -->  7 % 4 = 3  --> Server 3  (was 1!)
  hash("user_B") = 12   --> 12 % 4 = 0  --> Server 0  (same)
  hash("user_C") = 5    -->  5 % 4 = 1  --> Server 1  (was 2!)
  hash("user_D") = 9    -->  9 % 4 = 1  --> Server 1  (was 0!)
  hash("user_E") = 14   --> 14 % 4 = 2  --> Server 2  (same)
  hash("user_F") = 3    -->  3 % 4 = 3  --> Server 3  (was 0!)

  MOVED:
    user_A: Server 1 --> Server 3  MOVED
    user_B: Server 0 --> Server 0  stayed
    user_C: Server 2 --> Server 1  MOVED
    user_D: Server 0 --> Server 1  MOVED
    user_E: Server 2 --> Server 2  stayed
    user_F: Server 0 --> Server 3  MOVED

  4 out of 6 keys moved! That is 67%.

  With millions of cache keys, this means:
  - 67% cache miss rate (data is on the wrong server)
  - Massive database load as cache repopulates
  - Potential system outage
```

### The Math Is Brutal

When you go from N servers to N+1 servers with modular hashing:

```
Fraction of keys that must move ≈ N / (N+1)

  3 --> 4 servers: ~75% of keys move
  9 --> 10 servers: ~90% of keys move
  99 --> 100 servers: ~99% of keys move

  The more servers you have, the WORSE it gets!
```

This is unacceptable in a production system. You need a way to add or remove servers while moving as few keys as possible. That is exactly what consistent hashing does.

---

## 12.2 Consistent Hashing: The Hash Ring

Consistent hashing maps both servers and keys onto a circular ring (a "hash ring"). Each key is assigned to the nearest server on the ring, going clockwise.

### The Clock Analogy

Think of a clock face. The hours 1 through 12 are positions on the ring. Servers are placed at specific positions on the clock. Each key is hashed to a position on the clock, and it is assigned to the next server you encounter going clockwise.

```
THE HASH RING (Clock Analogy):

  Imagine the ring as a clock with positions 0 to 359 (degrees).

  Servers are placed at specific positions:
    Server A at position 90   (3 o'clock)
    Server B at position 210  (7 o'clock)
    Server C at position 330  (11 o'clock)

                    0 / 360
                      |
                  330 |
               C *    |
              /       |
            /         |
          /           |
  270 ---             +--- 90   * A
          \           |
            \         |
              \       |
               *      |
                 210  |
                  B   |
                      |
                    180

  How keys are assigned:
    hash("user_1") = 50   --> Clockwise to A (90)
    hash("user_2") = 120  --> Clockwise to B (210)
    hash("user_3") = 250  --> Clockwise to C (330)
    hash("user_4") = 340  --> Clockwise to A (90)*
    hash("user_5") = 100  --> Clockwise to B (210)

    * 340 passes 360/0 and the next server is A at 90
```

### Step-by-Step: How It Works

```
STEP 1: Create the ring

  The ring represents the full range of the hash function.
  For example, if using SHA-256, the ring goes from 0 to 2^256.
  We will use 0-359 for simplicity.

      0
      |
  330 *C           * A  90
      |           |
      |           |
      |           |
  270 +-----------+ 180
      |
      * B
      210


STEP 2: Place servers on the ring

  Hash each server's identifier to get its position:
    hash("Server_A") = 90
    hash("Server_B") = 210
    hash("Server_C") = 330


STEP 3: Place keys on the ring

  Hash each key to get its position:
    hash("key1") = 50
    hash("key2") = 150
    hash("key3") = 250

          0
          |
     k1 . |
    330 *C |          * A  90
          |         |
          |  . k2   |
          | 150     |
    270 --+---------+-- 180
          |
     k3 . |
     250  * B
          210


STEP 4: Assign keys to servers

  Walk clockwise from each key to find the first server:
    key1 (50)  --> clockwise --> Server A (90)
    key2 (150) --> clockwise --> Server B (210)
    key3 (250) --> clockwise --> Server C (330)

  Server A: key1
  Server B: key2
  Server C: key3
```

---

## 12.3 Adding and Removing Servers

The magic of consistent hashing is what happens when servers change.

### Adding a Server

```
ADDING SERVER D at position 150:

  BEFORE:                          AFTER:
       0                                0
       |                                |
  330 *C     * A 90               330 *C     * A 90
       |     |                         |     |
       |     |                         |  *D |
       |     |                         | 150 |
  270 -+-----+- 180              270 --+-----+-- 180
       |                               |
       *B                              *B
      210                             210

  Keys reassigned:
    key1 (50)  --> Still Server A (90)    NO CHANGE
    key2 (150) --> Now Server D (150)     MOVED (was B)
    key3 (250) --> Still Server C (330)   NO CHANGE

  Only key2 moved! (1 out of 3 keys = 33%)

  In general, when adding a server with N existing servers:
    Only K/N keys move (where K = total keys)
    That is 1/N of all keys, which is the MINIMUM possible.
```

### Removing a Server

```
REMOVING SERVER B (at position 210):

  BEFORE:                          AFTER:
       0                                0
       |                                |
  330 *C     * A 90               330 *C     * A 90
       |     |                         |     |
       |     |                         |     |
       |     |                         |     |
  270 -+-----+- 180              270 --+-----+-- 180
       |                               |
       *B  <-- removed                 |
      210                              |

  Keys reassigned:
    key1 (50)  --> Still Server A (90)    NO CHANGE
    key2 (150) --> Now Server C (330)     MOVED (was B)
    key3 (250) --> Now Server C (330)     MOVED (was B)

  Only keys that were on Server B moved to the
  next server clockwise (Server C).
  Other keys are unaffected.
```

### Comparison: Modular vs Consistent Hashing

```
KEYS MOVED WHEN ADDING 1 SERVER:

+------------------+-----------------------+-----------------------+
| Total Servers    | Modular Hashing       | Consistent Hashing    |
|                  | (keys moved)          | (keys moved)          |
+------------------+-----------------------+-----------------------+
| 3 --> 4          | ~75%                  | ~25%                  |
| 9 --> 10         | ~90%                  | ~10%                  |
| 99 --> 100       | ~99%                  | ~1%                   |
| 999 --> 1000     | ~99.9%               | ~0.1%                 |
+------------------+-----------------------+-----------------------+

Consistent hashing: Only K/N keys move (minimal disruption)
Modular hashing:    ~N/(N+1) keys move (catastrophic at scale)
```

---

## 12.4 The Problem with Basic Consistent Hashing

Basic consistent hashing has a serious flaw: **uneven distribution**. With only a few servers, the ring segments are likely to be very unequal in size, meaning some servers handle far more keys than others.

```
UNEVEN DISTRIBUTION:

  Imagine 3 servers that happen to hash close together:

           0
           |
      340 *C
      350 |*A
           |  *B  20
           |
  270 -----+----- 90
           |
           |
           |
           |
          180

  Server A handles: keys from 350 to 20  (30 degrees)
  Server B handles: keys from 20 to 340  (320 degrees!)
  Server C handles: keys from 340 to 350 (10 degrees)

  Server B handles ~80% of all keys!
  Servers A and C are nearly idle.
  This defeats the purpose of distributing load.
```

The solution is **virtual nodes**.

---

## 12.5 Virtual Nodes

Instead of placing each server at one position on the ring, place each server at multiple positions. Each position is called a **virtual node** (vnode). A server with 100 virtual nodes appears at 100 different positions on the ring.

### How Virtual Nodes Work

```
VIRTUAL NODES:

  Instead of:
    hash("Server_A") --> 1 position

  Use:
    hash("Server_A_1") --> position 45
    hash("Server_A_2") --> position 120
    hash("Server_A_3") --> position 200
    hash("Server_A_4") --> position 310

  Server A now "owns" 4 segments of the ring.


  WITH 4 VIRTUAL NODES PER SERVER (3 servers = 12 vnodes):

  Server A vnodes: A1(45), A2(120), A3(200), A4(310)
  Server B vnodes: B1(30), B2(95),  B3(170), B4(280)
  Server C vnodes: C1(60), C2(150), C3(230), C4(345)

           0
           |
      C4.345  B1.30
           | A1.45
      A4.310  C1.60
           |  B2.95
           | A2.120
  270 -----+----- 90
           | C2.150
           | B3.170
           |A3.200
           |C3.230
           |B4.280
          180

  Now the ring is much more evenly divided!
  Each server handles roughly 1/3 of the keys.
```

### Why Virtual Nodes Work

```
DISTRIBUTION WITH DIFFERENT VNODE COUNTS:

  +---------------------+----------------------------------+
  | VNodes per Server   | Load Distribution                |
  +---------------------+----------------------------------+
  | 1 (no vnodes)       | Highly uneven (10x difference)   |
  | 10                  | Moderately even (2-3x difference)|
  | 100                 | Very even (~10% variation)        |
  | 200                 | Nearly perfect (~5% variation)    |
  +---------------------+----------------------------------+

  More virtual nodes = more even distribution
  But also more memory to store the ring
```

### Virtual Nodes and Heterogeneous Servers

Virtual nodes also let you handle servers with different capacities. A powerful server gets more virtual nodes and handles more keys.

```
HETEROGENEOUS SERVERS:

  Server A: 16 GB RAM --> 100 virtual nodes
  Server B: 32 GB RAM --> 200 virtual nodes
  Server C: 64 GB RAM --> 400 virtual nodes

  Server C handles ~4x the keys of Server A,
  which matches its ~4x capacity.
```

---

## 12.6 Step-by-Step Example

Let us walk through a complete example with key operations.

### Initial Setup

```
SETUP: 3 servers, 3 virtual nodes each = 9 ring positions

  hash("A-1")=10,  hash("A-2")=120, hash("A-3")=240
  hash("B-1")=50,  hash("B-2")=160, hash("B-3")=300
  hash("C-1")=80,  hash("C-2")=200, hash("C-3")=330

  Ring (sorted positions):
  10(A), 50(B), 80(C), 120(A), 160(B), 200(C), 240(A), 300(B), 330(C)

       0
       |
  330(C)  10(A)
       |   50(B)
  300(B)   80(C)
       |  120(A)
       |  160(B)
  240(A)  200(C)
       |
      180
```

### Assigning Keys

```
  hash("order_1") = 15   --> Clockwise to 50(B)  --> Server B
  hash("order_2") = 90   --> Clockwise to 120(A) --> Server A
  hash("order_3") = 210  --> Clockwise to 240(A) --> Server A
  hash("order_4") = 310  --> Clockwise to 330(C) --> Server C
  hash("order_5") = 5    --> Clockwise to 10(A)  --> Server A
  hash("order_6") = 155  --> Clockwise to 160(B) --> Server B

  Result:
    Server A: order_2, order_3, order_5
    Server B: order_1, order_6
    Server C: order_4
```

### Adding Server D

```
  New virtual nodes:
  hash("D-1")=70, hash("D-2")=190, hash("D-3")=260

  Updated ring (sorted):
  10(A), 50(B), 70(D), 80(C), 120(A), 160(B), 190(D),
  200(C), 240(A), 260(D), 300(B), 330(C)

  Re-evaluate affected keys:
  hash("order_1") = 15  --> 50(B)  --> Server B  (unchanged)
  hash("order_2") = 90  --> 120(A) --> Server A  (unchanged)
  hash("order_3") = 210 --> 240(A) --> Server A  (unchanged)
  hash("order_4") = 310 --> 330(C) --> Server C  (unchanged)
  hash("order_5") = 5   --> 10(A)  --> Server A  (unchanged)
  hash("order_6") = 155 --> 160(B) --> Server B  (unchanged)

  In this example, no keys moved! This is because D's
  virtual nodes landed in positions that did not "steal"
  any existing key assignments. In practice, about K/N
  keys would move (where N is the new total server count).
```

### Server B Fails

```
  Remove all of B's virtual nodes: 50, 160, 300

  Updated ring:
  10(A), 70(D), 80(C), 120(A), 190(D), 200(C),
  240(A), 260(D), 330(C)

  Re-evaluate keys that were on Server B:
  hash("order_1") = 15  --> was 50(B) --> now 70(D) --> Server D
  hash("order_6") = 155 --> was 160(B)--> now 190(D)--> Server D

  Only keys on Server B moved. All other keys stay.

  Keys that were on B are distributed to the next
  servers clockwise from B's old positions, which
  means they spread across D, C, and A -- not all
  dumped on one server.
```

---

## 12.7 Real-World Usage

### Amazon DynamoDB

DynamoDB uses consistent hashing to distribute data across storage nodes. Each table's partition key is hashed to determine which node stores it. When nodes are added or removed, only a fraction of partitions are rebalanced.

```
DYNAMODB PARTITIONING:

  Table: Orders
  Partition Key: order_id

  hash("order_001") --> Node 3
  hash("order_002") --> Node 1
  hash("order_003") --> Node 5

  When Node 4 is added:
  Only keys in the ring segment "taken over" by
  Node 4 are moved. Other keys stay on their nodes.
```

### Apache Cassandra

Cassandra uses consistent hashing as its core data distribution mechanism. Each node is assigned a range of tokens on the ring. Data is placed on the node that owns the token range for its partition key.

```
CASSANDRA TOKEN RING:

  Node A: owns tokens 0 - 85
  Node B: owns tokens 86 - 170
  Node C: owns tokens 171 - 255

  Cassandra also uses virtual nodes (vnodes) by default.
  Each node owns 256 small token ranges instead of 1 large one.
  This makes rebalancing faster and load distribution more even.
```

### CDN Routing

CDNs use consistent hashing to decide which edge server caches which content. When an edge server goes down, only its content needs to be re-routed to other edges. Other content is unaffected.

```
CDN CONSISTENT HASHING:

  URL: /images/cat.jpg
  hash("/images/cat.jpg") --> Edge Server in Tokyo

  Tokyo edge goes down:
  hash("/images/cat.jpg") --> Next server clockwise
                          --> Edge Server in Seoul

  All other URLs continue to be served by their
  original edge servers. No mass cache invalidation.
```

### Discord

Discord uses consistent hashing to distribute chat messages and user state across its backend servers. When servers are added to handle growth, only a fraction of users are moved to the new servers.

### Load Balancers

Some load balancers use consistent hashing to route requests. This ensures that the same user always hits the same backend server (session affinity) while minimizing disruption when servers change.

```
CONSISTENT HASH LOAD BALANCING:

  hash(user_session_id) --> Backend Server

  Advantage over round-robin:
  - Same user always hits same server (good for caching)
  - Adding/removing servers only affects some users
  - Better cache hit ratios on backend servers
```

---

## 12.8 Implementation Details

### Choosing a Hash Function

The hash function must produce uniformly distributed values. Common choices:

```
+------------------+------------------+--------------------+
| Hash Function    | Speed            | Distribution       |
+------------------+------------------+--------------------+
| MD5              | Medium           | Excellent          |
| SHA-1            | Medium           | Excellent          |
| MurmurHash       | Fast             | Very good          |
| xxHash           | Very fast        | Very good          |
| CRC32            | Very fast        | Acceptable         |
+------------------+------------------+--------------------+

MurmurHash and xxHash are the most common choices for
consistent hashing because they are fast and have good
distribution without the overhead of cryptographic hashes.
```

### Data Structure for the Ring

The ring is typically implemented as a sorted array or a balanced binary search tree (like a red-black tree or a TreeMap in Java).

```
RING LOOKUP:

  Sorted array of positions: [10, 50, 80, 120, 160, 200, 240, 300, 330]
  Each position maps to a server: [A, B, C, A, B, C, A, B, C]

  To find the server for a key:
  1. Compute hash(key) = position
  2. Binary search for the smallest position >= key's position
  3. If no position >= key's position, wrap around to the first position

  Time complexity: O(log N) where N = number of virtual nodes
  Space complexity: O(N)

  With 3 servers and 200 vnodes each = 600 positions
  Binary search on 600 elements is very fast (~10 comparisons)
```

### Replication with Consistent Hashing

Many distributed systems replicate data to multiple servers for fault tolerance. With consistent hashing, data is replicated to the next N servers clockwise on the ring.

```
REPLICATION (replicas = 3):

  hash("key1") = 85

  Ring: ... 80(C), 120(A), 160(B), 200(C), ...

  Primary:  Server C (position 80 is closest but we go to next: 120? No, 80 is before 85)
  Actually: Walk clockwise from 85:
    Replica 1: 120 --> Server A  (primary)
    Replica 2: 160 --> Server B
    Replica 3: 200 --> Server C

  Data is stored on A, B, and C.
  If Server A fails, data is still available on B and C.

  With virtual nodes, you must ensure replicas are on
  DIFFERENT physical servers, not just different vnodes
  of the same server.
```

---

## 12.9 Alternatives and Variations

### Jump Consistent Hash

A simpler algorithm that produces balanced distribution without a ring. It maps keys to buckets using a deterministic sequence of random jumps.

**Pros:** Very fast, zero memory, perfectly balanced
**Cons:** Only works when adding/removing servers at the end (cannot remove a server from the middle)

### Rendezvous Hashing (Highest Random Weight)

Each key is assigned to the server that produces the highest hash value for that key-server combination.

```
RENDEZVOUS HASHING:

  For key "user_1":
    hash("user_1" + "Server_A") = 0.72
    hash("user_1" + "Server_B") = 0.31
    hash("user_1" + "Server_C") = 0.89  <-- Highest!
    --> Assign to Server C

  For key "user_2":
    hash("user_2" + "Server_A") = 0.65  <-- Highest!
    hash("user_2" + "Server_B") = 0.42
    hash("user_2" + "Server_C") = 0.18
    --> Assign to Server A
```

**Pros:** Simple, no ring data structure, good distribution
**Cons:** Must compute hash for every server on every lookup (O(N) per lookup)

### Comparison

```
+---------------------+----------+---------+----------+---------+
| Algorithm           | Lookup   | Memory  | Balance  | Remove  |
|                     | Speed    |         |          | Any Node|
+---------------------+----------+---------+----------+---------+
| Consistent Hashing  | O(log N) | O(N)    | Good     | Yes     |
| (with vnodes)       |          | (vnodes)|  (vnodes)|         |
+---------------------+----------+---------+----------+---------+
| Jump Hash           | O(log N) | O(1)    | Perfect  | No*     |
+---------------------+----------+---------+----------+---------+
| Rendezvous Hash     | O(N)     | O(1)    | Good     | Yes     |
+---------------------+----------+---------+----------+---------+

* Jump Hash only supports adding/removing at the end
```

---

## Common Mistakes

1. **Using consistent hashing without virtual nodes.** Without virtual nodes, the distribution is extremely uneven. Always use virtual nodes (100-200 per server is a common starting point).

2. **Not accounting for heterogeneous servers.** If servers have different capacities, assign proportionally more virtual nodes to more powerful servers.

3. **Replicating to virtual nodes of the same server.** When replicating, walk clockwise but skip virtual nodes that belong to a physical server you have already replicated to.

4. **Using a poor hash function.** A hash function with clustering (non-uniform output) defeats the purpose of consistent hashing. Use MurmurHash or xxHash.

5. **Ignoring hot keys.** Consistent hashing distributes keys evenly, but it does not solve the problem of one key being extremely popular (e.g., a viral tweet). You need additional mechanisms (replication, caching) for hot keys.

6. **Too few virtual nodes.** With fewer than 100 virtual nodes per server, load imbalance can be significant. More virtual nodes improve balance but use more memory.

7. **Not handling ring changes atomically.** When adding or removing servers, all nodes must agree on the new ring configuration at the same time. Otherwise, different nodes route the same key to different servers.

---

## Best Practices

1. **Use 100-200 virtual nodes per server.** This provides good balance without excessive memory usage.

2. **Use MurmurHash or xxHash** for fast, well-distributed hashing.

3. **Store the ring in a sorted data structure** (TreeMap, sorted array) for efficient O(log N) lookups.

4. **Replicate data to N distinct physical servers,** not just N positions on the ring.

5. **Handle hot keys separately.** For extremely popular keys, use caching or split the key across multiple sub-keys.

6. **Use a coordination service** (ZooKeeper, etcd, Consul) to maintain the ring configuration and ensure all nodes have a consistent view.

7. **Scale virtual nodes with server capacity.** More powerful servers should have more virtual nodes to receive proportionally more traffic.

8. **Monitor key distribution.** Periodically check that keys are distributed evenly across servers. Adjust virtual node counts if needed.

---

## Quick Summary

Modular hashing (hash % N) is simple but catastrophic when servers change: nearly all keys must be remapped. Consistent hashing solves this by placing both servers and keys on a circular hash ring. Each key is assigned to the first server encountered clockwise. When a server is added or removed, only K/N keys move (where K is total keys and N is total servers), which is the theoretical minimum. Virtual nodes (multiple ring positions per server) solve the uneven distribution problem by spreading each server's responsibility across many small segments. Real-world systems like DynamoDB, Cassandra, and CDN routers all use consistent hashing. Alternatives include jump consistent hash (simple, but limited) and rendezvous hashing (no ring, but O(N) lookup).

---

## Key Points

- Modular hashing causes ~N/(N+1) of keys to move when a server is added -- catastrophic at scale
- Consistent hashing uses a ring where keys are assigned to the nearest server clockwise
- Adding or removing a server moves only K/N keys (the minimum possible disruption)
- Virtual nodes (100-200 per server) are essential for even distribution across servers
- Heterogeneous servers get proportionally more virtual nodes based on their capacity
- Used by DynamoDB, Cassandra, CDN routers, Discord, and many distributed caches
- Use MurmurHash or xxHash for fast, uniform hash distribution
- Replication works by assigning data to the next N distinct physical servers on the ring

---

## Practice Questions

1. You have 5 cache servers and 1 million keys distributed using modular hashing. One server fails and you remove it. How many keys need to be remapped? Now answer the same question for consistent hashing with virtual nodes. What is the practical impact on cache hit ratio in each case?

2. You are running a distributed cache with consistent hashing and 3 servers. Server A has 16GB RAM, Server B has 32GB RAM, and Server C has 64GB RAM. How would you use virtual nodes to ensure each server handles traffic proportional to its capacity? How many virtual nodes would you assign to each?

3. Explain why consistent hashing alone does not solve the hot key problem. Give an example of a hot key in a social media system and propose a solution that works alongside consistent hashing.

4. Compare consistent hashing, jump hash, and rendezvous hashing for a CDN with 200 edge servers that occasionally adds and removes servers. Which would you choose and why?

5. In a Cassandra cluster using consistent hashing with virtual nodes, a new node is added. Describe step by step what happens to the data: which data moves, how it is transferred, and how the cluster maintains availability during the transition.

---

## Exercises

**Exercise 1: Build a Hash Ring**
Implement a consistent hash ring in pseudocode. Support these operations: `add_server(server_id, num_vnodes)`, `remove_server(server_id)`, and `get_server(key)`. Use a sorted array for the ring. Show the state of the ring after each operation for a scenario with 3 servers being added and then 1 being removed.

**Exercise 2: Distribution Analysis**
Using 3 servers and 1000 randomly generated keys, calculate the number of keys per server with: (a) modular hashing, (b) consistent hashing with 1 vnode per server, (c) consistent hashing with 10 vnodes per server, (d) consistent hashing with 200 vnodes per server. Show the standard deviation of keys per server for each approach.

**Exercise 3: Replication on the Ring**
Design a replication scheme using consistent hashing for a distributed key-value store with a replication factor of 3. Draw the hash ring with 4 servers (3 vnodes each). Show which servers hold each replica for 5 different keys. Handle the case where consecutive vnodes belong to the same physical server (skip them for replica placement).

---

## What Is Next?

Consistent hashing is a fundamental building block for distributed systems. It answers the question "which server handles this data?" In the next chapter, you will learn about the CAP theorem, which answers a deeper question: "what guarantees can a distributed system provide?" The CAP theorem explains the fundamental trade-offs between consistency, availability, and partition tolerance -- the constraints that every distributed system must navigate.
