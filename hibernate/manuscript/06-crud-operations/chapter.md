# Chapter 6: Basic CRUD Operations with JPA

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the four entity lifecycle states: New, Managed, Detached, Removed
- Use every method in CrudRepository and JpaRepository
- Distinguish between save, saveAndFlush, and saveAll
- Understand when and why Hibernate flushes changes to the database
- Use flush and clear operations for fine-grained control
- Handle Optional returns safely
- Perform batch save and delete operations
- Know how dirty checking eliminates the need for explicit updates

---

## Entity Lifecycle States

Every JPA entity exists in one of four states. Understanding these states is fundamental to understanding how JPA manages your data.

```
+-------------------------------------------------------------------+
|                    Entity Lifecycle States                          |
|                                                                    |
|  +----------+     persist()      +-----------+                     |
|  |          | -----------------> |           |                     |
|  |   NEW    |                    |  MANAGED  | <---+               |
|  | (Transient)                   |           |     |               |
|  +----------+                    +-----------+     |               |
|       ^                           |    |    |      |               |
|       |                   remove()|    |    |merge()|              |
|       |                           |    |    |      |               |
|       |                           v    |    |      |               |
|       |                    +-----------+|   |  +-----------+       |
|       |                    |           ||   |  |           |       |
|       |                    |  REMOVED  ||   +->| DETACHED  |       |
|       |                    |           ||      |           |       |
|       |                    +-----------+|      +-----------+       |
|       |                                 |         ^                |
|       |                                 |         |                |
|       |                                 +---------+                |
|       |                              detach() / clear()            |
|       |                              / transaction ends            |
|       |                                                            |
|       +--- garbage collected (no reference)                        |
+-------------------------------------------------------------------+
```

### State Descriptions

```
State        In Persistence    In Database    Tracked by       Example
             Context?                         EntityManager?
--------------------------------------------------------------------------
NEW          No                No             No               new Student()
(Transient)

MANAGED      Yes               Yes (or will   Yes              After persist()
                               be at flush)                    or find()

DETACHED     No                Yes            No               After detach(),
                                                               clear(), or
                                                               transaction end

REMOVED      Yes (marked       Yes (will be   Yes              After remove()
             for deletion)     deleted at                      (before flush)
                               flush)
```

### Lifecycle in Action

```java
// 1. NEW — just created, not tracked by JPA
Student student = new Student("Alice", "alice@example.com", 20);
// student is NEW (transient)
// Not in persistence context, not in database

// 2. MANAGED — tracked by JPA, changes are detected
studentRepository.save(student);
// student is now MANAGED
// In persistence context, will be INSERTed at flush

// 3. MANAGED — changes are auto-detected (dirty checking)
student.setAge(21);
// NO save() call needed!
// Hibernate detects the change and will UPDATE at flush

// 4. DETACHED — no longer tracked
// (happens automatically at end of @Transactional method)
// Changes to detached entities are NOT tracked

// 5. Re-attach a DETACHED entity
student.setEmail("alice.new@example.com");
studentRepository.save(student);
// save() calls merge() for existing entities
// Creates a new MANAGED copy with the updated state

// 6. REMOVED — marked for deletion
studentRepository.delete(student);
// student is REMOVED
// Will be DELETEd at flush
```

### Visualizing the Flow

```
Time -->

new Student("Alice")        repository.save(s)         s.setAge(21)
     |                           |                          |
     v                           v                          v
  +-----+                   +--------+                  +--------+
  | NEW |  -- persist() --> |MANAGED | -- auto-detect ->|MANAGED |
  +-----+                   +--------+    (dirty check) +--------+
                                 |                          |
                                 |                          |
                            (transaction                (transaction
                             commits)                    commits)
                                 |                          |
                                 v                          v
                            INSERT INTO               UPDATE students
                            students ...              SET age = 21 ...
```

---

## CrudRepository Methods

`CrudRepository` is the base interface that provides fundamental CRUD operations. Let us examine every method.

### Setup: The Employee Entity

For this chapter's examples, we will use an `Employee` entity:

```java
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Department department;

    @Column(precision = 10, scale = 2)
    private BigDecimal salary;

    private boolean active;

    public enum Department {
        ENGINEERING, MARKETING, SALES, HR, FINANCE
    }

    public Employee() {}

    public Employee(String name, String email, Department department,
                    BigDecimal salary) {
        this.name = name;
        this.email = email;
        this.department = department;
        this.salary = salary;
        this.active = true;
    }

    // getters, setters, toString...
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public Department getDepartment() { return department; }
    public void setDepartment(Department department) { this.department = department; }
    public BigDecimal getSalary() { return salary; }
    public void setSalary(BigDecimal salary) { this.salary = salary; }
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }

    @Override
    public String toString() {
        return "Employee{id=" + id + ", name='" + name + "', department=" +
               department + ", salary=" + salary + "}";
    }
}
```

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {
}
```

---

### CREATE Operations

#### save(S entity)

Saves a single entity. If the entity is new (ID is null), it calls `persist()` (INSERT). If the entity already exists (ID is not null), it calls `merge()` (UPDATE).

```java
// CREATE — new entity (id is null)
Employee emp = new Employee("Alice", "alice@company.com",
    Employee.Department.ENGINEERING, new BigDecimal("95000"));
Employee saved = employeeRepository.save(emp);
System.out.println("Saved with ID: " + saved.getId());  // ID is now set
```

```sql
-- SQL generated:
INSERT INTO employees (active, department, email, name, salary, id)
VALUES (true, 'ENGINEERING', 'alice@company.com', 'Alice', 95000.00, default)
```

#### saveAll(Iterable<S> entities)

Saves multiple entities in one call:

```java
List<Employee> employees = List.of(
    new Employee("Bob", "bob@company.com",
        Employee.Department.MARKETING, new BigDecimal("85000")),
    new Employee("Charlie", "charlie@company.com",
        Employee.Department.SALES, new BigDecimal("78000")),
    new Employee("Diana", "diana@company.com",
        Employee.Department.HR, new BigDecimal("82000"))
);

List<Employee> saved = employeeRepository.saveAll(employees);
System.out.println("Saved " + saved.size() + " employees");
```

```
saveAll() internals:
+------------------------------------------------------------------+
|  for each entity in the list:                                     |
|    if entity.getId() == null:                                     |
|      entityManager.persist(entity)   --> schedules INSERT         |
|    else:                                                          |
|      entityManager.merge(entity)     --> schedules UPDATE         |
|                                                                   |
|  All INSERTs/UPDATEs execute at flush time                        |
|                                                                   |
|  Note: With IDENTITY strategy, each INSERT executes immediately.  |
|  With SEQUENCE strategy and batch_size configured, INSERTs can    |
|  be batched for better performance.                               |
+------------------------------------------------------------------+
```

---

### READ Operations

#### findById(ID id)

Returns an `Optional<T>` containing the entity, or empty if not found:

```java
// Safe way — with Optional
Optional<Employee> optional = employeeRepository.findById(1L);

// Pattern 1: ifPresent
optional.ifPresent(emp ->
    System.out.println("Found: " + emp)
);

// Pattern 2: ifPresentOrElse
optional.ifPresentOrElse(
    emp -> System.out.println("Found: " + emp),
    ()  -> System.out.println("Employee not found")
);

// Pattern 3: orElseThrow (for service methods)
Employee emp = employeeRepository.findById(1L)
    .orElseThrow(() -> new RuntimeException("Employee not found with ID: 1"));

// Pattern 4: orElse (with default value)
Employee emp = employeeRepository.findById(1L)
    .orElse(new Employee("Unknown", "unknown@company.com",
        Employee.Department.HR, BigDecimal.ZERO));
```

```sql
-- SQL generated:
SELECT e.id, e.active, e.department, e.email, e.name, e.salary
FROM employees e
WHERE e.id = ?
```

#### findAll()

Returns all entities in the table:

```java
List<Employee> all = employeeRepository.findAll();
System.out.println("Total employees: " + all.size());
all.forEach(System.out::println);
```

```sql
-- SQL generated:
SELECT e.id, e.active, e.department, e.email, e.name, e.salary
FROM employees e
```

**Warning**: `findAll()` loads every row into memory. For tables with thousands of rows, use pagination instead (Chapter 11).

#### findAllById(Iterable<ID> ids)

Returns entities matching a list of IDs:

```java
List<Employee> selected = employeeRepository.findAllById(List.of(1L, 3L, 5L));
System.out.println("Found " + selected.size() + " employees");
```

```sql
-- SQL generated:
SELECT e.id, e.active, e.department, e.email, e.name, e.salary
FROM employees e
WHERE e.id IN (?, ?, ?)
```

**Note**: If some IDs do not exist, the method returns only the entities that were found — no exception is thrown. The returned list might be smaller than the input list.

#### existsById(ID id)

Checks if an entity exists without loading it:

```java
boolean exists = employeeRepository.existsById(1L);
System.out.println("Employee 1 exists: " + exists);
```

```sql
-- SQL generated (efficient — does not load the entity):
SELECT COUNT(*) FROM employees WHERE id = ?
-- Returns true if count > 0
```

#### count()

Returns the total number of entities:

```java
long total = employeeRepository.count();
System.out.println("Total employees: " + total);
```

```sql
-- SQL generated:
SELECT COUNT(*) FROM employees
```

---

### UPDATE Operations

JPA handles updates differently than you might expect. You do not call an explicit "update" method. Instead, you modify a managed entity and JPA detects the changes automatically.

#### Dirty Checking — Automatic Updates

```java
@Service
@Transactional    // Keeps entities managed for the duration of the method
public class EmployeeService {

