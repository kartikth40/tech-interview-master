---
title: Java specifics for LLD rounds
description: The interview-minimal Java you actually use in an LLD round, organized by why each thing matters - the constructs in every answer, the collections you declare, the gotchas that get you dinged, concurrency primitives, and a tiny runnable skeleton.
---

# Java specifics for LLD rounds

Most LLD interviews are conducted in Java. This page is the small slice of Java you actually
use in a round - organized by **why** each thing matters, not as a language tutorial. Learn
just this and you can write a clean LLD answer; skip the rest of the language for now.

!!! note "Coming from Python? Watch out for these"
    | Python habit | Java reality |
    |---|---|
    | duck typing | static types everywhere - you declare every type |
    | `None` | `null` (and prefer `Optional` over returning `null`) |
    | native method overloading by default args | no - you write real overloads or separate methods |
    | indentation defines blocks | `{ }` braces define blocks; `;` ends statements |

---

## 1. Constructs in every LLD answer

These four show up in almost every design. Know them cold.

### Interface vs abstract class

```java
// INTERFACE - a capability/contract. A class can implement MANY.
public interface PaymentGateway {
    boolean pay(double amount);                          // abstract by default
    default boolean refundSupported() { return false; }  // Java 8+ default method (has a body)
}

// ABSTRACT CLASS - shared state + partial behavior. A class extends ONE.
public abstract class Vehicle {
    protected final String plate;             // shared state
    protected Vehicle(String plate) { this.plate = plate; }
    public String honk() { return "beep"; }   // concrete shared behavior
    public abstract String spotSize();        // subclasses MUST implement
}

public class Car extends Vehicle implements PaymentGateway {   // extends ONE, implements MANY
    public Car(String plate) { super(plate); }
    @Override public String spotSize() { return "MEDIUM"; }
    @Override public boolean pay(double amount) { return true; }
}
```

- `implements` for interfaces (many), `extends` for a class (one).
- Interface = "can do X"; abstract class = "is an X with some shared guts".
- `@Override` lets the compiler verify you actually overrode something.

### Enum for fixed states/types

```java
public enum SeatStatus { FREE, HELD, BOOKED }

// enums can carry fields + methods - ideal for state machines & tiers
public enum VehicleType {
    CAR(2), BIKE(1), TRUCK(4);
    private final int spotsNeeded;
    VehicleType(int n) { this.spotsNeeded = n; }
    public int getSpotsNeeded() { return spotsNeeded; }
}
```

Model a fixed set of states/types as an `enum`, never as `String` constants - the compiler
then catches typos and missing cases.

### Constructor injection (and `@Autowired`)

```java
interface Database { void save(String data); }

class OrderService {
    private final Database db;
    OrderService(Database db) {   // constructor injection: dependency is required + final
        this.db = db;
    }
}

new OrderService(new MySQLDatabase());   // swap to a FakeDatabase in tests freely
```

`@Autowired` is the Spring version of the same idea: instead of you calling `new`, the Spring
container creates the `Database` bean and injects it into the constructor, so `OrderService`
never news-up its own dependency. **Constructor** injection is preferred over field injection
because the dependency is required, visible, and can be `final` (immutable), and the class is
easy to build in a plain unit test without a container. This is DIP in practice - see the
[DIP note in the roadmap](roadmap.md).

### Access modifiers

| Modifier | Visible from |
|---|---|
| `public` | everywhere |
| `protected` | same package + subclasses |
| *(none)* | same package only (package-private) |
| `private` | same class only |

LLD default: fields `private`, methods `public` when they're the API, `private` for helpers.
`this.x = x` resolves the field-vs-parameter name clash.

---

## 2. Collections you'll declare

Program to the **interface** (`List`/`Map`/`Set`), instantiate the concrete type.

```java
import java.util.*;

List<String> names = new ArrayList<>();            // declare as List, instantiate ArrayList
Map<String, Integer> ages = new HashMap<>();
Set<Integer> seen = new HashSet<>();

Deque<Integer> stack = new ArrayDeque<>();         // stack: push/pop/peek
Queue<Integer> q = new LinkedList<>();             // queue: offer/poll/peek
Queue<Integer> pq = new PriorityQueue<>();         // heap: smallest out first
```

