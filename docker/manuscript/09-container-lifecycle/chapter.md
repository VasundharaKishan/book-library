# Chapter 9: The Container Lifecycle

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand the complete container lifecycle and all possible states
- Create containers without starting them using `docker create`
- Start, stop, restart, pause, and unpause containers
- Remove containers and clean up resources
- View real-time logs with `docker logs -f`
- Execute commands inside running containers with `docker exec`
- Attach to a running container's process with `docker attach`
- Copy files between your computer and containers with `docker cp`
- Monitor container resource usage with `docker stats`
- View running processes inside containers with `docker top`

## Why This Chapter Matters

So far, you have been using `docker run` to create and start containers, and `docker stop` to shut them down. But containers have a much richer lifecycle than just "running" and "stopped."

**Real-life analogy:** Think of a container like a car. You do not just start it and park it. You can idle it, pause it at a red light, turn off the engine while keeping the car in place, and eventually sell it for scrap. Understanding all these states gives you full control over your containers.

In production, you need to debug containers that are misbehaving, check their logs, copy files in and out, and monitor their resource usage. This chapter teaches you every tool you need for day-to-day container management.

---

## Container States

A Docker container can be in one of several states. Here is the complete lifecycle:

```
+--------------------------------------------------+
|           Container Lifecycle Diagram             |
+--------------------------------------------------+
|                                                   |
|                docker create                      |
|                     |                             |
|                     v                             |
|               +-----------+                       |
|               | CREATED   |                       |
|               +-----------+                       |
|                     |                             |
|               docker start                        |
|                     |                             |
|                     v                             |
|               +-----------+    docker pause       |
|          +--->| RUNNING   |----------------+      |
|          |    +-----------+                |      |
|          |       |    |                    v      |
|          |       |    |              +-----------+|
|          |       |    |              | PAUSED    ||
|          |       |    |              +-----------+|
|          |       |    |                    |      |
|          |       |    |           docker unpause  |
|          |       |    |                    |      |
|          |       |    +<-------------------+      |
|          |       |                                |
|    docker|  docker stop                           |
|  restart |  (or app exits)                        |
|          |       |                                |
|          |       v                                |
|          |  +-----------+                         |
|          +--| STOPPED   |                         |
|             +-----------+                         |
|                  |                                |
|             docker rm                             |
|                  |                                |
|                  v                                |
|             +-----------+                         |
|             | REMOVED   |                         |
|             +-----------+                         |
|                                                   |
+--------------------------------------------------+
```

### State Descriptions

```
+-------------+------------------------------------------------+
| State       | Description                                    |
+-------------+------------------------------------------------+
| Created     | Container exists but has never been started.    |
|             | Like a car that has been built but never       |
|             | had the engine turned on.                      |
+-------------+------------------------------------------------+
| Running     | Container is actively executing its process.    |
|             | Like a car with the engine running.             |
+-------------+------------------------------------------------+
| Paused      | Container's processes are suspended (frozen).   |
|             | Like pressing pause on a video. Everything     |
|             | freezes but nothing is lost.                   |
+-------------+------------------------------------------------+
| Stopped     | Container's main process has exited. The        |
|             | container still exists with all its data.       |
|             | Like a car with the engine turned off but      |
|             | still parked in the garage.                    |
+-------------+------------------------------------------------+
| Removed     | Container has been deleted. It no longer        |
|             | exists. Like selling a car for scrap.          |
+-------------+------------------------------------------------+
```

---

## docker create: Creating Without Starting

`docker create` creates a new container but does not start it. The container sits in the "Created" state.

**Real-life analogy:** It is like setting up a tent at a campsite but not going inside yet. The tent is there, ready to be used, but nobody is in it.

### Syntax

```bash
$ docker create [options] image [command]
```

### Example

```bash
# Create a container without starting it
$ docker create --name my-web -p 8080:80 nginx:alpine
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6

# Check its status
$ docker ps -a --filter "name=my-web"
CONTAINER ID   IMAGE          STATUS    NAMES
a1b2c3d4e5f6   nginx:alpine   Created   my-web
```

