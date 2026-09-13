# Uber/Ola Ride-Hailing System Design
> **SDE-2 Interview Ready** | 45-minute format

## 🎯 Problem Statement

Design a ride-hailing platform like Uber or Ola that connects riders with drivers for on-demand transportation.

**Key Requirements:**
- Match riders with nearest available drivers
- Real-time location tracking
- Dynamic pricing (surge)
- ETA calculation
- Handle millions of rides per day

---

## 1️⃣ Requirements Clarification

### Functional Requirements:

**Rider Side:**
1. Request a ride (pickup/dropoff locations)
2. See nearby drivers on map
3. Get fare estimate
4. Track driver in real-time
5. Make payment
6. Rate driver

**Driver Side:**
1. Go online/offline
2. Accept/reject ride requests
3. Navigate to pickup → dropoff
4. Update location (GPS)
5. Complete ride, collect payment

**Platform:**
1. Match rider with nearest driver
2. Calculate ETA and route
3. Dynamic pricing (surge during peak hours)
4. Payment processing

### Non-Functional Requirements:
- **Scale:** 100M active users, 5M drivers, 15M rides/day
- **Latency:** 
  - Driver matching: <5 seconds
  - Location updates: Every 4 seconds
  - ETA updates: Every 30 seconds
- **Availability:** 99.99% uptime
- **Consistency:** Strong (one driver can't accept two rides)
- **GPS accuracy:** Within 50 meters

### Out of Scope:
- Food delivery (Uber Eats)
- Package delivery
- Ride scheduling (future rides)

---

## 2️⃣ Capacity Estimation

```
Active Users: 100M
Active Drivers: 5M
Rides per day: 15M

Rides per second:
- Average: 15M / 86400 = 170 rides/sec
- Peak (evening): 170 × 3 = 500 rides/sec

Location Updates:
- Active drivers: 1M (online at any time)
- Update frequency: Every 4 seconds
- Location updates/sec: 1M / 4 = 250K updates/sec

Storage:
Rides:
- Per ride: 1.5 KB (rider, driver, locations, fare, timestamps)
- Daily: 15M × 1.5 KB = 22.5 GB/day
- 5 years: 22.5 GB × 365 × 5 = 41 TB

GPS Locations:
- Per update: 50 bytes (driver_id, lat, lon, timestamp)
- Per ride: 150 updates (10 min avg × 60 sec / 4 sec)
- Daily: 15M × 150 × 50 bytes = 112.5 GB/day
- Retention: 30 days = 3.37 TB

Bandwidth:
- Location updates: 250K/sec × 50 bytes = 12.5 MB/sec
- Ride requests: 500/sec × 2 KB = 1 MB/sec
- Total: ~14 MB/sec
```

---

## 3️⃣ API Design

### Core APIs

```text
# 1. Request Ride (Rider)
POST /v1/rides/request
Headers: { Authorization: "Bearer <user_token>" }
Body:
  rider_id: "user_123"
  pickup: { lat: 12.9716, lon: 77.5946 }
  dropoff: { lat: 12.9352, lon: 77.6245 }
  ride_type: "sedan"        # sedan, suv, auto
Response:
  ride_id: "ride_abc123"
  estimated_fare: 250       # rupees
  estimated_time: 5         # minutes to pickup
  status: "searching"       # searching, matched, arrived, started, completed

# 2. Get Nearby Drivers (Rider - see drivers on map)
GET /v1/drivers/nearby?lat=12.9716&lon=77.5946&radius=3
Response:
  drivers: [
    {
      driver_id: "driver_456"
      location: { lat: 12.9720, lon: 77.5950 }
      distance: 0.5         # km
      eta: 2                # minutes
    }
  ]

# 3. Accept/Reject Ride (Driver)
POST /v1/rides/{ride_id}/accept
Body:
  driver_id: "driver_456"
Response:
  ride_id: "ride_abc123"
  rider: {
    name: "John Doe"
    phone: "+91-9876543210"
    pickup: { lat: 12.9716, lon: 77.5946 }
  }
  route: {
    distance: 2.3           # km to pickup
    duration: 5             # minutes
  }

# 4. Update Location (Driver - GPS)
POST /v1/drivers/location
Body:
  driver_id: "driver_456"
  location: { lat: 12.9720, lon: 77.5950 }
  timestamp: 1676464123
Response: { success: true }

# 5. Track Ride (Rider - real-time)
GET /v1/rides/{ride_id}/track
Response:
  ride_id: "ride_abc123"
  status: "started"         # matched, arrived, started, completed
  driver: {
    name: "Rajesh Kumar"
    phone: "+91-9876543210"
    location: { lat: 12.9500, lon: 77.6000 }
    rating: 4.8
  }
  eta: 15                   # minutes to destination
  fare: 250

# 6. Complete Ride
POST /v1/rides/{ride_id}/complete
Body:
  driver_id: "driver_456"
  final_fare: 275
  payment_method: "cash"
Response:
  ride_id: "ride_abc123"
  fare: 275
  distance: 8.5             # km
  duration: 22              # minutes
```

---

## 4️⃣ Database Design

### PostgreSQL (Relational Data)

```sql
-- Users (Riders)
CREATE TABLE users (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255),
  phone VARCHAR(15) UNIQUE,
  email VARCHAR(255),
  rating DECIMAL(2,1),
  created_at TIMESTAMP
);

-- Drivers
CREATE TABLE drivers (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255),
  phone VARCHAR(15) UNIQUE,
  vehicle_type VARCHAR(50),  -- sedan, suv, auto
  vehicle_number VARCHAR(20),
  rating DECIMAL(2,1),
  status VARCHAR(20),  -- online, offline, on_ride
  current_location GEOGRAPHY(POINT),  -- PostGIS
  last_location_update TIMESTAMP,
  created_at TIMESTAMP
);
CREATE INDEX idx_drivers_status ON drivers(status);
CREATE INDEX idx_drivers_location ON drivers USING GIST(current_location);

-- Rides
CREATE TABLE rides (
  id VARCHAR(50) PRIMARY KEY,
  rider_id VARCHAR(50) REFERENCES users(id),
  driver_id VARCHAR(50) REFERENCES drivers(id),
  
  pickup_location GEOGRAPHY(POINT),
  dropoff_location GEOGRAPHY(POINT),
  
  status VARCHAR(50),  -- requested, matched, arrived, started, completed, cancelled
  
  estimated_fare INT,
  final_fare INT,
  distance DECIMAL(5,2),  -- km
  duration INT,           -- minutes
  
  requested_at TIMESTAMP,
  matched_at TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  
  payment_method VARCHAR(50)
);
CREATE INDEX idx_rides_rider ON rides(rider_id);
CREATE INDEX idx_rides_driver ON rides(driver_id);
CREATE INDEX idx_rides_status ON rides(status);
```

### Redis (Real-time Data)

```text
# Driver locations (geo-indexed)
Key: drivers:available
Type: Geo Set
Command: GEOADD drivers:available 77.5946 12.9716 driver_456

# Find nearby drivers:
Command: GEORADIUS drivers:available 77.5946 12.9716 3 km

# Driver status
Key: driver:{driver_id}:status
Value: "online" | "offline" | "on_ride"
TTL: None

# Active ride
Key: driver:{driver_id}:active_ride
Value: ride_id
TTL: None

# Ride lock (prevent double assignment)
Key: ride:lock:{ride_id}
Value: 1
TTL: 60 seconds
```

### Cassandra (GPS Location History - Time-series)

```sql
CREATE TABLE gps_tracking (
  driver_id TEXT,
  timestamp TIMESTAMP,
  location FROZEN<location_type>,  -- {lat, lon}
  PRIMARY KEY (driver_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Query: Get driver's route
SELECT * FROM gps_tracking 
WHERE driver_id = 'driver_456' 
  AND timestamp > '2026-02-15 10:00:00'
  AND timestamp < '2026-02-15 11:00:00';
```

---

## 5️⃣ High-Level Design

```
┌─────────┐           ┌─────────┐
│ Riders  │           │ Drivers │
└────┬────┘           └────┬────┘
     │                     │
     │                     │ (GPS every 4s)
     ▼                     ▼
┌────────────────────────────────────┐
│      Load Balancer (WebSocket)     │
└──────┬─────────────────────┬───────┘
       │                     │
       ▼                     ▼
┌─────────────┐      ┌─────────────┐
│ Ride Service│      │ Location    │
│             │      │ Service     │
│ - Request   │      │             │
│ - Match     │      │ - Update GPS│
│ - Track     │      │ - Geo query │
└──────┬──────┘      └──────┬──────┘
       │                    │
       │                    ▼
       │             ┌─────────────┐
       │             │   Redis     │
       │             │ (Geo Index) │
       │             └─────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│      Matching Service                │
│                                      │
│  1. Find nearby drivers (3 km)      │
│  2. Filter: online, not on ride     │
│  3. Calculate ETA for each          │
│  4. Pick closest with best ETA      │
│  5. Send push notification          │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│      Notification Service            │
│  - Push to driver (FCM)              │
│  - SMS/Email                         │
└──────────────────────────────────────┘
       │
       ▼
┌─────────────┐    ┌──────────────┐
│ PostgreSQL  │    │  Cassandra   │
│             │    │              │
│ - Users     │    │ - GPS logs   │
│ - Drivers   │    │ - Analytics  │
│ - Rides     │    │              │
└─────────────┘    └──────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│      Background Services             │
│  - Pricing Service (surge)           │
│  - Payment Service                   │
│  - Analytics                         │
└──────────────────────────────────────┘
```

**Data Flow:**
1. Rider requests ride → Ride Service
2. Ride Service queries Redis for nearby drivers (3 km radius)
3. Matching Service filters available drivers
4. Calculate ETA for each driver
5. Pick closest driver
6. Send push notification to driver
7. Driver accepts → Update ride status
8. Driver shares GPS every 4 seconds → Location Service
9. Location Service updates Redis
10. Rider tracks driver via WebSocket
11. Ride completes → Payment, Rating

---

## 6️⃣ Low-Level Design

### Class Diagram

```
┌─────────────────────────────────┐
│      MatchingService            │
├─────────────────────────────────┤
│ - geoService: GeoService        │
│ - pricingService: PricingService│
│ - notificationService           │
├─────────────────────────────────┤
│ + findDriver(ride): Driver      │
│ + calculateETA(driver, pickup)  │
│ - filterAvailable(drivers)      │
└─────────────────────────────────┘
         │
         │ uses
         ▼
┌─────────────────────────────────┐
│      GeoService                 │
├─────────────────────────────────┤
│ + findNearby(lat, lon, radius)  │
│ + calculateDistance(p1, p2)     │
│ + getRoute(origin, dest)        │
└─────────────────────────────────┘
```

### Sequence Diagram (Ride Matching)

```
Rider    RideService   MatchingService   GeoService   Redis   Driver
  │          │              │                │          │        │
  │─Request─>│              │                │          │        │
  │          │              │                │          │        │
  │          │──Create Ride─>│              │          │        │
  │          │              │                │          │        │
  │          │              │─Find Nearby───>│         │        │
  │          │              │                │─GEORADIUS>│      │
  │          │              │                │<─drivers─│       │
  │          │              │<─drivers───────│          │        │
  │          │              │                │          │        │
  │          │              │─Calculate ETA──>│         │        │
  │          │              │<─route─────────│          │        │
  │          │              │                │          │        │
  │          │              │─Pick Best──────│          │        │
  │          │              │                │          │        │
  │          │              │─Acquire Lock───────────────────────>│
  │          │              │                │          │        │
  │          │              │─Send Push──────────────────────────>│
  │          │<─Ride Status─│                │          │        │
  │<─Matched─│              │                │          │        │
```

### State Machine (Ride Lifecycle)

```
┌───────────┐
│ REQUESTED │ (Rider requests ride)
└─────┬─────┘
      │
      ▼
┌───────────┐
│ SEARCHING │ (Finding driver)
└─────┬─────┘
      │
      ├──────────────┐
      │              │
      ▼              ▼
┌──────────┐    ┌──────────┐
│ MATCHED  │    │CANCELLED │
└─────┬────┘    └──────────┘
      │
      ▼
┌──────────┐
│ ARRIVED  │ (Driver at pickup)
└─────┬────┘
      │
      ▼
┌──────────┐
│ STARTED  │ (Ride in progress)
└─────┬────┘
      │
      ▼
┌───────────┐
│ COMPLETED │
└───────────┘
```

### Design Patterns

1. **Strategy Pattern** - Different pricing strategies (normal, surge, scheduled)
2. **Observer Pattern** - Notify rider of driver location updates
3. **State Pattern** - Ride state machine
4. **Factory Pattern** - Create different ride types (sedan, SUV, auto)

---

## 7️⃣ Deep Dives

### Deep Dive 1: Driver Matching Algorithm

**Challenge:** Find the best driver among thousands nearby

**Approach (the steps that matter):**
1. **Find candidates** - `GEORADIUS` on a Redis geo-index (`drivers:available`) for drivers within 3 km of pickup (expand to 5 km if empty). Redis geo query is O(log N + M).
2. **Rank** - for the closest ~5, compute real ETA via a maps/routing provider (accounts for traffic, not just straight-line distance) and pick the lowest ETA.
3. **Assign atomically** - acquire a short-TTL lock on the chosen driver (`SET driver:{id}:lock ride_id NX EX 60`) to prevent double-assignment; if the lock fails, try the next candidate.
4. **Commit + notify** - mark the driver `on_ride`, record the active ride, and push a request notification.

**Trade-offs:**
- ✅ Fast (Redis geo queries: O(log N + M))
- ✅ Accurate ETA (uses real-time traffic)
- ❌ Routing-API cost per request → cache common routes
- ❌ Lock contention at peak times

---

### Deep Dive 2: Real-time Location Tracking

**Challenge:** 250K GPS updates/second from drivers

**Solution:** Write to Redis (fast), batch write to Cassandra

**Implementation:**
```text
# Driver app sends GPS every 4 seconds
FUNCTION updateDriverLocation(driverId, location)
  # 1. Update Redis (for real-time queries)
  redis.geoAdd("drivers:available", location.lon, location.lat, driverId)

  # 2. Cache location with timestamp
  redis.set(
    "driver:" + driverId + ":location",
    serialize({ location: location, timestamp: currentTime() }),
    expirySeconds = 60          # 1 minute TTL
  )

  # 3. Buffer for batch write to Cassandra
  locationBuffer.add({
    driver_id: driverId,
    timestamp: currentTime(),
    location:  location
  })

  # Flush buffer every 10 seconds or 5000 records
  IF locationBuffer.size() >= 5000 OR locationBuffer.elapsedSeconds() >= 10 THEN
    flushLocationBuffer()
  END IF

  # 4. Notify rider via WebSocket (if driver is on active ride)
  rideId = redis.get("driver:" + driverId + ":active_ride")
  IF rideId EXISTS THEN
    websocket.send(rideId, {
      type: "location_update",
      driver_location: location,
      timestamp: currentTime()
    })
  END IF
END FUNCTION

# Batch write to Cassandra
FUNCTION flushLocationBuffer()
  locations = locationBuffer.getAll()

  batch = cassandra.newBatch()
  FOR EACH loc IN locations
    batch.add(
      "INSERT INTO gps_tracking (driver_id, timestamp, location) VALUES (?, ?, ?)",
      [loc.driver_id, loc.timestamp, loc.location]
    )
  END FOR

  batch.execute()
  locationBuffer.clear()
END FUNCTION
```

**Trade-offs:**
- ✅ High write throughput (250K/sec)
- ✅ Low latency for real-time queries (Redis)
- ✅ Historical data for analytics (Cassandra)
- ❌ Risk of data loss if server crashes (10s buffer)
- ❌ Eventual consistency (Cassandra)

**Alternative:** Use Kafka for streaming (more complex but more reliable)

---

### Deep Dive 3: Surge Pricing

**Challenge:** Dynamically adjust prices based on demand/supply

**The core idea (don't memorize the exact multipliers - they're product tuning):**
- **Fare** = base + (distance × per-km) + (duration × per-min), then × surge multiplier.
- **Surge** is driven by the **demand/supply ratio** in the pickup area: `pending_rides / available_drivers` (both computed locally - pending rides from the DB, drivers from the Redis geo-index within ~2 km). The higher the ratio, the higher the multiplier, **capped** (e.g. at 3×) so prices stay bounded.
- Optional signals nudge the multiplier: peak hours, weather. These are tunable knobs, not the design.

The interview point is the **feedback loop** (local demand/supply → bounded multiplier → incentivizes more drivers into the area), not the specific constants.

**Trade-offs:**
- ✅ Balances supply-demand dynamically; incentivizes drivers during peaks
- ❌ Customer dissatisfaction; hard to explain
- **Alternative:** flat pricing with longer wait times

---

## 8️⃣ Bottlenecks & Optimizations

### Bottlenecks:

1. **Redis Single Point of Failure**
   - Solution: Redis Sentinel (3-5 nodes with auto-failover)

2. **Google Maps API Rate Limits**
   - Solution: Cache common routes, use alternative maps (Mapbox)

3. **Database Write Load**
   - Problem: 250K GPS writes/sec
   - Solution: Batch writes, use Cassandra (optimized for writes)

4. **WebSocket Connections**
   - Problem: 1M concurrent connections
   - Solution: Distribute across multiple WebSocket servers, use Redis Pub/Sub

### Optimizations:

**1. Geospatial Indexing:**
```
Use Redis GEO commands (based on sorted sets):
- GEOADD: O(log N) per insert
- GEORADIUS: O(log N + M) where M = results

Alternative: Use PostGIS (PostgreSQL extension) for complex queries
```

**2. Caching:**
```
Cache driver locations (Redis): TTL 1 minute
Cache routes (Memcached): TTL 1 hour
Cache pricing (Redis): TTL 5 minutes
```

**3. Database Sharding:**
```
Shard rides by city:
- rides_bangalore
- rides_mumbai
- rides_delhi

Most queries are city-specific anyway
```

---

## 9️⃣ Interview Tips

### What to Focus on (45-min):

1. **Clarify requirements** (5 min)
   - Scale? (100M users)
   - Real-time tracking? (Yes, every 4s)
   - Geospatial queries? (Yes, find nearby drivers)

2. **Draw high-level design** (15 min)
   - Client → Load Balancer → Ride Service
   - Redis for geo-indexing
   - PostgreSQL for rides
   - Cassandra for GPS logs

3. **Deep dive: Driver matching** (10 min)
   - Redis GEORADIUS
   - Filter available drivers
   - Calculate ETA
   - Distributed locks

4. **Deep dive: Location tracking** (5 min)
   - Redis for real-time
   - Batch write to Cassandra
   - WebSocket for rider updates

5. **Discuss bottlenecks** (5 min)
   - Redis clustering
   - Google Maps API costs
   - WebSocket scaling

### Common Follow-ups:

**Q: How do you prevent a driver from getting multiple ride requests?**
A: Distributed locks in Redis (`driver:{id}:lock`), check status before sending notification

**Q: What if Google Maps API is down?**
A: Fallback to cached routes, Haversine formula for distance (less accurate), use alternative provider (Mapbox)

**Q: How do you handle driver going offline mid-ride?**
A: Monitor GPS updates, if no update for 30s send alert, reassign ride after 2 min

**Q: How do you calculate ETA accurately in traffic?**
A: Use Google Maps with traffic data, apply city-specific multipliers (Bangalore = 1.5x during peak)

---

## Summary

**Key Design Decisions:**
1. ✅ **Redis** for geospatial indexing (fast nearby driver queries)
2. ✅ **PostgreSQL** for transactional data (rides, users, drivers)
3. ✅ **Cassandra** for time-series GPS data (high write throughput)
4. ✅ **WebSocket** for real-time location updates
5. ✅ **Distributed locks** to prevent double-assignment

**Tech Stack:**
- Backend: Go/Node.js (high concurrency)
- Database: PostgreSQL (with PostGIS), Cassandra
- Cache: Redis (geo-indexing)
- Queue: Kafka (location updates stream)
- Maps: Google Maps API / Mapbox
- Real-time: WebSocket / Server-Sent Events
