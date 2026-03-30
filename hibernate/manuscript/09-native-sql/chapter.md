# Chapter 9: Native SQL Queries and Result Mapping

---

## Learning Goals

By the end of this chapter, you will be able to:

- Know when to use native SQL instead of JPQL
- Write native SQL queries with @Query(nativeQuery = true)
- Use named and positional parameters in native queries
- Map native query results to entities automatically
- Map native query results to DTOs using interfaces and classes
- Use @SqlResultSetMapping and @ColumnResult for complex mappings
- Use @ConstructorResult to map results to DTO constructors
- Combine native SQL with Spring Data JPA pagination
- Understand the trade-offs of native SQL vs JPQL

---

## When to Use Native SQL

JPQL handles the vast majority of queries. But there are times when you need to drop down to raw SQL:

```
+------------------------------------------------------------------+
|  Use Native SQL When:                                             |
|                                                                   |
|  1. Database-specific features                                    |
|     - Window functions (ROW_NUMBER, RANK, LAG, LEAD)              |
|     - Common Table Expressions (WITH ... AS)                      |
|     - Database-specific functions (PostgreSQL jsonb, etc.)         |
|     - Full-text search (tsvector in PostgreSQL)                    |
|                                                                   |
|  2. Complex queries that JPQL cannot express                      |
|     - UNION / INTERSECT / EXCEPT                                  |
|     - Recursive queries                                           |
|     - Complex subqueries in FROM clause                           |
|                                                                   |
|  3. Performance-critical queries                                  |
|     - Hand-tuned SQL with optimizer hints                         |
|     - Queries where JPQL generates suboptimal SQL                 |
|                                                                   |
|  4. Legacy database integration                                   |
|     - Views that do not map to entities                            |
|     - Stored procedures and functions                             |
|     - Schemas you cannot modify                                   |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|  Stick with JPQL When:                                            |
|                                                                   |
|  - Standard CRUD and simple joins                                 |
|  - You want database portability                                  |
|  - Derived query methods or @Query with JPQL work fine            |
|  - You want compile-time entity/field name validation             |
+------------------------------------------------------------------+
```

---

## Basic Native Queries with @Query

Add `nativeQuery = true` to the `@Query` annotation to write raw SQL:

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // JPQL (for comparison):
    @Query("SELECT e FROM Employee e WHERE e.active = true")
    List<Employee> findActiveJpql();

    // Native SQL (same result):
    @Query(value = "SELECT * FROM employees WHERE active = true",
           nativeQuery = true)
    List<Employee> findActiveNative();
}
```

```
JPQL vs Native SQL in @Query:
+------------------------------------------------------------------+
|  JPQL:                                                            |
|  @Query("SELECT e FROM Employee e WHERE e.active = true")         |
|  - Uses entity name (Employee) and field names (e.active)         |
|  - Database-independent                                           |
|  - Validated at startup                                           |
|                                                                   |
|  Native SQL:                                                      |
|  @Query(value = "SELECT * FROM employees WHERE active = true",    |
|         nativeQuery = true)                                       |
|  - Uses table name (employees) and column names (active)          |
|  - Database-specific                                              |
|  - NOT validated at startup (errors at runtime)                   |
+------------------------------------------------------------------+
```

### Parameters in Native Queries

```java
// Named parameters (use :paramName)
@Query(value = "SELECT * FROM employees WHERE department_id = :deptId AND salary > :minSalary",
       nativeQuery = true)
List<Employee> findByDeptAndSalary(@Param("deptId") Long deptId,
                                   @Param("minSalary") BigDecimal minSalary);

// Positional parameters (use ?1, ?2)
@Query(value = "SELECT * FROM employees WHERE department_id = ?1 AND salary > ?2",
       nativeQuery = true)
