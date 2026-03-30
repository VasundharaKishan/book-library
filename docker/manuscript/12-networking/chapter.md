# Chapter 12: Docker Networking

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Explain how Docker containers communicate with each other
- Understand the default bridge network and its limitations
- Map container ports to your host machine using `-p`
- Create custom bridge networks for better container communication
- Use container names as hostnames (DNS resolution)
- Connect an application container to a database container
- List, inspect, connect, and disconnect networks
- Choose the right network driver for your use case

---

## Why This Chapter Matters

Imagine you are building a web application. You have a web server running in one container and a database running in another container. How do they talk to each other? Can the web server find the database? Can the outside world reach your web server?

These are networking questions, and understanding Docker networking is essential for building real applications. Without networking knowledge, your containers are like isolated rooms with no doors or windows. This chapter gives you the keys to connect them.

Think of it this way. In the real world, a restaurant has a kitchen (the database) and a dining room (the web server). Customers (the outside world) enter through the front door (port mapping), and the waiters carry food between the kitchen and dining room through an internal hallway (the Docker network). This chapter teaches you how to build those hallways and doors.

---

## How Docker Networking Works

When you install Docker, it automatically creates a networking system that allows containers to communicate. Let us start by understanding the big picture.

```
┌─────────────────────────────────────────────────────┐
│                   Your Computer (Host)               │
│                                                      │
│   ┌──────────────┐        ┌──────────────┐          │
│   │  Container A  │        │  Container B  │          │
│   │  (Web App)    │        │  (Database)   │          │
│   │  Port 3000    │        │  Port 5432    │          │
│   └──────┬───────┘        └──────┬───────┘          │
│          │                        │                   │
│   ┌──────┴────────────────────────┴───────┐          │
│   │          Docker Network               │          │
│   │     (Internal communication)          │          │
│   └───────────────────┬───────────────────┘          │
│                       │                               │
│            ┌──────────┴──────────┐                    │
│            │   Port Mapping      │                    │
│            │  Host:Container     │                    │
│            └──────────┬──────────┘                    │
│                       │                               │
└───────────────────────┼───────────────────────────────┘
                        │
                   Outside World
                  (Your Browser)
```

Docker networking has three main concepts:

1. **Container-to-container communication**: Containers on the same network can talk to each other.
2. **Port mapping**: You expose container ports to your host machine so the outside world can reach them.
3. **Network isolation**: Containers on different networks cannot communicate unless you explicitly connect them.

---

## The Default Bridge Network

When you install Docker, it creates a network called `bridge`. This is the **default bridge network**. Every container you start without specifying a network gets connected to this default bridge network automatically.

Let us see it in action.

### Listing Docker Networks

Run this command to see all networks on your system:

```bash
docker network ls
```

**Output:**

```
NETWORK ID     NAME      DRIVER    SCOPE
a1b2c3d4e5f6   bridge    bridge    local
f6e5d4c3b2a1   host      host      local
1a2b3c4d5e6f   none      null      local
```

Let us break down each column:

- **NETWORK ID**: A unique identifier for the network. Docker generates this automatically.
- **NAME**: The human-readable name of the network.
- **DRIVER**: The type of network. We will explain drivers later in this chapter.
- **SCOPE**: Where the network is available. `local` means it exists only on this machine.

You see three networks that Docker created automatically:

1. **bridge**: The default network for containers. Think of it as a shared hallway.
2. **host**: Removes network isolation between the container and the host. The container uses the host's network directly.
3. **none**: No networking at all. The container is completely isolated.

### Running Containers on the Default Bridge

Let us start two containers and see how they communicate.

```bash
docker run -d --name web nginx
```

**Output:**

