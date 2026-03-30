# Chapter 24: Caching

## What You Will Learn

- What caching is and why it makes applications faster.
- How to enable caching with @EnableCaching.
- How to cache method results with @Cacheable.
- How to remove cached data with @CacheEvict.
- How to update cached data with @CachePut.
- How cache keys work and how to customize them.
- How ConcurrentMapCacheManager works as the default cache provider.
- When to cache and when not to cache.
- How to build a complete product service with caching.

## Why This Chapter Matters

Imagine you work at an information desk. Someone asks "What time does the museum open?" You look it up in a binder, flip through 50 pages, and find the answer: 9 AM. Thirty seconds later, another person asks the same question. Do you flip through the binder again? Of course not. You remember the answer because you just looked it up.

That is caching. Your application remembers answers to questions it has already answered so it does not have to do the work again.

Consider a product catalog page on an e-commerce site. Every time a user visits the page, the application queries the database, builds the response, and sends it back. If 1000 users visit the same page in a minute, that is 1000 identical database queries. With caching, you query the database once, store the result in memory, and serve the next 999 requests from the cache. The response time drops from 200 milliseconds to 2 milliseconds.

---

## 24.1 What Is Caching?

**Caching** is storing frequently accessed data in a fast storage layer (usually memory) so you can retrieve it quickly instead of recalculating or re-fetching it every time.

```
+-----------------------------------------------------+
|         WITHOUT CACHING                              |
+-----------------------------------------------------+
|                                                      |
|  Request 1: GET /api/products/42                     |
|       --> Query database (200ms)                     |
|       --> Return product                             |
|                                                      |
|  Request 2: GET /api/products/42                     |
|       --> Query database (200ms)  <-- Same query!    |
|       --> Return product                             |
|                                                      |
|  Request 3: GET /api/products/42                     |
|       --> Query database (200ms)  <-- Same again!    |
|       --> Return product                             |
|                                                      |
|  Total time: 600ms for 3 identical queries           |
+-----------------------------------------------------+

+-----------------------------------------------------+
|         WITH CACHING                                 |
+-----------------------------------------------------+
|                                                      |
|  Request 1: GET /api/products/42                     |
|       --> Query database (200ms)                     |
|       --> Store in cache                             |
|       --> Return product                             |
|                                                      |
|  Request 2: GET /api/products/42                     |
|       --> Found in cache! (2ms)  <-- No database!    |
|       --> Return product                             |
|                                                      |
|  Request 3: GET /api/products/42                     |
|       --> Found in cache! (2ms)  <-- No database!    |
|       --> Return product                             |
|                                                      |
|  Total time: 204ms (100x faster for requests 2 & 3) |
+-----------------------------------------------------+
```

### The Cache Flow

```
+---------------------------------------------------+
|              CACHE LOOKUP FLOW                     |
+---------------------------------------------------+
|                                                    |
|  Method called with arguments                      |
|       |                                            |
|       v                                            |
|  [Check cache: is there a stored result            |
|   for these arguments?]                            |
|       |                                            |
|       +--> YES (cache hit)                         |
|       |    Return cached result immediately        |
|       |    Method body does NOT execute             |
|       |                                            |
|       +--> NO (cache miss)                         |
|            Execute method body                     |
|            Store result in cache                   |
|            Return result                           |
|                                                    |
+---------------------------------------------------+
```

---

## 24.2 Enabling Caching in Spring Boot

Add the caching starter to your project (it is included with spring-boot-starter-web, but you need to enable it):

```java
// src/main/java/com/example/caching/CachingApplication.java
package com.example.caching;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching  // Enables caching support
public class CachingApplication {

    public static void main(String[] args) {
        SpringApplication.run(CachingApplication.class, args);
    }
}
```

**Line-by-line explanation:**

- `@EnableCaching` -- This annotation activates Spring's caching infrastructure. Without it, all caching annotations (@Cacheable, @CacheEvict, @CachePut) are silently ignored.

By default, Spring Boot uses `ConcurrentMapCacheManager`, which stores cached data in a simple in-memory `ConcurrentHashMap`. This is perfect for development and small applications. For production, you can switch to Redis, Caffeine, or EhCache without changing your code.

---

## 24.3 @Cacheable: Caching Method Results

The `@Cacheable` annotation stores the return value of a method in the cache. The next time the method is called with the same arguments, the cached value is returned without executing the method:

```java
// src/main/java/com/example/caching/service/ProductService.java
package com.example.caching.service;

import com.example.caching.entity.Product;
import com.example.caching.repository.ProductRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class ProductService {

    private static final Logger log =
        LoggerFactory.getLogger(ProductService.class);

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    @Cacheable("products")
    public Product getProductById(Long id) {
        log.info("Fetching product {} from database", id);
        simulateSlowQuery();  // Simulate slow database query

        return productRepository.findById(id)
            .orElseThrow(() -> new RuntimeException(
                "Product not found: " + id));
    }

    private void simulateSlowQuery() {
        try {
            Thread.sleep(2000);  // Simulate 2 second delay
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

**Line-by-line explanation:**

- `@Cacheable("products")` -- The string "products" is the **cache name**. Think of it as a named container. All products are stored in the "products" cache. You can have different caches for different types of data (like "products", "users", "orders").
- The first time `getProductById(42)` is called, the method executes, queries the database, and the result is stored in the cache with key `42`.
- The second time `getProductById(42)` is called, Spring finds the result in the cache and returns it immediately. The method body never executes. You will not see the log message.

### Testing the Cache

```bash
# First call - takes ~2 seconds (database query)
curl http://localhost:8080/api/products/1
# Log: "Fetching product 1 from database"

# Second call - instant (from cache)
curl http://localhost:8080/api/products/1
# No log message! Method body did not execute.

# Different product - takes ~2 seconds (not in cache yet)
curl http://localhost:8080/api/products/2
# Log: "Fetching product 2 from database"
```

---

## 24.4 Understanding Cache Keys

By default, Spring uses the method arguments as the cache key. Here is how it works:

```
+---------------------------------------------------+
|           CACHE KEY MAPPING                        |
+---------------------------------------------------+
|                                                    |
|  Cache name: "products"                            |
|                                                    |
|  Key       | Value                                 |
|  ----------|--------------------------------------  |
|  1         | Product{id=1, name="Widget", ...}     |
|  2         | Product{id=2, name="Gadget", ...}     |
|  42        | Product{id=42, name="Doohickey", ...} |
|                                                    |
|  getProductById(1)  --> uses key 1                 |
|  getProductById(2)  --> uses key 2                 |
|  getProductById(42) --> uses key 42                |
|                                                    |
+---------------------------------------------------+
```

### Multiple Arguments as Key

When a method has multiple arguments, all arguments form the key:

```java
@Cacheable("products")
public List<Product> searchProducts(String category, double maxPrice) {
    // Key is the combination of category AND maxPrice
    // searchProducts("electronics", 100.0) has a different key than
    // searchProducts("electronics", 200.0)
    return productRepository.findByCategoryAndPriceLessThan(
        category, maxPrice);
}
```

### Custom Cache Keys

You can specify which arguments to use as the key:

```java
// Use only the first argument as the key
@Cacheable(value = "products", key = "#category")
public List<Product> getByCategory(String category, int page) {
    return productRepository.findByCategory(category);
}

// Use a combination of arguments
@Cacheable(value = "products", key = "#category + '-' + #maxPrice")
public List<Product> searchProducts(String category, double maxPrice) {
    return productRepository.findByCategoryAndPriceLessThan(
        category, maxPrice);
}

// Use the object's property as the key
@Cacheable(value = "products", key = "#product.id")
public Product updateProduct(Product product) {
    return productRepository.save(product);
}
```

The `key` attribute uses **Spring Expression Language (SpEL)**. The `#` prefix refers to method parameters.

---

## 24.5 @CacheEvict: Removing Cached Data

When data changes (update, delete), you need to remove the stale cached data. Otherwise, users will get outdated information:

```java
@Service
public class ProductService {

    private static final Logger log =
        LoggerFactory.getLogger(ProductService.class);

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    @Cacheable("products")
    public Product getProductById(Long id) {
        log.info("Fetching product {} from database", id);
        return productRepository.findById(id)
            .orElseThrow(() -> new RuntimeException(
                "Product not found: " + id));
    }

    @CacheEvict(value = "products", key = "#id")
    public void deleteProduct(Long id) {
        log.info("Deleting product {} and evicting from cache", id);
        productRepository.deleteById(id);
    }

    @CacheEvict(value = "products", allEntries = true)
    public void clearProductCache() {
        log.info("All product cache entries cleared");
    }
}
```

**Line-by-line explanation:**