List<Employee> findByDeptAndSalary(Long deptId, BigDecimal minSalary);
```

### Native Queries That Return Entities

When you use `SELECT *` or select all columns that match the entity's mapping, Spring Data JPA automatically maps the result to the entity class:

```java
// Returns List<Employee> — automatic mapping
@Query(value = "SELECT * FROM employees WHERE active = true ORDER BY name",
       nativeQuery = true)
List<Employee> findActiveOrderByName();

// Also works with specific columns matching entity fields
@Query(value = "SELECT id, name, email, salary, active, hire_date, department_id " +
               "FROM employees WHERE salary > :min",
       nativeQuery = true)
List<Employee> findHighEarners(@Param("min") BigDecimal min);
```

**Important**: The column names in the result set must match the entity's column mappings. If you use `@Column(name = "hire_date")`, the SQL must select `hire_date`, not `hireDate`.

---

## Database-Specific Features

This is where native SQL really shines — using features that JPQL does not support.

### Window Functions

```java
// Rank employees by salary within each department
@Query(value = """
    SELECT e.*,
           RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) as salary_rank
    FROM employees e
    WHERE e.active = true
    """,
       nativeQuery = true)
List<Object[]> findEmployeesWithSalaryRank();

// Row number for pagination alternative
@Query(value = """
    SELECT * FROM (
        SELECT e.*, ROW_NUMBER() OVER (ORDER BY e.salary DESC) as rn
        FROM employees e
        WHERE e.active = true
    ) ranked WHERE rn BETWEEN :start AND :end
    """,
       nativeQuery = true)
List<Employee> findByRankRange(@Param("start") int start, @Param("end") int end);
```

### Common Table Expressions (CTEs)

```java
// Find departments where average salary exceeds the company average
@Query(value = """
    WITH company_avg AS (
        SELECT AVG(salary) as avg_salary FROM employees WHERE active = true
    ),
    dept_avg AS (
        SELECT department_id, AVG(salary) as avg_salary, COUNT(*) as emp_count
        FROM employees WHERE active = true
        GROUP BY department_id
    )
    SELECT d.id, d.name, da.avg_salary, da.emp_count
    FROM departments d
    JOIN dept_avg da ON d.id = da.department_id
    CROSS JOIN company_avg ca
    WHERE da.avg_salary > ca.avg_salary
    ORDER BY da.avg_salary DESC
    """,
       nativeQuery = true)
List<Object[]> findAboveAverageDepartments();
```

### UNION Queries

```java
// Combine results from multiple queries
@Query(value = """
    SELECT name, email, 'ACTIVE' as status FROM employees WHERE active = true
    UNION ALL
    SELECT name, email, 'INACTIVE' as status FROM employees WHERE active = false
    ORDER BY status, name
    """,
       nativeQuery = true)
List<Object[]> findAllWithStatus();
```

### H2-Specific Functions

```java
// H2 date functions
@Query(value = "SELECT * FROM employees WHERE YEAR(hire_date) = :year",
       nativeQuery = true)
List<Employee> findHiredInYear(@Param("year") int year);

// H2 string functions
@Query(value = "SELECT * FROM employees WHERE LOCATE(:keyword, LOWER(name)) > 0",
       nativeQuery = true)
List<Employee> searchName(@Param("keyword") String keyword);
```

---

## Mapping Results to DTOs

Native queries often return data that does not map to an entity. You need to map results to custom objects.

### Approach 1: Interface-Based Projections (Recommended)

The simplest and cleanest approach. Define an interface with getter methods matching the column names:

```java
// Step 1: Define a projection interface
public interface EmployeeSummaryProjection {
    String getName();
    String getEmail();
    BigDecimal getSalary();
    String getDepartmentName();  // Matches column alias "department_name"
}

// Step 2: Use it in the repository
@Query(value = """
    SELECT e.name, e.email, e.salary, d.name AS department_name
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE e.active = true
    ORDER BY e.salary DESC
    """,
       nativeQuery = true)
