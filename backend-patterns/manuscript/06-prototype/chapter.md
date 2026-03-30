# Chapter 6: Prototype Pattern -- Clone Objects Efficiently

## What You Will Learn

- What the Prototype pattern is and why cloning objects matters
- The difference between deep copy and shallow copy
- How to implement Prototype in Java using `Cloneable`
- How to implement Prototype in Python using the `copy` module
- How to build a Prototype Registry for managing reusable templates
- Real-world applications: template configurations, test data factories

## Why This Chapter Matters

Creating objects from scratch is expensive when they require database calls, network
requests, or complex initialization. Sometimes you need dozens of objects that are
almost identical, differing only in a few fields. Building each one from the ground up
wastes time and resources.

The Prototype pattern solves this by letting you clone an existing object and then tweak
the copy. Think of it like photocopying a filled-out form and changing just the name on
each copy, instead of filling out every form from a blank page.

If you have ever duplicated a configuration file and changed two lines, you already
understand the Prototype pattern. This chapter teaches you how to do it properly in code.

---

## The Problem

Imagine you are building a cloud deployment tool. Each server configuration has 40+
fields: operating system, CPU count, memory, disk size, network settings, security
groups, monitoring flags, and more. Most servers share 90% of the same configuration.

**Without Prototype**, you do this:

```
ServerConfig web1 = new ServerConfig();
web1.setOs("Ubuntu 22.04");
web1.setCpu(4);
web1.setMemory(16384);
web1.setDisk(100);
web1.setNetwork("vpc-main");
web1.setSecurityGroup("sg-web");
web1.setMonitoring(true);
// ... 33 more setters

ServerConfig web2 = new ServerConfig();
web2.setOs("Ubuntu 22.04");       // same
web2.setCpu(4);                    // same
web2.setMemory(16384);             // same
web2.setDisk(100);                 // same
web2.setNetwork("vpc-main");       // same
web2.setSecurityGroup("sg-web");   // same
web2.setMonitoring(true);          // same
// ... 33 more identical setters
web2.setHostname("web-server-2");  // only this is different!
```

That is 40 lines of code duplicated for every server. If you need 50 servers, that is
2000 lines of nearly identical code.

---

## The Solution: Prototype Pattern

The Prototype pattern says: **create one well-configured object, then clone it**.

```
+---------------------+
|    <<interface>>     |
|     Prototype        |
+---------------------+
| + clone(): Prototype |
+---------------------+
         ^
         |
+---------------------+
|  ConcretePrototype   |
+---------------------+
| - field1             |
| - field2             |
| - field3             |
+---------------------+
| + clone(): Prototype |
+---------------------+

Usage:
  original ---clone()---> copy
                           |
                     modify fields
                           |
                        result
```

**Key participants:**

- **Prototype**: declares the clone method
- **ConcretePrototype**: implements cloning by copying its own fields
- **Client**: creates new objects by asking a prototype to clone itself

---

## Deep Copy vs Shallow Copy

Before writing code, you must understand this critical distinction.

```
SHALLOW COPY                          DEEP COPY
+----------+    +----------+          +----------+    +----------+
| Original |    |   Copy   |          | Original |    |   Copy   |
+----------+    +----------+          +----------+    +----------+
| name: A  |    | name: A  |          | name: A  |    | name: A  |
| tags: ---|------>[ list ] |          | tags: ---|->[ list1 ]    |
+----------+    +----------+          +----------+  | tags: ---|->[ list2 ]
                                                     +----------+
  Both point to the SAME list.          Each has its OWN list.
  Change one, both change.             Independent copies.
```

**Shallow copy** duplicates the object but shares references to nested objects. If the
original has a list of tags, the copy points to the same list. Add a tag to the copy and
it shows up in the original too.

**Deep copy** duplicates everything recursively. The copy gets its own independent list.
Changes to one never affect the other.

**Rule of thumb**: If your object contains only primitive fields (int, String, boolean),
shallow copy is fine. If it contains collections, arrays, or other objects, you almost
certainly need deep copy.

---

## Java Implementation

### Basic Prototype with Cloneable

Java provides the `Cloneable` interface and `Object.clone()` method for this pattern.