Notice the status says "Created," not "Up."

### When to Use docker create

- When you want to set up a container in advance and start it later
- When you need to inspect a container's configuration before running it
- When building automation scripts that prepare containers first

---

## docker start: Starting a Container

`docker start` starts a container that is in the "Created" or "Stopped" state.

### Syntax

```bash
$ docker start [options] container_name_or_id
```

### Example

```bash
# Start the container we created above
$ docker start my-web
my-web

# Verify it is running
$ docker ps
CONTAINER ID   IMAGE          STATUS          NAMES
a1b2c3d4e5f6   nginx:alpine   Up 3 seconds   my-web
```

### Start with Attached Output

By default, `docker start` runs in the background. To see the output:

```bash
# Start and attach to see output (like docker run without -d)
$ docker start -a my-web
/docker-entrypoint.sh: Configuration complete; ready for start up
```

The `-a` flag attaches your terminal to the container's output, so you can see what it prints.

---

## docker stop: Stopping a Container Gracefully

`docker stop` sends a **SIGTERM** signal to the main process in the container, giving it time to shut down gracefully. If the process does not stop within 10 seconds (by default), Docker sends a **SIGKILL** to force it to stop.

**Real-life analogy:** `docker stop` is like telling someone "Please finish what you are doing and leave the room." You give them time to clean up. If they do not leave within 10 seconds, security escorts them out.

### Syntax

```bash
$ docker stop [options] container_name_or_id
```

### Examples

```bash
# Stop a container (waits up to 10 seconds)
$ docker stop my-web
my-web

# Stop with a custom timeout (wait up to 30 seconds)
$ docker stop -t 30 my-web
my-web

# Stop multiple containers at once
$ docker stop web-1 web-2 web-3
web-1
web-2
web-3
```

### What Happens During Stop

```
+--------------------------------------------------+
|    What docker stop Does                         |
+--------------------------------------------------+
|                                                  |
|    1. Docker sends SIGTERM to the main process   |
|       "Please shut down gracefully"              |
|                                                  |
|    2. Application receives the signal            |
|       - Closes database connections              |
|       - Finishes processing current requests     |
|       - Saves state if needed                    |
|       - Exits cleanly                            |
|                                                  |
|    3. If still running after timeout (10s):      |
|       Docker sends SIGKILL                       |
|       "You are being forced to stop NOW"         |
|                                                  |
+--------------------------------------------------+
```

### docker stop vs docker kill

```bash
# docker stop: graceful shutdown (SIGTERM, then SIGKILL after timeout)
$ docker stop my-web

# docker kill: immediate shutdown (SIGKILL, no grace period)
$ docker kill my-web
```

Use `docker stop` in normal situations. Use `docker kill` only when a container is unresponsive and will not stop gracefully.

---

## docker restart: Stop and Start in One Step

`docker restart` stops a running container and immediately starts it again.

**Real-life analogy:** It is like turning your computer off and back on again. The classic "have you tried restarting it?" fix.

### Syntax

```bash
$ docker restart [options] container_name_or_id
```

### Examples

```bash
# Restart a container
$ docker restart my-web
my-web

# Restart with a custom stop timeout
$ docker restart -t 5 my-web
my-web
```

### What Happens During Restart

```
+--------------------------------------------------+
|    Restart Process                               |
+--------------------------------------------------+
|                                                  |
|    RUNNING -----> STOPPED -----> RUNNING         |
|              stop           start                |
|                                                  |
|    1. Send SIGTERM (graceful stop)               |
|    2. Wait for process to exit                   |
|    3. Start the container again                  |
|    4. Container gets a new process               |
|       (but keeps the same filesystem)            |
|                                                  |
+--------------------------------------------------+
```

**Important:** Restarting a container does NOT reset its filesystem. Any files created or modified inside the container are still there after the restart. However, the process starts fresh (new PID, reset memory).

---

## docker pause and docker unpause: Freezing a Container

`docker pause` freezes all processes in a container. The container is still in memory, but nothing executes. `docker unpause` resumes the processes exactly where they left off.

