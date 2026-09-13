# Monitoring & Observability

## Overview

**Monitoring** tells you when something is wrong.  
**Observability** helps you understand **why** it's wrong.

In distributed systems, observability is critical because failures happen across multiple services, making root cause analysis challenging.

---

## 1️⃣ The Three Pillars of Observability

### **Metrics** (Numbers)
Quantitative measurements over time (CPU usage, request rate, latency)

### **Logs** (Events)
Discrete events that happened (errors, warnings, info)

### **Traces** (Requests)
Path of a request through distributed system

```
User Request → [API Gateway] → [User Service] → [Database]
                    ↓
              [Order Service] → [Payment Service] → [Stripe API]
                    ↓
              [Notification Service] → [Email Provider]
```

---

## 2️⃣ Metrics

### **Key Metrics to Track**

#### **Application Metrics:**
- **Request Rate**: Requests per second (RPS)
- **Error Rate**: Percentage of failed requests
- **Latency**: Response time (p50, p95, p99)
- **Saturation**: How "full" your service is (CPU, memory, disk)

#### **Infrastructure Metrics:**
- **CPU Usage**: % of CPU used
- **Memory Usage**: RAM consumption
- **Disk I/O**: Read/write operations per second
- **Network I/O**: Bytes sent/received

#### **Business Metrics:**
- **Active Users**: Currently online
- **Orders Created**: Per minute/hour
- **Revenue**: Dollars per minute

---

### **Two Standard Recipes: RED and USE**

Rather than inventing metrics ad hoc, use these well-known frameworks:

- **RED method** (for **request-driven services**): **R**ate (requests/sec), **E**rrors (failed requests/sec), **D**uration (latency distribution). This is the service consumer's view - "is the service serving requests well?"
- **USE method** (for **resources** like CPU, memory, disk, network): **U**tilization (% busy), **S**aturation (queued/waiting work), **E**rrors (device/op errors). This is the infra view - "is any resource maxed out?"

Rule of thumb: RED for every service endpoint, USE for every resource behind it. Together they cover both symptoms (RED) and causes (USE).

> ⚠️ **Pitfall - label cardinality explosion:** each unique combination of label values creates a separate time series. Putting high-cardinality values (user ID, request ID, raw URL with IDs) in labels can generate millions of series and overwhelm the metrics backend. Keep labels to bounded, low-cardinality dimensions (method, route template, status).

---

### **Implementing Metrics**

Instrumentation is typically a thin middleware/interceptor: define a **counter** for request totals and a **histogram** (with latency buckets) for durations, then record both on every request keyed by method/route/status. Metrics are exposed on a `/metrics` endpoint that a collector scrapes on an interval.

```text
counter   http_requests_total{method, route, status}          # increment per request
histogram http_request_duration_seconds{...} buckets=[.1,.5,1,2,5]  # observe latency
# middleware: on response-finished → counter.inc(labels); histogram.observe(labels, elapsed)
```

**The scraped metric shape (Prometheus exposition format):**
```
http_requests_total{method="GET",route="/api/users",status="200"} 1523
http_requests_total{method="GET",route="/api/users",status="500"} 12
http_request_duration_seconds_bucket{route="/api/users",le="0.5"} 1500
```
Each line is `name{labels} value` - a time series identified by its label set.

---

### **Querying Metrics (PromQL)**

```promql
# Request rate for last 5 minutes
rate(http_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate (percentage)
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# CPU usage across all instances
avg(node_cpu_usage) by (instance)
```

---

### **Visualization (Grafana)**

Dashboards turn the scraped time series into charts - request rate (line), error rate (line with threshold), latency distribution (heatmap), and resource gauges. The concrete panel/dashboard config is a tooling detail, not a design-round topic.

---

## 3️⃣ Logging

### **Structured Logging**

```text
# BAD: Unstructured logs
PRINT "User 123 created order 456 worth $99.99"

# GOOD: Structured logs (JSON)
logger = CREATE_LOGGER(format = JSON, output = FILE("app.log"))

logger.info("Order created", {
    userId: "123",
    orderId: "456",
    amount: 99.99,
    currency: "USD",
    timestamp: CURRENT_TIMESTAMP_ISO()
})
```

