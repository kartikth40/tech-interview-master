# Distributed Message Queue System Design (Kafka-style)
> **SDE-2 Interview Ready** | 45-minute format

## Problem Statement

Design a distributed message queue / streaming platform like Kafka: producers publish messages,
consumers read them, with durability, ordering, and horizontal scale.

> This is the **design-level** treatment. For the "when to use a queue / queue vs pub-sub" concept
> overview, see the component doc: [message-queues.md](../components/message-queues.md).

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. Producers publish messages to a **topic**; consumers subscribe and read.
2. Durable storage - messages survive broker restarts and aren't lost.
3. Support many consumers (consumer groups) reading independently.
4. Preserve ordering (at least within a partition).

### Non-Functional Requirements:
- **High throughput:** millions of messages/sec.
- **Durability:** replicated, no data loss on a broker failure.
- **Scalability:** add brokers/partitions to scale.
- **Low latency** for real-time consumers.
- **Retention:** keep messages for a configurable window (replay).

### Out of Scope:
- Exactly-once end-to-end across arbitrary sinks (discuss the approximation).

---

## 2️⃣ Capacity Estimation

```
1M messages/sec × 1 KB = 1 GB/sec write throughput → must be distributed
Retention 7 days: 1 GB/sec × 86,400 × 7 ≈ 600 TB (×replication factor 3 ≈ 1.8 PB)
Sequential disk writes are fast (~hundreds MB/s per disk) → append-only log is the trick
```

---

## 3️⃣ Core Concepts

| Concept | Meaning |
|---------|---------|
| **Topic** | a named stream of messages |
| **Partition** | a topic is split into partitions; the unit of parallelism + ordering |
| **Offset** | a message's position within a partition (monotonic) |
| **Broker** | a server holding partitions |
| **Producer** | writes to a topic (optionally keyed → same key → same partition) |
| **Consumer group** | consumers sharing the work; each partition read by one consumer in the group |

---

## 4️⃣ High-Level Design

```
Producers ──► [ Topic: orders ]
                 ├─ Partition 0 ─► Broker A (leader) ─replicate─► Broker B, C (followers)
                 ├─ Partition 1 ─► Broker B (leader) ─replicate─► Broker A, C
                 └─ Partition 2 ─► Broker C (leader) ─replicate─► Broker A, B

Consumer group "billing":  C1 reads P0, C2 reads P1+P2   (each partition → one consumer)

Coordination: ZooKeeper/KRaft tracks brokers, leaders, and consumer-group offsets
```

**Write:** producer hashes the key → partition → sends to that partition's **leader** broker →
leader appends to its log and replicates to followers → acks after the replication policy is met.
**Read:** a consumer in a group is assigned partitions and reads sequentially by offset, committing
its progress so it can resume after a restart.

---

## 5️⃣ Deep Dives

### Deep Dive 1: The append-only log (why it's fast)
Each partition is an append-only log file on disk. Writes are **sequential** (fast, even on disk),
and reads are sequential scans from an offset. No per-message random I/O. Consumers track their own
offset, so the broker doesn't manage per-consumer state per message. This log-centric design is why
Kafka hits high throughput.

### Deep Dive 2: Partitioning for scale + ordering
Partitions are the unit of parallelism: more partitions = more concurrent producers/consumers.
Ordering is guaranteed **only within a partition**, so messages that must stay ordered (e.g. events
for one user) are given the same key → same partition. Cross-partition order is not guaranteed.
*Follow-up hook:* what limits consumer parallelism? (partition count - a group can't have more active
consumers than partitions.)

### Deep Dive 3: Replication & durability
Each partition has a **leader** and N-1 **followers**. Producers can require acks from a quorum
(in-sync replicas) before a write is considered committed - trading latency for durability. If a
leader dies, a follower is promoted. This is leader-follower replication applied per partition. See
[DistributedSystemsConcepts.md](../DistributedSystemsConcepts.md).

### Deep Dive 4: Delivery semantics
- **At-most-once:** commit offset before processing → crash loses the message.
- **At-least-once:** process, then commit → a crash re-delivers (duplicates possible) → consumers
  must be **idempotent**.
- **Exactly-once:** approximated with idempotent producers + transactional writes + dedup; expensive
  and bounded to the platform. In practice: at-least-once + idempotent consumers.

### Deep Dive 5: Consumer groups & rebalancing
Within a group, partitions are distributed across consumers; if a consumer joins/leaves, the group
**rebalances** partition assignments. Different groups read the same topic independently (each has
its own offsets) - that's how one stream feeds many services.

---

## 6️⃣ Bottlenecks & Optimizations

- **Hot partition** (skewed key) → choose a better partition key or add partitions.
- **Rebalance storms** → sticky assignment, longer session timeouts.
- **Slow consumer / backlog** → scale consumers up to partition count; monitor consumer lag.
- **Retention/storage** → tiered storage, compaction (keep latest per key), time/size-based
  retention.

---

## 7️⃣ Interview Tips

1. Anchor on the **partitioned append-only log** - that's the whole idea.
2. Ordering is **per partition**; key messages that must stay ordered.
3. Discuss **replication** (leader/follower, in-sync replicas) for durability.
4. Be honest about **exactly-once** (approximation, not magic).

### Common Follow-ups:
**Q: How do you guarantee ordering?** Only within a partition; same key → same partition.
**Q: How do you scale consumers?** Add partitions; a group's parallelism is capped by partition count.
**Q: How do you avoid data loss?** Replication + require acks from in-sync replicas.
**Q: At-least-once vs exactly-once?** At-least-once + idempotent consumers is the practical default.

---

## Summary

**Key Decisions:**
1. ✅ **Partitioned append-only log** for high sequential throughput.
2. ✅ **Ordering within a partition**; key-based partitioning.
3. ✅ **Leader/follower replication** + in-sync-replica acks for durability.
4. ✅ **Consumer groups** with rebalancing; at-least-once + idempotency for delivery.

**Related:** [message-queues.md](../components/message-queues.md) ·
[DistributedSystemsConcepts.md](../DistributedSystemsConcepts.md) ·
[qa-system-design-concepts.md](../../QA-Bank/qa-system-design-concepts.md)