**Real-life analogy:** Pause is like pressing the pause button on a video game. The game freezes completely but nothing is lost. When you unpause, everything continues exactly where it was.

### Syntax

```bash
$ docker pause container_name_or_id
$ docker unpause container_name_or_id
```

### Example

```bash
# Start a container
$ docker run -d --name my-web -p 8080:80 nginx:alpine
a1b2c3d4...

# Verify it is running
$ curl http://localhost:8080
<!DOCTYPE html>...  (nginx welcome page)

# Pause the container
$ docker pause my-web
my-web

# Check the status
$ docker ps
CONTAINER ID   IMAGE          STATUS                NAMES
a1b2c3d4       nginx:alpine   Up 1 min (Paused)     my-web

# Try to access the website (it will hang/timeout)
$ curl --max-time 3 http://localhost:8080
curl: (28) Operation timed out

# Unpause the container
$ docker unpause my-web
my-web

# It works again!
$ curl http://localhost:8080
<!DOCTYPE html>...  (nginx welcome page)
```

### When to Use Pause

- Temporarily stop a container from using CPU without stopping it
- During backup operations where you need a consistent snapshot
- When debugging and you want to freeze state at a specific point

### Pause vs Stop

```
+--------------------------------------------------+
|    Pause vs Stop Comparison                      |
+--------------------------------------------------+
|                                                  |
|    Feature          Pause         Stop           |
|    ---------------- ------------- -------------- |
|    Process state    Frozen        Terminated     |
|    Memory           Preserved     Released       |
|    Resume speed     Instant       Needs restart  |
|    Network          Frozen        Closed         |
|    Filesystem       Unchanged     Unchanged      |
|    Use case         Temporary     Longer term    |
|                     freeze        shutdown       |
|                                                  |
+--------------------------------------------------+
```

---

## docker rm: Removing Containers

`docker rm` permanently deletes a container. This is irreversible -- once removed, the container and any data stored in its writable layer are gone forever.

**Real-life analogy:** `docker rm` is like throwing away a cardboard box. Once it is in the trash and the garbage truck takes it, you cannot get it back.

### Syntax

```bash
$ docker rm [options] container_name_or_id
```

### Examples

```bash
# Remove a stopped container
$ docker rm my-web
my-web

# Try to remove a running container (this fails!)
$ docker rm my-web
Error response from daemon: cannot remove container: container is running

# Force remove a running container (stops it first)
$ docker rm -f my-web
my-web

# Remove multiple containers
$ docker rm web-1 web-2 web-3

# Remove all stopped containers
$ docker container prune
WARNING! This will remove all stopped containers.
Are you sure you want to continue? [y/N] y
Deleted Containers:
a1b2c3d4e5f6
b2c3d4e5f6g7
Total reclaimed space: 25.3MB
```

### The --rm Flag: Auto-Remove

You can tell Docker to automatically remove a container when it stops:

```bash
# Container is automatically removed when it exits
$ docker run --rm --name temp-web -p 8080:80 nginx:alpine

# When you stop it, it is automatically removed
$ docker stop temp-web
# No need to docker rm -- it is already gone!

$ docker ps -a | grep temp-web
# (nothing -- the container was auto-removed)
```

This is very useful for temporary containers that you do not need to keep.

---

## docker logs: Viewing Container Output

`docker logs` shows you what a container has been printing to its standard output (stdout) and standard error (stderr). This is essential for debugging.

**Real-life analogy:** `docker logs` is like checking a security camera recording. You can see what happened inside the container, even if you were not watching at the time.

### Syntax

```bash
$ docker logs [options] container_name_or_id
```

### Basic Examples

```bash
# View all logs
$ docker logs my-web

# View the last 20 lines
$ docker logs --tail 20 my-web

# View logs with timestamps
$ docker logs -t my-web
2024-01-15T10:30:00.123Z  Server running on port 3000
2024-01-15T10:30:05.456Z  GET / 200 12ms
2024-01-15T10:30:10.789Z  GET /api/users 200 8ms
```

