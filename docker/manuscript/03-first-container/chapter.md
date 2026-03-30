# Chapter 3: Your First Real Container

## What You Will Learn

- How to run a real web server in a container (Nginx)
- How to run containers in the background (detached mode)
- How to map ports so you can access containers from your browser
- How to list, stop, and remove containers
- How to run interactive containers (like a Linux shell)
- How to name your containers
- How to start and restart stopped containers

## Why This Chapter Matters

In Chapter 2, you ran `hello-world`. It printed a message and stopped. That was a test.

Now it is time to do something real. You are going to run a web server inside a container. You will open it in your browser. You will control it -- start it, stop it, remove it. These are the commands you will use every single day when working with Docker.

Think of this chapter as your first driving lesson. You are going to start the car, drive around the block, park, and turn off the engine. Simple, but essential.

---

## Running a Web Server with Nginx

Nginx (pronounced "engine-x") is one of the most popular web servers in the world. Let us run it in a container.

### The Basic Run

```bash
docker run nginx
```

**Expected output:**

```
Unable to find image 'nginx:latest' locally
latest: Pulling from library/nginx
2d429b9e73a6: Pull complete
20c8b3871098: Pull complete
06da587a7970: Pull complete
...
Digest: sha256:56b388b0d79c738f4cf...
Status: Downloaded newer image for nginx:latest
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to
perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
...
2024/01/15 10:30:00 [notice] 1#1: start worker process 36
```

**What happened:**

1. Docker could not find the Nginx image on your computer.
2. Docker downloaded it from Docker Hub.
3. Docker created a container from the image.
4. Docker started the container.
5. Nginx started running inside the container.

**But there is a problem.** Your terminal is stuck. It is showing Nginx log messages. You cannot type anything else. The container is running in the **foreground**.

Press `Ctrl + C` to stop the container and get your terminal back.

---

## Detached Mode: Running in the Background

You do not want your terminal to be taken over by a container. You want containers to run in the background, like background music. This is called **detached mode**.

```bash
docker run -d nginx
```

**Expected output:**

```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0
```

**Line-by-line explanation:**
- `docker run` -- Create and start a container
- `-d` -- Run in **detached** mode (in the background)
- `nginx` -- The image to use
- The long string is the **container ID**. It is a unique identifier for this container. Think of it like a license plate for your container.

Your terminal is free. The container is running in the background. But how do you see it in your browser?

---

## Port Mapping: Connecting the Outside World to Your Container

Right now, Nginx is running inside the container. But the container is isolated. It is like a room with no door. The web server is running, but nothing outside the container can reach it.

You need to **map a port**. A port is like a door number. Web servers listen on port 80. You need to connect a port on your computer to port 80 inside the container.

```bash
docker run -d -p 8080:80 nginx
```

**Expected output:**

```
f4e3d2c1b0a9876543210fedcba9876543210fedcba9876543210fedcba987654
```

**Line-by-line explanation:**
- `-p 8080:80` -- Map port 8080 on your computer to port 80 in the container
- The format is `-p HOST_PORT:CONTAINER_PORT`
- `8080` is the port on YOUR computer (the host)
- `80` is the port INSIDE the container (where Nginx listens)

```
Your Computer (Host)                    Container
+-------------------+                  +-------------------+
|                   |   port mapping   |                   |
|  Port 8080  ------+------------------+------  Port 80    |
|                   |                  |                   |
|  Browser visits   |                  |   Nginx listens   |
|  localhost:8080   |                  |   on port 80      |
+-------------------+                  +-------------------+
```

Now open your web browser and go to:

```
http://localhost:8080
```

You should see the Nginx welcome page! It says "Welcome to nginx!" This web page is being served from inside your Docker container.

### Why Not Use Port 80 on Both Sides?

You could. This works:

```bash
docker run -d -p 80:80 nginx
```

