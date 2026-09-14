# ❓ Caching - Q&A

> Pairs with [Caching](../SystemDesign/components/caching.md). Format and
> tag legend: [Overview](README.md).

---

> **Q1. Why cache at all?**
> To cut latency and load by serving hot data from a fast layer (RAM ~microseconds) instead of a
> slow backend (DB query ~milliseconds). It improves response time, reduces backend cost, and helps
> absorb traffic spikes.
> *Follow-ups:* What's the downside? (staleness + added complexity/consistency work.)
> `Easy` · `MAANG`

> **Q2. Explain cache-aside (lazy loading).**
> The app checks the cache first; on a miss it reads the DB, populates the cache, and returns. Most
> common pattern - the cache only holds requested data, and a cache failure just means a DB read.
> Downside: first request per key is always a miss (cold cache).
> *Follow-ups:* How do you warm a cold cache? (pre-load hot keys.)
> `Med` · `MAANG`

> **Q3. Write-through vs write-back vs write-around?**
> Write-through writes cache + DB synchronously (consistent, slower writes). Write-back writes cache
> first and DB later (fast, risk of loss on crash). Write-around writes only the DB (avoids caching
> write-once data, but first read misses). See [Caching](../SystemDesign/components/caching.md).
> *Follow-ups:* Which risks data loss and why? (write-back - unflushed data lost on crash.)
> `Hard` · `Amazon`

> **Q4. What eviction policies do you know?**
> LRU (evict least recently used - good general default), LFU (least frequently used - good for
> stable hot sets), FIFO, and random. TTL expiry is orthogonal (time-based). LRU is the common
> interview answer; implement with a hash map + doubly linked list for O(1).
> *Follow-ups:* When does LFU beat LRU? (stable popularity; LRU evicts a hot item after a scan.)
> `Med` · `MAANG`

> **Q5. What's the hardest problem in caching?**
> Invalidation - keeping the cache consistent with the source of truth. Options: TTL (simple, allows
> staleness), explicit invalidation on write (fresh, more complex), or write-through. There's no free
> lunch; you trade freshness vs complexity.
> *Follow-ups:* TTL vs event-based invalidation trade-off?
> `Hard` · `MAANG`

> **Q6. What is a cache stampede (thundering herd) and how do you prevent it?**
> When a popular key expires, many requests miss simultaneously and all hit the DB at once. Prevent
> with a lock/single-flight (one request recomputes while others wait), staggered/jittered TTLs, or
> serving stale while refreshing in the background.
> *Follow-ups:* What is request coalescing / single-flight?
> `Hard` · `Google`

> **Q7. What is a hot key and how do you handle it?**
> A single key receiving disproportionate traffic, overloading one cache node. Mitigate by
> replicating the key across nodes, adding a local (in-process) cache in front, or splitting the key.
> *Follow-ups:* How does a local + distributed multi-layer cache help here?
> `Hard` · `Amazon`

> **Q8. Where can caching live in a request path?**
> Browser cache → CDN (edge) → application/in-process cache → distributed cache (Redis) → DB query
> cache. Each layer trades freshness for speed; the closer to the user, the faster but staler.
> *Follow-ups:* What belongs in a CDN vs Redis? (static/edge-cacheable vs dynamic shared data.)
> `Med` · `MAANG`

> **Q9. How do you distribute keys across cache nodes?**
> Consistent hashing, so adding/removing a node only remaps ~K/N keys instead of nearly all (which
> `mod N` would). Virtual nodes even out the distribution. See
> [Hashing](../Fundamentals/hashing.md).
> *Follow-ups:* What breaks if you use plain modulo hashing? (mass misses on scale change.)
> `Med` · `Amazon`

> **Q10. Write-through vs cache-aside for consistency?**
> Write-through updates the cache on every write, so reads are consistent but writes are slower and
> you may cache data never read. Cache-aside + invalidation is simpler and caches only what's read,
> but has a brief staleness window between DB write and cache update.
> *Follow-ups:* What's the race in cache-aside on concurrent write+read? (stale repopulation.)
> `Hard` · `Google`

> **Q11. How do you decide what and how long to cache?**
> Cache hot, read-heavy, expensive-to-compute, tolerant-of-staleness data. TTL depends on how stale
> the data can be: seconds for volatile counters, minutes/hours for catalogs, long for immutable
> assets. Apply the 80/20 rule - cache the hot ~20%.
> *Follow-ups:* What data should you NOT cache? (highly volatile, per-user-unique, sensitive.)
> `Med` · `MAANG`

> **Q12. What consistency issues arise with caching, and how do you reason about them?**
> The cache can serve stale data after the DB changes. You accept a bounded staleness window (TTL),
> invalidate on write, or use write-through - choosing based on how wrong a stale read can be. This
> is fundamentally the same freshness-vs-cost trade-off as replication lag.
> *Follow-ups:* How does this connect to eventual consistency?
> `Med` · `MAANG`

---

**Related:** [Caching](../SystemDesign/components/caching.md) ·
[Hashing Q&A](qa-hashing.md) · [Databases Q&A](qa-databases.md) ·
[System Design Concepts Q&A](qa-system-design-concepts.md)
