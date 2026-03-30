# Chapter 11: Volumes and Persistent Data

## What You Will Learn

By the end of this chapter, you will be able to:

- Explain why containers lose data when they are removed
- Describe the three types of Docker storage: volumes, bind mounts, and tmpfs mounts
- Create and manage named volumes with `docker volume create`
- Use bind mounts to share files between your computer and a container
- Inspect volumes to see where Docker stores data
- Persist database data using a PostgreSQL container with a volume
- Back up and restore volume data
- Use read-only volumes for security

## Why This Chapter Matters

Here is a problem that surprises every Docker beginner: you start a PostgreSQL database in a container, create tables, insert data, and everything works perfectly. Then you stop and remove the container. You start a new one, and all your data is gone. Every table. Every row. Vanished.

This happens because containers are **ephemeral** by design -- they are meant to be temporary. When a container is removed, everything inside it is deleted, including any files the application created.

**Real-life analogy:** A container is like a whiteboard. You can write anything on it, but when you erase the whiteboard (remove the container), everything is gone. Volumes are like a notebook -- even if you throw away the whiteboard, the notebook keeps your notes safe.

This chapter teaches you how to use volumes to persist data beyond the lifetime of a container. This is essential for databases, uploaded files, application logs, and any data you cannot afford to lose.

---

## Why Containers Lose Data

Every container has a **writable layer** that sits on top of the read-only image layers. When the application writes files, they go into this writable layer.

```
+--------------------------------------------------+
|    Container Filesystem                          |
+--------------------------------------------------+
|                                                  |
|    +---------------------------------------+     |
|    | Writable Layer (container-specific)    |     |
|    | - Application logs                    |     |
|    | - Database files                      |     |
|    | - Uploaded files                      |     |
|    | - Temp files                          |     |
|    +---------------------------------------+     |
|    | Read-only Image Layer 4 (CMD)         |     |
|    +---------------------------------------+     |
|    | Read-only Image Layer 3 (COPY code)   |     |
|    +---------------------------------------+     |
|    | Read-only Image Layer 2 (npm install) |     |
|    +---------------------------------------+     |
|    | Read-only Image Layer 1 (FROM node)   |     |
|    +---------------------------------------+     |
|                                                  |
|    When the container is removed,                |
|    the writable layer is DELETED.                |
|    The image layers remain untouched.            |
|                                                  |
+--------------------------------------------------+
```

### Demonstration: Data Loss

```bash
# Start a container and create a file
$ docker run -it --name test alpine /bin/sh
/ # echo "Important data!" > /my-data.txt
/ # cat /my-data.txt
Important data!
/ # exit

# The container is stopped but still exists
$ docker ps -a | grep test
CONTAINER ID   IMAGE    STATUS                    NAMES
a1b2c3d4       alpine   Exited (0) 5 seconds ago  test

# The data is still there in the stopped container
$ docker start test
$ docker exec test cat /my-data.txt
Important data!
$ docker stop test

# Now REMOVE the container
$ docker rm test
test

# Start a new container from the same image
$ docker run -it --name test alpine /bin/sh
/ # cat /my-data.txt
cat: can't open '/my-data.txt': No such file or directory
/ # exit

# The data is gone!
```

This is by design. Containers are meant to be disposable. But obviously, we need a way to keep important data. That is where volumes come in.

---

## Three Types of Docker Storage

Docker provides three ways to persist data:

```
+--------------------------------------------------+
|    Docker Storage Types                          |
+--------------------------------------------------+
|                                                  |
|    1. VOLUMES                                    |
|       Managed by Docker in a special area        |
|       Best for production data                   |
|       /var/lib/docker/volumes/                   |
|                                                  |
|    2. BIND MOUNTS                                |
|       Map a host directory to a container path   |
|       Best for development (live code reload)    |
|       Any path on the host machine               |
|                                                  |
|    3. TMPFS MOUNTS                               |
|       Stored in memory only (RAM)                |
|       Never written to disk                      |
|       Best for sensitive temporary data          |
|                                                  |
+--------------------------------------------------+
```

