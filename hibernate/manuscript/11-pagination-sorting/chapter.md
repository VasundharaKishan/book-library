# Chapter 11: Pagination, Sorting, and Query Optimization

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand why pagination is essential for performance and user experience
- Use Pageable, PageRequest, and Sort to paginate and sort query results
- Distinguish between Page, Slice, and List return types
- Implement pagination with derived methods, JPQL, native SQL, and Specifications
- Sort by multiple fields and handle custom sort mappings
- Write custom count queries for complex paginated queries
- Use @EntityGraph to optimize fetching at the query level
- Solve the N+1 problem with fetch joins and entity graphs
- Apply @QueryHints for query plan caching

---

## Why Pagination Matters

Without pagination, a query returns every matching row. This works when you have 50 employees but fails catastrophically with 500,000.

```
Without Pagination:
+------------------------------------------------------------------+
|                                                                   |
|  Client                       Server                  Database    |
|    |                            |                        |        |
|    |  GET /api/employees        |                        |        |
|    |--------------------------->|                        |        |
|    |                            |  SELECT * FROM         |        |
|    |                            |  employees             |        |
|    |                            |----------------------->|        |
|    |                            |                        |        |
|    |                            |  500,000 rows          |        |
|    |                            |<-----------------------|        |
|    |                            |                        |        |
|    |  500,000 JSON objects      |                        |        |
|    |  (50 MB response!)         |                        |        |
|    |<---------------------------|                        |        |
|    |                            |                        |        |
|  Problems:                                                        |
|  - Database loads ALL rows into memory                            |
|  - Server converts ALL rows to JSON                               |
|  - Network transfers 50 MB                                        |
|  - Client tries to render 500,000 items                           |
|  - Everyone is unhappy                                            |
+------------------------------------------------------------------+

With Pagination:
+------------------------------------------------------------------+
|                                                                   |
|  Client                       Server                  Database    |
|    |                            |                        |        |
|    |  GET /api/employees        |                        |        |
|    |    ?page=0&size=20         |                        |        |
|    |--------------------------->|                        |        |
|    |                            |  SELECT * FROM         |        |
|    |                            |  employees             |        |
|    |                            |  LIMIT 20 OFFSET 0     |        |
|    |                            |----------------------->|        |
|    |                            |                        |        |
|    |                            |  20 rows               |        |
|    |                            |<-----------------------|        |
|    |                            |                        |        |
|    |  20 JSON objects           |                        |        |
|    |  + metadata (total: 500K)  |                        |        |
|    |<---------------------------|                        |        |
|    |                            |                        |        |
|  Result:                                                          |
|  - Database reads only 20 rows                                    |
|  - Fast response, small payload                                   |
|  - Client renders one page at a time                              |
+------------------------------------------------------------------+
```

---

## Pageable, PageRequest, and Sort

Spring Data JPA provides three core types for pagination:

```
Pagination Types:
+------------------------------------------------------------------+
|                                                                   |
|  Pageable (interface)                                             |
|  +----------------------------+                                   |
|  | Defines WHAT to retrieve:  |                                   |
|  | - Page number (0-based)    |                                   |
|  | - Page size                |                                   |
|  | - Sort order               |                                   |
|  +----------------------------+                                   |
|           |                                                       |
|  PageRequest (implementation)                                     |
|  +----------------------------+                                   |
|  | Creates a Pageable:        |                                   |
|  | PageRequest.of(0, 20)      |                                   |
|  | PageRequest.of(0, 20,      |                                   |
|  |   Sort.by("name"))         |                                   |
|  +----------------------------+                                   |
|           |                                                       |
|  Sort                                                             |
|  +----------------------------+                                   |
|  | Defines ordering:          |                                   |
|  | Sort.by("name")            |                                   |
|  | Sort.by("name").ascending()|                                   |
|  | Sort.by("salary").desc()   |                                   |
|  | Sort.by("dept", "name")    |                                   |
|  +----------------------------+                                   |
|                                                                   |
+------------------------------------------------------------------+
```

### Creating PageRequest

