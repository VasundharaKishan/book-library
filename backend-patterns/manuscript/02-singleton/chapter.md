# Chapter 2: The Singleton Pattern

## What You Will Learn

- What the Singleton pattern is and what problem it solves
- How to implement Singleton in Java (private constructor, double-checked locking, enum)
- How to implement Singleton in Python (`__new__`, metaclass, module-level)
- How Spring handles singletons with `@Scope("singleton")`
- Why singletons can hurt testability and hide state
- Thread-safety concerns and how to address them
- When to use Singleton and when to avoid it

## Why This Chapter Matters

The Singleton is the most well-known design pattern and often the first one developers learn. It is also the most controversial. Used correctly, it solves real problems: you do not want 50 database connection pools or multiple logger instances competing for the same file. Used incorrectly, it creates hidden dependencies, makes testing painful, and introduces subtle concurrency bugs.

Every backend developer will encounter singletons. Your framework almost certainly uses them. Understanding how they work, when they help, and when they hurt is essential knowledge.

---

## The Problem

Imagine you are building a backend service that connects to a database. Every time a request arrives, your code creates a new database connection.

**Before (No Singleton) - The Pain:**

```java
// Java - Every request creates a new connection
public class OrderService {

    public Order getOrder(int id) {
        // NEW connection every single time
        Connection conn = DriverManager.getConnection(
            "jdbc:postgresql://localhost:5432/shop",
            "admin",
            "password"
        );
        // ... use connection
        conn.close();
        return order;
    }
}
```

```python
# Python - Every request creates a new connection
class OrderService:

    def get_order(self, order_id: int):
        # NEW connection every single time
        conn = psycopg2.connect(
            host="localhost",
            database="shop",
            user="admin",
            password="password"
        )
        # ... use connection
        conn.close()
        return order
```

What happens under load?

```
Request 1   --> new Connection() --> DB  (connection #1)
Request 2   --> new Connection() --> DB  (connection #2)
Request 3   --> new Connection() --> DB  (connection #3)
...
Request 500 --> new Connection() --> DB  (connection #500)
...
Request 1000 --> CRASH! Database refuses new connections.

+----------------------------------------------------------+
| PostgreSQL default max_connections = 100                  |
| MySQL default max_connections = 151                       |
|                                                          |
| You ran out of connections because every request          |
| created a new one instead of sharing a pool.             |
+----------------------------------------------------------+
```

The same problem appears with:
- Configuration objects (reading the same config file 1,000 times)
- Logger instances (multiple loggers fighting over the same log file)
- Cache managers (multiple caches storing duplicate data)
- Thread pools (creating pools of pools)

---

## The Solution: Singleton Pattern

The Singleton pattern ensures a class has only one instance and provides a global point of access to it.

```
+---------------------------------------------------------------+
|                    SINGLETON PATTERN                           |
+---------------------------------------------------------------+
|                                                               |
|  INTENT: Ensure a class has only one instance and provide     |
|          a global point of access to it.                      |
|                                                               |
|  CATEGORY: Creational                                         |
|                                                               |
+---------------------------------------------------------------+

  +-----------------------------+
  |        Singleton            |
  +-----------------------------+
  | - instance: Singleton       |  <-- static/class variable
  +-----------------------------+
  | - Singleton()               |  <-- private constructor
  | + getInstance(): Singleton  |  <-- public static method
  | + operation(): void         |
  +-----------------------------+

  How it works:
  +-----------+     +-------------------+
  | Client A  |---->|                   |
  +-----------+     |   getInstance()   |---> Same instance
  +-----------+     |                   |
  | Client B  |---->|                   |
  +-----------+     +-------------------+
  +-----------+
  | Client C  |---->  (all get the same object)
  +-----------+
```

---

## Java Implementation

### Approach 1: Basic Singleton (Not Thread-Safe)

