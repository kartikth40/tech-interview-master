# Food Delivery System Design (Swiggy/Zomato)
> **SDE-2 Interview Ready** | 45-minute format

## 🎯 Problem Statement

Design a food delivery platform like Swiggy or Zomato that connects:
- **Customers** - Browse restaurants, place orders
- **Restaurants** - Manage menu, accept orders
- **Delivery Partners** - Pick up and deliver orders

**Key Requirements:**
- 50M users, 5M daily active users
- 1M orders/day
- Real-time order tracking
- 30-minute average delivery time
- Support peak hours (lunch/dinner: 12-2 PM, 7-10 PM)

---

## 1️⃣ Requirements Clarification

### Functional Requirements:

1. **Customer Features**
   - Search restaurants by location, cuisine, rating
   - View menu, add items to cart
   - Place order (COD, UPI, Card)
   - Real-time order tracking
   - View order history

2. **Restaurant Features**
   - Manage menu (add/update dishes, pricing)
   - Accept/reject orders
   - Update preparation status

3. **Delivery Partner Features**
   - View available orders
   - Accept order
   - Update pickup/delivery status
   - Navigate to restaurant/customer

4. **Platform Features**
   - Delivery partner assignment (matching)
   - Pricing (delivery fee, surge pricing)
   - Ratings & reviews

### Non-Functional Requirements:
- **Scale:** 1M orders/day, peak 50K orders/hour
- **Availability:** 99.9% uptime
- **Latency:** <2 sec for restaurant search, <1 sec for tracking
- **Consistency:** Strong consistency for payments, eventual for tracking

### Out of Scope:
- Restaurant onboarding
- Customer support chat
- Loyalty programs (Swiggy One)

---

## 2️⃣ Capacity Estimation

```
Users: 50M total, 5M daily active users (DAU)
Orders per day: 1M
Orders per second:
- Average: 1M / 86400 = 12 orders/sec
- Peak (lunch/dinner 6 hours): 600K orders / 21600 sec = 28 orders/sec
- Peak surge: 28 × 3 = 85 orders/sec

Read vs Write:
- 1 order placed → 10 searches (10:1 read-to-write ratio)
- Read QPS: 120/sec avg, 850/sec peak

Delivery Partners:
- 1M orders/day
- 3 orders per partner per day
- Total partners needed: 1M / 3 = 330K active partners/day

Storage:
Per order: 5 KB (order details + metadata)
Daily: 1M × 5 KB = 5 GB/day
1 year: 5 GB × 365 = 1.8 TB

Bandwidth:
- Restaurant search: 100 KB response × 850 QPS = 85 MB/sec
- Order placement: 5 KB × 85 QPS = 425 KB/sec
```

---

## 3️⃣ API Design

### Core APIs (6 endpoints)

