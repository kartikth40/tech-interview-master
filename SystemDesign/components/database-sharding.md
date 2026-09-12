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
FUNCTION getShard(userId)
    IF userId >= 1 AND userId <= 1000000 THEN RETURN "shard1"
    IF userId >= 1000001 AND userId <= 2000000 THEN RETURN "shard2"
    IF userId >= 2000001 AND userId <= 3000000 THEN RETURN "shard3"
END FUNCTION

# Query
shard = getShard(userId)
user = SHARD_QUERY(shard, "SELECT * FROM users WHERE id = ?", userId)
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
FUNCTION getShard(userId)
    shardCount = 4
    hash = HASH(toString(userId))
    shardIndex = hash MOD shardCount

    RETURN shards[shardIndex]
END FUNCTION

# Examples
getShard(123)   -> shard2
getShard(456)   -> shard0
getShard(789)   -> shard3
```

**Hash Function:**
```text
FUNCTION hash(str)
    h = 0
    FOR EACH char IN str
        h = (h << 5) - h + charCode(char)
        h = h AS 32-bit integer
    END FOR
    RETURN ABS(h)
END FUNCTION
```

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
CLASS ConsistentHash
    FUNCTION init(shards = [], virtualNodes = 150)
        this.ring = empty map          # hash -> shard
        this.virtualNodes = virtualNodes
        FOR EACH shard IN shards
            this.addShard(shard)
        END FOR
    END FUNCTION

    FUNCTION addShard(shard)
        # Add virtual nodes for even distribution
        FOR i FROM 0 TO this.virtualNodes - 1
            hash = this.hash(shard + ":" + i)
            this.ring.put(hash, shard)
        END FOR
    END FUNCTION

    FUNCTION removeShard(shard)
        FOR i FROM 0 TO this.virtualNodes - 1
            hash = this.hash(shard + ":" + i)
            this.ring.remove(hash)
        END FOR
    END FUNCTION

    FUNCTION getShard(key)
        hash = this.hash(key)

        # Find first shard clockwise on ring
        sortedHashes = SORT_ASCENDING(this.ring.keys())
        FOR EACH ringHash IN sortedHashes
            IF ringHash >= hash THEN
                RETURN this.ring.get(ringHash)
            END IF
        END FOR

        # Wrap around
        RETURN this.ring.get(sortedHashes[0])
    END FUNCTION

    FUNCTION hash(str)
        h = 0
        FOR EACH char IN str
            h = (h << 5) - h + charCode(char)
            h = h AS 32-bit integer
        END FOR
        RETURN ABS(h)
    END FUNCTION
END CLASS

# Usage
ch = new ConsistentHash(["shard1", "shard2", "shard3"])

ch.getShard("user:123") -> shard2
ch.getShard("user:456") -> shard1

# Add new shard - only ~25% data needs to move
ch.addShard("shard4")
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
FUNCTION getShard(userId)
    userCountry = getUserCountry(userId)

    IF userCountry IN ["US", "CA", "MX"] THEN RETURN "shard_americas"
    IF userCountry IN ["UK", "FR", "DE", "IT"] THEN RETURN "shard_europe"
    IF userCountry IN ["IN", "CN", "JP", "SG"] THEN RETURN "shard_asia"

    RETURN "shard_global"
END FUNCTION
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
# Lookup table (can be in separate database or cache)
directory = {
    "user:123": "shard1",
    "user:456": "shard2",
    "user:789": "shard1"
}

FUNCTION getShard(userId)
    key = "user:" + userId
    RETURN directory[key] OR "shard_default"
END FUNCTION

# When user data grows too large, migrate to different shard
directory["user:123"] = "shard3"
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
```text
# Step 1: Start dual writes (write to both old and new shard)
FUNCTION writeUser(userId, data)
    oldShard = getOldShard(userId)
    newShard = getNewShard(userId)

    # Write to both shards in parallel
    PARALLEL
        SHARD_INSERT(oldShard, data)
        SHARD_INSERT(newShard, data)
    END PARALLEL
END FUNCTION

# Step 2: Background job migrates old data
FUNCTION migrateData()
    users = SHARD_QUERY(oldShard, "SELECT * FROM users WHERE id >= ? AND id < ?", start, end)

    FOR EACH user IN users
        SHARD_INSERT(newShard, user)
    END FOR
END FUNCTION

# Step 3: Switch reads to new shard
FUNCTION readUser(userId)
    newShard = getNewShard(userId)
    RETURN SHARD_QUERY(newShard, "SELECT * FROM users WHERE id = ?", userId)
END FUNCTION

