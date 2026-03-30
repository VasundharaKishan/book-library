# Chapter 16: Compose Networking and Volumes

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Explain how the default Compose network works
- Create and configure custom networks in Compose
- Use service names as hostnames for service discovery
- Declare and use named volumes in Compose
- Share volumes between multiple services
- Use external volumes created outside of Compose
- Isolate services using multiple networks
- Understand network isolation between different Compose projects

---

## Why This Chapter Matters

In the previous chapters, networking and volumes "just worked" because Compose handled them automatically. But as your applications grow more complex, you need to understand what is happening behind the scenes. You need to answer questions like:

- How do my services find each other?
- Can I prevent certain services from communicating?
- Where is my data actually stored?
- Can two different Compose projects share the same database?

Think of this chapter as learning how the plumbing and electrical wiring work in your house. When everything is fine, you do not think about them. But when you need to add a new room, fix a leak, or understand why the lights went out, you need to know how the systems work.

---

## The Default Compose Network

When you run `docker compose up`, Compose automatically creates a network for your project. Every service in the Compose file is connected to this network. You do not have to do anything — it just happens.

### How the Default Network Is Named

The default network name follows this pattern:

```
<project-directory-name>_default
```

For example, if your project is in a folder called `my-app`:

```bash
cd ~/my-app
docker compose up -d
```

Docker creates a network called `my-app_default`.

You can verify this:

```bash
docker network ls
```

**Output:**

```
NETWORK ID     NAME               DRIVER    SCOPE
a1b2c3d4e5f6   bridge             bridge    local
f6e5d4c3b2a1   host               host      local
d7e8f9a0b1c2   my-app_default     bridge    local
1a2b3c4d5e6f   none               null      local
```

### What the Default Network Provides

The default network gives you:

1. **Automatic DNS resolution**: Every service can reach every other service by its service name.
2. **Isolation from other projects**: Services in one Compose project cannot reach services in another.
3. **Isolation from standalone containers**: Standalone containers (started with `docker run`) are on the default bridge network, not your Compose network.

```
┌──────────────────────────────────────────┐
│         my-app_default network           │
│                                           │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│   │   web    │  │   api   │  │   db    │ │
│   │         ◄──►         ◄──►         │ │
│   └─────────┘  └─────────┘  └─────────┘ │
│                                           │
│   All services can reach each other       │
│   by name: "web", "api", "db"            │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│       other-project_default network      │
│                                           │
│   ┌─────────┐  ┌─────────┐              │
│   │  frontend│  │ backend │              │
│   │         ◄──►         │              │
│   └─────────┘  └─────────┘              │
│                                           │
│   Cannot reach services in my-app         │
└──────────────────────────────────────────┘
```

---

## Service Discovery: Service Name = Hostname

This is one of the most important concepts in Docker Compose networking. When you define a service in `docker-compose.yml`, the service name automatically becomes a hostname that other services can use.

### How It Works

```yaml
services:
  api:
    image: my-api
    environment:
      DATABASE_HOST: database    # <-- use the service name
      REDIS_HOST: cache          # <-- use the service name

  database:
    image: postgres:16

  cache:
    image: redis:7
```

Inside the `api` container:

- The hostname `database` resolves to the IP address of the `database` container.
- The hostname `cache` resolves to the IP address of the `cache` container.

This works because Docker runs a built-in DNS server for each Compose network. When a container asks "what is the IP address of `database`?", Docker's DNS server responds with the correct IP address.

```
┌───────────────────────────────────────────┐
│   Inside the "api" container              │
│                                            │
│   ping database                            │
│     │                                      │
│     ▼                                      │
│   Docker DNS Server                        │
│     │                                      │
│     ▼                                      │
│   "database" = 172.18.0.3                  │
│     │                                      │
│     ▼                                      │
│   PING 172.18.0.3 ... reply!              │
│                                            │
│   The service name IS the hostname         │
└───────────────────────────────────────────┘
```

### Connection String Examples