List<EmployeeSummaryProjection> findActiveSummaries();
```

```java
// Usage — clean and type-safe
List<EmployeeSummaryProjection> summaries = repository.findActiveSummaries();
for (EmployeeSummaryProjection s : summaries) {
    System.out.println(s.getName() + " (" + s.getDepartmentName() +
                       ") - $" + s.getSalary());
}
```

```
How Interface Projections Work:
+------------------------------------------------------------------+
|  SQL result row:                                                  |
|  | name    | email           | salary  | department_name |        |
|  | Alice   | alice@co.com    | 95000   | Engineering     |        |
|                                                                   |
|  Spring creates a proxy object implementing the interface:        |
|  proxy.getName()           --> "Alice"                            |
|  proxy.getEmail()          --> "alice@co.com"                     |
|  proxy.getSalary()         --> 95000                              |
|  proxy.getDepartmentName() --> "Engineering"                      |
|                                                                   |
|  Matching rules:                                                  |
|  - Method name getXxx maps to column "xxx" or "XXX"               |
|  - Use column aliases to match: d.name AS department_name         |
|  - Case-insensitive matching                                      |
+------------------------------------------------------------------+
```

### Approach 2: Class-Based Projections (DTO Classes)

Use a concrete class instead of an interface:

```java
// DTO class
public class DepartmentReport {
    private String departmentName;
    private long employeeCount;
    private double averageSalary;
    private BigDecimal totalSalary;

    // Constructor must match the query columns in order
    public DepartmentReport(String departmentName, long employeeCount,
                            double averageSalary, BigDecimal totalSalary) {
        this.departmentName = departmentName;
        this.employeeCount = employeeCount;
        this.averageSalary = averageSalary;
        this.totalSalary = totalSalary;
    }

    // Getters
    public String getDepartmentName() { return departmentName; }
    public long getEmployeeCount() { return employeeCount; }
    public double getAverageSalary() { return averageSalary; }
    public BigDecimal getTotalSalary() { return totalSalary; }
}
```

For native queries with class-based projections, you typically need `@SqlResultSetMapping` or return `Object[]` and map manually. Interface projections are simpler for native queries.

### Approach 3: Manual Mapping from Object[]

For complex results, sometimes manual mapping is the most practical:

```java
@Query(value = """
    SELECT d.name as dept_name,
           COUNT(e.id) as emp_count,
           COALESCE(AVG(e.salary), 0) as avg_salary,
           COALESCE(SUM(e.salary), 0) as total_salary
    FROM departments d
    LEFT JOIN employees e ON d.id = e.department_id AND e.active = true
    GROUP BY d.name
    ORDER BY emp_count DESC
    """,
       nativeQuery = true)
List<Object[]> findDepartmentReportRaw();
```

```java
// Service method that maps the results
public List<DepartmentReport> getDepartmentReport() {
    return repository.findDepartmentReportRaw().stream()
        .map(row -> new DepartmentReport(
            (String) row[0],                                // dept_name
            ((Number) row[1]).longValue(),                   // emp_count
            ((Number) row[2]).doubleValue(),                 // avg_salary
            row[3] != null ? new BigDecimal(row[3].toString()) : BigDecimal.ZERO
        ))
        .toList();
}
```

```
Projection Approaches Comparison:
+------------------------------------------------------------------+
|  Approach                  Pros                 Cons              |
|------------------------------------------------------------------|
|  Interface Projection      Clean, automatic     Cannot have       |
|  (Recommended)             Spring proxy magic   logic/methods     |
|                                                                   |
|  Class-Based DTO           Full control,        More setup for    |
|                            can add methods      native queries    |
|                                                                   |
|  Object[] + manual map     Works with any       Fragile, index-   |
|                            query shape          based, type-unsafe|
+------------------------------------------------------------------+
```

---

## @SqlResultSetMapping

For advanced result mapping, JPA provides `@SqlResultSetMapping` on the entity class. This is useful when you need to map native query results to entities or DTOs with precise control.

### Mapping to an Entity

```java
@Entity
@Table(name = "employees")
@SqlResultSetMapping(
    name = "EmployeeMapping",
    entities = @EntityResult(
        entityClass = Employee.class,
        fields = {
            @FieldResult(name = "id", column = "emp_id"),
            @FieldResult(name = "name", column = "emp_name"),
            @FieldResult(name = "email", column = "emp_email"),
            @FieldResult(name = "salary", column = "emp_salary"),
            @FieldResult(name = "active", column = "emp_active")
        }
    )
)
public class Employee {
    // ...
}
```

This is used when the SQL column names do not match the entity field mappings (perhaps from a complex join or view).

### @ConstructorResult — Mapping to DTOs

`@ConstructorResult` maps native query columns to a DTO constructor:

```java
@Entity
@Table(name = "employees")
@SqlResultSetMapping(
    name = "EmployeeSummaryMapping",
    classes = @ConstructorResult(
        targetClass = EmployeeSummary.class,
        columns = {
            @ColumnResult(name = "emp_name", type = String.class),
            @ColumnResult(name = "dept_name", type = String.class),
            @ColumnResult(name = "emp_salary", type = BigDecimal.class)
        }
    )
)
public class Employee {
    // ...
}
```

```java
// The DTO
public class EmployeeSummary {
    private String name;
    private String departmentName;
    private BigDecimal salary;

