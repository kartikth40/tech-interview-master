# ❓ System Design Concepts - Q&A

> Pairs with [System Design Guide](../SystemDesign/SystemDesignGuide.md),
> [components/](../SystemDesign/components/), and
> [Distributed Systems](../SystemDesign/DistributedSystemsConcepts.md). Format and tag
> legend: [Overview](README.md).

---

> **Q1. Horizontal vs vertical scaling?**
> Vertical scaling adds power to one machine (simple, but hits a hardware ceiling and is a single
> point of failure). Horizontal scaling adds more machines (near-unlimited, needs load balancing and
> handles failure better). Distributed systems favor horizontal.
> *Follow-ups:* What makes a service easy to scale horizontally? (statelessness.)
> `Easy` · `MAANG`

> **Q2. Why do stateless services scale better?**
> Any instance can serve any request, so you can add/remove instances freely behind a load balancer
> and lose one without losing session data. State is pushed to shared stores (DB, cache, session
> store) instead of living in the app server.
> *Follow-ups:* Where does session state go then? (Redis/DB, or a signed token.)
> `Med` · `MAANG`

> **Q3. How do you do a back-of-the-envelope estimate?**
> State assumptions (users, actions/user/day), derive QPS = actions/day ÷ ~86,400, apply a ×2-3 peak
> factor, then size storage (bytes×items×retention×replication) and bandwidth (QPS×payload).
> Order-of-magnitude is the goal. See [Latency Numbers & Estimation](../Fundamentals/latency-numbers-and-estimation.md).
> *Follow-ups:* 1M writes/day is roughly how many per second? (~12/s before peak.)
> `Med` · `MAANG`

> **Q4. Explain the CAP theorem and how it guides design.**
> During a network partition you must choose consistency or availability. A payment system leans CP
> (reject rather than serve wrong data); a social feed leans AP (stay up, tolerate staleness). PACELC
> adds a latency-vs-consistency trade-off even without partitions.
> *Follow-ups:* Classify a system you know as CP or AP.
> `Hard` · `MAANG`

> **Q5. L4 vs L7 load balancing?**
> L4 balances on TCP/UDP (IP + port) - fast, protocol-agnostic. L7 balances on application data (HTTP
> path, headers, cookies) - enables routing, TLS termination, and content-based rules at higher cost.
> See [Load Balancer](../SystemDesign/components/load-balancer.md).
> *Follow-ups:* When do you need L7? (path-based routing, sticky sessions, header rules.)
> `Med` · `MAANG`

> **Q6. What load-balancing algorithms exist?**
> Round robin, weighted round robin, least connections, IP/consistent hash (session affinity), and
> latency-based. Choice depends on whether backends are uniform and whether you need stickiness.
> *Follow-ups:* Why might least-connections beat round robin? (uneven request cost.)
> `Med` · `MAANG`

> **Q7. Why use a message queue?**
> To decouple producers from consumers, absorb spikes (buffer), enable async processing, and provide
> retries/backpressure. It trades immediate consistency for resilience and throughput. See
> [Message Queues](../SystemDesign/components/message-queues.md).
> *Follow-ups:* Queue vs pub/sub? (point-to-point work vs broadcast to many subscribers.)
> `Med` · `Amazon`

> **Q8. At-least-once vs exactly-once in a queue?**
> Most queues give at-least-once (retries can duplicate), so consumers must be idempotent.
> Exactly-once is hard end-to-end; it's usually at-least-once delivery + idempotent processing/dedup
> keys. At-most-once drops on failure.
> *Follow-ups:* How do you make a consumer idempotent? (dedup key, upsert, idempotency table.)
> `Hard` · `Amazon`

> **Q9. How does Kafka scale and preserve ordering?**
> A topic is split into partitions distributed across brokers; consumers in a group each own some
> partitions (parallelism). Ordering is guaranteed only within a partition, so you key messages that
> must stay ordered onto the same partition.
> *Follow-ups:* What limits your consumer parallelism? (partition count.)
> `Hard` · `Amazon`

> **Q10. What is consistent hashing and where is it used?**
> Placing nodes and keys on a hash ring so adding/removing a node only remaps ~K/N keys instead of
> nearly all. Virtual nodes even out load. Used by caches, DynamoDB, Cassandra. See
> [Hashing](../Fundamentals/hashing.md).
> *Follow-ups:* What problem does it solve vs `hash mod N`?
> `Med` · `Amazon`

> **Q11. Sharding vs replication - when do you need each?**
> Shard when data or write volume exceeds one node (splits different data). Replicate for
> availability and read scaling (copies the same data). They combine: shard for scale, replicate each
> shard for resilience. See [Database Sharding](../SystemDesign/components/database-sharding.md).
> *Follow-ups:* Why can't replicas scale writes?
> `Med` · `MAANG`

