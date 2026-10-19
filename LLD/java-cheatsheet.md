---
title: Java for LLD - Cheat Sheet
description: The Java you actually need in an LLD round - classes, access modifiers, static/final, interface vs abstract class, collections, enums, generics, exceptions, Optional, records, lambdas, streams, equals/hashCode - mapped from Python.
---

# Java for LLD - Cheat Sheet

Most LLD interviews are conducted in Java. This page is the Java you actually need in an LLD
round - the constructs that come up every time - mapped from Python, which the rest of this
section and the [DSA code library](../DSA/code-library/patterns.md) use. Not a full Java tutorial;
just the LLD-relevant 20%.

## Mental model: Python → Java

| Python | Java | Note |
|---|---|---|
| duck typing | static types everywhere | you must declare types |
| `self` | `this` | and `this` is optional unless disambiguating |
| `__init__` | constructor `ClassName(...)` | no return type; can overload |
| `def f(self):` | `ReturnType f() { }` | must declare return type |
| `_x` / `__x` | `private x` | Java enforces it |
| `list` / `dict` / `set` | `List` / `Map` / `Set` (interfaces) | program to the interface |
| `None` | `null` (prefer `Optional`) | |
| `ABC` + `@abstractmethod` | `interface` / `abstract class` | two distinct constructs |
| raise | `throw` | checked vs unchecked (see below) |
| `@dataclass` | `record` (Java 16+) | immutable value type |
| f-string | `String.format` / `"a" + b` / text blocks | |

---

## Class skeleton

```java
public class Account {
    private final String id;          // final = set once (immutable field)
    private double balance;           // mutable field

    public Account(String id, double balance) {   // constructor
        this.id = id;
        this.balance = balance;
    }

    public void deposit(double amount) {           // method: void = returns nothing
        if (amount <= 0) throw new IllegalArgumentException("positive only");
        this.balance += amount;
    }

    public double getBalance() { return balance; }  // getter (encapsulation)
    public String getId()      { return id; }
}
```

- `public` / `private` / `protected` control visibility (default = package-private).
- `this.x = x` resolves the field-vs-parameter name clash.

---

## Access modifiers

| Modifier | Visible from |
|---|---|
| `public` | everywhere |
| `protected` | same package + subclasses |
| *(none)* | same package only (package-private) |
| `private` | same class only |

LLD default: fields `private`, methods `public` if they're the API, `private` if helpers.

---

## `static` and `final`

```java
public class IdGen {
    public static final int MAX = 1000;     // static final = shared constant (CONVENTION: UPPER)
    private static int counter = 0;         // shared across all instances

    public static int next() {              // call as IdGen.next() - no object needed
        return ++counter;
    }
}
```

- `static` → belongs to the class, not an instance (constants, counters, factories, utils).
- `final` on a **variable** → can't reassign; on a **method** → can't override; on a **class**
  → can't extend.

---

## Interface vs abstract class (the LLD workhorses)

```java
// INTERFACE - a capability/contract. A class can implement MANY.
public interface PaymentGateway {
    boolean pay(double amount);                       // abstract by default
    default boolean refundSupported() { return false; }  // Java 8+ default method (has a body)
    static PaymentGateway noop() { return amt -> true; } // static factory on interface
}

// ABSTRACT CLASS - shared state + partial behavior. A class extends ONE.
public abstract class Vehicle {
    protected final String plate;         // shared state
    protected Vehicle(String plate) { this.plate = plate; }
    public String honk() { return "beep"; }   // concrete shared behavior
    public abstract String spotSize();         // subclasses MUST implement
}

public class Car extends Vehicle implements PaymentGateway {   // extends one, implements many
    public Car(String plate) { super(plate); }
    public String spotSize() { return "MEDIUM"; }
    public boolean pay(double amount) { return true; }
}
```

- `implements` for interfaces, `extends` for classes.
- `super(...)` calls the parent constructor; `super.method()` calls the parent's version.
- `@Override` on overriding methods - the compiler verifies you actually override something.

---

## Collections (program to the interface)

```java
import java.util.*;

List<String> names = new ArrayList<>();        // declare as List, instantiate ArrayList
names.add("a"); names.get(0); names.size();

Map<String, Integer> ages = new HashMap<>();
ages.put("ravi", 30); ages.get("ravi"); ages.getOrDefault("x", 0);
ages.containsKey("ravi");

Set<Integer> seen = new HashSet<>();
seen.add(1); seen.contains(1);

Deque<Integer> stack = new ArrayDeque<>();     // use as stack or queue
stack.push(1); stack.pop(); stack.peek();

Queue<Integer> q = new LinkedList<>();
q.offer(1); q.poll(); q.peek();

// iterate
for (String n : names) { ... }
for (Map.Entry<String,Integer> e : ages.entrySet()) { e.getKey(); e.getValue(); }
```

Concurrent variants for thread-safe LLD: `ConcurrentHashMap`, `CopyOnWriteArrayList`,
`ConcurrentLinkedQueue`, `BlockingQueue`.

