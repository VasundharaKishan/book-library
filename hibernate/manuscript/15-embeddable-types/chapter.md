# Chapter 15: Embeddable Types and Element Collections

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand what embeddable types are and when to use them
- Create value objects with @Embeddable and @Embedded
- Override column names with @AttributeOverride
- Use @ElementCollection to store collections of value types
- Configure @CollectionTable for element collections
- Distinguish between entities and value objects
- Nest embeddable types within other embeddables
- Use embeddable types as map keys
- Query embeddable fields with JPQL and derived methods

---

## Entities vs Value Objects

Before diving into embeddable types, you need to understand a fundamental distinction:

```
Entities vs Value Objects:
+------------------------------------------------------------------+
|                                                                   |
|  Entity                           Value Object                    |
|  +--------------------------+     +--------------------------+    |
|  | Has its own identity     |     | No identity of its own   |    |
|  | (id field / primary key) |     | (no id / no PK)          |    |
|  |                          |     |                          |    |
|  | Has its own lifecycle    |     | Belongs to an entity     |    |
|  | (exists independently)  |     | (cannot exist alone)     |    |
|  |                          |     |                          |    |
|  | Tracked by Hibernate    |     | Embedded in the owner's  |    |
|  | (managed entity)        |     | table (not a separate    |    |
|  |                          |     | table by default)        |    |
|  |                          |     |                          |    |
|  | Example: Customer,       |     | Example: Address, Money, |    |
|  | Order, Product           |     | PhoneNumber, DateRange   |    |
|  +--------------------------+     +--------------------------+    |
|                                                                   |
|  Question: Does this "thing" have meaning on its own?             |
|                                                                   |
|  "123 Main St, Springfield"  --> NO, it is part of a Customer    |
|  "Customer #42, Alice"       --> YES, it exists independently    |
|                                                                   |
|  If NO --> Value Object --> @Embeddable                           |
|  If YES --> Entity --> @Entity                                    |
+------------------------------------------------------------------+
```

### Real-World Analogies

Think about a house address. An address does not exist independently — it describes where a person lives. You would not have an "addresses" table with its own ID that customers reference via foreign key. Instead, the address fields (street, city, state, zip) are part of the customer record. That is a value object.

Now think about a product in an order. A product exists independently — it has its own ID, its own lifecycle, and multiple orders can reference it. That is an entity.

---

## @Embeddable and @Embedded

### Creating an Embeddable Class

```java
@Embeddable                          // JPA standard
public class Address {

    @Column(nullable = false)
    private String street;

    @Column(nullable = false, length = 100)
    private String city;

    @Column(nullable = false, length = 2)
    private String state;

    @Column(name = "zip_code", nullable = false, length = 10)
    private String zipCode;

    protected Address() {}           // Required by JPA

    public Address(String street, String city, String state, String zipCode) {
        this.street = street;
        this.city = city;
        this.state = state;
        this.zipCode = zipCode;
    }

    // Getters
    public String getStreet() { return street; }
    public String getCity() { return city; }
    public String getState() { return state; }
    public String getZipCode() { return zipCode; }

    // Value objects should implement equals and hashCode
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Address address = (Address) o;
        return Objects.equals(street, address.street) &&
               Objects.equals(city, address.city) &&
               Objects.equals(state, address.state) &&
               Objects.equals(zipCode, address.zipCode);
    }

    @Override
    public int hashCode() {
        return Objects.hash(street, city, state, zipCode);
    }

    @Override
    public String toString() {
        return street + ", " + city + ", " + state + " " + zipCode;
    }
}
```

### Using @Embedded in an Entity

```java
@Entity
@Table(name = "customers")
public class Customer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Embedded                              // JPA standard
    private Address address;

    protected Customer() {}

    public Customer(String name, Address address) {
        this.name = name;
        this.address = address;
    }

    // Getters and setters
    public Long getId() { return id; }
    public String getName() { return name; }
    public Address getAddress() { return address; }
    public void setAddress(Address address) { this.address = address; }
}
```

