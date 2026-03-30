# Chapter 16: Pagination and Sorting

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand why pagination and sorting are essential for any API
- Use `Pageable` and `PageRequest` to paginate query results
- Understand the difference between `Page` and `Slice`
- Sort data using the `Sort` class
- Auto-resolve `Pageable` parameters from HTTP request parameters
- Use `Page.map()` to transform paginated results
- Build complete paginated REST endpoints

## Why This Chapter Matters

Imagine you walk into a library and ask the librarian: "Give me every book you have." The librarian stares at you. The library has 50,000 books. Should they stack all 50,000 on the counter?

Of course not. Instead, the librarian would say: "Here are the first 20 books. When you are done, come back for the next 20."

This is exactly what pagination does for your API. Without pagination, a `GET /api/products` call on a database with 100,000 products would:
- Load all 100,000 records into memory
- Serialize them all into JSON
- Send a massive response over the network
- Make the browser or client process all of them at once

With pagination, you return 20 or 50 records at a time, along with metadata like "page 3 of 500." The client asks for exactly the data it needs.

Sorting is equally important. Users want to see products from cheapest to most expensive, or newest to oldest. Without sorting, data comes back in whatever order the database feels like returning it.

---

## How Pagination Works

```
Database has 50 products
Page size = 10

+--------+------------------------------------------+
| Page 0 | Products 1-10                            |   <-- First page
+--------+------------------------------------------+
| Page 1 | Products 11-20                           |
+--------+------------------------------------------+
| Page 2 | Products 21-30                           |
+--------+------------------------------------------+
| Page 3 | Products 31-40                           |
+--------+------------------------------------------+
| Page 4 | Products 41-50                           |   <-- Last page
+--------+------------------------------------------+

GET /api/products?page=0&size=10   ->  Returns products 1-10
GET /api/products?page=2&size=10   ->  Returns products 21-30
GET /api/products?page=4&size=10   ->  Returns products 41-50
```

**Important:** Pages are zero-indexed. The first page is page 0, not page 1.

---

## The Pageable Interface

`Pageable` is Spring Data's way of capturing pagination and sorting information. It holds three pieces of data:

```
+-----------------------------------+
|           Pageable                |
+-----------------------------------+
| page number  (which page?)        |
| page size    (how many per page?) |
| sort         (what order?)        |
+-----------------------------------+
```

### Creating Pageable with PageRequest

`PageRequest` is the most common way to create a `Pageable` object:

```java
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;

// Page 0 (first page), 10 items per page
Pageable pageable1 = PageRequest.of(0, 10);                  // Line 1

// Page 2 (third page), 20 items per page
Pageable pageable2 = PageRequest.of(2, 20);                  // Line 2

// Page 0, 10 items, sorted by price ascending
Pageable pageable3 = PageRequest.of(0, 10,
    Sort.by("price").ascending());                            // Line 3

// Page 0, 10 items, sorted by price descending
Pageable pageable4 = PageRequest.of(0, 10,
    Sort.by("price").descending());                           // Line 4

// Page 0, 10 items, sorted by multiple fields
Pageable pageable5 = PageRequest.of(0, 10,
    Sort.by("inStock").descending()
         .and(Sort.by("price").ascending()));                 // Line 5
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `PageRequest.of(0, 10)` | First page, 10 items, no sorting |
| 2 | `PageRequest.of(2, 20)` | Third page (zero-indexed), 20 items per page |
| 3 | `Sort.by("price").ascending()` | Sort by the `price` field in ascending order (cheapest first) |
| 4 | `Sort.by("price").descending()` | Sort by price descending (most expensive first) |
| 5 | `.and(Sort.by(...))` | Sort by `inStock` first (in-stock items first), then by price within each group |

---

## Page vs Slice

Spring Data provides two return types for paginated queries: `Page` and `Slice`.

### Page

`Page` extends `Slice` and adds a total count. It tells you exactly how many pages and total elements exist.

```
+-------------------------------------------+
|                Page<Product>              |
+-------------------------------------------+
| content      : List<Product>  (the data)  |
| number       : 2              (page num)  |
| size         : 10             (page size) |
| totalElements: 50             (total rows)|
| totalPages   : 5              (total pgs) |
| first        : false          (is first?) |
| last         : false          (is last?)  |
| hasNext      : true           (more pages)|
| hasPrevious  : true           (prev page) |
+-------------------------------------------+
```

**SQL generated for Page:**

```sql
-- Query 1: Get the data
SELECT * FROM products ORDER BY id LIMIT 10 OFFSET 20;

