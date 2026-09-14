# ⚖️ SQL vs NoSQL & Scaling

> The "which database would you pick and why" round, plus how you scale it and the follow-ups an
> interviewer chains after your first answer. Trade-off internals: [Database Internals](../Fundamentals/databases-internals.md);
> sharding: [Database Sharding](../SystemDesign/components/database-sharding.md); CAP/replication:
> [Distributed Systems](../SystemDesign/DistributedSystemsConcepts.md).

---

## The "which DB" framing `[core]`

Don't answer "SQL" or "NoSQL" reflexively - reason from requirements:

1. **Data shape & relationships** - highly relational with joins/transactions → SQL. Flexible/nested
   or schema-varying → document.
2. **Access patterns** - ad-hoc queries across dimensions → SQL. Known, key-based access at scale →
   NoSQL.
3. **Consistency needs** - money/inventory/uniqueness → strong (SQL or a strongly-consistent store).
   Feeds/counts/catalogs → eventual is fine.
4. **Scale & write volume** - massive writes beyond one node → NoSQL/wide-column or sharded SQL.
5. **Team/ops** - SQL is well-understood and flexible; NoSQL commits you to your access patterns.

**Good answer shape:** "It's mostly relational with transactional integrity (orders + payments), so
I'd start with a relational DB (Postgres); for the high-write event log I'd use a wide-column store."
Polyglot persistence - right tool per workload - reads as senior.

---

## Quick comparison `[core]`

| | SQL (relational) | NoSQL |
|--|------------------|-------|
| Schema | fixed, enforced | flexible |
| Joins / ad-hoc queries | strong | weak/none (model per query) |
| Transactions | ACID across rows/tables | often limited to one key/document |
| Scaling | vertical + read replicas; sharding is manual | horizontal by design |
| Consistency | strong | tunable / eventual |
| Fit | relationships, transactions, reporting | scale, flexible schema, known access patterns |

---

## Scaling a SQL database `[core]`

The usual ladder (do the cheap thing first):
1. **Indexes + query tuning** - fix the slow queries before adding hardware.
2. **Vertical scale** - bigger box (simple, but a ceiling + SPOF).
3. **Read replicas** - offload reads; introduces replication lag (stale reads).
4. **Caching** - Redis in front for hot reads (see [Caching](../SystemDesign/components/caching.md)).
5. **Sharding** - split writes across nodes when one can't keep up (last resort - adds cross-shard
   pain). See [Database Sharding](../SystemDesign/components/database-sharding.md).

*Follow-up hook:* what breaks when you shard? (cross-shard joins/transactions, rebalancing, hot
shards → use sagas, denormalization, good shard key.)

---

## Partition / shard key choice `[core]`

The single most important scaling decision. A good key:
- **Distributes evenly** (avoid hot partitions - e.g. don't shard by `country` if 80% are one
  country).
- **Matches your access pattern** so common queries hit one partition (avoid scatter-gather).
- Is **immutable** (changing a shard key means moving data).

Consistent hashing minimizes reshuffling when nodes change - see [Hashing](../Fundamentals/hashing.md).
*Follow-up hook:* a celebrity/hot key overloads one shard - fix? (sub-shard the key, cache, or
replicate it.)

---

## Consistency & CAP in the decision `[advanced]`

Once data is replicated/sharded, CAP forces the consistency-vs-availability choice during a
partition, and PACELC adds latency-vs-consistency otherwise. Map it to the domain:
- **Strong consistency:** payments, inventory-at-checkout, unique usernames.
- **Eventual consistency:** feeds, view counts, product catalogs, recommendations.

Choose per data type, not globally. Full treatment: [Distributed Systems](../SystemDesign/DistributedSystemsConcepts.md).

---

## The chained follow-ups (what comes after your first answer)

Interviewers rarely stop at "which DB." Be ready for:
- "It's getting slow - how do you scale reads?" → indexes, replicas, cache.
- "Writes are the bottleneck now?" → shard; pick a key; handle hot shards.
- "How do you keep replicas consistent?" → sync vs async, replication lag, read-your-writes.
- "Cross-shard transaction?" → avoid; use sagas / eventual consistency.
- "Schema change on a huge table?" → online migration, backfill, dual-write.

---

## Common interview traps

- Picking NoSQL "for scale" without access patterns to justify it.
- Jumping straight to sharding before indexes/replicas/caching.
- A shard key that creates hot partitions (low-cardinality or skewed).
- Assuming read replicas are instantly consistent (lag is real).
- Treating the whole app as one consistency model instead of per-data-type.

## Related

- Internals & SQL-vs-NoSQL trade-offs → [Database Internals](../Fundamentals/databases-internals.md)
- Sharding deep-dive → [Database Sharding](../SystemDesign/components/database-sharding.md)
- CAP / replication → [Distributed Systems](../SystemDesign/DistributedSystemsConcepts.md)
- NoSQL modeling → [NoSQL Types & Modeling](nosql-types-and-modeling.md)
