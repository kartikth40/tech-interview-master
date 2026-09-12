# System Design Interview Guide

## 🎯 Overview

System design interviews test your ability to design large-scale distributed systems. This guide provides frameworks, methodologies, and templates to tackle any system design question.

---

## 📋 Interview Framework (Use This Every Time)

### **Step 1: Requirements Clarification (5 min)**
Ask questions to understand scope:

**Functional Requirements:**
- What features are we building?
- What are the core use cases?
- What is the expected usage pattern?

**Non-Functional Requirements:**
- Scale (DAU, QPS, data size)?
- Performance (latency, throughput)?
- Availability vs Consistency (CAP theorem)?
- Durability requirements?

### **Step 2: Back-of-the-Envelope Estimation (5 min)**
Calculate capacity requirements:

```
Traffic Estimates:
- Daily Active Users (DAU): ?
- Requests per user per day: ?
- Total requests per day = DAU × requests per user
- Queries per second (QPS) = total requests / 86400
- Peak QPS = QPS × 2-3x

Storage Estimates:
- Data per user: ?
- Total data = DAU × data per user
- Storage needed for X years = ?

Bandwidth Estimates:
- Average request size: ?
- Bandwidth = QPS × average request size
```

### **Step 3: System Interface (API Design) (5 min)**
Define core APIs:

```text
# Example: URL Shortener
createShortURL(api_key, long_url, [custom_alias], [expire_date])
  -> returns: short_url

getOriginalURL(short_url)
  -> redirect to: long_url

deleteURL(api_key, short_url)
  -> returns: success/failure
```

### **Step 4: High-Level Design (10 min)**
Draw the architecture diagram:

```
Components to consider:
├── Client (Web/Mobile)
├── Load Balancer
├── Application Servers
├── Cache Layer
├── Database (SQL/NoSQL)
├── Object Storage (S3)
├── CDN
├── Message Queue
└── Search/Analytics
```

### **Step 5: Database Design (5 min)**
Design schema for key entities:

**SQL Example:**
```sql
Table: Users
- user_id (PK)
- name
- email
- created_at

Table: Posts
- post_id (PK)
- user_id (FK)
- content
- created_at
```

**NoSQL Example:**
```json
{
  "user_id": "uuid",
  "name": "John Doe",
  "posts": [
    {
      "post_id": "uuid",
      "content": "...",
      "timestamp": "2026-02-15"
    }
  ]
}
```

### **Step 6: Detailed Design (15 min)**
Deep dive into critical components:

- **Algorithm/Data Structure choices**
- **Database partitioning/sharding**
- **Caching strategy**
- **Load balancing**
- **Replication and Failover**

### **Step 7: Identify Bottlenecks & Trade-offs (5 min)**
Discuss:
- Single points of failure
- Scalability limitations
- Consistency vs Availability trade-offs
- Read-heavy vs Write-heavy optimizations

---

## 🔑 Key Concepts

### **1. Scalability**

**Horizontal Scaling (Scale Out):**
- Add more machines
- Better for distributed systems
- Requires load balancing

**Vertical Scaling (Scale Up):**
- Add more power to existing machine
- Limited by hardware capacity
- Simpler but has ceiling

### **2. CAP Theorem**

Pick 2 out of 3:
- **Consistency:** Every read receives the most recent write
- **Availability:** Every request receives a response (success/failure)
- **Partition Tolerance:** System continues despite network partitions

**Examples:**
- CP: MongoDB, HBase (Consistency + Partition Tolerance)
- AP: Cassandra, DynamoDB (Availability + Partition Tolerance)
- CA: RDBMS (Consistency + Availability, no partition tolerance)

### **3. Database Choices**

**SQL (Relational):**
- Use when: ACID compliance, complex queries, structured data
- Examples: PostgreSQL, MySQL
- Pros: Strong consistency, transactions, joins
- Cons: Hard to scale horizontally

**NoSQL:**

**Document DB (MongoDB, Couchbase):**
- Use when: Flexible schema, hierarchical data
- Pros: Fast reads, easy to scale
- Cons: Limited JOIN support

**Key-Value (Redis, DynamoDB):**
- Use when: Simple key-based lookups, caching
- Pros: Extremely fast, simple
- Cons: No complex queries

**Column-Family (Cassandra, HBase):**
- Use when: Write-heavy, time-series data
- Pros: High write throughput
- Cons: Complex to manage

**Graph DB (Neo4j):**
- Use when: Highly connected data (social networks)
- Pros: Fast relationship queries
- Cons: Doesn't scale as well

### **4. Caching**

**Cache Strategies:**

**Cache Aside:**
```
1. Check cache
2. If miss, read from DB
3. Update cache
```

**Write Through:**
```
1. Write to cache
2. Cache writes to DB synchronously
```

