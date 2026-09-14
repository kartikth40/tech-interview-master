# Instagram System Design
> **Interview Ready** | 45-minute format

## Problem Statement

Design a photo-sharing social media platform like Instagram that allows:
- Upload and share photos
- Follow users
- News feed (timeline)
- Like and comment on photos
- Search users

**Key Requirements:**
- 1B users, 300M daily active users
- 100M photos uploaded daily
- Read-heavy (read:write = 100:1)
- Low latency feed generation (<500ms)

---

## 1️⃣ Requirements Clarification

### Functional Requirements:

1. **Photo Sharing**
   - Upload photo with caption
   - Apply filters (optional)
   - Delete photo

2. **Feed**
   - News feed (photos from followed users)
   - User profile (user's photos)

3. **Social Features**
   - Follow/unfollow users
   - Like photo
   - Comment on photo

4. **Search**
   - Search users by username

### Non-Functional Requirements:
- **Scale:** 300M DAU, 100M photos/day
- **Availability:** 99.99% uptime
- **Latency:** <500ms for feed, <200ms for photo upload (async processing)
- **Storage:** Petabytes of photos
- **Read-heavy:** 100:1 ratio (browsing vs uploading)

### Out of Scope:
- Stories
- Reels (short videos)
- Direct messaging
- Instagram Shopping

---

## 2️⃣ Capacity Estimation

```
Users: 1B total, 300M daily active users (DAU)

Photo Uploads:
- 100M photos/day
- 100M / 86400 = 1,160 photos/sec
- Peak: 1,160 × 3 = 3,500 photos/sec

Feed Reads:
- Each user checks feed 10 times/day
- 300M × 10 = 3B feed requests/day
- 3B / 86400 = 34,700 feeds/sec
- Peak: 34,700 × 3 = 104,000 feeds/sec

Storage:
- Original photo: 2 MB avg
- Thumbnails (3 sizes): 200 KB total
- Total per photo: 2.2 MB
- Daily: 100M × 2.2 MB = 220 TB/day
- Yearly: 220 TB × 365 = 80 PB/year

Bandwidth:
- Feed: Each feed has 20 photos × 200 KB (thumbnail) = 4 MB
- 104K feeds/sec × 4 MB = 416 GB/sec (peak)
- Use CDN to serve 95%+ of this traffic
```

---

## 3️⃣ API Design

```text
# 1. Upload Photo
POST /v1/photos
Body: (multipart/form-data)
  photo: <file>
  caption: "Beautiful sunset! 🌅"
  location: "Goa, India"

Response: {
  photo_id: "abc123",
  status: "processing",  # processing → ready
  upload_url: "https://s3.amazonaws.com/presigned-url"
}

# 2. Get Photo
GET /v1/photos/{photo_id}

Response: {
  photo_id: "abc123",
  user: { id: "user_123", username: "john_doe", profile_pic: "..." },
  image_url: "https://cdn.instagram.com/photos/abc123.jpg",
  thumbnail_url: "https://cdn.instagram.com/photos/abc123_thumb.jpg",
  caption: "Beautiful sunset! 🌅",
  location: "Goa, India",
  likes: 5000,
  comments_count: 120,
  created_at: "2024-01-15T12:00:00Z"
}

# 3. Get News Feed
GET /v1/feed
  ?user_id=user_123&page=1&limit=20

Response: {
  photos: [
    {
      photo_id: "abc123",
      user: { username: "john_doe", ... },
      image_url: "...",
      caption: "...",
      likes: 5000,
      created_at: "2024-01-15T12:00:00Z"
    }
  ],
  next_page: 2
}

# 4. Follow User
POST /v1/users/{user_id}/follow
Body: { follower_id: "user_456" }

Response: {
  user_id: "user_789",
  follower_id: "user_456",
  followed_at: "2024-01-15T12:00:00Z"
}

# 5. Like Photo
POST /v1/photos/{photo_id}/like
Body: { user_id: "user_456" }

Response: {
  photo_id: "abc123",
  total_likes: 5001,
  user_liked: true
}

# 6. Comment on Photo
POST /v1/photos/{photo_id}/comments
Body: {
  user_id: "user_456",
  text: "Amazing photo!"
}

Response: {
  comment_id: "comment_xyz",
  photo_id: "abc123",
  user: { username: "sarah_smith", ... },
  text: "Amazing photo!",
  created_at: "2024-01-15T12:05:00Z"
}
```

---

## 4️⃣ Database Design

### PostgreSQL (Users, Relationships)

```sql
-- Users
CREATE TABLE users (
  id VARCHAR(50) PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  email VARCHAR(255) UNIQUE,
  full_name VARCHAR(255),
  bio TEXT,
  profile_pic_url TEXT,
  followers_count BIGINT DEFAULT 0,
  following_count BIGINT DEFAULT 0,
  created_at TIMESTAMP
);

-- Followers (Graph relationship)
CREATE TABLE followers (
  follower_id VARCHAR(50) REFERENCES users(id),
  followee_id VARCHAR(50) REFERENCES users(id),
  created_at TIMESTAMP,
  PRIMARY KEY (follower_id, followee_id)
);

CREATE INDEX idx_followers_followee ON followers(followee_id);
```

### Cassandra (Photos, Comments - Time-series)

```sql
-- Photos (partitioned by user for fast profile queries)
CREATE TABLE photos (
  user_id TEXT,
  photo_id TIMEUUID,
  image_url TEXT,
  thumbnail_url TEXT,
  caption TEXT,
  location TEXT,
  likes COUNTER,
  comments_count COUNTER,
  created_at TIMESTAMP,
  PRIMARY KEY (user_id, photo_id)
) WITH CLUSTERING ORDER BY (photo_id DESC);

-- Feed (pre-computed timeline for each user)
CREATE TABLE user_feed (
  user_id TEXT,
  photo_id TIMEUUID,
  author_id TEXT,
  created_at TIMESTAMP,
  PRIMARY KEY (user_id, photo_id)
) WITH CLUSTERING ORDER BY (photo_id DESC);

-- Comments
CREATE TABLE comments (
  photo_id TEXT,
  comment_id TIMEUUID,
  user_id TEXT,
  text TEXT,
  created_at TIMESTAMP,
  PRIMARY KEY (photo_id, comment_id)
) WITH CLUSTERING ORDER BY (comment_id DESC);
```

### Redis (Caching)

```text
# Feed cache (recent 100 photos)
Key: feed:{user_id}
Type: List
Value: [photo_id1, photo_id2, ...]
TTL: 30 minutes

# Photo metadata cache
Key: photo:{photo_id}
Value: JSON { user, image_url, caption, likes, ... }
TTL: 1 hour

# Like count
Key: photo:{photo_id}:likes
Type: Counter
Value: 5000
TTL: None
```

### Object Storage (S3)

```
Bucket: instagram-photos
Structure:
  /photos/{user_id}/{photo_id}/original.jpg
  /photos/{user_id}/{photo_id}/large.jpg    (1080×1080)
  /photos/{user_id}/{photo_id}/medium.jpg   (640×640)
  /photos/{user_id}/{photo_id}/thumb.jpg    (320×320)
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
│      CDN (CloudFront)                │
│  - Serve photos (95% traffic)        │
└──────┬───────────────────────────────┘
       │ (Cache miss)
       ▼
┌──────────────────────────────────────┐
│   Load Balancer (NGINX)              │
└──────┬───────────────────────────────┘
       │
   ┌───┴────┬──────────┬────────────┐
   ▼        ▼          ▼            ▼
┌──────┐ ┌────────┐ ┌────────┐ ┌──────┐
│Upload│ │ Feed   │ │ Social │ │Search│
│Service│ │Service │ │Service │ │Service│
└──┬───┘ └───┬────┘ └───┬────┘ └──┬───┘
   │         │          │         │
   │         │          │         │
   ▼         ▼          ▼         ▼
┌──────────────────────────────────────┐
│         Data Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌─────┐│
│  │Cassandra │  │PostgreSQL│  │Redis││
│  │ (Photos) │  │ (Users)  │  │Cache││
│  └──────────┘  └──────────┘  └─────┘│
└──────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│   Image Processing Service           │
│   - Resize (3 sizes)                 │
│   - Compress                         │
│   - Apply filters                    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   AWS S3 + CloudFront                │
│   - Store photos                     │
│   - Serve via CDN                    │
└──────────────────────────────────────┘
```

**Data Flow (Upload Photo):**
1. User uploads photo → Upload Service
2. Upload Service generates presigned S3 URL → User uploads directly to S3
3. S3 triggers event → Image Processing Service
4. Image Processing creates 3 sizes (large, medium, thumb)
5. Saves to S3 + updates metadata in Cassandra
6. Fanout Service pushes photo to followers' feeds

**Data Flow (View Feed):**
1. User requests feed → Feed Service
2. Check Redis cache (pre-computed feed)
3. If cache hit → Return photos from cache
4. If cache miss → Fetch from Cassandra → Cache in Redis

---

## 6️⃣ Low-Level Design

### Class Diagram

```
┌─────────────────┐
│  PhotoService   │
├─────────────────┤
│ + uploadPhoto() │
│ + getPhoto()    │
└────┬────────────┘
     │ uses
     ▼
┌─────────────────┐
│ FanoutService   │
├─────────────────┤
│ + fanoutPhoto() │
└─────────────────┘
```

### Sequence Diagram (Upload & Fanout)

```
User  UploadService  S3  ImageProcessor  Cassandra  FanoutService
 │         │          │         │            │           │
 │─Upload─>│          │         │            │           │
 │         │──────────────────>│         │            │           │
 │         │  Presigned URL    │         │            │           │
 │<────────│          │         │            │           │
 │         │          │         │            │           │
 │─────────────────>│         │            │           │
 │  Upload photo    │         │            │           │
 │         │          │         │            │           │
 │         │          │─Resize─>│            │           │
 │         │          │         │            │           │
 │         │          │<────────│            │           │
 │         │          │ (3 sizes)            │           │
 │         │          │         │            │           │
 │         │          │         │─Store─────>│           │
 │         │          │         │            │           │
 │         │          │         │─Fanout────────────────>│
 │         │          │         │            │  (push to│
 │         │          │         │            │ followers)│
```

---

## 7️⃣ Deep Dives

### Deep Dive 1: Feed Generation (Fanout)

**Challenge:** When user posts photo, push to millions of followers' feeds

**Solution: Hybrid Push-Pull (same as Twitter)**

```text
FUNCTION fanoutPhoto(photo):
    user = getUser(photo.user_id)

    # 1. Regular users (<10K followers) → Push to all followers
    IF user.followers_count < 10000:
        pushFanout(photo)
    # 2. Celebrities (>10K followers) → Pull at read time
    ELSE:
        pullFanout(photo)
END FUNCTION

FUNCTION pushFanout(photo):
    # Get user's followers
    followers = getFollowers(photo.user_id)

    # Push to each follower's feed (Redis + Cassandra)
    FOR EACH followerId IN followers:
        # Redis (fast)
        list-prepend photo.id to "feed:{followerId}"
        trim "feed:{followerId}" to keep only indices 0..999   # Keep last 1000

        # Cassandra (durable)
        execute Cassandra "INSERT INTO user_feed (user_id, photo_id, author_id, created_at)
                           VALUES (followerId, photo.id, photo.user_id, current time)"
END FUNCTION

FUNCTION pullFanout(photo):
    # Just store photo, no fanout
    # Fetched at read time and merged with regular feed
END FUNCTION

# Feed generation (read time)
FUNCTION getFeed(userId, limit = 20):
    # 1. Get pre-computed feed (regular users)
    cachedFeed = get range 0..limit from list "feed:{userId}"

    # 2. Get celebrity follows
    celebrityFollows = getCelebrityFollows(userId)

    # 3. Fetch recent photos from celebrities, in parallel
    celebrityPhotos = FOR EACH celebId IN celebrityFollows (in parallel):
        execute Cassandra "SELECT * FROM photos WHERE user_id = celebId
                           ORDER BY photo_id DESC LIMIT 20"

    # 4. Merge and sort by timestamp (newest first)
    allPhotos = cachedFeed combined with flattened celebrityPhotos
    SORT allPhotos by created_at descending

    RETURN first `limit` items of allPhotos
END FUNCTION
```

**Trade-offs:**
- ✅ Fast reads for most users (pre-computed)
- ✅ Fast writes for celebrities (no fanout)
- ❌ Slightly slower reads for users following many celebrities

---

### Deep Dive 2: Image Processing & CDN

**Challenge:** Resize 3,500 photos/sec and serve to 300M users

**Solution: Async Processing + CDN**

```text
FUNCTION processPhoto(s3Event):
    bucketName = s3Event.bucketName
    key        = s3Event.key   # photos/{user_id}/{photo_id}/original.jpg

    # 1. Download original from S3
    originalImage = get object from S3 (bucket = bucketName, key = key)

    # 2. Resize to 3 sizes (in parallel)
    sizes = [
        { name: "large",  width: 1080, height: 1080 },
        { name: "medium", width: 640,  height: 640  },
        { name: "thumb",  width: 320,  height: 320  }
    ]

    FOR EACH size IN sizes (in parallel):
        # Resize the image, cover-fit, JPEG quality 85
        resized = resize originalImage to (size.width x size.height), fit = cover,
                  encode as JPEG quality 85

        # Upload to S3
        resizedKey = key with "original.jpg" replaced by "{size.name}.jpg"
        upload to S3:
            bucket        = bucketName
            key           = resizedKey
            body          = resized
            contentType   = "image/jpeg"
            cacheControl  = "public, max-age=31536000"   # 1 year

    # 3. Update photo status in Cassandra
    photoId = extractPhotoId(key)
    execute Cassandra "UPDATE photos SET status = 'ready' WHERE photo_id = photoId"
END FUNCTION
```

**CDN Configuration:**
```text
# CloudFront distribution
{
  origins: [
    {
      id:         "s3-instagram-photos",
      domainName: "instagram-photos.s3.amazonaws.com",
      path:       "/photos"
    }
  ],
  cacheBehaviors: {
    pathPattern:    "/photos/*",
    targetOriginId: "s3-instagram-photos",
    ttl:            31536000,   # 1 year (images never change)
    compress:       true
  }
}
```

**Benefits:**
- ✅ S3 → CloudFront → Edge locations worldwide (<50ms latency)
- ✅ 95%+ traffic served from CDN (reduces S3 costs)
- ✅ Async processing (doesn't block user)

---

### Deep Dive 3: Sharding Strategy

**Challenge:** 1B users, 100B photos → Single database can't handle

**Solution: Shard by User ID**

```text
# Cassandra already handles sharding automatically via partition key

# Photos table: partitioned by user_id
# - All photos for a user are on same node
# - Fast profile queries: SELECT * FROM photos WHERE user_id = ?
# - Distribution: Hash(user_id) MOD num_nodes

# Feed table: partitioned by user_id
# - Each user's feed on one node
# - Fast feed queries: SELECT * FROM user_feed WHERE user_id = ?

# Example with 100 Cassandra nodes:
# - User 'user_123' → Hash('user_123') MOD 100 = Node 23
# - All photos and feed for 'user_123' on Node 23
```

**Why shard by user_id (not photo_id)?**
- ✅ Profile queries are fast (all user's photos on one node)
- ✅ Feed queries are fast (user's feed on one node)
- ❌ Hot users (celebrities) may create hot spots (mitigate: use consistent hashing)

---

## 8️⃣ Bottlenecks & Optimizations

### Bottlenecks:

1. **Feed generation (celebrities)** → Hybrid push-pull fanout
2. **Image serving** → CDN (CloudFront)
3. **Database hot spots** → Cassandra sharding + replication

### Optimizations:

**1. Lazy Loading:**
```
Load 20 photos initially
Load more on scroll (infinite scroll)
```

**2. Image Compression:**
```
Use modern formats (WebP, AVIF) for 30% size reduction
Serve via <picture> with fallback to JPEG
```

**3. Prefetching:**
```
Prefetch next page of feed in background
```

**4. Video Optimization (for Reels):**
```
HLS/DASH adaptive streaming
Multiple resolutions (480p, 720p, 1080p)
```

---

## 9️⃣ Interview Tips

### What to Focus on (45-min):

1. **Clarify requirements** (5 min)
   - Photos only or videos too?
   - Scale (300M DAU)

2. **High-level design** (10 min)
   - S3 for storage
   - CDN for serving
   - Cassandra for photos/feed
   - PostgreSQL for users

3. **Deep dive 1: Fanout** (10 min)
   - Hybrid push-pull

4. **Deep dive 2: Image processing** (10 min)
   - Resize to 3 sizes
   - Async processing

5. **Deep dive 3: Sharding** (5 min)
   - Shard by user_id

6. **Discuss CDN** (5 min)
   - 95% traffic from CDN

### Common Follow-ups:

**Q: How do you handle photo filters?**
A: Apply filters client-side (Instagram SDK), upload already filtered photo

**Q: How do you recommend photos (Explore page)?**
A: ML model - user's liked photos, hashtags, location, connections

**Q: How do you handle inappropriate content?**
A: ML image classification, user reporting, human moderation queue

**Q: How do you rank feed (not chronological)?**
A: ML ranking - user engagement, recency, author relationship, photo quality

**Q: How do you handle Stories (24-hour expiration)?**
A: Separate table with TTL, Redis for real-time, auto-delete after 24h

---

## Summary

**Key Decisions:**
1. ✅ **Hybrid fanout** (push for regular, pull for celebrities)
2. ✅ **S3 + CloudFront CDN** (95% traffic from CDN)
3. ✅ **Async image processing** (resize to 3 sizes)
4. ✅ **Cassandra sharding** (partition by user_id)

**Tech Stack:**
- Backend: Java/Python
- Database: Cassandra (photos/feed), PostgreSQL (users), Redis (cache)
- Storage: AWS S3
- CDN: CloudFront
- Image Processing: Sharp library
- Queue: Kafka
