# Appendix A: Docker Commands Cheat Sheet

## What You Will Learn

In this appendix, you will learn:

- Every Docker command organized by category
- What each command does in plain English
- Quick examples you can copy and paste
- The most common flags and options for each command

## Why This Chapter Matters

Think of this appendix as your toolbox label maker. When you are building a house, you do not memorize every tool. You learn where to find them. This cheat sheet works the same way. Keep it open while you work with Docker. Over time, the commands you use most will become second nature. For the rest, you will always know exactly where to look.

```
+-------------------------------------------------------+
|              YOUR DOCKER TOOLBOX                       |
|                                                        |
|  +-------------+  +-------------+  +-------------+    |
|  | Containers  |  |   Images    |  |   Volumes   |    |
|  | run, stop,  |  | build, pull |  | create, ls  |    |
|  | rm, logs... |  | push, tag.. |  | rm, prune.. |    |
|  +-------------+  +-------------+  +-------------+    |
|                                                        |
|  +-------------+  +-------------+  +-------------+    |
|  |  Networks   |  |   Compose   |  |   System    |    |
|  | create, ls  |  | up, down,   |  | info, prune |    |
|  | connect...  |  | ps, logs... |  | df, events  |    |
|  +-------------+  +-------------+  +-------------+    |
|                                                        |
|  +-------------+  +-------------+                      |
|  |   Swarm     |  |  kubectl    |                      |
|  | init, join  |  | get, apply  |                      |
|  | service...  |  | logs, exec  |                      |
|  +-------------+  +-------------+                      |
+-------------------------------------------------------+
```

---

## Container Commands

Containers are running instances of images. Think of images as recipes and containers as the actual dishes you cook from those recipes. These commands let you cook, serve, and clean up.

---

### docker run

**What it does:** Creates and starts a new container from an image.

Think of it as saying "take this recipe and cook a dish right now."

```bash
# Run a simple container
docker run hello-world
```

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

```bash
# Run in the background (detached mode) with a name
docker run -d --name my-web -p 8080:80 nginx
```