### Visual Comparison

```
+--------------------------------------------------+
|                     Host Machine                 |
|                                                  |
|  Filesystem:                Memory:              |
|  /var/lib/docker/volumes/   +----------+         |
|  +----------------+         | tmpfs    |         |
|  | Docker Volume  |         | mount    |         |
|  +-------+--------+         +----+-----+         |
|          |                       |               |
|  /home/user/project/             |               |
|  +----------------+              |               |
|  | Bind Mount     |              |               |
|  +-------+--------+              |               |
|          |                       |               |
|          v                       v               |
|  +------------------------------------------+   |
|  |            Container                      |   |
|  |                                           |   |
|  |  /data     /code        /tmp/secrets      |   |
|  |  (volume)  (bind mount) (tmpfs)           |   |
|  +------------------------------------------+   |
|                                                  |
+--------------------------------------------------+
```

---

## Named Volumes: Docker-Managed Storage

**Named volumes** are the recommended way to persist data. Docker creates and manages them in a special directory on your host machine.

**Real-life analogy:** A named volume is like a storage locker. You rent a locker (create a volume), put things in it (write data), and the locker keeps your stuff safe even if you move to a different apartment (remove the container). You can even give a new apartment (new container) the key to the same locker.

### Creating a Volume

```bash
$ docker volume create my-data
my-data
```

That is it. Docker creates a volume named `my-data` and manages it for you.

### Listing Volumes

```bash
$ docker volume ls
DRIVER    VOLUME NAME
local     my-data
```

### Using a Volume with a Container

You attach a volume to a container using the `-v` (or `--mount`) flag:

```bash
# Syntax: -v volume_name:container_path
$ docker run -d \
  -v my-data:/app/data \
  --name app1 \
  alpine sleep 3600
```

This mounts the `my-data` volume to `/app/data` inside the container. Any files written to `/app/data` are actually stored in the volume.

### Demonstration: Data Persists

```bash
# Create a volume
$ docker volume create demo-data
demo-data

# Start container 1 and write data
$ docker run -it --name writer -v demo-data:/data alpine /bin/sh
/ # echo "Hello from container 1!" > /data/message.txt
/ # echo "This data will survive!" >> /data/message.txt
/ # cat /data/message.txt
Hello from container 1!
This data will survive!
/ # exit

# Remove container 1
$ docker rm writer
writer

# Start container 2 with the SAME volume
$ docker run -it --name reader -v demo-data:/data alpine /bin/sh
/ # cat /data/message.txt
Hello from container 1!
This data will survive!
/ # exit

# The data survived! The volume persists even after container removal.
```

```
+--------------------------------------------------+
|    Volume Persistence                            |
+--------------------------------------------------+
|                                                  |
|    Container 1 (writer):                         |
|    Writes data to /data/message.txt              |
|    Container is removed ---> data remains!       |
|                                                  |
|    demo-data volume: [message.txt survives]      |
|                                                  |
|    Container 2 (reader):                         |
|    Mounts same volume to /data                   |
|    Reads /data/message.txt ---> data is there!   |
|                                                  |
+--------------------------------------------------+
```

### Auto-Creating Volumes

If you use `-v` with a volume name that does not exist, Docker creates it automatically:

```bash
# Docker creates "auto-volume" automatically
$ docker run -v auto-volume:/data alpine echo "Volume created!"

$ docker volume ls
DRIVER    VOLUME NAME
local     auto-volume
local     demo-data
```

---

## Volume Inspection

You can inspect a volume to see its details:

```bash
$ docker volume inspect my-data
[
    {
        "CreatedAt": "2024-01-15T10:30:00Z",
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/my-data/_data",
        "Name": "my-data",
        "Options": {},
        "Scope": "local"
    }
]
```

### Understanding the Output

