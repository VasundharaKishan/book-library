# Chapter 23: DTOs, Projections, and Data Transfer

---

## Learning Goals

By the end of this chapter, you will be able to:

- Explain why exposing JPA entities directly in APIs is problematic
- Create DTO classes for API request and response data
- Map between entities and DTOs manually and with MapStruct
- Use JPA interface-based projections for efficient read queries
- Use class-based projections with constructor expressions in JPQL
- Apply dynamic projections for flexible query return types
- Choose between DTOs, projections, and entities for different use cases
- Structure DTOs for create, update, and response scenarios

---

## Why Not Expose Entities Directly?

It is tempting to return JPA entities directly from controllers. It works, but causes serious problems in production:

```
Problems with Exposing Entities:
+------------------------------------------------------------------+
|                                                                   |
|  1. SECURITY — Leaking sensitive data                             |
|     @Entity User has: password, salt, loginAttempts,              |
|     internalNotes, isAdmin                                        |
|     Returning User in a GET /api/users endpoint                   |
|     exposes ALL fields in the JSON response!                      |
|                                                                   |
|  2. COUPLING — API tied to database schema                        |
|     If you rename a column or add a field, the API changes.       |
|     Frontend breaks. Mobile app breaks. Partner APIs break.       |
|                                                                   |
|  3. PERFORMANCE — Over-fetching                                   |
|     A list endpoint returns ALL entity fields + triggers          |
|     lazy loading of relationships during JSON serialization.      |
|     You send 20 fields when the client needs 3.                  |
|                                                                   |
|  4. CIRCULAR REFERENCES — Infinite JSON                           |
|     Department has List<Employee>, Employee has Department.       |
|     Jackson serializes Department -> employees -> department ->   |
|     employees -> ... StackOverflowError!                          |
|                                                                   |
|  5. LAZY LOADING — LazyInitializationException                    |
|     Entity returned from @Transactional method is detached.       |
|     JSON serializer accesses lazy field -> Exception!             |
|     (Unless OSIV is on, which has its own problems)               |
+------------------------------------------------------------------+
```

```
Entity vs DTO:
+------------------------------------------------------------------+
|                                                                   |
|  Entity (internal):           DTO (external):                     |
|  @Entity                      public class UserResponse {        |
|  public class User {              Long id;                        |
|      Long id;                     String name;                    |
|      String name;                 String email;                   |
|      String email;                String role;                    |
|      String passwordHash;    }                                    |
|      String salt;                                                 |
|      int loginAttempts;       Only exposes what the               |
|      String internalNotes;    client needs to see.                |
|      boolean isAdmin;         No sensitive data.                  |
|      Department department;   No circular references.             |
|      List<Role> roles;        No lazy loading issues.             |
|  }                                                                |
|                                                                   |
+------------------------------------------------------------------+
```

---

## DTO Pattern

A **Data Transfer Object (DTO)** is a simple class that carries data between layers. It has no business logic, no persistence annotations, and no database awareness.

### Response DTOs

```java
// What the API returns to clients
public class EmployeeResponse {
    private Long id;
    private String name;
    private String email;
    private BigDecimal salary;
    private String departmentName;  // Flattened from department.name
    private LocalDate hireDate;

    public EmployeeResponse() {}

    public EmployeeResponse(Long id, String name, String email,
                            BigDecimal salary, String departmentName,
                            LocalDate hireDate) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.salary = salary;
        this.departmentName = departmentName;
        this.hireDate = hireDate;
    }

    // Getters and setters...
}
```

### Request DTOs

```java
// What the client sends for creating
public class CreateEmployeeRequest {

    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100)
    private String name;

    @NotBlank @Email
    private String email;

    @NotNull @Positive
    private BigDecimal salary;

    @NotNull
    private Long departmentId;   // Client sends ID, not the entity

    // Getters and setters...
}

// What the client sends for updating (some fields optional)
public class UpdateEmployeeRequest {

    @Size(min = 2, max = 100)
    private String name;          // Optional — only update if provided

    @Email
    private String email;

    @Positive
    private BigDecimal salary;

    // Getters and setters...
}
```

