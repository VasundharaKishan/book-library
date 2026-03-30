# Chapter 16: Inheritance Mapping Strategies

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand the challenge of mapping Java inheritance to relational databases
- Use @MappedSuperclass for shared fields without inheritance mapping
- Implement SINGLE_TABLE inheritance strategy with discriminator columns
- Implement JOINED inheritance strategy with separate tables
- Implement TABLE_PER_CLASS inheritance strategy with union queries
- Use @DiscriminatorColumn and @DiscriminatorValue to control type identification
- Write polymorphic queries that return mixed entity types
- Choose the right inheritance strategy for your use case
- Understand the performance trade-offs of each strategy

---

## The Challenge: Inheritance in a Relational World

Java supports class inheritance. Databases do not. When you have a class hierarchy, you must decide how to represent it in tables.

```
Java Inheritance:
+------------------------------------------------------------------+
|                                                                   |
|              Payment (abstract)                                   |
|              +-------------------+                                |
|              | id: Long          |                                |
|              | amount: BigDecimal|                                |
|              | createdAt: Date   |                                |
|              +-------------------+                                |
|                   /          \                                     |
|                  /            \                                    |
|  CreditCardPayment          BankTransferPayment                  |
|  +-----------------+        +---------------------+               |
|  | cardNumber      |        | bankName            |               |
|  | expiryMonth     |        | accountNumber       |               |
|  | expiryYear      |        | routingNumber       |               |
|  +-----------------+        +---------------------+               |
|                                                                   |
|  Question: How do we store this in tables?                        |
|  - One table for all types?                                       |
|  - Separate tables joined by FK?                                  |
|  - Completely separate tables?                                    |
|  - Or just share fields without real inheritance?                 |
+------------------------------------------------------------------+
```

JPA provides four approaches:

```
Inheritance Mapping Options:
+------------------------------------------------------------------+
|                                                                   |
|  1. @MappedSuperclass                                             |
|     Not true inheritance mapping. Shares fields only.             |
|     No polymorphic queries. Each subclass has its own table.      |
|                                                                   |
|  2. SINGLE_TABLE (default JPA inheritance strategy)               |
|     ONE table for all types. Discriminator column identifies type.|
|     Fastest queries. Nullable columns for subclass-specific data. |
|                                                                   |
|  3. JOINED                                                        |
|     Separate table per class. Joined by primary key.              |
|     Normalized. Slower queries (JOINs needed).                    |
|                                                                   |
|  4. TABLE_PER_CLASS                                               |
|     Completely separate tables. No shared table.                  |
|     UNION queries for polymorphism. Rarely used.                  |
+------------------------------------------------------------------+
```

---

## @MappedSuperclass — Shared Fields Without Inheritance

`@MappedSuperclass` is not a true inheritance strategy. It simply lets you define common fields in a base class that are inherited by child entities. Each child gets its own independent table with the base class fields included.

```java
@MappedSuperclass   // NOT @Entity — this is not a table
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // Getters
    public Long getId() { return id; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
```

```java
@Entity
@Table(name = "products")
public class Product extends BaseEntity {
    @Column(nullable = false)
    private String name;
    private BigDecimal price;
    // ...
}

@Entity
@Table(name = "customers")
public class Customer extends BaseEntity {
    @Column(nullable = false)
    private String fullName;
    private String email;
    // ...
}
```

```
@MappedSuperclass Tables:
+------------------------------------------------------------------+
|                                                                   |
|  products                          customers                      |
|  +------+----------+----------+   +------+----------+----------+ |
|  |id(PK)| name     | price    |   |id(PK)| full_name| email    | |
|  |      | created_at           |   |      | created_at           | |
|  |      | updated_at           |   |      | updated_at           | |
|  +------+----------+----------+   +------+----------+----------+ |
|                                                                   |
|  Each entity has its OWN table with base fields copied in.        |
|  No relationship between the tables.                              |
|  You CANNOT write: "SELECT b FROM BaseEntity b"                   |
|  (BaseEntity is not an entity — no polymorphic queries)           |
+------------------------------------------------------------------+
```

### When to Use @MappedSuperclass

