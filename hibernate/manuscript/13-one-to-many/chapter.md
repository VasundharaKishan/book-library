# Chapter 13: One-to-Many and Many-to-One Relationships

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand one-to-many and many-to-one relationships and how they relate
- Map @ManyToOne (the owning side) with @JoinColumn
- Map @OneToMany (the inverse side) with mappedBy
- Write bidirectional helper methods to keep both sides synchronized
- Choose between unidirectional and bidirectional mappings
- Use orphanRemoval to auto-delete detached children
- Avoid the unidirectional @OneToMany without @JoinColumn anti-pattern
- Handle cascading correctly in parent-child relationships
- Query across one-to-many relationships with JPQL and derived methods

---

## Understanding One-to-Many Relationships

One-to-many is the most common relationship type in database modeling. One parent entity owns a collection of child entities.

```
One-to-Many Examples:
+------------------------------------------------------------------+
|                                                                   |
|  Department  ----< Employee      (One dept has many employees)    |
|  Author      ----< Book          (One author writes many books)   |
|  Order       ----< OrderItem     (One order has many line items)  |
|  Post        ----< Comment       (One post has many comments)     |
|  Customer    ----< Invoice       (One customer has many invoices) |
|  Category    ----< Product       (One category has many products) |
|                                                                   |
|  Legend:  ----<  means "has many"                                 |
+------------------------------------------------------------------+
```

### Two Sides of the Same Coin

One-to-many and many-to-one are the **same relationship** seen from different sides:

```
Same Relationship, Different Perspectives:
+------------------------------------------------------------------+
|                                                                   |
|  From Department's perspective:                                   |
|  "A Department has MANY Employees"    --> @OneToMany              |
|                                                                   |
|  From Employee's perspective:                                     |
|  "An Employee belongs to ONE Department"  --> @ManyToOne          |
|                                                                   |
|  Department (1) -------- (*) Employee                             |
|       |                        |                                  |
|       |  @OneToMany             |  @ManyToOne                     |
|       |  List<Employee>         |  Department department           |
|       |  (collection side)      |  (single-value side)            |
|       |  (inverse side)         |  (owning side)                  |
|                                                                   |
|  In the DATABASE, the FK is always on the "many" side:            |
|  employees table has department_id (FK)                           |
|  departments table does NOT have employee columns                 |
+------------------------------------------------------------------+
```

### Database Schema

```
Database Tables:
+------------------------------------------------------------------+
|                                                                   |
|  departments                      employees                       |
|  +--------+-----------+          +--------+--------+----------+   |
|  | id(PK) | name      |          | id(PK) | name   | dept_id  |   |
|  |--------+-----------|          |--------+--------+----------|   |
|  | 1      | Engineering|<---+    | 10     | Alice  | 1 (FK)   |   |
|  | 2      | Marketing |<---|-+  | 11     | Bob    | 1 (FK)   |   |
|  | 3      | Sales     |    | |  | 12     | Carol  | 2 (FK)   |   |
|  +--------+-----------+    | |  | 13     | Dave   | 2 (FK)   |   |
|                             | |  | 14     | Eve    | 1 (FK)   |   |
|                             | |  +--------+--------+----------+   |
|                             | |                                   |
|  The FK is on the "many" side (employees table)                   |
|  NOT on the "one" side (departments table)                        |
|  This is always the case for one-to-many / many-to-one            |
+------------------------------------------------------------------+
```

---

## @ManyToOne — The Owning Side

Start with `@ManyToOne` because it is simpler and more important. The "many" side always owns the relationship because that is where the foreign key lives.

```java
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @ManyToOne(fetch = FetchType.LAZY)        // JPA standard
    @JoinColumn(name = "department_id")        // JPA standard — FK column
    private Department department;

    protected Employee() {}

    public Employee(String name, String email) {
        this.name = name;
        this.email = email;
    }

    // Getters and setters
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public Department getDepartment() { return department; }
    public void setDepartment(Department department) {
        this.department = department;
    }
}
```

```
@ManyToOne Annotation Breakdown:
+------------------------------------------------------------------+
|                                                                   |
|  @ManyToOne(                                                      |
|      fetch = FetchType.LAZY  // Override default EAGER             |
|  )                           // Loads department only when         |
|                              // employee.getDepartment() is called |
|                                                                   |
|  @JoinColumn(                                                     |
|      name = "department_id"  // Column name in employees table    |
|  )                           // FK referencing departments.id     |
|                                                                   |
|  Default fetch: EAGER (loads department with every employee!)     |
|  Best practice: Always set FetchType.LAZY on @ManyToOne           |
|                                                                   |
|  Generated DDL:                                                   |
|  ALTER TABLE employees ADD COLUMN department_id BIGINT;           |
|  ALTER TABLE employees ADD FOREIGN KEY (department_id)            |
|      REFERENCES departments(id);                                  |
+------------------------------------------------------------------+
```

