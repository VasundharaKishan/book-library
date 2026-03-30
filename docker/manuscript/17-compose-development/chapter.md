# Chapter 17: Docker Compose for Development

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Use bind mounts for live code reloading during development
- Set up hot reload for Node.js, Python, and other frameworks
- Use `docker compose watch` for automatic sync and rebuild
- Create separate development and production Compose configurations
- Use `compose.override.yml` for environment-specific settings
- Combine multiple Compose files with `docker compose -f`
- Extend and override services for different environments
- Debug applications running inside containers
- Attach a debugger to a containerized application

---

## Why This Chapter Matters

Up to this point, every time you changed your application code, you had to rebuild the Docker image and restart the container. That workflow is fine for production, but it is painfully slow for development. Imagine having to wait 30 seconds to see the effect of a one-line change. You would give up on Docker very quickly.

This chapter shows you how to set up a development workflow where code changes appear instantly inside your container — no rebuild needed. It is the difference between driving to the post office to send a letter and sending an email. The result is the same, but one is dramatically faster.

Think of it this way. In production, your application is sealed inside a container like food sealed in a can. That is great for shipping and storage. But during development, you need to taste and adjust the recipe constantly. This chapter teaches you how to keep the kitchen (your development environment) open while still using containers.

---

## Bind Mounts for Live Code Reloading

A **bind mount** maps a directory on your host machine directly into the container. Unlike a named volume (which Docker manages), a bind mount uses a directory you specify. When you change a file on your host, the change appears inside the container immediately.

### How Bind Mounts Work

```
┌────────────────────────────────────────────┐
│   Your Computer (Host)                     │
│                                            │
│   ~/my-project/src/server.js               │
│         │                                  │
│         │  bind mount                      │
│         │                                  │
│   ┌─────▼──────────────────────────┐       │
│   │   Container                     │       │
│   │                                 │       │
│   │   /app/src/server.js            │       │
│   │   (same file! not a copy)       │       │
│   │                                 │       │
│   │   Changes on host appear here   │       │
│   │   instantly — no rebuild!       │       │
│   └─────────────────────────────────┘       │
│                                            │
└────────────────────────────────────────────┘
```

The key difference from the production workflow:

- **Production**: Code is copied into the image with `COPY` during build. Changes require a rebuild.
- **Development**: Code is mounted from your host. Changes are reflected immediately.

### Setting Up Bind Mounts in Compose

Here is a Node.js example:

```yaml
services:
  api:
    build: ./api
    ports:
      - "3000:3000"
    volumes:
      - ./api:/app                   # Mount source code
      - /app/node_modules            # Prevent overwriting node_modules
    environment:
      NODE_ENV: development
```

Let us explain each volume line:

- `./api:/app` — Mount the `./api` directory from your host into `/app` in the container. Every file in `./api` on your host is now also at `/app` in the container.
- `/app/node_modules` — This is an anonymous volume that preserves the container's `node_modules` directory. Without this, the bind mount would overwrite the container's `node_modules` with whatever is (or is not) in your host's `node_modules`.

### The node_modules Problem

This is a common source of confusion. Let us walk through what happens:

1. Your Dockerfile has `RUN npm install`, which installs dependencies inside the container at `/app/node_modules`.
2. You add a bind mount `./api:/app`, which maps your host directory over `/app` in the container.
3. Your host directory might not have a `node_modules` folder (or it has one built for a different OS).
4. The bind mount overwrites the container's `/app` completely, including the `node_modules` that `npm install` created.
5. Your application fails because the dependencies are gone.

The fix: add an anonymous volume for `node_modules`:

```yaml
volumes:
  - ./api:/app              # Mount source code from host
  - /app/node_modules       # Keep container's node_modules
```

```
┌──────────────────────────────────────────────┐
│   Without /app/node_modules volume:          │
│                                               │
│   Host ./api/         ──mount──>  /app/       │
│   ├── src/                       ├── src/     │
│   ├── package.json               ├── package.json
│   └── (no node_modules)          └── (empty!) │
│                                               │
│   node_modules is OVERWRITTEN — app crashes!  │
├──────────────────────────────────────────────┤
│   With /app/node_modules volume:             │
│                                               │
│   Host ./api/         ──mount──>  /app/       │
│   ├── src/                       ├── src/     │
│   ├── package.json               ├── package.json
│                                  └── node_modules/
│                                      (preserved!)
│                                               │
│   node_modules is kept from the build step    │
└──────────────────────────────────────────────┘
```