```
+--------------------------------------------------+
|    Volume Inspect Fields                         |
+--------------------------------------------------+
|                                                  |
|    Name        The volume name                   |
|    Driver      Storage driver (usually "local")  |
|    Mountpoint  Where Docker stores the data on   |
|                your host machine                 |
|    Scope       "local" means this machine only   |
|    CreatedAt   When the volume was created        |
|                                                  |
+--------------------------------------------------+
```

The **Mountpoint** shows you where the volume data physically lives on your host machine. On Linux, it is typically under `/var/lib/docker/volumes/`. On Docker Desktop (Mac/Windows), this path is inside the Docker VM.

---

## Bind Mounts: Sharing Host Directories

**Bind mounts** map a specific directory on your computer to a directory inside the container. Unlike volumes, you control exactly where the data is stored.

**Real-life analogy:** A bind mount is like putting a window between two rooms. Whatever is in the room on one side of the window is visible from the other side. If you add something from either side, both sides see it.

### Syntax

```bash
# Using -v flag (short form)
$ docker run -v /host/path:/container/path image

# Using --mount flag (long form, more explicit)
$ docker run --mount type=bind,source=/host/path,target=/container/path image
```

### Example: Development with Live Code Reload

This is the most common use of bind mounts -- mounting your source code into a container so changes you make on your computer are instantly visible inside the container:

```bash
# Your project is at /home/user/my-project
$ ls /home/user/my-project
Dockerfile  package.json  server.js  src/

# Mount it into the container
$ docker run -d \
  -p 3000:3000 \
  -v /home/user/my-project:/app \
  --name dev-server \
  node:18-alpine \
  sh -c "cd /app && npm install && npx nodemon server.js"
```

Now when you edit `server.js` on your computer, the changes are instantly visible inside the container. If you are using a tool like nodemon, it will detect the change and restart the server automatically.

```
+--------------------------------------------------+
|    Bind Mount for Development                    |
+--------------------------------------------------+
|                                                  |
|    Host Machine           Container              |
|    /home/user/my-project  /app                   |
|    +------------------+   +------------------+   |
|    | server.js        |<->| server.js        |   |
|    | package.json     |<->| package.json     |   |
|    | src/             |<->| src/             |   |
|    +------------------+   +------------------+   |
|                                                  |
|    Edit server.js on     Container sees the      |
|    your computer  -----> change immediately      |
|                                                  |
+--------------------------------------------------+
```

### Using $(pwd) for the Current Directory

Instead of typing the full path, you can use `$(pwd)` to refer to the current directory:

```bash
# Mount the current directory
$ cd /home/user/my-project
$ docker run -d \
  -p 3000:3000 \
  -v $(pwd):/app \
  --name dev-server \
  node:18-alpine \
  sh -c "cd /app && npm install && npx nodemon server.js"
```

`$(pwd)` is a shell command that prints the current working directory. It gets replaced with the full path before Docker sees it.

### Bind Mount vs Volume

```
+--------------------------------------------------+
|    Bind Mounts vs Volumes                        |
+--------------------------------------------------+
|                                                  |
|    Feature          Volume        Bind Mount     |
|    ------------------------------------------    |
|    Managed by       Docker        You            |
|    Location         Docker area   Anywhere       |
|    Create           docker volume Just use -v    |
|    Portable         Yes           No (host path) |
|    Best for         Production    Development    |
|    Pre-populate     Yes           No             |
|    Backup           docker cmds   cp/tar/rsync   |
|    Performance      Optimized     Direct access  |
|                                                  |
|    Use VOLUMES for production data               |
|    Use BIND MOUNTS for development               |
|                                                  |
+--------------------------------------------------+
```

### An Important Difference

When you mount a volume to a container path that already has data, the existing data in the image is copied to the volume (if the volume is empty). This is called **pre-population**.

With bind mounts, the host directory **replaces** whatever was in the container at that path. If the host directory is empty, the container path will be empty too, even if the image had files there.

