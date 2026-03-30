# Chapter 15: Repositories and CRUD Operations

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand what Spring Data JPA repositories are and why they are powerful
- Create a `JpaRepository` interface for any entity
- Perform CRUD operations: `save`, `findById`, `findAll`, `deleteById`
- Write derived query methods like `findByName` and `findByEmailAndActive`
- Use `@Query` for custom JPQL and native SQL queries
- Use `@Modifying` for update and delete queries
- Build a complete CRUD service and controller

## Why This Chapter Matters

In the last chapter, you created entity classes that map to database tables. But having tables without the ability to read and write data is like having a filing cabinet you cannot open.

Think about a library. The books (entities) sit on shelves (tables), but you need a librarian to find books, add new ones, remove old ones, and organize them. In Spring Data JPA, that librarian is called a **Repository**.

The remarkable thing about Spring Data JPA repositories is how little code you need to write. You declare an interface with method names that describe what you want, and Spring generates the implementation automatically. You ask for `findByAuthor(String author)`, and Spring writes the SQL query for you. No boilerplate, no repetition, no SQL.

---

## What Is a Repository?

A repository is an interface that provides methods to interact with the database for a specific entity. Spring Data JPA provides several levels of repository interfaces:

```
+--------------------------------------------------+
|              Repository<T, ID>                   |
|              (Marker interface, no methods)       |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|           CrudRepository<T, ID>                  |
|  save(), findById(), findAll(), delete(),        |
|  count(), existsById()                           |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|        ListCrudRepository<T, ID>                 |
|  Same as CrudRepository but returns List         |
|  instead of Iterable                             |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|         PagingAndSortingRepository<T, ID>        |
|  findAll(Sort), findAll(Pageable)                |
+-------------------------+------------------------+
                          |
                          v
+--------------------------------------------------+
|           JpaRepository<T, ID>                   |
|  flush(), saveAndFlush(), deleteInBatch(),       |
|  findAll(Example), getReferenceById()            |
|  + ALL methods from above interfaces             |
+--------------------------------------------------+
```

**JpaRepository** is the most commonly used because it includes everything. When in doubt, extend `JpaRepository`.

---

## Creating Your First Repository

### The Entity (from Chapter 14)

Let us use the `Product` entity from the previous chapter:

```java
package com.example.demo.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "product_name", nullable = false, length = 100)
    private String name;

    @Column(nullable = false)
    private Double price;

    @Column(length = 500)
    private String description;

    @Column(name = "in_stock")
    private Boolean inStock = true;

    public Product() {}

    public Product(String name, Double price, String description) {
        this.name = name;
        this.price = price;
        this.description = description;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public Double getPrice() { return price; }
    public void setPrice(Double price) { this.price = price; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Boolean getInStock() { return inStock; }
    public void setInStock(Boolean inStock) { this.inStock = inStock; }

    @Override
    public String toString() {
        return "Product{id=" + id + ", name='" + name + "', price=" + price + "}";
    }
}
```

### The Repository Interface

```java
package com.example.demo.repository;

import com.example.demo.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository                                                   // Line 1
public interface ProductRepository                            // Line 2
        extends JpaRepository<Product, Long> {                // Line 3
    // That's it! No method implementations needed.
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `@Repository` | Marks this as a repository bean. Optional for interfaces extending `JpaRepository` (Spring detects them automatically), but it is good practice for clarity |
| 2 | `interface ProductRepository` | This is an **interface**, not a class. You do not write any implementation. Spring generates one for you at runtime |
| 3 | `JpaRepository<Product, Long>` | The first type parameter (`Product`) is the entity class. The second (`Long`) is the type of the entity's `@Id` field |

With just these three lines, you get all of these methods for free:

```
+----------------------------------+--------------------------------------+
| Method                           | What It Does                         |
+----------------------------------+--------------------------------------+
| save(Product p)                  | Insert new or update existing        |
| saveAll(List<Product> list)      | Save multiple products at once       |
| findById(Long id)               | Find one product by ID               |
| findAll()                        | Get all products                     |
| findAllById(List<Long> ids)     | Find multiple products by IDs        |
| count()                          | Count total products                 |
| existsById(Long id)             | Check if a product exists            |
| deleteById(Long id)             | Delete a product by ID               |
| delete(Product p)               | Delete a product by entity           |
| deleteAll()                      | Delete all products                  |
| flush()                          | Force pending changes to database    |
| saveAndFlush(Product p)         | Save and immediately flush           |
+----------------------------------+--------------------------------------+
```

---

## CRUD Operations in Detail

### Create (Save)

```java
// Saving a NEW product (id is null, so JPA does an INSERT)
Product laptop = new Product("Laptop", 999.99, "High-performance laptop");
Product saved = productRepository.save(laptop);
System.out.println("Saved: " + saved.getId());  // Saved: 1

