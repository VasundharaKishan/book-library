# Chapter 27: Performance Tuning and Monitoring

---

## Learning Goals

By the end of this chapter, you will be able to:

- Enable and interpret Hibernate statistics for performance monitoring
- Configure batch inserts and updates for bulk operations
- Use JPQL bulk UPDATE and DELETE to bypass entity loading
- Understand and configure HikariCP connection pooling
- Enable slow query logging to catch inefficient queries
- Apply database indexing strategies for JPA queries
- Use StatelessSession for high-throughput operations
- Profile and optimize real-world query patterns
- Identify the top performance issues in Hibernate applications

---

## The Top Hibernate Performance Issues

```
Most Common Performance Problems (and where to find fixes):
+------------------------------------------------------------------+
|                                                                   |
|  #1  N+1 Queries (Chapter 18)                                    |
|      Loading N entities triggers N extra queries for relations    |
|      Fix: JOIN FETCH, @EntityGraph, @BatchSize                    |
|                                                                   |
|  #2  Loading too much data                                        |
|      SELECT * when you need 3 columns                             |
|      Fix: Projections, DTOs (Chapter 23)                          |
|                                                                   |
|  #3  No batch processing                                         |
|      1000 inserts = 1000 individual SQL statements                |
|      Fix: JDBC batching (this chapter)                            |
|                                                                   |
|  #4  Missing indexes                                              |
|      Full table scans on WHERE and ORDER BY columns               |
|      Fix: Database indexes (this chapter)                         |
|                                                                   |
|  #5  Connection pool exhaustion                                   |
|      Long transactions hold connections, others wait              |
|      Fix: HikariCP tuning, short transactions (this chapter)     |
|                                                                   |
|  #6  Dirty checking overhead                                      |
|      Hibernate compares every field of every managed entity       |
|      Fix: readOnly transactions, StatelessSession (this chapter) |
+------------------------------------------------------------------+
```

---

## Hibernate Statistics

Enable statistics to see exactly what Hibernate is doing:

```properties
# application.properties
spring.jpa.properties.hibernate.generate_statistics=true
logging.level.org.hibernate.stat=DEBUG
```

```
Statistics Output Example:
+------------------------------------------------------------------+
|                                                                   |
|  Session Metrics:                                                 |
|    Statements prepared: 23                                        |
|    Statements closed: 23                                          |
|    Transactions: 5 (5 successful, 0 failed)                      |
|                                                                   |
|  Entity Metrics:                                                  |
|    Entities loaded: 150                                           |
|    Entities inserted: 12                                          |
|    Entities updated: 3                                            |
|    Entities deleted: 1                                            |
|                                                                   |
|  Query Metrics:                                                   |
|    Queries executed: 23                                           |
|    Max query time: 245ms ("SELECT e FROM Employee e ...")         |
|    Total query time: 890ms                                        |
|                                                                   |
|  L2 Cache Metrics:                                                |
|    Cache hits: 45                                                 |
|    Cache misses: 12                                               |
|    Hit rate: 78.9%                                                |
|                                                                   |
|  Key things to look for:                                          |
|  - Statements prepared >> Transactions = possible N+1             |
|  - Max query time > 100ms = slow query to investigate             |
|  - Entities loaded >> needed = over-fetching                      |
+------------------------------------------------------------------+
```

### Programmatic Statistics Access

```java
@RestController
@RequestMapping("/api/admin")
public class MonitoringController {

    @Autowired
    private EntityManagerFactory emf;

    @GetMapping("/hibernate-stats")
    public Map<String, Object> getStats() {
        Statistics stats = emf.unwrap(SessionFactory.class).getStatistics();

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("queriesExecuted", stats.getQueryExecutionCount());
        result.put("slowestQuery", stats.getQueryExecutionMaxTimeQueryString());
        result.put("slowestQueryTime", stats.getQueryExecutionMaxTime() + "ms");
        result.put("entitiesLoaded", stats.getEntityLoadCount());
        result.put("entitiesInserted", stats.getEntityInsertCount());
        result.put("entitiesUpdated", stats.getEntityUpdateCount());
        result.put("connectionsObtained", stats.getConnectCount());
        result.put("transactionsCompleted", stats.getTransactionCount());
        result.put("l2CacheHits", stats.getSecondLevelCacheHitCount());
        result.put("l2CacheMisses", stats.getSecondLevelCacheMissCount());

        return result;
    }
}
```

