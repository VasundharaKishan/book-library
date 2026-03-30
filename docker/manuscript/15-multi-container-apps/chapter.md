# Chapter 15: Building Multi-Container Applications

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Build a real multi-container application from scratch
- Create a Node.js API that connects to PostgreSQL and Redis
- Write a complete `docker-compose.yml` for a three-service stack
- Use `depends_on` with health checks to control startup order
- Understand the wait-for-it pattern for database readiness
- Connect services through shared Docker networks
- Test and debug a full multi-container application
- View and analyze logs from all services together

---

## Why This Chapter Matters

In the previous chapter, you learned the basics of Docker Compose. Now it is time to build something real. This chapter walks you through creating a complete application with three services working together — the kind of architecture you will encounter in professional software development.

Think of this chapter as building your first real house. The previous chapter taught you what a blueprint is and how to read it. Now you are actually going to lay the foundation, put up the walls, install the plumbing, and wire the electricity. By the end, you will have a working building.

The application we will build is a simple task management API. Users can create, read, and delete tasks. The tasks are stored in PostgreSQL, and recently accessed tasks are cached in Redis for faster retrieval.

---

## The Architecture

Our application has three services:

```
┌─────────────────────────────────────────────────────┐
│                    Docker Compose                    │
│                                                      │
│   ┌──────────────┐                                  │
│   │   api         │  Node.js + Express              │
│   │   Port 3000   │  Handles HTTP requests          │
│   └──────┬───┬───┘                                  │
│          │   │                                       │
│          │   │                                       │
│   ┌──────▼───┘───┐    ┌──────────────┐             │
│   │   database    │    │   cache       │             │
│   │   Port 5432   │    │   Port 6379   │             │
│   │   PostgreSQL  │    │   Redis       │             │
│   │               │    │               │             │
│   │   Stores      │    │   Caches      │             │
│   │   tasks       │    │   recent      │             │
│   │   permanently │    │   tasks       │             │
│   └───────────────┘    └──────────────┘             │
│                                                      │
│   All services on the same network                   │
│   API connects to "database" and "cache" by name    │
└─────────────────────────────────────────────────────┘
```

- **api**: A Node.js application that exposes REST endpoints for managing tasks.
- **database**: A PostgreSQL database that stores tasks permanently.
- **cache**: A Redis instance that caches recently accessed tasks for speed.

---

## Setting Up the Project

### Step 1: Create the Project Structure

```bash
mkdir ~/task-manager
cd ~/task-manager
mkdir api
```

Your project will look like this:

```
task-manager/
├── docker-compose.yml
├── api/
│   ├── Dockerfile
│   ├── package.json
│   ├── server.js
│   └── wait-for-it.sh
└── database/
    └── init.sql
```

### Step 2: Create the Node.js API

Create `api/package.json`:

```json
{
  "name": "task-manager-api",
  "version": "1.0.0",
  "description": "A simple task manager API",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "pg": "^8.11.3",
    "redis": "^4.6.10"
  }
}
```

Let us explain each dependency:

- **express**: A popular web framework for Node.js. It makes it easy to create API endpoints.
- **pg**: A PostgreSQL client for Node.js. It lets us connect to and query the database.
- **redis**: A Redis client for Node.js. It lets us store and retrieve cached data.

Create `api/server.js`:

