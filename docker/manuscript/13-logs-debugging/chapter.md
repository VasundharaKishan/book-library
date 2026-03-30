# Chapter 13: Logs and Debugging

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Read container logs using `docker logs`
- Filter logs by time, count, and follow them in real time
- Get inside a running container with `docker exec`
- Inspect container details like IP address, mounts, and environment variables
- Add health checks to your Dockerfiles
- Monitor Docker events in real time
- Diagnose and fix the most common container problems
- Follow a systematic debugging flowchart when things go wrong

---

## Why This Chapter Matters

Things will go wrong. Your container will crash. Your application will not start. Your database connection will fail. A file will be missing. A port will be in use. This is not a question of "if" but "when."

The difference between a frustrated developer and a productive one is not that the productive developer never has problems. It is that they know how to find and fix problems quickly. This chapter gives you that superpower.

Think of debugging like being a detective. When a crime happens, a detective does not panic. They follow a process: check the evidence (logs), examine the scene (inspect), interview witnesses (events), and look for patterns (common issues). By the end of this chapter, you will be a Docker detective.

---

## Reading Container Logs with docker logs

Every application produces output — messages about what it is doing, warnings about potential problems, and error messages when something breaks. When an application runs inside a Docker container, Docker captures all of this output and stores it for you.

### Basic Log Reading

Let us start a container and look at its logs:

```bash
docker run -d --name my-web -p 8080:80 nginx
```

Now visit `http://localhost:8080` in your browser a few times. Then read the logs:

```bash
docker logs my-web
```

**Output:**

```
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
...
2024-01-15 10:30:00 172.17.0.1 - - [15/Jan/2024:10:30:00 +0000] "GET / HTTP/1.1" 200 615 "-" "Mozilla/5.0..."
2024-01-15 10:30:01 172.17.0.1 - - [15/Jan/2024:10:30:01 +0000] "GET /favicon.ico HTTP/1.1" 404 153 "-" "Mozilla/5.0..."
```

Each line is a log entry. For nginx, you can see:

- **Startup messages**: Lines that start with `/docker-entrypoint.sh` show nginx initializing.
- **Access logs**: Lines showing HTTP requests. The `200` means "OK" (the page was found). The `404` means "Not Found" (the favicon was not found, which is normal).

### Understanding What Docker Logs Captures

Docker captures two streams of output:

1. **stdout** (standard output): Normal messages. Think of this as the application talking normally.
2. **stderr** (standard error): Error messages. Think of this as the application shouting about problems.

```
┌─────────────────────────────────┐
│        Your Container           │
│                                 │
│   Application                   │
│     │                           │
│     ├── stdout ──> "Started OK" │──> docker logs
│     │                           │
│     └── stderr ──> "Error!"     │──> docker logs
│                                 │
└─────────────────────────────────┘
```

Both streams appear when you run `docker logs`. This is important to understand because some applications write their logs to files instead of stdout/stderr. If your application writes to `/var/log/app.log` inside the container, `docker logs` will not show those logs. You would need to go inside the container to read them.

### Showing Only the Last N Lines with --tail

When a container has been running for a long time, it may have thousands of log lines. You usually only care about the most recent ones.

```bash
docker logs --tail 10 my-web
```

This shows only the last 10 lines. You can change the number to whatever you need:

```bash
# Last 5 lines
docker logs --tail 5 my-web

# Last 100 lines
docker logs --tail 100 my-web

# Last 1 line
docker logs --tail 1 my-web
```

### Filtering by Time with --since

You can show logs from a specific time onward:

```bash
# Logs from the last 5 minutes
docker logs --since 5m my-web

# Logs from the last 1 hour
docker logs --since 1h my-web

# Logs from the last 30 seconds
docker logs --since 30s my-web

# Logs since a specific timestamp
docker logs --since "2024-01-15T10:30:00" my-web
```

The time units are:

- `s` for seconds
- `m` for minutes
- `h` for hours