```java
public class DatabaseConnectionPool {

    // Step 1: Static variable to hold the single instance
    private static DatabaseConnectionPool instance;

    // Step 2: Private constructor prevents external instantiation
    private DatabaseConnectionPool() {
        System.out.println("Initializing connection pool...");
        // In real code: create a pool of database connections
    }

    // Step 3: Public static method to get the instance
    public static DatabaseConnectionPool getInstance() {
        if (instance == null) {                    // Line A
            instance = new DatabaseConnectionPool(); // Line B
        }
        return instance;
    }

    public void executeQuery(String sql) {
        System.out.println("Executing: " + sql);
    }
}
```

**Line-by-line explanation:**

- `private static DatabaseConnectionPool instance;` -- A static field holds the one and only instance. It starts as `null`.
- `private DatabaseConnectionPool()` -- The constructor is `private`. No code outside this class can call `new DatabaseConnectionPool()`.
- `getInstance()` checks if `instance` is `null`. If yes, it creates one. If no, it returns the existing one.

**Usage and output:**

```java
public class Main {
    public static void main(String[] args) {
        // Both variables point to the SAME object
        DatabaseConnectionPool pool1 = DatabaseConnectionPool.getInstance();
        DatabaseConnectionPool pool2 = DatabaseConnectionPool.getInstance();

        pool1.executeQuery("SELECT * FROM orders");

        System.out.println("Same instance? " + (pool1 == pool2));
    }
}
```

```
Output:
Initializing connection pool...
Executing: SELECT * FROM orders
Same instance? true
```

Notice that "Initializing connection pool..." prints only once, even though `getInstance()` is called twice.

**The problem:** This is NOT thread-safe. Two threads could both see `instance == null` at Line A and both create new instances at Line B.

```
Thread 1: if (instance == null)  --> true  (instance is null)
Thread 2: if (instance == null)  --> true  (still null, Thread 1 hasn't finished)
Thread 1: instance = new DatabaseConnectionPool()  --> creates instance #1
Thread 2: instance = new DatabaseConnectionPool()  --> creates instance #2!

Result: TWO instances exist. Singleton violated.
```

### Approach 2: Thread-Safe with Double-Checked Locking

```java
public class DatabaseConnectionPool {

    // 'volatile' ensures all threads see the updated value
    private static volatile DatabaseConnectionPool instance;

    private final List<Connection> connections;

    private DatabaseConnectionPool() {
        System.out.println("Initializing connection pool...");
        connections = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            connections.add(createConnection());
        }
    }

    public static DatabaseConnectionPool getInstance() {
        // First check: avoid locking if instance already exists
        if (instance == null) {                            // Check 1
            synchronized (DatabaseConnectionPool.class) {  // Lock
                // Second check: another thread might have created
                // the instance between Check 1 and the Lock
                if (instance == null) {                    // Check 2
                    instance = new DatabaseConnectionPool();
                }
            }
        }
        return instance;
    }

    public Connection getConnection() {
        // Return a connection from the pool
        return connections.remove(0);
    }

    public void returnConnection(Connection conn) {
        connections.add(conn);
    }

    private Connection createConnection() {
        // Simplified - in real code, use actual DB connection
        return new Connection();
    }
}
```

**Line-by-line explanation:**

- `volatile` -- This keyword ensures that when one thread writes to `instance`, all other threads immediately see the new value. Without it, threads might cache a stale `null` value.
- First `if (instance == null)` (Check 1) -- A quick check without locking. If the instance already exists, we skip the expensive `synchronized` block entirely. This is why it is called "double-checked": we check twice.
- `synchronized (DatabaseConnectionPool.class)` -- Only one thread can enter this block at a time. This prevents two threads from creating two instances.
- Second `if (instance == null)` (Check 2) -- Inside the lock, we check again. Between Check 1 and acquiring the lock, another thread might have created the instance.

```
WHY DOUBLE-CHECKED LOCKING?

Without it (just synchronized):
  Thread 1: lock -> check -> create -> unlock
  Thread 2: lock -> check -> return  -> unlock   (SLOW: waits for lock)
  Thread 3: lock -> check -> return  -> unlock   (SLOW: waits for lock)
  Thread 4: lock -> check -> return  -> unlock   (SLOW: waits for lock)
  ... every call pays the locking cost

With double-checked locking:
  Thread 1: check1(null) -> lock -> check2(null) -> create -> unlock
  Thread 2: check1(null) -> lock -> check2(exists) -> return -> unlock
  Thread 3: check1(exists) -> return   (FAST: no lock needed)
  Thread 4: check1(exists) -> return   (FAST: no lock needed)
  ... after creation, no thread ever locks again
```

