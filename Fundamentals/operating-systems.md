# 🖥️ Operating Systems

!!! tip "Explain in 2 min"
    An OS manages hardware and shares it safely among programs. Two abstractions
    carry most interview weight. (1) **Process vs thread** — a process is an isolated program with its
    own memory; threads live inside a process and share its memory, so they're cheaper to switch but
    require synchronization. (2) **Virtual memory** — each process sees its own contiguous address
    space, which the OS maps to physical RAM in pages, letting programs use more memory than exists
    (paging to disk) and staying isolated from each other. The **scheduler** decides which thread runs
    next; a **context switch** saves one thread's state and loads another's, which costs real time.
    **Deadlock** is the classic hazard when processes wait on each other's resources forever.

---

## Process vs thread `[core]`

| | Process | Thread |
|--|---------|--------|
| Memory | own isolated address space | shares process memory |
| Creation cost | heavy | light |
| Communication | IPC (pipes, sockets, shared mem) | shared variables (needs locks) |
| Crash blast radius | isolated (one process dies) | can take down the whole process |
| Context switch cost | higher (swap address space + TLB) | lower |

**Rule of thumb:** threads for shared-state, low-overhead concurrency within one program; processes
for isolation and fault containment (a crash in one doesn't corrupt the others). In Python the GIL
pushes CPU-bound work toward processes — see [concurrency-and-parallelism.md](concurrency-and-parallelism.md).

---

## Context switch `[core]`

Saving the CPU state (registers, program counter, stack pointer) of the current thread and loading
another's so the CPU can switch execution. It's pure overhead — no useful work happens during the
switch — and it also pollutes CPU caches and the TLB, so *too many* switches (thread thrashing) hurt
throughput. Triggered by the scheduler's time slice expiring, a blocking I/O call, or a higher
priority thread becoming runnable.

---

## Scheduling `[core]`

The scheduler picks which runnable thread gets the CPU next, balancing responsiveness against
throughput and fairness.

| Policy | Idea | Trade-off |
|--------|------|-----------|
| FCFS | first come first served | simple; long jobs block short ones (convoy effect) |
| Round Robin | fixed time slice each, cycle | fair, responsive; overhead from switches |
| SJF / SRTF | shortest job first | optimal wait time; can starve long jobs, needs prediction |
| Priority | highest priority first | can starve low priority (fix with **aging**) |
| Multilevel feedback queue | multiple queues, jobs move by behavior | flexible; what real OSes approximate |

**Preemptive** (OS can interrupt a running thread) vs **cooperative** (thread runs until it yields).
Modern OSes are preemptive; cooperative shows up in async event loops.

---

## Virtual memory & paging `[core]`

Each process gets its own **virtual address space**; the OS + MMU translate virtual addresses to
physical RAM via **page tables**, in fixed-size **pages** (commonly 4 KB).

- **Isolation & security** — a process can't touch another's memory.
- **Overcommit** — total virtual memory can exceed physical RAM; inactive pages are **paged out** to
  disk and brought back on a **page fault**.
- **TLB** — a cache of recent virtual→physical translations; a TLB miss makes address translation
  slower, so locality matters.
- **Thrashing** — when working sets exceed RAM, the system spends most of its time paging in/out
  instead of doing work. The fix is more RAM or a smaller working set, not more paging.

Demand paging (load a page only when first accessed) keeps startup cheap.

---

## Deadlock `[core]`

Processes/threads wait on resources held by each other, forever. Requires all four **Coffman
conditions** simultaneously:

1. **Mutual exclusion** — a resource is held exclusively.
2. **Hold and wait** — hold one resource while requesting another.
3. **No preemption** — resources can't be forcibly taken.
4. **Circular wait** — a cycle of waiting processes.

Break *any one* to prevent deadlock. Practical strategies:
- **Prevention** — impose a global **resource ordering** (kills circular wait) — the most common
  real-world fix.
- **Avoidance** — Banker's algorithm grants only if a safe state remains (rarely used in practice).
- **Detection & recovery** — let it happen, detect cycles, kill/restart a victim.

Same conditions and fixes apply to lock deadlock in application code →
[concurrency-and-parallelism.md](concurrency-and-parallelism.md).

---

## Memory management `[core]`

- **Stack** — per-thread, LIFO, holds call frames and locals; fast, auto-freed on return; limited
  size (stack overflow on deep recursion).
- **Heap** — dynamically allocated, shared within a process; flexible but slower and prone to
  fragmentation and leaks.
- **Fragmentation** — external (free memory split into unusable gaps) vs internal (allocated block
  larger than needed).

Garbage collection, reference counting, and language-runtime specifics live in
memory-and-runtime.md *(planned)*.

---

## System calls `[core]`

The controlled entry point from **user mode** into **kernel mode** — how a program asks the OS to do
privileged things (open a file, send on a socket, spawn a process). It involves a mode switch, which
is more expensive than a normal function call, so high-performance code batches syscalls (e.g. `epoll`
over per-connection reads, buffered I/O over per-byte writes).

**User mode vs kernel mode**: user code runs sandboxed with limited privileges; the kernel runs with
full hardware access. This boundary is what keeps a buggy program from crashing the machine.

---

## Common interview traps

- Saying threads are "always faster" — they're cheaper to switch, but shared state needs
  synchronization and a thread crash can kill the whole process.
- Confusing concurrency (OS scheduling interleaving threads) with parallelism (multiple cores) —
  see [concurrency-and-parallelism.md](concurrency-and-parallelism.md).
- Forgetting virtual memory is about *isolation + overcommit*, not just "more memory."
- Listing only some Coffman conditions — all four are required, and breaking one is enough.
- Ignoring that syscalls and context switches are real costs in latency-sensitive code.

## Related

- Q&A drills: [qa-operating-systems.md](../QA-Bank/qa-operating-systems.md)
- Threads, locks, deadlock in app code → [concurrency-and-parallelism.md](concurrency-and-parallelism.md)
- GC, reference counting, Python runtime → [memory-and-runtime.md](memory-and-runtime.md)
- Estimation / latency numbers → [SystemDesign/SystemDesignGuide.md](../SystemDesign/SystemDesignGuide.md)
