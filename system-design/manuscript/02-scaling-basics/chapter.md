# Chapter 2: Scaling Basics

## What You Will Learn

- How a single server architecture works and where it breaks down
- The difference between vertical scaling (bigger machine) and horizontal scaling (more machines)
- Why stateless servers are easier to scale than stateful servers
- How to handle user sessions in a scaled environment
- When database becomes the bottleneck and what to watch for
- How to choose between scaling up and scaling out

## Why This Chapter Matters

Every successful application starts small. One server, one database, a handful of users. Then something wonderful and terrifying happens: people start using your product.

Suddenly, your single server is sweating. Response times climb. Users see errors. And you face the question that every growing system must answer: **how do we handle more load?**

Scaling is the foundation that everything else in this book builds upon. Load balancers, caches, CDNs, database replication -- they all exist to solve scaling problems. Before you can use those tools effectively, you need to understand why scaling is necessary and what your options are.

---

## 2.1 Single Server Architecture

Let us start at the beginning. The simplest possible web architecture looks like this:

```
+--------+         +---------------------------+
|        |  HTTP   |        Single Server       |
| User's | ------> |                           |
| Browser|         |  +-------+   +----------+ |
|        | <------ |  | Web   |   | Database | |
+--------+         |  | App   |-->|          | |
                    |  +-------+   +----------+ |
                    +---------------------------+
```

Everything runs on one machine:
- The web application that handles requests
- The database that stores data
- Static files (images, CSS, JavaScript)
- Maybe even a background job processor

### How It Works

1. A user types your URL into their browser
2. DNS resolves the domain name to your server's IP address
3. The browser sends an HTTP request to that IP
4. Your web application processes the request
5. It reads from or writes to the database
6. It sends back an HTML page (or JSON response)

### When One Server Is Enough

A single server can handle more than you might think:

- A modern server with 8 CPU cores and 32 GB RAM can handle thousands of concurrent connections
- If your application is well-written, one server can serve 1,000-10,000 requests per second
- For a blog, small business site, or early-stage startup with a few hundred users, this is perfectly fine

### When One Server Breaks Down

A single server has hard limits:

- **CPU saturation:** When all cores are busy, new requests wait in a queue
- **Memory exhaustion:** When RAM is full, the OS starts swapping to disk, and everything slows to a crawl
- **Disk I/O limits:** Databases need to read and write to disk, and disks have finite speed
- **Network bandwidth:** One network card can only move so much data
- **Single point of failure:** If this one server dies, everything dies

```
         Load Increasing Over Time

Requests  |                         X Server crashes
per       |                       X
second    |                    X
          |                 X
          |              X     <-- Response times
          |           X            start degrading
          |        X
          |     X
          |  X
          +----------------------------------
                     Time -->

         One server can only take so much.
```

You have two options when you hit these limits: make the server bigger, or add more servers.

---

## 2.2 Vertical Scaling (Scaling Up)

**Vertical scaling means making your existing server more powerful.**

### The "Bigger Desk" Analogy

Imagine you work at a desk and it is getting cluttered. You have papers everywhere, your monitor barely fits, and you keep knocking over your coffee.

Vertical scaling is like replacing your desk with a bigger desk. Same room, same person, just more workspace.

```
BEFORE (Small Server)           AFTER (Bigger Server)
+------------------+            +---------------------------+
|  4 CPU cores     |            |  32 CPU cores             |
|  16 GB RAM       |   ====>   |  256 GB RAM               |
|  500 GB HDD      |            |  2 TB NVMe SSD            |
|  1 Gbps network  |            |  10 Gbps network          |
+------------------+            +---------------------------+

Same architecture, more powerful hardware.
```

### How to Vertically Scale

- Add more RAM
- Upgrade to faster CPUs (more cores, higher clock speed)
- Replace HDD with SSD (or SSD with NVMe)
- Upgrade network interface
- Move to a larger cloud instance (e.g., from AWS t3.medium to r5.4xlarge)

### Advantages of Vertical Scaling

| Advantage | Why It Matters |
|-----------|---------------|
| Simple | No code changes needed. Your application does not know or care that the hardware changed. |
| No distributed complexity | One server means no network latency between components, no data synchronization issues. |
| Strong consistency | All data is in one place. No need to worry about replicas being out of sync. |
| Lower operational cost | One server is easier to monitor, maintain, and debug than many. |
| Transactions are simple | Database transactions work naturally on a single machine. |

### Limits of Vertical Scaling

