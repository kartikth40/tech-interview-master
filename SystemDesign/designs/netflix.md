# Netflix System Design
> **Interview Ready** | 45-minute format

## Problem Statement

Design a subscription-based video streaming platform like Netflix that:
- Streams videos to millions of concurrent users
- Provides personalized recommendations
- Supports offline downloads
- Adaptive bitrate streaming
- Multi-profile support per account

**Key Differences from YouTube:**
- No user uploads (curated content library)
- Subscription-based (not ad-supported)
- Strong ML-based recommendations
- Download for offline viewing

---

## 1️⃣ Requirements Clarification

### Functional Requirements:

1. **Content Delivery**
   - Stream videos (movies, TV shows, documentaries)
   - Adaptive bitrate streaming (SD, HD, 4K)
   - Resume playback from last position
   - Offline downloads

2. **Personalization**
   - Personalized recommendations
   - Continue watching row
   - User profiles (up to 5 per account)

3. **Search & Browse**
   - Search by title, genre, actor
   - Browse categories
   - Trending/Top 10

4. **Subscription**
   - Multiple plans (Mobile, Basic, Standard, Premium)
   - Payment processing

### Non-Functional Requirements:
- **Scale:** 250M subscribers, 100M concurrent viewers (peak)
- **Availability:** 99.99% uptime
- **Latency:** <2 sec to start playback
- **Storage:** Petabytes of video content
- **Bandwidth:** Terabits per second (CDN-heavy)

### Out of Scope:
- Live streaming
- User-generated content
- Social features

---

## 2️⃣ Capacity Estimation

```
Subscribers: 250M
Concurrent viewers (peak): 100M
Average video duration: 45 minutes

Streaming:
- 100M concurrent × 5 Mbps (HD) = 500,000 Gbps = 500 Tbps
- CDN serves 98%+ of this traffic

Storage:
- Content library: 10,000 titles
- Each title: Original (100 GB) + Transcoded (4 resolutions) = 150 GB
- Total: 10,000 × 150 GB = 1.5 PB
- With replication (3x): 4.5 PB

Recommendations:
- 250M users × 10 recommendations/day = 2.5B recommendations/day
- 2.5B / 86400 = 29K recommendations/sec

Offline Downloads:
- 20% users download content
- 50M users × 2 movies/month × 2 GB = 100M downloads × 2 GB = 200 PB/month bandwidth
```

---

## 3️⃣ API Design

```text
# 1. Get Home Page (Personalized)
GET /v1/browse/home
  ?user_id=user_123&profile_id=profile_456

Response: {
  rows: [
    {
      title: "Trending Now",
      videos: [
        {
          id: "video_123",
          title: "Stranger Things S4",
          thumbnail: "https://cdn.netflix.com/thumbnails/123.jpg",
          duration: 3600,
          match_score: 95  # Personalized match percentage
        }
      ]
    },
    {
      title: "Continue Watching",
      videos: [...]
    },
    {
      title: "Top 10 in India",
      videos: [...]
    }
  ]
}

# 2. Stream Video (HLS)
GET /v1/videos/{video_id}/stream
  ?quality=1080p&profile_id=profile_456

Response: (302 Redirect to CDN)
Location: https://cdn.netflix.com/videos/123/1080p/master.m3u8

# 3. Get Recommendations
GET /v1/recommendations
  ?user_id=user_123&profile_id=profile_456&limit=20

Response: {
  recommendations: [
    {
      video_id: "video_789",
      title: "The Crown",
      match_score: 92,
      reason: "Because you watched 'Stranger Things'"
    }
  ]
}

# 4. Download for Offline
POST /v1/downloads
Body: {
  video_id: "video_123",
  profile_id: "profile_456",
  quality: "720p"
}

Response: {
  download_id: "dl_abc123",
  download_url: "https://cdn.netflix.com/downloads/123.encrypted",
  license_url: "https://api.netflix.com/licenses/xyz",
  expires_at: "2024-02-15T12:00:00Z"  # 30 days
}

# 5. Update Watch Progress
POST /v1/videos/{video_id}/progress
Body: {
  profile_id: "profile_456",
  position: 1800,  # seconds
  duration: 3600
}

Response: {
  video_id: "video_123",
  position: 1800,
  percentage: 50
}
```

---

## 4️⃣ Database Design

