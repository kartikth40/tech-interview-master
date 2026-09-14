# 🗄️ Database Internals

!!! tip "Explain in 2 min"
    A database's job is to store data durably and let many clients read/write it
    correctly at once. **ACID** captures the correctness guarantees; **isolation levels** are the dial
    that trades strictness for concurrency. Under the hood, **indexes** (usually B-trees) turn O(n)
    scans into O(log n) lookups at the cost of slower writes and more space. To scale, we **replicate**
    (copies for availability and read throughput) and **partition/shard** (split data across nodes for
    write throughput and size). The moment data lives on multiple nodes, **CAP/PACELC** forces a
    choice between consistency and availability/latency. **SQL vs NoSQL** is mostly a question of
    whether you need strong relational guarantees and ad-hoc queries, or horizontal scale and a
    flexible schema.

---

## ACID `[core]`

| Property | Meaning |
|----------|---------|
| **Atomicity** | a transaction is all-or-nothing; partial effects never persist |
| **Consistency** | a transaction moves the DB from one valid state to another (constraints hold) |
| **Isolation** | concurrent transactions don't corrupt each other's view |
| **Durability** | once committed, data survives crashes (via write-ahead log) |

Atomicity and durability are usually implemented with a **write-ahead log (WAL)**: changes are
logged before being applied, so a crash can be replayed or rolled back.

---

## Isolation levels & anomalies `[core]`

Stricter isolation = fewer anomalies but less concurrency. The anomalies, weakest first:

- **Dirty read** - read another transaction's uncommitted change.
- **Non-repeatable read** - re-read a row and see a different value (someone updated it).
- **Phantom read** - re-run a range query and see new/removed rows.

| Level | Prevents | Still allows |
|-------|----------|--------------|
| Read Uncommitted | - | dirty, non-repeatable, phantom |
| Read Committed | dirty | non-repeatable, phantom |
| Repeatable Read | dirty, non-repeatable | phantom |
| Serializable | all | (behaves as if serial) - lowest concurrency |

Default is usually Read Committed (Postgres, Oracle) or Repeatable Read (MySQL InnoDB). Reach for
Serializable only when correctness demands it.

---

## Indexing `[core]`

An index is a secondary structure that makes lookups fast without scanning the whole table.

| Index type | Strength | Weakness | Used by |
|------------|----------|----------|---------|
| **B-tree / B+tree** | range + equality, sorted scans | write amplification | most RDBMS default |
| **Hash** | O(1) equality | no range queries | in-memory, some engines |
| **LSM-tree** | very fast writes (sequential) | reads may check multiple levels | Cassandra, RocksDB, LevelDB |

**Trade-off:** every index speeds reads but slows writes (each write updates the indexes) and costs
storage. Index the columns you filter/join/sort on - not everything. A **composite index** on
`(a, b)` helps queries on `a` or `a,b` but not `b` alone (leftmost-prefix rule).

- **B-tree vs LSM-tree** is a classic follow-up: B-trees update in place (read-optimized); LSM-trees
  append to memtables and flush sorted files, compacting later (write-optimized). Pick LSM for
  write-heavy ingest, B-tree for balanced/read-heavy.
- See [DSA/data-structures/tree/](../DSA/data-structures/tree/) for tree/BST/segment-tree code and
  [Hashing](hashing.md) for hash-index intuition.

---

## Normalization vs denormalization `[core]`

- **Normalization** removes redundancy by splitting into related tables (3NF). Fewer update
  anomalies, but reads need joins.
- **Denormalization** duplicates data to avoid joins. Faster reads, but writes must keep copies in
  sync.

**Rule of thumb:** normalize for write-heavy transactional systems (OLTP); denormalize for
read-heavy or analytical paths (OLAP), and for NoSQL where joins are expensive or unavailable.

---

## SQL vs NoSQL `[core]`

