# Chapter 10: Criteria API — Type-Safe Dynamic Queries

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand why the Criteria API exists and when to use it
- Build queries programmatically using CriteriaBuilder and CriteriaQuery
- Use Root, Join, and Predicate to construct WHERE clauses
- Create dynamic queries with conditional predicates
- Use the JPA Metamodel for compile-time type safety
- Apply aggregate functions, grouping, and ordering with Criteria API
- Implement Spring Data Specifications for reusable query fragments
- Combine specifications with and/or logic for complex filtering

---

## Why the Criteria API?

JPQL and native SQL are **string-based**. You write the query as a string, and errors are caught only at runtime (or startup for JPQL). The Criteria API solves this by letting you build queries with Java code:

```
String-Based Queries (JPQL / SQL):
+------------------------------------------------------------------+
|  @Query("SELECT e FROM Employee e WHERE e.departmnt = :dept")     |
|                                              ^                    |
|                                              Typo!                |
|                                              Not caught until     |
|                                              runtime / startup    |
+------------------------------------------------------------------+

Criteria API (Programmatic):
+------------------------------------------------------------------+
|  cb.equal(root.get("departmnt"), dept)                            |
|                       ^                                           |
|                       Still a string - caught at runtime          |
|                                                                   |
|  cb.equal(root.get(Employee_.department), dept)                   |
|                       ^                                           |
|                       Metamodel field - caught at COMPILE TIME    |
+------------------------------------------------------------------+
```

But the biggest advantage is **dynamic queries**. Consider a search form:

```
Search Employees Form:
+------------------------------------------------------------------+
|  Name:       [____________]  (optional)                           |
|  Department: [____________]  (optional)                           |
|  Min Salary: [____________]  (optional)                           |
|  Active:     [ ] Yes  [ ] No  [ ] Either  (optional)             |
|                                                                   |
|  [Search]                                                         |
+------------------------------------------------------------------+
```

With JPQL, building this query dynamically is ugly:

```java
// JPQL approach: string concatenation nightmare
public List<Employee> search(String name, String dept,
                              BigDecimal minSalary, Boolean active) {
    StringBuilder jpql = new StringBuilder("SELECT e FROM Employee e WHERE 1=1");
    Map<String, Object> params = new HashMap<>();

    if (name != null) {
        jpql.append(" AND LOWER(e.name) LIKE :name");
        params.put("name", "%" + name.toLowerCase() + "%");
    }
    if (dept != null) {
        jpql.append(" AND e.department.name = :dept");
        params.put("dept", dept);
    }
    if (minSalary != null) {
        jpql.append(" AND e.salary >= :minSalary");
        params.put("minSalary", minSalary);
    }
    if (active != null) {
        jpql.append(" AND e.active = :active");
        params.put("active", active);
    }

    TypedQuery<Employee> query = em.createQuery(jpql.toString(), Employee.class);
    params.forEach(query::setParameter);
    return query.getResultList();
}
```

With the Criteria API, it is cleaner and type-safe:

```java
// Criteria API approach: programmatic and clean
public List<Employee> search(String name, String dept,
                              BigDecimal minSalary, Boolean active) {
    CriteriaBuilder cb = em.getCriteriaBuilder();
    CriteriaQuery<Employee> cq = cb.createQuery(Employee.class);
    Root<Employee> root = cq.from(Employee.class);

    List<Predicate> predicates = new ArrayList<>();

    if (name != null) {
        predicates.add(cb.like(cb.lower(root.get("name")),
                       "%" + name.toLowerCase() + "%"));
    }
    if (dept != null) {
        predicates.add(cb.equal(root.get("department").get("name"), dept));
    }
    if (minSalary != null) {
        predicates.add(cb.greaterThanOrEqualTo(root.get("salary"), minSalary));
    }
    if (active != null) {
        predicates.add(cb.equal(root.get("active"), active));
    }

    cq.select(root).where(predicates.toArray(new Predicate[0]));
    return em.createQuery(cq).getResultList();
}
```

---

## Criteria API Building Blocks

The Criteria API consists of four main components:

