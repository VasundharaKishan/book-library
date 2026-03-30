# Chapter 14: Many-to-Many Relationships

---

## Learning Goals

By the end of this chapter, you will be able to:

- Understand many-to-many relationships and how they are stored in databases
- Map @ManyToMany with @JoinTable in JPA
- Configure join table column names with @JoinColumn and @InverseJoinColumn
- Implement bidirectional many-to-many with helper methods
- Add extra columns to a join table by converting to two @OneToMany relationships
- Choose between Set and List for many-to-many collections
- Understand the equals/hashCode contract for entities in Sets
- Query many-to-many relationships with JPQL and derived methods
- Avoid common performance pitfalls with many-to-many

---

## Understanding Many-to-Many Relationships

A many-to-many relationship exists when entities on both sides can be associated with multiple entities on the other side.

```
Many-to-Many Examples:
+------------------------------------------------------------------+
|                                                                   |
|  Student >----< Course     (A student takes many courses,         |
|                             a course has many students)           |
|                                                                   |
|  Book >----< Author        (A book can have many authors,         |
|                             an author can write many books)       |
|                                                                   |
|  User >----< Role          (A user can have many roles,           |
|                             a role can be assigned to many users) |
|                                                                   |
|  Product >----< Tag        (A product can have many tags,         |
|                             a tag applies to many products)       |
|                                                                   |
|  Employee >----< Project   (An employee works on many projects,   |
|                             a project has many employees)         |
|                                                                   |
|  Legend:  >----<  means "many-to-many"                            |
+------------------------------------------------------------------+
```

### How Databases Store Many-to-Many

Relational databases cannot represent many-to-many directly. They use a **join table** (also called an association table, junction table, or link table):

```
Database Schema for Student-Course:
+------------------------------------------------------------------+
|                                                                   |
|  students              student_courses           courses          |
|  +------+--------+    +------------+-----------+ +------+-------+ |
|  |id(PK)| name   |    |student_id  | course_id | |id(PK)| title | |
|  |------+--------|    |  (FK)      |   (FK)    | |------+-------| |
|  | 1    | Alice  |    | 1          | 101       | | 101  | Math  | |
|  | 2    | Bob    |    | 1          | 102       | | 102  | Sci   | |
|  | 3    | Carol  |    | 2          | 101       | | 103  | Eng   | |
|  +------+--------+    | 2          | 103       | +------+-------+ |
|                        | 3          | 102       |                 |
|                        +------------+-----------+                 |
|                                                                   |
|  Reading the join table:                                          |
|  Alice (1) takes Math (101) and Sci (102)                        |
|  Bob (2) takes Math (101) and Eng (103)                          |
|  Carol (3) takes Sci (102)                                       |
|                                                                   |
|  The join table has:                                              |
|  - NO primary key of its own (composite PK of both FKs)          |
|  - ONLY foreign keys (no extra data)                              |
|  - Two FK columns referencing each side                           |
+------------------------------------------------------------------+
```

---

## Basic @ManyToMany Mapping

### The Owning Side

One side must be the owning side (defines the `@JoinTable`). By convention, choose whichever side makes more sense as the "primary" entity:

```java
@Entity
@Table(name = "students")
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @ManyToMany                                        // JPA standard
    @JoinTable(
        name = "student_courses",                      // Join table name
        joinColumns = @JoinColumn(name = "student_id"),       // FK to this entity
        inverseJoinColumns = @JoinColumn(name = "course_id")  // FK to the other entity
    )
    private Set<Course> courses = new HashSet<>();

    protected Student() {}

    public Student(String name, String email) {
        this.name = name;
        this.email = email;
    }

    // ===== Helper Methods =====
    public void enrollIn(Course course) {
        courses.add(course);
        course.getStudentsInternal().add(this);
    }

    public void dropCourse(Course course) {
        courses.remove(course);
        course.getStudentsInternal().remove(this);
    }

    // Getters
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public Set<Course> getCourses() {
        return Collections.unmodifiableSet(courses);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Student student = (Student) o;
        return email != null && email.equals(student.email);
    }

    @Override
    public int hashCode() {
        return email != null ? email.hashCode() : 0;
    }
}
```