You can also use `--until` to show logs up to a certain time:

```bash
# Logs between 1 hour ago and 30 minutes ago
docker logs --since 1h --until 30m my-web
```

### Following Logs in Real Time with -f

The `-f` flag (short for `--follow`) streams logs continuously, just like `tail -f` on Linux. New log lines appear as they happen.

```bash
docker logs -f my-web
```

Now open your browser and visit `http://localhost:8080` again. You will see new log lines appear immediately in your terminal.

To stop following, press `Ctrl+C`. This stops the log stream but does not stop the container.

### Combining Flags

You can combine flags for precise log viewing:

```bash
# Follow logs, starting from the last 5 lines
docker logs -f --tail 5 my-web

# Show last 20 lines from the past hour
docker logs --tail 20 --since 1h my-web
```

### Showing Timestamps with -t

Add timestamps to each log line:

```bash
docker logs -t my-web
```

**Output:**

```
2024-01-15T10:30:00.123456789Z 172.17.0.1 - - "GET / HTTP/1.1" 200 615
2024-01-15T10:30:01.234567890Z 172.17.0.1 - - "GET /favicon.ico HTTP/1.1" 404 153
```

The `Z` at the end means the timestamp is in UTC (Coordinated Universal Time).

Clean up:

```bash
docker rm -f my-web
```

---

## Getting Inside a Container with docker exec

Sometimes reading logs is not enough. You need to go inside the container to investigate — check files, test commands, or look at the environment. The `docker exec` command lets you run commands inside a running container.

### Opening a Shell

The most common use of `docker exec` is opening an interactive shell:

```bash
docker run -d --name my-web nginx
docker exec -it my-web bash
```

Let us break down the flags:

- `-i` (interactive): Keeps the input stream open so you can type commands.
- `-t` (terminal): Allocates a terminal so the output is formatted nicely.
- `my-web`: The name of the container.
- `bash`: The command to run (a Bash shell).

You are now inside the container. Your prompt changes to something like:

```
root@a1b2c3d4e5f6:/#
```

You can explore:

```bash
# See what is in the root directory
ls /

# Check the nginx configuration
cat /etc/nginx/nginx.conf

# See running processes
ps aux

# Check the hostname
hostname

# Check environment variables
env
```

Type `exit` to leave:

```bash
exit
```

### When bash Is Not Available

Some minimal container images do not include `bash`. In that case, use `sh` (the Bourne shell), which is almost always available:

```bash
docker exec -it my-web sh
```

If the container is based on Alpine Linux (a very small Linux distribution), `sh` is your only option because Alpine does not include `bash` by default.

### Running a Single Command

You do not need to open a full shell. You can run a single command and get the output:

```bash
# Check the nginx version
docker exec my-web nginx -v
```

**Output:**

```
nginx version: nginx/1.25.3
```

```bash
# List files in a directory
docker exec my-web ls /etc/nginx/

# Check the IP address
docker exec my-web hostname -i

# Read a specific file
docker exec my-web cat /etc/hostname
```

Notice that for single commands, we do not need `-it` because we are not typing interactively.

Clean up:

```bash
docker rm -f my-web
```

---

## Inspecting Containers with docker inspect

The `docker inspect` command gives you a detailed JSON document with everything Docker knows about a container. It is like reading a container's medical record — every detail is there.

### Basic Inspection

```bash
docker run -d --name my-web -p 8080:80 nginx
docker inspect my-web
```

This produces a large amount of JSON output. The most useful sections are:

- **NetworkSettings**: IP address, ports, networks
- **Mounts**: Volumes and bind mounts
- **Config.Env**: Environment variables
- **State**: Running, paused, exit code, error messages

### Finding Specific Information with --format

Instead of reading through pages of JSON, you can extract exactly what you need using the `--format` flag with Go template syntax.

#### Get the Container's IP Address

```bash
docker inspect --format '{{.NetworkSettings.IPAddress}}' my-web
```