```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

```bash
# Run interactively with a terminal
docker run -it ubuntu bash
```

```
root@a1b2c3d4e5f6:/#
```

**Common flags:**

| Flag | What It Does |
|------|-------------|
| `-d` | Run in background (detached) |
| `-it` | Interactive mode with terminal |
| `--name` | Give the container a name |
| `-p 8080:80` | Map port 8080 on your machine to port 80 in the container |
| `-v /host:/container` | Mount a folder from your machine into the container |
| `-e KEY=VALUE` | Set an environment variable |
| `--rm` | Automatically remove container when it stops |
| `--network` | Connect to a specific network |
| `--restart` | Set restart policy (no, always, on-failure, unless-stopped) |

---

### docker ps

**What it does:** Lists running containers. Add `-a` to see all containers, including stopped ones.

Think of it as checking which dishes are currently being served.

```bash
# Show running containers
docker ps
```

```
CONTAINER ID   IMAGE   COMMAND                  CREATED          STATUS          PORTS                  NAMES
a1b2c3d4e5f6   nginx   "/docker-entrypoint.…"   5 minutes ago    Up 5 minutes    0.0.0.0:8080->80/tcp   my-web
```

```bash
# Show ALL containers (running and stopped)
docker ps -a
```

```
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS                     PORTS                  NAMES
a1b2c3d4e5f6   nginx         "/docker-entrypoint.…"   5 minutes ago    Up 5 minutes               0.0.0.0:8080->80/tcp   my-web
b2c3d4e5f6g7   hello-world   "/hello"                 10 minutes ago   Exited (0) 10 minutes ago                          hungry_tesla
```

**Common flags:**

| Flag | What It Does |
|------|-------------|
| `-a` | Show all containers (including stopped) |
| `-q` | Show only container IDs |
| `--filter` | Filter output (e.g., `--filter status=running`) |
| `--format` | Custom output format |

---

### docker stop

**What it does:** Gracefully stops a running container. It sends a polite "please shut down" signal, then waits 10 seconds before forcing it.

Think of it as asking a restaurant to close for the night — they finish serving current customers first.

```bash
# Stop a container by name
docker stop my-web
```

```
my-web
```

```bash
# Stop a container with a custom timeout (5 seconds)
docker stop -t 5 my-web
```

```
my-web
```

```bash
# Stop multiple containers at once
docker stop container1 container2 container3
```

---

### docker rm

**What it does:** Removes a stopped container. This is like washing the dish and putting it away — it is gone.

```bash
# Remove a stopped container
docker rm my-web
```

```
my-web
```

```bash
# Force remove a running container
docker rm -f my-web
```

```
my-web
```

```bash
# Remove all stopped containers
docker rm $(docker ps -aq -f status=exited)
```

**Common flags:**

| Flag | What It Does |
|------|-------------|
| `-f` | Force remove (even if running) |
| `-v` | Also remove associated volumes |

---

### docker logs

**What it does:** Shows the output (logs) from a container. Like reading the diary of what the container has been doing.

```bash
# Show all logs
docker logs my-web
```

```
/docker-entrypoint.sh: Configuration complete; ready for start up
2024-01-15 10:30:00 [notice] nginx/1.25.0
2024-01-15 10:30:00 [notice] start worker processes
```

```bash
# Follow logs in real time (like "tail -f")
docker logs -f my-web
```

```bash
# Show last 20 lines
docker logs --tail 20 my-web
```

```bash
# Show logs with timestamps
docker logs -t my-web
```

**Common flags:**

| Flag | What It Does |
|------|-------------|
| `-f` | Follow log output in real time |
| `--tail N` | Show only the last N lines |
| `-t` | Show timestamps |
| `--since` | Show logs since a timestamp (e.g., `--since 2h`) |

---

### docker exec

**What it does:** Runs a command inside a running container. Like reaching into a running machine to flip a switch.

```bash
# Open a shell inside a running container
docker exec -it my-web bash
```

```
root@a1b2c3d4e5f6:/#
```

```bash
# Run a single command
docker exec my-web cat /etc/nginx/nginx.conf
```

```bash
# Run a command as a different user
docker exec -u www-data my-web whoami
```

```
www-data
```

**Common flags:**

| Flag | What It Does |
|------|-------------|
| `-it` | Interactive mode with terminal |
| `-u` | Run as a specific user |
| `-w` | Set working directory |
| `-e` | Set environment variables |

---

### docker inspect

**What it does:** Shows detailed information about a container in JSON format. Like reading the full technical specification of a running machine.

```bash
# Inspect a container
docker inspect my-web
```

```json
[
    {
        "Id": "a1b2c3d4e5f6...",
        "State": {
            "Status": "running",
            "Running": true
        },
        "NetworkSettings": {
            "IPAddress": "172.17.0.2"
        }
    }
]
```

```bash
# Get just the IP address
docker inspect --format '{{.NetworkSettings.IPAddress}}' my-web
```

```
172.17.0.2
```

---

### docker stats

**What it does:** Shows live resource usage (CPU, memory, network) for containers. Like a heart rate monitor for your containers.

```bash
# Show stats for all running containers
docker stats
```

```
CONTAINER ID   NAME     CPU %   MEM USAGE / LIMIT     MEM %   NET I/O         BLOCK I/O    PIDS
a1b2c3d4e5f6   my-web   0.00%   3.5MiB / 7.77GiB     0.04%   1.2kB / 648B    0B / 0B      3
```

```bash
# Show stats for a specific container (one snapshot, no streaming)
docker stats --no-stream my-web
```

---

### docker top

**What it does:** Shows the processes running inside a container. Like peeking through a window to see who is working inside.

```bash
docker top my-web
```

```
UID    PID    PPID   C   STIME   TTY   TIME       CMD
root   1234   1233   0   10:30   ?     00:00:00   nginx: master process
www    1235   1234   0   10:30   ?     00:00:00   nginx: worker process
```

---

### docker cp

**What it does:** Copies files between your computer and a container. Like passing a note through a window.

```bash
# Copy a file FROM your computer TO a container
docker cp ./index.html my-web:/usr/share/nginx/html/index.html
```

```bash
# Copy a file FROM a container TO your computer
docker cp my-web:/var/log/nginx/access.log ./access.log
```

---

### docker rename

**What it does:** Renames a container. Simple as that.

```bash
docker rename my-web my-website
```

---

### docker wait

**What it does:** Blocks (waits) until a container stops, then prints the exit code. Useful in scripts where you need to know when something finishes.

```bash
docker wait my-web
```

```
0
```

The number `0` means the container exited successfully. Any other number means something went wrong.

---

### docker pause / docker unpause

**What it does:** Freezes all processes in a container (pause) and unfreezes them (unpause). Like pressing the pause button on a video — everything stops exactly where it is.

```bash
# Freeze the container
docker pause my-web

