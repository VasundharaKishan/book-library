# Chapter 2: Installing Docker

## What You Will Learn

- How to install Docker Desktop on Mac, Windows, and Linux
- How to verify that Docker is installed correctly
- How to create a Docker Hub account
- How to run your very first Docker command
- How to navigate the Docker Desktop interface

## Why This Chapter Matters

You cannot learn to drive by reading about cars. You need to sit in the driver's seat, start the engine, and move.

Docker is the same. You need it installed on your computer before you can do anything. This chapter walks you through every step. By the end, you will have Docker running and you will have launched your first container.

Do not skip this chapter. Follow along. Type every command. See every output. This is where your hands-on Docker journey begins.

---

## What You Need Before You Start

Before installing Docker, make sure your computer meets these requirements:

**For Mac:**
- macOS 12 (Monterey) or newer
- At least 4 GB of RAM
- Apple Silicon (M1, M2, M3, M4) or Intel processor

**For Windows:**
- Windows 10 version 21H2 or newer, or Windows 11
- At least 4 GB of RAM
- 64-bit processor
- Hardware virtualization enabled in BIOS (most modern computers have this)

**For Linux:**
- A 64-bit distribution (Ubuntu, Fedora, Debian, etc.)
- At least 4 GB of RAM
- A user account with sudo privileges

---

## Installing Docker Desktop on Mac

### Step 1: Download Docker Desktop

Open your web browser and go to:

```
https://www.docker.com/products/docker-desktop/
```

Click the **Download for Mac** button. The website will detect whether you have an Apple Silicon or Intel Mac and offer the correct download.

If you are not sure which chip you have, click the Apple menu in the top-left corner of your screen, then click **About This Mac**. If it says "Apple M1" or "Apple M2" or similar, you have Apple Silicon. If it says "Intel," you have an Intel chip.

### Step 2: Install the Application

1. Open the downloaded `.dmg` file. It will show a window with the Docker icon and an Applications folder.
2. Drag the Docker icon into the Applications folder.
3. Wait for the copy to finish.

```
+-------------------------------------------+
|                                           |
|   [ Docker Icon ]  --->  [ Applications ] |
|                                           |
|   Drag Docker to Applications             |
+-------------------------------------------+
```

### Step 3: Start Docker Desktop

1. Open your Applications folder.
2. Double-click **Docker**.
3. macOS may ask, "Are you sure you want to open it?" Click **Open**.
4. Docker may ask for your password. Enter it. Docker needs this to set up networking.
5. You will see the Docker icon (a whale) appear in your menu bar at the top of the screen.

### Step 4: Wait for Docker to Start

The whale icon in your menu bar will animate (the containers on the whale will move). This means Docker is starting up. Wait until the animation stops. This usually takes 30 to 60 seconds.

When Docker is ready, the whale icon will be still.

### Step 5: Accept the Terms

Docker Desktop will show you a service agreement. Read it and click **Accept** to continue.

---

## Installing Docker Desktop on Windows

### Step 1: Check Virtualization

Docker on Windows needs a feature called hardware virtualization. Most modern computers have it enabled. To check:

1. Press `Ctrl + Shift + Esc` to open Task Manager.
2. Click the **Performance** tab.
3. Click **CPU** on the left.
4. Look for "Virtualization" at the bottom. It should say **Enabled**.

If it says "Disabled," you need to enable it in your computer's BIOS settings. Search online for "enable virtualization [your computer model]" for specific instructions.

### Step 2: Enable WSL 2

Docker Desktop on Windows uses WSL 2 (Windows Subsystem for Linux). This lets Docker run Linux containers on Windows.

Open **PowerShell** as Administrator:
1. Right-click the Start button.
2. Click **Terminal (Admin)** or **PowerShell (Admin)**.

Then type this command:

```powershell
wsl --install
```

**What this does:** It installs WSL 2 and a default Linux distribution (usually Ubuntu). This is the foundation Docker needs to run containers on Windows.

Restart your computer after this command finishes.

### Step 3: Download Docker Desktop

Open your web browser and go to:

```
https://www.docker.com/products/docker-desktop/
```

Click **Download for Windows**.

### Step 4: Run the Installer

1. Double-click the downloaded `Docker Desktop Installer.exe`.
2. Make sure **Use WSL 2 instead of Hyper-V** is checked. This is the recommended option.
3. Click **OK** to start the installation.
4. Wait for the installation to finish. This may take a few minutes.
5. Click **Close and restart** when prompted.

### Step 5: Start Docker Desktop

After your computer restarts:

1. Find **Docker Desktop** in your Start menu.
2. Click to open it.
3. Docker may take a minute or two to start. You will see the Docker whale icon in your system tray (bottom-right corner of the screen).
4. Accept the service agreement when prompted.

---

## Installing Docker on Linux

On Linux, you can install Docker Engine directly or use Docker Desktop. We will show Docker Engine because it is more common on Linux.

### Ubuntu / Debian

Open a terminal and run these commands one by one:

```bash
# Step 1: Update your package list
sudo apt-get update
```

**What this does:** Downloads the latest list of available software packages. Think of it as refreshing the catalog at a store.

```bash
# Step 2: Install required packages
sudo apt-get install -y ca-certificates curl
```

**What this does:** Installs tools Docker needs to download files securely from the internet.

```bash
# Step 3: Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

**What this does:** A GPG key is like a digital signature. It proves that the Docker software you download is genuine and has not been tampered with.

```bash
# Step 4: Add the Docker repository
echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**What this does:** Tells your system where to find Docker packages. It is like adding a new store to your shopping list.

```bash
# Step 5: Update the package list again
sudo apt-get update
```

**What this does:** Refreshes the catalog now that we added the Docker store.

```bash
# Step 6: Install Docker
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

**What this does:** Installs Docker Engine and all related tools. Here is what each package is:
- `docker-ce` -- Docker Community Edition (the engine)
- `docker-ce-cli` -- The command-line tool
- `containerd.io` -- The container runtime (manages container processes)
- `docker-buildx-plugin` -- Advanced image building tool
- `docker-compose-plugin` -- Docker Compose (for multi-container apps)

```bash
# Step 7: Add your user to the docker group
sudo usermod -aG docker $USER
```

**What this does:** Lets you run Docker commands without typing `sudo` every time. You need to log out and log back in for this to take effect.

### Fedora / RHEL

```bash
# Step 1: Install the dnf-plugins-core package
sudo dnf -y install dnf-plugins-core

# Step 2: Add the Docker repository
sudo dnf config-manager --add-repo \
  https://download.docker.com/linux/fedora/docker-ce.repo

# Step 3: Install Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Step 4: Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Step 5: Add your user to the docker group
sudo usermod -aG docker $USER
```

Log out and log back in after running these commands.

---

## Verifying Your Installation

Now let us make sure Docker is installed correctly. Open your terminal (Mac/Linux) or PowerShell (Windows).

### Check the Docker Version

```bash
docker --version
```

**Expected output:**

```
Docker version 27.4.1, build b9d17ea
```

Your version number may be different. That is fine. As long as you see a version number, Docker is installed.

**Line-by-line explanation:**
- `docker` -- The Docker command-line tool
- `--version` -- A flag that asks "What version are you?"
- The output shows the version number and a build hash (a unique identifier for that specific build)

### Check Docker System Information

```bash
docker info
```

**Expected output (abbreviated):**

```
Client:
 Version:    27.4.1
 Context:    desktop-linux

Server:
 Containers: 0
  Running: 0
  Paused:  0
  Stopped: 0
 Images: 0
 Server Version: 27.4.1
 Storage Driver: overlay2
 Operating System: Docker Desktop
 Total Memory: 7.659GiB
 CPUs: 4
```

**Line-by-line explanation:**
- `Client` -- Information about the Docker CLI (the tool you are typing commands into)
- `Server` -- Information about Docker Engine (the background service)
- `Containers: 0` -- You have no containers yet (expected for a fresh install)
- `Images: 0` -- You have no images yet (also expected)
- `Storage Driver: overlay2` -- The file system technology Docker uses for images and containers
- `Total Memory` -- How much memory Docker can use
- `CPUs` -- How many CPU cores Docker can use

If you see an error like "Cannot connect to the Docker daemon," make sure Docker Desktop is running.

---

## Creating a Docker Hub Account

Docker Hub is the default place where Docker looks for images. You can use it without an account, but having one lets you:

- Download images faster (higher rate limits)
- Store your own images
- Access private repositories

### Step 1: Go to Docker Hub

Open your browser and visit:

```
https://hub.docker.com
```

### Step 2: Sign Up

1. Click **Sign Up**.
2. Enter a username, email, and password.
3. Complete the verification.
4. Check your email and verify your account.

### Step 3: Log In from the Command Line

Back in your terminal, type:

```bash
docker login
```

**Expected output:**

```
Log in with your Docker ID or email address to push and pull images.
Username: yourusername
Password:
Login Succeeded
```

**What this does:** Connects your terminal to your Docker Hub account. Now Docker can download images faster and push your own images.

Your password will not show as you type it. This is normal security behavior. Just type it and press Enter.

---

## Running Your First Container: hello-world

This is the moment. You are about to run your first Docker container. Type this command:

```bash
docker run hello-world
```

**Expected output:**

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
e6590344b1a5: Pull complete
Digest: sha256:c41088499908a59aae30...
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

Congratulations! You just ran your first container!

### What Just Happened? Step by Step

Let us break down exactly what Docker did:

```
Step 1: You typed "docker run hello-world"
         |
         v