### Following Logs in Real Time

The `-f` flag (follow) streams logs in real time, like `tail -f`:

```bash
# Follow logs in real time (press Ctrl+C to stop)
$ docker logs -f my-web
Server running on port 3000
GET / 200 12ms
GET /api/users 200 8ms
... (new logs appear as they happen) ...
```

### Combining Options

```bash
# Show the last 10 lines and follow new ones
$ docker logs --tail 10 -f my-web

# Show logs since a specific time
$ docker logs --since 2024-01-15T10:00:00 my-web

# Show logs from the last 5 minutes
$ docker logs --since 5m my-web

# Show logs with timestamps, last 5 lines, following
$ docker logs -t --tail 5 -f my-web
```

### Practical Debugging Example

```bash
# Your application is crashing. Let us investigate:

# Step 1: Check if the container is running
$ docker ps -a --filter "name=my-app"
CONTAINER ID   IMAGE    STATUS                     NAMES
a1b2c3d4       my-app   Exited (1) 2 minutes ago   my-app

# Status "Exited (1)" means the app crashed (exit code 1)

# Step 2: Check the logs to see what happened
$ docker logs my-app
Server starting on port 3000
Connected to database
Error: Cannot read properties of undefined (reading 'id')
    at /app/src/routes/users.js:15:28
    at Layer.handle [as handle_request] (/app/node_modules/express/lib/router/layer.js:95:5)

# Now you can see the exact error and file/line number!
```

---

## docker exec: Running Commands Inside a Container

`docker exec` lets you run a command inside a running container. This is one of the most frequently used Docker commands for debugging and administration.

**Real-life analogy:** `docker exec` is like reaching through a window into a room and pressing buttons. The room (container) is already there and running. You are just interacting with it from the outside.

### Syntax

```bash
$ docker exec [options] container command [arguments]
```

### Common Examples

```bash
# Run a simple command
$ docker exec my-web ls /app
node_modules
package.json
server.js

# Check the current user
$ docker exec my-web whoami
node

# Check environment variables
$ docker exec my-web env
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
NODE_VERSION=18.19.0
...

# Check running processes
$ docker exec my-web ps aux
PID   USER     COMMAND
    1 node     node server.js
   25 node     ps aux
```

### Interactive Shell Access

The most common use of `docker exec` is to open an interactive shell inside the container:

```bash
# Open a bash shell inside the container
$ docker exec -it my-web /bin/bash
root@a1b2c3d4:/app#

# If the container does not have bash (like Alpine), use sh
$ docker exec -it my-web /bin/sh
/app $
```

Breaking down the flags:

- `-i` (interactive) -- Keeps stdin open so you can type commands
- `-t` (tty) -- Allocates a terminal so you see a prompt and can use terminal features

Together, `-it` gives you an interactive terminal session inside the container.

### Inside the Container

Once inside, you can explore:

```bash
# You are now INSIDE the container
/app $ ls -la
total 32
drwxr-xr-x  1 node node 4096 Jan 15 10:30 .
drwxr-xr-x  1 root root 4096 Jan 15 10:30 ..
drwxr-xr-x 50 node node 4096 Jan 15 10:30 node_modules
-rw-r--r--  1 node node  320 Jan 15 10:30 package.json
-rw-r--r--  1 node node  580 Jan 15 10:30 server.js

# Check memory usage
/app $ free -m
              total       used       free
Mem:           7972       1234       5678

# Check disk usage
/app $ df -h
Filesystem      Size  Used Avail Use% Mounted on
overlay         59G   12G    44G  22% /

# Check network connectivity
/app $ wget -q -O- http://localhost:3000/health
{"status":"healthy"}

# Exit the container shell
/app $ exit
```

### Running Commands as a Different User

```bash
# Run as root (even if the container normally runs as non-root)
$ docker exec -u root my-web whoami
root

# Run as a specific user
$ docker exec -u node my-web whoami
node
```

### Setting Environment Variables

```bash
# Run a command with an additional environment variable
$ docker exec -e DEBUG=true my-web env | grep DEBUG
DEBUG=true
```