```
@JoinTable Annotation Breakdown:
+------------------------------------------------------------------+
|                                                                   |
|  @JoinTable(                                                      |
|      name = "student_courses",    // Name of the join table       |
|                                                                   |
|      joinColumns = @JoinColumn(   // FK pointing to THIS entity   |
|          name = "student_id"      // (Student.id)                 |
|      ),                                                           |
|                                                                   |
|      inverseJoinColumns =         // FK pointing to the OTHER     |
|          @JoinColumn(             // entity (Course.id)           |
|              name = "course_id"                                   |
|          )                                                        |
|  )                                                                |
|                                                                   |
|  Generated DDL:                                                   |
|  CREATE TABLE student_courses (                                   |
|      student_id BIGINT NOT NULL,                                  |
|      course_id BIGINT NOT NULL,                                   |
|      PRIMARY KEY (student_id, course_id),                         |
|      FOREIGN KEY (student_id) REFERENCES students(id),            |
|      FOREIGN KEY (course_id) REFERENCES courses(id)               |
|  );                                                               |
+------------------------------------------------------------------+
```

### The Inverse Side

```java
@Entity
@Table(name = "courses")
public class Course {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private int credits;

    @ManyToMany(mappedBy = "courses")   // Inverse side — points to owning field
    private Set<Student> students = new HashSet<>();

    protected Course() {}

    public Course(String title, int credits) {
        this.title = title;
        this.credits = credits;
    }

    // Internal access for helper methods (package-private)
    Set<Student> getStudentsInternal() {
        return students;
    }

    // Getters
    public Long getId() { return id; }
    public String getTitle() { return title; }
    public int getCredits() { return credits; }
    public Set<Student> getStudents() {
        return Collections.unmodifiableSet(students);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Course course = (Course) o;
        return title != null && title.equals(course.title);
    }

    @Override
    public int hashCode() {
        return title != null ? title.hashCode() : 0;
    }
}
```

```
Bidirectional @ManyToMany:
+------------------------------------------------------------------+
|                                                                   |
|  Student (Owning Side)              Course (Inverse Side)         |
|  +---------------------------+     +---------------------------+  |
|  | @ManyToMany               |     | @ManyToMany(              |  |
|  | @JoinTable(               |     |   mappedBy = "courses")   |  |
|  |   name="student_courses", |     | Set<Student> students     |  |
|  |   joinColumns=...,        |     +---------------------------+  |
|  |   inverseJoinColumns=...) |                                    |
|  | Set<Course> courses       |                                    |
|  +---------------------------+                                    |
|                                                                   |
|  The owning side defines the @JoinTable.                          |
|  The inverse side uses mappedBy.                                  |
|  Helper methods on the owning side update BOTH sides.             |
+------------------------------------------------------------------+
```

---

## Working with Many-to-Many

### Enrolling Students in Courses

```java
@Service
@Transactional
public class EnrollmentService {

    private final StudentRepository studentRepository;
    private final CourseRepository courseRepository;

    public EnrollmentService(StudentRepository studentRepository,
                             CourseRepository courseRepository) {
        this.studentRepository = studentRepository;
        this.courseRepository = courseRepository;
    }

    public void enrollStudentInCourse(Long studentId, Long courseId) {
        Student student = studentRepository.findById(studentId).orElseThrow();
        Course course = courseRepository.findById(courseId).orElseThrow();

        student.enrollIn(course);
        // Helper method updates both sides
        // Hibernate inserts into student_courses join table
    }

    public void dropStudentFromCourse(Long studentId, Long courseId) {
        Student student = studentRepository.findById(studentId).orElseThrow();
        Course course = courseRepository.findById(courseId).orElseThrow();

        student.dropCourse(course);
        // Helper method removes from both sides
        // Hibernate deletes from student_courses join table
    }
}
```