    private final EmployeeRepository repository;

    public EmployeeService(EmployeeRepository repository) {
        this.repository = repository;
    }

    public Employee updateSalary(Long id, BigDecimal newSalary) {
        Employee emp = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Not found"));

        emp.setSalary(newSalary);   // Modify the managed entity

        // NO save() call needed!
        // Hibernate detects the change (dirty checking)
        // and generates an UPDATE at transaction commit

        return emp;
    }
}
```

```
Dirty Checking Flow:
+------------------------------------------------------------------+
|  @Transactional method starts                                     |
|    |                                                              |
|    v                                                              |
|  findById(1L)                                                     |
|    --> SELECT ... FROM employees WHERE id = 1                     |
|    --> Employee loaded, state snapshot saved:                      |
|        {name:"Alice", salary:95000, department:ENGINEERING}       |
|    |                                                              |
|    v                                                              |
|  emp.setSalary(105000)                                            |
|    --> Java object changed in memory                              |
|    --> No SQL yet!                                                |
|    |                                                              |
|    v                                                              |
|  @Transactional method ends (transaction commits)                 |
|    --> Hibernate compares current state vs snapshot:               |
|        Current:  {name:"Alice", salary:105000, department:ENG}    |
|        Snapshot: {name:"Alice", salary:95000,  department:ENG}    |
|        DIFF:     salary changed!                                  |
|    --> Generates and executes:                                     |
|        UPDATE employees SET salary = 105000 WHERE id = 1          |
|    --> COMMIT                                                     |
+------------------------------------------------------------------+
```

This is one of JPA's most powerful features. You work with plain Java objects, and the framework handles persistence automatically.

#### Explicit save() for Updates

You can also use `save()` to update entities. This is necessary when:
- The entity is **detached** (not in a `@Transactional` context)
- You want to be explicit about the save operation

```java
// Load the entity (becomes detached after the method returns)
Employee emp = employeeRepository.findById(1L).orElseThrow();

// Modify the detached entity
emp.setDepartment(Employee.Department.FINANCE);
emp.setSalary(new BigDecimal("110000"));

// Must call save() to merge the detached entity
employeeRepository.save(emp);
```

```
save() for detached entities:
+------------------------------------------------------------------+
|  save(detachedEmployee)                                           |
|    |                                                              |
|    v                                                              |
|  Is id null?                                                      |
|    NO --> entityManager.merge(detachedEmployee)                   |
|           |                                                       |
|           v                                                       |
|           SELECT ... WHERE id = ?   (load current state)          |
|           Copy detached state onto managed entity                 |
|           UPDATE ... SET ... WHERE id = ?   (at flush)            |
+------------------------------------------------------------------+
```

#### When to Use save() vs Dirty Checking

```
+---------------------------------------------------------------+
|  Approach              When to Use                             |
|---------------------------------------------------------------|
|  Dirty checking        Inside @Transactional methods           |
|  (no save() needed)    Entity is managed (loaded in this       |
|                        transaction)                            |
|                        Cleaner code, fewer SQL calls           |
|                                                                |
|  Explicit save()       Entity is detached                      |
|                        In controllers or non-transactional     |
|                        code                                    |
|                        When you want to be explicit            |
+---------------------------------------------------------------+
```

---

### DELETE Operations

#### deleteById(ID id)

Deletes an entity by its primary key:

```java
employeeRepository.deleteById(3L);
```

```sql
-- SQL generated (two queries):
-- 1. Load the entity first
SELECT e.id, e.active, e.department, e.email, e.name, e.salary
FROM employees e WHERE e.id = ?

