# Chapter 7: Spring Data Derived Query Methods

---

## Learning Goals

By the end of this chapter, you will be able to:

- Write query methods using Spring Data JPA naming conventions
- Use all major query keywords (Between, Like, In, OrderBy, and more)
- Return different result types: List, Optional, Stream, and primitives
- Limit query results with First and Top
- Combine multiple conditions with And and Or
- Write delete and count query methods
- Use @Modifying for update and delete operations
- Debug derived query methods when they fail to parse

---

## How Derived Queries Work

Spring Data JPA reads your method name, parses it into parts, and generates JPQL (and ultimately SQL) automatically. You write zero query code — the method name IS the query.

```
Your Method Name                      What Spring Data Does
--------------------                  ----------------------------------------

findByEmail(String email)             1. Parses method name:
                                         find = query type
                                         By = predicate start
                                         Email = field name
                                      2. Generates JPQL:
                                         SELECT e FROM Employee e
                                         WHERE e.email = ?1
                                      3. Hibernate generates SQL:
                                         SELECT ... FROM employees
                                         WHERE email = ?
```

### The Parsing Formula

Every derived query method follows this structure:

```
+------------------------------------------------------------------+
|                                                                   |
|  [action] + By + [conditions] + [ordering]                        |
|                                                                   |
|  action:     find, read, get, query, search, stream,              |
|              count, exists, delete                                |
|                                                                   |
|  By:         separates the action from the conditions             |
|                                                                   |
|  conditions: FieldName + [Keyword] + And/Or + FieldName + ...     |
|              e.g., NameContaining, AgeGreaterThan,                |
|              EmailAndDepartment                                   |
|                                                                   |
|  ordering:   OrderByFieldAsc, OrderByFieldDesc                    |
|              (optional, at the end)                                |
|                                                                   |
+------------------------------------------------------------------+

Examples:
  findByName                    --> WHERE name = ?
  findByNameAndAge              --> WHERE name = ? AND age = ?
  findByAgeGreaterThanOrderByNameAsc
                                --> WHERE age > ? ORDER BY name ASC
  countByDepartment             --> SELECT COUNT(*) WHERE department = ?
  existsByEmail                 --> SELECT COUNT(*) > 0 WHERE email = ?
  deleteByActive                --> DELETE WHERE active = ?
```

---

## Setup: The Product Entity

For this chapter, we will use a `Product` entity with diverse field types:

```java
@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(nullable = false, unique = true, length = 20)
    private String sku;

    @Column(precision = 10, scale = 2)
    private BigDecimal price;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Category category;

    private int stockQuantity;

    private boolean active;

    private LocalDate launchDate;

    @Column(length = 100)
    private String brand;

    public enum Category {
        ELECTRONICS, CLOTHING, BOOKS, FOOD, HOME, SPORTS
    }

    // constructors, getters, setters, toString...
    public Product() {}

    public Product(String name, String sku, BigDecimal price,
                   Category category, int stock, String brand) {
        this.name = name;
        this.sku = sku;
        this.price = price;
        this.category = category;
        this.stockQuantity = stock;
        this.active = true;
        this.launchDate = LocalDate.now();
        this.brand = brand;
    }
}
```

---

## Equality and Simple Matching

### Exact Match

```java
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Find by exact field value
    List<Product> findByCategory(Product.Category category);
    // SQL: SELECT ... FROM products WHERE category = ?

    Optional<Product> findBySku(String sku);
    // SQL: SELECT ... FROM products WHERE sku = ?

    List<Product> findByActive(boolean active);
    // SQL: SELECT ... FROM products WHERE active = ?

    List<Product> findByBrand(String brand);
    // SQL: SELECT ... FROM products WHERE brand = ?
}
```

**Note**: `findBy` and `findAllBy` are equivalent. Both return a collection. For single results, use `Optional<T>` as the return type.

### Is, Equals (Synonyms for Exact Match)

```java
// These three are identical:
List<Product> findByCategory(Product.Category category);
List<Product> findByCategoryIs(Product.Category category);
List<Product> findByCategoryEquals(Product.Category category);
// All generate: WHERE category = ?
```

### Not, IsNot

```java
List<Product> findByCategoryNot(Product.Category category);
// SQL: WHERE category <> ?

List<Product> findByActiveIsNot(boolean active);
// SQL: WHERE active <> ?
```

---

## Comparison Keywords

### Numeric Comparisons

```java
// Greater than
List<Product> findByPriceGreaterThan(BigDecimal price);
// SQL: WHERE price > ?

// Greater than or equal
List<Product> findByPriceGreaterThanEqual(BigDecimal price);
// SQL: WHERE price >= ?

// Less than
List<Product> findByPriceLessThan(BigDecimal price);
// SQL: WHERE price < ?

// Less than or equal
List<Product> findByPriceLessThanEqual(BigDecimal price);
// SQL: WHERE price <= ?

// Between (inclusive on both ends)
List<Product> findByPriceBetween(BigDecimal min, BigDecimal max);
// SQL: WHERE price BETWEEN ? AND ?

// Stock quantity examples
List<Product> findByStockQuantityGreaterThan(int quantity);
// SQL: WHERE stock_quantity > ?

List<Product> findByStockQuantityLessThanEqual(int quantity);
// SQL: WHERE stock_quantity <= ?
```

