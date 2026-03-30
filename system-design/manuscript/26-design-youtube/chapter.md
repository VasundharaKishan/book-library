# Chapter 26: Designing YouTube

Every minute, over 500 hours of video are uploaded to YouTube. Billions of people watch over a billion hours of video every day, streamed seamlessly from data centers to devices on every continent. YouTube is one of the largest, most complex systems ever built -- combining massive storage, real-time video processing, adaptive streaming, global CDN delivery, and machine learning-powered recommendations into a single product.

In this chapter we will design YouTube from the ground up. You will learn how the video upload and transcoding pipeline works, why adaptive bitrate streaming (HLS/DASH) is essential for a good viewing experience, how CDN delivery works for large video files, how the search and recommendation engines function, and how all the pieces fit together. This is a system design classic that tests your ability to think about storage, compute, and bandwidth at truly enormous scale.

---

## 26.1 Understanding the Problem

YouTube's core features are:

1. **Upload a video** -- creators upload video files that are processed and made available to viewers.
2. **Stream a video** -- viewers watch videos with adaptive quality based on their connection speed.
3. **Search videos** -- find videos by title, description, tags, and content.
4. **Recommendations** -- personalized suggestions for what to watch next.
5. **Engagement** -- like, comment, subscribe, and share.

### What Makes YouTube Uniquely Challenging?

- **Enormous file sizes.** A single 10-minute 4K video is ~3 GB. Multiply by 500 hours uploaded per minute.
- **Transcoding compute.** Every uploaded video must be transcoded into dozens of formats and resolutions. This is CPU-intensive and time-consuming.
- **Global streaming.** A video uploaded in Tokyo must stream smoothly to a viewer in rural Brazil on a 3G connection.
- **Storage never shrinks.** Unlike chat messages that can be archived, videos are expected to be available forever. Storage only grows.

---

## 26.2 Requirements

### Functional Requirements

| # | Requirement | Description |
|---|-------------|-------------|
| F1 | **Upload video** | Creators upload video files (up to 256 GB, 12 hours). |
| F2 | **Stream video** | Viewers watch videos with adaptive quality. |
| F3 | **Search** | Find videos by keywords, filters (date, duration, quality). |
| F4 | **Recommendations** | Show personalized "up next" and home page suggestions. |
| F5 | **Like / comment** | Viewers engage with videos. |
| F6 | **Subscribe** | Viewers subscribe to channels. |
| F7 | **Thumbnails** | Auto-generated and custom thumbnails for each video. |

### Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NF1 | **High availability** | 99.99% uptime for streaming. |
| NF2 | **Low startup latency** | Video starts playing within 2 seconds. |
| NF3 | **Adaptive quality** | Adjust bitrate in real time based on network conditions. |
| NF4 | **Scalability** | 2 billion monthly active users, 1 billion hours watched daily. |
| NF5 | **Durability** | No uploaded video is ever lost. |
| NF6 | **Global reach** | Low latency streaming from any location on Earth. |

### Out of Scope

- Live streaming (different architecture).
- Monetization and ad serving.
- Content moderation (important but orthogonal).
- YouTube Shorts.

---

## 26.3 Back-of-the-Envelope Estimation

### Upload Traffic

| Metric | Value |
|--------|-------|
| Video uploads per minute | 500 hours of content |
| Average video length | 10 minutes |
| Videos uploaded per minute | 500 x 60 / 10 = 3,000 videos |
| Videos uploaded per second | ~50 videos/s |
| Average raw file size (1080p) | 1.5 GB |
| Upload bandwidth | 50 x 1.5 GB = 75 GB/s ingress |

### Storage

Raw uploads per day:

```
50 videos/s x 86,400 s x 1.5 GB = 6,480 TB/day ≈ 6.5 PB/day (raw)
```

After transcoding, each video is stored in multiple resolutions and formats:

| Resolution | Bitrate | Size (10 min video) |
|-----------|---------|-------------------|
| 144p | 0.1 Mbps | 7.5 MB |
| 240p | 0.3 Mbps | 22.5 MB |
| 360p | 0.7 Mbps | 52.5 MB |
| 480p | 1.5 Mbps | 112.5 MB |
| 720p | 3 Mbps | 225 MB |
| 1080p | 6 Mbps | 450 MB |
| 1440p | 10 Mbps | 750 MB |
| 4K | 20 Mbps | 1,500 MB |
| **Total (all resolutions)** | | **~3.1 GB** |

With ~2x overhead for different codecs (H.264, VP9, AV1):

```
Per video: ~6 GB total stored
Daily: 50 videos/s x 86,400 s x 6 GB = 25.9 PB/day
Yearly: ~9.5 EB/year
```

### Streaming Traffic

```
1 billion hours watched daily
Average bitrate: 5 Mbps (mix of qualities)
1B hours x 3600 s/hour x 5 Mbps = 18 exabits/day
= 2.25 exabytes/day = 26 TB/s sustained
```

This is the scale that requires a massive CDN.

### Thumbnail Storage

Each video generates 3 auto-thumbnails plus 1 custom upload, each in 3 sizes:

```
4 thumbnails x 3 sizes x 50 KB = 600 KB per video
50 videos/s x 86,400 s x 600 KB = 2.6 TB/day
```

Thumbnails are tiny compared to video but served much more frequently (every search result, recommendation, and browse page shows thumbnails).

---

## 26.4 High-Level Design

```
┌──────────┐          ┌───────────────┐
│ Creator   │─────────▶│  API Gateway  │
│ (Upload)  │          └───────┬───────┘
└──────────┘                   │
                    ┌──────────┼──────────────────┐
                    │          │                  │
             ┌──────▼──────┐  │           ┌──────▼──────┐
             │   Upload    │  │           │   Video     │
             │   Service   │  │           │   Metadata  │
             └──────┬──────┘  │           │   Service   │
                    │         │           └──────┬──────┘
             ┌──────▼──────┐  │           ┌──────▼──────┐
             │  Original   │  │           │  Metadata   │
             │  Storage    │  │           │  Database   │
             │  (S3/GCS)   │  │           │  (MySQL)    │
             └──────┬──────┘  │           └─────────────┘
                    │         │
             ┌──────▼─────────────────────────────────┐
             │         Transcoding Pipeline            │
             │                                         │
             │  Raw ──▶ Decode ──▶ Encode (N formats) │
             │                 ──▶ Thumbnails          │
             │                 ──▶ Quality checks      │
             └──────────────────────────┬──────────────┘
                                        │
             ┌──────────────────────────▼──────────────┐
             │         Transcoded Storage (S3/GCS)      │
             └──────────────────────────┬──────────────┘
                                        │
                                 ┌──────▼──────┐
                                 │     CDN      │
                                 │  (Global)    │
                                 └──────┬──────┘
                                        │
                                 ┌──────▼──────┐
                                 │   Viewer     │
                                 │  (Streaming) │
                                 └─────────────┘

              ┌───────────────┐     ┌──────────────────┐
              │ Search Index  │     │ Recommendation    │
              │(Elasticsearch)│     │ Engine (ML)       │
              └───────────────┘     └──────────────────┘
```

### Request Flow: Uploading a Video

1. Creator initiates upload through the client app.
2. **Upload Service** handles the upload:
   - For large files, uses **resumable upload** (chunked upload with checkpointing).
   - Raw video is stored in **original storage** (S3/GCS).
3. Upload Service creates a metadata record in the **Metadata Database** with status "processing".
4. Upload Service publishes a "video uploaded" event to the **message queue** (Kafka).
5. **Transcoding Pipeline** picks up the event and processes the video:
   - Decodes the original video.
   - Encodes into 8 resolutions x 2-3 codecs = 16-24 output files.
   - Generates thumbnails.
   - Runs quality checks (bitrate verification, corruption detection).
   - Stores all output files in **transcoded storage**.