```
Criteria API Architecture:
+------------------------------------------------------------------+
|                                                                   |
|  CriteriaBuilder (cb)                                             |
|  +--------------------------+                                     |
|  | Factory for everything:  |                                     |
|  | - CriteriaQuery          |                                     |
|  | - Predicates (WHERE)     |                                     |
|  | - Expressions            |                                     |
|  | - Aggregates             |                                     |
|  | - Ordering               |                                     |
|  +--------------------------+                                     |
|           |                                                       |
|           v                                                       |
|  CriteriaQuery<T> (cq)                                           |
|  +--------------------------+                                     |
|  | Represents the query:    |                                     |
|  | - .select()              |                                     |
|  | - .where()               |                                     |
|  | - .orderBy()             |                                     |
|  | - .groupBy()             |                                     |
|  | - .having()              |                                     |
|  +--------------------------+                                     |
|           |                                                       |
|           v                                                       |
|  Root<T> (root)                                                   |
|  +--------------------------+                                     |
|  | Represents the FROM:     |                                     |
|  | - .get("fieldName")      |                                     |
|  | - .join("relationship")  |                                     |
|  | - .fetch("relationship") |                                     |
|  +--------------------------+                                     |
|           |                                                       |
|           v                                                       |
|  Predicate                                                        |
|  +--------------------------+                                     |
|  | Represents a condition:  |                                     |
|  | cb.equal(a, b)           |                                     |
|  | cb.like(a, pattern)      |                                     |
|  | cb.greaterThan(a, b)     |                                     |
|  | cb.and(p1, p2)           |                                     |
|  | cb.or(p1, p2)            |                                     |
|  +--------------------------+                                     |
|                                                                   |
+------------------------------------------------------------------+
```

### Step-by-Step: Building a Criteria Query

```java
// Step 1: Get CriteriaBuilder from EntityManager
CriteriaBuilder cb = entityManager.getCriteriaBuilder();

// Step 2: Create a CriteriaQuery for the result type
CriteriaQuery<Employee> cq = cb.createQuery(Employee.class);

// Step 3: Define the FROM clause (the root entity)
Root<Employee> root = cq.from(Employee.class);

// Step 4: Build predicates (WHERE conditions)
Predicate isActive = cb.equal(root.get("active"), true);
Predicate highSalary = cb.greaterThan(root.get("salary"), new BigDecimal("80000"));

// Step 5: Compose the query
cq.select(root)
  .where(cb.and(isActive, highSalary))
  .orderBy(cb.desc(root.get("salary")));

// Step 6: Execute
List<Employee> results = entityManager.createQuery(cq).getResultList();
```

```
This generates SQL equivalent to:
+------------------------------------------------------------------+
|  SELECT * FROM employees                                          |
|  WHERE active = true AND salary > 80000                           |
|  ORDER BY salary DESC                                             |
+------------------------------------------------------------------+
```

---

## CriteriaBuilder Methods Reference

### Comparison Predicates

```java
CriteriaBuilder cb = em.getCriteriaBuilder();
Root<Employee> root = cq.from(Employee.class);

// Equality
cb.equal(root.get("name"), "Alice")           // name = 'Alice'
cb.notEqual(root.get("active"), false)        // active != false

// Comparison
cb.greaterThan(root.get("salary"), 50000)     // salary > 50000
cb.greaterThanOrEqualTo(root.get("salary"), 50000)  // salary >= 50000
cb.lessThan(root.get("salary"), 100000)       // salary < 100000
cb.lessThanOrEqualTo(root.get("salary"), 100000)    // salary <= 100000
cb.between(root.get("salary"), 50000, 100000) // salary BETWEEN 50000 AND 100000

// String matching
cb.like(root.get("name"), "%Alice%")          // name LIKE '%Alice%'
cb.like(root.get("name"), "A%")               // name LIKE 'A%'
cb.notLike(root.get("name"), "%test%")        // name NOT LIKE '%test%'

// Null checks
cb.isNull(root.get("email"))                  // email IS NULL
cb.isNotNull(root.get("email"))               // email IS NOT NULL

// Collection
root.get("name").in("Alice", "Bob", "Charlie") // name IN ('Alice', 'Bob', 'Charlie')
cb.not(root.get("name").in("Alice", "Bob"))    // name NOT IN ('Alice', 'Bob')
```

