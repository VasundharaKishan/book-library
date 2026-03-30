# Chapter 23: Docker in Production

## What You Will Learn

By the end of this chapter, you will be able to:

- Set resource limits on containers to prevent resource exhaustion
- Configure restart policies so containers self-heal after failures
- Choose and configure logging drivers for centralized log management
- Monitor containers with docker stats, cAdvisor, and Prometheus
- Handle graceful shutdown with proper SIGTERM handling
- Follow a production readiness checklist

---

## Why This Chapter Matters

Running Docker on your laptop for development is forgiving. If a container uses too much memory, you close it. If it crashes, you restart it manually. If the logs are messy, you scroll through the terminal.

Production is a different world. A container that consumes all available memory can take down every other container on the server. A crashed container that does not restart means your application is offline at 3 AM. Logs that are not forwarded to a central system are lost when the container is removed.

Think of the difference like this: driving in a parking lot versus driving on a highway. In a parking lot, mistakes are harmless. On a highway, every detail matters — speed, fuel, tire pressure, and mirrors. This chapter teaches you the "highway driving" skills for Docker.

---

## Resource Limits

By default, a container can use as much CPU and memory as it wants. On a shared server, one runaway container can starve every other container of resources.

### Memory Limits

```bash
# Limit container to 512 MB of memory
docker run --memory 512m myapp

# Limit to 1 GB
docker run --memory 1g myapp

# Limit memory AND swap (swap is disk used as overflow memory)
docker run --memory 512m --memory-swap 1g myapp
```

**What `--memory` does:**

- Sets a hard limit on how much RAM the container can use
- If the container tries to use more, it is **killed** by the Linux kernel (OOM — Out of Memory)
- The container's exit code will be 137 (which means "killed by signal 9 / SIGKILL")

```
+-----------------------------------------------------------+
|              Memory Limits                                 |
|                                                            |
|   Server has 4 GB RAM                                      |
|                                                            |
|   Without limits:                                          |
|   +-----------+ +----------+ +-----------+                 |
|   | Container | | Container| | Container |                 |
|   | A: 3 GB!! | | B: 0.5GB | | C: DEAD   |                |
|   +-----------+ +----------+ +-----------+                 |
|   Container A consumed all memory, C was killed.           |
|                                                            |
|   With limits (--memory 1g each):                          |
|   +-----------+ +----------+ +-----------+                 |
|   | Container | | Container| | Container |                 |
|   | A: 1 GB   | | B: 0.5GB | | C: 0.5GB  |                |
|   +-----------+ +----------+ +-----------+                 |
|   Each container gets its fair share. None can hog.        |
+-----------------------------------------------------------+
```

### CPU Limits

```bash
# Limit to 1 CPU core
docker run --cpus 1.0 myapp

# Limit to half a CPU core
docker run --cpus 0.5 myapp

# Limit to 2 CPU cores
docker run --cpus 2.0 myapp
```

**What `--cpus` does:**

- Sets how much CPU time the container can use
- `--cpus 1.0` means the container can use the equivalent of one full core
- `--cpus 0.5` means the container gets at most 50% of one core
- Unlike memory limits, exceeding the CPU limit does NOT kill the container — it just slows down

### CPU Shares (Relative Priority)

```bash
# Higher number = higher priority when CPU is contended
docker run --cpu-shares 1024 high-priority-app
docker run --cpu-shares 512  low-priority-app
```

CPU shares only matter when the CPU is fully loaded. When CPU is available, both containers can use as much as they need.

### Resource Limits in Docker Compose

```yaml
services:
  web:
    image: myapp:1.0.0
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
```

**Explanation:**

- `limits` — Maximum resources the container can use
- `reservations` — Minimum resources guaranteed to the container. Docker will not schedule the container on a host that cannot provide at least this much.

### Checking Resource Usage

```bash
docker stats
```

**Output:**

```
CONTAINER ID   NAME   CPU %   MEM USAGE / LIMIT   MEM %   NET I/O         BLOCK I/O
a1b2c3d4e5f6   web    2.5%    125MiB / 512MiB     24.4%   1.2MB / 500kB   0B / 0B
f6e5d4c3b2a1   db     15.3%   350MiB / 1GiB       34.2%   2.5MB / 1.8MB   50MB / 10MB
```

