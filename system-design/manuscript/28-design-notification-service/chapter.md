# Chapter 28: Design a Notification Service

## What You Will Learn

By the end of this chapter, you will understand how to design a scalable notification service that delivers messages across multiple channels. You will learn how to build a priority queue system, implement template engines, handle user preferences, manage delivery retries with exponential backoff, enforce rate limiting, support A/B testing, and track delivery analytics. You will walk away with a complete architecture that handles millions of notifications per day.

## Why This Chapter Matters

Notifications are everywhere. Every app you use sends push notifications, emails, or SMS messages. Behind the scenes, these systems must handle enormous scale, respect user preferences, guarantee delivery, and avoid spamming users. A notification service is one of the most common system design interview questions because it touches on queues, distributed systems, template rendering, third-party integrations, and analytics. Understanding this design will sharpen your skills across many system design topics.

---

## 1. Requirements Gathering

### Functional Requirements

Before drawing any diagrams, let us clarify what our notification service must do.

**Core features:**
- Send notifications via three channels: push notification, SMS, and email
- Support notification templates with variable substitution
- Respect user preferences (opt-in, opt-out, quiet hours, channel preferences)
- Schedule notifications for future delivery
- Track delivery status (sent, delivered, failed, opened)
- Support A/B testing of notification content
- Provide analytics dashboards

**Additional features:**
- Priority levels (urgent, high, normal, low)
- Rate limiting per user to prevent spamming
- Idempotent delivery (no duplicate notifications)
- Batch notifications (digest mode)

### Non-Functional Requirements

- **Scale:** 10 million notifications per day (approximately 115 per second average, with peaks of 1,000+ per second)
- **Latency:** Urgent notifications delivered within 1 second, normal within 5 minutes
- **Reliability:** At-least-once delivery with deduplication
- **Availability:** 99.9% uptime

### Back-of-Envelope Estimation

```
Daily notifications: 10 million
Average per second:  10M / 86,400 = ~115 notifications/sec
Peak (10x average):  ~1,150 notifications/sec

Storage per notification metadata: ~1 KB
Daily storage: 10M x 1 KB = 10 GB
Monthly storage: 300 GB
Yearly storage: 3.6 TB

Template storage: negligible (thousands of templates, ~1 KB each)
```

---

## 2. High-Level Architecture

Let us start with the big picture and then drill into each component.

```
+------------------+     +------------------+     +------------------+
|   API Clients    |     |  Scheduled Jobs  |     |  Event Triggers  |
|  (Web, Mobile,   |     |  (Cron-based     |     |  (User signup,   |
|   Internal APIs) |     |   campaigns)     |     |   order placed)  |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
+--------+------------------------+------------------------+---------+
|                      API Gateway / Load Balancer                   |
+--------+----------------------------------------------------------+
         |
         v
+--------+----------------------------------------------------------+
|                     Notification Service API                       |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
|  | Validation  |  | Idempotency |  | Rate Limit  |  | Auth &    | |
|  | Layer       |  | Check       |  | Check       |  | Authz     | |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
+--------+----------------------------------------------------------+
         |
         v
+--------+----------------------------------------------------------+
|                      Priority Queue System                         |
|  +----------+  +----------+  +----------+  +----------+           |
|  | URGENT   |  | HIGH     |  | NORMAL   |  | LOW      |           |
|  | Queue    |  | Queue    |  | Queue    |  | Queue    |           |
|  +----------+  +----------+  +----------+  +----------+           |
+--------+----------------------------------------------------------+
         |
         v
+--------+----------------------------------------------------------+
|                     Notification Workers                           |
|  +------------------+  +------------------+  +------------------+ |
|  | User Preference  |  | Template Engine  |  | A/B Test Engine  | |
|  | Resolver         |  | (Render Content) |  | (Select Variant) | |
|  +------------------+  +------------------+  +------------------+ |
+--------+----------------------------------------------------------+
         |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
+--------+------+  +---------+-----+  +---------+-----+
| Push Delivery |  | SMS Delivery  |  | Email Delivery|
| Service       |  | Service       |  | Service       |
| (APNs, FCM)   |  | (Twilio,     |  | (SendGrid,   |
|               |  |  Vonage)     |  |  SES)         |
+--------+------+  +---------+-----+  +---------+-----+
         |                   |                   |
         v                   v                   v
+--------+-------------------+-------------------+------+
|                  Delivery Tracker                      |
|  (Status updates, webhooks, delivery receipts)         |
+--------+----------------------------------------------+
         |
         v
+--------+----------------------------------------------+
|                  Analytics Service                     |
|  (Sent, delivered, opened, clicked, failed rates)      |
+-------------------------------------------------------+
```

