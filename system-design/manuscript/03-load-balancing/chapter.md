# Chapter 3: Load Balancing

## What You Will Learn

- What a load balancer does and why every scaled system needs one
- The most common load balancing algorithms and when to use each
- The difference between Layer 4 and Layer 7 load balancing
- How health checks keep traffic away from broken servers
- Active-passive vs active-active load balancer setups
- Software load balancers (Nginx, HAProxy) vs hardware appliances
- Global Server Load Balancing (GSLB) for multi-region deployments
- How to prevent the load balancer itself from becoming a single point of failure

## Why This Chapter Matters

In the previous chapter, you learned that horizontal scaling means running multiple servers. But that raises an immediate question: how does a user's request find the right server?

If you just give users the IP address of one server, you are back to a single point of failure. If you give them a list of IPs and say "pick one," you have chaos.

You need a traffic cop -- something that stands at the front door, accepts every incoming request, and routes it to the best available server. That is a load balancer, and it is one of the most critical components in any production system.

---

## 3.1 What Is a Load Balancer?

A load balancer is a device or software that distributes incoming network traffic across multiple servers. It ensures no single server bears too much load while keeping unhealthy servers out of the rotation.

### The Traffic Cop Analogy

Imagine a busy intersection with four lanes leading to a shopping mall's parking garage. Without a traffic cop, all cars might try to enter through the same lane, causing a jam. Three lanes sit empty.

A traffic cop stands at the intersection and directs cars: "You go left. You go right. You go straight. You wait -- that lane is full."

A load balancer does exactly this for network requests.

```
                    +--------+
                    | Client |
                    +---+----+
                        |
                        v
                 +------+-------+
                 | LOAD BALANCER|
                 | (Traffic Cop)|
                 +------+-------+
                        |
           +------------+------------+
           |            |            |
           v            v            v
      +--------+   +--------+   +--------+
      |Server 1|   |Server 2|   |Server 3|
      | (25%)  |   | (25%)  |   | (50%)  |
      +--------+   +--------+   +--------+

      The load balancer decides which server
      handles each incoming request.
```

### What a Load Balancer Does

1. **Distributes traffic:** Spreads requests across servers using a chosen algorithm
2. **Monitors health:** Checks if servers are alive and removes dead ones from rotation
3. **Provides a single entry point:** Users connect to one IP/domain, unaware of multiple backend servers
4. **Enables scaling:** You can add or remove servers without users noticing
5. **Improves availability:** If a server fails, traffic is automatically rerouted

### Where Load Balancers Sit

Load balancers can be placed at multiple tiers in your architecture:

```
+--------+
| Client |
+---+----+
    |
    v
+---+---+  <-- LB Tier 1: Between clients and web servers
| LB #1 |
+---+---+
    |
+---+---+---+
|   |   |   |
v   v   v   v
+--+ +--+ +--+ +--+
|W1| |W2| |W3| |W4|   Web Servers
+--+ +--+ +--+ +--+
    |       |
    v       v
  +-+-+   +-+-+  <-- LB Tier 2: Between web and app servers
  |LB2|   |LB3|
  +-+-+   +-+-+
    |       |
  +-+-+   +-+-+
  |A1 |   |A2 |       App Servers
  +---+   +---+
    |       |
    v       v
  +-+-------+-+  <-- LB Tier 3: Between app and database servers
  |   LB #4   |
  +-----+-----+
        |
  +-----+-----+
  |     |     |
  v     v     v
+---+ +---+ +---+
|DB1| |DB2| |DB3|    Database Servers
+---+ +---+ +---+
```

---

## 3.2 Load Balancing Algorithms

How does the load balancer decide which server gets the next request? That is determined by the algorithm. Each has trade-offs.

### Round Robin

The simplest algorithm. Requests go to servers in order: 1, 2, 3, 1, 2, 3, and so on.

```
Request 1 --> Server 1
Request 2 --> Server 2
Request 3 --> Server 3
Request 4 --> Server 1  (back to start)
Request 5 --> Server 2
Request 6 --> Server 3
...
```

**Pros:** Simple, fair distribution, no state needed.
**Cons:** Ignores server capacity and current load. If Server 1 is slower than Server 2, it still gets equal traffic.

**Best for:** Servers with identical specs and requests that take roughly equal time.

### Weighted Round Robin

Like round robin, but servers with more capacity get more requests.

