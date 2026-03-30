# Chapter 23: Designing Twitter (X)

Every second, thousands of people post tweets, millions scroll through their timelines, and trending topics shift in real time. Twitter (now X) is one of the most fascinating systems to design because it combines a deceptively simple product -- short text posts -- with enormous engineering challenges around fan-out, real-time delivery, and search at scale.

In this chapter we will design Twitter from the ground up. You will learn how timeline generation works, why fan-out strategy matters so much, how the search index keeps up with hundreds of thousands of tweets per second, and how all the pieces fit together into a coherent architecture. Whether you are preparing for an interview or building a social platform, this chapter gives you a complete blueprint.

---

## 23.1 Understanding the Problem

At its core, Twitter lets users do four things:

1. **Post a tweet** -- a short message (up to 280 characters) optionally with images, videos, or links.
2. **Follow other users** -- subscribe to see their tweets.
3. **View a timeline** -- a personalized feed of tweets from people you follow.
4. **Search tweets** -- find tweets by keyword, hashtag, or user.

Around these four features orbit many secondary concerns: trending topics, notifications, direct messages, retweets, likes, and media storage. We will focus on the core four and touch on the others as we go.

### Why Is Twitter Hard to Design?

The challenge is **asymmetric fan-out**. When a regular user with 200 followers tweets, delivering that tweet to 200 timelines is easy. When a celebrity with 50 million followers tweets, delivering to 50 million timelines in real time is a completely different problem. This asymmetry drives most of the interesting design decisions.

---

## 23.2 Requirements

### Functional Requirements

| # | Requirement | Description |
|---|-------------|-------------|
| F1 | **Post a tweet** | Users can post text (280 chars), optionally with images or video. |
| F2 | **Home timeline** | Users see a reverse-chronological feed of tweets from people they follow. |
| F3 | **Follow / unfollow** | Users can follow or unfollow other users. |
| F4 | **Search** | Users can search tweets by keyword, hashtag, or username. |
| F5 | **Like and retweet** | Users can like or retweet a tweet. |
| F6 | **Trending topics** | Surface the most-discussed topics in real time. |
| F7 | **Notifications** | Notify users when someone follows, likes, retweets, or mentions them. |

### Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NF1 | **High availability** | 99.99% uptime. Timeline must always load. |
| NF2 | **Low latency** | Timeline load under 200 ms (p99). |
| NF3 | **Scalability** | 500 million daily active users, 500 million tweets per day. |
| NF4 | **Consistency** | Eventual consistency is acceptable. A tweet may take a few seconds to appear in all followers' timelines. |
| NF5 | **Durability** | No tweet is ever lost once accepted. |

### Out of Scope

- Direct messages (covered in Chapter 25).
- Ads and monetization.
- Content moderation and spam detection.

---

## 23.3 Back-of-the-Envelope Estimation

### Traffic

| Metric | Value |
|--------|-------|
| Daily active users (DAU) | 500 million |
| Tweets per day | 500 million |
| Tweets per second | 500M / 86,400 ≈ **5,800 tweets/s** |
| Timeline reads per day | Each user checks timeline ~10 times/day = **5 billion reads/day** |
| Timeline reads per second | 5B / 86,400 ≈ **58,000 reads/s** |
| Read-to-write ratio | ~10:1 |

### Storage

| Item | Size |
|------|------|
| Tweet text | 280 bytes |
| User ID | 8 bytes |
| Timestamp | 8 bytes |
| Tweet ID | 8 bytes |
| Metadata (likes, retweet count, flags) | 50 bytes |
| **Total per tweet (text only)** | **~350 bytes** |

Over five years (text only):

```
500M tweets/day x 365 x 5 = 912.5 billion tweets
912.5B x 350 bytes ≈ 319 TB
```

### Media Storage

| Media type | Percentage of tweets | Average size |
|------------|---------------------|--------------|
| Image | 20% | 500 KB |
| Video | 5% | 5 MB |
| None | 75% | 0 |

Daily media storage:

