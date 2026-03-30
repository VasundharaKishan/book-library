# Chapter 4: How Containers Work

## What You Will Learn

- The difference between images and containers (with multiple analogies)
- How image layers work and why they matter
- What a union filesystem is (simplified)
- How namespaces provide isolation
- How cgroups limit resources
- Why containers start faster and use fewer resources than virtual machines

## Why This Chapter Matters

In the previous chapters, you ran containers. You started them, stopped them, and removed them. But you treated Docker like a black box. You typed commands and things happened.

Now it is time to open the box and look inside.

Understanding how containers work will help you:
- Debug problems when things go wrong
- Make better decisions about how to build and run containers
- Have intelligent conversations with your team about container architecture
- Understand why certain Docker commands exist

You do not need to be a kernel engineer to understand this chapter. We will use simple analogies and clear diagrams. Let us look under the hood.

---

## Images vs Containers

This is the most important concept in Docker. If you understand this, everything else becomes easier.

### Analogy 1: Recipe vs Cake

An **image** is like a recipe. A **container** is like a cake made from that recipe.

- The recipe (image) describes what ingredients to use and how to combine them.
- The cake (container) is the actual thing you eat.
- You can make many cakes from one recipe.
- Each cake is independent. Eating one cake does not affect the others.
- The recipe itself never changes when you bake a cake.

```
      Image (Recipe)                    Containers (Cakes)
+--------------------+          +--------+  +--------+  +--------+
| - Python 3.12      |   run   |  Cake  |  |  Cake  |  |  Cake  |
| - Flask library    | ------> |   1    |  |   2    |  |   3    |
| - Your app code    |   run   |        |  |        |  |        |
| - Config files     | ------> | Running|  |Running |  |Stopped |
+--------------------+   run   +--------+  +--------+  +--------+
                        ------>
  One image.                     Many containers.
  Never changes.                 Each is independent.
```

### Analogy 2: Class vs Object

If you know programming, this analogy will click immediately.

An **image** is like a class in object-oriented programming. A **container** is like an object (an instance of that class).

```python
# The Image (like a class definition)
class WebServer:
    python_version = "3.12"
    framework = "Flask"
    code = "app.py"

# Containers (like objects created from the class)
server_1 = WebServer()   # docker run my-app
server_2 = WebServer()   # docker run my-app
server_3 = WebServer()   # docker run my-app
```

```java
// In Java terms:
// Image = the .class file (blueprint)
// Container = the object in memory (instance)

WebServer server1 = new WebServer();  // docker run my-app
WebServer server2 = new WebServer();  // docker run my-app
```

Each container has its own state. Changing one container does not affect the others, just like changing one object does not affect other objects of the same class.

### Analogy 3: Stamp vs Impression

An image is like a rubber stamp. A container is like the impression the stamp makes on paper.

- One stamp can make many impressions.
- Each impression is on a different piece of paper.
- Changing one impression does not change the stamp.
- The stamp itself remains the same.

### The Technical Reality

An **image** is a read-only template. It contains:
- An operating system (usually a minimal Linux distribution)
- Your application code
- All libraries and dependencies
- Configuration files
- Instructions for how to start the application

A **container** is a running (or stopped) instance of an image. It contains:
- Everything from the image (read-only)
- A thin writable layer on top (for any changes)
- Its own process space
- Its own network interface
- Its own file system view

```
Container
+-----------------------------------+
|  Writable Layer (your changes)    |  <-- Only in the container
+-----------------------------------+
|  Image Layer 3 (app code)         |  <-- Read-only, from image
+-----------------------------------+
|  Image Layer 2 (libraries)        |  <-- Read-only, from image
+-----------------------------------+
|  Image Layer 1 (base OS)          |  <-- Read-only, from image
+-----------------------------------+
```

---

## Image Layers: Building Blocks

Docker images are not single, monolithic files. They are made of **layers**, stacked on top of each other. This is one of Docker's most clever design decisions.

### What Is a Layer?

A layer is a set of file system changes. Think of it like a transparent sheet of paper.

Imagine you are creating a picture using transparent overlays:

1. **Layer 1:** Draw the background (a blue sky). This is the base operating system.
2. **Layer 2:** Add some trees. These are the libraries your app needs.
3. **Layer 3:** Add a house. This is your application code.

When you stack them together, you see the complete picture.

```
Layer 3: App Code          +-----+
                           |house|
Layer 2: Libraries    +---+|     |+---+
                      |tree||     ||tree|
Layer 1: Base OS   ===+===++=====++===+=====
                      blue sky background

Stacked together: A complete scene
```

### How Layers Work in Docker