Here is how you would configure common applications to connect to other services:

```yaml
services:
  app:
    environment:
      # PostgreSQL connection
      DATABASE_URL: postgres://user:pass@database:5432/mydb

      # Redis connection
      REDIS_URL: redis://cache:6379

      # MongoDB connection
      MONGO_URL: mongodb://mongo:27017/mydb

      # MySQL connection
      MYSQL_HOST: mysql-db
      MYSQL_PORT: 3306
```

In every case, the hostname is the service name from the Compose file. The port is the container's internal port (not any mapped host port).

### An Important Distinction: Internal vs. External Ports

When services communicate with each other inside the Compose network, they use the **container port** (the internal port). Port mapping (`ports:`) only applies to access from outside Docker (your host machine).

```yaml
services:
  api:
    ports:
      - "8080:3000"    # External: access via localhost:8080
    environment:
      DATABASE_URL: postgres://user:pass@database:5432/mydb
      # Internal: connects to database:5432 (container port)

  database:
    image: postgres:16
    # No ports mapping needed! The API connects internally.
    # Only map ports if you need access from your host machine.
```

```
┌──────────────────────────────────────────────────┐
│                                                   │
│   Your Browser ──> localhost:8080 ──> api:3000   │
│   (external access uses mapped port 8080)        │
│                                                   │
│   api container ──> database:5432                │
│   (internal access uses container port 5432)     │
│                                                   │
│   api container ──> cache:6379                   │
│   (internal access uses container port 6379)     │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

## Custom Networks in Compose

While the default network works for simple applications, custom networks give you more control — especially when you need to isolate certain services from each other.

### Defining Custom Networks

```yaml
services:
  web:
    image: nginx
    networks:
      - frontend

  api:
    image: my-api
    networks:
      - frontend
      - backend

  database:
    image: postgres:16
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```

This creates two networks:

- **frontend**: Contains `web` and `api`.
- **backend**: Contains `api` and `database`.

```
┌─────────────────────────────────────────────────┐
│                                                  │
│   frontend network         backend network       │
│   ┌──────────────┐        ┌──────────────┐      │
│   │              │        │              │      │
│   │  web ◄──────►│ api ◄──►│  database   │      │
│   │              │        │              │      │
│   └──────────────┘        └──────────────┘      │
│                                                  │
│   web can reach api:       Yes (frontend)        │
│   api can reach database:  Yes (backend)         │
│   web can reach database:  No (different nets)   │
│                                                  │
└─────────────────────────────────────────────────┘
```

The key benefit: the `web` service cannot directly communicate with the `database`. It must go through the `api` service. This is a security best practice — the database is only accessible from the services that need it.

### Why Isolate Services?

Consider a security scenario. If an attacker compromises your web server, they can reach anything on the same network. With network isolation:

- If `web` is compromised, the attacker can only reach `api`, not `database`.
- The `database` is protected behind the `backend` network.
- The `api` acts as a gatekeeper between the two networks.

### Network Configuration Options

You can configure networks with additional options:

```yaml
networks:
  frontend:
    driver: bridge
    name: my-frontend-net     # Custom name instead of project prefix

  backend:
    driver: bridge
    ipam:                      # IP Address Management
      config:
        - subnet: 172.28.0.0/16
```

- `name`: Override the auto-generated network name.
- `ipam`: Customize the IP address range for the network.

---

## Named Volumes in Compose

Named volumes are Docker-managed storage that persist data across container restarts. In Compose, you declare named volumes in two places:

1. In the service definition (where the volume is mounted).
2. In the top-level `volumes` section (where the volume is declared).

### Declaring and Using Named Volumes

```yaml
services:
  database:
    image: postgres:16
    volumes:
      - db-data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis-data:/data

volumes:
  db-data:
  redis-data:
```

Let us trace what happens:

1. Compose sees `db-data:/var/lib/postgresql/data` in the `database` service.
2. It looks for `db-data` in the top-level `volumes` section.
3. If the volume does not exist, Docker creates it.
4. Docker mounts the volume at `/var/lib/postgresql/data` inside the container.
5. Any data PostgreSQL writes to that directory is stored in the volume.
6. When you run `docker compose down`, the containers are removed but the volume stays.
7. When you run `docker compose up` again, the same volume is mounted, and all data is still there.

### Volume Lifecycle

```
┌────────────── Volume Lifecycle ──────────────────┐
│                                                   │
│   docker compose up -d                            │
│     └──> Volume "db-data" created (if new)        │
│     └──> Volume mounted to container              │
│                                                   │
│   Application writes data                         │
│     └──> Data stored in volume                    │
│                                                   │
│   docker compose down                             │
│     └──> Container removed                        │
│     └──> Volume KEPT (data preserved)             │
│                                                   │
│   docker compose up -d (again)                    │
│     └──> Same volume mounted                      │
│     └──> All data still there!                    │
│                                                   │
│   docker compose down -v                          │
│     └──> Container removed                        │
│     └──> Volume DELETED (data gone!)              │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Volume Configuration Options

Named volumes can have configuration:

```yaml
volumes:
  db-data:
    driver: local              # The default driver

  important-data:
    driver: local
    name: my-production-data   # Custom name (not prefixed with project name)

  existing-volume:
    external: true             # Volume must already exist
```

- `driver`: The storage driver. `local` is the default and stores data on the host filesystem.
- `name`: Override the auto-generated name. By default, Compose names volumes as `<project>_<volume>`.
- `external: true`: The volume must already exist before you run `docker compose up`. Compose will not create it.

---

## Sharing Volumes Between Services

Sometimes multiple services need access to the same files. You can mount the same volume in multiple services.

### Example: Shared Upload Directory

```yaml
services:
  api:
    image: my-api
    volumes:
      - uploads:/app/uploads     # API writes uploaded files here

  processor:
    image: my-processor
    volumes:
      - uploads:/data/incoming   # Processor reads files from here

volumes:
  uploads:
```

```
┌──────────────────────────────────────────┐
│                                           │
│   ┌────────────┐    ┌────────────┐       │
│   │   api       │    │  processor  │       │
│   │             │    │             │       │
│   │ /app/uploads│    │/data/incoming│      │
│   │      │      │    │      │       │      │
│   └──────┼──────┘    └──────┼───────┘      │
│          │                  │               │
│          └────────┬─────────┘               │
│                   │                         │
│           ┌───────▼────────┐               │
│           │  uploads volume │               │
│           │  (shared data)  │               │
│           └────────────────┘               │
│                                           │
│   api writes a file -> processor can      │
│   read the same file immediately          │
└──────────────────────────────────────────┘
```

Both containers see the same files. When the `api` service saves an uploaded file, the `processor` service can immediately read it.

### Example: Shared Configuration

```yaml
services:
  web:
    image: nginx
    volumes:
      - shared-config:/etc/nginx/conf.d:ro

  api:
    image: my-api
    volumes:
      - shared-config:/etc/app/config:ro

  config-generator:
    image: my-config-tool
    volumes:
      - shared-config:/output     # This service writes the config

volumes:
  shared-config:
```

The `config-generator` writes configuration files to the shared volume. Both `web` and `api` read from it. The `:ro` (read-only) flag prevents them from accidentally modifying the configuration.

### Read-Only Volumes

Append `:ro` to a volume mount to make it read-only inside the container:

```yaml
services:
  web:
    volumes:
      - static-files:/usr/share/nginx/html:ro
```

The container can read files from this volume but cannot create, modify, or delete them. This is a good security practice for services that only need to read data.

---

## External Volumes

An **external volume** is a volume that exists outside of Docker Compose — you created it manually or it belongs to another project. Compose will not create or delete it.

### Creating an External Volume

```bash
docker volume create shared-database
```

### Using an External Volume in Compose