```java
// ServerConfig.java
import java.util.ArrayList;
import java.util.List;

public class ServerConfig implements Cloneable {
    private String hostname;
    private String os;
    private int cpu;
    private int memoryMb;
    private int diskGb;
    private String network;
    private String securityGroup;
    private boolean monitoring;
    private List<String> tags;

    public ServerConfig(String os, int cpu, int memoryMb, int diskGb,
                        String network, String securityGroup,
                        boolean monitoring) {
        this.os = os;
        this.cpu = cpu;
        this.memoryMb = memoryMb;
        this.diskGb = diskGb;
        this.network = network;
        this.securityGroup = securityGroup;
        this.monitoring = monitoring;
        this.tags = new ArrayList<>();
    }

    // Deep clone
    @Override
    public ServerConfig clone() {
        try {
            ServerConfig copy = (ServerConfig) super.clone();
            // Deep copy the mutable list
            copy.tags = new ArrayList<>(this.tags);
            return copy;
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException("Clone failed", e);
        }
    }

    public void setHostname(String hostname) { this.hostname = hostname; }
    public void addTag(String tag) { this.tags.add(tag); }
    public List<String> getTags() { return tags; }
    public String getHostname() { return hostname; }

    @Override
    public String toString() {
        return String.format("Server[host=%s, os=%s, cpu=%d, mem=%dMB, " +
                "disk=%dGB, net=%s, sg=%s, mon=%s, tags=%s]",
                hostname, os, cpu, memoryMb, diskGb, network,
                securityGroup, monitoring, tags);
    }
}
```

```java
// PrototypeDemo.java
public class PrototypeDemo {
    public static void main(String[] args) {
        // Step 1: Create and configure the template once
        ServerConfig webTemplate = new ServerConfig(
            "Ubuntu 22.04", 4, 16384, 100,
            "vpc-main", "sg-web", true
        );
        webTemplate.addTag("production");
        webTemplate.addTag("web-tier");

        // Step 2: Clone and customize
        ServerConfig web1 = webTemplate.clone();
        web1.setHostname("web-server-1");

        ServerConfig web2 = webTemplate.clone();
        web2.setHostname("web-server-2");
        web2.addTag("primary");

        // Step 3: Verify independence (deep copy proof)
        System.out.println(web1);
        System.out.println(web2);
        System.out.println("web1 tags: " + web1.getTags());
        System.out.println("web2 tags: " + web2.getTags());
        System.out.println("Same object? " + (web1 == web2));
    }
}
```

**Output:**
```
Server[host=web-server-1, os=Ubuntu 22.04, cpu=4, mem=16384MB, disk=100GB, net=vpc-main, sg=sg-web, mon=true, tags=[production, web-tier]]
Server[host=web-server-2, os=Ubuntu 22.04, cpu=4, mem=16384MB, disk=100GB, net=vpc-main, sg=sg-web, mon=true, tags=[production, web-tier, primary]]
web1 tags: [production, web-tier]
web2 tags: [production, web-tier, primary]
Same object? false
```

Notice that adding "primary" to web2's tags did not affect web1. That confirms our deep
copy works correctly.

### Copy Constructor Alternative

Many Java developers prefer copy constructors over `Cloneable` because they are more
explicit and avoid the checked exception hassle.

```java
public class ServerConfig {
    // ... fields ...

    // Copy constructor
    public ServerConfig(ServerConfig source) {
        this.hostname = source.hostname;
        this.os = source.os;
        this.cpu = source.cpu;
        this.memoryMb = source.memoryMb;
        this.diskGb = source.diskGb;
        this.network = source.network;
        this.securityGroup = source.securityGroup;
        this.monitoring = source.monitoring;
        this.tags = new ArrayList<>(source.tags); // deep copy
    }
}

// Usage:
ServerConfig web1 = new ServerConfig(webTemplate);
web1.setHostname("web-server-1");
```

This approach is recommended by Joshua Bloch in Effective Java. It gives you full
control over what gets copied and how.

---

## Python Implementation

### Using the copy Module

Python's `copy` module provides `copy()` for shallow copies and `deepcopy()` for deep
copies.