```
@MappedSuperclass Use Cases:
+------------------------------------------------------------------+
|                                                                   |
|  USE @MappedSuperclass when:                                      |
|  - You want shared audit fields (createdAt, updatedAt, createdBy) |
|  - You want a common id strategy across all entities              |
|  - The subclasses are UNRELATED (Product and Customer)            |
|  - You do NOT need polymorphic queries                            |
|                                                                   |
|  DO NOT use @MappedSuperclass when:                               |
|  - The classes are truly related (CreditCard and BankTransfer     |
|    are both Payments)                                             |
|  - You need to query "all payments" across types                  |
|  - You need a FK to the base type (order.payment_id)              |
+------------------------------------------------------------------+
```

---

## SINGLE_TABLE — One Table for All Types

The `SINGLE_TABLE` strategy stores the entire class hierarchy in a single database table. A **discriminator column** identifies which subclass each row represents.

```java
@Entity
@Table(name = "payments")
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)  // JPA standard
@DiscriminatorColumn(
    name = "payment_type",                              // JPA standard
    discriminatorType = DiscriminatorType.STRING
)
public abstract class Payment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private BigDecimal amount;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    protected Payment() {}

    public Payment(BigDecimal amount) {
        this.amount = amount;
    }

    public Long getId() { return id; }
    public BigDecimal getAmount() { return amount; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
```

```java
@Entity
@DiscriminatorValue("CREDIT_CARD")     // JPA standard
public class CreditCardPayment extends Payment {

    @Column(name = "card_number")
    private String cardNumber;

    @Column(name = "expiry_month")
    private Integer expiryMonth;

    @Column(name = "expiry_year")
    private Integer expiryYear;

    protected CreditCardPayment() {}

    public CreditCardPayment(BigDecimal amount, String cardNumber,
                             int expiryMonth, int expiryYear) {
        super(amount);
        this.cardNumber = cardNumber;
        this.expiryMonth = expiryMonth;
        this.expiryYear = expiryYear;
    }

    // Getters
    public String getCardNumber() { return cardNumber; }
    public Integer getExpiryMonth() { return expiryMonth; }
    public Integer getExpiryYear() { return expiryYear; }
}
```

```java
@Entity
@DiscriminatorValue("BANK_TRANSFER")
public class BankTransferPayment extends Payment {

    @Column(name = "bank_name")
    private String bankName;

    @Column(name = "account_number")
    private String accountNumber;

    @Column(name = "routing_number")
    private String routingNumber;

    protected BankTransferPayment() {}

    public BankTransferPayment(BigDecimal amount, String bankName,
                               String accountNumber, String routingNumber) {
        super(amount);
        this.bankName = bankName;
        this.accountNumber = accountNumber;
        this.routingNumber = routingNumber;
    }

    // Getters
    public String getBankName() { return bankName; }
    public String getAccountNumber() { return accountNumber; }
    public String getRoutingNumber() { return routingNumber; }
}
```

```
SINGLE_TABLE Database Layout:
+------------------------------------------------------------------+
|                                                                   |
|  payments (ONE table for all payment types)                       |
|  +----+--------+------+----------+-------+--------+-----+------+ |
|  | id | type   |amount| created  | card  | expiry | bank| acct | |
|  |    |        |      |          | _num  |_mo/_yr | name| _num | |
|  |----|--------|------|----------|-------|--------|-----|------| |
|  | 1  | CREDIT | 99.99| 2025-... | 4111  | 12/26  | null| null | |
|  |    | _CARD  |      |          |       |        |     |      | |
|  | 2  | BANK_  |250.00| 2025-... | null  | null   | Chase| 1234| |
|  |    |TRANSFER|      |          |       |        |     |      | |
|  | 3  | CREDIT | 49.99| 2025-... | 5500  | 03/27  | null| null | |
|  |    | _CARD  |      |          |       |        |     |      | |
|  +----+--------+------+----------+-------+--------+-----+------+ |
|                                                                   |
|  Discriminator column: payment_type                               |
|  - "CREDIT_CARD" rows have card columns, null bank columns        |
|  - "BANK_TRANSFER" rows have bank columns, null card columns      |
|  - Subclass columns MUST be nullable (different types use them)   |
+------------------------------------------------------------------+
```

### Querying SINGLE_TABLE