### Using @ManyToOne Alone (Unidirectional)

You can use `@ManyToOne` without a corresponding `@OneToMany`. This is called **unidirectional many-to-one**:

```java
// Employee knows its department
Employee employee = new Employee("Alice", "alice@co.com");
employee.setDepartment(engineeringDept);
employeeRepository.save(employee);

// Query employees by department
List<Employee> engineers = employeeRepository.findByDepartmentName("Engineering");

// Navigate from employee to department
String deptName = employee.getDepartment().getName();
```

This is perfectly valid and often sufficient. You only need `@OneToMany` on the Department side if you want to navigate from a department to its employees using `department.getEmployees()`.

---

## @OneToMany with mappedBy — The Inverse Side

Add `@OneToMany` to the parent entity when you need collection navigation:

```java
@Entity
@Table(name = "departments")
public class Department {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @OneToMany(mappedBy = "department",       // Field name in Employee
               cascade = CascadeType.ALL,     // Cascade operations to children
               orphanRemoval = true)          // Delete children removed from list
    private List<Employee> employees = new ArrayList<>();

    protected Department() {}

    public Department(String name) {
        this.name = name;
    }

    // ===== Bidirectional Helper Methods =====

    public void addEmployee(Employee employee) {
        employees.add(employee);
        employee.setDepartment(this);   // Set the owning side!
    }

    public void removeEmployee(Employee employee) {
        employees.remove(employee);
        employee.setDepartment(null);   // Clear the owning side!
    }

    // Getters
    public Long getId() { return id; }
    public String getName() { return name; }
    public List<Employee> getEmployees() {
        return Collections.unmodifiableList(employees);
    }
}
```

```
Bidirectional Mapping:
+------------------------------------------------------------------+
|                                                                   |
|  Department                       Employee                        |
|  +-------------------------+     +-------------------------+      |
|  | @OneToMany(             |     | @ManyToOne(             |      |
|  |   mappedBy="department",|     |   fetch=LAZY)           |      |
|  |   cascade=ALL,          |     | @JoinColumn(            |      |
|  |   orphanRemoval=true)   |     |   name="department_id") |      |
|  | List<Employee> employees|---->| Department department   |      |
|  +-------------------------+     +-------------------------+      |
|  INVERSE side                    OWNING side                      |
|  (no FK column)                  (has FK column)                  |
|  (mappedBy points to the         (JoinColumn defines              |
|   field on the owning side)       the FK column name)             |
|                                                                   |
|  RULE: mappedBy = "department"                                    |
|  means: "look at the 'department' field in Employee               |
|          to find the FK mapping"                                  |
+------------------------------------------------------------------+
```

---

## Why Helper Methods Are Critical

Without helper methods, it is easy to create inconsistent state:

```
Without Helper Methods — What Goes Wrong:
+------------------------------------------------------------------+
|                                                                   |
|  // WRONG: Only setting the collection side                       |
|  department.getEmployees().add(employee);                         |
|  // In-memory: department knows about employee                    |
|  // But employee.department is still null!                        |
|  // Database: department_id is NOT set (owning side not updated)  |
|                                                                   |
|  // WRONG: Only setting the @ManyToOne side                       |
|  employee.setDepartment(department);                              |
|  // In-memory: employee knows its department                      |
|  // But department.employees does not contain this employee!      |
|  // Database: FK IS set (owning side was updated)                 |
|  // But the in-memory collection is out of sync                   |
|                                                                   |
|  // CORRECT: Helper method sets BOTH sides                        |
|  department.addEmployee(employee);                                |
|  // In-memory: both sides are synchronized                        |
|  // Database: FK is correctly set                                 |
+------------------------------------------------------------------+
```

```java
// The helper methods in Department:

public void addEmployee(Employee employee) {
    employees.add(employee);          // Update the collection
    employee.setDepartment(this);     // Update the owning side (sets FK)
}

public void removeEmployee(Employee employee) {
    employees.remove(employee);       // Remove from collection
    employee.setDepartment(null);     // Clear the owning side (clears FK)
}
```

---

## Saving and Loading Parent-Child Data

### Creating a Department with Employees

