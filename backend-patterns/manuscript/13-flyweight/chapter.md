# Chapter 13: Flyweight Pattern -- Share Common State, Save Memory

## What You Will Learn

- What the Flyweight pattern is and why shared state saves memory
- The difference between intrinsic state (shared) and extrinsic state (unique)
- How to implement Flyweight in Java with a connection pool example
- How to implement Flyweight in Python with game entities
- When memory optimization matters and when it does not
- How to measure and verify memory savings

## Why This Chapter Matters

Imagine a game server managing 100,000 trees in a forest. Each tree has a texture image
(2MB), a mesh model (1MB), and a color palette (100KB). If every tree object stores its
own copy of these assets, you need 300GB of memory. But there are only 5 types of trees.
With Flyweight, you store 5 sets of shared data (15MB) and 100,000 tiny objects holding
just position and size (a few megabytes). Total: under 20MB instead of 300GB.

Flyweight is not about clever algorithms. It is about a simple realization: when
thousands of objects share the same data, store that data once and share it.

---

## The Problem

You are building a text editor that represents every character on screen as an object.
A typical document has 50,000 characters. Each character object stores:

```
Character {
    char value;          // 'A'           -- 2 bytes
    String fontFamily;   // "Arial"       -- ~40 bytes
    int fontSize;        // 12            -- 4 bytes
    Color color;         // RGB           -- 12 bytes
    boolean bold;        // true/false    -- 1 byte
    boolean italic;      // true/false    -- 1 byte
    int x, y;            // position      -- 8 bytes
}
// Object overhead:                       -- ~16 bytes
// Total per character:                   -- ~84 bytes
// 50,000 characters * 84 bytes = 4.2 MB
```

But most characters share the same font, size, color, and style. A document might use
only 10 distinct formatting combinations. With Flyweight, you store those 10 formatting
objects and each character just references one, plus its own position.

```
SharedFormat {                Character {
    fontFamily: "Arial"           format: -> SharedFormat  // 8 bytes (reference)
    fontSize: 12                  value: 'A'               // 2 bytes
    color: BLACK                  x: 150                   // 4 bytes
    bold: false                   y: 200                   // 4 bytes
    italic: false             }                            // + 16 bytes overhead
}                             // Total per character: ~34 bytes
                              // 50,000 * 34 = 1.7 MB (60% less)
```

---

## The Solution: Flyweight Pattern

```
+---------------------------+
|    FlyweightFactory       |
+---------------------------+
| - cache: Map<Key, Fly>    |
+---------------------------+
| + get(key): Flyweight     |
+---------------------------+
         |
         | creates/returns
         v
+---------------------------+
|      Flyweight            |
+---------------------------+
| Intrinsic State           |
| (shared, immutable)       |
+---------------------------+
| + operation(extrinsic)    |
+---------------------------+

  Client holds:
  +-----------+     +---------------------------+
  | Context   |---->|      Flyweight            |
  +-----------+     | (shared among many        |
  | extrinsic |     |  context objects)          |
  | state     |     +---------------------------+
  +-----------+
```

**Key concepts:**

- **Intrinsic state**: Data that is shared across many objects. It is stored inside the
  flyweight and never changes. Examples: font family, texture, mesh model, icon image.

- **Extrinsic state**: Data unique to each instance. It is stored outside the flyweight,
  typically by the client or context. Examples: position, timestamp, user ID.

- **Flyweight Factory**: Creates and caches flyweight objects. When asked for a
  flyweight, it returns an existing one if possible, or creates a new one.

```
INTRINSIC vs EXTRINSIC STATE

+----------------------------------------------------+
|                     Tree Object                     |
+----------------------------------------------------+
| INTRINSIC (shared)        | EXTRINSIC (unique)     |
|---------------------------|------------------------|
| texture: oak_texture.png  | x: 150                 |
| mesh: oak_model.obj       | y: 340                 |
| color_palette: autumn     | scale: 1.2             |
| species: "Oak"            | health: 85             |
| base_height: 15           | age: 30                |
+----------------------------------------------------+
    Stored ONCE per type         Stored per instance
    (5 tree types = 5 copies)    (100,000 instances)
```