### Cassandra (Watch History, Recommendations - Time-series)

```sql
-- Watch history
CREATE TABLE watch_history (
  profile_id TEXT,
  timestamp TIMESTAMP,
  video_id TEXT,
  position INT,
  duration INT,
  PRIMARY KEY (profile_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- User recommendations (pre-computed)
CREATE TABLE recommendations (
  profile_id TEXT,
  recommendation_id TIMEUUID,
  video_id TEXT,
  score DOUBLE,
  reason TEXT,
  created_at TIMESTAMP,
  PRIMARY KEY (profile_id, recommendation_id)
) WITH CLUSTERING ORDER BY (recommendation_id DESC);
```

### PostgreSQL (Users, Subscriptions, Content Metadata)

```sql
-- Users
CREATE TABLE users (
  id VARCHAR(50) PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  subscription_plan VARCHAR(20),  -- mobile, basic, standard, premium
  subscription_status VARCHAR(20),  -- active, canceled, expired
  created_at TIMESTAMP
);

-- Profiles (5 per user)
CREATE TABLE profiles (
  id VARCHAR(50) PRIMARY KEY,
  user_id VARCHAR(50) REFERENCES users(id),
  name VARCHAR(100),
  is_kids BOOLEAN DEFAULT false,
  created_at TIMESTAMP
);

-- Videos (Content Catalog)
CREATE TABLE videos (
  id VARCHAR(50) PRIMARY KEY,
  title VARCHAR(255),
  description TEXT,
  genres TEXT[],  -- ['Drama', 'Thriller']
  release_year INT,
  duration INT,  -- seconds
  rating VARCHAR(10),  -- PG-13, R, TV-MA
  created_at TIMESTAMP
);

CREATE INDEX idx_videos_genres ON videos USING GIN (genres);
```

### Redis (Caching, Session)

```text
# Video metadata cache
Key: video:{video_id}:metadata
Value: JSON { title, genres, duration, ... }
TTL: 24 hours

# Continue watching position
Key: profile:{profile_id}:video:{video_id}:position
Value: 1800  # seconds
TTL: 30 days

# Recommendation cache
Key: profile:{profile_id}:recommendations
Value: JSON [{ video_id, score, reason }, ...]
TTL: 6 hours
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
│      CDN (98% of traffic)            │
│  - Video streaming                   │
│  - 1000+ edge locations              │
└──────┬───────────────────────────────┘
       │ (2% cache miss)
       ▼
┌──────────────────────────────────────┐
│   Load Balancer                      │
└──────┬───────────────────────────────┘
       │
   ┌───┴────┬──────────┬────────────┐
   ▼        ▼          ▼            ▼
┌──────┐ ┌────────┐ ┌────────┐ ┌──────┐
│Video │ │ Reco   │ │ User   │ │Search│
│Service│ │Engine │ │Service │ │Service│
└──┬───┘ └───┬────┘ └───┬────┘ └──┬───┘
   │         │          │         │
   │         │          │         │
   ▼         ▼          ▼         ▼
┌──────────────────────────────────────┐
│         Data Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌─────┐│
│  │Cassandra │  │PostgreSQL│  │Redis││
│  │(History) │  │  (Users) │  │Cache││
│  └──────────┘  └──────────┘  └─────┘│
└──────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│   ML Recommendation Engine           │
│  - Collaborative filtering           │
│  - Content-based filtering           │
│  - Hybrid model                      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   AWS S3 (Video Storage)             │
│  - Original content                  │
│  - Transcoded (4 resolutions)        │
└──────────────────────────────────────┘
```

---

## 6️⃣ Low-Level Design

### Class Diagram

```
┌─────────────────────┐
│  VideoService       │
├─────────────────────┤
│ + streamVideo()     │
│ + getMetadata()     │
└──────┬──────────────┘
       │ uses
       ▼
┌─────────────────────┐
│ RecommendationEngine│
├─────────────────────┤
│ + getRecommendations()│
│ + updateModel()     │
└─────────────────────┘
```

---

## 7️⃣ Deep Dives

### Deep Dive 1: Recommendation Engine

**Challenge:** Personalize recommendations for 250M users

**Solution: Hybrid Recommendation System**