---

## Batch Inserts and Updates

By default, Hibernate sends one INSERT per entity. With batching, it groups multiple inserts into a single JDBC batch call.

```
Without Batching (default):
+------------------------------------------------------------------+
|                                                                   |
|  Inserting 1000 employees:                                        |
|  INSERT INTO employees (...) VALUES (...)   -- statement 1       |
|  INSERT INTO employees (...) VALUES (...)   -- statement 2       |
|  INSERT INTO employees (...) VALUES (...)   -- statement 3       |
|  ...                                                              |
|  INSERT INTO employees (...) VALUES (...)   -- statement 1000    |
|                                                                   |
|  1000 round-trips to the database!                                |
|  Each INSERT: send SQL -> database parses -> executes -> responds |
|                                                                   |
+------------------------------------------------------------------+

With Batching (batch_size = 50):
+------------------------------------------------------------------+
|                                                                   |
|  Inserting 1000 employees:                                        |
|  BATCH 1: 50 INSERTs sent together   -- 1 round-trip             |
|  BATCH 2: 50 INSERTs sent together   -- 1 round-trip             |
|  ...                                                              |
|  BATCH 20: 50 INSERTs sent together  -- 1 round-trip             |
|                                                                   |
|  20 round-trips instead of 1000!                                 |
|  50x fewer network round-trips.                                  |
+------------------------------------------------------------------+
```

### Configuration

```properties
# application.properties
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
spring.jpa.properties.hibernate.jdbc.batch_versioned_data=true
```

```
Batch Configuration Explained:
+------------------------------------------------------------------+
|                                                                   |
|  hibernate.jdbc.batch_size=50:                                    |
|  Group up to 50 statements in a single JDBC batch.               |
|                                                                   |
|  hibernate.order_inserts=true:                                    |
|  Reorder INSERT statements so same-entity inserts are grouped.   |
|  Without this: INSERT emp, INSERT dept, INSERT emp, INSERT dept   |
|  With this:    INSERT emp, INSERT emp, INSERT dept, INSERT dept   |
|  Grouping enables effective batching.                             |
|                                                                   |
|  hibernate.order_updates=true:                                    |
|  Same reordering for UPDATE statements.                           |
|                                                                   |
|  hibernate.jdbc.batch_versioned_data=true:                        |
|  Allow batching for entities with @Version (optimistic locking).  |
|                                                                   |
|  IMPORTANT: IDENTITY generation strategy DISABLES batching!      |
|  Hibernate must execute each INSERT immediately to get the ID.   |
|  Use SEQUENCE strategy for batch-heavy applications.              |
+------------------------------------------------------------------+
```

### Batch Insert Service

```java
@Service
public class BatchImportService {

    @PersistenceContext
    private EntityManager entityManager;

    @Transactional
    public int importEmployees(List<EmployeeData> dataList) {
        int batchSize = 50;
        int count = 0;

        for (int i = 0; i < dataList.size(); i++) {
            EmployeeData data = dataList.get(i);
            Employee employee = new Employee(data.getName(), data.getEmail());
            employee.setSalary(data.getSalary());
            entityManager.persist(employee);
            count++;

            if (count % batchSize == 0) {
                entityManager.flush();    // Send batch to DB
                entityManager.clear();    // Free memory
            }
        }

        entityManager.flush();
        entityManager.clear();

        return count;
    }
}
```

---

## JPQL Bulk Operations

