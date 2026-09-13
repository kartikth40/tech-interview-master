# ❓ Databases — Q&A

> Pairs with [Fundamentals/databases-internals.md](../Fundamentals/databases-internals.md). Format
> and tag legend: [QA-Bank/README.md](README.md).

---

> **Q1. What does ACID stand for?**
> Atomicity (all-or-nothing), Consistency (constraints stay valid), Isolation (concurrent txns don't
> corrupt each other), Durability (committed data survives crashes). Atomicity and durability are
> typically backed by a write-ahead log.
> *Follow-ups:* How is durability implemented? (WAL / fsync.)
> `Easy` · `MAANG`

> **Q2. Explain isolation levels and the anomalies they prevent.**
> From weakest: Read Uncommitted (allows dirty reads), Read Committed (no dirty reads),
> Repeatable Read (no non-repeatable reads), Serializable (no phantoms; behaves as if serial).
> Stronger isolation means fewer anomalies but less concurrency.
> *Follow-ups:* What's a phantom read?
> `Hard` · `MAANG`

> **Q3. Dirty read vs non-repeatable read vs phantom read?**
> Dirty read: seeing another txn's uncommitted change. Non-repeatable read: re-reading a row and
> getting a different value. Phantom: re-running a range query and seeing new/removed rows. Each is
> prevented at a higher isolation level.
> *Follow-ups:* Which level does most databases default to? (Read Committed / Repeatable Read.)
> `Hard` · `Google`

> **Q4. Why does an index speed up reads but slow writes?**
> An index is a secondary sorted structure (usually a B-tree) that avoids full scans for lookups. But
> every insert/update/delete must also update the indexes, adding write cost and storage — so you
> index the columns you filter/join/sort on, not everything.
> *Follow-ups:* When would you NOT add an index? (write-heavy, low-selectivity columns.)
> `Med` · `MAANG`