```text
# 1. Search Restaurants
GET /v1/restaurants/search
  ?lat=12.9716&lon=77.5946     # Bangalore coordinates
  &cuisine=north-indian
  &sort_by=rating
  &page=1&limit=20

Response:
  restaurants: [
    {
      id: "rest_123"
      name: "Biryani House"
      cuisine: ["North Indian", "Biryani"]
      rating: 4.3
      delivery_time: "30-35 min"
      distance: 2.5             # km
      is_open: true
      avg_cost_for_two: 400     # INR
    }
  ]
  total: 150
  page: 1

# 2. Get Restaurant Menu
GET /v1/restaurants/{restaurant_id}/menu

Response:
  restaurant_id: "rest_123"
  categories: [
    {
      name: "Biryani"
      items: [
        {
          id: "item_456"
          name: "Chicken Biryani"
          description: "Hyderabadi style"
          price: 220
          veg: false
          in_stock: true
          image_url: "https://cdn.swiggy.com/..."
        }
      ]
    }
  ]

# 3. Place Order
POST /v1/orders
Body:
  restaurant_id: "rest_123"
  items: [
    { item_id: "item_456", quantity: 2, price: 220 }
  ]
  delivery_address: {
    lat: 12.9716
    lon: 77.5946
    address: "123, MG Road, Bangalore"
  }
  payment_method: "UPI"
  total_amount: 500            # 440 + 40 delivery + 20 taxes

Response:
  order_id: "order_abc123"
  status: "placed"
  estimated_delivery_time: "2024-01-15T13:30:00Z"
  payment_status: "pending"

# 4. Get Order Status (Real-time tracking)
GET /v1/orders/{order_id}

Response:
  order_id: "order_abc123"
  status: "out_for_delivery"
  restaurant: { name: "Biryani House", ... }
  delivery_partner: {
    name: "Rajesh"
    phone: "+91-9876543210"
    current_location: { lat: 12.9750, lon: 77.5980 }
    vehicle_number: "KA-01-AB-1234"
  }
  timeline: [
    { status: "placed", timestamp: "2024-01-15T12:45:00Z" }
    { status: "accepted", timestamp: "2024-01-15T12:46:00Z" }
    { status: "preparing", timestamp: "2024-01-15T12:47:00Z" }
    { status: "ready_for_pickup", timestamp: "2024-01-15T13:05:00Z" }
    { status: "picked_up", timestamp: "2024-01-15T13:10:00Z" }
    { status: "out_for_delivery", timestamp: "2024-01-15T13:15:00Z" }
  ]
  eta: "15 min"

# 5. Assign Delivery Partner (Internal API - called by matching service)
POST /v1/internal/orders/{order_id}/assign
Body:
  delivery_partner_id: "partner_789"

Response:
  order_id: "order_abc123"
  delivery_partner_id: "partner_789"
  assigned_at: "2024-01-15T13:05:00Z"

# 6. Update Delivery Status (by delivery partner)
PATCH /v1/orders/{order_id}/status
Body:
  status: "picked_up"
  current_location: { lat: 12.9750, lon: 77.5980 }

Response:
  order_id: "order_abc123"
  status: "picked_up"
  updated_at: "2024-01-15T13:10:00Z"
```

---

## 4️⃣ Database Design

### PostgreSQL (Core Data - Users, Restaurants, Orders)

```sql
-- Users
CREATE TABLE users (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255),
  phone VARCHAR(15) UNIQUE,
  email VARCHAR(255),
  created_at TIMESTAMP
);

-- Restaurants
CREATE TABLE restaurants (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255),
  cuisine TEXT[],  -- ['North Indian', 'Chinese']
  rating DECIMAL(2,1),
  location GEOGRAPHY(POINT),  -- PostGIS for geospatial queries
  address TEXT,
  is_open BOOLEAN,
  created_at TIMESTAMP
);

CREATE INDEX idx_restaurants_location ON restaurants USING GIST (location);

-- Menu Items
CREATE TABLE menu_items (
  id VARCHAR(50) PRIMARY KEY,
  restaurant_id VARCHAR(50) REFERENCES restaurants(id),
  name VARCHAR(255),
  price DECIMAL(10,2),
  veg BOOLEAN,
  in_stock BOOLEAN,
  category VARCHAR(100)
);

CREATE INDEX idx_menu_restaurant ON menu_items(restaurant_id);

-- Orders
CREATE TABLE orders (
  id VARCHAR(50) PRIMARY KEY,
  user_id VARCHAR(50) REFERENCES users(id),
  restaurant_id VARCHAR(50) REFERENCES restaurants(id),
  delivery_partner_id VARCHAR(50),
  status VARCHAR(50),  -- placed, accepted, preparing, ready, picked_up, delivered
  total_amount DECIMAL(10,2),
  delivery_lat DECIMAL(10,6),
  delivery_lon DECIMAL(10,6),
  created_at TIMESTAMP,
  delivered_at TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Order Items
CREATE TABLE order_items (
  id VARCHAR(50) PRIMARY KEY,
  order_id VARCHAR(50) REFERENCES orders(id),
  item_id VARCHAR(50) REFERENCES menu_items(id),
  quantity INT,
  price DECIMAL(10,2)
);

-- Delivery Partners
CREATE TABLE delivery_partners (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255),
  phone VARCHAR(15),
  vehicle_number VARCHAR(20),
  status VARCHAR(20),  -- available, busy, offline
  current_lat DECIMAL(10,6),
  current_lon DECIMAL(10,6),
  rating DECIMAL(2,1)
);
```

### Redis (Caching, Real-time Tracking)