```java
@Repository
public interface PaymentRepository extends JpaRepository<Payment, Long> {

    // Polymorphic — returns ALL payment types
    List<Payment> findAll();
    // SQL: SELECT * FROM payments

    // Type-specific — returns only credit cards
    @Query("SELECT p FROM CreditCardPayment p WHERE p.amount > :min")
    List<CreditCardPayment> findLargeCreditCardPayments(@Param("min") BigDecimal min);
    // SQL: SELECT * FROM payments WHERE payment_type = 'CREDIT_CARD' AND amount > ?

    // Find by discriminator value
    @Query("SELECT p FROM Payment p WHERE TYPE(p) = CreditCardPayment")
    List<Payment> findCreditCardPayments();

    // Find all payments above an amount (polymorphic)
    List<Payment> findByAmountGreaterThan(BigDecimal amount);
    // SQL: SELECT * FROM payments WHERE amount > ?
    // Returns mix of CreditCardPayment and BankTransferPayment objects
}
```

```
SINGLE_TABLE Query Performance:
+------------------------------------------------------------------+
|                                                                   |
|  Polymorphic query: "Find all payments over $100"                 |
|  SELECT * FROM payments WHERE amount > 100                        |
|  --> SINGLE table scan, NO joins                                  |
|  --> FASTEST possible                                             |
|                                                                   |
|  Type-specific query: "Find all credit card payments"             |
|  SELECT * FROM payments WHERE payment_type = 'CREDIT_CARD'        |
|  --> Still SINGLE table, just adds WHERE clause                   |
|  --> Still very fast                                              |
|                                                                   |
|  INSERT: Single INSERT into one table                             |
|  --> Fastest possible                                             |
+------------------------------------------------------------------+
```

---

## JOINED — One Table Per Class, Linked by PK

The `JOINED` strategy creates a separate table for the base class and each subclass. They are linked by a shared primary key.

```java
@Entity
@Table(name = "vehicles")
@Inheritance(strategy = InheritanceType.JOINED)        // JPA standard
@DiscriminatorColumn(name = "vehicle_type")            // Optional for JOINED
public abstract class Vehicle {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String make;

    @Column(nullable = false)
    private String model;

    @Column(nullable = false)
    private int year;

    @Column(nullable = false)
    private BigDecimal price;

    protected Vehicle() {}

    public Vehicle(String make, String model, int year, BigDecimal price) {
        this.make = make;
        this.model = model;
        this.year = year;
        this.price = price;
    }

    // Getters
    public Long getId() { return id; }
    public String getMake() { return make; }
    public String getModel() { return model; }
    public int getYear() { return year; }
    public BigDecimal getPrice() { return price; }
}
```

```java
@Entity
@Table(name = "cars")
@DiscriminatorValue("CAR")
public class Car extends Vehicle {

    @Column(name = "num_doors")
    private int numDoors;

    @Column(name = "trunk_size")
    private int trunkSize;   // in liters

    protected Car() {}

    public Car(String make, String model, int year, BigDecimal price,
               int numDoors, int trunkSize) {
        super(make, model, year, price);
        this.numDoors = numDoors;
        this.trunkSize = trunkSize;
    }

    public int getNumDoors() { return numDoors; }
    public int getTrunkSize() { return trunkSize; }
}
```

```java
@Entity
@Table(name = "trucks")
@DiscriminatorValue("TRUCK")
public class Truck extends Vehicle {

    @Column(name = "payload_capacity")
    private double payloadCapacity;   // in tons

    @Column(name = "num_axles")
    private int numAxles;

    protected Truck() {}

    public Truck(String make, String model, int year, BigDecimal price,
                 double payloadCapacity, int numAxles) {
        super(make, model, year, price);
        this.payloadCapacity = payloadCapacity;
        this.numAxles = numAxles;
    }

    public double getPayloadCapacity() { return payloadCapacity; }
    public int getNumAxles() { return numAxles; }
}
```

