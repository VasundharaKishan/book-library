# Chapter 8: The Decorator Pattern

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand the Decorator pattern and how it adds behavior dynamically
- Explain why composition is often better than inheritance for extending behavior
- Build decorator chains in Java using the InputStream pattern
- Use Python function decorators (`@retry`, `@cache`, `@log`) for cross-cutting concerns
- Recognize the Decorator pattern in real-world backend systems: logging, caching, auth middleware, response compression
- Compare the Decorator pattern with inheritance and know when each is appropriate
- Avoid common mistakes like overly deep decorator chains and ordering bugs

---

## Why This Chapter Matters

Every backend system needs cross-cutting concerns. You need logging. You need caching. You need authentication checks. You need rate limiting. You need response compression. You need retry logic.

The naive approach is to shove all of this into every class. Your `UserService` does user logic *and* logging *and* caching *and* auth checks. Your `OrderService` does the same. Code is duplicated. Classes become bloated. Adding a new concern means modifying dozens of files.

The Decorator pattern solves this by letting you wrap an object with additional behavior, one layer at a time, without modifying the original class. Think of it like **Russian nesting dolls** (matryoshka dolls):

```
┌─────────────────────────────────────────────┐
│  Logging Decorator                          │
│  ┌───────────────────────────────────────┐  │
│  │  Caching Decorator                    │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  Auth Decorator                 │  │  │
│  │  │  ┌───────────────────────────┐  │  │  │
│  │  │  │                           │  │  │  │
│  │  │  │   Original Service        │  │  │  │
│  │  │  │   (core business logic)   │  │  │  │
│  │  │  │                           │  │  │  │
│  │  │  └───────────────────────────┘  │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

Each layer adds one behavior. The original service is untouched. You can mix and match layers as needed.

---

## The Problem

You have a data service interface:

```java
public interface DataService {
    String getData(String key);
    void saveData(String key, String value);
}
```

And a basic implementation:

```java
public class DatabaseService implements DataService {
    @Override
    public String getData(String key) {
        // Simulate database query
        System.out.println("  [DB] Querying database for key: " + key);
        return "value_for_" + key;
    }

    @Override
    public void saveData(String key, String value) {
        System.out.println("  [DB] Saving to database: " + key + " = " + value);
    }
}
```

Now you need to add logging, caching, and authentication. The inheritance approach looks like this:

```
                    DataService
                        │
                DatabaseService
                        │
          LoggingDatabaseService
                        │
     CachingLoggingDatabaseService
                        │
AuthCachingLoggingDatabaseService
```

This is a nightmare. What if you want caching without logging? What if you want auth without caching? You end up with a class for every combination:

```
DatabaseService
LoggingDatabaseService
CachingDatabaseService
AuthDatabaseService
LoggingCachingDatabaseService
LoggingAuthDatabaseService
CachingAuthDatabaseService
LoggingCachingAuthDatabaseService
```

That is 8 classes for 3 features. With 4 features, you need 16 classes. With 5 features, 32 classes. This is called the **class explosion problem**.

---

## The Solution: Decorator Pattern

Instead of inheritance, use composition. Each decorator wraps the original object and adds one behavior.

```
┌───────────────────────────────────────────────────────────┐
│                  Decorator Pattern Structure               │
├───────────────────────────────────────────────────────────┤
│                                                           │
│   ┌──────────────┐                                        │
│   │  <<interface>>│                                       │
│   │  DataService  │                                       │
│   └──────┬───────┘                                        │
│          │                                                │
│    ┌─────┴──────────────────────────┐                     │
│    │                                │                     │
│  ┌─┴────────────┐   ┌──────────────┴──────────┐          │
│  │DatabaseService│   │  <<abstract>>           │          │
│  │(concrete)     │   │  DataServiceDecorator   │          │
│  └───────────────┘   │  - wrapped: DataService │          │
│                      └──────────┬──────────────┘          │
│                                 │                         │
│              ┌──────────────────┼──────────────┐          │
│              │                  │              │          │
│     ┌────────┴───┐   ┌─────────┴──┐  ┌────────┴───┐     │
│     │  Logging   │   │  Caching   │  │   Auth     │     │
│     │  Decorator │   │  Decorator │  │  Decorator │     │
│     └────────────┘   └────────────┘  └────────────┘     │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