```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

```bash
docker run -d --name api nginx
```

**Output:**

```
b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1
```

Both containers are now running on the default bridge network. Let us verify:

```bash
docker network inspect bridge
```

**Output (simplified):**

```json
[
    {
        "Name": "bridge",
        "Driver": "bridge",
        "Containers": {
            "a1b2c3...": {
                "Name": "web",
                "IPv4Address": "172.17.0.2/16"
            },
            "b2c3d4...": {
                "Name": "api",
                "IPv4Address": "172.17.0.3/16"
            }
        }
    }
]
```

Both containers have IP addresses on the same network (172.17.0.x). They can communicate using these IP addresses.

### Testing Communication on the Default Bridge

Let us go inside the `web` container and try to reach the `api` container:

```bash
docker exec -it web bash
```

Now inside the container, install `ping` (it is not included by default in the nginx image):

```bash
apt-get update && apt-get install -y iputils-ping
```

Try pinging the `api` container by its IP address:

```bash
ping -c 3 172.17.0.3
```

**Output:**

```
PING 172.17.0.3 (172.17.0.3) 56(84) bytes of data.
64 bytes from 172.17.0.3: icmp_seq=1 ttl=64 time=0.089 ms
64 bytes from 172.17.0.3: icmp_seq=2 ttl=64 time=0.065 ms
64 bytes from 172.17.0.3: icmp_seq=3 ttl=64 time=0.071 ms

--- 172.17.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
```

It works. The containers can communicate by IP address.

Now try pinging by container name:

```bash
ping -c 3 api
```

**Output:**

```
ping: api: Name or service not known
```

This fails. The default bridge network does **not** provide DNS resolution (the ability to use container names as addresses). You can only use IP addresses.

Type `exit` to leave the container:

```bash
exit
```

### The Problem with the Default Bridge Network

The default bridge network has two significant limitations:

1. **No DNS resolution**: You cannot use container names to communicate. You must use IP addresses.
2. **IP addresses change**: Every time you restart a container, Docker might assign it a different IP address. This means your application would break because it is trying to connect to the old address.

Think of it like this. The default bridge network is like a building where apartments have numbers, but there is no directory listing who lives where. If your friend moves to a different apartment, you have no way to find them unless they tell you their new number.

```
┌─────────────────────────────────────────────┐
│        Default Bridge Network               │
│                                              │
│   Container "web"    Container "api"         │
│   IP: 172.17.0.2     IP: 172.17.0.3         │
│                                              │
│   web -> api:  Must use 172.17.0.3           │
│   web -> api:  Cannot use name "api"         │
│                                              │
│   After restart:                             │
│   IP: 172.17.0.4     IP: 172.17.0.2         │
│   (IPs may change!)                          │
└─────────────────────────────────────────────┘
```

This is why Docker recommends using **user-defined bridge networks** instead. Let us learn about those next.

Clean up:

```bash
docker rm -f web api
```

**Output:**

```
web
api
```

---

## Port Mapping: Letting the Outside World In

Before we move to custom networks, let us understand port mapping. By default, containers are isolated from the outside world. If you run a web server inside a container, you cannot access it from your browser. Port mapping creates a tunnel from your host machine into the container.

### What Is a Port?

A **port** is a numbered doorway on a computer where network traffic enters or exits. Think of your computer as an apartment building. Each apartment has a door number. Port 80 is the door for web traffic (HTTP). Port 443 is the door for secure web traffic (HTTPS). Port 5432 is the door for PostgreSQL databases.

When a container runs a web server on port 80 inside the container, that port 80 only exists inside the container. Your browser on the host machine cannot reach it. Port mapping connects a port on your host to a port in the container.

### Using the -p Flag

The `-p` flag (short for `--publish`) maps a host port to a container port.

```bash
docker run -d --name my-web -p 8080:80 nginx
```

Let us break down `-p 8080:80`:

- **8080**: The port on your host machine (your computer).
- **80**: The port inside the container where nginx is listening.
- **The colon** separates host from container: `host:container`.

```
┌────────────────────────────────────────────────┐
│              Your Computer (Host)               │
│                                                 │
│   Browser ──> localhost:8080                    │
│                    │                             │
│                    │  (port mapping)             │
│                    ▼                             │
│   ┌────────────────────────────┐                │
│   │      Container "my-web"    │                │
│   │      nginx on port 80      │                │
│   └────────────────────────────┘                │
└────────────────────────────────────────────────┘
```

Now open your browser and go to `http://localhost:8080`. You will see the nginx welcome page.

