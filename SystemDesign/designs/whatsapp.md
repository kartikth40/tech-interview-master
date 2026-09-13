# WhatsApp Messaging System Design
> **SDE-2 Interview Ready** | 45-minute format

## 🎯 Problem Statement

Design a real-time messaging platform like WhatsApp that supports:
- One-to-one messaging
- Group chats
- Message delivery guarantees
- End-to-end encryption (E2EE)
- Media sharing (images, videos)
- Online/offline status

**Key Requirements:**
- Support 2B users
- Real-time message delivery (<1 second)
- 100B messages/day
- End-to-end encryption
- 99.99% availability

---

## 1️⃣ Requirements Clarification

### Functional Requirements:

1. **Messaging**
   - Send/receive text messages (one-to-one)
   - Group chats (up to 256 members)
   - Delivery receipts (sent, delivered, read)
   - Message history

2. **Media Sharing**
   - Images, videos, documents
   - Upload to cloud, share links

3. **Status**
   - Online/offline/last seen
   - Typing indicators

4. **Encryption**
   - End-to-end encryption (E2EE)
   - Only sender and receiver can read

### Non-Functional Requirements:
- **Scale:** 2B users, 100B messages/day
- **Latency:** <1 second message delivery
- **Availability:** 99.99% uptime
- **Consistency:** Eventually consistent (messages may arrive out of order briefly)
- **Security:** End-to-end encryption

### Out of Scope:
- Voice/video calls
- Stories/Status updates
- Payments

---

## 2️⃣ Capacity Estimation

```
Users: 2B total, 500M daily active users (DAU)
Messages per day: 100B
Messages per second:
- Average: 100B / 86400 = 1.15M messages/sec
- Peak: 1.15M × 3 = 3.5M messages/sec

Storage:
Per message: 1 KB (text + metadata)
Daily: 100B × 1 KB = 100 TB/day
1 year: 100 TB × 365 = 36.5 PB

Media (images/videos):
- 30% messages have media
- Average size: 500 KB
- Daily: 30B × 500 KB = 15 PB/day

Bandwidth:
- Outgoing: 1.15M msg/sec × 1 KB = 1.15 GB/sec
- Peak: 3.5 GB/sec

WebSocket Connections:
- Active users: 500M
- Each user has 1 persistent WebSocket connection
- Total: 500M concurrent connections
```

---

## 3️⃣ API Design

### Core APIs

```text
# 1. Send Message (WebSocket)
Message {
  type: "send_message"
  message_id: "msg_abc123"        # Client-generated (for idempotency)
  from: "user_123"
  to: "user_456"                  # or group_id
  content: "Hello!"
  encrypted_content: "AES256_encrypted_base64"   # E2EE
  timestamp: 1676464123
  reply_to: "msg_xyz789"          # optional
}

# 2. Receive Message (WebSocket push)
Message {
  type: "new_message"
  message_id: "msg_abc123"
  from: "user_123"
  to: "user_456"
  encrypted_content: "AES256_encrypted_base64"
  timestamp: 1676464123
}

# 3. Delivery Receipt (WebSocket)
Message {
  type: "receipt"
  message_id: "msg_abc123"
  status: "delivered"             # sent, delivered, read
  timestamp: 1676464125
}

# 4. Upload Media (REST API)
POST /v1/media/upload
Headers: { Authorization: "Bearer <token>" }
Body: (multipart/form-data)
  file: <image.jpg>

Response:
  media_id: "media_xyz789"
  url: "https://cdn.whatsapp.com/media/xyz789.jpg"
  thumbnail_url: "https://cdn.whatsapp.com/media/xyz789_thumb.jpg"
  size: 524288                    # bytes
  mime_type: "image/jpeg"

# 5. Fetch Message History (REST API)
GET /v1/messages?user_id=user_456&before=msg_abc123&limit=50

Response:
  messages: [
    {
      message_id: "msg_abc123"
      from: "user_123"
      to: "user_456"
      encrypted_content: "..."
      timestamp: 1676464123
      status: "read"
    }
  ]
  has_more: true

# 6. Create Group (REST API)
POST /v1/groups
Body:
  name: "Family Group"
  members: ["user_123", "user_456", "user_789"]
  admin: "user_123"

Response:
  group_id: "group_abc123"
  name: "Family Group"
  members: [...]
  created_at: 1676464123
```

