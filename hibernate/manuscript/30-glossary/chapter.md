# Chapter 30: Glossary of JPA and Hibernate Terms

---

This glossary provides a quick reference for every key term, annotation, and concept covered in this book. Terms are grouped by category for easier browsing, then listed alphabetically within each group.

---

## Core Concepts

**Cascade**: The propagation of persistence operations (persist, merge, remove, refresh, detach) from a parent entity to its related entities. Configured with `CascadeType` on relationship annotations.

**Dirty Checking**: Hibernate's automatic mechanism for detecting changes to managed entities. At flush time, Hibernate compares the current state of each entity to a snapshot taken when it was loaded. Changed entities generate UPDATE statements automatically.

**Entity**: A Java class mapped to a database table using `@Entity`. Each instance represents a row in the table. Entities have a primary key (`@Id`) and are managed by the persistence context.

**Entity Lifecycle States**: The four states an entity can be in: **New** (created but not persisted), **Managed** (attached to a persistence context), **Detached** (was managed but the context is closed), **Removed** (scheduled for deletion).

**First-Level Cache (L1 Cache)**: The persistence context itself. Every entity loaded within a transaction is cached. Loading the same entity twice by ID returns the same object instance. Always enabled and cannot be disabled.

**Flush**: The process of synchronizing the persistence context with the database. Hibernate writes all pending INSERT, UPDATE, and DELETE statements to the database. Happens automatically before queries, at transaction commit, or manually via `flush()`.

**Impedance Mismatch**: The fundamental difference between how Java represents data (objects, inheritance, references) and how relational databases represent data (tables, rows, foreign keys). ORM frameworks bridge this gap.

**JDBC (Java Database Connectivity)**: The low-level Java API for interacting with databases. Requires manual SQL, connection management, and result mapping. Hibernate uses JDBC internally but abstracts it away.

**JPA (Jakarta Persistence API)**: The official Java specification for object-relational mapping. Defines standard annotations (`jakarta.persistence.*`), the `EntityManager` interface, JPQL, and the Criteria API. JPA is a specification, not an implementation.

**JPQL (Java Persistence Query Language)**: A SQL-like query language that operates on entities and their fields rather than tables and columns. Example: `SELECT e FROM Employee e WHERE e.salary > 50000`. Database-independent and validated at startup.

**Lazy Loading**: A fetching strategy where related entities or collections are loaded from the database only when first accessed. Configured with `FetchType.LAZY`. Prevents loading unnecessary data but can cause N+1 problems or `LazyInitializationException`.

**Managed Entity**: An entity that is currently attached to a persistence context. Changes to managed entities are automatically detected and persisted at flush time.

**N+1 Problem**: A performance issue where loading N entities triggers N additional queries to load their lazy relationships. Solved with `JOIN FETCH`, `@EntityGraph`, or `@BatchSize`.

**ORM (Object-Relational Mapping)**: A programming technique that automatically converts data between Java objects and relational database tables. Hibernate is the most popular Java ORM framework.

**Orphan Removal**: Automatic deletion of a child entity when it is removed from a parent's collection. Configured with `orphanRemoval = true` on `@OneToMany` or `@OneToOne`.

**Owning Side**: The side of a bidirectional relationship that controls the foreign key column. For `@OneToMany`/`@ManyToOne`, the `@ManyToOne` side is always the owning side. The owning side does NOT have `mappedBy`.

**Persistence Context**: The first-level cache managed by an `EntityManager`. It tracks all loaded entities, detects changes, and manages entity identity (only one instance per primary key).

**Persistence Unit**: A logical grouping of entity classes and configuration that defines a persistence context. In Spring Boot, configured via `application.properties`.

**Second-Level Cache (L2 Cache)**: An optional, shared cache that spans multiple transactions and sessions. Stores entity data beyond the persistence context lifecycle. Requires a cache provider like Ehcache or Caffeine.

**Session**: Hibernate's equivalent of the JPA `EntityManager`. Provides the same functionality plus Hibernate-specific features. In modern code, prefer `EntityManager`.

---

## JPA Annotations (jakarta.persistence.*)

**@Basic**: Marks a field as a basic (simple) type. Optional for most fields. Use `@Basic(fetch = FetchType.LAZY)` for lazy loading of large fields.

**@Cacheable**: Marks an entity as cacheable in the second-level cache. Requires `@EnableCaching` and a cache provider.

**@Column**: Specifies column details. Attributes: `name`, `nullable`, `unique`, `length`, `columnDefinition`, `updatable`, `insertable`.