**Output:**
```json
{
  "level": "info",
  "message": "Order created",
  "userId": "123",
  "orderId": "456",
  "amount": 99.99,
  "currency": "USD",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Why structured?**
- ✅ Easy to search: `userId:"123"` finds all logs for user 123
- ✅ Easy to aggregate: Count orders by currency
- ✅ Machine-readable: Can be parsed by log aggregators

---

### **Log Levels**

```text
logger.error("Payment failed", { orderId: "123", error: err.message })  # Needs immediate attention
logger.warn("Slow query detected", { query: sql, duration: 5000 })      # Potential issue
logger.info("User logged in", { userId: "123" })                        # Normal operation
logger.debug("Cache hit", { key: "user:123" })                          # Debugging info
```

**Best Practices:**
- ✅ Use appropriate log levels
- ✅ Include context (userId, requestId, traceId)
- ✅ Don't log sensitive data (passwords, credit cards)
- ✅ Don't log too much (high-frequency events can overwhelm storage)

---

### **Centralized Logging (ELK Stack)**

```
Application → Filebeat → Logstash → Elasticsearch → Kibana
                            ↓
                     (Parse, filter, enrich)
```

**Example: Searching logs in Kibana**
```
# Find all errors for user 123
level:"error" AND userId:"123"

# Find slow API calls (>1 second)
duration:>1000 AND route:"/api/*"

# Count errors by service
{
  "aggs": {
    "services": {
      "terms": { "field": "service.keyword" }
    }
  },
  "query": {
    "match": { "level": "error" }
  }
}
```

---

### **Log Correlation (Request ID)**

Track single request across multiple services:

```text
# Middleware to add request ID
ON REQUEST (request, response)
    request.id = request.headers["x-request-id"] OR GENERATE_UUID()
    SET_RESPONSE_HEADER(response, "x-request-id", request.id)
    CONTINUE
END ON

# Include request ID in all logs
ON POST "/api/orders" (request, response)
    logger.info("Creating order", { requestId: request.id, userId: request.user.id })

    TRY
        order = createOrder(request.body)
        logger.info("Order created", { requestId: request.id, orderId: order.id })
        RETURN RESPONSE(200, order)
    CATCH error
        logger.error("Order creation failed", { requestId: request.id, error: error.message })
        RETURN RESPONSE(500, { error: "Internal server error" })
    END TRY
END ON

# When calling downstream service, propagate request ID
FUNCTION chargePayment(orderId, amount, requestId)
    logger.info("Charging payment", { requestId, orderId, amount })

    response = HTTP_POST("http://payment-service/charge",
        body = { orderId: orderId, amount: amount },
        headers = { "x-request-id": requestId })

    logger.info("Payment charged", { requestId, orderId, transactionId: response.id })
END FUNCTION
```

**Now you can search all logs for one request:**
```
requestId:"abc-123-def"
```

Returns logs from API Gateway, Order Service, Payment Service, etc. - complete flow!

---

## 4️⃣ Distributed Tracing

### **Why Tracing?**

Imagine this scenario:
- User reports: "Checkout is slow"
- Logs show: `POST /checkout took 5 seconds`
- But which part was slow? Database? Payment API? Email service?

**Tracing shows the breakdown:**

```
POST /checkout [5000ms]
  ├─ Validate cart [50ms]
  ├─ Create order [100ms]
  │   └─ db.orders.insert [80ms]
  ├─ Charge payment [4500ms]  ← BOTTLENECK!
  │   ├─ db.payments.insert [30ms]
  │   └─ stripe.charge [4400ms]  ← Root cause
  └─ Send confirmation email [200ms]
      └─ sendgrid.send [180ms]
```

---

### **Implementing Tracing (OpenTelemetry)**

```text
# Distributed tracing setup (pseudocode)

# Initialize tracer: batch spans and export them to the trace backend
tracerProvider = CREATE_TRACER_PROVIDER()
tracerProvider.addExporter(BATCH_EXPORTER(endpoint = "http://trace-backend:14268/api/traces"))
tracerProvider.register()

# Auto-instrument inbound/outbound HTTP so spans are created automatically
ENABLE_AUTO_INSTRUMENTATION(["http", "web-framework"])