```python
# server_config.py
import copy

class ServerConfig:
    def __init__(self, os_name, cpu, memory_mb, disk_gb,
                 network, security_group, monitoring):
        self.hostname = None
        self.os_name = os_name
        self.cpu = cpu
        self.memory_mb = memory_mb
        self.disk_gb = disk_gb
        self.network = network
        self.security_group = security_group
        self.monitoring = monitoring
        self.tags = []
        self.metadata = {}

    def clone(self):
        """Create a deep copy of this config."""
        return copy.deepcopy(self)

    def add_tag(self, tag):
        self.tags.append(tag)

    def __repr__(self):
        return (f"Server[host={self.hostname}, os={self.os_name}, "
                f"cpu={self.cpu}, mem={self.memory_mb}MB, "
                f"disk={self.disk_gb}GB, tags={self.tags}]")


# Create the template
web_template = ServerConfig(
    os_name="Ubuntu 22.04",
    cpu=4,
    memory_mb=16384,
    disk_gb=100,
    network="vpc-main",
    security_group="sg-web",
    monitoring=True
)
web_template.add_tag("production")
web_template.add_tag("web-tier")

# Clone and customize
web1 = web_template.clone()
web1.hostname = "web-server-1"

web2 = web_template.clone()
web2.hostname = "web-server-2"
web2.add_tag("primary")

print(web1)
print(web2)
print(f"web1 tags: {web1.tags}")
print(f"web2 tags: {web2.tags}")
print(f"Same object? {web1 is web2}")
```

**Output:**
```
Server[host=web-server-1, os=Ubuntu 22.04, cpu=4, mem=16384MB, disk=100GB, tags=['production', 'web-tier']]
Server[host=web-server-2, os=Ubuntu 22.04, cpu=4, mem=16384MB, disk=100GB, tags=['production', 'web-tier', 'primary']]
web1 tags: ['production', 'web-tier']
web2 tags: ['production', 'web-tier', 'primary']
Same object? False
```

### Demonstrating Shallow vs Deep Copy

```python
import copy

class Team:
    def __init__(self, name):
        self.name = name
        self.members = ["Alice", "Bob"]

original = Team("Backend")

# Shallow copy -- shares the members list
shallow = copy.copy(original)
shallow.name = "Frontend"
shallow.members.append("Charlie")

print(f"Original members: {original.members}")
print(f"Shallow members:  {shallow.members}")
# Both show Charlie! The list is shared.

# Deep copy -- independent members list
original2 = Team("Backend")
deep = copy.deepcopy(original2)
deep.name = "Frontend"
deep.members.append("Diana")

print(f"Original2 members: {original2.members}")
print(f"Deep members:      {deep.members}")
# Only deep copy has Diana. Lists are independent.
```

**Output:**
```
Original members: ['Alice', 'Bob', 'Charlie']
Shallow members:  ['Alice', 'Bob', 'Charlie']
Original2 members: ['Alice', 'Bob']
Deep members:      ['Alice', 'Bob', 'Diana']
```

### Customizing Copy Behavior with __copy__ and __deepcopy__

Python lets you control exactly how your objects are copied.

```python
import copy

class DatabaseConfig:
    """Some fields should never be copied (like active connections)."""

    def __init__(self, host, port, db_name):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.connection = None  # should NOT be copied
        self.query_cache = {}   # should be reset on copy

    def __deepcopy__(self, memo):
        # Create new instance without calling __init__
        new_obj = DatabaseConfig.__new__(DatabaseConfig)
        memo[id(self)] = new_obj

        # Copy fields selectively
        new_obj.host = self.host
        new_obj.port = self.port
        new_obj.db_name = copy.deepcopy(self.db_name, memo)
        new_obj.connection = None       # reset, don't copy
        new_obj.query_cache = {}        # reset, don't copy

        return new_obj

    def __repr__(self):
        return (f"DBConfig[{self.host}:{self.port}/{self.db_name}, "
                f"connected={self.connection is not None}]")


config = DatabaseConfig("db.prod.internal", 5432, "users_db")
config.connection = "<active connection>"
config.query_cache = {"users": [1, 2, 3]}

clone = copy.deepcopy(config)
print(f"Original: {config}")
print(f"Clone:    {clone}")
print(f"Clone connection: {clone.connection}")
print(f"Clone cache: {clone.query_cache}")
```

**Output:**
```
Original: DBConfig[db.prod.internal:5432/users_db, connected=True]
Clone:    DBConfig[db.prod.internal:5432/users_db, connected=False]
Clone connection: None
Clone cache: {}
```

This is powerful: you decide which fields are cloned, which are reset, and which are
shared.

---

## Prototype Registry

A **Prototype Registry** stores pre-configured prototypes by name. Instead of
remembering how to configure each type of object, you look up a template and clone it.

