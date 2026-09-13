# 🌸 Bloom Filters & Probabilistic Structures

!!! tip "Explain in 2 min"
    Probabilistic data structures trade a little accuracy for a huge memory win.
    A **bloom filter** answers set membership as "definitely not present" or "possibly present" — never
    a false negative — in a tiny bit array, so you use it as a cheap pre-check before an expensive
    lookup (disk, DB). A **count-min sketch** estimates *how many times* it's seen an item (frequency)
    in fixed memory, overcounting a little. **HyperLogLog** estimates *how many distinct* items there
    are (cardinality) in kilobytes even for billions of items. The theme: when exact answers cost too
    much memory, an approximate answer with a known error bound is often good enough.

---

## 🌸 Bloom filter `[advanced]`

A bit array + *k* hash functions. To **add** an item, hash it *k* ways and set those *k* bits. To
**check**, hash it *k* ways and see if all *k* bits are set:
- All set → **possibly present** (could be a false positive — other items set those bits).
- Any unset → **definitely not present** (no false negatives).

```text
add(x):    FOR i in 1..k: bits[h_i(x) % m] = 1
contains(x): FOR i in 1..k: IF bits[h_i(x) % m] == 0: RETURN "no"
             RETURN "maybe"
```

- **No false negatives**, tunable false-positive rate (more bits + optimal *k* → fewer).
- **Can't delete** from a standard bloom filter (clearing a bit could break other items) — a
  **counting bloom filter** uses small counters instead of bits to allow deletion.

**When to use:** a cheap gate before an expensive operation. Examples: LSM-tree/SSTable "does this
key exist here?" (skip the disk read if not) — see [databases-internals.md](databases-internals.md);
"have I seen this URL?" in a [web crawler](../SystemDesign/designs/web-crawler.md); "is this username
taken?" pre-check. Built on hash functions — see [hashing.md](hashing.md).

---

## 📊 Count-min sketch `[advanced]`

Estimates **frequency** of items in a stream using a small 2-D array of counters and *k* hash
functions. To add, increment one counter per row; to query, take the **minimum** across the rows
(minimizing the effect of collisions). It **overcounts** (never undercounts), with a bounded error.

**When to use:** "top-k / heavy hitters" and approximate counts at stream scale where an exact
per-item counter map won't fit — trending terms, per-key traffic, rate stats.

---

## 🔢 HyperLogLog `[advanced]`

Estimates **cardinality** (number of *distinct* items) using a few KB regardless of set size, by
observing the maximum run of leading zeros in item hashes (rare long runs imply many distinct items).
Typical error ~1-2%.

**When to use:** "how many unique visitors / unique search terms / distinct IPs" over billions of
events, where storing every distinct item is infeasible. Redis `PFADD`/`PFCOUNT` is HyperLogLog.

---

## ⚖️ Choosing a structure

| Question | Structure | Error mode |
|----------|-----------|-----------|
| Is x in the set? | Bloom filter | false positives only |
| How many times has x appeared? | Count-min sketch | overcounts |
| How many *distinct* items? | HyperLogLog | ~1-2% off |
| Exact, small set | plain hash set/map | none (but O(n) memory) |

Reach for these only when the exact structure won't fit in memory — an approximate answer with a
known error bound beats an out-of-memory failure.

---

## ⚠️ Common interview traps

- Claiming a bloom filter can give false negatives — it cannot; only false positives.
- Trying to delete from a standard bloom filter (use a counting bloom filter).
- Confusing frequency (count-min) with cardinality (HyperLogLog) — different questions.
- Using them when an exact set fits fine — added complexity for no benefit.

## 🔗 Related

- Q&A drills: [qa-hashing.md](../QA-Bank/qa-hashing.md)
- Hash functions (the building block) → [hashing.md](hashing.md)
- SSTable/LSM use of bloom filters → [databases-internals.md](databases-internals.md)
- Web crawler "seen URL" filter → [SystemDesign/designs/web-crawler.md](../SystemDesign/designs/web-crawler.md)