```java
@Service
@Transactional
public class DepartmentService {

    private final DepartmentRepository departmentRepository;

    public DepartmentService(DepartmentRepository departmentRepository) {
        this.departmentRepository = departmentRepository;
    }

    public Department createDepartmentWithEmployees() {
        Department dept = new Department("Engineering");

        // Use helper methods — cascade persists the employees
        dept.addEmployee(new Employee("Alice", "alice@co.com"));
        dept.addEmployee(new Employee("Bob", "bob@co.com"));
        dept.addEmployee(new Employee("Carol", "carol@co.com"));

        return departmentRepository.save(dept);
        // ONE save call persists department AND all 3 employees
    }
}
```

```
Cascade Persist Flow:
+------------------------------------------------------------------+
|                                                                   |
|  departmentRepository.save(dept)                                  |
|       |                                                           |
|       v                                                           |
|  1. INSERT INTO departments (name) VALUES ('Engineering')         |
|     --> Generated id = 1                                          |
|                                                                   |
|  2. CascadeType.ALL propagates PERSIST to children:               |
|     INSERT INTO employees (name, email, department_id)            |
|     VALUES ('Alice', 'alice@co.com', 1)                           |
|                                                                   |
|     INSERT INTO employees (name, email, department_id)            |
|     VALUES ('Bob', 'bob@co.com', 1)                               |
|                                                                   |
|     INSERT INTO employees (name, email, department_id)            |
|     VALUES ('Carol', 'carol@co.com', 1)                           |
|                                                                   |
|  Result: 4 INSERT statements from 1 save() call                  |
+------------------------------------------------------------------+
```

### Loading and Navigating

```java
// Load department — employees are LAZY by default
Department dept = departmentRepository.findById(1L).orElseThrow();
// SQL: SELECT * FROM departments WHERE id = 1

// Access employees — triggers lazy loading
List<Employee> employees = dept.getEmployees();
// SQL: SELECT * FROM employees WHERE department_id = 1

// Load with employees eagerly (avoid N+1)
@Query("SELECT d FROM Department d LEFT JOIN FETCH d.employees WHERE d.id = :id")
Optional<Department> findByIdWithEmployees(@Param("id") Long id);
// SQL: SELECT d.*, e.* FROM departments d
//      LEFT JOIN employees e ON d.id = e.department_id WHERE d.id = 1
```

### Adding and Removing Children

```java
@Transactional
public void addEmployeeToDepartment(Long deptId, String name, String email) {
    Department dept = departmentRepository.findById(deptId).orElseThrow();
    dept.addEmployee(new Employee(name, email));
    // Cascade persists the new employee. No explicit save needed.
}

@Transactional
public void removeEmployeeFromDepartment(Long deptId, Long employeeId) {
    Department dept = departmentRepository.findByIdWithEmployees(deptId)
        .orElseThrow();

    dept.getEmployees().stream()
        .filter(e -> e.getId().equals(employeeId))
        .findFirst()
        .ifPresent(dept::removeEmployee);
    // orphanRemoval deletes the employee from the database
}

@Transactional
public void transferEmployee(Long fromDeptId, Long toDeptId, Long employeeId) {
    Department fromDept = departmentRepository.findByIdWithEmployees(fromDeptId)
        .orElseThrow();
    Department toDept = departmentRepository.findById(toDeptId).orElseThrow();

    Employee employee = fromDept.getEmployees().stream()
        .filter(e -> e.getId().equals(employeeId))
        .findFirst()
        .orElseThrow();

    fromDept.removeEmployee(employee);  // Removes from old department
    toDept.addEmployee(employee);       // Adds to new department
    // FK updated automatically (owning side changed)
}
```

```
Transfer Employee Flow:
+------------------------------------------------------------------+
|                                                                   |
|  Before:                                                          |
|  Engineering [Alice, Bob, Carol]    Marketing [Dave]              |
|                                                                   |
|  transferEmployee(engId, mktId, bobId)                            |
|                                                                   |
|  1. fromDept.removeEmployee(bob)                                  |
|     - Engineering.employees: [Alice, Carol]                       |
|     - bob.department = null                                       |
|                                                                   |
|  2. toDept.addEmployee(bob)                                       |
|     - Marketing.employees: [Dave, Bob]                            |
|     - bob.department = Marketing                                  |
|                                                                   |
|  3. Hibernate flushes:                                            |
|     UPDATE employees SET department_id = 2 WHERE id = 11          |
|     (Bob's FK changes from Engineering to Marketing)              |
|                                                                   |
|  After:                                                           |
|  Engineering [Alice, Carol]    Marketing [Dave, Bob]              |
+------------------------------------------------------------------+
```

---

## The Unidirectional @OneToMany Anti-Pattern