```javascript
const express = require('express');
const { Pool } = require('pg');
const { createClient } = require('redis');

// Create the Express application
const app = express();
app.use(express.json());

// PostgreSQL connection
// "database" is the service name from docker-compose.yml
// Docker DNS resolves "database" to the container's IP address
const pool = new Pool({
  host: process.env.DB_HOST || 'database',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'taskuser',
  password: process.env.DB_PASSWORD || 'taskpass',
  database: process.env.DB_NAME || 'taskdb',
});

// Redis connection
// "cache" is the service name from docker-compose.yml
const redisClient = createClient({
  url: process.env.REDIS_URL || 'redis://cache:6379',
});

// Connect to Redis when the app starts
redisClient.on('error', (err) => console.error('Redis error:', err));
redisClient.connect().then(() => {
  console.log('Connected to Redis');
});

// Health check endpoint
// This tells Docker (and other tools) that the API is working
app.get('/health', async (req, res) => {
  try {
    // Check database connection
    await pool.query('SELECT 1');
    // Check Redis connection
    await redisClient.ping();
    res.json({ status: 'healthy', database: 'connected', cache: 'connected' });
  } catch (error) {
    res.status(500).json({ status: 'unhealthy', error: error.message });
  }
});

// GET /tasks — Retrieve all tasks
app.get('/tasks', async (req, res) => {
  try {
    // First, check if tasks are cached in Redis
    const cachedTasks = await redisClient.get('all_tasks');
    if (cachedTasks) {
      console.log('Returning tasks from cache');
      return res.json(JSON.parse(cachedTasks));
    }

    // If not cached, query the database
    console.log('Querying tasks from database');
    const result = await pool.query(
      'SELECT * FROM tasks ORDER BY created_at DESC'
    );

    // Cache the result in Redis for 60 seconds
    await redisClient.setEx('all_tasks', 60, JSON.stringify(result.rows));

    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching tasks:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// POST /tasks — Create a new task
app.post('/tasks', async (req, res) => {
  try {
    const { title, description } = req.body;

    if (!title) {
      return res.status(400).json({ error: 'Title is required' });
    }

    const result = await pool.query(
      'INSERT INTO tasks (title, description) VALUES ($1, $2) RETURNING *',
      [title, description || '']
    );

    // Clear the cache because the data has changed
    await redisClient.del('all_tasks');

    console.log('Created task:', result.rows[0].id);
    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Error creating task:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// DELETE /tasks/:id — Delete a task
app.delete('/tasks/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query(
      'DELETE FROM tasks WHERE id = $1 RETURNING *',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Task not found' });
    }

    // Clear the cache because the data has changed
    await redisClient.del('all_tasks');

    console.log('Deleted task:', id);
    res.json({ message: 'Task deleted', task: result.rows[0] });
  } catch (error) {
    console.error('Error deleting task:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Task Manager API running on port ${PORT}`);
});
```

Let us walk through the key parts of this code:

1. **Database connection**: We connect to PostgreSQL using the hostname `database`. This is the service name in our `docker-compose.yml`. Docker's DNS automatically resolves this to the database container's IP address.

2. **Redis connection**: We connect to Redis using `redis://cache:6379`. Again, `cache` is the service name.

3. **Health check endpoint** (`/health`): This tests both the database and Redis connections. Docker will use this to know if the API is truly healthy.

4. **GET /tasks**: First checks Redis for cached results. If found, returns them immediately (fast). If not found, queries PostgreSQL and caches the result for 60 seconds.

5. **POST /tasks**: Creates a new task in PostgreSQL and clears the Redis cache so the next GET returns fresh data.

6. **DELETE /tasks/:id**: Deletes a task from PostgreSQL and clears the cache.

### Step 3: Create the Dockerfile for the API

Create `api/Dockerfile`:

```dockerfile
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy package files first (for better caching)
COPY package.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start the application
CMD ["npm", "start"]
```

We use `wget` instead of `curl` for the health check because Alpine Linux includes `wget` by default but not `curl`.

### Step 4: Create the Database Initialization Script

Create a directory and file:

```bash
mkdir database
```

Create `database/init.sql`:

```sql
-- This script runs automatically when the PostgreSQL container
-- starts for the first time. It creates the tasks table.

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some sample data so the API has something to show
INSERT INTO tasks (title, description) VALUES
    ('Learn Docker basics', 'Understand images, containers, and volumes'),
    ('Learn Docker Compose', 'Build multi-container applications'),
    ('Deploy to production', 'Use Docker in a real project');
```

This SQL script runs only when the PostgreSQL container starts for the very first time (when the data volume is empty). If the volume already has data, the script is skipped.

---

## The Complete docker-compose.yml