// Saving MULTIPLE products
List<Product> products = List.of(
    new Product("Phone", 699.99, "Smartphone"),
    new Product("Tablet", 449.99, "10-inch tablet")
);
List<Product> savedProducts = productRepository.saveAll(products);
```

**Generated SQL:**

```sql
Hibernate:
    insert into products (description, in_stock, product_name, price)
    values (?, ?, ?, ?)
```

### Read (Find)

```java
// Find by ID (returns Optional)
Optional<Product> optionalProduct = productRepository.findById(1L);  // Line 1

if (optionalProduct.isPresent()) {                                   // Line 2
    Product product = optionalProduct.get();                         // Line 3
    System.out.println("Found: " + product.getName());
} else {
    System.out.println("Product not found");
}

// Shorter version using orElseThrow
Product product = productRepository.findById(1L)                     // Line 4
    .orElseThrow(() -> new RuntimeException("Product not found"));

// Find all products
List<Product> allProducts = productRepository.findAll();             // Line 5
System.out.println("Total products: " + allProducts.size());

// Check if exists
boolean exists = productRepository.existsById(1L);                  // Line 6
System.out.println("Exists: " + exists);  // Exists: true

// Count all
long count = productRepository.count();                              // Line 7
System.out.println("Total: " + count);
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `findById(1L)` | Looks for a product with ID 1. Returns `Optional<Product>`, not `Product` directly |
| 2 | `isPresent()` | Checks if a product was found. Avoids `NullPointerException` |
| 3 | `optionalProduct.get()` | Extracts the actual `Product` from the `Optional` |
| 4 | `orElseThrow(...)` | Gets the product or throws an exception if not found. Cleaner than if-else |
| 5 | `findAll()` | Returns a `List<Product>` containing all products in the table |
| 6 | `existsById(1L)` | Returns `true` or `false`. More efficient than `findById` when you only need to check existence |
| 7 | `count()` | Returns the total number of rows in the table |

**Generated SQL for findById:**

```sql
Hibernate:
    select p1_0.id, p1_0.description, p1_0.in_stock,
           p1_0.product_name, p1_0.price
    from products p1_0
    where p1_0.id=?
```

### Update (Save with Existing ID)

```java
// Step 1: Find the existing product
Product product = productRepository.findById(1L)
    .orElseThrow(() -> new RuntimeException("Not found"));

// Step 2: Modify the fields
product.setPrice(899.99);
product.setDescription("Updated description");

// Step 3: Save again (id is NOT null, so JPA does an UPDATE)
Product updated = productRepository.save(product);
System.out.println("Updated price: " + updated.getPrice());  // 899.99
```

**Generated SQL:**

```sql
Hibernate:
    update products
    set description=?, in_stock=?, product_name=?, price=?
    where id=?
```

**How does `save()` know to INSERT or UPDATE?**

```
+---------------------------+
|     save(entity)          |
|         |                 |
|    Is entity.id null?     |
|      /          \         |
|    YES            NO      |
|     |              |      |
|   INSERT        UPDATE    |
|  (new row)    (existing)  |
+---------------------------+
```

### Delete

```java
// Delete by ID
productRepository.deleteById(1L);

// Delete by entity
Product product = productRepository.findById(2L)
    .orElseThrow(() -> new RuntimeException("Not found"));
productRepository.delete(product);

// Delete all
productRepository.deleteAll();
```

**Generated SQL:**

```sql
Hibernate:
    delete from products where id=?
```

---

## Derived Query Methods

One of the most powerful features of Spring Data JPA is **derived query methods**. You write a method name that describes what you want, and Spring generates the SQL automatically.