### Hot Reload for Node.js with nodemon

For Node.js, the file watcher tool **nodemon** automatically restarts your application when it detects file changes.

Update `api/package.json`:

```json
{
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
```

Update your Compose file to use the dev script:

```yaml
services:
  api:
    build: ./api
    ports:
      - "3000:3000"
    volumes:
      - ./api:/app
      - /app/node_modules
    command: npm run dev      # Override CMD from Dockerfile
    environment:
      NODE_ENV: development
```

The `command:` line overrides whatever `CMD` is set in the Dockerfile. Instead of `npm start` (which runs `node server.js`), it runs `npm run dev` (which runs `nodemon server.js`).

Now the workflow is:

1. Start the stack: `docker compose up -d`
2. Edit `api/server.js` on your host machine.
3. Save the file.
4. nodemon inside the container detects the change and restarts the server.
5. Refresh your browser to see the change — no rebuild needed.

### Hot Reload for Python with Flask

```yaml
services:
  web:
    build: ./web
    ports:
      - "5000:5000"
    volumes:
      - ./web:/app
    environment:
      FLASK_ENV: development
      FLASK_DEBUG: 1
    command: flask run --host=0.0.0.0 --reload
```

Flask's `--reload` flag watches for file changes and automatically restarts the server.

### Hot Reload for Frontend Applications

Frontend frameworks like React, Vue, and Angular have built-in hot reload. They work with Docker bind mounts:

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0
    environment:
      CHOKIDAR_USEPOLLING: "true"    # Needed for file watching in Docker
```

The `CHOKIDAR_USEPOLLING` environment variable tells the file watcher to use polling instead of native file system events. This is sometimes necessary because Docker's file system layer may not pass native change events from the host to the container.

---

## Docker Compose Watch

Docker Compose introduced a `watch` feature that provides a more sophisticated approach to syncing files during development. Instead of mounting your entire source directory, `watch` lets you define specific sync rules and trigger actions when files change.

### What docker compose watch Does

The `watch` command monitors your source files and performs actions when changes are detected:

- **sync**: Copy the changed file into the container.
- **rebuild**: Rebuild the image and recreate the container.
- **sync+restart**: Copy the file and restart the service.

### Setting Up Watch

```yaml
services:
  api:
    build: ./api
    ports:
      - "3000:3000"
    develop:
      watch:
        # Sync source code changes into the container
        - action: sync
          path: ./api/src
          target: /app/src

        # Rebuild when package.json changes (new dependencies)
        - action: rebuild
          path: ./api/package.json

        # Sync and restart when config changes
        - action: sync+restart
          path: ./api/config
          target: /app/config
```

Let us explain each rule:

1. **sync for source code**: When any file in `./api/src` changes, it is copied to `/app/src` in the container. The server detects the change and hot-reloads (if you are using nodemon or a similar tool).

2. **rebuild for dependencies**: When `package.json` changes (you added a new dependency), the entire image is rebuilt and the container is recreated. This ensures `npm install` runs with the new dependencies.

3. **sync+restart for config**: When configuration files change, they are copied to the container and the service is restarted. This is for files that require a restart to take effect but not a full rebuild.

### Running Watch Mode

```bash
docker compose watch
```

This starts the services and begins watching for file changes. The output shows what actions are triggered:

```
[+] Running 2/2
 ✔ Container myapp-api-1       Started
 ✔ Container myapp-database-1  Started