| Limitation | Reality |
|-----------|---------|
| Hardware ceiling | You cannot add infinite RAM or CPUs. The biggest servers top out at a few terabytes of RAM and a few hundred cores. |
| Cost grows non-linearly | Doubling performance often costs more than double the price. A server with 256 GB RAM costs much more than twice a 128 GB server. |
| Single point of failure | No matter how powerful, it is still one machine. If it fails, everything goes down. |
| Downtime during upgrades | Changing hardware usually means shutting the server down. |
| Diminishing returns | After a certain point, adding more resources gives smaller and smaller improvements due to software bottlenecks. |

### Real-World Vertical Scaling Example

AWS EC2 instance sizes (approximate, for illustration):

```
Instance Type    vCPUs    RAM       Cost/Month
--------------------------------------------
t3.micro           2      1 GB        ~$8
t3.large           2      8 GB       ~$60
r5.xlarge          4     32 GB      ~$180
r5.4xlarge        16    128 GB      ~$720
r5.16xlarge       64    512 GB    ~$2,880
u-24tb1.metal    448     24 TB   ~$160,000

Notice how cost grows much faster than capacity.
```

---

## 2.3 Horizontal Scaling (Scaling Out)

**Horizontal scaling means adding more servers to share the work.**

### The "Hiring More Workers" Analogy

Going back to the desk analogy. Instead of buying a bigger desk, you hire more people. Each person gets their own desk. You split the work among them.

The work gets done faster, and if one person calls in sick, the others can cover.

```
BEFORE (One Server)              AFTER (Multiple Servers)

+--------+    +---------+       +--------+    +---------+
| Client |--->| Server  |       | Client |--->| Load    |
+--------+    +---------+       +--------+    | Balancer|
                                              +----+----+
                                                   |
                                        +----------+----------+
                                        |          |          |
                                   +--------+ +--------+ +--------+
                                   |Server 1| |Server 2| |Server 3|
                                   +--------+ +--------+ +--------+
```

### How Horizontal Scaling Works

1. You run multiple copies of your application on different servers
2. A **load balancer** sits in front of the servers and distributes incoming requests
3. Each server handles a portion of the traffic
4. If you need more capacity, you add more servers
5. If a server fails, the others keep working

### Advantages of Horizontal Scaling

| Advantage | Why It Matters |
|-----------|---------------|
| (Nearly) unlimited scaling | Need more capacity? Add more servers. There is no hard ceiling. |
| Fault tolerance | If one server dies, the others continue serving. Users might not even notice. |
| No downtime for scaling | Add or remove servers without shutting anything down. |
| Cost-effective | Many small servers can be cheaper than one massive server. |
| Geographic distribution | You can place servers in different regions, closer to users. |

### Challenges of Horizontal Scaling

| Challenge | Why It Is Hard |
|-----------|---------------|
| Data consistency | With data spread across servers, keeping it in sync is complex. |
| Session management | If user state lives on one server, what happens when they hit a different server? |
| Operational complexity | More servers means more to monitor, deploy to, and debug. |
| Application changes | Your code needs to be designed to run on multiple servers (stateless design). |
| Database bottleneck | Even with many app servers, they all talk to the same database. |

---

## 2.4 Vertical vs Horizontal: Side by Side

```
     VERTICAL SCALING                    HORIZONTAL SCALING
     (Scale Up)                          (Scale Out)

     +-------------+                    +-----+ +-----+ +-----+
     |             |                    |     | |     | |     |
     |   BIGGER    |                    |Small| |Small| |Small|
     |   SERVER    |                    |  1  | |  2  | |  3  |
     |             |                    |     | |     | |     |
     |             |                    +-----+ +-----+ +-----+
     +-------------+

     Like getting a                     Like hiring more
     bigger desk                        workers

     Pros:                              Pros:
     - Simple                           - No ceiling
     - No code changes                  - Fault tolerant
     - Strong consistency               - Cost effective

     Cons:                              Cons:
     - Has a ceiling                    - More complex
     - Expensive at scale               - Data sync issues
     - Single point of failure          - Code must be stateless
```

### When to Use Which

**Start with vertical scaling when:**
- You are early stage with few users
- Your architecture is simple (monolith)
- You need strong consistency
- You want to move fast without infrastructure complexity

**Switch to horizontal scaling when:**
- You hit hardware limits
- You need fault tolerance (cannot afford downtime)
- Your user base is growing rapidly
- You need to serve users in multiple geographic regions

**In practice, most systems use both:** a reasonable server size (vertical) multiplied across many instances (horizontal).