6. Transcoding Pipeline publishes "transcoding complete" event.
7. **Metadata Service** updates the video status to "published".
8. **Search Indexer** indexes the video metadata for search.
9. The video is now available for streaming.

### Request Flow: Watching a Video

1. Viewer clicks on a video. Client requests the **video manifest** from the Metadata Service.
2. The manifest contains URLs for all available qualities (a `.m3u8` for HLS or `.mpd` for DASH).
3. Client's video player selects the appropriate quality based on screen size and bandwidth.
4. Player requests video **segments** (small chunks, typically 2-10 seconds each) from the **CDN**.
5. CDN serves segments from edge cache. On cache miss, pulls from origin (transcoded storage).
6. Player continuously monitors bandwidth and switches quality up or down (adaptive bitrate).
7. View event is logged for analytics and recommendation engine.

---

## 26.5 Deep Dive

### 26.5.1 Upload and Transcoding Pipeline

This is the most compute-intensive component. Let us break it down:

**Resumable Upload**

Large video files (potentially gigabytes) cannot be uploaded in a single HTTP request. We use resumable uploads:

```
1. Client: POST /upload/init
   Server: returns upload_id, chunk_size (5 MB)

2. Client uploads chunks:
   PUT /upload/{upload_id}/chunk/{chunk_number}
   (each chunk is 5 MB)

3. If upload is interrupted:
   Client: GET /upload/{upload_id}/status
   Server: returns last successful chunk number
   Client resumes from the next chunk

4. After all chunks uploaded:
   Client: POST /upload/{upload_id}/complete
   Server: concatenates chunks, starts processing
```

**Transcoding Architecture**

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Task       │     │  Transcoding │     │  Transcoding │
│   Queue      │────▶│  Worker 1    │     │  Worker N    │
│   (Kafka)    │     │  (GPU/CPU)   │     │  (GPU/CPU)   │
└─────────────┘     └──────┬───────┘     └──────┬───────┘
                           │                     │
                    ┌──────▼─────────────────────▼───┐
                    │      Transcoded Storage (S3)    │
                    └────────────────────────────────┘