# Unfreeze the container
docker unpause my-web
```

---

### docker attach

**What it does:** Connects your terminal to a running container's main process. Unlike `exec`, this connects to the process that is already running, not a new one.

```bash
docker attach my-web
```

> **Warning:** Pressing `Ctrl+C` while attached will stop the container. Use `Ctrl+P` then `Ctrl+Q` to detach without stopping.

---

### docker diff

**What it does:** Shows what files have changed inside a container compared to its original image. Like comparing a messy room to how it looked when it was clean.

```bash
docker diff my-web
```

```
C /var
C /var/log
C /var/log/nginx
A /var/log/nginx/access.log
A /var/log/nginx/error.log
```

- `A` = Added
- `C` = Changed
- `D` = Deleted

---

### docker export

**What it does:** Exports a container's filesystem as a tar archive. Like packing everything in a container into a suitcase.

```bash
docker export my-web > my-web-backup.tar
```

> **Note:** This exports the filesystem only, not the image layers or metadata. For full image backup, use `docker save` instead.

---

### docker commit

**What it does:** Creates a new image from a container's current state. Like taking a snapshot of a messy room and saving it as the "new normal."

```bash
docker commit my-web my-custom-nginx:v1
```

```
sha256:a1b2c3d4e5f6...
```

> **Note:** In practice, use a Dockerfile instead of `commit`. Dockerfiles are repeatable and version-controlled. Think of `commit` as a quick-and-dirty photo, while a Dockerfile is a proper blueprint.

---

## Image Commands

Images are the blueprints (recipes) for containers. These commands let you create, share, and manage those blueprints.

```
+---------------------------------------------------+
|                   IMAGE LIFECYCLE                  |
|                                                    |
|   Build ──> Tag ──> Push ──> (Registry) ──> Pull   |
|     │                                        │     |
|     ▼                                        ▼     |
|   images ──> inspect ──> history            run    |
|     │                                              |
|     ▼                                              |
|   save/load (backup)    rmi/prune (cleanup)        |
+---------------------------------------------------+
```

---

### docker build

**What it does:** Builds a new image from a Dockerfile. Like following a recipe to create a blueprint.

```bash
# Build an image from the current directory
docker build -t my-app:1.0 .
```

```
[+] Building 15.2s (10/10) FINISHED
 => [1/5] FROM node:18-alpine
 => [2/5] WORKDIR /app
 => [3/5] COPY package*.json ./
 => [4/5] RUN npm install
 => [5/5] COPY . .
 => exporting to image
 => => naming to docker.io/library/my-app:1.0
```

```bash
# Build with a specific Dockerfile
docker build -t my-app:1.0 -f Dockerfile.prod .
```

```bash
# Build with build arguments
docker build --build-arg NODE_ENV=production -t my-app:1.0 .
```

**Common flags:**

| Flag | What It Does |
|------|-------------|
| `-t` | Tag (name) the image |
| `-f` | Specify a Dockerfile by name |
| `--build-arg` | Pass variables to the build |
| `--no-cache` | Build from scratch, ignore cache |
| `--target` | Build a specific stage in a multi-stage build |

---

### docker pull

**What it does:** Downloads an image from a registry (like Docker Hub). Like ordering a recipe book from a store.

```bash
docker pull nginx
```

```
Using default tag: latest
latest: Pulling from library/nginx
a1b2c3d4e5f6: Pull complete
g7h8i9j0k1l2: Pull complete
Digest: sha256:abc123...
Status: Downloaded newer image for nginx:latest
docker.io/library/nginx:latest
```

```bash
# Pull a specific version
docker pull nginx:1.25

# Pull from a different registry
docker pull ghcr.io/myorg/my-app:2.0
```

---

### docker push

**What it does:** Uploads an image to a registry. Like publishing your recipe book so others can use it.

```bash
# You must be logged in first
docker login

# Tag your image for the registry
docker tag my-app:1.0 myusername/my-app:1.0