# Step 4: Stop dual writes, delete old data
```

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

## 🛠️ Sharding Implementation Example

```text
CLASS ShardManager
    FUNCTION init(shards)
        this.shards = shards   # list of database connections
    END FUNCTION

    # Hash-based sharding
    FUNCTION getShard(key)
        hash = this.hash(key)
        index = hash MOD LENGTH(this.shards)
        RETURN this.shards[index]
    END FUNCTION

    FUNCTION hash(str)
        h = 0
        FOR EACH char IN str
            h = (h << 5) - h + charCode(char)
            h = h AS 32-bit integer
        END FOR
        RETURN ABS(h)
    END FUNCTION

    # Insert
    FUNCTION insert(tableName, data)
        shard = this.getShard(data.id)
        RETURN SHARD_QUERY(shard, "INSERT INTO " + tableName + " SET ?", data)
    END FUNCTION

    # Get by ID (single shard)
    FUNCTION getById(tableName, id)
        shard = this.getShard(id)
        results = SHARD_QUERY(shard, "SELECT * FROM " + tableName + " WHERE id = ?", id)
        RETURN results[0]
    END FUNCTION

    # Scatter-gather query
    FUNCTION getAll(tableName, condition)
        results = []
        FOR EACH shard IN this.shards IN PARALLEL
            results.append(SHARD_QUERY(shard, "SELECT * FROM " + tableName + " WHERE " + condition))
        END FOR
        RETURN FLATTEN(results)
    END FUNCTION

    # Count (aggregate across shards)
    FUNCTION count(tableName)
        results = []
        FOR EACH shard IN this.shards IN PARALLEL
            results.append(SHARD_QUERY(shard, "SELECT COUNT(*) AS count FROM " + tableName))
        END FOR
        total = 0
        FOR EACH result IN results
            total = total + result[0].count
        END FOR
        RETURN total
    END FUNCTION
END CLASS

# Usage
shardManager = new ShardManager([shard1Connection, shard2Connection, shard3Connection])

shardManager.insert("users", { id: 123, name: "Alice" })
user = shardManager.getById("users", 123)
totalUsers = shardManager.count("users")
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
```text
CLASS SnowflakeID
    FUNCTION init(datacenterId, workerId)
        this.epoch = 1609459200000   # Custom epoch (Jan 1, 2021)
        this.datacenterIdBits = 5
        this.workerIdBits = 5
        this.sequenceBits = 12

        this.datacenterId = datacenterId
        this.workerId = workerId
        this.sequence = 0
        this.lastTimestamp = -1
    END FUNCTION

    FUNCTION generate()
        timestamp = CURRENT_TIME_MILLIS()

        # Handle clock moving backwards
        IF timestamp < this.lastTimestamp THEN
            THROW Error("Clock moved backwards")
        END IF

        # Same millisecond
        IF timestamp == this.lastTimestamp THEN
            this.sequence = (this.sequence + 1) AND ((1 << this.sequenceBits) - 1)

            IF this.sequence == 0 THEN
                # Sequence overflow - wait for next millisecond
                WHILE timestamp <= this.lastTimestamp
                    timestamp = CURRENT_TIME_MILLIS()
                END WHILE
            END IF
        ELSE
            this.sequence = 0
        END IF

        this.lastTimestamp = timestamp

        # Construct 64-bit ID by bit-shifting each component into place
        id = ((timestamp - this.epoch) << (this.datacenterIdBits + this.workerIdBits + this.sequenceBits))
             OR (this.datacenterId << (this.workerIdBits + this.sequenceBits))
             OR (this.workerId << this.sequenceBits)
             OR this.sequence

        RETURN toString(id)
    END FUNCTION
END CLASS

snowflake = new SnowflakeID(1, 1)
id = snowflake.generate()   # e.g. '7234567890123456'

# Pros: Time-sortable, 64-bit (fits in long), k-sorted
# Cons: Requires coordination (datacenter + worker ID)
```

**Snowflake Structure:**
```
64 bits total:
- 41 bits: timestamp (milliseconds since custom epoch)
- 5 bits: datacenter ID (32 datacenters)
- 5 bits: worker ID (32 workers per datacenter)
- 12 bits: sequence (4096 IDs per millisecond)

Capacity: 4096 IDs/ms per worker = 4M IDs/sec per worker
```

---

## 📊 When to Shard?

**Shard when:**
- ✅ Single database >1TB (slow queries, expensive backups)
- ✅ High traffic >10K QPS per database
- ✅ Read/write bottleneck on single server
- ✅ Need geographic data distribution

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
