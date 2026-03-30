# Chapter 3: Installing PostgreSQL

## What You Will Learn

By the end of this chapter, you will have:

- Understood why PostgreSQL is the best choice for learning SQL
- Installed PostgreSQL on your computer (Mac, Windows, or Linux)
- Set up pgAdmin 4, a graphical tool for managing databases
- Connected to PostgreSQL using the psql command line
- Created your first database
- Learned essential psql commands: `\l`, `\dt`, `\d`, and more
- Troubleshot common installation errors

## Why This Chapter Matters

You have learned the theory. Now it is time to install the tools and get your hands dirty. You cannot learn SQL by just reading about it. You need to type commands, see results, make mistakes, and fix them. This chapter sets up your workspace so you can follow along with every example in the rest of the book.

---

## Why PostgreSQL?

Before we install anything, let us briefly revisit why we are using PostgreSQL.

```
+-----------------------------+-----------------------------------+
| Reason                      | Details                           |
+-----------------------------+-----------------------------------+
| Free and open source        | No license fees, ever             |
| Standards-compliant         | Follows the SQL standard closely  |
| Feature-rich                | JSON, arrays, full-text search,   |
|                             |   window functions, CTEs, more    |
| Reliable                    | Used by Apple, Instagram, Spotify |
| Great community             | Excellent documentation and help  |
| Good for learning           | What you learn transfers to other |
|                             |   databases                       |
| Runs everywhere             | Mac, Windows, Linux, cloud        |
+-----------------------------+-----------------------------------+
```

PostgreSQL has been in active development since 1996. It is battle-tested, well-documented, and trusted by organizations of all sizes.

---

## Installing PostgreSQL on Mac

There are several ways to install PostgreSQL on a Mac. We will use **Homebrew**, which is the most popular package manager for macOS.

### Step 1: Install Homebrew (if you do not have it)

Open the **Terminal** app (you can find it in Applications > Utilities > Terminal, or search for "Terminal" using Spotlight with Command + Space).

Check if Homebrew is already installed:

```bash
brew --version
```

If you see a version number (like `Homebrew 4.x.x`), you are good. Skip to Step 2.

If you see "command not found," install Homebrew by pasting this command into your terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. You may need to enter your Mac password.

### Step 2: Install PostgreSQL

Run this command in your terminal:

```bash
brew install postgresql@16
```

This installs PostgreSQL version 16 (the latest stable version as of this writing). The download and installation may take a few minutes.

### Step 3: Start the PostgreSQL Service

After installation, start the PostgreSQL service so it runs in the background:

```bash
brew services start postgresql@16
```

You should see output like:

```
==> Successfully started `postgresql@16`
```

To verify it is running:

```bash
brew services list
```

You should see `postgresql@16` with a status of `started`.

### Step 4: Add PostgreSQL to Your PATH

You may need to add PostgreSQL to your PATH so your terminal can find the `psql` command. Run:

