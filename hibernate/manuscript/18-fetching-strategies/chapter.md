# Chapter 18: Fetching Strategies — Solving the N+1 Problem

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the difference between lazy and eager fetching
- Explain why the N+1 problem is the most common Hibernate performance issue
- Detect the N+1 problem using SQL logging
- Solve N+1 with JOIN FETCH in JPQL queries
- Use @EntityGraph for query-level fetch control
- Apply @BatchSize (Hibernate) to batch lazy loads
- Use @Fetch(FetchMode.SUBSELECT) for collection fetching
- Understand and fix LazyInitializationException
- Choose the right fetching strategy for different use cases
- Profile and measure fetching performance

---

## Lazy vs Eager Fetching

Every JPA relationship has a fetch type that controls when related data is loaded from the database.

```
Fetch Types:
+------------------------------------------------------------------+
|                                                                   |
|  FetchType.EAGER:                                                 |
|  Load the related entity IMMEDIATELY with the parent.             |
|  One query loads everything via JOIN.                              |
|                                                                   |
|  Employee e = em.find(Employee.class, 1L);                        |
|  SQL: SELECT e.*, d.*                                             |
|       FROM employees e                                            |
|       LEFT JOIN departments d ON e.department_id = d.id           |
|       WHERE e.id = 1                                              |
|  --> Department loaded immediately, even if never accessed         |
|                                                                   |
|  FetchType.LAZY:                                                  |
|  Load the related entity ONLY when it is accessed.                |
|  Parent loaded first, related data loaded on demand.              |
|                                                                   |
|  Employee e = em.find(Employee.class, 1L);                        |
|  SQL: SELECT e.* FROM employees e WHERE e.id = 1                  |
|  --> Department NOT loaded yet                                    |
|                                                                   |
|  e.getDepartment().getName();  // NOW it loads                    |
|  SQL: SELECT d.* FROM departments d WHERE d.id = 5               |
|  --> Department loaded on first access                            |
+------------------------------------------------------------------+
```

### JPA Default Fetch Types

```
Default Fetch Types:
+------------------------------------------------------------------+
|                                                                   |
|  Annotation         Default FetchType   Recommendation            |
|  ----------------------------------------------------------------|
|  @ManyToOne          EAGER              Change to LAZY!           |
|  @OneToOne           EAGER              Change to LAZY!           |
|  @OneToMany          LAZY               Keep LAZY (good default)  |
|  @ManyToMany         LAZY               Keep LAZY (good default)  |
|                                                                   |
|  Single-value associations (@ManyToOne, @OneToOne) default to     |
|  EAGER because loading one extra row seems cheap.                 |
|  BUT this compounds: 1000 employees = 1000 department loads!     |
|                                                                   |
|  RULE: Make EVERYTHING lazy, then eagerly fetch what you          |
|  need per query using JOIN FETCH or @EntityGraph.                 |
+------------------------------------------------------------------+
```

**Always override the defaults:**

```java
// BAD — uses default EAGER (loads department with every query)
@ManyToOne
private Department department;

// GOOD — lazy by default, load explicitly when needed
@ManyToOne(fetch = FetchType.LAZY)
private Department department;
```

---

## The N+1 Problem Explained

The N+1 problem is the single most common cause of poor Hibernate performance. It happens when loading N entities triggers N additional queries for their relationships.

```
The N+1 Problem — Step by Step:
+------------------------------------------------------------------+
|                                                                   |
|  Goal: Display 10 departments with their employee counts         |
|                                                                   |
|  Code:                                                            |
|  List<Department> depts = departmentRepository.findAll();         |
|  for (Department d : depts) {                                     |
|      System.out.println(d.getName() + ": " +                      |
|          d.getEmployees().size());  // Triggers lazy load!        |
|  }                                                                |
|                                                                   |
|  SQL queries generated:                                           |
|  ----------------------------------------------------------------|
|  Query 1:  SELECT * FROM departments                 (1 query)   |
|            Returns 10 departments                                 |
|                                                                   |
|  Query 2:  SELECT * FROM employees                               |
|            WHERE department_id = 1                   (dept #1)    |
|  Query 3:  SELECT * FROM employees                               |
|            WHERE department_id = 2                   (dept #2)    |
|  Query 4:  SELECT * FROM employees                               |
|            WHERE department_id = 3                   (dept #3)    |
|  ...                                                              |
|  Query 11: SELECT * FROM employees                               |
|            WHERE department_id = 10                  (dept #10)   |
|                                                                   |
|  Total: 1 + 10 = 11 queries   (N+1 where N=10)                  |
|                                                                   |
|  With 100 departments:  101 queries                               |
|  With 1000 departments: 1001 queries!                             |
+------------------------------------------------------------------+
```