```
Server weights: Server 1 = 3, Server 2 = 1, Server 3 = 1

Request 1 --> Server 1
Request 2 --> Server 1
Request 3 --> Server 1
Request 4 --> Server 2
Request 5 --> Server 3
Request 6 --> Server 1  (cycle repeats)
...
```

**Pros:** Accounts for different server capacities.
**Cons:** Weights are static. Does not react to real-time load.

**Best for:** Mixed hardware environments where some servers are more powerful.

### Least Connections

Each new request goes to the server with the fewest active connections.

```
Current state:
  Server 1: 12 active connections
  Server 2:  5 active connections  <-- next request goes here
  Server 3:  8 active connections
```

**Pros:** Adapts to real-time load. Handles requests of varying duration well.
**Cons:** Requires tracking connection counts. Slightly more overhead.

**Best for:** Applications where request processing times vary widely (e.g., some requests take 10ms, others take 5 seconds).

### Weighted Least Connections

Combines least connections with server weights. A server with weight 2 and 10 connections is considered less loaded than a server with weight 1 and 8 connections.

**Best for:** Mixed hardware with variable request durations.

### IP Hash

The client's IP address is hashed to determine which server handles the request. The same IP always goes to the same server.

```
hash("192.168.1.10") % 3 = 0 --> Server 1
hash("192.168.1.11") % 3 = 2 --> Server 3
hash("192.168.1.12") % 3 = 1 --> Server 2

Same client always hits the same server.
```

**Pros:** Ensures session persistence without sticky session cookies. Good for caching (same user always hits the same cache).
**Cons:** Uneven distribution if IP addresses are not uniformly distributed. Adding/removing servers changes the mapping (consistent hashing helps here).

**Best for:** Systems that benefit from server affinity without explicit session tracking.

### Random

Each request is assigned to a randomly chosen server.

**Pros:** Dead simple. Surprisingly effective with many servers (the law of large numbers evens it out).
**Cons:** No guarantee of even distribution, especially with few servers.

**Best for:** Large server pools where statistical distribution is acceptable.

### Algorithm Comparison Table

| Algorithm | Complexity | Adapts to Load | Session Affinity | Best Use Case |
|-----------|-----------|----------------|-----------------|---------------|
| Round Robin | Very Low | No | No | Identical servers, uniform requests |
| Weighted Round Robin | Low | No | No | Mixed hardware |
| Least Connections | Medium | Yes | No | Variable request durations |
| Weighted Least Conn | Medium | Yes | No | Mixed hardware + variable durations |
| IP Hash | Low | No | Yes | Session affinity, caching |
| Random | Very Low | No | No | Large pools, simple setup |

---

## 3.3 Layer 4 vs Layer 7 Load Balancing

Load balancers can operate at different layers of the network stack. The two most common are Layer 4 (transport) and Layer 7 (application).

### Layer 4 Load Balancing

Operates at the TCP/UDP level. It sees IP addresses and port numbers but does not look inside the actual request content.

```
L4 LOAD BALANCER

Client request:
  Source IP: 192.168.1.10
  Dest IP:   10.0.0.1 (LB)
  Dest Port: 443

LB decision based on: IP + Port
(Does NOT read HTTP headers, URL, cookies, etc.)

Forwards raw TCP connection to chosen server.
```

**Pros:**
- Very fast (no need to parse request content)
- Protocol agnostic (works with HTTP, WebSocket, gRPC, databases, anything TCP/UDP)
- Lower resource consumption

**Cons:**
- Cannot make routing decisions based on URL path, headers, or cookies
- Cannot modify request/response content
- Limited health check options (TCP connect vs actual HTTP response)

### Layer 7 Load Balancing

Operates at the HTTP/HTTPS level. It reads and understands the full request: URL, headers, cookies, request body.

```
L7 LOAD BALANCER

Client request:
  GET /api/users HTTP/1.1
  Host: example.com
  Cookie: session=abc123
  Content-Type: application/json

LB can route based on:
  - URL path (/api/* vs /static/*)
  - Host header (api.example.com vs www.example.com)
  - Cookie values
  - HTTP method (GET vs POST)
  - Request headers
  - Even request body content
```

**Pros:**
- Smart routing based on content (URL path, headers, cookies)
- Can cache responses
- Can compress/decompress content
- Can terminate SSL (handle HTTPS)
- Better health checks (can check HTTP response codes and content)
- Can modify requests and responses (add headers, rewrite URLs)