```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

> **Note:** If you use bash instead of zsh, replace `~/.zshrc` with `~/.bash_profile`.

### Step 5: Verify the Installation

```bash
psql --version
```

You should see something like:

```
psql (PostgreSQL) 16.x
```

### Step 6: Connect to PostgreSQL

```bash
psql postgres
```

You should see the PostgreSQL prompt:

```
postgres=#
```

Congratulations! You are connected to PostgreSQL. Type `\q` to quit for now. We will come back shortly.

---

## Installing PostgreSQL on Windows

### Step 1: Download the Installer

1. Go to the official PostgreSQL download page: **https://www.postgresql.org/download/windows/**
2. Click on **"Download the installer"** (this takes you to the EnterpriseDB page).
3. Download the latest version for Windows (PostgreSQL 16.x or newer).

### Step 2: Run the Installer

1. Double-click the downloaded `.exe` file.
2. Click **Next** through the welcome screen.
3. **Installation Directory:** Keep the default (usually `C:\Program Files\PostgreSQL\16`). Click Next.
4. **Select Components:** Make sure all boxes are checked:
   - PostgreSQL Server
   - pgAdmin 4
   - Stack Builder
   - Command Line Tools
5. **Data Directory:** Keep the default. Click Next.
6. **Password:** Enter a password for the `postgres` superuser. **Write this password down! You will need it.** Click Next.
7. **Port:** Keep the default port **5432**. Click Next.
8. **Locale:** Keep the default. Click Next.
9. Click **Next** and then **Finish** to complete the installation.

```
+------------------------------------------------------------------+
|                    IMPORTANT: REMEMBER YOUR PASSWORD              |
|                                                                   |
|  The password you set during installation is for the "postgres"   |
|  superuser account. You will need it every time you connect.      |
|                                                                   |
|  If you forget it, you will need to reset it, which is a pain.    |
|  Write it somewhere safe!                                         |
+------------------------------------------------------------------+
```

### Step 3: Verify the Installation

1. Open the **Start Menu**.
2. Search for **"SQL Shell (psql)"** and open it.
3. Press **Enter** for each prompt to accept the defaults (Server, Database, Port, Username).
4. Enter the password you set during installation.

You should see:

```
postgres=#
```

### Step 4: Add psql to Your PATH (Optional but Recommended)

To use `psql` from any command prompt or PowerShell window:

1. Open **System Properties** (search for "Environment Variables" in the Start Menu).
2. Click **Environment Variables**.
3. Under **System variables**, find `Path` and click **Edit**.
4. Click **New** and add: `C:\Program Files\PostgreSQL\16\bin`
5. Click **OK** on all windows.
6. Open a new Command Prompt or PowerShell and test:

```bash
psql --version
```

---

## Installing PostgreSQL on Linux (Ubuntu/Debian)

### Step 1: Update Your Package List

Open a terminal and run:

```bash
sudo apt update
```

### Step 2: Install PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib
```

The `postgresql-contrib` package includes useful additional tools and features.

### Step 3: Start and Enable the Service

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

The `enable` command makes sure PostgreSQL starts automatically when your computer boots.

### Step 4: Verify the Installation

```bash
psql --version
```

You should see the version number.

### Step 5: Connect to PostgreSQL

On Linux, PostgreSQL creates a system user called `postgres`. Switch to that user:

```bash
sudo -u postgres psql
```

You should see:

```
postgres=#
```

### Step 6: Set a Password for the postgres User

While connected to psql, set a password:

```sql
ALTER USER postgres PASSWORD 'your_secure_password';
```

Replace `your_secure_password` with an actual password. Remember this password.

Type `\q` to exit.

---

## Setting Up pgAdmin 4

**pgAdmin 4** is a free graphical tool for managing PostgreSQL databases. It gives you a visual interface instead of typing commands in a terminal. It is useful for browsing tables, running queries, and visualizing your data.

### Installing pgAdmin 4

**On Mac:**

```bash
brew install --cask pgadmin4
```

Or download from **https://www.pgadmin.org/download/pgadmin-4-macos/**

**On Windows:**

If you installed PostgreSQL using the EnterpriseDB installer, pgAdmin 4 was included. Find it in your Start Menu.

If not, download from **https://www.pgadmin.org/download/pgadmin-4-windows/**

**On Linux:**

```bash
sudo apt install pgadmin4-desktop
```

Or follow the official instructions at **https://www.pgadmin.org/download/pgadmin-4-apt/**

### First-Time Setup

1. Open pgAdmin 4.
2. It will ask you to set a **master password**. This is for pgAdmin itself, not PostgreSQL. Choose something you will remember.
3. In the left sidebar, click **Servers**.
4. Right-click **Servers** and select **Register > Server**.
5. In the **General** tab, give it a name like "Local PostgreSQL."
6. In the **Connection** tab:
   - Host: `localhost`
   - Port: `5432`
   - Maintenance database: `postgres`
   - Username: `postgres`
   - Password: the password you set during PostgreSQL installation
7. Click **Save**.

You should now see your PostgreSQL server in the sidebar. You can expand it to see databases, tables, and more.

```
+-- Servers
    +-- Local PostgreSQL
        +-- Databases
        |   +-- postgres (default database)
        +-- Login/Group Roles
        +-- Tablespaces
```

---

## The psql Command Line

While pgAdmin 4 is nice for visual exploration, **psql** is the command-line tool that professionals use daily. It is fast, powerful, and available on every system where PostgreSQL is installed.

