# Chapter 17: Entity Lifecycle and Persistence Context

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the four entity lifecycle states: New, Managed, Detached, Removed
- Explain what the persistence context is and how it works as a first-level cache
- Describe how dirty checking detects changes automatically
- Know when and how Hibernate flushes changes to the database
- Use flush modes to control when SQL is executed
- Work with detached entities: merge, reattach, and handle common issues
- Understand the open-session-in-view pattern and why it is controversial
- Use EntityManager methods (persist, merge, find, remove, detach, clear, flush)
- Avoid common pitfalls with entity state transitions

---

## The Four Entity States

Every JPA entity exists in one of four states relative to the **persistence context** (the first-level cache managed by Hibernate):

```
Entity Lifecycle States:
+------------------------------------------------------------------+
|                                                                   |
|                     +----------+                                  |
|         new         |          |       entityManager.persist()     |
|      keyword        |   NEW    |----------------------------+     |
|    (constructor)    | (Transient)                            |     |
|                     +----------+                             |     |
|                                                              v     |
|                                                        +---------+ |
|  entityManager  +----------+                           |         | |
|  .find()        |          |   entityManager.remove()  | MANAGED | |
|  ------------->| MANAGED  |------------------------->|         | |
|  @Query         |          |                           +---------+ |
|  repository     +----------+                             |     ^   |
|  .findById()         |  ^                                |     |   |
|                      |  |   entityManager.merge()        |     |   |
|  entityManager       |  +-------------------------------+     |   |
|  .detach()           |                                         |   |
|  .clear()            v                                         |   |
|  transaction    +----------+                                   |   |
|  ends           |          |   entityManager.merge()           |   |
|                 | DETACHED |-----------------------------------+   |
|                 |          |                                       |
|                 +----------+                                      |
|                                                                   |
|                 +----------+                                      |
|                 |          |   flush() / commit()                  |
|                 | REMOVED  |-------> DELETE SQL executed           |
|                 |          |         entity gone from DB           |
|                 +----------+                                      |
|                                                                   |
+------------------------------------------------------------------+
```

### State Definitions

```
State        In Persistence    Has DB     Tracked by      Changes
             Context?          Row?       Hibernate?      Auto-saved?
----------------------------------------------------------------------
NEW          No                No         No              No
(Transient)  Just created      Not yet    Not watching    Must call
             with new          in any     this object     persist()
                               table

MANAGED      Yes               Yes (or    Yes             Yes!
                               will be    Dirty checking  Changes saved
                               on flush)  is active       on flush

DETACHED     No                Yes        No              No
             Was managed,      Row        Not watching    Must call
             now disconnected  still      anymore         merge()
                               exists

REMOVED      Yes               Yes (until Yes             N/A
             Scheduled for     DELETE     Scheduled for   Will be
             deletion          runs)      removal         deleted
```

---

## The Persistence Context

The persistence context is the central concept in JPA. Think of it as a **workspace** where Hibernate tracks entities and their changes.

```
Persistence Context (First-Level Cache):
+------------------------------------------------------------------+
|                                                                   |
|  EntityManager (Spring @Transactional scope)                      |
|  +--------------------------------------------------------------+|
|  |  Persistence Context                                          ||
|  |  +----------------------------------------------------------+||
|  |  |  Identity Map (first-level cache)                         |||
|  |  |                                                           |||
|  |  |  Key: (Entity Type + ID)     Value: Entity Instance       |||
|  |  |  --------------------------  -------------------------    |||
|  |  |  (Employee, 1)               Employee{id=1, name="Alice"} |||
|  |  |  (Employee, 2)               Employee{id=2, name="Bob"}   |||
|  |  |  (Department, 10)            Department{id=10, name="Eng"}|||
|  |  |                                                           |||
|  |  |  Guarantees:                                              |||
|  |  |  - Same ID always returns SAME Java object (identity)     |||
|  |  |  - Loaded entities are cached (no duplicate queries)      |||
|  |  |  - Changes are tracked (dirty checking)                   |||
|  |  +----------------------------------------------------------+||
|  |                                                               ||
|  |  Action Queue (pending SQL)                                   ||
|  |  +----------------------------------------------------------+||
|  |  |  INSERT Employee(id=3, name="Carol")                      |||
|  |  |  UPDATE Employee SET name="Alicia" WHERE id=1             |||
|  |  |  DELETE FROM Employee WHERE id=2                          |||
|  |  +----------------------------------------------------------+||
|  +--------------------------------------------------------------+|
|                                                                   |
|  On flush/commit: Action Queue SQL is sent to the database        |
+------------------------------------------------------------------+
```

