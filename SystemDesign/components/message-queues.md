# Message Queues & Event Streaming

## 🎯 Overview

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

```text
# Client
FUNCTION callRemoteService(request)
    correlationId = GENERATE_UUID()
    replyQueue = "reply-" + correlationId

    # Send request
    QUEUE_SEND("service-requests", {
        data: request,
        replyTo: replyQueue,
        correlationId: correlationId
    })

    # Wait for response on the reply queue matching this correlationId
    WAIT FOR message ON QUEUE(replyQueue) WHERE message.correlationId == correlationId
    ACK(message)
    RETURN message.data
END FUNCTION
```

---

### **Pattern 4: Priority Queue**

```
High Priority Messages -> [Priority Queue] -> Consumer
Normal Priority Messages ->

- Critical messages processed first
- Example: VIP customer orders, alerts
```

```text
QUEUE_SEND("order-processing", orderData, {
    priority: IF order.isVIP THEN "high" ELSE "normal"
})
```

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

```text
# RabbitMQ-style message queue (pseudocode)

# Producer
FUNCTION sendMessage()
    connection = CONNECT_TO_BROKER("localhost")
    channel = connection.createChannel()

    queue = "tasks"
    DECLARE_QUEUE(channel, queue, durable = true)

    PUBLISH_TO_QUEUE(channel, queue, serialize({
        task: "resize-image",
        imageUrl: "https://..."
    }), persistent = true)   # persistent = survive broker restart

    PRINT "Message sent"
    channel.close()
    connection.close()
END FUNCTION

# Consumer
FUNCTION consumeMessages()
    connection = CONNECT_TO_BROKER("localhost")
    channel = connection.createChannel()

    queue = "tasks"
    DECLARE_QUEUE(channel, queue, durable = true)
    SET_PREFETCH(channel, 1)   # Process one message at a time

    ON QUEUE_MESSAGE(channel, queue) AS message
        task = deserialize(message.content)
        PRINT "Processing: " + task

        # Simulate work
        processTask(task)

        # Acknowledge (manual ack mode)
        ACK(channel, message)
    END ON
END FUNCTION
```

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

```text
# Kafka event streaming (pseudocode)
# Configure client with brokers: ["kafka1:9092", "kafka2:9092"]

# Producer
FUNCTION produceEvent()
    producer = KAFKA_PRODUCER(brokers = ["kafka1:9092", "kafka2:9092"])
    CONNECT(producer)

    PUBLISH producer TO topic "user-events" WITH
        key   = "user-123"           # Partitioning key
        value = serialize({
            event: "page_view",
            userId: "123",
            page: "/products",
            timestamp: NOW()
        })

    DISCONNECT(producer)
END FUNCTION

# Consumer
FUNCTION consumeEvents()
    consumer = KAFKA_CONSUMER(groupId = "analytics-service")
    CONNECT(consumer)
    SUBSCRIBE(consumer, topic = "user-events", fromBeginning = false)

    FOR EACH message CONSUMED FROM consumer
        event = deserialize(message.value)
        PRINT "Event: " + event

        # Process event
        trackAnalytics(event)
    END FOR
END FUNCTION
```

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

```text
# Managed cloud queue (SQS-style, pseudocode)
QUEUE_URL = "https://queue-service/123456/my-queue"

# Send message
FUNCTION sendMessage()
    QUEUE_SEND(QUEUE_URL,
        body = serialize({ orderId: "123", userId: "456" }),
        delaySeconds = 0)
END FUNCTION

# Receive and process
FUNCTION pollMessages()
    WHILE true
        messages = QUEUE_RECEIVE(QUEUE_URL,
            maxMessages = 10,
            waitTimeSeconds = 20)   # Long polling

        IF messages IS EMPTY THEN CONTINUE

        FOR EACH message IN messages
            data = deserialize(message.body)
            processOrder(data)

            # Delete message once processed
            QUEUE_DELETE(QUEUE_URL, message.receiptHandle)
        END FOR
    END WHILE
END FUNCTION
```

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

```text
# Stream-based queue (Redis Streams-style, pseudocode)

# Producer
FUNCTION addEvent()
    STREAM_APPEND("user-events", id = AUTO, fields = {
        event: "signup",
        userId: "123",
        timestamp: NOW()
    })
END FUNCTION

# Consumer Group
FUNCTION consumeEvents()
    # Create consumer group (start from beginning, create stream if missing)
    STREAM_CREATE_GROUP("user-events", group = "analytics-group", start = "0")

    WHILE true
        # Read new messages for this consumer, blocking up to 5000ms
        results = STREAM_READ_GROUP(
            group = "analytics-group",
            consumer = "consumer-1",
            count = 10,
            blockMillis = 5000,
            stream = "user-events",
            from = "new-messages")

        IF results IS EMPTY THEN CONTINUE

        FOR EACH (stream, messages) IN results
            FOR EACH (id, fields) IN messages
                event = parseFields(fields)
                processEvent(event)

                # Acknowledge
                STREAM_ACK("user-events", group = "analytics-group", id = id)
            END FOR
        END FOR
    END WHILE
END FUNCTION
```

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

Prevent duplicate messages from being processed.

```text
processedMessages = new Set()

FUNCTION processMessage(message)
    messageId = message.id

    # Check if already processed
    IF processedMessages.contains(messageId) THEN
        PRINT "Duplicate message, skipping"
        RETURN
    END IF

    # Process
    handleMessage(message)

    # Mark as processed
    processedMessages.add(messageId)

    # Store in cache with TTL (garbage collect old IDs)
    CACHE_SET("processed:" + messageId, "1", TTL = 86400)
END FUNCTION
```

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

