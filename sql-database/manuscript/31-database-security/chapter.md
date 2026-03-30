# Chapter 31: Database Security

## What You Will Learn

In this chapter, you will learn how to protect your database from unauthorized access and attacks. You will understand the difference between authentication and authorization, learn how to create roles and manage privileges, implement row-level security, protect against SQL injection, encrypt your data, and create backup strategies. By the end, you will set up a complete security model for a real application.

## Why This Chapter Matters

Imagine you own a bank. You would not leave the vault door open and hope that only honest people walk in. You would verify who enters the building (authentication), control which rooms they can access (authorization), install cameras (auditing), and keep copies of important records in a safe place (backups).

Your database works the same way. It holds your most valuable asset: data. Customer information, financial records, personal details -- all of it needs protection. A single security breach can destroy a business, damage trust, and violate privacy laws.

Whether you are building a small web application or managing enterprise systems, database security is not optional. It is essential.

---

## Authentication: Who Are You?

Authentication answers one simple question: "Who are you?"

Think of it like showing your ID at the door of a building. Before you can do anything inside, you must prove your identity.

PostgreSQL supports several authentication methods:

```
+--------------------+----------------------------------------+
| Method             | How It Works                           |
+--------------------+----------------------------------------+
| password           | Plain text password (not recommended)  |
| md5                | Hashed password (legacy)               |
| scram-sha-256      | Strongly hashed password (recommended) |
| peer               | Uses OS username (local connections)   |
| cert               | Uses SSL certificates                  |
| ldap               | Delegates to LDAP directory            |
+--------------------+----------------------------------------+
```

### The pg_hba.conf File

PostgreSQL controls authentication through a file called `pg_hba.conf` (Host-Based Authentication). Think of it as a guest list at the door.

Each line in this file says: "For this type of connection, from this address, to this database, for this user, use this authentication method."

```
# TYPE    DATABASE    USER       ADDRESS          METHOD

# Local connections (same machine)
local     all         postgres                    peer
local     all         all                         scram-sha-256

# Remote connections
host      all         all        127.0.0.1/32     scram-sha-256
host      all         all        192.168.1.0/24   scram-sha-256
host      myapp_db    app_user   10.0.0.0/8       scram-sha-256

# Reject everything else
host      all         all        0.0.0.0/0        reject
```

Let us break this down line by line:

- **Line 1**: Local connections from the `postgres` superuser use `peer` authentication (the OS verifies identity).
- **Line 2**: All other local connections require a password with `scram-sha-256` hashing.
- **Line 3**: Connections from localhost (127.0.0.1) require a hashed password.
- **Line 4**: Connections from the local network (192.168.1.x) require a hashed password.
- **Line 5**: Only the `app_user` can connect to `myapp_db` from the 10.x.x.x network.
- **Line 6**: Everything else is rejected.

The file is read from top to bottom, and the first matching rule wins. This is important. If you put a `reject` rule at the top, nobody can connect.

After editing `pg_hba.conf`, reload PostgreSQL to apply changes:

```sql
SELECT pg_reload_conf();
```

---

## Authorization: What Can You Do?

Authorization answers a different question: "Now that I know who you are, what are you allowed to do?"

Think of a hospital. A doctor can view patient records, a nurse can update vital signs, and a receptionist can only see appointment schedules. Everyone is authenticated (they have ID badges), but they have different levels of authorization.

### CREATE ROLE and CREATE USER

In PostgreSQL, users and roles are almost the same thing. The only difference is that `CREATE USER` automatically adds the `LOGIN` privilege.

```sql
-- Create a role (cannot log in by default)
CREATE ROLE read_only;

-- Create a user (can log in)
CREATE USER alice WITH PASSWORD 'secure_password_123';

-- These two are equivalent:
CREATE USER bob WITH PASSWORD 'bobs_password';
CREATE ROLE bob WITH LOGIN PASSWORD 'bobs_password';
```

Let us look at the output after creating these:

```
CREATE ROLE
CREATE ROLE
```

You can also set additional properties when creating a role:

```sql
CREATE ROLE admin_user WITH
    LOGIN
    PASSWORD 'admin_pass_456'
    CREATEDB
    CREATEROLE
    VALID UNTIL '2026-12-31';
```

Let us break this down:

- `LOGIN` -- This role can connect to the database.
- `PASSWORD` -- Sets the authentication password.
- `CREATEDB` -- This role can create new databases.
- `CREATEROLE` -- This role can create other roles.
- `VALID UNTIL` -- The password expires on this date.

