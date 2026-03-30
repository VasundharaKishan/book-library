# Chapter 10: The Proxy Pattern

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand the Proxy pattern and how it controls access to an object
- Implement four types of proxies: virtual (lazy loading), protection (access control), caching, and logging
- Recognize how JPA/Hibernate lazy loading uses proxies under the hood
- Build proxies in Python using property descriptors and custom classes
- Apply the Proxy pattern to real-world scenarios like API rate limiting and database connection pooling
- Know when a proxy adds value and when it adds unnecessary complexity

---

## Why This Chapter Matters

Not every object should be accessed directly. Sometimes creating an object is expensive -- loading a 50MB image from disk or establishing a database connection takes time and memory, and you want to delay it until absolutely necessary. Sometimes access needs to be controlled -- only administrators should see certain data. Sometimes you want to track every access for auditing, or cache results to avoid redundant work.

The Proxy pattern handles all of these by placing a stand-in object in front of the real one. Think of a **bodyguard**. The bodyguard stands between the celebrity and the public. Every request to meet the celebrity goes through the bodyguard first. The bodyguard can:

- **Check credentials** before allowing access (protection proxy)
- **Schedule the meeting** for later when the celebrity is available (virtual proxy)
- **Remember previous answers** so the celebrity does not have to repeat them (caching proxy)
- **Log every interaction** for security records (logging proxy)

```
   Without Proxy                        With Proxy

   ┌──────────┐     ┌────────────┐     ┌──────────┐    ┌───────┐    ┌────────────┐
   │  Client   │────>│ Real Object│     │  Client   │───>│ Proxy │───>│ Real Object│
   └──────────┘     └────────────┘     └──────────┘    └───────┘    └────────────┘
                                                          │
   Direct access,                        Proxy controls:
   no control                            - When to create
                                         - Who can access
                                         - What to cache
                                         - What to log
```

The key difference from other patterns: the proxy has the **same interface** as the real object. The client does not know it is talking to a proxy.

---

## The Problem

You have a document management system. Loading documents from the database is expensive -- each document can be several megabytes. Your application loads lists of documents, but users usually only open one or two. Loading all documents eagerly wastes memory and time:

```java
// Without proxy: ALL documents loaded immediately
List<Document> docs = documentRepository.findAll(); // loads 1000 documents, 50MB each
// User only views one document...
// 50GB of memory wasted
```

You also need access control (only authorized users can view certain documents), caching (do not reload a document that was just viewed), and audit logging (track who accessed what).

Without the Proxy pattern, you would scatter all this logic across your codebase.

---

## The Solution: Proxy Pattern

```
┌───────────────────────────────────────────────────────────┐
│                    Proxy Pattern Structure                  │
├───────────────────────────────────────────────────────────┤
│                                                            │
│   ┌──────────────┐                                         │
│   │  <<interface>>│                                        │
│   │  Document     │                                        │
│   │  + getTitle() │                                        │
│   │  + getContent│                                         │
│   │  + getSize() │                                         │
│   └──────┬───────┘                                         │
│          │                                                 │
│    ┌─────┴─────────────────────────┐                       │
│    │                               │                       │
│  ┌─┴──────────────┐   ┌───────────┴─────────┐             │
│  │ RealDocument    │   │  DocumentProxy      │             │
│  │                 │   │                     │             │
│  │ - title         │   │ - realDocument      │──────┐      │
│  │ - content       │   │ - documentId        │      │      │
│  │ - size          │   │ - loaded: boolean   │      │      │
│  │                 │   │                     │      │      │
│  │ + getTitle()    │   │ + getTitle()        │      │      │
│  │ + getContent()  │   │ + getContent()      │      │      │
│  │ + getSize()     │   │ + getSize()         │      │      │
│  └─────────────────┘   └─────────────────────┘      │      │
│         ^                                            │      │
│         └────────────── creates lazily ──────────────┘      │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

---

## Types of Proxies

### 1. Virtual Proxy (Lazy Loading)

Delays creation of an expensive object until it is actually needed.

```
┌────────────────────────────────────────────────────┐
│  Virtual Proxy: Lazy Loading                        │
│                                                     │
│  Client calls getContent()                          │
│       │                                             │
│       ▼                                             │
│  ┌─────────────┐   Is real object    ┌───────────┐ │
│  │    Proxy     │── loaded? ── NO ──>│ Create it │ │
│  │             │                     │ from DB   │ │
│  │             │── loaded? ── YES    └─────┬─────┘ │
│  │             │       │                   │       │
│  └─────────────┘       └───────────────────┘       │
│                              │                      │
│                              ▼                      │
│                     Delegate to real object          │
└────────────────────────────────────────────────────┘
```

### 2. Protection Proxy (Access Control)

Checks whether the caller has permission to access the real object.

### 3. Caching Proxy

Stores results from the real object and returns cached values for repeated requests.

### 4. Logging Proxy

Records every access to the real object for auditing or debugging.

---

## Java Example: Complete Proxy Implementation

### Step 1: The Interface

```java
public interface DataService {
    String fetchData(String key);
    void updateData(String key, String value);
    List<String> listKeys();
}
```

### Step 2: The Real Implementation

```java
public class DatabaseService implements DataService {

