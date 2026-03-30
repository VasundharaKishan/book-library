# Chapter 24: Designing Instagram

A billion people use Instagram every month to share photos, browse their feed, and discover content. Behind every double-tap and every perfectly filtered sunset photo is a system that handles hundreds of millions of image uploads, generates personalized news feeds at massive scale, and delivers photos from CDN edge servers around the world in milliseconds.

In this chapter we will design Instagram from scratch. You will learn how the image upload and processing pipeline works, how news feed generation differs from Twitter's approach, how to shard a social graph, and how to handle the unique challenges that celebrities create in any follow-based system. This is one of the most frequently asked system design questions, and by the end you will have a thorough, production-grade blueprint.

---

## 24.1 Understanding the Problem

Instagram's core features are:

1. **Upload a photo or video** -- with captions, filters, and location tags.
2. **News feed** -- a personalized feed of posts from people you follow.
3. **Follow / unfollow** -- subscribe to other users' content.
4. **Like and comment** -- engage with posts.
5. **Stories** -- ephemeral content that disappears after 24 hours.
6. **Explore** -- discover new content based on interests.

We will focus on the first four features and address stories and explore at a high level.

### How Is Instagram Different from Twitter?

While both are follow-based social networks, Instagram differs in important ways:

- **Every post has media.** Twitter posts are text-first; Instagram posts are image/video-first. This means media handling is not optional -- it IS the product.
- **Higher media quality.** Users expect high-resolution images loaded quickly.
- **Less real-time pressure.** A few seconds of delay in the news feed is more tolerable than on Twitter, where breaking news matters.
- **Smaller post volume.** Users post far fewer Instagram posts per day compared to tweets, but each post is much larger in bytes.

---

## 24.2 Requirements

### Functional Requirements

| # | Requirement | Description |
|---|-------------|-------------|
| F1 | **Upload photo/video** | Users can upload images (up to 10 in a carousel) and short videos with captions. |
| F2 | **News feed** | Users see posts from people they follow, ranked by relevance and recency. |
| F3 | **Follow / unfollow** | Users can follow or unfollow other accounts. |
| F4 | **Like** | Users can like a post. |
| F5 | **Comment** | Users can comment on a post. |
| F6 | **User profile** | View a user's posts, follower count, and bio. |

### Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NF1 | **High availability** | 99.99% uptime. Feed and uploads must always work. |
| NF2 | **Low latency** | News feed loads in under 300 ms. Images render in under 500 ms. |
| NF3 | **Scalability** | 1 billion monthly active users, 500 million DAU, 100 million photos/day. |
| NF4 | **Durability** | No uploaded photo is ever lost. |
| NF5 | **Consistency** | Eventual consistency. A new post may take a few seconds to appear in followers' feeds. |

### Out of Scope

- Stories and Reels.
- Direct messaging.
- Ads and monetization.
- Content recommendation (Explore page).

---

## 24.3 Back-of-the-Envelope Estimation

### Traffic

| Metric | Value |
|--------|-------|
| Daily active users | 500 million |
| Photo uploads per day | 100 million |
| Uploads per second | 100M / 86,400 ≈ **1,160 uploads/s** |
| Feed reads per day | 500M users x 10 opens = **5 billion/day** |
| Feed reads per second | 5B / 86,400 ≈ **58,000 reads/s** |

### Storage

| Item | Size |
|------|------|
| Original photo | 2 MB (average) |
| Processed versions (5 sizes) | 500 KB + 200 KB + 100 KB + 50 KB + 20 KB ≈ 870 KB |
| Total per photo (all versions) | ~3 MB |

Daily storage:

```
100M photos/day x 3 MB = 300 TB/day
```

Over five years:

```
300 TB/day x 365 x 5 ≈ 547 PB
```

This is enormous. Object storage (S3) with lifecycle policies is essential.

### Post Metadata

| Item | Size |
|------|------|
| Post ID | 8 bytes |
| User ID | 8 bytes |
| Caption | 500 bytes (average) |
| Location | 50 bytes |
| Timestamps | 16 bytes |
| Counters (likes, comments) | 16 bytes |
| Media references | 100 bytes |
| **Total per post** | **~700 bytes** |

