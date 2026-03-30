# Chapter 25: Optimizing Docker Images

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand why image size matters for speed, cost, and security
- Analyze image layers and wasted space with `dive`
- Use distroless base images for minimal containers
- Choose Alpine variants for smaller images
- Apply multi-stage builds to eliminate build-time dependencies
- Write effective `.dockerignore` files
- Leverage BuildKit features for faster, smarter builds
- Implement layer caching strategies that speed up rebuilds
- Transform a bloated image into an optimized one with before/after examples

---

## Why This Chapter Matters

A typical unoptimized Docker image for a Node.js application is around **1 GB**. An optimized version of the same application can be **50-100 MB** — ten to twenty times smaller.

Why does this matter?

```
+-----------------------------------------------------------+
|              Why Image Size Matters                        |
|                                                            |
|   1. FASTER PULLS                                          |
|      1 GB image over 100 Mbps = ~80 seconds                |
|      50 MB image over 100 Mbps = ~4 seconds                |
|      In a cluster with 50 nodes, that is 66 MINUTES saved. |
|                                                            |
|   2. LESS STORAGE                                          |
|      100 images x 1 GB = 100 GB on each server             |
|      100 images x 50 MB = 5 GB on each server              |
|                                                            |
|   3. SMALLER ATTACK SURFACE                                |
|      Fewer packages = fewer potential vulnerabilities       |
|      1 GB image: ~600 packages, ~200 known CVEs            |
|      50 MB image: ~20 packages, ~5 known CVEs              |
|                                                            |
|   4. FASTER CI/CD                                          |
|      Smaller images build and push faster                  |
|      Your pipeline finishes in 2 minutes instead of 10     |
|                                                            |
|   5. LOWER COSTS                                           |
|      Registry storage, bandwidth, and server disk space    |
|      all cost money. Smaller images = lower bills.         |
+-----------------------------------------------------------+
```

Think of it like packing for a trip. You could bring your entire wardrobe in three suitcases, or you could pack only what you need in a carry-on. The carry-on is faster through the airport, costs less (no checked bag fees), and you are less likely to lose something.

---

## Analyzing Images with Dive

Before optimizing, you need to understand what is inside your image. **dive** is a tool that lets you explore each layer of a Docker image and see exactly what files are added, modified, or removed.

### Installing Dive

```bash
# macOS
brew install dive

# Linux
wget https://github.com/wagoodman/dive/releases/download/v0.12.0/dive_0.12.0_linux_amd64.deb
sudo dpkg -i dive_0.12.0_linux_amd64.deb
```

### Using Dive

```bash
dive myapp:1.0.0
```

Dive opens an interactive terminal UI with two panels:

```
+-----------------------------------------------------------+
|              Dive Interface                                |
|                                                            |
|   Left Panel: Image Layers                                 |
|   +-----------------------------------------------------+ |
|   | Layer 1: FROM node:20         (350 MB)              | |
|   | Layer 2: RUN npm install      (200 MB)              | |
|   | Layer 3: COPY . .             (450 MB) <-- WHY?     | |
|   | Layer 4: RUN npm run build    (50 MB)               | |
|   +-----------------------------------------------------+ |
|                                                            |
|   Right Panel: Files in Selected Layer                     |
|   +-----------------------------------------------------+ |
|   | /app/node_modules/           (200 MB)               | |
|   | /app/.git/                   (150 MB)  <-- WASTE     | |
|   | /app/test/                   (50 MB)   <-- WASTE     | |
|   | /app/docs/                   (30 MB)   <-- WASTE     | |
|   +-----------------------------------------------------+ |
|                                                            |
|   Image efficiency: 45%  (Wasted space: 230 MB)           |
+-----------------------------------------------------------+
```

### What to Look For

1. **Unexpectedly large layers** — Why is COPY adding 450 MB?
2. **Files that should not be there** — `.git/`, `test/`, `docs/`, `node_modules/.cache`
3. **Duplicate files** — The same file appearing in multiple layers
4. **Wasted space** — Files added in one layer and deleted in another (they still take space)

### Dive in CI/CD

You can use dive in your CI pipeline to enforce image efficiency:

```bash
# Fail if the image efficiency is below 90%
CI=true dive myapp:1.0.0 --ci --lowestEfficiency 0.90
```

---

## Distroless Base Images