```java
// Page 0 (first page), 20 items per page, no sorting
Pageable pageable = PageRequest.of(0, 20);

// Page 2 (third page), 10 items per page
Pageable pageable = PageRequest.of(2, 10);

// With sorting
Pageable pageable = PageRequest.of(0, 20, Sort.by("name"));

// With descending sort
Pageable pageable = PageRequest.of(0, 20, Sort.by("salary").descending());

// With direction parameter
Pageable pageable = PageRequest.of(0, 20, Sort.Direction.DESC, "salary");

// With multiple sort fields
Pageable pageable = PageRequest.of(0, 20,
    Sort.by("department.name").ascending()
        .and(Sort.by("salary").descending()));
```

```
Page Numbering (0-based):
+------------------------------------------------------------------+
|                                                                   |
|  Data: [A, B, C, D, E, F, G, H, I, J, K, L, M, N, O]           |
|  Page size: 5                                                     |
|                                                                   |
|  Page 0: [A, B, C, D, E]    (offset 0)                           |
|  Page 1: [F, G, H, I, J]    (offset 5)                           |
|  Page 2: [K, L, M, N, O]    (offset 10)                          |
|                                                                   |
|  Total elements: 15                                               |
|  Total pages: 3                                                   |
|  Page 0 is the first page (not page 1!)                           |
+------------------------------------------------------------------+
```

---

## Sort API

Spring Data's `Sort` class provides a fluent API for defining sort orders:

```java
// Single field, ascending (default)
Sort sort = Sort.by("name");

// Single field, explicit direction
Sort sort = Sort.by(Sort.Direction.ASC, "name");
Sort sort = Sort.by(Sort.Direction.DESC, "salary");

// Fluent ascending / descending
Sort sort = Sort.by("salary").descending();
Sort sort = Sort.by("name").ascending();

// Multiple fields
Sort sort = Sort.by("department").ascending()
               .and(Sort.by("salary").descending());

// Shorthand for multiple fields, same direction
Sort sort = Sort.by(Sort.Direction.ASC, "lastName", "firstName");

// Unsorted
Sort sort = Sort.unsorted();

// Null handling (JPA standard)
Sort sort = Sort.by("email")
    .ascending()
    .nullsLast();  // or .nullsFirst()
```

### Sort with Repository Methods

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // Sort parameter on derived methods
    List<Employee> findByActive(boolean active, Sort sort);

    // Sort parameter with JPQL
    @Query("SELECT e FROM Employee e WHERE e.department.name = :dept")
    List<Employee> findByDepartment(@Param("dept") String dept, Sort sort);
}

// Usage
List<Employee> sorted = repository.findByActive(true,
    Sort.by("salary").descending());
```

---

## Page vs Slice vs List

Spring Data JPA offers three return types for paginated queries, each with different performance characteristics:

```
Return Type Comparison:
+------------------------------------------------------------------+
|                                                                   |
|  Page<T>                                                          |
|  +---------------------------------+                              |
|  | Content: List<T>                |  Executes TWO queries:       |
|  | Page number: 0                  |  1. SELECT ... LIMIT/OFFSET  |
|  | Page size: 20                   |  2. SELECT COUNT(*)          |
|  | Total elements: 1,542          |                              |
|  | Total pages: 78                |  Use when: UI needs total    |
|  | Has next: true                 |  page count (page 1 of 78)  |
|  | Has previous: false            |                              |
|  +---------------------------------+                              |
|                                                                   |
|  Slice<T>                                                         |
|  +---------------------------------+                              |
|  | Content: List<T>                |  Executes ONE query:         |
|  | Page number: 0                  |  SELECT ... LIMIT (size+1)   |
|  | Page size: 20                   |  Fetches 21 rows, returns 20 |
|  | Has next: true                 |  Checks if 21st exists       |
|  | Has previous: false            |                              |
|  | (NO total count!)              |  Use when: infinite scroll   |
|  +---------------------------------+  or "Load More" button       |
|                                                                   |
|  List<T>                                                          |
|  +---------------------------------+                              |
|  | Just the data, no metadata      |  Executes ONE query:         |
|  | [item1, item2, ..., item20]     |  SELECT ... LIMIT/OFFSET     |
|  |                                 |                              |
|  | (NO count, NO page info)        |  Use when: you only need     |
|  +---------------------------------+  the data subset             |
|                                                                   |
+------------------------------------------------------------------+
```

### Using Page

```java
// Repository
Page<Employee> findByActive(boolean active, Pageable pageable);