When you build a Docker image, each instruction creates a new layer:

```
Instruction 1: Start with Ubuntu          -> Layer 1 (Ubuntu base, ~75 MB)
Instruction 2: Install Python             -> Layer 2 (Python files, ~50 MB)
Instruction 3: Install Flask library      -> Layer 3 (Flask files, ~5 MB)
Instruction 4: Copy your application code -> Layer 4 (Your code, ~1 MB)
```

```
+---------------------------------------+
|  Layer 4: Your app code (1 MB)        |
+---------------------------------------+
|  Layer 3: Flask library (5 MB)        |
+---------------------------------------+
|  Layer 2: Python (50 MB)              |
+---------------------------------------+
|  Layer 1: Ubuntu base (75 MB)         |
+---------------------------------------+
Total image size: ~131 MB
```

### Why Layers Matter: Sharing and Caching

Here is the brilliant part. Layers are **shared** between images.

Suppose you have two applications:
- App A uses Python 3.12 + Flask
- App B uses Python 3.12 + Django

Both apps need Python 3.12. Docker does not store Python twice. Both images share the same Python layer.

```
App A Image              App B Image
+----------------+      +----------------+
| Flask + App A  |      | Django + App B |
+----------------+      +----------------+
|   Python 3.12  | <--- SHARED ---> |   Python 3.12  |
+----------------+      +----------------+
|   Ubuntu base  | <--- SHARED ---> |   Ubuntu base  |
+----------------+      +----------------+

Without sharing: 131 MB + 135 MB = 266 MB
With sharing:    131 MB + 9 MB   = 140 MB (Python & Ubuntu stored once)
```

This saves enormous amounts of disk space. If you have 10 Python applications, the Python layer is stored only once.

Layers also make **downloads faster**. If you already have the Python layer and you download a new image that uses Python, Docker skips the Python layer. It only downloads the layers you do not have.

```bash
# Downloading App A (first time, everything is new)
Pulling from library/app-a
a1b2c3: Pull complete    # Ubuntu layer
d4e5f6: Pull complete    # Python layer
g7h8i9: Pull complete    # Flask layer
j0k1l2: Pull complete    # App A code

# Downloading App B (shares layers with App A)
Pulling from library/app-b
a1b2c3: Already exists   # Ubuntu layer (already have it!)
d4e5f6: Already exists   # Python layer (already have it!)
m3n4o5: Pull complete    # Django layer (new)
p6q7r8: Pull complete    # App B code (new)
```

---

## Union Filesystem: Seeing Layers as One

You might wonder: if an image is made of multiple layers, how does the container see one file system?

The answer is a **union filesystem** (also called an overlay filesystem).

A union filesystem takes multiple layers and presents them as a single, unified view. It is like stacking transparent sheets. You see through all the layers at once, and the result looks like one picture.

### How It Works

```
What Docker stores:              What the container sees:
(separate layers)                (one unified view)

Layer 3: /app/server.py          /
Layer 2: /usr/bin/python         ├── app/
Layer 1: /bin/sh, /etc/...       │   └── server.py
                                 ├── usr/
         UNION FILESYSTEM        │   └── bin/
              ------>            │       └── python
                                 ├── bin/
                                 │   └── sh
                                 └── etc/
                                     └── ...
```

The container does not know about layers. It sees a normal file system. You can `ls`, `cd`, `cat`, and use any command as if everything is in one place.

### The Writable Layer

When a container modifies a file, the change goes into a thin **writable layer** on top. The original image layers are never changed.

This is called **copy-on-write**. When a container needs to change a file from an image layer, Docker copies that file into the writable layer first. Then the container modifies the copy.

```
Container's View:

+-----------------------------------+
|  Writable Layer                   |  <-- Changes go here
|  (modified /etc/config.txt)       |
+-----------------------------------+
|  Image Layer 3 (app code)         |  <-- Read-only
+-----------------------------------+
|  Image Layer 2 (libraries)        |  <-- Read-only
+-----------------------------------+
|  Image Layer 1 (base OS)          |  <-- Read-only
|  (original /etc/config.txt)       |
+-----------------------------------+

When the container reads /etc/config.txt, it gets the MODIFIED
version from the writable layer (the top layer wins).
```

**Important consequence:** When you delete a container, its writable layer is deleted too. Any changes you made inside the container are gone. This is why containers are called **ephemeral** (temporary).

---

## Namespaces: Isolation Rooms

Containers feel like separate machines. Each container has its own processes, its own network, its own file system. But they all run on the same physical computer with the same kernel.

How? The answer is **namespaces**.

### What Is a Namespace?

