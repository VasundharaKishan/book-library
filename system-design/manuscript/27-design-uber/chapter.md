# Chapter 27: Designing Uber

When you open a ride-hailing app, tap a button, and a car appears at your doorstep within minutes, a remarkable amount of engineering is working behind the scenes. In the time between your request and your driver's arrival, the system has matched you with the best available driver, calculated an estimated arrival time, set dynamic pricing based on supply and demand, and begun tracking both your location and the driver's location in real time.

In this chapter we will design Uber from scratch. You will learn how geospatial indexing works (geohash and quadtree), how the dispatch system matches riders with nearby drivers in milliseconds, how ETA estimation combines routing with real-time traffic data, how surge pricing balances supply and demand, and how real-time location tracking is delivered over WebSocket connections. This is one of the most challenging system design problems because it combines geography, real-time systems, economics, and payments into a single product.

---

## 27.1 Understanding the Problem

Uber's core flow is:

1. **Rider requests a ride** -- specifying pickup and dropoff locations.
2. **System matches a driver** -- finds the best available driver nearby.
3. **Driver accepts and navigates to pickup** -- both rider and driver see each other's location in real time.
4. **Trip begins** -- the system tracks the route and calculates the fare.
5. **Trip ends** -- payment is processed automatically.

### What Makes Uber Uniquely Challenging?

- **Geospatial queries at scale.** "Find all available drivers within 3 km of this location" must execute in milliseconds, millions of times per minute.
- **Real-time location updates.** Millions of drivers send GPS updates every 3-5 seconds. That is hundreds of thousands of writes per second.
- **Two-sided marketplace.** Unlike social networks where users are interchangeable, Uber must balance supply (drivers) and demand (riders) in real time, per location.
- **Time-critical matching.** A rider expects a match within seconds, not minutes. Delayed matching means lost riders.

---

## 27.2 Requirements

### Functional Requirements

| # | Requirement | Description |
|---|-------------|-------------|
| F1 | **Request a ride** | Rider specifies pickup and dropoff. System returns fare estimate and ETA. |
| F2 | **Match driver** | Find and assign the best nearby available driver. |
| F3 | **Real-time tracking** | Both rider and driver see each other's live location during the trip. |
| F4 | **Trip management** | Start trip, navigate, end trip, calculate fare. |
| F5 | **Payment** | Automatically charge the rider and pay the driver after the trip. |
| F6 | **Surge pricing** | Dynamically adjust prices based on real-time supply and demand. |
| F7 | **Driver availability** | Drivers can go online/offline. System tracks their status and location. |

### Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NF1 | **Low latency matching** | Match a driver within 5 seconds of request. |
| NF2 | **Real-time updates** | Location updates delivered within 1 second. |
| NF3 | **High availability** | 99.99% uptime. Ride requests must always work. |
| NF4 | **Scalability** | 20 million rides per day, 5 million concurrent drivers. |
| NF5 | **Accuracy** | ETA accurate within 2 minutes. Fare accurate to the cent. |
| NF6 | **Consistency** | A driver can only be matched to one rider at a time. No double-booking. |

### Out of Scope

- Uber Eats (food delivery).
- Driver onboarding and background checks.
- Autonomous vehicles.
- Multi-stop rides.

---

## 27.3 Back-of-the-Envelope Estimation

### Traffic

| Metric | Value |
|--------|-------|
| Daily rides | 20 million |
| Rides per second | 20M / 86,400 ≈ **230 rides/s** |
| Concurrent drivers online | 5 million |
| Driver location updates | Every 4 seconds |
| Location writes per second | 5M / 4 = **1.25 million writes/s** |
| Rider location queries (during trips) | ~2 million concurrent trips x 1 query/4s = **500,000 reads/s** |

### Storage

| Item | Size |
|------|------|
| Trip record | ~1 KB (pickup, dropoff, route, fare, timestamps) |
| Location history per trip | ~2 KB (GPS points every 4 seconds for ~20 min) |
| **Total per trip** | **~3 KB** |

Daily storage:

```
20M trips/day x 3 KB = 60 GB/day
Yearly: ~22 TB/year
```

Driver location data (ephemeral, in-memory):

```
5M drivers x 50 bytes (lat, lng, timestamp, status) = 250 MB
```

This fits entirely in memory. The geospatial index is an in-memory system.

### Geospatial Query Load

