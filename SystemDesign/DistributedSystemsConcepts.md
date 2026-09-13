# Distributed Systems Concepts

## Why This Matters

Every system design interview at SDE-2 level will probe your understanding of distributed systems. These concepts come up in almost every design - knowing them deeply separates good answers from great ones.

---

## 1️⃣ CAP Theorem (Deep Dive)

> In a distributed system, you can only guarantee 2 of 3: **Consistency**, **Availability**, **Partition Tolerance**.

Since network partitions are unavoidable in real distributed systems, the real choice is **CP vs AP**.

```
CP (Consistency + Partition Tolerance):
- All nodes see the same data at the same time
- System may reject requests during partition
- Examples: HBase, Zookeeper, MongoDB (strong consistency mode)
- Use when: Banking, inventory, anything where stale data = wrong

AP (Availability + Partition Tolerance):
- System always responds (may return stale data)
- Nodes may diverge during partition, sync later
- Examples: Cassandra, DynamoDB, CouchDB
- Use when: Social feeds, analytics, anything where eventual consistency is OK
```

### PACELC Extension
CAP only covers partition scenarios. PACELC adds the normal case:

```
If Partition (P):
  Choose between Availability (A) or Consistency (C)
Else (E - normal operation):
  Choose between Latency (L) or Consistency (C)

Examples:
- DynamoDB: PA/EL (available during partition, low latency normally)
- HBase: PC/EC (consistent during partition, consistent normally)
- Cassandra: PA/EL (tunable consistency)
```

---

## 2️⃣ Consistency Models

From strongest to weakest:

### Strong Consistency
> Every read returns the most recent write.

```
Write(x=5) → Read(x) always returns 5
Used in: Banking, inventory, leader election
Cost: Higher latency (must coordinate across nodes)
```

### Linearizability
> Operations appear instantaneous and in real-time order.

```
Most strict form of strong consistency.
Used in: Distributed locks, atomic counters
Example: Zookeeper, etcd
```

### Sequential Consistency
> All nodes see operations in the same order (not necessarily real-time).

```
Write(x=1) then Write(x=2) → all nodes see x=1 before x=2
But the timing may differ from wall clock
```

### Eventual Consistency
> Given no new updates, all replicas will eventually converge.

```
Write(x=5) → some reads may return old value temporarily
Eventually all nodes return x=5
Used in: DNS, social media feeds, shopping carts
Cost: Application must handle stale reads
```

### Read-Your-Writes Consistency
> After a write, the same client always reads the updated value.

```
User posts a tweet → they always see their own tweet immediately
Other users may see it later (eventual)
Implementation: Route user's reads to the same replica they wrote to
```

---

## 3️⃣ Replication

### Leader-Follower (Master-Slave)

```
Architecture:
  Leader ──writes──> Follower 1
         ──writes──> Follower 2
         ──writes──> Follower 3

Reads: From followers (scale reads)
Writes: Only to leader (single write path)

Pros:
✅ Simple, widely used
✅ Read scaling (add followers)
✅ Failover: promote follower to leader

Cons:
❌ Leader is bottleneck for writes
❌ Replication lag (followers may be behind)
❌ Failover is complex (split-brain risk)
```

### Multi-Leader (Multi-Master)

```
Architecture:
  Leader 1 ←──sync──→ Leader 2
  (DC East)            (DC West)

Pros:
✅ Write to nearest datacenter (low latency)
✅ No single point of failure for writes

Cons:
❌ Write conflicts (both leaders accept conflicting writes)
❌ Complex conflict resolution needed
❌ Hard to implement correctly

Conflict Resolution:
- Last Write Wins (LWW): Use timestamp, latest wins (risk: data loss)
- Merge: Combine both values (works for counters, sets)
- Custom: Application-level resolution
```

### Leaderless (Dynamo-style)

```
Architecture:
  Client ──writes──> Any N nodes
  Client ──reads──>  Any R nodes

Quorum: W + R > N ensures consistency
  N=3, W=2, R=2: Strong consistency
  N=3, W=1, R=1: High availability, eventual consistency

Examples: Cassandra, DynamoDB, Riak

Pros:
✅ No single point of failure
✅ Highly available
✅ Tunable consistency

Cons:
❌ Complex to reason about
❌ Possible to read stale data
```

---

## 4️⃣ Consensus Algorithms

### Raft (Easier to understand than Paxos)

```
Used in: etcd, CockroachDB, TiKV

Roles:
- Leader: Handles all client requests
- Follower: Replicates leader's log
- Candidate: Trying to become leader

Leader Election:
1. Follower times out (no heartbeat from leader)
2. Becomes Candidate, increments term, votes for self
3. Sends RequestVote to all nodes
4. If majority votes → becomes Leader
5. Sends heartbeats to prevent new elections

Log Replication:
1. Client sends command to Leader
2. Leader appends to log, sends AppendEntries to followers
3. Once majority acknowledge → commit
4. Leader responds to client
```

### Paxos (Conceptual)