For updating or deleting many rows, JPQL bulk operations bypass the persistence context entirely:

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // Bulk UPDATE — one SQL statement, no entity loading
    @Modifying(clearAutomatically = true)
    @Query("UPDATE Employee e SET e.salary = e.salary * :factor WHERE e.department.id = :deptId")
    int adjustSalaries(@Param("factor") BigDecimal factor, @Param("deptId") Long deptId);

    // Bulk DELETE — one SQL statement
    @Modifying(clearAutomatically = true)
    @Query("DELETE FROM Employee e WHERE e.active = false AND e.hireDate < :cutoff")
    int purgeInactive(@Param("cutoff") LocalDate cutoff);

    // Bulk status update
    @Modifying(clearAutomatically = true)
    @Query("UPDATE Employee e SET e.active = false WHERE e.department.id = :deptId")
    int deactivateDepartment(@Param("deptId") Long deptId);
}
```

```
Entity-by-Entity vs Bulk Operation:
+------------------------------------------------------------------+
|                                                                   |
|  Deactivating 500 employees in department 5:                      |
|                                                                   |
|  Entity-by-entity:                                                |
|  1. SELECT * FROM employees WHERE department_id = 5  (load 500)  |
|  2. For each: employee.setActive(false)               (in memory)|
|  3. Flush: 500 UPDATE statements                      (500 SQLs) |
|  Total: 501 SQL statements, 500 entities in memory               |
|                                                                   |
|  Bulk JPQL:                                                       |
|  UPDATE employees SET active = false WHERE department_id = 5      |
|  Total: 1 SQL statement, 0 entities in memory                    |
|                                                                   |
|  Bulk is ~500x faster for this operation.                        |
|  Use bulk for mass updates/deletes where entity logic is not     |
|  needed (no @PreUpdate callbacks, no cascade, no dirty checking). |
+------------------------------------------------------------------+
```

---

## Connection Pooling with HikariCP

Spring Boot uses HikariCP by default. Proper configuration prevents connection exhaustion.

```properties
# application.properties — HikariCP configuration
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.idle-timeout=300000
spring.datasource.hikari.max-lifetime=600000
spring.datasource.hikari.connection-timeout=30000
spring.datasource.hikari.leak-detection-threshold=60000
```

```
HikariCP Settings:
+------------------------------------------------------------------+
|                                                                   |
|  maximum-pool-size=10:                                            |
|  Maximum number of connections in the pool.                       |
|  Rule of thumb: connections = (2 * CPU cores) + disk spindles    |
|  For most apps: 10-20 is sufficient.                              |
|  More is NOT better — too many connections cause contention.      |
|                                                                   |
|  minimum-idle=5:                                                  |
|  Minimum connections kept ready (even when idle).                 |
|  Set equal to maximum-pool-size for stable performance.           |
|                                                                   |
|  connection-timeout=30000 (30s):                                  |
|  How long to wait for a connection from the pool.                 |
|  If pool is full and all connections are busy, wait up to 30s.   |
|  After 30s: throw SQLException (connection timeout).              |
|                                                                   |
|  leak-detection-threshold=60000 (60s):                            |
|  If a connection is not returned within 60s, log a warning.       |
|  Helps detect connection leaks (forgotten transactions).          |
|                                                                   |
+------------------------------------------------------------------+

