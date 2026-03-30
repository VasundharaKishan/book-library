# Chapter 21: Second-Level Cache and Query Cache

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the difference between first-level and second-level cache
- Know when second-level caching improves performance
- Configure a second-level cache provider (Caffeine/Ehcache) with Spring Boot
- Mark entities as cacheable with @Cacheable and @Cache
- Choose the right cache concurrency strategy (READ_ONLY, READ_WRITE, etc.)
- Enable and use the query cache for repeated queries
- Monitor cache hit rates and performance
- Know when caching hurts more than it helps
- Invalidate and manage cache entries

---

## First-Level Cache Recap

The first-level cache is the persistence context you learned about in Chapter 17. It exists within a single transaction.

```
First-Level Cache (Persistence Context):
+------------------------------------------------------------------+
|                                                                   |
|  Scope: One transaction (one @Transactional method)               |
|                                                                   |
|  Transaction A:                    Transaction B:                  |
|  +----------------------+         +----------------------+        |
|  | find(Employee, 1)    |         | find(Employee, 1)    |        |
|  | --> SQL SELECT       |         | --> SQL SELECT       |        |
|  | find(Employee, 1)    |         | (separate query!)    |        |
|  | --> FROM CACHE       |         |                      |        |
|  | (no SQL, same Tx)    |         |                      |        |
|  +----------------------+         +----------------------+        |
|                                                                   |
|  Limitation: Cache is NOT shared between transactions.            |
|  Every new transaction starts with an empty cache.                |
|  find(Employee, 1) in Tx B hits the DB again.                    |
+------------------------------------------------------------------+
```

---

## Second-Level Cache (L2 Cache)

The second-level cache is a **shared cache** that lives across transactions. When an entity is loaded, it is stored in the L2 cache. Future transactions can retrieve it without hitting the database.

```
L2 Cache Architecture:
+------------------------------------------------------------------+
|                                                                   |
|  Transaction A           Transaction B           Transaction C    |
|  +-----------+           +-----------+           +-----------+    |
|  | L1 Cache  |           | L1 Cache  |           | L1 Cache  |    |
|  |(per-Tx)   |           |(per-Tx)   |           |(per-Tx)   |    |
|  +-----------+           +-----------+           +-----------+    |
|       |                       |                       |           |
|       v                       v                       v           |
|  +-----------------------------------------------------------+   |
|  |              Second-Level Cache (L2)                       |   |
|  |              Shared across all transactions                |   |
|  |                                                           |   |
|  |  (Employee, 1) -> {name="Alice", salary=80000}            |   |
|  |  (Employee, 2) -> {name="Bob", salary=75000}              |   |
|  |  (Department, 10) -> {name="Engineering"}                  |   |
|  +-----------------------------------------------------------+   |
|       |                                                           |
|       v  (only on cache MISS)                                     |
|  +-----------------------------------------------------------+   |
|  |                     Database                               |   |
|  +-----------------------------------------------------------+   |
|                                                                   |
|  Flow for find(Employee, 1):                                      |
|  1. Check L1 (persistence context) --> miss                      |
|  2. Check L2 (shared cache) --> HIT! Return cached data          |
|  3. If L2 miss --> query database, store in L1 AND L2            |
+------------------------------------------------------------------+
```

### What Gets Cached

```
L2 Cache Stores DEHYDRATED Data:
+------------------------------------------------------------------+
|                                                                   |
|  The L2 cache does NOT store Java objects.                        |
|  It stores disassembled (dehydrated) state:                      |
|                                                                   |
|  Cache Key: (com.example.Employee, 1)                             |
|  Cache Value: {                                                   |
|    "name" -> "Alice",                                             |
|    "email" -> "alice@co.com",                                     |
|    "salary" -> 80000,                                             |
|    "department_id" -> 10    // FK value, not the Department object |
|  }                                                                |
|                                                                   |
|  When retrieved from L2:                                          |
|  1. Hibernate reads the dehydrated data                           |
|  2. Creates a new Employee object                                 |
|  3. Populates the fields                                          |
|  4. Puts it in the L1 cache (persistence context)                |
|  5. Returns the entity                                            |
|                                                                   |
|  Note: The department (FK) is not automatically loaded.           |
|  It may trigger another cache lookup or DB query.                 |
+------------------------------------------------------------------+
```