### Data Flow

1. A client sends a notification request to the API
2. The API validates the request, checks idempotency, and enforces rate limits
3. The notification is placed in the appropriate priority queue
4. Workers consume from queues, resolve user preferences, render templates, and select A/B variants
5. Channel-specific delivery services send the actual notification
6. Delivery tracker records status updates
7. Analytics service aggregates metrics

---

## 3. Detailed Component Design

### 3.1 Notification Service API

The API is the entry point. It accepts notification requests and performs initial processing.

**API Endpoints:**

```
POST /api/v1/notifications
  Send a single notification

POST /api/v1/notifications/batch
  Send notifications to multiple users

GET  /api/v1/notifications/{id}/status
  Check delivery status

PUT  /api/v1/users/{id}/preferences
  Update user notification preferences

POST /api/v1/templates
  Create or update a notification template

GET  /api/v1/analytics/notifications
  Retrieve notification analytics
```

**Request Schema:**

```json
{
  "notification_id": "uuid-123",         // Client-generated for idempotency
  "user_id": "user-456",
  "template_id": "welcome-email-v2",
  "channels": ["push", "email"],         // Desired channels
  "priority": "high",                    // urgent | high | normal | low
  "data": {                              // Template variables
    "user_name": "Alice",
    "action_url": "https://app.com/verify"
  },
  "schedule_at": "2025-01-15T09:00:00Z", // Optional: future delivery
  "ab_test_id": "test-789"               // Optional: A/B test
}
```

### 3.2 Idempotency Layer

Duplicate notifications are a terrible user experience. If a client retries a request due to a network timeout, we must not send the notification twice.

**How it works:**

```
Client sends notification with notification_id = "uuid-123"

Step 1: Check idempotency store
  Key: "idempotency:uuid-123"
  If EXISTS -> return cached response (already processed)
  If NOT EXISTS -> continue processing

Step 2: Process the notification

Step 3: Store result in idempotency store
  SET "idempotency:uuid-123" = response
  EXPIRE after 24 hours

+-------------------+     +-----------------+
| Incoming Request  |---->| Redis Idempotency|
| id = "uuid-123"   |     | Store            |
+-------------------+     +--------+--------+
                                   |
                          +--------+--------+
                          | Key exists?      |
                          +--------+--------+
                          |YES              |NO
                          v                 v
                   Return cached     Process request
                   response          and store result
```

We use Redis for the idempotency store because lookups are fast (sub-millisecond) and we can set automatic expiration on keys.

### 3.3 Priority Queue System

Not all notifications are equal. A two-factor authentication code is urgent. A weekly digest is low priority. Our queue system must handle this.

**Queue Architecture:**

```
                    Notification arrives
                           |
                    +------+------+
                    | Priority    |
                    | Router      |
                    +------+------+
                           |
          +-------+--------+--------+-------+
          |       |                 |       |
          v       v                 v       v
     +--------+ +------+     +--------+ +-----+
     |URGENT  | |HIGH  |     |NORMAL  | |LOW  |
     |Queue   | |Queue |     |Queue   | |Queue|
     |Weight:8| |Wt: 4 |     |Wt: 2  | |Wt:1 |
     +--------+ +------+     +--------+ +-----+
          |       |                 |       |
          +-------+--------+-------+-------+
                           |
                    Workers consume using
                    weighted round-robin
```

**Implementation with Kafka:**

We use Apache Kafka with four topics, one per priority level. Consumer groups use weighted consumption to ensure higher-priority messages are processed first.

```
Topics:
  notifications.urgent   (8 partitions, consumed first)
  notifications.high     (8 partitions)
  notifications.normal   (16 partitions)
  notifications.low      (4 partitions)

Consumer group: notification-workers
  - 20 worker instances
  - Workers poll urgent queue 8x, high 4x, normal 2x, low 1x
```

**Why not a single queue with priority field?**