Now for the main event. Create `docker-compose.yml` in the project root:

```yaml
services:
  # ──────────────────────────────────────────────────
  # API Service — Node.js application
  # ──────────────────────────────────────────────────
  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      DB_HOST: database
      DB_PORT: 5432
      DB_USER: taskuser
      DB_PASSWORD: taskpass
      DB_NAME: taskdb
      REDIS_URL: redis://cache:6379
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_healthy
    networks:
      - app-network

  # ──────────────────────────────────────────────────
  # Database Service — PostgreSQL
  # ──────────────────────────────────────────────────
  database:
    image: postgres:16
    environment:
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: taskpass
      POSTGRES_DB: taskdb
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser -d taskdb"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - app-network

  # ──────────────────────────────────────────────────
  # Cache Service — Redis
  # ──────────────────────────────────────────────────
  cache:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

# Named volumes for persistent data
volumes:
  db-data:

# Custom network
networks:
  app-network:
    driver: bridge
```

Let us go through each service in detail.

### The api Service Explained

```yaml
api:
  build: ./api
```

Build the Docker image from the `./api` directory, using the Dockerfile we created there.

```yaml
  ports:
    - "3000:3000"
```

Map host port 3000 to container port 3000. This lets us access the API from our browser or tools like curl.

```yaml
  environment:
    DB_HOST: database
    DB_PORT: 5432
    DB_USER: taskuser
    DB_PASSWORD: taskpass
    DB_NAME: taskdb
    REDIS_URL: redis://cache:6379
```

These environment variables tell the API how to connect to the database and cache. Notice that `DB_HOST` is set to `database` — the service name. And `REDIS_URL` uses `cache` — another service name. Docker's DNS handles the rest.

```yaml
  depends_on:
    database:
      condition: service_healthy
    cache:
      condition: service_healthy
```

This is crucial. The `depends_on` section tells Docker Compose that the API should not start until both the database and cache are healthy. Without this, the API might start before the database is ready, causing connection errors.

### The database Service Explained

```yaml
database:
  image: postgres:16
```

Use the official PostgreSQL 16 image.

```yaml
  volumes:
    - db-data:/var/lib/postgresql/data
    - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
```

Two volume mounts:

1. `db-data:/var/lib/postgresql/data` — A named volume that persists the database data. Without this, all data would be lost when the container stops.
2. `./database/init.sql:/docker-entrypoint-initdb.d/init.sql` — A bind mount that copies our initialization script into the container. PostgreSQL automatically runs any SQL file in `/docker-entrypoint-initdb.d/` when it starts for the first time.

```yaml
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U taskuser -d taskdb"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 10s
```

The health check uses `pg_isready`, a built-in PostgreSQL utility that checks if the database is accepting connections. Docker will run this command every 10 seconds. After the database reports healthy, the API service (which depends on it) can start.

### The cache Service Explained

```yaml
cache:
  image: redis:7-alpine
```

Use Redis 7 on Alpine Linux (a minimal, small image).

```yaml
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

The health check uses `redis-cli ping`, which returns `PONG` if Redis is working. This is the standard way to check Redis health.

---

## Understanding depends_on and Health Checks

The `depends_on` section controls startup order. Without it, Docker Compose starts all services simultaneously. This is a problem because:

1. The database needs several seconds to initialize before it accepts connections.
2. The API tries to connect to the database immediately when it starts.
3. If the database is not ready, the API crashes.

```
┌──────────── Without depends_on ────────────┐
│                                             │
│   Time 0s:  database starts initializing    │
│   Time 0s:  api starts and tries to connect │
│   Time 0s:  api CRASHES (database not ready)│
│   Time 3s:  database becomes ready          │
│                                             │
│   Result: API crashed before DB was ready   │
└─────────────────────────────────────────────┘

