# Google Drive / Dropbox System Design (File Storage & Sync)
> **SDE-2 Interview Ready** | 45-minute format

## 🎯 Problem Statement

Design a cloud file storage and sync service like Dropbox or Google Drive: users upload files, they
sync across devices, and can be shared.

**Example:** edit a file on your laptop; the change appears on your phone within seconds, and a
collaborator sees it too.

---

## 1️⃣ Requirements Clarification

### Functional Requirements:
1. Upload/download files; sync across a user's devices.
2. Sync only what changed (efficient for large files).
3. File versioning and sharing.
4. Offline edits reconcile on reconnect.

### Non-Functional Requirements:
- **Scale:** 100M users, billions of files, PB of storage.
- **Reliability:** never lose a file (high durability).
- **Efficiency:** don't re-upload whole files on small edits.
- **Consistency:** all devices converge; conflicts handled sanely.

### Out of Scope:
- Real-time collaborative editing (Google Docs OT/CRDT is a different problem).

---

## 2️⃣ Capacity Estimation

```
100M users × 100 files × 1 MB avg = 10 PB (before dedup + replication)
Read:write heavily read; but sync generates frequent small metadata ops
Chunk size ~4 MB → a 40 MB file = 10 chunks; only changed chunks re-upload
Metadata QPS dominates (sync polling/notifications) → separate metadata from block storage
```

---

## 3️⃣ API Design

```text
POST /v1/files                 # create file metadata, get upload URLs per chunk
PUT  <chunk upload URL>        # upload a chunk to block storage (direct to S3)
GET  /v1/files/{id}            # metadata + chunk list
GET  /v1/files/{id}/changes    # delta since a version (for sync)
POST /v1/files/{id}/share      # share with user/link
```

---

## 4️⃣ Core Idea: Split Metadata from Block Storage + Chunking

The two design keys:
1. **Chunk files** into fixed-size blocks (e.g. 4 MB). Sync and dedup operate on chunks, so a small
   edit only moves the changed chunk(s) — **delta sync**.
2. **Separate metadata service from block storage.** Metadata (file tree, versions, chunk lists,
   permissions) lives in a database; the actual bytes live in object storage (S3-like), often
   accessed directly by clients via signed URLs.

```
Client ──metadata ops──► Metadata Service ──► Metadata DB (files, chunks, versions, ACLs)
   │
   └──chunk bytes───────► Block Storage (S3) ◄── signed URLs, CDN for downloads
```

---

## 5️⃣ High-Level Design

```
                     ┌────────────────────┐
   Devices ─────────►│  Notification svc  │  (long-poll/WebSocket: "you have changes")
     │  sync         └─────────▲──────────┘
     │                         │ change events
     ▼                         │
┌─────────────────┐     ┌──────┴───────────┐        ┌──────────────┐
│  Metadata svc   │────►│  Metadata DB     │        │ Block Storage│
│ (files, chunks, │     │ (sharded by user)│        │   (S3)       │
│  versions, ACL) │     └──────────────────┘        └──────▲───────┘
└─────────────────┘                                        │
     ▲                                                      │
     └── clients upload/download chunks directly ───────────┘ (signed URLs)
```

**Upload flow:** client chunks the file, hashes each chunk, asks metadata service which chunks are
new (dedup), uploads only new chunks to S3, then commits the file version in metadata.
**Sync flow:** metadata service records a change; the notification service pushes "you have changes"
to the user's other devices, which pull the delta and download only new chunks.

---

## 6️⃣ Deep Dives

### Deep Dive 1: Delta sync via chunking + content hashing
Hash each chunk (content hash). On edit, only chunks whose hash changed are uploaded. On another
device, only those chunks are downloaded. This makes syncing a 1 GB file after a tiny edit cheap.
Content hashing also enables **dedup** — identical chunks (even across users) are stored once. See
[hashing.md](../../Fundamentals/hashing.md).

### Deep Dive 2: Metadata vs block storage split
Metadata is small, transactional, and queried constantly (sync); block data is huge and
write-once-read-many. Keeping them separate lets each scale independently — a sharded DB for
metadata, cheap object storage (+ CDN) for blocks. Clients hit S3 directly via signed URLs so bytes
don't flow through app servers.

### Deep Dive 3: How devices learn about changes (notification)
Polling every device constantly is wasteful. A notification service holds long-poll/WebSocket
connections and pushes a lightweight "changes available" signal; the device then pulls the delta.
This is the same push-signal + pull-detail pattern as a feed.

### Deep Dive 4: Conflict resolution
Two devices edit the same file offline. On reconnect, use versioning: if versions diverged, keep
both as **conflicted copies** (Dropbox's "conflicted copy" approach) rather than silently losing
one. Last-write-wins is simpler but can lose data. Track versions with a per-file version
number/vector.

### Deep Dive 5: Durability & storage efficiency
- **Durability:** replicate chunks across zones (or erasure coding) so no single failure loses data.
- **Dedup:** content-addressed chunks stored once, referenced by many files (huge savings).
- **Cold storage tiering:** move rarely accessed files to cheaper storage.

---

## 7️⃣ Bottlenecks & Optimizations

- **Metadata DB hot on sync** → shard by user; cache the file tree.
- **Small-file overhead** → pack tiny files; chunking shines on large files.
- **Upload bandwidth** → client-side compression + only-changed-chunk upload.
- **Notification fan-out** to many devices → efficient long-poll/WebSocket layer.

---

## 8️⃣ Interview Tips

1. Lead with **chunking + content hashing** (delta sync + dedup) and the **metadata/block split**.
2. Explain sync as **push a signal, pull the delta**.
3. Handle **conflicts** honestly (conflicted copies over silent LWW).
4. Mention **durability** (replication/erasure coding) and **dedup** savings.

### Common Follow-ups:
**Q: How do you sync a small edit to a huge file cheaply?** Chunk + content hash; upload changed chunks only.
**Q: How do you dedup storage?** Content-addressed chunks stored once, referenced by many files.
**Q: How do offline edits reconcile?** Versioning; keep conflicted copies on divergence.
**Q: How do other devices know to sync?** Notification service pushes a signal; device pulls the delta.

---

## Summary

**Key Decisions:**
1. ✅ **Chunking + content hashing** → delta sync + dedup.
2. ✅ **Metadata service (sharded DB) separate from block storage (S3 + CDN)**.
3. ✅ **Notification service** (push signal, pull delta) for cross-device sync.
4. ✅ **Versioning + conflicted copies**; **replication/erasure coding** for durability.

**Related:** [hashing.md](../../Fundamentals/hashing.md) ·
[database-sharding.md](../components/database-sharding.md) ·
[caching.md](../components/caching.md)
