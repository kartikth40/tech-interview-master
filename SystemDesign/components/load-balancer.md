# Load Balancer (Component Deep Dive)

## 🎯 What is a Load Balancer?

A load balancer distributes incoming network traffic across multiple servers to ensure no single server bears too much load, improving:
- **Availability** - If one server fails, traffic routes to healthy servers
- **Scalability** - Add more servers to handle increased load
- **Performance** - Distribute load evenly, reduce latency

---

## 📊 Types of Load Balancers

### 1. **Hardware Load Balancer**
```
Examples: F5, Citrix NetScaler
Pros: High performance, dedicated hardware
Cons: Expensive, difficult to scale
Use: Enterprise data centers
```

### 2. **Software Load Balancer**
```
Examples: HAProxy, NGINX, Envoy
Pros: Flexible, cost-effective, easy to scale
Cons: Runs on commodity hardware
Use: Modern cloud applications ⭐
```

### 3. **Cloud Load Balancer**
```
Examples: AWS ELB/ALB, Google Cloud Load Balancer, Azure Load Balancer
Pros: Fully managed, auto-scaling
Cons: Vendor lock-in, cost
Use: Cloud-native applications ⭐
```

---

## 🔧 Load Balancer Layers (OSI Model)

### **Layer 4 (Transport Layer) Load Balancer**

**How it works:**
- Operates at TCP/UDP level
- Routes based on IP address and port
- Does NOT inspect HTTP headers or content

**Pros:**
- ✅ Very fast (no packet inspection)
- ✅ Lower latency
- ✅ Protocol agnostic (HTTP, FTP, SMTP, etc.)