-- Query 2: Count total rows (extra query!)
SELECT COUNT(*) FROM products;
```

### Slice

`Slice` does not count the total. It only knows if there is a next page, not how many total pages exist.

```
+-------------------------------------------+
|               Slice<Product>             |
+-------------------------------------------+
| content      : List<Product>  (the data)  |
| number       : 2              (page num)  |
| size         : 10             (page size) |
| first        : false          (is first?) |
| last         : false          (is last?)  |
| hasNext      : true           (more pages)|
| hasPrevious  : true           (prev page) |
|                                           |
| NO totalElements                          |
| NO totalPages                             |
+-------------------------------------------+
```

**SQL generated for Slice:**

```sql
-- Only one query! Requests size+1 items to check if next page exists
SELECT * FROM products ORDER BY id LIMIT 11 OFFSET 20;
```

### When to Use Which

```
+------------------+----------------------------------------------+
| Use Page when    | Use Slice when                               |
+------------------+----------------------------------------------+
| You need to show | You have infinite scroll (like social media  |
| "Page 3 of 50"  | feeds) and only need "Load More" buttons     |
+------------------+----------------------------------------------+
| You need total   | The total count query is too expensive        |
| count for UI     | (millions of rows)                           |
+------------------+----------------------------------------------+
| Dataset is       | Dataset is very large and counting all rows  |
| moderate in size | would slow down the response                 |
+------------------+----------------------------------------------+
```

---

## Using Pagination in Repositories

### Adding Pageable to Repository Methods

Your `JpaRepository` already inherits a paginated `findAll` method. You can also add `Pageable` to your custom methods:

```java
package com.example.demo.repository;

import com.example.demo.entity.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Built-in from JpaRepository:
    // Page<Product> findAll(Pageable pageable);              // Line 1

    // Paginated derived query
    Page<Product> findByInStock(
        Boolean inStock, Pageable pageable);                  // Line 2

    // Paginated search
    Page<Product> findByNameContainingIgnoreCase(
        String keyword, Pageable pageable);                   // Line 3

    // Paginated with price filter
    Page<Product> findByPriceGreaterThan(
        Double price, Pageable pageable);                     // Line 4

    // Slice for infinite scroll
    Slice<Product> findByPriceLessThan(
        Double price, Pageable pageable);                     // Line 5

    // Paginated custom JPQL query
    @Query("SELECT p FROM Product p WHERE p.price BETWEEN :min AND :max")
    Page<Product> findByPriceRange(
        @Param("min") Double min,
        @Param("max") Double max,
        Pageable pageable);                                   // Line 6
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `findAll(Pageable)` | Already inherited from `JpaRepository`. Returns a `Page` of all products |
| 2 | `findByInStock(..., Pageable)` | Adds pagination to a derived query. Just add `Pageable` as the last parameter |
| 3 | `findByNameContainingIgnoreCase(..., Pageable)` | Paginated search by name. The `Pageable` also handles sorting |
| 4 | `findByPriceGreaterThan(..., Pageable)` | Filter + paginate. Returns a `Page` |
| 5 | `findByPriceLessThan(..., Pageable)` | Returns a `Slice` instead of `Page` (no total count query) |
| 6 | Custom `@Query` with `Pageable` | Add `Pageable` as the last parameter to any `@Query` method for pagination |

---

## The Sort Class

The `Sort` class lets you specify how results should be ordered.