```
Enroll Flow (SQL Generated):
+------------------------------------------------------------------+
|                                                                   |
|  student.enrollIn(course);                                        |
|                                                                   |
|  1. Hibernate detects change in courses Set (dirty checking)      |
|  2. On flush:                                                     |
|     INSERT INTO student_courses (student_id, course_id)           |
|     VALUES (1, 101)                                               |
|                                                                   |
|  student.dropCourse(course);                                      |
|                                                                   |
|  1. Hibernate detects removal from courses Set                    |
|  2. On flush:                                                     |
|     DELETE FROM student_courses                                   |
|     WHERE student_id = 1 AND course_id = 101                     |
|                                                                   |
|  Note: Only the join table is affected.                           |
|  The students and courses tables are NOT modified.                |
+------------------------------------------------------------------+
```

### Loading Data

```java
// Load student with courses eagerly
@Repository
public interface StudentRepository extends JpaRepository<Student, Long> {

    @EntityGraph(attributePaths = {"courses"})
    Optional<Student> findWithCoursesById(Long id);

    @Query("SELECT DISTINCT s FROM Student s LEFT JOIN FETCH s.courses " +
           "WHERE s.name LIKE %:name%")
    List<Student> searchWithCourses(@Param("name") String name);
}

@Repository
public interface CourseRepository extends JpaRepository<Course, Long> {

    @EntityGraph(attributePaths = {"students"})
    Optional<Course> findWithStudentsById(Long id);

    @Query("SELECT c FROM Course c WHERE SIZE(c.students) >= :min")
    List<Course> findPopularCourses(@Param("min") int min);
}
```

---

## Why Set Is Preferred Over List for @ManyToMany

```
List vs Set for @ManyToMany:
+------------------------------------------------------------------+
|                                                                   |
|  With List<Course>:                                               |
|  student.dropCourse(course);                                      |
|                                                                   |
|  Hibernate generates:                                             |
|  1. DELETE FROM student_courses WHERE student_id = 1  (ALL rows!) |
|  2. INSERT INTO student_courses (student_id, course_id)           |
|     VALUES (1, 102)                                 (re-insert!)  |
|  3. INSERT INTO student_courses (student_id, course_id)           |
|     VALUES (1, 103)                                 (re-insert!)  |
|                                                                   |
|  Removes ALL entries, then re-inserts the remaining ones!         |
|  If the student has 50 courses and drops 1: 1 DELETE + 49 INSERTs |
|                                                                   |
|  With Set<Course>:                                                |
|  student.dropCourse(course);                                      |
|                                                                   |
|  Hibernate generates:                                             |
|  1. DELETE FROM student_courses                                   |
|     WHERE student_id = 1 AND course_id = 101       (just 1 row!) |
|                                                                   |
|  Removes ONLY the specific entry! Much more efficient.            |
|                                                                   |
|  RULE: Always use Set<T> for @ManyToMany collections.             |
|  List<T> causes terrible performance on modifications.            |
+------------------------------------------------------------------+
```

This is one of the most important performance rules in Hibernate. Using `List` for `@ManyToMany` causes Hibernate to delete and recreate all join table entries whenever the collection changes. Using `Set` allows surgical inserts and deletes.

---

## Adding Extra Columns to the Join Table

The basic `@ManyToMany` only supports a join table with two foreign key columns. But what if you need extra columns?

```
Problem: Need Extra Data in the Relationship:
+------------------------------------------------------------------+
|                                                                   |
|  Student enrolls in Course:                                       |
|  - enrollment_date: When did they enroll?                         |
|  - grade: What grade did they receive?                            |
|  - semester: Which semester?                                      |
|                                                                   |
|  These cannot be stored with @ManyToMany!                         |
|  @ManyToMany only creates a join table with two FK columns.       |
|                                                                   |
|  Solution: Create an explicit join ENTITY                         |
|  and use two @ManyToOne / @OneToMany relationships instead.       |
|                                                                   |
|  Before:                                                          |
|  Student >----< Course                                            |
|  (simple @ManyToMany, no extra columns)                           |
|                                                                   |
|  After:                                                           |
|  Student ----< Enrollment >---- Course                            |
|  (two @OneToMany through an Enrollment entity)                    |
+------------------------------------------------------------------+
```

