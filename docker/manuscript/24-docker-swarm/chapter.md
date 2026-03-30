# Chapter 24: Docker Swarm

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand what container orchestration is and why it is needed
- Initialize a Docker Swarm cluster with `docker swarm init`
- Explain the roles of manager and worker nodes
- Understand the difference between services and containers
- Create and manage services with `docker service create`
- Scale services up and down with `--replicas`
- Perform rolling updates with zero downtime
- Deploy multi-service applications with `docker stack deploy`
- Use the Swarm visualizer to see your cluster
- Drain nodes for maintenance
- Compare Docker Swarm with Kubernetes

---

## Why This Chapter Matters

So far, you have run containers on a single machine. This works for development and small applications, but it breaks down when:

- **Your application gets more traffic than one server can handle** — You need to run copies on multiple machines
- **A server crashes** — Your application goes down and nobody restarts it
- **You need to update** — Stopping the old version and starting the new one causes downtime
- **You need load balancing** — Distributing traffic across multiple copies of your application

These are the problems that **container orchestration** solves. Think of orchestration like conducting an orchestra:

```
+-----------------------------------------------------------+
|              The Orchestra Analogy                         |
|                                                            |
|   Without a conductor (no orchestration):                  |
|   - Each musician plays at their own tempo                 |
|   - Nobody knows when to start or stop                    |
|   - If a musician gets sick, their part is silent          |
|   - Nobody coordinates the performance                     |
|                                                            |
|   With a conductor (orchestration):                        |
|   - Everyone plays in sync                                 |
|   - The conductor decides when each section plays          |
|   - If a musician is absent, another fills in              |
|   - The overall performance is coordinated                  |
+-----------------------------------------------------------+
```

Docker Swarm is Docker's built-in orchestration tool. It turns a group of Docker hosts into a single, coordinated cluster.

---

## What Is Docker Swarm?

**Docker Swarm** (or "Swarm mode") is a clustering and orchestration feature built into Docker. When you enable Swarm mode, your Docker host becomes part of a **swarm** — a group of machines that work together to run your containers.

```
+-----------------------------------------------------------+
|              Single Host vs Swarm                          |
|                                                            |
|   Single Host:                                             |
|   +------------------+                                     |
|   | Docker Host      |                                     |
|   | +----+ +----+    |                                     |
|   | | C1 | | C2 |    |  Only one machine.                  |
|   | +----+ +----+    |  If it dies, everything dies.       |
|   +------------------+                                     |
|                                                            |
|   Swarm (3 hosts):                                         |
|   +----------+ +----------+ +----------+                   |
|   | Manager  | | Worker 1 | | Worker 2 |                   |
|   | +----+   | | +----+   | | +----+   |                   |
|   | | C1 |   | | | C2 |   | | | C3 |   |                   |
|   | +----+   | | +----+   | | +----+   |                   |
|   +----------+ +----------+ +----------+                   |
|                                                            |
|   Three machines. If one dies, the others take over.       |
+-----------------------------------------------------------+
```

### Key Features

- **Built into Docker** — No extra software to install
- **Declarative service model** — You declare what you want ("run 5 copies"), Swarm makes it happen
- **Scaling** — Add or remove copies with one command
- **Rolling updates** — Update containers one at a time with zero downtime
- **Self-healing** — If a container crashes, Swarm starts a replacement
- **Load balancing** — Incoming traffic is distributed across all copies
- **Secure by default** — All communication between nodes is encrypted

---

## Initializing a Swarm

### docker swarm init

Turn your Docker host into a Swarm manager with one command:

```bash
docker swarm init
```

**Output:**

```
Swarm initialized: current node (abc123def456) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-abc123...xyz789 192.168.1.100:2377

To add a manager to this swarm, run 'docker swarm join-token manager'
and follow the instructions.
```

**What just happened:**

- Your Docker host became a **Swarm manager** node
- A **join token** was generated for adding other machines to the swarm
- The Swarm API is now listening on port 2377
- An overlay network called `ingress` was created for load balancing

### Verify the Swarm

```bash
docker node ls
```

**Output:**

```
ID                           HOSTNAME     STATUS    AVAILABILITY   MANAGER STATUS
abc123def456 *               my-server    Ready     Active         Leader
```

You have a one-node swarm. The `*` indicates this is the current node, and `Leader` means it is the primary manager.

---

## Nodes: Managers and Workers

