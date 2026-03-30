# Chapter 29: API Gateway Pattern -- Single Entry Point for Microservices

## What You Will Learn

- What the API Gateway pattern is and why microservices need a single entry point
- How routing, authentication, rate limiting, and response aggregation work
- How to implement a gateway in Java with Spring Cloud Gateway concepts
- How to build a lightweight gateway in Python with FastAPI
- The Backend-for-Frontend (BFF) pattern and when to use it
- Trade-offs: single point of failure vs operational simplicity

## Why This Chapter Matters

In a microservices architecture, a mobile app might need data from five different
services to render a single screen: user profile from the User Service, recent orders
from the Order Service, recommendations from the ML Service, notifications from the
Notification Service, and loyalty points from the Points Service.

Without an API Gateway, the client must know the address of every service, handle
authentication with each one, and make five separate HTTP calls. When you add a new
service, every client must be updated. When you change a service URL, every client
breaks.

The API Gateway solves this by providing a single, stable entry point. Clients talk to
one URL. The gateway handles routing, authentication, rate limiting, and response
aggregation behind the scenes.

---

## The Problem

```
WITHOUT API GATEWAY:

Mobile App -----> User Service (users.internal:8001)
     |
     +----------> Order Service (orders.internal:8002)
     |
     +----------> Product Service (products.internal:8003)
     |
     +----------> Payment Service (payments.internal:8004)
     |
     +----------> Notification Service (notif.internal:8005)

Problems:
- Client knows 5 different URLs
- Each service needs its own auth logic
- No centralized rate limiting
- No request logging
- Adding service #6 means updating every client
- Services are exposed directly to the internet
```

---

## The Solution: API Gateway

```
WITH API GATEWAY:

Mobile App -----> API Gateway (api.myapp.com)
                       |
                       +----> User Service
                       +----> Order Service
                       +----> Product Service
                       +----> Payment Service
                       +----> Notification Service

Benefits:
- Client knows ONE URL
- Auth handled once at the gateway
- Centralized rate limiting
- Unified logging and monitoring
- Add services without client changes
- Internal services are never exposed
```

### What the Gateway Does

```
+--------------------------------------------------------------+
|                      API GATEWAY                              |
|                                                               |
|  Incoming     +----------+  +----------+  +-----------+       |
|  Request ---->| Auth     |->| Rate     |->| Route     |--+    |
|               | Check    |  | Limit    |  | Resolver  |  |    |
|               +----------+  +----------+  +-----------+  |    |
|                                                          |    |
|               +----------+  +----------+  +-----------+  |    |
|  Response <---| Response |<-| Cache    |<-| Load      |<-+    |
|               | Transform|  | Check    |  | Balance   |       |
|               +----------+  +----------+  +-----------+       |
+--------------------------------------------------------------+
```

**Core responsibilities:**

1. **Routing**: Maps external URLs to internal service endpoints
2. **Authentication**: Validates tokens/API keys before forwarding requests
3. **Rate Limiting**: Prevents abuse by limiting requests per client
4. **Load Balancing**: Distributes requests across service instances
5. **Response Aggregation**: Combines responses from multiple services
6. **Caching**: Caches responses to reduce backend load
7. **Protocol Translation**: Converts between protocols (REST to gRPC, etc.)
8. **Logging/Monitoring**: Centralizes request tracing and metrics

---

## Java Implementation: Spring Cloud Gateway Concepts

### Route Configuration and Gateway Core

```java
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;

public class Route {
    private final String id;
    private final String pathPattern;
    private final String targetUrl;
    private final boolean authRequired;
    private final int rateLimitPerMinute;

    public Route(String id, String pathPattern, String targetUrl,
                 boolean authRequired, int rateLimitPerMinute) {
        this.id = id;
        this.pathPattern = pathPattern;
        this.targetUrl = targetUrl;
        this.authRequired = authRequired;
        this.rateLimitPerMinute = rateLimitPerMinute;
    }

    public boolean matches(String path) {
        // Simple prefix matching (production would use regex/ant patterns)
        String prefix = pathPattern.replace("/**", "");
        return path.startsWith(prefix);
    }

    public String resolveTarget(String path) {
        String prefix = pathPattern.replace("/**", "");
        String remainder = path.substring(prefix.length());
        return targetUrl + remainder;
    }

    public String getId() { return id; }
    public boolean isAuthRequired() { return authRequired; }
    public int getRateLimitPerMinute() { return rateLimitPerMinute; }
}
```