```
+--------------------------------------------------+
|    Pre-Population Behavior                       |
+--------------------------------------------------+
|                                                  |
|    Image has /app/config with default files      |
|                                                  |
|    Volume (empty):                               |
|    -v my-vol:/app/config                         |
|    Result: Volume gets the default files          |
|    (pre-populated from the image)                |
|                                                  |
|    Bind Mount (empty directory):                 |
|    -v /host/empty:/app/config                    |
|    Result: Container sees empty directory!        |
|    (host directory overrides image content)       |
|                                                  |
+--------------------------------------------------+
```

---

## tmpfs Mounts: Memory-Only Storage

**tmpfs mounts** store data in the host's memory (RAM). The data is never written to disk and disappears when the container stops.

**Real-life analogy:** A tmpfs mount is like a whiteboard in your office. You can write on it while you are there, but when you leave (the container stops), everything is erased. Nothing was ever saved permanently.

### Syntax

```bash
$ docker run --tmpfs /path/in/container image
# or
$ docker run --mount type=tmpfs,destination=/path/in/container image
```

### When to Use tmpfs

- **Sensitive data** that should never be written to disk (like encryption keys)
- **Temporary files** that do not need to persist
- **Performance** for high-speed temporary storage

### Example

```bash
$ docker run -d \
  --tmpfs /app/temp \
  --name secure-app \
  my-app

# Data in /app/temp is stored in RAM only
# It disappears when the container stops
```

---

## Database Persistence with PostgreSQL

The most important use of volumes is persisting database data. Let us walk through a complete example with PostgreSQL.

### The Problem: Data Loss Without Volumes

```bash
# Start PostgreSQL WITHOUT a volume
$ docker run -d \
  --name postgres-no-vol \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  postgres:16-alpine

# Wait for it to start
$ sleep 5

# Create a table and insert data
$ docker exec -it postgres-no-vol psql -U postgres -c "
  CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT);
  INSERT INTO users (name) VALUES ('Alice'), ('Bob');
  SELECT * FROM users;
"
 id | name
----+-------
  1 | Alice
  2 | Bob
(2 rows)

# Remove the container
$ docker stop postgres-no-vol && docker rm postgres-no-vol

# Start a new PostgreSQL container
$ docker run -d \
  --name postgres-no-vol \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  postgres:16-alpine

$ sleep 5

# Try to read the data
$ docker exec -it postgres-no-vol psql -U postgres -c "SELECT * FROM users;"
ERROR:  relation "users" does not exist

# Data is gone!
$ docker stop postgres-no-vol && docker rm postgres-no-vol
```

### The Solution: Volumes

```bash
# Create a volume for PostgreSQL data
$ docker volume create postgres-data

# Start PostgreSQL WITH a volume
$ docker run -d \
  --name postgres-vol \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:16-alpine

$ sleep 5

# Create a table and insert data
$ docker exec -it postgres-vol psql -U postgres -c "
  CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT);
  INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie');
  SELECT * FROM users;
"
 id |  name
----+---------
  1 | Alice
  2 | Bob
  3 | Charlie
(3 rows)

# Remove the container (the volume stays!)
$ docker stop postgres-vol && docker rm postgres-vol

# Start a NEW container with the SAME volume
$ docker run -d \
  --name postgres-new \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:16-alpine

$ sleep 5

# The data is still there!
$ docker exec -it postgres-new psql -U postgres -c "SELECT * FROM users;"
 id |  name
----+---------
  1 | Alice
  2 | Bob
  3 | Charlie
(3 rows)
```

The data survived because it was stored in the `postgres-data` volume, not in the container's writable layer.

```
+--------------------------------------------------+
|    PostgreSQL with Volume                        |
+--------------------------------------------------+
|                                                  |
|    Container 1 (postgres-vol):                   |
|    /var/lib/postgresql/data -> postgres-data vol  |
|    - Creates tables, inserts rows                |
|    - Container is removed                        |
|                                                  |
|    postgres-data volume:                         |
|    [Tables and rows are safely stored here]      |
|                                                  |
|    Container 2 (postgres-new):                   |
|    /var/lib/postgresql/data -> postgres-data vol  |
|    - Same volume, same data!                     |
|    - Tables and rows are all there               |
|                                                  |
+--------------------------------------------------+
```

