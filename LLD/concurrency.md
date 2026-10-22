---
title: Concurrency in LLD
description: Thread-safety for low-level design rounds - race conditions, locks, atomics, semaphores, condition variables, deadlock avoidance, thread pools, the canonical double-booking fix, and the Python GIL caveat. The biggest SDE-1 → SDE-2 gap.
---

# Concurrency in LLD

The single biggest gap between SDE-1 and SDE-2 LLD. Companies like Uber, Walmart, and Flipkart
push hard here. The question is almost always some variant of: *"multiple threads hit your
in-memory store at once - don't lose data, don't double-book, don't deadlock."*

!!! note "Language"
    Examples in **Java** - most LLD interviews are in Java and Java's concurrency model (true
    parallel threads) is what interviewers probe. Python's GIL gives a different story, kept here
    as a short prose talking point. See also
    [Fundamentals → Concurrency & Parallelism](../Fundamentals/concurrency-and-parallelism.md) for
    the CS-level treatment, and [Concurrency Q&A](../QA-Bank/qa-concurrency.md) for drills.

## Why it matters in an LLD round

Your "database" is an in-memory data structure. In a single-threaded demo that's fine. The
moment the interviewer says *"what if two users book the last seat simultaneously?"*, a
plain `dict`/`HashMap` with check-then-act logic is **broken**:

```java
// RACE CONDITION - two threads can both pass the check before either writes
boolean book(String seatId) {
    if ("FREE".equals(seats.get(seatId))) {   // T1 and T2 both read FREE
        seats.put(seatId, "BOOKED");          // both write -> double booking
        return true;
    }
    return false;
}
```

This is a **check-then-act** race (also called TOCTOU - time-of-check to time-of-use). The
read and the write are not atomic together.

---

## Core vocabulary (say these out loud in the interview)

- **Race condition** - outcome depends on thread timing; the classic check-then-act bug.
- **Critical section** - the code that touches shared state; must run atomically.
- **Mutual exclusion (mutex/lock)** - only one thread in the critical section at a time.
- **Atomicity** - an operation completes fully or not at all; no thread sees a half-state.
- **Deadlock** - threads wait on each other forever (A holds L1 wants L2; B holds L2 wants L1).
- **Starvation** - a thread never gets the lock because others keep winning.
- **Liveness vs safety** - *safety* = nothing bad happens (no double-book); *liveness* =
  something good eventually happens (no deadlock/starvation).
- **Thread-safe** - a class behaves correctly under concurrent access.

---

## Python's GIL - the honest caveat

CPython has a **Global Interpreter Lock**: only one thread executes Python bytecode at a
time. Consequences you should state:

- Python threads give **concurrency, not parallelism** for CPU-bound work. For CPU parallelism
  you'd use `multiprocessing`.
- The GIL does **not** make your code thread-safe. A single bytecode op is atomic, but a
  check-then-act (read a seat, see FREE, then write BOOKED) is **multiple** ops → still races.
  You still need locks.
- Java has true parallel threads, so Java's thread-safety concerns are sharper - which is why
  interviewers usually want the Java reasoning.

> Interview line: *"In CPython the GIL serializes bytecode so I get concurrency not
> parallelism, but check-then-act still isn't atomic, so I'll guard the critical section with
> a lock - exactly as I would in Java, where threads run truly in parallel."*

---

## Tool 1 - Locks (mutual exclusion)

```java
import java.util.concurrent.locks.ReentrantLock;

public class SeatStore {
    private final Map<String, String> seats = new HashMap<>();
    private final ReentrantLock lock = new ReentrantLock();

    public boolean book(String seatId) {
        lock.lock();
        try {
            if ("FREE".equals(seats.get(seatId))) {
                seats.put(seatId, "BOOKED");
                return true;
            }
            return false;
        } finally {
            lock.unlock();               // ALWAYS unlock in finally
        }
    }
}
```

Java also has the `synchronized` keyword (simpler, less flexible):

```java
public synchronized boolean book(String seatId) { ... }   // locks on 'this'
// or a block:
synchronized (someLock) { ... }
```

`synchronized` vs `ReentrantLock`: use `synchronized` for simple cases; reach for
`ReentrantLock` when you need `tryLock()` (timeout), fairness, or interruptible locking.