### Viewing Existing Roles

```sql
SELECT rolname, rolsuper, rolcreatedb, rolcanlogin
FROM pg_roles
WHERE rolname NOT LIKE 'pg_%'
ORDER BY rolname;
```

```
+--------------+----------+-------------+-------------+
| rolname      | rolsuper | rolcreatedb | rolcanlogin |
+--------------+----------+-------------+-------------+
| admin_user   | f        | t           | t           |
| alice        | f        | f           | t           |
| bob          | f        | f           | t           |
| postgres     | t        | t           | t           |
| read_only    | f        | f           | f           |
+--------------+----------+-------------+-------------+
(5 rows)
```

Notice that `read_only` has `rolcanlogin` set to `f` (false) because we created it with `CREATE ROLE` instead of `CREATE USER`. The `postgres` user is a superuser (`rolsuper = t`), which means it can do anything.

---

## GRANT and REVOKE Privileges

Privileges control exactly what a role can do. Think of them as keys to different rooms.

### Common Privileges

```
+-------------+------------------------------------------+
| Privilege   | What It Allows                           |
+-------------+------------------------------------------+
| SELECT      | Read data from a table                   |
| INSERT      | Add new rows to a table                  |
| UPDATE      | Modify existing rows                     |
| DELETE      | Remove rows from a table                 |
| TRUNCATE    | Empty a table completely                 |
| REFERENCES  | Create foreign key constraints           |
| TRIGGER     | Create triggers on a table               |
| CREATE      | Create objects in a schema               |
| CONNECT     | Connect to a database                    |
| USAGE       | Use a schema or sequence                 |
| ALL         | All available privileges                 |
+-------------+------------------------------------------+
```

### Granting Privileges

```sql
-- Grant SELECT on a specific table
GRANT SELECT ON employees TO alice;

-- Grant multiple privileges
GRANT SELECT, INSERT, UPDATE ON orders TO bob;

-- Grant all privileges on a table
GRANT ALL ON products TO admin_user;

-- Grant on all tables in a schema
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;

-- Grant usage on a schema
GRANT USAGE ON SCHEMA public TO read_only;
```

Let us understand what each line does:

- **Line 1**: Alice can now read data from the `employees` table, but she cannot insert, update, or delete.
- **Line 2**: Bob can read, add, and modify data in the `orders` table, but he cannot delete rows.
- **Line 3**: `admin_user` can do everything with the `products` table.
- **Line 4**: The `read_only` role can read all tables in the `public` schema.
- **Line 5**: The `read_only` role can access objects in the `public` schema. Without this, even `SELECT` would fail.

### Revoking Privileges

```sql
-- Remove INSERT privilege from bob on orders
REVOKE INSERT ON orders FROM bob;

-- Remove all privileges
REVOKE ALL ON products FROM admin_user;

-- Remove from all tables in a schema
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM alice;
```

### Default Privileges

When new tables are created in the future, you want certain roles to automatically have access. Default privileges handle this:

```sql
-- Any new table created by postgres will be readable by read_only
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO read_only;

-- Any new sequence will be usable by app_user
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE ON SEQUENCES TO app_user;
```

Without default privileges, you would need to run `GRANT` every time a new table is created. That is tedious and easy to forget.

---

## Role Hierarchy

Roles can be members of other roles. This creates a hierarchy, like an organizational chart.

```
            +------------------+
            |   db_admin       |
            | (all privileges) |
            +--------+---------+
                     |
          +----------+----------+
          |                     |
  +-------+-------+    +-------+-------+
  |  db_writer    |    |  db_reader    |
  | (read + write)|    | (read only)   |
  +-------+-------+    +-------+-------+
          |                     |
    +-----+-----+         +----+----+
    |     |     |         |         |
  alice  bob  carol     dave      eve
```

Here is how to set this up:

```sql
-- Step 1: Create the base roles
CREATE ROLE db_reader;
CREATE ROLE db_writer;
CREATE ROLE db_admin;

-- Step 2: Grant privileges to base roles
GRANT USAGE ON SCHEMA public TO db_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO db_reader;

GRANT USAGE ON SCHEMA public TO db_writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO db_writer;

GRANT ALL ON SCHEMA public TO db_admin;
GRANT ALL ON ALL TABLES IN SCHEMA public TO db_admin;

-- Step 3: Build the hierarchy
GRANT db_reader TO db_writer;   -- writers can also read
GRANT db_writer TO db_admin;    -- admins can also write

-- Step 4: Assign users to roles
GRANT db_reader TO dave;
GRANT db_reader TO eve;
GRANT db_writer TO alice;
GRANT db_writer TO bob;
GRANT db_writer TO carol;
GRANT db_admin TO admin_user;
```