### Identity Guarantee

The persistence context ensures that for any given entity type and ID, you always get the **same Java object instance**:

```java
@Transactional
public void demonstrateIdentity() {
    Employee e1 = entityManager.find(Employee.class, 1L);
    // SQL: SELECT * FROM employees WHERE id = 1

    Employee e2 = entityManager.find(Employee.class, 1L);
    // NO SQL! Returns cached instance from persistence context

    System.out.println(e1 == e2);  // true — exact same object!

    // Even queries return the same instance
    Employee e3 = employeeRepository.findByEmail("alice@co.com");
    // SQL runs, but if it returns id=1, Hibernate returns
    // the SAME object already in the persistence context

    System.out.println(e1 == e3);  // true — same object again!
}
```

```
Identity Guarantee Flow:
+------------------------------------------------------------------+
|                                                                   |
|  find(Employee.class, 1L)                                         |
|       |                                                           |
|       v                                                           |
|  Is (Employee, 1) in the persistence context?                     |
|       |                                                           |
|    YES --> Return the cached instance (no SQL)                    |
|       |                                                           |
|    NO --> Execute SELECT, create Employee object,                 |
|           store in persistence context, return it                 |
|                                                                   |
|  Result: Within a transaction, the SAME id always returns         |
|  the SAME Java object. This is called "repeatable read"           |
|  at the application level.                                        |
+------------------------------------------------------------------+
```

---

## Dirty Checking

Hibernate automatically detects changes to managed entities. You do not need to call `save()` or `update()` — just modify the object and Hibernate generates the appropriate UPDATE SQL on flush.

```java
@Transactional
public void updateEmployeeName(Long id, String newName) {
    Employee employee = employeeRepository.findById(id).orElseThrow();
    // employee is now MANAGED

    employee.setName(newName);
    // That's it! No save() call needed.
    // Hibernate detects the change and generates UPDATE on flush.
}
// When @Transactional ends, Hibernate flushes:
// UPDATE employees SET name = 'newName' WHERE id = ?
```

```
How Dirty Checking Works:
+------------------------------------------------------------------+
|                                                                   |
|  1. Entity loaded from DB:                                        |
|     Employee{id=1, name="Alice", salary=80000}                    |
|     Hibernate takes a SNAPSHOT of the original values             |
|     Snapshot: {name="Alice", salary=80000}                        |
|                                                                   |
|  2. Your code modifies the entity:                                |
|     employee.setName("Alicia");                                   |
|     employee.setSalary(85000);                                    |
|     Current: {name="Alicia", salary=85000}                        |
|                                                                   |
|  3. On flush, Hibernate compares current vs snapshot:             |
|     name:   "Alicia" != "Alice"    --> CHANGED                   |
|     salary: 85000 != 80000         --> CHANGED                   |
|                                                                   |
|  4. Hibernate generates UPDATE for changed fields:                |
|     UPDATE employees                                              |
|     SET name = 'Alicia', salary = 85000                           |
|     WHERE id = 1                                                  |
|                                                                   |
|  No explicit save() needed! Managed entities are auto-tracked.   |
+------------------------------------------------------------------+
```

### When save() IS Needed