A Swarm cluster consists of two types of nodes:

### Manager Nodes

**Manager nodes** make decisions for the cluster:

- Schedule which containers run on which nodes
- Maintain the cluster state
- Handle service creation, updates, and scaling
- Respond to API requests

```
+-----------------------------------------------------------+
|              Manager Node Responsibilities                 |
|                                                            |
|   +---------------------------------------------------+   |
|   | Manager Node                                      |   |
|   |                                                   |   |
|   | - Accepts commands (docker service create)         |   |
|   | - Decides where to place containers               |   |
|   | - Monitors container health                        |   |
|   | - Replaces failed containers                       |   |
|   | - Stores cluster configuration                     |   |
|   | - Can also run containers (optional)               |   |
|   +---------------------------------------------------+   |
+-----------------------------------------------------------+
```

### Worker Nodes

**Worker nodes** execute the work:

- Run containers assigned by the manager
- Report container status back to the manager
- Cannot make scheduling decisions

### Adding Worker Nodes

On the manager, get the join token:

```bash
docker swarm join-token worker
```

**Output:**

```
To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-abc123...xyz789 192.168.1.100:2377
```

On each worker machine, run that command:

```bash
docker swarm join --token SWMTKN-1-abc123...xyz789 192.168.1.100:2377
```

**Output:**

```
This node joined a swarm as a worker.
```

### Verify the Cluster

Back on the manager:

```bash
docker node ls
```

**Output:**

```
ID                           HOSTNAME       STATUS    AVAILABILITY   MANAGER STATUS
abc123def456 *               manager-1      Ready     Active         Leader
ghi789jkl012                 worker-1       Ready     Active
mno345pqr678                 worker-2       Ready     Active
```

You now have a three-node cluster: one manager and two workers.

### How Many Managers?

For production, use an **odd number** of managers for fault tolerance:

| Managers | Can Tolerate Failures | Recommended For       |
|----------|----------------------|-----------------------|
| 1        | 0                    | Development, testing   |
| 3        | 1                    | Small production       |
| 5        | 2                    | Large production       |
| 7        | 3                    | Very large production  |

The formula is: with N managers, the swarm tolerates (N-1)/2 failures. Three managers can lose one. Five managers can lose two.

---

## Services vs Containers

In Swarm mode, you do not run containers directly. Instead, you create **services**. A service is a definition of what you want to run. Swarm creates the actual containers (called **tasks**) based on that definition.

```
+-----------------------------------------------------------+
|              Service vs Container                          |
|                                                            |
|   docker run:                                              |
|     "Run ONE container on THIS machine"                    |
|     You manage it. You restart it. You scale it.           |
|                                                            |
|   docker service create:                                   |
|     "I want 3 copies of this app running SOMEWHERE"        |
|     Swarm manages them. Swarm restarts them.               |
|     Swarm decides which machines run them.                 |
|                                                            |
|   +---------------------------------------------------+   |
|   | Service: webapp (replicas: 3)                     |   |
|   |                                                   |   |
|   |   Task 1 (container) --> Worker 1                 |   |
|   |   Task 2 (container) --> Worker 2                 |   |
|   |   Task 3 (container) --> Manager 1                |   |
|   +---------------------------------------------------+   |
+-----------------------------------------------------------+
```

Think of a service as a **job posting** and tasks as the **employees hired**. The job posting says "I need 3 web developers." The employees are the actual people doing the work. If one quits, the job posting is still active — HR (Swarm) hires a replacement.

---

## Creating Services

### docker service create

```bash
docker service create \
  --name webapp \
  --replicas 3 \
  --publish 8080:80 \
  nginx:1.25
```

**Line-by-line explanation:**

- `docker service create` — Create a new service (instead of `docker run`)
- `--name webapp` — Give the service a name
- `--replicas 3` — Run 3 copies of this container
- `--publish 8080:80` — Map port 8080 on ALL nodes to port 80 in the containers
- `nginx:1.25` — The image to use

**Output:**

```
x9y8z7w6v5u4t3s2r1q0
```

This is the service ID.

### Check the Service

```bash
docker service ls
```

**Output:**

```
ID             NAME      MODE         REPLICAS   IMAGE         PORTS
x9y8z7w6v5u4   webapp    replicated   3/3        nginx:1.25    *:8080->80/tcp
```

`REPLICAS: 3/3` means 3 out of 3 desired replicas are running.