```

**Parallelization strategy**:
1. Split the video into segments (e.g., 10-second chunks).
2. Transcode each segment independently across multiple workers.
3. Each worker encodes its segment into all required resolutions.
4. Merge the transcoded segments back together.

This turns a 30-minute transcoding job into a 2-3 minute job with enough workers.

**Codec choices**:

| Codec | Compression | CPU cost | Compatibility |
|-------|------------|----------|--------------|
| H.264 | Good | Low | Universal |
| VP9 | 30% better than H.264 | High | Chrome, Android |
| AV1 | 30% better than VP9 | Very high | Growing support |

YouTube transcodes to multiple codecs and serves the most efficient one the client supports.

### 26.5.2 Adaptive Bitrate Streaming (HLS / DASH)

Adaptive bitrate streaming is the key technology that makes video playback smooth across varying network conditions.

**How it works**:

```
┌─────────────────────────────────────────────────────┐
│                    Video File                        │
│                                                     │
│  Split into segments:                               │
│  [Seg 1][Seg 2][Seg 3][Seg 4][Seg 5]...            │
│  (each 2-10 seconds)                                │
│                                                     │
│  Each segment encoded at multiple bitrates:          │
│                                                     │
│  4K:    [Seg1_4K ][Seg2_4K ][Seg3_4K ]...  20 Mbps │
│  1080p: [Seg1_1080][Seg2_1080][Seg3_1080]...  6 Mbps│
│  720p:  [Seg1_720 ][Seg2_720 ][Seg3_720 ]...  3 Mbps│
│  480p:  [Seg1_480 ][Seg2_480 ][Seg3_480 ]...  1.5Mbps│
│  360p:  [Seg1_360 ][Seg2_360 ][Seg3_360 ]...  0.7Mbps│
│                                                     │
│  Manifest file (.m3u8 / .mpd) lists all variants    │
└─────────────────────────────────────────────────────┘
```

**Playback flow**:

1. Player requests the manifest file.
2. Manifest lists all available qualities and segment URLs.
3. Player starts with a conservative quality (e.g., 720p).
4. Player downloads segment 1 at 720p.
5. Player measures actual download speed:
   - If bandwidth > 6 Mbps: switch to 1080p for the next segment.
   - If bandwidth < 1 Mbps: switch to 360p for the next segment.
6. Quality switches happen at segment boundaries (seamless to the viewer).

**HLS vs DASH**:

| Aspect | HLS (Apple) | DASH |
|--------|-------------|------|
| Manifest format | .m3u8 (text) | .mpd (XML) |
| Segment format | .ts or .fmp4 | .m4s (fmp4) |
| Browser support | Safari native, others via JS | Chrome, Firefox, Edge native |
| DRM support | FairPlay | Widevine, PlayReady |
| Market share | Dominant on Apple devices | Dominant elsewhere |

YouTube serves both HLS and DASH depending on the client.

### 26.5.3 CDN Delivery

YouTube's CDN strategy is multi-layered:

```
┌────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────┐
│ Viewer │───▶│  CDN Edge   │───▶│  CDN Regional│───▶│  Origin  │
│        │    │  (ISP-level)│    │  (City-level)│    │  (GCS)   │
└────────┘    └─────────────┘    └──────────────┘    └──────────┘
```

**Tier 1 -- Edge cache (ISP peering)**:
- YouTube deploys cache servers inside ISP networks (called Google Global Cache, or GGC).
- These serve the majority of popular video segments directly from the ISP's network.
- Zero transit cost for the ISP and minimal latency for the viewer.

**Tier 2 -- Regional edge (city PoPs)**:
- Google-owned data centers in major cities.
- Serve cache misses from Tier 1.

**Tier 3 -- Origin storage**:
- Video master copies in Google Cloud Storage.
- Only accessed for very cold content (old, unpopular videos).

**Cache strategy**:
- **Popular videos** (top 20% that generate 80% of views): proactively pushed to edge caches.
- **Long-tail videos** (millions of videos with few views each): cached on demand, evicted with LRU.
- **Segment-level caching**: only cache the segments actually requested, not entire videos.

### 26.5.4 Video Metadata and Search

**Metadata Database (MySQL)**:
- Stores video title, description, tags, category, upload date, view count, like/dislike count.
- Sharded by video_id.

**Search Index (Elasticsearch)**:
- Indexes video metadata for full-text search.
- Fields indexed: title (boosted weight), description, tags, channel name, auto-generated captions.
- Ranking factors: relevance score, view count, recency, engagement rate, channel authority.

**Auto-generated captions**:
- YouTube uses speech-to-text ML models to generate captions for uploaded videos.
- Captions are indexed for search, making video content searchable even if the title is vague.
- This is a significant competitive advantage (most of the searchable content is in the audio, not the title).

### 26.5.5 Recommendation Engine

Recommendations drive most views on YouTube (over 70% of watch time comes from recommendations).

**Architecture**:

```
┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│  User Watch  │────▶│  Feature       │────▶│  ML Model    │
│  History     │     │  Engineering   │     │  Serving     │
└──────────────┘     └────────────────┘     └──────┬───────┘
                                                   │