Then you would visit `http://localhost` (port 80 is the default for web browsers). But port 80 might already be used by another application on your computer. Using 8080 avoids conflicts.

### Running Multiple Containers on Different Ports

You can run multiple Nginx containers at the same time, each on a different port:

```bash
docker run -d -p 8081:80 nginx
docker run -d -p 8082:80 nginx
```

Now you have three web servers running:
- `http://localhost:8080` -- First Nginx
- `http://localhost:8081` -- Second Nginx
- `http://localhost:8082` -- Third Nginx

Each container is independent. They do not know about each other.

```
Your Computer
+------------------------------------------+
|                                          |
|  Port 8080 ----> Container 1 (Nginx)     |
|  Port 8081 ----> Container 2 (Nginx)     |
|  Port 8082 ----> Container 3 (Nginx)     |
|                                          |
+------------------------------------------+
```

---

## Listing Containers: docker ps

How do you see which containers are running? Use `docker ps`.

```bash
docker ps
```

**Expected output:**

```
CONTAINER ID   IMAGE   COMMAND                  CREATED         STATUS         PORTS                  NAMES
f4e3d2c1b0a9   nginx   "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes   0.0.0.0:8080->80/tcp   eager_pike
a1b2c3d4e5f6   nginx   "/docker-entrypoint.…"   5 minutes ago   Up 5 minutes   80/tcp                 zen_hopper
```

**Column explanations:**

| Column | Meaning |
|---|---|
| `CONTAINER ID` | The first 12 characters of the full container ID |
| `IMAGE` | The image the container was created from |
| `COMMAND` | The command running inside the container |
| `CREATED` | When the container was created |
| `STATUS` | Whether it is running and for how long |
| `PORTS` | Port mappings (host -> container) |
| `NAMES` | A random name Docker assigned |

Notice the `NAMES` column. Docker gives each container a random name like `eager_pike` or `zen_hopper`. These names are fun, but not very useful. We will learn to give our own names soon.

### Seeing All Containers (Including Stopped Ones)

`docker ps` only shows running containers. To see ALL containers, including stopped ones:

```bash
docker ps -a
```

**Expected output:**

```
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS                      PORTS                  NAMES
f4e3d2c1b0a9   nginx         "/docker-entrypoint.…"   5 minutes ago    Up 5 minutes                0.0.0.0:8080->80/tcp   eager_pike
a1b2c3d4e5f6   nginx         "/docker-entrypoint.…"   8 minutes ago    Up 8 minutes                80/tcp                 zen_hopper
b3c4d5e6f7g8   hello-world   "/hello"                 20 minutes ago   Exited (0) 20 minutes ago                          happy_morse
```

**What `-a` means:** The `-a` flag stands for "all." It shows every container, including ones that have stopped. The `hello-world` container from Chapter 2 is here too. Its status is "Exited (0)," which means it finished running successfully (exit code 0 means success).

---

## Stopping Containers: docker stop

To stop a running container, use `docker stop` followed by the container ID or name.

```bash
docker stop f4e3d2c1b0a9
```

**Expected output:**

```
f4e3d2c1b0a9
```

Docker prints the container ID to confirm it was stopped.

**What this does:** Sends a polite "please stop" signal to the container. The container has 10 seconds to shut down gracefully. If it does not stop in time, Docker forces it to stop.

You can also use the container name:

```bash
docker stop eager_pike
```

You do not need to type the full container ID. The first few characters are enough, as long as they are unique:

```bash
docker stop f4e
```

**Tip:** If `f4e` matches only one container, Docker knows which one you mean. If it matches multiple containers, Docker will tell you it is ambiguous.

### Verify the Container Stopped

```bash
docker ps
```

The stopped container should no longer appear in the list. Use `docker ps -a` to see it with a status of "Exited."

---

## Removing Containers: docker rm

Stopping a container does not delete it. It is like turning off a car. The car still exists. You can start it again later.

To actually delete a container:

```bash
docker rm f4e3d2c1b0a9
```

**Expected output:**

```
f4e3d2c1b0a9
```

**What this does:** Permanently deletes the container. It is gone. You cannot start it again.

**Important:** You can only remove stopped containers. If you try to remove a running container, Docker will refuse:

```bash
docker rm eager_pike
```

**Error output:**

```
Error response from daemon: You cannot remove a running container f4e3d2c1b0a9.
Stop the container before attempting removal or force remove.
```

### Force Remove a Running Container

If you want to stop AND remove in one step:

```bash
docker rm -f eager_pike
```

The `-f` flag means **force**. It stops the container immediately and then removes it.

### Remove All Stopped Containers

Over time, you will have many stopped containers. Clean them all up at once:

```bash
docker container prune
```

**Expected output:**

```
WARNING! This will remove all stopped containers.
Are you sure you want to continue? [y/N] y
Deleted Containers:
b3c4d5e6f7g8
a1b2c3d4e5f6

Total reclaimed space: 5.12kB
```

---

## Stop and Remove: A Quick Workflow

Here is a common workflow you will use constantly:

```bash
# 1. Run a container in the background with port mapping
docker run -d -p 8080:80 nginx

# 2. Check that it is running
docker ps

# 3. Visit http://localhost:8080 in your browser

# 4. When you are done, stop the container
docker stop <container_id>

# 5. Remove the container
docker rm <container_id>
```

Or do steps 4 and 5 together:

```bash
docker rm -f <container_id>
```

There is also a handy flag to automatically remove a container when it stops:

```bash
docker run -d -p 8080:80 --rm nginx
```

The `--rm` flag tells Docker: "When this container stops, delete it automatically." This is great for temporary containers.

---

## Interactive Containers: docker run -it

Not every container runs a web server. Sometimes you want to go INSIDE a container and look around. This is called running an **interactive** container.

```bash
docker run -it alpine sh
```

**Expected output:**

```
Unable to find image 'alpine:latest' locally
latest: Pulling from library/alpine
4abcf2066143: Pull complete
Digest: sha256:c5b1261d6d3e43071626931fc004f70149baeba2c8ec672bd4f27761f8e1ad6b
Status: Downloaded newer image for alpine:latest
/ #
```

**Line-by-line explanation:**
- `docker run` -- Create and start a container
- `-i` -- **Interactive** mode. Keep the input stream open so you can type commands.
- `-t` -- **TTY** mode. Give you a terminal with a command prompt.
- `-it` -- The two flags combined. Almost always used together.
- `alpine` -- A very small Linux distribution (about 7 MB). Perfect for experimenting.
- `sh` -- The command to run inside the container. `sh` is a shell (a command-line interface).

You are now INSIDE the container! The `/ #` prompt means you are the root user inside the Alpine Linux container.

### Explore Inside the Container

Try some commands:

```bash
/ # ls
bin    dev    etc    home   lib    media  mnt    opt    proc   root   run
sbin   srv    sys    tmp    usr    var
```

This is the file system inside the container. It is a tiny Linux system.

```bash
/ # cat /etc/os-release
NAME="Alpine Linux"
ID=alpine
VERSION_ID=3.19.0
PRETTY_NAME="Alpine Linux v3.19"
```

You are running Alpine Linux inside a container. Your host computer could be Mac, Windows, or any Linux distribution. The container has its own operating system.

```bash
/ # echo "Hello from inside a container!"
Hello from inside a container!
```

```bash
/ # whoami
root
```

You are the root user (administrator) inside this container. But this does not give you root access to your host computer. The container is isolated.

### Exit the Container

Type `exit` to leave the container:

```bash
/ # exit
```

You are back to your regular terminal. The container has stopped because the shell (`sh`) was the main process, and when it ended, the container stopped too.

### Interactive Containers with Other Images

You can run interactive sessions with any image. Here is Ubuntu:

```bash
docker run -it ubuntu bash
```

**Expected output:**

```
root@a1b2c3d4e5f6:/#
```

Now you have a full Ubuntu Linux environment. You can install software, run scripts, and experiment without affecting your host computer:

```bash
root@a1b2c3d4e5f6:/# apt-get update
root@a1b2c3d4e5f6:/# apt-get install -y curl
root@a1b2c3d4e5f6:/# curl --version
curl 8.5.0 (x86_64-pc-linux-gnu)...
```

Type `exit` to leave.

**Important:** Anything you install inside a container is lost when the container is removed. Containers are **ephemeral** (temporary by design). We will learn how to persist data in a later chapter.

---

## Naming Your Containers: --name

Docker gives random names to containers. Names like `eager_pike` and `zen_hopper` are hard to remember. You can choose your own name.

```bash
docker run -d -p 8080:80 --name my-web-server nginx
```

**Expected output:**

```
c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8
```

Now check the container:

```bash
docker ps
```

**Expected output:**

```
CONTAINER ID   IMAGE   COMMAND                  CREATED         STATUS         PORTS                  NAMES
c9d8e7f6a5b4   nginx   "/docker-entrypoint.…"   5 seconds ago   Up 4 seconds   0.0.0.0:8080->80/tcp   my-web-server
```

The `NAMES` column now shows `my-web-server`. Much easier to remember.

You can use this name everywhere you would use a container ID:

```bash
docker stop my-web-server
docker start my-web-server
docker rm my-web-server
```

### Naming Rules

- Names must be unique. You cannot have two containers with the same name.
- Names can contain letters, numbers, hyphens, and underscores.
- Names cannot start with a hyphen.
- If you try to create a container with a name that already exists, Docker will refuse.

```bash
docker run -d --name my-app nginx
docker run -d --name my-app nginx
```

**Error output:**

```
docker: Error response from daemon: Conflict. The container name "/my-app"
is already in use by container "c9d8e7f6a5b4". You have to remove (or rename)
that container to be able to reuse that name.
```

To fix this, remove the old container first:

```bash
docker rm -f my-app
docker run -d --name my-app nginx
```

---

## Starting and Restarting Containers

When you stop a container, it is not deleted. It still exists. You can start it again.

### Starting a Stopped Container

```bash
# First, stop a container
docker stop my-web-server

# Check that it is stopped
docker ps -a
```

**Expected output:**

```
CONTAINER ID   IMAGE   COMMAND                  CREATED         STATUS                     PORTS   NAMES
c9d8e7f6a5b4   nginx   "/docker-entrypoint.…"   10 minutes ago  Exited (0) 5 seconds ago           my-web-server
```

Now start it again:

```bash
docker start my-web-server
```

**Expected output:**

```
my-web-server
```

The container is running again with the same settings (same ports, same name).

### Restarting a Container

`docker restart` stops and starts a container in one command:

```bash
docker restart my-web-server
```

**Expected output:**

```
my-web-server
```

This is useful when a container is misbehaving and you want to give it a fresh start without reconfiguring everything.

### The Difference Between run, start, and restart

| Command | What It Does |
|---|---|
| `docker run` | Creates a NEW container from an image and starts it |
| `docker start` | Starts an EXISTING stopped container |
| `docker restart` | Stops and starts an EXISTING container |

This is a common point of confusion. `docker run` always creates a new container. If you want to start an existing one, use `docker start`.

```
docker run = Create + Start (new container)
docker start = Start (existing container)
docker restart = Stop + Start (existing container)
```

---

## Viewing Container Logs

When a container runs in the background, you might want to see what it is doing. Use `docker logs`.

```bash
docker logs my-web-server
```

**Expected output:**

```
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to
perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
...
2024/01/15 10:30:00 [notice] 1#1: start worker processes
2024/01/15 10:30:00 [notice] 1#1: start worker process 29
```

### Follow Logs in Real Time