**Cons:**
- ❌ Less intelligent routing (can't route based on URL)
- ❌ No session persistence based on cookies
- ❌ Can't make content-based decisions

**Example:**
```
Client → Load Balancer (TCP 443) → Server 1 (10.0.0.1:443)
                                 → Server 2 (10.0.0.2:443)
                                 → Server 3 (10.0.0.3:443)
```

**Use Cases:**
- High-throughput applications
- Non-HTTP protocols (SMTP, FTP, database connections)
- When speed is critical

---

### **Layer 7 (Application Layer) Load Balancer**

**How it works:**
- Operates at HTTP/HTTPS level
- Inspects HTTP headers, URLs, cookies
- Makes intelligent routing decisions based on content

**Pros:**
- ✅ Content-based routing (/api → API servers, /static → CDN)
- ✅ SSL termination
- ✅ Session persistence (sticky sessions)
- ✅ A/B testing, canary deployments

**Cons:**
- ❌ Slower (packet inspection overhead)
- ❌ Higher CPU usage
- ❌ HTTP-specific

**Example:**
```
Client → Load Balancer inspects URL:
  - /api/users → API Server Pool
  - /images   → Static File Server Pool
  - /admin    → Admin Server Pool
```

**Use Cases:**
- Microservices architectures
- Content-based routing
- SSL offloading
- Modern web applications ⭐

---

## ⚖️ Load Balancing Algorithms

### 1. **Round Robin**
```
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1 (cycle back)
```

**Pros:** Simple, fair distribution  
**Cons:** Doesn't account for server load  
**Use:** Servers have equal capacity

---

### 2. **Weighted Round Robin**
```
Server 1 (weight=3): Gets 3 requests
Server 2 (weight=2): Gets 2 requests
Server 3 (weight=1): Gets 1 request
```

**Pros:** Accounts for different server capacities  
**Cons:** Static weights  
**Use:** Heterogeneous server fleet

---

### 3. **Least Connections**
```
Server 1 (10 active connections) ← Route here
Server 2 (50 active connections)
Server 3 (30 active connections)
```

**Pros:** Dynamic, accounts for active load  
**Cons:** More complex to track  
**Use:** Long-lived connections (WebSockets, databases)

---

### 4. **Weighted Least Connections**
```
Combine least connections + server capacity weights
Score = active_connections / weight

Server 1 (10 connections, weight=2): Score = 5
Server 2 (20 connections, weight=5): Score = 4 ← Route here
Server 3 (15 connections, weight=3): Score = 5
```

**Pros:** Best of both worlds  
**Cons:** Most complex  
**Use:** Production systems with varying server capacities ⭐

---

### 5. **IP Hash (Session Affinity)**
```text
FUNCTION select_server(client_ip, servers):
    hash = murmurhash(client_ip)
    index = hash MOD length(servers)
    RETURN servers[index]

# Same client always routed to same server
Client 192.168.1.100 -> Server 2 (always)
```

**Pros:** Session persistence without cookies  
**Cons:** Uneven distribution if clients concentrated  
**Use:** Stateful applications, session management

---

### 6. **Least Response Time**
```
Server 1 (avg 50ms response time) ← Route here
Server 2 (avg 200ms response time)
Server 3 (avg 150ms response time)
```

**Pros:** Optimizes for latency  
**Cons:** Requires health checks, metrics  
**Use:** Geo-distributed servers

---

## 🏥 Health Checks

```text
# Active Health Check (Proactive)
FUNCTION health_check(server):
    TRY:
        response = HTTP GET server.url + "/health"  (timeout 2000 ms)
        RETURN response.status == 200
    CATCH error:
        RETURN false

# Run every 10 seconds
EVERY 10 seconds:
    FOR EACH server IN servers:
        server.healthy = health_check(server)

# Passive Health Check (Reactive)
FUNCTION handle_request(req, server):
    IF server.consecutive_failures >= 3:
        server.healthy = false
        # Remove from rotation for 60 seconds, then restore
        AFTER 60 seconds: server.healthy = true
```

**Metrics to Monitor:**
- Response status (200 OK vs 500 error)
- Response time (timeout after 2-5 seconds)
- Consecutive failures (mark unhealthy after 3 failures)
- Success rate (remove if <95%)

---

## 🔒 SSL Termination

```
Client (HTTPS) → Load Balancer (SSL terminated) → Servers (HTTP)

Benefits:
✅ Offload CPU-intensive encryption from backend servers
✅ Centralized certificate management
✅ Easier to update SSL certificates
✅ Faster server response times

Drawback:
❌ Traffic between LB and servers is unencrypted (use VPC/private network)
```

---

## 📝 Session Persistence (Sticky Sessions)

### **Problem:**
User logs in → Session stored on Server 1 → Next request goes to Server 2 → User appears logged out

### **Solutions:**

#### 1. **Cookie-Based Stickiness**
```text
# Load balancer sets cookie
Set-Cookie: SERVER_ID=server1; Path=/

# Client includes cookie in subsequent requests
Cookie: SERVER_ID=server1

# Load balancer reads cookie, routes to server1
```

#### 2. **IP Hash Stickiness**
```text
# Same client IP always -> same server
hash(client_ip) MOD num_servers = server_index
```

#### 3. **Session Store (Better)** ⭐
```text
# Store session in a shared store (e.g. Redis)
session = SHARED_STORE.get("session:" + session_id)

# Any server can handle any request
# No need for sticky sessions
```

---

## 🌍 Global Load Balancing (DNS-Based)

```
User in US → us-east-1.example.com
User in EU → eu-west-1.example.com
User in Asia → ap-southeast-1.example.com

DNS returns different IP based on:
- Geographic location (latency-based)
- Health of data centers
- Weighted distribution
```

**Tools:**
- AWS Route 53 (latency-based routing)
- Google Cloud Load Balancer (global anycast)
- Cloudflare (geo-routing)

---

## 🔧 Configuration (conceptual)

A Layer-7 balancer (NGINX/HAProxy/Envoy) is configured with:
- An **upstream pool** of backend servers, each with an optional **weight** (higher weight = more traffic) and **backup** servers used only when the primaries fail.
- **Content-based routing** by path (`/api/*` → API pool, `/static/*` → CDN/static pool) or header.
- A lightweight **health-check endpoint** the balancer polls to decide which backends are in rotation.

(Exact vendor config syntax isn't what an interview tests - the routing + health-check + weighting concepts are.)

---

## 📊 Comparison Matrix

| Algorithm | Pros | Cons | Best For |
|-----------|------|------|----------|
| Round Robin | Simple, fair | Ignores load | Equal servers |
| Weighted RR | Accounts for capacity | Static weights | Mixed capacities |
| Least Connections | Dynamic load balance | Complex tracking | Long connections |
| IP Hash | Session persistence | Uneven distribution | Stateful apps |
| Least Response Time | Low latency | Requires metrics | Geo-distributed |

---

## ⚠️ Common Pitfalls

| Problem | Solution |
|---------|----------|
| **Single point of failure** | Use multiple load balancers (active-passive or active-active) |
| **Session loss** | Use shared session store (Redis) instead of sticky sessions |
| **Overloaded server** | Implement circuit breaker pattern, rate limiting |
| **Slow health checks** | Use passive health checks + active checks |
| **SSL overhead** | Terminate SSL at load balancer |

---

## 🚀 Advanced Features

### 1. **Rate Limiting**
The balancer can rate-limit per client (e.g. keyed by source IP) - a sustained rate (e.g. 10 req/s)
with a small **burst** allowance - before requests ever reach the backends. (See token-bucket vs
sliding-window in [SystemDesignGuide.md](../SystemDesignGuide.md).)

### 2. **Request Routing**
```
Route based on:
- URL path (/api → API servers, /admin → Admin servers)
- HTTP headers (User-Agent: mobile → mobile backend)
- Query parameters (version=v2 → new backend)
- Cookies (A/B testing)
```

### 3. **Blue-Green Deployment**
```
Blue (current): 100% traffic
Green (new): 0% traffic

→ Deploy green, test
→ Shift 10% traffic to green
→ Monitor errors
→ Shift 100% traffic to green
→ Blue becomes standby
```

---

## 📈 Monitoring Metrics

```
Key metrics to track:
- Request rate (req/sec)
- Response time (P50, P95, P99)
- Error rate (4xx, 5xx)
- Active connections per server
- Server health status
- SSL handshake time
- Throughput (MB/s)
```

---

## Summary

**Load Balancer is essential for:**
- ✅ High availability (failover)
- ✅ Horizontal scalability (add more servers)
- ✅ Performance (distribute load)
- ✅ Flexibility (content-based routing)

**Best Practices:**
- Use Layer 7 for HTTP/HTTPS applications
- Implement health checks (both active and passive)
- Use shared session storage instead of sticky sessions
- Monitor metrics continuously
- Have redundant load balancers
- Use weighted algorithms for heterogeneous servers

**Next Steps:**
- Learn about [Caching](caching.md) for performance
- Understand [Database Sharding](database-sharding.md) for scale
