# Chapter 20: Logging, Monitoring, and Observability

## What You Will Learn

- The difference between metrics, logs, and traces -- the three pillars of observability
- How Prometheus collects and stores metrics using a pull-based model
- How the ELK stack (Elasticsearch, Logstash, Kibana) handles log aggregation at scale
- How distributed tracing with tools like Jaeger tracks requests across services
- How alerting works and how to avoid alert fatigue
- How Grafana dashboards visualize system health at a glance
- What SLIs, SLOs, and SLAs are and how they define reliability targets
- How health checks detect unhealthy services before they cause outages
- The four golden signals: latency, traffic, errors, and saturation

## Why This Chapter Matters

Imagine driving a car with no dashboard. No speedometer, no fuel gauge, no temperature warning, no check engine light. You would have no idea how fast you are going, whether you are about to run out of gas, or whether the engine is overheating. You would only find out something is wrong when the car breaks down on the highway.

Running a distributed system without monitoring is exactly like that. You have dozens of services, hundreds of servers, thousands of database connections, and millions of requests per minute. Without observability, you are blind. When something breaks (and it will), you have no idea what went wrong, where it went wrong, or how to fix it. Worse, you do not know about problems until your users start complaining.

Observability is not optional. It is the difference between a team that detects and fixes issues in minutes and a team that spends hours guessing in the dark. Every system design you build needs monitoring built in from the start. In interviews, mentioning observability shows that you think about production systems holistically.

---

## Metrics vs Logs vs Traces

These are the three pillars of observability. Each one answers a different question about your system.

### Metrics

**What happened at a high level?**

Metrics are numerical measurements collected at regular intervals. They tell you the overall health of your system: how many requests per second, what is the error rate, how much CPU is being used.

Think of metrics as the gauges on your car dashboard. They give you a quick snapshot of how things are going.

```
  Metrics Examples:

  +-----------------------------------+----------+
  | Metric                            | Value    |
  +-----------------------------------+----------+
  | http_requests_total               | 1,523,847|
  | http_request_duration_seconds_avg | 0.045    |
  | http_errors_total                 | 3,241    |
  | cpu_usage_percent                 | 67.3     |
  | memory_usage_bytes                | 4.2 GB   |
  | active_database_connections       | 85       |
  | queue_depth                       | 12,450   |
  +-----------------------------------+----------+

  Characteristics:
  - Numeric values (counters, gauges, histograms)
  - Collected at regular intervals (every 15-60 seconds)
  - Compact (just numbers, very space-efficient)
  - Aggregatable (can average, sum, percentile)
  - Best for: dashboards, alerting, trend analysis
```

### Logs

**What exactly happened in detail?**

Logs are timestamped text records of individual events. They contain the details you need when debugging a specific problem: what happened, when, where, and in what context.

Think of logs as a ship's logbook. Every event is recorded with a timestamp and details.

```
  Log Examples:

  2024-01-15 10:23:45.123 INFO  [order-service] [req-abc123]
    Order ORD-789 created for user user_456, total: $129.99

  2024-01-15 10:23:45.234 INFO  [payment-service] [req-abc123]
    Processing payment for order ORD-789, method: visa_4242

  2024-01-15 10:23:46.891 ERROR [payment-service] [req-abc123]
    Payment failed for order ORD-789: gateway timeout after 5000ms
    Stack trace:
      at PaymentGateway.charge(PaymentGateway.java:145)
      at PaymentService.processPayment(PaymentService.java:89)

  2024-01-15 10:23:46.892 WARN  [payment-service] [req-abc123]
    Retrying payment for order ORD-789 (attempt 2 of 3)

  Characteristics:
  - Text-based (structured JSON or unstructured text)
  - One entry per event
  - Verbose (large volume, expensive to store)
  - Not easily aggregatable
  - Best for: debugging, audit trails, forensic analysis
```

### Traces

**What was the journey of a single request across services?**

A trace follows a single request as it travels through multiple services. It shows the complete path, timing, and dependencies.

Think of it as a package tracking system. You can see every stop the package made, how long it stayed at each stop, and where it got delayed.

```
  Trace Example: "Place Order" Request

  Trace ID: trace-xyz-789
  Total Duration: 1,247 ms

  +-- API Gateway (12ms) -----------------------------------------+
  |                                                                |
  |  +-- Order Service (45ms) ---------------------------------+   |
  |  |                                                          |   |
  |  |  +-- User Service: Validate User (23ms) ----+           |   |
  |  |  |                                          |           |   |
  |  |  +------------------------------------------+           |   |
  |  |                                                          |   |
  |  |  +-- Inventory Service: Check Stock (89ms) -+           |   |
  |  |  |                                          |           |   |
  |  |  +------------------------------------------+           |   |
  |  |                                                          |   |
  |  |  +-- Payment Service: Charge Card (980ms) --+           |   |
  |  |  |                                          |           |   |
  |  |  |  +-- Payment Gateway (external) (945ms) -+           |   |
  |  |  |  |   *** SLOW! ***                      |           |   |
  |  |  |  +--------------------------------------+           |   |
  |  |  |                                          |           |   |
  |  |  +------------------------------------------+           |   |
  |  |                                                          |   |
  |  |  +-- Email Service: Send Confirmation (98ms)+           |   |
  |  |  |                                          |           |   |
  |  |  +------------------------------------------+           |   |
  |  |                                                          |   |
  |  +----------------------------------------------------------+   |
  |                                                                |
  +----------------------------------------------------------------+

  Insight: The payment gateway took 945ms out of 1,247ms total.
  That is 76% of the request time. The bottleneck is the
  external payment gateway, not our code.

  Characteristics:
  - Request-scoped (follows one request end to end)
  - Shows causality (which service called which)
  - Shows timing (where time was spent)
  - Essential for microservices debugging
  - Best for: latency analysis, dependency mapping, bottleneck identification
```