-- 2. Delete it
DELETE FROM employees WHERE id = ?
```

**Why two queries?** JPA requires the entity to be in the managed state before deletion. This allows lifecycle callbacks (`@PreRemove`, `@PostRemove`) to fire. If you want a single-query delete, use a custom `@Query` (Chapter 8).

#### delete(S entity)

Deletes a specific entity instance:

```java
Employee emp = employeeRepository.findById(1L).orElseThrow();
employeeRepository.delete(emp);
```

```sql
-- If entity is already managed, only the DELETE:
DELETE FROM employees WHERE id = ?
```

#### deleteAll()

Deletes all entities one by one (slow for large tables):

```java
employeeRepository.deleteAll();
```

```sql
-- Loads ALL entities first, then deletes one by one:
SELECT e.id, e.active, ... FROM employees e
DELETE FROM employees WHERE id = 1
DELETE FROM employees WHERE id = 2
DELETE FROM employees WHERE id = 3
-- ... for each entity!
```

**Warning**: `deleteAll()` loads every entity into memory and deletes them individually. For large tables, use `deleteAllInBatch()` instead (JpaRepository method).

#### deleteAllById(Iterable<ID> ids)

Deletes entities matching a list of IDs:

```java
employeeRepository.deleteAllById(List.of(2L, 4L, 6L));
```

---

## JpaRepository — Additional Methods

`JpaRepository` extends `CrudRepository` with several useful methods:

### Flush Operations

#### flush()

Forces Hibernate to send all pending SQL statements to the database immediately:

```java
Employee emp = new Employee("Eve", "eve@company.com",
    Employee.Department.ENGINEERING, new BigDecimal("92000"));
employeeRepository.save(emp);

// SQL is NOT yet sent to the database (it is queued)

employeeRepository.flush();

// NOW the INSERT has been sent to the database
// (but the transaction is not yet committed)
```

```
Normal flow (without flush):
+------------------------------------------------------------------+
|  save(emp)       --> entity queued in persistence context          |
|  save(emp2)      --> entity queued in persistence context          |
|  save(emp3)      --> entity queued in persistence context          |
|  (end of @Transactional)                                          |
|       --> flush: INSERT emp, INSERT emp2, INSERT emp3              |
|       --> commit transaction                                      |
+------------------------------------------------------------------+

With explicit flush:
+------------------------------------------------------------------+
|  save(emp)       --> entity queued in persistence context          |
|  flush()         --> INSERT emp sent to database NOW               |
|  save(emp2)      --> entity queued in persistence context          |
|  flush()         --> INSERT emp2 sent to database NOW              |
|  (end of @Transactional)                                          |
|       --> nothing to flush (already done)                         |
|       --> commit transaction                                      |
+------------------------------------------------------------------+
```

**When to flush:**
- When you need the database to validate constraints immediately
- When you need to call a stored procedure after the INSERT
- When you need the generated ID before the transaction commits
- When doing batch processing and need to manage memory

#### saveAndFlush(S entity)

Saves and immediately flushes to the database:

```java
// Equivalent to save() + flush()
Employee emp = employeeRepository.saveAndFlush(
    new Employee("Frank", "frank@company.com",
        Employee.Department.SALES, new BigDecimal("75000"))
);
// INSERT has been sent to the database immediately
// emp.getId() is guaranteed to be set
```

#### saveAllAndFlush(Iterable<S> entities)

Saves multiple entities and flushes:

```java
List<Employee> batch = List.of(emp1, emp2, emp3);
List<Employee> saved = employeeRepository.saveAllAndFlush(batch);
// All INSERTs sent to database immediately
```

### Batch Delete Operations

#### deleteInBatch(Iterable<T> entities)

Deletes entities in a single SQL DELETE statement (no loading required):

```java
List<Employee> toDelete = employeeRepository.findAllById(List.of(1L, 2L, 3L));
employeeRepository.deleteInBatch(toDelete);
```

```sql
-- SINGLE query (much faster than deleteAll):
DELETE FROM employees WHERE id IN (?, ?, ?)
```

#### deleteAllInBatch()

Deletes all rows with a single SQL statement:

```java
employeeRepository.deleteAllInBatch();
```

```sql
-- SINGLE query:
DELETE FROM employees
```

### Comparison: delete vs deleteInBatch

```
+------------------------------------------------------------------+
|  Method                  SQL Queries          Lifecycle Callbacks  |
|------------------------------------------------------------------|
|  delete(entity)          SELECT + DELETE      Yes (@PreRemove,     |
|                          per entity           @PostRemove fire)    |
|                                                                   |
|  deleteById(id)          SELECT + DELETE      Yes                  |
|                          per entity                                |
|                                                                   |
|  deleteAll()             SELECT all +         Yes                  |
|                          DELETE per entity                         |
|                                                                   |
|  deleteInBatch(list)     Single DELETE        No! (entities not    |
|                          WHERE id IN (...)    loaded, callbacks    |
|                                               do not fire)        |
|                                                                   |
|  deleteAllInBatch()      Single DELETE        No!                  |
|                          FROM table                                |
+------------------------------------------------------------------+
```

**Key trade-off**: `deleteInBatch` and `deleteAllInBatch` are much faster but skip JPA lifecycle callbacks. Use them when performance matters and you do not have `@PreRemove`/`@PostRemove` callbacks.

### getReferenceById(ID id)

Returns a lazy proxy — no database query until you access a field:

```java
Employee ref = employeeRepository.getReferenceById(1L);
// NO SQL executed yet! ref is a Hibernate proxy

