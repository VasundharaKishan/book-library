# Chapter 25: CQRS (Command Query Responsibility Segregation)

## What You Will Learn

- What CQRS is and the problem it solves
- How to separate read models from write models
- How to implement separate command and query services in Java
- How to implement CQRS in Python
- When to use different databases for reads and writes
- How CQRS applies to real-world e-commerce systems
- When CQRS is overkill and simpler patterns suffice

## Why This Chapter Matters

Most backend applications start with a single data model for both reading and writing. The `Product` table stores product data, and the same model serves both the admin editing products and the customer browsing the catalog. This works fine until it does not.

As your application grows, reads and writes develop conflicting requirements. Customers want fast, denormalized product listings with ratings, reviews, and pricing tiers joined together. Admins want a normalized write model that enforces business rules. The single model becomes a compromise that serves neither audience well. Read queries slow down because of the normalization needed for writes. Write operations become complex because of the denormalized fields needed for reads.

CQRS solves this by splitting your application into two sides: a **Command** side that handles writes with a model optimized for enforcing business rules, and a **Query** side that handles reads with a model optimized for fast retrieval. Each side can be designed, scaled, and optimized independently.

---

## The Problem

Consider an e-commerce product catalog. The write side needs to enforce rules: prices must be positive, stock cannot go negative, categories must exist. The read side needs to display products with their category names, average ratings, review counts, and calculated discount prices -- all in a single fast query.

### Before: One Model for Everything

```java
// Single model tries to serve both reads and writes
@Entity
public class Product {
    @Id private Long id;
    private String name;
    private String description;
    private BigDecimal price;
    private int stock;
    private Long categoryId;
    // ... 20 more fields
}

@Service
public class ProductService {

    // WRITE: complex validation and business rules
    public void updatePrice(Long productId, BigDecimal newPrice) {
        Product product = repository.findById(productId).orElseThrow();
        if (newPrice.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Price must be positive");
        }
        product.setPrice(newPrice);
        repository.save(product);
        // Also update search index, cache, price history...
    }

    // READ: needs joins across 5 tables for a catalog page
    public ProductCatalogView getProductForCatalog(Long productId) {
        // This query joins products, categories, reviews, images, promotions
        // It is slow and complex
        return entityManager.createQuery(
            "SELECT new ProductCatalogView(p.id, p.name, p.price, " +
            "c.name, AVG(r.rating), COUNT(r.id), ...) " +
            "FROM Product p " +
            "JOIN Category c ON p.categoryId = c.id " +
            "LEFT JOIN Review r ON r.productId = p.id " +
            "LEFT JOIN ProductImage i ON i.productId = p.id " +
            "LEFT JOIN Promotion pr ON pr.productId = p.id " +
            "WHERE p.id = :id " +
            "GROUP BY p.id, p.name, p.price, c.name",
            ProductCatalogView.class
        ).setParameter("id", productId).getSingleResult();
    }
}
```

**Problems:**

1. The catalog query joins 5 tables and is slow
2. Every product write triggers cache invalidation for reads
3. You cannot scale reads independently from writes
4. The Product entity is bloated with fields for both purposes
5. Read-optimized indexes slow down writes, and vice versa

---

## The Solution: CQRS

CQRS splits your system into two distinct paths:

```
                        +-------------+
                        |   Client    |
                        +------+------+
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v
        +--------+--------+        +--------+--------+
        |    COMMAND       |        |     QUERY        |
        |    (Write Side)  |        |    (Read Side)   |
        +--------+--------+        +--------+---------+
                 |                           |
                 v                           v
        +--------+--------+        +---------+--------+
        | Write Model      |        | Read Model        |
        | (Normalized)     |        | (Denormalized)    |
        |                  |        |                   |
        | products         |        | product_catalog   |
        | categories       |  --->  | (pre-joined view  |
        | reviews          | sync   |  with all data    |
        | promotions       |        |  flattened)       |
        +------------------+        +-------------------+
        | PostgreSQL       |        | PostgreSQL / Redis |
        | (optimized for   |        | (optimized for    |
        |  consistency)    |        |  fast reads)      |
        +------------------+        +-------------------+
```

---

## How CQRS Works

### The Command Side (Writes)

