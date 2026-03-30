# Chapter 22: Docker Security

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand why Docker security matters and common attack vectors
- Run containers as non-root users with the USER instruction
- Use read-only filesystems to prevent tampering
- Manage sensitive data with Docker secrets
- Scan images for vulnerabilities using Docker Scout and Trivy
- Choose trusted base images to reduce risk
- Minimize the attack surface using distroless and minimal images
- Prevent sensitive data from leaking into image layers
- Enable Docker Content Trust for image verification
- Follow a comprehensive security checklist

---

## Why This Chapter Matters

Imagine you leave your house with the front door wide open, all windows unlocked, your car keys on the dashboard, and your bank statements on the porch. Nobody forced you to do this — you just did not think about security.

Many Docker deployments are exactly like this. Containers run as root (the all-powerful superuser), images contain known vulnerabilities, passwords are baked into image layers, and anyone can push to the registry. Each of these is an open door for attackers.

Docker containers are NOT sandboxes. They share the host's kernel. A container running as root with the wrong configuration can access the host system, read other containers' data, or become a launching point for attacks.

Security is not something you add later. It must be part of every Dockerfile, every deployment, and every decision you make.

---

## Running as Non-Root

By default, processes inside a Docker container run as **root** — the superuser with unlimited permissions. This is the single most common Docker security mistake.

### Why Root Is Dangerous

```
+-----------------------------------------------------------+
|              The Root Problem                              |
|                                                            |
|   Container running as root:                               |
|   +--------------------------------------------------+     |
|   | root (UID 0)                                     |     |
|   |                                                  |     |
|   | Can read/write ALL files in the container         |     |
|   | Can install software                             |     |
|   | Can modify system settings                        |     |
|   | If the container "escapes," it is root on HOST   |     |
|   +--------------------------------------------------+     |
|                                                            |
|   Container running as non-root:                           |
|   +--------------------------------------------------+     |
|   | appuser (UID 1001)                               |     |
|   |                                                  |     |
|   | Can only read/write its own files                |     |
|   | Cannot install software                           |     |
|   | Cannot modify system settings                     |     |
|   | If it "escapes," it is a nobody on the HOST      |     |
|   +--------------------------------------------------+     |
+-----------------------------------------------------------+
```

### The USER Instruction

The `USER` instruction in a Dockerfile sets which user the container process runs as.

```dockerfile
# Dockerfile
FROM node:20-alpine

# Create a non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set the working directory
WORKDIR /app

# Copy files and install dependencies as root (needed for npm install)
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Start the application
CMD ["node", "server.js"]
```

**Line-by-line explanation:**

- `addgroup -S appgroup` — Creates a system group called "appgroup." The `-S` flag means "system group" (no home directory needed)
- `adduser -S appuser -G appgroup` — Creates a system user called "appuser" in the "appgroup" group
- `RUN chown -R appuser:appgroup /app` — Changes ownership of `/app` so the non-root user can read the files
- `USER appuser` — All subsequent commands (and the final CMD) run as "appuser" instead of root

### Verify It Works

```bash
# Build the image
docker build -t myapp-secure .

# Check which user the container runs as
docker run --rm myapp-secure whoami
```

**Output:**

```
appuser
```

```bash
# Try to do something only root can do
docker run --rm myapp-secure cat /etc/shadow
```

**Output:**

```
cat: can't open '/etc/shadow': Permission denied
```

The non-root user cannot access sensitive system files. This is exactly what we want.

### Override at Runtime

Even if the Dockerfile uses `USER root`, you can force a non-root user at runtime:

```bash
docker run --user 1001:1001 myapp
```

This runs the container as UID 1001, regardless of what the Dockerfile specifies.

---

## Read-Only Filesystem

A **read-only filesystem** prevents any process inside the container from writing to the filesystem. If an attacker gains access, they cannot modify application files, install malware, or alter configuration.

### Using --read-only

```bash
docker run --read-only myapp
```

**What happens:** Any attempt to write to the filesystem fails:

```bash
docker run --read-only myapp touch /tmp/test.txt
```

**Output:**

```
touch: cannot touch '/tmp/test.txt': Read-only file system
```