System.out.println(ref.getName());
// NOW the SQL executes:
// SELECT ... FROM employees WHERE id = ?
```

```
getReferenceById vs findById:
+------------------------------------------------------------------+
|                                                                   |
|  findById(1L):                                                    |
|    --> Immediately: SELECT ... WHERE id = 1                       |
|    --> Returns the actual entity (or empty Optional)              |
|    --> Use when you need the entity data NOW                      |
|                                                                   |
|  getReferenceById(1L):                                            |
|    --> No query! Returns a proxy object                           |
|    --> Query fires when you access any field                      |
|    --> Throws EntityNotFoundException if not found (on access)    |
|    --> Use when you only need a reference (for setting FKs)       |
|                                                                   |
+------------------------------------------------------------------+
```

`getReferenceById()` is useful when you need an entity reference for setting a relationship, without actually loading the entity data:

```java
// Setting a foreign key without loading the parent entity
Order order = new Order();
order.setCustomer(customerRepository.getReferenceById(42L));
// No SELECT on customers table! Just sets customer_id = 42
orderRepository.save(order);
```

---

## Complete CRUD Service Example

Here is a complete service class demonstrating all CRUD patterns:

```java
package com.example.hibernatedemo.service;

import com.example.hibernatedemo.entity.Employee;
import com.example.hibernatedemo.repository.EmployeeRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class EmployeeService {

    private final EmployeeRepository repository;

    public EmployeeService(EmployeeRepository repository) {
        this.repository = repository;
    }

    // --- CREATE ---

    public Employee createEmployee(String name, String email,
                                   Employee.Department dept, BigDecimal salary) {
        Employee emp = new Employee(name, email, dept, salary);
        return repository.save(emp);
    }

    public List<Employee> createEmployees(List<Employee> employees) {
        return repository.saveAll(employees);
    }

    // --- READ ---

    @Transactional(readOnly = true)    // Optimization: no dirty checking
    public Employee getEmployee(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new RuntimeException(
                "Employee not found with id: " + id));
    }

    @Transactional(readOnly = true)
    public List<Employee> getAllEmployees() {
        return repository.findAll();
    }

    @Transactional(readOnly = true)
    public boolean employeeExists(Long id) {
        return repository.existsById(id);
    }

    @Transactional(readOnly = true)
    public long countEmployees() {
        return repository.count();
    }

    // --- UPDATE ---

    public Employee updateEmployee(Long id, String name, String email) {
        Employee emp = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Not found: " + id));

        emp.setName(name);
        emp.setEmail(email);

        // No save() needed! Dirty checking handles the UPDATE
        return emp;
    }

    public Employee updateSalary(Long id, BigDecimal newSalary) {
        Employee emp = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Not found: " + id));

        emp.setSalary(newSalary);
        // Dirty checking will generate: UPDATE employees SET salary = ? WHERE id = ?

        return emp;
    }

    public Employee deactivateEmployee(Long id) {
        Employee emp = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Not found: " + id));

        emp.setActive(false);
        return emp;
    }

    // --- DELETE ---

    public void deleteEmployee(Long id) {
        if (!repository.existsById(id)) {
            throw new RuntimeException("Employee not found with id: " + id);
        }
        repository.deleteById(id);
    }

    public void deleteEmployees(List<Long> ids) {
        List<Employee> employees = repository.findAllById(ids);
        repository.deleteInBatch(employees);  // Efficient batch delete
    }

    public void deleteAllEmployees() {
        repository.deleteAllInBatch();  // Single DELETE statement
    }
}
```

### @Transactional(readOnly = true)

Notice the `@Transactional(readOnly = true)` on read methods. This is a performance optimization:

```
+------------------------------------------------------------------+
|  @Transactional(readOnly = true)                                  |
|                                                                   |
|  What it does:                                                    |
|  1. Tells Hibernate to skip dirty checking for all entities       |
|     loaded in this transaction (no snapshot comparison)            |
|  2. Tells the JDBC driver this is a read-only transaction         |
|     (driver may optimize accordingly)                             |
|  3. Prevents accidental writes (some databases throw errors       |
|     on writes in read-only transactions)                          |
|                                                                   |
|  Performance benefit:                                             |
|  - No snapshot stored for dirty checking                          |
|  - Less memory used                                               |
|  - Faster transaction commit (nothing to flush)                   |
|                                                                   |
|  Use for: findById, findAll, count, exists, any read-only method  |
+------------------------------------------------------------------+
```

---

## Understanding Flush Modes

Hibernate does not execute SQL immediately when you call `save()` or modify an entity. Instead, it queues changes and sends them to the database during a **flush**. Understanding when flushes happen is important for debugging.

### When Does Hibernate Flush?

```
+------------------------------------------------------------------+
|  Automatic Flush Triggers                                         |
|                                                                   |
|  1. Transaction commit                                            |
|     @Transactional method returns --> flush + commit              |
|                                                                   |
|  2. Before a JPQL/SQL query                                       |
|     If you persist an entity and then query for it,               |
|     Hibernate flushes first to ensure the query sees              |
|     the new data                                                  |
|                                                                   |
|  3. Explicit flush() call                                         |
|     repository.flush() or entityManager.flush()                   |
|                                                                   |
|  4. saveAndFlush() call                                           |
|     Combines save + immediate flush                               |
+------------------------------------------------------------------+
```

### Flush Before Query Example

```java
@Transactional
public void demonstrateFlushBeforeQuery() {
    // Save a new employee (queued, not yet in DB)
    Employee emp = new Employee("Grace", "grace@company.com",
        Employee.Department.ENGINEERING, new BigDecimal("100000"));
    employeeRepository.save(emp);

    // Query all employees — Hibernate flushes FIRST
    // so the query includes the new employee
    long count = employeeRepository.count();
    // Flush happens here automatically (before the COUNT query)
    // Then: SELECT COUNT(*) FROM employees

    System.out.println("Count: " + count);  // Includes Grace
}
```

```
Timeline:
+------------------------------------------------------------------+
|  save(grace)     --> queued in persistence context (no SQL)        |
|                                                                   |
|  count()         --> Hibernate detects a pending query             |
|                  --> AUTO flush: INSERT INTO employees ... (grace) |
|                  --> Then: SELECT COUNT(*) FROM employees          |
|                  --> Returns count including grace                 |
|                                                                   |
|  method returns  --> transaction commits                           |
+------------------------------------------------------------------+
```

---

## Working with Optional

Spring Data JPA methods that return a single entity use `Optional<T>`. Here are the key patterns:

### Safe Patterns

```java
// Pattern 1: orElseThrow — use in service methods
public Employee getEmployee(Long id) {
    return repository.findById(id)
        .orElseThrow(() -> new EmployeeNotFoundException(id));
}

