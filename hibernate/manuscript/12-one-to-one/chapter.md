# Chapter 12: One-to-One Relationships

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand when to use one-to-one relationships in a domain model
- Map unidirectional one-to-one relationships with @OneToOne and @JoinColumn
- Map bidirectional one-to-one relationships with mappedBy
- Share primary keys between related entities using @MapsId
- Control lazy vs eager loading for one-to-one associations
- Apply cascade operations to propagate persistence actions
- Choose between foreign key, shared primary key, and join table strategies
- Avoid common pitfalls in one-to-one mappings

---

## Understanding One-to-One Relationships

A one-to-one relationship means that one entity is associated with exactly one instance of another entity. Examples from the real world:

```
One-to-One Examples:
+------------------------------------------------------------------+
|                                                                   |
|  User        <------>  UserProfile                                |
|  (login info)          (bio, avatar, preferences)                 |
|                                                                   |
|  Employee    <------>  ParkingSpot                                 |
|  (employee data)       (assigned parking location)                |
|                                                                   |
|  Order       <------>  ShippingDetails                            |
|  (order info)          (tracking number, carrier, address)        |
|                                                                   |
|  Country     <------>  Capital                                    |
|  (country info)        (capital city details)                     |
|                                                                   |
+------------------------------------------------------------------+
```

### When to Use One-to-One

One-to-one relationships are appropriate when:

1. **Separation of concerns**: You want to keep a large entity manageable by splitting it into two tables (User + UserProfile)
2. **Optional data**: The related data might not exist for every row (not every employee has a parking spot)
3. **Different access patterns**: Some data is accessed frequently, other data rarely (user login vs profile details)
4. **Security isolation**: Sensitive data (salary details, medical records) in a separate table with different access controls

```
Why Split into Two Tables?
+------------------------------------------------------------------+
|                                                                   |
|  Option A: One Big Table                                          |
|  +----------------------------------------------------------+    |
|  | users                                                      |    |
|  | id | name | email | password | bio | avatar | theme | ... |    |
|  +----------------------------------------------------------+    |
|  Problems:                                                        |
|  - Wide rows (many columns) = slower queries                     |
|  - Loading login page loads ALL profile data too                  |
|  - NULL columns for users without profiles                        |
|                                                                   |
|  Option B: Two Tables with One-to-One                             |
|  +---------------------------+  +---------------------------+     |
|  | users                     |  | user_profiles             |     |
|  | id | name | email | pass  |  | id | user_id | bio | ... |     |
|  +---------------------------+  +---------------------------+     |
|  Benefits:                                                        |
|  - Narrow rows = faster queries                                  |
|  - Login page only loads users table                             |
|  - Profile data loaded on demand                                  |
|  - Clean separation of concerns                                  |
+------------------------------------------------------------------+
```

---

## Database Schema for One-to-One

There are three ways to implement one-to-one in a database:

```
Strategy 1: Foreign Key (Most Common)
+------------------------------------------------------------------+
|                                                                   |
|  users                          user_profiles                     |
|  +--------+---------+          +--------+----------+---------+    |
|  | id(PK) | name    |          | id(PK) | user_id  | bio     |    |
|  |--------+---------|          |--------+----------+---------|    |
|  | 1      | Alice   |<---+    | 10     | 1 (FK,UQ)| Hello...|    |
|  | 2      | Bob     |<---|-+  | 11     | 2 (FK,UQ)| Hi...   |    |
|  | 3      | Charlie |    | |  +--------+----------+---------+    |
|  +--------+---------+    | |                                      |
|                           | +-- user_id is a FOREIGN KEY          |
|                           +---- with a UNIQUE constraint          |
|                                 (ensures one-to-one)              |
+------------------------------------------------------------------+

Strategy 2: Shared Primary Key
+------------------------------------------------------------------+
|                                                                   |
|  users                          user_profiles                     |
|  +--------+---------+          +--------+---------+               |
|  | id(PK) | name    |          | id(PK) | bio     |               |
|  |--------+---------|          |--------+---------|               |
|  | 1      | Alice   |<------  | 1(FK)  | Hello...|               |
|  | 2      | Bob     |<------  | 2(FK)  | Hi...   |               |
|  +--------+---------+          +--------+---------+               |
|                                                                   |
|  user_profiles.id IS BOTH the primary key AND foreign key         |
|  Same value in both tables (user 1 -> profile 1)                  |
|  Most efficient: no extra column needed                           |
+------------------------------------------------------------------+

Strategy 3: Join Table (Rare for One-to-One)
+------------------------------------------------------------------+
|                                                                   |
|  users             user_profile_mapping       user_profiles       |
|  +------+------+   +----------+------------+  +------+-------+   |
|  |id(PK)|name  |   |user_id   |profile_id  |  |id(PK)|bio    |   |
|  |------+------|   |----------+------------|  |------+-------|   |
|  | 1    |Alice |   | 1(FK,UQ) | 10(FK,UQ)  |  | 10   |Hello..|   |
|  | 2    |Bob   |   | 2(FK,UQ) | 11(FK,UQ)  |  | 11   |Hi..   |   |
|  +------+------+   +----------+------------+  +------+-------+   |
|                                                                   |
|  Extra join table. Rarely used for one-to-one.                    |
|  Useful when you cannot modify either table's schema.             |
+------------------------------------------------------------------+
```

---

## Unidirectional One-to-One (Foreign Key)

The simplest form: one entity knows about the other, but not vice versa.

```
Unidirectional: User --> UserProfile
+------------------------------------------------------------------+
|                                                                   |
|  User                         UserProfile                         |
|  +-----------------------+    +-----------------------+           |
|  | id: Long              |    | id: Long              |           |
|  | name: String          |    | bio: String           |           |
|  | email: String         |    | avatarUrl: String     |           |
|  | profile: UserProfile -+--->| theme: String         |           |
|  +-----------------------+    +-----------------------+           |
|                                                                   |
|  User can access its profile: user.getProfile()                   |
|  UserProfile does NOT know about User                             |
+------------------------------------------------------------------+
```

```java
@Entity
@Table(name = "user_profiles")
public class UserProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 500)
    private String bio;

    @Column(name = "avatar_url")
    private String avatarUrl;

    @Column(length = 20)
    private String theme;

    // Default constructor required by JPA
    protected UserProfile() {}

    public UserProfile(String bio, String avatarUrl, String theme) {
        this.bio = bio;
        this.avatarUrl = avatarUrl;
        this.theme = theme;
    }

    // Getters and setters
    public Long getId() { return id; }
    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }
    public String getAvatarUrl() { return avatarUrl; }
    public void setAvatarUrl(String avatarUrl) { this.avatarUrl = avatarUrl; }
    public String getTheme() { return theme; }
    public void setTheme(String theme) { this.theme = theme; }
}
```

```java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @OneToOne(cascade = CascadeType.ALL, orphanRemoval = true)  // JPA standard
    @JoinColumn(name = "profile_id", unique = true)              // JPA standard
    private UserProfile profile;

    // Default constructor required by JPA
    protected User() {}

    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }

    // Getters and setters
    public Long getId() { return id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public UserProfile getProfile() { return profile; }
    public void setProfile(UserProfile profile) { this.profile = profile; }
}
```

### Understanding the Annotations

```
@OneToOne Breakdown:
+------------------------------------------------------------------+
|                                                                   |
|  @OneToOne(                                                       |
|      cascade = CascadeType.ALL,   // When User is saved/deleted,  |
|                                   // also save/delete the Profile |
|      orphanRemoval = true         // If profile is set to null,   |
|                                   // delete the orphaned Profile  |
|  )                                                                |
|                                                                   |
|  @JoinColumn(                                                     |
|      name = "profile_id",         // Column name in users table   |
|      unique = true                // UNIQUE constraint enforces   |
|                                   // one-to-one (not one-to-many) |
|  )                                                                |
|  private UserProfile profile;                                     |
|                                                                   |
|  Generated SQL:                                                   |
|  ALTER TABLE users ADD COLUMN profile_id BIGINT UNIQUE;           |
|  ALTER TABLE users ADD FOREIGN KEY (profile_id)                   |
|      REFERENCES user_profiles(id);                                |
+------------------------------------------------------------------+
```

