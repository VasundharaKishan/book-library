# Chapter 25: Designing a Chat System (WhatsApp / Messenger)

Billions of messages fly across chat systems every day. When you send "on my way" to a friend, you expect it to arrive instantly, in order, and exactly once. Behind that simple interaction lies a sophisticated system of persistent connections, message queues, ordering guarantees, and offline delivery mechanisms.

In this chapter we will design a chat system like WhatsApp or Facebook Messenger from scratch. You will learn why WebSockets are essential for real-time messaging, how to guarantee message ordering in a distributed system, how group chat fan-out works, how offline delivery ensures no message is ever lost, and how presence indicators ("online", "last seen") function at scale. This is one of the most rewarding system design exercises because it touches real-time communication, distributed systems, and encryption all in one problem.

---

## 25.1 Understanding the Problem

A chat system needs to support:

1. **One-to-one (1:1) messaging** -- send a text, image, or video to another user.
2. **Group messaging** -- send a message to a group of users (up to hundreds or thousands of members).
3. **Online/offline status** -- show whether a user is currently online and when they were last seen.
4. **Read receipts** -- indicate when a message has been delivered and read.
5. **Push notifications** -- alert users of new messages when the app is in the background.

### What Makes Chat Systems Unique?

Unlike the feed-based systems in previous chapters, chat requires **real-time, bidirectional communication**. HTTP's request-response model does not work well here because the server needs to push messages to clients as they arrive, without the client constantly polling. This drives the fundamental architecture choice: **persistent connections** (WebSockets or long polling).

Another unique challenge is **ordering**. In a feed, a post appearing a few seconds late is fine. In a chat, if message B arrives before message A, the conversation becomes confusing. Ordering guarantees are critical.

---

## 25.2 Requirements

### Functional Requirements

| # | Requirement | Description |
|---|-------------|-------------|
| F1 | **1:1 chat** | Send text, image, and video messages between two users. |
| F2 | **Group chat** | Groups of up to 500 members. Any member can send messages. |
| F3 | **Online status** | Show whether a user is online, and if not, their "last seen" time. |
| F4 | **Read receipts** | Show sent, delivered, and read indicators for each message. |
| F5 | **Push notifications** | Notify users of new messages when the app is in the background. |
| F6 | **Message history** | Users can scroll back through past messages. |

### Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NF1 | **Low latency** | Messages delivered in under 100 ms when both users are online. |
| NF2 | **Reliability** | No message is ever lost. Exactly-once delivery semantics. |
| NF3 | **Ordering** | Messages in a conversation appear in the order they were sent. |
| NF4 | **Scalability** | 1 billion connected users, 100 billion messages per day. |
| NF5 | **Availability** | 99.99% uptime. Chat must always work. |

### Out of Scope

- Voice and video calls.
- Stories and status updates.
- End-to-end encryption implementation details (we will discuss the concept).
- Payment features.

---

## 25.3 Back-of-the-Envelope Estimation

### Traffic

| Metric | Value |
|--------|-------|
| Connected users (concurrent) | 500 million |
| Messages per day | 100 billion |
| Messages per second | 100B / 86,400 ≈ **1.16 million msg/s** |
| Average message size | 200 bytes (text) |
| Messages with media | ~10% |

### Storage

Text messages over five years:

```
100B msg/day x 365 x 5 = 182.5 trillion messages
182.5T x 200 bytes ≈ 36.5 PB (text only)
```

Media messages (10% of total):

```
10B media msg/day x average 200 KB = 2 PB/day
Over 5 years: ~3,650 PB = 3.65 EB
```

### Connection Management

Each connected user maintains one WebSocket connection. With 500 million concurrent connections:

```
Each connection uses ~10 KB of memory
500M x 10 KB = 5 TB of RAM just for connections
At 100K connections per server: 5,000 chat servers
```

### Bandwidth

```
1.16M msg/s x 200 bytes = 232 MB/s (text only)
Plus media: roughly 10x = ~2.3 GB/s total
```

---

## 25.4 High-Level Design