---

## 4️⃣ Database Design

### Cassandra (Messages - Time-series, High Write)

```sql
-- Messages table (partitioned by user)
CREATE TABLE messages (
  user_id TEXT,
  message_id TIMEUUID,
  from_user_id TEXT,
  to_user_id TEXT,
  group_id TEXT,
  encrypted_content BLOB,
  timestamp TIMESTAMP,
  status TEXT,  -- sent, delivered, read
  PRIMARY KEY (user_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);

-- Query: Get recent messages for user
SELECT * FROM messages 
WHERE user_id = 'user_123' 
ORDER BY message_id DESC 
LIMIT 50;
```

### PostgreSQL (Users, Groups)

```sql
-- Users
CREATE TABLE users (
  id VARCHAR(50) PRIMARY KEY,
  phone VARCHAR(15) UNIQUE,
  username VARCHAR(100),
  public_key TEXT,  -- For E2EE
  last_seen TIMESTAMP,
  status VARCHAR(20),  -- online, offline
  created_at TIMESTAMP
);

-- Groups
CREATE TABLE groups (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255),
  created_by VARCHAR(50) REFERENCES users(id),
  created_at TIMESTAMP
);

-- Group Members
CREATE TABLE group_members (
  group_id VARCHAR(50) REFERENCES groups(id),
  user_id VARCHAR(50) REFERENCES users(id),
  role VARCHAR(20),  -- admin, member
  joined_at TIMESTAMP,
  PRIMARY KEY (group_id, user_id)
);
```

### Redis (Online Status, WebSocket Mapping)

```text
# Online status
Key: user:{user_id}:status
Value: "online" | "offline"
TTL: None

# Last seen
Key: user:{user_id}:last_seen
Value: timestamp
TTL: None

# WebSocket server mapping (for routing messages)
Key: user:{user_id}:ws_server
Value: "ws-server-1.whatsapp.com"
TTL: None (updated when connection changes)

# Undelivered messages queue
Key: user:{user_id}:pending_messages
Type: List
Value: [message_id1, message_id2, ...]
```

---

## 5️⃣ High-Level Design

```
┌─────────────┐
│   Users     │
│  (Mobile)   │
└──────┬──────┘
       │
       │ (Persistent WebSocket)
       ▼
┌──────────────────────────────────────┐
│   Load Balancer (WebSocket-aware)   │
│   - Sticky sessions                  │
│   - Health checks                    │
└──────┬───────────────────────────────┘
       │
   ┌───┴───┬─────────┬─────────┐
   ▼       ▼         ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ WS-1 │ │ WS-2 │ │ WS-3 │ │WS-100│  WebSocket Servers
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘  (500M connections / 5000/server = 100K servers)
   │        │        │        │
   └────────┴────────┴────────┘
            │
            ▼
┌──────────────────────────────────────┐
│      Message Service                 │
│                                      │
│  1. Validate message                 │
│  2. Encrypt (E2EE)                   │
│  3. Find recipient's WS server       │
│  4. Route message                    │
│  5. Store in Cassandra               │
│  6. Send delivery receipt            │
└──────┬───────────────────────────────┘
       │
   ┌───┴────┬──────────┐
   ▼        ▼          ▼
┌─────┐ ┌────────┐ ┌──────────┐
│Redis│ │Cassandra│ │PostgreSQL│
│     │ │         │ │          │
│-WS  │ │-Messages│ │- Users   │
│ map │ │         │ │- Groups  │
│-Status│ │       │ │          │
└─────┘ └────────┘ └──────────┘
       │
       ▼
┌──────────────────────────────────────┐
│      CDN (Media)                     │
│  - Images, videos                    │
│  - S3 + CloudFront                   │
└──────────────────────────────────────┘
```

