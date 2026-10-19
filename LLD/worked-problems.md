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

Python for the full code (runnable); key Java idioms noted inline ([Java Cheat Sheet](java-cheatsheet.md)).
Each follows the 7-step framework from the [overview](lld-overview.md#delivery-framework-7-steps-for-every-round).

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

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import itertools


class VehicleSize(Enum):
    SMALL = 1      # bike
    MEDIUM = 2     # car
    LARGE = 3      # truck


# --- Vehicle hierarchy (abstraction + inheritance) ---
class Vehicle(ABC):
    def __init__(self, plate: str, size: VehicleSize):
        self.plate = plate
        self.size = size

class Bike(Vehicle):
    def __init__(self, plate): super().__init__(plate, VehicleSize.SMALL)
class Car(Vehicle):
    def __init__(self, plate): super().__init__(plate, VehicleSize.MEDIUM)
class Truck(Vehicle):
    def __init__(self, plate): super().__init__(plate, VehicleSize.LARGE)


# --- Factory (creational) - callers don't new-up concrete classes ---
class VehicleFactory:
    _registry = {"bike": Bike, "car": Car, "truck": Truck}
    @staticmethod
    def create(kind: str, plate: str) -> Vehicle:
        return VehicleFactory._registry[kind](plate)


class ParkingSpot:
    def __init__(self, spot_id: str, size: VehicleSize):
        self.spot_id = spot_id
        self.size = size
        self.vehicle: Vehicle | None = None

    def is_free(self) -> bool:
        return self.vehicle is None

    def can_fit(self, v: Vehicle) -> bool:
        return self.is_free() and v.size.value <= self.size.value

    def park(self, v: Vehicle): self.vehicle = v
    def vacate(self):           self.vehicle = None


class Level:
    def __init__(self, level_id: int, spots: list[ParkingSpot]):
        self.level_id = level_id
        self.spots = spots                     # composition - created/owned here

    def available_spots(self, v: Vehicle) -> list[ParkingSpot]:
        return [s for s in self.spots if s.can_fit(v)]


# --- Strategy (behavioral) - how to pick a spot, swappable ---
class SpotAllocationStrategy(ABC):
    @abstractmethod
    def allocate(self, levels: list[Level], v: Vehicle) -> ParkingSpot | None: ...

class FirstAvailableStrategy(SpotAllocationStrategy):
    def allocate(self, levels, v):
        for level in levels:
            fits = level.available_spots(v)
            if fits:
                return fits[0]
        return None

class BestFitStrategy(SpotAllocationStrategy):
    """smallest spot that fits -> less wasted space"""
    def allocate(self, levels, v):
        candidates = [s for lvl in levels for s in lvl.available_spots(v)]
        return min(candidates, key=lambda s: s.size.value) if candidates else None


class Ticket:
    _ids = itertools.count(1)
    def __init__(self, spot: ParkingSpot, vehicle: Vehicle):
        self.ticket_id = next(Ticket._ids)
        self.spot = spot
        self.vehicle = vehicle
        self.entry_time = datetime.now()


class ParkingLot:
    def __init__(self, levels: list[Level], strategy: SpotAllocationStrategy):
        self.levels = levels                   # composition
        self.strategy = strategy               # aggregation (injected) - DIP
        self.active: dict[str, Ticket] = {}     # plate -> ticket

    def park(self, v: Vehicle) -> Ticket | None:
        spot = self.strategy.allocate(self.levels, v)
        if spot is None:
            return None                        # lot full for this size
        spot.park(v)
        ticket = Ticket(spot, v)
        self.active[v.plate] = ticket
        return ticket

    def unpark(self, plate: str) -> float:
        ticket = self.active.pop(plate)
        ticket.spot.vacate()
        hours = max(1, (datetime.now() - ticket.entry_time).seconds // 3600 + 1)
        return hours * 50.0                    # flat ₹50/hr


# --- demo (your "working demo") ---
if __name__ == "__main__":
    spots_l0 = [ParkingSpot("L0-1", VehicleSize.SMALL),
                ParkingSpot("L0-2", VehicleSize.MEDIUM),
                ParkingSpot("L0-3", VehicleSize.LARGE)]
    lot = ParkingLot([Level(0, spots_l0)], BestFitStrategy())

    car = VehicleFactory.create("car", "KA01AB1234")
    t = lot.park(car)
    print("parked at", t.spot.spot_id)         # parked at L0-2 (best fit for a car)
    print("fee:", lot.unpark("KA01AB1234"))     # fee: 50.0
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

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
import threading, itertools


class SeatStatus(Enum):
    FREE = "FREE"
    HELD = "HELD"
    BOOKED = "BOOKED"


class Seat:
    def __init__(self, label: str):
        self.label = label
        self.status = SeatStatus.FREE


# --- Payment behind an abstraction (DIP + Strategy) ---
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool: ...

class UpiGateway(PaymentGateway):
    def pay(self, amount): return True        # pretend it talks to UPI


class Show:
    def __init__(self, show_id: str, seats: list[Seat], price: float):
        self.show_id = show_id
        self.seats = {s.label: s for s in seats}
        self.price = price
        # fine-grained locking: one lock per seat so different seats don't block each other
        self._locks = {s.label: threading.Lock() for s in seats}

    def hold(self, label: str) -> bool:
        with self._locks[label]:              # critical section - prevents double booking
            seat = self.seats[label]
            if seat.status == SeatStatus.FREE:
                seat.status = SeatStatus.HELD
                # auto-release the hold after 5 min if not confirmed
                threading.Timer(300, self._release_if_held, args=[label]).start()
                return True
            return False

    def confirm(self, label: str) -> bool:
        with self._locks[label]:
            seat = self.seats[label]
            if seat.status == SeatStatus.HELD:
                seat.status = SeatStatus.BOOKED
                return True
            return False

    def _release_if_held(self, label: str):
        with self._locks[label]:
            if self.seats[label].status == SeatStatus.HELD:
                self.seats[label].status = SeatStatus.FREE


class Booking:
    _ids = itertools.count(1)
    def __init__(self, user: str, show: Show, seat_labels: list[str]):
        self.booking_id = next(Booking._ids)
        self.user = user
        self.show = show
        self.seat_labels = seat_labels
        self.confirmed = False

    def checkout(self, gateway: PaymentGateway) -> bool:
        # 1) hold all requested seats atomically-ish (per-seat locks)
        held = []
        for label in self.seat_labels:
            if self.show.hold(label):
                held.append(label)
            else:
                # couldn't get one seat -> roll back the holds we grabbed
                for h in held:
                    self.show._release_if_held(h)
                return False
        # 2) pay
        amount = self.show.price * len(self.seat_labels)
        if not gateway.pay(amount):
            for h in held:
                self.show._release_if_held(h)
            return False
        # 3) confirm
        for label in held:
            self.show.confirm(label)
        self.confirmed = True
        return True


if __name__ == "__main__":
    seats = [Seat(f"A{i}") for i in range(1, 6)]
    show = Show("SHOW1", seats, price=250.0)

    b1 = Booking("ravi", show, ["A1", "A2"])
    print("b1:", b1.checkout(UpiGateway()))        # b1: True

    # second user tries the SAME seat -> must fail (no double booking)
    b2 = Booking("asha", show, ["A2"])
    print("b2:", b2.checkout(UpiGateway()))        # b2: False
    print("A2 status:", show.seats["A2"].status)   # A2 status: SeatStatus.BOOKED
```

**Talking points:** seat lifecycle is a `State` (FREE→HELD→BOOKED) enforced in `Show`;
double-booking solved by a **per-seat lock** guarding check-then-act; multi-seat booking
rolls back partial holds (atomicity); payment is behind `PaymentGateway` so UPI/card/wallet
are swappable; the 5-min hold uses a timer (in Java: `ScheduledExecutorService`).

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

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import threading, time


class RateLimitStrategy(ABC):
    @abstractmethod
    def allow(self, key: str) -> bool: ...


class FixedWindowLimiter(RateLimitStrategy):
    """N requests per fixed window (simple; bursty at window edges)."""
    def __init__(self, limit: int, window_sec: float):
        self.limit = limit
        self.window = window_sec
        self._state: dict[str, list] = defaultdict(lambda: [0, 0.0])  # key -> [count, win_start]
        self._locks: dict[str, threading.Lock] = defaultdict(threading.Lock)

    def allow(self, key: str) -> bool:
        with self._locks[key]:                     # guard check-then-act per key
            count, start = self._state[key]
            now = time.time()
            if now - start >= self.window:          # new window -> reset
                self._state[key] = [1, now]
                return True
            if count < self.limit:
                self._state[key][0] += 1
                return True
            return False


class TokenBucketLimiter(RateLimitStrategy):
    """Refills tokens at a steady rate; allows controlled bursts up to capacity."""
    def __init__(self, capacity: int, refill_per_sec: float):
        self.capacity = capacity
        self.refill = refill_per_sec
        self._state: dict[str, list] = defaultdict(lambda: [0.0, 0.0])  # key -> [tokens, last_ts]
        self._locks: dict[str, threading.Lock] = defaultdict(threading.Lock)

    def allow(self, key: str) -> bool:
        with self._locks[key]:
            tokens, last = self._state[key]
            now = time.time()
            if last == 0.0:
                tokens, last = self.capacity, now    # first hit -> full bucket
            # refill based on elapsed time, capped at capacity
            tokens = min(self.capacity, tokens + (now - last) * self.refill)
            if tokens >= 1:
                self._state[key] = [tokens - 1, now]
                return True
            self._state[key] = [tokens, now]
            return False


class SlidingWindowLogLimiter(RateLimitStrategy):
    """Exact: keep timestamps in the last window; most accurate, more memory."""
    def __init__(self, limit: int, window_sec: float):
        self.limit = limit
        self.window = window_sec
        self._log: dict[str, deque] = defaultdict(deque)
        self._locks: dict[str, threading.Lock] = defaultdict(threading.Lock)

    def allow(self, key: str) -> bool:
        with self._locks[key]:
            now = time.time()
            log = self._log[key]
            while log and now - log[0] >= self.window:   # evict old timestamps
                log.popleft()
            if len(log) < self.limit:
                log.append(now)
                return True
            return False


class RateLimiter:
    def __init__(self, strategy: RateLimitStrategy):
        self.strategy = strategy                   # DIP - swap algorithm freely

    def is_allowed(self, key: str) -> bool:
        return self.strategy.allow(key)


if __name__ == "__main__":
    # 3 requests per 1 second, per user
    rl = RateLimiter(FixedWindowLimiter(limit=3, window_sec=1.0))
    results = [rl.is_allowed("user1") for _ in range(5)]
    print(results)                                 # [True, True, True, False, False]

    # concurrent hammering should still respect the limit (no race past the cap)
    rl2 = RateLimiter(TokenBucketLimiter(capacity=5, refill_per_sec=1.0))
    allowed = 0
    lock = threading.Lock()
    def worker():
        global allowed
        if rl2.is_allowed("user2"):
            with lock: allowed += 1
    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads: t.start()
    for t in threads: t.join()
    print("allowed under burst:", allowed)         # ~5 (capacity), never more
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
