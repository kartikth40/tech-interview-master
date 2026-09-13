# ❓ Networking — Q&A

> Pairs with [Fundamentals/networking.md](../Fundamentals/networking.md). Format and tag legend:
> [QA-Bank/README.md](README.md).

---

> **Q1. TCP vs UDP?**
> TCP is connection-oriented and reliable (ordered, retransmits, flow/congestion control) at the
> cost of overhead. UDP is connectionless and best-effort (may drop/reorder) but fast and low
> overhead. Use TCP when correctness matters (web, APIs); UDP when a late packet is worse than a
> lost one (live media, gaming, DNS).
> *Follow-ups:* Why does video streaming often prefer UDP?
> `Easy` · `MAANG`

> **Q2. Walk me through the TCP 3-way handshake.**
> SYN → SYN-ACK → ACK. The client and server exchange initial sequence numbers and confirm both
> directions work before any data flows. This round trip is why connection reuse (keep-alive)
> matters for performance.
> *Follow-ups:* How does connection teardown differ? (4-way FIN/ACK.)
> `Med` · `MAANG`

> **Q3. What happens when you type a URL and hit enter?**
> Parse URL → DNS resolve host to IP → TCP handshake → TLS handshake (for HTTPS) → send HTTP request
> → server processes (often via LB, cache/CDN, app, DB) → response → browser renders and fetches
> sub-resources. Good hooks: caching/CDN, load balancing, connection reuse.
> *Follow-ups:* Where would a CDN and a load balancer fit?
> `Med` · `MAANG`

> **Q4. How does DNS resolution work?**
> A resolver walks the hierarchy — root → TLD (.com) → authoritative server — to get the IP, with
> caching (TTL) at each level (browser, OS, resolver) to avoid repeating it. It usually rides UDP
> and falls back to TCP for large responses.
> *Follow-ups:* What's the difference between an A record and a CNAME?
> `Med` · `MAANG`

> **Q5. Explain the TLS handshake at a high level.**
> Client and server agree on ciphers, the server presents a CA-signed certificate the client
> verifies, and they derive a shared symmetric key (via a key exchange like ECDHE, giving forward
> secrecy). Bulk data then uses fast symmetric encryption. Pattern: asymmetric to bootstrap,
> symmetric to transfer.
> *Follow-ups:* Why not use asymmetric crypto for all the data? (too slow.)
> `Hard` · `MAANG`

> **Q6. HTTP/1.1 vs HTTP/2 vs HTTP/3 — what changed?**
> Each attacks head-of-line blocking and connection overhead. HTTP/2 multiplexes many streams over
> one TCP connection and compresses headers. HTTP/3 moves to QUIC over UDP, eliminating TCP-level
> head-of-line blocking by making reliability per-stream.
> *Follow-ups:* Does HTTP/2 fully fix head-of-line blocking? (no — TCP layer remains; HTTP/3 does.)
> `Hard` · `Google`

> **Q7. What is head-of-line blocking?**
> When one delayed item blocks everything queued behind it. In HTTP/1.1 one slow response blocks the
> connection; HTTP/2 fixes it at the HTTP layer but a lost TCP packet still stalls all streams;
> HTTP/3 (QUIC) fixes it per-stream.
> *Follow-ups:* Why does QUIC use UDP to solve this?
> `Hard` · `Google`

> **Q8. What are idempotent HTTP methods and why care?**
> An idempotent method produces the same result whether called once or many times — GET, PUT,
> DELETE are idempotent; POST is not. It matters for safe retries: clients/proxies can retry
> idempotent requests without side effects.
> *Follow-ups:* How do you make a POST safely retryable? (idempotency key.)
> `Med` · `Amazon`

> **Q9. What is a socket?**
> One endpoint of a network connection, identified by an IP and port. A full connection is the
> 4-tuple (source IP, source port, destination IP, destination port), which is how a server
> distinguishes many clients on the same port.
> *Follow-ups:* How does a server handle thousands of connections on port 443?
> `Med` · `MAANG`

> **Q10. WebSockets vs HTTP polling — when and why?**
> WebSockets upgrade an HTTP connection into a persistent, bidirectional channel so the server can
> push without the client polling — ideal for chat, live dashboards, collaborative editing. Polling
> repeatedly asks and wastes requests; SSE is a server→client-only alternative.
> *Follow-ups:* When is long-polling or SSE good enough?
> `Med` · `Meta`

> **Q11. What does a CDN do?**
> Caches content on edge servers geographically close to users, cutting latency and offloading the
> origin. Best for static assets; can cache dynamic responses briefly. Also absorbs traffic spikes
> and provides some DDoS protection.
> *Follow-ups:* How does the CDN know when to refresh? (TTL, cache-control, invalidation.)
> `Med` · `MAANG`

> **Q12. OSI model vs TCP/IP model?**
> OSI is the 7-layer teaching model; TCP/IP is the 4-layer model the internet uses (link, internet,
> transport, application). What matters in interviews is knowing which layer TCP (transport), IP
> (internet), and HTTP (application) live at and why.
> *Follow-ups:* Which layer does TLS sit at?
> `Easy` · `MAANG`

> **Q13. What is HTTP keep-alive and why does it help?**
> It reuses one TCP connection for multiple requests instead of opening a new one each time, saving
> the handshake (and TLS handshake) round trips. This is a big latency win for pages that fetch many
> resources.
> *Follow-ups:* How does HTTP/2 multiplexing extend this idea?
> `Med` · `MAANG`

> **Q14. What are common HTTP status code classes?**
> 2xx success, 3xx redirect, 4xx client error (400 bad request, 401 unauthorized, 403 forbidden, 404
> not found, 429 too many requests), 5xx server error (500, 503). Knowing 401 vs 403 and 429 is a
> frequent probe.
> *Follow-ups:* 401 vs 403? (not authenticated vs authenticated-but-not-allowed.)
> `Easy` · `MAANG`

> **Q15. What is the difference between latency and throughput?**
> Latency is the time for one operation (how long a single request takes); throughput is how many
> operations complete per unit time. You can have low throughput with low latency and vice versa —
> optimizing one can hurt the other (e.g. batching raises throughput but adds latency).
> *Follow-ups:* How does batching trade one for the other?
> `Med` · `MAANG`

> **Q16. Public-key vs symmetric encryption in transit?**
> Symmetric (one shared key) is fast but needs secure key sharing; asymmetric (public/private) solves
> key exchange and authentication but is slow. TLS uses asymmetric to authenticate and exchange a
> key, then symmetric for the actual data.
> *Follow-ups:* What is forward secrecy? (compromising the long-term key doesn't decrypt past sessions.)
> `Hard` · `Google`

> **Q17. What is a reverse proxy, and how is it different from a forward proxy?**
> A reverse proxy sits in front of servers (handling TLS termination, load balancing, caching); a
> forward proxy sits in front of clients (egress control, anonymity). Load balancers and API gateways
> are reverse proxies.
> *Follow-ups:* What does TLS termination at the proxy buy you?
> `Med` · `MAANG`

> **Q18. Why is UDP used for DNS despite being unreliable?**
> DNS queries are small and frequent, so avoiding TCP's handshake overhead matters more than
> guaranteed delivery — a lost query is just retried. Large responses (or zone transfers) fall back
> to TCP.
> *Follow-ups:* What changed with DNS-over-HTTPS/TLS? (privacy, at some latency cost.)
> `Med` · `Google`

---

**Related:** [Fundamentals/networking.md](../Fundamentals/networking.md) ·
[qa-security.md](qa-security.md) · [qa-system-design-concepts.md](qa-system-design-concepts.md)