```
How @Embedded Maps to the Database:
+------------------------------------------------------------------+
|                                                                   |
|  Java:                          Database (customers table):       |
|  +------------------+          +------+------+------+------+--+  |
|  | Customer         |          | id   | name |street| city |..|  |
|  | - id: Long       |          |------+------+------+------+--|  |
|  | - name: String   |          | 1    | Alice|123   | NYC  |..|  |
|  | - address: Address|          | 2    | Bob  |456   | LA   |..|  |
|  |   - street       |--------->| (all address columns are     |  |
|  |   - city         |          |  embedded in customers table)|  |
|  |   - state        |          +------+------+------+------+--+  |
|  |   - zipCode      |                                            |
|  +------------------+          No separate "addresses" table!     |
|                                                                   |
|  The embeddable fields become columns in the OWNER's table.       |
|  There is NO join, NO foreign key, NO separate table.             |
+------------------------------------------------------------------+
```

### Usage

```java
// Creating
Address address = new Address("123 Main St", "Springfield", "IL", "62701");
Customer customer = new Customer("Alice Johnson", address);
customerRepository.save(customer);

// Reading
Customer found = customerRepository.findById(1L).orElseThrow();
System.out.println(found.getAddress().getCity());  // "Springfield"

// Updating (replace the entire value object)
found.setAddress(new Address("456 Oak Ave", "Chicago", "IL", "60601"));
// Hibernate: UPDATE customers SET street='456 Oak Ave', city='Chicago', ...
```

---

## @AttributeOverride — Renaming Embedded Columns

When you embed the same type twice, you get column name conflicts. `@AttributeOverride` resolves this:

```java
@Entity
@Table(name = "companies")
public class Company {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street",  column = @Column(name = "billing_street")),
        @AttributeOverride(name = "city",    column = @Column(name = "billing_city")),
        @AttributeOverride(name = "state",   column = @Column(name = "billing_state")),
        @AttributeOverride(name = "zipCode", column = @Column(name = "billing_zip"))
    })
    private Address billingAddress;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "street",  column = @Column(name = "shipping_street")),
        @AttributeOverride(name = "city",    column = @Column(name = "shipping_city")),
        @AttributeOverride(name = "state",   column = @Column(name = "shipping_state")),
        @AttributeOverride(name = "zipCode", column = @Column(name = "shipping_zip"))
    })
    private Address shippingAddress;

    // constructor, getters, setters...
}
```

```
@AttributeOverride in the Database:
+------------------------------------------------------------------+
|                                                                   |
|  companies table:                                                 |
|  +----+------+----------------+----------------+                  |
|  | id | name | billing_street | shipping_street|                  |
|  |    |      | billing_city   | shipping_city  |                  |
|  |    |      | billing_state  | shipping_state |                  |
|  |    |      | billing_zip    | shipping_zip   |                  |
|  +----+------+----------------+----------------+                  |
|                                                                   |
|  Without @AttributeOverride, both Address fields would try        |
|  to create "street", "city", "state", "zip_code" columns,        |
|  causing a conflict. @AttributeOverride gives each a unique       |
|  column name prefix.                                              |
+------------------------------------------------------------------+
```

---

## @Embeddable for Money, DateRange, and Other Value Types

Embeddable types are perfect for domain concepts that have multiple fields but no identity:

### Money

```java
@Embeddable
public class Money {

    @Column(nullable = false, precision = 19, scale = 2)
    private BigDecimal amount;

    @Column(nullable = false, length = 3)
    @Enumerated(EnumType.STRING)
    private Currency currency;

    public enum Currency { USD, EUR, GBP, JPY }

    protected Money() {}

    public Money(BigDecimal amount, Currency currency) {
        this.amount = amount;
        this.currency = currency;
    }

    public Money(double amount, Currency currency) {
        this(BigDecimal.valueOf(amount), currency);
    }

    // Getters
    public BigDecimal getAmount() { return amount; }
    public Currency getCurrency() { return currency; }

    // Business methods
    public Money add(Money other) {
        if (this.currency != other.currency) {
            throw new IllegalArgumentException("Cannot add different currencies");
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }

    @Override
    public boolean equals(Object o) { /* compare amount and currency */ }

    @Override
    public int hashCode() { return Objects.hash(amount, currency); }

    @Override
    public String toString() { return amount + " " + currency; }
}
```

