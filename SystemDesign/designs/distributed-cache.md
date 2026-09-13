# Distributed Cache System Design (Redis/Memcached)
> **SDE-2 Interview Ready** | 45-minute format

## 🎯 Problem Statement

Design a distributed caching system like Redis or Memcached that:
- Stores key-value pairs in memory
- Fast read/write operations (<1ms)
- Distributed across multiple servers
- Handles cache eviction (LRU, LFU)
- High availability with replication

**Use Cases:**
- Session storage
- Database query caching
- API response caching
- Rate limiting

---

## 1️⃣ Requirements Clarification

### Functional Requirements:

1. **Basic Operations**
   - `SET key value [TTL]` - Store key-value with optional expiration
   - `GET key` - Retrieve value by key
   - `DELETE key` - Remove key
   - `EXISTS key` - Check if key exists

2. **Advanced Features**
   - TTL (Time-to-live) expiration
   - Atomic operations (INCR, DECR)
   - Data structures (strings, lists, sets, hashes)

3. **Distributed Features**
   - Horizontal scaling (multiple cache nodes)
   - Consistent hashing for key distribution
   - Replication for high availability

### Non-Functional Requirements:
- **Latency:** <1ms for read/write
- **Throughput:** 100K ops/sec per node
- **Availability:** 99.99% uptime
- **Scalability:** Add/remove nodes dynamically
- **Consistency:** Eventually consistent (AP system in CAP theorem)

### Out of Scope:
- Persistence to disk (pure in-memory cache)
- Complex transactions
- Pub/Sub messaging

---

## 2️⃣ Capacity Estimation

```
Cache Size:
- Average key size: 50 bytes
- Average value size: 500 bytes
- Total per entry: 550 bytes
- 10M keys: 550 bytes × 10M = 5.5 GB
- Single node capacity: 16 GB RAM → 30M keys

Throughput:
- 100K ops/sec per node
- 10 nodes → 1M ops/sec

Replication:
- Use master-slave replication (1 master, 2 replicas)
- Increases availability to 99.99%
```

---

## 3️⃣ API Design

```text
# 1. Set Key-Value
SET key value [EX seconds]
Example: SET user:123:session "abc123xyz" EX 3600

Response: OK

# 2. Get Value
GET key
Example: GET user:123:session

Response: "abc123xyz"

# 3. Delete Key
DEL key
Example: DEL user:123:session

Response: 1  (number of keys deleted)

# 4. Check Existence
EXISTS key
Example: EXISTS user:123:session

Response: 1  (true) or 0 (false)

# 5. Increment Counter (Atomic)
INCR key
Example: INCR page:views:123

Response: 501  (new value after increment)

# 6. Set Expiration
EXPIRE key seconds
Example: EXPIRE user:123:session 3600

Response: 1  (success)

# 7. Get TTL
TTL key
Example: TTL user:123:session

Response: 3500  (seconds remaining, -1 = no expiry, -2 = key doesn't exist)
```

---

## 4️⃣ Database Design

### In-Memory Data Structure

```text
# Hash Table (main storage)
cache = empty Map        # key -> { value, expiresAt }

# LRU Linked List (eviction)
lruList = empty DoublyLinkedList   # most recent -> least recent

# Data structure
STRUCTURE CacheEntry
  key       : string
  value     : any
  expiresAt : timestamp OR null   # Unix timestamp
  lruNode   : ListNode            # reference to LRU list node
END STRUCTURE
```

---

## 5️⃣ High-Level Design

```
┌──────────────────────────────────────────────────────┐
│                  Clients                             │
│  (Application Servers)                               │
└───────────┬──────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────┐
│      Cache Client Library                             │
│  - Consistent hashing                                 │
│  - Connection pooling                                 │
│  - Retry logic                                        │
└─────┬─────────────┬─────────────┬──────────────┬──────┘
      │             │             │              │
      ▼             ▼             ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  Cache   │  │  Cache   │  │  Cache   │  │  Cache   │
│  Node 1  │  │  Node 2  │  │  Node 3  │  │  Node 4  │
│ (Master) │  │ (Master) │  │ (Master) │  │ (Master) │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │
     │             │             │             │
   ┌─┴──┐        ┌─┴──┐        ┌─┴──┐        ┌─┴──┐
   │Rep1│        │Rep1│        │Rep1│        │Rep1│
   └────┘        └────┘        └────┘        └────┘
   ┌────┐        ┌────┐        ┌────┐        ┌────┐
   │Rep2│        │Rep2│        │Rep2│        │Rep2│
   └────┘        └────┘        └────┘        └────┘
```