A single queue with millions of messages makes priority sorting expensive. Separate queues let us control consumption rates independently. If the urgent queue backs up, we can add workers specifically for that queue.

### 3.4 Scheduling Service

For scheduled notifications (send this email at 9 AM tomorrow), we need a reliable scheduler.

```
+--------------------+
| Scheduled          |
| Notification       |
| Request            |
+--------+-----------+
         |
         v
+--------+-----------+     +------------------+
| Scheduler Service  |---->| Scheduled Store   |
| (Write to store)   |     | (Database table)  |
+--------------------+     +--------+---------+
                                    |
                           +--------+---------+
                           | Scheduler Worker |
                           | (Polls every     |
                           |  minute)         |
                           +--------+---------+
                                    |
                           Check: schedule_at <= NOW
                           AND status = 'pending'
                                    |
                                    v
                           Enqueue to Priority Queue
                           Mark status = 'queued'
```

**Database Schema for Scheduled Notifications:**

```sql
CREATE TABLE scheduled_notifications (
    id              UUID PRIMARY KEY,
    notification_id UUID NOT NULL,
    user_id         VARCHAR(64) NOT NULL,
    template_id     VARCHAR(128) NOT NULL,
    channels        JSONB NOT NULL,
    priority        VARCHAR(16) NOT NULL,
    data            JSONB NOT NULL,
    schedule_at     TIMESTAMP NOT NULL,
    status          VARCHAR(16) DEFAULT 'pending',
    created_at      TIMESTAMP DEFAULT NOW(),

    INDEX idx_schedule_at_status (schedule_at, status)
);
```

The scheduler worker runs every minute, queries for notifications whose `schedule_at` has passed, enqueues them, and marks them as processed. The index on `(schedule_at, status)` ensures this query is fast even with millions of rows.

### 3.5 User Preference Service

Users must be able to control what notifications they receive, through which channels, and when.

**Preference Model:**

```json
{
  "user_id": "user-456",
  "global_enabled": true,
  "quiet_hours": {
    "enabled": true,
    "start": "22:00",
    "end": "07:00",
    "timezone": "America/New_York"
  },
  "channels": {
    "push": { "enabled": true },
    "email": { "enabled": true, "frequency": "immediate" },
    "sms": { "enabled": false }
  },
  "categories": {
    "marketing": { "enabled": false },
    "transactional": { "enabled": true },
    "social": { "enabled": true, "channels": ["push"] }
  },
  "digest": {
    "enabled": true,
    "frequency": "daily",
    "time": "09:00"
  }
}
```

**Preference Resolution Flow:**

```
Notification for user-456, category="social", channels=["push","email"]
         |
         v
+--------+-----------+
| Load User Prefs    |
| (Cache in Redis,   |
|  fallback to DB)   |
+--------+-----------+
         |
         v
+--------+-----------+
| Global enabled?    |---NO---> Drop notification
+--------+-----------+
         |YES
         v
+--------+-----------+
| Category enabled?  |---NO---> Drop notification
+--------+-----------+
         |YES
         v
+--------+-----------+
| Channel filtering  |
| User wants: push   |
| Requested: push,   |
|   email             |
| Result: push only  |
+--------+-----------+
         |
         v
+--------+-----------+
| Quiet hours check  |
| Current time in    |
| user timezone:     |
| 23:30 EST          |
| Quiet: 22:00-07:00 |---IN QUIET HOURS---> Queue for 07:00
+--------+-----------+
         |NOT IN QUIET HOURS
         v
    Proceed to template rendering
```

### 3.6 Template Engine

Templates let us separate notification content from delivery logic. Marketing teams can update message copy without deploying code.

**Template Storage:**

```json
{
  "template_id": "order-confirmation-v3",
  "category": "transactional",
  "channels": {
    "push": {
      "title": "Order Confirmed!",
      "body": "Hi {{user_name}}, your order #{{order_id}} is confirmed."
    },
    "email": {
      "subject": "Your order #{{order_id}} is confirmed",
      "html_body": "<h1>Thanks, {{user_name}}!</h1><p>Order total: {{total}}</p>",
      "text_body": "Thanks, {{user_name}}! Order total: {{total}}"
    },
    "sms": {
      "body": "Order #{{order_id}} confirmed. Total: {{total}}"
    }
  },
  "version": 3,
  "created_at": "2025-01-10T12:00:00Z"
}
```