### Allowing Specific Writable Directories

Most applications need to write to some directories (temp files, logs, caches). Use `--tmpfs` to create writable temporary directories:

```bash
docker run --read-only \
  --tmpfs /tmp \
  --tmpfs /var/log \
  myapp
```

**What this does:**

- The entire filesystem is read-only
- `/tmp` and `/var/log` are writable, but stored in memory (not on disk)
- Data in `--tmpfs` directories is lost when the container stops

### In Docker Compose

```yaml
services:
  web:
    image: myapp:1.0.0
    read_only: true
    tmpfs:
      - /tmp
      - /var/log
```

```
+-----------------------------------------------------------+
|              Read-Only Filesystem                          |
|                                                            |
|   +---------------------------------------------------+   |
|   | Container Filesystem                              |   |
|   |                                                   |   |
|   |   /app          READ-ONLY  (application code)     |   |
|   |   /etc          READ-ONLY  (configuration)        |   |
|   |   /usr          READ-ONLY  (system files)         |   |
|   |   /tmp          WRITABLE   (temporary files)      |   |
|   |   /var/log      WRITABLE   (log files)            |   |
|   |                                                   |   |
|   |   Attacker cannot modify /app or install tools    |   |
|   +---------------------------------------------------+   |
+-----------------------------------------------------------+
```

---

## Docker Secrets

**Secrets** are sensitive data that your application needs but should never be stored in plain text inside an image. Examples include:

- Database passwords
- API keys
- TLS certificates
- Encryption keys

### The Wrong Way: Environment Variables in Dockerfiles

```dockerfile
# NEVER DO THIS
ENV DATABASE_PASSWORD=SuperSecret123
```

This bakes the password into the image. Anyone who pulls the image can see it:

```bash
docker inspect myapp | grep DATABASE_PASSWORD
# Output: "DATABASE_PASSWORD=SuperSecret123"
```

Even if you delete the variable in a later layer, it is still visible in the image history:

```bash
docker history myapp
```

### The Wrong Way: Copying Secret Files

```dockerfile
# NEVER DO THIS
COPY .env /app/.env
```

The `.env` file is now part of the image layer. Even if you delete it in a later `RUN` instruction, it exists in an earlier layer and can be extracted.

### The Right Way: Docker Swarm Secrets

Docker Swarm has built-in secrets management (covered more in Chapter 24):

```bash
# Create a secret
echo "SuperSecret123" | docker secret create db_password -

# Use it in a service
docker service create \
  --name webapp \
  --secret db_password \
  myapp:1.0.0
```

Inside the container, the secret is available as a file at `/run/secrets/db_password`:

```bash
# In your application code
cat /run/secrets/db_password
# Output: SuperSecret123
```

### The Right Way: Environment Variables at Runtime

Pass secrets at runtime, not build time:

```bash
docker run -e DATABASE_PASSWORD=SuperSecret123 myapp
```

Or use an environment file:

```bash
# .env file (NOT committed to Git, NOT copied into the image)
DATABASE_PASSWORD=SuperSecret123
API_KEY=abc123def456

docker run --env-file .env myapp
```

### The Right Way: Docker Compose Secrets