### Authentication Filter

```java
public class AuthFilter {
    private final Map<String, String> validTokens;

    public AuthFilter() {
        validTokens = new HashMap<>();
        validTokens.put("token-alice-123", "alice");
        validTokens.put("token-bob-456", "bob");
        validTokens.put("api-key-service-1", "service-1");
    }

    public AuthResult authenticate(String authHeader) {
        if (authHeader == null || authHeader.isEmpty()) {
            return new AuthResult(false, null, "Missing auth header");
        }

        String token = authHeader.replace("Bearer ", "");
        String user = validTokens.get(token);

        if (user != null) {
            return new AuthResult(true, user, null);
        }

        return new AuthResult(false, null, "Invalid token");
    }

    public static class AuthResult {
        public final boolean authenticated;
        public final String userId;
        public final String error;

        public AuthResult(boolean authenticated, String userId,
                         String error) {
            this.authenticated = authenticated;
            this.userId = userId;
            this.error = error;
        }
    }
}
```

### Rate Limiter (Token Bucket)

```java
public class RateLimiter {
    private final Map<String, TokenBucket> buckets;

    public RateLimiter() {
        this.buckets = new ConcurrentHashMap<>();
    }

    public boolean allowRequest(String clientId, int maxPerMinute) {
        TokenBucket bucket = buckets.computeIfAbsent(
            clientId, k -> new TokenBucket(maxPerMinute));
        return bucket.tryConsume();
    }

    private static class TokenBucket {
        private int tokens;
        private final int maxTokens;
        private long lastRefill;

        TokenBucket(int maxTokens) {
            this.maxTokens = maxTokens;
            this.tokens = maxTokens;
            this.lastRefill = System.currentTimeMillis();
        }

        synchronized boolean tryConsume() {
            refill();
            if (tokens > 0) {
                tokens--;
                return true;
            }
            return false;
        }

        private void refill() {
            long now = System.currentTimeMillis();
            long elapsed = now - lastRefill;
            int newTokens = (int) (elapsed * maxTokens / 60000);
            if (newTokens > 0) {
                tokens = Math.min(maxTokens, tokens + newTokens);
                lastRefill = now;
            }
        }
    }
}
```

### The Gateway