---

## Java Implementation: Connection Pool

A database connection pool is a practical Flyweight. The "intrinsic state" is the
connection configuration and the pooled connection itself. The "extrinsic state" is
which query is being executed and by whom.

### The Flyweight: Connection Configuration

```java
import java.util.Objects;

public class ConnectionConfig {
    private final String host;
    private final int port;
    private final String database;
    private final String driver;
    private final int timeoutSeconds;

    public ConnectionConfig(String host, int port, String database,
                            String driver, int timeoutSeconds) {
        this.host = host;
        this.port = port;
        this.database = database;
        this.driver = driver;
        this.timeoutSeconds = timeoutSeconds;
    }

    public String getConnectionString() {
        return String.format("%s://%s:%d/%s?timeout=%d",
                driver, host, port, database, timeoutSeconds);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ConnectionConfig)) return false;
        ConnectionConfig that = (ConnectionConfig) o;
        return port == that.port &&
               timeoutSeconds == that.timeoutSeconds &&
               host.equals(that.host) &&
               database.equals(that.database) &&
               driver.equals(that.driver);
    }

    @Override
    public int hashCode() {
        return Objects.hash(host, port, database, driver, timeoutSeconds);
    }

    @Override
    public String toString() {
        return getConnectionString();
    }
}
```

### The Flyweight Factory: Connection Pool

```java
import java.util.HashMap;
import java.util.Map;
import java.util.Queue;
import java.util.LinkedList;

public class ConnectionPool {
    private final Map<String, Queue<PooledConnection>> pool;
    private final Map<String, ConnectionConfig> configs;
    private final int maxPerKey;
    private int totalCreated = 0;
    private int totalReused = 0;

    public ConnectionPool(int maxPerKey) {
        this.pool = new HashMap<>();
        this.configs = new HashMap<>();
        this.maxPerKey = maxPerKey;
    }

    public void registerConfig(String name, ConnectionConfig config) {
        configs.put(name, config);
        pool.putIfAbsent(name, new LinkedList<>());
    }

    public PooledConnection acquire(String configName) {
        Queue<PooledConnection> available = pool.get(configName);
        if (available == null) {
            throw new IllegalArgumentException(
                "Unknown config: " + configName);
        }

        if (!available.isEmpty()) {
            totalReused++;
            PooledConnection conn = available.poll();
            conn.markAcquired();
            System.out.printf("  [REUSE] Connection for '%s' "
                    + "(pool size: %d)%n", configName, available.size());
            return conn;
        }

        totalCreated++;
        ConnectionConfig config = configs.get(configName);
        PooledConnection conn = new PooledConnection(config, configName);
        conn.markAcquired();
        System.out.printf("  [NEW]   Connection for '%s' created%n",
                configName);
        return conn;
    }

    public void release(PooledConnection connection) {
        String name = connection.getConfigName();
        Queue<PooledConnection> available = pool.get(name);

        if (available.size() < maxPerKey) {
            connection.markReleased();
            available.offer(connection);
            System.out.printf("  [RETURN] Connection for '%s' "
                    + "returned to pool (pool size: %d)%n",
                    name, available.size());
        } else {
            connection.close();
            System.out.printf("  [CLOSE] Connection for '%s' "
                    + "closed (pool full)%n", name);
        }
    }

    public void printStats() {
        System.out.printf("%nPool Stats: %d created, %d reused "
                + "(%.0f%% reuse rate)%n",
                totalCreated, totalReused,
                totalCreated + totalReused == 0 ? 0 :
                (100.0 * totalReused / (totalCreated + totalReused)));
    }
}
```