Step 2: Docker looked for the "hello-world" image on your computer.
        It did not find it.
        "Unable to find image 'hello-world:latest' locally"
         |
         v
Step 3: Docker went to Docker Hub and downloaded the image.
        "Pulling from library/hello-world"
        "Pull complete"
         |
         v
Step 4: Docker created a container from the image.
         |
         v
Step 5: Docker started the container.
        The container ran a small program that printed the
        "Hello from Docker!" message.
         |
         v
Step 6: The program finished. The container stopped.
```

```
Your Computer                        Docker Hub
+------------------+                 +------------------+
|                  |   1. "Do you    |                  |
|  Docker Engine   | ---have this?-->|  hello-world     |
|                  |                 |  image           |
|                  |   2. "Here     |                  |
|  [hello-world    | <--it is!"-----|                  |
|   image saved]   |                 +------------------+
|                  |
|  3. Create and   |
|     run container|
|                  |
|  4. "Hello from  |
|     Docker!"     |
+------------------+
```

### Understanding Each Line of Output

**`Unable to find image 'hello-world:latest' locally`**
Docker first checks your computer for the image. Since this is your first time, it does not find it. The word `latest` is a **tag** -- it means "the newest version."

**`latest: Pulling from library/hello-world`**
Docker is downloading the image from Docker Hub. The `library/` prefix means this is an official image maintained by Docker.

**`e6590344b1a5: Pull complete`**
The image has been downloaded. The long string of characters is a unique identifier for this image layer.

**`Digest: sha256:c41088499908a59aae30...`**
This is a fingerprint of the image. It guarantees you got exactly the right image and nothing was changed during download.

**`Status: Downloaded newer image for hello-world:latest`**
Docker confirms the download is complete.

**`Hello from Docker!`**
The container ran successfully and printed this message.

---

## Docker Desktop UI Overview

Docker Desktop gives you a graphical way to see what Docker is doing. Let us take a quick tour.

### Opening Docker Desktop

- **Mac:** Click the whale icon in the menu bar, then click **Dashboard**.
- **Windows:** Click the whale icon in the system tray, then click **Dashboard**.
- **Linux:** Open Docker Desktop from your applications menu.

### The Main Sections

```
+-----------------------------------------------------------+
|  Docker Desktop                                           |
+-----------------------------------------------------------+
|                                                           |
|  [ Containers ]  [ Images ]  [ Volumes ]  [ Builds ]     |
|                                                           |
|  Containers Tab:                                          |
|  +-----------------------------------------------------+ |
|  | NAME          IMAGE         STATUS      PORT         | |
|  +-----------------------------------------------------+ |
|  | (your containers will appear here)                   | |
|  +-----------------------------------------------------+ |
|                                                           |
+-----------------------------------------------------------+
```

**Containers tab:** Shows all your containers (running and stopped). You can start, stop, and delete containers from here.

**Images tab:** Shows all Docker images on your computer. You can see how much space each image uses.

**Volumes tab:** Shows data storage areas that persist even when containers are deleted. We will learn about volumes later.

**Builds tab:** Shows the history of images you have built.

### Container Details

When you click on a container, you can see:

- **Logs:** What the container printed to the screen (like the "Hello from Docker!" message)
- **Inspect:** Detailed technical information about the container
- **Terminal:** An interactive terminal inside the container
- **Stats:** CPU and memory usage

You do not need to use Docker Desktop for this book. Everything can be done from the command line. But it is useful to have a visual way to see what is happening.

---

## Troubleshooting Common Installation Issues

### "Cannot connect to the Docker daemon"

**What it means:** Docker Engine is not running.

**Fix:** Make sure Docker Desktop is open and running. Look for the whale icon in your menu bar (Mac) or system tray (Windows). If you are on Linux without Docker Desktop, start Docker with:

```bash
sudo systemctl start docker
```

### "Permission denied" on Linux

**What it means:** Your user is not in the `docker` group.

**Fix:** Run these commands and then log out and back in:

```bash
sudo usermod -aG docker $USER
```

Then close your terminal, log out, log back in, and open a new terminal.

### "WSL 2 is not installed" on Windows

**What it means:** Docker needs WSL 2 to run on Windows.

**Fix:** Open PowerShell as Administrator and run:

```powershell
wsl --install
```

Restart your computer after this finishes.

### Docker Desktop is slow to start

**What it means:** This is normal the first time. Docker needs to set up its environment.

**Fix:** Wait 1-2 minutes. If it consistently takes more than 5 minutes, try these steps:
1. Quit Docker Desktop completely.
2. Restart your computer.
3. Open Docker Desktop again.

### "No space left on device"

**What it means:** Docker has used up the disk space allocated to it.

**Fix:** Clean up unused Docker data:

```bash
docker system prune
```

**What this does:** Removes all stopped containers, unused networks, and dangling images. It frees up disk space. Docker will ask you to confirm before deleting anything.

---

## Common Mistakes

1. **Forgetting to start Docker Desktop.** Docker commands will not work if Docker Desktop is not running. Always check that the whale icon is visible.

2. **Not logging out after adding your user to the docker group (Linux).** The group change does not take effect until you log out and log back in.

3. **Running commands in the wrong terminal.** Make sure you are in a regular terminal (Mac/Linux) or PowerShell (Windows), not inside another application.

4. **Typing `sudo` before every Docker command on Mac/Windows.** You do not need `sudo` with Docker Desktop on Mac or Windows. Only Linux users need `sudo` (unless they added themselves to the docker group).

5. **Ignoring the Docker Desktop service agreement.** Docker Desktop requires you to accept the terms of service. The application will not work until you do.

---

## Best Practices

1. **Keep Docker Desktop updated.** New versions fix bugs, add features, and patch security issues. Enable automatic updates if your system supports it.

2. **Configure resource limits.** Docker Desktop lets you set how much memory and CPU it can use. Go to Settings > Resources. For most development work, 4 GB of memory and 2 CPUs is sufficient.

3. **Clean up regularly.** Docker images and containers take up disk space. Run `docker system prune` periodically to remove unused data.

4. **Use `docker info` to diagnose problems.** If something is not working, `docker info` tells you a lot about the state of your Docker installation.

---

## Quick Summary

Installing Docker means installing Docker Desktop (on Mac/Windows) or Docker Engine (on Linux). After installation, you verify it works with `docker --version` and `docker info`. Creating a Docker Hub account gives you access to thousands of pre-built images. Running `docker run hello-world` is the traditional first step that confirms everything is working.

---

## Key Points

- Docker Desktop is the easiest way to install Docker on Mac and Windows.
- Linux users can install Docker Engine directly from Docker's repository.
- `docker --version` checks that Docker is installed.
- `docker info` shows detailed information about your Docker installation.
- `docker run hello-world` downloads and runs a test container.
- Docker Hub is the default image registry. Create a free account for better access.
- When you run an image for the first time, Docker downloads it from Docker Hub automatically.
- Docker Desktop provides a graphical interface, but everything can be done from the command line.

---

## Practice Questions

1. What command do you use to check which version of Docker is installed?

2. When you run `docker run hello-world`, Docker says "Unable to find image locally." What does Docker do next?

3. What is WSL 2 and why does Docker need it on Windows?

4. After running `sudo usermod -aG docker $USER` on Linux, why do you need to log out and log back in?

5. What does the `docker system prune` command do? When would you use it?

---

## Exercises

### Exercise 1: Verify Your Installation

Run these three commands and write down the output:

```bash
docker --version
docker info
docker run hello-world
```

If any command fails, use the troubleshooting section to fix the issue.

### Exercise 2: Explore Docker Hub

1. Log in to Docker Hub at https://hub.docker.com.
2. Search for the `nginx` image.
3. Find out how many pulls the official Nginx image has.
4. Look at the tags. What is the difference between `nginx:latest` and `nginx:alpine`?

### Exercise 3: Explore Docker Desktop

1. Open Docker Desktop.
2. Go to the Containers tab. Do you see the `hello-world` container? What is its status?
3. Go to the Images tab. Do you see the `hello-world` image? How large is it?
4. Go to Settings > Resources. How much memory and how many CPUs are allocated to Docker?

---

## What Is Next?

Your Docker installation is working. You have run your first container. In the next chapter, we will run real containers -- a web server, an interactive Linux shell, and more. You will learn how to control containers: start them, stop them, name them, and clean them up.
