# ❓ Python Language — Q&A

> Pairs with [Fundamentals/memory-and-runtime.md](../Fundamentals/memory-and-runtime.md) and
> [oop-and-language-concepts.md](../Fundamentals/oop-and-language-concepts.md). Format and tag
> legend: [QA-Bank/README.md](README.md).

---

> **Q1. What is the GIL and what are its implications?**
> The Global Interpreter Lock lets only one thread execute Python bytecode at a time. So threads
> don't speed up CPU-bound work — use `multiprocessing` or native libs for that — but they're fine
> for I/O-bound work since the GIL is released during blocking I/O.
> *Follow-ups:* How does `asyncio` differ from threads for I/O?
> `Med` · `MAANG`

> **Q2. Is Python pass-by-value or pass-by-reference?**
> Neither exactly — it's pass-by-object-reference ("call by sharing"). Rebinding a parameter doesn't
> affect the caller, but mutating a mutable argument (list, dict) does. Immutable args (int, str,
> tuple) appear value-like because you can't mutate them in place.
> *Follow-ups:* Show a bug this causes. (mutating a shared default list.)
> `Med` · `MAANG`

> **Q3. Why is a mutable default argument dangerous?**
> The default is evaluated once at function definition and shared across all calls, so
> `def f(x=[])` accumulates state between calls. Use `def f(x=None)` and create the list inside.
> *Follow-ups:* When is the default expression evaluated? (at definition, not call.)
> `Med` · `MAANG`

> **Q4. Which Python types are mutable vs immutable?**
> Mutable: list, dict, set, most objects. Immutable: int, float, str, tuple, frozenset, bytes. Only
> immutable (hashable) types can be dict keys or set members.
> *Follow-ups:* Why can't a list be a dict key? (unhashable — mutable.)
> `Easy` · `MAANG`

> **Q5. What is a generator and why use one?**
> A function using `yield` that produces values lazily, one at a time, without building the whole
> sequence in memory. Ideal for large or infinite streams and memory-efficient pipelines.
> *Follow-ups:* Difference between a generator and a list comprehension? (lazy vs eager.)
> `Med` · `MAANG`

> **Q6. What is a decorator?**
> A callable that wraps a function to add behavior (logging, caching, auth, timing) without changing
> its body. `@lru_cache` and `@property` are stdlib examples. It's syntactic sugar for
> `f = decorator(f)`.
> *Follow-ups:* How would you write one that times a function?
> `Med` · `MAANG`

> **Q7. What is a context manager?**
> An object usable with `with` that guarantees setup and teardown (via `__enter__`/`__exit__`), even
> on exceptions — closing files, releasing locks, committing/rolling back transactions. The Pythonic
> answer to deterministic resource cleanup.
> *Follow-ups:* How do you write one with `contextlib`?
> `Med` · `MAANG`

> **Q8. How does Python manage memory / garbage collection?**
> Primarily reference counting (objects freed when their count hits zero) plus a generational cycle
> collector to reclaim reference cycles that counting alone can't. Old generations are collected less
> often (most objects die young).
> *Follow-ups:* Why does reference counting alone leak cycles?
> `Hard` · `Google`

> **Q9. `is` vs `==`?**
> `==` compares values (calls `__eq__`); `is` compares identity (same object in memory). Use `is`
> only for singletons like `None`. Small-int and string interning can make `is` deceptively true —
> don't rely on it for value equality.
> *Follow-ups:* Why does `256 is 256` but `257 is 257` may vary? (small-int caching.)
> `Med` · `MAANG`

> **Q10. What's the difference between a list and a tuple?**
> A list is mutable and general-purpose; a tuple is immutable and often used for fixed, heterogeneous
> records or as dict keys. Tuples are slightly more memory-efficient and hashable.
> *Follow-ups:* When would you deliberately choose a tuple? (fixed record, dict key, safety.)
> `Easy` · `MAANG`

> **Q11. What are `*args` and `**kwargs`?**
> `*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword
> arguments into a dict. They let functions accept a variable number of arguments and forward them.
> *Follow-ups:* How do you forward them to another function? (`f(*args, **kwargs)`.)
> `Easy` · `Startups`

> **Q12. How would you speed up CPU-bound Python code?**
> Move the hot work off the GIL: use `multiprocessing`, native/C extensions or NumPy (which release
> the GIL), or a different runtime. Profile first to find the real hotspot rather than guessing.
> *Follow-ups:* Why won't threads help here? (GIL serializes bytecode.)
> `Med` · `MAANG`

> **Q13. What is a shallow copy vs a deep copy?**
> A shallow copy duplicates the container but shares the nested objects; a deep copy recursively
> duplicates everything. Mutating a nested object through a shallow copy affects the original — a
> common bug with lists of lists.
> *Follow-ups:* Which does `list(x)` or `x[:]` give? (shallow.)
> `Med` · `Google`

---

**Related:** [Fundamentals/memory-and-runtime.md](../Fundamentals/memory-and-runtime.md) ·
[qa-concurrency.md](qa-concurrency.md) · [qa-oop-design.md](qa-oop-design.md)