### Common Port Mapping Patterns

Here are some common port mapping examples:

```bash
# Map host port 3000 to container port 3000 (same port)
docker run -d -p 3000:3000 my-node-app

# Map host port 5433 to container port 5432 (different ports)
docker run -d -p 5433:5432 postgres

# Map multiple ports
docker run -d -p 8080:80 -p 8443:443 nginx

# Map to a specific host IP address
docker run -d -p 127.0.0.1:8080:80 nginx

# Let Docker choose a random host port
docker run -d -p 80 nginx
```

Let us explain each:

- **Same port** (`3000:3000`): The simplest case. Host and container use the same port number.
- **Different ports** (`5433:5432`): Useful when the default port is already in use on your host. Here, PostgreSQL listens on 5432 inside the container, but you access it via 5433 on your host.
- **Multiple ports** (`-p 8080:80 -p 8443:443`): Maps more than one port. Useful for servers that use both HTTP and HTTPS.
- **Specific IP** (`127.0.0.1:8080:80`): Only allows connections from your own machine, not from other computers on your network.
- **Random port** (`-p 80`): Docker picks an available host port automatically. Use `docker port` to see which port was assigned.

### Checking Port Mappings

To see which ports are mapped for a running container:

```bash
docker port my-web
```

**Output:**

```
80/tcp -> 0.0.0.0:8080
```

This tells you that port 80 in the container is mapped to port 8080 on all host interfaces (`0.0.0.0` means all interfaces).

Clean up:

```bash
docker rm -f my-web
```

---

## User-Defined Bridge Networks

User-defined bridge networks solve the problems of the default bridge network. They provide:

1. **Automatic DNS resolution**: Containers can find each other by name.
2. **Better isolation**: Only containers you explicitly add can communicate.
3. **Live connection management**: You can connect and disconnect containers from networks without restarting them.

### Creating a Custom Network

Use `docker network create` to make a new network:

```bash
docker network create my-app-network
```

**Output:**

```
c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9
```

Docker returns the network ID. Now verify it exists:

```bash
docker network ls
```

**Output:**

```
NETWORK ID     NAME             DRIVER    SCOPE
a1b2c3d4e5f6   bridge           bridge    local
f6e5d4c3b2a1   host             host      local
c4d5e6f7g8h9   my-app-network   bridge    local
1a2b3c4d5e6f   none             null      local
```

Your new network `my-app-network` appears in the list. It uses the `bridge` driver by default.

### Running Containers on a Custom Network

Use the `--network` flag to start a container on your custom network:

```bash
docker run -d --name web --network my-app-network nginx
```

```bash
docker run -d --name api --network my-app-network nginx
```

Now let us test DNS resolution. Go inside the `web` container:

```bash
docker exec -it web bash
apt-get update && apt-get install -y iputils-ping
```

Try pinging the `api` container by name:

```bash
ping -c 3 api
```

**Output:**

```
PING api (172.18.0.3) 56(84) bytes of data.
64 bytes from api.my-app-network (172.18.0.3): icmp_seq=1 ttl=64 time=0.065 ms
64 bytes from api.my-app-network (172.18.0.3): icmp_seq=2 ttl=64 time=0.058 ms
64 bytes from api.my-app-network (172.18.0.3): icmp_seq=3 ttl=64 time=0.061 ms

--- api ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
```

It works. The container name `api` is automatically resolved to its IP address. This is the key advantage of user-defined bridge networks.

