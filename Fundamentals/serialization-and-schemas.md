# 📦 Serialization & Schemas

!!! tip "Explain in 2 min"
    Serialization turns in-memory objects into bytes for network or storage, and
    back. **JSON** is human-readable, schemaless, and universal - great for public APIs, but verbose
    and slow to parse. **Protobuf** and **Avro** are compact binary formats with a schema - much
    smaller and faster, ideal for internal service-to-service traffic and event streams. The subtle,
    interview-relevant part is **schema evolution**: services deploy independently, so old and new code
    must read each other's data. Formats support this via rules - add optional fields, never reuse
    field tags, provide defaults - so a change stays **backward and forward compatible**.

---

## JSON vs Protobuf vs Avro `[core]`

| | JSON | Protobuf | Avro |
|--|------|----------|------|
| Format | text | binary | binary |
| Schema | none (implicit) | `.proto`, required | `.avsc`, required |
| Size / speed | large, slower | small, fast | small, fast |
| Human-readable | yes | no | no |
| Schema travels with data | n/a | no (out of band) | often yes (or via registry) |
| Best for | public APIs, configs, logs | internal RPC (gRPC) | data pipelines, Kafka events |

**Rule of thumb:** JSON at the edge (public APIs, debuggability), binary + schema internally where
volume and speed matter. gRPC's use of Protobuf is covered in
[APIDesignPatterns.md](../SystemDesign/APIDesignPatterns.md) - this note is about the
*schema-evolution* angle, not re-explaining gRPC.

---

## Schema evolution & compatibility `[core]`

The core problem: producers and consumers deploy at different times, so data written by one version
must be readable by another. Two directions:
- **Backward compatible:** new code can read **old** data.
- **Forward compatible:** old code can read **new** data.

Rules that keep both working:
- **Add fields as optional / with defaults** - old readers skip unknown fields; new readers fill
  missing ones with the default.
- **Never change or reuse a field's tag/ID** (Protobuf field numbers, Avro names) - reusing a tag
  makes old data deserialize into the wrong field.
- **Don't remove required fields** - deprecate instead (mark optional, stop writing).
- **Rename via aliases**, not by changing the wire identity.

```text
# Protobuf: adding a field safely (v1 readers ignore field 3; v2 readers default it)
message User {
  string id    = 1;
  string name  = 2;
  string email = 3;   # NEW - optional in proto3, old readers skip it
}
# Breaking: changing field 2 from string to int, or reusing tag 2 for something else
```

**Avro** matters specifically because it separates the **writer's schema** (used to write) from the
**reader's schema** (used to read) and resolves differences using defaults/aliases - which is why
it's the common choice for long-lived Kafka event logs backed by a **schema registry**.

---

## Schema registry `[advanced]`

For event streams (Kafka), a **schema registry** stores schema versions centrally. Producers
register a schema and send a small schema ID with each message instead of the full schema; consumers
fetch the schema by ID to decode. It also **enforces compatibility** (rejects a producer trying to
push a breaking change), which is how large event-driven systems avoid breaking downstream consumers.

---

## When to use which `[core]`

- **Public / third-party API** → JSON (readable, universal, easy to debug/cache).
- **Internal high-volume RPC** → Protobuf over gRPC (small, fast, typed contract).
- **Event streaming / data lake** → Avro + schema registry (evolution + writer/reader schemas).
- **Config / logs** → JSON/YAML (human-edited).

---

## Common interview traps

- Treating "just use JSON everywhere" as free - verbosity and parse cost add up at scale.
- Reusing or renumbering field tags - the classic schema-evolution bug.
- Assuming a schema change is safe without checking **both** backward and forward compatibility.
- Forgetting that binary formats need the schema out-of-band (registry or shared `.proto`).

## Related

- Q&A drills: [qa-system-design-concepts.md](../QA-Bank/qa-system-design-concepts.md)
- gRPC / Protobuf in APIs → [SystemDesign/APIDesignPatterns.md](../SystemDesign/APIDesignPatterns.md)
- Kafka event compatibility → [distributed-message-queue.md](../SystemDesign/designs/distributed-message-queue.md)
- Idempotency & delivery (why event dedup matters) → [idempotency-and-delivery-semantics.md](idempotency-and-delivery-semantics.md)
