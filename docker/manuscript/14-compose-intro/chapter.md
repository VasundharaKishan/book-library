# Chapter 14: Introduction to Docker Compose

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Explain why Docker Compose exists and what problem it solves
- Understand the structure of a `docker-compose.yml` file
- Define services, ports, and environment variables in Compose
- Start and stop multi-container applications with a single command
- Use `docker compose up`, `down`, `ps`, `logs`, and `exec`
- Compare Compose commands to their individual Docker equivalents

---

## Why This Chapter Matters

In previous chapters, you learned how to run individual containers with `docker run`. That works fine when you have one or two containers. But real applications usually have more:

- A web server
- An API server
- A database
- Maybe a cache like Redis
- Maybe a message queue

Running each of these with separate `docker run` commands means remembering long commands, creating networks manually, making sure containers start in the right order, and typing the same thing every time you restart your application. This gets tedious fast.

Think of it like cooking a meal. If you have one dish, you can remember the recipe. But if you are preparing a five-course dinner, you need a written menu with instructions for every dish. Docker Compose is that menu — a single file that describes your entire application, and a single command to bring it all to life.

---

## What Is Docker Compose?

**Docker Compose** is a tool for defining and running multi-container Docker applications. Instead of typing multiple `docker run` commands, you describe your entire application in a YAML file called `docker-compose.yml`, and then start everything with one command: `docker compose up`.

### The Problem Without Compose

Let us say you have a web application that needs nginx and PostgreSQL. Without Compose, you would type:

```bash
# Step 1: Create a network
docker network create my-app-network

# Step 2: Start the database
docker run -d \
  --name my-postgres \
  --network my-app-network \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=myapp \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16

# Step 3: Start the web server
docker run -d \
  --name my-web \
  --network my-app-network \
  -p 8080:80 \
  nginx
```

That is three commands with many flags. And when you want to stop everything:

```bash
docker rm -f my-web my-postgres
docker network rm my-app-network
```

Now imagine doing this every day. Or imagine adding three more services. It becomes unmanageable.

### The Solution with Compose

The same setup in a `docker-compose.yml` file:

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"

  database:
    image: postgres:16
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

And to start everything:

```bash
docker compose up -d
```

That is it. One file, one command. Docker Compose creates the network automatically, starts both containers, and connects them. To stop everything:

```bash
docker compose down
```

---

## Understanding the docker-compose.yml File

The `docker-compose.yml` file is written in **YAML** (Yet Another Markup Language). YAML is a human-readable format for configuration files. If you have never seen YAML before, here are the basics:

- YAML uses **indentation** (spaces, not tabs) to show structure.
- A **key-value pair** looks like `key: value`.
- A **list** uses dashes: `- item`.
- Comments start with `#`.

### The Structure

Every `docker-compose.yml` file follows this structure:

```yaml
services:
  service-name-1:
    # Configuration for service 1
  service-name-2:
    # Configuration for service 2

volumes:
  # Named volumes used by services

networks:
  # Custom networks (optional)
```

Let us break down each section.

### The services Section

The `services` section is the heart of the file. Each service represents one container. The service name is what you choose — it becomes the container's hostname on the Docker network.

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"

  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://myuser:mypassword@database:5432/myapp

  database:
    image: postgres:16
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: myapp
```

This defines three services:

1. **web**: Uses the official `nginx` image and maps port 8080 to port 80.
2. **api**: Builds from a Dockerfile in the `./api` directory and passes an environment variable.
3. **database**: Uses the official `postgres:16` image with configuration via environment variables.

### image vs. build

There are two ways to specify what a service runs:

**Using `image`**: Pull a pre-built image from a registry (like Docker Hub):

```yaml
services:
  web:
    image: nginx:latest
```

**Using `build`**: Build an image from a Dockerfile in your project:

```yaml
services:
  api:
    build: ./api
```

This tells Compose to look for a Dockerfile in the `./api` directory and build the image.

You can also specify more build options:

```yaml
services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile.dev
```

- `context`: The directory containing the Dockerfile and files to copy.
- `dockerfile`: The name of the Dockerfile (if it is not the default `Dockerfile`).

### ports

The `ports` section maps host ports to container ports, just like `-p` in `docker run`:

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"        # Host port 8080 -> Container port 80
      - "8443:443"       # Host port 8443 -> Container port 443
```

