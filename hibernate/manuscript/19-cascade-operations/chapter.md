# Chapter 19: Cascade Operations and Lifecycle Propagation

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand what cascading means in JPA relationships
- Use each CascadeType (PERSIST, MERGE, REMOVE, REFRESH, DETACH, ALL)
- Explain the difference between CascadeType.REMOVE and orphanRemoval
- Apply lifecycle callbacks (@PrePersist, @PostPersist, @PreUpdate, @PostUpdate, @PreRemove, @PostRemove)
- Create reusable @EntityListeners for cross-cutting concerns
- Know when to cascade and when not to cascade
- Avoid dangerous cascade configurations that cause data loss
- Implement audit logging with lifecycle callbacks

---

## What Is Cascading?

Cascading means propagating a persistence operation from a parent entity to its related child entities. When you save, delete, or refresh a parent, the same operation can automatically apply to its children.

```
Cascading Concept:
+------------------------------------------------------------------+
|                                                                   |
|  Without Cascade:                                                 |
|  Order order = new Order();                                       |
|  OrderItem item1 = new OrderItem("Widget", 2);                   |
|  OrderItem item2 = new OrderItem("Gadget", 1);                   |
|  order.addItem(item1);                                            |
|  order.addItem(item2);                                            |
|                                                                   |
|  orderRepository.save(order);   // Saves order only               |
|  itemRepository.save(item1);    // Must save each item manually!  |
|  itemRepository.save(item2);    // Tedious and error-prone        |
|                                                                   |
|  With Cascade:                                                    |
|  @OneToMany(cascade = CascadeType.ALL)                            |
|  private List<OrderItem> items;                                   |
|                                                                   |
|  orderRepository.save(order);   // Saves order AND all items!     |
|  // One call does everything.                                     |
+------------------------------------------------------------------+
```

```
Cascade Flow:
+------------------------------------------------------------------+
|                                                                   |
|  Operation on Parent      CascadeType      Effect on Children     |
|  ----------------------------------------------------------------|
|  persist(order)           PERSIST           persist(item1)        |
|                                             persist(item2)        |
|                                                                   |
|  merge(order)             MERGE             merge(item1)          |
|                                             merge(item2)          |
|                                                                   |
|  remove(order)            REMOVE            remove(item1)         |
|                                             remove(item2)         |
|                                                                   |
|  refresh(order)           REFRESH           refresh(item1)        |
|                                             refresh(item2)        |
|                                                                   |
|  detach(order)            DETACH            detach(item1)         |
|                                             detach(item2)         |
|                                                                   |
|  ALL = all of the above                                           |
+------------------------------------------------------------------+
```

---

## CascadeType.PERSIST

Propagates the `persist` (save) operation from parent to children:

```java
@Entity
public class Order {

    @OneToMany(mappedBy = "order", cascade = CascadeType.PERSIST)
    private List<OrderItem> items = new ArrayList<>();

    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }
}
```

```java
// One save() persists the order AND all items
Order order = new Order("ORD-001");
order.addItem(new OrderItem("Widget", 2, new BigDecimal("9.99")));
order.addItem(new OrderItem("Gadget", 1, new BigDecimal("24.99")));
orderRepository.save(order);

// SQL generated:
// INSERT INTO orders (order_number) VALUES ('ORD-001')
// INSERT INTO order_items (name, quantity, price, order_id) VALUES ('Widget', 2, 9.99, 1)
// INSERT INTO order_items (name, quantity, price, order_id) VALUES ('Gadget', 1, 24.99, 1)
```

```
CascadeType.PERSIST Use Cases:
+------------------------------------------------------------------+
|                                                                   |
|  USE when: Parent creates children as part of its lifecycle       |
|  - Order creates OrderItems                                       |
|  - Post creates Comments                                          |
|  - Invoice creates LineItems                                      |
|                                                                   |
|  DO NOT USE when: Children exist independently                    |
|  - Department does not create Employees                           |
|    (employees are hired separately)                               |
|  - Student does not create Courses                                |
|    (courses exist before enrollment)                              |
+------------------------------------------------------------------+
```

---

## CascadeType.MERGE

Propagates the `merge` operation — reattaches detached parent and children:

```java
@Entity
public class Order {
    @OneToMany(mappedBy = "order", cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    private List<OrderItem> items = new ArrayList<>();
}
```