### N+1 with @ManyToOne (Eager Default)

The N+1 problem also happens with `@ManyToOne` when the default EAGER fetch type is not overridden:

```
@ManyToOne N+1:
+------------------------------------------------------------------+
|                                                                   |
|  @ManyToOne  // Default: EAGER!                                   |
|  private Department department;                                   |
|                                                                   |
|  List<Employee> employees = employeeRepository.findAll();         |
|                                                                   |
|  SQL queries:                                                     |
|  Query 1:  SELECT * FROM employees               (loads 100 emps)|
|                                                                   |
|  Hibernate sees EAGER @ManyToOne, loads each department:          |
|  Query 2:  SELECT * FROM departments WHERE id = 1                 |
|  Query 3:  SELECT * FROM departments WHERE id = 2                 |
|  Query 4:  SELECT * FROM departments WHERE id = 1  (duplicate!)   |
|  Query 5:  SELECT * FROM departments WHERE id = 3                 |
|  ...                                                              |
|                                                                   |
|  Even with persistence context caching (same dept not queried     |
|  twice), you still get 1 + number_of_unique_departments queries!  |
|                                                                   |
|  FIX: @ManyToOne(fetch = FetchType.LAZY)                          |
|  Then use JOIN FETCH when you actually need the department.       |
+------------------------------------------------------------------+
```

---

## Solution 1: JOIN FETCH in JPQL

`JOIN FETCH` tells Hibernate to load the relationship in the same query using a SQL JOIN:

```java
@Repository
public interface DepartmentRepository extends JpaRepository<Department, Long> {

    // WITHOUT JOIN FETCH — causes N+1
    @Query("SELECT d FROM Department d")
    List<Department> findAllBasic();
    // 1 query + N lazy loads when accessing employees

    // WITH JOIN FETCH — single query
    @Query("SELECT d FROM Department d LEFT JOIN FETCH d.employees")
    List<Department> findAllWithEmployees();
    // 1 query! All departments AND their employees loaded together
}
```

```
JOIN FETCH Generated SQL:
+------------------------------------------------------------------+
|                                                                   |
|  JPQL:  SELECT d FROM Department d LEFT JOIN FETCH d.employees    |
|                                                                   |
|  SQL:   SELECT d.*, e.*                                           |
|         FROM departments d                                        |
|         LEFT JOIN employees e ON d.id = e.department_id           |
|                                                                   |
|  Result set (denormalized):                                       |
|  | d.id | d.name      | e.id | e.name  | e.department_id |       |
|  |------|-------------|------|---------|-----------------|       |
|  | 1    | Engineering | 10   | Alice   | 1               |       |
|  | 1    | Engineering | 11   | Bob     | 1               |       |
|  | 1    | Engineering | 12   | Carol   | 1               |       |
|  | 2    | Marketing   | 13   | Dave    | 2               |       |
|  | 2    | Marketing   | 14   | Eve     | 2               |       |
|  | 3    | Sales       | NULL | NULL    | NULL            |       |
|  (LEFT JOIN includes Sales even though it has no employees)       |
|                                                                   |
|  Hibernate de-duplicates the result into:                         |
|  Department(1, "Engineering") --> [Alice, Bob, Carol]             |
|  Department(2, "Marketing")   --> [Dave, Eve]                     |
|  Department(3, "Sales")       --> []                              |
|                                                                   |
|  Total: 1 query instead of N+1!                                  |
+------------------------------------------------------------------+
```

### Multiple JOIN FETCH

```java
// Fetch department AND projects for employees
@Query("SELECT e FROM Employee e " +
       "LEFT JOIN FETCH e.department " +
       "LEFT JOIN FETCH e.projects " +
       "WHERE e.active = true")
List<Employee> findActiveWithDeptAndProjects();
```

### JOIN FETCH Limitations