// Service
Pageable pageable = PageRequest.of(0, 20, Sort.by("name"));
Page<Employee> page = repository.findByActive(true, pageable);

// Page metadata
page.getContent();           // List<Employee> - the 20 employees
page.getNumber();            // 0 - current page number
page.getSize();              // 20 - page size
page.getTotalElements();     // 1542 - total matching rows
page.getTotalPages();        // 78 - total pages (1542 / 20, rounded up)
page.hasNext();              // true - there are more pages
page.hasPrevious();          // false - this is the first page
page.isFirst();              // true
page.isLast();               // false
page.getNumberOfElements();  // 20 - elements on THIS page
```

### Using Slice

```java
// Repository
Slice<Employee> findByActive(boolean active, Pageable pageable);

// Service
Slice<Employee> slice = repository.findByActive(true, PageRequest.of(0, 20));

// Slice metadata (NO totalElements or totalPages)
slice.getContent();           // List<Employee>
slice.getNumber();            // 0
slice.getSize();              // 20
slice.hasNext();              // true (knows because it fetched 21 rows)
slice.hasPrevious();          // false
// slice.getTotalElements()   // DOES NOT EXIST on Slice!
// slice.getTotalPages()      // DOES NOT EXIST on Slice!
```

### When to Use Which

```
Decision Guide:
+------------------------------------------------------------------+
|                                                                   |
|  Need total count for "Page X of Y" display?                     |
|      |                                                            |
|   YES --> Use Page<T>                                             |
|      |    (extra COUNT query is acceptable)                       |
|      |                                                            |
|    NO                                                             |
|      |                                                            |
|      v                                                            |
|  Need "Load More" / "Next" button?                               |
|      |                                                            |
|   YES --> Use Slice<T>                                            |
|      |    (avoids COUNT query, knows if more data exists)         |
|      |                                                            |
|    NO                                                             |
|      |                                                            |
|      v                                                            |
|  Just need the data?                                              |
|      |                                                            |
|   YES --> Use List<T> with Pageable                               |
|           (simplest, no metadata overhead)                        |
+------------------------------------------------------------------+
|                                                                   |
|  Performance Impact:                                              |
|  Table with 1M rows, active = true matches 500K:                 |
|                                                                   |
|  Page<T>:  SELECT ... LIMIT 20    (~1ms)                          |
|          + SELECT COUNT(*) WHERE active = true  (~200ms)          |
|          = ~201ms total                                           |
|                                                                   |
|  Slice<T>: SELECT ... LIMIT 21    (~1ms)                          |
|          = ~1ms total                                             |
|                                                                   |
|  The COUNT query can be expensive on large tables!                |
+------------------------------------------------------------------+
```

---

## Pagination with Different Query Types

### Derived Methods

```java
// Page return
Page<Employee> findByActive(boolean active, Pageable pageable);

// Slice return
Slice<Employee> findByDepartmentName(String deptName, Pageable pageable);

// List return (still paginated — uses LIMIT/OFFSET — but no metadata)
List<Employee> findBySalaryGreaterThan(BigDecimal salary, Pageable pageable);

// With Sort only (no pagination)
List<Employee> findByActive(boolean active, Sort sort);
```

### JPQL with Pagination

```java
// JPQL with Page return — count query derived automatically
@Query("SELECT e FROM Employee e WHERE e.active = true")
Page<Employee> findActiveEmployees(Pageable pageable);

// JPQL with explicit count query (for complex queries)
@Query(value = "SELECT e FROM Employee e JOIN e.department d WHERE d.name = :dept",
       countQuery = "SELECT COUNT(e) FROM Employee e JOIN e.department d WHERE d.name = :dept")
Page<Employee> findByDept(@Param("dept") String dept, Pageable pageable);

// Slice (no count needed)
@Query("SELECT e FROM Employee e WHERE e.salary > :min")
Slice<Employee> findHighEarners(@Param("min") BigDecimal min, Pageable pageable);
```

### Native SQL with Pagination

```java
// Native SQL — MUST provide countQuery for Page return
@Query(value = "SELECT * FROM employees WHERE active = true",
       countQuery = "SELECT COUNT(*) FROM employees WHERE active = true",
       nativeQuery = true)
Page<Employee> findActiveNative(Pageable pageable);