**Output:**

```
172.17.0.2
```

#### Get the Container's Status

```bash
docker inspect --format '{{.State.Status}}' my-web
```

**Output:**

```
running
```

#### Get Environment Variables

```bash
docker inspect --format '{{.Config.Env}}' my-web
```

**Output:**

```
[PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin NGINX_VERSION=1.25.3 NJS_VERSION=0.8.2]
```

#### Get Mount Points

```bash
docker inspect --format '{{json .Mounts}}' my-web
```

**Output:**

```json
[]
```

An empty array means no volumes are mounted.

#### Get the Container's Restart Count

```bash
docker inspect --format '{{.RestartCount}}' my-web
```

**Output:**

```
0
```

#### Get the Port Mappings

```bash
docker inspect --format '{{json .NetworkSettings.Ports}}' my-web
```

**Output:**

```json
{"80/tcp":[{"HostIp":"0.0.0.0","HostPort":"8080"}]}
```

### Common docker inspect Queries Reference

```
┌──────────────────────────────────────┬─────────────────────────────────┐
│  What You Want                       │  Format String                  │
├──────────────────────────────────────┼─────────────────────────────────┤
│  IP Address                          │  {{.NetworkSettings.IPAddress}} │
│  Status                              │  {{.State.Status}}              │
│  Exit Code                           │  {{.State.ExitCode}}            │
│  Start Time                          │  {{.State.StartedAt}}           │
│  Image                               │  {{.Config.Image}}              │
│  Command                             │  {{.Config.Cmd}}                │
│  Environment Variables               │  {{.Config.Env}}                │
│  Mounted Volumes                     │  {{json .Mounts}}               │
│  Port Mappings                       │  {{json .NetworkSettings.Ports}}│
│  Restart Count                       │  {{.RestartCount}}              │
│  Container PID                       │  {{.State.Pid}}                 │
└──────────────────────────────────────┴─────────────────────────────────┘
```

Clean up:

```bash
docker rm -f my-web
```

---

## Health Checks in Dockerfiles

A **health check** is a command that Docker runs periodically to check if your application is working correctly. Think of it like a doctor regularly checking a patient's pulse. The container might be "running" (the process exists), but the application inside might have crashed, frozen, or become unresponsive.

### Why Health Checks Matter

Without a health check, Docker only knows if the main process is running. It does not know if the process is actually doing useful work. For example:

- A web server process might be running but returning errors for every request.
- A database might be running but not accepting connections.
- An API might be running but stuck in an infinite loop.

A health check tells Docker to periodically verify that the application is truly healthy.

### Adding a HEALTHCHECK to Your Dockerfile

```dockerfile
FROM nginx:latest

# Copy your website files
COPY ./html /usr/share/nginx/html

# Health check: curl the homepage every 30 seconds
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
```

Let us break down each part:

- `HEALTHCHECK`: The Dockerfile instruction that defines a health check.
- `--interval=30s`: Run the check every 30 seconds. Docker waits this long between checks.
- `--timeout=10s`: If the check takes longer than 10 seconds, consider it failed.
- `--start-period=5s`: Give the application 5 seconds to start up before beginning health checks. This prevents false failures during startup.
- `--retries=3`: The container is marked "unhealthy" after 3 consecutive failures. One failure alone does not mark it unhealthy.
- `CMD curl -f http://localhost/ || exit 1`: The actual check command. `curl -f` makes a request to the homepage. If it fails, exit with code 1 (unhealthy). If it succeeds, exit with code 0 (healthy).

### Health Check States

A container with a health check goes through these states:

```
┌───────────────────────────────────────────────────┐
│                                                    │
│   starting ──────> healthy ──────> unhealthy      │
│      │                │                │           │
│      │                │                │           │
│      │                └────────────────┘           │
│      │           (can recover back to healthy)     │
│      │                                             │
│   (during start-period,                            │
│    failures are ignored)                           │
│                                                    │
└───────────────────────────────────────────────────┘
```