Commands represent intentions to change state. They are imperative: "Create Product," "Update Price," "Cancel Order."

```
Command Flow:

  Client sends command
         |
         v
  +------------------+
  | Command Handler  |  <-- Validates and processes
  +------------------+
         |
         v
  +------------------+
  | Domain Model     |  <-- Business rules enforced
  | (Write Model)    |
  +------------------+
         |
         v
  +------------------+
  | Write Database   |  <-- Normalized tables
  +------------------+
         |
         v
  +------------------+
  | Publish Event    |  <-- "ProductPriceChanged"
  +------------------+
```

### The Query Side (Reads)

Queries return data without modifying state. They are questions: "Get product details," "List products in category."

```
Query Flow:

  Client sends query
         |
         v
  +------------------+
  | Query Handler    |  <-- Simple data retrieval
  +------------------+
         |
         v
  +------------------+
  | Read Model       |  <-- Denormalized, pre-joined
  | (View/Projection)|
  +------------------+
         |
         v
  +------------------+
  | Read Database    |  <-- Optimized for fast reads
  +------------------+
```

---

## Java Implementation: Separate Command and Query Services

### Step 1: Define Commands and Queries

```java
// ===== COMMANDS (Write operations) =====

public class CreateProductCommand {
    private final String name;
    private final String description;
    private final BigDecimal price;
    private final int stock;
    private final Long categoryId;

    public CreateProductCommand(String name, String description,
                                 BigDecimal price, int stock,
                                 Long categoryId) {
        this.name = name;
        this.description = description;
        this.price = price;
        this.stock = stock;
        this.categoryId = categoryId;
    }

    // Getters
    public String getName() { return name; }
    public String getDescription() { return description; }
    public BigDecimal getPrice() { return price; }
    public int getStock() { return stock; }
    public Long getCategoryId() { return categoryId; }
}

public class UpdatePriceCommand {
    private final Long productId;
    private final BigDecimal newPrice;

    public UpdatePriceCommand(Long productId, BigDecimal newPrice) {
        this.productId = productId;
        this.newPrice = newPrice;
    }

    public Long getProductId() { return productId; }
    public BigDecimal getNewPrice() { return newPrice; }
}

// ===== QUERIES (Read operations) =====

public class GetProductQuery {
    private final Long productId;

    public GetProductQuery(Long productId) {
        this.productId = productId;
    }

    public Long getProductId() { return productId; }
}

public class SearchProductsQuery {
    private final String keyword;
    private final String category;
    private final int page;
    private final int size;

    public SearchProductsQuery(String keyword, String category,
                                int page, int size) {
        this.keyword = keyword;
        this.category = category;
        this.page = page;
        this.size = size;
    }

    // Getters...
    public String getKeyword() { return keyword; }
    public String getCategory() { return category; }
    public int getPage() { return page; }
    public int getSize() { return size; }
}
```

### Step 2: Write Model (Command Side)

```java
// Write-side entity: normalized, enforces business rules
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private String description;

    @Column(nullable = false)
    private BigDecimal price;

    @Column(nullable = false)
    private int stock;

    @Column(name = "category_id", nullable = false)
    private Long categoryId;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // Business rule: price must be positive
    public void updatePrice(BigDecimal newPrice) {
        if (newPrice.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Price must be positive");
        }
        this.price = newPrice;
        this.updatedAt = LocalDateTime.now();
    }

    // Business rule: stock cannot go negative
    public void deductStock(int quantity) {
        if (quantity > this.stock) {
            throw new IllegalStateException("Insufficient stock");
        }
        this.stock -= quantity;
        this.updatedAt = LocalDateTime.now();
    }

    // Getters, setters, constructor omitted for brevity
}
```

### Step 3: Read Model (Query Side)