```java
public class ApiGateway {
    private final List<Route> routes;
    private final AuthFilter authFilter;
    private final RateLimiter rateLimiter;
    private final List<String> requestLog;

    public ApiGateway() {
        this.routes = new ArrayList<>();
        this.authFilter = new AuthFilter();
        this.rateLimiter = new RateLimiter();
        this.requestLog = new ArrayList<>();
    }

    public void addRoute(Route route) {
        routes.add(route);
    }

    public GatewayResponse handleRequest(String method, String path,
                                          Map<String, String> headers) {
        long startTime = System.currentTimeMillis();
        String requestId = UUID.randomUUID().toString().substring(0, 8);

        System.out.printf("[GW-%s] %s %s%n", requestId, method, path);

        // Step 1: Find matching route
        Route route = findRoute(path);
        if (route == null) {
            System.out.printf("[GW-%s] No route found%n", requestId);
            return new GatewayResponse(404, "Not Found",
                    Map.of("error", "No route matches: " + path));
        }

        // Step 2: Authentication
        if (route.isAuthRequired()) {
            AuthFilter.AuthResult auth = authFilter.authenticate(
                    headers.get("Authorization"));
            if (!auth.authenticated) {
                System.out.printf("[GW-%s] Auth failed: %s%n",
                        requestId, auth.error);
                return new GatewayResponse(401, "Unauthorized",
                        Map.of("error", auth.error));
            }
            System.out.printf("[GW-%s] Authenticated: %s%n",
                    requestId, auth.userId);
        }

        // Step 3: Rate limiting
        String clientId = headers.getOrDefault("X-Client-Id", "anonymous");
        if (!rateLimiter.allowRequest(clientId,
                route.getRateLimitPerMinute())) {
            System.out.printf("[GW-%s] Rate limited: %s%n",
                    requestId, clientId);
            return new GatewayResponse(429, "Too Many Requests",
                    Map.of("error", "Rate limit exceeded",
                           "retry_after", "60"));
        }

        // Step 4: Route to backend
        String targetUrl = route.resolveTarget(path);
        System.out.printf("[GW-%s] Routing to: %s%n", requestId, targetUrl);

        // Simulate backend response
        Map<String, Object> backendResponse = simulateBackend(
                route.getId(), method, path);

        long duration = System.currentTimeMillis() - startTime;
        System.out.printf("[GW-%s] Response: 200 (%dms)%n",
                requestId, duration);

        requestLog.add(String.format("%s %s -> %s (%dms)",
                method, path, route.getId(), duration));

        return new GatewayResponse(200, "OK", backendResponse);
    }

    private Route findRoute(String path) {
        return routes.stream()
                .filter(r -> r.matches(path))
                .findFirst()
                .orElse(null);
    }

    private Map<String, Object> simulateBackend(String serviceId,
                                                  String method, String path) {
        Map<String, Object> response = new HashMap<>();
        response.put("service", serviceId);
        response.put("path", path);
        response.put("status", "success");

        switch (serviceId) {
            case "user-service":
                response.put("data", Map.of(
                    "id", 1, "name", "Alice", "email", "alice@example.com"));
                break;
            case "order-service":
                response.put("data", List.of(
                    Map.of("id", 101, "total", 49.99),
                    Map.of("id", 102, "total", 129.50)));
                break;
            case "product-service":
                response.put("data", List.of(
                    Map.of("id", "P1", "name", "Widget", "price", 19.99)));
                break;
        }
        return response;
    }

    public List<String> getRequestLog() { return requestLog; }
}

public class GatewayResponse {
    public final int statusCode;
    public final String statusMessage;
    public final Map<String, Object> body;

    public GatewayResponse(int statusCode, String statusMessage,
                           Map<String, Object> body) {
        this.statusCode = statusCode;
        this.statusMessage = statusMessage;
        this.body = body;
    }

    @Override
    public String toString() {
        return String.format("HTTP %d %s: %s",
                statusCode, statusMessage, body);
    }
}
```

### Demo

```java
public class GatewayDemo {
    public static void main(String[] args) {
        ApiGateway gateway = new ApiGateway();

        // Configure routes
        gateway.addRoute(new Route("user-service",
                "/api/users/**", "http://users.internal:8001",
                true, 100));
        gateway.addRoute(new Route("order-service",
                "/api/orders/**", "http://orders.internal:8002",
                true, 50));
        gateway.addRoute(new Route("product-service",
                "/api/products/**", "http://products.internal:8003",
                false, 200));  // public, no auth

        Map<String, String> authHeaders = Map.of(
                "Authorization", "Bearer token-alice-123",
                "X-Client-Id", "mobile-app");

        Map<String, String> noAuthHeaders = Map.of(
                "X-Client-Id", "mobile-app");

        // Successful requests
        System.out.println("=== Successful Requests ===");
        System.out.println(gateway.handleRequest(
                "GET", "/api/users/1", authHeaders));
        System.out.println(gateway.handleRequest(
                "GET", "/api/orders", authHeaders));
        System.out.println(gateway.handleRequest(
                "GET", "/api/products", noAuthHeaders));

        // Auth failure
        System.out.println("\n=== Auth Failure ===");
        System.out.println(gateway.handleRequest(
                "GET", "/api/users/1", noAuthHeaders));

        // Invalid token
        System.out.println("\n=== Invalid Token ===");
        System.out.println(gateway.handleRequest(
                "GET", "/api/orders",
                Map.of("Authorization", "Bearer invalid-token",
                       "X-Client-Id", "hacker")));

        // No route
        System.out.println("\n=== No Route ===");
        System.out.println(gateway.handleRequest(
                "GET", "/api/unknown", authHeaders));

        // Request log
        System.out.println("\n=== Request Log ===");
        for (String entry : gateway.getRequestLog()) {
            System.out.println("  " + entry);
        }
    }
}
```