### Connecting to PostgreSQL with psql

The basic connection command is:

```bash
psql -U postgres -d postgres
```

**Flags explained:**
- `-U postgres` means connect as the user "postgres."
- `-d postgres` means connect to the database named "postgres."

On Mac (with Homebrew), you can often just type:

```bash
psql postgres
```

On Linux:

```bash
sudo -u postgres psql
```

### The psql Prompt

Once connected, you see a prompt like this:

```
postgres=#
```

- `postgres` is the name of the database you are connected to.
- `=#` means you are a superuser (administrator). Regular users see `=>`.

---

## Creating Your First Database

Let us create a database called `school`. Connect to psql and run:

```sql
CREATE DATABASE school;
```

```
CREATE DATABASE
```

That one line created a new, empty database called `school`. Now connect to it:

```bash
\c school
```

```
You are now connected to database "school" as user "postgres".
school=#
```

Notice the prompt changed from `postgres=#` to `school=#`. This tells you which database you are working in.

### Creating a Simple Table

Let us create a `students` table inside the `school` database:

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INTEGER
);
```

```
CREATE TABLE
```

**Line-by-line:**
- `CREATE TABLE students (` starts the table definition.
- `id SERIAL PRIMARY KEY` creates an auto-incrementing integer as the primary key.
- `first_name VARCHAR(50) NOT NULL` creates a text column that cannot be empty.
- `last_name VARCHAR(50) NOT NULL` same as above, for the last name.
- `email VARCHAR(100) UNIQUE` creates a text column where every value must be different.
- `age INTEGER` creates a whole number column.
- `)` ends the table definition.

### Inserting Some Data

```sql
INSERT INTO students (first_name, last_name, email, age)
VALUES ('Alice', 'Johnson', 'alice@email.com', 20);

INSERT INTO students (first_name, last_name, email, age)
VALUES ('Bob', 'Smith', 'bob@email.com', 22);
```

```
INSERT 0 1
INSERT 0 1
```

### Querying the Data

```sql
SELECT * FROM students;
```

```
 id | first_name | last_name |      email      | age
----+------------+-----------+-----------------+-----
  1 | Alice      | Johnson   | alice@email.com |  20
  2 | Bob        | Smith     | bob@email.com   |  22
(2 rows)
```

You just created a database, created a table, inserted data, and queried it. That is the full cycle.

---

## Essential psql Commands

psql has many built-in commands that start with a backslash (`\`). These are not SQL. They are psql-specific shortcuts.

### \l — List All Databases

```
\l
```

```
                                  List of databases
   Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges
-----------+----------+----------+-------------+-------------+-----------------------
 postgres  | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
 school    | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
 template0 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres          +
           |          |          |             |             | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres          +
           |          |          |             |             | postgres=CTc/postgres
(4 rows)
```

You can see the `school` database we just created, along with the default databases (`postgres`, `template0`, `template1`).

### \c — Connect to a Database

```
\c school
```

```
You are now connected to database "school" as user "postgres".
```

### \dt — List All Tables in the Current Database

```
\dt
```

```
          List of relations
 Schema |   Name   | Type  |  Owner
--------+----------+-------+----------
 public | students | table | postgres
(1 row)
```

### \d — Describe a Table's Structure

```
\d students
```

```
                                      Table "public.students"
   Column   |          Type          | Collation | Nullable |               Default
------------+------------------------+-----------+----------+-------------------------------------
 id         | integer                |           | not null | nextval('students_id_seq'::regclass)
 first_name | character varying(50)  |           | not null |
 last_name  | character varying(50)  |           | not null |
 email      | character varying(100) |           |          |
 age        | integer                |           |          |
Indexes:
    "students_pkey" PRIMARY KEY, btree (id)
    "students_email_key" UNIQUE CONSTRAINT, btree (email)