**@ConstructorResult**: Used within `@SqlResultSetMapping` to map native query results to a DTO constructor.

**@Convert / @Converter**: Defines a JPA attribute converter for custom type mapping between Java types and database column types.

**@DiscriminatorColumn**: Specifies the discriminator column used in single-table inheritance. Default name is `DTYPE`.

**@DiscriminatorValue**: Specifies the value stored in the discriminator column for a specific subclass.

**@ElementCollection**: Maps a collection of embeddable types or basic types (e.g., `List<String>`) to a separate table.

**@Embeddable**: Marks a class as an embeddable value object that can be embedded in entities. Does not have its own table or identity.

**@Embedded**: Marks a field as an embedded instance of an `@Embeddable` class.

**@Entity**: Marks a class as a JPA entity mapped to a database table.

**@EntityListeners**: Specifies callback listener classes for entity lifecycle events (e.g., `AuditingEntityListener`).

**@Enumerated**: Specifies how an enum is stored. `EnumType.STRING` stores the name; `EnumType.ORDINAL` stores the position (avoid ordinal).

**@GeneratedValue**: Specifies primary key generation strategy: `AUTO`, `IDENTITY`, `SEQUENCE`, `TABLE`, or `UUID`.

**@Id**: Marks the primary key field of an entity.

**@IdClass**: Specifies a composite primary key class for an entity with multiple `@Id` fields.

**@EmbeddedId**: Marks a field as an embedded composite primary key using an `@Embeddable` class.

**@Index**: Defines a database index on the entity's table. Used within `@Table(indexes = ...)`.

**@Inheritance**: Specifies the inheritance mapping strategy: `SINGLE_TABLE`, `JOINED`, or `TABLE_PER_CLASS`.

**@JoinColumn**: Specifies the foreign key column for a relationship. Used on the owning side.

**@JoinTable**: Specifies a join table for `@ManyToMany` relationships or unidirectional `@OneToMany`.

**@Lob**: Marks a field as a Large Object (CLOB for text, BLOB for binary).

**@ManyToMany**: Maps a many-to-many relationship. Requires a join table.

**@ManyToOne**: Maps a many-to-one relationship. The owning side that holds the foreign key. Default fetch: `EAGER` (change to `LAZY`).

**@MappedSuperclass**: Marks a class whose fields are inherited by entities but is not an entity itself. No table is created for it.

**@NamedEntityGraph**: Defines a reusable fetch plan for an entity. Referenced by name in `@EntityGraph`.

**@NamedQuery**: Defines a pre-compiled JPQL query on an entity. Validated at startup.

**@OneToMany**: Maps a one-to-many relationship. Typically the inverse side with `mappedBy`. Default fetch: `LAZY`.

**@OneToOne**: Maps a one-to-one relationship. Can be owning or inverse side.

**@OrderBy**: Specifies the default ordering for collection elements using JPQL field names.

**@PostLoad**: Lifecycle callback executed after an entity is loaded from the database.

**@PostPersist**: Lifecycle callback executed after an entity is persisted (INSERT).

**@PostRemove**: Lifecycle callback executed after an entity is removed (DELETE).

**@PostUpdate**: Lifecycle callback executed after an entity is updated (UPDATE).

**@PrePersist**: Lifecycle callback executed before an entity is persisted.

**@PreRemove**: Lifecycle callback executed before an entity is removed.

**@PreUpdate**: Lifecycle callback executed before an entity is updated.

**@Query**: Spring Data JPA annotation for defining custom JPQL or native SQL queries on repository methods.

**@SequenceGenerator**: Configures a database sequence for primary key generation.

**@SqlResultSetMapping**: Maps native query results to entities or DTOs with precise column-to-field control.

**@Table**: Specifies the table name, schema, and indexes for an entity.

**@Temporal**: Specifies the JDBC temporal type for `java.util.Date` or `java.util.Calendar` fields. Not needed for `java.time` types.

**@Transient**: Marks a field as not persisted. The field is ignored by JPA.

**@Version**: Marks a field for optimistic locking. Hibernate automatically increments it on each update and throws `OptimisticLockException` on concurrent modifications.

---

## Hibernate-Specific Annotations (org.hibernate.annotations.*)

**@BatchSize**: Controls the number of lazy-loaded collections or entities fetched in a single SQL IN clause. Reduces N+1 by batching.

**@DynamicInsert**: Generates INSERT statements that include only non-null columns.

**@DynamicUpdate**: Generates UPDATE statements that include only changed columns.