This shows real-time resource usage for all running containers.

---

## Restart Policies

A **restart policy** tells Docker what to do when a container stops. Without a restart policy, a crashed container stays dead until someone manually restarts it.

### Available Restart Policies

| Policy          | What It Does                                           |
|-----------------|-------------------------------------------------------|
| `no`            | Never restart (default)                                |
| `always`        | Always restart, no matter why it stopped               |
| `unless-stopped`| Always restart UNLESS manually stopped with `docker stop` |
| `on-failure`    | Restart only if the container exits with a non-zero exit code |

### Using Restart Policies

```bash
# Never restart (default behavior)
docker run --restart no myapp

# Always restart — even after Docker daemon restarts
docker run --restart always myapp

# Restart unless manually stopped
docker run --restart unless-stopped myapp

# Restart only on failure, up to 5 attempts
docker run --restart on-failure:5 myapp
```

### When to Use Each Policy

```
+-----------------------------------------------------------+
|              Restart Policy Decision Tree                   |
|                                                            |
|   Is this a development container?                         |
|     YES --> "no" (you want to see crashes)                 |
|     NO  --> Continue                                       |
|                                                            |
|   Should it survive Docker daemon restarts (reboots)?      |
|     YES --> Continue                                       |
|     NO  --> "on-failure" (restart only on crashes)         |
|                                                            |
|   Should `docker stop` permanently stop it?                |
|     YES --> "unless-stopped"                               |
|     NO  --> "always"                                       |
+-----------------------------------------------------------+
```

**Detailed explanation of each:**

**`no` (default):** The container stops and stays stopped. Use this for development, one-off tasks, and batch jobs.

```bash
docker run --restart no myapp
# Container crashes at 2 AM. It stays dead until morning.
```

**`always`:** Docker restarts the container whenever it stops, regardless of the exit code. It even restarts after the Docker daemon restarts (like after a server reboot).

```bash
docker run --restart always myapp
# Container crashes at 2 AM. Docker restarts it immediately.
# Server reboots at 3 AM. Docker restarts it after boot.
# You run `docker stop myapp`. Docker restarts it anyway!
```

**`unless-stopped`:** Like `always`, but respects `docker stop`. If you manually stop the container, it stays stopped even after a daemon restart.

```bash
docker run --restart unless-stopped myapp
# Container crashes at 2 AM. Docker restarts it.
# You run `docker stop myapp`. It stays stopped. Docker respects your intent.
```

**`on-failure[:max-retries]`:** Restarts only when the container exits with a non-zero exit code (meaning it crashed, not exited cleanly). The optional `max-retries` limits restart attempts.

```bash
docker run --restart on-failure:5 myapp
# Container crashes (exit code 1). Docker restarts it.
# After 5 consecutive failures, Docker gives up.
# Container exits with code 0 (clean exit). Docker does NOT restart it.
```

### Restart Policies in Docker Compose

```yaml
services:
  web:
    image: myapp:1.0.0
    restart: unless-stopped

  worker:
    image: myapp-worker:1.0.0
    restart: on-failure:5

  one-off-task:
    image: myapp-migrate:1.0.0
    restart: "no"
```

---

## Logging Drivers

By default, Docker captures container logs (stdout and stderr) and stores them as JSON files on the host. This works for development but creates problems in production:

- Log files grow without limit and fill up the disk
- Logs are lost when a container is removed
- You cannot search across multiple containers
- No central dashboard for monitoring

**Logging drivers** send container logs to external systems.

### Default: json-file

```bash
# View default logging driver
docker info | grep "Logging Driver"
# Output: Logging Driver: json-file
```

```bash
# Configure max file size and rotation
docker run \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  myapp
```

**What this does:**

- `max-size=10m` — Each log file can be at most 10 MB
- `max-file=3` — Keep at most 3 log files (total max: 30 MB)
- When the current file reaches 10 MB, it is rotated: `container-id.log` becomes `container-id.log.1`, and a new log file starts

> **Critical:** Without `max-size` and `max-file`, log files grow forever. A busy application can fill a 100 GB disk in days. Always set these limits.