### Saving and Loading

```java
@Service
@Transactional
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    // Save user with profile — cascade saves both
    public User createUserWithProfile(String name, String email,
                                       String bio, String avatarUrl) {
        User user = new User(name, email);

        UserProfile profile = new UserProfile(bio, avatarUrl, "light");
        user.setProfile(profile);  // Set the relationship

        return userRepository.save(user);  // Saves BOTH user and profile
    }

    // Loading user automatically loads profile (EAGER by default)
    public User getUser(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("User not found"));

        // profile is already loaded (EAGER is default for @OneToOne)
        System.out.println("Profile: " + user.getProfile().getBio());

        return user;
    }

    // Replace profile — orphanRemoval deletes the old one
    public void updateProfile(Long userId, String newBio) {
        User user = userRepository.findById(userId).orElseThrow();

        if (user.getProfile() != null) {
            user.getProfile().setBio(newBio);
        } else {
            user.setProfile(new UserProfile(newBio, null, "light"));
        }
        // No explicit save needed — dirty checking handles it
    }

    // Remove profile — orphanRemoval deletes the orphaned profile
    public void removeProfile(Long userId) {
        User user = userRepository.findById(userId).orElseThrow();
        user.setProfile(null);  // Profile becomes orphan, gets deleted
    }
}
```

```
Cascade in Action:
+------------------------------------------------------------------+
|                                                                   |
|  userRepository.save(user)                                        |
|       |                                                           |
|       v                                                           |
|  CascadeType.ALL means:                                          |
|  1. INSERT INTO user_profiles (bio, avatar_url, theme)            |
|     VALUES ('Hello', 'pic.jpg', 'light')  --> returns id = 10    |
|  2. INSERT INTO users (name, email, profile_id)                   |
|     VALUES ('Alice', 'alice@co.com', 10)                         |
|                                                                   |
|  userRepository.delete(user)                                      |
|       |                                                           |
|       v                                                           |
|  CascadeType.ALL means:                                          |
|  1. DELETE FROM users WHERE id = 1                                |
|  2. DELETE FROM user_profiles WHERE id = 10                       |
|                                                                   |
|  user.setProfile(null); // orphanRemoval                          |
|       |                                                           |
|       v                                                           |
|  1. UPDATE users SET profile_id = NULL WHERE id = 1               |
|  2. DELETE FROM user_profiles WHERE id = 10  (orphan removed)     |
+------------------------------------------------------------------+
```

---

## Bidirectional One-to-One

Both entities know about each other. One side is the **owning side** (has the foreign key), the other is the **inverse side** (uses `mappedBy`).

```
Bidirectional: User <--> UserProfile
+------------------------------------------------------------------+
|                                                                   |
|  User (Owning Side)               UserProfile (Inverse Side)     |
|  +-----------------------+        +-----------------------+       |
|  | id: Long              |        | id: Long              |       |
|  | name: String          |        | bio: String           |       |
|  | email: String         |        | avatarUrl: String     |       |
|  | profile: UserProfile -+------->| theme: String         |       |
|  +-----------------------+   <----+-user: User             |       |
|                                   +-----------------------+       |
|                                                                   |
|  Owning side: has @JoinColumn (foreign key in its table)          |
|  Inverse side: has mappedBy = "profile" (no FK, just a reference) |
|                                                                   |
|  user.getProfile()  --> works                                     |
|  profile.getUser()  --> also works                                |
+------------------------------------------------------------------+
```

```java
// Owning side — unchanged from unidirectional
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @OneToOne(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "profile_id", unique = true)
    private UserProfile profile;

    // Helper method to maintain both sides
    public void setProfile(UserProfile profile) {
        // Remove old profile's back-reference
        if (this.profile != null) {
            this.profile.setUser(null);
        }
        this.profile = profile;
        // Set new profile's back-reference
        if (profile != null) {
            profile.setUser(this);
        }
    }

    // ... constructors, other getters
}
```