Now dave and eve can only read data. Alice, bob, and carol can read and write. The admin_user can do everything.

The beauty of this approach is maintenance. If you need to change what "read access" means, you only update the `db_reader` role. All members automatically get the updated privileges.

---

## Row-Level Security (RLS)

Regular privileges control access to entire tables. Row-Level Security goes further. It controls which specific rows a user can see or modify.

Think of an apartment building. Everyone has access to the lobby (the table), but each tenant can only enter their own apartment (their rows).

### Enabling RLS

```sql
-- Create a table for a multi-tenant application
CREATE TABLE tenant_data (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER NOT NULL,
    data        TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO tenant_data (tenant_id, data) VALUES
    (1, 'Tenant 1 - Secret report'),
    (1, 'Tenant 1 - Budget plan'),
    (2, 'Tenant 2 - Strategy doc'),
    (2, 'Tenant 2 - Meeting notes'),
    (3, 'Tenant 3 - Product roadmap');

-- Enable Row-Level Security on the table
ALTER TABLE tenant_data ENABLE ROW LEVEL SECURITY;
```

### Creating Policies

```sql
-- Each tenant can only see their own data
CREATE POLICY tenant_isolation ON tenant_data
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::INTEGER);
```

Let us break down this policy:

- `tenant_isolation` -- The name of the policy (you choose this).
- `ON tenant_data` -- The table this policy applies to.
- `FOR ALL` -- Applies to SELECT, INSERT, UPDATE, and DELETE.
- `USING (...)` -- The condition that must be true for a row to be visible.
- `current_setting('app.tenant_id')` -- Reads a session variable that your application sets.

### How It Works

```sql
-- Application sets the tenant context when a user connects
SET app.tenant_id = '1';

-- Now queries only return Tenant 1's data
SELECT * FROM tenant_data;
```

```
+----+-----------+--------------------------+---------------------+
| id | tenant_id | data                     | created_at          |
+----+-----------+--------------------------+---------------------+
|  1 |         1 | Tenant 1 - Secret report | 2025-01-15 09:00:00 |
|  2 |         1 | Tenant 1 - Budget plan   | 2025-01-15 09:00:00 |
+----+-----------+--------------------------+---------------------+
(2 rows)
```

Even though there are five rows in the table, Tenant 1 only sees two. The other rows are completely invisible. It is as if they do not exist.

```sql
-- Switch to Tenant 2
SET app.tenant_id = '2';

SELECT * FROM tenant_data;
```

```
+----+-----------+--------------------------+---------------------+
| id | tenant_id | data                     | created_at          |
+----+-----------+--------------------------+---------------------+
|  3 |         2 | Tenant 2 - Strategy doc  | 2025-01-15 09:00:00 |
|  4 |         2 | Tenant 2 - Meeting notes | 2025-01-15 09:00:00 |
+----+-----------+--------------------------+---------------------+
(2 rows)
```

### Separate Policies for Different Operations

You can create different policies for reading and writing:

```sql
-- Everyone can read public posts
CREATE POLICY read_public ON posts
    FOR SELECT
    USING (is_public = true);

-- Users can only edit their own posts
CREATE POLICY edit_own ON posts
    FOR UPDATE
    USING (author_id = current_setting('app.user_id')::INTEGER);

-- Users can only delete their own posts
CREATE POLICY delete_own ON posts
    FOR DELETE
    USING (author_id = current_setting('app.user_id')::INTEGER);
```

### Important Note About Superusers

Row-Level Security does not apply to superusers or table owners by default. To force it on the table owner:

```sql
ALTER TABLE tenant_data FORCE ROW LEVEL SECURITY;
```

---

## SQL Injection: The Most Dangerous Attack

SQL injection is one of the most common and devastating database attacks. Understanding it is critical for every developer.

### What Is SQL Injection?

SQL injection happens when an attacker inserts malicious SQL code into a query through user input. It is like someone writing extra instructions on a form, and the system blindly follows them.