┌──────────── With depends_on + health ──────┐
│                                             │
│   Time 0s:  database starts initializing    │
│   Time 0s:  cache starts initializing       │
│   Time 2s:  cache is healthy                │
│   Time 3s:  database is healthy             │
│   Time 3s:  api starts (both deps healthy)  │
│   Time 3s:  api connects successfully       │
│                                             │
│   Result: Everything works!                 │
└─────────────────────────────────────────────┘
```

### depends_on Without Health Checks

A simple `depends_on` only waits for the container to start, not for the application inside to be ready:

```yaml
# This only waits for the container to start, NOT for the database to be ready
depends_on:
  - database
```

### depends_on With Health Checks (Recommended)

Adding `condition: service_healthy` waits for the health check to pass:

```yaml
# This waits until the database health check passes
depends_on:
  database:
    condition: service_healthy
```

This is the correct approach. Always use health checks with `depends_on` for reliable startup.

---

## The wait-for-it Pattern

Sometimes you cannot add health checks (for example, when using third-party images). An alternative approach is the **wait-for-it** script — a shell script that waits for a network port to become available before starting your application.

Create `api/wait-for-it.sh`:

```bash
#!/bin/sh
# wait-for-it.sh — Wait for a service to become available

HOST="$1"
PORT="$2"
shift 2
CMD="$@"

echo "Waiting for $HOST:$PORT to be ready..."

while ! nc -z "$HOST" "$PORT" 2>/dev/null; do
  echo "  $HOST:$PORT is not ready. Waiting..."
  sleep 1
done

echo "$HOST:$PORT is ready!"
exec $CMD
```

Make it executable:

```bash
chmod +x api/wait-for-it.sh
```

Use it in the Dockerfile:

```dockerfile
# Copy the wait script
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Wait for the database before starting
CMD ["/wait-for-it.sh", "database", "5432", "npm", "start"]
```

The script repeatedly tries to connect to `database:5432`. Once the connection succeeds, it runs `npm start`.

However, with Docker Compose's `depends_on` and health checks (as we did in our example), the wait-for-it approach is usually not needed. The health check approach is simpler and more reliable.

---

## Building and Running the Application

### Step 1: Build and Start

From the `task-manager` directory:

```bash
docker compose up -d --build
```

The `--build` flag forces Docker to build the images. Without it, Docker uses cached images if they exist.

**Output:**

```
[+] Building 15.2s (10/10) FINISHED
 => [api] Building...
 => ...
[+] Running 4/4
 ✔ Network task-manager_app-network  Created
 ✔ Container task-manager-cache-1     Started
 ✔ Container task-manager-database-1  Started
 ✔ Container task-manager-api-1       Started