```
┌───────────┐                              ┌───────────┐
│  Client A  │◀═══════ WebSocket ════════▶│  Chat      │
└───────────┘                              │  Server    │
                                           │  Cluster   │
┌───────────┐                              │            │
│  Client B  │◀═══════ WebSocket ════════▶│  (5,000    │
└───────────┘                              │  servers)  │
                                           └─────┬──────┘
                                                 │
                    ┌────────────────────────────┼─────────────────┐
                    │                            │                 │
             ┌──────▼──────┐           ┌────────▼────────┐  ┌────▼─────┐
             │  Message    │           │  Session/        │  │ Presence │
             │  Queue      │           │  Connection     │  │ Service  │
             │  (Kafka)    │           │  Registry       │  │          │
             └──────┬──────┘           │  (Redis)        │  └────┬─────┘
                    │                  └─────────────────┘       │
             ┌──────▼──────┐                              ┌─────▼──────┐
             │  Message    │                              │  Presence  │
             │  Store      │                              │  Cache     │
             │ (Cassandra) │                              │  (Redis)   │
             └─────────────┘                              └────────────┘
                    │
             ┌──────▼──────┐           ┌─────────────────┐
             │  Push       │           │  Media Service   │
             │ Notification│           │  (S3 + CDN)     │
             │  Service    │           └─────────────────┘
             └─────────────┘
```

### WebSocket Connection Flow

1. Client opens the app and initiates a WebSocket handshake with a chat server (via load balancer).
2. The load balancer assigns the client to a specific chat server using sticky routing (by user ID).
3. The chat server registers the connection in the **Session Registry** (Redis): `user_id -> chat_server_id`.
4. The WebSocket connection stays open for the duration of the session.
5. If the connection drops, the client reconnects (possibly to a different server), and the registry is updated.

### Message Flow: 1:1 Chat

```
Alice sends "Hello" to Bob:

1. Alice ──WebSocket──▶ Chat Server A
2. Chat Server A:
   a. Validates the message
   b. Generates a message ID (Snowflake)
   c. Stores the message in Message Store (Cassandra)
   d. Looks up Bob's connection in Session Registry
3. IF Bob is online:
   Chat Server A ──▶ Chat Server B (where Bob is connected)
   Chat Server B ──WebSocket──▶ Bob
4. IF Bob is offline:
   Chat Server A ──▶ Push Notification Service ──▶ Bob's phone
5. Chat Server A ──WebSocket──▶ Alice: "message delivered" ✓
```

### Message Flow: Group Chat

```
Alice sends "Meeting at 3pm" to a group of 200 members:

1. Alice ──WebSocket──▶ Chat Server A
2. Chat Server A:
   a. Validates the message
   b. Stores in Message Store
   c. Looks up all 200 group members' connections
3. For each online member:
   Route message to their chat server
4. For each offline member:
   Send push notification
```

---

## 25.5 Deep Dive

### 25.5.1 WebSocket vs. Long Polling

| Aspect | WebSocket | Long Polling |
|--------|-----------|-------------|
| **Connection** | Persistent, full-duplex | Repeated HTTP requests |
| **Latency** | Very low (sub-100 ms) | Higher (HTTP overhead per request) |
| **Server resources** | One connection per user | New connection per poll cycle |
| **Firewall/proxy support** | Sometimes blocked | Works everywhere (standard HTTP) |
| **Scalability** | More efficient at scale | Wastes bandwidth with empty responses |
| **Complexity** | More complex (connection management, reconnection) | Simpler to implement |

**Our choice: WebSocket** with long polling as a fallback for clients behind restrictive firewalls.

**Why WebSocket wins**: At 500 million concurrent users, long polling would create enormous overhead from constantly opening and closing HTTP connections. WebSocket keeps a single TCP connection open, enabling instant message delivery in both directions.

**Fallback strategy**: If a WebSocket connection fails after three attempts, fall back to long polling. The client polls every 3-5 seconds, and the server holds the request open for up to 30 seconds if no new messages are available (reducing unnecessary round trips).