When a rider requests a ride, the system queries nearby drivers:

```
230 ride requests/s x average 50 nearby drivers checked = 11,500 proximity lookups/s
```

Plus periodic re-indexing as drivers move:

```
1.25 million location updates/s requiring index updates
```

---

## 27.4 High-Level Design

```
┌────────────┐                               ┌────────────┐
│   Rider    │                               │   Driver   │
│   App      │                               │   App      │
└─────┬──────┘                               └─────┬──────┘
      │                                            │
      │ ┌───────────────────────────────────────┐  │
      └─▶│           API Gateway /              │◀─┘
         │          Load Balancer               │
         └──────────────┬───────────────────────┘
                        │
      ┌─────────────────┼─────────────────────────┐
      │                 │                         │
┌─────▼─────┐    ┌─────▼──────┐           ┌──────▼──────┐
│   Ride    │    │  Location  │           │   Trip      │
│  Request  │    │  Service   │           │  Service    │
│  Service  │    │            │           │             │
└─────┬─────┘    └─────┬──────┘           └──────┬──────┘
      │                │                         │
┌─────▼─────┐    ┌─────▼──────┐           ┌──────▼──────┐
│  Dispatch │    │ Geospatial │           │  Trip DB    │
│  Service  │    │   Index    │           │  (MySQL)    │
│           │    │  (Redis/   │           └─────────────┘
└─────┬─────┘    │  In-memory)│
      │          └────────────┘           ┌─────────────┐
      │                                   │  Payment    │
      │          ┌────────────┐           │  Service    │
      └─────────▶│   Surge    │           └─────────────┘
                 │  Pricing   │
                 │  Service   │           ┌─────────────┐
                 └────────────┘           │  WebSocket  │
                                          │  (Tracking) │
                                          └─────────────┘
```

### Request Flow: Requesting a Ride

```
1. Rider opens app, enters pickup and dropoff
2. Rider App ──▶ Ride Request Service:
   - Calculate fare estimate (distance + time + surge multiplier)
   - Display to rider
3. Rider confirms ──▶ Ride Request Service:
   - Create ride request record
   - Send to Dispatch Service
4. Dispatch Service:
   a. Query Geospatial Index: "available drivers within 3 km of pickup"
   b. Score candidates (proximity, rating, vehicle type, direction of travel)
   c. Send ride offer to the top driver
5. Driver App ◀── offer via WebSocket
6. Driver accepts ──▶ Dispatch Service:
   a. Mark driver as "on_trip" in Geospatial Index
   b. Create Trip record
   c. Notify rider via WebSocket: "Driver matched!"
7. Real-time tracking begins:
   - Driver location ──▶ Location Service ──▶ WebSocket ──▶ Rider App
   - Rider location ──▶ Location Service ──▶ WebSocket ──▶ Driver App
```

### Request Flow: Driver Rejecting or Timeout

```
If driver does not accept within 15 seconds:
1. Dispatch Service marks the offer as expired
2. Dispatch Service selects the next-best driver
3. Sends new offer
4. Repeat up to 3 times
5. If no driver accepts: notify rider "No drivers available"
```

---

## 27.5 Deep Dive

### 27.5.1 Geospatial Indexing

The fundamental operation is: "Find all available drivers near location (lat, lng) within radius R." There are two main approaches:

#### Geohash

A geohash encodes a (latitude, longitude) pair into a string where nearby locations share a common prefix:

```
Location: (37.7749, -122.4194)  -- San Francisco
Geohash:  9q8yyk8

Precision levels:
  "9"        -- covers ~5,000 km x 5,000 km
  "9q"       -- covers ~1,250 km x 625 km
  "9q8"      -- covers ~156 km x 156 km
  "9q8y"     -- covers ~39 km x 19.5 km
  "9q8yy"    -- covers ~5 km x 5 km
  "9q8yyk"   -- covers ~1.2 km x 0.6 km
  "9q8yyk8"  -- covers ~150 m x 150 m
```

**How to find nearby drivers using geohash**:

```
1. Compute the geohash of the rider's location at precision 6 (≈1 km cell)
2. Find the 8 neighboring geohash cells (to handle edge effects)
3. Query Redis: SMEMBERS drivers:available:{geohash} for each of the 9 cells
4. Filter by exact distance (some drivers in neighboring cells may be too far)
5. Sort by distance and score
```