```java
@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "amount", column = @Column(name = "price_amount")),
        @AttributeOverride(name = "currency", column = @Column(name = "price_currency"))
    })
    private Money price;

    // ...
}
```

### DateRange

```java
@Embeddable
public class DateRange {

    @Column(name = "start_date")
    private LocalDate startDate;

    @Column(name = "end_date")
    private LocalDate endDate;

    protected DateRange() {}

    public DateRange(LocalDate startDate, LocalDate endDate) {
        if (endDate != null && startDate != null && endDate.isBefore(startDate)) {
            throw new IllegalArgumentException("End date cannot be before start date");
        }
        this.startDate = startDate;
        this.endDate = endDate;
    }

    public boolean isActive() {
        LocalDate today = LocalDate.now();
        return (startDate == null || !today.isBefore(startDate)) &&
               (endDate == null || !today.isAfter(endDate));
    }

    public long getDurationDays() {
        if (startDate == null || endDate == null) return 0;
        return ChronoUnit.DAYS.between(startDate, endDate);
    }

    // Getters, equals, hashCode, toString...
}
```

```java
@Entity
public class Campaign {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Embedded
    private DateRange activePeriod;

    // ...
}
```

---

## Nesting Embeddable Types

Embeddable classes can contain other embeddable classes:

```java
@Embeddable
public class ContactInfo {

    @Column(nullable = false)
    private String email;

    @Column(name = "phone_number")
    private String phoneNumber;

    @Embedded
    private Address address;

    protected ContactInfo() {}

    public ContactInfo(String email, String phoneNumber, Address address) {
        this.email = email;
        this.phoneNumber = phoneNumber;
        this.address = address;
    }

    // Getters...
}
```

```java
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @Embedded
    private ContactInfo contactInfo;

    // ...
}
```

```
Nested Embeddable Mapping:
+------------------------------------------------------------------+
|                                                                   |
|  Java:                                                            |
|  Employee                                                         |
|    |-- id                                                         |
|    |-- name                                                       |
|    +-- contactInfo (ContactInfo)                                  |
|          |-- email                                                |
|          |-- phoneNumber                                          |
|          +-- address (Address)                                    |
|                |-- street                                         |
|                |-- city                                           |
|                |-- state                                          |
|                +-- zipCode                                        |
|                                                                   |
|  Database (employees table):                                      |
|  +----+------+-------+--------+--------+------+-------+-------+  |
|  | id | name | email | phone_ | street | city | state | zip_  |  |
|  |    |      |       | number |        |      |       | code  |  |
|  +----+------+-------+--------+--------+------+-------+-------+  |
|                                                                   |
|  All fields flattened into one table. No joins needed.            |
+------------------------------------------------------------------+
```

---

## @ElementCollection — Collections of Value Types

What if an entity has a collection of value objects? You cannot use `@OneToMany` because value objects are not entities. Use `@ElementCollection` instead:

```java
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ElementCollection                       // JPA standard
    @CollectionTable(                        // JPA standard
        name = "employee_phone_numbers",     // Separate table name
        joinColumns = @JoinColumn(name = "employee_id")  // FK column
    )
    @Column(name = "phone_number")           // Column for the value
    private Set<String> phoneNumbers = new HashSet<>();

    // ...
}
```

```
@ElementCollection of Strings:
+------------------------------------------------------------------+
|                                                                   |
|  Java:                                                            |
|  Employee                                                         |
|    |-- id: 1                                                      |
|    |-- name: "Alice"                                              |
|    +-- phoneNumbers: ["555-0101", "555-0102", "555-0103"]         |
|                                                                   |
|  Database:                                                        |
|                                                                   |
|  employees                  employee_phone_numbers                |
|  +----+-------+            +-------------+--------------+         |
|  | id | name  |            | employee_id | phone_number |         |
|  |----+-------|            |-------------+--------------|         |
|  | 1  | Alice |<-----------| 1           | 555-0101     |         |
|  | 2  | Bob   |     +------| 1           | 555-0102     |         |
|  +----+-------+     |      | 1           | 555-0103     |         |
|                      +------| 2           | 555-0201     |         |
|                             +-------------+--------------+         |
|                                                                   |
|  A SEPARATE TABLE is created for the collection.                  |
|  This is different from @Embedded (same table).                   |
|  Each element is a row. The FK links back to the owner entity.    |
+------------------------------------------------------------------+
```