```
Two phases:
Phase 1 (Prepare):
  Proposer → "I want to propose, promise not to accept lower proposals"
  Acceptors → "OK, I promise" (if higher than seen before)

Phase 2 (Accept):
  Proposer → "Accept this value"
  Acceptors → "Accepted" (if still promised)

Once majority accept → value is chosen
```

---

## 5️⃣ Distributed Transactions

### Two-Phase Commit (2PC)

```
Coordinator orchestrates transaction across multiple nodes.

Phase 1 (Prepare):
  Coordinator → "Can you commit?" → All participants
  Participants → "Yes" or "No"

Phase 2 (Commit/Abort):
  If all Yes → Coordinator → "Commit" → All participants
  If any No  → Coordinator → "Abort"  → All participants

Problems:
❌ Blocking: If coordinator crashes after Phase 1, participants wait forever
❌ Single point of failure (coordinator)
❌ Slow (2 round trips)
```

### Saga Pattern (Preferred for microservices)

```
Break transaction into local transactions with compensating actions.

Example: Book flight + hotel + car
  1. Book flight (success) → emit FlightBooked event
  2. Book hotel (success) → emit HotelBooked event
  3. Book car (FAIL) → emit CarBookingFailed event
  4. Compensate: Cancel hotel → emit HotelCancelled
  5. Compensate: Cancel flight → emit FlightCancelled

Two styles:
Choreography: Each service listens to events, acts, emits next event
  Pros: Decoupled, simple
  Cons: Hard to track overall state

Orchestration: Central saga orchestrator tells each service what to do
  Pros: Clear flow, easy to monitor
  Cons: Orchestrator is a dependency
```

---

## 6️⃣ Distributed Caching

Caching strategies (cache-aside, write-through, write-behind), eviction policies (LRU/LFU/TTL),
cache stampede, hot keys, and **consistent hashing** for distributing keys across cache nodes are
covered in depth in the dedicated component doc:

➡️ **[components/caching.md](components/caching.md)**

Two distributed-systems points worth remembering here:
- **Consistent hashing** remaps only ~K/N keys when a node is added/removed (vs `hash(key) % N`, which remaps almost everything). Virtual nodes even out the distribution.
- **Cache + DB consistency** is a write-strategy trade-off: write-through (consistent, slower writes) vs write-behind (fast writes, risk of loss) vs cache-aside + invalidation (simple, brief staleness).

---

## 7️⃣ Message Queues & Event Streaming

### Message Queue vs Event Stream

```
Message Queue (RabbitMQ, SQS):
  - Message consumed once, then deleted
  - Point-to-point or pub/sub
  - Good for: Task queues, job processing

Event Stream (Kafka):
  - Events retained for configurable period
  - Multiple consumers can read same event
  - Ordered within partition
  - Good for: Event sourcing, audit logs, stream processing
```

### Kafka Deep Dive

```
Concepts:
  Topic: Named stream of events
  Partition: Ordered, immutable log (unit of parallelism)
  Offset: Position of message in partition
  Consumer Group: Set of consumers sharing work

Guarantees:
  - At-least-once delivery (default)
  - Exactly-once (with transactions, more complex)
  - Ordering within partition (not across partitions)

Scaling:
  - More partitions = more parallelism
  - Consumers in group = partitions / consumers (each consumer gets some partitions)
  - Replication factor = fault tolerance

Producer:
  - Partition key determines which partition
  - Same key → same partition → ordered for that key
```

```text
# Kafka producer (pseudocode)
producer = KAFKA_PRODUCER(brokers = ["kafka:9092"])

PUBLISH producer TO topic "order-events" WITH
    key   = orderId          # Same order -> same partition -> ordered
    value = serialize({ orderId, status: "placed", userId })

# Kafka consumer (pseudocode)
consumer = KAFKA_CONSUMER(groupId = "order-processor")
SUBSCRIBE(consumer, topic = "order-events")

FOR EACH message CONSUMED FROM consumer
    event = deserialize(message.value)
    processOrder(event)
END FOR
```

---

## 8️⃣ Distributed Locks

### When You Need Them
- Prevent double-booking (hotel rooms, seats)
- Ensure only one instance runs a cron job
- Atomic read-modify-write across services

### Redis-Based Lock (Redlock)

```text
CLASS DistributedLock
    FUNCTION init(store)
        this.store = store   # distributed key-value store (e.g. Redis)
    END FUNCTION

    FUNCTION acquire(key, ttlMs)
        lockValue = NOW() + "-" + RANDOM()

        # Atomic set-if-not-exists with expiry
        result = STORE_SET_IF_ABSENT(this.store, "lock:" + key, lockValue, expiryMillis = ttlMs)

        IF result == SUCCESS THEN
            RETURN lockValue   # Lock acquired
        END IF
        RETURN null            # Lock not acquired
    END FUNCTION

    FUNCTION release(key, lockValue)
        # Atomic check-and-delete: only delete if we still own the lock
        ATOMIC
            IF STORE_GET(this.store, "lock:" + key) == lockValue THEN
                STORE_DELETE(this.store, "lock:" + key)
            END IF
        END ATOMIC
    END FUNCTION
END CLASS

# Usage
FUNCTION bookSeat(seatId, userId)
    lock = new DistributedLock(store)
    lockValue = lock.acquire("seat:" + seatId, 5000)   # 5s TTL

    IF lockValue IS null THEN
        THROW Error("Seat is being booked by someone else")
    END IF

    TRY
        seat = DB_GET_SEAT(seatId)
        IF seat.booked THEN THROW Error("Seat already booked")
        DB_BOOK_SEAT(seatId, userId)
    FINALLY
        lock.release("seat:" + seatId, lockValue)
    END TRY
END FUNCTION
```