```bash
docker logs -f my-web-server
```

The `-f` flag means **follow**. It shows new log entries as they appear, like `tail -f` on Linux. Press `Ctrl + C` to stop following.

### Show Only the Last Few Lines

```bash
docker logs --tail 5 my-web-server
```

This shows only the last 5 lines. Useful when a container has been running for a long time and has thousands of log lines.

---

## A Real-World Example: Python Web App

Let us run a Python application in a container. Docker Hub has a simple Python HTTP server we can use.

```bash
docker run -d -p 9000:8000 --name python-app python:3.12-slim \
  python -m http.server 8000
```

**Line-by-line explanation:**
- `-d` -- Run in the background
- `-p 9000:8000` -- Map your port 9000 to the container's port 8000
- `--name python-app` -- Name it `python-app`
- `python:3.12-slim` -- Use the Python 3.12 image (slim version, which is smaller)
- `python -m http.server 8000` -- The command to run inside the container. This starts Python's built-in web server on port 8000.

Now visit `http://localhost:9000` in your browser. You will see a directory listing. This is Python's simple HTTP server running inside a container.

To clean up:

```bash
docker rm -f python-app
```

---

## A Real-World Example: Node.js

Let us run a quick Node.js example too:

```bash
docker run -d -p 3000:3000 --name node-app node:20-slim \
  sh -c "echo 'const http = require(\"http\"); http.createServer((req, res) => { res.end(\"Hello from Node.js in Docker!\"); }).listen(3000);' | node"
```

**What this does:** Creates a tiny Node.js web server that responds with "Hello from Node.js in Docker!" on port 3000.

Visit `http://localhost:3000` in your browser to see the message.

To clean up:

```bash
docker rm -f node-app
```

---

## Container Lifecycle Diagram

Here is the complete lifecycle of a container:

```
                    docker run
                        |
                        v
                  +-----------+
                  |  CREATED  |
                  +-----------+
                        |
                        | (auto-starts)
                        v
                  +-----------+          docker stop
                  |  RUNNING  | -----------------------> +-----------+
                  +-----------+                          |  STOPPED  |
                        ^                                +-----------+
                        |                                      |
                        | docker start                         |
                        | docker restart                       |
                        +--------------------------------------+
                                                               |
                                                               | docker rm
                                                               v
                                                         +-----------+
                                                         |  REMOVED  |
                                                         +-----------+
                                                         (gone forever)
```

---

## Command Reference

Here is a summary of every command from this chapter:

| Command | What It Does |
|---|---|
| `docker run IMAGE` | Create and start a container |
| `docker run -d IMAGE` | Run in background (detached) |
| `docker run -p HOST:CONTAINER IMAGE` | Map ports |
| `docker run -it IMAGE COMMAND` | Run interactively |
| `docker run --name NAME IMAGE` | Give the container a name |
| `docker run --rm IMAGE` | Auto-remove when stopped |
| `docker ps` | List running containers |
| `docker ps -a` | List ALL containers |
| `docker stop CONTAINER` | Stop a container |
| `docker start CONTAINER` | Start a stopped container |
| `docker restart CONTAINER` | Restart a container |
| `docker rm CONTAINER` | Remove a stopped container |
| `docker rm -f CONTAINER` | Force remove (even if running) |
| `docker logs CONTAINER` | View container logs |
| `docker logs -f CONTAINER` | Follow logs in real time |
| `docker container prune` | Remove all stopped containers |

---

## Common Mistakes

1. **Forgetting the `-d` flag.** Running `docker run nginx` without `-d` will lock your terminal. Always use `-d` for long-running containers like web servers.

2. **Getting the port order wrong.** It is `-p HOST:CONTAINER`, not `-p CONTAINER:HOST`. The host port comes first. Remember: "Outside:Inside."

3. **Using `docker run` instead of `docker start`.** `docker run` creates a NEW container every time. If you already have a stopped container, use `docker start` to restart it.