A unidirectional `@OneToMany` (without `mappedBy`, without a corresponding `@ManyToOne`) should be avoided. It causes Hibernate to create an extra join table:

```
Anti-Pattern: Unidirectional @OneToMany
+------------------------------------------------------------------+
|                                                                   |
|  @Entity                                                          |
|  public class Department {                                        |
|      @OneToMany        // NO mappedBy, NO @JoinColumn             |
|      private List<Employee> employees;                            |
|  }                                                                |
|                                                                   |
|  @Entity                                                          |
|  public class Employee {                                          |
|      // NO @ManyToOne field!                                      |
|  }                                                                |
|                                                                   |
|  Hibernate creates THREE tables:                                  |
|  +-------------+    +---------------------+    +-------------+    |
|  | departments |    | departments_employees|    | employees   |    |
|  | id | name   |    | dept_id | emp_id    |    | id | name   |    |
|  +-------------+    +---------------------+    +-------------+    |
|                                                                   |
|  Problems:                                                        |
|  - Extra join table (unnecessary for one-to-many)                 |
|  - Extra JOINs in every query                                     |
|  - INSERT and DELETE operations are more complex                  |
|  - Hibernate deletes ALL rows in join table then re-inserts       |
|    when the collection changes (terrible performance!)            |
+------------------------------------------------------------------+
```

### The Fix

If you truly need a unidirectional `@OneToMany` (the child does not have a `@ManyToOne` reference), use `@JoinColumn` to specify the FK column directly:

```java
// Acceptable: Unidirectional @OneToMany WITH @JoinColumn
@Entity
public class Department {

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "department_id")  // FK column in employees table
    private List<Employee> employees = new ArrayList<>();
}
```

But the **best practice** is still to use a bidirectional mapping:

```
Recommended Approaches (best to worst):
+------------------------------------------------------------------+
|                                                                   |
|  1. Bidirectional @ManyToOne + @OneToMany(mappedBy)   BEST        |
|     - Most efficient SQL                                          |
|     - Navigate both directions                                    |
|     - FK managed by @ManyToOne side                               |
|                                                                   |
|  2. @ManyToOne only (no @OneToMany)                   GOOD        |
|     - Simplest mapping                                            |
|     - Use JPQL joins when you need the collection                 |
|     - Avoids collection management complexity                     |
|                                                                   |
|  3. Unidirectional @OneToMany WITH @JoinColumn        OK          |
|     - Works but generates extra UPDATE statements                 |
|     - INSERT employee, then UPDATE employee set FK                |
|                                                                   |
|  4. Unidirectional @OneToMany without @JoinColumn     AVOID!      |
|     - Creates unnecessary join table                              |
|     - Terrible performance on collection changes                  |
+------------------------------------------------------------------+
```

---

## Cascade and orphanRemoval in Depth

### CascadeType Options

```java
@OneToMany(mappedBy = "department",
           cascade = CascadeType.ALL,     // Shortcut for all types below
           orphanRemoval = true)
private List<Employee> employees;
```

```
Cascade Types Explained:
+------------------------------------------------------------------+
|                                                                   |
|  CascadeType      When It Fires         What It Does              |
|  ----------------------------------------------------------------|
|  PERSIST           save(parent)          Also save new children   |
|                                                                   |
|  MERGE             merge(parent)         Also merge children      |
|                    (reattach detached)                             |
|                                                                   |
|  REMOVE            delete(parent)        Also delete children     |
|                                                                   |
|  REFRESH           refresh(parent)       Also refresh children    |
|                    (reload from DB)                               |
|                                                                   |
|  DETACH            detach(parent)        Also detach children     |
|                    (remove from context)                          |
|                                                                   |
|  ALL               All of the above      Everything cascades      |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  orphanRemoval = true:                                            |
|  When a child is REMOVED from the collection (but the parent     |
|  is NOT deleted), delete the orphaned child.                      |
|                                                                   |
|  Example:                                                         |
|  dept.removeEmployee(bob);                                        |
|  // orphanRemoval: DELETE FROM employees WHERE id = bob.id        |
|  // without orphanRemoval: bob just has department_id = null      |
+------------------------------------------------------------------+
```

### When to Use Each Cascade