// Pattern 2: ifPresent — use when action is optional
public void logIfExists(Long id) {
    repository.findById(id)
        .ifPresent(emp -> log.info("Found employee: {}", emp.getName()));
}

// Pattern 3: map — transform the value
public String getEmployeeName(Long id) {
    return repository.findById(id)
        .map(Employee::getName)
        .orElse("Unknown");
}

// Pattern 4: filter — add conditions
public Optional<Employee> findActiveEmployee(Long id) {
    return repository.findById(id)
        .filter(Employee::isActive);
}

// Pattern 5: or — fallback to another lookup
public Employee findByIdOrEmail(Long id, String email) {
    return repository.findById(id)
        .or(() -> repository.findByEmail(email))
        .orElseThrow(() -> new RuntimeException("Not found"));
}
```

### Anti-Patterns to Avoid

```java
// BAD: Calling .get() without checking
Employee emp = repository.findById(id).get();
// Throws NoSuchElementException if not found!

// BAD: Checking isPresent() then get()
Optional<Employee> opt = repository.findById(id);
if (opt.isPresent()) {
    Employee emp = opt.get();
    // ... use emp
}
// BETTER: Use ifPresent, map, or orElseThrow

// BAD: Using Optional as a field type
public class MyService {
    private Optional<Employee> lastEmployee;  // Don't do this!
}
// Optional is for return values, not fields
```

---

## Batch Operations and Performance

### Saving in Batches

For large numbers of entities, saving one at a time is inefficient:

```java
// SLOW: 1000 individual save calls
for (int i = 0; i < 1000; i++) {
    repository.save(new Employee("Emp-" + i, "emp" + i + "@company.com",
        Employee.Department.ENGINEERING, new BigDecimal("50000")));
}