**Distroless images** from Google contain ONLY your application and its runtime dependencies. No shell, no package manager, no utilities like `curl`, `wget`, or `ls`.

### Why Distroless?

```
+-----------------------------------------------------------+
|              What Is Inside Each Base Image                |
|                                                            |
|   ubuntu:22.04 (77 MB):                                    |
|   +-----------------------------------------------------+ |
|   | Shell (bash), Package manager (apt), curl, wget,    | |
|   | ls, cat, grep, sed, awk, mount, sudo, systemd,     | |
|   | openssl, ca-certificates, libc, libstdc++, perl,    | |
|   | python3, coreutils, findutils, ...                  | |
|   +-----------------------------------------------------+ |
|                                                            |
|   distroless (20 MB):                                      |
|   +-----------------------------------------------------+ |
|   | ca-certificates, libc, libstdc++, tzdata            | |
|   | YOUR APPLICATION                                    | |
|   +-----------------------------------------------------+ |
|                                                            |
|   Everything else is GONE. Attackers have nothing to use.  |
+-----------------------------------------------------------+
```

### Using Distroless

Distroless images are designed for multi-stage builds. You build in a full image and copy the result to a distroless image.

**Node.js example:**

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# Stage 2: Production (distroless)
FROM gcr.io/distroless/nodejs20-debian12
WORKDIR /app
COPY --from=builder /app .
CMD ["server.js"]
```

**Go example (even smaller — no runtime needed):**

```dockerfile
# Stage 1: Build
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o server .

# Stage 2: Production (static distroless)
FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/server /server
CMD ["/server"]
```

The Go example produces an image under **10 MB** because the compiled binary includes everything it needs.

### Available Distroless Images

| Image                                          | Contents                     | Size  |
|------------------------------------------------|-----------------------------|-------|
| `gcr.io/distroless/static-debian12`            | CA certs, tzdata             | ~2 MB |
| `gcr.io/distroless/base-debian12`              | + glibc                      | ~20 MB|
| `gcr.io/distroless/cc-debian12`                | + libstdc++                  | ~25 MB|
| `gcr.io/distroless/nodejs20-debian12`          | + Node.js 20 runtime         | ~130 MB|
| `gcr.io/distroless/python3-debian12`           | + Python 3 runtime           | ~50 MB|
| `gcr.io/distroless/java21-debian12`            | + Java 21 runtime            | ~200 MB|

### The Trade-Off

Without a shell, you cannot:

- `docker exec -it container sh` — No shell to exec into
- Debug inside the container easily
- Install debugging tools on the fly

**Solution:** Use a debug variant during development:

```dockerfile
# For debugging (has a busybox shell)
FROM gcr.io/distroless/nodejs20-debian12:debug
```

---

## Alpine Variants

**Alpine Linux** is a minimal Linux distribution designed for security and small size. Many official Docker images offer Alpine variants.

### Size Comparison

```bash
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
```

```
IMAGE                    SIZE
node:20                  1.1 GB
node:20-slim             200 MB
node:20-alpine           135 MB
python:3.12              1.0 GB
python:3.12-slim         150 MB
python:3.12-alpine       55 MB
```

Alpine variants are typically **5-20x smaller** than their full counterparts.

### Using Alpine

```dockerfile
# Instead of this (1.1 GB):
FROM node:20

# Use this (135 MB):
FROM node:20-alpine
```

### Alpine Gotchas

Alpine uses **musl libc** instead of **glibc**. This can cause compatibility issues with some software:

1. **Native npm packages** may fail to compile. Fix by installing build tools:

```dockerfile
FROM node:20-alpine
RUN apk add --no-cache python3 make g++
```

2. **Some Python packages** with C extensions may not work. Use `python:3.12-slim` instead of Alpine in that case.

3. **DNS resolution** behaves slightly differently in Alpine. This rarely causes issues but can surprise you.

**Rule of thumb:** Try Alpine first. If something breaks, fall back to `-slim`. Only use the full image if `-slim` also has problems.

---

## Multi-Stage Builds Recap

Multi-stage builds are the single most impactful optimization technique. We covered them in an earlier chapter, but here is a quick recap with an optimization focus.

### The Problem

```dockerfile
# SINGLE STAGE — everything in one image
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci              # Installs ALL dependencies (including dev)
COPY . .
RUN npm run build       # Build step (generates dist/)
CMD ["node", "dist/server.js"]