```java
public class PooledConnection {
    private final ConnectionConfig config;  // intrinsic (shared)
    private final String configName;
    private boolean inUse;                  // extrinsic (per-use)
    private long acquiredAt;                // extrinsic (per-use)

    public PooledConnection(ConnectionConfig config, String configName) {
        this.config = config;
        this.configName = configName;
        this.inUse = false;
    }

    public void markAcquired() {
        this.inUse = true;
        this.acquiredAt = System.currentTimeMillis();
    }

    public void markReleased() {
        this.inUse = false;
    }

    public void close() {
        this.inUse = false;
    }

    public String getConfigName() { return configName; }
    public boolean isInUse() { return inUse; }

    // Execute uses shared config (intrinsic) with per-call query (extrinsic)
    public String execute(String query) {
        return String.format("Executing '%s' on %s", query, config);
    }
}
```

### Demo

```java
public class ConnectionPoolDemo {
    public static void main(String[] args) {
        ConnectionPool pool = new ConnectionPool(3);

        // Register shared configurations (intrinsic state)
        pool.registerConfig("users-db", new ConnectionConfig(
                "db1.internal", 5432, "users", "postgresql", 30));
        pool.registerConfig("orders-db", new ConnectionConfig(
                "db2.internal", 5432, "orders", "postgresql", 30));

        System.out.println("=== Round 1: First requests ===");
        PooledConnection c1 = pool.acquire("users-db");
        PooledConnection c2 = pool.acquire("users-db");
        PooledConnection c3 = pool.acquire("orders-db");

        System.out.println("\n=== Executing queries (extrinsic state) ===");
        System.out.println(c1.execute("SELECT * FROM users WHERE id=1"));
        System.out.println(c2.execute("SELECT * FROM users WHERE id=2"));
        System.out.println(c3.execute("SELECT * FROM orders LIMIT 10"));

        System.out.println("\n=== Releasing connections ===");
        pool.release(c1);
        pool.release(c2);
        pool.release(c3);

        System.out.println("\n=== Round 2: Connections reused ===");
        PooledConnection c4 = pool.acquire("users-db");
        PooledConnection c5 = pool.acquire("orders-db");
        System.out.println(c4.execute("SELECT COUNT(*) FROM users"));
        System.out.println(c5.execute("INSERT INTO orders VALUES(...)"));

        pool.release(c4);
        pool.release(c5);

        pool.printStats();
    }
}
```

**Output:**
```
=== Round 1: First requests ===
  [NEW]   Connection for 'users-db' created
  [NEW]   Connection for 'users-db' created
  [NEW]   Connection for 'orders-db' created

=== Executing queries (extrinsic state) ===
Executing 'SELECT * FROM users WHERE id=1' on postgresql://db1.internal:5432/users?timeout=30
Executing 'SELECT * FROM users WHERE id=2' on postgresql://db1.internal:5432/users?timeout=30
Executing 'SELECT * FROM orders LIMIT 10' on postgresql://db2.internal:5432/orders?timeout=30

=== Releasing connections ===
  [RETURN] Connection for 'users-db' returned to pool (pool size: 1)
  [RETURN] Connection for 'users-db' returned to pool (pool size: 2)
  [RETURN] Connection for 'orders-db' returned to pool (pool size: 1)

=== Round 2: Connections reused ===
  [REUSE] Connection for 'users-db' (pool size: 1)
  [REUSE] Connection for 'orders-db' (pool size: 0)
Executing 'SELECT COUNT(*) FROM users' on postgresql://db1.internal:5432/users?timeout=30
Executing 'INSERT INTO orders VALUES(...)' on postgresql://db2.internal:5432/orders?timeout=30
  [RETURN] Connection for 'users-db' returned to pool (pool size: 2)
  [RETURN] Connection for 'orders-db' returned to pool (pool size: 1)

Pool Stats: 3 created, 2 reused (40% reuse rate)
```

The `ConnectionConfig` is intrinsic state, shared among all connections to the same
database. The query string and timing are extrinsic state, different every time.

---

## Python Implementation: Game Entities

### Sharing Sprite Data Across Thousands of Entities