    private final Map<String, String> database = new HashMap<>();

    public DatabaseService() {
        // Simulate expensive initialization
        System.out.println("  [DB] Initializing database connection (slow)...");
        try { Thread.sleep(500); } catch (InterruptedException e) { }

        // Seed some data
        database.put("user:1", "Alice");
        database.put("user:2", "Bob");
        database.put("user:3", "Charlie");
        System.out.println("  [DB] Database ready with " + database.size() + " records");
    }

    @Override
    public String fetchData(String key) {
        System.out.println("  [DB] Fetching: " + key);
        try { Thread.sleep(100); } catch (InterruptedException e) { } // simulate latency
        return database.get(key);
    }

    @Override
    public void updateData(String key, String value) {
        System.out.println("  [DB] Updating: " + key + " = " + value);
        database.put(key, value);
    }

    @Override
    public List<String> listKeys() {
        System.out.println("  [DB] Listing all keys");
        return new ArrayList<>(database.keySet());
    }
}
```

### Step 3: Virtual Proxy (Lazy Loading)

```java
public class LazyLoadingProxy implements DataService {

    private DataService realService; // null until first use
    private final Supplier<DataService> serviceFactory;

    public LazyLoadingProxy(Supplier<DataService> serviceFactory) {
        this.serviceFactory = serviceFactory;
        System.out.println("  [LazyProxy] Created (real service NOT initialized yet)");
    }

    private DataService getRealService() {
        if (realService == null) {
            System.out.println("  [LazyProxy] First access -- initializing real service now");
            realService = serviceFactory.get();
        }
        return realService;
    }

    @Override
    public String fetchData(String key) {
        return getRealService().fetchData(key);
    }

    @Override
    public void updateData(String key, String value) {
        getRealService().updateData(key, value);
    }

    @Override
    public List<String> listKeys() {
        return getRealService().listKeys();
    }
}
```

### Step 4: Protection Proxy (Access Control)

```java
public class ProtectionProxy implements DataService {

    private final DataService realService;
    private final String currentUserRole;

    // Define which roles can perform which operations
    private static final Set<String> READ_ROLES = Set.of("ADMIN", "USER", "VIEWER");
    private static final Set<String> WRITE_ROLES = Set.of("ADMIN", "USER");
    private static final Set<String> LIST_ROLES = Set.of("ADMIN");

    public ProtectionProxy(DataService realService, String currentUserRole) {
        this.realService = realService;
        this.currentUserRole = currentUserRole;
        System.out.println("  [AuthProxy] Created for role: " + currentUserRole);
    }

    @Override
    public String fetchData(String key) {
        checkAccess("fetchData", READ_ROLES);
        return realService.fetchData(key);
    }

    @Override
    public void updateData(String key, String value) {
        checkAccess("updateData", WRITE_ROLES);
        realService.updateData(key, value);
    }

    @Override
    public List<String> listKeys() {
        checkAccess("listKeys", LIST_ROLES);
        return realService.listKeys();
    }