Key insight: every decorator *is a* `DataService` and *has a* `DataService`. This lets you stack them.

---

## Java Example: Building a Decorator Chain

### Step 1: The Base Decorator

```java
public abstract class DataServiceDecorator implements DataService {

    protected final DataService wrapped;

    public DataServiceDecorator(DataService wrapped) {
        this.wrapped = wrapped;
    }

    @Override
    public String getData(String key) {
        return wrapped.getData(key);
    }

    @Override
    public void saveData(String key, String value) {
        wrapped.saveData(key, value);
    }
}
```

By default, the decorator simply delegates to the wrapped object. Subclasses override methods to add behavior.

### Step 2: Logging Decorator

```java
public class LoggingDecorator extends DataServiceDecorator {

    private static final Logger logger = Logger.getLogger(LoggingDecorator.class.getName());

    public LoggingDecorator(DataService wrapped) {
        super(wrapped);
    }

    @Override
    public String getData(String key) {
        long start = System.currentTimeMillis();
        logger.info("getData() called with key: " + key);

        String result = super.getData(key); // delegate to wrapped service

        long elapsed = System.currentTimeMillis() - start;
        logger.info("getData() returned in " + elapsed + "ms. Result length: "
            + (result != null ? result.length() : 0));
        return result;
    }

    @Override
    public void saveData(String key, String value) {
        logger.info("saveData() called with key: " + key
            + ", value length: " + value.length());

        super.saveData(key, value); // delegate to wrapped service

        logger.info("saveData() completed for key: " + key);
    }
}
```

### Step 3: Caching Decorator

```java
public class CachingDecorator extends DataServiceDecorator {

    private final Map<String, String> cache = new ConcurrentHashMap<>();

    public CachingDecorator(DataService wrapped) {
        super(wrapped);
    }

    @Override
    public String getData(String key) {
        // Check cache first
        String cached = cache.get(key);
        if (cached != null) {
            System.out.println("  [Cache] HIT for key: " + key);
            return cached;
        }

        System.out.println("  [Cache] MISS for key: " + key);
        String result = super.getData(key); // delegate to wrapped service

        // Store in cache
        if (result != null) {
            cache.put(key, result);
        }
        return result;
    }

    @Override
    public void saveData(String key, String value) {
        super.saveData(key, value); // delegate to wrapped service
        cache.put(key, value); // update cache
        System.out.println("  [Cache] Updated cache for key: " + key);
    }
}
```

### Step 4: Authentication Decorator

```java
public class AuthDecorator extends DataServiceDecorator {

    private final String requiredRole;
    private String currentUserRole;

    public AuthDecorator(DataService wrapped, String requiredRole) {
        super(wrapped);
        this.requiredRole = requiredRole;
    }

    public void setCurrentUserRole(String role) {
        this.currentUserRole = role;
    }

    @Override
    public String getData(String key) {
        checkAccess("getData");
        return super.getData(key);
    }

    @Override
    public void saveData(String key, String value) {
        checkAccess("saveData");
        super.saveData(key, value);
    }

    private void checkAccess(String operation) {
        if (currentUserRole == null || !currentUserRole.equals(requiredRole)) {
            throw new SecurityException(
                "Access denied for operation '" + operation
                + "'. Required role: " + requiredRole
                + ", current role: " + currentUserRole
            );
        }
        System.out.println("  [Auth] Access granted for role: " + currentUserRole);
    }
}
```

### Step 5: Composing Decorators