```yaml
services:
  database:
    image: postgres:16
    volumes:
      - shared-database:/var/lib/postgresql/data

volumes:
  shared-database:
    external: true
```

The `external: true` flag tells Compose:

- Do **not** create this volume — it must already exist.
- Do **not** delete this volume on `docker compose down -v`.

If the volume does not exist, `docker compose up` will fail with an error:

```
ERROR: Volume shared-database declared as external, but could not be found.
```

### Why Use External Volumes?

1. **Sharing data between Compose projects**: Two different Compose projects can use the same external volume to share data.
2. **Protecting critical data**: External volumes are not deleted by `docker compose down -v`.
3. **Using pre-populated volumes**: You can create a volume, populate it with data, and then use it in Compose.

### Sharing a Volume Between Compose Projects

**Project A** (`~/project-a/docker-compose.yml`):

```yaml
services:
  writer:
    image: my-writer-app
    volumes:
      - shared-data:/data

volumes:
  shared-data:
    external: true
```

**Project B** (`~/project-b/docker-compose.yml`):

```yaml
services:
  reader:
    image: my-reader-app
    volumes:
      - shared-data:/data:ro

volumes:
  shared-data:
    external: true
```

Both projects use the same external volume `shared-data`. Project A writes to it, and Project B reads from it.

```
┌─────────────────┐        ┌─────────────────┐
│   Project A      │        │   Project B      │
│                  │        │                  │
│   writer ────────┼────────┼──── reader       │
│   /data (rw)     │        │   /data (ro)     │
│                  │        │                  │
└────────┬─────────┘        └────────┬─────────┘
         │                           │
         └─────────┬─────────────────┘
                   │
           ┌───────▼────────┐
           │  shared-data    │
           │  (external vol) │
           └────────────────┘
```

---

## Network Isolation Between Compose Projects

By default, each Compose project gets its own isolated network. Services in Project A cannot reach services in Project B, and vice versa.

### Demonstrating Isolation

**Project A** (`~/project-a/docker-compose.yml`):

```yaml
services:
  web-a:
    image: nginx
```

**Project B** (`~/project-b/docker-compose.yml`):

```yaml
services:
  web-b:
    image: nginx
```

When both are running:

```bash
# Start both projects
cd ~/project-a && docker compose up -d
cd ~/project-b && docker compose up -d

# Check networks
docker network ls
```

**Output:**

```
NETWORK ID     NAME                  DRIVER    SCOPE
...
d1e2f3a4b5c6   project-a_default     bridge    local
a6b5c4d3e2f1   project-b_default     bridge    local
```

Two separate networks. `web-a` cannot reach `web-b`:

```bash
# From inside web-a, try to reach web-b
docker compose -f ~/project-a/docker-compose.yml exec web-a ping -c 1 web-b
# ping: web-b: Name or service not known
```

### Connecting Compose Projects with External Networks

If you need services from different Compose projects to communicate, use an external network:

**Step 1: Create the external network**

```bash
docker network create shared-network
```

**Step 2: Use it in both projects**

**Project A** (`~/project-a/docker-compose.yml`):

```yaml
services:
  api-a:
    image: my-api
    networks:
      - shared

networks:
  shared:
    external: true
    name: shared-network
```

**Project B** (`~/project-b/docker-compose.yml`):

```yaml
services:
  api-b:
    image: my-api
    networks:
      - shared

networks:
  shared:
    external: true
    name: shared-network
```

Now `api-a` and `api-b` are on the same network and can communicate using their service names.

---

## Putting It All Together: A Complete Example

Let us build a Compose configuration that uses custom networks, named volumes, and shared volumes.