### How They Work Together

```
  The Three Pillars Together:

  METRICS tell you:  "Error rate jumped to 5% at 10:23 AM"
                      (Something is wrong!)

  LOGS tell you:     "Payment gateway returning timeout errors
                      for orders with amount > $100"
                      (This is what is breaking!)

  TRACES tell you:   "Request trace-xyz-789 shows the payment
                      gateway call took 5,000ms (timeout) while
                      the rest of the request took only 45ms"
                      (This is exactly where and why!)

  Investigation Flow:
  1. Alert fires (from metrics)       --> "What is wrong?"
  2. Look at dashboard (metrics)      --> "Error rate is 5%"
  3. Search logs for errors           --> "Payment timeouts"
  4. Find a failing trace             --> "Gateway takes 5s"
  5. Fix the issue                    --> "Increase timeout, add retry"
  6. Verify fix in metrics            --> "Error rate back to 0.1%"
```

---

## Prometheus: Metrics Collection

Prometheus is the most popular open-source metrics system. It uses a **pull-based** model: Prometheus scrapes metrics from your services at regular intervals.

### How Prometheus Works

```
  Prometheus Architecture:

  +----------+     +----------+     +----------+
  | Service A|     | Service B|     | Service C|
  | /metrics |     | /metrics |     | /metrics |
  +----+-----+     +----+-----+     +----+-----+
       ^                ^                ^
       |    Scrape      |    Scrape      |    Scrape
       |    (every 15s) |    (every 15s) |    (every 15s)
       |                |                |
  +----+----------------+----------------+----+
  |              PROMETHEUS                    |
  |                                            |
  |  +-----------+  +-----------+  +--------+  |
  |  | Scraper   |  | Time     |  | Query  |  |
  |  | (pulls    |  | Series   |  | Engine |  |
  |  |  metrics) |  | Database |  | (PromQL)|  |
  |  +-----------+  +-----------+  +--------+  |
  |                                            |
  +--------------------+-----------------------+
                       |
              +--------v--------+
              | Alertmanager    |
              | (sends alerts   |
              |  to Slack,      |
              |  PagerDuty)     |
              +-----------------+
                       |
              +--------v--------+
              | Grafana         |
              | (dashboards,    |
              |  visualization) |
              +-----------------+

  Pull-Based Model:
  - Each service exposes a /metrics endpoint
  - Prometheus scrapes all endpoints every 15 seconds
  - Metrics stored as time series (value over time)
  - PromQL queries the data for dashboards and alerts
```

### Metric Types

```
  Prometheus Metric Types:

  1. COUNTER (only goes up)
     Total number of HTTP requests: 1,523,847
     Total number of errors: 3,241
     Use: Request counts, error counts, bytes processed

  2. GAUGE (goes up and down)
     Current CPU usage: 67.3%
     Active connections: 85
     Queue depth: 12,450
     Use: Temperature, memory, active sessions

  3. HISTOGRAM (distribution of values)
     Request duration buckets:
       0-50ms:   45,000 requests  (60%)
       50-100ms: 22,500 requests  (30%)
       100-500ms: 6,000 requests  (8%)
       500ms+:    1,500 requests  (2%)
     Use: Latency percentiles, request sizes

  4. SUMMARY (similar to histogram, calculates percentiles)
     P50 latency: 42ms
     P95 latency: 187ms
     P99 latency: 892ms
     Use: When you need precise percentiles client-side
```

### PromQL: Querying Metrics

```
  PromQL Examples:

  # Total requests per second over the last 5 minutes
  rate(http_requests_total[5m])

  # Error rate (percentage of requests that are errors)
  rate(http_requests_total{status=~"5.."}[5m])
  / rate(http_requests_total[5m]) * 100

  # P99 latency
  histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

  # CPU usage above 80% for any instance
  cpu_usage_percent > 80

  # Memory usage by service
  memory_usage_bytes{service="order-service"} / 1024 / 1024 / 1024
```

---

## The ELK Stack: Log Aggregation

ELK stands for Elasticsearch, Logstash, and Kibana. It is the most widely used open-source log aggregation stack.

### The Problem with Logs at Scale

