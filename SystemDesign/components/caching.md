# Caching (Component Deep Dive)

## What is Caching?

Caching stores frequently accessed data in a fast storage layer to reduce latency and load on backend systems.

**Benefits:**
- ⚡ **Faster response times** (RAM access ~1ms vs DB query ~100ms)
- 💰 **Cost reduction** (fewer DB reads, less compute)
- 📈 **Scalability** (handle more traffic with same backend)
- 🛡️ **Reliability** (serve cached data if backend fails)

---

## Cache Hierarchy

```
L1: Browser Cache (1-5ms)
    ↓
L2: CDN Cache (10-50ms)
    ↓
L3: Application Cache / Redis (1-10ms)
    ↓
L4: Database Query Cache (10-50ms)
    ↓
Database (100-500ms)
```

---

## Caching Strategies

### 1. **Cache-Aside (Lazy Loading)** ⭐ Most Common

```text
FUNCTION getUser(userId)
    # 1. Check cache first
    cached = CACHE_GET("user:" + userId)
    IF cached EXISTS THEN
        RETURN deserialize(cached)
    END IF

    # 2. Cache miss - fetch from database
    user = DB_QUERY("SELECT * FROM users WHERE id = ?", userId)

    # 3. Update cache for next time (TTL = 1 hour)
    CACHE_SET("user:" + userId, serialize(user), TTL = 3600)

    RETURN user
END FUNCTION
```

**Pros:**
- ✅ Only requested data is cached (efficient memory usage)
- ✅ Resilient to cache failures (app still works)
- ✅ Simple to implement

**Cons:**
- ❌ Cache miss penalty (first request is slow)
- ❌ Stale data possible if not invalidated properly
- ❌ Each cache miss = 3 round trips (check cache, query DB, update cache)

**Use Cases:**
- Read-heavy workloads
- User profiles, product catalogs
- Data that doesn't change frequently

---

### 2. **Write-Through Cache**

```text
FUNCTION updateUser(userId, data)
    # 1. Write to database
    DB_QUERY("UPDATE users SET name = ? WHERE id = ?", data.name, userId)

    # 2. Immediately update cache
    CACHE_SET("user:" + userId, serialize(data), TTL = 3600)

    RETURN data
END FUNCTION
```

**Pros:**
- ✅ Cache always consistent with database
- ✅ No cache miss for recently written data
- ✅ Data durability (written to DB immediately)

**Cons:**
- ❌ Slower writes (wait for both DB + cache)
- ❌ Cache may store data that's never read (wasted memory)
- ❌ Write latency increases

**Use Cases:**
- Applications requiring strong consistency
- Read-after-write patterns
- Banking, financial transactions

---

### 3. **Write-Behind (Write-Back) Cache**

```text
FUNCTION updateUser(userId, data)
    # 1. Write to cache immediately (fast)
    CACHE_SET("user:" + userId, serialize(data), TTL = 3600)

    # 2. Asynchronously write to database (background job)
    QUEUE_ENQUEUE("writeUserToDB", { userId, data })

    RETURN data
END FUNCTION

# Background worker
FUNCTION writeUserToDB(job)
    userId = job.userId
    data = job.data
    DB_QUERY("UPDATE users SET name = ? WHERE id = ?", data.name, userId)
END FUNCTION
```

**Pros:**
- ✅ Very fast writes (only cache write is synchronous)
- ✅ Batch writes to DB (better throughput)
- ✅ Reduces database load significantly

**Cons:**
- ❌ Risk of data loss if cache crashes before DB write
- ❌ Complex implementation (need reliable queue)
- ❌ Eventual consistency

**Use Cases:**
- High write throughput systems
- Gaming leaderboards, analytics dashboards
- When eventual consistency is acceptable

---

### 4. **Refresh-Ahead (Proactive)**

```text
# Set cache with TTL
CACHE_SET("user:" + userId, serialize(user), TTL = 3600)

# Before expiration, refresh cache (runs periodically every minute)
EVERY 60 seconds DO
    ttl = CACHE_GET_TTL("user:" + userId)

    IF ttl < 300 THEN   # Refresh if < 5 minutes remaining
        freshUser = DB_QUERY("SELECT * FROM users WHERE id = ?", userId)
        CACHE_SET("user:" + userId, serialize(freshUser), TTL = 3600)
    END IF
END EVERY
```

**Pros:**
- ✅ Minimizes cache miss penalty
- ✅ Predictable response times
- ✅ Good for frequently accessed data

**Cons:**
- ❌ Difficult to predict which data to refresh
- ❌ Wasted refreshes if data not accessed
- ❌ Increased complexity

**Use Cases:**
- Homepage content, trending products
- Data accessed predictably (daily reports)
- Real-time dashboards

---

## Cache Eviction Policies

### 1. **LRU (Least Recently Used)** ⭐ Most Common

Evict the entry that was accessed longest ago. Implemented with a hash map + doubly linked list
(or an ordered map) for O(1) get/put - see the worked implementation in
[DSA/data-structures/design/lru_cache.py](../../DSA/data-structures/design/lru_cache.py).