```
Images: 500M x 0.20 x 500 KB = 50 TB/day
Videos: 500M x 0.05 x 5 MB  = 125 TB/day
Total media: ~175 TB/day
```

Over five years: **~319 PB**. Media dominates storage costs.

### Timeline Fan-out

Average followers per user: ~200. When a regular user tweets:

```
Fan-out writes = 200 timeline entries
200 x 8 bytes (tweet ID) = 1,600 bytes per tweet
```

But a celebrity with 50 million followers:

```
Fan-out writes = 50,000,000 timeline entries
```

At 5,800 tweets per second, if even 1% come from celebrities, that is 58 celebrity tweets per second times 50 million fan-out each -- **2.9 billion writes per second**. This is not feasible with pure fan-out on write. We need a hybrid approach.

---

## 23.4 High-Level Design

```
┌──────────┐         ┌───────────────┐
│  Client   │────────▶│ Load Balancer  │
│(Mobile/Web)│        └───────┬───────┘
└──────────┘                  │
                ┌─────────────┼──────────────┐
                │             │              │
         ┌──────▼──────┐ ┌───▼────┐  ┌──────▼──────┐
         │ Tweet Service│ │Timeline│  │Search Service│
         │  (Write API) │ │Service │  │             │
         └──────┬──────┘ └───┬────┘  └──────┬──────┘
                │            │               │
         ┌──────▼──────┐    │        ┌──────▼──────┐
         │  Tweet Store │    │        │ Search Index │
         │  (Database)  │    │        │(Elasticsearch)│
         └──────┬──────┘    │        └─────────────┘
                │            │
         ┌──────▼──────┐ ┌──▼───────────┐
         │ Fan-out      │ │Timeline Cache│
         │ Service      │ │  (Redis)     │
         └──────┬──────┘ └──────────────┘
                │
         ┌──────▼──────┐     ┌──────────────┐
         │ Notification │     │ Media Service │
         │ Service      │     │ (S3 + CDN)   │
         └─────────────┘     └──────────────┘
```

### Request Flow: Posting a Tweet

1. Client sends tweet to **Tweet Service** through the load balancer.
2. Tweet Service validates the request, assigns a unique tweet ID (using a distributed ID generator like Snowflake), and writes to the **Tweet Store**.
3. Tweet Service publishes an event to a **message queue** (Kafka).
4. **Fan-out Service** consumes the event. It looks up the author's followers and decides on the fan-out strategy:
   - **Regular user** (under 10,000 followers): fan-out on write. Push the tweet ID into each follower's timeline cache.
   - **Celebrity** (over 10,000 followers): skip fan-out. The tweet stays in the tweet store and is merged at read time.
5. **Media Service** processes any attached images or videos asynchronously.
6. **Search Service** indexes the tweet for full-text search.
7. **Notification Service** sends push notifications for mentions and followers with notifications enabled.

### Request Flow: Reading the Timeline

1. Client requests home timeline from **Timeline Service**.
2. Timeline Service reads the pre-computed timeline from **Redis** (list of tweet IDs for that user).
3. For each celebrity the user follows, Timeline Service fetches their latest tweets from the Tweet Store.
4. The two lists are merged and sorted by time.
5. Tweet details (text, author info, like count) are fetched from cache or database.
6. The assembled timeline is returned to the client.

---

## 23.5 Deep Dive

### 23.5.1 Fan-out on Write vs. Fan-out on Read

This is the most critical design decision for Twitter. Let us compare:

| Aspect | Fan-out on Write | Fan-out on Read |
|--------|-----------------|-----------------|
| **How it works** | When a tweet is posted, push it into every follower's timeline cache. | When a user loads their timeline, pull tweets from all followed users. |
| **Timeline read speed** | Very fast -- just read the pre-built list. | Slower -- must query N users' tweet lists and merge. |
| **Tweet post speed** | Slower for popular users -- must update millions of caches. | Fast -- just write one record. |
| **Storage** | High -- duplicate tweet IDs across millions of timelines. | Low -- tweets stored once. |
| **Best for** | Regular users with few followers. | Celebrities with millions of followers. |

