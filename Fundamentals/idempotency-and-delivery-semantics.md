# 🔁 Idempotency & Delivery Semantics

!!! tip "Explain in 2 min"
    In a distributed system, networks fail and clients retry — so the same
    request or message can arrive more than once. **Idempotency** means processing it twice has the
    same effect as processing it once (no double charge, no duplicate order). You get it with an
    **idempotency key**: the client sends a unique token, the server records it, and a retry with the
    same token is recognized and deduped. Message systems describe this as **delivery semantics**:
    *at-most-once* (may drop), *at-least-once* (may duplicate — the common default), and *exactly-once*
    (hard; usually faked with at-least-once + idempotent processing). The practical rule: assume
    at-least-once and make your consumers idempotent.

---

## 🔑 Idempotency `[core]`

An operation is **idempotent** if applying it multiple times equals applying it once.
- Naturally idempotent: `SET balance = 100`, `DELETE user 5`, HTTP `GET`/`PUT`/`DELETE`.
- Not idempotent: `balance = balance + 10`, "create a new order", HTTP `POST`.

**Idempotency key pattern** (how you make a non-idempotent operation safe to retry):

```text
FUNCTION handle(request):
    key = request.idempotency_key
    IF store.contains(key):
        RETURN store.get(key)        # replay the prior result, don't re-execute
    result = doWork(request)          # the real, non-idempotent action
    store.put(key, result)            # remember it (with a TTL)
    RETURN result
```

The client generates the key (e.g. a UUID per logical operation) and reuses it on retries. Stripe's
payment API is the canonical example — retrying a charge with the same key never double-charges.

---

## 📮 Delivery semantics `[core]`

| Semantic | Guarantee | Failure mode | Needs |
|----------|-----------|--------------|-------|
| **At-most-once** | never re-delivered | may **lose** messages | fire-and-forget, no retry |
| **At-least-once** ⭐ | never lost | may **duplicate** | retries + idempotent consumer |
| **Exactly-once** | once, no loss/dup | hard/expensive | idempotency + transactional commit |

**At-least-once is the practical default** for queues (Kafka, SQS): the producer/consumer retries on
uncertainty, so a message can arrive twice — which is fine *if the consumer is idempotent*.

The ordering trap that causes each:
```text
At-most-once:  commit offset  →  then process   (crash after commit = lost)
At-least-once: process        →  then commit     (crash after process = reprocessed)
```

---

## 🎯 "Exactly-once" — what it really means `[advanced]`

True end-to-end exactly-once across arbitrary systems is generally impossible; what people call
exactly-once is **at-least-once delivery + idempotent (or transactional) processing** so duplicates
have no visible effect:
- **Dedup by key:** consumer tracks processed message IDs and skips repeats.
- **Transactional/atomic commit:** process the message and commit the consumer offset in one atomic
  step (Kafka transactions), so a crash-replay doesn't double-apply.
Be honest in interviews: "exactly-once *effects*, achieved via at-least-once + idempotency."

---

## 🛠️ Making consumers idempotent `[core]`

- **Dedup table / set** of processed IDs (with TTL) — skip if seen.
- **Upsert instead of insert** — writing the same row twice is a no-op.
- **Conditional writes** — apply only if a version/state matches (optimistic concurrency, see
  [concurrency-and-parallelism.md](concurrency-and-parallelism.md)).
- **Natural idempotency** — design operations as "set to state X" rather than "increment".

---

## ⚠️ Common interview traps

- Claiming a queue gives exactly-once out of the box — it's at-least-once; you add idempotency.
- Forgetting that `POST`/increment aren't idempotent, so blind retries double-apply.
- Storing idempotency keys forever — use a TTL; keys are only needed during the retry window.
- Ignoring ordering of process-vs-commit, which is exactly what turns into loss or duplication.

## 🔗 Related

- Q&A drills: [qa-concurrency.md](../QA-Bank/qa-concurrency.md) · [qa-system-design-concepts.md](../QA-Bank/qa-system-design-concepts.md)
- Optimistic concurrency (conditional writes) → [concurrency-and-parallelism.md](concurrency-and-parallelism.md)
- Queues & delivery in practice → [distributed-message-queue.md](../SystemDesign/designs/distributed-message-queue.md)
- Notification retries/dedup → [notification-system.md](../SystemDesign/designs/notification-system.md)