# Push it
docker push myusername/my-app:1.0
```

```
The push refers to repository [docker.io/myusername/my-app]
a1b2c3d4e5f6: Pushed
g7h8i9j0k1l2: Pushed
1.0: digest: sha256:abc123... size: 1234
```

---

### docker images

**What it does:** Lists all images on your machine. Like looking at your shelf of recipe books.

```bash
docker images
```

```
REPOSITORY    TAG       IMAGE ID       CREATED         SIZE
my-app        1.0       a1b2c3d4e5f6   2 hours ago     175MB
nginx         latest    g7h8i9j0k1l2   2 weeks ago     187MB
node          18        m3n4o5p6q7r8   3 weeks ago     1.1GB
```

**Common flags:**

| Flag | What It Does |
|------|-------------|
| `-a` | Show all images (including intermediate) |
| `-q` | Show only image IDs |
| `--filter` | Filter output (e.g., `--filter dangling=true`) |

---

### docker rmi

**What it does:** Removes an image. Like throwing away a recipe book you no longer need.

```bash
# Remove by name
docker rmi my-app:1.0
```

```
Untagged: my-app:1.0
Deleted: sha256:a1b2c3d4e5f6...
```

```bash
# Force remove
docker rmi -f my-app:1.0

# Remove multiple images
docker rmi image1 image2 image3
```

---

### docker tag

**What it does:** Gives an image a new name (tag). Like putting a new label on an existing recipe book. The image itself does not change.

```bash
docker tag my-app:1.0 myusername/my-app:latest
docker tag my-app:1.0 myusername/my-app:1.0
```

---

### docker history

**What it does:** Shows the layers that make up an image. Like seeing the step-by-step history of how a recipe was created.

```bash
docker history my-app:1.0
```

```
IMAGE          CREATED        CREATED BY                                      SIZE
a1b2c3d4e5f6   2 hours ago    CMD ["node", "server.js"]                       0B
b2c3d4e5f6g7   2 hours ago    COPY . .                                        5.2MB
c3d4e5f6g7h8   2 hours ago    RUN npm install                                 45MB
d4e5f6g7h8i9   2 hours ago    COPY package*.json ./                           120kB
e5f6g7h8i9j0   2 hours ago    WORKDIR /app                                    0B
f6g7h8i9j0k1   3 weeks ago    /bin/sh -c #(nop) CMD ["node"]                  0B
```

---

### docker save

**What it does:** Saves an image to a tar file. Like making a backup copy of your recipe book.

```bash
docker save my-app:1.0 > my-app-backup.tar

# Or with gzip compression
docker save my-app:1.0 | gzip > my-app-backup.tar.gz
```

---

### docker load

**What it does:** Loads an image from a tar file. Like restoring a recipe book from a backup.

```bash
docker load < my-app-backup.tar
```

```
Loaded image: my-app:1.0
```

---

### docker image inspect

**What it does:** Shows detailed information about an image in JSON format.

```bash
docker image inspect nginx
```

```bash
# Get just the image size
docker image inspect --format '{{.Size}}' nginx
```

```
187234567
```

---

### docker image prune

**What it does:** Removes unused images (dangling images with no tag). Like cleaning out old recipe books you never use.

```bash
# Remove dangling images
docker image prune
```

```
WARNING! This will remove all dangling images.
Are you sure you want to continue? [y/N] y
Deleted Images:
deleted: sha256:a1b2c3d4e5f6...
Total reclaimed space: 234MB
```

```bash
# Remove ALL unused images (not just dangling)
docker image prune -a
```

---

## Volume Commands

Volumes are Docker's way of storing data that persists even when containers are deleted. Think of volumes as external hard drives you plug into your containers.

```
+-------------------------------------------+
|              VOLUMES                       |
|                                            |
|  Container A ──┐                           |
|                ├──> [my-data-volume]        |
|  Container B ──┘     (persists forever)    |
|                                            |
|  Container C ────> [logs-volume]           |
|                     (persists forever)     |
+-------------------------------------------+
```

---

### docker volume create

**What it does:** Creates a new named volume.

```bash
docker volume create my-data
```

```
my-data
```

```bash
# Use it when running a container
docker run -d --name db -v my-data:/var/lib/postgresql/data postgres
```

---

### docker volume ls

**What it does:** Lists all volumes.

```bash
docker volume ls
```

```
DRIVER    VOLUME NAME
local     my-data
local     logs-volume
local     db-backup
```

---

### docker volume inspect

**What it does:** Shows detailed information about a volume.

```bash
docker volume inspect my-data
```

```json
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

---

### docker volume rm

**What it does:** Removes a volume. The data inside is gone forever.

```bash
docker volume rm my-data
```

```
my-data
```

> **Warning:** This permanently deletes all data in the volume. Make sure no containers are using it.

---

### docker volume prune

**What it does:** Removes all volumes that are not currently attached to any container.