```java
// Load order in one transaction
Order detachedOrder = orderService.getOrder(1L);
// Transaction ends, order is DETACHED

// Modify in a different context (e.g., REST API receives modified order)
detachedOrder.getItems().get(0).setQuantity(5);
detachedOrder.addItem(new OrderItem("New Item", 1, new BigDecimal("14.99")));

// Merge back in a new transaction
orderService.updateOrder(detachedOrder);

@Transactional
public Order updateOrder(Order detachedOrder) {
    return orderRepository.save(detachedOrder);  // Calls merge internally
    // Cascade MERGE: merges order AND all items
    // Modified items get UPDATE, new items get INSERT
}
```

---

## CascadeType.REMOVE

Propagates the `remove` (delete) operation — deleting the parent deletes all children:

```java
@Entity
public class Order {
    @OneToMany(mappedBy = "order",
               cascade = {CascadeType.PERSIST, CascadeType.MERGE, CascadeType.REMOVE})
    private List<OrderItem> items = new ArrayList<>();
}
```

```java
// Deleting the order also deletes all items
orderRepository.deleteById(1L);

// SQL generated:
// DELETE FROM order_items WHERE order_id = 1   (children first)
// DELETE FROM orders WHERE id = 1              (then parent)
```

```
CascadeType.REMOVE — Danger Zone:
+------------------------------------------------------------------+
|                                                                   |
|  SAFE to cascade REMOVE:                                          |
|  - Parent OWNS children completely                                |
|  - Children cannot exist without parent                           |
|  - Deleting parent means children are meaningless                 |
|  Examples: Order->Items, Post->Comments, Invoice->Lines           |
|                                                                   |
|  DANGEROUS to cascade REMOVE:                                     |
|  - Children are SHARED between parents                            |
|  - Children have independent lifecycles                           |
|  - Deleting parent should NOT delete children                     |
|  Examples:                                                        |
|  - Department->Employees (employees should transfer, not die)     |
|  - Student->Courses (courses serve other students)                |
|  - User->Roles (roles are shared, must not be deleted)            |
|                                                                   |
|  NEVER use CascadeType.REMOVE on @ManyToMany!                    |
|  It would delete the shared entity, not just the link.            |
+------------------------------------------------------------------+
```

---

## CascadeType.REFRESH and CascadeType.DETACH

Less commonly used but useful in specific scenarios:

```java
// REFRESH: Reloads entity state from database, discarding in-memory changes
@OneToMany(cascade = CascadeType.REFRESH)
// When you call entityManager.refresh(order), items are also refreshed

// DETACH: Removes entity from persistence context
@OneToMany(cascade = CascadeType.DETACH)
// When you call entityManager.detach(order), items are also detached
```

---

## CascadeType.ALL

Shorthand for all cascade types combined:

```java
@OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
private List<OrderItem> items;

// Equivalent to:
@OneToMany(mappedBy = "order",
    cascade = {CascadeType.PERSIST, CascadeType.MERGE,
               CascadeType.REMOVE, CascadeType.REFRESH,
               CascadeType.DETACH})
private List<OrderItem> items;
```

```
When to Use CascadeType.ALL:
+------------------------------------------------------------------+
|                                                                   |
|  Use ALL when children are FULLY OWNED by parent:                 |
|  - Children created with parent                                   |
|  - Children updated with parent                                   |
|  - Children deleted with parent                                   |
|  - Children never shared or moved to another parent               |
|                                                                   |
|  Common pattern:                                                  |
|  @OneToMany(mappedBy = "parent",                                  |
|             cascade = CascadeType.ALL,                             |
|             orphanRemoval = true)                                  |
|  --> Complete lifecycle ownership                                  |
|                                                                   |
|  Use {PERSIST, MERGE} when children are NOT fully owned:          |
|  - Children may be moved between parents                          |
|  - Deleting parent should NOT delete children                     |
|  - Children have independent lifecycles                           |
+------------------------------------------------------------------+
```

---

## orphanRemoval vs CascadeType.REMOVE

These are often confused. They handle different scenarios:

```
orphanRemoval vs CascadeType.REMOVE:
+------------------------------------------------------------------+
|                                                                   |
|  CascadeType.REMOVE:                                              |
|  Triggers when: PARENT is deleted                                 |
|  Effect: Children are deleted along with parent                   |
|                                                                   |
|  orderRepository.delete(order);                                   |
|  --> Deletes order AND all items                                  |
|                                                                   |
|  orphanRemoval = true:                                            |
|  Triggers when: CHILD is removed from parent's collection         |
|  Effect: Removed child is deleted from database                   |
|                                                                   |
|  order.removeItem(item);                                          |
|  --> item is deleted from database (it is an "orphan")            |
|  --> Order itself is NOT deleted                                  |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  Example showing the difference:                                  |
|                                                                   |
|  Without orphanRemoval:                                           |
|  order.getItems().remove(item);                                   |
|  --> item.order_id set to NULL (item still exists in DB)          |
|  --> Orphaned row with no parent!                                 |
|                                                                   |
|  With orphanRemoval = true:                                       |
|  order.getItems().remove(item);                                   |
|  --> DELETE FROM order_items WHERE id = ?                         |
|  --> Item completely removed from database                        |
|                                                                   |
|  orphanRemoval INCLUDES CascadeType.REMOVE behavior.             |
|  If parent is deleted, children are also deleted.                 |
+------------------------------------------------------------------+
```

```java
@Entity
public class Order {

    @OneToMany(mappedBy = "order",
               cascade = CascadeType.ALL,
               orphanRemoval = true)        // Delete items removed from list
    private List<OrderItem> items = new ArrayList<>();

    public void removeItem(OrderItem item) {
        items.remove(item);         // Triggers orphanRemoval
        item.setOrder(null);        // Clear the relationship
    }

    public void clearItems() {
        items.clear();              // All items become orphans -> all deleted
    }

    public void replaceItems(List<OrderItem> newItems) {
        items.clear();                          // Delete old items (orphans)
        newItems.forEach(this::addItem);        // Add new items (cascade persist)
    }
}
```

---

## JPA Lifecycle Callbacks

JPA provides annotations that let you hook into entity state changes. These methods are called automatically by Hibernate at specific points in the entity lifecycle.

```
Lifecycle Callback Timing:
+------------------------------------------------------------------+
|                                                                   |
|  persist(entity)                                                  |
|       |                                                           |
|       v                                                           |
|  @PrePersist    --> Before INSERT SQL is generated                |
|       |             Set defaults, validate, generate timestamps   |
|       v                                                           |
|  INSERT SQL executed                                              |
|       |                                                           |
|       v                                                           |
|  @PostPersist   --> After INSERT completes                        |
|                     ID is available, log creation                 |
|                                                                   |
|  modify managed entity                                            |
|       |                                                           |
|       v                                                           |
|  @PreUpdate     --> Before UPDATE SQL is generated                |
|       |             Update timestamps, validate changes           |
|       v                                                           |
|  UPDATE SQL executed                                              |
|       |                                                           |
|       v                                                           |
|  @PostUpdate    --> After UPDATE completes                        |
|                     Log changes, trigger notifications            |
|                                                                   |
|  remove(entity)                                                   |
|       |                                                           |
|       v                                                           |
|  @PreRemove     --> Before DELETE SQL is generated                |
|       |             Cleanup, validate deletion is allowed         |
|       v                                                           |
|  DELETE SQL executed                                              |
|       |                                                           |
|       v                                                           |
|  @PostRemove    --> After DELETE completes                        |
|                     Log deletion, cleanup external resources      |
|                                                                   |
|  @PostLoad      --> After entity is loaded from database          |
|                     Initialize transient fields, compute values   |
+------------------------------------------------------------------+
```

### Using Lifecycle Callbacks on the Entity

```java
@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private BigDecimal price;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Transient  // Not persisted — computed after loading
    private String displayPrice;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    @PostLoad
    protected void onLoad() {
        displayPrice = "$" + price.setScale(2).toPlainString();
    }

    @PreRemove
    protected void onRemove() {
        System.out.println("About to delete product: " + name);
    }
}
```

### Rules for Lifecycle Callback Methods

```
Lifecycle Callback Rules:
+------------------------------------------------------------------+
|                                                                   |
|  1. Must be void return type                                      |
|  2. Must take no arguments (when on the entity itself)            |
|  3. Can be any access modifier (public, protected, private)       |
|  4. Should NOT call EntityManager methods                         |
|     (no persist, merge, remove, or queries inside callbacks)      |
|  5. Should NOT modify other entities                              |
|  6. Should be fast (called synchronously, blocks the operation)   |
|  7. Exceptions thrown will roll back the transaction               |
|                                                                   |
|  Valid uses:                                                       |
|  - Set timestamps                                                  |
|  - Validate data                                                   |
|  - Initialize computed fields                                      |
|  - Log events                                                      |
|                                                                   |
|  Invalid uses (will cause issues):                                |
|  - Load or save other entities                                    |
|  - Call repository methods                                        |
|  - Start new transactions                                         |
+------------------------------------------------------------------+
```