// Slice return — no countQuery needed
@Query(value = "SELECT * FROM employees WHERE salary > :min",
       nativeQuery = true)
Slice<Employee> findHighEarnersNative(@Param("min") BigDecimal min, Pageable pageable);
```

### Specifications with Pagination

```java
// Already built in to JpaSpecificationExecutor
Page<Employee> findAll(Specification<Employee> spec, Pageable pageable);

// Usage
Specification<Employee> spec = EmployeeSpecifications.isActive()
    .and(EmployeeSpecifications.salaryGreaterThan(new BigDecimal("50000")));

Page<Employee> page = repository.findAll(spec,
    PageRequest.of(0, 20, Sort.by("salary").descending()));
```

---

## Custom Count Queries

For complex queries with joins or subqueries, the auto-derived count query might be incorrect or slow. You can provide your own:

```java
// Problem: Auto-derived count with FETCH JOIN fails
@Query("SELECT e FROM Employee e JOIN FETCH e.department WHERE e.active = true")
Page<Employee> findActiveWithDept(Pageable pageable);
// ERROR! Hibernate cannot derive a COUNT query from a FETCH JOIN

// Solution: Provide explicit countQuery
@Query(value = "SELECT e FROM Employee e JOIN FETCH e.department WHERE e.active = true",
       countQuery = "SELECT COUNT(e) FROM Employee e WHERE e.active = true")
Page<Employee> findActiveWithDept(Pageable pageable);
```

```
Why Custom Count Queries Are Needed:
+------------------------------------------------------------------+
|                                                                   |
|  Auto-derived count:                                              |
|  Query:  SELECT e FROM Employee e                                 |
|          JOIN FETCH e.department                                   |
|          WHERE e.active = true                                    |
|                                                                   |
|  Hibernate tries: SELECT COUNT(e) FROM Employee e                 |
|                   JOIN FETCH e.department    <-- ERROR!            |
|                   WHERE e.active = true                           |
|                                                                   |
|  FETCH JOIN does not make sense in a COUNT query.                 |
|  Hibernate cannot strip it automatically for native queries.      |
|                                                                   |
|  Custom count:                                                    |
|  countQuery = "SELECT COUNT(e) FROM Employee e                    |
|                WHERE e.active = true"                             |
|  - Simple, fast, no join needed for counting                      |
+------------------------------------------------------------------+
```

---

## @EntityGraph — Query-Level Fetch Control

`@EntityGraph` (JPA 2.1 standard) lets you control which relationships are eagerly loaded **per query**, without changing the entity's default fetch type.

```
Fetching Without @EntityGraph (N+1 Problem):
+------------------------------------------------------------------+
|                                                                   |
|  Query: findAll()                                                 |
|                                                                   |
|  SQL 1:  SELECT * FROM employees                  (1 query)       |
|  Result: 100 employees                                            |
|                                                                   |
|  For EACH employee, accessing employee.getDepartment():           |
|  SQL 2:  SELECT * FROM departments WHERE id = 1   (query 2)      |
|  SQL 3:  SELECT * FROM departments WHERE id = 2   (query 3)      |
|  SQL 4:  SELECT * FROM departments WHERE id = 1   (query 4)      |
|  ...                                                              |
|  SQL 101: SELECT * FROM departments WHERE id = 5  (query 101)    |
|                                                                   |
|  Total: 1 + 100 = 101 queries!  (the N+1 problem)                |
+------------------------------------------------------------------+

Fetching With @EntityGraph:
+------------------------------------------------------------------+
|                                                                   |
|  Query: findAll() with @EntityGraph({"department"})               |
|                                                                   |
|  SQL 1:  SELECT e.*, d.*                                          |
|          FROM employees e                                         |
|          LEFT JOIN departments d ON e.department_id = d.id         |
|                                                        (1 query)  |
|  Result: 100 employees with departments already loaded            |
|                                                                   |
|  Total: 1 query! Everything loaded in a single JOIN.              |
+------------------------------------------------------------------+
```

### Using @EntityGraph on Repository Methods

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // Load department eagerly for this specific query
    @EntityGraph(attributePaths = {"department"})
    List<Employee> findByActive(boolean active);

    // Load multiple relationships
    @EntityGraph(attributePaths = {"department", "projects"})
    List<Employee> findAll();

    // Combine with JPQL
    @EntityGraph(attributePaths = {"department"})
    @Query("SELECT e FROM Employee e WHERE e.salary > :min")
    List<Employee> findHighEarnersWithDept(@Param("min") BigDecimal min);

    // Combine with pagination
    @EntityGraph(attributePaths = {"department"})
    Page<Employee> findByActive(boolean active, Pageable pageable);

    // Nested paths (department's company)
    @EntityGraph(attributePaths = {"department", "department.company"})
    List<Employee> findAll(Sort sort);
}
```