```bash
docker volume prune
```

```
WARNING! This will remove all local volumes not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Volumes:
old-data
unused-logs
Total reclaimed space: 1.2GB
```

---

## Network Commands

Networks let containers talk to each other. Think of networks as private phone lines between containers.

```
+--------------------------------------------------+
|           DOCKER NETWORKS                         |
|                                                   |
|  ┌─────────── my-network ──────────────┐          |
|  │                                      │         |
|  │  [web-app] ◄────► [database]         │         |
|  │      │                               │         |
|  │      ▼                               │         |
|  │  [cache]                             │         |
|  │                                      │         |
|  └──────────────────────────────────────┘          |
|                                                   |
|  ┌─────────── other-network ───────────┐          |
|  │  [monitoring] ◄───► [alerting]       │         |
|  └──────────────────────────────────────┘          |
+--------------------------------------------------+
```

---

### docker network create

**What it does:** Creates a new network.

```bash
docker network create my-network
```

```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

```bash
# Create a network with a specific subnet
docker network create --subnet 172.20.0.0/16 my-custom-network
```

---

### docker network ls

**What it does:** Lists all networks.

```bash
docker network ls
```

```
NETWORK ID     NAME          DRIVER    SCOPE
a1b2c3d4e5f6   bridge        bridge    local
g7h8i9j0k1l2   host          host      local
m3n4o5p6q7r8   none          null      local
s9t0u1v2w3x4   my-network    bridge    local
```

---

### docker network inspect

**What it does:** Shows detailed information about a network, including which containers are connected.

```bash
docker network inspect my-network
```

```json
[
    {
        "Name": "my-network",
        "Driver": "bridge",
        "Containers": {
            "a1b2c3d4...": {
                "Name": "web-app",
                "IPv4Address": "172.18.0.2/16"
            },
            "e5f6g7h8...": {
                "Name": "database",
                "IPv4Address": "172.18.0.3/16"
            }
        }
    }
]
```

---

### docker network rm

**What it does:** Removes a network.

```bash
docker network rm my-network
```

---

### docker network connect

**What it does:** Connects a running container to a network. Like plugging a phone into a new phone line.

```bash
docker network connect my-network my-container
```

---

### docker network disconnect

**What it does:** Disconnects a container from a network.

```bash
docker network disconnect my-network my-container
```

---

### docker network prune

**What it does:** Removes all networks that no container is using.

```bash
docker network prune
```

```
WARNING! This will remove all custom networks not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Networks:
old-network
test-network
```

---

## Docker Compose Commands

Docker Compose lets you define and run multi-container applications with a single YAML file. Think of it as an orchestra conductor — one person (one command) coordinates many musicians (containers).

```
+---------------------------------------------------+
|         docker-compose.yml                         |
|                                                    |
|   services:                                        |
|     web:        ──────>  [web container]           |
|     database:   ──────>  [db container]            |
|     cache:      ──────>  [redis container]         |
|                                                    |
|   One file controls everything!                    |
+---------------------------------------------------+
```

---

### docker compose up

**What it does:** Creates and starts all containers defined in your `docker-compose.yml`.

```bash
# Start everything
docker compose up

# Start in the background
docker compose up -d

# Rebuild images before starting
docker compose up --build

# Start only specific services
docker compose up -d web database
```

```
[+] Running 3/3
 ✔ Network myapp_default      Created
 ✔ Container myapp-database-1 Started
 ✔ Container myapp-web-1      Started
```

---

### docker compose down

**What it does:** Stops and removes all containers, networks created by `up`.

```bash
# Stop and remove containers
docker compose down

# Also remove volumes (careful — deletes data!)
docker compose down -v

# Also remove images
docker compose down --rmi all
```

```
[+] Running 3/3
 ✔ Container myapp-web-1      Removed
 ✔ Container myapp-database-1 Removed
 ✔ Network myapp_default      Removed
```

---

### docker compose ps

**What it does:** Lists containers managed by the current Compose file.

```bash
docker compose ps
```

```
NAME                 IMAGE      COMMAND                  SERVICE     STATUS          PORTS
myapp-web-1          nginx      "/docker-entrypoint.…"   web         Up 5 minutes    0.0.0.0:8080->80/tcp
myapp-database-1     postgres   "docker-entrypoint.s…"   database    Up 5 minutes    5432/tcp
```

---

### docker compose logs

**What it does:** Shows logs from all services or a specific service.

```bash
# All services
docker compose logs

