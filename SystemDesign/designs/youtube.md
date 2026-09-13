# YouTube System Design
> **SDE-2 Interview Ready** | 45-minute format

## 🎯 Problem Statement

Design a video streaming platform like YouTube that allows:
- Upload videos
- Stream videos to millions of users
- Search videos
- Like, comment, subscribe
- Recommendations

**Key Requirements:**
- 2B users, 500M daily active users
- 500 hours of video uploaded every minute
- 1B hours of video watched daily
- Low latency video streaming (<2 seconds to start playback)

---

## 1️⃣ Requirements Clarification

### Functional Requirements:

1. **Upload Videos**
   - Upload video files (MP4, AVI, etc.)
   - Add title, description, tags
   - Thumbnail generation

2. **Stream Videos**
   - Multiple resolutions (360p, 720p, 1080p, 4K)
   - Adaptive bitrate streaming
   - Resume playback from last position

3. **Search Videos**
   - Search by title, tags, channel

4. **Engagement**
   - Like/dislike video
   - Comment on videos
   - Subscribe to channels

5. **Recommendations**
   - Personalized video recommendations

### Non-Functional Requirements:
- **Scale:** 500M DAU, 500 hours uploaded/min, 1B hours watched/day
- **Availability:** 99.9% uptime
- **Latency:** <2 sec to start playback
- **Storage:** Petabytes of video storage
- **Bandwidth:** High bandwidth for streaming

### Out of Scope:
- Live streaming
- YouTube Premium features
- Monetization (ads)

---

## 2️⃣ Capacity Estimation

```
Users: 2B total, 500M daily active users (DAU)

Video Uploads:
- 500 hours uploaded per minute
- 500 hours × 60 min = 30,000 hours/day
- Average video duration: 10 minutes
- Videos uploaded/day: 30,000 hours × 60 / 10 = 180,000 videos/day

Video Streaming:
- 1B hours watched/day
- Concurrent viewers (peak): 1B hours / 24 hours = 41M viewers
- Videos per second: 41M viewers / 600 sec avg video = 69K video starts/sec

Storage:
- Original video: 10 min × 50 MB/min = 500 MB per video
- Transcoded (360p, 720p, 1080p, 4K): 500 MB × 4 = 2 GB per video
- Daily: 180K videos × 2 GB = 360 TB/day
- Yearly: 360 TB × 365 = 131 PB/year

Bandwidth:
- 41M concurrent viewers
- Average bitrate (720p): 5 Mbps
- Total: 41M × 5 Mbps = 205,000 Gbps = 205 Tbps
- Use CDN to distribute load (95%+ traffic served from CDN edge)
```

---

## 3️⃣ API Design

### Core APIs

```text
# 1. Upload Video
POST /v1/videos/upload
Body: (multipart/form-data)
  video: <file>
  title: "How to design YouTube"
  description: "System design tutorial"
  tags: ["system design", "youtube"]

Response: {
  video_id: "abc123",
  status: "processing",  # processing → ready
  upload_url: "https://s3.amazonaws.com/presigned-url"
}

# 2. Get Video Metadata
GET /v1/videos/{video_id}

Response: {
  video_id: "abc123",
  title: "How to design YouTube",
  description: "...",
  views: 1500000,
  likes: 50000,
  channel: {
    id: "channel_xyz",
    name: "Tech Channel",
    subscribers: 500000
  },
  thumbnail_url: "https://cdn.youtube.com/thumbnails/abc123.jpg",
  duration: 600,  # seconds
  resolutions: ["360p", "720p", "1080p"],
  status: "ready"
}

# 3. Stream Video (HLS/DASH)
GET /v1/videos/{video_id}/stream
  ?resolution=720p

Response: (302 Redirect to CDN)
Location: https://cdn.youtube.com/videos/abc123/720p/playlist.m3u8

# HLS Playlist (playlist.m3u8)
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment0.ts
#EXTINF:10.0,
segment1.ts
...

# 4. Search Videos
GET /v1/search
  ?query=system+design
  &page=1&limit=20

Response: {
  results: [
    {
      video_id: "abc123",
      title: "How to design YouTube",
      thumbnail_url: "...",
      views: 1500000,
      channel: "Tech Channel",
      duration: 600
    }
  ],
  total: 5000,
  page: 1
}

# 5. Like Video
POST /v1/videos/{video_id}/like
Body: { user_id: "user_123" }

Response: {
  video_id: "abc123",
  total_likes: 50001,
  user_liked: true
}

# 6. Get Recommendations
GET /v1/recommendations
  ?user_id=user_123&limit=20

Response: {
  videos: [
    {
      video_id: "def456",
      title: "Advanced System Design",
      thumbnail_url: "...",
      views: 800000
    }
  ]
}
```

