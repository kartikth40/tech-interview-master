# Ad Click Aggregation System Design (Streaming Analytics)
> **SDE-2 Interview Ready** | 45-minute format · *advanced / Xu Vol 2*

## Problem Statement

Design a system that ingests a massive stream of ad-click events and produces aggregated metrics
(clicks per ad per minute, top-N ads) in near real time for dashboards and billing.

**Example:** "How many times was ad #123 clicked in the last minute?" answered within seconds, over
billions of daily clicks.

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. Ingest click events (ad_id, user, timestamp, ...).
2. Aggregate counts over time windows (per minute/hour) per ad.
3. Support queries: click count for an ad in a range; top-N ads.
4. Correctness for **billing** (advertisers pay per click).

### Non-Functional Requirements:
- **Scale:** billions of events/day (~100K-1M events/sec).
- **Near real-time:** aggregates available within seconds.
- **Accuracy:** billing needs correct counts; tolerate brief lag, not loss.
- **Fault tolerant:** no double-counting, no lost events on failure.

### Out of Scope:
- Ad serving/targeting; fraud detection (mention as a downstream consumer).

---

## 2️⃣ Capacity Estimation

```
1B clicks/day ≈ 11.5K/sec average, peak ×5-10 → ~100K/sec
Event ~100 B → ~100 GB/day raw (store raw for reprocessing + aggregates for queries)
Aggregation state: per (ad_id, minute) counters → millions of keys, kept in a fast store
```

---

## 3️⃣ High-Level Design

```
Ad clicks ─► Ingest API ─► [ Message Queue: Kafka ] ─► Stream aggregators ─► Aggregation store
                                    │                     (windowed counts)     (per ad/minute)
                                    │                                                │
                                    └─► Raw event store (S3/HDFS) ◄── reprocess      ▼
                                        (source of truth for replay)          Query service ─► dashboards/billing
```

**Flow:** clicks land on an ingest API → written to Kafka (durable buffer) → stream processors
consume, aggregate by (ad_id, time window), and write counters to a store → a query service serves
dashboards/billing. Raw events are also archived for reprocessing.

---

## 4️⃣ Deep Dives

### Deep Dive 1: Windowed aggregation
Aggregate events into fixed **tumbling windows** (e.g. per minute) keyed by ad_id. A stream processor
(Kafka Streams / Flink / Spark Streaming) maintains `(ad_id, minute) -> count` and flushes it to the
aggregation store. Queries over a range sum the relevant per-minute buckets.

### Deep Dive 2: Late & out-of-order events (watermarks)
Events arrive late (network, mobile offline). Using **event time** (when the click happened) not
**processing time**, the processor holds a window open a little longer via a **watermark** before
finalizing it, so late events still count. There's a lag-vs-completeness trade-off - how long do you
wait? See time/ordering discussion in
[DistributedSystemsConcepts.md](../DistributedSystemsConcepts.md).

### Deep Dive 3: Exactly-once / no double-counting (billing)
Advertisers are billed, so double-counting = overcharging. Achieve effective exactly-once with:
- **Idempotent writes:** dedup by a unique event ID (client-generated) so a re-delivered event isn't
  counted twice.
- **Checkpointed offsets + transactional output:** the processor commits its input offset and its
  aggregate output atomically, so a crash-and-replay doesn't recount.
This is the at-least-once + idempotency pattern applied to aggregation - see
[qa-concurrency.md](../../QA-Bank/qa-concurrency.md).

### Deep Dive 4: Lambda vs Kappa architecture
- **Lambda:** a fast streaming path for near-real-time (approximate) + a batch path over the raw
  store for accurate recomputation; reconcile the two. Robust but two code paths.
- **Kappa:** a single streaming path; to "recompute," replay the raw event log through the same
  processor. Simpler; relies on durable, replayable logs (Kafka + S3).
Mention both; Kappa is the modern default when the log is replayable.

### Deep Dive 5: Hot keys / skew
A viral ad creates a hot (ad_id) partition. Mitigate by **sub-sharding** the key (e.g.
`ad_id + randomBucket`) during aggregation and summing the buckets at query time, so one ad doesn't
overwhelm a single aggregator.

---

## 5️⃣ Bottlenecks & Optimizations

- **Ingestion spikes** → Kafka buffers; scale aggregators by partition count.
- **Hot ad** → key sub-sharding + combine at read.
- **Query cost** → pre-aggregate per minute; roll up minutes → hours → days.
- **Reprocessing** → keep raw events (S3) so you can replay after a bug.

---

## 6️⃣ Interview Tips

1. Center on **Kafka → stream aggregator → aggregation store**, plus a raw archive for replay.
2. Raise **event-time windows + watermarks** for late/out-of-order events.
3. For billing, stress **no double-counting** (idempotency + checkpointing).
4. Contrast **Lambda vs Kappa**.

### Common Follow-ups:
**Q: How do you avoid double-counting for billing?** Idempotent dedup by event ID + checkpointed exactly-once.
**Q: How do you handle late clicks?** Event-time windows with watermarks.
**Q: How do you recompute after a bug?** Replay the raw event log (Kappa) or batch path (Lambda).
**Q: A viral ad overloads one aggregator - fix?** Sub-shard the hot key, sum at query time.

---

## Summary

**Key Decisions:**
1. ✅ **Kafka buffer → stream aggregation → aggregation store**, raw archive for replay.
2. ✅ **Event-time tumbling windows + watermarks** for late events.
3. ✅ **Idempotent dedup + checkpointing** for billing-grade correctness.
4. ✅ **Lambda vs Kappa**; **hot-key sub-sharding** for skew.

**Related:** [message-queues.md](../components/message-queues.md) ·
[distributed-message-queue.md](distributed-message-queue.md) ·
[DistributedSystemsConcepts.md](../DistributedSystemsConcepts.md)