```

### Step 2: Check Service Status

```bash
docker compose ps
```

**Output:**

```
NAME                       IMAGE              STATUS                    PORTS
task-manager-api-1         task-manager-api   Up 10s (healthy)          0.0.0.0:3000->3000/tcp
task-manager-cache-1       redis:7-alpine     Up 15s (healthy)          6379/tcp
task-manager-database-1    postgres:16        Up 15s (healthy)          5432/tcp
```

All three services are running and healthy.

### Step 3: Test the API

Let us test our API using `curl` (a command-line tool for making HTTP requests).

**Get all tasks** (should return the sample data from init.sql):

```bash
curl http://localhost:3000/tasks
```

**Output:**

```json
[
  {
    "id": 3,
    "title": "Deploy to production",
    "description": "Use Docker in a real project",
    "completed": false,
    "created_at": "2024-01-15T10:30:00.000Z"
  },
  {
    "id": 2,
    "title": "Learn Docker Compose",
    "description": "Build multi-container applications",
    "completed": false,
    "created_at": "2024-01-15T10:30:00.000Z"
  },
  {
    "id": 1,
    "title": "Learn Docker basics",
    "description": "Understand images, containers, and volumes",
    "completed": false,
    "created_at": "2024-01-15T10:30:00.000Z"
  }
]
```

**Create a new task**:

```bash
curl -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Read Chapter 15", "description": "Multi-container apps"}'
```

**Output:**

```json
{
  "id": 4,
  "title": "Read Chapter 15",
  "description": "Multi-container apps",
  "completed": false,
  "created_at": "2024-01-15T10:35:00.000Z"
}
```

**Delete a task**:

```bash
curl -X DELETE http://localhost:3000/tasks/1
```

**Output:**

```json
{
  "message": "Task deleted",
  "task": {
    "id": 1,
    "title": "Learn Docker basics",
    "description": "Understand images, containers, and volumes",
    "completed": false
  }
}
```

**Check the health endpoint**:

```bash
curl http://localhost:3000/health
```

**Output:**

```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected"
}
```

### Step 4: Observe Caching in Action

Run `GET /tasks` twice and watch the logs:

```bash
curl http://localhost:3000/tasks
curl http://localhost:3000/tasks
```

Now check the API logs:

```bash
docker compose logs api --tail 10
```

**Output:**

```
task-manager-api-1  | Querying tasks from database
task-manager-api-1  | Returning tasks from cache
```

The first request queried the database. The second request returned data from Redis cache. This is faster because Redis is an in-memory store.

---

## Working with Logs

Docker Compose makes it easy to view logs from all services.

### Viewing All Logs

```bash
docker compose logs
```

This shows logs from all three services, color-coded:

```
task-manager-database-1  | PostgreSQL init process complete; ready for start up.
task-manager-database-1  | database system is ready to accept connections
task-manager-cache-1     | Ready to accept connections
task-manager-api-1       | Connected to Redis
task-manager-api-1       | Task Manager API running on port 3000
```

### Following Logs in Real Time

```bash
docker compose logs -f
```

Press `Ctrl+C` to stop following.

### Logs for a Specific Service

```bash
# Only database logs
docker compose logs database

# Only API logs with follow
docker compose logs -f api

# Last 20 lines from all services
docker compose logs --tail 20
```

### Debugging a Specific Service

If something is not working, check the service logs first:

```bash
# Check if the database initialized correctly
docker compose logs database | head -30

# Check if the API connected to its dependencies
docker compose logs api

# Check if Redis is accepting connections
docker compose logs cache
```

---

## Stopping and Restarting

### Stop and Remove Everything

```bash
docker compose down
```

This stops all containers, removes them, and removes the network. The database data is preserved in the `db-data` volume.

### Stop Without Removing

```bash
docker compose stop
```

This stops containers but does not remove them. You can restart with `docker compose start`.

### Restart Everything

```bash
docker compose up -d
```

The database still has all its data because we used a named volume.

### Full Reset (Delete Everything Including Data)

```bash
docker compose down -v
```

The `-v` flag removes the named volumes, which deletes all database data. The next `docker compose up -d` will re-run the `init.sql` script because the volume is fresh.

---

## Common Mistakes

### Mistake 1: Not Using depends_on with Health Checks

```yaml
# Wrong: API starts before the database is ready
services:
  api:
    build: ./api
    depends_on:
      - database

# Right: API waits for the database health check to pass
services:
  api:
    build: ./api
    depends_on:
      database:
        condition: service_healthy
```

### Mistake 2: Using localhost in Connection Strings

```javascript
// Wrong: "localhost" refers to the API container itself, not the database
const pool = new Pool({ host: 'localhost', ... });

// Right: Use the service name as the hostname
const pool = new Pool({ host: 'database', ... });
```

### Mistake 3: Forgetting to Rebuild After Code Changes

```bash
# Wrong: this uses the old cached image
docker compose up -d

# Right: rebuild the image after code changes
docker compose up -d --build
```

### Mistake 4: Not Declaring Named Volumes

```yaml
# Wrong: volume "db-data" is used but not declared
services:
  database:
    volumes:
      - db-data:/var/lib/postgresql/data

# Right: declare the volume in the top-level volumes section
services:
  database:
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

### Mistake 5: Hardcoding Credentials in Source Code

```javascript
// Wrong: credentials hardcoded in source code
const pool = new Pool({
  host: 'database',
  user: 'taskuser',
  password: 'taskpass',
});

// Right: use environment variables
const pool = new Pool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});
```