Process multiple messages together for efficiency.

```text
FUNCTION batchProcessor()
    batch = []
    BATCH_SIZE = 100
    BATCH_TIMEOUT = 5000

    # Flush the batch whenever the timeout elapses
    timer = START_TIMER(BATCH_TIMEOUT, THEN processBatch(batch))

    ON QUEUE_MESSAGE("events") AS message
        batch.append(message)

        IF LENGTH(batch) >= BATCH_SIZE THEN
            CANCEL_TIMER(timer)
            processBatch(batch)
            batch = []
            timer = START_TIMER(BATCH_TIMEOUT, THEN processBatch(batch))
        END IF
    END ON
END FUNCTION

FUNCTION processBatch(messages)
    IF LENGTH(messages) == 0 THEN RETURN

    # Process all messages in one database transaction
    BEGIN TRANSACTION tx
        FOR EACH msg IN messages
            DB_QUERY(tx, "INSERT INTO events VALUES (?)", msg.data)
        END FOR
    COMMIT TRANSACTION

    # Acknowledge all
    FOR EACH msg IN messages
        ACK(msg)
    END FOR
END FUNCTION
```

---

### **5. Circuit Breaker**

Protect downstream services from cascading failures.

```text
CLASS CircuitBreaker
    FUNCTION init()
        this.state = "CLOSED"      # CLOSED, OPEN, HALF_OPEN
        this.failureCount = 0
        this.threshold = 5
        this.timeout = 60000       # 1 minute
    END FUNCTION

    FUNCTION execute(fn)
        IF this.state == "OPEN" THEN
            THROW Error("Circuit breaker is OPEN")
        END IF

        TRY
            result = fn()
            this.onSuccess()
            RETURN result
        CATCH error
            this.onFailure()
            THROW error
        END TRY
    END FUNCTION

    FUNCTION onSuccess()
        this.failureCount = 0
        this.state = "CLOSED"
    END FUNCTION

    FUNCTION onFailure()
        this.failureCount = this.failureCount + 1
        IF this.failureCount >= this.threshold THEN
            this.state = "OPEN"
            AFTER this.timeout DO
                this.state = "HALF_OPEN"
                this.failureCount = 0
            END AFTER
        END IF
    END FUNCTION
END CLASS

# Usage
breaker = new CircuitBreaker()

ON QUEUE_MESSAGE("orders") AS message
    TRY
        breaker.execute(FUNCTION() processOrder(message.data) END)
        ACK(message)
    CATCH error
        NACK(message)   # Requeue
    END TRY
END ON
```

---

## 6️⃣ Real-World Example: Video Processing Pipeline

```text
# Use case: User uploads video, needs transcoding to multiple formats

# 1. Upload service publishes event
FUNCTION handleVideoUpload(request)
    videoId = GENERATE_UUID()

    # Upload to object storage
    OBJECT_STORE_UPLOAD(request.file, "videos/raw/" + videoId + ".mp4")

    # Publish to event stream
    PUBLISH TO topic "video-uploaded" WITH
        key   = videoId
        value = serialize({
            videoId: videoId,
            userId: request.user.id,
            originalUrl: "store://videos/raw/" + videoId + ".mp4",
            timestamp: NOW()
        })

    RETURN { videoId: videoId, status: "Processing" }
END FUNCTION

# 2. Transcoding workers consume from stream
ON EVENT("video-uploaded") AS message
    videoId = message.value.videoId
    originalUrl = message.value.originalUrl

    qualities = ["360p", "720p", "1080p"]

    FOR EACH quality IN qualities
        # Add to work queue (for task distribution)
        QUEUE_SEND("transcoding-tasks", {
            videoId: videoId,
            inputUrl: originalUrl,
            outputQuality: quality,
            outputUrl: "store://videos/" + quality + "/" + videoId + ".mp4"
        }, priority = IF quality == "360p" THEN 10 ELSE 5)  # Prioritize low quality (quick preview)
    END FOR
END ON

# 3. Workers process transcoding
ON QUEUE_MESSAGE("transcoding-tasks") AS message
    videoId       = message.data.videoId
    inputUrl      = message.data.inputUrl
    outputQuality = message.data.outputQuality
    outputUrl     = message.data.outputUrl

    TRY
        # Download from object storage
        inputFile = OBJECT_STORE_DOWNLOAD(inputUrl)

        # Transcode to the target quality
        outputFile = TRANSCODE(inputFile, quality = outputQuality)

        # Upload result
        OBJECT_STORE_UPLOAD(outputFile, outputUrl)

        # Publish completion event
        PUBLISH TO topic "video-transcoded" WITH
            value = serialize({
                videoId: videoId,
                quality: outputQuality,
                url: outputUrl,
                timestamp: NOW()
            })

        ACK(message)
    CATCH error
        PRINT_ERROR "Transcoding failed: " + error

        IF message.retryCount < 3 THEN
            NACK(message)   # Retry
        ELSE
            QUEUE_SEND("failed-transcoding", message)
            ACK(message)
        END IF
    END TRY
END ON

# 4. Notification service notifies user
ON EVENT("video-transcoded") AS message
    videoId = message.value.videoId
    quality = message.value.quality

    # Check if all qualities done
    SET_ADD("video:" + videoId + ":completed", quality)
    total = SET_SIZE("video:" + videoId + ":completed")

    IF total == 3 THEN
        # All done, notify user
        sendPushNotification(userId, "Your video is ready!")
    END IF
END ON
```

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