---

## Setting Up L2 Cache with Spring Boot

### Step 1: Add Dependencies

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>

<!-- Caffeine (recommended for single-server apps) -->
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>

<!-- Hibernate JCache integration -->
<dependency>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-jcache</artifactId>
</dependency>
```

### Step 2: Configure Hibernate Properties

```properties
# application.properties

# Enable L2 cache
spring.jpa.properties.hibernate.cache.use_second_level_cache=true

# Enable query cache (optional)
spring.jpa.properties.hibernate.cache.use_query_cache=true

# Cache provider
spring.jpa.properties.hibernate.cache.region.factory_class=jcache

# Cache statistics (for monitoring)
spring.jpa.properties.hibernate.generate_statistics=true

# JCache provider
spring.cache.jcache.config=classpath:ehcache.xml
```

### Step 3: Mark Entities as Cacheable

```java
@Entity
@Table(name = "departments")
@Cacheable                                          // JPA standard
@org.hibernate.annotations.Cache(
    usage = CacheConcurrencyStrategy.READ_WRITE     // Hibernate-specific
)
public class Department {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @OneToMany(mappedBy = "department")
    @org.hibernate.annotations.Cache(
        usage = CacheConcurrencyStrategy.READ_WRITE  // Cache the collection too
    )
    private List<Employee> employees = new ArrayList<>();

    // ...
}
```

```
Caching Annotations:
+------------------------------------------------------------------+
|                                                                   |
|  @Cacheable (JPA standard, jakarta.persistence)                   |
|  - Marks entity as eligible for L2 caching                        |
|  - Simple on/off flag                                             |
|  - No cache strategy control                                      |
|                                                                   |
|  @Cache (Hibernate-specific, org.hibernate.annotations)           |
|  - Defines the caching STRATEGY                                   |
|  - Controls concurrency behavior                                  |
|  - Can be applied to entities AND collections                     |
|                                                                   |
|  You typically use BOTH:                                          |
|  @Cacheable           --> "This entity can be cached"             |
|  @Cache(usage = ...)  --> "Cache it with this strategy"           |
+------------------------------------------------------------------+
```

---

## Cache Concurrency Strategies

The strategy controls how the cache handles concurrent reads and writes:

```
Cache Concurrency Strategies:
+------------------------------------------------------------------+
|                                                                   |
|  READ_ONLY:                                                       |
|  - Entity is never modified after creation                        |
|  - Fastest (no locking, no invalidation)                          |
|  - Throws exception if you try to update a cached entity          |
|  - Use for: lookup tables, enums, static reference data           |
|  Example: Country, Currency, Status codes                         |
|                                                                   |
|  NONSTRICT_READ_WRITE:                                            |
|  - Entity is rarely modified                                      |
|  - No locking — brief window of stale data after update           |
|  - Good performance, slightly inconsistent during writes          |
|  - Use for: data that changes rarely, staleness is acceptable     |
|  Example: Product catalog, user profiles                          |
|                                                                   |
|  READ_WRITE:                                                      |
|  - Entity is read and written frequently                          |
|  - Uses soft locks to prevent stale reads during updates          |
|  - Good balance of consistency and performance                    |
|  - Use for: most business entities                                |
|  Example: Orders, accounts, inventory                             |
|                                                                   |
|  TRANSACTIONAL:                                                   |
|  - Full transaction isolation in the cache                        |
|  - Requires a JTA transaction manager                             |
|  - Highest consistency, lowest performance                        |
|  - Rarely needed in Spring Boot applications                     |
+------------------------------------------------------------------+
```

```
Choosing a Strategy:
+------------------------------------------------------------------+
|                                                                   |
|  Is the data immutable (never updated)?                           |
|      |                                                            |
|   YES --> READ_ONLY (fastest, safest)                             |
|      |                                                            |
|    NO                                                             |
|      |                                                            |
|  Is brief staleness acceptable?                                   |
|  (user sees old data for a few ms during updates)                 |
|      |                                                            |
|   YES --> NONSTRICT_READ_WRITE (fast, simple)                     |
|      |                                                            |
|    NO --> READ_WRITE (consistent, slightly slower)                |
+------------------------------------------------------------------+
```

---

## Practical Examples

### Read-Only Cache: Country Lookup

```java
@Entity
@Table(name = "countries")
@Cacheable
@org.hibernate.annotations.Cache(usage = CacheConcurrencyStrategy.READ_ONLY)
public class Country {