**Data Flow:**
1. User A sends message to User B via WebSocket
2. Message arrives at WebSocket Server 1
3. Message Service validates and encrypts
4. Lookup User B's WebSocket server (Redis: `user:B:ws_server`)
5. If User B is online → Route to their WebSocket server → Push message
6. If User B is offline → Store in pending queue (Redis)
7. Store message in Cassandra (both users' partitions)
8. Send delivery receipt to User A

---

## 6️⃣ Low-Level Design

### Class Diagram

```
┌──────────────────────────────┐
│    WebSocketServer           │
├──────────────────────────────┤
│ - connections: Map<userId, WS>│
│ - messageService             │
├──────────────────────────────┤
│ + onConnect(userId)          │
│ + onMessage(msg)             │
│ + onDisconnect(userId)       │
│ + sendToUser(userId, msg)    │
└──────┬───────────────────────┘
       │
       │ uses
       ▼
┌──────────────────────────────┐
│    MessageService            │
├──────────────────────────────┤
│ - db: CassandraClient        │
│ - cache: RedisClient         │
│ - router: MessageRouter      │
├──────────────────────────────┤
│ + send(from, to, content)    │
│ + receive(messageId)         │
│ + markDelivered(messageId)   │
└──────────────────────────────┘
       │
       │ uses
       ▼
┌──────────────────────────────┐
│    MessageRouter             │
├──────────────────────────────┤
│ + findRecipientServer(userId)│
│ + route(message, server)     │
└──────────────────────────────┘
```

### Sequence Diagram (Send Message)

```
UserA   WS-Server1   MessageService   Redis   Cassandra   WS-Server2   UserB
  │         │              │            │         │            │         │
  │─Send───>│              │            │         │            │         │
  │         │              │            │         │            │         │
  │         │─Process─────>│            │         │            │         │
  │         │              │            │         │            │         │
  │         │              │─Find UserB─>│        │            │         │
  │         │              │<─server────│         │            │         │
  │         │              │            │         │            │         │
  │         │              │─Store─────────────────>│          │         │
  │         │              │            │         │            │         │
  │         │              │─Route──────────────────────────────────────>│
  │         │              │            │         │            │<────────│
  │         │<─Receipt────│            │         │            │         │
  │<────────│              │            │         │            │         │
```

### State Machine (Message Status)

```
┌──────┐
│ SENT │ (Sent from client)
└───┬──┘
    │
    ▼
┌───────────┐
│ DELIVERED │ (Received by recipient's device)
└─────┬─────┘
      │
      ▼
┌──────┐
│ READ │ (Viewed by recipient)
└──────┘
```

### Design Patterns

1. **Observer Pattern** - WebSocket connections observe message events
2. **Pub/Sub Pattern** - Message routing across WebSocket servers (Redis Pub/Sub)
3. **Strategy Pattern** - Different encryption strategies (E2EE, transport encryption)

---

## 7️⃣ Deep Dives

### Deep Dive 1: WebSocket Server Architecture

**Challenge:** Manage 500M concurrent WebSocket connections

**Solution:** Horizontal scaling + Connection pooling

**Approach:**
```text
CLASS WebSocketServer

  # State
  connections = empty Map      # userId -> WebSocket connection
  serverId    = config.SERVER_ID

  FUNCTION onConnect(ws, userId)
    # 1. Store connection
    connections[userId] = ws

    # 2. Register in Redis (for routing)
    redis.set("user:" + userId + ":ws_server", serverId)
    redis.set("user:" + userId + ":status", "online")

    # 3. Send pending messages (queued while offline)
    pending = redis.listRange("user:" + userId + ":pending", 0, -1)
    FOR EACH msgId IN pending
      message = getMessageFromDB(msgId)
      ws.send(message)
    END FOR
    redis.delete("user:" + userId + ":pending")

    # 4. Notify contacts (user came online)
    notifyContacts(userId, { status: "online" })
  END FUNCTION

  FUNCTION onMessage(ws, data)
    msg = parse(data)
    # Route to message service
    messageService.send(msg)
  END FUNCTION

  FUNCTION onDisconnect(userId)
    # 1. Remove connection
    connections.remove(userId)

    # 2. Update Redis
    redis.set("user:" + userId + ":status", "offline")
    redis.set("user:" + userId + ":last_seen", currentTime())
    redis.delete("user:" + userId + ":ws_server")

    # 3. Notify contacts
    notifyContacts(userId, { status: "offline" })
  END FUNCTION

  FUNCTION sendToUser(userId, message)
    ws = connections[userId]

    IF ws EXISTS THEN
      ws.send(message)
    ELSE
      # User not connected to this server -> add to pending queue
      redis.listPushRight("user:" + userId + ":pending", message.id)
    END IF
  END FUNCTION

END CLASS
```

**Scaling:**
- 500M connections / 5000 connections per server = **100,000 servers**
- Use AWS Auto Scaling Groups
- Each server has 8 GB RAM (5000 connections × 1.5 MB/connection = 7.5 GB)

**Trade-offs:**
- ✅ Horizontally scalable
- ✅ Fault tolerant (one server down = 5K users reconnect)
- ❌ High infrastructure cost
- ❌ Complex routing (need Redis for WS server mapping)

---

### Deep Dive 2: Message Routing

**Challenge:** Route message from User A (on WS-Server-1) to User B (on WS-Server-2)

**Solution:** Redis Pub/Sub + Server-to-Server communication

**Approach:**
```text
CLASS MessageService

  FUNCTION send(from, to, content)
    # 1. Generate message ID
    messageId = generateUUID()

    # 2. Store in Cassandra (sender's partition)
    cassandra.execute(
      "INSERT INTO messages (user_id, message_id, from_user_id, to_user_id, encrypted_content, timestamp, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
      [from, messageId, from, to, content, currentTime(), "sent"]
    )

    # 3. Store in Cassandra (recipient's partition)
    cassandra.execute(
      "INSERT INTO messages (user_id, message_id, from_user_id, to_user_id, encrypted_content, timestamp, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
      [to, messageId, from, to, content, currentTime(), "sent"]
    )

    # 4. Find recipient's WebSocket server
    recipientServer = redis.get("user:" + to + ":ws_server")

    IF recipientServer EXISTS THEN
      # 5. User is online -> push via Redis Pub/Sub
      redis.publish("ws:" + recipientServer, {
        type: "new_message"
        to: to
        message: {
          message_id: messageId
          from: from
          encrypted_content: content
          timestamp: currentTime()
        }
      })
    ELSE
      # 6. User is offline -> queue message
      redis.listPushRight("user:" + to + ":pending", messageId)
    END IF

    # 7. Send delivery receipt to sender
    RETURN { message_id: messageId, status: "sent" }
  END FUNCTION

END CLASS

# WebSocket server subscribes to its channel
redis.subscribe("ws:" + serverId)

ON redis message (channel, message)
  data   = parse(message)
  userId = data.to
  ws     = connections[userId]

  IF ws EXISTS THEN
    ws.send(data.message)
    # Send delivered receipt
    sendReceipt(data.message.message_id, "delivered")
  END IF
END ON
```

**Trade-offs:**
- ✅ Fast routing via Redis Pub/Sub (<10ms)
- ✅ Decoupled architecture (servers don't need to know each other)
- ❌ Redis is single point of failure (use Redis Sentinel)
- ❌ Message loss risk if Redis fails (mitigated by Cassandra persistence)

**Alternative:** Server-to-server HTTP/gRPC (more reliable but slower)

---

### Deep Dive 3: End-to-End Encryption (E2EE)

**Challenge:** Ensure only sender and receiver can read messages

**Solution:** Signal Protocol (used by WhatsApp)

**High-level Flow:**
```
1. Key Exchange (one-time setup):
   - User A generates key pair (public_key_A, private_key_A)
   - User B generates key pair (public_key_B, private_key_B)
   - Public keys stored on server
   - Private keys never leave device

2. Sending Message (User A → User B):
   - User A fetches User B's public key from server
   - User A encrypts message with User B's public key
   - Encrypted message sent to server
   - Server cannot decrypt (doesn't have private key)
   - Only User B can decrypt with private_key_B

3. Server's Role:
   - Store encrypted messages (cannot read)
   - Deliver to recipient
   - Distribute public keys
```

**Pseudo-code:**
```text
# User A (Sender)
FUNCTION sendEncryptedMessage(content, recipientId)
  # 1. Fetch recipient's public key
  recipientPublicKey = fetchPublicKey(recipientId)

  # 2. Encrypt message
  encryptedContent = encrypt(content, recipientPublicKey)

  # 3. Send to server
  sendMessage({
    from: myUserId
    to: recipientId
    encrypted_content: encryptedContent
  })
END FUNCTION

# User B (Receiver)
FUNCTION receiveEncryptedMessage(message)
  # 1. Decrypt with private key (stored on device)
  decryptedContent = decrypt(
    message.encrypted_content,
    myPrivateKey        # Never sent to server
  )

  RETURN decryptedContent
END FUNCTION
```

**Trade-offs:**
- ✅ Maximum privacy (server can't read messages)
- ✅ Compliant with privacy regulations
- ❌ Cannot search messages on server (client-side only)
- ❌ Cannot recover messages if device is lost (unless backed up with key)
- ❌ Key exchange complexity

**Note for Interview:** Don't go deep into Signal Protocol crypto details. High-level understanding is enough for SDE-2.

---

## 8️⃣ Bottlenecks & Optimizations

### Bottlenecks:

1. **WebSocket Server Capacity**
   - Problem: Each server handles 5K connections
   - Solution: Auto-scale to 100K servers, use spot instances (cheaper)

2. **Message Fanout (Group Messages)**
   - Problem: Message to 256-member group = 256 writes
   - Solution: Async fanout worker, batch writes to Cassandra

3. **Redis Single Point of Failure**
   - Problem: Redis stores WS server mappings
   - Solution: Redis Sentinel cluster (3-5 nodes)

4. **Cassandra Write Load**
   - Problem: 1.15M writes/sec
   - Solution: Cassandra is optimized for writes (LSM trees), scale to 500+ nodes

### Optimizations:

**1. Message Compression:**
```
Compress text messages with gzip before encryption
Saves ~60% bandwidth
```

**2. CDN for Media:**
```
Store images/videos in S3
Serve via CloudFront CDN
Reduces backend load by 90%
```

**3. Lazy Loading:**
```
Load last 50 messages on open chat
Fetch older messages on scroll (pagination)
```

**4. Delta Updates:**
```
Instead of sending full message list, send only new messages
Reduces data transfer
```

---

## 9️⃣ Interview Tips

### What to Focus on (45-min):

1. **Clarify requirements** (5 min)
   - Scale? Real-time? E2EE?
   - One-to-one vs groups?

2. **Draw high-level design** (15 min)
   - WebSocket servers for real-time
   - Cassandra for message storage
   - Redis for online status & routing

3. **Deep dive 1: WebSocket scaling** (10 min)
   - 500M connections = 100K servers
   - Connection mapping in Redis
   - Pending message queue for offline users

4. **Deep dive 2: Message routing** (5 min)
   - Redis Pub/Sub for cross-server routing
   - Cassandra for persistence

5. **Discuss E2EE** (5 min)
   - Signal Protocol (high-level)
   - Server can't read messages

### Common Follow-ups:

**Q: How do you handle group messages (256 members)?**
A: Fanout to all members asynchronously, batch writes to Cassandra, use message queue (Kafka) for buffering

**Q: What if a WebSocket server crashes?**
A: Users reconnect to another server (via load balancer), fetch pending messages from Redis queue

**Q: How do you show "User is typing..."?**
A: Send ephemeral event via WebSocket (not stored in DB), recipient shows indicator for 3 seconds

**Q: How do you ensure message ordering?**
A: Use timestamp + message ID (TIMEUUID in Cassandra), client sorts messages by timestamp

**Q: How do you optimize for slow networks (India)?**
A: Compress messages, show optimistic UI (send before server confirms), queue messages offline

---

## Summary

**Key Design Decisions:**
1. ✅ **WebSocket** for real-time bidirectional communication
2. ✅ **Cassandra** for high write throughput (time-series messages)
3. ✅ **Redis Pub/Sub** for cross-server message routing
4. ✅ **E2EE** for privacy (Signal Protocol)
5. ✅ **CDN** for media delivery (S3 + CloudFront)

**Tech Stack:**
- Backend: Node.js/Go (WebSocket support)
- Database: Cassandra (messages), PostgreSQL (users/groups)
- Cache: Redis (online status, WS mapping)
- Queue: Kafka (group message fanout)
- Storage: AWS S3 (media)
- CDN: CloudFront