Connection Pool Lifecycle:
+------------------------------------------------------------------+
|                                                                   |
|  Request 1  ----+                                                 |
|  Request 2  ----|---> [Connection Pool]                           |
|  Request 3  ----+     [C1] [C2] [C3] [C4] [C5] ... [C10]        |
|  Request 4  ----+            |                                    |
|  ...                         v                                    |
|                         Database                                  |
|                                                                   |
|  Each @Transactional method:                                      |
|  1. Borrows a connection from the pool                            |
|  2. Uses it for queries and updates                               |
|  3. Returns it when transaction commits/rollbacks                 |
|                                                                   |
|  If all 10 connections are busy:                                  |
|  Request 11 WAITS (up to connection-timeout)                      |
|  --> This is why short transactions matter!                       |
+------------------------------------------------------------------+
```

---

## Slow Query Logging

### Hibernate Slow Query Log

```properties
# Log queries slower than 500ms
spring.jpa.properties.hibernate.session.events.log.LOG_QUERIES_SLOWER_THAN_MS=500
logging.level.org.hibernate.SQL_SLOW=INFO
```

### SQL Logging for Development

```properties
# Show all SQL with formatting (development only)
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# Better: use logging framework (includes parameters)
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.orm.jdbc.bind=TRACE
```

```
SQL Logging Output:
+------------------------------------------------------------------+
|                                                                   |
|  Hibernate:                                                       |
|      select                                                       |
|          e1_0.id,                                                 |
|          e1_0.name,                                               |
|          e1_0.email,                                              |
|          e1_0.salary                                              |
|      from                                                         |
|          employees e1_0                                           |
|      where                                                        |
|          e1_0.department_id=?                                     |
|                                                                   |
|  Binding: [1]     <-- parameter value (with TRACE level)          |
|                                                                   |
|  Look for:                                                        |
|  - Same query repeated many times (N+1)                           |
|  - SELECT * when you need few columns (over-fetching)             |
|  - Missing WHERE clause (full table scan)                         |
|  - Queries without LIMIT (unbounded results)                      |
+------------------------------------------------------------------+
```

---

## Database Indexing

Indexes speed up WHERE, JOIN, and ORDER BY operations. Without indexes, the database scans every row.

```
Index Impact:
+------------------------------------------------------------------+
|                                                                   |
|  employees table: 1,000,000 rows                                  |
|                                                                   |
|  Query: SELECT * FROM employees WHERE email = 'alice@co.com'      |
|                                                                   |
|  Without index:                                                   |
|  Full table scan: checks ALL 1,000,000 rows                      |
|  Time: ~500ms                                                     |
|                                                                   |
|  With index on email:                                             |
|  B-tree lookup: finds the row directly                            |
|  Time: ~1ms                                                       |
|                                                                   |
|  500x faster!                                                     |
+------------------------------------------------------------------+
```

### When to Add Indexes

```
Index These Columns:
+------------------------------------------------------------------+
|                                                                   |
|  Always index:                                                    |
|  - Primary keys (automatic)                                       |
|  - Foreign keys (department_id, customer_id)                      |
|  - Unique constraints (email, username)                           |
|  - Columns in WHERE clauses used frequently                      |
|  - Columns in ORDER BY for paginated queries                     |
|  - Columns in JOIN conditions                                     |
|                                                                   |
|  Consider indexing:                                               |
|  - Status columns (active, status) if filtered often              |
|  - Date columns (created_at) if sorted/filtered by date          |
|  - Composite indexes for multi-column WHERE clauses              |
|                                                                   |
|  Do NOT index:                                                    |
|  - Columns rarely used in queries                                 |
|  - Columns with very low cardinality (boolean with 50/50 split)  |
|  - Tables with very few rows (< 1000)                            |
|  - Columns that are updated very frequently                      |
|    (indexes slow down INSERT/UPDATE)                              |
+------------------------------------------------------------------+
```

### Creating Indexes with JPA

```java
@Entity
@Table(name = "employees", indexes = {
    @Index(name = "idx_employee_email", columnList = "email"),
    @Index(name = "idx_employee_department", columnList = "department_id"),
    @Index(name = "idx_employee_active_hire",
           columnList = "active, hire_date")  // Composite index
})
public class Employee {
    // ...
}
```

Or in Flyway migrations (recommended for production):

```sql
-- V10__Add_performance_indexes.sql
CREATE INDEX idx_employee_email ON employees(email);
CREATE INDEX idx_employee_department ON employees(department_id);
CREATE INDEX idx_employee_active_hire ON employees(active, hire_date);
CREATE INDEX idx_order_customer_status ON orders(customer_id, status);
CREATE INDEX idx_order_created ON orders(created_at);
```

---

## StatelessSession for High-Throughput

Hibernate's `StatelessSession` bypasses the persistence context entirely — no caching, no dirty checking, no cascading:

```java
@Service
public class BulkExportService {

    @Autowired
    private EntityManagerFactory emf;