### Logical Operators

```java
Predicate isActive = cb.equal(root.get("active"), true);
Predicate highSalary = cb.greaterThan(root.get("salary"), 80000);
Predicate inEngineering = cb.equal(root.get("department").get("name"), "Engineering");

// AND
cb.and(isActive, highSalary)                  // active = true AND salary > 80000
cb.and(isActive, highSalary, inEngineering)   // all three combined with AND

// OR
cb.or(highSalary, inEngineering)              // salary > 80000 OR dept = 'Engineering'

// NOT
cb.not(isActive)                              // NOT (active = true)

// Complex combinations
cb.and(
    isActive,
    cb.or(highSalary, inEngineering)
)
// active = true AND (salary > 80000 OR dept = 'Engineering')
```

```
Predicate Composition:
+------------------------------------------------------------------+
|                                                                   |
|  Simple:     cb.equal(root.get("active"), true)                   |
|              --> WHERE active = true                               |
|                                                                   |
|  AND:        cb.and(p1, p2)                                       |
|              --> WHERE active = true AND salary > 80000            |
|                                                                   |
|  OR:         cb.or(p1, p2)                                        |
|              --> WHERE active = true OR salary > 80000             |
|                                                                   |
|  Nested:     cb.and(p1, cb.or(p2, p3))                            |
|              --> WHERE active = true                               |
|                  AND (salary > 80000 OR dept = 'Engineering')      |
|                                                                   |
|  Array:      cb.and(predicates.toArray(new Predicate[0]))         |
|              --> WHERE p1 AND p2 AND p3 AND ...                    |
|              (perfect for dynamic queries!)                        |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Joins with Criteria API

### Basic Join

```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Employee> cq = cb.createQuery(Employee.class);
Root<Employee> employee = cq.from(Employee.class);

// INNER JOIN to department
Join<Employee, Department> department = employee.join("department");

// WHERE clause using the joined entity
cq.select(employee)
  .where(cb.equal(department.get("name"), "Engineering"));

// Generated SQL: SELECT e.* FROM employees e
//                JOIN departments d ON e.department_id = d.id
//                WHERE d.name = 'Engineering'
```

### Join Types

```java
// INNER JOIN (default)
Join<Employee, Department> dept = employee.join("department");
Join<Employee, Department> dept = employee.join("department", JoinType.INNER);

// LEFT JOIN
Join<Employee, Department> dept = employee.join("department", JoinType.LEFT);

// Multiple joins
Join<Employee, Department> dept = employee.join("department");
Join<Department, Company> company = dept.join("company");

cq.where(cb.equal(company.get("name"), "TechCorp"));
// SELECT e.* FROM employees e
// JOIN departments d ON e.department_id = d.id
// JOIN companies c ON d.company_id = c.id
// WHERE c.name = 'TechCorp'
```

```
Join Diagram:
+------------------------------------------------------------------+
|                                                                   |
|  Root<Employee> employee                                          |
|       |                                                           |
|       |-- .join("department") --> Join<Employee, Department>       |
|       |       |                                                   |
|       |       |-- .join("company") --> Join<Department, Company>   |
|       |                                                           |
|       |-- .join("projects") --> Join<Employee, Project>            |
|       |                                                           |
|       |-- .get("name") --> Path<String>  (for WHERE/SELECT)       |
|       |-- .get("salary") --> Path<BigDecimal>                     |
|                                                                   |
|  Each join produces a new root you can navigate further           |
+------------------------------------------------------------------+
```

### Fetch Joins (Solving N+1)

```java
// Fetch join — loads the relationship eagerly in the same query
Root<Employee> employee = cq.from(Employee.class);
employee.fetch("department", JoinType.LEFT);

// This prevents the N+1 problem:
// Instead of 1 query for employees + N queries for departments,
// it loads everything in a single query
```

---

## Aggregate Functions and Grouping

### Aggregate Functions

```java
CriteriaBuilder cb = em.getCriteriaBuilder();

// Count
CriteriaQuery<Long> countQuery = cb.createQuery(Long.class);
Root<Employee> root = countQuery.from(Employee.class);
countQuery.select(cb.count(root));
countQuery.where(cb.equal(root.get("active"), true));
Long count = em.createQuery(countQuery).getSingleResult();