**Data Distribution:**
- Consistent hashing to distribute keys across nodes
- Each key belongs to one master node
- Master replicates to 2 replicas (async)

---

## 6️⃣ Low-Level Design

### Class Diagram

```
┌────────────────────────┐
│   CacheNode            │
├────────────────────────┤
│ - hashTable: Map       │
│ - lruList: LRUList     │
│ - maxSize: number      │
├────────────────────────┤
│ + get(key): value      │
│ + set(key, value, ttl) │
│ + delete(key): boolean │
│ + evict(): void        │
└────────────────────────┘
       │
       │ uses
       ▼
┌────────────────────────┐
│   LRUList              │
├────────────────────────┤
│ - head: Node           │
│ - tail: Node           │
├────────────────────────┤
│ + moveToFront(node)    │
│ + removeLast(): Node   │
└────────────────────────┘
```

---

## 7️⃣ Deep Dives

### Deep Dive 1: LRU Cache Implementation

**Challenge:** Evict least recently used items when cache is full

**Solution: Hash Table + Doubly Linked List**

```text
CLASS LRUCache

  FUNCTION init(capacity)
    this.capacity = capacity
    this.cache    = empty Map        # key -> { value, expiresAt, node }
    this.head     = new ListNode()   # dummy head
    this.tail     = new ListNode()   # dummy tail
    this.head.next = this.tail
    this.tail.prev = this.head
  END FUNCTION

  FUNCTION get(key)
    IF key NOT IN this.cache THEN
      RETURN null
    END IF

    entry = this.cache[key]

    # Check expiration
    IF entry.expiresAt IS SET AND currentTime() > entry.expiresAt THEN
      this.delete(key)
      RETURN null
    END IF

    # Move to front (most recently used)
    this.moveToFront(entry.node)

    RETURN entry.value
  END FUNCTION

  FUNCTION set(key, value, ttl = null)
    # Delete if exists (will re-add)
    IF key IN this.cache THEN
      this.delete(key)
    END IF

    # Evict if at capacity
    IF this.cache.size >= this.capacity THEN
      this.evictLRU()
    END IF

    # Create new entry
    node      = new ListNode(key)
    expiresAt = IF ttl IS SET THEN currentTime() + (ttl * 1000) ELSE null

    this.cache[key] = { value: value, expiresAt: expiresAt, node: node }

    # Add to front
    this.addToFront(node)
  END FUNCTION

  FUNCTION delete(key)
    IF key NOT IN this.cache THEN
      RETURN false
    END IF

    entry = this.cache[key]
    this.removeNode(entry.node)
    this.cache.remove(key)

    RETURN true
  END FUNCTION

  FUNCTION evictLRU()
    # Remove tail (least recently used)
    lruNode = this.tail.prev

    IF lruNode IS NOT this.head THEN
      this.removeNode(lruNode)
      this.cache.remove(lruNode.key)
    END IF
  END FUNCTION

  # Helper: Move node to front
  FUNCTION moveToFront(node)
    this.removeNode(node)
    this.addToFront(node)
  END FUNCTION

  # Helper: Add node to front
  FUNCTION addToFront(node)
    node.next            = this.head.next
    node.prev            = this.head
    this.head.next.prev  = node
    this.head.next       = node
  END FUNCTION

  # Helper: Remove node from list
  FUNCTION removeNode(node)
    node.prev.next = node.next
    node.next.prev = node.prev
  END FUNCTION

END CLASS

CLASS ListNode
  FUNCTION init(key = null)
    this.key  = key
    this.prev = null
    this.next = null
  END FUNCTION
END CLASS
```

**Time Complexity:**
- GET: O(1)
- SET: O(1)
- DELETE: O(1)
- EVICT: O(1)

**Space Complexity:** O(n) where n = number of keys

---

### Deep Dive 2: Consistent Hashing (Distributed Cache)

**Challenge:** Distribute keys across multiple cache nodes, minimize data movement when nodes are added/removed

**Solution: Consistent Hashing with Virtual Nodes**