┌──────────────┐     ┌────────────────┐     ┌──────▼───────┐
│  Video       │────▶│  Candidate     │────▶│  Ranking     │
│  Features    │     │  Generation    │     │  (Top N)     │
└──────────────┘     └────────────────┘     └──────────────┘
```

**Two-stage pipeline**:

1. **Candidate generation**: from millions of videos, narrow down to a few hundred candidates.
   - Collaborative filtering: users who watched video A also watched video B.
   - Content-based: videos with similar titles, tags, and categories.
   - Social signals: videos popular among the user's demographic.

2. **Ranking**: score each candidate and select the top N.
   - Features: video age, view velocity, user engagement history, watch time prediction.
   - Model: deep neural network trained on billions of watch events.
   - Output: predicted watch time (not click probability -- this reduces clickbait).

**Serving**: Pre-compute recommendations periodically (every few hours) and cache them. Augment with real-time signals (what the user just watched) at request time.

### 26.5.6 Thumbnail Generation

Thumbnails are critical for click-through rate. YouTube generates them automatically:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Transcoded │────▶│  Thumbnail   │────▶│  Thumbnail   │
│  Video      │     │  Extractor   │     │  Storage     │
└─────────────┘     │              │     │  (S3 + CDN)  │
                    │ - Sample N   │     └──────────────┘
                    │   frames     │
                    │ - Score by   │
                    │   quality    │
                    │ - Pick top 3 │
                    └──────────────┘
```

**Process**:
1. Sample frames at regular intervals (every 2 seconds).
2. Score each frame using an ML model (clarity, composition, faces, text readability).
3. Select the top 3 as auto-generated thumbnails.
4. Creator can also upload a custom thumbnail.
5. Generate each thumbnail in multiple sizes (120x90, 320x180, 480x360, 1280x720).
6. Serve from CDN with aggressive caching (thumbnails are immutable once generated).

---

## 26.6 Database Schema

### Videos Table

```sql
CREATE TABLE videos (
    video_id        BIGINT PRIMARY KEY,     -- Snowflake ID
    channel_id      BIGINT NOT NULL,
    title           VARCHAR(100) NOT NULL,
    description     TEXT,
    status          ENUM('uploading', 'processing', 'published', 'failed', 'removed'),
    duration_seconds INT,
    original_s3_key VARCHAR(500),
    view_count      BIGINT DEFAULT 0,
    like_count      INT DEFAULT 0,
    dislike_count   INT DEFAULT 0,
    comment_count   INT DEFAULT 0,
    category        VARCHAR(50),
    tags            JSON,
    language        VARCHAR(10),
    published_at    TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW(),
    INDEX idx_channel_time (channel_id, published_at DESC),
    INDEX idx_status (status)
);
-- Sharded by video_id
```

### Video Formats Table

```sql
CREATE TABLE video_formats (
    video_id        BIGINT NOT NULL,
    format_id       INT NOT NULL,           -- e.g., 1=144p_h264, 2=240p_h264, ...
    resolution      VARCHAR(10),            -- '1080p', '720p', etc.
    codec           VARCHAR(20),            -- 'h264', 'vp9', 'av1'
    bitrate_kbps    INT,
    s3_key          VARCHAR(500),
    manifest_url    VARCHAR(500),
    file_size_bytes BIGINT,
    PRIMARY KEY (video_id, format_id)
);
-- Sharded by video_id (co-located with videos)
```

### Channels Table

```sql
CREATE TABLE channels (
    channel_id      BIGINT PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    subscriber_count BIGINT DEFAULT 0,
    video_count     INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### Comments Table

```sql
CREATE TABLE comments (
    comment_id      BIGINT PRIMARY KEY,
    video_id        BIGINT NOT NULL,
    user_id         BIGINT NOT NULL,
    content         VARCHAR(10000),
    parent_id       BIGINT,                -- for threaded replies
    like_count      INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    INDEX idx_video_time (video_id, created_at DESC)
);
-- Sharded by video_id
```

### Watch History Table

```sql
CREATE TABLE watch_history (
    user_id         BIGINT,
    video_id        BIGINT,
    watched_seconds INT,
    total_seconds   INT,
    watched_at      TIMESTAMP,
    PRIMARY KEY (user_id, watched_at)
) -- In Cassandra or BigTable for write throughput
WITH CLUSTERING ORDER BY (watched_at DESC);
```

### Thumbnails Table

```sql
CREATE TABLE thumbnails (
    video_id        BIGINT NOT NULL,
    thumbnail_type  ENUM('auto_1', 'auto_2', 'auto_3', 'custom'),
    size            VARCHAR(20),            -- '120x90', '320x180', etc.
    s3_key          VARCHAR(500),
    is_default      BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (video_id, thumbnail_type, size)
);
```

---

## 26.7 API Design

### Upload a Video

**Step 1: Initialize upload**

```
POST /api/v1/videos/upload/init
Authorization: Bearer {token}