```python
import sys


class SpriteData:
    """Intrinsic state: shared graphical data for an entity type.

    In a real game, this would hold actual texture bytes, mesh data, etc.
    Here we simulate it with a large byte array.
    """

    def __init__(self, entity_type, texture_size_kb, animation_frames):
        self.entity_type = entity_type
        self.animation_frames = animation_frames
        # Simulate large texture data
        self.texture_data = bytearray(texture_size_kb * 1024)
        self.frame_count = len(animation_frames)

    def get_frame(self, frame_index):
        return self.animation_frames[frame_index % self.frame_count]


class SpriteFactory:
    """Flyweight factory: creates and caches shared sprite data."""

    _sprites = {}
    _stats = {"hits": 0, "misses": 0}

    @classmethod
    def get_sprite(cls, entity_type, texture_size_kb=512,
                   animation_frames=None):
        if entity_type in cls._sprites:
            cls._stats["hits"] += 1
            return cls._sprites[entity_type]

        if animation_frames is None:
            animation_frames = ["idle_0", "idle_1", "idle_2"]

        cls._stats["misses"] += 1
        sprite = SpriteData(entity_type, texture_size_kb,
                            animation_frames)
        cls._sprites[entity_type] = sprite
        return sprite

    @classmethod
    def get_stats(cls):
        total = cls._stats["hits"] + cls._stats["misses"]
        reuse = (cls._stats["hits"] / total * 100) if total > 0 else 0
        return {
            "unique_sprites": len(cls._sprites),
            "cache_hits": cls._stats["hits"],
            "cache_misses": cls._stats["misses"],
            "reuse_rate": f"{reuse:.1f}%"
        }


class GameEntity:
    """Context: individual entity with unique position and state."""

    def __init__(self, entity_type, x, y):
        # Extrinsic state (unique per entity)
        self.x = x
        self.y = y
        self.health = 100
        self.current_frame = 0

        # Intrinsic state (shared via flyweight)
        self.sprite = SpriteFactory.get_sprite(entity_type)

    def update(self):
        self.current_frame += 1

    def render(self):
        frame = self.sprite.get_frame(self.current_frame)
        return (f"{self.sprite.entity_type} at ({self.x},{self.y}) "
                f"frame={frame} hp={self.health}")


# Create many entities sharing few sprite types
import random

entities = []
entity_types = ["goblin", "skeleton", "orc", "bat", "spider"]

print("Creating 10,000 game entities...")
for i in range(10_000):
    etype = random.choice(entity_types)
    x = random.randint(0, 1000)
    y = random.randint(0, 1000)
    entities.append(GameEntity(etype, x, y))

# Show some entities
print("\nSample entities:")
for entity in entities[:5]:
    print(f"  {entity.render()}")

# Memory analysis
sprite_memory = sum(
    sys.getsizeof(s.texture_data)
    for s in SpriteFactory._sprites.values()
)
entity_memory = len(entities) * sys.getsizeof(entities[0])

print(f"\n=== Memory Analysis ===")
print(f"Unique sprite types: {len(SpriteFactory._sprites)}")
print(f"Shared sprite data:  {sprite_memory / 1024:.0f} KB")
print(f"Entity references:   {entity_memory / 1024:.0f} KB")
print(f"Total with sharing:  {(sprite_memory + entity_memory) / 1024:.0f} KB")

without_sharing = len(entities) * (512 * 1024)  # each with own texture
print(f"Without sharing:     {without_sharing / 1024 / 1024:.0f} MB")
print(f"Memory saved:        {(1 - (sprite_memory + entity_memory) / without_sharing) * 100:.1f}%")

print(f"\nFactory stats: {SpriteFactory.get_stats()}")
```