```java
public class Main {
    public static void main(String[] args) {
        // Start with the base service
        DataService service = new DatabaseService();

        // Wrap with caching
        service = new CachingDecorator(service);

        // Wrap with logging
        service = new LoggingDecorator(service);

        // Now: Logging -> Caching -> Database
        // When getData() is called:
        //   1. LoggingDecorator logs the call
        //   2. CachingDecorator checks cache
        //   3. If cache miss, DatabaseService queries DB

        System.out.println("=== First call (cache miss) ===");
        String result1 = service.getData("user:42");
        System.out.println("Result: " + result1);

        System.out.println("\n=== Second call (cache hit) ===");
        String result2 = service.getData("user:42");
        System.out.println("Result: " + result2);

        System.out.println("\n=== Save data ===");
        service.saveData("user:99", "Alice");
    }
}
```

**Output:**

```
=== First call (cache miss) ===
INFO: getData() called with key: user:42
  [Cache] MISS for key: user:42
  [DB] Querying database for key: user:42
INFO: getData() returned in 5ms. Result length: 14
Result: value_for_user:42

=== Second call (cache hit) ===
INFO: getData() called with key: user:42
  [Cache] HIT for key: user:42
INFO: getData() returned in 0ms. Result length: 14
Result: value_for_user:42

=== Save data ===
INFO: saveData() called with key: user:99, value length: 5
  [DB] Saving to database: user:99 = Alice
  [Cache] Updated cache for key: user:99
INFO: saveData() completed for key: user:99
```

Notice the second call never hits the database. The caching decorator intercepted it.

### The Java InputStream Chain: A Classic Decorator

Java's I/O library is one of the most famous examples of the Decorator pattern in the real world:

```java
// Each wrapper adds one capability
InputStream raw       = new FileInputStream("data.txt");       // reads bytes
InputStream buffered  = new BufferedInputStream(raw);           // adds buffering
InputStream data      = new DataInputStream(buffered);          // adds typed reads

// The chain: DataInputStream -> BufferedInputStream -> FileInputStream -> File
// Each layer IS an InputStream and HAS an InputStream
```

```
┌──────────────────────────────────────────────┐
│  DataInputStream                              │
│  (read Java primitives: readInt, readDouble)  │
│  ┌────────────────────────────────────────┐   │
│  │  BufferedInputStream                   │   │
│  │  (read chunks into memory buffer)      │   │
│  │  ┌──────────────────────────────────┐  │   │
│  │  │  FileInputStream                 │  │   │
│  │  │  (read raw bytes from disk)      │  │   │
│  │  └──────────────────────────────────┘  │   │
│  └────────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

### Before vs After

**Before (without decorators) -- everything in one class:**

```java
public class DoEverythingService implements DataService {
    private Map<String, String> cache = new HashMap<>();
    private Logger logger = Logger.getLogger("service");
    private String requiredRole = "ADMIN";
    private String currentRole;

    @Override
    public String getData(String key) {
        // Auth check
        if (!requiredRole.equals(currentRole)) throw new SecurityException("Denied");

        // Logging
        logger.info("getData called: " + key);
        long start = System.currentTimeMillis();

        // Caching
        if (cache.containsKey(key)) {
            logger.info("Cache hit");
            return cache.get(key);
        }

        // Actual work
        String result = queryDatabase(key);

        // More caching
        cache.put(key, result);

        // More logging
        logger.info("getData completed in " + (System.currentTimeMillis() - start) + "ms");
        return result;
    }
    // Imagine saveData() with the same mess...
}
```

**After (with decorators) -- each concern is separate:**

```java
DataService service = new DatabaseService();              // core logic
service = new CachingDecorator(service);                  // + caching
service = new LoggingDecorator(service);                  // + logging
service = new AuthDecorator(service, "ADMIN");            // + auth
// Clean. Each class has one responsibility.
```

---

## Python Example: Function Decorators

Python has built-in syntax for the Decorator pattern using the `@` symbol. This is so fundamental to Python that it has its own language feature.

### The @retry Decorator

```python
import time
import functools
import random