```
┌─────────────────────────────────────────────────┐
│        User-Defined Bridge Network              │
│        "my-app-network"                         │
│                                                  │
│   Container "web"      Container "api"           │
│   IP: 172.18.0.2       IP: 172.18.0.3           │
│                                                  │
│   web -> api:  Can use name "api"     ✓          │
│   web -> api:  Can use IP 172.18.0.3  ✓          │
│                                                  │
│   Docker DNS resolves "api" -> 172.18.0.3        │
│   Even after restart, name stays the same!       │
└─────────────────────────────────────────────────┘
```

Exit the container:

```bash
exit
```

Clean up:

```bash
docker rm -f web api
```

### Default Bridge vs. User-Defined Bridge

Here is a comparison to make the differences clear:

```
┌─────────────────────────┬──────────────────────────────┐
│   Default Bridge        │   User-Defined Bridge        │
├─────────────────────────┼──────────────────────────────┤
│ Created automatically   │ You create it manually       │
│ No DNS resolution       │ Automatic DNS resolution     │
│ All containers join     │ Only specified containers     │
│   by default            │   join                        │
│ Less secure (shared     │ More secure (isolated         │
│   by all containers)    │   to your app)                │
│ Cannot connect/          │ Can connect/disconnect       │
│   disconnect live        │   containers at any time     │
│ Use IP addresses only   │ Use container names           │
└─────────────────────────┴──────────────────────────────┘
```

**Bottom line**: Always use user-defined bridge networks for your applications. The default bridge network should only be used for quick, throwaway experiments.

---

## Connecting an Application to a Database

Let us put everything together with a real-world example. We will run a PostgreSQL database and connect a simple application to it.

### Step 1: Create the Network

```bash
docker network create app-network
```

### Step 2: Start the Database

```bash
docker run -d \
  --name my-postgres \
  --network app-network \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=myapp \
  postgres:16
```

Let us break down this command:

- `-d`: Run in the background (detached mode).
- `--name my-postgres`: Give the container the name "my-postgres". Other containers will use this name to connect.
- `--network app-network`: Attach the container to our custom network.
- `-e POSTGRES_USER=myuser`: Set the database username.
- `-e POSTGRES_PASSWORD=mypassword`: Set the database password.
- `-e POSTGRES_DB=myapp`: Create a database called "myapp".
- `postgres:16`: Use the official PostgreSQL 16 image.

### Step 3: Start an Application Container

Let us start a simple container and connect to the database from it:

```bash
docker run -it --rm \
  --name my-app \
  --network app-network \
  postgres:16 \
  psql -h my-postgres -U myuser -d myapp
```

Let us break this down:

- `-it`: Interactive mode with a terminal (so we can type commands).
- `--rm`: Remove the container when we exit.
- `--network app-network`: Connect to the same network as the database.
- `postgres:16`: We use the postgres image because it includes the `psql` client.
- `psql -h my-postgres -U myuser -d myapp`: Connect to the host `my-postgres` (the container name), as user `myuser`, to the database `myapp`.

**Output:**

```
Password for user myuser:
```

Type `mypassword` and press Enter:

```
psql (16.1)
Type "help" for help.

myapp=>
```

You are now connected to the PostgreSQL database running in another container. The key thing to notice is that we used `my-postgres` as the hostname. Docker's DNS resolved that name to the database container's IP address automatically.

Let us run a quick SQL command to verify:

```sql
SELECT version();
```

**Output:**

```
                          version
------------------------------------------------------------
 PostgreSQL 16.1 on x86_64-pc-linux-gnu, compiled by ...
(1 row)
```

Type `\q` to exit psql, or press Ctrl+D.