### See Where Tasks Are Running

```bash
docker service ps webapp
```

**Output:**

```
ID             NAME       IMAGE        NODE        DESIRED STATE   CURRENT STATE
a1b2c3d4e5f6   webapp.1   nginx:1.25   manager-1   Running         Running 30 seconds ago
g7h8i9j0k1l2   webapp.2   nginx:1.25   worker-1    Running         Running 28 seconds ago
m3n4o5p6q7r8   webapp.3   nginx:1.25   worker-2    Running         Running 29 seconds ago
```

Swarm distributed the 3 replicas across the 3 nodes automatically.

### Routing Mesh (Built-In Load Balancing)

When you publish a port, Swarm creates a **routing mesh**. Any node in the swarm can receive traffic on that port, and Swarm routes it to a running container — even if that node is not running the container.

```
+-----------------------------------------------------------+
|              Swarm Routing Mesh                            |
|                                                            |
|   User request --> ANY node:8080                           |
|                                                            |
|   +----------+     +----------+     +----------+           |
|   | Manager  |     | Worker 1 |     | Worker 2 |           |
|   | Port 8080| --> | Port 8080| --> | Port 8080|           |
|   |          |     | [webapp] |     | [webapp] |           |
|   +----------+     +----------+     +----------+           |
|                                                            |
|   Request to Manager:8080 gets routed to Worker 1 or 2.   |
|   Request to Worker 1:8080 may go to Worker 2's container. |
|   The routing mesh handles this transparently.             |
+-----------------------------------------------------------+
```

This means you can point your load balancer at ANY node in the swarm, and traffic reaches the right container.

---

## Scaling Services

Scaling is as simple as changing the replica count.

### Scale Up

```bash
docker service scale webapp=5
```

**Output:**

```
webapp scaled to 5
overall progress: 5 out of 5 tasks
1/5: running
2/5: running
3/5: running
4/5: running
5/5: running
verify: Service converged
```

Swarm created 2 new containers and distributed them across available nodes.

### Scale Down

```bash
docker service scale webapp=2
```

Swarm removes 3 containers, keeping only 2.

### Verify

```bash
docker service ls
```

**Output:**

```
ID             NAME      MODE         REPLICAS   IMAGE         PORTS
x9y8z7w6v5u4   webapp    replicated   2/2        nginx:1.25    *:8080->80/tcp
```

### Self-Healing

If a container crashes or a node goes down, Swarm automatically starts a replacement:

```bash
# Manually kill a container to simulate a crash
docker kill $(docker ps -q --filter "name=webapp")
```

Within seconds, Swarm detects the missing container and starts a new one. Run `docker service ps webapp` to see the replacement.

---

## Rolling Updates

A **rolling update** replaces containers one at a time (or in batches), ensuring the service stays available throughout the update.

```
+-----------------------------------------------------------+
|              Rolling Update Process                        |
|                                                            |
|   Before update (all running v1):                          |
|   [v1] [v1] [v1] [v1]                                     |
|                                                            |
|   Step 1: Stop one v1, start one v2:                       |
|   [v2] [v1] [v1] [v1]                                     |
|                                                            |
|   Step 2: (wait delay) Stop another v1, start v2:          |
|   [v2] [v2] [v1] [v1]                                     |
|                                                            |
|   Step 3: Continue...                                      |
|   [v2] [v2] [v2] [v1]                                     |
|                                                            |
|   Step 4: Done!                                            |
|   [v2] [v2] [v2] [v2]                                     |
|                                                            |
|   At NO point was the service completely down.             |
+-----------------------------------------------------------+
```

### Performing a Rolling Update

```bash
docker service update \
  --image nginx:1.26 \
  --update-delay 10s \
  --update-parallelism 1 \
  --update-failure-action rollback \
  webapp
```

**Line-by-line explanation:**

- `--image nginx:1.26` — Update to this new image version
- `--update-delay 10s` — Wait 10 seconds between updating each container
- `--update-parallelism 1` — Update 1 container at a time (default)
- `--update-failure-action rollback` — If the new container fails to start, automatically roll back to the previous version
- `webapp` — The service to update

### Watch the Update Progress

```bash
docker service ps webapp
```

**Output during update:**