### syslog

Sends logs to a syslog server, which is the standard logging system on Linux:

```bash
docker run \
  --log-driver syslog \
  --log-opt syslog-address=udp://logserver:514 \
  --log-opt tag="myapp" \
  myapp
```

### fluentd

Sends logs to **Fluentd**, a popular log collection and forwarding tool:

```bash
docker run \
  --log-driver fluentd \
  --log-opt fluentd-address=localhost:24224 \
  --log-opt tag="docker.myapp" \
  myapp
```

```
+-----------------------------------------------------------+
|              Centralized Logging Architecture              |
|                                                            |
|   Server 1              Server 2                           |
|   +---------+           +---------+                        |
|   | App A   |           | App C   |                        |
|   | App B   |           | App D   |                        |
|   +---------+           +---------+                        |
|       |                     |                              |
|       v                     v                              |
|   +------------------------------------------+             |
|   |          Fluentd / Logstash              |             |
|   |      (collects and forwards logs)        |             |
|   +------------------------------------------+             |
|       |                                                    |
|       v                                                    |
|   +------------------------------------------+             |
|   |     Elasticsearch / Loki / CloudWatch    |             |
|   |          (stores and indexes)            |             |
|   +------------------------------------------+             |
|       |                                                    |
|       v                                                    |
|   +------------------------------------------+             |
|   |        Kibana / Grafana Dashboard         |             |
|   |          (search and visualize)           |             |
|   +------------------------------------------+             |
+-----------------------------------------------------------+
```

### Logging Drivers in Docker Compose

```yaml
services:
  web:
    image: myapp:1.0.0
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### Comparison of Logging Drivers

| Driver     | Where Logs Go        | Use Case                    |
|-----------|---------------------|----------------------------|
| json-file | Local JSON files     | Development, small setups   |
| syslog    | Syslog server        | Linux infrastructure        |
| fluentd   | Fluentd collector    | Kubernetes, complex setups  |
| awslogs   | AWS CloudWatch       | AWS deployments             |
| gcplogs   | Google Cloud Logging | GCP deployments             |
| gelf      | Graylog (GELF)       | Graylog users               |
| none      | Nowhere (discarded)  | When logs are not needed    |

---

## Monitoring

Monitoring tells you what your containers are doing right now and alerts you when something goes wrong.

### docker stats (Built-In)

The simplest monitoring tool is built into Docker:

```bash
# Real-time resource usage for all containers
docker stats

# Monitor specific containers
docker stats web db redis

# One-time snapshot (no streaming)
docker stats --no-stream
```

**Output:**

```
CONTAINER   CPU %   MEM USAGE / LIMIT   MEM %   NET I/O        BLOCK I/O
web         3.2%    128MiB / 512MiB     25.0%   5.2MB / 1.1MB  0B / 0B
db          12.1%   450MiB / 1GiB       44.0%   2.1MB / 890kB  100MB / 50MB
redis       0.5%    12MiB / 256MiB      4.7%    500kB / 200kB  0B / 0B
```

**Column meanings:**

- `CPU %` — Percentage of CPU being used
- `MEM USAGE / LIMIT` — Current memory usage and the limit (if set)
- `MEM %` — Memory usage as a percentage of the limit
- `NET I/O` — Network data received / sent
- `BLOCK I/O` — Disk data read / written

### cAdvisor (Container Advisor)

**cAdvisor** is Google's open-source tool for monitoring container resource usage. It provides a web UI and exports metrics for Prometheus.

```bash
docker run -d \
  --name cadvisor \
  --volume /:/rootfs:ro \
  --volume /var/run:/var/run:ro \
  --volume /sys:/sys:ro \
  --volume /var/lib/docker/:/var/lib/docker:ro \
  --publish 8080:8080 \
  gcr.io/cadvisor/cadvisor:latest
```

**After starting, open `http://localhost:8080` in your browser.** You will see:

- CPU usage graphs per container
- Memory usage graphs per container
- Network traffic per container
- Filesystem usage per container

### Prometheus + Grafana

For production monitoring, **Prometheus** collects metrics and **Grafana** visualizes them in dashboards.

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"
    restart: unless-stopped