### How It Works

```
Method name:  findByNameAndPriceGreaterThan(String name, Double price)
                |    |         |
                |    |         +-- Condition: price > ?
                |    +------------ Field: name = ?
                +----------------- Action: SELECT ... WHERE
```

Spring parses the method name and generates the query. Think of it as writing a query in plain English.

### Adding Derived Methods to ProductRepository

```java
package com.example.demo.repository;

import com.example.demo.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Find products by exact name
    List<Product> findByName(String name);                    // Line 1

    // Find products by stock status
    List<Product> findByInStock(Boolean inStock);             // Line 2

    // Find products cheaper than a given price
    List<Product> findByPriceLessThan(Double price);          // Line 3

    // Find products within a price range
    List<Product> findByPriceBetween(
        Double minPrice, Double maxPrice);                    // Line 4

    // Find products by name containing a keyword (LIKE %keyword%)
    List<Product> findByNameContainingIgnoreCase(
        String keyword);                                      // Line 5

    // Find products by name AND in stock
    List<Product> findByNameAndInStock(
        String name, Boolean inStock);                        // Line 6

    // Find products by name OR description containing keyword
    List<Product> findByNameContainingOrDescriptionContaining(
        String nameKeyword, String descKeyword);              // Line 7

    // Find products ordered by price (ascending)
    List<Product> findByInStockOrderByPriceAsc(
        Boolean inStock);                                     // Line 8

    // Find products ordered by price (descending)
    List<Product> findByInStockOrderByPriceDesc(
        Boolean inStock);                                     // Line 9

    // Count products by stock status
    long countByInStock(Boolean inStock);                     // Line 10

    // Check if a product exists by name
    boolean existsByName(String name);                        // Line 11

    // Find first product by name
    Optional<Product> findFirstByName(String name);           // Line 12

    // Find top 3 cheapest products
    List<Product> findTop3ByOrderByPriceAsc();                // Line 13

    // Delete products by stock status
    void deleteByInStock(Boolean inStock);                    // Line 14
}
```

**Line-by-line explanation:**

| Line | Method | Generated SQL (simplified) |
|------|--------|---------------------------|
| 1 | `findByName(name)` | `SELECT * FROM products WHERE product_name = ?` |
| 2 | `findByInStock(inStock)` | `SELECT * FROM products WHERE in_stock = ?` |
| 3 | `findByPriceLessThan(price)` | `SELECT * FROM products WHERE price < ?` |
| 4 | `findByPriceBetween(min, max)` | `SELECT * FROM products WHERE price BETWEEN ? AND ?` |
| 5 | `findByNameContainingIgnoreCase(kw)` | `SELECT * FROM products WHERE LOWER(product_name) LIKE LOWER('%' || ? || '%')` |
| 6 | `findByNameAndInStock(name, stock)` | `SELECT * FROM products WHERE product_name = ? AND in_stock = ?` |
| 7 | `findByNameContaining...` | `SELECT * FROM products WHERE product_name LIKE ? OR description LIKE ?` |
| 8 | `findByInStockOrderByPriceAsc(stock)` | `SELECT * FROM products WHERE in_stock = ? ORDER BY price ASC` |
| 9 | `findByInStockOrderByPriceDesc(stock)` | `SELECT * FROM products WHERE in_stock = ? ORDER BY price DESC` |
| 10 | `countByInStock(stock)` | `SELECT COUNT(*) FROM products WHERE in_stock = ?` |
| 11 | `existsByName(name)` | `SELECT COUNT(*) > 0 FROM products WHERE product_name = ?` |
| 12 | `findFirstByName(name)` | `SELECT * FROM products WHERE product_name = ? LIMIT 1` |
| 13 | `findTop3ByOrderByPriceAsc()` | `SELECT * FROM products ORDER BY price ASC LIMIT 3` |
| 14 | `deleteByInStock(stock)` | `DELETE FROM products WHERE in_stock = ?` |

### Derived Query Keywords Reference