**Template Rendering Process:**

```
Input:
  template_id = "order-confirmation-v3"
  channel = "email"
  data = { "user_name": "Alice", "order_id": "12345", "total": "$99.00" }

Step 1: Load template from cache (Redis) or database
Step 2: Select channel-specific content
Step 3: Substitute variables using Mustache/Handlebars syntax
Step 4: Validate output (no unresolved {{variables}})

Output:
  subject: "Your order #12345 is confirmed"
  html_body: "<h1>Thanks, Alice!</h1><p>Order total: $99.00</p>"
  text_body: "Thanks, Alice! Order total: $99.00"
```

Templates are versioned. When you update a template, the old version remains available. Scheduled notifications that were created with version 2 will still render with version 2, even if version 3 now exists.

### 3.7 A/B Testing Engine

A/B testing lets you compare different notification variants to see which performs better.

```
+--------------------+
| Notification with  |
| ab_test_id="t-789" |
+--------+-----------+
         |
         v
+--------+-----------+
| A/B Test Config    |
| Test "t-789":      |
|   Variant A: 50%   |
|     template: v1   |
|   Variant B: 50%   |
|     template: v2   |
+--------+-----------+
         |
         v
+--------+-----------+
| Consistent Hash    |
| hash(user_id) %100 |
| Result: 42         |
| 42 < 50 -> A       |
+--------+-----------+
         |
         v
+--------+-----------+
| Record Assignment  |
| user-456 -> A      |
| (for analytics)    |
+--------+-----------+
         |
         v
    Render Variant A template
```

Key design decisions for A/B testing:

1. **Consistent assignment:** The same user always sees the same variant. We use a hash of the user ID, not random selection, so a user who receives multiple notifications from the same test always gets the same variant.

2. **Statistical tracking:** We track delivery rate, open rate, and click rate per variant. The analytics service computes statistical significance.

3. **Gradual rollout:** Start with 10/90 split, then move to 50/50 once the new variant looks safe.

### 3.8 Channel Delivery Services

Each channel has its own delivery service that handles the specifics of that channel.

```
+----------------------------------------------------------+
|                 Push Notification Service                  |
|                                                           |
|  +------------------+     +--------------------------+   |
|  | Device Token     |     | Platform Router          |   |
|  | Registry         |     |   iOS -> APNs            |   |
|  | (user -> tokens) |     |   Android -> FCM         |   |
|  +------------------+     |   Web -> Web Push API     |   |
|                           +--------------------------+   |
|                                                           |
|  Handles: Token refresh, invalid token cleanup,           |
|           payload size limits (4KB APNs, 4KB FCM)         |
+----------------------------------------------------------+

+----------------------------------------------------------+
|                   SMS Delivery Service                     |
|                                                           |
|  +------------------+     +--------------------------+   |
|  | Phone Number     |     | Provider Router          |   |
|  | Validator        |     |   US/CA -> Twilio         |   |
|  | (E.164 format)   |     |   EU -> Vonage            |   |
|  +------------------+     |   Asia -> Local provider  |   |
|                           +--------------------------+   |
|                                                           |
|  Handles: Character limits (160 GSM, 70 Unicode),         |
|           country code routing, opt-out (STOP keyword)    |
+----------------------------------------------------------+

+----------------------------------------------------------+
|                  Email Delivery Service                    |
|                                                           |
|  +------------------+     +--------------------------+   |
|  | Email Validator  |     | Provider Router          |   |
|  | (MX record check)|     |   Transactional -> SES   |   |
|  +------------------+     |   Marketing -> SendGrid  |   |
|                           +--------------------------+   |
|                                                           |
|  Handles: DKIM/SPF/DMARC, bounce processing,             |
|           unsubscribe headers, attachment limits           |
+----------------------------------------------------------+
```

**Why separate services per channel?**

Each channel has unique constraints, failure modes, and rate limits. Push notifications can fail because a device token expired. SMS can fail because a phone number is invalid. Email can fail because the receiving server is temporarily down. Separate services let us handle each channel's quirks independently and scale them separately.

### 3.9 Retry with Exponential Backoff

Notifications can fail. The third-party provider might be down, the user's device might be unreachable, or we might hit a rate limit. We need smart retries.