```yaml
services:
  # ──────────────────────────────────────────
  # Frontend — Nginx serving static files
  # ──────────────────────────────────────────
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - static-assets:/usr/share/nginx/html:ro
    networks:
      - frontend
    depends_on:
      - api

  # ──────────────────────────────────────────
  # API — Node.js application
  # ──────────────────────────────────────────
  api:
    build: ./api
    ports:
      - "3000:3000"
    volumes:
      - uploads:/app/uploads
    environment:
      DB_HOST: database
      REDIS_URL: redis://cache:6379
    networks:
      - frontend
      - backend
    depends_on:
      database:
        condition: service_healthy
      cache:
        condition: service_healthy

  # ──────────────────────────────────────────
  # Database — PostgreSQL
  # ──────────────────────────────────────────
  database:
    image: postgres:16
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
      POSTGRES_DB: appdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  # ──────────────────────────────────────────
  # Cache — Redis
  # ──────────────────────────────────────────
  cache:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  # ──────────────────────────────────────────
  # Asset Builder — Generates static files
  # ──────────────────────────────────────────
  asset-builder:
    build: ./assets
    volumes:
      - static-assets:/output
    profiles:
      - build

# ──────────────────────────────────────────
# Volumes
# ──────────────────────────────────────────
volumes:
  db-data:          # PostgreSQL data
  redis-data:       # Redis persistence
  uploads:          # User-uploaded files
  static-assets:    # Built frontend assets (shared between builder and web)

# ──────────────────────────────────────────
# Networks
# ──────────────────────────────────────────
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```

Let us trace the network isolation:

```
┌───────────────────────────────────────────────────────┐
│                                                        │
│   frontend network              backend network        │
│   ┌──────────┐                 ┌──────────┐           │
│   │          │                 │          │           │
│   │  web  ◄──┤──► api ◄───────┤──► database│          │
│   │  :8080   │                 │  :5432    │           │
│   │          │                 │          │           │
│   └──────────┘                 │  cache    │           │
│                                │  :6379    │           │
│                                │          │           │
│                                └──────────┘           │
│                                                        │
│   web -> api:        Yes (frontend)                   │
│   web -> database:   No  (different networks)         │
│   web -> cache:      No  (different networks)         │
│   api -> database:   Yes (backend)                    │
│   api -> cache:      Yes (backend)                    │
│   api -> web:        Yes (frontend)                   │
│                                                        │
└───────────────────────────────────────────────────────┘
```

And the volume sharing:

```
┌───────────────────────────────────────────────────────┐
│                                                        │
│   asset-builder ──writes──> static-assets <──reads── web
│                                                        │
│   api ──writes/reads──> uploads                       │
│                                                        │
│   database ──writes/reads──> db-data                  │
│                                                        │
│   cache ──writes/reads──> redis-data                  │
│                                                        │
└───────────────────────────────────────────────────────┘
```

---

## Common Mistakes

### Mistake 1: Not Declaring Volumes at the Top Level

```yaml
# Wrong: volume is used but not declared
services:
  database:
    volumes:
      - my-data:/var/lib/postgresql/data
# Error: volume "my-data" is not declared

# Right: declare it
services:
  database:
    volumes:
      - my-data:/var/lib/postgresql/data

volumes:
  my-data:
```

### Mistake 2: Using Mapped Ports for Inter-Service Communication

```yaml
services:
  api:
    ports:
      - "8080:3000"
    environment:
      # Wrong: using the mapped host port
      DATABASE_URL: postgres://user:pass@database:5433/mydb

  database:
    image: postgres:16
    ports:
      - "5433:5432"
    # Right: use the container port (5432), not the host port (5433)
```

Other services should always use the container's internal port. The mapped port is only for access from your host machine.

### Mistake 3: Expecting External Volumes to Be Auto-Created

```yaml
volumes:
  my-volume:
    external: true
# If "my-volume" does not exist, docker compose up will fail!
```

Create the volume first:

```bash
docker volume create my-volume
```

### Mistake 4: Forgetting Network Assignment

```yaml
# Wrong: web is on frontend but api is not — they cannot communicate
services:
  web:
    image: nginx
    networks:
      - frontend
  api:
    image: my-api
    networks:
      - backend     # Missing "frontend"! web cannot reach api.
```

If a service needs to communicate with services on multiple networks, it must be on all of those networks.