// Sum
CriteriaQuery<BigDecimal> sumQuery = cb.createQuery(BigDecimal.class);
Root<Employee> sumRoot = sumQuery.from(Employee.class);
sumQuery.select(cb.sum(sumRoot.get("salary")));
BigDecimal totalSalary = em.createQuery(sumQuery).getSingleResult();

// Average
CriteriaQuery<Double> avgQuery = cb.createQuery(Double.class);
Root<Employee> avgRoot = avgQuery.from(Employee.class);
avgQuery.select(cb.avg(avgRoot.get("salary")));
Double avgSalary = em.createQuery(avgQuery).getSingleResult();

// Min / Max
CriteriaQuery<BigDecimal> maxQuery = cb.createQuery(BigDecimal.class);
Root<Employee> maxRoot = maxQuery.from(Employee.class);
maxQuery.select(cb.max(maxRoot.get("salary")));
BigDecimal maxSalary = em.createQuery(maxQuery).getSingleResult();
```

### GROUP BY and HAVING

```java
// Department salary report: average salary per department, only where avg > 70000
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Object[]> cq = cb.createQuery(Object[].class);
Root<Employee> employee = cq.from(Employee.class);
Join<Employee, Department> dept = employee.join("department");

cq.multiselect(
    dept.get("name"),                         // department name
    cb.count(employee),                       // employee count
    cb.avg(employee.get("salary")),           // average salary
    cb.sum(employee.get("salary"))            // total salary
);

cq.groupBy(dept.get("name"));
cq.having(cb.gt(cb.avg(employee.get("salary")), 70000));
cq.orderBy(cb.desc(cb.avg(employee.get("salary"))));

List<Object[]> results = em.createQuery(cq).getResultList();
for (Object[] row : results) {
    System.out.printf("Dept: %s, Count: %d, Avg: %.2f, Total: %s%n",
        row[0], row[1], row[2], row[3]);
}

// Generated SQL:
// SELECT d.name, COUNT(e.id), AVG(e.salary), SUM(e.salary)
// FROM employees e JOIN departments d ON e.department_id = d.id
// GROUP BY d.name
// HAVING AVG(e.salary) > 70000
// ORDER BY AVG(e.salary) DESC
```

---

## JPA Metamodel — Compile-Time Type Safety

String-based field names (`root.get("salary")`) can have typos. The JPA Metamodel generates static classes that provide compile-time checking.

### What the Metamodel Looks Like

For each entity class, a corresponding metamodel class is generated:

```
Entity Class:                        Generated Metamodel Class:
+-----------------------------+      +-----------------------------+
| @Entity                     |      | @StaticMetamodel(           |
| public class Employee {     |      |   Employee.class)           |
|   @Id                       |      | public abstract class       |
|   private Long id;          | ---> |   Employee_ {               |
|   private String name;      |      |   static volatile           |
|   private BigDecimal salary;|      |     SingularAttribute       |
|   private boolean active;   |      |       <Employee, Long> id;  |
|   private Department dept;  |      |   static volatile           |
| }                           |      |     SingularAttribute       |
+-----------------------------+      |       <Employee, String>    |
                                     |       name;                 |
                                     |   static volatile           |
                                     |     SingularAttribute       |
                                     |       <Employee, BigDecimal>|
                                     |       salary;               |
                                     |   // ... more fields        |
                                     | }                           |
                                     +-----------------------------+
```

### Setting Up Metamodel Generation

Add the Hibernate JPA Metamodel Generator to your `pom.xml`:

```xml
<dependency>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-jpamodelgen</artifactId>
    <scope>provided</scope>
</dependency>
```

Spring Boot's dependency management handles the version. The `provided` scope means it is only needed during compilation, not at runtime.

After adding this dependency and building (`mvn compile`), you will find generated classes like `Employee_` in your `target/generated-sources` directory.

### Using the Metamodel

```java
// Without metamodel (string-based, error-prone):
root.get("salary")            // typo in "salary" only caught at runtime
root.get("department")        // type unknown to compiler

