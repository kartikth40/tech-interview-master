# 📐 Latency Numbers & Estimation

> **Explain in 2 min:** Back-of-the-envelope estimation is turning a vague prompt ("design Twitter")
> into rough numbers — QPS, storage, bandwidth — so your design decisions are grounded. The method:
> state assumptions (users, actions/user/day), derive **QPS = actions/day ÷ ~86,400**, apply a
> **peak factor** (×2-3), then size storage (bytes/item × items) and bandwidth (QPS × size). You
> don't need precision — you need the right **order of magnitude** and to show the reasoning. A
> handful of memorized latency numbers (memory ~100 ns, SSD ~100 µs, disk seek ~10 ms, cross-country
> RTT ~150 ms) let you reason about where time goes.
>
> This file is the **drilling companion**; the estimation *step* within the interview framework and
> the full memorized table live in
> [SystemDesign/SystemDesignGuide.md](../SystemDesign/SystemDesignGuide.md).

---

## 🔢 Powers of 2 & scale words `[core]`

Data sizes are powers of 2; traffic/counts are powers of 10. Know the mapping cold:

| Power of 2 | ≈ Value | Name |
|------------|---------|------|
| 2¹⁰ | ~1 thousand | 1 KB |
| 2²⁰ | ~1 million | 1 MB |
| 2³⁰ | ~1 billion | 1 GB |
| 2⁴⁰ | ~1 trillion | 1 TB |
| 2⁵⁰ | ~10¹⁵ | 1 PB |

**Time anchors:** 1 day ≈ 86,400 s ≈ **~10⁵ s**. So **1 million events/day ≈ 12/sec** (before peak
factor). This single conversion drives most QPS math.

---

## ⏱️ Latency numbers to know `[core]`

A compact recall set (approximate, orders of magnitude — that's the point):

| Operation | Approx latency |
|-----------|----------------|
| L1/L2 cache reference | ~1 ns |
| Main memory reference | ~100 ns |
| Read 1 MB sequentially from memory | ~10 µs |
| SSD random read | ~100 µs |
| Read 1 MB from SSD | ~1 ms |
| Disk seek (spinning) | ~10 ms |
| Round trip within a datacenter | ~0.5 ms |
| Round trip cross-country (US) | ~150 ms |

**Takeaways to say out loud:** memory is ~100,000× faster than a disk seek; a network round trip
across regions dwarfs local compute; sequential beats random. This is *why* we cache, batch, and
keep data local. Full table + context: [SystemDesignGuide.md](../SystemDesign/SystemDesignGuide.md).

---

## 🧮 The estimation method `[core]`

A repeatable four-step drill:

```text
1. TRAFFIC
   DAU × actions/user/day = actions/day
   QPS      = actions/day / 86,400        (~ /10^5)
   Peak QPS = QPS × 2–3                    (traffic isn't uniform)

2. STORAGE
   bytes/item × items/day = storage/day
   × 365 × retention years = total (add replication factor)

3. BANDWIDTH
   read/write QPS × avg payload size = bytes/sec

4. MEMORY (cache)
   apply the 80/20 rule: cache the hot ~20% of daily reads
```

Round aggressively (use 10⁵ for 86,400, 100 KB for "a photo") and keep units explicit. Interviewers
grade the *approach and assumptions*, not arithmetic to 3 significant figures.

---

## 🏋️ Worked drill: a photo-sharing feed `[core]`

Assumptions stated up front (make them, don't ask for exact figures):
- 100 M DAU, each posts 1 photo/day, reads 100 photos/day.
- Photo ≈ 1 MB (stored), metadata ≈ 1 KB.

```text
Writes:  100M posts/day / 10^5 s   ≈ 1,000 writes/sec  → peak ~2–3K/sec
Reads:   100M × 100 / 10^5 s       ≈ 100,000 reads/sec → peak ~250K/sec  (read-heavy!)
Storage: 100M × 1 MB/day           = 100 TB/day  → ~36 PB/year (×replication)
Bandwidth (read): 100K/sec × 1 MB  ≈ 100 GB/sec  → screams "CDN + cache"
```

The numbers *drive the design*: read-heavy → caching + read replicas + CDN; 100 TB/day → object
storage + sharding, not a single DB.

---

## 📊 Useful reference points `[advanced]`

Rough single-node ceilings (vary widely with workload — use as sanity anchors, not guarantees):
- Commodity server: **~1K QPS** for real work.
- Single SQL DB: a few K reads/sec, fewer writes.
- Redis / in-memory: **~100K+ ops/sec** per node.
- 1 Gbps link ≈ 125 MB/sec.

**Availability "nines":** 99.9% ≈ 8.8 h down/year; 99.99% ≈ 52 min; 99.999% ≈ 5 min. Handy when a
prompt states an SLA.

---

## ⚠️ Common interview traps

- Skipping estimation and jumping to boxes-and-arrows — the numbers justify the design.
- Forgetting the **peak factor** (traffic isn't spread evenly over 24 h).
- Ignoring **replication** in storage math (3× is common).
- Not noticing a system is read-heavy vs write-heavy — it changes everything (cache/replicas vs
  sharding/queues).
- False precision — round to orders of magnitude and move on.

## 🔗 Related

- Q&A drills: [qa-system-design-concepts.md](../QA-Bank/qa-system-design-concepts.md)
- Estimation step in the interview framework + full latency table → [SystemDesign/SystemDesignGuide.md](../SystemDesign/SystemDesignGuide.md)
- Caching (why hot-data caching works) → [SystemDesign/components/caching.md](../SystemDesign/components/caching.md)
- Sharding (when storage/writes exceed one node) → [SystemDesign/components/database-sharding.md](../SystemDesign/components/database-sharding.md)