```
+-----------------------+------------------------------+
| Keyword               | SQL Equivalent               |
+-----------------------+------------------------------+
| findBy                | SELECT ... WHERE             |
| countBy               | SELECT COUNT(*) WHERE        |
| existsBy              | SELECT COUNT(*) > 0 WHERE    |
| deleteBy              | DELETE ... WHERE             |
+-----------------------+------------------------------+
| And                   | AND                          |
| Or                    | OR                           |
+-----------------------+------------------------------+
| Is, Equals            | = (default, can be omitted)  |
| Not                   | <>                           |
| IsNull                | IS NULL                      |
| IsNotNull             | IS NOT NULL                  |
| LessThan              | <                            |
| LessThanEqual         | <=                           |
| GreaterThan           | >                            |
| GreaterThanEqual      | >=                           |
| Between               | BETWEEN ? AND ?              |
| Like                  | LIKE                         |
| Containing            | LIKE '%?%'                   |
| StartingWith          | LIKE '?%'                    |
| EndingWith            | LIKE '%?'                    |
| IgnoreCase            | LOWER(...) = LOWER(?)        |
| In                    | IN (?, ?, ?)                 |
| NotIn                 | NOT IN (?, ?, ?)             |
| True                  | = TRUE                       |
| False                 | = FALSE                      |
| OrderBy...Asc         | ORDER BY ... ASC             |
| OrderBy...Desc        | ORDER BY ... DESC            |
| First, Top            | LIMIT 1 / LIMIT N            |
+-----------------------+------------------------------+
```

---

## Custom Queries with @Query

Sometimes derived query methods get too long or you need a query that cannot be expressed through method naming. In these cases, use `@Query`.

### JPQL Queries (Java Persistence Query Language)

JPQL is like SQL but uses entity class names and field names instead of table and column names.

```java
package com.example.demo.repository;

import com.example.demo.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // JPQL query using positional parameter
    @Query("SELECT p FROM Product p WHERE p.price > ?1")     // Line 1
    List<Product> findExpensiveProducts(Double minPrice);

    // JPQL query using named parameter
    @Query("SELECT p FROM Product p WHERE p.name LIKE %:keyword%") // Line 2
    List<Product> searchByName(
        @Param("keyword") String keyword);                    // Line 3

    // JPQL query with multiple conditions
    @Query("SELECT p FROM Product p WHERE p.price BETWEEN :min AND :max "
         + "AND p.inStock = true ORDER BY p.price ASC")       // Line 4
    List<Product> findAvailableInPriceRange(
        @Param("min") Double minPrice,
        @Param("max") Double maxPrice);

    // JPQL query returning specific fields
    @Query("SELECT p.name, p.price FROM Product p "
         + "WHERE p.inStock = true")                          // Line 5
    List<Object[]> findProductNameAndPrice();

    // Native SQL query
    @Query(value = "SELECT * FROM products WHERE price > :price",
           nativeQuery = true)                                // Line 6
    List<Product> findExpensiveProductsNative(
        @Param("price") Double price);

    // Count query
    @Query("SELECT COUNT(p) FROM Product p WHERE p.inStock = :inStock")
    long countByStockStatus(@Param("inStock") Boolean inStock); // Line 7
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `?1` | Positional parameter. `?1` refers to the first method parameter, `?2` to the second, etc. |
| 2 | `%:keyword%` | Named parameter with LIKE wildcards. Searches for products containing the keyword |
| 3 | `@Param("keyword")` | Maps the method parameter to the named parameter `:keyword` in the query |
| 4 | `BETWEEN :min AND :max` | Range query with two named parameters |
| 5 | `SELECT p.name, p.price` | Returns only specific fields instead of the full entity. Result is `List<Object[]>` where each array has two elements |
| 6 | `nativeQuery = true` | Uses raw SQL instead of JPQL. Notice it uses table name `products` and column name `price` instead of entity name `Product` and field name |
| 7 | `SELECT COUNT(p)` | JPQL aggregate function to count matching records |

### JPQL vs Native SQL

```
+------------------------+-------------------------------------------+
| Feature                | JPQL                 | Native SQL          |
+------------------------+-------------------------------------------+
| Uses                   | Entity/field names   | Table/column names  |
| Database portable      | Yes                  | No (DB-specific)    |
| Example                | SELECT p FROM        | SELECT * FROM       |
|                        | Product p            | products            |
| Annotation             | @Query("...")         | @Query(value="...", |
|                        |                      |  nativeQuery=true)  |
| Best for               | Most queries         | Complex SQL,        |
|                        |                      | DB-specific features|
+------------------------+-------------------------------------------+
```

### @Modifying for UPDATE and DELETE Queries

By default, `@Query` methods are read-only (SELECT). To run UPDATE or DELETE queries, you need `@Modifying` and `@Transactional`.

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Update query
    @Modifying                                                // Line 1
    @Transactional                                            // Line 2
    @Query("UPDATE Product p SET p.price = :newPrice "
         + "WHERE p.name = :name")                            // Line 3
    int updatePriceByName(
        @Param("name") String name,
        @Param("newPrice") Double newPrice);                  // Line 4

    // Delete query
    @Modifying
    @Transactional
    @Query("DELETE FROM Product p WHERE p.inStock = false")   // Line 5
    int deleteOutOfStockProducts();                           // Line 6

    // Bulk update
    @Modifying
    @Transactional
    @Query("UPDATE Product p SET p.inStock = :status "
         + "WHERE p.price > :price")
    int updateStockStatusByPrice(
        @Param("status") Boolean status,
        @Param("price") Double price);
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `@Modifying` | Tells Spring this query modifies data (not a SELECT). Required for UPDATE and DELETE queries |
| 2 | `@Transactional` | Wraps the query in a database transaction. Required for modifying queries |
| 3 | `UPDATE Product p SET...` | JPQL update statement. Uses entity name and field names |
| 4 | `int` return type | Returns the number of rows affected by the update |
| 5 | `DELETE FROM Product p` | JPQL delete statement |
| 6 | `int` return type | Returns the number of rows deleted |

---

## Building a Complete CRUD Service

Now let us put everything together into a proper service layer.

### Why a Service Layer?

```
+------------------+     +------------------+     +------------------+
|    Controller    | --> |     Service      | --> |    Repository    |
|                  |     |                  |     |                  |
| Handles HTTP     |     | Business logic   |     | Database access  |
| requests/        |     | Validation       |     | CRUD operations  |
| responses        |     | Transformations  |     | Query execution  |
+------------------+     +------------------+     +------------------+
```

The service layer sits between the controller and the repository. It contains business logic and keeps your controllers thin.

### ProductService

```java
package com.example.demo.service;