Over five years:

```
100M posts/day x 365 x 5 x 700 bytes ≈ 127 TB
```

Metadata is manageable. Media storage dominates by 4,000x.

---

## 24.4 High-Level Design

```
┌──────────┐         ┌────────────────┐
│  Client   │────────▶│  API Gateway   │
│(iOS/Android)│       │& Load Balancer │
└──────────┘         └───────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
   │   Post      │   │   Feed      │   │   User      │
   │   Service   │   │   Service   │   │   Service   │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                 │                  │
   ┌──────▼──────┐   ┌─────▼───────┐   ┌─────▼───────┐
   │  Post DB    │   │ Feed Cache  │   │  User DB    │
   │  (MySQL)    │   │  (Redis)    │   │  (MySQL)    │
   └──────┬──────┘   └─────────────┘   └─────────────┘
          │
   ┌──────▼──────────────────────────────┐
   │        Image Processing Pipeline     │
   │                                      │
   │  Upload ──▶ S3 ──▶ Resize/Compress  │
   │                     ──▶ CDN Push     │
   └──────────────────────────────────────┘
          │
   ┌──────▼──────┐
   │  Message    │ ──▶ Fan-out Service
   │  Queue      │ ──▶ Notification Service
   │  (Kafka)    │ ──▶ Search Indexer
   └─────────────┘
```

### Request Flow: Uploading a Photo

1. Client uploads the image to a **pre-signed URL** (direct to S3), bypassing application servers for large file transfers.
2. Client sends post metadata (caption, location, media references) to **Post Service**.
3. Post Service validates the request, stores metadata in **Post DB**, and publishes an event to **Kafka**.
4. **Image Processing Pipeline** (triggered by S3 event or Kafka):
   - Generates multiple resolutions (thumbnail: 150x150, small: 320px, medium: 640px, large: 1080px, original).
   - Applies compression (WebP format for supported clients, JPEG fallback).
   - Strips EXIF data for privacy.
   - Stores all versions in S3.
   - Invalidates or pre-warms CDN cache.
5. **Fan-out Service** pushes the post ID to followers' feed caches.
6. **Notification Service** notifies relevant users.

### Request Flow: Loading the News Feed

1. Client requests feed from **Feed Service**.
2. Feed Service reads pre-computed feed from **Redis** (list of post IDs).
3. For celebrities the user follows, fetches their recent posts directly from Post DB.
4. Merges and ranks posts (by relevance score, not just chronological order).
5. Fetches full post metadata and user info from cache or database.
6. Returns the assembled feed. Image URLs point to the CDN.

### Why Pre-signed URLs for Upload?

Uploading multi-megabyte images through application servers wastes bandwidth and CPU on machines that should be handling API logic. Pre-signed URLs let clients upload directly to S3:

```
1. Client ──▶ Post Service: "I want to upload a photo"
2. Post Service generates a pre-signed S3 URL (valid for 15 minutes)
3. Post Service ──▶ Client: returns the pre-signed URL
4. Client ──▶ S3: uploads the image directly
5. S3 ──▶ Lambda/Worker: triggers processing pipeline
```

---

## 24.5 Deep Dive

### 24.5.1 Image Processing Pipeline

This is the most Instagram-specific component. Every uploaded image goes through:

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌─────┐
│  Raw    │───▶│ Validate│───▶│  Resize  │───▶│ Compress │───▶│Store│
│ Upload  │    │ & Scan  │    │ (5 sizes)│    │(WebP/JPEG)│   │(S3) │
└─────────┘    └─────────┘    └──────────┘    └──────────┘    └──┬──┘
                                                                 │
                                                           ┌─────▼─────┐
                                                           │ CDN Push  │
                                                           └───────────┘