Always use quotes around port mappings in YAML. Without quotes, YAML might interpret `80:80` as a base-60 number (a quirk of the YAML specification).

### environment

The `environment` section sets environment variables inside the container, just like `-e` in `docker run`:

```yaml
services:
  database:
    image: postgres:16
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: myapp
```

You can also write it as a list:

```yaml
services:
  database:
    image: postgres:16
    environment:
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypassword
      - POSTGRES_DB=myapp
```

Both formats are equivalent. Choose the one you find more readable.

### volumes

The `volumes` section mounts storage, just like `-v` in `docker run`:

```yaml
services:
  database:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data    # Named volume
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # Bind mount

volumes:
  pgdata:    # Declare the named volume
```

Named volumes (like `pgdata`) must be declared in a top-level `volumes` section at the bottom of the file.

### A Complete Example

Here is a complete `docker-compose.yml` with all the pieces together:

```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api

  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://myuser:mypassword@database:5432/myapp
      REDIS_URL: redis://cache:6379
    depends_on:
      - database
      - cache

  database:
    image: postgres:16
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data

  cache:
    image: redis:7

volumes:
  pgdata:
```

```
┌──────────────────────────────────────────────────┐
│              docker-compose.yml                   │
│                                                   │
│   ┌────────┐    ┌────────┐    ┌──────────┐       │
│   │  web   │───>│  api   │───>│ database │       │
│   │ :8080  │    │ :3000  │    │ postgres │       │
│   │ nginx  │    │ node   │    │ :5432    │       │
│   └────────┘    └───┬────┘    └──────────┘       │
│                     │                             │
│                     │         ┌──────────┐       │
│                     └────────>│  cache   │       │
│                               │  redis   │       │
│                               │  :6379   │       │
│                               └──────────┘       │
│                                                   │
│   All services share one auto-created network     │
└──────────────────────────────────────────────────┘
```

---

## Essential Compose Commands

Now that you understand the file, let us learn the commands to work with it.

### docker compose up — Start Everything

```bash
docker compose up -d
```

This command:

1. Reads `docker-compose.yml` in the current directory.
2. Creates a network for the project (if one does not exist).
3. Builds images (for services with `build`).
4. Creates and starts all containers.
5. The `-d` flag runs everything in the background (detached mode).

**Output:**

```
[+] Running 4/4
 ✔ Network myapp_default     Created
 ✔ Container myapp-cache-1    Started
 ✔ Container myapp-database-1 Started
 ✔ Container myapp-api-1      Started
 ✔ Container myapp-web-1      Started
```

Notice that Docker Compose names things with a prefix. The prefix is the name of the directory your `docker-compose.yml` is in. If your project is in a folder called `myapp`, the containers are named `myapp-web-1`, `myapp-database-1`, and so on.

Without `-d`, Compose runs in the foreground and you see logs from all services in your terminal. Press `Ctrl+C` to stop everything.

```bash
# Foreground mode (logs stream to terminal)
docker compose up

# Background mode (runs silently)
docker compose up -d
```

### docker compose down — Stop Everything

```bash
docker compose down
```

This command:

1. Stops all containers defined in the Compose file.
2. Removes the containers.
3. Removes the network.
4. Does **not** remove volumes (your data is safe).

**Output:**

```
[+] Running 5/5
 ✔ Container myapp-web-1      Removed
 ✔ Container myapp-api-1      Removed
 ✔ Container myapp-cache-1    Removed
 ✔ Container myapp-database-1 Removed
 ✔ Network myapp_default      Removed
```

To also remove volumes (delete all data):

```bash
docker compose down -v
```

The `-v` flag removes named volumes. Use this carefully — it deletes your database data.

### docker compose ps — List Running Services

```bash
docker compose ps
```

**Output:**