    private void checkAccess(String operation, Set<String> allowedRoles) {
        if (!allowedRoles.contains(currentUserRole)) {
            System.out.println("  [AuthProxy] ACCESS DENIED: " + currentUserRole
                + " cannot perform " + operation);
            throw new SecurityException("Role '" + currentUserRole
                + "' is not authorized for operation: " + operation);
        }
        System.out.println("  [AuthProxy] Access granted for " + operation);
    }
}
```

### Step 5: Caching Proxy

```java
public class CachingProxy implements DataService {

    private final DataService realService;
    private final Map<String, String> cache = new ConcurrentHashMap<>();
    private final Map<String, Long> cacheTimestamps = new ConcurrentHashMap<>();
    private final long ttlMillis;

    public CachingProxy(DataService realService, long ttlMillis) {
        this.realService = realService;
        this.ttlMillis = ttlMillis;
        System.out.println("  [CacheProxy] Created with TTL: " + ttlMillis + "ms");
    }

    @Override
    public String fetchData(String key) {
        // Check cache
        if (cache.containsKey(key)) {
            long age = System.currentTimeMillis() - cacheTimestamps.get(key);
            if (age < ttlMillis) {
                System.out.println("  [CacheProxy] HIT for " + key
                    + " (age: " + age + "ms)");
                return cache.get(key);
            }
            System.out.println("  [CacheProxy] EXPIRED for " + key);
            cache.remove(key);
            cacheTimestamps.remove(key);
        } else {
            System.out.println("  [CacheProxy] MISS for " + key);
        }

        // Fetch from real service and cache
        String value = realService.fetchData(key);
        if (value != null) {
            cache.put(key, value);
            cacheTimestamps.put(key, System.currentTimeMillis());
        }
        return value;
    }

    @Override
    public void updateData(String key, String value) {
        realService.updateData(key, value);
        // Invalidate cache for this key
        cache.remove(key);
        cacheTimestamps.remove(key);
        System.out.println("  [CacheProxy] Invalidated cache for " + key);
    }

    @Override
    public List<String> listKeys() {
        return realService.listKeys(); // lists are not cached
    }
}
```

### Step 6: Logging Proxy

```java
public class LoggingProxy implements DataService {

    private final DataService realService;
    private final List<String> auditLog = new ArrayList<>();

    public LoggingProxy(DataService realService) {
        this.realService = realService;
    }

    @Override
    public String fetchData(String key) {
        String logEntry = timestamp() + " FETCH key=" + key;
        auditLog.add(logEntry);
        System.out.println("  [AuditProxy] " + logEntry);

        String result = realService.fetchData(key);

        String resultLog = timestamp() + " FETCH_RESULT key=" + key
            + " found=" + (result != null);
        auditLog.add(resultLog);
        return result;
    }

    @Override
    public void updateData(String key, String value) {
        String logEntry = timestamp() + " UPDATE key=" + key + " value=" + value;
        auditLog.add(logEntry);
        System.out.println("  [AuditProxy] " + logEntry);
        realService.updateData(key, value);
    }

    @Override
    public List<String> listKeys() {
        String logEntry = timestamp() + " LIST_KEYS";
        auditLog.add(logEntry);
        System.out.println("  [AuditProxy] " + logEntry);
        return realService.listKeys();
    }

    public List<String> getAuditLog() {
        return Collections.unmodifiableList(auditLog);
    }

