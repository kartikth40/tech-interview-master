# Stock Exchange / Matching Engine System Design
> **SDE-2 Interview Ready** | 45-minute format · *advanced / low-frequency*

## 🎯 Problem Statement

Design the core of a stock exchange: accept buy/sell orders, match them fairly, and publish trades
and market data — with correctness and very low latency.

**Example:** a buy order at $100 matches a resting sell order at $100; both parties get a fill, and
the trade is broadcast.

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. Place/cancel orders (market, limit).
2. **Match** orders by price-time priority; execute trades.
3. Maintain the **order book** per symbol.
4. Publish market data (trades, book updates) to clients.

### Non-Functional Requirements:
- **Correctness:** no lost/duplicated orders; deterministic matching (money is at stake).
- **Very low latency:** microseconds-to-millisecond matching.
- **Fairness:** strict price-time priority.
- **Durability + auditability:** every order/trade is recorded (regulatory).

### Out of Scope:
- Clearing/settlement, KYC, brokerage front-end.

---

## 2️⃣ Capacity Estimation

```
Peak ~1M orders/sec across symbols; per-symbol matching is single-threaded for determinism
Latency budget: matching in microseconds → in-memory order book, no DB on the hot path
Durability: append every order to a log (sequencer) before/at matching for replay + audit
```

---

## 3️⃣ Core: The Matching Engine + Order Book

The heart is a **matching engine** holding an in-memory **order book** per symbol:
- **Bids** (buys) sorted by price descending, then time; **asks** (sells) ascending, then time.
- A new order matches against the best opposite price while prices cross, generating trades; any
  remainder rests in the book (limit) or is rejected/partial (market).

```text
FUNCTION match(order):        # per symbol, single-threaded for determinism
    book = orderBook[order.symbol]
    WHILE order.qty > 0 AND crosses(order, book.bestOpposite()):
        resting = book.bestOpposite()
        tradeQty = min(order.qty, resting.qty)
        emitTrade(order, resting, resting.price, tradeQty)   # price-time priority
        order.qty   -= tradeQty
        resting.qty -= tradeQty
        IF resting.qty == 0: book.remove(resting)
    IF order.qty > 0 AND order.type == LIMIT:
        book.add(order)       # rest remainder
```

**Price-time priority:** best price wins; ties broken by earliest arrival. Determinism matters — the
same input sequence must always produce the same trades.

---

## 4️⃣ High-Level Design

```
Clients ─► Order Gateway ─► [ Sequencer / append-only log ] ─► Matching Engine (per symbol)
           (validate,        assigns a global order,             in-memory order book
            auth, risk)      durable + replayable                     │
                                                                       ├─► Trades ─► Market Data feed ─► clients
                                                                       └─► persisted for audit/settlement
```

**Flow:** gateway validates + risk-checks → order goes to a **sequencer** that assigns a strict order
and appends to a durable log → the matching engine consumes the log in order and matches → trades and
book updates are published to a market-data feed and persisted.

---

## 5️⃣ Deep Dives

### Deep Dive 1: Why single-threaded per symbol
Concurrency in matching would make trade outcomes non-deterministic and hard to audit. So each symbol
is matched by a **single thread** processing a strictly ordered input stream — extremely fast because
it's all in memory and lock-free. Scale across symbols by sharding symbols to different
engines/cores, not by parallelizing one book.

### Deep Dive 2: The sequencer (ordering + durability)
A **sequencer** assigns every incoming order a monotonic sequence number and appends it to a durable,
replayable log **before** matching. This gives: a single source of truth for order arrival (fairness),
crash recovery (replay the log to rebuild the book), and audit. It's the same append-only-log idea as
a message queue — see [distributed-message-queue.md](distributed-message-queue.md).

### Deep Dive 3: Fault tolerance via replay
The matching engine is deterministic, so recovery = replay the ordered log into a fresh engine to
rebuild the exact order book and continue. Run a **hot standby** replaying the same log; on primary
failure, the standby takes over with identical state. No trade is lost because nothing matches before
it's durably sequenced.

### Deep Dive 4: Low latency techniques
In-memory order book, no DB on the hot path, lock-free single-threaded matching, kernel-bypass
networking in real exchanges, and co-location. Persistence and market-data publishing happen
off the critical path (async) so they don't slow matching.

### Deep Dive 5: Market data fan-out
Trades and book deltas must reach many clients fast. Publish to a fan-out feed (multicast in real
exchanges; pub/sub otherwise), offering both a full book snapshot and incremental updates so a client
can sync then follow deltas.

---

## 6️⃣ Bottlenecks & Optimizations

- **Single symbol throughput** → shard symbols across engines; you can't parallelize one book.
- **Persistence on the hot path** → sequence to a fast append log; write to slow storage async.
- **Market-data fan-out** → multicast / efficient pub-sub; snapshot + deltas.
- **GC pauses** (managed runtimes) → off-heap/preallocated structures to avoid pauses in matching.

---

## 7️⃣ Interview Tips

1. Center on the **in-memory order book + single-threaded, deterministic matching** with price-time
   priority.
2. Introduce the **sequencer/append-log** for ordering, durability, and replay-based recovery.
3. Scale **across symbols**, not within one book.
4. Keep persistence and market data **off the hot path**.

### Common Follow-ups:
**Q: Why single-threaded matching?** Determinism + auditability; it's in-memory and fast anyway.
**Q: How do you recover after a crash?** Replay the sequenced log to rebuild the book; hot standby.
**Q: How do you scale?** Shard symbols across engines.
**Q: How do you keep latency low?** In-memory, lock-free, no DB on the path, async persistence.

---

## Summary

**Key Decisions:**
1. ✅ **In-memory order book** + **single-threaded deterministic matching** (price-time priority).
2. ✅ **Sequencer + append-only log** for ordering, durability, replay recovery.
3. ✅ **Hot standby** via deterministic replay; **shard by symbol** to scale.
4. ✅ Persistence + market-data fan-out kept **off the hot path**.

**Related:** [distributed-message-queue.md](distributed-message-queue.md) ·
[DistributedSystemsConcepts.md](../DistributedSystemsConcepts.md) ·
[qa-system-design-concepts.md](../../QA-Bank/qa-system-design-concepts.md)