```
JOINED Database Layout:
+------------------------------------------------------------------+
|                                                                   |
|  vehicles (base table)                                            |
|  +------+------+--------+------+----------+                      |
|  |id(PK)| make | model  | year | price    |                      |
|  |------+------+--------+------+----------|                      |
|  | 1    | Toyota| Camry | 2024 | 35000    |                      |
|  | 2    | Ford | F-150  | 2024 | 55000    |                      |
|  | 3    | Honda| Civic  | 2025 | 28000    |                      |
|  +------+------+--------+------+----------+                      |
|                                                                   |
|  cars (subclass table)       trucks (subclass table)              |
|  +------+-------+-------+   +------+---------+-------+           |
|  |id(PK)| doors | trunk |   |id(PK)| payload | axles |           |
|  | (FK) |       |       |   | (FK) |         |       |           |
|  |------+-------+-------|   |------+---------+-------|           |
|  | 1    | 4     | 500   |   | 2    | 2.5     | 2     |           |
|  | 3    | 4     | 400   |   +------+---------+-------+           |
|  +------+-------+-------+                                        |
|                                                                   |
|  cars.id and trucks.id are BOTH primary keys AND foreign keys     |
|  referencing vehicles.id. Same value, shared primary key.         |
|                                                                   |
|  No null columns! Each table only has relevant fields.            |
+------------------------------------------------------------------+
```

### Querying JOINED Strategy

```
JOINED Query Performance:
+------------------------------------------------------------------+
|                                                                   |
|  Polymorphic query: "Find all vehicles over $30K"                 |
|  SELECT v.*, c.*, t.*                                             |
|  FROM vehicles v                                                  |
|  LEFT JOIN cars c ON v.id = c.id                                  |
|  LEFT JOIN trucks t ON v.id = t.id                                |
|  WHERE v.price > 30000                                            |
|  --> Requires JOIN across ALL subclass tables                     |
|  --> Slower than SINGLE_TABLE                                     |
|  --> More JOINs with more subclasses                              |
|                                                                   |
|  Type-specific query: "Find all cars"                             |
|  SELECT v.*, c.*                                                  |
|  FROM vehicles v                                                  |
|  INNER JOIN cars c ON v.id = c.id                                 |
|  --> Only ONE join (the specific subclass)                        |
|  --> Reasonably fast                                              |
|                                                                   |
|  INSERT: TWO inserts (base + subclass table)                      |
|  --> Slightly slower than SINGLE_TABLE                            |
+------------------------------------------------------------------+
```

---

## TABLE_PER_CLASS — Completely Separate Tables

Each concrete class gets its own table with ALL fields (inherited + own). No shared table exists.

```java
@Entity
@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)   // JPA standard
public abstract class Notification {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)  // IDENTITY won't work here
    private Long id;

    @Column(nullable = false)
    private String recipient;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String message;

    @Column(name = "sent_at")
    private LocalDateTime sentAt;

    protected Notification() {}

    public Notification(String recipient, String message) {
        this.recipient = recipient;
        this.message = message;
        this.sentAt = LocalDateTime.now();
    }

    // Getters
    public Long getId() { return id; }
    public String getRecipient() { return recipient; }
    public String getMessage() { return message; }
    public LocalDateTime getSentAt() { return sentAt; }
}

@Entity
@Table(name = "email_notifications")
public class EmailNotification extends Notification {
    @Column(name = "subject_line")
    private String subjectLine;
    // constructor, getters...
}

@Entity
@Table(name = "sms_notifications")
public class SmsNotification extends Notification {
    @Column(name = "phone_number")
    private String phoneNumber;
    // constructor, getters...
}
```

```
TABLE_PER_CLASS Database Layout:
+------------------------------------------------------------------+
|                                                                   |
|  email_notifications (ALL fields duplicated)                      |
|  +------+-----------+---------+----------+----------+             |
|  |id(PK)| recipient | message | sent_at  | subject  |             |
|  |------+-----------+---------+----------+----------|             |
|  | 1    | alice@co  | Hello.. | 2025-... | Welcome  |             |
|  | 3    | bob@co    | Update..| 2025-... | News     |             |
|  +------+-----------+---------+----------+----------+             |
|                                                                   |
|  sms_notifications (ALL fields duplicated)                        |
|  +------+-----------+---------+----------+----------+             |
|  |id(PK)| recipient | message | sent_at  | phone    |             |
|  |------+-----------+---------+----------+----------|             |
|  | 2    | charlie   | Code... | 2025-... | 555-0123 |             |
|  +------+-----------+---------+----------+----------+             |
|                                                                   |
|  No base table exists. Each table has ALL fields.                 |
|  IDs must be globally unique (cannot use IDENTITY).               |
|  recipient, message, sent_at are DUPLICATED in each table.        |
+------------------------------------------------------------------+
```

