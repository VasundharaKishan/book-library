# Chapter 17: Blob Storage

## What You Will Learn

- What blob storage is and why it exists
- The difference between object storage, block storage, and file storage
- How S3-like architecture works under the hood
- What metadata is and how it makes objects searchable
- How pre-signed URLs provide secure, temporary access to files
- How CDN integration accelerates file delivery worldwide
- How an image processing pipeline handles uploads at scale
- How video transcoding works and why it is necessary
- What storage tiers are and how to save money with lifecycle policies
- How Instagram handles millions of photo uploads per day

## Why This Chapter Matters

Imagine a library. Books are neatly organized on shelves with a catalog system. You look up a title in the catalog, find the shelf number, and walk to the right spot. Now imagine a warehouse full of shipping containers. Each container holds something different: furniture, electronics, clothing. You do not organize them by type. You give each container a unique label, record its location, and retrieve it by label when needed.

Blob storage works like that warehouse. "Blob" stands for Binary Large Object. It stores unstructured data: photos, videos, PDFs, backups, log files -- anything that is not a row in a database table. Every time you upload a profile picture, watch a video, or download a file from the cloud, you are interacting with blob storage. Companies like Netflix, Instagram, and Dropbox store petabytes of data in blob storage. Understanding how it works is essential for any system design involving media, files, or large data.

---

## What Is Blob Storage?

Blob storage is a system designed to store large, unstructured binary data. Unlike a relational database (which stores structured rows and columns) or a file system (which organizes files in directories), blob storage treats each piece of data as an opaque "blob" identified by a unique key.

```
  Relational Database:           File System:              Blob Storage:
  (Structured Data)              (Hierarchical)            (Flat Namespace)

  +----+-------+------+         /home/                    bucket: my-photos
  | id | name  | age  |           /user/                    key: photo_001.jpg
  +----+-------+------+             /photos/                key: photo_002.jpg
  | 1  | Alice | 30   |               img1.jpg              key: vacation/sunset.jpg
  | 2  | Bob   | 25   |               img2.jpg              key: profile/avatar.png
  +----+-------+------+             /docs/
                                       resume.pdf           bucket: my-docs
  Best for: queries,             Best for: local            key: resume.pdf
  joins, transactions            access, small files        key: report_2024.pdf

                                                           Best for: large files,
                                                           media, backups, any
                                                           unstructured data
```

### Core Concepts

- **Blob**: A chunk of binary data. Could be an image, video, PDF, database backup, or any file.
- **Bucket** (Container): A top-level namespace that groups related blobs. Like a folder, but flat.
- **Key** (Object Key): A unique identifier for a blob within a bucket. Often looks like a file path: `users/123/profile.jpg`.
- **Metadata**: Key-value pairs attached to a blob describing it (content type, size, upload date, custom tags).

```
  Blob Storage Anatomy:

  +--------------------------------------------------+
  |  BUCKET: "instagram-photos"                       |
  |                                                   |
  |  +---------------------------------------------+ |
  |  | KEY: "users/alice/photo_001.jpg"             | |
  |  | DATA: [binary image data, 2.3 MB]            | |
  |  | METADATA:                                    | |
  |  |   content-type: image/jpeg                   | |
  |  |   size: 2,412,544 bytes                      | |
  |  |   uploaded: 2024-01-15T10:30:00Z             | |
  |  |   resolution: 4032x3024                      | |
  |  |   user-id: alice_123                         | |
  |  +---------------------------------------------+ |
  |                                                   |
  |  +---------------------------------------------+ |
  |  | KEY: "users/bob/video_042.mp4"               | |
  |  | DATA: [binary video data, 156 MB]            | |
  |  | METADATA:                                    | |
  |  |   content-type: video/mp4                    | |
  |  |   size: 163,577,856 bytes                    | |
  |  |   duration: 45s                              | |
  |  +---------------------------------------------+ |
  +--------------------------------------------------+
```