    public void exportAllEmployees(Writer writer) {
        SessionFactory sessionFactory = emf.unwrap(SessionFactory.class);

        try (StatelessSession session = sessionFactory.openStatelessSession()) {
            ScrollableResults<Employee> results = session
                .createQuery("FROM Employee e ORDER BY e.id", Employee.class)
                .setFetchSize(100)
                .scroll(ScrollMode.FORWARD_ONLY);

            while (results.next()) {
                Employee employee = results.get();
                writer.write(employee.toCsvLine());
                // No persistence context = no memory buildup
                // Can process millions of rows
            }
        }
    }
}
```

```
Session vs StatelessSession:
+------------------------------------------------------------------+
|                                                                   |
|  Regular Session (EntityManager):                                 |
|  + Dirty checking (auto-save changes)                             |
|  + First-level cache (identity guarantee)                         |
|  + Cascading operations                                           |
|  + Lazy loading                                                   |
|  - Memory overhead (snapshots, managed entities)                  |
|  - Slow for bulk operations                                       |
|                                                                   |
|  StatelessSession:                                                |
|  + No persistence context (zero memory overhead)                  |
|  + No dirty checking (fast)                                       |
|  + Processes millions of rows without OutOfMemoryError           |
|  - No caching (every access hits DB)                              |
|  - No cascading (manage relationships manually)                   |
|  - No lazy loading (load everything upfront)                      |
|  - Must call insert/update/delete explicitly                      |
|                                                                   |
|  Use StatelessSession for:                                        |
|  - Batch imports/exports                                          |
|  - ETL processes                                                  |
|  - Data migration scripts                                         |
|  - Report generation over large datasets                          |
+------------------------------------------------------------------+
```

---

## Performance Checklist

```
Pre-Production Performance Checklist:
+------------------------------------------------------------------+
|                                                                   |
|  [ ] All @ManyToOne set to FetchType.LAZY                         |
|  [ ] All @OneToOne set to FetchType.LAZY                          |
|  [ ] N+1 queries identified and fixed (JOIN FETCH / @EntityGraph) |
|  [ ] default_batch_fetch_size configured (16 or 32)               |
|  [ ] JDBC batch_size set for bulk operations (50)                 |
|  [ ] order_inserts and order_updates enabled                      |
|  [ ] Read-only methods annotated with @Transactional(readOnly)    |
|  [ ] Projections/DTOs used for list endpoints                     |
|  [ ] Bulk operations use JPQL UPDATE/DELETE when possible         |
|  [ ] Indexes on FK columns, frequent WHERE/ORDER BY columns      |
|  [ ] HikariCP pool size appropriate for workload                  |
|  [ ] Slow query logging enabled                                   |
|  [ ] Statistics enabled in staging (disabled in production)       |
|  [ ] spring.jpa.open-in-view=false                                |
|  [ ] ddl-auto=validate (Flyway manages schema)                   |
|  [ ] Connection leak detection enabled                            |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Not enabling JDBC batching**: Default batch_size is 1 (no batching). Set `hibernate.jdbc.batch_size=50` for any application that does bulk writes.

2. **Using IDENTITY generation with batching**: `GenerationType.IDENTITY` forces immediate INSERT to get the generated ID, disabling batching. Use `SEQUENCE` for batch-heavy operations.

3. **Over-sizing the connection pool**: 100 connections is almost never better than 10-20. More connections mean more database memory, more context switching, and more contention.

4. **Not indexing foreign key columns**: JPA does not create FK indexes automatically (some databases do, some do not). Always create indexes on FK columns explicitly.

5. **Disabling SQL logging in development**: You cannot optimize what you cannot see. Always enable SQL logging during development to catch N+1 and other issues early.

6. **Using entity-by-entity operations for mass updates**: Updating 10,000 rows by loading each entity, modifying it, and relying on dirty checking generates 10,001 SQL statements. Use JPQL bulk UPDATE instead (1 SQL statement).

---

## Best Practices

1. **Enable JDBC batching globally**: Set `batch_size=50`, `order_inserts=true`, `order_updates=true` as defaults. They help even for small operations.

2. **Use JPQL bulk operations for mass updates/deletes**: `UPDATE Employee e SET e.active = false WHERE ...` is orders of magnitude faster than loading and modifying entities individually.

3. **Set `default_batch_fetch_size=16`**: This global setting reduces N+1 without changing any code. Good baseline optimization.

4. **Index every FK column**: `CREATE INDEX idx_employee_dept ON employees(department_id)`. This speeds up JOINs and cascade deletes.