```text
# Restaurant search cache (frequently searched locations)
Key: restaurants:location:12.9716:77.5946:north-indian
Value: JSON list [{ id: "rest_123", name: "...", ... }]
TTL: 5 minutes

# Delivery partner location (real-time)
Key: partner:{partner_id}:location
Value: "12.9750,77.5980"  # lat,lon
TTL: 60 seconds

# Available delivery partners (geospatial)
Key: partners:available
Type: Geo (Redis geospatial data structure)
Value: partner_id at (lat, lon)

# Order status cache
Key: order:{order_id}:status
Value: "out_for_delivery"
TTL: 1 hour
```

### Cassandra (Time-series - Location Tracking)

```sql
-- Delivery partner location history (for analytics)
CREATE TABLE delivery_tracking (
  partner_id TEXT,
  timestamp TIMESTAMP,
  lat DOUBLE,
  lon DOUBLE,
  order_id TEXT,
  PRIMARY KEY (partner_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

---

## 5️⃣ High-Level Design

```
┌──────────────────────────────────────────────────────────────┐
│                      Clients                                 │
│   Customer App  |  Restaurant App  |  Delivery Partner App  │
└──────────┬───────────────┬──────────────────┬────────────────┘
           │               │                  │
           ▼               ▼                  ▼
    ┌──────────────────────────────────────────────┐
    │         Load Balancer (NGINX)                │
    └──────────┬───────────────────────────────────┘
               │
    ┌──────────┴────────────┬────────────┬──────────────┐
    ▼                       ▼            ▼              ▼
┌─────────┐         ┌──────────┐   ┌──────────┐  ┌──────────┐
│ Search  │         │  Order   │   │ Tracking │  │ Payment  │
│ Service │         │ Service  │   │ Service  │  │ Service  │
└────┬────┘         └─────┬────┘   └────┬─────┘  └────┬─────┘
     │                    │             │             │
     │                    │             │             │
     ▼                    ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
│  ┌──────────┐  ┌───────┐  ┌──────────┐  ┌──────────────┐   │
│  │PostgreSQL│  │ Redis │  │Cassandra │  │Kafka (Events)│   │
│  │          │  │       │  │(Tracking)│  │              │   │
│  │-Restaurants│ │-Cache│  └──────────┘  └──────────────┘   │
│  │-Orders   │  │-Geo   │                                    │
│  │-Users    │  │-Status│                                    │
│  └──────────┘  └───────┘                                    │
└─────────────────────────────────────────────────────────────┘
         │                           │
         ▼                           ▼
┌──────────────────┐       ┌──────────────────────┐
│ Matching Service │       │  Notification Service│
│(Assign Delivery) │       │  (SMS, Push)         │
└──────────────────┘       └──────────────────────┘
```

**Data Flow (Order Placement):**
1. Customer places order → Order Service
2. Order Service validates & creates order in PostgreSQL
3. Publishes `OrderPlaced` event to Kafka
4. Matching Service consumes event → Finds nearby available delivery partners (Redis GEORADIUS)
5. Assigns delivery partner → Updates order
6. Notification Service sends SMS/push to restaurant & delivery partner
7. Tracking Service starts tracking delivery partner location (Redis + Cassandra)

---

## 6️⃣ Low-Level Design

### Class Diagram

```
┌───────────────────────┐
│   OrderService        │
├───────────────────────┤
│ + placeOrder()        │
│ + getOrderStatus()    │
│ + updateOrderStatus() │
└──────┬────────────────┘
       │ uses
       ▼
┌───────────────────────┐
│  MatchingService      │
├───────────────────────┤
│ + findDeliveryPartner()│
│ + assignPartner()     │
└──────┬────────────────┘
       │ uses
       ▼
┌───────────────────────┐
│   GeoService          │
├───────────────────────┤
│ + findNearby()        │
│ + calculateETA()      │
└───────────────────────┘
```

### Sequence Diagram (Order Flow)

```
Customer  OrderService  Kafka  MatchingService  DeliveryPartner  Restaurant
   │          │           │           │                │              │
   │─Place───>│           │           │                │              │
   │          │           │           │                │              │
   │          │─Create────┴──────────>│                │              │
   │          │  order    │ OrderPlaced                │              │
   │<─────────│           │           │                │              │
   │  order_id│           │           │                │              │
   │          │           │─Find─────>│                │              │
   │          │           │  partner  │                │              │
   │          │           │<──────────│                │              │
   │          │           │  partner_id                │              │
   │          │           │                            │              │
   │          │           │─Assign────────────────────>│              │
   │          │           │                            │<─Accept─────│
   │          │           │                            │              │
   │          │           │─Notify────────────────────────────────────>│
   │          │           │                            │              │
