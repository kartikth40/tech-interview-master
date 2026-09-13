# Database Sharding (Component Deep Dive)

## 🎯 What is Database Sharding?

Sharding is a horizontal partitioning strategy that splits a large database into smaller, more manageable pieces called **shards**. Each shard is a separate database that holds a subset of the data.

**Why Shard?**
- 📈 **Scalability**: Single database can't handle billions of rows
- ⚡ **Performance**: Smaller databases = faster queries
- 💰 **Cost**: Cheaper to scale horizontally (add servers) than vertically (bigger server)
- 🌍 **Geography**: Store data closer to users

---

## 📊 Vertical vs Horizontal Partitioning

### **Vertical Partitioning (Split by Columns)**
```sql
-- Original table
Users: id | name | email | bio | avatar_url | preferences

-- Split into two tables
UsersBasic: id | name | email
UsersProfile: id | bio | avatar_url | preferences

Use: Separate frequently accessed from rarely accessed columns
```

### **Horizontal Partitioning (Split by Rows)** ⭐ Sharding
```sql
-- Shard 1
Users: (id: 1-1M)

-- Shard 2
Users: (id: 1M-2M)

-- Shard 3
Users: (id: 2M-3M)

Use: Distribute data across multiple servers
```

---

## 🔧 Sharding Strategies

### 1. **Range-Based Sharding**

```text
# Map contiguous key ranges to shards: 1..1M -> shard1, 1M..2M -> shard2, ...
getShard(userId): find the range that contains userId, return its shard
```

**Pros:**
- ✅ Simple to implement
- ✅ Easy to add new shards (add range)
- ✅ Range queries efficient (users 1M-1.5M → single shard)

**Cons:**
- ❌ Uneven data distribution (hotspots possible)
- ❌ Newer data gets more traffic (last shard overloaded)
- ❌ Hard to rebalance

**Use Cases:**
- Time-series data (shard by date)
- Logs, analytics events
- Sequential IDs

---

### 2. **Hash-Based Sharding** ⭐ Most Common

```text
# shardIndex = hash(shardKey) MOD shardCount, then route to shards[shardIndex]
getShard(userId): return shards[ hash(userId) MOD shardCount ]
```

Use a well-distributed hash (MD5/MurmurHash), not a hand-rolled one, to avoid clustering.

**Pros:**
- ✅ Even data distribution
- ✅ No hotspots
- ✅ Simple hash function

**Cons:**
- ❌ Range queries require querying all shards
- ❌ Adding/removing shards requires rehashing (data migration)
- ❌ Hard to rebalance

**Use Cases:**
- User data (shard by user_id)
- Product catalog (shard by product_id)
- General purpose

---

### 3. **Consistent Hashing** ⭐ Best for Dynamic Shards

```text
# Concept: hash both shards and keys onto a circular ring (0 .. 2^32).
# To place a key: hash it, then walk clockwise to the first shard on the ring.
# Adding/removing a shard only re-homes the keys between it and its neighbor
#   (~1/N of data), instead of rehashing everything like plain hash MOD N.
#
# Virtual nodes: each physical shard is placed at MANY points on the ring
#   (e.g. 150 "vnodes"). Without them, distribution is lopsided and removing
#   a node dumps ALL of its load onto its single clockwise successor.
# Real systems hash with MD5/MurmurHash, not a hand-rolled hash.
```

**Pros:**
- ✅ Minimal data movement when adding/removing shards (~1/N data moves)
- ✅ Even distribution with virtual nodes
- ✅ Dynamic scaling

**Cons:**
- ❌ More complex to implement
- ❌ Range queries still require all shards

**Use Cases:**
- Distributed caches (Redis, Memcached)
- Cloud storage systems
- When frequent shard changes expected

---

### 4. **Geographic Sharding**

```text
# Route by user's region: Americas -> shard_americas, Europe -> shard_europe, ...
getShard(userId): map the user's country to its regional shard
```

**Pros:**
- ✅ Low latency (data close to users)
- ✅ Regulatory compliance (GDPR, data residency)
- ✅ Natural partitioning

**Cons:**
- ❌ Uneven distribution (more users in some regions)
- ❌ Cross-region queries expensive
- ❌ Complexity in global features

**Use Cases:**
- Global applications (Facebook, Instagram)
- Data privacy requirements (EU GDPR)
- Multi-region deployments

---

### 5. **Directory-Based Sharding**

```text
# Keep an explicit key -> shard lookup table (in a DB or cache).
getShard(userId): return directory["user:" + userId]
# To rebalance a single record, just update its directory entry to a new shard.
```

**Pros:**
- ✅ Flexible (can rebalance individual records)
- ✅ No fixed sharding logic
- ✅ Easy to migrate hot data

**Cons:**
- ❌ Lookup table = single point of failure / bottleneck
- ❌ Extra hop for every query
- ❌ Directory can become large

**Use Cases:**
- When sharding key changes frequently
- Complex sharding requirements
- Migration from unsharded to sharded

---

## 🗂️ Choosing the Shard Key