```yaml
# docker-compose.yml
services:
  web:
    image: myapp:1.0.0
    secrets:
      - db_password
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

The secret file is mounted read-only at `/run/secrets/db_password` inside the container.

```
+-----------------------------------------------------------+
|              Secrets: Wrong vs Right                       |
|                                                            |
|   WRONG:                                                   |
|   +---------------------+                                  |
|   | Dockerfile          |  ENV PASSWORD=secret             |
|   | Image Layer         |  Password baked in forever       |
|   +---------------------+                                  |
|                                                            |
|   RIGHT:                                                   |
|   +---------------------+       +----------------+         |
|   | Dockerfile          |       | Runtime        |         |
|   | No secrets inside   | <---- | -e PASSWORD=.. |         |
|   +---------------------+       | --secret ...   |         |
|                                 +----------------+         |
|                                                            |
|   Secrets are injected at runtime, never stored in image.  |
+-----------------------------------------------------------+
```

---

## Image Scanning

**Image scanning** analyzes your Docker image for known security vulnerabilities. Think of it as a virus scan for your Docker images.

### What Scanners Look For

- **CVEs** (Common Vulnerabilities and Exposures) — Known security bugs in software packages
- **Outdated packages** — Libraries with newer, patched versions available
- **Misconfigurations** — Insecure Dockerfile patterns
- **Malware** — Known malicious code

### Docker Scout

**Docker Scout** is Docker's built-in scanning tool.

```bash
# Scan a local image
docker scout cves myapp:1.0.0
```

**Sample output:**

```
    i New version 1.14.0 available (installed version is 1.13.1)
    ✓ Image stored for indexing
    ✗ Detected 3 vulnerable packages with a total of 12 vulnerabilities

   0C     3H     5M     4L  myapp:1.0.0

  Pkg          Installed  Fixed     Vulnerability     Severity
  curl         7.88.1     8.4.0     CVE-2023-38545   HIGH
  openssl      3.0.2      3.0.12    CVE-2023-5678    HIGH
  openssl      3.0.2      3.0.12    CVE-2023-5679    HIGH
  zlib         1.2.13     1.3       CVE-2023-45853   MEDIUM
```

**Reading the output:**

- `0C` — 0 Critical vulnerabilities
- `3H` — 3 High severity vulnerabilities
- `5M` — 5 Medium severity vulnerabilities
- `4L` — 4 Low severity vulnerabilities
- `Fixed` column — Shows which version fixes the vulnerability. Update to this version.

```bash
# Get recommendations for fixing vulnerabilities
docker scout recommendations myapp:1.0.0
```

### Trivy

**Trivy** is a popular open-source scanner by Aqua Security. It is fast, comprehensive, and free.

```bash
# Install Trivy (macOS)
brew install trivy

# Scan a Docker image
trivy image myapp:1.0.0
```

**Sample output:**

```
myapp:1.0.0 (alpine 3.18.4)
Total: 5 (UNKNOWN: 0, LOW: 2, MEDIUM: 2, HIGH: 1, CRITICAL: 0)

+---------+------------------+----------+---------+---------+
| Library | Vulnerability    | Severity | Version | Fixed   |
+---------+------------------+----------+---------+---------+
| curl    | CVE-2023-38545  | HIGH     | 7.88.1  | 8.4.0   |
| zlib    | CVE-2023-45853  | MEDIUM   | 1.2.13  | 1.3     |
| libxml2 | CVE-2023-45322  | MEDIUM   | 2.11.5  | 2.11.6  |
| busybox | CVE-2023-42365  | LOW      | 1.36.1  | 1.36.2  |
| musl    | CVE-2023-43789  | LOW      | 1.2.4   | 1.2.5   |
+---------+------------------+----------+---------+---------+
```

### Scanning in CI/CD

Add scanning to your CI/CD pipeline so vulnerabilities are caught before deployment:

```yaml
# In your GitHub Actions workflow
      - name: Scan image with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:1.0.0
          format: table
          exit-code: 1           # Fail the build if vulnerabilities found
          severity: CRITICAL,HIGH  # Only fail on critical and high
```

Setting `exit-code: 1` means the build **fails** if critical or high vulnerabilities are found, preventing the image from being pushed to the registry.

---

## Trusted Base Images

The base image you choose in your `FROM` instruction is the foundation of your container's security. A compromised or outdated base image undermines everything you build on top.

### Use Official Images

Official images are reviewed and maintained by Docker or the software vendor:

```dockerfile
# Good — official image
FROM node:20-alpine

# Risky — random user's image
FROM someguy/node:latest
```

### Pin Specific Versions

```dockerfile
# Bad — could change at any time
FROM node:latest

# Better — pinned to minor version
FROM node:20-alpine

