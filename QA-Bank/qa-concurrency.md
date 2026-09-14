# ❓ Concurrency & Parallelism - Q&A

> Pairs with [Concurrency & Parallelism](../Fundamentals/concurrency-and-parallelism.md).
> Format and tag legend: [Overview](README.md).

---

> **Q1. Concurrency vs parallelism?**
> Concurrency is *structuring* a program so tasks make progress independently (can be interleaved on
> one core); parallelism is *executing* tasks at the same instant on multiple cores. Concurrency is
> about structure, parallelism about execution - you can have one without the other.
> *Follow-ups:* Give an example of concurrent-but-not-parallel. (async event loop on one core.)
> `Easy` · `MAANG`

> **Q2. When would you use threads vs async?**
> Async (an event loop) shines for I/O-bound work with many idle waits - thousands of connections,
> minimal per-task memory. Threads suit shared-state concurrency and can use preemption; processes
> suit CPU-bound work. The classic bug is a blocking/CPU-heavy call stalling an event loop.
> *Follow-ups:* Why does one blocking call hurt an event loop? (cooperative - no preemption.)
> `Med` · `MAANG`

> **Q3. What's a race condition?**
> When the result depends on the timing of interleaved operations on shared state. The canonical
> example is `count += 1`, which is read-modify-write; two threads can both read the old value and
> lose an update.
> *Follow-ups:* How do you fix it? (lock, atomic op, or don't share.)
> `Easy` · `MAANG`

> **Q4. Why isn't `count += 1` atomic?**
> It compiles to three steps - read, add, write. Another thread can interleave between them, so both
> read the same old value and one increment is lost. Atomicity means the whole operation is
> indivisible; you get it with a lock or a hardware atomic instruction.
> *Follow-ups:* What's a compare-and-swap (CAS)?
> `Med` · `MAANG`

> **Q5. Mutex vs semaphore?**
> A mutex allows exactly one holder and has ownership (only the locker unlocks). A semaphore is a
> counter permitting up to N concurrent holders - useful to cap access to a pool (e.g. ≤10 DB
> connections). A binary semaphore looks like a mutex but lacks ownership.
> *Follow-ups:* When would a semaphore be the right tool? (connection/resource pools.)
> `Med` · `MAANG`

> **Q6. What is a deadlock and how do you avoid it in application code?**
> Threads wait on locks each other holds, forever. It needs all four Coffman conditions; the
> practical fix is a consistent global lock-acquisition order so a cycle can't form. Also: lock
> timeouts, or acquiring all locks at once.
> *Follow-ups:* Show a two-lock deadlock and its fix.
> `Med` · `Amazon`

> **Q7. Deadlock vs livelock vs starvation?**
> Deadlock: threads are stuck waiting forever (no progress, no CPU). Livelock: threads keep changing
> state reacting to each other but still make no progress. Starvation: a thread never gets a
> resource because others keep winning - fixed with fairness/aging.
> *Follow-ups:* Give a real livelock example. (two threads both backing off and retrying in sync.)
> `Hard` · `Google`

> **Q8. What is a critical section?**
> Code that must not be executed by more than one thread at once because it touches shared state.
> Keep it as small as possible - holding a lock longer than necessary serializes threads and kills
> throughput.
> *Follow-ups:* Why is a coarse lock bad for scalability?
> `Easy` · `MAANG`

> **Q9. Optimistic vs pessimistic locking?**
> Pessimistic locks first, assuming conflict is likely (safe, blocks others, risks deadlock).
> Optimistic proceeds without locking and checks at commit that nothing changed (via a version
> number); if it did, retry. Optimistic wins when conflicts are rare.
> *Follow-ups:* How does this map to databases? (MVCC / version columns.)
> `Med` · `Amazon`

> **Q10. What does the Python GIL mean for concurrency?**
> Only one thread executes Python bytecode at a time, so threads don't parallelize CPU-bound work.
> Use `multiprocessing` (or native libs that release the GIL) for CPU-bound tasks; threads or
> `asyncio` are fine for I/O-bound work since the GIL is released during blocking I/O.
> *Follow-ups:* Why do threads still help for I/O in Python?
> `Med` · `MAANG`

> **Q11. Explain Amdahl's law.**
> Speedup from parallelism is capped by the serial fraction: if fraction s must run sequentially,
> max speedup is 1/s regardless of core count. So 10% serial work caps you at 10×. Lesson:
> parallelize the dominant parallel part and don't expect linear scaling.
> *Follow-ups:* What's the practical implication for adding cores? (diminishing returns.)
> `Hard` · `Google`

> **Q12. What is a thread pool and why use one?**
> A fixed set of reusable worker threads pulling tasks from a queue. It avoids the cost of spawning a
> thread per task and bounds concurrency, which protects downstream resources (DB, CPU). Most web
> servers and executors use this model.
> *Follow-ups:* What happens if the pool is too small? Too large?
> `Med` · `MAANG`

> **Q13. Explain the producer-consumer pattern.**
> Producers push work onto a bounded queue; consumers pull and process it. The queue decouples their
> rates and provides backpressure - producers block when it's full, so a fast producer can't
> overwhelm slow consumers.
> *Follow-ups:* What coordinates the handoff? (condition variable / blocking queue.)
> `Med` · `Amazon`

> **Q14. What's the difference between a lock and an atomic operation?**
> A lock guards an arbitrary critical section but has acquire/release overhead and deadlock risk. An
> atomic operation is a single indivisible hardware instruction (increment, CAS) - faster and
> lock-free, but only for simple operations.
> *Follow-ups:* When would you prefer atomics? (counters, flags, lock-free structures.)
> `Hard` · `Google`

> **Q15. What is a read-write lock?**
> It allows many concurrent readers OR one exclusive writer. Good for read-heavy shared data where
> reads vastly outnumber writes. The risk is writer starvation if readers keep arriving - needs a
> fairness policy.
> *Follow-ups:* When is a plain mutex better? (write-heavy or very short critical sections.)
> `Med` · `MAANG`

> **Q16. What is thread safety?**
> Code is thread-safe if it behaves correctly when accessed by multiple threads concurrently,
> without external synchronization. Achieved via immutability, confinement (no sharing), or proper
> locking around shared mutable state.
> *Follow-ups:* Why are immutable objects inherently thread-safe? (no writes to race on.)
> `Med` · `MAANG`

> **Q17. What is a condition variable?**
> A synchronization primitive that lets a thread wait until some predicate becomes true, releasing
> the associated lock while waiting and reacquiring it on wakeup. Used for producer-consumer handoff
> ("wait until queue non-empty").
> *Follow-ups:* Why check the predicate in a loop? (spurious wakeups.)
> `Hard` · `Google`

> **Q18. What causes false sharing?**
> Two threads modify independent variables that happen to sit on the same cache line, so the cache
> coherence protocol keeps invalidating each other's cache - killing performance despite no logical
> contention. Fix with padding/alignment.
> *Follow-ups:* How would you diagnose it? (profiler showing cache-line contention.)
> `Hard` · `Google`

> **Q19. At-least-once vs at-most-once vs exactly-once delivery?**
> At-least-once may deliver duplicates (retry on uncertainty) - needs idempotent consumers.
> At-most-once may drop messages (no retry). Exactly-once is hard in distributed systems; usually
> approximated by at-least-once + idempotency/dedup.
> *Follow-ups:* How do you make a consumer idempotent? (dedup key, upsert.)
> `Hard` · `Amazon`

> **Q20. What is optimistic concurrency with a version number?**
> Read a record with its version; on write, update only if the version still matches, then bump it.
> If another writer got there first the version mismatches and you retry. Avoids locks when conflicts
> are rare.
> *Follow-ups:* What's the failure mode under high contention? (retry storms.)
> `Med` · `Startups`

> **Q21. How do you share state safely across processes?**
> Since processes don't share memory, use IPC: shared memory (fast, needs synchronization), message
> passing/queues (safer, copies), or an external store (Redis/DB). Message passing is usually the
> cleaner default.
> *Follow-ups:* Why is "share nothing" a popular concurrency model? (no locks, no races.)
> `Med` · `MAANG`

> **Q22. Why is "just add more locks" a bad instinct?**
> More locks increase deadlock risk, reduce concurrency (threads serialize), and add overhead.
> Prefer smaller critical sections, a consistent lock order, lock-free atomics, or eliminating
> sharing (immutability, confinement) over piling on locks.
> *Follow-ups:* What's lock contention and how do you measure it?
> `Med` · `MAANG`

---

**Related:** [Concurrency & Parallelism](../Fundamentals/concurrency-and-parallelism.md) ·
[Operating Systems Q&A](qa-operating-systems.md) · [Python Language Q&A](qa-language-python.md)