Watching ./api/src for changes...
Watching ./api/package.json for changes...
Watching ./api/config for changes...
```

When you edit a file:

```
Syncing ./api/src/server.js to /app/src/server.js
```

### Watch vs. Bind Mounts

```
┌──────────────────────────┬──────────────────────────┐
│   Bind Mounts            │   Docker Compose Watch   │
├──────────────────────────┼──────────────────────────┤
│ Mount entire directory   │ Sync specific paths      │
│ Real-time (instant)      │ Near real-time (slight   │
│                          │  delay for sync)          │
│ node_modules hack needed │ No hack needed           │
│ Works with any Compose   │ Requires newer Compose   │
│  version                 │  versions                │
│ Can cause permission     │ Fewer permission issues  │
│  issues across OS        │                          │
│ Simpler to set up        │ More configuration       │
│ Cannot trigger rebuilds  │ Can trigger rebuilds     │
│                          │  on dependency changes   │
└──────────────────────────┴──────────────────────────┘
```

Both approaches are valid. Bind mounts are simpler and work immediately. Watch mode is more flexible and avoids some common issues with bind mounts.

---

## Development vs. Production Compose Files

Your development environment needs things that production does not:

- Bind mounts for code syncing
- Debug ports open
- Hot reload commands
- Verbose logging
- Development environment variables

Your production environment needs things that development does not:

- Optimized images
- No source code mounted
- Production commands
- Minimal logging
- Production secrets

Docker Compose lets you handle this with multiple files.

### The compose.override.yml Pattern

Docker Compose automatically loads two files if they exist:

1. `docker-compose.yml` (or `compose.yml`) — The base configuration.
2. `docker-compose.override.yml` (or `compose.override.yml`) — Overrides for development.

The override file is merged on top of the base file. Values in the override file replace or extend values in the base file.

**Base file: `docker-compose.yml`**

This contains configuration shared between development and production:

```yaml
services:
  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      DB_HOST: database
      DB_USER: appuser
      DB_NAME: appdb
    depends_on:
      database:
        condition: service_healthy

  database:
    image: postgres:16
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  db-data:
```

**Override file: `docker-compose.override.yml`**

This adds development-specific settings:

```yaml
services:
  api:
    volumes:
      - ./api:/app
      - /app/node_modules
    command: npm run dev
    environment:
      NODE_ENV: development
      DEBUG: "true"

  database:
    ports:
      - "5432:5432"    # Expose DB port for local GUI tools
```

When you run `docker compose up -d`, both files are merged automatically:

```
┌──────────────────────────────────────────────────┐
│   docker-compose.yml + docker-compose.override.yml│
│                                                   │
│   api:                                            │
│     build: ./api                  (from base)     │
│     ports: ["3000:3000"]          (from base)     │
│     volumes:                      (from override) │
│       - ./api:/app                                │
│       - /app/node_modules                         │
│     command: npm run dev          (from override) │
│     environment:                                  │
│       DB_HOST: database           (from base)     │
│       DB_USER: appuser            (from base)     │
│       DB_NAME: appdb              (from base)     │
│       NODE_ENV: development       (from override) │
│       DEBUG: "true"               (from override) │
│                                                   │
│   database:                                       │
│     image: postgres:16            (from base)     │
│     ports: ["5432:5432"]          (from override) │
│     volumes, healthcheck...       (from base)     │
│                                                   │
└──────────────────────────────────────────────────┘
```

The override file does not replace the entire service — it merges. Lists like `environment` are combined. Single values like `command` are replaced.

### Production File: compose.production.yml

For production, create a separate file:

**`compose.production.yml`**:

```yaml
services:
  api:
    command: npm start
    environment:
      NODE_ENV: production
    restart: always

  database:
    restart: always
    # No port mapping — database not accessible from outside
```

To use the production file instead of the override:

```bash
docker compose -f docker-compose.yml -f compose.production.yml up -d
```

The `-f` flag specifies which files to use. When you provide `-f` explicitly, the automatic loading of `docker-compose.override.yml` is skipped.

---

## Using Multiple Compose Files with -f

The `-f` flag lets you combine any number of Compose files. Files are applied in order — later files override earlier ones.

### Common Patterns

```bash
# Development (default: base + override)
docker compose up -d

# Production (base + production overrides)
docker compose -f docker-compose.yml -f compose.production.yml up -d

# Testing (base + test overrides)
docker compose -f docker-compose.yml -f compose.test.yml up -d

# Production with monitoring (base + production + monitoring)
docker compose -f docker-compose.yml \
  -f compose.production.yml \
  -f compose.monitoring.yml \
  up -d
```

### Example: Test Configuration

**`compose.test.yml`**:

```yaml
services:
  api:
    command: npm test
    environment:
      NODE_ENV: test
      DB_NAME: testdb

  database:
    environment:
      POSTGRES_DB: testdb
    # Use a temporary volume for test data
    volumes:
      - test-data:/var/lib/postgresql/data

volumes:
  test-data:
```

Run tests:

```bash
docker compose -f docker-compose.yml -f compose.test.yml up --abort-on-container-exit
```

The `--abort-on-container-exit` flag stops all services when any one service exits. This is perfect for test runs — when the test runner finishes, everything shuts down.

---

## Extending Services

Docker Compose supports extending services to avoid repeating configuration.

### Using YAML Anchors

YAML anchors let you define a block once and reuse it:

```yaml
x-common-env: &common-env
  DB_HOST: database
  DB_USER: appuser
  DB_PASSWORD: apppass
  DB_NAME: appdb

services:
  api:
    build: ./api
    environment:
      <<: *common-env
      PORT: 3000

  worker:
    build: ./worker
    environment:
      <<: *common-env
      QUEUE_NAME: tasks
```

Let us break down the syntax:

- `x-common-env:` — Any top-level key starting with `x-` is an extension field. Compose ignores it.
- `&common-env` — This creates an anchor named `common-env` that points to the block of environment variables.
- `<<: *common-env` — This merges the anchored block into the current position. The `<<` means "merge" and `*common-env` references the anchor.

The result is equivalent to:

```yaml
services:
  api:
    environment:
      DB_HOST: database
      DB_USER: appuser
      DB_PASSWORD: apppass
      DB_NAME: appdb
      PORT: 3000

  worker:
    environment:
      DB_HOST: database
      DB_USER: appuser
      DB_PASSWORD: apppass
      DB_NAME: appdb
      QUEUE_NAME: tasks
```

### Using Extension Fields for Service Templates

```yaml
x-service-base: &service-base
  restart: unless-stopped
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"

services:
  api:
    <<: *service-base
    build: ./api
    ports:
      - "3000:3000"

  worker:
    <<: *service-base
    build: ./worker
```

Both `api` and `worker` inherit the `restart` and `logging` configuration from the `x-service-base` template.

---

## Debugging Inside Containers

When your application runs inside a container, you need a way to debug it. Here are several approaches.

### Approach 1: docker compose exec

The simplest way to investigate is to get a shell inside the container:

```bash
docker compose exec api sh
```

From inside, you can:

```bash
# Check environment variables
env | grep DB

# Test the database connection
ping database

# Check file permissions
ls -la /app/

# Read application logs
cat /app/logs/error.log

# Check what processes are running
ps aux

# Test an endpoint from inside the container
wget -qO- http://localhost:3000/health
```

### Approach 2: Adding Debug Tools to Development Images

Your production Dockerfile should be minimal, but your development setup can include debugging tools:

```yaml
services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile.dev    # Use a development Dockerfile
```

**`api/Dockerfile.dev`**:

```dockerfile
FROM node:20

# Install debugging and diagnostic tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    net-tools \
    iputils-ping \
    vim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
EXPOSE 9229    # Node.js debug port

CMD ["npm", "run", "dev"]
```

### Approach 3: Attaching a Node.js Debugger

Node.js has a built-in debugging protocol. You can attach VS Code or Chrome DevTools to a running Node.js process inside a container.

**Step 1: Start Node.js in debug mode**

Update `package.json`:

```json
{
  "scripts": {
    "dev": "nodemon server.js",
    "debug": "nodemon --inspect=0.0.0.0:9229 server.js"
  }
}
```

The `--inspect=0.0.0.0:9229` flag tells Node.js to:

- Start the debug server.
- Listen on all interfaces (`0.0.0.0`), not just localhost. This is necessary because the debugger connects from outside the container.
- Use port 9229 (the default Node.js debug port).

**Step 2: Expose the debug port in Compose**

```yaml
services:
  api:
    build: ./api
    ports:
      - "3000:3000"
      - "9229:9229"    # Debug port
    volumes:
      - ./api:/app
      - /app/node_modules
    command: npm run debug
```

**Step 3: Configure VS Code**

Create `.vscode/launch.json` in your project root:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to Docker",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "address": "localhost",
      "localRoot": "${workspaceFolder}/api",
      "remoteRoot": "/app",
      "restart": true
    }
  ]
}
```

Let us explain the key fields:

- `request: "attach"`: Attach to an already-running process (not launch a new one).
- `port: 9229`: The debug port we exposed.
- `localRoot`: Where the source code lives on your host machine.
- `remoteRoot`: Where the source code lives inside the container.
- `restart: true`: Reattach if the server restarts (from nodemon).

**Step 4: Start debugging**