```
Attempt 1: Send immediately
  Failed? Wait 1 second

Attempt 2: Retry after 1s
  Failed? Wait 2 seconds

Attempt 3: Retry after 2s
  Failed? Wait 4 seconds

Attempt 4: Retry after 4s
  Failed? Wait 8 seconds

Attempt 5: Retry after 8s
  Failed? Move to Dead Letter Queue

Formula: delay = base_delay * 2^(attempt - 1) + random_jitter

Jitter prevents all retries from hitting the provider at the same time
(thundering herd problem).
```

**Retry Flow:**

```
+-------------------+
| Send Notification |
+--------+----------+
         |
    +----+----+
    | Success? |
    +----+----+
    YES  |    NO
     |   |     |
     v   |     v
  Record |  +--+------------------+
  success|  | Retryable error?    |
         |  | (timeout, 5xx,      |
         |  |  rate limited)      |
         |  +--+------------------+
         |  YES |            NO |
         |      v               v
         |  +---+----------+  Record permanent
         |  | Max retries  |  failure
         |  | reached?     |
         |  +---+----------+
         |  NO  |       YES |
         |      v           v
         |  Add back to   Move to Dead
         |  queue with     Letter Queue
         |  delay          (DLQ)
         |
         v
      Done
```

**Dead Letter Queue (DLQ):** Notifications that fail all retry attempts go to a DLQ. Operations teams monitor the DLQ and can manually retry or investigate failures. Common DLQ reasons include invalid device tokens, deactivated phone numbers, and permanent email bounces.

### 3.10 Rate Limiting Per User

We must protect users from being spammed, even if our own systems or clients try to send too many notifications.

```
Rate Limiting Rules:
  - Max 5 push notifications per user per hour
  - Max 3 SMS per user per day
  - Max 10 emails per user per day
  - Max 1 notification of same type per user per 5 minutes

+-------------------+
| Notification for  |
| user-456          |
+--------+----------+
         |
         v
+--------+----------+     +------------------+
| Rate Limit Check  |---->| Redis Counters   |
| (per user,        |     |                  |
|  per channel,     |     | push:user-456:   |
|  per type)        |     |   hour -> 3      |
+--------+----------+     | sms:user-456:    |
         |                 |   day -> 1       |
    +----+----+            +------------------+
    | Within  |
    | limits? |
    +----+----+
    YES  |    NO
     |   |     |
     v   |     v
  Continue|  +--+------------------+
  sending |  | Priority override?  |
          |  | (urgent bypasses    |
          |  |  some limits)       |
          |  +--+------------------+
          |  YES |            NO |
          |      v               v
          |  Continue         Drop or defer
          |  sending          notification
          |
          v
       Proceed to delivery
```

Urgent notifications (like security alerts or OTP codes) can bypass rate limits. But even urgent notifications have a hard cap to prevent abuse.

### 3.11 Delivery Tracking and Analytics

Tracking every notification through its lifecycle gives us the data to improve delivery rates and user engagement.

**Notification Lifecycle States:**

```
CREATED --> QUEUED --> PROCESSING --> SENT --> DELIVERED --> OPENED --> CLICKED
                          |            |
                          v            v
                       FILTERED     FAILED --> RETRYING --> SENT
                       (user prefs)    |
                                       v
                                   DEAD_LETTERED
```

**Analytics Data Model:**

```sql
CREATE TABLE notification_events (
    event_id        UUID PRIMARY KEY,
    notification_id UUID NOT NULL,
    user_id         VARCHAR(64) NOT NULL,
    channel         VARCHAR(16) NOT NULL,
    event_type      VARCHAR(32) NOT NULL,
    ab_test_id      VARCHAR(64),
    ab_variant      VARCHAR(16),
    metadata        JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Partitioned by created_at for efficient time-range queries
-- Indexed on (notification_id), (user_id, created_at)
```

**Analytics Dashboard Metrics:**

