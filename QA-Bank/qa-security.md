# ❓ Security - Q&A

> Pairs with [Fundamentals/security-fundamentals.md](../Fundamentals/security-fundamentals.md).
> Format and tag legend: [QA-Bank/README.md](README.md).

---

> **Q1. Authentication vs authorization?**
> Authentication proves who you are; authorization decides what you're allowed to do.
> Authentication comes first (login), then authorization checks permissions (RBAC/ABAC) for each
> action. Mixing them up is a common slip.
> *Follow-ups:* Give an example of each in an API request.
> `Easy` · `MAANG`

> **Q2. Sessions vs JWT - trade-offs?**
> Server sessions are stateful: easy to revoke, but need a session store and complicate scaling.
> JWTs are stateless: the server verifies a signature and stores nothing (scales well), but are hard
> to revoke before expiry - mitigate with short TTLs plus refresh tokens.
> *Follow-ups:* How do you revoke a JWT early? (short TTL + refresh, or a blocklist.)
> `Med` · `MAANG`

> **Q3. Is OAuth2 authentication or authorization?**
> Authorization - it lets an app access a user's data on another service without sharing the
> password. OIDC is the identity layer built on top of OAuth2 that adds authentication (the "Sign in
> with Google" ID token). Calling OAuth2 "authentication" is a classic mistake.
> *Follow-ups:* What does the ID token in OIDC add?
> `Hard` · `Google`

> **Q4. How should passwords be stored?**
> Hashed with a slow, salted algorithm - bcrypt, scrypt, or Argon2 - never plaintext or a fast hash.
> A per-user salt defeats rainbow tables; a work factor keeps brute force expensive over time.
> *Follow-ups:* What's a pepper vs a salt?
> `Med` · `MAANG`

> **Q5. What is XSS and how do you defend against it?**
> Cross-site scripting: an attacker injects JavaScript that runs in a victim's browser (e.g. via
> unescaped user content). Defend by escaping/encoding output, a Content-Security-Policy, and marking
> session cookies `HttpOnly` so scripts can't read them.
> *Follow-ups:* Stored vs reflected XSS?
> `Med` · `Meta`

> **Q6. What is CSRF and how do you prevent it?**
> Cross-site request forgery tricks a logged-in user's browser into making an unwanted authenticated
> request. Prevent with anti-CSRF tokens, `SameSite` cookies, and checking the Origin/Referer.
> *Follow-ups:* Why does SameSite=Lax help?
> `Med` · `MAANG`

> **Q7. How do you prevent SQL injection?**
> Use parameterized queries / prepared statements so user input is treated as data, never as SQL.
> Also apply least-privilege DB accounts and input validation. Never build queries by string
> concatenation.
> *Follow-ups:* Why isn't escaping/blocklisting input a reliable fix? (parameterization separates code from data.)
> `Med` · `MAANG`

> **Q8. What is SSRF?**
> Server-side request forgery: an attacker makes the server fetch an attacker-chosen URL - often to
> reach internal services or cloud metadata endpoints. Defend by allowlisting outbound hosts and
> blocking internal IP ranges.
> *Follow-ups:* Why are cloud metadata endpoints a common SSRF target? (credentials.)
> `Hard` · `Amazon`

> **Q9. Symmetric vs asymmetric encryption?**
> Symmetric uses one shared key (fast, but key distribution is the hard part). Asymmetric uses a
> public/private key pair (solves key exchange and enables signatures, but slow). TLS combines them:
> asymmetric to exchange a key, symmetric for the bulk data.
> *Follow-ups:* Where does hashing fit? (integrity - one-way, not encryption.)
> `Med` · `MAANG`

> **Q10. Where should you store a JWT on the client?**
> Prefer an `HttpOnly`, `Secure`, `SameSite` cookie so JavaScript (and thus XSS) can't read it.
> `localStorage` is convenient but XSS-exposed. Whatever you choose, keep access tokens short-lived.
> *Follow-ups:* What's the CSRF trade-off of cookie storage? (add SameSite / CSRF tokens.)
> `Hard` · `Meta`

> **Q11. What is rate limiting and why is it a security control?**
> Capping requests per client per window protects against brute-force, credential stuffing, scraping,
> and abuse, and provides backpressure. Common algorithms: token bucket, leaky bucket, sliding
> window; back it with Redis for a distributed counter and return 429.
> *Follow-ups:* Why a stricter limit on login endpoints?
> `Med` · `MAANG`

> **Q12. Name a few security principles you design by.**
> Defense in depth (layered controls), least privilege (minimum access), fail securely (errors deny,
> not grant), never trust input (validate at boundaries), and don't roll your own crypto (use vetted
> libraries).
> *Follow-ups:* Give an example of "fail securely."
> `Med` · `Amazon`

> **Q13. How do you manage secrets (API keys, DB passwords)?**
> Keep them out of source and images; use a secrets manager / vault, inject at runtime via env vars
> or mounted files, rotate regularly, and audit access. A key committed to git should be treated as
> compromised and rotated.
> *Follow-ups:* What do you do the moment a secret leaks to a public repo? (rotate immediately.)
> `Med` · `MAANG`

---

**Related:** [Fundamentals/security-fundamentals.md](../Fundamentals/security-fundamentals.md) ·
[qa-networking.md](qa-networking.md) · [qa-hashing.md](qa-hashing.md)