tracer = GET_TRACER("order-service")

# Manual instrumentation for custom operations
FUNCTION createOrder(orderData)
    span = tracer.startSpan("createOrder")
    SET_SPAN_ATTRIBUTE(span, "user.id", orderData.userId)
    SET_SPAN_ATTRIBUTE(span, "order.total", orderData.total)

    TRY
        # Database operation
        dbSpan = tracer.startSpan("db.insertOrder", parent = span)
        order = DB_INSERT("orders", orderData)
        END_SPAN(dbSpan)

        # Call payment service
        paymentSpan = tracer.startSpan("chargePayment", parent = span)
        paymentService.charge({ orderId: order.id, amount: order.total })
        END_SPAN(paymentSpan)

        # Send email
        emailSpan = tracer.startSpan("sendEmail", parent = span)
        emailService.send({ to: orderData.email, template: "order_confirmation" })
        END_SPAN(emailSpan)

        SET_SPAN_STATUS(span, OK)
        RETURN order
    CATCH error
        RECORD_EXCEPTION(span, error)
        SET_SPAN_STATUS(span, ERROR, error.message)
        THROW error
    FINALLY
        END_SPAN(span)
    END TRY
END FUNCTION
```

---

### **Context Propagation**

Trace context must be passed between services via HTTP headers:

```text
# Outgoing request (trace context injected automatically by HTTP instrumentation)
FUNCTION chargePayment(orderData, parentSpan)
    # The tracing layer injects trace context into headers:
    # traceparent: 00-{trace-id}-{span-id}-01

    response = HTTP_POST("http://payment-service/charge", orderData)
    RETURN response
END FUNCTION

# Receiving service extracts trace context from headers
# and continues the trace
```

**Trace Headers (W3C Trace Context standard):**
```
traceparent: 00-<trace-id (32 hex)>-<span-id (16 hex)>-01
             version - trace ID - parent span ID - flags (01 = sampled)
```
The **trace ID** stays constant across all services in one request; each hop adds a new **span ID** whose parent is the caller's span.

---

## 5️⃣ Alerting

### **What to Alert On**

#### **Symptom-Based Alerts (User Impact):**
- ✅ High error rate (>1%)
- ✅ High latency (p95 > 2 seconds)
- ✅ Low availability (uptime < 99.9%)

#### **Cause-Based Alerts (Infrastructure):**
- ⚠️ High CPU usage (>80%)
- ⚠️ Low disk space (<10%)
- ⚠️ Database connection pool exhausted

**Prefer symptom-based alerts.** High CPU doesn't necessarily mean users are affected.

---

### **Alerting Principles**

The concrete rule/routing config (Alertmanager YAML) is tooling detail. What matters in a design discussion:

- **Alert on symptoms, not causes.** Page on user-visible pain (error rate, p95 latency, availability), not on every high-CPU blip. High CPU that doesn't hurt users isn't worth waking someone up.
- **Route by severity.** `critical` → PagerDuty (wake the on-call), `warning` → Slack/ticket (handle in business hours). An alert with no clear owner or action is noise.
- **Avoid alert fatigue.** Group related alerts, add `for:` durations so brief blips self-heal without paging, and delete alerts nobody acts on. If everything pages, on-call learns to ignore alerts.

---

## 6️⃣ Health Checks

### **Liveness Probe**

Is the service alive? If not, restart it.

```text
# Simple liveness check
ON GET "/health/live" (request, response)
    RETURN RESPONSE(200, { status: "ok" })
END ON

# The orchestrator will restart the instance if this fails
```

---

### **Readiness Probe**

Is the service ready to receive traffic? If not, don't send requests.

```text
# Check dependencies before accepting traffic
ON GET "/health/ready" (request, response)
    TRY
        DB_QUERY("SELECT 1")   # Test database
        CACHE_PING()           # Test cache
        RETURN RESPONSE(200, { status: "ready" })
    CATCH error
        RETURN RESPONSE(503, { status: "not ready", error: error.message })
    END TRY
END ON