### Date Comparisons

```java
// Products launched after a date
List<Product> findByLaunchDateAfter(LocalDate date);
// SQL: WHERE launch_date > ?

// Products launched before a date
List<Product> findByLaunchDateBefore(LocalDate date);
// SQL: WHERE launch_date < ?

// Products launched between two dates
List<Product> findByLaunchDateBetween(LocalDate start, LocalDate end);
// SQL: WHERE launch_date BETWEEN ? AND ?
```

### Keyword Reference: Comparisons

```
Keyword              SQL Equivalent        Example Method
----------------------------------------------------------------------
GreaterThan          >                     findByPriceGreaterThan
GreaterThanEqual     >=                    findByPriceGreaterThanEqual
LessThan             <                     findByPriceLessThan
LessThanEqual        <=                    findByPriceLessThanEqual
Between              BETWEEN x AND y       findByPriceBetween
After                >                     findByLaunchDateAfter
Before               <                     findByLaunchDateBefore
```

**Note**: `After` and `Before` are equivalent to `GreaterThan` and `LessThan` but read better with date fields.

---

## String Matching Keywords

### Like, NotLike

```java
// Requires caller to provide wildcards
List<Product> findByNameLike(String pattern);
// Usage: findByNameLike("%Widget%")
// SQL: WHERE name LIKE ?

List<Product> findByNameNotLike(String pattern);
// SQL: WHERE name NOT LIKE ?
```

### Containing, StartingWith, EndingWith

These methods add the `%` wildcards automatically:

```java
// Contains substring (adds % on both sides)
List<Product> findByNameContaining(String keyword);
// Usage: findByNameContaining("Widget")
// SQL: WHERE name LIKE '%Widget%'

// Starts with prefix (adds % on the right)
List<Product> findByNameStartingWith(String prefix);
// Usage: findByNameStartingWith("Super")
// SQL: WHERE name LIKE 'Super%'

// Ends with suffix (adds % on the left)
List<Product> findByNameEndingWith(String suffix);
// Usage: findByNameEndingWith("Pro")
// SQL: WHERE name LIKE '%Pro'
```

```
Like vs Containing vs StartingWith vs EndingWith:
+------------------------------------------------------------------+
|  Method                          Pattern Sent to SQL              |
|------------------------------------------------------------------|
|  findByNameLike("%Widget%")      WHERE name LIKE '%Widget%'       |
|  findByNameContaining("Widget")  WHERE name LIKE '%Widget%'       |
|  findByNameStartingWith("Wi")    WHERE name LIKE 'Wi%'            |
|  findByNameEndingWith("get")     WHERE name LIKE '%get'           |
|                                                                   |
|  Like:          You provide the % wildcards                       |
|  Containing:    % added on both sides automatically               |
|  StartingWith:  % added on right side automatically               |
|  EndingWith:    % added on left side automatically                |
+------------------------------------------------------------------+
```

### Case-Insensitive Matching

```java
// Ignore case for string comparisons
List<Product> findByNameIgnoreCase(String name);
// SQL: WHERE UPPER(name) = UPPER(?)

List<Product> findByNameContainingIgnoreCase(String keyword);
// SQL: WHERE UPPER(name) LIKE UPPER('%keyword%')

List<Product> findByBrandIgnoreCase(String brand);
// SQL: WHERE UPPER(brand) = UPPER(?)
```

### Keyword Reference: Strings

```
Keyword              SQL Equivalent        Wildcard Handling
----------------------------------------------------------------------
Like                 LIKE                  Manual (you add %)
NotLike              NOT LIKE              Manual
Containing           LIKE '%x%'            Automatic (both sides)
StartingWith         LIKE 'x%'             Automatic (right side)
EndingWith           LIKE '%x'             Automatic (left side)
IgnoreCase           UPPER(col)=UPPER(?)   Case-insensitive
```

---

## Null Checking

```java
// Field is null
List<Product> findByBrandIsNull();
// SQL: WHERE brand IS NULL

// Field is not null
List<Product> findByBrandIsNotNull();
// SQL: WHERE brand IS NOT NULL

// Also valid syntax:
List<Product> findByBrandNull();        // Same as IsNull
List<Product> findByBrandNotNull();     // Same as IsNotNull
```

---

## Boolean Keywords

```java
// True
List<Product> findByActiveTrue();
// SQL: WHERE active = true

// False
List<Product> findByActiveFalse();
// SQL: WHERE active = false
```

These are cleaner than `findByActive(true)` when you always query for a specific boolean value.

---

## Collection Keywords: In and NotIn

