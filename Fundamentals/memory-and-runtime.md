# 🧠 Memory & Runtime

!!! tip "Explain in 2 min"
    Programs use two main memory regions: the **stack** (fast, automatic, holds
    call frames and locals) and the **heap** (dynamic, manually or automatically managed, holds
    long-lived objects). How the heap gets cleaned up defines the runtime: manual (`free`), **reference
    counting** (free when the count hits zero), or a **tracing garbage collector** (periodically find
    and reclaim unreachable objects). A **memory leak** is memory you no longer need but the runtime
    still considers reachable. Language semantics matter too - whether arguments are copied or shared
    (pass-by-value vs reference) changes what a callee can affect. Python specifically uses reference
    counting + a cycle collector, and its **GIL** shapes how you do concurrency.

---

## Stack vs heap `[core]`

| | Stack | Heap |
|--|-------|------|
| Holds | call frames, locals, return addresses | dynamically allocated objects |
| Lifetime | auto-freed when the function returns | until freed / GC'd |
| Speed | very fast (just move a pointer) | slower (allocator bookkeeping) |
| Size | small, fixed limit | large |
| Failure | stack overflow (deep recursion) | out-of-memory, fragmentation, leaks |

Each thread has its own stack; the heap is shared across threads (hence the need for synchronization
- see [concurrency-and-parallelism.md](concurrency-and-parallelism.md)).

---

## Garbage collection `[core]`

Automatic reclamation of unreachable heap memory. Main approaches:

- **Reference counting** - each object tracks how many references point to it; freed at zero.
  Immediate reclamation, predictable, but **can't collect reference cycles** and has per-op overhead.
- **Mark-and-sweep (tracing)** - periodically start from roots, *mark* everything reachable, *sweep*
  the rest. Handles cycles; but causes pauses.
- **Generational GC** - exploits the "most objects die young" observation: collect the young
  generation often (cheap), older generations rarely. Used by the JVM and CPython's cycle collector.
- **Copying / compacting** - move live objects together to eliminate fragmentation.

**Trade-off:** GC trades a bit of throughput and occasional **pause times** for safety from
manual-memory bugs (use-after-free, double-free). Latency-sensitive systems tune the GC or minimize
allocations to avoid stop-the-world pauses.

---

## Memory leaks `[core]`

Memory that's no longer needed but still **reachable**, so the GC won't reclaim it. Even in
GC'd languages you can leak via:
- Objects lingering in a long-lived collection (a cache/map that's never pruned).
- Forgotten event listeners / callbacks holding references.
- Closures capturing large objects.
- Unclosed resources (files, sockets, connections).

The fix is usually to drop references you no longer need (evict from caches, unregister listeners)
and to close resources deterministically (context managers / try-with-resources).

---

## Pass-by-value vs pass-by-reference `[core]`

- **Pass-by-value** - the callee gets a *copy*; changes don't affect the caller's variable.
- **Pass-by-reference** - the callee gets an alias; changes are visible to the caller.

**Python is pass-by-object-reference** (a.k.a. "call by sharing"): the reference is passed by value.
Practically:
- Rebinding a parameter (`x = ...`) never affects the caller.
- *Mutating* a mutable argument (`lst.append(...)`) **does** affect the caller.
- Immutable arguments (int, str, tuple) appear value-like because you can't mutate them in place.

This is a top source of "why did my list change?" bugs - see value/reference semantics in
[oop-and-language-concepts.md](oop-and-language-concepts.md).

---

## Python runtime specifics `[advanced]`

Frequently probed for Python roles:

- **GIL** - one thread runs Python bytecode at a time, so threads don't parallelize CPU-bound work;
  use processes for CPU, threads/async for I/O. Full treatment in
  [concurrency-and-parallelism.md](concurrency-and-parallelism.md).
- **Memory model** - reference counting for immediate reclamation + a generational cycle collector
  for reference cycles.
- **Mutability** - `list`/`dict`/`set` mutable; `int`/`str`/`tuple`/`frozenset` immutable. Never use
  a mutable default argument (`def f(x=[])`) - it's shared across calls.
- **Generators** - produce values lazily with `yield`, so you can iterate huge/infinite sequences
  without building them in memory. The basis of memory-efficient pipelines.
- **Decorators** - wrap a function to add behavior (logging, caching, auth) without changing its
  body; `@lru_cache`, `@property` are stdlib examples.
- **Context managers** - `with` guarantees setup/teardown (closing files, releasing locks) even on
  exceptions - the Pythonic answer to deterministic resource cleanup and leak prevention.

---

## Common interview traps

- Saying "GC means no memory leaks" - you still leak via reachable-but-unused references.
- Claiming reference counting handles everything - it can't collect cycles (needs a tracing pass).
- Calling Python "pass by reference" or "pass by value" - it's pass-by-object-reference; mutability
  decides visibility.
- Using a mutable default argument and being surprised it persists across calls.
- Ignoring GC pause times when reasoning about tail latency.

## Related

- Q&A drills: [qa-language-python.md](../QA-Bank/qa-language-python.md)
- Stack/heap sharing across threads, GIL → [concurrency-and-parallelism.md](concurrency-and-parallelism.md)
- Value vs reference semantics, immutability → [oop-and-language-concepts.md](oop-and-language-concepts.md)
- Process/thread memory isolation, virtual memory → [operating-systems.md](operating-systems.md)