```
When to Call save() / persist():
+------------------------------------------------------------------+
|                                                                   |
|  NEED save():                                                     |
|  - Creating a NEW entity (not yet in DB)                          |
|    Employee e = new Employee("Alice", "alice@co.com");            |
|    employeeRepository.save(e);  // persist new entity             |
|                                                                   |
|  - Merging a DETACHED entity (was managed, now disconnected)      |
|    employee = employeeRepository.save(detachedEmployee);          |
|    // merge back into persistence context                         |
|                                                                   |
|  DO NOT NEED save():                                              |
|  - Modifying a MANAGED entity (loaded in current transaction)     |
|    Employee e = employeeRepository.findById(1L).orElseThrow();    |
|    e.setName("Alicia");                                           |
|    // Auto-saved on flush. Calling save() here works but          |
|    // is unnecessary and misleading.                              |
+------------------------------------------------------------------+
```

---

## Flushing

Flushing is the process of synchronizing the persistence context with the database — sending all pending SQL statements.

```
Flush Triggers:
+------------------------------------------------------------------+
|                                                                   |
|  Hibernate flushes automatically when:                            |
|                                                                   |
|  1. Transaction commits (@Transactional method ends)              |
|     --> All pending changes flushed then committed                |
|                                                                   |
|  2. Before a JPQL/HQL query executes                              |
|     --> Ensures query sees the latest data                        |
|     employee.setName("Alicia");                                   |
|     List<Employee> result = em.createQuery(                       |
|         "SELECT e FROM Employee e WHERE e.name = 'Alicia'")       |
|         .getResultList();                                         |
|     --> Hibernate flushes the UPDATE before running SELECT        |
|     --> Query correctly finds the employee                        |
|                                                                   |
|  3. When you call entityManager.flush() explicitly                |
|     --> Forces immediate flush                                    |
|                                                                   |
|  Flushing does NOT commit the transaction!                        |
|  The SQL is sent to the DB but can still be rolled back.          |
+------------------------------------------------------------------+
```

### Flush Ordering

Hibernate flushes SQL in a specific order to satisfy foreign key constraints:

```
Flush SQL Order:
+------------------------------------------------------------------+
|                                                                   |
|  1. INSERT statements (new entities)                              |
|     - Parent entities first (departments before employees)        |
|                                                                   |
|  2. UPDATE statements (modified entities)                         |
|     - In order of modification                                    |
|                                                                   |
|  3. DELETE collection elements                                    |
|     - Remove from join tables first                               |
|                                                                   |
|  4. DELETE statements (removed entities)                          |
|     - Child entities first (employees before departments)         |
|     - Reverse order of INSERT                                     |
|                                                                   |
|  This ordering ensures FK constraints are never violated.         |
|  Hibernate handles this automatically.                            |
+------------------------------------------------------------------+
```

### Flush Modes

```java
// JPA standard flush modes
entityManager.setFlushMode(FlushModeType.AUTO);    // Default — flush before queries
entityManager.setFlushMode(FlushModeType.COMMIT);  // Only flush on commit
```

```
Flush Modes:
+------------------------------------------------------------------+
|                                                                   |
|  FlushModeType.AUTO (default):                                    |
|  - Flushes before every JPQL/HQL query                            |
|  - Flushes on commit                                              |
|  - Safest: queries always see latest changes                      |
|  - May cause extra flushes (performance overhead)                 |
|                                                                   |
|  FlushModeType.COMMIT:                                            |
|  - Flushes ONLY on commit                                         |
|  - Queries might NOT see uncommitted changes                      |
|  - Fewer flushes (better performance for batch operations)        |
|  - Use when you know queries don't need pending changes           |
|                                                                   |
|  Recommendation: Keep AUTO for correctness.                       |
|  Switch to COMMIT only for performance-critical batch operations. |
+------------------------------------------------------------------+
```

---

## EntityManager Methods and State Transitions

### persist() — New to Managed