### How It Works

Imagine a login form where a user enters their username and password. The application builds a query like this:

```
Dangerous code (DO NOT USE):

query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
```

If a normal user types `alice` and `mypassword`, the query becomes:

```sql
SELECT * FROM users
WHERE username = 'alice' AND password = 'mypassword';
```

That works fine. But what if an attacker types this as the username:

```
' OR '1'='1' --
```

Now the query becomes:

```sql
SELECT * FROM users
WHERE username = '' OR '1'='1' --' AND password = 'anything';
```

Let us break down what happened:

```
Original:  WHERE username = '___INPUT___' AND password = '...'

Injected:  WHERE username = '' OR '1'='1' --' AND password = '...'
                                  ^^^^^^^^  ^^
                                  Always     Comment (ignores
                                  true!      the rest)
```

The `OR '1'='1'` is always true, so the query returns ALL users. The `--` is a comment that ignores the password check entirely. The attacker just logged in without knowing any password.

### Even Worse: Destructive Injection

An attacker could type this as the username:

```
'; DROP TABLE users; --
```

The query becomes:

```sql
SELECT * FROM users WHERE username = ''; DROP TABLE users; --'...
```

This runs two commands: the SELECT query (which returns nothing), and then `DROP TABLE users`, which deletes the entire users table. Your application just lost all user data.

### How SQL Injection Looks Step by Step

```
Step 1: Attacker finds a search box on your website

Step 2: Instead of typing a normal search term, they type:
        ' UNION SELECT username, password FROM users --

Step 3: Your vulnerable code builds:
        SELECT name, price FROM products
        WHERE name LIKE '' UNION SELECT username, password FROM users --'

Step 4: The database runs BOTH queries:
        - First: searches products (returns nothing)
        - Second: returns all usernames and passwords!

Step 5: The attacker sees everyone's credentials on the search results page
```

### How to Prevent SQL Injection

The solution is simple: **never put user input directly into SQL strings**. Use parameterized queries instead.

**Bad (vulnerable):**

```python
# Python example - NEVER DO THIS
username = request.form['username']
query = "SELECT * FROM users WHERE username = '" + username + "'"
cursor.execute(query)
```

**Good (safe):**

```python
# Python example - ALWAYS DO THIS
username = request.form['username']
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))
```

The difference is that `%s` is a placeholder. The database driver handles the input safely, escaping any special characters. The attacker's input is treated as data, not as SQL code.

Here is how it looks in different languages:

```
+------------------+----------------------------------+
| Language         | Parameterized Query Example      |
+------------------+----------------------------------+
| Python (psycopg) | cursor.execute(sql, (param,))   |
| Java (JDBC)      | stmt.setString(1, param)        |
| Node.js (pg)     | pool.query(sql, [param])        |
| PHP (PDO)        | $stmt->execute([$param])        |
| C# (Npgsql)      | cmd.Parameters.AddWithValue()   |
+------------------+----------------------------------+
```

### Additional Prevention Measures

```sql
-- 1. Use least-privilege roles (limit what app user can do)
CREATE ROLE app_readonly WITH LOGIN PASSWORD 'readonly_pass';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

-- 2. Revoke unnecessary privileges
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- 3. Use views to limit exposed data
CREATE VIEW safe_user_list AS
SELECT id, username, email, created_at
FROM users;
-- The view hides password_hash and other sensitive columns

GRANT SELECT ON safe_user_list TO app_readonly;
```

Even if an attacker manages to inject SQL, the damage is limited because the role does not have permission to drop tables or read password columns.

---

## Encryption: Protecting Data at Rest and in Transit

Encryption converts readable data into an unreadable format that can only be decoded with the right key. Think of it as putting your data in a locked safe. Even if someone steals the safe, they cannot read what is inside without the key.

### Encryption in Transit (SSL/TLS)

When data travels between your application and the database, it passes through networks. Without encryption, anyone who intercepts this traffic can read it. This is called a "man-in-the-middle" attack.

```
Without SSL:
  App  ----[plain text: "SELECT * FROM users"]----> Database
              ^
              |
          Attacker reads everything!

With SSL:
  App  ----[encrypted: "x8#kL9$mQ2..."]----> Database
              ^
              |
          Attacker sees gibberish
```

#### Configuring SSL in PostgreSQL

In `postgresql.conf`:

```
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
ssl_ca_file = '/path/to/ca.crt'
```

