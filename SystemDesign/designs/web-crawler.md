# Web Crawler System Design
> **SDE-2 Interview Ready** | 45-minute format

## Problem Statement

Design a web crawler that systematically downloads web pages starting from seed URLs, extracts
links, and keeps crawling - at scale, politely, and without getting stuck.

**Example:** a search engine's crawler fetching billions of pages, respecting `robots.txt`, avoiding
duplicates and traps.

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. Start from seed URLs, download pages, extract and follow links (BFS).
2. Store page content for downstream processing (indexing).
3. Respect politeness (`robots.txt`, per-host rate limits).
4. Re-crawl for freshness.

### Non-Functional Requirements:
- **Scale:** billions of pages; distributed across many workers.
- **Politeness:** don't hammer a single host.
- **Robustness:** handle traps, huge pages, slow/dead servers, duplicate content.
- **Extensible:** pluggable parsers/content types.

### Out of Scope:
- Building the search index / ranking (crawler feeds it).

---

## 2️⃣ Capacity Estimation

```
Target: 1B pages/month
Rate = 1B / (30×24×3600) ≈ 400 pages/sec (peak ×2-3)
Page ≈ 500 KB avg → 1B × 500 KB = 500 TB/month raw content (compress + dedup)
URL metadata: 1B × ~100 B = ~100 GB "seen URLs" set → use a bloom filter to keep it in RAM
```

---

## 3️⃣ Components

```text
Seeds → URL Frontier ──> Fetcher(s) ──> Content parser ──> Link extractor
             ▲                │                                   │
             │                ▼                                   │
      "URL seen?" filter   Content store (S3/HDFS)                │
      (bloom + DB)            │                                   │
             └───────────────┴──── new URLs (filtered) ◄──────────┘
```

- **URL Frontier:** the queue of URLs to crawl (priority + politeness aware).
- **Fetcher:** downloads pages (many workers, respects robots.txt + per-host limits).
- **Parser:** extracts text + links; detects content type.
- **URL-seen filter:** dedup so we don't re-queue URLs.
- **Content store:** raw pages for indexing.
- **Content dedup:** detect identical/near-identical pages.

---

## 4️⃣ High-Level Design

```
        ┌──────────────┐
        │ URL Frontier │  (priority queues + per-host queues)
        └──────┬───────┘
   ┌───────────┼───────────┐
   ▼           ▼           ▼
┌──────┐   ┌──────┐   ┌──────┐
│Fetch │   │Fetch │   │Fetch │  (distributed workers)
│worker│   │worker│   │worker│
└──┬───┘   └──┬───┘   └──┬───┘
   └──────────┴──────────┘
              │ downloaded pages
              ▼
        ┌──────────────┐   ┌────────────────┐
        │  Parser +    │──►│ Content store  │ (S3/HDFS)
        │ link extract │   └────────────────┘
        └──────┬───────┘
               │ extracted URLs
               ▼
        ┌──────────────┐   "seen?" via bloom filter + URL DB
        │ URL filter/  │──────────────────────────────►
        │ dedup        │      new URLs → back to Frontier
        └──────────────┘
```

**Loop:** Frontier → Fetch → Parse → extract links → filter seen → enqueue new → repeat (BFS).

---

## 5️⃣ Deep Dives

### Deep Dive 1: URL Frontier (politeness + priority)
Two concerns: **don't overload a host**, and **crawl important pages first**.
- **Politeness:** partition URLs into **per-host queues**; a host is served by one worker at a time
  with a delay between requests. This prevents hammering one server.
- **Priority:** a front set of priority queues (by PageRank/freshness/importance) picks what to crawl
  next. High-value pages jump ahead.
The frontier is essentially a two-level queue: prioritizer → per-host queues.

### Deep Dive 2: Detecting already-seen URLs
Billions of URLs won't fit checking a DB per link. Use a **bloom filter** in memory as a cheap
pre-check: "definitely not seen" → enqueue; "maybe seen" → confirm against the URL store. No false
negatives means we never re-crawl by mistake. See
[hashing.md](../../Fundamentals/hashing.md).

### Deep Dive 3: Politeness via robots.txt
Fetch and cache each host's `robots.txt`; honor `Disallow` rules and `Crawl-delay`. Identify with a
proper User-Agent. Being impolite gets you IP-banned and is the point of the "how do you not get
blocked" follow-up.

### Deep Dive 4: Traps and robustness
- **Spider traps:** infinite URL spaces (calendars, `?page=1,2,3…∞`) → cap depth/URLs per domain,
  detect patterns.
- **Duplicate content:** many URLs → same content. Hash page content (or a **SimHash** for
  near-duplicates) and skip dupes.
- **Huge/slow pages:** enforce size and timeout limits.
- **Freshness:** re-crawl based on how often a page changes (news hourly, archives rarely).

### Deep Dive 5: Distributed coordination
Shard the frontier (e.g. by host hash) across nodes so each host is owned by one node - this keeps
politeness correct without cross-node coordination and scales horizontally.

---

## 6️⃣ Bottlenecks & Optimizations

- **DNS lookups** are a hidden bottleneck at scale → cache DNS aggressively.
- **Per-host serialization** limits throughput on big sites → crawl many hosts in parallel, not one
  host faster.
- **Content dedup** saves huge storage → hash + near-duplicate detection.
- **Frontier size** → persist to disk/DB; keep only hot portions in memory.

---

## 7️⃣ Interview Tips

1. Frame it as **BFS over the web graph** with a smart frontier.
2. The two things interviewers want: **politeness** (per-host queues + robots.txt) and **dedup**
   (bloom filter for seen URLs, content hash for duplicate pages).
3. Raise spider traps and freshness yourself.

### Common Follow-ups:
**Q: How do you avoid re-crawling the same URL?** Bloom filter + URL store.
**Q: How do you avoid getting banned?** robots.txt, crawl-delay, per-host rate limit, good User-Agent.
**Q: How do you detect duplicate pages?** Content hashing / SimHash for near-duplicates.
**Q: How do you keep the index fresh?** Re-crawl by change frequency.

---

## Summary

**Key Decisions:**
1. ✅ **URL Frontier** = priority queues + per-host queues (politeness).
2. ✅ **Bloom filter** for the seen-URL set; content hashing for duplicate pages.
3. ✅ Respect **robots.txt** + crawl-delay; distributed fetchers sharded by host.
4. ✅ Handle **traps, freshness, DNS caching**.

**Related:** [hashing.md](../../Fundamentals/hashing.md) ·
[message-queues.md](../components/message-queues.md) ·
[qa-system-design-concepts.md](../../QA-Bank/qa-system-design-concepts.md)