And set the values in `docker-compose.yml`:

```yaml
environment:
  DB_HOST: database
  DB_USER: taskuser
  DB_PASSWORD: taskpass
```

---

## Best Practices

1. **Always use health checks** for services that other services depend on. This prevents race conditions during startup.

2. **Use environment variables** for all configuration. Never hardcode hostnames, ports, or credentials.

3. **Use named volumes** for any data you want to persist (databases, file uploads, etc.).

4. **Use `--build`** when you change application code to ensure the image is rebuilt.

5. **Start with `docker compose logs`** when debugging. The logs almost always contain the answer.

6. **Use meaningful service names** that describe the role: `database` instead of `postgres`, `cache` instead of `redis`.

7. **Keep the init script idempotent**. Use `CREATE TABLE IF NOT EXISTS` instead of `CREATE TABLE` so the script does not fail if run multiple times.

8. **Test the health endpoint** manually with curl to make sure it works before relying on it for health checks.

---

## Quick Summary

In this chapter, you built a real multi-container application with a Node.js API, PostgreSQL database, and Redis cache. The `docker-compose.yml` file defined all three services, their configurations, and their dependencies. You used `depends_on` with `condition: service_healthy` to ensure services start in the correct order. Health checks used `pg_isready` for PostgreSQL and `redis-cli ping` for Redis. The API connected to other services using their service names as hostnames, which Docker's DNS resolved automatically. You tested the API with curl and observed how Redis caching speeds up repeated requests.

---

## Key Points

- Multi-container applications use Docker Compose to define and run multiple services together.
- Services communicate using their service names as hostnames (Docker DNS resolution).
- `depends_on` with `condition: service_healthy` ensures services start only after their dependencies are ready.
- Health checks should verify that the application is truly functional, not just that the process is running.
- PostgreSQL runs SQL files in `/docker-entrypoint-initdb.d/` during first-time initialization.
- Named volumes persist database data across container restarts.
- Redis provides fast in-memory caching to reduce database load.
- Use `docker compose up -d --build` to rebuild images after code changes.
- Use `docker compose logs` as the first debugging step.
- Always use environment variables for connection strings and credentials.

---

## Practice Questions

1. Why do we use `condition: service_healthy` instead of just listing the service in `depends_on`? What would happen without health checks?

2. In the API code, the database connection uses `host: 'database'`. How does Docker know which IP address `database` refers to?

3. What is the purpose of the `init.sql` file, and where must it be mounted in the PostgreSQL container? When does it run?

4. Explain how Redis caching works in this application. What happens when you create a new task — why do we clear the cache?

5. If you run `docker compose down -v` and then `docker compose up -d`, what happens to the data in the database?

---

## Exercises

### Exercise 1: Extend the API

1. Clone the task manager project from this chapter.
2. Add a `PUT /tasks/:id` endpoint that updates a task's title and description.
3. Make sure to clear the Redis cache when a task is updated.
4. Rebuild and test with curl.

### Exercise 2: Add a Fourth Service

1. Add an Adminer service (a web-based database management tool) to the `docker-compose.yml`:
   ```yaml
   adminer:
     image: adminer
     ports:
       - "8080:8080"
   ```
2. Start the stack and access Adminer at `http://localhost:8080`.
3. Log in with the database credentials and browse the tasks table.

### Exercise 3: Simulate a Failure

1. Start the full stack.
2. Stop only the database service: `docker compose stop database`.
3. Try to create a task via curl. What error do you get?
4. Check the API logs. What do they say?
5. Check the health endpoint. What status does it report?
6. Restart the database: `docker compose start database`.
7. Verify that everything recovers.

---

## What Is Next?

You have built a real multi-container application. But we glossed over some important details about networking and volumes in Compose. In the next chapter, you will take a deep dive into Compose networking (how services discover each other, custom networks, and network isolation) and Compose volumes (named volumes, volume declarations, and sharing volumes between services). These concepts are essential for building secure and well-organized applications.