    private String timestamp() {
        return java.time.LocalDateTime.now()
            .format(java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss.SSS"));
    }
}
```

### Step 7: Composing Proxies

Proxies can be stacked just like decorators, because they share the same interface:

```java
public class Main {
    public static void main(String[] args) {
        // Layer 1: Lazy loading (delays DB initialization)
        DataService service = new LazyLoadingProxy(DatabaseService::new);

        // Layer 2: Caching (avoids redundant DB queries)
        service = new CachingProxy(service, 5000); // 5 second TTL

        // Layer 3: Access control
        service = new ProtectionProxy(service, "ADMIN");

        // Layer 4: Audit logging
        service = new LoggingProxy(service);

        // The chain: Logging -> Auth -> Caching -> LazyLoading -> Database
        System.out.println("=== Service created (DB not initialized yet) ===\n");

        System.out.println("=== First fetch (triggers lazy init + cache miss) ===");
        String result1 = service.fetchData("user:1");
        System.out.println("Result: " + result1 + "\n");

        System.out.println("=== Second fetch (cache hit, no DB access) ===");
        String result2 = service.fetchData("user:1");
        System.out.println("Result: " + result2 + "\n");

        System.out.println("=== Update (invalidates cache) ===");
        service.updateData("user:1", "Alice Updated");
        System.out.println();

        System.out.println("=== Fetch after update (cache miss again) ===");
        String result3 = service.fetchData("user:1");
        System.out.println("Result: " + result3);
    }
}
```

**Output:**

```
=== Service created (DB not initialized yet) ===

=== First fetch (triggers lazy init + cache miss) ===
  [AuditProxy] 10:30:01.234 FETCH key=user:1
  [AuthProxy] Access granted for fetchData
  [CacheProxy] MISS for user:1
  [LazyProxy] First access -- initializing real service now
  [DB] Initializing database connection (slow)...
  [DB] Database ready with 3 records
  [DB] Fetching: user:1
Result: Alice

=== Second fetch (cache hit, no DB access) ===
  [AuditProxy] 10:30:01.740 FETCH key=user:1
  [AuthProxy] Access granted for fetchData
  [CacheProxy] HIT for user:1 (age: 506ms)
Result: Alice

=== Update (invalidates cache) ===
  [AuditProxy] 10:30:01.741 UPDATE key=user:1 value=Alice Updated
  [AuthProxy] Access granted for updateData
  [DB] Updating: user:1 = Alice Updated
  [CacheProxy] Invalidated cache for user:1

=== Fetch after update (cache miss again) ===
  [AuditProxy] 10:30:01.742 FETCH key=user:1
  [AuthProxy] Access granted for fetchData
  [CacheProxy] MISS for user:1
  [DB] Fetching: user:1
Result: Alice Updated
```

### JPA Lazy Loading Is a Proxy

Hibernate and JPA use the Proxy pattern extensively. When you define a `@ManyToOne(fetch = FetchType.LAZY)` relationship, JPA does not load the related entity immediately. Instead, it creates a proxy object:

```java
@Entity
public class Order {
    @Id
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    private Customer customer; // This is actually a PROXY, not a real Customer

    // When you call order.getCustomer().getName():
    // 1. getCustomer() returns the proxy object (no DB query)
    // 2. getName() triggers the proxy to load the real Customer from DB
    // 3. Subsequent calls to getName() return the cached value
}
```

```
┌──────────────────────────────────────────────────┐
│  JPA Lazy Loading                                 │
│                                                   │
│  order.getCustomer()                              │
│       │                                           │
│       ▼                                           │
│  Returns CustomerProxy (not real Customer)        │
│                                                   │
│  order.getCustomer().getName()                    │
│       │                                           │
│       ▼                                           │
│  CustomerProxy.getName()                          │
│       │                                           │
│       ├── Is real Customer loaded? ── NO          │
│       │       │                                   │
│       │       ▼                                   │
│       │   SELECT * FROM customer WHERE id = ?     │
│       │       │                                   │
│       │       ▼                                   │
│       │   Store real Customer in proxy            │
│       │       │                                   │
│       ├── Is real Customer loaded? ── YES         │
│       │       │                                   │
│       ▼       ▼                                   │
│  Return realCustomer.getName()                    │
└──────────────────────────────────────────────────┘
```

### Before vs After

**Before (without proxy) -- everything loaded eagerly:**

```java
// Loading a user with their profile picture, orders, and reviews
User user = userRepository.findById(42); // Loads EVERYTHING
// user.profilePicture = 5MB blob (loaded even if not displayed)
// user.orders = 500 order objects (loaded even if not listed)
// user.reviews = 200 review objects (loaded even if not shown)
// Total: potentially 100MB of data for displaying a username
```

**After (with proxy) -- loaded on demand:**

```java
User user = userRepository.findById(42); // Loads just user fields
// user.profilePicture -> Proxy (loaded when user views their profile)
// user.orders -> Proxy (loaded when user clicks "My Orders")
// user.reviews -> Proxy (loaded when user visits reviews page)
// Total: a few KB until actually needed
```

---

## Python Example: Proxy with Property Descriptors

### Virtual Proxy with Lazy Properties

```python
class LazyProperty:
    """A descriptor that acts as a virtual proxy for expensive attributes."""

