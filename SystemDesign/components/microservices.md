# Microservices Architecture

## Overview

Microservices architecture splits a monolithic application into small, independent services that communicate over the network. Each service owns its data and can be deployed independently.

---

## 1️⃣ Monolith vs Microservices

### **Monolithic Architecture**

```
┌─────────────────────────────────────────────┐
│         Single Application                   │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Auth   │  │ Payments │  │ Products │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│         Single Database                      │
│  ┌──────────────────────────────────────┐   │
│  │     users | products | orders        │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Pros:**
- ✅ Simple to develop and deploy
- ✅ Easy to test (everything in one place)
- ✅ No network latency between components

**Cons:**
- ❌ Tight coupling (change in one module affects others)
- ❌ Hard to scale (must scale entire app, not individual parts)
- ❌ Long deployment cycles (entire app must be redeployed)
- ❌ Technology lock-in (entire app uses same stack)

---

### **Microservices Architecture**

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Auth      │   │  Payments   │   │  Products   │
│   Service   │   │   Service   │   │   Service   │
│             │   │             │   │             │
│ ┌─────────┐ │   │ ┌─────────┐ │   │ ┌─────────┐ │
│ │  Users  │ │   │ │Payments │ │   │ │Products │ │
│ │   DB    │ │   │ │   DB    │ │   │ │   DB    │ │
│ └─────────┘ │   │ └─────────┘ │   │ └─────────┘ │
└─────────────┘   └─────────────┘   └─────────────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                 API Gateway
```