### @NamedEntityGraph (on the Entity)

For reusable fetch plans, define the graph on the entity class:

```java
@Entity
@Table(name = "employees")
@NamedEntityGraph(
    name = "Employee.withDepartment",
    attributeNodes = @NamedAttributeNode("department")
)
@NamedEntityGraph(
    name = "Employee.withDepartmentAndProjects",
    attributeNodes = {
        @NamedAttributeNode("department"),
        @NamedAttributeNode("projects")
    }
)
@NamedEntityGraph(
    name = "Employee.full",
    attributeNodes = {
        @NamedAttributeNode(value = "department",
            subgraph = "department-with-company"),
        @NamedAttributeNode("projects")
    },
    subgraphs = @NamedSubgraph(
        name = "department-with-company",
        attributeNodes = @NamedAttributeNode("company")
    )
)
public class Employee {
    // ...
}
```

```java
// Reference by name in repository
@EntityGraph("Employee.withDepartment")
List<Employee> findByActive(boolean active);

@EntityGraph("Employee.full")
Optional<Employee> findById(Long id);
```

```
@EntityGraph Types:
+------------------------------------------------------------------+
|                                                                   |
|  FETCH graph (default):                                           |
|  - Attributes in the graph: loaded EAGERLY                       |
|  - Attributes NOT in the graph: loaded LAZILY                    |
|  - Overrides the entity's default fetch type                     |
|                                                                   |
|  LOAD graph:                                                      |
|  - Attributes in the graph: loaded EAGERLY                       |
|  - Attributes NOT in the graph: use entity's DEFAULT fetch type  |
|                                                                   |
|  @EntityGraph(                                                    |
|    attributePaths = {"department"},                                |
|    type = EntityGraph.EntityGraphType.FETCH  // or LOAD           |
|  )                                                                |
|                                                                   |
|  Most of the time, FETCH (default) is what you want.             |
+------------------------------------------------------------------+
```

---

## @QueryHints for Optimization