def retry(max_attempts=3, delay_seconds=1.0, exceptions=(Exception,)):
    """Retry a function call if it raises specified exceptions."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    print(f"  [Retry] Attempt {attempt}/{max_attempts} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay_seconds)
            raise last_exception

        return wrapper

    return decorator


# Usage
@retry(max_attempts=3, delay_seconds=0.5, exceptions=(ConnectionError,))
def fetch_user_data(user_id: int) -> dict:
    """Simulates an unreliable API call."""
    if random.random() < 0.6:  # 60% chance of failure
        raise ConnectionError(f"Failed to connect to user service")
    return {"user_id": user_id, "name": "Alice", "email": "alice@example.com"}


# When you call fetch_user_data(42), the retry decorator
# automatically retries up to 3 times if ConnectionError is raised
result = fetch_user_data(42)
print(f"Got user: {result}")
```

**Output (example run):**

```
  [Retry] Attempt 1/3 failed: Failed to connect to user service
  [Retry] Attempt 2/3 failed: Failed to connect to user service
Got user: {'user_id': 42, 'name': 'Alice', 'email': 'alice@example.com'}
```

### The @cache Decorator

```python
import functools
import time


def cache(ttl_seconds=60):
    """Cache function results with a time-to-live."""

    def decorator(func):
        _cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a hashable cache key from the arguments
            cache_key = (args, tuple(sorted(kwargs.items())))

            # Check if cached and not expired
            if cache_key in _cache:
                result, cached_at = _cache[cache_key]
                age = time.time() - cached_at
                if age < ttl_seconds:
                    print(f"  [Cache] HIT (age: {age:.1f}s)")
                    return result
                else:
                    print(f"  [Cache] EXPIRED (age: {age:.1f}s)")

            print(f"  [Cache] MISS -- calling {func.__name__}")
            result = func(*args, **kwargs)
            _cache[cache_key] = (result, time.time())
            return result

        # Expose cache management methods
        wrapper.clear_cache = lambda: _cache.clear()
        wrapper.cache_size = lambda: len(_cache)
        return wrapper

    return decorator


@cache(ttl_seconds=30)
def get_product_catalog(category: str) -> list:
    """Expensive database query to fetch products."""
    print(f"  [DB] Querying products for category: {category}")
    time.sleep(0.5)  # simulate slow query
    return [
        {"id": 1, "name": "Widget A", "category": category},
        {"id": 2, "name": "Widget B", "category": category},
    ]


# First call: cache miss
products = get_product_catalog("electronics")
print(f"Products: {len(products)} items\n")

# Second call: cache hit
products = get_product_catalog("electronics")
print(f"Products: {len(products)} items")
```

**Output:**

```
  [Cache] MISS -- calling get_product_catalog
  [DB] Querying products for category: electronics
Products: 2 items

  [Cache] HIT (age: 0.5s)
Products: 2 items
```

### The @log Decorator

```python
import functools
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def log(func):
    """Log function entry, exit, arguments, and duration."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        logger.info(f"Calling {func_name}({signature})")
        start = time.time()

        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"{func_name} returned {result!r} in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"{func_name} raised {type(e).__name__}: {e} after {elapsed:.3f}s")
            raise

    return wrapper