### The Hybrid Approach

Twitter uses a **hybrid** strategy:

```
         ┌──────────────────────────────────────────┐
         │           Fan-out Decision Engine          │
         │                                            │
         │  if (author.followers < THRESHOLD):        │
         │      fan_out_on_write(tweet, followers)    │
         │  else:                                     │
         │      mark_as_celebrity_tweet(tweet)         │
         └──────────────────────────────────────────┘
```

- **Threshold**: Typically around 10,000 followers.
- Regular users: their tweets are pushed to followers' timeline caches immediately (fan-out on write).
- Celebrities: their tweets are NOT pushed. Instead, when a user reads their timeline, the system merges the pre-built cache with fresh celebrity tweets (fan-out on read).

This gives us the best of both worlds: fast reads for the 99% case and manageable write load for the 1% of celebrity tweets.

### 23.5.2 Timeline Service

The timeline is stored in Redis as a sorted set per user:

```
Key:    timeline:{user_id}
Value:  sorted set of (tweet_id, timestamp)
```

Each user's timeline cache holds the most recent 800 tweet IDs. When a new tweet is pushed via fan-out on write, the oldest entry is evicted.

**Reading the timeline**:

```
1. ZREVRANGE timeline:{user_id} 0 19       -- get top 20 tweet IDs
2. For each celebrity the user follows:
     GET latest tweets from tweets:{celebrity_id}
3. Merge the two lists by timestamp
4. MGET tweet:{id} for each tweet ID        -- fetch full tweet objects
5. Return assembled timeline to client
```

**Why Redis?** It keeps everything in memory, supports sorted sets natively, and handles hundreds of thousands of operations per second per node. A Redis cluster with sharding by user_id scales horizontally.

### 23.5.3 Tweet Storage

We need two storage layers:

**Primary Database (MySQL / PostgreSQL with sharding)**:
- Source of truth for all tweets.
- Sharded by tweet_id for even distribution.
- Each shard holds a partition of all tweets.

**Cache Layer (Redis / Memcached)**:
- Hot tweets (recent, viral) are cached.
- Cache-aside pattern: read from cache first, fall back to database.

### 23.5.4 Media Service

Tweets with images or videos go through a processing pipeline:

```
┌────────┐    ┌──────────┐    ┌───────────────┐    ┌─────┐
│ Upload │───▶│  Object  │───▶│  Processing   │───▶│ CDN │
│  API   │    │  Store   │    │  Pipeline     │    │     │
└────────┘    │  (S3)    │    │               │    └─────┘
              └──────────┘    │ - Resize      │
                              │ - Compress    │
                              │ - Thumbnails  │
                              │ - Strip EXIF  │
                              └───────────────┘
```

1. Client uploads the media file to an upload API that returns a media ID.
2. The raw file is stored in object storage (S3).
3. An asynchronous pipeline generates multiple sizes (thumbnail, small, medium, large) and compresses them.
4. Processed files are pushed to a CDN for low-latency global delivery.
5. The tweet references the media ID; clients fetch media directly from the CDN.

### 23.5.5 Search Index

Twitter needs to index tweets for real-time search. The search architecture:

```
┌─────────────┐     ┌───────────────┐     ┌──────────────┐
│  Tweet Event │────▶│  Indexing     │────▶│Elasticsearch │
│  (Kafka)     │     │  Workers      │     │  Cluster     │
└─────────────┘     └───────────────┘     └──────────────┘
                                                 │
                                          ┌──────▼──────┐
                                          │ Search API   │
                                          └─────────────┘
```

- **Inverted index**: maps each word/hashtag to a list of tweet IDs.
- **Near real-time**: new tweets are searchable within seconds (Elasticsearch refresh interval).
- **Ranking**: results ranked by recency, engagement (likes, retweets), and relevance.
- **Sharding**: the index is sharded by time (recent tweets on faster hardware, older tweets on cheaper storage).

### 23.5.6 Trending Topics