```java
// Read-side view: denormalized, optimized for display
public class ProductCatalogView {
    private Long id;
    private String name;
    private String description;
    private BigDecimal price;
    private BigDecimal discountedPrice;
    private int stock;
    private boolean inStock;
    private String categoryName;
    private double averageRating;
    private int reviewCount;
    private String thumbnailUrl;

    // This class is a flat, read-optimized projection
    // No business logic, just data for display

    public ProductCatalogView() {}

    public ProductCatalogView(Long id, String name, BigDecimal price,
                               String categoryName, double averageRating,
                               int reviewCount, int stock) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.categoryName = categoryName;
        this.averageRating = averageRating;
        this.reviewCount = reviewCount;
        this.stock = stock;
        this.inStock = stock > 0;
    }

    // Getters and setters...
    public Long getId() { return id; }
    public String getName() { return name; }
    public BigDecimal getPrice() { return price; }
    public String getCategoryName() { return categoryName; }
    public double getAverageRating() { return averageRating; }
    public int getReviewCount() { return reviewCount; }
    public boolean isInStock() { return inStock; }

    @Override
    public String toString() {
        return String.format("%-20s $%-8s %-12s Rating: %.1f (%d reviews) %s",
            name, price, categoryName, averageRating, reviewCount,
            inStock ? "In Stock" : "Out of Stock");
    }
}
```

### Step 4: Command Handler (Write Service)

```java
@Service
public class ProductCommandService {

    private final ProductRepository productRepository;
    private final ApplicationEventPublisher eventPublisher;

    public ProductCommandService(ProductRepository productRepository,
                                  ApplicationEventPublisher eventPublisher) {
        this.productRepository = productRepository;
        this.eventPublisher = eventPublisher;
    }

    @Transactional
    public Long handle(CreateProductCommand command) {
        Product product = new Product();
        product.setName(command.getName());
        product.setDescription(command.getDescription());
        product.setPrice(command.getPrice());
        product.setStock(command.getStock());
        product.setCategoryId(command.getCategoryId());
        product.setCreatedAt(LocalDateTime.now());

        Product saved = productRepository.save(product);

        // Publish event to sync the read model
        eventPublisher.publishEvent(
            new ProductCreatedEvent(saved.getId(), saved.getName(),
                                    saved.getPrice(), saved.getStock()));

        System.out.println("Command: Created product " + saved.getId());
        return saved.getId();
    }

    @Transactional
    public void handle(UpdatePriceCommand command) {
        Product product = productRepository.findById(command.getProductId())
            .orElseThrow(() -> new RuntimeException("Product not found"));

        product.updatePrice(command.getNewPrice());
        productRepository.save(product);

        // Publish event to sync the read model
        eventPublisher.publishEvent(
            new ProductPriceChangedEvent(product.getId(),
                                         command.getNewPrice()));

        System.out.println("Command: Updated price for product " +
                           product.getId());
    }
}
```

### Step 5: Query Handler (Read Service)

```java
@Service
public class ProductQueryService {

    private final JdbcTemplate jdbcTemplate;

    public ProductQueryService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public ProductCatalogView handle(GetProductQuery query) {
        // Read directly from the denormalized read model
        String sql = """
            SELECT id, name, price, category_name, average_rating,
                   review_count, stock
            FROM product_catalog_view
            WHERE id = ?
            """;

        return jdbcTemplate.queryForObject(sql,
            (rs, rowNum) -> new ProductCatalogView(
                rs.getLong("id"),
                rs.getString("name"),
                rs.getBigDecimal("price"),
                rs.getString("category_name"),
                rs.getDouble("average_rating"),
                rs.getInt("review_count"),
                rs.getInt("stock")
            ),
            query.getProductId()
        );
    }

    public List<ProductCatalogView> handle(SearchProductsQuery query) {
        String sql = """
            SELECT id, name, price, category_name, average_rating,
                   review_count, stock
            FROM product_catalog_view
            WHERE (? IS NULL OR name ILIKE ?)
              AND (? IS NULL OR category_name = ?)
            ORDER BY average_rating DESC
            LIMIT ? OFFSET ?
            """;

        String keyword = query.getKeyword() != null
            ? "%" + query.getKeyword() + "%" : null;

        return jdbcTemplate.query(sql,
            (rs, rowNum) -> new ProductCatalogView(
                rs.getLong("id"),
                rs.getString("name"),
                rs.getBigDecimal("price"),
                rs.getString("category_name"),
                rs.getDouble("average_rating"),
                rs.getInt("review_count"),
                rs.getInt("stock")
            ),
            keyword, keyword,
            query.getCategory(), query.getCategory(),
            query.getSize(), query.getPage() * query.getSize()
        );
    }
}
```

### Step 6: Event Handler (Syncs Read Model)