@log
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price."""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError(f"Invalid discount: {discount_percent}")
    return price * (1 - discount_percent / 100)


# Normal call
result = calculate_discount(100.0, 15.0)
print(f"Discounted price: ${result:.2f}\n")

# Call that raises an exception
try:
    calculate_discount(100.0, -5.0)
except ValueError:
    print("Caught the error (but it was logged automatically)")
```

**Output:**

```
2024-01-15 10:30:00 - Calling calculate_discount(100.0, 15.0)
2024-01-15 10:30:00 - calculate_discount returned 85.0 in 0.000s
Discounted price: $85.00

2024-01-15 10:30:00 - Calling calculate_discount(100.0, -5.0)
2024-01-15 10:30:00 - calculate_discount raised ValueError: Invalid discount: -5.0 after 0.000s
Caught the error (but it was logged automatically)
```

### Stacking Python Decorators

The real power shows when you stack decorators. Decorators are applied bottom-up but execute top-down:

```python
@log                    # 3rd applied, 1st to execute
@retry(max_attempts=3)  # 2nd applied, 2nd to execute
@cache(ttl_seconds=300) # 1st applied, 3rd to execute
def fetch_exchange_rate(base: str, target: str) -> float:
    """Fetch currency exchange rate from external API."""
    print(f"  [API] Fetching {base}/{target} rate...")
    if random.random() < 0.3:
        raise ConnectionError("Rate service unavailable")
    return 1.08  # simulated EUR/USD rate
```

Execution flow:

```
    Call: fetch_exchange_rate("EUR", "USD")
         │
         ▼
    ┌─────────────┐
    │  @log        │  1. Log the call
    │             │
    │  ┌─────────┐│
    │  │ @retry   ││  2. Retry on failure
    │  │         ││
    │  │ ┌──────┐││
    │  │ │@cache │││  3. Check cache first
    │  │ │      │││
    │  │ │ func │││  4. Call actual function
    │  │ │      │││
    │  │ └──────┘││
    │  └─────────┘│
    └─────────────┘
```

### Python Class-Based Decorators

For more complex scenarios, you can use class-based decorators that mirror the Java approach:

```python
from abc import ABC, abstractmethod


class DataService(ABC):
    """Target interface."""

    @abstractmethod
    def get_data(self, key: str) -> str:
        pass

    @abstractmethod
    def save_data(self, key: str, value: str) -> None:
        pass


class DatabaseService(DataService):
    """Concrete implementation."""

    def get_data(self, key: str) -> str:
        print(f"  [DB] Querying: {key}")
        return f"value_for_{key}"

    def save_data(self, key: str, value: str) -> None:
        print(f"  [DB] Saving: {key} = {value}")


class DataServiceDecorator(DataService):
    """Base decorator -- delegates everything to the wrapped service."""

    def __init__(self, wrapped: DataService):
        self._wrapped = wrapped

    def get_data(self, key: str) -> str:
        return self._wrapped.get_data(key)

    def save_data(self, key: str, value: str) -> None:
        self._wrapped.save_data(key, value)


class LoggingDecorator(DataServiceDecorator):
    def get_data(self, key: str) -> str:
        print(f"  [Log] get_data({key})")
        result = super().get_data(key)
        print(f"  [Log] get_data returned: {result}")
        return result

    def save_data(self, key: str, value: str) -> None:
        print(f"  [Log] save_data({key}, {value})")
        super().save_data(key, value)
        print(f"  [Log] save_data completed")


class CachingDecorator(DataServiceDecorator):
    def __init__(self, wrapped: DataService):
        super().__init__(wrapped)
        self._cache = {}

    def get_data(self, key: str) -> str:
        if key in self._cache:
            print(f"  [Cache] HIT: {key}")
            return self._cache[key]
        print(f"  [Cache] MISS: {key}")
        result = super().get_data(key)
        self._cache[key] = result
        return result


# Compose decorators
service = DatabaseService()
service = CachingDecorator(service)
service = LoggingDecorator(service)

service.get_data("user:1")
print()
service.get_data("user:1")  # cache hit
```

**Output:**

```
  [Log] get_data(user:1)
  [Cache] MISS: user:1
  [DB] Querying: user:1
  [Log] get_data returned: value_for_user:1

  [Log] get_data(user:1)
  [Cache] HIT: user:1
  [Log] get_data returned: value_for_user:1
```

---

## Real-World Backend Use Cases

### Use Case 1: HTTP Middleware Stack

Web frameworks like Express, Django, and Spring use the Decorator pattern for middleware:

```
Request ──> Auth ──> RateLimit ──> Logging ──> Compression ──> Handler
                                                                  │
Response <── Auth <── RateLimit <── Logging <── Compression <──────┘
```

Each middleware decorates the next one. It can modify the request before passing it along and modify the response on the way back.

### Use Case 2: Response Compression

```java
public class CompressionDecorator extends DataServiceDecorator {

    public CompressionDecorator(DataService wrapped) {
        super(wrapped);
    }

    @Override
    public String getData(String key) {
        String rawData = super.getData(key);
        // In a real system, this would use GZIP or Brotli
        System.out.println("  [Compress] Compressing " + rawData.length() + " bytes");
        return compress(rawData);
    }

    private String compress(String data) {
        // Simulated compression
        return "[compressed:" + data + "]";
    }
}
```

### Use Case 3: Metrics Collection

```python
import time


class MetricsDecorator(DataServiceDecorator):
    """Collects timing metrics for monitoring dashboards."""

    def __init__(self, wrapped, metrics_client):
        super().__init__(wrapped)
        self._metrics = metrics_client

    def get_data(self, key):
        start = time.time()
        try:
            result = super().get_data(key)
            self._metrics.record("get_data.success", time.time() - start)
            return result
        except Exception as e:
            self._metrics.record("get_data.error", time.time() - start)
            raise
```

---

## Decorator vs Inheritance

| Aspect | Decorator | Inheritance |
|---|---|---|
| Adding behavior | At runtime, flexible | At compile time, fixed |
| Combinations | Mix and match freely | One class per combination |
| Number of classes | One per behavior | Exponential (class explosion) |
| Complexity | Can be hard to debug deep chains | Simpler for 1-2 behaviors |
| Open/Closed Principle | Follows it perfectly | Often violates it |
| When to use | Cross-cutting concerns, optional behaviors | Is-a relationships, core type hierarchy |

**Rule of thumb:** If you are adding behavior that is **orthogonal** to the core functionality (logging, caching, auth, metrics), use decorators. If you are defining a **type hierarchy** (Dog is an Animal), use inheritance.

---

## When to Use / When NOT to Use

### Use the Decorator Pattern When:

- You need to add responsibilities to objects dynamically
- You want to add cross-cutting concerns (logging, caching, auth, metrics)
- Extension by subclassing is impractical due to class explosion
- You want to combine behaviors flexibly at runtime
- You need to follow the Open/Closed Principle (open for extension, closed for modification)

### Do NOT Use the Decorator Pattern When:

- You only need one fixed combination of behaviors -- just write that class
- The decorator chain would be deeply nested (more than 4-5 levels), making debugging hard
- The interface has many methods and most decorators only care about one -- consider aspect-oriented programming instead
- You need to access the specific type of the wrapped object -- decorators hide it

---

## Common Mistakes

### Mistake 1: Forgetting functools.wraps in Python

```python
# BAD: Loses the original function's name and docstring
def log(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log
def my_function():
    """Does something important."""
    pass

print(my_function.__name__)  # prints "wrapper" -- wrong!

# GOOD: Preserves metadata
def log(func):
    @functools.wraps(func)  # preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### Mistake 2: Order-Dependent Bugs

```java
// Order matters! These two produce different behavior:

// Option A: Cache first, then log
DataService serviceA = new LoggingDecorator(new CachingDecorator(new DatabaseService()));
// Logs every call, including cache hits

// Option B: Log first, then cache
DataService serviceB = new CachingDecorator(new LoggingDecorator(new DatabaseService()));
// Only logs cache misses (when the actual service is called)

// Think carefully about which behavior you want!
```

### Mistake 3: Breaking the Interface Contract

```java
// BAD: Decorator changes the return type semantics
public class BadCachingDecorator extends DataServiceDecorator {
    @Override
    public String getData(String key) {
        String cached = cache.get(key);
        if (cached != null) return cached;
        return null; // BUG: should delegate to wrapped, not return null
    }
}
```

Always delegate to the wrapped object when the decorator cannot handle the call itself.

---

## Best Practices

1. **Keep decorators focused.** Each decorator should add exactly one behavior. "LoggingAndCachingDecorator" is a sign that you should split it into two.

2. **Order decorators intentionally.** Think about what happens when each layer runs. Document the expected order if it matters.

3. **Always use `functools.wraps`** in Python function decorators to preserve metadata.

4. **Make decorators transparent.** A client should not be able to tell whether it is talking to a decorated or undecorated object.

5. **Test decorators independently.** Test each decorator with a mock wrapped object. Then test the composition.

6. **Use a builder or factory** to construct complex decorator chains, rather than nesting constructors manually.

---

## Quick Summary

The Decorator pattern wraps an object with additional behavior without modifying its class. Like Russian nesting dolls, you can layer multiple decorators to combine behaviors. Each decorator implements the same interface as the wrapped object, so clients cannot tell the difference.

```
Client ──> Decorator A ──> Decorator B ──> Decorator C ──> Real Object
             (logging)       (caching)       (auth)       (core logic)
```

In Java, this appears as wrapper classes implementing a common interface. In Python, the `@decorator` syntax provides a concise way to wrap functions. Both approaches solve the same problem: adding behavior without modifying existing code.

---

## Key Points

- The Decorator pattern adds behavior dynamically through composition, not inheritance
- It avoids the class explosion problem that arises from combining features via subclassing
- Each decorator implements the same interface as the object it wraps
- Decorators can be stacked in any order -- but order matters for behavior
- Java's InputStream hierarchy is a classic real-world example
- Python's `@decorator` syntax is syntactic sugar for the Decorator pattern
- Always use `functools.wraps` in Python decorators
- Keep decorators focused on one concern each

---

## Practice Questions

1. You have a `MessageSender` interface with `send(to, message)`. You need logging, retry logic, and rate limiting. How many classes do you need with the Decorator pattern vs with inheritance for all combinations?

2. In the Java InputStream chain `new DataInputStream(new BufferedInputStream(new FileInputStream("f.txt")))`, which class is the "innermost doll" and which is the "outermost doll"? What happens when you call `readInt()` on the outer object?

3. Why does the order of decorators matter? Give an example where swapping two decorators produces different behavior.

4. How does the Decorator pattern relate to the Single Responsibility Principle?

5. A colleague writes a Python decorator that modifies a function's return value. When they try to access the function's docstring, they get `None`. What did they forget?

---

## Exercises

### Exercise 1: Build a Retry Decorator in Java

Create a `RetryDecorator` that wraps any `DataService` and retries failed calls up to N times with exponential backoff. The decorator should:
- Catch specified exception types
- Wait `delay * 2^attempt` between retries
- Log each retry attempt
- Re-throw the exception after all attempts are exhausted

### Exercise 2: Python Rate-Limiting Decorator

Write a `@rate_limit(calls_per_second=5)` decorator that:
- Tracks how many times the function has been called in the current second
- Raises a `RateLimitExceeded` exception if the limit is exceeded
- Resets the counter each second
- Works with any function signature

### Exercise 3: Compose a Full Middleware Stack

Using either Java or Python, build a complete HTTP middleware stack with these decorators:
1. `LoggingMiddleware` -- logs request/response
2. `AuthMiddleware` -- checks for an API key header
3. `RateLimitMiddleware` -- limits to 100 requests per minute
4. `CompressionMiddleware` -- compresses responses larger than 1KB

Wire them together and demonstrate a request flowing through all four layers.

---

## What Is Next?

You now know how to add behavior to objects dynamically. But what if the problem is not adding behavior -- it is that the underlying system is too complex? What if a client needs to coordinate five different subsystems just to complete one operation?

In the next chapter, you will learn the **Facade pattern**, which provides a simple interface to a complex subsystem. Where the Decorator adds layers, the Facade hides them.