### Approach 3: Enum Singleton (Recommended in Java)

Joshua Bloch, author of *Effective Java*, recommends this as the best way to implement Singleton in Java.

```java
public enum DatabaseConnectionPool {

    INSTANCE;  // The single instance

    private final List<Object> connections = new ArrayList<>();

    // Constructor runs once when the enum is loaded
    DatabaseConnectionPool() {
        System.out.println("Initializing connection pool...");
        for (int i = 0; i < 10; i++) {
            connections.add(createConnection());
        }
    }

    public Object getConnection() {
        if (connections.isEmpty()) {
            throw new RuntimeException("No available connections");
        }
        return connections.remove(0);
    }

    public void returnConnection(Object conn) {
        connections.add(conn);
    }

    private Object createConnection() {
        return new Object(); // Simplified
    }
}
```

**Usage:**

```java
public class Main {
    public static void main(String[] args) {
        // Access via INSTANCE - clean and simple
        Object conn = DatabaseConnectionPool.INSTANCE.getConnection();
        System.out.println("Got connection: " + conn);
        DatabaseConnectionPool.INSTANCE.returnConnection(conn);
    }
}
```

```
Output:
Initializing connection pool...
Got connection: java.lang.Object@1b6d3586
```

**Why enum Singleton is best:**

```
+----------------------------------------------------------+
|  ENUM SINGLETON ADVANTAGES                               |
+----------------------------------------------------------+
|                                                          |
|  1. Thread-safe by default (JVM handles it)              |
|  2. Serialization-safe (no duplicate on deserialization)  |
|  3. Reflection-safe (cannot create via reflection)        |
|  4. Concise - no boilerplate code                        |
|  5. Lazy initialization by the JVM                        |
|                                                          |
+----------------------------------------------------------+
```

---

## Python Implementation

### Approach 1: Using `__new__`

```python
class DatabaseConnectionPool:
    """Singleton connection pool using __new__."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Initializing connection pool...")
            cls._instance = super().__new__(cls)
            cls._instance._connections = [f"conn_{i}" for i in range(10)]
        return cls._instance

    def get_connection(self) -> str:
        if not self._connections:
            raise RuntimeError("No available connections")
        return self._connections.pop()

    def return_connection(self, conn: str):
        self._connections.append(conn)
```

**Line-by-line explanation:**

- `_instance = None` -- Class variable that holds the single instance. `None` means no instance has been created yet.
- `__new__(cls)` -- This special method is called BEFORE `__init__`. It controls object creation. By overriding it, we control whether a new object is actually created.
- `if cls._instance is None` -- First time: `_instance` is `None`, so we create the object. Every subsequent time: `_instance` already exists, so we return it.
- `super().__new__(cls)` -- Calls the parent class `object.__new__()` to actually create the instance.
- We initialize `_connections` inside `__new__`, not in `__init__`, because `__init__` would run every time someone calls `DatabaseConnectionPool()`, resetting the connections.

**Usage and output:**

```python
pool1 = DatabaseConnectionPool()
pool2 = DatabaseConnectionPool()

conn = pool1.get_connection()
print(f"Got connection: {conn}")
print(f"Same instance? {pool1 is pool2}")
```

```
Output:
Initializing connection pool...
Got connection: conn_9
Same instance? True
```

### Approach 2: Using a Metaclass

```python
class SingletonMeta(type):
    """A metaclass that creates Singleton instances."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Create the instance using the normal mechanism
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class AppConfig(metaclass=SingletonMeta):
    """Application configuration - singleton via metaclass."""

    def __init__(self):
        print("Loading configuration...")
        self.database_url = "postgresql://localhost:5432/myapp"
        self.cache_ttl = 300
        self.debug_mode = False
        self.max_retries = 3

    def get(self, key: str):
        return getattr(self, key, None)

    def set(self, key: str, value):
        setattr(self, key, value)
```