```
+---------------------------------------------------------------+
|              Notification Analytics Dashboard                  |
+---------------------------------------------------------------+
| Time Range: Last 7 Days                                       |
+---------------------------------------------------------------+
|                                                               |
| Total Sent: 70,000,000    Delivery Rate: 97.2%                |
|                                                               |
| By Channel:                                                   |
|   Push:  40M sent | 38.5M delivered | 12M opened | 96.3% DR  |
|   Email: 25M sent | 24.5M delivered | 8M opened  | 98.0% DR  |
|   SMS:    5M sent |  4.8M delivered | N/A         | 96.0% DR  |
|                                                               |
| Top Failure Reasons:                                          |
|   Invalid device token:  45%                                  |
|   Email bounce:          25%                                  |
|   Provider timeout:      15%                                  |
|   Rate limited:          10%                                  |
|   Other:                  5%                                  |
|                                                               |
| A/B Test Results (test-789):                                  |
|   Variant A: 52% open rate (p < 0.05, significant)            |
|   Variant B: 48% open rate                                    |
+---------------------------------------------------------------+
```

---

## 4. Complete Architecture Diagram

Here is the full system architecture with all components connected.

```
+------------------------------------------------------------------+
|                        CLIENTS                                    |
|  +----------+  +-------------+  +-------------+  +------------+  |
|  | Mobile   |  | Web App     |  | Internal    |  | Cron Jobs  |  |
|  | App      |  |             |  | Services    |  | (Campaigns)|  |
|  +----+-----+  +------+------+  +------+------+  +-----+------+  |
+-------|---------------|---------------|---------------|------------+
        |               |               |               |
        v               v               v               v
+-------+---------------+---------------+---------------+-----------+
|                    API Gateway / Load Balancer                     |
|                   (Rate limiting, auth, routing)                   |
+----------------------------------+--------------------------------+
                                   |
                                   v
+----------------------------------+--------------------------------+
|                    NOTIFICATION SERVICE API                        |
|  +--------+  +-----------+  +----------+  +----------+  +------+  |
|  | Auth   |  | Validate  |  | Idempot- |  | Rate     |  | Pref |  |
|  | Check  |->| Request   |->| ency     |->| Limit    |->| Check|  |
|  +--------+  +-----------+  | Check    |  | Check    |  +--+---+  |
|                              +----------+  +----------+     |      |
+----------------------------------+--------------------------+------+
                                   |                          |
                         +---------+--------+           +-----+-----+
                         |                  |           | Scheduler |
                         v                  v           | Service   |
              +----------+--+    +----------+--+        +-----+-----+
              | Immediate   |    | Scheduled    |             |
              | Queue       |    | Store (DB)   |<------------+
              +----------+--+    +-------------+    (polls every min)
                         |
                         v
+------------------------+------------------------------------------+
|                   PRIORITY QUEUE (Kafka)                           |
|  +---------+  +--------+  +---------+  +--------+                |
|  | URGENT  |  | HIGH   |  | NORMAL  |  | LOW    |                |
|  | topic   |  | topic  |  | topic   |  | topic  |                |
|  +---------+  +--------+  +---------+  +--------+                |
+------------------------+------------------------------------------+
                         |
                         v
+------------------------+------------------------------------------+
|                 NOTIFICATION WORKERS (20 instances)                |
|                                                                    |
|  1. Consume from priority queues (weighted round-robin)            |
|  2. Resolve user preferences (Redis cache -> DB fallback)          |
|  3. Select A/B test variant (consistent hashing)                   |
|  4. Render template (variable substitution)                        |
|  5. Route to channel delivery service                              |
+------+-------------------+-------------------+--------------------+
       |                   |                   |
       v                   v                   v
+------+------+    +-------+------+    +-------+------+
| Push        |    | SMS          |    | Email        |
| Delivery    |    | Delivery     |    | Delivery     |
| Service     |    | Service      |    | Service      |
+------+------+    +-------+------+    +-------+------+
       |                   |                   |
       v                   v                   v
+------+------+    +-------+------+    +-------+------+
| APNs / FCM  |    | Twilio /     |    | SES /        |
| / Web Push  |    | Vonage       |    | SendGrid     |
+------+------+    +-------+------+    +-------+------+
       |                   |                   |
       +-------------------+-------------------+
                           |
                           v
+------+----------------------------------------------------+
|                DELIVERY TRACKER                            |
|  +-------------+  +--------------+  +------------------+  |
|  | Status DB   |  | Webhook      |  | Retry Manager    |  |
|  | (events)    |  | Receiver     |  | (exp. backoff)   |  |
|  +-------------+  +--------------+  +------------------+  |
+------+----------------------------------------------------+
       |
       v
+------+----------------------------------------------------+
|                ANALYTICS SERVICE                           |
|  +------------------+  +------------------+               |
|  | Real-time Metrics|  | Batch Analytics  |               |
|  | (Redis counters) |  | (Data warehouse) |               |
|  +------------------+  +------------------+               |
+-----------------------------------------------------------+

+-----------------------+  +--------------------------------+
| SUPPORTING SERVICES   |  | DATA STORES                    |
| +-------------------+ |  | +-------------------+          |
| | User Preference   | |  | | PostgreSQL        |          |
| | Service           | |  | | (preferences,     |          |
| +-------------------+ |  | |  templates,       |          |
| | Template Service  | |  | |  schedules)       |          |
| +-------------------+ |  | +-------------------+          |
| | A/B Test Service  | |  | | Redis             |          |
| +-------------------+ |  | | (cache, rate      |          |
| | Device Token      | |  | |  limits,          |          |
| | Registry          | |  | |  idempotency)     |          |
| +-------------------+ |  | +-------------------+          |
+-----------------------+  | | Kafka             |          |
                           | | (priority queues)  |          |
                           | +-------------------+          |
                           | | ClickHouse /       |          |
                           | | Analytics DB       |          |
                           | +-------------------+          |
                           +--------------------------------+
```