---

## Object Storage vs Block Storage vs File Storage

These three storage types serve very different purposes. Understanding the differences is critical for system design.

### Block Storage

Block storage splits data into fixed-size chunks called "blocks" and stores them on disk. It is the lowest level of storage. Your laptop's hard drive is block storage. In the cloud, it powers virtual machine disks.

Think of it as a stack of blank papers. You can write anything on any page, but there is no built-in organization. The operating system or database manages how blocks are used.

### File Storage

File storage organizes data in a hierarchical directory structure with files and folders. It is what you see in your computer's file explorer. In the cloud, services like Amazon EFS or Azure Files provide shared file storage.

Think of it as a filing cabinet. Folders hold subfolders, which hold files. You navigate by path: `/reports/2024/january/sales.csv`.

### Object Storage

Object storage stores data as objects in a flat namespace. Each object has data, metadata, and a unique key. There are no directories (although keys can use `/` to simulate them). It is designed for massive scale, durability, and HTTP access.

Think of it as a warehouse of labeled containers. You do not care where the container is physically stored. You just use the label to find it.

```
  Comparison:

  +------------------+-------------------+-------------------+
  |   Block Storage  |   File Storage    |  Object Storage   |
  +------------------+-------------------+-------------------+
  | Fixed-size blocks| Files in folders  | Objects with keys |
  | No metadata      | File metadata     | Rich metadata     |
  | Low-level access | Path-based access | HTTP API access   |
  | Fastest I/O      | Moderate I/O      | Higher latency    |
  | Limited scale    | Moderate scale    | Unlimited scale   |
  | VM disks, DBs    | Shared file sys   | Media, backups    |
  +------------------+-------------------+-------------------+

  Examples:
  Block: AWS EBS, Azure Disk, GCP Persistent Disk
  File:  AWS EFS, Azure Files, GCP Filestore
  Object: AWS S3, Azure Blob, GCP Cloud Storage
```

| Feature | Block Storage | File Storage | Object Storage |
|---|---|---|---|
| Access pattern | Random read/write | Sequential, path-based | Whole object read/write |
| Latency | Sub-millisecond | Milliseconds | Tens of milliseconds |
| Scale | Terabytes | Terabytes | Petabytes+ |
| Protocol | SCSI, NVMe | NFS, SMB | HTTP REST API |
| Best for | Databases, VMs | Shared documents | Media files, backups |
| Modify part of file? | Yes (block-level) | Yes (seek + write) | No (replace entire object) |

### Key Insight

Object storage cannot modify part of a file. To change one pixel in a photo, you must re-upload the entire photo. This is a deliberate trade-off: giving up partial updates enables massive scalability and durability.

---

## S3-Like Architecture

Amazon S3 (Simple Storage Service) is the most widely used blob storage service. Understanding its architecture helps you understand all object storage systems.

### How S3 Works Internally

```
  S3-Like Architecture (Simplified):

  +--------+    PUT /bucket/key    +------------------+
  | Client | --------------------> |   API Gateway    |
  +--------+                       | (Load Balanced)  |
                                   +--------+---------+
                                            |
                                   +--------v---------+
                                   |  Metadata Store   |
                                   |  (Key -> Location)|
                                   |  (DynamoDB-like)  |
                                   +--------+---------+
                                            |
                              +-------------+-------------+
                              |             |             |
                     +--------v--+  +-------v---+  +-----v-----+
                     | Storage   |  | Storage   |  | Storage   |
                     | Node A    |  | Node B    |  | Node C    |
                     | (Replica 1)|  | (Replica 2)|  | (Replica 3)|
                     +-----------+  +-----------+  +-----------+
                     | Disk 1    |  | Disk 1    |  | Disk 1    |
                     | Disk 2    |  | Disk 2    |  | Disk 2    |
                     | ...       |  | ...       |  | ...       |
                     +-----------+  +-----------+  +-----------+

  Write Path:
  1. Client sends PUT request with object data
  2. API Gateway routes to metadata store
  3. Metadata store assigns storage nodes
  4. Data replicated to 3+ nodes across availability zones
  5. Metadata (key, location, checksum) stored
  6. Client gets 200 OK after all replicas confirm

  Read Path:
  1. Client sends GET request with bucket + key
  2. API Gateway queries metadata store for location
  3. Data fetched from nearest healthy storage node
  4. Client receives object data
```