```

This shows you every column, its data type, whether it can be NULL, and its default value. It also shows indexes and constraints.

### Other Useful psql Commands

```
+-----------+-------------------------------------------+
| Command   | What It Does                              |
+-----------+-------------------------------------------+
| \l        | List all databases                        |
| \c dbname | Connect to a database                     |
| \dt       | List tables in current database            |
| \d table  | Describe a table (columns, types, etc.)   |
| \du       | List all users/roles                      |
| \di       | List all indexes                          |
| \dn       | List all schemas                          |
| \df       | List all functions                        |
| \timing   | Toggle query execution time display       |
| \x        | Toggle expanded output (vertical display) |
| \q        | Quit psql                                 |
| \?        | Show all psql commands                    |
| \h        | Show SQL command help                     |
| \h SELECT | Show help for the SELECT command           |
+-----------+-------------------------------------------+
```

### Multiline Commands

In psql, a command does not run until you type a semicolon (`;`) and press Enter. This means you can split commands across multiple lines:

```
school=# SELECT
school-#   first_name,
school-#   last_name
school-# FROM students;
```

Notice the prompt changes from `=#` to `-#` when you are in the middle of a command. The `-#` tells you, "I am waiting for more input."

If you forget the semicolon:

```
school=# SELECT * FROM students
school-#
```

The database is waiting. Just type `;` and press Enter:

```
school-# ;
```

---

## Common Errors and Fixes

### Error: "psql: command not found"

**Cause:** PostgreSQL's `bin` directory is not in your PATH.