Trending topics are computed by a streaming analytics pipeline:

```
┌──────────┐     ┌──────────────┐     ┌────────────────┐
│  Tweets  │────▶│  Stream      │────▶│  Trending      │
│  (Kafka) │     │  Processor   │     │  Topics Cache  │
└──────────┘     │ (Flink/Spark)│     │  (Redis)       │
                 └──────────────┘     └────────────────┘
```

**Algorithm**:
1. Extract hashtags and significant phrases from each tweet.
2. Count occurrences in a sliding window (e.g., last 5 minutes, last hour).
3. Apply a velocity formula: topics that spike suddenly rank higher than steadily popular ones.
4. Filter out evergreen terms (common words that always trend).
5. Store the top N trending topics in Redis, refreshed every 30-60 seconds.
6. Segment by geography for localized trends.

### 23.5.7 Notification Service

When certain events occur (mention, follow, like, retweet), the notification service alerts the user:

```
┌──────────────┐     ┌──────────────┐     ┌───────────────┐
│  Event       │────▶│ Notification │────▶│ Push Gateway   │
│  (Kafka)     │     │ Service      │     │ (APNs / FCM)  │
└──────────────┘     └──────┬───────┘     └───────────────┘
                            │
                     ┌──────▼───────┐
                     │ Notification  │
                     │ Store (DB)    │
                     └──────────────┘
```

- **Priority levels**: mentions and DMs are high priority (push immediately); likes on old tweets are low priority (batch).
- **Rate limiting**: if a tweet goes viral, do not send 10,000 individual like notifications. Aggregate them ("50 people liked your tweet").
- **User preferences**: respect mute, block, and notification settings.

---

## 23.6 Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id       BIGINT PRIMARY KEY,    -- Snowflake ID
    username      VARCHAR(50) UNIQUE NOT NULL,
    display_name  VARCHAR(100),
    email         VARCHAR(255) UNIQUE,
    bio           VARCHAR(280),
    profile_image VARCHAR(500),
    followers_count  INT DEFAULT 0,
    following_count  INT DEFAULT 0,
    is_celebrity  BOOLEAN DEFAULT FALSE, -- fan-out threshold flag
    created_at    TIMESTAMP DEFAULT NOW()
);
```

### Tweets Table

```sql
CREATE TABLE tweets (
    tweet_id      BIGINT PRIMARY KEY,    -- Snowflake ID (time-sortable)
    user_id       BIGINT NOT NULL,
    content       VARCHAR(280),
    media_ids     JSON,                  -- array of media references
    reply_to      BIGINT,                -- NULL if not a reply
    retweet_of    BIGINT,                -- NULL if not a retweet
    like_count    INT DEFAULT 0,
    retweet_count INT DEFAULT 0,
    reply_count   INT DEFAULT 0,
    created_at    TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_time (user_id, created_at DESC)
);
-- Sharded by tweet_id
```

### Follows Table

```sql
CREATE TABLE follows (
    follower_id   BIGINT NOT NULL,
    followee_id   BIGINT NOT NULL,
    created_at    TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, followee_id),
    INDEX idx_followee (followee_id, follower_id)
);
-- Sharded by follower_id
```

### Likes Table

```sql
CREATE TABLE likes (
    user_id       BIGINT NOT NULL,
    tweet_id      BIGINT NOT NULL,
    created_at    TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, tweet_id),
    INDEX idx_tweet (tweet_id)
);
```

### Timeline Cache (Redis)

```
Key:    timeline:{user_id}
Type:   Sorted Set
Score:  tweet timestamp (epoch ms)
Member: tweet_id

Max size: 800 entries per user (oldest evicted)
```

---

## 23.7 API Design

### Post a Tweet

```
POST /api/v1/tweets
Authorization: Bearer {token}

Request Body:
{
    "content": "Hello, world!",
    "media_ids": ["media_123", "media_456"],
    "reply_to": null
}