// With metamodel (type-safe, compile-time checked):
root.get(Employee_.salary)    // compiler verifies "salary" exists and is BigDecimal
root.get(Employee_.department) // compiler knows this is a Department
```

Full example:

```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Employee> cq = cb.createQuery(Employee.class);
Root<Employee> root = cq.from(Employee.class);

// All field references are compile-time checked
cq.select(root)
  .where(cb.and(
      cb.equal(root.get(Employee_.active), true),
      cb.greaterThan(root.get(Employee_.salary), new BigDecimal("80000")),
      cb.like(root.get(Employee_.name), "%Alice%")
  ))
  .orderBy(cb.desc(root.get(Employee_.salary)));

List<Employee> results = em.createQuery(cq).getResultList();
```

If you rename `salary` to `compensation` in the `Employee` entity, `Employee_.salary` immediately causes a compilation error, telling you exactly where to update.

---

## Spring Data Specifications

The Criteria API is powerful but verbose. **Spring Data Specifications** provide a cleaner interface by wrapping Criteria API predicates into reusable, composable objects.

### The Specification Interface

```java
// JPA Standard (what Spring wraps)
public interface Specification<T> extends Serializable {
    Predicate toPredicate(Root<T> root,
                          CriteriaQuery<?> query,
                          CriteriaBuilder criteriaBuilder);
}
```

```
How Specifications Work:
+------------------------------------------------------------------+
|                                                                   |
|  Specification<Employee>                                          |
|  +----------------------------+                                   |
|  | toPredicate(root, cq, cb)  |                                   |
|  | {                          |                                   |
|  |   return cb.equal(         |----> Returns ONE Predicate        |
|  |     root.get("active"),    |                                   |
|  |     true);                 |                                   |
|  | }                          |                                   |
|  +----------------------------+                                   |
|                                                                   |
|  Multiple Specifications can be combined:                         |
|  spec1.and(spec2).and(spec3)  ----> AND chain of predicates       |
|  spec1.or(spec2)              ----> OR combination                |
|                                                                   |
|  Repository uses them:                                            |
|  repository.findAll(spec)     ----> Executes with combined WHERE  |
|  repository.findAll(spec, pageable) ----> With pagination         |
+------------------------------------------------------------------+
```

### Setting Up: Extend JpaSpecificationExecutor

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long>,
                                            JpaSpecificationExecutor<Employee> {
    // JpaSpecificationExecutor adds:
    // List<T> findAll(Specification<T> spec)
    // Page<T> findAll(Specification<T> spec, Pageable pageable)
    // long count(Specification<T> spec)
    // boolean exists(Specification<T> spec)
    // Optional<T> findOne(Specification<T> spec)
}
```

### Creating Specifications

```java
public class EmployeeSpecifications {

    public static Specification<Employee> isActive() {
        return (root, query, cb) -> cb.equal(root.get("active"), true);
    }

    public static Specification<Employee> hasName(String name) {
        return (root, query, cb) ->
            cb.like(cb.lower(root.get("name")),
                    "%" + name.toLowerCase() + "%");
    }

    public static Specification<Employee> inDepartment(String deptName) {
        return (root, query, cb) ->
            cb.equal(root.get("department").get("name"), deptName);
    }

    public static Specification<Employee> salaryGreaterThan(BigDecimal min) {
        return (root, query, cb) ->
            cb.greaterThan(root.get("salary"), min);
    }

    public static Specification<Employee> salaryBetween(BigDecimal min,
                                                         BigDecimal max) {
        return (root, query, cb) -> cb.between(root.get("salary"), min, max);
    }

    public static Specification<Employee> hiredAfter(LocalDate date) {
        return (root, query, cb) ->
            cb.greaterThan(root.get("hireDate"), date);
    }

    public static Specification<Employee> hiredInYear(int year) {
        return (root, query, cb) -> {
            LocalDate start = LocalDate.of(year, 1, 1);
            LocalDate end = LocalDate.of(year, 12, 31);
            return cb.between(root.get("hireDate"), start, end);
        };
    }
}
```

### Combining Specifications