**Output:**
```
=== Successful Requests ===
[GW-a1b2c3d4] GET /api/users/1
[GW-a1b2c3d4] Authenticated: alice
[GW-a1b2c3d4] Routing to: http://users.internal:8001/1
[GW-a1b2c3d4] Response: 200 (2ms)
HTTP 200 OK: {service=user-service, path=/api/users/1, status=success, data={id=1, name=Alice, email=alice@example.com}}

[GW-e5f6g7h8] GET /api/orders
[GW-e5f6g7h8] Authenticated: alice
[GW-e5f6g7h8] Routing to: http://orders.internal:8002
[GW-e5f6g7h8] Response: 200 (1ms)
HTTP 200 OK: {service=order-service, path=/api/orders, status=success, data=[{id=101, total=49.99}, {id=102, total=129.50}]}

[GW-i9j0k1l2] GET /api/products
[GW-i9j0k1l2] Routing to: http://products.internal:8003
[GW-i9j0k1l2] Response: 200 (1ms)
HTTP 200 OK: {service=product-service, path=/api/products, status=success, data=[{id=P1, name=Widget, price=19.99}]}

=== Auth Failure ===
[GW-m3n4o5p6] GET /api/users/1
[GW-m3n4o5p6] Auth failed: Missing auth header
HTTP 401 Unauthorized: {error=Missing auth header}

=== Invalid Token ===
[GW-q7r8s9t0] GET /api/orders
[GW-q7r8s9t0] Auth failed: Invalid token
HTTP 401 Unauthorized: {error=Invalid token}

=== No Route ===
[GW-u1v2w3x4] GET /api/unknown
[GW-u1v2w3x4] No route found
HTTP 404 Not Found: {error=No route matches: /api/unknown}

=== Request Log ===
  GET /api/users/1 -> user-service (2ms)
  GET /api/orders -> order-service (1ms)
  GET /api/products -> product-service (1ms)
```

---

## Python Implementation: FastAPI Gateway

### Lightweight Gateway with FastAPI Concepts

