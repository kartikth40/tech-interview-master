# Search Autocomplete / Typeahead System Design
> **SDE-2 Interview Ready** | 45-minute format

## 🎯 Problem Statement

Design a search autocomplete (typeahead) that, as a user types a prefix, returns the top few most
relevant completions in real time.

**Example:** typing "sys" instantly suggests "system design", "system design interview", "systemctl"
— ranked by popularity.

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. Given a prefix, return the **top-k** (e.g. 5) suggestions.
2. Rank by popularity/relevance.
3. Suggestions update over time as query trends change.

### Non-Functional Requirements:
- **Very low latency:** must feel instant (<50-100ms end to end, per keystroke).
- **Scale:** huge query volume (every keystroke is a request); read-heavy.
- **Fresh enough:** trending terms appear within hours, not instantly.

### Out of Scope:
- Full search / ranking of results pages (this is just the suggestion box).
- Spell correction (mention as an extension).

---

## 2️⃣ Capacity Estimation

```
100M searches/day, ~20 chars each, ~4 keystrokes trigger a request
Requests ≈ 100M × 4 / 86,400 ≈ 4,600 req/sec average, peak ×2-3 → ~14K req/sec
This is READ-heavy and latency-critical → serve from memory (cache/trie), precompute rankings offline
Corpus: top few million distinct queries carry most traffic (80/20)
```

---

## 3️⃣ API Design

```text
GET /v1/autocomplete?prefix=sys&limit=5
Response: {
  suggestions: ["system design", "system design interview", "systemctl", ...]
}
# Called on (debounced) keystrokes; must be cache/CDN-friendly.
```

---

## 4️⃣ Core Data Structure: Trie

A **trie (prefix tree)** maps a prefix to completions in O(prefix length). To make top-k instant,
**precompute and cache the top-k suggestions at each node** rather than walking the whole subtree per
request.

```text
# Each trie node stores its top-k completions (precomputed offline)
node "sys" -> ["system design", "system design interview", "systemctl", ...]

FUNCTION autocomplete(prefix):
    node = trie.walk(prefix)        # O(len(prefix))
    IF node is null: RETURN []
    RETURN node.topK               # O(1) — precomputed
```

See the trie implementation: [DSA/data-structures/tree/trie.py](../../DSA/data-structures/tree/trie.py).

---

## 5️⃣ High-Level Design

Two planes — a fast read path and an offline build path:

```
READ PATH (per keystroke, latency-critical)
  Client ─► CDN/edge cache ─► Autocomplete service ─► in-memory Trie (top-k cached)
                                     │ miss
                                     ▼
                               Redis (prefix → top-k)

BUILD PATH (offline, hourly)
  Query logs ─► aggregation (count queries) ─► ranking ─► build Trie with top-k per node
             (Kafka + batch/stream job)                 │
                                                        ▼
                                          push new Trie snapshot to servers + cache
```

The read path never computes rankings; it only looks up precomputed data. The build path recomputes
popularity from query logs periodically and ships a fresh trie.

---

## 6️⃣ Deep Dives

### Deep Dive 1: Precomputed top-k at each node
Walking a subtree to find the top-k on every keystroke is too slow. Instead, offline, compute the
top-k completions for **every prefix** and store them on the node (or in Redis keyed by prefix). Read
becomes O(len(prefix)) walk + O(1) return. Trade-off: more storage and a rebuild lag, for instant
reads.

### Deep Dive 2: The data-gathering / ranking pipeline
Query logs stream into Kafka; a batch/stream job aggregates counts over a rolling window and ranks
terms (raw frequency, or time-decayed to favor trending). It then rebuilds the trie's per-node top-k
and publishes a new snapshot. Runs hourly — freshness vs cost trade-off.

### Deep Dive 3: Scaling the trie (sharding)
The full trie is large. Shard it by **first character(s)** of the prefix across servers (e.g. a-f,
g-m, …), or replicate the whole read-only trie to many servers since it's rebuilt offline and only
read at runtime. Replication is simplest given the read-heavy, write-offline pattern.

### Deep Dive 4: Caching and CDN
Popular prefixes are extremely cacheable. Cache `prefix → top-k` in Redis and even at the CDN/edge
with a short TTL. Debounce on the client (wait ~100ms between keystrokes) to cut request volume. See
[caching.md](../components/caching.md).

### Deep Dive 5: Freshness vs latency
Suggestions don't need to be real-time. A rebuild every hour keeps trends current while keeping the
read path a pure in-memory lookup. For breaking trends, a smaller fast-path job can inject hot terms
sooner.

---

## 7️⃣ Bottlenecks & Optimizations

- **Per-keystroke request volume** → client debounce + aggressive caching/CDN.
- **Trie rebuild cost** → incremental updates or rebuild off-peak; publish snapshots atomically.
- **Memory** → keep only the top few million prefixes; long-tail falls back to a slower path.
- **Hot prefixes** → cache/replicate; they're the bulk of traffic (80/20).

---

## 8️⃣ Interview Tips

1. Lead with **trie + precomputed top-k per node** — that's the core insight.
2. Separate the **fast read path** from the **offline build/ranking pipeline**.
3. Stress **caching/CDN + debounce** for the per-keystroke load.
4. Freshness is hourly, not real-time — say so.

### Common Follow-ups:
**Q: Why not compute top-k per request?** Too slow; precompute per node offline.
**Q: How do trending terms show up?** Periodic rebuild from query logs (time-decayed counts).
**Q: How do you scale the trie?** Replicate the read-only trie; or shard by prefix.
**Q: How do you cut request volume?** Client debounce + CDN/Redis caching of hot prefixes.

---

## Summary

**Key Decisions:**
1. ✅ **Trie with precomputed top-k** at each node → O(1) suggestion lookup.
2. ✅ **Offline pipeline** (Kafka + aggregation) rebuilds rankings hourly.
3. ✅ **Read-only trie replicated** + heavy **caching/CDN** + client debounce.
4. ✅ Freshness is **near-real-time (hourly)**, prioritizing read latency.

**Related:** [DSA/data-structures/tree/trie.py](../../DSA/data-structures/tree/trie.py) ·
[caching.md](../components/caching.md) ·
[qa-system-design-concepts.md](../../QA-Bank/qa-system-design-concepts.md)