```
Cascade Decision Guide:
+------------------------------------------------------------------+
|                                                                   |
|  Parent owns children completely?                                 |
|  (Children cannot exist without parent)                           |
|  Example: Order --> OrderItems                                    |
|      |                                                            |
|   YES --> cascade = CascadeType.ALL, orphanRemoval = true         |
|                                                                   |
|  Parent creates children but they are shared?                     |
|  (Children may belong to other parents too)                       |
|  Example: Department --> Employees                                |
|      |                                                            |
|   MAYBE --> cascade = {PERSIST, MERGE}                            |
|             (do NOT cascade REMOVE — would delete shared data)    |
|             (do NOT use orphanRemoval — employee moves depts)     |
|                                                                   |
|  Parent just references existing children?                        |
|  (Children are managed independently)                             |
|  Example: Tag --> Products (many-to-many via join)                |
|      |                                                            |
|   NO --> No cascade at all                                        |
+------------------------------------------------------------------+
```

---

## Collection Types: List vs Set

JPA supports several collection types for `@OneToMany`:

```java
// List — ordered, allows duplicates
@OneToMany(mappedBy = "department")
private List<Employee> employees = new ArrayList<>();

// Set — unordered, no duplicates
@OneToMany(mappedBy = "department")
private Set<Employee> employees = new HashSet<>();
```

```
List vs Set for @OneToMany:
+------------------------------------------------------------------+
|                                                                   |
|  List<Employee>                    Set<Employee>                  |
|  ---------------------------       ---------------------------    |
|  Preserves insertion order         No guaranteed order            |
|  Allows duplicates (rare in DB)    No duplicates                  |
|  Uses ArrayList internally         Uses HashSet internally        |
|  Remove by index or value          Remove by value only           |
|                                                                   |
|  Hibernate behavior:               Hibernate behavior:            |
|  - remove(obj) works fine          - Requires equals/hashCode!    |
|  - No extra requirements           - Without proper equals,       |
|                                      contains() and remove()      |
|                                      will not work correctly      |
|                                                                   |
|  Recommendation:                                                  |
|  Use List for simplicity unless you need Set semantics.           |
|  If using Set, ALWAYS implement equals() and hashCode()           |
|  based on a business key (NOT the auto-generated id).             |
+------------------------------------------------------------------+
```

### Implementing equals and hashCode for Entities

When using `Set<Employee>`, you need proper `equals()` and `hashCode()`:

```java
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    // ... other fields

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Employee employee = (Employee) o;
        // Use business key (email), NOT id
        return email != null && email.equals(employee.email);
    }

    @Override
    public int hashCode() {
        // Use business key (email), NOT id
        return email != null ? email.hashCode() : 0;
    }
}
```

```
Why NOT Use id for equals/hashCode:
+------------------------------------------------------------------+
|                                                                   |
|  Problem with id-based equals:                                    |
|                                                                   |
|  Employee e1 = new Employee("Alice", "alice@co.com");             |
|  // e1.id is null (not yet saved)                                 |
|                                                                   |
|  Set<Employee> set = new HashSet<>();                             |
|  set.add(e1);                                                     |
|  // hashCode based on id = null --> hashCode = 0                  |
|                                                                   |
|  employeeRepository.save(e1);                                     |
|  // e1.id is now 1 --> hashCode changes!                          |
|                                                                   |
|  set.contains(e1); // FALSE! hashCode changed after insertion     |
|  // The Set cannot find the element because the hash bucket       |
|  // changed. The element is "lost" in the Set.                    |
|                                                                   |
|  Solution: Use a stable business key (email, ISBN, SSN)           |
|  that does not change between new and persisted states.           |
+------------------------------------------------------------------+
```

---

## Querying One-to-Many Relationships

### Derived Query Methods

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // Find employees by department name
    List<Employee> findByDepartmentName(String deptName);

    // Count employees in a department
    long countByDepartmentId(Long deptId);

    // Find by department and salary
    List<Employee> findByDepartmentNameAndSalaryGreaterThan(
        String deptName, BigDecimal minSalary);

    // Check if department has any employees
    boolean existsByDepartmentId(Long deptId);
}

@Repository
public interface DepartmentRepository extends JpaRepository<Department, Long> {

    // Find departments that have employees with a certain name
    List<Department> findByEmployeesName(String employeeName);

    // Find departments with employees earning above threshold
    @Query("SELECT DISTINCT d FROM Department d JOIN d.employees e WHERE e.salary > :min")
    List<Department> findDepartmentsWithHighEarners(@Param("min") BigDecimal min);
}
```

### JPQL Queries

```java
// JOIN FETCH to avoid N+1
@Query("SELECT d FROM Department d LEFT JOIN FETCH d.employees WHERE d.name = :name")
Optional<Department> findByNameWithEmployees(@Param("name") String name);

// Aggregate query
@Query("SELECT d.name, COUNT(e), AVG(e.salary) " +
       "FROM Department d LEFT JOIN d.employees e " +
       "GROUP BY d.name ORDER BY COUNT(e) DESC")