**Cons:**
- Slower than L4 (must parse every request)
- More resource intensive
- Only works with HTTP/HTTPS (and sometimes other specific protocols)

### L4 vs L7 Comparison

```
L4 LOAD BALANCER                    L7 LOAD BALANCER
+------------------+               +------------------+
| Sees:            |               | Sees:            |
| - IP addresses   |               | - Everything L4  |
| - Port numbers   |               |   sees PLUS:     |
| - TCP/UDP        |               | - URL path       |
|                  |               | - HTTP headers   |
| Cannot see:      |               | - Cookies        |
| - URL path       |               | - Request body   |
| - HTTP headers   |               | - HTTP method    |
| - Cookies        |               |                  |
| - Request body   |               | Can do:          |
|                  |               | - Content routing |
| Fast, simple,    |               | - SSL termination|
| protocol agnostic|               | - Caching        |
+------------------+               +------------------+
```

### Real-World Example: Content-Based Routing with L7

```
L7 Load Balancer Routing Rules:

/api/*          --> API server pool (4 servers)
/images/*       --> Image server pool (2 servers)
/static/*       --> Static file server pool (2 servers)
/admin/*        --> Admin server (1 server, internal only)
everything else --> Web server pool (3 servers)

+--------+
| Client |
+---+----+
    |
    v
+---+-----------+
| L7 LB         |
| /api/* ?      +---> API Servers [S1] [S2] [S3] [S4]
| /images/* ?   +---> Image Servers [S5] [S6]
| /static/* ?   +---> Static Servers [S7] [S8]
| /admin/* ?    +---> Admin Server [S9]
| /* (default)  +---> Web Servers [S10] [S11] [S12]
+---------------+
```

---

## 3.4 Health Checks

A load balancer is only useful if it knows which servers are healthy. Health checks are periodic tests that verify server availability.

### How Health Checks Work

```
HEALTH CHECK CYCLE

Load Balancer sends check every N seconds:

  LB ---[GET /health]--> Server 1: 200 OK      (healthy)
  LB ---[GET /health]--> Server 2: 200 OK      (healthy)
  LB ---[GET /health]--> Server 3: 503 Error   (unhealthy!)
  LB ---[GET /health]--> Server 4: timeout      (unhealthy!)

After M consecutive failures:
  Server 3 is removed from pool
  Server 4 is removed from pool

Traffic now goes only to Servers 1 and 2.

After Server 3 passes K consecutive checks:
  Server 3 is added back to pool.
```

### Types of Health Checks

**TCP Check (Layer 4):**
- Tries to open a TCP connection to the server
- If the connection succeeds, the server is healthy
- Simple and fast, but does not verify the application is actually working

**HTTP Check (Layer 7):**
- Sends an HTTP request (usually GET /health)
- Checks the response status code (expecting 200)
- Can also check response content
- More accurate but more overhead

**Application-Level Check:**
- The /health endpoint verifies that the application can reach its dependencies
- Checks database connectivity, cache availability, disk space
- Most thorough but slowest

**Example: A Good Health Check Endpoint**

```python
@app.route('/health')
def health_check():
    checks = {}

    # Check database connectivity
    try:
        db.execute("SELECT 1")
        checks['database'] = 'ok'
    except Exception:
        checks['database'] = 'failed'

    # Check Redis connectivity
    try:
        redis_client.ping()
        checks['redis'] = 'ok'
    except Exception:
        checks['redis'] = 'failed'

    # Check disk space
    disk_usage = get_disk_usage_percent()
    checks['disk'] = 'ok' if disk_usage < 90 else 'warning'

    # Determine overall health
    all_ok = all(v == 'ok' for v in checks.values())
    status_code = 200 if all_ok else 503

    return jsonify({
        'status': 'healthy' if all_ok else 'unhealthy',
        'checks': checks
    }), status_code
```

### Health Check Configuration Parameters

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| Interval | Time between checks | 5-30 seconds |
| Timeout | Max wait for response | 2-5 seconds |
| Unhealthy threshold | Consecutive failures to mark unhealthy | 2-3 |
| Healthy threshold | Consecutive successes to mark healthy | 2-5 |
| Path | URL to check (for HTTP checks) | /health |

---

## 3.5 Active-Passive vs Active-Active

What happens if the load balancer itself fails? After all, it is also a server that can crash.

### Active-Passive (Failover)

One load balancer handles all traffic (active). A second load balancer sits idle, monitoring the first (passive). If the active one fails, the passive one takes over.