# Specific service
docker compose logs web

# Follow in real time
docker compose logs -f web
```

---

### docker compose exec

**What it does:** Runs a command in a running service container.

```bash
# Open a shell in the web service
docker compose exec web bash

# Run a database query
docker compose exec database psql -U postgres -d mydb -c "SELECT * FROM users;"
```

---

### docker compose build

**What it does:** Builds (or rebuilds) images for services defined with a `build` section.

```bash
# Build all services
docker compose build

# Build a specific service
docker compose build web

# Build without cache
docker compose build --no-cache
```

---

### docker compose pull

**What it does:** Pulls the latest images for services defined with an `image` section.

```bash
docker compose pull
```

```
[+] Pulling 2/2
 ✔ database Pulled
 ✔ cache    Pulled
```

---

### docker compose restart

**What it does:** Restarts one or more services.

```bash
# Restart all services
docker compose restart

# Restart a specific service
docker compose restart web
```

---

### docker compose stop

**What it does:** Stops services without removing them. You can start them again later with `docker compose start`.

```bash
docker compose stop
```

---

### docker compose config

**What it does:** Validates and displays the final Compose configuration. Very useful for debugging.

```bash
docker compose config
```

This shows the fully resolved YAML with all variables substituted and defaults applied.

---

### docker compose top

**What it does:** Shows running processes for each service.

```bash
docker compose top
```

```
myapp-web-1
UID    PID    PPID   C   STIME   TTY   TIME       CMD
root   1234   1233   0   10:30   ?     00:00:00   nginx: master process

myapp-database-1
UID       PID    PPID   C   STIME   TTY   TIME       CMD
postgres  5678   5677   0   10:30   ?     00:00:01   postgres
```

---

## System Commands

These commands help you understand and manage Docker itself — the engine under the hood.

---

### docker info

**What it does:** Shows system-wide information about your Docker installation.

```bash
docker info
```

```
Client:
 Version:    24.0.7
Server:
 Containers: 5
  Running: 2
  Paused: 0
  Stopped: 3
 Images: 12
 Server Version: 24.0.7
 Storage Driver: overlay2
 Operating System: Ubuntu 22.04
 Total Memory: 7.77GiB
 CPUs: 4
```

---

### docker version

**What it does:** Shows the Docker client and server version.

```bash
docker version
```

```
Client:
 Version:           24.0.7
 API version:       1.43

Server:
 Engine:
  Version:          24.0.7
  API version:      1.43
```

---

### docker system df

**What it does:** Shows how much disk space Docker is using. Like checking how full your hard drive is.

```bash
docker system df
```

```
TYPE            TOTAL   ACTIVE   SIZE      RECLAIMABLE
Images          12      3        4.2GB     3.1GB (73%)
Containers      5       2        120MB     80MB (66%)
Local Volumes   4       2        500MB     200MB (40%)
Build Cache     0       0        0B        0B
```

```bash
# Show detailed breakdown
docker system df -v
```

---

### docker system prune

**What it does:** Removes all unused data — stopped containers, dangling images, unused networks, and build cache. The big cleanup button.

```bash
docker system prune
```

```
WARNING! This will remove:
  - all stopped containers
  - all networks not used by at least one container
  - all dangling images
  - all dangling build cache

Are you sure you want to continue? [y/N] y
Total reclaimed space: 2.3GB
```

```bash
# Also remove unused volumes (be very careful!)
docker system prune --volumes

# Remove everything unused, including tagged images
docker system prune -a
```

---

### docker events

**What it does:** Shows real-time events from the Docker daemon. Like watching a live security camera feed of everything Docker does.

```bash
docker events
```

```
2024-01-15T10:30:00.000000000Z container start a1b2c3d4...
2024-01-15T10:30:05.000000000Z container die b2c3d4e5...
2024-01-15T10:30:06.000000000Z network connect s9t0u1v2...
```

```bash
# Filter events by type
docker events --filter type=container