### The Enrollment Entity (Join Entity)

```java
@Entity
@Table(name = "enrollments")
public class Enrollment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "student_id", nullable = false)
    private Student student;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "course_id", nullable = false)
    private Course course;

    // ===== Extra columns! =====
    @Column(name = "enrolled_at", nullable = false)
    private LocalDate enrolledAt;

    @Column(length = 2)
    private String grade;    // "A", "B+", "C", etc.

    @Column(nullable = false, length = 20)
    private String semester;  // "Fall 2025", "Spring 2026"

    protected Enrollment() {}

    public Enrollment(Student student, Course course, String semester) {
        this.student = student;
        this.course = course;
        this.semester = semester;
        this.enrolledAt = LocalDate.now();
    }

    // Getters and setters
    public Long getId() { return id; }
    public Student getStudent() { return student; }
    public Course getCourse() { return course; }
    public LocalDate getEnrolledAt() { return enrolledAt; }
    public String getGrade() { return grade; }
    public void setGrade(String grade) { this.grade = grade; }
    public String getSemester() { return semester; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Enrollment that = (Enrollment) o;
        return student != null && course != null &&
               student.equals(that.student) && course.equals(that.course) &&
               semester != null && semester.equals(that.semester);
    }

    @Override
    public int hashCode() {
        return Objects.hash(
            student != null ? student.getEmail() : null,
            course != null ? course.getTitle() : null,
            semester
        );
    }
}
```

### Updated Student and Course Entities

```java
@Entity
@Table(name = "students")
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @OneToMany(mappedBy = "student", cascade = CascadeType.ALL,
               orphanRemoval = true)
    private Set<Enrollment> enrollments = new HashSet<>();

    protected Student() {}

    public Student(String name, String email) {
        this.name = name;
        this.email = email;
    }

    // Helper methods
    public Enrollment enrollIn(Course course, String semester) {
        Enrollment enrollment = new Enrollment(this, course, semester);
        enrollments.add(enrollment);
        course.getEnrollmentsInternal().add(enrollment);
        return enrollment;
    }

    public void drop(Course course, String semester) {
        enrollments.removeIf(e ->
            e.getCourse().equals(course) && e.getSemester().equals(semester));
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public Set<Enrollment> getEnrollments() {
        return Collections.unmodifiableSet(enrollments);
    }

    // equals/hashCode based on email (same as before)
}
```

```java
@Entity
@Table(name = "courses")
public class Course {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    private int credits;

    @OneToMany(mappedBy = "course", cascade = CascadeType.ALL,
               orphanRemoval = true)
    private Set<Enrollment> enrollments = new HashSet<>();

    protected Course() {}

    public Course(String title, int credits) {
        this.title = title;
        this.credits = credits;
    }

    Set<Enrollment> getEnrollmentsInternal() {
        return enrollments;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public int getCredits() { return credits; }
    public Set<Enrollment> getEnrollments() {
        return Collections.unmodifiableSet(enrollments);
    }

    // equals/hashCode based on title (same as before)
}
```

```
Database Schema with Join Entity:
+------------------------------------------------------------------+
|                                                                   |
|  students             enrollments              courses            |
|  +------+--------+   +------+------+------+   +------+-------+   |
|  |id(PK)| name   |   |id(PK)|stu_id|crs_id|  |id(PK)| title |   |
|  |------+--------|   |      |(FK)  |(FK)  |   |------+-------|   |
|  | 1    | Alice  |   | 1    | 1    | 101  |   | 101  | Math  |   |
|  | 2    | Bob    |   | 2    | 1    | 102  |   | 102  | Sci   |   |
|  +------+--------+   | 3    | 2    | 101  |   | 103  | Eng   |   |
|                       +------+------+------+   +------+-------+   |
|                       |enrolled_at  |grade |                      |
|                       |-------------|------|                      |
|                       |2025-09-01   | A    |                      |
|                       |2025-09-01   | B+   |                      |
|                       |2025-09-05   | null |                      |
|                       +-------------+------+                      |
|                                                                   |
|  Now we can store enrollment_date, grade, semester, etc.          |
|  Each enrollment is its own entity with its own id.               |
+------------------------------------------------------------------+
```

