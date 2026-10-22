---
title: LLD Overview - What, Why, and How
description: What low-level design interviews actually test, how they differ from DSA and HLD, the two round formats, the scoring rubric, a learning roadmap, and the 7-step delivery framework.
---

# LLD Overview - What, Why, and How

The entry point to the LLD track. This page frames what low-level design rounds are, how they
differ from DSA and HLD, what interviewers score, and the roadmap + framework the rest of this
section builds on.

!!! tip "Where to go next"
    - **Fundamentals in depth** (OOP → SOLID → patterns → UML): [Roadmap](roadmap.md)
    - **Thread-safety** (the SDE-2 gap): [Concurrency](concurrency.md)
    - **More patterns + trade-offs**: [Extended Patterns](patterns-extended.md)
    - **Java syntax for LLD** (mapped from Python): [Java Cheat Sheet](java-cheatsheet.md)
    - **Full solved problems**: [Worked Problems](worked-problems.md)
    - **The visual modeling layer** (flowcharts, decision trees): [LLD Mental Models](lld-mental-models.md)
    - **Canonical code reference** (SOLID + GoF patterns, runnable): [Low-Level Design Guide](LowLevelDesign.md)

---

## Why LLD rounds reject people

LLD rounds reject a lot of candidates - especially freshers / SDE-1 - not because LLD is hard,
but because there is **no single accepted final solution** and most people never prepare for it.
The skill is turning a vague requirement into **classes, objects, relationships, and schemas**.

Framing: asked to "design a parking lot," DSA has a clear optimal endpoint; LLD does not.

---

## LLD vs DSA

Most developers prepare only DSA and assume it's enough. That myth breaks the moment a
machine-coding / LLD round shows up.

| Aspect | DSA | LLD |
|---|---|---|
| Goal | Find an optimized solution (brute force → optimal) the interviewer agrees on, then code it | Turn a **vague requirement** into classes, objects, relationships, schemas |
| Endpoint | Clear final outcome - you know you'll land somewhere | Open-ended - no single "correct" answer |
| Stress | Lower (defined target) | Higher (ambiguous) |

"LLD round" and "machine coding round" are *mostly* the same thing - companies just name it
differently.

---

## LLD vs HLD

**HLD (High-Level Design = System Design)** is the bird's-eye view of an architecture; **LLD** is
the inside view of one component's objects and code.

| | HLD (System Design) | LLD |
|---|---|---|
| Question | "Design Zomato / Rapido" | "Design the restaurant, menu, order, delivery agent" |
| You decide | Components, services, DBs, queues, Kafka; non-functional reqs (scaling, reliability, consistency) | Classes, methods, relationships - who owns what, who talks to whom |
| Output | An agreed **architecture** (no code) | A **class/UML diagram** + **running code** |

For the HLD side, see the [System Design Guide](../SystemDesign/SystemDesignGuide.md).

---

## Why LLD rounds exist (what they test)

The core reason: **can your code survive change?** Interviewers check whether you write code that
is:

- **Extensible** - other engineers can build on it
- **Clean, modular, readable** - follows best practices
- A faithful **model of a real-world system** - can you think in terms of objects?

The real test: **will your design hold when requirements change?**

> A candidate who writes *working* code is fine. A candidate who writes code that others can
> **understand and extend** is the real bar.

---

## What an LLD round consists of

Three questions to settle **before** writing any code:

1. **Which format am I in?** (two formats - see below)
2. **What rubric am I scored on?** (know this → rounds get much easier)
3. **How do I spend the next 60–90 min so I don't get rejected?** (the delivery framework)

Everything else - SOLID, UML, patterns - comes *after* these three.

> Common mistake: jumping straight into "I'll use this design pattern" and getting confused by
> trying to memorize things. That doesn't help.

---

## The two formats

| Format | Companies (examples) | Duration | Deliverable | Constraints |
|---|---|---|---|---|
| **Machine coding** | Flipkart, Uber, Swiggy, Cred, Razorpay, PhonePe, BrowserStack | 90–120 min + discussion | **Running code** / working demo | No internet, **everything in-memory** (in-memory structures abstract the DB) |
| **Whiteboard / verbal OOD** | Amazon, Microsoft, Goldman Sachs | ~45–60 min | Class diagram, key interfaces, pseudo-code | Conversational - expect **interruptions**; correct & reframe |

Machine coding flow: get a problem statement (requirements + assumptions), build a working demo,
then discuss on top of it (where a factory/decorator could fit).

---

## Rubric - how it's scored

**Bare minimum (required) - for any "write code" round:**

1. **Demoable, functionally correct code** - runs, not buggy, prints expected output
2. **Code readability** - the strongest signal; meaningful names, modular code
3. **Proper entity modeling**
4. **Modularity & extensibility** - separation of concerns, abstraction, SOLID
5. **Corner / edge case handling**

**Good to have:** time complexity, optimality, how to optimize further, scalability, cleanliness.

> **Working code is the entry ticket, not the goal.** No working code = already rejected. Working
> code only *gets you to* the round where the other criteria are judged.