### Durability and Availability

S3 provides 99.999999999% (eleven 9s) durability. This means if you store 10 million objects, you can expect to lose one object every 10,000 years.

How? By storing each object redundantly across multiple physical locations.

```
  Durability through Redundancy:

  Your photo "vacation.jpg" stored in S3:

  +-------------------+     +-------------------+     +-------------------+
  | Availability      |     | Availability      |     | Availability      |
  | Zone A            |     | Zone B            |     | Zone C            |
  | (Building 1)      |     | (Building 2)      |     | (Building 3)      |
  |                   |     |                   |     |                   |
  | [vacation.jpg]    |     | [vacation.jpg]    |     | [vacation.jpg]    |
  | Copy 1            |     | Copy 2            |     | Copy 3            |
  +-------------------+     +-------------------+     +-------------------+

  Even if an entire building burns down,
  your photo is safe in the other two.
```

### Common S3 Operations

| Operation | HTTP Method | Description |
|---|---|---|
| Upload | PUT | Store a new object |
| Download | GET | Retrieve an object |
| Delete | DELETE | Remove an object |
| List | GET (bucket) | List objects in a bucket |
| Head | HEAD | Get object metadata without downloading |
| Copy | PUT (with copy source) | Copy an object within S3 |

---

## Metadata

Metadata is data about data. Every object in blob storage carries metadata alongside its binary content.

### System Metadata

Automatically set by the storage system:

- `Content-Length`: Size of the object in bytes
- `Content-Type`: MIME type (image/jpeg, video/mp4, application/pdf)
- `Last-Modified`: When the object was last updated
- `ETag`: A hash of the object content (for cache validation)

### User-Defined Metadata

Custom key-value pairs you attach to objects:

- `x-amz-meta-user-id: alice_123`
- `x-amz-meta-camera-model: iPhone 15 Pro`
- `x-amz-meta-gps-location: 37.7749,-122.4194`

### Why Metadata Matters

Metadata enables searching, filtering, and processing without downloading the actual file.

```
  Using Metadata:

  "Find all photos uploaded by alice_123 that are larger
   than 5 MB and were taken with an iPhone"

  Instead of downloading every photo to check:

  Query metadata store:
    WHERE user-id = "alice_123"
    AND content-length > 5242880
    AND camera-model LIKE "iPhone%"

  Returns matching keys without touching the actual files.
```

---

## Pre-Signed URLs

A pre-signed URL is a temporary, self-expiring link that grants access to a private object without requiring authentication. It is one of the most important patterns in blob storage.

### The Problem

Your objects are private. Only your server can access them. But you need to let users upload and download files directly without routing all traffic through your server.

### How Pre-Signed URLs Work

```
  Pre-Signed URL Flow (Download):

  1. Client requests file access
  +--------+     "I need photo_123.jpg"     +--------+
  | Client | -----------------------------> | Server |
  +--------+                                +--------+
                                                |
  2. Server generates pre-signed URL            |
     (signed with secret key, expires in 15 min)|
                                                |
  3. Server returns pre-signed URL              |
  +--------+     "https://s3.../photo_123   +--------+
  | Client | <-------- ?signature=abc&      | Server |
  +--------+            expires=1705312000" +--------+
       |
  4. Client downloads directly from S3
       |        GET (pre-signed URL)
       +-------------------------------> +-----+
                                          | S3  |
       <-------------------------------  +-----+
              (file data, 2.3 MB)

  The server never touches the file data.
  S3 verifies the signature and expiration.
```

