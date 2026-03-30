# Chapter 19: Notification System

## What You Will Learn

- The four types of notifications: push, SMS, email, and in-app
- How to design a notification service architecture from scratch
- How notification templates work and why they save engineering time
- How user preferences and opt-out management work
- How priority levels and throttling prevent notification fatigue
- How to track delivery status across multiple channels
- How retry logic handles transient failures
- How APNs, FCM, and SMTP deliver notifications to devices and inboxes
- How fan-out sends one notification to millions of users
- How Uber's ride notification flow works end to end

## Why This Chapter Matters

Your phone buzzes. You glance down. "Your Uber is arriving in 2 minutes." That simple message seems effortless, but behind it is a system that chose the right channel (push notification, not email), personalized the message (your driver's name, car model, license plate), delivered it in under a second, tracked whether you received it, and decided not to send you an SMS because you already saw the push notification.

Notifications are how applications stay connected with their users. A well-designed notification system increases engagement and provides timely information. A poorly designed one annoys users into disabling notifications or uninstalling the app entirely. Every company with a mobile app or web presence needs a notification system. Understanding how to build one at scale is one of the most practical system design skills you can have.

---

## Types of Notifications

There are four primary notification channels, each with different characteristics, costs, and user expectations.

### Push Notifications

Messages sent directly to a user's mobile device or web browser. They appear on the lock screen or as banners even when the app is not open.

```
  Push Notification Flow:

  +--------+                    +---------+                   +--------+
  | Your   |   Send message    | APNs or |   Deliver to      | User's |
  | Server | ----------------> | FCM     | ----------------> | Device |
  +--------+                   +---------+                   +--------+

  APNs = Apple Push Notification service (iOS)
  FCM  = Firebase Cloud Messaging (Android + Web)

  Characteristics:
  - Cost: Free (no per-message charge)
  - Delivery: Near-instant (under 1 second)
  - Rich content: Images, buttons, sounds
  - Requires: User permission, device token
  - Risk: Users can disable or uninstall
```

### SMS (Text Messages)

Messages sent to a user's phone number via cellular networks. They work on any phone, even without internet.

```
  SMS Flow:

  +--------+                    +----------+                  +--------+
  | Your   |   API call        | Twilio / |   Cellular       | User's |
  | Server | ----------------> | AWS SNS  | ----------------> | Phone  |
  +--------+                   +----------+                  +--------+

  Characteristics:
  - Cost: $0.01-$0.05 per message (expensive at scale)
  - Delivery: 1-30 seconds
  - Content: Text only, 160 characters
  - Requires: Phone number
  - Works without internet or smartphone
  - Best for: Security codes (2FA), critical alerts
```

### Email

Messages delivered to a user's email inbox. Rich HTML content with links, images, and formatting.

```
  Email Flow:

  +--------+                    +-----------+                 +--------+
  | Your   |   SMTP/API        | SendGrid /|   Email          | User's |
  | Server | ----------------> | SES /     | ----------------> | Inbox  |
  +--------+                   | Mailgun   |                  +--------+
                               +-----------+

  Characteristics:
  - Cost: $0.0001-$0.001 per email (cheap)
  - Delivery: Seconds to minutes
  - Rich content: HTML, images, attachments
  - Requires: Email address
  - Risk: Spam filters may block delivery
  - Best for: Receipts, newsletters, detailed updates
```

### In-App Notifications

Messages displayed within your application when the user is actively using it. They appear as badges, banners, or notification feeds.

```
  In-App Notification Flow:

  +--------+                    +-----------+                 +--------+
  | Your   |   WebSocket or    | Client    |   Show in        | User's |
  | Server | ----------------> | App       | ----------------> | Screen |
  +--------+   Server-Sent     +-----------+   notification   +--------+
               Events (SSE)                     center

  Characteristics:
  - Cost: Free (within your infrastructure)
  - Delivery: Instant (if user is online)
  - Rich content: Any UI element
  - Requires: User to be in the app
  - No permissions needed
  - Best for: Activity feeds, social updates, badges
```

### Channel Comparison

| Feature | Push | SMS | Email | In-App |
|---|---|---|---|---|
| Cost per message | Free | $0.01-0.05 | $0.0001 | Free |
| Delivery speed | <1 second | 1-30 seconds | Seconds-minutes | Instant |
| Reach | App installed | Any phone | Any email | App open |
| Rich content | Limited | No | Yes | Yes |
| User permission | Required | Varies by country | CAN-SPAM rules | None |
| Offline delivery | Yes (queued) | Yes | Yes | No |

---

## Notification Service Architecture

Let us design the architecture for a notification system that handles all four channels at scale.

```
  Notification Service Architecture:

  +----------+    +-----------+    +------------------+    +-----------+
  | Order    |--->|           |    |                  |    |           |
  | Service  |    |           |    |  NOTIFICATION    |    | Template  |
  +----------+    |           |    |  SERVICE         |    | Engine    |
                  |  API      |    |                  |    |           |
  +----------+    |  GATEWAY  |--->| 1. Validate      |--->| Render    |
  | Payment  |--->|           |    | 2. Check prefs   |    | message   |
  | Service  |    |           |    | 3. Apply priority |    | from      |
  +----------+    |           |    | 4. Route channel  |    | template  |
                  |           |    | 5. Rate limit     |    +-----------+
  +----------+    |           |    |                  |
  | Auth     |--->|           |    +--------+---------+
  | Service  |    +-----------+             |
  +----------+                    +---------+---------+
                                  |                   |
                           +------v------+     +------v------+
                           | Priority    |     | User Prefs  |
                           | Queue       |     | Store       |
                           | (Kafka)     |     | (Database)  |
                           +------+------+     +-------------+
                                  |
                    +-------------+-------------+
                    |             |             |
              +-----v----+ +-----v----+ +-----v----+
              | Push      | | SMS      | | Email    |
              | Worker    | | Worker   | | Worker   |
              +-----+----+ +-----+----+ +-----+----+
                    |             |             |
              +-----v----+ +-----v----+ +-----v----+
              | APNs/FCM | | Twilio/  | | SES/     |
              |          | | SNS      | | SendGrid |
              +----------+ +----------+ +----------+
                    |             |             |
              +-----v-----------v-------------v----+
              |        Delivery Tracker             |
              | (Track sent, delivered, opened,     |
              |  failed, bounced)                   |
              +------------------------------------+
```

### Request Flow

```
  Notification Request:

  {
    "user_id": "user_123",
    "type": "order_shipped",
    "data": {
      "order_id": "ORD-789",
      "tracking_number": "FX123456",
      "carrier": "FedEx",
      "eta": "2024-01-17"
    },
    "channels": ["push", "email"],
    "priority": "high"
  }

  Processing Steps:

  1. VALIDATE
     - Is user_id valid?
     - Is notification type recognized?
     - Is required data present?

  2. CHECK USER PREFERENCES
     - Has user opted out of this notification type?
     - Has user disabled this channel?
     - What is user's preferred language?
     - What is user's timezone?

  3. APPLY PRIORITY AND THROTTLING
     - Is this high, medium, or low priority?
     - Has user received too many notifications today?
     - Is this a duplicate of a recent notification?

  4. RENDER TEMPLATE
     - Load template for "order_shipped"
     - Fill in data: order ID, tracking number, carrier
     - Localize to user's language
     - Generate push text, email HTML, SMS text

  5. ROUTE TO CHANNEL WORKERS
     - Enqueue push notification to push worker
     - Enqueue email to email worker
     - Each worker handles delivery independently

  6. TRACK DELIVERY
     - Record: sent at, delivered at, opened at
     - Handle failures: retry or fallback to another channel
```

---

## Notification Templates

Templates separate the notification content from the notification logic. Instead of hardcoding messages, you define templates with placeholders that are filled in at send time.

```
  Template System:

  Template: "order_shipped"
  +---------------------------------------------------------+
  | Push Title: "Your order is on the way!"                  |
  | Push Body:  "Order {{order_id}} shipped via {{carrier}}. |
  |              Expected delivery: {{eta}}"                 |
  |                                                          |
  | Email Subject: "Your order {{order_id}} has shipped"     |
  | Email Body:   (HTML template with tracking link)         |
  |                                                          |
  | SMS: "Your order {{order_id}} shipped. Track: {{url}}"   |
  +---------------------------------------------------------+

  Data: {order_id: "ORD-789", carrier: "FedEx", eta: "Jan 17"}

  Rendered Push:
  Title: "Your order is on the way!"
  Body:  "Order ORD-789 shipped via FedEx. Expected delivery: Jan 17"

  Benefits:
  - Non-engineers can update notification text
  - Supports multiple languages (one template per language)
  - A/B test different messages without code changes
  - Consistent formatting across all notifications
```

### Template Storage

```
  Template Storage:

  +----+------------------+----------+------+-----------------+
  | ID | Type             | Channel  | Lang | Content         |
  +----+------------------+----------+------+-----------------+
  | 1  | order_shipped    | push     | en   | "Your order..." |
  | 2  | order_shipped    | push     | es   | "Tu pedido..."  |
  | 3  | order_shipped    | email    | en   | "<html>..."     |
  | 4  | order_shipped    | sms      | en   | "Order {{id}}.."|
  | 5  | payment_received | push     | en   | "Payment of..." |
  | 6  | payment_received | email    | en   | "<html>..."     |
  +----+------------------+----------+------+-----------------+

  Lookup: type + channel + language = template content
```

---

## User Preferences

Users must be able to control what notifications they receive and how they receive them. This is not just good UX -- it is legally required in many jurisdictions.

```
  User Preferences Model:

  User: alice_123
  +-------------------------+------+-----+-------+--------+
  | Notification Type       | Push | SMS | Email | In-App |
  +-------------------------+------+-----+-------+--------+
  | Order updates           |  ON  | OFF |  ON   |   ON   |
  | Promotional offers      | OFF  | OFF |  ON   |  OFF   |
  | Security alerts         |  ON  |  ON |  ON   |   ON   |
  | Social (likes, follows) |  ON  | OFF | OFF   |   ON   |
  | Price drop alerts       |  ON  | OFF |  ON   |   ON   |
  +-------------------------+------+-----+-------+--------+

  Quiet Hours: 10:00 PM - 8:00 AM (user's timezone)
  Language: English
  Timezone: America/New_York

  Processing Logic:
  1. Receive notification request for alice_123
  2. Look up preferences for this notification type
  3. Filter out disabled channels
  4. Check quiet hours (delay if in quiet period)
  5. Send only to enabled channels
```

### Global Opt-Out

Every notification must include an unsubscribe mechanism. For email, this is legally required (CAN-SPAM, GDPR). For push notifications, the OS provides a system-level toggle.

```
  Unsubscribe Flow:

  Email footer: "Unsubscribe from order updates"
       |
       v
  +--------+  Click   +-------------+  Update    +----------+
  | User   | -------> | Unsubscribe | ---------> | Prefs    |
  | Email  |          | Service     |            | Database |
  +--------+          +-------------+            +----------+
                            |
                      Generate one-time
                      token (no login needed)

  Important:
  - One-click unsubscribe (no login required)
  - Confirm the unsubscribe on a landing page
  - Take effect immediately
  - Include "manage all preferences" link
```

---

## Priority and Throttling

Not all notifications are equal. A security alert ("Someone logged into your account from a new device") is far more important than a promotional email ("20% off sneakers this weekend"). Priority and throttling systems ensure important notifications get through while preventing notification fatigue.

### Priority Levels

```
  Priority Levels:

  +----------+-------------------+---------------------------+
  | Priority | Examples          | Behavior                  |
  +----------+-------------------+---------------------------+
  | CRITICAL | Security alerts,  | Bypass all throttling,    |
  |          | 2FA codes,        | send immediately, wake    |
  |          | fraud detection   | device, override quiet hrs|
  +----------+-------------------+---------------------------+
  | HIGH     | Order shipped,    | Send immediately,         |
  |          | payment received, | respect quiet hours,      |
  |          | ride arriving     | bypass daily limits       |
  +----------+-------------------+---------------------------+
  | MEDIUM   | Social updates,   | Send within minutes,      |
  |          | price drops,      | respect all limits,       |
  |          | recommendations   | can be batched            |
  +----------+-------------------+---------------------------+
  | LOW      | Newsletters,      | Batch and send at optimal |
  |          | promotions,       | time, first to be dropped |
  |          | weekly digests    | if user near daily limit  |
  +----------+-------------------+---------------------------+
```

### Throttling

```
  Throttling Rules:

  Per-User Limits:
  - Max 5 push notifications per hour
  - Max 20 push notifications per day
  - Max 1 SMS per hour (except CRITICAL)
  - Max 3 emails per day (except transactional)

  Throttling Decision Tree:
  +-------------------+
  | New notification  |
  +--------+----------+
           |
           v
  +--------+----------+
  | Priority =        |
  | CRITICAL?         |
  +--------+----------+
      YES  |     | NO
           v     v
  Send     +-----+----------+
  now      | User at daily  |
           | limit?         |
           +-----+----------+
            YES  |     | NO
                 v     v
           +-----+  +--+----------+
           | DROP |  | In quiet   |
           | (log)|  | hours?     |
           +------+  +--+---------+
                   YES  |     | NO
                        v     v
                  +-----+  +--+------+
                  |DELAY |  | SEND   |
                  |until |  | NOW    |
                  |8 AM  |  +--------+
                  +------+
```

### Batching

Low-priority notifications can be batched together instead of sending one at a time.

```
  Batching Example:

  Without batching (annoying):
  10:01 AM - "Alice liked your photo"
  10:03 AM - "Bob liked your photo"
  10:07 AM - "Charlie liked your photo"
  10:12 AM - "Diana liked your photo"
  10:15 AM - "Eve liked your photo"

  With batching (pleasant):
  10:15 AM - "Alice, Bob, and 3 others liked your photo"

  Implementation:
  - Collect notifications of the same type for a time window (5-15 min)
  - If only 1 notification, send individually
  - If 2-3, list names: "Alice and Bob liked your photo"
  - If 4+, summarize: "Alice, Bob, and 3 others liked your photo"
```

---

## Delivery Tracking

After sending a notification, you need to know: Was it delivered? Was it opened? Did the user take action? This data drives optimization and debugging.

```
  Notification Lifecycle:

  +----------+    +--------+    +-----------+    +--------+    +--------+
  | CREATED  |--->| QUEUED |--->| SENT      |--->|DELIVERED|-->| OPENED |
  +----------+    +--------+    +-----------+    +--------+    +--------+
       |               |             |                              |
       v               v             v                              v
  +---------+    +---------+   +-----------+                  +---------+
  | FILTERED|    | DROPPED |   |  FAILED   |                  | CLICKED |
  | (prefs) |    | (thrtl) |   | (bounce/  |                  | (CTA)   |
  +---------+    +---------+   |  timeout) |                  +---------+
                               +-----------+
                                     |
                               +-----v-----+
                               |  RETRYING  |
                               +-----------+


  Delivery Tracking Table:
  +----------+----------+---------+--------+-----------+---------+
  | notif_id | user_id  | channel | status | timestamp | details |
  +----------+----------+---------+--------+-----------+---------+
  | n_001    | user_123 | push    | opened | 10:05:03  |         |
  | n_001    | user_123 | email   | sent   | 10:05:01  | SES ID  |
  | n_002    | user_456 | push    | failed | 10:06:00  | expired |
  |          |          |         |        |           | token   |
  | n_003    | user_789 | sms     | delivd | 10:07:02  | Twilio  |
  +----------+----------+---------+--------+-----------+---------+
```

### Delivery Metrics

```
  Key Metrics to Track:

  +-----------------------------------+
  | Metric            | Target        |
  +-----------------------------------+
  | Delivery rate     | > 95%         |
  | Push open rate    | > 5%          |
  | Email open rate   | > 20%         |
  | Click-through rate| > 2%          |
  | Unsubscribe rate  | < 0.5%       |
  | Bounce rate       | < 2%          |
  | Spam complaint    | < 0.1%       |
  | Avg delivery time | < 5 seconds   |
  +-----------------------------------+
```

---

## Retry Logic

Notification delivery can fail for many reasons: the push service is temporarily down, the email bounces, or the SMS gateway is overloaded. A good retry strategy handles transient failures without overwhelming downstream services.

```
  Retry Strategy:

  Attempt 1: Send immediately
       |
       FAIL (timeout)
       |
  Wait 1 second
       |
  Attempt 2: Retry
       |
       FAIL (server error)
       |
  Wait 4 seconds (exponential backoff)
       |
  Attempt 3: Retry
       |
       FAIL (server error)
       |
  Wait 16 seconds
       |
  Attempt 4: Retry
       |
       FAIL
       |
  Wait 64 seconds
       |
  Attempt 5: Final retry
       |
       FAIL
       |
  Move to Dead Letter Queue
  Alert operations team
  Consider fallback channel


  Exponential Backoff with Jitter:

  Delay = min(base * 2^attempt + random_jitter, max_delay)

  Attempt 1: 1s  + jitter (0-500ms)
  Attempt 2: 4s  + jitter (0-500ms)
  Attempt 3: 16s + jitter (0-500ms)
  Attempt 4: 64s + jitter (0-500ms)
  Attempt 5: 120s (max)

  Jitter prevents thundering herd:
  Without jitter: 1000 failed notifications all retry at exactly 4s
  With jitter:    1000 retries spread across 4.0s - 4.5s
```

### Channel Fallback

If the primary channel fails, fall back to an alternative channel.

```
  Channel Fallback:

  Notification: "Your ride is arriving"
  Primary channel: Push notification

  +--------+     Push      +------+
  | Server | ------------> | APNs |  FAIL (token expired)
  +--------+               +------+
       |
       | Fallback to SMS
       v
  +--------+     SMS       +--------+
  | Server | ------------> | Twilio |  SUCCESS
  +--------+               +--------+

  Fallback rules:
  - CRITICAL: Push -> SMS -> Email (try all)
  - HIGH: Push -> Email
  - MEDIUM: Push only (no fallback)
  - LOW: Email only (no fallback)
```

---

## APNs, FCM, and SMTP

These are the three core delivery protocols for push notifications and email.

### Apple Push Notification Service (APNs)

```
  APNs Architecture:

  +--------+    HTTP/2     +------+    Persistent    +--------+
  | Your   | -----------> | APNs | -- Connection --> | iPhone |
  | Server |              |      |                   +--------+
  +--------+              +------+
                              |
                         +----+----+
                         | Features|
                         +---------+
                         | - HTTP/2 multiplexing
                         | - JWT or certificate auth
                         | - Immediate feedback on errors
                         | - Device token per app
                         | - Priority: 10 (immediate)
                         |           5 (power-saving)
                         | - TTL: how long to keep trying
                         +---------+

  Device Token:
  When a user installs your app and allows notifications,
  APNs gives the app a unique device token.
  Your server stores this token and uses it to send pushes.

  Token lifecycle:
  - Generated on app install
  - Can change (user reinstalls, new device)
  - Your server must handle token updates
  - Invalid tokens mean the app was uninstalled
```

### Firebase Cloud Messaging (FCM)

```
  FCM Architecture:

  +--------+    HTTPS      +------+                  +---------+
  | Your   | -----------> | FCM  | ---- Push -----> | Android |
  | Server |              |      | ---- Push -----> | Web     |
  +--------+              +------+ ---- Push -----> | iOS*    |
                              |
                         +----+----+
                         | Features|
                         +---------+
                         | - Supports Android, iOS, Web
                         | - Topics (subscribe groups)
                         | - Conditions (topic combos)
                         | - Data messages (app handles)
                         | - Notification messages (FCM shows)
                         | - Message batching
                         +---------+

  * FCM can also deliver to iOS through APNs.

  Topics:
  Instead of sending to individual tokens,
  subscribe users to topics and send to the topic.

  Example:
  Topic: "breaking_news" -> 1 million subscribers
  One API call to FCM -> delivered to all subscribers
```

### SMTP (Simple Mail Transfer Protocol)

```
  Email Delivery Path:

  +--------+   SMTP/API   +-----------+   SMTP    +----------+   SMTP    +--------+
  | Your   | -----------> | Email     | --------> | Receiving| --------> | User's |
  | Server |              | Service   |           | Mail     |           | Inbox  |
  +--------+              | (SES,     |           | Server   |           +--------+
                          | SendGrid) |           | (Gmail)  |
                          +-----------+           +----------+

  Email Deliverability Factors:
  +--------------------------------------------------+
  | Factor           | Why It Matters                 |
  +--------------------------------------------------+
  | SPF Record       | Proves your server is          |
  |                  | authorized to send email       |
  +--------------------------------------------------+
  | DKIM Signature   | Proves email was not modified  |
  |                  | in transit                     |
  +--------------------------------------------------+
  | DMARC Policy     | Tells receivers what to do     |
  |                  | with unauthenticated email     |
  +--------------------------------------------------+
  | Sender reputation| Based on bounce rate, spam     |
  |                  | complaints, engagement         |
  +--------------------------------------------------+
  | List hygiene     | Remove invalid addresses,      |
  |                  | honor unsubscribes promptly    |
  +--------------------------------------------------+
```

---

## Fan-Out: Sending to Millions

When you need to send a notification to millions of users (a product announcement, a breaking news alert), you need a fan-out strategy.

### The Challenge

```
  The Fan-Out Problem:

  "Send a notification to all 10 million users"

  Naive approach:
  FOR each user in 10,000,000 users:
    send_notification(user)

  Time: 10,000,000 x 50ms = 500,000 seconds = 5.8 DAYS

  That is obviously not going to work.
```

### Fan-Out Architecture

```
  Fan-Out Architecture:

  Step 1: Create notification
  +----------+    "New feature launched!"    +-------------+
  | Admin    | ---------------------------> | Notification|
  | Console  |                              | Service     |
  +----------+                              +------+------+
                                                   |
  Step 2: Fan-out to user segments                 |
                                                   v
                                            +------+------+
                                            | Fan-Out     |
                                            | Service     |
                                            +------+------+
                                                   |
                    +------------------------------+------------------------------+
                    |                              |                              |
                    v                              v                              v
           +-------+-------+             +--------+------+             +---------+-----+
           | Segment:      |             | Segment:      |             | Segment:      |
           | Users A-G     |             | Users H-P     |             | Users Q-Z     |
           | (3.3M users)  |             | (3.3M users)  |             | (3.3M users)  |
           +-------+-------+             +--------+------+             +---------+-----+
                   |                              |                              |
            Kafka partition 0             Kafka partition 1             Kafka partition 2
                   |                              |                              |
           +-------v-------+             +--------v------+             +---------v-----+
           | Worker Pool   |             | Worker Pool   |             | Worker Pool   |
           | (20 workers)  |             | (20 workers)  |             | (20 workers)  |
           | 50,000/sec    |             | 50,000/sec    |             | 50,000/sec    |
           +---------------+             +---------------+             +---------------+

  Total throughput: 150,000 notifications/second
  Time to send to 10M users: ~67 seconds

  Key techniques:
  1. Partition users into segments
  2. Use Kafka to buffer and distribute work
  3. Multiple worker pools process in parallel
  4. Batch API calls to push services (FCM supports 500/batch)
  5. Use topics for broadcast (FCM topics, APNs groups)
```

---

## Uber Ride Notification Flow

Let us trace the complete notification flow for an Uber ride, from request to completion.

```
  Uber Ride Notification Flow:

  Event 1: Ride Requested
  +---------+   Request    +----------+   Push    +----------+
  | Rider   | -----------> | Ride     | -------> | Driver   |
  | App     |              | Service  |          | App      |
  +---------+              +----------+          +----------+
                                |
                          "Looking for a driver..."
                                |
                                v
                          Push to Rider: "Finding your ride..."

  Event 2: Driver Accepted
  +---------+   Accept     +----------+
  | Driver  | -----------> | Ride     |
  | App     |              | Service  |
  +---------+              +----+-----+
                                |
                    +-----------+-----------+
                    |                       |
                    v                       v
              Push to Rider:          In-App Update:
              "John is on the way    Show driver photo,
               in a Toyota Camry    car details, ETA
               (ABC 1234)"          on map

  Event 3: Driver Arriving
  +---------+   Location   +----------+   Geofence    +----------+
  | Driver  |   update     | Location | -- trigger --> | Notif.   |
  | App     | -----------> | Service  |               | Service  |
  +---------+              +----------+               +----+-----+
                                                           |
                    +--------------------------------------+
                    |                       |
                    v                       v
              Push to Rider:          SMS Fallback:
              "Your driver is         "Your Uber is
               arriving now!"         arriving. Look
                                      for Toyota Camry
                                      ABC 1234"

  Event 4: Ride Started
  +---------+   Start ride  +----------+
  | Driver  | -----------> | Ride     |
  | App     |              | Service  |
  +---------+              +----+-----+
                                |
                                v
                          In-App to Rider:
                          Show route, ETA,
                          live tracking

  Event 5: Ride Completed
  +---------+   End ride    +----------+
  | Driver  | -----------> | Ride     |
  | App     |              | Service  |
  +---------+              +----+-----+
                                |
                    +-----------+-----------+----------+
                    |                       |          |
                    v                       v          v
              Push to Rider:          Email:      In-App:
              "Trip complete!        Receipt     Rate your
               $24.50"              with map,    driver
                                    fare         (1-5 stars)
                                    breakdown

  Event 6: Rating Received
  +---------+   5 stars    +----------+
  | Rider   | -----------> | Rating   |
  | App     |              | Service  |
  +---------+              +----+-----+
                                |
                                v
                          Push to Driver:
                          "You received a
                           5-star rating!"


  Channel Selection Logic:

  +-------------------+--------+------+-------+--------+
  | Event             | Push   | SMS  | Email | In-App |
  +-------------------+--------+------+-------+--------+
  | Finding driver    | YES    | no   | no    | YES    |
  | Driver accepted   | YES    | no   | no    | YES    |
  | Driver arriving   | YES    | YES* | no    | YES    |
  | Ride started      | no     | no   | no    | YES    |
  | Ride completed    | YES    | no   | YES   | YES    |
  | Rating received   | YES    | no   | no    | YES    |
  +-------------------+--------+------+-------+--------+

  * SMS only if push delivery fails (fallback)
```

---

## Trade-offs

| Decision | Option A | Option B |
|---|---|---|
| Delivery | Best-effort (fast, may lose) | Guaranteed (reliable, slower, complex) |
| Channel | Single channel (simple) | Multi-channel with fallback (reliable, costly) |
| Timing | Send immediately (real-time) | Batch and send at optimal time (fewer interruptions) |
| Template | Hardcoded messages (simple, inflexible) | Template engine (flexible, more moving parts) |
| Fan-out | Sequential (simple, slow) | Parallel with Kafka (fast, complex infrastructure) |
| Preference | Opt-out only (more reach) | Opt-in only (less reach, higher engagement) |
| Priority queue | Single queue (simple) | Multiple priority queues (complex, better UX) |

---

## Common Mistakes

1. **Not respecting user preferences.** Sending notifications to users who opted out is not just bad UX -- it violates regulations like GDPR and CAN-SPAM. Always check preferences before sending.

2. **Sending too many notifications.** Notification fatigue is the number one reason users disable push notifications or uninstall apps. Implement throttling and batching.

3. **Not handling token expiration.** Push notification device tokens expire when users uninstall the app or get a new device. If you keep sending to expired tokens, your sender reputation drops and delivery rates suffer.

4. **No retry with backoff.** Transient failures are normal. Retrying immediately (or not at all) either overwhelms the downstream service or loses the notification. Use exponential backoff with jitter.

5. **Ignoring email deliverability.** Without SPF, DKIM, and DMARC records, your emails land in spam. Monitor bounce rates and spam complaints.

6. **No delivery tracking.** If you do not track delivery status, you have no idea if notifications are actually reaching users. You cannot improve what you do not measure.

---

## Best Practices

1. **Implement user preference management from day one.** Let users control notification types, channels, and quiet hours. This reduces unsubscribes and improves engagement.

2. **Use templates for all notification content.** Separate content from code. This enables localization, A/B testing, and non-engineer content updates.

3. **Prioritize notifications.** Not all notifications are equal. Security alerts should bypass throttling. Promotions should be batched. Use at least three priority levels.

4. **Track delivery end-to-end.** Record created, queued, sent, delivered, opened, and clicked timestamps. Monitor delivery rates and alert on drops.

5. **Implement exponential backoff with jitter for retries.** Start with a 1-second delay, double each time, add random jitter, and cap at a maximum delay. After a set number of retries, move to a dead letter queue.

6. **Use channel fallback for critical notifications.** If push fails, try SMS. If SMS fails, try email. Ensure the user receives critical information through at least one channel.

7. **Clean up invalid tokens regularly.** When APNs or FCM reports an invalid token, remove it immediately. Sending to invalid tokens damages your sender reputation.

8. **Batch low-priority notifications.** Combine multiple social notifications ("Alice, Bob, and 3 others liked your photo") instead of sending five separate notifications.

---

## Quick Summary

A notification system delivers messages to users through four channels: push notifications (via APNs for iOS and FCM for Android), SMS (via providers like Twilio), email (via SMTP services like SES or SendGrid), and in-app notifications (via WebSockets or polling). The architecture consists of a notification service that validates requests, checks user preferences, applies priority and throttling rules, renders templates, and routes messages to channel-specific workers. Templates separate content from logic, enabling localization and A/B testing. User preferences give users control over what they receive and through which channels. Priority levels and throttling prevent notification fatigue. Delivery tracking records the lifecycle of each notification from creation through delivery and engagement. Retry logic with exponential backoff handles transient failures. Fan-out architectures using Kafka and parallel workers enable sending to millions of users in seconds.

---

## Key Points

- Four notification channels (push, SMS, email, in-app) each have different costs, latencies, and capabilities
- User preferences and opt-out management are both a UX requirement and a legal obligation
- Priority levels ensure critical notifications like security alerts always get through
- Throttling and batching prevent notification fatigue and reduce unsubscribes
- Templates separate content from code, enabling localization and A/B testing
- Retry with exponential backoff and jitter handles transient delivery failures gracefully
- Channel fallback ensures critical notifications reach users even when one channel fails
- Delivery tracking (sent, delivered, opened, clicked) is essential for measuring effectiveness

---

## Practice Questions

1. Your notification system sends 10 million push notifications per day. Your delivery rate has dropped from 95% to 70% over the past month. What are the most likely causes? How would you investigate and fix the problem?

2. You need to send a price drop alert to 5 million users within 30 minutes. Each push notification takes 50 milliseconds to send. How would you design the fan-out system? What infrastructure do you need?

3. A user receives a push notification for a security alert but does not see it (their phone was off). How would you ensure they receive the alert through another channel? What is the fallback timeline?

4. Your email open rate dropped from 25% to 8% after a new marketing campaign. Your spam complaint rate is at 0.3%. What happened? How would you recover your sender reputation?

5. Design the notification preference system for a social media app. What notification types would you define? What default settings would you use? How would you handle users who have not set preferences?

---

## Exercises

**Exercise 1: Design a Multi-Channel Notification Pipeline**

Design the complete notification architecture for a banking app. Requirements: transaction alerts (immediate), monthly statements (batch email), security alerts (multi-channel with fallback), marketing offers (user-opted-in only). Include the priority system, throttling rules, template structure, and delivery tracking. Draw the architecture diagram.

**Exercise 2: Build a Fan-Out System**

Your news app has 20 million users. Breaking news must reach all users within 2 minutes. Design the fan-out architecture. Calculate the required throughput, number of workers, and Kafka partition count. Consider that FCM supports batches of 500 messages per API call. Handle the case where 5% of device tokens are invalid.

**Exercise 3: Notification Analytics Dashboard**

Design the data model and queries for a notification analytics dashboard. The dashboard must show: notifications sent per channel per hour, delivery rates, open rates, click-through rates, unsubscribe rates, and average delivery latency. Define the database schema, the data collection pipeline, and how you would compute real-time vs. daily aggregate metrics.

---

## What Is Next?

You now know how to design notification systems that reach users through the right channel at the right time with the right message. But how do you know your notification system (and the rest of your infrastructure) is actually working? How do you detect problems before users complain? In the next chapter, you will learn about logging, monitoring, and observability: how to instrument your systems with metrics, logs, and traces so you can see what is happening inside your distributed system in real time.