---

## docker attach: Connecting to the Main Process

`docker attach` connects your terminal to the container's main process (PID 1). This is different from `docker exec` because you are connecting to the existing process, not starting a new one.

**Real-life analogy:** `docker exec -it bash` is like opening a new window into a room. `docker attach` is like picking up an already-connected phone call.

### Syntax

```bash
$ docker attach [options] container_name_or_id
```

### Example

```bash
# Start a container
$ docker run -d --name my-web -p 3000:3000 node-api:1.0

# Attach to it (you will see its output)
$ docker attach my-web
Server running on port 3000
GET / 200 12ms
GET /api/users 200 8ms
```

### Important Warning About docker attach

When you press `Ctrl+C` while attached, it sends the signal to the container's main process. This can **stop the container**:

```bash
# Attached to my-web
$ docker attach my-web
Server running on port 3000
^C   # <-- Pressing Ctrl+C STOPS the container!
```

To detach without stopping the container, use the key sequence `Ctrl+P, Ctrl+Q`:

```bash
# Detach without stopping
$ docker attach my-web
Server running on port 3000
# Press Ctrl+P, then Ctrl+Q
read escape sequence
$  # Back to your terminal, container still running
```

### When to Use attach vs exec

```
+--------------------------------------------------+
|    attach vs exec                                |
+--------------------------------------------------+
|                                                  |
|    Use docker attach when:                       |
|    - You want to see the main process output     |
|    - You want to interact with the main process  |
|    - You are running an interactive app          |
|                                                  |
|    Use docker exec when:                         |
|    - You want to run a NEW command               |
|    - You want to debug (open a shell)            |
|    - You want to inspect files or processes      |
|    - You do NOT want to risk stopping the        |
|      container (safer option)                    |
|                                                  |
+--------------------------------------------------+
```

In practice, `docker exec` is used much more frequently than `docker attach`.

---

## docker cp: Copying Files Between Host and Container

`docker cp` copies files and directories between your computer (the host) and a container. The container can be running or stopped.

**Real-life analogy:** `docker cp` is like passing items through a window. You can hand things in (host to container) or take things out (container to host).

### Syntax

```bash
# Copy from host to container
$ docker cp local_path container:container_path

# Copy from container to host
$ docker cp container:container_path local_path
```

### Examples: Host to Container

```bash
# Copy a file into a running container
$ docker cp config.json my-web:/app/config.json

# Copy a directory into a container
$ docker cp ./logs my-web:/app/logs

# Verify the file was copied
$ docker exec my-web ls /app/config.json
/app/config.json
```

### Examples: Container to Host

```bash
# Copy a log file from the container to your computer
$ docker cp my-web:/app/logs/error.log ./error.log

# Copy the entire app directory from the container
$ docker cp my-web:/app ./container-app

# Copy from a stopped container (this also works!)
$ docker stop my-web
$ docker cp my-web:/app/data.db ./backup-data.db
```

### Practical Use Cases

```bash
# Use Case 1: Quick config update without rebuilding
$ docker cp new-nginx.conf my-web:/etc/nginx/nginx.conf
$ docker restart my-web

# Use Case 2: Extract logs for analysis
$ docker cp my-web:/var/log/app.log ./app.log

# Use Case 3: Debug a crash by copying the core dump
$ docker cp crashed-app:/app/core.dump ./core.dump

# Use Case 4: Add test data to a running container
$ docker cp test-data.json my-web:/app/data/test-data.json
```

**Warning:** Copying files into a container is a temporary fix. The changes will be lost when the container is removed. For permanent changes, update your Dockerfile and rebuild.

---

## docker stats: Monitoring Resource Usage

`docker stats` shows real-time resource usage statistics for running containers, similar to the `top` command on Linux.

**Real-life analogy:** `docker stats` is like the dashboard in your car. It shows you how much fuel (CPU) you are using, the engine temperature (memory), and how fast you are going (network traffic).

### Syntax

```bash
$ docker stats [options] [container_names...]
```

### Example