    def __init__(self, factory):
        self._factory = factory
        self._attr_name = None

    def __set_name__(self, owner, name):
        self._attr_name = f"_lazy_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if not hasattr(obj, self._attr_name):
            print(f"  [LazyProperty] Loading '{self._attr_name}' for first time")
            value = self._factory(obj)
            setattr(obj, self._attr_name, value)
        else:
            print(f"  [LazyProperty] Returning cached '{self._attr_name}'")
        return getattr(obj, self._attr_name)


class UserProfile:
    """User with lazily loaded expensive attributes."""

    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name
        print(f"  [UserProfile] Created for {name} (no heavy data loaded)")

    @LazyProperty
    def order_history(self):
        """Expensive: loads all orders from database."""
        print(f"  [DB] Loading order history for {self.user_id}...")
        import time; time.sleep(0.3)
        return [
            {"order_id": "ORD-1", "total": 99.99},
            {"order_id": "ORD-2", "total": 149.50},
            {"order_id": "ORD-3", "total": 29.99},
        ]

    @LazyProperty
    def profile_image(self):
        """Expensive: loads large image from storage."""
        print(f"  [Storage] Loading profile image for {self.user_id}...")
        import time; time.sleep(0.5)
        return b"<fake image data -- imagine 5MB here>"


def main():
    print("=== Creating user (fast) ===")
    user = UserProfile("USR-42", "Alice")

    print("\n=== Accessing name (no proxy, instant) ===")
    print(f"Name: {user.name}")

    print("\n=== Accessing order_history (first time, slow) ===")
    orders = user.order_history
    print(f"Orders: {len(orders)} found")

    print("\n=== Accessing order_history (second time, cached) ===")
    orders = user.order_history
    print(f"Orders: {len(orders)} found")

    print("\n=== Profile image never accessed -- never loaded ===")
    print("Done!")


if __name__ == "__main__":
    main()
```

**Output:**

```
=== Creating user (fast) ===
  [UserProfile] Created for Alice (no heavy data loaded)

=== Accessing name (no proxy, instant) ===
Name: Alice

=== Accessing order_history (first time, slow) ===
  [LazyProperty] Loading '_lazy_order_history' for first time
  [DB] Loading order history for USR-42...
Orders: 3 found

=== Accessing order_history (second time, cached) ===
  [LazyProperty] Returning cached '_lazy_order_history'
Orders: 3 found

=== Profile image never accessed -- never loaded ===
Done!
```

### Protection and Rate-Limiting Proxy

```python
import time
from collections import defaultdict


class APIService:
    """The real service that handles API requests."""

    def get_resource(self, resource_id: str) -> dict:
        print(f"  [API] Fetching resource: {resource_id}")
        return {"id": resource_id, "data": f"Content for {resource_id}"}

    def create_resource(self, data: dict) -> dict:
        print(f"  [API] Creating resource: {data}")
        return {"id": "new-123", **data}

    def delete_resource(self, resource_id: str) -> bool:
        print(f"  [API] Deleting resource: {resource_id}")
        return True


class RateLimitingProxy:
    """Proxy that enforces rate limits on the API service."""

    def __init__(self, real_service: APIService, max_calls_per_minute: int):
        self._service = real_service
        self._max_calls = max_calls_per_minute
        self._call_timestamps: list[float] = []

    def _check_rate_limit(self):
        """Remove old timestamps and check if limit is exceeded."""
        now = time.time()
        cutoff = now - 60  # one minute window
        self._call_timestamps = [t for t in self._call_timestamps if t > cutoff]

        if len(self._call_timestamps) >= self._max_calls:
            wait_time = 60 - (now - self._call_timestamps[0])
            raise RuntimeError(
                f"Rate limit exceeded ({self._max_calls}/min). "
                f"Try again in {wait_time:.1f} seconds."
            )
        self._call_timestamps.append(now)
        remaining = self._max_calls - len(self._call_timestamps)
        print(f"  [RateLimit] Request allowed. {remaining} calls remaining this minute.")