> **Q12. How do you generate unique IDs at scale?**
> Options: UUIDv4 (random, no coordination, but not sortable and scatters index writes), Snowflake
> (64-bit timestamp+machine+sequence, time-sortable, needs worker IDs), or DB ticket/range servers.
> Snowflake is the common answer.
> *Follow-ups:* Why are time-sortable IDs nice for a B-tree index? (sequential inserts, good locality.)
> `Hard` · `Amazon`

> **Q13. Fan-out on write vs fan-out on read (news feed)?**
> Fan-out on write pushes each post into followers' feeds at write time (fast reads, expensive for
> celebrities). Fan-out on read builds the feed at read time (cheap writes, slower reads). Real
> systems use a hybrid - precompute for most, read-time merge for high-follower accounts.
> *Follow-ups:* Why is a celebrity with 100M followers a problem for fan-out on write?
> `Hard` · `Meta`

> **Q14. What's a CDN and when does it help?**
> Edge caching of content close to users to cut latency and offload the origin. Great for static
> assets and cacheable responses; also absorbs spikes and adds DDoS protection. Less useful for
> highly personalized/dynamic data.
> *Follow-ups:* How does content get invalidated at the edge? (TTL, purge/invalidation API.)
> `Med` · `MAANG`

> **Q15. What is a rate limiter and which algorithm would you pick?**
> Caps requests per client per window to prevent abuse/overload. Token bucket allows bursts, leaky
> bucket smooths, sliding-window counter balances accuracy and memory. Store counters in Redis for a
> distributed limit; enforce at the gateway and/or per service.
> *Follow-ups:* How do you rate-limit across many app servers? (shared Redis counter, atomic incr.)
> `Med` · `MAANG`

> **Q16. How do you design for high availability?**
> Remove single points of failure via redundancy (multiple instances/AZs/regions), health checks +
> failover, load balancing, replication, and graceful degradation. Measure with availability "nines"
> (99.99% ≈ 52 min downtime/year).
> *Follow-ups:* What's the difference between failover and load balancing?
> `Med` · `MAANG`

> **Q17. What is a circuit breaker?**
> A resilience pattern: after repeated failures to a dependency, "open" the circuit and fail fast
> (skip calling it) for a cooldown, then probe with a trial request before closing again. Prevents
> cascading failures and gives the dependency time to recover. See
> [Microservices](../SystemDesign/components/microservices.md).
> *Follow-ups:* How does it differ from a retry? (retry hammers; breaker stops hammering.)
> `Hard` · `Amazon`

> **Q18. Strong vs eventual consistency - when each?**
> Strong: every read sees the latest write (needed for balances, inventory, uniqueness). Eventual:
> replicas converge over time (fine for feeds, counts, catalogs) and buys availability + low latency.
> Choose per data type, not globally.
> *Follow-ups:* How do you make eventual consistency acceptable? (read-your-writes, UI cues.)
> `Med` · `MAANG`

> **Q19. What is idempotency and why does it matter in APIs?**
> An idempotent operation has the same effect whether applied once or many times, so clients can
> safely retry after a timeout without double-charging or duplicating. Implement with an idempotency
> key the server dedups on.
> *Follow-ups:* Which HTTP methods are idempotent by spec? (GET, PUT, DELETE.)
> `Med` · `Amazon`

> **Q20. How do you approach a system design interview?**
> Clarify functional + non-functional requirements, estimate scale, sketch a high-level design, then
> deep-dive the bottlenecks and trade-offs - talking aloud and starting simple before scaling. See
> the framework in [System Design Guide](../SystemDesign/SystemDesignGuide.md).
> *Follow-ups:* What's the most common mistake? (jumping to a solution before clarifying scope.)
> `Med` · `MAANG`

> **Q21. How would you scale a read-heavy system?**
> Add caching (CDN + Redis), read replicas, and denormalized/precomputed views; push static content
> to a CDN. Identify the read/write ratio first - read-heavy points to caching + replicas, write-heavy
> to sharding + queues.
> *Follow-ups:* What consistency cost do read replicas introduce? (replication lag.)
> `Med` · `MAANG`

> **Q22. What is a single point of failure and how do you find one?**
> Any component whose failure takes down the system (one DB, one LB, one region). Find them by
> tracing the request path and asking "what if this dies?" Remove via redundancy and failover.
> *Follow-ups:* Is a single load balancer a SPOF, and how do you fix it? (yes - redundant LBs + DNS/anycast.)
> `Med` · `Amazon`

---

**Related:** [System Design Guide](../SystemDesign/SystemDesignGuide.md) ·
[Distributed Systems](../SystemDesign/DistributedSystemsConcepts.md) ·
[Databases Q&A](qa-databases.md) · [Caching Q&A](qa-caching.md)