```

### State Machine (Order Status)

```
┌────────┐
│ PLACED │ (Customer placed order)
└───┬────┘
    │
    ▼
┌──────────┐
│ ACCEPTED │ (Restaurant accepted)
└─────┬────┘
      │
      ▼
┌───────────┐
│ PREPARING │ (Restaurant preparing food)
└──────┬────┘
       │
       ▼
┌────────────────┐
│ READY_FOR_PICKUP│ (Food ready)
└────────┬────────┘
         │
         ▼
┌──────────────┐
│  PICKED_UP   │ (Delivery partner picked up)
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│OUT_FOR_DELIVERY  │ (On the way)
└────────┬─────────┘
         │
         ▼
┌───────────┐
│ DELIVERED │ (Order completed)
└───────────┘
```

### Design Patterns

1. **Event-Driven Architecture** - Kafka for order events (OrderPlaced, OrderAccepted, OrderDelivered)
2. **Strategy Pattern** - Different matching algorithms (distance-based, rating-based, hybrid)
3. **Observer Pattern** - Real-time tracking (WebSocket for live location updates)
4. **CQRS** - Read-heavy (restaurant search) vs write (order placement) separation

---

## 7️⃣ Deep Dives

### Deep Dive 1: Delivery Partner Matching Algorithm

**Challenge:** Assign nearest available delivery partner to order within 30 seconds

**Approach: Distance + ETA + Load Balancing**

```text
CLASS MatchingService

  FUNCTION findDeliveryPartner(order)
    restaurant_lat = order.restaurant_lat
    restaurant_lon = order.restaurant_lon

    # 1. Find delivery partners within 3 km of restaurant (Redis GEORADIUS)
    nearbyPartners = redis.geoRadius(
      "partners:available",
      restaurant_lon, restaurant_lat,
      3, "km",              # 3 km radius
      WITH_DISTANCE,        # include distance
      ORDER_ASCENDING       # sort by distance
    )

    IF nearbyPartners IS EMPTY THEN
      # Expand radius to 5 km
      nearbyPartners = redis.geoRadius(
        "partners:available",
        restaurant_lon, restaurant_lat,
        5, "km",
        WITH_DISTANCE,
        ORDER_ASCENDING
      )
    END IF

    # 2. Calculate ETA for each partner
    partnersWithETA = empty list
    FOR EACH (partnerId, distance) IN nearbyPartners
      partner = getPartnerDetails(partnerId)

      # ETA = distance / average_speed (20 km/h in city)
      etaMinutes = (distance / 20) * 60

      # Consider partner rating & current load
      score = calculateScore(distance, partner.rating, partner.active_orders)

      append { partnerId: partnerId, distance: distance, etaMinutes: etaMinutes, score: score } TO partnersWithETA
    END FOR

    # 3. Select best partner (lowest score = best)
    SORT partnersWithETA BY score ASCENDING
    bestPartner = partnersWithETA[0]

    # 4. Try to assign (with distributed lock to prevent double-assignment)
    lockKey      = "partner:" + bestPartner.partnerId + ":lock"
    lockAcquired = redis.setIfAbsent(lockKey, order.id, expirySeconds = 10)

    IF lockAcquired THEN
      # Assign partner
      assignPartner(order.id, bestPartner.partnerId)

      # Remove from available pool
      redis.geoRemove("partners:available", bestPartner.partnerId)

      RETURN bestPartner
    ELSE
      # Partner already assigned, try next
      RETURN findDeliveryPartner(order)
    END IF
  END FUNCTION

  FUNCTION calculateScore(distance, rating, activeOrders)
    # Lower score = better
    RETURN (
      distance * 2 +          # distance weight: 2x
      (5 - rating) * 5 +      # rating weight: 5x (prefer 4.5+ rating)
      activeOrders * 3        # load weight: 3x (prefer low load)
    )
  END FUNCTION