```
DTO Flow Through Layers:
+------------------------------------------------------------------+
|                                                                   |
|  Client          Controller         Service          Repository   |
|    |                 |                  |                 |        |
|    | JSON request    |                  |                 |        |
|    |--------------->|                  |                 |        |
|    |                 | CreateEmployee   |                 |        |
|    |                 | Request (DTO)    |                 |        |
|    |                 |---------------->|                 |        |
|    |                 |                  | Convert DTO     |        |
|    |                 |                  | to Entity       |        |
|    |                 |                  |---------------->|        |
|    |                 |                  |    save(entity)  |        |
|    |                 |                  |<----------------|        |
|    |                 |                  | Convert Entity   |        |
|    |                 |  EmployeeResponse| to DTO          |        |
|    |                 |<----------------|                 |        |
|    | JSON response   |                  |                 |        |
|    |<---------------|                  |                 |        |
|                                                                   |
|  DTOs cross layer boundaries. Entities stay in the service layer. |
+------------------------------------------------------------------+
```

---

## Manual Mapping

The simplest approach — write mapping methods by hand:

```java
@Service
@Transactional
public class EmployeeService {

    private final EmployeeRepository employeeRepository;
    private final DepartmentRepository departmentRepository;

    // === Create ===
    public EmployeeResponse create(CreateEmployeeRequest request) {
        Department department = departmentRepository
            .findById(request.getDepartmentId())
            .orElseThrow(() -> new RuntimeException("Department not found"));

        Employee employee = new Employee();
        employee.setName(request.getName());
        employee.setEmail(request.getEmail());
        employee.setSalary(request.getSalary());
        employee.setDepartment(department);
        employee.setHireDate(LocalDate.now());

        Employee saved = employeeRepository.save(employee);
        return toResponse(saved);
    }

    // === Read ===
    @Transactional(readOnly = true)
    public EmployeeResponse getById(Long id) {
        Employee employee = employeeRepository.findWithDeptById(id)
            .orElseThrow(() -> new RuntimeException("Employee not found"));
        return toResponse(employee);
    }

    // === List ===
    @Transactional(readOnly = true)
    public Page<EmployeeResponse> getAll(Pageable pageable) {
        return employeeRepository.findAll(pageable)
            .map(this::toResponse);
    }

    // === Update ===
    public EmployeeResponse update(Long id, UpdateEmployeeRequest request) {
        Employee employee = employeeRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Employee not found"));

        if (request.getName() != null) employee.setName(request.getName());
        if (request.getEmail() != null) employee.setEmail(request.getEmail());
        if (request.getSalary() != null) employee.setSalary(request.getSalary());

        return toResponse(employee);
    }

    // === Mapping Method ===
    private EmployeeResponse toResponse(Employee e) {
        return new EmployeeResponse(
            e.getId(),
            e.getName(),
            e.getEmail(),
            e.getSalary(),
            e.getDepartment() != null ? e.getDepartment().getName() : null,
            e.getHireDate()
        );
    }
}
```

```
Manual Mapping Trade-offs:
+------------------------------------------------------------------+
|                                                                   |
|  Pros:                                                            |
|  + No extra dependencies                                         |
|  + Full control over mapping logic                                |
|  + Easy to debug (just step through the method)                   |
|  + Works with any project                                         |
|                                                                   |
|  Cons:                                                            |
|  - Tedious for entities with many fields                          |
|  - Easy to forget a field when entity changes                    |
|  - Repetitive code across services                                |
|  - No compile-time detection of missing mappings                  |
+------------------------------------------------------------------+
```

---

## MapStruct — Automated Mapping

MapStruct generates mapping code at compile time. You define an interface, and MapStruct creates the implementation:

### Setup

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.mapstruct</groupId>
    <artifactId>mapstruct</artifactId>
    <version>1.5.5.Final</version>
</dependency>

<!-- Annotation processor -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <annotationProcessorPaths>
            <path>
                <groupId>org.mapstruct</groupId>
                <artifactId>mapstruct-processor</artifactId>
                <version>1.5.5.Final</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

