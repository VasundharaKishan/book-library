# Chapter 6: Your First Dockerfile

## What You Will Learn

By the end of this chapter, you will be able to:

- Explain what a Dockerfile is and why it exists
- Write a Dockerfile from scratch using common instructions
- Understand each instruction: FROM, WORKDIR, COPY, RUN, CMD, ENTRYPOINT, and EXPOSE
- Build a Docker image using `docker build`
- Understand what build context means and how to control it
- Use a `.dockerignore` file to exclude unnecessary files
- Explain how Docker layer caching works and why it matters
- Build and run a complete Node.js application using a Dockerfile

## Why This Chapter Matters

Up until now, you have been pulling images that other people created. That is like eating at restaurants -- someone else made the food for you. But what if you want to cook your own meal? What if you have your own application and you want to package it into a Docker image?

That is where the Dockerfile comes in. It is the recipe that tells Docker exactly how to build your custom image. Every professional developer who works with Docker writes Dockerfiles. It is one of the most important skills in modern software development.

Without Dockerfiles, you would have to manually set up every container by hand. Imagine having to install software, copy files, and configure settings every single time you wanted to run your application. A Dockerfile automates all of that into a single, repeatable file.

---

## What Is a Dockerfile?

A **Dockerfile** is a plain text file that contains a series of instructions. Each instruction tells Docker to perform a specific action, like installing software or copying files. When you run `docker build`, Docker reads these instructions one by one and creates an image.

Think of it like a cooking recipe:

```
RECIPE: Chocolate Cake

START WITH:    A basic cake pan (the base)
ADD:           2 cups flour
ADD:           1 cup sugar
MIX IN:        3 eggs
BAKE AT:       350 degrees for 30 minutes
SERVE:         On a plate with frosting
```

A Dockerfile works the same way:

```
Dockerfile: My Application

START WITH:    A Linux operating system with Node.js installed
SET UP:        A working directory inside the container
COPY:          My application code into the container
INSTALL:       My application dependencies
EXPOSE:        The port my app listens on
RUN:           My application when the container starts
```

Here is what a real Dockerfile looks like:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

Do not worry if this looks confusing right now. We will go through every single line in detail.

### Key Rules About Dockerfiles

1. The file must be named exactly `Dockerfile` (capital D, no file extension)
2. Each instruction is written in UPPERCASE by convention (FROM, RUN, COPY, etc.)
3. Docker executes instructions from top to bottom, in order
4. Each instruction creates a new **layer** in the image (more on this later)

---

## The FROM Instruction: Your Starting Point

Every Dockerfile must start with a `FROM` instruction. It tells Docker which base image to use as the foundation.

**Real-life analogy:** If you are building a house, FROM is like choosing the foundation. You would not pour concrete from scratch every time. Instead, you start with an existing foundation and build on top of it.

### Syntax

```dockerfile
FROM image_name:tag
```

### Examples

```dockerfile
# Start with Ubuntu Linux
FROM ubuntu:22.04

# Start with a lightweight Linux distribution
FROM alpine:3.18

# Start with Node.js pre-installed
FROM node:18-alpine

# Start with Python pre-installed
FROM python:3.11-slim

# Start with Java pre-installed
FROM eclipse-temurin:17-jre-alpine
```

### What Happens Behind the Scenes

When Docker encounters the FROM instruction:

```
+--------------------------------------------------+
|          What FROM Does                          |
+--------------------------------------------------+
|                                                  |
|  FROM node:18-alpine                             |
|       |                                          |
|       v                                          |
|  1. Check if image exists locally                |
|       |                                          |
|       v                                          |
|  2. If not, pull from Docker Hub                 |
|       |                                          |
|       v                                          |
|  3. Use it as the starting layer                 |
|       |                                          |
|       v                                          |
|  4. All subsequent instructions build on top     |
|                                                  |
+--------------------------------------------------+
```

### Choosing a Base Image

The base image you choose matters a lot. Here is a comparison:

```
+-------------------+----------+---------------------------+
| Base Image        | Size     | What Is Included          |
+-------------------+----------+---------------------------+
| ubuntu:22.04      | ~77 MB   | Full Ubuntu OS            |
| debian:12-slim    | ~74 MB   | Minimal Debian OS         |
| alpine:3.18       | ~7 MB    | Tiny Linux OS             |
| node:18           | ~350 MB  | Debian + Node.js          |
| node:18-slim      | ~180 MB  | Slim Debian + Node.js     |
| node:18-alpine    | ~120 MB  | Alpine + Node.js          |
| scratch           | 0 MB     | Completely empty          |
+-------------------+----------+---------------------------+
```

**The `-alpine` variants** use Alpine Linux as their base. Alpine is a tiny Linux distribution (about 7 MB) that is perfect for containers because it keeps your images small.

**The `-slim` variants** remove unnecessary packages from the standard image, giving you a middle ground between full and Alpine.

**The `scratch` image** is completely empty. It is used for compiled languages like Go where the binary includes everything it needs.

---

## The WORKDIR Instruction: Setting Your Working Directory

`WORKDIR` sets the working directory inside the container. All subsequent instructions (like COPY, RUN, and CMD) will execute relative to this directory.

**Real-life analogy:** WORKDIR is like walking into a specific room in your house before you start working. If you say `WORKDIR /app`, it is like saying "go to the /app room. Everything I do from now on happens in this room."

### Syntax

```dockerfile
WORKDIR /path/to/directory
```

### Example

```dockerfile
FROM node:18-alpine

# Set the working directory to /app
WORKDIR /app

# Now all paths are relative to /app
# This copies package.json to /app/package.json
COPY package.json .
```

### What If the Directory Does Not Exist?

Docker creates it automatically. You do not need to run `mkdir` first.

```dockerfile
# Docker will create /app/src if it does not exist
WORKDIR /app/src
```

### Multiple WORKDIR Instructions

You can use WORKDIR multiple times. Relative paths build on the previous WORKDIR:

```dockerfile
WORKDIR /app
# Current directory: /app

WORKDIR src
# Current directory: /app/src

WORKDIR ../config
# Current directory: /app/config
```

---

## The COPY Instruction: Adding Your Files

`COPY` copies files and directories from your computer (the build context) into the image.

**Real-life analogy:** COPY is like packing items from your desk into a moving box. You pick specific items from your desk (your computer) and place them in the box (the container image).

### Syntax

```dockerfile
COPY source destination
```

### Examples

```dockerfile
# Copy a single file to the current WORKDIR
COPY package.json .

# Copy a single file to a specific location
COPY package.json /app/package.json

# Copy everything from the current directory
COPY . .

# Copy a specific directory
COPY src/ /app/src/

# Copy multiple files
COPY package.json package-lock.json ./
```

### Understanding the Dot (.)

The dot `.` means "current directory." But which current directory?

- **On the left side (source):** The `.` refers to the build context directory on your computer
- **On the right side (destination):** The `.` refers to the WORKDIR inside the container

```dockerfile
WORKDIR /app

# Source: everything in the build context on your computer
# Destination: /app/ inside the container
COPY . .
```

### The --chown Flag

You can change the ownership of copied files:

```dockerfile
COPY --chown=node:node package.json .
```

This makes the `node` user (instead of root) the owner of the file.

---

## The RUN Instruction: Executing Commands During Build

`RUN` executes a command during the image build process. It is commonly used to install software packages, create directories, or download files.

**Real-life analogy:** RUN is like following a step in a recipe while cooking. "Mix the ingredients" happens during cooking time, not when you serve the dish. Similarly, RUN commands happen during build time, not when the container starts.

### Syntax

There are two forms:

```dockerfile
# Shell form (runs in /bin/sh -c)
RUN command

# Exec form (runs directly, no shell processing)
RUN ["executable", "param1", "param2"]
```

### Examples