END CLASS
```

**Trade-offs:**
- ✅ Fast matching (<1 second)
- ✅ Considers distance, rating, load
- ❌ Greedy algorithm (may not be globally optimal)
- ❌ Doesn't account for traffic (can integrate Google Maps API for real ETA)

**Alternative: Batch Matching**
- Wait for 10-20 orders, then optimize assignment (Hungarian algorithm)
- Better global optimization but higher latency

---

### Deep Dive 2: Real-time Order Tracking

**Challenge:** Show delivery partner's live location to customer (updated every 5 seconds)

**Solution: WebSocket + Redis + Cassandra**

```text
# Delivery Partner App (sends location every 5 seconds)
CLASS DeliveryPartnerService

  FUNCTION updateLocation(partnerId, lat, lon)
    # 1. Update Redis (for real-time tracking)
    redis.geoAdd("partners:location", lon, lat, partnerId)
    redis.set("partner:" + partnerId + ":location", lat + "," + lon, expirySeconds = 60)

    # 2. Get active order for this partner
    orderId = redis.get("partner:" + partnerId + ":active_order")

    IF orderId EXISTS THEN
      # 3. Push to WebSocket server (for customer app)
      publishEvent({
        type: "location_update",
        order_id: orderId,
        location: { lat: lat, lon: lon },
        timestamp: currentTime()
      })

      # 4. Store in Cassandra (for analytics)
      cassandra.execute(
        "INSERT INTO delivery_tracking (partner_id, timestamp, lat, lon, order_id) VALUES (?, ?, ?, ?, ?)",
        [partnerId, currentTime(), lat, lon, orderId]
      )
    END IF
  END FUNCTION

END CLASS

# Customer App (receives updates via WebSocket)
ON websocket "location_update" (data)
  # Update map marker position
  updateDeliveryPartnerMarker(data.location)

  # Recalculate ETA
  eta = calculateETA(currentLocation, data.location)
  updateETADisplay(eta)
END ON
```

**Optimizations:**
- Batch writes to Cassandra (every 10 updates instead of every update)
- Only send updates when movement > 50 meters (avoid jitter)
- Use WebSocket or Server-Sent Events (SSE) for push

**Trade-offs:**
- ✅ Real-time updates (5-sec frequency)
- ✅ Low latency (<500ms)
- ❌ High WebSocket server cost (5M DAU = 500K concurrent connections during peak)
- ❌ Battery drain on delivery partner's phone (mitigate: adaptive frequency based on proximity)

---

### Deep Dive 3: Surge Pricing

**Challenge:** Increase delivery fees during high demand (lunch/dinner rush)

**Solution: Dynamic Pricing Algorithm**

```text
CLASS PricingService

  FUNCTION calculateDeliveryFee(restaurantId, deliveryLocation, timestamp)
    basePrice = 40    # INR

    # 1. Calculate distance
    distance    = calculateDistance(restaurant.location, deliveryLocation)
    distanceFee = distance * 5    # Rs 5/km

    # 2. Peak hours multiplier
    hour = hourOf(timestamp)
    peakMultiplier = 1.0
    IF (hour >= 12 AND hour <= 14) OR (hour >= 19 AND hour <= 22) THEN
      peakMultiplier = 1.5    # 50% surge during lunch/dinner
    END IF

    # 3. Demand-supply ratio (from cache)
    areaGrid          = getGridId(deliveryLocation)
    pendingOrders     = redis.get("area:" + areaGrid + ":pending_orders") OR DEFAULT 0
    availablePartners = redis.get("area:" + areaGrid + ":available_partners") OR DEFAULT 1

    demandSupplyRatio = pendingOrders / availablePartners
    surgeMultiplier   = 1.0
    IF demandSupplyRatio > 5 THEN
      surgeMultiplier = 2.0    # 2x surge when demand is 5x supply
    ELSE IF demandSupplyRatio > 3 THEN
      surgeMultiplier = 1.5
    END IF

    # 4. Weather (from external API)
    isRaining         = checkWeather(deliveryLocation)
    weatherMultiplier = IF isRaining THEN 1.3 ELSE 1.0

    # 5. Final price
    totalFee = round(
      (basePrice + distanceFee) * peakMultiplier * surgeMultiplier * weatherMultiplier
    )

    RETURN {
      base: basePrice,
      distance_fee: distanceFee,
      surge_multiplier: peakMultiplier * surgeMultiplier * weatherMultiplier,
      total: totalFee
    }
  END FUNCTION

