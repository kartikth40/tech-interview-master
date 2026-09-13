# 🗂️ NoSQL Types & Data Modeling

> The "which NoSQL store and how would you model it" material. Internals (SQL vs NoSQL trade-offs,
> replication) live in [Fundamentals/databases-internals.md](../Fundamentals/databases-internals.md);
> sharding in [database-sharding.md](../SystemDesign/components/database-sharding.md). The decision
> framing is in [sql-vs-nosql-and-scaling.md](sql-vs-nosql-and-scaling.md).

---

## 🧩 The four families `[core]`

| Type | Model | Strength | Example | Use when |
|------|-------|----------|---------|----------|
| **Key-value** | `key → opaque value` | fastest lookups, simple | Redis, DynamoDB | sessions, caches, simple lookups by key |
| **Document** | JSON-like documents | flexible nested objects, query fields | MongoDB | catalogs, user profiles, content |
| **Wide-column** | rows with dynamic column families | huge write throughput, time-series | Cassandra, HBase | events, logs, sensor/time data |
| **Graph** | nodes + edges | traversing relationships | Neo4j | social graphs, recommendations, fraud |

**Pick-the-store heuristic:** what's the *primary access pattern*? Lookup by key → KV. Nested objects
queried by field → document. Massive writes + range scans by key → wide-column. Multi-hop
relationship traversal → graph.

---

## 🎯 Access-pattern-first modeling `[core]`

The biggest mindset shift from SQL: in NoSQL you **model for your queries, not for normalization**.
You don't design normalized tables then figure out queries — you list the queries first and shape the
data so each is a single efficient read.
- No joins (mostly), so related data is **denormalized/embedded** or duplicated.
- The **partition key** must match how you read (see sharding), or you'll scatter-gather.
- Adding a new access pattern often means adding a new table/index with duplicated data.

---

## 🪆 Embed vs reference (document modeling) `[core]`

```text
# Embed: store related data inside the document
Order { id, items: [ {sku, qty, price}, ... ], total }   # one read gets everything

# Reference: store an ID, fetch separately
Order { id, item_ids: [123, 456] }                        # extra lookups, but items shared/large
```

| | Embed | Reference |
|--|-------|-----------|
| Reads | one read gets it all | multiple reads |
| Writes | update whole doc | update pieces independently |
| Best when | data read together, bounded size, owned by parent | shared, large, or unbounded relationships |

**Rule of thumb:** embed "has-a, read-together, bounded" data; reference "shared, large, or
many-to-many" data. Watch the document size limit (e.g. Mongo 16 MB) — unbounded arrays are a smell.

---

## 🔎 Secondary indexes `[advanced]`

NoSQL stores index by the primary/partition key by default; querying by *other* attributes needs a
**secondary index**, which the store maintains for you (local or global). They cost write throughput
and storage, and global secondary indexes may be eventually consistent. If you find yourself needing
many secondary indexes, a relational DB might fit better.
*Follow-up hook:* why can a DynamoDB global secondary index be stale? (async maintenance.)

---

## ⚖️ Denormalization trade-offs `[core]`

NoSQL leans on denormalization to avoid joins: duplicate data so each query is one read. The cost is
**write amplification and consistency work** — when the duplicated field changes, you must update
every copy (often async, accepting brief inconsistency). You're trading write complexity and eventual
consistency for read speed and scale.

---

## ⚠️ Common interview traps

- Modeling NoSQL like SQL (normalized tables) and then being surprised there are no joins.
- Choosing NoSQL "because it scales" without stating the access patterns that justify it.
- Unbounded embedded arrays (hitting document size limits, hot documents).
- Assuming secondary indexes are free and strongly consistent.
- Picking a graph DB when a couple of joins in SQL would do — reserve it for genuine multi-hop
  traversal.

## 🔗 Related

- SQL vs NoSQL decision + scaling → [sql-vs-nosql-and-scaling.md](sql-vs-nosql-and-scaling.md)
- Internals / trade-offs → [Fundamentals/databases-internals.md](../Fundamentals/databases-internals.md)
- Partition keys / sharding → [SystemDesign/components/database-sharding.md](../SystemDesign/components/database-sharding.md)
- Short Q&A → [QA-Bank/qa-databases.md](../QA-Bank/qa-databases.md)