# Final image contains:
# - All source code (not needed at runtime)
# - All dev dependencies (typescript, eslint, jest — not needed)
# - Build tools (not needed)
# - Test files (not needed)
# Result: ~500 MB
```

### The Solution

```dockerfile
# MULTI-STAGE — separate build from runtime
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci                    # All deps (including dev) for building
COPY . .
RUN npm run build             # Compile TypeScript, bundle, etc.

# Stage 2: Production
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production  # Only production dependencies
COPY --from=builder /app/dist ./dist
USER node
CMD ["node", "dist/server.js"]

# Final image contains:
# - Only production dependencies
# - Only compiled output (dist/)
# - No source code, no dev tools, no tests
# Result: ~150 MB
```

```
+-----------------------------------------------------------+
|              Multi-Stage Build Flow                        |
|                                                            |
|   Stage 1 (builder):        Stage 2 (production):          |
|   +-------------------+    +-------------------+           |
|   | node:20-alpine    |    | node:20-alpine    |           |
|   | Source code        |    | dist/ (from S1)   |           |
|   | ALL node_modules   |    | Prod node_modules |           |
|   | TypeScript         |    | (no source code)  |           |
|   | Test files         |    | (no dev deps)     |           |
|   | Build output (dist)|    |                   |           |
|   +-------------------+    +-------------------+           |
|          500 MB                   150 MB                   |
|                                                            |
|   Stage 1 is DISCARDED. Only Stage 2 becomes the image.   |
+-----------------------------------------------------------+
```

---

## .dockerignore Optimization

The `.dockerignore` file tells Docker which files to exclude from the **build context** — the files sent to the Docker daemon when you run `docker build`.

### Why .dockerignore Matters

Without `.dockerignore`, Docker sends EVERYTHING in your project directory to the daemon:

```bash
# Watch the build context size
docker build -t myapp .
# Output: Sending build context to Docker daemon  500MB
```

With a good `.dockerignore`:

```bash
docker build -t myapp .
# Output: Sending build context to Docker daemon  2.5MB
```

### A Comprehensive .dockerignore

```
# .dockerignore

# Version control
.git
.gitignore

# Dependencies (will be installed inside the container)
node_modules
vendor
__pycache__
*.pyc

# Build output (will be built inside the container)
dist
build
out
*.o
*.a

# Development and test files
test
tests
__tests__
*.test.js
*.spec.js
coverage
.nyc_output

# Documentation
docs
*.md
LICENSE
CHANGELOG

# IDE and editor files
.vscode
.idea
*.swp
*.swo
*~

# Environment and secrets
.env
.env.*
*.pem
*.key
*.cert
credentials.json
secrets/

# Docker files (avoid recursive builds)
Dockerfile*
docker-compose*
.dockerignore

# OS files
.DS_Store
Thumbs.db

# CI/CD files
.github
.gitlab-ci.yml
.travis.yml
Jenkinsfile

# Logs
*.log
logs/
```

### Before and After

| Without .dockerignore     | With .dockerignore        |
|---------------------------|---------------------------|
| Build context: 500 MB     | Build context: 2.5 MB     |
| Includes .git (150 MB)    | Excluded                  |
| Includes node_modules     | Excluded (installed fresh) |
| Includes test files       | Excluded                  |
| Includes docs             | Excluded                  |
| Build time: 45 seconds    | Build time: 15 seconds    |

---

## BuildKit Features

**BuildKit** is Docker's modern build engine. It is faster, more efficient, and has features not available in the legacy builder.

### Enabling BuildKit

```bash
# Enable for a single build
DOCKER_BUILDKIT=1 docker build -t myapp .

# Enable globally (add to ~/.bashrc or ~/.zshrc)
export DOCKER_BUILDKIT=1
```

Docker Desktop has BuildKit enabled by default. On Linux servers, you may need to enable it.

### Parallel Stage Execution

BuildKit automatically builds independent stages in parallel:

```dockerfile
# These two stages build AT THE SAME TIME
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.12-alpine AS backend-builder
WORKDIR /backend
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .

# Final stage uses output from both
FROM python:3.12-alpine
COPY --from=frontend-builder /frontend/dist /app/static
COPY --from=backend-builder /backend /app
CMD ["python", "/app/server.py"]
```

The legacy builder runs stages sequentially. BuildKit runs `frontend-builder` and `backend-builder` simultaneously, cutting build time nearly in half.

### Inline Cache Metadata

BuildKit can embed cache metadata in pushed images, allowing future builds to pull cache from the registry:

```bash
docker build \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  -t myusername/myapp:latest \
  .

docker push myusername/myapp:latest

# Future builds can cache FROM the registry
docker build \
  --cache-from myusername/myapp:latest \
  -t myusername/myapp:v1.0.1 \
  .
```

### Secret Mounts

BuildKit lets you use secrets during the build without storing them in any layer:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
# Mount .npmrc as a secret — available during this RUN but not in any layer
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci --only=production
COPY . .
CMD ["node", "server.js"]
```

```bash
docker build --secret id=npmrc,src=.npmrc -t myapp .
```

The `.npmrc` file (which may contain registry tokens) is available during `npm ci` but is NOT stored in the image.

### Cache Mounts

BuildKit can cache directories between builds, dramatically speeding up package installations:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
# Cache npm's download cache between builds
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production
COPY . .
CMD ["node", "server.js"]
```

Even if `package.json` changes, npm reuses cached downloads instead of downloading everything from scratch.

**Python example:**

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
COPY . .
CMD ["python", "server.py"]
```

---

## Layer Caching Strategies

Docker caches each layer and reuses it if nothing has changed. Understanding how the cache works lets you structure your Dockerfile for maximum cache hits.

### The Cache Rule

Docker reuses a cached layer if:
1. The instruction has not changed
2. ALL files referenced by the instruction have not changed
3. ALL previous layers are also cached (cache is sequential)

**The moment one layer is invalidated, ALL subsequent layers are rebuilt.**

```
+-----------------------------------------------------------+
|              Cache Invalidation                            |
|                                                            |
|   Layer 1: FROM node:20-alpine         CACHED             |
|   Layer 2: WORKDIR /app                CACHED             |
|   Layer 3: COPY package.json .         CACHED             |
|   Layer 4: RUN npm install             CACHED             |
|   Layer 5: COPY . .                    INVALIDATED        |
|   Layer 6: RUN npm run build           REBUILT (no cache)  |
|   Layer 7: CMD ["node", "server.js"]   REBUILT (no cache)  |
|                                                            |
|   Changing source code (Layer 5) does NOT invalidate       |
|   the npm install (Layer 4) because it comes BEFORE.       |
+-----------------------------------------------------------+
```

### Strategy 1: Copy Dependency Files First

```dockerfile
# GOOD — dependency installation is cached unless package.json changes
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./   # Changes rarely
RUN npm ci                                # Cached most of the time
COPY . .                                  # Changes often
RUN npm run build
```

```dockerfile
# BAD — npm install runs every time ANY file changes
FROM node:20-alpine
WORKDIR /app
COPY . .                                  # Invalidated on every change
RUN npm ci                                # Never cached
RUN npm run build
```

### Strategy 2: Separate Rarely-Changing Layers

```dockerfile
FROM python:3.12-alpine

# Layer 1: System dependencies (change very rarely)
RUN apk add --no-cache libpq-dev

# Layer 2: Python dependencies (change occasionally)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 3: Application code (changes often)
COPY . .

CMD ["python", "server.py"]
```

Order layers from **least frequently changed** to **most frequently changed**.

### Strategy 3: Combine Related RUN Commands

```dockerfile
# BAD — three separate layers
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# GOOD — one layer, and the cleanup actually saves space
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
```

When you delete files in a separate `RUN` instruction, the files still exist in the earlier layer. Combining them into one `RUN` means the deleted files never appear in the final layer.

---

## Before and After: Complete Optimization Example

Let us take a real-world Node.js application and optimize it step by step.

### Before: Unoptimized (1.1 GB)

```dockerfile
FROM node:20
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

**Problems:**

1. Uses `node:20` (full Debian — 1.1 GB base)
2. Copies everything (including `.git`, `node_modules`, tests)
3. No `.dockerignore`
4. Installs dev dependencies in the final image
5. Runs as root
6. No multi-stage build

### After: Optimized (85 MB)

```dockerfile
# syntax=docker/dockerfile:1

# Stage 1: Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Stage 2: Build
FROM deps AS builder
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS production
WORKDIR /app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy only production dependencies
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production && \
    npm cache clean --force