In `pg_hba.conf`, force SSL for remote connections:

```
# Require SSL for all remote connections
hostssl    all    all    0.0.0.0/0    scram-sha-256
```

Using `hostssl` instead of `host` means the connection must use SSL or it will be rejected.

#### Connecting with SSL from an Application

```python
# Python connection with SSL
import psycopg2

conn = psycopg2.connect(
    host='db.example.com',
    dbname='myapp',
    user='app_user',
    password='secure_password',
    sslmode='verify-full',
    sslrootcert='/path/to/ca.crt'
)
```

The `sslmode` options from least to most secure:

```
+---------------+------------------------------------------+
| sslmode       | Behavior                                 |
+---------------+------------------------------------------+
| disable       | No SSL (not recommended)                 |
| allow         | Try non-SSL first, then SSL              |
| prefer        | Try SSL first, then non-SSL (default)    |
| require       | Must use SSL, no certificate check       |
| verify-ca     | Must use SSL, verify CA certificate       |
| verify-full   | Must use SSL, verify CA + hostname        |
+---------------+------------------------------------------+
```

For production, always use `verify-full`.

### Encryption at Rest

Encryption at rest protects data stored on disk. If someone steals the hard drive, the data is unreadable.

#### Column-Level Encryption with pgcrypto

```sql
-- Enable the pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive data before storing
INSERT INTO customers (name, email, ssn_encrypted)
VALUES (
    'Alice Smith',
    'alice@example.com',
    pgp_sym_encrypt('123-45-6789', 'my_encryption_key')
);

-- Decrypt when reading
SELECT
    name,
    email,
    pgp_sym_decrypt(ssn_encrypted, 'my_encryption_key') AS ssn
FROM customers
WHERE name = 'Alice Smith';
```

```
+-------------+-------------------+--------------+
| name        | email             | ssn          |
+-------------+-------------------+--------------+
| Alice Smith | alice@example.com | 123-45-6789  |
+-------------+-------------------+--------------+
(1 row)
```

The `ssn_encrypted` column stores the data in an unreadable format. Only someone with the encryption key can decrypt it.

#### Full-Disk Encryption

For complete protection, use full-disk encryption at the operating system level:

- **Linux**: LUKS (Linux Unified Key Setup)
- **macOS**: FileVault
- **Windows**: BitLocker

This encrypts everything on the disk, including the database files, logs, and temporary files.

---

## Backup Strategies

Backups are your last line of defense. If everything else fails -- a hacker deletes your data, a disk crashes, or someone runs a bad query -- backups save you.

The rule of backups: "If you have not tested restoring from a backup, you do not have a backup."

### pg_dump: Logical Backups

`pg_dump` creates a text file containing SQL commands that can recreate your database.

```bash
# Dump a single database to a SQL file
pg_dump -h localhost -U postgres myapp_db > backup_2025_01_15.sql

# Dump in custom format (compressed, more flexible)
pg_dump -h localhost -U postgres -Fc myapp_db > backup_2025_01_15.dump

# Dump only the schema (no data)
pg_dump -h localhost -U postgres --schema-only myapp_db > schema_only.sql

# Dump only the data (no schema)
pg_dump -h localhost -U postgres --data-only myapp_db > data_only.sql

# Dump a specific table
pg_dump -h localhost -U postgres -t orders myapp_db > orders_backup.sql
```

Let us understand the flags:

- `-h localhost` -- Connect to this host.
- `-U postgres` -- Connect as this user.
- `-Fc` -- Use custom format (compressed and allows selective restore).
- `-t orders` -- Only dump the `orders` table.
- `--schema-only` -- Structure without data.
- `--data-only` -- Data without structure.

### pg_restore: Restoring Backups

```bash
# Restore from custom format dump
pg_restore -h localhost -U postgres -d myapp_db backup_2025_01_15.dump

# Restore only a specific table
pg_restore -h localhost -U postgres -d myapp_db -t orders backup_2025_01_15.dump

# Restore with clean (drop objects first)
pg_restore -h localhost -U postgres -d myapp_db --clean backup_2025_01_15.dump

# For plain SQL dumps, use psql instead
psql -h localhost -U postgres -d myapp_db < backup_2025_01_15.sql
```

### pg_dumpall: Backing Up Everything

`pg_dumpall` backs up all databases on a server, plus global objects like roles and tablespaces:

```bash
# Backup everything including roles
pg_dumpall -h localhost -U postgres > full_backup.sql

# Backup only global objects (roles, tablespaces)
pg_dumpall -h localhost -U postgres --globals-only > globals.sql
```

### Backup Strategy: The 3-2-1 Rule

A solid backup strategy follows the 3-2-1 rule:

```
+-------------------------------------------+
|          The 3-2-1 Backup Rule            |
+-------------------------------------------+
|                                           |
|  3 copies of your data                    |
|    - The original                         |
|    - A local backup                       |
|    - An offsite backup                    |
|                                           |
|  2 different types of storage             |
|    - Local disk                           |
|    - Cloud storage or tape                |
|                                           |
|  1 copy offsite                           |
|    - Different physical location          |
|    - Protects against fire, flood, theft  |
|                                           |
+-------------------------------------------+
```

### Automated Backup Script

Here is a practical backup script you might use:

```bash
#!/bin/bash
# Daily PostgreSQL backup script

# Configuration
DB_NAME="myapp_db"
DB_USER="postgres"
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y-%m-%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory if it does not exist
mkdir -p "$BACKUP_DIR"

# Create the backup
pg_dump -U "$DB_USER" -Fc "$DB_NAME" > "$BACKUP_DIR/${DB_NAME}_${DATE}.dump"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup successful: ${DB_NAME}_${DATE}.dump"
else
    echo "Backup FAILED!" >&2
    exit 1
fi

# Remove backups older than retention period
find "$BACKUP_DIR" -name "*.dump" -mtime +$RETENTION_DAYS -delete

echo "Old backups cleaned up (kept last $RETENTION_DAYS days)"
```

---

## Practical Exercise: Setting Up Roles for an Application

Let us put everything together by setting up a complete security model for a web application.

### The Scenario

You are building a blog application with three types of users:

1. **Readers** -- Can view published posts and comments.
2. **Authors** -- Can create and edit their own posts and comments.
3. **Administrators** -- Can manage everything, including users.

### Step 1: Create the Database and Tables

```sql
-- Connect as superuser and create the database
CREATE DATABASE blog_app;

-- Connect to blog_app, then create tables
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    role        VARCHAR(20) NOT NULL DEFAULT 'reader',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id          SERIAL PRIMARY KEY,
    author_id   INTEGER REFERENCES users(id),
    title       VARCHAR(200) NOT NULL,
    body        TEXT NOT NULL,
    is_published BOOLEAN DEFAULT false,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id          SERIAL PRIMARY KEY,
    post_id     INTEGER REFERENCES posts(id),
    user_id     INTEGER REFERENCES users(id),
    body        TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 2: Create the Roles

```sql
-- Base roles (no login)
CREATE ROLE blog_reader;
CREATE ROLE blog_author;
CREATE ROLE blog_admin;

-- Build hierarchy: authors can read, admins can do everything
GRANT blog_reader TO blog_author;
GRANT blog_author TO blog_admin;
```

### Step 3: Grant Privileges

```sql
-- Schema access for all roles
GRANT USAGE ON SCHEMA public TO blog_reader;
GRANT USAGE ON SCHEMA public TO blog_author;
GRANT USAGE ON SCHEMA public TO blog_admin;

-- Readers: can only SELECT published posts and all comments
GRANT SELECT ON posts TO blog_reader;
GRANT SELECT ON comments TO blog_reader;
GRANT SELECT ON users TO blog_reader;

-- Authors: can INSERT and UPDATE posts and comments
GRANT INSERT, UPDATE ON posts TO blog_author;
GRANT INSERT, UPDATE ON comments TO blog_author;
GRANT USAGE ON SEQUENCE posts_id_seq TO blog_author;
GRANT USAGE ON SEQUENCE comments_id_seq TO blog_author;

-- Admins: full control
GRANT ALL ON ALL TABLES IN SCHEMA public TO blog_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO blog_admin;
```

### Step 4: Enable Row-Level Security

```sql
-- Enable RLS on posts
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Readers can only see published posts
CREATE POLICY reader_see_published ON posts
    FOR SELECT
    TO blog_reader
    USING (is_published = true);

-- Authors can see published posts AND their own drafts
CREATE POLICY author_see_own ON posts
    FOR SELECT
    TO blog_author
    USING (
        is_published = true
        OR author_id = current_setting('app.user_id')::INTEGER
    );

