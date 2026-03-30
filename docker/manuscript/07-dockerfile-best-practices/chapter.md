# Chapter 7: Dockerfile Best Practices

## What You Will Learn

By the end of this chapter, you will be able to:

- Use multi-stage builds to dramatically reduce image size
- Minimize the number of layers by combining RUN commands
- Order Dockerfile instructions for optimal cache performance
- Run containers as a non-root user for better security
- Write effective `.dockerignore` files
- Choose specific image tags instead of `:latest`
- Understand the difference between COPY and ADD
- Add health checks to your containers
- Compare image sizes before and after applying best practices

## Why This Chapter Matters

In the previous chapter, you learned how to write a Dockerfile and build an image. But writing a Dockerfile that works and writing a Dockerfile that works *well* are two very different things.

A poorly written Dockerfile might produce an image that is 1.2 GB in size, takes 5 minutes to build, and runs as the root user (a serious security risk). The same application, with a well-written Dockerfile, might produce a 50 MB image that builds in 10 seconds and runs securely.

In professional environments, these differences matter enormously. Larger images mean slower deployments, higher storage costs, and more security vulnerabilities. This chapter teaches you the techniques that separate amateur Dockerfiles from professional ones.

---

## Multi-Stage Builds: The Biggest Win

Multi-stage builds are the single most powerful technique for reducing image size. They let you use one image for building your application and a different, much smaller image for running it.

**Real-life analogy:** Think about baking a cake. You need a big messy kitchen with mixing bowls, a whisk, measuring cups, and an oven to *make* the cake. But when you *serve* the cake, you only need the cake itself and a plate. You do not bring the entire kitchen to the dinner table. Multi-stage builds work the same way -- you use a big "kitchen" image to build your app, then copy only the finished product to a small "plate" image.

### The Problem Without Multi-Stage Builds

Consider building a React application:

```dockerfile
# Single-stage build (the old way)
FROM node:18

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

# The built files are in /app/build
# But we also have node_modules, source code, build tools...

CMD ["npx", "serve", "-s", "build"]
```

This image contains:
- Node.js runtime (~350 MB)
- `node_modules` directory (~200 MB)
- Source code (~5 MB)
- Build tools (~100 MB)
- The actual built files we need (~2 MB)

**Total image size: ~660 MB** for an app that only needs 2 MB of files.

### The Solution: Multi-Stage Builds

```dockerfile
# ============================================
# Stage 1: Build (the kitchen)
# ============================================
FROM node:18 AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

# At this point, /app/build contains our static files

# ============================================
# Stage 2: Production (the plate)
# ============================================
FROM nginx:alpine

# Copy ONLY the built files from stage 1
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Breaking this down:

**Stage 1 (`builder`):**
- Uses the full Node.js image with all build tools
- Installs dependencies and builds the application
- Named `builder` using `AS builder`

**Stage 2 (production):**
- Starts fresh with a tiny nginx:alpine image
- Copies only the built files from stage 1 using `COPY --from=builder`
- Does not include Node.js, node_modules, or source code

```
+--------------------------------------------------+
|    Multi-Stage Build Flow                        |
+--------------------------------------------------+
|                                                  |
|    Stage 1: builder (node:18)                    |
|    +------------------------------------+        |
|    | node_modules/     200 MB           |        |
|    | src/              5 MB             |        |
|    | build tools       100 MB           |        |
|    | build/            2 MB  ----+      |        |
|    +------------------------------------+  |     |
|                                         |  |     |
|                            Only this    |  |     |
|                            gets copied -+  |     |
|                                            |     |
|    Stage 2: production (nginx:alpine)      v     |
|    +------------------------------------+        |
|    | nginx             10 MB            |        |
|    | build/            2 MB             |        |
|    +------------------------------------+        |
|                                                  |
|    Final image size: ~12 MB                      |
|    (down from ~660 MB!)                          |
|                                                  |
+--------------------------------------------------+
```

### Size Comparison

```
+-----------------------+-------------+
| Approach              | Image Size  |
+-----------------------+-------------+
| Single stage          | ~660 MB     |
| Multi-stage           | ~12 MB      |
| Reduction             | 98%         |
+-----------------------+-------------+
```

### Multi-Stage Build for a Go Application

Go is even more dramatic because Go compiles to a single binary:

```dockerfile
# Stage 1: Build
FROM golang:1.21 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server

# Stage 2: Production
FROM scratch