```java
import org.springframework.data.domain.Sort;

// Sort by a single field ascending
Sort sort1 = Sort.by("price");                               // Line 1
// Same as above (ascending is default)
Sort sort2 = Sort.by(Sort.Direction.ASC, "price");           // Line 2

// Sort by a single field descending
Sort sort3 = Sort.by(Sort.Direction.DESC, "price");          // Line 3

// Sort by multiple fields
Sort sort4 = Sort.by("name").ascending()
    .and(Sort.by("price").descending());                     // Line 4

// Sort by multiple fields (shorter syntax)
Sort sort5 = Sort.by(
    Sort.Order.asc("name"),
    Sort.Order.desc("price")
);                                                            // Line 5

// Unsorted (no ordering)
Sort sort6 = Sort.unsorted();                                // Line 6
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `Sort.by("price")` | Sort by price ascending (default direction) |
| 2 | `Sort.by(Sort.Direction.ASC, "price")` | Explicit ascending sort by price |
| 3 | `Sort.by(Sort.Direction.DESC, "price")` | Sort by price descending (most expensive first) |
| 4 | `.and(Sort.by(...))` | Chain multiple sort criteria. Sort by name first, then by price within same names |
| 5 | `Sort.Order.asc/desc` | Alternative syntax using `Sort.Order` objects |
| 6 | `Sort.unsorted()` | No sorting applied |

### Using Sort in Repository

```java
// In the service layer
List<Product> products = productRepository.findAll(
    Sort.by("price").ascending()
);

// Combine sort with pagination
Pageable pageable = PageRequest.of(0, 10,
    Sort.by("price").descending());
Page<Product> page = productRepository.findAll(pageable);
```

---

## Auto-Resolving Pageable from Request Parameters

Here is where Spring's magic shines. When you add a `Pageable` parameter to a controller method, Spring automatically creates it from the request's query parameters.

### How Auto-Resolution Works

```
HTTP Request:
GET /api/products?page=2&size=10&sort=price,desc

                    |
                    v  Spring auto-creates:

Pageable pageable = PageRequest.of(2, 10,
    Sort.by("price").descending());
```

You do not need to manually parse `page`, `size`, or `sort` parameters. Spring does it all.

### Supported Request Parameters

```
+-------------------+---------------------------------------+
| Parameter         | Example                               |
+-------------------+---------------------------------------+
| page              | ?page=0        (default: 0)           |
| size              | ?size=20       (default: 20)           |
| sort              | ?sort=price    (ascending by default)  |
| sort (desc)       | ?sort=price,desc                      |
| sort (multiple)   | ?sort=name,asc&sort=price,desc        |
+-------------------+---------------------------------------+
```

### Controller with Auto-Resolved Pageable

```java
package com.example.demo.controller;