    @Id
    private String code;   // "US", "GB", "FR"

    @Column(nullable = false)
    private String name;   // "United States", "United Kingdom"

    // Constructor, getters (no setters — immutable)
}
```

```java
// First call: database query, stored in L2 cache
Country us = countryRepository.findById("US").orElseThrow();
// SQL: SELECT * FROM countries WHERE code = 'US'

// Second call (same or different transaction): L2 cache hit!
Country usAgain = countryRepository.findById("US").orElseThrow();
// No SQL! Served from L2 cache.

// 1000th call: still from cache, zero DB queries
```

### Read-Write Cache: Product

```java
@Entity
@Table(name = "products")
@Cacheable
@org.hibernate.annotations.Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private BigDecimal price;

    private boolean active;

    // Getters, setters...
}
```

```
Read-Write Cache Flow:
+------------------------------------------------------------------+
|                                                                   |
|  Read:                                                            |
|  find(Product, 1) --> L1 miss --> L2 HIT --> return from cache   |
|                       (no database query)                         |
|                                                                   |
|  Write:                                                           |
|  product.setPrice(newPrice);                                      |
|  On flush/commit:                                                 |
|  1. UPDATE products SET price = ? WHERE id = 1  (DB updated)     |
|  2. L2 cache entry for (Product, 1) is invalidated               |
|  3. Next read will query DB and repopulate cache                  |
|                                                                   |
|  Soft Lock during update:                                         |
|  1. Before UPDATE: L2 entry is "soft-locked"                     |
|  2. Other transactions reading (Product, 1) see the lock         |
|     and go directly to the database (avoid stale read)           |
|  3. After COMMIT: lock released, cache updated                    |
+------------------------------------------------------------------+
```

### Caching Collections

```java
@Entity
@Cacheable
@org.hibernate.annotations.Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Department {

    @OneToMany(mappedBy = "department")
    @org.hibernate.annotations.Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
    private List<Employee> employees = new ArrayList<>();
}
```

```
Collection Cache:
+------------------------------------------------------------------+
|                                                                   |
|  The collection cache stores the LIST OF IDs, not entity data:   |
|                                                                   |
|  Cache Region: "com.example.Department.employees"                 |
|  Cache Key: Department id = 10                                    |
|  Cache Value: [1, 2, 3, 5, 8]  (employee IDs only)              |
|                                                                   |
|  When loading department.getEmployees():                          |
|  1. Look up collection cache for Department 10 --> [1,2,3,5,8]   |
|  2. For each ID, look up entity cache for Employee                |
|     Employee 1 --> L2 HIT (cached entity data)                   |
|     Employee 2 --> L2 HIT                                        |
|     Employee 3 --> L2 MISS --> DB query, then cache it            |
|     ...                                                           |
|                                                                   |
|  Collection cache + entity cache work TOGETHER.                   |
|  If employees are also @Cacheable, most lookups are cache hits.  |
+------------------------------------------------------------------+
```

---

## Query Cache

The query cache stores **query results** (lists of entity IDs) keyed by the query string and parameters:

```properties
# Enable query cache
spring.jpa.properties.hibernate.cache.use_query_cache=true
```

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Enable query cache for this specific query
    @QueryHints(@QueryHint(name = "org.hibernate.cacheable", value = "true"))
    List<Product> findByActiveTrue();

    @QueryHints(@QueryHint(name = "org.hibernate.cacheable", value = "true"))
    @Query("SELECT p FROM Product p WHERE p.price < :max AND p.active = true")
    List<Product> findAffordableProducts(@Param("max") BigDecimal max);
}
```