---

## 4️⃣ Database Design

### PostgreSQL (Metadata)

```sql
-- Videos
CREATE TABLE videos (
  id VARCHAR(50) PRIMARY KEY,
  user_id VARCHAR(50) REFERENCES users(id),
  title VARCHAR(255),
  description TEXT,
  duration INT,  -- seconds
  status VARCHAR(20),  -- processing, ready, failed
  views BIGINT DEFAULT 0,
  likes BIGINT DEFAULT 0,
  created_at TIMESTAMP
);

CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_created_at ON videos(created_at DESC);

-- Users (Channels)
CREATE TABLE users (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  subscribers BIGINT DEFAULT 0,
  created_at TIMESTAMP
);

-- Comments
CREATE TABLE comments (
  id VARCHAR(50) PRIMARY KEY,
  video_id VARCHAR(50) REFERENCES videos(id),
  user_id VARCHAR(50) REFERENCES users(id),
  text TEXT,
  likes INT DEFAULT 0,
  created_at TIMESTAMP
);

CREATE INDEX idx_comments_video_id ON comments(video_id);
```

### Cassandra (Time-series Data - Views, Likes)

```sql
-- Video views (for analytics)
CREATE TABLE video_views (
  video_id TEXT,
  timestamp TIMESTAMP,
  user_id TEXT,
  watch_duration INT,  -- seconds
  PRIMARY KEY (video_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

### Redis (Caching, Counters)

```text
# Video metadata cache
Key: video:{video_id}:metadata
Value: JSON { title, views, likes, ... }
TTL: 1 hour

# View count (real-time)
Key: video:{video_id}:views
Type: Counter
Value: 1500000

# Like count
Key: video:{video_id}:likes
Type: Counter
Value: 50000

# Trending videos
Key: trending:videos:daily
Type: Sorted Set (score = views in last 24h)
Value: [(video_id, score), ...]
```

### Elasticsearch (Search)

```json
{
  "mappings": {
    "properties": {
      "video_id": { "type": "keyword" },
      "title": { "type": "text" },
      "description": { "type": "text" },
      "tags": { "type": "keyword" },
      "channel": { "type": "text" },
      "views": { "type": "long" },
      "created_at": { "type": "date" }
    }
  }
}
```

### Object Storage (S3/GCS)

```
Bucket: youtube-videos
Structure:
  /videos/{video_id}/original.mp4
  /videos/{video_id}/360p/segment0.ts
  /videos/{video_id}/360p/segment1.ts
  /videos/{video_id}/720p/segment0.ts
  /videos/{video_id}/1080p/segment0.ts
  /thumbnails/{video_id}.jpg
```

---

## 5️⃣ High-Level Design

```
┌──────────────┐
│    Users     │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│      CDN (CloudFront/Akamai)         │
│  - 95% of video streaming traffic    │
│  - Edge locations worldwide          │
└──────┬───────────────────────────────┘
       │ (5% cache miss)
       ▼
┌──────────────────────────────────────┐
│   Load Balancer (NGINX)              │
└──────┬───────────────────────────────┘
       │
   ┌───┴────┬──────────┬────────────┐
   ▼        ▼          ▼            ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
│ Upload │ │Stream│ │ Search │ │Engagement│
│Service │ │Service│ │Service │ │ Service  │
└───┬────┘ └──┬───┘ └───┬────┘ └────┬─────┘
    │         │         │           │
    │         │         │           │
    ▼         ▼         ▼           ▼