- `@CacheEvict(value = "products", key = "#id")` -- When this method runs, it removes the entry with the given key from the "products" cache. After deleting product 42 from the database, the cached copy is also removed.
- `@CacheEvict(value = "products", allEntries = true)` -- Removes ALL entries from the "products" cache. Use this when you need to clear the entire cache (like after a bulk import).

```
+---------------------------------------------------+
|           CACHE EVICTION FLOW                      |
+---------------------------------------------------+
|                                                    |
|  Before deleteProduct(42):                         |
|  Cache: { 1: Widget, 2: Gadget, 42: Doohickey }   |
|                                                    |
|  deleteProduct(42) runs:                           |
|    1. Delete from database                         |
|    2. @CacheEvict removes key 42 from cache        |
|                                                    |
|  After deleteProduct(42):                          |
|  Cache: { 1: Widget, 2: Gadget }                   |
|                                                    |
|  Next call to getProductById(42):                  |
|    Cache miss --> Query database --> Not found      |
|                                                    |
+---------------------------------------------------+
```

---

## 24.6 @CachePut: Updating the Cache

`@CachePut` always executes the method and updates the cache with the result. Unlike `@Cacheable` (which skips the method if a cached value exists), `@CachePut` always runs the method:

```java
@CachePut(value = "products", key = "#product.id")
public Product updateProduct(Product product) {
    log.info("Updating product {} and refreshing cache",
        product.getId());
    return productRepository.save(product);
}
```

**Line-by-line explanation:**

- `@CachePut(value = "products", key = "#product.id")` -- Executes the method, saves the product to the database, and stores the returned product in the cache. The next time someone calls `getProductById()` with this ID, they get the updated product from the cache.

### @Cacheable vs @CachePut vs @CacheEvict

| Annotation | Executes Method? | Updates Cache? | Use Case |
|------------|:----------------:|:--------------:|----------|
| `@Cacheable` | Only on cache miss | Yes (stores result) | Read operations |
| `@CachePut` | Always | Yes (updates result) | Update operations |
| `@CacheEvict` | Always | Yes (removes entry) | Delete operations |

```
+---------------------------------------------------+
|     COMPLETE CRUD WITH CACHING                     |
+---------------------------------------------------+
|                                                    |
|  CREATE: save(product)                             |
|    @CachePut --> Store in cache after saving        |
|                                                    |
|  READ: getProductById(42)                          |
|    @Cacheable --> Return from cache if exists       |
|                  Query database if not              |
|                                                    |
|  UPDATE: updateProduct(product)                    |
|    @CachePut --> Update cache after saving          |
|                                                    |
|  DELETE: deleteProduct(42)                         |
|    @CacheEvict --> Remove from cache after delete   |
|                                                    |
+---------------------------------------------------+
```

---

## 24.7 Complete Product Service Example

Let us build a complete service with all caching annotations:

### The Product Entity

```java
// src/main/java/com/example/caching/entity/Product.java
package com.example.caching.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private String category;
    private double price;

    public Product() {}

    public Product(String name, String category, double price) {
        this.name = name;
        this.category = category;
        this.price = price;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    @Override
    public String toString() {
        return "Product{id=" + id + ", name='" + name +
            "', category='" + category +
            "', price=" + price + "}";
    }
}
```

### The Product Repository

```java
// src/main/java/com/example/caching/repository/ProductRepository.java
package com.example.caching.repository;

import com.example.caching.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Long> {

    List<Product> findByCategory(String category);
}
```

### The Complete Cached Product Service

```java
// src/main/java/com/example/caching/service/ProductService.java
package com.example.caching.service;

import com.example.caching.entity.Product;
import com.example.caching.repository.ProductRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CachePut;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ProductService {

    private static final Logger log =
        LoggerFactory.getLogger(ProductService.class);

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    @Cacheable("products")
    public Product getProductById(Long id) {
        log.info("Cache miss - Fetching product {} from database", id);
        return productRepository.findById(id)
            .orElseThrow(() -> new RuntimeException(
                "Product not found: " + id));
    }

    @Cacheable("productsByCategory")
    public List<Product> getProductsByCategory(String category) {
        log.info("Cache miss - Fetching products in category: {}",
            category);
        return productRepository.findByCategory(category);
    }

    @CachePut(value = "products", key = "#result.id")
    public Product createProduct(Product product) {
        log.info("Creating product: {}", product.getName());
        return productRepository.save(product);
    }

    @CachePut(value = "products", key = "#product.id")
    @CacheEvict(value = "productsByCategory", allEntries = true)
    public Product updateProduct(Product product) {
        log.info("Updating product: {}", product.getId());

        if (!productRepository.existsById(product.getId())) {
            throw new RuntimeException(
                "Product not found: " + product.getId());
        }

        return productRepository.save(product);
    }

    @CacheEvict(value = {"products", "productsByCategory"},
                allEntries = true)
    public void deleteProduct(Long id) {
        log.info("Deleting product: {}", id);
        productRepository.deleteById(id);
    }
}
```

