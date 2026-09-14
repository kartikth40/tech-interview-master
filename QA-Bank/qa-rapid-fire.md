# ❓ Rapid Fire - 1-Line Drills

> One-line definitions for warm-up or last-minute review. Cover the term, then check. For depth,
> jump to the matching [Fundamentals](../Fundamentals/) note or the topic Q&A file. Format legend:
> [Overview](README.md).

Each entry: **term** - a one-sentence answer you could say in an interview.

---

## Systems & OS

1. **Process vs thread** - process = isolated memory; thread = shares its process's memory, cheaper to switch.
2. **Context switch** - save one thread's CPU state, load another's; pure overhead that also thrashes caches.
3. **Deadlock** - threads wait on each other forever; needs all four Coffman conditions.
4. **Race condition** - result depends on interleaving of operations on shared state.
5. **Mutex vs semaphore** - mutex allows one holder; semaphore allows up to N.
6. **Virtual memory** - per-process address space mapped to RAM in pages; gives isolation + overcommit.

## Concurrency

7. **Concurrency vs parallelism** - structuring overlapping tasks vs actually running them at once.
8. **Idempotent** - doing it twice has the same effect as doing it once.
9. **Amdahl's law** - speedup is capped at 1/(serial fraction).
10. **GIL** - Python's lock allowing one thread of bytecode at a time (kills CPU-bound threading).

## Networking

11. **TCP vs UDP** - reliable ordered stream vs fast best-effort datagrams.
12. **3-way handshake** - SYN, SYN-ACK, ACK to open a TCP connection.
13. **TLS handshake** - asymmetric crypto to authenticate + exchange a key, then symmetric for data.
14. **DNS** - resolves a hostname to an IP by walking root → TLD → authoritative, cached by TTL.
15. **Head-of-line blocking** - one stalled item blocks everything queued behind it.

## Databases

16. **ACID** - Atomicity, Consistency, Isolation, Durability.
17. **CAP** - under a partition, choose Consistency or Availability, not both.
18. **Index** - secondary sorted structure (usually B-tree) that avoids full scans; slows writes.
19. **Sharding vs replication** - split different data across nodes vs copy the same data to many.
20. **MVCC** - versioned rows so readers and writers don't block each other.

## Hashing, caching, security

21. **Consistent hashing** - ring placement so a node change remaps only ~K/N keys.
22. **Bloom filter** - probabilistic set: "definitely not" or "maybe"; no false negatives.
23. **Cache-aside** - check cache, on miss read DB and populate it.
24. **AuthN vs authZ** - who you are vs what you're allowed to do.
25. **Idempotency key** - client-supplied token letting the server dedup retried requests.

---

**Related:** [QA-Bank index](README.md) · [Fundamentals](../Fundamentals/) ·
[System Design Guide](../SystemDesign/SystemDesignGuide.md)