A namespace is a Linux kernel feature that creates an isolated view of a system resource. Think of it as a one-way mirror.

Imagine a building with many offices. Each office has a window. But the windows are one-way mirrors. You can see your own office clearly. You cannot see into other offices. And you do not even know other offices exist.

That is what namespaces do for containers.

### Types of Namespaces

Docker uses several types of namespaces:

#### 1. PID Namespace (Process Isolation)

Each container has its own process list. Inside the container, the main process has PID 1 (process ID 1). It cannot see processes from other containers or from the host.

```
Host Computer:
PID 1: systemd (init)
PID 100: Docker Engine
PID 200: Container A's process (nginx)
PID 201: Container A's worker
PID 300: Container B's process (python)

Container A sees:              Container B sees:
PID 1: nginx                  PID 1: python
PID 2: worker                 (no other processes)
(no other processes)

Each container thinks it is the only thing running.
```

#### 2. Network Namespace (Network Isolation)

Each container has its own network stack. Its own IP address. Its own ports. Container A can listen on port 80, and Container B can also listen on port 80. They do not conflict because they have different network namespaces.

```
Host Network:  172.17.0.1

Container A Network:  172.17.0.2
  Port 80: nginx

Container B Network:  172.17.0.3
  Port 80: apache

Container C Network:  172.17.0.4
  Port 3000: node app

Each container has its own IP address and its own ports.
Port 80 in Container A is different from port 80 in Container B.
```

#### 3. Mount Namespace (Filesystem Isolation)

Each container has its own view of the filesystem. Container A sees its own files. Container B sees its own files. They cannot see each other's files.

```
Container A's filesystem:     Container B's filesystem:
/                             /
├── app/                      ├── app/
│   └── server.py             │   └── index.js
├── usr/                      ├── usr/
│   └── bin/python             │   └── bin/node
└── etc/                      └── etc/

Completely separate views. Container A cannot see
Container B's files, and vice versa.
```

#### 4. User Namespace (User Isolation)

A process can be root (administrator) inside a container but a regular user on the host. This is important for security.

#### 5. UTS Namespace (Hostname Isolation)

Each container has its own hostname. You can name your container anything without affecting other containers or the host.

### Namespaces Summary

```
+---Container A----+    +---Container B----+
|                  |    |                  |
| PID namespace:   |    | PID namespace:   |
|  PID 1: nginx    |    |  PID 1: python   |
|                  |    |                  |
| Net namespace:   |    | Net namespace:   |
|  172.17.0.2      |    |  172.17.0.3      |
|                  |    |                  |
| Mnt namespace:   |    | Mnt namespace:   |
|  /app/server.py  |    |  /app/main.py    |
|                  |    |                  |
| UTS namespace:   |    | UTS namespace:   |
|  web-server      |    |  api-server      |
+------------------+    +------------------+
         |                       |
         |    Shared Kernel      |
         +-----------+-----------+
                     |
              +------+------+
              | Linux Kernel |
              | (one kernel  |
              |  for all)    |
              +-------------+
```

---

## Cgroups: Resource Limits

Namespaces handle isolation (who can see what). **Cgroups** handle resource limits (who can use how much).

### What Is a Cgroup?

Cgroup stands for **control group**. It is a Linux kernel feature that limits how much of a resource (CPU, memory, disk, network) a process can use.

### The Analogy

Imagine an apartment building with shared utilities:
- Water, electricity, and internet are shared among all apartments.
- Without limits, one apartment could use all the water pressure.
- The building manager sets limits: each apartment gets a maximum amount of water, electricity, and bandwidth.

Cgroups are the building manager for containers.

### Memory Limits

You can tell Docker exactly how much memory a container can use:

```bash
docker run -d --memory=512m nginx
```

**What this does:** The container can use at most 512 megabytes of RAM. If it tries to use more, the kernel can terminate the process inside the container (known as an OOM kill -- Out Of Memory kill).

```
Host Memory: 16 GB
+--------------------------------------------------+
|                                                  |
|  Container A: max 512 MB  [=====     ]           |
|  Container B: max 1 GB    [==========          ] |
|  Container C: max 256 MB  [===       ]           |
|                                                  |
|  Remaining: available for host and other apps    |
+--------------------------------------------------+
```

### CPU Limits

You can limit how much CPU a container can use:

```bash
docker run -d --cpus=1.5 nginx
```

**What this does:** The container can use at most 1.5 CPU cores. If the host has 4 cores, this container can use up to 37.5% of the total CPU.

```bash
docker run -d --cpus=0.5 nginx
```

**What this does:** The container gets at most half of one CPU core.