### Using the Join Entity

```java
@Service
@Transactional
public class EnrollmentService {

    private final StudentRepository studentRepository;
    private final CourseRepository courseRepository;
    private final EnrollmentRepository enrollmentRepository;

    // Constructor...

    public void enroll(Long studentId, Long courseId, String semester) {
        Student student = studentRepository.findById(studentId).orElseThrow();
        Course course = courseRepository.findById(courseId).orElseThrow();
        student.enrollIn(course, semester);
    }

    public void assignGrade(Long enrollmentId, String grade) {
        Enrollment enrollment = enrollmentRepository.findById(enrollmentId)
            .orElseThrow();
        enrollment.setGrade(grade);
    }

    @Transactional(readOnly = true)
    public List<Enrollment> getStudentTranscript(Long studentId) {
        return enrollmentRepository.findByStudentIdOrderBySemesterDesc(studentId);
    }

    @Transactional(readOnly = true)
    public double getStudentGPA(Long studentId) {
        return enrollmentRepository.findByStudentId(studentId).stream()
            .filter(e -> e.getGrade() != null)
            .mapToDouble(this::gradeToPoints)
            .average()
            .orElse(0.0);
    }

    private double gradeToPoints(Enrollment e) {
        return switch (e.getGrade()) {
            case "A" -> 4.0;
            case "A-" -> 3.7;
            case "B+" -> 3.3;
            case "B" -> 3.0;
            case "B-" -> 2.7;
            case "C+" -> 2.3;
            case "C" -> 2.0;
            default -> 0.0;
        };
    }
}
```

```java
@Repository
public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {

    List<Enrollment> findByStudentId(Long studentId);
    List<Enrollment> findByStudentIdOrderBySemesterDesc(Long studentId);
    List<Enrollment> findByCourseId(Long courseId);
    List<Enrollment> findBySemester(String semester);

    @Query("SELECT e FROM Enrollment e JOIN FETCH e.course " +
           "WHERE e.student.id = :studentId AND e.grade IS NOT NULL")
    List<Enrollment> findGradedByStudent(@Param("studentId") Long studentId);

    @Query("SELECT e.course.title, AVG(CASE " +
           "WHEN e.grade = 'A' THEN 4.0 WHEN e.grade = 'B' THEN 3.0 " +
           "WHEN e.grade = 'C' THEN 2.0 ELSE 0 END) " +
           "FROM Enrollment e WHERE e.grade IS NOT NULL " +
           "GROUP BY e.course.title ORDER BY 2 DESC")
    List<Object[]> getCourseAverageGrades();

    boolean existsByStudentIdAndCourseIdAndSemester(
        Long studentId, Long courseId, String semester);
}
```

---

## @ManyToMany vs Join Entity: Decision Guide

```
When to Use Which:
+------------------------------------------------------------------+
|                                                                   |
|  Use @ManyToMany when:                                            |
|  +-------------------------------+                                |
|  | - Join table has ONLY two FKs |                                |
|  | - No extra data on the link   |                                |
|  | - Simple tag/label/role       |                                |
|  |   associations                |                                |
|  | - You do not need to query    |                                |
|  |   the relationship itself     |                                |
|  +-------------------------------+                                |
|                                                                   |
|  Examples:                                                        |
|  - Product <-> Tag                                                |
|  - User <-> Role                                                  |
|  - Article <-> Category                                           |
|                                                                   |
|  Use Join Entity when:                                            |
|  +-------------------------------+                                |
|  | - Join table needs extra      |                                |
|  |   columns (date, status,     |                                |
|  |   quantity, grade, etc.)      |                                |
|  | - You need to query the       |                                |
|  |   relationship itself         |                                |
|  | - The link has its own        |                                |
|  |   lifecycle                   |                                |
|  +-------------------------------+                                |
|                                                                   |
|  Examples:                                                        |
|  - Student <-> Course (with grade, semester)                      |
|  - Order <-> Product (with quantity, price)                       |
|  - Employee <-> Project (with role, start/end date)               |
|  - User <-> Group (with joined_at, is_admin)                      |
+------------------------------------------------------------------+
|                                                                   |
|  Pro tip: When in doubt, use a join entity.                       |
|  Requirements often grow, and adding columns to @ManyToMany       |
|  later requires a significant refactor. A join entity is          |
|  more work upfront but more flexible long-term.                   |
+------------------------------------------------------------------+
```