```
ID             NAME          IMAGE        NODE        DESIRED STATE   CURRENT STATE
s1t2u3v4w5x6   webapp.1     nginx:1.26   worker-1    Running         Running 5 seconds ago
a1b2c3d4e5f6    \_ webapp.1  nginx:1.25   worker-1    Shutdown        Shutdown 10 seconds ago
g7h8i9j0k1l2   webapp.2     nginx:1.25   worker-2    Running         Running 2 minutes ago
```

The `\_` prefix shows the previous version of that task. Swarm keeps a history so you can see what changed.

### Rolling Back

If something goes wrong, roll back to the previous version:

```bash
docker service rollback webapp
```

Swarm replaces all containers with the previous image version.

### Configuring Update Behavior at Creation

```bash
docker service create \
  --name webapp \
  --replicas 4 \
  --publish 8080:80 \
  --update-delay 10s \
  --update-parallelism 2 \
  --update-failure-action rollback \
  --rollback-delay 5s \
  --rollback-parallelism 1 \
  nginx:1.25
```

This creates the service with update and rollback policies built in. Every future update will use these settings.

---

## Stack Deploy with Compose Files

For multi-service applications, you can deploy an entire stack using a Docker Compose file.

### Compose File for Swarm

```yaml
# docker-compose.yml (Swarm-compatible)
version: "3.8"

services:
  web:
    image: myusername/webapp:1.0.0
    ports:
      - "8080:80"
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
    networks:
      - frontend

  api:
    image: myusername/api-server:1.0.0
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
    networks:
      - frontend
      - backend

  db:
    image: postgres:16-alpine
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
    secrets:
      - db_password
    networks:
      - backend

networks:
  frontend:
  backend:

volumes:
  db-data:

secrets:
  db_password:
    external: true
```

### Deploy the Stack

```bash
# First, create the secret
echo "MyDatabasePassword" | docker secret create db_password -

# Deploy the stack
docker stack deploy -c docker-compose.yml myapp
```

**Output:**

```
Creating network myapp_frontend
Creating network myapp_backend
Creating service myapp_web
Creating service myapp_api
Creating service myapp_db
```

### Manage the Stack

```bash
# List all stacks
docker stack ls
```

**Output:**

```
NAME      SERVICES   ORCHESTRATOR
myapp     3          Swarm
```

```bash
# List services in the stack
docker stack services myapp
```

**Output:**

```
ID             NAME        MODE         REPLICAS   IMAGE                         PORTS
a1b2c3d4e5f6   myapp_web   replicated   3/3        myusername/webapp:1.0.0        *:8080->80/tcp
g7h8i9j0k1l2   myapp_api   replicated   2/2        myusername/api-server:1.0.0
m3n4o5p6q7r8   myapp_db    replicated   1/1        postgres:16-alpine
```

```bash
# Remove the stack
docker stack rm myapp
```

### Key Differences from Regular Compose

The `deploy` section is **Swarm-only**. It is ignored by `docker compose up`. Some key Swarm-specific settings:

- `deploy.replicas` — How many copies to run
- `deploy.update_config` — How to perform rolling updates
- `deploy.placement.constraints` — Control which nodes run which services
- `deploy.resources` — CPU and memory limits
- `secrets` — Swarm secrets management

---

## Swarm Visualizer

The **Docker Swarm Visualizer** is a web application that shows your cluster in a visual dashboard.

```bash
docker service create \
  --name visualizer \
  --publish 9090:8080 \
  --constraint 'node.role == manager' \
  --mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock \
  dockersamples/visualizer:latest
```

Open `http://manager-ip:9090` in your browser. You will see:

```
+-----------------------------------------------------------+
|              Swarm Visualizer (Web UI)                     |
|                                                            |
|   +----------------+ +----------------+ +----------------+ |
|   | manager-1      | | worker-1       | | worker-2       | |
|   |                | |                | |                | |
|   | [webapp.1]     | | [webapp.2]     | | [webapp.3]     | |
|   | [visualizer]   | | [api.1]        | | [api.2]        | |
|   | [db.1]         | |                | |                | |
|   +----------------+ +----------------+ +----------------+ |
|                                                            |
|   Each box is a node. Each colored rectangle is a task.    |
+-----------------------------------------------------------+
```

---

## Draining Nodes

**Draining** a node tells Swarm to stop running tasks on that node and reschedule them elsewhere. This is useful for maintenance — updating the operating system, replacing hardware, or decommissioning a server.

### Drain a Node

```bash
docker node update --availability drain worker-2
```

**What happens:**

