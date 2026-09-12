# Microservices Architecture

## 🎯 Overview

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

Distributes traffic across multiple service instances.

```text
# Client-side load balancing with Round Robin

CLASS LoadBalancer
    FUNCTION init(services)
        this.services = services   # list of service base URLs
        this.currentIndex = 0
    END FUNCTION

    FUNCTION getNextService()
        service = this.services[this.currentIndex]
        this.currentIndex = (this.currentIndex + 1) MOD LENGTH(this.services)
        RETURN service
    END FUNCTION

    FUNCTION request(path, data)
        service = this.getNextService()
        RETURN HTTP_POST(service + path, data)
    END FUNCTION
END CLASS

lb = new LoadBalancer([
    "http://payment-service-1:3000",
    "http://payment-service-2:3000",
    "http://payment-service-3:3000"
])

# Usage
lb.request("/charge", { amount: 100 })
```

**Load Balancing Strategies:**
- Round Robin
- Least Connections
- Weighted Round Robin
- IP Hash
- Random

---

### **D. Circuit Breaker**

Prevents cascading failures when downstream service is failing.

```text
CLASS CircuitBreaker
    FUNCTION init(serviceCall, options = {})
        this.serviceCall = serviceCall
        this.failureThreshold = options.failureThreshold OR 5
        this.timeout = options.timeout OR 60000
        this.state = "CLOSED"          # CLOSED, OPEN, HALF_OPEN
        this.failureCount = 0
        this.nextAttempt = NOW()
    END FUNCTION

    FUNCTION execute(args...)
        IF this.state == "OPEN" THEN
            IF NOW() < this.nextAttempt THEN
                THROW Error("Circuit breaker is OPEN")
            END IF
            this.state = "HALF_OPEN"
        END IF

        TRY
            result = this.serviceCall(args...)
            this.onSuccess()
            RETURN result
        CATCH error
            this.onFailure()
            THROW error
        END TRY
    END FUNCTION

    FUNCTION onSuccess()
        this.failureCount = 0
        this.state = "CLOSED"
    END FUNCTION

    FUNCTION onFailure()
        this.failureCount = this.failureCount + 1
        IF this.failureCount >= this.failureThreshold THEN
            this.state = "OPEN"
            this.nextAttempt = NOW() + this.timeout
        END IF
    END FUNCTION
END CLASS

# Usage
paymentServiceCall = FUNCTION(data) RETURN HTTP_POST("http://payment-service/charge", data) END
breaker = new CircuitBreaker(paymentServiceCall, { failureThreshold: 3 })

TRY
    result = breaker.execute({ amount: 100 })
CATCH error
    # Fallback logic
    PRINT "Payment service unavailable, using fallback"
END TRY
```

**States:**
- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Service failing, requests immediately fail (fast fail)
- **HALF_OPEN**: Testing if service recovered, limited requests allowed

---

### **E. Saga Pattern (Distributed Transactions)**

Handle transactions across multiple services without 2-phase commit.

```text
# Choreography-based Saga (event-driven)

# Order Service
FUNCTION createOrder(orderData)
    order = DB_CREATE("orders", MERGE(orderData, { status: "PENDING" }))

    PUBLISH("order.created", {
        orderId: order.id,
        userId: orderData.userId,
        items: orderData.items,
        total: orderData.total
    })
END FUNCTION

# Payment Service
ON EVENT("order.created") AS event
    TRY
        chargeUser(event.userId, event.total)
        PUBLISH("payment.success", { orderId: event.orderId })
    CATCH error
        PUBLISH("payment.failed", { orderId: event.orderId, reason: error.message })
    END TRY
END ON

# Inventory Service
ON EVENT("payment.success") AS event
    TRY
        reserveItems(event.orderId)
        PUBLISH("inventory.reserved", { orderId: event.orderId })
    CATCH error
        # Compensating transaction: refund payment
        PUBLISH("inventory.reservation.failed", { orderId: event.orderId })
    END TRY
END ON

# Payment Service (compensating transaction)
ON EVENT("inventory.reservation.failed") AS event
    refundUser(event.orderId)
    PUBLISH("payment.refunded", { orderId: event.orderId })
END ON

# Order Service (update final status)
ON EVENT("inventory.reserved") AS event
    DB_UPDATE("orders", event.orderId, { status: "CONFIRMED" })
END ON

ON EVENT("payment.refunded") AS event
    DB_UPDATE("orders", event.orderId, { status: "CANCELLED" })
END ON
```

**Alternative: Orchestration-based Saga**