```
  Pre-Signed URL Flow (Upload):

  1. Client asks server for upload permission
  +--------+    "I want to upload a photo"  +--------+
  | Client | -----------------------------> | Server |
  +--------+                                +--------+
                                                |
  2. Server generates pre-signed PUT URL        |
     (allows upload to specific key)            |
                                                |
  3. Server returns URL                         |
  +--------+    "PUT to this URL"           +--------+
  | Client | <----------------------------- | Server |
  +--------+                                +--------+
       |
  4. Client uploads directly to S3
       |       PUT (file data)
       +-------------------------------> +-----+
                                          | S3  |
       <-------------------------------  +-----+
              (200 OK)

  Benefits:
  - Server never handles large file uploads
  - Reduces server bandwidth and CPU
  - S3 handles upload at scale
  - URL expires, so access is temporary
```

### Security Considerations

- **Set short expiration times.** 15 minutes for uploads, 1 hour for downloads is typical.
- **Restrict to specific operations.** An upload URL should not allow downloads.
- **Include content type restrictions.** Prevent users from uploading executables when you expect images.
- **Use one-time URLs for sensitive content.** Some systems invalidate the URL after first use.

---

## CDN Integration

A Content Delivery Network (CDN) caches your blob storage content at edge locations around the world, delivering files to users from the nearest server.

### Without a CDN

```
  Without CDN:

  User in Tokyo                          S3 in US-East
  +--------+                             +--------+
  |  User  | ---- 12,000 km ----------> |   S3   |
  | Tokyo  | <--- 200ms latency ------- | Virginia|
  +--------+                             +--------+

  Every request travels across the Pacific Ocean.
  Slow. Expensive (egress bandwidth).
```

### With a CDN

```
  With CDN:

  User in Tokyo        CDN Edge in Tokyo           S3 in US-East
  +--------+           +------------+              +--------+
  |  User  | -- 5ms -> | CDN Edge   |              |   S3   |
  | Tokyo  | <-------- | (Cached!)  |              | Virginia|
  +--------+           +------------+              +--------+
                             |                          |
                        First request:                  |
                        Cache miss, fetch from S3 ----->|
                        Cache the response              |
                             |                          |
                        Subsequent requests:            |
                        Serve from cache (5ms)          |

  Benefits:
  - Latency: 200ms -> 5ms for cached content
  - Bandwidth: S3 egress reduced by 90%+
  - Scalability: CDN handles traffic spikes
  - Cost: CDN egress is cheaper than S3 egress
```

### CDN + Blob Storage Architecture

```
  Complete CDN Integration:

  +--------+                +----------+             +---------+
  | Client |   GET image    |   CDN    |  Cache miss |   S3    |
  |        | -------------> | (Edge)   | ----------> | (Origin)|
  +--------+                +----------+             +---------+
       ^                         |
       |     Cached response     |
       +-------------------------+

  Cache-Control: public, max-age=31536000
  (Cache for 1 year -- images rarely change)

  Cache Invalidation:
  When a user updates their profile photo:
  1. Upload new photo to S3 with new key (e.g., photo_v2.jpg)
  2. Update application to reference new key
  3. Old key eventually expires from CDN cache

  OR: Use versioned keys
  - avatar_abc123.jpg (hash of content in filename)
  - When content changes, hash changes, new URL, no invalidation needed
```

---

## Image Processing Pipeline

When a user uploads an image, you rarely store just the original. You need thumbnails, compressed versions, and different sizes for different devices.