List<Object[]> getDepartmentStatistics();

// Find departments with employee count
@Query("SELECT new com.example.dto.DeptSummary(d.name, SIZE(d.employees)) " +
       "FROM Department d")
List<DeptSummary> getDepartmentSummaries();
```

---

## @OrderBy — Ordering Collection Elements

You can specify a default ordering for collection elements:

```java
@Entity
public class Department {

    @OneToMany(mappedBy = "department")
    @OrderBy("name ASC")  // JPA standard — order by employee name
    private List<Employee> employees = new ArrayList<>();
}

// Multiple sort fields
@OneToMany(mappedBy = "post")
@OrderBy("createdAt DESC, author ASC")  // Newest first, then by author
private List<Comment> comments = new ArrayList<>();
```

```
@OrderBy Behavior:
+------------------------------------------------------------------+
|                                                                   |
|  When Hibernate loads the collection, it adds ORDER BY to SQL:    |
|                                                                   |
|  Without @OrderBy:                                                |
|  SELECT * FROM employees WHERE department_id = 1                  |
|  (no guaranteed order)                                            |
|                                                                   |
|  With @OrderBy("name ASC"):                                       |
|  SELECT * FROM employees WHERE department_id = 1 ORDER BY name    |
|  (always alphabetical)                                            |
|                                                                   |
|  Note: @OrderBy uses JPQL field names, not column names.          |
|  Use "name" not "employee_name".                                  |
+------------------------------------------------------------------+
```

---

## Complete Example: Post and Comments

A practical blog example with comments as owned children:

```java
@Entity
@Table(name = "posts")
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "post", cascade = CascadeType.ALL,
               orphanRemoval = true)
    @OrderBy("createdAt ASC")
    private List<Comment> comments = new ArrayList<>();

    protected Post() {}

    public Post(String title, String content) {
        this.title = title;
        this.content = content;
        this.createdAt = LocalDateTime.now();
    }

    // Helper methods
    public Comment addComment(String author, String text) {
        Comment comment = new Comment(author, text);
        comments.add(comment);
        comment.setPost(this);
        return comment;
    }

    public void removeComment(Comment comment) {
        comments.remove(comment);
        comment.setPost(null);
    }

    public int getCommentCount() {
        return comments.size();
    }

    // Getters
    public Long getId() { return id; }
    public String getTitle() { return title; }
    public String getContent() { return content; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public List<Comment> getComments() {
        return Collections.unmodifiableList(comments);
    }
}
```

```java
@Entity
@Table(name = "comments")
public class Comment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String author;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String text;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "post_id", nullable = false)
    private Post post;

    protected Comment() {}

    public Comment(String author, String text) {
        this.author = author;
        this.text = text;
        this.createdAt = LocalDateTime.now();
    }

    // Getters and setters
    public Long getId() { return id; }
    public String getAuthor() { return author; }
    public String getText() { return text; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public Post getPost() { return post; }
    public void setPost(Post post) { this.post = post; }
}
```

```java
@Repository
public interface PostRepository extends JpaRepository<Post, Long> {

    @EntityGraph(attributePaths = {"comments"})
    Optional<Post> findWithCommentsById(Long id);

    @Query("SELECT p FROM Post p LEFT JOIN FETCH p.comments WHERE p.title LIKE %:keyword%")
    List<Post> searchWithComments(@Param("keyword") String keyword);

    @Query("SELECT p FROM Post p WHERE SIZE(p.comments) >= :minComments")
    List<Post> findPopularPosts(@Param("minComments") int minComments);
}
```

```java
@Service
@Transactional
public class BlogService {

    private final PostRepository postRepository;

    public BlogService(PostRepository postRepository) {
        this.postRepository = postRepository;
    }

    public Post createPostWithComments() {
        Post post = new Post("My First Post", "This is the content...");
        post.addComment("Alice", "Great post!");
        post.addComment("Bob", "Thanks for sharing.");
        return postRepository.save(post);
    }

    public void addComment(Long postId, String author, String text) {
        Post post = postRepository.findById(postId).orElseThrow();
        post.addComment(author, text);
        // Cascade saves the new comment
    }

    public void deleteComment(Long postId, Long commentId) {
        Post post = postRepository.findWithCommentsById(postId).orElseThrow();
        post.getComments().stream()
            .filter(c -> c.getId().equals(commentId))
            .findFirst()
            .ifPresent(post::removeComment);
        // orphanRemoval deletes the comment
    }