**Line-by-line explanation:**

- `class SingletonMeta(type)` -- A metaclass is a "class of a class." It controls how classes themselves are created and called.
- `_instances = {}` -- A dictionary that maps each class to its singleton instance. This allows the metaclass to be reused for multiple singleton classes.
- `__call__` -- This method is invoked when you write `AppConfig()`. The metaclass intercepts the call and returns the existing instance if one exists.

**Usage and output:**

```python
config1 = AppConfig()
config2 = AppConfig()

config1.set("debug_mode", True)
print(f"Debug mode from config2: {config2.get('debug_mode')}")
print(f"Same instance? {config1 is config2}")
```

```
Output:
Loading configuration...
Debug mode from config2: True
Same instance? True
```

Notice that "Loading configuration..." prints only once, and changing a value through `config1` is immediately visible through `config2` because they are the same object.

### Approach 3: Module-Level Singleton (Pythonic Way)

In Python, a module is only loaded once. This means any object created at the module level is naturally a singleton.

```python
# config.py - The entire module IS the singleton

import json

class _AppConfig:
    """Internal config class. The singleton is the module-level instance."""

    def __init__(self, config_path: str = "config.json"):
        print("Loading configuration...")
        self._data = self._load(config_path)

    def _load(self, path: str) -> dict:
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "database_url": "postgresql://localhost:5432/myapp",
                "cache_ttl": 300,
                "debug_mode": False,
            }

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value


# The singleton instance - created when the module is first imported
config = _AppConfig()
```

**Usage:**

```python
# service_a.py
from config import config

print(config.get("database_url"))

# service_b.py
from config import config

config.set("debug_mode", True)
```

Both `service_a.py` and `service_b.py` get the same `config` object because Python only executes the module code once.

```
+----------------------------------------------------------+
|  PYTHONIC SINGLETON: MODULE-LEVEL APPROACH                |
+----------------------------------------------------------+
|                                                          |
|  PROS:                                                   |
|  - Simplest approach                                     |
|  - No special classes or metaclasses needed               |
|  - Thread-safe (Python's import system handles it)        |
|  - Naturally discoverable                                |
|                                                          |
|  CONS:                                                   |
|  - Instance is created at import time (eager, not lazy)  |
|  - Harder to mock in tests (but doable with patch)       |
|                                                          |
+----------------------------------------------------------+
```

### Thread Safety in Python

Python has the Global Interpreter Lock (GIL), which means only one thread executes Python bytecode at a time. However, the GIL does NOT make your singleton automatically thread-safe in all cases.

```python
import threading

class ThreadSafeConnectionPool:
    """Thread-safe singleton with a lock."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking - same idea as Java
                if cls._instance is None:
                    print("Initializing connection pool...")
                    cls._instance = super().__new__(cls)
                    cls._instance._connections = [
                        f"conn_{i}" for i in range(10)
                    ]
                    cls._instance._pool_lock = threading.Lock()
        return cls._instance

    def get_connection(self) -> str:
        with self._pool_lock:
            if not self._connections:
                raise RuntimeError("No available connections")
            return self._connections.pop()

    def return_connection(self, conn: str):
        with self._pool_lock:
            self._connections.append(conn)
```

---

## Spring Framework: @Scope("singleton")

Spring beans are singletons by default. You do not need to implement the pattern yourself.

```java
import org.springframework.stereotype.Component;

@Component  // Spring creates ONE instance and shares it
public class UserRepository {

    public UserRepository() {
        System.out.println("UserRepository created");
    }

    public User findById(int id) {
        // ... database query
        return new User(id, "John");
    }
}
```

```java
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private final UserRepository userRepository;

    // Spring injects the SAME UserRepository instance everywhere
    public OrderService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}
```

```java
@Service
public class PaymentService {

    private final UserRepository userRepository;

    // Same UserRepository instance as OrderService got
    public PaymentService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}
```

