# Unique ID Generator System Design (Distributed IDs)
> **SDE-2 Interview Ready** | 45-minute format

## Problem Statement

Design a service that generates globally unique IDs across a distributed system - no central
sequence bottleneck, and ideally IDs that sort roughly by creation time.

**Example:** every tweet, order, or message needs a unique 64-bit ID generated on any of thousands
of servers without collisions.

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. Generate unique IDs across many machines.
2. IDs are numeric and ideally **time-sortable** (roughly ordered by creation).
3. High throughput (thousands+ IDs/sec per node).

### Non-Functional Requirements:
- **Uniqueness:** absolutely no collisions.
- **Scalable:** no single coordinator on the hot path.
- **Compact:** prefer 64-bit (fits a BIGINT, indexes well).
- **Low latency:** generated locally, no network round trip.

### Out of Scope:
- Human-readable / vanity IDs.

---

## 2️⃣ Options & Trade-offs

| Approach | Unique? | Sortable? | Coordination | Notes |
|----------|---------|-----------|--------------|-------|
| **DB auto-increment** | yes | yes | central (bottleneck/SPOF) | simple, doesn't scale/shard |
| **UUIDv4 (128-bit)** | yes | no | none | random, but big and scatters index writes |
| **DB ticket server** | yes | roughly | central-ish | hand out ranges/blocks to reduce contention |
| **Snowflake (64-bit)** ⭐ | yes | yes | worker-ID assignment only | the standard answer |

---

## 3️⃣ Snowflake (the standard answer)

Compose a 64-bit ID from time + machine + sequence so any worker generates unique, time-sortable IDs
with no per-ID coordination:

```
64 bits total:
- 1 bit : sign (unused, always 0)
- 41 bits: timestamp (ms since a custom epoch) → ~69 years of range
- 5 bits : datacenter ID (32 datacenters)
- 5 bits : worker ID (32 workers per datacenter)
- 12 bits: sequence (4096 IDs per millisecond per worker)

Capacity: 4096 IDs/ms per worker = ~4M IDs/sec per worker
```

```text
FUNCTION nextId():
    ts = currentMillis()
    IF ts == lastTs:
        sequence = (sequence + 1) AND 0xFFF        # 12-bit wrap
        IF sequence == 0:                          # exhausted this ms
            ts = waitUntilNextMillis(lastTs)       # spin to next ms
    ELSE:
        sequence = 0
    lastTs = ts

    RETURN ((ts - EPOCH) << 22)
         | (datacenterId << 17)
         | (workerId << 12)
         | sequence
```

Because the timestamp is in the **high bits**, IDs are **time-sortable (k-sorted)** - sequential
inserts give good B-tree index locality, unlike random UUIDv4 which scatters writes across the index.
See indexing in [databases-internals.md](../../Fundamentals/databases-internals.md).

---

## 4️⃣ High-Level Design

```
┌──────────────┐    each app node embeds an ID generator (a library),
│  App node 1  │──┐ configured with a unique (datacenterId, workerId)
│  (worker 5)  │  │
├──────────────┤  │   worker IDs assigned by ZooKeeper/etcd at startup
│  App node 2  │  │   (or a config service), so no two workers collide
│  (worker 6)  │  │
└──────────────┘  ▼
        ┌────────────────────┐
        │ ZooKeeper / etcd    │  ← hands out unique worker IDs, detects
        │ (worker-ID registry)│    dead workers so IDs can be reused
        └────────────────────┘
```

IDs are generated **in-process** (no network call), which is why Snowflake is fast. The only
coordination is assigning each worker a distinct ID at startup.

---

## 5️⃣ Deep Dives

### Deep Dive 1: Clock skew and going backwards
Snowflake trusts the wall clock. If NTP moves the clock **backwards**, a worker could regenerate a
timestamp it already used → potential duplicate. Handle it: if `currentMillis() < lastTs`, either
wait until the clock catches up, or reject/alert. Never emit an ID with a timestamp earlier than the
last one issued.
*Follow-up hook:* logical clocks vs wall clocks - see
[DistributedSystemsConcepts.md](../DistributedSystemsConcepts.md).

### Deep Dive 2: Worker-ID assignment
Two workers with the same (datacenter, worker) bits will collide. Assign the 10 bits via a
coordination service (ZooKeeper/etcd) that leases IDs and reclaims them when a node dies. For small
fleets, static config works.

### Deep Dive 3: Sequence exhaustion
Only 4096 IDs per millisecond per worker. If a worker exceeds that, spin-wait to the next
millisecond. If one worker needs more, add workers (parallelism) rather than widening the field.

### Deep Dive 4: UUID vs Snowflake vs ticket server
- **UUIDv4:** zero coordination, but 128-bit and unsortable → bad index locality.
- **DB ticket server:** a table/sequence hands out ID ranges (e.g. 1000 at a time) to each node,
  cutting central contention; roughly sortable, but still a central dependency.
- **Snowflake:** best balance - local, compact, time-sortable.

---

## 6️⃣ Bottlenecks & Optimizations

- **Custom epoch:** start the 41-bit timestamp at your service's launch date to maximize lifespan.
- **Bit allocation is tunable:** trade worker bits for sequence bits based on fleet size vs per-node
  rate.
- **Availability:** since generation is in-process, there's no runtime SPOF - only the startup
  worker-ID assignment depends on the coordinator.

---

## 7️⃣ Interview Tips

1. Reject DB auto-increment early (bottleneck, doesn't shard).
2. Lead with **Snowflake**; explain the bit layout and why high-bit timestamp = sortable.
3. Raise **clock skew** yourself - it's the favorite follow-up.
4. Mention worker-ID assignment via ZooKeeper/etcd.

### Common Follow-ups:
**Q: Why not UUID?** Not sortable, 128-bit, scatters DB index writes.
**Q: What if the clock goes backwards?** Wait or reject; never emit a smaller timestamp than the last.
**Q: How are worker IDs assigned uniquely?** Coordination service leases them.
**Q: Why are sortable IDs nice?** Sequential B-tree inserts → good index locality.

---

## Summary

**Key Decisions:**
1. ✅ **Snowflake 64-bit** (timestamp + datacenter + worker + sequence).
2. ✅ IDs generated **in-process** → fast, no runtime SPOF.
3. ✅ **Worker IDs** assigned by ZooKeeper/etcd.
4. ✅ Handle **clock skew** (never go backwards).

**Related:** [database-sharding.md](../components/database-sharding.md) ·
[databases-internals.md](../../Fundamentals/databases-internals.md) ·
[DistributedSystemsConcepts.md](../DistributedSystemsConcepts.md)