```
  Image Processing Pipeline:

  +--------+                                    +---------+
  | User   |  Upload original (12 MB)           |   S3    |
  | Device | ---------------------------------> | (Raw)   |
  +--------+                                    +----+----+
                                                     |
                                              Upload event
                                                     |
                                                     v
                                              +------+------+
                                              | Image       |
                                              | Processor   |
                                              | (Lambda/    |
                                              |  Worker)    |
                                              +------+------+
                                                     |
                              +----------------------+----------------------+
                              |                      |                      |
                              v                      v                      v
                    +---------+----+       +---------+----+       +---------+----+
                    | Thumbnail    |       | Medium       |       | Full Size    |
                    | 150x150      |       | 640x640      |       | 1080x1080    |
                    | 15 KB        |       | 80 KB        |       | 250 KB       |
                    | WebP format  |       | WebP format  |       | JPEG format  |
                    +---------+----+       +---------+----+       +---------+----+
                              |                      |                      |
                              v                      v                      v
                    +---------+----+       +---------+----+       +---------+----+
                    | S3: /thumb/  |       | S3: /medium/ |       | S3: /full/   |
                    | photo_001    |       | photo_001    |       | photo_001    |
                    +--------------+       +--------------+       +--------------+
                              |                      |                      |
                              +----------+-----------+
                                         |
                                         v
                                  +------+------+
                                  |     CDN     |
                                  | (Cached at  |
                                  |  edges)     |
                                  +-------------+

  Processing steps:
  1. Validate file type (is it really an image?)
  2. Strip EXIF data (remove GPS coordinates for privacy)
  3. Resize to multiple dimensions
  4. Convert to efficient format (WebP for web, HEIC for iOS)
  5. Compress (reduce file size without visible quality loss)
  6. Store all versions in S3
  7. Update metadata database with URLs
  8. Invalidate CDN cache if replacing existing image
```

---

## Video Transcoding

Video files are much larger than images and require transcoding: converting the video into multiple formats and quality levels so it plays smoothly on any device and network speed.

### Why Transcoding Is Necessary

A raw video uploaded from a phone might be:
- 4K resolution (3840x2160)
- H.265 codec
- 150 Mbps bitrate
- 500 MB for a 30-second clip

But a user on a 3G connection with an old phone needs:
- 480p resolution
- H.264 codec (widely supported)
- 1 Mbps bitrate
- 5 MB for the same 30 seconds

Transcoding creates multiple versions so the player can switch quality based on network conditions (adaptive bitrate streaming).

```
  Video Transcoding Pipeline:

  +--------+   Upload     +---------+   Event    +-------------+
  | User   | -----------> | S3 Raw  | --------> | Transcoding |
  +--------+   (500 MB)   | Bucket  |           | Service     |
                           +---------+           +------+------+
                                                        |
                           +----------------------------+
                           |            |               |
                           v            v               v
                     +-----------+ +-----------+  +-----------+
                     | 1080p     | | 720p      |  | 480p      |
                     | H.264     | | H.264     |  | H.264     |
                     | 5 Mbps    | | 2.5 Mbps  |  | 1 Mbps    |
                     | 150 MB    | | 75 MB     |  | 30 MB     |
                     +-----------+ +-----------+  +-----------+
                           |            |               |
                           v            v               v
                     +-----------+ +-----------+  +-----------+
                     | S3 Output | | S3 Output |  | S3 Output |
                     | /1080p/   | | /720p/    |  | /480p/    |
                     +-----------+ +-----------+  +-----------+
                                    |
                                    v
                           +--------+--------+
                           | Manifest File   |
                           | (HLS/DASH)      |
                           | Lists all       |
                           | quality levels  |
                           +-----------------+
                                    |
                                    v
                              +-----+-----+
                              |    CDN    |
                              +-----------+

  Adaptive Bitrate Streaming:
  The video player checks network speed and switches quality:

  Fast WiFi:   [1080p] ████████████████████████
  Slow 4G:     [1080p] ████ [720p] █████ [480p] ████
  3G:          [480p]  ████████████████████████
```

---

## Storage Tiers