```text
CLASS ConsistentHash

  FUNCTION init(nodes, virtualNodesPerNode = 150)
    this.ring                = empty Map    # hash -> node
    this.sortedHashes        = empty list
    this.virtualNodesPerNode = virtualNodesPerNode

    # Add all nodes
    FOR EACH node IN nodes
      this.addNode(node)
    END FOR
  END FUNCTION

  FUNCTION addNode(node)
    # Create virtual nodes (replicas)
    FOR i FROM 0 TO this.virtualNodesPerNode - 1
      virtualNodeId = node.id + ":" + i
      hash          = this.hash(virtualNodeId)

      this.ring[hash] = node
      append hash TO this.sortedHashes
    END FOR

    # Keep hashes sorted
    SORT this.sortedHashes ASCENDING
  END FUNCTION

  FUNCTION removeNode(node)
    # Remove all virtual nodes
    FOR i FROM 0 TO this.virtualNodesPerNode - 1
      virtualNodeId = node.id + ":" + i
      hash          = this.hash(virtualNodeId)

      this.ring.remove(hash)
      index = indexOf(this.sortedHashes, hash)
      removeAt(this.sortedHashes, index)
    END FOR
  END FUNCTION

  FUNCTION getNode(key)
    IF this.sortedHashes IS EMPTY THEN
      RETURN null
    END IF

    keyHash = this.hash(key)

    # Find first node clockwise (binary search)
    left  = 0
    right = length(this.sortedHashes) - 1

    WHILE left <= right DO
      mid = floor((left + right) / 2)

      IF this.sortedHashes[mid] EQUALS keyHash THEN
        RETURN this.ring[this.sortedHashes[mid]]
      ELSE IF this.sortedHashes[mid] < keyHash THEN
        left = mid + 1
      ELSE
        right = mid - 1
      END IF
    END WHILE

    # If not found, wrap around to first node
    IF left >= length(this.sortedHashes) THEN
      left = 0
    END IF

    RETURN this.ring[this.sortedHashes[left]]
  END FUNCTION

  FUNCTION hash(key)
    # Use CRC32 or MurmurHash for fast hashing
    RETURN crc32(key)
  END FUNCTION

END CLASS

# Usage
nodes = [
  { id: "cache-1", host: "10.0.0.1", port: 6379 },
  { id: "cache-2", host: "10.0.0.2", port: 6379 },
  { id: "cache-3", host: "10.0.0.3", port: 6379 }
]

hashRing = new ConsistentHash(nodes)

# Get node for key
node = hashRing.getNode("user:123:session")
print("Key should be stored on " + node.id)
```

**Benefits:**
- ✅ Adding/removing nodes affects only 1/N of keys (minimal data movement)
- ✅ Even distribution with virtual nodes
- ✅ Fast lookup O(log N)

**Without Consistent Hashing:**
- Simple hash: `node = hash(key) % N`
- Problem: Adding node changes N → All keys rehashed → 100% data movement!

**With Consistent Hashing:**
- Adding node → Only 1/N keys move
- Removing node → Only 1/N keys move

---

### Deep Dive 3: Replication & High Availability

**Challenge:** If cache node fails, all its data is lost

**Solution: Master-Slave Replication**

```text
CLASS CacheCluster

  FUNCTION init()
    this.masters  = empty list
    this.replicas = empty Map      # master -> [replica1, replica2]
  END FUNCTION

  FUNCTION set(key, value, ttl)
    # 1. Find master node using consistent hashing
    master = this.hashRing.getNode(key)

    # 2. Write to master (synchronous)
    master.set(key, value, ttl)

    # 3. Asynchronously replicate to slaves
    replicas = this.replicas[master.id]

    IF replicas EXISTS THEN
      # Fire-and-forget replication (async)
      this.replicateAsync(key, value, ttl, replicas)
    END IF
  END FUNCTION

  FUNCTION get(key)
    # 1. Find master node
    master = this.hashRing.getNode(key)

    # 2. Try master first
    TRY
      RETURN master.get(key)
    CATCH err
      # 3. Fallback to replica if master is down
      replicas = this.replicas[master.id]

      IF replicas EXISTS AND length(replicas) > 0 THEN
        RETURN replicas[0].get(key)
      END IF

      THROW err
    END TRY
  END FUNCTION

  FUNCTION replicateAsync(key, value, ttl, replicas)
    # Replicate to all replicas in parallel
    FOR EACH replica IN replicas IN PARALLEL
      TRY
        replica.set(key, value, ttl)
      CATCH err
        logError("Replication failed to " + replica.id, err)
      END TRY
    END FOR
  END FUNCTION

  # Failover: Promote replica to master
  FUNCTION handleMasterFailure(failedMaster)
    replicas = this.replicas[failedMaster.id]

    IF replicas EXISTS AND length(replicas) > 0 THEN
      # Promote first replica to master
      newMaster = replicas[0]

      # Update hash ring
      this.hashRing.removeNode(failedMaster)
      this.hashRing.addNode(newMaster)

      # Remaining replicas become replicas of new master
      this.replicas[newMaster.id] = replicas EXCLUDING first element
      this.replicas.remove(failedMaster.id)

      log("Promoted " + newMaster.id + " to master")
    END IF
  END FUNCTION

END CLASS
```