**Good Shard Key Properties:**
- ✅ **High Cardinality**: Many unique values (e.g., user_id ✅, country ❌)
- ✅ **Even Distribution**: Avoids hotspots
- ✅ **Query Friendly**: Queries include shard key (no scatter-gather)
- ✅ **Immutable**: Doesn't change (changing = data migration)

**Examples:**

| Shard Key | Cardinality | Distribution | Best For |
|-----------|-------------|--------------|----------|
| user_id | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | User data |
| email | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | User data |
| timestamp | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ (recent = hotspot) | Time-series |
| country | ⭐⭐ | ⭐⭐ (uneven) | Geographic |
| tenant_id | ⭐⭐⭐⭐ | ⭐⭐⭐ | Multi-tenant SaaS |

**Bad Shard Keys:**
- ❌ **Boolean fields** (male/female → only 2 shards)
- ❌ **Status fields** (active/inactive → uneven)
- ❌ **Timestamp** (recent data = hotspot)

---

## 🎯 Querying Sharded Data

### **Single-Shard Query (Fast)** ✅
```text
# Query includes shard key
FUNCTION getUser(userId)
    shard = getShard(userId)
    user = SHARD_QUERY(shard, "SELECT * FROM users WHERE id = ?", userId)
    RETURN user
END FUNCTION

# Latency: 10ms
```

### **Scatter-Gather Query (Slow)** ❌
```text
# Query does NOT include shard key - must query ALL shards
FUNCTION getUserByEmail(email)
    # Fan out the query to every shard in parallel
    results = []
    FOR EACH shard IN shards IN PARALLEL
        results.append(SHARD_QUERY(shard, "SELECT * FROM users WHERE email = ?", email))
    END FOR

    RETURN FIRST(FLATTEN(results) WHERE user IS NOT null)
END FUNCTION

# Latency: 10ms * num_shards (if 10 shards = 100ms)
```

**Solution: Denormalize or Secondary Index**
```text
# Option 1: Store email -> user_id mapping
userId = INDEX_GET(emailIndex, email)
shard = getShard(userId)
user = SHARD_QUERY(shard, "SELECT * FROM users WHERE id = ?", userId)

# Option 2: Global secondary index (search engine)
user = SEARCH_ENGINE_QUERY(index = "users", match = { email: email })
```

---

## 🔗 Handling Joins Across Shards

### **Problem:**
```sql
-- Works in single database
SELECT orders.*, users.name 
FROM orders 
JOIN users ON orders.user_id = users.id;

-- Doesn't work with sharding:
-- orders and users might be on different shards
```

### **Solutions:**

#### 1. **Denormalize** ⭐ Best
```text
# Store user data in orders table
Orders: id | user_id | user_name | product_id | total

# No join needed
orders = SHARD_QUERY(shard, "SELECT * FROM orders WHERE user_id = ?", userId)
```

#### 2. **Application-Level Join**
```text
# Fetch from multiple shards, join in app
orders = SHARD_QUERY(ordersShard, "SELECT * FROM orders WHERE user_id = ?", userId)
user = SHARD_QUERY(usersShard, "SELECT * FROM users WHERE id = ?", userId)

result = []
FOR EACH order IN orders
    enriched = COPY(order)
    enriched.user_name = user.name
    result.append(enriched)
END FOR
```

#### 3. **Co-locate Related Data** (Shard by Same Key)
```sql
-- Shard both users and orders by user_id
-- All user's data on same shard
Shard 1: users (id: 1-1M), orders (user_id: 1-1M)
Shard 2: users (id: 1M-2M), orders (user_id: 1M-2M)

-- Join works within shard
SELECT orders.*, users.name 
FROM orders 
JOIN users ON orders.user_id = users.id
WHERE users.id = 123;
```

---

## 🔄 Rebalancing Shards

### **When to Rebalance:**
- Shard becomes too large (>1TB)
- Uneven data distribution (shard1 = 10GB, shard2 = 500GB)
- Adding new shards
- Hot shard (one shard gets 90% traffic)

### **Rebalancing Strategies:**

#### 1. **Online Migration (Zero Downtime)**

Four-step dual-write cutover:
1. **Dual-write**: writes go to both the old and the new shard so they stay in sync.
2. **Backfill**: a background job copies existing rows from old shard to new shard.
3. **Switch reads**: once backfill is verified, point reads at the new shard.
4. **Cut over**: stop dual-writes and drop the old data.

#### 2. **Virtual Shards**
```text
# Create 256 virtual shards, map to 4 physical shards
virtualShardCount = 256
physicalShardCount = 4

FUNCTION getVirtualShard(userId)
    RETURN hash(userId) MOD virtualShardCount
END FUNCTION

FUNCTION getPhysicalShard(virtualShard)
    RETURN FLOOR(virtualShard / (virtualShardCount / physicalShardCount))
END FUNCTION

# Add 5th physical shard: remap virtual shards 200-255 -> shard5
# Only ~20% data needs to move
```

---

## 🏗️ Database Sharding Architectures

### **1. Application-Level Sharding**
```
App ──→ Sharding Logic ──→ Shard 1
                        ──→ Shard 2
                        ──→ Shard 3

Pros: Full control
Cons: App handles complexity
```