### 25.5.2 Chat Server Architecture

Each chat server handles ~100,000 concurrent WebSocket connections. The server:

- Maintains an in-memory map of `connection_id -> user_id`.
- Listens for incoming messages from connected clients.
- Publishes messages to the message queue (Kafka) for persistence and fan-out.
- Receives messages from other chat servers (for cross-server delivery) via an internal messaging layer.

**Cross-server message routing**:

```
┌──────────────┐                    ┌──────────────┐
│ Chat Server A │                    │ Chat Server B │
│              │                    │              │
│ Alice ═══╗  │   Internal Bus     │  ╔═══ Bob   │
│          ║  │ ◀════════════════▶ │  ║          │
│          ║  │    (Redis Pub/Sub  │  ║          │
│          ║  │     or gRPC)       │  ║          │
└──────────╨──┘                    └──╨──────────┘
```

Options for cross-server communication:
1. **Redis Pub/Sub**: Each chat server subscribes to a channel named after itself. To send a message to a user on Server B, Server A publishes to Server B's channel.
2. **Direct gRPC**: Server A calls Server B directly. Faster but requires service discovery.
3. **Message queue (Kafka)**: Each server consumes from a partition. More durable but slightly higher latency.

We use **Redis Pub/Sub** for its simplicity and low latency, with Kafka as the durable backing store.

### 25.5.3 Message Storage

Chat messages have a unique access pattern:
- Most reads are for **recent messages** (the latest 50 messages in a conversation).
- Historical messages are read infrequently (scrolling back).
- Writes are heavy (1.16 million messages per second).
- Messages are rarely updated or deleted.

This makes **Cassandra** an excellent choice:

```sql
CREATE TABLE messages (
    conversation_id  UUID,
    message_id       TIMEUUID,     -- time-sortable unique ID
    sender_id        BIGINT,
    content          TEXT,
    media_url        TEXT,
    message_type     TEXT,          -- 'text', 'image', 'video'
    status           TEXT,          -- 'sent', 'delivered', 'read'
    created_at       TIMESTAMP,
    PRIMARY KEY (conversation_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
```

**Why Cassandra?**
- Optimized for write-heavy workloads (LSM tree storage engine).
- Partition by `conversation_id`: all messages in a conversation are co-located.
- Clustering by `message_id` (time-sorted): reading the latest N messages is a simple range scan.
- Linear horizontal scalability.
- Tunable consistency (QUORUM for writes, ONE for reads is a good balance).

### 25.5.4 Message Ordering

Ordering is crucial in chat. We need to guarantee that messages in a conversation appear in the order they were sent.

**Challenge**: In a distributed system, clocks are not perfectly synchronized. If Alice sends message A at 10:00:00.001 and Bob sends message B at 10:00:00.002 (on a different server), can we guarantee A appears before B?

**Solution: Per-conversation sequence numbers**

```
Each conversation maintains a monotonically increasing sequence number.

When a message arrives:
1. Acquire a lock on the conversation (Redis distributed lock or DB row lock)
2. Increment the sequence number
3. Assign the sequence number to the message
4. Release the lock
5. Store the message with the sequence number

Clients display messages ordered by sequence number, not by timestamp.
```

**Optimization for 1:1 chats**: Since only two people can send messages, we can use a simpler approach:
- Each sender maintains their own local sequence counter.
- The message includes `(sender_id, sender_seq_num)`.
- The server assigns a global sequence number using an atomic counter in Redis.

**For group chats**: The per-conversation lock approach works because the throughput per conversation is bounded (humans can only type so fast).

### 25.5.5 Offline Message Delivery

When a user is offline, messages must be stored and delivered when they come back online:

```
1. Alice sends message to Bob (offline)
2. Chat Server stores message in Cassandra with status = 'sent'
3. Chat Server sends push notification to Bob
4. Bob opens the app hours later
5. Bob's client connects via WebSocket
6. Client sends "sync request" with last_received_message_id
7. Chat Server queries Cassandra:
   SELECT * FROM messages
   WHERE conversation_id = ?
   AND message_id > last_received_message_id
   ORDER BY message_id ASC
8. Server streams pending messages to Bob over WebSocket
9. For each message, server updates status to 'delivered'
10. Server notifies Alice: "message delivered ✓✓"
```