```java
@Transactional
public void persistExample() {
    Employee employee = new Employee("Alice", "alice@co.com");
    // State: NEW (transient) — not tracked, no DB row

    entityManager.persist(employee);
    // State: MANAGED — tracked by persistence context
    // No SQL yet! INSERT is queued for flush.
    // employee.getId() may be set immediately (IDENTITY strategy)
    // or later (SEQUENCE strategy)

    employee.setName("Alicia");
    // Still MANAGED — this change will be included in the INSERT
    // or generate an UPDATE after the INSERT
}
// Transaction commits: INSERT INTO employees (name, email) VALUES ('Alicia', 'alice@co.com')
```

```
persist() Flow:
+------------------------------------------------------------------+
|                                                                   |
|  Employee e = new Employee(...)     --> State: NEW                |
|       |                                                           |
|       v                                                           |
|  entityManager.persist(e)           --> State: MANAGED            |
|       |                                - Added to persistence ctx |
|       |                                - INSERT queued            |
|       |                                - ID may be assigned       |
|       v                                                           |
|  e.setName("Alicia")               --> Still MANAGED              |
|       |                                - Change detected (dirty)  |
|       v                                                           |
|  Transaction commit                 --> FLUSH                     |
|       |                                - INSERT executed          |
|       v                                - COMMIT                   |
|  After commit                       --> State: DETACHED           |
|                                        - No longer tracked        |
+------------------------------------------------------------------+
```

### find() — Database to Managed

```java
@Transactional
public void findExample() {
    Employee employee = entityManager.find(Employee.class, 1L);
    // SQL: SELECT * FROM employees WHERE id = 1
    // State: MANAGED — loaded into persistence context

    // Second find — no SQL! Returned from cache.
    Employee same = entityManager.find(Employee.class, 1L);
    assert employee == same;  // Same Java object instance

    // find returns null if not found (does NOT throw)
    Employee notFound = entityManager.find(Employee.class, 999L);
    assert notFound == null;
}
```

### merge() — Detached to Managed

```java
@Transactional
public Employee mergeExample(Employee detachedEmployee) {
    // detachedEmployee was loaded in a previous transaction
    // State: DETACHED — has an ID but not tracked

    detachedEmployee.setName("Updated Name");
    // This change is NOT tracked! Entity is detached.

    Employee managedEmployee = entityManager.merge(detachedEmployee);
    // State of managedEmployee: MANAGED (new copy in persistence context)
    // State of detachedEmployee: STILL DETACHED (not the same object!)

    assert detachedEmployee != managedEmployee;  // Different objects!
    // Always use the RETURNED entity, not the original.

    return managedEmployee;
}
```

```
merge() — Critical Detail:
+------------------------------------------------------------------+
|                                                                   |
|  Employee detached = loadedInPreviousTransaction();               |
|  detached.setName("New Name");                                    |
|                                                                   |
|  Employee managed = entityManager.merge(detached);                |
|                                                                   |
|  What merge() does:                                               |
|  1. Finds entity with same ID in persistence context              |
|     - If found: copies state from detached to managed instance    |
|     - If not found: loads from DB, then copies state              |
|  2. Returns the MANAGED copy (not the original!)                  |
|                                                                   |
|  CRITICAL: detached and managed are DIFFERENT objects!            |
|  detached is still detached. managed is the one being tracked.    |
|                                                                   |
|  Common mistake:                                                  |
|  entityManager.merge(detached);                                   |
|  detached.setSalary(100000);  // BUG! Changes to detached         |
|                               // are NOT tracked!                 |
|                                                                   |
|  Correct:                                                         |
|  Employee managed = entityManager.merge(detached);                |
|  managed.setSalary(100000);   // Correct — changes to managed     |
|                               // ARE tracked                      |
+------------------------------------------------------------------+
```

### remove() — Managed to Removed

```java
@Transactional
public void removeExample(Long id) {
    Employee employee = entityManager.find(Employee.class, id);
    // State: MANAGED

    entityManager.remove(employee);
    // State: REMOVED — scheduled for deletion
    // DELETE is queued, not yet executed

    // You can still read the entity's data
    System.out.println(employee.getName());  // Works

    // But it will be deleted on flush/commit
}
// Transaction commits: DELETE FROM employees WHERE id = ?
```