```java
// Find products in a set of categories
List<Product> findByCategoryIn(Collection<Product.Category> categories);
// Usage: findByCategoryIn(List.of(Category.ELECTRONICS, Category.BOOKS))
// SQL: WHERE category IN (?, ?)

// Find products NOT in a set of categories
List<Product> findByCategoryNotIn(Collection<Product.Category> categories);
// SQL: WHERE category NOT IN (?, ?)

// Works with any field type
List<Product> findByBrandIn(Collection<String> brands);
// Usage: findByBrandIn(List.of("Apple", "Samsung", "Sony"))
// SQL: WHERE brand IN (?, ?, ?)
```

---

## Combining Conditions: And, Or

### And (Both conditions must match)

```java
// Two conditions
List<Product> findByCategoryAndActive(Product.Category category, boolean active);
// SQL: WHERE category = ? AND active = ?

// Three conditions
List<Product> findByCategoryAndActiveAndPriceGreaterThan(
    Product.Category category, boolean active, BigDecimal price);
// SQL: WHERE category = ? AND active = ? AND price > ?

// String + numeric
List<Product> findByBrandAndPriceLessThan(String brand, BigDecimal price);
// SQL: WHERE brand = ? AND price < ?
```

### Or (Either condition must match)

```java
List<Product> findByCategoryOrBrand(Product.Category category, String brand);
// SQL: WHERE category = ? OR brand = ?

List<Product> findByPriceLessThanOrStockQuantityGreaterThan(
    BigDecimal price, int stock);
// SQL: WHERE price < ? OR stock_quantity > ?
```

### Combining And with Or

For complex conditions mixing And and Or, the method name becomes unwieldy. Use `@Query` instead (Chapter 8):

```java
// This works but is hard to read:
List<Product> findByCategoryAndPriceGreaterThanOrBrandAndActiveTrue(
    Product.Category cat, BigDecimal price, String brand);
// SQL: WHERE (category = ? AND price > ?) OR (brand = ? AND active = true)

// Better: Use @Query for complex logic (Chapter 8)
```

---

## Ordering Results

### OrderBy in Method Name

```java
// Ascending (default)
List<Product> findByCategoryOrderByNameAsc(Product.Category category);
// SQL: WHERE category = ? ORDER BY name ASC

// Descending
List<Product> findByCategoryOrderByPriceDesc(Product.Category category);
// SQL: WHERE category = ? ORDER BY price DESC

// Multiple sort fields
List<Product> findByCategoryOrderByPriceDescNameAsc(Product.Category category);
// SQL: WHERE category = ? ORDER BY price DESC, name ASC

// Order all results (no filter)
List<Product> findAllByOrderByNameAsc();
// SQL: SELECT ... FROM products ORDER BY name ASC
// Note: "AllBy" + "OrderBy" — the By after All is required
```

### Sort Parameter (More Flexible)

Instead of baking the sort order into the method name, pass a `Sort` parameter:

```java
// Method definition — accepts Sort parameter
List<Product> findByCategory(Product.Category category, Sort sort);

// Usage — sort is decided at call time
List<Product> cheapest = repository.findByCategory(
    Category.ELECTRONICS,
    Sort.by("price").ascending()
);

List<Product> newest = repository.findByCategory(
    Category.ELECTRONICS,
    Sort.by("launchDate").descending()
);

// Multiple sort fields
List<Product> sorted = repository.findByCategory(
    Category.ELECTRONICS,
    Sort.by(Sort.Order.desc("price"), Sort.Order.asc("name"))
);
```

```
OrderBy in method name vs Sort parameter:
+------------------------------------------------------------------+
|  OrderBy in Name                  Sort Parameter                  |
|  findByCategoryOrderByPriceDesc   findByCategory(cat, Sort)       |
|                                                                   |
|  Fixed sort order                 Flexible sort order             |
|  Sort is part of the method       Sort is decided by caller       |
|  Simpler for one sort order       Better when sort varies         |
|  New method for each sort         One method handles all sorts    |
+------------------------------------------------------------------+
```

---

## Limiting Results: First, Top

### First and Top

```java
// Get the first result
Optional<Product> findFirstByCategoryOrderByPriceAsc(Product.Category category);
// SQL: WHERE category = ? ORDER BY price ASC LIMIT 1
// Returns the cheapest product in a category

// Get the top result (same as First)
Optional<Product> findTopByCategoryOrderByPriceDesc(Product.Category category);
// SQL: WHERE category = ? ORDER BY price DESC LIMIT 1
// Returns the most expensive product in a category

// Get top N results
List<Product> findTop3ByCategoryOrderByPriceDesc(Product.Category category);
// SQL: WHERE category = ? ORDER BY price DESC LIMIT 3
// Returns the 3 most expensive products

List<Product> findFirst5ByOrderByLaunchDateDesc();
// SQL: SELECT ... FROM products ORDER BY launch_date DESC LIMIT 5
// Returns the 5 most recently launched products

// Count variant
List<Product> findTop10ByActiveTrueOrderByStockQuantityAsc();
// SQL: WHERE active = true ORDER BY stock_quantity ASC LIMIT 10
// Returns 10 products with lowest stock
```