```
Query Cache Behavior:
+------------------------------------------------------------------+
|                                                                   |
|  First call: findByActiveTrue()                                   |
|  1. Query cache MISS (never executed before)                      |
|  2. Execute SQL: SELECT * FROM products WHERE active = true       |
|  3. Store in query cache:                                         |
|     Key: "findByActiveTrue" + params                              |
|     Value: [1, 3, 5, 7, 9]  (list of product IDs)               |
|  4. Store each product in entity L2 cache                        |
|                                                                   |
|  Second call: findByActiveTrue()                                  |
|  1. Query cache HIT! Returns [1, 3, 5, 7, 9]                    |
|  2. Look up each ID in entity L2 cache                           |
|  3. No SQL at all!                                                |
|                                                                   |
|  INVALIDATION:                                                    |
|  Any INSERT, UPDATE, or DELETE on the products table              |
|  invalidates ALL query cache entries for products.                |
|  This is aggressive — even updating product 99 invalidates       |
|  the cache for findByActiveTrue.                                  |
+------------------------------------------------------------------+
```

### When Query Cache Helps vs Hurts

```
Query Cache Decision:
+------------------------------------------------------------------+
|                                                                   |
|  Query cache HELPS when:                                          |
|  - The SAME query is executed frequently                          |
|  - The underlying data RARELY changes                             |
|  - The result set is small                                        |
|  Examples:                                                        |
|  - findAllActiveCountries() (changes yearly)                      |
|  - findAllRoles() (changes rarely)                                |
|  - findProductsByCategory("popular") (changes daily)              |
|                                                                   |
|  Query cache HURTS when:                                          |
|  - The table is updated frequently                                |
|  - Queries have many different parameter combinations             |
|  - Result sets are large                                          |
|  Examples:                                                        |
|  - findByUserId(userId) (thousands of unique IDs)                |
|  - Real-time data (prices, stock levels, chat messages)           |
|  - Tables with frequent writes (audit logs, events)              |
|                                                                   |
|  Rule of thumb: Query cache is most useful for                    |
|  "read-mostly, shared-across-users" data.                        |
+------------------------------------------------------------------+
```

---

## Monitoring Cache Performance

### Hibernate Statistics

```java
@RestController
@RequestMapping("/api/admin/cache")
public class CacheMonitorController {

    @Autowired
    private EntityManagerFactory emf;

    @GetMapping("/stats")
    public Map<String, Object> getCacheStats() {
        Statistics stats = emf.unwrap(SessionFactory.class).getStatistics();

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("L2 cache hits", stats.getSecondLevelCacheHitCount());
        result.put("L2 cache misses", stats.getSecondLevelCacheMissCount());
        result.put("L2 cache puts", stats.getSecondLevelCachePutCount());
        result.put("Query cache hits", stats.getQueryCacheHitCount());
        result.put("Query cache misses", stats.getQueryCacheMissCount());

        long hits = stats.getSecondLevelCacheHitCount();
        long misses = stats.getSecondLevelCacheMissCount();
        double hitRate = (hits + misses) > 0
            ? (double) hits / (hits + misses) * 100 : 0;
        result.put("L2 hit rate", String.format("%.1f%%", hitRate));

        return result;
    }
}
```

```
Good Cache Hit Rates:
+------------------------------------------------------------------+
|                                                                   |
|  Hit Rate          Assessment                                     |
|  ----------------------------------------------------------------|
|  > 90%             Excellent — cache is highly effective          |
|  70-90%            Good — working well for most reads             |
|  50-70%            Moderate — review if entities change too often |
|  < 50%             Poor — cache may not be worth the overhead     |
|                    Consider removing caching for this entity      |
|                                                                   |
|  If hit rate is low, possible causes:                             |
|  - Entity is updated too frequently (invalidates cache)           |
|  - Cache size too small (entries evicted prematurely)             |
|  - Entities loaded by different access patterns (IDs vs queries)  |
+------------------------------------------------------------------+
```

---

## When NOT to Cache