    public EmployeeSummary(String name, String departmentName, BigDecimal salary) {
        this.name = name;
        this.departmentName = departmentName;
        this.salary = salary;
    }
    // getters...
}
```

```java
// Using with EntityManager (not directly supported in @Query)
@Repository
public class CustomEmployeeRepository {

    @PersistenceContext
    private EntityManager em;

    public List<EmployeeSummary> findSummaries() {
        return em.createNativeQuery(
            "SELECT e.name AS emp_name, d.name AS dept_name, e.salary AS emp_salary " +
            "FROM employees e JOIN departments d ON e.department_id = d.id",
            "EmployeeSummaryMapping"
        ).getResultList();
    }
}
```

```
@SqlResultSetMapping usage:
+------------------------------------------------------------------+
|  For simple native queries:                                       |
|    Use interface projections (easiest)                             |
|                                                                   |
|  For complex column name remapping:                               |
|    Use @SqlResultSetMapping with @EntityResult                    |
|                                                                   |
|  For mapping to DTOs from EntityManager:                          |
|    Use @SqlResultSetMapping with @ConstructorResult               |
|                                                                   |
|  For Spring Data @Query with native SQL:                          |
|    Interface projections work best                                |
|    @SqlResultSetMapping is used with EntityManager directly       |
+------------------------------------------------------------------+
```

---

## Native Queries with Pagination

Spring Data JPA supports pagination with native queries, but requires a separate count query:

```java
// Must provide countQuery for pagination
@Query(value = "SELECT * FROM employees WHERE active = true ORDER BY name",
       countQuery = "SELECT COUNT(*) FROM employees WHERE active = true",
       nativeQuery = true)
Page<Employee> findActivePagedNative(Pageable pageable);
```

```
Why countQuery is needed:
+------------------------------------------------------------------+
|  For JPQL, Hibernate can derive the count query automatically:    |
|  @Query("SELECT e FROM Employee e WHERE e.active = true")         |
|  --> Hibernate derives: SELECT COUNT(e) FROM Employee e            |
|                         WHERE e.active = true                     |
|                                                                   |
|  For native SQL, Hibernate cannot parse the SQL to derive a       |
|  count query. You must provide it explicitly:                     |
|  @Query(value = "SELECT * FROM employees WHERE active = true",    |
|         countQuery = "SELECT COUNT(*) FROM employees ...",         |
|         nativeQuery = true)                                       |
+------------------------------------------------------------------+
```

### Pagination with Projections

```java
// Interface projection with pagination
@Query(value = "SELECT e.name, e.email, e.salary FROM employees e WHERE e.active = true",
       countQuery = "SELECT COUNT(*) FROM employees WHERE active = true",
       nativeQuery = true)