---

## 5. Database Schema

### Core Tables

```sql
-- Notification requests
CREATE TABLE notifications (
    id              UUID PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    template_id     VARCHAR(128) NOT NULL,
    channels        JSONB NOT NULL,
    priority        VARCHAR(16) NOT NULL DEFAULT 'normal',
    data            JSONB NOT NULL,
    ab_test_id      VARCHAR(64),
    status          VARCHAR(32) NOT NULL DEFAULT 'created',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Notification delivery attempts per channel
CREATE TABLE notification_deliveries (
    id              UUID PRIMARY KEY,
    notification_id UUID REFERENCES notifications(id),
    channel         VARCHAR(16) NOT NULL,
    status          VARCHAR(32) NOT NULL,
    provider        VARCHAR(64),
    provider_msg_id VARCHAR(256),
    attempt_count   INT DEFAULT 1,
    error_message   TEXT,
    sent_at         TIMESTAMP,
    delivered_at    TIMESTAMP,
    opened_at       TIMESTAMP,
    clicked_at      TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- User preferences
CREATE TABLE user_preferences (
    user_id         VARCHAR(64) PRIMARY KEY,
    preferences     JSONB NOT NULL,
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Templates
CREATE TABLE notification_templates (
    template_id     VARCHAR(128) NOT NULL,
    version         INT NOT NULL,
    category        VARCHAR(64) NOT NULL,
    content         JSONB NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (template_id, version)
);

-- Device tokens for push notifications
CREATE TABLE device_tokens (
    id              UUID PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    platform        VARCHAR(16) NOT NULL, -- ios, android, web
    token           TEXT NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    last_used_at    TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, token)
);
```

---

## 6. Scaling Considerations

### Horizontal Scaling

```
Component          | How to Scale
-------------------+-----------------------------------------------
API Servers        | Add more instances behind load balancer
Priority Queues    | Add Kafka partitions, add consumer instances
Workers            | Add more worker instances (stateless)
Push Service       | Scale independently per platform
SMS Service        | Scale based on geographic load
Email Service      | Scale based on send volume
Redis              | Redis Cluster for sharding
PostgreSQL         | Read replicas for preferences/templates
Analytics DB       | Column-store DB (ClickHouse) for analytics
```

### Handling Traffic Spikes

Major events (Black Friday, New Year) can cause 10-100x normal traffic.

**Strategies:**
1. **Pre-warm queues:** For known campaigns, pre-generate notifications and queue them
2. **Auto-scaling workers:** Kubernetes HPA scales workers based on queue depth
3. **Backpressure:** If queues are too deep, reject low-priority notifications
4. **Circuit breakers:** If a provider is down, stop sending and buffer messages

---

## Common Mistakes

1. **No idempotency.** Without deduplication, retries send duplicate notifications. Users get the same message twice or more. Always use client-generated IDs.

2. **Single queue for all priorities.** A massive marketing campaign floods the queue, and urgent security alerts get stuck behind millions of marketing emails. Use separate queues per priority.

