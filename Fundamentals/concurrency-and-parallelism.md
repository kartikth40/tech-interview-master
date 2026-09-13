# 🧵 Concurrency & Parallelism

> **Explain in 2 min:** **Concurrency** is *dealing with* many things at once — structuring a
> program so tasks make progress independently (interleaved on one core is fine). **Parallelism**
> is *doing* many things at once — literally running on multiple cores. Concurrency is about
> structure; parallelism is about execution. A single-core machine can be concurrent (an event loop
> juggling I/O) but not parallel. The hard part isn't starting tasks — it's **shared mutable
> state**: two tasks touching the same data race, so we coordinate with locks, or avoid sharing
> altogether (message passing, immutability). In Python specifically, the **GIL** means threads
> don't run Python bytecode in parallel, so you use threads/async for I/O-bound work and processes
> for CPU-bound work.

---

## 🎯 Concurrency vs parallelism `[core]`

| | Concurrency | Parallelism |
|--|-------------|-------------|
| Question | *"how do I structure tasks that overlap in time?"* | *"how do I run tasks at the same instant?"* |
| Needs multiple cores | no | yes |
| Classic example | one chef switching between dishes | many chefs, one dish each |
| Goal | responsiveness, throughput on I/O | raw compute speedup |

They compose: a web server is *concurrent* (thousands of in-flight requests) and *parallel* (worker
processes across cores).

---

## 🧠 Threads vs async / event loop `[core]`

Two ways to be concurrent:

- **Threads (preemptive):** OS schedules threads and can switch at any instruction. Shared memory
  by default → you must synchronize. Cheap-ish but each thread has a stack, and context switches
  cost.
- **Async / event loop (cooperative):** one thread runs an event loop; tasks *yield* at `await`
  points (usually I/O). No preemption → far fewer race conditions, but a CPU-bound task or a
  blocking call *stalls the whole loop*.

**Rule of thumb:** async shines for **I/O-bound** work with many idle waits (network, disk);
threads/processes for **CPU-bound** work. Mixing a blocking call into an event loop is the most
common async bug.

---

## 🔒 Synchronization primitives `[core]`

| Primitive | What it does | Use when |
|-----------|--------------|----------|
| **Mutex / lock** | one holder at a time (mutual exclusion) | protect a critical section |
| **Semaphore** | allows up to *N* holders | limit concurrency (e.g. ≤10 DB connections) |
| **Read-write lock** | many readers *or* one writer | read-heavy shared data |
| **Condition variable** | wait until a predicate is signalled | producer-consumer handoff |
| **Atomic operation** | indivisible read-modify-write | counters, flags without a full lock |

A **critical section** is code that must not be entered by more than one thread at a time. Keep it
as small as possible — holding a lock longer than needed kills throughput.

---

## 💥 Race conditions & atomicity `[core]`

A **race condition**: the result depends on the *timing* of interleaved operations. The canonical
example is `count += 1`, which is really *read → add → write* — three steps that another thread can
interleave, losing an update.

```text
# Two threads run count += 1 on count = 0; expected 2, can get 1
Thread A: read count (0)
Thread B: read count (0)
Thread A: write 1
Thread B: write 1        # A's increment is lost
```

**Atomicity** means an operation is all-or-nothing and indivisible — no other thread can observe a
partial state. Fix the race with a lock, an atomic increment, or by not sharing the counter.

---

## ⚰️ Deadlock, livelock, starvation `[core]`

- **Deadlock** — threads wait on each other forever. Needs all four **Coffman conditions**: mutual
  exclusion, hold-and-wait, no preemption, circular wait. Break *any one* to prevent it — most
  practically, impose a **global lock ordering** so cycles can't form.
- **Livelock** — threads keep changing state in response to each other but make no progress (two
  people stepping side-to-side in a hallway).
- **Starvation** — a thread never gets the resource because others keep winning (e.g. writers
  starved by a stream of readers). Fixed with fairness / aging.

```text
# Deadlock via inconsistent lock order
Thread A: lock(X); ... lock(Y)
Thread B: lock(Y); ... lock(X)   # A holds X waits Y, B holds Y waits X → stuck
# Fix: everyone locks X before Y
```

---

## 🏭 Producer-consumer & thread pools `[core]`

- **Producer-consumer** — producers push work onto a bounded queue, consumers pull. The queue
  decouples rates and provides backpressure (producers block when it's full). A condition variable
  or blocking queue coordinates the handoff.
- **Thread pool** — a fixed set of reusable worker threads pulling from a task queue. Avoids the
  cost of spawning a thread per task and bounds concurrency (which protects downstream resources).
  This is the model behind most web servers and executors.

---

## 📉 Amdahl's law `[advanced]`

Speedup from parallelism is capped by the **serial fraction**. If fraction *s* of the work is
inherently sequential, max speedup with infinite cores is **1/s**. So if 10% is serial, you can
never go faster than 10×, no matter how many cores. The lesson: parallelize the *big* parallel
portion, and don't expect linear scaling — coordination and the serial tail dominate at scale.

---

## 🐍 Python: the GIL `[core]`

The **Global Interpreter Lock** lets only one thread execute Python bytecode at a time. Consequences:
- **CPU-bound + threads → no speedup** (threads fight over the GIL). Use `multiprocessing` or native
  extensions that release the GIL (NumPy) instead.
- **I/O-bound + threads → fine**, because the GIL is released during blocking I/O.
- **`asyncio`** gives single-threaded concurrency for I/O without threads at all.

Quick decision guide:

| Workload | Best tool in Python |
|----------|---------------------|
| Many network/disk waits | `asyncio` or threads |
| Heavy computation | `multiprocessing` / native libs |
| Mix | processes for compute + async for I/O |

> Note: recent CPython has an experimental *free-threaded* (no-GIL) build. Mention it as "coming"
> but the GIL model is still what interviews expect.

---

## 🔐 Optimistic vs pessimistic locking `[advanced]`

- **Pessimistic** — lock first, assume conflict is likely. Blocks others (row locks, `SELECT … FOR
  UPDATE`). Safe but reduces concurrency; risks deadlock.
- **Optimistic** — don't lock; proceed, then at commit check nothing changed (a **version number**
  or timestamp). If it did, retry. Great when conflicts are rare; wasteful when they're frequent.

This maps directly to database concurrency control (MVCC is optimistic-flavored) →
[databases-internals.md](databases-internals.md).

---

## ⚠️ Common interview traps

- Saying "concurrency = parallelism." Structure vs execution — keep them distinct.
- Claiming Python threads speed up CPU-bound code (the GIL prevents it).
- Forgetting `count += 1` is not atomic.
- Proposing "add more locks" — over-locking causes deadlock and kills throughput; prefer smaller
  critical sections, lock ordering, or no sharing.
- Ignoring that an event loop is stalled by one blocking/CPU-heavy call.

## 🔗 Related

- Q&A drills: [qa-concurrency.md](../QA-Bank/qa-concurrency.md)
- Optimistic locking / MVCC → [databases-internals.md](databases-internals.md)
- OS scheduling & context switches → [operating-systems.md](operating-systems.md)
- Distributed coordination (consensus, sagas) → [SystemDesign/DistributedSystemsConcepts.md](../SystemDesign/DistributedSystemsConcepts.md)