Page<EmployeeBasicProjection> findActiveProjectedPaged(Pageable pageable);

public interface EmployeeBasicProjection {
    String getName();
    String getEmail();
    BigDecimal getSalary();
}
```

### Usage

```java
// Page 0, 10 items per page, sorted by salary descending
Pageable pageable = PageRequest.of(0, 10, Sort.by("salary").descending());
Page<Employee> page = repository.findActivePagedNative(pageable);

System.out.println("Total elements: " + page.getTotalElements());
System.out.println("Total pages: " + page.getTotalPages());
System.out.println("Current page: " + page.getNumber());
page.getContent().forEach(e -> System.out.println("  " + e));
```

---

## Native UPDATE and DELETE

```java
// Native UPDATE
@Modifying
@Query(value = "UPDATE employees SET salary = salary * :factor WHERE department_id = :deptId",
       nativeQuery = true)
int adjustSalariesNative(@Param("factor") BigDecimal factor,
                         @Param("deptId") Long deptId);

// Native DELETE
@Modifying
@Query(value = "DELETE FROM employees WHERE active = false AND hire_date < :cutoff",
       nativeQuery = true)
int purgeOldInactive(@Param("cutoff") LocalDate cutoff);

// Native INSERT (rare, but possible)
@Modifying
@Query(value = "INSERT INTO employees (name, email, salary, active, department_id) " +
               "VALUES (:name, :email, :salary, true, :deptId)",
       nativeQuery = true)
void insertEmployee(@Param("name") String name, @Param("email") String email,
                    @Param("salary") BigDecimal salary, @Param("deptId") Long deptId);
```

**Note**: Native `@Modifying` queries follow the same rules as JPQL ones — they require `@Transactional` and do not update the persistence context. Use `clearAutomatically = true` when needed.

---

## Calling Database Functions and Stored Procedures

### Calling Database Functions

```java
// H2 built-in functions
@Query(value = "SELECT * FROM employees WHERE DATEDIFF('YEAR', hire_date, CURRENT_DATE) > :years",
       nativeQuery = true)
List<Employee> findLongTermEmployees(@Param("years") int years);

// Using CASE in native SQL
@Query(value = """
    SELECT e.name,
           CASE WHEN e.salary >= 100000 THEN 'Senior'
                WHEN e.salary >= 70000 THEN 'Mid-Level'
                ELSE 'Junior' END AS level
    FROM employees e
    WHERE e.active = true
    ORDER BY e.salary DESC
    """,
       nativeQuery = true)
List<Object[]> findEmployeeLevels();
```

### Calling Stored Procedures (JPA Standard)

```java
// Define the stored procedure call on the entity
@Entity
@NamedStoredProcedureQuery(
    name = "Employee.raiseByDepartment",
    procedureName = "raise_by_department",
    parameters = {
        @StoredProcedureParameter(mode = ParameterMode.IN,
            name = "dept_id", type = Long.class),
        @StoredProcedureParameter(mode = ParameterMode.IN,
            name = "raise_pct", type = BigDecimal.class),
        @StoredProcedureParameter(mode = ParameterMode.OUT,
            name = "affected_count", type = Integer.class)
    }
)
public class Employee { ... }

// Call from repository
@Procedure(name = "Employee.raiseByDepartment")
int raiseByDepartment(@Param("dept_id") Long deptId,
                      @Param("raise_pct") BigDecimal raisePct);