1. Run `docker compose up -d`.
2. In VS Code, open the Run and Debug panel (Ctrl+Shift+D or Cmd+Shift+D).
3. Select "Attach to Docker" and click the green play button.
4. Set breakpoints in your code.
5. Make a request to your API. VS Code will pause at the breakpoint.

```
┌─────────────────────────────────────────────────┐
│                                                  │
│   VS Code (your host)                           │
│   ┌────────────────────┐                        │
│   │ Breakpoint at       │                        │
│   │ line 42 of          │                        │
│   │ server.js           │                        │
│   └────────┬───────────┘                        │
│            │                                     │
│            │  Debug protocol (port 9229)         │
│            ▼                                     │
│   ┌────────────────────┐                        │
│   │ Container "api"     │                        │
│   │                     │                        │
│   │ Node.js paused at   │                        │
│   │ line 42             │                        │
│   │                     │                        │
│   │ Variables, call     │                        │
│   │ stack visible in    │                        │
│   │ VS Code             │                        │
│   └────────────────────┘                        │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## A Complete Development Setup

Here is a full development Compose configuration that brings everything together:

**`docker-compose.yml`** (base):

```yaml
services:
  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      DB_HOST: database
      DB_USER: appuser
      DB_PASSWORD: apppass
      DB_NAME: appdb
      REDIS_URL: redis://cache:6379
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_healthy
    networks:
      - app-network

  database:
    image: postgres:16
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  cache:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

volumes:
  db-data:

networks:
  app-network:
```

**`docker-compose.override.yml`** (development overrides, loaded automatically):

```yaml
services:
  api:
    volumes:
      - ./api:/app
      - /app/node_modules
    ports:
      - "9229:9229"          # Debug port
    command: npm run debug
    environment:
      NODE_ENV: development
      DEBUG: "*"

  database:
    ports:
      - "5432:5432"          # Access from host for DB GUI tools

  cache:
    ports:
      - "6379:6379"          # Access from host for Redis CLI
```

**`compose.production.yml`** (production overrides, loaded explicitly):

```yaml
services:
  api:
    command: npm start
    environment:
      NODE_ENV: production
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M

  database:
    restart: always
    # No host port mapping

  cache:
    restart: always
    # No host port mapping
```

### Daily Development Workflow

```bash
# Start development environment
docker compose up -d

# Watch logs while developing
docker compose logs -f api

# After changing code: nothing to do!
# nodemon restarts automatically

# After adding a new npm package:
docker compose exec api npm install new-package
docker compose up -d --build    # Rebuild to include new package

# Run tests
docker compose exec api npm test

# Debug: set breakpoint in VS Code and attach debugger

# Stop at end of day
docker compose down

# Start fresh (reset database)
docker compose down -v
docker compose up -d
```

---

## Common Mistakes

### Mistake 1: Forgetting to Bind Mount During Development

```yaml
# Wrong: code is baked into the image, changes require rebuild
services:
  api:
    build: ./api
    command: npm run dev
    # Missing volumes! Every change needs `docker compose build`

# Right: bind mount for instant changes
services:
  api:
    build: ./api
    volumes:
      - ./api:/app
      - /app/node_modules
    command: npm run dev
```

### Mistake 2: Not Handling node_modules

```yaml
# Wrong: bind mount overwrites node_modules
services:
  api:
    volumes:
      - ./api:/app          # This wipes out /app/node_modules!

# Right: protect node_modules with an anonymous volume
services:
  api:
    volumes:
      - ./api:/app
      - /app/node_modules   # Preserve container's node_modules
```

### Mistake 3: Not Binding to 0.0.0.0

Many development servers bind to `127.0.0.1` (localhost) by default. Inside a container, `127.0.0.1` means "inside this container only," so connections from outside the container are refused.

```bash
# Wrong: server only accessible inside the container
node server.js --host 127.0.0.1

# Right: server accessible from outside the container
node server.js --host 0.0.0.0
```

Or in your application code:

```javascript
// Wrong
app.listen(3000, '127.0.0.1');

// Right
app.listen(3000, '0.0.0.0');
```

### Mistake 4: Using Production Compose File for Development

```bash
# Wrong: uses the production file which has no bind mounts
docker compose -f docker-compose.yml -f compose.production.yml up -d