import com.example.demo.entity.Product;
import com.example.demo.repository.ProductRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service                                                      // Line 1
public class ProductService {

    private final ProductRepository productRepository;        // Line 2

    public ProductService(ProductRepository productRepository) { // Line 3
        this.productRepository = productRepository;
    }

    // CREATE
    public Product createProduct(Product product) {           // Line 4
        return productRepository.save(product);
    }

    // READ - Get all
    public List<Product> getAllProducts() {                    // Line 5
        return productRepository.findAll();
    }

    // READ - Get by ID
    public Product getProductById(Long id) {                  // Line 6
        return productRepository.findById(id)
            .orElseThrow(() -> new RuntimeException(
                "Product not found with id: " + id));
    }

    // UPDATE
    public Product updateProduct(Long id, Product productDetails) { // Line 7
        Product existingProduct = getProductById(id);         // Line 8

        existingProduct.setName(productDetails.getName());    // Line 9
        existingProduct.setPrice(productDetails.getPrice());
        existingProduct.setDescription(
            productDetails.getDescription());
        existingProduct.setInStock(productDetails.getInStock());

        return productRepository.save(existingProduct);       // Line 10
    }

    // DELETE
    public void deleteProduct(Long id) {                      // Line 11
        Product product = getProductById(id);                 // Line 12
        productRepository.delete(product);
    }

    // SEARCH
    public List<Product> searchProducts(String keyword) {     // Line 13
        return productRepository
            .findByNameContainingIgnoreCase(keyword);
    }

    // FILTER by price range
    public List<Product> getProductsByPriceRange(
            Double minPrice, Double maxPrice) {
        return productRepository
            .findByPriceBetween(minPrice, maxPrice);
    }

    // FILTER by stock status
    public List<Product> getInStockProducts() {
        return productRepository.findByInStock(true);
    }