```
  The Log Problem:

  50 microservices x 10 instances each = 500 servers

  Each server generates ~100 MB of logs per hour
  Total: 50 GB of logs per hour = 1.2 TB per day

  Without centralized logging:
  - SSH into each of 500 servers to find a log entry? No.
  - Correlate events across services? Impossible.
  - Search for an error from last Tuesday? Good luck.

  You need centralized log aggregation.
```

### ELK Architecture

```
  ELK Stack Architecture:

  +----------+  +----------+  +----------+
  | Service  |  | Service  |  | Service  |
  | Instance |  | Instance |  | Instance |
  +----+-----+  +----+-----+  +----+-----+
       |              |              |
       | Filebeat     | Filebeat     | Filebeat
       | (shipper)    | (shipper)    | (shipper)
       |              |              |
       +-------+------+------+------+
               |             |
               v             v
       +-------+-------------+-------+
       |         LOGSTASH             |
       |                              |
       |  1. PARSE (extract fields    |
       |     from unstructured text)  |
       |                              |
       |  2. TRANSFORM (add metadata, |
       |     rename fields, filter)   |
       |                              |
       |  3. ENRICH (add geo-IP,      |
       |     add service name)        |
       +-------------+---------------+
                     |
                     v
       +-------------+---------------+
       |       ELASTICSEARCH          |
       |                              |
       |  Index: logs-2024-01-15      |
       |  Searchable within seconds   |
       |  Retention: 30 days          |
       +-------------+---------------+
                     |
                     v
       +-------------+---------------+
       |          KIBANA              |
       |                              |
       |  - Search logs in real time  |
       |  - Build visualizations      |
       |  - Create dashboards         |
       |  - Set up alerts             |
       +------------------------------+

  Modern alternative: Many teams now use
  Filebeat -> Elasticsearch directly (no Logstash)
  or Fluentd instead of Logstash (EFK stack).
```

### Structured Logging

```
  Unstructured Log (Hard to Parse):

  2024-01-15 10:23:45 ERROR Payment failed for order ORD-789
  user user_456 amount $129.99 gateway timeout

  Which part is the order ID? Which is the user?
  Logstash must guess using regex patterns. Fragile.


  Structured Log (JSON - Easy to Parse):

  {
    "timestamp": "2024-01-15T10:23:45.123Z",
    "level": "ERROR",
    "service": "payment-service",
    "instance": "payment-3",
    "trace_id": "trace-xyz-789",
    "message": "Payment failed",
    "order_id": "ORD-789",
    "user_id": "user_456",
    "amount": 129.99,
    "currency": "USD",
    "error": "gateway_timeout",
    "duration_ms": 5000
  }

  Every field is explicitly named.
  Elasticsearch can index and search every field.
  No parsing guesswork needed.
```

### Log Retention Strategy

```
  Log Retention:

  +--------------------+-------------+------------------+
  | Age                | Storage     | Searchable?      |
  +--------------------+-------------+------------------+
  | Last 7 days        | Hot nodes   | Yes (fast)       |
  |                    | (SSD)       |                  |
  +--------------------+-------------+------------------+
  | 7-30 days          | Warm nodes  | Yes (slower)     |
  |                    | (HDD)       |                  |
  +--------------------+-------------+------------------+
  | 30-90 days         | Cold storage| After restore    |
  |                    | (S3/Glacier)|                  |
  +--------------------+-------------+------------------+
  | 90+ days           | Deleted     | No               |
  +--------------------+-------------+------------------+

  Use Index Lifecycle Management (ILM) to automate:
  - Roll over indices daily
  - Move old indices to cheaper storage
  - Delete indices after retention period
```

---

## Distributed Tracing with Jaeger

In a microservices architecture, a single user request can travel through 10 or more services. Distributed tracing tracks the entire journey of a request, showing timing, dependencies, and bottlenecks.

### How Distributed Tracing Works

```
  Distributed Tracing Concepts:

  TRACE: The entire journey of a request (has a unique Trace ID)
  SPAN: One operation within the trace (one service call)

  Trace ID: abc-123

  +-- Span 1: API Gateway (12ms) -------------------------+
  |   Span ID: span-1                                     |
  |   Parent: none                                        |
  |                                                        |
  |   +-- Span 2: Order Service (245ms) ---------------+  |
  |   |   Span ID: span-2                              |  |
  |   |   Parent: span-1                               |  |
  |   |                                                 |  |
  |   |   +-- Span 3: DB Query (15ms) ------+          |  |
  |   |   |   Span ID: span-3               |          |  |
  |   |   |   Parent: span-2                |          |  |
  |   |   +----------------------------------+          |  |
  |   |                                                 |  |
  |   |   +-- Span 4: Payment Service (200ms)+         |  |
  |   |   |   Span ID: span-4               |          |  |
  |   |   |   Parent: span-2                |          |  |
  |   |   |                                  |          |  |
  |   |   |   +-- Span 5: Stripe API (180ms)+          |  |
  |   |   |   |   Parent: span-4            |          |  |
  |   |   |   +------------------------------+          |  |
  |   |   |                                  |          |  |
  |   |   +----------------------------------+          |  |
  |   |                                                 |  |
  |   +-------------------------------------------------+  |
  |                                                        |
  +--------------------------------------------------------+
```