```
ACTIVE-PASSIVE

Normal operation:
+--------+                         +----------+
| Client | -----> [Active LB] ---> | Servers  |
+--------+       /                 +----------+
                /
         [Passive LB]
         (monitoring,
          ready to
          take over)

After active LB fails:
+--------+                         +----------+
| Client | -----> [Passive LB] --> | Servers  |
+--------+   (now active)         +----------+

         [Dead LB]
         (being repaired)
```

**How it works:**
- Both LBs share a virtual IP (VIP) address
- The passive LB sends heartbeats to the active LB
- If heartbeats stop, the passive LB claims the VIP
- This switchover typically takes a few seconds

**Pros:** Simple, clear roles.
**Cons:** Wasteful (passive LB sits idle). Switchover causes brief downtime.

### Active-Active

Both load balancers handle traffic simultaneously. If one fails, the other absorbs all traffic.

```
ACTIVE-ACTIVE

Normal operation:
+--------+     [LB #1] --+---> +----------+
| Client | --->           |     | Servers  |
+--------+     [LB #2] --+---> +----------+

Both LBs handle traffic. DNS or an upstream
router distributes clients across both.

After LB #1 fails:
+--------+                      +----------+
| Client | ---> [LB #2] ------> | Servers  |
+--------+                      +----------+

LB #2 handles all traffic until LB #1 recovers.
```

**Pros:** No wasted resources. Better throughput (both handle traffic). Faster failover.
**Cons:** More complex configuration. Need to ensure both LBs have consistent state.

---

## 3.6 Software vs Hardware Load Balancers

### Software Load Balancers

Software that runs on standard servers. The two most popular are Nginx and HAProxy.

**Nginx Configuration Example:**

```nginx
upstream backend_servers {
    least_conn;  # Use least connections algorithm

    server 10.0.1.1:8080 weight=3;
    server 10.0.1.2:8080 weight=2;
    server 10.0.1.3:8080 weight=1;

    # Health check parameters
    server 10.0.1.4:8080 backup;  # Only used if others are down
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Timeouts
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /health {
        access_log off;
        return 200 "OK";
    }
}
```

**HAProxy Configuration Example:**

```
frontend http_front
    bind *:80
    default_backend http_back

backend http_back
    balance roundrobin
    option httpchk GET /health

    server server1 10.0.1.1:8080 check weight 3
    server server2 10.0.1.2:8080 check weight 2
    server server3 10.0.1.3:8080 check weight 1
    server server4 10.0.1.4:8080 check backup
```

### Hardware Load Balancers

Dedicated physical appliances from vendors like F5 (BIG-IP) and Citrix (NetScaler). They are purpose-built for high-performance traffic distribution.

### Software vs Hardware Comparison

| Aspect | Software (Nginx/HAProxy) | Hardware (F5/Citrix) |
|--------|-------------------------|---------------------|
| Cost | Free or low cost | $10,000 - $100,000+ |
| Performance | Very good (millions of req/s) | Exceptional (specialized chips) |
| Flexibility | Highly configurable | Vendor-dependent |
| Scalability | Scale by adding servers | Buy bigger appliance |
| Cloud compatibility | Excellent | Limited |
| Setup complexity | Moderate | High (specialized knowledge) |
| Maintenance | Community + self | Vendor support contracts |

### Cloud Load Balancers

In cloud environments, managed load balancers are the most common choice:

- **AWS:** Elastic Load Balancer (ALB for L7, NLB for L4)
- **Google Cloud:** Cloud Load Balancing
- **Azure:** Azure Load Balancer

These are software load balancers managed by the cloud provider. You do not maintain the infrastructure, and they scale automatically.

---

## 3.7 Global Server Load Balancing (GSLB)

When your system spans multiple data centers or regions, you need a way to route users to the nearest or best-performing data center. This is GSLB.

### How GSLB Works

GSLB typically uses DNS to route users to the best data center before a request even reaches a local load balancer.