```
First vs Top:
+------------------------------------------------------------------+
|  "First" and "Top" are synonyms — they behave identically         |
|                                                                   |
|  findFirst...     = findTop...                                    |
|  findFirst3...    = findTop3...                                   |
|  findFirst10...   = findTop10...                                  |
|                                                                   |
|  Without a number: returns 1 result (Optional<T> or T)            |
|  With a number N:  returns up to N results (List<T>)              |
+------------------------------------------------------------------+
```

---

## Return Types

Derived query methods support various return types:

```
Return Type           When to Use                     Example
----------------------------------------------------------------------
List<T>               Multiple results expected       findByCategory(cat)
Optional<T>           Zero or one result              findBySku(sku)
T                     Exactly one result (risky)      findBySku(sku)
                      Throws if not found!
Stream<T>             Process results lazily           streamByCategory(cat)
long                  Count queries                   countByCategory(cat)
boolean               Existence checks                existsBySku(sku)
void                  Delete methods                  deleteByCategory(cat)
Page<T>               Paginated results               findByCategory(cat, pageable)
Slice<T>              Paginated without total count   findByCategory(cat, pageable)
```

### Stream Return Type

```java
// Returns a Java Stream for lazy processing
@QueryHints(@QueryHint(name = HINT_FETCH_SIZE, value = "25"))
Stream<Product> streamByCategory(Product.Category category);
```

```java
// Usage — MUST be in @Transactional and close the stream
@Transactional(readOnly = true)
public void processExpensiveProducts() {
    try (Stream<Product> stream = repository.streamByCategory(Category.ELECTRONICS)) {
        stream
            .filter(p -> p.getPrice().compareTo(new BigDecimal("500")) > 0)
            .forEach(p -> System.out.println("Expensive: " + p.getName()));
    }
}
```

**Important**: Streams from repositories must be used within a `@Transactional` context and should be closed (use try-with-resources).

---

## Count and Exists Methods

### Count

```java
// Count by field value
long countByCategory(Product.Category category);
// SQL: SELECT COUNT(*) FROM products WHERE category = ?

long countByActiveTrue();
// SQL: SELECT COUNT(*) FROM products WHERE active = true

long countByPriceGreaterThan(BigDecimal price);
// SQL: SELECT COUNT(*) FROM products WHERE price > ?

long countByBrandAndCategory(String brand, Product.Category category);
// SQL: SELECT COUNT(*) FROM products WHERE brand = ? AND category = ?
```

### Exists

```java
// Check existence
boolean existsBySku(String sku);
// SQL: SELECT COUNT(*) FROM products WHERE sku = ?
// Returns true if count > 0

boolean existsByNameContaining(String keyword);
// SQL: SELECT COUNT(*) FROM products WHERE name LIKE '%keyword%'

boolean existsByCategoryAndActiveTrue(Product.Category category);
// SQL: SELECT COUNT(*) FROM products WHERE category = ? AND active = true
```

---

## Delete Methods

### Derived Delete Methods

```java
// Delete by field value
void deleteByCategory(Product.Category category);
// SQL: SELECT ... WHERE category = ?   (loads entities)
//      DELETE FROM products WHERE id = ?   (per entity)

long deleteByActiveFalse();
// Returns the count of deleted entities
// SQL: Same as above — loads then deletes individually

void deleteByBrand(String brand);
// SQL: loads by brand, deletes each individually

// With @Transactional (required for delete methods)
@Transactional
public void removeInactiveProducts() {
    long count = productRepository.deleteByActiveFalse();
    System.out.println("Deleted " + count + " inactive products");
}
```

### How Derived Deletes Work

```
Derived delete flow:
+------------------------------------------------------------------+
|  deleteByCategory(ELECTRONICS)                                    |
|    |                                                              |
|    v                                                              |
|  1. SELECT ... FROM products WHERE category = 'ELECTRONICS'       |
|     (loads ALL matching entities into persistence context)        |
|    |                                                              |
|    v                                                              |
|  2. For EACH entity:                                              |
|     - @PreRemove callback fires                                   |
|     - entityManager.remove(entity)                                |
|     - DELETE FROM products WHERE id = ?                           |
|     - @PostRemove callback fires                                  |
|    |                                                              |
|    v                                                              |
|  Result: N SELECT + N DELETE statements                           |
|  (not efficient for bulk deletes!)                                |
+------------------------------------------------------------------+
```

**Important**: Derived delete methods load entities first and delete them one by one. For bulk deletes, use `@Query` with `@Modifying` (covered below) or `deleteInBatch()`.

---

## @Modifying for Bulk Updates and Deletes