```java
@Component
public class ProductReadModelUpdater {

    private final JdbcTemplate jdbcTemplate;

    public ProductReadModelUpdater(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @EventListener
    public void on(ProductCreatedEvent event) {
        jdbcTemplate.update("""
            INSERT INTO product_catalog_view
                (id, name, price, category_name, average_rating,
                 review_count, stock)
            VALUES (?, ?, ?, ?, 0.0, 0, ?)
            """,
            event.getProductId(),
            event.getName(),
            event.getPrice(),
            "Uncategorized",  // Would look up category name
            event.getStock()
        );
        System.out.println("Read model: Added product " +
                           event.getProductId());
    }

    @EventListener
    public void on(ProductPriceChangedEvent event) {
        jdbcTemplate.update(
            "UPDATE product_catalog_view SET price = ? WHERE id = ?",
            event.getNewPrice(),
            event.getProductId()
        );
        System.out.println("Read model: Updated price for product " +
                           event.getProductId());
    }
}
```

### Step 7: REST Controller

```java
@RestController
@RequestMapping("/products")
public class ProductController {

    private final ProductCommandService commandService;
    private final ProductQueryService queryService;

    public ProductController(ProductCommandService commandService,
                              ProductQueryService queryService) {
        this.commandService = commandService;
        this.queryService = queryService;
    }

    // COMMAND endpoints (writes)
    @PostMapping
    public ResponseEntity<Long> createProduct(
            @RequestBody CreateProductCommand command) {
        Long id = commandService.handle(command);
        return ResponseEntity.status(HttpStatus.CREATED).body(id);
    }

    @PutMapping("/{id}/price")
    public ResponseEntity<Void> updatePrice(
            @PathVariable Long id,
            @RequestBody BigDecimal newPrice) {
        commandService.handle(new UpdatePriceCommand(id, newPrice));
        return ResponseEntity.ok().build();
    }

    // QUERY endpoints (reads)
    @GetMapping("/{id}")
    public ProductCatalogView getProduct(@PathVariable Long id) {
        return queryService.handle(new GetProductQuery(id));
    }

    @GetMapping
    public List<ProductCatalogView> searchProducts(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return queryService.handle(
            new SearchProductsQuery(keyword, category, page, size));
    }
}
```

**Output when running:**

```
Command: Created product 1
Read model: Added product 1

Command: Created product 2
Read model: Added product 2

Command: Updated price for product 1
Read model: Updated price for product 1

Query result:
Laptop Pro           $1299.99  Electronics  Rating: 4.5 (120 reviews) In Stock
Wireless Mouse       $29.99    Accessories  Rating: 4.2 (85 reviews)  In Stock
```

---

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# ===== COMMANDS =====

@dataclass
class CreateProductCommand:
    name: str
    description: str
    price: float
    stock: int
    category_id: int

@dataclass
class UpdatePriceCommand:
    product_id: int
    new_price: float

# ===== QUERIES =====

@dataclass
class GetProductQuery:
    product_id: int

@dataclass
class SearchProductsQuery:
    keyword: Optional[str] = None
    category: Optional[str] = None
    page: int = 0
    size: int = 20

# ===== WRITE MODEL =====

class Product:
    """Write model: enforces business rules."""

    def __init__(self, id, name, description, price, stock, category_id):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.category_id = category_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_price(self, new_price: float):
        if new_price <= 0:
            raise ValueError("Price must be positive")
        self.price = new_price
        self.updated_at = datetime.utcnow()

    def deduct_stock(self, quantity: int):
        if quantity > self.stock:
            raise ValueError("Insufficient stock")
        self.stock -= quantity
        self.updated_at = datetime.utcnow()

# ===== READ MODEL =====

@dataclass
class ProductCatalogView:
    """Read model: optimized for display."""
    id: int
    name: str
    price: float
    category_name: str
    average_rating: float
    review_count: int
    stock: int
    in_stock: bool = True

    def __post_init__(self):
        self.in_stock = self.stock > 0

    def __str__(self):
        status = "In Stock" if self.in_stock else "Out of Stock"
        return (f"{self.name:<20} ${self.price:<8.2f} "
                f"{self.category_name:<12} "
                f"Rating: {self.average_rating:.1f} "
                f"({self.review_count} reviews) {status}")


