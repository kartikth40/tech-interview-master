# Nearby Friends / Proximity Service System Design
> **SDE-2 Interview Ready** | 45-minute format

## Problem Statement

Design a service that shows a user which of their friends are nearby, updating in near real time as
people move - like Snap Map or "Nearby Friends" on Facebook.

**Example:** open the app and see friends within 5 km, refreshing every few seconds.

> Complements the [Uber](uber.md) design (geospatial matching); this focuses on continuous location
> updates and privacy for a social graph.

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. Users publish their location periodically.
2. A user sees friends within a radius, updated in near real time.
3. Respect privacy (opt-in, granular sharing).

### Non-Functional Requirements:
- **Scale:** 100M users, frequent location updates (bursty writes).
- **Low latency:** proximity results in <1s.
- **Freshness:** locations no more than a few seconds stale.
- **Privacy:** users control who sees them; off means invisible.

### Out of Scope:
- Turn-by-turn routing; matching strangers (that's ride-hailing/dating).

---

## 2️⃣ Capacity Estimation

```
100M users, active 10M, each sends location every 5s
Writes = 10M / 5 = 2M location updates/sec → very write-heavy
Each user has ~200 friends → proximity check is bounded to the friend set, not all users
Store current location in memory (Redis) - ephemeral, TTL'd; history optional
```

---

## 3️⃣ API Design

```text
POST /v1/location   { lat, lng, ts }        # publish my location (every few sec)
GET  /v1/nearby?radius_km=5                 # friends within radius
# Real-time: WebSocket/pub-sub push of friends' location updates
```

---

## 4️⃣ Key Insight: Proximity is bounded by the friend graph

Unlike Uber (match any nearby driver), "nearby friends" only cares about a user's **friends** -
a bounded set (~hundreds). So we don't need a global geo query per request; we compute distance
against the user's friends' cached locations. Geospatial indexing still helps when the friend set is
large or for "friends in this area" queries.

---

## 5️⃣ High-Level Design

```
Devices ──location updates (every ~5s)──►┌──────────────────┐
   ▲                                     │ Location Ingest  │
   │  push friends' updates              │  (stateless)     │
   │                                     └────────┬─────────┘
┌──┴───────────────┐                              ▼
│  Pub/Sub layer   │◄───────────────────  ┌──────────────────┐
│ (Redis / WS)     │   publish update      │ Location Store   │
└──────────────────┘   to friends'         │ Redis GEO / TTL  │  current loc only
                       channels            │ (sharded by user)│
                                           └──────────────────┘
                                                  ▲
                                           ┌──────┴───────┐
                                           │ Friend graph │  who are my friends?
                                           └──────────────┘
```

**Flow:** device posts location → ingest updates the location store (with TTL) → publishes the
update to the user's friends via pub/sub → each friend's device (subscribed) receives it and updates
the map. On demand, `GET /nearby` reads friends' cached locations and filters by radius.

---

## 6️⃣ Deep Dives

### Deep Dive 1: Geospatial indexing (geohash / quadtree)
To answer "who/what is near this point," encode locations with a **geohash** (a string prefix where
nearby points share prefixes) or a **quadtree** (recursively subdivided cells). Both let you query a
cell + neighbors instead of scanning everything. Redis `GEO` commands (backed by geohash) give
`GEOSEARCH ... BYRADIUS` out of the box. Uber uses similar grid indexing - see [uber.md](uber.md).

### Deep Dive 2: Handling the write storm
2M updates/sec is the hard part. Mitigations: **adaptive update frequency** (send less often when
stationary), store only the **latest** location (overwrite, TTL - no history), shard the location
store by user ID, and treat updates as fire-and-forget. Losing one update is fine; the next arrives
in seconds.

### Deep Dive 3: Real-time delivery via pub/sub
Each user subscribes to a channel; when a friend's location changes, publish to that channel and
push over a WebSocket. This is push (not poll) so the map updates live. For users with many active
friends, batch updates over a short window to cut message volume.

### Deep Dive 4: Privacy
Location is sensitive: sharing is **opt-in and granular** (per friend / ghost mode / precise vs
approximate). If a user goes invisible, stop publishing and drop their cached location. Never expose
location to non-friends. This is a first-class requirement, not an afterthought - see
[security-fundamentals.md](../../Fundamentals/security-fundamentals.md).

### Deep Dive 5: Staleness & TTL
Store current location with a short **TTL** so a user who goes offline simply disappears (their key
expires) rather than showing a stale position. Freshness beats history here.

---

## 7️⃣ Bottlenecks & Optimizations

- **Write throughput** → adaptive frequency, latest-only writes, shard by user.
- **Fan-out to many friends** → batch/window updates; pub/sub per channel.
- **Hot areas** (concerts, cities) → geospatial cells still bound the query; cache popular cells.
- **Battery/data on device** → back off updates when stationary.

---

## 8️⃣ Interview Tips

1. Call out the key difference from Uber: **bounded by the friend set**, not a global match.
2. The write storm is the real challenge - adaptive frequency + latest-only + TTL.
3. Use **geohash/quadtree** (or Redis GEO) for area queries.
4. Treat **privacy** as a core requirement.

### Common Follow-ups:
**Q: How do you handle 2M updates/sec?** Adaptive frequency, latest-only + TTL, shard by user, fire-and-forget.
**Q: How do you find who's nearby?** Geohash/quadtree cells (or Redis GEO), filtered to friends.
**Q: How is this different from Uber?** Bounded to friends, continuous updates, privacy-first.
**Q: How do you push updates live?** Pub/sub + WebSocket to subscribed friends.

---

## Summary

**Key Decisions:**
1. ✅ Proximity **bounded by the friend graph** (not a global geo scan).
2. ✅ **Geohash/quadtree (Redis GEO)** for area queries.
3. ✅ Handle the **write storm**: adaptive frequency, latest-only + TTL, shard by user.
4. ✅ **Pub/sub + WebSocket** for real-time delivery; **privacy** (opt-in, ghost mode) first-class.

**Related:** [uber.md](uber.md) ·
[security-fundamentals.md](../../Fundamentals/security-fundamentals.md) ·
[caching.md](../components/caching.md)