import com.example.demo.entity.Product;
import com.example.demo.service.ProductService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    // GET /api/products?page=0&size=10&sort=price,desc
    @GetMapping
    public ResponseEntity<Page<Product>> getAllProducts(
            Pageable pageable) {                              // Line 1
        Page<Product> products =
            productService.getAllProducts(pageable);
        return ResponseEntity.ok(products);
    }

    // With custom defaults: page=0, size=5, sort by name asc
    @GetMapping("/custom")
    public ResponseEntity<Page<Product>> getProductsWithDefaults(
            @PageableDefault(size = 5, sort = "name",
                direction = Sort.Direction.ASC)
            Pageable pageable) {                              // Line 2
        Page<Product> products =
            productService.getAllProducts(pageable);
        return ResponseEntity.ok(products);
    }

    // Paginated search
    // GET /api/products/search?keyword=phone&page=0&size=10
    @GetMapping("/search")
    public ResponseEntity<Page<Product>> searchProducts(
            @RequestParam String keyword,
            Pageable pageable) {                              // Line 3
        Page<Product> products =
            productService.searchProducts(keyword, pageable);
        return ResponseEntity.ok(products);
    }

    // Paginated filter by stock status
    // GET /api/products/in-stock?page=0&size=10&sort=price,asc
    @GetMapping("/in-stock")
    public ResponseEntity<Page<Product>> getInStockProducts(
            Pageable pageable) {
        Page<Product> products =
            productService.getInStockProducts(pageable);
        return ResponseEntity.ok(products);
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `Pageable pageable` | Spring automatically creates this from `?page=`, `?size=`, and `?sort=` query parameters |
| 2 | `@PageableDefault(size = 5, ...)` | Sets default values when the client does not provide pagination parameters |
| 3 | `@RequestParam String keyword, Pageable pageable` | Combines regular request parameters with auto-resolved pagination |

### Configuring Default Pageable Values

You can set global defaults in `application.properties`:

```properties
# Default page size (default is 20)
spring.data.web.pageable.default-page-size=10

# Maximum page size (prevents clients from requesting too much data)
spring.data.web.pageable.max-page-size=100

# Use 1-based page numbering (default is 0-based)
# spring.data.web.pageable.one-indexed-parameters=true
```

---

## The Service Layer with Pagination

```java
package com.example.demo.service;

import com.example.demo.entity.Product;
import com.example.demo.repository.ProductRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
public class ProductService {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public Page<Product> getAllProducts(Pageable pageable) {
        return productRepository.findAll(pageable);
    }

    public Page<Product> searchProducts(
            String keyword, Pageable pageable) {
        return productRepository
            .findByNameContainingIgnoreCase(keyword, pageable);
    }

    public Page<Product> getInStockProducts(Pageable pageable) {
        return productRepository
            .findByInStock(true, pageable);
    }

    public Page<Product> getProductsByPriceRange(
            Double min, Double max, Pageable pageable) {
        return productRepository
            .findByPriceRange(min, max, pageable);
    }
}
```

---

## Understanding the Page Response

When you return a `Page<Product>` from a controller, Spring serializes it into this JSON structure:

```
GET /api/products?page=1&size=3&sort=price,asc
```

**Response:**

```json
{
    "content": [
        {
            "id": 5,
            "name": "Smartwatch",
            "price": 299.99,
            "description": "Fitness tracking smartwatch",
            "inStock": true
        },
        {
            "id": 4,
            "name": "Tablet",
            "price": 449.99,
            "description": "10-inch display tablet",
            "inStock": false
        },
        {
            "id": 2,
            "name": "Smartphone",
            "price": 699.99,
            "description": "Latest model with 128GB storage",
            "inStock": true
        }
    ],
    "pageable": {
        "pageNumber": 1,
        "pageSize": 3,
        "sort": {
            "sorted": true,
            "empty": false,
            "unsorted": false
        },
        "offset": 3,
        "paged": true,
        "unpaged": false
    },
    "totalElements": 5,
    "totalPages": 2,
    "last": true,
    "size": 3,
    "number": 1,
    "sort": {
        "sorted": true,
        "empty": false,
        "unsorted": false
    },
    "numberOfElements": 2,
    "first": false,
    "empty": false
}
```

Let us break down each field:

```
+---------------------+-------+-------------------------------------------+
| Field               | Value | Meaning                                   |
+---------------------+-------+-------------------------------------------+
| content             | [...]  | The actual data for this page             |
| pageable.pageNumber | 1     | Current page number (0-indexed)           |
| pageable.pageSize   | 3     | Items per page                            |
| pageable.offset     | 3     | How many items were skipped (page * size) |
| totalElements       | 5     | Total items across all pages              |
| totalPages          | 2     | Total number of pages                     |
| last                | true  | Is this the last page?                    |
| first               | false | Is this the first page?                   |
| number              | 1     | Current page number (same as pageNumber)  |
| numberOfElements    | 2     | Items on THIS page (may be less than size |
|                     |       | on the last page)                         |
| empty               | false | Is the content empty?                     |
| sort.sorted         | true  | Is the result sorted?                     |
+---------------------+-------+-------------------------------------------+
```

---

## Using Page.map() to Transform Results

Often you want to transform entities before returning them. For example, converting entities to DTOs. `Page.map()` transforms each element while preserving all pagination metadata.

```java
package com.example.demo.dto;

public class ProductSummaryDTO {
    private Long id;
    private String name;
    private Double price;
    private String availability;

    public ProductSummaryDTO(Long id, String name, Double price,
                             String availability) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.availability = availability;
    }

    // Getters
    public Long getId() { return id; }
    public String getName() { return name; }
    public Double getPrice() { return price; }
    public String getAvailability() { return availability; }
}
```

### Using map() in the Service

```java
@Service
public class ProductService {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public Page<ProductSummaryDTO> getProductSummaries(
            Pageable pageable) {

        Page<Product> productPage =
            productRepository.findAll(pageable);              // Line 1

        return productPage.map(product ->                     // Line 2
            new ProductSummaryDTO(
                product.getId(),
                product.getName(),
                product.getPrice(),
                product.getInStock()
                    ? "In Stock" : "Out of Stock"             // Line 3
            )
        );
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `findAll(pageable)` | Gets a `Page<Product>` from the database |
| 2 | `productPage.map(...)` | Transforms each `Product` into a `ProductSummaryDTO`. Returns `Page<ProductSummaryDTO>` with the same pagination metadata |
| 3 | Ternary operator | Converts the boolean `inStock` to a human-readable string |

### Controller Using the DTO

```java
@GetMapping("/summaries")
public ResponseEntity<Page<ProductSummaryDTO>> getProductSummaries(
        Pageable pageable) {
    Page<ProductSummaryDTO> summaries =
        productService.getProductSummaries(pageable);
    return ResponseEntity.ok(summaries);
}
```

**Response:**

```json
{
    "content": [
        {"id": 1, "name": "Laptop", "price": 999.99, "availability": "In Stock"},
        {"id": 2, "name": "Smartphone", "price": 699.99, "availability": "In Stock"},
        {"id": 3, "name": "Headphones", "price": 149.99, "availability": "In Stock"}
    ],
    "totalElements": 5,
    "totalPages": 2,
    "number": 0,
    "size": 3,
    "first": true,
    "last": false
}
```

---

## Complete Paginated REST API Example

Here is a complete working example with all the pieces together.

**application.properties:**

```properties
spring.application.name=pagination-demo
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.defer-datasource-initialization=true

# Pagination defaults
spring.data.web.pageable.default-page-size=10
spring.data.web.pageable.max-page-size=50
```

**data.sql (sample data):**

```sql
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Laptop', 999.99, 'High-performance laptop', true);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Smartphone', 699.99, 'Latest smartphone', true);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Headphones', 149.99, 'Wireless headphones', true);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Tablet', 449.99, '10-inch tablet', false);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Smartwatch', 299.99, 'Fitness smartwatch', true);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Monitor', 349.99, '27-inch 4K monitor', true);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Keyboard', 79.99, 'Mechanical keyboard', true);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Mouse', 49.99, 'Ergonomic mouse', true);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Webcam', 89.99, '1080p webcam', false);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Speaker', 129.99, 'Bluetooth speaker', true);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('Printer', 199.99, 'Laser printer', false);
INSERT INTO products (product_name, price, description, in_stock)
VALUES ('SSD', 89.99, '1TB solid state drive', true);
```

**ProductController.java (complete):**

```java
package com.example.demo.controller;

