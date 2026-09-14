# API Design Patterns

## Overview

Choosing the right API style is a common system design discussion. This guide covers REST, GraphQL, and gRPC - when to use each, trade-offs, and interview-ready talking points.

---

## 1️⃣ REST (Representational State Transfer)

### Core Principles
- **Stateless** - each request contains all info needed
- **Resource-based** - URLs represent nouns, HTTP verbs represent actions
- **Uniform interface** - standard HTTP methods
- **Cacheable** - responses can be cached

### HTTP Methods
| Method | Action | Idempotent | Safe |
|--------|--------|-----------|------|
| GET | Read | ✅ | ✅ |
| POST | Create | ❌ | ❌ |
| PUT | Replace | ✅ | ❌ |
| PATCH | Partial update | ❌ | ❌ |
| DELETE | Delete | ✅ | ❌ |

### REST API Design Best Practices

```
# Resource naming - use nouns, not verbs
✅ GET /users/123
❌ GET /getUser?id=123

# Nested resources for relationships
GET /users/123/orders          # All orders for user 123
GET /users/123/orders/456      # Specific order

# Filtering, sorting, pagination via query params
GET /products?category=electronics&sort=price&order=asc&page=2&limit=20

# Versioning
GET /v1/users/123
GET /v2/users/123

# Status codes
200 OK           - Success
201 Created      - Resource created (POST)
204 No Content   - Success, no body (DELETE)
400 Bad Request  - Invalid input
401 Unauthorized - Not authenticated
403 Forbidden    - Authenticated but not authorized
404 Not Found    - Resource doesn't exist
409 Conflict     - Duplicate resource
422 Unprocessable - Validation error
429 Too Many Requests - Rate limited
500 Internal Server Error
```

### REST Response Structure

```text
# Standard response envelope
{
  "success": true,
  "data": {
    "id": "user_123",
    "name": "Rahul Sharma",
    "email": "rahul@example.com"
  },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 150
  }
}

# Error response
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [
      { "field": "email", "message": "Email cannot be empty" }
    ]
  }
}
```

### REST Pros & Cons
| ✅ Pros | ❌ Cons |
|---------|---------|
| Simple, widely understood | Over-fetching (getting more data than needed) |
| Great tooling (Postman, Swagger) | Under-fetching (multiple requests for related data) |
| HTTP caching built-in | No real-time support natively |
| Stateless = easy to scale | Versioning can get messy |
| Works everywhere | N+1 query problem |

---

## 2️⃣ GraphQL

### Core Concepts
- **Single endpoint** - `POST /graphql`
- **Client specifies shape** - ask for exactly what you need
- **Strongly typed schema** - self-documenting
- **Queries** (read), **Mutations** (write), **Subscriptions** (real-time)

### Schema Definition

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  orders: [Order!]!
  createdAt: String!
}

type Order {
  id: ID!
  total: Float!
  status: String!
  items: [OrderItem!]!
}

type OrderItem {
  product: Product!
  quantity: Int!
  price: Float!
}

type Query {
  user(id: ID!): User
  users(page: Int, limit: Int): [User!]!
  order(id: ID!): Order
}

type Mutation {
  createUser(name: String!, email: String!): User!
  updateUser(id: ID!, name: String): User!
  deleteUser(id: ID!): Boolean!
  placeOrder(userId: ID!, items: [OrderItemInput!]!): Order!
}

type Subscription {
  orderStatusChanged(orderId: ID!): Order!
}
```

### Query Examples

```graphql
# Fetch only what you need (no over-fetching)
query GetUserWithOrders {
  user(id: "123") {
    name
    email
    orders {
      id
      total
      status
    }
  }
}

# Mutation
mutation CreateUser {
  createUser(name: "Priya", email: "priya@example.com") {
    id
    name
  }
}

# Real-time subscription
subscription TrackOrder {
  orderStatusChanged(orderId: "ORD-456") {
    id
    status
  }
}
```

### Resolvers & the N+1 Problem

Each field maps to a **resolver** function. A naive setup causes the **N+1 problem**: fetching N
users, then one query per user for their orders (1 + N queries). The fix is a **DataLoader** - it
batches the per-key requests within a single tick into one query (`SELECT ... WHERE user_id IN (...)`)
and returns results in key order, turning 1 + N queries into 2. This is the single most important
GraphQL performance talking point.

### GraphQL Pros & Cons
| ✅ Pros | ❌ Cons |
|---------|---------|
| No over/under-fetching | Complex to set up |
| Single endpoint | N+1 problem (need DataLoader) |
| Self-documenting schema | Harder to cache (POST requests) |
| Great for complex, nested data | Overkill for simple CRUD |
| Real-time via subscriptions | Learning curve |

---

## 3️⃣ gRPC (Google Remote Procedure Call)

### Core Concepts
- **Protocol Buffers** - binary serialization (smaller, faster than JSON)
- **HTTP/2** - multiplexing, bidirectional streaming
- **Strongly typed** - `.proto` schema files
- **4 communication patterns** - unary, server streaming, client streaming, bidirectional

### Proto Definition

```protobuf
syntax = "proto3";