### How Trace Context Propagates

```
  Context Propagation:

  Every service passes the Trace ID and Span ID to the next service
  via HTTP headers.

  Request from Client:
  GET /api/orders HTTP/1.1

  API Gateway adds trace context:
  GET /orders HTTP/1.1
  traceparent: 00-abc123-span1-01

  API Gateway calls Order Service:
  GET /internal/orders HTTP/1.1
  traceparent: 00-abc123-span2-01

  Order Service calls Payment Service:
  POST /internal/payments HTTP/1.1
  traceparent: 00-abc123-span4-01

  Every service:
  1. Reads the traceparent header
  2. Creates a new span (child of the parent span)
  3. Records timing and metadata
  4. Passes the trace context to downstream calls
  5. Sends completed spans to the tracing backend (Jaeger)
```

### Jaeger Architecture

```
  Jaeger Architecture:

  +----------+  +----------+  +----------+
  | Service A|  | Service B|  | Service C|
  | (traced) |  | (traced) |  | (traced) |
  +----+-----+  +----+-----+  +----+-----+
       |              |              |
       | Spans        | Spans        | Spans
       |              |              |
  +----v--------------v--------------v----+
  |           JAEGER AGENT                 |
  |     (sidecar or shared daemon)         |
  |     Batches and forwards spans         |
  +-------------------+-------------------+
                      |
                      v
  +-------------------+-------------------+
  |           JAEGER COLLECTOR             |
  |     Validates and indexes spans        |
  +-------------------+-------------------+
                      |
                      v
  +-------------------+-------------------+
  |           STORAGE (Backend)            |
  |     Elasticsearch or Cassandra         |
  +-------------------+-------------------+
                      |
                      v
  +-------------------+-------------------+
  |           JAEGER QUERY + UI            |
  |     Search traces, visualize spans     |
  +----------------------------------------+
```

### Sampling

You cannot trace every request in a high-traffic system. At 100,000 requests per second, storing every trace would be prohibitively expensive. Sampling strategies select which requests to trace.

```
  Sampling Strategies:

  1. Probabilistic: Trace 1% of all requests
     Simple, even coverage, might miss rare errors

  2. Rate-limiting: Trace 10 requests per second per service
     Predictable cost, might miss spikes

  3. Adaptive: Increase sampling when errors occur
     Best coverage of problems, more complex

  4. Head-based: Decide at the first service whether to trace
     Consistent (whole trace or nothing), can miss slow calls

  5. Tail-based: Decide after the trace is complete
     Can trace only errors/slow requests, requires buffering
```

---

## Alerting

Monitoring without alerting is just a screen nobody looks at. Alerts notify engineers when something needs attention.

### Alert Design

```
  Good Alert vs Bad Alert:

  BAD ALERT:
  "CPU usage is at 82% on server web-14"
  - Is this actually a problem? Maybe 82% is normal.
  - What should I do? No actionable information.
  - Fires constantly? Engineers start ignoring it.

  GOOD ALERT:
  "Error rate exceeded 1% for the order-service
   (currently 3.5%) for the past 5 minutes.
   SLO burn rate: 10x normal.
   Dashboard: https://grafana.internal/order-service
   Runbook: https://wiki.internal/runbooks/order-errors"

  - Clear problem statement
  - Includes current value and threshold
  - Links to dashboard and runbook
  - Based on user-facing symptoms, not internal metrics
```

### Alert Routing

```
  Alert Routing:

  +------------------+
  | Prometheus       |
  | (fires alerts)   |
  +--------+---------+
           |
  +--------v---------+
  | Alertmanager     |
  |                  |
  | - Group related  |
  |   alerts         |
  | - Suppress       |
  |   duplicates     |
  | - Route by       |
  |   severity       |
  | - Silence during |
  |   maintenance    |
  +--------+---------+
           |
     +-----+-----+-----+
     |           |     |
     v           v     v
  +------+  +------+ +--------+
  | Slack |  |PagerD| | Email  |
  | (info)|  |uty   | | (low)  |
  +------+  |(crit) | +--------+
            +------+

  Severity Routing:
  - CRITICAL: PagerDuty (wakes someone up at 3 AM)
  - WARNING:  Slack #alerts channel
  - INFO:     Email digest (daily)
```

### Avoiding Alert Fatigue

```
  Alert Fatigue:

  Monday:    47 alerts fired. 3 were real problems.
  Tuesday:   52 alerts fired. 1 was a real problem.
  Wednesday: 61 alerts fired. 2 were real problems.

  By Thursday, the on-call engineer ignores all alerts.
  On Friday, a real outage goes unnoticed for 45 minutes.

  Rules to Prevent Alert Fatigue:
  1. Every alert must be actionable (if not, delete it)
  2. Alert on symptoms, not causes (error rate, not CPU)
  3. Set thresholds based on data, not guesses
  4. Use alert grouping (10 alerts for the same issue = 1 notification)
  5. Review alerts monthly: delete noisy ones, adjust thresholds
  6. Target: <5 actionable alerts per on-call shift
```