```
JOIN FETCH Limitations:
+------------------------------------------------------------------+
|                                                                   |
|  1. Cannot JOIN FETCH multiple collections (bags):                |
|     SELECT d FROM Department d                                    |
|       LEFT JOIN FETCH d.employees                                 |
|       LEFT JOIN FETCH d.projects    <-- MultipleBagFetchException!|
|                                                                   |
|     Reason: Fetching two Lists creates a Cartesian product        |
|     with ambiguous results.                                       |
|                                                                   |
|     Fixes:                                                        |
|     a. Use Set instead of List for collections                    |
|     b. Fetch in separate queries (two queries, each with          |
|        one JOIN FETCH)                                            |
|     c. Use @BatchSize on one collection                           |
|                                                                   |
|  2. Cannot use JOIN FETCH with COUNT for pagination:              |
|     Page<Department> findAll(Pageable p)                          |
|     with JOIN FETCH fails for count query derivation.             |
|     --> Provide explicit countQuery.                              |
|                                                                   |
|  3. LEFT JOIN FETCH vs JOIN FETCH:                                |
|     LEFT JOIN FETCH: includes parents with no children            |
|     JOIN FETCH: excludes parents with no children                 |
|     Usually you want LEFT JOIN FETCH.                             |
+------------------------------------------------------------------+
```

### DISTINCT with JOIN FETCH

JOIN FETCH with `@OneToMany` can produce duplicate parent entities:

```java
// WITHOUT DISTINCT — departments may appear multiple times!
@Query("SELECT d FROM Department d LEFT JOIN FETCH d.employees")
List<Department> findAllWithEmployees();
// Engineering appears 3 times (once for each employee)

// WITH DISTINCT — each department appears once
@Query("SELECT DISTINCT d FROM Department d LEFT JOIN FETCH d.employees")
List<Department> findAllWithEmployeesDistinct();
// Engineering appears once with 3 employees
```

```
DISTINCT Behavior:
+------------------------------------------------------------------+
|                                                                   |
|  Without DISTINCT:                                                |
|  findAllWithEmployees() returns:                                  |
|  [Engineering, Engineering, Engineering, Marketing, Marketing]    |
|  (3 copies of Engineering, 2 copies of Marketing)                |
|                                                                   |
|  With DISTINCT:                                                   |
|  findAllWithEmployeesDistinct() returns:                          |
|  [Engineering, Marketing, Sales]                                  |
|  (one of each, with employees fully loaded)                       |
|                                                                   |
|  Hibernate 6 applies DISTINCT at the entity level,                |
|  not the SQL level (avoids adding DISTINCT to SQL which           |
|  would slow down the database query).                             |
+------------------------------------------------------------------+
```

---

## Solution 2: @EntityGraph

`@EntityGraph` (JPA 2.1) specifies fetch plans at the query level without writing JPQL:

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // Override findAll() with eager department loading
    @Override
    @EntityGraph(attributePaths = {"department"})
    List<Employee> findAll();

    // Fetch department for specific queries
    @EntityGraph(attributePaths = {"department"})
    List<Employee> findByActive(boolean active);

    // Fetch multiple relationships
    @EntityGraph(attributePaths = {"department", "projects"})
    Optional<Employee> findById(Long id);

    // Nested paths
    @EntityGraph(attributePaths = {"department", "department.company"})
    List<Employee> findBySalaryGreaterThan(BigDecimal min);

    // Combine with JPQL
    @EntityGraph(attributePaths = {"department"})
    @Query("SELECT e FROM Employee e WHERE e.salary > :min")
    List<Employee> findHighEarnersWithDept(@Param("min") BigDecimal min);
}
```

```
@EntityGraph vs JOIN FETCH:
+------------------------------------------------------------------+
|                                                                   |
|  @EntityGraph:                                                    |
|  + Works on derived query methods (findByX)                       |
|  + Clean — no JPQL needed                                         |
|  + Easy to add/remove relationships                               |
|  - Cannot control JOIN type (always LEFT JOIN)                    |
|  - Cannot filter the fetched collection                           |
|                                                                   |
|  JOIN FETCH:                                                      |
|  + Full control over JOIN type (LEFT, INNER)                      |
|  + Can add WHERE conditions on the joined entity                  |
|  + More explicit about what happens                               |
|  - Requires JPQL query                                            |
|  - More verbose                                                   |
|                                                                   |
|  When to use which:                                               |
|  - Simple eager loading on derived methods: @EntityGraph           |
|  - Complex queries with conditions on joined data: JOIN FETCH     |
|  - Both solve the N+1 problem equally well                       |
+------------------------------------------------------------------+
```

---

## Solution 3: @BatchSize (Hibernate-Specific)

`@BatchSize` tells Hibernate to batch multiple lazy loads into a single query using `IN (...)`:

```java
@Entity
@Table(name = "departments")
public class Department {