**Pros:** Evicts truly unused data  
**Cons:** Doesn't account for access frequency  
**Use:** General-purpose caching

---

### 2. **LFU (Least Frequently Used)**

Evict the entry with the lowest access count (track a frequency counter per key; O(1) with a
frequency-bucket structure).

**Pros:** Keeps "hot" data in cache  
**Cons:** Old popular items are hard to evict (frequency doesn't decay)  
**Use:** Recommendation systems, analytics

---

### 3. **FIFO (First In First Out)**

**Pros:** Simple to implement  
**Cons:** May evict frequently used data  
**Use:** Simple caching needs

---

### 4. **TTL (Time To Live)**

```text
CACHE_SET("session:abc123", sessionData, TTL = 900)   # 15 minutes

# Auto-expires after TTL (the cache removes the key when TTL elapses)
AFTER 900 seconds DO
    CACHE_DELETE("session:abc123")
END AFTER
```

**Pros:** Automatic expiration, prevents stale data  
**Cons:** Arbitrary expiration time  
**Use:** Session storage, temporary data

---

## TTL Best Practices

```text
# Different TTLs for different data types
TTLs = {
    userProfile:    3600,    # 1 hour
    productCatalog: 600,     # 10 minutes
    homePageData:   60,      # 1 minute
    sessionData:    1800,    # 30 minutes
    apiResponse:    300      # 5 minutes
}

# Dynamic TTL based on data freshness
FUNCTION calculateTTL(data)
    IF data.changesOften THEN RETURN 60      # 1 minute
    IF data.changesDaily THEN RETURN 86400   # 24 hours
    RETURN 3600                              # Default 1 hour
END FUNCTION
```

---

## Cache Invalidation

> "There are only two hard things in Computer Science: cache invalidation and naming things." - Phil Karlton

### 1. **TTL-Based (Passive)**
```text
# Automatically expires
CACHE_SET("key", value, TTL = 3600)
```

### 2. **Event-Based (Active)**
```text
# On data update
FUNCTION updateUser(userId, data)
    DB_UPDATE("users", userId, data)

    # Invalidate cache
    CACHE_DELETE("user:" + userId)

    # Or update cache immediately (write-through)
    CACHE_SET("user:" + userId, serialize(data), TTL = 3600)
END FUNCTION
```

### 3. **Tag-Based Invalidation**
```text
# Tag cache entries
CACHE_SET("user:123", userData)
SET_ADD("tags:user:123", "user:123")
SET_ADD("tags:team:5", "user:123")   # User belongs to team 5

# Invalidate all cache entries for team 5
FUNCTION invalidateTeam(teamId)
    keys = SET_MEMBERS("tags:team:" + teamId)
    CACHE_DELETE(keys)   # delete all matching keys
END FUNCTION
```

---

## Cache Stampede (Thundering Herd)

### **Problem:**
```
Cache expires → 1000 concurrent requests → All miss cache → All query DB → DB overloaded
```

### **Solution 1: Lock-Based**
```text
locked = new Set()

FUNCTION getUser(userId)
    cached = CACHE_GET("user:" + userId)
    IF cached EXISTS THEN RETURN deserialize(cached)

    # Only first request fetches from DB
    IF locked.contains(userId) THEN
        SLEEP(100 ms)          # Wait for first request to populate cache
        RETURN getUser(userId) # Retry
    END IF

    locked.add(userId)
    TRY
        user = DB_QUERY("SELECT * FROM users WHERE id = ?", userId)
        CACHE_SET("user:" + userId, serialize(user), TTL = 3600)
        RETURN user
    FINALLY
        locked.remove(userId)
    END TRY
END FUNCTION
```

### **Solution 2: Probabilistic Early Expiration**
```text
FUNCTION getUser(userId)
    cached = CACHE_GET("user:" + userId)
    ttl = CACHE_GET_TTL("user:" + userId)

    # Randomly refresh before expiration
    shouldRefresh = (ttl < 300) AND (RANDOM() < 0.1)

    IF cached EXISTS AND NOT shouldRefresh THEN
        RETURN deserialize(cached)
    END IF

    # Refresh cache
    user = DB_QUERY("SELECT * FROM users WHERE id = ?", userId)
    CACHE_SET("user:" + userId, serialize(user), TTL = 3600)
    RETURN user
END FUNCTION
```

---

## Hot Key Problem

### **Problem:**
One key (e.g., celebrity user profile) gets 1M req/sec → Single cache server overloaded

### **Solutions:**

#### 1. **Local Caching**
```text
# Cache hot data in application memory
local_cache = empty map

FUNCTION getUser(userId)
    # Check local cache first (fastest)
    IF localCache.contains(userId) THEN
        RETURN localCache.get(userId)
    END IF

    # Check distributed cache
    cached = CACHE_GET("user:" + userId)
    IF cached EXISTS THEN
        user = deserialize(cached)
        localCache.put(userId, user)   # Store locally
        RETURN user
    END IF

    # Fetch from DB
    user = DB_QUERY("SELECT * FROM users WHERE id = ?", userId)
    CACHE_SET("user:" + userId, serialize(user), TTL = 3600)
    localCache.put(userId, user)
    RETURN user
END FUNCTION
```

#### 2. **Replication**
```
Hot key replicated across multiple cache servers:
user:celebrity → user:celebrity:1, user:celebrity:2, user:celebrity:3

Randomly select replica:
replica = random integer in [1, 3]
key = "user:celebrity:" + replica
```

---

## Cache Efficiency Metrics

Track hits and misses; **hit rate = hits / (hits + misses)**. Target >80%.

**Key Metrics:**
- **Hit Rate**: Hits / (Hits + Misses) - Target: >80%
- **Miss Rate**: Misses / (Hits + Misses) - Lower is better
- **Eviction Rate**: How often cache is full and evicts data
- **Memory Usage**: Current usage vs capacity
- **Latency**: P50, P95, P99 response times

---

## Distributed Caching

### **Single Server Cache (Simple)**
```
App Server 1 ──→ Redis
App Server 2 ──→ Redis
App Server 3 ──→ Redis
```

### **Cache Cluster (Scalable)** ⭐
```
App Servers ──→ Hash(key) % num_servers
                  ↓
               Server 1 (keys A-H)
               Server 2 (keys I-P)
               Server 3 (keys Q-Z)
```

### **Consistent Hashing** ⭐ (Handles server addition/removal)

Map both nodes and keys onto a hash ring; a key belongs to the first node clockwise. Adding or
removing a node only remaps ~1/N of keys (vs `hash(key) % N`, which remaps almost everything).
Use **virtual nodes** (e.g. 150 per physical node) for even distribution. Lookup is O(log N) via
binary search over the sorted ring. See the worked pseudocode in
[designs/distributed-cache.md](../designs/distributed-cache.md).

---

## CDN (Content Delivery Network)

```
User in US → US CDN Edge → Origin Server (California)
User in EU → EU CDN Edge → Origin Server (California)
User in Asia → Asia CDN Edge → Origin Server (California)

Benefits:
✅ Reduced latency (serve from nearest edge)
✅ Reduced bandwidth costs (offload origin)
✅ Better availability (distributed)
✅ DDoS protection
```

**CDN Best Practices:**
```text
# Set cache headers for static assets
SET_RESPONSE_HEADER("Cache-Control", "public, max-age=31536000, immutable")

# Versioned URLs for cache busting
# reference the asset as: /js/app.v123.js

# When app.js changes, deploy as app.v124.js
# Browser fetches new version, old version cached forever
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| **Stale data** | Use TTL + event-based invalidation |
| **Cache stampede** | Use locks or probabilistic expiration |
| **Memory overflow** | Set max memory + eviction policy |
| **Hot keys** | Use local cache or replication |
| **Cache inconsistency** | Use write-through or invalidation |
| **Over-caching** | Cache only frequently accessed data |

---

## Multi-Level Caching Architecture

```
Request Flow:

1. Browser Cache (200ms saved)
   ↓ miss
2. CDN (500ms saved)
   ↓ miss
3. Application In-Memory Cache (800ms saved)
   ↓ miss
4. Redis Cluster (900ms saved)
   ↓ miss
5. Database Query Cache (950ms saved)
   ↓ miss
6. Database (1000ms)
```

**Example Implementation:**
```text
FUNCTION getProduct(productId)
    # L1: In-memory cache (fastest, small)
    IF memoryCache.contains(productId) THEN
        RETURN memoryCache.get(productId)
    END IF

    # L2: Distributed cache (fast, larger)
    cached = CACHE_GET("product:" + productId)
    IF cached EXISTS THEN
        product = deserialize(cached)
        memoryCache.put(productId, product)   # Populate L1
        RETURN product
    END IF

    # L3: Database (slow, largest)
    product = DB_QUERY("SELECT * FROM products WHERE id = ?", productId)

    # Populate all cache levels
    CACHE_SET("product:" + productId, serialize(product), TTL = 3600)
    memoryCache.put(productId, product)

    RETURN product
END FUNCTION
```

---

## When to Cache?

**Cache if:**
- ✅ Data is read frequently (>10x reads vs writes)
- ✅ Data is expensive to compute/fetch
- ✅ Data doesn't change often
- ✅ Slight staleness is acceptable

**Don't cache if:**
- ❌ Data changes very frequently
- ❌ Strong consistency required
- ❌ Data is accessed rarely
- ❌ Data is already fast to fetch

---

## Summary

**Caching is essential for:**
- ⚡ Performance (reduce latency from 100ms → 1ms)
- 💰 Cost savings (reduce database load by 90%+)
- 📈 Scalability (handle 10x more traffic)

**Best Practices:**
- Use cache-aside for read-heavy workloads
- Implement TTL-based + event-based invalidation
- Monitor cache hit rate (target >80%)
- Use LRU eviction policy for general use
- Prevent cache stampede with locks
- Use consistent hashing for distributed cache
- Implement multi-level caching for high traffic

**Next Steps:**
- Learn about [Load Balancer](load-balancer.md) for distribution
- Understand [Database Sharding](database-sharding.md) for scaling data