# The orchestrator won't send traffic until this returns 200
```

---

### **Liveness vs Readiness**

A **liveness** probe failing means the instance is broken and should be **restarted**; a **readiness** probe failing means the instance is temporarily unable to serve (e.g., a dependency is down or it's still warming up) and should be **pulled from the load balancer** without being killed. The orchestrator polls both on an interval with a failure threshold before acting.

---

## 7️⃣ Observability Stack Example

### **Full Stack**

```
┌───────────────────────────────────────────────┐
│            Application Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Service1 │  │ Service2 │  │ Service3 │    │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘    │
│        │             │             │          │
│   Metrics       Logs         Traces           │
└────────┼─────────────┼─────────────┼──────────┘
         │             │             │
         ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Prometheus  │ │    ELK      │ │   Jaeger    │
│  (Metrics)  │ │   (Logs)    │ │  (Traces)   │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┴───────────────┘
                       │
                       ▼
               ┌─────────────┐
               │   Grafana   │
               │ (Dashboards)│
               └─────────────┘
```

---

### **Unified Observability (Modern Approach)**

```
Application → OpenTelemetry Collector → Backend
               (Metrics, Logs, Traces)

Backends:
- Datadog
- New Relic
- Honeycomb
- Grafana Cloud (Loki + Tempo + Mimir)
```

**Benefits:**
- ✅ Single SDK (OpenTelemetry)
- ✅ Vendor-neutral
- ✅ Correlate metrics, logs, traces in one view

---

## 8️⃣ Best Practices

### **1. Use Correlation IDs**

Link metrics, logs, and traces with same request ID.

```text
logger.info("Order created", {
    traceId: SPAN_CONTEXT(span).traceId,
    orderId: order.id
})
```

Now you can:
1. See error in logs (traceId: abc-123)
2. Click to view full trace in Jaeger
3. See all metrics for that request

---

### **2. Sample Traces**

Don't trace 100% of requests (too expensive). Sample based on:
- Traffic volume (1% of requests if high traffic)
- Errors (always trace failed requests)
- Slow requests (always trace if latency > threshold)

```text
sampler = RATIO_BASED_SAMPLER(0.01)   # 1% sampling

# Or: Sample all errors / slow requests
IF error OR duration > 1000 THEN
    FORCE_SAMPLE()   # Always sample
END IF
```

---

### **3. Monitor the Four Golden Signals**

From Google's SRE book:

1. **Latency**: How long requests take
2. **Traffic**: How many requests
3. **Errors**: Rate of failed requests
4. **Saturation**: How "full" your service is (CPU, memory, disk)

**Watch tail latency (p99), not just the average.** Averages hide the slow requests that hurt real users. Tail latency matters because of **fan-out amplification**: when one request fans out to many services (or one service makes many parallel backend calls) and must wait for *all* of them, the overall latency is governed by the **slowest** response. If each of 100 backends is fast 99% of the time, the chance that *at least one* is slow on any given request is ~63% - so a rare per-call p99 becomes the *common* case at the top level. One slow dependency blows up the whole request's p99, which is why you optimize and alert on tails.

---

### **4. Set SLOs (Service Level Objectives)**

```
Availability SLO: 99.9% (43 minutes/month downtime allowed)
Latency SLO: 95% of requests < 500ms
Error Rate SLO: < 0.1%
```

Alert when SLO is at risk (don't wait for 100% breach).

**Error budgets - the actionable half of an SLO.** A 99.9% availability SLO permits 0.1% failure; that 0.1% is your **error budget** for the period (~43 min/month). It turns reliability into a spendable number: if the budget is healthy, ship features fast; if it's nearly exhausted, freeze risky changes and focus on stability. It also depersonalizes the dev-vs-ops tension - the budget, not opinion, decides when to slow down.

---

## Summary

**Metrics**: What is broken?  
**Logs**: Why is it broken?  
**Traces**: Where is it broken?

**Essential Tools:**
- Prometheus + Grafana (metrics)
- ELK Stack or Loki (logs)
- Jaeger or Tempo (traces)
- Alertmanager (alerts)

**Key Practices:**
- ✅ Use structured logging
- ✅ Track request IDs across services
- ✅ Instrument critical paths
- ✅ Alert on symptoms, not causes
- ✅ Monitor the four golden signals
- ✅ Set and track SLOs