**Handling long offline periods**: If a user has been offline for days and has thousands of pending messages across many conversations:
- Fetch conversations with unread messages first (metadata query).
- Load messages per conversation as the user opens each one.
- Do not dump all pending messages at once (would overwhelm the client and the connection).

### 25.5.6 Group Chat Fan-out

Group messaging introduces a fan-out challenge similar to Twitter, but with key differences:

- **Group sizes are smaller** (max 500 members vs millions of followers).
- **Every message must be delivered** (no "eventual consistency" for chat).
- **Ordering within the group must be consistent** for all members.

**Fan-out approach for groups**:

```
Message arrives for group G (200 members):

1. Store message in messages table (partition: group_conversation_id)
2. Look up all 200 members in group_members table
3. For each member:
   a. If online: route to their chat server
   b. If offline: increment unread counter, send push notification
4. Batch the routing: group members by chat server to minimize cross-server calls

Optimization:
- For small groups (< 50): fan-out synchronously
- For large groups (50-500): fan-out asynchronously via Kafka
```

**Why not fan-out on write (like Twitter)?**
In Twitter, fan-out on write means copying tweet IDs to followers' timeline caches. In chat, we do not copy messages -- we just route them. The message lives in one place (the conversation partition in Cassandra), and all group members read from that same partition. The "fan-out" is really just notification routing, not data duplication.

### 25.5.7 End-to-End Encryption Overview

Modern chat systems use end-to-end encryption (E2EE) so that even the server cannot read messages:

```
┌──────────┐                     ┌──────────┐
│  Alice    │                     │   Bob    │
│           │                     │          │
│ Plaintext │    ┌──────────┐    │Plaintext │
│ "Hello"   │───▶│  Server  │───▶│ "Hello"  │
│           │    │          │    │          │
│ Encrypted │    │ Encrypted│    │Encrypted │
│ with Bob's│    │ cannot   │    │decrypted │
│ public key│    │ read it  │    │with Bob's│
│           │    └──────────┘    │priv. key │
└──────────┘                     └──────────┘
```

**Key concepts**:
- Each user has a public/private key pair generated on their device.
- Public keys are exchanged via the server (key distribution).
- Messages are encrypted with the recipient's public key before leaving the sender's device.
- The server stores and forwards encrypted blobs -- it never sees plaintext.
- Group chats use a shared group key, distributed via pairwise encryption.

**Impact on system design**:
- The server cannot index or search message content.
- The server cannot filter spam or malware from messages.
- Message storage is opaque (encrypted blobs).
- Key management adds complexity (key rotation, multi-device sync, key verification).

We will not implement E2EE in this design, but mentioning it in an interview shows awareness of privacy requirements.

### 25.5.8 Presence Service

The presence service tracks which users are online and when they were last active:

```
┌────────────┐     ┌──────────────┐     ┌──────────────┐
│ Chat Server │────▶│  Presence    │────▶│   Redis      │
│ (heartbeat) │     │  Service     │     │   Cache      │
└────────────┘     └──────────────┘     └──────────────┘
```

**How it works**:

1. When a user connects via WebSocket, the presence service sets their status to "online" in Redis:
   ```
   SET presence:{user_id} "online" EX 60
   ```
2. The chat server sends a heartbeat every 30 seconds to refresh the TTL.
3. If no heartbeat arrives for 60 seconds, Redis expires the key, and the user is considered offline.
4. The "last seen" timestamp is updated when the key expires.

**Challenges at scale**:
- 500 million users checking friends' online status would create enormous read traffic.
- **Solution**: Subscribe to presence updates only for users in the current chat. Do not poll for all contacts.
- Use Redis Pub/Sub: when a user's status changes, publish to a channel. Only chat servers with interested clients subscribe.