COPY --from=builder /app/server /server

EXPOSE 8080
ENTRYPOINT ["/server"]
```

The `scratch` image is completely empty (0 bytes). The final image contains only the compiled Go binary.

```
+-----------------------+-------------+
| Approach              | Image Size  |
+-----------------------+-------------+
| Single stage (golang) | ~850 MB     |
| Multi-stage (scratch) | ~8 MB       |
| Reduction             | 99%         |
+-----------------------+-------------+
```

---

## Minimize Layers: Combine RUN Commands

Every RUN instruction creates a new layer. Unnecessary layers increase image size and slow down pulls.

**Real-life analogy:** Imagine you go to the grocery store three times in one day -- once for bread, once for milk, and once for eggs. That is three trips. It would be much more efficient to buy all three things in a single trip. Combining RUN commands is the same idea.

### The Problem

```dockerfile
# BAD: 7 separate layers
FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget
RUN apt-get install -y git
RUN apt-get install -y vim
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
```

Each RUN creates a layer. Even though we clean up in the last two commands, the packages still exist in earlier layers. Docker layers are additive -- deleting something in a later layer does not remove it from earlier layers.

```
+--------------------------------------------------+
|    Why Separate Layers Waste Space               |
+--------------------------------------------------+
|                                                  |
|    Layer 7: rm -rf /var/lib/apt/lists/*  (+0 MB) |
|    Layer 6: apt-get clean                (+0 MB) |
|    Layer 5: install vim                  (+30 MB) |
|    Layer 4: install git                  (+50 MB) |
|    Layer 3: install wget                 (+5 MB)  |
|    Layer 2: install curl                 (+5 MB)  |
|    Layer 1: apt-get update               (+25 MB) |
|    Base:    ubuntu:22.04                 (+77 MB) |
|                                                  |
|    Total: ~192 MB                                |
|    (cleanup in layers 6-7 does NOT reduce        |
|     the size of layers 1-5!)                     |
|                                                  |
+--------------------------------------------------+
```

### The Solution

```dockerfile
# GOOD: 1 layer for all package operations
FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y \
        curl \
        wget \
        git \
        vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

Now the update, installation, and cleanup all happen in a single layer. The temporary files from `apt-get update` never get stored in a separate layer.

```
+--------------------------------------------------+
|    Combined Layer                                |
+--------------------------------------------------+
|                                                  |
|    Layer 1: update + install + clean    (+70 MB) |
|    Base:    ubuntu:22.04                (+77 MB) |
|                                                  |
|    Total: ~147 MB (saved ~45 MB)                 |
|                                                  |
+--------------------------------------------------+
```

### Formatting Tips

Use backslashes and alphabetical ordering to keep combined RUN commands readable:

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git \
        vim \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

The `--no-install-recommends` flag tells apt not to install suggested packages, which further reduces image size.

---

## Order Instructions for Cache: Dependencies Before Code

We touched on this in Chapter 6, but it is worth emphasizing because it is one of the most impactful best practices.

**The rule:** Put things that change **rarely** at the **top** of your Dockerfile, and things that change **frequently** at the **bottom**.

### Why It Matters

Remember: when a layer changes, all subsequent layers are rebuilt. So if your code changes (which happens many times a day), you want to make sure expensive operations like `npm install` are above the code copy and can remain cached.

### The Pattern

```dockerfile
FROM node:18-alpine

WORKDIR /app

# 1. Copy ONLY dependency files (changes rarely)
COPY package.json package-lock.json ./

# 2. Install dependencies (expensive, but cached if step 1 unchanged)
RUN npm ci --only=production

# 3. Copy application code (changes frequently)
COPY . .

# 4. Configuration (changes rarely)
EXPOSE 3000
CMD ["node", "server.js"]
```

### Cache Performance Comparison

```
+--------------------------------------------------+
|    Developer's Typical Day                       |
+--------------------------------------------------+
|                                                  |
|    Action              Good Order   Bad Order    |
|    ------------------------------------------    |
|    Change code         0.5s build   30s build    |
|    Change code         0.5s build   30s build    |
|    Change code         0.5s build   30s build    |
|    Add dependency      30s build    30s build    |
|    Change code         0.5s build   30s build    |
|    Change code         0.5s build   30s build    |
|    ------------------------------------------    |
|    Total (6 builds)    62s          180s          |
|    Time saved          118 seconds               |
|                                                  |
+--------------------------------------------------+
```

Over a day with many rebuilds, good ordering saves minutes. Over a week, it saves hours.

### Python Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy dependency file first
COPY requirements.txt .

# Install dependencies (cached if requirements.txt unchanged)
RUN pip install --no-cache-dir -r requirements.txt

# Copy code last
COPY . .

CMD ["python", "app.py"]
```

### Java Example

```dockerfile
FROM maven:3.9-eclipse-temurin-17

WORKDIR /app

# Copy dependency definition first
COPY pom.xml .

# Download dependencies (cached if pom.xml unchanged)
RUN mvn dependency:go-offline

# Copy source code last
COPY src ./src

RUN mvn package -DskipTests

CMD ["java", "-jar", "target/app.jar"]
```

---

## Non-Root USER: Security First

By default, containers run as the **root** user. This is a security risk. If an attacker breaks into your container, they have root access and can potentially escape to the host system.

**Real-life analogy:** Running a container as root is like giving every employee the master key to the entire building. They only need access to their own office. Give them a key that opens just their office door.

### The Problem

```bash
# By default, processes run as root inside containers
$ docker run node:18-alpine whoami
root

$ docker run node:18-alpine id
uid=0(root) gid=0(root)
```

### The Solution: Add a USER Instruction

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --only=production

COPY . .

# Create a non-root user
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup

# Change ownership of the app directory
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

EXPOSE 3000
CMD ["node", "server.js"]
```

### Some Base Images Include Non-Root Users

Many official images come with a non-root user already created:

```dockerfile
# node images have a user called "node"
FROM node:18-alpine

WORKDIR /app

COPY --chown=node:node package.json package-lock.json ./
RUN npm ci --only=production

COPY --chown=node:node . .

# Use the built-in "node" user
USER node

EXPOSE 3000
CMD ["node", "server.js"]
```

The `--chown=node:node` flag in COPY sets the owner of the files as they are copied, which is cleaner than running `chown` afterward.

### Verifying It Works

```bash
$ docker build -t secure-app .

$ docker run secure-app whoami
node

$ docker run secure-app id
uid=1000(node) gid=1000(node)
```

The process is no longer running as root.

### Where to Place USER

Place `USER` after all operations that require root privileges (like installing packages) but before the `CMD`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# These operations might need root
COPY package.json package-lock.json ./
RUN npm ci --only=production
COPY . .

# Switch to non-root AFTER setup is done
USER node

# These run as the non-root user
EXPOSE 3000
CMD ["node", "server.js"]
```

---

## Use .dockerignore Effectively

We covered `.dockerignore` in Chapter 6, but here is a more comprehensive example:

```
# Version control
.git
.gitignore
.gitattributes

# CI/CD
.github
.gitlab-ci.yml
.circleci
Jenkinsfile

# Docker (no need to include these in the image)
Dockerfile
Dockerfile.*
docker-compose*.yml
.dockerignore

# Dependencies (installed inside the container)
node_modules
vendor
__pycache__
*.pyc
.venv
venv

# IDE and editor files
.vscode
.idea
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Test and coverage
coverage
.nyc_output
*.test.js
*.spec.js
test
tests
__tests__

# Documentation
README.md
CHANGELOG.md
LICENSE
docs

# Environment and secrets
.env
.env.*
*.pem
*.key

# Build artifacts
dist
build
*.log
tmp
temp
```

### Impact of a Good .dockerignore

```
+-------------------------------------------+
| File/Directory    | Size   | Needed?      |
+-------------------------------------------+
| node_modules/     | 200 MB | No (reinstalled)|
| .git/             | 50 MB  | No           |
| coverage/         | 10 MB  | No           |
| .vscode/          | 1 MB   | No           |
| .env              | 1 KB   | DANGEROUS!   |
| src/              | 2 MB   | Yes          |
| package.json      | 1 KB   | Yes          |
| server.js         | 5 KB   | Yes          |
+-------------------------------------------+
| Without .dockerignore: ~263 MB sent        |
| With .dockerignore:    ~2 MB sent          |
+-------------------------------------------+
```

---

## Specific Tags, Not :latest

Always use specific version tags for your base images. Never use `:latest` in production Dockerfiles.

**Real-life analogy:** Imagine ordering "the latest model" of a car. Today that might be a sedan. Next month, it might be an SUV. If your parking garage only fits sedans, you have a problem. Specify the exact model you want.

### The Problem with :latest

```dockerfile
# BAD: What version of Node.js will you get?
FROM node:latest

# It could be Node 18 today and Node 22 tomorrow
# Your app might not work with Node 22
# Your builds are not reproducible
```

### Use Specific Tags

```dockerfile
# GOOD: Always gets Node.js 18 on Alpine
FROM node:18-alpine

# BETTER: Specific minor version
FROM node:18.19-alpine

# BEST: Specific patch version (most reproducible)
FROM node:18.19.0-alpine3.18
```

### Comparison

```
+--------------------------------------------------+
|    Tag Specificity                               |
+--------------------------------------------------+
|                                                  |
|    node:latest         Could be anything!        |
|    node:18             Node 18, any minor/patch  |
|    node:18-alpine      Node 18 on Alpine Linux   |
|    node:18.19-alpine   Specific minor version    |
|    node:18.19.0-alpine Exact version (best)      |
|                                                  |
|    More specific = More reproducible             |
|                                                  |
+--------------------------------------------------+
```

---

## COPY vs ADD: Know the Difference

Both `COPY` and `ADD` copy files into the image, but they have different capabilities.

### COPY (Recommended)

`COPY` does exactly one thing: it copies files and directories from the build context into the image.

```dockerfile
COPY package.json .
COPY src/ /app/src/
```

### ADD (Use Sparingly)

`ADD` does everything COPY does, plus:
1. It can extract compressed archives (`.tar.gz`, `.tar.bz2`, etc.)
2. It can download files from URLs

```dockerfile
# ADD can extract tar files automatically
ADD app.tar.gz /app/

# ADD can download from URLs (but DON'T do this)
ADD https://example.com/file.txt /app/
```

### Why COPY Is Better

```
+--------------------------------------------------+
|    COPY vs ADD                                   |
+--------------------------------------------------+
|                                                  |
|    Feature          | COPY    | ADD              |
|    -----------------+---------+------------------+
|    Copy files       | Yes     | Yes              |
|    Copy directories | Yes     | Yes              |
|    Extract archives | No      | Yes (auto)       |
|    Download URLs    | No      | Yes (no caching) |
|    Predictable      | Yes     | Surprising       |
|    Recommended      | Yes     | Rarely           |
|                                                  |
|    Rule: Use COPY unless you specifically need   |
|    ADD's auto-extraction feature.                |
|                                                  |
+--------------------------------------------------+
```

The problem with ADD is its "magic" behavior. If you `ADD` a file called `data.tar.gz`, it gets automatically extracted. This can be surprising if you just wanted to copy the archive without extracting it.

For downloading files, use `RUN curl` or `RUN wget` instead of `ADD`, because:
- Downloaded files are not cached
- You cannot verify checksums
- You cannot extract and clean up in the same layer

```dockerfile
# BAD: ADD for downloading
ADD https://example.com/big-file.tar.gz /app/

# GOOD: RUN curl for downloading
RUN curl -fsSL https://example.com/big-file.tar.gz | tar -xz -C /app/ && \
    rm -f /app/big-file.tar.gz
```

---

## HEALTHCHECK: Is Your Container Healthy?

A `HEALTHCHECK` instruction tells Docker how to check if your container is actually working, not just running.

**Real-life analogy:** A heartbeat monitor does not just check if a patient is in the room. It checks if their heart is actually beating. HEALTHCHECK does the same for your container.

### The Problem Without HEALTHCHECK

```bash
$ docker ps
CONTAINER ID   IMAGE     STATUS
a1b2c3d4e5f6   my-app    Up 2 hours
```

The container says "Up" but the application inside might have crashed, run out of memory, or be stuck in an infinite loop. Docker does not know the difference.

### Adding a HEALTHCHECK

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --only=production
COPY . .

# Health check: try to reach the /health endpoint every 30 seconds
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

Breaking down the options:

- `--interval=30s` -- Check every 30 seconds
- `--timeout=10s` -- Wait up to 10 seconds for a response
- `--start-period=5s` -- Give the app 5 seconds to start up before checking
- `--retries=3` -- Fail after 3 consecutive failed checks
- `CMD curl -f http://localhost:3000/health || exit 1` -- The actual check command

### How It Looks in docker ps

```bash
$ docker ps
CONTAINER ID   IMAGE     STATUS
a1b2c3d4       my-app    Up 2 min (healthy)
b5c6d7e8       my-app    Up 5 min (unhealthy)
f9g0h1i2       my-app    Up 10 sec (health: starting)
```

Docker now shows three possible health states:

```
+--------------------------------------------------+
|    Container Health States                       |
+--------------------------------------------------+
|                                                  |
|    starting   -> Just started, waiting for       |
|                  first successful check          |
|                                                  |
|    healthy    -> Health check is passing          |
|                                                  |
|    unhealthy  -> Health check is failing          |
|                  (3+ consecutive failures)        |
|                                                  |
+--------------------------------------------------+
```

### Health Check Without curl

If your image does not include `curl` (to keep it small), you can use other approaches:

```dockerfile
# For Node.js: use a custom health check script
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1) })"

# For Python: use wget (available on Alpine)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5000/health || exit 1
```

---

## Before and After: Putting It All Together

Let us take a real Dockerfile and apply all the best practices we have learned.

### Before: The Naive Dockerfile

```dockerfile
FROM node:latest

COPY . /app
WORKDIR /app

RUN npm install
RUN npm run build

EXPOSE 3000
CMD npm start
```

Problems:
- Uses `:latest` (not reproducible)
- Copies everything before installing (cache busting)
- No `.dockerignore`
- Separate RUN commands
- No non-root user
- No health check
- Shell form CMD
- Single stage (includes build tools in production)

### After: The Professional Dockerfile

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependency files first for cache
COPY package.json package-lock.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production
FROM node:18-alpine

WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json ./

# Install ONLY production dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy built application from builder stage
COPY --from=builder /app/dist ./dist

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

# Run as non-root user
USER node

EXPOSE 3000

# Exec form CMD
CMD ["node", "dist/server.js"]
```

### Size and Build Time Comparison

```
+--------------------------------------------------+
|    Before vs After Comparison                    |
+--------------------------------------------------+
|                                                  |
|    Metric              Before       After        |
|    -----------------------------------------------
|    Base image          node:latest  node:18-alpine|
|    Image size          950 MB       120 MB       |
|    Build (first)       60 sec       45 sec       |
|    Build (code change) 55 sec       3 sec        |
|    Runs as             root         node (safe)  |
|    Health check        No           Yes          |
|    Reproducible        No           Yes          |
|    Build tools in prod Yes          No           |
|                                                  |
|    Size reduction: 87%                           |
|    Rebuild speedup: 18x faster                   |
|                                                  |
+--------------------------------------------------+
```

### Checking Image Sizes

You can compare image sizes using `docker images`:

```bash
$ docker images
REPOSITORY     TAG        SIZE
my-app         naive      950MB
my-app         optimized  120MB
```

Or for more detail, use `docker history`:

```bash
$ docker history my-app:optimized
IMAGE          CREATED        SIZE      COMMENT
a1b2c3d4       2 min ago      0B        CMD ["node", "dist/server.js"]
e5f6g7h8       2 min ago      0B        EXPOSE 3000
i9j0k1l2       2 min ago      0B        USER node
m3n4o5p6       2 min ago      0B        HEALTHCHECK ...
q7r8s9t0       2 min ago      1.5MB     COPY dist from builder
u1v2w3x4       2 min ago      45MB      npm ci --only=production
y5z6a7b8       3 min ago      3KB       COPY package*.json
c9d0e1f2       3 min ago      0B        WORKDIR /app
g3h4i5j6       2 weeks ago    75MB      node:18-alpine base
```

---

## Best Practices Checklist

Here is a quick reference checklist for writing professional Dockerfiles:

```
+--------------------------------------------------+
|    Dockerfile Best Practices Checklist            |
+--------------------------------------------------+
|                                                  |
|  [ ] Use multi-stage builds                      |
|  [ ] Use specific base image tags (not :latest)  |
|  [ ] Use -alpine or -slim variants               |
|  [ ] Copy dependency files before code           |
|  [ ] Combine RUN commands with &&                |
|  [ ] Clean up in the same RUN layer              |
|  [ ] Use COPY instead of ADD                     |
|  [ ] Add a .dockerignore file                    |
|  [ ] Run as non-root USER                        |
|  [ ] Use exec form for CMD                       |
|  [ ] Add a HEALTHCHECK                           |
|  [ ] Do not install unnecessary packages         |
|  [ ] Add comments explaining each section        |
|                                                  |
+--------------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Building Without a .dockerignore

```bash
# Without .dockerignore, secrets can leak into the image
$ docker build -t my-app .
# .env file with API keys is now inside the image!
# Anyone who pulls your image can extract those secrets
```

### Mistake 2: Running npm install Instead of npm ci

```dockerfile
# BAD: npm install can modify package-lock.json
RUN npm install

# GOOD: npm ci uses exact versions from package-lock.json
RUN npm ci
```

`npm ci` (clean install) is designed for automated environments. It:
- Installs exact versions from `package-lock.json`
- Is faster than `npm install`
- Deletes `node_modules` before installing
- Fails if `package-lock.json` and `package.json` are out of sync

### Mistake 3: Not Cleaning Up in the Same Layer

```dockerfile
# BAD: cleanup in separate layer does not reduce size
RUN apt-get update && apt-get install -y gcc
RUN rm -rf /var/lib/apt/lists/*

# GOOD: cleanup in same layer removes files before layer is saved
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*
```

### Mistake 4: Using ADD When COPY Would Work

```dockerfile
# BAD: ADD has surprising auto-extraction behavior
ADD config.tar.gz /app/

# GOOD: Be explicit about what you want
COPY config.tar.gz /app/
RUN tar -xzf /app/config.tar.gz -C /app/ && rm /app/config.tar.gz
```

### Mistake 5: Ignoring HEALTHCHECK

Without HEALTHCHECK, Docker only knows if the main process is running. It does not know if your application is actually responding to requests. A crashed web server that keeps the process alive will appear "healthy" without a proper health check.

---

## Quick Summary

Professional Dockerfiles use several techniques to produce small, fast, and secure images:

- **Multi-stage builds** separate the build environment from the production environment, often reducing image size by 80-99%
- **Combining RUN commands** prevents temporary files from being stored in separate layers
- **Ordering for cache** means putting dependencies before code so that expensive installations are cached
- **Non-root USER** prevents attackers from having root access if they break into the container
- **Specific tags** make builds reproducible by locking down the base image version
- **COPY over ADD** keeps behavior predictable
- **HEALTHCHECK** lets Docker (and orchestrators) know if your application is truly healthy

---

## Key Points

- Multi-stage builds are the most effective way to reduce image size
- Each RUN instruction creates a layer; combine related commands
- Put things that change rarely at the top of the Dockerfile
- Always run containers as a non-root user in production
- Never use `:latest` in production Dockerfiles
- Use `COPY` unless you specifically need `ADD`'s auto-extraction
- HEALTHCHECK tells Docker how to verify your application is working
- A good `.dockerignore` speeds up builds and prevents secret leaks
- Use `npm ci` instead of `npm install` in Dockerfiles

---

## Practice Questions

1. What is a multi-stage build, and why does it reduce image size? What keyword connects the stages?

2. You have a Dockerfile with three separate RUN commands that install packages. Why is this worse than combining them into one RUN command? Give an example of the combined version.

3. Why should you always run your production containers as a non-root user? What instruction changes the user?

4. A developer uses `FROM node:latest` in their Dockerfile. Their application works today but fails after they rebuild the image next month. What likely happened?

5. What is the difference between COPY and ADD? When would you use ADD?

---

## Exercises

### Exercise 1: Multi-Stage Build

Take the following single-stage Dockerfile and convert it to a multi-stage build:

```dockerfile
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
CMD ["node", "dist/server.js"]
```

Build both versions and compare the image sizes using `docker images`.

### Exercise 2: Apply All Best Practices

Write a Dockerfile for a Python Flask application that:
1. Uses `python:3.11-slim` as the base
2. Copies `requirements.txt` before the rest of the code
3. Installs dependencies with `pip install --no-cache-dir`
4. Runs as a non-root user
5. Includes a health check
6. Uses exec form CMD

### Exercise 3: Measure the Difference

1. Create a simple Node.js application
2. Write a "naive" Dockerfile (single stage, no `.dockerignore`, `:latest` tag)
3. Write an "optimized" Dockerfile (multi-stage, `.dockerignore`, specific tag, non-root user)
4. Build both and compare:
   - Image size (`docker images`)
   - Build time (use `time docker build`)
   - User inside container (`docker run IMAGE whoami`)

---

## What Is Next?

Now that you know how to write professional Dockerfiles, the next chapter puts these skills to work. You will build complete, production-ready Docker images for three different applications: a Node.js Express API, a Python Flask API, and a Java Spring Boot application. Each one will use the best practices you learned in this chapter.