When you need to update or delete many rows efficiently (without loading entities), use `@Query` with `@Modifying`:

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // Bulk UPDATE — single SQL statement, no entity loading
    @Modifying
    @Query("UPDATE Product p SET p.active = false WHERE p.category = :category")
    int deactivateByCategory(@Param("category") Product.Category category);
    // Returns the number of rows updated

    // Bulk DELETE — single SQL statement, no entity loading
    @Modifying
    @Query("DELETE FROM Product p WHERE p.active = false")
    int deleteInactiveProducts();
    // Returns the number of rows deleted

    // Bulk UPDATE with multiple fields
    @Modifying
    @Query("UPDATE Product p SET p.price = p.price * :multiplier " +
           "WHERE p.category = :category")
    int adjustPriceByCategory(@Param("multiplier") BigDecimal multiplier,
                              @Param("category") Product.Category category);
}
```

```
Derived delete vs @Modifying delete:
+------------------------------------------------------------------+
|  Derived: deleteByActiveFalse()                                   |
|    --> SELECT all inactive products (loads into memory)            |
|    --> DELETE each one individually                                |
|    --> N+1 SQL statements                                         |
|    --> Lifecycle callbacks fire                                    |
|                                                                   |
|  @Modifying: @Query("DELETE FROM Product WHERE active = false")   |
|    --> Single DELETE statement                                    |
|    --> No entities loaded into memory                              |
|    --> 1 SQL statement                                            |
|    --> Lifecycle callbacks do NOT fire                             |
+------------------------------------------------------------------+
```

### @Modifying with clearAutomatically

After a `@Modifying` query, the persistence context might contain stale data (entities that were updated in the database but not in memory). Use `clearAutomatically = true` to clear the cache:

```java
@Modifying(clearAutomatically = true)
@Query("UPDATE Product p SET p.price = p.price * 1.1 WHERE p.category = :cat")
int applyPriceIncrease(@Param("cat") Product.Category category);
// After this runs, all managed entities are cleared from the cache
// Next findById will load fresh data from the database
```

```
Without clearAutomatically:
+------------------------------------------------------------------+
|  Product p = findById(1L);      // price = 100.00 (cached)        |
|  applyPriceIncrease(ELECTRONICS); // DB: price = 110.00           |
|  Product p2 = findById(1L);    // price = 100.00 (STALE CACHE!)  |
+------------------------------------------------------------------+

With clearAutomatically = true:
+------------------------------------------------------------------+
|  Product p = findById(1L);      // price = 100.00 (cached)        |
|  applyPriceIncrease(ELECTRONICS); // DB: price = 110.00           |
|  // Persistence context cleared automatically                     |
|  Product p2 = findById(1L);    // price = 110.00 (fresh from DB) |
+------------------------------------------------------------------+
```

---

## Complete Repository Example

Here is a comprehensive repository showcasing all the query method patterns:

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    // === Exact Match ===
    Optional<Product> findBySku(String sku);
    List<Product> findByCategory(Product.Category category);
    List<Product> findByBrand(String brand);
    List<Product> findByActiveTrue();
    List<Product> findByActiveFalse();

    // === Comparisons ===
    List<Product> findByPriceGreaterThan(BigDecimal price);
    List<Product> findByPriceLessThanEqual(BigDecimal price);
    List<Product> findByPriceBetween(BigDecimal min, BigDecimal max);
    List<Product> findByStockQuantityLessThan(int quantity);
    List<Product> findByLaunchDateAfter(LocalDate date);
    List<Product> findByLaunchDateBetween(LocalDate start, LocalDate end);

    // === String Matching ===
    List<Product> findByNameContaining(String keyword);
    List<Product> findByNameContainingIgnoreCase(String keyword);
    List<Product> findByNameStartingWith(String prefix);
    List<Product> findByBrandIgnoreCase(String brand);

    // === Null Checks ===
    List<Product> findByBrandIsNull();
    List<Product> findByBrandIsNotNull();

    // === Collections ===
    List<Product> findByCategoryIn(Collection<Product.Category> categories);
    List<Product> findByBrandIn(Collection<String> brands);

    // === Combined Conditions ===
    List<Product> findByCategoryAndActiveTrue(Product.Category category);
    List<Product> findByBrandAndPriceLessThan(String brand, BigDecimal price);
    List<Product> findByCategoryAndPriceBetween(
        Product.Category category, BigDecimal min, BigDecimal max);

    // === Ordering ===
    List<Product> findByCategoryOrderByPriceAsc(Product.Category category);
    List<Product> findByActiveTrueOrderByLaunchDateDesc();
    List<Product> findByCategory(Product.Category category, Sort sort);

    // === Limiting ===
    Optional<Product> findFirstByCategoryOrderByPriceAsc(Product.Category cat);
    List<Product> findTop5ByCategoryOrderByPriceDesc(Product.Category cat);
    List<Product> findFirst10ByOrderByLaunchDateDesc();

    // === Count and Exists ===
    long countByCategory(Product.Category category);
    long countByActiveTrue();
    boolean existsBySku(String sku);
    boolean existsByCategoryAndPriceGreaterThan(
        Product.Category category, BigDecimal price);

    // === Derived Deletes ===
    @Transactional
    long deleteByActiveFalse();

    @Transactional
    void deleteByCategory(Product.Category category);

    // === Bulk Operations with @Modifying ===
    @Modifying(clearAutomatically = true)
    @Query("UPDATE Product p SET p.active = false WHERE p.category = :category")
    int deactivateByCategory(@Param("category") Product.Category category);

    @Modifying(clearAutomatically = true)
    @Query("DELETE FROM Product p WHERE p.active = false AND p.stockQuantity = 0")
    int removeDeadStock();
}
```