### @ElementCollection of Embeddable Types

```java
@Embeddable
public class Skill {

    @Column(nullable = false)
    private String name;

    @Enumerated(EnumType.STRING)
    private SkillLevel level;

    public enum SkillLevel { BEGINNER, INTERMEDIATE, ADVANCED, EXPERT }

    protected Skill() {}

    public Skill(String name, SkillLevel level) {
        this.name = name;
        this.level = level;
    }

    // Getters, equals, hashCode...
}
```

```java
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ElementCollection(fetch = FetchType.LAZY)
    @CollectionTable(
        name = "employee_skills",
        joinColumns = @JoinColumn(name = "employee_id")
    )
    private List<Skill> skills = new ArrayList<>();

    public void addSkill(String name, Skill.SkillLevel level) {
        skills.add(new Skill(name, level));
    }

    public void removeSkill(String name) {
        skills.removeIf(s -> s.getName().equals(name));
    }

    // ...
}
```

```
@ElementCollection of Embeddable:
+------------------------------------------------------------------+
|                                                                   |
|  employees                   employee_skills                      |
|  +----+-------+             +-------------+--------+-----------+  |
|  | id | name  |             | employee_id | name   | level     |  |
|  |----+-------|             |-------------+--------+-----------|  |
|  | 1  | Alice |<------------| 1           | Java   | EXPERT    |  |
|  +----+-------+      +-----| 1           | SQL    | ADVANCED  |  |
|                       |     | 1           | React  | BEGINNER  |  |
|                       |     +-------------+--------+-----------+  |
|                       |                                           |
|  Each Skill embeddable becomes a row in employee_skills.          |
|  The Skill fields (name, level) become columns.                   |
|  No separate "skills" entity — these are value objects.           |
+------------------------------------------------------------------+
```

### @ElementCollection of Enums

```java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;

    @ElementCollection(fetch = FetchType.EAGER)  // Roles usually loaded eagerly
    @CollectionTable(name = "user_roles",
                     joinColumns = @JoinColumn(name = "user_id"))
    @Column(name = "role")
    @Enumerated(EnumType.STRING)
    private Set<Role> roles = new HashSet<>();

    public enum Role { USER, EDITOR, ADMIN, SUPER_ADMIN }

    public void addRole(Role role) { roles.add(role); }
    public void removeRole(Role role) { roles.remove(role); }
    public boolean hasRole(Role role) { return roles.contains(role); }

    // ...
}
```

---

## @ElementCollection with Map

You can also use `@ElementCollection` with a `Map`:

```java
@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ElementCollection
    @CollectionTable(name = "product_attributes",
                     joinColumns = @JoinColumn(name = "product_id"))
    @MapKeyColumn(name = "attribute_name")       // Column for the map key
    @Column(name = "attribute_value")             // Column for the map value
    private Map<String, String> attributes = new HashMap<>();

    public void setAttribute(String key, String value) {
        attributes.put(key, value);
    }

    public String getAttribute(String key) {
        return attributes.get(key);
    }

    // ...
}
```

```
@ElementCollection with Map:
+------------------------------------------------------------------+
|                                                                   |
|  Java:                                                            |
|  Product                                                          |
|    |-- id: 1                                                      |
|    |-- name: "Laptop"                                             |
|    +-- attributes:                                                |
|          "color" -> "silver"                                      |
|          "weight" -> "1.4kg"                                      |
|          "screen" -> "14 inch"                                    |
|                                                                   |
|  Database:                                                        |
|                                                                   |
|  products                   product_attributes                    |
|  +----+--------+           +------------+----------------+-----+  |
|  | id | name   |           | product_id | attribute_name |value|  |
|  |----+--------|           |------------+----------------+-----|  |
|  | 1  | Laptop |<----------| 1          | color          |silv |  |
|  +----+--------+           | 1          | weight         |1.4kg|  |
|                             | 1          | screen         |14in |  |
|                             +------------+----------------+-----+  |
+------------------------------------------------------------------+
```

