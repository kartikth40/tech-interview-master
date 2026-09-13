# ❓ OOP & Design - Q&A

> Pairs with [Fundamentals/oop-and-language-concepts.md](../Fundamentals/oop-and-language-concepts.md)
> and [SystemDesign/LowLevelDesign.md](../SystemDesign/LowLevelDesign.md). Format and tag legend:
> [QA-Bank/README.md](README.md).

---

> **Q1. What are the four pillars of OOP?**
> Encapsulation (bundle data + behavior, hide internals), abstraction (expose what, hide how),
> inheritance (subclass reuses/extends a parent), polymorphism (one interface, many implementations).
> Polymorphism is what lets you add new types without touching callers.
> *Follow-ups:* Give a concrete polymorphism example. (`shape.area()` dispatching per type.)
> `Easy` · `MAANG`

> **Q2. Explain SOLID quickly.**
> Single Responsibility (one reason to change), Open/Closed (extend without modifying), Liskov
> Substitution (subtypes usable as the base), Interface Segregation (small focused interfaces),
> Dependency Inversion (depend on abstractions). See [LowLevelDesign.md](../SystemDesign/LowLevelDesign.md).
> *Follow-ups:* Give an example of a Liskov violation.
> `Med` · `MAANG`

> **Q3. Composition vs inheritance - which do you favor and why?**
> Favor composition ("has-a") over inheritance ("is-a"). Deep inheritance hierarchies are rigid and
> hit the fragile-base-class problem; composition builds behavior from swappable pieces, which is
> more flexible and testable. Use inheritance only for a true, stable "is-a" with substitutability.
> *Follow-ups:* When is inheritance the right call?
> `Med` · `MAANG`

> **Q4. Interface vs abstract class?**
> An interface is a pure contract (method signatures, no state) that unrelated types can implement,
> and a class can implement many. An abstract class can hold shared implementation and state but is
> usually single-inheritance. Interface for a capability across types; abstract class for shared code
> among relatives.
> *Follow-ups:* Why can a class implement many interfaces but extend one class?
> `Med` · `MAANG`

> **Q5. What is polymorphism at runtime vs compile time?**
> Runtime (dynamic dispatch): the actual method is chosen by the object's type at runtime
> (overriding). Compile time (static): resolved by signature at compile time (overloading, generics).
> Runtime polymorphism is what enables the Open/Closed principle.
> *Follow-ups:* How does this relate to virtual methods / vtables?
> `Hard` · `Google`

> **Q6. What does encapsulation buy you?**
> It hides internal representation behind a controlled interface, so you can validate changes, keep
> invariants, and change internals without breaking callers. It's the basis for maintainable,
> loosely-coupled code.
> *Follow-ups:* Why are public mutable fields a smell?
> `Easy` · `MAANG`

> **Q7. What is immutability and why is it useful?**
> An immutable object can't change after creation. Benefits: thread-safe by default (no write races),
> safe to share/cache, usable as map/set keys, easier to reason about. Cost: creating modified copies
> instead of mutating in place.
> *Follow-ups:* Why are immutable objects inherently thread-safe?
> `Med` · `MAANG`

> **Q8. Value vs reference semantics?**
> Value: the variable holds the data and assignment copies it (mutations don't affect the original).
> Reference: the variable holds a pointer and assignment shares the object (mutations are visible
> through all references). Sharing mutable references is a common bug source.
> *Follow-ups:* Is Python pass-by-value or reference? (pass-by-object-reference.)
> `Med` · `MAANG`

> **Q9. What is the Strategy pattern and when do you use it?**
> Encapsulate interchangeable algorithms behind a common interface and inject the one you want at
> runtime. Use it to swap behavior (sort order, pricing rule, payment method) without conditionals -
> a composition-based alternative to subclassing.
> *Follow-ups:* How does it support Open/Closed?
> `Med` · `Amazon`

> **Q10. Factory pattern - what problem does it solve?**
> It centralizes object creation so callers depend on an interface rather than concrete classes,
> making it easy to change what gets instantiated. Useful when construction is complex or the concrete
> type depends on config/input.
> *Follow-ups:* Factory method vs abstract factory?
> `Med` · `MAANG`

> **Q11. What is the Observer pattern?**
> Subjects maintain a list of observers and notify them on state change - decoupling the source from
> its listeners. It underlies event systems, pub/sub, and UI data binding.
> *Follow-ups:* How does this relate to pub/sub in distributed systems?
> `Med` · `Meta`

> **Q12. What is the Singleton pattern and why is it controversial?**
> Ensures a class has one instance with a global access point (config, connection pool). It's
> criticized for hidden global state, tight coupling, and testability problems - dependency injection
> is often preferred.
> *Follow-ups:* How do you make a singleton thread-safe?
> `Med` · `MAANG`

> **Q13. How do you approach a low-level design question?**
> Clarify requirements and scope, identify the core entities/nouns, define their responsibilities and
> relationships, apply SOLID, choose patterns where they fit, then walk an example flow. See the LLD
> framework in [LowLevelDesign.md](../SystemDesign/LowLevelDesign.md).
> *Follow-ups:* How do you avoid over-engineering with patterns?
> `Hard` · `Amazon`

> **Q14. Coupling vs cohesion?**
> Coupling is how dependent modules are on each other (want it low); cohesion is how focused a module
> is on a single purpose (want it high). Good design is high cohesion + low coupling - easier to
> change and test.
> *Follow-ups:* How does dependency inversion reduce coupling?
> `Med` · `Google`

> **Q15. What is dependency injection and why use it?**
> Passing a component's dependencies in from outside rather than constructing them internally. It
> decouples classes from concrete implementations, makes testing easy (inject mocks), and supports
> the Dependency Inversion principle.
> *Follow-ups:* Constructor vs setter injection?
> `Med` · `MAANG`

> **Q16. How do you handle errors - exceptions vs error values?**
> Exceptions separate the happy path from error handling (catch specific ones, don't swallow, clean
> up with finally/context managers). Error values (Go/Rust) are explicit with no hidden control flow
> but more verbose. Principles: fail fast, handle at the right level, distinguish bugs from
> recoverable errors.
> *Follow-ups:* Why is catching a broad exception and ignoring it dangerous?
> `Med` · `MAANG`

> **Q17. What are generics and why do they matter?**
> Type-safe parameterization over types (`List<T>`) so you avoid duplicating logic per type or losing
> safety with `Object`/`Any`. They catch type errors early and document intent. Python uses type
> hints + `TypeVar` for the same readability benefit.
> *Follow-ups:* What's type erasure? (Java drops generic types at runtime.)
> `Hard` · `Google`

---

**Related:** [Fundamentals/oop-and-language-concepts.md](../Fundamentals/oop-and-language-concepts.md) ·
[SystemDesign/LowLevelDesign.md](../SystemDesign/LowLevelDesign.md) ·
[qa-language-python.md](qa-language-python.md)