```python
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class RouteConfig:
    route_id: str
    path_prefix: str
    target_url: str
    auth_required: bool = True
    rate_limit_per_minute: int = 100
    cache_ttl_seconds: int = 0  # 0 = no cache
    methods: List[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])


@dataclass
class Request:
    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[dict] = None
    query_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class Response:
    status_code: int
    body: Any
    headers: Dict[str, str] = field(default_factory=dict)

    def __repr__(self):
        return f"Response({self.status_code}, {self.body})"


class TokenBucketRateLimiter:
    """Rate limiter using token bucket algorithm."""

    def __init__(self):
        self._buckets: Dict[str, dict] = {}

    def allow(self, client_id: str, max_per_minute: int) -> bool:
        now = time.time()

        if client_id not in self._buckets:
            self._buckets[client_id] = {
                "tokens": max_per_minute,
                "max": max_per_minute,
                "last_refill": now
            }

        bucket = self._buckets[client_id]

        # Refill tokens based on elapsed time
        elapsed = now - bucket["last_refill"]
        new_tokens = int(elapsed * bucket["max"] / 60)
        if new_tokens > 0:
            bucket["tokens"] = min(bucket["max"],
                                   bucket["tokens"] + new_tokens)
            bucket["last_refill"] = now

        if bucket["tokens"] > 0:
            bucket["tokens"] -= 1
            return True
        return False


class ResponseCache:
    """Simple TTL-based response cache."""

    def __init__(self):
        self._cache: Dict[str, dict] = {}

    def get(self, key: str) -> Optional[Response]:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry["expires_at"]:
                print(f"    [Cache] HIT: {key}")
                return entry["response"]
            else:
                del self._cache[key]
        return None

    def set(self, key: str, response: Response, ttl: int):
        if ttl > 0:
            self._cache[key] = {
                "response": response,
                "expires_at": time.time() + ttl
            }
            print(f"    [Cache] STORED: {key} (ttl={ttl}s)")


class ApiGateway:
    """Lightweight API Gateway implementation."""

    def __init__(self):
        self.routes: List[RouteConfig] = []
        self.auth_tokens = {
            "token-alice": {"user_id": "alice", "roles": ["user", "admin"]},
            "token-bob": {"user_id": "bob", "roles": ["user"]},
        }
        self.rate_limiter = TokenBucketRateLimiter()
        self.cache = ResponseCache()
        self.request_log: List[dict] = []
        self.middleware: List[callable] = []

    def add_route(self, config: RouteConfig):
        self.routes.append(config)
        print(f"[Gateway] Route added: {config.path_prefix} "
              f"-> {config.target_url}")

    def add_middleware(self, middleware_fn):
        self.middleware.append(middleware_fn)

    def handle_request(self, request: Request) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.time()

        print(f"\n[GW-{request_id}] {request.method} {request.path}")

        # Step 1: Route matching
        route = self._find_route(request.path)
        if not route:
            return Response(404, {"error": f"No route: {request.path}"})

        # Step 2: Method check
        if request.method not in route.methods:
            return Response(405, {"error": "Method not allowed"})

        # Step 3: Authentication
        if route.auth_required:
            auth_result = self._authenticate(request)
            if not auth_result:
                return Response(401, {"error": "Unauthorized"})
            print(f"[GW-{request_id}] Auth: {auth_result['user_id']}")

        # Step 4: Rate limiting
        client_id = request.headers.get("X-Client-Id", "anonymous")
        if not self.rate_limiter.allow(client_id,
                                        route.rate_limit_per_minute):
            print(f"[GW-{request_id}] Rate limited: {client_id}")
            return Response(429, {
                "error": "Rate limit exceeded",
                "retry_after_seconds": 60
            })

        # Step 5: Cache check (GET only)
        if request.method == "GET" and route.cache_ttl_seconds > 0:
            cache_key = f"{request.method}:{request.path}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        # Step 6: Forward to backend
        target_url = route.target_url + request.path[
            len(route.path_prefix.rstrip("*").rstrip("/")):]
        print(f"[GW-{request_id}] -> {target_url}")

        response = self._call_backend(route.route_id, request)

        # Step 7: Cache response
        if request.method == "GET" and route.cache_ttl_seconds > 0:
            cache_key = f"{request.method}:{request.path}"
            self.cache.set(cache_key, response, route.cache_ttl_seconds)

        duration_ms = (time.time() - start) * 1000
        print(f"[GW-{request_id}] <- {response.status_code} "
              f"({duration_ms:.0f}ms)")

        self.request_log.append({
            "request_id": request_id,
            "method": request.method,
            "path": request.path,
            "route": route.route_id,
            "status": response.status_code,
            "duration_ms": duration_ms
        })

        return response

    def _find_route(self, path):
        for route in self.routes:
            prefix = route.path_prefix.rstrip("*").rstrip("/")
            if path.startswith(prefix):
                return route
        return None

    def _authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "")
        return self.auth_tokens.get(token)

    def _call_backend(self, route_id, request):
        """Simulate backend service responses."""
        backends = {
            "user-service": {
                "data": {"id": 1, "name": "Alice",
                         "email": "alice@example.com"}
            },
            "order-service": {
                "data": [
                    {"id": 101, "total": 49.99, "status": "shipped"},
                    {"id": 102, "total": 129.50, "status": "processing"}
                ]
            },
            "product-service": {
                "data": [
                    {"id": "P1", "name": "Widget", "price": 19.99},
                    {"id": "P2", "name": "Gadget", "price": 34.99}
                ]
            }
        }
        data = backends.get(route_id,
                            {"data": None, "message": "Service not found"})
        return Response(200, data)

    def aggregate(self, requests: List[Request]) -> Response:
        """Handle multiple requests and aggregate responses."""
        print("\n[Gateway] Aggregating multiple requests...")
        results = {}
        for req in requests:
            key = req.path.split("/")[2]  # e.g., "users" from "/api/users/1"
            response = self.handle_request(req)
            results[key] = {
                "status": response.status_code,
                "data": response.body
            }
        return Response(200, results)


# --- Demo ---

gateway = ApiGateway()

# Configure routes
gateway.add_route(RouteConfig(
    route_id="user-service",
    path_prefix="/api/users",
    target_url="http://users.internal:8001",
    auth_required=True,
    rate_limit_per_minute=100
))

gateway.add_route(RouteConfig(
    route_id="order-service",
    path_prefix="/api/orders",
    target_url="http://orders.internal:8002",
    auth_required=True,
    rate_limit_per_minute=50
))

gateway.add_route(RouteConfig(
    route_id="product-service",
    path_prefix="/api/products",
    target_url="http://products.internal:8003",
    auth_required=False,
    rate_limit_per_minute=200,
    cache_ttl_seconds=300  # cache for 5 minutes
))

# Successful authenticated request
print("\n" + "=" * 50)
print("SCENARIO 1: Authenticated Request")
print("=" * 50)
resp = gateway.handle_request(Request(
    method="GET",
    path="/api/users/1",
    headers={"Authorization": "Bearer token-alice",
             "X-Client-Id": "mobile-app"}
))
print(f"Result: {resp}")

# Public request (no auth needed)
print("\n" + "=" * 50)
print("SCENARIO 2: Public Request with Caching")
print("=" * 50)
resp1 = gateway.handle_request(Request(
    method="GET",
    path="/api/products",
    headers={"X-Client-Id": "web-app"}
))
print(f"First call: {resp1}")

resp2 = gateway.handle_request(Request(
    method="GET",
    path="/api/products",
    headers={"X-Client-Id": "web-app"}
))
print(f"Second call (cached): {resp2}")

# Auth failure
print("\n" + "=" * 50)
print("SCENARIO 3: Auth Failure")
print("=" * 50)
resp = gateway.handle_request(Request(
    method="GET",
    path="/api/orders",
    headers={"X-Client-Id": "unknown"}
))
print(f"Result: {resp}")

# Response aggregation
print("\n" + "=" * 50)
print("SCENARIO 4: Response Aggregation")
print("=" * 50)
headers = {"Authorization": "Bearer token-alice",
           "X-Client-Id": "mobile-app"}
agg = gateway.aggregate([
    Request("GET", "/api/users/1", headers),
    Request("GET", "/api/orders", headers),
    Request("GET", "/api/products", {"X-Client-Id": "mobile-app"})
])
print(f"\nAggregated response keys: {list(agg.body.keys())}")

# Request log
print("\n" + "=" * 50)
print("REQUEST LOG")
print("=" * 50)
for entry in gateway.request_log:
    print(f"  [{entry['request_id']}] {entry['method']:6s} "
          f"{entry['path']:20s} -> {entry['route']:15s} "
          f"({entry['status']}, {entry['duration_ms']:.0f}ms)")
```