Request Body:
{
    "title": "System Design Tutorial",
    "description": "Learn system design...",
    "file_size": 1500000000,
    "content_type": "video/mp4",
    "category": "Education",
    "tags": ["system design", "interview"]
}

Response: 200 OK
{
    "upload_id": "upload_abc123",
    "video_id": "vid_789",
    "chunk_size": 5242880,
    "upload_url": "https://upload.youtube.com/v1/upload/upload_abc123"
}
```

**Step 2: Upload chunks**

```
PUT /api/v1/videos/upload/{upload_id}/chunk/{chunk_number}
Content-Type: application/octet-stream
Content-Length: 5242880

[binary chunk data]

Response: 200 OK
{
    "chunk_number": 42,
    "status": "received"
}
```

**Step 3: Complete upload**

```
POST /api/v1/videos/upload/{upload_id}/complete

Response: 202 Accepted
{
    "video_id": "vid_789",
    "status": "processing",
    "estimated_processing_time": "5 minutes"
}
```

### Stream a Video

```
GET /api/v1/videos/{video_id}/manifest
Authorization: Bearer {token}

Response: 200 OK
{
    "video_id": "vid_789",
    "title": "System Design Tutorial",
    "manifest_urls": {
        "hls": "https://cdn.youtube.com/vid_789/master.m3u8",
        "dash": "https://cdn.youtube.com/vid_789/manifest.mpd"
    },
    "available_qualities": ["4k", "1080p", "720p", "480p", "360p", "240p", "144p"],
    "thumbnails": {
        "default": "https://cdn.youtube.com/vid_789/thumb_default.jpg"
    }
}
```

### Search Videos

```
GET /api/v1/search?q=system+design&sort=relevance&duration=medium&limit=20&cursor=xxx
Authorization: Bearer {token}

Response: 200 OK
{
    "results": [
        {
            "video_id": "vid_789",
            "title": "System Design Tutorial",
            "channel": {"name": "TechChannel", "subscriber_count": 500000},
            "view_count": 1200000,
            "duration": 3600,
            "thumbnail": "https://cdn.youtube.com/vid_789/thumb_320x180.jpg",
            "published_at": "2025-01-10T08:00:00Z"
        }
    ],
    "next_cursor": "..."
}
```

### Get Recommendations

```
GET /api/v1/recommendations?video_id={video_id}&limit=20
Authorization: Bearer {token}

