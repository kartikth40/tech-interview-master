# Rate Limiter System Design
> **SDE-2 Interview Ready** | 45-minute format

## Problem Statement

Design a rate limiter that caps how many requests a client can make in a time window, protecting
services from abuse, brute-force, scraping, and overload.

**Example:** "Allow at most 100 requests per user per minute; reject the rest with HTTP 429."

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. Limit requests per client (by user ID, API key, or IP) per time window.
2. Reject excess requests with a clear signal (HTTP 429 + `Retry-After`).
3. Support different rules per endpoint (e.g. 5 logins/min, 1000 reads/min).

### Non-Functional Requirements:
- **Low latency:** the limiter is on the hot path - must add minimal overhead (<1-2ms).
- **Accuracy:** don't allow significantly more than the limit.
- **Distributed:** many app servers must share one limit per client.
- **Availability:** a limiter outage shouldn't take down the service (fail-open vs fail-closed decision).

### Out of Scope:
- Billing/quota accounting (related but separate).
- WAF / bot detection.

---

## 2️⃣ Capacity Estimation

```
Assume 1M active clients, 100 req/client/min average
Requests/sec = 1M × 100 / 60 ≈ 1.67M req/sec (peak ×2-3)
Each check reads+writes one counter → the counter store must sustain ~several M ops/sec
Memory: one counter per active client per rule; a few counters × 1M clients × ~50 B ≈ tens of MB
```

Takeaway: the store must be fast and in-memory (Redis-class), and the per-request cost must be a
single atomic op.

---

## 3️⃣ API / Interface Design

```text
# Limiter is usually middleware, not a public API. Conceptual contract:
allow(clientId, rule) -> { allowed: bool, remaining: int, retryAfterSec: int }

# On reject, the service returns:
HTTP 429 Too Many Requests
Headers:
  Retry-After: 5
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1700000000
```

---

## 4️⃣ Algorithms

| Algorithm | How it works | Trade-off |
|-----------|--------------|-----------|
| **Token Bucket** ⭐ | Bucket refills tokens at a fixed rate; each request takes one; empty = reject | Allows bursts up to bucket size; simple, most common |
| **Leaky Bucket** | Requests queue and drain at a fixed rate | Smooths bursts into a steady output rate; adds queueing delay |
| **Fixed Window** | Count per fixed clock window (per minute) | Simple, but allows 2× burst at window boundaries |
| **Sliding Window Log** | Store timestamps of recent requests; count those in the last window | Accurate, but memory grows with request rate |
| **Sliding Window Counter** ⭐ | Weighted blend of current + previous fixed window | Good accuracy/memory balance; common in practice |

**Token bucket (the default answer):**

```text
FUNCTION allow(clientId, capacity, refillPerSec):
    now = current time
    bucket = store.get(clientId)   # { tokens, lastRefill }
    IF bucket is null:
        bucket = { tokens: capacity, lastRefill: now }

    # Refill based on elapsed time
    elapsed = now - bucket.lastRefill
    bucket.tokens = min(capacity, bucket.tokens + elapsed × refillPerSec)
    bucket.lastRefill = now

    IF bucket.tokens >= 1:
        bucket.tokens = bucket.tokens - 1
        store.set(clientId, bucket)
        RETURN allowed
    ELSE:
        store.set(clientId, bucket)
        RETURN rejected   # 429
```

**Fixed-window boundary problem:** with a per-minute window, a client can send the full limit at
`00:59` and again at `01:00` - 2× the intended rate across a few seconds. The sliding-window counter
fixes this by weighting the previous window:

```text
# Approximate count = current window count + previous window count × overlap_fraction
weighted = curCount + prevCount × ((windowSize - elapsedInCurrent) / windowSize)
IF weighted < limit: allow ELSE reject
```

---

## 5️⃣ High-Level Design

```
┌──────────────┐
│    Clients   │
└──────┬───────┘
       ▼
┌───────────────────────────┐
│  API Gateway / LB         │  ← coarse global limit (per IP/API key)
│  [Rate Limiter middleware]│
└──────┬────────────────────┘
       │ allowed
       ▼
┌────────┐ ┌────────┐        ┌──────────────┐
│ Service│ │ Service│ ...    │    Redis     │  ← shared counters
│  (fine │ │  (fine │◄──────►│ (atomic INCR │
│  limit)│ │  limit)│        │  + TTL)      │
└────────┘ └────────┘        └──────────────┘
```