```java
// Import static for cleaner code
import static com.example.spec.EmployeeSpecifications.*;

// Simple usage
List<Employee> activeEmployees = repository.findAll(isActive());

// Combine with AND
List<Employee> activeEngineers = repository.findAll(
    isActive().and(inDepartment("Engineering"))
);

// Combine with AND and OR
Specification<Employee> spec = isActive()
    .and(salaryGreaterThan(new BigDecimal("70000")))
    .and(inDepartment("Engineering").or(inDepartment("Product")));

List<Employee> results = repository.findAll(spec);

// With pagination
Page<Employee> page = repository.findAll(spec, PageRequest.of(0, 20));
```

```
Specification Composition:
+------------------------------------------------------------------+
|                                                                   |
|  isActive()                                                       |
|      .and(salaryGreaterThan(70000))                               |
|      .and(inDepartment("Engineering").or(inDepartment("Product")))|
|                                                                   |
|  Generates:                                                       |
|  WHERE active = true                                              |
|    AND salary > 70000                                             |
|    AND (department.name = 'Engineering'                           |
|         OR department.name = 'Product')                           |
+------------------------------------------------------------------+
```

---

## Dynamic Search with Specifications

This is where Specifications truly shine — building queries from user input:

```java
@Service
public class EmployeeSearchService {

    private final EmployeeRepository repository;

    public EmployeeSearchService(EmployeeRepository repository) {
        this.repository = repository;
    }

    public Page<Employee> search(EmployeeSearchCriteria criteria, Pageable pageable) {

        Specification<Employee> spec = Specification.where(null); // start with no filter

        if (criteria.getName() != null && !criteria.getName().isBlank()) {
            spec = spec.and(EmployeeSpecifications.hasName(criteria.getName()));
        }

        if (criteria.getDepartment() != null) {
            spec = spec.and(EmployeeSpecifications.inDepartment(criteria.getDepartment()));
        }

        if (criteria.getMinSalary() != null) {
            spec = spec.and(EmployeeSpecifications.salaryGreaterThan(criteria.getMinSalary()));
        }

        if (criteria.getMaxSalary() != null) {
            spec = spec.and(EmployeeSpecifications.salaryLessThan(criteria.getMaxSalary()));
        }

        if (criteria.getActiveOnly() != null && criteria.getActiveOnly()) {
            spec = spec.and(EmployeeSpecifications.isActive());
        }

        if (criteria.getHiredAfter() != null) {
            spec = spec.and(EmployeeSpecifications.hiredAfter(criteria.getHiredAfter()));
        }

        return repository.findAll(spec, pageable);
    }
}
```

```java
// The search criteria DTO
public class EmployeeSearchCriteria {
    private String name;
    private String department;
    private BigDecimal minSalary;
    private BigDecimal maxSalary;
    private Boolean activeOnly;
    private LocalDate hiredAfter;

    // getters and setters
}
```

```java
// Controller usage
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    private final EmployeeSearchService searchService;

    @GetMapping("/search")
    public Page<Employee> search(
            @RequestParam(required = false) String name,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) BigDecimal minSalary,
            @RequestParam(required = false) BigDecimal maxSalary,
            @RequestParam(required = false) Boolean activeOnly,
            @RequestParam(required = false) LocalDate hiredAfter,
            Pageable pageable) {

        EmployeeSearchCriteria criteria = new EmployeeSearchCriteria();
        criteria.setName(name);
        criteria.setDepartment(department);
        criteria.setMinSalary(minSalary);
        criteria.setMaxSalary(maxSalary);
        criteria.setActiveOnly(activeOnly);
        criteria.setHiredAfter(hiredAfter);

        return searchService.search(criteria, pageable);
    }
}
```

```
Dynamic Query Building Flow:
+------------------------------------------------------------------+
|                                                                   |
|  User request: /api/employees/search?name=Ali&minSalary=60000    |
|                                                                   |
|  Step 1: Start with empty spec (WHERE true)                       |
|                                                                   |
|  Step 2: name="Ali" is present                                   |
|          --> spec AND hasName("Ali")                              |
|          WHERE LOWER(name) LIKE '%ali%'                           |
|                                                                   |
|  Step 3: department=null, skip                                    |
|                                                                   |
|  Step 4: minSalary=60000 is present                              |
|          --> spec AND salaryGreaterThan(60000)                    |
|          WHERE LOWER(name) LIKE '%ali%' AND salary > 60000        |
|                                                                   |
|  Step 5: Execute with pagination                                  |
|          repository.findAll(spec, pageable)                       |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Specifications with Joins

When you need to filter by related entities:

```java
public class EmployeeSpecifications {