```

**Validation**: Check file type, size limits (max 30 MB), and scan for malware or prohibited content.

**Resize**: Generate five versions:

| Version | Max dimension | Use case |
|---------|--------------|----------|
| Thumbnail | 150 x 150 | Profile grid, notifications |
| Small | 320px wide | Feed on slow connections |
| Medium | 640px wide | Standard feed view |
| Large | 1080px wide | Full-screen view |
| Original | As uploaded | Zoom, download |

**Compression**: Use WebP (30% smaller than JPEG at same quality) for modern clients, JPEG for older ones. Target quality: 80-85%.

**EXIF stripping**: Remove GPS coordinates, camera info, and other metadata for user privacy.

**CDN push**: Pre-warm the CDN by pushing processed images to edge locations in regions where the uploader's followers are concentrated.

### 24.5.2 News Feed Generation

Instagram's feed is ranked, not purely chronological. The ranking considers:

- **Recency**: newer posts score higher.
- **Relationship**: posts from accounts you interact with frequently score higher.
- **Interest**: posts similar to content you have liked before score higher.
- **Engagement velocity**: posts getting lots of likes quickly score higher.

The feed is generated in two phases:

**Phase 1 -- Candidate generation (offline/near-real-time)**:
- Fan-out service pushes post IDs to followers' feed caches (same hybrid approach as Twitter).
- Each user's cache holds the last 500 candidate post IDs.

**Phase 2 -- Ranking (at read time)**:
- When the user opens the app, Feed Service fetches the 500 candidates.
- A lightweight ranking model scores each candidate.
- The top N posts are returned, ordered by score.

This two-phase approach separates the expensive fan-out (done once per post) from the personalized ranking (done per feed request).

### 24.5.3 Database Schema and Sharding

#### Sharding Strategy

The primary shard key is **user_id**. This means:
- All of a user's posts are on the same shard.
- A user's profile query hits only one shard.
- The follow graph for a user is on one shard.

The trade-off: feed generation must query multiple shards (one per followed user). This is acceptable because:
- Fan-out pre-computes the feed in Redis (so the read path rarely hits the database).
- When we do need to query multiple shards, we do it in parallel.

#### Shard Count Estimation

With 500 million DAU and ~700 bytes per post metadata:

```
Posts over 5 years: 100M/day x 365 x 5 = 182.5 billion posts
Metadata: 182.5B x 700 bytes ≈ 127 TB
With indexes: ~250 TB

At 500 GB per shard: 250 TB / 500 GB = 500 shards
```

Add follows, likes, and comments and we need roughly **1,000 shards**.

### 24.5.4 Celebrity Handling

Celebrities (accounts with millions of followers) create the same fan-out problem as in Twitter. Instagram uses a similar hybrid approach:

**Regular accounts (under 50K followers)**:
- Fan-out on write: push post ID to all followers' feed caches.

**Celebrity accounts (over 50K followers)**:
- Fan-out on read: do NOT push to followers' caches. Instead, when a user loads their feed, merge celebrity posts at read time.

**Mixed timelines**: Most users follow a mix of regular accounts and a few celebrities. The Feed Service:
1. Reads the pre-built feed from Redis (contains regular account posts).
2. Fetches recent posts from each celebrity the user follows.
3. Merges and ranks.

The celebrity threshold for Instagram can be higher than Twitter (50K vs 10K) because:
- Instagram has far fewer posts per user per day than tweets.
- Feed latency tolerance is higher (300 ms vs 200 ms).

### 24.5.5 CDN Strategy

With 100 million photos per day, CDN is critical:

**Multi-tier caching**:

```
┌────────┐    ┌─────────────┐    ┌─────────────┐    ┌────────┐
│ Client │───▶│  CDN Edge   │───▶│ CDN Regional │───▶│   S3   │
│        │    │  (closest)  │    │  (mid-tier)  │    │(origin)│
└────────┘    └─────────────┘    └─────────────┘    └────────┘
```

- **Edge servers**: in 100+ cities worldwide. Serve ~95% of image requests.
- **Regional servers**: in 10-15 regions. Serve cache misses from edge.
- **Origin (S3)**: only hit for very cold content.

**Smart pre-warming**: When a post is uploaded, predict where followers are located and push the image to those edge servers proactively, before anyone requests it.

**Adaptive image serving**: Serve different image sizes based on:
- Client screen resolution (1x, 2x, 3x).
- Network speed (smaller images on slow connections).
- Format support (WebP vs JPEG).

---

## 24.6 Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id         BIGINT PRIMARY KEY,
    username        VARCHAR(30) UNIQUE NOT NULL,
    display_name    VARCHAR(100),
    email           VARCHAR(255) UNIQUE,
    phone           VARCHAR(20),
    bio             VARCHAR(300),
    profile_pic_url VARCHAR(500),
    is_private      BOOLEAN DEFAULT FALSE,
    is_celebrity    BOOLEAN DEFAULT FALSE,
    followers_count INT DEFAULT 0,
    following_count INT DEFAULT 0,
    posts_count     INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW()
);
-- Sharded by user_id
```