```bash
$ docker stats
CONTAINER ID   NAME        CPU %   MEM USAGE / LIMIT     MEM %   NET I/O          BLOCK I/O
a1b2c3d4       node-api    0.15%   45.2MiB / 7.77GiB     0.57%   1.2kB / 648B     0B / 0B
b2c3d4e5       python-api  0.08%   62.1MiB / 7.77GiB     0.78%   1.1kB / 580B     0B / 0B
c3d4e5f6       java-api    0.52%   185MiB / 7.77GiB      2.32%   2.3kB / 1.1kB    4.1MB / 0B
```

### Understanding the Output

```
+--------------------------------------------------+
|    docker stats Columns Explained                |
+--------------------------------------------------+
|                                                  |
|    CONTAINER ID  Unique container identifier     |
|    NAME          Container name                  |
|    CPU %         CPU usage as a percentage       |
|    MEM USAGE     Current memory used             |
|    / LIMIT       Maximum memory allowed          |
|    MEM %         Memory usage as a percentage    |
|    NET I/O       Network data in / out           |
|    BLOCK I/O     Disk read / write               |
|                                                  |
+--------------------------------------------------+
```

### Monitor Specific Containers

```bash
# Monitor only specific containers
$ docker stats node-api python-api

# Show stats once (not streaming)
$ docker stats --no-stream
CONTAINER ID   NAME        CPU %   MEM USAGE / LIMIT     MEM %
a1b2c3d4       node-api    0.15%   45.2MiB / 7.77GiB     0.57%
b2c3d4e5       python-api  0.08%   62.1MiB / 7.77GiB     0.78%

# Custom format
$ docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
NAME          CPU %     MEM USAGE / LIMIT
node-api      0.15%     45.2MiB / 7.77GiB
python-api    0.08%     62.1MiB / 7.77GiB
```

### Comparing Resource Usage Across Languages

```
+--------------------------------------------------+
|    Resource Usage by Language                    |
+--------------------------------------------------+
|                                                  |
|    Application     Idle CPU  Idle Memory         |
|    -------------------------------------------- |
|    Node.js Express  ~0.1%    ~45 MB              |
|    Python Flask      ~0.1%    ~62 MB              |
|    Java Spring Boot  ~0.5%    ~185 MB             |
|                                                  |
|    Note: Java uses more memory because the JVM   |
|    pre-allocates memory for the heap.            |
|                                                  |
+--------------------------------------------------+
```

---

## docker top: Viewing Processes Inside a Container

`docker top` shows the running processes inside a container, similar to the `ps` command.

**Real-life analogy:** `docker top` is like looking through a window to see who is inside a room and what they are doing.

### Syntax

```bash
$ docker top container_name_or_id
```

### Example

```bash
# View processes in a Node.js container
$ docker top node-api
UID    PID    PPID   C   STIME   TTY   TIME       CMD
node   1234   1233   0   10:30   ?     00:00:02   node src/server.js

# View processes in a Python container (with gunicorn workers)
$ docker top python-api
UID      PID    PPID   C   STIME   TTY   TIME       CMD
appuser  2345   2344   0   10:31   ?     00:00:01   gunicorn: master [app.main:app]
appuser  2346   2345   0   10:31   ?     00:00:00   gunicorn: worker [app.main:app]
appuser  2347   2345   0   10:31   ?     00:00:00   gunicorn: worker [app.main:app]
appuser  2348   2345   0   10:31   ?     00:00:00   gunicorn: worker [app.main:app]
appuser  2349   2345   0   10:31   ?     00:00:00   gunicorn: worker [app.main:app]
```

### Using Custom ps Options

You can pass custom formatting options:

```bash
# Show specific fields
$ docker top my-web -o pid,user,%cpu,%mem,command
PID    USER    %CPU   %MEM   COMMAND
1234   node    0.1    0.5    node src/server.js
```

---

## Putting It All Together: A Debugging Session

Here is a realistic scenario that combines several commands:

```bash
# Scenario: Your web application is not responding to requests

# Step 1: Check if the container is running
$ docker ps -a --filter "name=my-app"
CONTAINER ID   IMAGE    STATUS        NAMES
a1b2c3d4       my-app   Up 2 hours    my-app

# It says "Up" but let us dig deeper

# Step 2: Check resource usage
$ docker stats --no-stream my-app
NAME     CPU %   MEM USAGE / LIMIT     MEM %
my-app   98.5%   750MiB / 1GiB         73.2%

# CPU is at 98.5%! Something is using too much CPU

# Step 3: Check what processes are running
$ docker top my-app
UID    PID    CMD
node   1234   node src/server.js
node   1235   node src/worker.js   # <-- suspicious!

# Step 4: Check the logs
$ docker logs --tail 50 my-app
...
[ERROR] Worker stuck in infinite loop processing job #4521
[WARN] Memory usage approaching limit
[ERROR] Worker stuck in infinite loop processing job #4521
...

# Step 5: Get a shell inside the container for investigation
$ docker exec -it my-app /bin/sh

/app $ ls -la src/worker.js
-rw-r--r-- 1 node node 2048 Jan 15 10:30 src/worker.js

/app $ cat src/worker.js | head -20
# (examine the file to find the bug)

/app $ exit

# Step 6: Copy the problematic file out for editing
$ docker cp my-app:/app/src/worker.js ./worker.js

# Step 7: Fix the file and copy it back
$ vim ./worker.js  # (fix the infinite loop)
$ docker cp ./worker.js my-app:/app/src/worker.js

# Step 8: Restart the container
$ docker restart my-app

# Step 9: Verify it is working
$ docker stats --no-stream my-app
NAME     CPU %   MEM USAGE / LIMIT     MEM %
my-app   0.2%    45MiB / 1GiB          4.4%

# CPU is back to normal!

# Step 10: Follow logs to confirm
$ docker logs -f --tail 10 my-app
Server running on port 3000
Worker processing job #4522 - completed
Worker processing job #4523 - completed
...
```

---

## Quick Reference: Container Management Commands

```
+--------------------------------------------------+
|    Container Lifecycle Commands                  |
+--------------------------------------------------+
|                                                  |
|    CREATE:                                       |
|    docker create    Create without starting      |
|    docker run       Create and start (combined)  |
|                                                  |
|    STATE CHANGES:                                |
|    docker start     Created/Stopped -> Running   |
|    docker stop      Running -> Stopped           |
|    docker restart   Stop then Start              |
|    docker pause     Running -> Paused            |
|    docker unpause   Paused -> Running            |
|    docker kill      Force stop immediately       |
|                                                  |
|    REMOVE:                                       |
|    docker rm        Delete a stopped container   |
|    docker rm -f     Force delete (even running)  |
|    docker prune     Delete ALL stopped containers|
|                                                  |
|    INSPECT:                                      |
|    docker logs      View container output        |
|    docker logs -f   Follow logs in real time     |
|    docker exec      Run command in container     |
|    docker attach    Connect to main process      |
|    docker cp        Copy files in/out            |
|    docker stats     Monitor resource usage       |
|    docker top       View running processes       |
|                                                  |
+--------------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Trying to Remove a Running Container

```bash
# This fails
$ docker rm my-web
Error: cannot remove running container

# Solution 1: Stop first, then remove
$ docker stop my-web && docker rm my-web

# Solution 2: Force remove
$ docker rm -f my-web
```

### Mistake 2: Pressing Ctrl+C in docker attach

```bash
# This STOPS the container!
$ docker attach my-web
^C  # Container stops!

# Instead, detach with Ctrl+P, Ctrl+Q
# Or use docker exec instead of attach
```

### Mistake 3: Forgetting --rm for Temporary Containers

```bash
# BAD: creates containers that pile up
$ docker run -d nginx:alpine
$ docker run -d nginx:alpine
$ docker run -d nginx:alpine
# Now you have 3 containers to clean up