```
┌─────────────────────────────────────────────────────┐
│              app-network                             │
│                                                      │
│   ┌──────────────────┐    ┌──────────────────┐      │
│   │    my-app         │    │   my-postgres     │      │
│   │                   │    │                   │      │
│   │  psql connects    │───>│  PostgreSQL       │      │
│   │  to "my-postgres" │    │  Port 5432        │      │
│   │                   │    │                   │      │
│   └──────────────────┘    └──────────────────┘      │
│                                                      │
│   DNS: "my-postgres" resolves to 172.18.0.2          │
└─────────────────────────────────────────────────────┘
```

### Step 4: Expose the Database (Optional)

If you also want to connect to the database from your host machine (for example, using a database GUI tool), add port mapping:

```bash
docker rm -f my-postgres

docker run -d \
  --name my-postgres \
  --network app-network \
  -p 5432:5432 \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=myapp \
  postgres:16
```

Now you can connect from your host at `localhost:5432` AND other containers can still connect using the name `my-postgres`.

Clean up:

```bash
docker rm -f my-postgres
docker network rm app-network
```

---

## Network Management Commands

Here is a complete reference for managing Docker networks.

### docker network ls — List All Networks

```bash
docker network ls
```

**Output:**

```
NETWORK ID     NAME      DRIVER    SCOPE
a1b2c3d4e5f6   bridge    bridge    local
f6e5d4c3b2a1   host      host      local
1a2b3c4d5e6f   none      null      local
```

### docker network inspect — View Network Details

```bash
docker network inspect bridge
```

This shows detailed information about a network, including which containers are connected, the subnet, the gateway, and more.

### docker network create — Create a Network

```bash
# Basic creation
docker network create my-network

# With a specific subnet
docker network create --subnet 192.168.1.0/24 my-network

# With a specific driver
docker network create --driver bridge my-network
```

### docker network connect — Add a Container to a Network

You can add a running container to a network without restarting it:

```bash
docker network connect my-network my-container
```

This is useful when you need a container to communicate with containers on multiple networks.

### docker network disconnect — Remove a Container from a Network

```bash
docker network disconnect my-network my-container
```

The container keeps running but can no longer communicate with other containers on that network.

### docker network rm — Delete a Network

```bash
docker network rm my-network
```

You cannot delete a network that has containers connected to it. You must disconnect or remove all containers first.

### docker network prune — Remove Unused Networks

```bash
docker network prune
```

**Output:**

```
WARNING! This will remove all custom networks not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Networks:
my-old-network
test-network
```

This removes all custom networks that have no containers connected to them. The default bridge, host, and none networks are never removed.

---

## Connecting a Container to Multiple Networks

A container can belong to more than one network. This is useful when you want a container to communicate with different groups of containers.

```bash
# Create two networks
docker network create frontend-network
docker network create backend-network

# Start containers
docker run -d --name web --network frontend-network nginx
docker run -d --name api --network backend-network nginx
docker run -d --name database --network backend-network postgres:16

# Connect the API to the frontend network too
docker network connect frontend-network api
```

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│   frontend-network          backend-network          │
│   ┌──────────────┐         ┌──────────────┐         │
│   │              │         │              │         │
│   │  web ◄──────►│ api ◄──►│  database    │         │
│   │              │         │              │         │
│   └──────────────┘         └──────────────┘         │
│                                                      │
│   web can reach api:     Yes (frontend-network)      │
│   api can reach database: Yes (backend-network)      │
│   web can reach database: No  (different networks)   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

In this setup:
- The `web` container can reach `api` because they share `frontend-network`.
- The `api` container can reach `database` because they share `backend-network`.
- The `web` container **cannot** reach `database` because they are on different networks.

This is a common pattern for security. The database is only accessible from the API layer, never directly from the web layer.

Clean up:

```bash
docker rm -f web api database
docker network rm frontend-network backend-network
```

---

## Network Driver Types

Docker supports different network drivers, each designed for a specific use case. Think of network drivers like different types of roads — a highway, a private road, and no road at all.

### Bridge Driver (Default)

The **bridge** driver creates an isolated network on your host machine. Containers on the same bridge network can communicate. This is the most common driver and the one you will use for most applications.