### detach() and clear()

```java
@Transactional
public void detachExample() {
    Employee employee = entityManager.find(Employee.class, 1L);
    // State: MANAGED

    entityManager.detach(employee);
    // State: DETACHED — removed from persistence context
    // Future changes are NOT tracked

    employee.setName("New Name");
    // This change is LOST — entity is detached, no dirty checking

    // clear() detaches ALL entities
    Employee e1 = entityManager.find(Employee.class, 1L);
    Employee e2 = entityManager.find(Employee.class, 2L);

    entityManager.clear();
    // Both e1 and e2 are now DETACHED
    // Persistence context is empty
    // Pending changes are DISCARDED (not flushed!)
}
```

```
detach() vs clear():
+------------------------------------------------------------------+
|                                                                   |
|  detach(entity):                                                  |
|  - Removes ONE entity from persistence context                    |
|  - Other entities remain managed                                  |
|  - Pending changes for THIS entity are discarded                  |
|                                                                   |
|  clear():                                                         |
|  - Removes ALL entities from persistence context                  |
|  - Persistence context is completely emptied                      |
|  - ALL pending changes are discarded                              |
|  - Typically preceded by flush() to save pending changes:         |
|    entityManager.flush();  // save everything to DB               |
|    entityManager.clear();  // free memory                         |
|                                                                   |
|  Use case for flush() + clear():                                  |
|  Batch processing — periodically flush and clear to avoid         |
|  memory buildup when processing thousands of entities.            |
+------------------------------------------------------------------+
```

---

## Spring Data JPA and the Persistence Context

When you use Spring Data JPA repositories, the persistence context is managed automatically through `@Transactional`:

```
Spring @Transactional and Persistence Context:
+------------------------------------------------------------------+
|                                                                   |
|  @Service                                                         |
|  public class EmployeeService {                                   |
|                                                                   |
|      @Transactional                                               |
|      public void updateEmployee(Long id, String name) {           |
|          |                                                        |
|          |  Transaction begins                                    |
|          |  EntityManager created                                  |
|          |  Persistence context opened                             |
|          v                                                        |
|          Employee e = repository.findById(id).orElseThrow();      |
|          |  SQL: SELECT ... (entity loaded, state: MANAGED)       |
|          v                                                        |
|          e.setName(name);                                         |
|          |  No SQL yet — change tracked by dirty checking         |
|          v                                                        |
|          // Method ends, @Transactional triggers:                 |
|          // 1. Flush (dirty checking generates UPDATE SQL)        |
|          // 2. Commit (transaction committed)                     |
|          // 3. Persistence context closed                          |
|          // 4. All entities become DETACHED                       |
|      }                                                            |
|  }                                                                |
+------------------------------------------------------------------+
```

### save() in Spring Data JPA

Spring Data's `save()` method internally calls either `persist()` or `merge()` depending on the entity state:

```java
// SimpleJpaRepository.save() — what Spring does internally:
@Transactional
public <S extends T> S save(S entity) {
    if (entityInformation.isNew(entity)) {
        entityManager.persist(entity);    // NEW entity --> persist
        return entity;
    } else {
        return entityManager.merge(entity);  // Existing entity --> merge
    }
}
```

```
How Spring Data save() Decides:
+------------------------------------------------------------------+
|                                                                   |
|  repository.save(entity)                                          |
|       |                                                           |
|       v                                                           |
|  Is the entity new?                                               |
|  (id == null, or @Version is null/0)                              |
|       |                                                           |
|    YES --> entityManager.persist(entity)                          |
|       |   Returns the SAME object (now managed)                   |
|       |                                                           |
|    NO  --> entityManager.merge(entity)                            |
|            Returns a NEW managed copy                             |
|            (original may be different object!)                    |
|                                                                   |
|  This is why save() returns the entity — always use the           |
|  returned value, not the original:                                |
|  Employee saved = repository.save(employee);  // Use 'saved'     |
+------------------------------------------------------------------+
```

