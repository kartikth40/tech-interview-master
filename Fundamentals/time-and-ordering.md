# ⏱️ Time & Ordering

!!! tip "Explain in 2 min"
    In a distributed system you can't trust wall clocks to order events — each
    machine's clock drifts, and even with NTP they're only loosely synchronized, so "later timestamp =
    happened later" is wrong. Instead we reason about **causality**: which events *could have*
    influenced which. **Lamport clocks** (a single counter bumped on every event and message) give a
    total order consistent with causality but can't tell whether two events are truly concurrent.
    **Vector clocks** (a counter per node) can — they detect whether one event happened-before another
    or they're concurrent (a conflict). This is why systems use vector clocks for conflict detection
    and logical ordering rather than timestamps.

---

## 🕰️ Why wall clocks fail `[advanced]`

Each machine has its own clock, and they **drift** apart. **NTP** synchronizes them but only to
within milliseconds-to-tens-of-ms, and it can jump the clock forward or **backward**. Consequences:
- Ordering events by timestamp across machines is unreliable — a "later" timestamp may be an earlier
  event on a faster-drifting clock.
- Last-write-wins by timestamp can **silently lose data** when clocks disagree.
- IDs/tokens that assume a monotonic clock can break when the clock goes backward (see the Snowflake
  clock-skew issue in [unique-id-generator.md](../SystemDesign/designs/unique-id-generator.md)).

So for correctness we track **causality**, not physical time.

---

## ➡️ Happens-before `[advanced]`

Event A **happens-before** B (A → B) if:
1. They're on the same node and A comes first, or
2. A is a message send and B is its receive, or
3. Transitively (A → C and C → B).

If neither A → B nor B → A, the events are **concurrent** — no causal relationship. This partial
order is what we actually care about; wall-clock time is just an unreliable proxy for it.

---

## 🔢 Lamport clocks `[advanced]`

A single integer counter per node:
- Increment on every local event.
- On send, attach the counter; on receive, set `counter = max(local, received) + 1`.

This gives timestamps where **A → B implies L(A) < L(B)** (a total order consistent with causality).
But the converse fails: `L(A) < L(B)` does **not** mean A → B — they might be concurrent. So Lamport
clocks order events but **can't detect concurrency/conflicts**.

---

## 🧮 Vector clocks `[advanced]`

A vector of counters, one entry per node (`[A:2, B:1, C:0]`):
- Increment your own entry on an event.
- On receive, take the element-wise **max** with the incoming vector, then bump your own entry.

Compare two vectors:
- All entries ≤ (and at least one <) → one **happened-before** the other.
- Neither dominates → **concurrent** (a genuine conflict).

This is why Dynamo-style stores use vector clocks to tell "this write supersedes that one" from "two
writes conflict, ask the app to merge" — see [key-value-store.md](../SystemDesign/designs/key-value-store.md).
Cost: the vector grows with the number of nodes (truncate stale entries).

---

## ⚖️ Which to use `[advanced]`

| Need | Use |
|------|-----|
| Roughly-synced human-facing timestamps | NTP wall clock (accept skew) |
| A total order consistent with causality | Lamport clock |
| Detect concurrent writes / conflicts | Vector clock |
| Strong global ordering across nodes | consensus (Raft/Paxos) — see below |

For a strict, agreed-upon order (a replicated log, leader election), you need **consensus**
(Raft/Paxos), covered in [DistributedSystemsConcepts.md](../SystemDesign/DistributedSystemsConcepts.md).
Some systems (Google Spanner) use tightly-bounded physical clocks (TrueTime) to order globally — the
exception that proves how hard clock-based ordering is.

---

## ⚠️ Common interview traps

- Ordering distributed events by wall-clock timestamp (clocks drift; NTP isn't exact).
- Using last-write-wins by timestamp and not realizing it can lose concurrent updates.
- Saying Lamport clocks detect conflicts — they give a total order but can't identify concurrency;
  vector clocks can.
- Forgetting vector clocks grow with node count (need truncation/pruning).

## 🔗 Related

- Q&A drills: [qa-databases.md](../QA-Bank/qa-databases.md) · [qa-system-design-concepts.md](../QA-Bank/qa-system-design-concepts.md)
- Consensus, replication, CAP → [DistributedSystemsConcepts.md](../SystemDesign/DistributedSystemsConcepts.md)
- Vector clocks in a KV store → [key-value-store.md](../SystemDesign/designs/key-value-store.md)
- Snowflake clock skew → [unique-id-generator.md](../SystemDesign/designs/unique-id-generator.md)