Response: 201 Created
{
    "tweet_id": "1234567890",
    "content": "Hello, world!",
    "created_at": "2025-01-15T10:30:00Z",
    "media": [
        {"id": "media_123", "url": "https://cdn.twitter.com/..."}
    ]
}
```

### Get Home Timeline

```
GET /api/v1/timeline?cursor={last_tweet_id}&limit=20
Authorization: Bearer {token}

Response: 200 OK
{
    "tweets": [
        {
            "tweet_id": "1234567890",
            "user": {"user_id": "42", "username": "alice", ...},
            "content": "Hello, world!",
            "like_count": 15,
            "retweet_count": 3,
            "created_at": "2025-01-15T10:30:00Z"
        },
        ...
    ],
    "next_cursor": "1234567880"
}
```

### Follow a User

```
POST /api/v1/users/{user_id}/follow
Authorization: Bearer {token}

Response: 200 OK
{
    "following": true,
    "user_id": "99"
}
```

### Search Tweets

```
GET /api/v1/search?q=system+design&type=recent&cursor={}&limit=20
Authorization: Bearer {token}

Response: 200 OK
{
    "tweets": [...],
    "next_cursor": "..."
}
```

---

## 23.8 Scaling the System

### Tweet Store Sharding

Shard tweets by `tweet_id` using consistent hashing. Since tweet IDs are generated with Snowflake (which embeds a timestamp), we get time-ordered IDs that spread evenly across shards.

### Timeline Cache Sharding

Shard Redis by `user_id`. Each user's timeline lives on one Redis node, making reads fast (no cross-shard queries).

### Fan-out Workers

The fan-out service is the most write-intensive component. Scale it by:
- Using a Kafka consumer group with many partitions.
- Each partition handles fan-out for a subset of users.
- During peak times (major events), auto-scale the consumer group.

### Search Index Scaling

- **Time-based sharding**: recent tweets on SSDs, older tweets on HDDs.
- **Replication**: each shard has 2-3 replicas for read throughput.
- **Query routing**: search queries hit all shards in parallel; results are merged and ranked.

### CDN for Media

- Media files are served from CDN edge locations worldwide.
- Upload goes to the origin (S3); CDN pulls on first request and caches.
- Multiple CDN providers for redundancy.

### Database Read Replicas

- Each MySQL shard has 3-5 read replicas.
- Timeline Service reads from replicas; writes go to the primary.
- Replication lag (typically under 1 second) is acceptable for timeline reads.

---

## 23.9 Trade-offs

| Decision | Option A | Option B | Our Choice | Why |
|----------|----------|----------|-------------|-----|
| Fan-out strategy | Pure write | Pure read | **Hybrid** | Handles both regular users and celebrities efficiently. |
| Tweet ID generation | UUID | Snowflake | **Snowflake** | Time-sortable, 64-bit (compact), no coordination needed. |
| Timeline storage | Database | Redis | **Redis** | In-memory speed is essential for timeline latency. |
| Search engine | Custom inverted index | Elasticsearch | **Elasticsearch** | Mature, battle-tested, supports near real-time indexing. |
| Consistency model | Strong | Eventual | **Eventual** | Users tolerate a few seconds of delay; strong consistency is too expensive at this scale. |
| Media storage | Own infrastructure | Cloud object storage | **Cloud (S3)** | Petabyte-scale, 11 nines durability, no operational burden. |

---

## 23.10 Common Mistakes

1. **Using only fan-out on write.** This falls apart for celebrity accounts. Always discuss the hybrid approach.

2. **Forgetting the celebrity problem entirely.** If you do not mention that some users have millions of followers, the interviewer will ask.

3. **Storing full tweets in the timeline cache.** Store only tweet IDs and timestamps. Fetch full tweet data separately -- this keeps the cache small and avoids data consistency issues.

4. **Ignoring media storage.** Media is the largest storage cost by orders of magnitude. Mentioning CDN and object storage shows you think about real production systems.

5. **Not discussing ID generation.** Auto-increment IDs break with sharding. Snowflake IDs solve this elegantly.

6. **Treating search as an afterthought.** Real-time search is a core feature, not a nice-to-have.

---

## 23.11 Best Practices

1. **Separate read and write paths.** The timeline read path and tweet write path have very different performance profiles. Design them independently.

2. **Use event-driven architecture.** Kafka decouples the tweet write from fan-out, search indexing, notification, and trending computation. Each consumer processes events at its own pace.

3. **Cache aggressively but invalidate carefully.** Timeline caches, tweet caches, and user profile caches all reduce database load. Use TTLs and event-driven invalidation.

4. **Design for graceful degradation.** If the fan-out service falls behind, timelines still work (they just miss very recent tweets). If search is down, the timeline still loads.

5. **Monitor fan-out latency.** Track the p99 time from tweet creation to appearance in followers' timelines. This is the key user experience metric.

6. **Use cursor-based pagination.** Offset-based pagination breaks at Twitter's scale. Use the last tweet ID as a cursor.

---

## 23.12 Quick Summary

Twitter's architecture revolves around three key insights: (1) use a hybrid fan-out strategy to handle both regular users and celebrities, (2) pre-compute timelines in Redis for fast reads while merging celebrity tweets at read time, and (3) use event-driven architecture (Kafka) to decouple tweet creation from downstream processing (fan-out, search, notifications, trending). Media storage dominates costs and is handled by object storage plus CDN. Search uses an inverted index (Elasticsearch) with time-based sharding for efficient real-time queries.

---

## 23.13 Key Points

- **Hybrid fan-out** is the heart of the design: fan-out on write for regular users, fan-out on read for celebrities.
- **Redis sorted sets** store pre-computed timelines (tweet IDs only, not full tweets).
- **Snowflake IDs** provide time-sortable, globally unique tweet identifiers without coordination.
- **Kafka** decouples tweet creation from fan-out, indexing, notifications, and trending.
- **Celebrity threshold** (~10K followers) determines the fan-out strategy per user.
- **Media pipeline** handles upload, processing (resize, compress, thumbnail), and CDN delivery.
- **Elasticsearch** provides near real-time full-text search with time-based sharding.
- **Trending topics** use streaming analytics with sliding windows and velocity detection.
- **Eventual consistency** is acceptable -- users tolerate a few seconds of delay.
- **Storage is dominated by media** (hundreds of TB per day for video and images).

---

## 23.14 Practice Questions

1. If a celebrity with 100 million followers tweets, and you use pure fan-out on write, how long would it take to update all timelines assuming each write takes 1 microsecond?

2. How would you handle the case where a user unfollows someone? Do you remove the unfollowed user's tweets from the timeline cache?

3. If Redis goes down for a user's timeline, how would you rebuild it?

4. How would you implement "quote tweets" in this design?

5. A breaking news event causes 10x normal tweet volume. Which components are most likely to become bottlenecks, and how would you handle it?

---

## 23.15 Exercises

1. **Capacity planning**: Calculate the number of Redis nodes needed to store timelines for 500 million users, where each timeline holds 800 tweet IDs (8 bytes each). Assume each Redis node has 64 GB of RAM.

2. **Fan-out simulation**: Write pseudocode for the fan-out decision engine that handles regular users, celebrities, and "protected" accounts (private tweets visible only to approved followers).

3. **Trending algorithm**: Design a data structure that can efficiently track the top 10 trending hashtags in a sliding 5-minute window, processing 5,000 tweets per second.

4. **Schema extension**: Extend the database schema to support Twitter threads (a chain of tweets by the same user).

5. **Failure scenario**: The fan-out service is down for 10 minutes. Design a recovery mechanism that processes the backlog without overwhelming downstream services.

---

## 23.16 What Is Next?

In this chapter we tackled the fan-out problem, timeline generation, and real-time search. In the next chapter, **Chapter 24: Designing Instagram**, we will explore a system with a similar social graph but a very different content model -- images and photos. You will see how the news feed generation differs when every post is visual, how image processing pipelines work at scale, and how CDN strategies change when media is not optional but the entire product.