### How Did We Know to Use /var/lib/postgresql/data?

The PostgreSQL Docker image documentation tells you where it stores data. Every database image documents its data directory:

```
+--------------------------------------------------+
|    Common Database Data Directories              |
+--------------------------------------------------+
|                                                  |
|    Database        Data Directory                |
|    -----------------------------------------------
|    PostgreSQL      /var/lib/postgresql/data       |
|    MySQL           /var/lib/mysql                 |
|    MongoDB         /data/db                      |
|    Redis           /data                         |
|                                                  |
+--------------------------------------------------+
```

---

## Backup and Restore

Backing up volume data is essential. Here are two common approaches.

### Method 1: Copy From a Container

```bash
# Start a temporary container that mounts the volume
# and copies data to a tar archive
$ docker run --rm \
  -v postgres-data:/source \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/postgres-backup.tar.gz -C /source .

# This creates postgres-backup.tar.gz in your current directory
$ ls -lh postgres-backup.tar.gz
-rw-r--r--  1 user  staff   15M Jan 15 12:00 postgres-backup.tar.gz
```

Let us break down what this command does:

1. `docker run --rm` -- Start a temporary container that auto-removes when done
2. `-v postgres-data:/source` -- Mount the volume we want to back up to `/source`
3. `-v $(pwd):/backup` -- Mount the current directory on our host to `/backup`
4. `alpine` -- Use a tiny Alpine image (we just need the tar command)
5. `tar czf /backup/postgres-backup.tar.gz -C /source .` -- Create a compressed archive of everything in `/source` and save it to `/backup`

### Method 2: Restore From Backup

```bash
# Create a new volume
$ docker volume create postgres-restored

# Restore the backup into the new volume
$ docker run --rm \
  -v postgres-restored:/target \
  -v $(pwd):/backup \
  alpine \
  sh -c "cd /target && tar xzf /backup/postgres-backup.tar.gz"

# Use the restored volume with a new container
$ docker run -d \
  --name restored-db \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  -v postgres-restored:/var/lib/postgresql/data \
  postgres:16-alpine
```

### Backup Flow Diagram

```
+--------------------------------------------------+
|    Volume Backup and Restore Flow                |
+--------------------------------------------------+
|                                                  |
|    BACKUP:                                       |
|    postgres-data volume                          |
|         |                                        |
|         v                                        |
|    [temp container reads volume]                 |
|         |                                        |
|         v                                        |
|    tar czf backup.tar.gz                         |
|         |                                        |
|         v                                        |
|    Host: ./backup.tar.gz                         |
|                                                  |
|    RESTORE:                                      |
|    Host: ./backup.tar.gz                         |
|         |                                        |
|         v                                        |
|    [temp container writes to new volume]         |
|         |                                        |
|         v                                        |
|    postgres-restored volume                      |
|         |                                        |
|         v                                        |
|    New container uses restored volume            |
|                                                  |
+--------------------------------------------------+
```

---

## Read-Only Volumes

You can mount a volume as read-only by adding `:ro` to the mount:

```bash
# Mount config as read-only
$ docker run -d \
  -v app-config:/app/config:ro \
  --name my-app \
  my-app
```

The container can read files in `/app/config` but cannot modify them. Any attempt to write will fail:

```bash
$ docker exec my-app touch /app/config/test.txt
touch: /app/config/test.txt: Read-only file system
```

### When to Use Read-Only Mounts

```
+--------------------------------------------------+
|    Read-Only Mount Use Cases                     |
+--------------------------------------------------+
|                                                  |
|    Configuration files:                          |
|    -v ./nginx.conf:/etc/nginx/nginx.conf:ro      |
|    (App can read config but not modify it)       |
|                                                  |
|    SSL certificates:                             |
|    -v certs:/etc/ssl/certs:ro                    |
|    (App can use certs but not change them)       |
|                                                  |
|    Static assets:                                |
|    -v static-files:/app/public:ro                |
|    (Web server serves files but cannot alter)    |
|                                                  |
|    Source code (CI/CD):                          |
|    -v $(pwd):/app:ro                             |
|    (Build tools read code but cannot modify)     |
|                                                  |
+--------------------------------------------------+
```