    @OneToMany(mappedBy = "department")
    @BatchSize(size = 10)    // Hibernate-specific
    private List<Employee> employees = new ArrayList<>();
}
```

```
@BatchSize Behavior:
+------------------------------------------------------------------+
|                                                                   |
|  Without @BatchSize — standard lazy loading (N+1):                |
|  Query 1: SELECT * FROM departments  (10 departments)             |
|  Query 2: SELECT * FROM employees WHERE department_id = 1         |
|  Query 3: SELECT * FROM employees WHERE department_id = 2         |
|  ...                                                              |
|  Query 11: SELECT * FROM employees WHERE department_id = 10       |
|  Total: 11 queries                                                |
|                                                                   |
|  With @BatchSize(size = 10):                                      |
|  Query 1: SELECT * FROM departments  (10 departments)             |
|  Query 2: SELECT * FROM employees                                 |
|           WHERE department_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) |
|  Total: 2 queries!                                                |
|                                                                   |
|  With 25 departments and @BatchSize(size = 10):                   |
|  Query 1: SELECT * FROM departments  (25 departments)             |
|  Query 2: SELECT ... WHERE department_id IN (1,2,...,10)           |
|  Query 3: SELECT ... WHERE department_id IN (11,12,...,20)         |
|  Query 4: SELECT ... WHERE department_id IN (21,22,...,25)         |
|  Total: 4 queries (1 + ceil(25/10) = 4)                          |
|                                                                   |
|  N+1 reduced to 1 + ceil(N / batchSize)                           |
+------------------------------------------------------------------+
```

### Global @BatchSize

Set a default batch size for all lazy collections:

```properties
# application.properties
spring.jpa.properties.hibernate.default_batch_fetch_size=16
```

This applies `@BatchSize(size = 16)` to all lazy collections and `@ManyToOne` relationships without needing to annotate each one.

```
When to Use @BatchSize:
+------------------------------------------------------------------+
|                                                                   |
|  @BatchSize is great when:                                        |
|  - You cannot use JOIN FETCH (multiple collections)               |
|  - You want a "good enough" global optimization                   |
|  - You do not want to write custom JPQL for every query           |
|  - Some queries need the collection, others do not                |
|                                                                   |
|  @BatchSize is NOT ideal when:                                    |
|  - You always need the collection (JOIN FETCH is faster: 1 query) |
|  - You need precise control over the SQL                          |
+------------------------------------------------------------------+
```

---

## Solution 4: @Fetch(FetchMode.SUBSELECT) (Hibernate-Specific)

`SUBSELECT` fetching loads ALL collections in a single query using a subquery:

```java
@Entity
public class Department {

    @OneToMany(mappedBy = "department")
    @Fetch(FetchMode.SUBSELECT)    // Hibernate-specific
    private List<Employee> employees = new ArrayList<>();
}
```

```
SUBSELECT Behavior:
+------------------------------------------------------------------+
|                                                                   |
|  Query 1: SELECT * FROM departments WHERE active = true           |
|           (returns 50 departments)                                |
|                                                                   |
|  When any department's employees are accessed:                    |
|  Query 2: SELECT * FROM employees WHERE department_id IN          |
|           (SELECT id FROM departments WHERE active = true)        |
|           (loads ALL employees for ALL 50 departments at once)    |
|                                                                   |
|  Total: 2 queries regardless of number of departments!            |
|                                                                   |
|  Comparison:                                                      |
|  N+1 (no optimization):     1 + 50 = 51 queries                  |
|  @BatchSize(size = 10):     1 + 5  = 6 queries                   |
|  @Fetch(SUBSELECT):         1 + 1  = 2 queries (always)          |
|  JOIN FETCH:                1 query (but data is denormalized)    |
+------------------------------------------------------------------+
```

---

## Solving MultipleBagFetchException

When you try to JOIN FETCH two `List<>` collections, Hibernate throws `MultipleBagFetchException`:

```java
// FAILS! Cannot fetch two Lists at once.
@Query("SELECT d FROM Department d " +
       "LEFT JOIN FETCH d.employees " +
       "LEFT JOIN FETCH d.projects")