- **starting**: The container just started and is within the start period. Health check failures are ignored.
- **healthy**: The health check is passing. The application is working correctly.
- **unhealthy**: The health check has failed the specified number of retries in a row. Something is wrong.

### Checking Health Status

You can see the health status in `docker ps`:

```bash
docker ps
```

**Output:**

```
CONTAINER ID   IMAGE     STATUS                    PORTS
a1b2c3d4e5f6   my-app    Up 2 minutes (healthy)    0.0.0.0:8080->80/tcp
```

Notice the `(healthy)` in the STATUS column.

You can also get detailed health information with `docker inspect`:

```bash
docker inspect --format '{{json .State.Health}}' my-app
```

**Output (formatted):**

```json
{
  "Status": "healthy",
  "FailingStreak": 0,
  "Log": [
    {
      "Start": "2024-01-15T10:30:00.123Z",
      "End": "2024-01-15T10:30:00.456Z",
      "ExitCode": 0,
      "Output": "..."
    }
  ]
}
```

### Health Check Examples for Different Applications

```dockerfile
# Node.js application
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# PostgreSQL database
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD pg_isready -U postgres || exit 1

# Redis
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD redis-cli ping || exit 1

# Simple check if a process is running
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD pgrep -x my-process || exit 1
```

---

## Monitoring Docker Events

The `docker events` command shows you a real-time stream of everything happening in Docker — containers starting, stopping, dying, networks being created, volumes being mounted, and more.

### Watching Events

```bash
docker events
```

Now open a second terminal and run:

```bash
docker run --name test-events nginx
```

Back in your first terminal, you will see events like:

```
2024-01-15T10:30:00.000 container create a1b2c3... (image=nginx, name=test-events)
2024-01-15T10:30:00.100 container attach a1b2c3... (image=nginx, name=test-events)
2024-01-15T10:30:00.200 network connect a1b2c3... (name=bridge, container=test-events)
2024-01-15T10:30:00.300 container start a1b2c3... (image=nginx, name=test-events)
```

Each event tells you:

- **When** it happened (timestamp)
- **What** happened (create, attach, connect, start)
- **Which** container was involved
- **Additional details** (image name, network name)

### Filtering Events

You can filter events to show only what you care about:

```bash
# Only container events
docker events --filter type=container

# Only events for a specific container
docker events --filter container=my-web

# Only specific event types
docker events --filter event=start
docker events --filter event=die

# Combine filters
docker events --filter type=container --filter event=die
```

### Viewing Past Events

By default, `docker events` shows events in real time. You can also look at past events:

```bash
# Events from the last 10 minutes
docker events --since 10m

# Events from a specific time
docker events --since "2024-01-15T10:00:00"
```

Press `Ctrl+C` to stop watching events.

---

## Common Issues and How to Fix Them

Here are the most frequent problems you will encounter with Docker containers and how to diagnose and fix each one.

### Issue 1: Port Conflict

**Symptom**: You get an error when starting a container with port mapping.

```
Error response from daemon: driver failed programming external connectivity:
Bind for 0.0.0.0:8080 failed: port is already allocated
```

**Cause**: Another container or application is already using that port on your host.

**Diagnosis**:

```bash
# Find what is using the port
# On macOS/Linux:
lsof -i :8080

# Or check which Docker container is using it:
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep 8080
```

**Fix**: Either stop the other container or use a different host port:

```bash
# Stop the conflicting container
docker rm -f other-container

# Or use a different port
docker run -d -p 8081:80 my-app
```

### Issue 2: Container Exits Immediately

**Symptom**: You start a container and it exits right away.

```bash
docker run -d --name my-app my-image
docker ps
# Container is not listed (not running)

docker ps -a
# Container shows "Exited (1) 2 seconds ago"
```

**Diagnosis**:

```bash
# Check the exit code
docker inspect --format '{{.State.ExitCode}}' my-app

# Read the logs for error messages
docker logs my-app
```

**Common exit codes**:

```
┌──────────────┬────────────────────────────────────┐
│  Exit Code   │  Meaning                           │
├──────────────┼────────────────────────────────────┤
│  0           │  Normal exit (application finished) │
│  1           │  General error                      │
│  2           │  Misuse of command                  │
│  126         │  Command not executable             │
│  127         │  Command not found                  │
│  137         │  Killed (OOM or docker kill)        │
│  139         │  Segmentation fault                 │
│  143         │  Terminated (docker stop)           │
└──────────────┴────────────────────────────────────┘
```

**Fix**: Read the logs to understand the error. Common causes include:

- Wrong command in the Dockerfile `CMD`
- Missing environment variables
- Missing files or dependencies
- Wrong working directory

### Issue 3: Missing Files Inside the Container

**Symptom**: Your application cannot find a file it needs.

```
Error: ENOENT: no such file or directory, open '/app/config.json'
```

**Diagnosis**:

```bash
# Go inside the container and check
docker exec -it my-app sh

# List the files in the app directory
ls -la /app/

# Check the current working directory
pwd
```

**Fix**:

- Make sure the `COPY` instruction in your Dockerfile includes the file.
- Check that the `WORKDIR` matches where your application expects files.
- Verify that the `.dockerignore` file is not excluding the file.

### Issue 4: Permission Denied

**Symptom**: Your application cannot read or write a file.

```
Error: EACCES: permission denied, open '/app/data/output.txt'
```

**Diagnosis**:

```bash
# Check file permissions
docker exec my-app ls -la /app/data/

# Check which user the container runs as
docker exec my-app whoami
docker exec my-app id
```

**Fix**: In your Dockerfile, make sure the files are owned by the right user:

```dockerfile
# Option 1: Change ownership
COPY --chown=node:node . /app

# Option 2: Change permissions
RUN chmod -R 755 /app/data
```

### Issue 5: OOM Killed (Out of Memory)

**Symptom**: The container suddenly stops and the exit code is 137.

**Diagnosis**:

```bash
# Check the exit code
docker inspect --format '{{.State.ExitCode}}' my-app
# Returns: 137

# Check if it was killed due to memory
docker inspect --format '{{.State.OOMKilled}}' my-app
# Returns: true
```

**Fix**: Either increase the memory limit or fix the memory leak in your application:

```bash
# Run with more memory (512MB limit)
docker run -d --memory=512m my-app

# Run with no memory limit (not recommended for production)
docker run -d my-app
```

### Issue 6: Cannot Connect to Database

**Symptom**: Your application cannot connect to the database container.

```
Error: connect ECONNREFUSED 127.0.0.1:5432
```

**Cause**: The application is trying to connect to `localhost` or `127.0.0.1`, which refers to the application container itself, not the database container.

**Fix**:

1. Make sure both containers are on the same Docker network.
2. Use the database container's name as the hostname, not `localhost`.

```bash
# Wrong: connecting to localhost
DATABASE_HOST=localhost

# Right: connecting to the container name
DATABASE_HOST=my-postgres
```

---

## Systematic Debugging Flowchart

When something goes wrong, follow this flowchart. It will guide you through the most effective debugging steps in the right order.