**Fix (Mac):**
```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Fix (Windows):** Add `C:\Program Files\PostgreSQL\16\bin` to your system PATH (see the Windows installation section).

**Fix (Linux):** PostgreSQL is usually in the PATH by default. If not:
```bash
sudo apt install postgresql-client
```

### Error: "connection refused" or "could not connect to server"

**Cause:** The PostgreSQL service is not running.

**Fix (Mac):**
```bash
brew services start postgresql@16
```

**Fix (Windows):** Open the Services app (search for "Services" in Start Menu), find "postgresql-x64-16", and click Start.

**Fix (Linux):**
```bash
sudo systemctl start postgresql
```

### Error: "password authentication failed for user postgres"

**Cause:** Wrong password.

**Fix:** If you forgot your password, you need to reset it. The process varies by operating system.

**On Mac (Homebrew):** Homebrew installations often do not require a password. Try:
```bash
psql postgres
```

**On Linux:** Edit the pg_hba.conf file to temporarily allow passwordless access:
```bash
sudo -u postgres psql
ALTER USER postgres PASSWORD 'new_password';
\q
```

### Error: "database does not exist"

**Cause:** You are trying to connect to a database that has not been created yet.

**Fix:** Connect to the default `postgres` database first, then create your database:
```bash
psql -U postgres -d postgres
```
```sql
CREATE DATABASE school;
```

### Error: "role does not exist"

**Cause:** The username you are trying to connect with does not exist in PostgreSQL.

**Fix:** Create the role:
```bash
sudo -u postgres psql
```
```sql
CREATE ROLE your_username WITH LOGIN PASSWORD 'your_password';
```

### Error: "permission denied"

**Cause:** Your user does not have the necessary privileges.

**Fix:** Grant privileges:
```sql
GRANT ALL PRIVILEGES ON DATABASE school TO your_username;
```

---

## Verifying Everything Works

Let us run through a quick checklist to make sure your setup is complete.

```
+----+----------------------------------------+------------------+
| #  | Check                                  | Command          |
+----+----------------------------------------+------------------+
| 1  | PostgreSQL is installed                | psql --version   |
| 2  | PostgreSQL service is running          | (platform-specific)|
| 3  | You can connect to psql                | psql postgres    |
| 4  | You can list databases                 | \l               |
| 5  | You can create a database              | CREATE DATABASE  |
| 6  | You can connect to your database       | \c school        |
| 7  | You can create a table                 | CREATE TABLE     |
| 8  | You can insert data                    | INSERT INTO      |
| 9  | You can query data                     | SELECT * FROM    |
| 10 | pgAdmin 4 connects to your server      | (visual check)   |
+----+----------------------------------------+------------------+
```

If all ten checks pass, you are ready for the rest of this book.

---

## Common Mistakes

1. **Not starting the PostgreSQL service.** Installing PostgreSQL does not automatically start it on every system. Make sure the service is running before trying to connect.

2. **Forgetting the semicolon.** Every SQL command in psql must end with a semicolon (`;`). If your command does not seem to run, you probably forgot the semicolon.

3. **Confusing psql commands and SQL commands.** Commands that start with a backslash (like `\l`, `\dt`) are psql shortcuts. They do not end with a semicolon. SQL commands (like `SELECT`, `CREATE TABLE`) must end with a semicolon.

4. **Forgetting the postgres password.** Write it down during installation. You will need it many times.

5. **Trying to run psql before adding it to PATH.** If `psql` is not found, you need to add the PostgreSQL bin directory to your system PATH.

---

## Best Practices

1. **Use psql for learning.** It is the fastest way to experiment. Type a command, see the result immediately.

2. **Use pgAdmin 4 for exploring.** When you want to browse tables visually or see table structures at a glance, pgAdmin is helpful.

3. **Keep your PostgreSQL service running.** On Mac, use `brew services start postgresql@16` so it starts automatically. On Linux, use `systemctl enable postgresql`.

4. **Create a separate database for each project.** Do not dump everything into the default `postgres` database. Create a `school` database for school examples, a `bookstore` database for bookstore examples, and so on.

5. **Use `\d table_name` frequently.** It is the fastest way to remind yourself what columns a table has and what types they use.

---

## Quick Summary

PostgreSQL is free, powerful, and the best RDBMS for learning SQL. You can install it on Mac (using Homebrew), Windows (using the EnterpriseDB installer), or Linux (using apt). pgAdmin 4 provides a graphical interface, while psql provides a fast command-line interface. Essential psql commands include `\l` (list databases), `\dt` (list tables), `\d` (describe a table), and `\c` (connect to a database). Every SQL command must end with a semicolon.

---

## Key Points

- Install PostgreSQL using Homebrew (Mac), the EnterpriseDB installer (Windows), or apt (Linux).
- **psql** is the command-line client. **pgAdmin 4** is the graphical client.
- The default superuser is called `postgres`.
- Use `\l` to list databases, `\dt` to list tables, `\d table_name` to describe a table.
- Use `\c database_name` to switch to a different database.
- Every SQL statement must end with a semicolon (`;`).
- psql backslash commands (like `\l`) do not need a semicolon.
- Keep the PostgreSQL service running while you work.
- Always remember your `postgres` user password.

---

## Practice Questions

1. What is the difference between psql and pgAdmin 4? When would you use each?

2. You type `SELECT * FROM students` in psql and nothing happens. What did you probably forget?

3. What psql command shows you the columns, data types, and constraints of a table called `courses`?

4. What is the default port number for PostgreSQL?

5. You get an error "connection refused" when trying to run psql. What is the most likely cause and how do you fix it?

---

## Exercises

### Exercise 1: Install and Verify

Follow the installation instructions for your operating system. Verify your installation by:
1. Checking the PostgreSQL version with `psql --version`.
2. Connecting to the default database with `psql postgres`.
3. Running `\l` to list all databases.
4. Creating a test database called `my_first_db`.
5. Connecting to it with `\c my_first_db`.
6. Running `\dt` to confirm it has no tables yet.

### Exercise 2: Create a Practice Database

1. Create a database called `practice`.
2. Connect to it.
3. Create a table called `movies` with these columns:
   - `id` (auto-incrementing primary key)
   - `title` (text, up to 200 characters, required)
   - `release_year` (integer)
   - `rating` (numeric with one decimal place)
4. Insert three movies of your choice.
5. Run `SELECT * FROM movies;` to see your data.
6. Run `\d movies` to see the table structure.

### Exercise 3: Explore psql

Connect to your `practice` database and try each of these commands. Write down what each one shows you:
1. `\l`
2. `\dt`
3. `\d movies`
4. `\du`
5. `\timing`
6. `SELECT * FROM movies;` (after turning on timing)
7. `\x` then `SELECT * FROM movies;` (what changed?)

---

## What Is Next?

Now that PostgreSQL is installed and running, you are ready to start building real databases. In Chapter 4, you will learn how to **create databases and tables** using SQL. You will master the `CREATE TABLE` command, learn about column constraints like NOT NULL and UNIQUE, and build complete, well-structured tables from scratch.
