# Message Queues & Event Streaming

## Overview

Message queues are intermediate buffers that enable asynchronous communication between services. They decouple producers from consumers and handle traffic spikes, failures, and retry logic.

---

## 1️⃣ When to Use Message Queues

### ✅ Use Cases:
1. **Asynchronous Processing**: Send email, generate report (don't block user request)
2. **Load Leveling**: Handle traffic spikes (queue absorbs burst, workers process at steady rate)
3. **Service Decoupling**: Producer doesn't need to know consumer details
4. **Event-Driven Architecture**: Microservices react to events
5. **Guaranteed Delivery**: Persist messages until successfully processed
6. **Fan-out**: One message to multiple consumers (pub/sub)

### ❌ When NOT to Use:
- Real-time request-response (use REST/gRPC instead)
- Need immediate result (synchronous processing)
- Very low latency required (<1ms)

---

## 2️⃣ Message Queue Patterns

### **Pattern 1: Point-to-Point (Work Queue)**

```
Producer -> [Queue] -> Consumer 1
                   -> Consumer 2
                   -> Consumer 3

- One message consumed by ONE consumer
- Load balancing across multiple workers
- Example: Image processing, order fulfillment
```

```text
# Producer (sends work)
FUNCTION createOrder(orderData)
    QUEUE_SEND("order-processing", {
        orderId: orderData.id,
        userId: orderData.userId,
        items: orderData.items
    })

    RETURN { status: "Order received, processing..." }
END FUNCTION

# Consumer (processes work)
ON QUEUE_MESSAGE("order-processing") AS message
    orderId = message.data.orderId
    userId  = message.data.userId
    items   = message.data.items

    # Process order
    processPayment(orderId)
    updateInventory(items)
    sendConfirmationEmail(userId)

    # Acknowledge message (remove from queue)
    ACK(message)
END ON
```

---

### **Pattern 2: Pub/Sub (Fan-Out)**

```
Publisher -> [Topic] -> Subscriber 1 (Email Service)
                    -> Subscriber 2 (Analytics)
                    -> Subscriber 3 (Notification Service)

- One message delivered to ALL subscribers
- Services don't know about each other
- Example: User registration event
```

```text
# Publisher
FUNCTION registerUser(userData)
    DB_CREATE_USER(userData)

    # Publish event (multiple services will react)
    PUBLISH("user.registered", {
        userId: userData.id,
        email: userData.email,
        timestamp: NOW()
    })
END FUNCTION

# Subscriber 1: Email Service
ON EVENT("user.registered") AS event
    sendWelcomeEmail(event.email)
END ON

# Subscriber 2: Analytics
ON EVENT("user.registered") AS event
    trackSignup(event.userId)
END ON

# Subscriber 3: Notification Service
ON EVENT("user.registered") AS event
    sendPushNotification(event.userId, "Welcome!")
END ON
```

---

### **Pattern 3: Request-Reply (RPC over Queue)**

```
Client -> [Request Queue] -> Server
       <- [Reply Queue] <--

- Client waits for response
- Useful for distributed RPC
```

Client sends the request with a `correlationId` and a `replyTo` queue, then blocks waiting for the matching reply. The server processes the request and posts the response to the reply queue keyed by the same `correlationId`.

---

### **Pattern 4: Priority Queue**

```
High Priority Messages -> [Priority Queue] -> Consumer
Normal Priority Messages ->

- Critical messages processed first
- Example: VIP customer orders, alerts
```

Tag each message with a priority (e.g. high for VIP orders) so the broker dequeues higher-priority messages first. Watch for starvation of low-priority messages under sustained high-priority load.

---

### **Pattern 5: Dead Letter Queue (DLQ)**

```
[Main Queue] -> Consumer (fails 3 times) -> [Dead Letter Queue] -> Manual Review

- Failed messages sent to DLQ after max retries
- Prevents infinite retry loops
- Allows investigation of failures
```

```text
ON QUEUE_MESSAGE("order-processing") AS message
    TRY
        processOrder(message.data)
        ACK(message)
    CATCH error
        IF message.retryCount >= 3 THEN
            # Move to dead letter queue
            QUEUE_SEND("order-processing-dlq", message)
            ACK(message)
        ELSE
            # Retry later
            NACK(message)
        END IF
    END TRY
END ON
```

---

## 3️⃣ Popular Message Queue Technologies

### **RabbitMQ**

**Best for**: Traditional message queuing, complex routing

Broker-based AMQP queue: producers publish to an exchange that routes to durable queues; consumers pull with a prefetch limit and manually ACK. A message is redelivered if the consumer dies before ACKing.

**RabbitMQ Features:**
- ✅ AMQP protocol (standard)
- ✅ Complex routing (topic exchanges, headers)
- ✅ Message priority
- ✅ Dead letter queues
- ✅ TTL (time-to-live)
- ❌ Lower throughput (~20K msg/sec per broker)

---

### **Apache Kafka**

**Best for**: High-throughput event streaming, real-time analytics

Append-only partitioned log: producers write records keyed for partitioning; consumers in a group each own a subset of partitions and track their own offset (messages are retained, not deleted on read, so they can be replayed). Ordering is guaranteed only *per partition*, and partitions are distributed across consumer-group members for parallelism.

**Kafka Features:**
- ✅ Extreme throughput (1M+ msg/sec)
- ✅ Horizontal scaling (partitions)
- ✅ Message retention (replay events)
- ✅ Exactly-once semantics
- ✅ Stream processing (Kafka Streams)
- ❌ Complex setup/operations
- ❌ Not ideal for traditional queuing (no message deletion on consume)

---

### **AWS SQS (Simple Queue Service)**

**Best for**: AWS-native, serverless queuing

Fully managed queue: send a message, then long-poll to receive a batch; a received message is hidden by a visibility timeout and must be explicitly deleted once processed (otherwise it reappears for retry). Standard queues are at-least-once + best-effort order; FIFO queues add ordering + dedup at lower throughput.

**SQS Features:**
- ✅ Fully managed (no servers)
- ✅ Auto-scaling
- ✅ Cheap ($0.40 per million requests)
- ✅ FIFO queues available
- ❌ Limited throughput (3K msg/sec standard, 300 msg/sec FIFO)
- ❌ No pub/sub (use SNS instead)

---

### **Redis Streams**

**Best for**: Simple event streaming with Redis infrastructure

Append-only stream in Redis: producers `XADD` entries; consumer groups let multiple consumers split the stream, each reading new entries (blocking) and `XACK`-ing them. In-memory so very fast, but bounded by a single instance and lacking true partitioning.

**Redis Streams Features:**
- ✅ Simple (if already using Redis)
- ✅ Consumer groups
- ✅ Message persistence
- ✅ Fast (in-memory)
- ❌ Limited by single Redis instance throughput
- ❌ No built-in partitioning

---

## 4️⃣ Queue Comparison

| Feature | RabbitMQ | Kafka | SQS | Redis Streams |
|---------|----------|-------|-----|---------------|
| **Throughput** | 20K/sec | 1M+/sec | 3K/sec | 100K/sec |
| **Latency** | <10ms | ~5ms | ~100ms | <1ms |
| **Message Retention** | Until consumed | Days/weeks | 14 days | Indefinite |
| **Message Replay** | ❌ | ✅ | ❌ | ✅ |
| **Ordering** | Per queue | Per partition | FIFO queues | ✅ |
| **Use Case** | Task queues | Event streaming | Serverless | Simple streaming |
| **Complexity** | Medium | High | Low | Low |

---

## 4️⃣.5 Delivery Semantics (Core Trade-off)

How many times a consumer is guaranteed to see a message. This is the central reliability trade-off when choosing/configuring a queue:

| Semantic | Guarantee | Cost / Mechanism | When to use |
|----------|-----------|------------------|-------------|
| **At-most-once** | 0 or 1 delivery; may lose messages | Fire-and-forget, ACK before processing | Metrics, logs where loss is tolerable |
| **At-least-once** ⭐ | ≥1 delivery; may duplicate | ACK after processing + retries; consumer must be **idempotent** | Default for most systems |
| **Exactly-once** | Exactly 1 effective processing | Expensive: dedup + transactional offset/state commit | Financial/critical flows |

Key caveat: Kafka's "exactly-once" is **exactly-once processing *within* Kafka** (consume → transform → produce, with transactional offset commits). It does **not** extend end-to-end to external systems - the moment you write to a database, call a third-party API, or send an email, you're back to at-least-once and need idempotency/dedup on your side. In interviews, default to **at-least-once + idempotent consumers**; only claim exactly-once when you can describe the dedup/transaction mechanism.

---

## 5️⃣ Design Patterns & Best Practices

### **1. Idempotency**

Messages may be delivered more than once (at-least-once delivery). Design consumers to be idempotent.

```text
# BAD: Not idempotent
FUNCTION processOrder(order)
    DB_QUERY("UPDATE inventory SET quantity = quantity - 1 WHERE product_id = ?", order.productId)
END FUNCTION

# GOOD: Idempotent
FUNCTION processOrder(order)
    # Check if already processed
    existing = DB_QUERY("SELECT * FROM processed_orders WHERE order_id = ?", order.id)
    IF existing EXISTS THEN RETURN

    # Process (transaction ensures atomicity)
    BEGIN TRANSACTION tx
        DB_QUERY(tx, "UPDATE inventory SET quantity = quantity - 1 WHERE product_id = ?", order.productId)
        DB_QUERY(tx, "INSERT INTO processed_orders (order_id) VALUES (?)", order.id)
    COMMIT TRANSACTION
END FUNCTION
```

---

### **2. Message Deduplication**

Prevent duplicate messages from being processed. Give each message a stable ID and record processed IDs in a shared store (e.g. Redis with a TTL). On receipt, skip the message if its ID is already present, otherwise process it and record the ID. The TTL bounds the dedup window and garbage-collects old IDs. This is the mechanism behind idempotent consumers under at-least-once delivery.

---

### **3. Exponential Backoff for Retries**

```text
FUNCTION processWithRetry(message, maxRetries = 5)
    FOR attempt FROM 0 TO maxRetries - 1
        TRY
            processMessage(message)
            ACK(message)
            RETURN
        CATCH error
            delay = (2 ^ attempt) * 1000   # 1s, 2s, 4s, 8s, 16s
            PRINT "Retry " + (attempt + 1) + "/" + maxRetries + " after " + delay + "ms"
            SLEEP(delay)
        END TRY
    END FOR

    # Max retries exceeded, send to DLQ
    QUEUE_SEND("failed-messages", message)
    ACK(message)
END FUNCTION
```

---

### **4. Message Batching**

Process multiple messages together for efficiency. Accumulate incoming messages into a buffer and flush when either a size threshold (e.g. 100 messages) or a time threshold (e.g. 5s) is hit, whichever comes first. The whole batch is written in one DB transaction and ACKed together. This amortizes per-message overhead (round-trips, commits) and boosts throughput, at the cost of a little added latency - the classic throughput-vs-latency trade-off.

---

### **5. Circuit Breaker**

Protect downstream services from cascading failures by tripping OPEN after repeated failures and short-circuiting calls until a cooldown elapses. See Circuit Breaker in [Microservices](microservices.md) for the full pattern (canonical location).

---

## 6️⃣ Real-World Example: Video Processing Pipeline

Use case: user uploads a video that must be transcoded into multiple formats.

```
Upload API ──"video-uploaded"──▶ Fan-out ──▶ [transcoding-tasks queue]
                                               │  360p task
                                               │  720p task
                                               │  1080p task
                                               ▼
                                     Transcode worker pool (N workers)
                                               │
                                          "video-transcoded"
                                               ▼
                                     Notification service (all done? notify)
```

Fan-out concept:
- **Publish once, expand to many**: one `video-uploaded` event is fanned out into one transcode task per target quality (360p/720p/1080p), pushed onto a shared work queue.
- **Parallel workers**: a pool of interchangeable workers pulls tasks and transcodes independently, so throughput scales by adding workers (point-to-point work queue).
- **Prioritize**: give the low-res task higher priority so a quick preview is ready first.
- **Per-task resilience**: retry a failed task a few times, then route it to a DLQ instead of blocking the batch.
- **Completion tracking**: each worker emits `video-transcoded`; a collector counts completed qualities and notifies the user once all are done.

---

## Summary

**When to use what:**
- **RabbitMQ**: Traditional task queues, complex routing, low-medium throughput
- **Kafka**: High-throughput event streaming, analytics, message replay needed
- **SQS**: AWS serverless, simple queuing, don't want to manage infrastructure
- **Redis Streams**: Simple streaming, already using Redis, low latency

**Key takeaways:**
- ✅ Decouple services with async messaging
- ✅ Handle failures with retries, DLQ, circuit breakers
- ✅ Design idempotent consumers (messages may be delivered twice)
- ✅ Use batching for efficiency
- ✅ Monitor queue depth (alert if growing = consumers can't keep up)