package user;

service UserService {
  // Unary RPC
  rpc GetUser (GetUserRequest) returns (User);

  // Server streaming - server sends multiple responses
  rpc ListUsers (ListUsersRequest) returns (stream User);

  // Client streaming - client sends multiple requests
  rpc CreateUsers (stream CreateUserRequest) returns (CreateUsersResponse);

  // Bidirectional streaming
  rpc Chat (stream ChatMessage) returns (stream ChatMessage);
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}

message GetUserRequest {
  string id = 1;
}

message ListUsersRequest {
  int32 page = 1;
  int32 limit = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message CreateUsersResponse {
  repeated User users = 1;
  int32 created_count = 2;
}
```

The server implements the RPCs declared in the `.proto` service (a code generator produces the
typed stubs). For a unary RPC you return one response; for server streaming you write many responses
then close the stream. The `.proto` file is the contract shared by client and server.

### gRPC Pros & Cons
| ✅ Pros | ❌ Cons |
|---------|---------|
| Very fast (binary + HTTP/2) | Not human-readable |
| Streaming support | Limited browser support |
| Strong typing | Steeper learning curve |
| Code generation | Harder to debug |
| Great for microservices | Overkill for public APIs |

---

## 4️⃣ When to Use What

```
Decision Tree:

Is it a public API?
├── Yes → REST (universal support, easy to consume)
└── No (internal microservices)
    ├── Need real-time / streaming? → gRPC or GraphQL subscriptions
    ├── Complex nested data, mobile client? → GraphQL
    └── High performance, service-to-service? → gRPC

Is the client mobile?
├── Yes → GraphQL (reduce over-fetching, save bandwidth)
└── No → REST or gRPC

Need real-time?
├── Yes → WebSockets, gRPC streaming, or GraphQL subscriptions
└── No → REST or GraphQL queries
```

### Comparison Table

| | REST | GraphQL | gRPC |
|--|------|---------|------|
| Protocol | HTTP/1.1 | HTTP/1.1 | HTTP/2 |
| Format | JSON | JSON | Protobuf (binary) |
| Schema | OpenAPI (optional) | Required | Required (.proto) |
| Caching | Easy (GET) | Hard | Hard |
| Real-time | Polling/SSE | Subscriptions | Streaming |
| Browser support | ✅ | ✅ | ⚠️ (grpc-web) |
| Performance | Good | Good | Excellent |
| Best for | Public APIs, CRUD | Complex data, mobile | Microservices, streaming |

---

## 5️⃣ API Security

- **Authentication** - verify identity via a bearer token (e.g. JWT) in the `Authorization` header; reject missing/invalid tokens with 401. Attach the decoded principal to the request.
- **Authorization** - after authentication, check the principal's role/permissions for the resource; reject with 403 if insufficient. Keep authZ separate from authN.
- **Rate limiting** - cap requests per client per window (see the token-bucket vs sliding-window discussion in [System Design Guide](SystemDesignGuide.md)); use a stricter limit on auth endpoints (e.g. 5 login attempts / 15 min) to blunt brute-force.
- **Input validation** - validate and normalize every field at the edge (type, length, format); reject with 422 and field-level error details. Never trust client input.
- **Transport** - always TLS; never log secrets or tokens.

---

## 6️⃣ API Versioning Strategies

```text
# Strategy 1: URL versioning (most common)
MOUNT "/v1" -> v1Router
MOUNT "/v2" -> v2Router
# GET /v1/users vs GET /v2/users

# Strategy 2: Header versioning
ON REQUEST (request, response, next)
    version = request.headers["api-version"] OR "v1"
    request.apiVersion = version
    next()
END ON

# Strategy 3: Query param
# GET /users?version=2

# Strategy 4: Content negotiation
# Accept: application/vnd.myapi.v2+json
```

**Recommendation:** URL versioning for public APIs (most visible, easiest to test)

---

## 7️⃣ Interview Talking Points

**"Why REST over GraphQL?"**
> REST is simpler, has better caching support, and is universally understood. For a CRUD API with predictable data shapes, REST is the right choice. GraphQL shines when clients have diverse data needs or when you want to avoid multiple round trips.

**"Why gRPC for microservices?"**
> gRPC uses Protocol Buffers (binary, ~5x smaller than JSON) over HTTP/2 (multiplexed connections). For internal service-to-service calls doing thousands of RPC calls per second, this performance difference is significant. The strongly-typed schema also acts as a contract between services.

**"How do you handle API versioning?"**
> I prefer URL versioning (`/v1/`, `/v2/`) for public APIs because it's explicit and easy to test. For internal APIs, I use header versioning to keep URLs clean. The key is maintaining backward compatibility - never remove fields, only add them.

---

## Related Resources

- [System Design Guide](SystemDesignGuide.md)
- [Low-Level Design Guide](LowLevelDesign.md)
- [Microservices Component](components/microservices.md)