### Mistake 5: Assuming Compose Projects Can See Each Other

Services in different Compose projects are on different networks by default. They cannot communicate unless you use an external network.

---

## Best Practices

1. **Use custom networks for security**. Separate your frontend and backend tiers. Only the API should have access to the database.

2. **Always declare named volumes**. Named volumes persist data and have clear names. Avoid anonymous volumes.

3. **Use `:ro` (read-only) mounts** when a service only needs to read data. This prevents accidental modifications.

4. **Use `external: true` for critical data**. This prevents accidental deletion with `docker compose down -v`.

5. **Use service names as hostnames**. Never hardcode IP addresses. Service names are stable and handled by Docker DNS.

6. **Use internal ports for service-to-service communication**. Only map ports to the host when you need external access.

7. **Document your network topology**. Add comments in your `docker-compose.yml` explaining which networks serve which purpose.

8. **Regularly clean up unused volumes** with `docker volume prune`. Old volumes can consume significant disk space.

---

## Quick Summary

Docker Compose automatically creates a default network where all services can reach each other by name. For more control, you can define custom networks to isolate services — for example, keeping the database on a backend network that the web server cannot reach. Named volumes persist data across container restarts and must be declared in both the service definition and the top-level `volumes` section. Volumes can be shared between services for scenarios like file uploads or shared configuration. External volumes and networks allow sharing resources between different Compose projects while protecting critical data from accidental deletion.

---

## Key Points

- Compose automatically creates a default network named `<project>_default`.
- Service names are automatically registered as DNS hostnames on the Compose network.
- Services communicate using container ports (internal), not mapped host ports.
- Custom networks in Compose provide isolation between service groups.
- A service can belong to multiple networks to bridge between them.
- Named volumes must be declared in the top-level `volumes:` section.
- Volumes can be shared between services by mounting the same volume in multiple services.
- Use `:ro` to mount volumes as read-only when a service only needs to read data.
- `external: true` means the volume or network must already exist and will not be managed by Compose.
- Different Compose projects are network-isolated by default; use external networks to connect them.

---

## Practice Questions

1. You have a Compose file with services `web`, `api`, and `database`. Without defining any custom networks, can `web` communicate with `database`? Why or why not?

2. What is the difference between a named volume and an external volume? When would you use each?

3. Your `api` service needs to connect to PostgreSQL on port 5432. In the Compose file, the `database` service maps port `5433:5432`. What host and port should the `api` service use to connect? Why?

4. Explain how you would prevent a `frontend` service from directly accessing a `database` service while still allowing an `api` service to access both.

5. Two Compose projects need to share a PostgreSQL database. How would you set this up?

---

## Exercises

### Exercise 1: Network Isolation

1. Create a `docker-compose.yml` with three services: `web` (nginx), `api` (nginx), and `db` (nginx).
2. Create two networks: `public` and `private`.
3. Put `web` on `public`, `db` on `private`, and `api` on both.
4. Start the stack and verify:
   - `web` can ping `api`
   - `api` can ping `db`
   - `web` cannot ping `db`

### Exercise 2: Shared Volumes

1. Create a Compose file with two services.
2. Service `writer` runs `busybox` and writes a file to a shared volume every 5 seconds.
3. Service `reader` runs `busybox` and reads the file from the shared volume.
4. Verify that `reader` can see the files written by `writer`.

### Exercise 3: External Resources

1. Create a Docker network manually: `docker network create my-external-net`.
2. Create a Docker volume manually: `docker volume create my-external-data`.
3. Write a `docker-compose.yml` that uses both of these external resources.
4. Start the stack and verify everything works.
5. Run `docker compose down -v` and verify the external volume was NOT deleted.

---

## What Is Next?

You now understand how Compose manages networks and volumes. In the next chapter, you will learn how to use Docker Compose for development workflows — bind mounts for live code reloading, watch mode, development vs. production configurations, and debugging inside containers. These techniques will make your daily development workflow much more efficient.