### Mapper Interface

```java
@Mapper(componentModel = "spring")   // Generates a Spring @Component bean
public interface EmployeeMapper {

    // Auto-maps matching field names (id, name, email, salary, hireDate)
    @Mapping(source = "department.name", target = "departmentName")
    EmployeeResponse toResponse(Employee employee);

    // Map a list
    List<EmployeeResponse> toResponseList(List<Employee> employees);

    // Create entity from request (ignore id and department — set separately)
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "department", ignore = true)
    @Mapping(target = "hireDate", ignore = true)
    Employee toEntity(CreateEmployeeRequest request);

    // Update existing entity from request (null values are skipped)
    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "department", ignore = true)
    void updateEntity(UpdateEmployeeRequest request, @MappingTarget Employee employee);
}
```

```java
// Usage in service
@Service
public class EmployeeService {

    private final EmployeeRepository employeeRepository;
    private final DepartmentRepository departmentRepository;
    private final EmployeeMapper mapper;   // Inject the mapper

    public EmployeeResponse create(CreateEmployeeRequest request) {
        Employee employee = mapper.toEntity(request);
        employee.setHireDate(LocalDate.now());

        Department dept = departmentRepository.findById(request.getDepartmentId())
            .orElseThrow();
        employee.setDepartment(dept);

        return mapper.toResponse(employeeRepository.save(employee));
    }

    public EmployeeResponse update(Long id, UpdateEmployeeRequest request) {
        Employee employee = employeeRepository.findById(id).orElseThrow();
        mapper.updateEntity(request, employee);  // Updates non-null fields
        return mapper.toResponse(employee);
    }
}
```

```
MapStruct at Compile Time:
+------------------------------------------------------------------+
|                                                                   |
|  You write:                                                       |
|  @Mapper interface EmployeeMapper {                               |
|      EmployeeResponse toResponse(Employee employee);              |
|  }                                                                |
|                                                                   |
|  MapStruct generates (at compile time):                           |
|  @Component                                                       |
|  public class EmployeeMapperImpl implements EmployeeMapper {      |
|      @Override                                                    |
|      public EmployeeResponse toResponse(Employee employee) {     |
|          if (employee == null) return null;                        |
|          EmployeeResponse dto = new EmployeeResponse();           |
|          dto.setId(employee.getId());                              |
|          dto.setName(employee.getName());                          |
|          dto.setEmail(employee.getEmail());                        |
|          dto.setSalary(employee.getSalary());                      |
|          dto.setHireDate(employee.getHireDate());                  |
|          if (employee.getDepartment() != null) {                  |
|              dto.setDepartmentName(                                |
|                  employee.getDepartment().getName());              |
|          }                                                        |
|          return dto;                                               |
|      }                                                            |
|  }                                                                |
|                                                                   |
|  No reflection. No runtime overhead. Just plain method calls.    |
+------------------------------------------------------------------+
```

---

## JPA Interface-Based Projections

Instead of loading a full entity and mapping to a DTO, you can ask JPA to load only the fields you need:

```java
// Projection interface — only the fields needed for the list view
public interface EmployeeListProjection {
    Long getId();
    String getName();
    String getEmail();

    @Value("#{target.department.name}")  // SpEL for nested fields
    String getDepartmentName();
}
```

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // Returns projections — Hibernate loads ONLY the needed columns
    List<EmployeeListProjection> findByActive(boolean active);

    // Projections with pagination
    Page<EmployeeListProjection> findByDepartmentName(String dept, Pageable pageable);

    // Projections with JPQL
    @Query("SELECT e FROM Employee e WHERE e.salary > :min")
    List<EmployeeListProjection> findHighEarnerProjections(@Param("min") BigDecimal min);
}
```

```
Entity vs Projection SQL:
+------------------------------------------------------------------+
|                                                                   |
|  Entity query: List<Employee> findByActive(boolean active)        |
|  SQL: SELECT id, name, email, salary, hire_date, bio,             |
|       department_id, active, created_at, updated_at               |
|       FROM employees WHERE active = true                          |
|  --> Loads ALL 10 columns                                         |
|                                                                   |
|  Projection: List<EmployeeListProjection> findByActive(boolean)   |
|  SQL: SELECT id, name, email                                      |
|       FROM employees WHERE active = true                          |
|  --> Loads ONLY 3 columns (what the projection needs)             |
|                                                                   |
|  Benefits:                                                        |
|  - Less data transferred from database                            |
|  - No entity managed in persistence context (less memory)         |
|  - No dirty checking overhead                                     |
|  - No lazy loading issues (no entity = no proxies)                |
+------------------------------------------------------------------+
```

---

## Class-Based Projections (JPQL Constructor Expressions)

Use the `new` keyword in JPQL to construct DTOs directly:

```java
// DTO for the projection
public class EmployeeSummary {
    private final String name;
    private final String email;
    private final BigDecimal salary;
    private final String departmentName;