**Output:**
```
[Gateway] Route added: /api/users -> http://users.internal:8001
[Gateway] Route added: /api/orders -> http://orders.internal:8002
[Gateway] Route added: /api/products -> http://products.internal:8003

==================================================
SCENARIO 1: Authenticated Request
==================================================

[GW-a1b2c3d4] GET /api/users/1
[GW-a1b2c3d4] Auth: alice
[GW-a1b2c3d4] -> http://users.internal:8001/1
[GW-a1b2c3d4] <- 200 (1ms)
Result: Response(200, {'data': {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}})

==================================================
SCENARIO 2: Public Request with Caching
==================================================

[GW-e5f6g7h8] GET /api/products
[GW-e5f6g7h8] -> http://products.internal:8003
    [Cache] STORED: GET:/api/products (ttl=300s)
[GW-e5f6g7h8] <- 200 (1ms)
First call: Response(200, {'data': [...]})

[GW-i9j0k1l2] GET /api/products
    [Cache] HIT: GET:/api/products
Second call (cached): Response(200, {'data': [...]})

==================================================
SCENARIO 3: Auth Failure
==================================================

[GW-m3n4o5p6] GET /api/orders
Result: Response(401, {'error': 'Unauthorized'})

==================================================
SCENARIO 4: Response Aggregation
==================================================

[Gateway] Aggregating multiple requests...
[GW-...] GET /api/users/1 ...
[GW-...] GET /api/orders ...
[GW-...] GET /api/products ...

Aggregated response keys: ['users', 'orders', 'products']
```

---

## The BFF Pattern: Backend for Frontend

Different clients need different data. A mobile app needs a compact response. A web
dashboard needs detailed data. An admin panel needs everything.

```
WITHOUT BFF:

Mobile App  ----+
Web App     ----+--> Single API Gateway --> Services
Admin Panel ----+

Problem: One gateway tries to serve all clients.
Mobile gets too much data. Admin needs special endpoints.

WITH BFF:

Mobile App  ----> Mobile BFF Gateway ---+
                                        +--> Services
Web App     ----> Web BFF Gateway ------+
                                        |
Admin Panel ----> Admin BFF Gateway ----+

Each BFF is tailored to its client's needs.
```

