# Chapter 19: Layered Architecture -- The Three-Tier Foundation

## What You Will Learn

- The three-tier layered architecture pattern: Presentation, Business, and Data
- What each layer is responsible for and what it should never do
- How layers communicate through well-defined interfaces
- Benefits and drawbacks of the layered approach
- A complete Spring Boot example showing all three layers
- A complete Python (Flask) example for comparison
- When layered architecture is the right choice and when to consider alternatives

## Why This Chapter Matters

Layered architecture is the most widely used architectural pattern in the industry. When someone says "we have a controller, a service, and a repository," they are describing layered architecture. It is the default pattern for most web applications, enterprise systems, and APIs. Understanding it deeply is essential because it is likely the pattern you will work with most, and it is also the pattern whose limitations drive the adoption of more advanced architectures like hexagonal and clean architecture.

---

## 19.1 What Is Layered Architecture?

Layered architecture divides an application into horizontal layers, each with a distinct responsibility. Each layer only communicates with the layer directly below it.

```
  +-----------------------------------------------------+
  |                                                      |
  |              PRESENTATION LAYER                      |
  |         (Controllers, Views, API endpoints)          |
  |                                                      |
  |                      | calls                        |
  |                      v                               |
  +-----------------------------------------------------+
  |                                                      |
  |              BUSINESS LOGIC LAYER                    |
  |         (Services, Domain rules, Validation)         |
  |                                                      |
  |                      | calls                        |
  |                      v                               |
  +-----------------------------------------------------+
  |                                                      |
  |              DATA ACCESS LAYER                       |
  |         (Repositories, DAOs, ORM, SQL)               |
  |                                                      |
  +-----------------------------------------------------+
  |                                                      |
  |              DATABASE                                |
  |         (PostgreSQL, MySQL, MongoDB)                 |
  |                                                      |
  +-----------------------------------------------------+
```

### The Core Rule

Each layer depends only on the layer directly below it. The Presentation layer calls the Business layer. The Business layer calls the Data Access layer. No layer reaches past its neighbor.

```
  +-----------------------------------------------------------+
  |              ALLOWED             |    NOT ALLOWED          |
  +-----------------------------------------------------------+
  |  Presentation -> Business        | Presentation -> Data   |
  |  Business -> Data Access         | Data Access -> Business|
  |                                  | Business -> Presentation|
  +-----------------------------------------------------------+
```

---

## 19.2 The Presentation Layer

### Responsibility

The Presentation layer handles all interaction with the outside world. For a web application, this means HTTP requests and responses. For a desktop app, this means UI events and screen updates.

### What It Should Do

- Accept incoming requests (HTTP, CLI, events)
- Validate input format (is it valid JSON? are required fields present?)
- Call the appropriate business logic
- Format the response for the client
- Handle HTTP status codes, content types, headers

### What It Should NOT Do

- Contain business rules or calculations
- Access the database directly
- Know about SQL, table names, or data formats
- Make decisions about data processing