```

---

## Mixing Native SQL and JPQL

In practice, most repositories use a combination of derived methods, JPQL, and native SQL:

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // === Derived Methods (simplest queries) ===
    List<Employee> findByActiveTrue();
    Optional<Employee> findByEmail(String email);
    long countByDepartment_Name(String deptName);

    // === JPQL (standard queries with entity navigation) ===
    @Query("SELECT e FROM Employee e JOIN FETCH e.department WHERE e.active = true")
    List<Employee> findActiveWithDepartment();

    @Query("SELECT new com.example.dto.EmployeeSummary(e.name, d.name, e.salary) " +
           "FROM Employee e JOIN e.department d ORDER BY e.salary DESC")
    List<EmployeeSummary> findSummaries();

    // === Native SQL (database-specific features) ===
    @Query(value = """
        SELECT e.*, RANK() OVER (PARTITION BY e.department_id
                                 ORDER BY e.salary DESC) as rnk
        FROM employees e
        WHERE e.active = true
        """,
           nativeQuery = true)
    List<Object[]> findWithDepartmentRank();

    @Query(value = """
        WITH dept_stats AS (
            SELECT department_id, AVG(salary) as avg_sal
            FROM employees WHERE active = true
            GROUP BY department_id
        )
        SELECT e.* FROM employees e
        JOIN dept_stats ds ON e.department_id = ds.department_id
        WHERE e.salary > ds.avg_sal * 1.2
        """,
           nativeQuery = true)
    List<Employee> findTopPerformers();
}
```

