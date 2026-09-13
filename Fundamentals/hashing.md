# 🔑 Hashing

> **Explain in 2 min:** A hash function maps arbitrary input to a fixed-size value. We use it for
> two very different jobs. (1) **Hash tables** — turn a key into an array index for average O(1)
> lookup; the main problem is *collisions*, handled by chaining or open addressing, and we resize
> when the table gets too full. (2) **Distribution / integrity** — consistent hashing spreads keys
> across servers with minimal reshuffling when nodes change; cryptographic hashes (SHA-256) give
> tamper-evidence and are one-way. The interview trap is conflating the two: a fast non-crypto hash
> (like the one behind a `dict`) is *wrong* for passwords, and a slow crypto hash is *wrong* for a
> hot inner-loop hash table.

---

## 🎯 What a hash function is `[core]`

A function `h(key) → integer` that is:
- **Deterministic** — same input always gives the same output.
- **Uniform** — spreads inputs evenly across the output range (few clusters).
- **Fast** — for hash-table use, cheap to compute.

Different goals demand different properties, summarized here:

| Use case | Wants | Does *not* need | Example |
|----------|-------|-----------------|---------|
| Hash table | speed, uniformity | security | Python `hash()`, FNV, MurmurHash |
| Sharding / load balancing | uniformity, stability under resize | security | consistent hashing over MD5/xxHash |
| Integrity / dedup | collision resistance | speed | SHA-256, CRC (weak, non-crypto) |
| Passwords | *slowness*, salt | speed | bcrypt, scrypt, Argon2 |

---

## 🧺 Hash tables & collision handling `[core]`

A collision is two keys hashing to the same bucket. It's unavoidable (pigeonhole principle), so the
design question is *how you resolve it*.

### Separate chaining
Each bucket holds a list (or tree) of entries. On collision, append to the bucket's list.
- Simple; degrades gracefully; load factor can exceed 1.
- Extra memory for pointers; cache-unfriendly (list nodes scattered).
- Java's `HashMap` chains, and converts a bucket to a balanced tree once it exceeds ~8 entries to
  bound worst-case lookup at O(log n) instead of O(n).

### Open addressing
All entries live in the array itself; on collision, *probe* for the next free slot.
- **Linear probing** (`i+1, i+2, …`): cache-friendly but suffers *primary clustering*.
- **Quadratic probing** (`i+1², i+2², …`): reduces clustering.
- **Double hashing** (`i + k·h2(key)`): best distribution, more compute.
- Cache-friendly and no pointer overhead, but performance collapses as load factor approaches 1,
  and deletion needs tombstones.

```text
# Open addressing with linear probing (insert)
FUNCTION insert(table, key, value)
    idx = hash(key) MOD table.size
    WHILE table[idx] is occupied AND table[idx].key != key
        idx = (idx + 1) MOD table.size   # probe next slot
    table[idx] = (key, value)
```

**When to use which:** chaining when load factor is unpredictable or entries are large; open
addressing when memory locality matters and you can keep the table under ~70% full.

> Working hash-table-backed code (LRU cache): [DSA/data-structures/design/lru_cache.py](../DSA/data-structures/design/lru_cache.py).
> Trie and BST for key structures where hashing doesn't apply: [DSA/data-structures/tree/](../DSA/data-structures/tree/).

---

## 📏 Load factor & resizing `[core]`

**Load factor α = entries / buckets.** It's the dial that trades memory for speed.
- Low α → wasted space but few collisions.
- High α → dense, more collisions, slower.
- Typical threshold: resize when α > 0.75 (chaining) or ~0.5–0.7 (open addressing).

**Resizing** allocates a bigger table (usually 2×) and **rehashes every entry**, because the bucket
index depends on table size. That single resize is O(n), but amortized over many inserts it's O(1)
per insert — the same amortization argument as a dynamic array doubling.

> This "O(1) amortized but O(n) worst-case single op" point is a common interview follow-up. The
> fix for latency-sensitive systems is *incremental resizing* (Redis rehashes gradually across
> operations rather than in one stop-the-world pass).

---

## 🌐 Consistent hashing `[advanced]`