```text
FUNCTION getRecommendations(profileId, limit = 20):
    # 1. Check cache
    cached = get "profile:{profileId}:recommendations" from Redis
    IF cached exists:
        RETURN parsed cached value

    # 2. Collaborative filtering (users who watched similar videos)
    collaborativeRecos = collaborativeFiltering(profileId)

    # 3. Content-based filtering (similar genres, actors, directors)
    contentRecos = contentBasedFiltering(profileId)

    # 4. Trending/Popular (for cold start problem)
    trendingRecos = getTrending()

    # 5. Merge with weights
    mergedRecos = mergeRecommendations([
        { recs: collaborativeRecos, weight: 0.5 },
        { recs: contentRecos,       weight: 0.3 },
        { recs: trendingRecos,      weight: 0.2 }
    ])

    # 6. Diversity filter (avoid recommending all similar content)
    diverseRecos = diversityFilter(mergedRecos)

    # 7. Cache for 6 hours
    set "profile:{profileId}:recommendations" = serialized diverseRecos
        in Redis with TTL 21600 seconds

    RETURN first `limit` items of diverseRecos
END FUNCTION

FUNCTION collaborativeFiltering(profileId):
    # Find users with similar watch history
    watchHistory = getWatchHistory(profileId)

    # Use Matrix Factorization (SVD) or ALS
    # Pre-trained model stored in Redis/ML model server
    similarUsers = mlModel.findSimilarUsers(profileId)

    # Get videos watched by similar users but not by this user
    recommendations = empty list
    FOR EACH user IN similarUsers:
        theirVideos = getWatchHistory(user.id)

        FOR EACH video IN theirVideos:
            IF watchHistory does NOT contain video.id:
                append to recommendations:
                    video_id: video.id,
                    score:    user.similarity * video.rating,
                    reason:   "Because users like you enjoyed this"

    SORT recommendations by score descending
    RETURN recommendations
END FUNCTION

FUNCTION mergeRecommendations(sources):
    merged = empty map keyed by video_id

    FOR EACH { recs, weight } IN sources:
        FOR EACH rec IN recs:
            existing = merged[rec.video_id] OR { score: 0 }
            merged[rec.video_id] = rec with
                score = existing.score + (rec.score * weight)

    result = all values of merged
    SORT result by score descending
    RETURN result
END FUNCTION
```

**Trade-offs:**
- ✅ Personalized (high user engagement)
- ✅ Diverse content discovery
- ❌ Computationally expensive (mitigated by caching)
- ❌ Cold start problem for new users (use trending as fallback)

---

### Deep Dive 2: Offline Downloads (DRM)

**Challenge:** Allow downloads while preventing piracy

**Solution: Encrypted Downloads with DRM**

```text
FUNCTION initiateDownload(videoId, profileId, quality):
    # 1. Check subscription plan (Premium only for downloads)
    user = getUserForProfile(profileId)

    IF user.subscription_plan is NOT one of ["standard", "premium"]:
        RAISE error "Downloads require Standard or Premium plan"

    # 2. Generate encrypted download URL
    encryptedFile = "{videoId}_{quality}_encrypted.mp4"
    downloadUrl = generate S3 presigned URL (bucket = "netflix-downloads",
                                             key    = encryptedFile,
                                             expires in 3600 seconds)  # 1 hour to start download

    # 3. Generate DRM license (Widevine/FairPlay)
    license = drmService.generateLicense(
        video_id:   videoId,
        profile_id: profileId,
        expires_at: current time + 30 days
    )

    # 4. Store download record
    query database "INSERT INTO downloads (profile_id, video_id, license_id, expires_at)
                    VALUES (profileId, videoId, license.id, license.expires_at)"

    RETURN {
        download_url: downloadUrl,
        license_url:  "https://api.netflix.com/licenses/{license.id}",
        expires_at:   license.expires_at
    }
END FUNCTION
```

**DRM Technologies:**
- **Widevine** (Android, Chrome)
- **FairPlay** (iOS, Safari)
- **PlayReady** (Windows)

**Trade-offs:**
- ✅ Prevents piracy
- ✅ Offline viewing for users
- ❌ Complex implementation
- ❌ Device limitations (frustrates users)

---

### Deep Dive 3: Open Connect (Netflix CDN)

**Challenge:** Serve 500 Tbps to 100M concurrent viewers globally

**Solution: Custom CDN inside ISP networks**