Pick the shape by need: **Deque** for stack/queue, **Queue/PriorityQueue** when you want
FIFO or priority ordering.

### Map idioms that prevent bugs

```java
ages.getOrDefault("x", 0);                         // read with a default, no null check
ages.putIfAbsent("ravi", 30);                      // only set if missing
counts.merge("a", 1, Integer::sum);                // increment-or-init a counter

// one-liner "group into buckets" without manual null checks
Map<String, List<String>> byCity = new HashMap<>();
byCity.computeIfAbsent("BLR", k -> new ArrayList<>()).add("ravi");
```

### Thread-safe variants

For concurrent LLD, use `ConcurrentHashMap`, `CopyOnWriteArrayList`, or a `BlockingQueue`
instead of the plain versions. Details and when-to-use live in
[Concurrency](concurrency.md) - don't reinvent locking around a plain `HashMap`.

---

## 3. Gotchas that get you dinged

### `equals` + `hashCode` together (for Map/Set keys)

If an object is a `HashSet` element or `HashMap` key, override **both** - or use a `record`,
which generates them for you.

```java
@Override public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof SeatId)) return false;
    SeatId other = (SeatId) o;
    return this.row == other.row && this.col == other.col;
}
@Override public int hashCode() { return Objects.hash(row, col); }
```

Rule: equal objects must have equal hashCodes.

### `==` vs `.equals()`

`==` compares references (same object?); `.equals()` compares value. For objects - especially
`String` - use `.equals()`. `==` is only for primitives and null checks.

### `record` for immutable value objects (Java 16+)

```java
public record Money(long amountInPaise, String currency) { }   // auto ctor/getters/equals/hashCode
Money m = new Money(50000, "INR");
m.amountInPaise();                 // accessor (no "get" prefix)
```

Perfect for `Money`, `Point`, `SeatId`, immutable DTOs - and immutable = thread-safe for free.

### `final` and `Optional`

- `final` field = set once (immutability); `final` method = can't override; `final` class =
  can't extend. Prefer `final` fields for anything that shouldn't change after construction.
- Return `Optional<T>` instead of `null` so "may be absent" shows up in the type:

```java
Optional<Account> find(String id) {
    return Optional.ofNullable(accounts.get(id));
}
Account a = find("x").orElseThrow(() -> new IllegalStateException("not found"));
```

---

## 4. Concurrency primitives (brief)

For thread safety: `synchronized` methods/blocks for simple mutual exclusion, `ReentrantLock`
when you need tryLock/fairness, and `AtomicInteger` for lock-free counters. Keep it minimal in
an interview and reach for `ConcurrentHashMap`/`BlockingQueue` before hand-rolling locks.

Full treatment - locks, semaphores, executors, the producer/consumer pattern - is in
[Concurrency](concurrency.md). Don't duplicate it here; just name the primitive you'd use and
link the detail.

---

## 5. A tiny runnable skeleton

Your "working demo": a `main` that builds objects in memory and prints results.

```java
public class Main {
    public static void main(String[] args) {    // entry point - exact signature
        ParkingLot lot = new ParkingLot(2);
        System.out.println(lot.park(new Car("KA01")));
    }
}
```

Compile/run: `javac Main.java && java Main`.

---

## Streams & lambdas (2-line mention)

A lambda is a one-method implementation inline (`Comparator<String> c = (a, b) -> a.length() -
b.length();`) - handy for Strategy/Command. Streams (`list.stream().filter(...).map(...)`) are
fine for small aggregations but don't let them hurt readability in an LLD answer.

---

## Quick "don't embarrass yourself" list

- Declare collections by interface: `List<X> x = new ArrayList<>();`
- `equals`/`hashCode` together, or use `record`.
- `@Override` whenever you override.
- Fields `private`, expose via methods.
- Model fixed states as `enum`, not `String`.
- Prefer immutability (`final` fields, `record`) - simpler + thread-safe.
- Program to abstractions (`PaymentGateway`, not `RazorpayGateway`) for DIP.

## Related

- Concepts these constructs serve → [Roadmap](roadmap.md)
- Java concurrency primitives in context → [Concurrency](concurrency.md)
- OOP & language fundamentals → [Fundamentals → OOP & Language](../Fundamentals/oop-and-language-concepts.md)