---

## Grafana Dashboards

Grafana is the most popular open-source dashboard tool. It connects to Prometheus, Elasticsearch, and dozens of other data sources to visualize metrics and logs.

### Dashboard Design Principles

```
  Dashboard Layout:

  +----------------------------------------------------------------+
  |                    ORDER SERVICE DASHBOARD                       |
  +----------------------------------------------------------------+
  |                                                                  |
  |  TOP ROW: Golden Signals (at a glance)                          |
  |  +------------+  +------------+  +----------+  +-------------+  |
  |  | Requests/s |  | Error Rate |  | P99      |  | Saturation  |  |
  |  |   1,247    |  |   0.3%     |  | Latency  |  | CPU: 45%    |  |
  |  |  (green)   |  |  (green)   |  |  187ms   |  | Mem: 62%    |  |
  |  +------------+  +------------+  | (yellow)  |  | (green)     |  |
  |                                  +----------+  +-------------+  |
  |                                                                  |
  |  MIDDLE ROW: Request Details                                    |
  |  +------------------------------+  +---------------------------+ |
  |  | Requests per Second          |  | Response Time Distribution| |
  |  |     ___                      |  |                           | |
  |  |    /   \    ___              |  |  P50: [====] 42ms         | |
  |  |   /     \__/   \            |  |  P95: [=========] 187ms   | |
  |  |  /              \___        |  |  P99: [============] 892ms | |
  |  | /                    \      |  |                           | |
  |  +------------------------------+  +---------------------------+ |
  |                                                                  |
  |  BOTTOM ROW: Dependencies                                      |
  |  +------------------------------+  +---------------------------+ |
  |  | Database Connections         |  | Downstream Service Health | |
  |  |  Active: 85 / Max: 200      |  |  Payment:  OK  (12ms)    | |
  |  |  Wait: 3                     |  |  Inventory: OK  (8ms)    | |
  |  |                              |  |  Email:    SLOW (450ms)  | |
  |  +------------------------------+  +---------------------------+ |
  +----------------------------------------------------------------+

  Dashboard Design Rules:
  1. Golden signals at the top (most important, visible first)
  2. Time range selector (last 1h, 6h, 24h, 7d)
  3. Color coding: Green (good), Yellow (warning), Red (critical)
  4. One dashboard per service (not one giant dashboard)
  5. Link to related dashboards (click database panel -> DB dashboard)
```

---

## SLI, SLO, and SLA

These three terms define how you measure and commit to reliability.

### SLI: Service Level Indicator

An SLI is a **measurement** of a specific aspect of your service's behavior. It is the raw metric.

```
  SLI Examples:

  - Request latency: P99 response time = 187ms
  - Availability: Successful requests / Total requests = 99.95%
  - Error rate: Failed requests / Total requests = 0.05%
  - Throughput: 1,247 requests per second
```

### SLO: Service Level Objective

An SLO is a **target** for your SLI. It is the goal your team aims to meet.

```
  SLO Examples:

  - "99.9% of requests will complete in under 500ms"
  - "The service will be available 99.95% of the time"
  - "The error rate will be below 0.1%"

  SLO = SLI + Target

  SLI: P99 latency is 187ms
  SLO: P99 latency must be under 500ms
  Status: MEETING SLO (187ms < 500ms)
```

### SLA: Service Level Agreement

An SLA is a **contract** with customers that includes consequences (usually financial) if the SLO is not met.

```
  SLA Examples:

  "We guarantee 99.99% uptime. If uptime falls below:
   - 99.99%: No penalty
   - 99.9%:  10% credit on monthly bill
   - 99.0%:  25% credit on monthly bill
   - Below 99.0%: 50% credit on monthly bill"

  Relationship:

  SLI          SLO              SLA
  (Metric)     (Target)         (Contract)
  "What we     "What we         "What we
   measure"     aim for"         promise"

  Availability  99.95% target    99.9% guaranteed
  (measured)    (internal goal)  (with penalties)

  Note: SLO is stricter than SLA.
  Your internal target (99.95%) should be higher than
  your external promise (99.9%). This gives you a buffer.
```

### Error Budget

```
  Error Budget:

  SLO: 99.9% availability per month

  Total minutes in a month: 43,200 (30 days)
  Allowed downtime: 43,200 x 0.001 = 43.2 minutes

  Error Budget = 43.2 minutes of downtime per month

  +--------------------------------------------------+
  |  Error Budget for January                         |
  |                                                    |
  |  Budget: 43.2 minutes                             |
  |  Used:   12.5 minutes (Jan 8: DB failover, 12.5m) |
  |  Remaining: 30.7 minutes                          |
  |                                                    |
  |  [=========-------------------------------]        |
  |   29% used                71% remaining            |
  +--------------------------------------------------+

  If error budget is exhausted:
  - Freeze new feature deployments
  - Focus on reliability improvements
  - Review what caused the budget to be consumed
```

---

## Health Checks