# Best — pinned to exact version with digest
FROM node:20.10.0-alpine3.19@sha256:abc123...
```

The **digest** (`@sha256:...`) is a unique hash of the image. Even if someone overwrites the `20.10.0-alpine3.19` tag, the digest ensures you get the exact same image every time.

### Prefer Minimal Base Images

```
+-----------------------------------------------------------+
|              Base Image Comparison                         |
|                                                            |
|   Image              Size      Packages   Attack Surface   |
|   ---------------    ------    --------   ---------------  |
|   ubuntu:22.04       77 MB     ~400       Large            |
|   debian:bookworm    124 MB    ~300       Large            |
|   node:20            1.1 GB    ~600       Very large       |
|   node:20-slim       200 MB    ~150       Medium           |
|   node:20-alpine     130 MB    ~50        Small            |
|   gcr.io/distroless  ~20 MB    ~5         Tiny             |
|                                                            |
|   Fewer packages = fewer potential vulnerabilities.        |
+-----------------------------------------------------------+
```

---

## Minimizing the Attack Surface

The **attack surface** is everything in your container that an attacker could potentially exploit. The smaller the attack surface, the fewer ways an attacker can get in.

### Remove Unnecessary Tools

```dockerfile
# After installing build dependencies, remove them
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    npm ci --only=production && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
```

Or better yet, use **multi-stage builds** so build tools never appear in the final image:

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production (no build tools)
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/server.js"]
```

### Distroless Images

**Distroless images** from Google contain ONLY your application and its runtime dependencies. No shell, no package manager, no system utilities.

```dockerfile
# Multi-stage build with distroless final image
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

FROM gcr.io/distroless/nodejs20-debian12
WORKDIR /app
COPY --from=builder /app .
CMD ["server.js"]
```

**Why distroless is more secure:**

- No shell → Attackers cannot open a shell inside the container
- No package manager → Attackers cannot install additional tools
- No utilities (curl, wget, etc.) → Attackers cannot download payloads
- Dramatically fewer packages → Dramatically fewer vulnerabilities

**The trade-off:** Debugging is harder because you cannot `docker exec -it container sh`. For debugging, use a sidecar container or multi-stage build with a debug target.

---

## No Sensitive Data in Images

Every layer of a Docker image is permanent and inspectable. Deleting a file in a later layer does NOT remove it from earlier layers.

### The Layer Problem

```dockerfile
# This is INSECURE even though we delete the file
COPY credentials.json /app/credentials.json
RUN process-credentials.sh
RUN rm /app/credentials.json  # File is STILL in the layer above!
```

```
+-----------------------------------------------------------+
|              Image Layers Are Permanent                    |
|                                                            |
|   Layer 3:  RUN rm credentials.json   (file "removed")    |
|   Layer 2:  RUN process-credentials   (file used)         |
|   Layer 1:  COPY credentials.json     (file EXISTS here!) |
|                                                            |
|   An attacker can extract Layer 1 and read the file.       |
|   docker history and docker save reveal all layers.        |
+-----------------------------------------------------------+
```

### How to Check for Leaked Secrets

```bash
# View all layers and commands
docker history myapp:1.0.0

# Export and inspect layers
docker save myapp:1.0.0 -o image.tar
tar xf image.tar
# Each layer is a separate tar file you can inspect
```

### Rules for Keeping Secrets Out

1. **Use `.dockerignore`** to exclude sensitive files from the build context:

```
# .dockerignore
.env
*.pem
*.key
credentials.json
secrets/
.git
```

2. **Use multi-stage builds** to ensure build-time secrets do not appear in the final image:

```dockerfile
FROM alpine AS builder
# Use secrets only in the build stage
COPY credentials.json .
RUN process-with-credentials.sh

FROM alpine
# Final image has NO credentials
COPY --from=builder /app/output ./output
```

3. **Use BuildKit secrets** for build-time secrets that should never be in any layer:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci --only=production
```

```bash
docker build --secret id=npmrc,src=.npmrc -t myapp .
```

The `.npmrc` file is available during the build but is NOT stored in any layer.

---

## Docker Content Trust

**Docker Content Trust (DCT)** ensures that the images you pull are signed by the publisher and have not been tampered with.

### The Problem Without DCT

```
+-----------------------------------------------------------+
|              Man-in-the-Middle Attack                      |
|                                                            |
|   You:  docker pull myapp:1.0                              |
|                |                                           |
|                v                                           |
|   Attacker:  Intercepts the pull and serves a              |
|              modified image with malware.                   |
|                |                                           |
|                v                                           |
|   You run the malware thinking it is your app.             |
+-----------------------------------------------------------+
```

### Enabling Docker Content Trust

```bash
# Enable for the current shell session
export DOCKER_CONTENT_TRUST=1