┌──────────────────────────────────────────┐
│         Data Layer                       │
│  ┌──────────┐  ┌───────────┐  ┌────────┐│
│  │PostgreSQL│  │Elasticsearch│ │ Redis  ││
│  │(Metadata)│  │  (Search)   │ │(Cache) ││
│  └──────────┘  └───────────┘  └────────┘│
└──────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────┐
│   Transcoding Service (FFmpeg)           │
│   - Convert to multiple resolutions     │
│   - Generate HLS/DASH segments           │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│   Object Storage (S3/GCS)                │
│   - Original videos                      │
│   - Transcoded videos (360p-4K)          │
│   - Thumbnails                           │
└──────────────────────────────────────────┘
```

**Data Flow (Video Upload):**
1. User uploads video → Upload Service
2. Upload Service generates presigned S3 URL → User uploads directly to S3
3. S3 triggers event → Transcoding Service
4. Transcoding Service transcodes to multiple resolutions (360p, 720p, 1080p, 4K)
5. Saves segments to S3 + updates metadata in PostgreSQL
6. Elasticsearch indexes video for search

**Data Flow (Video Streaming):**
1. User requests video → Stream Service
2. Stream Service redirects to CDN URL
3. CDN serves video (HLS playlist + segments)
4. If CDN cache miss → Fetch from S3 origin

---

## 6️⃣ Low-Level Design

### Class Diagram

```
┌────────────────────────┐
│   UploadService        │
├────────────────────────┤
│ + generatePresignedURL()│
│ + createVideoMetadata()│
└──────┬─────────────────┘
       │ triggers
       ▼
┌────────────────────────┐
│  TranscodingService    │
├────────────────────────┤
│ + transcodeVideo()     │
│ + generateThumbnail()  │
│ + createHLSSegments()  │
└────────────────────────┘
```

### Sequence Diagram (Upload & Transcode)

```
User  UploadService  S3  TranscodingService  PostgreSQL  Elasticsearch
 │        │          │         │                 │            │
 │─Upload─>│         │         │                 │            │
 │        │          │         │                 │            │
 │        │─Presigned URL────>│         │                 │            │
 │<───────│          │         │                 │            │
 │        │          │         │                 │            │
 │─────────────────>│         │                 │            │
 │  Upload video    │         │                 │            │
 │        │          │         │                 │            │
 │        │          │─Event──>│                 │            │
 │        │          │  (video uploaded)         │            │
 │        │          │         │                 │            │
 │        │          │         │─Transcode──────────────────────────>│
 │        │          │<────────│  (360p, 720p, 1080p)        │
 │        │          │         │                 │            │
 │        │          │         │─Update metadata─>│           │
 │        │          │         │                 │            │
 │        │          │         │─Index────────────────────────>│
```

### State Machine (Video Status)

```
┌────────────┐
│  UPLOADED  │ (Original video uploaded to S3)
└─────┬──────┘
      │
      ▼
┌─────────────┐
│ PROCESSING  │ (Transcoding in progress)
└──────┬──────┘
       │
   ┌───┴────┐
   ▼        ▼
┌──────┐  ┌────────┐
│READY │  │ FAILED │
└──────┘  └────────┘
```

### Design Patterns

1. **Pub/Sub Pattern** - S3 event triggers transcoding
2. **CDN Pattern** - Cache video segments at edge locations
3. **Adaptive Streaming** - HLS/DASH for quality adjustment

---

## 7️⃣ Deep Dives

### Deep Dive 1: Video Transcoding Pipeline

**Challenge:** Transcode 180K videos/day to multiple resolutions within minutes

**Solution: Distributed Transcoding with Queue**

```text
# S3 Event → SNS → SQS → Transcoding Workers

