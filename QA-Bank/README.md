# ❓ Q&A Bank

Short, defensible interview answers — the kind an interviewer would accept in a conceptual round or
as a follow-up. This is **not** a LeetCode problem list (that's
[InterviewPrep/MockInterviewQuestions.md](../InterviewPrep/MockInterviewQuestions.md)); it's the
"explain X / why X vs Y" bank that pairs with the [Fundamentals](../Fundamentals/) concept notes.

## How to use

- **Drill actively:** read the question, answer out loud in 2-5 sentences *before* reading the
  answer. Interviewers grade clarity and trade-off reasoning, not word-for-word recall.
- Each answer is **interview-length** on purpose. For the deeper "why," follow the link to the
  matching Fundamentals note at the top of each file.
- Use the **Follow-ups** under each answer to simulate how a real interviewer pushes deeper.
- **Rapid-fire** ([qa-rapid-fire.md](qa-rapid-fire.md)) is for one-line definitions — warm-up or
  last-minute review.

## Answer format

Every question follows the same shape:

> **Q. The question.**
> Answer first — 2-5 sentences, trade-off framed.
> *Follow-ups:* the natural next probes.
> `Difficulty` · `Companies`

## Legend

**Difficulty:** `Easy` (any SDE-1) · `Med` (standard SDE-1/2) · `Hard` (SDE-2 / senior depth).

**Companies:** directional tags for where a question commonly appears — `MAANG` (broadly across big
tech), or a specific culture cue like `Amazon`, `Meta`, `Google`, `Startups` (Indian unicorns /
fintech). These are *indicative, not guarantees* — no invented frequencies.

## Files

| File | Topic | ~Q | Pairs with |
|------|-------|----|-----------|
| [qa-operating-systems.md](qa-operating-systems.md) | processes, threads, memory, scheduling | 18 | [operating-systems.md](../Fundamentals/operating-systems.md) |
| [qa-concurrency.md](qa-concurrency.md) | locks, races, deadlock, async, GIL | 22 | [concurrency-and-parallelism.md](../Fundamentals/concurrency-and-parallelism.md) |
| [qa-networking.md](qa-networking.md) | TCP/UDP, HTTP, TLS, DNS | 18 | [networking.md](../Fundamentals/networking.md) |
| [qa-databases.md](qa-databases.md) | ACID, isolation, indexing, SQL/NoSQL | 22 | [databases-internals.md](../Fundamentals/databases-internals.md) |
| [qa-hashing.md](qa-hashing.md) | hash tables, consistent hashing, bloom | 12 | [hashing.md](../Fundamentals/hashing.md) |
| [qa-caching.md](qa-caching.md) | strategies, eviction, invalidation | 12 | [caching.md](../SystemDesign/components/caching.md) |
| [qa-security.md](qa-security.md) | authN/authZ, tokens, attacks | 13 | [security-fundamentals.md](../Fundamentals/security-fundamentals.md) |
| [qa-oop-design.md](qa-oop-design.md) | OOP pillars, SOLID, patterns | 17 | [oop-and-language-concepts.md](../Fundamentals/oop-and-language-concepts.md) |
| [qa-system-design-concepts.md](qa-system-design-concepts.md) | CAP, LB, queues, sharding, estimation | 22 | [SystemDesignGuide.md](../SystemDesign/SystemDesignGuide.md) |
| [qa-language-python.md](qa-language-python.md) | GIL, mutability, generators, decorators | 13 | [memory-and-runtime.md](../Fundamentals/memory-and-runtime.md) |
| [qa-rapid-fire.md](qa-rapid-fire.md) | 1-line "define X" drills | 25 | all of the above |

**Target:** ~200 Q&A total across the bank.