1. Swarm stops scheduling new tasks on `worker-2`
2. All running tasks on `worker-2` are stopped
3. Replacement tasks are started on other available nodes
4. `worker-2` is now idle — safe to perform maintenance

### Verify

```bash
docker node ls
```

**Output:**

```
ID              HOSTNAME     STATUS    AVAILABILITY   MANAGER STATUS
abc123 *        manager-1    Ready     Active         Leader
ghi789          worker-1     Ready     Active
mno345          worker-2     Ready     Drain
```

`worker-2` shows `Drain` — it is not running any tasks.

### Reactivate the Node

After maintenance:

```bash
docker node update --availability active worker-2
```

Swarm can now schedule tasks on `worker-2` again. Existing tasks are NOT moved back automatically — new tasks and rebalancing will use it.

---

## Swarm vs Kubernetes

Docker Swarm and Kubernetes both solve the same problem — container orchestration — but with very different approaches.

```
+-----------------------------------------------------------+
|              Swarm vs Kubernetes                           |
|                                                            |
|   Docker Swarm:                                            |
|   - "Easy to learn, limited features"                     |
|   - Like a bicycle: simple, gets you where you need to go |
|                                                            |
|   Kubernetes:                                              |
|   - "Complex to learn, unlimited features"                |
|   - Like a car: powerful, but you need driving lessons     |
+-----------------------------------------------------------+
```

### Comparison Table

| Feature                | Docker Swarm            | Kubernetes               |
|------------------------|------------------------|--------------------------|
| Setup difficulty       | Very easy              | Complex                  |
| Learning curve         | Gentle                 | Steep                    |
| Built into Docker      | Yes                    | No (separate install)    |
| Scaling                | Manual or simple       | Auto-scaling built in    |
| Rolling updates        | Yes                    | Yes, more options        |
| Service discovery      | Built in               | Built in, more flexible  |
| Load balancing         | Built in               | Built in + Ingress       |
| Storage management     | Basic                  | Advanced (PV, PVC, SC)   |
| Networking             | Overlay networks       | CNI plugins (many options)|
| Configuration          | Docker Compose files   | YAML manifests           |
| Community & ecosystem  | Smaller                | Massive                  |
| Cloud provider support | Limited                | AWS EKS, GKE, AKS       |
| Best for               | Small-medium teams     | Large teams, complex apps|

### When to Choose Swarm

- You are already using Docker and want something simple
- Your team is small (1-10 people)
- You have a few services (1-20)
- You do not need auto-scaling
- You want to get started quickly without a learning curve

### When to Choose Kubernetes

- You have a large team (10+ people)
- You run many services (20+)
- You need auto-scaling based on CPU, memory, or custom metrics
- You need advanced networking (service mesh, ingress controllers)
- You deploy to cloud providers (AWS, GCP, Azure all offer managed Kubernetes)
- You need a large ecosystem of tools and plugins

### Learning Path

If you are new to orchestration, start with Docker Swarm. The concepts (services, replicas, rolling updates, nodes) are the same in Kubernetes — just with different commands and more options. Swarm is the training ground; Kubernetes is the next level.

---

## Common Mistakes

### Mistake 1: Running a Single Manager in Production

```bash
docker swarm init  # Only one manager
```

If this manager dies, the entire swarm is leaderless. No new tasks can be scheduled, no updates can be performed.

**Fix:** Use at least 3 manager nodes in production for fault tolerance.

### Mistake 2: Not Using Update Policies

```bash
docker service update --image myapp:2.0 webapp
# No --update-delay, no --update-failure-action
```

Without update policies, all containers update simultaneously. If the new version has a bug, the entire service goes down.

**Fix:** Always configure update delay and rollback action:

```bash
docker service update \
  --image myapp:2.0 \
  --update-delay 10s \
  --update-failure-action rollback \
  webapp
```

### Mistake 3: Storing Data in Containers Without Volumes

If a task (container) is rescheduled to a different node, any data written to the container's filesystem is lost.

**Fix:** Use volumes for all persistent data, especially databases.

### Mistake 4: Exposing Manager Ports to the Internet

The Swarm management port (2377) and the node communication ports (7946, 4789) should only be accessible between swarm nodes.

**Fix:** Use firewall rules to restrict access to these ports to only swarm node IPs.

### Mistake 5: Not Using Secrets for Sensitive Data