```
Netflix Open Connect Architecture:

1. Netflix places CDN servers (Open Connect Appliances) 
   inside ISP data centers

2. ISPs get benefits:
   - Reduced bandwidth costs (traffic stays within ISP)
   - Better user experience (lower latency)

3. Netflix benefits:
   - 95%+ traffic served from within ISP (<10ms latency)
   - Lower CDN costs
   - Better control over streaming quality

Flow:
User → ISP → Open Connect Appliance → Stream video
(All within ISP network, no internet transit!)

Fallback:
If content not in OCA → Route to nearest Netflix CDN → S3 origin
```

**Predictive Caching:**
```text
FUNCTION predictAndCache():
    # Predict what users will watch tonight (ML model)
    predictions = mlModel.predictPopularContent(
        region: "India",
        time:   "19:00-23:00",   # Prime time
        day:    "Friday"
    )

    # Pre-cache to Open Connect during off-peak hours (2 AM - 6 AM)
    FOR EACH video IN predictions.top100:
        IF NOT ocaHasVideo(video.id):
            cacheVideoToOCA(video.id, region = "India")
END FUNCTION
```

**Trade-offs:**
- ✅ Extremely low latency (<10ms)
- ✅ Reduces transit costs by 90%
- ✅ ISPs love it (saves them bandwidth)
- ❌ Hardware cost (Netflix provides servers to ISPs)
- ❌ Complex deployment (need agreements with 1000+ ISPs)

---

## 8️⃣ Bottlenecks & Optimizations

### Bottlenecks:

1. **Streaming bandwidth** → Open Connect CDN (98% traffic from ISP)
2. **Recommendation latency** → Pre-compute daily, cache 6 hours
3. **Cold start (new users)** → Trending/popular content

### Optimizations:

**1. Per-Title Encoding:**
```
Different content needs different bitrates
Action scenes: Higher bitrate (lots of motion)
Dialogue scenes: Lower bitrate (static)

Netflix uses ML to determine optimal bitrate per scene
Result: 20% bandwidth savings
```

**2. Download Scheduling:**
```
Schedule downloads during off-peak (2 AM - 6 AM)
Offer "Download while charging" option
Reduces peak load
```

**3. Personalized Thumbnails:**
```
Show different thumbnails to different users
Use A/B testing (Multi-Armed Bandit)
Increases click-through rate by 20%
```

---

## 9️⃣ Interview Tips

### What to Focus on (45-min):

1. **Clarify requirements** (5 min)
   - Subscription vs ads?
   - Offline downloads?
   - Recommendations?

2. **High-level design** (10 min)
   - CDN-heavy (98% traffic)
   - ML recommendation engine
   - Cassandra + PostgreSQL

3. **Deep dive 1: Recommendations** (10 min)
   - Collaborative + content-based
   - Hybrid model with caching

4. **Deep dive 2: Open Connect CDN** (10 min)
   - Custom CDN inside ISPs
   - Predictive caching

5. **Deep dive 3: DRM downloads** (5 min)
   - Widevine/FairPlay
   - License expiration

6. **Optimizations** (5 min)
   - Per-title encoding
   - A/B testing thumbnails

### Common Follow-ups:

**Q: Netflix vs YouTube differences?**
A: 
- Netflix: Curated content, subscription, ML recommendations, DRM downloads
- YouTube: User uploads, ads, simpler recommendations, no DRM

**Q: How to prevent password sharing?**
A: Device tracking, location monitoring, limit concurrent streams

**Q: How to handle regional content (India-only shows)?**
A: Geo-fencing, content licensing tables, different catalogs per region

**Q: How to optimize for mobile (India)?**
A: Mobile-only plan (SD quality), lower starting bitrate, download for offline

---

## Summary

**Key Decisions:**
1. ✅ **Open Connect CDN** (95% traffic from within ISP)
2. ✅ **Hybrid ML recommendations** (collaborative + content-based)
3. ✅ **DRM for downloads** (Widevine/FairPlay)
4. ✅ **Per-title encoding** (optimize bitrate per content)
5. ✅ **A/B testing** (personalized thumbnails)

**Tech Stack:**
- Backend: Java (Spring Boot)
- ML: Python (TensorFlow), Spark for training
- Database: Cassandra (history), PostgreSQL (users), Redis (cache)
- Storage: AWS S3
- CDN: Open Connect (custom) + CloudFront
- Encoding: FFmpeg with per-title optimization