---

## Querying Embeddable Fields

### Derived Query Methods

```java
@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    // Query by embedded field — use dot notation
    List<Customer> findByAddressCity(String city);
    List<Customer> findByAddressState(String state);
    List<Customer> findByAddressCityAndAddressState(String city, String state);
    List<Customer> findByAddressZipCode(String zipCode);
}
```

### JPQL with Embeddable Fields

```java
// Navigate embedded fields with dot notation
@Query("SELECT c FROM Customer c WHERE c.address.city = :city")
List<Customer> findByCity(@Param("city") String city);

// Use embedded fields in SELECT
@Query("SELECT c.name, c.address.city, c.address.state FROM Customer c")
List<Object[]> findNamesAndLocations();

// Use embedded fields in ORDER BY
@Query("SELECT c FROM Customer c ORDER BY c.address.state, c.address.city")
List<Customer> findAllOrderedByLocation();
```

### Querying @ElementCollection

```java
// Find employees who have a specific skill
@Query("SELECT e FROM Employee e JOIN e.skills s WHERE s.name = :skillName")
List<Employee> findBySkill(@Param("skillName") String skillName);

// Find employees with a specific skill at a specific level
@Query("SELECT e FROM Employee e JOIN e.skills s " +
       "WHERE s.name = :skill AND s.level = :level")
List<Employee> findBySkillAndLevel(@Param("skill") String skill,
                                   @Param("level") Skill.SkillLevel level);

// Count skills per employee
@Query("SELECT e.name, SIZE(e.skills) FROM Employee e GROUP BY e.name")
List<Object[]> countSkillsPerEmployee();

// Find users with a specific role
@Query("SELECT u FROM User u JOIN u.roles r WHERE r = :role")
List<User> findByRole(@Param("role") User.Role role);
```

---

## @ElementCollection vs @OneToMany — When to Use Which

```
Decision Guide: @ElementCollection vs @OneToMany
+------------------------------------------------------------------+
|                                                                   |
|  Does the "child" data have its own identity?                     |
|  (Does it have a meaningful ID? Is it referenced elsewhere?)      |
|      |                                                            |
|   YES --> Use @OneToMany with a proper @Entity                    |
|      |    Example: Order --> OrderItem (OrderItem has its own ID,  |
|      |    quantity, price, product reference)                     |
|      |                                                            |
|    NO --> Does it have multiple fields?                            |
|           |                                                       |
|        YES --> @ElementCollection of @Embeddable                  |
|           |    Example: Employee --> Skill (name + level)          |
|           |                                                       |
|        NO  --> @ElementCollection of simple types                 |
|                Example: Employee --> phoneNumbers (Set<String>)    |
|                         User --> roles (Set<Role>)                |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  Key Differences:                                                 |
|                                                                   |
|  @ElementCollection              @OneToMany                      |
|  -------------------------       -------------------------        |
|  No ID on child                  Child has its own @Id            |
|  Child is a value object         Child is a managed entity        |
|  Cannot be shared                Can be shared (FK references)    |
|  Always owned by parent          Can exist independently          |
|  Deleted when parent deleted     Lifecycle can be independent     |
|  No lazy/eager per item          Each item independently loadable |
|  No cascading needed             Requires cascade configuration   |
|  Simpler but less flexible       More complex but more powerful   |
|                                                                   |
|  IMPORTANT: @ElementCollection replaces the ENTIRE collection     |
|  on update (DELETE all, then INSERT all). For large or            |
|  frequently modified collections, use @OneToMany instead.         |
+------------------------------------------------------------------+
```

### The Hidden Performance Trap