**Pros:**
- ✅ Independent deployment (update one service without affecting others)
- ✅ Independent scaling (scale only what's needed)
- ✅ Technology flexibility (each service can use different stack)
- ✅ Fault isolation (failure in one service doesn't crash entire system)
- ✅ Team autonomy (different teams own different services)

**Cons:**
- ❌ Distributed system complexity (network failures, latency)
- ❌ Data consistency challenges (no ACID transactions across services)
- ❌ Testing complexity (integration tests harder)
- ❌ Operational overhead (deploy/monitor many services)

---

## Service Boundaries — Where to Split

The hardest part of microservices isn't the tech, it's deciding **where the seams go**.

- **Split by business capability / DDD bounded context.** Each service should own one cohesive area of the domain (e.g., Payments, Inventory, Notifications) and its data. A good boundary changes for one business reason and rarely needs to be edited alongside another service.
- **High cohesion, low coupling.** Things that change together belong together. If a "feature" constantly requires coordinated edits across three services, the boundary is wrong.
- ⚠️ **Anti-pattern — the "distributed monolith":** services are split physically but remain tightly coupled (chatty synchronous calls, shared database, lock-step deploys). You pay all the operational cost of distribution with none of the independence. If services can't deploy independently, they aren't really separate.

---

## 2️⃣ Microservices Communication Patterns

### **Pattern 1: Synchronous (HTTP/REST, gRPC)**

```text
# Order Service calls Payment Service via HTTP

FUNCTION createOrder(request)
    order = DB_CREATE("orders", request.body)

    # Synchronous call to Payment Service
    paymentResponse = HTTP_POST("http://payment-service/api/charge", {
        orderId: order.id,
        amount: order.total,
        userId: order.userId
    })

    IF paymentResponse.status == "success" THEN
        order.status = "PAID"
        DB_SAVE(order)
        RETURN RESPONSE(200, { success: true, orderId: order.id })
    ELSE
        RETURN RESPONSE(400, { error: "Payment failed" })
    END IF
END FUNCTION
```

**Pros:**
- ✅ Simple (request-response)
- ✅ Immediate result

**Cons:**
- ❌ Tight coupling (caller waits for response)
- ❌ Cascading failures (if payment service is down, order service fails)
- ❌ Higher latency (network roundtrip)

---

### **Pattern 2: Asynchronous (Message Queue/Event Bus)**

```text
# Order Service publishes event, Payment Service subscribes

# Order Service
FUNCTION createOrder(request)
    order = DB_CREATE("orders", MERGE(request.body, { status: "PENDING" }))

    # Publish event (non-blocking)
    PUBLISH("order.created", {
        orderId: order.id,
        userId: order.userId,
        amount: order.total
    })

    # Return immediately
    RETURN RESPONSE(200, { success: true, orderId: order.id, status: "PENDING" })
END FUNCTION

# Payment Service (separate process)
ON EVENT("order.created") AS event
    orderId = event.orderId
    userId  = event.userId
    amount  = event.amount

    paymentResult = chargeUser(userId, amount)

    # Publish result
    PUBLISH("payment.processed", {
        orderId: orderId,
        status: paymentResult.status
    })
END ON

# Order Service listens for payment result
ON EVENT("payment.processed") AS event
    DB_UPDATE("orders", event.orderId, {
        status: IF event.status == "success" THEN "PAID" ELSE "FAILED"
    })
END ON
```

**Pros:**
- ✅ Loose coupling (services don't need to know about each other)
- ✅ Resilient (if payment service is down, message queued for later)
- ✅ Scalable (can process events in parallel)

**Cons:**
- ❌ Eventual consistency (order status updates asynchronously)
- ❌ Complexity (need message broker infrastructure)
- ❌ Debugging harder (distributed traces needed)

---

## 3️⃣ Key Components

### **A. API Gateway**

Single entry point for all clients. Routes requests to appropriate microservices.

```text
# API Gateway (pseudocode)

# Route each path prefix to the matching backend service
ROUTE "/api/users"    -> PROXY TO "http://user-service:3001"
ROUTE "/api/products" -> PROXY TO "http://product-service:3002"
ROUTE "/api/orders"   -> PROXY TO "http://order-service:3003"

# Cross-cutting concerns applied to every request
USE authenticationMiddleware   # Centralized auth
USE rateLimitMiddleware        # Rate limiting
USE loggingMiddleware          # Request logging

LISTEN ON port 80
```

**Responsibilities:**
- Routing
- Authentication/Authorization
- Rate limiting
- Request/Response transformation
- Protocol translation (REST → gRPC)
- Caching

---

### **B. Service Discovery**

Services register themselves and discover other services dynamically.

```text
# Service registry + discovery (pseudocode)

# Service Registration (on startup)
FUNCTION registerService()
    REGISTRY_REGISTER({
        name: "user-service",
        address: "10.0.1.5",
        port: 3001,
        healthCheck: {
            url: "http://10.0.1.5:3001/health",
            interval: "10s"
        }
    })
    PRINT "Service registered"
END FUNCTION

# Service Discovery (when calling another service)
FUNCTION callPaymentService(data)
    # Get available healthy instances
    services = REGISTRY_LOOKUP("payment-service")

    # Pick one (load balance)
    instance = services[RANDOM_INDEX(services)]

    # Call it
    response = HTTP_POST("http://" + instance.address + ":" + instance.port + "/charge", data)

    RETURN response
END FUNCTION
```

**Popular Tools:**
- Consul
- Eureka (Netflix)
- etcd
- ZooKeeper

---

### **C. Load Balancer**

Distributes traffic across multiple service instances. Common strategies: Round Robin, Least Connections, Weighted Round Robin, IP Hash, Random.

> 📌 See **components/load-balancer.md** for load balancing algorithms and trade-offs.

---

### **D. Circuit Breaker**

Prevents cascading failures when a downstream service is failing. The breaker wraps calls to a dependency and tracks failures. It has three states:

- **CLOSED**: normal operation, requests pass through and failures are counted.
- **OPEN**: after N consecutive failures the breaker trips; requests fail fast (no wait) and a fallback is served, giving the downstream time to recover.
- **HALF-OPEN**: after a cooldown, a few trial requests are allowed. Success → CLOSED; failure → back to OPEN.

**Trade-off:** protects the system from wasting resources on a dead dependency and stops failure from spreading, at the cost of tuning thresholds/timeouts (too sensitive = false trips, too lax = slow to protect).

---

### **E. Saga Pattern (Distributed Transactions)**

Handle transactions across multiple services without 2-phase commit. A saga is a sequence of local transactions; if one step fails, earlier steps are undone by **compensating transactions** (e.g., refund a charge, release a reservation). There are two coordination styles.

**Choreography (event-driven):** each service reacts to events and emits its own, no central coordinator.

```text
# Each service listens and reacts, publishing the next event
Order      → PUBLISH order.created
Payment    → ON order.created → charge → PUBLISH payment.success | payment.failed
Inventory  → ON payment.success → reserve → PUBLISH inventory.reserved | inventory.failed
Payment    → ON inventory.failed → refund (compensating) → PUBLISH payment.refunded
Order      → ON inventory.reserved → status = CONFIRMED
           → ON payment.refunded  → status = CANCELLED
```

**Orchestration:** a central orchestrator drives the steps explicitly — call payment, then inventory, then shipping — and on any failure it invokes the compensations in reverse order. The flow lives in one place instead of being spread across event handlers.

**Trade-off:** choreography is **decoupled** (services don't know about each other) but the end-to-end flow is **hard to trace and reason about** — no single place shows the whole saga. Orchestration gives **central visibility and control** but the coordinator is a **single point of failure** and a source of coupling.

---

## 4️⃣ Data Management

### **Database per Service**

Each microservice owns its database.

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   User      │   │  Order      │   │  Payment    │
│   Service   │   │  Service    │   │   Service   │
│             │   │             │   │             │
│ ┌─────────┐ │   │ ┌─────────┐ │   │ ┌─────────┐ │
│ │  Users  │ │   │ │ Orders  │ │   │ │Payments │ │
│ │   DB    │ │   │ │   DB    │ │   │ │   DB    │ │
│ └─────────┘ │   │ └─────────┘ │   │ └─────────┘ │
└─────────────┘   └─────────────┘   └─────────────┘

❌ No direct database access across services
✅ Only communicate via APIs or events
```

**Why?**
- ✅ Independent scaling (different databases optimized for different workloads)
- ✅ Technology flexibility (PostgreSQL for relational, MongoDB for documents)
- ✅ Fault isolation (database failure doesn't affect other services)

**Challenges:**
- ❌ No JOIN queries across services
- ❌ Data duplication (eventual consistency)

---

### **Event Sourcing**

Instead of storing current state, store the full sequence of immutable events that led to it (e.g., `AccountCreated`, `MoneyDeposited`, `MoneyWithdrawn`). Current state is derived by replaying events; snapshots avoid replaying from the beginning every time.

> **Note:** gives a complete audit trail, time-travel, and the ability to replay with corrected logic — but querying "current state" now requires a projection.

> ⚠️ **Caution:** Event Sourcing is advanced and often over-engineering. Reach for it only when an immutable audit trail or event replay is a real requirement (finance, ledgers, compliance) — not by default.

---

### **CQRS (Command Query Responsibility Segregation)**

Separate the **write model** (commands that mutate state / emit events) from the **read model** (denormalized views optimized for queries). Reads and writes use different data models, often different stores, kept in sync via events. This lets you scale and optimize each side independently.

> **Note:** frequently paired with Event Sourcing, but the two are independent choices.

> ⚠️ **Caution:** CQRS adds eventual consistency and operational complexity. Use it only when read and write workloads are genuinely asymmetric (very high read volume, or complex query shapes the write model can't serve) — otherwise a single model is simpler and correct.

---

## 5️⃣ Deployment Patterns

### **Container Orchestration (Kubernetes)**

Services are packaged as containers and deployed **declaratively** (desired state, not manual steps). The orchestrator runs N **replicas** behind a stable service address and uses **health checks** to restart or reschedule unhealthy instances. This gives auto-scaling (HPA), self-healing, service discovery, and rolling (zero-downtime) updates — the operational detail is out of scope for a design round.

---

## 6️⃣ Monitoring & Observability

Distributed systems need request-level visibility across service hops to find where latency and errors originate.

> 📌 See **Distributed Tracing** in **components/monitoring.md** (canonical home for tracing, metrics, and logging).

---

## Summary

**Microservices Are Right When:**
- ✅ Large team (50+ engineers)
- ✅ Need independent scaling
- ✅ Different parts of system have different tech requirements
- ✅ Frequent deployments

**Stick with Monolith When:**
- ✅ Small team (<10 engineers)
- ✅ Simple application
- ✅ Early-stage product (iterate fast)

**Key Takeaways:**
- 🔹 Start with monolith, extract microservices when needed
- 🔹 Each service owns its data
- 🔹 Communicate via APIs or events
- 🔹 Use API Gateway as single entry point
- 🔹 Implement circuit breakers to prevent cascading failures
- 🔹 Use Saga pattern for distributed transactions
- 🔹 Monitor with distributed tracing