### Posts Table

```sql
CREATE TABLE posts (
    post_id         BIGINT PRIMARY KEY,     -- Snowflake ID
    user_id         BIGINT NOT NULL,
    caption         VARCHAR(2200),
    location_id     BIGINT,
    like_count      INT DEFAULT 0,
    comment_count   INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_time (user_id, created_at DESC)
);
-- Sharded by user_id
```

### Post Media Table

```sql
CREATE TABLE post_media (
    media_id        BIGINT PRIMARY KEY,
    post_id         BIGINT NOT NULL,
    media_type      ENUM('IMAGE', 'VIDEO'),
    s3_key          VARCHAR(500) NOT NULL,
    width           INT,
    height          INT,
    display_order   TINYINT NOT NULL,      -- for carousel ordering
    INDEX idx_post (post_id)
);
-- Sharded by user_id (co-located with posts)
```

### Follows Table

```sql
CREATE TABLE follows (
    follower_id     BIGINT NOT NULL,
    followee_id     BIGINT NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, followee_id),
    INDEX idx_followee (followee_id)
);
-- Sharded by follower_id
```

### Likes Table

```sql
CREATE TABLE likes (
    user_id         BIGINT NOT NULL,
    post_id         BIGINT NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, post_id),
    INDEX idx_post (post_id)
);
-- Sharded by post_id
```

### Comments Table

```sql
CREATE TABLE comments (
    comment_id      BIGINT PRIMARY KEY,
    post_id         BIGINT NOT NULL,
    user_id         BIGINT NOT NULL,
    content         VARCHAR(2200),
    parent_id       BIGINT,                -- for nested replies
    created_at      TIMESTAMP DEFAULT NOW(),
    INDEX idx_post_time (post_id, created_at)
);
-- Sharded by post_id
```

### Feed Cache (Redis)

```
Key:    feed:{user_id}
Type:   Sorted Set
Score:  post timestamp (epoch ms)
Member: post_id

Max size: 500 entries per user
TTL: 7 days (rebuild from database if expired)
```

---

## 24.7 API Design

### Upload a Photo

**Step 1: Get upload URL**

```
POST /api/v1/media/upload-url
Authorization: Bearer {token}

Request Body:
{
    "content_type": "image/jpeg",
    "file_size": 2048000
}

Response: 200 OK
{
    "upload_url": "https://s3.amazonaws.com/instagram-uploads/...",
    "media_id": "media_789",
    "expires_at": "2025-01-15T11:00:00Z"
}
```

**Step 2: Upload to S3** (client uploads directly)

**Step 3: Create post**

```
POST /api/v1/posts
Authorization: Bearer {token}

Request Body:
{
    "caption": "Beautiful sunset #photography",
    "media_ids": ["media_789"],
    "location": {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles"}
}

Response: 201 Created
{
    "post_id": "9876543210",
    "user": {"user_id": "42", "username": "alice"},
    "caption": "Beautiful sunset #photography",
    "media": [
        {
            "media_id": "media_789",
            "url": "https://cdn.instagram.com/p/media_789/large.webp",
            "width": 1080,
            "height": 1350
        }
    ],
    "created_at": "2025-01-15T10:30:00Z"
}
```

### Get News Feed