4. **Forgetting to remove old containers.** Stopped containers take up disk space. Use `docker ps -a` to see them and `docker container prune` to clean them up.

5. **Port conflicts.** If port 8080 is already in use, Docker will show an error. Choose a different port. Common alternatives: 8081, 8082, 9000, 3000.

---

## Best Practices

1. **Always name your containers.** Use `--name` so you can easily reference them. Names like `my-web-server` are much better than `eager_pike`.

2. **Use `--rm` for temporary containers.** If you are just experimenting, use `--rm` so the container is automatically deleted when it stops.

3. **Use `-d` for servers.** Web servers, databases, and other long-running services should run in detached mode.

4. **Use `-it` for exploration.** When you want to explore an image or debug something, use interactive mode with a shell.

5. **Clean up regularly.** Run `docker ps -a` to see stopped containers. Run `docker container prune` to remove them.

---

## Quick Summary

You can run containers in the foreground or background (detached mode with `-d`). Port mapping (`-p HOST:CONTAINER`) lets your browser connect to services inside containers. `docker ps` lists running containers. `docker stop` and `docker rm` control the container lifecycle. Interactive containers (`-it`) let you explore and run commands inside a container. Naming containers (`--name`) makes them easier to manage.

---

## Key Points

- `docker run -d` runs a container in the background so your terminal stays free.
- `-p 8080:80` maps port 8080 on your computer to port 80 inside the container.
- `docker ps` shows running containers. `docker ps -a` shows all containers.
- `docker stop` gracefully stops a container. `docker rm` deletes it.
- `docker run -it alpine sh` gives you an interactive shell inside a container.
- `--name` lets you give a container a human-readable name.
- `docker start` restarts a stopped container. `docker run` creates a new one.
- `--rm` automatically removes a container when it stops.
- Containers are ephemeral. Anything installed inside a container is lost when it is removed.

---

## Practice Questions

1. What is the difference between running a container with and without the `-d` flag?

2. You run `docker run -d -p 3000:80 nginx`. What URL would you visit in your browser to see the Nginx welcome page?

3. What is the difference between `docker stop` and `docker rm`? Can you remove a running container?

4. You run `docker run -it ubuntu bash` and install Python inside the container. You type `exit`, then `docker start` the container. Is Python still installed? What if you `docker rm` the container and `docker run` a new one?

5. Why would you use the `--name` flag when running a container?

---

## Exercises

### Exercise 1: Web Server Challenge

1. Run an Nginx container in the background on port 9090.
2. Give it the name `exercise-web`.
3. Verify it is running with `docker ps`.
4. Visit it in your browser.
5. View its logs.
6. Stop it.
7. Start it again (do not use `docker run`).
8. Finally, remove it.

Write down every command you used.

### Exercise 2: Multiple Containers

1. Run three Nginx containers in the background on ports 8001, 8002, and 8003.
2. Name them `web-1`, `web-2`, and `web-3`.
3. Use `docker ps` to verify all three are running.
4. Stop only `web-2`.
5. Use `docker ps` and `docker ps -a` to see the difference.
6. Remove all three containers.

### Exercise 3: Interactive Exploration

1. Run an interactive Alpine container with `docker run -it alpine sh`.
2. Inside the container, run `uname -a` to see the operating system information.
3. Run `ls /` to see the root file system.
4. Create a file: `echo "I was here" > /tmp/myfile.txt`
5. Verify the file exists: `cat /tmp/myfile.txt`
6. Exit the container.
7. Start a NEW Alpine container with `docker run -it alpine sh`.
8. Check if `/tmp/myfile.txt` exists. Why or why not?

---

## What Is Next?

You can now run, stop, and manage containers. But how do containers actually work? What happens behind the scenes? In the next chapter, we will look under the hood and understand images, layers, namespaces, and cgroups -- the technology that makes containers possible.