---

## 2.5 Stateless vs Stateful Servers

The ability to scale horizontally depends heavily on whether your servers are **stateful** or **stateless**. This distinction is critical.

### Stateful Servers

A stateful server remembers information about each user between requests. User session data, shopping cart contents, or authentication status is stored **in the server's memory**.

```
STATEFUL SERVER PROBLEM

User Alice's session is on Server 1.

+-------+      +-----------+      +----------+
| Alice | ---> | Server 1  | ---> | Server 1 |
+-------+      | (has her  |      | knows who|
               | session)  |      | Alice is |
               +-----------+      +----------+

What if Server 1 dies? Or what if the load
balancer sends Alice to Server 2?

+-------+      +-----------+      +----------+
| Alice | ---> | Server 2  | ---> | Server 2 |
+-------+      | (no idea  |      | "Who is  |
               | who Alice |      |  Alice?" |
               |   is)     |      |          |
               +-----------+      +----------+

Alice gets logged out. Her cart is empty.
She is not happy.
```

**Problems with stateful servers:**
- Users are "stuck" to specific servers
- Scaling out is hard because new servers do not have existing session data
- Server failures cause data loss and user disruption
- Uneven load distribution (some servers have more active sessions)

### Stateless Servers

A stateless server does not store any user-specific data between requests. Every request contains all the information the server needs to process it. Session data is stored **externally** (in a database, cache, or the client itself).

```
STATELESS SERVER -- ANY SERVER CAN HANDLE ANY REQUEST

+-------+      +---------------+      +----------+
| Alice | ---> | Load Balancer | ---> | Server 1 | ---+
+-------+      +---------------+      +----------+    |
                     |                                  |
                     +----------> +----------+         |
                                  | Server 2 | ---+    |
                                  +----------+    |    |
                                                   |    |
                                                   v    v
                                            +--------------+
                                            | Shared State |
                                            | (Redis /     |
                                            |  Database)   |
                                            +--------------+

Any server can handle Alice's request because
the session data is in the shared store, not
on any individual server.
```

**Benefits of stateless servers:**
- Any server can handle any request
- Easy to add or remove servers
- Server failures do not lose user data
- Load is distributed evenly
- Auto-scaling becomes straightforward

---

## 2.6 Session Handling Strategies

When you move to stateless servers, you need a strategy for handling user sessions. Here are the three main approaches.

### Strategy 1: Sticky Sessions

The load balancer routes all requests from the same user to the same server. The server stores the session in its own memory.

```
+-------+                         +----------+
| Alice | ---- always goes to --> | Server 1 |
+-------+                         +----------+

+-------+                         +----------+
|  Bob  | ---- always goes to --> | Server 2 |
+-------+                         +----------+
```

**How it works:** The load balancer uses a cookie or the user's IP address to consistently route them to the same backend server.

**Pros:**
- Simple to implement (load balancer configuration only)
- No external session store needed
- Low latency for session reads (data is in local memory)

**Cons:**
- Uneven load distribution (some servers get "heavier" users)
- If a server dies, all sessions on that server are lost
- Hard to auto-scale (removing a server means losing sessions)
- Not truly stateless

### Strategy 2: External Session Store

Store all session data in an external shared store like Redis or Memcached. Servers read and write session data from this store.

```
+----------+     +----------+     +----------+
| Server 1 |     | Server 2 |     | Server 3 |
+----+-----+     +----+-----+     +----+-----+
     |                |                |
     +-------+--------+--------+------+
             |                 |
             v                 v
     +---------------+  +---------------+
     | Redis Primary |  | Redis Replica |
     +---------------+  +---------------+

All servers read/write sessions to Redis.
Any server can handle any user's request.
```

**Pros:**
- True stateless servers -- any server can handle any request
- Server failures do not lose sessions
- Easy to auto-scale (just add/remove app servers)
- Session data survives server restarts

**Cons:**
- Extra infrastructure (Redis/Memcached cluster)
- Network latency for every session read/write
- Session store becomes a critical dependency (needs its own high availability)

**Example: Express.js with Redis sessions:**

```javascript
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');

const redisClient = createClient({
  host: 'redis-session-store.example.com',
  port: 6379
});

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: 'your-secret-key',
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 1800000  // 30 minutes
  }
}));
```

### Strategy 3: Client-Side Sessions (JWT)

Store session data in the client itself, usually as a signed JSON Web Token (JWT) in a cookie or header.