    // Join to department and filter by department name
    public static Specification<Employee> inDepartment(String deptName) {
        return (root, query, cb) -> {
            Join<Employee, Department> dept = root.join("department");
            return cb.equal(dept.get("name"), deptName);
        };
    }

    // Join to projects (many-to-many) and filter
    public static Specification<Employee> onProject(String projectName) {
        return (root, query, cb) -> {
            Join<Employee, Project> projects = root.join("projects");
            return cb.equal(projects.get("name"), projectName);
        };
    }

    // Avoid duplicate results with distinct
    public static Specification<Employee> onProjectDistinct(String projectName) {
        return (root, query, cb) -> {
            query.distinct(true);  // Prevent duplicates from joins
            Join<Employee, Project> projects = root.join("projects");
            return cb.equal(projects.get("name"), projectName);
        };
    }
}
```

---

## Criteria API vs JPQL vs Native SQL

```
+------------------------------------------------------------------+
| Feature          | Derived    | JPQL      | Criteria  | Native   |
|                  | Methods    |           | API/Spec  | SQL      |
|------------------------------------------------------------------|
| Syntax           | Method     | String    | Java API  | String   |
|                  | names      |           |           |          |
| Type safety      | High       | Low       | High      | None     |
|                  |            |           | (w/meta)  |          |
| Dynamic queries  | No         | Ugly      | Elegant   | Ugly     |
| Reusable pieces  | No         | No        | Yes       | No       |
|                  |            |           | (specs)   |          |
| Readability      | Excellent  | Good      | Verbose   | Good     |
|                  | (simple)   |           |           |          |
| DB portability   | Yes        | Yes       | Yes       | No       |
| Complex queries  | Very       | Good      | Good      | Full     |
|                  | limited    |           |           | power    |
| Learning curve   | Easy       | Medium    | Steep     | Medium   |
|                  |            |           |           |          |
| Best for         | Simple     | Fixed     | Dynamic   | DB-      |
|                  | lookups    | queries   | filters   | specific |
|                  |            |           | & search  | features |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Using string field names instead of metamodel**: `root.get("salary")` works but is error-prone. Use `root.get(Employee_.salary)` with the JPA Metamodel for compile-time safety.

2. **Forgetting distinct with joins**: Joining a collection (`@OneToMany`, `@ManyToMany`) can produce duplicate root entities. Add `query.distinct(true)` in your specification.

3. **Creating new joins in each specification**: If two specifications both join the same relationship, you get two joins in the SQL. Extract the join into a shared specification or check if the join already exists.

4. **Not using Specification.where(null) for empty start**: When building dynamic specs, start with `Specification.where(null)` so `.and()` chains work even when all filters are null.

5. **Overusing Criteria API for simple queries**: For straightforward queries, derived methods or JPQL are simpler and more readable. Reserve Criteria API for dynamic filtering scenarios.

6. **Forgetting to extend JpaSpecificationExecutor**: Specifications only work if your repository extends `JpaSpecificationExecutor<T>` in addition to `JpaRepository<T, ID>`.

---

## Best Practices

1. **Use Specifications for search/filter endpoints**: Any endpoint where users can optionally filter by multiple fields is a perfect use case for Specifications.

2. **Group specifications in a dedicated class**: Create `EmployeeSpecifications`, `OrderSpecifications`, etc. This keeps them organized and reusable.

3. **Enable the JPA Metamodel**: The `hibernate-jpamodelgen` dependency is lightweight and catches field name errors at compile time instead of runtime.

4. **Combine with pagination**: Specifications work seamlessly with `Pageable`. Always return `Page<T>` for search endpoints.

5. **Keep specifications focused**: Each specification should represent one filter condition. Complex logic comes from combining simple specifications, not from writing one giant specification.

