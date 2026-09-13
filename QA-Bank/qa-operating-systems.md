# ❓ Operating Systems — Q&A

> Pairs with [Fundamentals/operating-systems.md](../Fundamentals/operating-systems.md). Format and
> tag legend: [QA-Bank/README.md](README.md).

---

> **Q1. Process vs thread?**
> A process is an isolated program with its own address space; a thread runs inside a process and
> shares its memory. Threads are cheaper to create and switch and communicate via shared variables;
> processes are isolated, so a crash in one doesn't corrupt others but they need IPC to talk.
> *Follow-ups:* When would you pick multiprocessing over threads? (CPU-bound work, fault isolation.)
> `Easy` · `MAANG`

> **Q2. What happens during a context switch, and why does it cost?**
> The OS saves the current thread's CPU state (registers, PC, stack pointer) and loads another's so
> the CPU can switch execution. It's pure overhead — no useful work happens — and it also evicts
> cache/TLB entries, so excessive switching hurts throughput.
> *Follow-ups:* What triggers one? (time-slice expiry, blocking I/O, higher-priority thread.)
> `Med` · `MAANG`

> **Q3. What is virtual memory and why do we have it?**
> Each process gets its own virtual address space that the OS/MMU maps to physical RAM in pages. It
> gives isolation (processes can't touch each other's memory) and overcommit (total virtual memory
> can exceed RAM, with inactive pages paged to disk).
> *Follow-ups:* What's a page fault? What's thrashing?
> `Med` · `MAANG`

> **Q4. Explain paging and the TLB.**
> Memory is split into fixed-size pages; page tables map virtual pages to physical frames. The TLB
> caches recent translations so the CPU doesn't walk the page table every access — a TLB miss makes
> that access much slower, which is why memory locality matters.
> *Follow-ups:* What is demand paging?
> `Med` · `Google`

> **Q5. What is thrashing?**
> When the combined working set exceeds physical RAM, the system spends most of its time paging
> pages in and out rather than doing work, and throughput collapses. The fix is more RAM or a
> smaller working set — not more swap.
> *Follow-ups:* How would you detect it in production? (high page-fault rate, low CPU utilization.)
> `Med` · `MAANG`

> **Q6. Stack vs heap?**
> The stack holds call frames and locals, is per-thread, and is auto-freed on return (fast, limited
> size). The heap holds dynamically allocated objects, is shared within a process, and lives until
> freed/GC'd (flexible, slower, can fragment or leak).
> *Follow-ups:* What causes a stack overflow? (deep/infinite recursion.)
> `Easy` · `MAANG`

> **Q7. What are the four Coffman conditions for deadlock?**
> Mutual exclusion, hold-and-wait, no preemption, and circular wait — all four must hold
> simultaneously. Breaking any one prevents deadlock.
> *Follow-ups:* Which is easiest to break in practice? (circular wait, via a global lock ordering.)
> `Med` · `MAANG`

> **Q8. How do you prevent deadlock?**
> The most practical approach is to impose a global resource-ordering so a circular wait can't form.
> Others: avoidance (Banker's algorithm — rarely used), or detection + recovery (detect cycles, kill
> a victim).
> *Follow-ups:* Difference between deadlock prevention and avoidance?
> `Med` · `Amazon`

> **Q9. Preemptive vs cooperative scheduling?**
> Preemptive: the OS can interrupt a running thread at any time (fair, responsive, what modern OSes
> use). Cooperative: a task runs until it voluntarily yields (simpler, but one misbehaving task can
> starve everyone) — the model behind async event loops.
> *Follow-ups:* Where do you see cooperative scheduling today? (asyncio, older systems.)
> `Med` · `MAANG`

> **Q10. Name a few CPU scheduling policies and a trade-off of each.**
> FCFS (simple, but long jobs block short ones), Round Robin (fair/responsive, switch overhead),
> Shortest Job First (optimal wait, can starve long jobs), Priority (can starve low priority — fix
> with aging). Real OSes approximate a multilevel feedback queue.
> *Follow-ups:* What is priority inversion?
> `Med` · `Google`

> **Q11. What is a system call?**
> The controlled entry point from user mode into kernel mode — how a program requests a privileged
> operation (open a file, send on a socket). It involves a mode switch, which is costlier than a
> normal function call, so hot paths batch syscalls.
> *Follow-ups:* Why is user/kernel mode separation important? (isolation, stability, security.)
> `Med` · `MAANG`

> **Q12. User mode vs kernel mode?**
> User mode runs application code sandboxed with limited privileges; kernel mode has full hardware
> access. The boundary keeps a buggy or malicious program from crashing the machine or reading other
> processes' memory.
> *Follow-ups:* What causes a transition into kernel mode? (syscalls, interrupts, faults.)
> `Easy` · `MAANG`

> **Q13. How do processes communicate (IPC)?**
> Via pipes, message queues, shared memory, sockets, or signals. Shared memory is fastest (no copy)
> but needs synchronization; message passing is safer but copies data.
> *Follow-ups:* Trade-off between shared memory and message passing?
> `Med` · `Amazon`

> **Q14. What is a zombie process? An orphan?**
> A zombie has finished but its exit status hasn't been reaped by the parent, so its entry lingers
> in the process table. An orphan's parent died first; it gets re-parented (to init/PID 1), which
> reaps it.
> *Follow-ups:* How do you avoid accumulating zombies? (parent calls wait().)
> `Hard` · `Google`

> **Q15. Concurrency vs parallelism (at the OS level)?**
> Concurrency is the OS interleaving multiple threads so they make progress (possible on one core);
> parallelism is threads literally running at once on multiple cores. Scheduling gives concurrency;
> multiple cores give parallelism.
> *Follow-ups:* Can you have concurrency without parallelism? (yes — single core, time-sliced.)
> `Easy` · `MAANG`

> **Q16. What is a mutex vs a semaphore (OS view)?**
> A mutex allows one holder at a time (ownership-based mutual exclusion). A semaphore is a counter
> allowing up to N holders — useful to cap concurrent access to a pool of resources. A binary
> semaphore resembles a mutex but has no ownership concept.
> *Follow-ups:* Why does ownership matter? (correct release, priority inheritance.)
> `Med` · `MAANG`

> **Q17. What is memory fragmentation?**
> External fragmentation: free memory is split into scattered gaps too small to satisfy a request
> even though total free space is enough. Internal: an allocated block is bigger than requested, so
> the slack is wasted. Compaction or better allocators mitigate it.
> *Follow-ups:* How does paging help with external fragmentation? (fixed-size frames avoid it.)
> `Hard` · `Google`

> **Q18. Why is a page size a trade-off?**
> Larger pages mean smaller page tables and better TLB coverage but more internal fragmentation and
> wasted I/O when paging. Smaller pages waste less memory but need bigger page tables and cause more
> TLB misses.
> *Follow-ups:* What are huge pages used for? (databases, JVMs — reduce TLB pressure.)
> `Hard` · `Amazon`

---

**Related:** [Fundamentals/operating-systems.md](../Fundamentals/operating-systems.md) ·
[qa-concurrency.md](qa-concurrency.md) · [qa-language-python.md](qa-language-python.md)