**@Fetch(FetchMode)**: Controls how a collection is fetched: `SELECT` (separate query), `JOIN` (join with parent), `SUBSELECT` (single subselect for all collections).

**@Filter / @FilterDef**: Defines a parameterized SQL filter that can be enabled or disabled at runtime. Useful for soft deletes.

**@Formula**: Maps a field to a SQL expression instead of a column. Computed on every load.

**@NaturalId**: Marks a field as a natural (business) key. Provides `byNaturalId()` lookup in Hibernate.

**@SQLDelete**: Overrides the default DELETE statement. Used for soft deletes: `@SQLDelete(sql = "UPDATE table SET deleted = true WHERE id = ?")`.

**@Where**: Adds a SQL WHERE clause to entity loading or collection fetching. Used for soft delete filtering.

---

## Spring Data JPA Terms

**CrudRepository**: Base interface providing basic CRUD methods: `save`, `findById`, `findAll`, `deleteById`, `count`, `existsById`.

**Derived Query Methods**: Repository methods whose queries are automatically generated from the method name. Example: `findByNameContaining(String name)`.

**JpaRepository**: Extends `CrudRepository` with JPA-specific methods: `flush`, `saveAndFlush`, batch deletes, `findAll(Sort)`, `findAll(Pageable)`.

**JpaSpecificationExecutor**: Interface that adds Specification-based querying to a repository. Enables dynamic query composition.

**Page**: A paginated result that includes content, total elements, total pages, and navigation metadata. Requires an extra COUNT query.

**Pageable / PageRequest**: Defines pagination parameters: page number (0-based), page size, and sort order.

**Slice**: A paginated result that knows if more data exists but does not count the total. More efficient than Page for large datasets.

**Sort**: Defines ordering: field name, direction (ASC/DESC), and null handling.

**Specification**: A functional interface for building type-safe, composable query predicates using the Criteria API. Can be combined with `and()`, `or()`, `not()`.

---

## Transaction and Performance Terms

**ACID**: Atomicity, Consistency, Isolation, Durability — the four guarantees of a database transaction.

**@Transactional**: Spring annotation that wraps a method in a database transaction. Key attributes: `readOnly`, `propagation`, `isolation`, `rollbackFor`.

**Batch Processing**: Executing multiple SQL statements in groups (batches) rather than one at a time. Configured with `hibernate.jdbc.batch_size`.

**Connection Pool**: A pool of pre-created database connections reused across requests. HikariCP is the default in Spring Boot.

**Isolation Level**: Defines how concurrent transactions interact. Common levels: `READ_COMMITTED`, `REPEATABLE_READ`, `SERIALIZABLE`.

**Optimistic Locking**: A concurrency strategy using a `@Version` field. The transaction fails if another transaction modified the entity first.

**Propagation**: Defines how transactions interact when methods call other transactional methods. Common: `REQUIRED` (default), `REQUIRES_NEW`, `SUPPORTS`.

**Query Cache**: An optional Hibernate cache that stores the results (entity IDs) of queries. Must be used with the second-level entity cache.

**Read-Only Transaction**: A transaction marked with `readOnly = true` that skips dirty checking, improving performance for read-heavy operations.

**StatelessSession**: A Hibernate-specific lightweight session that bypasses the persistence context. Used for bulk operations where caching overhead is unwanted.

---

## Database Migration Terms

**Baseline**: Initializing Flyway on an existing database by marking the current schema as the starting point.

**Flyway**: A database migration tool that applies versioned SQL scripts to evolve the database schema. Runs automatically on Spring Boot startup.

**Repeatable Migration**: A Flyway migration (prefix `R__`) that is re-executed whenever its content changes. Used for views, stored procedures, and reference data.

**Versioned Migration**: A Flyway migration (prefix `V1__`, `V2__`) that runs exactly once and is never modified after execution.

---

## Architecture Terms

**Controller**: The HTTP layer that handles requests, validates input, and returns responses. Annotated with `@RestController`.

**DTO (Data Transfer Object)**: A plain object used to transfer data between layers. Entities are never exposed directly in API responses.

**Repository**: The data access layer that interacts with the database. Annotated with `@Repository`. In Spring Data JPA, typically an interface extending `JpaRepository`.

**Service**: The business logic layer that orchestrates operations, enforces rules, and manages transactions. Annotated with `@Service`.

---

This glossary covers the essential terms you will encounter when working with JPA and Hibernate. Return to it whenever you need a quick refresher on a concept, annotation, or pattern.
