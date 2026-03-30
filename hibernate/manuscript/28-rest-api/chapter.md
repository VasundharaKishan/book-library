# Chapter 28: Building a Complete REST API

---

## Learning Goals

By the end of this chapter, you will be able to:

- Design a complete REST API with proper HTTP methods and status codes
- Build CRUD endpoints with Spring Boot, JPA, and Hibernate
- Apply all the patterns from previous chapters in one cohesive application
- Use request/response DTOs with validation
- Implement pagination and sorting in API endpoints
- Add a global exception handler for consistent error responses
- Document the API with OpenAPI/Swagger
- Test endpoints with MockMvc
- Follow REST best practices for resource naming and response structure

---

## API Design

We will build a **Product Management API** that demonstrates all the patterns from this book.

```
API Endpoints:
+------------------------------------------------------------------+
|                                                                   |
|  Products:                                                        |
|  GET    /api/products              List (paginated, sortable)     |
|  GET    /api/products/{id}         Get one by ID                  |
|  POST   /api/products              Create new product             |
|  PUT    /api/products/{id}         Full update                    |
|  PATCH  /api/products/{id}         Partial update                 |
|  DELETE /api/products/{id}         Delete                         |
|  GET    /api/products/search       Search with filters            |
|                                                                   |
|  Categories:                                                      |
|  GET    /api/categories            List all categories            |
|  POST   /api/categories            Create category                |
|  GET    /api/categories/{id}/products  Products by category       |
|                                                                   |
|  HTTP Status Codes:                                               |
|  200 OK              Successful GET, PUT, PATCH                   |
|  201 Created         Successful POST                              |
|  204 No Content      Successful DELETE                            |
|  400 Bad Request     Validation error                             |
|  404 Not Found       Resource does not exist                      |
|  409 Conflict        Duplicate or concurrent update               |
|  500 Internal Error  Unexpected server error                      |
+------------------------------------------------------------------+
```

---

## Entity Layer

```java
@Entity
@Table(name = "categories")
public class Category extends BaseEntity {

    @NotBlank
    @Column(nullable = false, unique = true, length = 100)
    private String name;

    @Size(max = 500)
    private String description;

    @OneToMany(mappedBy = "category")
    private List<Product> products = new ArrayList<>();

    protected Category() {}

    public Category(String name, String description) {
        this.name = name;
        this.description = description;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public List<Product> getProducts() { return Collections.unmodifiableList(products); }
}
```

```java
@Entity
@Table(name = "products", indexes = {
    @Index(name = "idx_product_category", columnList = "category_id"),
    @Index(name = "idx_product_sku", columnList = "sku"),
    @Index(name = "idx_product_active", columnList = "active")
})
public class Product extends BaseEntity {

    @NotBlank
    @Column(nullable = false, length = 200)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @NotNull
    @Positive
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @NotBlank
    @Column(nullable = false, unique = true, length = 50)
    private String sku;

    @PositiveOrZero
    @Column(name = "stock_quantity", nullable = false)
    private int stockQuantity;

    @Column(nullable = false)
    private boolean active = true;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private Category category;

    protected Product() {}

    public Product(String name, String description, BigDecimal price,
                   String sku, int stockQuantity) {
        this.name = name;
        this.description = description;
        this.price = price;
        this.sku = sku;
        this.stockQuantity = stockQuantity;
    }

    // Getters and setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }
    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }
    public int getStockQuantity() { return stockQuantity; }
    public void setStockQuantity(int stockQuantity) { this.stockQuantity = stockQuantity; }
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
    public Category getCategory() { return category; }
    public void setCategory(Category category) { this.category = category; }
}
```

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Version
    private Integer version;

    public Long getId() { return id; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public Integer getVersion() { return version; }
}
```

---

## DTO Layer

```java
// === Request DTOs ===

public class CreateProductRequest {