Response: 200 OK
{
    "recommendations": [
        {
            "video_id": "vid_456",
            "title": "Advanced System Design",
            "reason": "Similar to what you watched",
            ...
        }
    ]
}
```

---

## 26.8 Scaling the System

### Upload and Transcoding

- **Auto-scaling worker fleet**: scale transcoding workers based on queue depth.
- **GPU acceleration**: use GPU instances for video encoding (10-50x faster than CPU).
- **Spot/preemptible instances**: transcoding is fault-tolerant (can restart from the last checkpoint), making it ideal for cheap spot instances.
- **Priority queues**: creator partners and paying users get faster transcoding.

### Storage Tiering

```
┌─────────────────────────────────────────────────────┐
│                   Storage Tiers                      │
│                                                     │
│  Hot (SSD):    Videos < 7 days old (most views)     │
│  Warm (HDD):  Videos 7-90 days old                  │
│  Cold (Archive): Videos > 90 days old, < 10 views/month │
│  Glacier:     Videos > 1 year, near zero views       │
└─────────────────────────────────────────────────────┘
```

Lifecycle policies automatically migrate videos between tiers. When a cold video is requested, it is promoted back to warm/hot storage.

### CDN Scaling

- Deploy cache servers at ISP peering points (Google Global Cache).
- Use consistent hashing to distribute video segments across CDN nodes.
- Serve popular videos from L1 cache (hit rate > 90%).
- Pre-warm CDN for videos that are predicted to go viral (based on early view velocity).

### View Count Scaling

View counts are updated billions of times per day. Exact real-time counting is expensive:

```
Approximate counting strategy:
1. Client logs view events to Kafka
2. Stream processor (Flink) counts views in 1-minute windows
3. Aggregated counts written to Redis (near real-time display)
4. Batch job reconciles exact counts every hour and writes to MySQL
```

### Database Scaling

- **Videos metadata**: MySQL sharded by video_id. 500 shards with read replicas.
- **Watch history**: Cassandra (write-heavy, time-series). Partition by user_id.
- **View counts**: Redis for real-time approximate, MySQL for exact historical.
- **Search index**: Elasticsearch cluster with time-based sharding.

---

## 26.9 Trade-offs

| Decision | Option A | Option B | Our Choice | Why |
|----------|----------|----------|-------------|-----|
| Upload method | Single request | Resumable chunked | **Resumable** | Large files need checkpoint/resume capability. |
| Transcoding | On-demand | Pre-transcode all formats | **Pre-transcode** | Pay compute cost once; serve instantly forever. |
| Codec strategy | Single codec (H.264) | Multi-codec | **Multi-codec** | 30-50% bandwidth savings with VP9/AV1 for supported clients. |
| Streaming protocol | Progressive download | Adaptive bitrate (HLS/DASH) | **Adaptive** | Adjusts to network conditions; better experience on variable connections. |
| CDN strategy | Third-party CDN | Own CDN (ISP peering) | **Own CDN** | At YouTube's scale, owning is cheaper and gives more control. |
| View counting | Exact real-time | Approximate near real-time | **Approximate** | Exact counting at billions/day is too expensive; approximate is good enough for display. |
| Recommendation | Collaborative filtering only | Deep learning | **Deep learning** | Better personalization, predicts watch time (not just clicks). |

---

## 26.10 Common Mistakes

1. **Ignoring transcoding complexity.** Saying "we just store the video" misses the most compute-intensive part of the system. Always discuss the transcoding pipeline, codec choices, and parallelization.

2. **Forgetting adaptive bitrate.** Serving a single quality file means either wasting bandwidth on low-end connections or providing poor quality on fast ones. ABR is essential.

3. **Underestimating storage.** YouTube-scale storage is measured in exabytes. Discuss storage tiering and lifecycle management.

4. **Not mentioning resumable uploads.** A 2 GB video upload over a flaky connection needs resume capability. This is not optional.

5. **Treating CDN as a black box.** At YouTube's scale, CDN is not just "put it on Cloudflare." Discuss ISP peering, cache hierarchy, and pre-warming strategies.

6. **Ignoring the recommendation engine.** Recommendations drive 70%+ of views. Skipping this means missing a core component.

---

## 26.11 Best Practices

1. **Transcode in parallel using segmented encoding.** Split the video into chunks, transcode each independently, then merge. This reduces processing time from hours to minutes.

2. **Use multiple codecs.** Serve AV1 to clients that support it (50% bandwidth savings over H.264), VP9 as fallback, and H.264 for universal compatibility.

3. **Implement storage tiering aggressively.** Most videos get 90% of their views in the first week. Move cold content to cheaper storage tiers automatically.

4. **Pre-warm CDN for trending content.** When a video's view velocity spikes, proactively push it to more edge locations before it overwhelms the origin.

5. **Log watch events for everything.** Watch history, completion rate, pause/seek events, and quality switches are all valuable signals for the recommendation engine and content analytics.

6. **Separate the upload pipeline from the serving pipeline.** Uploading and transcoding are CPU/bandwidth-intensive; serving is latency-sensitive. Keep them on separate infrastructure.

---

## 26.12 Quick Summary

YouTube's architecture is built around four pillars: (1) a resumable upload pipeline that feeds into a massively parallel transcoding system, producing video segments in multiple resolutions and codecs; (2) adaptive bitrate streaming (HLS/DASH) that serves video in small segments, dynamically adjusting quality based on the viewer's network conditions; (3) a multi-tier CDN with ISP-level peering that serves 90%+ of video traffic from edge caches; and (4) a deep learning-based recommendation engine that drives 70%+ of watch time by predicting user engagement. Storage is measured in exabytes and managed through aggressive tiering. View counts use approximate near-real-time counting for display with periodic exact reconciliation.

---

## 26.13 Key Points

- **Resumable chunked uploads** handle large video files (up to 256 GB) with checkpoint/resume capability.
- **Parallel segmented transcoding** splits videos into chunks, encodes independently, and merges -- reducing processing time by 10x+.
- **Multiple codecs** (H.264, VP9, AV1) serve the most efficient format each client supports.
- **Adaptive bitrate streaming** (HLS/DASH) adjusts video quality per segment based on real-time network conditions.
- **ISP-level CDN peering** (Google Global Cache) serves most traffic from within the viewer's ISP network.
- **Storage tiering** (hot/warm/cold/archive) manages exabyte-scale storage costs.
- **Approximate view counting** (stream processing + periodic batch reconciliation) handles billions of daily view events.
- **Two-stage recommendation** (candidate generation + deep learning ranking) predicts watch time, not just clicks.
- **Auto-generated thumbnails** use ML to select the best frames; multiple sizes are served from CDN.
- **Video segments** (2-10 seconds each) are the unit of caching, streaming, and quality switching.

---

## 26.14 Practice Questions

1. A creator uploads a 4K, 2-hour video (50 GB raw). Estimate the total storage needed after transcoding into all resolutions and codecs.

2. How would you handle the case where a video goes viral 5 minutes after upload, before transcoding into all formats is complete?

3. If the CDN cache hit rate drops from 95% to 85%, what is the impact on origin servers (in TB/s of additional traffic)?

4. How would you design the "watch later" and "playlist" features? What database and caching strategy would you use?

5. A video has 1 billion views. How would you efficiently count and display this without overwhelming the database?

---

## 26.15 Exercises

1. **Transcoding capacity**: If each transcoding worker can process 1 minute of video per minute (real-time speed), and YouTube receives 500 hours of video per minute that needs to be transcoded into 20 formats, how many workers are needed? What if GPU workers are 20x faster?

2. **CDN cost estimation**: Calculate the monthly CDN egress cost for serving 1 billion hours of video at an average bitrate of 5 Mbps, assuming $0.02 per GB of egress.

3. **Manifest file design**: Write a sample HLS manifest file (.m3u8) for a video with 4 quality levels (360p, 720p, 1080p, 4K), showing the segment URLs and bitrate declarations.

4. **Storage lifecycle**: Design the rules for a storage lifecycle policy that minimizes cost while ensuring videos are always accessible. Consider view frequency, video age, and access latency requirements.

5. **Recommendation evaluation**: Design an A/B testing framework for the recommendation engine. What metrics would you track? How would you ensure the test is statistically significant?

---

## 26.16 What Is Next?

In this chapter we designed a video platform handling exabytes of storage, millions of concurrent streams, and sophisticated content recommendations. In the next chapter, **Chapter 27: Designing Uber**, we move to a fundamentally different domain: real-time geospatial systems. You will learn about geohashing and quadtrees for spatial indexing, real-time driver matching, ETA estimation, surge pricing algorithms, and how to build a dispatch system that matches riders with drivers in seconds -- challenges that require thinking about geography, time, and economics simultaneously.