**Reducing noise**:
- Do not broadcast every micro-disconnect (e.g., switching from WiFi to cellular).
- Use a grace period: if a user disconnects and reconnects within 30 seconds, do not change their status.

---

## 25.6 Database Schema

### Conversations Table

```sql
-- Cassandra
CREATE TABLE conversations (
    conversation_id    UUID PRIMARY KEY,
    conversation_type  TEXT,           -- '1:1' or 'group'
    name               TEXT,           -- group name (null for 1:1)
    created_by         BIGINT,
    created_at         TIMESTAMP,
    last_message_at    TIMESTAMP,
    last_message_preview TEXT
);
```

### Conversation Members Table

```sql
-- Cassandra
CREATE TABLE conversation_members (
    conversation_id    UUID,
    user_id            BIGINT,
    role               TEXT,           -- 'admin', 'member'
    joined_at          TIMESTAMP,
    unread_count       INT,
    last_read_message  TIMEUUID,
    PRIMARY KEY (conversation_id, user_id)
);

-- Reverse index: find all conversations for a user
CREATE TABLE user_conversations (
    user_id            BIGINT,
    last_message_at    TIMESTAMP,
    conversation_id    UUID,
    PRIMARY KEY (user_id, last_message_at)
) WITH CLUSTERING ORDER BY (last_message_at DESC);
```

### Messages Table

```sql
-- Cassandra
CREATE TABLE messages (
    conversation_id    UUID,
    message_id         TIMEUUID,
    sender_id          BIGINT,
    content            TEXT,
    media_url          TEXT,
    media_type         TEXT,
    reply_to           TIMEUUID,
    sequence_num       BIGINT,
    status             TEXT,           -- 'sent', 'delivered', 'read'
    created_at         TIMESTAMP,
    PRIMARY KEY (conversation_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
```

### Session Registry (Redis)

```
Key:    session:{user_id}
Value:  chat_server_id
TTL:    None (managed by connect/disconnect events)
```

### Presence Cache (Redis)

```
Key:    presence:{user_id}
Value:  {"status": "online", "last_seen": "2025-01-15T10:30:00Z"}
TTL:    60 seconds (refreshed by heartbeat)
```

### Unread Counters (Redis)

```
Key:    unread:{user_id}:{conversation_id}
Value:  integer count
```

---

## 25.7 API Design

### Send a Message

```
WebSocket Frame (client -> server):
{
    "action": "send_message",
    "conversation_id": "conv_123",
    "content": "Hello, Bob!",
    "media_id": null,
    "reply_to": null,
    "client_message_id": "client_uuid_456"  -- for idempotency
}

WebSocket Frame (server -> sender, acknowledgment):
{
    "action": "message_ack",
    "client_message_id": "client_uuid_456",
    "message_id": "msg_789",
    "status": "sent",
    "timestamp": "2025-01-15T10:30:00.123Z"
}

WebSocket Frame (server -> recipient):
{
    "action": "new_message",
    "conversation_id": "conv_123",
    "message_id": "msg_789",
    "sender_id": "42",
    "content": "Hello, Bob!",
    "timestamp": "2025-01-15T10:30:00.123Z"
}
```

### Get Message History (REST API for initial load)

```
GET /api/v1/conversations/{conversation_id}/messages?before={message_id}&limit=50
Authorization: Bearer {token}

Response: 200 OK
{
    "messages": [
        {
            "message_id": "msg_789",
            "sender_id": "42",
            "content": "Hello, Bob!",
            "status": "read",
            "created_at": "2025-01-15T10:30:00Z"
        },
        ...
    ],
    "has_more": true
}
```

### Mark Messages as Read

```
WebSocket Frame (client -> server):
{
    "action": "mark_read",
    "conversation_id": "conv_123",
    "last_read_message_id": "msg_789"
}
```

### Get Online Status

```
GET /api/v1/users/{user_id}/presence
Authorization: Bearer {token}

Response: 200 OK
{
    "user_id": "99",
    "status": "offline",
    "last_seen": "2025-01-15T09:45:00Z"
}
```