```
Spring Container:
+----------------------------------------------------------+
|                                                          |
|  Bean: userRepository (SINGLETON scope)                  |
|  +---------------------------------------------------+  |
|  |  UserRepository instance                          |  |
|  +---------------------------------------------------+  |
|        ^                    ^                            |
|        |                    |                            |
|  +-----+------+     +------+-------+                    |
|  | OrderService|     | PaymentService|                   |
|  +------------+     +--------------+                    |
|  (both share the same UserRepository)                   |
|                                                          |
+----------------------------------------------------------+
```

You can explicitly set the scope:

```java
@Component
@Scope("singleton")   // This is the DEFAULT - same as no @Scope
public class CacheManager {
    // ...
}

@Component
@Scope("prototype")   // NEW instance every time it is injected
public class RequestHandler {
    // ...
}
```

```
+----------------------------------+----------------------------------+
|  SINGLETON SCOPE (default)       |  PROTOTYPE SCOPE                 |
+----------------------------------+----------------------------------+
|  One instance per container      |  New instance every injection    |
|  Shared across all consumers     |  Each consumer gets its own      |
|  Created at startup (eager)      |  Created on demand (lazy)        |
|  Good for: stateless services    |  Good for: stateful objects      |
+----------------------------------+----------------------------------+
```

---

## Real-World Backend Use Case: Application Logger

A logger is one of the most natural uses of the Singleton pattern. You want exactly one logger instance to manage log files, formatting, and output destinations.

**Java Implementation:**

```java
public enum Logger {
    INSTANCE;

    private final List<String> logEntries = new ArrayList<>();
    private LogLevel currentLevel = LogLevel.INFO;

    public enum LogLevel {
        DEBUG, INFO, WARN, ERROR
    }

    public void setLevel(LogLevel level) {
        this.currentLevel = level;
    }

    public void debug(String message) {
        log(LogLevel.DEBUG, message);
    }

    public void info(String message) {
        log(LogLevel.INFO, message);
    }

    public void warn(String message) {
        log(LogLevel.WARN, message);
    }

    public void error(String message) {
        log(LogLevel.ERROR, message);
    }

    private void log(LogLevel level, String message) {
        if (level.ordinal() >= currentLevel.ordinal()) {
            String entry = String.format(
                "[%s] %s: %s",
                java.time.LocalDateTime.now(),
                level,
                message
            );
            logEntries.add(entry);
            System.out.println(entry);
        }
    }

    public List<String> getLogEntries() {
        return Collections.unmodifiableList(logEntries);
    }
}
```

**Usage:**

```java
// In OrderService.java
Logger.INSTANCE.info("Processing order #1234");

// In PaymentService.java
Logger.INSTANCE.info("Payment received for order #1234");

// In ErrorHandler.java
Logger.INSTANCE.error("Failed to connect to payment gateway");
```

```
Output:
[2024-01-15T10:30:45] INFO: Processing order #1234
[2024-01-15T10:30:46] INFO: Payment received for order #1234
[2024-01-15T10:30:47] ERROR: Failed to connect to payment gateway
```

**Python Implementation:**

```python
import datetime
from enum import IntEnum

class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._log_entries = []
            cls._instance._level = LogLevel.INFO
        return cls._instance

    def set_level(self, level: LogLevel):
        self._level = level

    def debug(self, message: str):
        self._log(LogLevel.DEBUG, message)

    def info(self, message: str):
        self._log(LogLevel.INFO, message)

    def warn(self, message: str):
        self._log(LogLevel.WARN, message)

    def error(self, message: str):
        self._log(LogLevel.ERROR, message)

    def _log(self, level: LogLevel, message: str):
        if level >= self._level:
            entry = f"[{datetime.datetime.now()}] {level.name}: {message}"
            self._log_entries.append(entry)
            print(entry)

    @property
    def log_entries(self):
        return list(self._log_entries)
```

**Usage:**

```python
# In order_service.py
logger = Logger()
logger.info("Processing order #1234")

# In payment_service.py
logger = Logger()
logger.info("Payment received for order #1234")

# Both 'logger' variables are the SAME object
```