**Replication Strategies:**

**1. Asynchronous Replication (Used above)**
- Master writes immediately, replicates async
- ✅ Low latency
- ❌ Possible data loss if master fails before replication

**2. Synchronous Replication**
- Master waits for replica ACK before responding
- ✅ No data loss
- ❌ Higher latency

**Trade-off:** For caching, asynchronous is acceptable (cache misses are okay)

---

## 8️⃣ Bottlenecks & Optimizations

### Bottlenecks:

1. **Single-threaded** → Use thread pool or async I/O (Redis uses single-threaded event loop)
2. **Network latency** → Connection pooling, pipelining
3. **Hotspot keys** → Client-side caching, split hot keys

### Optimizations:

**1. Pipelining (Batch Commands):**
```text
# Instead of 3 round trips:
cache.set("key1", "val1")
cache.set("key2", "val2")
cache.set("key3", "val3")

# Use pipeline (1 round trip):
cache.pipeline([
  ["set", "key1", "val1"],
  ["set", "key2", "val2"],
  ["set", "key3", "val3"]
])
```

**2. Client-side Caching:**
```text
# Cache hot keys in application memory
localCache = empty Map

FUNCTION get(key)
  IF key IN localCache THEN
    RETURN localCache[key]
  END IF

  value = redisCache.get(key)
  localCache[key] = value

  RETURN value
END FUNCTION
```

**3. Connection Pooling:**
```
Reuse TCP connections instead of creating new ones
Reduces connection overhead (3-way handshake)
```

---

## 9️⃣ Interview Tips

### What to Focus on (45-min):

1. **Clarify requirements** (5 min)
   - Pure in-memory or persistent?
   - Eviction policy (LRU, LFU)?
   - Distributed?

2. **High-level design** (10 min)
   - Hash table + LRU list
   - Consistent hashing for distribution

3. **Deep dive 1: LRU implementation** (15 min)
   - Hash table + doubly linked list
   - O(1) operations

4. **Deep dive 2: Consistent hashing** (10 min)
   - Virtual nodes
   - Minimal data movement

5. **Discuss replication** (5 min)
   - Master-slave
   - Async vs sync

6. **Bottlenecks** (5 min)

### Common Follow-ups:

**Q: LRU vs LFU eviction?**
A: 
- LRU (Least Recently Used): Evict oldest accessed item
- LFU (Least Frequently Used): Evict least accessed item (requires counter)

**Q: How do you handle cache stampede?**
A: Use locking/semaphore, only one process fetches from DB, others wait

**Q: What if all nodes fail?**
A: Application should handle gracefully (fallback to DB), use circuit breaker

**Q: How do you ensure cache coherence (sync with DB)?**
A: 
- Write-through: Update cache + DB simultaneously
- Write-back: Update cache, async update DB
- Cache-aside: Application handles cache + DB separately

**Q: Redis vs Memcached?**
A:
- Redis: Supports data structures (lists, sets), persistence, replication
- Memcached: Simple key-value, multi-threaded, slightly faster for pure caching

---

## Summary

**Key Decisions:**
1. ✅ **LRU eviction** (hash table + doubly linked list)
2. ✅ **Consistent hashing** (distribute keys, virtual nodes)
3. ✅ **Master-slave replication** (async for low latency)
4. ✅ **TTL expiration** (lazy deletion + active deletion)

**Tech Stack:**
- Language: C/Go (low-level performance)
- Network: TCP with connection pooling
- Serialization: MessagePack/Protobuf

**Performance:**
- Latency: <1ms (in-memory)
- Throughput: 100K ops/sec per node
- Availability: 99.99% (with replication)
