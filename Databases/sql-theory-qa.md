# 🧠 SQL Theory - Q&A

> The conceptual SQL questions interviewers ask, answer-first. Deeper internals (ACID, isolation,
> MVCC, index structures) live in [Database Internals](../Fundamentals/databases-internals.md)
> - this links there rather than repeating. Query practice: [SQL Query Patterns](sql-query-patterns.md).

---

> **Q1. What is normalization? Walk 1NF → 3NF.**
> Organizing tables to remove redundancy and update anomalies. **1NF:** atomic columns, no repeating
> groups. **2NF:** 1NF + every non-key column depends on the *whole* primary key (no partial
> dependency). **3NF:** 2NF + no non-key column depends on another non-key column (no transitive
> dependency). BCNF is a stricter 3NF.
> *Follow-ups:* When do you denormalize? (read-heavy/analytical paths, avoid joins.)

> **Q2. Normalization vs denormalization - the trade-off?**
> Normalized: less redundancy, fewer update anomalies, but reads need joins. Denormalized: duplicate
> data for join-free fast reads, but writes must keep copies in sync. Normalize for write-heavy OLTP;
> denormalize for read-heavy/OLAP and NoSQL. See [Database Internals](../Fundamentals/databases-internals.md).
> *Follow-ups:* How do you keep denormalized copies consistent? (app logic, triggers, async updates.)

> **Q3. Primary vs foreign vs composite vs candidate key?**
> Primary: the chosen unique row identifier (not null). Candidate: any column set that *could* be the
> primary key. Composite: a key made of multiple columns. Foreign: a column referencing another
> table's primary key (enforces referential integrity).
> *Follow-ups:* Can a table have multiple candidate keys? (yes; you pick one as primary.)

> **Q4. When does an index help, and when does it hurt?**
> Helps reads that filter/join/sort on the indexed column(s) by avoiding full scans (O(log n) via a
> B-tree). Hurts writes (every insert/update maintains the index) and costs storage. Low-selectivity
> columns (e.g. boolean) barely help. Index what you query, not everything.
> *Follow-ups:* Why is indexing a boolean column usually pointless? (low selectivity → scan anyway.)

> **Q5. What is a covering index?**
> An index that contains *all* columns a query needs, so the DB answers it from the index alone
> without touching the table ("index-only scan"). Great for hot read queries; costs more storage and
> write overhead.
> *Follow-ups:* How is this different from a normal index? (normal index still fetches the row.)

> **Q6. Why does composite index column order matter?**
> An index on `(a, b)` is sorted by `a` then `b`, so it serves queries on `a` or `a, b` - but not
> `b` alone (leftmost-prefix rule). Put the most selective / most-filtered column first, matching
> your query patterns.
> *Follow-ups:* Does `(a,b)` help `WHERE b = ?`? (no - b isn't a leading prefix.)

> **Q7. What does EXPLAIN tell you?**
> The query planner's execution plan: which indexes are used, join order/algorithm (nested loop,
> hash, merge), and estimated rows/cost. You use it to spot full scans where an index should apply,
> bad join orders, or missing indexes.
> *Follow-ups:* You see a "seq scan" on a big table - what do you check? (missing/unused index,
> low selectivity, stale stats.)

> **Q8. What is a transaction and the ACID properties?**
> A group of operations that commit all-or-nothing. **A**tomicity (all or none), **C**onsistency
> (constraints stay valid), **I**solation (concurrent txns don't corrupt each other), **D**urability
> (committed survives crashes). Details: [Database Internals](../Fundamentals/databases-internals.md).
> *Follow-ups:* How is atomicity/durability implemented? (write-ahead log.)

> **Q9. Explain isolation levels and their anomalies.**
> Read Uncommitted (allows dirty reads), Read Committed (no dirty), Repeatable Read (no
> non-repeatable), Serializable (no phantoms). Higher = fewer anomalies, less concurrency. Full table
> in [Database Internals](../Fundamentals/databases-internals.md).
> *Follow-ups:* What's a phantom read? (a range re-query returns new/removed rows.)

> **Q10. ACID consistency vs CAP consistency?**
> ACID consistency = a transaction leaves the DB valid (constraints hold). CAP consistency = every
> read sees the latest write across nodes (linearizability). Different concepts; conflating them is a
> common slip.
> *Follow-ups:* Which does a single-node DB always give? (ACID consistency.)

> **Q11. What is the N+1 query problem?**
> Fetching a list then issuing one query per item (1 + N queries), often from ORM lazy loading. Fix
> with a join, eager loading, or batching children into one `IN (...)`.
> *Follow-ups:* How would you detect it? (query logs showing repeated similar queries.)

> **Q12. WHERE vs HAVING?**
> WHERE filters rows *before* grouping; HAVING filters groups *after* aggregation. Aggregates
> (`COUNT`, `AVG`) can only appear in HAVING, not WHERE.
> *Follow-ups:* Can you use a column alias in WHERE? (usually no - it's evaluated before SELECT.)

> **Q13. DELETE vs TRUNCATE vs DROP?**
> DELETE removes rows (logged, can have WHERE, fires triggers). TRUNCATE removes all rows fast
> (minimal logging, no WHERE, resets identity). DROP removes the whole table (schema + data).
> *Follow-ups:* Which can you roll back? (DELETE always; TRUNCATE/DROP depend on the DB.)

> **Q14. What is a deadlock in a database and how do you avoid it?**
> Two transactions each hold a lock the other needs, waiting forever. The DB detects it and kills a
> victim. Avoid by acquiring locks in a consistent order and keeping transactions short. See
> [Concurrency & Parallelism](../Fundamentals/concurrency-and-parallelism.md).
> *Follow-ups:* Optimistic vs pessimistic locking? (version-check-and-retry vs lock up front.)

> **Q15. When would you use a materialized view?**
> When an expensive aggregation/join is read often but changes rarely - precompute and store it,
> refreshing periodically. Trades storage + staleness for fast reads. A regular view is just a saved
> query (no storage).
> *Follow-ups:* View vs materialized view? (view = query alias; materialized = stored result.)

---

## Related

- Internals (ACID, isolation, MVCC, indexing) → [Database Internals](../Fundamentals/databases-internals.md)
- Query patterns → [SQL Query Patterns](sql-query-patterns.md)
- Short Q&A → [Databases Q&A](../QA-Bank/qa-databases.md)
- SQL vs NoSQL + scaling → [SQL vs NoSQL & Scaling](sql-vs-nosql-and-scaling.md)