```
GLOBAL SERVER LOAD BALANCING

User in Tokyo requests example.com

1. DNS query: "Where is example.com?"

2. GSLB DNS server considers:
   - User's geographic location (Tokyo)
   - Health of each data center
   - Current load at each data center
   - Latency from user to each data center

3. DNS response: "example.com is at 203.0.113.10"
   (IP of the Tokyo data center)

4. User connects to Tokyo data center

+----------+                              +-----------+
| User in  |  DNS: example.com?           | GSLB DNS  |
| Tokyo    | ---------------------------> | Server    |
+----------+                              +-----------+
     |                                         |
     |    Answer: 203.0.113.10 (Tokyo DC)     |
     | <---------------------------------------+
     |
     +---> Tokyo Data Center
           +--------+    +--------+
           | LB     |--->|Servers |
           +--------+    +--------+

Meanwhile...

+----------+                              +-----------+
| User in  |  DNS: example.com?           | GSLB DNS  |
| London   | ---------------------------> | Server    |
+----------+                              +-----------+
     |                                         |
     |    Answer: 198.51.100.20 (London DC)   |
     | <---------------------------------------+
     |
     +---> London Data Center
           +--------+    +--------+
           | LB     |--->|Servers |
           +--------+    +--------+
```

### GSLB Routing Methods

| Method | How It Works | Best For |
|--------|-------------|----------|
| Geographic | Route to nearest data center | Latency-sensitive apps |
| Latency-based | Route to lowest-latency data center | Performance optimization |
| Weighted | Distribute traffic by percentage across regions | Gradual rollouts |
| Failover | Route to primary, switch to backup if primary fails | Disaster recovery |
| Round Robin DNS | Alternate between data center IPs | Simple distribution |

---

## 3.8 Avoiding the Single Point of Failure

A load balancer that is itself a single point of failure defeats its purpose. Here is how to prevent that:

```
REDUNDANT LOAD BALANCER SETUP

                    +----------+
                    |   DNS    |
                    | (points  |
                    | to VIP)  |
                    +----+-----+
                         |
                   Virtual IP (VIP)
                    shared between
                    both LBs
                         |
              +----------+----------+
              |                     |
         +----+----+          +----+----+
         | LB #1   |          | LB #2   |
         | (Active) | <------> | (Standby)|
         +----+----+ heartbeat+----+----+
              |                     |
              +----------+----------+
                         |
              +----------+----------+
              |          |          |
         +----+--+ +----+--+ +----+--+
         |Server1| |Server2| |Server3|
         +-------+ +-------+ +-------+

If LB #1 fails, LB #2 claims the VIP
and starts handling all traffic.
Users see no change (same IP address).
```

### Strategies for LB High Availability

1. **Virtual IP (VIP) with failover:** Two LBs share a floating IP. Tools like Keepalived manage the failover.
2. **DNS-based:** Multiple LB IPs in DNS. If one goes down, DNS health checks remove it.
3. **Cloud managed:** AWS ALB, GCP Cloud LB, etc., are inherently highly available (the cloud provider handles redundancy).
4. **Anycast IP:** The same IP is advertised from multiple locations. Network routing handles failover.

---

## Trade-Offs Table

| Decision | Option A | Option B | When to Choose A | When to Choose B |
|----------|----------|----------|-----------------|-----------------|
| L4 vs L7 | Layer 4 (TCP) | Layer 7 (HTTP) | Non-HTTP protocols, raw speed needed | Content routing, SSL termination, caching |
| Round Robin vs Least Conn | Round Robin | Least Connections | Uniform requests, same servers | Variable request times, mixed hardware |
| Active-Passive vs Active-Active | Active-Passive | Active-Active | Simpler setup, lower cost | Maximum uptime, better resource use |
| Software vs Hardware LB | Software (Nginx/HAProxy) | Hardware (F5) | Cost-sensitive, cloud environment | Ultra-high throughput, enterprise compliance |
| Local vs Global LB | Local LB only | GSLB + Local LB | Single region deployment | Multi-region, global user base |

---

## Common Mistakes

1. **Using the load balancer as the only line of defense.** A load balancer distributes traffic but does not fix application bugs or database bottlenecks.

2. **Not setting up health checks.** Without health checks, the load balancer sends traffic to dead servers, causing errors for users.

3. **Overly aggressive health checks.** Checking every 1 second with a 1-failure threshold means a single slow response removes a server from rotation. Transient issues become outages.

4. **Ignoring SSL/TLS termination.** If every backend server handles its own SSL, you waste CPU and complicate certificate management. Let the load balancer handle it.

5. **Single load balancer without redundancy.** You added a load balancer to avoid a single point of failure in your servers, but the load balancer itself is now one.

6. **Choosing the wrong algorithm.** Round robin when your servers have different capacities, or least connections when all requests take the same time (unnecessary overhead).