Not all data is accessed equally. A photo uploaded today gets viewed frequently. A photo from five years ago might never be viewed again. Storage tiers let you pay less for data you rarely access.

```
  Storage Tiers (S3 Example):

  +------------------------------------------------------------------+
  |  Tier          | Access     | Cost/GB  | Retrieval  | Use Case   |
  +------------------------------------------------------------------+
  |  Standard      | Frequent   | $0.023   | Instant    | Active     |
  |                |            |          |            | content    |
  +------------------------------------------------------------------+
  |  Infrequent    | Monthly    | $0.0125  | Instant    | Older      |
  |  Access (IA)   |            |          | (+ fee)    | content    |
  +------------------------------------------------------------------+
  |  Glacier       | Rare       | $0.004   | Minutes    | Archives   |
  |  Instant       |            |          |            |            |
  +------------------------------------------------------------------+
  |  Glacier       | Very rare  | $0.0036  | Hours      | Compliance |
  |  Flexible      |            |          | (3-5 hrs)  |            |
  +------------------------------------------------------------------+
  |  Glacier       | Almost     | $0.00099 | 12 hours   | Legal      |
  |  Deep Archive  | never      |          |            | retention  |
  +------------------------------------------------------------------+

  Cost savings: Standard vs Deep Archive = 23x cheaper!
```

### Lifecycle Policies

You can automate moving data between tiers based on age.

```
  Lifecycle Policy Example:

  Day 0-30:     STANDARD         (frequently accessed)
      |
      | After 30 days
      v
  Day 30-90:    INFREQUENT ACCESS (accessed sometimes)
      |
      | After 90 days
      v
  Day 90-365:   GLACIER INSTANT   (rarely accessed)
      |
      | After 1 year
      v
  Day 365+:     DEEP ARCHIVE      (compliance retention)
      |
      | After 7 years
      v
  DELETE                           (retention period over)

  You set this policy once. S3 automatically moves
  objects between tiers. No code needed.
```

---

## Instagram Upload Flow: Putting It All Together

Let us trace what happens when a user uploads a photo to Instagram, from tap to feed.

```
  Instagram Photo Upload Flow:

  Step 1: Upload Request
  +----------+    POST /upload    +------------+
  |  Mobile  | ----------------> |  API       |
  |  App     |                   |  Gateway   |
  +----------+                   +-----+------+
                                       |
  Step 2: Get Pre-Signed URL           |
  +----------+  Pre-signed URL   +-----+------+
  |  Mobile  | <---------------- |  Upload    |
  |  App     |                   |  Service   |
  +----------+                   +-----+------+
       |                               |
  Step 3: Direct Upload to S3          |
       |    PUT (12 MB photo)          |
       +------------------------> +----+----+
                                  | S3 Raw  |
                                  | Bucket  |
                                  +----+----+
                                       |
  Step 4: Event Trigger                |
                                       v
                                 +-----+------+
                                 | Event:     |
                                 | PhotoUploaded
                                 +-----+------+
                                       |
         +-----------------------------+-----------------------------+
         |                             |                             |
         v                             v                             v
  +------+------+              +-------+------+              +------+------+
  | Image       |              | Content      |              | Metadata    |
  | Processor   |              | Moderation   |              | Extractor   |
  | - Resize    |              | - NSFW check |              | - EXIF data |
  | - Compress  |              | - Violence   |              | - GPS strip |
  | - Thumbnail |              | - Copyright  |              | - Tags      |
  +------+------+              +-------+------+              +------+------+
         |                             |                             |
         v                             v                             v
  +------+------+              +-------+------+              +------+------+
  | S3 Processed|              | Approved?    |              | Database    |
  | Bucket      |              | Yes/No       |              | (PostgreSQL)|
  | /thumb/     |              +--------------+              +--------------+
  | /medium/    |
  | /full/      |
  +------+------+
         |
  Step 5: CDN Distribution
         v
  +------+------+
  |     CDN     |
  | Edge servers|
  | worldwide   |
  +------+------+
         |
  Step 6: Feed Update
         v
  +------+------+     +------+------+
  | Feed        |     | Notification|
  | Service     |     | Service     |
  | (Fan-out to |     | (Push to    |
  |  followers) |     |  followers) |
  +-------------+     +-------------+

  Timeline:
  t=0s:    User taps "Share"
  t=0.5s:  Pre-signed URL received
  t=3s:    Photo uploaded to S3
  t=5s:    Image processing complete
  t=5.5s:  Content moderation approved
  t=6s:    Photo appears in user's profile
  t=6-30s: Photo appears in followers' feeds
```

