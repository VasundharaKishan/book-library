# Chapter 26: Database Migrations with Flyway

---

## Learning Goals

By the end of this chapter, you will be able to:

- Explain why ddl-auto=update is dangerous in production
- Understand database migrations and why they are essential
- Set up Flyway in a Spring Boot project
- Write versioned migration scripts with proper naming conventions
- Add columns, create tables, insert seed data, and alter constraints
- Use repeatable migrations for views and stored procedures
- Baseline an existing database for Flyway adoption
- Handle migration errors and resolve failed states
- Integrate Flyway with your development workflow

---

## Why Not ddl-auto=update?

During development, you have been using `spring.jpa.hibernate.ddl-auto=update`, which lets Hibernate automatically modify the database schema. This is convenient for learning but dangerous in production.

```
ddl-auto Options:
+------------------------------------------------------------------+
|                                                                   |
|  Value        What It Does                    Safe for Prod?      |
|  ----------------------------------------------------------------|
|  create       Drops ALL tables, recreates     NEVER (data loss!)  |
|  create-drop  Like create, drops on shutdown  NEVER               |
|  update       Adds missing columns/tables     DANGEROUS           |
|  validate     Checks schema matches entities  YES (read-only)     |
|  none         Does nothing                    YES                 |
+------------------------------------------------------------------+

Why ddl-auto=update Is Dangerous:
+------------------------------------------------------------------+
|                                                                   |
|  1. It NEVER deletes columns or tables                            |
|     Remove a field from your entity --> column stays in DB        |
|     Orphaned columns accumulate forever                           |
|                                                                   |
|  2. It NEVER renames columns                                      |
|     Rename a field --> old column stays, new column created       |
|     Data in old column is lost                                    |
|                                                                   |
|  3. It can ALTER columns in unexpected ways                       |
|     Change @Column(length=100) to length=200                      |
|     --> ALTER TABLE may lock the table for minutes on large data  |
|                                                                   |
|  4. No rollback capability                                        |
|     If a schema change breaks something, you cannot undo it      |
|                                                                   |
|  5. No audit trail                                                |
|     No record of what changed, when, or why                      |
|                                                                   |
|  6. Different environments drift apart                            |
|     Dev, staging, and production may have different schemas       |
|     because updates ran at different times                        |
+------------------------------------------------------------------+
```

---

## What Are Database Migrations?

Database migrations are **versioned SQL scripts** that evolve your schema in a controlled, repeatable, and auditable way. Each script runs once, in order, and is tracked so it never runs again.

```
Migration Concept:
+------------------------------------------------------------------+
|                                                                   |
|  V1__Create_employees_table.sql                                   |
|  CREATE TABLE employees (                                         |
|      id BIGINT PRIMARY KEY AUTO_INCREMENT,                        |
|      name VARCHAR(100) NOT NULL                                   |
|  );                                                               |
|       |                                                           |
|       v                                                           |
|  V2__Add_email_column.sql                                         |
|  ALTER TABLE employees ADD COLUMN email VARCHAR(150);             |
|       |                                                           |
|       v                                                           |
|  V3__Add_departments_table.sql                                    |
|  CREATE TABLE departments (...);                                  |
|  ALTER TABLE employees ADD COLUMN department_id BIGINT;            |
|       |                                                           |
|       v                                                           |
|  V4__Add_salary_column.sql                                        |
|  ALTER TABLE employees ADD COLUMN salary DECIMAL(10,2);           |
|                                                                   |
|  Each migration builds on the previous one.                       |
|  Run them in order on any database to get the current schema.    |
|  Every environment ends up with the exact same structure.         |
+------------------------------------------------------------------+
```

---

## Setting Up Flyway

### Add Dependency

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```

### Configure Application Properties

```properties
# application.properties

# Let Flyway manage the schema, not Hibernate
spring.jpa.hibernate.ddl-auto=validate