    // COUNT
    public long getProductCount() {
        return productRepository.count();
    }

    // BULK UPDATE
    @Transactional                                            // Line 14
    public int markExpensiveProductsOutOfStock(Double priceThreshold) {
        return productRepository
            .updateStockStatusByPrice(false, priceThreshold);
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `@Service` | Marks this class as a service component. Spring creates a single instance and manages it |
| 2 | `private final ProductRepository` | Declares the repository dependency as `final` for immutability |
| 3 | Constructor injection | Spring automatically injects the `ProductRepository` bean |
| 4 | `createProduct(...)` | Saves a new product. The returned product has a generated ID |
| 5 | `getAllProducts()` | Returns all products from the database |
| 6 | `getProductById(...)` | Finds a product by ID or throws an exception if not found |
| 7 | `updateProduct(...)` | Accepts the ID and new data to update |
| 8 | `getProductById(id)` | First, find the existing product (throws if not found) |
| 9 | `existingProduct.setName(...)` | Update each field with new values |
| 10 | `productRepository.save(...)` | Save the modified entity. Since it has an ID, JPA does an UPDATE |
| 11 | `deleteProduct(...)` | Deletes a product by ID |
| 12 | `getProductById(id)` | Verify the product exists before deleting. Gives a clear error message if not found |
| 13 | `searchProducts(...)` | Uses the derived query method for searching by name |
| 14 | `@Transactional` | Ensures the bulk update runs in a single database transaction |

### ProductController

```java
package com.example.demo.controller;

import com.example.demo.entity.Product;
import com.example.demo.service.ProductService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    // GET /api/products
    @GetMapping
    public ResponseEntity<List<Product>> getAllProducts() {
        List<Product> products = productService.getAllProducts();
        return ResponseEntity.ok(products);
    }

    // GET /api/products/5
    @GetMapping("/{id}")
    public ResponseEntity<Product> getProductById(
            @PathVariable Long id) {
        Product product = productService.getProductById(id);
        return ResponseEntity.ok(product);
    }

    // POST /api/products
    @PostMapping
    public ResponseEntity<Product> createProduct(
            @RequestBody Product product) {
        Product created = productService.createProduct(product);
        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(created);
    }

    // PUT /api/products/5
    @PutMapping("/{id}")
    public ResponseEntity<Product> updateProduct(
            @PathVariable Long id,
            @RequestBody Product product) {
        Product updated = productService.updateProduct(id, product);
        return ResponseEntity.ok(updated);
    }

    // DELETE /api/products/5
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, String>> deleteProduct(
            @PathVariable Long id) {
        productService.deleteProduct(id);
        return ResponseEntity.ok(
            Map.of("message", "Product deleted successfully"));
    }

    // GET /api/products/search?keyword=laptop
    @GetMapping("/search")
    public ResponseEntity<List<Product>> searchProducts(
            @RequestParam String keyword) {
        List<Product> products = productService.searchProducts(keyword);
        return ResponseEntity.ok(products);
    }

    // GET /api/products/price-range?min=100&max=500
    @GetMapping("/price-range")
    public ResponseEntity<List<Product>> getProductsByPriceRange(
            @RequestParam Double min,
            @RequestParam Double max) {
        List<Product> products =
            productService.getProductsByPriceRange(min, max);
        return ResponseEntity.ok(products);
    }

    // GET /api/products/in-stock
    @GetMapping("/in-stock")
    public ResponseEntity<List<Product>> getInStockProducts() {
        List<Product> products = productService.getInStockProducts();
        return ResponseEntity.ok(products);
    }

    // GET /api/products/count
    @GetMapping("/count")
    public ResponseEntity<Map<String, Long>> getProductCount() {
        long count = productService.getProductCount();
        return ResponseEntity.ok(Map.of("count", count));
    }
}
```

### Testing the Complete CRUD API

**Create a product:**

```
POST http://localhost:8080/api/products
Content-Type: application/json

{
    "name": "Mechanical Keyboard",
    "price": 129.99,
    "description": "RGB mechanical keyboard",
    "inStock": true
}
```

**Response (201 Created):**

```json
{
    "id": 6,
    "name": "Mechanical Keyboard",
    "price": 129.99,
    "description": "RGB mechanical keyboard",
    "inStock": true
}
```

**Get all products:**

```
GET http://localhost:8080/api/products
```

**Response (200 OK):**

```json
[
    {"id": 1, "name": "Laptop", "price": 999.99, "description": "High-performance laptop", "inStock": true},
    {"id": 2, "name": "Smartphone", "price": 699.99, "description": "Latest model", "inStock": true},
    {"id": 3, "name": "Headphones", "price": 149.99, "description": "Noise-cancelling", "inStock": true},
    {"id": 4, "name": "Tablet", "price": 449.99, "description": "10-inch display", "inStock": false},
    {"id": 5, "name": "Smartwatch", "price": 299.99, "description": "Fitness tracking", "inStock": true}
]
```

**Update a product:**

```
PUT http://localhost:8080/api/products/1
Content-Type: application/json

{
    "name": "Laptop Pro",
    "price": 1299.99,
    "description": "Pro laptop with M3 chip",
    "inStock": true
}
```

**Response (200 OK):**

```json
{
    "id": 1,
    "name": "Laptop Pro",
    "price": 1299.99,
    "description": "Pro laptop with M3 chip",
    "inStock": true
}
```

**Delete a product:**

```
DELETE http://localhost:8080/api/products/4
```

**Response (200 OK):**

```json
{
    "message": "Product deleted successfully"
}
```

**Search products:**

```
GET http://localhost:8080/api/products/search?keyword=phone
```

**Response (200 OK):**

```json
[
    {"id": 2, "name": "Smartphone", "price": 699.99, "description": "Latest model", "inStock": true},
    {"id": 3, "name": "Headphones", "price": 149.99, "description": "Noise-cancelling", "inStock": true}
]
```

---

## Complete Project Structure

```
src/main/java/com/example/demo/
├── DemoApplication.java
├── controller/
│   └── ProductController.java
├── entity/
│   └── Product.java
├── repository/
│   └── ProductRepository.java
└── service/
    └── ProductService.java

src/main/resources/
├── application.properties
└── data.sql
```

---

## Common Mistakes

### Mistake 1: Writing a Class Instead of an Interface

```java
// WRONG - Repository must be an interface
public class ProductRepository extends JpaRepository<Product, Long> {
    // This will not compile!
}

// CORRECT - Repository must be an interface
public interface ProductRepository extends JpaRepository<Product, Long> {
    // Spring generates the implementation
}
```

### Mistake 2: Wrong Field Names in Derived Queries

```java
// WRONG - Using column name instead of Java field name
List<Product> findByProduct_name(String name);
// Field is called "name" in Java, not "product_name"

// CORRECT - Use the Java field name
List<Product> findByName(String name);
```

### Mistake 3: Missing @Transactional for Modifying Queries

```java
// WRONG - Will throw TransactionRequiredException
@Modifying
@Query("UPDATE Product p SET p.price = :price WHERE p.id = :id")
int updatePrice(@Param("id") Long id, @Param("price") Double price);

// CORRECT - Add @Transactional
@Modifying
@Transactional
@Query("UPDATE Product p SET p.price = :price WHERE p.id = :id")
int updatePrice(@Param("id") Long id, @Param("price") Double price);
```

### Mistake 4: Not Handling Optional Properly

```java
// WRONG - Can throw NoSuchElementException
Product product = productRepository.findById(999L).get();

// CORRECT - Handle the empty case
Product product = productRepository.findById(999L)
    .orElseThrow(() -> new RuntimeException("Product not found"));

// Also CORRECT - Check first
Optional<Product> optional = productRepository.findById(999L);
if (optional.isPresent()) {
    Product product = optional.get();
}
```

### Mistake 5: Using Entity Directly as Request/Response

While we use entities directly in this chapter for simplicity, in production you should use DTOs (Data Transfer Objects) to decouple your API from your database schema. We will address this in later chapters.

---

## Best Practices

1. **Always use the service layer**: Do not call the repository directly from the controller. The service layer handles business logic and validation.

2. **Use `Optional` properly**: `findById` returns `Optional`. Always handle the empty case with `orElseThrow`, `orElse`, or `isPresent`.

3. **Prefer derived query methods for simple queries**: They are self-documenting and type-safe. Use `@Query` only when the method name would be too long.

4. **Use `@Param` with named parameters**: Named parameters are more readable than positional parameters (`?1`, `?2`).

5. **Return `ResponseEntity`**: Use `ResponseEntity` in controllers to control HTTP status codes and headers.

6. **Verify existence before delete**: Check that the entity exists before deleting. This gives users a clear error message instead of a silent no-op.

7. **Use constructor injection**: Always inject repositories through the constructor, not with `@Autowired` on fields.

8. **Keep repositories focused**: Each repository should manage exactly one entity. Do not add methods for multiple entities in a single repository.

---

## Quick Summary

```
+------------------------------------------+
|  Repositories & CRUD Quick Reference     |
+------------------------------------------+
|                                          |
|  INTERFACE:                              |
|  JpaRepository<Entity, IdType>           |
|                                          |
|  BUILT-IN METHODS:                       |
|  save()       -> INSERT or UPDATE        |
|  findById()   -> SELECT by ID (Optional) |
|  findAll()    -> SELECT all              |
|  deleteById() -> DELETE by ID            |
|  count()      -> COUNT all              |
|  existsById() -> Boolean check           |
|                                          |
|  DERIVED QUERIES:                        |
|  findByField(value)                      |
|  findByFieldAndField(v1, v2)             |
|  findByFieldContaining(keyword)          |
|  findByFieldGreaterThan(value)           |
|  findByFieldOrderByFieldAsc()            |
|                                          |
|  CUSTOM QUERIES:                         |
|  @Query("SELECT p FROM Product p ...")   |
|  @Query(value="...", nativeQuery=true)   |
|                                          |
|  MODIFYING:                              |
|  @Modifying + @Transactional + @Query    |
|                                          |
+------------------------------------------+
```

---

## Key Points

1. `JpaRepository<Product, Long>` gives you a full set of CRUD methods without writing any implementation code.

2. `save()` performs an INSERT when the entity ID is `null` and an UPDATE when the ID exists.

3. `findById()` returns `Optional<T>` -- always handle the empty case.

4. Derived query methods like `findByNameAndPriceLessThan` are parsed by Spring and converted to SQL automatically.

5. Use `@Query` for complex queries that cannot be expressed through method naming. JPQL uses entity names; native SQL uses table names.

6. `@Modifying` and `@Transactional` are required for UPDATE and DELETE queries.

7. The service layer contains business logic and sits between the controller and repository.

---

## Practice Questions

1. What is the difference between `CrudRepository` and `JpaRepository`? Why would you choose one over the other?

2. How does `save()` decide whether to INSERT or UPDATE? What determines this behavior?

3. Write a derived query method to find all users whose email ends with `@gmail.com` and who are active, ordered by last name.

4. What is the difference between JPQL and native SQL in a `@Query` annotation? When would you use native SQL?

5. Why do you need both `@Modifying` and `@Transactional` for UPDATE queries?

---

## Exercises

### Exercise 1: Build a Complete User CRUD

Using the `User` entity from Chapter 14, create:
- `UserRepository` with derived methods: `findByEmail`, `findByActiveTrue`, `findByLastNameContaining`
- `UserService` with full CRUD operations and a method to deactivate a user
- `UserController` with endpoints for all CRUD operations and search

Test all endpoints with Postman or curl.

### Exercise 2: Library Management System

Create a `Book` entity with fields: `id`, `title`, `author`, `isbn`, `genre`, `publishedYear`, `available`. Build a complete repository with these query methods:
- Find books by author
- Find books by genre
- Find available books published after a given year
- Search books by title keyword
- Count books by genre
- A `@Query` method to find the most expensive book in each genre

### Exercise 3: Custom Query Challenge

Write these queries using `@Query`:
- Find the average price of all products
- Find all products whose name starts with a given letter
- Update all products to be in stock where the price is less than a threshold
- Find the top 5 most expensive in-stock products

---

## What Is Next?

Now that you can perform CRUD operations, what happens when your database has thousands or millions of records? Returning all of them at once would be slow and wasteful. In the next chapter, you will learn about **Pagination and Sorting** -- how to return data in manageable chunks and in the order the user wants.