(For a *discussion* round, some code-specific criteria drop out - you're writing pseudo-code.)

---

## Learning roadmap (do in this order)

1. **OOP basics** - class, object, constructor, `static`, `final`, overloading vs overriding
2. **Four pillars** - encapsulation, abstraction, inheritance, polymorphism (the *boundaries*,
   not just definitions)
3. **Relationships** - association, aggregation, composition (categorize almost any LLD question)
4. **SOLID** - the foundation of LLD code
5. **Interface vs abstract** - a clear boundary on when to use each
6. **Design patterns** - comes with *practice*, not memorization
7. **UML basics** - class & sequence diagrams
8. **Practice** + **mock interviews**

Each of these is expanded with examples in the **[Roadmap](roadmap.md)**.

> Don't open with "I'll use strategy pattern" with no rationale. Start with **clarification**.

---

## Delivery framework - 7 steps for every round

Run these in order, every time. The first three are design; the last four are code. Spend the
most time on steps 1-3 - a wrong model is expensive to fix later.

| # | Step | What you do | Output |
|---|------|-------------|--------|
| 1 | **Clarify** | Ask before designing - the prompt is vague on purpose | Agreed scope & assumptions |
| 2 | **Nouns → classes** | List nouns, then prune (most are attributes) | The real entities |
| 3 | **Relationships** | Decide who owns whom | association / aggregation / composition |
| 4 | **Write classes** | Fields + methods; interfaces where behavior varies | Skeleton classes |
| 5 | **SOLID & refactor** | Start simple, then tighten responsibilities | Clean, decoupled classes |
| 6 | **Patterns** | Add one only if it removes real pain | A working demo first |
| 7 | **Edge cases** | Handle the failure paths | Robust, demoable code |

**Step 1 - clarifying questions** (the examples interviewers expect you to ask):

- *Parking lot* - can one vehicle take two spots? how many floors?
- *BookMyShow* - is a seat held before or after payment? how do you prevent **double booking**?
- *Splitwise* - currencies other than INR? (internationalization)

**Step 2 - nouns, then prune.** For a movie-booking app the nouns are *user, movie, theater,
screen, seat, booking, payment* - but *ticket price* lives inside `Booking` and *seat number*
inside `Seat`, so those are **attributes**, not classes.

**Steps 5-6 - the discipline that scores.** Start brute-force and get it working, *then* apply
SOLID and reach for a pattern only when you can name the pain it removes. A **finished working
demo beats a half-built "perfect" design** - that's the entry ticket.

For the same flow as a flowchart, see [LLD Mental Models](lld-mental-models.md).

---

## Object relationships (the heart of LLD)

Most interview problems are really about relationships. Spot these three and ~half the LLD is
done. Key question: **"If the whole disappears, does the part still make sense?"**

- **Association** - *they know each other, both live on their own.* Teacher & student; a
  **vehicle & parking spot** (the vehicle exists before and after being parked).
- **Aggregation** - *the whole holds the part, but the part survives alone.* Library & books;
  Splitwise **group & user** (delete the group, users remain); theater & movie.
- **Composition** - *the part dies with the whole (cascade delete).* House & room; BookMyShow
  **screen & seat** (seat "A9" has no meaning alone); parking lot & level.

The full modeling detail, UML arrows, and trade-offs are in the
[Roadmap → Relationships](roadmap.md#3-relationships).

---

## Do's & Don'ts

**Green flags:**

- Clarifying questions that drive class design **first**
- One clear responsibility per class (say it out loud)
- A **rationale** behind every pattern you choose (why Builder and not Factory?)
- **Thinking out loud** - silence = near-certain fail
- A **working demo** at the end

**Red flags:**

- Typing code without discussing
- One big "manager" class / fat interface → tight coupling, no rationale
- Long silences, not asking for hints
- Half-built classes spanning five features - finish **one** before the next

---

## Learn by example - a sentence into classes

Design a movie booking app:

1. **Pick nouns** - user, movie, theater, screen, seat, booking, payment
2. **Link them** - theater contains screen, screen contains seats, user creates booking, booking
   has payment
3. **Ask the edges** - can one user book multiple seats (1→many)? can a booking be cancelled? can
   a seat be held 5 min? what if payment fails? (~20–30% of LLD is this requirement gathering)

Practice on paper for any five apps on your phone (Rapido, Zomato, …). Full solved versions:
[Worked Problems](worked-problems.md).

---

## Takeaways

- **Concurrency / multi-threading** is the hard part - Uber, Walmart, Flipkart focus on it. See
  [Concurrency](concurrency.md).
- LLD is not pretty diagrams - it's **code the next person can read and extend.**
- Follow the 7-step framework. Start simple (library management, BookMyShow), **not** Uber first.
- Practice by **breaking your own design**, then fixing it.

## Related

- [Roadmap](roadmap.md) · [Concurrency](concurrency.md) · [Extended Patterns](patterns-extended.md)
  · [Java Cheat Sheet](java-cheatsheet.md) · [Worked Problems](worked-problems.md)
- [Low-Level Design Guide](LowLevelDesign.md) · [LLD Mental Models](lld-mental-models.md)
- OOP pillars & SOLID in [Fundamentals](../Fundamentals/oop-and-language-concepts.md) · [OOP & Design Q&A](../QA-Bank/qa-oop-design.md)