List<Department> findWithAll();
// --> MultipleBagFetchException
```

```
Solutions for MultipleBagFetchException:
+------------------------------------------------------------------+
|                                                                   |
|  Solution 1: Use Set instead of List                              |
|  @OneToMany(mappedBy = "department")                              |
|  private Set<Employee> employees = new HashSet<>();               |
|  --> Sets do not cause Cartesian product ambiguity                |
|  --> JOIN FETCH of multiple Sets works                            |
|                                                                   |
|  Solution 2: Fetch in separate queries                            |
|  @EntityGraph(attributePaths = {"employees"})                     |
|  List<Department> findAllWithEmployees();                         |
|                                                                   |
|  @EntityGraph(attributePaths = {"projects"})                      |
|  List<Department> findAllWithProjects();                          |
|  --> Call both methods; persistence context merges results        |
|                                                                   |
|  Solution 3: Use @BatchSize on one collection                     |
|  JOIN FETCH the primary collection                                |
|  @BatchSize on the secondary collection                           |
|  --> 1 JOIN FETCH + batched lazy loading                          |
|                                                                   |
|  Solution 4: Fetch one, use SUBSELECT for the other               |
|  JOIN FETCH employees                                              |
|  @Fetch(FetchMode.SUBSELECT) on projects                          |
+------------------------------------------------------------------+
```

### Solution 2 in Practice: Two-Query Approach

```java
@Service
@Transactional(readOnly = true)
public class DepartmentService {

    private final DepartmentRepository repository;

    public List<Department> findAllWithEverything() {
        // Query 1: Load departments + employees
        List<Department> departments = repository.findAllWithEmployees();

        // Query 2: Load same departments + projects
        // Persistence context already has these departments,
        // so this just adds the projects to the same instances
        repository.findAllWithProjects();

        // Both collections are now loaded on the same objects
        return departments;
    }
}
```

---

## LazyInitializationException

This exception occurs when you access a lazy relationship outside the persistence context (after the transaction has ended):

```
LazyInitializationException:
+------------------------------------------------------------------+
|                                                                   |
|  @Service                                                         |
|  public class EmployeeService {                                   |
|                                                                   |
|      @Transactional                                               |
|      public Employee getEmployee(Long id) {                       |
|          return employeeRepository.findById(id).orElseThrow();    |
|      }                                                            |
|  }                                                                |
|                                                                   |
|  @RestController                                                  |
|  public class EmployeeController {                                |
|                                                                   |
|      public String getDeptName(@PathVariable Long id) {           |
|          Employee e = service.getEmployee(id);                    |
|          // Transaction already ended!                             |
|          // Persistence context is closed!                        |
|          return e.getDepartment().getName();                       |
|          //      ^^^^^^^^^^^^^^^^                                 |
|          // LazyInitializationException!                          |
|          // Cannot initialize proxy — no Session                  |
|      }                                                            |
|  }                                                                |
|                                                                   |
+------------------------------------------------------------------+
```

### Fixes for LazyInitializationException

```
How to Fix LazyInitializationException:
+------------------------------------------------------------------+
|                                                                   |
|  Fix 1: Load the data within the transaction (BEST)               |
|  @Transactional(readOnly = true)                                  |
|  public EmployeeDto getEmployee(Long id) {                        |
|      Employee e = repository.findById(id).orElseThrow();          |
|      return new EmployeeDto(                                      |
|          e.getName(),                                              |
|          e.getDepartment().getName()  // Loaded inside @Tx        |
|      );                                                           |
|  }                                                                |
|                                                                   |
|  Fix 2: Use JOIN FETCH or @EntityGraph                             |
|  @EntityGraph(attributePaths = {"department"})                    |
|  Optional<Employee> findWithDeptById(Long id);                    |
|  --> Department loaded eagerly with the employee                  |
|                                                                   |
|  Fix 3: Use a DTO projection (no entity, no lazy issue)           |
|  @Query("SELECT new com.example.EmployeeDto(e.name, d.name) " +  |
|         "FROM Employee e JOIN e.department d WHERE e.id = :id")   |
|  Optional<EmployeeDto> findDtoById(@Param("id") Long id);        |
|                                                                   |
|  DO NOT FIX WITH:                                                 |
|  - Making everything EAGER (causes N+1 everywhere)               |
|  - Enabling OSIV (masks the problem, causes hidden N+1)          |
|  - Hibernate.initialize() outside transaction (too late)          |
+------------------------------------------------------------------+
```

---

## Detecting N+1 Problems

### Enable SQL Logging

```properties
# application.properties
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# Better: use logging with parameter values
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.orm.jdbc.bind=TRACE
```

### Hibernate Statistics

```properties
# Enable statistics
spring.jpa.properties.hibernate.generate_statistics=true
```

```java
// Programmatic check
@Autowired
private EntityManagerFactory emf;