---

## @EntityListeners — Reusable Lifecycle Logic

Instead of putting lifecycle callbacks on every entity, extract them into a separate listener class:

```java
// Reusable audit listener
public class AuditListener {

    @PrePersist
    public void setCreatedAt(Object entity) {
        if (entity instanceof Auditable auditable) {
            auditable.setCreatedAt(LocalDateTime.now());
            auditable.setUpdatedAt(LocalDateTime.now());
        }
    }

    @PreUpdate
    public void setUpdatedAt(Object entity) {
        if (entity instanceof Auditable auditable) {
            auditable.setUpdatedAt(LocalDateTime.now());
        }
    }
}
```

```java
// Interface for auditable entities
public interface Auditable {
    void setCreatedAt(LocalDateTime createdAt);
    void setUpdatedAt(LocalDateTime updatedAt);
}
```

```java
// Apply the listener to any entity
@Entity
@Table(name = "products")
@EntityListeners(AuditListener.class)    // JPA standard
public class Product implements Auditable {

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Override
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}

@Entity
@Table(name = "orders")
@EntityListeners(AuditListener.class)    // Same listener, different entity
public class Order implements Auditable {
    // Same audit fields...
}
```

### Spring Data JPA Auditing (Easier Approach)

Spring Data JPA provides built-in auditing support that is simpler than manual `@EntityListeners`:

```java
// 1. Enable auditing
@Configuration
@EnableJpaAuditing
public class JpaConfig {
}

// 2. Use Spring's audit annotations
@Entity
@EntityListeners(AuditingEntityListener.class)  // Spring's listener
public class Product {

    @CreatedDate                         // Spring Data annotation
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate                    // Spring Data annotation
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @CreatedBy                           // Spring Data annotation
    @Column(name = "created_by", updatable = false)
    private String createdBy;

    @LastModifiedBy                      // Spring Data annotation
    @Column(name = "modified_by")
    private String modifiedBy;
}

// 3. Provide the current user (for @CreatedBy / @LastModifiedBy)
@Component
public class AuditorAwareImpl implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        // In a real app, get from SecurityContext:
        // return Optional.of(SecurityContextHolder.getContext()
        //     .getAuthentication().getName());
        return Optional.of("system");
    }
}
```

```
Spring Data Auditing vs Manual Callbacks:
+------------------------------------------------------------------+
|                                                                   |
|  Manual @PrePersist / @PreUpdate:                                 |
|  - More control                                                   |
|  - Works without Spring                                           |
|  - Must implement in each entity or via listener                  |
|                                                                   |
|  Spring Data @CreatedDate / @LastModifiedDate:                    |
|  - Less code                                                      |
|  - Built-in @CreatedBy / @LastModifiedBy support                  |
|  - Just add annotations + enable auditing                         |
|  - Recommended for Spring Boot applications                      |
+------------------------------------------------------------------+
```

---

## Practical Example: Audit Trail with Callbacks

```java
// Audit log entity
@Entity
@Table(name = "audit_logs")
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "entity_type", nullable = false)
    private String entityType;

    @Column(name = "entity_id", nullable = false)
    private Long entityId;

    @Column(nullable = false)
    private String action;  // CREATED, UPDATED, DELETED

    @Column(name = "performed_at", nullable = false)
    private LocalDateTime performedAt;

    @Column(name = "performed_by")
    private String performedBy;

    public AuditLog() {}

    public AuditLog(String entityType, Long entityId, String action) {
        this.entityType = entityType;
        this.entityId = entityId;
        this.action = action;
        this.performedAt = LocalDateTime.now();
        this.performedBy = "system"; // Replace with actual user
    }

    // Getters...
}
```

```java
// Service that manually creates audit logs
// (Cannot use EntityManager in lifecycle callbacks,
//  so use application events or service-level logging)
@Service
public class ProductService {

    private final ProductRepository productRepository;
    private final AuditLogRepository auditLogRepository;

    @Transactional
    public Product createProduct(String name, BigDecimal price) {
        Product product = productRepository.save(new Product(name, price));

        auditLogRepository.save(
            new AuditLog("Product", product.getId(), "CREATED"));

        return product;
    }

    @Transactional
    public Product updateProduct(Long id, String name, BigDecimal price) {
        Product product = productRepository.findById(id).orElseThrow();
        product.setName(name);
        product.setPrice(price);

        auditLogRepository.save(
            new AuditLog("Product", product.getId(), "UPDATED"));

        return product;
    }

    @Transactional
    public void deleteProduct(Long id) {
        Product product = productRepository.findById(id).orElseThrow();

        auditLogRepository.save(
            new AuditLog("Product", id, "DELETED"));

        productRepository.delete(product);
    }
}
```