```java
// Inverse side — add the back-reference
@Entity
@Table(name = "user_profiles")
public class UserProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 500)
    private String bio;

    @Column(name = "avatar_url")
    private String avatarUrl;

    @Column(length = 20)
    private String theme;

    @OneToOne(mappedBy = "profile")  // "profile" is the field name in User
    private User user;

    // ... constructors, getters, setters
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
}
```

```
Owning Side vs Inverse Side:
+------------------------------------------------------------------+
|                                                                   |
|  Owning Side (User)            Inverse Side (UserProfile)         |
|  ---------------------------   ---------------------------        |
|  Has @JoinColumn               Has mappedBy                      |
|  Controls the foreign key      Read-only mirror                  |
|  Database writes go here       No database column                |
|  Setting this side updates DB  Setting only this side does NOT    |
|                                update the database!              |
|                                                                   |
|  CRITICAL:                                                        |
|  user.setProfile(profile)  --> UPDATES the database               |
|  profile.setUser(user)     --> does NOT update database alone!    |
|                                                                   |
|  Always set the OWNING side. The inverse side is for navigation   |
|  convenience only.                                                |
+------------------------------------------------------------------+
```

### Importance of Helper Methods

Always use helper methods that synchronize both sides:

```java
// WRONG: Setting only the inverse side
UserProfile profile = new UserProfile("Hello", null, "light");
profile.setUser(user);  // This alone does NOT set the FK!
// Database: users.profile_id is still NULL

// CORRECT: Setting the owning side (with helper)
user.setProfile(profile);  // Helper sets BOTH sides
// Database: users.profile_id = profile.id
```

---

## Shared Primary Key with @MapsId

The most efficient one-to-one strategy: the child table uses the parent's primary key as its own primary key. No extra foreign key column is needed.

```
Shared Primary Key:
+------------------------------------------------------------------+
|                                                                   |
|  users                          user_profiles                     |
|  +--------+---------+          +--------+---------+               |
|  | id(PK) | name    |          | id(PK) | bio     |               |
|  |--------+---------|          | (FK)   |         |               |
|  | 1      | Alice   |<---------| 1      | Hello...|               |
|  | 2      | Bob     |<---------| 2      | Hi...   |               |
|  | 3      | Charlie |          +--------+---------+               |
|  +--------+---------+                                             |
|                                                                   |
|  user_profiles.id = users.id (same value)                         |
|  No separate profile_id column needed                             |
|  One less column, one less index = more efficient                 |
+------------------------------------------------------------------+
```

```java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL,
              orphanRemoval = true)
    private UserProfile profile;

    // Helper
    public void setProfile(UserProfile profile) {
        if (this.profile != null) {
            this.profile.setUser(null);
        }
        this.profile = profile;
        if (profile != null) {
            profile.setUser(this);
        }
    }

    // ... constructors, getters
}
```

```java
@Entity
@Table(name = "user_profiles")
public class UserProfile {

    @Id  // This ID will be copied from User's ID
    private Long id;

    @Column(length = 500)
    private String bio;

    @Column(name = "avatar_url")
    private String avatarUrl;

    @OneToOne
    @MapsId  // The magic: profile.id = user.id
    @JoinColumn(name = "id")  // The FK column IS the PK column
    private User user;

    protected UserProfile() {}

    public UserProfile(String bio, String avatarUrl) {
        this.bio = bio;
        this.avatarUrl = avatarUrl;
    }

    // Getters and setters
    public Long getId() { return id; }
    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }
    public String getAvatarUrl() { return avatarUrl; }
    public void setAvatarUrl(String avatarUrl) { this.avatarUrl = avatarUrl; }
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
}
```

```
How @MapsId Works:
+------------------------------------------------------------------+
|                                                                   |
|  1. User is saved:                                                |
|     INSERT INTO users (name, email) VALUES ('Alice', 'a@co.com')  |
|     --> Generated id = 1                                          |
|                                                                   |
|  2. UserProfile is saved (via cascade):                           |
|     @MapsId copies user.id into profile.id automatically          |
|     INSERT INTO user_profiles (id, bio, avatar_url)               |
|     VALUES (1, 'Hello', 'pic.jpg')                                |
|            ^                                                      |
|            |-- Same value as user.id!                             |
|                                                                   |
|  3. Loading profile by user ID is instant:                        |
|     SELECT * FROM user_profiles WHERE id = 1                      |
|     (PK lookup - the fastest possible query)                      |
|                                                                   |
|  No @GeneratedValue on UserProfile.id!                            |
|  The ID comes from the User, not from the database.               |
+------------------------------------------------------------------+
```