# Right: just use docker compose up (loads override automatically)
docker compose up -d
```

### Mistake 5: Leaving Debug Ports Open in Production

```yaml
# DANGER: debug port exposed in production
services:
  api:
    ports:
      - "3000:3000"
      - "9229:9229"    # This should ONLY be in the dev override!
```

Always put debug ports in the override file, never in the base file.

---

## Best Practices

1. **Keep the base Compose file environment-agnostic**. It should work for both development and production. Put environment-specific settings in override files.

2. **Use `docker-compose.override.yml` for development**. It is loaded automatically, so your development workflow is just `docker compose up -d`.

3. **Use bind mounts only in development**. Production should use the code baked into the image.

4. **Always protect language-specific dependency directories** (`node_modules`, `vendor`, `venv`, etc.) with anonymous volumes when using bind mounts.

5. **Use hot reload tools** (nodemon, Flask debug mode, etc.) to avoid manual restarts.

6. **Expose debug ports only in development**. Never expose debug ports in production.

7. **Use YAML anchors** to avoid duplicating configuration across services.

8. **Add `.dockerignore`** to prevent unnecessary files from being included in builds (especially `node_modules`, `.git`, and IDE files).

---

## Quick Summary

Docker Compose provides powerful tools for development workflows. Bind mounts sync your source code from the host into containers for instant feedback. The `docker compose watch` feature offers file syncing with automatic rebuild triggers. Override files (`docker-compose.override.yml`) let you maintain separate development and production configurations without duplicating the base setup. YAML anchors reduce configuration repetition. For debugging, you can attach VS Code or Chrome DevTools to Node.js running inside containers by exposing the debug port and configuring the source mapping.

---

## Key Points

- Bind mounts (`./src:/app`) sync host files into containers for live code reloading.
- Protect dependency directories (like `node_modules`) with anonymous volumes.
- `docker compose watch` provides file sync with rebuild triggers for dependency changes.
- `docker-compose.override.yml` is automatically loaded and should contain development settings.
- Use `docker compose -f` to explicitly specify which files to combine.
- Override files merge with (not replace) the base file.
- Hot reload tools (nodemon, Flask debug mode) automatically restart on code changes.
- Bind your development server to `0.0.0.0`, not `127.0.0.1`, for access from outside the container.
- Expose debug ports only in development override files, never in the base or production files.
- YAML anchors (`&name` and `*name`) reduce configuration duplication.

---

## Practice Questions

1. Why do you need an anonymous volume for `/app/node_modules` when using bind mounts? What would happen without it?

2. Explain the difference between `docker compose watch` with `action: sync` and `action: rebuild`. When would you use each one?

3. You have a base `docker-compose.yml` and a `docker-compose.override.yml`. If both files define an `environment` section for the same service, what happens? Are the values merged or replaced?

4. Why must a development server bind to `0.0.0.0` instead of `127.0.0.1` inside a Docker container?

5. Describe how you would set up a debugging workflow for a Node.js application running inside a Docker container.

---

## Exercises

### Exercise 1: Hot Reload Setup

1. Create a simple Node.js Express application that returns "Hello World" on GET /.
2. Write a `docker-compose.yml` with bind mounts and nodemon for hot reload.
3. Start the stack and verify the page works.
4. Change the response text to "Hello Docker" without restarting.
5. Refresh the browser and verify the change appears.

### Exercise 2: Development and Production Configs

1. Create a base `docker-compose.yml` for a Node.js app with PostgreSQL.
2. Create a `docker-compose.override.yml` that adds bind mounts, debug port, and `npm run dev`.
3. Create a `compose.production.yml` that uses `npm start`, `NODE_ENV=production`, and no bind mounts.
4. Start in development mode and verify bind mounts work.
5. Stop, then start in production mode using `-f` flags and verify there are no bind mounts.

### Exercise 3: Attaching a Debugger

1. Set up a Node.js application in Docker with the debug port exposed (9229).
2. Configure VS Code with a `launch.json` that attaches to the containerized app.
3. Set a breakpoint in your request handler.
4. Make a request and verify VS Code pauses at the breakpoint.
5. Inspect variables and step through the code.

---

## What Is Next?

You now have a professional development workflow with Docker Compose. In the next chapter, you will build a complete full-stack project from scratch: a React frontend, a Spring Boot API, a PostgreSQL database, and an Nginx reverse proxy. This is the kind of setup you will encounter in real-world projects, and you will create the entire stack with Docker Compose.