# GOOD: auto-remove when done
$ docker run --rm -d nginx:alpine
```

### Mistake 4: Not Checking Logs When Something Fails

```bash
# Container keeps restarting? Check the logs!
$ docker logs my-app
Error: Cannot find module 'express'
# The issue is clear: express is not installed
```

### Mistake 5: Using docker attach Instead of docker exec

```bash
# docker attach connects to PID 1 -- can be dangerous
# docker exec creates a NEW process -- much safer

# PREFERRED for debugging:
$ docker exec -it my-web /bin/sh

# ONLY use attach when you specifically need to interact
# with the main process (rare)
```

---

## Best Practices

1. **Use `--rm` for temporary containers** to prevent a buildup of stopped containers that consume disk space.

2. **Use `docker exec` instead of `docker attach`** for debugging. It is safer and more flexible.

3. **Always check logs first** when debugging container issues. Most problems are visible in the logs.

4. **Use `docker stats`** to monitor resource usage and catch runaway processes.

5. **Name your containers** with `--name` so you can refer to them easily instead of using container IDs.

6. **Use `docker logs --tail N -f`** to follow recent logs without seeing the entire log history.

7. **Stop containers gracefully** with `docker stop` before removing them. Only use `docker kill` or `docker rm -f` as a last resort.

8. **Regularly prune stopped containers** with `docker container prune` to free up disk space.

---

## Quick Summary

Containers have a complete lifecycle with five states: Created, Running, Paused, Stopped, and Removed. Docker provides commands to transition between each state. For debugging, `docker logs` shows output, `docker exec` lets you run commands inside containers, and `docker stats` monitors resource usage. `docker cp` copies files between your computer and containers. Understanding these commands is essential for managing containers in both development and production.

---

## Key Points

- Containers have five states: Created, Running, Paused, Stopped, Removed
- `docker create` makes a container without starting it; `docker run` does both
- `docker stop` sends SIGTERM for graceful shutdown; `docker kill` forces immediate stop
- `docker pause` freezes processes in memory; `docker unpause` resumes them
- `docker logs -f` follows container output in real time
- `docker exec -it container /bin/sh` opens an interactive shell for debugging
- `docker attach` connects to PID 1 (be careful with Ctrl+C)
- `docker cp` works in both directions and even on stopped containers
- `docker stats` shows CPU, memory, and network usage
- Use `--rm` for temporary containers to prevent clutter

---

## Practice Questions

1. What is the difference between `docker stop` and `docker kill`? When would you use each?

2. You need to look at a configuration file inside a running container. Which command would you use: `docker exec`, `docker attach`, or `docker cp`? Why?

3. A container shows "Up 2 hours" in `docker ps` but the application inside is not responding. How would you investigate the problem? List the commands you would use.

4. What is the difference between `docker pause` and `docker stop`? What happens to memory in each case?

5. You press Ctrl+C while running `docker attach my-web`. What happens? How can you detach without stopping the container?

---

## Exercises

### Exercise 1: Lifecycle Walk-Through

Walk through the complete container lifecycle:
1. Create a container with `docker create` (do not start it)
2. Start it with `docker start`
3. Pause it and verify it is paused with `docker ps`
4. Unpause it
5. Stop it
6. Start it again (restart from stopped state)
7. Remove it

### Exercise 2: Debug a Misbehaving Container

1. Run a container: `docker run -d --name debug-me nginx:alpine`
2. Use `docker exec` to get a shell inside the container
3. From inside the container, modify the nginx welcome page
4. From outside the container, use `docker cp` to copy the modified file to your computer
5. Check the container's resource usage with `docker stats`
6. View the container's processes with `docker top`

### Exercise 3: Log Analysis

1. Run a container with a Node.js or Python application
2. Make several requests to the application with curl
3. Use `docker logs --tail 5` to see the last 5 log entries
4. Use `docker logs --since 1m` to see logs from the last minute
5. Use `docker logs -f` to follow logs in real time while making more requests

---

## What Is Next?

Now that you understand the container lifecycle and know how to manage, debug, and monitor containers, the next chapter covers environment variables and configuration. You will learn how to pass configuration to your containers without hardcoding values in your Dockerfile -- a critical skill for running the same image in development, staging, and production environments.