**Output:**
```
Creating 10,000 game entities...

Sample entities:
  skeleton at (423,891) frame=idle_0 hp=100
  goblin at (156,302) frame=idle_0 hp=100
  orc at (789,445) frame=idle_0 hp=100
  bat at (234,667) frame=idle_0 hp=100
  spider at (912,123) frame=idle_0 hp=100

=== Memory Analysis ===
Unique sprite types: 5
Shared sprite data:  2560 KB
Entity references:   547 KB
Total with sharing:  3107 KB
Without sharing:     5000 MB
Memory saved:        99.9%

Factory stats: {'unique_sprites': 5, 'cache_hits': 9995, 'cache_misses': 5, 'reuse_rate': '99.9%'}
```

Instead of 5GB of texture data (10,000 entities x 512KB each), we use only 2.5MB (5
unique textures). That is a 99.9% reduction.

---

## Real-World Use Case: Text Formatting

```python
class CharacterFormat:
    """Flyweight: shared text formatting."""

    def __init__(self, font, size, color, bold, italic):
        self.font = font
        self.size = size
        self.color = color
        self.bold = bold
        self.italic = italic

    def __repr__(self):
        style = ""
        if self.bold:
            style += "B"
        if self.italic:
            style += "I"
        return f"[{self.font} {self.size}pt {self.color} {style}]"


class FormatFactory:
    """Flyweight factory for text formats."""

    _cache = {}

    @classmethod
    def get_format(cls, font="Arial", size=12, color="black",
                   bold=False, italic=False):
        key = (font, size, color, bold, italic)
        if key not in cls._cache:
            cls._cache[key] = CharacterFormat(
                font, size, color, bold, italic)
        return cls._cache[key]

    @classmethod
    def format_count(cls):
        return len(cls._cache)


class FormattedChar:
    """Context: one character with its format and position."""

    def __init__(self, char, row, col, fmt):
        self.char = char        # extrinsic
        self.row = row          # extrinsic
        self.col = col          # extrinsic
        self.format = fmt       # intrinsic (shared flyweight)


class Document:
    def __init__(self):
        self.characters = []

    def add_text(self, text, row, start_col, **fmt_kwargs):
        fmt = FormatFactory.get_format(**fmt_kwargs)
        for i, char in enumerate(text):
            self.characters.append(
                FormattedChar(char, row, start_col + i, fmt))

    def render(self):
        current_fmt = None
        output = []
        for ch in self.characters:
            if ch.format != current_fmt:
                current_fmt = ch.format
                output.append(f"\n  {current_fmt}: ")
            output.append(ch.char)
        return "".join(output)


# Build a document
doc = Document()
doc.add_text("Hello World", row=0, start_col=0,
             font="Arial", size=24, bold=True)
doc.add_text("This is normal text. ", row=1, start_col=0)
doc.add_text("This is italic.", row=1, start_col=21,
             italic=True)
doc.add_text("Back to normal text again.", row=2, start_col=0)

print("=== Document ===")
print(doc.render())
print(f"\nTotal characters: {len(doc.characters)}")
print(f"Unique formats:   {FormatFactory.format_count()}")
print(f"Formats shared across {len(doc.characters)} characters")
```

**Output:**
```
=== Document ===
  [Arial 24pt black B]: Hello World
  [Arial 12pt black ]: This is normal text.
  [Arial 12pt black I]: This is italic.
  [Arial 12pt black ]: Back to normal text again.

Total characters: 72
Unique formats:   3
Formats shared across 72 characters
```

72 characters share only 3 format objects. In a real document with thousands of
characters, this saving becomes significant.

---

## Before vs After Comparison

### Before: Every Object Owns Its Data

```python
class TreeWithoutFlyweight:
    def __init__(self, species, x, y, texture_path):
        self.species = species
        self.x = x
        self.y = y
        # Each tree loads its own copy of the texture
        self.texture = load_texture(texture_path)  # 2MB each!
        self.mesh = load_mesh(species)              # 1MB each!

# 10,000 oak trees = 10,000 * 3MB = 30GB
trees = [TreeWithoutFlyweight("oak", i, i, "oak.png")
         for i in range(10_000)]
```

### After: Shared Intrinsic State