```
TABLE_PER_CLASS Query Performance:
+------------------------------------------------------------------+
|                                                                   |
|  Polymorphic query: "Find all notifications"                      |
|  SELECT * FROM email_notifications                                |
|  UNION ALL                                                        |
|  SELECT * FROM sms_notifications                                  |
|  --> Requires UNION across ALL subclass tables                    |
|  --> SLOWEST for polymorphic queries                              |
|  --> More tables = more UNIONs                                    |
|                                                                   |
|  Type-specific query: "Find all email notifications"              |
|  SELECT * FROM email_notifications                                |
|  --> SINGLE table, NO joins, NO unions                            |
|  --> FASTEST for type-specific queries                            |
|                                                                   |
|  INSERT: Single INSERT into one table                             |
|  --> Fast (like SINGLE_TABLE)                                     |
+------------------------------------------------------------------+
```

---

## Strategy Comparison

```
Complete Comparison:
+------------------------------------------------------------------+
|                                                                   |
|  Criteria          SINGLE_TABLE  JOINED    TABLE_PER_CLASS        |
|  ----------------------------------------------------------------|
|  Polymorphic       Fastest       Moderate  Slowest (UNION)        |
|  query speed       (1 table)     (JOINs)   (UNION ALL)           |
|                                                                   |
|  Type-specific     Fast (WHERE   Moderate  Fastest                |
|  query speed       on discrim)   (1 JOIN)  (1 table, no join)    |
|                                                                   |
|  INSERT speed      Fastest       Moderate  Fast                   |
|                    (1 INSERT)    (2 INSERTs)(1 INSERT)            |
|                                                                   |
|  Data integrity    Weak          Strong    Moderate               |
|                    (nullable     (NOT NULL (NOT NULL OK)          |
|                    subclass cols) OK)                              |
|                                                                   |
|  Normalization     Poor          Good      Poor                   |
|                    (1 wide table)(separate (fields duplicated     |
|                    with nulls)   tables)    in each table)        |
|                                                                   |
|  Schema changes    Easy          Moderate  Hard (must alter       |
|                    (1 table)     (base or   ALL tables for        |
|                                  sub table) base field changes)   |
|                                                                   |
|  FK references     Easy          Easy      Difficult              |
|  from other        (FK to 1      (FK to    (FK to which table?)  |
|  entities          table)        base)                             |
|                                                                   |
|  @GeneratedValue   All types     All types AUTO or SEQUENCE       |
|  strategies        work          work      (IDENTITY fails)       |
+------------------------------------------------------------------+
```

### Choosing a Strategy

```
Decision Guide:
+------------------------------------------------------------------+
|                                                                   |
|  Do you need polymorphic queries?                                 |
|  ("Find all payments", "Find all vehicles")                       |
|      |                                                            |
|    NO --> Use @MappedSuperclass (simplest, no inheritance)        |
|      |                                                            |
|   YES                                                             |
|      |                                                            |
|      v                                                            |
|  How many subclass-specific fields?                               |
|      |                                                            |
|   FEW (< 5 per subclass)                                         |
|      |--> SINGLE_TABLE (fast, simple, some null columns OK)       |
|      |                                                            |
|   MANY (subclasses are very different)                            |
|      |--> JOINED (normalized, no wasted space, but slower)        |
|      |                                                            |
|  Are polymorphic queries rare?                                    |
|  Mostly query one type at a time?                                 |
|      |                                                            |
|   YES --> TABLE_PER_CLASS (fastest per-type, slowest polymorphic) |
|                                                                   |
|  Default recommendation: SINGLE_TABLE                             |
|  It is the simplest, fastest for most queries, and the            |
|  JPA default for a reason. Use JOINED only when the subclass      |
|  differences are large and data integrity matters.                |
+------------------------------------------------------------------+
```

---

## Referencing Inherited Entities from Other Entities

A key advantage of SINGLE_TABLE and JOINED is that other entities can have a foreign key to the base class:

```java
@Entity
@Table(name = "orders")
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "payment_id")
    private Payment payment;    // Can be CreditCard or BankTransfer

    // ... other fields
}
```

```
FK to Inherited Entity:
+------------------------------------------------------------------+
|                                                                   |
|  SINGLE_TABLE and JOINED:                                         |
|  orders.payment_id --> payments.id                                |
|  Works perfectly. FK points to ONE table.                         |
|                                                                   |
|  TABLE_PER_CLASS:                                                 |
|  orders.payment_id --> ??? (credit_cards.id or bank_transfers.id?)|
|  PROBLEMATIC! FK must reference a specific table,                 |
|  but there is no shared base table.                               |
|  Most databases cannot enforce this FK constraint.                |
+------------------------------------------------------------------+
```