### Key Design Decisions in the Instagram Flow

1. **Pre-signed URLs** keep the upload service stateless. It never touches the file data.
2. **Event-driven processing** allows parallel execution of image processing, content moderation, and metadata extraction.
3. **Multiple image sizes** are generated once and cached forever, saving compute on every view.
4. **CDN caching** means popular photos are served from edge locations, not from S3.
5. **Content moderation** runs asynchronously. The photo is not visible until approved.

---

## Trade-offs

| Decision | Option A | Option B |
|---|---|---|
| Storage type | Object storage (scalable, HTTP, cheap) | File storage (low latency, hierarchical, POSIX) |
| Upload method | Through your server (control, small files) | Pre-signed URL (scalable, large files) |
| Image processing | Synchronous on upload (slower upload, instant access) | Async via event (fast upload, brief delay) |
| Image format | JPEG (universal, larger) | WebP (smaller, newer browser support) |
| CDN strategy | Pull-based (CDN fetches from origin on miss) | Push-based (pre-populate CDN edges) |
| Storage tier | Keep everything in Standard (fast, expensive) | Lifecycle policy (cheaper, retrieval delay for old data) |
| Video | Store original only (save storage) | Transcode to multiple qualities (better user experience) |

---

## Common Mistakes

1. **Routing file uploads through your application server.** A 100 MB video upload ties up a server thread for minutes. Use pre-signed URLs to let clients upload directly to blob storage.

2. **Not generating multiple image sizes.** Serving a 12 MB original photo to a mobile device displaying a 150-pixel thumbnail wastes bandwidth and slows the app. Generate thumbnails and medium-size versions on upload.

3. **Using the same S3 key pattern for all files.** Keys like `/photos/1.jpg`, `/photos/2.jpg` concentrate requests on the same S3 partition. Use random prefixes or hashed keys to distribute load: `/a3f2/photos/1.jpg`.

4. **Forgetting to set Cache-Control headers.** Without proper cache headers, CDN edges re-fetch from S3 on every request, negating the benefit of having a CDN.

5. **Not using lifecycle policies.** Storing years of backup data in Standard tier wastes money. Move old data to cheaper tiers automatically.

6. **Ignoring content moderation.** Allowing unmoderated uploads exposes your platform to legal risk. Always scan uploads before making them publicly visible.

---

## Best Practices

1. **Use pre-signed URLs for all uploads and private downloads.** This keeps your servers stateless and offloads bandwidth to the storage provider.

2. **Generate multiple sizes and formats on upload.** Create thumbnails, medium, and full-size versions. Convert to WebP for web delivery. This is a one-time compute cost that saves bandwidth on every view.

3. **Use content-addressable keys.** Name objects by their content hash: `sha256(content).jpg`. This provides automatic deduplication and makes cache invalidation trivial (new content = new key = new URL).

4. **Set aggressive Cache-Control headers for immutable content.** Images and videos rarely change. Cache them for a year: `Cache-Control: public, max-age=31536000, immutable`.

5. **Configure lifecycle policies from day one.** Define rules for moving data to cheaper tiers as it ages. This saves significant cost at scale.

6. **Separate raw uploads from processed files.** Use different buckets for raw uploads and processed files. This makes it easy to reprocess if you change your image pipeline.