```python
class TreeType:  # Flyweight
    def __init__(self, species, texture_path):
        self.species = species
        self.texture = load_texture(texture_path)  # 2MB, loaded ONCE
        self.mesh = load_mesh(species)              # 1MB, loaded ONCE

class Tree:  # Context
    def __init__(self, tree_type, x, y):
        self.type = tree_type  # reference to shared flyweight
        self.x = x             # unique per tree
        self.y = y             # unique per tree

# 5 tree types * 3MB = 15MB shared data
# 10,000 trees * ~32 bytes = ~312KB for positions
# Total: ~15.3MB instead of 30GB
```

---

## When Memory Matters

Flyweight is worth the complexity only when:

```
+-------------------------------------------------------------------+
| Memory savings = (N - U) * S                                      |
|                                                                   |
| N = number of objects                                             |
| U = number of unique intrinsic state combinations                 |
| S = size of intrinsic state per object                            |
|                                                                   |
| Example:                                                          |
| 10,000 trees - 5 types = 9,995 duplicates avoided                |
| 9,995 * 3MB = ~29.9 GB saved                                     |
+-------------------------------------------------------------------+
```

**Flyweight is worth it when:**
- N is very large (thousands or millions of objects)
- U is much smaller than N (few unique types)
- S is significant (kilobytes or more per shared state)

**Flyweight is NOT worth it when:**
- N is small (hundreds or fewer)
- Every object is unique (U equals N)
- S is tiny (a few bytes)
- The complexity of managing shared state outweighs memory savings

---

## When to Use / When NOT to Use

### Use Flyweight When

- Your application creates huge numbers of similar objects
- Memory consumption is a real, measured problem
- Objects can be split into shared (intrinsic) and unique (extrinsic) state
- The intrinsic state is large relative to the extrinsic state
- Most objects share a small number of distinct intrinsic state combinations
- Examples: game sprites, text formatting, connection pools, cached configs

### Do NOT Use Flyweight When

- You have few objects (premature optimization)
- Memory is not a bottleneck (profile first, optimize second)
- Objects cannot be meaningfully split into shared/unique state
- The shared state is mutable (flyweights must be immutable)
- Thread safety of shared state is too complex for your use case
- The indirection makes code significantly harder to understand

---

## Common Mistakes

### Mistake 1: Mutable Flyweights

```python
# WRONG: flyweight state can be changed
class SpriteData:
    def __init__(self, entity_type):
        self.entity_type = entity_type
        self.color = "red"  # mutable!

sprite = SpriteFactory.get("goblin")
sprite.color = "blue"  # Changes it for ALL goblins!

# RIGHT: flyweights must be immutable
class SpriteData:
    def __init__(self, entity_type, color):
        self._entity_type = entity_type
        self._color = color

    @property
    def entity_type(self):
        return self._entity_type

    @property
    def color(self):
        return self._color
```

### Mistake 2: Putting Extrinsic State in the Flyweight

```java
// WRONG: position is unique per entity, not shared
public class TreeType {
    String species;
    byte[] texture;
    int x, y;  // This should NOT be here!
}

// RIGHT: only shared data in the flyweight
public class TreeType {
    final String species;
    final byte[] texture;
    // x, y stays in the Tree context object
}
```

### Mistake 3: No Factory Control

```python
# WRONG: creating flyweights directly
sprite1 = SpriteData("goblin", 512, ["idle"])
sprite2 = SpriteData("goblin", 512, ["idle"])
# sprite1 is not sprite2 -- no sharing!

# RIGHT: always go through the factory
sprite1 = SpriteFactory.get_sprite("goblin")
sprite2 = SpriteFactory.get_sprite("goblin")
# sprite1 is sprite2 -- same object, shared
```

---

## Best Practices

1. **Make flyweights immutable.** Since they are shared, any mutation affects all users.
   Use final fields in Java, properties in Python, and no setters.

2. **Always use a factory.** Direct construction bypasses the cache and defeats the
   pattern. Make the flyweight constructor private or protected.

