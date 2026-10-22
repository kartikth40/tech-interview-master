---
title: LLD Worked Problems
description: Three fully solved LLD problems - Parking Lot, Movie Booking (BookMyShow), and Rate Limiter - from requirements to runnable code, each with design trade-offs and talking points.
---

# LLD Worked Problems

The highest-leverage practice: full designs from requirements → classes → working code, so you
have reference solutions to compare your own attempts against. Three problems, each showing a
different relationship/pattern mix:

1. **Parking Lot** - composition/aggregation + Strategy + Factory (the canonical starter)
2. **Movie Booking (BookMyShow)** - relationships + State + concurrency (double-booking)
3. **Rate Limiter** - concurrency-first, thread-safe, Strategy

Java for the full code; key Java idioms noted inline ([Java Cheat Sheet](java-cheatsheet.md)).
Each follows the 7-step framework from the [overview](lld-overview.md#delivery-framework-7-steps-for-every-round).

!!! note "Reference implementations"
    The code below is written to be **correct and readable as an interview reference** — it is
    **not compiled or run** by this site. Treat it as the target to diff your own attempt against,
    not as a packaged, executable project.

!!! tip "How to use"
    Attempt the problem yourself first (5-min clarify → nouns → relationships → classes → code),
    **then** read the solution and diff your design. Reading alone won't build the muscle. These
    also appear in compact form in the [Low-Level Design Guide](LowLevelDesign.md); here they're
    expanded with trade-offs and concurrency.

---

# Problem 1 - Parking Lot

## Step 1: Clarify (questions to ask)
- Multiple levels/floors? → **yes, N levels**
- Vehicle types & sizes? → **bike / car / truck**, each needs a spot of matching size
- How is a spot chosen? → pluggable (**nearest to entry**, etc.) → Strategy
- Payment/ticket? → issue a **ticket** on entry, compute fee on exit by duration
- Concurrency? → assume single-threaded for v1, note where locks go (see Problem 3 for the
  concurrent version)

## Step 2: Nouns → prune
`ParkingLot, Level, ParkingSpot, Vehicle(Car/Bike/Truck), Ticket, SpotAllocationStrategy`.
Dropped: *plate number* (attribute of Vehicle), *fee* (computed on Ticket).

## Step 3: Relationships
- `ParkingLot` ◆── `Level` (composition - levels die with the lot)
- `Level` ◆── `ParkingSpot` (composition)
- `ParkingSpot` ──→ `Vehicle` (association - vehicle exists independently)
- `ParkingLot` ──→ `SpotAllocationStrategy` (aggregation - strategy injected)
- `Vehicle` ──▷ `Car/Bike/Truck` (inheritance; `Vehicle` abstract)

## Steps 4–6: Classes + SOLID + patterns

```java
import java.util.*;

// size ordinal gives the ordering: SMALL < MEDIUM < LARGE
enum VehicleSize { SMALL, MEDIUM, LARGE } // bike, car, truck

// --- Vehicle hierarchy (abstraction + inheritance) ---
abstract class Vehicle {
    final String plate;
    final VehicleSize size;
    Vehicle(String plate, VehicleSize size) { this.plate = plate; this.size = size; }
}
class Bike  extends Vehicle { Bike(String plate)  { super(plate, VehicleSize.SMALL);  } }
class Car   extends Vehicle { Car(String plate)   { super(plate, VehicleSize.MEDIUM); } }
class Truck extends Vehicle { Truck(String plate) { super(plate, VehicleSize.LARGE);  } }

// --- Factory (creational) - callers don't new-up concrete classes ---
class VehicleFactory {
    static Vehicle create(String kind, String plate) {
        switch (kind) {
            case "bike":  return new Bike(plate);
            case "car":   return new Car(plate);
            case "truck": return new Truck(plate);
            default: throw new IllegalArgumentException("unknown kind: " + kind);
        }
    }
}

class ParkingSpot {
    final String spotId;
    final VehicleSize size;
    Vehicle vehicle; // null when free

    ParkingSpot(String spotId, VehicleSize size) { this.spotId = spotId; this.size = size; }

    boolean isFree() { return vehicle == null; }
    boolean canFit(Vehicle v) { return isFree() && v.size.ordinal() <= size.ordinal(); }
    void park(Vehicle v) { vehicle = v; }
    void vacate() { vehicle = null; }
}

class Level {
    final int levelId;
    final List<ParkingSpot> spots; // composition - created/owned here

    Level(int levelId, List<ParkingSpot> spots) { this.levelId = levelId; this.spots = spots; }

    List<ParkingSpot> availableSpots(Vehicle v) {
        List<ParkingSpot> fits = new ArrayList<>();
        for (ParkingSpot s : spots) if (s.canFit(v)) fits.add(s);
        return fits;
    }
}

// --- Strategy (behavioral) - how to pick a spot, swappable ---
interface SpotAllocationStrategy {
    ParkingSpot allocate(List<Level> levels, Vehicle v); // null if none fits
}

class FirstAvailableStrategy implements SpotAllocationStrategy {
    public ParkingSpot allocate(List<Level> levels, Vehicle v) {
        for (Level level : levels) {
            List<ParkingSpot> fits = level.availableSpots(v);
            if (!fits.isEmpty()) return fits.get(0);
        }
        return null;
    }
}

class BestFitStrategy implements SpotAllocationStrategy { // smallest spot that fits -> less waste
    public ParkingSpot allocate(List<Level> levels, Vehicle v) {
        ParkingSpot best = null;
        for (Level level : levels) {
            for (ParkingSpot s : level.availableSpots(v)) {
                if (best == null || s.size.ordinal() < best.size.ordinal()) best = s;
            }
        }
        return best;
    }
}

class Ticket {
    static int counter = 1;
    final int ticketId;
    final ParkingSpot spot;
    final Vehicle vehicle;
    final long entryTimeMs;

    Ticket(ParkingSpot spot, Vehicle vehicle) {
        this.ticketId = counter++;
        this.spot = spot;
        this.vehicle = vehicle;
        this.entryTimeMs = System.currentTimeMillis();
    }
}

class ParkingLot {
    final List<Level> levels;              // composition
    final SpotAllocationStrategy strategy; // aggregation (injected) - DIP
    final Map<String, Ticket> active = new HashMap<>(); // plate -> ticket

    ParkingLot(List<Level> levels, SpotAllocationStrategy strategy) {
        this.levels = levels;
        this.strategy = strategy;
    }

    Ticket park(Vehicle v) {
        ParkingSpot spot = strategy.allocate(levels, v);
        if (spot == null) return null;     // lot full for this size
        spot.park(v);
        Ticket ticket = new Ticket(spot, v);
        active.put(v.plate, ticket);
        return ticket;
    }

    double unpark(String plate) {
        Ticket ticket = active.remove(plate);
        ticket.spot.vacate();
        long elapsedMs = System.currentTimeMillis() - ticket.entryTimeMs;
        long hours = Math.max(1, elapsedMs / 3_600_000 + 1);
        return hours * 50.0;               // flat ₹50/hr
    }
}

// --- demo (your "working demo") ---
public class ParkingLotDemo {
    public static void main(String[] args) {
        List<ParkingSpot> spotsL0 = Arrays.asList(
            new ParkingSpot("L0-1", VehicleSize.SMALL),
            new ParkingSpot("L0-2", VehicleSize.MEDIUM),
            new ParkingSpot("L0-3", VehicleSize.LARGE));
        ParkingLot lot = new ParkingLot(
            Arrays.asList(new Level(0, spotsL0)), new BestFitStrategy());

        Vehicle car = VehicleFactory.create("car", "KA01AB1234");
        Ticket t = lot.park(car);
        System.out.println("parked at " + t.spot.spotId);   // parked at L0-2 (best fit for a car)
        System.out.println("fee: " + lot.unpark("KA01AB1234")); // fee: 50.0
    }
}
// Expected output:
// parked at L0-2
// fee: 50.0
```

**Talking points to say out loud:** `Vehicle` is abstract (shared blueprint → OCP: add
`Van` without touching anything); spot allocation is Strategy (swap policy at runtime);
`ParkingLot` depends on the `SpotAllocationStrategy` *abstraction* (DIP); for concurrency,
guard `park`/`unpark` with a lock or make the spot grab a CAS (see Problem 3).

### Key design trade-offs
- **Vehicle: inheritance vs composition.** I used a small inheritance hierarchy because
  `Bike/Car/Truck` is a genuine, stable is-a with only a size difference. If vehicles gained
  independent axes (fuel type, EV charging, size), inheritance would explode combinatorially -
  switch to composition (`Vehicle` *has* an `EngineType`, a `SizeClass`). Say which future you're
  betting on.
- **Allocation: Strategy vs a flag.** Strategy is worth it here because the policy genuinely
  varies (first-fit vs best-fit vs nearest-to-exit) and realistically grows. For exactly two
  fixed policies, a boolean + `if` would be lighter - call that out rather than defaulting to
  the pattern.
- **FirstAvailable vs BestFit.** FirstAvailable is O(spots-until-hit) and cheap but wastes
  large spots on small cars; BestFit reduces waste but scans all spots (O(n)) - in a real
  system you'd keep per-size free-lists/heaps so allocation is O(1) amortized. Mention the data
  structure, not just the policy.
- **Fee model.** Kept a flat hourly rate for the demo; flagged that tiered/vehicle-based
  pricing is itself a Strategy if the interviewer pushes.

---

# Problem 2 - Movie Booking (BookMyShow)

## Step 1: Clarify
- Scope: cities → theaters → screens → shows → seats? → **yes**
- Seat hold before payment? → **hold for 5 min, then release** → State + timeout
- Double booking under concurrency? → **must prevent** → locking
- Payment? → abstract behind an interface (Strategy/adapter)

## Step 2: Nouns → prune
`City, Theater, Screen, Show, Seat, Booking, Payment, User`.
Dropped: *ticket price* (on Show/Seat), *seat number* (attribute of Seat).

## Step 3: Relationships
- `Theater` ◆── `Screen` (composition)
- `Screen` ◆── `Seat` (composition - "no screen, no seat")
- `Screen` ──→ `Show` (a show runs on a screen; show references screen - association)
- `User` ──→ `Booking` (user creates booking - association)
- `Booking` ◆── `Payment` (payment owned by the booking)
- Movie ──→ Theater is **aggregation** (one movie runs in many theaters, outlives them)

## Steps 4–6: Classes + State + concurrency

```java
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.ReentrantLock;

enum SeatStatus { FREE, HELD, BOOKED }

class Seat {
    final String label;
    SeatStatus status = SeatStatus.FREE;
    Seat(String label) { this.label = label; }
}

// --- Payment behind an abstraction (DIP + Strategy) ---
interface PaymentGateway {
    boolean pay(double amount);
}
class UpiGateway implements PaymentGateway {
    public boolean pay(double amount) { return true; } // pretend it talks to UPI
}

class Show {
    final String showId;
    final double price;
    final Map<String, Seat> seats = new HashMap<>();
    // fine-grained locking: one lock per seat so different seats don't block each other
    final Map<String, ReentrantLock> locks = new HashMap<>();
    // shared scheduler for the 5-min auto-release of un-confirmed holds
    final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    Show(String showId, List<Seat> seatList, double price) {
        this.showId = showId;
        this.price = price;
        for (Seat s : seatList) {
            seats.put(s.label, s);
            locks.put(s.label, new ReentrantLock());
        }
    }

    boolean hold(String label) {
        ReentrantLock lock = locks.get(label);
        lock.lock();                                  // critical section - prevents double booking
        try {
            Seat seat = seats.get(label);
            if (seat.status == SeatStatus.FREE) {
                seat.status = SeatStatus.HELD;
                // auto-release the hold after 5 min if not confirmed
                scheduler.schedule(() -> releaseIfHeld(label), 5, TimeUnit.MINUTES);
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }

    boolean confirm(String label) {
        ReentrantLock lock = locks.get(label);
        lock.lock();
        try {
            Seat seat = seats.get(label);
            if (seat.status == SeatStatus.HELD) {
                seat.status = SeatStatus.BOOKED;
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }

    void releaseIfHeld(String label) {
        ReentrantLock lock = locks.get(label);
        lock.lock();
        try {
            if (seats.get(label).status == SeatStatus.HELD) {
                seats.get(label).status = SeatStatus.FREE;
            }
        } finally {
            lock.unlock();
        }
    }
}

class Booking {
    static int counter = 1;
    final int bookingId;
    final String user;
    final Show show;
    final List<String> seatLabels;
    boolean confirmed = false;

    Booking(String user, Show show, List<String> seatLabels) {
        this.bookingId = counter++;
        this.user = user;
        this.show = show;
        this.seatLabels = seatLabels;
    }

    boolean checkout(PaymentGateway gateway) {
        // 1) hold all requested seats one at a time (per-seat locks) with rollback
        List<String> held = new ArrayList<>();
        for (String label : seatLabels) {
            if (show.hold(label)) {
                held.add(label);
            } else {
                for (String h : held) show.releaseIfHeld(h); // roll back grabbed holds
                return false;
            }
        }
        // 2) pay
        double amount = show.price * seatLabels.size();
        if (!gateway.pay(amount)) {
            for (String h : held) show.releaseIfHeld(h);
            return false;
        }
        // 3) confirm
        for (String label : held) show.confirm(label);
        confirmed = true;
        return true;
    }
}

public class BookMyShowDemo {
    public static void main(String[] args) {
        List<Seat> seats = new ArrayList<>();
        for (int i = 1; i <= 5; i++) seats.add(new Seat("A" + i));
        Show show = new Show("SHOW1", seats, 250.0);

        Booking b1 = new Booking("ravi", show, Arrays.asList("A1", "A2"));
        System.out.println("b1: " + b1.checkout(new UpiGateway()));        // b1: true

        // second user tries the SAME seat -> must fail (no double booking)
        Booking b2 = new Booking("asha", show, Arrays.asList("A2"));
        System.out.println("b2: " + b2.checkout(new UpiGateway()));        // b2: false
        System.out.println("A2 status: " + show.seats.get("A2").status);   // A2 status: BOOKED

        show.scheduler.shutdown(); // stop the daemon-less scheduler so the JVM can exit
    }
}
// Expected output:
// b1: true
// b2: false
// A2 status: BOOKED
```

**Talking points:** seat lifecycle is a `State` (FREE→HELD→BOOKED) enforced in `Show`;
double-booking solved by a **per-seat lock** guarding check-then-act; multi-seat booking
rolls back partial holds (atomicity); payment is behind `PaymentGateway` so UPI/card/wallet
are swappable; the 5-min hold is scheduled on a `ScheduledExecutorService` that auto-releases
an un-confirmed seat.

**If pushed on scale:** the per-seat lock is the key insight - mention that in a real system
this becomes a DB row lock / optimistic version check, but in an in-memory LLD the lock is the
analog.

### Key design trade-offs
- **Locking granularity: per-seat vs per-show.** Per-seat maximizes concurrency (two users
  booking different seats never block) at the cost of many lock objects and a subtle deadlock
  risk for multi-seat bookings - I avoid it by acquiring holds one at a time with rollback
  rather than holding several locks at once. A single per-show lock is dead simple and
  deadlock-free but serializes the whole show. Start per-show if asked for simplicity, go
  per-seat when asked for throughput - name the pivot.
- **Pessimistic lock vs optimistic (CAS).** A lock blocks; an optimistic
  `compare-and-swap(FREE→HELD)` doesn't block and scales better under low contention, but you
  must handle the retry/fail path. For the "everyone wants the last seat" hot-row case,
  optimistic retries can livelock - pessimistic is actually calmer there. Trade-off is
  contention-dependent; say so.
- **Hold-with-timeout vs no hold.** Holding a seat for 5 min improves UX (pay without losing
  the seat) but ties up inventory and needs a cleanup mechanism (timer/scheduled sweep). No
  hold is simpler but races the user against payment latency. This is a product trade-off, not
  just a code one.
- **Rollback strategy.** Releasing partial holds on failure keeps the booking atomic at the
  cost of extra bookkeeping; the alternative (let holds expire naturally) is simpler but leaves
  seats falsely blocked for the hold window.

---

# Problem 3 - Rate Limiter (concurrency-first)

The one that separates SDE-1 from SDE-2. Expect "make it thread-safe" immediately.

## Step 1: Clarify
- Per-user or global? → **per-user** (key = userId/IP)
- Which algorithm? → offer **Fixed Window, Sliding Window, Token Bucket** → Strategy
- Thread-safe? → **yes, mandatory**
- Distributed? → out of scope for LLD (would be Redis); do in-memory, mention the extension

## Step 2–3: Design
- `RateLimiter` ──→ `RateLimitStrategy` (aggregation/DIP - algorithm injected)
- Strategies: `FixedWindow`, `TokenBucket`, `SlidingWindowLog`
- Per-key state guarded by locks (fine-grained: one lock per key)

## Steps 4–6: Code

```java
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantLock;

interface RateLimitStrategy {
    boolean allow(String key);
}

// one ReentrantLock per key, created on demand (no two threads ever see different locks)
abstract class PerKeyLimiter implements RateLimitStrategy {
    private final Map<String, ReentrantLock> locks = new ConcurrentHashMap<>();
    ReentrantLock lockFor(String key) {
        return locks.computeIfAbsent(key, k -> new ReentrantLock());
    }
}

// N requests per fixed window (simple; bursty at window edges).
class FixedWindowLimiter extends PerKeyLimiter {
    private final int limit;
    private final long windowMs;
    private final Map<String, long[]> state = new ConcurrentHashMap<>(); // key -> [count, winStartMs]

    FixedWindowLimiter(int limit, double windowSec) {
        this.limit = limit;
        this.windowMs = (long) (windowSec * 1000);
    }

    public boolean allow(String key) {
        ReentrantLock lock = lockFor(key);
        lock.lock();                                       // guard check-then-act per key
        try {
            long now = System.currentTimeMillis();
            long[] s = state.get(key);
            if (s == null || now - s[1] >= windowMs) {     // new window -> reset
                state.put(key, new long[]{1, now});
                return true;
            }
            if (s[0] < limit) {
                s[0]++;
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }
}

// Refills tokens at a steady rate; allows controlled bursts up to capacity.
class TokenBucketLimiter extends PerKeyLimiter {
    private final double capacity;
    private final double refillPerSec;
    private final Map<String, double[]> state = new ConcurrentHashMap<>(); // key -> [tokens, lastMs]

    TokenBucketLimiter(int capacity, double refillPerSec) {
        this.capacity = capacity;
        this.refillPerSec = refillPerSec;
    }

    public boolean allow(String key) {
        ReentrantLock lock = lockFor(key);
        lock.lock();
        try {
            long now = System.currentTimeMillis();
            double[] s = state.get(key);
            double tokens, last;
            if (s == null) {
                tokens = capacity; last = now;             // first hit -> full bucket
            } else {
                tokens = s[0]; last = s[1];
            }
            // refill based on elapsed time, capped at capacity
            tokens = Math.min(capacity, tokens + (now - last) / 1000.0 * refillPerSec);
            if (tokens >= 1) {
                state.put(key, new double[]{tokens - 1, now});
                return true;
            }
            state.put(key, new double[]{tokens, now});
            return false;
        } finally {
            lock.unlock();
        }
    }
}

// Exact: keep timestamps in the last window; most accurate, more memory.
class SlidingWindowLogLimiter extends PerKeyLimiter {
    private final int limit;
    private final long windowMs;
    private final Map<String, Deque<Long>> log = new ConcurrentHashMap<>();

    SlidingWindowLogLimiter(int limit, double windowSec) {
        this.limit = limit;
        this.windowMs = (long) (windowSec * 1000);
    }

    public boolean allow(String key) {
        ReentrantLock lock = lockFor(key);
        lock.lock();
        try {
            long now = System.currentTimeMillis();
            Deque<Long> times = log.computeIfAbsent(key, k -> new ArrayDeque<>());
            while (!times.isEmpty() && now - times.peekFirst() >= windowMs) {
                times.pollFirst();                         // evict old timestamps
            }
            if (times.size() < limit) {
                times.addLast(now);
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }
}

class RateLimiter {
    private final RateLimitStrategy strategy;              // DIP - swap algorithm freely
    RateLimiter(RateLimitStrategy strategy) { this.strategy = strategy; }
    boolean isAllowed(String key) { return strategy.allow(key); }
}

public class RateLimiterDemo {
    public static void main(String[] args) throws InterruptedException {
        // 3 requests per 1 second, per user
        RateLimiter rl = new RateLimiter(new FixedWindowLimiter(3, 1.0));
        List<Boolean> results = new ArrayList<>();
        for (int i = 0; i < 5; i++) results.add(rl.isAllowed("user1"));
        System.out.println(results);                       // [true, true, true, false, false]

        // concurrent hammering should still respect the limit (no race past the cap)
        RateLimiter rl2 = new RateLimiter(new TokenBucketLimiter(5, 1.0));
        AtomicInteger allowed = new AtomicInteger(0);
        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < 20; i++) {
            Thread t = new Thread(() -> { if (rl2.isAllowed("user2")) allowed.incrementAndGet(); });
            threads.add(t);
            t.start();
        }
        for (Thread t : threads) t.join();
        System.out.println("allowed under burst: " + allowed.get()); // ~5 (capacity), never more
    }
}
// Expected output:
// [true, true, true, false, false]
// allowed under burst: 5
```

**Talking points:** three algorithms behind one `RateLimitStrategy` interface (Strategy +
DIP); each per-key state guarded by a **per-key lock** so different users never block each
other.

### Key design trade-offs

Algorithm choice (the heart of this problem):

| Algorithm | Accuracy | Memory | Burst behavior | Use when |
|---|---|---|---|---|
| **Fixed Window** | Loose | O(1) per key | Allows 2× burst at window edges (bug-prone) | Simplest need, rough limiting |
| **Sliding Window Log** | Exact | O(requests in window) per key | None - precise | Accuracy matters, volume is low |
| **Sliding Window Counter** | Near-exact | O(1) per key | Smooths edges, approximate | Good accuracy/memory balance (common prod pick) |
| **Token Bucket** | Rate + burst | O(1) per key | **Allows controlled bursts** up to capacity | APIs that should tolerate short spikes (usual default) |
| **Leaky Bucket** | Smooths output | O(queue) | None - constant drain rate | Traffic shaping, steady downstream |

Other decisions:

- **Per-key lock vs one global lock.** Per-key lets different users proceed in parallel (the
  point of a rate limiter); a global lock would serialize every request and become the
  bottleneck. Cost is a lock per key and memory you must eventually evict.
- **In-memory vs distributed.** In-memory is correct only for a single instance; behind a load
  balancer each node limits independently (effectively N× the limit). *Extension to mention:*
  move state to Redis with atomic `INCR`/Lua scripts for a shared counter - out of LLD scope
  but shows system-design awareness.
- **Eviction.** Unbounded per-key state is a memory leak; real implementations expire idle keys
  (TTL / LRU). Worth flagging even if you don't code it.

---

# How to drill these

1. Cover the solution. Do steps 1–3 (clarify → nouns → relationships) **on paper** in 5 min.
2. Code the classes without looking. Run the demo. Does it print the expected output?
3. Diff against the reference. Where did you miss a relationship or an abstraction?
4. **Break it**: add a requirement and check nothing existing changes -
   - Parking Lot: add electric-vehicle charging spots, or a "nearest to exit" strategy
   - BookMyShow: add group discounts, or per-seat pricing (premium rows)
   - Rate Limiter: add a new algorithm (leaky bucket) - should be one new class, zero edits
5. If adding the requirement forces you to edit existing classes, your OCP is weak - refactor.

> Next problems to attempt the same way (increasing difficulty): Vending Machine (State),
> Elevator (State + scheduling), Splitwise (aggregation + balance graph), Logging Framework
> (Chain of Responsibility), In-memory Key-Value store with TTL (concurrency).

## Related

- An **Elevator System** reference implementation lives in the
  [Low-Level Design Guide](LowLevelDesign.md) - a good next problem to attempt.
- Thread-safety details behind the BookMyShow / Rate Limiter locking → [Concurrency](concurrency.md)
- Pattern choices justified → [Roadmap → Design Patterns](roadmap.md#6-design-patterns) ·
  [Extended Patterns](patterns-extended.md)
- Java versions of these demos → [Java Cheat Sheet](java-cheatsheet.md)