**Redis data structure**:

```
Key:    drivers:available:{geohash_prefix}
Type:   Set
Members: driver_id values

Example:
  drivers:available:9q8yyk → {driver_101, driver_205, driver_389}
```

When a driver's location updates:
1. Compute old geohash and new geohash.
2. If different: SREM from old cell, SADD to new cell.
3. If same: no index change needed.

#### Quadtree

A quadtree recursively divides the map into four quadrants. Each leaf node contains a manageable number of drivers:

```
┌──────────────────────────────┐
│              │               │
│   NW (12    │   NE (8       │
│   drivers)  │   drivers)    │
│             │               │
├──────────────┼──────────────┤
│              │               │
│   SW         │   SE          │
│   ┌────┬────┐│              │
│   │ 5  │ 3  ││   (45        │
│   ├────┼────┤│   drivers)   │
│   │ 7  │ 15 ││     ──▶      │
│   └────┴────┘│   subdivide! │
│              │               │
└──────────────────────────────┘
```

**Rules**:
- Each cell has a maximum capacity (e.g., 100 drivers).
- When a cell exceeds capacity, subdivide it into 4 children.
- Dense areas (downtown) have many small cells; sparse areas (rural) have few large cells.

**Pros vs. geohash**:

| Aspect | Geohash | Quadtree |
|--------|---------|----------|
| Implementation | Simple (string operations) | More complex (tree structure) |
| Density adaptation | Fixed grid size | Adapts to driver density |
| Query | String prefix matching | Tree traversal |
| Update cost | O(1) hash compute | O(log N) tree traversal |
| Best for | Uniform-ish distribution | Highly variable density |

**Our choice**: **Geohash with Redis** for simplicity and speed. At Uber's scale, the slight inefficiency in sparse areas is outweighed by the simplicity and Redis's performance.

### 27.5.2 Driver Matching (Dispatch)

Finding nearby drivers is just the first step. The dispatch service must pick the **best** driver:

**Scoring factors**:

```
score = w1 * proximity_score
      + w2 * eta_score
      + w3 * driver_rating
      + w4 * heading_score
      + w5 * acceptance_rate
```

| Factor | Description |
|--------|-------------|
| **Proximity** | Straight-line distance to pickup. |
| **ETA** | Actual driving time (accounts for roads, traffic). |
| **Rating** | Higher-rated drivers preferred. |
| **Heading** | Driver already heading toward pickup scores higher (less time to turn around). |
| **Acceptance rate** | Drivers who frequently decline offers are deprioritized. |

**Dispatch algorithm**:

```
1. Query geospatial index for available drivers within 3 km
2. If fewer than 3 candidates, expand to 5 km
3. For each candidate:
   a. Calculate ETA via routing service
   b. Compute score
4. Sort by score (descending)
5. Offer to top-scored driver
6. If declined/timeout (15s), offer to next driver
7. If no match after 3 attempts, expand radius and retry
8. If still no match, inform rider
```

**Preventing double-booking**: When a ride offer is sent to a driver, that driver is temporarily "locked" (status = "offered"). No other ride request can be offered to them. If they decline or timeout, the lock is released.

### 27.5.3 ETA Estimation

ETA (Estimated Time of Arrival) is one of Uber's most critical calculations. An inaccurate ETA leads to frustrated riders and poor driver utilization.

**Components**:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Road Graph  │     │  Real-time   │     │  Historical  │
│  (Map Data)  │     │  Traffic     │     │  Travel Time │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                     ┌──────▼──────┐
                     │  Routing    │
                     │  Engine     │
                     │  (Dijkstra/ │
                     │   A*)       │
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │    ETA      │
                     └─────────────┘