6. **Use the right tool for the job**: Derived methods for simple lookups, JPQL for fixed queries with joins, Specifications for dynamic search, native SQL for database-specific features.

---

## Summary

In this chapter, you learned how to build type-safe, dynamic queries:

- **Criteria API** lets you build queries programmatically using `CriteriaBuilder`, `CriteriaQuery`, `Root`, and `Predicate`. It eliminates string-based query errors.

- **The main components**: `CriteriaBuilder` creates predicates and expressions, `CriteriaQuery` represents the query structure, `Root` defines the FROM entity, and `Predicate` defines WHERE conditions.

- **JPA Metamodel** (`Employee_`) provides compile-time type safety by generating static field references from your entity classes.

- **Spring Data Specifications** wrap the Criteria API in a clean, composable interface. Each specification is a single predicate that can be combined with `.and()` and `.or()`.

- **Dynamic search** is the primary use case — building queries from optional user-provided filter criteria without ugly string concatenation.

- **Joins in Criteria API** use `root.join("relationship")` and `root.fetch("relationship")` for eager loading.

---

## Interview Questions

**Q1: What is the main advantage of the Criteria API over JPQL?**

The Criteria API excels at dynamic query construction. When a query's conditions depend on user input (optional filters in a search form), the Criteria API builds the query programmatically without string concatenation. Combined with the JPA Metamodel, it also provides compile-time type safety.

**Q2: What is a Spring Data Specification?**

A Specification is an implementation of the `Specification<T>` interface that encapsulates a single query predicate. It takes a `Root`, `CriteriaQuery`, and `CriteriaBuilder` and returns a `Predicate`. Specifications can be combined using `.and()` and `.or()` to create complex queries from simple, reusable pieces.

**Q3: What is the JPA Metamodel and why should you use it?**

The JPA Metamodel generates static classes (like `Employee_`) that contain typed references to entity fields. Instead of `root.get("salary")` (where a typo only fails at runtime), you use `root.get(Employee_.salary)` which fails at compile time if the field does not exist or the type is wrong.

**Q4: How do you handle optional search criteria with Specifications?**

Start with `Specification.where(null)` as a base. For each non-null criterion, chain with `.and(someSpec)`. Null specifications are ignored, so only provided criteria are added to the query. This avoids `if-else` chains building JPQL strings.

**Q5: What is JpaSpecificationExecutor?**

It is a Spring Data interface that your repository must extend to use Specifications. It adds methods like `findAll(Specification<T>)`, `findAll(Specification<T>, Pageable)`, `count(Specification<T>)`, and `exists(Specification<T>)`.

**Q6: When would you use the Criteria API vs JPQL?**

Use Criteria API (via Specifications) for dynamic queries with optional filters, search endpoints, and when type safety is important. Use JPQL for fixed queries with known structure, especially when readability matters more than dynamism.

---

## Practice Exercises

**Exercise 1: Basic Criteria Query**
Write a Criteria API query that finds all employees with salary between two values, ordered by salary descending. Execute it using EntityManager.

**Exercise 2: Specification Factory**
Create a `ProductSpecifications` class for a `Product` entity with fields (name, category, price, inStock). Write specifications for: `hasCategory`, `priceBetween`, `isInStock`, `nameContains`. Test combining them.

**Exercise 3: Dynamic Product Search**
Build a `ProductSearchService` that accepts an optional name, category, min price, max price, and inStock flag. Use Specifications to build the query dynamically. Return paginated results.

**Exercise 4: Metamodel Setup**
Add the `hibernate-jpamodelgen` dependency to a project and refactor string-based Criteria queries to use the generated metamodel classes. Verify that renaming a field causes a compile error.

**Exercise 5: Complex Specification**
Write a specification that finds employees who are either (a) in the "Engineering" department with salary above 90,000 or (b) in the "Sales" department with salary above 70,000, and who were hired in the last 2 years. Combine at least 3 specifications.

---

## What Is Next?

In the next chapter, we will explore **Pagination, Sorting, and Query Optimization**. You will learn how to efficiently return subsets of data with `Pageable`, `Page`, and `Slice`, sort by multiple fields, write custom count queries, and use `@EntityGraph` to control fetching at the query level — essential skills for building performant APIs.