```
+--------+                        +----------+
| Client |  --- sends JWT with -> | Server   |
| (has   |  --- every request --> | (verifies|
|  JWT)  |                        |  JWT,    |
+--------+                        |  needs   |
                                  |  no      |
                                  |  storage)|
                                  +----------+

The server does not store anything.
The client carries its own session.
```

**Pros:**
- Zero server-side storage needed
- Works great with microservices (any service can verify the token)
- No session store infrastructure to manage
- Scales infinitely on the server side

**Cons:**
- Cannot easily revoke a session (the token is valid until it expires)
- Token size increases with more data (sent with every request)
- Sensitive data should not go in the token (it is encoded, not encrypted)
- Token refresh logic adds complexity

### Comparison Table

| Aspect | Sticky Sessions | External Store (Redis) | Client-Side (JWT) |
|--------|----------------|----------------------|-------------------|
| Server statefulness | Stateful | Stateless | Stateless |
| Fault tolerance | Low | High | High |
| Scalability | Limited | Good | Excellent |
| Complexity | Low | Medium | Medium |
| Session revocation | Easy | Easy | Hard |
| Latency overhead | None | Network hop to Redis | Token verification |
| Infrastructure | None extra | Redis cluster | None extra |

---

## 2.7 Database Bottleneck Preview

Even with perfect horizontal scaling of your application servers, you will eventually hit a wall: **the database**.

```
+----------+  +----------+  +----------+  +----------+
| Server 1 |  | Server 2 |  | Server 3 |  | Server 4 |
+----+-----+  +----+-----+  +----+-----+  +----+-----+
     |             |             |             |
     +------+------+------+-----+------+------+
            |             |            |
            v             v            v
         +--------------------------------+
         |        SINGLE DATABASE         |
         |     (This is the bottleneck)   |
         +--------------------------------+

You scaled the app servers, but they all
compete for the same database resources.
```

### Why the Database Becomes the Bottleneck

- **Connection limits:** Each database has a maximum number of concurrent connections (e.g., PostgreSQL defaults to 100)
- **Write contention:** Only one write can happen to a given row at a time
- **Disk I/O:** Even SSDs have limits on reads and writes per second
- **Query complexity:** As data grows, queries take longer without proper indexing
- **Single server limits:** The database runs on one machine with all the same limits we discussed

### Signs Your Database Is the Bottleneck

- Application servers have low CPU usage but responses are slow
- Database CPU or I/O is consistently high
- Query execution times are increasing
- Connection pool is frequently exhausted
- Replication lag is growing (if using replicas)

### What You Can Do About It (Preview)

We will cover these topics in detail in later chapters:

1. **Read replicas:** Send read queries to copies of the database
2. **Caching:** Put frequently accessed data in Redis or Memcached (Chapter 4)
3. **Database sharding:** Split data across multiple database servers
4. **Query optimization:** Better indexes, query rewriting, denormalization
5. **Connection pooling:** Reuse database connections instead of creating new ones
6. **Choosing the right database:** SQL vs NoSQL has scaling implications (Chapter 6)

---

## Trade-Offs Table

| Decision | Option A | Option B | When to Choose A | When to Choose B |
|----------|----------|----------|-----------------|-----------------|
| Vertical vs Horizontal | Scale up (bigger machine) | Scale out (more machines) | Early stage, simple app, strong consistency needed | Growing traffic, need fault tolerance, global users |
| Stateful vs Stateless | Stateful servers | Stateless servers | Very simple app, no scaling needed | Any system that needs to scale |
| Session: Sticky vs Shared | Sticky sessions | External session store | Quick fix, low traffic | Production systems, need reliability |
| Session: Server vs Client | Server-side sessions | JWT/client-side sessions | Need session revocation, sensitive data | Microservices, API-first, mobile apps |
| Single DB vs Multiple | One database | Replicas/shards | Small data, low traffic | Read-heavy workloads, large datasets |

---

## Common Mistakes

1. **Premature horizontal scaling.** Adding load balancers and multiple servers when a single, slightly bigger server would work fine. Complexity has a cost.

2. **Keeping state in application servers.** Storing session data, uploaded files, or caches in server memory makes horizontal scaling painful. Externalize everything.

3. **Ignoring the database.** Scaling application servers is easy. The database is usually the real bottleneck, and it is harder to scale.

4. **Not planning for failure.** Scaling is not just about handling more load. It is also about surviving when things go wrong. A single server is a single point of failure.