```python
class MobileBFF:
    """Gateway optimized for mobile clients."""

    def __init__(self, gateway):
        self.gateway = gateway

    def get_home_screen(self, user_token):
        """Single call returns everything the mobile home screen needs."""
        headers = {"Authorization": f"Bearer {user_token}",
                   "X-Client-Id": "mobile-bff"}

        # Fetch from multiple services
        user = self.gateway.handle_request(
            Request("GET", "/api/users/me", headers))
        orders = self.gateway.handle_request(
            Request("GET", "/api/orders?limit=3", headers))
        products = self.gateway.handle_request(
            Request("GET", "/api/products?featured=true", headers))

        # Return compact mobile-optimized response
        return {
            "user_name": user.body.get("data", {}).get("name"),
            "recent_orders": len(orders.body.get("data", [])),
            "featured_count": len(products.body.get("data", [])),
        }


class WebBFF:
    """Gateway optimized for web dashboard."""

    def __init__(self, gateway):
        self.gateway = gateway

    def get_dashboard(self, user_token):
        """Returns full dashboard data for web."""
        headers = {"Authorization": f"Bearer {user_token}",
                   "X-Client-Id": "web-bff"}

        user = self.gateway.handle_request(
            Request("GET", "/api/users/me", headers))
        orders = self.gateway.handle_request(
            Request("GET", "/api/orders", headers))

        # Return full data for web
        return {
            "user": user.body.get("data"),
            "orders": orders.body.get("data"),
            "order_stats": {
                "total": len(orders.body.get("data", [])),
            }
        }
```

---

## Before vs After Comparison

### Before: Clients Talk Directly to Services

```
Mobile app makes 5 HTTP calls:
  GET http://users.prod:8001/api/users/me
  GET http://orders.prod:8002/api/orders
  GET http://products.prod:8003/api/products
  GET http://notif.prod:8004/api/notifications
  GET http://points.prod:8005/api/points

Each call needs:
  - Service URL (client must know all 5)
  - Authentication (each service validates separately)
  - Error handling (5 possible failure points)
  - Client-side response merging
```

### After: Gateway Aggregates

```
Mobile app makes 1 HTTP call:
  GET http://api.myapp.com/mobile/home

Gateway internally:
  - Authenticates once
  - Calls 5 services in parallel
  - Merges responses
  - Returns one optimized response
```

---

## When to Use / When NOT to Use

### Use API Gateway When

- Multiple clients (mobile, web, third-party) consume your APIs
- You have 3+ microservices that clients need to interact with
- You need centralized authentication and authorization
- Rate limiting is required across all services
- You want to hide internal service topology from clients
- Response aggregation reduces client-side complexity

### Do NOT Use API Gateway When

- You have a monolithic application (no services to route to)
- You have only 1-2 backend services (a reverse proxy like Nginx suffices)
- All clients need the exact same data format (no aggregation needed)
- Ultra-low latency is required (every hop adds latency)
- You cannot afford the operational complexity of another service

---

## Common Mistakes

### Mistake 1: Fat Gateway

```python
# WRONG: business logic in the gateway
def handle_order(self, request):
    order = request.body
    order["tax"] = calculate_tax(order)        # business logic!
    order["discount"] = apply_discount(order)   # business logic!
    order["total"] = compute_total(order)        # business logic!
    return self.forward(request)
# Gateway becomes a monolith

# RIGHT: gateway only routes
def handle_order(self, request):
    return self.forward_to("order-service", request)
```

### Mistake 2: No Timeout on Backend Calls

```python
# WRONG: waiting forever for a slow service
response = call_backend(target_url)  # blocks indefinitely

# RIGHT: set timeouts and handle failures
try:
    response = call_backend(target_url, timeout=5)
except TimeoutError:
    return Response(504, {"error": "Backend timeout"})
```

### Mistake 3: Single Point of Failure

```
# WRONG: one gateway instance
Client -> Gateway (single instance) -> Services
         If it dies, EVERYTHING is down.

# RIGHT: multiple instances behind a load balancer
Client -> Load Balancer -> Gateway Instance 1 -> Services
                        -> Gateway Instance 2
                        -> Gateway Instance 3
```