# Copy built application from builder stage
COPY --from=builder /app/dist ./dist

# Set ownership and switch to non-root user
RUN chown -R appuser:appgroup /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))"

EXPOSE 3000
CMD ["node", "dist/server.js"]
```

**.dockerignore:**

```
.git
node_modules
dist
test
docs
*.md
.env
.vscode
Dockerfile
docker-compose*
.dockerignore
coverage
.nyc_output
```

### Size Comparison

```
+-----------------------------------------------------------+
|              Before vs After                               |
|                                                            |
|   Before:                           After:                 |
|   +---------------------------+    +---------------------+ |
|   | node:20 base     1,100 MB|    | node:20-alpine  135MB| |
|   | ALL node_modules   200 MB|    | Prod modules     40MB| |
|   | Source code          5 MB|    | dist/ only        5MB| |
|   | .git               150 MB|    | (no .git)            | |
|   | Tests               50 MB|    | (no tests)           | |
|   | Docs                30 MB|    | (no docs)            | |
|   +---------------------------+    +---------------------+ |
|   TOTAL:            ~1,535 MB      TOTAL:           ~85 MB  |
|                                                            |
|   Reduction: 94%                                           |
+-----------------------------------------------------------+
```

### What Changed and Why

| Optimization                    | Size Saved | How                                    |
|--------------------------------|-----------|----------------------------------------|
| Alpine base instead of full     | ~965 MB   | `node:20-alpine` vs `node:20`          |
| Multi-stage build               | ~255 MB   | Dev deps and source code excluded       |
| `.dockerignore`                 | ~200 MB   | `.git`, tests, docs not sent to daemon  |
| Production-only dependencies    | ~160 MB   | `npm ci --only=production`              |
| Cache mounts                    | 0 MB      | Faster builds, no size change           |
| Non-root user                   | 0 MB      | Security, no size change                |
| Health check                    | 0 MB      | Reliability, no size change             |

---

## Common Mistakes

### Mistake 1: Not Using .dockerignore

Without `.dockerignore`, your `.git` directory (often 100+ MB) and `node_modules` (often 200+ MB) are sent to the Docker daemon and potentially copied into the image.

**Fix:** Always create a `.dockerignore` file. Start with the comprehensive example in this chapter.

### Mistake 2: Using the Full Base Image

```dockerfile
FROM python:3.12    # 1 GB
```

**Fix:**

```dockerfile
FROM python:3.12-alpine    # 55 MB
```

### Mistake 3: Installing Dev Dependencies in Production

```dockerfile
RUN npm install    # Installs EVERYTHING, including dev deps
```

**Fix:**

```dockerfile
RUN npm ci --only=production    # Only what your app needs to run
```

### Mistake 4: Deleting Files in a Separate RUN Layer

```dockerfile
COPY big-file.tar.gz .        # Layer 1: 500 MB
RUN tar xf big-file.tar.gz    # Layer 2: 500 MB (extracted)
RUN rm big-file.tar.gz        # Layer 3: rm saves nothing! Layer 1 still has it.
```

**Fix:** Do it all in one layer:

```dockerfile
RUN curl -O https://example.com/big-file.tar.gz && \
    tar xf big-file.tar.gz && \
    rm big-file.tar.gz