5. **Monitor with Hibernate statistics in staging**: Enable statistics, run load tests, identify slowest queries and highest query counts.

6. **Keep transactions short**: Avoid calling external services inside `@Transactional`. Each second of transaction time is a second a connection is held.

---

## Summary

- **Hibernate statistics** reveal query counts, entity operations, cache hit rates, and slowest queries. Essential for identifying bottlenecks.

- **JDBC batching** groups multiple INSERT/UPDATE statements into single round-trips. Configure `batch_size=50` with `order_inserts=true`.

- **JPQL bulk operations** (`UPDATE`, `DELETE`) execute a single SQL statement instead of loading and modifying entities individually. Use for mass operations.

- **HikariCP** connection pooling: size the pool based on CPU cores, not request volume. Enable leak detection. Keep transactions short.

- **Slow query logging** catches queries that take too long. Enable with `LOG_QUERIES_SLOWER_THAN_MS`.

- **Database indexes** on FK columns, WHERE columns, and ORDER BY columns prevent full table scans.

- **StatelessSession** bypasses the persistence context for high-throughput operations with zero memory overhead.

---

## Interview Questions

**Q1: What is the most common Hibernate performance problem?**

The N+1 query problem. Loading N entities and accessing their lazy relationships triggers N additional queries (1 for the parent list + N for each relationship). Fix with JOIN FETCH, @EntityGraph, or @BatchSize.

**Q2: How does JDBC batching improve performance?**

Instead of sending each INSERT/UPDATE as a separate network round-trip, batching groups multiple statements (e.g., 50) into a single JDBC batch call. This reduces network overhead by a factor of the batch size. Configure with `hibernate.jdbc.batch_size`.

**Q3: Why does GenerationType.IDENTITY disable JDBC batching?**

IDENTITY relies on the database to generate the ID via auto-increment, which requires executing each INSERT immediately to retrieve the generated value. Batching requires deferring execution, which conflicts with IDENTITY. Use SEQUENCE instead.

**Q4: How do you size a connection pool?**

A good starting formula is `connections = (2 * CPU cores) + effective_spindle_count`. For most applications, 10-20 connections is sufficient. More connections cause contention and waste database resources. Monitor connection wait times and adjust.

**Q5: When should you use StatelessSession instead of EntityManager?**

For high-throughput batch operations: importing millions of rows, ETL processes, bulk exports, and report generation over large datasets. StatelessSession has no persistence context (zero memory overhead), no dirty checking, and no caching — making it suitable for processing unlimited data without OutOfMemoryError.

**Q6: What columns should you always index?**

Primary keys (automatic), foreign key columns (not always automatic), unique constraint columns, columns frequently used in WHERE clauses, columns used in ORDER BY for paginated queries, and columns used in JOIN conditions.

---

## Practice Exercises

**Exercise 1: Batch Insert Performance**
Insert 10,000 employees with and without JDBC batching. Measure the time difference. Use `System.nanoTime()` before and after. Enable SQL logging to verify batching is working.

**Exercise 2: Bulk vs Entity Update**
Deactivate 500 employees in a department two ways: (a) load all, set active=false, let dirty checking update; (b) JPQL `UPDATE Employee e SET e.active = false WHERE ...`. Compare query counts and execution time.

**Exercise 3: Index Impact**
Create a table with 100,000 rows. Query by a non-indexed column and measure time. Add an index. Query again and measure. Compare the difference.

**Exercise 4: Connection Pool Monitoring**
Set `maximum-pool-size=2` and `leak-detection-threshold=5000`. Create a service that holds a transaction for 10 seconds. Call it 3 times concurrently. Observe the connection timeout and leak detection warnings.

**Exercise 5: Statistics Analysis**
Enable Hibernate statistics. Run your application's main use cases. Review the statistics output and identify: (a) the slowest query, (b) the highest query count (potential N+1), (c) cache hit rate.

---

## What Is Next?

In the next chapter, we will put everything together and build a **Complete REST API with Spring Boot and Hibernate**. You will create a full CRUD API with proper DTOs, validation, error handling, pagination, and all the best practices from this book.
