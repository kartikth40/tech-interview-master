# 🧱 OOP & Language Concepts

!!! tip "Explain in 2 min"
    Object-oriented programming organizes code around **objects** that bundle
    data with behavior. The four pillars — **encapsulation, abstraction, inheritance,
    polymorphism** — are about hiding detail and letting one interface serve many types. On top of
    that, **SOLID** gives five principles for keeping OO code changeable. The most repeated practical
    lesson is **"favor composition over inheritance"**: deep inheritance trees are rigid, while
    composing small pieces stays flexible. Language-level, know the difference between **value and
    reference** semantics (what gets copied vs shared), why **immutability** simplifies concurrency,
    and how you handle errors.

---

## The four pillars `[core]`

| Pillar | Idea | Example |
|--------|------|---------|
| **Encapsulation** | bundle data + methods, hide internals behind an interface | private fields with getters/validation |
| **Abstraction** | expose *what*, hide *how* | `list.sort()` — you don't see the algorithm |
| **Inheritance** | a subclass reuses/extends a parent | `Dog extends Animal` |
| **Polymorphism** | one interface, many implementations | `shape.area()` dispatches per type |

Polymorphism is the one interviewers probe: it's what lets you write code against an abstraction
(`Shape`) and add new types (`Triangle`) without touching the caller — the basis of the
Open/Closed principle.

---

## SOLID `[core]`

Five principles for maintainable OO design:
- **S**ingle Responsibility — a class has one reason to change.
- **O**pen/Closed — open for extension, closed for modification.
- **L**iskov Substitution — subtypes must be usable wherever the base type is.
- **I**nterface Segregation — many small interfaces beat one fat one.
- **D**ependency Inversion — depend on abstractions, not concretions.

Full explanations with Python examples and GoF design patterns live in the canonical home:
👉 [SystemDesign/LowLevelDesign.md](../SystemDesign/LowLevelDesign.md). Know them well enough to
name a violation and its fix in an LLD round.

---

## Composition vs inheritance `[core]`

- **Inheritance** ("is-a") — subclass gets the parent's behavior. Tight coupling; deep hierarchies
  are brittle and hit the fragile-base-class problem.
- **Composition** ("has-a") — build behavior by holding other objects and delegating. Flexible,
  swappable, testable.

**Favor composition over inheritance.** Use inheritance only for a genuine, stable "is-a" with
substitutability (Liskov). When you're inheriting just to reuse code, compose instead. This is also
why many designs prefer *interfaces + composition* (strategy pattern) over subclassing.

---

## Interface vs abstract class `[core]`

| | Interface | Abstract class |
|--|-----------|----------------|
| Contains | method signatures (a contract) | signatures + some implementation + state |
| State | none (traditionally) | can have fields |
| Multiple | a class can implement many | usually single inheritance |
| Use when | "these unrelated types can all do X" | "these related types share code + a base" |

Rule of thumb: interface for a capability across unrelated types (`Comparable`, `Iterable`);
abstract class to share common implementation among close relatives. (Python blurs this with ABCs
and mixins; the distinction still matters conceptually.)

---

## Value vs reference semantics `[core]`

- **Value** — the variable holds the data; assignment/passing *copies* it. Mutating the copy
  doesn't affect the original (primitives; structs in some languages).
- **Reference** — the variable holds a pointer; assignment/passing shares the *same* object.
  Mutating through one name is visible through the other (objects, lists, dicts).

This is the source of countless bugs (mutating a shared list a caller still holds). In Python,
everything is an object reference, but *immutable* types (int, str, tuple) behave value-like because
you can't mutate them in place — see [memory-and-runtime.md](memory-and-runtime.md) for the
pass-by-object-reference detail.

---

## Immutability `[core]`

An immutable object can't change after creation. Benefits: **thread-safe by default** (no races on
read-only data — see [concurrency-and-parallelism.md](concurrency-and-parallelism.md)), safe to
share and cache, easier to reason about, usable as dict/set keys. Cost: creating modified copies
instead of mutating. Favor immutability for shared/config/value objects; use mutability where in-place
update genuinely matters for performance.

---

## Generics `[advanced]`

Generics let you write type-safe code parameterized over a type — `List<T>`, `Map<K,V>` — instead of
duplicating logic per type or losing type safety with `Object`/`Any`. They catch type errors at
compile time and document intent. (Python uses type hints + `TypeVar` / `Generic` for the same
readability benefit, checked by tools like mypy rather than at runtime.)

---

## Error handling `[core]`

Two broad styles:
- **Exceptions** — throw/catch; separates the happy path from error handling. Common in Python/Java.
  Catch specific exceptions, don't swallow them, clean up with `finally`/context managers.
- **Error values / results** — return an error alongside the value (Go's `err`, Rust's `Result`).
  Explicit, no hidden control flow, but verbose.

Principles that read well in interviews: **fail fast**, catch at the level that can actually handle
it, never silently swallow, and distinguish *recoverable* errors from *bugs* (don't catch the latter
to hide them).

---

## Common interview traps

- Reciting the four pillars but not being able to give a concrete polymorphism example.
- Reaching for inheritance to reuse code — prefer composition unless it's a true "is-a".
- Not knowing which SOLID principle a given smell violates (name it + the fix).
- Assuming Python is "pass by value" or "pass by reference" — it's pass-by-object-reference;
  mutability decides what the caller sees.
- Catching broad exceptions and swallowing them (hides bugs).

## Related

- Q&A drills: [qa-oop-design.md](../QA-Bank/qa-oop-design.md)
- SOLID + GoF patterns + LLD problems → [SystemDesign/LowLevelDesign.md](../SystemDesign/LowLevelDesign.md)
- Value/reference, GC, Python runtime → [memory-and-runtime.md](memory-and-runtime.md)
- Immutability & thread safety → [concurrency-and-parallelism.md](concurrency-and-parallelism.md)