```
Do NOT Cache:
+------------------------------------------------------------------+
|                                                                   |
|  1. Frequently updated entities                                   |
|     - Cache is invalidated on every update                        |
|     - High invalidation rate = low hit rate = wasted memory       |
|     - Example: real-time stock prices, live chat messages         |
|                                                                   |
|  2. Entities with large data                                      |
|     - LOBs, large text fields, binary data                        |
|     - Consumes too much cache memory                              |
|     - Better to query on demand                                   |
|                                                                   |
|  3. Security-sensitive data                                       |
|     - User sessions, tokens, permissions that change frequently   |
|     - Stale cache = security vulnerability                        |
|                                                                   |
|  4. Data that must always be fresh                                |
|     - Inventory counts (must be real-time for ordering)           |
|     - Account balances (stale balance = wrong transaction)        |
|                                                                   |
|  5. Entities only loaded once (unique access patterns)            |
|     - Each entity loaded by a different user, never reused        |
|     - Cache fills up with never-reaccessed entries                |
|                                                                   |
|  DO Cache:                                                        |
|  - Reference data (countries, currencies, categories)             |
|  - Configuration (settings, feature flags)                        |
|  - Slowly changing data (product catalog, user profiles)          |
|  - Frequently read, shared across users                           |
+------------------------------------------------------------------+
```

---

## Cache Configuration with Caffeine

```java
@Configuration
public class CacheConfig {

    @Bean
    public HibernatePropertiesCustomizer hibernateSecondLevelCacheCustomizer() {
        return properties -> {
            properties.put("hibernate.cache.use_second_level_cache", "true");
            properties.put("hibernate.cache.use_query_cache", "true");
            properties.put("hibernate.cache.region.factory_class",
                "org.hibernate.cache.jcache.internal.JCacheRegionFactory");
            properties.put("hibernate.javax.cache.provider",
                "com.github.benmanes.caffeine.jcache.spi.CaffeineCachingProvider");
        };
    }
}
```

Or use Ehcache with an XML configuration:

```xml
<!-- src/main/resources/ehcache.xml -->
<config xmlns='http://www.ehcache.org/v3'>

    <!-- Default cache template -->
    <cache-template name="default">
        <expiry>
            <ttl unit="minutes">60</ttl>
        </expiry>
        <heap unit="entries">1000</heap>
    </cache-template>

    <!-- Entity-specific cache -->
    <cache alias="com.example.entity.Product" uses-template="default">
        <heap unit="entries">5000</heap>
    </cache>

    <!-- Collection cache -->
    <cache alias="com.example.entity.Department.employees" uses-template="default">
        <heap unit="entries">500</heap>
    </cache>

    <!-- Query cache region -->
    <cache alias="default-query-results-region" uses-template="default">
        <expiry>
            <ttl unit="minutes">5</ttl>
        </expiry>
    </cache>

</config>
```

---

## Common Mistakes

1. **Caching entities that change frequently**: If an entity is updated every few seconds, the cache is constantly invalidated. Hit rate drops below 50%, and you pay the overhead of caching without the benefit.

2. **Enabling query cache without entity cache**: The query cache stores entity IDs. If those entities are not in the L2 entity cache, each ID triggers a database lookup — potentially worse than no caching.

3. **Caching without monitoring**: Without statistics, you cannot tell if caching is helping. Enable `hibernate.generate_statistics=true` and monitor hit rates.

4. **Using READ_ONLY for mutable entities**: `READ_ONLY` throws an exception on update. If the entity might ever be modified, use `NONSTRICT_READ_WRITE` or `READ_WRITE`.

5. **Expecting the L2 cache to work with JPQL queries**: `find()` by ID uses L2 cache. JPQL queries go to the database by default. You need the query cache (with `@QueryHint`) for JPQL result caching.

6. **Not configuring cache sizes**: Without size limits, caches grow unbounded. Always set maximum entry counts and TTL (time-to-live) for eviction.

---

## Best Practices

1. **Start without caching, add when needed**: Premature caching adds complexity. Profile first, identify hot spots, then cache strategically.

2. **Cache reference data first**: Countries, currencies, categories, roles — these change rarely and are read constantly. Best ROI for caching.

3. **Always monitor cache statistics**: Track hit rates, miss rates, and eviction counts. Remove caching for entities with low hit rates.