---

## instanceof and Polymorphic Operations

When you load entities polymorphically, you can use `instanceof` to handle type-specific logic:

```java
@Service
@Transactional(readOnly = true)
public class PaymentReportService {

    private final PaymentRepository paymentRepository;

    public void printPaymentReport() {
        List<Payment> payments = paymentRepository.findAll();

        for (Payment payment : payments) {
            System.out.printf("$%.2f on %s", payment.getAmount(),
                payment.getCreatedAt());

            if (payment instanceof CreditCardPayment cc) {
                System.out.printf(" via Credit Card ending %s",
                    cc.getCardNumber().substring(cc.getCardNumber().length() - 4));
            } else if (payment instanceof BankTransferPayment bt) {
                System.out.printf(" via Bank Transfer from %s", bt.getBankName());
            }

            System.out.println();
        }
    }
}
```

### TYPE() in JPQL

```java
// Find payments of a specific type
@Query("SELECT p FROM Payment p WHERE TYPE(p) = CreditCardPayment")
List<Payment> findCreditCardPayments();

@Query("SELECT p FROM Payment p WHERE TYPE(p) IN (CreditCardPayment, BankTransferPayment)")
List<Payment> findElectronicPayments();

// Count by type
@Query("SELECT TYPE(p), COUNT(p) FROM Payment p GROUP BY TYPE(p)")
List<Object[]> countByType();
```

---

## Common Mistakes

1. **Using TABLE_PER_CLASS with IDENTITY generation**: `GenerationType.IDENTITY` relies on database auto-increment, but IDs must be globally unique across tables. Use `AUTO`, `SEQUENCE`, or `TABLE` instead.

2. **Not making subclass columns nullable with SINGLE_TABLE**: In SINGLE_TABLE, a credit card row has null bank columns and vice versa. Subclass-specific columns MUST be nullable. Adding `@Column(nullable = false)` on subclass fields causes insert failures.

3. **Adding too many subclasses to SINGLE_TABLE**: If you have 10 subclasses each with 5 unique columns, the table has 50+ columns where most are null. Consider JOINED for better data integrity.

4. **Using TABLE_PER_CLASS with FK relationships**: Other entities cannot have proper FK constraints to TABLE_PER_CLASS entities because there is no shared table to reference.

5. **Choosing JOINED for small hierarchies**: If subclasses differ by only 2-3 fields, JOINED adds unnecessary JOINs. SINGLE_TABLE is simpler and faster.

6. **Forgetting @DiscriminatorValue**: Without an explicit discriminator value, JPA uses the class name as the default. This is brittle — renaming the class changes stored data.

---

## Best Practices

1. **Default to SINGLE_TABLE**: It is the fastest for queries, simplest to implement, and handles most use cases. Accept the nullable columns trade-off.

2. **Use @MappedSuperclass for audit fields**: Common fields like `id`, `createdAt`, `updatedAt` across unrelated entities belong in a `@MappedSuperclass`, not an inheritance hierarchy.

3. **Always set @DiscriminatorValue explicitly**: Do not rely on the default class name. Explicit values are stable across refactoring and renaming.

4. **Avoid deep inheritance hierarchies**: One level of subclassing is clean. Two or more levels become difficult to manage and query. Prefer composition over deep inheritance.

5. **Use JOINED only when subclasses are significantly different**: If subclasses have many unique columns and you need NOT NULL constraints, JOINED is appropriate. Otherwise, SINGLE_TABLE is simpler.

6. **Avoid TABLE_PER_CLASS in most cases**: It has limited support for FK relationships, requires UNION for polymorphic queries, and does not support IDENTITY generation. Use it only when you almost never query polymorphically.

---

## Summary

In this chapter, you learned how to map Java inheritance hierarchies to database tables:

- **@MappedSuperclass** shares fields across unrelated entities without creating inheritance in the database. No polymorphic queries, each subclass has its own table.

- **SINGLE_TABLE** stores the entire hierarchy in one table with a discriminator column. Fastest for queries but subclass columns must be nullable.