**Write Behind:**
```
1. Write to cache
2. Cache writes to DB asynchronously (batch)
```

**Eviction Policies:**
- LRU (Least Recently Used)
- LFU (Least Frequently Used)
- FIFO (First In First Out)

### **5. Load Balancing**

**Algorithms:**
- Round Robin
- Least Connections
- Weighted Round Robin
- IP Hash (session affinity)

**Layers:**
- Layer 4 (Transport): Fast, TCP/UDP based
- Layer 7 (Application): Slower, HTTP based, content-aware

### **6. Replication**

**Master-Slave:**
- All writes to master
- Reads from slaves
- Eventual consistency

**Master-Master:**
- Writes to any master
- Sync between masters
- Conflict resolution needed

**Multi-Master:**
- Multiple writable replicas
- Complex conflict resolution
- High availability

### **7. Partitioning/Sharding**

**Horizontal Partitioning:**
- Split rows across multiple DBs
- Shard key determines partition

**Vertical Partitioning:**
- Split columns into different tables/DBs
- Group related columns together

**Sharding Strategies:**
- Hash-based: `shard = hash(key) % num_shards`
- Range-based: `if id < 1000 → shard1, else → shard2`
- Directory-based: Lookup table for shard location

### **8. Message Queues**

**Use Cases:**
- Asynchronous processing
- Decoupling services
- Load leveling

**Examples:**
- RabbitMQ, Apache Kafka, Amazon SQS

### **9. CDN (Content Delivery Network)**

**Use when:**
- Serving static content (images, videos, CSS, JS)
- Global user base
- Reduce latency

**How it works:**
- Edge servers cache content close to users
- Origin server serves as source of truth

---

## 📐 Common Design Patterns

### **1. Read-Heavy System**
```
Solutions:
- Extensive caching (Redis, Memcached)
- Read replicas
- CDN for static content
- Database indexing
```

### **2. Write-Heavy System**
```
Solutions:
- Message queue to buffer writes
- Write-behind caching
- Database sharding
- Batch inserts
- Cassandra/HBase (optimized for writes)
```

### **3. Low Latency System**
```
Solutions:
- Caching at multiple layers
- CDN for static content
- Async processing
- In-memory databases (Redis)
- Geographic distribution
```

### **4. High Availability System**
```
Solutions:
- Redundancy (multiple servers)
- Load balancers with health checks
- Database replication
- No single point of failure
- Automatic failover
```

---

## 🎯 Common Pitfalls to Avoid

❌ **Don't jump straight to design** - Clarify requirements first  
❌ **Don't over-engineer** - Start simple, then scale  
❌ **Don't ignore trade-offs** - Discuss pros/cons of choices  
❌ **Don't forget non-functional requirements** - Scale, latency, availability  
❌ **Don't design in silence** - Talk through your thought process  
❌ **Don't ignore single points of failure** - Always discuss redundancy  
❌ **Don't forget monitoring** - Mention logging, metrics, alerts  

---

## 🔟 The "10× Load" Mental Model

A powerful interview technique: at every stage of your design, ask yourself **"What breaks if traffic increases 10×?"**

```
Current: 1K QPS
10× → 10K QPS: Add caching layer (Redis), read replicas
10× → 100K QPS: Database sharding, CDN for static content
10× → 1M QPS: Multi-region deployment, queue-based processing, 
               dedicated services for hot paths

For each component, think:
├── Database: Add read replicas → shard → separate read/write DBs
├── Cache: Local cache → Redis → Redis cluster → multi-layer cache
├── App servers: Horizontal scaling behind load balancer
├── Writes: Async via message queue → batch processing
└── Reads: CDN → cache → read replicas → denormalized views
```

This shows interviewers you think about scalability proactively, not reactively. Practice this for every design you study — it builds the intuition MAANG looks for.

**Key questions to ask at each scale jump:**
- Where's the bottleneck now?
- What's the read:write ratio? (Cache-heavy vs queue-heavy)
- Can I make this operation async?
- Do I need strong consistency here, or is eventual OK?
- What's the cost trade-off of this scaling approach?

---

## 📚 Next Steps

1. Study [Design Examples](designs/) - Real-world system designs
2. Learn [Components](components/) - Deep dive into building blocks
3. Practice with mock interviews
4. Read "Designing Data-Intensive Applications" by Martin Kleppmann

---

## 🔗 Related Resources

- [URL Shortener Design](designs/url-shortener.md)
- [Twitter Design](designs/twitter.md)
- [Instagram Design](designs/instagram.md)
- [Distributed Cache Design](designs/distributed-cache.md)
- [Load Balancer Component](components/load-balancer.md)
- [Caching Component](components/caching.md)
- [Database Sharding Component](components/database-sharding.md)