# ===== COMMAND HANDLER =====

class ProductCommandHandler:
    """Handles write operations."""

    def __init__(self, write_repo, event_bus):
        self.write_repo = write_repo
        self.event_bus = event_bus

    def handle_create(self, command: CreateProductCommand) -> int:
        product = Product(
            id=None,
            name=command.name,
            description=command.description,
            price=command.price,
            stock=command.stock,
            category_id=command.category_id
        )
        saved = self.write_repo.save(product)
        print(f"Command: Created product {saved.id}")

        # Publish event to sync read model
        self.event_bus.publish("product_created", {
            "id": saved.id,
            "name": saved.name,
            "price": saved.price,
            "stock": saved.stock,
            "category_id": saved.category_id,
        })
        return saved.id

    def handle_update_price(self, command: UpdatePriceCommand):
        product = self.write_repo.find_by_id(command.product_id)
        if product is None:
            raise ValueError(f"Product not found: {command.product_id}")

        product.update_price(command.new_price)
        self.write_repo.save(product)
        print(f"Command: Updated price for product {product.id}")

        self.event_bus.publish("product_price_changed", {
            "id": product.id,
            "new_price": command.new_price,
        })


# ===== QUERY HANDLER =====

class ProductQueryHandler:
    """Handles read operations from the read model."""

    def __init__(self, read_repo):
        self.read_repo = read_repo

    def handle_get(self, query: GetProductQuery) -> Optional[ProductCatalogView]:
        return self.read_repo.find_by_id(query.product_id)

    def handle_search(self, query: SearchProductsQuery) -> List[ProductCatalogView]:
        results = self.read_repo.find_all()

        if query.keyword:
            results = [p for p in results
                       if query.keyword.lower() in p.name.lower()]
        if query.category:
            results = [p for p in results
                       if p.category_name == query.category]

        start = query.page * query.size
        return results[start:start + query.size]


# ===== EVENT BUS (syncs read model) =====

class SimpleEventBus:
    def __init__(self):
        self._handlers = {}

    def subscribe(self, event_type, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event_type, data):
        for handler in self._handlers.get(event_type, []):
            handler(data)


# ===== IN-MEMORY REPOSITORIES =====

class InMemoryWriteRepo:
    def __init__(self):
        self._store = {}
        self._next_id = 1

    def save(self, product):
        if product.id is None:
            product.id = self._next_id
            self._next_id += 1
        self._store[product.id] = product
        return product

    def find_by_id(self, product_id):
        return self._store.get(product_id)


class InMemoryReadRepo:
    def __init__(self):
        self._store = {}

    def save(self, view: ProductCatalogView):
        self._store[view.id] = view

    def find_by_id(self, product_id):
        return self._store.get(product_id)

    def find_all(self):
        return list(self._store.values())

    def update_price(self, product_id, new_price):
        if product_id in self._store:
            self._store[product_id].price = new_price


# ===== WIRE IT TOGETHER =====

# Categories lookup (simplified)
categories = {1: "Electronics", 2: "Accessories", 3: "Books"}

# Setup
write_repo = InMemoryWriteRepo()
read_repo = InMemoryReadRepo()
event_bus = SimpleEventBus()

# Read model updater (subscribes to events)
def on_product_created(data):
    view = ProductCatalogView(
        id=data["id"],
        name=data["name"],
        price=data["price"],
        category_name=categories.get(data["category_id"], "Unknown"),
        average_rating=0.0,
        review_count=0,
        stock=data["stock"],
    )
    read_repo.save(view)
    print(f"Read model: Added product {data['id']}")

def on_price_changed(data):
    read_repo.update_price(data["id"], data["new_price"])
    print(f"Read model: Updated price for product {data['id']}")

event_bus.subscribe("product_created", on_product_created)
event_bus.subscribe("product_price_changed", on_price_changed)

# Handlers
command_handler = ProductCommandHandler(write_repo, event_bus)
query_handler = ProductQueryHandler(read_repo)

# Use the system
command_handler.handle_create(
    CreateProductCommand("Laptop Pro", "High-end laptop", 1299.99, 50, 1))