```

**Prometheus configuration:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'docker'
    static_configs:
      - targets: ['host.docker.internal:9323']
```

```
+-----------------------------------------------------------+
|              Monitoring Stack                              |
|                                                            |
|   Your Containers                                          |
|   +------+ +------+ +------+                               |
|   | Web  | | DB   | | Redis|                               |
|   +------+ +------+ +------+                               |
|       |        |        |                                  |
|       v        v        v                                  |
|   +---------------------------+                            |
|   |       cAdvisor            |  Collects metrics          |
|   +---------------------------+                            |
|               |                                            |
|               v                                            |
|   +---------------------------+                            |
|   |       Prometheus          |  Stores metrics            |
|   +---------------------------+  Time-series database      |
|               |                                            |
|               v                                            |
|   +---------------------------+                            |
|   |       Grafana             |  Visualizes metrics        |
|   +---------------------------+  Dashboards + alerts       |
+-----------------------------------------------------------+
```

### Health Checks

**Health checks** let Docker (and monitoring tools) know if your application is actually working, not just running.

```dockerfile
# In your Dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
  CMD curl -f http://localhost:3000/health || exit 1
```

**What each option means:**

- `--interval=30s` — Check every 30 seconds
- `--timeout=5s` — If the check takes more than 5 seconds, it counts as a failure
- `--retries=3` — After 3 consecutive failures, mark the container as "unhealthy"
- `--start-period=10s` — Wait 10 seconds after starting before the first check (gives the app time to boot)
- `CMD curl -f http://localhost:3000/health || exit 1` — The actual health check command. Exit code 0 = healthy, exit code 1 = unhealthy.

```bash
# Check container health status
docker inspect --format='{{.State.Health.Status}}' myapp
# Output: healthy
```

```bash
# See health check history
docker inspect --format='{{json .State.Health}}' myapp | python3 -m json.tool
```

---

## Graceful Shutdown

When Docker stops a container, it sends a **SIGTERM** signal first, waits for the process to shut down cleanly, and then sends **SIGKILL** (force kill) if it takes too long.

```
+-----------------------------------------------------------+
|              Docker Stop Sequence                          |
|                                                            |
|   docker stop myapp                                        |
|        |                                                   |
|        v                                                   |
|   1. Send SIGTERM to the main process                      |
|      "Please shut down gracefully"                         |
|        |                                                   |
|        v                                                   |
|   2. Wait (default: 10 seconds)                            |
|      Container can finish requests, close connections,     |
|      save state, flush buffers                             |
|        |                                                   |
|        v (if still running after timeout)                  |
|   3. Send SIGKILL                                          |
|      "You are dead now. No choice."                        |
|      Immediate termination. No cleanup.                    |
+-----------------------------------------------------------+
```

### Why Graceful Shutdown Matters

Without graceful shutdown:

- **HTTP requests in progress are dropped** — Users see error pages
- **Database transactions are interrupted** — Data corruption possible
- **Files being written are truncated** — Partial data on disk
- **Connections to other services are abandoned** — Other services may retry and create duplicates

### Handling SIGTERM in Node.js

```javascript
// server.js
const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end('Hello World\n');
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received. Shutting down gracefully...');

  // Stop accepting new connections
  server.close(() => {
    console.log('All connections closed. Exiting.');
    process.exit(0);
  });

  // Force exit after 5 seconds if connections are not closed
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 5000);
});
```

### Handling SIGTERM in Python

```python
# server.py
import signal
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello World\n')

server = HTTPServer(('', 8000), Handler)

def graceful_shutdown(signum, frame):
    print('SIGTERM received. Shutting down...')
    server.shutdown()
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)

print('Server running on port 8000')
server.serve_forever()
```

### The PID 1 Problem

In Docker, the main process runs as **PID 1** (process ID 1). PID 1 has special behavior in Linux — it does NOT receive default signal handlers. This means:

```dockerfile
# PROBLEM: Shell form wraps your command in /bin/sh
CMD node server.js
# Actually runs: /bin/sh -c "node server.js"
# PID 1 is /bin/sh, not node. SIGTERM goes to /bin/sh,
# which does NOT forward it to node.
```