    def get_resource(self, resource_id: str) -> dict:
        self._check_rate_limit()
        return self._service.get_resource(resource_id)

    def create_resource(self, data: dict) -> dict:
        self._check_rate_limit()
        return self._service.create_resource(data)

    def delete_resource(self, resource_id: str) -> bool:
        self._check_rate_limit()
        return self._service.delete_resource(resource_id)


class ProtectionProxy:
    """Proxy that checks permissions before allowing operations."""

    PERMISSIONS = {
        "ADMIN": {"get_resource", "create_resource", "delete_resource"},
        "USER": {"get_resource", "create_resource"},
        "VIEWER": {"get_resource"},
    }

    def __init__(self, real_service, user_role: str):
        self._service = real_service
        self._role = user_role

    def _check_permission(self, operation: str):
        allowed = self.PERMISSIONS.get(self._role, set())
        if operation not in allowed:
            raise PermissionError(
                f"Role '{self._role}' cannot perform '{operation}'. "
                f"Allowed: {allowed}"
            )
        print(f"  [Auth] {self._role} authorized for {operation}")

    def get_resource(self, resource_id: str) -> dict:
        self._check_permission("get_resource")
        return self._service.get_resource(resource_id)

    def create_resource(self, data: dict) -> dict:
        self._check_permission("create_resource")
        return self._service.create_resource(data)

    def delete_resource(self, resource_id: str) -> bool:
        self._check_permission("delete_resource")
        return self._service.delete_resource(resource_id)


def main():
    # Build the proxy chain: Auth -> RateLimit -> Real Service
    real_service = APIService()
    rate_limited = RateLimitingProxy(real_service, max_calls_per_minute=5)
    protected = ProtectionProxy(rate_limited, user_role="USER")

    # Allowed: USER can get and create
    print("=== GET (allowed for USER) ===")
    result = protected.get_resource("item-42")
    print(f"Result: {result}\n")

    print("=== CREATE (allowed for USER) ===")
    result = protected.create_resource({"name": "New Item"})
    print(f"Result: {result}\n")

    # Denied: USER cannot delete
    print("=== DELETE (denied for USER) ===")
    try:
        protected.delete_resource("item-42")
    except PermissionError as e:
        print(f"Error: {e}\n")

    # Rate limiting demo
    print("=== Hitting rate limit ===")
    for i in range(5):
        try:
            protected.get_resource(f"item-{i}")
        except RuntimeError as e:
            print(f"Blocked: {e}")


if __name__ == "__main__":
    main()
```

**Output:**

```
=== GET (allowed for USER) ===
  [Auth] USER authorized for get_resource
  [RateLimit] Request allowed. 4 calls remaining this minute.
  [API] Fetching resource: item-42
Result: {'id': 'item-42', 'data': 'Content for item-42'}

=== CREATE (allowed for USER) ===
  [Auth] USER authorized for create_resource
  [RateLimit] Request allowed. 3 calls remaining this minute.
  [API] Creating resource: {'name': 'New Item'}
Result: {'id': 'new-123', 'name': 'New Item'}

=== DELETE (denied for USER) ===
Error: Role 'USER' cannot perform 'delete_resource'. Allowed: {'get_resource', 'create_resource'}

=== Hitting rate limit ===
  [Auth] USER authorized for get_resource
  [RateLimit] Request allowed. 2 calls remaining this minute.
  [API] Fetching resource: item-0
  [Auth] USER authorized for get_resource
  [RateLimit] Request allowed. 1 calls remaining this minute.
  [API] Fetching resource: item-1
  [Auth] USER authorized for get_resource
  [RateLimit] Request allowed. 0 calls remaining this minute.
  [API] Fetching resource: item-2
  [Auth] USER authorized for get_resource
Blocked: Rate limit exceeded (5/min). Try again in 59.8 seconds.
```

---

## Real-World Backend Use Cases

### Use Case 1: Database Connection Pooling

Connection pools are essentially caching proxies. Instead of creating a new database connection for every query, the pool proxy returns an existing idle connection:

```
┌─────────────────────────────────────────────────────┐
│  Connection Pool Proxy                               │
│                                                      │
│  Client calls getConnection()                        │
│       │                                              │
│       ▼                                              │
│  ┌──────────────┐                                    │
│  │ Pool Proxy    │                                   │
│  │              │── Idle connection available? ──YES  │
│  │              │       │                     │      │
│  │              │       │              Return idle   │
│  │              │       │              connection    │
│  │              │       │                            │
│  │              │── NO ── Pool full? ── YES ── WAIT  │
│  │              │              │                      │
│  │              │              NO                     │
│  │              │              │                      │
│  │              │       Create new connection         │
│  └──────────────┘                                    │
└─────────────────────────────────────────────────────┘
```

### Use Case 2: API Rate Limiting

API gateways use protection/rate-limiting proxies to prevent abuse:

```java
public class RateLimitingProxy implements ApiEndpoint {
    private final ApiEndpoint realEndpoint;
    private final RateLimiter rateLimiter; // e.g., Guava RateLimiter