4. **Set appropriate TTLs**: Reference data can cache for hours. Business data should cache for minutes. No cache should live forever without validation.

5. **Cache both entities AND collections**: If you cache a Department, also cache its employees collection. Otherwise, accessing employees still hits the database.

6. **Use the query cache sparingly**: Only for frequently repeated queries on stable data. The aggressive invalidation (any table change clears all query caches for that table) makes it counterproductive for volatile data.

---

## Summary

- **First-level cache** (persistence context) exists per transaction. Same entity ID returns the same object within a transaction.

- **Second-level cache** is shared across transactions. Stores dehydrated entity state. Reduces database queries for frequently read entities.

- **Cache concurrency strategies**: `READ_ONLY` for immutable data, `NONSTRICT_READ_WRITE` for rarely changed data, `READ_WRITE` for general use.

- **Query cache** stores query results (entity IDs) keyed by query + parameters. Invalidated on any table modification. Best for stable, frequently repeated queries.

- **Collection cache** stores the list of child IDs, not entity data. Works together with entity cache.

- **Monitor cache statistics** to ensure caching is actually helping. Low hit rates mean caching is adding overhead without benefit.

- **Cache reference data** (countries, roles, categories) for best ROI. Avoid caching frequently updated or security-sensitive data.

---

## Interview Questions

**Q1: What is the difference between L1 and L2 cache in Hibernate?**

L1 (first-level) cache is the persistence context — scoped to a single transaction, always on, cannot be disabled. L2 (second-level) cache is shared across transactions, optional, and requires explicit configuration. L1 stores entity objects; L2 stores dehydrated data (field values, not objects).

**Q2: What does the second-level cache store?**

Dehydrated entity state: field values and foreign key IDs, not Java objects. When retrieved from L2, Hibernate creates a new entity object, populates fields from the cached data, and places it in the L1 cache.

**Q3: When should you use READ_ONLY vs READ_WRITE cache strategy?**

`READ_ONLY` for immutable reference data that is never updated (countries, currencies). It is fastest because no locking or invalidation is needed. `READ_WRITE` for mutable business data that is both read and written. It uses soft locks to prevent stale reads during updates.

**Q4: How does the query cache work and when should you use it?**

The query cache stores the list of entity IDs returned by a query, keyed by the query string and parameters. On cache hit, it returns the IDs and looks up each entity in the L2 entity cache. It is invalidated when any row in the queried table is modified. Use it only for frequently repeated queries on stable data.

**Q5: What is a common mistake when setting up L2 caching?**

Enabling the query cache without also caching the entities. The query cache stores IDs, not data. If the entity is not in the L2 cache, each ID triggers a database SELECT — potentially slower than running the query directly.

---

## Practice Exercises

**Exercise 1: L2 Cache Setup**
Add Caffeine or Ehcache L2 cache to your project. Mark the `Country` entity as `READ_ONLY` cacheable. Load the same country by ID in two separate transactions. Verify with SQL logging that the second load has no SQL query.

**Exercise 2: Cache Statistics**
Enable Hibernate statistics. Load a cacheable entity 100 times across different service calls. Print the cache hit count, miss count, and hit rate. Verify the hit rate is close to 99%.

**Exercise 3: Query Cache**
Enable the query cache. Mark `findByActiveTrue()` as cacheable. Call it 5 times. Verify only the first call generates SQL. Then update one product and call again — verify the cache was invalidated (SQL is executed).

**Exercise 4: Collection Cache**
Cache a `Department.employees` collection. Load a department and access its employees in two transactions. Verify the second access has no SQL for the collection or the employee entities.

**Exercise 5: Cache Comparison**
Create two services: one with L2 caching enabled and one without. Load the same 100 products 10 times each. Use `System.nanoTime()` to measure the time difference. Document the performance improvement.

---

## What Is Next?

In the next chapter, we will explore **Bean Validation with Hibernate Validator** — how to declaratively validate entity data using annotations like `@NotNull`, `@Size`, `@Email`, and `@Pattern`. You will learn to create custom validators, use validation groups, and integrate validation with Spring MVC for automatic request validation.