### Why Cgroups Matter

Without cgroups, one misbehaving container could:
- Use all available memory, causing other containers to crash
- Use 100% of the CPU, making other containers slow
- Write to disk so fast that other containers cannot read or write

Cgroups prevent one container from being a "noisy neighbor."

```
Without Cgroups:                 With Cgroups:
+-------------------+           +-------------------+
| Container A:      |           | Container A:      |
|   USES ALL CPU!   |           |   Limited to 1 CPU|
|   100% memory!    |           |   Max 512 MB RAM  |
+-------------------+           +-------------------+
| Container B:      |           | Container B:      |
|   Starving...     |           |   Gets fair share |
|   No resources!   |           |   of resources    |
+-------------------+           +-------------------+
```

---

## Why Containers Are Fast (vs VMs)

Now you understand the pieces. Let us put it all together and see why containers are so much faster than virtual machines.

### Virtual Machine Startup

When you start a VM:

1. The hypervisor allocates hardware resources.
2. A complete operating system boots up (kernel, init system, services).
3. The OS loads drivers, starts system services.
4. Finally, your application starts.

This takes **minutes**.

```
VM Startup Timeline:
0s -------- 30s -------- 60s -------- 90s -------- 120s
|           |            |            |             |
Boot BIOS   Load kernel  Start       Start          App
            & init       services    networking     ready

Total: 1-3 minutes
```

### Container Startup

When you start a container:

1. Docker creates namespaces (microseconds).
2. Docker sets up cgroups (microseconds).
3. Docker mounts the union filesystem (microseconds).
4. Docker starts your application process.

That is it. No OS boot. No drivers. No system services. Just your application.

This takes **seconds** (often less than one second).

```
Container Startup Timeline:
0s -------- 0.1s -------- 0.5s -------- 1s
|           |             |             |
Create      Mount FS      Start app     App
namespaces  + cgroups     process       ready
& network

Total: Under 1 second
```

### Resource Comparison

```
Virtual Machine:                    Container:
+-------------------------+        +-------------------------+
|  Your App               |        |  Your App               |
+-------------------------+        +-------------------------+
|  Libraries              |        |  Libraries              |
+-------------------------+        +-------------------------+
|  Guest OS               |        |  (no guest OS!)         |
|  (1-10 GB)              |        |                         |
|  - Kernel               |        +-------------------------+
|  - System services      |        Uses host kernel directly.
|  - Drivers              |        Total: 10-500 MB
|  - Everything an OS has |
+-------------------------+
|  Hypervisor             |
+-------------------------+
Total: 1-10 GB
```

### Side-by-Side Summary

| Aspect | Virtual Machine | Container |
|---|---|---|
| **Startup** | Minutes | Seconds (or less) |
| **Size** | 1-10 GB | 10-500 MB |
| **RAM overhead** | 512 MB - 2 GB per VM | A few MB per container |
| **Isolation** | Hardware-level (very strong) | Kernel-level (strong) |
| **OS** | Each has its own | Shares host OS kernel |
| **Density** | 5-20 per server | 100s-1000s per server |
| **Boot** | Full OS boot | Start a process |

### The Key Insight

A virtual machine virtualizes **hardware**. It creates a fake computer with fake CPU, fake RAM, and fake disk. Then it installs a real operating system on this fake hardware.

A container virtualizes the **operating system**. It creates an isolated environment using the host's kernel. No fake hardware. No second OS. Just isolation.

This is why containers are fast. They skip the most expensive step: booting an operating system.

---

## Putting It All Together

Here is the complete picture of how a container works:

```
+----------------------------------------------------+
|                   Container                        |
|                                                    |
|  +----------------------------------------------+ |
|  |  Writable Layer (copy-on-write)               | |
|  +----------------------------------------------+ |
|  |  Image Layers (read-only, shared)             | |
|  |  [App Code] [Libraries] [Base OS]             | |
|  +----------------------------------------------+ |
|                                                    |
|  Isolated by:                                      |
|  - PID namespace    (own process list)             |
|  - Network namespace (own IP + ports)              |
|  - Mount namespace   (own filesystem)              |
|  - User namespace    (own user IDs)                |
|  - UTS namespace     (own hostname)                |
|                                                    |
|  Limited by:                                       |
|  - Memory cgroup  (max RAM)                        |
|  - CPU cgroup     (max CPU)                        |
|  - I/O cgroup     (max disk speed)                 |
+----------------------------------------------------+
                        |
                  Uses host kernel
                        |
                +-------+-------+
                |  Linux Kernel |
                +---------------+
                |   Hardware    |
                +---------------+
```