JPA `@QueryHints` let you pass hints to the persistence provider for optimization:

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // Read-only hint — Hibernate skips dirty checking for these entities
    @QueryHints(@QueryHint(name = "org.hibernate.readOnly", value = "true"))
    @Query("SELECT e FROM Employee e WHERE e.active = true")
    List<Employee> findActiveReadOnly();

    // Comment hint — adds a SQL comment for debugging in query logs
    @QueryHints(@QueryHint(name = "org.hibernate.comment",
                           value = "Employee active list"))
    List<Employee> findByActive(boolean active);

    // Fetch size hint — controls JDBC fetch size for large result sets
    @QueryHints(@QueryHint(name = "org.hibernate.fetchSize", value = "50"))
    @Query("SELECT e FROM Employee e")
    List<Employee> findAllWithFetchSize();

    // Timeout hint — query timeout in seconds
    @QueryHints(@QueryHint(name = "jakarta.persistence.query.timeout",
                           value = "5000"))
    @Query("SELECT e FROM Employee e WHERE e.active = true")
    List<Employee> findActiveWithTimeout();
}
```

```
Common @QueryHints:
+------------------------------------------------------------------+
|  Hint                                     Effect                  |
|------------------------------------------------------------------|
|  org.hibernate.readOnly = "true"          Skip dirty checking     |
|                                           (faster for read-only   |
|                                           data, saves memory)     |
|                                                                   |
|  org.hibernate.fetchSize = "50"           JDBC rows fetched per   |
|                                           database round-trip     |
|                                                                   |
|  org.hibernate.comment = "..."            SQL comment for logging |
|                                                                   |
|  org.hibernate.cacheable = "true"         Use query cache         |
|                                                                   |
|  jakarta.persistence.query.timeout        Query timeout (ms)      |
|  = "5000"                                                         |
+------------------------------------------------------------------+
```

---

## Pagination in REST Controllers

A complete example of exposing paginated data through a REST API:

```java
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    private final EmployeeRepository repository;

    public EmployeeController(EmployeeRepository repository) {
        this.repository = repository;
    }

    // Spring Boot auto-resolves Pageable from query parameters:
    // GET /api/employees?page=0&size=20&sort=name,asc&sort=salary,desc
    @GetMapping
    public Page<Employee> getAll(Pageable pageable) {
        return repository.findAll(pageable);
    }

    // With default values
    @GetMapping("/active")
    public Page<Employee> getActive(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "name") String sortBy,
            @RequestParam(defaultValue = "asc") String direction) {

        Sort sort = direction.equalsIgnoreCase("desc")
            ? Sort.by(sortBy).descending()
            : Sort.by(sortBy).ascending();

        return repository.findByActive(true,
            PageRequest.of(page, size, sort));
    }
}
```

```
REST Pagination Request/Response:
+------------------------------------------------------------------+
|                                                                   |
|  Request:                                                         |
|  GET /api/employees?page=0&size=3&sort=salary,desc               |
|                                                                   |
|  Response:                                                        |
|  {                                                                |
|    "content": [                                                   |
|      {"id": 5, "name": "Alice", "salary": 120000},               |
|      {"id": 12, "name": "Bob", "salary": 110000},                |
|      {"id": 3, "name": "Charlie", "salary": 95000}               |
|    ],                                                             |
|    "pageable": {                                                  |
|      "pageNumber": 0,                                             |
|      "pageSize": 3,                                               |
|      "sort": { "sorted": true, "orders": [...] }                 |
|    },                                                             |
|    "totalElements": 150,                                          |
|    "totalPages": 50,                                              |
|    "first": true,                                                 |
|    "last": false,                                                 |
|    "numberOfElements": 3                                          |
|  }                                                                |
|                                                                   |
+------------------------------------------------------------------+
```

### Limiting Page Size

Always limit the maximum page size to prevent abuse:

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        PageableHandlerMethodArgumentResolver resolver =
            new PageableHandlerMethodArgumentResolver();
        resolver.setMaxPageSize(100);         // Max 100 items per page
        resolver.setFallbackPageable(
            PageRequest.of(0, 20));           // Default: page 0, size 20
        resolvers.add(resolver);
    }
}
```

---

## Transforming Page Content

Often you need to convert entity pages to DTO pages:

```java
// Entity to DTO conversion using Page.map()
public Page<EmployeeDto> getEmployees(Pageable pageable) {
    Page<Employee> entityPage = repository.findByActive(true, pageable);

    // map() preserves all pagination metadata
    return entityPage.map(employee -> new EmployeeDto(
        employee.getId(),
        employee.getName(),
        employee.getEmail(),
        employee.getDepartment().getName()
    ));
}
```

```
Page.map() Transformation:
+------------------------------------------------------------------+
|                                                                   |
|  Page<Employee>                      Page<EmployeeDto>            |
|  +-------------------+              +--------------------+        |
|  | Employee(id=1,    |    map()     | EmployeeDto(id=1,  |        |
|  |   name="Alice",   | ----------> |   name="Alice",    |        |
|  |   email="a@co",   |             |   email="a@co",    |        |
|  |   dept=Dept(...))  |             |   deptName="Eng")  |        |
|  +-------------------+              +--------------------+        |
|  | totalElements: 150|    same      | totalElements: 150 |        |
|  | totalPages: 8     | ----------> | totalPages: 8      |        |
|  | number: 0         |  metadata   | number: 0          |        |
|  +-------------------+  preserved  +--------------------+        |
+------------------------------------------------------------------+
```

---

## Keyset Pagination (Scroll API)

For very large datasets, offset-based pagination becomes slow because the database must skip over all previous rows. **Keyset pagination** (also called cursor-based pagination) is more efficient:

```
Offset vs Keyset Pagination Performance:
+------------------------------------------------------------------+
|                                                                   |
|  Offset pagination (page 1000, size 20):                          |
|  SELECT * FROM employees ORDER BY id LIMIT 20 OFFSET 20000       |
|  --> Database reads 20,020 rows, discards 20,000, returns 20      |
|  --> Gets SLOWER as page number increases                         |
|                                                                   |
|  Keyset pagination (after id = 20000):                            |
|  SELECT * FROM employees WHERE id > 20000 ORDER BY id LIMIT 20   |
|  --> Database uses index to jump directly, reads only 20 rows     |
|  --> SAME speed regardless of position                            |
|                                                                   |
|  Performance:                                                     |
|  Page 1:    Offset ~1ms     Keyset ~1ms      (same)              |
|  Page 100:  Offset ~10ms    Keyset ~1ms                           |
|  Page 1000: Offset ~100ms   Keyset ~1ms      (big difference!)   |
|  Page 10K:  Offset ~1000ms  Keyset ~1ms      (10x faster)        |
+------------------------------------------------------------------+
```

Spring Data JPA 3.1+ supports keyset pagination through the `ScrollPosition` and `Window` API:

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    Window<Employee> findByActiveTrue(OffsetScrollPosition position, Limit limit, Sort sort);
}

// Usage
Window<Employee> firstPage = repository.findByActiveTrue(
    ScrollPosition.offset(),        // start from beginning
    Limit.of(20),                   // 20 items
    Sort.by("salary").descending()  // sort order
);