```bash
# Bridge is the default driver
docker network create my-bridge-network

# Explicit driver specification (same result)
docker network create --driver bridge my-bridge-network
```

**When to use**: For most single-host applications. This is the right choice 99% of the time during development.

### Host Driver

The **host** driver removes the network isolation between the container and the host. The container shares the host's network directly. This means the container does not get its own IP address — it uses the host's IP address.

```bash
docker run -d --network host nginx
```

With the host network, there is no port mapping needed. If nginx listens on port 80 inside the container, it is available at port 80 on your host directly.

```
┌─────────────────────────────────────┐
│   Bridge Driver                      │
│                                      │
│   Host (port 8080) ──> Container     │
│   (port mapping required)            │
│                                      │
│   Container has own IP: 172.17.0.2   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   Host Driver                        │
│                                      │
│   Host = Container                   │
│   (no port mapping needed)           │
│                                      │
│   Container uses host IP directly    │
└─────────────────────────────────────┘
```

**When to use**: When you need maximum network performance and do not need network isolation. Common in performance-critical applications. Note that the host network driver only works on Linux, not on Docker Desktop for Mac or Windows.

### None Driver

The **none** driver gives the container no network access at all. The container is completely isolated.

```bash
docker run -d --network none nginx
```

The container cannot communicate with other containers, the host, or the internet.

**When to use**: For security-sensitive containers that should not have any network access, such as a container that only processes local files.

### Summary of Network Drivers

```
┌───────────┬────────────────────────────┬──────────────────────┐
│  Driver   │  Description               │  Use Case            │
├───────────┼────────────────────────────┼──────────────────────┤
│  bridge   │  Isolated network on the   │  Most applications   │
│           │  host. Containers get own  │  (default choice)    │
│           │  IP addresses.             │                      │
├───────────┼────────────────────────────┼──────────────────────┤
│  host     │  Container uses the host   │  Performance-        │
│           │  network directly. No      │  critical apps.      │
│           │  isolation.                │  Linux only.         │
├───────────┼────────────────────────────┼──────────────────────┤
│  none     │  No networking at all.     │  Security-sensitive  │
│           │  Complete isolation.       │  workloads.          │
└───────────┴────────────────────────────┴──────────────────────┘
```

---

## Common Mistakes

### Mistake 1: Using the Default Bridge Network for Applications

```bash
# Wrong: relies on IP addresses that can change
docker run -d --name db postgres:16
docker run -d --name app my-app
# Inside app, connecting to db by IP 172.17.0.2 — fragile!

# Right: use a custom network with DNS
docker network create app-net
docker run -d --name db --network app-net postgres:16
docker run -d --name app --network app-net my-app
# Inside app, connecting to "db" by name — reliable!
```

### Mistake 2: Forgetting Port Mapping

```bash
# Wrong: no port mapping, cannot access from browser
docker run -d nginx

# Right: map a host port
docker run -d -p 8080:80 nginx
```

### Mistake 3: Port Already in Use

```bash
# This will fail if port 8080 is already in use
docker run -d -p 8080:80 nginx
```

**Error:**

```
Error response from daemon: driver failed programming external connectivity:
Bind for 0.0.0.0:8080 failed: port is already allocated
```

**Solution**: Use a different host port:

```bash
docker run -d -p 8081:80 nginx
```

### Mistake 4: Containers on Different Networks

```bash
# These containers cannot communicate!
docker network create network-a
docker network create network-b
docker run -d --name web --network network-a nginx
docker run -d --name api --network network-b nginx
# web cannot reach api — they are on different networks
```

**Solution**: Put them on the same network, or use `docker network connect` to add the container to an additional network.

### Mistake 5: Confusing Host Port and Container Port Order

```bash
# Wrong order thinking: this maps host 80 to container 3000
# Actual: this maps host 3000 to container 80
docker run -d -p 3000:80 nginx
```