    @Override
    public Response handle(Request request) {
        String clientId = request.getHeader("X-API-Key");
        if (!rateLimiter.tryAcquire(clientId)) {
            return Response.status(429)
                .body("Rate limit exceeded. Try again later.")
                .build();
        }
        return realEndpoint.handle(request);
    }
}
```

### Use Case 3: Remote Proxy

A remote proxy represents an object that lives on a different server. The client calls methods on the proxy as if it were local, but the proxy serializes the call and sends it over the network:

```
┌──────────┐    ┌─────────────┐    Network    ┌─────────────┐    ┌──────────┐
│  Client   │──>│ Remote Proxy│──────────────>│   Stub      │──>│  Real    │
│          │    │ (local)     │    HTTP/gRPC   │  (remote)   │    │ Object  │
│          │    │             │               │             │    │ (remote)│
└──────────┘    └─────────────┘               └─────────────┘    └──────────┘
```

Java RMI, gRPC stubs, and REST client libraries all follow this pattern.

---

## When to Use / When NOT to Use

### Use the Proxy Pattern When:

- You need lazy initialization of heavyweight objects (virtual proxy)
- You need access control based on caller identity or role (protection proxy)
- You want to cache results of expensive operations (caching proxy)
- You need audit logging of object access (logging proxy)
- You want to enforce rate limits on API calls
- You need to manage database connection pools
- You want to add remote communication transparency

### Do NOT Use the Proxy Pattern When:

- Direct access is sufficient and the added indirection is not needed
- The proxy would add latency without providing value
- The object is cheap to create and does not need lazy loading
- Access control is better handled at a higher level (e.g., framework middleware)
- Caching is better handled by a dedicated cache layer (e.g., Redis)

---

## Common Mistakes

### Mistake 1: Proxy That Does Not Match the Real Object's Interface

```java
// BAD: Proxy adds methods that the real object does not have
public class BadProxy implements DataService {
    // DataService methods...

    public void clearCache() { } // Not part of DataService interface!
    public int getCacheSize() { } // Not part of DataService interface!
}

// GOOD: Proxy matches the interface exactly
// Put cache management in a separate interface or accessor
```

### Mistake 2: Forgetting to Delegate

```java
// BAD: Proxy forgets to delegate updateData, breaks functionality
public class IncompleteProxy implements DataService {
    @Override
    public String fetchData(String key) {
        return realService.fetchData(key); // correct
    }