```
GET /api/v1/feed?cursor={last_post_id}&limit=10
Authorization: Bearer {token}

Response: 200 OK
{
    "posts": [
        {
            "post_id": "9876543210",
            "user": {"user_id": "42", "username": "alice", "profile_pic": "..."},
            "caption": "Beautiful sunset #photography",
            "media": [...],
            "like_count": 342,
            "comment_count": 15,
            "liked_by_viewer": false,
            "created_at": "2025-01-15T10:30:00Z"
        }
    ],
    "next_cursor": "9876543200"
}
```

### Like a Post

```
POST /api/v1/posts/{post_id}/like
Authorization: Bearer {token}

Response: 200 OK
{
    "liked": true,
    "like_count": 343
}
```

### Comment on a Post

```
POST /api/v1/posts/{post_id}/comments
Authorization: Bearer {token}

Request Body:
{
    "content": "Stunning shot!",
    "parent_id": null
}

Response: 201 Created
{
    "comment_id": "comment_123",
    "content": "Stunning shot!",
    "user": {"user_id": "99", "username": "bob"},
    "created_at": "2025-01-15T10:35:00Z"
}
```

---

## 24.8 Scaling the System

### Image Storage

- **Object storage (S3)** with intelligent tiering:
  - Hot tier: images less than 30 days old (frequently accessed).
  - Warm tier: 30-90 days old.
  - Cold tier: over 90 days old (rarely accessed, cheaper storage).
- **Lifecycle policies** move images between tiers automatically.

### Database Sharding

- **Shard by user_id** using consistent hashing.
- Co-locate related tables (users, posts, post_media) on the same shard.
- Follows table is sharded by follower_id for efficient "who do I follow?" queries.
- Likes and comments are sharded by post_id for efficient "show me likes for this post" queries.

### Feed Cache Scaling

- Redis cluster sharded by user_id.
- Each node handles ~1 million users' feeds.
- Total: 500 Redis nodes for 500 million DAU.
- Replication factor: 3 (one primary, two replicas).

### Auto-Scaling

- **Upload service**: scale based on upload queue depth.
- **Image processing**: scale based on processing queue length. Use spot instances for cost savings.
- **Feed service**: scale based on request rate (predictable daily patterns -- peak at morning and evening).

### Geographic Distribution

- Deploy application servers in multiple regions (US, Europe, Asia).
- Database primaries in one region; read replicas in all regions.
- CDN handles image delivery globally.
- Users are routed to the nearest region.

---

## 24.9 Trade-offs

| Decision | Option A | Option B | Our Choice | Why |
|----------|----------|----------|-------------|-----|
| Upload path | Through app server | Pre-signed URL to S3 | **Pre-signed URL** | Avoids wasting app server bandwidth on large files. |
| Image format | JPEG only | WebP + JPEG fallback | **WebP + fallback** | 30% smaller files, faster loading, with backward compatibility. |
| Feed ranking | Chronological | ML-ranked | **ML-ranked** | Increases engagement; chronological option as user setting. |
| Feed pre-computation | Compute on read | Fan-out on write | **Hybrid** | Balances write cost (celebrities) with read speed (regular users). |
| Sharding key | post_id | user_id | **user_id** | Co-locates user's data; profile page hits one shard. |
| Like counts | Exact (DB query) | Approximate (counter cache) | **Approximate** | Exact counts at scale require expensive distributed counting. |

---

## 24.10 Common Mistakes

1. **Routing image uploads through application servers.** This wastes bandwidth and creates bottlenecks. Use pre-signed URLs for direct S3 upload.

2. **Storing only one image size.** Serving a 5 MB original to a mobile device on 3G is a terrible user experience. Always generate multiple sizes.

3. **Forgetting about image processing latency.** The user should see their post immediately, even before all resized versions are ready. Show the original or a client-side preview while processing happens asynchronously.

4. **Ignoring CDN costs.** At 100 million images per day, CDN bandwidth is a significant cost. Discuss image compression, format optimization, and cache hit rates.

5. **Using a single global database.** At Instagram's scale, you need sharding. Discuss the shard key choice and its implications.

6. **Not mentioning privacy.** EXIF stripping removes GPS coordinates from uploaded photos. This is a real production concern.