public void checkQueryCount() {
    Statistics stats = emf.unwrap(SessionFactory.class).getStatistics();
    stats.clear();

    // Execute your code here
    departmentService.getAllWithEmployees();

    long queryCount = stats.getQueryExecutionCount();
    System.out.println("Queries executed: " + queryCount);
    // If this shows 11 for 10 departments, you have N+1!
}
```

### Assert Query Count in Tests

```java
// Using datasource-proxy or a custom counter
@Test
void shouldLoadDepartmentsInOneQuery() {
    // Enable query counter
    long before = getQueryCount();

    List<Department> depts = repository.findAllWithEmployees();
    depts.forEach(d -> d.getEmployees().size()); // Force access

    long queries = getQueryCount() - before;
    assertThat(queries).isEqualTo(1); // Exactly 1 query, no N+1
}
```

---

## Fetching Strategy Decision Guide

```
Which Fetching Strategy to Use:
+------------------------------------------------------------------+
|                                                                   |
|  Always need the related data?                                    |
|      |                                                            |
|   YES                                                             |
|      |                                                            |
|      v                                                            |
|  Single collection or @ManyToOne?                                 |
|      |                                                            |
|   YES --> JOIN FETCH or @EntityGraph                              |
|      |    (1 query, most efficient)                               |
|      |                                                            |
|   Multiple collections?                                           |
|      |                                                            |
|      +--> Can use Set? --> JOIN FETCH both                        |
|      |                                                            |
|      +--> Must use List? --> Two queries or                       |
|           JOIN FETCH one + @BatchSize on the other                |
|                                                                   |
|  Sometimes need the related data?                                 |
|      |                                                            |
|      +--> @BatchSize (global default)                             |
|      |    Lazy by default, batch-loads when accessed              |
|      |    Best "general purpose" optimization                     |
|      |                                                            |
|      +--> @Fetch(SUBSELECT) (always loads ALL in 1 extra query)  |
|                                                                   |
|  Never need the related data?                                     |
|      |                                                            |
|      +--> FetchType.LAZY, no optimization needed                  |
|           (never accessed = never loaded = zero overhead)         |
+------------------------------------------------------------------+
```

```
Performance Comparison (10 departments, each with employees):
+------------------------------------------------------------------+
|                                                                   |
|  Strategy                       Queries   Notes                   |
|  ----------------------------------------------------------------|
|  Default LAZY (N+1)             11        1 + 10 lazy loads       |
|  @BatchSize(size = 10)          2         1 + 1 batch IN(...)     |
|  @BatchSize(size = 5)           3         1 + 2 batches           |
|  @Fetch(SUBSELECT)              2         1 + 1 subquery          |
|  JOIN FETCH                     1         Everything in 1 query   |
|  @EntityGraph                   1         Same as JOIN FETCH      |
|  EAGER (default on @ManyToOne)  11        Same as N+1!            |
|                                                                   |
|  Note: JOIN FETCH returns more data (denormalized result set)     |
|  which uses more memory and network bandwidth.                    |
|  @BatchSize/SUBSELECT return normalized data in fewer queries.    |
|  For large result sets, 2 queries may be faster than 1 large one. |
+------------------------------------------------------------------+
```

---

## Real-World Example: Employee Dashboard

```java
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String email;
    private BigDecimal salary;
    private boolean active;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(name = "employee_projects",
        joinColumns = @JoinColumn(name = "employee_id"),
        inverseJoinColumns = @JoinColumn(name = "project_id"))
    private Set<Project> projects = new HashSet<>();
}
```

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // For list view (just need department name)
    @EntityGraph(attributePaths = {"department"})
    List<Employee> findByActive(boolean active);

    // For detail view (need everything)
    @Query("SELECT DISTINCT e FROM Employee e " +
           "LEFT JOIN FETCH e.department " +
           "LEFT JOIN FETCH e.projects " +
           "WHERE e.id = :id")
    Optional<Employee> findDetailById(@Param("id") Long id);

    // For reporting (no relationships needed — use DTO)
    @Query("SELECT new com.example.dto.EmployeeReport(" +
           "e.name, e.salary, d.name) " +
           "FROM Employee e JOIN e.department d " +
           "WHERE e.active = true")
    List<EmployeeReport> findActiveReport();
}
```

