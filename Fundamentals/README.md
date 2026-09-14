# CS Fundamentals

The concept notes an interviewer *probes* - hashing, concurrency, OS, networking, DB
internals, security, OOP, memory, estimation. This pillar answers the **"explain X in 2
minutes"** and **"why X vs Y"** questions that come up outside of coding and system-design
rounds (and inside them, as follow-ups).

## How to use this

- Each file is **interview-length**: intuition, key trade-offs, and "when would you use X vs Y" -
  not a textbook. If you want the 2-minute spoken answer, read the **"Explain in 2 min"** box at
  the top of each concept.
- Topics are tagged **[core]** (must-know for entry-to-mid level) or **[advanced]** (rarely asked, nice
  to have for senior roles).
- Concepts with a canonical deep-dive elsewhere (caching, sharding, CAP) are **linked, not
  re-explained** - go there for depth.
- Pair each concept with its **Q&A file** (see map below) for rapid-fire drilling.

## Concept files

| # | File | Covers | Depth |
|---|------|--------|-------|
| A1 | [Operating Systems](operating-systems.md) | process vs thread, context switch, scheduling, virtual memory/paging, deadlock, syscalls | core |
| A2 | [Concurrency & Parallelism](concurrency-and-parallelism.md) | concurrency vs parallelism, threads vs async, locks, race conditions, deadlock, thread pools, Amdahl, GIL | core |
| A3 | [Networking](networking.md) | OSI/TCP-IP, TCP vs UDP, HTTP/1.1/2/3, TLS handshake, DNS, "URL → page", WebSockets, CDN | core |
| A4 | [Database Internals](databases-internals.md) | ACID, isolation levels, indexing, normalization, SQL vs NoSQL, replication, partitioning, CAP/PACELC, MVCC | core |
| A5 | [Hashing](hashing.md) | hash functions, collision handling, load factor/resizing, consistent hashing, bloom filters, crypto vs table hash, HMAC | core |
| A6 | [Security Fundamentals](security-fundamentals.md) | authN vs authZ, sessions/JWT/OAuth2, password hashing, TLS, XSS/CSRF/SQLi/SSRF, rate limiting | core |
| A7 | [OOP & Language Concepts](oop-and-language-concepts.md) | 4 OOP pillars, SOLID, composition vs inheritance, interface vs abstract, immutability, generics | core |
| A8 | [Memory & Runtime](memory-and-runtime.md) | stack vs heap, garbage collection, memory leaks, reference counting, Python GIL/generators/decorators | advanced |
| A9 | [Latency Numbers & Estimation](latency-numbers-and-estimation.md) | numbers every engineer should know, back-of-envelope drills, QPS/storage/bandwidth math | core |
| A10 | [Distributed Systems](../SystemDesign/DistributedSystemsConcepts.md) | CAP/PACELC, replication, consensus, sagas | advanced |
| A11 | [Bloom Filters & Probabilistic Structures](bloom-filters-and-probabilistic.md) | bloom/counting bloom, count-min sketch, HyperLogLog - approximate answers, tiny memory | advanced |
| A12 | [Serialization & Schemas](serialization-and-schemas.md) | JSON vs Protobuf vs Avro, schema evolution/compat, schema registry | core |
| A13 | [Idempotency & Delivery Semantics](idempotency-and-delivery-semantics.md) | idempotency keys, at-least/at-most/exactly-once, dedup, retries | core |
| A14 | [Time & Ordering](time-and-ordering.md) | wall-clock skew/NTP, happens-before, Lamport clocks, vector clocks | advanced |

## Concept → Q&A map

The [Q&A Bank](../QA-Bank/README.md) holds short, defensible interview answers. Each concept note
maps to a Q&A file for drilling:

| Concept | Q&A file |
|---------|----------|
| Operating systems | [Operating Systems Q&A](../QA-Bank/qa-operating-systems.md) |
| Concurrency & parallelism | [Concurrency Q&A](../QA-Bank/qa-concurrency.md) |
| Networking | [Networking Q&A](../QA-Bank/qa-networking.md) |
| Databases | [Databases Q&A](../QA-Bank/qa-databases.md) |
| Hashing | [Hashing Q&A](../QA-Bank/qa-hashing.md) |
| Caching | [Caching Q&A](../QA-Bank/qa-caching.md) |
| Security | [Security Q&A](../QA-Bank/qa-security.md) |
| OOP & design | [OOP & Design Q&A](../QA-Bank/qa-oop-design.md) |
| System design concepts | [System Design Concepts Q&A](../QA-Bank/qa-system-design-concepts.md) |
| Python language | [Python Language Q&A](../QA-Bank/qa-language-python.md) |

## Related material (canonical homes - don't duplicate, link)

- **Caching** strategies & eviction → [Caching](../SystemDesign/components/caching.md)
- **Sharding / partitioning** → [Database Sharding](../SystemDesign/components/database-sharding.md)
- **CAP / replication / consensus** → [Distributed Systems](../SystemDesign/DistributedSystemsConcepts.md)
- **SOLID / GoF patterns** → [Low-Level Design](../SystemDesign/LowLevelDesign.md)
- **Latency / estimation numbers** → [System Design Guide](../SystemDesign/SystemDesignGuide.md)
- **Hash-table / heap / trie code** → [DSA/data-structures/](../DSA/data-structures/)