```dockerfile
# Install a package on Ubuntu/Debian
RUN apt-get update && apt-get install -y curl

# Install a package on Alpine
RUN apk add --no-cache curl

# Install Node.js dependencies
RUN npm install

# Create a directory
RUN mkdir -p /app/logs

# Download a file
RUN curl -o /app/data.json https://example.com/data.json
```

### Combining RUN Commands

Each RUN instruction creates a new layer. To keep your image small, combine related commands:

```dockerfile
# BAD: Three separate layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget

# GOOD: One layer
RUN apt-get update && \
    apt-get install -y curl wget && \
    rm -rf /var/lib/apt/lists/*
```

The backslash `\` at the end of a line means "this command continues on the next line." It makes long commands easier to read.

The `&&` means "run the next command only if the previous one succeeded."

---

## CMD vs ENTRYPOINT: What Runs When the Container Starts

This is where many beginners get confused. Both CMD and ENTRYPOINT define what happens when a container starts, but they work differently.

### CMD: The Default Command

`CMD` sets the default command that runs when a container starts. Users can override it easily.

**Real-life analogy:** CMD is like setting a default radio station in your car. You can always change the station, but if you just turn on the radio without thinking, it plays the default.

```dockerfile
# Shell form
CMD node server.js

# Exec form (preferred)
CMD ["node", "server.js"]
```

**Important:** There can only be one CMD instruction in a Dockerfile. If you write multiple CMD instructions, only the last one takes effect.

### Overriding CMD

When you run a container, you can override the CMD:

```bash
# Uses the default CMD from the Dockerfile
$ docker run my-app

# Overrides CMD with "node test.js"
$ docker run my-app node test.js

# Overrides CMD with a shell
$ docker run -it my-app /bin/sh
```

### ENTRYPOINT: The Fixed Command

`ENTRYPOINT` sets a command that always runs. It cannot be easily overridden.

**Real-life analogy:** ENTRYPOINT is like the ignition system in your car. No matter where you want to go, you always need to turn the key (or push the start button). The destination (CMD) might change, but the ignition (ENTRYPOINT) stays the same.

```dockerfile
ENTRYPOINT ["node"]
CMD ["server.js"]
```

With this setup:

```bash
# Runs: node server.js (ENTRYPOINT + CMD)
$ docker run my-app

# Runs: node test.js (ENTRYPOINT + override)
$ docker run my-app test.js

# Runs: node --version (ENTRYPOINT + override)
$ docker run my-app --version
```

### Comparison Table

```
+---------------+---------------------------+---------------------------+
| Feature       | CMD                       | ENTRYPOINT                |
+---------------+---------------------------+---------------------------+
| Purpose       | Default command/args      | Fixed command              |
| Override      | Easy (just add args)      | Requires --entrypoint     |
| Multiple      | Last one wins             | Last one wins              |
| Used for      | Flexible containers       | Single-purpose containers  |
| Common with   | General apps              | CLI tools, wrappers        |
+---------------+---------------------------+---------------------------+
```

### Using CMD and ENTRYPOINT Together

The most common pattern is to use both:

```dockerfile
# ENTRYPOINT defines the executable
ENTRYPOINT ["python"]

# CMD provides default arguments
CMD ["app.py"]
```

```
+--------------------------------------------------+
|     How ENTRYPOINT + CMD Work Together           |
+--------------------------------------------------+
|                                                  |
|  ENTRYPOINT: ["python"]   (the program)          |
|  CMD:        ["app.py"]   (default argument)     |
|                                                  |
|  docker run my-app                               |
|  => python app.py                                |
|                                                  |
|  docker run my-app test.py                       |
|  => python test.py   (CMD is overridden)         |
|                                                  |
|  docker run my-app --version                     |
|  => python --version (CMD is overridden)         |
|                                                  |
+--------------------------------------------------+
```

### When to Use Which?

Use **CMD** when:
- You want users to easily override the command
- Your container is a general-purpose application
- You are building a development container

Use **ENTRYPOINT** when:
- You want the container to act as a specific executable
- You are building a CLI tool (like a linter or test runner)
- You always want the same program to run, just with different arguments

Use **both** when:
- You want a fixed program (ENTRYPOINT) with default arguments (CMD)
- You want users to easily change arguments but not the program

---

## The EXPOSE Instruction: Documenting Ports

`EXPOSE` tells Docker (and anyone reading the Dockerfile) which ports the application inside the container listens on.

**Real-life analogy:** EXPOSE is like putting a sign on a building's door that says "Entrance on Port 3000." It does not actually open the door. It just tells people which door to use.

### Important Distinction

`EXPOSE` does **not** actually publish the port. It is documentation. To actually make the port accessible, you still need the `-p` flag when running the container:

```bash
# EXPOSE 3000 in Dockerfile tells you the app uses port 3000
# But you still need -p to publish it
$ docker run -p 3000:3000 my-app
```

### Syntax

```dockerfile
# Expose a single port
EXPOSE 3000