---

## Practical Example: User and Role

A simple `@ManyToMany` example — no extra columns needed:

```java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false)
    private String password;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();

    protected User() {}

    public User(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public void addRole(Role role) {
        roles.add(role);
        role.getUsersInternal().add(this);
    }

    public void removeRole(Role role) {
        roles.remove(role);
        role.getUsersInternal().remove(this);
    }

    public boolean hasRole(String roleName) {
        return roles.stream().anyMatch(r -> r.getName().equals(roleName));
    }

    // Getters
    public Long getId() { return id; }
    public String getUsername() { return username; }
    public Set<Role> getRoles() { return Collections.unmodifiableSet(roles); }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return username != null && username.equals(user.username);
    }

    @Override
    public int hashCode() {
        return username != null ? username.hashCode() : 0;
    }
}
```

```java
@Entity
@Table(name = "roles")
public class Role {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @ManyToMany(mappedBy = "roles")
    private Set<User> users = new HashSet<>();

    protected Role() {}

    public Role(String name) {
        this.name = name;
    }

    Set<User> getUsersInternal() {
        return users;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public Set<User> getUsers() { return Collections.unmodifiableSet(users); }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Role role = (Role) o;
        return name != null && name.equals(role.name);
    }

    @Override
    public int hashCode() {
        return name != null ? name.hashCode() : 0;
    }
}
```

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByUsername(String username);

    @EntityGraph(attributePaths = {"roles"})
    Optional<User> findWithRolesByUsername(String username);

    // Find users who have a specific role
    @Query("SELECT u FROM User u JOIN u.roles r WHERE r.name = :roleName")
    List<User> findByRoleName(@Param("roleName") String roleName);

    // Find users with multiple roles
    @Query("SELECT u FROM User u WHERE SIZE(u.roles) >= :count")
    List<User> findUsersWithMultipleRoles(@Param("count") int count);
}
```

---

## Cascade Rules for Many-to-Many

```
Cascade Rules for @ManyToMany:
+------------------------------------------------------------------+
|                                                                   |
|  CRITICAL: Do NOT use CascadeType.REMOVE or CascadeType.ALL      |
|  on @ManyToMany relationships!                                    |
|                                                                   |
|  Why?                                                             |
|  - If Student has cascade REMOVE on courses:                      |
|    Deleting a student would DELETE the shared courses!             |
|    Other students would lose their courses.                       |
|                                                                   |
|  - If User has cascade REMOVE on roles:                           |
|    Deleting a user would DELETE the shared roles!                  |
|    Other users would lose their role assignments.                 |
|                                                                   |
|  Safe cascade options for @ManyToMany:                            |
|  +----------------------------+                                   |
|  | cascade = {CascadeType.PERSIST, CascadeType.MERGE}            |
|  | or no cascade at all       |                                   |
|  +----------------------------+                                   |
|                                                                   |
|  For join entities (@OneToMany on both sides):                    |
|  cascade = CascadeType.ALL with orphanRemoval = true is OK        |
|  because the enrollment/link is owned by the parent.              |
+------------------------------------------------------------------+
```

---

## Querying Many-to-Many with JPQL

```java
// Find all students enrolled in a specific course
@Query("SELECT s FROM Student s JOIN s.courses c WHERE c.title = :title")
List<Student> findStudentsByCourse(@Param("title") String courseTitle);

// Find students who take both Math and Science
@Query("SELECT s FROM Student s JOIN s.courses c1 JOIN s.courses c2 " +
       "WHERE c1.title = 'Math' AND c2.title = 'Science'")
List<Student> findStudentsTakingMathAndScience();