```dockerfile
# SOLUTION: Exec form runs your command directly
CMD ["node", "server.js"]
# node IS PID 1. SIGTERM goes directly to node.
```

**Always use the exec form (JSON array) for CMD and ENTRYPOINT.** The shell form wraps your command in `/bin/sh`, which does not forward signals.

### Using tini as an Init Process

If your application spawns child processes, you may need a proper init system. **tini** is a tiny init process designed for containers:

```dockerfile
FROM node:20-alpine

# Install tini
RUN apk add --no-cache tini

WORKDIR /app
COPY . .
RUN npm ci --only=production

# Use tini as the entrypoint
ENTRYPOINT ["tini", "--"]
CMD ["node", "server.js"]
```

tini properly forwards signals and reaps zombie processes (cleaned up child processes that have exited but not been collected).

### Adjusting the Stop Timeout

```bash
# Give the container 30 seconds to shut down (default is 10)
docker stop --time 30 myapp
```

In Docker Compose:

```yaml
services:
  web:
    image: myapp:1.0.0
    stop_grace_period: 30s
```

---

## Production Checklist

Use this checklist before deploying any container to production.

### Resource Management

```
[ ] Set memory limits (--memory)
[ ] Set CPU limits (--cpus)
[ ] Configure log rotation (max-size, max-file)
[ ] Monitor resource usage (docker stats, cAdvisor, Prometheus)
```

### Reliability

```
[ ] Set appropriate restart policy (usually unless-stopped)
[ ] Add health checks (HEALTHCHECK in Dockerfile)
[ ] Handle SIGTERM for graceful shutdown
[ ] Use exec form for CMD (JSON array syntax)
[ ] Test container behavior under load
[ ] Test container recovery after crash
```

### Logging and Monitoring

```
[ ] Configure logging driver (or at minimum, log rotation)
[ ] Set up centralized log aggregation for multi-server deployments
[ ] Add monitoring dashboards (Grafana)
[ ] Configure alerts for high CPU, memory, and error rates
[ ] Ensure application logs include timestamps and request IDs
```

### Security (from Chapter 22)

```
[ ] Run as non-root user
[ ] Use minimal base images
[ ] Scan for vulnerabilities
[ ] No secrets in image layers
[ ] Read-only filesystem where possible
[ ] Drop unnecessary capabilities
```

### Deployment

```
[ ] Pin image versions (no :latest in production)
[ ] Use Docker Compose or orchestration for multi-container apps
[ ] Test rollback procedure
[ ] Document deployment process
[ ] Set up CI/CD pipeline (from Chapter 21)
```

---

## Common Mistakes

### Mistake 1: No Memory Limits

```bash
# A memory leak causes the container to use ALL available memory
docker run myapp  # No --memory flag
```

The container grows to consume all available RAM, then the Linux OOM killer starts killing processes — possibly including other containers or system processes.

**Fix:**

```bash
docker run --memory 512m myapp
```

### Mistake 2: Using restart: always for Everything

```bash
# A container that crashes on startup will restart in an infinite loop
docker run --restart always broken-app
```

If the application always fails (like a misconfigured database connection), Docker restarts it endlessly, consuming CPU and filling logs.

**Fix:** Use `on-failure:5` to limit retries, or `unless-stopped` so you can manually stop the loop with `docker stop`.

### Mistake 3: No Log Rotation

Without `max-size` and `max-file`, Docker log files grow without limit:

```bash
# Check log file size
du -sh /var/lib/docker/containers/*/
# Could show: 50G for a single container!
```

**Fix:** Always set log rotation:

```bash
docker run --log-opt max-size=10m --log-opt max-file=3 myapp
```

Or set it globally in `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Mistake 4: Shell Form CMD

```dockerfile
# WRONG — SIGTERM is not forwarded to the application
CMD node server.js