# Expose multiple ports
EXPOSE 3000
EXPOSE 8080

# Expose UDP port
EXPOSE 53/udp
```

### Why Bother with EXPOSE?

Even though EXPOSE does not publish ports, it serves important purposes:

1. **Documentation:** Other developers know which ports the app uses
2. **Docker Compose:** Some tools use EXPOSE information automatically
3. **Best practice:** It makes your Dockerfile self-documenting

---

## Building an Image: docker build

Now that you understand the instructions, let us build an image.

### The docker build Command

```bash
$ docker build -t image_name:tag path_to_build_context
```

Breaking this down:

- `docker build` -- tells Docker to build an image
- `-t image_name:tag` -- gives the image a name and tag (like a version)
- `path_to_build_context` -- the directory containing the Dockerfile and source files

### Examples

```bash
# Build from the current directory, name it "my-app"
$ docker build -t my-app .

# Build with a specific tag
$ docker build -t my-app:1.0 .

# Build with a specific Dockerfile name
$ docker build -t my-app -f Dockerfile.dev .

# Build from a different directory
$ docker build -t my-app ./my-project
```

### Understanding Build Output

When you run `docker build`, Docker shows you each step:

```
$ docker build -t my-app .

[+] Building 15.2s (10/10) FINISHED
 => [internal] load build definition from Dockerfile          0.0s
 => [internal] load .dockerignore                             0.0s
 => [internal] load metadata for docker.io/library/node:18    1.2s
 => [1/5] FROM docker.io/library/node:18-alpine@sha256:abc   3.4s
 => [2/5] WORKDIR /app                                       0.1s
 => [3/5] COPY package.json .                                 0.1s
 => [4/5] RUN npm install                                     8.3s
 => [5/5] COPY . .                                            0.2s
 => exporting to image                                        1.9s
 => => naming to docker.io/library/my-app                     0.0s
```

Each line starting with `=>` is a build step. The numbers `[1/5]`, `[2/5]`, etc., correspond to the instructions in your Dockerfile.

---

## Build Context: What Docker Can See

The **build context** is the set of files and directories that Docker can access during the build. When you run `docker build .`, the `.` (dot) tells Docker that the current directory is the build context.

**Real-life analogy:** The build context is like the counter space in your kitchen. You can only cook with ingredients that are on the counter. Files outside the build context are like ingredients still in the pantry -- Docker cannot reach them.

### How It Works

```
+--------------------------------------------------+
|    Your Computer                                 |
|                                                  |
|    my-project/              <-- Build Context    |
|    +-- Dockerfile                                |
|    +-- package.json                              |
|    +-- server.js                                 |
|    +-- src/                                      |
|    |   +-- app.js                                |
|    |   +-- routes.js                             |
|    +-- node_modules/        <-- Sent to Docker!  |
|    +-- .git/                <-- Sent to Docker!  |
|    +-- test-data.zip        <-- Sent to Docker!  |
|                                                  |
+--------------------------------------------------+
```

**Everything** in the build context directory gets sent to the Docker daemon before the build starts. This is why large directories (like `node_modules` or `.git`) can slow down your build.

### The Problem

```bash
$ docker build -t my-app .
Sending build context to Docker daemon  245.8MB
```

245 MB! That is because Docker is sending `node_modules`, `.git`, and other large directories that you do not need in the image.

---

## The .dockerignore File: Keeping Builds Fast

A `.dockerignore` file tells Docker which files and directories to exclude from the build context. It works exactly like `.gitignore`.

**Real-life analogy:** When you pack a suitcase for a trip, you do not pack everything in your closet. You leave behind things you do not need. The `.dockerignore` file is your "do not pack" list.

### Creating a .dockerignore File

Create a file named `.dockerignore` in the same directory as your Dockerfile:

```
# .dockerignore