> **Q5. B-tree vs LSM-tree index?**
> B-trees update in place and are read-optimized (balanced, good for range + point queries).
> LSM-trees append to in-memory memtables and flush sorted files, compacting later — write-optimized
> but reads may touch multiple levels. Pick LSM for write-heavy ingest (Cassandra, RocksDB), B-tree
> for balanced/read-heavy.
> *Follow-ups:* How do bloom filters help LSM reads? (skip SSTables that can't contain the key.)
> `Hard` · `Amazon`

> **Q6. What is a composite index and the leftmost-prefix rule?**
> A composite index on (a, b) is sorted by a then b. It can serve queries on `a` or `a, b`, but not
> `b` alone, because the ordering only groups by the leading column(s). Column order in the index
> matters.
> *Follow-ups:* Does it help `WHERE b = ? ORDER BY a`? (partially — depends.)
> `Hard` · `Google`

> **Q7. Normalization vs denormalization?**
> Normalization removes redundancy by splitting into related tables — fewer update anomalies, but
> reads need joins. Denormalization duplicates data to avoid joins — faster reads, but writes must
> keep copies in sync. Normalize for write-heavy OLTP; denormalize for read-heavy/analytical paths
> and NoSQL.
> *Follow-ups:* Why is denormalization common in NoSQL? (joins are expensive/unavailable.)
> `Med` · `MAANG`

> **Q8. SQL vs NoSQL — how do you choose?**
> SQL: fixed schema, strong ACID, rich ad-hoc joins, scales vertically + read replicas — good for
> transactions and relationships. NoSQL: flexible schema, horizontal scale, access-pattern-first,
> often eventual consistency — good for huge scale and simple/known access patterns.
> *Follow-ups:* "NoSQL scales better" — when is that misleading? (only if access patterns fit.)
> `Med` · `MAANG`

> **Q9. What are the NoSQL families?**
> Key-value (Redis, DynamoDB), document (MongoDB), wide-column (Cassandra), graph (Neo4j). You pick
> based on access patterns: KV for simple lookups, document for nested objects, wide-column for
> large write-heavy tables, graph for relationship traversal.
> *Follow-ups:* When would a graph DB beat a relational one? (deep multi-hop relationships.)
> `Med` · `Startups`

> **Q10. Explain database replication and its trade-offs.**
> Copies of data on multiple nodes for availability and read scaling. Single-leader (simple, no
> write conflicts, followers can be stale), multi-leader (write availability, conflict resolution),
> leaderless/quorum (Dynamo-style, W+R>N). Sync replication is durable but slow; async is fast but
> can lose recent writes on failover.
> *Follow-ups:* What is replication lag and what bug does it cause?
> `Hard` · `Amazon`

> **Q11. What is replication lag and how do you handle "read-your-writes"?**
> Async followers can be behind the leader, so a user may not see their own just-written data.
> Fix by routing that user's reads to the leader (or a synced replica) for a short window, or track a
> version/timestamp and read from a replica that's caught up.
> *Follow-ups:* What is monotonic-read consistency?
> `Hard` · `MAANG`

> **Q12. Replication vs partitioning (sharding)?**
> Replication copies the same data to multiple nodes (availability, read throughput). Partitioning
> splits different data across nodes (write throughput, size). They're orthogonal and usually
> combined: shard for scale, replicate each shard for availability.
> *Follow-ups:* Why can't replication alone scale writes? (every replica takes every write.)
> `Med` · `MAANG`

> **Q13. What sharding strategies exist and what's the risk?**
> Range-based (good for range queries, risk of hotspots), hash-based (even distribution, no range
> queries), consistent hashing (minimal reshuffle on node changes). The main risk is a hot shard;
> mitigate with a good shard key and virtual nodes. See
> [database-sharding.md](../SystemDesign/components/database-sharding.md).
> *Follow-ups:* How do you pick a shard key?
> `Hard` · `Amazon`

> **Q14. What does the CAP theorem say?**
> During a network partition you must choose between consistency and availability — you can't have
> both. It only forces a choice *during a partition*; PACELC adds that even without one you trade
> latency vs consistency. See [DistributedSystemsConcepts.md](../SystemDesign/DistributedSystemsConcepts.md).
> *Follow-ups:* Is "CA" a real option? (not in a distributed system that can partition.)
> `Hard` · `MAANG`

> **Q15. ACID consistency vs CAP consistency — same thing?**
> No. ACID consistency means a transaction leaves the DB in a valid state (constraints hold). CAP
> consistency means every read sees the latest write across all nodes (linearizability). Conflating
> them is a common slip.
> *Follow-ups:* Which one does a single-node DB always give?
> `Hard` · `Google`

> **Q16. What is MVCC?**
> Multi-Version Concurrency Control: each write creates a new version of a row and each transaction
> reads a consistent snapshot, so readers and writers don't block each other. Used by Postgres and
> InnoDB. Old versions must be cleaned up (Postgres VACUUM).
> *Follow-ups:* How does MVCC relate to optimistic concurrency?
> `Hard` · `Google`

> **Q17. Why use connection pooling?**
> Opening a DB connection is expensive (TCP + auth + session setup). A pool keeps connections open
> and reuses them, and caps total connections so the DB isn't overwhelmed. Under-sizing throttles the
> app; over-sizing exhausts DB resources.
> *Follow-ups:* What happens when the pool is exhausted? (requests queue or time out.)
> `Med` · `MAANG`

> **Q18. What is a transaction and when do you need one?**
> A group of operations executed atomically — all commit or all roll back. You need one when
> multiple writes must be consistent together (transfer money: debit + credit) or when you rely on
> isolation to prevent concurrent anomalies.
> *Follow-ups:* How do you do transactions across shards/services? (avoid; use sagas.)
> `Med` · `Amazon`

> **Q19. What is a saga and when do you use it?**
> A pattern for distributed transactions across services: a sequence of local transactions, each
> with a compensating action to undo it if a later step fails. Used because cross-service 2PC is
> slow and fragile. See [DistributedSystemsConcepts.md](../SystemDesign/DistributedSystemsConcepts.md).
> *Follow-ups:* Orchestration vs choreography sagas?
> `Hard` · `Amazon`

> **Q20. When would you choose eventual consistency?**
> When availability and low latency matter more than every read being current, and the domain
> tolerates brief staleness (social feeds, view counts, product catalogs). Avoid it where correctness
> is critical (account balances, inventory at checkout).
> *Follow-ups:* How do you make eventual consistency acceptable to users? (read-your-writes, UI cues.)
> `Med` · `MAANG`

> **Q21. What causes the N+1 query problem and how do you fix it?**
> Fetching a list then issuing one query per item (1 + N queries), usually from lazy loading in an
> ORM. Fix with eager loading / a join / batching the child queries into one `IN (...)`.
> *Follow-ups:* How would you detect it? (query logs showing repeated similar queries.)
> `Med` · `Startups`

> **Q22. Optimistic vs pessimistic locking in a database?**
> Pessimistic locks rows up front (`SELECT ... FOR UPDATE`) — safe under contention, but blocks and
> risks deadlock. Optimistic uses a version column and only commits if unchanged, retrying on
> conflict — better when conflicts are rare.
> *Follow-ups:* Which fits a high-contention counter? (neither scales — consider sharded counters.)
> `Hard` · `Amazon`

---

**Related:** [Fundamentals/databases-internals.md](../Fundamentals/databases-internals.md) ·
[qa-hashing.md](qa-hashing.md) · [qa-system-design-concepts.md](qa-system-design-concepts.md) ·
[qa-caching.md](qa-caching.md) · **SQL/NoSQL deep-dive + query practice:**
[Databases/](../Databases/README.md)