### When to Use @MapsId

```
Strategy Comparison:
+------------------------------------------------------------------+
|                                                                   |
|  Strategy          Extra Column?  Lookup Speed   Recommended?     |
|  ----------------------------------------------------------------|
|  Foreign Key       Yes (FK col)   FK index       Good default     |
|  (@JoinColumn)                    lookup                          |
|                                                                   |
|  Shared PK         No             PK lookup      Best for true    |
|  (@MapsId)                        (fastest)      1:1 always       |
|                                                                   |
|  Join Table        Yes (whole     Two joins      Only for legacy  |
|  (@JoinTable)      extra table)   (slowest)      schemas          |
|                                                                   |
|  Use @MapsId when:                                                |
|  - The child entity ALWAYS exists with its parent                 |
|  - You want maximum performance (PK lookups)                      |
|  - You do not need independent IDs                                |
|                                                                   |
|  Use Foreign Key when:                                            |
|  - The relationship is optional (child may not exist)             |
|  - The child might be shared or reassigned                        |
|  - You need independent auto-generated IDs                        |
+------------------------------------------------------------------+
```

---

## Lazy Loading with One-to-One

By default, `@OneToOne` uses `FetchType.EAGER` — the related entity is loaded immediately with the parent. This can be a performance concern.

```
Default @OneToOne Fetching:
+------------------------------------------------------------------+
|                                                                   |
|  userRepository.findById(1L);                                     |
|                                                                   |
|  SQL Generated (EAGER, default):                                  |
|  SELECT u.*, p.*                                                  |
|  FROM users u                                                     |
|  LEFT JOIN user_profiles p ON u.profile_id = p.id                 |
|  WHERE u.id = 1                                                   |
|                                                                   |
|  Always loads profile even if you only need user.name!            |
+------------------------------------------------------------------+
```

### Setting Lazy Loading

```java
@OneToOne(fetch = FetchType.LAZY, cascade = CascadeType.ALL)
@JoinColumn(name = "profile_id", unique = true)
private UserProfile profile;
```

### The Lazy Loading Caveat for @OneToOne

**Important**: Lazy loading on the **inverse side** (mappedBy) of a `@OneToOne` does not always work as expected with standard JPA:

```
Lazy Loading Caveat:
+------------------------------------------------------------------+
|                                                                   |
|  Owning Side (has @JoinColumn):                                   |
|  @OneToOne(fetch = FetchType.LAZY)                                |
|  @JoinColumn(name = "profile_id")                                 |
|  private UserProfile profile;                                     |
|  --> LAZY works correctly                                         |
|  --> Hibernate creates a proxy (loads on first access)            |
|                                                                   |
|  Inverse Side (has mappedBy):                                     |
|  @OneToOne(mappedBy = "user", fetch = FetchType.LAZY)             |
|  private User user;                                               |
|  --> LAZY may NOT work!                                           |
|  --> Hibernate cannot create a proxy because it does not know     |
|      if the relationship is null or not without querying           |
|  --> It must query to check, which defeats the purpose of LAZY    |
|                                                                   |
|  Solutions:                                                       |
|  1. Use @MapsId (shared PK) — eliminates the problem              |
|  2. Use optional = false if always present                        |
|  3. Accept eager loading on the inverse side                      |
|  4. Use Hibernate bytecode enhancement (advanced)                 |
+------------------------------------------------------------------+
```

```java
// Making lazy work on inverse side with optional = false
@OneToOne(mappedBy = "user", fetch = FetchType.LAZY, optional = false)
private UserProfile profile;
// Tells Hibernate: profile is NEVER null, so it can safely create a proxy
```

---

## Optional vs Required Relationships