---

## Enums (use them for states & fixed sets)

```java
public enum SeatStatus { FREE, HELD, BOOKED }

// enums can have fields + methods - great for state machines & pricing tiers
public enum VehicleType {
    CAR(2), BIKE(1), TRUCK(4);
    private final int spotsNeeded;
    VehicleType(int n) { this.spotsNeeded = n; }
    public int getSpotsNeeded() { return spotsNeeded; }
}

SeatStatus s = SeatStatus.FREE;
switch (s) {
    case FREE  -> System.out.println("open");
    case BOOKED -> System.out.println("taken");
    default -> {}
}
```

Enums are the idiomatic way to model a fixed set of states/types in Java LLD - cleaner than
string constants.

---

## Generics (type-safe containers & methods)

```java
// generic class
public class Box<T> {
    private T value;
    public void set(T v) { this.value = v; }
    public T get() { return value; }
}
Box<String> b = new Box<>();    // T = String

// generic method
public static <T> T firstOrNull(List<T> list) {
    return list.isEmpty() ? null : list.get(0);
}

// bounded type - T must be Comparable
public static <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;
}

// wildcards
List<? extends Number> nums;    // read-only "some subtype of Number"
List<? super Integer> sink;     // write Integers into it
```

Comes up in a generic `Repository<T>`, a `Cache<K,V>`, or an event bus.

---

## Exceptions

```java
// custom exception hierarchy (good LLD signal)
public class BookingException extends RuntimeException {   // unchecked (RuntimeException)
    public BookingException(String msg) { super(msg); }
}
public class SeatUnavailableException extends BookingException {
    public SeatUnavailableException(String seat) { super("seat taken: " + seat); }
}

void book(String seat) {
    if (taken(seat)) throw new SeatUnavailableException(seat);
}

try {
    book("A1");
} catch (SeatUnavailableException e) {
    System.out.println(e.getMessage());
} finally {
    // always runs (cleanup)
}
```

- **Checked** (extends `Exception`) → must be declared with `throws` or caught. Interviewers
  often prefer **unchecked** (`RuntimeException`) for domain errors to avoid clutter.
- Design a small exception hierarchy per domain; don't throw raw `Exception`.

---

## `Optional` (avoid null)

```java
import java.util.Optional;

Optional<Account> find(String id) {
    return accounts.containsKey(id) ? Optional.of(accounts.get(id)) : Optional.empty();
}

find("x").ifPresent(a -> System.out.println(a.getBalance()));
Account a = find("x").orElseThrow(() -> new BookingException("not found"));
double bal = find("x").map(Account::getBalance).orElse(0.0);
```

Signals "may be absent" in the type system instead of returning `null`.

---

## `record` - immutable value objects (Java 16+)

```java
public record Money(long amountInPaise, String currency) { }   // auto ctor/getters/equals/hashCode/toString
Money m = new Money(50000, "INR");
m.amountInPaise();                 // accessor (no "get" prefix)
```

The Java answer to `@dataclass(frozen=True)`. Perfect for `Money`, `Point`, `SeatId`,
immutable DTOs - and immutable = thread-safe for free.

---

## Lambdas & functional interfaces

```java
Runnable r = () -> System.out.println("run");
Comparator<String> byLen = (a, b) -> a.length() - b.length();
names.sort(byLen);
names.sort(Comparator.comparingInt(String::length));   // method reference

// Strategy via lambda (no concrete class needed)
interface Discount { double apply(double price); }
Discount tenPct = price -> price * 0.9;
```

Any interface with one abstract method (`@FunctionalInterface`) can be a lambda - lets you
implement Strategy/Command inline.

---

## Streams (concise collection processing)

```java
import java.util.stream.*;

List<String> result = names.stream()
    .filter(n -> n.length() > 2)
    .map(String::toUpperCase)
    .sorted()
    .collect(Collectors.toList());

int total = items.stream().mapToInt(Item::getPrice).sum();
Map<Type, List<Item>> byType = items.stream()
    .collect(Collectors.groupingBy(Item::getType));
```

Don't overuse in LLD - readability first - but handy for aggregations.

---

## `equals` / `hashCode` (needed for Map/Set keys)

If you put your object in a `HashSet`/`HashMap` key, override both (or use a `record`, which
does it for you):

```java
@Override public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof SeatId)) return false;
    SeatId other = (SeatId) o;
    return this.row == other.row && this.col == other.col;
}
@Override public int hashCode() { return Objects.hash(row, col); }
```

Rule: equal objects must have equal hashCodes. A `record` handles this automatically.

---

## Minimal runnable program

```java
public class Main {
    public static void main(String[] args) {    // entry point - exact signature
        ParkingLot lot = new ParkingLot(2);
        System.out.println(lot.park(new Car("KA01")));
    }
}
```

Compile/run: `javac Main.java && java Main`. In an in-memory LLD demo, your `main` creates
objects and prints results - that's your "working demo".

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