```

Or use multi-stage builds.

### Mistake 5: Copying Source Code Before Installing Dependencies

```dockerfile
COPY . .               # Invalidated on EVERY code change
RUN npm ci             # Reinstalls dependencies EVERY time
```

**Fix:**

```dockerfile
COPY package*.json ./  # Only invalidated when dependencies change
RUN npm ci             # Cached unless package.json changes
COPY . .               # Source code changes do not invalidate npm ci
```

---

## Best Practices

1. **Use Alpine or slim base images** — Start small, only add what you need
2. **Use multi-stage builds** — Keep build tools and dev dependencies out of the final image
3. **Write a comprehensive `.dockerignore`** — Exclude `.git`, `node_modules`, tests, docs
4. **Copy dependency files before source code** — Maximize layer cache hits
5. **Combine RUN instructions** — Avoid files in intermediate layers that waste space
6. **Use BuildKit cache mounts** — Speed up package installation with persistent caches
7. **Analyze with dive** — Find wasted space and unexpected files
8. **Use `--no-install-recommends`** (apt) or `--no-cache` (apk) — Skip optional packages
9. **Clean up in the same layer** — Remove package manager caches in the same RUN instruction
10. **Consider distroless for production** — Minimum possible attack surface

---

## Quick Summary

Optimizing Docker images reduces pull times, storage costs, CI/CD duration, and security vulnerabilities. Tools like dive reveal what is inside each layer and where space is wasted. Distroless and Alpine base images provide dramatically smaller foundations. Multi-stage builds separate the build environment from the runtime environment, excluding dev dependencies and build tools. A well-crafted `.dockerignore` prevents large or sensitive files from entering the build context. BuildKit features like parallel stage execution, cache mounts, and secret mounts make builds faster and more secure. Layer ordering — placing rarely-changing instructions before frequently-changing ones — maximizes cache efficiency. Together, these techniques can reduce a 1.5 GB image to under 100 MB.

---

## Key Points

- **Image size directly impacts** pull speed, storage costs, CI/CD time, and security
- **dive** analyzes image layers and shows wasted space
- **Distroless images** include only your app and runtime — no shell, no package manager
- **Alpine variants** are 5-20x smaller than full images
- **Multi-stage builds** keep build tools out of the final image
- **`.dockerignore`** prevents large files (`.git`, `node_modules`) from entering the build
- **BuildKit** enables parallel builds, cache mounts, and secret mounts
- **Layer order matters** — put rarely-changing instructions first for better caching
- **Combine RUN commands** to avoid files persisting in intermediate layers
- **Copy dependency files before source code** so dependency installation is cached

---

## Practice Questions

1. Why does deleting a file in a separate RUN layer NOT reduce the image size? How can you avoid this problem?

2. What is the difference between `node:20`, `node:20-slim`, and `node:20-alpine`? When would you choose each?

3. What does `dive` show you about a Docker image? How would you use it to identify optimization opportunities?

4. Explain why `COPY package.json .` followed by `RUN npm ci` followed by `COPY . .` is more efficient than `COPY . .` followed by `RUN npm ci`. What caching behavior is different?

5. What are BuildKit cache mounts? How do they speed up Docker builds?

---

## Exercises

### Exercise 1: Analyze and Optimize

1. Build an unoptimized image using the "Before" Dockerfile from this chapter (use any Node.js app, or create a simple one)
2. Run `dive` on the image and note the total size and efficiency score
3. Apply each optimization one at a time:
   a. Add `.dockerignore` → rebuild → check size
   b. Switch to Alpine base → rebuild → check size
   c. Add multi-stage build → rebuild → check size
   d. Add production-only dependencies → rebuild → check size
4. Record the size after each step to see the cumulative impact

### Exercise 2: Compare Base Images

1. Build the same application using four different base images:
   - `FROM node:20`
   - `FROM node:20-slim`
   - `FROM node:20-alpine`
   - `FROM gcr.io/distroless/nodejs20-debian12` (with multi-stage)
2. Compare the sizes with `docker images`
3. Run `trivy image` on each to compare vulnerability counts
4. Try to `docker exec -it container sh` on each — which ones allow it?

### Exercise 3: BuildKit Features

1. Build an image WITHOUT BuildKit: `DOCKER_BUILDKIT=0 docker build -t myapp-legacy .`
2. Build the same image WITH BuildKit: `DOCKER_BUILDKIT=1 docker build -t myapp-buildkit .`
3. Compare build times
4. Add cache mounts for your package manager and rebuild twice — note how the second build is faster
5. Use a multi-stage Dockerfile with two independent build stages and observe BuildKit building them in parallel

---

## What Is Next?

Congratulations! You have now covered the full journey of Docker — from understanding what containers are, through building and optimizing images, to deploying them in production with orchestration. You know how to:

- Build efficient Docker images with multi-stage builds
- Manage configuration with environment variables and volumes
- Compose multi-container applications
- Push images to registries with proper tagging
- Automate builds with CI/CD
- Secure and harden containers
- Run containers reliably in production
- Orchestrate across multiple machines with Docker Swarm
- Optimize images for speed, security, and cost

The next step in your container journey is to explore **Kubernetes** for large-scale orchestration, or to deepen your Docker skills by applying everything in this book to a real project. Build something, deploy it, and iterate. The best learning happens by doing.