import com.example.demo.entity.Product;
import com.example.demo.service.ProductService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    // Basic pagination
    // GET /api/products?page=0&size=5
    // GET /api/products?page=0&size=5&sort=price,desc
    // GET /api/products?page=0&size=5&sort=name,asc&sort=price,desc
    @GetMapping
    public ResponseEntity<Page<Product>> getAllProducts(
            @PageableDefault(size = 10, sort = "id")
            Pageable pageable) {
        return ResponseEntity.ok(
            productService.getAllProducts(pageable));
    }

    // Search with pagination
    // GET /api/products/search?keyword=smart&page=0&size=5
    @GetMapping("/search")
    public ResponseEntity<Page<Product>> searchProducts(
            @RequestParam String keyword,
            Pageable pageable) {
        return ResponseEntity.ok(
            productService.searchProducts(keyword, pageable));
    }

    // Filter by stock status with pagination
    // GET /api/products/available?page=0&size=5&sort=price,asc
    @GetMapping("/available")
    public ResponseEntity<Page<Product>> getAvailableProducts(
            Pageable pageable) {
        return ResponseEntity.ok(
            productService.getInStockProducts(pageable));
    }

    // Price range with pagination
    // GET /api/products/price-range?min=100&max=500&page=0&size=5
    @GetMapping("/price-range")
    public ResponseEntity<Page<Product>> getProductsByPriceRange(
            @RequestParam Double min,
            @RequestParam Double max,
            Pageable pageable) {
        return ResponseEntity.ok(
            productService.getProductsByPriceRange(
                min, max, pageable));
    }
}
```

### Testing the Paginated API

**Request 1: First page, 3 items, sorted by price ascending**

```
GET http://localhost:8080/api/products?page=0&size=3&sort=price,asc
```

**Response:**

```json
{
    "content": [
        {"id": 8, "name": "Mouse", "price": 49.99, ...},
        {"id": 7, "name": "Keyboard", "price": 79.99, ...},
        {"id": 9, "name": "Webcam", "price": 89.99, ...}
    ],
    "totalElements": 12,
    "totalPages": 4,
    "number": 0,
    "size": 3,
    "first": true,
    "last": false
}
```

**Request 2: Second page, same settings**

```
GET http://localhost:8080/api/products?page=1&size=3&sort=price,asc
```

**Response:**

```json
{
    "content": [
        {"id": 12, "name": "SSD", "price": 89.99, ...},
        {"id": 10, "name": "Speaker", "price": 129.99, ...},
        {"id": 3, "name": "Headphones", "price": 149.99, ...}
    ],
    "totalElements": 12,
    "totalPages": 4,
    "number": 1,
    "size": 3,
    "first": false,
    "last": false
}
```

**Request 3: Search with pagination**

```
GET http://localhost:8080/api/products/search?keyword=smart&page=0&size=10
```

**Response:**

```json
{
    "content": [
        {"id": 2, "name": "Smartphone", "price": 699.99, ...},
        {"id": 5, "name": "Smartwatch", "price": 299.99, ...}
    ],
    "totalElements": 2,
    "totalPages": 1,
    "number": 0,
    "size": 10,
    "first": true,
    "last": true
}
```

---

## Pagination Flow Diagram

```
Client Request                    Spring Boot Application
     |                                    |
     |  GET /api/products?               |
     |  page=1&size=3&sort=price,desc    |
     |----------------------------------->|
     |                                    |
     |                          +-------------------+
     |                          | Spring resolves   |
     |                          | Pageable from     |
     |                          | query parameters  |
     |                          +--------+----------+
     |                                   |
     |                          +--------v----------+
     |                          | Controller calls  |
     |                          | service method    |
     |                          +--------+----------+
     |                                   |
     |                          +--------v----------+
     |                          | Service calls     |
     |                          | repository with   |
     |                          | Pageable          |
     |                          +--------+----------+
     |                                   |
     |                          +--------v----------+
     |                          | Repository runs:  |
     |                          | SELECT * FROM     |
     |                          |   products        |
     |                          | ORDER BY price    |
     |                          |   DESC            |
     |                          | LIMIT 3 OFFSET 3  |
     |                          |                   |
     |                          | SELECT COUNT(*)   |
     |                          |   FROM products   |
     |                          +--------+----------+
     |                                   |
     |                          +--------v----------+
     |                          | Page<Product>     |
     |                          | serialized to JSON|
     |                          +--------+----------+
     |                                   |
     |  200 OK                           |
     |  { "content": [...],             |
     |    "totalElements": 12,           |
     |    "totalPages": 4, ... }         |
     |<----------------------------------|