-- Authors can only update their own posts
CREATE POLICY author_edit_own ON posts
    FOR UPDATE
    TO blog_author
    USING (author_id = current_setting('app.user_id')::INTEGER);

-- Authors can insert posts (as themselves)
CREATE POLICY author_insert ON posts
    FOR INSERT
    TO blog_author
    WITH CHECK (author_id = current_setting('app.user_id')::INTEGER);

-- Admins can do everything (bypass RLS)
CREATE POLICY admin_all ON posts
    FOR ALL
    TO blog_admin
    USING (true)
    WITH CHECK (true);
```

### Step 5: Create Application Users

```sql
-- Create actual login users and assign roles
CREATE USER app_reader WITH PASSWORD 'reader_pass_789';
GRANT blog_reader TO app_reader;

CREATE USER app_author WITH PASSWORD 'author_pass_456';
GRANT blog_author TO app_author;

CREATE USER app_admin WITH PASSWORD 'admin_pass_123';
GRANT blog_admin TO app_admin;
```

### Step 6: Test the Security

```sql
-- Insert test data as superuser
INSERT INTO users (username, email, role) VALUES
    ('alice', 'alice@blog.com', 'author'),
    ('bob', 'bob@blog.com', 'author'),
    ('admin', 'admin@blog.com', 'admin');

INSERT INTO posts (author_id, title, body, is_published) VALUES
    (1, 'Alice Published Post', 'Hello world!', true),
    (1, 'Alice Draft Post', 'Work in progress...', false),
    (2, 'Bob Published Post', 'Bob here!', true),
    (2, 'Bob Draft Post', 'Still writing...', false);
```

Now let us test as different users:

```sql
-- Test as reader
SET ROLE app_reader;
SELECT id, title, is_published FROM posts;
```

```
+----+----------------------+--------------+
| id | title                | is_published |
+----+----------------------+--------------+
|  1 | Alice Published Post | t            |
|  3 | Bob Published Post   | t            |
+----+----------------------+--------------+
(2 rows)
```

The reader only sees published posts. The drafts are invisible.

```sql
-- Test as Alice (author)
RESET ROLE;
SET ROLE app_author;
SET app.user_id = '1';