    @NotBlank(message = "Product name is required")
    @Size(min = 2, max = 200, message = "Name must be between 2 and 200 characters")
    private String name;

    @Size(max = 2000, message = "Description must be at most 2000 characters")
    private String description;

    @NotNull(message = "Price is required")
    @Positive(message = "Price must be positive")
    @Digits(integer = 8, fraction = 2, message = "Price format: up to 8 digits and 2 decimals")
    private BigDecimal price;

    @NotBlank(message = "SKU is required")
    @Size(min = 3, max = 50, message = "SKU must be between 3 and 50 characters")
    private String sku;

    @NotNull(message = "Stock quantity is required")
    @PositiveOrZero(message = "Stock cannot be negative")
    private Integer stockQuantity;

    private Long categoryId;

    // Getters and setters...
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }
    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }
    public Integer getStockQuantity() { return stockQuantity; }
    public void setStockQuantity(Integer stockQuantity) { this.stockQuantity = stockQuantity; }
    public Long getCategoryId() { return categoryId; }
    public void setCategoryId(Long categoryId) { this.categoryId = categoryId; }
}

public class UpdateProductRequest {

    @Size(min = 2, max = 200)
    private String name;           // All fields optional for partial update

    @Size(max = 2000)
    private String description;

    @Positive
    private BigDecimal price;

    @PositiveOrZero
    private Integer stockQuantity;

    private Boolean active;

    private Long categoryId;

    // Getters and setters...
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }
    public Integer getStockQuantity() { return stockQuantity; }
    public void setStockQuantity(Integer stockQuantity) { this.stockQuantity = stockQuantity; }
    public Boolean getActive() { return active; }
    public void setActive(Boolean active) { this.active = active; }
    public Long getCategoryId() { return categoryId; }
    public void setCategoryId(Long categoryId) { this.categoryId = categoryId; }
}
```

```java
// === Response DTOs ===

public class ProductResponse {

    private Long id;
    private String name;
    private String description;
    private BigDecimal price;
    private String sku;
    private int stockQuantity;
    private boolean active;
    private String categoryName;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public ProductResponse() {}

    public ProductResponse(Long id, String name, String description, BigDecimal price,
                           String sku, int stockQuantity, boolean active,
                           String categoryName, LocalDateTime createdAt,
                           LocalDateTime updatedAt) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.price = price;
        this.sku = sku;
        this.stockQuantity = stockQuantity;
        this.active = active;
        this.categoryName = categoryName;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    // Getters...
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public BigDecimal getPrice() { return price; }
    public String getSku() { return sku; }
    public int getStockQuantity() { return stockQuantity; }
    public boolean isActive() { return active; }
    public String getCategoryName() { return categoryName; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}

// Lightweight list item
public interface ProductListProjection {
    Long getId();
    String getName();
    BigDecimal getPrice();
    String getSku();
    int getStockQuantity();
    boolean getActive();
}
```

---

## Repository Layer

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long>,
        JpaSpecificationExecutor<Product> {

    boolean existsBySku(String sku);
    boolean existsBySkuAndIdNot(String sku, Long id);

    @EntityGraph(attributePaths = {"category"})
    Optional<Product> findWithCategoryById(Long id);

    @EntityGraph(attributePaths = {"category"})
    Page<Product> findByActive(boolean active, Pageable pageable);

    Page<ProductListProjection> findProjectedByActive(boolean active, Pageable pageable);

    @Query("SELECT p FROM Product p WHERE p.category.id = :categoryId AND p.active = true")
    Page<Product> findByCategoryId(@Param("categoryId") Long categoryId, Pageable pageable);
}

@Repository
public interface CategoryRepository extends JpaRepository<Category, Long> {

    boolean existsByName(String name);
    Optional<Category> findByName(String name);
}
```

---

## Service Layer

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