```
NAME                 IMAGE        COMMAND                  SERVICE    STATUS    PORTS
myapp-api-1          myapp-api    "node server.js"         api        running   0.0.0.0:3000->3000/tcp
myapp-cache-1        redis:7      "docker-entrypoint..."   cache      running   6379/tcp
myapp-database-1     postgres:16  "docker-entrypoint..."   database   running   5432/tcp
myapp-web-1          nginx:latest "/docker-entrypoint..."  web        running   0.0.0.0:8080->80/tcp
```

This shows all services, their status, and port mappings.

### docker compose logs — View Logs

```bash
# Logs from all services
docker compose logs

# Logs from a specific service
docker compose logs api

# Follow logs in real time
docker compose logs -f

# Follow logs for a specific service
docker compose logs -f api

# Last 20 lines from all services
docker compose logs --tail 20

# Last 10 lines from a specific service, following
docker compose logs -f --tail 10 database
```

Compose logs are color-coded by service, making it easy to tell which service produced which line:

```
myapp-api-1       | Server started on port 3000
myapp-database-1  | PostgreSQL init process complete
myapp-cache-1     | Ready to accept connections
myapp-web-1       | nginx started
```

### docker compose exec — Run Commands in a Service

```bash
# Open a shell in the api service
docker compose exec api sh

# Run a single command in the database service
docker compose exec database psql -U myuser -d myapp

# Check the nginx configuration
docker compose exec web nginx -t
```

Notice the difference from `docker exec`:

- `docker exec` uses the **container name**: `docker exec -it myapp-api-1 sh`
- `docker compose exec` uses the **service name**: `docker compose exec api sh`

The service name is simpler and does not depend on the project prefix.

### docker compose build — Build Images

```bash
# Build all services that have "build" defined
docker compose build

# Build a specific service
docker compose build api

# Build with no cache (fresh build)
docker compose build --no-cache
```

### docker compose restart — Restart Services

```bash
# Restart all services
docker compose restart

# Restart a specific service
docker compose restart api
```

---

## Compose vs. Individual Docker Commands

Here is a side-by-side comparison to show how much simpler Compose makes things:

```
┌────────────────────────────────┬───────────────────────────────────┐
│  Without Compose               │  With Compose                     │
├────────────────────────────────┼───────────────────────────────────┤
│ docker network create mynet    │ (automatic)                       │
│                                │                                   │
│ docker run -d                  │ docker compose up -d              │
│   --name db                    │                                   │
│   --network mynet              │ (Everything defined in            │
│   -e POSTGRES_USER=user        │  docker-compose.yml)              │
│   -e POSTGRES_PASSWORD=pass    │                                   │
│   -v pgdata:/var/lib/...       │                                   │
│   postgres:16                  │                                   │
│                                │                                   │
│ docker run -d                  │                                   │
│   --name api                   │                                   │
│   --network mynet              │                                   │
│   -p 3000:3000                 │                                   │
│   -e DATABASE_URL=...          │                                   │
│   my-api                       │                                   │
├────────────────────────────────┼───────────────────────────────────┤
│ docker logs db                 │ docker compose logs database      │
│ docker logs api                │ docker compose logs api           │
│                                │ docker compose logs (all)         │
├────────────────────────────────┼───────────────────────────────────┤
│ docker exec -it db psql ...    │ docker compose exec database psql │
├────────────────────────────────┼───────────────────────────────────┤
│ docker rm -f api db            │ docker compose down               │
│ docker network rm mynet        │                                   │
├────────────────────────────────┼───────────────────────────────────┤
│ (repeat all commands           │ docker compose up -d              │
│  to start again)               │ (one command restarts everything) │
└────────────────────────────────┴───────────────────────────────────┘
```

The key advantages of Compose:

1. **Declarative**: You describe what you want, not how to do it.
2. **Repeatable**: The same file produces the same result every time.
3. **Shareable**: You can share the file with your team, and everyone gets the same setup.
4. **Version controlled**: The file goes into Git, so changes are tracked.
5. **One command**: Start, stop, and manage everything with simple commands.

---

## A Hands-On Example

Let us build a simple example from scratch. We will run nginx with a custom HTML page and a PostgreSQL database.

### Step 1: Create the Project Directory

```bash
mkdir ~/compose-demo
cd ~/compose-demo
```

### Step 2: Create a Simple HTML Page