---

## When Singletons Hurt

Singletons are not always the right choice. Here are the real dangers.

### 1. Hidden Dependencies

```java
// BAD: Hidden dependency on Singleton
public class OrderService {

    public void processOrder(Order order) {
        // Where does this dependency come from?
        // You cannot see it in the constructor.
        DatabaseConnectionPool.getInstance().executeQuery(
            "INSERT INTO orders ..."
        );
        Logger.INSTANCE.info("Order processed");
        CacheManager.getInstance().invalidate("orders");
    }
}

// BETTER: Explicit dependencies via constructor injection
public class OrderService {

    private final DatabaseConnectionPool pool;
    private final Logger logger;
    private final CacheManager cache;

    // Dependencies are VISIBLE and EXPLICIT
    public OrderService(DatabaseConnectionPool pool,
                        Logger logger,
                        CacheManager cache) {
        this.pool = pool;
        this.logger = logger;
        this.cache = cache;
    }

    public void processOrder(Order order) {
        pool.executeQuery("INSERT INTO orders ...");
        logger.info("Order processed");
        cache.invalidate("orders");
    }
}
```

### 2. Testing Nightmare

```java
// Hard to test: How do you replace the real database?
public class OrderServiceTest {

    @Test
    void testProcessOrder() {
        // PROBLEM: This uses the REAL database connection pool
        // You cannot replace it with a mock
        OrderService service = new OrderService();
        service.processOrder(new Order());
        // This test hits the real database!
    }
}
```

```python
# Hard to test: global state persists between tests
def test_logger_counts():
    logger = Logger()
    logger.info("Test message")

    # PROBLEM: If another test ran first, log_entries
    # already has entries from that test!
    assert len(logger.log_entries) == 1  # FAILS!
```

### 3. Global Mutable State

```
+----------------------------------------------------------+
|  THE GLOBAL STATE PROBLEM                                |
+----------------------------------------------------------+
|                                                          |
|  Thread A: config.set("max_retries", 5)                  |
|  Thread B: config.set("max_retries", 3)                  |
|  Thread C: retries = config.get("max_retries")           |
|                                                          |
|  What does Thread C get? 5? 3? It depends on timing.    |
|  This is a race condition caused by shared mutable       |
|  state in a singleton.                                   |
|                                                          |
+----------------------------------------------------------+
```

---

## When to Use / When NOT to Use

```
+----------------------------------+----------------------------------+
|  USE SINGLETON WHEN              |  DO NOT USE SINGLETON WHEN       |
+----------------------------------+----------------------------------+
|                                  |                                  |
| - Exactly one instance makes     | - You need different instances   |
|   logical sense (connection      |   for different contexts (e.g.,  |
|   pool, config, logger)          |   per-request state)             |
|                                  |                                  |
| - Creating multiple instances    | - You are using it as a lazy     |
|   would waste resources or       |   way to avoid passing           |
|   cause conflicts                |   dependencies                   |
|                                  |                                  |
| - The object is truly stateless  | - The singleton has mutable      |
|   or has read-only state         |   state accessed by multiple     |
|                                  |   threads                        |
|                                  |                                  |
| - Your framework manages the     | - You are making it a singleton  |
|   lifecycle for you (Spring)     |   "just in case"                 |
|                                  |                                  |
+----------------------------------+----------------------------------+
```

---

## Common Mistakes

1. **Forgetting thread safety.** The basic `if (instance == null)` check is not atomic. In multi-threaded backend services, always use thread-safe approaches.

2. **Using Singleton for everything.** Not everything needs to be a singleton. Request objects, user sessions, and domain entities should NOT be singletons.

3. **Storing request-specific state in a Singleton.** A singleton is shared across all requests. If you store `currentUser` in a singleton, all users will see the same user.

4. **Ignoring the testing cost.** If your singleton cannot be mocked or replaced in tests, you will end up with slow, fragile, integration-like unit tests.

5. **Singleton as a global variable.** If you are using Singleton just to avoid passing objects around, you are using global variables with extra steps.

---

