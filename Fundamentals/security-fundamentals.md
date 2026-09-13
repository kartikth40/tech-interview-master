# 🔐 Security Fundamentals

!!! tip "Explain in 2 min"
    Application security starts with two questions: **who are you
    (authentication)** and **what are you allowed to do (authorization)**. You prove identity with
    sessions, tokens (JWT), or delegated flows (OAuth2/OIDC). You protect data in transit with **TLS**
    and data at rest / passwords with the right **hashing** (slow, salted - bcrypt/Argon2, never plain
    SHA). On top of that, most breaches come from a short list of well-known attacks - **XSS, CSRF,
    SQL injection, SSRF** - each with a standard defense (escape output, anti-CSRF tokens,
    parameterized queries, allowlist outbound requests). The mindset: never trust input, apply defense
    in depth, and give the least privilege necessary.

---

## Authentication vs authorization `[core]`

| | Authentication (authN) | Authorization (authZ) |
|--|------------------------|------------------------|
| Question | who are you? | what can you do? |
| Proves | identity | permissions |
| Example | logging in with a password | "only admins can delete" |
| Comes | first | after authN |

Mixing them up is a classic interview slip. AuthN establishes identity; authZ decides access for
that identity (RBAC = role-based, ABAC = attribute-based).

---

## Sessions vs JWT vs OAuth2/OIDC `[core]`

| Approach | How it works | Trade-off |
|----------|--------------|-----------|
| **Session (stateful)** | server stores session, client holds a cookie with the session ID | easy to revoke; needs server/shared store; scaling requires sticky sessions or a session store |
| **JWT (stateless)** | signed token carries claims; server verifies signature, stores nothing | scales well, no lookup; **hard to revoke** before expiry; keep them short-lived + use refresh tokens |
| **OAuth2** | *delegated authorization* - "let app X access my data on service Y" without sharing the password | not authentication by itself |
| **OIDC** | identity layer on top of OAuth2 - adds an ID token for "who is this user" (Google/GitHub login) | the actual "Sign in with…" standard |

Common follow-up: *where do you store a JWT?* Prefer an `HttpOnly`, `Secure`, `SameSite` cookie
(mitigates XSS token theft) over `localStorage`. And revocation: use short access-token TTLs plus a
refresh-token flow, or a small blocklist.

---

## Password storage `[core]`

Never store plaintext or a fast hash. Use a **slow, salted** password hash - **bcrypt, scrypt, or
Argon2** - deliberately expensive to brute-force.
- **Salt** (per-user random) defeats rainbow tables and makes identical passwords hash differently.
- **Pepper** (a server-side secret) adds a layer an attacker with only the DB can't use.
- **Work factor** should scale up over time as hardware gets faster.

This is the "third category" of hashing - see the hash-vs-crypto-vs-password breakdown in
[hashing.md](hashing.md).

---

## Symmetric vs asymmetric encryption `[core]`

- **Symmetric** (AES) - one shared key for encrypt + decrypt. Fast; the hard part is *sharing the
  key* safely.
- **Asymmetric** (RSA, ECC) - public/private key pair. Encrypt with public, decrypt with private
  (or sign with private, verify with public). Slower.

They combine in **TLS**: asymmetric crypto to authenticate and exchange a key, then a fast symmetric
key for the bulk data (see the [TLS handshake in networking.md](networking.md)). **Hashing** is a
third primitive - one-way, not encryption; **HMAC** proves integrity + authenticity with a shared
key.

---

## Common attacks & defenses `[core]`

| Attack | What it is | Primary defense |
|--------|-----------|-----------------|
| **XSS** (cross-site scripting) | attacker injects JS that runs in a victim's browser | escape/encode output, Content-Security-Policy, `HttpOnly` cookies |
| **CSRF** (cross-site request forgery) | trick a logged-in user's browser into making an unwanted request | anti-CSRF tokens, `SameSite` cookies, check Origin |
| **SQL injection** | untrusted input alters a SQL query | **parameterized queries / prepared statements**, least-privilege DB user |
| **SSRF** (server-side request forgery) | make the server fetch an attacker-chosen URL (e.g. cloud metadata) | allowlist outbound hosts, block internal IP ranges |

The unifying rule: **never trust input, and separate code from data** (parameterization for SQL,
encoding for HTML). Injection-class bugs (SQLi, command injection, XSS) all stem from mixing the two.

---

## Rate limiting `[core]`

Caps how often a client can act - protects against brute-force, scraping, and abuse, and provides
backpressure. Common algorithms: **token bucket** (allows bursts), **leaky bucket** (smooths),
**fixed/sliding window** (counts per interval). Usually keyed by IP, API key, or user, backed by
Redis for a distributed counter. Return `429 Too Many Requests` with a `Retry-After` header.
System-design context: [SystemDesignGuide.md](../SystemDesign/SystemDesignGuide.md).

---

## Secrets management `[core]`

Keep credentials out of source code and images. Use a **secrets manager / vault** (HashiCorp Vault,
AWS Secrets Manager, KMS-encrypted config), inject at runtime via env vars or mounted files,
**rotate** regularly, and audit access. Committing a key to git is a real incident, not a hypothetical
- once pushed, treat it as compromised and rotate.

---

## Principles to state `[core]`

- **Defense in depth** - layered controls; one failure shouldn't be game over.
- **Least privilege** - grant the minimum access needed.
- **Fail securely** - errors default to denying access, not granting it.
- **Never trust input** - validate/sanitize everything crossing a trust boundary.
- **Don't roll your own crypto** - use vetted libraries and standards.

---

## Common interview traps

- Conflating authentication with authorization.
- Calling OAuth2 an "authentication" protocol - it's *authorization*; OIDC adds authentication.
- Hashing passwords with SHA-256 (fast = brute-forceable) instead of bcrypt/Argon2 + salt.
- Storing JWTs in `localStorage` (XSS-exposed) and having no revocation story.
- Defending SQL injection with input escaping/blocklists instead of parameterized queries.
- Treating HTTPS as "security done" - it protects transit, not stored data or app-layer bugs.

## Related

- Q&A drills: [qa-security.md](../QA-Bank/qa-security.md)
- Password hashing, HMAC, crypto-vs-table hash → [hashing.md](hashing.md)
- TLS handshake, HTTPS → [networking.md](networking.md)
- Rate limiting in system design → [SystemDesign/SystemDesignGuide.md](../SystemDesign/SystemDesignGuide.md)