Health checks are endpoints that report whether a service is functioning correctly. They are used by load balancers, orchestrators (Kubernetes), and monitoring systems to detect and replace unhealthy instances.

### Types of Health Checks

```
  Health Check Types:

  1. LIVENESS CHECK: "Is the process running?"
     GET /health/live
     Response: 200 OK

     Checks: Process is alive, not deadlocked
     Action if failed: Restart the container

  2. READINESS CHECK: "Can the service handle requests?"
     GET /health/ready
     Response: 200 OK or 503 Service Unavailable

     Checks: Database connected, cache warmed, dependencies available
     Action if failed: Remove from load balancer (but do not restart)

  3. DEEP HEALTH CHECK: "Are all dependencies healthy?"
     GET /health/deep
     Response:
     {
       "status": "degraded",
       "checks": {
         "database": {"status": "healthy", "latency_ms": 5},
         "redis": {"status": "healthy", "latency_ms": 2},
         "payment_gateway": {"status": "unhealthy", "error": "timeout"},
         "disk_space": {"status": "healthy", "free_gb": 45}
       }
     }

     Checks: Every dependency individually
     Use: Debugging, not for load balancer decisions
     Warning: Can be slow, do not call frequently


  Health Check Flow with Load Balancer:

  +--------+
  | Load   |    GET /health/ready (every 10s)
  | Balancer| ----+----+----+
  +---+----+     |    |    |
      |          v    v    v
      |     +----+ +----+ +----+
      |     | S1 | | S2 | | S3 |
      |     | OK | | OK | |FAIL|
      |     +----+ +----+ +----+
      |                      |
      |              Remove from rotation
      |              (no traffic until healthy)
      |
      | Route traffic only to S1 and S2
      v
  +--------+  +--------+
  | S1     |  | S2     |
  +--------+  +--------+
```

---

## The Four Golden Signals

Google's Site Reliability Engineering book defines four golden signals that every service should monitor. If you monitor nothing else, monitor these.

### 1. Latency

How long it takes to serve a request. Track both successful and failed requests separately (failed requests are often fast because they error out immediately).

```
  Latency Monitoring:

  Track percentiles, not averages!

  Average latency: 85ms   <-- Looks fine!

  But the distribution:
  P50:  42ms    (half of requests are fast)
  P90: 120ms    (10% of users wait over 120ms)
  P95: 350ms    (5% of users wait over 350ms)
  P99: 2,100ms  (1% of users wait over 2 seconds!)

  The average hides the long tail.
  1% of 1 million daily users = 10,000 users having a bad experience.

  Always monitor P50, P95, and P99.
```

### 2. Traffic

How much demand is placed on your system. Measured as requests per second for web services, or transactions per second for databases.

```
  Traffic Monitoring:

  Requests per Second (RPS):
  +--------------------------------------------------+
  |                                                    |
  |  2000 |              ****                         |
  |       |           ***    ***                      |
  |  1500 |         **          **                    |
  |       |       **              **                  |
  |  1000 |     **                  **                |
  |       |   **                      **              |
  |   500 | **                          ****          |
  |       |*                                ****      |
  |     0 +--+--+--+--+--+--+--+--+--+--+--+--+--+  |
  |       00 02 04 06 08 10 12 14 16 18 20 22 24    |
  |                    Hour of Day                    |
  +--------------------------------------------------+

  Normal pattern: Low at night, peak during business hours.
  Anomaly: Sudden spike at 3 AM = possible attack or bot traffic.
```

### 3. Errors

The rate of requests that fail. This includes explicit errors (HTTP 5xx), implicit errors (HTTP 200 but wrong content), and policy-based errors (responses slower than a threshold).

```
  Error Rate Monitoring:

  Error Rate = Failed Requests / Total Requests

  +--------------------------------------------------+
  | Error Rate over Time                              |
  |                                                    |
  |  5% |                                              |
  |     |                         *                    |
  |  4% |                        * *                   |
  |     |                       *   *                  |
  |  3% |                      *     *                 |
  |     |                     *       *                |
  |  2% |                    *         *               |
  |     | SLO: 1% -------*-----------*---------        |
  |  1% |              **             **               |
  |     |            **                 ***            |
  |  0% |************                     *********    |
  |     +--+--+--+--+--+--+--+--+--+--+--+--+--+--+  |
  |     10:00    10:15    10:30    10:45    11:00      |
  +--------------------------------------------------+

  At 10:25, error rate crossed the 1% SLO.
  Alert fired. Engineer investigated.
  Root cause: Database connection pool exhausted.
  Fixed at 10:45. Error rate returned to normal.
```

### 4. Saturation

How "full" your service is. How close you are to capacity limits. Track the resources that will exhaust first.

```
  Saturation Monitoring:

  Resource Utilization:

  CPU:          [================--------] 67%    OK
  Memory:       [====================----] 82%    WARNING
  Disk I/O:     [========----------------] 34%    OK
  DB Connections:[========================] 95%    CRITICAL!
  Network:      [============------------] 51%    OK

  The most saturated resource is the bottleneck.
  In this case: database connections at 95%.
  If traffic increases 5%, connections will be exhausted.

  Action: Increase connection pool size or add read replicas.
```