```

**Road graph**: A weighted directed graph where:
- Nodes are intersections.
- Edges are road segments.
- Edge weights are travel times (not distances).

**Real-time traffic**: Edge weights are updated every few minutes based on:
- GPS data from Uber drivers currently on the road.
- Third-party traffic data.
- Time of day and day of week patterns.

**Algorithm**: Modified A* search with traffic-aware edge weights. For long routes, use hierarchical routing (compute on highway graph first, then local roads).

**ETA caching**: For popular routes (e.g., airport to downtown), cache ETAs and refresh every 5 minutes. Avoids recomputing the same routes millions of times.

### 27.5.4 Surge Pricing

Surge pricing dynamically adjusts fares when demand exceeds supply in a geographic area:

```
┌──────────────────────────────────────────────┐
│              Surge Pricing Engine             │
│                                              │
│  For each geographic zone (hexagonal grid):  │
│                                              │
│  demand = ride_requests_last_5min            │
│  supply = available_drivers_in_zone          │
│                                              │
│  ratio = demand / supply                     │
│                                              │
│  if ratio > 1.5:                             │
│      surge_multiplier = f(ratio)              │
│      (e.g., 2.0x, 2.5x, 3.0x)              │
│  else:                                       │
│      surge_multiplier = 1.0                  │
│                                              │
│  Fare = base_fare * surge_multiplier          │
│       + per_mile * distance                   │
│       + per_minute * duration                 │
│       + booking_fee                           │
└──────────────────────────────────────────────┘
```

**Geographic zones**: The city is divided into hexagonal zones (hexagons tile without gaps, unlike squares). Each zone is about 1 km across.

**Update frequency**: Surge multipliers recalculated every 1-2 minutes.

**Smoothing**: To prevent jarring price jumps, apply exponential moving average:

```
new_surge = 0.7 * calculated_surge + 0.3 * previous_surge
```

**Communication**: The rider sees the surge multiplier before confirming. They can wait for the surge to decrease or accept the higher fare.

### 27.5.5 Trip Service

The trip service manages the lifecycle of a ride:

```
States: REQUESTED ──▶ MATCHED ──▶ DRIVER_EN_ROUTE ──▶ ARRIVED
                                                        │
        ──▶ TRIP_STARTED ──▶ TRIP_COMPLETED ──▶ PAYMENT_PROCESSED
```

**Fare calculation** (at trip end):

```
fare = base_fare
     + (distance_miles * per_mile_rate)
     + (duration_minutes * per_minute_rate)
     + surge_multiplier_at_request_time * variable_fare
     + booking_fee
     + tolls
     - promotions / discounts

-- The surge multiplier is locked in at request time, not trip end
```

**Route tracking**: During the trip, the driver's GPS coordinates are recorded every 4 seconds. This forms the actual route, used for:
- Fare calculation (actual distance traveled).
- Detecting route deviations.
- Historical trip display.

### 27.5.6 Payment Service

Payment is processed automatically at the end of each trip:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Trip       │────▶│  Payment     │────▶│  Payment     │
│  Service    │     │  Service     │     │  Gateway     │
│  (fare)     │     │              │     │ (Stripe/     │
└─────────────┘     │  - Auth hold │     │  Braintree)  │
                    │  - Capture   │     └──────────────┘
                    │  - Split     │
                    │    (driver/  │
                    │     Uber)    │
                    └──────────────┘
```

**Authorization hold**: When a rider requests a ride, a hold is placed on their payment method for the estimated fare. This ensures the rider can pay.

**Capture**: After the trip, the actual fare is captured (may differ from the estimate due to route changes).

**Split**: The fare is split between the driver (typically 75-80%) and Uber (20-25%).

**Reliability**: Payment processing uses the saga pattern:
1. Charge rider's payment method.
2. If successful, credit driver's account.
3. If charge fails, retry with exponential backoff.
4. If still fails, mark trip as "payment pending" and notify rider.

### 27.5.7 Real-Time Location Tracking (WebSocket)

During a trip, both rider and driver see each other's live location:

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  Driver  │════▶│  Location    │════▶│  Rider   │
│   App    │WS   │  Service     │WS   │   App    │
│          │     │              │     │          │
│ GPS every│     │ - Validate   │     │ Updates  │
│ 4 seconds│     │ - Store      │     │ on map   │
│          │     │ - Forward    │     │          │
└──────────┘     └──────┬───────┘     └──────────┘
                        │
                 ┌──────▼───────┐
                 │ Geospatial   │
                 │ Index Update │
                 └──────────────┘