// BETTER: saveAll with a list
List<Employee> batch = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    batch.add(new Employee("Emp-" + i, "emp" + i + "@company.com",
        Employee.Department.ENGINEERING, new BigDecimal("50000")));
}
repository.saveAll(batch);  // Single method call
```

### Clearing the Persistence Context

When saving very large numbers of entities, the persistence context grows and consumes memory. Periodically flush and clear:

```java
@Transactional
public void importEmployees(List<Employee> employees) {
    int batchSize = 50;

    for (int i = 0; i < employees.size(); i++) {
        entityManager.persist(employees.get(i));

        if (i > 0 && i % batchSize == 0) {
            entityManager.flush();    // Send SQL to database
            entityManager.clear();    // Free memory (detach all entities)
            System.out.println("Flushed batch at index " + i);
        }
    }
    // Final flush happens at transaction commit
}
```

```
Memory usage during batch processing:
+------------------------------------------------------------------+
|                                                                   |
|  Without flush/clear:                                             |
|  Memory: [##########] [####################] [################...]|
|  Entities in context keep growing --> OutOfMemoryError            |
|                                                                   |
|  With flush/clear every 50:                                       |
|  Memory: [####] flush/clear [####] flush/clear [####] ...         |
|  Memory stays bounded                                             |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Calling save() on already-managed entities inside @Transactional**: Dirty checking handles updates automatically. Calling `save()` on a managed entity is redundant (though not harmful — it just triggers an unnecessary merge).

```java
@Transactional
public void updateName(Long id, String name) {
    Employee emp = repository.findById(id).orElseThrow();
    emp.setName(name);
    // repository.save(emp);  // UNNECESSARY! Dirty checking handles it
}
```

2. **Using deleteAll() on large tables**: `deleteAll()` loads every entity then deletes them one by one. Use `deleteAllInBatch()` for a single DELETE statement.

3. **Calling .get() on Optional without checking**: Always use `orElseThrow()`, `orElse()`, `ifPresent()`, or `map()`. Never call `.get()` directly.

4. **Forgetting @Transactional**: Without `@Transactional`, each repository call runs in its own transaction. This means entities become detached between calls, dirty checking does not work, and multiple database operations are not atomic.

5. **Not using readOnly = true for read operations**: Read-only transactions skip dirty checking and snapshot storage, improving performance for query-heavy methods.

6. **Expecting deleteById() to throw an exception for non-existent IDs**: In Spring Data JPA 3.x, `deleteById()` for a non-existent ID does not throw — it simply does nothing (after running a SELECT). Check with `existsById()` first if you need to verify existence.

---

## Best Practices

1. **Use @Transactional at the service layer**: Put `@Transactional` on service classes or methods, not on repositories or controllers. The service layer defines the business transaction boundary.

2. **Use @Transactional(readOnly = true) for read operations**: This is a free performance optimization. Mark all read-only service methods with it.

3. **Let dirty checking handle updates**: Inside `@Transactional` methods, modify managed entities directly. Do not call `save()` unless the entity is detached.

4. **Use deleteInBatch for bulk deletes**: When deleting multiple entities and you do not need lifecycle callbacks, `deleteInBatch()` is significantly faster than `deleteAll()`.

5. **Use orElseThrow() for required lookups**: When an entity must exist, use `orElseThrow()` with a descriptive exception. This makes the error message clear and the code intention obvious.

6. **Use saveAll() instead of save() in a loop**: `saveAll()` is more efficient and expresses the batch intent clearly.

---

## Summary

In this chapter, you mastered CRUD operations in JPA:

- **Entity lifecycle states** (New, Managed, Detached, Removed) determine how JPA tracks and persists changes. Managed entities are tracked; detached entities are not.

- **Dirty checking** automatically detects changes to managed entities and generates UPDATE statements at flush time. Inside `@Transactional` methods, you do not need to call `save()` after modifying an entity.

- **CrudRepository** provides `save`, `findById`, `findAll`, `delete`, `count`, and `existsById`. These cover most basic data access needs.

- **JpaRepository** adds `flush()`, `saveAndFlush()`, `deleteInBatch()`, `deleteAllInBatch()`, and `getReferenceById()` for finer control over persistence and performance.

- **Flush** sends queued SQL to the database. It happens automatically at transaction commit, before queries, and when you call `flush()` explicitly.

- **Optional** must be handled safely using `orElseThrow()`, `ifPresent()`, `map()`, or `orElse()`. Never call `.get()` without checking.

- **@Transactional(readOnly = true)** optimizes read operations by skipping dirty checking.

- **Batch operations** (`saveAll`, `deleteInBatch`, `deleteAllInBatch`) are significantly more efficient than individual operations for large datasets.

---

## Interview Questions

**Q1: What are the four entity lifecycle states in JPA?**

New (transient — not tracked, not in DB), Managed (tracked by EntityManager, in persistence context), Detached (was managed but no longer tracked — after transaction ends or clear()), and Removed (marked for deletion, will be deleted at flush). Only managed entities are tracked for dirty checking.

**Q2: What is dirty checking and how does it work?**

Dirty checking is JPA's mechanism for automatically detecting changes to managed entities. When an entity is loaded, Hibernate takes a snapshot of its state. At flush time (usually transaction commit), Hibernate compares the current state against the snapshot. If any field has changed, it generates and executes an UPDATE statement. This means you do not need to call save() explicitly for updates to managed entities.

**Q3: What is the difference between save() and saveAndFlush()?**

`save()` adds the entity to the persistence context and schedules an INSERT or UPDATE, but the SQL is not immediately sent to the database. `saveAndFlush()` does the same but also immediately flushes the persistence context, sending the SQL to the database right away. Use `saveAndFlush()` when you need the database to validate constraints immediately or when you need the generated ID before the transaction commits.

**Q4: Why does deleteById() execute a SELECT before the DELETE?**

JPA requires entities to be in the managed state before removal. This ensures lifecycle callbacks (`@PreRemove`, `@PostRemove`) fire correctly. `deleteById()` first loads the entity with `findById()`, making it managed, then calls `remove()` on it. If you do not need lifecycle callbacks, use `deleteInBatch()` or a custom `@Query` with a DELETE statement for better performance.

**Q5: What is the difference between deleteAll() and deleteAllInBatch()?**

`deleteAll()` loads every entity into memory, then deletes them one by one with individual DELETE statements. It fires lifecycle callbacks but is very slow for large tables. `deleteAllInBatch()` executes a single `DELETE FROM table` SQL statement — no entity loading, no lifecycle callbacks, but much faster.

**Q6: What does @Transactional(readOnly = true) do?**

It marks the transaction as read-only, which provides two optimizations: (1) Hibernate skips dirty checking — no snapshots are taken and no comparison is done at flush time, saving memory and CPU. (2) The JDBC driver is hinted that this is read-only, allowing potential database-level optimizations. Use it for all methods that only read data.

**Q7: When should you call flush() explicitly?**

Explicit flush is needed when: (1) you need the database to validate constraints before the transaction commits, (2) you need to interleave SQL execution with other logic, (3) you are doing batch processing and need to clear the persistence context periodically to manage memory (flush then clear), (4) you need the generated ID from an INSERT before the transaction ends.

**Q8: What is getReferenceById() and how does it differ from findById()?**

`getReferenceById()` returns a lazy proxy without executing a database query. The actual SQL fires only when you access a non-ID field. It is useful for setting foreign key references without loading the entity. `findById()` immediately executes a SELECT and returns the full entity (or empty Optional). If the entity does not exist, `getReferenceById()` throws `EntityNotFoundException` on field access, while `findById()` returns an empty Optional.

---

## Practice Exercises

**Exercise 1: CRUD Service**
Create a `BookService` with methods: `createBook`, `getBook`, `getAllBooks`, `updateTitle`, `deleteBook`. Use proper `@Transactional` annotations (readOnly for reads). Demonstrate dirty checking by updating a book without calling `save()`.

**Exercise 2: Batch Performance**
Save 500 employees using three approaches: (a) individual `save()` calls in a loop, (b) `saveAll()` with a list, (c) `saveAll()` with flush/clear every 50. Enable SQL logging and count the INSERT statements for each approach. Which is fastest?

**Exercise 3: Delete Comparison**
Create 100 employees. Then delete them using: (a) `deleteAll()`, (b) `deleteAllInBatch()`, (c) `deleteAllById()` with all IDs. Count the SQL statements for each approach and measure which is fastest.

**Exercise 4: Lifecycle States**
Write a `CommandLineRunner` that demonstrates all four entity states with print statements and SQL logging:
1. Create a `new Employee()` and print its ID (should be null — NEW state)
2. Call `save()` and print its ID (should be set — MANAGED state)
3. Modify the entity and observe the UPDATE at flush (MANAGED + dirty checking)
4. Call `delete()` and observe the DELETE (REMOVED state)

**Exercise 5: Optional Handling**
Create a service that finds an employee by ID. Write five different implementations using: `orElseThrow()`, `ifPresent()`, `map()`, `orElse()`, and `filter()`. Write a test or runner that calls each one with both existing and non-existing IDs.

---

## What Is Next?

In the next chapter, we will explore **Spring Data Derived Query Methods** in depth. You will learn the complete naming convention for query methods, all available keywords (Between, Like, In, OrderBy, and many more), how to use different return types (List, Optional, Stream, Page), and how to write complex finders without any SQL or JPQL. By the end of Chapter 7, you will be able to express most queries simply by naming a method.