### Create a Group

```
POST /api/v1/conversations
Authorization: Bearer {token}

Request Body:
{
    "type": "group",
    "name": "Project Team",
    "member_ids": ["42", "99", "155", "201"]
}

Response: 201 Created
{
    "conversation_id": "conv_456",
    "type": "group",
    "name": "Project Team",
    "members": [...]
}
```

---

## 25.8 Scaling the System

### Chat Server Scaling

- **Horizontal scaling**: add more chat servers as concurrent users grow.
- **Sticky sessions**: route each user to the same server via consistent hashing on user_id.
- **Graceful drain**: before shutting down a server for maintenance, migrate connections to other servers.
- **Connection limits**: cap each server at 100K connections to prevent memory exhaustion.

### Message Store (Cassandra) Scaling

- **Partition key**: `conversation_id`. All messages in a conversation are on the same partition.
- **Partition size monitoring**: very active group chats could create hot partitions. If a conversation exceeds a partition size threshold, archive older messages to cold storage.
- **Replication factor**: 3 (across different racks/availability zones).
- **Compaction strategy**: leveled compaction for read-heavy access patterns.

### Session Registry Scaling

- Redis cluster with consistent hashing by user_id.
- With 500 million users: each entry is ~50 bytes, total ~25 GB. Fits in a small Redis cluster.

### Message Queue (Kafka) Scaling

- Partition by conversation_id to maintain ordering within a conversation.
- Number of partitions: start with 1,000, scale as needed.
- Consumer groups: one for persistence, one for push notifications, one for analytics.

### Push Notification Scaling

- Push notifications go through APNs (Apple) and FCM (Google).
- Both have rate limits. Use a queue to smooth out bursts.
- Batch notifications: if a user receives 50 messages while offline, send one summary notification, not 50.

---

## 25.9 Trade-offs

| Decision | Option A | Option B | Our Choice | Why |
|----------|----------|----------|-------------|-----|
| Real-time protocol | Long polling | WebSocket | **WebSocket** | Lower latency, less overhead at scale. Long polling as fallback. |
| Message store | MySQL (sharded) | Cassandra | **Cassandra** | Write-optimized, excellent for time-series data, linear scaling. |
| Cross-server routing | Redis Pub/Sub | gRPC direct | **Redis Pub/Sub** | Simpler, decoupled. gRPC is faster but tightly couples servers. |
| Message ordering | Timestamps | Sequence numbers | **Sequence numbers** | Clock skew makes timestamps unreliable across distributed servers. |
| Group fan-out | Copy message to each member | Shared partition, route notifications | **Shared partition** | Avoids data duplication; routing is lightweight. |
| Presence protocol | Poll-based | Heartbeat + Pub/Sub | **Heartbeat + Pub/Sub** | Efficient, low overhead, handles scale well. |
| Encryption | Server-side | End-to-end | **E2EE** (concept) | Users expect privacy. Server cannot read messages. |

---

## 25.10 Common Mistakes

1. **Using HTTP polling for real-time chat.** Polling every second creates 500 million requests per second from polling alone. WebSocket is not optional at this scale.

2. **Ignoring message ordering.** Saying "just use timestamps" fails because distributed clocks have skew. Use per-conversation sequence numbers.

3. **Storing messages in a relational database.** At 1.16 million writes per second, a relational database with B-tree indexes would collapse. Cassandra's LSM tree architecture handles write-heavy workloads far better.

4. **Forgetting offline delivery.** If you only describe the "both users online" case, you miss half the problem. Always discuss what happens when the recipient is offline.

5. **Not discussing the session registry.** How does Server A know that Bob is connected to Server B? The session registry is the answer.

6. **Treating group chat as a simple extension of 1:1 chat.** Group chat has unique challenges: fan-out to hundreds of members, ordering across multiple senders, and admin controls.

---

## 25.11 Best Practices

1. **Use idempotency keys for messages.** The client generates a `client_message_id` with each message. If the client retries (due to a network glitch), the server deduplicates using this key.