---

## Volume Cleanup

Volumes persist even after all containers using them are removed. Over time, unused volumes can accumulate and waste disk space.

### Removing a Specific Volume

```bash
# Remove a volume (must not be in use by any container)
$ docker volume rm my-data
my-data

# Try to remove a volume that is in use
$ docker volume rm postgres-data
Error: volume is in use

# You must stop and remove the container first
$ docker stop postgres-new && docker rm postgres-new
$ docker volume rm postgres-data
postgres-data
```

### Removing All Unused Volumes

```bash
$ docker volume prune
WARNING! This will remove anonymous local volumes not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Volumes:
abc123def456
ghi789jkl012

Total reclaimed space: 256.3MB
```

**Warning:** `docker volume prune` deletes unused volumes permanently. Make sure you have backed up any data you need before running this command.

### Listing All Volumes

```bash
$ docker volume ls
DRIVER    VOLUME NAME
local     postgres-data
local     postgres-restored
local     demo-data
local     auto-volume

# Filter for specific volumes
$ docker volume ls --filter "name=postgres"
DRIVER    VOLUME NAME
local     postgres-data
local     postgres-restored
```

---

## Quick Reference: Volume Commands

```
+--------------------------------------------------+
|    Volume Commands                               |
+--------------------------------------------------+
|                                                  |
|    CREATE:                                       |
|    docker volume create NAME                     |
|                                                  |
|    LIST:                                         |
|    docker volume ls                              |
|                                                  |
|    INSPECT:                                      |
|    docker volume inspect NAME                    |
|                                                  |
|    REMOVE:                                       |
|    docker volume rm NAME                         |
|                                                  |
|    REMOVE ALL UNUSED:                            |
|    docker volume prune                           |
|                                                  |
|    USE WITH CONTAINER:                           |
|    docker run -v NAME:/path image                |
|    docker run -v NAME:/path:ro image (read-only) |
|    docker run -v /host:/path image (bind mount)  |
|    docker run --tmpfs /path image (memory only)  |
|                                                  |
+--------------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Forgetting to Use a Volume for Database Containers

```bash
# BAD: No volume -- data is lost when container is removed
$ docker run -d -e POSTGRES_PASSWORD=pass postgres:16-alpine

# GOOD: Volume preserves data
$ docker run -d -e POSTGRES_PASSWORD=pass \
  -v pgdata:/var/lib/postgresql/data postgres:16-alpine
```

### Mistake 2: Using a Bind Mount When You Need a Volume

```bash
# BAD for production: bind mount depends on host path
$ docker run -v /home/user/data:/data my-app

# GOOD for production: named volume is portable
$ docker run -v app-data:/data my-app
```

Bind mounts are great for development (live code editing) but volumes are better for production because they are managed by Docker and do not depend on a specific host directory.

### Mistake 3: Not Backing Up Volumes Before Removing Them

```bash
# DANGEROUS: Are you sure there is nothing important in these volumes?
$ docker volume prune -f

# SAFER: List volumes first, back up important ones, then prune
$ docker volume ls
$ docker run --rm -v important-data:/source -v $(pwd):/backup alpine \
    tar czf /backup/important-backup.tar.gz -C /source .
$ docker volume prune
```

### Mistake 4: Mounting Over Important Container Directories

```bash
# BAD: This replaces the entire /app directory, including node_modules!
$ docker run -v $(pwd):/app my-node-app
# The container's /app/node_modules is gone because the bind mount replaced it

# SOLUTION: Use an anonymous volume for node_modules
$ docker run \
  -v $(pwd):/app \
  -v /app/node_modules \
  my-node-app