When you type `docker run nginx`:

1. Docker pulls the Nginx image (if not already downloaded).
2. Docker stacks the image layers using a union filesystem.
3. Docker adds a writable layer on top.
4. Docker creates namespaces for process, network, filesystem, user, and hostname isolation.
5. Docker creates cgroups to limit resource usage (if specified).
6. Docker starts the Nginx process inside this isolated environment.

The result: an isolated, resource-controlled environment that starts in under a second. That is a container.

---

## Common Mistakes

1. **Thinking containers are small VMs.** They are not. There is no guest operating system. There is no hypervisor. Containers are isolated processes sharing the host kernel.

2. **Thinking container isolation is the same as VM isolation.** VM isolation is stronger because VMs have their own kernel. Container isolation is good for most use cases but not suitable for running untrusted code from unknown sources.

3. **Forgetting that container changes are temporary.** Changes in the writable layer are lost when the container is removed. Use volumes (covered in a later chapter) to persist data.

4. **Confusing image layers with container layers.** Image layers are read-only and shared. The container has one additional writable layer. Only the writable layer is unique to that container.

5. **Thinking each container has its own kernel.** All containers on a host share the same Linux kernel. This is the fundamental difference between containers and VMs.

---

## Best Practices

1. **Think of containers as disposable.** Design your applications so that containers can be created and destroyed at will. Do not store important data inside containers.

2. **Keep images small.** Fewer layers and smaller layers mean faster downloads, less disk space, and faster startup. Use minimal base images like Alpine when possible.

3. **Set resource limits in production.** Always use `--memory` and `--cpus` in production to prevent one container from consuming all resources.

4. **Use official base images.** Official images are maintained by Docker and the software vendors. They are optimized, secure, and well-tested.

5. **Understand the layer cache.** When building images, Docker caches layers. Put things that change rarely (like OS packages) in early layers and things that change often (like your code) in later layers. This makes rebuilds faster.

---

## Quick Summary

Images are read-only blueprints made of stacked layers. Containers are running instances of images with an additional writable layer. Union filesystems combine layers into a single view. Namespaces provide isolation (process, network, filesystem, user, hostname). Cgroups limit resource usage (CPU, memory, I/O). Containers are fast because they share the host kernel and skip the OS boot process that VMs require.

---

## Key Points

- An image is a read-only template (like a recipe or a class). A container is a running instance (like a cake or an object).
- Images are built from layers. Each layer represents a set of filesystem changes.
- Layers are shared between images, saving disk space and download time.
- A union filesystem merges layers into one unified view.
- Each container gets a thin writable layer on top of the image layers (copy-on-write).
- Namespaces isolate containers from each other (processes, network, filesystem, users, hostname).
- Cgroups limit how much CPU, memory, and I/O a container can use.
- Containers share the host kernel. VMs have their own kernel. This is why containers start in seconds and VMs take minutes.

---

## Practice Questions

1. Explain the difference between an image and a container using your own analogy (not one from this chapter).

2. An image has 4 layers. You create 3 containers from this image. How many copies of the image layers exist on disk? Why?

3. What happens when a container modifies a file that comes from an image layer? What mechanism handles this?

4. Name three types of namespaces and explain what each one isolates.

5. You have a server with 16 GB of RAM. You want to run 4 containers, each limited to 2 GB. What Docker flag would you use? What happens if a container tries to use 3 GB?

---

## Exercises

### Exercise 1: Observe Image Layers

Run these commands and observe the layers:

```bash
docker pull nginx
docker image inspect nginx
```

Look at the output of `docker image inspect`. Find the "Layers" section. How many layers does the Nginx image have? What does each layer hash represent?

### Exercise 2: Test Isolation

Open two terminals. In each one, run an interactive Alpine container:

```bash
# Terminal 1
docker run -it --name box-a alpine sh

# Terminal 2
docker run -it --name box-b alpine sh
```

In box-a, create a file:
```bash
echo "I am box A" > /tmp/identity.txt
```

In box-b, try to read that file:
```bash
cat /tmp/identity.txt
```

What happens? Why?

### Exercise 3: Resource Limits

Run a container with memory limits:

```bash
docker run -d --memory=100m --name limited-box nginx
```

Then inspect it:

```bash
docker inspect limited-box | grep -i memory
```

What memory limit is shown? Try running a container with `--memory=10m`. Does Nginx start? What happens?

---

## What Is Next?

You now understand how containers work on the inside. In the next chapter, we will take a closer look at Docker images -- how to find them, inspect them, manage them, and understand tags and digests. Images are the foundation of everything in Docker, and mastering them is the next step in your Docker journey.