```

**Protocol**: WebSocket for persistent bidirectional connection. Falls back to SSE (Server-Sent Events) if WebSocket is blocked.

**Location update flow**:
1. Driver app sends GPS coordinates to Location Service via WebSocket every 4 seconds.
2. Location Service validates the update (reject impossible speeds, out-of-bounds coordinates).
3. Updates the driver's position in the Geospatial Index.
4. If the driver is on a trip, forwards the location to the matched rider via WebSocket.
5. Stores the location in the trip's route history.

**Bandwidth optimization**:
- Send only (lat, lng, timestamp, heading) -- about 30 bytes per update.
- Compress updates using delta encoding: send only the change from the previous position.
- Batch updates on the client side: if the driver has not moved significantly, skip the update.

### 27.5.8 Complete Architecture

Putting it all together:

```
┌──────────────────────────────────────────────────────────────┐
│                        API Gateway                           │
│                     (Load Balancer)                          │
└────────┬──────────┬──────────┬──────────┬──────────┬────────┘
         │          │          │          │          │
  ┌──────▼───┐ ┌───▼─────┐ ┌─▼────────┐│   ┌──────▼───┐
  │  Ride    │ │Location │ │  Trip    ││   │ Payment │
  │  Request │ │Service  │ │ Service  ││   │ Service │
  │  Service │ │         │ │          ││   │         │
  └────┬─────┘ └────┬────┘ └────┬─────┘│   └────┬────┘
       │            │           │      │        │
  ┌────▼─────┐ ┌────▼────┐ ┌───▼──┐   │   ┌────▼────┐
  │ Dispatch │ │Geospatial│ │Trip │   │   │Payment │
  │ Service  │ │  Index   │ │ DB  │   │   │Gateway │
  │          │ │(Redis)   │ │(SQL)│   │   │(Stripe)│
  └────┬─────┘ └─────────┘ └─────┘   │   └────────┘
       │                              │
  ┌────▼─────┐                   ┌────▼─────┐
  │  Surge   │                   │ WebSocket│
  │ Pricing  │                   │ Gateway  │
  │ Service  │                   │(Tracking)│
  └──────────┘                   └──────────┘
       │
  ┌────▼─────┐                   ┌──────────┐
  │ Routing  │                   │  Kafka   │
  │ Engine   │                   │(Events)  │
  │(ETA/Maps)│                   └──────────┘
  └──────────┘