---

## Testing Derived Queries

Here is a DataLoader that tests various query methods:

```java
@Component
public class QueryDemoRunner implements CommandLineRunner {

    private final ProductRepository repository;

    public QueryDemoRunner(ProductRepository repository) {
        this.repository = repository;
    }

    @Override
    public void run(String... args) {
        seedData();
        runQueries();
    }

    private void seedData() {
        repository.saveAll(List.of(
            new Product("Laptop Pro 15", "LAP-001", new BigDecimal("1299.99"),
                Product.Category.ELECTRONICS, 50, "Apple"),
            new Product("Wireless Mouse", "MOU-001", new BigDecimal("29.99"),
                Product.Category.ELECTRONICS, 200, "Logitech"),
            new Product("Java Programming", "BOK-001", new BigDecimal("49.99"),
                Product.Category.BOOKS, 100, null),
            new Product("Running Shoes", "SHO-001", new BigDecimal("89.99"),
                Product.Category.SPORTS, 75, "Nike"),
            new Product("Cotton T-Shirt", "TSH-001", new BigDecimal("19.99"),
                Product.Category.CLOTHING, 300, "Uniqlo"),
            new Product("Bluetooth Speaker", "SPK-001", new BigDecimal("79.99"),
                Product.Category.ELECTRONICS, 0, "Sony"),
            new Product("Cookbook Basics", "BOK-002", new BigDecimal("34.99"),
                Product.Category.BOOKS, 60, null),
            new Product("Laptop Stand", "STD-001", new BigDecimal("45.99"),
                Product.Category.ELECTRONICS, 150, "Amazon")
        ));
    }

    private void runQueries() {
        System.out.println("\n=== Derived Query Demonstrations ===\n");

        // Exact match
        System.out.println("--- Electronics ---");
        repository.findByCategory(Product.Category.ELECTRONICS)
            .forEach(p -> System.out.println("  " + p.getName() + " - $" + p.getPrice()));

        // Price range
        System.out.println("\n--- Price $30-$100 ---");
        repository.findByPriceBetween(new BigDecimal("30"), new BigDecimal("100"))
            .forEach(p -> System.out.println("  " + p.getName() + " - $" + p.getPrice()));

        // String search
        System.out.println("\n--- Name containing 'Laptop' ---");
        repository.findByNameContainingIgnoreCase("laptop")
            .forEach(p -> System.out.println("  " + p.getName()));

        // Null check
        System.out.println("\n--- No brand ---");
        repository.findByBrandIsNull()
            .forEach(p -> System.out.println("  " + p.getName()));

        // Combined conditions
        System.out.println("\n--- Electronics under $100 ---");
        repository.findByBrandAndPriceLessThan("Apple", new BigDecimal("2000"))
            .forEach(p -> System.out.println("  " + p.getName() + " - $" + p.getPrice()));

        // Top N
        System.out.println("\n--- Top 3 most expensive electronics ---");
        repository.findTop5ByCategoryOrderByPriceDesc(Product.Category.ELECTRONICS)
            .forEach(p -> System.out.println("  " + p.getName() + " - $" + p.getPrice()));

        // Cheapest in category
        System.out.println("\n--- Cheapest electronic ---");
        repository.findFirstByCategoryOrderByPriceAsc(Product.Category.ELECTRONICS)
            .ifPresent(p -> System.out.println("  " + p.getName() + " - $" + p.getPrice()));

        // Count
        System.out.println("\n--- Counts ---");
        System.out.println("  Electronics: " + repository.countByCategory(Product.Category.ELECTRONICS));
        System.out.println("  Books: " + repository.countByCategory(Product.Category.BOOKS));
        System.out.println("  Active: " + repository.countByActiveTrue());

        // Exists
        System.out.println("\n--- Exists ---");
        System.out.println("  SKU LAP-001: " + repository.existsBySku("LAP-001"));
        System.out.println("  SKU XXX-999: " + repository.existsBySku("XXX-999"));

        // Sort parameter
        System.out.println("\n--- Electronics sorted by price ascending ---");
        repository.findByCategory(Product.Category.ELECTRONICS,
                Sort.by("price").ascending())
            .forEach(p -> System.out.println("  " + p.getName() + " - $" + p.getPrice()));
    }
}
```

---

## Complete Keyword Reference