command_handler.handle_create(
    CreateProductCommand("Wireless Mouse", "Ergonomic mouse", 29.99, 200, 2))

command_handler.handle_update_price(UpdatePriceCommand(1, 1199.99))

print("\nSearch results:")
results = query_handler.handle_search(SearchProductsQuery())
for product in results:
    print(f"  {product}")
```

**Output:**

```
Command: Created product 1
Read model: Added product 1
Command: Created product 2
Read model: Added product 2
Command: Updated price for product 1
Read model: Updated price for product 1

Search results:
  Laptop Pro           $1199.99  Electronics  Rating: 0.0 (0 reviews) In Stock
  Wireless Mouse       $29.99    Accessories  Rating: 0.0 (0 reviews) In Stock
```

---

## Using Different Databases for Read and Write

In advanced CQRS, you can use entirely different databases:

```
+-------------------+          +-------------------+
|   Command Side    |          |    Query Side     |
+-------------------+          +-------------------+
|                   |          |                   |
| PostgreSQL        |  Events  | Elasticsearch     |
| (Normalized)      | -------> | (Full-text search)|
|                   |          |                   |
| - products        |          | - product_catalog |
| - categories      |   or     |   (denormalized   |
| - reviews         |          |    documents)     |
| - inventory       |          |                   |
+-------------------+  Redis   +-------------------+
                       Cache
                         |
                         v
                    +----------+
                    |  Redis   |
                    | (Hot     |
                    |  data    |
                    |  cache)  |
                    +----------+
```

### Synchronization Strategies

```
Strategy 1: Synchronous (Simple, Consistent)
  Write --> Update Read Model --> Return Response
  Pro: Read model always up to date
  Con: Slower writes

Strategy 2: Asynchronous via Events (Scalable)
  Write --> Return Response
            \--> Event Queue --> Update Read Model (eventually)
  Pro: Fast writes, scalable
  Con: Read model may be stale briefly (eventual consistency)

Strategy 3: Periodic Sync (Simple, Batch)
  Write --> Return Response
  Cron job (every 5 min) --> Rebuild Read Model
  Pro: Very simple
  Con: Data can be up to 5 minutes stale