### Reentrancy
Both `threading.RLock` (Python) and `ReentrantLock`/`synchronized` (Java) let the **same
thread** re-acquire a lock it already holds (needed when method A holds the lock and calls
method B that also locks). A plain `threading.Lock()` would **deadlock on itself** - use
`RLock` if a locked method calls another locked method on the same object.

---

## Tool 2 - Lock granularity (coarse vs fine)

One global lock is correct but slow - it serializes *everything*. Finer locks = more
parallelism, more deadlock risk.

```java
// FINE-GRAINED: one lock per seat -> two users booking DIFFERENT seats don't block each other
class SeatStore {
    private final Map<String, String> seats = new HashMap<>();
    private final Map<String, ReentrantLock> locks = new HashMap<>();

    SeatStore(List<String> seatIds) {
        for (String s : seatIds) {
            seats.put(s, "FREE");
            locks.put(s, new ReentrantLock());
        }
    }

    boolean book(String seatId) {
        ReentrantLock lock = locks.get(seatId);
        lock.lock();                         // only locks THIS seat
        try {
            if ("FREE".equals(seats.get(seatId))) {
                seats.put(seatId, "BOOKED");
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }
}
```

Talking point: *"Coarse lock is simplest and always correct; I'd start there, then shard the
lock per-seat (or per-level in a parking lot) if the interviewer pushes on throughput."*

---

## Tool 3 - Atomics & concurrent collections (lock-free-ish)

For simple counters/flags, atomic operations avoid explicit locks.

```java
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.ConcurrentHashMap;

AtomicInteger ticketId = new AtomicInteger(0);
int next = ticketId.incrementAndGet();          // atomic, no lock needed

Map<String,String> seats = new ConcurrentHashMap<>();
// atomic check-then-act in ONE call - this is the clean fix for double-booking:
boolean booked = seats.replace(seatId, "FREE", "BOOKED");   // CAS: only succeeds if currently FREE
// or:
seats.putIfAbsent(key, value);                  // atomic
seats.compute(key, (k,v) -> ...);               // atomic read-modify-write
```

`ConcurrentHashMap` is the default thread-safe map in Java LLD. Its `replace(k, oldV, newV)`
is a compare-and-swap that solves check-then-act in a single atomic step - mention it.

Python equivalent: there's no `ConcurrentHashMap`. `queue.Queue` is thread-safe; for maps you
guard a `dict` with a `Lock`, or use `threading` primitives. State this difference.

---

## Tool 4 - Semaphore (limit N concurrent, not just 1)

Use when up to N threads may enter (e.g. a parking lot with N free spots, a connection pool
of size N).

```java
import java.util.concurrent.Semaphore;
Semaphore spots = new Semaphore(100);
if (spots.tryAcquire()) { /* park */ } else { /* full */ }
// spots.release() when the car leaves
```

Lock = semaphore with 1 permit. Semaphore = generalization to N.

---

## Tool 5 - Condition variables (wait for a state)