    @Transactional
    public ProductResponse create(CreateProductRequest request) {
        if (productRepository.existsBySku(request.getSku())) {
            throw new DuplicateResourceException("Product", "SKU", request.getSku());
        }

        Product product = new Product(
            request.getName(),
            request.getDescription(),
            request.getPrice(),
            request.getSku(),
            request.getStockQuantity()
        );

        if (request.getCategoryId() != null) {
            Category category = categoryRepository.findById(request.getCategoryId())
                .orElseThrow(() -> new ResourceNotFoundException(
                    "Category", request.getCategoryId()));
            product.setCategory(category);
        }

        Product saved = productRepository.save(product);
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public ProductResponse getById(Long id) {
        Product product = productRepository.findWithCategoryById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product", id));
        return toResponse(product);
    }

    @Transactional(readOnly = true)
    public Page<ProductResponse> getAll(Pageable pageable) {
        return productRepository.findByActive(true, pageable)
            .map(this::toResponse);
    }

    @Transactional(readOnly = true)
    public Page<ProductResponse> search(String name, Long categoryId,
                                         BigDecimal minPrice, BigDecimal maxPrice,
                                         Pageable pageable) {
        Specification<Product> spec = Specification.where(null);

        if (name != null && !name.isBlank()) {
            spec = spec.and((root, query, cb) ->
                cb.like(cb.lower(root.get("name")), "%" + name.toLowerCase() + "%"));
        }
        if (categoryId != null) {
            spec = spec.and((root, query, cb) ->
                cb.equal(root.get("category").get("id"), categoryId));
        }
        if (minPrice != null) {
            spec = spec.and((root, query, cb) ->
                cb.greaterThanOrEqualTo(root.get("price"), minPrice));
        }
        if (maxPrice != null) {
            spec = spec.and((root, query, cb) ->
                cb.lessThanOrEqualTo(root.get("price"), maxPrice));
        }
        spec = spec.and((root, query, cb) -> cb.isTrue(root.get("active")));

        return productRepository.findAll(spec, pageable).map(this::toResponse);
    }

    @Transactional
    public ProductResponse update(Long id, UpdateProductRequest request) {
        Product product = productRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product", id));

        if (request.getName() != null) product.setName(request.getName());
        if (request.getDescription() != null) product.setDescription(request.getDescription());
        if (request.getPrice() != null) product.setPrice(request.getPrice());
        if (request.getStockQuantity() != null) product.setStockQuantity(request.getStockQuantity());
        if (request.getActive() != null) product.setActive(request.getActive());

        if (request.getCategoryId() != null) {
            Category category = categoryRepository.findById(request.getCategoryId())
                .orElseThrow(() -> new ResourceNotFoundException(
                    "Category", request.getCategoryId()));
            product.setCategory(category);
        }

        return toResponse(product);
    }

    @Transactional
    public void delete(Long id) {
        if (!productRepository.existsById(id)) {
            throw new ResourceNotFoundException("Product", id);
        }
        productRepository.deleteById(id);
    }

    private ProductResponse toResponse(Product product) {
        return new ProductResponse(
            product.getId(),
            product.getName(),
            product.getDescription(),
            product.getPrice(),
            product.getSku(),
            product.getStockQuantity(),
            product.isActive(),
            product.getCategory() != null ? product.getCategory().getName() : null,
            product.getCreatedAt(),
            product.getUpdatedAt()
        );
    }
}
```

---

## Controller Layer

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping
    public Page<ProductResponse> getAll(Pageable pageable) {
        return productService.getAll(pageable);
    }

    @GetMapping("/{id}")
    public ProductResponse getById(@PathVariable Long id) {
        return productService.getById(id);
    }

    @GetMapping("/search")
    public Page<ProductResponse> search(
            @RequestParam(required = false) String name,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) BigDecimal minPrice,
            @RequestParam(required = false) BigDecimal maxPrice,
            Pageable pageable) {
        return productService.search(name, categoryId, minPrice, maxPrice, pageable);
    }

    @PostMapping
    public ResponseEntity<ProductResponse> create(
            @Valid @RequestBody CreateProductRequest request) {
        ProductResponse response = productService.create(request);
        URI location = URI.create("/api/products/" + response.getId());
        return ResponseEntity.created(location).body(response);
    }

    @PutMapping("/{id}")
    public ProductResponse update(
            @PathVariable Long id,
            @Valid @RequestBody UpdateProductRequest request) {
        return productService.update(id, request);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        productService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

```
Request/Response Flow:
+------------------------------------------------------------------+
|                                                                   |
|  POST /api/products                                               |
|  { "name": "Widget", "price": 19.99, "sku": "WDG-001",          |
|    "stockQuantity": 100, "categoryId": 1 }                       |
|       |                                                           |
|       v                                                           |
|  Controller: @Valid validates request DTO                         |
|       |                                                           |
|       v                                                           |
|  Service: checks SKU uniqueness, loads category, saves entity    |
|       |                                                           |
|       v                                                           |
|  Response: 201 Created                                            |
|  Location: /api/products/42                                       |
|  {                                                                |
|    "id": 42,                                                      |
|    "name": "Widget",                                              |
|    "price": 19.99,                                                |
|    "sku": "WDG-001",                                              |
|    "stockQuantity": 100,                                          |
|    "active": true,                                                |
|    "categoryName": "Electronics",                                 |
|    "createdAt": "2025-09-15T14:30:00",                            |
|    "updatedAt": "2025-09-15T14:30:00"                             |
|  }                                                                |
+------------------------------------------------------------------+
```

---

## Global Exception Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex, HttpServletRequest request) {
        return buildResponse(404, ex.getErrorCode(), ex.getMessage(), request);
    }

    @ExceptionHandler(DuplicateResourceException.class)
    public ResponseEntity<ErrorResponse> handleDuplicate(
            DuplicateResourceException ex, HttpServletRequest request) {
        return buildResponse(409, ex.getErrorCode(), ex.getMessage(), request);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            MethodArgumentNotValidException ex, HttpServletRequest request) {
        Map<String, String> fieldErrors = new LinkedHashMap<>();
        ex.getBindingResult().getFieldErrors()
            .forEach(fe -> fieldErrors.put(fe.getField(), fe.getDefaultMessage()));

        ErrorResponse error = new ErrorResponse(400, "VALIDATION_FAILED",
            "Request validation failed", request.getRequestURI());
        error.setFieldErrors(fieldErrors);
        return ResponseEntity.badRequest().body(error);
    }

    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<ErrorResponse> handleDataIntegrity(
            DataIntegrityViolationException ex, HttpServletRequest request) {
        return buildResponse(409, "DATA_INTEGRITY",
            "A data integrity constraint was violated", request);
    }

    @ExceptionHandler(OptimisticLockingFailureException.class)
    public ResponseEntity<ErrorResponse> handleOptimisticLock(
            OptimisticLockingFailureException ex, HttpServletRequest request) {
        return buildResponse(409, "CONCURRENT_UPDATE",
            "Record was modified by another user. Please refresh.", request);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneral(
            Exception ex, HttpServletRequest request) {
        log.error("Unhandled exception at {}", request.getRequestURI(), ex);
        return buildResponse(500, "INTERNAL_ERROR",
            "An unexpected error occurred", request);
    }

    private ResponseEntity<ErrorResponse> buildResponse(
            int status, String code, String message, HttpServletRequest request) {
        ErrorResponse error = new ErrorResponse(status, code, message,
            request.getRequestURI());
        return ResponseEntity.status(status).body(error);
    }
}
```

---

## Testing with MockMvc

```java
@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void createProduct_validRequest_returns201() throws Exception {
        CreateProductRequest request = new CreateProductRequest();
        request.setName("Widget");
        request.setPrice(new BigDecimal("19.99"));
        request.setSku("WDG-001");
        request.setStockQuantity(100);

        ProductResponse response = new ProductResponse(
            1L, "Widget", null, new BigDecimal("19.99"), "WDG-001",
            100, true, null, LocalDateTime.now(), LocalDateTime.now());

        when(productService.create(any())).thenReturn(response);

        mockMvc.perform(post("/api/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.name").value("Widget"))
            .andExpect(jsonPath("$.sku").value("WDG-001"))
            .andExpect(header().string("Location", "/api/products/1"));
    }

    @Test
    void createProduct_invalidRequest_returns400() throws Exception {
        CreateProductRequest request = new CreateProductRequest();
        // Missing all required fields

        mockMvc.perform(post("/api/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.error").value("VALIDATION_FAILED"))
            .andExpect(jsonPath("$.fieldErrors.name").value("Product name is required"))
            .andExpect(jsonPath("$.fieldErrors.price").value("Price is required"));
    }

    @Test
    void getById_notFound_returns404() throws Exception {
        when(productService.getById(999L))
            .thenThrow(new ResourceNotFoundException("Product", 999L));

        mockMvc.perform(get("/api/products/999"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.error").value("NOT_FOUND"))
            .andExpect(jsonPath("$.message").value("Product with id 999 not found"));
    }

    @Test
    void getAll_returnsPaginatedResults() throws Exception {
        List<ProductResponse> products = List.of(
            new ProductResponse(1L, "Widget", null, new BigDecimal("19.99"),
                "WDG-001", 100, true, "Electronics",
                LocalDateTime.now(), LocalDateTime.now())
        );
        Page<ProductResponse> page = new PageImpl<>(products, PageRequest.of(0, 20), 1);

        when(productService.getAll(any())).thenReturn(page);

        mockMvc.perform(get("/api/products")
                .param("page", "0")
                .param("size", "20")
                .param("sort", "name,asc"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.content").isArray())
            .andExpect(jsonPath("$.content[0].name").value("Widget"))
            .andExpect(jsonPath("$.totalElements").value(1));
    }

    @Test
    void delete_returnsNoContent() throws Exception {
        doNothing().when(productService).delete(1L);

        mockMvc.perform(delete("/api/products/1"))
            .andExpect(status().isNoContent());
    }
}
```

---

## Application Configuration

```properties
# application.properties

# Database
spring.datasource.url=jdbc:h2:mem:productdb
spring.datasource.driver-class-name=org.h2.Driver
spring.h2.console.enabled=true

# JPA / Hibernate
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.open-in-view=false
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.default_batch_fetch_size=16

# Flyway
spring.flyway.enabled=true

# Logging (development)
logging.level.org.hibernate.SQL=DEBUG

# Jackson
spring.jackson.serialization.write-dates-as-timestamps=false

# Pagination defaults
spring.data.web.pageable.default-page-size=20
spring.data.web.pageable.max-page-size=100
```

---

## Patterns Applied

```
Patterns from This Book Used in the API:
+------------------------------------------------------------------+
|                                                                   |
|  Ch  Pattern                      Applied In                      |
|  ----------------------------------------------------------------|
|  4   JPA annotations              Entity mappings                 |
|  6   CRUD operations              Service create/read/update/del  |
|  7   Derived queries              Repository methods              |
|  10  Specifications               Search with dynamic filters     |
|  11  Pagination                   Page<T> in list endpoints       |
|  13  @ManyToOne relationship      Product -> Category             |
|  17  Persistence context          Dirty checking in update()     |
|  18  @EntityGraph                 Eager loading for detail view   |
|  20  @Transactional               Service method boundaries      |
|  22  Bean Validation              @Valid on request DTOs          |
|  23  DTOs and Projections         Request/Response DTOs           |
|  24  Layered architecture         Controller/Service/Repository   |
|  25  Exception handling           @ControllerAdvice               |
|  26  Flyway                       ddl-auto=validate               |
|  27  Performance                  Batch size, OSIV=false          |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Returning entities from controllers**: Always map to response DTOs. Entities expose internal structure, cause circular references, and trigger lazy loading issues.

2. **Putting validation in the service instead of the DTO**: Use `@Valid` on request DTOs in the controller. This catches errors before reaching the service.

3. **Not using readOnly on GET methods**: All read operations should use `@Transactional(readOnly = true)` for performance.

4. **Hardcoding page size without limits**: Always configure `max-page-size` to prevent `?size=1000000` requests.

5. **Inconsistent error responses**: Every error should follow the same format (status, error code, message, path, timestamp).

---

## Best Practices

1. **Separate request and response DTOs**: Different fields, different validation, different purposes.
2. **Use 201 Created with Location header for POST**: Tell the client where to find the new resource.
3. **Use 204 No Content for DELETE**: Acknowledge success without returning data.
4. **Use Pageable for all list endpoints**: Every list can grow. Always paginate.
5. **Test every endpoint and error case**: Happy paths, validation errors, not found, duplicates.
6. **Disable open-in-view**: Force all data loading to happen in the service layer.

---

## Summary

This chapter brought together all the patterns from the book into a complete, production-quality REST API:

- **Entities** with proper annotations, relationships, validation, and a shared BaseEntity.
- **DTOs** for request validation and response formatting, never exposing entities.
- **Repositories** with derived methods, @EntityGraph, projections, and Specifications.
- **Services** with business logic, transaction management, and entity-DTO mapping.
- **Controllers** with proper HTTP methods, status codes, and validated request bodies.
- **Global exception handling** for consistent, informative error responses.
- **Tests** with MockMvc for every endpoint and error scenario.
- **Configuration** with OSIV disabled, Flyway, batch processing, and pagination limits.

---

## Interview Questions

**Q1: What HTTP status codes should a REST API return for CRUD operations?**

GET: 200 OK. POST: 201 Created (with Location header). PUT/PATCH: 200 OK (with updated resource). DELETE: 204 No Content. Errors: 400 for validation, 404 for not found, 409 for conflicts, 500 for server errors.

**Q2: Why should you use separate DTOs for request and response?**

Request DTOs have validation annotations and only include fields the client can set. Response DTOs include computed fields (timestamps, category names) and exclude sensitive data. They serve different purposes and change independently.

**Q3: How do you implement search with multiple optional filters?**

Use Spring Data Specifications (JpaSpecificationExecutor). Build predicates conditionally for each non-null filter parameter. Combine with `Specification.and()`. Pass to `repository.findAll(spec, pageable)`.

**Q4: What is the benefit of using @EntityGraph in the detail endpoint but not the list endpoint?**

The detail endpoint needs full data (category name, etc.), so @EntityGraph prevents N+1. The list endpoint may use a lighter projection that does not need relationships, avoiding unnecessary JOINs and data transfer.

---

## Practice Exercises

**Exercise 1: Complete CRUD API**
Build the Product Management API from this chapter. Test all endpoints with an HTTP client (curl, Postman, or HTTPie).

**Exercise 2: Add Category CRUD**
Add full CRUD endpoints for Categories. Include listing products by category with pagination.

**Exercise 3: Search Endpoint**
Implement the `/api/products/search` endpoint with filters for name, category, price range, and active status. Test with various filter combinations.

**Exercise 4: Test Coverage**
Write MockMvc tests for every endpoint: create (valid/invalid), get (found/not found), update, delete, list with pagination, search with filters.

**Exercise 5: API Documentation**
Add SpringDoc OpenAPI (`springdoc-openapi-starter-webmvc-ui`) dependency. Add `@Operation` and `@ApiResponse` annotations. Access the Swagger UI at `/swagger-ui.html`.

---

## What Is Next?

In the next chapter, we will build a **complete capstone project** — a Library Management System with complex entity relationships, full CRUD APIs, search and filtering, Flyway migrations, and comprehensive tests. This will be the culmination of everything you have learned.