END CLASS
```

**Trade-offs:**
- ✅ Balances demand/supply
- ✅ Increases delivery partner earnings during peak (incentivizes)
- ❌ Customer dissatisfaction during surge
- ❌ Complexity in explaining surge to customers

---

## 8️⃣ Bottlenecks & Optimizations

### Bottlenecks:

1. **Restaurant Search (Geospatial Queries)**
   - Problem: PostGIS queries slow for 100K+ restaurants
   - Solution: Use Elasticsearch with geo_distance queries (faster), cache popular searches in Redis

2. **Delivery Partner Matching**
   - Problem: Sequential search during peak (85 orders/sec)
   - Solution: Pre-compute available partners in grid cells, batch matching every 5 seconds

3. **Real-time Tracking (WebSocket Scaling)**
   - Problem: 500K concurrent WebSocket connections
   - Solution: Horizontal scaling (100 servers × 5K connections), use Redis Pub/Sub for message routing

4. **Database Writes (Peak Load)**
   - Problem: 85 writes/sec (orders) + 5K writes/sec (location updates)
   - Solution: PostgreSQL master-slave replication, Cassandra for write-heavy location tracking

### Optimizations:

**1. Grid-based Geospatial Indexing:**
```
Divide city into 1 km × 1 km grid cells
Store delivery partners in each cell
Faster lookup: O(1) instead of O(n)
```

**2. Predictive Partner Positioning:**
```
ML model to predict demand hotspots
Incentivize delivery partners to move to high-demand areas before peak
```

**3. Caching Strategy:**
```
- Restaurant list: Cache by location (5 min TTL)
- Menu: Cache per restaurant (1 hour TTL, invalidate on update)
- Order status: Cache in Redis (1 hour TTL)
```

---

## 9️⃣ Interview Tips

### What to Focus on (45-min):

1. **Clarify requirements** (5 min)
   - Scale? Peak load?
   - Real-time tracking? Payment?

2. **High-level design** (15 min)
   - Search, Order, Tracking, Matching services
   - PostgreSQL (core), Redis (cache/geo), Cassandra (tracking)

3. **Deep dive 1: Delivery partner matching** (10 min)
   - Redis GEORADIUS for nearby partners
   - Scoring algorithm (distance + rating + load)
   - Distributed locks for assignment

4. **Deep dive 2: Real-time tracking** (5 min)
   - WebSocket for push updates
   - Redis for real-time location, Cassandra for history

5. **Discuss surge pricing** (5 min)
   - Peak hours, demand/supply, weather

6. **Bottlenecks** (5 min)
   - Geospatial queries (Elasticsearch)
   - WebSocket scaling (horizontal)

### Common Follow-ups:

**Q: How do you handle order cancellations?**
A: Idempotent refund API, release delivery partner back to available pool, notify restaurant

**Q: What if delivery partner goes offline mid-delivery?**
A: Timeout detection (no location update for 2 min) → Reassign to nearest available partner

**Q: How do you optimize delivery routes?**
A: Implement multi-drop routing (one partner delivers 2-3 orders in same area), use TSP algorithm

**Q: How do you prevent fraud (fake orders)?**
A: OTP verification at delivery, flag suspicious patterns (multiple cancellations), require prepaid for new users

**Q: How do you handle restaurants being slow?**
A: Track average preparation time per restaurant, adjust estimated delivery time, send nudge notifications

---

## Summary

**Key Design Decisions:**
1. ✅ **PostgreSQL** for core data (ACID for orders)
2. ✅ **Redis GEORADIUS** for geospatial queries (delivery partner matching)
3. ✅ **Cassandra** for time-series (location tracking)
4. ✅ **Kafka** for event-driven architecture (order events)
5. ✅ **WebSocket** for real-time tracking

**Tech Stack:**
- Backend: Node.js / Go / Java
- Database: PostgreSQL (core), Redis (cache/geo), Cassandra (tracking)
- Queue: Kafka (events)
- Search: Elasticsearch (restaurant search)
- Notifications: Firebase Cloud Messaging (FCM), AWS SNS