```
+------------------------------+
|      PrototypeRegistry       |
+------------------------------+
|  "web-small"  -> ServerConfig|
|  "web-large"  -> ServerConfig|
|  "db-primary" -> ServerConfig|
|  "cache"      -> ServerConfig|
+------------------------------+
| + register(name, prototype)  |
| + get(name): ServerConfig    |
+------------------------------+

  registry.get("web-small")
       |
       v
    clone()
       |
       v
  new independent copy
```

### Java Prototype Registry

```java
import java.util.HashMap;
import java.util.Map;

public class ServerRegistry {
    private final Map<String, ServerConfig> prototypes = new HashMap<>();

    public void register(String name, ServerConfig prototype) {
        prototypes.put(name, prototype);
    }

    public ServerConfig create(String name) {
        ServerConfig prototype = prototypes.get(name);
        if (prototype == null) {
            throw new IllegalArgumentException(
                "No prototype registered: " + name);
        }
        return prototype.clone();
    }

    public boolean has(String name) {
        return prototypes.containsKey(name);
    }
}
```

```java
// RegistryDemo.java
public class RegistryDemo {
    public static void main(String[] args) {
        ServerRegistry registry = new ServerRegistry();

        // Register templates once at startup
        ServerConfig webSmall = new ServerConfig(
            "Ubuntu 22.04", 2, 4096, 50,
            "vpc-main", "sg-web", true);
        webSmall.addTag("web-tier");

        ServerConfig webLarge = new ServerConfig(
            "Ubuntu 22.04", 8, 32768, 200,
            "vpc-main", "sg-web", true);
        webLarge.addTag("web-tier");
        webLarge.addTag("high-traffic");

        ServerConfig dbPrimary = new ServerConfig(
            "Ubuntu 22.04", 16, 65536, 1000,
            "vpc-data", "sg-database", true);
        dbPrimary.addTag("database");
        dbPrimary.addTag("primary");

        registry.register("web-small", webSmall);
        registry.register("web-large", webLarge);
        registry.register("db-primary", dbPrimary);

        // Create servers from templates
        ServerConfig server1 = registry.create("web-small");
        server1.setHostname("web-1");

        ServerConfig server2 = registry.create("web-large");
        server2.setHostname("web-2");

        ServerConfig server3 = registry.create("db-primary");
        server3.setHostname("db-main");

        System.out.println(server1);
        System.out.println(server2);
        System.out.println(server3);
    }
}
```

**Output:**
```
Server[host=web-1, os=Ubuntu 22.04, cpu=2, mem=4096MB, disk=50GB, net=vpc-main, sg=sg-web, mon=true, tags=[web-tier]]
Server[host=web-2, os=Ubuntu 22.04, cpu=8, mem=32768MB, disk=200GB, net=vpc-main, sg=sg-web, mon=true, tags=[web-tier, high-traffic]]
Server[host=db-main, os=Ubuntu 22.04, cpu=16, mem=65536MB, disk=1000GB, net=vpc-data, sg=sg-database, mon=true, tags=[database, primary]]
```

### Python Prototype Registry

```python
import copy

class PrototypeRegistry:
    def __init__(self):
        self._prototypes = {}

    def register(self, name, prototype):
        self._prototypes[name] = prototype

    def create(self, name, **overrides):
        if name not in self._prototypes:
            raise KeyError(f"No prototype registered: {name}")

        clone = copy.deepcopy(self._prototypes[name])

        # Apply any field overrides
        for key, value in overrides.items():
            setattr(clone, key, value)

        return clone

    def list_templates(self):
        return list(self._prototypes.keys())


# Setup
registry = PrototypeRegistry()

web_small = ServerConfig("Ubuntu 22.04", 2, 4096, 50,
                         "vpc-main", "sg-web", True)
web_small.add_tag("web-tier")

db_template = ServerConfig("Ubuntu 22.04", 16, 65536, 1000,
                           "vpc-data", "sg-database", True)
db_template.add_tag("database")

registry.register("web-small", web_small)
registry.register("db-primary", db_template)

# Create with overrides
server = registry.create("web-small", hostname="web-1")
db = registry.create("db-primary", hostname="db-main")

print(server)
print(db)
print(f"Available templates: {registry.list_templates()}")
```

**Output:**
```
Server[host=web-1, os=Ubuntu 22.04, cpu=2, mem=4096MB, disk=50GB, tags=['web-tier']]
Server[host=db-main, os=Ubuntu 22.04, cpu=16, mem=65536MB, disk=1000GB, tags=['database']]
Available templates: ['web-small', 'db-primary']
```