// Count enrollments per course
@Query("SELECT c.title, SIZE(c.students) FROM Course c ORDER BY SIZE(c.students) DESC")
List<Object[]> getCoursPopularity();

// Find courses with no students
@Query("SELECT c FROM Course c WHERE c.students IS EMPTY")
List<Course> findEmptyCourses();

// Find students not enrolled in any course
@Query("SELECT s FROM Student s WHERE s.courses IS EMPTY")
List<Student> findUnenrolledStudents();
```

---

## Removing All Associations Before Deleting

When deleting an entity in a many-to-many relationship, you must remove the associations first:

```java
@Service
@Transactional
public class StudentService {

    private final StudentRepository studentRepository;

    // Delete a student — must clear associations first
    public void deleteStudent(Long studentId) {
        Student student = studentRepository.findWithCoursesById(studentId)
            .orElseThrow();

        // Remove student from all courses
        for (Course course : new HashSet<>(student.getCourses())) {
            student.dropCourse(course);
        }

        // Now safe to delete — join table entries already removed
        studentRepository.delete(student);
    }
}
```

```
Deletion Flow:
+------------------------------------------------------------------+
|                                                                   |
|  WITHOUT clearing associations:                                   |
|  studentRepository.delete(student);                               |
|  --> ERROR! FK constraint violation                               |
|  student_courses still has rows referencing this student           |
|                                                                   |
|  WITH clearing associations:                                      |
|  1. student.dropCourse(math);                                     |
|     DELETE FROM student_courses WHERE student_id=1 AND course_id=101 |
|  2. student.dropCourse(science);                                  |
|     DELETE FROM student_courses WHERE student_id=1 AND course_id=102 |
|  3. studentRepository.delete(student);                            |
|     DELETE FROM students WHERE id = 1     (now safe!)             |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Using List instead of Set for @ManyToMany**: List causes Hibernate to delete ALL join table entries and re-insert the remaining ones on every modification. Set allows targeted insert/delete. Always use `Set<T>`.

2. **Using CascadeType.REMOVE or ALL on @ManyToMany**: This deletes the shared entity when one side is deleted. A student deletion would delete shared courses. Use `{PERSIST, MERGE}` or no cascade.

3. **Forgetting helper methods**: Setting only one side of the relationship causes inconsistency. Always synchronize both sides with `addX()` and `removeX()` helper methods.

4. **Not implementing equals/hashCode when using Set**: Without proper `equals()` and `hashCode()`, `Set.contains()`, `Set.remove()`, and `Set.add()` do not work correctly. Use a business key, not the auto-generated `id`.

5. **Using @ManyToMany when extra columns are needed**: If you need dates, quantities, statuses, or any extra data on the association, you cannot use `@ManyToMany`. Convert to a join entity with two `@ManyToOne` relationships.

6. **Not loading associations before deletion**: Deleting an entity with active many-to-many associations causes FK constraint violations. Clear all associations first, then delete.

---

## Best Practices

1. **Always use Set for @ManyToMany collections**: This is a hard rule for performance. `Set` gives O(1) insert/remove on the join table. `List` gives O(n) re-insert.

2. **Implement equals/hashCode using business keys**: Use a unique, immutable field like `email`, `username`, or `title` — never the auto-generated `id` which is null before persistence.

3. **Start with a join entity if you might need extra columns**: Requirements evolve. Converting `@ManyToMany` to a join entity later is a significant refactor. When in doubt, use a join entity upfront.

4. **Do not cascade REMOVE on @ManyToMany**: Cascade only `PERSIST` and `MERGE`, or use no cascade and manage entities independently.

5. **Use @EntityGraph or JOIN FETCH to load associations**: Avoid N+1 when accessing the many-to-many collections by fetching eagerly at the query level.

6. **Consider whether you really need the inverse side**: A unidirectional `@ManyToMany` (only on the owning side) is simpler. Add the inverse side only if you need to navigate from both directions.

---

## Summary

In this chapter, you learned how to map the most complex relationship type:

- **@ManyToMany** creates a join table with two foreign key columns. One side is the owning side (defines `@JoinTable`), the other uses `mappedBy`.