    // Constructor must match the JPQL new() arguments
    public EmployeeSummary(String name, String email,
                           BigDecimal salary, String departmentName) {
        this.name = name;
        this.email = email;
        this.salary = salary;
        this.departmentName = departmentName;
    }

    // Getters...
}
```

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    @Query("SELECT new com.example.dto.EmployeeSummary(" +
           "e.name, e.email, e.salary, d.name) " +
           "FROM Employee e JOIN e.department d " +
           "WHERE e.active = true " +
           "ORDER BY e.salary DESC")
    List<EmployeeSummary> findActiveSummaries();

    // With pagination
    @Query(value = "SELECT new com.example.dto.EmployeeSummary(" +
                   "e.name, e.email, e.salary, d.name) " +
                   "FROM Employee e JOIN e.department d WHERE e.active = true",
           countQuery = "SELECT COUNT(e) FROM Employee e WHERE e.active = true")
    Page<EmployeeSummary> findActiveSummariesPaged(Pageable pageable);
}
```

```
Constructor Expression vs Interface Projection:
+------------------------------------------------------------------+
|                                                                   |
|  Interface Projection:                                            |
|  + No JPQL needed — works with derived methods                    |
|  + Clean, simple                                                  |
|  - Spring creates proxy objects (slight overhead)                 |
|  - Nested properties need @Value SpEL                             |
|                                                                   |
|  Constructor Expression (new ...):                                |
|  + No proxy — creates real DTO objects                            |
|  + Full control over SQL with JPQL                                |
|  + JOINs are explicit (no N+1 risk)                               |
|  - Requires full class path in JPQL string                        |
|  - Constructor must match query column order exactly              |
|                                                                   |
|  Use interface projections for simple queries.                    |
|  Use constructor expressions for complex queries with JOINs.     |
+------------------------------------------------------------------+
```

---

## Dynamic Projections

Return different projections from the same query using generics:

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // Dynamic projection — caller chooses the return type
    <T> List<T> findByActive(boolean active, Class<T> type);

    <T> Optional<T> findById(Long id, Class<T> type);
}
```

```java
// Use different projections for different use cases
// List view — minimal fields
List<EmployeeListProjection> listView =
    repository.findByActive(true, EmployeeListProjection.class);

// Detail view — more fields
List<EmployeeDetailProjection> detailView =
    repository.findByActive(true, EmployeeDetailProjection.class);

// Full entity when needed
List<Employee> entities =
    repository.findByActive(true, Employee.class);