```bash
mkdir html
```

Create `html/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Compose Demo</title>
</head>
<body>
    <h1>Hello from Docker Compose!</h1>
    <p>This page is served by nginx running in a Docker container.</p>
    <p>A PostgreSQL database is running in another container.</p>
</body>
</html>
```

### Step 3: Create the docker-compose.yml

Create `docker-compose.yml` in the project root:

```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro

  database:
    image: postgres:16
    environment:
      POSTGRES_USER: demo
      POSTGRES_PASSWORD: demo123
      POSTGRES_DB: demoapp
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

Let us explain every line:

- `services:` — Start of the services section.
- `web:` — A service named "web."
- `image: nginx:latest` — Use the official nginx image.
- `ports: - "8080:80"` — Map host port 8080 to container port 80.
- `volumes: - ./html:/usr/share/nginx/html:ro` — Mount the local `html` directory into the container. The `:ro` means read-only (the container cannot modify your files).
- `database:` — A service named "database."
- `image: postgres:16` — Use PostgreSQL 16.
- `environment:` — Set database configuration via environment variables.
- `volumes: - db-data:/var/lib/postgresql/data` — Persist database data in a named volume.
- `volumes: db-data:` — Declare the named volume at the top level.

### Step 4: Start the Application

```bash
docker compose up -d
```

**Output:**

```
[+] Running 3/3
 ✔ Network compose-demo_default       Created
 ✔ Container compose-demo-database-1  Started
 ✔ Container compose-demo-web-1       Started
```

### Step 5: Verify Everything Is Running

```bash
docker compose ps
```

**Output:**

```
NAME                        IMAGE         STATUS    PORTS
compose-demo-database-1     postgres:16   running   5432/tcp
compose-demo-web-1          nginx:latest  running   0.0.0.0:8080->80/tcp
```

Visit `http://localhost:8080` in your browser. You should see your HTML page.

### Step 6: Connect to the Database

```bash
docker compose exec database psql -U demo -d demoapp
```

**Output:**

```
psql (16.1)
Type "help" for help.

demoapp=>
```

You are connected. Type `\q` to exit.

### Step 7: View the Logs

```bash
docker compose logs
```

You will see logs from both services, color-coded.

### Step 8: Stop Everything

```bash
docker compose down
```

**Output:**

```
[+] Running 3/3
 ✔ Container compose-demo-web-1       Removed
 ✔ Container compose-demo-database-1  Removed
 ✔ Network compose-demo_default       Removed
```

Everything is stopped and cleaned up. Your database data is preserved in the `db-data` volume and will be there when you run `docker compose up -d` again.

---

## Common Mistakes

### Mistake 1: Using Tabs Instead of Spaces in YAML

YAML does not allow tabs for indentation. Use spaces only. Most editors can be configured to insert spaces when you press the Tab key.

```yaml
# Wrong (uses a tab)
services:
	web:    # <-- This is a tab. YAML will reject this.

# Right (uses spaces)
services:
  web:     # <-- This uses 2 spaces. YAML accepts this.
```

### Mistake 2: Wrong Indentation Level

YAML is very strict about indentation. Every level must be indented consistently.

```yaml
# Wrong: ports is at the wrong level
services:
  web:
    image: nginx
  ports:              # <-- Wrong! This should be under "web", not at the same level
    - "8080:80"

# Right
services:
  web:
    image: nginx
    ports:            # <-- Correct! Indented under "web"
      - "8080:80"
```

### Mistake 3: Forgetting to Quote Port Numbers

```yaml
# Potentially wrong (YAML may misinterpret this)
ports:
  - 80:80

# Right (always quote port mappings)
ports:
  - "80:80"
```

### Mistake 4: Forgetting the Top-Level volumes Section

```yaml
# Wrong: uses a named volume but does not declare it
services:
  database:
    volumes:
      - pgdata:/var/lib/postgresql/data
# Missing: volumes section at the bottom

# Right: declare the volume
services:
  database:
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### Mistake 5: Running Compose from the Wrong Directory

Docker Compose looks for `docker-compose.yml` in the current directory. If you run `docker compose up` from the wrong directory, it will not find the file.

```bash
# Wrong: not in the project directory
cd ~
docker compose up
# Error: no configuration file provided