// Get next page using the last item's position
if (firstPage.hasNext()) {
    Window<Employee> secondPage = repository.findByActiveTrue(
        firstPage.positionAt(firstPage.size() - 1),
        Limit.of(20),
        Sort.by("salary").descending()
    );
}
```

---

## Common Mistakes

1. **Forgetting that pages are 0-based**: Page 0 is the first page. Passing page=1 returns the second page of results. If your frontend uses 1-based pagination, subtract 1 before creating `PageRequest`.

2. **Using Page when Slice is sufficient**: If your UI shows "Load More" instead of "Page 1 of 50", use `Slice<T>`. The COUNT query for `Page<T>` can be expensive on large tables.

3. **Not providing countQuery for complex JPQL or native queries**: Queries with FETCH JOIN, UNION, or subqueries cannot have their count query auto-derived. Provide an explicit `countQuery`.

4. **Sorting by non-indexed columns**: Pagination with `ORDER BY` on a column without a database index forces a full table sort. Add indexes on frequently sorted columns.

5. **Using offset pagination on huge datasets**: Offset-based pagination (LIMIT/OFFSET) gets slower as the offset grows because the database must scan and discard earlier rows. For datasets with millions of rows, consider keyset pagination.

6. **Not limiting max page size**: Without a max page size limit, a client can request `?size=1000000` and pull your entire database into memory. Always configure a maximum.

7. **Ignoring @EntityGraph with pagination**: Paginating a query that triggers N+1 lazy loading means each page of 20 items generates 21 queries (1 + 20). Add `@EntityGraph` to eagerly load the needed relationships in one query.

---

## Best Practices

1. **Always paginate list endpoints**: Never return unbounded lists from an API. Default to `PageRequest.of(0, 20)` and let clients override with query parameters.

2. **Choose Page vs Slice based on UI needs**: Use `Page<T>` for traditional pagination controls ("Page 3 of 47"). Use `Slice<T>` for infinite scroll or "Load More" patterns. Use `List<T>` when you do not need pagination metadata.

3. **Add @EntityGraph to paginated queries**: Prevent N+1 by eagerly loading relationships used in the response, especially when converting entities to DTOs.

4. **Set a maximum page size**: Configure `PageableHandlerMethodArgumentResolver` with `setMaxPageSize(100)` to prevent abuse.

5. **Use Page.map() for DTO conversion**: The `map()` method preserves all pagination metadata, making it perfect for entity-to-DTO conversion.

6. **Index your sort columns**: If users can sort by salary, department name, or hire date, ensure those columns have database indexes.

7. **Use Pageable directly in controller parameters**: Spring Boot auto-resolves `Pageable` from query parameters (`?page=0&size=20&sort=name,asc`), eliminating manual parsing.

---

## Summary

In this chapter, you learned how to efficiently retrieve subsets of data:

- **Pageable** and **PageRequest** define what page to retrieve, how many items per page, and the sort order. Pages are 0-indexed.

- **Page<T>** returns data plus full pagination metadata (total count, total pages) but requires an extra COUNT query. **Slice<T>** skips the count and just knows if more data exists. **List<T>** returns only the data.

- **Sort** provides a fluent API for single-field, multi-field, and directional sorting with null handling.

- **Pagination works with all query types**: derived methods, JPQL, native SQL, and Specifications.

- **@EntityGraph** controls eager fetching per query, solving the N+1 problem without changing entity defaults. Use `attributePaths` for inline definition or `@NamedEntityGraph` for reusable fetch plans.

- **@QueryHints** pass optimization hints like read-only mode, fetch size, and query timeout.

- **Page.map()** transforms entity pages to DTO pages while preserving all pagination metadata.

- **Keyset pagination** outperforms offset pagination on large datasets by using indexed lookups instead of OFFSET.

---

## Interview Questions

**Q1: What is the difference between Page and Slice in Spring Data JPA?**

`Page<T>` executes an additional COUNT query to know the total number of elements and total pages. It provides full navigation metadata. `Slice<T>` fetches one extra row (size+1) to determine if a next page exists, but does not count the total. Use Page for traditional "Page X of Y" UIs; use Slice for infinite scroll or "Load More" patterns where total count is unnecessary.

**Q2: How does Spring Boot resolve Pageable from HTTP request parameters?**

Spring Boot's `PageableHandlerMethodArgumentResolver` reads `page`, `size`, and `sort` query parameters and creates a `Pageable` instance. For example, `?page=0&size=20&sort=name,asc&sort=salary,desc` creates `PageRequest.of(0, 20, Sort.by("name").ascending().and(Sort.by("salary").descending()))`.

**Q3: What is the N+1 problem and how does @EntityGraph solve it?**

The N+1 problem occurs when loading N entities triggers N additional queries to load their lazy relationships (1 query for the list + N queries for each related entity). `@EntityGraph` specifies which relationships should be eagerly loaded in a single JOIN query, reducing N+1 queries to 1 query.

**Q4: When would you provide a custom countQuery?**

When the auto-derived count query fails or is inefficient. Common cases: queries with FETCH JOIN (count cannot include FETCH), native SQL queries (count cannot be auto-derived), complex queries with subqueries or UNIONs, and when the count can be simplified for performance.

**Q5: What is keyset pagination and when should you use it?**

Keyset pagination (cursor-based) uses the last seen value as a filter (`WHERE id > lastId`) instead of OFFSET. It maintains constant performance regardless of position because the database uses an index to jump directly to the right spot. Use it when paginating millions of rows where offset-based pagination becomes too slow at high page numbers.

**Q6: How do you convert a Page of entities to a Page of DTOs?**

Use `Page.map()`. This method transforms each element using a mapping function while preserving all pagination metadata (total elements, total pages, page number, sort). Example: `entityPage.map(e -> new EmployeeDto(e.getId(), e.getName()))`.

---

## Practice Exercises

**Exercise 1: Basic Pagination**
Create a `ProductRepository` with a `Page<Product> findByCategory(String category, Pageable pageable)` method. Write a test that loads page 0 with 5 items, then page 1, and verifies the content and metadata.

**Exercise 2: Slice vs Page**
Implement the same query returning `Slice<Product>` and `Page<Product>`. Enable SQL logging and compare the number of queries executed. Verify that Slice does not have totalElements.

**Exercise 3: Multi-Field Sorting**
Create an endpoint `GET /api/products` that supports sorting by `category` (ascending) and then `price` (descending). Test with sample data and verify the order.

**Exercise 4: EntityGraph**
Create a `Product` entity with a lazy `@ManyToOne` relationship to `Category`. Write a query that returns 20 products with pagination. First observe the N+1 problem in SQL logs, then add `@EntityGraph(attributePaths = {"category"})` and verify it is reduced to 1 query.

**Exercise 5: Paginated Search API**
Build a `GET /api/employees/search` endpoint that accepts optional filters (name, department, minSalary, maxSalary) and pagination parameters. Use Specifications from Chapter 10 combined with `Pageable`. Return `Page<EmployeeDto>` using `Page.map()`.

---

## What Is Next?

In the next chapter, we begin **Part III: Relationships and Mapping**. We will start with **One-to-One Relationships** — how to map them with `@OneToOne`, choose between unidirectional and bidirectional, share primary keys with `@MapsId`, and handle lazy loading and cascading for one-to-one associations.