```

---

## Choosing the Right Approach

```
Decision Guide:
+------------------------------------------------------------------+
|                                                                   |
|  Need to CREATE or UPDATE data?                                   |
|      |                                                            |
|   YES --> Use request DTOs + manual/MapStruct mapping to entity   |
|                                                                   |
|  Need to READ data for API response?                              |
|      |                                                            |
|      v                                                            |
|  Simple query, few fields, no JOINs?                              |
|      |                                                            |
|   YES --> Interface projection (cleanest)                         |
|      |                                                            |
|    NO                                                             |
|      |                                                            |
|      v                                                            |
|  Complex query with JOINs and aggregations?                       |
|      |                                                            |
|   YES --> Constructor expression in JPQL (most control)           |
|      |                                                            |
|    NO                                                             |
|      |                                                            |
|      v                                                            |
|  Need to load full entity for business logic, then map?           |
|      |                                                            |
|   YES --> Entity + MapStruct/manual mapping to response DTO      |
|                                                                   |
|  Performance Priority:                                            |
|  1. Constructor expression (pure SQL, no entity overhead)         |
|  2. Interface projection (proxy, minimal columns)                 |
|  3. Entity + DTO mapping (full entity load + conversion)          |
+------------------------------------------------------------------+
```

```
Complete Approach Comparison:
+------------------------------------------------------------------+
|                                                                   |
|  Approach             Performance   Ease    Flexibility           |
|  ----------------------------------------------------------------|
|  Entity directly       Poor         Easy    Low (security issues) |
|  Entity + manual map   Medium       Medium  High                  |
|  Entity + MapStruct    Medium       Easy    High                  |
|  Interface projection  Good         Easy    Medium                |
|  Constructor expr      Best         Medium  High                  |
+------------------------------------------------------------------+
```

---

## DTO Organization

```
Project Structure:
+------------------------------------------------------------------+
|                                                                   |
|  src/main/java/com/example/                                       |
|  +-- entity/                                                      |
|  |   +-- Employee.java                                            |
|  |   +-- Department.java                                          |
|  +-- dto/                                                         |
|  |   +-- employee/                                                |
|  |   |   +-- CreateEmployeeRequest.java                           |
|  |   |   +-- UpdateEmployeeRequest.java                           |
|  |   |   +-- EmployeeResponse.java                                |
|  |   |   +-- EmployeeListProjection.java   (interface)            |
|  |   |   +-- EmployeeSummary.java          (constructor expr)     |
|  |   +-- department/                                              |
|  |       +-- CreateDepartmentRequest.java                         |
|  |       +-- DepartmentResponse.java                              |
|  +-- mapper/                                                      |
|  |   +-- EmployeeMapper.java                                     |
|  |   +-- DepartmentMapper.java                                   |
|  +-- controller/                                                  |
|  +-- service/                                                     |
|  +-- repository/                                                  |
|                                                                   |
|  Convention:                                                      |
|  - Request DTOs: CreateXxxRequest, UpdateXxxRequest               |
|  - Response DTOs: XxxResponse, XxxSummary                         |
|  - Projections: XxxListProjection, XxxDetailProjection            |
|  - Mappers: XxxMapper (one per entity)                            |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Returning entities from controllers**: Exposes sensitive fields, causes circular references, triggers lazy loading errors. Always return DTOs.

2. **Creating one DTO for everything**: Different endpoints need different fields. Use separate DTOs for create, update, list, and detail views.

3. **Mapping inside controllers**: Keep mapping in the service layer. Controllers should receive and return DTOs. Services handle entity-DTO conversion.

4. **Accessing lazy fields during DTO mapping**: If mapping happens outside `@Transactional`, lazy fields trigger `LazyInitializationException`. Map inside the transaction or use `@EntityGraph`.

5. **Using constructor expressions with `SELECT *`**: Constructor expressions must list specific fields, not use wildcard. `SELECT new Dto(e)` does not work — use `SELECT new Dto(e.name, e.email)`.

6. **Ignoring partial updates**: Using `@NotNull` on all update DTO fields forces clients to send everything. Allow null fields and only update non-null values.

---

## Best Practices

1. **Never expose entities in API responses**: Always convert to response DTOs. This is a non-negotiable best practice for production applications.

2. **Use separate DTOs for create, update, and response**: Each operation has different required/optional fields and validation rules.

3. **Use projections for read-heavy endpoints**: Interface projections and constructor expressions are more efficient than loading full entities and mapping.

4. **Use MapStruct for complex mappings**: When entities have many fields, MapStruct eliminates boilerplate and catches missing mappings at compile time.

5. **Keep DTOs simple**: DTOs should be plain data holders. No business logic, no persistence annotations, no framework dependencies.