```
                    ┌──────────────────────┐
                    │  Container Problem?  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Is the container      │
                    │ running?              │
                    │ docker ps             │
                    └──────┬───────┬───────┘
                           │       │
                     Yes   │       │  No
                           │       │
              ┌────────────▼─┐  ┌──▼──────────────────┐
              │ Check logs   │  │ Check exited         │
              │ docker logs  │  │ container            │
              │ my-container │  │ docker ps -a         │
              └──────┬───────┘  └──────┬───────────────┘
                     │                  │
                     │           ┌──────▼───────────────┐
                     │           │ Read the logs         │
                     │           │ docker logs           │
                     │           │ my-container          │
                     │           └──────┬───────────────┘
                     │                  │
              ┌──────▼───────┐  ┌──────▼───────────────┐
              │ Can you      │  │ Check exit code       │
              │ reach the    │  │ docker inspect        │
              │ service?     │  │ --format              │
              │ curl/wget    │  │ '{{.State.ExitCode}}' │
              └──┬───────┬───┘  └──────┬───────────────┘
                 │       │              │
           Yes   │       │ No    ┌──────▼───────────────┐
                 │       │       │ Fix the issue:        │
        ┌────────▼──┐    │       │ - Code error (1)      │
        │ App works  │   │       │ - Missing cmd (127)   │
        │ Check for  │   │       │ - OOM killed (137)    │
        │ specific   │   │       │ - Permissions (126)   │
        │ errors in  │   │       └──────────────────────┘
        │ logs       │   │
        └────────────┘   │
                  ┌──────▼───────────────┐
                  │ Check:                │
                  │ 1. Port mapping (-p)  │
                  │ 2. Network settings   │
                  │ 3. Firewall rules     │
                  │ 4. App listening on   │
                  │    0.0.0.0 not        │
                  │    127.0.0.1          │
                  └──────────────────────┘
```

### Step-by-Step Debugging Process

Follow these steps in order when you encounter a problem:

**Step 1: Is the container running?**

```bash
docker ps
```

If your container is not in the list, it is not running. Check stopped containers:

```bash
docker ps -a
```

**Step 2: Read the logs**

```bash
docker logs my-container
docker logs --tail 50 my-container
```

Most problems will be explained in the logs. Read the error messages carefully.

**Step 3: Check the exit code (if the container stopped)**

```bash
docker inspect --format '{{.State.ExitCode}}' my-container
```

The exit code tells you what kind of failure occurred.

**Step 4: Go inside and investigate**

```bash
docker exec -it my-container sh
```

Check files, permissions, environment variables, and network connectivity from inside the container.

**Step 5: Check network settings**

```bash
# What network is the container on?
docker inspect --format '{{json .NetworkSettings.Networks}}' my-container

# Can the container reach other containers?
docker exec my-container ping -c 3 other-container
```

**Step 6: Check resource usage**

```bash
docker stats my-container
```

This shows real-time CPU, memory, and network usage. If memory usage is near the limit, the container might get OOM killed.

**Step 7: Watch events**

```bash
docker events --filter container=my-container
```

This shows what Docker is doing with your container in real time.

---

## Common Mistakes

### Mistake 1: Not Reading the Logs

Many beginners skip `docker logs` and go straight to trying random fixes. Always read the logs first. The answer is usually right there.

### Mistake 2: Using docker exec on a Stopped Container

```bash
# This will fail — the container must be running
docker exec -it my-stopped-container sh
```

**Error:**

```
Error response from daemon: Container ... is not running
```

If the container is stopped, you cannot exec into it. Instead, start it in a way that keeps it running:

```bash
# Start with an interactive shell to investigate
docker run -it my-image sh
```

### Mistake 3: Forgetting -it Flags

```bash
# This will not work interactively
docker exec my-container bash
```

Without `-it`, you cannot type commands. Always use `-it` for interactive sessions.

### Mistake 4: Ignoring Health Check Failures

If `docker ps` shows `(unhealthy)`, do not ignore it. Check the health check logs:

```bash
docker inspect --format '{{json .State.Health}}' my-container
```

### Mistake 5: Looking at the Wrong Container

When running multiple containers, make sure you are reading logs from the correct one. Use `docker ps` to list all running containers and their names.

---

## Best Practices

1. **Always check logs first**. The `docker logs` command should be your first step when debugging.

2. **Add health checks to every production Dockerfile**. They help orchestrators (like Docker Compose and Kubernetes) know when your application is truly ready.

3. **Use `--tail` and `--since` to filter logs**. Do not scroll through thousands of lines when you only need the recent ones.