# Filter events since a specific time
docker events --since 1h
```

---

## Swarm Commands

Docker Swarm turns a group of Docker machines into a single cluster. Think of it as connecting multiple kitchens so they can cook together for a much bigger restaurant.

```
+---------------------------------------------------+
|              DOCKER SWARM CLUSTER                  |
|                                                    |
|  ┌──────────────┐   ┌──────────────┐              |
|  │  Manager     │   │  Worker      │              |
|  │  Node        │   │  Node 1      │              |
|  │              │   │              │              |
|  │ ┌──────────┐ │   │ ┌──────────┐ │              |
|  │ │ Service  │ │   │ │ Service  │ │              |
|  │ │ Replica  │ │   │ │ Replica  │ │              |
|  │ └──────────┘ │   │ └──────────┘ │              |
|  └──────────────┘   └──────────────┘              |
|                                                    |
|                     ┌──────────────┐              |
|                     │  Worker      │              |
|                     │  Node 2      │              |
|                     │              │              |
|                     │ ┌──────────┐ │              |
|                     │ │ Service  │ │              |
|                     │ │ Replica  │ │              |
|                     │ └──────────┘ │              |
|                     └──────────────┘              |
+---------------------------------------------------+
```

---

### docker swarm init

**What it does:** Initializes the current machine as a Swarm manager.

```bash
docker swarm init
```

```
Swarm initialized: current node is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-abc123... 192.168.1.100:2377
```

---

### docker swarm join

**What it does:** Joins a machine to an existing Swarm as a worker.

```bash
docker swarm join --token SWMTKN-1-abc123... 192.168.1.100:2377
```

```
This node joined a swarm as a worker.
```

---

### docker swarm leave

**What it does:** Removes the current machine from the Swarm.

```bash
docker swarm leave

# Force leave if it is a manager
docker swarm leave --force
```

---

### docker node

**What it does:** Manages nodes (machines) in the Swarm.

```bash
# List all nodes
docker node ls
```

```
ID             HOSTNAME       STATUS   AVAILABILITY   MANAGER STATUS
a1b2c3d4e5 *   manager-1      Ready    Active         Leader
f6g7h8i9j0     worker-1       Ready    Active
k1l2m3n4o5     worker-2       Ready    Active
```

```bash
# Inspect a node
docker node inspect worker-1

# Drain a node (stop scheduling new tasks on it)
docker node update --availability drain worker-1
```

---

### docker service

**What it does:** Manages services in the Swarm. A service is a definition of how to run containers across the cluster.

```bash
# Create a service with 3 replicas
docker service create --name web --replicas 3 -p 8080:80 nginx
```

```
a1b2c3d4e5f6g7h8i9j0
```

```bash
# List services
docker service ls
```

```
ID             NAME   MODE         REPLICAS   IMAGE
a1b2c3d4e5f6   web    replicated   3/3        nginx:latest
```

```bash
# Scale a service
docker service scale web=5

# See which nodes are running the service
docker service ps web

# Update a service
docker service update --image nginx:1.25 web

# Remove a service
docker service rm web
```

---

### docker stack

**What it does:** Manages stacks (multi-service applications) in the Swarm using Compose files.

```bash
# Deploy a stack from a Compose file
docker stack deploy -c docker-compose.yml myapp
```

```
Creating network myapp_default
Creating service myapp_web
Creating service myapp_database
```

```bash
# List stacks
docker stack ls

# List services in a stack
docker stack services myapp

# Remove a stack
docker stack rm myapp
```

---

## kubectl Quick Reference

kubectl is the command-line tool for Kubernetes. If Docker Swarm is a few kitchens working together, Kubernetes is an entire restaurant chain managed from a central headquarters.

```
+---------------------------------------------------+
|           KUBERNETES QUICK REFERENCE               |
|                                                    |
|   kubectl get      = "Show me what exists"         |
|   kubectl describe = "Tell me everything about it" |
|   kubectl apply    = "Make it happen"               |
|   kubectl delete   = "Remove it"                   |
|   kubectl logs     = "Show me the output"          |
|   kubectl exec     = "Run something inside"        |
|   kubectl scale    = "Change the count"            |
|   kubectl rollout  = "Manage updates"              |
+---------------------------------------------------+
```

---

### kubectl get

**What it does:** Lists resources. The most-used kubectl command.

```bash
# List all pods
kubectl get pods
```

```
NAME                     READY   STATUS    RESTARTS   AGE
web-app-7d4b8c9f-x2k9   1/1     Running   0          5m
web-app-7d4b8c9f-m3p7   1/1     Running   0          5m
database-5c6d7e8f-j4k2  1/1     Running   0          5m
```

```bash
# List services
kubectl get services

# List deployments
kubectl get deployments

# List everything
kubectl get all

# List pods with more detail
kubectl get pods -o wide