6. **Use Page.map() for paginated DTO conversion**: `repository.findAll(pageable).map(mapper::toResponse)` preserves pagination metadata while converting content.

---

## Summary

- **DTOs** separate internal entity structure from external API contracts. They prevent security leaks, circular references, lazy loading issues, and tight coupling.

- **Request DTOs** carry validated input data (CreateXxxRequest, UpdateXxxRequest). **Response DTOs** carry formatted output data (XxxResponse).

- **Manual mapping** is simple but tedious. **MapStruct** generates mapping code at compile time with zero runtime overhead.

- **Interface projections** let Spring Data load only the columns you need — no entity, no persistence context, no lazy loading.

- **Constructor expressions** (`SELECT new Dto(...)` in JPQL) are the most efficient — they produce DTO objects directly from the query.

- **Dynamic projections** (`<T> List<T> findBy(..., Class<T>)`) let the caller choose the projection type.

- Different use cases warrant different approaches: projections for reads, DTOs + mapping for writes.

---

## Interview Questions

**Q1: Why should you not return JPA entities from REST controllers?**

Exposing entities causes: (1) security risks (password, internal fields leaked), (2) API coupled to database schema, (3) circular references in JSON (entity A references B, B references A), (4) LazyInitializationException during serialization, (5) over-fetching (all fields sent when client needs few).

**Q2: What is the difference between interface projections and constructor expressions?**

Interface projections define getter methods that Spring proxies to map query results. They work with derived query methods without JPQL. Constructor expressions use `SELECT new DTO(...)` in JPQL to directly instantiate DTO objects. Constructor expressions give more control and create real objects (not proxies), but require explicit JPQL.

**Q3: How does MapStruct differ from runtime mapping libraries?**

MapStruct generates mapping code at compile time as plain Java method calls. There is no reflection, no runtime overhead, and missing mappings cause compile errors. Runtime libraries (like ModelMapper) use reflection to map fields, which is slower and errors are only caught at runtime.

**Q4: When would you use a projection vs loading the entity and mapping?**

Use projections for read-only endpoints where you need a subset of fields — they are more efficient (less data from DB, no persistence context). Load the full entity when you need to modify it (update/delete) or when business logic requires the complete object state.

**Q5: How do you handle partial updates with DTOs?**

Use an update DTO where all fields are optional (nullable). In the service method, check each field for null before updating the entity: `if (request.getName() != null) entity.setName(request.getName())`. MapStruct supports this with `@BeanMapping(nullValuePropertyMappingStrategy = IGNORE)`.

---

## Practice Exercises

**Exercise 1: Entity to DTO**
Create a `Product` entity with 10 fields. Create a `ProductResponse` with 6 fields and a `ProductListItem` with 3 fields. Write manual mapping methods. Test that sensitive fields (costPrice, supplierNotes) are not in the response.

**Exercise 2: MapStruct**
Add MapStruct to your project. Create a `ProductMapper` interface that maps Entity to Response, Request to Entity, and handles partial updates. Verify the generated implementation in `target/generated-sources`.

**Exercise 3: Interface Projection**
Create a `ProductSummaryProjection` interface with `getName()`, `getPrice()`, and `getCategoryName()`. Use it in a repository method. Compare the SQL generated vs loading full entities.

**Exercise 4: Constructor Expression**
Write a JPQL query using `SELECT new ProductReport(p.name, c.name, p.price, p.stockQuantity)` with a JOIN to Category. Verify it produces efficient SQL and returns the correct DTO.

**Exercise 5: Complete CRUD with DTOs**
Build a complete CRUD API for an `Employee` resource: `CreateEmployeeRequest`, `UpdateEmployeeRequest`, `EmployeeResponse`, `EmployeeListItem`. Use projections for the list endpoint, full entity + mapping for detail/create/update. Validate requests. Handle errors.

---

## What Is Next?

In the next chapter, we will explore **Repository Pattern, Service Layer, and Architecture** — how to organize a production Spring Boot application with proper layering. You will learn about the Controller-Service-Repository architecture, transaction boundaries, custom repository implementations, and base entity classes for shared behavior.