# Now Docker refuses to pull unsigned images
docker pull unsigned-image:latest
# Error: remote trust data does not exist

# Pull a signed image (works fine)
docker pull docker/trusttest:latest
```

### Signing Your Images

```bash
# Enable content trust
export DOCKER_CONTENT_TRUST=1

# Push — Docker will ask you to create signing keys
docker push myusername/myapp:1.0.0
```

The first time, Docker generates a root key and a repository key. Store these keys safely — losing them means you cannot sign future images for that repository.

### When to Use DCT

- **Production environments** — Always verify image authenticity
- **Regulated industries** — Compliance often requires image signing
- **Open source projects** — Lets users verify they are running the official image

---

## Security Checklist

Use this checklist for every Docker deployment:

### Dockerfile Security

```
[ ] Run as non-root user (USER instruction)
[ ] Use a minimal base image (alpine, slim, or distroless)
[ ] Pin base image versions (avoid :latest)
[ ] No secrets in ENV instructions
[ ] No secrets copied into layers
[ ] Use .dockerignore to exclude sensitive files
[ ] Use multi-stage builds to exclude build tools
[ ] Remove unnecessary packages after installation
[ ] Set HEALTHCHECK for monitoring
```

### Runtime Security

```
[ ] Use --read-only filesystem where possible
[ ] Pass secrets via runtime environment or Docker secrets
[ ] Drop unnecessary Linux capabilities (--cap-drop ALL)
[ ] Limit memory and CPU (--memory, --cpus)
[ ] Use --no-new-privileges to prevent privilege escalation
[ ] Set restart policy appropriately
[ ] Do not mount the Docker socket into containers
[ ] Use network segmentation (separate Docker networks)
```

### Registry Security

```
[ ] Use private repositories for proprietary images
[ ] Enable vulnerability scanning on the registry
[ ] Use access tokens instead of passwords
[ ] Enable Docker Content Trust for signed images
[ ] Set up image retention policies
[ ] Regularly rotate access tokens
```

### CI/CD Security

```
[ ] Scan images for vulnerabilities in the pipeline
[ ] Fail builds on critical/high vulnerabilities
[ ] Never hardcode credentials in workflow files
[ ] Do not push images from pull requests
[ ] Pin CI/CD action versions
[ ] Use separate tokens for CI/CD (not personal credentials)
```

### Advanced Runtime Hardening

```bash
# Drop ALL Linux capabilities and add back only what you need
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp

# Prevent privilege escalation
docker run --security-opt no-new-privileges myapp

# Limit resources
docker run --memory 512m --cpus 1.0 myapp