```java
// Optional (default) — profile may be null
@OneToOne(cascade = CascadeType.ALL, optional = true)  // default is true
@JoinColumn(name = "profile_id", unique = true)
private UserProfile profile;

// Required — profile must always exist
@OneToOne(cascade = CascadeType.ALL, optional = false)
@JoinColumn(name = "profile_id", nullable = false, unique = true)
private UserProfile profile;
```

```
Optional vs Required:
+------------------------------------------------------------------+
|                                                                   |
|  optional = true (default):                                       |
|  - LEFT JOIN used when loading                                    |
|  - profile_id column can be NULL                                  |
|  - user.getProfile() may return null                              |
|  - Use when: not all users have profiles                          |
|                                                                   |
|  optional = false:                                                |
|  - INNER JOIN used when loading (more efficient)                  |
|  - profile_id column is NOT NULL                                  |
|  - user.getProfile() never returns null                           |
|  - Use when: every user MUST have a profile                       |
|  - Also helps lazy loading work on the inverse side               |
+------------------------------------------------------------------+
```

---

## Complete Example: Employee and ParkingSpot

A practical bidirectional one-to-one with @MapsId:

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

    @OneToOne(mappedBy = "employee", cascade = CascadeType.ALL,
              orphanRemoval = true, fetch = FetchType.LAZY)
    private ParkingSpot parkingSpot;

    protected Employee() {}

    public Employee(String name, String email) {
        this.name = name;
        this.email = email;
    }

    // Convenience method — keeps both sides in sync
    public void assignParkingSpot(String spotNumber, String level) {
        ParkingSpot spot = new ParkingSpot(spotNumber, level);
        spot.setEmployee(this);
        this.parkingSpot = spot;
    }

    public void removeParkingSpot() {
        if (this.parkingSpot != null) {
            this.parkingSpot.setEmployee(null);
            this.parkingSpot = null;  // orphanRemoval deletes it
        }
    }

    // Getters
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public ParkingSpot getParkingSpot() { return parkingSpot; }
}
```

```java
@Entity
@Table(name = "parking_spots")
public class ParkingSpot {

    @Id
    private Long id;

    @Column(name = "spot_number", nullable = false)
    private String spotNumber;

    @Column(nullable = false)
    private String level;

    @OneToOne
    @MapsId
    @JoinColumn(name = "id")
    private Employee employee;

    protected ParkingSpot() {}

    public ParkingSpot(String spotNumber, String level) {
        this.spotNumber = spotNumber;
        this.level = level;
    }

    // Getters and setters
    public Long getId() { return id; }
    public String getSpotNumber() { return spotNumber; }
    public void setSpotNumber(String spotNumber) { this.spotNumber = spotNumber; }
    public String getLevel() { return level; }
    public void setLevel(String level) { this.level = level; }
    public Employee getEmployee() { return employee; }
    public void setEmployee(Employee employee) { this.employee = employee; }
}
```

### Repository and Service

```java
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    @EntityGraph(attributePaths = {"parkingSpot"})
    Optional<Employee> findByEmail(String email);

    @Query("SELECT e FROM Employee e LEFT JOIN FETCH e.parkingSpot WHERE e.parkingSpot IS NOT NULL")
    List<Employee> findAllWithParkingSpots();
}
```

```java
@Service
@Transactional
public class ParkingService {

    private final EmployeeRepository employeeRepository;

    public ParkingService(EmployeeRepository employeeRepository) {
        this.employeeRepository = employeeRepository;
    }

    public void assignSpot(Long employeeId, String spotNumber, String level) {
        Employee employee = employeeRepository.findById(employeeId)
            .orElseThrow(() -> new RuntimeException("Employee not found"));

        employee.assignParkingSpot(spotNumber, level);
        // Cascade saves the ParkingSpot automatically
    }

    public void removeSpot(Long employeeId) {
        Employee employee = employeeRepository.findById(employeeId)
            .orElseThrow(() -> new RuntimeException("Employee not found"));

        employee.removeParkingSpot();
        // orphanRemoval deletes the ParkingSpot automatically
    }