2. **Separate the connection layer from business logic.** Chat servers handle WebSocket connections; business logic (validation, storage, routing) runs in separate services. This makes each layer independently scalable.

3. **Implement graceful reconnection.** When a WebSocket drops, the client should reconnect and sync missed messages using the `last_received_message_id`. Make this seamless to the user.

4. **Batch push notifications.** Do not send a push notification for every single message in a group. If a user is offline and receives 20 messages in a group, send one notification: "20 new messages in Project Team."

5. **Use heartbeats wisely.** A heartbeat interval of 30 seconds balances between accuracy (knowing when a user goes offline) and overhead (network and server resources).

6. **Archive old messages to cold storage.** Messages older than 1 year can be moved to cheaper storage (S3 or cheaper Cassandra tiers) and loaded on demand.

---

## 25.12 Quick Summary

A chat system's architecture revolves around three pillars: (1) persistent WebSocket connections for real-time bidirectional messaging, managed by a fleet of chat servers with a Redis-based session registry for cross-server routing; (2) Cassandra for message storage, partitioned by conversation_id for co-located, time-sorted message retrieval; and (3) per-conversation sequence numbers for ordering guarantees, combined with offline delivery through push notifications and sync-on-reconnect. Group chat uses shared message storage (not duplication) with notification fan-out. Presence is tracked via heartbeats with Redis TTLs.

---

## 25.13 Key Points

- **WebSocket** provides persistent, full-duplex connections for real-time message delivery.
- **Session registry** (Redis) maps each user to their chat server for cross-server message routing.
- **Cassandra** stores messages partitioned by conversation_id, optimized for write-heavy time-series data.
- **Per-conversation sequence numbers** guarantee message ordering despite clock skew.
- **Offline delivery** uses push notifications plus sync-on-reconnect to ensure no message is lost.
- **Group chat** stores messages once (shared partition) and fans out notifications, not data.
- **Heartbeat-based presence** with Redis TTLs tracks online/offline status efficiently.
- **Read receipts** use a watermark approach: "I have read everything up to message X."
- **Idempotency keys** (client_message_id) prevent duplicate message delivery on retry.
- **End-to-end encryption** ensures even the server cannot read message content.

---

## 25.14 Practice Questions

1. If a chat server crashes and 100,000 users lose their connections, what happens? How do they reconnect, and how are pending messages delivered?

2. How would you handle a group with 10,000 members (like a broadcast channel)? Does the architecture change?

3. Alice sends a message on her phone, then immediately opens the app on her laptop. How do you ensure the message appears on both devices?

4. How would you implement "typing indicators" ("Alice is typing...") without overwhelming the system?

5. If Cassandra is temporarily unavailable, should the chat server still accept messages? If so, where do they go?

---

## 25.15 Exercises

1. **Connection capacity**: Calculate how many chat servers you need for 500 million concurrent connections. Assume each server has 32 GB of RAM and each connection uses 10 KB.

2. **Ordering simulation**: Write pseudocode for the sequence number assignment mechanism for a group chat with concurrent senders. Show how you handle the case where two messages arrive at the server simultaneously.

3. **Offline sync protocol**: Design the protocol for syncing messages when a user comes back online after 3 days. Consider that they might be in 50 group chats, each with hundreds of unread messages.

4. **Presence at scale**: If each user has an average of 200 contacts and checks their presence every 10 seconds, calculate the read load on the presence service. Design a solution that keeps this load manageable.

5. **Multi-device sync**: Extend the design to support users logged in on 3 devices simultaneously. How does message delivery change? How does read receipt sync work?

---

## 25.16 What Is Next?

In this chapter we built a real-time messaging system with WebSocket connections, message ordering, offline delivery, and presence tracking. In the next chapter, **Chapter 26: Designing YouTube**, we shift from text-based communication to the world of video. You will learn about video upload and transcoding pipelines, adaptive bitrate streaming (HLS/DASH), CDN delivery for large video files, and recommendation engines -- a completely different set of challenges that make video platforms among the most complex systems to design.
