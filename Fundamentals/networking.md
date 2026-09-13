# 🌐 Networking

!!! tip "Explain in 2 min"
    Networking is how two machines exchange bytes reliably over an unreliable
    medium. The **TCP/IP** model layers this: link → internet (**IP** routes packets) → transport
    (**TCP** gives reliable ordered streams, **UDP** gives fast fire-and-forget) → application (HTTP,
    DNS). **DNS** turns a name into an IP; **TCP's handshake** sets up a connection; **TLS** then
    negotiates encryption on top. **HTTP** rides over that — evolving from HTTP/1.1's head-of-line
    blocking to HTTP/2 multiplexing to HTTP/3 over QUIC/UDP. The classic interview question,
    "what happens when you type a URL," walks this whole stack end to end.

---

## 🧱 OSI vs TCP/IP `[core]`

OSI is the 7-layer teaching model; TCP/IP is the 4-layer model the internet actually uses.

| TCP/IP layer | OSI equivalent | Job | Examples |
|--------------|----------------|-----|----------|
| Application | 5-7 | app-level semantics | HTTP, DNS, TLS, gRPC |
| Transport | 4 | process-to-process delivery | TCP, UDP |
| Internet | 3 | routing across networks | IP, ICMP |
| Link | 1-2 | physical/local delivery | Ethernet, Wi-Fi, ARP |

You rarely need all 7 OSI names in an interview — knowing which layer TCP, IP, and HTTP live at, and
why, matters more.

---

## 🔀 TCP vs UDP `[core]`

| | TCP | UDP |
|--|-----|-----|
| Connection | connection-oriented (handshake) | connectionless |
| Reliability | guaranteed, ordered, retransmits | best-effort, may drop/reorder |
| Overhead | higher (ACKs, state) | minimal |
| Flow/congestion control | yes | no |
| Use when | correctness matters: web, APIs, file transfer | speed > completeness: video/voice, gaming, DNS |

**Rule of thumb:** default to TCP; reach for UDP when a late packet is worse than a lost one (live
media) or you want to build your own protocol on top (QUIC does exactly this).

---

## 🤝 TCP handshake & connection setup `[core]`

TCP opens with a **3-way handshake** — `SYN → SYN-ACK → ACK` — to agree on sequence numbers before
any data flows. This round trip is why connection reuse matters: **keep-alive** lets multiple
requests share one connection instead of paying the handshake each time. Closing uses a 4-way
exchange (`FIN`/`ACK` each way).

```text
Client                    Server
  | ---- SYN ----------->  |   "let's talk, my seq=x"
  | <--- SYN-ACK --------  |   "ok, my seq=y, ack x+1"
  | ---- ACK ----------->  |   "ack y+1" -> connection established
```

---

## 🔒 HTTPS / TLS handshake `[core]`

TLS runs on top of TCP to give **encryption, integrity, and server authentication**. Simplified:
1. Client sends supported ciphers + random.
2. Server sends its **certificate** (public key, signed by a CA) + random.
3. Client verifies the cert chain against trusted CAs, then they derive a shared **symmetric** key
   (via key exchange like ECDHE — giving *forward secrecy*).
4. Bulk data is encrypted with that fast symmetric key.

The pattern — **asymmetric crypto to bootstrap, symmetric to transfer** — recurs everywhere. Deeper
crypto detail lives in [security-fundamentals.md](security-fundamentals.md). TLS 1.3 cut the
handshake to one round trip (0-RTT for resumption).

---

## 📖 DNS `[core]`

DNS resolves a hostname to an IP, walking a hierarchy: **resolver → root → TLD (.com) →
authoritative** server. Results are **cached** with a TTL at every level (browser, OS, resolver) to
avoid repeating the walk. Record types worth knowing: `A`/`AAAA` (IPv4/IPv6), `CNAME` (alias),
`MX` (mail), `NS` (nameserver). DNS usually rides UDP (fast, small) and falls back to TCP for large
responses.

---

## 🌍 What happens when you type a URL `[core]`

The end-to-end walk that ties the stack together:
1. **URL parse** — scheme, host, path.
2. **DNS** — resolve host → IP (check caches first).
3. **TCP handshake** to the server IP (port 443 for HTTPS).
4. **TLS handshake** — negotiate encryption, verify cert.
5. **HTTP request** sent (`GET /path`, headers, cookies).
6. **Server** processes (maybe hitting caches/CDN, load balancer, app, DB) and responds.
7. **Browser** renders — parse HTML, fetch sub-resources (often multiplexed), run JS.

Great answer hooks: CDN/cache at step 6, load balancing (→ [load-balancer](../SystemDesign/components/load-balancer.md)),
and connection reuse (keep-alive, HTTP/2).

---

## 🚀 HTTP/1.1 vs 2 vs 3 `[core]`

| | HTTP/1.1 | HTTP/2 | HTTP/3 |
|--|----------|--------|--------|
| Transport | TCP | TCP | **QUIC over UDP** |
| Concurrency | one request/response per connection (pipelining broken) | **multiplexed** streams on one connection | multiplexed, no TCP head-of-line blocking |
| Head-of-line blocking | at HTTP layer | fixed at HTTP, still at TCP layer | eliminated (per-stream) |
| Headers | plaintext | **HPACK** compression | QPACK compression |
| Setup | TCP + TLS | TCP + TLS | combined (faster) |

The through-line: each version attacks **head-of-line blocking** and connection overhead. HTTP/3
moving to UDP is why QUIC exists — it reimplements reliability per-stream so one lost packet doesn't
stall the others.

---

## 🔌 Sockets, ports & WebSockets `[core]`

- A **socket** is one endpoint of a connection, identified by `(IP, port)`. A connection is the
  4-tuple `(src IP, src port, dst IP, dst port)`.
- **Ports** distinguish services on a host (80 HTTP, 443 HTTPS, 22 SSH, 53 DNS).
- **WebSockets** upgrade an HTTP connection to a **persistent, bidirectional** channel — the server
  can push without the client polling. Use for chat, live dashboards, collaborative editing. The
  alternatives are long-polling (older) and Server-Sent Events (server→client only).

---

## 🗺️ CDN basics `[core]`

A Content Delivery Network caches content on **edge servers** geographically close to users, cutting
latency and offloading the origin. Best for static assets (images, JS, video); can also cache
dynamic responses briefly. Deeper treatment with caching strategies:
[caching component](../SystemDesign/components/caching.md).

---

## ⚠️ Common interview traps

- Saying "TCP is always better than UDP" — UDP wins when latency beats reliability (live media, DNS).
- Forgetting DNS resolution and TLS are separate steps in the URL walk.
- Claiming HTTP/2 fully removes head-of-line blocking — it still exists at the **TCP** layer;
  HTTP/3 (QUIC/UDP) is what actually fixes it.
- Confusing a socket (endpoint) with a port (service identifier).
- Ignoring connection reuse (keep-alive / multiplexing) when reasoning about performance.

## 🔗 Related

- Q&A drills: [qa-networking.md](../QA-Bank/qa-networking.md)
- TLS crypto, certs, attacks → [security-fundamentals.md](security-fundamentals.md)
- Load balancing → [SystemDesign/components/load-balancer.md](../SystemDesign/components/load-balancer.md)
- CDN / caching → [SystemDesign/components/caching.md](../SystemDesign/components/caching.md)
- Latency numbers (RTT, cross-region) → [latency-numbers-and-estimation.md](latency-numbers-and-estimation.md)