---

## Open Session in View (OSIV)

Spring Boot enables **Open Session in View** by default. This keeps the persistence context open for the entire HTTP request, even after the service method's `@Transactional` completes.

```
With OSIV (spring.jpa.open-in-view=true, the default):
+------------------------------------------------------------------+
|                                                                   |
|  HTTP Request Lifecycle:                                          |
|  +------------------------------------------------------------+  |
|  |  Filter opens persistence context                           |  |
|  |       |                                                     |  |
|  |  Controller                                                 |  |
|  |       |                                                     |  |
|  |  @Transactional Service method                              |  |
|  |  +----------------------------------------------+           |  |
|  |  | Transaction + persistence context active     |           |  |
|  |  | Entities are MANAGED                         |           |  |
|  |  | Changes are auto-flushed on commit           |           |  |
|  |  +----------------------------------------------+           |  |
|  |  Transaction committed, but persistence context STAYS OPEN  |  |
|  |       |                                                     |  |
|  |  Controller continues — entities still MANAGED (read-only)  |  |
|  |  Lazy loading WORKS here (extra queries triggered)          |  |
|  |       |                                                     |  |
|  |  JSON serialization — lazy collections loaded on demand     |  |
|  |       |                                                     |  |
|  |  Filter closes persistence context                          |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+

Without OSIV (spring.jpa.open-in-view=false):
+------------------------------------------------------------------+
|                                                                   |
|  HTTP Request Lifecycle:                                          |
|  +------------------------------------------------------------+  |
|  |  Controller                                                 |  |
|  |       |                                                     |  |
|  |  @Transactional Service method                              |  |
|  |  +----------------------------------------------+           |  |
|  |  | Transaction + persistence context active     |           |  |
|  |  | Entities are MANAGED                         |           |  |
|  |  +----------------------------------------------+           |  |
|  |  Transaction committed, persistence context CLOSED          |  |
|  |  Entities become DETACHED                                   |  |
|  |       |                                                     |  |
|  |  Controller — entities are DETACHED                         |  |
|  |  Lazy loading FAILS: LazyInitializationException!           |  |
|  |       |                                                     |  |
|  |  Must use DTOs or fetch everything in the service           |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

### OSIV: The Debate

```
OSIV Pros and Cons:
+------------------------------------------------------------------+
|                                                                   |
|  PROS (why Spring enables it by default):                         |
|  - Convenient: lazy loading works everywhere                      |
|  - No LazyInitializationException surprises                       |
|  - Less upfront thinking about what to fetch                      |
|                                                                   |
|  CONS (why many teams disable it):                                |
|  - Hidden N+1 queries: lazy loads in the view layer               |
|    generate unexpected SQL, hard to find and optimize             |
|  - Database connection held for entire request                    |
|    (including JSON serialization and network I/O)                 |
|  - Violates separation of concerns: data access in               |
|    the presentation layer                                         |
|  - Can cause accidental writes if entity is modified              |
|    outside the service transaction                                |
|                                                                   |
|  Recommendation for production:                                   |
|  spring.jpa.open-in-view=false                                    |
|  - Forces you to fetch everything needed in the service layer     |
|  - Use DTOs or @EntityGraph to load data explicitly               |
|  - Better performance, clearer architecture                       |
+------------------------------------------------------------------+
```

To disable OSIV:

```properties
# application.properties
spring.jpa.open-in-view=false
```

---

## Batch Processing with flush() and clear()

When processing many entities, the persistence context grows and slows down. Use `flush()` + `clear()` periodically:

```java
@Service
public class BatchService {

    @PersistenceContext
    private EntityManager entityManager;