**Line-by-line explanation:**

- `@Cacheable("products")` on `getProductById` -- Caches individual products by their ID.
- `@Cacheable("productsByCategory")` on `getProductsByCategory` -- Uses a separate cache for category queries. Different data, different cache.
- `@CachePut(value = "products", key = "#result.id")` on `createProduct` -- The `#result` refers to the return value of the method. After saving, the newly created product (with its generated ID) is cached.
- `@CachePut` + `@CacheEvict` on `updateProduct` -- Updates the individual product cache AND clears the category cache (because the product's category might have changed).
- `@CacheEvict(value = {"products", "productsByCategory"}, allEntries = true)` on `deleteProduct` -- Clears both caches when a product is deleted.

### The Product Controller

```java
// src/main/java/com/example/caching/controller/ProductController.java
package com.example.caching.controller;

import com.example.caching.entity.Product;
import com.example.caching.service.ProductService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Product> getProduct(@PathVariable Long id) {
        return ResponseEntity.ok(productService.getProductById(id));
    }

    @GetMapping("/category/{category}")
    public ResponseEntity<List<Product>> getByCategory(
            @PathVariable String category) {
        return ResponseEntity.ok(
            productService.getProductsByCategory(category));
    }

    @PostMapping
    public ResponseEntity<Product> createProduct(
            @RequestBody Product product) {
        Product created = productService.createProduct(product);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Product> updateProduct(
            @PathVariable Long id,
            @RequestBody Product product) {
        product.setId(id);
        return ResponseEntity.ok(productService.updateProduct(product));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        productService.deleteProduct(id);
        return ResponseEntity.noContent().build();
    }
}
```

---

## 24.8 Testing the Caching Behavior

### Step 1: Create a Product

```bash
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "category": "electronics", "price": 29.99}'
```

**Output:**
```json
{"id": 1, "name": "Widget", "category": "electronics", "price": 29.99}
```

**Log:**
```
Creating product: Widget
```

### Step 2: Get the Product (First Call - Cache Miss)

```bash
curl http://localhost:8080/api/products/1
```

**Log:**
```
Cache miss - Fetching product 1 from database
```

### Step 3: Get the Product Again (Cache Hit)

```bash
curl http://localhost:8080/api/products/1
```

**Log:** (Nothing! The method body did not execute because the result came from the cache.)

### Step 4: Update the Product

```bash
curl -X PUT http://localhost:8080/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Super Widget", "category": "electronics", "price": 39.99}'
```

**Log:**
```
Updating product: 1
```

### Step 5: Get the Updated Product (From Cache)

```bash
curl http://localhost:8080/api/products/1
```

**Output:** Shows the updated product. No log message because `@CachePut` already updated the cache during the update.

---

## 24.9 ConcurrentMapCacheManager

By default, Spring Boot uses `ConcurrentMapCacheManager`. It stores cache entries in `ConcurrentHashMap` objects in memory.

You can also configure it explicitly:

```java
// src/main/java/com/example/caching/config/CacheConfig.java
package com.example.caching.config;

import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager(
            "products",
            "productsByCategory"
        );
    }
}
```

**Line-by-line explanation:**

- `ConcurrentMapCacheManager("products", "productsByCategory")` -- Pre-creates the named caches. You can also let Spring create them on demand (which is the default behavior).

### Characteristics of ConcurrentMapCacheManager

| Feature | ConcurrentMapCacheManager |
|---------|--------------------------|
| Storage | In-memory (heap) |
| Eviction | None (entries stay forever until explicitly removed) |
| Max size | No limit (can cause OutOfMemoryError) |
| TTL (Time-to-live) | Not supported |
| Distributed | No (single JVM only) |
| Use case | Development, small apps, testing |

> **For production** with high traffic, consider switching to Caffeine (in-memory with TTL and size limits) or Redis (distributed, persistent). The beauty of Spring's cache abstraction is that you only need to change the CacheManager bean. Your `@Cacheable`, `@CacheEvict`, and `@CachePut` annotations stay the same.

---

## 24.10 Conditional Caching

Sometimes you want to cache results only under certain conditions:

```java
// Only cache if the product price is above 10
@Cacheable(value = "products",
           condition = "#id > 0")
public Product getProductById(Long id) {
    return productRepository.findById(id).orElseThrow();
}

// Only cache if the result is not null
@Cacheable(value = "products",
           unless = "#result == null")
public Product findProduct(Long id) {
    return productRepository.findById(id).orElse(null);
}

// Combine conditions
@Cacheable(value = "products",
           condition = "#id > 0",
           unless = "#result.price < 1.0")
public Product getProduct(Long id) {
    return productRepository.findById(id).orElseThrow();
}
```

**Line-by-line explanation:**

- `condition` -- Evaluated BEFORE the method runs. If it returns false, the cache is not checked and the result is not cached. Use `#paramName` to reference method arguments.
- `unless` -- Evaluated AFTER the method runs. If it returns true, the result is NOT cached. Use `#result` to reference the return value.

| Attribute | When Evaluated | If True |
|-----------|----------------|---------|
| `condition` | Before method | Cache is checked and result is cached |
| `unless` | After method | Result is NOT cached |

---

## 24.11 When to Cache and When Not to Cache

### Good Candidates for Caching

| Data Type | Why Cache It |
|-----------|-------------|
| **Product catalogs** | Rarely change, frequently accessed |
| **User profiles** | Read often, updated rarely |
| **Configuration data** | Almost never changes |
| **API responses from external services** | Slow to fetch, rate-limited |
| **Computed results** | Expensive calculations, same inputs give same outputs |

### Bad Candidates for Caching

| Data Type | Why NOT Cache It |
|-----------|-----------------|
| **Real-time stock prices** | Changes every second |
| **User session data** | Unique per user, short-lived |
| **Random or unique data** | Every call produces different results |
| **Data that must always be fresh** | Account balances, inventory counts |
| **Very large datasets** | Can exhaust memory |

### The Caching Decision Flowchart

```
+---------------------------------------------------+
|     SHOULD YOU CACHE THIS DATA?                    |
+---------------------------------------------------+
|                                                    |
|  Is the data read frequently?                      |
|       |                                            |
|       +--> No --> Do not cache                     |
|       |                                            |
|       +--> Yes --> Continue                        |
|       |                                            |
|       v                                            |
|  Does the data change rarely?                      |
|       |                                            |
|       +--> No --> Do not cache (or use short TTL)  |
|       |                                            |
|       +--> Yes --> Continue                        |
|       |                                            |
|       v                                            |
|  Is fetching the data slow or expensive?           |
|       |                                            |
|       +--> No --> Caching provides little benefit   |
|       |                                            |
|       +--> Yes --> CACHE IT!                       |
|       |                                            |
|       v                                            |
|  Is stale data acceptable for a short time?        |
|       |                                            |
|       +--> No --> Cache with immediate eviction     |
|       |          on updates                         |
|       |                                            |
|       +--> Yes --> Cache with TTL                  |
|                                                    |
+---------------------------------------------------+
```

---

## 24.12 Initializing Sample Data

For testing, let us create sample data on startup:

```java
// src/main/java/com/example/caching/config/DataInitializer.java
package com.example.caching.config;

import com.example.caching.entity.Product;
import com.example.caching.repository.ProductRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private final ProductRepository productRepository;

    public DataInitializer(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    @Override
    public void run(String... args) {
        productRepository.save(
            new Product("Laptop", "electronics", 999.99));
        productRepository.save(
            new Product("Phone", "electronics", 699.99));
        productRepository.save(
            new Product("Desk", "furniture", 249.99));
        productRepository.save(
            new Product("Chair", "furniture", 199.99));
        productRepository.save(
            new Product("Coffee Mug", "kitchen", 12.99));

        System.out.println("Sample products loaded: "
            + productRepository.count());
    }
}
```

And the application properties:

```properties
# src/main/resources/application.properties
spring.datasource.url=jdbc:h2:mem:cachingdb
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.hibernate.ddl-auto=create-drop
spring.h2.console.enabled=true

# Show cache-related logs
logging.level.org.springframework.cache=TRACE
logging.level.com.example.caching=DEBUG
```

Setting `org.springframework.cache` to TRACE lets you see cache hits and misses in the logs.

---

## Common Mistakes

1. **Forgetting @EnableCaching.** Without this annotation, all caching annotations are ignored. Your application will work, but nothing will be cached.

2. **Calling cached methods from within the same class.** Spring caching uses proxies. If method A in a class calls method B (which has @Cacheable) in the same class, the cache is bypassed because the proxy is not involved. Always call cached methods from another class.

    ```java
    @Service
    public class ProductService {

        @Cacheable("products")
        public Product getById(Long id) { ... }

        public Product getAndProcess(Long id) {
            // THIS BYPASSES THE CACHE because it is a
            // self-invocation (same class)
            Product p = getById(id);
            return process(p);
        }
    }
    ```

3. **Not evicting the cache when data changes.** If you update or delete data without evicting the cache, users will see stale data.

4. **Caching mutable objects.** If you cache an object and then modify it, the cached version is also modified (because they are the same object in memory). Cache immutable objects or copies.

5. **Using the default ConcurrentMapCacheManager in production with high traffic.** It has no size limit and no TTL. Entries stay forever and can cause OutOfMemoryError.

6. **Caching null values unintentionally.** By default, null values are cached. Use `unless = "#result == null"` to prevent this.

---

## Best Practices

1. **Cache at the service layer, not the controller layer.** The service layer is where business logic lives. Caching there means any caller benefits from the cache.

2. **Use meaningful cache names.** Use names like "products", "userProfiles", "orderSummaries" instead of generic names like "cache1" or "myCache".

3. **Always evict or update the cache when data changes.** Pair every write operation with a @CacheEvict or @CachePut.

4. **Log cache misses.** Add a log statement in cached methods so you can see when the method actually executes versus when the cache is used.

5. **Consider cache size and TTL for production.** Switch from ConcurrentMapCacheManager to Caffeine (for size limits and TTL) or Redis (for distributed caching).

6. **Test with caching enabled and disabled.** Your application should work correctly even without caching. Caching is an optimization, not a requirement.

---

## Quick Summary

Caching stores frequently accessed data in memory so your application can return results instantly instead of querying the database every time. Spring Boot's caching is enabled with @EnableCaching and uses three main annotations. @Cacheable stores a method's return value in the cache and returns the cached value on subsequent calls with the same arguments. @CacheEvict removes entries from the cache when data is deleted or you need to refresh. @CachePut always executes the method and updates the cache with the result, used for update operations. Cache keys are based on method arguments by default but can be customized with SpEL expressions. The default ConcurrentMapCacheManager is good for development but should be replaced with Caffeine or Redis for production use.

---

## Key Points

- @EnableCaching activates Spring's caching infrastructure.
- @Cacheable caches method results. The method is skipped on cache hits.
- @CacheEvict removes entries from the cache.
- @CachePut always runs the method and updates the cache.
- Cache keys default to method arguments. Customize with the `key` attribute.
- Use `condition` to control when caching applies (evaluated before the method).
- Use `unless` to prevent caching certain results (evaluated after the method).
- Self-invocation (calling a cached method from within the same class) bypasses the cache.
- ConcurrentMapCacheManager is the default. It has no size limits or TTL.
- Always evict or update the cache when the underlying data changes.
- Caching is best for data that is read often, changes rarely, and is expensive to fetch.

---

## Practice Questions

1. What is the difference between @Cacheable and @CachePut? When would you use each?

2. Why does calling a @Cacheable method from within the same class bypass the cache?

3. What happens if you use @Cacheable but forget to add @EnableCaching to your application?

4. You have a method `getUser(Long id)` with @Cacheable. A user updates their profile. How do you make sure the next call to `getUser` returns the updated data?

5. Why is ConcurrentMapCacheManager not recommended for high-traffic production applications?

---

## Exercises

### Exercise 1: Cache a User Service

Create a UserService with @Cacheable on `getUserById()`. Create a UserController that calls it. Call the endpoint three times and verify (using log output) that the database is only queried once.

### Exercise 2: Implement Cache Eviction

Add update and delete operations to the UserService from Exercise 1. Use @CachePut for updates and @CacheEvict for deletes. Test that after updating a user, the cached version reflects the new data.

### Exercise 3: Category-Based Caching

Create a product service that caches products by category using a separate cache called "productsByCategory". When a product is added, updated, or deleted, clear the category cache. Test by fetching products by category, adding a new product, and fetching again (the second fetch should hit the database because the cache was cleared).

---

## What Is Next?

Your application is now faster thanks to caching. You have learned how to store results in memory, evict stale data, and update cached values when the underlying data changes. In Chapter 25, you will learn how to send emails from your Spring Boot application. You will configure an email service, send plain text and HTML emails, and attach files to messages.