# Flyway configuration
spring.flyway.enabled=true
spring.flyway.locations=classpath:db/migration
spring.flyway.baseline-on-migrate=false
```

```
Configuration Explained:
+------------------------------------------------------------------+
|                                                                   |
|  ddl-auto=validate:                                               |
|  Hibernate checks that entity mappings match the database schema  |
|  but does NOT modify the schema. Flyway handles all changes.     |
|  If they don't match, the app fails to start (catches errors).   |
|                                                                   |
|  flyway.locations=classpath:db/migration:                         |
|  Flyway looks for SQL files in src/main/resources/db/migration/  |
|                                                                   |
|  On application startup:                                          |
|  1. Flyway checks flyway_schema_history table                    |
|  2. Finds which migrations have already run                      |
|  3. Runs any NEW migrations in version order                     |
|  4. Updates flyway_schema_history                                |
|  5. Hibernate validates schema matches entities                  |
|  6. Application starts normally                                   |
+------------------------------------------------------------------+
```

---

## Writing Migration Scripts

### Naming Convention

```
Flyway Naming Convention:
+------------------------------------------------------------------+
|                                                                   |
|  V{version}__{description}.sql                                    |
|  |  |          |                                                  |
|  |  |          +-- Description (underscores for spaces)           |
|  |  +------------- Version number                                 |
|  +---------------- V = Versioned migration                        |
|                                                                   |
|  Examples:                                                        |
|  V1__Create_employees_table.sql                                   |
|  V2__Add_email_to_employees.sql                                   |
|  V3__Create_departments_table.sql                                 |
|  V4__Add_department_id_to_employees.sql                           |
|  V5__Insert_seed_data.sql                                         |
|                                                                   |
|  Rules:                                                           |
|  - V is uppercase                                                 |
|  - Version can be: 1, 2, 3 or 1.1, 1.2, 2.0 or timestamps       |
|  - TWO underscores (__) separate version from description         |
|  - Description uses underscores (no spaces)                       |
|  - .sql extension                                                 |
|  - Files go in src/main/resources/db/migration/                   |
+------------------------------------------------------------------+
```

### Example Migrations

```sql
-- V1__Create_departments_table.sql
CREATE TABLE departments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER DEFAULT 0
);
```

```sql
-- V2__Create_employees_table.sql
CREATE TABLE employees (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    salary DECIMAL(10, 2),
    hire_date DATE,
    active BOOLEAN DEFAULT TRUE,
    department_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER DEFAULT 0,
    CONSTRAINT fk_employee_department
        FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE INDEX idx_employee_email ON employees(email);
CREATE INDEX idx_employee_department ON employees(department_id);
```

```sql
-- V3__Insert_default_departments.sql
INSERT INTO departments (name) VALUES ('Engineering');
INSERT INTO departments (name) VALUES ('Marketing');
INSERT INTO departments (name) VALUES ('Sales');
INSERT INTO departments (name) VALUES ('Human Resources');
INSERT INTO departments (name) VALUES ('Finance');
```

```sql
-- V4__Add_phone_to_employees.sql
ALTER TABLE employees ADD COLUMN phone VARCHAR(20);
```

```sql
-- V5__Create_projects_table.sql
CREATE TABLE projects (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE employee_projects (
    employee_id BIGINT NOT NULL,
    project_id BIGINT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(50),
    PRIMARY KEY (employee_id, project_id),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

```sql
-- V6__Add_bio_column_to_employees.sql
ALTER TABLE employees ADD COLUMN bio TEXT;

-- V7__Rename_phone_to_phone_number.sql
ALTER TABLE employees ALTER COLUMN phone RENAME TO phone_number;
```

```
File Structure:
+------------------------------------------------------------------+
|                                                                   |
|  src/main/resources/                                              |
|  +-- db/                                                          |
|  |   +-- migration/                                               |
|  |       +-- V1__Create_departments_table.sql                     |
|  |       +-- V2__Create_employees_table.sql                       |
|  |       +-- V3__Insert_default_departments.sql                   |
|  |       +-- V4__Add_phone_to_employees.sql                       |
|  |       +-- V5__Create_projects_table.sql                        |
|  |       +-- V6__Add_bio_column_to_employees.sql                  |
|  |       +-- V7__Rename_phone_to_phone_number.sql                 |
|  +-- application.properties                                       |
+------------------------------------------------------------------+
```

---

## How Flyway Tracks Migrations

Flyway creates a `flyway_schema_history` table to track which migrations have run:

```
flyway_schema_history Table:
+------------------------------------------------------------------+
|                                                                   |
|  | version | description              | script                  | |
|  |---------|--------------------------|-------------------------| |
|  | 1       | Create departments table | V1__Create_depart...sql | |
|  | 2       | Create employees table   | V2__Create_employ...sql | |
|  | 3       | Insert default depts     | V3__Insert_defaul...sql | |
|  | 4       | Add phone to employees   | V4__Add_phone_to_...sql | |
|                                                                   |
|  | installed_on        | execution_time | checksum   | success |  |
|  |---------------------|----------------|------------|---------|  |
|  | 2025-09-01 10:00:00 | 45             | -123456789 | true    |  |
|  | 2025-09-01 10:00:01 | 120            | 987654321  | true    |  |
|  | 2025-09-01 10:00:01 | 15             | -555555555 | true    |  |
|  | 2025-09-15 14:30:00 | 30             | 111111111  | true    |  |
|                                                                   |
|  On next startup:                                                 |
|  Flyway sees V1-V4 already ran. If V5 exists, it runs V5 only.  |
|  Already-run migrations are NEVER re-executed.                   |
|                                                                   |
|  Checksum: Hash of the file content. If you modify an already-   |
|  run migration file, Flyway detects the change and FAILS.        |
|  This prevents accidental modification of applied migrations.    |
+------------------------------------------------------------------+
```

---

## Repeatable Migrations

Repeatable migrations run every time their content changes. Useful for views, functions, and stored procedures:

```
Repeatable Migration Naming:
+------------------------------------------------------------------+
|                                                                   |
|  R__{description}.sql                                             |
|  |     |                                                          |
|  |     +-- Description                                            |
|  +-------- R = Repeatable (runs when checksum changes)            |
|                                                                   |
|  Examples:                                                        |
|  R__Create_employee_summary_view.sql                              |
|  R__Create_department_statistics_function.sql                     |
+------------------------------------------------------------------+
```

```sql
-- R__Create_employee_summary_view.sql
-- This runs every time the file content changes

CREATE OR REPLACE VIEW employee_summary AS
SELECT
    e.id,
    e.name,
    e.email,
    e.salary,
    d.name AS department_name,
    e.hire_date,
    e.active
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;
```

```
Versioned vs Repeatable:
+------------------------------------------------------------------+
|                                                                   |
|  Versioned (V1__, V2__):                                          |
|  - Runs ONCE, tracked by version number                           |
|  - For schema changes: CREATE TABLE, ALTER TABLE, INSERT          |
|  - Cannot be modified after running                               |
|  - Order matters (V1 before V2)                                   |
|                                                                   |
|  Repeatable (R__):                                                |
|  - Runs every time content changes (checksum comparison)          |
|  - For replaceable objects: views, functions, procedures          |
|  - Can be modified freely                                         |
|  - Always runs AFTER all versioned migrations                     |
+------------------------------------------------------------------+
```

---

## Baselining an Existing Database

If you are adding Flyway to a project that already has a database schema, use baselining:

```properties
# application.properties
spring.flyway.baseline-on-migrate=true
spring.flyway.baseline-version=0
```

```
Baseline Process:
+------------------------------------------------------------------+
|                                                                   |
|  Existing database with tables already created manually           |
|       |                                                           |
|       v                                                           |
|  Add Flyway with baseline-on-migrate=true                         |
|       |                                                           |
|       v                                                           |
|  Flyway creates flyway_schema_history with baseline entry         |
|  (marks version 0 as "baseline")                                  |
|       |                                                           |
|       v                                                           |
|  Future migrations start from V1                                  |
|  V1 = first CHANGE (not the initial schema)                       |
|       |                                                           |
|       v                                                           |
|  Optional: Create V0__Baseline.sql for documentation              |
|  (contains CREATE TABLE statements matching existing schema)      |
|  (Flyway skips it because baseline version is 0)                  |
+------------------------------------------------------------------+
```

---

## Development Workflow

```
Migration Workflow:
+------------------------------------------------------------------+
|                                                                   |
|  1. Developer adds a field to an entity:                          |
|     @Column(name = "phone_number")                                |
|     private String phoneNumber;                                   |
|                                                                   |
|  2. Developer creates a migration script:                         |
|     V8__Add_phone_number_to_employees.sql                         |
|     ALTER TABLE employees ADD COLUMN phone_number VARCHAR(20);    |
|                                                                   |
|  3. Developer runs the app:                                       |
|     Flyway executes V8                                            |
|     Hibernate validates schema matches entity (ddl-auto=validate) |
|     App starts successfully                                       |
|                                                                   |
|  4. Developer commits both files:                                 |
|     - Entity change (Java)                                        |
|     - Migration script (SQL)                                      |
|                                                                   |
|  5. Other developers pull and run:                                |
|     Flyway automatically runs V8 on their database                |
|     Everyone has the same schema                                  |
|                                                                   |
|  6. CI/CD deploys to staging/production:                          |
|     Flyway runs V8 on staging database                            |
|     Flyway runs V8 on production database                         |
|     All environments are in sync                                  |
+------------------------------------------------------------------+
```

---

## Handling Migration Failures

```
When a Migration Fails:
+------------------------------------------------------------------+
|                                                                   |
|  V5 has a SQL syntax error:                                       |
|  CRAETE TABLE projects (...)    <-- typo!                         |
|                                                                   |
|  Flyway tries to run V5 --> SQL error                             |
|  flyway_schema_history marks V5 as failed (success = false)      |
|  Application fails to start                                       |
|                                                                   |
|  To fix:                                                          |
|                                                                   |
|  Option 1: Fix the SQL and repair                                 |
|  1. Fix the typo in V5__Create_projects_table.sql                 |
|  2. Run: flyway repair (or Spring Boot command)                   |
|     This removes the failed entry from flyway_schema_history     |
|  3. Restart the app — Flyway retries V5 with fixed SQL           |
|                                                                   |
|  Option 2: In development, clean and restart                     |
|  spring.flyway.clean-disabled=false  (ONLY in dev!)               |
|  Run: flyway clean (drops everything, reruns all migrations)     |
|                                                                   |
|  NEVER use flyway clean in production!                            |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **Modifying already-applied migration files**: Flyway checksums detect changes to applied migrations and refuses to start. Applied migrations are immutable — create a new migration for changes.

2. **Using ddl-auto=update alongside Flyway**: Both try to manage the schema. Use `ddl-auto=validate` (or `none`) with Flyway. Let Flyway be the single source of truth.

3. **Forgetting to create a migration when changing entities**: Adding a field to an entity without a corresponding migration causes `validate` to fail. Always pair entity changes with migration scripts.

4. **Writing non-idempotent migrations**: If a migration fails halfway, some DDL might have executed. Write migrations that can handle partial application (use `IF NOT EXISTS` where possible).

5. **Using database-specific SQL in migrations meant for H2**: H2 syntax differs from PostgreSQL/MySQL. If you test with H2 but deploy to PostgreSQL, some SQL may not be portable.

6. **Numbering gaps or conflicts in team development**: Two developers creating V5 independently causes a conflict. Use timestamps (`V20250915143000__`) or coordinate version numbers.

---

## Best Practices

1. **One migration per change**: Keep migrations small and focused. `V5__Add_email_index.sql` is better than `V5__Multiple_changes.sql`.

2. **Never modify applied migrations**: Once a migration has run in any environment, treat it as immutable. Fix mistakes with new migrations.

3. **Use validate in production**: `spring.jpa.hibernate.ddl-auto=validate` catches schema mismatches at startup instead of at runtime.

4. **Commit migrations with their entity changes**: The migration and the Java entity change should be in the same commit. They are a unit.

5. **Test migrations in CI**: Run migrations against a fresh database in your CI pipeline to catch issues before production.

6. **Use descriptive migration names**: `V12__Add_indexes_for_search_performance.sql` tells the team what and why without opening the file.

---

## Summary

- **ddl-auto=update is dangerous** in production: it never drops columns, never renames, and provides no rollback or audit trail. Use `validate` instead.

- **Flyway** manages database schema changes through versioned SQL migration scripts that run in order, once, and are tracked in `flyway_schema_history`.

- **Naming convention**: `V{version}__{description}.sql` for versioned migrations, `R__{description}.sql` for repeatable migrations.

- **Repeatable migrations** re-run when their content changes — useful for views and functions.

- **Baselining** integrates Flyway with an existing database without re-creating the schema.

- **Never modify** applied migrations. Create new migrations to fix or change previous schema decisions.

- **Pair entity changes with migrations**: Every `@Column` change needs a corresponding SQL migration.

---

## Interview Questions

**Q1: Why should you not use ddl-auto=update in production?**

It never removes columns or tables (orphaned data accumulates), never renames (creates new column, loses data), can lock tables during ALTER on large datasets, provides no rollback capability, no audit trail, and causes schema drift across environments.

**Q2: How does Flyway ensure migrations run in order and only once?**

Flyway tracks applied migrations in `flyway_schema_history` table with version numbers, checksums, and timestamps. On startup, it compares available migration files against applied versions and runs only new migrations in version order. It detects modified files via checksum comparison.

**Q3: What is the difference between versioned and repeatable migrations?**

Versioned migrations (V1__, V2__) run once and are immutable — for DDL changes. Repeatable migrations (R__) re-run whenever their content changes — for replaceable database objects like views and functions. Repeatable always run after all versioned migrations.

**Q4: How do you add Flyway to an existing project with an established database?**

Use `spring.flyway.baseline-on-migrate=true`. Flyway creates a baseline entry in `flyway_schema_history` marking the current state. Future migrations start from the next version number. Optionally create a V0 script documenting the existing schema.

**Q5: What happens if a migration fails?**

Flyway marks the migration as failed in `flyway_schema_history`. The application cannot start until the issue is resolved. Fix the SQL script, run `flyway repair` to remove the failed entry, and restart. In development, `flyway clean` can reset everything.

---

## Practice Exercises

**Exercise 1: First Migration**
Remove `ddl-auto=update` and switch to `validate`. Write V1-V3 migrations that create the tables your entities need. Verify the app starts successfully.

**Exercise 2: Schema Evolution**
Add a new field to an entity. Write the corresponding migration. Verify `validate` passes. Then try adding a field WITHOUT a migration and observe the startup error.

**Exercise 3: Seed Data**
Write a migration that inserts default data (categories, roles, status codes). Verify the data exists on startup.

**Exercise 4: Repeatable Migration**
Create a database view using a repeatable migration. Modify the view definition and verify Flyway re-runs it on the next startup.

**Exercise 5: Team Simulation**
Simulate two developers creating migrations concurrently. Both create V5 with different changes. Observe the conflict. Resolve by renumbering one to V6.

---

## What Is Next?

In the next chapter, we will explore **Performance Tuning and Monitoring** — batch processing, bulk operations, connection pooling, slow query logging, Hibernate statistics, and indexing strategies. You will learn how to identify and fix performance bottlenecks in JPA/Hibernate applications.