# RIGHT — SIGTERM goes directly to the application
CMD ["node", "server.js"]
```

### Mistake 5: No Health Checks

Without health checks, Docker considers a container "healthy" as long as the process is running — even if the application is frozen, deadlocked, or returning errors.

**Fix:** Add a HEALTHCHECK to your Dockerfile or docker-compose.yml.

---

## Best Practices

1. **Always set memory limits** — Prevent one container from starving others
2. **Use `unless-stopped` restart policy** — Self-healing with manual override
3. **Configure log rotation** — Prevent disk space exhaustion
4. **Add health checks** — Let Docker know if your application is actually working
5. **Handle SIGTERM** — Shut down gracefully to avoid dropped requests and data loss
6. **Use exec form for CMD** — Ensure signals reach your application
7. **Monitor with Prometheus + Grafana** — Real-time visibility and alerting
8. **Set the stop grace period** — Give applications enough time to shut down cleanly
9. **Use tini for multi-process containers** — Proper signal forwarding and zombie reaping
10. **Test failure scenarios** — Kill containers intentionally and verify recovery

---

## Quick Summary

Production Docker deployments require resource limits to prevent containers from consuming all available memory and CPU. Restart policies like `unless-stopped` enable self-healing while respecting manual overrides. Logging drivers and log rotation prevent disk exhaustion and enable centralized log management. Monitoring with docker stats, cAdvisor, and Prometheus provides visibility into container performance. Graceful shutdown through proper SIGTERM handling prevents dropped requests and data corruption. Health checks tell Docker whether an application is truly working, not just running. Together, these practices transform containers from development tools into production-ready infrastructure.

---

## Key Points

- **`--memory`** and **`--cpus`** prevent resource exhaustion on shared servers
- **Restart policies** control what happens when a container stops: `no`, `always`, `unless-stopped`, `on-failure`
- **Log rotation** (`max-size`, `max-file`) is essential to prevent disk full errors
- **Logging drivers** (syslog, fluentd, awslogs) send logs to centralized systems
- **docker stats** provides real-time resource usage; **cAdvisor** and **Prometheus** provide historical data
- **SIGTERM** is Docker's polite shutdown signal; **SIGKILL** is the forced shutdown after timeout
- **Exec form** (`CMD ["node", "server.js"]`) ensures signals reach your application
- **Health checks** detect when an application is frozen or broken, not just when the process exits
- **tini** is a minimal init process that handles signals and zombie processes correctly
- A **production checklist** covers resources, reliability, logging, security, and deployment

---

## Practice Questions

1. What happens when a container exceeds its memory limit set by `--memory`? How is this different from exceeding its CPU limit set by `--cpus`?

2. Explain the difference between the restart policies `always` and `unless-stopped`. When would you choose one over the other?

3. Why is log rotation important? What Docker options control log rotation, and what happens if you do not configure them?

4. What is the difference between `CMD node server.js` and `CMD ["node", "server.js"]` in a Dockerfile? Why does it matter for graceful shutdown?

5. Describe the Docker stop sequence. What signal is sent first? How long does Docker wait? What happens after the timeout?

---

## Exercises

### Exercise 1: Resource Limits

1. Run a container with `--memory 128m` using any image
2. Inside the container, try to allocate more memory than the limit (you can use a stress test tool)
3. Observe what happens when the limit is exceeded
4. Run `docker inspect` on the container to see the exit code (should be 137)
5. Repeat with `--cpus 0.5` and observe how CPU usage is throttled using `docker stats`

### Exercise 2: Restart Policies

1. Create a container that deliberately crashes after 5 seconds: `docker run --restart on-failure:3 alpine sh -c "echo 'Starting...'; sleep 5; exit 1"`
2. Watch the container restart (use `docker ps` and `docker logs`)
3. After 3 restarts, verify Docker stops trying
4. Change to `--restart unless-stopped` and observe the difference
5. Stop it manually with `docker stop` and verify it does not restart

### Exercise 3: Monitoring Stack

1. Start cAdvisor using the command shown in this chapter
2. Open `http://localhost:8080` and explore the container metrics
3. Run a few containers with resource limits
4. Observe CPU and memory usage in the cAdvisor dashboard
5. Bonus: Set up the full Prometheus + Grafana stack using the docker-compose file in this chapter

---

## What Is Next?

You now know how to run containers reliably in production. But what happens when one server is not enough? When you need to run 10, 50, or 100 copies of your application across multiple machines? In the next chapter, we explore **Docker Swarm** — Docker's built-in orchestration tool for managing clusters of containers across multiple servers.
