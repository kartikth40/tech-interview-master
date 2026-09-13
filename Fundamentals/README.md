# 🧠 CS Fundamentals

The concept notes an interviewer *probes* — hashing, concurrency, OS, networking, DB
internals, security, OOP, memory, estimation. This pillar answers the **"explain X in 2
minutes"** and **"why X vs Y"** questions that come up outside of coding and system-design
rounds (and inside them, as follow-ups).

## How to use this

- Each file is **interview-length**: intuition, key trade-offs, and "when would you use X vs Y" —
  not a textbook. If you want the 2-minute spoken answer, read the **"Explain in 2 min"** box at
  the top of each concept.
- Topics are tagged **[core]** (must-know for any SDE-1/2) or **[advanced]** (rarely asked, nice
  to have for SDE-2 / senior).
- Concepts with a canonical deep-dive elsewhere (caching, sharding, CAP) are **linked, not
  re-explained** — go there for depth.
- Pair each concept with its **Q&A file** (see map below) for rapid-fire drilling.

## Concept files

| # | File | Covers | Depth |
|---|------|--------|-------|
| A1 | [operating-systems.md](operating-systems.md) | process vs thread, context switch, scheduling, virtual memory/paging, deadlock, syscalls | core |
| A2 | [concurrency-and-parallelism.md](concurrency-and-parallelism.md) | concurrency vs parallelism, threads vs async, locks, race conditions, deadlock, thread pools, Amdahl, GIL | core |
| A3 | [networking.md](networking.md) | OSI/TCP-IP, TCP vs UDP, HTTP/1.1/2/3, TLS handshake, DNS, "URL → page", WebSockets, CDN | core |
| A4 | [databases-internals.md](databases-internals.md) | ACID, isolation levels, indexing, normalization, SQL vs NoSQL, replication, partitioning, CAP/PACELC, MVCC | core |
| A5 | [hashing.md](hashing.md) | hash functions, collision handling, load factor/resizing, consistent hashing, bloom filters, crypto vs table hash, HMAC | core |
| A6 | [security-fundamentals.md](security-fundamentals.md) | authN vs authZ, sessions/JWT/OAuth2, password hashing, TLS, XSS/CSRF/SQLi/SSRF, rate limiting | core |
| A7 | [oop-and-language-concepts.md](oop-and-language-concepts.md) | 4 OOP pillars, SOLID, composition vs inheritance, interface vs abstract, immutability, generics | core |
| A8 | [memory-and-runtime.md](memory-and-runtime.md) | stack vs heap, garbage collection, memory leaks, reference counting, Python GIL/generators/decorators | advanced |
| A9 | [latency-numbers-and-estimation.md](latency-numbers-and-estimation.md) | numbers every engineer should know, back-of-envelope drills, QPS/storage/bandwidth math | core |
| A10 | Distributed systems → [SystemDesign/DistributedSystemsConcepts.md](../SystemDesign/DistributedSystemsConcepts.md) | CAP/PACELC, replication, consensus, sagas | advanced |
| A11 | [bloom-filters-and-probabilistic.md](bloom-filters-and-probabilistic.md) | bloom/counting bloom, count-min sketch, HyperLogLog — approximate answers, tiny memory | advanced |
| A12 | [serialization-and-schemas.md](serialization-and-schemas.md) | JSON vs Protobuf vs Avro, schema evolution/compat, schema registry | core |
| A13 | [idempotency-and-delivery-semantics.md](idempotency-and-delivery-semantics.md) | idempotency keys, at-least/at-most/exactly-once, dedup, retries | core |
| A14 | [time-and-ordering.md](time-and-ordering.md) | wall-clock skew/NTP, happens-before, Lamport clocks, vector clocks | advanced |

## Concept → Q&A map

The [Q&A Bank](../QA-Bank/README.md) holds short, defensible interview answers. Each concept note
maps to a Q&A file for drilling:

| Concept | Q&A file |
|---------|----------|
| Operating systems | [qa-operating-systems.md](../QA-Bank/qa-operating-systems.md) |
| Concurrency & parallelism | [qa-concurrency.md](../QA-Bank/qa-concurrency.md) |
| Networking | [qa-networking.md](../QA-Bank/qa-networking.md) |
| Databases | [qa-databases.md](../QA-Bank/qa-databases.md) |
| Hashing | [qa-hashing.md](../QA-Bank/qa-hashing.md) |
| Caching | [qa-caching.md](../QA-Bank/qa-caching.md) |
| Security | [qa-security.md](../QA-Bank/qa-security.md) |
| OOP & design | [qa-oop-design.md](../QA-Bank/qa-oop-design.md) |
| System design concepts | [qa-system-design-concepts.md](../QA-Bank/qa-system-design-concepts.md) |
| Python language | [qa-language-python.md](../QA-Bank/qa-language-python.md) |

## Related material (canonical homes — don't duplicate, link)

- **Caching** strategies & eviction → [SystemDesign/components/caching.md](../SystemDesign/components/caching.md)
- **Sharding / partitioning** → [SystemDesign/components/database-sharding.md](../SystemDesign/components/database-sharding.md)
- **CAP / replication / consensus** → [SystemDesign/DistributedSystemsConcepts.md](../SystemDesign/DistributedSystemsConcepts.md)
- **SOLID / GoF patterns** → [SystemDesign/LowLevelDesign.md](../SystemDesign/LowLevelDesign.md)
- **Latency / estimation numbers** → [SystemDesign/SystemDesignGuide.md](../SystemDesign/SystemDesignGuide.md)
- **Hash-table / heap / trie code** → [DSA/data-structures/](../DSA/data-structures/)