FUNCTION processVideo(videoId):
    # 1. Download original video from S3
    originalVideo = get object from S3 (bucket = "youtube-videos",
                                        key = "videos/{videoId}/original.mp4")

    # 2. Transcode to multiple resolutions (in parallel)
    resolutions = ["360p", "720p", "1080p", "4k"]

    FOR EACH resolution IN resolutions (in parallel):
        # Transcode using FFmpeg
        segments = transcodeToHLS(originalVideo, resolution)

        # Upload segments to S3
        FOR EACH segment IN segments:
            upload to S3 (bucket = "youtube-videos",
                          key    = "videos/{videoId}/{resolution}/{segment.name}",
                          body   = segment.data)

        # Create HLS playlist
        playlist = createHLSPlaylist(segments)
        upload to S3 (bucket = "youtube-videos",
                      key    = "videos/{videoId}/{resolution}/playlist.m3u8",
                      body   = playlist)

    # 3. Generate thumbnail (from frame at 2 seconds)
    thumbnail = generateThumbnail(originalVideo, at 2 seconds)
    upload to S3 (bucket = "youtube-videos",
                  key    = "thumbnails/{videoId}.jpg",
                  body   = thumbnail)

    # 4. Update video status in DB
    query database "UPDATE videos SET status = 'ready' WHERE id = videoId"

    # 5. Index in Elasticsearch
    index into Elasticsearch index "videos" with id = videoId, document = {
        video_id:    videoId,
        title:       video.title,
        description: video.description,
        created_at:  video.created_at
    }
END FUNCTION

FUNCTION transcodeToHLS(video, resolution):
    # Use FFmpeg to create HLS segments (10 seconds each)
    command = "ffmpeg -i {video}
                 -vf scale={getResolutionSize(resolution)}
                 -c:v h264 -crf 23
                 -hls_time 10
                 -hls_list_size 0
                 -hls_segment_filename segment%03d.ts
                 playlist.m3u8"

    # Execute FFmpeg (returns list of segments)
    RETURN executeFFmpeg(command)
END FUNCTION
```

**Scaling:**
- Use AWS Elastic Transcoder or custom EC2 fleet
- Each worker handles 1 video at a time
- 180K videos/day, 1 hour per video = 7,500 concurrent workers needed
- Use spot instances (70% cost savings)

**Trade-offs:**
- ✅ Parallel transcoding (faster)
- ✅ Cost-effective with spot instances
- ❌ Transcoding expensive (CPU/GPU intensive)
- ❌ Takes time (30 min - 2 hours depending on video length)

---

### Deep Dive 2: Adaptive Bitrate Streaming (HLS/DASH)

**Challenge:** Deliver smooth video playback across varying network speeds

**Solution: HTTP Live Streaming (HLS)**

**How it works:**
```
1. Server creates multiple renditions of video (360p, 720p, 1080p)
2. Each rendition split into 10-second segments
3. Client downloads master playlist (lists all resolutions)
4. Client starts with low resolution (360p)
5. Client monitors network speed
6. If network fast → Download higher resolution segments
7. If network slow → Download lower resolution segments
```

**Master playlist** - a small manifest listing each rendition and its bandwidth/resolution; the
client picks one and fetches that rendition's segment playlist:
```
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360    -> 360p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720  -> 720p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080 -> 1080p/playlist.m3u8
```

**Client adaptation logic (the key idea):** start at the lowest rendition, measure the download
speed of each ~10s segment (`bandwidth ≈ segment_bytes × 8 / download_time`), and switch to the
highest rendition whose required bandwidth fits within ~80% of measured bandwidth (headroom to
avoid oscillation). This is all client-side; the server just hosts static segments + playlists.

**Trade-offs:**
- ✅ Smooth playback (no buffering)
- ✅ Adapts to network conditions
- ❌ Frequent resolution changes can be jarring
- ❌ Higher storage (multiple versions of same video)

---

### Deep Dive 3: View Count at Scale

**Challenge:** Update view counts for 41M concurrent viewers without overloading database

**Solution: Redis Counters + Periodic Batch Updates**

```text
FUNCTION recordView(videoId, userId):
    # 1. Increment counter in Redis (fast)
    atomic increment of "video:{videoId}:views"

    # 2. Add to Kafka stream (for analytics)
    send to Kafka topic "video_views":
        key   = videoId
        value = {
            video_id:  videoId,
            user_id:   userId,
            timestamp: current time
        }

    # Note: Don't update PostgreSQL immediately (too slow)