---

## Best Practices

1. **Always configure health checks.** Both TCP (is the port open?) and HTTP (does the application respond correctly?).

2. **Use L7 load balancing for web applications.** The ability to route based on URL path, terminate SSL, and inspect headers is worth the small performance cost.

3. **Set up redundant load balancers.** Active-passive at minimum. Active-active if you can manage the complexity.

4. **Terminate SSL at the load balancer.** Manage certificates in one place, offload encryption from your application servers.

5. **Start with round robin or least connections.** These cover 90% of use cases. Only get fancy when you have a specific need.

6. **Monitor your load balancer.** Track connection counts, error rates, latency, and backend server health. The LB is the front door -- if it is slow, everything is slow.

7. **Use cloud-managed load balancers when possible.** They handle redundancy, scaling, and SSL certificate management for you.

---

## Quick Summary

A load balancer distributes incoming traffic across multiple servers, acting as a traffic cop for your system. The most common algorithms are round robin, weighted round robin, least connections, and IP hash. Layer 4 load balancers work at the TCP level (fast but limited), while Layer 7 load balancers understand HTTP (smarter but heavier). Health checks ensure traffic only goes to healthy servers. Active-passive setups provide failover redundancy, while active-active setups use both load balancers simultaneously. For global deployments, GSLB uses DNS to route users to the nearest data center. The load balancer itself must be made redundant to avoid becoming the very single point of failure it was meant to eliminate.

---

## Key Points

- A load balancer distributes traffic across multiple servers and removes unhealthy servers from rotation
- Round robin is simplest; least connections adapts to real-time load; IP hash provides session affinity
- L4 load balancing is fast and protocol-agnostic; L7 load balancing is smarter and can route by content
- Health checks are essential -- without them, broken servers still receive traffic
- Always make the load balancer itself redundant (active-passive or active-active)
- Cloud-managed load balancers (AWS ALB, GCP LB) handle redundancy and scaling automatically
- GSLB routes users to the best data center using DNS-based routing

---

## Practice Questions

1. You have 3 backend servers. Server A has 16 GB RAM, Server B has 8 GB RAM, and Server C has 8 GB RAM. Which load balancing algorithm would you choose and why? What weights would you assign?

2. Your application uses WebSocket connections for real-time chat. Should you use L4 or L7 load balancing? What are the implications of each choice?

3. A load balancer is configured with 5-second health check intervals and a 2-failure threshold. Server 2 starts returning 503 errors. How long (at minimum) before the server is removed from rotation? What happens to requests sent to Server 2 during that window?

4. Explain why an active-active load balancer setup is better for availability but more complex than active-passive. What specific challenges does active-active introduce?

5. Your system serves users in North America, Europe, and Asia. You have data centers in Virginia, Frankfurt, and Tokyo. Describe how you would set up GSLB to route users to the nearest data center, and what happens if the Frankfurt data center goes down.

---

## Exercises

**Exercise 1: Nginx Configuration**

Write an Nginx configuration that:
- Listens on port 443 with SSL
- Routes `/api/*` requests to a pool of 3 API servers using least connections
- Routes `/static/*` requests to a pool of 2 static file servers using round robin
- Includes a health check endpoint that returns 200
- Has a backup server that only receives traffic if all primary servers are down

**Exercise 2: Algorithm Selection**

For each of the following scenarios, choose the best load balancing algorithm and explain your reasoning:
- A video streaming service where videos take varying amounts of time to transcode
- A static website served by 10 identical servers
- An e-commerce site where keeping users on the same server improves cache hit rates
- A microservice that processes both quick (5ms) and slow (30s) requests

**Exercise 3: Failure Scenario Analysis**

Draw the architecture of a system with two active-passive load balancers, six backend servers, and a GSLB for two data centers. Then walk through what happens when:
- One backend server crashes
- The active load balancer in Data Center 1 crashes
- The entire Data Center 1 goes offline
- The network link between the two data centers goes down

For each scenario, describe the user impact, the automated recovery, and how long users might be affected.

---

## What Is Next?

Load balancers distribute traffic, but they do not reduce the amount of work each server does. If every request requires a database query that takes 50 milliseconds, adding servers only gets you so far. In Chapter 4, we will explore **caching** -- the art of keeping frequently accessed data close at hand so you can serve it in microseconds instead of milliseconds. Caching is one of the most powerful tools in system design, and it works at every level of the stack.