```yaml
# BAD: Password in plain text in the compose file
environment:
  DB_PASSWORD: MySecret123
```

**Fix:** Use Docker Swarm secrets:

```yaml
secrets:
  - db_password
```

---

## Best Practices

1. **Use 3 or 5 manager nodes** in production for fault tolerance
2. **Always configure rolling update policies** — Set delay, parallelism, and rollback action
3. **Use secrets for sensitive data** — Never put passwords in compose files or environment variables
4. **Drain nodes before maintenance** — Safely move tasks before updating or rebooting
5. **Use placement constraints** — Pin databases to specific nodes with fast storage
6. **Monitor your swarm** — Use the visualizer during development, Prometheus in production
7. **Set resource limits** — Prevent one service from consuming all resources
8. **Use overlay networks** — Isolate service communication with dedicated networks
9. **Keep manager nodes lightweight** — Avoid running heavy workloads on managers
10. **Test rollback procedures** — Regularly verify that rollbacks work correctly

---

## Quick Summary

Docker Swarm turns multiple Docker hosts into a coordinated cluster that manages containers as services. Manager nodes make scheduling decisions while worker nodes execute tasks. Services define the desired state (image, replicas, ports), and Swarm ensures that state is maintained — replacing crashed containers and distributing workloads. Rolling updates replace containers gradually for zero-downtime deployments. Stack deploy uses Docker Compose files to deploy multi-service applications. Draining nodes allows safe maintenance without service disruption. While Kubernetes offers more features and a larger ecosystem, Docker Swarm provides a simpler path to container orchestration that uses familiar Docker concepts and commands.

---

## Key Points

- **Docker Swarm** turns multiple Docker hosts into a single orchestrated cluster
- **Manager nodes** schedule tasks and maintain state; **worker nodes** run containers
- **Services** define the desired state; **tasks** are the actual running containers
- **`docker service create`** creates a service; **`docker service scale`** changes the replica count
- **Rolling updates** replace containers gradually with `--update-delay` and `--update-parallelism`
- **`docker stack deploy`** deploys multi-service applications from Compose files
- **Routing mesh** lets any node receive traffic and route it to the right container
- **Self-healing** automatically replaces crashed containers
- **Drain** removes a node from the scheduling pool for safe maintenance
- **Swarm is simpler** than Kubernetes but has fewer features; start with Swarm, graduate to Kubernetes

---

## Practice Questions

1. What is the difference between a manager node and a worker node in Docker Swarm? Can a manager node also run containers?

2. Explain the difference between `docker run` and `docker service create`. When would you use each?

3. You have a service with 4 replicas and you need to update the image. Describe how a rolling update works with `--update-delay 10s` and `--update-parallelism 1`.

4. What happens when you drain a node? What happens to the tasks that were running on it?

5. When would you choose Docker Swarm over Kubernetes? When would you choose Kubernetes over Docker Swarm?

---

## Exercises

### Exercise 1: Create Your First Swarm

1. Initialize a single-node swarm with `docker swarm init`
2. Create a service: `docker service create --name web --replicas 3 --publish 8080:80 nginx:latest`
3. Visit `http://localhost:8080` to verify it works
4. Run `docker service ps web` to see where tasks are running
5. Kill one container manually and watch Swarm replace it
6. Scale to 5 replicas and verify with `docker service ls`

### Exercise 2: Rolling Update

1. Create a service running `nginx:1.24` with 4 replicas
2. Perform a rolling update to `nginx:1.25` with a 5-second delay
3. Watch the update progress with `docker service ps`
4. Roll back to `nginx:1.24` with `docker service rollback`
5. Verify all tasks are back on the previous version

### Exercise 3: Stack Deploy

1. Create a `docker-compose.yml` with two services: a web app (nginx) and an API (any simple image)
2. Add `deploy` sections with replicas, update config, and resource limits
3. Deploy the stack with `docker stack deploy -c docker-compose.yml mystack`
4. List all services with `docker stack services mystack`
5. Update one service's image and watch the rolling update
6. Remove the stack with `docker stack rm mystack`

---

## What Is Next?

You now know how to orchestrate containers across multiple machines. But orchestration only works well when your images are efficient. In the next chapter, we explore **Optimizing Docker Images** — reducing image sizes for faster pulls, smaller attack surfaces, and more efficient use of storage and bandwidth. A 1 GB image that could be 50 MB is not just wasteful — it is a bottleneck that slows down everything.