    public String getSpotInfo(Long employeeId) {
        Employee employee = employeeRepository.findById(employeeId)
            .orElseThrow(() -> new RuntimeException("Employee not found"));

        ParkingSpot spot = employee.getParkingSpot();
        if (spot == null) {
            return employee.getName() + " has no assigned parking spot";
        }
        return employee.getName() + " - Spot " + spot.getSpotNumber() +
               " (Level " + spot.getLevel() + ")";
    }
}
```

### Testing

```java
@SpringBootTest
@Transactional
class ParkingServiceTest {

    @Autowired
    private ParkingService parkingService;

    @Autowired
    private EmployeeRepository employeeRepository;

    @Test
    void shouldAssignAndRemoveParkingSpot() {
        // Create employee
        Employee emp = new Employee("Alice", "alice@company.com");
        employeeRepository.save(emp);

        // Assign parking spot
        parkingService.assignSpot(emp.getId(), "A-15", "Ground");

        // Verify
        Employee loaded = employeeRepository.findById(emp.getId()).orElseThrow();
        assertNotNull(loaded.getParkingSpot());
        assertEquals("A-15", loaded.getParkingSpot().getSpotNumber());
        assertEquals("Ground", loaded.getParkingSpot().getLevel());
        assertEquals(loaded.getId(), loaded.getParkingSpot().getId()); // Same ID!

        // Remove parking spot
        parkingService.removeSpot(emp.getId());

        // Verify removal
        Employee reloaded = employeeRepository.findById(emp.getId()).orElseThrow();
        assertNull(reloaded.getParkingSpot());
    }
}
```

---

## Common Mistakes

1. **Only setting the inverse side (mappedBy) and expecting the FK to update**:
   ```java
   // WRONG
   profile.setUser(user);  // inverse side only — FK not updated!
   // CORRECT
   user.setProfile(profile);  // owning side — FK IS updated
   ```

2. **Forgetting `unique = true` on @JoinColumn**: Without the unique constraint, the database allows multiple rows referencing the same parent — making it a one-to-many relationship at the database level.

3. **Using @GeneratedValue with @MapsId**: When using `@MapsId`, the ID is copied from the parent entity. Adding `@GeneratedValue` causes a conflict. Remove it from the child entity.

4. **Not using helper methods for bidirectional relationships**: Failing to synchronize both sides leads to inconsistent in-memory state, even if the database is correct after flush.

5. **Assuming LAZY works on the inverse side**: The `mappedBy` side of `@OneToOne` often loads eagerly regardless of `FetchType.LAZY` setting. Use `@MapsId` or `optional = false` to mitigate.

6. **Cascading in both directions**: Having `cascade = CascadeType.ALL` on both sides of a bidirectional relationship can cause issues. Cascade from the parent (owning side) only.

---

## Best Practices

1. **Prefer @MapsId for true one-to-one**: When the child entity always exists with its parent and has no independent identity, shared primary keys are the most efficient mapping.

2. **Keep cascade on the parent side only**: The parent entity should cascade operations to the child. The inverse side (mappedBy) should not cascade back.

3. **Use bidirectional helper methods**: Write methods like `setProfile()` that synchronize both sides of the relationship to prevent inconsistencies.

4. **Set fetch = FetchType.LAZY on the owning side**: Override the default EAGER loading when you do not always need the related entity. Use `@EntityGraph` to eagerly load it when needed.

5. **Use orphanRemoval for owned children**: When the child cannot exist without the parent (like a UserProfile without a User), enable `orphanRemoval = true`.

6. **Mark required relationships with optional = false**: This generates NOT NULL constraints, uses INNER JOIN (faster), and helps lazy loading work on inverse sides.

---

## Summary

In this chapter, you learned how to map one-to-one relationships:

- **@OneToOne** marks a single-valued association. By default it is EAGER fetched. Use `@JoinColumn` on the owning side to define the foreign key column.

- **Unidirectional** means only one entity references the other. **Bidirectional** means both entities reference each other, with `mappedBy` on the inverse side.

- **@MapsId** creates a shared primary key — the child's ID equals the parent's ID. This is the most efficient strategy for true one-to-one relationships.

- **The owning side** (with `@JoinColumn`) controls the foreign key. Always set the owning side. The inverse side (`mappedBy`) is for navigation convenience only.

- **Cascade** propagates operations from parent to child. **orphanRemoval** deletes children that are no longer referenced.

- **Lazy loading** works reliably on the owning side but may not work on the inverse side (mappedBy) of `@OneToOne` without `@MapsId` or `optional = false`.

- **Helper methods** that synchronize both sides of a bidirectional relationship are essential for consistent in-memory state.

---

## Interview Questions

**Q1: What is the difference between unidirectional and bidirectional one-to-one?**

Unidirectional: only one entity has a reference to the other (e.g., User has UserProfile, but UserProfile does not know about User). Bidirectional: both entities reference each other. The owning side has `@JoinColumn`, the inverse side has `@OneToOne(mappedBy = "fieldName")`.

**Q2: What does @MapsId do and when would you use it?**

`@MapsId` makes the child entity use the parent entity's primary key as its own primary key. The child's ID equals the parent's ID. Use it for true one-to-one relationships where the child always exists with the parent and does not need an independent identity. It eliminates an extra column and provides the fastest lookup (PK-based).

**Q3: Why is it important to set the owning side in a bidirectional relationship?**

The owning side (the entity with `@JoinColumn`) controls the foreign key in the database. Only changes made to the owning side are persisted. If you only set the inverse side (`mappedBy`), the database foreign key is not updated, even though the in-memory state appears correct.

**Q4: Does lazy loading work on both sides of a @OneToOne bidirectional relationship?**

Lazy loading works reliably on the owning side (where `@JoinColumn` is). On the inverse side (`mappedBy`), lazy loading may not work because Hibernate cannot determine if the relationship is null without querying the database. Solutions include using `@MapsId`, setting `optional = false`, or using Hibernate bytecode enhancement.

**Q5: What is the difference between orphanRemoval and CascadeType.REMOVE?**

`CascadeType.REMOVE` deletes the child when the parent is deleted. `orphanRemoval = true` also deletes the child when the relationship is broken (e.g., `user.setProfile(null)`). orphanRemoval is a superset of CascadeType.REMOVE — it covers both parent deletion and relationship removal.

**Q6: What happens if you forget `unique = true` on @JoinColumn for a one-to-one?**

Without the unique constraint, the database allows multiple entities to reference the same target, effectively making it a one-to-many relationship at the database level. JPA will still treat it as one-to-one in your Java code, but the database constraint is not enforced, which could lead to data integrity issues.

---

## Practice Exercises

**Exercise 1: Unidirectional One-to-One**
Create `Order` and `ShippingDetails` entities with a unidirectional `@OneToOne` from Order to ShippingDetails. Use `CascadeType.ALL`. Write a service that creates an order with shipping details and test it.

**Exercise 2: Bidirectional with @MapsId**
Create `Student` and `StudentCard` entities with a bidirectional one-to-one using `@MapsId`. The StudentCard should share the Student's primary key. Write helper methods and test that both sides stay synchronized.

**Exercise 3: Lazy Loading Verification**
Create a one-to-one relationship with `FetchType.LAZY`. Enable SQL logging and verify:
(a) That accessing the parent does NOT load the child immediately
(b) That accessing the child triggers a second query
(c) That using `@EntityGraph` loads both in one query

**Exercise 4: orphanRemoval**
Create entities where the child uses `orphanRemoval = true`. Test three scenarios:
(a) Saving parent with child (cascade)
(b) Replacing the child with a new one (old child should be deleted)
(c) Setting the child to null (old child should be deleted)

**Exercise 5: Strategy Comparison**
Implement the same one-to-one relationship (Country and Capital) three ways: foreign key, shared primary key (@MapsId), and join table. Enable SQL logging and compare the generated schema and queries for each strategy.

---

## What Is Next?

In the next chapter, we will explore **One-to-Many and Many-to-One Relationships** — the most common relationship type in database modeling. You will learn how to map parent-child relationships, understand the owning side concept in a many-to-one context, write bidirectional helper methods, and avoid the common pitfalls of collection-valued associations.