### All Four Together

```
  Four Golden Signals Dashboard:

  +---------------------------+---------------------------+
  |  LATENCY                  |  TRAFFIC                  |
  |  P50: 42ms  P99: 187ms   |  1,247 req/s              |
  |  [Status: OK]             |  [Status: OK]             |
  +---------------------------+---------------------------+
  |  ERRORS                   |  SATURATION               |
  |  Rate: 0.3%               |  CPU: 45%  Mem: 62%       |
  |  [Status: OK]             |  DB Conn: 85/200 (42%)    |
  |                           |  [Status: OK]             |
  +---------------------------+---------------------------+

  If any of these turn red, you have a problem.
  Start investigating immediately.
```

---

## Putting It All Together: Production Observability Stack

```
  Complete Observability Architecture:

  +----------+  +----------+  +----------+  +----------+
  | Service  |  | Service  |  | Service  |  | Service  |
  | A        |  | B        |  | C        |  | D        |
  +----+-----+  +----+-----+  +----+-----+  +----+-----+
       |              |              |              |
       | Metrics      | Logs         | Traces       | All three
       |              |              |              |
  +----v----+    +----v----+    +----v----+    +----v----+
  |Prometheus|   |Filebeat |    | Jaeger  |    |         |
  | (scrape) |   | (ship)  |    | Agent   |    |         |
  +----+-----+   +----+----+    +----+----+    |         |
       |              |              |          |         |
       v              v              v          |         |
  +----------+  +----------+  +----------+     |         |
  |Prometheus|  |Elastic   |  | Jaeger   |     |         |
  |  TSDB    |  |search    |  | Collector|     |         |
  +----+-----+  +----+-----+  +----+-----+     |         |
       |              |              |          |         |
       |              |              |          |         |
       +--------+-----+-------+-----+          |         |
                |              |                |         |
                v              v                |         |
           +----+----+   +----+----+            |         |
           | Grafana |   | Kibana  |            |         |
           | (Metrics|   | (Logs)  |            |         |
           |  & Dash)|   |         |            |         |
           +---------+   +---------+            |         |
                |                               |         |
                v                               |         |
           +----+----+                          |         |
           | Alert   |                          |         |
           | manager |                          |         |
           +----+----+                          |         |
                |                               |         |
         +------+------+                        |         |
         |      |      |                        |         |
         v      v      v                        |         |
      Slack  PagerDuty Email                    |         |
                                                |         |
                                                +---------+


  Investigation Workflow:

  1. Alert fires:     "Order service error rate > 1%"
  2. Open Grafana:    Check golden signals dashboard
  3. Narrow timeframe: Error started at 10:23 AM
  4. Search Kibana:   "level:ERROR AND service:order-service AND @timestamp > 10:23"
  5. Find error:      "Connection pool exhausted, max connections reached"
  6. Open Jaeger:     Find slow traces around 10:23
  7. See bottleneck:  DB queries taking 5s instead of 50ms
  8. Root cause:      A new query without an index causing table scans
  9. Fix:             Add database index, deploy
  10. Verify:         Error rate drops, latency normalizes on Grafana
```

---

## Trade-offs

| Decision | Option A | Option B |
|---|---|---|
| Metrics system | Prometheus (pull, open-source, flexible) | Datadog (push, managed, expensive) |
| Log aggregation | ELK stack (open-source, complex to operate) | Cloud-native (CloudWatch, managed, simpler) |
| Tracing | Jaeger (open-source, self-hosted) | AWS X-Ray (managed, vendor lock-in) |
| Log format | Structured JSON (searchable, larger) | Plain text (human-readable, hard to parse) |
| Sampling | Trace everything (complete data, expensive) | Sample 1% (cheap, may miss rare errors) |
| Alert threshold | Tight (catches everything, noisy) | Loose (quiet, may miss issues) |
| Dashboard | One per service (focused, many dashboards) | Global overview (context, less detail) |

---

## Common Mistakes

1. **No monitoring until something breaks.** By then it is too late. Build monitoring into your system from day one, not as an afterthought.

2. **Alerting on causes instead of symptoms.** Do not alert on "CPU at 80%." Alert on "error rate above 1%" or "P99 latency above 500ms." Users do not care about your CPU; they care about the experience.

3. **Using averages instead of percentiles for latency.** An average of 85ms hides the fact that 1% of users are waiting 2 seconds. Always use P50, P95, and P99.

4. **Too many alerts (alert fatigue).** If your on-call engineer gets 50 alerts per shift and only 2 are real problems, they will start ignoring all alerts. Every alert must be actionable. Delete the rest.

5. **Not correlating metrics, logs, and traces.** Metrics tell you something is wrong. Logs tell you what is wrong. Traces tell you where it is wrong. You need all three working together with shared correlation IDs.

6. **No runbooks for alerts.** An alert that says "Error rate is high" without a link to troubleshooting steps is useless at 3 AM. Every alert should link to a runbook.

---

## Best Practices