---

## Real-World Use Case: Test Data Factory

Prototype shines when generating test data. Tests need many similar objects with small
variations.

```python
import copy
from datetime import datetime, timedelta

class User:
    def __init__(self):
        self.id = None
        self.name = "Test User"
        self.email = "test@example.com"
        self.role = "viewer"
        self.is_active = True
        self.created_at = datetime.now()
        self.preferences = {
            "theme": "light",
            "language": "en",
            "notifications": True
        }

    def __repr__(self):
        return (f"User(id={self.id}, name='{self.name}', "
                f"email='{self.email}', role='{self.role}')")


class TestDataFactory:
    """Factory that uses prototypes to generate test data quickly."""

    _counter = 0

    def __init__(self):
        self._prototypes = {}
        self._setup_defaults()

    def _setup_defaults(self):
        # Standard user prototype
        standard = User()
        self._prototypes["standard"] = standard

        # Admin user prototype
        admin = User()
        admin.name = "Admin User"
        admin.email = "admin@example.com"
        admin.role = "admin"
        admin.preferences["theme"] = "dark"
        self._prototypes["admin"] = admin

        # Inactive user prototype
        inactive = User()
        inactive.is_active = False
        inactive.name = "Inactive User"
        self._prototypes["inactive"] = inactive

    def create_user(self, template="standard", **overrides):
        TestDataFactory._counter += 1
        user = copy.deepcopy(self._prototypes[template])
        user.id = TestDataFactory._counter

        for key, value in overrides.items():
            setattr(user, key, value)

        return user

    def create_users(self, count, template="standard"):
        return [self.create_user(template) for _ in range(count)]


# Usage in tests
factory = TestDataFactory()

# Quick single users
alice = factory.create_user(name="Alice", email="alice@test.com")
admin = factory.create_user("admin", name="Bob")
inactive = factory.create_user("inactive")

print(alice)
print(admin)
print(inactive)

# Bulk creation
viewers = factory.create_users(3)
print(f"\nBulk viewers: {viewers}")

# Verify independence
alice.preferences["theme"] = "dark"
another = factory.create_user()
print(f"\nAlice theme: {alice.preferences['theme']}")
print(f"Another theme: {another.preferences['theme']}")
```

**Output:**
```
User(id=1, name='Alice', email='alice@test.com', role='viewer')
User(id=2, name='Bob', email='admin@example.com', role='admin')
User(id=3, name='Inactive User', email='test@example.com', role='viewer')

Bulk viewers: [User(id=4, name='Test User', email='test@example.com', role='viewer'), User(id=5, name='Test User', email='test@example.com', role='viewer'), User(id=6, name='Test User', email='test@example.com', role='viewer')]

Alice theme: dark
Another theme: light
```

---

## Real-World Use Case: Template Configurations

```java
// EmailTemplate.java
import java.util.HashMap;
import java.util.Map;

public class EmailTemplate implements Cloneable {
    private String subject;
    private String body;
    private String sender;
    private Map<String, String> headers;
    private String contentType;

    public EmailTemplate(String subject, String body, String sender) {
        this.subject = subject;
        this.body = body;
        this.sender = sender;
        this.headers = new HashMap<>();
        this.contentType = "text/html";
    }

    @Override
    public EmailTemplate clone() {
        try {
            EmailTemplate copy = (EmailTemplate) super.clone();
            copy.headers = new HashMap<>(this.headers);
            return copy;
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }

    public void setSubject(String subject) { this.subject = subject; }
    public void setBody(String body) { this.body = body; }
    public void addHeader(String key, String value) {
        headers.put(key, value);
    }

    @Override
    public String toString() {
        return String.format("Email[to=%s, subject='%s', type=%s, " +
                "headers=%s]", sender, subject, contentType, headers);
    }
}

// Usage
public class EmailDemo {
    public static void main(String[] args) {
        // Create base template
        EmailTemplate welcomeTemplate = new EmailTemplate(
            "Welcome to Our Platform",
            "<h1>Welcome, {{name}}!</h1><p>Get started...</p>",
            "noreply@platform.com"
        );
        welcomeTemplate.addHeader("X-Priority", "1");
        welcomeTemplate.addHeader("X-Category", "onboarding");

        // Clone for different users
        EmailTemplate email1 = welcomeTemplate.clone();
        email1.setBody("<h1>Welcome, Alice!</h1><p>Get started...</p>");

        EmailTemplate email2 = welcomeTemplate.clone();
        email2.setBody("<h1>Welcome, Bob!</h1><p>Get started...</p>");

        // Clone and modify for a different template type
        EmailTemplate resetTemplate = welcomeTemplate.clone();
        resetTemplate.setSubject("Password Reset Request");
        resetTemplate.setBody("<h1>Reset your password</h1>");
        resetTemplate.addHeader("X-Category", "security");

        System.out.println(email1);
        System.out.println(email2);
        System.out.println(resetTemplate);
    }
}
```