```
@ElementCollection Update Behavior:
+------------------------------------------------------------------+
|                                                                   |
|  Adding ONE phone number to an employee with 5 numbers:           |
|                                                                   |
|  employee.getPhoneNumbers().add("555-0106");                      |
|                                                                   |
|  Hibernate executes:                                              |
|  1. DELETE FROM employee_phone_numbers WHERE employee_id = 1      |
|  2. INSERT INTO employee_phone_numbers (employee_id, phone_number)|
|     VALUES (1, '555-0101')                                        |
|  3. INSERT ... VALUES (1, '555-0102')                             |
|  4. INSERT ... VALUES (1, '555-0103')                             |
|  5. INSERT ... VALUES (1, '555-0104')                             |
|  6. INSERT ... VALUES (1, '555-0105')                             |
|  7. INSERT ... VALUES (1, '555-0106')   <-- the new one           |
|                                                                   |
|  7 SQL statements to add 1 phone number!                          |
|  Hibernate DELETES all rows then RE-INSERTS everything.           |
|                                                                   |
|  For small, rarely-modified collections: fine.                    |
|  For large or frequently-modified collections: use @OneToMany.    |
+------------------------------------------------------------------+
```

---

## Null Embeddable Behavior

When all fields of an embedded object are null, Hibernate treats the entire embeddable as null:

```java
Customer customer = new Customer("Alice", null);  // No address
customerRepository.save(customer);

Customer found = customerRepository.findById(1L).orElseThrow();
found.getAddress();  // Returns null (not an Address with null fields)
```