Naive sharding does `server = hash(key) MOD N`. Add or remove one server and **almost every key
remaps** — catastrophic for a cache (mass misses) or a stateful store (mass data movement).

Consistent hashing places servers *and* keys on a hash ring; a key belongs to the next server
clockwise. Adding/removing a node only remaps the keys in that node's arc — on average **K/N keys**
move instead of nearly all of them. **Virtual nodes** (many ring positions per physical server)
smooth out uneven distribution and let you weight bigger servers.

This is the canonical technique behind DynamoDB, Cassandra, and distributed caches. Full treatment
with diagrams lives in the sharding deep-dive:
👉 [SystemDesign/components/database-sharding.md](../SystemDesign/components/database-sharding.md).

---

## 🌸 Bloom filters `[advanced]`

A probabilistic set: "**definitely not present**" or "**possibly present**" — never a false
negative, but tunable false positives. Uses *k* hash functions setting bits in a bit array; you
can't delete (a counting Bloom filter can). Tiny memory footprint.

**When to use:** a cheap pre-check before an expensive lookup. Examples: does this key exist before
hitting disk/DB (Cassandra, HBase use them on SSTables), has this URL been seen, is this username
taken. A negative answer skips the expensive path entirely.

---

## 🔐 Cryptographic vs hash-table hashing `[core]`

| | Hash-table hash | Cryptographic hash |
|--|-----------------|---------------------|
| Goal | speed + uniform buckets | collision/preimage resistance |
| Speed | as fast as possible | deliberately non-trivial |
| Reversibility concern | none | must be one-way |
| Examples | MurmurHash, FNV, `dict` | SHA-256, SHA-3, BLAKE3 |
| Misuse | using SHA-256 in a hot map (slow) | using a table hash for passwords/integrity (insecure) |

**Password hashing is a third category.** You want it *slow* and *salted* to resist brute force:
use **bcrypt / scrypt / Argon2**, never a plain SHA. A per-user **salt** stops rainbow-table
attacks; a **pepper** (secret added server-side) adds another layer. (More in
security-fundamentals.md *(planned)*.)

**HMAC** = hash-based Message Authentication Code. It combines a message with a secret key
(`HMAC(key, msg)`) to prove both **integrity** and **authenticity** — the receiver, knowing the
key, can verify the sender computed it. Used for signing API requests, webhooks, and JWTs (HS256).

---

## 🧩 Where hashing shows up

- **Sharding / partitioning** — route key → node (consistent hashing). → [sharding doc](../SystemDesign/components/database-sharding.md)
- **Caching** — cache keys, cache-key hashing. → [caching doc](../SystemDesign/components/caching.md)
- **Deduplication** — content hash as identity (git commits, S3 ETags, dedup storage).
- **Checksums / integrity** — detect corruption in transit or at rest (CRC, SHA).
- **Data structures** — hash sets/maps, `k`-sum lookups, string search (Rabin-Karp rolling hash →
  [DSA/algorithms/string/rabin_karp.py](../DSA/algorithms/string/rabin_karp.py)).

---

## ⚠️ Common interview traps

- Claiming hash tables are "O(1)" without the *average-case, assuming good hash + bounded load
  factor* caveat. Worst case is O(n) (all keys collide).
- Using `MOD N` sharding then being surprised by mass cache misses on scale-out — reach for
  consistent hashing.
- Hashing passwords with SHA-256 (fast = brute-forceable). Use bcrypt/Argon2 + salt.
- Forgetting that resizing rehashes everything, so a single insert can spike to O(n).
- Thinking a Bloom filter can give false negatives — it can't; only false positives.

## 🔗 Related

- Q&A drills: [qa-hashing.md](../QA-Bank/qa-hashing.md) · [qa-caching.md](../QA-Bank/qa-caching.md)
- [Consistent hashing / sharding](../SystemDesign/components/database-sharding.md)
- [Caching component](../SystemDesign/components/caching.md)
- [Rabin-Karp rolling hash](../DSA/algorithms/string/rabin_karp.py) · [LRU cache](../DSA/data-structures/design/lru_cache.py)