### Spring Boot Controller (Java)

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping
    public ResponseEntity<List<ProductResponse>> getAllProducts() {
        List<Product> products = productService.findAll();
        List<ProductResponse> response = products.stream()
                .map(ProductResponse::from)
                .collect(Collectors.toList());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProductResponse> getProduct(@PathVariable Long id) {
        Product product = productService.findById(id);
        return ResponseEntity.ok(ProductResponse.from(product));
    }

    @PostMapping
    public ResponseEntity<ProductResponse> createProduct(
            @Valid @RequestBody CreateProductRequest request) {
        Product product = productService.create(
                request.getName(),
                request.getPrice(),
                request.getCategory()
        );
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ProductResponse.from(product));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

### Flask Controller (Python)

```python
from flask import Flask, request, jsonify
from product_service import ProductService

app = Flask(__name__)
product_service = ProductService()


@app.route("/api/products", methods=["GET"])
def get_all_products():
    products = product_service.find_all()
    return jsonify([p.to_dict() for p in products])


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = product_service.find_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict())


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json()
    if not data.get("name") or not data.get("price"):
        return jsonify({"error": "Name and price are required"}), 400

    product = product_service.create(
        name=data["name"],
        price=data["price"],
        category=data.get("category", "general")
    )
    return jsonify(product.to_dict()), 201


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product_service.delete(product_id)
    return "", 204
```

---

## 19.3 The Business Logic Layer

### Responsibility

The Business Logic layer contains the rules that define what your application does. It is the heart of the system -- the code that would exist regardless of whether the interface is a web app, mobile app, or CLI.

### What It Should Do

- Enforce business rules and constraints
- Orchestrate operations across multiple data sources
- Perform calculations, transformations, and validations
- Define the domain model (entities, value objects)

### What It Should NOT Do

- Know about HTTP, HTML, or any presentation format
- Import web framework classes
- Handle request parsing or response formatting
- Contain SQL queries or direct database access

### Service Class (Java)

```java
@Service
public class ProductService {

    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;

    public ProductService(ProductRepository productRepository,
                          CategoryRepository categoryRepository) {
        this.productRepository = productRepository;
        this.categoryRepository = categoryRepository;
    }

    public List<Product> findAll() {
        return productRepository.findAll();
    }

    public Product findById(Long id) {
        return productRepository.findById(id)
                .orElseThrow(() -> new ProductNotFoundException(
                        "Product not found: " + id));
    }

    public Product create(String name, double price, String categoryName) {
        if (price <= 0) {
            throw new InvalidProductException("Price must be positive");
        }
        if (name == null || name.trim().isEmpty()) {
            throw new InvalidProductException("Name cannot be empty");
        }
        if (productRepository.existsByName(name)) {
            throw new DuplicateProductException("Product already exists: " + name);
        }

        Category category = categoryRepository.findByName(categoryName)
                .orElseGet(() -> categoryRepository.save(new Category(categoryName)));

        Product product = new Product(name, price, category);
        return productRepository.save(product);
    }

    public void delete(Long id) {
        Product product = findById(id);
        if (product.hasActiveOrders()) {
            throw new BusinessRuleException(
                    "Cannot delete product with active orders");
        }
        productRepository.delete(product);
    }

    public Product applyDiscount(Long productId, double discountPercent) {
        if (discountPercent < 0 || discountPercent > 50) {
            throw new InvalidProductException(
                    "Discount must be between 0% and 50%");
        }
        Product product = findById(productId);
        product.applyDiscount(discountPercent);
        return productRepository.save(product);
    }
}
```

### Service Class (Python)

```python
class ProductService:

    def __init__(self, product_repo=None, category_repo=None):
        self.product_repo = product_repo or ProductRepository()
        self.category_repo = category_repo or CategoryRepository()

    def find_all(self):
        return self.product_repo.find_all()

    def find_by_id(self, product_id):
        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product not found: {product_id}")
        return product

    def create(self, name, price, category="general"):
        if price <= 0:
            raise InvalidProductError("Price must be positive")
        if not name or not name.strip():
            raise InvalidProductError("Name cannot be empty")
        if self.product_repo.exists_by_name(name):
            raise DuplicateProductError(f"Product already exists: {name}")

        cat = self.category_repo.find_by_name(category)
        if not cat:
            cat = self.category_repo.save(Category(category))

        product = Product(name=name, price=price, category=cat)
        return self.product_repo.save(product)

    def delete(self, product_id):
        product = self.find_by_id(product_id)
        if product.has_active_orders():
            raise BusinessRuleError("Cannot delete product with active orders")
        self.product_repo.delete(product)

    def apply_discount(self, product_id, discount_percent):
        if not 0 <= discount_percent <= 50:
            raise InvalidProductError("Discount must be between 0% and 50%")
        product = self.find_by_id(product_id)
        product.apply_discount(discount_percent)
        return self.product_repo.save(product)
```

### The Domain Model

```java
public class Product {
    private Long id;
    private String name;
    private double price;
    private double originalPrice;
    private Category category;
    private List<Order> activeOrders;

    public Product(String name, double price, Category category) {
        this.name = name;
        this.price = price;
        this.originalPrice = price;
        this.category = category;
        this.activeOrders = new ArrayList<>();
    }

    public void applyDiscount(double percent) {
        this.price = originalPrice * (1 - percent / 100);
    }

    public boolean hasActiveOrders() {
        return !activeOrders.isEmpty();
    }

    // Getters...
}
```

---

## 19.4 The Data Access Layer

### Responsibility

The Data Access layer handles all communication with data storage systems. It translates between domain objects and database records.

### What It Should Do

- Execute database queries (SQL, NoSQL, etc.)
- Map database rows to domain objects and vice versa
- Handle connection pooling and transaction management
- Provide a clean interface to the business layer

### What It Should NOT Do

- Contain business rules
- Make decisions about which data to return based on business logic
- Format data for the UI
- Know about HTTP or any presentation concern

### Repository Interface and Implementation (Java / Spring Data)

```java
// Interface (used by the business layer)
public interface ProductRepository {
    List<Product> findAll();
    Optional<Product> findById(Long id);
    boolean existsByName(String name);
    Product save(Product product);
    void delete(Product product);
}

// Implementation using Spring Data JPA
@Repository
public class JpaProductRepository implements ProductRepository {

    private final SpringDataProductRepository springRepo;

    public JpaProductRepository(SpringDataProductRepository springRepo) {
        this.springRepo = springRepo;
    }

    @Override
    public List<Product> findAll() {
        return springRepo.findAll().stream()
                .map(this::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public Optional<Product> findById(Long id) {
        return springRepo.findById(id).map(this::toDomain);
    }

    @Override
    public boolean existsByName(String name) {
        return springRepo.existsByName(name);
    }

    @Override
    public Product save(Product product) {
        ProductEntity entity = toEntity(product);
        ProductEntity saved = springRepo.save(entity);
        return toDomain(saved);
    }

    @Override
    public void delete(Product product) {
        springRepo.deleteById(product.getId());
    }

    private Product toDomain(ProductEntity entity) {
        return new Product(entity.getId(), entity.getName(),
                entity.getPrice(), entity.getCategory());
    }

    private ProductEntity toEntity(Product product) {
        return new ProductEntity(product.getId(), product.getName(),
                product.getPrice(), product.getCategory());
    }
}

// Spring Data interface
interface SpringDataProductRepository extends JpaRepository<ProductEntity, Long> {
    boolean existsByName(String name);
}
```

### Repository (Python with SQLAlchemy)

```python
from sqlalchemy.orm import Session
from models import ProductModel


class ProductRepository:

    def __init__(self, session: Session = None):
        self.session = session or get_default_session()

    def find_all(self):
        rows = self.session.query(ProductModel).all()
        return [self._to_domain(row) for row in rows]

    def find_by_id(self, product_id):
        row = self.session.query(ProductModel).get(product_id)
        return self._to_domain(row) if row else None

    def exists_by_name(self, name):
        return self.session.query(ProductModel).filter_by(name=name).count() > 0

    def save(self, product):
        entity = self._to_entity(product)
        self.session.add(entity)
        self.session.commit()
        return self._to_domain(entity)

    def delete(self, product):
        entity = self.session.query(ProductModel).get(product.id)
        if entity:
            self.session.delete(entity)
            self.session.commit()

    def _to_domain(self, entity):
        return Product(
            id=entity.id,
            name=entity.name,
            price=entity.price,
            category=entity.category
        )

    def _to_entity(self, product):
        return ProductModel(
            id=product.id,
            name=product.name,
            price=product.price,
            category=product.category
        )
```

---

## 19.5 Complete Spring Boot Example: Project Structure

Here is how a layered architecture looks as a project structure:

```
  src/main/java/com/example/shop/
  +-- controller/                  <-- Presentation Layer
  |   +-- ProductController.java
  |   +-- OrderController.java
  |   +-- dto/
  |       +-- CreateProductRequest.java
  |       +-- ProductResponse.java
  |
  +-- service/                     <-- Business Logic Layer
  |   +-- ProductService.java
  |   +-- OrderService.java
  |   +-- exception/
  |       +-- ProductNotFoundException.java
  |       +-- InvalidProductException.java
  |
  +-- domain/                      <-- Domain Model
  |   +-- Product.java
  |   +-- Order.java
  |   +-- Category.java
  |
  +-- repository/                  <-- Data Access Layer
  |   +-- ProductRepository.java   (interface)
  |   +-- JpaProductRepository.java (implementation)
  |   +-- entity/
  |       +-- ProductEntity.java   (JPA entity)
  |
  +-- config/                      <-- Configuration
      +-- AppConfig.java
```

### Request Flow Through the Layers

```
  HTTP Request: POST /api/products
  {"name": "Widget", "price": 9.99, "category": "tools"}

       |
       v
  +------------------+
  | ProductController |  1. Parse JSON into CreateProductRequest
  |  (Presentation)   |  2. Call productService.create(...)
  +--------+---------+
           |
           v
  +------------------+
  | ProductService    |  3. Validate business rules
  |  (Business)       |  4. Create Product domain object
  |                   |  5. Call repository.save(product)
  +--------+---------+
           |
           v
  +------------------+
  | JpaProductRepo    |  6. Convert Product to ProductEntity
  |  (Data Access)    |  7. Execute INSERT INTO products ...
  |                   |  8. Return saved Product
  +--------+---------+
           |
           v
  +------------------+
  | ProductService    |  9. Return Product to controller
  +--------+---------+
           |
           v
  +------------------+
  | ProductController |  10. Convert Product to ProductResponse
  |                   |  11. Return HTTP 201 Created
  +------------------+

       |
       v
  HTTP Response: 201 Created
  {"id": 42, "name": "Widget", "price": 9.99}
```

---

## 19.6 Benefits of Layered Architecture

```
  +-------------------------------------------------------+
  |                    BENEFITS                            |
  +-------------------------------------------------------+
  |                                                        |
  |  1. SIMPLICITY                                         |
  |     Easy to understand. Most developers already        |
  |     know it. Low learning curve.                       |
  |                                                        |
  |  2. SEPARATION OF CONCERNS                             |
  |     Each layer has a clear responsibility.              |
  |     Changes in one layer rarely affect others.         |
  |                                                        |
  |  3. TESTABILITY                                        |
  |     Business logic can be tested independently         |
  |     by mocking the data access layer.                  |
  |                                                        |
  |  4. TEAM ORGANIZATION                                  |
  |     Different developers can work on different         |
  |     layers with minimal conflicts.                     |
  |                                                        |
  |  5. TECHNOLOGY FLEXIBILITY                             |
  |     You can change the database without touching       |
  |     the presentation layer.                            |
  |                                                        |
  +-------------------------------------------------------+
```

---

## 19.7 Drawbacks of Layered Architecture

```
  +-------------------------------------------------------+
  |                    DRAWBACKS                           |
  +-------------------------------------------------------+
  |                                                        |
  |  1. LAYER LEAKING                                      |
  |     Business logic creeps into controllers.            |
  |     SQL logic creeps into services.                    |
  |     Discipline is needed to keep layers clean.         |
  |                                                        |
  |  2. PASS-THROUGH LAYERS                                |
  |     Sometimes a controller just passes data to a       |
  |     service that passes it to a repository.            |
  |     The service layer adds no value.                   |
  |                                                        |
  |  3. DATABASE-DRIVEN DESIGN                             |
  |     The natural tendency is to design from the         |
  |     database up. This makes the domain model           |
  |     mirror the database schema instead of the          |
  |     business concepts.                                 |
  |                                                        |
  |  4. MONOLITHIC TENDENCY                                |
  |     Layers run in the same process. As the app         |
  |     grows, it becomes a large monolith.                |
  |                                                        |
  |  5. DEPENDENCY DIRECTION                               |
  |     Business logic depends on the data access          |
  |     layer, which violates the Dependency Rule          |
  |     from Clean Architecture (Chapter 18).              |
  |                                                        |
  +-------------------------------------------------------+
```

### The Dependency Problem

In traditional layered architecture, the business layer depends on the data access layer:

```
  Controller  -->  Service  -->  Repository (concrete class)
```

This means the business logic knows about the persistence technology. To fix this, use dependency inversion:

```
  Controller  -->  Service  -->  Repository (interface)
                                      ^
                                      |
                              JpaRepository (implementation)
```

Now the service depends on an abstraction, not a concrete implementation. This is how layered architecture evolves toward clean architecture.

---

## 19.8 Layer Leaking: The Most Common Problem

Layer leaking happens when code that belongs in one layer ends up in another.

### BEFORE: Business Logic in the Controller

```java
@PostMapping("/orders")
public ResponseEntity<String> createOrder(@RequestBody OrderRequest req) {
    // This business logic belongs in the SERVICE layer!
    double total = 0;
    for (Item item : req.getItems()) {
        Product p = productRepository.findById(item.getProductId());
        if (p.getStock() < item.getQuantity()) {
            return ResponseEntity.badRequest().body("Out of stock: " + p.getName());
        }
        total += p.getPrice() * item.getQuantity();
    }
    if (total > 1000) {
        total *= 0.95; // Discount
    }

    // This data access belongs in the REPOSITORY layer!
    jdbcTemplate.update("INSERT INTO orders (customer_id, total) VALUES (?, ?)",
            req.getCustomerId(), total);

    return ResponseEntity.ok("Order created");
}
```

### AFTER: Proper Layer Separation

```java
// Controller: only HTTP concerns
@PostMapping("/orders")
public ResponseEntity<OrderResponse> createOrder(@RequestBody OrderRequest req) {
    Order order = orderService.create(req.getCustomerId(), req.getItems());
    return ResponseEntity.status(HttpStatus.CREATED)
            .body(OrderResponse.from(order));
}

// Service: business logic
public Order create(Long customerId, List<OrderItem> items) {
    for (OrderItem item : items) {
        Product product = productRepository.findById(item.getProductId())
                .orElseThrow(() -> new ProductNotFoundException(item.getProductId()));
        if (product.getStock() < item.getQuantity()) {
            throw new InsufficientStockException(product.getName());
        }
    }

    double total = calculateTotal(items);
    Order order = new Order(customerId, items, total);
    return orderRepository.save(order);
}

private double calculateTotal(List<OrderItem> items) {
    double total = items.stream()
            .mapToDouble(i -> i.getPrice() * i.getQuantity())
            .sum();
    if (total > 1000) {
        total *= 0.95;
    }
    return total;
}
```

---

## Common Mistakes

1. **Putting business logic in controllers.** The controller's job is to handle HTTP, not to calculate discounts or validate business rules.
2. **Calling the repository from the controller.** Always go through the service layer, even if the service just passes the call through. This keeps your architecture consistent and makes it easy to add business logic later.
3. **Using JPA entities as API responses.** This couples your database schema to your API contract. Use DTOs (Data Transfer Objects) to decouple them.
4. **Creating one service per controller.** Services should be organized around business capabilities, not around UI needs. Multiple controllers can share the same service.
5. **Skipping the repository interface.** Always define a repository interface in the business layer. This lets you swap implementations and test with fakes.

---

## Best Practices

1. **Keep controllers thin.** Controllers should parse input, call a service, and format output. Nothing more.
2. **Keep services fat with business logic.** All business rules, validations, and orchestration belong here.
3. **Use DTOs at layer boundaries.** Do not let JPA entities, HTTP request objects, or database result sets leak across layers.
4. **Define repository interfaces in the business layer.** Implement them in the data access layer. This follows the Dependency Inversion Principle.
5. **Use exception handling across layers.** Business exceptions thrown by services should be caught by controllers and translated into appropriate HTTP responses.

---

## Quick Summary

| Layer | Responsibility | Example Classes |
|-------|---------------|----------------|
| Presentation | HTTP, input/output formatting | Controllers, DTOs, Views |
| Business Logic | Rules, validation, orchestration | Services, Domain objects |
| Data Access | Storage, retrieval, mapping | Repositories, DAOs, Entities |

---

## Key Points

- Layered architecture divides the application into Presentation, Business, and Data Access layers.
- Each layer has a single responsibility and communicates only with the layer directly below it.
- The pattern is simple, widely understood, and effective for most business applications.
- The main risk is layer leaking -- business logic in controllers or SQL in services.
- Using interfaces at layer boundaries enables dependency inversion and testability.

---

## Practice Questions

1. A developer puts a `SELECT` query directly in a controller method. Which architectural principle does this violate? Where should the query go?

2. Your service method returns a `ProductEntity` (a JPA-annotated class) directly to the controller, which serializes it to JSON. What problems could this cause?

3. Is it acceptable for the Presentation layer to bypass the Business layer and call the Data Access layer directly? When, if ever, might this be justified?

4. Compare the dependency direction in traditional layered architecture versus Clean Architecture. What is the key difference?

5. Your team has a service class with 50 methods covering users, orders, products, and reports. Which code smell from Chapter 14 does this exhibit? How would you fix it?

---

## Exercises

### Exercise 1: Layer Identification

For each of these code snippets, identify which layer it belongs in (Presentation, Business, or Data Access) and explain why:

```java
// Snippet A
if (order.getTotal() > 500 && customer.getLoyaltyYears() >= 2) {
    order.applyDiscount(0.10);
}

// Snippet B
@GetMapping("/users/{id}")
public ResponseEntity<UserDto> getUser(@PathVariable Long id) { ... }

// Snippet C
String sql = "SELECT * FROM products WHERE category = ? AND price < ?";
```

### Exercise 2: Build a Three-Layer Application

Build a simple "Task Manager" application with the following layers:

1. **Presentation**: REST endpoints for creating, listing, and completing tasks
2. **Business**: Validation (title not empty, due date in the future), status transitions (only "pending" tasks can be marked "complete")
3. **Data Access**: In-memory list storage (no real database needed)

Implement in either Java (Spring Boot) or Python (Flask). Verify that no layer violates its boundaries.

### Exercise 3: Find the Layer Leaks

Review this code and identify all layer violations:

```python
@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    # Check stock (should be in service)
    conn = sqlite3.connect("shop.db")
    cursor = conn.execute(
        "SELECT stock FROM products WHERE id = ?", (data["product_id"],))
    stock = cursor.fetchone()[0]
    if stock < data["quantity"]:
        return jsonify({"error": "Out of stock"}), 400

    # Calculate total (should be in service)
    total = data["price"] * data["quantity"] * 1.08

    # Save order (should be in repository)
    conn.execute("INSERT INTO orders (product_id, total) VALUES (?, ?)",
                 (data["product_id"], total))
    conn.commit()

    return jsonify({"total": total}), 201
```

Refactor it into proper layers.

---

## What Is Next?

Layered architecture is a solid foundation, but it has a significant limitation: the business layer depends on the data access layer. Chapter 20: Hexagonal Architecture solves this by inverting the dependency direction, placing the domain at the center and pushing all infrastructure to the edges. This makes the core business logic truly independent of databases, frameworks, and external services.