---

## 24.11 Best Practices

1. **Separate the upload path from the metadata path.** Upload images directly to object storage; send metadata to application servers. This keeps the two concerns decoupled and independently scalable.

2. **Generate multiple image sizes asynchronously.** Do not block the upload response on image processing. Return success immediately and process in the background.

3. **Use content-addressable storage for deduplication.** Hash the image content and use the hash as the S3 key. If two users upload the same image, store it only once.

4. **Implement progressive image loading.** Load a tiny blurred placeholder first, then swap in the full image. This creates a perception of speed.

5. **Cache user profiles aggressively.** Every feed item shows the poster's username and profile picture. Cache these in Redis to avoid millions of database lookups per second.

6. **Use cursor-based pagination for feeds.** Never use OFFSET/LIMIT at scale -- it becomes slower as the offset increases.

---

## 24.12 Quick Summary

Instagram's architecture centers on three pillars: (1) a robust image processing pipeline that generates multiple sizes, compresses into modern formats, strips metadata, and distributes through a multi-tier CDN; (2) a hybrid fan-out strategy for news feed generation that pre-computes feeds for regular users while merging celebrity posts at read time; and (3) user_id-based sharding that co-locates each user's data for efficient profile and post queries. Pre-signed URLs enable direct-to-S3 uploads, keeping application servers lean. The feed uses ML-based ranking to surface the most relevant content.

---

## 24.13 Key Points

- **Pre-signed URLs** let clients upload images directly to S3, bypassing application servers.
- **Image processing pipeline** generates five sizes, compresses to WebP, and strips EXIF data asynchronously.
- **Multi-tier CDN** (edge, regional, origin) serves 95%+ of image requests from cache.
- **Hybrid fan-out** handles both regular and celebrity accounts for feed generation.
- **ML-based feed ranking** considers recency, relationship strength, interest, and engagement velocity.
- **Sharding by user_id** co-locates user profiles, posts, and media on the same shard.
- **Media storage dominates costs** at ~300 TB/day, requiring intelligent storage tiering.
- **Approximate like counts** (cached counters) are used instead of exact database counts at scale.
- **Progressive image loading** with blurred placeholders improves perceived performance.
- **Content-addressable storage** deduplicates identical images across users.

---

## 24.14 Practice Questions

1. If Instagram processes 100 million images per day and each image takes 5 seconds to process, how many processing workers do you need?

2. How would you handle the case where a user uploads a carousel of 10 images? Should all images be processed before the post appears in feeds?

3. A user with 10 million followers uploads a photo. Walk through the exact sequence of events from upload to the photo appearing in a follower's feed.

4. How would you implement a "like" button that feels instant to the user while being durable?

5. If the CDN cache hit rate drops from 95% to 80%, what happens to the origin servers, and how would you diagnose and fix it?

---

## 24.15 Exercises

1. **Storage cost estimation**: Calculate the monthly S3 storage cost for Instagram assuming 300 TB/day of new images, a 3-tier storage policy, and current S3 pricing.

2. **CDN bandwidth**: If the average user scrolls through 50 images per feed session (640px wide, WebP, ~80 KB each) and there are 5 billion feed sessions per day, calculate the daily CDN egress bandwidth.

3. **Schema design**: Extend the database schema to support Instagram Stories (ephemeral posts that expire after 24 hours). Consider how this affects storage and cleanup.

4. **Cache warming**: Design an algorithm that predicts which CDN edge servers should be pre-warmed when a celebrity uploads a photo, based on their follower distribution.

5. **Deduplication**: Design a system to detect and deduplicate near-identical images (not just exact matches) using perceptual hashing.

---

## 24.16 What Is Next?

In this chapter we designed a media-heavy social platform with image processing, CDN delivery, and ranked feeds. In the next chapter, **Chapter 25: Designing a Chat System**, we shift to a completely different paradigm: real-time, bidirectional communication. You will learn about WebSockets, message ordering guarantees, offline delivery, and how to build presence indicators -- challenges that require a fundamentally different architecture from the feed-based systems we have designed so far.