```

---

## Common Mistakes

### Mistake 1: Not Adding Pageable as the Last Parameter

```java
// WRONG - Pageable must be the last parameter in derived queries
Page<Product> findByPageableAndName(Pageable pageable, String name);

// CORRECT - Pageable is always the last parameter
Page<Product> findByName(String name, Pageable pageable);
```

### Mistake 2: Forgetting That Pages Are Zero-Indexed

```
// Client expects page 1 to be the first page
GET /api/products?page=1&size=10
// But this actually returns the SECOND page!

// The first page is page 0
GET /api/products?page=0&size=10
// This returns the first page
```

If your frontend uses 1-based pagination, you can configure Spring to accept it:

```properties
spring.data.web.pageable.one-indexed-parameters=true
```

### Mistake 3: Returning List Instead of Page

```java
// WRONG - Loses pagination metadata
@GetMapping
public List<Product> getAllProducts(Pageable pageable) {
    return productService.getAllProducts(pageable).getContent();
    // Client loses totalElements, totalPages, etc.
}

// CORRECT - Return the full Page
@GetMapping
public Page<Product> getAllProducts(Pageable pageable) {
    return productService.getAllProducts(pageable);
    // Client gets data + all pagination metadata
}
```

### Mistake 4: Using Wrong Field Names in sort Parameter

```
// WRONG - Using column name instead of Java field name
GET /api/products?sort=product_name,asc
// Error: No property 'product_name' found

// CORRECT - Use the Java field name
GET /api/products?sort=name,asc
```

### Mistake 5: Not Limiting Maximum Page Size

```properties
# Without this, a client could request ALL records:
# GET /api/products?size=999999
# This would load everything into memory!

