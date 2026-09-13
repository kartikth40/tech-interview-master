# Databases - Interview Deep-Dive

Database knowledge shows up in almost every SDE-1/SDE-2 loop - as a dedicated round, a system-design
follow-up, or a live SQL exercise. This section is the focused, interview-ready home for **the
questions actually asked** plus hands-on **query practice**.

It complements, and links to (rather than repeats), the existing DB material:
- **Theory / internals** → [Fundamentals/databases-internals.md](../Fundamentals/databases-internals.md)
  (ACID, isolation levels, indexing, MVCC, replication).
- **Short conceptual Q&A** → [QA-Bank/qa-databases.md](../QA-Bank/qa-databases.md).
- **Sharding / partitioning** → [SystemDesign/components/database-sharding.md](../SystemDesign/components/database-sharding.md).

## How to use

- **SQL rounds:** drill [sql-query-patterns.md](sql-query-patterns.md), then time yourself on
  [query-practice-set.md](query-practice-set.md).
- **Conceptual/theory rounds:** work through [sql-theory-qa.md](sql-theory-qa.md).
- **Design "which database" moments:** [nosql-types-and-modeling.md](nosql-types-and-modeling.md)
  and [sql-vs-nosql-and-scaling.md](sql-vs-nosql-and-scaling.md).

## Files

| File | Focus |
|------|-------|
| [sql-query-patterns.md](sql-query-patterns.md) | the query shapes interviewers ask (joins, windows, dedup, nth-highest) + what each tests |
| [sql-theory-qa.md](sql-theory-qa.md) | normalization, keys, indexing, EXPLAIN, transactions - Q&A style |
| [nosql-types-and-modeling.md](nosql-types-and-modeling.md) | KV/document/column/graph, pick-the-store, embed vs reference |
| [sql-vs-nosql-and-scaling.md](sql-vs-nosql-and-scaling.md) | "which DB and why", CAP/PACELC, replication, sharding, hot partitions |
| [query-practice-set.md](query-practice-set.md) | ~12 worked query problems with schema + expected output, easy → hard |

## Conventions

- **Interview-length:** a worked query + a short "what's tested" note - not a textbook chapter.
- **Trade-offs first:** "when would you use X vs Y" beats rote definitions.
- **Cross-link, don't duplicate:** internals live in `databases-internals.md`; this section
  references them.