# Read-only filesystem with specific writable paths
docker run --read-only --tmpfs /tmp myapp
```

---

## Common Mistakes

### Mistake 1: Running as Root Because "It Is Easier"

```dockerfile
# The entire Dockerfile runs as root by default
FROM node:20
WORKDIR /app
COPY . .
RUN npm install
CMD ["node", "server.js"]
# No USER instruction — runs as root!
```

**Fix:** Always add a USER instruction before the CMD.

### Mistake 2: Baking Passwords into ENV

```dockerfile
# NEVER DO THIS
ENV DB_PASSWORD=MyPassword123
```

**Fix:** Pass at runtime with `-e` or use Docker secrets.

### Mistake 3: Using a Full Operating System as Base Image

```dockerfile
# Unnecessary — includes compilers, editors, and hundreds of tools
FROM ubuntu:22.04
```

**Fix:** Use `alpine`, `slim`, or `distroless` variants.

### Mistake 4: Not Scanning Images

Building an image and pushing it without scanning is like shipping a product without quality control.

**Fix:** Add `trivy image` or `docker scout cves` to your CI/CD pipeline.

### Mistake 5: Mounting the Docker Socket

```bash
# EXTREMELY DANGEROUS — gives the container full control of Docker
docker run -v /var/run/docker.sock:/var/run/docker.sock myapp
```

This gives the container the ability to create, modify, and delete ANY container on the host. Only do this when absolutely necessary (like for monitoring tools) and never in production without understanding the risks.

---

## Best Practices

1. **Always run as non-root** — Use the `USER` instruction in every Dockerfile
2. **Use minimal base images** — Fewer packages means fewer vulnerabilities
3. **Scan images regularly** — Add scanning to CI/CD and run it on a schedule
4. **Never store secrets in images** — Use runtime injection or Docker secrets
5. **Use read-only filesystems** — Prevent tampering with application files
6. **Drop unnecessary capabilities** — Use `--cap-drop ALL` and add back only what you need
7. **Pin base image versions** — Avoid unexpected changes from moving tags
8. **Use multi-stage builds** — Keep build tools out of production images
9. **Enable Docker Content Trust** — Verify image authenticity
10. **Keep images updated** — Rebuild regularly to pick up security patches

---

## Quick Summary

Docker security starts with running containers as non-root users and using minimal base images to reduce the attack surface. Read-only filesystems prevent tampering, while Docker secrets keep sensitive data out of image layers. Image scanning with tools like Docker Scout and Trivy catches known vulnerabilities before deployment. Distroless images provide the smallest possible attack surface by including only your application and its runtime. Docker Content Trust verifies that images have not been tampered with. Following a security checklist ensures you do not miss any important hardening step.

---

## Key Points

- **Never run as root** — Use the `USER` instruction to create and switch to a non-root user
- **Read-only filesystems** (`--read-only`) prevent processes from modifying the container
- **Docker secrets** inject sensitive data at runtime, never storing it in image layers
- **Image scanning** (Docker Scout, Trivy) finds known vulnerabilities in your images
- **Minimal base images** (alpine, slim, distroless) reduce the number of potential vulnerabilities
- **Multi-stage builds** keep build tools and secrets out of the final image
- **`.dockerignore`** prevents sensitive files from entering the build context
- **Docker Content Trust** verifies that images are signed and unmodified
- **Drop capabilities** (`--cap-drop ALL`) removes unnecessary Linux permissions
- Image layers are **permanent** — deleting a file in a later layer does not remove it from earlier layers

---

## Practice Questions

1. Why is running a container as root dangerous? What could happen if a root container has a vulnerability that allows "container escape"?

2. You need to pass a database password to your container. Describe two WRONG ways and two RIGHT ways to do this.

3. What is a distroless image? Why is it more secure than a regular base image? What is the trade-off?

4. You run `docker history myapp` and see a layer that contains `COPY credentials.json /app/`. The next layer shows `RUN rm /app/credentials.json`. Is the credentials file still accessible? Why or why not?

5. What does `--cap-drop ALL` do? Why would you want to use it?

---

## Exercises

### Exercise 1: Secure a Dockerfile

Start with this insecure Dockerfile:

```dockerfile
FROM node:20
WORKDIR /app
ENV API_KEY=sk-secret-key-12345
COPY . .
RUN npm install
CMD ["node", "server.js"]
```

Fix all security issues:
1. Add a non-root user
2. Remove the secret from ENV
3. Use an alpine base image
4. Add a `.dockerignore` file
5. Use multi-stage build to minimize the final image

### Exercise 2: Scan and Fix Vulnerabilities

1. Build a Docker image using `FROM node:20`
2. Scan it with `docker scout cves` or `trivy image`
3. Note the number and severity of vulnerabilities
4. Rebuild using `FROM node:20-alpine`
5. Scan again and compare the results
6. Try `FROM gcr.io/distroless/nodejs20-debian12` and scan a third time

### Exercise 3: Read-Only Container

1. Run a container with `--read-only`: `docker run --read-only nginx`
2. It will likely fail. Read the error message.
3. Add `--tmpfs` flags for the directories nginx needs to write to
4. Verify the container runs successfully
5. Try to create a file in a non-tmpfs directory to confirm it is read-only

---

## What Is Next?

Security is one piece of running containers in production. In the next chapter, we cover **Docker in Production** — resource limits to prevent containers from consuming all available memory, restart policies for self-healing, logging drivers for centralized log management, monitoring with Prometheus, and graceful shutdown handling. These are the operational skills that separate development experiments from production-ready deployments.