```

The second `-v /app/node_modules` (without a colon) creates an anonymous volume for `node_modules` inside the container, preventing the bind mount from overwriting it.

### Mistake 5: Confusing Volume Names with Host Paths

```bash
# This creates a VOLUME named "mydata"
$ docker run -v mydata:/app/data alpine

# This creates a BIND MOUNT from ./mydata on your host
$ docker run -v ./mydata:/app/data alpine

# This creates a BIND MOUNT from /mydata on your host
$ docker run -v /mydata:/app/data alpine
```

The rule: if the source contains a `/` (slash), it is a bind mount. If it is just a name (no slashes), it is a volume.

---

## Best Practices

1. **Always use volumes for database containers.** PostgreSQL, MySQL, MongoDB, Redis -- any database needs a volume to persist data.

2. **Use named volumes for production data.** Named volumes are portable and managed by Docker.

3. **Use bind mounts for development.** Bind mounts let you edit code on your host and see changes immediately in the container.

4. **Back up volumes regularly.** Use the tar-based backup method shown in this chapter.

5. **Use read-only mounts** for configuration files and certificates that the container should not modify.

6. **Clean up unused volumes** periodically with `docker volume prune` to free disk space.

7. **Know your database's data directory.** Check the image documentation to know where to mount the volume.

8. **Do not store secrets in volumes.** Use Docker secrets or environment variables for sensitive data.

---

## Quick Summary

Containers are ephemeral -- their writable layer is deleted when they are removed. Docker provides three storage options: volumes (managed by Docker, best for production), bind mounts (map host directories, best for development), and tmpfs mounts (memory-only, for temporary sensitive data). Named volumes persist data beyond the lifetime of any container. Database containers should always use volumes. Volumes can be backed up by mounting them in a temporary container and creating a tar archive.

---

## Key Points

- Container data is lost when the container is removed (ephemeral filesystem)
- Docker volumes persist data independently of containers
- Three storage types: volumes (Docker-managed), bind mounts (host paths), tmpfs (memory)
- Create volumes with `docker volume create` or let Docker auto-create them
- Mount volumes with `-v volume_name:/container/path`
- Bind mounts use `-v /host/path:/container/path`
- Add `:ro` for read-only mounts
- Always use volumes for databases (PostgreSQL, MySQL, MongoDB)
- Back up volumes by mounting them in a temporary container and using tar
- Names without slashes are volumes; paths with slashes are bind mounts
- Clean up with `docker volume prune` (be careful -- this is permanent)

---

## Practice Questions

1. What happens to data inside a container when you run `docker rm`? Why does this happen?

2. What are the three types of Docker storage? When would you use each one?

3. You start a PostgreSQL container without a volume, create a table, insert data, and then remove and recreate the container. What happens to your data? How would you fix this?

4. What is the difference between a named volume and a bind mount? Give an example of when you would use each.

5. You mount a volume as read-only with `-v config:/app/config:ro`. What happens when the application tries to write a file to `/app/config`?

---

## Exercises

### Exercise 1: Volume Basics

1. Create a named volume called `exercise-data`
2. Start a container that mounts the volume at `/data`
3. Write a file to `/data/hello.txt` inside the container
4. Remove the container
5. Start a new container with the same volume
6. Verify the file is still there
7. Clean up: remove the container and the volume

### Exercise 2: Database Persistence

1. Create a volume called `mysql-data`
2. Start a MySQL container with the volume mounted at `/var/lib/mysql`
3. Create a database and a table with some data
4. Stop and remove the container
5. Start a new MySQL container with the same volume
6. Verify your database, table, and data are still intact

### Exercise 3: Backup and Restore

1. Create a volume and populate it with several files using a container
2. Back up the volume to a tar.gz file on your host
3. Remove the original volume
4. Create a new volume and restore the backup into it
5. Verify all files are present in the restored volume

---

## What Is Next?

You now understand how to persist data in Docker using volumes and bind mounts. This is a fundamental skill for running stateful applications like databases. In the next chapter, we will explore Docker networking -- how containers communicate with each other and the outside world. You will learn how to connect a web application container to a database container, creating multi-container applications.