```text
# Order Orchestrator coordinates the saga

CLASS OrderSaga
    FUNCTION execute(orderData)
        order = DB_CREATE("orders", MERGE(orderData, { status: "PENDING" }))

        TRY
            # Step 1: Charge payment
            paymentService.charge({
                userId: orderData.userId,
                amount: orderData.total
            })

            # Step 2: Reserve inventory
            inventoryService.reserve({
                orderId: order.id,
                items: orderData.items
            })

            # Step 3: Ship order
            shippingService.scheduleShipment({
                orderId: order.id,
                address: orderData.address
            })

            # Success
            DB_UPDATE("orders", order.id, { status: "CONFIRMED" })
            RETURN { success: true, orderId: order.id }

        CATCH error
            # Compensate (rollback)
            this.compensate(order.id)
            THROW error
        END TRY
    END FUNCTION

    FUNCTION compensate(orderId)
        # Reverse in opposite order
        shippingService.cancelShipment(orderId)
        inventoryService.releaseReservation(orderId)
        paymentService.refund(orderId)
        DB_UPDATE("orders", orderId, { status: "CANCELLED" })
    END FUNCTION
END CLASS
```

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

Store all changes as immutable events instead of current state.

```text
# Traditional approach: Store current state
DB_UPDATE("accounts", accountId, { balance: 500 })

# Event Sourcing: Store all events
EVENT_STORE_APPEND("account-123", [
    { type: "AccountCreated", balance: 0, timestamp: "2024-01-01" },
    { type: "MoneyDeposited", amount: 1000, timestamp: "2024-01-02" },
    { type: "MoneyWithdrawn", amount: 500, timestamp: "2024-01-03" }
])

# Rebuild current state by replaying events
FUNCTION getCurrentBalance(events)
    balance = 0
    FOR EACH event IN events
        SWITCH event.type
            CASE "AccountCreated":  balance = event.balance
            CASE "MoneyDeposited":  balance = balance + event.amount
            CASE "MoneyWithdrawn":  balance = balance - event.amount
            DEFAULT:                # no change
        END SWITCH
    END FOR
    RETURN balance
END FUNCTION

events = EVENT_STORE_GET("account-123")
currentBalance = getCurrentBalance(events)   # 500
```

**Benefits:**
- ✅ Complete audit trail
- ✅ Time travel (rebuild state at any point in time)
- ✅ Event replay (fix bugs by replaying with corrected logic)

---

### **CQRS (Command Query Responsibility Segregation)**

Separate read and write models.

```text
# Write Model (Commands)
CLASS OrderService
    FUNCTION createOrder(orderData)
        event = MERGE({
            type: "OrderCreated",
            orderId: GENERATE_UUID(),
            timestamp: NOW()
        }, orderData)

        EVENT_STORE_APPEND(event.orderId, [event])
        PUBLISH("order.created", event)
    END FUNCTION
END CLASS

# Read Model (Queries) - separate database optimized for reads
ON EVENT("order.created") AS event
    # Update read-optimized view
    READ_DB_INSERT("orders", {
        orderId: event.orderId,
        userId: event.userId,
        total: event.total,
        status: "PENDING",
        createdAt: event.timestamp
    })
END ON

# Query from read model
FUNCTION getOrderHistory(userId)
    RETURN READ_DB_FIND("orders", { userId: userId }) SORTED BY createdAt DESCENDING
END FUNCTION
```

**Benefits:**
- ✅ Optimize read and write separately
- ✅ Scale reads independently (read replicas)
- ✅ Denormalize data for fast queries

---

## 5️⃣ Deployment Patterns

### **Container Orchestration (Kubernetes)**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3  # Run 3 instances
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: myregistry/user-service:v1.2.3
        ports:
        - containerPort: 3000
        env:
        - name: DB_HOST
          value: postgres-service
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

**Kubernetes Features:**
- Auto-scaling (HPA - Horizontal Pod Autoscaler)
- Self-healing (restart failed containers)
- Load balancing
- Service discovery
- Rolling updates (zero downtime)

---

## 6️⃣ Monitoring & Observability

### **Distributed Tracing**

Track requests across multiple services.

```text
# Distributed tracing (pseudocode)
# tracer is scoped to the "order-service"

FUNCTION createOrder(orderData)
    # Start span
    span = START_SPAN("createOrder")
    SET_SPAN_ATTRIBUTE(span, "user.id", orderData.userId)
    SET_SPAN_ATTRIBUTE(span, "order.total", orderData.total)

    TRY
        # Save order
        order = DB_CREATE("orders", orderData)

        # Call payment service (propagate trace context as a child span)
        paymentSpan = START_SPAN("chargePayment", parent = span)
        paymentService.charge({ orderId: order.id, amount: order.total })
        END_SPAN(paymentSpan)

        SET_SPAN_STATUS(span, OK)
        RETURN order
    CATCH error
        SET_SPAN_STATUS(span, ERROR, error.message)
        THROW error
    FINALLY
        END_SPAN(span)
    END TRY
END FUNCTION
```

**Visualize with Jaeger:**
```
createOrder [200ms]
  ├─ db.orders.create [50ms]
  ├─ chargePayment [120ms]
  │   ├─ db.payments.create [30ms]
  │   └─ stripe.charge [80ms]
  └─ eventBus.publish [10ms]
```

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