```
Keyword              Example                           SQL Clause
----------------------------------------------------------------------
And                  findByNameAndPrice                WHERE x=? AND y=?
Or                   findByNameOrPrice                 WHERE x=? OR y=?
Is, Equals           findByName, findByNameIs          WHERE x = ?
Not, IsNot           findByNameNot                     WHERE x <> ?
Between              findByPriceBetween                WHERE x BETWEEN ? AND ?
LessThan             findByPriceLessThan               WHERE x < ?
LessThanEqual        findByPriceLessThanEqual          WHERE x <= ?
GreaterThan          findByPriceGreaterThan            WHERE x > ?
GreaterThanEqual     findByPriceGreaterThanEqual       WHERE x >= ?
After                findByDateAfter                   WHERE x > ?
Before               findByDateBefore                  WHERE x < ?
IsNull, Null         findByBrandIsNull                 WHERE x IS NULL
IsNotNull, NotNull   findByBrandIsNotNull              WHERE x IS NOT NULL
Like                 findByNameLike                    WHERE x LIKE ?
NotLike              findByNameNotLike                 WHERE x NOT LIKE ?
Containing           findByNameContaining              WHERE x LIKE '%?%'
StartingWith         findByNameStartingWith            WHERE x LIKE '?%'
EndingWith           findByNameEndingWith              WHERE x LIKE '%?'
IgnoreCase           findByNameIgnoreCase              WHERE UPPER(x)=UPPER(?)
In                   findByCategoryIn                  WHERE x IN (?)
NotIn                findByCategoryNotIn               WHERE x NOT IN (?)
True                 findByActiveTrue                  WHERE x = true
False                findByActiveFalse                 WHERE x = false
OrderBy              ...OrderByNameAsc                 ORDER BY x ASC
Not                  findByNameNot                     WHERE x <> ?
First, Top           findFirst3By...                   LIMIT 3
```

---

## Debugging Derived Queries

### Common Error: Property Not Found

```
PropertyReferenceException:
No property 'emailAddress' found for type 'Product'
```

This means the field name in your method does not match the entity field name. Check for typos:

```java
// Entity has field: private String email;

// WRONG: emailAddress does not match
List<Product> findByEmailAddress(String email);

// CORRECT: matches the field name
List<Product> findByEmail(String email);
```

### Common Error: Ambiguous Property Path

If your entity has nested objects (covered in later chapters), Spring Data might misparse the method name:

```java
// Entity has: private String orderDate;
// AND also:   private Order order; (with field date inside)

// Spring might parse "OrderDate" as "order.date" instead of "orderDate"
List<Product> findByOrderDate(LocalDate date);

// Fix: Use underscores to force correct parsing
List<Product> findByOrder_Date(LocalDate date);  // order.date
// vs
List<Product> findByOrderDate(LocalDate date);    // orderDate field
```

### Verifying Generated SQL

Always check the SQL generated by your derived queries. Enable SQL logging:

```properties
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

Then call the method and verify the SQL in the console matches your intent.

---

## Common Mistakes

1. **Method name does not match field name**: `findByUserName` fails if the field is `username` (one word). The method name is parsed based on camelCase — each capital letter starts a new word.

2. **Using Like without wildcards**: `findByNameLike("Widget")` generates `WHERE name LIKE 'Widget'` (exact match, not a pattern). Use `findByNameContaining("Widget")` instead, which adds `%` automatically.

3. **Expecting derived deletes to be efficient**: `deleteByCategory(BOOKS)` loads all matching entities then deletes them one by one. For bulk deletes, use `@Modifying` with `@Query`.

4. **Missing @Transactional on delete methods**: Derived delete and `@Modifying` methods require a transaction. Either annotate the calling service method with `@Transactional` or put `@Transactional` on the repository method.

5. **Forgetting clearAutomatically on @Modifying**: After a bulk UPDATE, cached entities in the persistence context are stale. Use `@Modifying(clearAutomatically = true)` to avoid reading outdated data.

6. **Method names that are too long**: `findByCategoryAndActiveTrueAndPriceGreaterThanAndBrandNotNullOrderByPriceAsc` is technically valid but unreadable. Use `@Query` for complex queries.

---

## Best Practices

1. **Use Containing instead of Like**: `findByNameContaining("Widget")` is cleaner than `findByNameLike("%Widget%")` because wildcards are handled automatically.

2. **Use Sort parameter for flexible ordering**: Instead of creating multiple methods with different OrderBy clauses, create one method that accepts a `Sort` parameter.

3. **Return Optional for single-result queries**: When a query should return zero or one result, use `Optional<T>`. This forces callers to handle the empty case.

4. **Use @Modifying for bulk operations**: When updating or deleting many rows, `@Modifying` with `@Query` is much more efficient than derived methods.

5. **Keep method names readable**: If a method name exceeds ~60 characters, switch to `@Query` with JPQL (Chapter 8). Readability matters more than avoiding SQL.

6. **Use IgnoreCase for user-facing searches**: When users search by name or title, they do not expect case-sensitive matching. Add `IgnoreCase` to string search methods.

---

## Summary

In this chapter, you learned how to write queries simply by naming methods:

- **Derived query methods** are parsed from method names into JPQL and SQL. Spring Data JPA supports dozens of keywords for building queries without writing any query language.

- **Comparison keywords** (GreaterThan, LessThan, Between, After, Before) handle numeric and date comparisons.

- **String keywords** (Containing, StartingWith, EndingWith, Like, IgnoreCase) handle text searching with automatic wildcard management.

- **Logical operators** (And, Or) combine multiple conditions. For complex logic, prefer `@Query`.

- **Result limiting** (First, Top, Top3, Top10) returns a subset of results, useful for "most recent" or "top N" queries.

- **Return types** include List, Optional, Stream, long (count), boolean (exists), and void (deletes).

- **Sort parameter** allows flexible ordering without creating multiple methods.

- **@Modifying** enables efficient bulk UPDATE and DELETE operations with a single SQL statement.

---

## Interview Questions

**Q1: How does Spring Data JPA generate a query from a method name?**

Spring Data parses the method name into components: the action prefix (find, count, exists, delete), the By keyword, field names, condition keywords (GreaterThan, Containing, etc.), logical operators (And, Or), and ordering (OrderBy). It maps field names to entity properties and keywords to JPQL/SQL clauses, then generates the query automatically at application startup.

**Q2: What is the difference between findByNameLike and findByNameContaining?**

`findByNameLike` expects the caller to provide the wildcard characters (e.g., `"%Widget%"`). `findByNameContaining` automatically wraps the parameter with `%` on both sides. Similarly, `StartingWith` adds `%` on the right, and `EndingWith` adds `%` on the left.

**Q3: How do you limit query results in derived methods?**

Use `First` or `Top` keywords. `findFirstByOrderByPriceAsc()` returns the single cheapest product. `findTop5ByOrderByPriceDesc()` returns the five most expensive. Without a number, it returns one result; with a number N, it returns up to N results.

**Q4: What is the difference between a derived delete method and a @Modifying delete?**

A derived delete method (`deleteByCategory(cat)`) loads all matching entities into the persistence context, fires lifecycle callbacks (@PreRemove), and deletes them one by one with individual DELETE statements. A `@Modifying @Query("DELETE FROM Product p WHERE p.category = :cat")` executes a single DELETE SQL statement, does not load entities, and does not fire lifecycle callbacks. @Modifying is much faster for bulk operations.

**Q5: What does @Modifying(clearAutomatically = true) do?**

After executing a bulk UPDATE or DELETE query, the persistence context may contain stale entities that no longer match the database state. `clearAutomatically = true` clears the entire persistence context after the query executes, ensuring subsequent queries fetch fresh data from the database.

**Q6: When should you use a Sort parameter instead of OrderBy in the method name?**

Use a Sort parameter when the sort order needs to be flexible — when different callers might want different orderings. Use OrderBy in the method name when the sort order is fixed and always the same. Sort parameters avoid creating multiple methods with different OrderBy clauses.

**Q7: Can you combine And and Or in derived query methods?**

Yes, but the behavior can be confusing because And takes precedence over Or (just like in SQL). For complex conditions mixing And and Or, the method name becomes long and hard to read. It is better to use `@Query` with JPQL for complex logic.

**Q8: How do you debug a derived query method that is not working correctly?**

Enable SQL logging (`spring.jpa.show-sql=true`) and parameter logging (`logging.level.org.hibernate.orm.jdbc.bind=TRACE`). Call the method and compare the generated SQL with your expected query. Common issues include: property name mismatches (check field names), wrong keyword usage (e.g., Like without wildcards), and ambiguous property paths in entities with nested objects.

---

## Practice Exercises

**Exercise 1: Employee Queries**
Create an `EmployeeRepository` with derived methods for:
- Find by department
- Find by salary greater than a given amount
- Find by name containing a keyword (case-insensitive)
- Find by department and salary between two values
- Find the top 3 highest-paid employees
- Count employees by department
- Check if an email exists

Test each method with sample data and verify the generated SQL.

**Exercise 2: Keyword Exploration**
For the Product entity, write derived query methods that use each of these keywords at least once: Between, Containing, IgnoreCase, In, IsNull, True, OrderBy, First, And, Or. Verify each generates correct SQL.

**Exercise 3: Sort Flexibility**
Create a method `findByActiveTrue(Sort sort)`. Call it with five different Sort configurations: by name ascending, by price descending, by stock ascending, by launch date descending, and by category ascending then price descending. Verify each produces the correct ORDER BY clause.

**Exercise 4: Bulk Operations**
Create @Modifying methods to: (a) deactivate all products with stock = 0, (b) increase prices by 10% for a given category, (c) delete all inactive products. Compare the SQL generated versus equivalent derived methods.

**Exercise 5: Search Feature**
Build a simple product search feature using derived methods. Create methods for:
- Search by name keyword (case-insensitive)
- Filter by category
- Filter by price range
- Filter by brand (in a list of brands)
- Combine: search by name AND category AND price range
Write a service method that calls each one with test data.

---

## What Is Next?

In the next chapter, we will explore **JPQL — The JPA Query Language**. While derived query methods are powerful, they have limits — you cannot express joins, aggregate functions, subqueries, or complex conditions through method names alone. JPQL gives you full query power while remaining database-independent. You will learn SELECT, WHERE, JOIN, GROUP BY, aggregate functions, named parameters, and how to use `@Query` for custom queries that go beyond what method names can express.