```

---

## 27.6 Database Schema

### Riders Table

```sql
CREATE TABLE riders (
    rider_id        BIGINT PRIMARY KEY,
    name            VARCHAR(100),
    email           VARCHAR(255) UNIQUE,
    phone           VARCHAR(20) UNIQUE,
    rating          DECIMAL(3,2) DEFAULT 5.00,
    payment_method_id VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### Drivers Table

```sql
CREATE TABLE drivers (
    driver_id       BIGINT PRIMARY KEY,
    name            VARCHAR(100),
    email           VARCHAR(255) UNIQUE,
    phone           VARCHAR(20) UNIQUE,
    license_plate   VARCHAR(20),
    vehicle_type    ENUM('economy', 'comfort', 'xl', 'premium'),
    vehicle_make    VARCHAR(50),
    vehicle_model   VARCHAR(50),
    vehicle_color   VARCHAR(30),
    rating          DECIMAL(3,2) DEFAULT 5.00,
    status          ENUM('offline', 'available', 'offered', 'on_trip'),
    created_at      TIMESTAMP DEFAULT NOW(),
    INDEX idx_status (status)
);
```

### Trips Table

```sql
CREATE TABLE trips (
    trip_id             BIGINT PRIMARY KEY,
    rider_id            BIGINT NOT NULL,
    driver_id           BIGINT,
    status              ENUM('requested', 'matched', 'driver_en_route',
                             'arrived', 'in_progress', 'completed',
                             'cancelled'),
    pickup_lat          DECIMAL(10, 7),
    pickup_lng          DECIMAL(10, 7),
    pickup_address      VARCHAR(500),
    dropoff_lat         DECIMAL(10, 7),
    dropoff_lng         DECIMAL(10, 7),
    dropoff_address     VARCHAR(500),
    vehicle_type        ENUM('economy', 'comfort', 'xl', 'premium'),
    surge_multiplier    DECIMAL(3,1) DEFAULT 1.0,
    estimated_fare      DECIMAL(10,2),
    actual_fare         DECIMAL(10,2),
    distance_miles      DECIMAL(8,2),
    duration_minutes    DECIMAL(8,2),
    requested_at        TIMESTAMP,
    matched_at          TIMESTAMP,
    pickup_at           TIMESTAMP,
    dropoff_at          TIMESTAMP,
    created_at          TIMESTAMP DEFAULT NOW(),
    INDEX idx_rider (rider_id, created_at DESC),
    INDEX idx_driver (driver_id, created_at DESC),
    INDEX idx_status (status)
);
-- Sharded by trip_id
```

### Trip Route Points Table

```sql
-- High-write, time-series data: use Cassandra
CREATE TABLE trip_route_points (
    trip_id         BIGINT,
    recorded_at     TIMESTAMP,
    lat             DECIMAL(10, 7),
    lng             DECIMAL(10, 7),
    speed_mph       DECIMAL(5, 1),
    heading         INT,
    PRIMARY KEY (trip_id, recorded_at)
) WITH CLUSTERING ORDER BY (recorded_at ASC);
```

### Geospatial Index (Redis)

```
-- Available drivers indexed by geohash
Key:    drivers:geo:{geohash_6}
Type:   Set
Members: driver_id

-- Driver details (for quick lookup)
Key:    driver:location:{driver_id}
Type:   Hash
Fields: lat, lng, geohash, heading, speed, status, vehicle_type, rating
TTL:    60 seconds (refreshed with each location update)

-- Surge pricing zones
Key:    surge:{zone_id}
Type:   String
Value:  multiplier (e.g., "2.5")
TTL:    120 seconds (refreshed by surge pricing service)
```

### Payments Table

```sql
CREATE TABLE payments (
    payment_id      BIGINT PRIMARY KEY,
    trip_id         BIGINT NOT NULL,
    rider_id        BIGINT NOT NULL,
    driver_id       BIGINT NOT NULL,
    amount          DECIMAL(10,2),
    driver_payout   DECIMAL(10,2),
    platform_fee    DECIMAL(10,2),
    payment_method  VARCHAR(50),
    status          ENUM('authorized', 'captured', 'failed', 'refunded'),
    processed_at    TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW(),
    INDEX idx_trip (trip_id)
);
```

---

## 27.7 API Design

### Request a Ride

```
POST /api/v1/rides/estimate
Authorization: Bearer {token}

Request Body:
{
    "pickup": {"lat": 37.7749, "lng": -122.4194},
    "dropoff": {"lat": 37.3382, "lng": -121.8863},
    "vehicle_type": "economy"
}

Response: 200 OK
{
    "estimates": [
        {
            "vehicle_type": "economy",
            "fare_range": {"min": 42.00, "max": 56.00},
            "surge_multiplier": 1.5,
            "eta_minutes": 4,
            "distance_miles": 45.2,
            "duration_minutes": 55
        },
        {
            "vehicle_type": "comfort",
            "fare_range": {"min": 58.00, "max": 72.00},
            ...
        }
    ]
}
```

### Confirm Ride Request

```
POST /api/v1/rides
Authorization: Bearer {token}

Request Body:
{
    "pickup": {"lat": 37.7749, "lng": -122.4194, "address": "123 Market St"},
    "dropoff": {"lat": 37.3382, "lng": -121.8863, "address": "456 First St"},
    "vehicle_type": "economy",
    "payment_method_id": "pm_abc123"
}

Response: 201 Created
{
    "trip_id": "trip_789",
    "status": "requested",
    "surge_multiplier": 1.5,
    "estimated_fare": 49.00,
    "message": "Finding your driver..."
}
```

### Driver Accept/Decline (WebSocket)

```
-- Server to Driver (offer):
{
    "action": "ride_offer",
    "trip_id": "trip_789",
    "pickup": {"lat": 37.7749, "lng": -122.4194, "address": "123 Market St"},
    "dropoff_address": "456 First St",
    "estimated_fare": 49.00,
    "estimated_distance": 45.2,
    "expires_in_seconds": 15
}

-- Driver to Server (accept):
{
    "action": "accept_ride",
    "trip_id": "trip_789"
}
```

### Update Driver Location (WebSocket)

```
-- Driver to Server (every 4 seconds):
{
    "action": "location_update",
    "lat": 37.7751,
    "lng": -122.4190,
    "heading": 45,
    "speed": 25.5,
    "timestamp": 1705312200000
}
```

### End Trip

```
POST /api/v1/trips/{trip_id}/complete
Authorization: Bearer {driver_token}

Response: 200 OK
{
    "trip_id": "trip_789",
    "status": "completed",
    "actual_fare": 52.30,
    "distance_miles": 46.1,
    "duration_minutes": 58,
    "payment_status": "captured"
}
```

---

## 27.8 Scaling the System

### Geospatial Index Scaling

- **Redis cluster** sharded by geographic region (each city or metro area gets its own Redis cluster).
- Within a city, further shard by geohash prefix (e.g., all geohash cells starting with "9q8" on one shard).
- Each shard handles ~500,000 location updates per second.

### Location Service Scaling

- Stateless service behind a load balancer.
- Auto-scale based on WebSocket connection count.
- Each server handles ~200,000 concurrent WebSocket connections.
- With 5 million concurrent drivers: ~25 location service servers.

### Dispatch Service Scaling

- Partition by city/region. Each region has its own dispatch cluster.
- Within a region, dispatch requests are load-balanced across workers.
- Use distributed locking (Redis SETNX) to prevent double-booking drivers.

### Trip Database Scaling

- MySQL sharded by trip_id.
- Read replicas for queries (trip history, analytics).
- Trip route points stored in Cassandra (write-heavy time-series data).

### Regional Deployment

Uber operates in hundreds of cities. Each city is semi-independent:

```
┌─────────────────────────────────────────────┐
│               Global Services               │
│  (Accounts, Payments, Analytics)            │
└───────────────┬─────────────────────────────┘
                │
    ┌───────────┼───────────────┐
    │           │               │
┌───▼──────┐ ┌─▼──────────┐ ┌─▼──────────┐
│ US-West  │ │ US-East    │ │ Europe     │
│ Region   │ │ Region     │ │ Region     │
│          │ │            │ │            │
│ - SF     │ │ - NYC      │ │ - London   │
│ - LA     │ │ - Chicago  │ │ - Paris    │
│ - Seattle│ │ - Miami    │ │ - Berlin   │
└──────────┘ └────────────┘ └────────────┘
```

Each region has its own:
- Geospatial index (drivers are local).
- Dispatch service (matching is local).
- Location service (low latency for real-time updates).

Global services (payments, accounts) are centralized.

---

## 27.9 Trade-offs

| Decision | Option A | Option B | Our Choice | Why |
|----------|----------|----------|-------------|-----|
| Geospatial index | Quadtree | Geohash + Redis | **Geohash** | Simpler to implement, Redis provides speed and scalability. |
| Driver matching | Nearest driver | Scored matching | **Scored** | Nearest is not always best (ETA, heading, rating matter). |
| Pricing | Fixed | Dynamic (surge) | **Dynamic** | Balances supply and demand in real time. |
| Location updates | HTTP polling | WebSocket | **WebSocket** | 1.25M updates/s is only feasible with persistent connections. |
| Trip data | Single DB | MySQL + Cassandra | **Hybrid** | Trip metadata in MySQL (relational queries), GPS points in Cassandra (write-heavy time-series). |
| Dispatch scope | Global | Per-city | **Per-city** | Matching is inherently local; global dispatch adds unnecessary latency. |
| Fare calculation | Pre-trip estimate only | Post-trip actual | **Both** | Estimate for transparency; actual for accuracy. Surge locked at request time. |

---

## 27.10 Common Mistakes

1. **Using a relational database for the geospatial index.** SQL spatial queries are too slow for 1.25 million location updates per second. Use an in-memory solution like Redis.

2. **Matching the nearest driver only.** The nearest driver by straight-line distance may be across a river with no bridge. Use ETA (actual driving time) as the primary matching criterion.

3. **Ignoring driver double-booking.** Without proper locking, two concurrent ride requests could match the same driver. Use distributed locks or atomic operations.

4. **Forgetting surge pricing.** If you design a fixed-pricing system, the interviewer will ask what happens at peak times when demand exceeds supply. Discuss surge pricing proactively.

5. **Not separating the dispatch into geographic regions.** A rider in San Francisco should never be matched with a driver in New York. Regional partitioning is not optional.

6. **Treating payment as trivial.** Payment involves authorization holds, capture, splits, refunds, and fraud detection. At least mention the saga pattern and idempotency.

---

## 27.11 Best Practices

1. **Lock the surge multiplier at request time.** If the rider sees a 1.5x surge and confirms, they pay 1.5x even if the surge increases to 2.0x during the trip. This builds trust.

2. **Use exponential backoff for driver matching.** Start with a small radius (2 km). If no drivers, expand to 5 km, then 10 km. Do not search the entire city from the start.

3. **Store raw GPS data for every trip.** This is essential for fare disputes, safety investigations, and route optimization training data.

4. **Implement graceful degradation.** If the surge pricing service is down, fall back to 1.0x (no surge). If the routing engine is slow, use straight-line distance estimates temporarily.

5. **Pre-compute popular ETAs.** Airport-to-downtown, major landmarks, business districts -- these routes are requested thousands of times per day. Cache the results.

6. **Use hexagonal grids for surge zones.** Hexagons have uniform neighbor distances (unlike squares with diagonal neighbors), making surge calculations more consistent.

---

## 27.12 Quick Summary

Uber's architecture centers on four pillars: (1) a geohash-based geospatial index in Redis that supports 1.25 million driver location updates per second and millisecond proximity queries; (2) a scored dispatch system that matches riders with the best available driver based on ETA, rating, heading, and acceptance rate, with distributed locking to prevent double-booking; (3) real-time location tracking over WebSocket connections, enabling both rider and driver to see each other's positions during a trip; and (4) a dynamic surge pricing engine that recalculates supply/demand ratios per geographic zone every 1-2 minutes. The system is partitioned by city/region for locality, with global services for payments and accounts.

---

## 27.13 Key Points

- **Geohash + Redis** provides fast geospatial indexing for finding nearby drivers in milliseconds.
- **Scored dispatch** considers ETA, rating, heading, and acceptance rate -- not just distance.
- **Distributed locking** prevents double-booking drivers across concurrent ride requests.
- **WebSocket connections** deliver real-time location updates every 4 seconds during trips.
- **Surge pricing** uses hexagonal zones with supply/demand ratios recalculated every 1-2 minutes.
- **ETA estimation** combines road graph routing (A*) with real-time traffic data from driver GPS signals.
- **Payment processing** uses authorization holds at request time and capture at trip end, with saga pattern for reliability.
- **Regional partitioning** keeps dispatch, geospatial index, and location services local to each city.
- **Trip route tracking** stores GPS points in Cassandra for fare calculation, disputes, and analytics.
- **Surge multiplier is locked at request time** to build rider trust and prevent surprise charges.

---

## 27.14 Practice Questions

1. How would you handle the case where a driver's GPS signal is lost during a trip? How do you calculate the fare if you are missing route data?

2. At 3 AM on New Year's Eve, demand spikes 20x and almost no drivers are available. How does the system behave? What prevents the surge multiplier from going infinitely high?

3. A rider requests a ride at the exact border of two geohash cells. How do you ensure you find the nearest driver who might be in either cell?

4. How would you implement ride-sharing (UberPool) where multiple riders share a vehicle? How does matching and routing change?

5. If a driver's app crashes mid-trip, what happens? How does the system detect this and recover?

---

## 27.15 Exercises

1. **Geohash implementation**: Write pseudocode to encode a (latitude, longitude) pair into a geohash string of precision 6. Then write the function to find the 8 neighboring geohash cells.

2. **Dispatch simulation**: Given a list of 10 available drivers (each with lat, lng, rating, heading), a rider's pickup location, and a simple scoring formula, write pseudocode for the dispatch algorithm that returns the best driver.

3. **Surge pricing model**: Design a surge pricing model for a city divided into 100 hexagonal zones. Define the data structures, the update frequency, and the formula for calculating the surge multiplier. Handle edge cases: what happens when supply is zero?

4. **Capacity planning**: Calculate the number of Redis nodes needed for the geospatial index in a city with 500,000 concurrent drivers, assuming each driver occupies 100 bytes and each Redis node has 32 GB of RAM. Include overhead for geohash sets.

5. **Failure scenario**: The Redis cluster holding the geospatial index goes down for 5 minutes. Design a recovery strategy that minimizes rider impact. Can you still match rides? How do you rebuild the index?

---

## 27.16 What Is Next?

In this chapter we designed a real-time ride-hailing system with geospatial indexing, driver dispatch, surge pricing, and live location tracking. This was one of the most complex designs in this book, combining real-time systems, geography, economics, and payments into a single coherent architecture. In the next chapter, **Chapter 28: Designing a Notification Service**, we will design the system responsible for delivering push notifications, emails, and SMS messages at scale -- a service that many of the systems we have designed in previous chapters depend on.