```
Null Embeddable Behavior:
+------------------------------------------------------------------+
|                                                                   |
|  Database row:                                                    |
|  | id | name  | street | city | state | zip_code |               |
|  | 1  | Alice | NULL   | NULL | NULL  | NULL     |               |
|                                                                   |
|  When ALL embedded columns are NULL:                              |
|  customer.getAddress() returns NULL (not new Address(null...))    |
|                                                                   |
|  When ANY embedded column is NOT NULL:                            |
|  | id | name  | street | city   | state | zip_code |             |
|  | 2  | Bob   | NULL   | Chicago| NULL  | NULL     |             |
|  customer.getAddress() returns Address(null, "Chicago", null, null)|
|                                                                   |
|  To avoid NullPointerException, check for null:                   |
|  if (customer.getAddress() != null) {                             |
|      String city = customer.getAddress().getCity();                |
|  }                                                                |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Giving an @Embeddable class an @Id field**: Embeddable types are value objects — they do not have their own identity. If you need an ID, it should be an `@Entity`, not an `@Embeddable`.

2. **Using @ElementCollection for large collections**: Hibernate deletes and re-inserts all rows on every modification. For collections with more than a few dozen items, or collections modified frequently, use `@OneToMany` with a proper entity instead.

3. **Forgetting @AttributeOverride when embedding the same type twice**: Two `@Embedded Address` fields in the same entity will create duplicate column names. Use `@AttributeOverride` to give each set of columns unique names.

4. **Not implementing equals and hashCode on @Embeddable classes**: Value objects should be compared by their field values, not by identity. Without proper `equals()`, operations like `Set.contains()` and `List.remove()` will not work correctly.

5. **Using @ElementCollection with FetchType.EAGER unnecessarily**: The default is LAZY, which is correct for most cases. Only use EAGER for very small collections that are always needed (like user roles).

6. **Not checking for null on optional embedded fields**: When all columns of an embedded field are null, Hibernate returns `null` for the entire embeddable, which can cause `NullPointerException`.

---

## Best Practices

1. **Use @Embeddable for domain value objects**: Address, Money, DateRange, PhoneNumber — any concept that has multiple fields but no independent identity should be an embeddable.

2. **Make embeddable classes immutable when possible**: Value objects should ideally not change after creation. Provide a constructor, getters, but no setters. To "update" a value, replace the entire object.

3. **Always implement equals, hashCode, and toString**: Value objects are defined by their content, not their identity. These methods should compare all fields.

4. **Keep @ElementCollection small**: Use it for 0-20 items that rarely change (tags, roles, phone numbers). For larger or frequently modified collections, use `@OneToMany`.

5. **Use @Embedded to reduce entity bloat**: Instead of 10 address-related fields cluttering your entity, group them into an `Address` embeddable. This makes the entity cleaner and the address concept reusable.

6. **Prefer @Embeddable over creating a separate entity table**: If the data has no independent lifecycle and is always accessed with its owner, embedding is simpler and more performant (no joins needed).

---

## Summary

In this chapter, you learned how to model value objects in JPA:

- **@Embeddable** marks a class as a value object (no identity, no table, no primary key). Its fields become columns in the owning entity's table.

- **@Embedded** places an embeddable object inside an entity. The embeddable's fields are flattened into the entity's table.

- **@AttributeOverride** renames embedded columns to avoid conflicts when the same embeddable type is used multiple times.

- **@ElementCollection** stores a collection of value objects (or simple types) in a separate table linked by a foreign key. Unlike `@OneToMany`, the elements have no identity.

- **@CollectionTable** configures the table name and join column for element collections.

- **Value objects vs entities**: Value objects have no identity, belong to an entity, and cannot exist alone. Entities have their own identity and lifecycle.

- **Performance warning**: `@ElementCollection` replaces all rows on modification (DELETE + INSERT all). Use `@OneToMany` for large or frequently modified collections.

---

## Interview Questions

**Q1: What is the difference between @Embeddable and @Entity?**

An `@Entity` has its own identity (`@Id`), its own database table, and its own lifecycle — it can exist independently. An `@Embeddable` is a value object with no identity, no table, and no independent lifecycle. Its fields are embedded as columns in the owning entity's table. Use `@Entity` for things like Customer, Order, Product. Use `@Embeddable` for things like Address, Money, DateRange.

**Q2: When would you use @ElementCollection instead of @OneToMany?**

Use `@ElementCollection` when the collection items are value objects (no identity, cannot exist independently, always belong to one owner). Examples: phone numbers, tags, roles, skills. Use `@OneToMany` when the items are entities with their own identity that may be shared or have independent lifecycles. Also prefer `@OneToMany` for large collections, since `@ElementCollection` deletes and re-inserts all items on every modification.

**Q3: What happens when you embed the same @Embeddable type twice without @AttributeOverride?**

It causes a column name conflict. Both embedded fields try to create columns with the same names (e.g., two "street" columns), resulting in a mapping error at startup. Use `@AttributeOverride` to give each set of columns unique names.

**Q4: How does Hibernate handle null values for @Embedded fields?**

When ALL columns of an embedded field are null in the database, Hibernate returns `null` for the entire embeddable object (not an embeddable instance with null fields). If ANY column has a non-null value, Hibernate creates an embeddable instance.

**Q5: What is the performance concern with @ElementCollection?**

When modifying an element collection, Hibernate typically deletes ALL existing rows for that owner and re-inserts them all. Adding one element to a collection of 100 items generates 1 DELETE + 101 INSERT statements. This makes `@ElementCollection` unsuitable for large or frequently modified collections.

**Q6: Can embeddable types be nested?**

Yes. An `@Embeddable` class can contain another `@Embedded` field that references another `@Embeddable` class. For example, a `ContactInfo` embeddable can contain an `Address` embeddable. All fields from both levels are flattened into the owning entity's table columns.

---

## Practice Exercises

**Exercise 1: Address Embeddable**
Create an `Address` embeddable and use it in a `Customer` entity. Save, load, and update addresses. Query customers by city and state using derived methods.

**Exercise 2: Money Value Object**
Create a `Money` embeddable with amount and currency. Use it in a `Product` entity. Add an `@AttributeOverride` to have both `originalPrice` and `salePrice` Money fields.

**Exercise 3: Element Collection of Strings**
Add a `Set<String>` of tags to a `Product` entity using `@ElementCollection`. Write methods to add/remove tags. Query products by tag using JPQL.

**Exercise 4: Element Collection of Embeddables**
Create an `Education` embeddable (institution, degree, year) and add `@ElementCollection` of `Education` to an `Employee` entity. Save, query, and verify.

**Exercise 5: Comparison Test**
Model phone numbers both ways: (a) `@ElementCollection` of strings, and (b) `@OneToMany` with a `PhoneNumber` entity. Add 10 numbers, then add 1 more. Enable SQL logging and compare the number of SQL statements. Observe the DELETE + re-INSERT behavior of `@ElementCollection`.

---

## What Is Next?

In the next chapter, we will explore **Inheritance Mapping Strategies** — how to map Java class hierarchies (abstract classes, subclasses) to database tables. You will learn the three JPA strategies (SINGLE_TABLE, JOINED, TABLE_PER_CLASS), when to use each, and the simpler `@MappedSuperclass` alternative for sharing common fields.