- **JOINED** creates a separate table per class linked by primary key. Normalized and supports NOT NULL on subclass columns, but requires JOINs for queries.

- **TABLE_PER_CLASS** puts everything in separate tables with duplicated base fields. Fastest for type-specific queries but requires UNION for polymorphic queries.

- **Default to SINGLE_TABLE** for most use cases. Use JOINED when subclasses have many unique fields and data integrity matters. Use @MappedSuperclass for shared audit/timestamp fields. Avoid TABLE_PER_CLASS unless polymorphic queries are rare.

---

## Interview Questions

**Q1: What are the JPA inheritance strategies?**

JPA provides three true inheritance strategies: `SINGLE_TABLE` (one table with discriminator), `JOINED` (separate tables linked by PK), and `TABLE_PER_CLASS` (independent tables with duplicated fields). Additionally, `@MappedSuperclass` provides field sharing without true inheritance mapping.

**Q2: What is a discriminator column?**

A discriminator column is a special column in the database table that identifies which subclass a particular row represents. For example, a `payment_type` column with values `CREDIT_CARD` or `BANK_TRANSFER`. It is defined with `@DiscriminatorColumn` on the base class and `@DiscriminatorValue` on each subclass.

**Q3: Why must subclass-specific columns be nullable in SINGLE_TABLE?**

Because all types share one table. A credit card row has values for `card_number` and `expiry_month` but null for `bank_name` and `account_number`. A bank transfer row is the opposite. Each row only uses its own subclass columns — the rest must accept null.

**Q4: When would you choose JOINED over SINGLE_TABLE?**

When subclasses have many unique columns (e.g., 15+ each), when you need NOT NULL constraints on subclass columns, or when the table would become excessively wide with SINGLE_TABLE. JOINED provides better normalization at the cost of JOIN queries.

**Q5: What is the limitation of TABLE_PER_CLASS with GenerationType.IDENTITY?**

`IDENTITY` uses database auto-increment, which generates IDs per table. Two tables could generate the same ID (both have row with id=1). Since polymorphic queries use UNION across tables, IDs must be globally unique. Use `SEQUENCE` or `TABLE` generation instead.

**Q6: How do you perform a type-specific query in JPQL?**

Use the `TYPE()` function: `SELECT p FROM Payment p WHERE TYPE(p) = CreditCardPayment`. You can also use `IN`: `WHERE TYPE(p) IN (CreditCardPayment, BankTransferPayment)`. Alternatively, query the subclass directly: `SELECT c FROM CreditCardPayment c`.

---

## Practice Exercises

**Exercise 1: @MappedSuperclass**
Create a `BaseEntity` with `id`, `createdAt`, `updatedAt` and `@PrePersist`/`@PreUpdate` callbacks. Create `Product` and `Category` entities extending it. Verify that both entities have audit timestamps set automatically.

**Exercise 2: SINGLE_TABLE Payment System**
Implement the Payment hierarchy (CreditCardPayment, BankTransferPayment) with SINGLE_TABLE strategy. Create an Order entity with a `@ManyToOne` to Payment. Test polymorphic queries, type-specific queries, and the `TYPE()` function.

**Exercise 3: JOINED Vehicle System**
Implement the Vehicle hierarchy (Car, Truck, Motorcycle) with JOINED strategy. Add 5 vehicles of mixed types. Enable SQL logging and compare the queries generated for: (a) findAll(), (b) finding only cars, (c) inserting a new truck.

**Exercise 4: Strategy Comparison**
Map the same 3-class hierarchy with all three strategies (in separate packages). Insert 100 records of mixed types. Benchmark: (a) polymorphic findAll(), (b) type-specific find, (c) insert speed. Compare query counts and shapes.

**Exercise 5: Shape Hierarchy**
Design a `Shape` hierarchy with `Circle` (radius), `Rectangle` (width, height), and `Triangle` (base, height, sideA, sideB). Add an `area()` method to each. Choose the most appropriate inheritance strategy and justify your choice. Implement and test with polymorphic queries.

---

## What Is Next?

In the next chapter, we enter **Part IV: Deep Dive** and start with **Entity Lifecycle and Persistence Context**. You will learn how Hibernate manages entities internally — the four lifecycle states (New, Managed, Detached, Removed), how the first-level cache works, how dirty checking detects changes automatically, and when and how Hibernate flushes changes to the database.