7. **Monitor storage costs.** Track storage usage by bucket, tier, and age. Set alerts for unexpected growth.

8. **Enable versioning for critical data.** S3 versioning keeps previous versions of objects, protecting against accidental overwrites and deletes.

---

## Quick Summary

Blob storage stores unstructured binary data -- photos, videos, documents, backups -- as objects identified by unique keys within buckets. Object storage differs from block and file storage in that it scales to petabytes, uses HTTP APIs, and trades random access for durability and simplicity. S3-like systems replicate data across multiple availability zones for eleven-nines durability. Metadata attached to objects enables searching and filtering without downloading file contents. Pre-signed URLs allow clients to upload and download directly from blob storage, keeping your servers stateless. CDN integration caches content at edge locations worldwide, reducing latency from hundreds of milliseconds to single digits. Image processing pipelines generate multiple sizes and formats on upload. Video transcoding creates multiple quality levels for adaptive bitrate streaming. Storage tiers let you save money by automatically moving less-accessed data to cheaper storage classes.

---

## Key Points

- Blob storage stores unstructured data as objects with keys, metadata, and binary content
- Object storage scales to petabytes but does not support partial updates -- you replace the entire object
- S3 achieves eleven-nines durability by replicating across availability zones
- Pre-signed URLs let clients upload and download directly from blob storage, bypassing your servers
- CDN integration caches content at edge locations, reducing latency dramatically
- Image processing pipelines create multiple sizes and formats on upload to save bandwidth on every view
- Video transcoding produces multiple quality levels for adaptive bitrate streaming
- Storage tiers save money by moving less-accessed data to cheaper classes automatically

---

## Practice Questions

1. You are designing a system where users upload profile photos. Each photo is 5 MB. You have 100 million users and 10% update their photo each month. How much storage do you need? Should you keep old versions? What storage tiers would you use?

2. A user in Tokyo uploads a photo that a user in New York wants to view 5 seconds later. Trace the request path from upload to view, including S3, CDN, and any processing. What is the expected latency for the viewer?

3. Your image processing pipeline crashes after resizing an image but before generating the thumbnail. The user refreshes the page and sees a broken image. How would you design the system to handle partial processing failures?

4. You are building a video streaming platform. A creator uploads a 2 GB video. It needs to be available in 1080p, 720p, and 480p. How would you design the transcoding pipeline? How long should the creator wait before the video is available?

5. Your S3 bill jumped from $10,000 to $50,000 this month. What are the most likely causes? How would you investigate and reduce costs?

---

## Exercises

**Exercise 1: Design a Document Storage System**

Design a blob storage architecture for a company document management system. Users upload Word documents, PDFs, and spreadsheets. Requirements: version history, full-text search of document contents, role-based access control, and audit logging. Draw the architecture showing upload flow, storage, indexing, and retrieval.

**Exercise 2: Build a CDN Strategy**

You run a photo-sharing platform with 50 million daily active users. 80% of photo views happen within the first 24 hours of upload. 15% happen in the first week. 5% happen after one week. Design a CDN and storage strategy that minimizes cost while keeping the experience fast. Include cache warming, TTL policies, and storage tier transitions.

**Exercise 3: Image Processing at Scale**

Your e-commerce platform has 10 million product images. A new business requirement asks you to add watermarks to all images and convert them from JPEG to WebP format. Design a batch processing pipeline that can reprocess all 10 million images within 24 hours. Calculate the compute resources needed assuming each image takes 2 seconds to process.

---

## What Is Next?

You now understand how to store, process, and deliver large files at scale. But what happens when a user wants to find something specific among millions of items? Typing "blue running shoes size 10" and getting relevant results in under 100 milliseconds requires a completely different kind of system. In the next chapter, you will learn about search systems: how inverted indexes work, how Elasticsearch powers full-text search, and how to build search architectures that handle millions of queries per second.