# Add a maximum page size
spring.data.web.pageable.max-page-size=100
```

---

## Best Practices

1. **Always set a maximum page size**: Use `spring.data.web.pageable.max-page-size` to prevent clients from requesting too much data at once.

2. **Use `@PageableDefault` for sensible defaults**: When no pagination parameters are provided, return a reasonable number of items (10-20).

3. **Use `Page` for traditional pagination**: When you need "Page X of Y" in the UI.

4. **Use `Slice` for infinite scroll**: When you only need "Load More" and total count is expensive to compute.

5. **Sort by a unique field**: Always include a unique field (like `id`) in your sort to ensure consistent ordering across pages.

6. **Use `Page.map()` for DTOs**: Transform entities to DTOs while preserving pagination metadata.

7. **Document your API defaults**: Make sure API consumers know the default page size and sort order.

8. **Return `ResponseEntity<Page<T>>`**: This gives you control over HTTP status codes while returning full pagination metadata.

---

## Quick Summary

```
+--------------------------------------------+
|  Pagination & Sorting Quick Reference      |
+--------------------------------------------+
|                                            |
|  REQUEST PARAMETERS:                       |
|  ?page=0         (zero-indexed)            |
|  ?size=10        (items per page)          |
|  ?sort=field,asc (sort ascending)          |
|  ?sort=field,desc (sort descending)        |
|                                            |
|  JAVA CLASSES:                             |
|  Pageable        -> auto-resolved from     |
|                     request params         |
|  PageRequest.of(page, size, sort)          |
|  Sort.by("field").ascending()              |
|  Page<T>         -> data + total count     |
|  Slice<T>        -> data, no total count   |
|                                            |
|  REPOSITORY:                               |
|  Page<T> findAll(Pageable p)               |
|  Page<T> findByField(val, Pageable p)      |
|                                            |
|  CONTROLLER:                               |
|  method(Pageable pageable)                 |
|  method(@PageableDefault(...) Pageable p)  |
|                                            |
|  TRANSFORMATION:                           |
|  page.map(entity -> dto)                   |
|                                            |
+--------------------------------------------+
```

---

## Key Points

1. Pagination prevents loading entire datasets into memory. Always paginate API endpoints that return collections.

2. Pages are zero-indexed by default. Page 0 is the first page.

3. `Pageable` is auto-resolved from request parameters (`page`, `size`, `sort`) when used as a controller method parameter.

4. `Page<T>` includes total count (runs an extra COUNT query). `Slice<T>` does not include total count (faster for large datasets).

5. Add `Pageable` as the last parameter to any repository method to make it paginated.

6. `Page.map()` transforms each element while preserving all pagination metadata.

7. Use `@PageableDefault` to set defaults and `spring.data.web.pageable.max-page-size` to limit the maximum page size.

---

## Practice Questions

1. What is the difference between `Page` and `Slice`? When would you use each one?

2. What query parameters does Spring auto-resolve for a `Pageable` controller parameter? What are the defaults?

3. If you have 25 products and request `?page=2&size=10`, how many products will be returned? What will `totalPages` be?

4. How does `Page.map()` work? Why is it useful for transforming entities to DTOs?

5. Why should you always set `spring.data.web.pageable.max-page-size`? What could happen without it?

---

## Exercises

### Exercise 1: Paginated User API

Create a paginated API for the `User` entity with these endpoints:
- `GET /api/users` - List all users with pagination and sorting
- `GET /api/users/active` - List only active users with pagination
- `GET /api/users/search?name=alice` - Search by name with pagination

Include at least 15 users in `data.sql` and test with different page sizes and sort orders.

### Exercise 2: Custom Page Response

The default `Page` JSON response includes a lot of metadata. Create a custom response wrapper class that simplifies the response to:

```json
{
    "data": [...],
    "currentPage": 0,
    "totalPages": 5,
    "totalItems": 50,
    "hasNext": true,
    "hasPrevious": false
}
```

Use `Page.map()` or create a utility method that converts any `Page<T>` to your custom response.

### Exercise 3: Sorting Challenge

Create an endpoint that accepts a `category` parameter and returns products sorted by:
- In-stock products first, then out-of-stock
- Within each stock status group, sorted by price ascending

Test with at least 20 products across 3 categories.

---

## What Is Next?

Your API can now store data, query it, and return it in paginated, sorted chunks. But there is one critical piece missing: security. Right now, anyone can access your API endpoints, create products, delete products, or view user data. In the next chapter, you will learn about **Spring Security** -- how to protect your API with authentication and authorization.