| | SQL (relational) | NoSQL |
|--|------------------|-------|
| Schema | fixed, enforced | flexible / schemaless |
| Scaling | vertical + read replicas | horizontal by design |
| Queries | rich ad-hoc joins | access-pattern-first |
| Consistency | strong (ACID) | often eventual (BASE) |
| Fit | transactions, reporting, relationships | huge scale, simple access patterns, flexible docs |

NoSQL families: **key-value** (Redis, DynamoDB), **document** (MongoDB), **wide-column**
(Cassandra), **graph** (Neo4j). "NoSQL scales better" is only true when your access patterns are
known up front - model the queries first.

---

## Replication `[core]`

Keeping copies of data on multiple nodes for **availability** and **read throughput**.

- **Single-leader** - one node takes writes, replicates to followers. Simple, no write conflicts;
  follower reads can be stale (replication lag).
- **Multi-leader** - multiple write nodes (e.g. multi-region). Better write availability, but
  conflict resolution needed.
- **Leaderless** (Dynamo-style) - write to several nodes, read from several, use quorums (`W + R >
  N`) for consistency.

**Sync vs async replication:** sync is durable but slow (wait for followers); async is fast but can
lose the newest writes on leader failure. Replication lag is the source of "I wrote it but can't
read it back" bugs - fix with read-your-writes routing.

---

## Partitioning / sharding `[core]`

Splitting data *across* nodes so no single node holds it all - the key to write scaling. Strategies
(range, hash, consistent hashing) and the rebalancing/hot-shard problems have a canonical home:
👉 [Database Sharding](../SystemDesign/components/database-sharding.md).
Consistent-hashing intuition is in [Hashing](hashing.md).

Replication and partitioning are orthogonal and usually combined: shard for size/writes, replicate
each shard for availability/reads.

---

## CAP / PACELC `[advanced]`

Once data is distributed, a network **partition (P)** forces a choice between **consistency (C)** and
**availability (A)** - you can't have both during a partition. **PACELC** extends it: *else* (when
there's no partition) you still trade **latency (L)** vs **consistency (C)**.

This is a system-design cornerstone with a full treatment (plus consensus, quorums, sagas) here:
👉 [Distributed Systems](../SystemDesign/DistributedSystemsConcepts.md).

---

## MVCC & concurrency control `[advanced]`

**Multi-Version Concurrency Control** lets readers and writers not block each other: each write
creates a new *version* of a row, and each transaction reads a consistent snapshot. Used by Postgres
and MySQL InnoDB. It's the optimistic-flavored counterpart to lock-based control -
see optimistic vs pessimistic locking in [Concurrency & Parallelism](concurrency-and-parallelism.md).

Old versions accumulate and must be cleaned up (Postgres `VACUUM`) - a real operational gotcha.

---

## Connection pooling `[core]`

Opening a DB connection is expensive (TCP + auth + session setup). A **connection pool** keeps a set
of open connections and hands them out, capping total connections so the DB isn't overwhelmed. This
is the DB-side analogue of a thread pool. Under-sizing throttles the app; over-sizing exhausts DB
resources.

---

## Common interview traps

- Confusing **consistency** in ACID (constraints valid) with **consistency** in CAP (all nodes see
  the same data) - different meanings.
- Saying "just add indexes" - indexes slow writes and cost space; they're a trade-off.
- Assuming replicas are instantly consistent (replication lag is real).
- Treating CAP as "pick 2 always" - the choice only bites *during a partition*; PACELC captures the
  normal-operation latency trade-off.
- Choosing NoSQL "because it scales" without knowing the access patterns.

## Related

- Q&A drills: [Databases Q&A](../QA-Bank/qa-databases.md)
- [Sharding / partitioning deep-dive](../SystemDesign/components/database-sharding.md)
- [CAP / replication / consensus](../SystemDesign/DistributedSystemsConcepts.md)
- [Caching](../SystemDesign/components/caching.md) · [Hashing](hashing.md) · [Concurrency](concurrency-and-parallelism.md)