    @Transactional
    public void importEmployees(List<EmployeeData> dataList) {
        int batchSize = 50;

        for (int i = 0; i < dataList.size(); i++) {
            EmployeeData data = dataList.get(i);
            Employee employee = new Employee(data.getName(), data.getEmail());
            entityManager.persist(employee);

            // Every 50 entities: flush to DB and clear the cache
            if ((i + 1) % batchSize == 0) {
                entityManager.flush();  // Send INSERTs to DB
                entityManager.clear();  // Free memory
            }
        }
        // Final flush for remaining entities
        entityManager.flush();
        entityManager.clear();
    }
}
```

```
Batch Processing Memory:
+------------------------------------------------------------------+
|                                                                   |
|  Without flush + clear:                                           |
|                                                                   |
|  Persistence context grows with each persist:                     |
|  [1] [1,2] [1,2,3] ... [1,2,3,...,10000]                        |
|  Memory: 10,000 entities + 10,000 snapshots                      |
|  Dirty checking: compares ALL 10,000 on every flush               |
|  --> OutOfMemoryError with large datasets                         |
|                                                                   |
|  With flush + clear (batch size 50):                              |
|                                                                   |
|  [1..50] --> flush + clear --> [51..100] --> flush + clear -->    |
|  [101..150] --> ...                                               |
|  Memory: max 50 entities at any time                              |
|  Dirty checking: compares only 50 entities per flush              |
|  --> Constant memory usage, scales to millions                    |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Calling save() on managed entities unnecessarily**: When an entity is loaded within `@Transactional`, changes are auto-detected. Calling `repository.save(entity)` after `entity.setName()` is redundant and confusing.

2. **Using the original entity after merge()**: `merge()` returns a NEW managed copy. The original remains detached. Always use the returned entity: `Employee managed = em.merge(detached);`.

3. **Calling clear() without flush()**: `clear()` discards ALL pending changes. If you clear without flushing first, unsaved modifications are silently lost.

4. **Expecting lazy loading after transaction ends**: Without OSIV, accessing a lazy collection after the `@Transactional` method returns throws `LazyInitializationException`. Load all needed data within the transaction.

5. **Modifying detached entities and expecting auto-save**: Detached entities are not tracked. Changes are ignored unless you call `merge()` or `save()` within a new transaction.

6. **Not understanding that flush is not commit**: `flush()` sends SQL to the database but does NOT commit. The transaction can still be rolled back. Only `commit` (at the end of `@Transactional`) makes changes permanent.

---

## Best Practices

1. **Disable OSIV in production**: Set `spring.jpa.open-in-view=false`. Fetch all required data in the service layer using `@EntityGraph`, `JOIN FETCH`, or DTOs.

2. **Do not call save() on managed entities**: If you loaded an entity within `@Transactional`, just modify it. Dirty checking handles the rest. Only call `save()` for new entities or when merging detached ones.

3. **Always use the return value of save() and merge()**: The returned entity is the managed instance. The passed-in entity might be a different (detached) object.

4. **Use flush() + clear() for batch operations**: When processing hundreds or thousands of entities, periodically flush and clear to prevent memory buildup and slow dirty checking.

5. **Keep transactions short**: Long transactions hold database connections and locks. Do your processing, save the results, and end the transaction. Avoid calling external APIs or doing I/O within a transaction.

6. **Use @Transactional(readOnly = true) for read-only operations**: This tells Hibernate to skip dirty checking, saving CPU and memory. It also hints to the database to use a read-only transaction.

---

## Summary

In this chapter, you learned how Hibernate manages entities internally:

- **Four lifecycle states**: NEW (transient, no DB row), MANAGED (tracked, auto-saved), DETACHED (disconnected, not tracked), REMOVED (scheduled for deletion).

- **Persistence context** is a first-level cache that guarantees identity (same ID = same object), caches loaded entities, and tracks changes via dirty checking.

- **Dirty checking** automatically detects changes to managed entities by comparing current values against a snapshot taken at load time. No explicit save needed.

- **Flushing** sends pending SQL to the database. It happens automatically before queries (AUTO mode) and on transaction commit. It is NOT a commit.