5. **Scaling before measuring.** Always identify the bottleneck before scaling. If your database is the problem, adding more app servers will not help.

6. **Forgetting about data locality.** When you have servers in multiple regions, data access patterns matter. A server in Tokyo hitting a database in Virginia will have high latency regardless of how many servers you have.

---

## Best Practices

1. **Start simple.** Begin with one server. It is good enough longer than you think.

2. **Measure before scaling.** Use monitoring to identify the actual bottleneck (CPU, memory, disk, network, database).

3. **Make servers stateless early.** Even if you only have one server, design your application as if you have many. It is much easier to do this from the start than to retrofit it later.

4. **Use an external session store.** Redis or Memcached is cheap and eliminates a whole class of scaling problems.

5. **Separate static and dynamic content.** Serve images, CSS, and JavaScript from a CDN (Chapter 5), not your application server.

6. **Plan for the database.** Think about read/write ratios, data volume, and query patterns early. These inform your database scaling strategy.

7. **Automate scaling.** Use auto-scaling groups (in cloud environments) to automatically add servers during peak traffic and remove them during quiet periods.

---

## Quick Summary

Every system starts with a single server. As traffic grows, you face a choice: make the server bigger (vertical scaling) or add more servers (horizontal scaling). Vertical scaling is simple but has a ceiling and a single point of failure. Horizontal scaling is more flexible but requires your application to be stateless. Session handling is the first challenge of horizontal scaling, and the main strategies are sticky sessions, external session stores, and client-side tokens. Even after scaling your application servers, the database often becomes the bottleneck, which sets the stage for topics covered in the rest of this book.

---

## Key Points

- A single server works for small applications but has hard limits on CPU, memory, disk, and network
- Vertical scaling (bigger machine) is simple but expensive and has a ceiling
- Horizontal scaling (more machines) is flexible but requires stateless design
- Stateful servers store user data in memory, making scaling difficult
- Stateless servers store no user data, enabling any server to handle any request
- Session strategies: sticky sessions (simple but fragile), external store (robust), JWT (no server storage)
- The database is usually the first bottleneck you hit after scaling application servers

---

## Practice Questions

1. Your single-server application is seeing 95% CPU utilization during peak hours. Response times have doubled. Would you scale vertically or horizontally first? Explain your reasoning.

2. You have a stateful application server storing user shopping carts in memory. You need to add a second server. What are your options for handling the shopping cart data, and what are the trade-offs of each?

3. A startup launches with 100 users and plans to reach 1 million in 2 years. Should they start with a scalable, horizontally scaled architecture from day one? Why or why not?

4. Explain why a JWT-based session system is harder to "log out" a user from compared to a Redis-based session store. What are some workarounds?

5. Your monitoring shows application server CPU is at 20% but the database CPU is at 90%. Would adding more application servers help? What would you do instead?

---

## Exercises

**Exercise 1: Architecture Evolution**

Draw the architecture for each stage of growth for a photo-sharing app:
- Stage 1: 100 users (single server)
- Stage 2: 10,000 users (need to separate concerns)
- Stage 3: 1,000,000 users (need horizontal scaling)

For each stage, identify: what changed, why, and what new problems the change introduces.

**Exercise 2: Stateless Refactoring**

You have a Flask (Python) web application that stores login sessions in a Python dictionary in memory:

```python
sessions = {}

@app.route('/login', methods=['POST'])
def login():
    user = authenticate(request.form['username'], request.form['password'])
    session_id = generate_session_id()
    sessions[session_id] = {'user_id': user.id, 'login_time': time.time()}
    response = make_response(redirect('/dashboard'))
    response.set_cookie('session_id', session_id)
    return response
```

Refactor this to use Redis as an external session store. What changes do you need to make? What new failure modes does this introduce?

**Exercise 3: Capacity Planning**

Your e-commerce site gets the following traffic:
- Average: 500 requests/second
- Black Friday peak: 15,000 requests/second
- Each app server can handle 1,000 requests/second

Calculate:
- How many servers do you need for average traffic?
- How many for Black Friday?
- If each server costs $200/month, what is the cost difference between always running peak capacity vs auto-scaling?

---

## What Is Next?

You now understand that horizontal scaling requires distributing requests across multiple servers. But how does a user's request reach the right server? And how do you make sure the load is spread evenly? In Chapter 3, we will dive into **load balancing** -- the traffic cop that sits between users and your servers, directing each request to the best available server. We will cover algorithms, health checks, L4 vs L7 load balancing, and how to avoid making the load balancer itself a single point of failure.