**Where to enforce:**
- **API gateway / LB** - coarse, cheap, protects everything (per IP/API key).
- **Per service** - fine-grained, per-endpoint rules and per-user limits.
Often both: broad protection at the edge, precise rules in the service.

---

## 6️⃣ Distributed Rate Limiting

The core challenge: many app servers, one logical limit per client. A local in-memory counter per
server would let a client do `N × serverCount` requests.

**Solution: shared counter in Redis with atomic ops.**

```text
FUNCTION allowDistributed(clientId, limit, windowSec):
    key = "rl:" + clientId + ":" + currentWindow()
    # INCR is atomic; first hit sets TTL so the window expires
    count = redis.INCR(key)
    IF count == 1:
        redis.EXPIRE(key, windowSec)
    RETURN count <= limit
```

- Use **atomic INCR** (or a Lua script for token bucket) so concurrent servers don't race.
- **Per-key TTL** auto-expires windows - no cleanup job.
- For token bucket, run the read-modify-write as a **Lua script** so it's atomic on the Redis side.

**Trade-offs:**
- ✅ Single source of truth across servers.
- ✅ Fast (in-memory, one round trip).
- ❌ Redis is a dependency and potential SPOF → replicate; decide fail-open (availability) vs
  fail-closed (protection) if Redis is unreachable.
- ❌ A cross-datacenter setup adds latency; often each region limits locally and syncs loosely.

---

## 7️⃣ Deep Dives

### Deep Dive 1: Race conditions under concurrency
Two servers reading a counter, both seeing "99 < 100", both allowing → 101 through. Fix by making
the check-and-increment atomic: Redis `INCR` for windowed counters, or a Lua script that does the
whole token-bucket update server-side. See
[concurrency-and-parallelism.md](../../Fundamentals/concurrency-and-parallelism.md) for the
underlying race.

### Deep Dive 2: Fail-open vs fail-closed
If the counter store is down, do you allow all traffic (fail-open - favors availability, risks
overload) or block it (fail-closed - favors protection, risks an outage)? Most user-facing systems
fail-open with local fallback limits; security-critical endpoints (login) fail-closed.

### Deep Dive 3: Where limits live and rule config
Keep rules in config (per endpoint, per plan tier), loaded at startup and refreshable. A gateway
applies coarse per-IP limits; services apply per-user/per-endpoint limits. Return standard
`X-RateLimit-*` headers so clients can self-throttle.

---

## 8️⃣ Bottlenecks & Optimizations

- **Redis hot key** for a very active client → shard the counter or add a short local pre-check
  (local token bucket that syncs periodically).
- **Round-trip latency** → co-locate Redis, or use a local sliding window with periodic reconciliation
  for approximate limits.
- **Thundering clients** on reset boundaries → jitter windows or use sliding-window counter.

---

## 9️⃣ Interview Tips

1. Clarify: limit by what key (user/IP/API key)? per endpoint? distributed?
2. Name the algorithms; default to **token bucket**, mention sliding-window counter for accuracy.
3. Make it **distributed** with a shared Redis counter + atomic ops - this is the point of the question.
4. Discuss fail-open vs fail-closed and where to enforce (gateway vs service).
5. Return 429 + `Retry-After`.

### Common Follow-ups:
**Q: Why not a fixed window?** Boundary burst allows ~2× the rate; use sliding-window counter.
**Q: How do you keep it consistent across servers?** Shared counter in Redis with atomic INCR/Lua.
**Q: What if Redis goes down?** Replicate; choose fail-open vs fail-closed per endpoint criticality.
**Q: How do you rate-limit login specifically?** Stricter limit (e.g. 5/15min), fail-closed.

---

## Summary

**Key Decisions:**
1. ✅ **Token bucket** (bursts) or **sliding-window counter** (accuracy).
2. ✅ **Shared Redis counter** with atomic INCR / Lua for distributed correctness.
3. ✅ Enforce at **gateway (coarse) + service (fine)**.
4. ✅ Return **429 + Retry-After**; decide **fail-open vs fail-closed**.

**Related:** [SystemDesignGuide.md](../SystemDesignGuide.md) ·
[security-fundamentals.md](../../Fundamentals/security-fundamentals.md) ·
[qa-system-design-concepts.md](../../QA-Bank/qa-system-design-concepts.md)