```java
@Service
@Transactional(readOnly = true)
public class EmployeeService {

    private final EmployeeRepository repository;

    // List endpoint — loads department for display
    public List<EmployeeListDto> getActiveEmployees() {
        return repository.findByActive(true).stream()
            .map(e -> new EmployeeListDto(
                e.getId(),
                e.getName(),
                e.getDepartment().getName() // Already loaded via @EntityGraph
            ))
            .toList();
    }

    // Detail endpoint — loads everything
    public EmployeeDetailDto getEmployeeDetail(Long id) {
        Employee e = repository.findDetailById(id).orElseThrow();
        return new EmployeeDetailDto(
            e.getId(),
            e.getName(),
            e.getDepartment().getName(),
            e.getProjects().stream().map(Project::getName).toList()
        );
    }

    // Report endpoint — no entities at all
    public List<EmployeeReport> getReport() {
        return repository.findActiveReport();
    }
}
```

```
Different Fetch Plans for Different Use Cases:
+------------------------------------------------------------------+
|                                                                   |
|  Use Case           Relationships Needed    Approach              |
|  ----------------------------------------------------------------|
|  Employee list      department name         @EntityGraph({dept})  |
|  Employee detail    dept + projects         JOIN FETCH both       |
|  Salary report      dept name only          DTO projection        |
|  Employee search    none (just employee)    No fetch optimization |
|  Bulk update        none                    JPQL UPDATE           |
|                                                                   |
|  Key insight: There is no single "right" fetch plan.              |
|  Different screens/APIs need different data, so use               |
|  different queries with different fetch strategies.               |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Leaving @ManyToOne as default EAGER**: This is the #1 cause of N+1 in real applications. Always set `fetch = FetchType.LAZY` on `@ManyToOne` and `@OneToOne`.

2. **Adding EAGER to fix LazyInitializationException**: This "fixes" one place but adds unnecessary joins everywhere else. Use `@EntityGraph` or `JOIN FETCH` on the specific queries that need the data.

3. **Using JOIN FETCH without DISTINCT**: `@OneToMany` JOIN FETCH produces duplicate parent entities. Always add `DISTINCT` in the JPQL.

4. **Fetching two Lists with JOIN FETCH**: Two `List<>` collections cause `MultipleBagFetchException`. Convert to `Set<>` or use separate queries.

5. **Not detecting N+1 during development**: Enable SQL logging and Hibernate statistics during development. Check query counts for list operations. N+1 is invisible without logging.

6. **Applying the same fetch strategy everywhere**: Different queries need different fetch plans. A list endpoint needs fewer relationships than a detail endpoint.

---

## Best Practices

1. **Make all relationships LAZY**: Set `FetchType.LAZY` on every `@ManyToOne`, `@OneToOne`, `@OneToMany`, and `@ManyToMany`. Then selectively fetch what you need.

2. **Set a global default_batch_fetch_size**: Add `hibernate.default_batch_fetch_size=16` as a baseline optimization. This reduces N+1 to N/16+1 without any code changes.

3. **Use @EntityGraph for simple eager loading**: When you need department with employees, `@EntityGraph(attributePaths = {"department"})` is cleaner than writing JPQL.

4. **Use JOIN FETCH for complex queries**: When you need control over JOIN type, filtering, or multiple conditions on the joined entity.

5. **Use DTO projections when you do not need entities**: A `SELECT new EmployeeDto(e.name, d.name)` query avoids all lazy loading issues because there are no entities to lazy-load.

6. **Always enable SQL logging during development**: `logging.level.org.hibernate.SQL=DEBUG` makes N+1 immediately visible. Fix it before it reaches production.

7. **Match fetch plans to use cases**: Create different repository methods for different screens: `findListView()`, `findDetailView()`, `findForReport()`.

---

## Summary

In this chapter, you learned how to tame Hibernate's fetching behavior:

- **Lazy vs Eager**: Lazy loads on access, Eager loads immediately. Default to LAZY for everything.

- **N+1 problem**: Loading N entities triggers N additional queries for their relationships. The most common Hibernate performance issue.

- **JOIN FETCH**: Loads relationships in one query via SQL JOIN. Most efficient but requires JPQL and careful handling of DISTINCT and multiple collections.

- **@EntityGraph**: Declarative fetch plans on repository methods. Cleaner than JPQL for simple cases. Same performance as JOIN FETCH.

- **@BatchSize**: Batches lazy loads into IN(...) queries. Good global default (`hibernate.default_batch_fetch_size`). Reduces N+1 to ceil(N/batchSize)+1.

- **@Fetch(SUBSELECT)**: Loads all collections in one subquery. Always 2 queries total regardless of N.

- **LazyInitializationException**: Occurs when accessing lazy data outside the persistence context. Fix by loading data within `@Transactional`, using `@EntityGraph`/JOIN FETCH, or using DTO projections.

- **Different use cases need different fetch plans**. There is no universal "right" fetching strategy.

---

## Interview Questions

**Q1: What is the N+1 problem in Hibernate?**

The N+1 problem occurs when loading a list of N entities triggers N additional queries to load their lazy relationships. For example, loading 100 departments and accessing each department's employees generates 1 query for departments + 100 queries for employees = 101 total. It is the most common cause of poor Hibernate performance.

**Q2: What are the JPA default fetch types and why should you change them?**

`@ManyToOne` and `@OneToOne` default to `EAGER`. `@OneToMany` and `@ManyToMany` default to `LAZY`. The EAGER defaults on single-value associations cause N+1 problems when loading collections of entities. Best practice: set everything to `LAZY` and use `JOIN FETCH` or `@EntityGraph` for specific queries that need related data.

**Q3: What is the difference between JOIN FETCH and @EntityGraph?**

Both solve N+1 by loading relationships eagerly in a single query. `JOIN FETCH` is used in JPQL queries and gives full control over JOIN type and filtering. `@EntityGraph` is declarative (annotation-based), works with derived query methods, and is cleaner for simple cases. They produce similar SQL.

**Q4: How does @BatchSize reduce the N+1 problem?**

Instead of loading each lazy collection one at a time (`N` individual queries), `@BatchSize(size=10)` groups lazy loads into batches of 10 using `WHERE id IN (1,2,...,10)`. This reduces N+1 queries to `1 + ceil(N/batchSize)` queries. It is a good default optimization that works without changing queries.

**Q5: What causes MultipleBagFetchException and how do you fix it?**

It occurs when JOIN FETCHing two `List<>` collections simultaneously, which creates an ambiguous Cartesian product. Fixes: (1) change `List` to `Set` for the collections, (2) fetch collections in separate queries, (3) JOIN FETCH one and use `@BatchSize` on the other.

**Q6: What is LazyInitializationException and what is the correct fix?**

It occurs when accessing a lazy relationship after the persistence context is closed (transaction ended). The correct fix is to load all needed data within the `@Transactional` service method using `JOIN FETCH`, `@EntityGraph`, or DTO projections. Do NOT fix by making relationships EAGER or enabling OSIV.

---

## Practice Exercises

**Exercise 1: N+1 Detection**
Create `Department` and `Employee` entities with a lazy `@OneToMany`. Load all departments and access each department's employees. Enable SQL logging and count the queries. Verify it is N+1.

**Exercise 2: JOIN FETCH Fix**
Fix the N+1 from Exercise 1 using JOIN FETCH. Verify the query count drops to 1. Add DISTINCT and verify no duplicate departments.

**Exercise 3: @BatchSize Comparison**
Apply `@BatchSize(size = 5)` to the employees collection. With 20 departments, verify the query count is 1 + 4 = 5 (instead of 21). Then try the global `default_batch_fetch_size` property.

**Exercise 4: Multiple Collections**
Add a `@ManyToMany` `projects` collection to Department. Try to JOIN FETCH both `employees` and `projects`. Observe `MultipleBagFetchException`. Fix it using: (a) Set instead of List, (b) two separate queries.

**Exercise 5: Real-World Fetch Plans**
Create repository methods for three use cases: (a) list view with department name only, (b) detail view with department + projects, (c) report with just names and salaries (DTO). Verify each generates optimal SQL.

---

## What Is Next?

In the next chapter, we will explore **Cascade Operations and Lifecycle Propagation**. You will learn how cascade types control the propagation of persist, merge, remove, refresh, and detach operations through entity relationships, and how lifecycle callbacks (`@PrePersist`, `@PostUpdate`, etc.) let you hook into entity state changes.