**Output:**
```
Email[to=noreply@platform.com, subject='Welcome to Our Platform', type=text/html, headers={X-Priority=1, X-Category=onboarding}]
Email[to=noreply@platform.com, subject='Welcome to Our Platform', type=text/html, headers={X-Priority=1, X-Category=onboarding}]
Email[to=noreply@platform.com, subject='Password Reset Request', type=text/html, headers={X-Priority=1, X-Category=security}]
```

---

## Before vs After Comparison

### Before: Without Prototype

```java
// Creating test users manually -- repetitive and error-prone
User user1 = new User();
user1.setName("Test User 1");
user1.setEmail("test1@example.com");
user1.setRole("viewer");
user1.setActive(true);
user1.setTheme("light");
user1.setLanguage("en");
user1.setNotifications(true);
user1.setCreatedAt(new Date());

User user2 = new User();
user2.setName("Test User 2");
user2.setEmail("test2@example.com");
user2.setRole("viewer");        // same
user2.setActive(true);           // same
user2.setTheme("light");         // same
user2.setLanguage("en");         // same
user2.setNotifications(true);    // same
user2.setCreatedAt(new Date());  // same

// Repeat 50 more times...
```

**Problems:**
- Massive code duplication
- Easy to miss a field
- Hard to update when a new field is added
- No single source of truth for "default" configuration

### After: With Prototype

```java
User template = createDefaultUser();

User user1 = template.clone();
user1.setName("Test User 1");
user1.setEmail("test1@example.com");

User user2 = template.clone();
user2.setName("Test User 2");
user2.setEmail("test2@example.com");

// Clean, maintainable, consistent
```

**Benefits:**
- One template captures all defaults
- Changes to defaults propagate automatically
- Cloning is faster than constructing from scratch
- Less code, fewer bugs

---

## When to Use / When NOT to Use

### Use Prototype When

- Objects have many fields and most are the same across instances
- Object creation is expensive (database lookups, file parsing, network calls)
- You need many variations of a base configuration
- You want to avoid building complex class hierarchies of factories
- Runtime object creation from templates is needed
- Test data generation requires many similar objects

### Do NOT Use Prototype When

- Objects are simple with few fields (just use a constructor)
- Every instance is completely different (nothing to share)
- Objects have no mutable state (use a shared reference instead)
- Circular references make deep copying complex and error-prone
- The object graph is very deep and cloning is actually slower than construction
- Objects hold non-cloneable resources (threads, file handles, sockets)

---

## Common Mistakes

### Mistake 1: Forgetting Deep Copy

```java
// WRONG: shallow copy shares the list
@Override
public Config clone() {
    try {
        return (Config) super.clone(); // tags list is shared!
    } catch (CloneNotSupportedException e) {
        throw new RuntimeException(e);
    }
}

// RIGHT: deep copy mutable fields
@Override
public Config clone() {
    try {
        Config copy = (Config) super.clone();
        copy.tags = new ArrayList<>(this.tags);    // new list
        copy.metadata = new HashMap<>(this.metadata); // new map
        return copy;
    } catch (CloneNotSupportedException e) {
        throw new RuntimeException(e);
    }
}
```

### Mistake 2: Cloning Non-Cloneable Resources

```python
# WRONG: cloning a database connection
class Service:
    def __init__(self):
        self.db_connection = create_connection()  # cannot clone this
        self.config = {...}

    def clone(self):
        return copy.deepcopy(self)  # will fail or create invalid state

# RIGHT: reset non-cloneable fields
def __deepcopy__(self, memo):
    new_obj = Service.__new__(Service)
    new_obj.config = copy.deepcopy(self.config, memo)
    new_obj.db_connection = None  # must be initialized separately
    return new_obj
```

### Mistake 3: Modifying the Prototype Itself