- **persist()** makes a new entity managed. **merge()** copies a detached entity into the persistence context (returns a new managed copy). **remove()** schedules deletion. **detach()** and **clear()** remove entities from tracking.

- **OSIV** keeps the persistence context open for the entire HTTP request. Convenient but causes hidden N+1 queries and holds DB connections too long. Disable in production.

- **Batch processing** requires periodic `flush()` + `clear()` to prevent memory exhaustion.

---

## Interview Questions

**Q1: What are the four JPA entity lifecycle states?**

NEW (transient): created with `new`, no persistence context or DB row. MANAGED: tracked by the persistence context, changes auto-detected. DETACHED: was managed but disconnected (transaction ended, or explicitly detached). REMOVED: scheduled for deletion, will be deleted on flush.

**Q2: What is the persistence context and what guarantees does it provide?**

The persistence context is Hibernate's first-level cache. It guarantees: (1) identity — the same entity ID always returns the same Java object within a transaction, (2) caching — repeated finds for the same ID do not hit the database, (3) dirty checking — changes to managed entities are automatically detected and flushed as SQL.

**Q3: Do you need to call save() after modifying a managed entity?**

No. Managed entities are tracked by dirty checking. When you modify a field, Hibernate detects the change and generates an UPDATE on flush/commit. Calling `save()` is only needed for new entities (persist) or detached entities (merge).

**Q4: What is the difference between flush() and commit()?**

`flush()` sends pending SQL statements to the database but does not end the transaction — changes can still be rolled back. `commit()` finalizes the transaction, making all changes permanent. Hibernate flushes automatically before commit.

**Q5: Why does merge() return a different object?**

`merge()` copies the state of a detached entity into a managed instance (either an existing managed entity with the same ID, or a newly loaded one). The returned managed copy is tracked by the persistence context. The original detached entity remains detached and untracked.

**Q6: What is Open Session in View and should you use it?**

OSIV keeps the persistence context open for the entire HTTP request, allowing lazy loading in controllers and view rendering. Spring Boot enables it by default. It should be disabled in production (`spring.jpa.open-in-view=false`) because it causes hidden N+1 queries, holds database connections too long, and violates the separation between service and presentation layers.

**Q7: How do you handle batch processing to avoid OutOfMemoryError?**

Periodically call `entityManager.flush()` followed by `entityManager.clear()` (e.g., every 50 entities). `flush()` sends pending SQL to the database, and `clear()` removes all entities from the persistence context, freeing memory. This keeps memory usage constant regardless of the total number of entities.

---

## Practice Exercises

**Exercise 1: State Transitions**
Write a test method that creates an entity, persists it, modifies it, detaches it, merges it, and removes it. After each step, verify the entity's state by checking if the persistence context contains it (`entityManager.contains(entity)`).

**Exercise 2: Identity Guarantee**
Load the same entity by ID twice and by a query. Verify that all three references point to the exact same Java object (`==`). Then clear the persistence context and load again — verify you get a different object instance.

**Exercise 3: Dirty Checking**
Load an entity, modify three fields, and let the transaction commit. Enable SQL logging and verify that Hibernate generates a single UPDATE with all three changes — without any explicit save() call.

**Exercise 4: merge() Behavior**
Create a method that returns a detached entity (load in one transaction, return after transaction ends). In a new transaction, modify the detached entity and merge it. Verify: (a) the returned entity is different from the original, (b) only the returned entity is managed, (c) the database is updated.

**Exercise 5: Batch Import**
Write a batch import method that inserts 1,000 entities. First implement without flush/clear and observe memory growth. Then add flush/clear every 50 entities. Enable Hibernate statistics to compare the two approaches.

---

## What Is Next?

In the next chapter, we will tackle **Fetching Strategies: Solving the N+1 Problem**. You will learn the difference between lazy and eager fetching, understand why the N+1 problem is the most common Hibernate performance issue, and master the tools to solve it: JOIN FETCH, @EntityGraph, @BatchSize, and subselect fetching.