```
Decision Guide: Which Query Type to Use?
+------------------------------------------------------------------+
|  Start Here                                                       |
|      |                                                            |
|      v                                                            |
|  Can a derived method express it?                                 |
|      |                                                            |
|   YES --> Use derived method (findByNameContaining, etc.)         |
|      |                                                            |
|    NO                                                             |
|      |                                                            |
|      v                                                            |
|  Can JPQL express it? (joins, aggregates, subqueries)             |
|      |                                                            |
|   YES --> Use @Query with JPQL                                    |
|      |                                                            |
|    NO                                                             |
|      |                                                            |
|      v                                                            |
|  Need DB-specific features?                                       |
|  (window functions, CTEs, UNION, hints)                           |
|      |                                                            |
|   YES --> Use @Query(nativeQuery = true) with native SQL          |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Using entity/field names in native queries**: Native SQL uses **table and column names**, not entity and field names. `SELECT * FROM Employee` fails; use `SELECT * FROM employees`.

2. **Forgetting countQuery with pagination**: `Page<T>` return type with native queries requires an explicit `countQuery`. Without it, you get an error.

3. **Column name mismatches with interface projections**: The getter method name (`getDepartmentName`) must match the column name or alias (`department_name`). Case-insensitive, but underscores matter.

4. **Losing database portability**: Native SQL ties your code to a specific database. If you switch from H2 to PostgreSQL, some native queries might need changes (different date functions, syntax variations).

5. **Not using clearAutomatically on @Modifying native queries**: Same as JPQL — bulk updates via native SQL do not update the persistence context.

6. **Expecting native queries to be validated at startup**: Unlike JPQL, native SQL is not parsed by Hibernate at startup. Syntax errors are only caught at runtime when the query executes.

---

## Best Practices

1. **Prefer JPQL over native SQL**: Use native SQL only when JPQL cannot express what you need. JPQL is portable, validated at startup, and works with entity relationships naturally.

2. **Use interface projections for native query results**: They are the simplest and cleanest way to map non-entity results from native queries.

3. **Always provide countQuery for paginated native queries**: This is required and prevents runtime errors.

4. **Use text blocks (triple quotes) for long queries**: Java text blocks (`"""..."""`) make multi-line SQL queries much more readable than string concatenation.

5. **Comment your native queries**: Since native SQL is not self-documenting like JPQL (which uses entity names), add comments explaining why native SQL is needed and what database-specific features it uses.

6. **Test native queries against your target database**: If you develop with H2 but deploy to PostgreSQL, test native queries against PostgreSQL early. SQL dialects differ.

---

## Summary

In this chapter, you learned when and how to use native SQL queries:

- **Native SQL** is needed for database-specific features (window functions, CTEs, UNION), complex queries that JPQL cannot express, and performance-critical hand-tuned SQL.

- **@Query(nativeQuery = true)** enables native SQL in Spring Data JPA repositories. It uses table/column names instead of entity/field names.

- **Interface projections** are the recommended way to map native query results to DTOs. Define an interface with getters matching column names/aliases.

- **@SqlResultSetMapping** with **@ConstructorResult** provides advanced result mapping for complex native queries used with EntityManager.

- **Pagination** with native queries requires an explicit `countQuery` parameter.

- **Native @Modifying** works the same as JPQL — use for bulk UPDATE/DELETE, requires @Transactional, does not update the persistence context.

- **The decision hierarchy**: Use derived methods first, then JPQL, then native SQL. Each step adds power but reduces portability.

---

## Interview Questions

**Q1: When should you use native SQL instead of JPQL?**

Use native SQL for: database-specific features (window functions, CTEs, full-text search), UNION queries, recursive queries, complex subqueries in FROM clauses, optimizer hints, queries against views or legacy schemas, and when JPQL generates suboptimal SQL that needs hand-tuning.

**Q2: How do you map native query results to DTOs in Spring Data JPA?**

The simplest approach is interface-based projections: define an interface with getter methods matching column names or aliases, and use it as the return type. For more complex mappings, use `@SqlResultSetMapping` with `@ConstructorResult` on the entity class, or manually map `Object[]` results in a service method.

**Q3: Why does a native query with Page return type require a countQuery?**

For JPQL, Hibernate can automatically derive a count query by analyzing the query structure. For native SQL, Hibernate cannot parse the SQL to derive a count. The count query must be provided explicitly so Spring Data can determine the total number of elements for pagination metadata.

**Q4: What is the key difference between native SQL and JPQL in terms of naming?**

JPQL uses entity class names and Java field names (e.g., `SELECT e FROM Employee e WHERE e.firstName = :name`). Native SQL uses database table names and column names (e.g., `SELECT * FROM employees WHERE first_name = :name`). This is the most common source of errors when switching between the two.

**Q5: Are native queries validated at application startup?**

No. JPQL queries (both @Query and @NamedQuery) are parsed and validated at startup — a typo causes an immediate error. Native SQL is passed directly to the database at runtime. Syntax errors are only caught when the query is actually executed.

**Q6: How do interface projections work with native queries?**

Spring Data creates a dynamic proxy implementing the projection interface. When a native query returns results, Spring maps each column to the corresponding getter method by matching the getter name to the column name or alias (case-insensitive). `getDepartmentName()` maps to a column named `department_name` or `DEPARTMENT_NAME`.

---

## Practice Exercises

**Exercise 1: Window Functions**
Write a native query that ranks employees by salary within each department using `RANK() OVER (PARTITION BY ...)`. Return the results with employee name, department, salary, and rank. Use an interface projection.

**Exercise 2: CTE Query**
Write a native query using a CTE that finds employees whose salary is more than 20% above their department's average. Test it with sample data.

**Exercise 3: Projection Comparison**
Write the same query (employees with department names, salary above a threshold) three ways: (a) returning `Object[]`, (b) using an interface projection, (c) using JPQL with a constructor expression. Compare the code clarity.

**Exercise 4: Paginated Native Query**
Write a native query that returns all active employees with pagination support. Include the countQuery. Test with `PageRequest.of(0, 5)` and verify the total elements, total pages, and content.

**Exercise 5: Mixed Repository**
Create a repository for a `Product` entity that uses all three query types: 3 derived methods, 3 JPQL queries, and 3 native queries. Choose each type based on the complexity of the query. Explain your choices.

---

## What Is Next?

In the next chapter, we will explore the **Criteria API — Type-Safe Dynamic Queries**. While JPQL and native SQL are string-based (and prone to typos), the Criteria API lets you build queries programmatically with compile-time type safety. You will learn how to use `CriteriaBuilder`, `CriteriaQuery`, and `Predicate` for dynamic query construction, and how Spring Data Specifications make the Criteria API practical for everyday use.
