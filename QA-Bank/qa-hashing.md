# ❓ Hashing - Q&A

> Pairs with [Hashing](../Fundamentals/hashing.md). Format and tag legend:
> [Overview](README.md).

---

> **Q1. Why is hash-table lookup O(1) average but O(n) worst case?**
> With a good hash and bounded load factor, keys spread evenly so lookups hit short buckets - O(1)
> average. Worst case, all keys collide into one bucket and you scan them linearly - O(n). Java's
> HashMap tree-ifies large buckets to bound this at O(log n).
> *Follow-ups:* What breaks the O(1) assumption? (bad hash, adversarial keys, high load factor.)
> `Med` · `MAANG`

> **Q2. Chaining vs open addressing for collisions?**
> Chaining stores a list per bucket (simple, load factor can exceed 1, but pointer overhead and poor
> cache locality). Open addressing probes for the next free slot (cache-friendly, no pointers, but
> degrades near full and needs tombstones for deletion).
> *Follow-ups:* When would you pick open addressing? (memory locality matters, table kept <70% full.)
> `Med` · `Google`

> **Q3. What is load factor and why resize?**
> Load factor = entries / buckets. High load factor means more collisions and slower ops. When it
> crosses a threshold (~0.75), the table resizes (usually doubles) and rehashes every entry -
> O(n) once, but O(1) amortized per insert.
> *Follow-ups:* Why does a single insert sometimes spike to O(n)? (triggers a resize/rehash.)
> `Med` · `MAANG`

> **Q4. Why does resizing require rehashing everything?**
> The bucket index is `hash(key) mod tableSize`, so changing the table size changes where each key
> belongs. Every entry must be recomputed and moved. Latency-sensitive systems (Redis) do this
> incrementally instead of all at once.
> *Follow-ups:* How does incremental rehashing avoid a stall?
> `Hard` · `Google`

> **Q5. What problem does consistent hashing solve?**
> Naive `hash(key) mod N` remaps almost every key when N changes - catastrophic for caches/sharding.
> Consistent hashing puts nodes and keys on a ring so adding/removing a node only remaps ~K/N keys.
> See [Database Sharding](../SystemDesign/components/database-sharding.md).
> *Follow-ups:* What do virtual nodes fix? (uneven distribution + weighting.)
> `Hard` · `Amazon`

> **Q6. What is a bloom filter and when would you use one?**
> A probabilistic set answering "definitely not present" or "possibly present" - no false negatives,
> tunable false positives, tiny memory. Use it as a cheap pre-check before an expensive lookup (DB,
> disk), e.g. LSM-tree SSTables, "have I seen this URL."
> *Follow-ups:* Can you delete from a bloom filter? (not a standard one - use a counting bloom.)
> `Hard` · `Google`

> **Q7. Cryptographic hash vs hash-table hash?**
> A hash-table hash optimizes for speed and uniform buckets (MurmurHash, the one behind a dict). A
> cryptographic hash (SHA-256) optimizes for collision/preimage resistance and is deliberately not
> reversible - using it in a hot map is slow, and using a table hash for integrity is insecure.
> *Follow-ups:* Which category is a password hash? (a third one - deliberately slow.)
> `Med` · `MAANG`

> **Q8. How should passwords be hashed?**
> With a slow, salted algorithm - bcrypt, scrypt, or Argon2 - never a fast hash like SHA-256. A
> per-user salt defeats rainbow tables; a work factor keeps it expensive as hardware improves.
> *Follow-ups:* Why is a fast hash bad for passwords? (brute-forceable at scale.)
> `Med` · `MAANG`

> **Q9. What is HMAC?**
> A hash-based message authentication code: `HMAC(secret_key, message)` proves both integrity and
> authenticity - a receiver who knows the key can verify the sender computed it. Used to sign API
> requests, webhooks, and JWTs (HS256).
> *Follow-ups:* How is HMAC different from just hashing the message? (the secret key authenticates.)
> `Hard` · `Amazon`

> **Q10. Why can't you rely on `hash(key) mod N` for sharding across a changing cluster?**
> Because changing N re-maps nearly all keys, causing mass cache misses or huge data movement. It's
> fine only for a fixed number of buckets. For dynamic clusters use consistent hashing.
> *Follow-ups:* What real systems use consistent hashing? (DynamoDB, Cassandra, Redis Cluster.)
> `Med` · `Amazon`

> **Q11. What properties make a good hash function for a hash table?**
> Deterministic, fast, and uniform (spreads inputs evenly to minimize collisions). It does not need
> to be cryptographically secure. A poor distribution clusters keys and degrades lookups toward
> O(n).
> *Follow-ups:* What's an adversarial input attack on hashing? (crafted keys that all collide → DoS.)
> `Med` · `Google`

> **Q12. Where does hashing show up beyond hash tables?**
> Sharding/partitioning (route key → node), deduplication (content hash as identity - git, S3
> ETags), integrity/checksums (detect corruption), and string search (Rabin-Karp rolling hash). Same
> primitive, different goals.
> *Follow-ups:* Why is a content hash a good dedup key? (identical content → identical hash.)
> `Med` · `MAANG`

---

**Related:** [Hashing](../Fundamentals/hashing.md) ·
[Databases Q&A](qa-databases.md) · [Caching Q&A](qa-caching.md) · [Security Q&A](qa-security.md)