---

## 9️⃣ Failure Patterns & Resilience

### Circuit Breaker

```text
CLASS CircuitBreaker
    FUNCTION init(threshold = 5, timeout = 60000)
        this.failureCount = 0
        this.threshold = threshold    # Failures before opening
        this.timeout = timeout        # Time before trying again
        this.state = "CLOSED"         # CLOSED, OPEN, HALF_OPEN
        this.nextAttempt = NOW()
    END FUNCTION

    FUNCTION call(fn)
        IF this.state == "OPEN" THEN
            IF NOW() < this.nextAttempt THEN
                THROW Error("Circuit breaker is OPEN")
            END IF
            this.state = "HALF_OPEN"
        END IF

        TRY
            result = fn()
            this.onSuccess()
            RETURN result
        CATCH err
            this.onFailure()
            THROW err
        END TRY
    END FUNCTION

    # private
    FUNCTION onSuccess()
        this.failureCount = 0
        this.state = "CLOSED"
    END FUNCTION

    # private
    FUNCTION onFailure()
        this.failureCount = this.failureCount + 1
        IF this.failureCount >= this.threshold THEN
            this.state = "OPEN"
            this.nextAttempt = NOW() + this.timeout
        END IF
    END FUNCTION
END CLASS

# Usage
breaker = new CircuitBreaker(5, 30000)

FUNCTION callPaymentService(data)
    RETURN breaker.call(FUNCTION() RETURN paymentAPI.charge(data) END)
END FUNCTION
```

### Retry with Exponential Backoff

```text
FUNCTION withRetry(fn, maxRetries = 3, baseDelay = 100)
    FOR attempt FROM 0 TO maxRetries
        TRY
            RETURN fn()
        CATCH err
            IF attempt == maxRetries THEN THROW err

            # Exponential backoff with jitter
            delay = baseDelay * (2 ^ attempt) + RANDOM() * 100
            SLEEP(delay)
        END TRY
    END FOR
END FUNCTION

# Usage
result = withRetry(FUNCTION() RETURN externalAPI.getData() END, 3, 200)
# Retries at: 200ms, 400ms, 800ms (+ jitter)
```

### Bulkhead Pattern

```
Isolate failures - don't let one service take down everything.

Example: Separate thread pools for different services
  - Payment service: 20 threads
  - Notification service: 10 threads
  - Analytics service: 5 threads

If analytics is slow → only analytics threads are blocked
Payment and notifications continue working
```

---

## Observability

### The Three Pillars

```
Metrics: Numerical measurements over time
  - Request rate, error rate, latency (RED metrics)
  - CPU, memory, disk (USE metrics)
  - Tools: Prometheus + Grafana

Logs: Timestamped records of events
  - Structured logging (JSON) > unstructured
  - Log levels: DEBUG, INFO, WARN, ERROR
  - Tools: ELK Stack (Elasticsearch, Logstash, Kibana)

Traces: End-to-end request journey across services
  - Trace ID propagated through all services
  - Shows where time is spent
  - Tools: Jaeger, Zipkin, AWS X-Ray
```

### Key Metrics to Track

```
RED Method (for services):
  Rate: Requests per second
  Errors: Error rate (%)
  Duration: Latency (P50, P95, P99)

USE Method (for resources):
  Utilization: % time resource is busy
  Saturation: Queue length
  Errors: Error count

SLI/SLO/SLA:
  SLI (Service Level Indicator): Actual measurement (e.g., 99.5% uptime)
  SLO (Service Level Objective): Target (e.g., 99.9% uptime)
  SLA (Service Level Agreement): Contract with penalty (e.g., 99.9% or refund)
```

---

## Quick Reference

| Concept | Key Point | Example |
|---------|-----------|---------|
| CAP Theorem | CP vs AP trade-off | MongoDB (CP) vs Cassandra (AP) |
| Eventual Consistency | Replicas converge over time | DNS, social feeds |
| Leader-Follower | Writes to leader, reads from followers | MySQL replication |
| Saga Pattern | Distributed transactions via compensation | Booking systems |
| Consistent Hashing | Minimize remapping when nodes change | Redis cluster |
| Circuit Breaker | Stop calling failing services | Payment gateway |
| Raft | Leader election + log replication | etcd, CockroachDB |

---

## Related Resources

- [System Design Guide](SystemDesignGuide.md)
- [Message Queues Component](components/message-queues.md)
- [Caching Component](components/caching.md)
- [Database Sharding Component](components/database-sharding.md)