### **2. Proxy-Based Sharding** ⭐
```
App ──→ Proxy (Vitess, ProxySQL) ──→ Shard 1
                                  ──→ Shard 2
                                  ──→ Shard 3

Pros: App unaware of sharding
Cons: Proxy = potential bottleneck
```

### **3. Database-Native Sharding**
```
Examples:
- MongoDB (automatic sharding)
- Cassandra (partition key)
- CockroachDB (range-based)
- Citus (PostgreSQL extension)

Pros: Built-in, optimized
Cons: Vendor-specific
```

---

## ⚠️ Common Pitfalls

| Problem | Solution |
|---------|----------|
| **Hotspots** | Use hash-based sharding, not range-based |
| **Cross-shard joins** | Denormalize data or co-locate related data |
| **Scatter-gather slow** | Add secondary indexes (Elasticsearch) |
| **Auto-increment IDs** | Use globally unique IDs (UUID, Snowflake ID) |
| **Transactions** | Avoid cross-shard transactions (use sagas) |
| **Schema changes** | Apply to all shards simultaneously |

### Hot Keys / Celebrity Partitions

Even with perfect hashing, a single key can be disproportionately hot (a celebrity with millions of followers, a viral product). All of that traffic lands on one shard, so the shard becomes a bottleneck no matter how many shards you add. Mitigations:
- **Key salting**: append a bucket suffix (`celebrityId#0..N`) so the key's writes/reads spread across N shards; the app fans out and merges.
- **Split the hot entity**: model the celebrity's data as multiple sub-partitions (e.g. shard followers by follower_id, not by celebrity_id).
- **Cache/replicate** the hot key in front of the shard to absorb read load.

---

## 🆔 Globally Unique IDs (Required for Sharding)

### **Problem with Auto-Increment:**
```sql
-- Each shard has id=1, id=2, id=3...
Shard 1: users (id: 1, 2, 3, ...)
Shard 2: users (id: 1, 2, 3, ...) ← Conflict!
```

### **Solutions:**

#### 1. **UUID (128-bit)** ✅
```text
userId = GENERATE_UUID()   # e.g. '550e8400-e29b-41d4-a716-446655440000'

# Pros: Truly unique, no coordination
# Cons: Large (36 chars), not time-sortable, poor database index performance
```

#### 2. **Twitter Snowflake (64-bit)** ⭐ Best

Compose a 64-bit ID from timestamp + machine bits + a per-ms sequence counter, so IDs are unique across shards without a central sequence. Requires coordination to assign each generator a distinct datacenter/worker ID.

**Snowflake Structure:**
```
64 bits total:
- 41 bits: timestamp (milliseconds since custom epoch)
- 5 bits: datacenter ID (32 datacenters)
- 5 bits: worker ID (32 workers per datacenter)
- 12 bits: sequence (4096 IDs per millisecond)

Capacity: 4096 IDs/ms per worker = 4M IDs/sec per worker
```

Because the timestamp occupies the high bits, Snowflake IDs are time-sortable (k-sorted) → sequential inserts give good B-tree index locality, unlike random UUIDv4 which scatters writes across the index.

---

## 📊 When to Shard?

**Shard when:**
- ✅ Single database >1TB (slow queries, expensive backups)
- ✅ High traffic >10K QPS per database
- ✅ Read/write bottleneck on single server
- ✅ Need geographic data distribution

**Quick capacity estimation (how many shards?):**
- Total data / capacity per shard = shard count. E.g. 1 TB data ÷ 200 GB per shard = 5 shards → round up to **8** for headroom and clean power-of-2 rebalancing.
- Sanity-check throughput too: total QPS ÷ per-shard QPS ceiling. Take the larger of the storage-driven and throughput-driven counts.

**Don't shard if:**
- ❌ Data <100GB (vertical scaling sufficient)
- ❌ Traffic <1K QPS (caching + read replicas sufficient)
- ❌ Can partition by service (microservices)
- ❌ Team lacks sharding expertise

**Alternatives to Sharding:**
1. **Caching** (Redis) - Reduce database load by 90%
2. **Read Replicas** - Scale reads horizontally
3. **Vertical Scaling** - Bigger database server (up to 96 cores, 768GB RAM)
4. **Partitioning** - Split within single database (PostgreSQL partitions)
5. **Microservices** - Split by domain (users DB, products DB, orders DB)

---

## Summary

**Database Sharding:**
- 📈 Horizontal partitioning to scale beyond single database
- 🎯 Shard by high-cardinality, immutable key (user_id ✅, status ❌)
- ⚖️ Hash-based (even distribution) or Range-based (range queries)
- 🔄 Consistent hashing for dynamic shard addition/removal
- 🆔 Use globally unique IDs (Snowflake ID ⭐)

**Best Practices:**
- Denormalize data to avoid cross-shard joins
- Co-locate related data on same shard
- Use proxy layer (Vitess) to hide sharding from app
- Plan for rebalancing from day one
- Start with fewer shards (4-8), add as needed
- Monitor shard size and traffic distribution

**Next Steps:**
- Learn about [Load Balancer](load-balancer.md) for request distribution
- Understand [Caching](caching.md) to reduce database load