Use when a thread must **wait until** some condition holds (producer/consumer, "wait for a
spot to free up").

```java
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

class BoundedLot {
    private int free;
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull = lock.newCondition();

    BoundedLot(int capacity) { this.free = capacity; }

    void park() throws InterruptedException {
        lock.lock();
        try {
            while (free == 0) {
                notFull.await();          // releases lock, sleeps until signalled
            }
            free--;
        } finally {
            lock.unlock();
        }
    }

    void leave() {
        lock.lock();
        try {
            free++;
            notFull.signal();             // wake one waiting thread
        } finally {
            lock.unlock();
        }
    }
}
```

Always `await()` inside a `while` (not `if`) to re-check the condition after waking - guards
against spurious wakeups and lost races.

---

## Deadlock - causes & avoidance

Deadlock needs all four (Coffman conditions): mutual exclusion, hold-and-wait, no preemption,
circular wait. Break any one.

Most practical fixes:

1. **Lock ordering** - always acquire multiple locks in a consistent global order (e.g. by
   seat id). Breaks circular wait. This is the #1 answer interviewers want.
2. **`tryLock` with timeout** - if you can't get all locks, back off and retry.
3. **Coarse lock** - one lock = can't deadlock (at the cost of throughput).

```java
// transfer money between two accounts WITHOUT deadlock: lock in a fixed order
void transfer(Account a, Account b, int amount) {
    // consistent ordering by id breaks circular wait
    Account first  = a.id < b.id ? a : b;
    Account second = a.id < b.id ? b : a;
    first.lock.lock();
    try {
        second.lock.lock();
        try {
            a.balance -= amount;
            b.balance += amount;
        } finally {
            second.lock.unlock();
        }
    } finally {
        first.lock.unlock();
    }
}
```

---

## The canonical "double booking" solution (reference answer)

When asked *"two users book the last seat at once"*, present this progression:

1. **Name the bug**: check-then-act race; a plain map double-books.
2. **Fix v1 (lock)**: wrap check+write in a lock → correct, coarse.
3. **Fix v2 (fine-grained)**: per-seat lock → correct + concurrent across seats.
4. **Fix v3 (lock-free)**: `ConcurrentHashMap.replace(seat, FREE, BOOKED)` (Java) - atomic
   CAS, no explicit lock.
5. **Mention seat-hold + timeout**: hold a seat for N minutes (a `State`: HELD), release via a
   scheduled task if payment doesn't complete → `ScheduledExecutorService` (Java) /
   `threading.Timer` (Python).

```java
// Fine-grained + hold-with-timeout sketch
import java.util.concurrent.*;
import java.util.concurrent.locks.ReentrantLock;

class SeatBooking {
    private final Map<String, String> state = new HashMap<>();   // FREE | HELD | BOOKED
    private final Map<String, ReentrantLock> locks = new HashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    SeatBooking(List<String> seatIds) {
        for (String s : seatIds) {
            state.put(s, "FREE");
            locks.put(s, new ReentrantLock());
        }
    }

    boolean hold(String seatId, int holdSeconds) {
        ReentrantLock lock = locks.get(seatId);
        lock.lock();
        try {
            if (!"FREE".equals(state.get(seatId))) return false;
            state.put(seatId, "HELD");
        } finally {
            lock.unlock();
        }
        scheduler.schedule(() -> releaseIfHeld(seatId), holdSeconds, TimeUnit.SECONDS);
        return true;
    }

    boolean confirm(String seatId) {
        ReentrantLock lock = locks.get(seatId);
        lock.lock();
        try {
            if ("HELD".equals(state.get(seatId))) {
                state.put(seatId, "BOOKED");
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }

    private void releaseIfHeld(String seatId) {
        ReentrantLock lock = locks.get(seatId);
        lock.lock();
        try {
            if ("HELD".equals(state.get(seatId))) state.put(seatId, "FREE");
        } finally {
            lock.unlock();
        }
    }
}
```

---

## Thread pools / executors (don't spawn raw threads)

For "process many requests concurrently", use a pool, not `Thread()` per request.

```java
import java.util.concurrent.*;
ExecutorService pool = Executors.newFixedThreadPool(10);
Future<Boolean> f = pool.submit(() -> handle(req));
ScheduledExecutorService sched = Executors.newScheduledThreadPool(1);
sched.schedule(() -> releaseSeat(id), 5, TimeUnit.MINUTES);   // seat-hold timeout
pool.shutdown();
```

---

## Checklist to mention when asked "is this thread-safe?"

- [ ] Identify shared mutable state (the maps/counters)
- [ ] Identify critical sections (check-then-act, read-modify-write)
- [ ] Guard them: lock, atomic/CAS, or concurrent collection
- [ ] Choose lock granularity (start coarse, refine if pushed)
- [ ] Avoid deadlock (consistent lock ordering)
- [ ] Prefer immutable objects where possible (immutable = inherently thread-safe)
- [ ] Use executors/pools, not raw threads
- [ ] For Python, note the GIL (concurrency not parallelism) but that locks are still required

> Immutability is the cheapest concurrency win: an object that never changes after
> construction needs no locking. Model value objects (Money, Ticket, SeatId) as immutable.

## Related

- The double-booking fix applied end-to-end → [Worked Problems → BookMyShow & Rate Limiter](worked-problems.md)
- Locking/synchronization syntax in Java → [Java Cheat Sheet](java-cheatsheet.md)
- CS-level threading, memory model, deadlock → [Fundamentals → Concurrency & Parallelism](../Fundamentals/concurrency-and-parallelism.md)
- Drill questions → [Concurrency Q&A](../QA-Bank/qa-concurrency.md)
- [LLD Roadmap](roadmap.md) · [Overview](lld-overview.md)
