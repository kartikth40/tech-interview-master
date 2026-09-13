# Distributed Key-Value Store System Design (Dynamo-style)
> **SDE-2 Interview Ready** | 45-minute format

## 🎯 Problem Statement

Design a distributed key-value store (like DynamoDB / Cassandra) that stores `key → value` pairs
across many nodes with high availability and horizontal scale.

**Example:** `put("user:123", {...})` / `get("user:123")` served from a cluster that survives node
failures and scales by adding machines.

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. `put(key, value)` and `get(key)`.
2. Data distributed across many nodes; scale by adding nodes.
3. Tolerate node failures without data loss or downtime.

### Non-Functional Requirements:
- **Scale:** billions of keys, TB-PB of data, high throughput.
- **Availability:** always writable/readable (lean AP for this design).
- **Low latency:** single-digit ms reads/writes.
- **Tunable consistency:** let the caller trade consistency for latency.

### Out of Scope:
- Rich queries / secondary indexes / transactions across keys (KV, not relational).

---

## 2️⃣ Capacity Estimation

```
1B keys × 1 KB avg value = 1 TB logical; ×3 replication = 3 TB
Throughput target: 100K+ ops/sec
Per node ~100K ops/sec, ~1 TB → cluster of tens of nodes, sized by throughput and storage
```

---

## 3️⃣ API Design

```text
put(key, value, [context])   # context = version/vector clock from a prior read
get(key) -> { value(s), context }
delete(key)
# Consistency knobs per call:
#   N = replicas, W = write quorum, R = read quorum
```

---

## 4️⃣ Core Design Decisions

The classic Dynamo building blocks — this question is really "do you know these five ideas?":

| Concern | Technique |
|---------|-----------|
| Distribute keys across nodes | **Consistent hashing** (ring + virtual nodes) |
| Availability + durability | **Replication** to N nodes |
| Tunable consistency | **Quorum** — W + R > N gives read-your-writes |
| Concurrent-write conflicts | **Versioning** with vector clocks |
| Detect/repair divergence | **Merkle trees** + read repair + anti-entropy |
| Temporary node failure | **Hinted handoff** |

---

## 5️⃣ High-Level Design

```
                 Coordinator (any node can coordinate)
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌─────────┐       ┌─────────┐       ┌─────────┐
   │ Node A  │       │ Node B  │       │ Node C  │   ...on a hash ring
   │ (vnodes)│◄─────►│ (vnodes)│◄─────►│ (vnodes)│   gossip membership
   └─────────┘       └─────────┘       └─────────┘
   key hashed to a ring position → first N nodes clockwise are its replicas
```

**Write path:** client → coordinator → send to N replicas → wait for W acks → success.
**Read path:** coordinator → read from N replicas → wait for R responses → reconcile versions → return.

---

## 6️⃣ Deep Dives

### Deep Dive 1: Consistent hashing (data distribution)
Place nodes and keys on a hash ring; a key's replicas are the next N nodes clockwise. Adding/removing
a node only remaps ~K/N keys instead of nearly all (which `hash mod N` would). **Virtual nodes**
(many ring positions per physical node) even out load and let you weight bigger nodes. Full treatment:
[database-sharding.md](../components/database-sharding.md) and
[hashing.md](../../Fundamentals/hashing.md).

### Deep Dive 2: Replication + quorum (tunable consistency)
Each key is replicated to N nodes. A write succeeds after **W** acks; a read waits for **R** responses.
If **W + R > N**, read and write sets overlap, guaranteeing a read sees the latest write
(strong-ish). Tune it:
- `W=1, R=1` → fast, weakly consistent.
- `W=N, R=1` → fast reads, slow durable writes.
- `W=quorum, R=quorum` → balanced (e.g. N=3, W=2, R=2).

This is the CAP/PACELC dial in practice — see
[DistributedSystemsConcepts.md](../DistributedSystemsConcepts.md).

### Deep Dive 3: Versioning with vector clocks (conflict resolution)
With multiple writable replicas, two clients can update the same key concurrently. A **vector clock**
(`[node:counter]` per replica) records causality so the system can tell whether one version
supersedes another or they genuinely **conflict**. Conflicts are resolved by last-write-wins
(simple, can lose data) or returned to the client to merge (like a shopping cart union).
*Follow-up hook:* why is LWW dangerous? (silent lost updates under clock skew.)

### Deep Dive 4: Failure handling — hinted handoff & read repair
- **Hinted handoff:** if a replica is temporarily down, another node accepts the write and holds a
  "hint" to deliver it when the node returns → stays available.
- **Read repair:** on a read, if replicas disagree, push the newest version to the stale ones.
- **Anti-entropy with Merkle trees:** replicas compare hash trees of their key ranges to find
  differences cheaply and sync only what diverged.

### Deep Dive 5: Storage engine
Each node typically uses an **LSM-tree** (memtable + sorted SSTables + compaction) for fast writes,
with a **bloom filter** per SSTable to skip files that can't contain a key. See indexing in
[databases-internals.md](../../Fundamentals/databases-internals.md).

---

## 7️⃣ Bottlenecks & Optimizations

- **Hot key / hot partition** → add virtual nodes, cache, or split the key.
- **Compaction load** (LSM) competes with reads → schedule/throttle it.
- **Wide vector clocks** over time → truncate old entries.
- **Cross-region latency** → per-region quorums, async replication between regions.

---

## 8️⃣ Interview Tips

1. State it's AP with tunable consistency (unless asked for CP).
2. Lead with the five pillars: consistent hashing, replication, quorum (W+R>N), vector clocks,
   Merkle/anti-entropy.
3. Draw the ring and the read/write quorum path.
4. Discuss conflict resolution honestly (LWW vs client merge).

### Common Follow-ups:
**Q: How do you get read-your-writes?** W + R > N.
**Q: How do you detect concurrent writes?** Vector clocks (causality), not timestamps alone.
**Q: How do replicas re-sync after a partition?** Merkle-tree anti-entropy + read repair.
**Q: Why LSM over B-tree here?** Write-optimized for high ingest.

---

## Summary

**Key Decisions:**
1. ✅ **Consistent hashing** (+ virtual nodes) for distribution.
2. ✅ **N replicas** with **quorum W + R > N** for tunable consistency.
3. ✅ **Vector clocks** for conflict detection; LWW or client-merge to resolve.
4. ✅ **Hinted handoff + read repair + Merkle anti-entropy** for failures.
5. ✅ **LSM-tree + bloom filters** per node for write-heavy storage.

**Related:** [DistributedSystemsConcepts.md](../DistributedSystemsConcepts.md) ·
[database-sharding.md](../components/database-sharding.md) ·
[databases-internals.md](../../Fundamentals/databases-internals.md) ·
[hashing.md](../../Fundamentals/hashing.md)