3. **Ignoring user preferences.** Sending notifications to users who opted out violates trust and potentially regulations like GDPR and CAN-SPAM. Always check preferences before sending.

4. **No retry backoff.** Retrying immediately and repeatedly when a provider is down creates a thundering herd and may get your account rate-limited or banned. Use exponential backoff with jitter.

5. **Tight coupling to providers.** Hardcoding Twilio or SendGrid everywhere makes it impossible to switch providers. Abstract each channel behind an interface.

6. **Synchronous delivery.** Trying to send the notification in the API request path makes the API slow and unreliable. Always queue notifications and process them asynchronously.

---

## Best Practices

1. **Use separate delivery services per channel.** Each channel has different failure modes, rate limits, and constraints. Independent services let you scale and debug each channel separately.

2. **Implement circuit breakers for external providers.** When a provider goes down, stop hammering it. Buffer notifications and retry when the circuit closes.

3. **Cache user preferences aggressively.** Preferences change rarely but are checked on every notification. Cache them in Redis with a TTL and invalidate on update.

4. **Monitor delivery rates by channel and provider.** A sudden drop in delivery rate for push notifications might mean your APNs certificate expired. Set up alerts on delivery rate thresholds.

5. **Design templates to degrade gracefully.** If a variable is missing, show a sensible default rather than crashing. Use fallback values in templates.

6. **Log every state transition.** Every notification should have a complete audit trail: created, queued, processed, sent, delivered, opened. This is essential for debugging and compliance.

---

## Quick Summary

A notification service accepts requests from clients, validates them, checks for duplicates, enforces rate limits, queues them by priority, resolves user preferences, renders templates, selects A/B variants, and dispatches through channel-specific delivery services. Failed deliveries are retried with exponential backoff. Every state transition is tracked for analytics and debugging.

---

## Key Points

- Use separate priority queues (not a single sorted queue) for different urgency levels
- Idempotency keys prevent duplicate notification delivery on retries
- User preference resolution must happen before rendering and sending
- Each delivery channel (push, SMS, email) should be an independent service
- Exponential backoff with jitter prevents thundering herd on retries
- Rate limiting per user prevents notification spam
- A/B testing uses consistent hashing so users always see the same variant
- Dead letter queues catch permanently failed notifications for manual review
- Templates separate content from delivery logic, enabling non-engineer updates

---

## Practice Questions

1. How would you handle a scenario where a user has multiple devices and should receive a push notification on all of them? What happens if one device token is invalid?

2. A marketing team wants to send 50 million promotional emails over the weekend. How would you design the system to handle this batch without impacting transactional notifications?

3. Your SMS provider reports a 30% failure rate for messages to a specific country. How would you detect this, alert on it, and route around the problem?

4. A notification contains time-sensitive information (a flash sale ending in 2 hours). How would you ensure the notification is not delivered after the sale ends?

5. How would you implement notification grouping (showing "Alice and 5 others liked your post" instead of 6 separate notifications)?

---

## Exercises

**Exercise 1: Design the Rate Limiter**

Design a Redis-based rate limiter that enforces the following rules for notifications:
- Maximum 5 push notifications per user per hour
- Maximum 10 emails per user per day
- Maximum 1 notification of the same template per user per 10 minutes

Write pseudocode for the rate limit check function. Consider what happens when Redis is temporarily unavailable.

**Exercise 2: Build a Retry Simulator**

Write a program (in any language) that simulates the retry logic for notification delivery. Your simulator should:
- Accept a failure probability (e.g., 30%)
- Implement exponential backoff with jitter
- Track how many attempts each notification needs
- Calculate the average delivery time across 1000 notifications
- Report how many notifications end up in the dead letter queue

**Exercise 3: Design the Preference Resolution Cache**

Design a caching strategy for user preferences that balances freshness with performance. Address:
- How to invalidate the cache when a user updates preferences
- How to handle cache misses without overloading the database
- How to prevent a cache stampede when Redis restarts
- What default preferences to use for a new user who has not set any

---

## What Is Next?

Now that you understand how to design a notification service that handles multiple channels, priorities, and user preferences, the next chapter will tackle another critical infrastructure component: a distributed rate limiter. You will learn the algorithms (token bucket, sliding window) and implementation details (Redis, Lua scripts) that power rate limiting at scale. Rate limiting is not just a feature of notification services -- it protects every API and service in your architecture.