# Dependencies (will be installed inside the container)
node_modules

# Version control
.git
.gitignore

# IDE files
.vscode
.idea
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Docker files
Dockerfile
docker-compose.yml

# Documentation
README.md
LICENSE

# Test files
coverage
*.test.js

# Environment files with secrets
.env
.env.local
```

### Before and After .dockerignore

```
Without .dockerignore:
$ docker build -t my-app .
Sending build context to Docker daemon  245.8MB
Build time: 45 seconds

With .dockerignore:
$ docker build -t my-app .
Sending build context to Docker daemon  1.2MB
Build time: 12 seconds
```

That is a huge improvement. The build context went from 245 MB to 1.2 MB.

### Pattern Syntax

```
# Ignore a specific file
secret.key

# Ignore a directory
node_modules

# Ignore by extension
*.log
*.tmp

# Ignore with wildcards
temp*

# Exception (do NOT ignore this)
!important.log

# Ignore in subdirectories
**/*.test.js
```

---

## Layer Caching: Why Build Order Matters

This is one of the most important concepts in Docker. Understanding layer caching can make your builds go from minutes to seconds.

### What Is a Layer?

Every instruction in a Dockerfile creates a new **layer**. A layer is like a transparent sheet that contains only the changes made by that instruction.

```
+--------------------------------------------------+
|    How Layers Stack Up                           |
+--------------------------------------------------+
|                                                  |
|    CMD ["node", "server.js"]    <- Layer 6       |
|    EXPOSE 3000                  <- Layer 5       |
|    COPY . .                     <- Layer 4       |
|    RUN npm install              <- Layer 3       |
|    COPY package.json .          <- Layer 2       |
|    WORKDIR /app                 <- Layer 1       |
|    FROM node:18-alpine          <- Base Layer    |
|                                                  |
+--------------------------------------------------+
```

### How Caching Works

Docker caches each layer. When you rebuild an image, Docker checks if anything has changed for each instruction:

- **If nothing changed:** Docker reuses the cached layer (instant)
- **If something changed:** Docker rebuilds that layer AND all layers after it

```
+--------------------------------------------------+
|    Layer Caching in Action                       |
+--------------------------------------------------+
|                                                  |
|    First Build:                                  |
|    FROM node:18-alpine      [BUILD] 3s           |
|    WORKDIR /app             [BUILD] 0.1s         |
|    COPY package.json .      [BUILD] 0.1s         |
|    RUN npm install          [BUILD] 15s          |
|    COPY . .                 [BUILD] 0.2s         |
|    CMD ["node", "server.js"][BUILD] 0.1s         |
|    Total: ~18.5 seconds                          |
|                                                  |
|    Second Build (only code changed):             |
|    FROM node:18-alpine      [CACHED] instant     |
|    WORKDIR /app             [CACHED] instant     |
|    COPY package.json .      [CACHED] instant     |
|    RUN npm install          [CACHED] instant     |
|    COPY . .                 [BUILD] 0.2s         |
|    CMD ["node", "server.js"][BUILD] 0.1s         |
|    Total: ~0.3 seconds                           |
|                                                  |
+--------------------------------------------------+
```

The second build is almost instant because Docker reused the cached layers for everything before the code change.

### The Cache-Busting Problem

Here is the key rule: **When a layer changes, all subsequent layers are rebuilt.**

```dockerfile
# BAD ORDER - cache busted on every code change
FROM node:18-alpine
WORKDIR /app
COPY . .                    # <-- Changes every time you edit code
RUN npm install             # <-- Must reinstall every time!
CMD ["node", "server.js"]
```

```dockerfile
# GOOD ORDER - npm install is cached unless package.json changes
FROM node:18-alpine
WORKDIR /app
COPY package.json .         # <-- Only changes when dependencies change
RUN npm install             # <-- Cached if package.json unchanged
COPY . .                    # <-- Changes when code changes
CMD ["node", "server.js"]
```

```
+--------------------------------------------------+
|    Why Order Matters                             |
+--------------------------------------------------+
|                                                  |
|    BAD: COPY everything, then npm install        |
|    - Edit server.js                              |
|    - COPY . . invalidates cache                  |
|    - npm install MUST re-run (15 seconds)        |
|    - Total rebuild: ~18 seconds                  |
|                                                  |
|    GOOD: COPY package.json, install, then code   |
|    - Edit server.js                              |
|    - COPY package.json is still cached           |
|    - npm install is still cached                 |
|    - Only COPY . . re-runs (0.2 seconds)         |
|    - Total rebuild: ~0.3 seconds                 |
|                                                  |
+--------------------------------------------------+
```

---

## Complete Example: Node.js Application

Let us put everything together and build a real Node.js application.

### Step 1: Create the Project Structure

```
my-node-app/
+-- Dockerfile
+-- .dockerignore
+-- package.json
+-- server.js
```

### Step 2: Create package.json

```json
{
  "name": "my-node-app",
  "version": "1.0.0",
  "description": "A simple Node.js app in Docker",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

### Step 3: Create server.js

```javascript
const express = require('express');
const app = express();
const PORT = 3000;

// A simple route that returns a greeting
app.get('/', (req, res) => {
  res.json({
    message: 'Hello from Docker!',
    timestamp: new Date().toISOString(),
    hostname: require('os').hostname()
  });
});

// A health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on port ${PORT}`);
});
```

### Step 4: Create .dockerignore

```
node_modules
.git
.gitignore
README.md
.DS_Store
*.log
```

### Step 5: Write the Dockerfile

```dockerfile
# Step 1: Start with Node.js on Alpine Linux
# Alpine is a tiny Linux distribution (~7 MB)
# node:18-alpine gives us Node.js 18 on Alpine
FROM node:18-alpine

# Step 2: Set the working directory inside the container
# All subsequent commands will run from /app
# Docker creates /app if it does not exist
WORKDIR /app

# Step 3: Copy ONLY package.json first
# We do this before copying all code for better caching
# If package.json has not changed, npm install will be cached
COPY package.json .

# Step 4: Install dependencies
# npm install reads package.json and installs everything listed
# This layer is cached unless package.json changes
RUN npm install

# Step 5: Copy the rest of the application code
# This is done AFTER npm install for caching reasons
# Changes to server.js will not trigger a reinstall
COPY . .

# Step 6: Document which port the app uses
# This does not actually publish the port
# It tells other developers "this app listens on 3000"
EXPOSE 3000

# Step 7: Define the command to start the application
# When the container starts, it runs: node server.js
# Using exec form (array) is best practice
CMD ["node", "server.js"]
```

### Step 6: Build the Image

```bash
$ cd my-node-app

$ docker build -t my-node-app:1.0 .
```

Expected output:

```
[+] Building 18.4s (10/10) FINISHED
 => [internal] load build definition from Dockerfile          0.0s
 => [internal] load .dockerignore                             0.0s
 => [internal] load metadata for docker.io/library/node:18    1.1s
 => [1/5] FROM docker.io/library/node:18-alpine@sha256:abc   4.2s
 => [2/5] WORKDIR /app                                       0.1s
 => [3/5] COPY package.json .                                 0.0s
 => [4/5] RUN npm install                                    11.3s
 => [5/5] COPY . .                                            0.1s
 => exporting to image                                        1.6s
 => => naming to docker.io/library/my-node-app:1.0            0.0s
```

### Step 7: Run the Container

```bash
$ docker run -d -p 3000:3000 --name my-app my-node-app:1.0
a1b2c3d4e5f6...
```

Breaking down the flags:
- `-d` -- run in detached mode (in the background)
- `-p 3000:3000` -- map port 3000 on your computer to port 3000 in the container
- `--name my-app` -- give the container a friendly name
- `my-node-app:1.0` -- the image to run

### Step 8: Test the Application

```bash
$ curl http://localhost:3000
{
  "message": "Hello from Docker!",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "hostname": "a1b2c3d4e5f6"
}

$ curl http://localhost:3000/health
{
  "status": "healthy"
}
```

Your application is running inside a Docker container.

### Step 9: Verify the Layer Cache

Make a small change to `server.js` (change the message text) and rebuild:

```bash
$ docker build -t my-node-app:1.1 .
```

Expected output:

```
[+] Building 1.2s (10/10) FINISHED
 => [internal] load build definition from Dockerfile          0.0s
 => [internal] load .dockerignore                             0.0s
 => [internal] load metadata for docker.io/library/node:18    0.3s
 => CACHED [1/5] FROM docker.io/library/node:18-alpine        0.0s
 => CACHED [2/5] WORKDIR /app                                 0.0s
 => CACHED [3/5] COPY package.json .                          0.0s
 => CACHED [4/5] RUN npm install                              0.0s
 => [5/5] COPY . .                                            0.2s
 => exporting to image                                        0.7s
 => => naming to docker.io/library/my-node-app:1.1            0.0s
```

Notice the word `CACHED` on steps 1 through 4. Only step 5 (copying the code) and the export had to run. The build went from 18 seconds to 1.2 seconds.

### Step 10: Clean Up

```bash
$ docker stop my-app
my-app

$ docker rm my-app
my-app
```

---

## Complete Dockerfile Anatomy

Here is a visual reference for all the instructions we covered:

```
+--------------------------------------------------+
|                 DOCKERFILE ANATOMY               |
+--------------------------------------------------+
|                                                  |
|  FROM node:18-alpine                             |
|  ^                                               |
|  |  Base image (required, must be first)         |
|                                                  |
|  WORKDIR /app                                    |
|  ^                                               |
|  |  Set working directory                        |
|                                                  |
|  COPY package.json .                             |
|  ^                                               |
|  |  Copy files from build context to image       |
|                                                  |
|  RUN npm install                                 |
|  ^                                               |
|  |  Execute command during build                 |
|                                                  |
|  COPY . .                                        |
|  ^                                               |
|  |  Copy remaining files                         |
|                                                  |
|  EXPOSE 3000                                     |
|  ^                                               |
|  |  Document the port (informational only)       |
|                                                  |
|  CMD ["node", "server.js"]                       |
|  ^                                               |
|  |  Default command when container starts        |
|                                                  |
+--------------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Forgetting to Name the File Correctly

```bash
# WRONG file names:
dockerfile        # lowercase 'd'
Dockerfile.txt    # has an extension
DockerFile        # wrong capitalization

# CORRECT:
Dockerfile        # capital D, no extension
```

### Mistake 2: Copying Everything Before Installing Dependencies

```dockerfile
# BAD: Busts cache on every code change
COPY . .
RUN npm install

# GOOD: Caches npm install when only code changes
COPY package.json package-lock.json ./
RUN npm install
COPY . .
```

### Mistake 3: Using CMD When You Mean RUN

```dockerfile
# WRONG: CMD runs when container STARTS, not during build
CMD apt-get update && apt-get install -y curl

# RIGHT: RUN executes during BUILD
RUN apt-get update && apt-get install -y curl
```

### Mistake 4: Not Using .dockerignore

```bash
# Without .dockerignore, you might accidentally:
# - Send node_modules (100+ MB) to the build context
# - Include .git directory (can be very large)
# - Copy .env files with secrets into the image
```

### Mistake 5: Confusing EXPOSE with -p

```dockerfile
# EXPOSE does NOT publish the port
EXPOSE 3000

# You STILL need -p when running:
# docker run -p 3000:3000 my-app
```

---

## Best Practices

1. **Always use a `.dockerignore` file** to keep your build context small and avoid copying secrets into the image.

2. **Copy dependency files first, then install, then copy code.** This maximizes layer caching.

3. **Use specific base image tags** like `node:18-alpine` instead of `node:latest`. This ensures reproducible builds.

4. **Use exec form for CMD** (`CMD ["node", "server.js"]` instead of `CMD node server.js`). Exec form handles signals properly.

5. **Keep your Dockerfile readable** with comments explaining each step.

6. **Minimize the number of layers** by combining related RUN commands.

7. **Do not install unnecessary packages.** Every package increases image size and potential security vulnerabilities.

8. **Use `WORKDIR` instead of `RUN mkdir && cd`.** WORKDIR is cleaner and persists across instructions.

---

## Quick Summary

A Dockerfile is a text file with instructions for building a Docker image. Each instruction performs a specific action:

- `FROM` sets the base image (required, must be first)
- `WORKDIR` sets the working directory inside the container
- `COPY` copies files from your computer into the image
- `RUN` executes commands during the build process
- `CMD` sets the default command when a container starts (can be overridden)
- `ENTRYPOINT` sets a fixed command when a container starts (hard to override)
- `EXPOSE` documents which port the application uses

You build images with `docker build -t name:tag .` and Docker uses layer caching to speed up rebuilds. A `.dockerignore` file excludes unnecessary files from the build context.

---

## Key Points

- A Dockerfile is a recipe for building Docker images
- Every Dockerfile must start with `FROM`
- Each instruction creates a layer; layers are cached for faster rebuilds
- Put things that change rarely at the top, and things that change often at the bottom
- `CMD` is the default command (easily overridden); `ENTRYPOINT` is the fixed command
- `EXPOSE` is documentation only -- it does not publish ports
- The build context is everything Docker can see during the build
- `.dockerignore` keeps the build context small and prevents secrets from leaking
- Layer caching can make rebuilds nearly instant if you order instructions wisely

---

## Practice Questions

1. What is the difference between `CMD` and `ENTRYPOINT`? When would you use each one?

2. Why is it important to copy `package.json` and run `npm install` before copying the rest of the application code? What happens if you copy everything first?

3. You have a Dockerfile with `EXPOSE 8080`. You run the container with `docker run my-app`. Can you access the application on port 8080 from your browser? Why or why not?

4. What does the `.` (dot) at the end of `docker build -t my-app .` mean? What is it called?

5. You change one line of code in `server.js` and rebuild the image. Which layers will Docker rebuild, and which will come from the cache?

---

## Exercises

### Exercise 1: Build Your First Dockerfile

Create a simple Dockerfile that:
1. Uses `node:18-alpine` as the base image
2. Sets the working directory to `/app`
3. Copies a simple JavaScript file that prints "Hello, Docker!"
4. Runs the script using `CMD`

Build the image and run it. Verify the output.

### Exercise 2: Experiment with Layer Caching

1. Create a Node.js project with a `package.json` and a `server.js`
2. Write a Dockerfile with proper instruction ordering
3. Build the image and note the build time
4. Change only the `server.js` file
5. Rebuild and observe which steps say CACHED
6. Now change `package.json` (add a dependency)
7. Rebuild and observe which steps are rebuilt

### Exercise 3: CMD vs ENTRYPOINT

1. Create a Dockerfile with `CMD ["echo", "Hello from CMD"]`
2. Build and run it. Note the output.
3. Run it again with `docker run my-app echo "Custom message"`. What happens?
4. Change CMD to `ENTRYPOINT ["echo"]` and `CMD ["Hello from ENTRYPOINT"]`
5. Build and run it. Then try `docker run my-app "Custom message"`. What is different?

---

## What Is Next?

You now know how to write a Dockerfile and build your own images. In the next chapter, we will learn Dockerfile best practices that professional developers use to create smaller, faster, and more secure images. You will learn about multi-stage builds, running as non-root users, and techniques that can cut your image size by 90 percent or more.