    @Transactional(readOnly = true)
    public Post getPostWithComments(Long postId) {
        return postRepository.findWithCommentsById(postId)
            .orElseThrow(() -> new RuntimeException("Post not found"));
    }
}
```

---

## Avoiding the N+1 Problem

The N+1 problem is especially common with `@OneToMany`:

```
The N+1 Problem:
+------------------------------------------------------------------+
|                                                                   |
|  // Load all departments                                          |
|  List<Department> departments = departmentRepository.findAll();   |
|  // SQL: SELECT * FROM departments   --> returns 10 departments   |
|                                                                   |
|  // Access each department's employees                            |
|  for (Department dept : departments) {                            |
|      System.out.println(dept.getName() + ": " +                   |
|          dept.getEmployees().size());  // Lazy load triggered!     |
|  }                                                                |
|                                                                   |
|  SQL queries generated:                                           |
|  1. SELECT * FROM departments                       (1 query)     |
|  2. SELECT * FROM employees WHERE department_id = 1  (query 2)    |
|  3. SELECT * FROM employees WHERE department_id = 2  (query 3)    |
|  ...                                                              |
|  11. SELECT * FROM employees WHERE department_id = 10 (query 11)  |
|                                                                   |
|  Total: 1 + 10 = 11 queries (N+1 where N=10)                     |
+------------------------------------------------------------------+