1. **Instrument the four golden signals for every service.** Latency, traffic, errors, and saturation. If you monitor nothing else, monitor these.

2. **Use structured logging (JSON).** Make every log entry machine-parseable with explicit fields for service, level, trace ID, and relevant business data.

3. **Include trace IDs in all logs.** This lets you correlate logs across services for a single request. Search Kibana by trace ID to see the full picture.

4. **Set SLOs based on user impact.** Define what "good enough" means for your users, then measure against it. Use error budgets to balance reliability and feature velocity.

5. **Alert on SLO burn rate, not raw thresholds.** Instead of "error rate > 1%," alert on "we are consuming our monthly error budget 10x faster than normal." This reduces false positives.

6. **Review alerts quarterly.** Delete alerts nobody acts on. Adjust thresholds based on historical data. Add alerts for new failure modes you discovered.

7. **Build dashboards top-down.** Start with the overview (four golden signals), then drill down into subsystems (database, cache, queue). Link dashboards together for easy navigation.

8. **Practice incident response.** Run game days where you inject failures and practice using your observability tools to find and fix problems. The worst time to learn your dashboards is during a real outage.

---

## Quick Summary

Observability has three pillars: metrics (numeric measurements over time), logs (detailed event records), and traces (request journeys across services). Prometheus collects metrics by scraping endpoints, stores them as time series, and supports alerting via PromQL and Alertmanager. The ELK stack aggregates logs from hundreds of servers into a searchable central store. Jaeger provides distributed tracing to follow requests across microservices, revealing bottlenecks and dependencies. Alerts should be actionable, symptom-based, and linked to runbooks. Grafana dashboards visualize system health at a glance. SLIs measure service behavior, SLOs set targets, and SLAs make contractual promises with consequences. Health checks let load balancers and orchestrators detect and replace unhealthy instances. The four golden signals -- latency, traffic, errors, and saturation -- are the minimum metrics every service must monitor.

---

## Key Points

- Metrics, logs, and traces each answer different questions: what happened, what exactly happened, and what was the request's journey
- Prometheus uses a pull model to scrape metrics from service endpoints every 15 seconds
- The ELK stack centralizes logs from hundreds of servers into a searchable store
- Distributed tracing with Jaeger follows requests across services to find bottlenecks
- Alert on symptoms (error rate, latency) not causes (CPU, memory)
- SLOs define reliability targets; error budgets balance reliability with feature velocity
- The four golden signals (latency, traffic, errors, saturation) are the minimum monitoring for any service
- Always use percentiles (P50, P95, P99) instead of averages for latency

---

## Practice Questions

1. Your e-commerce platform has 30 microservices. The checkout flow takes 3 seconds instead of the usual 500 milliseconds. You have Prometheus, ELK, and Jaeger deployed. Walk through exactly how you would diagnose the problem step by step.

2. Your SLO is 99.9% availability. It is January 20th and you have already consumed 80% of your monthly error budget. What actions would you take? When would you resume normal feature deployments?

3. Your on-call engineer received 147 alerts last week. Only 8 required action. How would you reduce alert noise while ensuring real problems are still caught?

4. You are deploying a new service. What metrics, logs, and traces would you instrument before the first deployment? What dashboards and alerts would you create?

5. Your service has a P99 latency of 2 seconds but a P50 of 50 milliseconds. The average is 120 milliseconds. Your SLO says P99 must be under 500 milliseconds. What could cause such a large gap between P50 and P99? How would you investigate?

---

## Exercises

**Exercise 1: Design an Observability Stack**

You are building an e-commerce platform with 15 microservices. Design the complete observability stack: metrics collection, log aggregation, distributed tracing, alerting, and dashboards. Choose specific tools for each layer. Define the four golden signals for three critical services (API gateway, order service, payment service). Write the alert rules and specify the routing (what goes to Slack, what wakes someone up).

**Exercise 2: Create an SLO Framework**

Define SLOs for a food delivery application. Consider these user journeys: browsing restaurants, placing an order, tracking a delivery, and making a payment. For each journey, define the SLIs you would measure, the SLO targets, and the error budget. Calculate how much downtime is allowed per month for each SLO. Describe what happens when the error budget is exhausted.

**Exercise 3: Incident Investigation**

It is 2:00 AM. An alert fires: "Payment service error rate exceeded 5% for 10 minutes." Write a detailed incident investigation plan. What dashboards would you check first? What log queries would you run? How would you use traces to find the root cause? Write the post-incident review document including timeline, root cause, impact, and preventive measures.

---

## What Is Next?

You now have the tools to see inside your distributed systems: metrics for the big picture, logs for the details, and traces for the journey. You can set targets with SLOs, alert on problems, and investigate incidents systematically. With the foundation chapters complete -- from scaling and databases to message queues, microservices, event-driven architecture, blob storage, search, notifications, and monitoring -- you are ready to put it all together. In the next chapters, you will design complete systems from scratch: URL shorteners, social media platforms, chat applications, and more. Each design will combine multiple concepts from these foundation chapters into a cohesive architecture.