## Best Practices

1. **Prefer framework-managed singletons.** In Spring, use `@Component` or `@Service`. In Python frameworks, use dependency injection. Let the framework handle the lifecycle.

2. **Use constructor injection.** Even if the underlying object is a singleton, inject it through constructors. This makes dependencies visible and testable.

3. **Make singletons immutable when possible.** If configuration is loaded once and never changes, make it read-only. This eliminates thread-safety concerns.

4. **In Java, prefer enum Singleton.** It is thread-safe, serialization-safe, and reflection-safe with zero boilerplate.

5. **In Python, prefer module-level singletons.** It is the most Pythonic approach and naturally thread-safe during import.

6. **Document that a class is a Singleton.** Not everyone will notice the private constructor or `__new__` override. A clear comment or docstring helps.

---

## Quick Summary

| Aspect | Details |
|--------|---------|
| Pattern name | Singleton |
| Category | Creational |
| Intent | Ensure exactly one instance exists |
| Problem it solves | Multiple instances wasting resources or causing conflicts |
| Java approaches | Private constructor + `getInstance()`, double-checked locking, enum (recommended) |
| Python approaches | `__new__`, metaclass, module-level (recommended) |
| Spring | Singleton scope is the default for all beans |
| Main danger | Hidden dependencies, testing difficulty, global mutable state |

---

## Key Points

1. The Singleton pattern guarantees exactly one instance of a class exists in the application.

2. In Java, the enum approach is the safest and most concise way to implement Singleton. It handles thread safety, serialization, and reflection automatically.

3. In Python, the module-level approach is the most idiomatic. A module is loaded once, so any object created at module level is naturally a singleton.

4. Thread safety is critical in backend applications. The basic `if null` check is not thread-safe. Use double-checked locking, enums, or framework support.

5. The biggest danger of Singleton is not the pattern itself but how developers misuse it: as a replacement for proper dependency injection, as a global variable, or as a place to store mutable shared state.

6. Modern frameworks like Spring manage singletons for you. Prefer framework-managed singletons over hand-rolled implementations.

---

## Practice Questions

1. Why is the basic Singleton implementation (without synchronization) not thread-safe? Describe a specific scenario where two threads could create two instances.

2. Explain what the `volatile` keyword does in the double-checked locking Singleton in Java. What would happen without it?

3. A developer stores the currently authenticated user in a Singleton `SessionManager`. Why is this dangerous in a backend serving multiple users concurrently?

4. Compare the enum Singleton approach in Java with the module-level approach in Python. What are the advantages and disadvantages of each?

5. Your team uses Spring Boot. A junior developer writes a hand-rolled Singleton with `private static instance` and `getInstance()` for a repository class. What would you suggest instead, and why?

---

## Exercises

### Exercise 1: Thread-Safe Configuration Manager

Implement a thread-safe `ConfigurationManager` singleton in both Java and Python. It should:
- Load configuration from a properties/JSON file on first access
- Provide `get(key)` and `getOrDefault(key, default)` methods
- Be immutable after initialization (no `set` method)
- Be thread-safe

### Exercise 2: Singleton vs. Dependency Injection

Refactor the following code to remove the Singleton dependency and use constructor injection instead. Then write a unit test that uses a mock.

```java
public class NotificationService {
    public void sendNotification(String userId, String message) {
        User user = UserRepository.getInstance().findById(userId);
        EmailClient.getInstance().send(user.getEmail(), message);
        Logger.getInstance().info("Notification sent to " + userId);
    }
}
```

### Exercise 3: Connection Pool with Metrics

Extend the `DatabaseConnectionPool` singleton to track:
- Total connections created
- Currently active connections
- Peak concurrent connections

Make sure the metrics tracking is thread-safe. Implement in both Java and Python.

---

## What Is Next?

In the next chapter, we explore the Factory Method pattern. While the Singleton controls how many instances exist, the Factory Method controls which class gets instantiated. You will learn how to decouple your code from concrete classes, making it easy to add new types (email, SMS, push notifications) without modifying existing code. This is the Open/Closed Principle in action.