---

## Cascade Decision Framework

```
Complete Cascade Decision Guide:
+------------------------------------------------------------------+
|                                                                   |
|  Question 1: Does the parent CREATE the children?                 |
|       |                                                           |
|    YES --> Include CascadeType.PERSIST                            |
|    NO  --> Do not include PERSIST                                 |
|            (save children independently)                          |
|                                                                   |
|  Question 2: Are children modified through the parent?            |
|       |                                                           |
|    YES --> Include CascadeType.MERGE                              |
|    NO  --> Do not include MERGE                                   |
|                                                                   |
|  Question 3: Should deleting the parent delete children?          |
|       |                                                           |
|    YES --> Is the child SHARED with other parents?                |
|       |       |                                                   |
|       |    YES --> DO NOT cascade REMOVE! (would delete shared)   |
|       |    NO  --> Include CascadeType.REMOVE                     |
|       |                                                           |
|    NO  --> Do not include REMOVE                                  |
|                                                                   |
|  Question 4: Should removing a child from the collection          |
|              delete it from the database?                          |
|       |                                                           |
|    YES --> Add orphanRemoval = true                               |
|    NO  --> Leave orphanRemoval = false (default)                  |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  Common Patterns:                                                 |
|                                                                   |
|  Fully owned children (Order->Items):                             |
|    cascade = ALL, orphanRemoval = true                            |
|                                                                   |
|  Parent creates but does not delete children:                     |
|    cascade = {PERSIST, MERGE}                                     |
|                                                                   |
|  Independent entities with reference only:                        |
|    No cascade at all                                              |
|                                                                   |
|  @ManyToMany (shared entities):                                   |
|    cascade = {PERSIST, MERGE} at most                             |
|    NEVER cascade REMOVE                                           |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Using CascadeType.ALL on @ManyToMany**: This includes REMOVE, which deletes shared entities. A student deletion would delete courses that other students are enrolled in. Use `{PERSIST, MERGE}` or no cascade.

2. **Using CascadeType.REMOVE on non-owned children**: If employees can transfer departments, `cascade = REMOVE` on `Department.employees` would delete transferred employees when the old department is deleted.

3. **Calling EntityManager methods inside lifecycle callbacks**: `@PrePersist`, `@PreUpdate`, etc. should not call `entityManager.persist()`, `merge()`, or run queries. This causes unpredictable behavior and potential infinite loops.

4. **Confusing orphanRemoval with CascadeType.REMOVE**: REMOVE triggers on parent deletion. orphanRemoval triggers on child removal from the collection. They handle different scenarios but orphanRemoval includes REMOVE behavior.

5. **Using orphanRemoval with @ManyToMany**: Removing a student from a course's student list should not delete the student. orphanRemoval is for owned children only.

6. **Forgetting that cascade operates on the relationship, not the entity**: Cascade is defined on the `@OneToMany`, `@ManyToOne`, etc. annotation. It affects how operations propagate through that specific relationship.

---

## Best Practices

1. **Default cascade for owned children**: Use `cascade = CascadeType.ALL, orphanRemoval = true` for children that cannot exist without their parent (OrderItem, Comment, LineItem).

2. **Minimal cascade for shared references**: Use `cascade = {PERSIST, MERGE}` or no cascade for entities that have independent lifecycles (Employee, Course, Role).

3. **Never cascade REMOVE on @ManyToMany**: The shared entity would be deleted, affecting all other relationships.

4. **Use Spring Data JPA auditing for timestamps**: `@CreatedDate` and `@LastModifiedDate` with `@EnableJpaAuditing` is cleaner than manual `@PrePersist`/`@PreUpdate`.

5. **Keep lifecycle callbacks simple and fast**: Set timestamps, validate data, initialize fields. Do not perform database operations or call external services.

6. **Use @MappedSuperclass for common audit fields**: Put `createdAt`, `updatedAt`, `createdBy`, `modifiedBy` in a base class so all entities inherit them.

---

## Summary

In this chapter, you learned how to manage operation propagation and entity lifecycle events:

- **CascadeType.PERSIST**: Saves children when parent is saved. Use for parent-creates-children patterns.
- **CascadeType.MERGE**: Reattaches children when parent is merged. Use with PERSIST for full write propagation.
- **CascadeType.REMOVE**: Deletes children when parent is deleted. Only for fully owned children.
- **CascadeType.ALL**: All cascade types combined. Use with orphanRemoval for complete ownership.
- **orphanRemoval**: Deletes children removed from the collection (not just when parent is deleted). Includes REMOVE behavior.
- **Lifecycle callbacks** (`@PrePersist`, `@PostLoad`, etc.) hook into entity state changes for timestamps, validation, and computed fields.
- **@EntityListeners** extract lifecycle logic into reusable classes.
- **Spring Data JPA auditing** (`@CreatedDate`, `@LastModifiedDate`, `@EnableJpaAuditing`) provides the simplest approach for audit timestamps and user tracking.

---

## Interview Questions

**Q1: What is the difference between CascadeType.REMOVE and orphanRemoval?**

`CascadeType.REMOVE` deletes children when the PARENT is deleted. `orphanRemoval` deletes children when they are removed from the PARENT'S COLLECTION (the parent still exists). orphanRemoval also includes REMOVE behavior. Example: `order.removeItem(item)` triggers orphanRemoval (deletes item); `orderRepository.delete(order)` triggers both.

**Q2: When should you NOT use CascadeType.ALL?**

When children are shared between parents or have independent lifecycles. Examples: Employees (can transfer departments), Courses (shared by students), Roles (shared by users). Using ALL would cascade REMOVE, deleting shared entities when one parent is deleted.

**Q3: What are JPA lifecycle callbacks and name three of them?**

Lifecycle callbacks are methods annotated with JPA annotations that are called automatically at specific points in an entity's lifecycle. Examples: `@PrePersist` (before INSERT), `@PreUpdate` (before UPDATE), `@PostLoad` (after SELECT), `@PreRemove` (before DELETE), `@PostPersist` (after INSERT).

**Q4: What restrictions apply to lifecycle callback methods?**

They must return void, take no arguments (when on the entity), should not call EntityManager methods (persist, merge, remove, queries), should not modify other entities, and should be fast. Exceptions thrown inside callbacks will roll back the transaction.

**Q5: How does Spring Data JPA auditing work?**

Enable with `@EnableJpaAuditing`, add `@EntityListeners(AuditingEntityListener.class)` to entities, and annotate fields with `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy`. For user tracking, implement `AuditorAware<String>` as a Spring bean to provide the current user.

**Q6: What cascade types are safe for @ManyToMany?**

Only `PERSIST` and `MERGE` are safe. Never use `REMOVE`, `ALL`, or `orphanRemoval` on `@ManyToMany` because they would delete shared entities, not just the association.

---

## Practice Exercises

**Exercise 1: Cascade PERSIST**
Create `Invoice` and `LineItem` entities. Configure cascade PERSIST. Write a service that creates an invoice with 3 line items in a single save. Verify all 4 rows are created.

**Exercise 2: orphanRemoval**
Add `orphanRemoval = true` to the Invoice-LineItem relationship. Write a test that: (a) creates an invoice with 3 items, (b) removes 1 item from the list, (c) verifies only 2 items remain in the database.

**Exercise 3: Dangerous Cascade**
Create `Department` and `Employee` with `cascade = ALL`. Delete a department with employees. Observe that employees are deleted. Change to `cascade = {PERSIST, MERGE}`. Try to delete the department again (expect FK constraint error). Discuss which behavior is correct.

**Exercise 4: Audit with Spring Data**
Enable Spring Data JPA auditing. Create a `BaseEntity` with `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy`. Implement `AuditorAware`. Create a Product entity extending BaseEntity. Verify timestamps and user are set automatically.

**Exercise 5: Lifecycle Callbacks**
Create a `Document` entity with `@PrePersist` (generate a UUID slug), `@PreUpdate` (increment a version counter), and `@PostLoad` (compute a word count from content). Write tests verifying each callback fires at the correct time.

---

## What Is Next?

In the next chapter, we will explore **Transaction Management** — one of the most important topics for production applications. You will learn about ACID properties, Spring's `@Transactional` annotation, propagation levels, isolation levels, read-only optimization, rollback rules, and common transaction pitfalls like self-invocation and checked exceptions.