# Right: navigate to the project directory first
cd ~/myproject
docker compose up
```

---

## Best Practices

1. **Use meaningful service names**. Name services by their role: `web`, `api`, `database`, `cache`, not `service1`, `service2`.

2. **Always specify image versions**. Use `postgres:16` instead of `postgres:latest`. This ensures everyone gets the same version.

3. **Use named volumes for data you want to keep**. Database data should always be in a named volume.

4. **Use environment variables for configuration**. Do not hardcode values that might change between environments.

5. **Keep your `docker-compose.yml` in version control**. Commit it to Git so your team can use it.

6. **Use `docker compose down` instead of stopping containers individually**. This ensures clean shutdown and network removal.

7. **Organize your project** with the Compose file at the root and subdirectories for each service.

```
my-project/
├── docker-compose.yml
├── api/
│   ├── Dockerfile
│   ├── package.json
│   └── server.js
├── web/
│   └── index.html
└── database/
    └── init.sql
```

---

## Quick Summary

Docker Compose lets you define multi-container applications in a single YAML file and manage them with simple commands. The `docker-compose.yml` file defines services (containers), their images or build instructions, ports, environment variables, and volumes. Use `docker compose up -d` to start everything, `docker compose down` to stop everything, `docker compose ps` to list services, `docker compose logs` to view logs, and `docker compose exec` to run commands inside services. Compose automatically creates a network for your services, so they can find each other by name.

---

## Key Points

- Docker Compose replaces multiple `docker run` commands with a single YAML file.
- The `docker-compose.yml` file has three main sections: `services`, `volumes`, and `networks`.
- Each service can use `image` (pre-built) or `build` (from Dockerfile).
- Port mappings use the same `host:container` format as `docker run -p`.
- Compose automatically creates a default network for all services.
- `docker compose up -d` starts all services in the background.
- `docker compose down` stops and removes all services and networks.
- `docker compose logs` shows output from all services.
- `docker compose exec service-name command` runs commands inside a service.
- YAML uses spaces for indentation, never tabs.

---

## Practice Questions

1. What problem does Docker Compose solve? Why would you use it instead of individual `docker run` commands?

2. What is the difference between `image` and `build` in a service definition? When would you use each one?

3. You run `docker compose up -d` and then make changes to your `docker-compose.yml`. What command do you run to apply the changes?

4. What does `docker compose down -v` do differently from `docker compose down`? When would you use the `-v` flag, and when would you avoid it?

5. In a `docker-compose.yml` file, the `database` service uses a named volume called `pgdata`. Where must `pgdata` be declared, and why?

---

## Exercises

### Exercise 1: Your First Compose File

1. Create a new directory called `exercise-compose`.
2. Write a `docker-compose.yml` that runs nginx with port 9090 mapped to port 80.
3. Start the service with `docker compose up -d`.
4. Verify it is running with `docker compose ps`.
5. Visit `http://localhost:9090` in your browser.
6. View the logs with `docker compose logs`.
7. Stop everything with `docker compose down`.

### Exercise 2: Two Services

1. Create a `docker-compose.yml` with two services: nginx (web) and Redis (cache).
2. Map nginx to port 8080.
3. Start both services.
4. Verify both are running.
5. Use `docker compose exec` to connect to Redis and run `redis-cli ping`.
6. View logs from only the cache service.
7. Stop everything.

### Exercise 3: Build and Run

1. Create a simple Node.js application (a file called `server.js` that responds with "Hello from Compose").
2. Create a Dockerfile for it.
3. Write a `docker-compose.yml` that uses `build: .` to build and run your app.
4. Start the application with `docker compose up -d`.
5. Test it by visiting the appropriate URL.
6. Make a change to `server.js`, rebuild with `docker compose build`, and restart.
7. Stop everything.

---

## What Is Next?

You now know how to define multi-container applications with Docker Compose. In the next chapter, you will put this knowledge to work by building a real application with three services: a Node.js API, a PostgreSQL database, and a Redis cache. You will see how to wire everything together, handle service dependencies, and test the full stack.