SELECT id, title, is_published FROM posts;
```

```
+----+----------------------+--------------+
| id | title                | is_published |
+----+----------------------+--------------+
|  1 | Alice Published Post | t            |
|  2 | Alice Draft Post     | f            |
|  3 | Bob Published Post   | t            |
+----+----------------------+--------------+
(3 rows)
```

Alice sees all published posts plus her own draft. She cannot see Bob's draft.

```sql
-- Alice tries to update Bob's post
UPDATE posts SET title = 'Hacked!' WHERE id = 3;
```

```
UPDATE 0
```

Zero rows updated. The RLS policy prevented Alice from modifying Bob's post.

### The Complete Security Architecture

```
+----------------------------------------------------------+
|                    Blog Application                       |
+----------------------------------------------------------+
|                                                          |
|  Web Browser                                             |
|       |                                                  |
|       v                                                  |
|  Application Server (sets app.user_id per session)       |
|       |                                                  |
|       v (SSL/TLS encrypted connection)                   |
|  PostgreSQL                                              |
|       |                                                  |
|       +-- pg_hba.conf (authentication)                   |
|       |       "Are you allowed to connect?"              |
|       |                                                  |
|       +-- Roles & Privileges (authorization)             |
|       |       "Can you access this table?"               |
|       |                                                  |
|       +-- Row-Level Security (fine-grained control)      |
|       |       "Can you see this specific row?"           |
|       |                                                  |
|       +-- Encryption at rest (pgcrypto / disk)           |
|       |       "Data safe even if disk is stolen"         |
|       |                                                  |
|       +-- Backups (pg_dump)                              |
|               "Recovery if all else fails"               |
|                                                          |
+----------------------------------------------------------+
```

---

## Common Mistakes

1. **Using the superuser for your application.** The `postgres` superuser should only be used for administration. Create a dedicated role with minimal privileges for your application.

2. **Forgetting to grant USAGE on schemas.** Even if you grant `SELECT` on a table, the user cannot access it without `USAGE` on the schema.

3. **Not setting default privileges.** New tables created after your `GRANT` statements will not have the privileges you expect. Use `ALTER DEFAULT PRIVILEGES`.

4. **Building SQL queries with string concatenation.** This is the number one cause of SQL injection. Always use parameterized queries.

5. **Storing passwords in plain text.** Use PostgreSQL's `scram-sha-256` authentication and never store application passwords without hashing (use bcrypt or argon2 in your application).

6. **Not testing backup restoration.** A backup you have never tested might be corrupted or incomplete. Regularly test restoring to a separate server.

7. **Leaving SSL disabled for remote connections.** Without SSL, passwords and data travel across the network in plain text.

---

## Best Practices

1. **Follow the Principle of Least Privilege.** Give each role only the minimum permissions it needs. Start with nothing and add privileges as required.

2. **Use role hierarchy.** Create base roles for common permission sets and assign users to these roles. This makes maintenance much easier.

3. **Enable RLS for multi-tenant applications.** Row-Level Security is the most reliable way to ensure data isolation between tenants.

4. **Always use parameterized queries.** There is no exception to this rule. Every query that includes user input must use parameters.

5. **Encrypt sensitive data.** Use SSL for connections and pgcrypto for sensitive columns like social security numbers or credit card data.

6. **Automate backups.** Set up a cron job to run backups daily. Test restoration monthly. Keep backups in multiple locations.

7. **Rotate passwords regularly.** Use the `VALID UNTIL` clause on roles and update passwords on a schedule.

8. **Audit access.** Enable PostgreSQL logging to track who accesses what data and when.

---

## Quick Summary

Database security is built in layers:

- **Authentication** (pg_hba.conf) verifies identity.
- **Authorization** (GRANT/REVOKE) controls table-level access.
- **Row-Level Security** controls row-level access.
- **Parameterized queries** prevent SQL injection.
- **Encryption** protects data in transit (SSL) and at rest (pgcrypto).
- **Backups** (pg_dump/pg_restore) provide recovery from disasters.

---

## Key Points

- Authentication verifies who you are. Authorization controls what you can do.
- `CREATE ROLE` creates a role without login. `CREATE USER` creates a role with login.
- `GRANT` gives privileges. `REVOKE` takes them away.
- Role hierarchy simplifies permission management by letting roles inherit from other roles.
- Row-Level Security (RLS) controls which rows a user can see or modify.
- SQL injection is prevented by using parameterized queries. Never concatenate user input into SQL.
- SSL/TLS encrypts data traveling between your application and the database.
- pgcrypto can encrypt sensitive columns stored in the database.
- pg_dump creates logical backups. pg_restore recovers from them.
- Follow the 3-2-1 rule: 3 copies, 2 storage types, 1 offsite.

---

## Practice Questions

1. What is the difference between authentication and authorization? Give a real-life example of each.

2. You have a table called `invoices` and a role called `accountant`. Write the SQL to grant the accountant read access and the ability to insert new invoices, but not delete or update them.

3. Explain what SQL injection is and why this code is dangerous:
   ```python
   query = "SELECT * FROM users WHERE id = " + user_input
   ```
   How would you fix it?

4. You are building a SaaS application where each company should only see their own data. Which PostgreSQL feature would you use, and how does it work?

5. What is the difference between `host` and `hostssl` in `pg_hba.conf`? Which one should you use for production?

---

## Exercises

### Exercise 1: Set Up a Secure Role System

Create a role system for a hospital database with the following requirements:

- **Doctors** can read all patient records and update diagnosis fields.
- **Nurses** can read patient records and update vital signs.
- **Receptionists** can read patient names and appointment dates but cannot see medical details.
- **Administrators** can do everything.

Create the roles, build the hierarchy, and write the GRANT statements.

### Exercise 2: Implement Row-Level Security

You have a `documents` table in a company where each department should only see its own documents. Create the table, enable RLS, and write policies so that:

- Users in the HR department only see HR documents.
- Users in the Engineering department only see Engineering documents.
- The CEO can see all documents.

### Exercise 3: Create a Backup and Restore Plan

Write a shell script that:

1. Creates a compressed backup of a database called `production_db`.
2. Stores it in `/var/backups/` with a timestamp in the filename.
3. Removes backups older than 7 days.
4. Logs the result to a file.

Then write the command to restore from one of these backups to a new database called `production_db_restored`.

---

## What Is Next?

You now know how to lock down your database like a vault. In the next chapter, you will put everything you have learned throughout this book into practice by building a complete e-commerce database from scratch. You will design the schema, create the tables, write queries, build views, add indexes, and implement triggers and functions -- a full, real-world project.