# List pods in all namespaces
kubectl get pods --all-namespaces
```

---

### kubectl describe

**What it does:** Shows detailed information about a resource. When something goes wrong, this is your best friend.

```bash
kubectl describe pod web-app-7d4b8c9f-x2k9
```

```
Name:         web-app-7d4b8c9f-x2k9
Namespace:    default
Status:       Running
IP:           10.244.0.5
Containers:
  web-app:
    Image:    my-app:1.0
    Port:     3000/TCP
    State:    Running
Events:
  Normal  Scheduled  5m   default-scheduler  Successfully assigned...
  Normal  Pulled     5m   kubelet            Container image already present
  Normal  Started    5m   kubelet            Started container web-app
```

---

### kubectl apply

**What it does:** Creates or updates resources from a YAML file. The standard way to deploy things in Kubernetes.

```bash
# Apply a single file
kubectl apply -f deployment.yaml
```

```
deployment.apps/web-app created
```

```bash
# Apply all YAML files in a directory
kubectl apply -f ./k8s/

# Apply from a URL
kubectl apply -f https://example.com/deployment.yaml
```

---

### kubectl delete

**What it does:** Removes resources.

```bash
# Delete a specific pod
kubectl delete pod web-app-7d4b8c9f-x2k9

# Delete using a YAML file
kubectl delete -f deployment.yaml

# Delete all pods with a specific label
kubectl delete pods -l app=web-app
```

---

### kubectl logs

**What it does:** Shows logs from a pod.

```bash
# Show logs
kubectl logs web-app-7d4b8c9f-x2k9

# Follow logs in real time
kubectl logs -f web-app-7d4b8c9f-x2k9

# Show logs from a specific container (multi-container pod)
kubectl logs web-app-7d4b8c9f-x2k9 -c sidecar

# Show logs from a previous (crashed) instance
kubectl logs web-app-7d4b8c9f-x2k9 --previous
```

---

### kubectl exec

**What it does:** Runs a command inside a pod.

```bash
# Open a shell
kubectl exec -it web-app-7d4b8c9f-x2k9 -- bash

# Run a single command
kubectl exec web-app-7d4b8c9f-x2k9 -- cat /app/config.json
```

---

### kubectl scale

**What it does:** Changes the number of replicas in a deployment.

```bash
kubectl scale deployment web-app --replicas=5
```

```
deployment.apps/web-app scaled
```

---

### kubectl rollout

**What it does:** Manages rollouts (updates) for deployments.

```bash
# Check rollout status
kubectl rollout status deployment/web-app
```

```
deployment "web-app" successfully rolled out
```

```bash
# View rollout history
kubectl rollout history deployment/web-app

# Undo the last rollout
kubectl rollout undo deployment/web-app

# Undo to a specific revision
kubectl rollout undo deployment/web-app --to-revision=2
```

---

## Quick Reference Table

Here is a side-by-side comparison of the most common tasks:

| Task | Docker Command | kubectl Command |
|------|---------------|----------------|
| Run something | `docker run nginx` | `kubectl run nginx --image=nginx` |
| List running | `docker ps` | `kubectl get pods` |
| Stop | `docker stop my-web` | `kubectl delete pod my-pod` |
| View logs | `docker logs my-web` | `kubectl logs my-pod` |
| Shell access | `docker exec -it my-web bash` | `kubectl exec -it my-pod -- bash` |
| Deploy app | `docker compose up` | `kubectl apply -f app.yaml` |
| Scale | `docker compose up --scale web=3` | `kubectl scale deploy web --replicas=3` |
| Clean up | `docker system prune` | `kubectl delete all --all` |

---

## Key Points

- **Container commands** let you create, run, monitor, and clean up containers. The most important ones are `run`, `ps`, `stop`, `rm`, `logs`, and `exec`.
- **Image commands** handle blueprints. You will use `build`, `pull`, `push`, `images`, and `rmi` the most.
- **Volume commands** manage persistent data. Always use named volumes for important data.
- **Network commands** control how containers communicate. Custom networks give you automatic DNS.
- **Compose commands** orchestrate multi-container apps. `up`, `down`, `ps`, and `logs` are your daily tools.
- **System commands** keep Docker healthy. Run `docker system prune` regularly to free up disk space.
- **Swarm commands** manage container clusters. Great for simpler deployments.
- **kubectl commands** manage Kubernetes clusters. More powerful but more complex than Swarm.
- When in doubt about any command, add `--help` to see all available options (e.g., `docker run --help`).