END FUNCTION

# Background job (runs every 5 minutes)
FUNCTION syncViewCounts():
    # 1. Get all video IDs with updated views
    videoKeys = all Redis keys matching "video:*:views"

    # 2. Batch update PostgreSQL
    FOR EACH key IN videoKeys:
        videoId    = second segment of key (split on ':')
        redisCount = get value at key

        query database "UPDATE videos SET views = views + redisCount WHERE id = videoId"

        # Reset Redis counter
        delete key from Redis
END FUNCTION
```

**Trade-offs:**
- ✅ Fast writes (Redis is in-memory)
- ✅ No database hotspots
- ❌ View counts in PostgreSQL are 5 minutes stale (acceptable)
- ❌ Risk of losing counts if Redis fails (mitigated by Kafka stream)

---

## 8️⃣ Bottlenecks & Optimizations

### Bottlenecks:

1. **Transcoding Cost & Time**
   - Problem: 180K videos/day × $0.02/minute = $36K/day
   - Solution: Only transcode popular videos to 4K, use machine learning to predict viral videos

2. **Storage Cost**
   - Problem: 131 PB/year × $0.023/GB/month = $30M/month
   - Solution: Archive old/unpopular videos to Glacier ($0.004/GB), delete after 10 years

3. **Bandwidth Cost**
   - Problem: 205 Tbps × CDN costs
   - Solution: Peer-to-peer CDN (WebRTC), aggressive caching

4. **Database Hot Videos**
   - Problem: Popular videos get millions of reads
   - Solution: Cache heavily in Redis + CDN, use read replicas

### Optimizations:

**1. Lazy Transcoding:**
```
Don't transcode all resolutions immediately
Transcode 360p first (ready in 5 min)
Transcode other resolutions on-demand if video gets views
```

**2. Intelligent Caching:**
```
Cache trending videos closer to users (CDN edge)
Use LRU eviction for non-trending
```

**3. Resume Playback:**
```
Store last watched position in Redis
Key: user:{user_id}:video:{video_id}:position
Value: timestamp (seconds)
```

---

## 9️⃣ Interview Tips

### What to Focus on (45-min):

1. **Clarify requirements** (5 min)
   - Scale? Upload vs streaming ratio?

2. **High-level design** (15 min)
   - CDN for streaming (most important)
   - S3 for storage
   - Transcoding service
   - PostgreSQL for metadata

3. **Deep dive 1: Transcoding** (10 min)
   - FFmpeg, multiple resolutions
   - Queue-based processing (SQS)
   - Scaling with workers

4. **Deep dive 2: Adaptive streaming (HLS)** (10 min)
   - Explain HLS concept
   - Client switches quality based on bandwidth

5. **Discuss view counts** (5 min)
   - Redis counters + batch updates

### Common Follow-ups:

**Q: How do you handle duplicate video detection?**
A: Generate perceptual hash of video frames, compare with existing videos

**Q: How do you recommend videos?**
A: Collaborative filtering (users who watched video A also watched B), content-based (similar tags)

**Q: How do you prevent copyright violations?**
A: Content ID system - fingerprint videos, match against database of copyrighted content

**Q: How do you optimize for mobile (low bandwidth in India)?**
A: Start with 144p/240p, aggressive compression, allow download for offline viewing

---

## Summary

**Key Design Decisions:**
1. ✅ **CDN** for 95%+ video delivery (CloudFront/Akamai)
2. ✅ **S3/GCS** for video storage
3. ✅ **HLS/DASH** for adaptive bitrate streaming
4. ✅ **Distributed transcoding** (SQS + EC2 workers)
5. ✅ **Redis** for view counters

**Tech Stack:**
- Backend: Java/Go (Spring Boot)
- Storage: AWS S3/GCS
- CDN: CloudFront/Akamai
- Database: PostgreSQL (metadata), Cassandra (analytics)
- Cache: Redis
- Search: Elasticsearch
- Queue: SQS/Kafka
- Transcoding: FFmpeg (AWS Elastic Transcoder)