```python
# WRONG: accidentally modifying the template
template = registry.get("web-server")  # this IS the template
template.hostname = "oops"  # you just changed the template!

# RIGHT: always clone first
server = registry.create("web-server")  # returns a clone
server.hostname = "web-1"  # safe to modify
```

---

## Best Practices

1. **Always deep copy mutable fields.** Lists, maps, sets, and nested objects must be
   independently copied. This is the number one source of Prototype bugs.

2. **Use copy constructors in Java over Cloneable.** The `Cloneable` interface is
   considered broken by many experts. Copy constructors are explicit and type-safe.

3. **Document what gets copied.** Not every field should be cloned (connections, caches,
   IDs). Make it clear in comments or documentation.

4. **Make prototypes immutable after registration.** Once a prototype is stored in a
   registry, treat it as read-only. Any modification corrupts all future clones.

5. **Combine with Registry pattern.** A prototype by itself is useful. A prototype
   registry makes it powerful for managing multiple templates.

6. **Generate unique IDs on clone.** Cloned objects should get new IDs, not copies of
   the original's ID. Handle this in the clone method or factory.

7. **Test clone independence.** Write tests that modify a clone and verify the original
   is unchanged. This catches shallow copy bugs early.

---

## Quick Summary

The Prototype pattern creates new objects by cloning existing ones. It eliminates
repetitive construction code and is especially useful when objects share most of their
configuration. Deep copy ensures clones are fully independent. A Prototype Registry
provides named access to pre-configured templates.

```
Problem:  Creating many similar objects is repetitive and expensive.
Solution: Clone a template object and customize the copy.
Key:      Always use deep copy for objects with mutable nested fields.
```

---

## Key Points

- **Prototype** creates objects by cloning rather than constructing from scratch
- **Shallow copy** shares references to nested objects; **deep copy** creates independent copies
- Java offers `Cloneable` and `Object.clone()`, but copy constructors are often preferred
- Python's `copy.deepcopy()` handles deep cloning; customize with `__deepcopy__`
- A **Prototype Registry** maps names to pre-configured templates for easy lookup
- Always deep copy mutable fields (lists, maps, nested objects)
- Prototype shines for test data generation and configuration templates
- Never clone non-cloneable resources like connections or threads

---

## Practice Questions

1. What is the difference between shallow copy and deep copy? Give an example where
   using shallow copy instead of deep copy would cause a bug.

2. Why does Joshua Bloch recommend copy constructors over `Cloneable` in Java? What
   are two specific advantages?

3. You have a `Report` object with a `List<Chart>` field, and each `Chart` has a
   `List<DataPoint>`. Describe step by step how you would implement deep cloning for
   this object in Java.

4. In what scenario would cloning an object actually be slower than constructing a new
   one? Describe a concrete example.

5. How does a Prototype Registry improve upon using the Prototype pattern alone?

---

## Exercises

### Exercise 1: Document Template System

Build a document template system with the following requirements:

- A `Document` class with fields: title, author, content, metadata (Map), tags (List),
  and creation date
- A `DocumentRegistry` that stores named templates ("invoice", "report", "memo")
- Cloning a document must produce a fully independent copy
- The creation date should reset to "now" on every clone, not copy the original's date
- Write a test that creates 3 invoices from the template, modifies each differently,
  and verifies they are independent

### Exercise 2: Game Character Prototype

Create a role-playing game character system:

- A `Character` class with name, health, attack, defense, inventory (List of Items),
  and skills (Map of skill name to level)
- Pre-register three archetypes: "warrior", "mage", "rogue"
- Implement both shallow and deep clone methods
- Write code that demonstrates the bug caused by shallow cloning (modifying one
  character's inventory affects another) and then fix it with deep cloning

### Exercise 3: API Response Caching with Prototype

Design a caching layer that stores API response prototypes:

- Cache stores prototype `ApiResponse` objects (status, headers Map, body, timestamp)
- When a cache hit occurs, return a deep clone (so callers can modify without corrupting
  the cache)
- The timestamp on the clone should reflect "now", not the cached time
- Implement cache expiration: entries older than N seconds return null
- Demonstrate that modifying a returned response does not affect the cached version

---

## What Is Next?

In the next chapter, we move from creating objects to structuring them. The **Adapter
Pattern** shows you how to make incompatible interfaces work together, like plugging a
European appliance into an American outlet. Where Prototype is about efficient creation,
Adapter is about seamless integration between systems that were never designed to
collaborate.