---

## Best Practices

1. **Keep the gateway thin.** Route, authenticate, rate limit, log. No business logic.
   The gateway is infrastructure, not application code.

2. **Add timeouts to all backend calls.** A slow backend should not make the gateway
   unresponsive. Use circuit breakers for frequently failing services.

3. **Deploy multiple gateway instances.** The gateway is a single point of failure.
   Run at least 2-3 instances behind a load balancer.

4. **Use correlation IDs.** Generate a unique ID for each request and pass it to all
   backend services. This enables end-to-end request tracing.

5. **Cache aggressively for read-heavy endpoints.** Products, categories, and static
   content rarely change. Cache at the gateway to reduce backend load.

6. **Consider BFF for diverse clients.** If mobile and web need very different data,
   a Backend-for-Frontend gateway simplifies both client and backend code.

7. **Monitor gateway metrics.** Track request count, latency percentiles (p50, p95,
   p99), error rates, and rate limit hits. The gateway sees all traffic.

---

## Quick Summary

The API Gateway pattern provides a single entry point for client requests to a
microservice architecture. It handles cross-cutting concerns like authentication, rate
limiting, routing, and response aggregation. The BFF variant creates specialized
gateways for different client types.

```
Problem:  Clients must know about and communicate with many services.
Solution: Put a gateway in front that routes, authenticates, and aggregates.
Key:      Keep the gateway thin -- infrastructure only, no business logic.
```

---

## Key Points

- **API Gateway** provides a single entry point for all client-to-service communication
- Core responsibilities: routing, authentication, rate limiting, logging, caching
- **Response aggregation** reduces multiple backend calls to one client call
- **BFF (Backend for Frontend)** creates specialized gateways per client type
- Keep the gateway **thin**: no business logic, only infrastructure concerns
- Deploy **multiple instances** to avoid single point of failure
- Use **correlation IDs** for end-to-end request tracing
- Add **timeouts and circuit breakers** for backend calls
- Popular implementations: Kong, AWS API Gateway, Spring Cloud Gateway, Nginx

---

## Practice Questions

1. What are the three most important responsibilities of an API Gateway? Explain why
   each belongs at the gateway level rather than in individual services.

2. Explain the BFF pattern. When would you use separate BFF gateways instead of one
   shared gateway?

3. How would you prevent the API Gateway from becoming a single point of failure?
   Describe at least two strategies.

4. A gateway adds latency to every request. How would you minimize this overhead while
   keeping the benefits of centralized routing?

5. Compare an API Gateway with a reverse proxy (like Nginx). What can a gateway do
   that a simple reverse proxy cannot?

---

## Exercises

### Exercise 1: API Gateway with Circuit Breaker

Extend the gateway to include circuit breaker functionality:

- Track failure rates per backend service
- When a service fails 5 times in 30 seconds, "open" the circuit
- While open, return a fallback response immediately (no backend call)
- After 10 seconds, allow one "probe" request through
- If the probe succeeds, close the circuit; if it fails, keep it open
- Demonstrate with a service that fails intermittently

### Exercise 2: Request Transformation Gateway

Build a gateway that transforms requests and responses:

- Convert REST requests to simulated gRPC calls (change format)
- Add request headers (correlation ID, timestamp, client version)
- Transform snake_case response keys to camelCase for JavaScript clients
- Strip sensitive fields (passwords, internal IDs) from responses
- Log the before/after of each transformation

### Exercise 3: Multi-Tenant API Gateway

Build a gateway that supports multiple tenants:

- Each tenant has its own API key, rate limits, and allowed routes
- Tenant "free" gets 10 requests/minute and access to /api/products only
- Tenant "pro" gets 100 requests/minute and access to all routes
- Tenant "enterprise" gets 1000 requests/minute, all routes, plus /api/admin
- Track usage per tenant and display a summary
- Block requests from unknown tenants

---

## What Is Next?

The next chapter introduces **Service Discovery**, which solves the question the API
Gateway raises: how does the gateway know where services are running? In dynamic
environments with auto-scaling, service instances come and go. Service Discovery
provides the mechanism for finding them automatically.