```

---

## Real-World: E-Commerce Product Catalog

```
WRITE SIDE (Admin Panel)                READ SIDE (Customer Storefront)
+---------------------------+          +---------------------------+
| Normalized PostgreSQL     |          | Denormalized Read Store   |
|                           |          |                           |
| products                  |          | product_catalog_view      |
|   id, name, price,        |          |   id, name, price,        |
|   description, category_id|  Events  |   discounted_price,       |
|                           | -------> |   category_name,          |
| categories                |          |   avg_rating,             |
|   id, name, parent_id     |          |   review_count,           |
|                           |          |   thumbnail_url,          |
| reviews                   |          |   in_stock,               |
|   id, product_id, rating, |          |   tags                    |
|   comment                 |          |                           |
|                           |          | (Single table, no joins,  |
| promotions                |          |  indexed for search)      |
|   id, product_id,         |          |                           |
|   discount_percent        |          +---------------------------+
+---------------------------+
```

The write side has 4 normalized tables with referential integrity. The read side has 1 flat table with all data pre-joined. A customer catalog query hits one table with no joins, returning results in milliseconds.

---

## When CQRS Is Overkill

CQRS adds complexity. Do not use it when:

```
+-------------------------------+----------------------------------+
| Scenario                      | Better Alternative               |
+-------------------------------+----------------------------------+
| Simple CRUD application       | Standard service + repository    |
| Read and write models are     | Single model works fine          |
|   nearly identical            |                                  |
| Low traffic (< 100 req/sec)   | Single database with indexes     |
| Small team (1-3 developers)   | Simpler architecture, less       |
|                               |   cognitive overhead             |
| Prototype / MVP               | Ship fast, refactor later        |
| Data is always read right     | Single source of truth is        |
|   after write                 |   simpler                        |
+-------------------------------+----------------------------------+
```

---

## When to Use / When NOT to Use

### Use CQRS When

- Read and write workloads have very different performance requirements
- You need to scale reads and writes independently
- Your read queries require complex joins across many tables
- You are building an event-driven system
- Different teams own the read and write sides
- You need different data stores for different access patterns

### Do NOT Use CQRS When

- Your read and write models look the same
- You have a simple CRUD application
- Eventual consistency is not acceptable for your use case
- Your team is small and the added complexity is not justified
- You do not have the infrastructure to manage separate data stores

---

## Common Mistakes

1. **Applying CQRS everywhere.** CQRS is a pattern for specific parts of your system, not the entire application. Use it only where read and write models genuinely diverge.

2. **Ignoring eventual consistency.** When the read model is updated asynchronously, it may be slightly behind the write model. Your UI must handle this gracefully.

3. **Making the read model too complex.** The read model should be simple and flat. If you are writing complex query logic in the read service, you are doing it wrong.

4. **Not handling sync failures.** If the event that updates the read model fails, the data becomes permanently stale. Build retry mechanisms and monitoring.

5. **Using CQRS without events.** You can use CQRS without event sourcing, but you need a synchronization mechanism. Without one, the read model drifts.

---

## Best Practices

1. **Start with a single database.** Use database views or materialized views for the read model before introducing separate databases.

2. **Use events for synchronization.** Domain events are the natural way to keep the read model in sync with the write model.

3. **Design read models for specific use cases.** Create one read model per screen or API endpoint. A product list view and a product detail view can be different read models.

4. **Monitor sync lag.** Track the delay between a write and when the read model reflects it. Alert if it exceeds your SLA.

5. **Make commands explicit.** Name your commands after business actions: `PlaceOrder`, `CancelSubscription`, `ApproveRefund`. Not `UpdateOrderStatus`.

---

## Quick Summary

CQRS separates your application into a command side (writes) and a query side (reads), each with its own model optimized for its purpose. The write model is normalized and enforces business rules. The read model is denormalized and optimized for fast retrieval. Events synchronize the two sides. CQRS enables independent scaling and optimization of reads and writes but adds complexity through eventual consistency and data synchronization. Use it when read and write patterns genuinely differ; avoid it for simple CRUD applications.

---

## Key Points

- CQRS splits the application into separate command (write) and query (read) paths
- The write model is normalized and enforces business rules
- The read model is denormalized and optimized for fast retrieval
- Events synchronize the write model with the read model
- You can use different databases for reads and writes
- Eventual consistency is a trade-off you must design around
- CQRS is not all-or-nothing; apply it to specific bounded contexts
- Start simple with database views before introducing separate stores
- CQRS pairs naturally with Event Sourcing (covered in the next chapter)

---

## Practice Questions

1. Explain the difference between the command model and the query model in CQRS. Why would you want them to be different?

2. What is eventual consistency, and how does it affect the user experience in a CQRS system? How would you handle a scenario where a user creates a product and immediately tries to search for it?

3. You have an e-commerce system where 95% of traffic is product browsing (reads) and 5% is admin updates (writes). How would CQRS help you scale this system?

4. Compare synchronous and asynchronous synchronization strategies for keeping the read model updated. What are the trade-offs of each?

5. A colleague wants to apply CQRS to a simple blog application with 100 daily users. What would you advise?

---

## Exercises

### Exercise 1: Blog with CQRS

Build a simple blog system using CQRS. The write side handles `CreatePost`, `UpdatePost`, and `PublishPost` commands. The read side provides `GetPost`, `ListPublishedPosts`, and `SearchPosts` queries. Use events to sync the read model. The read model should include the author name (joined from a users table on the write side).

### Exercise 2: Inventory CQRS

Create an inventory system where the write side tracks stock levels with business rules (no negative stock, maximum stock limits). The read side provides a dashboard view with product name, current stock, stock status (Low/Medium/High), and last restocked date -- all in a single flat query.

### Exercise 3: Multi-View Read Models

Extend the e-commerce example to have three different read models: (1) a product list view with minimal data for catalog pages, (2) a product detail view with full information, and (3) a product analytics view with sales counts and revenue. Demonstrate how all three are updated from the same write events.

---

## What Is Next?

CQRS separates how you read and write data, but both sides still store the current state. The next chapter introduces **Event Sourcing**, where instead of storing the current state, you store the sequence of events that led to that state. Event Sourcing and CQRS are natural partners: events from the write side rebuild the read model. Together, they provide a complete audit trail, the ability to replay history, and powerful debugging capabilities.