4. **Write application logs to stdout/stderr**. This ensures `docker logs` captures them. Avoid writing to log files inside the container.

5. **Use meaningful container names**. `--name my-postgres` is much easier to debug than a random container ID.

6. **Monitor with `docker stats`** to keep an eye on resource usage before problems occur.

7. **Set restart policies** for production containers so they recover from crashes automatically:
   ```bash
   docker run -d --restart unless-stopped my-app
   ```

8. **Keep health check intervals reasonable**. Checking every second is too aggressive. Every 30 seconds is usually fine.

---

## Quick Summary

Docker provides powerful tools for debugging containers. Use `docker logs` to read application output, with `--tail`, `--since`, and `-f` to filter and follow logs. Use `docker exec -it` to get inside running containers and investigate. Use `docker inspect` to extract specific details like IP addresses, mounts, and environment variables. Add `HEALTHCHECK` instructions to your Dockerfiles so Docker can monitor your application's actual health. Use `docker events` to see what Docker is doing in real time. When problems occur, follow the debugging flowchart: check if the container is running, read the logs, check the exit code, investigate from inside, check network and resources.

---

## Key Points

- `docker logs` shows stdout and stderr output from a container.
- `--tail N` shows the last N lines, `--since` filters by time, `-f` follows in real time.
- `docker exec -it container sh` opens a shell inside a running container.
- `docker inspect` returns detailed JSON about a container; use `--format` to extract specific fields.
- `HEALTHCHECK` in a Dockerfile lets Docker monitor if your application is truly working.
- Health check states are: starting, healthy, and unhealthy.
- `docker events` shows a real-time stream of all Docker activity.
- Common issues include port conflicts, immediate exits, missing files, permission denied, and OOM kills.
- Exit code 137 usually means the container was killed due to memory limits.
- Always check logs first when debugging; the answer is usually there.

---

## Practice Questions

1. Your container shows "Exited (137)" in `docker ps -a`. What does exit code 137 mean, and how would you investigate further?

2. What is the difference between `docker logs my-container` and `docker logs -f my-container`? When would you use each one?

3. Why does Docker recommend that applications write logs to stdout/stderr instead of log files? What happens if an application writes to a log file inside the container?

4. Explain what each part of this HEALTHCHECK instruction does:
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
     CMD curl -f http://localhost:3000/health || exit 1
   ```

5. You start a container and it exits immediately. Walk through the steps you would take to diagnose the problem.

---

## Exercises

### Exercise 1: Log Investigation

1. Run an nginx container named `log-test` with port 8080 mapped to port 80.
2. Visit `http://localhost:8080` in your browser 5 times.
3. View only the last 3 log lines.
4. View logs from the last 2 minutes.
5. Follow the logs in real time and visit the page again to see new entries appear.
6. Clean up.

### Exercise 2: Container Inspection

1. Run a PostgreSQL container named `inspect-test` with environment variables for user, password, and database.
2. Use `docker inspect` with `--format` to find the container's IP address.
3. Use `docker inspect` to find the environment variables.
4. Use `docker exec` to go inside the container and verify the database was created.
5. Clean up.

### Exercise 3: Health Check Debugging

1. Create a Dockerfile based on nginx that includes a HEALTHCHECK which curls localhost.
2. Build and run the container.
3. Wait 30 seconds and check the health status using `docker ps` and `docker inspect`.
4. Now create another Dockerfile with a health check that will fail (for example, curl a port that is not listening).
5. Build and run it, then observe the health status change to unhealthy.
6. Check the health check log using `docker inspect`.
7. Clean up.

---

## What Is Next?

You can now debug individual containers like a pro. But real applications have multiple containers — a web server, an API, a database, maybe a cache. Managing all of these separately with `docker run` commands is tedious and error-prone. In the next chapter, you will learn about Docker Compose, a tool that lets you define and run multi-container applications with a single file and a single command.