3. **Profile before applying.** Flyweight adds indirection. Only use it when you have
   measured that memory is actually a problem. Do not guess.

4. **Clearly separate intrinsic and extrinsic state.** Document which fields are shared
   and which are unique. This is the core design decision of Flyweight.

5. **Consider thread safety.** Since flyweights are shared across threads, they must
   be thread-safe. Immutability is the easiest way to achieve this.

6. **Use identity comparison for cache hits.** After getting a flyweight from the
   factory, you can use `==` (Java) or `is` (Python) to check if two objects share
   the same flyweight.

7. **Combine with other patterns.** Flyweight often works with Composite (shared leaf
   data in trees) and Factory Method (the flyweight factory).

---

## Quick Summary

The Flyweight pattern reduces memory by sharing common (intrinsic) state across many
objects while keeping unique (extrinsic) state external. A factory ensures that shared
objects are created once and reused. The pattern is essential when creating thousands or
millions of similar objects where most of the data is identical.

```
Problem:  Thousands of objects duplicate the same large data.
Solution: Extract shared data into flyweight objects, referenced by many.
Key:      Intrinsic state is shared and immutable.
          Extrinsic state is unique and stored externally.
```

---

## Key Points

- **Flyweight** shares intrinsic (common, immutable) state to reduce memory
- **Intrinsic state** is stored inside the flyweight; **extrinsic state** stays with the
  context object
- A **Flyweight Factory** creates and caches flyweight instances
- Flyweights must be **immutable** because they are shared
- The pattern saves memory when N objects share U << N distinct states of size S
- Always **profile first** -- only apply Flyweight when memory is a measured problem
- Common examples: game sprites, text formatting, connection pools, icon caches
- Java's `String.intern()` and `Integer.valueOf()` (for -128 to 127) are built-in
  flyweight implementations

---

## Practice Questions

1. Explain the difference between intrinsic and extrinsic state. For a "Button" UI
   component used across 500 forms, what would be intrinsic and what would be extrinsic?

2. Why must flyweight objects be immutable? What bug would occur if a flyweight's
   intrinsic state were mutable?

3. Java caches Integer objects for values -128 to 127. Explain why this is an example
   of the Flyweight pattern and what the intrinsic/extrinsic states are.

4. When would applying Flyweight actually make performance worse? Describe a scenario
   where the overhead of the factory and lookups exceeds the memory savings.

5. How does Flyweight differ from a simple cache? What is the key distinction?

---

## Exercises

### Exercise 1: Icon Cache System

Build an icon management system for a dashboard:

- An `Icon` flyweight class with: name, SVG path data (simulate with a large string),
  default size, and color
- An `IconFactory` that caches icons by name
- An `IconInstance` context with position (x, y), actual size, and rotation
- Create 1,000 icon instances from 10 unique icons
- Measure and print memory usage with and without sharing

### Exercise 2: Map Tile System

Implement a game map with shared tiles:

- A `TileType` flyweight with: terrain name, movement cost, texture data (simulated),
  and walkable flag
- A `MapTile` context with: row, column, elevation, and damage modifier
- A `TileFactory` that manages the shared tile types
- Create a 100x100 grid (10,000 tiles) using only 6 terrain types
- Implement `render_map()` that prints a small section using terrain abbreviations

### Exercise 3: Log Entry Formatter

Build a logging system that shares format templates:

- A `LogFormat` flyweight with: pattern string, date format, separator, and colors
- A `LogEntry` context with: message, timestamp, level, and source
- A `LogFormatFactory` with preset formats: "simple", "detailed", "json", "csv"
- Generate 10,000 log entries across 4 format types
- Compare memory usage: each entry owning its format vs sharing via flyweight

---

## What Is Next?

Having learned how to reduce memory with shared state, the next chapter explores the
**Proxy Pattern**, which controls access to objects. Where Flyweight optimizes resource
usage by sharing data, Proxy optimizes resource usage by deferring creation, caching
results, or restricting access. Both patterns put a layer between the client and the
real object, but for very different reasons.