Solutions:
+------------------------------------------------------------------+
|                                                                   |
|  1. JOIN FETCH in JPQL:                                           |
|     @Query("SELECT d FROM Department d LEFT JOIN FETCH             |
|             d.employees")                                         |
|     List<Department> findAllWithEmployees();                      |
|     --> 1 query with LEFT JOIN                                    |
|                                                                   |
|  2. @EntityGraph:                                                 |
|     @EntityGraph(attributePaths = {"employees"})                  |
|     List<Department> findAll();                                   |
|     --> 1 query with LEFT JOIN                                    |
|                                                                   |
|  3. @BatchSize (Hibernate-specific):                              |
|     @OneToMany(mappedBy = "department")                           |
|     @BatchSize(size = 10)                                         |
|     private List<Employee> employees;                             |
|     --> Loads employees for up to 10 departments in 1 query       |
|     --> Reduces N+1 to 1 + ceil(N/10)                             |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Modifying only the @OneToMany collection without setting @ManyToOne**: The collection side (inverse) does not control the FK. You must set the `@ManyToOne` side for the database to be updated.

2. **Using unidirectional @OneToMany without @JoinColumn**: This creates an unnecessary join table with terrible performance. Always add `@JoinColumn` or use a bidirectional mapping.

3. **Cascading REMOVE on shared children**: If an employee can transfer between departments, `cascade = CascadeType.REMOVE` would delete the employee when the department is deleted. Use `cascade = {PERSIST, MERGE}` instead.

4. **Forgetting to initialize the collection**: `private List<Employee> employees;` (null) will throw `NullPointerException` when you call `addEmployee()`. Always initialize: `= new ArrayList<>()`.

5. **Loading large collections unnecessarily**: If a department has 10,000 employees, `dept.getEmployees()` loads all of them. Use JPQL queries with pagination instead of navigating through the collection.

6. **Not setting fetch = FetchType.LAZY on @ManyToOne**: The default for `@ManyToOne` is EAGER. Loading 1,000 employees loads 1,000 departments eagerly. Always set `FetchType.LAZY`.

---

## Best Practices

1. **Always set `fetch = FetchType.LAZY` on @ManyToOne**: The default EAGER loading is almost never what you want. Load the parent entity on demand with `@EntityGraph` or `JOIN FETCH`.

2. **Use bidirectional mappings with helper methods**: The combination of `@ManyToOne` + `@OneToMany(mappedBy)` with `addChild()`/`removeChild()` helpers is the cleanest and most efficient approach.

3. **Use `cascade = CascadeType.ALL` and `orphanRemoval` only for truly owned children**: Order items belong to an order (cascade ALL). Employees do not belong to a department in the same way (they can transfer).

4. **Return unmodifiable collections from getters**: `return Collections.unmodifiableList(employees)` forces callers to use helper methods, maintaining consistency.

5. **Prefer JPQL queries over collection navigation for large sets**: Instead of `dept.getEmployees().stream().filter(...)`, use `employeeRepository.findByDepartmentIdAndSalaryGreaterThan(deptId, min)`.

6. **Initialize collections to avoid NullPointerException**: Always write `= new ArrayList<>()` or `= new HashSet<>()` in the field declaration.

---

## Summary

In this chapter, you learned how to map the most common relationship type:

- **@ManyToOne** is the owning side and should always have `fetch = FetchType.LAZY`. The foreign key column lives in the child table.

- **@OneToMany(mappedBy)** is the inverse side. It provides collection navigation but does not control the foreign key. The `mappedBy` value is the field name on the child entity.

- **Helper methods** (`addChild()`, `removeChild()`) are essential for keeping both sides of a bidirectional relationship synchronized.

- **Cascade** propagates persistence operations from parent to child. Use `CascadeType.ALL` for truly owned children; use `{PERSIST, MERGE}` for shared children.

- **orphanRemoval** deletes children that are removed from the collection, not just when the parent is deleted.

- **Avoid unidirectional @OneToMany without @JoinColumn** — it creates a join table with poor performance.

- **The N+1 problem** occurs when lazy-loading collections in a loop. Solve it with `JOIN FETCH`, `@EntityGraph`, or `@BatchSize`.

- **@OrderBy** defines a default ordering for collection elements.

---

## Interview Questions

**Q1: What is the difference between @ManyToOne and @OneToMany?**

They are two sides of the same relationship. `@ManyToOne` is on the child entity (many employees belong to one department) and is the owning side that controls the foreign key. `@OneToMany` is on the parent entity (one department has many employees) and is the inverse side that provides collection navigation via `mappedBy`.

**Q2: Why is it important to use helper methods in bidirectional relationships?**

Helper methods synchronize both sides of the relationship in memory. Without them, you might only set the collection side (inverse), which does not update the foreign key. Or you might only set the `@ManyToOne` side, which updates the FK but leaves the parent's collection inconsistent. Helper methods ensure both sides are always in sync.

**Q3: What happens if you use @OneToMany without mappedBy or @JoinColumn?**

Hibernate creates an unnecessary join table (e.g., `departments_employees`) to manage the relationship. This adds an extra table, requires extra JOINs, and causes poor performance — especially for collection modifications where Hibernate deletes all join table rows and re-inserts them.

**Q4: When should you use orphanRemoval = true?**

When the child entity cannot meaningfully exist without its parent. Examples: OrderItem without an Order, Comment without a Post. When you remove the child from the parent's collection, `orphanRemoval` automatically deletes it from the database. Do not use it when children can be transferred to another parent (e.g., Employee transferring departments).

**Q5: What is the N+1 problem and how do you solve it with @OneToMany?**

Loading N parent entities and then accessing their lazy collections triggers N additional queries (1 for parents + N for each collection). Solutions: (1) `JOIN FETCH` in JPQL loads everything in one query, (2) `@EntityGraph` specifies eager loading per query, (3) `@BatchSize` (Hibernate) batches multiple collection loads into fewer queries.

**Q6: Why should @ManyToOne default fetch type be changed to LAZY?**

The JPA default for `@ManyToOne` is `FetchType.EAGER`, which loads the parent entity immediately with every child query. If you load 1,000 employees, it joins the departments table 1,000 times even if you do not need department data. Setting `FetchType.LAZY` defers loading until you actually call `employee.getDepartment()`.

---

## Practice Exercises

**Exercise 1: Basic Bidirectional Mapping**
Create `Category` and `Product` entities with a bidirectional one-to-many relationship. Write helper methods, a service to add/remove products from categories, and test all operations.

**Exercise 2: Cascade Behavior**
Create `Order` and `OrderItem` entities where items are fully owned by the order. Test: (a) creating an order with 3 items in one save, (b) removing an item (orphanRemoval), (c) deleting the order (cascade removes all items).

**Exercise 3: N+1 Detection and Fix**
Load all departments and print each department's employee count. Enable SQL logging. Count the queries (observe N+1). Fix it with (a) JOIN FETCH and (b) @EntityGraph. Verify the query count drops to 1.

**Exercise 4: Transfer Between Parents**
Implement an employee transfer feature. Write a service method that moves an employee from one department to another. Verify the FK is updated and both collections are correct. Handle edge cases (employee not found, same department).

**Exercise 5: Blog Application**
Build a blog with `Author`, `Post`, and `Comment` entities. Author has many Posts (bidirectional). Post has many Comments (bidirectional, owned). Write a service with: create post, add comment, delete comment, get post with comments, get author with all posts and comments (solve N+1).

---

## What Is Next?

In the next chapter, we will explore **Many-to-Many Relationships** — the most complex relationship type. You will learn how to use `@ManyToMany` with `@JoinTable`, add extra columns to join tables by breaking them into two `@OneToMany` relationships, handle the equals/hashCode challenge with Sets, and choose the right collection type for many-to-many associations.