    @Override
    public void updateData(String key, String value) {
        // Forgot to delegate! Updates silently disappear
        System.out.println("Update received");
    }
}
```

### Mistake 3: Thread-Unsafe Lazy Loading

```java
// BAD: Two threads can create the real object simultaneously
private DataService getRealService() {
    if (realService == null) { // Thread A checks, sees null
        // Thread B also checks, also sees null
        realService = new ExpensiveService(); // Both threads create it
    }
    return realService;
}

// GOOD: Thread-safe lazy initialization
private volatile DataService realService;

private synchronized DataService getRealService() {
    if (realService == null) {
        realService = new ExpensiveService();
    }
    return realService;
}
```

---

## Best Practices

1. **Match the interface exactly.** A proxy must implement the same interface as the real object. Clients should not be able to tell the difference.

2. **Use the right type of proxy.** Do not combine lazy loading, caching, and auth into one proxy class. Separate concerns into separate proxy layers.

3. **Be thread-safe.** If the proxy is shared across threads, ensure lazy loading, caching, and rate limiting are synchronized correctly.

4. **Document proxy behavior.** Make it clear to other developers that the object they are using might be a proxy. Especially for lazy-loading proxies where accessing a field can trigger a database query.

5. **Consider using framework proxies.** Spring AOP, Java dynamic proxies, and Python descriptors provide proxy infrastructure. You do not always need to write proxies from scratch.

6. **Cache invalidation is hard.** If you build a caching proxy, think carefully about when cached values become stale and how they are evicted.

---

## Quick Summary

The Proxy pattern places a stand-in object in front of the real object to control access. Like a bodyguard who screens visitors, a proxy can delay creation (virtual), check permissions (protection), store results (caching), or record access (logging). The proxy has the same interface as the real object, so clients use it transparently.

```
┌──────────┐       ┌──────────────────────────────┐       ┌──────────────┐
│  Client   │──────>│         Proxy                │──────>│  Real Object │
│          │       │                              │       │              │
│ Calls the│       │  - Lazy load                 │       │  Does the    │
│ interface│       │  - Check access              │       │  actual work │
│          │       │  - Cache results             │       │              │
│          │       │  - Log access                │       │              │
└──────────┘       └──────────────────────────────┘       └──────────────┘
                    Same interface as real object
```

---

## Key Points

- A proxy controls access to another object while maintaining the same interface
- Four main types: virtual (lazy), protection (auth), caching, and logging
- JPA/Hibernate lazy loading is the most common real-world proxy example in Java
- Proxies can be stacked like decorators since they share the same interface
- The client should not know (or care) whether it is talking to a proxy or the real object
- Thread safety is critical for lazy-loading and caching proxies
- Python descriptors and dynamic proxies reduce boilerplate

---

## Practice Questions

1. You have a `ReportGenerator` that takes 30 seconds to produce a report. Most users request the same report multiple times. Which type of proxy would you use, and how would you handle cache invalidation when the underlying data changes?

2. How does the Proxy pattern differ from the Decorator pattern? They both wrap objects and forward calls -- what is the fundamental difference in intent?

3. Your JPA entity has a `@OneToMany(fetch = FetchType.LAZY)` relationship. You access the collection outside a transaction and get a `LazyInitializationException`. What happened, and how does this relate to the Proxy pattern?

4. A rate-limiting proxy keeps track of requests per minute. How would you handle this in a distributed system where multiple server instances share the rate limit?

5. You need to log every database query in production for compliance. Would you use a logging proxy or an aspect-oriented approach? What are the trade-offs?

---

## Exercises

### Exercise 1: Build a Connection Pool Proxy

Create a `ConnectionPoolProxy` that manages a fixed pool of database connections:
- Initialize with a maximum pool size
- `getConnection()` returns an available connection or blocks until one is free
- `releaseConnection()` returns a connection to the pool
- Track how many active and idle connections exist

### Exercise 2: Python Smart Reference Proxy

Build a proxy class that wraps any object and:
- Counts how many times each method is called
- Tracks the last access time for each method
- Provides a `get_usage_stats()` method that returns all collected statistics
- Does not require the wrapped object's class to be modified

### Exercise 3: Tiered Caching Proxy

Create a two-tier caching proxy:
- Level 1 (L1): In-memory cache with a 10-second TTL and max 100 entries
- Level 2 (L2): Simulated Redis cache with a 60-second TTL
- On cache miss: check L1, then L2, then the real service
- On cache hit in L2: populate L1 for faster subsequent access
- Implement cache eviction using LRU (Least Recently Used) for L1

---

## What Is Next?

You now know how to control access to objects using proxies. But what happens when you have two independent dimensions of variation that multiply together? What if you have notifications (Email, SMS, Push) and urgency levels (Normal, Urgent) and you do not want to create a class for every combination?

In the next chapter, you will learn the **Bridge pattern**, which separates an abstraction from its implementation so they can vary independently. Where the Proxy controls access, the Bridge controls complexity.