- **Always use Set**, not List, for `@ManyToMany` collections. List causes full delete-and-reinsert of the join table on every change.

- **Helper methods** synchronize both sides of the bidirectional relationship, just as with `@OneToMany`.

- **Never cascade REMOVE** on `@ManyToMany`. It would delete shared entities. Use `{PERSIST, MERGE}` or no cascade.

- **Join entities** replace `@ManyToMany` when you need extra columns (date, grade, quantity) on the association. This converts the relationship into two `@ManyToOne` / `@OneToMany` pairs.

- **equals/hashCode** must use business keys (not auto-generated IDs) when entities are stored in Sets.

- **Clear associations before deleting** entities in many-to-many relationships to avoid FK constraint violations.

---

## Interview Questions

**Q1: How does a relational database represent a many-to-many relationship?**

With a join table (also called association table or junction table). The join table has two foreign key columns, each referencing one side of the relationship. The composite of both foreign keys forms the primary key. For example, `student_courses` has `student_id` and `course_id`, both as foreign keys.

**Q2: Why should you use Set instead of List for @ManyToMany collections?**

When using `List`, Hibernate handles collection changes by deleting ALL rows from the join table and re-inserting the remaining ones. With `Set`, Hibernate can insert or delete individual rows. For a student with 50 courses who drops 1, `List` generates 1 DELETE + 49 INSERTs, while `Set` generates just 1 DELETE.

**Q3: When should you convert @ManyToMany to a join entity?**

When the association needs extra columns beyond the two foreign keys. Examples: enrollment date, grade, quantity, role, status, or any metadata about the relationship itself. Also when you need to query the relationship directly (e.g., "find all enrollments from this semester").

**Q4: Why should you not use CascadeType.REMOVE on @ManyToMany?**

Because both sides of a many-to-many share the referenced entities. If a student has `cascade = REMOVE` on courses, deleting the student would also delete the courses — which are shared with other students. This would cascade into data loss for unrelated entities.

**Q5: How do you implement equals and hashCode for entities used in Sets?**

Use a natural business key (like `email`, `username`, or `ISBN`) that is unique, immutable, and available before the entity is persisted. Never use the auto-generated `id` because it is `null` for new entities, which breaks the `hashCode` contract when the entity is added to a Set before being saved.

**Q6: What is the difference between the owning side and inverse side in @ManyToMany?**

The owning side defines the `@JoinTable` and controls the join table's SQL (inserts and deletes). The inverse side uses `mappedBy` and is read-only — changes to the inverse collection are not persisted. Only changes to the owning side's collection trigger database updates.

---

## Practice Exercises

**Exercise 1: Simple Many-to-Many**
Create `Article` and `Tag` entities with a basic `@ManyToMany` using `Set`. Write helper methods, a service to add/remove tags, and verify the join table entries.

**Exercise 2: Join Entity**
Create `Employee`, `Project`, and `Assignment` (join entity) where an assignment has `role` (String) and `startDate`/`endDate` (LocalDate). Write a service with: assign employee to project, end assignment, find all active assignments for a project.

**Exercise 3: Set vs List Performance**
Map the same many-to-many relationship twice — once with `Set` and once with `List`. Enable SQL logging. Add 5 associations, then remove 1. Count and compare the SQL statements generated.

**Exercise 4: User-Role Authorization**
Build a complete User-Role system with: create user, create role, assign role to user, remove role, check `hasRole()`, find all users with a specific role, find users with multiple roles. Write repository queries using JPQL.

**Exercise 5: Safe Deletion**
Create entities with many-to-many relationships. Write a test that: (a) tries to delete an entity without clearing associations (expect error), (b) clears associations first then deletes (expect success). Verify the join table is cleaned up properly.

---

## What Is Next?

In the next chapter, we will explore **Embeddable Types and Element Collections**. You will learn how to use `@Embeddable` and `@Embedded` to model value objects (like Address) that are stored in the parent table, and `@ElementCollection` for collections of simple values or embeddables that are stored in a separate table without being full entities.