Remember: it is always `host:container`. Think of it as `outside:inside`.

---

## Best Practices

1. **Always use user-defined bridge networks** for multi-container applications. Never rely on the default bridge network.

2. **Use meaningful network names** that describe their purpose: `frontend-net`, `backend-net`, `app-network`.

3. **Separate concerns with multiple networks**. Put your web tier and database tier on different networks. Connect the API to both.

4. **Use container names as hostnames** in your application configuration. For example, set your database host to `my-postgres` instead of an IP address.

5. **Only expose ports you need**. Do not map ports unless you need to access the container from outside Docker.

6. **Use specific host IPs for security**. Instead of `-p 8080:80` (accessible from anywhere), use `-p 127.0.0.1:8080:80` (accessible only from your machine).

7. **Clean up unused networks** regularly with `docker network prune`.

---

## Quick Summary

Docker networking allows containers to communicate with each other and with the outside world. The default bridge network connects all containers but does not support DNS resolution. User-defined bridge networks solve this by letting containers find each other by name. Port mapping with `-p host:container` lets traffic from the outside world reach containers. Network drivers (bridge, host, none) provide different levels of isolation. For real applications, always create custom networks and use container names as hostnames.

---

## Key Points

- Docker creates three default networks: bridge, host, and none.
- The default bridge network does not support DNS resolution (you cannot use container names).
- User-defined bridge networks provide automatic DNS resolution and better isolation.
- Port mapping (`-p host:container`) lets the outside world reach containers.
- The format is always `host_port:container_port` — think "outside:inside."
- Use `docker network create` to make a custom network.
- Use `docker network connect` and `docker network disconnect` to manage containers at runtime.
- The bridge driver is the right choice for most applications.
- Containers on different networks cannot communicate unless explicitly connected.
- Always use container names (not IP addresses) for inter-container communication.

---

## Practice Questions

1. What is the difference between the default bridge network and a user-defined bridge network? Why does Docker recommend user-defined networks?

2. You run `docker run -d -p 5000:3000 my-app`. What does this command do? Which port do you use in your browser to access the app?

3. You have three containers: `frontend`, `api`, and `database`. You want the frontend to communicate with the api, and the api to communicate with the database, but the frontend should NOT be able to reach the database directly. How would you set up the networks?

4. What happens if you try to delete a network that still has containers connected to it?

5. Explain the difference between the bridge, host, and none network drivers. When would you use each one?

---

## Exercises

### Exercise 1: Build a Two-Container Network

1. Create a custom network called `exercise-net`.
2. Start an nginx container named `webserver` on `exercise-net` with port 8080 mapped to port 80.
3. Start another nginx container named `backend` on `exercise-net`.
4. Go inside `webserver` and verify you can ping `backend` by name.
5. Access the webserver from your browser at `http://localhost:8080`.
6. Clean up all containers and the network.

### Exercise 2: Multi-Network Isolation

1. Create two networks: `public-net` and `private-net`.
2. Start a container named `web` on `public-net`.
3. Start a container named `api` on both `public-net` and `private-net`.
4. Start a container named `db` on `private-net`.
5. Verify that `web` can reach `api` but cannot reach `db`.
6. Verify that `api` can reach both `web` and `db`.
7. Clean up everything.

### Exercise 3: Connect an App to a Database

1. Create a network called `db-net`.
2. Start a PostgreSQL container named `mydb` on `db-net` with username `admin`, password `secret123`, and database `testdb`.
3. Start another container on the same network and use `psql` to connect to `mydb` by name.
4. Create a table and insert some data to verify the connection works.
5. Clean up everything.

---

## What Is Next?

You now know how to connect containers and let them communicate. But when something goes wrong, how do you figure out what happened? In the next chapter, you will learn how to read container logs, debug issues, inspect container internals, and systematically solve common problems. These debugging skills will save you hours of frustration as you build more complex applications.
